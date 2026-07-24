"""Bounded stochastic workers remain subordinate to deterministic host policy."""

from __future__ import annotations

import json
import subprocess
import time
from threading import Event
from dataclasses import replace
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor

import pytest

from lib.service_intelligence import (
    AdapterFailure,
    AppServerTurn,
    CodexAppServerClient,
    ENRICHMENT_OUTPUT_SCHEMA,
    GitBranchManager,
    GitWorktreeTestExecutor,
    IntelligenceLedger,
    MaintenancePolicy,
    RepairSupervisor,
    StructuredIntelligenceWorkers,
    TestOutcome,
)
from lib.service_store import ServiceStore
from lib.service_supervisor import RefreshSupervisor


NOW = datetime(2026, 7, 24, 20, 0, tzinfo=timezone.utc)


def test_enrichment_output_schema_uses_app_server_strict_subset():
    entity_schema = ENRICHMENT_OUTPUT_SCHEMA["properties"]["entity_proposals"][
        "items"
    ]

    assert entity_schema["properties"]["schema_version"] == {
        "enum": [1],
        "type": "integer",
    }
    encoded = json.dumps(ENRICHMENT_OUTPUT_SCHEMA)
    assert '"const"' not in encoded
    assert '"minLength"' not in encoded
    assert '"maxLength"' not in encoded
    assert '"pattern"' not in encoded


def _job(db_path):
    ServiceStore(db_path).initialize()
    supervisor = RefreshSupervisor(db_path, clock=lambda: NOW)
    supervisor.initialize()
    return supervisor.enqueue_refresh(
        query_request_id="query-ai",
        query="adapter repair",
        sources=("reddit",),
        profile_id="default",
        freshness_window_seconds=3600,
        max_attempts=2,
        budget_cents=100,
    ).job


class FakeAppServer:
    def __init__(self, outputs):
        self.outputs = list(outputs)
        self.calls = []

    def structured_turn(self, **kwargs):
        self.calls.append(kwargs)
        output = self.outputs.pop(0)
        return AppServerTurn(
            model_ref="openai:gpt-5.6-codex",
            thread_id="thread-001",
            turn_id=f"turn-{len(self.calls):03d}",
            output=output,
            events=({"method": "turn/completed"},),
        )


class FailingAppServer:
    def structured_turn(self, **kwargs):
        del kwargs
        raise RuntimeError("synthetic app-server failure")


class FakeBranches:
    def __init__(self):
        self.calls = []

    def create(self, run_id, parent_branch):
        self.calls.append((run_id, parent_branch))
        return f"repair/{run_id[-8:]}"


class FakeTests:
    def __init__(self, passed=True):
        self.passed = passed
        self.calls = []

    def run(self, command, *, cwd, branch):
        self.calls.append((command, cwd, branch))
        return TestOutcome(
            command=command,
            passed=self.passed,
            metrics={"failures": 0 if self.passed else 1},
            output={"exit_code": 0 if self.passed else 1},
        )


