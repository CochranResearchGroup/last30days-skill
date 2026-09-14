"""Repo-only WI-005 synthetic follow proof on the stock cache-only runtime.

Synthetic preparation is an explicit fixture write, never live collection.
Public probes perform reads and expected effect denials only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import signal
import socket
import sqlite3
import subprocess
import sys
import tarfile
import time
from contextlib import closing, contextmanager
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [
    str(ROOT),
    str(ROOT / "skills/last30days/scripts"),
    str(Path(__file__).parent),
]

import lane_runtime
from lib.service_acquisition_worker import execute_work
from lib.service_client import ServiceClient, ServiceClientError
from lib.service_collection import CollectionCoordinator
from lib.service_contracts import PostSearchRequest
from lib.service_job_runner import AcquisitionJobRunner, JobRunnerPolicy
from lib.service_publication import CorpusPublisher
from lib.service_refresh import RefreshPolicy, ServiceRefreshScheduler
from lib.service_retrieval import HybridRetriever, LocalHashEmbeddingProvider
from lib.service_store import ServiceStore
from lib.service_supervisor import RefreshSupervisor
from post_search_dogfood import (
    FreshMCP,
    assert_parity,
    build_mcp,
    database_digest,
    digest,
    owned_process_census,
    service_request,
)

from tests.test_service_collection import NOW, _follow_spec, _spec


@contextmanager
def unchanged(db):
    """Prove each public read or denied effect left the entire store unchanged."""
    before = database_digest(db)
    try:
        yield
    finally:
        assert database_digest(db) == before, "public follow probe mutated database"


def assert_follow_parity(expected, actual):
    assert expected == actual, "follow evidence parity mismatch"


def verify_source_manifest(manifest):
    """Bind packaged production modules to this probe's exact clean source."""
    for entry in manifest["files"]:
        source = (ROOT / entry["source"]).resolve(strict=True)
        assert source.is_relative_to(ROOT), "source manifest path mismatch"
        assert hashlib.sha256(source.read_bytes()).hexdigest() == entry["sha256"], (
            "source artifact mismatch"
        )


@contextmanager
def fixture_effect_guard():
    """Fixture preparation cannot silently fall through to DNS/network/children."""

    def deny(*_args, **_kwargs):
        raise AssertionError("fixture external effect attempted")

    with (
        patch.object(socket, "getaddrinfo", deny),
        patch.object(socket.socket, "connect", deny),
        patch.object(socket.socket, "connect_ex", deny),
        patch.object(subprocess, "Popen", deny),
    ):
        yield


def seed_fixture(db):
    """Prepare a bounded synthetic history using the real production pipeline."""
    with fixture_effect_guard():
        return _seed_fixture(db)


