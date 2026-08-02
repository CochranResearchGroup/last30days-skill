"""Typed recurring collection specifications and durable interval accounting."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Callable, Mapping

from . import service_contracts as contracts
from .service_refresh import ServiceRefreshScheduler
from .service_source_policy import SOURCE_ACCESS_METHODS
from .service_temporal import access_partition_id


Clock = Callable[[], datetime]
_SURFACE_SELECTORS = {
    "feed": "feed",
    "topic": "topic",
    "poster": "poster",
    "channel": "channel",
    "account": "account",
    "profile": "profile_url",
}
_TRIGGERS = frozenset({"timer", "manual"})
_BROWSER_SOURCES = frozenset({"x", "facebook", "linkedin"})


class CollectionSpecValidationError(ValueError):
    """Raised when a collection specification is not strict and bounded."""


def _canonical_json(value: object) -> str:
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def _digest(value: object) -> str:
    return "sha256:" + hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _stable_id(prefix: str, value: object) -> str:
    return f"{prefix}-{hashlib.sha256(_canonical_json(value).encode()).hexdigest()[:32]}"


def _timestamp(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _parse_timestamp(value: str, field: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, ValueError) as exc:
        raise CollectionSpecValidationError(
            f"{field} must be an ISO-8601 timestamp"
        ) from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise CollectionSpecValidationError(f"{field} must include a timezone")
    return parsed.astimezone(timezone.utc)


def _bounded_int(
    payload: Mapping[str, object],
    field: str,
    minimum: int,
    maximum: int,
) -> int:
    value = payload[field]
    if isinstance(value, bool) or not isinstance(value, int):
        raise CollectionSpecValidationError(f"{field} must be an integer")
    if not minimum <= value <= maximum:
        raise CollectionSpecValidationError(
            f"{field} must be between {minimum} and {maximum}"
        )
    return value


def _nonempty(payload: Mapping[str, object], field: str, maximum: int = 512) -> str:
    value = payload[field]
    if not isinstance(value, str) or not value.strip():
        raise CollectionSpecValidationError(f"{field} must be a non-empty string")
    if len(value) > maximum:
        raise CollectionSpecValidationError(f"{field} exceeds {maximum} characters")
    return value.strip()


@dataclass(frozen=True)
class CollectionSpec:
    schema_version: int
    collection_spec_id: str
    name: str
    source: str
    surface_kind: str
    selector: dict[str, str]
    profile_id: str
    interval_seconds: int
    lookback_seconds: int
    item_limit: int
    wall_timeout_seconds: int
    network_request_limit: int
    budget_cents: int
    retention_class: str
    redaction_class: str
    assessment_enabled: bool
    enabled: bool
    spec_version: int
    required_access_method: str | None = None

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> CollectionSpec:
        if not isinstance(payload, Mapping):
            raise CollectionSpecValidationError("collection spec must be an object")
        required_fields = frozenset(
            {
                "schema_version",
                "collection_spec_id",
                "name",
                "source",
                "surface_kind",
                "selector",
                "profile_id",
                "interval_seconds",
                "lookback_seconds",
                "item_limit",
                "wall_timeout_seconds",
                "network_request_limit",
                "budget_cents",
                "retention_class",
                "redaction_class",
                "assessment_enabled",
                "enabled",
                "spec_version",
            }
        )
        allowed_fields = required_fields | {"required_access_method"}
        unknown = sorted(set(payload) - allowed_fields)
        missing = sorted(required_fields - set(payload))
        if missing:
            raise CollectionSpecValidationError(
                f"missing fields: {', '.join(missing)}"
            )
        if unknown:
            raise CollectionSpecValidationError(
                f"unknown fields: {', '.join(unknown)}"
            )
        if payload["schema_version"] != 1:
            raise CollectionSpecValidationError("schema_version must be 1")
        surface_kind = _nonempty(payload, "surface_kind", 32).casefold()
        selector_field = _SURFACE_SELECTORS.get(surface_kind)
        if selector_field is None:
            raise CollectionSpecValidationError("surface_kind is unsupported")
        selector = payload["selector"]
        if (
            not isinstance(selector, Mapping)
            or set(selector) != {selector_field}
            or not isinstance(selector.get(selector_field), str)
            or not str(selector[selector_field]).strip()
        ):
            raise CollectionSpecValidationError(
                f"selector for {surface_kind} must contain only {selector_field}"
            )
        selector_value = str(selector[selector_field]).strip()
        if len(selector_value) > 4096:
            raise CollectionSpecValidationError("selector exceeds 4096 characters")
        profile_id = _nonempty(payload, "profile_id", 128)
        retention = _nonempty(payload, "retention_class", 32).casefold()
        if retention not in {"cache", "durable", "ephemeral"}:
            raise CollectionSpecValidationError("retention_class is invalid")
        redaction = _nonempty(payload, "redaction_class", 32).casefold()
        if redaction not in {"public", "authenticated", "restricted"}:
            raise CollectionSpecValidationError("redaction_class is invalid")
        source = _nonempty(payload, "source", 64).casefold()
        required_access_method = payload.get("required_access_method")
        if required_access_method is not None:
            if not isinstance(required_access_method, str) or not required_access_method.strip():
                raise CollectionSpecValidationError(
                    "required_access_method must be a non-empty string"
                )
            required_access_method = required_access_method.strip().casefold()
            if required_access_method not in SOURCE_ACCESS_METHODS.get(source, ()):
                raise CollectionSpecValidationError(
                    "required_access_method is unsupported for source"
                )
        if source in _BROWSER_SOURCES and redaction != "authenticated":
            raise CollectionSpecValidationError(
                "redaction_class must be authenticated for browser sources"
            )
        if profile_id != "default" and redaction == "public":
            raise CollectionSpecValidationError(
                "redaction_class must be authenticated for a named profile"
            )
        for field in ("assessment_enabled", "enabled"):
            if not isinstance(payload[field], bool):
                raise CollectionSpecValidationError(f"{field} must be boolean")
        return cls(
            schema_version=1,
            collection_spec_id=_nonempty(payload, "collection_spec_id", 128),
            name=_nonempty(payload, "name", 256),
            source=source,
            surface_kind=surface_kind,
            selector={selector_field: selector_value},
            profile_id=profile_id,
            interval_seconds=_bounded_int(
                payload, "interval_seconds", 60, 31_536_000
            ),
            lookback_seconds=_bounded_int(
                payload, "lookback_seconds", 60, 31_536_000
            ),
            item_limit=_bounded_int(payload, "item_limit", 1, 100),
            wall_timeout_seconds=_bounded_int(
                payload, "wall_timeout_seconds", 1, 3600
            ),
            network_request_limit=_bounded_int(
                payload, "network_request_limit", 0, 100_000
            ),
            budget_cents=_bounded_int(payload, "budget_cents", 0, 10_000_000),
            retention_class=retention,
            redaction_class=redaction,
            assessment_enabled=bool(payload["assessment_enabled"]),
            enabled=bool(payload["enabled"]),
            spec_version=_bounded_int(payload, "spec_version", 1, 1_000_000),
            required_access_method=required_access_method,
        )

    @property
    def selector_digest(self) -> str:
        return _digest(self.selector)

    @property
    def spec_digest(self) -> str:
        return _digest(self.to_dict())

    @property
    def query(self) -> str:
        return next(iter(self.selector.values()))

    @property
    def access_partition_id(self) -> str:
        return access_partition_id(self.redaction_class, self.profile_id)

    def to_dict(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "schema_version": self.schema_version,
            "collection_spec_id": self.collection_spec_id,
            "name": self.name,
            "source": self.source,
            "surface_kind": self.surface_kind,
            "selector": dict(self.selector),
            "profile_id": self.profile_id,
            "interval_seconds": self.interval_seconds,
            "lookback_seconds": self.lookback_seconds,
            "item_limit": self.item_limit,
            "wall_timeout_seconds": self.wall_timeout_seconds,
            "network_request_limit": self.network_request_limit,
            "budget_cents": self.budget_cents,
            "retention_class": self.retention_class,
            "redaction_class": self.redaction_class,
            "assessment_enabled": self.assessment_enabled,
            "enabled": self.enabled,
            "spec_version": self.spec_version,
        }
        if self.required_access_method is not None:
            payload["required_access_method"] = self.required_access_method
        return payload


@dataclass(frozen=True)
class CollectionRun:
    collection_run_id: str
    collection_spec_id: str
    job_id: str
    state: str
    interval_from: str
    interval_to: str
    access_partition_id: str
    network_request_count: int | None = None
    attempted_count: int | None = None
    observed_count: int | None = None
    accepted_count: int | None = None
    rejected_count: int | None = None
    stored_count: int | None = None
    deduplicated_count: int | None = None
    indexed_count: int | None = None
    pre_document_count: int | None = None
    pre_embedding_count: int | None = None
    pre_index_version: str | None = None
    post_document_count: int | None = None
    post_embedding_count: int | None = None
    post_index_version: str | None = None
    attempted_access_methods: tuple[str, ...] | None = None
    selected_access_method: str | None = None
    adapter_variant: str | None = None

    def to_dict(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "collection_run_id": self.collection_run_id,
            "collection_spec_id": self.collection_spec_id,
            "job_id": self.job_id,
            "state": self.state,
            "interval_from": self.interval_from,
            "interval_to": self.interval_to,
            "access_partition_id": self.access_partition_id,
        }
        if self.network_request_count is not None:
            payload.update(
                {
                    "network_request_count": self.network_request_count,
                    "counts": {
                        "attempted": self.attempted_count,
                        "observed": self.observed_count,
                        "accepted": self.accepted_count,
                        "rejected": self.rejected_count,
                        "stored": self.stored_count,
                        "deduplicated": self.deduplicated_count,
                        "indexed": self.indexed_count,
                    },
                    "pre_snapshot": {
                        "document_count": self.pre_document_count,
                        "embedding_count": self.pre_embedding_count,
                        "index_version": self.pre_index_version,
                    },
                    "post_snapshot": {
                        "document_count": self.post_document_count,
                        "embedding_count": self.post_embedding_count,
                        "index_version": self.post_index_version,
                    },
                    "provenance": {
                        "attempted_access_methods": list(
                            self.attempted_access_methods or ()
                        ),
                        "selected_access_method": self.selected_access_method,
                        "adapter_variant": self.adapter_variant,
                    },
                }
            )
        return payload


class CollectionCoordinator:
    """Persist specs and coalesce timer/manual work onto durable refresh jobs."""

    def __init__(
        self,
        db_path: Path,
        scheduler: ServiceRefreshScheduler,
        *,
        clock: Clock | None = None,
    ) -> None:
        self.db_path = Path(db_path)
        self.scheduler = scheduler
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self.scheduler.ledger.initialize()

    def _now(self) -> datetime:
        value = self._clock()
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("clock must return a timezone-aware datetime")
        return value.astimezone(timezone.utc)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=5)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA busy_timeout=5000")
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    @staticmethod
    def _floor_interval(value: datetime, seconds: int) -> datetime:
        epoch = int(value.timestamp())
        return datetime.fromtimestamp(epoch - (epoch % seconds), tz=timezone.utc)

    @staticmethod
    def _run_from_row(
        row: sqlite3.Row,
        receipt: Mapping[str, object] | None = None,
    ) -> CollectionRun:
        if not row["job_id"]:
            raise RuntimeError("collection run has not been linked to a job")
        evidence = receipt or {}
        counts = evidence.get("counts")
        counts = counts if isinstance(counts, Mapping) else {}
        before = evidence.get("pre_snapshot")
        before = before if isinstance(before, Mapping) else {}
        after = evidence.get("post_snapshot")
        after = after if isinstance(after, Mapping) else {}
        provenance = evidence.get("provenance")
        provenance = provenance if isinstance(provenance, Mapping) else {}
        attempted_methods = provenance.get("attempted_access_methods")
        attempted_methods = (
            tuple(str(item) for item in attempted_methods)
            if isinstance(attempted_methods, list)
            else None
        )
        return CollectionRun(
            collection_run_id=row["collection_run_id"],
            collection_spec_id=row["collection_spec_id"],
            job_id=row["job_id"],
            state=row["state"],
            interval_from=row["interval_from"],
            interval_to=row["interval_to"],
            access_partition_id=row["access_partition_id"],
            network_request_count=evidence.get("network_request_count"),
            attempted_count=counts.get("attempted", row["attempted_count"]),
            observed_count=counts.get("observed", row["observed_count"]),
            accepted_count=counts.get("accepted"),
            rejected_count=counts.get("rejected"),
            stored_count=counts.get("stored", row["stored_count"]),
            deduplicated_count=counts.get("deduplicated"),
            indexed_count=counts.get("indexed"),
            pre_document_count=before.get("document_count"),
            pre_embedding_count=before.get("embedding_count"),
            pre_index_version=before.get("index_version"),
            post_document_count=after.get("document_count"),
            post_embedding_count=after.get("embedding_count"),
            post_index_version=after.get("index_version"),
            attempted_access_methods=attempted_methods,
            selected_access_method=provenance.get("selected_access_method"),
            adapter_variant=provenance.get("adapter_variant"),
        )

    @staticmethod
    def _put_observability_envelope(
        conn: sqlite3.Connection,
        *,
        envelope_type: str,
        envelope_id: str,
        payload: Mapping[str, object],
    ) -> None:
        payload_json = _canonical_json(payload)
        payload_sha256 = hashlib.sha256(payload_json.encode("utf-8")).hexdigest()
        existing = conn.execute(
            """SELECT payload_sha256 FROM service_envelopes
               WHERE envelope_type = ? AND envelope_id = ?""",
            (envelope_type, envelope_id),
        ).fetchone()
        if existing is not None:
            if existing["payload_sha256"] != payload_sha256:
                raise RuntimeError("immutable collection observability conflict")
            return
        conn.execute(
            """INSERT INTO service_envelopes
               (envelope_type, envelope_id, schema_version,
                payload_json, payload_sha256)
               VALUES (?, ?, 1, ?, ?)""",
            (envelope_type, envelope_id, payload_json, payload_sha256),
        )

    def put_spec(self, spec: CollectionSpec) -> CollectionSpec:
        now = _timestamp(self._now())
        partition_kind = (
            "public" if spec.access_partition_id == "public" else "authenticated"
        )
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            current = conn.execute(
                """SELECT s.spec_version, s.enabled, r.spec_digest
                   FROM collection_specs AS s
                   JOIN collection_spec_revisions AS r
                     ON r.collection_spec_id = s.collection_spec_id
                    AND r.spec_version = s.spec_version
                   WHERE s.collection_spec_id = ?""",
                (spec.collection_spec_id,),
            ).fetchone()
            if current is not None:
                current_version = int(current["spec_version"])
                if spec.spec_version == current_version:
                    if spec.spec_digest != current["spec_digest"]:
                        raise CollectionSpecValidationError(
                            "spec_version is immutable; increment it for edits"
                        )
                elif spec.spec_version != current_version + 1:
                    raise CollectionSpecValidationError(
                        "spec_version must increment exactly once"
                    )
            resuming = (
                current is not None
                and not bool(current["enabled"])
                and spec.enabled
            )
            conn.execute(
                """INSERT OR IGNORE INTO access_partitions
                   (partition_id, partition_kind, profile_id, created_at)
                   VALUES (?, ?, ?, ?)""",
                (
                    spec.access_partition_id,
                    partition_kind,
                    None if partition_kind == "public" else spec.profile_id,
                    now,
                ),
            )
            conn.execute(
                """INSERT INTO collection_specs
                   (collection_spec_id, name, source, surface_kind, selector_json,
                    profile_id, schedule, item_limit, enabled, spec_version,
                    access_partition_id, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                   ON CONFLICT(collection_spec_id) DO UPDATE SET
                     name = excluded.name,
                     source = excluded.source,
                     surface_kind = excluded.surface_kind,
                     selector_json = excluded.selector_json,
                     profile_id = excluded.profile_id,
                     schedule = excluded.schedule,
                     item_limit = excluded.item_limit,
                     enabled = excluded.enabled,
                     spec_version = excluded.spec_version,
                     access_partition_id = excluded.access_partition_id,
                     updated_at = excluded.updated_at""",
                (
                    spec.collection_spec_id,
                    spec.name,
                    spec.source,
                    spec.surface_kind,
                    _canonical_json(spec.selector),
                    spec.profile_id,
                    f"every:{spec.interval_seconds}",
                    spec.item_limit,
                    int(spec.enabled),
                    spec.spec_version,
                    spec.access_partition_id,
                    now,
                    now,
                ),
            )
            conn.execute(
                """INSERT OR IGNORE INTO collection_spec_revisions
                   (collection_spec_id, spec_version, spec_json, spec_digest,
                    selector_digest, access_partition_id, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    spec.collection_spec_id,
                    spec.spec_version,
                    _canonical_json(spec.to_dict()),
                    spec.spec_digest,
                    spec.selector_digest,
                    spec.access_partition_id,
                    now,
                ),
            )
            first_due = _timestamp(
                self._floor_interval(self._now(), spec.interval_seconds)
            )
            conn.execute(
                """INSERT INTO collection_schedule_state
                   (collection_spec_id, next_due_at, access_partition_id)
                   VALUES (?, ?, ?)
                   ON CONFLICT(collection_spec_id) DO UPDATE SET
                     access_partition_id = excluded.access_partition_id,
                     next_due_at = CASE
                       WHEN ? THEN excluded.next_due_at
                       ELSE collection_schedule_state.next_due_at
                     END""",
                (
                    spec.collection_spec_id,
                    first_due,
                    spec.access_partition_id,
                    int(resuming),
                ),
            )
            conn.execute(
                """INSERT INTO collection_cursors
                   (collection_spec_id, cursor_value, watermark_value,
                    lease_generation, updated_at, access_partition_id)
                   VALUES (?, NULL, NULL, 0, ?, ?)
                   ON CONFLICT(collection_spec_id) DO NOTHING""",
                (spec.collection_spec_id, now, spec.access_partition_id),
            )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
        return spec

    def get_spec(self, collection_spec_id: str) -> CollectionSpec:
        conn = self._connect()
        try:
            row = conn.execute(
                """SELECT r.spec_json
                   FROM collection_specs AS s
                   JOIN collection_spec_revisions AS r
                     ON r.collection_spec_id = s.collection_spec_id
                    AND r.spec_version = s.spec_version
                   WHERE s.collection_spec_id = ?""",
                (collection_spec_id,),
            ).fetchone()
        finally:
            conn.close()
        if row is None:
            raise KeyError(f"collection spec not found: {collection_spec_id}")
        return CollectionSpec.from_dict(json.loads(row["spec_json"]))

    def get_spec_revision(
        self,
        collection_spec_id: str,
        spec_version: int,
    ) -> CollectionSpec:
        conn = self._connect()
        try:
            row = conn.execute(
                """SELECT spec_json
                   FROM collection_spec_revisions
                   WHERE collection_spec_id = ? AND spec_version = ?""",
                (collection_spec_id, spec_version),
            ).fetchone()
        finally:
            conn.close()
        if row is None:
            raise KeyError(
                f"collection spec revision not found: "
                f"{collection_spec_id}@{spec_version}"
            )
        return CollectionSpec.from_dict(json.loads(row["spec_json"]))

    def list_specs(self) -> tuple[dict[str, object], ...]:
        conn = self._connect()
        try:
            rows = conn.execute(
                """SELECT s.collection_spec_id, r.spec_json,
                          q.next_due_at, q.last_scheduled_at,
                          q.consecutive_failures, q.retry_after,
                          (
                              SELECT cr.state
                              FROM collection_runs AS cr
                              WHERE cr.collection_spec_id = s.collection_spec_id
                              ORDER BY cr.scheduled_for DESC, cr.collection_run_id DESC
                              LIMIT 1
                          ) AS last_run_state
                   FROM collection_specs AS s
                   JOIN collection_spec_revisions AS r
                     ON r.collection_spec_id = s.collection_spec_id
                    AND r.spec_version = s.spec_version
                   JOIN collection_schedule_state AS q
                     ON q.collection_spec_id = s.collection_spec_id
                   ORDER BY s.name, s.collection_spec_id"""
            ).fetchall()
            output: list[dict[str, object]] = []
            for row in rows:
                run_row = conn.execute(
                    """SELECT * FROM collection_runs
                       WHERE collection_spec_id = ?
                       ORDER BY scheduled_for DESC, collection_run_id DESC
                       LIMIT 1""",
                    (row["collection_spec_id"],),
                ).fetchone()
                receipt_row = (
                    conn.execute(
                        """SELECT payload_json FROM service_envelopes
                           WHERE envelope_type = 'collection_run_receipt'
                             AND substr(envelope_id, 1, length(?) + 1) = ? || ':'
                           ORDER BY created_at DESC, envelope_id DESC
                           LIMIT 1""",
                        (
                            run_row["collection_run_id"],
                            run_row["collection_run_id"],
                        ),
                    ).fetchone()
                    if run_row is not None
                    else None
                )
                receipt = (
                    json.loads(receipt_row["payload_json"])
                    if receipt_row is not None
                    else None
                )
                output.append(
                    {
                        "spec": json.loads(row["spec_json"]),
                        "schedule": {
                            "next_due_at": row["next_due_at"],
                            "last_scheduled_at": row["last_scheduled_at"],
                            "consecutive_failures": row["consecutive_failures"],
                            "retry_after": row["retry_after"],
                        },
                        "last_run_state": row["last_run_state"],
                        "last_run": (
                            self._run_from_row(run_row, receipt).to_dict()
                            if run_row is not None
                            else None
                        ),
                    }
                )
        finally:
            conn.close()
        return tuple(output)

    def policy_for_job(self, job_id: str) -> dict[str, object] | None:
        conn = self._connect()
        try:
            row = conn.execute(
                """SELECT sr.spec_json, r.trigger_kind, j.max_attempts
                   FROM collection_runs AS r
                   JOIN collection_spec_revisions AS sr
                     ON sr.collection_spec_id = r.collection_spec_id
                    AND sr.spec_version = r.spec_version
                   JOIN service_jobs AS j ON j.job_id = r.job_id
                   WHERE r.job_id = ?
                   ORDER BY r.scheduled_for, r.collection_run_id
                   LIMIT 1""",
                (job_id,),
            ).fetchone()
        finally:
            conn.close()
        if row is None:
            return None
        policy = json.loads(row["spec_json"])
        policy["_manual_retry_budget"] = (
            row["trigger_kind"] == "manual" and int(row["max_attempts"]) == 2
        )
        return policy

    def set_enabled(self, collection_spec_id: str, *, enabled: bool) -> CollectionSpec:
        spec = self.get_spec(collection_spec_id)
        updated = CollectionSpec.from_dict(
            {
                **spec.to_dict(),
                "enabled": enabled,
                "spec_version": spec.spec_version + 1,
            }
        )
        return self.put_spec(updated)

    def enqueue_interval(
        self,
        collection_spec_id: str,
        *,
        scheduled_for: str,
        trigger: str,
        max_attempts: int | None = None,
    ) -> CollectionRun:
        if trigger not in _TRIGGERS:
            raise ValueError("trigger must be timer or manual")
        if trigger == "timer":
            if max_attempts is not None:
                raise ValueError("timer max_attempts is service-owned")
            resolved_max_attempts = 2
        else:
            resolved_max_attempts = 1 if max_attempts is None else max_attempts
            if (
                isinstance(resolved_max_attempts, bool)
                or not isinstance(resolved_max_attempts, int)
                or resolved_max_attempts not in {1, 2}
            ):
                raise ValueError("manual max_attempts must be 1 or 2")
        spec = self.get_spec(collection_spec_id)
        scheduled = _parse_timestamp(scheduled_for, "scheduled_for")
        interval_to_dt = self._floor_interval(scheduled, spec.interval_seconds)
        interval_from_dt = interval_to_dt - timedelta(seconds=spec.lookback_seconds)
        interval_from = _timestamp(interval_from_dt)
        interval_to = _timestamp(interval_to_dt)
        run_id = _stable_id(
            "collection-run",
            {
                "collection_spec_id": spec.collection_spec_id,
                "interval_from": interval_from,
                "interval_to": interval_to,
            },
        )
        now = _timestamp(self._now())
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            existing = conn.execute(
                """SELECT * FROM collection_runs
                   WHERE collection_spec_id = ?
                     AND interval_from = ? AND interval_to = ?""",
                (spec.collection_spec_id, interval_from, interval_to),
            ).fetchone()
            if existing is None:
                conn.execute(
                    """INSERT INTO collection_runs
                       (collection_run_id, collection_spec_id, job_id, state,
                        claimed_by, lease_generation, scheduled_for, started_at,
                        completed_at, cursor_before, cursor_after,
                        watermark_before, watermark_after, attempted_count,
                        observed_count, stored_count, error_code,
                        access_partition_id, interval_from, interval_to,
                        trigger_kind, spec_version)
                       SELECT ?, ?, NULL, 'scheduling', NULL, c.lease_generation,
                              ?, NULL, NULL, c.cursor_value, NULL,
                              c.watermark_value, NULL, 0, 0, 0, NULL, ?,
                              ?, ?, ?, ?
                       FROM collection_cursors AS c
                       WHERE c.collection_spec_id = ?""",
                    (
                        run_id,
                        spec.collection_spec_id,
                        _timestamp(scheduled),
                        spec.access_partition_id,
                        interval_from,
                        interval_to,
                        trigger,
                        spec.spec_version,
                        spec.collection_spec_id,
                    ),
                )
            else:
                run_id = existing["collection_run_id"]
            conn.execute(
                """INSERT OR IGNORE INTO collection_run_triggers
                   (collection_run_id, trigger_kind, requested_at,
                    access_partition_id)
                   VALUES (?, ?, ?, ?)""",
                (run_id, trigger, now, spec.access_partition_id),
            )
            current = conn.execute(
                "SELECT * FROM collection_runs WHERE collection_run_id = ?",
                (run_id,),
            ).fetchone()
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
        if current is not None and current["job_id"]:
            return self._run_from_row(current)

        request_id = _stable_id("collection-request", run_id)
        request = contracts.QueryRequest.from_dict(
            {
                "schema_version": contracts.SCHEMA_VERSION,
                "request_id": request_id,
                "profile_id": spec.profile_id,
                "query": spec.query,
                "freshness_policy": "force_refresh",
                "response_mode": "evidence",
                "filters": {
                    "sources": [spec.source],
                    "published_after": interval_from,
                    "published_before": interval_to,
                },
                "top_k": spec.item_limit,
                "max_chars": 65_536,
                "wait_ms": 0,
            }
        )
        self.scheduler.ledger.put_envelope(
            request.CONTRACT_NAME,
            request.request_id,
            request,
        )
        result = self.scheduler.supervisor.enqueue_refresh(
            query_request_id=request.request_id,
            query=(
                f"{self.scheduler.query_scope(request)}"
                f"\ncollection-spec:{spec.collection_spec_id}"
                f"\ncollection-spec-version:{spec.spec_version}"
            ),
            sources=(spec.source,),
            profile_id=spec.profile_id,
            freshness_window_seconds=spec.interval_seconds,
            max_attempts=resolved_max_attempts,
            budget_cents=spec.budget_cents,
        )
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            conn.execute(
                """UPDATE collection_runs
                   SET job_id = ?, state = 'queued'
                   WHERE collection_run_id = ? AND job_id IS NULL""",
                (result.job.job_id, run_id),
            )
            conn.execute(
                """INSERT OR IGNORE INTO collection_run_attempts
                   (collection_run_id, attempt, job_id, state, started_at,
                    access_partition_id)
                   VALUES (?, 1, ?, 'queued', ?, ?)""",
                (run_id, result.job.job_id, now, spec.access_partition_id),
            )
            row = conn.execute(
                "SELECT * FROM collection_runs WHERE collection_run_id = ?",
                (run_id,),
            ).fetchone()
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
        return self._run_from_row(row)

    def enqueue_due(self, *, limit: int = 10) -> tuple[CollectionRun, ...]:
        if not 1 <= limit <= 1000:
            raise ValueError("limit must be between 1 and 1000")
        self.reconcile_terminal_jobs()
        now = self._now()
        now_text = _timestamp(now)
        conn = self._connect()
        try:
            rows = conn.execute(
                """SELECT s.collection_spec_id, r.spec_json, q.next_due_at
                   FROM collection_specs AS s
                   JOIN collection_spec_revisions AS r
                     ON r.collection_spec_id = s.collection_spec_id
                    AND r.spec_version = s.spec_version
                   JOIN collection_schedule_state AS q
                     ON q.collection_spec_id = s.collection_spec_id
                   WHERE s.enabled = 1
                     AND q.next_due_at <= ?
                     AND (q.retry_after IS NULL OR q.retry_after <= ?)
                     AND NOT EXISTS (
                         SELECT 1
                         FROM collection_runs AS active
                         LEFT JOIN service_jobs AS job
                           ON job.job_id = active.job_id
                         WHERE active.collection_spec_id = s.collection_spec_id
                           AND active.state NOT IN ('published', 'partial', 'failed')
                           AND (
                               active.job_id IS NULL
                               OR job.job_id IS NULL
                               OR job.state NOT IN ('published', 'partial', 'failed')
                           )
                     )
                   ORDER BY q.next_due_at, s.collection_spec_id
                   LIMIT ?""",
                (now_text, now_text, limit),
            ).fetchall()
        finally:
            conn.close()
        created: list[CollectionRun] = []
        for row in rows:
            spec = CollectionSpec.from_dict(json.loads(row["spec_json"]))
            run = self.enqueue_interval(
                spec.collection_spec_id,
                scheduled_for=row["next_due_at"],
                trigger="timer",
            )
            created.append(run)
            due = _parse_timestamp(row["next_due_at"], "next_due_at")
            while due <= now:
                due += timedelta(seconds=spec.interval_seconds)
            conn = self._connect()
            try:
                conn.execute(
                    """UPDATE collection_schedule_state
                       SET next_due_at = ?, last_scheduled_at = ?
                       WHERE collection_spec_id = ?""",
                    (_timestamp(due), row["next_due_at"], spec.collection_spec_id),
                )
                conn.commit()
            finally:
                conn.close()
        return tuple(created)

    def reconcile_terminal_jobs(self) -> int:
        """Close collection state when supervisor recovery terminalized a job."""
        conn = self._connect()
        try:
            rows = conn.execute(
                """SELECT DISTINCT j.job_id, j.state, j.error_code, s.source
                   FROM service_jobs AS j
                   JOIN collection_runs AS r ON r.job_id = j.job_id
                   JOIN collection_specs AS s
                     ON s.collection_spec_id = r.collection_spec_id
                   WHERE j.state IN ('published', 'partial', 'failed')
                     AND r.state NOT IN ('published', 'partial', 'failed')
                   ORDER BY j.job_id"""
            ).fetchall()
        finally:
            conn.close()
        for row in rows:
            completed_at = self._now()
            conn = self._connect()
            try:
                conn.execute(
                    """UPDATE collection_run_attempts
                       SET state = ?, completed_at = COALESCE(completed_at, ?),
                           error_code = COALESCE(error_code, ?)
                       WHERE job_id = ?
                         AND state NOT IN ('published', 'partial', 'failed')""",
                    (
                        row["state"],
                        _timestamp(completed_at),
                        row["error_code"],
                        row["job_id"],
                    ),
                )
                conn.commit()
            finally:
                conn.close()
            self.record_completion(
                job_id=row["job_id"],
                state=row["state"],
                outcomes=(
                    {
                        "attempted_count": 0,
                        "observed_count": 0,
                        "stored_count": 0,
                        "error_code": row["error_code"],
                        "source": row["source"],
                        "status": (
                            "succeeded"
                            if row["state"] == "published"
                            else row["state"]
                        ),
                        "retry_after": None,
                        "retry": (
                            {
                                "eligible": False,
                                "reason": "missing_attempt_receipt",
                            }
                            if row["error_code"]
                            == "manual_retry_evidence_missing"
                            else None
                        ),
                    },
                ),
                completed_at=completed_at,
            )
        return len(rows)

    def record_started(
        self,
        *,
        job_id: str,
        worker_id: str,
        lease_generation: int,
        pre_snapshot: Mapping[str, object] | None = None,
    ) -> None:
        now = _timestamp(self._now())
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            runs = conn.execute(
                """SELECT r.collection_run_id, r.access_partition_id, s.profile_id
                   FROM collection_runs AS r
                   JOIN collection_specs AS s
                     ON s.collection_spec_id = r.collection_spec_id
                   WHERE r.job_id = ?""",
                (job_id,),
            ).fetchall()
            lease_expires_at = _timestamp(
                self._now() + timedelta(seconds=3900)
            )
            for run in runs:
                existing = conn.execute(
                    """SELECT collection_run_id, lease_expires_at
                       FROM collection_profile_leases
                       WHERE profile_id = ?""",
                    (run["profile_id"],),
                ).fetchone()
                if (
                    existing is not None
                    and existing["collection_run_id"] != run["collection_run_id"]
                    and _parse_timestamp(
                        existing["lease_expires_at"], "lease_expires_at"
                    )
                    > self._now()
                ):
                    raise RuntimeError("collection profile is already leased")
                conn.execute(
                    """INSERT INTO collection_profile_leases
                       (profile_id, collection_run_id, lease_owner,
                        lease_generation, lease_expires_at, access_partition_id)
                       VALUES (?, ?, ?, ?, ?, ?)
                       ON CONFLICT(profile_id) DO UPDATE SET
                         collection_run_id = excluded.collection_run_id,
                         lease_owner = excluded.lease_owner,
                         lease_generation = excluded.lease_generation,
                         lease_expires_at = excluded.lease_expires_at,
                         access_partition_id = excluded.access_partition_id""",
                    (
                        run["profile_id"],
                        run["collection_run_id"],
                        worker_id,
                        lease_generation,
                        lease_expires_at,
                        run["access_partition_id"],
                    ),
                )
                if pre_snapshot is not None:
                    self._put_observability_envelope(
                        conn,
                        envelope_type="collection_run_attempt_start",
                        envelope_id=(
                            f"{run['collection_run_id']}:{lease_generation}"
                        ),
                        payload={
                            "schema_version": 1,
                            "collection_run_id": run["collection_run_id"],
                            "attempt": lease_generation,
                            "captured_at": now,
                            "snapshot": dict(pre_snapshot),
                        },
                    )
            conn.execute(
                """UPDATE collection_runs
                   SET state = 'acquiring', claimed_by = ?,
                       lease_generation = ?, started_at = COALESCE(started_at, ?),
                       completed_at = NULL, error_code = NULL
                   WHERE job_id = ?""",
                (worker_id, lease_generation, now, job_id),
            )
            conn.execute(
                """INSERT INTO collection_run_attempts
                   (collection_run_id, attempt, job_id, state, started_at,
                    access_partition_id)
                   SELECT collection_run_id, ?, job_id, 'acquiring', ?,
                          access_partition_id
                   FROM collection_runs
                   WHERE job_id = ?
                   ON CONFLICT(collection_run_id, attempt) DO UPDATE SET
                     state = excluded.state,
                     started_at = excluded.started_at,
                     completed_at = NULL,
                     error_code = NULL""",
                (lease_generation, now, job_id),
            )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def record_assessment(
        self,
        *,
        job_id: str,
        acquisition_id: str,
        state: str,
        item_count: int,
        task_id: str | None = None,
        error_code: str | None = None,
    ) -> None:
        now = _timestamp(self._now())
        conn = self._connect()
        try:
            rows = conn.execute(
                "SELECT * FROM collection_runs WHERE job_id = ?",
                (job_id,),
            ).fetchall()
            for row in rows:
                batch_id = _stable_id(
                    "assessment-batch",
                    {
                        "collection_run_id": row["collection_run_id"],
                        "acquisition_id": acquisition_id,
                    },
                )
                conn.execute(
                    """INSERT INTO collection_assessment_batches
                       (assessment_batch_id, collection_run_id,
                        collection_spec_id, acquisition_id, task_id, state,
                        item_count, error_code, created_at, updated_at,
                        access_partition_id)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                       ON CONFLICT(collection_run_id, acquisition_id) DO UPDATE SET
                         task_id = excluded.task_id,
                         state = excluded.state,
                         item_count = excluded.item_count,
                         error_code = excluded.error_code,
                         updated_at = excluded.updated_at""",
                    (
                        batch_id,
                        row["collection_run_id"],
                        row["collection_spec_id"],
                        acquisition_id,
                        task_id,
                        state,
                        item_count,
                        error_code,
                        now,
                        now,
                        row["access_partition_id"],
                    ),
                )
            conn.commit()
        finally:
            conn.close()

    def record_completion(
        self,
        *,
        job_id: str,
        state: str,
        outcomes: tuple[Mapping[str, object], ...],
        completed_at: datetime,
        pre_snapshot: Mapping[str, object] | None = None,
        post_snapshot: Mapping[str, object] | None = None,
    ) -> None:
        completed = _timestamp(completed_at)
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            runs = conn.execute(
                "SELECT * FROM collection_runs WHERE job_id = ?",
                (job_id,),
            ).fetchall()
            for run in runs:
                attempted = sum(int(item.get("attempted_count") or 0) for item in outcomes)
                observed = sum(int(item.get("observed_count") or 0) for item in outcomes)
                stored = sum(int(item.get("stored_count") or 0) for item in outcomes)
                network_values = [
                    item.get("network_request_count") for item in outcomes
                ]
                network_requests = (
                    sum(int(value) for value in network_values)
                    if all(
                        isinstance(value, int) and not isinstance(value, bool)
                        for value in network_values
                    )
                    else None
                )
                accepted = sum(int(item.get("accepted_count") or 0) for item in outcomes)
                rejected = sum(int(item.get("rejected_count") or 0) for item in outcomes)
                deduplicated = sum(
                    int(item.get("deduplicated_count") or 0) for item in outcomes
                )
                indexed = sum(int(item.get("indexed_count") or 0) for item in outcomes)
                attempted_methods: list[str] = []
                for item in outcomes:
                    methods = item.get("attempted_access_methods")
                    if isinstance(methods, list):
                        for method in methods:
                            if isinstance(method, str) and method not in attempted_methods:
                                attempted_methods.append(method)
                selected_method = next(
                    (
                        str(item["selected_access_method"])
                        for item in outcomes
                        if item.get("selected_access_method") is not None
                    ),
                    None,
                )
                adapter_variant = next(
                    (
                        str(item["adapter_variant"])
                        for item in outcomes
                        if item.get("adapter_variant") is not None
                    ),
                    None,
                )
                before = pre_snapshot or {}
                after = post_snapshot or {}
                error_code = next(
                    (
                        str(item["error_code"])
                        for item in outcomes
                        if item.get("error_code")
                    ),
                    None,
                )
                cursor_after = next(
                    (
                        str(item["cursor_after"])
                        for item in outcomes
                        if item.get("cursor_after") is not None
                    ),
                    None,
                )
                watermark_after = next(
                    (
                        str(item["watermark_after"])
                        for item in outcomes
                        if item.get("watermark_after") is not None
                    ),
                    None,
                )
                retry = next(
                    (
                        dict(item["retry"])
                        for item in outcomes
                        if isinstance(item.get("retry"), Mapping)
                    ),
                    None,
                )
                conn.execute(
                    """UPDATE collection_runs
                       SET state = ?, completed_at = ?, cursor_after = ?,
                           watermark_after = ?, attempted_count = ?,
                           observed_count = ?, stored_count = ?, error_code = ?
                       WHERE collection_run_id = ?""",
                    (
                        state,
                        completed,
                        cursor_after,
                        watermark_after,
                        attempted,
                        observed,
                        stored,
                        error_code,
                        run["collection_run_id"],
                    ),
                )
                receipt = {
                    "schema_version": 1,
                    "collection_run_id": run["collection_run_id"],
                    "collection_spec_id": run["collection_spec_id"],
                    "job_id": job_id,
                    "attempt": run["lease_generation"],
                    "state": state,
                    "completed_at": completed,
                    "network_request_count": network_requests,
                    "counts": {
                        "attempted": attempted,
                        "observed": observed,
                        "accepted": accepted,
                        "rejected": rejected,
                        "stored": stored,
                        "deduplicated": deduplicated,
                        "indexed": indexed,
                    },
                    "pre_snapshot": dict(before),
                    "post_snapshot": dict(after),
                    "provenance": {
                        "attempted_access_methods": attempted_methods,
                        "selected_access_method": selected_method,
                        "adapter_variant": adapter_variant,
                    },
                    "error_code": error_code,
                    "retry": retry,
                }
                self._put_observability_envelope(
                    conn,
                    envelope_type="collection_run_receipt",
                    envelope_id=(
                        f"{run['collection_run_id']}:{run['lease_generation']}"
                    ),
                    payload=receipt,
                )
                conn.execute(
                    """UPDATE collection_run_attempts
                       SET state = ?, completed_at = ?, error_code = ?
                       WHERE collection_run_id = ? AND attempt = ?""",
                    (
                        state,
                        completed,
                        error_code,
                        run["collection_run_id"],
                        run["lease_generation"],
                    ),
                )
                coverage_state = (
                    "observed"
                    if observed > 0
                    else "observed_empty"
                    if state in {"published", "partial"}
                    else "failed"
                )
                spec = self.get_spec_revision(
                    run["collection_spec_id"],
                    int(run["spec_version"]),
                )
                coverage_id = _stable_id(
                    "coverage",
                    {
                        "collection_run_id": run["collection_run_id"],
                        "selector": spec.selector_digest,
                    },
                )
                conn.execute(
                    """INSERT OR REPLACE INTO collection_coverage_intervals
                       (coverage_id, collection_run_id, collection_spec_id,
                        interval_from, interval_to, coverage_state,
                        selector_digest, attempted_count, observed_count,
                        access_partition_id, recorded_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        coverage_id,
                        run["collection_run_id"],
                        run["collection_spec_id"],
                        run["interval_from"],
                        run["interval_to"],
                        coverage_state,
                        spec.selector_digest,
                        attempted,
                        observed,
                        run["access_partition_id"],
                        completed,
                    ),
                )
                if state in {"published", "partial"}:
                    conn.execute(
                        """UPDATE collection_cursors
                           SET cursor_value = COALESCE(?, cursor_value),
                               watermark_value = COALESCE(?, watermark_value),
                               updated_at = ?
                           WHERE collection_spec_id = ?""",
                        (
                            cursor_after,
                            watermark_after,
                            completed,
                            run["collection_spec_id"],
                        ),
                    )
                    conn.execute(
                        """UPDATE collection_gaps
                           SET status = 'resolved', resolved_at = ?
                           WHERE collection_spec_id = ? AND status = 'open'
                             AND interval_from = ? AND interval_to = ?""",
                        (
                            completed,
                            run["collection_spec_id"],
                            run["interval_from"],
                            run["interval_to"],
                        ),
                    )
                else:
                    gap_id = _stable_id(
                        "gap",
                        {
                            "collection_run_id": run["collection_run_id"],
                            "kind": "acquisition_failed",
                        },
                    )
                    conn.execute(
                        """INSERT OR IGNORE INTO collection_gaps
                           (gap_id, collection_spec_id, collection_run_id,
                            gap_kind, interval_from, interval_to, detail_json,
                            status, access_partition_id, detected_at, resolved_at)
                           VALUES (?, ?, ?, 'acquisition_failed', ?, ?, ?,
                                   'open', ?, ?, NULL)""",
                        (
                            gap_id,
                            run["collection_spec_id"],
                            run["collection_run_id"],
                            run["interval_from"],
                            run["interval_to"],
                            _canonical_json({"error_code": error_code}),
                            run["access_partition_id"],
                            completed,
                        ),
                    )
                for outcome in outcomes:
                    source = str(outcome["source"])
                    outcome_status = str(outcome["status"])
                    outcome_attempted = int(outcome.get("attempted_count") or 0)
                    outcome_observed = int(outcome.get("observed_count") or 0)
                    failed = outcome_status not in {"succeeded", "partial"}
                    previous = conn.execute(
                        """SELECT consecutive_failures
                           FROM collection_source_health
                           WHERE collection_spec_id = ? AND source = ?""",
                        (run["collection_spec_id"], source),
                    ).fetchone()
                    failure_count = (
                        (int(previous[0]) if previous else 0) + 1 if failed else 0
                    )
                    conn.execute(
                        """INSERT INTO collection_source_health
                           (collection_spec_id, source, process_state, yield_state,
                            last_status, last_attempted_count, last_observed_count,
                            consecutive_failures, retry_after, error_code,
                            updated_at, access_partition_id)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                           ON CONFLICT(collection_spec_id, source) DO UPDATE SET
                             process_state = excluded.process_state,
                             yield_state = excluded.yield_state,
                             last_status = excluded.last_status,
                             last_attempted_count = excluded.last_attempted_count,
                             last_observed_count = excluded.last_observed_count,
                             consecutive_failures = excluded.consecutive_failures,
                             retry_after = excluded.retry_after,
                             error_code = excluded.error_code,
                             updated_at = excluded.updated_at""",
                        (
                            run["collection_spec_id"],
                            source,
                            "degraded" if failed else "healthy",
                            "nonzero" if outcome_observed else "zero",
                            outcome_status,
                            outcome_attempted,
                            outcome_observed,
                            failure_count,
                            outcome.get("retry_after"),
                            outcome.get("error_code"),
                            completed,
                            run["access_partition_id"],
                        ),
                    )
                retry_values = sorted(
                    str(item["retry_after"])
                    for item in outcomes
                    if item.get("retry_after")
                )
                conn.execute(
                    """UPDATE collection_schedule_state
                       SET consecutive_failures =
                             CASE WHEN ? IN ('published', 'partial')
                                  THEN 0 ELSE consecutive_failures + 1 END,
                           retry_after = CASE
                             WHEN ? IN ('published', 'partial') THEN NULL
                             ELSE ? END
                       WHERE collection_spec_id = ?""",
                    (
                        state,
                        state,
                        retry_values[0] if retry_values else None,
                        run["collection_spec_id"],
                    ),
                )
                conn.execute(
                    """DELETE FROM collection_profile_leases
                       WHERE collection_run_id = ?""",
                    (run["collection_run_id"],),
                )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
