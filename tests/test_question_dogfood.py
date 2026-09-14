"""Provider-free evidence-integrity checks for the public question probe."""

import importlib.util
import shutil
import sqlite3
import sys
import threading
from pathlib import Path

import pytest
from lib.service_app import initialize_application
from lib.service_client import ServiceClient
from lib.service_http import UnixServiceServer


def _probe():
    path = (
        Path(__file__).resolve().parents[1]
        / "dev/last30days/scripts/question_dogfood.py"
    )
    spec = importlib.util.spec_from_file_location("question_dogfood", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_probe_requires_exact_immutable_answer_parity():
    probe = _probe()
    with pytest.raises(AssertionError, match="parity"):
        probe.assert_question_parity(
            {"answer": {"output_digest": "original"}},
            {"answer": {"output_digest": "forged"}},
        )


def test_probe_distinguishes_expected_question_writes_from_corpus_mutation(tmp_path):
    probe = _probe()
    db = tmp_path / "fixture.db"
    with sqlite3.connect(db) as conn:
        conn.execute("CREATE TABLE documents (content TEXT)")
        conn.execute("CREATE TABLE service_question_tasks (state TEXT)")
    baseline = probe.non_question_digest(db)
    with sqlite3.connect(db) as conn:
        conn.execute("INSERT INTO service_question_tasks VALUES ('pending')")
    assert probe.non_question_digest(db) == baseline
    with sqlite3.connect(db) as conn:
        conn.execute("INSERT INTO documents VALUES ('unexpected')")
    assert probe.non_question_digest(db) != baseline


@pytest.mark.skipif(
    not hasattr(ServiceClient, "ask_question"),
    reason="coordinator question transport join pending",
)
@pytest.mark.skipif(shutil.which("go") is None, reason="Go toolchain unavailable")
def test_probe_crosses_http_and_fresh_mcp(tmp_path):
    probe = _probe()
    db = tmp_path / "questions.db"
    probe.seed_fixture(db)
    app = initialize_application(db, retriever=object(), effect_mode="cache_only")
    server = UnixServiceServer(tmp_path / "s", app)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        binary = probe.build_mcp(tmp_path / "mcp")
        with probe.FreshMCP(binary, server.socket_path, tmp_path / "mcp-home") as mcp:
            receipt, anchor = probe.check_questions(
                ServiceClient(server.socket_path), mcp, db
            )
            assert receipt["state"] == "passed"
            assert receipt["case_count"] == 6
            assert anchor["status"]["state"] == "answered"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
