"""Frozen evidence history, byte bounds and acceptance safety."""

import sqlite3

import pytest
from lib import service_monitor_contracts as c
from lib.service_monitors import MonitorKernelError

from tests.test_service_monitor_application import command, composition, create


def evaluate(app, capture_id):
    snapshot = command(
        app, "capture", monitor_id="monitor-fixture", capture_id=capture_id
    )
    return command(
        app,
        "evaluate",
        monitor_id="monitor-fixture",
        snapshot_id=snapshot["snapshot_id"],
    )


def test_digest_retains_prior_evidence_across_absent_views_and_later_revision(tmp_path):
    app, _, ref = composition(tmp_path)
    create(app, ref)
    command(app, "activate", monitor_id="monitor-fixture")
    first = evaluate(app, "first")
    command(app, "accept", run_id=first["run"]["run_id"])
    with sqlite3.connect(app.db_path) as conn:
        conn.execute(
            "UPDATE documents SET current_version_id=NULL WHERE document_id='doc-legacy'"
        )
    absent = evaluate(app, "absent")
    assert absent["digest"]["counts"]["removed"] == 0
    command(app, "accept", run_id=absent["run"]["run_id"])
    with sqlite3.connect(app.db_path) as conn:
        conn.row_factory = sqlite3.Row
        row = dict(
            conn.execute(
                "SELECT * FROM document_versions WHERE version_id='follow-version-1'"
            ).fetchone()
        )
        row.update(
            version_id="follow-version-2",
            content_hash="sha256:follow-version-2",
            normalized_text="revised browser evidence",
        )
        conn.execute(
            f"INSERT INTO document_versions ({','.join(row)}) VALUES ({','.join('?' for _ in row)})",
            tuple(row.values()),
        )
        conn.execute(
            "UPDATE documents SET current_version_id='follow-version-2' WHERE document_id='doc-legacy'"
        )
        conn.execute("""INSERT INTO document_version_sightings
            SELECT 'follow-version-2', 'second-acquisition', topic_id, collection_spec_id,
                   collection_run_id, observed_at, access_partition_id
            FROM document_version_sightings WHERE version_id='follow-version-1'""")
    revised = evaluate(app, "revised")
    assert revised["digest"]["counts"]["revised"] == 1
    assert {
        ref["version_id"] for ref in revised["digest"]["entries"][0]["evidence_refs"]
    } == {"follow-version-1", "follow-version-2"}


def test_explicit_frozen_tombstone_digest_cites_prior_evidence_not_absence(tmp_path):
    app, _, ref = composition(tmp_path)
    create(app, ref)
    command(app, "activate", monitor_id="monitor-fixture")
    first = evaluate(app, "baseline")
    command(app, "accept", run_id=first["run"]["run_id"])
    original = app.repository.capture_receipt(first["run"]["snapshot_id"])
    snapshot = {
        **original["snapshot"],
        "snapshot_id": "explicit-fixture-tombstone",
        "evidence": [{**original["snapshot"]["evidence"][0], "tombstoned": True}],
    }
    # Explicit synthetic storage fact, not a provider-empty response or search absence.
    app.repository.begin_capture(snapshot["snapshot_id"], "explicit-fixture-tombstone")
    app.repository.put_snapshot(c.SavedQueryViewSnapshotV1.from_dict(snapshot))
    app.repository.finish_capture(
        snapshot["snapshot_id"],
        receipt={**original, "snapshot": snapshot, "evidence_refs": []},
    )
    removed = command(
        app,
        "evaluate",
        monitor_id="monitor-fixture",
        snapshot_id=snapshot["snapshot_id"],
    )
    assert removed["digest"]["counts"]["removed"] == 1
    assert (
        removed["digest"]["entries"][0]["evidence_refs"][0]["version_id"]
        == "follow-version-1"
    )
    assert removed["digest"]["entries"][0]["current_version_id"] is None


def test_partial_capture_and_failed_renderer_cannot_advance_baseline(
    tmp_path, monkeypatch
):
    app, _, ref = composition(tmp_path)
    create(app, ref)
    command(app, "activate", monitor_id="monitor-fixture")
    app.follows.max_bytes = 1
    partial = evaluate(app, "partial")
    assert partial["digest"]["coverage"]["status"] == "partial"
    with pytest.raises(MonitorKernelError):
        command(app, "accept", run_id=partial["run"]["run_id"])
    app.follows.max_bytes = 32768
    snap = command(
        app, "capture", monitor_id="monitor-fixture", capture_id="render-failure"
    )
    import lib.service_monitor_application as module

    def failed(*args, **kwargs):
        raise MonitorKernelError(
            c.MonitorErrorCode.VIEW_UNAVAILABLE, "fixture renderer failure"
        )

    monkeypatch.setattr(module, "prepare_digest", failed)
    with pytest.raises(MonitorKernelError):
        command(
            app,
            "evaluate",
            monitor_id="monitor-fixture",
            snapshot_id=snap["snapshot_id"],
        )
    assert command(app, "baseline", monitor_id="monitor-fixture") == {"baseline": None}


def test_digest_uses_the_immutable_spec_revision_selected_by_the_run(
    tmp_path, monkeypatch
):
    app, _, ref = composition(tmp_path)
    create(app, ref)
    command(app, "activate", monitor_id="monitor-fixture")
    snapshot = command(
        app, "capture", monitor_id="monitor-fixture", capture_id="revision-race"
    )
    original_evaluate = app.kernel.evaluate

    def interleaved_evaluate(monitor_id, snapshot_id):
        command(
            app,
            "revise",
            monitor_id="monitor-fixture",
            expected_revision=2,
            name="Race-safe",
            cadence_seconds=3600,
            max_items=1,
            retention_days=30,
        )
        return original_evaluate(monitor_id, snapshot_id)

    def assert_frozen_spec(repository, records, run, spec):
        del repository, records
        assert spec.revision == run.monitor_revision == 3
        assert spec.max_items == 1
        return {"frozen_revision": spec.revision}

    monkeypatch.setattr(app.kernel, "evaluate", interleaved_evaluate)
    import lib.service_monitor_application as module

    monkeypatch.setattr(module, "prepare_digest", assert_frozen_spec)
    result = command(
        app,
        "evaluate",
        monitor_id="monitor-fixture",
        snapshot_id=snapshot["snapshot_id"],
    )
    assert result["digest"] == {"frozen_revision": 3}
