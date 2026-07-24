"""Live Go MCP to Python service contract smoke over a real Unix socket."""

from __future__ import annotations

import json
import os
import select
import shutil
import subprocess
import sys
import time
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SERVICE = ROOT / "skills" / "last30days" / "scripts" / "service.py"


def _response(process: subprocess.Popen[str], request_id: int) -> dict:
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        ready, _, _ = select.select([process.stdout], [], [], 0.2)
        if not ready:
            continue
        line = process.stdout.readline()
        if not line:
            break
        payload = json.loads(line)
        if payload.get("id") == request_id:
            return payload
    raise AssertionError(f"MCP response {request_id} was not returned")


def _call(
    process: subprocess.Popen[str],
    request_id: int,
    method: str,
    params: dict | None = None,
) -> dict:
    assert process.stdin is not None
    process.stdin.write(
        json.dumps(
            {
                "jsonrpc": "2.0",
                "id": request_id,
                "method": method,
                **({"params": params} if params is not None else {}),
            },
            separators=(",", ":"),
        )
        + "\n"
    )
    process.stdin.flush()
    return _response(process, request_id)


@pytest.mark.skipif(shutil.which("go") is None, reason="Go toolchain unavailable")
def test_real_service_mcp_discovery_query_refresh_and_poll(tmp_path):
    socket_path = tmp_path / "runtime" / "service.sock"
    db_path = tmp_path / "research.db"
    binary = tmp_path / "last30days-mcp"
    subprocess.run(
        ["go", "build", "-o", str(binary), "./cmd/last30days-pp-mcp"],
        cwd=ROOT / "mcp",
        check=True,
        capture_output=True,
        text=True,
    )
    service = subprocess.Popen(
        [
            sys.executable,
            os.fspath(SERVICE),
            "serve",
            "--socket",
            os.fspath(socket_path),
            "--db",
            os.fspath(db_path),
        ],
        cwd=SERVICE.parent,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        deadline = time.monotonic() + 10
        while not socket_path.is_socket() and time.monotonic() < deadline:
            if service.poll() is not None:
                raise AssertionError(service.stderr.read())
            time.sleep(0.05)
        assert socket_path.is_socket()

        env = {
            **os.environ,
            "LAST30DAYS_SERVICE_SOCKET": os.fspath(socket_path),
        }
        mcp = subprocess.Popen(
            [os.fspath(binary)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            text=True,
            bufsize=1,
        )
        try:
            initialized = _call(
                mcp,
                1,
                "initialize",
                {
                    "protocolVersion": "2025-03-26",
                    "capabilities": {},
                    "clientInfo": {"name": "pytest", "version": "1"},
                },
            )
            assert "result" in initialized
            assert mcp.stdin is not None
            mcp.stdin.write(
                '{"jsonrpc":"2.0","method":"notifications/initialized"}\n'
            )
            mcp.stdin.flush()

            listed = _call(mcp, 2, "tools/list")
            assert sorted(
                tool["name"] for tool in listed["result"]["tools"]
            ) == sorted(
                ["service_info", "query", "refresh", "job_status", "topic"]
            )
            info = _call(
                mcp,
                3,
                "tools/call",
                {"name": "service_info", "arguments": {}},
            )
            assert json.loads(info["result"]["content"][0]["text"])["status"] in {
                "ready",
                "degraded",
            }
            query = _call(
                mcp,
                4,
                "tools/call",
                {
                    "name": "query",
                    "arguments": {
                        "query": "integration fixture",
                        "freshness_policy": "cache_only",
                    },
                },
            )
            assert (
                json.loads(query["result"]["content"][0]["text"])["cache_status"]
                == "miss"
            )
            refresh = _call(
                mcp,
                5,
                "tools/call",
                {
                    "name": "refresh",
                    "arguments": {
                        "query": "integration fixture",
                        "sources": ["test-fixture"],
                    },
                },
            )
            job_id = json.loads(refresh["result"]["content"][0]["text"])[
                "job_id"
            ]
            polled = _call(
                mcp,
                6,
                "tools/call",
                {"name": "job_status", "arguments": {"job_id": job_id}},
            )
            assert (
                json.loads(polled["result"]["content"][0]["text"])["job_id"]
                == job_id
            )
        finally:
            mcp.terminate()
            mcp.wait(timeout=5)
    finally:
        service.terminate()
        service.wait(timeout=10)
