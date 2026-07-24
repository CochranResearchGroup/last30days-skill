"""Application-facing refresh policy over the durable supervisor."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable

from . import service_contracts as contracts
from .service_store import ServiceStore
from .service_supervisor import RefreshSupervisor, normalize_sources


Clock = Callable[[], datetime]


@dataclass(frozen=True)
class RefreshPolicy:
    default_sources: tuple[str, ...]
    freshness_seconds: int = 86_400
    max_attempts: int = 2
    budget_cents: int = 100

    def __post_init__(self) -> None:
        normalize_sources(self.default_sources)
        if not 1 <= self.freshness_seconds <= 31_536_000:
            raise ValueError("freshness_seconds must be between 1 and 31536000")
        if not 1 <= self.max_attempts <= 100:
            raise ValueError("max_attempts must be between 1 and 100")
        if not 0 <= self.budget_cents <= 10_000_000:
            raise ValueError("budget_cents must be between 0 and 10000000")


class ServiceRefreshScheduler:
    """Translate query semantics into durable, coalesced refresh work."""

    def __init__(
        self,
        supervisor: RefreshSupervisor,
        ledger: ServiceStore,
        policy: RefreshPolicy,
        *,
        clock: Clock | None = None,
    ) -> None:
        self.supervisor = supervisor
        self.ledger = ledger
        self.policy = policy
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    def _now(self) -> datetime:
        value = self._clock()
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("clock must return a timezone-aware datetime")
        return value.astimezone(timezone.utc)

    @staticmethod
    def _parse_time(value: str) -> datetime:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            raise ValueError("coverage timestamps must include a timezone")
        return parsed.astimezone(timezone.utc)

    def sources_for(self, request: contracts.QueryRequest) -> tuple[str, ...]:
        requested = request.filters.get("sources")
        return normalize_sources(requested or self.policy.default_sources)

    @staticmethod
    def query_scope(request: contracts.QueryRequest) -> str:
        """Include non-source filters in refresh identity without changing search text."""
        scope_filters = {
            key: value
            for key, value in request.filters.items()
            if key != "sources"
        }
        query = " ".join(request.query.split())
        if not scope_filters:
            return query
        encoded = json.dumps(
            scope_filters,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        )
        digest = hashlib.sha256(encoded.encode("utf-8")).hexdigest()[:16]
        return f"{query}\nfilter-scope:{digest}"

    def _coverage_map(
        self, request: contracts.QueryRequest
    ) -> dict[str, object]:
        sources = self.sources_for(request)
        return {
            record.source: record
            for record in self.supervisor.coverage_for(
                query=self.query_scope(request),
                profile_id=request.profile_id,
                sources=sources,
            )
        }

    def cache_status(
        self,
        request: contracts.QueryRequest,
        fallback: contracts.CacheStatus,
    ) -> contracts.CacheStatus:
        sources = self.sources_for(request)
        coverage = self._coverage_map(request)
        now = self._now()
        if not coverage:
            return fallback
        if len(coverage) == len(sources) and all(
            record.status
            in {
                contracts.AcquisitionStatus.SUCCEEDED,
                contracts.AcquisitionStatus.PARTIAL,
            }
            and self._parse_time(record.fresh_until) > now
            for record in coverage.values()
        ):
            return contracts.CacheStatus.FRESH
        if fallback is contracts.CacheStatus.FRESH:
            return contracts.CacheStatus.STALE
        return fallback

    def ensure_refresh(self, request: contracts.QueryRequest) -> str | None:
        """Persist the request, then create or join only currently eligible work."""
        self.ledger.put_envelope(
            contracts.QueryRequest.CONTRACT_NAME,
            request.request_id,
            request,
        )
        sources = self.sources_for(request)
        if request.freshness_policy is contracts.FreshnessPolicy.FORCE_REFRESH:
            eligible = sources
        else:
            now = self._now()
            coverage = self._coverage_map(request)
            eligible_items: list[str] = []
            for source in sources:
                record = coverage.get(source)
                if record is None:
                    eligible_items.append(source)
                    continue
                successful_and_fresh = (
                    record.status
                    in {
                        contracts.AcquisitionStatus.SUCCEEDED,
                        contracts.AcquisitionStatus.PARTIAL,
                    }
                    and self._parse_time(record.fresh_until) > now
                )
                negative_gate_active = (
                    record.status
                    in {
                        contracts.AcquisitionStatus.FAILED,
                        contracts.AcquisitionStatus.AWAITING_OPERATOR,
                    }
                    and record.retry_after is not None
                    and self._parse_time(record.retry_after) > now
                )
                if not successful_and_fresh and not negative_gate_active:
                    eligible_items.append(source)
            eligible = tuple(eligible_items)
        if not eligible:
            return None
        result = self.supervisor.enqueue_refresh(
            query_request_id=request.request_id,
            query=self.query_scope(request),
            sources=eligible,
            profile_id=request.profile_id,
            freshness_window_seconds=self.policy.freshness_seconds,
            max_attempts=self.policy.max_attempts,
            budget_cents=self.policy.budget_cents,
        )
        return result.job.job_id
