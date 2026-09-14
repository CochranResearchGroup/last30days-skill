"""Provider-free behavior through the monitor product command interface."""

import sqlite3
import threading
from datetime import UTC, datetime

import pytest
from lib import service_monitor_contracts as contracts
from lib.service_monitor_application import MonitorApplication
from lib.service_client import ServiceClient, ServiceClientError
from lib.service_http import UnixServiceServer
from lib.service_monitors import MonitorKernelError
from lib.service_post_search import PostSearchBackend

from tests.test_service_collection import _coordinator, _follow_spec
from tests.test_service_post_search import _seed_post_corpus


def composition(tmp_path):
    db, _, _, _, collections = _coordinator(tmp_path)
    _seed_post_corpus(db)
    spec = collections.put_spec(_follow_spec())
    with sqlite3.connect(db) as conn:
        conn.row_factory = sqlite3.Row
        row = dict(
            conn.execute(
                "SELECT * FROM document_versions WHERE version_id='version-legacy-current'"
            ).fetchone()
        )
        row.update(
            version_id="follow-version-1",
            content_hash="sha256:follow-version-1",
            access_partition_id="profile:x-primary",
        )
        conn.execute(
            f"INSERT INTO document_versions ({','.join(row)}) VALUES ({','.join('?' for _ in row)})",
            tuple(row.values()),
        )
        conn.execute(
            "UPDATE documents SET source='x', access_partition_id='profile:x-primary'"
        )
        conn.execute("UPDATE documents SET current_version_id='follow-version-1'")
        conn.execute(
            """INSERT INTO document_version_sightings
            (version_id, acquisition_id, collection_spec_id, collection_run_id,
             observed_at, access_partition_id)
            VALUES ('follow-version-1', 'follow-fixture', ?, 'fixture-run',
                    '2026-09-05T12:01:00Z', 'profile:x-primary')""",
            (spec.collection_spec_id,),
        )
    backend = PostSearchBackend(db, clock=lambda: datetime(2026, 9, 14, tzinfo=UTC))
    app = MonitorApplication(
        db,
        backend,
        collection_reader=collections,
        access_partitions=lambda profile: ("public", "profile:" + profile),
        clock=lambda: "2026-09-14T00:00:00Z",
    )
    ref = {
        "schema_version": 1,
        "view_kind": "follow",
        "collection_spec_id": spec.collection_spec_id,
        "spec_version": 1,
    }
    return app, collections, ref


def command(app, action, **fields):
    return app.command(
        {"profile_id": "x-primary", "command": {"action": action, **fields}}
    )


def create(app, ref):
    return command(
        app,
        "create",
        monitor_id="monitor-fixture",
        name="Fixture follow",
        view_ref=ref,
        cadence_seconds=3600,
        max_items=20,
        retention_days=30,
    )


def test_real_follow_to_frozen_digest_is_explicit_and_restart_safe(tmp_path):
    app, collections, ref = composition(tmp_path)
    created = create(app, ref)
    assert created["lifecycle_state"] == "disabled"
    command(app, "activate", monitor_id=created["monitor_id"])
    captured = command(
        app, "capture", monitor_id=created["monitor_id"], capture_id="first"
    )
    assert captured["view_ref"] == ref
    assert len(captured["evidence"]) == 1
    result = command(
        app,
        "evaluate",
        monitor_id=created["monitor_id"],
        snapshot_id=captured["snapshot_id"],
    )
    digest = result["digest"]
    assert digest["comparison_status"] == "baseline_only"
    assert digest["current_count"] == 1
    assert command(app, "baseline", monitor_id=created["monitor_id"]) == {
        "baseline": None
    }
    command(app, "accept", run_id=result["run"]["run_id"])
    second = command(
        app, "capture", monitor_id=created["monitor_id"], capture_id="second"
    )
    result2 = command(
        app,
        "evaluate",
        monitor_id=created["monitor_id"],
        snapshot_id=second["snapshot_id"],
    )
    assert result2["digest"]["counts"]["unchanged"] == 1
    assert (
        result2["digest"]["entries"][0]["evidence_refs"][0]["version_id"]
        == "follow-version-1"
    )
    reopened = MonitorApplication(
        app.db_path,
        app.search_backend,
        collection_reader=collections,
        access_partitions=app.access_partitions,
    )
    assert (
        command(reopened, "digest", run_id=result2["run"]["run_id"])
        == result2["digest"]
    )
    assert (
        command(
            reopened, "capture", monitor_id=created["monitor_id"], capture_id="second"
        )
        == second
    )


