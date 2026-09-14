"""Durable provider-free question workflow over frozen stored-post evidence."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Protocol, Sequence

import store

from . import service_contracts as contracts
from . import service_question_contracts as question_contracts


Clock = Callable[[], datetime]
QUESTION_SCHEMA_VERSION = 1

_QUESTION_MIGRATION_V1 = """
BEGIN IMMEDIATE;
CREATE TABLE IF NOT EXISTS service_question_schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS service_question_requests (
    request_id TEXT PRIMARY KEY,
    request_fingerprint TEXT NOT NULL,
    request_json TEXT NOT NULL,
    request_digest TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS service_question_retrievals (
    question_id TEXT PRIMARY KEY,
    request_id TEXT NOT NULL REFERENCES service_question_requests(request_id),
    search_head_id TEXT NOT NULL,
    evidence_set_id TEXT NOT NULL,
    access_partitions_digest TEXT NOT NULL,
    retrieval_json TEXT NOT NULL,
    retrieval_digest TEXT NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE (request_id, search_head_id, evidence_set_id, access_partitions_digest)
);
CREATE TABLE IF NOT EXISTS service_question_tasks (
    question_id TEXT PRIMARY KEY REFERENCES service_question_retrievals(question_id),
    idempotency_key TEXT NOT NULL UNIQUE,
    state TEXT NOT NULL CHECK (
        state IN (
            'pending', 'running', 'answered', 'no_evidence',
            'insufficient_evidence', 'conflicting_evidence',
            'model_unavailable', 'failed'
        )
    ),
    attempt_count INTEGER NOT NULL DEFAULT 0 CHECK (attempt_count >= 0),
    max_attempts INTEGER NOT NULL CHECK (max_attempts IN (1, 2)),
    lease_owner TEXT,
    lease_generation INTEGER NOT NULL DEFAULT 0 CHECK (lease_generation >= 0),
    lease_expires_at TEXT,
    answer_id TEXT,
    error_json TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS service_question_tasks_ready
    ON service_question_tasks(state, created_at, question_id);
CREATE TABLE IF NOT EXISTS service_question_attempts (
    question_id TEXT NOT NULL REFERENCES service_question_tasks(question_id),
    attempt_number INTEGER NOT NULL CHECK (attempt_number > 0),
    lease_generation INTEGER NOT NULL CHECK (lease_generation > 0),
    worker_id TEXT NOT NULL,
    started_at TEXT NOT NULL,
    PRIMARY KEY (question_id, attempt_number),
    UNIQUE (question_id, lease_generation)
);
CREATE TABLE IF NOT EXISTS service_question_answers (
    answer_id TEXT PRIMARY KEY,
    question_id TEXT NOT NULL UNIQUE REFERENCES service_question_tasks(question_id),
    answer_json TEXT NOT NULL,
    output_digest TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS service_question_failures (
    failure_id TEXT PRIMARY KEY,
    question_id TEXT NOT NULL REFERENCES service_question_tasks(question_id),
    attempt_count INTEGER NOT NULL CHECK (attempt_count >= 0),
    error_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE (question_id, attempt_count, error_json)
);
CREATE TRIGGER IF NOT EXISTS service_question_requests_immutable_update
BEFORE UPDATE ON service_question_requests BEGIN
    SELECT RAISE(ABORT, 'question request is immutable');
END;
CREATE TRIGGER IF NOT EXISTS service_question_requests_immutable_delete
BEFORE DELETE ON service_question_requests BEGIN
    SELECT RAISE(ABORT, 'question request is immutable');
END;
CREATE TRIGGER IF NOT EXISTS service_question_retrievals_immutable_update
BEFORE UPDATE ON service_question_retrievals BEGIN
    SELECT RAISE(ABORT, 'question retrieval is immutable');
END;
CREATE TRIGGER IF NOT EXISTS service_question_retrievals_immutable_delete
BEFORE DELETE ON service_question_retrievals BEGIN
    SELECT RAISE(ABORT, 'question retrieval is immutable');
END;
CREATE TRIGGER IF NOT EXISTS service_question_attempts_immutable_update
BEFORE UPDATE ON service_question_attempts BEGIN
    SELECT RAISE(ABORT, 'question attempt is immutable');
END;
CREATE TRIGGER IF NOT EXISTS service_question_attempts_immutable_delete
BEFORE DELETE ON service_question_attempts BEGIN
    SELECT RAISE(ABORT, 'question attempt is immutable');
END;
CREATE TRIGGER IF NOT EXISTS service_question_answers_immutable_update
BEFORE UPDATE ON service_question_answers BEGIN
    SELECT RAISE(ABORT, 'question answer is immutable');
END;
CREATE TRIGGER IF NOT EXISTS service_question_answers_immutable_delete
BEFORE DELETE ON service_question_answers BEGIN
    SELECT RAISE(ABORT, 'question answer is immutable');
END;
CREATE TRIGGER IF NOT EXISTS service_question_failures_immutable_update
BEFORE UPDATE ON service_question_failures BEGIN
    SELECT RAISE(ABORT, 'question failure is immutable');
END;
CREATE TRIGGER IF NOT EXISTS service_question_failures_immutable_delete
BEFORE DELETE ON service_question_failures BEGIN
    SELECT RAISE(ABORT, 'question failure is immutable');
END;
INSERT OR IGNORE INTO service_question_schema_version(version) VALUES (1);
COMMIT;
"""


class QuestionRequestConflict(RuntimeError):
    """Raised when a caller reuses a request ID for different normalized input."""


class QuestionLeaseError(RuntimeError):
    """Raised when a worker tries to mutate a task without its current lease."""


class QuestionValidationError(RuntimeError):
    """A safe deterministic rejection of worker output."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = question_contracts.validate_error_code(code)


class QuestionWorkerError(RuntimeError):
    """A fake/no-tool worker failure with an explicit retry classification."""

    def __init__(self, code: str, message: str, *, retryable: bool) -> None:
        super().__init__(message)
        self.code = question_contracts.validate_error_code(code)
        self.retryable = retryable


class PostSearchBackend(Protocol):
    def search(
        self,
        request: contracts.PostSearchRequest,
        *,
        access_partitions: Sequence[str],
    ) -> contracts.PostSearchResponse: ...


class NoToolAnswerWorker(Protocol):
    worker_ref: str

    def answer(
        self, payload: Mapping[str, Any]
    ) -> Mapping[str, Any] | AnswerWorkerResult: ...


@dataclass(frozen=True)
class AnswerWorkerResult:
    """Worker output plus host-owned execution identity and effect receipts."""

    output: object
    worker_ref: str
    model_invoked: bool
    evidence_only_fallback: bool = False


def _timestamp(value: datetime) -> str:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("clock must return a timezone-aware datetime")
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _parse_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(
        timezone.utc
    )


def _connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path), timeout=5)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout=5000")
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def migrate_question_schema(db_path: Path) -> None:
    """Apply the additive question-owned schema without changing service ABI."""
    conn = _connect(db_path)
    try:
        row = conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' "
            "AND name = 'service_question_schema_version'"
        ).fetchone()
        if row is not None:
            current = conn.execute(
                "SELECT COALESCE(MAX(version), 0) FROM service_question_schema_version"
            ).fetchone()[0]
            if int(current) > QUESTION_SCHEMA_VERSION:
                raise RuntimeError(
                    "question database schema is newer than this runtime"
                )
        conn.executescript(_QUESTION_MIGRATION_V1)
    except Exception:
        if conn.in_transaction:
            conn.rollback()
        raise
    finally:
        conn.close()