def test_structured_enrichment_and_evaluation_are_schema_validated_and_replayable(
    tmp_path,
):
    db_path = tmp_path / "research.db"
    job = _job(db_path)
    client = FakeAppServer(
        [
            {
                "action": "propose_enrichment",
                "entity_proposals": [],
                "relationship_proposals": [],
                "confidence": 0.8,
                "rationale": "No unsupported entities were invented.",
                "evidence_ids": ["chunk-001"],
            },
            {
                "action": "record_judgments",
                "judgments": [
                    {
                        "case_id": "case-001",
                        "document_id": "doc-001",
                        "relevance": 3,
                        "evidence_ids": ["case-001"],
                    }
                ],
                "confidence": 0.9,
                "rationale": "The cited document directly answers the case.",
                "evidence_ids": ["case-001"],
            },
        ]
    )
    ledger = IntelligenceLedger(db_path, clock=lambda: NOW)
    workers = StructuredIntelligenceWorkers(
        ledger,
        client,
        cwd=tmp_path,
    )

    enrichment = workers.enrich(
        job_id=job.job_id,
        input_payload={"chunks": [{"chunk_id": "chunk-001", "text": "evidence"}]},
    )
    evaluation = workers.evaluate(
        job_id=job.job_id,
        input_payload={
            "cases": [
                {
                    "case_id": "case-001",
                    "expected_document_ids": ["doc-001"],
                }
            ]
        },
    )

    assert enrichment.accepted is True
    assert evaluation.accepted is True
    assert ledger.get_artifact(enrichment.input_ref)["payload"]["chunks"][0][
        "chunk_id"
    ] == "chunk-001"
    assert ledger.get_artifact(evaluation.output_ref)["judgments"][0][
        "relevance"
    ] == 3
    replay = ledger.replay_calls(job.job_id)
    assert [row["loop_name"] for row in replay] == [
        "entity_relationship_enrichment",
        "retrieval_evaluation_judgment",
    ]
    assert all(row["event_stream_ref"] for row in replay)
    assert "Normalized public input JSON" in client.calls[0]["prompt"]
    assert '"chunk_id":"chunk-001"' in client.calls[0]["prompt"]
    with pytest.raises(RuntimeError, match="call bound"):
        workers.enrich(job_id=job.job_id, input_payload={"chunks": []})


def test_invalid_structured_output_is_recorded_but_never_accepted(tmp_path):
    db_path = tmp_path / "research.db"
    job = _job(db_path)
    client = FakeAppServer(
        [
            {
                "action": "propose_enrichment",
                "entity_proposals": [],
                "relationship_proposals": [],
                "confidence": 1.2,
                "rationale": "invalid",
                "evidence_ids": [],
                "unexpected": "must fail closed",
            }
        ]
    )
    workers = StructuredIntelligenceWorkers(
        IntelligenceLedger(db_path, clock=lambda: NOW),
        client,
        cwd=tmp_path,
    )

    result = workers.enrich(job_id=job.job_id, input_payload={"chunks": []})

    assert result.accepted is False
    assert "output_schema_invalid" in result.validator_errors


def test_failed_model_call_is_replayable_and_consumes_atomic_bound(tmp_path):
    db_path = tmp_path / "research.db"
    job = _job(db_path)
    ledger = IntelligenceLedger(db_path, clock=lambda: NOW)
    workers = StructuredIntelligenceWorkers(
        ledger,
        FailingAppServer(),
        cwd=tmp_path,
    )

    with pytest.raises(RuntimeError, match="synthetic"):
        workers.enrich(
            job_id=job.job_id,
            input_payload={"chunks": [{"chunk_id": "chunk-001", "text": "public"}]},
        )
    with pytest.raises(RuntimeError, match="call bound"):
        workers.enrich(
            job_id=job.job_id,
            input_payload={"chunks": [{"chunk_id": "chunk-001", "text": "public"}]},
        )

    replay = ledger.replay_calls(job.job_id)
    assert len(replay) == 1
    assert replay[0]["status"] == "failed"
    assert replay[0]["error_code"] == "runtimeerror"
    assert replay[0]["event_stream_ref"]


def test_model_call_reservation_is_concurrency_safe(tmp_path):
    db_path = tmp_path / "research.db"
    job = _job(db_path)
    ledger = IntelligenceLedger(db_path, clock=lambda: NOW)
    input_ref = ledger.put_artifact({"chunks": []}, kind="test:input")

    def reserve():
        return ledger.reserve_model_call(
            job_id=job.job_id,
            loop_name="concurrent-test",
            input_ref=input_ref,
            max_calls=1,
            reserved_cost_cents=1,
            cost_budget_cents=1,
        )

    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = []
        for future in [pool.submit(reserve), pool.submit(reserve)]:
            try:
                outcomes.append(("ok", future.result()))
            except RuntimeError as exc:
                outcomes.append(("error", str(exc)))

    assert [kind for kind, _ in outcomes].count("ok") == 1
    assert [kind for kind, _ in outcomes].count("error") == 1