def test_monitor_lifecycle_is_explicit_scoped_and_source_archive_pauses(tmp_path):
    app, collections, ref = composition(tmp_path)
    create(app, ref)
    assert (
        command(app, "list", limit=10, after=None)["monitors"][0]["monitor_id"]
        == "monitor-fixture"
    )
    revised = command(
        app,
        "revise",
        monitor_id="monitor-fixture",
        expected_revision=1,
        name="Renamed",
        cadence_seconds=7200,
        max_items=10,
        retention_days=15,
    )
    assert revised["revision"] == 2
    for action in ("get", "capture", "archive"):
        fields = {"monitor_id": "monitor-fixture"}
        if action == "capture":
            fields["capture_id"] = "denied"
        errors = []
        for monitor_id in ("monitor-fixture", "absent"):
            with pytest.raises(MonitorKernelError) as denied:
                app.command(
                    {
                        "profile_id": "other",
                        "command": {
                            "action": action,
                            **fields,
                            "monitor_id": monitor_id,
                        },
                    }
                )
            errors.append((denied.value.code, str(denied.value)))
        assert errors[0] == errors[1]
    command(app, "activate", monitor_id="monitor-fixture")
    snapshot = command(
        app, "capture", monitor_id="monitor-fixture", capture_id="before-archive"
    )
    result = command(
        app,
        "evaluate",
        monitor_id="monitor-fixture",
        snapshot_id=snapshot["snapshot_id"],
    )
    command(app, "reject", run_id=result["run"]["run_id"])
    assert command(app, "baseline", monitor_id="monitor-fixture") == {"baseline": None}
    collections.archive_spec(ref["collection_spec_id"])
    with pytest.raises(MonitorKernelError):
        command(
            app, "capture", monitor_id="monitor-fixture", capture_id="after-archive"
        )
    assert (
        command(app, "get", monitor_id="monitor-fixture")["lifecycle_state"] == "paused"
    )
    assert command(app, "digest", run_id=result["run"]["run_id"]) == result["digest"]
    assert (
        command(app, "history", monitor_id="monitor-fixture", limit=10, after=None)[
            "runs"
        ][0]
        == result["run"]
    )
    command(app, "archive", monitor_id="monitor-fixture")
    with pytest.raises(MonitorKernelError):
        command(app, "activate", monitor_id="monitor-fixture")


def test_monitor_names_are_partition_scoped_not_global_existence_oracles(tmp_path):
    app, _, _ = composition(tmp_path)
    snapshots = {}
    for profile in ("x-primary", "other"):
        query = contracts.SavedQueryDefinitionV1.from_dict(
            {
                "schema_version": 1,
                "saved_query_id": "query-" + profile,
                "version": 1,
                "access_partition_id": "profile:" + profile,
                "search": {
                    "profile_id": profile,
                    "query": None,
                    "filters": {"sources": ["x"]},
                    "page_size": 20,
                    "sort": "observed_desc",
                    "revision_mode": "current",
                },
            }
        )
        app.repository.save(query)
        result = app.command(
            {
                "profile_id": profile,
                "command": {
                    "action": "create",
                    "monitor_id": "same-name",
                    "name": profile,
                    "view_ref": query.view_ref.to_dict(),
                    "cadence_seconds": 3600,
                    "max_items": 20,
                    "retention_days": 30,
                },
            }
        )
        assert result["monitor_id"] == "same-name"
        assert result["name"] == profile
        app.command(
            {
                "profile_id": profile,
                "command": {"action": "activate", "monitor_id": "same-name"},
            }
        )
        snapshots[profile] = app.command(
            {
                "profile_id": profile,
                "command": {
                    "action": "capture",
                    "monitor_id": "same-name",
                    "capture_id": "partition-probe",
                },
            }
        )["snapshot_id"]

    for action in ("evaluate", "resume"):
        if action == "resume":
            app.command(
                {
                    "profile_id": "other",
                    "command": {"action": "pause", "monitor_id": "same-name"},
                }
            )
        observed = []
        for snapshot_id in (snapshots["x-primary"], "absent-snapshot"):
            with pytest.raises(MonitorKernelError) as denied:
                app.command(
                    {
                        "profile_id": "other",
                        "command": {
                            "action": action,
                            "monitor_id": "same-name",
                            "snapshot_id": snapshot_id,
                        },
                    }
                )
            observed.append((denied.value.code, str(denied.value)))
        assert observed[0] == observed[1]
        assert observed[0][0] is contracts.MonitorErrorCode.VIEW_UNAVAILABLE
        if action == "evaluate":
            socket_path = tmp_path / "runtime" / "service.sock"

            class MonitorTransport:
                @staticmethod
                def monitor(payload):
                    return app.command(payload)

            server = UnixServiceServer(socket_path, MonitorTransport())
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                client = ServiceClient(socket_path)
                public_errors = []
                for snapshot_id in (snapshots["x-primary"], "absent-snapshot"):
                    with pytest.raises(ServiceClientError) as denied:
                        client.monitor(
                            {
                                "action": "evaluate",
                                "monitor_id": "same-name",
                                "snapshot_id": snapshot_id,
                            },
                            profile_id="other",
                        )
                    public_errors.append(str(denied.value))
                assert public_errors[0] == public_errors[1]
                assert public_errors[0].startswith("view_unavailable:")
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=2)
