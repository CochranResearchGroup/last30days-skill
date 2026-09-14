#!/usr/bin/env python3
"""Run the Plan 0107 joined provider-free product acceptance."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sqlite3
import sys
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [
    str(ROOT),
    str(ROOT / "skills/last30days/scripts"),
    str(Path(__file__).parent),
]

import follow_dogfood
import lane_runtime
import monitor_dogfood
import post_search_dogfood
import question_dogfood
from lib.service_client import ServiceClient

from dev.last30days.quality import EvaluationCaseV1
from dev.last30days.quality.adapters import (
    FixtureCatalog,
    QuestionGroundingAdapter,
)

build_mcp = post_search_dogfood.build_mcp


def verify_artifact(path: Path) -> dict[str, str]:
    """Bind the packaged runtime to the exact source tree used by this driver."""
    artifact = Path(path).resolve(strict=True)
    with tarfile.open(artifact, "r:gz") as archive:
        members = [
            item
            for item in archive.getmembers()
            if item.name.endswith("/runtime-manifest.json")
        ]
        if len(members) != 1 or members[0].size > 1_048_576:
            raise ValueError("runtime_manifest_invalid")
        stream = archive.extractfile(members[0])
        if stream is None:
            raise ValueError("runtime_manifest_invalid")
        manifest_bytes = stream.read()
        manifest = json.loads(manifest_bytes)
    for entry in manifest["files"]:
        source = (ROOT / entry["source"]).resolve(strict=True)
        if not source.is_relative_to(ROOT):
            raise ValueError("runtime_manifest_source_invalid")
        if hashlib.sha256(source.read_bytes()).hexdigest() != entry["sha256"]:
            raise ValueError("runtime_manifest_source_mismatch")
    return {
        "sha256": hashlib.sha256(artifact.read_bytes()).hexdigest(),
        "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
        "service_version": str(manifest["service_version"]),
    }


def _file_digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _reset_database(descriptor) -> None:
    """Remove only the campaign descriptor's disposable working database."""
    database = Path(descriptor.database_path)
    state_root = Path(descriptor.state_root).resolve(strict=True)
    data_root = (state_root / "data").resolve(strict=True)
    if database.resolve(strict=True).parent != data_root:
        raise ValueError("database_outside_campaign_state")
    for path in (database, Path(str(database) + "-wal"), Path(str(database) + "-shm")):
        path.unlink(missing_ok=True)


def _seal_database(database: Path) -> None:
    with sqlite3.connect(database) as conn:
        conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")


def _grounding_case(database: Path, anchor: dict[str, object]) -> EvaluationCaseV1:
    status = anchor["status"]
    assert isinstance(status, dict) and isinstance(status.get("answer"), dict)
    answer = status["answer"]
    with sqlite3.connect(database) as conn:
        row = conn.execute(
            "SELECT retrieval_json FROM service_question_retrievals WHERE question_id=?",
            (status["question_id"],),
        ).fetchone()
    if row is None:
        raise AssertionError("question retrieval is not durable")
    citations = [item["evidence_id"] for item in json.loads(row[0])["evidence"]]
    return EvaluationCaseV1.from_dict(
        {
            "case_id": "plan0107-grounding",
            "axis": "grounding",
            "tags": ["provider-free", "synthetic"],
            "fixture": {
                "fixture_id": "plan0107-search-question",
                "digest": _file_digest(database),
            },
            "adapter_input": {
                "question_id": status["question_id"],
                "profile_id": anchor["profile_id"],
                "access_partitions": ["public"],
                "expected_answer_id": answer["answer_id"],
                "expected_answer_state": answer["answer_state"],
                "expected_evidence_ids": citations,
                "expected_uncertainty_codes": answer["uncertainty_codes"],
            },
        },
        "plan0107.grounding",
    )