def test_worker_rejects_unsupplied_evidence_and_secret_like_input(tmp_path):
    db_path = tmp_path / "research.db"
    job = _job(db_path)
    client = FakeAppServer(
        [
            {
                "action": "propose_enrichment",
                "entity_proposals": [],
                "relationship_proposals": [],
                "confidence": 0.8,
                "rationale": "unsupported citation",
                "evidence_ids": ["invented-evidence"],
            }
        ]
    )
    workers = StructuredIntelligenceWorkers(
        IntelligenceLedger(db_path, clock=lambda: NOW),
        client,
        cwd=tmp_path,
        max_calls_per_job_loop=2,
        cost_budget_cents=2,
    )

    result = workers.enrich(
        job_id=job.job_id,
        input_payload={"chunks": [{"chunk_id": "chunk-001", "text": "public"}]},
    )
    assert result.accepted is False
    assert "evidence_not_supplied" in result.validator_errors
    with pytest.raises(ValueError, match="credential"):
        workers.enrich(
            job_id=job.job_id,
            input_payload={
                "chunks": [
                    {
                        "chunk_id": "chunk-002",
                        "text": "api_key=abcdefghijklmnop",
                    }
                ]
            },
        )


def test_nonempty_enrichment_grounds_only_provenance_identifiers(tmp_path):
    db_path = tmp_path / "research.db"
    job = _job(db_path)
    client = FakeAppServer(
        [
            {
                "action": "propose_enrichment",
                "entity_proposals": [
                    {
                        "schema_version": 1,
                        "proposal_id": "new-proposal-id",
                        "document_id": "doc-001",
                        "evidence_chunk_id": "chunk-001",
                        "canonical_name": "Example Product",
                        "entity_type": "product",
                        "evidence_start": 0,
                        "evidence_end": 7,
                        "extractor_version": "app-intelligence-v1",
                        "confidence": 0.9,
                    }
                ],
                "relationship_proposals": [],
                "confidence": 0.9,
                "rationale": "The public chunk names the product.",
                "evidence_ids": ["chunk-001"],
            }
        ]
    )
    result = StructuredIntelligenceWorkers(
        IntelligenceLedger(db_path, clock=lambda: NOW),
        client,
        cwd=tmp_path,
    ).enrich(
        job_id=job.job_id,
        input_payload={
            "chunks": [
                {
                    "chunk_id": "chunk-001",
                    "document_id": "doc-001",
                    "text": "Example Product",
                }
            ]
        },
    )

    assert result.accepted is True


