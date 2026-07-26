"""Isolated source-worker entrypoint and direct adapter registry.

This module is imported only by the acquisition subprocess.  The query service
and deterministic supervisor never import browser or source adapters.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import threading
import urllib.request
from collections.abc import Callable, Mapping
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import env as env_config
from . import normalize
from . import service_contracts as contracts
from .service_worker import PROFILE_SOURCE_ADAPTERS, SOURCE_ADAPTERS


Adapter = Callable[
    [contracts.AcquisitionWorkRequest, Mapping[str, str]], dict[str, Any]
]

_PROFILE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$")
_OPERATOR_ERRORS = frozenset(
    {"auth_required", "checkpoint_required", "profile_mismatch"}
)
_RATE_LIMIT_ERRORS = frozenset(
    {"rate_limited", "rate_limit_detected", "http_429"}
)
_CONFIGURATION_ERRORS = frozenset(
    {
        "agent_browser_missing",
        "missing_credential",
        "missing_tool",
        "unsupported_source",
        "invalid_profile",
        "invalid_configuration",
    }
)
_CONTENT_ERRORS = frozenset(
    {
        "extraction_empty",
        "navigation_mismatch",
        "quality_gate_failed",
    }
)
_PERMANENT_ERRORS = frozenset(
    {
        "invalid_request",
        "invalid_contract",
        "validator_failed",
        "network_budget_exhausted",
        "budget_exhausted",
    }
)


def _default_config_root(environ: Mapping[str, str]) -> Path:
    override = environ.get("LAST30DAYS_CONFIG_DIR")
    if override:
        return Path(override).expanduser()
    xdg = environ.get("XDG_CONFIG_HOME")
    if xdg:
        return Path(xdg) / "last30days"
    return Path.home() / ".config" / "last30days"


def load_profile_config(
    profile_id: str,
    *,
    config_root: Path | None = None,
    environ: Mapping[str, str] | None = None,
) -> dict[str, str]:
    """Resolve one named user profile without consulting the worker CWD."""
    if not _PROFILE_ID.fullmatch(profile_id):
        raise contracts.ContractValidationError("invalid profile_id")
    process_env = dict(os.environ if environ is None else environ)
    root = Path(config_root) if config_root is not None else _default_config_root(
        process_env
    )
    config = env_config.load_env_file(root / ".env")
    config.update(env_config.load_env_file(root / "profiles" / f"{profile_id}.env"))
    config.update(process_env)
    return config


def _depth(value: str) -> str:
    return "default" if value == "standard" else value


def _x_adapter(
    request: contracts.AcquisitionWorkRequest, config: Mapping[str, str]
) -> dict[str, Any]:
    from . import x_browser

    return x_browser.search_x_browser(
        request.query,
        request.from_date,
        request.to_date,
        depth=_depth(request.depth),
        config=dict(config),
    )


def _facebook_adapter(
    request: contracts.AcquisitionWorkRequest, config: Mapping[str, str]
) -> dict[str, Any]:
    from . import facebook

    return facebook.search_facebook(
        request.query,
        request.from_date,
        request.to_date,
        depth=_depth(request.depth),
        config=dict(config),
    )


def _linkedin_adapter(
    request: contracts.AcquisitionWorkRequest, config: Mapping[str, str]
) -> dict[str, Any]:
    from . import linkedin

    return linkedin.search_linkedin(
        request.query,
        request.from_date,
        request.to_date,
        depth=_depth(request.depth),
        config=dict(config),
    )


def _linkedin_profile_adapter(
    request: contracts.AcquisitionWorkRequest, config: Mapping[str, str]
) -> dict[str, Any]:
    from . import linkedin

    return linkedin.acquire_linkedin_profile(request.query, config=dict(config))


def _youtube_adapter(
    request: contracts.AcquisitionWorkRequest, config: Mapping[str, str]
) -> dict[str, Any]:
    del config
    from . import youtube_yt

    return youtube_yt.search_youtube(
        request.query,
        request.from_date,
        request.to_date,
        depth=_depth(request.depth),
    )


def _reddit_adapter(
    request: contracts.AcquisitionWorkRequest, config: Mapping[str, str]
) -> dict[str, Any]:
    from . import reddit, reddit_public

    public_items = reddit_public.search_reddit_public(
        request.query,
        request.from_date,
        request.to_date,
        depth=_depth(request.depth),
    )
    if public_items:
        return {"items": public_items, "_cost_cents": 0}
    token = config.get("SCRAPECREATORS_API_KEY")
    if not token:
        return {"items": [], "_cost_cents": 0}
    result = reddit.search_reddit(
        request.query,
        request.from_date,
        request.to_date,
        depth=_depth(request.depth),
        token=token,
    )
    result["_cost_cents"] = 1
    return result


_DEFAULT_ADAPTERS: dict[str, Adapter] = {
    "x_agent_browser": _x_adapter,
    "facebook_agent_browser": _facebook_adapter,
    "linkedin_agent_browser": _linkedin_adapter,
    "linkedin_profile_agent_browser": _linkedin_profile_adapter,
    "youtube_ytdlp": _youtube_adapter,
    "reddit_api": _reddit_adapter,
}


def _sanitize(value: Any) -> Any:
    if isinstance(value, Mapping):
        clean: dict[str, Any] = {}
        for key, nested in value.items():
            name = str(key)
            normalized = name.strip().lower().replace("-", "_")
            if normalized in contracts.FORBIDDEN_LEDGER_FIELDS:
                continue
            clean[name] = _sanitize(nested)
        return clean
    if isinstance(value, list):
        return [_sanitize(item) for item in value[:1000]]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)[:512]


def _retry_class(error_code: str) -> contracts.RetryClass:
    if error_code in _OPERATOR_ERRORS:
        return contracts.RetryClass.OPERATOR
    if error_code in _RATE_LIMIT_ERRORS:
        return contracts.RetryClass.RATE_LIMIT
    if error_code in _CONFIGURATION_ERRORS:
        return contracts.RetryClass.CONFIGURATION
    if error_code in _CONTENT_ERRORS:
        return contracts.RetryClass.CONTENT
    if error_code in _PERMANENT_ERRORS:
        return contracts.RetryClass.PERMANENT
    return contracts.RetryClass.TRANSIENT


def _safe_error_code(value: object) -> str | None:
    text = str(value or "").strip().casefold()
    if not text:
        return None
    normalized = re.sub(r"[^a-z0-9_]+", "_", text).strip("_")[:64]
    if not normalized or not normalized[0].isalpha():
        return "source_error"
    return normalized


def _safe_failure_stage(value: object) -> str:
    text = str(value or "").strip().casefold()
    normalized = re.sub(r"[^a-z0-9_]+", "_", text).strip("_")[:64]
    return normalized or "adapter_result"


def _failure_signature(
    request: contracts.AcquisitionWorkRequest,
    *,
    error_code: str,
    retry_class: contracts.RetryClass,
    failure_stage: str,
) -> str:
    payload = {
        "adapter": request.adapter,
        "adapter_version": request.adapter_version,
        "error_code": error_code,
        "failure_stage": failure_stage,
        "retry_class": retry_class.value,
        "source": request.source,
    }
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def _normalized_items(
    request: contracts.AcquisitionWorkRequest, raw_items: list[dict[str, Any]]
) -> list[contracts.AcquiredItem]:
    if request.adapter == "linkedin_profile_agent_browser":
        items: list[contracts.AcquiredItem] = []
        for raw in raw_items[: request.item_limit]:
            metadata = _sanitize(raw.get("metadata") or {})
            if metadata.get("surface_kind") != "profile":
                continue
            items.append(
                contracts.AcquiredItem.from_dict(
                    {
                        "source_native_id": str(raw.get("source_native_id") or ""),
                        "url": str(raw.get("url") or ""),
                        "title": str(raw.get("title") or ""),
                        "text": str(raw.get("text") or ""),
                        "author": raw.get("author"),
                        "published_at": None,
                        "metadata": metadata,
                    }
                )
            )
        return items
    normalized = normalize.normalize_source_items(
        request.source,
        raw_items,
        request.from_date,
        request.to_date,
        freshness_mode="balanced_recent",
    )
    items: list[contracts.AcquiredItem] = []
    for item in normalized[: request.item_limit]:
        text = (item.body or item.snippet or item.title).strip()
        title = (item.title or text[:160]).strip()
        if not item.item_id or not item.url or not title or not text:
            continue
        metadata = _sanitize(
            {
                **dict(item.metadata),
                "container": item.container,
                "date_confidence": item.date_confidence,
                "engagement": dict(item.engagement),
                "relevance_hint": item.relevance_hint,
            }
        )
        items.append(
            contracts.AcquiredItem.from_dict(
                {
                    "source_native_id": item.item_id,
                    "url": item.url,
                    "title": title,
                    "text": text,
                    "author": item.author,
                    "published_at": item.published_at,
                    "metadata": metadata,
                }
            )
        )
    return items


def execute_work(
    request: contracts.AcquisitionWorkRequest,
    config: Mapping[str, str],
    *,
    adapters: Mapping[str, Adapter] | None = None,
    clock: Callable[[], datetime] | None = None,
) -> contracts.AcquisitionWorkResult:
    """Execute one adapter and return a proposal; never mutate service state."""
    adapter_registry = adapters or _DEFAULT_ADAPTERS
    adapter = adapter_registry.get(request.adapter)
    now = clock or (lambda: datetime.now(timezone.utc))
    observed_at = now().astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    if adapter is None:
        raw: dict[str, Any] = {
            "items": [],
            "error_type": "unsupported_source",
            "diagnostics": {"failure_stage": "adapter_selection"},
        }
    elif request.network_request_limit == 0:
        raw = {
            "items": [],
            "error_type": "network_budget_exhausted",
            "diagnostics": {"failure_stage": "budget_guard"},
        }
    else:
        original_urlopen = urllib.request.urlopen
        network_lock = threading.Lock()
        network_count = 0
        network_exhausted = False

        def bounded_urlopen(*args, **kwargs):
            nonlocal network_count, network_exhausted
            with network_lock:
                network_count += 1
                if network_count > request.network_request_limit:
                    network_exhausted = True
                    raise RuntimeError("network request budget exhausted")
            return original_urlopen(*args, **kwargs)

        urllib.request.urlopen = bounded_urlopen
        try:
            raw = adapter(request, config)
        except Exception:
            raw = {
                "items": [],
                "error_type": "adapter_exception",
                "diagnostics": {"failure_stage": "adapter_execution"},
            }
        finally:
            urllib.request.urlopen = original_urlopen
        if network_exhausted:
            raw = {
                "items": [],
                "error_type": "network_budget_exhausted",
                "diagnostics": {
                    "failure_stage": "budget_guard",
                    "network_requests": network_count,
                },
            }
    raw_items = raw.get("items")
    if not isinstance(raw_items, list):
        raw_items = []
    try:
        items = _normalized_items(request, raw_items)
    except (TypeError, ValueError, contracts.ContractValidationError):
        items = []
        raw = {
            "items": [],
            "error_type": "validator_failed",
            "diagnostics": {"failure_stage": "normalization"},
        }
    error_code = _safe_error_code(raw.get("error_type"))
    if error_code is None and raw.get("error"):
        error_code = "source_error"
    retry_class = (
        _retry_class(error_code)
        if error_code is not None
        else contracts.RetryClass.NONE
    )
    if error_code is None:
        status = contracts.AcquisitionStatus.SUCCEEDED
    elif items:
        status = contracts.AcquisitionStatus.PARTIAL
    elif retry_class is contracts.RetryClass.OPERATOR:
        status = contracts.AcquisitionStatus.AWAITING_OPERATOR
    else:
        status = contracts.AcquisitionStatus.FAILED
    retry_after = raw.get("retry_after_seconds")
    if not isinstance(retry_after, int) or isinstance(retry_after, bool):
        retry_after = None
    fetched_at = now().astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    diagnostics = _sanitize(raw.get("diagnostics") or {})
    if not isinstance(diagnostics, dict):
        diagnostics = {}
    cost_cents = raw.get("_cost_cents", 0)
    if (
        isinstance(cost_cents, bool)
        or not isinstance(cost_cents, int)
        or not 0 <= cost_cents <= request.cost_budget_cents
    ):
        items = []
        error_code = "validator_failed"
        retry_class = contracts.RetryClass.PERMANENT
        status = contracts.AcquisitionStatus.FAILED
        retry_after = None
        cost_cents = 0
        diagnostics = {"failure_stage": "cost_validation"}
    failure_stage = ""
    if error_code is not None:
        failure_stage = _safe_failure_stage(diagnostics.get("failure_stage"))
        diagnostics["failure_stage"] = failure_stage
    encoded_diagnostics = json.dumps(
        diagnostics,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    )
    if len(encoded_diagnostics) > 16_384:
        diagnostics = {
            "truncated": True,
            **({"failure_stage": failure_stage} if failure_stage else {}),
        }
    if error_code is not None:
        diagnostics["failure_signature"] = _failure_signature(
            request,
            error_code=error_code,
            retry_class=retry_class,
            failure_stage=failure_stage,
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
            "safe_error_code": error_code,
            "retry_class": retry_class.value,
            "retry_after_seconds": retry_after,
            "observed_at": observed_at,
            "fetched_at": fetched_at,
            "items": [item.to_dict() for item in items],
            "item_count": len(items),
            "cost_cents": cost_cents,
            "diagnostics": diagnostics,
        }
    )


def main() -> int:
    try:
        payload = json.load(sys.stdin)
        request = contracts.AcquisitionWorkRequest.from_dict(payload)
        expected = {
            SOURCE_ADAPTERS.get(request.source),
            PROFILE_SOURCE_ADAPTERS.get(request.source),
        }
        if (request.adapter, request.adapter_version) not in expected:
            raise contracts.ContractValidationError("source adapter mismatch")
        config = load_profile_config(request.profile_id)
        result = execute_work(request, config)
        json.dump(
            result.to_dict(),
            sys.stdout,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        )
        return 0
    except (
        json.JSONDecodeError,
        contracts.ContractValidationError,
        OSError,
    ):
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
