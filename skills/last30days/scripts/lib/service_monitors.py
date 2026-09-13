"""Provider-free saved-monitor persistence and comparison kernel."""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sqlite3
from typing import Callable

import store

from . import service_monitor_contracts as contracts


MonitorErrorCode = contracts.MonitorErrorCode
MONITOR_SCHEMA_VERSION = 1

MONITOR_SCHEMA_V1 = """
BEGIN IMMEDIATE;

CREATE TABLE IF NOT EXISTS service_monitor_schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS service_monitor_specs (
    monitor_id TEXT NOT NULL,
    revision INTEGER NOT NULL CHECK (revision > 0),
    access_partition_id TEXT NOT NULL,
    view_kind TEXT NOT NULL CHECK (view_kind = 'saved_query'),
    view_id TEXT NOT NULL,
    view_revision INTEGER NOT NULL CHECK (view_revision > 0),
    lifecycle_state TEXT NOT NULL
        CHECK (lifecycle_state IN ('disabled', 'active', 'paused', 'archived')),
    payload_json TEXT NOT NULL,
    payload_sha256 TEXT NOT NULL,
    created_at TEXT NOT NULL,
    PRIMARY KEY (monitor_id, revision)
);

CREATE TABLE IF NOT EXISTS service_monitor_view_snapshots (
    snapshot_id TEXT PRIMARY KEY,
    access_partition_id TEXT NOT NULL,
    view_id TEXT NOT NULL,
    view_revision INTEGER NOT NULL CHECK (view_revision > 0),
    evidence_head_id TEXT NOT NULL,
    knowledge_cutoff TEXT NOT NULL,
    coverage_status TEXT NOT NULL
        CHECK (coverage_status IN ('complete', 'partial')),
    payload_json TEXT NOT NULL,
    payload_sha256 TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS service_monitor_runs (
    run_id TEXT PRIMARY KEY,
    monitor_id TEXT NOT NULL,
    monitor_revision INTEGER NOT NULL,
    snapshot_id TEXT NOT NULL
        REFERENCES service_monitor_view_snapshots(snapshot_id),
    prior_baseline_id TEXT,
    candidate_baseline_id TEXT NOT NULL UNIQUE,
    comparison_status TEXT NOT NULL
        CHECK (comparison_status IN (
            'baseline_only', 'complete', 'comparison_incomplete'
        )),
    payload_json TEXT NOT NULL,
    payload_sha256 TEXT NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE (run_id, monitor_id),
    FOREIGN KEY (monitor_id, monitor_revision)
        REFERENCES service_monitor_specs(monitor_id, revision)
);

CREATE TABLE IF NOT EXISTS service_monitor_baselines (
    baseline_id TEXT PRIMARY KEY,
    monitor_id TEXT NOT NULL,
    monitor_revision INTEGER NOT NULL,
    snapshot_id TEXT NOT NULL
        REFERENCES service_monitor_view_snapshots(snapshot_id),
    run_id TEXT NOT NULL UNIQUE REFERENCES service_monitor_runs(run_id),
    payload_json TEXT NOT NULL,
    payload_sha256 TEXT NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE (baseline_id, monitor_id),
    FOREIGN KEY (monitor_id, monitor_revision)
        REFERENCES service_monitor_specs(monitor_id, revision)
);

CREATE TABLE IF NOT EXISTS service_monitor_decisions (
    decision_id TEXT PRIMARY KEY,
    monitor_id TEXT NOT NULL,
    run_id TEXT NOT NULL UNIQUE REFERENCES service_monitor_runs(run_id),
    baseline_id TEXT NOT NULL REFERENCES service_monitor_baselines(baseline_id),
    decision TEXT NOT NULL CHECK (decision IN ('accepted', 'rejected')),
    payload_json TEXT NOT NULL,
    payload_sha256 TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (run_id, monitor_id)
        REFERENCES service_monitor_runs(run_id, monitor_id),
    FOREIGN KEY (baseline_id, monitor_id)
        REFERENCES service_monitor_baselines(baseline_id, monitor_id)
);

CREATE TABLE IF NOT EXISTS service_monitor_baseline_heads (
    monitor_id TEXT PRIMARY KEY,
    baseline_id TEXT NOT NULL REFERENCES service_monitor_baselines(baseline_id),
    decision_id TEXT NOT NULL REFERENCES service_monitor_decisions(decision_id),
    updated_at TEXT NOT NULL,
    FOREIGN KEY (baseline_id, monitor_id)
        REFERENCES service_monitor_baselines(baseline_id, monitor_id)
);

CREATE INDEX IF NOT EXISTS idx_service_monitor_specs_current
    ON service_monitor_specs(monitor_id, revision DESC);
CREATE INDEX IF NOT EXISTS idx_service_monitor_runs_monitor
    ON service_monitor_runs(monitor_id, created_at, run_id);

CREATE TRIGGER IF NOT EXISTS service_monitor_specs_immutable_update
BEFORE UPDATE ON service_monitor_specs BEGIN
    SELECT RAISE(ABORT, 'monitor spec is immutable');
END;
CREATE TRIGGER IF NOT EXISTS service_monitor_specs_immutable_delete
BEFORE DELETE ON service_monitor_specs BEGIN
    SELECT RAISE(ABORT, 'monitor spec is immutable');
END;
CREATE TRIGGER IF NOT EXISTS service_monitor_view_snapshots_immutable_update
BEFORE UPDATE ON service_monitor_view_snapshots BEGIN
    SELECT RAISE(ABORT, 'monitor view snapshot is immutable');
END;
CREATE TRIGGER IF NOT EXISTS service_monitor_view_snapshots_immutable_delete
BEFORE DELETE ON service_monitor_view_snapshots BEGIN
    SELECT RAISE(ABORT, 'monitor view snapshot is immutable');
END;
CREATE TRIGGER IF NOT EXISTS service_monitor_runs_immutable_update
BEFORE UPDATE ON service_monitor_runs BEGIN
    SELECT RAISE(ABORT, 'monitor run is immutable');
END;
CREATE TRIGGER IF NOT EXISTS service_monitor_runs_immutable_delete
BEFORE DELETE ON service_monitor_runs BEGIN
    SELECT RAISE(ABORT, 'monitor run is immutable');
END;
CREATE TRIGGER IF NOT EXISTS service_monitor_baselines_immutable_update
BEFORE UPDATE ON service_monitor_baselines BEGIN
    SELECT RAISE(ABORT, 'monitor baseline is immutable');
END;
CREATE TRIGGER IF NOT EXISTS service_monitor_baselines_immutable_delete
BEFORE DELETE ON service_monitor_baselines BEGIN
    SELECT RAISE(ABORT, 'monitor baseline is immutable');
END;
CREATE TRIGGER IF NOT EXISTS service_monitor_decisions_immutable_update
BEFORE UPDATE ON service_monitor_decisions BEGIN
    SELECT RAISE(ABORT, 'monitor decision is immutable');
END;
CREATE TRIGGER IF NOT EXISTS service_monitor_decisions_immutable_delete
BEFORE DELETE ON service_monitor_decisions BEGIN
    SELECT RAISE(ABORT, 'monitor decision is immutable');
END;

INSERT OR IGNORE INTO service_monitor_schema_version(version) VALUES (1);
COMMIT;
"""


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class MonitorKernelError(RuntimeError):
    """Fail-closed monitor error with a stable machine-readable code."""

    def __init__(
        self,
        code: contracts.MonitorErrorCode,
        message: str,
        *,
        monitor_id: str | None = None,
        run_id: str | None = None,
    ) -> None:
        self.code = code
        self.contract = contracts.MonitorErrorV1.from_dict(
            {
                "schema_version": contracts.SCHEMA_VERSION,
                "code": code.value,
                "message": message,
                "monitor_id": monitor_id,
                "run_id": run_id,
            }
        )
        super().__init__(message)


