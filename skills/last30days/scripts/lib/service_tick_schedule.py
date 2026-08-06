"""Service-owned cadence admission for durable all-source ticks."""

from __future__ import annotations

import sqlite3
from collections.abc import Callable, Mapping
from datetime import datetime, timedelta, timezone
from pathlib import Path

from . import service_contracts as contracts
from .service_tick import (
    TickCoordinator,
    _canonical_json,
    _load_config,
    _stable_id,
)


_TERMINAL_TICK_STATES = frozenset(
    {"complete", "complete_degraded", "failed", "missed_due_to_overlap"}
)


def _timestamp(value: datetime) -> str:
    if value.tzinfo is None:
        raise ValueError("schedule clock must be timezone-aware")
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _from_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(
        timezone.utc
    )


class TickScheduleCoordinator:
    """Deep module owning one configured schedule and its durable admission state."""

    def __init__(
        self,
        db_path: Path,
        *,
        tick_coordinator: TickCoordinator,
        config_path: Path,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self.db_path = Path(db_path)
        self.tick_coordinator = tick_coordinator
        self.config_path = Path(config_path)
        self.clock = clock or (lambda: datetime.now(timezone.utc))
        config, _, config_digest = _load_config(self.config_path)
        tick = config["tick"]
        schedule = tick.get("schedule") if isinstance(tick, Mapping) else None
        self.schedule = dict(schedule) if isinstance(schedule, Mapping) else None
        self.config_digest = config_digest
        self.lateness_seconds = int(tick["lateness_seconds"])

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=5)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("PRAGMA busy_timeout=5000")
        return conn

    @staticmethod
    def _latest_boundary(
        now: datetime, *, interval_seconds: int, anchor_seconds: int
    ) -> datetime:
        epoch_seconds = int(now.astimezone(timezone.utc).timestamp())
        aligned_seconds = (
            (epoch_seconds - anchor_seconds) // interval_seconds
        ) * interval_seconds + anchor_seconds
        return datetime.fromtimestamp(aligned_seconds, tz=timezone.utc)

    @staticmethod
    def _request(
        schedule_id: str, boundary: datetime, interval_seconds: int
    ) -> contracts.TickRequest:
        return contracts.TickRequest.from_dict(
            {
                "schema_version": contracts.SCHEMA_VERSION,
                "schedule_id": schedule_id,
                "interval_from": _timestamp(
                    boundary - timedelta(seconds=interval_seconds)
                ),
                "interval_to": _timestamp(boundary),
                "trigger": contracts.TickTrigger.TIMER.value,
            }
        )

    def _event(
        self,
        conn: sqlite3.Connection,
        *,
        schedule_id: str,
        event_type: str,
        occurred_at: str,
        boundary: str | None = None,
        tick_id: str | None = None,
        payload: Mapping[str, object] | None = None,
    ) -> None:
        sequence = int(
            conn.execute(
                """SELECT COALESCE(MAX(sequence), 0) + 1
                   FROM service_tick_schedule_events WHERE schedule_id = ?""",
                (schedule_id,),
            ).fetchone()[0]
        )
        conn.execute(
            """INSERT INTO service_tick_schedule_events (
                   event_id, schedule_id, sequence, event_type, boundary,
                   tick_id, payload_json, occurred_at
               ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                _stable_id(
                    "tick-schedule-event",
                    {"schedule_id": schedule_id, "sequence": sequence},
                ),
                schedule_id,
                sequence,
                event_type,
                boundary,
                tick_id,
                _canonical_json(dict(payload or {})),
                occurred_at,
            ),
        )

    def status(self) -> dict[str, object]:
        """Return sanitized state without admitting work."""
        schedule = self.schedule
        if schedule is None:
            return self._disabled_status()
        conn = self._connect()
        try:
            row = conn.execute(
                "SELECT * FROM service_tick_schedules WHERE schedule_id = ?",
                (schedule["schedule_id"],),
            ).fetchone()
            if row is None:
                state = {
                    "state": "uninitialized",
                    "next_boundary": None,
                    "last_boundary": None,
                    "last_tick_id": None,
                    "last_tick_state": None,
                    "runtime_error": None,
                }
            else:
                state = {
                    "state": row["state"],
                    "next_boundary": row["next_boundary"],
                    "last_boundary": row["last_boundary"],
                    "last_tick_id": row["last_tick_id"],
                    "last_tick_state": row["last_tick_state"],
                    "runtime_error": row["last_error_code"],
                }
        finally:
            conn.close()
        if row is None and schedule["enabled"] is False:
            return self._disabled_status()
        return {
            "schema_version": 1,
            "enabled": (
                bool(row["enabled"])
                if row is not None
                else bool(schedule["enabled"])
            ),
            "schedule_id": schedule["schedule_id"],
            "interval_seconds": (
                row["interval_seconds"]
                if row is not None
                else schedule["interval_seconds"]
            ),
            "anchor_seconds": (
                row["anchor_seconds"] if row is not None else schedule["anchor_seconds"]
            ),
            **state,
        }

    def _pause_existing(self) -> None:
        schedule = self.schedule
        schedule_id = str(schedule["schedule_id"]) if schedule else None
        now_text = _timestamp(self.clock())
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            if schedule_id is None:
                rows = conn.execute(
                    """SELECT schedule_id FROM service_tick_schedules
                       WHERE enabled = 1 OR state != 'paused'"""
                ).fetchall()
            else:
                rows = conn.execute(
                    """SELECT schedule_id FROM service_tick_schedules
                       WHERE schedule_id = ? AND (enabled = 1 OR state != 'paused')""",
                    (schedule_id,),
                ).fetchall()
            for row in rows:
                bound_id = str(row["schedule_id"])
                conn.execute(
                    """UPDATE service_tick_schedules
                       SET enabled = 0, state = 'paused', last_error_code = NULL,
                           updated_at = ? WHERE schedule_id = ?""",
                    (now_text, bound_id),
                )
                self._event(
                    conn,
                    schedule_id=bound_id,
                    event_type="paused",
                    occurred_at=now_text,
                )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _disabled_status(self) -> dict[str, object]:
        schedule = self.schedule
        return {
            "schema_version": 1,
            "enabled": False,
            "schedule_id": schedule["schedule_id"] if schedule else None,
            "interval_seconds": schedule["interval_seconds"] if schedule else None,
            "anchor_seconds": schedule["anchor_seconds"] if schedule else None,
            "state": "disabled",
            "next_boundary": None,
            "last_boundary": None,
            "last_tick_id": None,
            "last_tick_state": None,
            "runtime_error": None,
        }

    def poll(self) -> dict[str, object]:
        """Admit due work when enabled and return sanitized current status."""
        schedule = self.schedule
        if schedule is None or schedule["enabled"] is False:
            self._pause_existing()
            return self.status()

        now = self.clock().astimezone(timezone.utc)
        now_text = _timestamp(now)
        schedule_id = str(schedule["schedule_id"])
        interval_seconds = int(schedule["interval_seconds"])
        anchor_seconds = int(schedule["anchor_seconds"])
        request_boundary: datetime | None = None
        recovery_attempt_count: int | None = None

        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            replaced_rows = conn.execute(
                """SELECT * FROM service_tick_schedules
                   WHERE schedule_id != ? AND enabled = 1
                   ORDER BY updated_at DESC, schedule_id""",
                (schedule_id,),
            ).fetchall()
            if replaced_rows:
                predecessor = replaced_rows[0]
                for replaced in replaced_rows:
                    replaced_id = str(replaced["schedule_id"])
                    conn.execute(
                        """UPDATE service_tick_schedules
                           SET enabled = 0, state = 'paused',
                               last_error_code = 'schedule_config_replaced',
                               updated_at = ? WHERE schedule_id = ?""",
                        (now_text, replaced_id),
                    )
                    self._event(
                        conn,
                        schedule_id=replaced_id,
                        event_type="config_replaced",
                        occurred_at=now_text,
                        payload={"replacement_schedule_id": schedule_id},
                    )
                conn.execute(
                    """INSERT INTO service_tick_schedules (
                           schedule_id, config_digest, interval_seconds,
                           anchor_seconds, enabled, state, next_boundary,
                           last_boundary, last_tick_id, last_tick_state,
                           last_error_code, created_at, updated_at
                       ) VALUES (?, ?, ?, ?, 0, 'paused', ?, ?, ?, ?,
                                 'schedule_config_replaced', ?, ?)
                       ON CONFLICT(schedule_id) DO UPDATE SET
                           enabled = 0, state = 'paused',
                           last_error_code = 'schedule_config_replaced',
                           updated_at = excluded.updated_at""",
                    (
                        schedule_id,
                        self.config_digest,
                        interval_seconds,
                        anchor_seconds,
                        predecessor["next_boundary"],
                        predecessor["last_boundary"],
                        predecessor["last_tick_id"],
                        predecessor["last_tick_state"],
                        now_text,
                        now_text,
                    ),
                )
                current_event_count = int(
                    conn.execute(
                        """SELECT COUNT(*) FROM service_tick_schedule_events
                           WHERE schedule_id = ?""",
                        (schedule_id,),
                    ).fetchone()[0]
                )
                if current_event_count == 0:
                    self._event(
                        conn,
                        schedule_id=schedule_id,
                        event_type="config_replaced",
                        occurred_at=now_text,
                        tick_id=predecessor["last_tick_id"],
                        payload={
                            "predecessor_schedule_id": predecessor["schedule_id"]
                        },
                    )
                conn.commit()
                return self.status()
            row = conn.execute(
                "SELECT * FROM service_tick_schedules WHERE schedule_id = ?",
                (schedule_id,),
            ).fetchone()
            if row is not None and (
                row["config_digest"] != self.config_digest
                or int(row["interval_seconds"]) != interval_seconds
                or int(row["anchor_seconds"]) != anchor_seconds
            ):
                if not (
                    row["state"] == "paused"
                    and row["last_error_code"] == "schedule_config_replaced"
                ):
                    conn.execute(
                        """UPDATE service_tick_schedules
                           SET enabled = 0, state = 'paused',
                               last_error_code = 'schedule_config_replaced',
                               updated_at = ? WHERE schedule_id = ?""",
                        (now_text, schedule_id),
                    )
                    self._event(
                        conn,
                        schedule_id=schedule_id,
                        event_type="config_replaced",
                        occurred_at=now_text,
                        payload={"new_config_digest": self.config_digest},
                    )
                conn.commit()
                return self.status()
            if row is not None and row["state"] == "paused":
                conn.commit()
                return self.status()
            if row is None:
                latest = self._latest_boundary(
                    now,
                    interval_seconds=interval_seconds,
                    anchor_seconds=anchor_seconds,
                )
                next_boundary = latest + timedelta(seconds=interval_seconds)
                if (now - latest).total_seconds() > self.lateness_seconds:
                    conn.execute(
                        """INSERT INTO service_tick_schedules (
                               schedule_id, config_digest, interval_seconds,
                               anchor_seconds, enabled, state, next_boundary,
                               created_at, updated_at
                           ) VALUES (?, ?, ?, ?, 1, 'ready', ?, ?, ?)""",
                        (
                            schedule_id,
                            self.config_digest,
                            interval_seconds,
                            anchor_seconds,
                            _timestamp(next_boundary),
                            now_text,
                            now_text,
                        ),
                    )
                    self._event(
                        conn,
                        schedule_id=schedule_id,
                        event_type="initialized",
                        occurred_at=now_text,
                        payload={
                            "interval_seconds": interval_seconds,
                            "anchor_seconds": anchor_seconds,
                        },
                    )
                    self._event(
                        conn,
                        schedule_id=schedule_id,
                        event_type="skipped_stale",
                        boundary=_timestamp(latest),
                        occurred_at=now_text,
                    )
                else:
                    request_boundary = latest
                    conn.execute(
                        """INSERT INTO service_tick_schedules (
                               schedule_id, config_digest, interval_seconds,
                               anchor_seconds, enabled, state, next_boundary,
                               last_boundary, created_at, updated_at
                           ) VALUES (?, ?, ?, ?, 1, 'admitting', ?, ?, ?, ?)""",
                        (
                            schedule_id,
                            self.config_digest,
                            interval_seconds,
                            anchor_seconds,
                            _timestamp(next_boundary),
                            _timestamp(latest),
                            now_text,
                            now_text,
                        ),
                    )
                    self._event(
                        conn,
                        schedule_id=schedule_id,
                        event_type="initialized",
                        occurred_at=now_text,
                        payload={
                            "interval_seconds": interval_seconds,
                            "anchor_seconds": anchor_seconds,
                        },
                    )
                    self._event(
                        conn,
                        schedule_id=schedule_id,
                        event_type="admitted",
                        boundary=_timestamp(latest),
                        occurred_at=now_text,
                    )
            else:
                last_tick_id = row["last_tick_id"]
                if last_tick_id is not None:
                    tick = conn.execute(
                        "SELECT state FROM service_ticks WHERE tick_id = ?",
                        (last_tick_id,),
                    ).fetchone()
                    tick_state = str(tick["state"]) if tick is not None else None
                    if tick_state not in _TERMINAL_TICK_STATES:
                        attempt = conn.execute(
                            """SELECT state, lease_expires_at
                               FROM service_tick_attempts WHERE tick_id = ?
                               ORDER BY attempt DESC LIMIT 1""",
                            (last_tick_id,),
                        ).fetchone()
                        if (
                            attempt is not None
                            and attempt["state"] == "running"
                            and attempt["lease_expires_at"] is not None
                            and attempt["lease_expires_at"] > now_text
                        ):
                            conn.execute(
                                """UPDATE service_tick_schedules
                                   SET state = 'recovery_waiting',
                                       last_tick_state = ?, updated_at = ?
                                   WHERE schedule_id = ?""",
                                (tick_state, now_text, schedule_id),
                            )
                        else:
                            recovery_attempt_count = int(
                                conn.execute(
                                    """SELECT COUNT(*) FROM service_tick_attempts
                                       WHERE tick_id = ?""",
                                    (last_tick_id,),
                                ).fetchone()[0]
                            )
                            request_boundary = _from_timestamp(row["last_boundary"])
                    elif _from_timestamp(row["next_boundary"]) <= now:
                        next_due = _from_timestamp(row["next_boundary"])
                        latest = self._latest_boundary(
                            now,
                            interval_seconds=interval_seconds,
                            anchor_seconds=anchor_seconds,
                        )
                        next_boundary = latest + timedelta(seconds=interval_seconds)
                        if (now - latest).total_seconds() > self.lateness_seconds:
                            conn.execute(
                                """UPDATE service_tick_schedules
                                   SET state = 'ready', next_boundary = ?,
                                       last_error_code = NULL, updated_at = ?
                                   WHERE schedule_id = ?""",
                                (_timestamp(next_boundary), now_text, schedule_id),
                            )
                            self._event(
                                conn,
                                schedule_id=schedule_id,
                                event_type="skipped_stale",
                                boundary=_timestamp(latest),
                                occurred_at=now_text,
                            )
                        else:
                            request_boundary = latest
                            skipped_intervals = max(
                                0,
                                int(
                                    (latest - next_due).total_seconds()
                                    // interval_seconds
                                ),
                            )
                            conn.execute(
                                """UPDATE service_tick_schedules
                                   SET state = 'admitting',
                                       next_boundary = ?, last_boundary = ?,
                                       last_tick_id = NULL, last_tick_state = NULL,
                                       last_error_code = NULL, updated_at = ?
                                   WHERE schedule_id = ?""",
                                (
                                    _timestamp(next_boundary),
                                    _timestamp(request_boundary),
                                    now_text,
                                    schedule_id,
                                ),
                            )
                            self._event(
                                conn,
                                schedule_id=schedule_id,
                                event_type="admitted",
                                boundary=_timestamp(request_boundary),
                                occurred_at=now_text,
                                payload={"skipped_intervals": skipped_intervals},
                            )
                    else:
                        conn.execute(
                            """UPDATE service_tick_schedules
                               SET state = 'ready', last_tick_state = ?, updated_at = ?
                               WHERE schedule_id = ?""",
                            (tick_state, now_text, schedule_id),
                        )
                elif row["last_boundary"] is not None:
                    request_boundary = _from_timestamp(row["last_boundary"])
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

        if request_boundary is None:
            return self.status()

        request = self._request(schedule_id, request_boundary, interval_seconds)
        try:
            receipt = self.tick_coordinator.enqueue_tick(request)
        except Exception:
            conn = self._connect()
            try:
                conn.execute("BEGIN IMMEDIATE")
                tick = conn.execute(
                    """SELECT tick_id, state FROM service_ticks
                       WHERE schedule_id = ? AND interval_to = ?
                       ORDER BY created_at DESC LIMIT 1""",
                    (schedule_id, _timestamp(request_boundary)),
                ).fetchone()
                conn.execute(
                    """UPDATE service_tick_schedules
                       SET enabled = 0, state = 'paused', last_tick_id = ?,
                           last_tick_state = ?,
                           last_error_code = 'tick_enqueue_failed', updated_at = ?
                       WHERE schedule_id = ?""",
                    (
                        tick["tick_id"] if tick is not None else None,
                        tick["state"] if tick is not None else None,
                        now_text,
                        schedule_id,
                    ),
                )
                self._event(
                    conn,
                    schedule_id=schedule_id,
                    event_type="paused",
                    boundary=_timestamp(request_boundary),
                    tick_id=tick["tick_id"] if tick is not None else None,
                    occurred_at=now_text,
                    payload={"safe_error_code": "tick_enqueue_failed"},
                )
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            finally:
                conn.close()
            raise
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            prior = conn.execute(
                """SELECT last_tick_id FROM service_tick_schedules
                   WHERE schedule_id = ?""",
                (schedule_id,),
            ).fetchone()
            conn.execute(
                """UPDATE service_tick_schedules
                   SET state = 'active', last_tick_id = ?, last_tick_state = ?,
                       last_error_code = NULL, updated_at = ?
                   WHERE schedule_id = ?""",
                (receipt.tick_id, receipt.state.value, now_text, schedule_id),
            )
            if prior is None or prior["last_tick_id"] != receipt.tick_id:
                self._event(
                    conn,
                    schedule_id=schedule_id,
                    event_type="tick_bound",
                    boundary=_timestamp(request_boundary),
                    tick_id=receipt.tick_id,
                    occurred_at=now_text,
                    payload={"tick_state": receipt.state.value},
                )
            elif (
                recovery_attempt_count is not None
                and len(receipt.execution_attempt_ids) > recovery_attempt_count
            ):
                self._event(
                    conn,
                    schedule_id=schedule_id,
                    event_type="resumed",
                    boundary=_timestamp(request_boundary),
                    tick_id=receipt.tick_id,
                    occurred_at=now_text,
                    payload={
                        "previous_attempt_count": recovery_attempt_count,
                        "current_attempt_count": len(receipt.execution_attempt_ids),
                    },
                )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
        return self.status()
