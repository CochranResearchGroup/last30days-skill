"""Provider-free acceptance tests for the saved-monitor kernel."""

from dataclasses import FrozenInstanceError
import json
import sqlite3
from pathlib import Path

import pytest

from lib import service_monitor_contracts as contracts
from lib.service_monitors import (
    FakeSavedQueryViewProvider,
    MonitorErrorCode,
    MonitorKernel,
    MonitorKernelError,
    MonitorRepository,
)


FIXTURE = json.loads(
    (Path(__file__).parent / "fixtures" / "monitor_packet1.json").read_text(
        encoding="utf-8"
    )
)


def _kernel(tmp_path):
    repository = MonitorRepository(tmp_path / "monitor.db")
    repository.initialize()
    provider = FakeSavedQueryViewProvider()
    kernel = MonitorKernel(
        repository,
        provider,
        clock=lambda: "2026-09-13T12:30:00Z",
    )
    return repository, provider, kernel


def _view_ref() -> contracts.SavedQueryViewRefV1:
    return contracts.SavedQueryViewRefV1.from_dict(
        {
            "schema_version": 1,
            "view_kind": "saved_query",
            "saved_query_id": "query-browser-agents",
            "saved_query_version": 3,
        }
    )


def _spec_payload(**overrides):
    payload = {
        "schema_version": 1,
        "monitor_id": "monitor-browser-agents",
        "revision": 1,
        "name": "Browser agent changes",
        "view_ref": _view_ref().to_dict(),
        "access_partition_id": "public",
        "lifecycle_state": "disabled",
        "comparison_policy": "stable_evidence_v1",
        "cadence_seconds": 86400,
        "max_items": 50,
        "retention_days": 90,
        "created_by": "operator",
        "created_at": "2026-09-13T12:00:00Z",
    }
    payload.update(overrides)
    return payload


def test_monitor_spec_round_trips_a_strict_immutable_contract():
    payload = _spec_payload()

    spec = contracts.MonitorSpecV1.from_dict(payload)

    assert spec.to_dict() == payload
    with pytest.raises(FrozenInstanceError):
        spec.name = "rewritten"
    with pytest.raises(contracts.MonitorContractError, match="unknown fields"):
        contracts.MonitorSpecV1.from_dict({**payload, "delivery": "forbidden"})
    with pytest.raises(contracts.MonitorContractError, match="saved_query_version"):
        contracts.SavedQueryViewRefV1.from_dict(
            {**payload["view_ref"], "saved_query_version": 0}
        )


def test_monitor_migration_creates_immutable_durable_tables(tmp_path):
    repository = MonitorRepository(tmp_path / "monitor.db")
    repository.initialize()

    conn = sqlite3.connect(repository.db_path)
    tables = {
        row[0]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        )
    }
    assert {
        "service_monitor_specs",
        "service_monitor_view_snapshots",
        "service_monitor_runs",
        "service_monitor_baselines",
        "service_monitor_decisions",
        "service_monitor_baseline_heads",
    } <= tables
    assert conn.execute("SELECT MAX(version) FROM schema_version").fetchone()[0] == 18
    assert conn.execute(
        "SELECT MAX(version) FROM service_monitor_schema_version"
    ).fetchone()[0] == 1
    conn.close()


def test_first_run_replays_and_only_acceptance_advances_the_baseline(tmp_path):
    repository, provider, kernel = _kernel(tmp_path)
    spec = contracts.MonitorSpecV1.from_dict(FIXTURE["monitor_spec"])
    snapshot = contracts.SavedQueryViewSnapshotV1.from_dict(
        FIXTURE["initial_snapshot"]
    )
    provider.register(snapshot)
    kernel.create(spec)
    kernel.activate(spec.monitor_id, actor="operator")

    first = kernel.evaluate(spec.monitor_id, snapshot.snapshot_id)
    replay = kernel.evaluate(spec.monitor_id, snapshot.snapshot_id)

    assert replay == first
    assert first.comparison.status is contracts.ComparisonStatus.BASELINE_ONLY
    assert repository.current_baseline(spec.monitor_id) is None

    decision = kernel.accept(first.run_id, actor="operator")

    assert decision.decision is contracts.DecisionKind.ACCEPTED
    assert repository.current_baseline(spec.monitor_id).baseline_id == (
        first.candidate_baseline_id
    )
    assert kernel.accept(first.run_id, actor="operator") == decision


