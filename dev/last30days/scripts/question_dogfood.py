"""Repo-only WI-003 fresh-client proof against one isolated WI-001 runtime."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
import sys
from contextlib import closing
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [
    str(ROOT),
    str(ROOT / "skills/last30days/scripts"),
    str(Path(__file__).parent),
]

import lane_runtime
from lib.service_client import ServiceClient, ServiceClientError
from lib.service_contracts import PostSearchRequest
from lib.service_question_contracts import EvidenceReadRequestV1, QuestionRequestV1
from post_search_dogfood import (
    FreshMCP,
    build_mcp,
    digest,
    owned_process_census,
    seed_fixture,
)

from tests.test_service_question_evidence import _question_request


def assert_question_parity(http_payload, mcp_payload):
    """Question answers are durable: even generated times and digests must match."""
    assert http_payload == mcp_payload, "question HTTP/MCP parity mismatch"


def non_question_digest(db):
    """Hash all persisted non-question tables, including corpus and effect ledgers."""
    tables = {}
    with closing(
        sqlite3.connect(f"{Path(db).resolve().as_uri()}?mode=ro", uri=True)
    ) as conn:
        conn.execute("PRAGMA query_only=ON")
        for name, schema in conn.execute(
            "SELECT name, sql FROM sqlite_master WHERE type='table' ORDER BY name"
        ):
            if name.startswith(("service_question_", "sqlite_")):
                continue
            quoted = '"' + name.replace('"', '""') + '"'
            rows = [list(row) for row in conn.execute(f"SELECT * FROM {quoted}")]
            # Blob values are retained exactly while remaining JSON serializable.
            rows = [
                [
                    {"blob_hex": value.hex()} if isinstance(value, bytes) else value
                    for value in row
                ]
                for row in rows
            ]
            tables[name] = {
                "schema": schema,
                "rows": sorted(rows, key=lambda row: json.dumps(row, sort_keys=True)),
            }
    return digest(tables)


def _tool(mcp, name, arguments):
    result = mcp.tool(name, arguments)
    assert not result.get("isError"), result
    payload = json.loads(result["content"][0]["text"])
    assert (
        len(json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode())
        <= 131_072
    )
    return payload


def check_questions(client, mcp, db):
    """Exercise real transports; admission may write only the question ledger."""
    tools = {item["name"]: item for item in mcp.call("tools/list")["tools"]}
    for name in ("search_posts", "ask_question", "question_status", "read_evidence"):
        assert name in tools, name
        assert tools[name]["annotations"]["readOnlyHint"] is (name != "ask_question")
        assert tools[name]["annotations"]["openWorldHint"] is (name == "ask_question")
    assert set(tools["ask_question"]["inputSchema"]["properties"]) == set(
        _question_request().to_dict()
    )
    assert set(tools["question_status"]["inputSchema"]["properties"]) == {
        "question_id",
        "profile_id",
    }
    baseline = non_question_digest(db)
    search = client.search_posts(
        PostSearchRequest.from_dict(
            {
                "schema_version": 1,
                "request_id": "question-probe-search",
                "profile_id": "default",
                "query": "reliable browser agents",
                "filters": {},
                "page_size": 20,
                "cursor": None,
            }
        )
    )
    assert {hit.storage_family for hit in search.hits} == {"legacy", "temporal"}
    assert (
        _tool(mcp, "search_posts", {"query": "reliable browser agents"})["returned"]
        == search.returned
    )
    checks = []
    anchor = None
    cases = (
        ("evidence", {"answer_mode": "evidence_only"}, "answered"),
        (
            "empty",
            {"answer_mode": "evidence_only", "filters": {"authors": ["absent"]}},
            "no_evidence",
        ),
        ("unavailable", {}, "model_unavailable"),
        ("fallback", {"model_fallback": "evidence_only"}, "answered"),
        (
            "private",
            {
                "answer_mode": "evidence_only",
                "profile_id": "other",
                "filters": {"sources": ["x"]},
            },
            "answered",
        ),
        (
            "all_filters",
            {
                "answer_mode": "evidence_only",
                "filters": {
                    "sources": ["x"],
                    "authors": ["bob"],
                    "topic_ids": ["7"],
                    "collection_refs": ["temporal:target:x-service:target-1"],
                    "published_after": "2026-09-07T00:00:00Z",
                    "published_before": "2026-09-08T00:00:00Z",
                    "observed_after": "2026-09-07T00:00:00Z",
                    "observed_before": "2026-09-10T00:00:00Z",
                },
            },
            "answered",
        ),
    )
    for name, overrides, expected in cases:
        payload = _question_request(
            request_id=f"question-probe-{name}", profile_id="default"
        ).to_dict()
        payload.update(overrides)
        payload["limits"]["wait_ms"] = 0
        request = QuestionRequestV1.from_dict(payload)
        result = client.ask_question(request).to_dict()
        assert result["state"] == expected, (name, result)
        assert_question_parity(result, _tool(mcp, "ask_question", payload))
        status_args = {
            "question_id": result["question_id"],
            "profile_id": request.profile_id,
        }
        assert_question_parity(result, client.question_status(**status_args).to_dict())
        assert_question_parity(result, _tool(mcp, "question_status", status_args))
        answer = result["answer"]
        if answer:
            assert answer["cache_only"] is True
            assert answer["acquisition_performed"] is False
            assert answer["model_invoked"] is False
            refs = {
                ref["evidence_id"]: ref
                for statement in answer["statements"]
                for ref in statement["citations"]
            }
            if refs:
                read_payload = {
                    "schema_version": 1,
                    "request_id": f"read-{name}",
                    "profile_id": request.profile_id,
                    "refs": list(refs.values()),
                    "max_response_bytes": 65536,
                }
                read = client.read_evidence(
                    EvidenceReadRequestV1.from_dict(read_payload)
                ).to_dict()
                assert_question_parity(read, _tool(mcp, "read_evidence", read_payload))
                assert not read["omitted_refs"]
                assert {item["ref"]["evidence_id"] for item in read["items"]} == set(
                    refs
                )
                for item in read["items"]:
                    assert item["status"] == "available"
                    assert item["ref"] == refs[item["ref"]["evidence_id"]]
                    assert item["evidence"]["version_id"] == item["ref"]["version_id"]
                if name == "all_filters":
                    assert {ref["version_id"] for ref in refs.values()} == {
                        "version-tick-new"
                    }
        if name == "evidence":
            anchor = {
                "status": result,
                "profile_id": request.profile_id,
                "evidence_request": read_payload,
                "evidence": read,
            }
        assert non_question_digest(db) == baseline, (
            "question operation changed non-question state"
        )
        checks.append(
            {"case": name, "state": result["state"], "status_digest": digest(result)}
        )
    assert anchor is not None
    for question_id in (anchor["status"]["question_id"], "question-absent"):
        denied = {"question_id": question_id, "profile_id": "unauthorized"}
        assert mcp.tool("question_status", denied).get("isError") is True
        try:
            client.question_status(**denied)
        except ServiceClientError as exc:
            assert "question unavailable" in str(exc)
        else:
            raise AssertionError("question status disclosed another profile")
    invalid = _question_request(request_id="invalid-temporal").to_dict()
    invalid["temporal"]["as_of"] = "2026-09-01T00:00:00Z"
    assert mcp.tool("ask_question", invalid).get("isError") is True
    assert non_question_digest(db) == baseline
    return {
        "state": "passed",
        "cases": checks,
        "case_count": len(checks),
        "non_question_digest": baseline,
        "discovery_digest": digest(tools),
    }, anchor


def run(args):
    if args.worktree.resolve() != ROOT:
        raise ValueError("probe must use its exact source worktree")
    descriptor = lane_runtime._expected_descriptor(args)
    if Path(descriptor.state_root).exists():
        raise ValueError("fresh_runtime_root_required")
    report = {
        "schema_version": 1,
        "plan": "0117",
        "work_item": "WI-003",
        "state": "failed",
        "source_commit": descriptor.commit,
        "descriptor": descriptor.to_dict(),
        "provider_free": True,
        "synthetic_only": True,
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
    )
    assert readiness["ok"], readiness
    owned = []
    active = False
    receipt_path = Path(descriptor.state_root) / "receipts/question-packet4.json"
    try:
        for cycle in range(2):
            started = lane_runtime.up(args)
            assert started["state"] == "ready", started
            active = True
            owned.append(started["process"])
            entry = {"startup": started}
            report["runtime_cycles"].append(entry)
            db = Path(descriptor.database_path)
            if cycle == 0:
                seed_fixture(db)
                binary = build_mcp(Path(descriptor.state_root) / "question-mcp")
                report["mcp_binary_sha256"] = hashlib.sha256(
                    binary.read_bytes()
                ).hexdigest()
            with FreshMCP(
                binary,
                Path(descriptor.socket_path),
                Path(descriptor.state_root) / f"mcp-home-{cycle}",
            ) as mcp:
                report["mcp_processes"].append(mcp.birth)
                info = _tool(mcp, "service_info", {})
                assert info["compatibility_state"] == "compatible"
                assert (
                    info["runtime_manifest_sha256"]
                    == started["artifact"]["manifest_sha256"]
                )
                entry["mcp_service_info"] = info
                client = ServiceClient(Path(descriptor.socket_path), timeout=35)
                if cycle == 0:
                    report["question"], anchor = check_questions(client, mcp, db)
                else:
                    before = non_question_digest(db)
                    status_args = {
                        "question_id": anchor["status"]["question_id"],
                        "profile_id": anchor["profile_id"],
                    }
                    assert_question_parity(
                        anchor["status"],
                        client.question_status(**status_args).to_dict(),
                    )
                    assert_question_parity(
                        anchor["status"], _tool(mcp, "question_status", status_args)
                    )
                    assert_question_parity(
                        anchor["evidence"],
                        _tool(mcp, "read_evidence", anchor["evidence_request"]),
                    )
                    assert non_question_digest(db) == before
                    report["durable_restart"] = True
            entry["before_down"] = lane_runtime.status(args)
            entry["down"] = lane_runtime.down(args)
            assert entry["down"]["state"] == "stopped", entry["down"]
            active = False
            os.waitpid(started["process"]["pid"], 0)
        report["final_controller_status"] = lane_runtime.status(args)
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
        report["owned_process_census"] = owned_process_census(
            [*owned, *report["mcp_processes"]]
        )
        if report["owned_process_census"]:
            report["state"] = "failed"
        if receipt_path.parent.exists():
            lane_runtime._atomic_json(receipt_path, report)
    assert report["state"] == "passed", report
    return receipt_path, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worktree", type=Path, default=ROOT)
    parser.add_argument("--lane", default="p36-question-packet4")
    parser.add_argument("--work-item", default="WI-003", choices=["WI-003"])
    parser.add_argument("--plan", default="0117", choices=["0117"])
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
