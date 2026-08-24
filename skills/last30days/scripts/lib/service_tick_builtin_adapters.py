"""Bridge installed isolated acquisition workers into durable tick providers."""

from __future__ import annotations

import base64
from datetime import datetime
from collections.abc import Mapping

from . import service_contracts as contracts
from .service_tick_adapters import AdapterRegistry, AdapterSpec
from .service_worker import WorkerExecutionError
from .service_tick_runner import (
    CollectedItem,
    CollectedMedia,
    ProviderContext,
    ProviderResult,
)


_ADAPTERS = {
    "x_agent_browser": ("x", "1"),
    "facebook_agent_browser": ("facebook", "1"),
    "linkedin_agent_browser": ("linkedin", "1"),
    "linkedin_profile_agent_browser": ("linkedin", "1"),
    "youtube_ytdlp": ("youtube", "1"),
    "reddit_keyless": ("reddit", "1"),
    "reddit_agent_browser": ("reddit", "1"),
    "reddit_scrapecreators": ("reddit", "1"),
}


def _normalization_proof_ref(adapter: str) -> str:
    return (
        "fixture:tests/test_service_tick_runtime.py:"
        "test_installed_worker_adapters_preserve_nonzero_normalized_items:"
        f"{adapter}"
    )


def _selector_text(context: ProviderContext) -> str:
    for field in ("query", "topic", "feed", "url", "handle"):
        value = context.selector.get(field)
        if isinstance(value, str) and value.strip():
            return value.strip()
    raise ValueError("target selector requires query, topic, feed, url, or handle")


def _retry_failure_class(retry_class: contracts.RetryClass) -> str:
    return {
        contracts.RetryClass.OPERATOR: "authentication",
        contracts.RetryClass.RATE_LIMIT: "rate_limit",
        contracts.RetryClass.CONFIGURATION: "configuration",
        contracts.RetryClass.CONTENT: "policy",
        contracts.RetryClass.PERMANENT: "permanent",
        contracts.RetryClass.TRANSIENT: "transient",
        contracts.RetryClass.NONE: "permanent",
    }[retry_class]


def _failure_class(result: contracts.AcquisitionWorkResult) -> str:
    if result.safe_error_code in {"captcha_required", "checkpoint_required"}:
        return "challenge"
    return _retry_failure_class(result.retry_class)


def _wall_seconds(result: contracts.AcquisitionWorkResult) -> int:
    observed = datetime.fromisoformat(result.observed_at.replace("Z", "+00:00"))
    fetched = datetime.fromisoformat(result.fetched_at.replace("Z", "+00:00"))
    return max(1, int((fetched - observed).total_seconds()))


def _browser_operations(
    diagnostics: Mapping[str, object],
) -> tuple[dict[str, object], ...]:
    raw_operations = diagnostics.get("browser_operations")
    if not isinstance(raw_operations, list):
        return ()
    operations: list[dict[str, object]] = []
    for raw in raw_operations[:12]:
        if not isinstance(raw, Mapping):
            continue
        operation = raw.get("operation")
        status = raw.get("status")
        duration_ms = raw.get("duration_ms")
        if (
            not isinstance(operation, str)
            or not 0 < len(operation) <= 64
            or status not in {"ok", "failed", "timed_out"}
            or isinstance(duration_ms, bool)
            or not isinstance(duration_ms, int)
            or not 0 <= duration_ms <= 600_000
        ):
            continue
        sanitized: dict[str, object] = {
            "operation": operation,
            "status": status,
            "duration_ms": duration_ms,
        }
        error_type = raw.get("error_type")
        if isinstance(error_type, str) and 0 < len(error_type) <= 64:
            sanitized["error_type"] = error_type
        operations.append(sanitized)
    return tuple(operations)


def _rejection_counts(diagnostics: Mapping[str, object]) -> dict[str, int]:
    raw_counts = diagnostics.get("rejection_counts")
    if not isinstance(raw_counts, Mapping):
        return {}
    counts: dict[str, int] = {}
    for raw_reason, raw_count in list(raw_counts.items())[:32]:
        if (
            not isinstance(raw_reason, str)
            or not 0 < len(raw_reason) <= 64
            or isinstance(raw_count, bool)
            or not isinstance(raw_count, int)
            or not 0 <= raw_count <= 1_000_000
        ):
            continue
        counts[raw_reason] = raw_count
    return counts


def _failure_stage(diagnostics: Mapping[str, object]) -> str | None:
    value = diagnostics.get("failure_stage")
    if not isinstance(value, str):
        return None
    value = value.strip()
    if (
        not value
        or len(value) > 64
        or any(
            character not in "abcdefghijklmnopqrstuvwxyz0123456789_"
            for character in value
        )
    ):
        return None
    return value


def _failure_signature(diagnostics: Mapping[str, object]) -> str | None:
    value = diagnostics.get("failure_signature")
    if not isinstance(value, str) or not value.startswith("sha256:"):
        return None
    digest = value.removeprefix("sha256:")
    if len(digest) != 64 or any(
        character not in "0123456789abcdef" for character in digest
    ):
        return None
    return value


