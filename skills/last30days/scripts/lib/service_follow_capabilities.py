"""Closed provider-native capability declarations for tailored follows."""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass

from .service_source_policy import load_service_source_policy


class FollowCapabilityError(ValueError):
    pass


@dataclass(frozen=True)
class FollowCapabilityV1:
    source: str
    target_kind: str
    state: str
    reason_code: str | None = None
    validator: Callable[[str], str] | None = None
    selector_field: str = ""
    route: str = ""
    access_method: str = ""
    identity_kind: str = "provider_native"
    locator_forms: tuple[str, ...] = ()
    operations: tuple[str, ...] = (
        "create_disabled",
        "get",
        "list",
        "update",
        "pause",
        "resume",
        "archive",
        "run",
    )
    interval_seconds_min: int = 60
    interval_seconds_max: int = 31_536_000
    item_limit_max: int = 100
    injected_transport: bool = False

    def __post_init__(self) -> None:
        if self.state not in {"available", "unavailable", "unsupported"}:
            raise FollowCapabilityError("capability state is invalid")
        if self.state == "available" and self.validator is None:
            raise FollowCapabilityError("available capability requires validator")
        if self.state == "available" and not (
            self.route and self.selector_field and self.access_method
        ):
            raise FollowCapabilityError(
                "available capability requires route, selector, and access method"
            )
        if (
            not 60
            <= self.interval_seconds_min
            <= self.interval_seconds_max
            <= 31_536_000
            or not 1 <= self.item_limit_max <= 100
        ):
            raise FollowCapabilityError("capability bounds exceed collection limits")
        if self.state != "available" and not self.reason_code:
            raise FollowCapabilityError("non-available capability requires reason_code")

    def to_dict(self) -> dict[str, object]:
        return {
            "source": self.source,
            "target_kind": self.target_kind,
            "contract_version": 1,
            "state": self.state,
            "reason_code": self.reason_code,
            "selector_field": self.selector_field,
            "route": self.route,
            "access_method": self.access_method,
            "identity_kind": self.identity_kind,
            "locator_forms": list(self.locator_forms),
            "operations": list(self.operations),
            "authentication_class": "authenticated_partition",
            "access_partition_required": True,
            "resolution_required": False,
            "live_resolution_supported": False,
            "bounds": {
                "interval_seconds_min": self.interval_seconds_min,
                "interval_seconds_max": self.interval_seconds_max,
                "item_limit_max": self.item_limit_max,
                "page_limit_max": 10,
            },
            "execution_mode": "injected_transport"
            if self.injected_transport
            else "installed_adapter",
        }


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
            FollowCapabilityV1(
                source, target_kind, "unsupported", "unsupported_target"
            ),
        )

    @property
    def available_targets(self) -> tuple[tuple[str, str], ...]:
        return tuple(
            sorted(
                key
                for key, value in self._indexed.items()
                if value.state == "available"
            )
        )

    @property
    def digest(self) -> str:
        rows = [
            item.to_dict()
            for item in sorted(
                self._indexed.values(), key=lambda item: (item.source, item.target_kind)
            )
        ]
        encoded = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
        return "sha256:" + hashlib.sha256(encoded).hexdigest()

    def catalog(self, config: Mapping[str, object], *, which=None) -> dict[str, object]:
        """Read-only declarations; neither dependency discovery nor fixtures enable work."""
        policy = load_service_source_policy(config)
        rows = []
        for item in sorted(
            self._indexed.values(), key=lambda row: (row.source, row.target_kind)
        ):
            row = item.to_dict()
            reason = None
            if item.source not in policy.sources:
                reason = "source_disabled"
            elif item.access_method not in policy.access_order(item.source):
                reason = "access_method_disabled"
            elif not policy.method_available(
                item.source, item.access_method, config, which=which
            ):
                reason = (
                    "missing_tool"
                    if item.access_method in {"yt_dlp", "agent_browser"}
                    else "missing_credential"
                )
            row["dependency_readiness"] = {
                "state": "unavailable" if reason else "ready",
                "reason_code": reason,
            }
            execution_reason = reason or (
                "transport_not_configured" if item.injected_transport else None
            )
            row["execution_readiness"] = {
                "state": "unavailable" if execution_reason else "ready",
                "reason_code": execution_reason,
            }
            rows.append(row)
        return {"schema_version": 1, "registry_digest": self.digest, "targets": rows}


def _identity(value: str) -> str:
    if not value:
        raise FollowCapabilityError("follow target is empty")
    return value


def canonical_reddit_community(value: str) -> str:
    if not isinstance(value, str):
        raise FollowCapabilityError("malformed_target")
    candidate = value.casefold().removeprefix("r/")
    if re.fullmatch(r"[a-z0-9_]{3,21}", candidate, re.ASCII) is None:
        raise FollowCapabilityError("malformed_target")
    return candidate


def canonical_reddit_user(value: str) -> str:
    if not isinstance(value, str):
        raise FollowCapabilityError("malformed_target")
    candidate = value.casefold().removeprefix("u/")
    if re.fullmatch(r"[a-z0-9_-]{3,20}", candidate, re.ASCII) is None:
        raise FollowCapabilityError("malformed_target")
    return candidate


def canonical_youtube_channel(value: str) -> str:
    if not isinstance(value, str):
        raise FollowCapabilityError("malformed_target")
    if value.startswith(("@", "http://", "https://")):
        raise FollowCapabilityError("unresolved_target")
    if re.fullmatch(r"UC[A-Za-z0-9_-]{22}", value, re.ASCII) is None:
        raise FollowCapabilityError("malformed_target")
    return value


