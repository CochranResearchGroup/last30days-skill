"""Acceptance-harness checks for synthetic cross-service follow evidence."""

import importlib.util
import shutil
import sqlite3
import subprocess
import sys
import threading
from pathlib import Path
from types import SimpleNamespace

import pytest
from lib.service_app import initialize_application
from lib.service_client import ServiceClient
from lib.service_http import UnixServiceServer
from lib.service_retrieval import HybridRetriever


def _probe():
    path = (
        Path(__file__).resolve().parents[1] / "dev/last30days/scripts/follow_dogfood.py"
    )
    spec = importlib.util.spec_from_file_location("follow_dogfood", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_synthetic_follow_preparation_retains_native_overlap_and_history(tmp_path):
    probe = _probe()
    receipt = probe.seed_fixture(tmp_path / "research.db")
    assert receipt["versions"] == 3  # Reddit, YouTube, private Reddit decoy.
    assert receipt["sightings"] == 6
    assert receipt["fixture_route_calls"] == 4
    assert receipt["external_requests"] == 0
    assert receipt["replay_work"] is None
    assert receipt["x_history_unchanged"] is True
    assert receipt["frozen_revision"] == 1


def test_stock_cache_only_application_reads_seeded_follows(tmp_path):
    probe = _probe()
    db = tmp_path / "research.db"
    probe.seed_fixture(db)
    from tests.test_service_process import _wait_ready

    socket = tmp_path / "s"
    process = subprocess.Popen(
        [
            sys.executable,
            str(probe.ROOT / "skills/last30days/scripts/service.py"),
            "serve",
            "--effect-mode",
            "cache_only",
            "--socket",
            str(socket),
            "--db",
            str(db),
        ],
        env={"HOME": str(tmp_path), "PATH": "/usr/bin:/bin"},
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        client = ServiceClient(socket)
        _wait_ready(client, process)
        result = client.intelligence(
            {
                "action": "collection",
                "operation": "list",
                "profile_id": "follow-owner",
                "include_archived": True,
            }
        )
        assert len(result["collections"]) == 7
    finally:
        process.terminate()
        process.communicate(timeout=8)


def test_probe_rejects_mutation_and_forged_history(tmp_path):
    probe = _probe()
    db = tmp_path / "research.db"
    with sqlite3.connect(db) as conn:
        conn.execute("CREATE TABLE service_jobs (state TEXT)")
    with (
        pytest.raises(AssertionError, match="mutated"),
        probe.unchanged(db),
        sqlite3.connect(db) as conn,
    ):
        conn.execute("INSERT INTO service_jobs VALUES ('queued')")
    with pytest.raises(AssertionError, match="parity"):
        probe.assert_follow_parity(
            {"history": [{"follow_target_id": "accepted"}]},
            {"history": [{"follow_target_id": "forged"}]},
        )


@pytest.mark.skipif(shutil.which("go") is None, reason="Go toolchain unavailable")
def test_probe_crosses_real_http_and_fresh_mcp(tmp_path):
    probe = _probe()
    db = tmp_path / "research.db"
    seed = probe.seed_fixture(db)
    # The composition join is coordinator-owned; this fixture supplies the
    # existing reader while testing actual transports and the denial interface.
    from tests.test_service_collection import _coordinator

    retriever = HybridRetriever(db)
    *_, coordinator = _coordinator(tmp_path)
    app = initialize_application(
        db, retriever, effect_mode="cache_only", collection_coordinator=coordinator
    )
    server = UnixServiceServer(tmp_path / "s", app)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        binary = probe.build_mcp(tmp_path / "mcp")
        with probe.FreshMCP(binary, server.socket_path, tmp_path / "mcp-home") as mcp:
            result = probe.check_follows(
                ServiceClient(server.socket_path), mcp, db, seed
            )
            assert result["authorized_collections"] == 7
            assert result["denied_operations"] == 6
            assert result["search_cases"] == 8
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_probe_refuses_existing_fixture_and_mismatched_artifact(tmp_path):
    probe = _probe()
    db = tmp_path / "research.db"
    probe.seed_fixture(db)
    before = probe.database_digest(db)
    with pytest.raises(ValueError, match="not_empty"):
        probe.seed_fixture(db)
    assert probe.database_digest(db) == before
    manifest = {"files": [{"source": "service/VERSION", "sha256": "0" * 64}]}
    with pytest.raises(AssertionError, match="source.*mismatch"):
        probe.verify_source_manifest(manifest)


def test_runtime_probe_rejects_reused_identity_before_start(tmp_path, monkeypatch):
    probe = _probe()
    import lane_runtime

    monkeypatch.setattr(
        lane_runtime,
        "_expected_descriptor",
        lambda args: SimpleNamespace(state_root=str(tmp_path)),
    )
    with pytest.raises(ValueError, match="fresh_runtime_root_required"):
        probe.run(SimpleNamespace(worktree=probe.ROOT))


def test_synthetic_preparation_denies_network_and_process_effects():
    probe = _probe()
    import socket

    with (
        pytest.raises(AssertionError, match="fixture external effect"),
        probe.fixture_effect_guard(),
    ):
        socket.getaddrinfo("fixture.invalid", 443)
    with (
        pytest.raises(AssertionError, match="fixture external effect"),
        probe.fixture_effect_guard(),
    ):
        subprocess.Popen([sys.executable, "-c", "pass"])


def test_cli_readback_preserves_entire_synthetic_database(tmp_path):
    probe = _probe()
    db = tmp_path / "research.db"
    seed = probe.seed_fixture(db)
    descriptor = SimpleNamespace(
        state_root=str(tmp_path),
        config_dir=str(tmp_path / "config"),
        data_dir=str(tmp_path),
        database_path=str(db),
        socket_path=str(tmp_path / "s"),
        runtime_id="test-follow",
        effect_mode="cache_only",
        credential_policy="deny",
        schedule_policy="deny",
        browser_policy="deny",
    )
    result = probe.check_cli(
        probe.ROOT / "skills/last30days/scripts/service.py", descriptor, seed
    )
    assert result["read_count"] == 6
    assert result["profile_authorization_claimed"] is False
