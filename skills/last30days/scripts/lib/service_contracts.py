"""Versioned public contracts for the last30days intelligence service.

The service, CLI, and MCP adapters exchange these envelopes.  Validation lives
at this seam so callers do not need to understand storage or acquisition
implementation details.
"""

from __future__ import annotations

import base64
import binascii
import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from pathlib import Path
from typing import Any, ClassVar, Mapping
from urllib.parse import urlparse


SCHEMA_VERSION = 1
SAFE_ERROR_CODE = re.compile(r"^[a-z][a-z0-9_]{0,63}$")
SCHEMA_CATALOG_PATH = (
    Path(__file__).resolve().parents[2]
    / "schemas"
    / f"service-contracts-v{SCHEMA_VERSION}.json"
)
SCHEMA_CATALOG_SHA256 = hashlib.sha256(SCHEMA_CATALOG_PATH.read_bytes()).hexdigest()
MAX_ACQUISITION_BINARY_EVIDENCE_BYTES = 524_288
FORBIDDEN_LEDGER_FIELDS = frozenset(
    {
        "access_token",
        "api_key",
        "auth_token",
        "authorization",
        "browser_id",
        "cookie",
        "cookies",
        "credential",
        "credentials",
        "ct0",
        "display_id",
        "operator_url",
        "password",
        "refresh_token",
        "route_id",
        "secret",
        "session_name",
        "tab_id",
        "user_data_dir",
    }
)


class ContractValidationError(ValueError):
    """Raised when an external service envelope violates its contract."""