def _quality_grounding(database: Path, anchor: dict[str, object]) -> dict[str, object]:
    before = database.read_bytes()
    outcome = QuestionGroundingAdapter(
        FixtureCatalog({"plan0107-search-question": database})
    ).evaluate(_grounding_case(database, anchor), result_limit=20)
    if outcome.state != "passed":
        raise AssertionError(f"grounding quality failed: {outcome.failure_codes}")
    if database.read_bytes() != before:
        raise AssertionError("grounding quality mutated its sealed fixture")
    return {
        "state": outcome.state,
        "outcome": outcome.to_dict(),
        "fixture_sha256": _file_digest(database),
        "database_reads": True,
        "database_writes": 0,
        "network_requests": 0,
        "model_calls": 0,
        "browser_actions": 0,
        "runtime_mutations": 0,
    }


def _service_info(mcp) -> dict[str, object]:
    result = mcp.tool("service_info", {})
    if result.get("isError"):
        raise AssertionError(result)
    return json.loads(result["content"][0]["text"])


def _check_search_question_quality(client, mcp, database: Path):
    """Retain the question head before search tests publish a later revision."""
    questions, anchor = question_dogfood.check_questions(client, mcp, database)
    search, _ = post_search_dogfood.check_search(client, mcp, database)
    return {"search": search, "questions": questions}, anchor


def _execute_phase(args, descriptor, binary: Path, name: str) -> dict[str, object]:
    if Path(descriptor.database_path).exists():
        _reset_database(descriptor)
    started = lane_runtime.up(args)
    if started["state"] != "ready":
        raise AssertionError(started)
    active = True
    mcp_birth = None
    phase: dict[str, object] = {
        "name": name,
        "runtime_id": descriptor.runtime_id,
        "startup": started,
    }
    try:
        status = lane_runtime.status(args)
        if status["state"] != "ready":
            raise AssertionError(status)
        phase["status"] = status
        database = Path(descriptor.database_path)
        if name == "search_question_quality":
            post_search_dogfood.seed_fixture(database)
        elif name == "follows":
            seed = follow_dogfood.seed_fixture(database)
        elif name == "monitors":
            monitor_ref = monitor_dogfood.seed_monitors(database)
        else:
            raise ValueError("unknown_campaign_phase")
        if not binary.exists():
            build_mcp(binary)
        with post_search_dogfood.FreshMCP(
            binary,
            Path(descriptor.socket_path),
            Path(descriptor.state_root) / f"mcp-home-{name}",
        ) as mcp:
            mcp_birth = mcp.birth
            mcp_info = _service_info(mcp)
            http_info = (
                ServiceClient(Path(descriptor.socket_path)).service_info().to_dict()
            )
            for key in (
                "service_version",
                "service_api_version",
                "contract_schema_version",
                "contract_sha256",
                "database_schema_version",
                "runtime_manifest_sha256",
            ):
                if not mcp_info[key] == http_info[key] == started["service_info"][key]:
                    raise AssertionError(f"runtime identity mismatch: {key}")
            phase["mcp_service_info"] = mcp_info
            phase["http_service_info"] = http_info
            client = ServiceClient(Path(descriptor.socket_path), timeout=35)
            if name == "search_question_quality":
                phase["result"], anchor = _check_search_question_quality(
                    client, mcp, database
                )
            elif name == "follows":
                follows = follow_dogfood.check_follows(client, mcp, database, seed)
                cli = follow_dogfood.check_cli(
                    Path(started["process"]["cmdline"][1]), descriptor, seed
                )
                phase["result"] = {"follows": follows, "cli": cli}
            else:
                monitors, monitor_anchor = monitor_dogfood.check_monitors(
                    client, mcp, database, monitor_ref
                )
                cli_digest = monitor_dogfood.cli_read(
                    Path(descriptor.socket_path),
                    {"action": "digest", "run_id": monitor_anchor["run_id"]},
                    "x-primary",
                    Path(descriptor.state_root),
                )
                monitor_dogfood.assert_parity(monitor_anchor["digest"], cli_digest)
                phase["result"] = {"monitors": monitors, "cli_digest": cli_digest}
        down = lane_runtime.down(args)
        if down["state"] != "stopped":
            raise AssertionError(down)
        phase["down"] = down
        active = False
        os.waitpid(started["process"]["pid"], 0)
        _seal_database(database)
        fixture = Path(descriptor.state_root) / "receipts/fixtures" / f"{name}.sqlite"
        fixture.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        shutil.copy2(database, fixture)
        phase["fixture"] = {"path": str(fixture), "sha256": _file_digest(fixture)}
        if name == "search_question_quality":
            phase["result"]["quality"] = _quality_grounding(fixture, anchor)
        census = post_search_dogfood.owned_process_census(
            [started["process"], mcp_birth]
        )
        if census:
            raise AssertionError(f"owned processes remain: {census}")
        phase["owned_process_census"] = census
        phase["final_status"] = lane_runtime.status(args)
        if phase["final_status"]["state"] != "absent":
            raise AssertionError("phase runtime owner remains")
        if Path(descriptor.socket_path).exists():
            raise AssertionError("phase socket remains")
        return phase
    finally:
        if active:
            teardown = lane_runtime.down(args)
            phase["failure_teardown"] = teardown
            if teardown["state"] == "stopped":
                try:
                    os.waitpid(started["process"]["pid"], 0)
                except ChildProcessError:
                    pass


