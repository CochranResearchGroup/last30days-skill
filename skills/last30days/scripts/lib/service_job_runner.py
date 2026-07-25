"""Deterministic orchestration from durable leases to corpus publication."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Callable, Protocol

from . import service_contracts as contracts
from .service_publication import CorpusPublisher
from .service_refresh import ServiceRefreshScheduler
from .service_store import ServiceStore
from .service_supervisor import RefreshSupervisor
from .service_worker import (
    SOURCE_ADAPTERS,
    SOURCE_COST_RESERVATIONS_CENTS,
    WorkerExecutionError,
)


Clock = Callable[[], datetime]


class AcquisitionRunner(Protocol):
    def run(
        self, request: contracts.AcquisitionWorkRequest
    ) -> contracts.AcquisitionWorkResult: ...


@dataclass(frozen=True)
class JobRunnerPolicy:
    lease_seconds: int = 300
    wall_timeout_seconds: int = 120
    item_limit: int = 50
    network_request_limit: int = 100
    depth: str = "standard"
    successful_coverage_seconds: int = 86_400
    negative_cache_seconds: int = 300

    def __post_init__(self) -> None:
        if not 1 <= self.lease_seconds <= 86_400:
            raise ValueError("lease_seconds must be between 1 and 86400")
        if not 1 <= self.wall_timeout_seconds <= 3600:
            raise ValueError("wall_timeout_seconds must be between 1 and 3600")
        if self.lease_seconds <= self.wall_timeout_seconds:
            raise ValueError("lease_seconds must exceed wall_timeout_seconds")
        if not 1 <= self.item_limit <= 10_000:
            raise ValueError("item_limit must be between 1 and 10000")
        if not 0 <= self.network_request_limit <= 100_000:
            raise ValueError(
                "network_request_limit must be between 0 and 100000"
            )
        if self.depth not in {"quick", "standard", "deep"}:
            raise ValueError("depth must be quick, standard, or deep")
        if not 1 <= self.successful_coverage_seconds <= 31_536_000:
            raise ValueError("successful_coverage_seconds is outside limits")
        if not 1 <= self.negative_cache_seconds <= 86_400:
            raise ValueError("negative_cache_seconds is outside limits")


@dataclass(frozen=True)
class _Outcome:
    request: contracts.AcquisitionWorkRequest
    result: contracts.AcquisitionWorkResult
    retry_after: str | None


class AcquisitionJobRunner:
    """Run at most one durable refresh job through the host state machine."""

    def __init__(
        self,
        supervisor: RefreshSupervisor,
        ledger: ServiceStore,
        publisher: CorpusPublisher,
        worker: AcquisitionRunner,
        scheduler: ServiceRefreshScheduler,
        policy: JobRunnerPolicy = JobRunnerPolicy(),
        *,
        clock: Clock | None = None,
    ) -> None:
        self.supervisor = supervisor
        self.ledger = ledger
        self.publisher = publisher
        self.worker = worker
        self.scheduler = scheduler
        self.policy = policy
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    def _now(self) -> datetime:
        value = self._clock()
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("clock must return a timezone-aware datetime")
        return value.astimezone(timezone.utc)

    def cancel_active_work(self) -> None:
        cancel = getattr(self.worker, "cancel_all", None)
        if callable(cancel):
            cancel()

    @staticmethod
    def _format_time(value: datetime) -> str:
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")

    @staticmethod
    def _parse_time(value: str) -> datetime:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            raise ValueError("worker timestamps must include a timezone")
        return parsed.astimezone(timezone.utc)

    @staticmethod
    def _job_sources(job_id: str, events: tuple[contracts.JobEvent, ...]) -> tuple[str, ...]:
        for event in events:
            if event.event_type == "job_enqueued":
                sources = event.payload.get("sources")
                if isinstance(sources, list) and all(
                    isinstance(source, str) and source for source in sources
                ):
                    return tuple(sources)
        raise RuntimeError(f"job {job_id} has no replayable source set")

    @staticmethod
    def _work_id(job_id: str, lease_generation: int, source: str) -> str:
        digest = hashlib.sha256(
            f"{job_id}:{lease_generation}:{source}".encode("utf-8")
        ).hexdigest()
        return f"work-{digest[:32]}"

    @staticmethod
    def _date_range(
        request: contracts.QueryRequest, now: datetime
    ) -> tuple[str, str]:
        from_value = request.filters.get("published_after")
        to_value = request.filters.get("published_before")
        from_date = (
            str(from_value).split("T", 1)[0]
            if from_value
            else (now - timedelta(days=30)).date().isoformat()
        )
        to_date = (
            str(to_value).split("T", 1)[0]
            if to_value
            else now.date().isoformat()
        )
        return from_date, to_date

    def _retry_delay(
        self,
        job: contracts.JobRecord,
        source: str,
        result: contracts.AcquisitionWorkResult,
    ) -> int | None:
        if result.retry_class in {
            contracts.RetryClass.OPERATOR,
            contracts.RetryClass.CONFIGURATION,
            contracts.RetryClass.PERMANENT,
            contracts.RetryClass.NONE,
        }:
            return (
                self.policy.negative_cache_seconds
                if result.retry_class is contracts.RetryClass.OPERATOR
                else None
            )
        if result.retry_after_seconds is not None:
            return result.retry_after_seconds
        base = (
            self.policy.negative_cache_seconds
            if result.retry_class is contracts.RetryClass.RATE_LIMIT
            else min(3600, 30 * (2 ** max(0, job.attempts - 1)))
        )
        jitter_bound = max(1, base // 10)
        jitter = int(
            hashlib.sha256(
                f"{job.job_id}:{job.attempts}:{source}".encode("utf-8")
            ).hexdigest()[:8],
            16,
        ) % jitter_bound
        return min(86_400, base + jitter)

    def _failure_result(
        self,
        request: contracts.AcquisitionWorkRequest,
        failure: WorkerExecutionError,
    ) -> contracts.AcquisitionWorkResult:
        now = self._format_time(self._now())
        status = (
            contracts.AcquisitionStatus.AWAITING_OPERATOR
            if failure.retry_class is contracts.RetryClass.OPERATOR
            else contracts.AcquisitionStatus.FAILED
        )
        return contracts.AcquisitionWorkResult.from_dict(
            {
                "schema_version": contracts.SCHEMA_VERSION,
                "work_id": request.work_id,
                "job_id": request.job_id,
                "lease_generation": request.lease_generation,
                "source": request.source,
                "adapter": request.adapter,
                "adapter_version": request.adapter_version,
                "status": status.value,
                "safe_error_code": failure.code,
                "retry_class": failure.retry_class.value,
                "retry_after_seconds": failure.retry_after_seconds,
                "observed_at": now,
                "fetched_at": now,
                "items": [],
                "item_count": 0,
                "cost_cents": 0,
                "diagnostics": {},
            }
        )

    def _record_coverage(
        self,
        job: contracts.JobRecord,
        query_request: contracts.QueryRequest,
        outcome: _Outcome,
        *,
        worker_id: str,
        index_version: str | None,
    ) -> None:
        fetched = self._parse_time(outcome.result.fetched_at)
        if outcome.result.status in {
            contracts.AcquisitionStatus.SUCCEEDED,
            contracts.AcquisitionStatus.PARTIAL,
        }:
            fresh_until = fetched + timedelta(
                seconds=self.policy.successful_coverage_seconds
            )
        else:
            fresh_until = fetched
        self.supervisor.record_coverage(
            job.job_id,
            query=self.scheduler.query_scope(query_request),
            profile_id=query_request.profile_id,
            source=outcome.result.source,
            status=outcome.result.status,
            fetched_at=outcome.result.fetched_at,
            fresh_until=self._format_time(fresh_until),
            retry_after=outcome.retry_after,
            worker_id=worker_id,
            lease_generation=job.lease_generation,
            index_version=index_version,
            error_code=outcome.result.safe_error_code,
        )

    def run_once(self, *, worker_id: str) -> contracts.JobRecord | None:
        job = self.supervisor.lease_next(
            worker_id=worker_id,
            lease_seconds=self.policy.lease_seconds,
        )
        if job is None:
            return None
        snapshot = self.supervisor.get_snapshot(job.job_id)
        sources = self._job_sources(job.job_id, snapshot.events)
        envelope = self.ledger.get_envelope(
            contracts.QueryRequest.CONTRACT_NAME,
            job.query_request_id,
        )
        if not isinstance(envelope, contracts.QueryRequest):
            raise RuntimeError("refresh job does not reference a query request")
        query_request = envelope
        job = self.supervisor.transition(
            job.job_id,
            to_state=contracts.JobState.ACQUIRING,
            worker_id=worker_id,
            lease_generation=job.lease_generation,
        )
        from_date, to_date = self._date_range(query_request, self._now())
        outcomes: list[_Outcome] = []
        for source in sources:
            job = self.supervisor.renew_lease(
                job.job_id,
                worker_id=worker_id,
                lease_generation=job.lease_generation,
                lease_seconds=self.policy.lease_seconds,
            )
            adapter, adapter_version = SOURCE_ADAPTERS.get(
                source,
                (f"{source}_unsupported", "1"),
            )
            remaining_budget = job.budget_cents - job.spent_cents
            reserved_cost = SOURCE_COST_RESERVATIONS_CENTS.get(source, 0)
            work = contracts.AcquisitionWorkRequest.from_dict(
                {
                    "schema_version": contracts.SCHEMA_VERSION,
                    "work_id": self._work_id(
                        job.job_id, job.lease_generation, source
                    ),
                    "job_id": job.job_id,
                    "lease_generation": job.lease_generation,
                    "attempt": job.attempts,
                    "profile_id": query_request.profile_id,
                    "source": source,
                    "query": query_request.query,
                    "from_date": from_date,
                    "to_date": to_date,
                    "depth": self.policy.depth,
                    "adapter": adapter,
                    "adapter_version": adapter_version,
                    "wall_timeout_seconds": self.policy.wall_timeout_seconds,
                    "item_limit": min(self.policy.item_limit, query_request.top_k),
                    "network_request_limit": self.policy.network_request_limit,
                    "cost_budget_cents": reserved_cost,
                }
            )
            if reserved_cost > remaining_budget:
                result = self._failure_result(
                    work,
                    WorkerExecutionError(
                        "budget_exhausted",
                        contracts.RetryClass.PERMANENT,
                    ),
                )
            else:
                if reserved_cost:
                    job = self.supervisor.record_spend(
                        job.job_id,
                        amount_cents=reserved_cost,
                        worker_id=worker_id,
                        lease_generation=job.lease_generation,
                    )
                try:
                    result = self.worker.run(work)
                except WorkerExecutionError as failure:
                    result = self._failure_result(work, failure)
            if self._parse_time(result.fetched_at) > self._now() + timedelta(
                minutes=5
            ):
                result = self._failure_result(
                    work,
                    WorkerExecutionError(
                        "validator_failed",
                        contracts.RetryClass.PERMANENT,
                    ),
                )
            self.publisher.record_result(work, result, worker_id=worker_id)
            delay = self._retry_delay(job, source, result)
            retry_after = (
                self._format_time(self._now() + timedelta(seconds=delay))
                if delay is not None
                else None
            )
            outcomes.append(_Outcome(work, result, retry_after))

        completed = [
            outcome
            for outcome in outcomes
            if outcome.result.status
            in {
                contracts.AcquisitionStatus.SUCCEEDED,
                contracts.AcquisitionStatus.PARTIAL,
            }
        ]
        if not completed:
            for outcome in outcomes:
                self._record_coverage(
                    job,
                    query_request,
                    outcome,
                    worker_id=worker_id,
                    index_version=None,
                )
            operator = next(
                (
                    outcome
                    for outcome in outcomes
                    if outcome.result.status
                    is contracts.AcquisitionStatus.AWAITING_OPERATOR
                ),
                None,
            )
            failure = operator or outcomes[0]
            retryable = failure.result.retry_class in {
                contracts.RetryClass.RATE_LIMIT,
                contracts.RetryClass.TRANSIENT,
                contracts.RetryClass.CONTENT,
            }
            return self.supervisor.handle_failure(
                job.job_id,
                error_code=failure.result.safe_error_code or "acquisition_failed",
                retryable=retryable,
                retry_after=failure.retry_after,
                awaiting_operator=operator is not None,
                worker_id=worker_id,
                lease_generation=job.lease_generation,
            )

        job = self.supervisor.transition(
            job.job_id,
            to_state=contracts.JobState.NORMALIZING,
            worker_id=worker_id,
            lease_generation=job.lease_generation,
        )
        job = self.supervisor.transition(
            job.job_id,
            to_state=contracts.JobState.INDEXING,
            worker_id=worker_id,
            lease_generation=job.lease_generation,
        )
        index_version = self.publisher.publish_index()
        for outcome in outcomes:
            self._record_coverage(
                job,
                query_request,
                outcome,
                worker_id=worker_id,
                index_version=index_version,
            )
        job = self.supervisor.transition(
            job.job_id,
            to_state=contracts.JobState.VALIDATING,
            worker_id=worker_id,
            lease_generation=job.lease_generation,
        )
        is_partial = any(
            outcome.result.status is not contracts.AcquisitionStatus.SUCCEEDED
            for outcome in outcomes
        )
        terminal = (
            contracts.JobState.PARTIAL
            if is_partial
            else contracts.JobState.PUBLISHED
        )
        error_code = next(
            (
                outcome.result.safe_error_code
                for outcome in outcomes
                if outcome.result.safe_error_code
            ),
            None,
        )
        return self.supervisor.transition(
            job.job_id,
            to_state=terminal,
            worker_id=worker_id,
            lease_generation=job.lease_generation,
            published_index_version=index_version,
            error_code=error_code,
            payload={
                "source_count": len(outcomes),
                "successful_source_count": len(completed),
            },
        )
