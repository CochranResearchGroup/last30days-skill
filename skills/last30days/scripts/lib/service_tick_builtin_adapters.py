"""Bridge installed isolated acquisition workers into durable tick providers."""

from __future__ import annotations

import base64
from datetime import datetime

from . import service_contracts as contracts
from .service_tick_adapters import AdapterRegistry, AdapterSpec
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
    for field in ("query", "topic", "url", "handle"):
        value = context.selector.get(field)
        if isinstance(value, str) and value.strip():
            return value.strip()
    raise ValueError("target selector requires query, topic, url, or handle")


def _failure_class(result: contracts.AcquisitionWorkResult) -> str:
    if result.safe_error_code in {"captcha_required", "checkpoint_required"}:
        return "challenge"
    return {
        contracts.RetryClass.OPERATOR: "authentication",
        contracts.RetryClass.RATE_LIMIT: "rate_limit",
        contracts.RetryClass.CONFIGURATION: "configuration",
        contracts.RetryClass.CONTENT: "policy",
        contracts.RetryClass.PERMANENT: "permanent",
        contracts.RetryClass.TRANSIENT: "transient",
        contracts.RetryClass.NONE: "permanent",
    }[result.retry_class]


def _wall_seconds(result: contracts.AcquisitionWorkResult) -> int:
    observed = datetime.fromisoformat(result.observed_at.replace("Z", "+00:00"))
    fetched = datetime.fromisoformat(result.fetched_at.replace("Z", "+00:00"))
    return max(1, int((fetched - observed).total_seconds()))


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
            }
        )
        result = self.worker.run(request)
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
        if items:
            return ProviderResult(
                status="success",
                items=items,
                usage=usage,
                failure_class=(
                    _failure_class(result) if result.safe_error_code else None
                ),
                safe_error_code=result.safe_error_code,
                page_signals=tuple(result.diagnostics.get("page_signals") or ()),
                operator_url=result.operator_url,
                rendered_page=result.rendered_page,
                rendered_page_mime_type=result.rendered_page_mime_type,
                outcome_counts=outcome_counts,
            )
        if result.status is contracts.AcquisitionStatus.SUCCEEDED:
            return ProviderResult(
                status="empty",
                items=(),
                usage=usage,
                outcome_counts=outcome_counts,
            )
        return ProviderResult(
            status="failure",
            items=(),
            usage=usage,
            failure_class=_failure_class(result),
            safe_error_code=result.safe_error_code or "source_error",
            page_signals=tuple(result.diagnostics.get("page_signals") or ()),
            operator_url=result.operator_url,
            rendered_page=result.rendered_page,
            rendered_page_mime_type=result.rendered_page_mime_type,
            outcome_counts=outcome_counts,
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
