"""Deterministic orchestration from durable leases to corpus publication."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, replace
from datetime import datetime, timedelta, timezone
from typing import Callable, Mapping, Protocol

from . import service_contracts as contracts
from .service_publication import (
    CorpusEvidenceSnapshot,
    CorpusPublisher,
    PublicationStats,
)
from .service_profiles import ProfilePublisher
from .service_refresh import ServiceRefreshScheduler
from .service_store import ServiceStore
from .service_supervisor import RefreshSupervisor
from .service_worker import (
    COLLECTION_ACCESS_METHOD_ADAPTERS,
    PROFILE_SOURCE_ADAPTERS,
    SOURCE_ADAPTERS,
    SOURCE_COST_RESERVATIONS_CENTS,
    WorkerExecutionError,
)


Clock = Callable[[], datetime]


class AcquisitionRunner(Protocol):
    def run(
        self, request: contracts.AcquisitionWorkRequest
    ) -> contracts.AcquisitionWorkResult: ...


class CollectionRecorder(Protocol):
    def policy_for_job(self, job_id: str) -> Mapping[str, object] | None: ...

    def record_started(
        self,
        *,
        job_id: str,
        worker_id: str,
        lease_generation: int,
        pre_snapshot: Mapping[str, object] | None = None,
    ) -> None: ...

    def record_assessment(
        self,
        *,
        job_id: str,
        acquisition_id: str,
        state: str,
        item_count: int,
        task_id: str | None = None,
        error_code: str | None = None,
    ) -> None: ...

    def record_completion(
        self,
        *,
        job_id: str,
        state: str,
        outcomes: tuple[Mapping[str, object], ...],
        completed_at: datetime,
        pre_snapshot: Mapping[str, object],
        post_snapshot: Mapping[str, object],
    ) -> None: ...


class AssessmentQueue(Protocol):
    def enqueue_for_acquisition(
        self,
        *,
        job_id: str,
        acquisition_id: str,
        item_limit: int = 20,
        max_cost_cents: int = 5,
    ): ...


@dataclass(frozen=True)
class JobRunnerPolicy:
    lease_seconds: int = 300
    wall_timeout_seconds: int = 120
    item_limit: int = 100
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
    publication: PublicationStats
    indexed_count: int = 0


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
        collection_coordinator: CollectionRecorder | None = None,
        assessment_queue: AssessmentQueue | None = None,
        profile_publisher: ProfilePublisher | None = None,
    ) -> None:
        self.supervisor = supervisor
        self.ledger = ledger
        self.publisher = publisher
        self.worker = worker
        self.scheduler = scheduler
        self.policy = policy
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self.collection_coordinator = collection_coordinator
        self.assessment_queue = assessment_queue
        self.profile_publisher = profile_publisher

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

    @staticmethod
    def _failure_is_retryable(
        outcome: _Outcome,
        collection_policy: Mapping[str, object] | None,
    ) -> bool:
        generic_retryable = outcome.result.retry_class in {
            contracts.RetryClass.RATE_LIMIT,
            contracts.RetryClass.TRANSIENT,
            contracts.RetryClass.CONTENT,
        }
        if not collection_policy or not collection_policy.get(
            "_manual_retry_budget", False
        ):
            return generic_retryable
        return (
            outcome.result.retry_class is contracts.RetryClass.TRANSIENT
            and outcome.result.safe_error_code
            in {
                "agent_browser_error",
                "agent_browser_timeout",
                "route_stale",
                "worker_timeout",
            }
            and outcome.result.accepted_count == 0
            and outcome.publication.stored_count == 0
            and outcome.publication.deduplicated_count == 0
            and outcome.indexed_count == 0
        )

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
                "diagnostics": {
                    "attempted_access_methods": [],
                    "selected_access_method": None,
                    "adapter_variant": request.adapter,
                },
                "network_request_count": 0,
                "attempted_count": 0,
                "observed_count": 0,
                "accepted_count": 0,
                "rejected_count": 0,
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

    @classmethod
    def _collection_outcome(
        cls,
        outcome: _Outcome,
        collection_policy: Mapping[str, object] | None,
    ) -> dict[str, object]:
        diagnostics = outcome.result.diagnostics
        attempted = (
            outcome.result.attempted_count
            if outcome.result.attempted_count is not None
            else outcome.result.item_count
        )
        attempted_methods = diagnostics.get("attempted_access_methods")
        if not isinstance(attempted_methods, list) or not all(
            isinstance(item, str) for item in attempted_methods
        ):
            attempted_methods = []
        payload: dict[str, object] = {
            "source": outcome.result.source,
            "status": outcome.result.status.value,
            "attempted_count": attempted,
            "network_request_count": outcome.result.network_request_count,
            "observed_count": (
                outcome.result.observed_count
                if outcome.result.observed_count is not None
                else outcome.result.item_count
            ),
            "accepted_count": (
                outcome.result.accepted_count
                if outcome.result.accepted_count is not None
                else outcome.result.item_count
            ),
            "rejected_count": outcome.result.rejected_count or 0,
            "stored_count": outcome.publication.stored_count,
            "deduplicated_count": outcome.publication.deduplicated_count,
            "indexed_count": outcome.indexed_count,
            "attempted_access_methods": attempted_methods,
            "selected_access_method": diagnostics.get("selected_access_method"),
            "adapter_variant": diagnostics.get("adapter_variant"),
            "cursor_after": diagnostics.get("cursor_after"),
            "watermark_after": diagnostics.get("watermark_after"),
            "retry_after": outcome.retry_after,
            "error_code": outcome.result.safe_error_code,
        }
        if collection_policy and collection_policy.get(
            "_manual_retry_budget", False
        ):
            payload["retry"] = {
                "eligible": cls._failure_is_retryable(
                    outcome, collection_policy
                ),
                "retry_class": outcome.result.retry_class.value,
                "error_code": outcome.result.safe_error_code,
                "accepted_count": outcome.result.accepted_count,
                "stored_count": outcome.publication.stored_count,
                "deduplicated_count": outcome.publication.deduplicated_count,
                "indexed_count": outcome.indexed_count,
            }
        return payload

    def _record_collection_completion(
        self,
        job: contracts.JobRecord,
        outcomes: list[_Outcome],
        *,
        pre_snapshot: CorpusEvidenceSnapshot,
        post_snapshot: CorpusEvidenceSnapshot,
        collection_policy: Mapping[str, object] | None,
    ) -> None:
        if self.collection_coordinator is None:
            return
        self.collection_coordinator.record_completion(
            job_id=job.job_id,
            state=job.state.value,
            outcomes=tuple(
                self._collection_outcome(item, collection_policy)
                for item in outcomes
            ),
            completed_at=self._now(),
            pre_snapshot=pre_snapshot.to_dict(),
            post_snapshot=post_snapshot.to_dict(),
        )

    def run_once(self, *, worker_id: str) -> contracts.JobRecord | None:
        job = self.supervisor.lease_next(
            worker_id=worker_id,
            lease_seconds=self.policy.lease_seconds,
        )
        if job is None:
            return None
        pre_snapshot = self.publisher.evidence_snapshot()
        if self.collection_coordinator is not None:
            self.collection_coordinator.record_started(
                job_id=job.job_id,
                worker_id=worker_id,
                lease_generation=job.lease_generation,
                pre_snapshot=pre_snapshot.to_dict(),
            )
        snapshot = self.supervisor.get_snapshot(job.job_id)
        sources = self._job_sources(job.job_id, snapshot.events)
        envelope = self.ledger.get_envelope(
            contracts.QueryRequest.CONTRACT_NAME,
            job.query_request_id,
        )
        if not isinstance(envelope, contracts.QueryRequest):
            raise RuntimeError("refresh job does not reference a query request")
        query_request = envelope
        collection_policy = (
            self.collection_coordinator.policy_for_job(job.job_id)
            if self.collection_coordinator is not None
            else None
        )
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
            required_access_method = (
                collection_policy.get("required_access_method")
                if collection_policy
                else None
            )
            if required_access_method:
                adapter, adapter_version, reserved_cost = (
                    COLLECTION_ACCESS_METHOD_ADAPTERS.get(
                        (source, str(required_access_method)),
                        (f"{source}_unsupported", "1", 0),
                    )
                )
                if source == "linkedin" and collection_policy.get("surface_kind") == "profile":
                    adapter, adapter_version = PROFILE_SOURCE_ADAPTERS[source]
            else:
                adapter_registry = (
                    PROFILE_SOURCE_ADAPTERS
                    if collection_policy
                    and collection_policy.get("surface_kind") == "profile"
                    else SOURCE_ADAPTERS
                )
                adapter, adapter_version = adapter_registry.get(
                    source,
                    (f"{source}_unsupported", "1"),
                )
                reserved_cost = SOURCE_COST_RESERVATIONS_CENTS.get(source, 0)
            remaining_budget = job.budget_cents - job.spent_cents
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
                    "wall_timeout_seconds": min(
                        self.policy.wall_timeout_seconds,
                        int(
                            collection_policy.get(
                                "wall_timeout_seconds",
                                self.policy.wall_timeout_seconds,
                            )
                        )
                        if collection_policy
                        else self.policy.wall_timeout_seconds,
                    ),
                    "item_limit": min(
                        self.policy.item_limit,
                        query_request.top_k,
                        int(
                            collection_policy.get(
                                "item_limit", self.policy.item_limit
                            )
                        )
                        if collection_policy
                        else self.policy.item_limit,
                    ),
                    "network_request_limit": min(
                        self.policy.network_request_limit,
                        int(
                            collection_policy.get(
                                "network_request_limit",
                                self.policy.network_request_limit,
                            )
                        )
                        if collection_policy
                        else self.policy.network_request_limit,
                    ),
                    "cost_budget_cents": reserved_cost,
                    "surface_kind": str(
                        collection_policy.get("surface_kind", "topic")
                        if collection_policy
                        else "topic"
                    ),
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
                except Exception:
                    result = self._failure_result(
                        work,
                        WorkerExecutionError(
                            "worker_internal_error",
                            contracts.RetryClass.TRANSIENT,
                        ),
                    )
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
            publication = self.publisher.record_result(
                work,
                result,
                worker_id=worker_id,
                retention_class=(
                    str(collection_policy["retention_class"])
                    if collection_policy
                    else None
                ),
                redaction_class=(
                    str(collection_policy["redaction_class"])
                    if collection_policy
                    else None
                ),
            )
            if (
                self.profile_publisher is not None
                and collection_policy
                and collection_policy.get("surface_kind") == "profile"
                and result.status
                in {
                    contracts.AcquisitionStatus.SUCCEEDED,
                    contracts.AcquisitionStatus.PARTIAL,
                }
            ):
                self.profile_publisher.publish_acquisition(result.work_id)
            if (
                self.collection_coordinator is not None
                and self.assessment_queue is not None
                and result.status
                in {
                    contracts.AcquisitionStatus.SUCCEEDED,
                    contracts.AcquisitionStatus.PARTIAL,
                }
            ):
                try:
                    task = self.assessment_queue.enqueue_for_acquisition(
                        job_id=job.job_id,
                        acquisition_id=result.work_id,
                        item_limit=min(result.item_count, self.policy.item_limit),
                    )
                    self.collection_coordinator.record_assessment(
                        job_id=job.job_id,
                        acquisition_id=result.work_id,
                        state="queued" if task is not None else "skipped",
                        item_count=result.item_count,
                        task_id=getattr(task, "task_id", None),
                    )
                except Exception as exc:
                    self.collection_coordinator.record_assessment(
                        job_id=job.job_id,
                        acquisition_id=result.work_id,
                        state="failed",
                        item_count=result.item_count,
                        error_code=type(exc).__name__.casefold(),
                    )
            delay = self._retry_delay(job, source, result)
            retry_after = (
                self._format_time(self._now() + timedelta(seconds=delay))
                if delay is not None
                else None
            )
            outcomes.append(_Outcome(work, result, retry_after, publication))

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
            retryable = self._failure_is_retryable(failure, collection_policy)
            terminal_job = self.supervisor.handle_failure(
                job.job_id,
                error_code=failure.result.safe_error_code or "acquisition_failed",
                retryable=retryable,
                retry_after=failure.retry_after,
                awaiting_operator=operator is not None,
                worker_id=worker_id,
                lease_generation=job.lease_generation,
            )
            self._record_collection_completion(
                terminal_job,
                outcomes,
                pre_snapshot=pre_snapshot,
                post_snapshot=self.publisher.evidence_snapshot(),
                collection_policy=collection_policy,
            )
            return terminal_job

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
        outcomes = [
            replace(
                outcome,
                indexed_count=self.publisher.indexed_item_count(
                    outcome.result.work_id,
                    index_version,
                ),
            )
            for outcome in outcomes
        ]
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
        terminal_job = self.supervisor.transition(
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
        self._record_collection_completion(
            terminal_job,
            outcomes,
            pre_snapshot=pre_snapshot,
            post_snapshot=self.publisher.evidence_snapshot(),
            collection_policy=collection_policy,
        )
        return terminal_job
