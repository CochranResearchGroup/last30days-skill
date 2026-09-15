"""Fresh Go MCP process against an in-process, provider-free fixture server."""

import json
import os
import shutil
import sqlite3
import subprocess
import threading
from pathlib import Path

import pytest
from lib.service_app import initialize_application
from lib.service_client import ServiceClient
from lib.service_contracts import PostSearchRequest, PostSearchResponse
from lib.service_http import UnixServiceServer

from tests.post_search_fixtures import add_vectors
from tests.test_mcp_service_integration import _call
from tests.test_service_post_search import _request_payload, _seed_post_corpus

ROOT = Path(__file__).resolve().parents[1]


def _logical_database_dump(db: Path) -> tuple[str, ...]:
    """Compare committed SQLite contents independently of WAL checkpointing."""
    with sqlite3.connect(f"{db.resolve().as_uri()}?mode=ro", uri=True) as connection:
        connection.execute("PRAGMA query_only=ON")
        return tuple(connection.iterdump())


@pytest.mark.skipif(shutil.which("go") is None, reason="Go toolchain unavailable")
def test_fresh_mcp_client_preserves_hybrid_pages_and_python_http_contract(tmp_path):
    fixture = json.loads((ROOT / "tests/fixtures/post_search_packet3.json").read_text())
    args = fixture["mcp_arguments"]
    db, binary = tmp_path / "search.db", tmp_path / "mcp"
    _seed_post_corpus(db)
    add_vectors(db, query=args["query"])
    app = initialize_application(db, retriever=object(), effect_mode="cache_only")
    request = _request_payload(
        query=args["query"], filters={"sources": args["sources"]}, page_size=1
    )
    version = json.loads((ROOT / "mcp/manifest.json").read_text())["version"]
    subprocess.run(
        [
            "go",
            "build",
            "-trimpath",
            "-ldflags",
            f"-X main.Version={version}",
            "-o",
            str(binary),
            "./cmd/last30days-pp-mcp",
        ],
        cwd=ROOT / "mcp",
        check=True,
        capture_output=True,
        timeout=120,
    )
    server = UnixServiceServer(tmp_path / "runtime/service.sock", app)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    before = _logical_database_dump(db)
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
    try:
        initialized = _call(
            process,
            1,
            "initialize",
            {
                "protocolVersion": "2025-03-26",
                "capabilities": {},
                "clientInfo": {"name": "post-search-fixture", "version": "1"},
            },
        )
        assert "result" in initialized
        process.stdin.write('{"jsonrpc":"2.0","method":"notifications/initialized"}\n')
        process.stdin.flush()
        first = _call(
            process, 2, "tools/call", {"name": "search_posts", "arguments": args}
        )
        payload = json.loads(first["result"]["content"][0]["text"])
        parsed = PostSearchResponse.from_dict(payload)
        assert (
            parsed.hits
            == ServiceClient(server.socket_path)
            .search_posts(PostSearchRequest.from_dict(request))
            .hits
        )
        assert parsed.coverage["ranking_version"] == fixture["ranking_version"]
        assert parsed.hits[0].matching_channels == ("semantic",)
        second = _call(
            process,
            3,
            "tools/call",
            {
                "name": "search_posts",
                "arguments": {**args, "cursor": parsed.next_cursor},
            },
        )
        second_payload = json.loads(second["result"]["content"][0]["text"])
        second_page = PostSearchResponse.from_dict(second_payload)
        assert (
            sorted(hit.storage_family for hit in (*parsed.hits, *second_page.hits))
            == fixture["semantic_only_families"]
        )
        assert second_page.next_cursor is None
        assert _logical_database_dump(db) == before
    finally:
        process.terminate()
        process.wait(timeout=5)
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
