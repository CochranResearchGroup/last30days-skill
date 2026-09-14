"""Provider-free monitor probe evidence-integrity tests."""

import importlib.util
import sqlite3
import sys
from pathlib import Path

import pytest


def probe():
    path = (
        Path(__file__).resolve().parents[1]
        / "dev/last30days/scripts/monitor_dogfood.py"
    )
    spec = importlib.util.spec_from_file_location("monitor_dogfood", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_monitor_probe_excludes_only_declared_monitor_writes(tmp_path):
    module = probe()
    db = tmp_path / "fixture.db"
    with sqlite3.connect(db) as conn:
        conn.execute("CREATE TABLE documents (content TEXT)")
        conn.execute("CREATE TABLE service_monitor_records (payload TEXT)")
    baseline = module.non_monitor_digest(db)
    with sqlite3.connect(db) as conn:
        conn.execute("INSERT INTO service_monitor_records VALUES ('expected')")
    assert module.non_monitor_digest(db) == baseline
    with sqlite3.connect(db) as conn:
        conn.execute("INSERT INTO documents VALUES ('unexpected')")
    assert module.non_monitor_digest(db) != baseline


def test_monitor_probe_does_not_hide_undeclared_prefixed_tables(tmp_path):
    module = probe()
    db = tmp_path / "fixture.db"
    with sqlite3.connect(db) as conn:
        conn.execute("CREATE TABLE documents (content TEXT)")
    baseline = module.non_monitor_digest(db)
    with sqlite3.connect(db) as conn:
        conn.execute("CREATE TABLE service_monitor_undeclared (content TEXT)")
    assert module.non_monitor_digest(db) != baseline


def test_monitor_probe_requires_exact_digest_parity():
    with pytest.raises(AssertionError, match="parity"):
        probe().assert_parity({"digest_id": "before"}, {"digest_id": "forged"})


def test_monitor_probe_fixture_is_cache_only_and_follow_identity_is_exact(tmp_path):
    module = probe()
    db = tmp_path / "fixture.db"
    ref = module.seed_monitors(db)
    assert ref == {
        "schema_version": 1,
        "view_kind": "follow",
        "collection_spec_id": "follow-x-account-alice",
        "spec_version": 1,
    }
    with sqlite3.connect(db) as conn:
        assert conn.execute(
            "SELECT enabled FROM collection_specs WHERE collection_spec_id=?",
            (ref["collection_spec_id"],),
        ).fetchone() == (0,)
        assert conn.execute("SELECT count(*) FROM collection_runs").fetchone() == (0,)


def test_monitor_probe_crosses_real_http_and_fresh_mcp(tmp_path):
    import shutil
    import threading

    from lib.service_app import initialize_application
    from lib.service_client import ServiceClient
    from lib.service_http import UnixServiceServer
    from lib.service_runtime import build_collection_read_authority

    if not hasattr(ServiceClient, "monitor"):
        pytest.skip("coordinator monitor transport join pending")
    if shutil.which("go") is None:
        pytest.skip("Go toolchain unavailable")
    module = probe()
    db = tmp_path / "fixture.db"
    ref = module.seed_monitors(db)
    app = initialize_application(
        db,
        retriever=object(),
        effect_mode="cache_only",
        collection_coordinator=build_collection_read_authority(db),
    )
    server = UnixServiceServer(tmp_path / "s", app)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        binary = module.build_mcp(tmp_path / "mcp")
        with module.FreshMCP(binary, server.socket_path, tmp_path / "mcp-home") as mcp:
            receipt, anchor = module.check_monitors(
                ServiceClient(server.socket_path), mcp, db, ref
            )
            assert receipt["state"] == "passed"
            assert anchor["digest"]["counts"]["unchanged"] == 1
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