def _canonical_json(value: object) -> str:
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _stable_id(prefix: str, value: object) -> str:
    return f"{prefix}-{_digest(value)[:32]}"


class FakeSavedQueryViewProvider:
    """In-memory adapter exposing only pre-registered immutable query views."""

    def __init__(self) -> None:
        self._snapshots: dict[str, contracts.SavedQueryViewSnapshotV1] = {}

    def register(self, snapshot: contracts.SavedQueryViewSnapshotV1) -> None:
        existing = self._snapshots.get(snapshot.snapshot_id)
        if existing is not None and existing != snapshot:
            raise MonitorKernelError(
                MonitorErrorCode.IMMUTABLE_CONFLICT,
                f"immutable view snapshot conflict: {snapshot.snapshot_id}",
            )
        self._snapshots[snapshot.snapshot_id] = snapshot

    def read(
        self,
        view_ref: contracts.SavedQueryViewRefV1,
        access_partition_id: str,
        snapshot_id: str,
    ) -> contracts.SavedQueryViewSnapshotV1:
        snapshot = self._snapshots.get(snapshot_id)
        if snapshot is None:
            raise MonitorKernelError(
                MonitorErrorCode.VIEW_UNAVAILABLE,
                "saved query view snapshot is unavailable",
            )
        if snapshot.view_ref != view_ref:
            raise MonitorKernelError(
                MonitorErrorCode.VIEW_MISMATCH,
                "saved query view revision does not match the monitor",
            )
        if snapshot.access_partition_id != access_partition_id:
            raise MonitorKernelError(
                MonitorErrorCode.PARTITION_MISMATCH,
                "saved query view is not available in the monitor partition",
            )
        return snapshot