def test_repair_supervisor_bounds_branch_tests_and_human_gated_actions(tmp_path):
    db_path = tmp_path / "research.db"
    job = _job(db_path)
    recommendation = {
        "action": "apply_patch",
        "confidence": 0.87,
        "target_files": ["skills/last30days/scripts/lib/reddit.py"],
        "risk": "medium",
        "rationale": "The adapter parser no longer matches the fixture.",
        "next_prompt": "Patch only the parser and preserve the public contract.",
    }
    client = FakeAppServer([recommendation])
    branches = FakeBranches()
    tests = FakeTests()
    policy = MaintenancePolicy(
        repeated_failure_threshold=2,
        max_investigation_attempts=2,
        max_rework=1,
        max_branches=1,
        allowed_write_roots=("skills/last30days/scripts/lib",),
        allowed_tests=("uv run pytest tests/test_reddit.py",),
        allowed_approvers=("operator@example.test",),
    )
    supervisor = RepairSupervisor(
        IntelligenceLedger(db_path, clock=lambda: NOW),
        client,
        policy,
        cwd=tmp_path,
        branch_manager=branches,
        test_executor=tests,
    )
    failure = AdapterFailure(
        job_id=job.job_id,
        adapter="reddit",
        failure_fingerprint="parser:listing-shape-v2",
        occurrences=2,
        evidence_ids=("ev-001",),
        diagnostic_refs=("artifact:log-redacted",),
    )

    result = supervisor.investigate(failure)
    branch = supervisor.prepare_branch(result.run_id, parent_branch="main")
    evaluation = supervisor.evaluate(
        result.run_id,
        commands=("uv run pytest tests/test_reddit.py",),
    )
    rework_evaluation = supervisor.evaluate(
        result.run_id,
        commands=("uv run pytest tests/test_reddit.py",),
    )
    with pytest.raises(RuntimeError, match="rework bound"):
        supervisor.evaluate(
            result.run_id,
            commands=("uv run pytest tests/test_reddit.py",),
        )

    assert result.accepted is True
    assert branch.startswith("repair/")
    assert evaluation.passed is True
    assert rework_evaluation.passed is True
    assert supervisor.action_authorized(result.run_id, "publish") is False
    approval_id = supervisor.request_approval(result.run_id, "publish")
    with pytest.raises(PermissionError):
        supervisor.decide_approval(
            approval_id,
            approved=True,
            decided_by="model",
        )
    supervisor.decide_approval(
        approval_id,
        approved=True,
        decided_by="operator@example.test",
    )
    assert supervisor.action_authorized(result.run_id, "publish") is True
    assert (
        supervisor.action_authorized(result.run_id, "mutate_live_source_config")
        is False
    )


def test_repair_supervisor_fails_closed_on_scope_and_attempt_bounds(tmp_path):
    db_path = tmp_path / "research.db"
    job = _job(db_path)
    unsafe = {
        "action": "apply_patch",
        "confidence": 0.9,
        "target_files": ["/etc/passwd"],
        "risk": "high",
        "rationale": "unsafe",
        "next_prompt": None,
    }
    client = FakeAppServer([unsafe, unsafe])
    policy = MaintenancePolicy(
        repeated_failure_threshold=2,
        max_investigation_attempts=2,
        max_rework=1,
        max_branches=1,
        allowed_write_roots=("skills/last30days/scripts/lib",),
        allowed_tests=("uv run pytest tests/test_reddit.py",),
        allowed_approvers=("operator@example.test",),
    )
    supervisor = RepairSupervisor(
        IntelligenceLedger(db_path, clock=lambda: NOW),
        client,
        policy,
        cwd=tmp_path,
        branch_manager=FakeBranches(),
        test_executor=FakeTests(),
    )
    failure = AdapterFailure(
        job_id=job.job_id,
        adapter="reddit",
        failure_fingerprint="unsafe",
        occurrences=2,
        evidence_ids=(),
        diagnostic_refs=(),
    )

    assert supervisor.investigate(failure).accepted is False
    assert supervisor.investigate(failure).accepted is False
    with pytest.raises(RuntimeError, match="attempt bound"):
        supervisor.investigate(failure)
    with pytest.raises(ValueError, match="not allowlisted"):
        supervisor.evaluate(
            supervisor.run_id_for(failure),
            commands=("curl https://example.com",),
        )


def test_policy_serialization_is_stable_and_secret_free():
    policy = MaintenancePolicy(
        repeated_failure_threshold=2,
        max_investigation_attempts=2,
        max_rework=1,
        max_branches=1,
        allowed_write_roots=("skills/last30days/scripts/lib",),
        allowed_tests=("uv run pytest tests/test_reddit.py",),
        allowed_approvers=("operator@example.test",),
    )

    payload = policy.to_dict()

    assert json.dumps(payload, sort_keys=True) == json.dumps(
        replace(policy).to_dict(),
        sort_keys=True,
    )
    assert "token" not in json.dumps(payload).casefold()