def _seed_fixture(db):
    db = Path(db)
    if db.exists():
        with closing(
            sqlite3.connect(f"{db.resolve().as_uri()}?mode=ro", uri=True)
        ) as conn:
            tables = {
                row[0]
                for row in conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                )
            }
            for table in (
                "documents",
                "collection_specs",
                "service_jobs",
                "service_ticks",
            ):
                if (
                    table in tables
                    and conn.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
                ):
                    raise ValueError("fixture_database_not_empty")
    supervisor = RefreshSupervisor(db, clock=lambda: NOW)
    supervisor.initialize()
    ledger = ServiceStore(db)
    scheduler = ServiceRefreshScheduler(
        supervisor,
        ledger,
        RefreshPolicy(
            default_sources=("reddit", "youtube"),
            freshness_seconds=3600,
            max_attempts=1,
            budget_cents=100,
        ),
        clock=lambda: NOW,
    )
    coordinator = CollectionCoordinator(
        db,
        scheduler,
        clock=lambda: NOW,
        follow_execution_ready=lambda spec: spec.source in {"reddit", "youtube"},
    )
    fixtures = {
        source: json.loads(
            (ROOT / f"tests/fixtures/follow_{source}_packet2.json").read_text()
        )
        for source in ("reddit", "youtube")
    }
    specs = []
    for source, kind, value, profile in (
        ("reddit", "community", "fixturelab", "follow-owner"),
        ("reddit", "user", "fixture-user", "follow-owner"),
        ("youtube", "channel", "UCabcdefghijklmnopqrstuv", "follow-owner"),
        ("reddit", "community", "fixturelab", "private"),
    ):
        specs.append(
            coordinator.put_spec(
                _follow_spec(
                    collection_spec_id=f"native-{kind}-{profile}",
                    name=f"Fixture {kind} {profile}",
                    source=source,
                    surface_kind=kind,
                    selector={kind: value},
                    profile_id=profile,
                    lookback_seconds=604800,
                )
            )
        )
    for source in ("reddit", "youtube"):
        specs.append(
            coordinator.put_spec(
                _spec(
                    collection_spec_id=f"general-{source}",
                    name=f"General {source}",
                    source=source,
                    selector={"topic": "fixture"},
                    profile_id="follow-owner",
                    redaction_class="authenticated",
                    enabled=False,
                    assessment_enabled=False,
                    required_access_method="keyless"
                    if source == "reddit"
                    else "yt_dlp",
                    lookback_seconds=604800,
                )
            )
        )
    requests, route_calls, results = [], [], []

    class Worker:
        def run(self, request):
            requests.append(request.to_dict())
            fixture = json.loads(json.dumps(fixtures[request.source]))
            if request.profile_id == "private":
                raw = fixture["payload"]["data"]["children"][0]["data"]
                raw["permalink"] = raw["permalink"].replace(raw["id"], "private001")
                raw["id"] = "private001"

            def transport(url, **limits):
                route_calls.append(
                    {"url": url, "request_limit": limits["network_request_limit"]}
                )
                return fixture

            def general(*_args):
                if request.source == "reddit":
                    raw = fixture["payload"]["data"]["children"][0]["data"]
                    item = {
                        "id": raw["id"],
                        "url": "https://www.reddit.com" + raw["permalink"],
                        "title": raw["title"],
                        "selftext": raw["selftext"],
                        "subreddit": raw["subreddit"],
                        "date": "2026-07-23T12:00:00Z",
                        "metadata": {"author": raw["author"]},
                    }
                else:
                    raw = fixture["payload"]["entries"][0]
                    item = {
                        "video_id": raw["id"],
                        "url": "https://www.youtube.com/watch?v=" + raw["id"],
                        "title": raw["title"],
                        "description": raw["description"],
                        "channel_name": raw["channel"],
                        "date": "2026-07-23T00:00:00Z",
                        "media": [],
                    }
                return {"items": [item]}

            result = execute_work(
                request,
                {},
                clock=lambda: NOW,
                adapters={request.adapter: general},
                follow_transports={
                    "reddit_community_posts": transport,
                    "reddit_user_posts": transport,
                    "youtube_channel_uploads": transport,
                },
            )
            results.append(result.to_dict())
            return result

    for spec in specs:
        first = coordinator.enqueue_interval(
            spec.collection_spec_id, scheduled_for=NOW.isoformat(), trigger="manual"
        )
        assert (
            coordinator.enqueue_interval(
                spec.collection_spec_id, scheduled_for=NOW.isoformat(), trigger="timer"
            ).collection_run_id
            == first.collection_run_id
        )
    coordinator.set_enabled(specs[0].collection_spec_id, enabled=True)
    coordinator.set_enabled(specs[0].collection_spec_id, enabled=False)
    runner = AcquisitionJobRunner(
        supervisor,
        ledger,
        CorpusPublisher(
            db,
            HybridRetriever(db, embedding_provider=LocalHashEmbeddingProvider()),
            clock=lambda: NOW,
        ),
        Worker(),
        scheduler,
        JobRunnerPolicy(lease_seconds=121),
        clock=lambda: NOW,
        collection_coordinator=coordinator,
    )
    for index in range(len(specs)):
        assert (
            runner.run_once(worker_id=f"follow-fixture-{index}").state.value
            == "published"
        )
    replay = runner.run_once(worker_id="follow-fixture-replay")
    assert replay is None
    coordinator.archive_spec(specs[2].collection_spec_id)
    x = coordinator.put_spec(
        _follow_spec(collection_spec_id="x-history", profile_id="follow-owner")
    )
    x_before = x.to_dict()
    coordinator.set_enabled(x.collection_spec_id, enabled=True)
    coordinator.set_enabled(x.collection_spec_id, enabled=False)
    archived_x = coordinator.archive_spec(x.collection_spec_id)
    assert x.follow_target_id == archived_x.follow_target_id
    quarantine = coordinator.put_spec(
        _follow_spec(
            collection_spec_id="quarantined",
            name="Historical malformed target",
            source="reddit",
            surface_kind="community",
            selector={"community": "fixtureold"},
            profile_id="follow-owner",
        )
    )
    malformed = replace(quarantine, selector={"community": "bad//target"}, enabled=True)
    with closing(sqlite3.connect(db)) as conn:
        conn.execute(
            "UPDATE collection_specs SET enabled=1, selector_json=? WHERE collection_spec_id=?",
            (json.dumps(malformed.selector), malformed.collection_spec_id),
        )
        conn.execute(
            "UPDATE collection_spec_revisions SET spec_json=?, spec_digest=?, selector_digest=? WHERE collection_spec_id=?",
            (
                json.dumps(malformed.to_dict()),
                malformed.spec_digest,
                malformed.selector_digest,
                malformed.collection_spec_id,
            ),
        )
        conn.commit()
        versions = conn.execute("SELECT count(*) FROM document_versions").fetchone()[0]
        sightings = conn.execute(
            "SELECT count(*) FROM document_version_sightings"
        ).fetchone()[0]
        original_x = json.loads(
            conn.execute(
                "SELECT spec_json FROM collection_spec_revisions WHERE collection_spec_id='x-history' AND spec_version=1"
            ).fetchone()[0]
        )
    assert coordinator.get_spec("quarantined").is_quarantined_follow
    assert original_x == x_before
    assert requests[0]["collection_context"]["spec_version"] == 1
    return {
        "versions": versions,
        "sightings": sightings,
        "fixture_route_calls": len(route_calls),
        "external_requests": 0,
        "replay_work": replay,
        "x_history_unchanged": True,
        "frozen_revision": 1,
        "fixture_sha256": {key: digest(value) for key, value in fixtures.items()},
        "requests": requests,
        "results": results,
        "route_calls": route_calls,
        "collections": list(coordinator.list_specs(include_archived=True)),
        "details": {
            item["spec"]["collection_spec_id"]: coordinator.get_spec_detail(
                item["spec"]["collection_spec_id"]
            )
            for item in coordinator.list_specs(include_archived=True)
        },
        "database_digest": database_digest(db),
    }


