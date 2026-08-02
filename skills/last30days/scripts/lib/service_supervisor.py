"""Deterministic, replayable control plane for refresh jobs.

This module deliberately knows nothing about source adapters, browsers, or
network clients.  It owns only durable scheduling policy: identity,
coalescing, leases, transitions, budgets, coverage gates, and safe readback.
"""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Callable, Iterable, Mapping

import store

from . import service_contracts as contracts


Clock = Callable[[], datetime]

_ACTIVE_STATES = frozenset(
    {
        contracts.JobState.QUEUED,
        contracts.JobState.PLANNING,
        contracts.JobState.ACQUIRING,
        contracts.JobState.NORMALIZING,
        contracts.JobState.INDEXING,
        contracts.JobState.ENRICHING,
        contracts.JobState.VALIDATING,
        contracts.JobState.AWAITING_OPERATOR,
    }
)
_LEASED_STATES = _ACTIVE_STATES - {
    contracts.JobState.QUEUED,
    contracts.JobState.AWAITING_OPERATOR,
}
_TERMINAL_STATES = frozenset(
    {
        contracts.JobState.PUBLISHED,
        contracts.JobState.PARTIAL,
        contracts.JobState.FAILED,
    }
)
_ALLOWED_TRANSITIONS: Mapping[
    contracts.JobState, frozenset[contracts.JobState]
] = {
    contracts.JobState.QUEUED: frozenset({contracts.JobState.PLANNING}),
    contracts.JobState.PLANNING: frozenset(
        {
            contracts.JobState.ACQUIRING,
            contracts.JobState.FAILED,
            contracts.JobState.AWAITING_OPERATOR,
        }
    ),
    contracts.JobState.ACQUIRING: frozenset(
        {
            contracts.JobState.NORMALIZING,
            contracts.JobState.PARTIAL,
            contracts.JobState.FAILED,
            contracts.JobState.AWAITING_OPERATOR,
        }
    ),
    contracts.JobState.NORMALIZING: frozenset(
        {
            contracts.JobState.INDEXING,
            contracts.JobState.PARTIAL,
            contracts.JobState.FAILED,
        }
    ),
    contracts.JobState.INDEXING: frozenset(
        {
            contracts.JobState.ENRICHING,
            contracts.JobState.VALIDATING,
            contracts.JobState.PARTIAL,
            contracts.JobState.FAILED,
        }
    ),
    contracts.JobState.ENRICHING: frozenset(
        {
            contracts.JobState.VALIDATING,
            contracts.JobState.PARTIAL,
            contracts.JobState.FAILED,
        }
    ),
    contracts.JobState.VALIDATING: frozenset(
        {
            contracts.JobState.PUBLISHED,
            contracts.JobState.PARTIAL,
            contracts.JobState.FAILED,
        }
    ),
    contracts.JobState.AWAITING_OPERATOR: frozenset(
        {contracts.JobState.QUEUED, contracts.JobState.FAILED}
    ),
}
_SAFE_CODE = re.compile(r"^[a-z0-9][a-z0-9_.-]{0,63}$")


class SupervisorError(RuntimeError):
    """Base class for deterministic policy failures."""


class InvalidTransitionError(SupervisorError):
    """Raised when a requested state transition is outside the state machine."""


class LeaseError(SupervisorError):
    """Raised when a worker does not own a live lease for a mutation."""


class BudgetExceededError(SupervisorError):
    """Raised before a job would exceed its configured monetary budget."""


@dataclass(frozen=True)
class EnqueueResult:
    job: contracts.JobRecord
    created: bool


@dataclass(frozen=True)
class JobSnapshot:
    job: contracts.JobRecord
    events: tuple[contracts.JobEvent, ...]
    remaining_budget_cents: int


@dataclass(frozen=True)
class CoverageRecord:
    profile_id: str
    normalized_query: str
    source: str
    status: contracts.AcquisitionStatus
    fetched_at: str
    fresh_until: str
    retry_after: str | None
    job_id: str | None
    index_version: str | None
    error_code: str | None
    updated_at: str


def normalize_query_scope(query: str) -> str:
    """Return the canonical query scope used by dedupe and coverage records."""
    if not isinstance(query, str) or not query.strip():
        raise ValueError("query must be a non-empty string")
    return " ".join(query.split()).casefold()


