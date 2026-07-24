"""Behavior tests for the durable deterministic refresh supervisor."""

from __future__ import annotations

import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

import pytest

from lib import service_contracts
from lib.service_supervisor import (
    BudgetExceededError,
    InvalidTransitionError,
    LeaseError,
    RefreshSupervisor,
)


NOW = datetime(2026, 7, 24, 12, 0, tzinfo=timezone.utc)


def _supervisor(tmp_path) -> RefreshSupervisor:
    supervisor = RefreshSupervisor(tmp_path / "research.db", clock=lambda: NOW)
    supervisor.initialize()
    return supervisor


class MutableClock:
    def __init__(self, value: datetime):
        self.value = value

    def __call__(self) -> datetime:
        return self.value


def test_concurrent_equivalent_refreshes_coalesce_to_one_durable_job(tmp_path):
    supervisor = _supervisor(tmp_path)
    barrier = threading.Barrier(2)

    def enqueue(request_id, query, sources, profile_id):
        barrier.wait()
        return supervisor.enqueue_refresh(
            query_request_id=request_id,
            query=query,
            sources=sources,
            profile_id=profile_id,
            freshness_window_seconds=3600,
            max_attempts=3,
            budget_cents=250,
        )

    with ThreadPoolExecutor(max_workers=2) as pool:
        first_future = pool.submit(
            enqueue,
            "request-1",
            "  Agent   Browser Profiles ",
            ["YouTube", "x", "youtube"],
            "Primary",
        )
        second_future = pool.submit(
            enqueue,
            "request-2",
            "agent browser profiles",
            ["X", "YOUTUBE"],
            "primary",
        )
        first, second = first_future.result(), second_future.result()

    assert {first.created, second.created} == {True, False}
    assert second.job == first.job
    assert first.job.state is service_contracts.JobState.QUEUED
    assert first.job.attempts == 0
    assert first.job.spent_cents == 0
    snapshot = supervisor.get_snapshot(first.job.job_id)
    assert [event.event_type for event in snapshot.events] == ["job_enqueued"]
    assert snapshot.remaining_budget_cents == 250


def test_expired_lease_is_reclaimed_with_fencing_and_sequenced_replay(tmp_path):
    clock = MutableClock(NOW)
    supervisor = RefreshSupervisor(tmp_path / "research.db", clock=clock)
    supervisor.initialize()
    queued = supervisor.enqueue_refresh(
        query_request_id="request-lease",
        query="browser broker",
        sources=["x"],
        profile_id="primary",
        freshness_window_seconds=3600,
        max_attempts=2,
        budget_cents=100,
    ).job

    first = supervisor.lease_next(worker_id="worker-a", lease_seconds=30)
    assert first is not None
    assert first.job_id == queued.job_id
    assert first.state is service_contracts.JobState.PLANNING
    assert first.attempts == 1
    assert first.lease_generation == 1
    supervisor.transition(
        first.job_id,
        to_state=service_contracts.JobState.ACQUIRING,
        worker_id="worker-a",
        lease_generation=first.lease_generation,
    )

    clock.value = NOW.replace(minute=1)
    reclaimed = supervisor.lease_next(worker_id="worker-b", lease_seconds=30)
    assert reclaimed is not None
    assert reclaimed.job_id == first.job_id
    assert reclaimed.attempts == 2
    assert reclaimed.lease_generation == 2
    with pytest.raises(LeaseError):
        supervisor.transition(
            first.job_id,
            to_state=service_contracts.JobState.ACQUIRING,
            worker_id="worker-a",
            lease_generation=first.lease_generation,
        )

    events = supervisor.get_events(first.job_id)
    assert [event.sequence for event in events] == list(range(1, len(events) + 1))
    assert [event.event_type for event in events] == [
        "job_enqueued",
        "lease_acquired",
        "state_transitioned",
        "lease_expired",
        "lease_acquired",
    ]


def test_state_machine_and_budget_are_enforced_atomically(tmp_path):
    supervisor = _supervisor(tmp_path)
    supervisor.enqueue_refresh(
        query_request_id="request-budget",
        query="youtube transcripts",
        sources=["youtube"],
        profile_id="primary",
        freshness_window_seconds=600,
        max_attempts=1,
        budget_cents=75,
    )
    leased = supervisor.lease_next(worker_id="worker-a", lease_seconds=60)
    assert leased is not None
    renewed = supervisor.renew_lease(
        leased.job_id,
        worker_id="worker-a",
        lease_generation=leased.lease_generation,
        lease_seconds=120,
    )
    assert renewed.lease_generation == leased.lease_generation
    assert renewed.lease_expires_at == "2026-07-24T12:02:00Z"

    with pytest.raises(InvalidTransitionError):
        supervisor.transition(
            leased.job_id,
            to_state=service_contracts.JobState.INDEXING,
            worker_id="worker-a",
            lease_generation=leased.lease_generation,
        )
    spent = supervisor.record_spend(
        leased.job_id,
        amount_cents=50,
        worker_id="worker-a",
        lease_generation=leased.lease_generation,
    )
    assert spent.spent_cents == 50
    with pytest.raises(BudgetExceededError):
        supervisor.record_spend(
            leased.job_id,
            amount_cents=26,
            worker_id="worker-a",
            lease_generation=leased.lease_generation,
        )

    snapshot = supervisor.get_snapshot(leased.job_id)
    assert snapshot.job.state is service_contracts.JobState.PLANNING
    assert snapshot.remaining_budget_cents == 25
    assert [event.event_type for event in snapshot.events] == [
        "job_enqueued",
        "lease_acquired",
        "lease_renewed",
        "budget_spent",
    ]