@dataclass(frozen=True)
class QuestionLease:
    question_id: str
    lease_generation: int
    attempt_count: int
    worker_id: str
    request: question_contracts.QuestionRequestV1
    retrieval: dict[str, Any]


class QuestionQueue:
    """Deep queue module owning replay, leases, attempts, and terminal receipts."""

    def __init__(self, db_path: Path, *, clock: Clock | None = None) -> None:
        self.db_path = Path(db_path)
        self.clock = clock or (lambda: datetime.now(timezone.utc))
        store.init_db(self.db_path)
        migrate_question_schema(self.db_path)

    def _now(self) -> datetime:
        value = self.clock()
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("clock must return a timezone-aware datetime")
        return value.astimezone(timezone.utc)

    def enqueue(
        self,
        request: question_contracts.QuestionRequestV1,
        retrieval: Mapping[str, Any],
    ) -> question_contracts.QuestionStatusV1:
        request_json = question_contracts.canonical_json(request.to_dict())
        request_digest = question_contracts.digest(request.to_dict())
        retrieval_json = question_contracts.canonical_json(retrieval)
        retrieval_digest = question_contracts.digest(retrieval)
        question_id = str(retrieval["question_id"])
        idempotency_key = "question-task:v1:" + question_id.removeprefix("question-")
        now = _timestamp(self._now())
        conn = _connect(self.db_path)
        try:
            conn.execute("BEGIN IMMEDIATE")
            existing_request = conn.execute(
                "SELECT request_fingerprint FROM service_question_requests WHERE request_id = ?",
                (request.request_id,),
            ).fetchone()
            if (
                existing_request is not None
                and existing_request["request_fingerprint"] != request.request_fingerprint
            ):
                raise QuestionRequestConflict(
                    f"request_id {request.request_id!r} was reused with different content"
                )
            conn.execute(
                """INSERT OR IGNORE INTO service_question_requests
                   (request_id, request_fingerprint, request_json, request_digest, created_at)
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    request.request_id,
                    request.request_fingerprint,
                    request_json,
                    request_digest,
                    now,
                ),
            )
            conn.execute(
                """INSERT OR IGNORE INTO service_question_retrievals
                   (question_id, request_id, search_head_id, evidence_set_id,
                    access_partitions_digest, retrieval_json, retrieval_digest, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    question_id,
                    request.request_id,
                    retrieval["search_head_id"],
                    retrieval["evidence_set_id"],
                    retrieval["access_partitions_digest"],
                    retrieval_json,
                    retrieval_digest,
                    now,
                ),
            )
            conn.execute(
                """INSERT OR IGNORE INTO service_question_tasks
                   (question_id, idempotency_key, state, max_attempts,
                    created_at, updated_at)
                   VALUES (?, ?, 'pending', ?, ?, ?)""",
                (question_id, idempotency_key, request.limits.max_attempts, now, now),
            )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
        return self.status(question_id)

    def status(self, question_id: str) -> question_contracts.QuestionStatusV1:
        conn = _connect(self.db_path)
        try:
            row = conn.execute(
                """SELECT t.*, a.answer_json
                   FROM service_question_tasks AS t
                   LEFT JOIN service_question_answers AS a ON a.answer_id = t.answer_id
                   WHERE t.question_id = ?""",
                (question_id,),
            ).fetchone()
        finally:
            conn.close()
        if row is None:
            raise KeyError(f"question not found: {question_id}")
        return question_contracts.QuestionStatusV1.from_dict(
            {
                "schema_version": 1,
                "question_id": row["question_id"],
                "state": row["state"],
                "attempt_count": row["attempt_count"],
                "max_attempts": row["max_attempts"],
                "lease_generation": row["lease_generation"],
                "lease_expires_at": row["lease_expires_at"],
                "answer": json.loads(row["answer_json"]) if row["answer_json"] else None,
                "error": json.loads(row["error_json"]) if row["error_json"] else None,
            }
        )

    @staticmethod
    def _record_failure(
        conn: sqlite3.Connection,
        *,
        question_id: str,
        attempt_count: int,
        error: question_contracts.QuestionErrorV1,
        created_at: str,
    ) -> None:
        error_json = question_contracts.canonical_json(error.to_dict())
        failure_id = question_contracts.stable_id(
            "question-failure",
            {
                "question_id": question_id,
                "attempt_count": attempt_count,
                "error": error.to_dict(),
            },
        )
        conn.execute(
            """INSERT OR IGNORE INTO service_question_failures
               (failure_id, question_id, attempt_count, error_json, created_at)
               VALUES (?, ?, ?, ?, ?)""",
            (failure_id, question_id, attempt_count, error_json, created_at),
        )

    def claim_next(
        self,
        *,
        worker_id: str,
        lease_seconds: int = 120,
        question_id: str | None = None,
    ) -> QuestionLease | None:
        if not isinstance(worker_id, str) or not worker_id.strip():
            raise ValueError("worker_id must be non-empty")
        if not isinstance(lease_seconds, int) or isinstance(lease_seconds, bool) or not 1 <= lease_seconds <= 3600:
            raise ValueError("lease_seconds must be between 1 and 3600")
        now_dt = self._now()
        now = _timestamp(now_dt)
        expires_at = _timestamp(now_dt + timedelta(seconds=lease_seconds))
        conn = _connect(self.db_path)
        try:
            conn.execute("BEGIN IMMEDIATE")
            expired = conn.execute(
                """SELECT question_id, attempt_count, max_attempts
                   FROM service_question_tasks
                   WHERE state = 'running' AND lease_expires_at <= ?
                     AND (? IS NULL OR question_id = ?)
                   ORDER BY lease_expires_at, question_id""",
                (now, question_id, question_id),
            ).fetchall()
            for row in expired:
                exhausted = int(row["attempt_count"]) >= int(row["max_attempts"])
                error = question_contracts.QuestionErrorV1.from_dict(
                    {
                        "code": "call_bound_exhausted" if exhausted else "lease_expired",
                        "message": (
                            "question worker attempt bound exhausted"
                            if exhausted
                            else "question worker lease expired"
                        ),
                        "retryable": not exhausted,
                    }
                )
                self._record_failure(
                    conn,
                    question_id=row["question_id"],
                    attempt_count=row["attempt_count"],
                    error=error,
                    created_at=now,
                )
                conn.execute(
                    """UPDATE service_question_tasks
                       SET state = ?, lease_owner = NULL, lease_expires_at = NULL,
                           error_json = ?, updated_at = ?
                       WHERE question_id = ? AND state = 'running'""",
                    (
                        "failed" if exhausted else "pending",
                        question_contracts.canonical_json(error.to_dict()) if exhausted else None,
                        now,
                        row["question_id"],
                    ),
                )
            row = conn.execute(
                """SELECT t.*, r.retrieval_json, q.request_json
                   FROM service_question_tasks AS t
                   JOIN service_question_retrievals AS r USING (question_id)
                   JOIN service_question_requests AS q USING (request_id)
                   WHERE t.state = 'pending' AND (? IS NULL OR t.question_id = ?)
                   ORDER BY t.created_at, t.question_id
                   LIMIT 1""",
                (question_id, question_id),
            ).fetchone()
            if row is None:
                conn.commit()
                return None
            generation = int(row["lease_generation"]) + 1
            attempt_count = int(row["attempt_count"]) + 1
            conn.execute(
                """UPDATE service_question_tasks
                   SET state = 'running', attempt_count = ?, lease_owner = ?,
                       lease_generation = ?, lease_expires_at = ?,
                       error_json = NULL, updated_at = ?
                   WHERE question_id = ? AND state = 'pending'""",
                (
                    attempt_count,
                    worker_id,
                    generation,
                    expires_at,
                    now,
                    row["question_id"],
                ),
            )
            conn.execute(
                """INSERT INTO service_question_attempts
                   (question_id, attempt_number, lease_generation, worker_id, started_at)
                   VALUES (?, ?, ?, ?, ?)""",
                (row["question_id"], attempt_count, generation, worker_id, now),
            )
            conn.commit()
            return QuestionLease(
                question_id=row["question_id"],
                lease_generation=generation,
                attempt_count=attempt_count,
                worker_id=worker_id,
                request=question_contracts.QuestionRequestV1.from_dict(
                    json.loads(row["request_json"])
                ),
                retrieval=json.loads(row["retrieval_json"]),
            )
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def complete(
        self,
        lease: QuestionLease,
        answer: question_contracts.QuestionAnswerV1,
    ) -> question_contracts.QuestionStatusV1:
        if answer.question_id != lease.question_id:
            raise QuestionLeaseError("answer question_id does not match lease")
        expected_input_digest = question_contracts.digest(
            {"request": lease.request.to_dict(), "retrieval": lease.retrieval}
        )
        expected_citations = {
            item["evidence_id"]: {
                key: item[key]
                for key in (
                    "evidence_id",
                    "storage_family",
                    "version_id",
                    "content_hash",
                    "source_url",
                    "access_partition_id",
                )
            }
            for item in lease.retrieval["evidence"]
        }
        citations_close = all(
            citation.evidence_id in expected_citations
            and citation.to_dict() == expected_citations[citation.evidence_id]
            for statement in answer.statements
            for citation in statement.citations
        )
        expected_coverage = {
            "partial": lease.retrieval["coverage"]["partial"],
            "stale": lease.retrieval["coverage"]["stale"],
        }
        if (
            answer.request_fingerprint != lease.request.request_fingerprint
            or answer.search_head_id != lease.retrieval["search_head_id"]
            or answer.evidence_set_id != lease.retrieval["evidence_set_id"]
            or answer.input_digest != expected_input_digest
            or answer.attempt_count != lease.attempt_count
            or answer.coverage != expected_coverage
            or not citations_close
            or (answer.evidence_only_fallback and answer.model_invoked)
            or (
                answer.evidence_only_fallback
                and answer.worker_ref != "deterministic-evidence-fallback-v1"
            )
            or (
                answer.evidence_only_fallback
                and (
                    lease.request.model_fallback != "evidence_only"
                    or answer.error is None
                    or answer.error.code != "model_unavailable"
                )
            )
            or (
                answer.model_invoked
                and not answer.worker_ref.startswith("structured-turn:")
            )
        ):
            raise QuestionValidationError(
                "correlation_mismatch",
                "answer does not match the frozen retrieval and lease",
            )
        now = _timestamp(self._now())
        conn = _connect(self.db_path)
        try:
            conn.execute("BEGIN IMMEDIATE")
            existing = conn.execute(
                "SELECT answer_id, output_digest FROM service_question_answers WHERE question_id = ?",
                (lease.question_id,),
            ).fetchone()
            if existing is not None:
                if (
                    existing["answer_id"] != answer.answer_id
                    or existing["output_digest"] != answer.output_digest
                ):
                    raise QuestionLeaseError("question already has a different answer")
                conn.commit()
                return self.status(lease.question_id)
            row = conn.execute(
                "SELECT * FROM service_question_tasks WHERE question_id = ?",
                (lease.question_id,),
            ).fetchone()
            if row is None:
                raise KeyError(f"question not found: {lease.question_id}")
            if (
                row["state"] != "running"
                or row["lease_owner"] != lease.worker_id
                or int(row["lease_generation"]) != lease.lease_generation
                or row["lease_expires_at"] is None
                or row["lease_expires_at"] <= now
            ):
                raise QuestionLeaseError("question lease is absent, stale, or expired")
            if answer.error is not None:
                self._record_failure(
                    conn,
                    question_id=answer.question_id,
                    attempt_count=answer.attempt_count,
                    error=answer.error,
                    created_at=now,
                )
            conn.execute(
                """INSERT INTO service_question_answers
                   (answer_id, question_id, answer_json, output_digest, created_at)
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    answer.answer_id,
                    answer.question_id,
                    question_contracts.canonical_json(answer.to_dict()),
                    answer.output_digest,
                    now,
                ),
            )
            conn.execute(
                """UPDATE service_question_tasks
                   SET state = ?, answer_id = ?, error_json = ?,
                       lease_owner = NULL, lease_expires_at = NULL, updated_at = ?
                   WHERE question_id = ?""",
                (
                    answer.answer_state,
                    answer.answer_id,
                    (
                        question_contracts.canonical_json(answer.error.to_dict())
                        if answer.error
                        else None
                    ),
                    now,
                    answer.question_id,
                ),
            )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
        return self.status(lease.question_id)

    def complete_without_worker(
        self,
        answer: question_contracts.QuestionAnswerV1,
    ) -> question_contracts.QuestionStatusV1:
        if (
            answer.attempt_count != 0
            or answer.model_invoked
            or answer.worker_ref != "deterministic-host-v1"
            or answer.answer_state not in {"answered", "no_evidence", "insufficient_evidence"}
        ):
            raise QuestionLeaseError("answer is not eligible for host completion")
        now = _timestamp(self._now())
        conn = _connect(self.db_path)
        try:
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute(
                "SELECT state, attempt_count, answer_id FROM service_question_tasks WHERE question_id = ?",
                (answer.question_id,),
            ).fetchone()
            if row is None:
                raise KeyError(f"question not found: {answer.question_id}")
            if row["answer_id"] is not None:
                conn.commit()
                return self.status(answer.question_id)
            if row["state"] != "pending" or int(row["attempt_count"]) != 0:
                raise QuestionLeaseError("question is not eligible for host completion")
            if answer.error is not None:
                self._record_failure(
                    conn, question_id=answer.question_id, attempt_count=0,
                    error=answer.error, created_at=now,
                )
            conn.execute(
                """INSERT INTO service_question_answers
                   (answer_id, question_id, answer_json, output_digest, created_at)
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    answer.answer_id,
                    answer.question_id,
                    question_contracts.canonical_json(answer.to_dict()),
                    answer.output_digest,
                    now,
                ),
            )
            conn.execute(
                """UPDATE service_question_tasks
                   SET state = ?, answer_id = ?, error_json = ?, updated_at = ?
                   WHERE question_id = ?""",
                (
                    answer.answer_state, answer.answer_id,
                    question_contracts.canonical_json(answer.error.to_dict()) if answer.error else None,
                    now, answer.question_id,
                ),
            )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
        return self.status(answer.question_id)

    def fail(
        self,
        lease: QuestionLease,
        *,
        code: str,
        message: str,
        retryable: bool,
    ) -> question_contracts.QuestionStatusV1:
        error = question_contracts.QuestionErrorV1.from_dict(
            {"code": code, "message": message, "retryable": retryable}
        )
        now = _timestamp(self._now())
        conn = _connect(self.db_path)
        try:
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute(
                "SELECT * FROM service_question_tasks WHERE question_id = ?",
                (lease.question_id,),
            ).fetchone()
            if row is None:
                raise KeyError(f"question not found: {lease.question_id}")
            if (
                row["state"] != "running"
                or row["lease_owner"] != lease.worker_id
                or int(row["lease_generation"]) != lease.lease_generation
                or row["lease_expires_at"] is None
                or row["lease_expires_at"] <= now
            ):
                raise QuestionLeaseError("question lease is absent, stale, or expired")
            can_retry = retryable and int(row["attempt_count"]) < int(row["max_attempts"])
            if can_retry:
                state = "pending"
            elif error.code == "model_unavailable":
                state = "model_unavailable"
            else:
                state = "failed"
            persisted_error = question_contracts.QuestionErrorV1.from_dict(
                {**error.to_dict(), "retryable": can_retry}
            )
            self._record_failure(
                conn,
                question_id=lease.question_id,
                attempt_count=lease.attempt_count,
                error=persisted_error,
                created_at=now,
            )
            conn.execute(
                """UPDATE service_question_tasks
                   SET state = ?, lease_owner = NULL, lease_expires_at = NULL,
                       error_json = ?, updated_at = ?
                   WHERE question_id = ?""",
                (
                    state,
                    None if can_retry else question_contracts.canonical_json(persisted_error.to_dict()),
                    now,
                    lease.question_id,
                ),
            )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
        return self.status(lease.question_id)