def normalize_sources(sources: Iterable[str]) -> tuple[str, ...]:
    """Return a stable, unique, case-insensitive source set."""
    if isinstance(sources, (str, bytes)):
        raise ValueError("sources must be an iterable of source names")
    items = tuple(sources)
    if not items or any(
        not isinstance(source, str) or not source.strip() for source in items
    ):
        raise ValueError("sources must contain only non-empty source names")
    normalized = {" ".join(source.split()).casefold() for source in items}
    if not normalized:
        raise ValueError("sources must contain at least one source")
    return tuple(sorted(normalized))


def refresh_dedupe_key(
    *,
    query: str,
    sources: Iterable[str],
    profile_id: str,
    freshness_window_seconds: int,
) -> str:
    """Return a content-addressed identity for an in-flight refresh scope."""
    if not isinstance(profile_id, str) or not profile_id.strip():
        raise ValueError("profile_id must be a non-empty string")
    if (
        isinstance(freshness_window_seconds, bool)
        or not isinstance(freshness_window_seconds, int)
        or freshness_window_seconds < 0
    ):
        raise ValueError("freshness_window_seconds must be a non-negative integer")
    canonical = {
        "freshness_window_seconds": freshness_window_seconds,
        "profile_id": " ".join(profile_id.split()).casefold(),
        "query": normalize_query_scope(query),
        "sources": normalize_sources(sources),
    }
    encoded = json.dumps(
        canonical, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return f"refresh:v1:{hashlib.sha256(encoded).hexdigest()}"


class RefreshSupervisor:
    """Small public interface over the complete durable scheduling policy."""

    def __init__(self, db_path: Path, *, clock: Clock | None = None):
        self.db_path = Path(db_path)
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    def initialize(self) -> None:
        store.init_db(self.db_path)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=5)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA busy_timeout=5000")
        deadline = time.monotonic() + 5
        while True:
            try:
                conn.execute("PRAGMA journal_mode=WAL")
                break
            except sqlite3.OperationalError as exc:
                if (
                    "locked" not in str(exc).lower()
                    or time.monotonic() >= deadline
                ):
                    conn.close()
                    raise
                time.sleep(0.01)
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    def _now(self) -> datetime:
        value = self._clock()
        if value.tzinfo is None or value.utcoffset() is None:
            raise SupervisorError("clock must return a timezone-aware datetime")
        return value.astimezone(timezone.utc)

    @staticmethod
    def _format_time(value: datetime) -> str:
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")

    @staticmethod
    def _parse_time(value: str, field: str) -> datetime:
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except (AttributeError, ValueError) as exc:
            raise ValueError(f"{field} must be an ISO-8601 timestamp") from exc
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            raise ValueError(f"{field} must include a timezone")
        return parsed.astimezone(timezone.utc)

    def enqueue_refresh(
        self,
        *,
        query_request_id: str,
        query: str,
        sources: Iterable[str],
        profile_id: str,
        freshness_window_seconds: int,
        max_attempts: int,
        budget_cents: int,
        not_before_at: str | None = None,
    ) -> EnqueueResult:
        """Create or join the single active job for a normalized refresh scope."""
        if not isinstance(query_request_id, str) or not query_request_id.strip():
            raise ValueError("query_request_id must be a non-empty string")
        if (
            isinstance(max_attempts, bool)
            or not isinstance(max_attempts, int)
            or not 1 <= max_attempts <= 100
        ):
            raise ValueError("max_attempts must be between 1 and 100")
        if (
            isinstance(budget_cents, bool)
            or not isinstance(budget_cents, int)
            or not 0 <= budget_cents <= 10_000_000
        ):
            raise ValueError("budget_cents must be between 0 and 10000000")
        normalized_query = normalize_query_scope(query)
        normalized_sources = normalize_sources(sources)
        key = refresh_dedupe_key(
            query=normalized_query,
            sources=normalized_sources,
            profile_id=profile_id,
            freshness_window_seconds=freshness_window_seconds,
        )
        now = self._format_time(self._now())
        if not_before_at is not None:
            not_before_at = self._format_time(
                self._parse_time(not_before_at, "not_before_at")
            )
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            existing = self._select_active_by_dedupe(conn, key)
            if existing is not None:
                conn.commit()
                return EnqueueResult(self._job_from_row(existing), False)
            job_id = str(uuid.uuid4())
            conn.execute(
                """INSERT INTO service_jobs
                   (job_id, job_type, dedupe_key, state, query_request_id,
                    attempts, max_attempts, budget_cents, spent_cents,
                    lease_generation, lease_owner, lease_expires_at, not_before_at,
                    created_at, updated_at, published_index_version, error_code)
                   VALUES (?, ?, ?, ?, ?, 0, ?, ?, 0, 0, NULL, NULL, ?, ?, ?,
                           NULL, NULL)""",
                (
                    job_id,
                    contracts.JobType.REFRESH.value,
                    key,
                    contracts.JobState.QUEUED.value,
                    query_request_id.strip(),
                    max_attempts,
                    budget_cents,
                    not_before_at,
                    now,
                    now,
                ),
            )
            self._append_event(
                conn,
                job_id=job_id,
                event_type="job_enqueued",
                phase=contracts.JobState.QUEUED,
                occurred_at=now,
                payload={
                    "normalized_query": normalized_query,
                    "profile_id": " ".join(profile_id.split()).casefold(),
                    "sources": list(normalized_sources),
                    "freshness_window_seconds": freshness_window_seconds,
                },
            )
            row = self._select_job(conn, job_id)
            conn.commit()
            return EnqueueResult(self._job_from_row(row), True)
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    @staticmethod
    def _select_active_by_dedupe(
        conn: sqlite3.Connection, dedupe_key: str
    ) -> sqlite3.Row | None:
        placeholders = ",".join("?" for _ in _ACTIVE_STATES)
        return conn.execute(
            f"""SELECT * FROM service_jobs
                WHERE dedupe_key = ? AND state IN ({placeholders})
                LIMIT 1""",
            (dedupe_key, *(state.value for state in _ACTIVE_STATES)),
        ).fetchone()

    @staticmethod
    def _select_job(conn: sqlite3.Connection, job_id: str) -> sqlite3.Row:
        row = conn.execute(
            "SELECT * FROM service_jobs WHERE job_id = ?", (job_id,)
        ).fetchone()
        if row is None:
            raise KeyError(f"job not found: {job_id}")
        return row

    @staticmethod
    def _job_from_row(row: sqlite3.Row) -> contracts.JobRecord:
        return contracts.JobRecord.from_dict(
            {
                "schema_version": contracts.SCHEMA_VERSION,
                "job_id": row["job_id"],
                "job_type": row["job_type"],
                "dedupe_key": row["dedupe_key"],
                "state": row["state"],
                "query_request_id": row["query_request_id"],
                "attempts": row["attempts"],
                "max_attempts": row["max_attempts"],
                "budget_cents": row["budget_cents"],
                "spent_cents": row["spent_cents"],
                "lease_generation": row["lease_generation"],
                "lease_owner": row["lease_owner"],
                "lease_expires_at": row["lease_expires_at"],
                "not_before_at": row["not_before_at"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
                "published_index_version": row["published_index_version"],
                "error_code": row["error_code"],
            }
        )

    def get_job(self, job_id: str) -> contracts.JobRecord:
        conn = self._connect()
        try:
            return self._job_from_row(self._select_job(conn, job_id))
        finally:
            conn.close()

    def get_events(self, job_id: str) -> tuple[contracts.JobEvent, ...]:
        conn = self._connect()
        try:
            self._select_job(conn, job_id)
            rows = conn.execute(
                """SELECT * FROM service_job_events
                   WHERE job_id = ? ORDER BY sequence""",
                (job_id,),
            ).fetchall()
        finally:
            conn.close()
        return tuple(self._event_from_row(row) for row in rows)

    def get_snapshot(self, job_id: str) -> JobSnapshot:
        conn = self._connect()
        try:
            conn.execute("BEGIN")
            job = self._job_from_row(self._select_job(conn, job_id))
            rows = conn.execute(
                """SELECT * FROM service_job_events
                   WHERE job_id = ? ORDER BY sequence""",
                (job_id,),
            ).fetchall()
            conn.commit()
        finally:
            conn.close()
        return JobSnapshot(
            job=job,
            events=tuple(self._event_from_row(row) for row in rows),
            remaining_budget_cents=job.budget_cents - job.spent_cents,
        )

    def lease_next(
        self, *, worker_id: str, lease_seconds: int
    ) -> contracts.JobRecord | None:
        """Atomically recover expired work and claim the next eligible job.

        Every claim increments ``lease_generation``.  All later mutations must
        present that generation, fencing workers whose leases expired.
        """
        if not isinstance(worker_id, str) or not worker_id.strip():
            raise ValueError("worker_id must be a non-empty string")
        if (
            isinstance(lease_seconds, bool)
            or not isinstance(lease_seconds, int)
            or not 1 <= lease_seconds <= 86_400
        ):
            raise ValueError("lease_seconds must be between 1 and 86400")
        now_dt = self._now()
        now = self._format_time(now_dt)
        expires_at = self._format_time(now_dt + timedelta(seconds=lease_seconds))
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            self._recover_expired_leases(conn, now=now)
            row = conn.execute(
                """SELECT * FROM service_jobs
                   WHERE state = ?
                     AND attempts < max_attempts
                     AND (not_before_at IS NULL OR not_before_at <= ?)
                   ORDER BY created_at, job_id
                   LIMIT 1""",
                (contracts.JobState.QUEUED.value, now),
            ).fetchone()
            if row is None:
                conn.commit()
                return None
            generation = row["lease_generation"] + 1
            attempts = row["attempts"] + 1
            updated = conn.execute(
                """UPDATE service_jobs
                   SET state = ?, attempts = ?, lease_generation = ?,
                       lease_owner = ?, lease_expires_at = ?, updated_at = ?,
                       error_code = NULL
                   WHERE job_id = ? AND state = ?""",
                (
                    contracts.JobState.PLANNING.value,
                    attempts,
                    generation,
                    worker_id.strip(),
                    expires_at,
                    now,
                    row["job_id"],
                    contracts.JobState.QUEUED.value,
                ),
            )
            if updated.rowcount != 1:
                raise SupervisorError("atomic lease claim failed")
            self._append_event(
                conn,
                job_id=row["job_id"],
                event_type="lease_acquired",
                phase=contracts.JobState.PLANNING,
                occurred_at=now,
                payload={
                    "attempt": attempts,
                    "lease_generation": generation,
                },
            )
            claimed = self._job_from_row(self._select_job(conn, row["job_id"]))
            conn.commit()
            return claimed
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _recover_expired_leases(
        self, conn: sqlite3.Connection, *, now: str
    ) -> None:
        placeholders = ",".join("?" for _ in _LEASED_STATES)
        rows = conn.execute(
            f"""SELECT * FROM service_jobs
                WHERE state IN ({placeholders})
                  AND lease_owner IS NOT NULL
                  AND lease_expires_at <= ?
                ORDER BY lease_expires_at, job_id""",
            (*(state.value for state in _LEASED_STATES), now),
        ).fetchall()
        for row in rows:
            manual_retry_budget = bool(
                int(row["max_attempts"]) == 2
                and conn.execute(
                    """SELECT 1 FROM collection_runs
                       WHERE job_id = ? AND trigger_kind = 'manual'
                       LIMIT 1""",
                    (row["job_id"],),
                ).fetchone()
            )
            exhausted = (
                row["attempts"] >= row["max_attempts"] or manual_retry_budget
            )
            next_state = (
                contracts.JobState.FAILED
                if exhausted
                else contracts.JobState.QUEUED
            )
            error_code = (
                "manual_retry_evidence_missing"
                if manual_retry_budget
                else ("retry_exhausted" if exhausted else None)
            )
            conn.execute(
                """UPDATE service_jobs
                   SET state = ?, lease_owner = NULL, lease_expires_at = NULL,
                       updated_at = ?, error_code = ?
                   WHERE job_id = ? AND lease_generation = ?""",
                (
                    next_state.value,
                    now,
                    error_code,
                    row["job_id"],
                    row["lease_generation"],
                ),
            )
            self._append_event(
                conn,
                job_id=row["job_id"],
                event_type="lease_expired",
                phase=next_state,
                occurred_at=now,
                payload={
                    "attempt": row["attempts"],
                    "retry_scheduled": not exhausted,
                },
            )

    def transition(
        self,
        job_id: str,
        *,
        to_state: contracts.JobState,
        worker_id: str,
        lease_generation: int,
        payload: Mapping[str, object] | None = None,
        published_index_version: str | None = None,
        error_code: str | None = None,
    ) -> contracts.JobRecord:
        """Apply one fenced state transition and append its replay event."""
        try:
            to_state = contracts.JobState(to_state)
        except (TypeError, ValueError) as exc:
            raise InvalidTransitionError("unknown target state") from exc
        now = self._format_time(self._now())
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            row = self._select_job(conn, job_id)
            current = contracts.JobState(row["state"])
            self._assert_live_lease(
                row,
                worker_id=worker_id,
                lease_generation=lease_generation,
                now=now,
            )
            if to_state not in _ALLOWED_TRANSITIONS.get(current, frozenset()):
                raise InvalidTransitionError(
                    f"cannot transition job from {current.value} to {to_state.value}"
                )
            if (
                to_state
                in {contracts.JobState.PUBLISHED, contracts.JobState.PARTIAL}
                and not published_index_version
            ):
                raise InvalidTransitionError(
                    "published and partial jobs require published_index_version"
                )
            if error_code is not None and not _SAFE_CODE.fullmatch(error_code):
                raise ValueError("error_code must be a safe identifier")
            clears_lease = to_state in _TERMINAL_STATES or (
                to_state is contracts.JobState.AWAITING_OPERATOR
            )
            updated = conn.execute(
                """UPDATE service_jobs
                   SET state = ?, updated_at = ?,
                       published_index_version = COALESCE(?, published_index_version),
                       error_code = ?,
                       lease_owner = CASE WHEN ? THEN NULL ELSE lease_owner END,
                       lease_expires_at = CASE WHEN ? THEN NULL ELSE lease_expires_at END
                   WHERE job_id = ? AND lease_owner = ?
                     AND lease_generation = ? AND lease_expires_at > ?""",
                (
                    to_state.value,
                    now,
                    published_index_version,
                    error_code,
                    clears_lease,
                    clears_lease,
                    job_id,
                    worker_id.strip(),
                    lease_generation,
                    now,
                ),
            )
            if updated.rowcount != 1:
                raise LeaseError("worker lease is no longer current")
            event_payload: dict[str, object] = {
                "from_state": current.value,
                "to_state": to_state.value,
            }
            if payload:
                event_payload["result"] = dict(payload)
            if published_index_version:
                event_payload["published_index_version"] = published_index_version
            if error_code:
                event_payload["error_code"] = error_code
            self._append_event(
                conn,
                job_id=job_id,
                event_type="state_transitioned",
                phase=to_state,
                occurred_at=now,
                payload=event_payload,
            )
            job = self._job_from_row(self._select_job(conn, job_id))
            conn.commit()
            return job
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def renew_lease(
        self,
        job_id: str,
        *,
        worker_id: str,
        lease_generation: int,
        lease_seconds: int,
    ) -> contracts.JobRecord:
        """Extend a live fenced lease without changing its generation."""
        if (
            isinstance(lease_seconds, bool)
            or not isinstance(lease_seconds, int)
            or not 1 <= lease_seconds <= 86_400
        ):
            raise ValueError("lease_seconds must be between 1 and 86400")
        now_dt = self._now()
        now = self._format_time(now_dt)
        expires_at = self._format_time(now_dt + timedelta(seconds=lease_seconds))
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            row = self._select_job(conn, job_id)
            self._assert_live_lease(
                row,
                worker_id=worker_id,
                lease_generation=lease_generation,
                now=now,
            )
            updated = conn.execute(
                """UPDATE service_jobs
                   SET lease_expires_at = ?, updated_at = ?
                   WHERE job_id = ? AND lease_owner = ?
                     AND lease_generation = ? AND lease_expires_at > ?""",
                (
                    expires_at,
                    now,
                    job_id,
                    worker_id.strip(),
                    lease_generation,
                    now,
                ),
            )
            if updated.rowcount != 1:
                raise LeaseError("worker lease is no longer current")
            self._append_event(
                conn,
                job_id=job_id,
                event_type="lease_renewed",
                phase=contracts.JobState(row["state"]),
                occurred_at=now,
                payload={"lease_generation": lease_generation},
            )
            job = self._job_from_row(self._select_job(conn, job_id))
            conn.commit()
            return job
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def record_spend(
        self,
        job_id: str,
        *,
        amount_cents: int,
        worker_id: str,
        lease_generation: int,
    ) -> contracts.JobRecord:
        """Atomically reserve actual spend without crossing the job budget."""
        if (
            isinstance(amount_cents, bool)
            or not isinstance(amount_cents, int)
            or amount_cents <= 0
        ):
            raise ValueError("amount_cents must be a positive integer")
        now = self._format_time(self._now())
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            row = self._select_job(conn, job_id)
            self._assert_live_lease(
                row,
                worker_id=worker_id,
                lease_generation=lease_generation,
                now=now,
            )
            new_spent = row["spent_cents"] + amount_cents
            if new_spent > row["budget_cents"]:
                raise BudgetExceededError(
                    f"job budget exceeded by {new_spent - row['budget_cents']} cents"
                )
            updated = conn.execute(
                """UPDATE service_jobs
                   SET spent_cents = ?, updated_at = ?
                   WHERE job_id = ? AND lease_owner = ?
                     AND lease_generation = ? AND lease_expires_at > ?
                     AND spent_cents = ?""",
                (
                    new_spent,
                    now,
                    job_id,
                    worker_id.strip(),
                    lease_generation,
                    now,
                    row["spent_cents"],
                ),
            )
            if updated.rowcount != 1:
                raise LeaseError("worker lease is no longer current")
            self._append_event(
                conn,
                job_id=job_id,
                event_type="budget_spent",
                phase=contracts.JobState(row["state"]),
                occurred_at=now,
                payload={
                    "amount_cents": amount_cents,
                    "remaining_cents": row["budget_cents"] - new_spent,
                },
            )
            job = self._job_from_row(self._select_job(conn, job_id))
            conn.commit()
            return job
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def record_coverage(
        self,
        job_id: str,
        *,
        query: str,
        profile_id: str,
        source: str,
        status: contracts.AcquisitionStatus,
        fetched_at: str,
        fresh_until: str,
        retry_after: str | None,
        worker_id: str,
        lease_generation: int,
        index_version: str | None = None,
        error_code: str | None = None,
    ) -> CoverageRecord:
        """Upsert one normalized source coverage outcome under a live lease."""
        try:
            status = contracts.AcquisitionStatus(status)
        except (TypeError, ValueError) as exc:
            raise ValueError("invalid acquisition status") from exc
        normalized_query = normalize_query_scope(query)
        normalized_profile = self._normalize_name(profile_id, "profile_id")
        normalized_source = self._normalize_name(source, "source")
        fetched_at = self._format_time(self._parse_time(fetched_at, "fetched_at"))
        fresh_until = self._format_time(
            self._parse_time(fresh_until, "fresh_until")
        )
        if retry_after is not None:
            retry_after = self._format_time(
                self._parse_time(retry_after, "retry_after")
            )
        if error_code is not None and not _SAFE_CODE.fullmatch(error_code):
            raise ValueError("error_code must be a safe identifier")
        now = self._format_time(self._now())
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            row = self._select_job(conn, job_id)
            self._assert_live_lease(
                row,
                worker_id=worker_id,
                lease_generation=lease_generation,
                now=now,
            )
            conn.execute(
                """INSERT INTO service_query_coverage
                   (profile_id, normalized_query, source, status, fetched_at,
                    fresh_until, retry_after, job_id, index_version, error_code,
                    updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                   ON CONFLICT(profile_id, normalized_query, source) DO UPDATE SET
                       status = excluded.status,
                       fetched_at = excluded.fetched_at,
                       fresh_until = excluded.fresh_until,
                       retry_after = excluded.retry_after,
                       job_id = excluded.job_id,
                       index_version = excluded.index_version,
                       error_code = excluded.error_code,
                       updated_at = excluded.updated_at""",
                (
                    normalized_profile,
                    normalized_query,
                    normalized_source,
                    status.value,
                    fetched_at,
                    fresh_until,
                    retry_after,
                    job_id,
                    index_version,
                    error_code,
                    now,
                ),
            )
            self._append_event(
                conn,
                job_id=job_id,
                event_type="coverage_recorded",
                phase=contracts.JobState(row["state"]),
                occurred_at=now,
                payload={
                    "source": normalized_source,
                    "status": status.value,
                    "has_retry_after": retry_after is not None,
                },
            )
            coverage = self._select_coverage(
                conn,
                profile_id=normalized_profile,
                normalized_query=normalized_query,
                source=normalized_source,
            )
            conn.commit()
            return coverage
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def negative_cache_hits(
        self,
        *,
        query: str,
        profile_id: str,
        sources: Iterable[str],
    ) -> tuple[CoverageRecord, ...]:
        """Return failed source scopes whose deterministic retry gate is active."""
        normalized_query = normalize_query_scope(query)
        normalized_profile = self._normalize_name(profile_id, "profile_id")
        normalized_sources = normalize_sources(sources)
        placeholders = ",".join("?" for _ in normalized_sources)
        now = self._format_time(self._now())
        conn = self._connect()
        try:
            rows = conn.execute(
                f"""SELECT * FROM service_query_coverage
                    WHERE profile_id = ?
                      AND normalized_query = ?
                      AND source IN ({placeholders})
                      AND status IN (?, ?)
                      AND retry_after IS NOT NULL
                      AND retry_after > ?
                    ORDER BY source""",
                (
                    normalized_profile,
                    normalized_query,
                    *normalized_sources,
                    contracts.AcquisitionStatus.FAILED.value,
                    contracts.AcquisitionStatus.AWAITING_OPERATOR.value,
                    now,
                ),
            ).fetchall()
        finally:
            conn.close()
        return tuple(self._coverage_from_row(row) for row in rows)

    def coverage_for(
        self,
        *,
        query: str,
        profile_id: str,
        sources: Iterable[str],
    ) -> tuple[CoverageRecord, ...]:
        """Return durable coverage for the requested normalized source scopes."""
        normalized_query = normalize_query_scope(query)
        normalized_profile = self._normalize_name(profile_id, "profile_id")
        normalized_sources = normalize_sources(sources)
        placeholders = ",".join("?" for _ in normalized_sources)
        conn = self._connect()
        try:
            rows = conn.execute(
                f"""SELECT * FROM service_query_coverage
                    WHERE profile_id = ?
                      AND normalized_query = ?
                      AND source IN ({placeholders})
                    ORDER BY source""",
                (
                    normalized_profile,
                    normalized_query,
                    *normalized_sources,
                ),
            ).fetchall()
        finally:
            conn.close()
        return tuple(self._coverage_from_row(row) for row in rows)

    def handle_failure(
        self,
        job_id: str,
        *,
        error_code: str,
        retryable: bool,
        retry_after: str | None,
        awaiting_operator: bool,
        worker_id: str,
        lease_generation: int,
    ) -> contracts.JobRecord:
        """Classify a worker failure into retry, terminal, or operator state."""
        if not _SAFE_CODE.fullmatch(error_code):
            raise ValueError("error_code must be a safe identifier")
        if not isinstance(retryable, bool) or not isinstance(awaiting_operator, bool):
            raise ValueError("failure classifications must be booleans")
        if awaiting_operator and retryable:
            raise ValueError("awaiting_operator failures cannot also be retryable")
        if retry_after is not None:
            retry_after = self._format_time(
                self._parse_time(retry_after, "retry_after")
            )
        now = self._format_time(self._now())
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            row = self._select_job(conn, job_id)
            self._assert_live_lease(
                row,
                worker_id=worker_id,
                lease_generation=lease_generation,
                now=now,
            )
            if contracts.JobState(row["state"]) not in _LEASED_STATES:
                raise InvalidTransitionError("only active leased work can fail")
            if awaiting_operator:
                next_state = contracts.JobState.AWAITING_OPERATOR
                not_before_at = None
                event_type = "awaiting_operator"
            elif retryable and row["attempts"] < row["max_attempts"]:
                next_state = contracts.JobState.QUEUED
                not_before_at = retry_after or now
                event_type = "retry_scheduled"
            else:
                next_state = contracts.JobState.FAILED
                not_before_at = None
                event_type = "job_failed"
            updated = conn.execute(
                """UPDATE service_jobs
                   SET state = ?, not_before_at = ?, error_code = ?,
                       lease_owner = NULL, lease_expires_at = NULL, updated_at = ?
                   WHERE job_id = ? AND lease_owner = ?
                     AND lease_generation = ? AND lease_expires_at > ?""",
                (
                    next_state.value,
                    not_before_at,
                    error_code,
                    now,
                    job_id,
                    worker_id.strip(),
                    lease_generation,
                    now,
                ),
            )
            if updated.rowcount != 1:
                raise LeaseError("worker lease is no longer current")
            self._append_event(
                conn,
                job_id=job_id,
                event_type=event_type,
                phase=next_state,
                occurred_at=now,
                payload={
                    "error_code": error_code,
                    "retryable": retryable,
                    "retry_after": not_before_at,
                },
            )
            job = self._job_from_row(self._select_job(conn, job_id))
            conn.commit()
            return job
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def resume_after_operator(
        self, job_id: str, *, not_before_at: str | None = None
    ) -> contracts.JobRecord:
        """Return operator-unblocked work to the queue without acquiring it."""
        now = self._format_time(self._now())
        if not_before_at is not None:
            not_before_at = self._format_time(
                self._parse_time(not_before_at, "not_before_at")
            )
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            row = self._select_job(conn, job_id)
            if row["state"] != contracts.JobState.AWAITING_OPERATOR.value:
                raise InvalidTransitionError(
                    "only awaiting_operator jobs can be resumed"
                )
            if row["attempts"] >= row["max_attempts"]:
                raise InvalidTransitionError(
                    "operator-unblocked job has exhausted its attempts"
                )
            conn.execute(
                """UPDATE service_jobs
                   SET state = ?, not_before_at = ?, error_code = NULL,
                       updated_at = ?
                   WHERE job_id = ? AND state = ?""",
                (
                    contracts.JobState.QUEUED.value,
                    not_before_at,
                    now,
                    job_id,
                    contracts.JobState.AWAITING_OPERATOR.value,
                ),
            )
            self._append_event(
                conn,
                job_id=job_id,
                event_type="operator_resumed",
                phase=contracts.JobState.QUEUED,
                occurred_at=now,
                payload={"scheduled": not_before_at is not None},
            )
            job = self._job_from_row(self._select_job(conn, job_id))
            conn.commit()
            return job
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    @staticmethod
    def _normalize_name(value: str, field: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field} must be a non-empty string")
        return " ".join(value.split()).casefold()

    def _select_coverage(
        self,
        conn: sqlite3.Connection,
        *,
        profile_id: str,
        normalized_query: str,
        source: str,
    ) -> CoverageRecord:
        row = conn.execute(
            """SELECT * FROM service_query_coverage
               WHERE profile_id = ? AND normalized_query = ? AND source = ?""",
            (profile_id, normalized_query, source),
        ).fetchone()
        if row is None:
            raise SupervisorError("coverage write was not persisted")
        return self._coverage_from_row(row)

    @staticmethod
    def _coverage_from_row(row: sqlite3.Row) -> CoverageRecord:
        try:
            status = contracts.AcquisitionStatus(row["status"])
        except ValueError as exc:
            raise SupervisorError("invalid persisted coverage status") from exc
        return CoverageRecord(
            profile_id=row["profile_id"],
            normalized_query=row["normalized_query"],
            source=row["source"],
            status=status,
            fetched_at=row["fetched_at"],
            fresh_until=row["fresh_until"],
            retry_after=row["retry_after"],
            job_id=row["job_id"],
            index_version=row["index_version"],
            error_code=row["error_code"],
            updated_at=row["updated_at"],
        )

    @staticmethod
    def _assert_live_lease(
        row: sqlite3.Row,
        *,
        worker_id: str,
        lease_generation: int,
        now: str,
    ) -> None:
        if (
            row["lease_owner"] != worker_id.strip()
            or row["lease_generation"] != lease_generation
            or row["lease_expires_at"] is None
            or row["lease_expires_at"] <= now
        ):
            raise LeaseError("worker lease is no longer current")

    @staticmethod
    def _event_from_row(row: sqlite3.Row) -> contracts.JobEvent:
        try:
            payload = json.loads(row["payload_json"])
        except json.JSONDecodeError as exc:
            raise SupervisorError(
                f"invalid event payload for {row['event_id']}"
            ) from exc
        return contracts.JobEvent.from_dict(
            {
                "schema_version": contracts.SCHEMA_VERSION,
                "event_id": row["event_id"],
                "job_id": row["job_id"],
                "sequence": row["sequence"],
                "event_type": row["event_type"],
                "phase": row["phase"],
                "occurred_at": row["occurred_at"],
                "payload": payload,
                "redaction_class": row["redaction_class"],
            }
        )

    @staticmethod
    def _append_event(
        conn: sqlite3.Connection,
        *,
        job_id: str,
        event_type: str,
        phase: contracts.JobState,
        occurred_at: str,
        payload: Mapping[str, object],
        redaction_class: contracts.RedactionClass = contracts.RedactionClass.PUBLIC,
    ) -> contracts.JobEvent:
        sequence = conn.execute(
            """SELECT COALESCE(MAX(sequence), 0) + 1
               FROM service_job_events WHERE job_id = ?""",
            (job_id,),
        ).fetchone()[0]
        event = contracts.JobEvent.from_dict(
            {
                "schema_version": contracts.SCHEMA_VERSION,
                "event_id": str(uuid.uuid4()),
                "job_id": job_id,
                "sequence": sequence,
                "event_type": event_type,
                "phase": phase.value,
                "occurred_at": occurred_at,
                "payload": dict(payload),
                "redaction_class": redaction_class.value,
            }
        )
        conn.execute(
            """INSERT INTO service_job_events
               (event_id, job_id, sequence, event_type, phase, occurred_at,
                payload_json, redaction_class)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                event.event_id,
                event.job_id,
                event.sequence,
                event.event_type,
                event.phase.value,
                event.occurred_at,
                json.dumps(
                    event.payload,
                    ensure_ascii=False,
                    allow_nan=False,
                    separators=(",", ":"),
                    sort_keys=True,
                ),
                event.redaction_class.value,
            ),
        )
        return event