DEFAULT_FOLLOW_CAPABILITIES = FollowCapabilityRegistry(
    [
        *(
            FollowCapabilityV1(
                "x",
                kind,
                "available",
                validator=_identity,
                selector_field="list_id" if kind == "list" else kind,
                route=f"x_{kind}",
                access_method="agent_browser",
                identity_kind="accepted_x_identity",
            )
            for kind in ("feed", "topic", "account", "list")
        ),
        FollowCapabilityV1(
            "reddit",
            "community",
            "available",
            validator=canonical_reddit_community,
            selector_field="community",
            route="reddit_community_posts",
            access_method="keyless",
            locator_forms=("name", "r/name"),
            injected_transport=True,
        ),
        FollowCapabilityV1(
            "reddit",
            "user",
            "available",
            validator=canonical_reddit_user,
            selector_field="user",
            route="reddit_user_posts",
            access_method="keyless",
            locator_forms=("name", "u/name"),
            injected_transport=True,
        ),
        FollowCapabilityV1(
            "youtube",
            "channel",
            "available",
            validator=canonical_youtube_channel,
            selector_field="channel",
            route="youtube_channel_uploads",
            access_method="yt_dlp",
            locator_forms=("channel_id",),
            injected_transport=True,
        ),
    ]
)


def validate_native_request(
    request, config: Mapping[str, object], source: str
) -> FollowTargetV1:
    """Bind native routing to the frozen cause, identity and access partition."""
    context = request.collection_context
    capability = DEFAULT_FOLLOW_CAPABILITIES.capability(source, request.surface_kind)
    if (
        request.source != source
        or context is None
        or context.collection_purpose != "tailored_follow"
    ):
        raise FollowCapabilityError("route_mismatch")
    if (
        not capability.injected_transport
        or context.surface_kind != request.surface_kind
    ):
        raise FollowCapabilityError("unsupported_target")
    selector = context.selector
    if set(selector) != {capability.selector_field} or capability.validator is None:
        raise FollowCapabilityError("route_mismatch")
    native_id = capability.validator(selector[capability.selector_field])
    if selector[capability.selector_field] != native_id or request.query != native_id:
        raise FollowCapabilityError("route_mismatch")
    canonical = lambda value: json.dumps(
        value,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
        allow_nan=False,
    )
    selector_digest = (
        "sha256:" + hashlib.sha256(canonical(selector).encode()).hexdigest()
    )
    identity = {
        "source": source,
        "surface_kind": request.surface_kind,
        "selector": selector,
        "access_partition_id": context.access_partition_id,
    }
    target_id = (
        "follow-target-" + hashlib.sha256(canonical(identity).encode()).hexdigest()[:32]
    )
    if (
        context.selector_digest != selector_digest
        or context.follow_target_id != target_id
    ):
        raise FollowCapabilityError("route_mismatch")
    if context.access_partition_id != f"profile:{request.profile_id}":
        raise FollowCapabilityError("unauthorized_target")
    adapters = {
        "reddit": {"reddit_keyless", "reddit_api"},
        "youtube": {"youtube_ytdlp"},
    }
    policy = load_service_source_policy(config)
    if (
        source not in policy.sources
        or capability.access_method not in policy.access_order(source)
    ):
        raise FollowCapabilityError("unauthorized_target")
    if (
        request.adapter not in adapters[source]
        or not 1 <= request.item_limit <= capability.item_limit_max
    ):
        raise FollowCapabilityError("route_mismatch")
    return FollowTargetV1(
        source,
        request.surface_kind,
        native_id,
        dict(selector),
        context.access_partition_id,
    )


def compatibility_trace(rows: Iterable[Mapping[str, object]]) -> dict[str, object]:
    """Classify disposable historical payloads without changing them."""
    counts = {"preserved": 0, "mapped": 0, "quarantined": 0}
    classified: dict[str, list[str]] = {key: [] for key in counts}
    for row in rows:
        if row.get("collection_purpose", "general") != "tailored_follow":
            classification = "preserved"
        else:
            capability = DEFAULT_FOLLOW_CAPABILITIES.capability(
                str(row.get("source", "")), str(row.get("surface_kind", ""))
            )
            classification = (
                "mapped" if capability.state == "available" else "quarantined"
            )
            if classification == "mapped" and capability.source != "x":
                # Native compatibility requires the actual persisted spec, not
                # merely a newly available source/kind pair.
                from .service_collection import CollectionSpec

                try:
                    if CollectionSpec.from_dict(row).is_quarantined_follow:
                        classification = "quarantined"
                except (ValueError, TypeError, KeyError):
                    classification = "quarantined"
        identity = {
            key: row.get(key)
            for key in (
                "collection_spec_id",
                "spec_version",
                "source",
                "surface_kind",
                "selector_digest",
                "follow_target_id",
                "access_partition_id",
            )
            if row.get(key) is not None
        }
        encoded_identity = json.dumps(
            identity, sort_keys=True, separators=(",", ":")
        ).encode()
        classified[classification].append(hashlib.sha256(encoded_identity).hexdigest())
        counts[classification] += 1
    class_digests = {
        key: "sha256:"
        + hashlib.sha256(
            json.dumps(sorted(values), separators=(",", ":")).encode()
        ).hexdigest()
        for key, values in classified.items()
    }
    encoded = json.dumps(
        {"counts": counts, "class_digests": class_digests},
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    return {
        **counts,
        "class_digests": class_digests,
        "digest": "sha256:" + hashlib.sha256(encoded).hexdigest(),
    }
