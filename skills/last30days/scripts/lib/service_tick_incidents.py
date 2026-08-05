"""Durable deterministic incidents, sequential notifications, and Guac gate."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Protocol
from urllib.parse import urlparse

import store

from .service_tick_media import MediaDerivativePublisher


Clock = Callable[[], datetime]
_INCIDENT_TYPES = frozenset(
    {
        "captcha_required",
        "cloudflare_challenge",
        "rate_limit_warning",
        "rate_limit_blocked",
        "reauthentication_required",
        "provider_degraded",
        "notification_exhausted",
    }
)
_BROWSER_INCIDENTS = frozenset(
    {
        "captcha_required",
        "cloudflare_challenge",
        "rate_limit_blocked",
        "reauthentication_required",
    }
)
_ISSUE_CODES = {
    "captcha": "captcha_required",
    "captcha_required": "captcha_required",
    "checkpoint_required": "captcha_required",
    "cloudflare": "cloudflare_challenge",
    "cloudflare_challenge": "cloudflare_challenge",
    "rate_limit_warning": "rate_limit_warning",
    "rate_limit_detected": "rate_limit_warning",
    "rate_limited": "rate_limit_blocked",
    "rate_limit_blocked": "rate_limit_blocked",
    "auth_required": "reauthentication_required",
    "profile_mismatch": "reauthentication_required",
    "reauthentication_required": "reauthentication_required",
    "provider_degraded": "provider_degraded",
}


def classify_provider_issue(
    safe_error_code: str | None, page_signals: Sequence[str]
) -> str | None:
    """Map exact adapter/page signals to incidents without model judgment."""
    for signal in page_signals:
        if signal in _ISSUE_CODES:
            return _ISSUE_CODES[signal]
    if safe_error_code is None:
        return None
    return _ISSUE_CODES.get(safe_error_code)


def _canonical_json(value: object) -> str:
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def _digest(value: object) -> str:
    return "sha256:" + hashlib.sha256(_canonical_json(value).encode()).hexdigest()


def _stable_id(prefix: str, value: object) -> str:
    return f"{prefix}-{hashlib.sha256(_canonical_json(value).encode()).hexdigest()[:32]}"


def _text(value: object, field: str, maximum: int = 4_096) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > maximum:
        raise ValueError(f"{field} must be a bounded non-empty string")
    return value


def _now(clock: Clock) -> str:
    value = clock()
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("clock must return a timezone-aware datetime")
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class IncidentSignal:
    tick_id: str
    lane_id: str
    source: str
    profile_ref: str
    stage: str
    incident_type: str
    severity: str
    safe_summary: str
    access_partition_id: str
    rendered_page: bytes | None = None
    rendered_page_mime_type: str | None = None
    operator_url: str | None = None

    def __post_init__(self) -> None:
        for field, maximum in (
            ("tick_id", 128),
            ("lane_id", 128),
            ("source", 64),
            ("profile_ref", 256),
            ("stage", 64),
            ("safe_summary", 4_096),
            ("access_partition_id", 256),
        ):
            _text(getattr(self, field), field, maximum)
        if self.incident_type not in _INCIDENT_TYPES:
            raise ValueError("incident_type is unsupported")
        if self.severity not in {"warning", "error", "critical"}:
            raise ValueError("incident severity is unsupported")
        if self.rendered_page is not None:
            if not isinstance(self.rendered_page, bytes) or not self.rendered_page:
                raise ValueError("rendered_page must be non-empty bytes")
            _text(self.rendered_page_mime_type, "rendered_page_mime_type", 256)
        if self.operator_url is not None:
            url = _text(self.operator_url, "operator_url", 4_096)
            parsed = urlparse(url)
            if (
                parsed.scheme != "https"
                or not parsed.hostname
                or parsed.hostname.casefold() in {"localhost", "127.0.0.1", "::1"}
            ):
                raise ValueError("operator_url must be an external HTTPS URL")


@dataclass(frozen=True)
class IncidentReceipt:
    incident_id: str
    fingerprint: str
    state: str
    incident_type: str
    occurrence_count: int
    protected_artifact_ref: str | None

    def to_dict(self) -> dict[str, object]:
        return {
            "incident_id": self.incident_id,
            "fingerprint": self.fingerprint,
            "state": self.state,
            "incident_type": self.incident_type,
            "occurrence_count": self.occurrence_count,
            "protected_artifact_ref": self.protected_artifact_ref,
        }


@dataclass(frozen=True)
class DeliveryReceipt:
    incident_id: str
    transport_id: str
    delivery_ref: str


class NotificationTransport(Protocol):
    transport_id: str

    def readiness(self) -> bool: ...

    def send(self, payload: Mapping[str, object]) -> str: ...


class NotificationExhaustedError(RuntimeError):
    pass


class NotificationPreflightError(RuntimeError):
    pass


class ObservationGateError(RuntimeError):
    pass


class IncidentManager:
    def __init__(
        self,
        db_path: Path,
        media: MediaDerivativePublisher,
        *,
        clock: Clock | None = None,
    ) -> None:
        self.db_path = Path(db_path)
        self.media = media
        self.clock = clock or (lambda: datetime.now(timezone.utc))
        store.init_db(self.db_path)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=5)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    @staticmethod
    def _receipt(row: sqlite3.Row) -> IncidentReceipt:
        return IncidentReceipt(
            incident_id=str(row["incident_id"]),
            fingerprint=str(row["fingerprint"]),
            state=str(row["state"]),
            incident_type=str(row["incident_type"]),
            occurrence_count=int(row["occurrence_count"]),
            protected_artifact_ref=(
                str(row["protected_artifact_ref"])
                if row["protected_artifact_ref"] is not None
                else None
            ),
        )

    @staticmethod
    def _row(conn: sqlite3.Connection, incident_id: str) -> sqlite3.Row:
        row = conn.execute(
            "SELECT * FROM service_incidents WHERE incident_id = ?", (incident_id,)
        ).fetchone()
        if row is None:
            raise KeyError(f"unknown incident: {incident_id}")
        return row

    def get(self, incident_id: str) -> IncidentReceipt:
        identifier = _text(incident_id, "incident_id", 128)
        conn = self._connect()
        try:
            return self._receipt(self._row(conn, identifier))
        finally:
            conn.close()

    def _append_transition(
        self,
        conn: sqlite3.Connection,
        *,
        incident_id: str,
        transition_type: str,
        from_state: str | None,
        to_state: str,
        tick_id: str,
        payload: Mapping[str, object],
        occurred_at: str,
    ) -> None:
        sequence = int(
            conn.execute(
                """SELECT COALESCE(MAX(sequence), 0) + 1
                   FROM service_incident_transitions WHERE incident_id = ?""",
                (incident_id,),
            ).fetchone()[0]
        )
        conn.execute(
            """INSERT INTO service_incident_transitions (
                   transition_id, incident_id, sequence, transition_type,
                   from_state, to_state, tick_id, safe_payload_json, occurred_at
               ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                _stable_id(
                    "incident-transition",
                    {"incident_id": incident_id, "sequence": sequence},
                ),
                incident_id,
                sequence,
                transition_type,
                from_state,
                to_state,
                tick_id,
                _canonical_json(dict(payload)),
                occurred_at,
            ),
        )

    def record(self, signal: IncidentSignal) -> IncidentReceipt:
        if not isinstance(signal, IncidentSignal):
            raise TypeError("signal must be IncidentSignal")
        now = _now(self.clock)
        fingerprint = _digest(
            {
                "source": signal.source,
                "profile_ref": signal.profile_ref,
                "stage": signal.stage,
                "incident_type": signal.incident_type,
            }
        )
        incident_id = _stable_id("incident", fingerprint)
        conn = self._connect()
        capture_required = False
        capture_reason = "detected"
        try:
            conn.execute("BEGIN IMMEDIATE")
            existing = conn.execute(
                "SELECT * FROM service_incidents WHERE fingerprint = ?",
                (fingerprint,),
            ).fetchone()
            if existing is None:
                conn.execute(
                    """INSERT INTO service_incidents (
                           incident_id, fingerprint, first_tick_id, last_tick_id,
                           lane_id, source, profile_ref, stage, incident_type,
                           severity, state, safe_summary, access_partition_id,
                           operator_url, occurrence_count, first_detected_at,
                           last_detected_at
                       ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'open', ?, ?, ?, 1, ?, ?)""",
                    (
                        incident_id,
                        fingerprint,
                        signal.tick_id,
                        signal.tick_id,
                        signal.lane_id,
                        signal.source,
                        signal.profile_ref,
                        signal.stage,
                        signal.incident_type,
                        signal.severity,
                        signal.safe_summary,
                        signal.access_partition_id,
                        signal.operator_url,
                        now,
                        now,
                    ),
                )
                self._append_transition(
                    conn,
                    incident_id=incident_id,
                    transition_type="detected",
                    from_state=None,
                    to_state="open",
                    tick_id=signal.tick_id,
                    payload={"severity": signal.severity},
                    occurred_at=now,
                )
                capture_required = signal.rendered_page is not None
            else:
                incident_id = str(existing["incident_id"])
                previous_state = str(existing["state"])
                next_state = "open" if previous_state == "resolved" else previous_state
                meaningful_change = (
                    signal.severity != existing["severity"]
                    or signal.safe_summary != existing["safe_summary"]
                    or previous_state == "resolved"
                )
                conn.execute(
                    """UPDATE service_incidents
                       SET last_tick_id = ?, lane_id = ?, severity = ?,
                           safe_summary = ?, occurrence_count = occurrence_count + 1,
                           last_detected_at = ?, state = ?,
                           operator_url = COALESCE(?, operator_url),
                           resolved_at = CASE WHEN ? = 'open' THEN NULL ELSE resolved_at END,
                           resolution_execution_id = CASE
                               WHEN ? = 'open' THEN NULL ELSE resolution_execution_id END
                       WHERE incident_id = ?""",
                    (
                        signal.tick_id,
                        signal.lane_id,
                        signal.severity,
                        signal.safe_summary,
                        now,
                        next_state,
                        signal.operator_url,
                        next_state,
                        next_state,
                        incident_id,
                    ),
                )
                if meaningful_change:
                    self._append_transition(
                        conn,
                        incident_id=incident_id,
                        transition_type="changed",
                        from_state=previous_state,
                        to_state=next_state,
                        tick_id=signal.tick_id,
                        payload={"severity": signal.severity},
                        occurred_at=now,
                    )
                    capture_required = signal.rendered_page is not None
                    capture_reason = "changed"
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

        if capture_required:
            asset = self.media.store_asset(
                parent_version_id=f"incident:{incident_id}",
                source_url=f"incident-rendered-page:{incident_id}",
                content=signal.rendered_page or b"",
                mime_type=signal.rendered_page_mime_type or "application/octet-stream",
                media_kind="rendered_page",
                alt_text=None,
                access_partition_id=signal.access_partition_id,
                retention_class="incident",
            )
            conn = self._connect()
            try:
                conn.execute(
                    """UPDATE service_incidents
                       SET protected_asset_id = ?, protected_artifact_ref = ?
                       WHERE incident_id = ?""",
                    (asset.asset_id, asset.storage_ref, incident_id),
                )
                conn.execute(
                    """INSERT OR IGNORE INTO service_incident_artifacts (
                           incident_artifact_id, incident_id, tick_id, asset_id,
                           artifact_ref, capture_reason, created_at
                       ) VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (
                        _stable_id(
                            "incident-artifact",
                            {
                                "incident_id": incident_id,
                                "tick_id": signal.tick_id,
                                "asset_id": asset.asset_id,
                            },
                        ),
                        incident_id,
                        signal.tick_id,
                        asset.asset_id,
                        asset.storage_ref,
                        capture_reason,
                        _now(self.clock),
                    ),
                )
                conn.commit()
            finally:
                conn.close()
        conn = self._connect()
        try:
            return self._receipt(self._row(conn, incident_id))
        finally:
            conn.close()

    def notify(
        self,
        incident_id: str,
        transports: Sequence[NotificationTransport],
        *,
        reminder_seconds: int | None = None,
    ) -> DeliveryReceipt:
        if not transports:
            raise ValueError("notification transport chain must not be empty")
        if reminder_seconds is not None and (
            isinstance(reminder_seconds, bool)
            or not isinstance(reminder_seconds, int)
            or reminder_seconds < 60
            or reminder_seconds > 604_800
        ):
            raise ValueError("reminder_seconds must be between 60 and 604800")
        conn = self._connect()
        try:
            incident = self._row(conn, incident_id)
            transition = conn.execute(
                """SELECT sequence, transition_type
                   FROM service_incident_transitions
                   WHERE incident_id = ?
                     AND transition_type IN ('detected', 'changed', 'resolved')
                   ORDER BY sequence DESC LIMIT 1""",
                (incident_id,),
            ).fetchone()
            if transition is None:
                raise RuntimeError("incident is missing a notifiable transition")
            kind = {
                "detected": "detected",
                "changed": "state_change",
                "resolved": "resolved",
            }[str(transition["transition_type"])]
            notification_sequence = int(transition["sequence"])
            prior = conn.execute(
                """SELECT transport_id, delivery_ref, attempted_at
                   FROM service_notification_deliveries
                   WHERE incident_id = ? AND notification_kind = ?
                     AND notification_sequence = ? AND state = 'success'
                   ORDER BY transport_ordinal LIMIT 1""",
                (incident_id, kind, notification_sequence),
            ).fetchone()
            if prior is not None and kind == "resolved":
                return DeliveryReceipt(
                    incident_id, str(prior["transport_id"]), str(prior["delivery_ref"])
                )
            if prior is not None:
                if reminder_seconds is None:
                    return DeliveryReceipt(
                        incident_id,
                        str(prior["transport_id"]),
                        str(prior["delivery_ref"]),
                    )
                last = conn.execute(
                    """SELECT transport_id, delivery_ref, attempted_at
                       FROM service_notification_deliveries
                       WHERE incident_id = ? AND state = 'success'
                       ORDER BY attempted_at DESC, notification_kind DESC LIMIT 1""",
                    (incident_id,),
                ).fetchone()
                now_dt = datetime.fromisoformat(_now(self.clock).replace("Z", "+00:00"))
                last_dt = datetime.fromisoformat(
                    str(last["attempted_at"]).replace("Z", "+00:00")
                )
                if (now_dt - last_dt).total_seconds() < reminder_seconds:
                    return DeliveryReceipt(
                        incident_id,
                        str(last["transport_id"]),
                        str(last["delivery_ref"]),
                    )
                kind = "reminder"
                notification_sequence = int(
                    conn.execute(
                        """SELECT COALESCE(MAX(notification_sequence), 0) + 1
                           FROM service_notification_deliveries
                           WHERE incident_id = ? AND notification_kind = 'reminder'""",
                        (incident_id,),
                    ).fetchone()[0]
                )
            payload = {
                "incident_id": incident_id,
                "notification_kind": kind,
                "notification_sequence": notification_sequence,
                "incident_type": incident["incident_type"],
                "severity": incident["severity"],
                "source": incident["source"],
                "stage": incident["stage"],
                "safe_summary": incident["safe_summary"],
                "protected_artifact_ref": incident["protected_artifact_ref"],
            }
        finally:
            conn.close()

        for ordinal, transport in enumerate(transports):
            transport_id = _text(transport.transport_id, "transport_id", 128)
            state = "failed"
            error_code = None
            delivery_ref = None
            try:
                if not transport.readiness():
                    raise RuntimeError("transport_not_ready")
                delivery_ref = _text(transport.send(payload), "delivery_ref", 512)
                state = "success"
            except Exception as exc:
                error_code = type(exc).__name__.casefold()
            attempted_at = _now(self.clock)
            conn = self._connect()
            try:
                conn.execute(
                        """INSERT OR IGNORE INTO service_notification_deliveries (
                           delivery_attempt_id, incident_id, tick_id, notification_kind,
                           notification_sequence, transport_ordinal, transport_id,
                           state, safe_error_code, delivery_ref, payload_digest,
                           attempted_at
                       ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        _stable_id(
                            "notification-attempt",
                            {
                                "incident_id": incident_id,
                                "kind": kind,
                                "sequence": notification_sequence,
                                "ordinal": ordinal,
                            },
                        ),
                        incident_id,
                        str(incident["last_tick_id"]),
                        kind,
                        notification_sequence,
                        ordinal,
                        transport_id,
                        state,
                        error_code,
                        delivery_ref,
                        _digest(payload),
                        attempted_at,
                    ),
                )
                conn.commit()
            finally:
                conn.close()
            if state == "success":
                return DeliveryReceipt(incident_id, transport_id, str(delivery_ref))
        self.record(
            IncidentSignal(
                tick_id=str(incident["last_tick_id"]),
                lane_id=str(incident["lane_id"]),
                source="notification",
                profile_ref=str(incident["profile_ref"]),
                stage="notification",
                incident_type="notification_exhausted",
                severity="critical",
                safe_summary="Every configured notification transport failed.",
                access_partition_id=str(incident["access_partition_id"]),
            )
        )
        raise NotificationExhaustedError(
            f"notification chain exhausted for incident {incident_id}"
        )

    def require_notification_readiness(
        self, transports: Sequence[NotificationTransport]
    ) -> str:
        """Perform only non-message readiness checks in configured order."""
        if not transports:
            raise NotificationPreflightError("notification transport chain is empty")
        for transport in transports:
            transport_id = _text(transport.transport_id, "transport_id", 128)
            try:
                if transport.readiness():
                    return transport_id
            except Exception:
                continue
        raise NotificationPreflightError(
            "no configured notification transport passed readiness"
        )

    def acknowledge(self, incident_id: str, *, actor_ref: str) -> IncidentReceipt:
        actor = _text(actor_ref, "actor_ref", 256)
        now = _now(self.clock)
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            row = self._row(conn, incident_id)
            if row["state"] == "resolved":
                raise ObservationGateError("resolved incident cannot be acknowledged")
            conn.execute(
                """UPDATE service_incidents
                   SET state = 'acknowledged', acknowledged_at = ?,
                       acknowledged_by_ref = ? WHERE incident_id = ?""",
                (now, actor, incident_id),
            )
            self._append_transition(
                conn,
                incident_id=incident_id,
                transition_type="acknowledged",
                from_state=str(row["state"]),
                to_state="acknowledged",
                tick_id=str(row["last_tick_id"]),
                payload={"actor_ref": actor},
                occurred_at=now,
            )
            result = self._receipt(self._row(conn, incident_id))
            conn.commit()
            return result
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def request_observation(self, incident_id: str) -> str:
        conn = self._connect()
        try:
            row = self._row(conn, incident_id)
            if row["state"] != "acknowledged":
                raise ObservationGateError("incident must be acknowledged first")
            if row["incident_type"] not in _BROWSER_INCIDENTS:
                raise ObservationGateError("incident does not allow browser observation")
            if row["operator_url"] is None:
                raise ObservationGateError(
                    "incident has no agent-browser external operator URL"
                )
            url = str(row["operator_url"])
            request_id = _stable_id("observation-request", incident_id)
            conn.execute(
                """INSERT OR IGNORE INTO service_incident_observations (
                       observation_request_id, incident_id, public_operator_url,
                       requested_at
                   ) VALUES (?, ?, ?, ?)""",
                (request_id, incident_id, url, _now(self.clock)),
            )
            existing = conn.execute(
                """SELECT public_operator_url FROM service_incident_observations
                   WHERE incident_id = ?""",
                (incident_id,),
            ).fetchone()[0]
            if existing != url:
                raise ObservationGateError("observation URL is already immutable")
            conn.commit()
            return url
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def resolve(
        self, incident_id: str, *, successful_execution_id: str
    ) -> IncidentReceipt:
        proof = _text(successful_execution_id, "successful_execution_id", 128)
        now = _now(self.clock)
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            row = self._row(conn, incident_id)
            if row["state"] == "resolved":
                if row["resolution_execution_id"] != proof:
                    raise ValueError("incident resolution proof is immutable")
                conn.commit()
                return self._receipt(row)
            conn.execute(
                """UPDATE service_incidents
                   SET state = 'resolved', resolved_at = ?,
                       resolution_execution_id = ? WHERE incident_id = ?""",
                (now, proof, incident_id),
            )
            self._append_transition(
                conn,
                incident_id=incident_id,
                transition_type="resolved",
                from_state=str(row["state"]),
                to_state="resolved",
                tick_id=str(row["last_tick_id"]),
                payload={"successful_execution_id": proof},
                occurred_at=now,
            )
            result = self._receipt(self._row(conn, incident_id))
            conn.commit()
            return result
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def resolve_matching(
        self,
        *,
        source: str,
        profile_ref: str,
        stage: str,
        successful_execution_id: str,
        transports: Sequence[NotificationTransport],
        reminder_seconds: int | None = None,
    ) -> tuple[IncidentReceipt, ...]:
        """Resolve only incidents matched to an exact successful provider lane."""
        source_value = _text(source, "source", 64)
        profile = _text(profile_ref, "profile_ref", 256)
        stage_value = _text(stage, "stage", 64)
        proof = _text(successful_execution_id, "successful_execution_id", 128)
        conn = self._connect()
        try:
            incident_ids = tuple(
                str(row[0])
                for row in conn.execute(
                    """SELECT incident_id FROM service_incidents
                       WHERE source = ? AND profile_ref = ? AND stage = ?
                         AND state <> 'resolved'
                       ORDER BY incident_id""",
                    (source_value, profile, stage_value),
                ).fetchall()
            )
        finally:
            conn.close()
        resolved = []
        for incident_id in incident_ids:
            receipt = self.resolve(
                incident_id,
                successful_execution_id=proof,
            )
            self.notify(
                incident_id,
                transports,
                reminder_seconds=reminder_seconds,
            )
            resolved.append(receipt)
        return tuple(resolved)