def test_comparison_distinguishes_changes_without_treating_top_k_absence_as_removal(
    tmp_path,
):
    repository, provider, kernel = _kernel(tmp_path)
    spec = contracts.MonitorSpecV1.from_dict(FIXTURE["monitor_spec"])
    initial = contracts.SavedQueryViewSnapshotV1.from_dict(
        FIXTURE["initial_snapshot"]
    )
    changed = contracts.SavedQueryViewSnapshotV1.from_dict(
        FIXTURE["changed_snapshot"]
    )
    provider.register(initial)
    provider.register(changed)
    kernel.create(spec)
    kernel.activate(spec.monitor_id, actor="operator")
    initial_run = kernel.evaluate(spec.monitor_id, initial.snapshot_id)
    kernel.accept(initial_run.run_id, actor="operator")

    changed_run = kernel.evaluate(spec.monitor_id, changed.snapshot_id)

    assert changed_run.comparison.status is contracts.ComparisonStatus.COMPLETE
    assert {
        kind: [item.evidence_id for item in changed_run.comparison.by_kind(kind)]
        for kind in contracts.ChangeKind
    } == {
        contracts.ChangeKind.NEW: ["evidence-c"],
        contracts.ChangeKind.REVISED: ["evidence-b"],
        contracts.ChangeKind.UNCHANGED: ["evidence-a"],
        contracts.ChangeKind.REMOVED: ["evidence-removed"],
    }
    candidate = repository.get_baseline(changed_run.candidate_baseline_id)
    assert {item.evidence_id: item.version_id for item in candidate.evidence} == {
        "evidence-a": "version-a1",
        "evidence-b": "version-b2",
        "evidence-c": "version-c1",
        "evidence-gone-from-top-k": "version-g1",
    }


def test_incomplete_or_rejected_runs_never_advance_the_accepted_baseline(tmp_path):
    repository, provider, kernel = _kernel(tmp_path)
    spec = contracts.MonitorSpecV1.from_dict(FIXTURE["monitor_spec"])
    initial = contracts.SavedQueryViewSnapshotV1.from_dict(
        FIXTURE["initial_snapshot"]
    )
    partial_payload = json.loads(json.dumps(FIXTURE["changed_snapshot"]))
    partial_payload["snapshot_id"] = "snapshot-partial"
    partial_payload["coverage"] = {
        "status": "partial",
        "sources": ["reddit", "x"],
        "gaps": ["x:window-incomplete"],
    }
    partial = contracts.SavedQueryViewSnapshotV1.from_dict(partial_payload)
    changed = contracts.SavedQueryViewSnapshotV1.from_dict(
        FIXTURE["changed_snapshot"]
    )
    for snapshot in (initial, partial, changed):
        provider.register(snapshot)
    kernel.create(spec)
    kernel.activate(spec.monitor_id, actor="operator")
    initial_run = kernel.evaluate(spec.monitor_id, initial.snapshot_id)
    kernel.accept(initial_run.run_id, actor="operator")
    accepted_id = initial_run.candidate_baseline_id

    partial_run = kernel.evaluate(spec.monitor_id, partial.snapshot_id)

    assert partial_run.comparison.status is contracts.ComparisonStatus.INCOMPLETE
    assert partial_run.comparison.by_kind(contracts.ChangeKind.REMOVED) == ()
    with pytest.raises(MonitorKernelError) as incomplete:
        kernel.accept(partial_run.run_id, actor="operator")
    assert incomplete.value.code is MonitorErrorCode.COMPARISON_INCOMPLETE
    assert repository.current_baseline(spec.monitor_id).baseline_id == accepted_id

    changed_run = kernel.evaluate(spec.monitor_id, changed.snapshot_id)
    rejected = kernel.reject(changed_run.run_id, actor="operator")
    assert rejected.decision is contracts.DecisionKind.REJECTED
    assert repository.current_baseline(spec.monitor_id).baseline_id == accepted_id
    with pytest.raises(MonitorKernelError) as conflict:
        kernel.accept(changed_run.run_id, actor="operator")
    assert conflict.value.code is MonitorErrorCode.DECISION_CONFLICT