def load_schema_catalog(path: Path | None = None) -> dict[str, Any]:
    """Load and minimally validate the canonical shipped JSON Schema catalog."""
    catalog_path = path or SCHEMA_CATALOG_PATH
    try:
        payload = json.loads(catalog_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractValidationError(
            f"unable to load schema catalog: {catalog_path}"
        ) from exc
    if not isinstance(payload, dict):
        raise ContractValidationError("schema catalog must be an object")
    if payload.get("schema_version") != SCHEMA_VERSION:
        raise ContractValidationError(
            f"schema catalog version must be {SCHEMA_VERSION}"
        )
    contracts = payload.get("contracts")
    if not isinstance(contracts, dict):
        raise ContractValidationError("schema catalog contracts must be an object")
    return payload


class FreshnessPolicy(StrEnum):
    CACHE_ONLY = "cache_only"
    PREFER_CACHE = "prefer_cache"
    REFRESH_IF_STALE = "refresh_if_stale"
    FORCE_REFRESH = "force_refresh"


class ResponseMode(StrEnum):
    EVIDENCE = "evidence"
    BRIEF = "brief"


class CacheStatus(StrEnum):
    FRESH = "fresh"
    STALE = "stale"
    MISS = "miss"


class ServiceStatus(StrEnum):
    STARTING = "starting"
    READY = "ready"
    DEGRADED = "degraded"


class AcquisitionStatus(StrEnum):
    SUCCEEDED = "succeeded"
    PARTIAL = "partial"
    FAILED = "failed"
    AWAITING_OPERATOR = "awaiting_operator"


class RetryClass(StrEnum):
    NONE = "none"
    OPERATOR = "operator"
    RATE_LIMIT = "rate_limit"
    TRANSIENT = "transient"
    CONFIGURATION = "configuration"
    CONTENT = "content"
    PERMANENT = "permanent"


class RetentionClass(StrEnum):
    EPHEMERAL = "ephemeral"
    CACHE = "cache"
    DURABLE = "durable"


class RedactionClass(StrEnum):
    PUBLIC = "public"
    AUTHENTICATED = "authenticated"
    RESTRICTED = "restricted"


class JobType(StrEnum):
    REFRESH = "refresh"
    ENRICHMENT = "enrichment"
    MAINTENANCE = "maintenance"


class JobState(StrEnum):
    QUEUED = "queued"
    PLANNING = "planning"
    ACQUIRING = "acquiring"
    NORMALIZING = "normalizing"
    INDEXING = "indexing"
    ENRICHING = "enriching"
    VALIDATING = "validating"
    PUBLISHED = "published"
    PARTIAL = "partial"
    FAILED = "failed"
    AWAITING_OPERATOR = "awaiting_operator"


class TickTrigger(StrEnum):
    MANUAL = "manual"
    TIMER = "timer"


class TickState(StrEnum):
    QUEUED = "queued"
    PREFLIGHT = "preflight"
    COLLECTING = "collecting"
    ANALYZING = "analyzing"
    CATALOGING = "cataloging"
    INDEXING = "indexing"
    COMPLETE = "complete"
    COMPLETE_DEGRADED = "complete_degraded"
    FAILED = "failed"
    MISSED_DUE_TO_OVERLAP = "missed_due_to_overlap"


class TickLaneState(StrEnum):
    READY = "ready"
    SUCCESS = "success"
    EMPTY = "empty"
    UNSUPPORTED = "unsupported"
    FAILURE = "failure"
    BLOCKED_HUMAN = "blocked_human"
    BUDGET_EXHAUSTED = "budget_exhausted"


def _require_exact_fields(
    payload: Mapping[str, Any],
    *,
    required: frozenset[str],
    optional: frozenset[str] = frozenset(),
) -> None:
    missing = sorted(required - payload.keys())
    if missing:
        raise ContractValidationError(f"missing fields: {', '.join(missing)}")
    unknown = sorted(payload.keys() - required - optional)
    if unknown:
        raise ContractValidationError(f"unknown fields: {', '.join(unknown)}")


def _require_non_empty_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ContractValidationError(f"{field} must be a non-empty string")
    return value


def _require_bounded_string(value: Any, field: str, maximum: int) -> str:
    value = _require_non_empty_string(value, field)
    if len(value) > maximum:
        raise ContractValidationError(f"{field} cannot exceed {maximum} characters")
    return value


def _require_integer_between(value: Any, field: str, minimum: int, maximum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ContractValidationError(f"{field} must be an integer")
    if not minimum <= value <= maximum:
        raise ContractValidationError(
            f"{field} must be between {minimum} and {maximum}"
        )
    return value


def _validate_schema_version(value: Any) -> int:
    if value != SCHEMA_VERSION:
        raise ContractValidationError(
            f"schema_version must be {SCHEMA_VERSION}, got {value!r}"
        )
    return SCHEMA_VERSION


def _validate_json_object(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ContractValidationError(f"{field} must be an object")
    copied = dict(value)
    try:
        json.dumps(copied, allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise ContractValidationError(f"{field} must contain valid JSON") from exc
    _reject_forbidden_ledger_fields(copied, field)
    return copied


def _reject_forbidden_ledger_fields(value: Any, path: str) -> None:
    if isinstance(value, Mapping):
        for key, nested in value.items():
            normalized = str(key).strip().lower().replace("-", "_")
            if normalized in FORBIDDEN_LEDGER_FIELDS:
                raise ContractValidationError(
                    f"forbidden field in service ledger: {path}.{key}"
                )
            _reject_forbidden_ledger_fields(nested, f"{path}.{key}")
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            _reject_forbidden_ledger_fields(nested, f"{path}[{index}]")


def _validate_filters(value: Any) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ContractValidationError("filters must be an object")
    filters = dict(value)
    allowed = {"sources", "topic_ids", "published_after", "published_before"}
    unknown = sorted(set(filters) - allowed)
    if unknown:
        raise ContractValidationError(
            f"unknown filter fields: {', '.join(unknown)}"
        )
    for field in ("sources", "topic_ids"):
        if field in filters:
            items = filters[field]
            if not isinstance(items, list) or not all(
                isinstance(item, str) and item.strip() for item in items
            ):
                raise ContractValidationError(
                    f"filters.{field} must be a list of non-empty strings"
                )
            filters[field] = list(items)
    for field in ("published_after", "published_before"):
        if field in filters:
            _require_non_empty_string(filters[field], f"filters.{field}")
    return filters


@dataclass(frozen=True)
class QueryRequest:
    """One bounded cache query independent of transport and storage."""

    schema_version: int
    request_id: str
    profile_id: str
    query: str
    freshness_policy: FreshnessPolicy
    response_mode: ResponseMode
    filters: dict[str, Any]
    top_k: int
    max_chars: int
    wait_ms: int

    CONTRACT_NAME: ClassVar[str] = "query_request"

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> QueryRequest:
        if not isinstance(payload, Mapping):
            raise ContractValidationError("query request must be an object")
        _require_exact_fields(
            payload,
            required=frozenset(
                {
                    "schema_version",
                    "request_id",
                    "profile_id",
                    "query",
                    "freshness_policy",
                    "response_mode",
                    "filters",
                    "top_k",
                    "max_chars",
                    "wait_ms",
                }
            ),
        )
        try:
            freshness_policy = FreshnessPolicy(payload["freshness_policy"])
        except (TypeError, ValueError) as exc:
            raise ContractValidationError("invalid freshness_policy") from exc
        try:
            response_mode = ResponseMode(payload["response_mode"])
        except (TypeError, ValueError) as exc:
            raise ContractValidationError("invalid response_mode") from exc
        return cls(
            schema_version=_validate_schema_version(payload["schema_version"]),
            request_id=_require_bounded_string(
                payload["request_id"], "request_id", 128
            ),
            profile_id=_require_non_empty_string(
                payload["profile_id"], "profile_id"
            ),
            query=_require_non_empty_string(payload["query"], "query"),
            freshness_policy=freshness_policy,
            response_mode=response_mode,
            filters=_validate_filters(payload["filters"]),
            top_k=_require_integer_between(payload["top_k"], "top_k", 1, 100),
            max_chars=_require_integer_between(
                payload["max_chars"], "max_chars", 512, 65536
            ),
            wait_ms=_require_integer_between(
                payload["wait_ms"], "wait_ms", 0, 300000
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "request_id": self.request_id,
            "profile_id": self.profile_id,
            "query": self.query,
            "freshness_policy": self.freshness_policy.value,
            "response_mode": self.response_mode.value,
            "filters": dict(self.filters),
            "top_k": self.top_k,
            "max_chars": self.max_chars,
            "wait_ms": self.wait_ms,
        }


def _require_optional_string(value: Any, field: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ContractValidationError(f"{field} must be a string or null")
    return value


def _validate_timestamp(value: Any, field: str) -> datetime:
    text = _require_non_empty_string(value, field)
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ContractValidationError(
            f"{field} must be an ISO-8601 timestamp"
        ) from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ContractValidationError(f"{field} must include a timezone")
    return parsed.astimezone(timezone.utc)


def _canonical_timestamp(value: Any, field: str) -> str:
    return _validate_timestamp(value, field).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class TickRequest:
    """One manual or scheduled request for an immutable global tick interval."""

    schema_version: int
    schedule_id: str
    interval_from: str
    interval_to: str
    trigger: TickTrigger

    CONTRACT_NAME: ClassVar[str] = "tick_request"

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> TickRequest:
        if not isinstance(payload, Mapping):
            raise ContractValidationError("tick request must be an object")
        _require_exact_fields(
            payload,
            required=frozenset(
                {
                    "schema_version",
                    "schedule_id",
                    "interval_from",
                    "interval_to",
                    "trigger",
                }
            ),
        )
        interval_from = _canonical_timestamp(
            payload["interval_from"], "interval_from"
        )
        interval_to = _canonical_timestamp(payload["interval_to"], "interval_to")
        if interval_to <= interval_from:
            raise ContractValidationError("interval_to must be after interval_from")
        try:
            trigger = TickTrigger(payload["trigger"])
        except (TypeError, ValueError) as exc:
            raise ContractValidationError("invalid tick trigger") from exc
        return cls(
            schema_version=_validate_schema_version(payload["schema_version"]),
            schedule_id=_require_bounded_string(
                payload["schedule_id"], "schedule_id", 128
            ),
            interval_from=interval_from,
            interval_to=interval_to,
            trigger=trigger,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "schedule_id": self.schedule_id,
            "interval_from": self.interval_from,
            "interval_to": self.interval_to,
            "trigger": self.trigger.value,
        }


@dataclass(frozen=True)
class TickLaneReceipt:
    """Caller-visible state for one immutable service/target tick lane."""

    schema_version: int
    lane_id: str
    service_id: str
    target_id: str
    access_partition_id: str
    state: TickLaneState

    CONTRACT_NAME: ClassVar[str] = "tick_lane_receipt"

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> TickLaneReceipt:
        if not isinstance(payload, Mapping):
            raise ContractValidationError("tick lane receipt must be an object")
        _require_exact_fields(
            payload,
            required=frozenset(
                {
                    "schema_version",
                    "lane_id",
                    "service_id",
                    "target_id",
                    "access_partition_id",
                    "state",
                }
            ),
        )
        try:
            state = TickLaneState(payload["state"])
        except (TypeError, ValueError) as exc:
            raise ContractValidationError("invalid tick lane state") from exc
        return cls(
            schema_version=_validate_schema_version(payload["schema_version"]),
            lane_id=_require_bounded_string(payload["lane_id"], "lane_id", 128),
            service_id=_require_bounded_string(
                payload["service_id"], "service_id", 128
            ),
            target_id=_require_bounded_string(
                payload["target_id"], "target_id", 128
            ),
            access_partition_id=_require_bounded_string(
                payload["access_partition_id"], "access_partition_id", 256
            ),
            state=state,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "lane_id": self.lane_id,
            "service_id": self.service_id,
            "target_id": self.target_id,
            "access_partition_id": self.access_partition_id,
            "state": self.state.value,
        }


@dataclass(frozen=True)
class TickReceipt:
    """Compact durable receipt returned by the deep tick interface."""

    schema_version: int
    tick_id: str
    schedule_id: str
    interval_from: str
    interval_to: str
    trigger: TickTrigger
    config_revision: str
    config_digest: str
    state: TickState
    execution_attempt_ids: tuple[str, ...]
    lanes: tuple[TickLaneReceipt, ...]
    stage_states: dict[str, str]
    budget_summary: dict[str, Any]
    provider_attempt_ids: tuple[str, ...]
    resource_lease_ids: tuple[str, ...]
    source_version_ids: tuple[str, ...]
    incident_ids: tuple[str, ...]
    incident_transition_ids: tuple[str, ...]
    notification_delivery_ids: tuple[str, ...]
    anomaly_result_ids: tuple[str, ...]
    artifact_ids: tuple[str, ...]
    derivative_ids: tuple[str, ...]
    catalog_cluster_ids: tuple[str, ...]
    snapshot_id: str | None
    head_promoted: bool
    manifest_digests: dict[str, str]
    receipt_manifests: dict[str, Any]
    coverage_gaps: tuple[str, ...]
    versions: dict[str, str]
    created_at: str
    updated_at: str

    CONTRACT_NAME: ClassVar[str] = "tick_receipt"

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> TickReceipt:
        if not isinstance(payload, Mapping):
            raise ContractValidationError("tick receipt must be an object")
        _require_exact_fields(
            payload,
            required=frozenset(
                {
                    "schema_version",
                    "tick_id",
                    "schedule_id",
                    "interval_from",
                    "interval_to",
                    "trigger",
                    "config_revision",
                    "config_digest",
                    "state",
                    "execution_attempt_ids",
                    "lanes",
                    "stage_states",
                    "budget_summary",
                    "provider_attempt_ids",
                    "resource_lease_ids",
                    "source_version_ids",
                    "incident_ids",
                    "incident_transition_ids",
                    "notification_delivery_ids",
                    "anomaly_result_ids",
                    "artifact_ids",
                    "derivative_ids",
                    "catalog_cluster_ids",
                    "snapshot_id",
                    "head_promoted",
                    "manifest_digests",
                    "receipt_manifests",
                    "coverage_gaps",
                    "versions",
                    "created_at",
                    "updated_at",
                }
            ),
        )
        try:
            trigger = TickTrigger(payload["trigger"])
            state = TickState(payload["state"])
        except (TypeError, ValueError) as exc:
            raise ContractValidationError("invalid tick receipt state") from exc
        raw_attempts = payload["execution_attempt_ids"]
        if not isinstance(raw_attempts, list) or not raw_attempts:
            raise ContractValidationError(
                "execution_attempt_ids must be a non-empty list"
            )
        attempt_ids = tuple(
            _require_bounded_string(value, "execution_attempt_ids", 128)
            for value in raw_attempts
        )
        if len(set(attempt_ids)) != len(attempt_ids):
            raise ContractValidationError("execution_attempt_ids must be unique")
        raw_lanes = payload["lanes"]
        if not isinstance(raw_lanes, list) or len(raw_lanes) > 100_000:
            raise ContractValidationError("lanes must be a bounded list")
        lanes = tuple(TickLaneReceipt.from_dict(value) for value in raw_lanes)
        if len({lane.lane_id for lane in lanes}) != len(lanes):
            raise ContractValidationError("lane IDs must be unique")

        def identifiers(field: str) -> tuple[str, ...]:
            values = payload[field]
            if not isinstance(values, list) or len(values) > 1_000_000:
                raise ContractValidationError(f"{field} must be a bounded list")
            result = tuple(
                _require_bounded_string(value, field, 256) for value in values
            )
            if len(set(result)) != len(result):
                raise ContractValidationError(f"{field} must be unique")
            return result

        stage_states = _validate_json_object(payload["stage_states"], "stage_states")
        if any(
            not isinstance(key, str) or not isinstance(value, str)
            for key, value in stage_states.items()
        ):
            raise ContractValidationError("stage_states must map strings to strings")
        budget_summary = _validate_json_object(
            payload["budget_summary"], "budget_summary"
        )
        _reject_forbidden_ledger_fields(budget_summary, "budget_summary")
        manifest_digests = _validate_json_object(
            payload["manifest_digests"], "manifest_digests"
        )
        if any(
            not isinstance(key, str)
            or not isinstance(value, str)
            or re.fullmatch(r"sha256:[0-9a-f]{64}", value) is None
            for key, value in manifest_digests.items()
        ):
            raise ContractValidationError("manifest_digests must contain sha256 values")
        receipt_manifests = _validate_json_object(
            payload["receipt_manifests"], "receipt_manifests"
        )
        if set(receipt_manifests) != set(manifest_digests):
            raise ContractValidationError(
                "receipt_manifests must exactly match manifest_digests"
            )
        versions = _validate_json_object(payload["versions"], "versions")
        if any(
            not isinstance(key, str) or not isinstance(value, str) or not value
            for key, value in versions.items()
        ):
            raise ContractValidationError("versions must map strings to strings")
        snapshot_id = payload["snapshot_id"]
        if snapshot_id is not None:
            snapshot_id = _require_bounded_string(snapshot_id, "snapshot_id", 128)
        if not isinstance(payload["head_promoted"], bool):
            raise ContractValidationError("head_promoted must be boolean")
        interval_from = _canonical_timestamp(
            payload["interval_from"], "interval_from"
        )
        interval_to = _canonical_timestamp(payload["interval_to"], "interval_to")
        if interval_to <= interval_from:
            raise ContractValidationError("interval_to must be after interval_from")
        config_digest = _require_bounded_string(
            payload["config_digest"], "config_digest", 71
        )
        if re.fullmatch(r"sha256:[0-9a-f]{64}", config_digest) is None:
            raise ContractValidationError("config_digest must be a sha256 digest")
        created_at = _canonical_timestamp(payload["created_at"], "created_at")
        updated_at = _canonical_timestamp(payload["updated_at"], "updated_at")
        if updated_at < created_at:
            raise ContractValidationError("updated_at cannot precede created_at")
        return cls(
            schema_version=_validate_schema_version(payload["schema_version"]),
            tick_id=_require_bounded_string(payload["tick_id"], "tick_id", 128),
            schedule_id=_require_bounded_string(
                payload["schedule_id"], "schedule_id", 128
            ),
            interval_from=interval_from,
            interval_to=interval_to,
            trigger=trigger,
            config_revision=_require_bounded_string(
                payload["config_revision"], "config_revision", 128
            ),
            config_digest=config_digest,
            state=state,
            execution_attempt_ids=attempt_ids,
            lanes=lanes,
            stage_states={str(key): str(value) for key, value in stage_states.items()},
            budget_summary=budget_summary,
            provider_attempt_ids=identifiers("provider_attempt_ids"),
            resource_lease_ids=identifiers("resource_lease_ids"),
            source_version_ids=identifiers("source_version_ids"),
            incident_ids=identifiers("incident_ids"),
            incident_transition_ids=identifiers("incident_transition_ids"),
            notification_delivery_ids=identifiers("notification_delivery_ids"),
            anomaly_result_ids=identifiers("anomaly_result_ids"),
            artifact_ids=identifiers("artifact_ids"),
            derivative_ids=identifiers("derivative_ids"),
            catalog_cluster_ids=identifiers("catalog_cluster_ids"),
            snapshot_id=snapshot_id,
            head_promoted=payload["head_promoted"],
            manifest_digests={
                str(key): str(value) for key, value in manifest_digests.items()
            },
            receipt_manifests=receipt_manifests,
            coverage_gaps=identifiers("coverage_gaps"),
            versions={str(key): str(value) for key, value in versions.items()},
            created_at=created_at,
            updated_at=updated_at,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "tick_id": self.tick_id,
            "schedule_id": self.schedule_id,
            "interval_from": self.interval_from,
            "interval_to": self.interval_to,
            "trigger": self.trigger.value,
            "config_revision": self.config_revision,
            "config_digest": self.config_digest,
            "state": self.state.value,
            "execution_attempt_ids": list(self.execution_attempt_ids),
            "lanes": [lane.to_dict() for lane in self.lanes],
            "stage_states": dict(self.stage_states),
            "budget_summary": dict(self.budget_summary),
            "provider_attempt_ids": list(self.provider_attempt_ids),
            "resource_lease_ids": list(self.resource_lease_ids),
            "source_version_ids": list(self.source_version_ids),
            "incident_ids": list(self.incident_ids),
            "incident_transition_ids": list(self.incident_transition_ids),
            "notification_delivery_ids": list(self.notification_delivery_ids),
            "anomaly_result_ids": list(self.anomaly_result_ids),
            "artifact_ids": list(self.artifact_ids),
            "derivative_ids": list(self.derivative_ids),
            "catalog_cluster_ids": list(self.catalog_cluster_ids),
            "snapshot_id": self.snapshot_id,
            "head_promoted": self.head_promoted,
            "manifest_digests": dict(self.manifest_digests),
            "receipt_manifests": dict(self.receipt_manifests),
            "coverage_gaps": list(self.coverage_gaps),
            "versions": dict(self.versions),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


def _require_confidence(value: Any) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ContractValidationError("confidence must be numeric")
    confidence = float(value)
    if not 0 <= confidence <= 1:
        raise ContractValidationError("confidence must be between 0 and 1")
    return confidence


def _validate_scores(value: Any) -> dict[str, float]:
    if not isinstance(value, Mapping):
        raise ContractValidationError("scores must be an object")
    required = frozenset({"lexical", "semantic", "graph", "recency", "fused"})
    _require_exact_fields(value, required=required)
    scores: dict[str, float] = {}
    for name in sorted(required):
        score = value[name]
        if isinstance(score, bool) or not isinstance(score, (int, float)):
            raise ContractValidationError(f"scores.{name} must be numeric")
        numeric = float(score)
        if not 0 <= numeric <= 1:
            raise ContractValidationError(
                f"scores.{name} must be between 0 and 1"
            )
        scores[name] = numeric
    return scores


def _validate_media(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list) or len(value) > 16:
        raise ContractValidationError("media must be a bounded array")
    fields = frozenset(
        {
            "kind",
            "url",
            "preview_url",
            "mime_type",
            "width",
            "height",
            "duration_seconds",
            "alt_text",
        }
    )
    assets: list[dict[str, Any]] = []
    for raw in value:
        if not isinstance(raw, Mapping):
            raise ContractValidationError("media items must be objects")
        _require_exact_fields(raw, required=fields)
        kind = raw["kind"]
        if kind not in {"image", "video"}:
            raise ContractValidationError("media.kind must be image or video")
        asset: dict[str, Any] = {
            "kind": kind,
            "url": _require_bounded_string(raw["url"], "media.url", 4096),
            "preview_url": _require_optional_string(
                raw["preview_url"], "media.preview_url"
            ),
            "mime_type": _require_optional_string(
                raw["mime_type"], "media.mime_type"
            ),
            "alt_text": _require_optional_string(raw["alt_text"], "media.alt_text"),
        }
        for name, maximum in (
            ("width", 100_000),
            ("height", 100_000),
            ("duration_seconds", 86_400),
        ):
            numeric = raw[name]
            asset[name] = (
                None
                if numeric is None
                else _require_integer_between(numeric, f"media.{name}", 0, maximum)
            )
        assets.append(asset)
    return assets


def _require_timestamp_text(value: Any, field: str) -> str:
    text = _require_non_empty_string(value, field)
    _validate_timestamp(text, field)
    return text


def _require_optional_timestamp_text(value: Any, field: str) -> str | None:
    if value is None:
        return None
    return _require_timestamp_text(value, field)


@dataclass(frozen=True)
class TemporalEvidenceRef:
    """Partition-safe evidence coordinates with explicit temporal semantics."""

    schema_version: int
    evidence_id: str
    document_id: str
    version_id: str
    chunk_id: str
    access_partition_id: str
    span_start: int
    span_end: int
    span_digest: str
    observed_at: str
    published_at: str | None
    valid_from: str | None
    valid_to: str | None
    system_from: str
    system_to: str | None

    CONTRACT_NAME: ClassVar[str] = "temporal_evidence_ref"

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> TemporalEvidenceRef:
        if not isinstance(payload, Mapping):
            raise ContractValidationError("temporal evidence ref must be an object")
        fields = frozenset(
            {
                "schema_version",
                "evidence_id",
                "document_id",
                "version_id",
                "chunk_id",
                "access_partition_id",
                "span_start",
                "span_end",
                "span_digest",
                "observed_at",
                "published_at",
                "valid_from",
                "valid_to",
                "system_from",
                "system_to",
            }
        )
        _require_exact_fields(payload, required=fields)
        span_start = _require_integer_between(
            payload["span_start"], "span_start", 0, 10_000_000
        )
        span_end = _require_integer_between(
            payload["span_end"], "span_end", 1, 10_000_000
        )
        if span_end <= span_start:
            raise ContractValidationError("span_end must be greater than span_start")
        return cls(
            schema_version=_validate_schema_version(payload["schema_version"]),
            evidence_id=_require_non_empty_string(
                payload["evidence_id"], "evidence_id"
            ),
            document_id=_require_non_empty_string(
                payload["document_id"], "document_id"
            ),
            version_id=_require_non_empty_string(payload["version_id"], "version_id"),
            chunk_id=_require_non_empty_string(payload["chunk_id"], "chunk_id"),
            access_partition_id=_require_non_empty_string(
                payload["access_partition_id"], "access_partition_id"
            ),
            span_start=span_start,
            span_end=span_end,
            span_digest=_require_non_empty_string(
                payload["span_digest"], "span_digest"
            ),
            observed_at=_require_timestamp_text(
                payload["observed_at"], "observed_at"
            ),
            published_at=_require_optional_timestamp_text(
                payload["published_at"], "published_at"
            ),
            valid_from=_require_optional_timestamp_text(
                payload["valid_from"], "valid_from"
            ),
            valid_to=_require_optional_timestamp_text(
                payload["valid_to"], "valid_to"
            ),
            system_from=_require_timestamp_text(
                payload["system_from"], "system_from"
            ),
            system_to=_require_optional_timestamp_text(
                payload["system_to"], "system_to"
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "evidence_id": self.evidence_id,
            "document_id": self.document_id,
            "version_id": self.version_id,
            "chunk_id": self.chunk_id,
            "access_partition_id": self.access_partition_id,
            "span_start": self.span_start,
            "span_end": self.span_end,
            "span_digest": self.span_digest,
            "observed_at": self.observed_at,
            "published_at": self.published_at,
            "valid_from": self.valid_from,
            "valid_to": self.valid_to,
            "system_from": self.system_from,
            "system_to": self.system_to,
        }


@dataclass(frozen=True)
class EvidenceItem:
    """One citation-ready retrieval result with replayable rank features."""

    schema_version: int
    evidence_id: str
    document_id: str
    source: str
    source_native_id: str
    url: str
    title: str
    snippet: str
    author: str | None
    published_at: str | None
    fetched_at: str
    acquisition_id: str
    content_hash: str
    scores: dict[str, float]
    media: list[dict[str, Any]]
    access_partition_id: str | None = None
    matching_channels: list[str] = field(default_factory=list)
    provenance: dict[str, Any] = field(default_factory=dict)

    CONTRACT_NAME: ClassVar[str] = "evidence_item"

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> EvidenceItem:
        if not isinstance(payload, Mapping):
            raise ContractValidationError("evidence item must be an object")
        required = frozenset(
            {
                "schema_version",
                "evidence_id",
                "document_id",
                "source",
                "source_native_id",
                "url",
                "title",
                "snippet",
                "author",
                "published_at",
                "fetched_at",
                "acquisition_id",
                "content_hash",
                "scores",
            }
        )
        _require_exact_fields(
            payload,
            required=required,
            optional=frozenset(
                {
                    "media",
                    "access_partition_id",
                    "matching_channels",
                    "provenance",
                }
            ),
        )
        raw_channels = payload.get("matching_channels", [])
        matching_channels = _require_string_list(raw_channels, "matching_channels")
        allowed_channels = {
            "lexical_source",
            "source_alt_text",
            "ocr",
            "semantic_source",
            "semantic_sidecar",
            "catalog",
        }
        if len(matching_channels) > 16 or len(matching_channels) != len(
            set(matching_channels)
        ) or (
            set(matching_channels) - allowed_channels
        ):
            raise ContractValidationError("matching_channels is invalid")
        access_partition_id = payload.get("access_partition_id")
        return cls(
            schema_version=_validate_schema_version(payload["schema_version"]),
            evidence_id=_require_non_empty_string(
                payload["evidence_id"], "evidence_id"
            ),
            document_id=_require_non_empty_string(
                payload["document_id"], "document_id"
            ),
            source=_require_non_empty_string(payload["source"], "source"),
            source_native_id=_require_non_empty_string(
                payload["source_native_id"], "source_native_id"
            ),
            url=_require_non_empty_string(payload["url"], "url"),
            title=_require_non_empty_string(payload["title"], "title"),
            snippet=_require_non_empty_string(payload["snippet"], "snippet"),
            author=_require_optional_string(payload["author"], "author"),
            published_at=_require_optional_string(
                payload["published_at"], "published_at"
            ),
            fetched_at=_require_non_empty_string(
                payload["fetched_at"], "fetched_at"
            ),
            acquisition_id=_require_non_empty_string(
                payload["acquisition_id"], "acquisition_id"
            ),
            content_hash=_require_non_empty_string(
                payload["content_hash"], "content_hash"
            ),
            scores=_validate_scores(payload["scores"]),
            media=_validate_media(payload.get("media", [])),
            access_partition_id=(
                _require_bounded_string(
                    access_partition_id, "access_partition_id", 256
                )
                if access_partition_id is not None
                else None
            ),
            matching_channels=matching_channels,
            provenance=_validate_json_object(
                payload.get("provenance", {}), "provenance"
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        payload = {
            "schema_version": self.schema_version,
            "evidence_id": self.evidence_id,
            "document_id": self.document_id,
            "source": self.source,
            "source_native_id": self.source_native_id,
            "url": self.url,
            "title": self.title,
            "snippet": self.snippet,
            "author": self.author,
            "published_at": self.published_at,
            "fetched_at": self.fetched_at,
            "acquisition_id": self.acquisition_id,
            "content_hash": self.content_hash,
            "scores": dict(self.scores),
            "media": [dict(asset) for asset in self.media],
        }
        if self.access_partition_id is not None:
            payload["access_partition_id"] = self.access_partition_id
        if self.matching_channels:
            payload["matching_channels"] = list(self.matching_channels)
        if self.provenance:
            payload["provenance"] = dict(self.provenance)
        return payload


@dataclass(frozen=True)
class QueryResponse:
    """Bounded, citation-ready response from the cache query authority."""

    schema_version: int
    request_id: str
    index_version: str
    cache_status: CacheStatus
    generated_at: str
    evidence: list[EvidenceItem]
    brief: str | None
    job_id: str | None
    diagnostics_available: bool
    truncated: bool
    next_cursor: str | None
    tick_snapshot: dict[str, Any] | None = None

    CONTRACT_NAME: ClassVar[str] = "query_response"

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> QueryResponse:
        if not isinstance(payload, Mapping):
            raise ContractValidationError("query response must be an object")
        fields = frozenset(
            {
                "schema_version",
                "request_id",
                "index_version",
                "cache_status",
                "generated_at",
                "evidence",
                "brief",
                "job_id",
                "diagnostics_available",
                "truncated",
                "next_cursor",
            }
        )
        _require_exact_fields(
            payload,
            required=fields,
            optional=frozenset({"tick_snapshot"}),
        )
        try:
            cache_status = CacheStatus(payload["cache_status"])
        except (TypeError, ValueError) as exc:
            raise ContractValidationError("invalid cache_status") from exc
        raw_evidence = payload["evidence"]
        if not isinstance(raw_evidence, list):
            raise ContractValidationError("evidence must be an array")
        evidence = [EvidenceItem.from_dict(item) for item in raw_evidence]
        if len(evidence) > 100:
            raise ContractValidationError("evidence cannot exceed 100 items")
        for field in ("diagnostics_available", "truncated"):
            if not isinstance(payload[field], bool):
                raise ContractValidationError(f"{field} must be a boolean")
        return cls(
            schema_version=_validate_schema_version(payload["schema_version"]),
            request_id=_require_bounded_string(
                payload["request_id"], "request_id", 128
            ),
            index_version=_require_non_empty_string(
                payload["index_version"], "index_version"
            ),
            cache_status=cache_status,
            generated_at=_require_non_empty_string(
                payload["generated_at"], "generated_at"
            ),
            evidence=evidence,
            brief=_require_optional_string(payload["brief"], "brief"),
            job_id=_require_optional_string(payload["job_id"], "job_id"),
            diagnostics_available=payload["diagnostics_available"],
            truncated=payload["truncated"],
            next_cursor=_require_optional_string(
                payload["next_cursor"], "next_cursor"
            ),
            tick_snapshot=(
                _validate_json_object(payload["tick_snapshot"], "tick_snapshot")
                if payload.get("tick_snapshot") is not None
                else None
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        payload = {
            "schema_version": self.schema_version,
            "request_id": self.request_id,
            "index_version": self.index_version,
            "cache_status": self.cache_status.value,
            "generated_at": self.generated_at,
            "evidence": [item.to_dict() for item in self.evidence],
            "brief": self.brief,
            "job_id": self.job_id,
            "diagnostics_available": self.diagnostics_available,
            "truncated": self.truncated,
            "next_cursor": self.next_cursor,
        }
        if self.tick_snapshot is not None:
            payload["tick_snapshot"] = dict(self.tick_snapshot)
        return payload


@dataclass(frozen=True)
class ServiceInfo:
    """Dynamic capability and readiness truth for clients."""

    schema_version: int
    product: str
    service_version: str
    service_api_version: int
    contract_schema_version: int
    contract_sha256: str
    database_schema_version: int
    runtime_manifest_sha256: str | None
    mcp_adapter_version: str | None
    mcp_supported_service_api_min: int | None
    mcp_supported_service_api_max: int | None
    mcp_supported_database_schema_min: int | None
    mcp_supported_database_schema_max: int | None
    compatibility_state: str
    status: ServiceStatus
    capabilities: list[str]
    sources: dict[str, Any]
    freshness_policies: list[str]
    response_modes: list[str]
    limits: dict[str, Any]
    index: dict[str, Any]
    transport: str

    CONTRACT_NAME: ClassVar[str] = "service_info"

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> ServiceInfo:
        if not isinstance(payload, Mapping):
            raise ContractValidationError("service info must be an object")
        fields = frozenset(
            {
                "schema_version",
                "product",
                "service_version",
                "service_api_version",
                "contract_schema_version",
                "contract_sha256",
                "database_schema_version",
                "runtime_manifest_sha256",
                "mcp_adapter_version",
                "mcp_supported_service_api_min",
                "mcp_supported_service_api_max",
                "mcp_supported_database_schema_min",
                "mcp_supported_database_schema_max",
                "compatibility_state",
                "status",
                "capabilities",
                "sources",
                "freshness_policies",
                "response_modes",
                "limits",
                "index",
                "transport",
            }
        )
        _require_exact_fields(payload, required=fields)
        try:
            status = ServiceStatus(payload["status"])
        except (TypeError, ValueError) as exc:
            raise ContractValidationError("invalid service status") from exc
        freshness_policies = _require_string_list(
            payload["freshness_policies"], "freshness_policies"
        )
        invalid_freshness = sorted(
            set(freshness_policies) - {item.value for item in FreshnessPolicy}
        )
        if invalid_freshness:
            raise ContractValidationError(
                f"invalid freshness policies: {', '.join(invalid_freshness)}"
            )
        response_modes = _require_string_list(
            payload["response_modes"], "response_modes"
        )
        invalid_modes = sorted(
            set(response_modes) - {item.value for item in ResponseMode}
        )
        if invalid_modes:
            raise ContractValidationError(
                f"invalid response modes: {', '.join(invalid_modes)}"
            )
        transport = _require_non_empty_string(payload["transport"], "transport")
        if transport != "unix":
            raise ContractValidationError("transport must be unix")
        product = _require_non_empty_string(payload["product"], "product")
        if product != "last30days":
            raise ContractValidationError("product must be last30days")
        contract_sha256 = _require_non_empty_string(
            payload["contract_sha256"], "contract_sha256"
        )
        if re.fullmatch(r"[0-9a-f]{64}", contract_sha256) is None:
            raise ContractValidationError("contract_sha256 is invalid")
        runtime_manifest_sha256 = payload["runtime_manifest_sha256"]
        if runtime_manifest_sha256 is not None and (
            not isinstance(runtime_manifest_sha256, str)
            or re.fullmatch(r"[0-9a-f]{64}", runtime_manifest_sha256) is None
        ):
            raise ContractValidationError("runtime_manifest_sha256 is invalid")
        mcp_adapter_version = payload["mcp_adapter_version"]
        if mcp_adapter_version is not None and (
            not isinstance(mcp_adapter_version, str)
            or not 0 < len(mcp_adapter_version) <= 64
        ):
            raise ContractValidationError("mcp_adapter_version is invalid")

        def optional_version(name: str) -> int | None:
            value = payload[name]
            if value is None:
                return None
            return _require_integer_between(value, name, 1, 2_147_483_647)

        compatibility_state = _require_non_empty_string(
            payload["compatibility_state"], "compatibility_state"
        )
        if compatibility_state not in {
            "compatible",
            "mcp_client_not_declared",
            "product_mismatch",
            "service_api_unsupported",
            "contract_schema_unsupported",
            "contract_digest_mismatch",
            "database_schema_unsupported",
            "runtime_manifest_invalid",
            "handshake_invalid",
        }:
            raise ContractValidationError("compatibility_state is invalid")
        return cls(
            schema_version=_validate_schema_version(payload["schema_version"]),
            product=product,
            service_version=_require_non_empty_string(
                payload["service_version"], "service_version"
            ),
            service_api_version=_require_integer_between(
                payload["service_api_version"],
                "service_api_version",
                1,
                2_147_483_647,
            ),
            contract_schema_version=_require_integer_between(
                payload["contract_schema_version"],
                "contract_schema_version",
                1,
                2_147_483_647,
            ),
            contract_sha256=contract_sha256,
            database_schema_version=_require_integer_between(
                payload["database_schema_version"],
                "database_schema_version",
                1,
                2_147_483_647,
            ),
            runtime_manifest_sha256=runtime_manifest_sha256,
            mcp_adapter_version=mcp_adapter_version,
            mcp_supported_service_api_min=optional_version(
                "mcp_supported_service_api_min"
            ),
            mcp_supported_service_api_max=optional_version(
                "mcp_supported_service_api_max"
            ),
            mcp_supported_database_schema_min=optional_version(
                "mcp_supported_database_schema_min"
            ),
            mcp_supported_database_schema_max=optional_version(
                "mcp_supported_database_schema_max"
            ),
            compatibility_state=compatibility_state,
            status=status,
            capabilities=_require_string_list(
                payload["capabilities"], "capabilities"
            ),
            sources=_validate_json_object(payload["sources"], "sources"),
            freshness_policies=freshness_policies,
            response_modes=response_modes,
            limits=_validate_json_object(payload["limits"], "limits"),
            index=_validate_json_object(payload["index"], "index"),
            transport=transport,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "product": self.product,
            "service_version": self.service_version,
            "service_api_version": self.service_api_version,
            "contract_schema_version": self.contract_schema_version,
            "contract_sha256": self.contract_sha256,
            "database_schema_version": self.database_schema_version,
            "runtime_manifest_sha256": self.runtime_manifest_sha256,
            "mcp_adapter_version": self.mcp_adapter_version,
            "mcp_supported_service_api_min": self.mcp_supported_service_api_min,
            "mcp_supported_service_api_max": self.mcp_supported_service_api_max,
            "mcp_supported_database_schema_min": (
                self.mcp_supported_database_schema_min
            ),
            "mcp_supported_database_schema_max": (
                self.mcp_supported_database_schema_max
            ),
            "compatibility_state": self.compatibility_state,
            "status": self.status.value,
            "capabilities": list(self.capabilities),
            "sources": dict(self.sources),
            "freshness_policies": list(self.freshness_policies),
            "response_modes": list(self.response_modes),
            "limits": dict(self.limits),
            "index": dict(self.index),
            "transport": self.transport,
        }


@dataclass(frozen=True)
class AcquisitionWorkRequest:
    """Bounded authority granted to one isolated source worker attempt."""

    schema_version: int
    work_id: str
    job_id: str
    lease_generation: int
    attempt: int
    profile_id: str
    source: str
    query: str
    from_date: str
    to_date: str
    depth: str
    adapter: str
    adapter_version: str
    wall_timeout_seconds: int
    item_limit: int
    network_request_limit: int
    cost_budget_cents: int

    CONTRACT_NAME: ClassVar[str] = "acquisition_work_request"

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> AcquisitionWorkRequest:
        if not isinstance(payload, Mapping):
            raise ContractValidationError("acquisition work request must be an object")
        fields = frozenset(
            {
                "schema_version",
                "work_id",
                "job_id",
                "lease_generation",
                "attempt",
                "profile_id",
                "source",
                "query",
                "from_date",
                "to_date",
                "depth",
                "adapter",
                "adapter_version",
                "wall_timeout_seconds",
                "item_limit",
                "network_request_limit",
                "cost_budget_cents",
            }
        )
        _require_exact_fields(payload, required=fields)
        depth = _require_non_empty_string(payload["depth"], "depth")
        if depth not in {"quick", "standard", "deep"}:
            raise ContractValidationError("depth must be quick, standard, or deep")
        return cls(
            schema_version=_validate_schema_version(payload["schema_version"]),
            work_id=_require_bounded_string(payload["work_id"], "work_id", 128),
            job_id=_require_bounded_string(payload["job_id"], "job_id", 128),
            lease_generation=_require_integer_between(
                payload["lease_generation"], "lease_generation", 1, 2_147_483_647
            ),
            attempt=_require_integer_between(payload["attempt"], "attempt", 1, 100),
            profile_id=_require_bounded_string(
                payload["profile_id"], "profile_id", 128
            ),
            source=_require_bounded_string(payload["source"], "source", 64),
            query=_require_bounded_string(payload["query"], "query", 8192),
            from_date=_require_bounded_string(
                payload["from_date"], "from_date", 64
            ),
            to_date=_require_bounded_string(payload["to_date"], "to_date", 64),
            depth=depth,
            adapter=_require_bounded_string(payload["adapter"], "adapter", 128),
            adapter_version=_require_bounded_string(
                payload["adapter_version"], "adapter_version", 64
            ),
            wall_timeout_seconds=_require_integer_between(
                payload["wall_timeout_seconds"],
                "wall_timeout_seconds",
                1,
                3600,
            ),
            item_limit=_require_integer_between(
                payload["item_limit"], "item_limit", 1, 10_000
            ),
            network_request_limit=_require_integer_between(
                payload["network_request_limit"],
                "network_request_limit",
                0,
                100_000,
            ),
            cost_budget_cents=_require_integer_between(
                payload["cost_budget_cents"],
                "cost_budget_cents",
                0,
                10_000_000,
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "work_id": self.work_id,
            "job_id": self.job_id,
            "lease_generation": self.lease_generation,
            "attempt": self.attempt,
            "profile_id": self.profile_id,
            "source": self.source,
            "query": self.query,
            "from_date": self.from_date,
            "to_date": self.to_date,
            "depth": self.depth,
            "adapter": self.adapter,
            "adapter_version": self.adapter_version,
            "wall_timeout_seconds": self.wall_timeout_seconds,
            "item_limit": self.item_limit,
            "network_request_limit": self.network_request_limit,
            "cost_budget_cents": self.cost_budget_cents,
        }


@dataclass(frozen=True)
class AcquiredMedia:
    """Bounded binary media carried across the isolated worker boundary."""

    source_url: str
    content_base64: str
    mime_type: str
    media_kind: str
    alt_text: str | None

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> AcquiredMedia:
        fields = frozenset(
            {"source_url", "content_base64", "mime_type", "media_kind", "alt_text"}
        )
        _require_exact_fields(payload, required=fields)
        encoded = _require_bounded_string(
            payload["content_base64"], "content_base64", 699_052
        )
        try:
            content = base64.b64decode(encoded, validate=True)
        except (binascii.Error, ValueError) as exc:
            raise ContractValidationError("content_base64 must be valid base64") from exc
        if not content or len(content) > 524_288:
            raise ContractValidationError(
                "decoded media content must contain between 1 and 524288 bytes"
            )
        media_kind = _require_bounded_string(
            payload["media_kind"], "media_kind", 64
        )
        if media_kind not in {"image", "video_thumbnail"}:
            raise ContractValidationError("media_kind is unsupported")
        return cls(
            source_url=_require_bounded_string(
                payload["source_url"], "source_url", 4096
            ),
            content_base64=encoded,
            mime_type=_require_bounded_string(payload["mime_type"], "mime_type", 256),
            media_kind=media_kind,
            alt_text=_require_optional_string(payload["alt_text"], "alt_text"),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_url": self.source_url,
            "content_base64": self.content_base64,
            "mime_type": self.mime_type,
            "media_kind": self.media_kind,
            "alt_text": self.alt_text,
        }


@dataclass(frozen=True)
class AcquiredItem:
    """One normalized, sanitized content item returned by a source worker."""

    source_native_id: str
    url: str
    title: str
    text: str
    author: str | None
    published_at: str | None
    metadata: dict[str, Any]
    media: list[AcquiredMedia]

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> AcquiredItem:
        fields = frozenset(
            {
                "source_native_id",
                "url",
                "title",
                "text",
                "author",
                "published_at",
                "metadata",
            }
        )
        _require_exact_fields(payload, required=fields, optional=frozenset({"media"}))
        raw_media = payload.get("media", [])
        if not isinstance(raw_media, list) or len(raw_media) > 16:
            raise ContractValidationError("media must be a bounded array")
        return cls(
            source_native_id=_require_bounded_string(
                payload["source_native_id"], "source_native_id", 512
            ),
            url=_require_bounded_string(payload["url"], "url", 4096),
            title=_require_bounded_string(payload["title"], "title", 2048),
            text=_require_bounded_string(payload["text"], "text", 65_536),
            author=_require_optional_string(payload["author"], "author"),
            published_at=_require_optional_string(
                payload["published_at"], "published_at"
            ),
            metadata=_validate_json_object(payload["metadata"], "metadata"),
            media=[AcquiredMedia.from_dict(value) for value in raw_media],
        )

    def to_dict(self) -> dict[str, Any]:
        payload = {
            "source_native_id": self.source_native_id,
            "url": self.url,
            "title": self.title,
            "text": self.text,
            "author": self.author,
            "published_at": self.published_at,
            "metadata": dict(self.metadata),
        }
        if self.media:
            payload["media"] = [value.to_dict() for value in self.media]
        return payload


@dataclass(frozen=True)
class AcquisitionWorkResult:
    """Schema-validated proposal from a worker; the host alone may publish it."""

    schema_version: int
    work_id: str
    job_id: str
    lease_generation: int
    source: str
    adapter: str
    adapter_version: str
    status: AcquisitionStatus
    safe_error_code: str | None
    retry_class: RetryClass
    retry_after_seconds: int | None
    observed_at: str
    fetched_at: str
    items: list[AcquiredItem]
    item_count: int
    cost_cents: int
    diagnostics: dict[str, Any]
    operator_url: str | None = None
    rendered_page: bytes | None = None
    rendered_page_mime_type: str | None = None
    network_request_count: int | None = None
    attempted_count: int | None = None
    observed_count: int | None = None
    accepted_count: int | None = None
    rejected_count: int | None = None

    CONTRACT_NAME: ClassVar[str] = "acquisition_work_result"

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> AcquisitionWorkResult:
        if not isinstance(payload, Mapping):
            raise ContractValidationError("acquisition work result must be an object")
        fields = frozenset(
            {
                "schema_version",
                "work_id",
                "job_id",
                "lease_generation",
                "source",
                "adapter",
                "adapter_version",
                "status",
                "safe_error_code",
                "retry_class",
                "retry_after_seconds",
                "observed_at",
                "fetched_at",
                "items",
                "item_count",
                "cost_cents",
                "diagnostics",
            }
        )
        evidence_fields = frozenset(
            {"operator_url", "rendered_page_base64", "rendered_page_mime_type"}
        )
        observability_fields = frozenset(
            {
                "network_request_count",
                "attempted_count",
                "observed_count",
                "accepted_count",
                "rejected_count",
            }
        )
        _require_exact_fields(
            payload,
            required=fields,
            optional=observability_fields | evidence_fields,
        )
        try:
            status = AcquisitionStatus(payload["status"])
            retry_class = RetryClass(payload["retry_class"])
        except (TypeError, ValueError) as exc:
            raise ContractValidationError(
                "invalid acquisition status or retry class"
            ) from exc
        raw_items = payload["items"]
        if not isinstance(raw_items, list) or len(raw_items) > 10_000:
            raise ContractValidationError("items must be a bounded array")
        items = [AcquiredItem.from_dict(item) for item in raw_items]
        binary_evidence_bytes = sum(
            len(base64.b64decode(media.content_base64, validate=True))
            for item in items
            for media in item.media
        )
        if binary_evidence_bytes > MAX_ACQUISITION_BINARY_EVIDENCE_BYTES:
            raise ContractValidationError(
                "aggregate binary evidence exceeds the 524288-byte limit"
            )
        item_count = _require_integer_between(
            payload["item_count"], "item_count", 0, 10_000
        )
        if item_count != len(items):
            raise ContractValidationError("item_count must equal the items length")
        present_observability = observability_fields.intersection(payload)
        if present_observability and present_observability != observability_fields:
            raise ContractValidationError(
                "observability counts must be supplied together"
            )
        network_request_count: int | None = None
        attempted_count: int | None = None
        observed_count: int | None = None
        accepted_count: int | None = None
        rejected_count: int | None = None
        if present_observability:
            network_request_count = _require_integer_between(
                payload["network_request_count"],
                "network_request_count",
                0,
                1_000_000,
            )
            attempted_count = _require_integer_between(
                payload["attempted_count"], "attempted_count", 0, 10_000
            )
            observed_count = _require_integer_between(
                payload["observed_count"], "observed_count", 0, 10_000
            )
            accepted_count = _require_integer_between(
                payload["accepted_count"], "accepted_count", 0, 10_000
            )
            rejected_count = _require_integer_between(
                payload["rejected_count"], "rejected_count", 0, 10_000
            )
            if (
                accepted_count != item_count
                or attempted_count < observed_count
                or observed_count != accepted_count + rejected_count
            ):
                raise ContractValidationError("inconsistent outcome counts")
        retry_after = payload["retry_after_seconds"]
        if retry_after is not None:
            retry_after = _require_integer_between(
                retry_after, "retry_after_seconds", 0, 86_400
            )
        if status is AcquisitionStatus.AWAITING_OPERATOR and (
            retry_class is not RetryClass.OPERATOR
        ):
            raise ContractValidationError(
                "awaiting_operator results require the operator retry class"
            )
        if status is AcquisitionStatus.SUCCEEDED and (
            retry_class is not RetryClass.NONE
        ):
            raise ContractValidationError(
                "succeeded results require the none retry class"
            )
        safe_error_code = _require_optional_string(
            payload["safe_error_code"], "safe_error_code"
        )
        if safe_error_code is not None and not SAFE_ERROR_CODE.fullmatch(
            safe_error_code
        ):
            raise ContractValidationError("safe_error_code is not a safe code")
        if status is AcquisitionStatus.SUCCEEDED:
            if safe_error_code is not None or retry_after is not None:
                raise ContractValidationError(
                    "succeeded results cannot carry failure metadata"
                )
        elif safe_error_code is None:
            raise ContractValidationError(
                "non-success results require a safe_error_code"
            )
        if status is not AcquisitionStatus.SUCCEEDED and (
            retry_class is RetryClass.NONE
        ):
            raise ContractValidationError(
                "non-success results require a retry classification"
            )
        operator_url = payload.get("operator_url")
        if operator_url is not None:
            operator_url = _require_bounded_string(operator_url, "operator_url", 4096)
            parsed = urlparse(operator_url)
            if (
                parsed.scheme != "https"
                or not parsed.hostname
                or parsed.hostname.casefold() in {"localhost", "127.0.0.1", "::1"}
            ):
                raise ContractValidationError(
                    "operator_url must be an external HTTPS URL"
                )
            if status is AcquisitionStatus.SUCCEEDED:
                raise ContractValidationError(
                    "succeeded results cannot carry an operator URL"
                )
        encoded_page = payload.get("rendered_page_base64")
        page_mime = payload.get("rendered_page_mime_type")
        if (encoded_page is None) != (page_mime is None):
            raise ContractValidationError(
                "rendered page bytes and MIME type must be supplied together"
            )
        rendered_page = None
        if encoded_page is not None:
            encoded_page = _require_bounded_string(
                encoded_page, "rendered_page_base64", 699_052
            )
            try:
                rendered_page = base64.b64decode(encoded_page, validate=True)
            except (binascii.Error, ValueError) as exc:
                raise ContractValidationError(
                    "rendered_page_base64 must be valid base64"
                ) from exc
            if not rendered_page or len(rendered_page) > 524_288:
                raise ContractValidationError(
                    "rendered page must contain between 1 and 524288 bytes"
                )
            binary_evidence_bytes += len(rendered_page)
            if binary_evidence_bytes > MAX_ACQUISITION_BINARY_EVIDENCE_BYTES:
                raise ContractValidationError(
                    "aggregate binary evidence exceeds the 524288-byte limit"
                )
            page_mime = _require_bounded_string(
                page_mime, "rendered_page_mime_type", 256
            )
        if retry_after is not None and retry_class not in {
            RetryClass.RATE_LIMIT,
            RetryClass.TRANSIENT,
            RetryClass.CONTENT,
        }:
            raise ContractValidationError(
                "retry_after_seconds requires a retryable classification"
            )
        observed_at = _validate_timestamp(payload["observed_at"], "observed_at")
        fetched_at = _validate_timestamp(payload["fetched_at"], "fetched_at")
        if fetched_at < observed_at:
            raise ContractValidationError(
                "fetched_at cannot precede observed_at"
            )
        return cls(
            schema_version=_validate_schema_version(payload["schema_version"]),
            work_id=_require_bounded_string(payload["work_id"], "work_id", 128),
            job_id=_require_bounded_string(payload["job_id"], "job_id", 128),
            lease_generation=_require_integer_between(
                payload["lease_generation"], "lease_generation", 1, 2_147_483_647
            ),
            source=_require_bounded_string(payload["source"], "source", 64),
            adapter=_require_bounded_string(payload["adapter"], "adapter", 128),
            adapter_version=_require_bounded_string(
                payload["adapter_version"], "adapter_version", 64
            ),
            status=status,
            safe_error_code=safe_error_code,
            retry_class=retry_class,
            retry_after_seconds=retry_after,
            observed_at=payload["observed_at"],
            fetched_at=payload["fetched_at"],
            items=items,
            item_count=item_count,
            cost_cents=_require_integer_between(
                payload["cost_cents"], "cost_cents", 0, 10_000_000
            ),
            diagnostics=_validate_json_object(
                payload["diagnostics"], "diagnostics"
            ),
            operator_url=operator_url,
            rendered_page=rendered_page,
            rendered_page_mime_type=page_mime,
            network_request_count=network_request_count,
            attempted_count=attempted_count,
            observed_count=observed_count,
            accepted_count=accepted_count,
            rejected_count=rejected_count,
        )

    def to_dict(self) -> dict[str, Any]:
        payload = {
            "schema_version": self.schema_version,
            "work_id": self.work_id,
            "job_id": self.job_id,
            "lease_generation": self.lease_generation,
            "source": self.source,
            "adapter": self.adapter,
            "adapter_version": self.adapter_version,
            "status": self.status.value,
            "safe_error_code": self.safe_error_code,
            "retry_class": self.retry_class.value,
            "retry_after_seconds": self.retry_after_seconds,
            "observed_at": self.observed_at,
            "fetched_at": self.fetched_at,
            "items": [item.to_dict() for item in self.items],
            "item_count": self.item_count,
            "cost_cents": self.cost_cents,
            "diagnostics": dict(self.diagnostics),
        }
        if self.network_request_count is not None:
            payload.update(
                {
                    "network_request_count": self.network_request_count,
                    "attempted_count": self.attempted_count,
                    "observed_count": self.observed_count,
                    "accepted_count": self.accepted_count,
                    "rejected_count": self.rejected_count,
                }
            )
        if self.operator_url is not None:
            payload["operator_url"] = self.operator_url
        if self.rendered_page is not None:
            payload["rendered_page_base64"] = base64.b64encode(
                self.rendered_page
            ).decode("ascii")
            payload["rendered_page_mime_type"] = self.rendered_page_mime_type
        return payload


@dataclass(frozen=True)
class EntityProposal:
    """Evidence-bounded entity mention proposed for deterministic promotion."""

    schema_version: int
    proposal_id: str
    document_id: str
    evidence_chunk_id: str
    canonical_name: str
    entity_type: str
    evidence_start: int
    evidence_end: int
    extractor_version: str
    confidence: float

    CONTRACT_NAME: ClassVar[str] = "entity_proposal"
    ENTITY_TYPES: ClassVar[frozenset[str]] = frozenset(
        {"organization", "person", "product", "project", "location", "topic"}
    )

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> EntityProposal:
        if not isinstance(payload, Mapping):
            raise ContractValidationError("entity proposal must be an object")
        fields = frozenset(
            {
                "schema_version",
                "proposal_id",
                "document_id",
                "evidence_chunk_id",
                "canonical_name",
                "entity_type",
                "evidence_start",
                "evidence_end",
                "extractor_version",
                "confidence",
            }
        )
        _require_exact_fields(payload, required=fields)
        entity_type = _require_bounded_string(
            payload["entity_type"], "entity_type", 64
        )
        if entity_type not in cls.ENTITY_TYPES:
            raise ContractValidationError("entity_type is not supported")
        start = _require_integer_between(
            payload["evidence_start"], "evidence_start", 0, 10_000_000
        )
        end = _require_integer_between(
            payload["evidence_end"], "evidence_end", 1, 10_000_000
        )
        if end <= start:
            raise ContractValidationError("entity evidence range must be non-empty")
        return cls(
            schema_version=_validate_schema_version(payload["schema_version"]),
            proposal_id=_require_bounded_string(
                payload["proposal_id"], "proposal_id", 128
            ),
            document_id=_require_bounded_string(
                payload["document_id"], "document_id", 128
            ),
            evidence_chunk_id=_require_bounded_string(
                payload["evidence_chunk_id"], "evidence_chunk_id", 128
            ),
            canonical_name=_require_bounded_string(
                payload["canonical_name"], "canonical_name", 256
            ),
            entity_type=entity_type,
            evidence_start=start,
            evidence_end=end,
            extractor_version=_require_bounded_string(
                payload["extractor_version"], "extractor_version", 128
            ),
            confidence=_require_confidence(payload["confidence"]),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "proposal_id": self.proposal_id,
            "document_id": self.document_id,
            "evidence_chunk_id": self.evidence_chunk_id,
            "canonical_name": self.canonical_name,
            "entity_type": self.entity_type,
            "evidence_start": self.evidence_start,
            "evidence_end": self.evidence_end,
            "extractor_version": self.extractor_version,
            "confidence": self.confidence,
        }


@dataclass(frozen=True)
class RelationshipProposal:
    """Resolved edge proposal that must retain an existing evidence chunk."""

    schema_version: int
    proposal_id: str
    document_id: str
    evidence_chunk_id: str
    evidence_start: int
    evidence_end: int
    subject_entity_id: str
    predicate: str
    object_entity_id: str
    extractor_version: str
    confidence: float

    CONTRACT_NAME: ClassVar[str] = "relationship_proposal"

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> RelationshipProposal:
        if not isinstance(payload, Mapping):
            raise ContractValidationError(
                "relationship proposal must be an object"
            )
        fields = frozenset(
            {
                "schema_version",
                "proposal_id",
                "document_id",
                "evidence_chunk_id",
                "evidence_start",
                "evidence_end",
                "subject_entity_id",
                "predicate",
                "object_entity_id",
                "extractor_version",
                "confidence",
            }
        )
        _require_exact_fields(payload, required=fields)
        subject = _require_bounded_string(
            payload["subject_entity_id"], "subject_entity_id", 128
        )
        object_id = _require_bounded_string(
            payload["object_entity_id"], "object_entity_id", 128
        )
        if subject == object_id:
            raise ContractValidationError(
                "relationship proposal cannot be a self-edge"
            )
        predicate = _require_bounded_string(
            payload["predicate"], "predicate", 64
        )
        if not SAFE_ERROR_CODE.fullmatch(predicate):
            raise ContractValidationError("predicate must be a safe code")
        start = _require_integer_between(
            payload["evidence_start"], "evidence_start", 0, 2_147_483_647
        )
        end = _require_integer_between(
            payload["evidence_end"], "evidence_end", 1, 2_147_483_647
        )
        if end <= start:
            raise ContractValidationError("evidence_end must exceed evidence_start")
        return cls(
            schema_version=_validate_schema_version(payload["schema_version"]),
            proposal_id=_require_bounded_string(
                payload["proposal_id"], "proposal_id", 128
            ),
            document_id=_require_bounded_string(
                payload["document_id"], "document_id", 128
            ),
            evidence_chunk_id=_require_bounded_string(
                payload["evidence_chunk_id"], "evidence_chunk_id", 128
            ),
            evidence_start=start,
            evidence_end=end,
            subject_entity_id=subject,
            predicate=predicate,
            object_entity_id=object_id,
            extractor_version=_require_bounded_string(
                payload["extractor_version"], "extractor_version", 128
            ),
            confidence=_require_confidence(payload["confidence"]),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "proposal_id": self.proposal_id,
            "document_id": self.document_id,
            "evidence_chunk_id": self.evidence_chunk_id,
            "evidence_start": self.evidence_start,
            "evidence_end": self.evidence_end,
            "subject_entity_id": self.subject_entity_id,
            "predicate": self.predicate,
            "object_entity_id": self.object_entity_id,
            "extractor_version": self.extractor_version,
            "confidence": self.confidence,
        }


@dataclass(frozen=True)
class AcquisitionEnvelope:
    """Redacted record of one bounded source acquisition attempt."""

    schema_version: int
    acquisition_id: str
    job_id: str
    profile_id: str
    source: str
    adapter: str
    adapter_version: str
    query: str
    status: AcquisitionStatus
    observed_at: str
    fetched_at: str
    artifact_ref: str | None
    content_hash: str | None
    retention_class: RetentionClass
    redaction_class: RedactionClass
    item_count: int
    diagnostics_ref: str | None

    CONTRACT_NAME: ClassVar[str] = "acquisition_envelope"

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> AcquisitionEnvelope:
        if not isinstance(payload, Mapping):
            raise ContractValidationError("acquisition envelope must be an object")
        fields = frozenset(
            {
                "schema_version",
                "acquisition_id",
                "job_id",
                "profile_id",
                "source",
                "adapter",
                "adapter_version",
                "query",
                "status",
                "observed_at",
                "fetched_at",
                "artifact_ref",
                "content_hash",
                "retention_class",
                "redaction_class",
                "item_count",
                "diagnostics_ref",
            }
        )
        _require_exact_fields(payload, required=fields)
        try:
            status = AcquisitionStatus(payload["status"])
            retention_class = RetentionClass(payload["retention_class"])
            redaction_class = RedactionClass(payload["redaction_class"])
        except (TypeError, ValueError) as exc:
            raise ContractValidationError(
                "invalid acquisition status or data classification"
            ) from exc
        return cls(
            schema_version=_validate_schema_version(payload["schema_version"]),
            acquisition_id=_require_non_empty_string(
                payload["acquisition_id"], "acquisition_id"
            ),
            job_id=_require_non_empty_string(payload["job_id"], "job_id"),
            profile_id=_require_non_empty_string(
                payload["profile_id"], "profile_id"
            ),
            source=_require_non_empty_string(payload["source"], "source"),
            adapter=_require_non_empty_string(payload["adapter"], "adapter"),
            adapter_version=_require_non_empty_string(
                payload["adapter_version"], "adapter_version"
            ),
            query=_require_non_empty_string(payload["query"], "query"),
            status=status,
            observed_at=_require_non_empty_string(
                payload["observed_at"], "observed_at"
            ),
            fetched_at=_require_non_empty_string(
                payload["fetched_at"], "fetched_at"
            ),
            artifact_ref=_require_optional_string(
                payload["artifact_ref"], "artifact_ref"
            ),
            content_hash=_require_optional_string(
                payload["content_hash"], "content_hash"
            ),
            retention_class=retention_class,
            redaction_class=redaction_class,
            item_count=_require_integer_between(
                payload["item_count"], "item_count", 0, 1_000_000
            ),
            diagnostics_ref=_require_optional_string(
                payload["diagnostics_ref"], "diagnostics_ref"
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "acquisition_id": self.acquisition_id,
            "job_id": self.job_id,
            "profile_id": self.profile_id,
            "source": self.source,
            "adapter": self.adapter,
            "adapter_version": self.adapter_version,
            "query": self.query,
            "status": self.status.value,
            "observed_at": self.observed_at,
            "fetched_at": self.fetched_at,
            "artifact_ref": self.artifact_ref,
            "content_hash": self.content_hash,
            "retention_class": self.retention_class.value,
            "redaction_class": self.redaction_class.value,
            "item_count": self.item_count,
            "diagnostics_ref": self.diagnostics_ref,
        }


@dataclass(frozen=True)
class JobRecord:
    """Replayable deterministic-supervisor state for one bounded job."""

    schema_version: int
    job_id: str
    job_type: JobType
    dedupe_key: str
    state: JobState
    query_request_id: str
    attempts: int
    max_attempts: int
    budget_cents: int
    spent_cents: int
    lease_generation: int
    lease_owner: str | None
    lease_expires_at: str | None
    not_before_at: str | None
    created_at: str
    updated_at: str
    published_index_version: str | None
    error_code: str | None

    CONTRACT_NAME: ClassVar[str] = "job_record"

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> JobRecord:
        if not isinstance(payload, Mapping):
            raise ContractValidationError("job record must be an object")
        fields = frozenset(
            {
                "schema_version",
                "job_id",
                "job_type",
                "dedupe_key",
                "state",
                "query_request_id",
                "attempts",
                "max_attempts",
                "budget_cents",
                "spent_cents",
                "lease_generation",
                "lease_owner",
                "lease_expires_at",
                "not_before_at",
                "created_at",
                "updated_at",
                "published_index_version",
                "error_code",
            }
        )
        _require_exact_fields(payload, required=fields)
        try:
            job_type = JobType(payload["job_type"])
            state = JobState(payload["state"])
        except (TypeError, ValueError) as exc:
            raise ContractValidationError("invalid job_type or state") from exc
        attempts = _require_integer_between(
            payload["attempts"], "attempts", 0, 100
        )
        max_attempts = _require_integer_between(
            payload["max_attempts"], "max_attempts", 1, 100
        )
        if attempts > max_attempts:
            raise ContractValidationError("attempts cannot exceed max_attempts")
        budget_cents = _require_integer_between(
            payload["budget_cents"], "budget_cents", 0, 10_000_000
        )
        spent_cents = _require_integer_between(
            payload["spent_cents"], "spent_cents", 0, 10_000_000
        )
        if spent_cents > budget_cents:
            raise ContractValidationError("spent_cents cannot exceed budget_cents")
        return cls(
            schema_version=_validate_schema_version(payload["schema_version"]),
            job_id=_require_non_empty_string(payload["job_id"], "job_id"),
            job_type=job_type,
            dedupe_key=_require_non_empty_string(
                payload["dedupe_key"], "dedupe_key"
            ),
            state=state,
            query_request_id=_require_non_empty_string(
                payload["query_request_id"], "query_request_id"
            ),
            attempts=attempts,
            max_attempts=max_attempts,
            budget_cents=budget_cents,
            spent_cents=spent_cents,
            lease_generation=_require_integer_between(
                payload["lease_generation"], "lease_generation", 0, 2_147_483_647
            ),
            lease_owner=_require_optional_string(
                payload["lease_owner"], "lease_owner"
            ),
            lease_expires_at=_require_optional_string(
                payload["lease_expires_at"], "lease_expires_at"
            ),
            not_before_at=_require_optional_string(
                payload["not_before_at"], "not_before_at"
            ),
            created_at=_require_non_empty_string(
                payload["created_at"], "created_at"
            ),
            updated_at=_require_non_empty_string(
                payload["updated_at"], "updated_at"
            ),
            published_index_version=_require_optional_string(
                payload["published_index_version"], "published_index_version"
            ),
            error_code=_require_optional_string(
                payload["error_code"], "error_code"
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "job_id": self.job_id,
            "job_type": self.job_type.value,
            "dedupe_key": self.dedupe_key,
            "state": self.state.value,
            "query_request_id": self.query_request_id,
            "attempts": self.attempts,
            "max_attempts": self.max_attempts,
            "budget_cents": self.budget_cents,
            "spent_cents": self.spent_cents,
            "lease_generation": self.lease_generation,
            "lease_owner": self.lease_owner,
            "lease_expires_at": self.lease_expires_at,
            "not_before_at": self.not_before_at,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "published_index_version": self.published_index_version,
            "error_code": self.error_code,
        }


@dataclass(frozen=True)
class JobEvent:
    """One append-only event in the deterministic supervisor replay log."""

    schema_version: int
    event_id: str
    job_id: str
    sequence: int
    event_type: str
    phase: JobState
    occurred_at: str
    payload: dict[str, Any]
    redaction_class: RedactionClass

    CONTRACT_NAME: ClassVar[str] = "job_event"

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> JobEvent:
        if not isinstance(payload, Mapping):
            raise ContractValidationError("job event must be an object")
        fields = frozenset(
            {
                "schema_version",
                "event_id",
                "job_id",
                "sequence",
                "event_type",
                "phase",
                "occurred_at",
                "payload",
                "redaction_class",
            }
        )
        _require_exact_fields(payload, required=fields)
        try:
            phase = JobState(payload["phase"])
            redaction_class = RedactionClass(payload["redaction_class"])
        except (TypeError, ValueError) as exc:
            raise ContractValidationError(
                "invalid event phase or redaction_class"
            ) from exc
        return cls(
            schema_version=_validate_schema_version(payload["schema_version"]),
            event_id=_require_non_empty_string(payload["event_id"], "event_id"),
            job_id=_require_non_empty_string(payload["job_id"], "job_id"),
            sequence=_require_integer_between(
                payload["sequence"], "sequence", 1, 2_147_483_647
            ),
            event_type=_require_non_empty_string(
                payload["event_type"], "event_type"
            ),
            phase=phase,
            occurred_at=_require_non_empty_string(
                payload["occurred_at"], "occurred_at"
            ),
            payload=_validate_json_object(payload["payload"], "payload"),
            redaction_class=redaction_class,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "event_id": self.event_id,
            "job_id": self.job_id,
            "sequence": self.sequence,
            "event_type": self.event_type,
            "phase": self.phase.value,
            "occurred_at": self.occurred_at,
            "payload": dict(self.payload),
            "redaction_class": self.redaction_class.value,
        }


def _require_string_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list) or not all(
        isinstance(item, str) and item.strip() for item in value
    ):
        raise ContractValidationError(
            f"{field} must be a list of non-empty strings"
        )
    return list(value)


@dataclass(frozen=True)
class DecisionRecord:
    """Model proposal plus the deterministic host's validation outcome."""

    schema_version: int
    decision_id: str
    job_id: str
    loop_name: str
    action: str
    confidence: float
    evidence_ids: list[str]
    rationale: str
    model_ref: str
    input_ref: str
    output_ref: str
    accepted: bool
    validator_errors: list[str]
    created_at: str

    CONTRACT_NAME: ClassVar[str] = "decision_record"

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> DecisionRecord:
        if not isinstance(payload, Mapping):
            raise ContractValidationError("decision record must be an object")
        fields = frozenset(
            {
                "schema_version",
                "decision_id",
                "job_id",
                "loop_name",
                "action",
                "confidence",
                "evidence_ids",
                "rationale",
                "model_ref",
                "input_ref",
                "output_ref",
                "accepted",
                "validator_errors",
                "created_at",
            }
        )
        _require_exact_fields(payload, required=fields)
        confidence = payload["confidence"]
        if isinstance(confidence, bool) or not isinstance(
            confidence, (int, float)
        ):
            raise ContractValidationError("confidence must be numeric")
        confidence = float(confidence)
        if not 0 <= confidence <= 1:
            raise ContractValidationError("confidence must be between 0 and 1")
        if not isinstance(payload["accepted"], bool):
            raise ContractValidationError("accepted must be a boolean")
        return cls(
            schema_version=_validate_schema_version(payload["schema_version"]),
            decision_id=_require_non_empty_string(
                payload["decision_id"], "decision_id"
            ),
            job_id=_require_non_empty_string(payload["job_id"], "job_id"),
            loop_name=_require_non_empty_string(
                payload["loop_name"], "loop_name"
            ),
            action=_require_non_empty_string(payload["action"], "action"),
            confidence=confidence,
            evidence_ids=_require_string_list(
                payload["evidence_ids"], "evidence_ids"
            ),
            rationale=_require_non_empty_string(
                payload["rationale"], "rationale"
            ),
            model_ref=_require_non_empty_string(
                payload["model_ref"], "model_ref"
            ),
            input_ref=_require_non_empty_string(
                payload["input_ref"], "input_ref"
            ),
            output_ref=_require_non_empty_string(
                payload["output_ref"], "output_ref"
            ),
            accepted=payload["accepted"],
            validator_errors=_require_string_list(
                payload["validator_errors"], "validator_errors"
            ),
            created_at=_require_non_empty_string(
                payload["created_at"], "created_at"
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "decision_id": self.decision_id,
            "job_id": self.job_id,
            "loop_name": self.loop_name,
            "action": self.action,
            "confidence": self.confidence,
            "evidence_ids": list(self.evidence_ids),
            "rationale": self.rationale,
            "model_ref": self.model_ref,
            "input_ref": self.input_ref,
            "output_ref": self.output_ref,
            "accepted": self.accepted,
            "validator_errors": list(self.validator_errors),
            "created_at": self.created_at,
        }


ContractEnvelope = (
    QueryRequest
    | QueryResponse
    | ServiceInfo
    | EvidenceItem
    | TemporalEvidenceRef
    | AcquisitionWorkRequest
    | AcquisitionWorkResult
    | EntityProposal
    | RelationshipProposal
    | AcquisitionEnvelope
    | JobRecord
    | JobEvent
    | DecisionRecord
    | TickRequest
    | TickLaneReceipt
    | TickReceipt
)

_CONTRACT_TYPES = {
    QueryRequest.CONTRACT_NAME: QueryRequest,
    QueryResponse.CONTRACT_NAME: QueryResponse,
    ServiceInfo.CONTRACT_NAME: ServiceInfo,
    EvidenceItem.CONTRACT_NAME: EvidenceItem,
    TemporalEvidenceRef.CONTRACT_NAME: TemporalEvidenceRef,
    AcquisitionWorkRequest.CONTRACT_NAME: AcquisitionWorkRequest,
    AcquisitionWorkResult.CONTRACT_NAME: AcquisitionWorkResult,
    EntityProposal.CONTRACT_NAME: EntityProposal,
    RelationshipProposal.CONTRACT_NAME: RelationshipProposal,
    AcquisitionEnvelope.CONTRACT_NAME: AcquisitionEnvelope,
    JobRecord.CONTRACT_NAME: JobRecord,
    JobEvent.CONTRACT_NAME: JobEvent,
    DecisionRecord.CONTRACT_NAME: DecisionRecord,
    TickRequest.CONTRACT_NAME: TickRequest,
    TickLaneReceipt.CONTRACT_NAME: TickLaneReceipt,
    TickReceipt.CONTRACT_NAME: TickReceipt,
}


def parse_envelope(
    contract_name: str, payload: Mapping[str, Any]
) -> Any:
    """Validate one external envelope through the named public contract."""
    contract_type = _CONTRACT_TYPES.get(contract_name)
    if contract_type is None and contract_name == "collection_spec":
        from .service_collection import CollectionSpec

        contract_type = CollectionSpec
    if contract_type is None and contract_name in {
        "intelligence_evidence_ref",
        "intelligence_task_request",
        "intelligence_task_result",
        "validation_receipt",
        "promotion_receipt",
        "replay_receipt",
    }:
        from .service_intelligence_contracts import (
            IntelligenceEvidenceRef,
            IntelligenceTaskRequest,
            IntelligenceTaskResult,
            PromotionReceipt,
            ReplayReceipt,
            ValidationReceiptEnvelope,
        )

        contract_type = {
            "intelligence_evidence_ref": IntelligenceEvidenceRef,
            "intelligence_task_request": IntelligenceTaskRequest,
            "intelligence_task_result": IntelligenceTaskResult,
            "validation_receipt": ValidationReceiptEnvelope,
            "promotion_receipt": PromotionReceipt,
            "replay_receipt": ReplayReceipt,
        }[contract_name]
    if contract_type is None:
        raise ContractValidationError(f"unknown contract: {contract_name}")
    try:
        return contract_type.from_dict(payload)
    except ContractValidationError:
        raise
    except (TypeError, ValueError) as exc:
        raise ContractValidationError(str(exc)) from exc