def _search_question_quality(args, descriptor, binary, name):
    return _execute_phase(args, descriptor, binary, name)


def _follows(args, descriptor, binary, name):
    return _execute_phase(args, descriptor, binary, name)


def _monitors(args, descriptor, binary, name):
    return _execute_phase(args, descriptor, binary, name)


PHASE_RUNNERS = (
    ("search_question_quality", _search_question_quality),
    ("follows", _follows),
    ("monitors", _monitors),
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worktree", type=Path, default=ROOT)
    parser.add_argument("--lane", default="p52-provider-free-productization")
    parser.add_argument("--work-item", default="WI-000", choices=["WI-000"])
    parser.add_argument("--plan", default="0107", choices=["0107"])
    parser.add_argument("--state-root", type=Path, required=True)
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--artifact", type=Path, required=True)
    parser.add_argument("--timeout", type=float, default=15)
    return parser


def run(args):
    if args.worktree.resolve() != ROOT:
        raise ValueError("probe must use exact source worktree")
    descriptor = lane_runtime._expected_descriptor(args)
    if Path(descriptor.state_root).exists():
        raise ValueError("fresh_runtime_root_required")
    artifact = verify_artifact(args.artifact)
    readiness = lane_runtime.doctor(
        lane_id=args.lane,
        work_item=args.work_item,
        plan=args.plan,
        worktree=args.worktree,
        state_base=args.state_root,
        runtime_base=args.runtime_root,
        environ=os.environ,
    )
    if not readiness["ok"]:
        raise RuntimeError(readiness["reasons"])
    binary = Path(descriptor.state_root) / "campaign-mcp"
    report = {
        "schema_version": 1,
        "plan": "0107",
        "work_item": "WI-000",
        "state": "failed",
        "source_commit": descriptor.commit,
        "runtime_id": descriptor.runtime_id,
        "descriptor": descriptor.to_dict(),
        "artifact": artifact,
        "doctor": readiness,
        "provider_free": True,
        "synthetic_only": True,
        "phases": [],
    }
    receipt_path = Path(descriptor.state_root) / "receipts/plan0107-final-runtime.json"
    try:
        for name, runner in PHASE_RUNNERS:
            phase = runner(args, descriptor, binary, name)
            if phase["runtime_id"] != descriptor.runtime_id:
                raise AssertionError("phase runtime identity mismatch")
            report["phases"].append(phase)
        report["final_controller_status"] = lane_runtime.status(args)
        if report["final_controller_status"]["state"] != "absent":
            raise AssertionError("runtime owner remains after campaign")
        report["state"] = "passed"
    except BaseException as exc:
        report["failure"] = {"type": type(exc).__name__, "message": str(exc)[:2048]}
        raise
    finally:
        if receipt_path.parent.exists():
            lane_runtime._atomic_json(receipt_path, report)
    return receipt_path, report


def main() -> None:
    path, report = run(build_parser().parse_args())
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
