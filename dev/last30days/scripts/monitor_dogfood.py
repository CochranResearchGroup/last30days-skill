"""Repo-only WI-006 fresh-client proof in an isolated cache-only runtime."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
import subprocess
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
from lib.service_collection import CollectionCoordinator
from lib.service_refresh import RefreshPolicy, ServiceRefreshScheduler
from lib.service_store import ServiceStore
from lib.service_supervisor import RefreshSupervisor
from post_search_dogfood import (
    FreshMCP,
    build_mcp,
    digest,
    owned_process_census,
    seed_fixture,
)

from tests.test_service_collection import _follow_spec

DECLARED_MONITOR_TABLES = frozenset(
    {
        "service_monitor_schema_version",
        "service_monitor_specs",
        "service_monitor_view_snapshots",
        "service_monitor_runs",
        "service_monitor_baselines",
        "service_monitor_decisions",
        "service_monitor_baseline_heads",
        "service_monitor_saved_queries",
        "service_monitor_query_captures",
        "service_monitor_records",
        "service_monitor_delivery_attempts",
    }
)


def assert_parity(first, second):
    assert first == second, "monitor immutable parity mismatch"


def non_monitor_digest(db):
    tables = {}
    with closing(
        sqlite3.connect(f"{Path(db).resolve().as_uri()}?mode=ro", uri=True)
    ) as conn:
        conn.execute("PRAGMA query_only=ON")
        for name, schema in conn.execute(
            "SELECT name, sql FROM sqlite_master WHERE type='table' ORDER BY name"
        ):
            if name in DECLARED_MONITOR_TABLES or name.startswith("sqlite_"):
                continue
            quoted = '"' + name.replace('"', '""') + '"'
            rows = [
                [
                    {"blob_hex": value.hex()} if isinstance(value, bytes) else value
                    for value in row
                ]
                for row in conn.execute(f"SELECT * FROM {quoted}")
            ]
            tables[name] = {
                "schema": schema,
                "rows": sorted(rows, key=lambda row: json.dumps(row, sort_keys=True)),
            }
    return digest(tables)


def seed_monitors(db):
    """Explicit synthetic precondition, before the zero-effect measurement."""
    seed_fixture(db)
    supervisor = RefreshSupervisor(db)
    supervisor.initialize()
    scheduler = ServiceRefreshScheduler(
        supervisor, ServiceStore(db), RefreshPolicy(default_sources=("x",))
    )
    collections = CollectionCoordinator(db, scheduler)
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
            "UPDATE documents SET source='x', access_partition_id='profile:x-primary', current_version_id='follow-version-1' WHERE document_id='doc-legacy'"
        )
        conn.execute(
            """INSERT INTO document_version_sightings
            (version_id, acquisition_id, collection_spec_id, collection_run_id, observed_at, access_partition_id)
            VALUES ('follow-version-1', 'follow-probe', ?, 'fixture-run', '2026-09-05T12:01:00Z', 'profile:x-primary')""",
            (spec.collection_spec_id,),
        )
    return {
        "schema_version": 1,
        "view_kind": "follow",
        "collection_spec_id": spec.collection_spec_id,
        "spec_version": spec.spec_version,
    }


def tool(mcp, command, profile="x-primary"):
    result = mcp.tool("monitor", {"profile_id": profile, "command": command})
    assert not result.get("isError"), result
    return json.loads(result["content"][0]["text"])


def cli_read(socket_path, command, profile, state_root):
    path = state_root / "monitor-cli-input.json"
    lane_runtime._atomic_json(path, command)
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "skills/last30days/scripts/service.py"),
            "monitor",
            "--socket",
            str(socket_path),
            "--profile",
            profile,
            "--input",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
        timeout=15,
        env={"PATH": "/usr/bin:/bin", "HOME": str(state_root)},
    )
    return json.loads(result.stdout)


def check_monitors(client, mcp, db, ref):
    catalog = {item["name"]: item for item in mcp.call("tools/list")["tools"]}
    assert "monitor" in catalog
    assert set(catalog["monitor"]["inputSchema"]["properties"]) == {
        "profile_id",
        "command",
    }
    before = non_monitor_digest(db)
    request = {
        "action": "create",
        "monitor_id": "dogfood-follow",
        "name": "Synthetic follow monitor",
        "view_ref": ref,
        "cadence_seconds": 3600,
        "max_items": 20,
        "retention_days": 30,
    }
    created = client.monitor(request, profile_id="x-primary")
    assert_parity(created, tool(mcp, request))
    assert created["lifecycle_state"] == "disabled"
    tool(mcp, {"action": "activate", "monitor_id": "dogfood-follow"})
    capture = {
        "action": "capture",
        "monitor_id": "dogfood-follow",
        "capture_id": "initial",
    }
    initial = client.monitor(capture, profile_id="x-primary")
    assert len(initial["evidence"]) == 1
    assert_parity(initial, tool(mcp, capture))
    result = tool(
        mcp,
        {
            "action": "evaluate",
            "monitor_id": "dogfood-follow",
            "snapshot_id": initial["snapshot_id"],
        },
    )
    run_id = result["run"]["run_id"]
    assert result["digest"]["comparison_status"] == "baseline_only"
    assert client.monitor(
        {"action": "baseline", "monitor_id": "dogfood-follow"}, profile_id="x-primary"
    ) == {"baseline": None}
    accepted = client.monitor(
        {"action": "accept", "run_id": run_id}, profile_id="x-primary"
    )
    assert_parity(accepted, tool(mcp, {"action": "accept", "run_id": run_id}))
    second = tool(mcp, {**capture, "capture_id": "second"})
    result = client.monitor(
        {
            "action": "evaluate",
            "monitor_id": "dogfood-follow",
            "snapshot_id": second["snapshot_id"],
        },
        profile_id="x-primary",
    )
    assert result["digest"]["counts"]["unchanged"] == 1
    assert (
        result["digest"]["entries"][0]["evidence_refs"][0]["version_id"]
        == "follow-version-1"
    )
    run_id = result["run"]["run_id"]
    assert_parity(result["digest"], tool(mcp, {"action": "digest", "run_id": run_id}))
    tool(mcp, {"action": "accept", "run_id": run_id})
    preference = tool(
        mcp,
        {
            "action": "set_delivery",
            "monitor_id": "dogfood-follow",
            "expected_version": 0,
            "channel_config_ref": "fixture-only",
        },
    )
    assert preference["mode"] == "disabled"
    intent = tool(
        mcp, {"action": "prepare_delivery", "run_id": run_id, "preference_version": 1}
    )
    assert intent["mode"] == "disabled"
    for profile, bad in (
        ("other", {"action": "digest", "run_id": run_id}),
        ("x-primary", {"action": "send", "intent_id": intent["intent_id"]}),
        (
            "x-primary",
            {
                "action": "get",
                "monitor_id": "dogfood-follow",
                "access_partition_id": "other",
            },
        ),
    ):
        denied = mcp.tool("monitor", {"profile_id": profile, "command": bad})
        assert denied.get("isError"), denied
        try:
            client.monitor(bad, profile_id=profile)
        except ServiceClientError:
            pass
        else:
            raise AssertionError("HTTP monitor denial absent")
    # Public saved-query -> monitor composition uses the same command seam.
    definition = {
        "schema_version": 1,
        "saved_query_id": "dogfood-query",
        "version": 1,
        "access_partition_id": "public",
        "search": {
            "profile_id": "default",
            "query": None,
            "filters": {"sources": ["x"]},
            "page_size": 20,
            "sort": "observed_desc",
            "revision_mode": "current",
        },
    }
    client.saved_query({"action": "save", "definition": definition})
    query_ref = {
        "schema_version": 1,
        "view_kind": "saved_query",
        "saved_query_id": "dogfood-query",
        "saved_query_version": 1,
    }
    tool(
        mcp,
        {**request, "monitor_id": "dogfood-query", "view_ref": query_ref},
        "default",
    )
    tool(mcp, {"action": "activate", "monitor_id": "dogfood-query"}, "default")
    query_snapshot = tool(
        mcp,
        {"action": "capture", "monitor_id": "dogfood-query", "capture_id": "query"},
        "default",
    )
    query_result = tool(
        mcp,
        {
            "action": "evaluate",
            "monitor_id": "dogfood-query",
            "snapshot_id": query_snapshot["snapshot_id"],
        },
        "default",
    )
    assert query_result["digest"]["current_count"] >= 1
    assert non_monitor_digest(db) == before
    return {
        "state": "passed",
        "discovery_digest": digest(catalog),
        "non_monitor_digest": before,
        "follow_digest": result["digest"],
        "query_digest": query_result["digest"],
        "intent": intent,
        "case_count": 5,
    }, {
        "run_id": run_id,
        "digest": result["digest"],
        "capture": second,
        "intent": intent,
    }


def run(args):
    if args.worktree.resolve() != ROOT:
        raise ValueError("probe must use exact source worktree")
    descriptor = lane_runtime._expected_descriptor(args)
    if Path(descriptor.state_root).exists():
        raise ValueError("fresh_runtime_root_required")
    readiness = lane_runtime.doctor(
        lane_id=args.lane,
        work_item=args.work_item,
        plan=args.plan,
        worktree=args.worktree,
        state_base=args.state_root,
        runtime_base=args.runtime_root,
    )
    assert readiness["ok"], readiness
    report = {
        "schema_version": 1,
        "plan": "0121",
        "work_item": "WI-006",
        "state": "failed",
        "source_commit": descriptor.commit,
        "descriptor": descriptor.to_dict(),
        "provider_free": True,
        "synthetic_only": True,
        "runtime_cycles": [],
        "mcp_processes": [],
    }
    receipt_path = (
        Path(descriptor.state_root) / "receipts/monitor-product-closeout.json"
    )
    active, owned = False, []
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
                ref = seed_monitors(db)
                binary = build_mcp(Path(descriptor.state_root) / "monitor-mcp")
                report["mcp_binary_sha256"] = hashlib.sha256(
                    binary.read_bytes()
                ).hexdigest()
            with FreshMCP(
                binary,
                Path(descriptor.socket_path),
                Path(descriptor.state_root) / f"mcp-home-{cycle}",
            ) as mcp:
                report["mcp_processes"].append(mcp.birth)
                info_result = mcp.tool("service_info", {})
                assert not info_result.get("isError")
                info = json.loads(info_result["content"][0]["text"])
                assert info["compatibility_state"] == "compatible"
                assert (
                    info["runtime_manifest_sha256"]
                    == started["artifact"]["manifest_sha256"]
                )
                entry["service_info"] = info
                client = ServiceClient(Path(descriptor.socket_path), timeout=20)
                if cycle == 0:
                    report["monitor"], anchor = check_monitors(client, mcp, db, ref)
                else:
                    before = non_monitor_digest(db)
                    request = {"action": "digest", "run_id": anchor["run_id"]}
                    assert_parity(
                        anchor["digest"],
                        client.monitor(request, profile_id="x-primary"),
                    )
                    assert_parity(anchor["digest"], tool(mcp, request))
                    assert_parity(
                        anchor["digest"],
                        cli_read(
                            Path(descriptor.socket_path),
                            request,
                            "x-primary",
                            Path(descriptor.state_root),
                        ),
                    )
                    capture = {
                        "action": "capture",
                        "monitor_id": "dogfood-follow",
                        "capture_id": "second",
                    }
                    assert_parity(anchor["capture"], tool(mcp, capture))
                    assert_parity(
                        anchor["intent"],
                        tool(
                            mcp,
                            {
                                "action": "delivery_intent",
                                "intent_id": anchor["intent"]["intent_id"],
                            },
                        )["intent"],
                    )
                    assert non_monitor_digest(db) == before
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
    parser.add_argument("--lane", default="p40-monitor-closeout")
    parser.add_argument("--work-item", default="WI-006", choices=["WI-006"])
    parser.add_argument("--plan", default="0121", choices=["0121"])
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
