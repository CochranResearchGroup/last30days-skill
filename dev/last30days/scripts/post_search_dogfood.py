"""Repo-only WI-002 acceptance on one fresh WI-001 cache-only runtime.

Run through ``uv run python`` from a clean topic worktree. This deliberately
uses synthetic repository fixtures and never accepts an arbitrary service URL.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import select
import sqlite3
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [
    str(ROOT),
    str(ROOT / "skills/last30days/scripts"),
    str(Path(__file__).parent),
]

import lane_runtime
from lib.service_client import ServiceClient, ServiceClientError
from lib.service_contracts import PostSearchRequest, PostSearchResponse

from tests.post_search_fixtures import add_vectors
from tests.test_service_post_search import _seed_packet_two


def digest(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def database_digest(db):
    with sqlite3.connect(f"{db.as_uri()}?mode=ro", uri=True) as conn:
        conn.execute("PRAGMA query_only=ON")
        return digest(list(conn.iterdump()))


def seed_fixture(db):
    """Seed only a new/empty database; production selection is absent by design."""
    if db.exists():
        with sqlite3.connect(f"{db.as_uri()}?mode=ro", uri=True) as conn:
            names = {
                row[0]
                for row in conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                )
            }
            for table in (
                "documents",
                "service_source_records",
                "service_ticks",
                "service_jobs",
            ):
                if (
                    table in names
                    and conn.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
                ):
                    raise ValueError("fixture_database_not_empty")
    _seed_packet_two(db)
    add_vectors(db)
    with sqlite3.connect(db) as conn:
        # The same native post and content seen by both adapters must dedupe.
        conn.execute("""INSERT INTO service_source_records VALUES
            ('replica', 'reddit-service', 'reddit', 'reddit-1',
             'https://reddit.example/1', 'public', 'replica-v1', '2026-09-06T12:01:00Z')""")
        conn.execute("""INSERT INTO service_source_versions
            SELECT 'replica-v1', 'replica', 'replica-attempt', content_hash,
                   title, normalized_text, author, published_at, '{}', observed_at,
                   access_partition_id, retention_class, system_from
            FROM document_versions WHERE version_id='version-legacy-current'""")


def publish_fixture(db):
    """One explicit synthetic publication between otherwise read-only probes."""
    with sqlite3.connect(db) as conn:
        conn.execute("""INSERT INTO service_source_versions
            SELECT 'packet4-published-later', record_id, provider_attempt_id,
                   'sha256:packet4-later', title, normalized_text, author, published_at,
                   metadata_json, observed_at, access_partition_id,
                   retention_class, '2026-09-10T00:00:00Z'
            FROM service_source_versions WHERE version_id='version-tick-new'""")
        conn.execute(
            "UPDATE service_source_records SET current_version_id='packet4-published-later' WHERE record_id='record-tick-public'"
        )


def build_mcp(binary):
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
        env={**os.environ, "GOPROXY": "off", "GOSUMDB": "off", "GOTOOLCHAIN": "local"},
    )
    return binary


class FreshMCP:
    """A bounded fresh stdio client with private HOME and no ambient credentials."""

    def __init__(self, binary, socket_path, home):
        self.binary, self.socket_path, self.home = binary, socket_path, home
        self.process = None
        self.request_id = 0
        self.pending = b""
        self.birth = None

    def __enter__(self):
        self.home.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.process = subprocess.Popen(
            [str(self.binary)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
            env={
                "HOME": str(self.home),
                "PATH": "/usr/bin:/bin",
                "LAST30DAYS_SERVICE_SOCKET": str(self.socket_path),
            },
        )
        self.birth = lane_runtime._process_birth(self.process.pid)
        try:
            self.call(
                "initialize",
                {
                    "protocolVersion": "2025-03-26",
                    "capabilities": {},
                    "clientInfo": {"name": "wi002-packet4", "version": "1"},
                },
            )
            self.process.stdin.write(
                b'{"jsonrpc":"2.0","method":"notifications/initialized"}\n'
            )
            self.process.stdin.flush()
            return self
        except BaseException:
            self.__exit__(None, None, None)
            raise

    def call(self, method, params=None):
        self.request_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method,
            "params": params or {},
        }
        self.process.stdin.write(json.dumps(request).encode() + b"\n")
        self.process.stdin.flush()
        deadline = time.monotonic() + 12
        while time.monotonic() < deadline:
            if b"\n" in self.pending:
                raw, self.pending = self.pending.split(b"\n", 1)
                response = json.loads(raw)
                if response.get("id") == self.request_id:
                    assert "error" not in response, "MCP protocol error"
                    return response["result"]
                continue
            ready, _, _ = select.select(
                [self.process.stdout], [], [], max(0, deadline - time.monotonic())
            )
            if ready:
                chunk = os.read(self.process.stdout.fileno(), 65_536)
                if not chunk:
                    break
                self.pending += chunk
                assert len(self.pending) <= 1_048_576, (
                    "MCP response exceeded probe bound"
                )
        raise AssertionError("MCP response timeout")

    def tool(self, name, arguments):
        return self.call("tools/call", {"name": name, "arguments": arguments})

    def search(self, arguments):
        result = self.tool("search_posts", arguments)
        assert not result.get("isError"), result
        return json.loads(result["content"][0]["text"])

    def __exit__(self, *_args):
        if self.process is not None:
            if self.process.poll() is None:
                self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=5)
            self.process.stdin.close()
            self.process.stdout.close()


def service_request(arguments):
    filters = {
        key: arguments[key]
        for key in (
            "sources",
            "authors",
            "topic_ids",
            "collection_refs",
            "published_after",
            "published_before",
            "observed_after",
            "observed_before",
        )
        if key in arguments
    }
    return {
        "schema_version": 1,
        "request_id": "wi002-packet4",
        "profile_id": arguments.get("profile_id", "default"),
        "query": arguments.get("query"),
        "filters": filters,
        "page_size": arguments.get("page_size", 20),
        "cursor": arguments.get("cursor"),
        "revision_mode": arguments.get("revision_mode", "current"),
        "sort": arguments.get("sort", "relevance"),
    }


def assert_parity(http, mcp):
    # The two transports generate different request IDs and wall-clock stamps.
    ignored = {"request_id", "generated_at"}
    assert {k: v for k, v in http.items() if k not in ignored} == {
        k: v for k, v in mcp.items() if k not in ignored
    }, "HTTP/MCP parity mismatch"
    PostSearchResponse.from_dict(http)
    PostSearchResponse.from_dict(mcp)


def owned_process_census(owners):
    """Read the OS again, including descendants in the owned process sessions."""
    sessions = {int(owner["pid"]) for owner in owners if owner is not None}
    found = []
    for path in Path("/proc").iterdir():
        if not path.name.isdigit():
            continue
        try:
            fields = (path / "stat").read_text().rsplit(") ", 1)[1].split()
            if int(fields[3]) in sessions:
                found.append(
                    {
                        "pid": int(path.name),
                        "session": int(fields[3]),
                        "state": fields[0],
                        "start_ticks": int(fields[19]),
                    }
                )
        except (FileNotFoundError, PermissionError, ProcessLookupError):
            continue
    return sorted(found, key=lambda item: item["pid"])


def check_search(client, mcp, db):
    checks = []
    initial_digest = database_digest(db)
    tools = mcp.call("tools/list")["tools"]
    search_tool = next(tool for tool in tools if tool["name"] == "search_posts")
    assert search_tool["annotations"]["readOnlyHint"] is True
    assert search_tool["annotations"]["openWorldHint"] is False
    assert {
        "query",
        "authors",
        "topic_ids",
        "collection_refs",
        "observed_after",
        "cursor",
    } <= set(search_tool["inputSchema"]["properties"])

    def query(arguments):
        before = database_digest(db)
        payload = client.search_posts(
            PostSearchRequest.from_dict(service_request(arguments))
        ).to_dict()
        other = mcp.search(arguments)
        assert_parity(payload, other)
        assert (
            len(json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode())
            <= 131_072
        )
        assert database_digest(db) == before, "search mutated database"
        return payload

    cases = [
        ("federated_current", {"query": "reliable browser agents"}, {"reddit", "x"}, 2),
        ("source", {"sources": ["reddit"]}, {"reddit"}, 1),
        ("author_legacy", {"authors": ["alice"]}, {"reddit"}, 1),
        ("author_temporal", {"authors": ["bob"]}, {"x"}, 1),
        ("topic", {"topic_ids": ["7"]}, {"reddit", "x"}, 2),
        ("private_topic", {"topic_ids": ["99"]}, set(), 0),
        ("legacy_spec", {"collection_refs": ["legacy:spec:spec-1"]}, {"reddit"}, 1),
        ("legacy_run", {"collection_refs": ["legacy:run:run-1"]}, {"reddit"}, 1),
        (
            "temporal_schedule",
            {"collection_refs": ["temporal:schedule:schedule-1"]},
            {"x"},
            1,
        ),
        (
            "temporal_target",
            {"collection_refs": ["temporal:target:x-service:target-1"]},
            {"x"},
            1,
        ),
        ("published_after", {"published_after": "2026-09-06T00:00:00Z"}, {"x"}, 1),
        (
            "published_before",
            {"published_before": "2026-09-06T00:00:00Z"},
            {"reddit"},
            1,
        ),
        (
            "observed_after",
            {"observed_after": "2026-09-08T12:00:00Z"},
            {"reddit", "x"},
            2,
        ),
        ("observed_before", {"observed_before": "2026-09-07T00:00:00Z"}, {"reddit"}, 1),
        (
            "all_revisions",
            {"sources": ["reddit", "x"], "revision_mode": "all"},
            {"reddit", "x"},
            4,
        ),
        ("private_partition", {"sources": ["x"], "profile_id": "other"}, {"x"}, 2),
        ("other_profile", {"sources": ["x"], "profile_id": "unrelated"}, {"x"}, 1),
        ("empty", {"authors": ["absent"]}, set(), 0),
        ("conjunctive", {"authors": ["alice"], "sources": ["x"]}, set(), 0),
    ]
    for name, arguments, sources, count in cases:
        page = query(arguments)
        assert {hit["source"] for hit in page["hits"]} == sources, name
        assert page["returned"] == count, name
        assert (
            len({(hit["post_id"], hit["revision_id"]) for hit in page["hits"]}) == count
        ), name
        allowed = {"public", f"profile:{arguments.get('profile_id', 'default')}"}
        for hit in page["hits"]:
            assert hit["access_partition_id"] in allowed
            assert hit["evidence_ref"]["version_id"] == hit["revision_id"]
            assert "99" not in hit["topic_ids"]
        checks.append(
            {"case": name, "returned": count, "response_digest": digest(page)}
        )
    for sort in ("published_desc", "observed_desc"):
        page = query({"sources": ["reddit", "x"], "sort": sort})
        values = [hit[sort.removesuffix("_desc") + "_at"] for hit in page["hits"]]
        assert values == sorted(values, reverse=True)

    for invalid in (
        {},
        {"query": "---"},
        {"query": "browser", "unexpected": True},
        {"query": "browser", "page_size": 0},
    ):
        assert mcp.tool("search_posts", invalid).get("isError") is True
        raw = service_request(invalid)
        if "unexpected" in invalid:
            raw["unexpected"] = True
        try:
            client._request("POST", "/v1/posts/search", raw)
        except ServiceClientError as exc:
            assert "invalid_contract" in str(exc)
        else:
            raise AssertionError("HTTP accepted malformed search")
    assert database_digest(db) == initial_digest, "read-only matrix changed database"

    args = {"sources": ["reddit", "x"], "revision_mode": "all", "page_size": 1}
    expected = query({**args, "page_size": 100})["hits"]
    first = query(args)
    assert first["next_cursor"]
    replay = {**args, "cursor": first["next_cursor"]}
    for changed in ({**replay, "profile_id": "other"}, {**replay, "sources": ["x"]}):
        assert mcp.tool("search_posts", changed).get("isError") is True
    publish_fixture(db)
    publication_digest = database_digest(db)
    hits, page = list(first["hits"]), first
    for _ in range(10):
        if not page["next_cursor"]:
            break
        page = query({**args, "cursor": page["next_cursor"]})
        assert page["search_head_id"] == first["search_head_id"]
        hits.extend(page["hits"])
    else:
        raise AssertionError("pagination exceeded frozen ten-page bound")
    assert hits == expected, "publication changed retained pagination"
    assert "packet4-published-later" in {
        hit["revision_id"] for hit in query({"sources": ["x"]})["hits"]
    }
    assert database_digest(db) == publication_digest
    return {
        "state": "passed",
        "case_count": len(checks),
        "cases": checks,
        "read_only": True,
        "database_before_publication": initial_digest,
        "database_after_publication": publication_digest,
        "publication_pinned": True,
        "retained_head": first["search_head_id"],
        "discovery_digest": digest(search_tool),
    }, replay


def run(args):
    assert args.worktree.resolve() == ROOT, (
        "probe must run from its exact source worktree"
    )
    descriptor = lane_runtime._expected_descriptor(args)
    if Path(descriptor.state_root).exists():
        raise ValueError("fresh_runtime_root_required")
    report = {
        "schema_version": 1,
        "plan": "0114",
        "work_item": "WI-002",
        "state": "failed",
        "source_commit": descriptor.commit,
        "descriptor": descriptor.to_dict(),
        "synthetic_only": True,
        "provider_free": True,
        "runtime_cycles": [],
        "mcp_processes": [],
    }
    readiness = lane_runtime.doctor(
        lane_id=args.lane,
        work_item=args.work_item,
        plan=args.plan,
        worktree=args.worktree,
        state_base=args.state_root,
        runtime_base=args.runtime_root,
        environ=os.environ,
    )
    report["doctor"] = {"ok": readiness["ok"], "reasons": readiness["reasons"]}
    assert readiness["ok"], readiness["reasons"]
    active = False
    receipt_path = Path(descriptor.state_root) / "receipts/search-packet4.json"
    owned = []
    try:
        for cycle in range(2):
            started = lane_runtime.up(args)
            assert started["state"] == "ready", started
            active = True
            owned.append(started["process"])
            entry = {"startup": started}
            report["runtime_cycles"].append(entry)
            db = Path(descriptor.database_path)
            assert lane_runtime.status(args)["state"] == "ready"
            if cycle == 0:
                seed_fixture(db)
                binary = build_mcp(Path(descriptor.state_root) / "search-mcp")
                report["mcp_binary_sha256"] = hashlib.sha256(
                    binary.read_bytes()
                ).hexdigest()
            before = database_digest(db)
            with FreshMCP(
                binary,
                Path(descriptor.socket_path),
                Path(descriptor.state_root) / f"mcp-home-{cycle}",
            ) as mcp:
                report["mcp_processes"].append(mcp.birth)
                info = json.loads(mcp.tool("service_info", {})["content"][0]["text"])
                assert info["compatibility_state"] == "compatible"
                assert (
                    info["runtime_manifest_sha256"]
                    == started["artifact"]["manifest_sha256"]
                )
                entry["mcp_service_info"] = info
                client = ServiceClient(Path(descriptor.socket_path))
                if cycle == 0:
                    report["search"], replay = check_search(client, mcp, db)
                else:
                    assert started["process"] != owned[0], "runtime was not restarted"
                    result = mcp.tool("search_posts", replay)
                    assert result.get("isError") and "cursor_stale" in str(result)
                    try:
                        client._request(
                            "POST", "/v1/posts/search", service_request(replay)
                        )
                    except ServiceClientError as exc:
                        assert "cursor_stale" in str(exc)
                    else:
                        raise AssertionError("HTTP accepted pre-restart cursor")
                    assert database_digest(db) == before
                    report["restart_stale"] = True
            entry["before_down"] = lane_runtime.status(args)
            entry["down"] = lane_runtime.down(args)
            assert entry["down"]["state"] == "stopped", entry["down"]
            active = False
            # Reap children created by the controller in this process.
            os.waitpid(started["process"]["pid"], 0)
        census = owned_process_census([*owned, *report["mcp_processes"]])
        report["owned_process_census"] = census
        report["final_controller_status"] = lane_runtime.status(args)
        assert census == []
        assert report["final_controller_status"]["state"] == "absent"
        assert not Path(descriptor.socket_path).exists()
        report["state"] = "passed"
    except BaseException as exc:
        report["failure"] = {"type": type(exc).__name__, "message": str(exc)[:2048]}
        raise
    finally:
        if active:
            report["failure_teardown"] = lane_runtime.down(args)
            if report["failure_teardown"]["state"] == "stopped":
                try:
                    os.waitpid(owned[-1]["pid"], 0)
                except ChildProcessError:
                    pass
        if receipt_path.parent.exists():
            lane_runtime._atomic_json(receipt_path, report)
    return receipt_path, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worktree", type=Path, default=ROOT)
    parser.add_argument("--lane", default="p33-search-packet4")
    parser.add_argument("--work-item", default="WI-002", choices=["WI-002"])
    parser.add_argument("--plan", default="0114", choices=["0114"])
    parser.add_argument("--state-root", type=Path, required=True)
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--artifact", type=Path, required=True)
    parser.add_argument("--timeout", type=float, default=10)
    path, report = run(parser.parse_args())
    print(
        json.dumps(
            {
                "state": report["state"],
                "receipt": str(path),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