class QuestionService:
    """Freeze one search result and expose durable question status."""

    def __init__(
        self,
        db_path: Path,
        search_backend: PostSearchBackend,
        *,
        clock: Clock | None = None,
    ) -> None:
        self.clock = clock or (lambda: datetime.now(timezone.utc))
        self.search_backend = search_backend
        self.queue = QuestionQueue(db_path, clock=self.clock)

    def submit(
        self,
        request: question_contracts.QuestionRequestV1,
        *,
        access_partitions: Sequence[str],
    ) -> question_contracts.QuestionStatusV1:
        if any(value is not None for value in request.temporal.to_dict().values()):
            raise question_contracts.QuestionContractError(
                "unsupported_temporal_intent: use published/observed search filters"
            )
        partitions = tuple(dict.fromkeys(access_partitions))
        if not partitions or not all(isinstance(item, str) and item for item in partitions):
            raise question_contracts.QuestionContractError(
                "authorized access partitions must not be empty"
            )
        search_request = contracts.PostSearchRequest.from_dict(
            {
                "schema_version": 1,
                "request_id": question_contracts.stable_id(
                    "question-search", request.request_fingerprint
                ),
                "profile_id": request.profile_id,
                "query": request.question,
                "filters": request.filters,
                "page_size": request.limits.evidence_limit,
                "cursor": None,
            }
        )
        response = self.search_backend.search(
            search_request, access_partitions=partitions
        )
        authorized = set(partitions)
        selected: list[dict[str, Any]] = []
        byte_truncated = False
        for hit in response.hits[: request.limits.evidence_limit]:
            if hit.access_partition_id not in authorized:
                raise question_contracts.QuestionContractError(
                    "search returned evidence outside authorized partitions"
                )
            citation_core = {
                **hit.evidence_ref.to_dict(),
                "access_partition_id": hit.access_partition_id,
            }
            citation = question_contracts.QuestionCitationV1.from_dict(
                {
                    "evidence_id": question_contracts.stable_id(
                        "question-evidence", citation_core
                    ),
                    **citation_core,
                }
            )
            item = {
                **citation.to_dict(),
                "post_id": hit.post_id,
                "source": hit.source,
                "title": hit.title,
                "author": hit.author,
                "text": hit.text,
                "published_at": hit.published_at,
                "observed_at": hit.observed_at,
            }
            candidate = [*selected, item]
            if (
                len(question_contracts.canonical_json(candidate).encode())
                > request.limits.max_evidence_bytes
            ):
                byte_truncated = True
                break
            selected.append(item)
        evidence_set_id = question_contracts.stable_id(
            "evidence-set", [item["evidence_id"] for item in selected]
        )
        access_digest = question_contracts.digest(sorted(partitions))
        question_id = question_contracts.stable_id(
            "question",
            {
                "request_fingerprint": request.request_fingerprint,
                "search_head_id": response.search_head_id,
                "evidence_set_id": evidence_set_id,
                "access_partitions_digest": access_digest,
                "answer_mode": request.answer_mode,
                "model_fallback": request.model_fallback,
                "policy_version": "question-answer-policy-v1",
            },
        )
        stale = False
        if selected and request.limits.max_evidence_age_seconds is not None:
            newest = max(_parse_timestamp(str(item["observed_at"])) for item in selected)
            stale = newest < self.clock().astimezone(timezone.utc) - timedelta(
                seconds=request.limits.max_evidence_age_seconds
            )
        partial = bool(
            response.truncated
            or response.coverage.get("unavailable_filters")
            or byte_truncated
            or len(response.hits) > len(selected)
        )
        retrieval = {
            "schema_version": 1,
            "question_id": question_id,
            "request_id": request.request_id,
            "request_fingerprint": request.request_fingerprint,
            "search_head_id": response.search_head_id,
            "evidence_set_id": evidence_set_id,
            "access_partitions_digest": access_digest,
            "evidence": selected,
            "coverage": {
                "partial": partial,
                "stale": stale,
                "search": response.coverage,
                "byte_truncated": byte_truncated,
            },
            "search_receipt": {
                "search_head_id": response.search_head_id,
                "component_heads": response.coverage.get("component_heads", {}),
                "ordered_evidence_ids": [
                    item["evidence_id"] for item in selected
                ],
                "returned": response.returned,
                "truncated": response.truncated,
                "next_cursor": response.next_cursor,
                "coverage": response.coverage,
            },
            "selection_receipt": {
                "evidence_limit": request.limits.evidence_limit,
                "max_evidence_bytes": request.limits.max_evidence_bytes,
                "selected_count": len(selected),
                "selected_bytes": len(
                    question_contracts.canonical_json(selected).encode()
                ),
                "byte_truncated": byte_truncated,
            },
            "cache_only": True,
            "acquisition_performed": False,
        }
        status = self.queue.enqueue(request, retrieval)
        if status.state != "pending":
            return status
        if selected and request.answer_mode != "evidence_only":
            return status
        uncertainty_codes = tuple(
            code
            for enabled, code in (
                (partial, "partial_coverage"),
                (stale, "stale_evidence"),
            )
            if enabled
        )
        statements: tuple[question_contracts.AnswerStatementV1, ...] = ()
        answer_state = "no_evidence"
        summary = "No authorized evidence was found."[:request.limits.max_answer_characters]
        if selected:
            answer_budget = request.limits.max_answer_characters
            summary = f"Evidence-only result from {len(selected)} immutable item(s)."[
                : max(1, answer_budget - 1)
            ]
            remaining_characters = answer_budget - len(summary)
            bounded_statements: list[question_contracts.AnswerStatementV1] = []
            for item in selected[: request.limits.max_statements]:
                if remaining_characters <= 0:
                    break
                text = str(item["text"])[:min(remaining_characters, 8192)]
                if not text:
                    continue
                bounded_statements.append(
                    question_contracts.AnswerStatementV1.create(
                        text=text,
                        statement_kind="source_fact",
                        support_state="supported",
                        citations=(
                            question_contracts.QuestionCitationV1.from_dict(
                                {
                                    key: item[key]
                                    for key in (
                                        "evidence_id",
                                        "storage_family",
                                        "version_id",
                                        "content_hash",
                                        "source_url",
                                        "access_partition_id",
                                    )
                                }
                            ),
                        ),
                        alternatives=(),
                    )
                )
                remaining_characters -= len(text)
            statements = tuple(bounded_statements)
            answer_state = "answered" if statements else "insufficient_evidence"
            if not statements:
                uncertainty_codes = (*uncertainty_codes, "answer_too_large")
        elif "no_evidence" not in uncertainty_codes:
            uncertainty_codes = (*uncertainty_codes, "no_evidence")
        answer = question_contracts.QuestionAnswerV1.create(
            question_id=question_id,
            request_fingerprint=request.request_fingerprint,
            search_head_id=response.search_head_id,
            evidence_set_id=evidence_set_id,
            answer_state=answer_state,
            summary=summary,
            statements=statements,
            uncertainty_codes=uncertainty_codes,
            coverage={"partial": partial, "stale": stale},
            worker_ref="deterministic-host-v1",
            generated_at=_timestamp(self.clock()),
            input_digest=question_contracts.digest(
                {"request": request.to_dict(), "retrieval": retrieval}
            ),
            attempt_count=0,
            model_invoked=False,
            evidence_only_fallback=False,
            error=None,
        )
        return self.queue.complete_without_worker(
            _bounded_public_answer(answer, request.limits.max_answer_characters)
        )

    def status(self, question_id: str) -> question_contracts.QuestionStatusV1:
        return self.queue.status(question_id)