def tool_payload(mcp, name, arguments):
    result = mcp.tool(name, arguments)
    assert not result.get("isError"), result
    payload = json.loads(result["content"][0]["text"])
    assert len(json.dumps(payload, separators=(",", ":")).encode()) <= 131_072
    return payload


def check_follows(client, mcp, db, seed):
    """Check public reads and outer denials, without running acquisition."""
    tools = {item["name"]: item for item in mcp.call("tools/list")["tools"]}
    assert {"follow_capabilities", "collection", "search_posts"} <= set(tools)
    assert tools["follow_capabilities"]["annotations"]["readOnlyHint"] is True
    assert tools["follow_capabilities"]["annotations"]["openWorldHint"] is False
    with unchanged(db):
        catalog = client.follow_capabilities()
        assert_follow_parity(catalog, client._request("GET", "/v1/follow-capabilities"))
        assert_follow_parity(catalog, tool_payload(mcp, "follow_capabilities", {}))
    native = {(row["source"], row["target_kind"]): row for row in catalog["targets"]}
    for key in (("reddit", "community"), ("reddit", "user"), ("youtube", "channel")):
        row = native[key]
        assert row["state"] == "available"
        assert row["execution_readiness"]["state"] == "unavailable"
        assert "dependency_readiness" in row
    for row in catalog["targets"]:
        if row["source"] in {"facebook", "linkedin"}:
            assert row["state"] != "available"

    def collection(arguments):
        with unchanged(db):
            http = client.intelligence({"action": "collection", **arguments})
            assert_follow_parity(http, tool_payload(mcp, "collection", arguments))
            return http

    owned = [
        item
        for item in seed["collections"]
        if item["spec"]["profile_id"] == "follow-owner"
    ]
    listing = collection(
        {"operation": "list", "profile_id": "follow-owner", "include_archived": True}
    )
    assert_follow_parity(owned, listing["collections"])
    details = {}
    for item in owned:
        identifier = item["spec"]["collection_spec_id"]
        result = collection(
            {
                "operation": "get",
                "profile_id": "follow-owner",
                "collection_spec_id": identifier,
            }
        )
        assert_follow_parity(seed["details"][identifier], result["collection"])
        details[identifier] = result["collection"]
    assert [r["spec_version"] for r in details["x-history"]["history"]] == [1, 2, 3, 4]
    frozen = next(
        request
        for request in seed["requests"]
        if request["collection_context"]["collection_spec_id"]
        == "native-community-follow-owner"
    )
    assert (
        details["native-community-follow-owner"]["last_run"]["job_id"]
        == frozen["job_id"]
    )
    assert frozen["collection_context"]["spec_version"] == 1
    assert details["native-community-follow-owner"]["spec"]["spec_version"] == 3

    for profile in ("other", "default"):
        assert (
            collection(
                {"operation": "list", "profile_id": profile, "include_archived": True}
            )["collections"]
            == []
        )
        with unchanged(db):
            args = {
                "operation": "get",
                "profile_id": profile,
                "collection_spec_id": "native-community-follow-owner",
            }
            denied = mcp.tool("collection", args)
            assert denied.get("isError") is True
            assert "native-community-follow-owner" not in json.dumps(denied)
            try:
                client.intelligence({"action": "collection", **args})
            except ServiceClientError as exc:
                assert str(exc) == "invalid_contract: request contract is invalid"
            else:
                raise AssertionError("cross-profile collection disclosed")
    private = collection(
        {"operation": "list", "profile_id": "private", "include_archived": True}
    )
    assert len(private["collections"]) == 1

    searches = []
    cases = [
        ("follow-owner", identifier, 1)
        for identifier in (
            "native-community-follow-owner",
            "native-user-follow-owner",
            "native-channel-follow-owner",
            "general-reddit",
            "general-youtube",
        )
    ]
    cases += [
        ("follow-owner", "native-community-private", 0),
        ("other", "native-community-follow-owner", 0),
        ("default", "native-community-follow-owner", 0),
    ]
    for profile, identifier, expected in cases:
        arguments = {
            "profile_id": profile,
            "collection_refs": [f"legacy:spec:{identifier}"],
            "page_size": 20,
        }
        with unchanged(db):
            response = client.search_posts(
                PostSearchRequest.from_dict(service_request(arguments))
            ).to_dict()
            assert_parity(response, tool_payload(mcp, "search_posts", arguments))
            assert response["returned"] == expected
            if expected:
                hit = response["hits"][0]
                overlap = (
                    {
                        "native-community-follow-owner",
                        "native-user-follow-owner",
                        "general-reddit",
                    }
                    if hit["source"] == "reddit"
                    else {"native-channel-follow-owner", "general-youtube"}
                )
                assert set(hit["collection_refs"]) >= {
                    f"legacy:spec:{item}" for item in overlap
                }
            assert "native-community-private" not in json.dumps(
                response.get("hits", [])
            )
            searches.append(
                {
                    "profile": profile,
                    "collection": identifier,
                    "response": {
                        k: v
                        for k, v in response.items()
                        if k not in {"request_id", "generated_at"}
                    },
                }
            )

    denials = []
    for operation in ("put", "pause", "resume", "archive", "run"):
        arguments = {
            "operation": operation,
            "profile_id": "follow-owner",
            "collection_spec_id": "native-community-follow-owner",
        }
        if operation == "put":
            arguments["spec"] = details["native-community-follow-owner"]["spec"]
        with unchanged(db):
            denied = mcp.tool("collection", arguments)
            assert denied.get("isError") is True
            assert "effect_disabled_by_runtime" in json.dumps(denied)
            try:
                client.intelligence({"action": "collection", **arguments})
            except ServiceClientError as exc:
                expected = f"effect_disabled_by_runtime: runtime policy denies collection_{operation}"
                assert str(exc) == expected
                denials.append(expected)
            else:
                raise AssertionError("runtime collection effect admitted")
    with unchanged(db):
        try:
            client.resume_job(seed["requests"][0]["job_id"])
        except ServiceClientError as exc:
            assert (
                str(exc)
                == "effect_disabled_by_runtime: runtime policy denies job_resume"
            )
            denials.append(str(exc))
        else:
            raise AssertionError("runtime job resume admitted")
        assert client.tick_schedule_status()["enabled"] is False
    return {
        "state": "passed",
        "authorized_collections": len(owned),
        "search_cases": len(searches),
        "denied_operations": len(denials),
        "catalog": catalog,
        "details": details,
        "searches": searches,
        "denials": denials,
        "database_digest": database_digest(db),
    }


