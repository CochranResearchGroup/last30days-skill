"""Follow capture provenance, immutable history and safe bounded migration."""

import sqlite3

import pytest
import store
from lib import service_monitor_contracts as c
from lib.service_monitors import (
    MONITOR_SCHEMA_V1,
    MonitorKernelError,
    MonitorRepository,
)

from tests.test_service_monitor_application import command, composition, create
from tests.test_service_monitors import _spec_payload


def test_v1_monitor_payload_bytes_survive_follow_schema_upgrade(tmp_path):
    db = tmp_path / "legacy.db"
    store.init_db(db)
    with sqlite3.connect(db) as conn:
        conn.executescript(MONITOR_SCHEMA_V1)
    repository = MonitorRepository(db)
    repository.put_spec(c.MonitorSpecV1.from_dict(_spec_payload()))
    with sqlite3.connect(db) as conn:
        before = conn.execute(
            "SELECT payload_json, payload_sha256 FROM service_monitor_specs"
        ).fetchall()
    repository.initialize()
    repository.initialize()
    with sqlite3.connect(db) as conn:
        assert (
            conn.execute(
                "SELECT payload_json, payload_sha256 FROM service_monitor_specs"
            ).fetchall()
            == before
        )
        assert (
            conn.execute("PRAGMA foreign_key_check(service_monitor_specs)").fetchall()
            == []
        )
    assert (
        repository.current_spec("monitor-browser-agents").to_dict() == _spec_payload()
    )


def test_follow_capture_keeps_multiple_authorized_causes_without_duplicate_evidence(
    tmp_path,
):
    app, _, ref = composition(tmp_path)
    create(app, ref)
    command(app, "activate", monitor_id="monitor-fixture")
    with sqlite3.connect(app.db_path) as conn:
        conn.execute("""INSERT INTO document_version_sightings
            SELECT version_id, 'second-cause', topic_id, 'other-follow',
                   'second-run', observed_at, access_partition_id
            FROM document_version_sightings WHERE version_id='follow-version-1'""")
    snapshot = command(
        app, "capture", monitor_id="monitor-fixture", capture_id="multi-cause"
    )
    receipt = app.repository.capture_receipt(snapshot["snapshot_id"])
    assert len(snapshot["evidence"]) == 1
    assert set(receipt["evidence_refs"][0]["collection_refs"]) >= {
        "legacy:spec:other-follow",
        "legacy:spec:" + ref["collection_spec_id"],
    }
    app.follows.max_items = 0  # invalid host configuration is not a public command
    with pytest.raises(MonitorKernelError):
        command(app, "capture", monitor_id="monitor-fixture", capture_id="multi-cause")
