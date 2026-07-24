"""End-to-end deterministic job orchestration with injected workers."""

from datetime import datetime, timezone

from lib import service_contracts as contracts
from lib.service_job_runner import AcquisitionJobRunner, JobRunnerPolicy
from lib.service_publication import CorpusPublisher
from lib.service_refresh import RefreshPolicy, ServiceRefreshScheduler
from lib.service_retrieval import HybridRetriever
from lib.service_store import ServiceStore
from lib.service_supervisor import RefreshSupervisor


NOW = datetime(2026, 7, 24, 12, 0, tzinfo=timezone.utc)


def _query(request_id, sources):
    return contracts.QueryRequest.from_dict(
        {
            "schema_version": 1,
            "request_id": request_id,
            "profile_id": "default",
            "query": "agent intelligence service",
            "freshness_policy": "force_refresh",
            "response_mode": "evidence",
            "filters": {"sources": sources},
            "top_k": 8,
            "max_chars": 8192,
            "wait_ms": 0,
        }
    )


class FakeWorker:
    def __init__(self, outcomes):
        self.outcomes = outcomes
        self.requests = []

    def run(self, request):
        self.requests.append(request)
        outcome = self.outcomes[request.source]
        items = outcome.get("items", [])
        return contracts.AcquisitionWorkResult.from_dict(
            {
                "schema_version": 1,
                "work_id": request.work_id,
                "job_id": request.job_id,
                "lease_generation": request.lease_generation,
                "source": request.source,
                "adapter": request.adapter,
                "adapter_version": request.adapter_version,
                "status": outcome["status"],
                "safe_error_code": outcome.get("error_code"),
                "retry_class": outcome.get("retry_class", "none"),
                "retry_after_seconds": outcome.get("retry_after_seconds"),
                "observed_at": "2026-07-24T12:00:00Z",
                "fetched_at": "2026-07-24T12:00:01Z",
                "items": items,
                "item_count": len(items),
                "cost_cents": outcome.get("cost_cents", 0),
                "diagnostics": {"accepted_count": len(items)},
            }
        )


def _runtime(tmp_path, worker, *, budget_cents=50):
    db_path = tmp_path / "research.db"
    supervisor = RefreshSupervisor(db_path, clock=lambda: NOW)
    supervisor.initialize()
    ledger = ServiceStore(db_path)
    retriever = HybridRetriever(db_path)
    scheduler = ServiceRefreshScheduler(
        supervisor,
        ledger,
        RefreshPolicy(
            default_sources=("reddit",),
            freshness_seconds=3600,
            max_attempts=2,
            budget_cents=budget_cents,
        ),
        clock=lambda: NOW,
    )
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
            depth="standard",
            successful_coverage_seconds=3600,
            negative_cache_seconds=300,
        ),
        clock=lambda: NOW,
    )
    return scheduler, supervisor, retriever, runner


def test_one_source_success_and_one_failure_publishes_a_partial_index(tmp_path):
    worker = FakeWorker(
        {
            "x": {
                "status": "succeeded",
                "items": [
                    {
                        "source_native_id": "x-001",
                        "url": "https://x.com/example/status/1",
                        "title": "Agent service",
                        "text": "A cache-backed intelligence service with citations.",
                        "author": "example",
                        "published_at": "2026-07-23T12:00:00Z",
                        "metadata": {},
                    }
                ],
            },
            "youtube": {
                "status": "failed",
                "error_code": "worker_timeout",
                "retry_class": "transient",
                "retry_after_seconds": 30,
            },
        }
    )
    scheduler, supervisor, retriever, runner = _runtime(tmp_path, worker)
    job_id = scheduler.ensure_refresh(_query("query-partial", ["x", "youtube"]))

    completed = runner.run_once(worker_id="service-worker")

    assert completed is not None and completed.job_id == job_id
    assert completed.state is contracts.JobState.PARTIAL
    assert completed.published_index_version is not None
    assert sum(
        event.event_type == "lease_renewed"
        for event in supervisor.get_events(job_id)
    ) == 2
    assert [item.source for item in retriever.search("cache-backed")] == ["x"]
    coverage = supervisor.coverage_for(
        query=scheduler.query_scope(_query("query-partial", ["x", "youtube"])),
        profile_id="default",
        sources=["x", "youtube"],
    )
    assert [(item.source, item.status.value) for item in coverage] == [
        ("x", "succeeded"),
        ("youtube", "failed"),
    ]


def test_auth_only_failure_waits_for_operator_without_retry(tmp_path):
    worker = FakeWorker(
        {
            "facebook": {
                "status": "awaiting_operator",
                "error_code": "auth_required",
                "retry_class": "operator",
            }
        }
    )
    scheduler, supervisor, _retriever, runner = _runtime(tmp_path, worker)
    job_id = scheduler.ensure_refresh(_query("query-auth", ["facebook"]))

    completed = runner.run_once(worker_id="service-worker")

    assert completed is not None and completed.job_id == job_id
    assert completed.state is contracts.JobState.AWAITING_OPERATOR
    assert completed.lease_owner is None
    assert supervisor.lease_next(worker_id="other", lease_seconds=60) is None


def test_explicit_empty_success_publishes_fresh_negative_coverage(tmp_path):
    worker = FakeWorker({"reddit": {"status": "succeeded"}})
    scheduler, _supervisor, _retriever, runner = _runtime(tmp_path, worker)
    request = _query("query-empty", ["reddit"])
    scheduler.ensure_refresh(request)

    completed = runner.run_once(worker_id="service-worker")

    assert completed is not None
    assert completed.state is contracts.JobState.PUBLISHED
    prefer_cache = contracts.QueryRequest.from_dict(
        {**request.to_dict(), "request_id": "query-empty-2", "freshness_policy": "prefer_cache"}
    )
    assert scheduler.cache_status(prefer_cache, contracts.CacheStatus.MISS) is contracts.CacheStatus.FRESH
    assert scheduler.ensure_refresh(prefer_cache) is None


def test_all_transient_failures_release_lease_into_bounded_retry(tmp_path):
    worker = FakeWorker(
        {
            "youtube": {
                "status": "failed",
                "error_code": "worker_timeout",
                "retry_class": "transient",
            }
        }
    )
    scheduler, supervisor, _retriever, runner = _runtime(tmp_path, worker)
    job_id = scheduler.ensure_refresh(_query("query-retry", ["youtube"]))

    completed = runner.run_once(worker_id="service-worker")

    assert completed is not None and completed.job_id == job_id
    assert completed.state is contracts.JobState.QUEUED
    assert completed.attempts == 1
    assert completed.not_before_at is not None
    assert completed.lease_owner is None
    assert supervisor.lease_next(worker_id="early-worker", lease_seconds=60) is None


def test_host_budget_reservation_prevents_paid_backup_launch(tmp_path):
    worker = FakeWorker({"reddit": {"status": "succeeded"}})
    scheduler, _supervisor, _retriever, runner = _runtime(
        tmp_path, worker, budget_cents=0
    )
    scheduler.ensure_refresh(_query("query-no-budget", ["reddit"]))

    completed = runner.run_once(worker_id="service-worker")

    assert completed is not None
    assert completed.state is contracts.JobState.FAILED
    assert completed.error_code == "budget_exhausted"
    assert worker.requests == []