class MonitorRepository:
    """Durable module for immutable monitor records and the accepted head."""

    def __init__(self, db_path: Path) -> None:
        self.db_path = Path(db_path)

    def initialize(self) -> None:
        store.init_db(self.db_path)
        conn = self._connect()
        try:
            conn.executescript(MONITOR_SCHEMA_V1)
            version = conn.execute(
                "SELECT MAX(version) FROM service_monitor_schema_version"
            ).fetchone()[0]
            if version > MONITOR_SCHEMA_VERSION:
                raise MonitorKernelError(
                    MonitorErrorCode.SCHEMA_UNSUPPORTED,
                    f"monitor schema {version} is newer than supported "
                    f"version {MONITOR_SCHEMA_VERSION}",
                )
        finally:
            conn.close()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=5)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA busy_timeout=5000")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    @staticmethod
    def _serialized(contract: object) -> tuple[str, str]:
        payload = contract.to_dict()  # type: ignore[attr-defined]
        text = _canonical_json(payload)
        return text, hashlib.sha256(text.encode("utf-8")).hexdigest()

    @staticmethod
    def _immutable_insert(
        conn: sqlite3.Connection,
        *,
        table: str,
        key_column: str,
        key: str,
        digest: str,
        statement: str,
        values: tuple[object, ...],
    ) -> bool:
        existing = conn.execute(
            f"SELECT payload_sha256 FROM {table} WHERE {key_column} = ?",
            (key,),
        ).fetchone()
        if existing is not None:
            if existing["payload_sha256"] != digest:
                raise MonitorKernelError(
                    MonitorErrorCode.IMMUTABLE_CONFLICT,
                    f"immutable record conflict: {table}/{key}",
                )
            return False
        conn.execute(statement, values)
        return True

    def put_spec(self, spec: contracts.MonitorSpecV1) -> None:
        payload, digest = self._serialized(spec)
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            existing = conn.execute(
                """SELECT payload_sha256 FROM service_monitor_specs
                   WHERE monitor_id = ? AND revision = ?""",
                (spec.monitor_id, spec.revision),
            ).fetchone()
            if existing is not None:
                if existing["payload_sha256"] != digest:
                    raise MonitorKernelError(
                        MonitorErrorCode.IMMUTABLE_CONFLICT,
                        "immutable monitor spec conflict",
                    )
                conn.commit()
                return
            prior_row = conn.execute(
                """SELECT payload_json FROM service_monitor_specs
                   WHERE monitor_id = ? ORDER BY revision DESC LIMIT 1""",
                (spec.monitor_id,),
            ).fetchone()
            if prior_row is None:
                if spec.revision != 1 or (
                    spec.lifecycle_state is not contracts.MonitorLifecycle.DISABLED
                ):
                    raise MonitorKernelError(
                        MonitorErrorCode.INVALID_REVISION,
                        "a monitor must begin at revision 1 in disabled state",
                    )
            else:
                prior = contracts.MonitorSpecV1.from_dict(
                    json.loads(prior_row["payload_json"])
                )
                if spec.revision != prior.revision + 1:
                    raise MonitorKernelError(
                        MonitorErrorCode.INVALID_REVISION,
                        "monitor revisions must advance by exactly one",
                    )
                if (
                    spec.view_ref != prior.view_ref
                    or spec.access_partition_id != prior.access_partition_id
                ):
                    raise MonitorKernelError(
                        MonitorErrorCode.INVALID_REVISION,
                        "view identity and partition cannot change across revisions",
                    )
                self._validate_transition(prior.lifecycle_state, spec.lifecycle_state)
            conn.execute(
                """INSERT INTO service_monitor_specs (
                       monitor_id, revision, access_partition_id, view_kind,
                       view_id, view_revision, lifecycle_state, payload_json,
                       payload_sha256, created_at
                   ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    spec.monitor_id,
                    spec.revision,
                    spec.access_partition_id,
                    spec.view_ref.view_kind,
                    spec.view_ref.saved_query_id,
                    spec.view_ref.saved_query_version,
                    spec.lifecycle_state.value,
                    payload,
                    digest,
                    spec.created_at,
                ),
            )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    @staticmethod
    def _validate_transition(
        prior: contracts.MonitorLifecycle,
        current: contracts.MonitorLifecycle,
    ) -> None:
        allowed = {
            contracts.MonitorLifecycle.DISABLED: {
                contracts.MonitorLifecycle.ACTIVE,
                contracts.MonitorLifecycle.ARCHIVED,
            },
            contracts.MonitorLifecycle.ACTIVE: {
                contracts.MonitorLifecycle.PAUSED,
                contracts.MonitorLifecycle.ARCHIVED,
            },
            contracts.MonitorLifecycle.PAUSED: {
                contracts.MonitorLifecycle.ACTIVE,
                contracts.MonitorLifecycle.ARCHIVED,
            },
            contracts.MonitorLifecycle.ARCHIVED: set(),
        }
        if current not in allowed[prior]:
            raise MonitorKernelError(
                MonitorErrorCode.INVALID_LIFECYCLE,
                f"invalid monitor lifecycle transition: {prior.value}->{current.value}",
            )

    def current_spec(self, monitor_id: str) -> contracts.MonitorSpecV1:
        conn = self._connect()
        try:
            row = conn.execute(
                """SELECT payload_json FROM service_monitor_specs
                   WHERE monitor_id = ? ORDER BY revision DESC LIMIT 1""",
                (monitor_id,),
            ).fetchone()
        finally:
            conn.close()
        if row is None:
            raise KeyError(f"monitor not found: {monitor_id}")
        return contracts.MonitorSpecV1.from_dict(json.loads(row["payload_json"]))

    def put_snapshot(self, snapshot: contracts.SavedQueryViewSnapshotV1) -> None:
        payload, digest = self._serialized(snapshot)
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            self._immutable_insert(
                conn,
                table="service_monitor_view_snapshots",
                key_column="snapshot_id",
                key=snapshot.snapshot_id,
                digest=digest,
                statement="""INSERT INTO service_monitor_view_snapshots (
                    snapshot_id, access_partition_id, view_id, view_revision,
                    evidence_head_id, knowledge_cutoff, coverage_status,
                    payload_json, payload_sha256
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                values=(
                    snapshot.snapshot_id,
                    snapshot.access_partition_id,
                    snapshot.view_ref.saved_query_id,
                    snapshot.view_ref.saved_query_version,
                    snapshot.evidence_head_id,
                    snapshot.knowledge_cutoff,
                    snapshot.coverage.status.value,
                    payload,
                    digest,
                ),
            )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def get_run(self, run_id: str) -> contracts.MonitorRunV1:
        return self._read_contract(
            "service_monitor_runs",
            "run_id",
            run_id,
            contracts.MonitorRunV1.from_dict,
        )

    def get_baseline(self, baseline_id: str) -> contracts.MonitorBaselineV1:
        return self._read_contract(
            "service_monitor_baselines",
            "baseline_id",
            baseline_id,
            contracts.MonitorBaselineV1.from_dict,
        )

    def _read_contract(self, table, key_column, key, parser):
        conn = self._connect()
        try:
            row = conn.execute(
                f"SELECT payload_json, payload_sha256 FROM {table} "
                f"WHERE {key_column} = ?",
                (key,),
            ).fetchone()
        finally:
            conn.close()
        if row is None:
            raise KeyError(f"record not found: {table}/{key}")
        digest = hashlib.sha256(row["payload_json"].encode("utf-8")).hexdigest()
        if digest != row["payload_sha256"]:
            raise MonitorKernelError(
                MonitorErrorCode.IMMUTABLE_CONFLICT,
                f"persisted record hash mismatch: {table}/{key}",
            )
        return parser(json.loads(row["payload_json"]))

    def put_run_and_baseline(
        self,
        run: contracts.MonitorRunV1,
        baseline: contracts.MonitorBaselineV1,
    ) -> contracts.MonitorRunV1:
        run_payload, run_digest = self._serialized(run)
        baseline_payload, baseline_digest = self._serialized(baseline)
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            existing = conn.execute(
                "SELECT payload_json, payload_sha256 FROM service_monitor_runs WHERE run_id = ?",
                (run.run_id,),
            ).fetchone()
            if existing is not None:
                if existing["payload_sha256"] != run_digest:
                    raise MonitorKernelError(
                        MonitorErrorCode.IMMUTABLE_CONFLICT,
                        "immutable monitor run conflict",
                    )
                conn.commit()
                return contracts.MonitorRunV1.from_dict(
                    json.loads(existing["payload_json"])
                )
            conn.execute(
                """INSERT INTO service_monitor_runs (
                       run_id, monitor_id, monitor_revision, snapshot_id,
                       prior_baseline_id, candidate_baseline_id,
                       comparison_status, payload_json, payload_sha256, created_at
                   ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    run.run_id,
                    run.monitor_id,
                    run.monitor_revision,
                    run.snapshot_id,
                    run.prior_baseline_id,
                    run.candidate_baseline_id,
                    run.comparison.status.value,
                    run_payload,
                    run_digest,
                    run.created_at,
                ),
            )
            conn.execute(
                """INSERT INTO service_monitor_baselines (
                       baseline_id, monitor_id, monitor_revision, snapshot_id,
                       run_id, payload_json, payload_sha256, created_at
                   ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    baseline.baseline_id,
                    baseline.monitor_id,
                    baseline.monitor_revision,
                    baseline.snapshot_id,
                    run.run_id,
                    baseline_payload,
                    baseline_digest,
                    baseline.created_at,
                ),
            )
            conn.commit()
            return run
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def current_baseline(
        self, monitor_id: str
    ) -> contracts.MonitorBaselineV1 | None:
        conn = self._connect()
        try:
            row = conn.execute(
                "SELECT baseline_id FROM service_monitor_baseline_heads WHERE monitor_id = ?",
                (monitor_id,),
            ).fetchone()
        finally:
            conn.close()
        return None if row is None else self.get_baseline(row["baseline_id"])

    def decide(
        self,
        run: contracts.MonitorRunV1,
        decision: contracts.MonitorDecisionV1,
    ) -> contracts.MonitorDecisionV1:
        payload, digest = self._serialized(decision)
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            existing = conn.execute(
                """SELECT payload_json FROM service_monitor_decisions
                   WHERE run_id = ?""",
                (run.run_id,),
            ).fetchone()
            if existing is not None:
                prior = contracts.MonitorDecisionV1.from_dict(
                    json.loads(existing["payload_json"])
                )
                if prior.decision is not decision.decision:
                    raise MonitorKernelError(
                        MonitorErrorCode.DECISION_CONFLICT,
                        "monitor run already has the opposite decision",
                    )
                conn.commit()
                return prior
            if decision.decision is contracts.DecisionKind.ACCEPTED:
                if run.comparison.status is contracts.ComparisonStatus.INCOMPLETE:
                    raise MonitorKernelError(
                        MonitorErrorCode.COMPARISON_INCOMPLETE,
                        "an incomplete comparison cannot advance the baseline",
                    )
                head = conn.execute(
                    """SELECT baseline_id FROM service_monitor_baseline_heads
                       WHERE monitor_id = ?""",
                    (run.monitor_id,),
                ).fetchone()
                current_id = None if head is None else head["baseline_id"]
                if current_id != run.prior_baseline_id:
                    raise MonitorKernelError(
                        MonitorErrorCode.STALE_BASELINE,
                        "accepted baseline changed after this run was prepared",
                    )
            conn.execute(
                """INSERT INTO service_monitor_decisions (
                       decision_id, monitor_id, run_id, baseline_id, decision,
                       payload_json, payload_sha256, created_at
                   ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    decision.decision_id,
                    decision.monitor_id,
                    decision.run_id,
                    decision.baseline_id,
                    decision.decision.value,
                    payload,
                    digest,
                    decision.decided_at,
                ),
            )
            if decision.decision is contracts.DecisionKind.ACCEPTED:
                conn.execute(
                    """INSERT INTO service_monitor_baseline_heads (
                           monitor_id, baseline_id, decision_id, updated_at
                       ) VALUES (?, ?, ?, ?)
                       ON CONFLICT(monitor_id) DO UPDATE SET
                           baseline_id = excluded.baseline_id,
                           decision_id = excluded.decision_id,
                           updated_at = excluded.updated_at""",
                    (
                        run.monitor_id,
                        run.candidate_baseline_id,
                        decision.decision_id,
                        decision.decided_at,
                    ),
                )
            conn.commit()
            return decision
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()


class MonitorKernel:
    """Deep monitor module: lifecycle, frozen evaluation, replay, and acceptance."""

    def __init__(
        self,
        repository: MonitorRepository,
        view_provider: FakeSavedQueryViewProvider,
        *,
        clock: Callable[[], str] | None = None,
    ) -> None:
        self.repository = repository
        self.view_provider = view_provider
        self.clock = clock or _utc_now

    def create(self, spec: contracts.MonitorSpecV1) -> contracts.MonitorSpecV1:
        self.repository.put_spec(spec)
        return spec

    def _transition(
        self,
        monitor_id: str,
        state: contracts.MonitorLifecycle,
        actor: str,
    ) -> contracts.MonitorSpecV1:
        prior = self.repository.current_spec(monitor_id)
        current = replace(
            prior,
            revision=prior.revision + 1,
            lifecycle_state=state,
            created_by=actor,
            created_at=self.clock(),
        )
        self.repository.put_spec(current)
        return current

    def activate(self, monitor_id: str, *, actor: str) -> contracts.MonitorSpecV1:
        return self._transition(
            monitor_id, contracts.MonitorLifecycle.ACTIVE, actor
        )

    def pause(self, monitor_id: str, *, actor: str) -> contracts.MonitorSpecV1:
        return self._transition(
            monitor_id, contracts.MonitorLifecycle.PAUSED, actor
        )

    def resume(
        self, monitor_id: str, snapshot_id: str, *, actor: str
    ) -> contracts.MonitorSpecV1:
        prior = self.repository.current_spec(monitor_id)
        if prior.lifecycle_state is not contracts.MonitorLifecycle.PAUSED:
            raise MonitorKernelError(
                MonitorErrorCode.INVALID_LIFECYCLE,
                "only a paused monitor can resume",
                monitor_id=monitor_id,
            )
        self.view_provider.read(
            prior.view_ref, prior.access_partition_id, snapshot_id
        )
        return self._transition(
            monitor_id, contracts.MonitorLifecycle.ACTIVE, actor
        )

    def archive(self, monitor_id: str, *, actor: str) -> contracts.MonitorSpecV1:
        return self._transition(
            monitor_id, contracts.MonitorLifecycle.ARCHIVED, actor
        )

    def evaluate(self, monitor_id: str, snapshot_id: str) -> contracts.MonitorRunV1:
        spec = self.repository.current_spec(monitor_id)
        if spec.lifecycle_state is contracts.MonitorLifecycle.PAUSED:
            raise MonitorKernelError(
                MonitorErrorCode.MONITOR_PAUSED, "paused monitor cannot run"
            )
        if spec.lifecycle_state is contracts.MonitorLifecycle.ARCHIVED:
            raise MonitorKernelError(
                MonitorErrorCode.MONITOR_ARCHIVED, "archived monitor cannot run"
            )
        if spec.lifecycle_state is not contracts.MonitorLifecycle.ACTIVE:
            raise MonitorKernelError(
                MonitorErrorCode.INVALID_LIFECYCLE, "disabled monitor cannot run"
            )
        snapshot = self.view_provider.read(
            spec.view_ref, spec.access_partition_id, snapshot_id
        )
        self.repository.put_snapshot(snapshot)
        prior = self.repository.current_baseline(monitor_id)
        run_identity = {
            "schema_version": contracts.SCHEMA_VERSION,
            "monitor_id": spec.monitor_id,
            "monitor_revision": spec.revision,
            "snapshot": snapshot.to_dict(),
            "prior_baseline_id": None if prior is None else prior.baseline_id,
            "comparator_version": contracts.COMPARATOR_VERSION,
        }
        run_id = _stable_id("monitor-run", run_identity)
        try:
            return self.repository.get_run(run_id)
        except KeyError:
            pass
        comparison, candidate_evidence = self._compare(snapshot, prior)
        created_at = self.clock()
        baseline_id = _stable_id("monitor-baseline", {"run_id": run_id})
        baseline = contracts.MonitorBaselineV1.from_dict(
            {
                "schema_version": contracts.SCHEMA_VERSION,
                "baseline_id": baseline_id,
                "monitor_id": spec.monitor_id,
                "monitor_revision": spec.revision,
                "snapshot_id": snapshot.snapshot_id,
                "access_partition_id": spec.access_partition_id,
                "evidence_head_id": snapshot.evidence_head_id,
                "knowledge_cutoff": snapshot.knowledge_cutoff,
                "evidence": [item.to_dict() for item in candidate_evidence],
                "created_at": created_at,
            }
        )
        run = contracts.MonitorRunV1.from_dict(
            {
                "schema_version": contracts.SCHEMA_VERSION,
                "run_id": run_id,
                "monitor_id": spec.monitor_id,
                "monitor_revision": spec.revision,
                "snapshot_id": snapshot.snapshot_id,
                "prior_baseline_id": None if prior is None else prior.baseline_id,
                "candidate_baseline_id": baseline_id,
                "comparison": comparison.to_dict(),
                "created_at": created_at,
            }
        )
        return self.repository.put_run_and_baseline(run, baseline)

    @staticmethod
    def _compare(
        snapshot: contracts.SavedQueryViewSnapshotV1,
        prior: contracts.MonitorBaselineV1 | None,
    ) -> tuple[
        contracts.MonitorComparisonV1,
        tuple[contracts.EvidenceVersionV1, ...],
    ]:
        current_all = {item.evidence_id: item for item in snapshot.evidence}
        current = {
            key: item for key, item in current_all.items() if not item.tombstoned
        }
        prior_items = {} if prior is None else {
            item.evidence_id: item for item in prior.evidence
        }
        if prior is None:
            status = contracts.ComparisonStatus.BASELINE_ONLY
            changes: list[contracts.EvidenceChangeV1] = []
        else:
            status = (
                contracts.ComparisonStatus.COMPLETE
                if snapshot.coverage.status is contracts.CoverageStatus.COMPLETE
                else contracts.ComparisonStatus.INCOMPLETE
            )
            changes = []
            for evidence_id, item in sorted(current.items()):
                previous = prior_items.get(evidence_id)
                kind = (
                    contracts.ChangeKind.NEW
                    if previous is None
                    else contracts.ChangeKind.UNCHANGED
                    if previous.version_id == item.version_id
                    else contracts.ChangeKind.REVISED
                )
                changes.append(
                    contracts.EvidenceChangeV1.from_dict(
                        {
                            "kind": kind.value,
                            "evidence_id": evidence_id,
                            "prior_version_id": (
                                None if previous is None else previous.version_id
                            ),
                            "current_version_id": item.version_id,
                        }
                    )
                )
            if status is contracts.ComparisonStatus.COMPLETE:
                for evidence_id, item in sorted(current_all.items()):
                    previous = prior_items.get(evidence_id)
                    if item.tombstoned and previous is not None:
                        changes.append(
                            contracts.EvidenceChangeV1.from_dict(
                                {
                                    "kind": contracts.ChangeKind.REMOVED.value,
                                    "evidence_id": evidence_id,
                                    "prior_version_id": previous.version_id,
                                    "current_version_id": None,
                                }
                            )
                        )
        candidate = dict(prior_items)
        candidate.update(current)
        if snapshot.coverage.status is contracts.CoverageStatus.COMPLETE:
            for evidence_id, item in current_all.items():
                if item.tombstoned:
                    candidate.pop(evidence_id, None)
        comparison = contracts.MonitorComparisonV1.from_dict(
            {
                "schema_version": contracts.SCHEMA_VERSION,
                "comparator_version": contracts.COMPARATOR_VERSION,
                "status": status.value,
                "prior_baseline_id": None if prior is None else prior.baseline_id,
                "snapshot_id": snapshot.snapshot_id,
                "prior_count": len(prior_items),
                "current_count": len(current),
                "changes": [item.to_dict() for item in changes],
            }
        )
        return comparison, tuple(candidate[key] for key in sorted(candidate))

    def _decide(
        self,
        run_id: str,
        kind: contracts.DecisionKind,
        actor: str,
    ) -> contracts.MonitorDecisionV1:
        run = self.repository.get_run(run_id)
        decision = contracts.MonitorDecisionV1.from_dict(
            {
                "schema_version": contracts.SCHEMA_VERSION,
                "decision_id": _stable_id(
                    "monitor-decision",
                    {"run_id": run.run_id, "decision": kind.value},
                ),
                "monitor_id": run.monitor_id,
                "run_id": run.run_id,
                "baseline_id": run.candidate_baseline_id,
                "decision": kind.value,
                "decided_by": actor,
                "decided_at": self.clock(),
            }
        )
        return self.repository.decide(run, decision)

    def accept(self, run_id: str, *, actor: str) -> contracts.MonitorDecisionV1:
        return self._decide(run_id, contracts.DecisionKind.ACCEPTED, actor)

    def reject(self, run_id: str, *, actor: str) -> contracts.MonitorDecisionV1:
        return self._decide(run_id, contracts.DecisionKind.REJECTED, actor)
