"""Isolated source-worker entrypoint and direct adapter registry.

This module is imported only by the acquisition subprocess.  The query service
and deterministic supervisor never import browser or source adapters.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import re
import socket
import subprocess
import sys
import tempfile
import threading
import time
import urllib.request
from collections.abc import Callable, Mapping
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

from . import env as env_config
from . import normalize
from . import service_contracts as contracts
from . import service_tick_http
from .service_worker import (
    COLLECTION_ACCESS_METHOD_ADAPTERS,
    PROFILE_SOURCE_ADAPTERS,
    SOURCE_ADAPTERS,
)
from .service_source_policy import (
    ServiceSourcePolicyError,
    load_service_source_policy,
)


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
        "unsafe_media_url",
        "wall_time_budget_exhausted",
        "media_redirect_limit_exceeded",
    }
)
_RENDERED_PAGE_ERRORS = frozenset(
    {
        "auth_required",
        "captcha_required",
        "checkpoint_required",
        "cloudflare_challenge",
        "rate_limited",
    }
)
_MAX_ACQUIRED_MEDIA_BYTES = 524_288
_MAX_ACQUIRED_MEDIA_ITEM_BYTES = 262_144
_MAX_RENDERED_PAGE_BYTES = 524_288
_BOUNDED_REDDIT_ITEM_LIMIT = 3
_BOUNDED_REDDIT_FALLBACK_TIMEOUT_SECONDS = 20
_MAX_MEDIA_REDIRECTS = 3
_ACCESS_METHOD_BY_ADAPTER = {
    "x_agent_browser": "agent_browser",
    "facebook_agent_browser": "agent_browser",
    "linkedin_agent_browser": "agent_browser",
    "linkedin_profile_agent_browser": "agent_browser",
    "youtube_ytdlp": "yt_dlp",
    "reddit_keyless": "keyless",
    "reddit_agent_browser": "agent_browser",
    "reddit_scrapecreators": "scrapecreators",
}


_REDDIT_ADAPTER_VARIANT_BY_METHOD = {
    "keyless": "reddit_keyless",
    "agent_browser": "reddit_agent_browser",
    "scrapecreators": "reddit_scrapecreators",
}


def _with_access_method_provenance(
    result: dict[str, Any],
    *,
    attempted: list[str],
    selected: str | None,
) -> dict[str, Any]:
    diagnostics = result.get("diagnostics")
    diagnostics = dict(diagnostics) if isinstance(diagnostics, Mapping) else {}
    diagnostics["attempted_access_methods"] = list(attempted)
    diagnostics["selected_access_method"] = selected
    result["diagnostics"] = diagnostics
    return result


def _result_adapter_variant(
    adapter: str,
    diagnostics: Mapping[str, Any],
) -> str:
    if adapter != "reddit_api":
        return adapter
    selected = diagnostics.get("selected_access_method")
    if isinstance(selected, str) and selected in _REDDIT_ADAPTER_VARIANT_BY_METHOD:
        return _REDDIT_ADAPTER_VARIANT_BY_METHOD[selected]
    attempted = diagnostics.get("attempted_access_methods")
    if isinstance(attempted, list):
        methods = [method for method in attempted if isinstance(method, str)]
        if len(methods) == 1 and methods[0] in _REDDIT_ADAPTER_VARIANT_BY_METHOD:
            return _REDDIT_ADAPTER_VARIANT_BY_METHOD[methods[0]]
        if methods:
            return "reddit_access_chain"
    return adapter


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


def _account_opaque_source_request(result: dict[str, Any]) -> dict[str, Any]:
    result["_network_request_count"] = 1
    return result


def _x_adapter(
    request: contracts.AcquisitionWorkRequest, config: Mapping[str, str]
) -> dict[str, Any]:
    from . import x_browser

    if request.surface_kind == "feed":
        return _account_opaque_source_request(x_browser.scrape_x_feed(
            request.from_date,
            request.to_date,
            depth=_depth(request.depth),
            config=dict(config),
            limit=request.item_limit,
        ))
    return _account_opaque_source_request(x_browser.search_x_browser(
        request.query,
        request.from_date,
        request.to_date,
        depth=_depth(request.depth),
        config=dict(config),
        limit=request.item_limit,
    ))


def _facebook_adapter(
    request: contracts.AcquisitionWorkRequest, config: Mapping[str, str]
) -> dict[str, Any]:
    from . import facebook

    constrained_config = dict(config)
    constrained_config["LAST30DAYS_FACEBOOK_MAX_RESULTS"] = str(request.item_limit)
    requested_timeout = int(
        constrained_config.get("LAST30DAYS_FACEBOOK_TIMEOUT")
        or facebook.DEPTH_CONFIG[_depth(request.depth)]["timeout"]
    )
    parent_bounded_timeout = max(1, request.wall_timeout_seconds - 15)
    constrained_config["LAST30DAYS_FACEBOOK_TIMEOUT"] = str(
        min(requested_timeout, parent_bounded_timeout)
    )
    return _account_opaque_source_request(
        facebook.search_facebook(
            request.query,
            request.from_date,
            request.to_date,
            depth=_depth(request.depth),
            config=constrained_config,
        )
    )


def _linkedin_adapter(
    request: contracts.AcquisitionWorkRequest, config: Mapping[str, str]
) -> dict[str, Any]:
    from . import linkedin

    if request.surface_kind == "feed":
        return _account_opaque_source_request(linkedin.scrape_linkedin_feed(
            request.from_date,
            request.to_date,
            depth=_depth(request.depth),
            config=dict(config),
            limit=request.item_limit,
        ))
    return _account_opaque_source_request(linkedin.search_linkedin(
        request.query,
        request.from_date,
        request.to_date,
        depth=_depth(request.depth),
        config=dict(config),
        limit=request.item_limit,
    ))


def _linkedin_profile_adapter(
    request: contracts.AcquisitionWorkRequest, config: Mapping[str, str]
) -> dict[str, Any]:
    from . import linkedin

    return _account_opaque_source_request(
        linkedin.acquire_linkedin_profile(request.query, config=dict(config))
    )


def _youtube_adapter(
    request: contracts.AcquisitionWorkRequest, config: Mapping[str, str]
) -> dict[str, Any]:
    del config
    from . import youtube_yt

    result = youtube_yt.search_youtube(
        request.query,
        request.from_date,
        request.to_date,
        depth=_depth(request.depth),
    )
    return _account_opaque_source_request(result)


def _reddit_adapter(
    request: contracts.AcquisitionWorkRequest, config: Mapping[str, str]
) -> dict[str, Any]:
    from . import reddit, reddit_browser, reddit_public

    bounded = request.item_limit <= _BOUNDED_REDDIT_ITEM_LIMIT
    depth = "quick" if bounded else _depth(request.depth)
    policy = load_service_source_policy(config)
    access_order = policy.access_order("reddit")
    browser_result: dict[str, Any] | None = None
    total_cost_cents = 0
    unavailable: list[str] = []
    attempted: list[str] = []
    for method in access_order:
        if not policy.method_available("reddit", method, config):
            unavailable.append(method)
            continue
        attempted.append(method)
        if method == "keyless":
            public_items = reddit_public.search_reddit_public(
                request.query,
                request.from_date,
                request.to_date,
                depth=depth,
            )
            if public_items:
                return _with_access_method_provenance(
                    {"items": public_items, "_cost_cents": total_cost_cents},
                    attempted=attempted,
                    selected=method,
                )
            continue
        if method == "agent_browser":
            try:
                browser_result = reddit_browser.search_reddit_browser(
                    request.query,
                    request.from_date,
                    request.to_date,
                    depth=depth,
                    config=dict(config),
                    limit=request.item_limit,
                )
            except Exception:
                return _with_access_method_provenance(
                    {
                        "items": [],
                        "error_type": "adapter_exception",
                        "diagnostics": {"failure_stage": "adapter_execution"},
                        "_network_request_count": 1,
                        "_cost_cents": total_cost_cents,
                    },
                    attempted=attempted,
                    selected=None,
                )
            browser_result["_network_request_count"] = 1
            if browser_result.get("items"):
                browser_result["_cost_cents"] = total_cost_cents
                return _with_access_method_provenance(
                    browser_result, attempted=attempted, selected=method
                )
            continue
        if method == "scrapecreators":
            token = config.get("SCRAPECREATORS_API_KEY")
            search_options: dict[str, Any] = {}
            if bounded:
                search_options = {
                    "global_search_limit": 1,
                    "subreddit_search_limit": 0,
                    "request_timeout": _BOUNDED_REDDIT_FALLBACK_TIMEOUT_SECONDS,
                    "request_retries": 1,
                    "min_dns_retries": 1,
                }
            result = reddit.search_reddit(
                request.query,
                request.from_date,
                request.to_date,
                depth=depth,
                token=token,
                **search_options,
            )
            total_cost_cents += 1
            if browser_result is not None:
                browser_diagnostics = browser_result.get("diagnostics")
                browser_diagnostics = (
                    browser_diagnostics
                    if isinstance(browser_diagnostics, Mapping)
                    else {}
                )
                paid_diagnostics = result.get("diagnostics")
                paid_diagnostics = (
                    dict(paid_diagnostics)
                    if isinstance(paid_diagnostics, Mapping)
                    else {}
                )
                browser_error_type = _safe_error_code(browser_result.get("error_type"))
                if browser_error_type is None:
                    browser_error_type = (
                        "verified_no_results"
                        if browser_diagnostics.get("verified_no_results") is True
                        else "empty_result"
                    )
                paid_diagnostics["browser_fallback"] = {
                    "error_type": browser_error_type,
                    "failure_stage": _safe_failure_stage(
                        browser_diagnostics.get("failure_stage")
                    ),
                }
                result["diagnostics"] = paid_diagnostics
            result["_cost_cents"] = total_cost_cents
            if browser_result is not None:
                result["_network_request_count"] = 1
            if result.get("items"):
                return _with_access_method_provenance(
                    result, attempted=attempted, selected=method
                )

    if browser_result is not None:
        browser_result["_cost_cents"] = total_cost_cents
        if unavailable:
            diagnostics = browser_result.get("diagnostics")
            diagnostics = dict(diagnostics) if isinstance(diagnostics, Mapping) else {}
            diagnostics["unavailable_access_methods"] = unavailable
            browser_result["diagnostics"] = diagnostics
        return _with_access_method_provenance(
            browser_result, attempted=attempted, selected=None
        )
    result = {"items": [], "_cost_cents": total_cost_cents}
    if unavailable:
        result["diagnostics"] = {"unavailable_access_methods": unavailable}
    return _with_access_method_provenance(
        result, attempted=attempted, selected=None
    )


def _reddit_method_adapter(method: str) -> Adapter:
    def run(
        request: contracts.AcquisitionWorkRequest,
        config: Mapping[str, str],
    ) -> dict[str, Any]:
        constrained_config = dict(config)
        constrained_config["LAST30DAYS_REDDIT_ACCESS_ORDER"] = method
        return _reddit_adapter(request, constrained_config)

    return run


_DEFAULT_ADAPTERS: dict[str, Adapter] = {
    "x_agent_browser": _x_adapter,
    "facebook_agent_browser": _facebook_adapter,
    "linkedin_agent_browser": _linkedin_adapter,
    "linkedin_profile_agent_browser": _linkedin_profile_adapter,
    "youtube_ytdlp": _youtube_adapter,
    "reddit_api": _reddit_adapter,
    "reddit_keyless": _reddit_method_adapter("keyless"),
    "reddit_agent_browser": _reddit_method_adapter("agent_browser"),
    "reddit_scrapecreators": _reddit_method_adapter("scrapecreators"),
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


def _external_operator_url(raw: Mapping[str, Any]) -> str | None:
    value = raw.get("operator_url")
    if not isinstance(value, str) or not value.strip() or len(value) > 4_096:
        return None
    parsed = urlparse(value)
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.hostname.casefold() in {"localhost", "127.0.0.1", "::1"}
    ):
        return None
    return value


def _capture_rendered_page(raw: dict[str, Any]) -> None:
    """Capture the current agent-browser tab without requesting a Guac lease."""
    if raw.get("rendered_page_base64") or raw.get("error_type") not in _RENDERED_PAGE_ERRORS:
        return
    session = raw.get("session")
    if not isinstance(session, str) or not _PROFILE_ID.fullmatch(session):
        return
    try:
        with tempfile.TemporaryDirectory(prefix="last30days-rendered-page-") as root:
            output = Path(root) / "page.jpg"
            completed = subprocess.run(
                [
                    "agent-browser",
                    "--json",
                    "--session",
                    session,
                    "screenshot",
                    str(output),
                    "--screenshot-format",
                    "jpeg",
                    "--screenshot-quality",
                    "60",
                ],
                capture_output=True,
                text=True,
                timeout=15,
                encoding="utf-8",
                errors="replace",
            )
            if completed.returncode != 0 or not output.is_file():
                return
            content = output.read_bytes()
            if not content or len(content) > _MAX_RENDERED_PAGE_BYTES:
                return
            raw["rendered_page_base64"] = base64.b64encode(content).decode("ascii")
            raw["rendered_page_mime_type"] = "image/jpeg"
    except (OSError, subprocess.SubprocessError):
        return


def _materialized_media(
    metadata: Mapping[str, Any],
    fetcher: Callable[[str], tuple[bytes, str] | None] | None,
) -> list[contracts.AcquiredMedia]:
    if fetcher is None:
        return []
    raw_media = metadata.get("media")
    if not isinstance(raw_media, list):
        return []
    output: list[contracts.AcquiredMedia] = []
    for candidate in raw_media[:16]:
        if not isinstance(candidate, Mapping):
            continue
        kind = str(candidate.get("kind") or "")
        if kind == "image":
            media_kind = "image"
            source_url = candidate.get("url")
        elif kind in {"video", "video_thumbnail"}:
            media_kind = "video_thumbnail"
            source_url = candidate.get("preview_url") or (
                candidate.get("url") if kind == "video_thumbnail" else None
            )
        else:
            continue
        if not isinstance(source_url, str):
            continue
        parsed = urlparse(source_url)
        if parsed.scheme != "https" or not parsed.hostname:
            continue
        fetched = fetcher(source_url)
        if fetched is None:
            continue
        content, observed_mime_type = fetched
        mime_type = str(candidate.get("mime_type") or observed_mime_type)
        try:
            output.append(
                contracts.AcquiredMedia.from_dict(
                    {
                        "source_url": source_url,
                        "content_base64": base64.b64encode(content).decode("ascii"),
                        "mime_type": mime_type,
                        "media_kind": media_kind,
                        "alt_text": (
                            str(candidate["alt_text"])
                            if candidate.get("alt_text")
                            else None
                        ),
                    }
                )
            )
        except contracts.ContractValidationError:
            continue
    return output


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


def _unexpected_exception_reason(exc: Exception) -> str:
    """Return a bounded class-only reason without retaining exception text."""
    class_name = type(exc).__name__
    snake_name = re.sub(r"(?<!^)(?=[A-Z])", "_", class_name).casefold()
    normalized = re.sub(r"[^a-z0-9_]+", "_", snake_name).strip("_")[:48]
    return f"unexpected_{normalized or 'exception'}"[:64]


def _safe_failure_stage(value: object) -> str:
    text = str(value or "").strip().casefold()
    normalized = re.sub(r"[^a-z0-9_]+", "_", text).strip("_")[:64]
    return normalized or "adapter_result"


def _safe_failure_reason(value: object) -> str:
    text = str(value or "").strip()
    return text if re.fullmatch(r"[a-z][a-z0-9_]{0,63}", text) else ""


def _failure_signature(
    request: contracts.AcquisitionWorkRequest,
    *,
    error_code: str,
    retry_class: contracts.RetryClass,
    failure_stage: str,
    failure_reason_code: str,
) -> str:
    payload = {
        "adapter": request.adapter,
        "adapter_version": request.adapter_version,
        "error_code": error_code,
        "failure_stage": failure_stage,
        "failure_reason_code": failure_reason_code,
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
    request: contracts.AcquisitionWorkRequest,
    raw_items: list[dict[str, Any]],
    *,
    media_fetcher: Callable[[str], tuple[bytes, str] | None] | None = None,
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
                        "media": [
                            value.to_dict()
                            for value in _materialized_media(metadata, media_fetcher)
                        ],
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
                    "media": [
                        value.to_dict()
                        for value in _materialized_media(metadata, media_fetcher)
                    ],
                }
            )
        )
    return items


def _observed_candidate_count(
    raw_items: list[dict[str, Any]], diagnostics: Mapping[str, Any]
) -> int:
    candidate_counts = diagnostics.get("candidate_counts")
    if isinstance(candidate_counts, Mapping):
        values = [
            value
            for key, value in candidate_counts.items()
            if str(key) != "rejected"
            if isinstance(value, int) and not isinstance(value, bool) and value >= 0
        ]
        expected_values = len(candidate_counts) - int("rejected" in candidate_counts)
        if len(values) == expected_values:
            return max(len(raw_items), sum(values))
    candidate_count = diagnostics.get("candidate_count")
    if (
        isinstance(candidate_count, int)
        and not isinstance(candidate_count, bool)
        and candidate_count >= 0
    ):
        return max(len(raw_items), candidate_count)
    accepted_count = diagnostics.get("accepted_count")
    rejection_counts = diagnostics.get("rejection_counts")
    if (
        isinstance(accepted_count, int)
        and not isinstance(accepted_count, bool)
        and accepted_count >= 0
        and isinstance(rejection_counts, Mapping)
    ):
        rejected = [
            value
            for value in rejection_counts.values()
            if isinstance(value, int) and not isinstance(value, bool) and value >= 0
        ]
        if len(rejected) == len(rejection_counts):
            return max(len(raw_items), accepted_count + sum(rejected))
    return len(raw_items)


def execute_work(
    request: contracts.AcquisitionWorkRequest,
    config: Mapping[str, str],
    *,
    adapters: Mapping[str, Adapter] | None = None,
    clock: Callable[[], datetime] | None = None,
    media_transport: service_tick_http.MediaTransport | None = None,
    address_resolver: Callable[..., Any] | None = None,
    monotonic_clock: Callable[[], float] | None = None,
) -> contracts.AcquisitionWorkResult:
    """Execute one adapter and return a proposal; never mutate service state."""
    adapter_registry = adapters or _DEFAULT_ADAPTERS
    adapter = adapter_registry.get(request.adapter)
    now = clock or (lambda: datetime.now(timezone.utc))
    monotonic = monotonic_clock or time.monotonic
    started_monotonic = monotonic()
    resolver = address_resolver or socket.getaddrinfo
    observed_time = now().astimezone(timezone.utc)
    observed_at = observed_time.isoformat().replace("+00:00", "Z")
    network_count = 0
    network_lock = threading.Lock()
    network_exhausted = False

    def reserve_network_request() -> None:
        nonlocal network_count, network_exhausted
        with network_lock:
            network_count += 1
            if network_count > request.network_request_limit:
                network_exhausted = True
                raise RuntimeError("network request budget exhausted")
    try:
        source_policy = load_service_source_policy(config)
        source_policy.access_order(request.source)
    except ServiceSourcePolicyError:
        raw = {
            "items": [],
            "error_type": "invalid_configuration",
            "diagnostics": {"failure_stage": "source_policy"},
        }
    else:
        raw = {}
    if raw:
        pass
    elif adapter is None:
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

        def bounded_urlopen(*args, **kwargs):
            reserve_network_request()
            return original_urlopen(*args, **kwargs)

        urllib.request.urlopen = bounded_urlopen
        try:
            raw = adapter(request, config)
        except Exception as exc:
            raw = {
                "items": [],
                "error_type": "adapter_exception",
                "diagnostics": {
                    "failure_stage": "adapter_execution",
                    "failure_reason_code": _unexpected_exception_reason(exc),
                },
            }
        finally:
            urllib.request.urlopen = original_urlopen
        if isinstance(raw, dict):
            _capture_rendered_page(raw)
        if network_exhausted:
            raw = {
                "items": [],
                "error_type": "network_budget_exhausted",
                "diagnostics": {
                    "failure_stage": "budget_guard",
                    "network_requests": network_count,
                },
            }
    external_network_count = raw.pop("_network_request_count", 0)
    if (
        isinstance(external_network_count, bool)
        or not isinstance(external_network_count, int)
        or external_network_count < 0
    ):
        raw = {
            "items": [],
            "error_type": "validator_failed",
            "diagnostics": {"failure_stage": "request_accounting"},
        }
    else:
        network_count += external_network_count
    if network_count > request.network_request_limit:
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
    remaining_media_bytes = _MAX_ACQUIRED_MEDIA_BYTES
    media_error_code: str | None = None
    media_deadline = started_monotonic + request.wall_timeout_seconds
    active_media_transport = (
        media_transport
        or service_tick_http.DeadlinePinnedMediaTransport(
            resolver=resolver,
            monotonic_clock=monotonic,
        )
    )

    def fetch_media(source_url: str) -> tuple[bytes, str] | None:
        nonlocal remaining_media_bytes, media_error_code
        if network_count >= request.network_request_limit:
            media_error_code = "network_budget_exhausted"
            return None
        if remaining_media_bytes <= 0:
            return None
        maximum = min(_MAX_ACQUIRED_MEDIA_ITEM_BYTES, remaining_media_bytes)
        current_url = source_url
        for redirect_ordinal in range(_MAX_MEDIA_REDIRECTS + 1):
            if network_count >= request.network_request_limit:
                media_error_code = "network_budget_exhausted"
                return None
            try:
                response = active_media_transport.get(
                    current_url,
                    deadline=media_deadline,
                    maximum_bytes=maximum,
                    before_connect=reserve_network_request,
                )
            except service_tick_http.MediaDeadlineExceeded:
                media_error_code = "wall_time_budget_exhausted"
                return None
            except service_tick_http.UnsafeMediaDestination:
                media_error_code = "unsafe_media_url"
                return None
            except RuntimeError:
                if network_exhausted:
                    media_error_code = "network_budget_exhausted"
                return None
            except OSError:
                return None
            status = response.status
            if 300 <= status < 400:
                location = response.headers.get("location")
                if not isinstance(location, str) or not location.strip():
                    return None
                if redirect_ordinal >= _MAX_MEDIA_REDIRECTS:
                    media_error_code = "media_redirect_limit_exceeded"
                    return None
                current_url = urljoin(current_url, location.strip())
                continue
            if status >= 400:
                return None
            content = response.content
            mime_type = str(
                response.headers.get("content-type", "application/octet-stream")
            ).split(";", 1)[0]
            if not content or len(content) > maximum:
                return None
            remaining_media_bytes -= len(content)
            return content, mime_type
        media_error_code = "media_redirect_limit_exceeded"
        return None

    try:
        items = _normalized_items(
            request,
            raw_items,
            media_fetcher=fetch_media,
        )
    except (TypeError, ValueError, contracts.ContractValidationError):
        items = []
        raw = {
            "items": [],
            "error_type": "validator_failed",
            "diagnostics": {"failure_stage": "normalization"},
        }
    if media_error_code is not None:
        diagnostics = raw.get("diagnostics")
        if not isinstance(diagnostics, dict):
            diagnostics = {}
            raw["diagnostics"] = diagnostics
        diagnostics["media_error_code"] = media_error_code
        if not items and not raw.get("error_type"):
            raw["error_type"] = media_error_code
            diagnostics["failure_stage"] = "media_fetch"
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
    fetched_time = max(now().astimezone(timezone.utc), observed_time)
    fetched_at = fetched_time.isoformat().replace("+00:00", "Z")
    diagnostics = _sanitize(raw.get("diagnostics") or {})
    if not isinstance(diagnostics, dict):
        diagnostics = {}
    observed_count = _observed_candidate_count(raw_items, diagnostics)
    access_method = _ACCESS_METHOD_BY_ADAPTER.get(request.adapter)
    if access_method is not None:
        diagnostics.setdefault("attempted_access_methods", [access_method])
        diagnostics.setdefault(
            "selected_access_method", access_method if raw_items else None
        )
    diagnostics["adapter_variant"] = _result_adapter_variant(
        request.adapter,
        diagnostics,
    )
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
    accepted_count = len(items)
    rejected_count = max(0, observed_count - accepted_count)
    rejection_counts = diagnostics.get("rejection_counts")
    if not isinstance(rejection_counts, dict):
        rejection_counts = {}
        diagnostics["rejection_counts"] = rejection_counts
    accounted_rejections = sum(
        value
        for value in rejection_counts.values()
        if isinstance(value, int) and not isinstance(value, bool) and value >= 0
    )
    normalization_filtered = max(0, rejected_count - accounted_rejections)
    if normalization_filtered:
        previous_normalization_filtered = rejection_counts.get(
            "normalization_filtered"
        )
        if (
            isinstance(previous_normalization_filtered, bool)
            or not isinstance(previous_normalization_filtered, int)
            or previous_normalization_filtered < 0
        ):
            previous_normalization_filtered = 0
        rejection_counts["normalization_filtered"] = (
            previous_normalization_filtered
            + normalization_filtered
        )
    failure_stage = ""
    failure_reason_code = ""
    if error_code is not None:
        failure_stage = _safe_failure_stage(diagnostics.get("failure_stage"))
        diagnostics["failure_stage"] = failure_stage
        failure_reason_code = _safe_failure_reason(
            diagnostics.get("failure_reason_code")
        )
        if failure_reason_code:
            diagnostics["failure_reason_code"] = failure_reason_code
        else:
            diagnostics.pop("failure_reason_code", None)
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
            **(
                {"failure_reason_code": failure_reason_code}
                if failure_reason_code
                else {}
            ),
        }
    if error_code is not None:
        diagnostics["failure_signature"] = _failure_signature(
            request,
            error_code=error_code,
            retry_class=retry_class,
            failure_stage=failure_stage,
            failure_reason_code=failure_reason_code,
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
            **(
                {"operator_url": operator_url}
                if (operator_url := _external_operator_url(raw)) is not None
                else {}
            ),
            **(
                {
                    "rendered_page_base64": raw["rendered_page_base64"],
                    "rendered_page_mime_type": raw["rendered_page_mime_type"],
                }
                if raw.get("rendered_page_base64")
                and raw.get("rendered_page_mime_type")
                else {}
            ),
            "network_request_count": network_count,
            "attempted_count": observed_count,
            "observed_count": observed_count,
            "accepted_count": accepted_count,
            "rejected_count": rejected_count,
        }
    )


def main() -> int:
    try:
        payload = json.load(sys.stdin)
        request = contracts.AcquisitionWorkRequest.from_dict(payload)
        expected = {
            SOURCE_ADAPTERS.get(request.source),
            PROFILE_SOURCE_ADAPTERS.get(request.source),
            *(
                (adapter, version)
                for (source, _method), (adapter, version, _cost) in
                COLLECTION_ACCESS_METHOD_ADAPTERS.items()
                if source == request.source
            ),
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