def test_existing_maintenance_run_rejects_policy_drift(tmp_path):
    db_path = tmp_path / "research.db"
    job = _job(db_path)
    ledger = IntelligenceLedger(db_path, clock=lambda: NOW)
    policy = MaintenancePolicy(
        repeated_failure_threshold=2,
        max_investigation_attempts=2,
        max_rework=1,
        max_branches=1,
        allowed_write_roots=("skills/last30days/scripts/lib",),
        allowed_tests=("uv run pytest tests/test_reddit.py",),
        allowed_approvers=("operator@example.test",),
    )
    failure = AdapterFailure(
        job_id=job.job_id,
        adapter="reddit",
        failure_fingerprint="policy-drift",
        occurrences=2,
        evidence_ids=(),
        diagnostic_refs=(),
    )
    ledger.begin_or_get_run(failure, policy)

    with pytest.raises(RuntimeError, match="policy is immutable"):
        ledger.begin_or_get_run(
            failure,
            replace(policy, allowed_approvers=("different@example.test",)),
        )


def test_failed_evaluation_cannot_request_approval(tmp_path):
    db_path = tmp_path / "research.db"
    job = _job(db_path)
    policy = MaintenancePolicy(
        repeated_failure_threshold=2,
        max_investigation_attempts=2,
        max_rework=1,
        max_branches=1,
        allowed_write_roots=("skills/last30days/scripts/lib",),
        allowed_tests=("uv run pytest tests/test_reddit.py",),
        allowed_approvers=("operator@example.test",),
    )
    supervisor = RepairSupervisor(
        IntelligenceLedger(db_path, clock=lambda: NOW),
        FakeAppServer(
            [
                {
                    "action": "apply_patch",
                    "confidence": 0.8,
                    "target_files": ["skills/last30days/scripts/lib/reddit.py"],
                    "risk": "medium",
                    "rationale": "bounded repair",
                    "next_prompt": None,
                }
            ]
        ),
        policy,
        cwd=tmp_path,
        branch_manager=FakeBranches(),
        test_executor=FakeTests(passed=False),
    )
    result = supervisor.investigate(
        AdapterFailure(
            job_id=job.job_id,
            adapter="reddit",
            failure_fingerprint="failed-eval",
            occurrences=2,
            evidence_ids=(),
            diagnostic_refs=(),
        )
    )
    supervisor.prepare_branch(result.run_id, parent_branch="main")
    assert (
        supervisor.evaluate(
            result.run_id,
            commands=("uv run pytest tests/test_reddit.py",),
        ).passed
        is False
    )
    with pytest.raises(RuntimeError, match="passing evaluation"):
        supervisor.request_approval(result.run_id, "publish")


