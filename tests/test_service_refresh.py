"""Service-level refresh scheduling and coverage-policy tests."""

from datetime import datetime, timezone

from lib import service_contracts as contracts
from lib.service_refresh import RefreshPolicy, ServiceRefreshScheduler
from lib.service_store import ServiceStore
from lib.service_supervisor import RefreshSupervisor


NOW = datetime(2026, 7, 24, 12, 0, tzinfo=timezone.utc)


def _request(request_id="query-001", **overrides):
    values = {
        "schema_version": 1,
        "request_id": request_id,
        "profile_id": "default",
        "query": "cache service",
        "freshness_policy": "prefer_cache",
        "response_mode": "evidence",
        "filters": {"sources": ["x", "youtube"]},
        "top_k": 8,
        "max_chars": 8192,
        "wait_ms": 0,
    }
    values.update(overrides)
    return contracts.QueryRequest.from_dict(values)


def _scheduler(tmp_path):
    db_path = tmp_path / "research.db"
    supervisor = RefreshSupervisor(db_path, clock=lambda: NOW)
    supervisor.initialize()
    return (
        ServiceRefreshScheduler(
            supervisor,
            ServiceStore(db_path),
            RefreshPolicy(
                default_sources=("reddit",),
                freshness_seconds=3600,
                max_attempts=2,
                budget_cents=50,
            ),
            clock=lambda: NOW,
        ),
        supervisor,
    )


def test_scheduler_persists_request_and_coalesces_equivalent_refreshes(tmp_path):
    scheduler, supervisor = _scheduler(tmp_path)
    first = _request("query-001")
    second = _request("query-002", query="  CACHE   SERVICE ")

    first_job = scheduler.ensure_refresh(first)
    second_job = scheduler.ensure_refresh(second)

    assert first_job == second_job
    assert first_job is not None
    assert supervisor.get_job(first_job).state is contracts.JobState.QUEUED
    restored = scheduler.ledger.get_envelope("query_request", "query-001")
    assert restored.to_dict() == first.to_dict()


def test_fresh_successful_coverage_marks_empty_cache_fresh_and_skips_job(tmp_path):
    scheduler, supervisor = _scheduler(tmp_path)
    request = _request(filters={"sources": ["x"]})
    job_id = scheduler.ensure_refresh(request)
    leased = supervisor.lease_next(worker_id="worker", lease_seconds=60)
    assert leased is not None and leased.job_id == job_id
    leased = supervisor.transition(
        leased.job_id,
        to_state=contracts.JobState.ACQUIRING,
        worker_id="worker",
        lease_generation=leased.lease_generation,
    )
    supervisor.record_coverage(
        leased.job_id,
        query=scheduler.query_scope(request),
        profile_id=request.profile_id,
        source="x",
        status=contracts.AcquisitionStatus.SUCCEEDED,
        fetched_at="2026-07-24T12:00:00Z",
        fresh_until="2026-07-24T13:00:00Z",
        retry_after=None,
        worker_id="worker",
        lease_generation=leased.lease_generation,
    )
    supervisor.transition(
        leased.job_id,
        to_state=contracts.JobState.NORMALIZING,
        worker_id="worker",
        lease_generation=leased.lease_generation,
    )
    supervisor.transition(
        leased.job_id,
        to_state=contracts.JobState.INDEXING,
        worker_id="worker",
        lease_generation=leased.lease_generation,
    )
    supervisor.transition(
        leased.job_id,
        to_state=contracts.JobState.VALIDATING,
        worker_id="worker",
        lease_generation=leased.lease_generation,
    )
    supervisor.transition(
        leased.job_id,
        to_state=contracts.JobState.PUBLISHED,
        worker_id="worker",
        lease_generation=leased.lease_generation,
        published_index_version="index-empty",
    )

    assert (
        scheduler.cache_status(request, contracts.CacheStatus.MISS)
        is contracts.CacheStatus.FRESH
    )
    assert scheduler.ensure_refresh(_request("query-002", filters={"sources": ["x"]})) is None


def test_force_refresh_ignores_fresh_coverage(tmp_path):
    scheduler, _supervisor = _scheduler(tmp_path)
    request = _request(
        freshness_policy="force_refresh",
        filters={"sources": ["x"]},
    )

    assert scheduler.ensure_refresh(request) is not None
