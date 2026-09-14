"""Public CLI/HTTP/MCP parity for immutable saved-query composition."""

import json
import os
import shutil
import subprocess
import threading
from pathlib import Path

import pytest

from lib.service_app import initialize_application
from lib.service_client import ServiceClient, ServiceClientError
from lib.service_http import UnixServiceServer
from tests.test_mcp_service_integration import _call
from tests.test_service_post_search import _seed_post_corpus


ROOT = Path(__file__).resolve().parents[1]


def _definition():
    return {
        "schema_version": 1,
        "saved_query_id": "query-transport",
        "version": 1,
        "access_partition_id": "public",
        "search": {
            "profile_id": "default",
            "query": None,
            "filters": {"sources": ["reddit", "x"]},
            "page_size": 100,
            "sort": "observed_desc",
            "revision_mode": "current",
        },
    }


def test_saved_query_public_schema_registers_exact_command_families():
    catalog = json.loads(
        (ROOT / "skills/last30days/schemas/saved-query-contracts-v1.json").read_text()
    )
    assert catalog["schema_version"] == 1
    assert set(catalog["contracts"]) == {
        "saved_query_view_ref",
        "saved_query_definition",
        "saved_query_command_request",
        "saved_query_view_snapshot",
    }
    variants = catalog["contracts"]["saved_query_command_request"]["properties"][
        "command"
    ]["oneOf"]
    actions = set()
    for variant in variants:
        action = variant["properties"]["action"]
        actions.update(action.get("enum", [action.get("const")]))
    assert actions == {"save", "get", "capture", "receipt"}


@pytest.mark.skipif(shutil.which("go") is None, reason="Go toolchain unavailable")
def test_saved_query_cli_http_and_fresh_mcp_share_one_closed_contract(tmp_path):
    db = tmp_path / "corpus.db"
    binary = tmp_path / "mcp"
    command_file = tmp_path / "get.json"
    _seed_post_corpus(db)
    app = initialize_application(db, retriever=object(), effect_mode="cache_only")
    server = UnixServiceServer(tmp_path / "runtime/service.sock", app)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    client = ServiceClient(server.socket_path)
    saved = client.saved_query({"action": "save", "definition": _definition()})
    mismatched = _definition()
    mismatched["saved_query_id"] = "query-wrong-profile"
    mismatched["search"]["profile_id"] = "other"
    with pytest.raises(ServiceClientError, match="invalid_contract"):
        client.saved_query({"action": "save", "definition": mismatched})
    view_ref = {
        "schema_version": 1,
        "view_kind": "saved_query",
        "saved_query_id": "query-transport",
        "saved_query_version": 1,
    }
    command_file.write_text(
        json.dumps({"action": "get", "view_ref": view_ref}), encoding="utf-8"
    )
    version = json.loads((ROOT / "mcp/manifest.json").read_text())["version"]
    subprocess.run(
        [
            "go", "build", "-trimpath", "-ldflags", f"-X main.Version={version}",
            "-o", str(binary), "./cmd/last30days-pp-mcp",
        ],
        cwd=ROOT / "mcp",
        check=True,
        capture_output=True,
        timeout=120,
    )
    process = None
    try:
        cli = subprocess.run(
            [
                os.environ.get("PYTHON", "python3"),
                str(ROOT / "skills/last30days/scripts/service.py"),
                "saved-query", "--input", str(command_file),
                "--socket", str(server.socket_path),
            ],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert json.loads(cli.stdout) == saved
        process = subprocess.Popen(
            [str(binary)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env={
                "PATH": os.environ["PATH"],
                "LAST30DAYS_SERVICE_SOCKET": str(server.socket_path),
            },
            text=True,
            bufsize=1,
        )
        initialized = _call(
            process,
            1,
            "initialize",
            {
                "protocolVersion": "2025-03-26",
                "capabilities": {},
                "clientInfo": {"name": "saved-query-fixture", "version": "1"},
            },
        )
        assert "result" in initialized
        process.stdin.write(
            '{"jsonrpc":"2.0","method":"notifications/initialized"}\n'
        )
        process.stdin.flush()
        captured = _call(
            process,
            2,
            "tools/call",
            {
                "name": "saved_query",
                "arguments": {
                    "action": "capture",
                    "view_ref": view_ref,
                    "capture_id": "capture-transport",
                },
            },
        )
        assert not captured["result"].get("isError", False)
        snapshot = json.loads(captured["result"]["content"][0]["text"])
        receipt = client.saved_query(
            {
                "action": "receipt",
                "view_ref": view_ref,
                "capture_id": "capture-transport",
            }
        )
        assert receipt["snapshot"] == snapshot
        assert receipt["coverage_scope"] == "bounded_cache_view_only"
        with pytest.raises(ServiceClientError, match="partition_mismatch"):
            client.saved_query(
                {"action": "get", "view_ref": view_ref}, profile_id="other"
            )
    finally:
        if process is not None:
            process.terminate()
            process.wait(timeout=5)
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