def _bounded_public_answer(
    answer: question_contracts.QuestionAnswerV1, max_characters: int
) -> question_contracts.QuestionAnswerV1:
    """Persist a compact rejection, never an answer the public client cannot read."""
    characters = len(answer.summary) + sum(len(item.text) for item in answer.statements)
    # Reserve 4 KiB for the enclosing status fields and its repeated error.
    if (characters <= max_characters
            and len(question_contracts.canonical_json(answer.to_dict()).encode()) <= 126_976):
        return answer
    values = answer.to_dict()
    for key in ("schema_version", "answer_id", "output_digest", "cache_only", "acquisition_performed"):
        values.pop(key)
    values.update(
        answer_state="insufficient_evidence",
        summary="Answer exceeds the public response budget."[:max_characters],
        statements=(),
        uncertainty_codes=tuple(dict.fromkeys((*answer.uncertainty_codes, "answer_too_large"))),
        error=question_contracts.QuestionErrorV1.from_dict({
            "code": "answer_too_large", "message": "answer exceeds the public response budget", "retryable": False,
        }),
    )
    return question_contracts.QuestionAnswerV1.create(**values)


def _worker_answer(
    lease: QuestionLease,
    output: Mapping[str, Any],
    *,
    worker_ref: str,
    generated_at: str,
    model_invoked: bool = False,
    evidence_only_fallback: bool = False,
) -> question_contracts.QuestionAnswerV1:
    expected = {
        "answer_state",
        "summary",
        "statements",
        "uncertainty_codes",
    }
    if model_invoked:
        expected.add("action")
    if not isinstance(output, Mapping) or set(output) != expected:
        raise QuestionValidationError(
            "invalid_worker_contract", "worker output fields are invalid"
        )
    if model_invoked and output["action"] != "answer_from_evidence":
        raise QuestionValidationError(
            "invalid_worker_action", "worker action is invalid"
        )
    state = output["answer_state"]
    if state not in {"answered", "conflicting_evidence", "insufficient_evidence"}:
        raise QuestionValidationError("invalid_answer_state", "worker answer_state is invalid")
    summary = output["summary"]
    if not isinstance(summary, str) or not summary.strip():
        raise QuestionValidationError("invalid_summary", "worker summary is invalid")
    if len(summary) > lease.request.limits.max_answer_characters:
        raise QuestionValidationError("answer_too_large", "worker summary exceeds its bound")
    raw_statements = output["statements"]
    if not isinstance(raw_statements, list) or len(raw_statements) > lease.request.limits.max_statements:
        raise QuestionValidationError("statement_bound_exceeded", "worker statements exceed their bound")
    evidence = {
        item["evidence_id"]: question_contracts.QuestionCitationV1.from_dict(
            {
                key: item[key]
                for key in (
                    "evidence_id",
                    "storage_family",
                    "version_id",
                    "content_hash",
                    "source_url",
                    "access_partition_id",
                )
            }
        )
        for item in lease.retrieval["evidence"]
    }
    statements: list[question_contracts.AnswerStatementV1] = []
    statement_fields = {
        "text",
        "statement_kind",
        "support_state",
        "citation_ids",
        "alternatives",
    }
    for raw in raw_statements:
        if not isinstance(raw, Mapping) or set(raw) != statement_fields:
            raise QuestionValidationError(
                "invalid_statement_contract", "worker statement fields are invalid"
            )
        citation_ids = raw["citation_ids"]
        if not isinstance(citation_ids, list) or not all(
            isinstance(item, str) for item in citation_ids
        ):
            raise QuestionValidationError("invalid_citation", "citation_ids is invalid")
        if any(citation_id not in evidence for citation_id in citation_ids):
            raise QuestionValidationError(
                "invalid_citation", "statement cites evidence outside the frozen set"
            )
        if raw["statement_kind"] == "source_fact" and raw["support_state"] == "insufficient":
            raise QuestionValidationError(
                "statement_support_mismatch",
                "source_fact statements cannot claim insufficient support",
            )
        if raw["support_state"] == "mixed" and (
            len(citation_ids) < 2 or len(raw["alternatives"]) < 2
        ):
            raise QuestionValidationError(
                "conflict_sides_omitted",
                "mixed statements must preserve both cited alternatives",
            )
        if raw["support_state"] in {"supported", "mixed"} and not citation_ids:
            raise QuestionValidationError(
                "unsupported_claim", "substantive statement has no citation"
            )
        try:
            statement = question_contracts.AnswerStatementV1.create(
                text=raw["text"],
                statement_kind=raw["statement_kind"],
                support_state=raw["support_state"],
                citations=tuple(evidence[citation_id] for citation_id in citation_ids),
                alternatives=tuple(raw["alternatives"]),
            )
        except (KeyError, TypeError, question_contracts.QuestionContractError) as exc:
            raise QuestionValidationError(
                "invalid_statement_contract", str(exc)
            ) from exc
        statements.append(statement)
    if len(summary) + sum(len(statement.text) for statement in statements) > (
        lease.request.limits.max_answer_characters
    ):
        raise QuestionValidationError(
            "answer_too_large", "worker answer exceeds its total character bound"
        )
    if state == "answered" and any(
        statement.support_state != "supported" for statement in statements
    ):
        raise QuestionValidationError(
            "unsupported_claim", "answered result contains a non-supported statement"
        )
    uncertainty = output["uncertainty_codes"]
    if not isinstance(uncertainty, list) or not all(
        isinstance(item, str) for item in uncertainty
    ):
        raise QuestionValidationError(
            "invalid_uncertainty", "uncertainty_codes is invalid"
        )
    flags = lease.retrieval["coverage"]
    if flags["partial"] and "partial_coverage" not in uncertainty:
        raise QuestionValidationError(
            "partial_coverage_unlabeled", "partial coverage must be labeled"
        )
    if flags["stale"] and "stale_evidence" not in uncertainty:
        raise QuestionValidationError(
            "stale_evidence_unlabeled", "stale evidence must be labeled"
        )
    input_payload = {
        "request": lease.request.to_dict(),
        "retrieval": lease.retrieval,
    }
    try:
        return question_contracts.QuestionAnswerV1.create(
            question_id=lease.question_id,
            request_fingerprint=lease.request.request_fingerprint,
            search_head_id=lease.retrieval["search_head_id"],
            evidence_set_id=lease.retrieval["evidence_set_id"],
            answer_state=state,
            summary=summary,
            statements=tuple(statements),
            uncertainty_codes=tuple(uncertainty),
            coverage={"partial": flags["partial"], "stale": flags["stale"]},
            worker_ref=worker_ref,
            generated_at=generated_at,
            input_digest=question_contracts.digest(input_payload),
            attempt_count=lease.attempt_count,
            model_invoked=model_invoked,
            evidence_only_fallback=evidence_only_fallback,
            error=None,
        )
    except question_contracts.QuestionContractError as exc:
        raise QuestionValidationError("invalid_worker_contract", str(exc)) from exc