class AcquisitionWorkerTickAdapter:
    def __init__(self, worker, *, adapter: str, adapter_version: str) -> None:
        self.worker = worker
        self.adapter = adapter
        self.adapter_version = adapter_version

    def __call__(self, context: ProviderContext) -> ProviderResult:
        if not isinstance(context, ProviderContext):
            raise TypeError("tick adapter context is invalid")
        profile_id = context.selector.get("profile_id", "default")
        if not isinstance(profile_id, str) or not profile_id.strip():
            raise ValueError("target selector profile_id must be a non-empty string")
        depth = context.selector.get("depth", "standard")
        if depth not in {"quick", "standard", "deep"}:
            raise ValueError("target selector depth is unsupported")
        request = contracts.AcquisitionWorkRequest.from_dict(
            {
                "schema_version": contracts.SCHEMA_VERSION,
                "work_id": f"tick-work:{context.lane_id}:{context.provider_id}",
                "job_id": context.tick_id,
                "lease_generation": 1,
                "attempt": 1,
                "profile_id": profile_id,
                "source": context.source,
                "query": _selector_text(context),
                "from_date": context.interval_from[:10],
                "to_date": context.interval_to[:10],
                "depth": depth,
                "adapter": self.adapter,
                "adapter_version": self.adapter_version,
                "wall_timeout_seconds": context.limits["wall_seconds"],
                "item_limit": max(1, context.limits["items"]),
                "network_request_limit": context.limits["network_requests"],
                "cost_budget_cents": context.limits["cost_cents"],
                "surface_kind": context.surface_kind,
            }
        )
        try:
            result = self.worker.run(request)
        except WorkerExecutionError as exc:
            return ProviderResult.failure(
                failure_class=_retry_failure_class(exc.retry_class),
                safe_error_code=exc.code,
                usage={
                    "attempts": 1,
                    "network_requests": 0,
                    "wall_seconds": (
                        context.limits["wall_seconds"]
                        if exc.code == "worker_timeout"
                        else 0
                    ),
                    "items": 0,
                    "cost_cents": 0,
                    "model_tokens": 0,
                },
            )
        if not isinstance(result, contracts.AcquisitionWorkResult):
            raise TypeError("acquisition worker returned an invalid result")
        items = tuple(
            CollectedItem(
                source_native_id=item.source_native_id,
                url=item.url,
                title=item.title,
                text=item.text,
                author=item.author,
                published_at=item.published_at,
                media=tuple(
                    CollectedMedia(
                        source_url=media.source_url,
                        content=base64.b64decode(
                            media.content_base64, validate=True
                        ),
                        mime_type=media.mime_type,
                        media_kind=media.media_kind,
                        alt_text=media.alt_text,
                    )
                    for media in item.media
                ),
                metadata=dict(item.metadata),
            )
            for item in result.items
        )
        usage = {
            "attempts": 1,
            "network_requests": int(result.network_request_count or 0),
            "wall_seconds": _wall_seconds(result),
            "items": len(items),
            "cost_cents": result.cost_cents,
            "model_tokens": 0,
        }
        outcome_counts = {
            "attempted": (
                len(items)
                if result.attempted_count is None
                else int(result.attempted_count)
            ),
            "observed": (
                len(items)
                if result.observed_count is None
                else int(result.observed_count)
            ),
            "accepted": (
                len(items)
                if result.accepted_count is None
                else int(result.accepted_count)
            ),
            "rejected": (
                0 if result.rejected_count is None else int(result.rejected_count)
            ),
        }
        browser_operations = _browser_operations(result.diagnostics)
        rejection_counts = _rejection_counts(result.diagnostics)
        failure_stage = _failure_stage(result.diagnostics)
        failure_signature = _failure_signature(result.diagnostics)
        if items:
            return ProviderResult(
                status=(
                    "partial"
                    if result.status is contracts.AcquisitionStatus.PARTIAL
                    else "success"
                ),
                items=items,
                usage=usage,
                failure_class=(
                    _failure_class(result) if result.safe_error_code else None
                ),
                safe_error_code=result.safe_error_code,
                failure_stage=failure_stage,
                failure_signature=failure_signature,
                page_signals=tuple(result.diagnostics.get("page_signals") or ()),
                operator_url=result.operator_url,
                rendered_page=result.rendered_page,
                rendered_page_mime_type=result.rendered_page_mime_type,
                outcome_counts=outcome_counts,
                browser_operations=browser_operations,
                rejection_counts=rejection_counts,
            )
        if result.status is contracts.AcquisitionStatus.SUCCEEDED:
            return ProviderResult(
                status="empty",
                items=(),
                usage=usage,
                outcome_counts=outcome_counts,
                browser_operations=browser_operations,
                rejection_counts=rejection_counts,
            )
        return ProviderResult(
            status="failure",
            items=(),
            usage=usage,
            failure_class=_failure_class(result),
            safe_error_code=result.safe_error_code or "source_error",
            failure_stage=failure_stage,
            failure_signature=failure_signature,
            page_signals=tuple(result.diagnostics.get("page_signals") or ()),
            operator_url=result.operator_url,
            rendered_page=result.rendered_page,
            rendered_page_mime_type=result.rendered_page_mime_type,
            outcome_counts=outcome_counts,
            browser_operations=browser_operations,
            rejection_counts=rejection_counts,
        )


def build_acquisition_adapter_registry(worker) -> AdapterRegistry:
    specs = []
    for adapter, (source, version) in sorted(_ADAPTERS.items()):
        specs.append(
            AdapterSpec(
                adapter,
                frozenset({"collect"}),
                frozenset({source}),
                AcquisitionWorkerTickAdapter(
                    worker,
                    adapter=adapter,
                    adapter_version=version,
                ),
                _normalization_proof_ref(adapter),
            )
        )
    return AdapterRegistry(specs)
