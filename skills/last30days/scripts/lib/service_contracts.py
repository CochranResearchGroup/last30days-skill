"""Versioned public contracts for the last30days intelligence service.

The service, CLI, and MCP adapters exchange these envelopes.  Validation lives
at this seam so callers do not need to understand storage or acquisition
implementation details.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any, ClassVar, Mapping


SCHEMA_VERSION = 1
SCHEMA_CATALOG_PATH = (
    Path(__file__).resolve().parents[2]
    / "schemas"
    / f"service-contracts-v{SCHEMA_VERSION}.json"
)
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


class AcquisitionStatus(StrEnum):
    SUCCEEDED = "succeeded"
    PARTIAL = "partial"
    FAILED = "failed"
    AWAITING_OPERATOR = "awaiting_operator"


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
            request_id=_require_non_empty_string(
                payload["request_id"], "request_id"
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

    CONTRACT_NAME: ClassVar[str] = "evidence_item"

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> EvidenceItem:
        if not isinstance(payload, Mapping):
            raise ContractValidationError("evidence item must be an object")
        fields = frozenset(
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
        _require_exact_fields(payload, required=fields)
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
        )

    def to_dict(self) -> dict[str, Any]:
        return {
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
    lease_owner: str | None
    lease_expires_at: str | None
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
                "lease_owner",
                "lease_expires_at",
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
            budget_cents=_require_integer_between(
                payload["budget_cents"], "budget_cents", 0, 10_000_000
            ),
            lease_owner=_require_optional_string(
                payload["lease_owner"], "lease_owner"
            ),
            lease_expires_at=_require_optional_string(
                payload["lease_expires_at"], "lease_expires_at"
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
            "lease_owner": self.lease_owner,
            "lease_expires_at": self.lease_expires_at,
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
    | EvidenceItem
    | AcquisitionEnvelope
    | JobRecord
    | JobEvent
    | DecisionRecord
)

_CONTRACT_TYPES = {
    QueryRequest.CONTRACT_NAME: QueryRequest,
    EvidenceItem.CONTRACT_NAME: EvidenceItem,
    AcquisitionEnvelope.CONTRACT_NAME: AcquisitionEnvelope,
    JobRecord.CONTRACT_NAME: JobRecord,
    JobEvent.CONTRACT_NAME: JobEvent,
    DecisionRecord.CONTRACT_NAME: DecisionRecord,
}


def parse_envelope(
    contract_name: str, payload: Mapping[str, Any]
) -> ContractEnvelope:
    """Validate one external envelope through the named public contract."""
    contract_type = _CONTRACT_TYPES.get(contract_name)
    if contract_type is None:
        raise ContractValidationError(f"unknown contract: {contract_name}")
    return contract_type.from_dict(payload)