def test_branch_and_evaluation_claims_are_concurrency_safe(tmp_path):
    db_path = tmp_path / "research.db"
    job = _job(db_path)
    policy = MaintenancePolicy(
        repeated_failure_threshold=2,
        max_investigation_attempts=2,
        max_rework=0,
        max_branches=1,
        allowed_write_roots=("skills/last30days/scripts/lib",),
        allowed_tests=("uv run pytest tests/test_reddit.py",),
        allowed_approvers=("operator@example.test",),
    )
    entered = Event()
    release = Event()

    class SlowBranches(FakeBranches):
        def create(self, run_id, parent_branch):
            entered.set()
            release.wait(timeout=2)
            return super().create(run_id, parent_branch)

    supervisor = RepairSupervisor(
        IntelligenceLedger(db_path, clock=lambda: NOW),
        FakeAppServer(
            [
                {
                    "action": "apply_patch",
                    "confidence": 0.8,
                    "target_files": ["skills/last30days/scripts/lib/reddit.py"],
                    "risk": "medium",
                    "rationale": "bounded repair",
                    "next_prompt": None,
                }
            ]
        ),
        policy,
        cwd=tmp_path,
        branch_manager=SlowBranches(),
        test_executor=FakeTests(),
    )
    result = supervisor.investigate(
        AdapterFailure(
            job_id=job.job_id,
            adapter="reddit",
            failure_fingerprint="concurrency",
            occurrences=2,
            evidence_ids=(),
            diagnostic_refs=(),
        )
    )
    with ThreadPoolExecutor(max_workers=2) as pool:
        first = pool.submit(
            supervisor.prepare_branch,
            result.run_id,
            parent_branch="main",
        )
        assert entered.wait(timeout=2)
        second = pool.submit(
            supervisor.prepare_branch,
            result.run_id,
            parent_branch="main",
        )
        with pytest.raises(RuntimeError, match="recommendation"):
            second.result(timeout=2)
        release.set()
        assert first.result(timeout=2).startswith("repair/")

    entered.clear()
    release.clear()

    class SlowTests(FakeTests):
        def run(self, command, *, cwd, branch):
            entered.set()
            release.wait(timeout=2)
            return super().run(command, cwd=cwd, branch=branch)

    supervisor.test_executor = SlowTests()
    with ThreadPoolExecutor(max_workers=2) as pool:
        first = pool.submit(
            supervisor.evaluate,
            result.run_id,
            commands=("uv run pytest tests/test_reddit.py",),
        )
        assert entered.wait(timeout=2)
        second = pool.submit(
            supervisor.evaluate,
            result.run_id,
            commands=("uv run pytest tests/test_reddit.py",),
        )
        with pytest.raises(RuntimeError, match="not ready"):
            second.result(timeout=2)
        release.set()
        assert first.result(timeout=2).passed is True


def test_concrete_git_branch_and_worktree_test_executor(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-b", "main"], cwd=repo, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.test"],
        cwd=repo,
        check=True,
    )
    subprocess.run(["git", "config", "user.name", "Test"], cwd=repo, check=True)
    (repo / "README.md").write_text("test\n", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "test"], cwd=repo, check=True, capture_output=True)
    run_id = "repair-run-" + "a" * 24

    branch = GitBranchManager(cwd=repo).create(run_id, "main")
    result = GitWorktreeTestExecutor(
        state_root=tmp_path / "worktrees",
    ).run(
        "git status --porcelain",
        cwd=repo,
        branch=branch,
    )

    assert branch == "last30days-repair/" + "a" * 24
    assert result.passed is True
    assert result.output["stdout_tail"] == ""
    assert list((tmp_path / "worktrees").iterdir()) == []


def test_app_server_accepts_only_completed_agent_item_for_active_turn():
    valid = {
        "method": "item/completed",
        "params": {
            "turnId": "turn-1",
            "item": {"type": "agentMessage", "text": '{"ok":true}'},
        },
    }
    unrelated = {
        "method": "item/completed",
        "params": {
            "turnId": "turn-2",
            "item": {"type": "agentMessage", "text": '{"ok":false}'},
        },
    }

    assert CodexAppServerClient._completed_agent_text(valid, "turn-1") == '{"ok":true}'
    assert CodexAppServerClient._completed_agent_text(unrelated, "turn-1") is None


def test_app_server_response_requires_matching_id_and_object_result():
    class StubClient(CodexAppServerClient):
        def __init__(self, payloads):
            self.payloads = iter(payloads)

        def _next(self, process, deadline):
            del process, deadline
            return next(self.payloads)

    events = []
    response = StubClient(
        [
            {"method": "notice", "params": {}},
            {"id": 7, "result": {"ok": True}},
        ]
    )._read_response(object(), 7, events, time.monotonic() + 1)
    assert response["result"] == {"ok": True}
    assert events == [{"method": "notice", "params": {}}]

    with pytest.raises(RuntimeError, match="invalid result"):
        StubClient([{"id": 7, "result": "not-an-object"}])._read_response(
            object(),
            7,
            [],
            time.monotonic() + 1,
        )
