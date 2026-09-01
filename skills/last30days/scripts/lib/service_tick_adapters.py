"""Installed capability registry for config-driven durable tick providers."""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import Callable


_SAFE_NAME = re.compile(r"^[a-z0-9][a-z0-9_.-]{0,127}$")


class AdapterRegistryError(ValueError):
    """Raised when config asks for an absent or incompatible adapter."""


@dataclass(frozen=True)
class AdapterSpec:
    """Non-secret capability declaration for one installed adapter type."""

    adapter_type: str
    capabilities: frozenset[str]
    source_kinds: frozenset[str] | None = None
    runner: Callable[[object], object] | None = None
    normalization_proof_ref: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.adapter_type, str) or not _SAFE_NAME.fullmatch(
            self.adapter_type
        ):
            raise AdapterRegistryError("adapter_type must be a safe identifier")
        if not self.capabilities or any(
            not isinstance(value, str) or not _SAFE_NAME.fullmatch(value)
            for value in self.capabilities
        ):
            raise AdapterRegistryError("capabilities must be safe identifiers")
        if self.source_kinds is not None and (
            not self.source_kinds
            or any(
                not isinstance(value, str) or not _SAFE_NAME.fullmatch(value)
                for value in self.source_kinds
            )
        ):
            raise AdapterRegistryError("source_kinds must be safe identifiers")
        if self.normalization_proof_ref is not None and (
            not isinstance(self.normalization_proof_ref, str)
            or not self.normalization_proof_ref.strip()
            or len(self.normalization_proof_ref) > 512
        ):
            raise AdapterRegistryError(
                "normalization_proof_ref must be a bounded non-empty string"
            )

    def admits(self, *, source: str, capability: str) -> bool:
        return capability in self.capabilities and (
            self.source_kinds is None or source in self.source_kinds
        )

    def collect(self, context: object) -> object:
        if self.runner is None:
            raise AdapterRegistryError(
                f"adapter has no installed runner: {self.adapter_type}"
            )
        return self.runner(context)


class AdapterRegistry:
    """Exact registry; config cannot turn a path or module into executable code."""

    def __init__(self, specs: Iterable[AdapterSpec] = ()) -> None:
        installed: dict[str, AdapterSpec] = {}
        for spec in specs:
            if not isinstance(spec, AdapterSpec):
                raise TypeError("adapter registry entries must be AdapterSpec values")
            if spec.adapter_type in installed:
                raise AdapterRegistryError(
                    f"duplicate installed adapter: {spec.adapter_type}"
                )
            installed[spec.adapter_type] = spec
        self._installed = installed

    @property
    def adapter_types(self) -> tuple[str, ...]:
        return tuple(sorted(self._installed))

    def require(
        self, adapter_type: str, *, source: str, capability: str
    ) -> AdapterSpec:
        spec = self._installed.get(adapter_type)
        if spec is None:
            raise AdapterRegistryError(f"adapter is not installed: {adapter_type}")
        if not spec.admits(source=source, capability=capability):
            raise AdapterRegistryError(
                f"adapter {adapter_type} does not declare {capability} for {source}"
            )
        return spec


def next_provider_ordinal(
    providers: Sequence[Mapping[str, object]],
    *,
    current_ordinal: int,
    failure_class: str,
) -> int | None:
    """Return only the immediately next configured provider when eligible."""
    if (
        isinstance(current_ordinal, bool)
        or not isinstance(current_ordinal, int)
        or not 0 <= current_ordinal < len(providers)
    ):
        raise ValueError("current_ordinal is outside the provider chain")
    if not isinstance(failure_class, str) or not _SAFE_NAME.fullmatch(failure_class):
        raise ValueError("failure_class must be a safe identifier")
    fallback_on = providers[current_ordinal].get("fallback_on")
    if not isinstance(fallback_on, list) or any(
        not isinstance(value, str) for value in fallback_on
    ):
        raise ValueError("provider fallback_on must be a string list")
    next_ordinal = current_ordinal + 1
    if failure_class not in fallback_on or next_ordinal >= len(providers):
        return None
    return next_ordinal


def should_retry_provider(
    provider: Mapping[str, object],
    *,
    failure_class: str,
    retry_ordinal: int,
) -> bool:
    """Retry transient failures while another configured attempt remains."""
    if (
        isinstance(retry_ordinal, bool)
        or not isinstance(retry_ordinal, int)
        or retry_ordinal < 0
    ):
        raise ValueError("retry_ordinal must be a non-negative integer")
    limits = provider.get("limits")
    if not isinstance(limits, Mapping):
        raise ValueError("provider limits must be an object")
    attempts = limits.get("attempts")
    if isinstance(attempts, bool) or not isinstance(attempts, int):
        raise ValueError("provider attempts limit must be an integer")
    return failure_class == "transient" and retry_ordinal + 1 < attempts


def default_adapter_registry() -> AdapterRegistry:
    """Built-in declarations; deployments may inject a different registry."""
    collect = frozenset({"collect"})
    return AdapterRegistry(
        [
            AdapterSpec("agent_browser", collect),
            AdapterSpec("keyless", collect),
            AdapterSpec("paid_api", collect),
            AdapterSpec(
                "reddit_agent_browser",
                collect,
                frozenset({"reddit"}),
                normalization_proof_ref=(
                    "fixture:tests/test_service_tick_runtime.py:"
                    "test_installed_worker_adapters_preserve_nonzero_normalized_items:"
                    "reddit_agent_browser"
                ),
            ),
            AdapterSpec(
                "reddit_keyless",
                collect,
                frozenset({"reddit"}),
                normalization_proof_ref=(
                    "fixture:tests/test_service_tick_runtime.py:"
                    "test_installed_worker_adapters_preserve_nonzero_normalized_items:"
                    "reddit_keyless"
                ),
            ),
            AdapterSpec(
                "reddit_scrapecreators",
                collect,
                frozenset({"reddit"}),
                normalization_proof_ref=(
                    "fixture:tests/test_service_tick_runtime.py:"
                    "test_installed_worker_adapters_preserve_nonzero_normalized_items:"
                    "reddit_scrapecreators"
                ),
            ),
            AdapterSpec("scrapecreators", collect),
            AdapterSpec("youtube_yt_dlp", collect, frozenset({"youtube"})),
            AdapterSpec(
                "youtube_ytdlp",
                collect,
                frozenset({"youtube"}),
                normalization_proof_ref=(
                    "fixture:tests/test_service_tick_runtime.py:"
                    "test_installed_worker_adapters_preserve_nonzero_normalized_items:"
                    "youtube_ytdlp"
                ),
            ),
            AdapterSpec("yt_dlp", collect, frozenset({"youtube"})),
        ]
    )
