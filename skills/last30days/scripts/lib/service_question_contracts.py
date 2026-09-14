"""Strict provider-free contracts for evidence-grounded question tasks."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping

from .service_contracts import ContractValidationError, PostSearchRequest


QUESTION_SCHEMA_VERSION = 1
_PROFILE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_SAFE_CODE = re.compile(r"^[a-z][a-z0-9_]{0,63}$")


class QuestionContractError(ValueError):
    """Raised when a question workflow value violates its strict contract."""


def canonical_json(value: object) -> str:
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def digest(value: object) -> str:
    return "sha256:" + hashlib.sha256(canonical_json(value).encode()).hexdigest()


def stable_id(prefix: str, value: object) -> str:
    return f"{prefix}-{digest(value).removeprefix('sha256:')[:32]}"


def _serialized_size_with_counter(
    payload: Mapping[str, Any], counter_field: str
) -> int:
    measured = 2
    while True:
        updated = len(canonical_json({**payload, counter_field: measured}).encode())
        if updated == measured:
            return updated
        measured = updated


def _exact(payload: Mapping[str, Any], fields: frozenset[str], name: str) -> None:
    actual = set(payload)
    if actual != fields:
        unknown = sorted(actual - fields)
        missing = sorted(fields - actual)
        if unknown:
            raise QuestionContractError(f"{name} has unknown fields: {unknown}")
        raise QuestionContractError(f"{name} is missing fields: {missing}")


def _text(value: Any, name: str, maximum: int) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > maximum:
        raise QuestionContractError(
            f"{name} must be a non-empty string of at most {maximum} characters"
        )
    return value


def _integer(value: Any, name: str, minimum: int, maximum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise QuestionContractError(f"{name} must be an integer")
    if not minimum <= value <= maximum:
        raise QuestionContractError(
            f"{name} must be between {minimum} and {maximum}"
        )
    return value


def _timestamp(value: Any, name: str, *, optional: bool = True) -> str | None:
    if value is None and optional:
        return None
    text = _text(value, name, 64)
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as exc:
        raise QuestionContractError(f"{name} must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise QuestionContractError(f"{name} must include a timezone")
    return parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _string_list(
    value: Any,
    name: str,
    *,
    maximum: int,
    item_maximum: int = 256,
) -> tuple[str, ...]:
    if not isinstance(value, list) or len(value) > maximum:
        raise QuestionContractError(f"{name} must be a list of at most {maximum}")
    items = tuple(_text(item, f"{name} item", item_maximum) for item in value)
    if len(set(items)) != len(items):
        raise QuestionContractError(f"{name} must not contain duplicates")
    return items


@dataclass(frozen=True)
class QuestionLimitsV1:
    evidence_limit: int
    max_evidence_bytes: int
    max_answer_characters: int
    max_statements: int
    wait_ms: int
    max_evidence_age_seconds: int | None
    max_attempts: int

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> QuestionLimitsV1:
        if not isinstance(payload, Mapping):
            raise QuestionContractError("limits must be an object")
        _exact(
            payload,
            frozenset(
                {
                    "evidence_limit",
                    "max_evidence_bytes",
                    "max_answer_characters",
                    "max_statements",
                    "wait_ms",
                    "max_evidence_age_seconds",
                    "max_attempts",
                }
            ),
            "limits",
        )
        age = payload["max_evidence_age_seconds"]
        if age is not None:
            age = _integer(age, "max_evidence_age_seconds", 1, 31_536_000)
        return cls(
            evidence_limit=_integer(payload["evidence_limit"], "evidence_limit", 1, 50),
            max_evidence_bytes=_integer(
                payload["max_evidence_bytes"], "max_evidence_bytes", 1024, 1_048_576
            ),
            max_answer_characters=_integer(
                payload["max_answer_characters"],
                "max_answer_characters",
                1,
                32_768,
            ),
            max_statements=_integer(payload["max_statements"], "max_statements", 1, 50),
            wait_ms=_integer(payload["wait_ms"], "wait_ms", 0, 30_000),
            max_evidence_age_seconds=age,
            max_attempts=_integer(payload["max_attempts"], "max_attempts", 1, 2),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "evidence_limit": self.evidence_limit,
            "max_evidence_bytes": self.max_evidence_bytes,
            "max_answer_characters": self.max_answer_characters,
            "max_statements": self.max_statements,
            "wait_ms": self.wait_ms,
            "max_evidence_age_seconds": self.max_evidence_age_seconds,
            "max_attempts": self.max_attempts,
        }


@dataclass(frozen=True)
class QuestionTemporalV1:
    as_of: str | None
    during_from: str | None
    during_to: str | None
    known_as_of: str | None

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> QuestionTemporalV1:
        if not isinstance(payload, Mapping):
            raise QuestionContractError("temporal must be an object")
        _exact(
            payload,
            frozenset({"as_of", "during_from", "during_to", "known_as_of"}),
            "temporal",
        )
        during_from = _timestamp(payload["during_from"], "during_from")
        during_to = _timestamp(payload["during_to"], "during_to")
        if during_from is not None and during_to is not None and during_from > during_to:
            raise QuestionContractError("during_from must not exceed during_to")
        return cls(
            as_of=_timestamp(payload["as_of"], "as_of"),
            during_from=during_from,
            during_to=during_to,
            known_as_of=_timestamp(payload["known_as_of"], "known_as_of"),
        )

    def to_dict(self) -> dict[str, str | None]:
        return {
            "as_of": self.as_of,
            "during_from": self.during_from,
            "during_to": self.during_to,
            "known_as_of": self.known_as_of,
        }


def _filters(value: Any) -> dict[str, Any]:
    # The public search parser owns filter validation and normalization.
    try:
        return PostSearchRequest.from_dict(
            {
                "schema_version": 1,
                "request_id": "question-filter-validation",
                "profile_id": "public",
                "query": "question",
                "filters": value,
                "page_size": 1,
                "cursor": None,
            }
        ).filters
    except ContractValidationError as exc:
        raise QuestionContractError(str(exc)) from exc


@dataclass(frozen=True)
class QuestionRequestV1:
    schema_version: int
    request_id: str
    profile_id: str
    question: str
    filters: dict[str, Any]
    temporal: QuestionTemporalV1
    answer_mode: str
    model_fallback: str
    limits: QuestionLimitsV1

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> QuestionRequestV1:
        if not isinstance(payload, Mapping):
            raise QuestionContractError("question request must be an object")
        _exact(
            payload,
            frozenset(
                {
                    "schema_version",
                    "request_id",
                    "profile_id",
                    "question",
                    "filters",
                    "temporal",
                    "answer_mode",
                    "model_fallback",
                    "limits",
                }
            ),
            "question request",
        )
        if payload["schema_version"] != QUESTION_SCHEMA_VERSION:
            raise QuestionContractError("schema_version must be 1")
        profile_id = _text(payload["profile_id"], "profile_id", 128)
        if _PROFILE_ID.fullmatch(profile_id) is None:
            raise QuestionContractError("profile_id is invalid")
        answer_mode = payload["answer_mode"]
        if answer_mode not in {"synthesized", "evidence_only"}:
            raise QuestionContractError("answer_mode is invalid")
        fallback = payload["model_fallback"]
        if fallback not in {"none", "evidence_only"}:
            raise QuestionContractError("model_fallback is invalid")
        return cls(
            schema_version=1,
            request_id=_text(payload["request_id"], "request_id", 128),
            profile_id=profile_id,
            question=_text(payload["question"], "question", 4096),
            filters=_filters(payload["filters"]),
            temporal=QuestionTemporalV1.from_dict(payload["temporal"]),
            answer_mode=str(answer_mode),
            model_fallback=str(fallback),
            limits=QuestionLimitsV1.from_dict(payload["limits"]),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "request_id": self.request_id,
            "profile_id": self.profile_id,
            "question": self.question,
            "filters": dict(self.filters),
            "temporal": self.temporal.to_dict(),
            "answer_mode": self.answer_mode,
            "model_fallback": self.model_fallback,
            "limits": self.limits.to_dict(),
        }

    @property
    def request_fingerprint(self) -> str:
        payload = self.to_dict()
        payload.pop("request_id")
        return digest(payload)

    @property
    def idempotency_key(self) -> str:
        return "question-request:v1:" + stable_id(
            "request", {"request_id": self.request_id, "fingerprint": self.request_fingerprint}
        ).removeprefix("request-")


def validate_error_code(value: Any, name: str = "error_code") -> str:
    code = _text(value, name, 64)
    if _SAFE_CODE.fullmatch(code) is None:
        raise QuestionContractError(f"{name} is invalid")
    return code


@dataclass(frozen=True)
class QuestionCitationV1:
    evidence_id: str
    storage_family: str
    version_id: str
    content_hash: str
    source_url: str
    access_partition_id: str

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> QuestionCitationV1:
        if not isinstance(payload, Mapping):
            raise QuestionContractError("citation must be an object")
        _exact(
            payload,
            frozenset(
                {
                    "evidence_id",
                    "storage_family",
                    "version_id",
                    "content_hash",
                    "source_url",
                    "access_partition_id",
                }
            ),
            "citation",
        )
        storage_family = payload["storage_family"]
        if storage_family not in {"legacy", "temporal"}:
            raise QuestionContractError("citation storage_family is invalid")
        return cls(
            evidence_id=_text(payload["evidence_id"], "evidence_id", 128),
            storage_family=str(storage_family),
            version_id=_text(payload["version_id"], "version_id", 256),
            content_hash=_text(payload["content_hash"], "content_hash", 256),
            source_url=_text(payload["source_url"], "source_url", 4096),
            access_partition_id=_text(
                payload["access_partition_id"], "access_partition_id", 256
            ),
        )

    def to_dict(self) -> dict[str, str]:
        return {
            "evidence_id": self.evidence_id,
            "storage_family": self.storage_family,
            "version_id": self.version_id,
            "content_hash": self.content_hash,
            "source_url": self.source_url,
            "access_partition_id": self.access_partition_id,
        }


@dataclass(frozen=True)
class EvidenceReadRequestV1:
    schema_version: int
    request_id: str
    profile_id: str
    refs: tuple[QuestionCitationV1, ...]
    max_response_bytes: int

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> EvidenceReadRequestV1:
        if not isinstance(payload, Mapping):
            raise QuestionContractError("evidence read request must be an object")
        _exact(
            payload,
            frozenset(
                {
                    "schema_version",
                    "request_id",
                    "profile_id",
                    "refs",
                    "max_response_bytes",
                }
            ),
            "evidence read request",
        )
        if payload["schema_version"] != QUESTION_SCHEMA_VERSION:
            raise QuestionContractError(
                f"schema_version must be {QUESTION_SCHEMA_VERSION}"
            )
        profile_id = _text(payload["profile_id"], "profile_id", 128)
        if _PROFILE_ID.fullmatch(profile_id) is None:
            raise QuestionContractError("profile_id is invalid")
        raw_refs = payload["refs"]
        if not isinstance(raw_refs, list) or not 1 <= len(raw_refs) <= 20:
            raise QuestionContractError("refs must contain between 1 and 20 items")
        refs = tuple(QuestionCitationV1.from_dict(item) for item in raw_refs)
        evidence_ids = [item.evidence_id for item in refs]
        if len(evidence_ids) != len(set(evidence_ids)):
            raise QuestionContractError("refs must not contain duplicates")
        ref_identities = [
            (
                item.storage_family,
                item.version_id,
                item.content_hash,
                item.source_url,
                item.access_partition_id,
            )
            for item in refs
        ]
        if len(ref_identities) != len(set(ref_identities)):
            raise QuestionContractError("refs must not contain duplicates")
        allowed_partitions = {"public", f"profile:{profile_id}"}
        if any(item.access_partition_id not in allowed_partitions for item in refs):
            raise QuestionContractError("refs contain a mixed-profile partition")
        request_id = _text(payload["request_id"], "request_id", 128)
        max_response_bytes = _integer(
            payload["max_response_bytes"],
            "max_response_bytes",
            512,
            131_072,
        )
        minimum_response_bytes = _serialized_size_with_counter(
            {
                "schema_version": QUESTION_SCHEMA_VERSION,
                "request_id": request_id,
                "items": [],
                "omitted_refs": evidence_ids,
                "truncated": True,
            },
            "response_bytes",
        )
        if max_response_bytes < minimum_response_bytes:
            raise QuestionContractError(
                "max_response_bytes cannot represent all omitted refs"
            )
        return cls(
            schema_version=QUESTION_SCHEMA_VERSION,
            request_id=request_id,
            profile_id=profile_id,
            refs=refs,
            max_response_bytes=max_response_bytes,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "request_id": self.request_id,
            "profile_id": self.profile_id,
            "refs": [item.to_dict() for item in self.refs],
            "max_response_bytes": self.max_response_bytes,
        }


_EVIDENCE_FIELDS = frozenset(
    {
        "storage_family",
        "version_id",
        "source",
        "source_native_id",
        "canonical_url",
        "author",
        "title",
        "text",
        "text_truncated",
        "content_hash",
        "access_partition_id",
        "published_at",
        "observed_at",
        "fetched_at",
        "valid_from",
        "valid_to",
        "system_from",
        "system_to",
        "created_at",
        "metadata",
        "media",
        "collection_refs",
        "topic_ids",
        "provenance",
    }
)


def _evidence_record(
    value: Any, ref: QuestionCitationV1
) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise QuestionContractError("available evidence must be an object")
    _exact(value, _EVIDENCE_FIELDS, "available evidence")
    for field, expected in (
        ("storage_family", ref.storage_family),
        ("version_id", ref.version_id),
        ("content_hash", ref.content_hash),
        ("canonical_url", ref.source_url),
        ("access_partition_id", ref.access_partition_id),
    ):
        if value[field] != expected:
            raise QuestionContractError(
                f"available evidence {field} does not match ref"
            )
    author = value["author"]
    if author is not None:
        author = _text(author, "evidence author", 1024)
    text_truncated = value["text_truncated"]
    if not isinstance(text_truncated, bool):
        raise QuestionContractError("evidence text_truncated must be a boolean")
    observed_at = _timestamp(
        value["observed_at"], "evidence observed_at", optional=False
    )
    metadata = value["metadata"]
    provenance = value["provenance"]
    media = value["media"]
    if not isinstance(metadata, Mapping) or not isinstance(provenance, Mapping):
        raise QuestionContractError("evidence metadata and provenance must be objects")
    if not isinstance(media, list):
        raise QuestionContractError("evidence media must be a list")
    try:
        structured_size = len(
            canonical_json(
                {"metadata": metadata, "media": media, "provenance": provenance}
            ).encode()
        )
    except (TypeError, ValueError) as exc:
        raise QuestionContractError("evidence structured fields are invalid") from exc
    if structured_size > 65_536:
        raise QuestionContractError("evidence structured fields are oversized")
    return {
        "storage_family": ref.storage_family,
        "version_id": ref.version_id,
        "source": _text(value["source"], "evidence source", 128),
        "source_native_id": _text(
            value["source_native_id"], "evidence source_native_id", 1024
        ),
        "canonical_url": ref.source_url,
        "author": author,
        "title": _text(value["title"], "evidence title", 4096),
        "text": _text(value["text"], "evidence text", 32_768),
        "text_truncated": text_truncated,
        "content_hash": ref.content_hash,
        "access_partition_id": ref.access_partition_id,
        "published_at": _timestamp(
            value["published_at"], "evidence published_at"
        ),
        "observed_at": observed_at,
        "fetched_at": _timestamp(value["fetched_at"], "evidence fetched_at"),
        "valid_from": _timestamp(value["valid_from"], "evidence valid_from"),
        "valid_to": _timestamp(value["valid_to"], "evidence valid_to"),
        "system_from": _timestamp(value["system_from"], "evidence system_from"),
        "system_to": _timestamp(value["system_to"], "evidence system_to"),
        "created_at": _timestamp(value["created_at"], "evidence created_at"),
        "metadata": dict(metadata),
        "media": list(media),
        "collection_refs": list(
            _string_list(
                value["collection_refs"],
                "evidence collection_refs",
                maximum=100,
                item_maximum=256,
            )
        ),
        "topic_ids": list(
            _string_list(
                value["topic_ids"],
                "evidence topic_ids",
                maximum=100,
                item_maximum=256,
            )
        ),
        "provenance": dict(provenance),
    }


@dataclass(frozen=True)
class EvidenceReadItemV1:
    ref: QuestionCitationV1
    status: str
    evidence: Mapping[str, Any] | None

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> EvidenceReadItemV1:
        if not isinstance(payload, Mapping):
            raise QuestionContractError("evidence read item must be an object")
        _exact(payload, frozenset({"ref", "status", "evidence"}), "evidence read item")
        status = payload["status"]
        if status not in {"available", "unavailable"}:
            raise QuestionContractError("evidence read status is invalid")
        evidence = payload["evidence"]
        if status == "unavailable" and evidence is not None:
            raise QuestionContractError("unavailable evidence must be null")
        ref = QuestionCitationV1.from_dict(payload["ref"])
        return cls(
            ref=ref,
            status=str(status),
            evidence=_evidence_record(evidence, ref) if status == "available" else None,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "ref": self.ref.to_dict(),
            "status": self.status,
            "evidence": dict(self.evidence) if self.evidence is not None else None,
        }


@dataclass(frozen=True)
class EvidenceReadResponseV1:
    schema_version: int
    request_id: str
    items: tuple[EvidenceReadItemV1, ...]
    omitted_refs: tuple[str, ...]
    truncated: bool
    response_bytes: int

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> EvidenceReadResponseV1:
        if not isinstance(payload, Mapping):
            raise QuestionContractError("evidence read response must be an object")
        _exact(
            payload,
            frozenset(
                {
                    "schema_version",
                    "request_id",
                    "items",
                    "omitted_refs",
                    "truncated",
                    "response_bytes",
                }
            ),
            "evidence read response",
        )
        if payload["schema_version"] != QUESTION_SCHEMA_VERSION:
            raise QuestionContractError(
                f"schema_version must be {QUESTION_SCHEMA_VERSION}"
            )
        raw_items = payload["items"]
        if not isinstance(raw_items, list) or len(raw_items) > 20:
            raise QuestionContractError("items must be a list of at most 20 items")
        items = tuple(EvidenceReadItemV1.from_dict(item) for item in raw_items)
        omitted_refs = _string_list(
            payload["omitted_refs"], "omitted_refs", maximum=20, item_maximum=128
        )
        correlated = [item.ref.evidence_id for item in items] + list(omitted_refs)
        if len(correlated) != len(set(correlated)):
            raise QuestionContractError("response refs must not contain duplicates")
        truncated = payload["truncated"]
        if not isinstance(truncated, bool) or truncated != bool(omitted_refs):
            raise QuestionContractError("truncated must match omitted_refs")
        result = cls(
            schema_version=QUESTION_SCHEMA_VERSION,
            request_id=_text(payload["request_id"], "request_id", 128),
            items=items,
            omitted_refs=omitted_refs,
            truncated=truncated,
            response_bytes=_integer(
                payload["response_bytes"], "response_bytes", 2, 131_072
            ),
        )
        if result.response_bytes != len(canonical_json(result.to_dict()).encode()):
            raise QuestionContractError(
                "response_bytes does not match serialized response"
            )
        return result

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "request_id": self.request_id,
            "items": [item.to_dict() for item in self.items],
            "omitted_refs": list(self.omitted_refs),
            "truncated": self.truncated,
            "response_bytes": self.response_bytes,
        }


@dataclass(frozen=True)
class AnswerStatementV1:
    statement_id: str
    text: str
    statement_kind: str
    support_state: str
    citations: tuple[QuestionCitationV1, ...]
    alternatives: tuple[str, ...]

    @classmethod
    def create(
        cls,
        *,
        text: str,
        statement_kind: str,
        support_state: str,
        citations: tuple[QuestionCitationV1, ...],
        alternatives: tuple[str, ...],
    ) -> AnswerStatementV1:
        core = {
            "text": text,
            "statement_kind": statement_kind,
            "support_state": support_state,
            "citations": [citation.to_dict() for citation in citations],
            "alternatives": list(alternatives),
        }
        return cls.from_dict({"statement_id": stable_id("statement", core), **core})

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> AnswerStatementV1:
        if not isinstance(payload, Mapping):
            raise QuestionContractError("statement must be an object")
        fields = frozenset(
            {
                "statement_id",
                "text",
                "statement_kind",
                "support_state",
                "citations",
                "alternatives",
            }
        )
        _exact(payload, fields, "statement")
        kind = payload["statement_kind"]
        if kind not in {"source_fact", "temporal_inference", "analytical_inference"}:
            raise QuestionContractError("statement_kind is invalid")
        support = payload["support_state"]
        if support not in {"supported", "mixed", "insufficient"}:
            raise QuestionContractError("support_state is invalid")
        raw_citations = payload["citations"]
        if not isinstance(raw_citations, list) or len(raw_citations) > 20:
            raise QuestionContractError("citations must be a bounded list")
        citations = tuple(QuestionCitationV1.from_dict(item) for item in raw_citations)
        if len({item.evidence_id for item in citations}) != len(citations):
            raise QuestionContractError("citations must not contain duplicates")
        alternatives = _string_list(
            payload["alternatives"], "alternatives", maximum=8, item_maximum=4096
        )
        if support == "supported" and not citations:
            raise QuestionContractError("supported statement requires a citation")
        if support == "mixed" and (len(citations) < 2 or len(alternatives) < 2):
            raise QuestionContractError(
                "mixed statement requires two citations and two alternatives"
            )
        core = {key: payload[key] for key in fields if key != "statement_id"}
        statement_id = _text(payload["statement_id"], "statement_id", 128)
        if statement_id != stable_id("statement", core):
            raise QuestionContractError("statement_id does not match statement content")
        return cls(
            statement_id=statement_id,
            text=_text(payload["text"], "statement text", 8192),
            statement_kind=str(kind),
            support_state=str(support),
            citations=citations,
            alternatives=alternatives,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "statement_id": self.statement_id,
            "text": self.text,
            "statement_kind": self.statement_kind,
            "support_state": self.support_state,
            "citations": [citation.to_dict() for citation in self.citations],
            "alternatives": list(self.alternatives),
        }


@dataclass(frozen=True)
class QuestionErrorV1:
    code: str
    message: str
    retryable: bool

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> QuestionErrorV1:
        if not isinstance(payload, Mapping):
            raise QuestionContractError("error must be an object")
        _exact(payload, frozenset({"code", "message", "retryable"}), "error")
        if not isinstance(payload["retryable"], bool):
            raise QuestionContractError("error retryable must be boolean")
        return cls(
            code=validate_error_code(payload["code"]),
            message=_text(payload["message"], "error message", 1024),
            retryable=payload["retryable"],
        )

    def to_dict(self) -> dict[str, Any]:
        return {"code": self.code, "message": self.message, "retryable": self.retryable}


_ANSWER_STATES = frozenset(
    {
        "answered",
        "no_evidence",
        "insufficient_evidence",
        "conflicting_evidence",
        "model_unavailable",
        "failed",
    }
)


@dataclass(frozen=True)
class QuestionAnswerV1:
    schema_version: int
    question_id: str
    answer_id: str
    request_fingerprint: str
    search_head_id: str
    evidence_set_id: str
    answer_state: str
    summary: str
    statements: tuple[AnswerStatementV1, ...]
    uncertainty_codes: tuple[str, ...]
    coverage: dict[str, bool]
    worker_ref: str
    generated_at: str
    input_digest: str
    output_digest: str
    attempt_count: int
    model_invoked: bool
    evidence_only_fallback: bool
    cache_only: bool
    acquisition_performed: bool
    error: QuestionErrorV1 | None

    @classmethod
    def create(cls, **values: Any) -> QuestionAnswerV1:
        core = {
            "schema_version": 1,
            **{
                key: (
                    [item.to_dict() for item in value]
                    if key == "statements"
                    else list(value)
                    if key == "uncertainty_codes"
                    else value.to_dict()
                    if key == "error" and value is not None
                    else value
                )
                for key, value in values.items()
            },
            "cache_only": True,
            "acquisition_performed": False,
        }
        output_digest = digest(core)
        answer_id = stable_id(
            "answer",
            {
                "question_id": core["question_id"],
                "input_digest": core["input_digest"],
                "output_digest": output_digest,
            },
        )
        return cls.from_dict(
            {**core, "answer_id": answer_id, "output_digest": output_digest}
        )

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> QuestionAnswerV1:
        if not isinstance(payload, Mapping):
            raise QuestionContractError("answer must be an object")
        fields = frozenset(
            {
                "schema_version",
                "question_id",
                "answer_id",
                "request_fingerprint",
                "search_head_id",
                "evidence_set_id",
                "answer_state",
                "summary",
                "statements",
                "uncertainty_codes",
                "coverage",
                "worker_ref",
                "generated_at",
                "input_digest",
                "output_digest",
                "attempt_count",
                "model_invoked",
                "evidence_only_fallback",
                "cache_only",
                "acquisition_performed",
                "error",
            }
        )
        _exact(payload, fields, "answer")
        if payload["schema_version"] != 1:
            raise QuestionContractError("answer schema_version must be 1")
        state = payload["answer_state"]
        if state not in _ANSWER_STATES:
            raise QuestionContractError("answer_state is invalid")
        raw_statements = payload["statements"]
        if not isinstance(raw_statements, list) or len(raw_statements) > 50:
            raise QuestionContractError("statements must be a bounded list")
        statements = tuple(AnswerStatementV1.from_dict(item) for item in raw_statements)
        if state == "answered" and not statements:
            raise QuestionContractError("answered result requires statements")
        if state == "conflicting_evidence" and not any(
            statement.support_state == "mixed" for statement in statements
        ):
            raise QuestionContractError("conflicting result requires a mixed statement")
        coverage = payload["coverage"]
        if not isinstance(coverage, Mapping):
            raise QuestionContractError("coverage must be an object")
        _exact(coverage, frozenset({"partial", "stale"}), "coverage")
        if not all(isinstance(coverage[field], bool) for field in coverage):
            raise QuestionContractError("coverage flags must be boolean")
        uncertainty = _string_list(
            payload["uncertainty_codes"], "uncertainty_codes", maximum=20, item_maximum=64
        )
        for code in uncertainty:
            validate_error_code(code, "uncertainty code")
        for field in (
            "model_invoked",
            "evidence_only_fallback",
            "cache_only",
            "acquisition_performed",
        ):
            if not isinstance(payload[field], bool):
                raise QuestionContractError(f"{field} must be boolean")
        if payload["cache_only"] is not True or payload["acquisition_performed"] is not False:
            raise QuestionContractError("Packet 1 answers must remain cache-only")
        error = None if payload["error"] is None else QuestionErrorV1.from_dict(payload["error"])
        core = {key: payload[key] for key in fields if key not in {"answer_id", "output_digest"}}
        output_digest = _text(payload["output_digest"], "output_digest", 128)
        if output_digest != digest(core):
            raise QuestionContractError("output_digest does not match answer content")
        question_id = _text(payload["question_id"], "question_id", 128)
        input_digest = _text(payload["input_digest"], "input_digest", 128)
        answer_id = _text(payload["answer_id"], "answer_id", 128)
        if answer_id != stable_id(
            "answer",
            {
                "question_id": question_id,
                "input_digest": input_digest,
                "output_digest": output_digest,
            },
        ):
            raise QuestionContractError("answer_id does not match answer content")
        return cls(
            schema_version=1,
            question_id=question_id,
            answer_id=answer_id,
            request_fingerprint=_text(
                payload["request_fingerprint"], "request_fingerprint", 128
            ),
            search_head_id=_text(payload["search_head_id"], "search_head_id", 128),
            evidence_set_id=_text(payload["evidence_set_id"], "evidence_set_id", 128),
            answer_state=str(state),
            summary=_text(payload["summary"], "summary", 32768),
            statements=statements,
            uncertainty_codes=uncertainty,
            coverage={"partial": coverage["partial"], "stale": coverage["stale"]},
            worker_ref=_text(payload["worker_ref"], "worker_ref", 256),
            generated_at=_timestamp(payload["generated_at"], "generated_at", optional=False) or "",
            input_digest=input_digest,
            output_digest=output_digest,
            attempt_count=_integer(payload["attempt_count"], "attempt_count", 0, 2),
            model_invoked=payload["model_invoked"],
            evidence_only_fallback=payload["evidence_only_fallback"],
            cache_only=True,
            acquisition_performed=False,
            error=error,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "question_id": self.question_id,
            "answer_id": self.answer_id,
            "request_fingerprint": self.request_fingerprint,
            "search_head_id": self.search_head_id,
            "evidence_set_id": self.evidence_set_id,
            "answer_state": self.answer_state,
            "summary": self.summary,
            "statements": [statement.to_dict() for statement in self.statements],
            "uncertainty_codes": list(self.uncertainty_codes),
            "coverage": dict(self.coverage),
            "worker_ref": self.worker_ref,
            "generated_at": self.generated_at,
            "input_digest": self.input_digest,
            "output_digest": self.output_digest,
            "attempt_count": self.attempt_count,
            "model_invoked": self.model_invoked,
            "evidence_only_fallback": self.evidence_only_fallback,
            "cache_only": self.cache_only,
            "acquisition_performed": self.acquisition_performed,
            "error": self.error.to_dict() if self.error else None,
        }


@dataclass(frozen=True)
class QuestionStatusV1:
    schema_version: int
    question_id: str
    state: str
    attempt_count: int
    max_attempts: int
    lease_generation: int
    lease_expires_at: str | None
    answer: QuestionAnswerV1 | None
    error: QuestionErrorV1 | None

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> QuestionStatusV1:
        if not isinstance(payload, Mapping):
            raise QuestionContractError("status must be an object")
        _exact(
            payload,
            frozenset(
                {
                    "schema_version",
                    "question_id",
                    "state",
                    "attempt_count",
                    "max_attempts",
                    "lease_generation",
                    "lease_expires_at",
                    "answer",
                    "error",
                }
            ),
            "status",
        )
        if payload["schema_version"] != 1:
            raise QuestionContractError("status schema_version must be 1")
        state = payload["state"]
        allowed = _ANSWER_STATES | {"pending", "running"}
        if state not in allowed:
            raise QuestionContractError("status state is invalid")
        answer = None if payload["answer"] is None else QuestionAnswerV1.from_dict(payload["answer"])
        error = None if payload["error"] is None else QuestionErrorV1.from_dict(payload["error"])
        if state in {"pending", "running"} and answer is not None:
            raise QuestionContractError("non-terminal status cannot contain an answer")
        if answer is not None and answer.answer_state != state:
            raise QuestionContractError("status and answer state must match")
        return cls(
            schema_version=1,
            question_id=_text(payload["question_id"], "question_id", 128),
            state=str(state),
            attempt_count=_integer(payload["attempt_count"], "attempt_count", 0, 2),
            max_attempts=_integer(payload["max_attempts"], "max_attempts", 1, 2),
            lease_generation=_integer(
                payload["lease_generation"], "lease_generation", 0, 1_000_000
            ),
            lease_expires_at=_timestamp(payload["lease_expires_at"], "lease_expires_at"),
            answer=answer,
            error=error,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "question_id": self.question_id,
            "state": self.state,
            "attempt_count": self.attempt_count,
            "max_attempts": self.max_attempts,
            "lease_generation": self.lease_generation,
            "lease_expires_at": self.lease_expires_at,
            "answer": self.answer.to_dict() if self.answer else None,
            "error": self.error.to_dict() if self.error else None,
        }