def check_cli(entrypoint, descriptor, seed):
    """CLI is a direct-database operator read, not a profile-scoped HTTP client."""
    environment = lane_runtime.build_child_environment(descriptor)
    db = Path(descriptor.database_path)

    def call(*arguments):
        with unchanged(db):
            result = subprocess.run(
                [
                    sys.executable,
                    str(entrypoint),
                    "collection",
                    *arguments,
                    "--db",
                    str(db),
                ],
                env=environment,
                capture_output=True,
                check=True,
                timeout=12,
            )
            assert len(result.stdout) <= 131_072
            return json.loads(result.stdout)

    listing = call("list", "--include-archived")
    assert_follow_parity(seed["collections"], listing["collections"])
    for identifier in (
        "native-community-follow-owner",
        "native-user-follow-owner",
        "native-channel-follow-owner",
        "x-history",
        "quarantined",
    ):
        assert_follow_parity(seed["details"][identifier], call("get", identifier))
    return {
        "state": "passed",
        "scope": "explicit_disposable_database_operator_reads",
        "profile_authorization_claimed": False,
        "read_count": 6,
        "digest": digest(listing),
    }


def run(args):
    if args.worktree.resolve() != ROOT:
        raise ValueError("probe must use its exact source worktree")
    descriptor = lane_runtime._expected_descriptor(args)
    if Path(descriptor.state_root).exists():
        raise ValueError("fresh_runtime_root_required")
    first = hashlib.sha256(args.artifact.read_bytes()).hexdigest()
    second = hashlib.sha256(args.comparison_artifact.read_bytes()).hexdigest()
    assert first == second, "reproducible artifact mismatch"
    with tarfile.open(args.artifact, "r:gz") as archive:
        manifests = [
            item
            for item in archive.getmembers()
            if item.name.endswith("/runtime-manifest.json")
        ]
        assert len(manifests) == 1 and manifests[0].size <= 1_048_576
        manifest = json.load(archive.extractfile(manifests[0]))
    verify_source_manifest(manifest)
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
        "plan": "0120",
        "work_item": "WI-005",
        "state": "failed",
        "source_commit": descriptor.commit,
        "descriptor": descriptor.to_dict(),
        "provider_free": True,
        "synthetic_only": True,
        "build_sha256": [first, second],
        "runtime_cycles": [],
        "mcp_processes": [],
        "acceptance_bound_seconds": 180,
    }
    owned = []
    active = False
    receipt_path = Path(descriptor.state_root) / "receipts/follow-packet3.json"
    started_at = time.monotonic()

    def deadline(_signum, _frame):
        raise TimeoutError("follow runtime acceptance deadline exceeded")

    previous = signal.signal(signal.SIGALRM, deadline)
    signal.alarm(180)
    try:
        for cycle in range(2):
            started = lane_runtime.up(args)
            assert started["state"] == "ready", started
            active = True
            owned.append(started["process"])
            entry = {"startup": started}
            report["runtime_cycles"].append(entry)
            assert started["artifact"]["sha256"] == first
            entrypoint = Path(started["process"]["cmdline"][1])
            assert entrypoint.is_relative_to(Path(descriptor.artifacts_dir))
            db = Path(descriptor.database_path)
            if cycle == 0:
                report["preparation_before_digest"] = database_digest(db)
                seed = seed_fixture(db)
                report["synthetic_preparation"] = seed
                binary = build_mcp(Path(descriptor.state_root) / "follow-mcp")
                report["mcp_binary_sha256"] = hashlib.sha256(
                    binary.read_bytes()
                ).hexdigest()
            with FreshMCP(
                binary,
                Path(descriptor.socket_path),
                Path(descriptor.state_root) / f"mcp-home-{cycle}",
            ) as mcp:
                report["mcp_processes"].append(mcp.birth)
                client = ServiceClient(Path(descriptor.socket_path), timeout=12)
                info = tool_payload(mcp, "service_info", {})
                assert info["compatibility_state"] == "compatible"
                http_info = client.service_info().to_dict()
                for key in (
                    "service_version",
                    "service_api_version",
                    "contract_schema_version",
                    "contract_sha256",
                    "database_schema_version",
                    "runtime_manifest_sha256",
                ):
                    assert (
                        info[key] == http_info[key] == started["service_info"][key]
                    ), f"runtime identity mismatch: {key}"
                assert (
                    info["runtime_manifest_sha256"]
                    == started["artifact"]["manifest_sha256"]
                )
                assert info["service_version"] == manifest["service_version"]
                entry["mcp_service_info"] = info
                entry["follow"] = check_follows(client, mcp, db, seed)
                entry["cli"] = check_cli(entrypoint, descriptor, seed)
                if cycle:
                    assert_follow_parity(
                        report["runtime_cycles"][0]["follow"], entry["follow"]
                    )
                    assert_follow_parity(
                        report["runtime_cycles"][0]["cli"], entry["cli"]
                    )
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
        signal.alarm(0)
        signal.signal(signal.SIGALRM, previous)
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
        report["elapsed_seconds"] = round(time.monotonic() - started_at, 3)
        if receipt_path.parent.exists():
            lane_runtime._atomic_json(receipt_path, report)
    assert report["state"] == "passed", report
    return receipt_path, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worktree", type=Path, default=ROOT)
    parser.add_argument("--lane", default="p39-follow-packet3")
    parser.add_argument("--work-item", default="WI-005", choices=["WI-005"])
    parser.add_argument("--plan", default="0120", choices=["0120"])
    parser.add_argument("--state-root", type=Path, required=True)
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--artifact", type=Path, required=True)
    parser.add_argument("--comparison-artifact", type=Path, required=True)
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
