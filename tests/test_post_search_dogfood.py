"""The closeout probe verifies public behavior and detects false parity."""

import copy
import importlib.util
import shutil
import sys
import threading
from pathlib import Path
from types import SimpleNamespace

import pytest
from lib.service_app import initialize_application
from lib.service_client import ServiceClient
from lib.service_http import UnixServiceServer

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "dev/last30days/scripts/post_search_dogfood.py"


def _probe():
    spec = importlib.util.spec_from_file_location("post_search_dogfood", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.mark.skipif(shutil.which("go") is None, reason="Go toolchain unavailable")
def test_probe_exercises_real_http_and_fresh_mcp_and_detects_evidence_drift(tmp_path):
    probe = _probe()
    db = tmp_path / "search.db"
    probe.seed_fixture(db)
    app = initialize_application(db, retriever=object(), effect_mode="cache_only")
    server = UnixServiceServer(tmp_path / "socket/s", app)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    binary = probe.build_mcp(tmp_path / "mcp")
    try:
        with probe.FreshMCP(binary, server.socket_path, tmp_path / "mcp-home") as mcp:
            report, replay = probe.check_search(
                ServiceClient(server.socket_path), mcp, db
            )
            assert report["state"] == "passed"
            assert report["case_count"] >= 15
            assert report["read_only"] is True
            assert report["publication_pinned"] is True
            assert replay["cursor"]
            request = probe.service_request({"query": "browser"})
            payload = ServiceClient(server.socket_path)._request(
                "POST", "/v1/posts/search", request
            )
            changed = copy.deepcopy(payload)
            changed["hits"][0]["evidence_ref"]["content_hash"] = "sha256:forged"
            with pytest.raises(AssertionError, match="parity"):
                probe.assert_parity(payload, changed)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_fixture_seed_refuses_existing_corpus(tmp_path):
    probe = _probe()
    db = tmp_path / "search.db"
    probe.seed_fixture(db)
    before = db.read_bytes()
    with pytest.raises(ValueError, match="not_empty"):
        probe.seed_fixture(db)
    assert db.read_bytes() == before


def test_runtime_probe_refuses_reusing_existing_state_before_start(
    tmp_path, monkeypatch
):
    probe = _probe()
    monkeypatch.setattr(
        probe.lane_runtime,
        "_expected_descriptor",
        lambda args: SimpleNamespace(state_root=tmp_path),
    )
    monkeypatch.setattr(
        probe.lane_runtime, "up", lambda args: pytest.fail("must not start")
    )
    with pytest.raises(ValueError, match="fresh_runtime_root_required"):
        probe.run(SimpleNamespace(worktree=ROOT))


def test_census_detects_an_owned_process_session(tmp_path):
    probe = _probe()
    process = probe.subprocess.Popen(
        [sys.executable, "-c", "import time; time.sleep(30)"], start_new_session=True
    )
    try:
        assert any(
            row["pid"] == process.pid
            for row in probe.owned_process_census([{"pid": process.pid}])
        )
    finally:
        process.terminate()
        process.wait(timeout=5)
    assert probe.owned_process_census([{"pid": process.pid}]) == []