def test_pause_resume_archive_and_partition_fail_closed_with_distinct_errors(
    tmp_path,
):
    repository, provider, kernel = _kernel(tmp_path)
    spec = contracts.MonitorSpecV1.from_dict(FIXTURE["monitor_spec"])
    initial = contracts.SavedQueryViewSnapshotV1.from_dict(
        FIXTURE["initial_snapshot"]
    )
    provider.register(initial)
    kernel.create(spec)
    kernel.activate(spec.monitor_id, actor="operator")

    paused = kernel.pause(spec.monitor_id, actor="operator")
    assert paused.lifecycle_state is contracts.MonitorLifecycle.PAUSED
    with pytest.raises(MonitorKernelError) as paused_error:
        kernel.evaluate(spec.monitor_id, initial.snapshot_id)
    assert paused_error.value.code is MonitorErrorCode.MONITOR_PAUSED
    assert paused_error.value.contract.to_dict() == {
        "schema_version": 1,
        "code": "monitor_paused",
        "message": "paused monitor cannot run",
        "monitor_id": None,
        "run_id": None,
    }

    resumed = kernel.resume(spec.monitor_id, initial.snapshot_id, actor="operator")
    assert resumed.lifecycle_state is contracts.MonitorLifecycle.ACTIVE
    assert kernel.evaluate(spec.monitor_id, initial.snapshot_id).monitor_revision == 4

    archived = kernel.archive(spec.monitor_id, actor="operator")
    assert archived.lifecycle_state is contracts.MonitorLifecycle.ARCHIVED
    with pytest.raises(MonitorKernelError) as archived_error:
        kernel.evaluate(spec.monitor_id, initial.snapshot_id)
    assert archived_error.value.code is MonitorErrorCode.MONITOR_ARCHIVED

    partition_payload = json.loads(json.dumps(FIXTURE["initial_snapshot"]))
    partition_payload["snapshot_id"] = "snapshot-private"
    partition_payload["access_partition_id"] = "profile:private"
    private = contracts.SavedQueryViewSnapshotV1.from_dict(partition_payload)
    provider.register(private)
    with pytest.raises(MonitorKernelError) as partition_error:
        provider.read(spec.view_ref, "public", private.snapshot_id)
    assert partition_error.value.code is MonitorErrorCode.PARTITION_MISMATCH

    with pytest.raises(MonitorKernelError) as terminal_error:
        kernel.resume(spec.monitor_id, initial.snapshot_id, actor="operator")
    assert terminal_error.value.code is MonitorErrorCode.INVALID_LIFECYCLE


def test_monitor_spec_rows_and_view_identity_are_immutable(tmp_path):
    repository, _, kernel = _kernel(tmp_path)
    spec = contracts.MonitorSpecV1.from_dict(FIXTURE["monitor_spec"])
    kernel.create(spec)

    conn = sqlite3.connect(repository.db_path)
    with pytest.raises(sqlite3.IntegrityError, match="monitor spec is immutable"):
        conn.execute(
            "UPDATE service_monitor_specs SET lifecycle_state = 'active' "
            "WHERE monitor_id = ? AND revision = 1",
            (spec.monitor_id,),
        )
    conn.close()

    changed_ref = contracts.SavedQueryViewRefV1.from_dict(
        {
            **spec.view_ref.to_dict(),
            "saved_query_version": spec.view_ref.saved_query_version + 1,
        }
    )
    invalid_revision = contracts.MonitorSpecV1.from_dict(
        {
            **spec.to_dict(),
            "revision": 2,
            "view_ref": changed_ref.to_dict(),
            "lifecycle_state": "active",
            "created_at": "2026-09-13T12:30:00Z",
        }
    )
    with pytest.raises(MonitorKernelError) as changed_view:
        repository.put_spec(invalid_revision)
    assert changed_view.value.code is MonitorErrorCode.INVALID_REVISION


def test_acceptance_rejects_a_run_prepared_from_a_stale_baseline(tmp_path):
    repository, provider, kernel = _kernel(tmp_path)
    spec = contracts.MonitorSpecV1.from_dict(FIXTURE["monitor_spec"])
    initial = contracts.SavedQueryViewSnapshotV1.from_dict(
        FIXTURE["initial_snapshot"]
    )
    changed = contracts.SavedQueryViewSnapshotV1.from_dict(
        FIXTURE["changed_snapshot"]
    )
    competing_payload = json.loads(json.dumps(FIXTURE["changed_snapshot"]))
    competing_payload["snapshot_id"] = "snapshot-competing"
    competing_payload["evidence_head_id"] = "search-head-003"
    competing_payload["knowledge_cutoff"] = "2026-09-13T13:00:00Z"
    competing_payload["coverage_end"] = "2026-09-13T12:59:59Z"
    competing_payload["evidence"].append(
        {
            "evidence_id": "evidence-d",
            "version_id": "version-d1",
            "tombstoned": False,
        }
    )
    competing = contracts.SavedQueryViewSnapshotV1.from_dict(competing_payload)
    for snapshot in (initial, changed, competing):
        provider.register(snapshot)
    kernel.create(spec)
    kernel.activate(spec.monitor_id, actor="operator")
    first = kernel.evaluate(spec.monitor_id, initial.snapshot_id)
    kernel.accept(first.run_id, actor="operator")

    left = kernel.evaluate(spec.monitor_id, changed.snapshot_id)
    right = kernel.evaluate(spec.monitor_id, competing.snapshot_id)
    kernel.accept(left.run_id, actor="operator")

    with pytest.raises(MonitorKernelError) as stale:
        kernel.accept(right.run_id, actor="operator")
    assert stale.value.code is MonitorErrorCode.STALE_BASELINE
    assert repository.current_baseline(spec.monitor_id).baseline_id == (
        left.candidate_baseline_id
    )