def _evidence_only_fallback_answer(
    lease: QuestionLease,
    *,
    generated_at: str,
    error: question_contracts.QuestionErrorV1,
) -> question_contracts.QuestionAnswerV1:
    evidence = lease.retrieval["evidence"]
    summary = "Model unavailable; returning immutable evidence only."[
        : lease.request.limits.max_answer_characters
    ]
    statement_budget = lease.request.limits.max_answer_characters - len(summary)
    statements = tuple(
        question_contracts.AnswerStatementV1.create(
            text=str(item["text"])[:min(statement_budget, 8192)],
            statement_kind="source_fact",
            support_state="supported",
            citations=(
                question_contracts.QuestionCitationV1.from_dict(
                    {
                        key: item[key]
                        for key in (
                            "evidence_id",
                            "storage_family",
                            "version_id",
                            "content_hash",
                            "source_url",
                            "access_partition_id",
                        )
                    }
                ),
            ),
            alternatives=(),
        )
        for item in evidence[:1]
        if statement_budget > 0
    )
    flags = lease.retrieval["coverage"]
    uncertainty = ["model_unavailable"]
    if flags["partial"]:
        uncertainty.append("partial_coverage")
    if flags["stale"]:
        uncertainty.append("stale_evidence")
    return question_contracts.QuestionAnswerV1.create(
        question_id=lease.question_id,
        request_fingerprint=lease.request.request_fingerprint,
        search_head_id=lease.retrieval["search_head_id"],
        evidence_set_id=lease.retrieval["evidence_set_id"],
        answer_state="answered" if statements else "insufficient_evidence",
        summary=summary,
        statements=statements,
        uncertainty_codes=tuple(uncertainty),
        coverage={"partial": flags["partial"], "stale": flags["stale"]},
        worker_ref="deterministic-evidence-fallback-v1",
        generated_at=generated_at,
        input_digest=question_contracts.digest(
            {"request": lease.request.to_dict(), "retrieval": lease.retrieval}
        ),
        attempt_count=lease.attempt_count,
        model_invoked=False,
        evidence_only_fallback=True,
        error=error,
    )


