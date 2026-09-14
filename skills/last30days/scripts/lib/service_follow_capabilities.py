"""Closed provider-native capability declarations for tailored follows."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Callable, Iterable, Mapping


class FollowCapabilityError(ValueError):
    pass


@dataclass(frozen=True)
class FollowCapabilityV1:
    source: str
    target_kind: str
    state: str
    reason_code: str | None = None
    validator: Callable[[str], str] | None = None

    def __post_init__(self) -> None:
        if self.state not in {"available", "unavailable", "unsupported"}:
            raise FollowCapabilityError("capability state is invalid")
        if self.state == "available" and self.validator is None:
            raise FollowCapabilityError("available capability requires validator")
        if self.state != "available" and not self.reason_code:
            raise FollowCapabilityError("non-available capability requires reason_code")


@dataclass(frozen=True)
class FollowTargetV1:
    source: str
    target_kind: str
    canonical_id: str
    selector: dict[str, str]
    access_partition_id: str


class FollowCapabilityRegistry:
    def __init__(self, capabilities: Iterable[FollowCapabilityV1]) -> None:
        indexed: dict[tuple[str, str], FollowCapabilityV1] = {}
        for capability in capabilities:
            key = (capability.source, capability.target_kind)
            if key in indexed:
                raise FollowCapabilityError("duplicate follow capability")
            indexed[key] = capability
        self._indexed = indexed

    def capability(self, source: str, target_kind: str) -> FollowCapabilityV1:
        return self._indexed.get(
            (source, target_kind),
            FollowCapabilityV1(source, target_kind, "unsupported", "unsupported_target"),
        )

    @property
    def digest(self) -> str:
        rows = [
            {"source": item.source, "target_kind": item.target_kind, "state": item.state, "reason_code": item.reason_code}
            for item in sorted(self._indexed.values(), key=lambda item: (item.source, item.target_kind))
        ]
        encoded = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
        return "sha256:" + hashlib.sha256(encoded).hexdigest()


def _identity(value: str) -> str:
    if not value:
        raise FollowCapabilityError("follow target is empty")
    return value


DEFAULT_FOLLOW_CAPABILITIES = FollowCapabilityRegistry(
    [
        *(FollowCapabilityV1("x", kind, "available", validator=_identity) for kind in ("feed", "topic", "account", "list")),
        FollowCapabilityV1("reddit", "community", "unavailable", "adapter_not_implemented"),
        FollowCapabilityV1("reddit", "user", "unavailable", "adapter_not_implemented"),
        FollowCapabilityV1("youtube", "channel", "unavailable", "adapter_not_implemented"),
    ]
)


def compatibility_trace(rows: Iterable[Mapping[str, object]]) -> dict[str, object]:
    """Classify disposable historical payloads without changing them."""
    counts = {"preserved": 0, "mapped": 0, "quarantined": 0}
    for row in rows:
        if row.get("collection_purpose", "general") != "tailored_follow":
            counts["preserved"] += 1
            continue
        capability = DEFAULT_FOLLOW_CAPABILITIES.capability(str(row.get("source", "")), str(row.get("surface_kind", "")))
        counts["mapped" if capability.state == "available" else "quarantined"] += 1
    encoded = json.dumps(counts, sort_keys=True, separators=(",", ":")).encode()
    return {**counts, "digest": "sha256:" + hashlib.sha256(encoded).hexdigest()}