def test_negative_cache_blocks_only_sources_inside_retry_window(tmp_path):
    clock = MutableClock(NOW)
    supervisor = RefreshSupervisor(tmp_path / "research.db", clock=clock)
    supervisor.initialize()
    supervisor.enqueue_refresh(
        query_request_id="request-negative",
        query="authenticated timelines",
        sources=["x"],
        profile_id="primary",
        freshness_window_seconds=300,
        max_attempts=2,
        budget_cents=0,
    )
    leased = supervisor.lease_next(worker_id="worker-a", lease_seconds=120)
    assert leased is not None
    leased = supervisor.transition(
        leased.job_id,
        to_state=service_contracts.JobState.ACQUIRING,
        worker_id="worker-a",
        lease_generation=leased.lease_generation,
    )
    supervisor.record_coverage(
        leased.job_id,
        query="  Authenticated   Timelines ",
        profile_id="PRIMARY",
        source="X",
        status=service_contracts.AcquisitionStatus.FAILED,
        fetched_at="2026-07-24T12:00:00Z",
        fresh_until="2026-07-24T12:00:00Z",
        retry_after="2026-07-24T12:10:00Z",
        error_code="rate_limited",
        worker_id="worker-a",
        lease_generation=leased.lease_generation,
    )
    coverage = supervisor.coverage_for(
        query="authenticated timelines",
        profile_id="primary",
        sources=["youtube", "x"],
    )
    assert [(item.source, item.status.value) for item in coverage] == [
        ("x", "failed")
    ]

    hits = supervisor.negative_cache_hits(
        query="authenticated timelines",
        profile_id="primary",
        sources=["youtube", "x"],
    )
    assert [(hit.source, hit.error_code) for hit in hits] == [
        ("x", "rate_limited")
    ]

    clock.value = NOW.replace(minute=11)
    assert (
        supervisor.negative_cache_hits(
            query="authenticated timelines",
            profile_id="primary",
            sources=["x"],
        )
        == ()
    )


def test_retry_taxonomy_schedules_backoff_and_maps_auth_to_operator_wait(tmp_path):
    clock = MutableClock(NOW)
    supervisor = RefreshSupervisor(tmp_path / "research.db", clock=clock)
    supervisor.initialize()
    supervisor.enqueue_refresh(
        query_request_id="request-retry",
        query="x timeline",
        sources=["x"],
        profile_id="primary",
        freshness_window_seconds=300,
        max_attempts=3,
        budget_cents=0,
    )
    first = supervisor.lease_next(worker_id="worker-a", lease_seconds=60)
    assert first is not None
    retry = supervisor.handle_failure(
        first.job_id,
        error_code="upstream_timeout",
        retryable=True,
        retry_after="2026-07-24T12:05:00Z",
        awaiting_operator=False,
        worker_id="worker-a",
        lease_generation=first.lease_generation,
    )
    assert retry.state is service_contracts.JobState.QUEUED
    assert retry.not_before_at == "2026-07-24T12:05:00Z"
    assert supervisor.lease_next(worker_id="worker-b", lease_seconds=60) is None

    clock.value = NOW.replace(minute=5)
    second = supervisor.lease_next(worker_id="worker-b", lease_seconds=60)
    assert second is not None
    waiting = supervisor.handle_failure(
        second.job_id,
        error_code="authentication_required",
        retryable=False,
        retry_after=None,
        awaiting_operator=True,
        worker_id="worker-b",
        lease_generation=second.lease_generation,
    )
    assert waiting.state is service_contracts.JobState.AWAITING_OPERATOR
    assert waiting.lease_owner is None
    resumed = supervisor.resume_after_operator(waiting.job_id)
    assert resumed.state is service_contracts.JobState.QUEUED
    assert resumed.error_code is None
    third = supervisor.lease_next(worker_id="worker-c", lease_seconds=60)
    assert third is not None
    exhausted = supervisor.handle_failure(
        third.job_id,
        error_code="upstream_timeout",
        retryable=True,
        retry_after="2026-07-24T12:06:00Z",
        awaiting_operator=False,
        worker_id="worker-c",
        lease_generation=third.lease_generation,
    )
    assert exhausted.state is service_contracts.JobState.FAILED
    assert exhausted.attempts == exhausted.max_attempts == 3
    assert supervisor.lease_next(worker_id="worker-d", lease_seconds=60) is None