class QuestionRunner:
    """Run one bounded answer attempt under deterministic host validation."""

    def __init__(
        self,
        queue: QuestionQueue,
        worker: NoToolAnswerWorker,
        *,
        clock: Clock | None = None,
    ) -> None:
        self.queue = queue
        self.worker = worker
        self.clock = clock or (lambda: datetime.now(timezone.utc))

    def run_once(
        self, *, worker_id: str, question_id: str | None = None
    ) -> question_contracts.QuestionStatusV1 | None:
        lease = self.queue.claim_next(worker_id=worker_id, question_id=question_id)
        if lease is None:
            return None
        evidence = lease.retrieval["evidence"]
        payload = {
            "schema_version": 1,
            "action": "answer_from_evidence",
            "question_id": lease.question_id,
            "question": lease.request.question,
            "answer_mode": lease.request.answer_mode,
            "evidence": evidence,
            "allowed_citation_ids": [item["evidence_id"] for item in evidence],
            "coverage": {
                "partial": lease.retrieval["coverage"]["partial"],
                "stale": lease.retrieval["coverage"]["stale"],
            },
        }
        generated_at = _timestamp(self.clock())
        receipt_worker_ref = self.worker.worker_ref
        model_invoked = False
        evidence_only_fallback = False
        try:
            worker_result = self.worker.answer(payload)
            if isinstance(worker_result, AnswerWorkerResult):
                output = worker_result.output
                receipt_worker_ref = worker_result.worker_ref
                model_invoked = worker_result.model_invoked
                evidence_only_fallback = worker_result.evidence_only_fallback
            else:
                output = worker_result
            answer = _worker_answer(
                lease,
                output,
                worker_ref=receipt_worker_ref,
                generated_at=generated_at,
                model_invoked=model_invoked,
                evidence_only_fallback=evidence_only_fallback,
            )
        except QuestionWorkerError as exc:
            if exc.code == "model_unavailable" and lease.request.model_fallback == "evidence_only":
                error = question_contracts.QuestionErrorV1.from_dict(
                    {"code": exc.code, "message": str(exc), "retryable": False}
                )
                return self.queue.complete(
                    lease,
                    _bounded_public_answer(
                        _evidence_only_fallback_answer(lease, generated_at=generated_at, error=error),
                        lease.request.limits.max_answer_characters,
                    ),
                )
            return self.queue.fail(
                lease,
                code=exc.code,
                message=str(exc),
                retryable=exc.retryable,
            )
        except QuestionValidationError as exc:
            error = question_contracts.QuestionErrorV1.from_dict(
                {"code": exc.code, "message": str(exc), "retryable": False}
            )
            answer = question_contracts.QuestionAnswerV1.create(
                question_id=lease.question_id,
                request_fingerprint=lease.request.request_fingerprint,
                search_head_id=lease.retrieval["search_head_id"],
                evidence_set_id=lease.retrieval["evidence_set_id"],
                answer_state="insufficient_evidence",
                summary=f"Answer rejected: {exc}",
                statements=(),
                uncertainty_codes=(exc.code,),
                coverage={
                    "partial": lease.retrieval["coverage"]["partial"],
                    "stale": lease.retrieval["coverage"]["stale"],
                },
                worker_ref=receipt_worker_ref,
                generated_at=generated_at,
                input_digest=question_contracts.digest(
                    {"request": lease.request.to_dict(), "retrieval": lease.retrieval}
                ),
                attempt_count=lease.attempt_count,
                model_invoked=model_invoked,
                evidence_only_fallback=evidence_only_fallback,
                error=error,
            )
        return self.queue.complete(
            lease, _bounded_public_answer(answer, lease.request.limits.max_answer_characters)
        )
