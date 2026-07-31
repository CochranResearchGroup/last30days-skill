"""Strict user-scoped source and access-method policy for the service runtime."""

from __future__ import annotations

import shutil
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass


class ServiceSourcePolicyError(ValueError):
    """Raised when the effective service source policy is ambiguous or unsafe."""


SOURCE_ACCESS_METHODS: dict[str, tuple[str, ...]] = {
    "facebook": ("agent_browser",),
    "linkedin": ("agent_browser",),
    "reddit": ("keyless", "agent_browser", "scrapecreators"),
    "x": ("agent_browser",),
    "youtube": ("yt_dlp",),
}
DEFAULT_SERVICE_SOURCES = tuple(SOURCE_ACCESS_METHODS)
_TRUE_VALUES = frozenset({"1", "true", "yes", "on"})


def _enabled(value: object) -> bool:
    return str(value or "").strip().casefold() in _TRUE_VALUES


def _csv(value: object, *, field: str) -> tuple[str, ...]:
    text = str(value or "").strip()
    if not text:
        raise ServiceSourcePolicyError(f"{field} must not be empty")
    values = tuple(part.strip().casefold() for part in text.split(","))
    if any(not part for part in values):
        raise ServiceSourcePolicyError(f"{field} contains an empty entry")
    if len(set(values)) != len(values):
        raise ServiceSourcePolicyError(f"{field} contains a duplicate entry")
    return values


def _default_access_order(source: str, config: Mapping[str, object]) -> tuple[str, ...]:
    if source == "reddit":
        methods = ["keyless"]
        if _enabled(config.get("LAST30DAYS_REDDIT_BROWSER")):
            methods.append("agent_browser")
        methods.append("scrapecreators")
        return tuple(methods)
    return SOURCE_ACCESS_METHODS[source]


@dataclass(frozen=True)
class ServiceSourcePolicy:
    sources: tuple[str, ...]
    access_orders: dict[str, tuple[str, ...]]
    explicit_source_catalog: bool
    explicit_access_orders: frozenset[str]

    def access_order(self, source: str) -> tuple[str, ...]:
        try:
            return self.access_orders[source]
        except KeyError as exc:
            raise ServiceSourcePolicyError(
                f"source is not enabled by LAST30DAYS_SERVICE_SOURCES: {source}"
            ) from exc

    def method_available(
        self,
        source: str,
        method: str,
        config: Mapping[str, object],
        *,
        which: Callable[[str], str | None] | None = None,
    ) -> bool:
        resolve = which or shutil.which
        if method not in self.access_order(source):
            return False
        if method == "keyless":
            return True
        if method == "scrapecreators":
            return bool(config.get("SCRAPECREATORS_API_KEY"))
        if method == "yt_dlp":
            return bool(resolve("yt-dlp"))
        if method == "agent_browser":
            if not resolve("agent-browser"):
                return False
            if source in self.explicit_access_orders:
                return True
            return _enabled(config.get(f"LAST30DAYS_{source.upper()}_BROWSER"))
        return False

    def source_ready(
        self,
        source: str,
        config: Mapping[str, object],
        *,
        which: Callable[[str], str | None] | None = None,
    ) -> bool:
        return any(
            self.method_available(source, method, config, which=which)
            for method in self.access_order(source)
        )


def load_service_source_policy(
    config: Mapping[str, object],
    *,
    sources_override: Sequence[str] | None = None,
) -> ServiceSourcePolicy:
    """Resolve and validate the effective user-scoped service source policy."""
    explicit_catalog = sources_override is None and "LAST30DAYS_SERVICE_SOURCES" in config
    if sources_override is not None:
        sources = tuple(str(source).strip().casefold() for source in sources_override)
        if not sources or any(not source for source in sources):
            raise ServiceSourcePolicyError("sources_override must not be empty")
        if len(set(sources)) != len(sources):
            raise ServiceSourcePolicyError("sources_override contains a duplicate entry")
    elif explicit_catalog:
        sources = _csv(
            config.get("LAST30DAYS_SERVICE_SOURCES"),
            field="LAST30DAYS_SERVICE_SOURCES",
        )
    else:
        sources = DEFAULT_SERVICE_SOURCES

    unknown_sources = tuple(source for source in sources if source not in SOURCE_ACCESS_METHODS)
    if unknown_sources:
        raise ServiceSourcePolicyError(
            "LAST30DAYS_SERVICE_SOURCES contains unsupported source(s): "
            + ", ".join(unknown_sources)
        )

    access_orders: dict[str, tuple[str, ...]] = {}
    explicit_orders: set[str] = set()
    for source in sources:
        field = f"LAST30DAYS_{source.upper()}_ACCESS_ORDER"
        if field in config:
            methods = _csv(config.get(field), field=field)
            explicit_orders.add(source)
        else:
            methods = _default_access_order(source, config)
        unsupported = tuple(
            method for method in methods if method not in SOURCE_ACCESS_METHODS[source]
        )
        if unsupported:
            raise ServiceSourcePolicyError(
                f"{field} contains unsupported method(s): {', '.join(unsupported)}"
            )
        access_orders[source] = methods

    return ServiceSourcePolicy(
        sources=sources,
        access_orders=access_orders,
        explicit_source_catalog=explicit_catalog,
        explicit_access_orders=frozenset(explicit_orders),
    )
