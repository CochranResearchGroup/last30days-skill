"""Governed recurring collection and post-publication assessment boundaries."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timedelta, timezone

import pytest

from lib import service_contracts as contracts
from lib.service_collection import (
    CollectionCoordinator,
    CollectionSpec,
    CollectionSpecValidationError,
)
from lib.service_intelligence_contracts import (
    ContentAssessmentQueue,
    ContentAssessmentWorker,
)
from lib.service_job_runner import AcquisitionJobRunner, JobRunnerPolicy
from lib.service_publication import CorpusPublisher
from lib.service_refresh import RefreshPolicy, ServiceRefreshScheduler
from lib.service_retrieval import HybridRetriever
from lib.service_store import ServiceStore
from lib.service_supervisor import RefreshSupervisor


NOW = datetime(2026, 7, 25, 12, 0, tzinfo=timezone.utc)


def _spec(**overrides: object) -> CollectionSpec:
    payload: dict[str, object] = {
        "schema_version": 1,
        "collection_spec_id": "spec-reddit-ai",
        "name": "Reddit agent intelligence",
        "source": "reddit",
        "surface_kind": "topic",
        "selector": {"topic": "agent intelligence"},
        "profile_id": "default",
        "interval_seconds": 3600,
        "lookback_seconds": 7200,
        "item_limit": 20,
        "wall_timeout_seconds": 90,
        "network_request_limit": 50,
        "budget_cents": 25,
        "retention_class": "cache",
        "redaction_class": "public",
        "assessment_enabled": True,
        "enabled": True,
        "spec_version": 1,
    }
    payload.update(overrides)
    return CollectionSpec.from_dict(payload)


def _coordinator(tmp_path, *, now=NOW):
    db_path = tmp_path / "research.db"
    supervisor = RefreshSupervisor(db_path, clock=lambda: now)
    supervisor.initialize()
    ledger = ServiceStore(db_path)
    scheduler = ServiceRefreshScheduler(
        supervisor,
        ledger,
        RefreshPolicy(
            default_sources=("reddit",),
            freshness_seconds=3600,
            max_attempts=2,
            budget_cents=100,
        ),
        clock=lambda: now,
    )
    coordinator = CollectionCoordinator(
        db_path,
        scheduler,
        clock=lambda: now,
    )
    return db_path, supervisor, ledger, scheduler, coordinator


def test_collection_spec_is_strict_bounded_and_surface_typed():
    spec = _spec()

    assert CollectionSpec.from_dict(spec.to_dict()) == spec
    assert contracts.parse_envelope("collection_spec", spec.to_dict()) == spec
    assert spec.selector_digest.startswith("sha256:")
    assert spec.query == "agent intelligence"

    with pytest.raises(CollectionSpecValidationError, match="unknown fields"):
        CollectionSpec.from_dict({**spec.to_dict(), "cookie": "forbidden"})
    with pytest.raises(CollectionSpecValidationError, match="selector"):
        _spec(selector={"handle": "@wrong-for-topic"})
    with pytest.raises(CollectionSpecValidationError, match="redaction_class"):
        _spec(profile_id="browser", redaction_class="public")
    with pytest.raises(CollectionSpecValidationError, match="browser sources"):
        _spec(source="linkedin")
    with pytest.raises(CollectionSpecValidationError, match="item_limit"):
        _spec(item_limit=10001)


def test_timer_and_manual_trigger_coalesce_into_one_interval_run(tmp_path):
    db_path, supervisor, _ledger, _scheduler, coordinator = _coordinator(tmp_path)
    stored = coordinator.put_spec(_spec())

    timer = coordinator.enqueue_interval(
        stored.collection_spec_id,
        scheduled_for="2026-07-25T12:00:00Z",
        trigger="timer",
    )
    manual = coordinator.enqueue_interval(
        stored.collection_spec_id,
        scheduled_for="2026-07-25T12:17:00Z",
        trigger="manual",
    )

    assert timer.collection_run_id == manual.collection_run_id
    assert timer.job_id == manual.job_id
    assert supervisor.get_job(timer.job_id).state is contracts.JobState.QUEUED

    conn = sqlite3.connect(db_path)
    try:
        revision = conn.execute(
            "SELECT spec_json, selector_digest FROM collection_spec_revisions"
        ).fetchone()
        runs = conn.execute("SELECT COUNT(*) FROM collection_runs").fetchone()[0]
        claims = conn.execute(
            "SELECT trigger_kind FROM collection_run_triggers ORDER BY trigger_kind"
        ).fetchall()
    finally:
        conn.close()
    assert json.loads(revision[0]) == stored.to_dict()
    assert revision[1] == stored.selector_digest
    assert runs == 1
    assert [row[0] for row in claims] == ["manual", "timer"]


def test_collection_spec_edits_require_one_new_immutable_revision(tmp_path):
    db_path, _supervisor, _ledger, _scheduler, coordinator = _coordinator(tmp_path)
    coordinator.put_spec(_spec())

    with pytest.raises(CollectionSpecValidationError, match="immutable"):
        coordinator.put_spec(_spec(item_limit=30))
    coordinator.put_spec(_spec(item_limit=30, spec_version=2))

    conn = sqlite3.connect(db_path)
    try:
        revisions = conn.execute(
            """SELECT spec_version, spec_json
               FROM collection_spec_revisions ORDER BY spec_version"""
        ).fetchall()
    finally:
        conn.close()
    assert [row[0] for row in revisions] == [1, 2]
    assert json.loads(revisions[0][1])["item_limit"] == 20
    assert json.loads(revisions[1][1])["item_limit"] == 30


def test_collection_run_freezes_its_spec_revision_and_dedupe_scope(tmp_path):
    db_path, _supervisor, _ledger, _scheduler, coordinator = _coordinator(tmp_path)
    first = coordinator.put_spec(_spec())
    second = coordinator.put_spec(
        _spec(
            collection_spec_id="spec-reddit-ai-copy",
            name="Reddit agent intelligence copy",
        )
    )
    first_run = coordinator.enqueue_interval(
        first.collection_spec_id,
        scheduled_for="2026-07-25T12:00:00Z",
        trigger="timer",
    )
    second_run = coordinator.enqueue_interval(
        second.collection_spec_id,
        scheduled_for="2026-07-25T12:00:00Z",
        trigger="timer",
    )
    coordinator.put_spec(_spec(item_limit=30, spec_version=2))

    assert first_run.job_id != second_run.job_id
    assert coordinator.policy_for_job(first_run.job_id)["item_limit"] == 20
    conn = sqlite3.connect(db_path)
    try:
        frozen_version = conn.execute(
            """SELECT spec_version FROM collection_runs
               WHERE collection_run_id = ?""",
            (first_run.collection_run_id,),
        ).fetchone()[0]
    finally:
        conn.close()
    assert frozen_version == 1


def test_due_tick_respects_pause_and_advances_next_due_deterministically(tmp_path):
    db_path, _supervisor, _ledger, _scheduler, coordinator = _coordinator(tmp_path)
    coordinator.put_spec(_spec())
    coordinator.put_spec(
        _spec(
            collection_spec_id="spec-paused",
            name="Paused",
            selector={"topic": "paused"},
            enabled=False,
        )
    )

    created = coordinator.enqueue_due(limit=10)
    assert [run.collection_spec_id for run in created] == ["spec-reddit-ai"]
    assert coordinator.enqueue_due(limit=10) == ()

    conn = sqlite3.connect(db_path)
    try:
        next_due = conn.execute(
            """SELECT next_due_at FROM collection_schedule_state
               WHERE collection_spec_id = 'spec-reddit-ai'"""
        ).fetchone()[0]
    finally:
        conn.close()
    assert next_due == "2026-07-25T13:00:00Z"


def test_named_profile_lease_prevents_overlapping_collection_runs(tmp_path):
    _db_path, _supervisor, _ledger, _scheduler, coordinator = _coordinator(tmp_path)
    first = _spec(
        collection_spec_id="linkedin-people",
        name="LinkedIn people",
        source="linkedin",
        surface_kind="profile",
        selector={"profile_url": "https://linkedin.example/in/person"},
        profile_id="linkedin-main",
        redaction_class="authenticated",
    )
    second = _spec(
        collection_spec_id="linkedin-companies",
        name="LinkedIn companies",
        source="linkedin",
        surface_kind="profile",
        selector={"profile_url": "https://linkedin.example/company/acme"},
        profile_id="linkedin-main",
        redaction_class="authenticated",
    )
    coordinator.put_spec(first)
    coordinator.put_spec(second)
    run_one = coordinator.enqueue_interval(
        first.collection_spec_id,
        scheduled_for="2026-07-25T12:00:00Z",
        trigger="timer",
    )
    run_two = coordinator.enqueue_interval(
        second.collection_spec_id,
        scheduled_for="2026-07-25T12:00:00Z",
        trigger="timer",
    )

    coordinator.record_started(
        job_id=run_one.job_id,
        worker_id="collector-one",
        lease_generation=1,
    )
    with pytest.raises(RuntimeError, match="already leased"):
        coordinator.record_started(
            job_id=run_two.job_id,
            worker_id="collector-two",
            lease_generation=1,
        )


class _Worker:
    def __init__(self):
        self.requests = []

    def run(self, request):
        self.requests.append(request)
        return contracts.AcquisitionWorkResult.from_dict(
            {
                "schema_version": 1,
                "work_id": request.work_id,
                "job_id": request.job_id,
                "lease_generation": request.lease_generation,
                "source": request.source,
                "adapter": request.adapter,
                "adapter_version": request.adapter_version,
                "status": "succeeded",
                "safe_error_code": None,
                "retry_class": "none",
                "retry_after_seconds": None,
                "observed_at": "2026-07-25T12:00:00Z",
                "fetched_at": "2026-07-25T12:00:01Z",
                "items": [
                    {
                        "source_native_id": "post-1",
                        "url": "https://reddit.example/post-1",
                        "title": "Agent intelligence",
                        "text": "A deterministic service boundary.",
                        "author": "builder",
                        "published_at": "2026-07-25T11:55:00Z",
                        "metadata": {},
                    }
                ],
                "item_count": 1,
                "cost_cents": 0,
                "diagnostics": {"attempted_count": 3, "cursor_after": "cursor-2"},
            }
        )


class _FailingAssessment:
    def enqueue_for_acquisition(self, **kwargs):
        del kwargs
        raise RuntimeError("synthetic assessment outage")


class _AssessmentClient:
    def __init__(self):
        self.calls = []

    def structured_turn(self, **kwargs):
        self.calls.append(kwargs)

        class Turn:
            model_ref = "openai-codex:gpt-5.5"
            output = {
                "action": "record_assessment",
                "proposals": [
                    {
                        "proposal_kind": "content_signal",
                        "proposal_key": "signal:novel",
                        "confidence": 0.9,
                        "evidence_ids": [],
                        "payload": {
                            "content_type": "post",
                            "novelty": "novel",
                            "relevance": "high",
                            "follow_up_priority": "normal",
                        },
                    }
                ],
                "uncertainty_codes": [],
                "rationale": "The evidence reports a new service boundary.",
            }

        return Turn()


def test_collection_completion_records_yield_coverage_cursor_and_assessment_failure(
    tmp_path,
):
    db_path, supervisor, ledger, scheduler, coordinator = _coordinator(tmp_path)
    coordinator.put_spec(_spec())
    run = coordinator.enqueue_interval(
        "spec-reddit-ai",
        scheduled_for="2026-07-25T12:00:00Z",
        trigger="timer",
    )
    retriever = HybridRetriever(db_path)
    runner = AcquisitionJobRunner(
        supervisor,
        ledger,
        CorpusPublisher(db_path, retriever, clock=lambda: NOW),
        _Worker(),
        scheduler,
        JobRunnerPolicy(
            lease_seconds=120,
            wall_timeout_seconds=90,
            item_limit=20,
            network_request_limit=50,
            successful_coverage_seconds=3600,
            negative_cache_seconds=300,
        ),
        clock=lambda: NOW,
        collection_coordinator=coordinator,
        assessment_queue=_FailingAssessment(),
    )

    completed = runner.run_once(worker_id="collector-1")
    assert completed.state is contracts.JobState.PUBLISHED

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        stored_run = conn.execute(
            "SELECT * FROM collection_runs WHERE collection_run_id = ?",
            (run.collection_run_id,),
        ).fetchone()
        coverage = conn.execute(
            "SELECT * FROM collection_coverage_intervals"
        ).fetchone()
        cursor = conn.execute("SELECT * FROM collection_cursors").fetchone()
        health = conn.execute("SELECT * FROM collection_source_health").fetchone()
        sighting = conn.execute(
            "SELECT collection_spec_id, collection_run_id "
            "FROM document_version_sightings"
        ).fetchone()
        assessment = conn.execute(
            "SELECT state, error_code FROM collection_assessment_batches"
        ).fetchone()
    finally:
        conn.close()

    assert stored_run["state"] == "published"
    assert stored_run["attempted_count"] == 3
    assert stored_run["observed_count"] == 1
    assert stored_run["stored_count"] == 1
    assert coverage["coverage_state"] == "observed"
    assert cursor["cursor_value"] == "cursor-2"
    assert health["process_state"] == "healthy"
    assert health["yield_state"] == "nonzero"
    assert tuple(sighting) == ("spec-reddit-ai", run.collection_run_id)
    assert tuple(assessment) == ("failed", "runtimeerror")


def test_runner_applies_frozen_collection_limits_and_retention(tmp_path):
    db_path, supervisor, ledger, scheduler, coordinator = _coordinator(tmp_path)
    coordinator.put_spec(
        _spec(
            item_limit=3,
            wall_timeout_seconds=25,
            network_request_limit=4,
            retention_class="durable",
        )
    )
    run = coordinator.enqueue_interval(
        "spec-reddit-ai",
        scheduled_for="2026-07-25T12:00:00Z",
        trigger="timer",
    )
    coordinator.put_spec(
        _spec(
            item_limit=30,
            wall_timeout_seconds=50,
            network_request_limit=40,
            retention_class="cache",
            spec_version=2,
        )
    )
    retriever = HybridRetriever(db_path)
    worker = _Worker()
    runner = AcquisitionJobRunner(
        supervisor,
        ledger,
        CorpusPublisher(db_path, retriever, clock=lambda: NOW),
        worker,
        scheduler,
        JobRunnerPolicy(
            lease_seconds=120,
            wall_timeout_seconds=90,
            item_limit=20,
            network_request_limit=50,
            successful_coverage_seconds=3600,
            negative_cache_seconds=300,
        ),
        clock=lambda: NOW,
        collection_coordinator=coordinator,
    )

    completed = runner.run_once(worker_id="collector-frozen-policy")

    assert completed is not None and completed.state is contracts.JobState.PUBLISHED
    assert worker.requests[0].item_limit == 3
    assert worker.requests[0].wall_timeout_seconds == 25
    assert worker.requests[0].network_request_limit == 4
    conn = sqlite3.connect(db_path)
    try:
        retention = conn.execute(
            "SELECT retention_class FROM document_versions"
        ).fetchone()[0]
        frozen_version = conn.execute(
            "SELECT spec_version FROM collection_runs WHERE collection_run_id = ?",
            (run.collection_run_id,),
        ).fetchone()[0]
    finally:
        conn.close()
    assert retention == "durable"
    assert frozen_version == 1


def test_failed_collection_records_gap_without_advancing_cursor(tmp_path):
    db_path, _supervisor, _ledger, _scheduler, coordinator = _coordinator(tmp_path)
    coordinator.put_spec(_spec())
    run = coordinator.enqueue_interval(
        "spec-reddit-ai",
        scheduled_for="2026-07-25T12:00:00Z",
        trigger="timer",
    )
    coordinator.record_completion(
        job_id=run.job_id,
        state="failed",
        outcomes=(
            {
                "source": "reddit",
                "status": "failed",
                "attempted_count": 0,
                "observed_count": 0,
                "stored_count": 0,
                "cursor_after": None,
                "watermark_after": None,
                "error_code": "rate_limited",
            },
        ),
        completed_at=(NOW + timedelta(seconds=1)),
    )

    conn = sqlite3.connect(db_path)
    try:
        gap = conn.execute(
            "SELECT gap_kind, status FROM collection_gaps"
        ).fetchone()
        cursor = conn.execute(
            "SELECT cursor_value FROM collection_cursors"
        ).fetchone()
    finally:
        conn.close()
    assert gap == ("acquisition_failed", "open")
    assert cursor[0] is None


def test_retry_attempt_is_separate_and_resolves_the_interval_gap(tmp_path):
    db_path, _supervisor, _ledger, _scheduler, coordinator = _coordinator(tmp_path)
    coordinator.put_spec(_spec())
    run = coordinator.enqueue_interval(
        "spec-reddit-ai",
        scheduled_for="2026-07-25T12:00:00Z",
        trigger="timer",
    )
    coordinator.record_started(
        job_id=run.job_id,
        worker_id="collector",
        lease_generation=1,
    )
    coordinator.record_completion(
        job_id=run.job_id,
        state="queued",
        outcomes=(
            {
                "source": "reddit",
                "status": "failed",
                "attempted_count": 1,
                "observed_count": 0,
                "stored_count": 0,
                "cursor_after": None,
                "watermark_after": None,
                "retry_after": "2026-07-25T12:05:00Z",
                "error_code": "rate_limited",
            },
        ),
        completed_at=NOW + timedelta(seconds=1),
    )
    coordinator.record_started(
        job_id=run.job_id,
        worker_id="collector",
        lease_generation=2,
    )
    coordinator.record_completion(
        job_id=run.job_id,
        state="published",
        outcomes=(
            {
                "source": "reddit",
                "status": "succeeded",
                "attempted_count": 2,
                "observed_count": 1,
                "stored_count": 1,
                "cursor_after": "cursor-after-retry",
                "watermark_after": None,
                "retry_after": None,
                "error_code": None,
            },
        ),
        completed_at=NOW + timedelta(minutes=5),
    )

    conn = sqlite3.connect(db_path)
    try:
        attempts = conn.execute(
            """SELECT attempt, state FROM collection_run_attempts
               ORDER BY attempt"""
        ).fetchall()
        gap = conn.execute(
            "SELECT status, resolved_at FROM collection_gaps"
        ).fetchone()
        cursor = conn.execute(
            "SELECT cursor_value FROM collection_cursors"
        ).fetchone()[0]
    finally:
        conn.close()
    assert attempts == [(1, "queued"), (2, "published")]
    assert gap[0] == "resolved"
    assert gap[1] == "2026-07-25T12:05:00Z"
    assert cursor == "cursor-after-retry"


def test_disabled_app_intelligence_keeps_collection_operational(tmp_path):
    db_path, supervisor, ledger, scheduler, coordinator = _coordinator(tmp_path)
    coordinator.put_spec(_spec(assessment_enabled=False))
    coordinator.enqueue_interval(
        "spec-reddit-ai",
        scheduled_for="2026-07-25T12:00:00Z",
        trigger="timer",
    )
    retriever = HybridRetriever(db_path)
    runner = AcquisitionJobRunner(
        supervisor,
        ledger,
        CorpusPublisher(db_path, retriever, clock=lambda: NOW),
        _Worker(),
        scheduler,
        JobRunnerPolicy(
            lease_seconds=120,
            wall_timeout_seconds=90,
            item_limit=20,
            network_request_limit=50,
            successful_coverage_seconds=3600,
            negative_cache_seconds=300,
        ),
        clock=lambda: NOW,
        collection_coordinator=coordinator,
        assessment_queue=ContentAssessmentQueue(db_path, clock=lambda: NOW),
    )

    completed = runner.run_once(worker_id="collector-disabled-ai")
    assert completed.state is contracts.JobState.PUBLISHED

    conn = sqlite3.connect(db_path)
    try:
        assessment_state = conn.execute(
            "SELECT state FROM collection_assessment_batches"
        ).fetchone()[0]
        task_count = conn.execute(
            "SELECT COUNT(*) FROM service_intelligence_tasks"
        ).fetchone()[0]
    finally:
        conn.close()
    assert assessment_state == "skipped"
    assert task_count == 0


def test_enabled_assessment_is_queued_only_after_immutable_evidence_exists(tmp_path):
    db_path, supervisor, ledger, scheduler, coordinator = _coordinator(tmp_path)
    coordinator.put_spec(_spec())
    coordinator.enqueue_interval(
        "spec-reddit-ai",
        scheduled_for="2026-07-25T12:00:00Z",
        trigger="timer",
    )
    retriever = HybridRetriever(db_path)
    runner = AcquisitionJobRunner(
        supervisor,
        ledger,
        CorpusPublisher(db_path, retriever, clock=lambda: NOW),
        _Worker(),
        scheduler,
        JobRunnerPolicy(
            lease_seconds=120,
            wall_timeout_seconds=90,
            item_limit=20,
            network_request_limit=50,
            successful_coverage_seconds=3600,
            negative_cache_seconds=300,
        ),
        clock=lambda: NOW,
        collection_coordinator=coordinator,
        assessment_queue=ContentAssessmentQueue(db_path, clock=lambda: NOW),
    )

    completed = runner.run_once(worker_id="collector-assessment")
    assert completed.state is contracts.JobState.PUBLISHED

    conn = sqlite3.connect(db_path)
    try:
        task = conn.execute(
            """SELECT t.state, t.request_json, b.state
               FROM service_intelligence_tasks AS t
               JOIN collection_assessment_batches AS b ON b.task_id = t.task_id"""
        ).fetchone()
        evidence_count = conn.execute(
            "SELECT COUNT(*) FROM evidence_spans"
        ).fetchone()[0]
    finally:
        conn.close()
    request = json.loads(task[1])
    assert task[0] == "queued"
    assert task[2] == "queued"
    assert evidence_count == 1
    assert request["evidence_refs"][0]["evidence_id"]
    assert request["source_version_ids"][0]

    client = _AssessmentClient()
    client_output = client
    # The stochastic leaf can cite only evidence supplied by the host.
    original_turn = client.structured_turn

    def with_evidence(**kwargs):
        turn = original_turn(**kwargs)
        turn.output["proposals"][0]["evidence_ids"] = [
            request["evidence_refs"][0]["evidence_id"]
        ]
        return turn

    client_output.structured_turn = with_evidence
    queue = ContentAssessmentQueue(db_path, clock=lambda: NOW)
    receipt = ContentAssessmentWorker(
        queue,
        client_output,
        cwd=tmp_path,
    ).run_once(worker_id="assessment-worker")
    assert receipt.accepted is True
    assert len(client.calls) == 1
    assert "Normalized input" in client.calls[0]["prompt"]

    conn = sqlite3.connect(db_path)
    try:
        task_state = conn.execute(
            "SELECT state FROM service_intelligence_tasks"
        ).fetchone()[0]
        batch_state = conn.execute(
            "SELECT state FROM collection_assessment_batches"
        ).fetchone()[0]
    finally:
        conn.close()
    assert task_state == "completed"
    assert batch_state == "completed"
