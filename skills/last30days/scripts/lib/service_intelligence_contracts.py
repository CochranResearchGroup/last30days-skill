"""Deterministic contracts and durable queue for bounded App Intelligence tasks."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import StrEnum
from pathlib import Path
from typing import Callable, Mapping, Protocol

import store


Clock = Callable[[], datetime]

CONTENT_ASSESSMENT_OUTPUT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "action",
        "proposals",
        "uncertainty_codes",
        "rationale",
    ],
    "properties": {
        "action": {"const": "record_assessment"},
        "proposals": {
            "type": "array",
            "maxItems": 100,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "proposal_kind",
                    "proposal_key",
                    "confidence",
                    "evidence_ids",
                    "payload",
                ],
                "properties": {
                    "proposal_kind": {"const": "content_signal"},
                    "proposal_key": {
                        "type": "string",
                        "minLength": 1,
                        "maxLength": 256,
                    },
                    "confidence": {
                        "type": "number",
                        "minimum": 0,
                        "maximum": 1,
                    },
                    "evidence_ids": {
                        "type": "array",
                        "minItems": 1,
                        "maxItems": 20,
                        "items": {
                            "type": "string",
                            "minLength": 1,
                            "maxLength": 128,
                        },
                    },
                    "payload": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": [
                            "content_type",
                            "novelty",
                            "relevance",
                            "follow_up_priority",
                        ],
                        "properties": {
                            "content_type": {
                                "type": "string",
                                "enum": [
                                    "post",
                                    "article",
                                    "video",
                                    "comment",
                                    "profile",
                                    "other",
                                ],
                            },
                            "novelty": {
                                "type": "string",
                                "enum": [
                                    "duplicate",
                                    "known_update",
                                    "novel",
                                    "uncertain",
                                ],
                            },
                            "relevance": {
                                "type": "string",
                                "enum": ["low", "medium", "high", "uncertain"],
                            },
                            "follow_up_priority": {
                                "type": "string",
                                "enum": ["none", "normal", "high", "review"],
                            },
                            "entity_candidates": {
                                "type": "array",
                                "maxItems": 20,
                                "items": {"type": "string", "maxLength": 256},
                            },
                            "claim_candidates": {
                                "type": "array",
                                "maxItems": 20,
                                "items": {"type": "string", "maxLength": 256},
                            },
                            "event_candidates": {
                                "type": "array",
                                "maxItems": 20,
                                "items": {"type": "string", "maxLength": 256},
                            },
                            "profile_change_candidates": {
                                "type": "array",
                                "maxItems": 20,
                                "items": {"type": "string", "maxLength": 256},
                            },
                        },
                    },
                },
            },
        },
        "uncertainty_codes": {
            "type": "array",
            "maxItems": 20,
            "items": {"type": "string", "minLength": 1, "maxLength": 64},
        },
        "rationale": {"type": "string", "minLength": 1, "maxLength": 4096},
    },
}


class StructuredAssessmentClient(Protocol):
    def structured_turn(
        self,
        *,
        prompt: str,
        output_schema: Mapping[str, object],
        cwd: Path,
        model: str | None = None,
    ): ...


def _canonical_json(value: object) -> str:
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def _digest(value: object) -> str:
    return "sha256:" + hashlib.sha256(_canonical_json(value).encode()).hexdigest()


def _stable_id(prefix: str, value: object) -> str:
    return f"{prefix}-{hashlib.sha256(_canonical_json(value).encode()).hexdigest()[:32]}"


def _timestamp(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _exact(
    payload: Mapping[str, object],
    *,
    required: frozenset[str],
) -> None:
    missing = sorted(required - set(payload))
    unknown = sorted(set(payload) - required)
    if missing:
        raise ValueError(f"missing fields: {', '.join(missing)}")
    if unknown:
        raise ValueError(f"unknown fields: {', '.join(unknown)}")


def _text(value: object, field: str, maximum: int = 4096) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    if len(value) > maximum:
        raise ValueError(f"{field} exceeds {maximum} characters")
    return value


def _optional_text(value: object, field: str, maximum: int = 4096) -> str | None:
    if value is None:
        return None
    return _text(value, field, maximum)


def _digest_text(value: object, field: str) -> str:
    text = _text(value, field, 71)
    if (
        not text.startswith("sha256:")
        or len(text) != 71
        or any(character not in "0123456789abcdef" for character in text[7:])
    ):
        raise ValueError(f"{field} must be a sha256 digest")
    return text


def _time(value: object, field: str) -> str:
    text = _text(value, field, 64)
    parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field} must include a timezone")
    return _timestamp(parsed)


class ValidatorCode(StrEnum):
    SCHEMA_INVALID = "schema_invalid"
    CORRELATION_MISMATCH = "correlation_mismatch"
    INPUT_DIGEST_MISMATCH = "input_digest_mismatch"
    OUTPUT_DIGEST_MISMATCH = "output_digest_mismatch"
    POLICY_VERSION_MISMATCH = "policy_version_mismatch"
    ACTION_NOT_ALLOWED = "action_not_allowed"
    UNKNOWN_EVIDENCE = "unknown_evidence"
    ACCESS_PARTITION_MISMATCH = "access_partition_mismatch"
    BUDGET_EXHAUSTED = "budget_exhausted"
    DUPLICATE_PROPOSAL = "duplicate_proposal"


@dataclass(frozen=True)
class IntelligenceEvidenceRef:
    evidence_id: str
    version_id: str
    chunk_id: str
    content_digest: str
    observed_at: str
    valid_from: str | None
    valid_to: str | None
    access_partition_id: str

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> IntelligenceEvidenceRef:
        fields = frozenset(
            {
                "evidence_id",
                "version_id",
                "chunk_id",
                "content_digest",
                "observed_at",
                "valid_from",
                "valid_to",
                "access_partition_id",
            }
        )
        _exact(payload, required=fields)
        return cls(
            evidence_id=_text(payload["evidence_id"], "evidence_id", 128),
            version_id=_text(payload["version_id"], "version_id", 128),
            chunk_id=_text(payload["chunk_id"], "chunk_id", 128),
            content_digest=_digest_text(payload["content_digest"], "content_digest"),
            observed_at=_time(payload["observed_at"], "observed_at"),
            valid_from=(
                _time(payload["valid_from"], "valid_from")
                if payload["valid_from"] is not None
                else None
            ),
            valid_to=(
                _time(payload["valid_to"], "valid_to")
                if payload["valid_to"] is not None
                else None
            ),
            access_partition_id=_text(
                payload["access_partition_id"], "access_partition_id", 256
            ),
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "evidence_id": self.evidence_id,
            "version_id": self.version_id,
            "chunk_id": self.chunk_id,
            "content_digest": self.content_digest,
            "observed_at": self.observed_at,
            "valid_from": self.valid_from,
            "valid_to": self.valid_to,
            "access_partition_id": self.access_partition_id,
        }


@dataclass(frozen=True)
class IntelligenceLimits:
    max_items: int
    max_bytes: int
    max_calls: int
    max_cost_cents: int
    wall_timeout_seconds: int

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> IntelligenceLimits:
        fields = frozenset(
            {
                "max_items",
                "max_bytes",
                "max_calls",
                "max_cost_cents",
                "wall_timeout_seconds",
            }
        )
        _exact(payload, required=fields)
        values: dict[str, int] = {}
        bounds = {
            "max_items": (1, 100),
            "max_bytes": (1024, 1_048_576),
            "max_calls": (0, 5),
            "max_cost_cents": (0, 10_000),
            "wall_timeout_seconds": (1, 3600),
        }
        for field, (minimum, maximum) in bounds.items():
            value = payload[field]
            if isinstance(value, bool) or not isinstance(value, int):
                raise ValueError(f"{field} must be an integer")
            if not minimum <= value <= maximum:
                raise ValueError(f"{field} is outside limits")
            values[field] = value
        return cls(**values)

    def to_dict(self) -> dict[str, int]:
        return {
            "max_items": self.max_items,
            "max_bytes": self.max_bytes,
            "max_calls": self.max_calls,
            "max_cost_cents": self.max_cost_cents,
            "wall_timeout_seconds": self.wall_timeout_seconds,
        }


@dataclass(frozen=True)
class IntelligenceTaskRequest:
    schema_version: int
    contract_name: str
    contract_version: int
    task_type: str
    task_id: str
    job_id: str | None
    run_id: str | None
    idempotency_key: str
    input_artifact_ref: str
    input_digest: str
    evidence_refs: tuple[IntelligenceEvidenceRef, ...]
    source_version_ids: tuple[str, ...]
    corpus_version: str | None
    policy_version: str
    worker_config_ref: str
    access_partition_id: str
    redaction_class: str
    requested_at: str
    allowed_actions: tuple[str, ...]
    limits: IntelligenceLimits

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> IntelligenceTaskRequest:
        fields = frozenset(
            {
                "schema_version",
                "contract_name",
                "contract_version",
                "task_type",
                "task_id",
                "job_id",
                "run_id",
                "idempotency_key",
                "input_artifact_ref",
                "input_digest",
                "evidence_refs",
                "source_version_ids",
                "corpus_version",
                "policy_version",
                "worker_config_ref",
                "access_partition_id",
                "redaction_class",
                "requested_at",
                "allowed_actions",
                "limits",
            }
        )
        _exact(payload, required=fields)
        if payload["schema_version"] != 1:
            raise ValueError("schema_version must be 1")
        if payload["contract_name"] != "intelligence_task_request":
            raise ValueError("contract_name is invalid")
        if payload["contract_version"] != 1:
            raise ValueError("contract_version is unsupported")
        evidence = payload["evidence_refs"]
        if not isinstance(evidence, list) or not 1 <= len(evidence) <= 100:
            raise ValueError("evidence_refs must contain between 1 and 100 items")
        version_ids = payload["source_version_ids"]
        if (
            not isinstance(version_ids, list)
            or not 1 <= len(version_ids) <= 100
            or not all(isinstance(item, str) and item for item in version_ids)
        ):
            raise ValueError("source_version_ids are invalid")
        actions = payload["allowed_actions"]
        if (
            not isinstance(actions, list)
            or not 1 <= len(actions) <= 8
            or not all(isinstance(item, str) and item for item in actions)
        ):
            raise ValueError("allowed_actions are invalid")
        if len(set(actions)) != len(actions):
            raise ValueError("allowed_actions must be unique")
        redaction = _text(payload["redaction_class"], "redaction_class", 32)
        if redaction not in {"public", "authenticated", "restricted"}:
            raise ValueError("redaction_class is invalid")
        refs = tuple(
            IntelligenceEvidenceRef.from_dict(item)
            for item in evidence
            if isinstance(item, Mapping)
        )
        if len(refs) != len(evidence):
            raise ValueError("evidence_refs must be objects")
        partition = _text(
            payload["access_partition_id"], "access_partition_id", 256
        )
        if any(ref.access_partition_id != partition for ref in refs):
            raise ValueError("evidence access partition mismatch")
        return cls(
            schema_version=1,
            contract_name="intelligence_task_request",
            contract_version=1,
            task_type=_text(payload["task_type"], "task_type", 64),
            task_id=_text(payload["task_id"], "task_id", 128),
            job_id=_optional_text(payload["job_id"], "job_id", 128),
            run_id=_optional_text(payload["run_id"], "run_id", 128),
            idempotency_key=_text(
                payload["idempotency_key"], "idempotency_key", 256
            ),
            input_artifact_ref=_text(
                payload["input_artifact_ref"], "input_artifact_ref", 512
            ),
            input_digest=_digest_text(payload["input_digest"], "input_digest"),
            evidence_refs=refs,
            source_version_ids=tuple(version_ids),
            corpus_version=_optional_text(
                payload["corpus_version"], "corpus_version", 128
            ),
            policy_version=_text(
                payload["policy_version"], "policy_version", 128
            ),
            worker_config_ref=_text(
                payload["worker_config_ref"], "worker_config_ref", 256
            ),
            access_partition_id=partition,
            redaction_class=redaction,
            requested_at=_time(payload["requested_at"], "requested_at"),
            allowed_actions=tuple(actions),
            limits=IntelligenceLimits.from_dict(payload["limits"]),  # type: ignore[arg-type]
        )

    @classmethod
    def validate(cls, payload: Mapping[str, object]) -> ValidatorCode | None:
        try:
            cls.from_dict(payload)
        except (TypeError, ValueError):
            return ValidatorCode.SCHEMA_INVALID
        return None

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "contract_name": self.contract_name,
            "contract_version": self.contract_version,
            "task_type": self.task_type,
            "task_id": self.task_id,
            "job_id": self.job_id,
            "run_id": self.run_id,
            "idempotency_key": self.idempotency_key,
            "input_artifact_ref": self.input_artifact_ref,
            "input_digest": self.input_digest,
            "evidence_refs": [item.to_dict() for item in self.evidence_refs],
            "source_version_ids": list(self.source_version_ids),
            "corpus_version": self.corpus_version,
            "policy_version": self.policy_version,
            "worker_config_ref": self.worker_config_ref,
            "access_partition_id": self.access_partition_id,
            "redaction_class": self.redaction_class,
            "requested_at": self.requested_at,
            "allowed_actions": list(self.allowed_actions),
            "limits": self.limits.to_dict(),
        }


@dataclass(frozen=True)
class IntelligenceProposal:
    proposal_kind: str
    proposal_key: str
    confidence: float
    evidence_ids: tuple[str, ...]
    payload: dict[str, object]

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> IntelligenceProposal:
        fields = frozenset(
            {
                "proposal_kind",
                "proposal_key",
                "confidence",
                "evidence_ids",
                "payload",
            }
        )
        _exact(payload, required=fields)
        confidence = payload["confidence"]
        if (
            isinstance(confidence, bool)
            or not isinstance(confidence, (int, float))
            or not 0 <= float(confidence) <= 1
        ):
            raise ValueError("confidence is invalid")
        evidence = payload["evidence_ids"]
        if (
            not isinstance(evidence, list)
            or not 1 <= len(evidence) <= 20
            or not all(isinstance(item, str) and item for item in evidence)
        ):
            raise ValueError("evidence_ids are invalid")
        proposal_payload = payload["payload"]
        if not isinstance(proposal_payload, Mapping):
            raise ValueError("payload must be an object")
        if len(_canonical_json(proposal_payload).encode()) > 16_384:
            raise ValueError("proposal payload exceeds limits")
        return cls(
            proposal_kind=_text(
                payload["proposal_kind"], "proposal_kind", 64
            ),
            proposal_key=_text(payload["proposal_key"], "proposal_key", 256),
            confidence=float(confidence),
            evidence_ids=tuple(evidence),
            payload=dict(proposal_payload),
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "proposal_kind": self.proposal_kind,
            "proposal_key": self.proposal_key,
            "confidence": self.confidence,
            "evidence_ids": list(self.evidence_ids),
            "payload": dict(self.payload),
        }


@dataclass(frozen=True)
class IntelligenceTaskResult:
    schema_version: int
    contract_name: str
    contract_version: int
    task_type: str
    task_id: str
    run_id: str | None
    input_digest: str
    policy_version: str
    action: str
    proposals: tuple[IntelligenceProposal, ...]
    uncertainty_codes: tuple[str, ...]
    rationale: str
    worker_ref: str
    output_digest: str

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> IntelligenceTaskResult:
        fields = frozenset(
            {
                "schema_version",
                "contract_name",
                "contract_version",
                "task_type",
                "task_id",
                "run_id",
                "input_digest",
                "policy_version",
                "action",
                "proposals",
                "uncertainty_codes",
                "rationale",
                "worker_ref",
                "output_digest",
            }
        )
        _exact(payload, required=fields)
        if payload["schema_version"] != 1:
            raise ValueError("schema_version must be 1")
        if payload["contract_name"] != "intelligence_task_result":
            raise ValueError("contract_name is invalid")
        if payload["contract_version"] != 1:
            raise ValueError("contract_version is unsupported")
        proposals = payload["proposals"]
        if not isinstance(proposals, list) or len(proposals) > 100:
            raise ValueError("proposals are invalid")
        parsed_proposals = tuple(
            IntelligenceProposal.from_dict(item)
            for item in proposals
            if isinstance(item, Mapping)
        )
        if len(parsed_proposals) != len(proposals):
            raise ValueError("proposals must be objects")
        uncertainty = payload["uncertainty_codes"]
        if (
            not isinstance(uncertainty, list)
            or len(uncertainty) > 20
            or not all(isinstance(item, str) and item for item in uncertainty)
        ):
            raise ValueError("uncertainty_codes are invalid")
        return cls(
            schema_version=1,
            contract_name="intelligence_task_result",
            contract_version=1,
            task_type=_text(payload["task_type"], "task_type", 64),
            task_id=_text(payload["task_id"], "task_id", 128),
            run_id=_optional_text(payload["run_id"], "run_id", 128),
            input_digest=_digest_text(payload["input_digest"], "input_digest"),
            policy_version=_text(
                payload["policy_version"], "policy_version", 128
            ),
            action=_text(payload["action"], "action", 64),
            proposals=parsed_proposals,
            uncertainty_codes=tuple(uncertainty),
            rationale=_text(payload["rationale"], "rationale", 4096),
            worker_ref=_text(payload["worker_ref"], "worker_ref", 256),
            output_digest=_digest_text(payload["output_digest"], "output_digest"),
        )

    @classmethod
    def from_worker_dict(
        cls, payload: Mapping[str, object]
    ) -> IntelligenceTaskResult:
        if "output_digest" in payload:
            raise ValueError("worker output must not assign output_digest")
        host_digest = _digest(dict(payload))
        return cls.from_dict({**dict(payload), "output_digest": host_digest})

    @property
    def computed_output_digest(self) -> str:
        payload = self.to_dict()
        payload.pop("output_digest")
        return _digest(payload)

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "contract_name": self.contract_name,
            "contract_version": self.contract_version,
            "task_type": self.task_type,
            "task_id": self.task_id,
            "run_id": self.run_id,
            "input_digest": self.input_digest,
            "policy_version": self.policy_version,
            "action": self.action,
            "proposals": [item.to_dict() for item in self.proposals],
            "uncertainty_codes": list(self.uncertainty_codes),
            "rationale": self.rationale,
            "worker_ref": self.worker_ref,
            "output_digest": self.output_digest,
        }


@dataclass(frozen=True)
class ValidationReceipt:
    accepted: bool
    validator_codes: tuple[str, ...]


@dataclass(frozen=True)
class ValidationReceiptEnvelope:
    schema_version: int
    validation_receipt_id: str
    task_id: str
    accepted: bool
    validator_codes: tuple[str, ...]
    input_digest: str
    output_digest: str
    policy_version: str
    validator_version: str
    created_at: str

    @classmethod
    def from_dict(
        cls, payload: Mapping[str, object]
    ) -> ValidationReceiptEnvelope:
        fields = frozenset(
            {
                "schema_version",
                "validation_receipt_id",
                "task_id",
                "accepted",
                "validator_codes",
                "input_digest",
                "output_digest",
                "policy_version",
                "validator_version",
                "created_at",
            }
        )
        _exact(payload, required=fields)
        codes = payload["validator_codes"]
        if (
            payload["schema_version"] != 1
            or not isinstance(payload["accepted"], bool)
            or not isinstance(codes, list)
            or not all(isinstance(item, str) and item for item in codes)
        ):
            raise ValueError("validation receipt is invalid")
        return cls(
            schema_version=1,
            validation_receipt_id=_text(
                payload["validation_receipt_id"], "validation_receipt_id", 128
            ),
            task_id=_text(payload["task_id"], "task_id", 128),
            accepted=payload["accepted"],
            validator_codes=tuple(codes),
            input_digest=_digest_text(payload["input_digest"], "input_digest"),
            output_digest=_digest_text(payload["output_digest"], "output_digest"),
            policy_version=_text(
                payload["policy_version"], "policy_version", 128
            ),
            validator_version=_text(
                payload["validator_version"], "validator_version", 128
            ),
            created_at=_time(payload["created_at"], "created_at"),
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "validation_receipt_id": self.validation_receipt_id,
            "task_id": self.task_id,
            "accepted": self.accepted,
            "validator_codes": list(self.validator_codes),
            "input_digest": self.input_digest,
            "output_digest": self.output_digest,
            "policy_version": self.policy_version,
            "validator_version": self.validator_version,
            "created_at": self.created_at,
        }


@dataclass(frozen=True)
class PromotionReceipt:
    schema_version: int
    promotion_receipt_id: str
    task_id: str
    validation_receipt_id: str
    accepted_ids: tuple[str, ...]
    rejection_codes: tuple[str, ...]
    prior_authority_version: str | None
    resulting_authority_version: str | None
    idempotency_outcome: str
    created_at: str

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> PromotionReceipt:
        fields = frozenset(
            {
                "schema_version",
                "promotion_receipt_id",
                "task_id",
                "validation_receipt_id",
                "accepted_ids",
                "rejection_codes",
                "prior_authority_version",
                "resulting_authority_version",
                "idempotency_outcome",
                "created_at",
            }
        )
        _exact(payload, required=fields)
        accepted = payload["accepted_ids"]
        rejected = payload["rejection_codes"]
        outcome = payload["idempotency_outcome"]
        if (
            payload["schema_version"] != 1
            or not isinstance(accepted, list)
            or not isinstance(rejected, list)
            or not all(isinstance(item, str) and item for item in [*accepted, *rejected])
            or outcome not in {"created", "reused", "no_op", "rejected"}
        ):
            raise ValueError("promotion receipt is invalid")
        return cls(
            schema_version=1,
            promotion_receipt_id=_text(
                payload["promotion_receipt_id"], "promotion_receipt_id", 128
            ),
            task_id=_text(payload["task_id"], "task_id", 128),
            validation_receipt_id=_text(
                payload["validation_receipt_id"], "validation_receipt_id", 128
            ),
            accepted_ids=tuple(accepted),
            rejection_codes=tuple(rejected),
            prior_authority_version=_optional_text(
                payload["prior_authority_version"],
                "prior_authority_version",
                128,
            ),
            resulting_authority_version=_optional_text(
                payload["resulting_authority_version"],
                "resulting_authority_version",
                128,
            ),
            idempotency_outcome=str(outcome),
            created_at=_time(payload["created_at"], "created_at"),
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "promotion_receipt_id": self.promotion_receipt_id,
            "task_id": self.task_id,
            "validation_receipt_id": self.validation_receipt_id,
            "accepted_ids": list(self.accepted_ids),
            "rejection_codes": list(self.rejection_codes),
            "prior_authority_version": self.prior_authority_version,
            "resulting_authority_version": self.resulting_authority_version,
            "idempotency_outcome": self.idempotency_outcome,
            "created_at": self.created_at,
        }


@dataclass(frozen=True)
class ReplayReceipt:
    schema_version: int
    replay_receipt_id: str
    task_id: str
    validation_receipt_id: str
    request_digest: str
    output_digest: str
    policy_version: str
    replay_state: str
    created_at: str

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> ReplayReceipt:
        fields = frozenset(
            {
                "schema_version",
                "replay_receipt_id",
                "task_id",
                "validation_receipt_id",
                "request_digest",
                "output_digest",
                "policy_version",
                "replay_state",
                "created_at",
            }
        )
        _exact(payload, required=fields)
        if (
            payload["schema_version"] != 1
            or payload["replay_state"] not in {"replayable", "not_replayable"}
        ):
            raise ValueError("replay receipt is invalid")
        return cls(
            schema_version=1,
            replay_receipt_id=_text(
                payload["replay_receipt_id"], "replay_receipt_id", 128
            ),
            task_id=_text(payload["task_id"], "task_id", 128),
            validation_receipt_id=_text(
                payload["validation_receipt_id"], "validation_receipt_id", 128
            ),
            request_digest=_digest_text(
                payload["request_digest"], "request_digest"
            ),
            output_digest=_digest_text(payload["output_digest"], "output_digest"),
            policy_version=_text(
                payload["policy_version"], "policy_version", 128
            ),
            replay_state=str(payload["replay_state"]),
            created_at=_time(payload["created_at"], "created_at"),
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "replay_receipt_id": self.replay_receipt_id,
            "task_id": self.task_id,
            "validation_receipt_id": self.validation_receipt_id,
            "request_digest": self.request_digest,
            "output_digest": self.output_digest,
            "policy_version": self.policy_version,
            "replay_state": self.replay_state,
            "created_at": self.created_at,
        }


@dataclass(frozen=True)
class CompletionReceipt:
    validation_receipt_id: str
    promotion_receipt_id: str
    replay_receipt_id: str
    accepted: bool
    validator_codes: tuple[str, ...]


class TaskContractRegistry:
    """Versioned contract registry and deterministic result validator."""

    def __init__(self) -> None:
        self._requests = {
            ("content_assessment", 1): IntelligenceTaskRequest,
            ("profile_change_assessment", 1): IntelligenceTaskRequest,
            ("identity_resolution", 1): IntelligenceTaskRequest,
            ("knowledge_extraction", 1): IntelligenceTaskRequest,
            ("retrieval_evaluation", 1): IntelligenceTaskRequest,
        }

    @classmethod
    def default(cls) -> TaskContractRegistry:
        return cls()

    def request(self, task_type: str, contract_version: int):
        try:
            return self._requests[(task_type, contract_version)]
        except KeyError as exc:
            raise KeyError(
                f"unsupported task contract: {task_type}@{contract_version}"
            ) from exc

    def validate_result(
        self,
        request: IntelligenceTaskRequest,
        result: IntelligenceTaskResult,
    ) -> ValidationReceipt:
        codes: list[str] = []
        if (
            result.task_type != request.task_type
            or result.task_id != request.task_id
            or result.run_id != request.run_id
        ):
            codes.append(ValidatorCode.CORRELATION_MISMATCH.value)
        if result.input_digest != request.input_digest:
            codes.append(ValidatorCode.INPUT_DIGEST_MISMATCH.value)
        if result.output_digest != result.computed_output_digest:
            codes.append(ValidatorCode.OUTPUT_DIGEST_MISMATCH.value)
        if result.policy_version != request.policy_version:
            codes.append(ValidatorCode.POLICY_VERSION_MISMATCH.value)
        if result.action not in request.allowed_actions:
            codes.append(ValidatorCode.ACTION_NOT_ALLOWED.value)
        supplied = {item.evidence_id for item in request.evidence_refs}
        cited = {
            evidence_id
            for proposal in result.proposals
            for evidence_id in proposal.evidence_ids
        }
        if cited - supplied:
            codes.append(ValidatorCode.UNKNOWN_EVIDENCE.value)
        proposal_keys = [item.proposal_key for item in result.proposals]
        if len(proposal_keys) != len(set(proposal_keys)):
            codes.append(ValidatorCode.DUPLICATE_PROPOSAL.value)
        if request.task_type == "content_assessment" and any(
            not self._valid_content_assessment_proposal(proposal)
            for proposal in result.proposals
        ):
            codes.append(ValidatorCode.SCHEMA_INVALID.value)
        if request.task_type == "profile_change_assessment" and any(
            not self._valid_profile_change_proposal(proposal)
            for proposal in result.proposals
        ):
            codes.append(ValidatorCode.SCHEMA_INVALID.value)
        if request.task_type == "identity_resolution" and any(
            not self._valid_identity_resolution_proposal(proposal)
            for proposal in result.proposals
        ):
            codes.append(ValidatorCode.SCHEMA_INVALID.value)
        if request.task_type == "knowledge_extraction" and any(
            not self._valid_knowledge_proposal(proposal)
            for proposal in result.proposals
        ):
            codes.append(ValidatorCode.SCHEMA_INVALID.value)
        if request.task_type == "retrieval_evaluation" and any(
            not self._valid_retrieval_evaluation_proposal(proposal)
            for proposal in result.proposals
        ):
            codes.append(ValidatorCode.SCHEMA_INVALID.value)
        return ValidationReceipt(not codes, tuple(codes))

    @staticmethod
    def _valid_content_assessment_proposal(
        proposal: IntelligenceProposal,
    ) -> bool:
        if proposal.proposal_kind != "content_signal":
            return False
        required = {
            "content_type",
            "novelty",
            "relevance",
            "follow_up_priority",
        }
        optional = {
            "entity_candidates",
            "claim_candidates",
            "event_candidates",
            "profile_change_candidates",
        }
        if set(proposal.payload) - required - optional or not required.issubset(
            proposal.payload
        ):
            return False
        enums = {
            "content_type": {
                "post",
                "article",
                "video",
                "comment",
                "profile",
                "other",
            },
            "novelty": {"duplicate", "known_update", "novel", "uncertain"},
            "relevance": {"low", "medium", "high", "uncertain"},
            "follow_up_priority": {"none", "normal", "high", "review"},
        }
        if any(proposal.payload[field] not in allowed for field, allowed in enums.items()):
            return False
        for field in optional:
            if field not in proposal.payload:
                continue
            values = proposal.payload[field]
            if (
                not isinstance(values, list)
                or len(values) > 20
                or not all(
                    isinstance(value, str) and 0 < len(value) <= 256
                    for value in values
                )
            ):
                return False
        return True

    @staticmethod
    def _valid_profile_change_proposal(proposal: IntelligenceProposal) -> bool:
        return (
            proposal.proposal_kind == "profile_change"
            and set(proposal.payload)
            == {
                "prior_snapshot_id",
                "current_snapshot_id",
                "section_kind",
                "change_state",
            }
            and proposal.payload["change_state"]
            in {"changed", "unchanged", "uncertain"}
            and all(
                isinstance(proposal.payload[field], str)
                and 0 < len(proposal.payload[field]) <= 256
                for field in (
                    "prior_snapshot_id",
                    "current_snapshot_id",
                    "section_kind",
                )
            )
        )

    @staticmethod
    def _valid_identity_resolution_proposal(
        proposal: IntelligenceProposal,
    ) -> bool:
        return (
            proposal.proposal_kind == "identity_resolution"
            and set(proposal.payload) == {"candidate_id", "outcome"}
            and proposal.payload["candidate_id"] == proposal.proposal_key
            and proposal.payload["outcome"]
            in {
                "same_entity",
                "different_entity",
                "ambiguous",
                "insufficient_evidence",
            }
        )

    @staticmethod
    def _valid_knowledge_proposal(proposal: IntelligenceProposal) -> bool:
        if proposal.proposal_kind == "temporal_claim":
            required = {
                "subject_entity_id",
                "predicate",
                "object",
                "valid_from",
                "valid_to",
            }
        elif proposal.proposal_kind == "temporal_event":
            required = {
                "event_type",
                "title",
                "event_time_from",
                "event_time_to",
                "entity_roles",
            }
        else:
            return False
        return set(proposal.payload) == required

    @staticmethod
    def _valid_retrieval_evaluation_proposal(
        proposal: IntelligenceProposal,
    ) -> bool:
        payload = proposal.payload
        recall = payload.get("evidence_recall")
        return (
            proposal.proposal_kind == "retrieval_evaluation"
            and set(payload)
            == {
                "case_id",
                "verdict",
                "evidence_recall",
                "temporal_correct",
                "access_safe",
            }
            and payload["case_id"] == proposal.proposal_key
            and payload["verdict"] in {"pass", "fail", "review"}
            and isinstance(recall, (int, float))
            and not isinstance(recall, bool)
            and 0 <= float(recall) <= 1
            and isinstance(payload["temporal_correct"], bool)
            and isinstance(payload["access_safe"], bool)
        )


class ContentAssessmentQueue:
    """Durable, idempotent queue populated only from immutable corpus evidence."""

    def __init__(self, db_path: Path, *, clock: Clock | None = None) -> None:
        self.db_path = Path(db_path)
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        store.init_db(self.db_path)

    def _now(self) -> datetime:
        value = self._clock()
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("clock must return a timezone-aware datetime")
        return value.astimezone(timezone.utc)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=5)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA busy_timeout=5000")
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    def enqueue(self, request: IntelligenceTaskRequest) -> IntelligenceTaskRequest:
        now = request.requested_at
        encoded = _canonical_json(request.to_dict())
        conn = self._connect()
        try:
            conn.execute(
                """INSERT OR IGNORE INTO service_intelligence_tasks
                   (task_id, task_type, contract_version, idempotency_key,
                    job_id, run_id, input_digest, access_partition_id,
                    request_json, request_digest, state, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'queued', ?, ?)""",
                (
                    request.task_id,
                    request.task_type,
                    request.contract_version,
                    request.idempotency_key,
                    request.job_id,
                    request.run_id,
                    request.input_digest,
                    request.access_partition_id,
                    encoded,
                    _digest(request.to_dict()),
                    now,
                    now,
                ),
            )
            row = conn.execute(
                """SELECT request_json FROM service_intelligence_tasks
                   WHERE idempotency_key = ?""",
                (request.idempotency_key,),
            ).fetchone()
            conn.commit()
        finally:
            conn.close()
        if row is None:
            raise RuntimeError("intelligence task was not persisted")
        return IntelligenceTaskRequest.from_dict(json.loads(row["request_json"]))

    def complete(
        self,
        task_id: str,
        result: IntelligenceTaskResult,
    ) -> CompletionReceipt:
        conn = self._connect()
        try:
            row = conn.execute(
                "SELECT * FROM service_intelligence_tasks WHERE task_id = ?",
                (task_id,),
            ).fetchone()
            if row is None:
                raise KeyError(f"intelligence task not found: {task_id}")
            request = IntelligenceTaskRequest.from_dict(
                json.loads(row["request_json"])
            )
            if result.task_id != task_id:
                validation = ValidationReceipt(
                    False,
                    (ValidatorCode.CORRELATION_MISMATCH.value,),
                )
            else:
                validation = TaskContractRegistry.default().validate_result(
                    request, result
                )
            validation_id = _stable_id(
                "validation-receipt",
                {
                    "task_id": task_id,
                    "output_digest": result.output_digest,
                    "validator_version": "intelligence-validator-v1",
                },
            )
            promotion_id = _stable_id(
                "promotion-receipt",
                {
                    "task_id": task_id,
                    "validation_receipt_id": validation_id,
                },
            )
            replay_id = _stable_id(
                "replay-receipt",
                {
                    "task_id": task_id,
                    "validation_receipt_id": validation_id,
                },
            )
            existing = conn.execute(
                """SELECT validation_receipt_id, accepted,
                          validator_codes_json
                   FROM service_intelligence_validation_receipts
                   WHERE validation_receipt_id = ?""",
                (validation_id,),
            ).fetchone()
            if existing is not None:
                return CompletionReceipt(
                    validation_receipt_id=existing["validation_receipt_id"],
                    promotion_receipt_id=promotion_id,
                    replay_receipt_id=replay_id,
                    accepted=bool(existing["accepted"]),
                    validator_codes=tuple(
                        json.loads(existing["validator_codes_json"])
                    ),
                )
            now = _timestamp(self._now())
            conn.execute("BEGIN IMMEDIATE")
            conn.execute(
                """UPDATE service_intelligence_tasks
                   SET state = ?, result_json = ?, output_digest = ?,
                       error_code = ?, updated_at = ?
                   WHERE task_id = ?""",
                (
                    "completed" if validation.accepted else "rejected",
                    _canonical_json(result.to_dict()),
                    result.output_digest,
                    (
                        validation.validator_codes[0]
                        if validation.validator_codes
                        else None
                    ),
                    now,
                    task_id,
                ),
            )
            conn.execute(
                """INSERT INTO service_intelligence_validation_receipts
                   (validation_receipt_id, task_id, accepted,
                    validator_codes_json, input_digest, output_digest,
                    policy_version, validator_version, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, 'intelligence-validator-v1', ?)""",
                (
                    validation_id,
                    task_id,
                    int(validation.accepted),
                    _canonical_json(list(validation.validator_codes)),
                    request.input_digest,
                    result.output_digest,
                    request.policy_version,
                    now,
                ),
            )
            accepted_ids = (
                [proposal.proposal_key for proposal in result.proposals]
                if validation.accepted
                else []
            )
            conn.execute(
                """INSERT INTO service_intelligence_promotion_receipts
                   (promotion_receipt_id, task_id, validation_receipt_id,
                    accepted_ids_json, rejection_codes_json,
                    prior_authority_version, resulting_authority_version,
                    idempotency_outcome, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    promotion_id,
                    task_id,
                    validation_id,
                    _canonical_json(accepted_ids),
                    _canonical_json(list(validation.validator_codes)),
                    request.corpus_version,
                    request.corpus_version,
                    "created" if validation.accepted else "rejected",
                    now,
                ),
            )
            conn.execute(
                """INSERT INTO service_intelligence_replay_receipts
                   (replay_receipt_id, task_id, validation_receipt_id,
                    request_digest, output_digest, policy_version,
                    replay_state, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, 'replayable', ?)""",
                (
                    replay_id,
                    task_id,
                    validation_id,
                    row["request_digest"],
                    result.output_digest,
                    request.policy_version,
                    now,
                ),
            )
            conn.execute(
                """UPDATE collection_assessment_batches
                   SET state = ?, error_code = ?, updated_at = ?
                   WHERE task_id = ?""",
                (
                    "completed" if validation.accepted else "rejected",
                    (
                        validation.validator_codes[0]
                        if validation.validator_codes
                        else None
                    ),
                    now,
                    task_id,
                ),
            )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
        return CompletionReceipt(
            validation_receipt_id=validation_id,
            promotion_receipt_id=promotion_id,
            replay_receipt_id=replay_id,
            accepted=validation.accepted,
            validator_codes=validation.validator_codes,
        )

    def claim_next(
        self,
        *,
        worker_id: str,
        lease_seconds: int = 120,
    ) -> IntelligenceTaskRequest | None:
        if not worker_id.strip():
            raise ValueError("worker_id must be non-empty")
        if not 1 <= lease_seconds <= 3600:
            raise ValueError("lease_seconds must be between 1 and 3600")
        now_dt = self._now()
        now = _timestamp(now_dt)
        expires = _timestamp(now_dt + timedelta(seconds=lease_seconds))
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            expired = conn.execute(
                """SELECT task_id, request_json, attempt_count
                   FROM service_intelligence_tasks
                   WHERE state = 'running' AND lease_expires_at <= ?""",
                (now,),
            ).fetchall()
            for row in expired:
                request = IntelligenceTaskRequest.from_dict(
                    json.loads(row["request_json"])
                )
                exhausted = int(row["attempt_count"]) >= request.limits.max_calls
                conn.execute(
                    """UPDATE service_intelligence_tasks
                       SET state = ?, lease_owner = NULL, lease_expires_at = NULL,
                           error_code = ?, updated_at = ?
                       WHERE task_id = ?""",
                    (
                        "failed" if exhausted else "queued",
                        "call_bound_exhausted" if exhausted else "lease_expired",
                        now,
                        row["task_id"],
                    ),
                )
            row = conn.execute(
                """SELECT * FROM service_intelligence_tasks
                   WHERE state = 'queued'
                   ORDER BY created_at, task_id
                   LIMIT 1"""
            ).fetchone()
            if row is None:
                conn.commit()
                return None
            request = IntelligenceTaskRequest.from_dict(json.loads(row["request_json"]))
            if int(row["attempt_count"]) >= request.limits.max_calls:
                conn.execute(
                    """UPDATE service_intelligence_tasks
                       SET state = 'failed', error_code = 'call_bound_exhausted',
                           updated_at = ?
                       WHERE task_id = ?""",
                    (now, row["task_id"]),
                )
                conn.commit()
                return None
            generation = int(row["lease_generation"]) + 1
            conn.execute(
                """UPDATE service_intelligence_tasks
                   SET state = 'running', attempt_count = attempt_count + 1,
                       lease_owner = ?, lease_generation = ?,
                       lease_expires_at = ?, error_code = NULL, updated_at = ?
                   WHERE task_id = ? AND state = 'queued'""",
                (worker_id, generation, expires, now, row["task_id"]),
            )
            conn.commit()
            return request
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def materialize_input(
        self,
        request: IntelligenceTaskRequest,
    ) -> dict[str, object]:
        conn = self._connect()
        try:
            materialized: list[dict[str, object]] = []
            for ref in request.evidence_refs:
                row = conn.execute(
                    """SELECT e.evidence_id, e.version_id, e.chunk_id,
                              e.span_start, e.span_end, e.span_digest,
                              e.access_partition_id, c.text
                       FROM evidence_spans AS e
                       JOIN document_version_chunks AS c
                         ON c.chunk_id = e.chunk_id
                        AND c.version_id = e.version_id
                        AND c.access_partition_id = e.access_partition_id
                       WHERE e.evidence_id = ?""",
                    (ref.evidence_id,),
                ).fetchone()
                if row is None:
                    raise RuntimeError("assessment evidence is unavailable")
                stored_digest = str(row["span_digest"])
                if not stored_digest.startswith("sha256:"):
                    stored_digest = f"sha256:{stored_digest}"
                if (
                    row["version_id"] != ref.version_id
                    or row["chunk_id"] != ref.chunk_id
                    or row["access_partition_id"] != request.access_partition_id
                    or stored_digest != ref.content_digest
                ):
                    raise RuntimeError("assessment evidence failed closure")
                materialized.append(
                    {
                        "evidence_id": ref.evidence_id,
                        "version_id": ref.version_id,
                        "observed_at": ref.observed_at,
                        "text": row["text"][row["span_start"] : row["span_end"]],
                    }
                )
        finally:
            conn.close()
        payload = {
            "task_id": request.task_id,
            "policy_version": request.policy_version,
            "evidence": materialized,
        }
        if len(_canonical_json(payload).encode()) > request.limits.max_bytes:
            raise RuntimeError("assessment input exceeds task byte bound")
        return payload

    def fail(self, task_id: str, *, error_code: str, retryable: bool) -> None:
        now = _timestamp(self._now())
        conn = self._connect()
        try:
            row = conn.execute(
                """SELECT request_json, attempt_count
                   FROM service_intelligence_tasks WHERE task_id = ?""",
                (task_id,),
            ).fetchone()
            if row is None:
                raise KeyError(f"intelligence task not found: {task_id}")
            request = IntelligenceTaskRequest.from_dict(
                json.loads(row["request_json"])
            )
            state = (
                "queued"
                if retryable and int(row["attempt_count"]) < request.limits.max_calls
                else "failed"
            )
            conn.execute(
                """UPDATE service_intelligence_tasks
                   SET state = ?, lease_owner = NULL, lease_expires_at = NULL,
                       error_code = ?, updated_at = ?
                   WHERE task_id = ?""",
                (state, error_code, now, task_id),
            )
            conn.execute(
                """UPDATE collection_assessment_batches
                   SET state = ?, error_code = ?, updated_at = ?
                   WHERE task_id = ?""",
                (state, error_code, now, task_id),
            )
            conn.commit()
        finally:
            conn.close()

    def enqueue_for_acquisition(
        self,
        *,
        job_id: str,
        acquisition_id: str,
        item_limit: int = 20,
        max_cost_cents: int = 5,
    ) -> IntelligenceTaskRequest | None:
        conn = self._connect()
        try:
            run = conn.execute(
                """SELECT r.collection_run_id, r.collection_spec_id,
                          r.access_partition_id, sr.spec_json
                   FROM collection_runs AS r
                   JOIN collection_spec_revisions AS sr
                     ON sr.collection_spec_id = r.collection_spec_id
                    AND sr.spec_version = r.spec_version
                   WHERE r.job_id = ?
                   ORDER BY r.scheduled_for, r.collection_run_id
                   LIMIT 1""",
                (job_id,),
            ).fetchone()
            if run is None:
                return None
            spec = json.loads(run["spec_json"])
            if not spec.get("assessment_enabled", False):
                return None
            evidence_rows = conn.execute(
                """SELECT e.evidence_id, e.version_id, e.chunk_id,
                          e.span_digest, v.observed_at, v.valid_from, v.valid_to,
                          e.access_partition_id
                   FROM document_version_sightings AS s
                   JOIN evidence_spans AS e ON e.version_id = s.version_id
                   JOIN document_versions AS v ON v.version_id = e.version_id
                   WHERE s.acquisition_id = ?
                   ORDER BY e.version_id, e.chunk_id, e.span_start
                   LIMIT ?""",
                (acquisition_id, min(item_limit, 100)),
            ).fetchall()
            if not evidence_rows:
                return None
            index = conn.execute(
                "SELECT index_version FROM service_index_head WHERE singleton_id = 1"
            ).fetchone()
        finally:
            conn.close()
        evidence = [
            {
                "evidence_id": row["evidence_id"],
                "version_id": row["version_id"],
                "chunk_id": row["chunk_id"],
                "content_digest": (
                    row["span_digest"]
                    if str(row["span_digest"]).startswith("sha256:")
                    else f"sha256:{row['span_digest']}"
                ),
                "observed_at": row["observed_at"],
                "valid_from": row["valid_from"],
                "valid_to": row["valid_to"],
                "access_partition_id": row["access_partition_id"],
            }
            for row in evidence_rows
        ]
        version_ids = sorted({str(item["version_id"]) for item in evidence})
        input_digest = _digest(
            {
                "evidence_refs": evidence,
                "source_version_ids": version_ids,
                "policy_version": "content-assessment-v1",
            }
        )
        idempotency_key = f"content-assessment:v1:{input_digest.removeprefix('sha256:')}"
        task_id = _stable_id("intelligence-task", idempotency_key)
        requested_at = _timestamp(self._now())
        request = IntelligenceTaskRequest.from_dict(
            {
                "schema_version": 1,
                "contract_name": "intelligence_task_request",
                "contract_version": 1,
                "task_type": "content_assessment",
                "task_id": task_id,
                "job_id": job_id,
                "run_id": run["collection_run_id"],
                "idempotency_key": idempotency_key,
                "input_artifact_ref": f"acquisition:{acquisition_id}",
                "input_digest": input_digest,
                "evidence_refs": evidence,
                "source_version_ids": version_ids,
                "corpus_version": index["index_version"] if index else None,
                "policy_version": "content-assessment-v1",
                "worker_config_ref": "app-intelligence:content-assessment-v1",
                "access_partition_id": run["access_partition_id"],
                "redaction_class": spec["redaction_class"],
                "requested_at": requested_at,
                "allowed_actions": ["record_assessment"],
                "limits": {
                    "max_items": min(len(evidence), 100),
                    "max_bytes": 65_536,
                    "max_calls": 1,
                    "max_cost_cents": max_cost_cents,
                    "wall_timeout_seconds": 60,
                },
            }
        )
        return self.enqueue(request)


class ContentAssessmentWorker:
    """One bounded stochastic leaf behind deterministic task and receipt control."""

    def __init__(
        self,
        queue: ContentAssessmentQueue,
        client: StructuredAssessmentClient,
        *,
        cwd: Path,
        model: str | None = None,
    ) -> None:
        self.queue = queue
        self.client = client
        self.cwd = Path(cwd)
        self.model = model

    def run_once(self, *, worker_id: str) -> CompletionReceipt | None:
        request = self.queue.claim_next(worker_id=worker_id)
        if request is None:
            return None
        try:
            input_payload = self.queue.materialize_input(request)
            turn = self.client.structured_turn(
                prompt=(
                    "Assess only the supplied immutable evidence. Return one "
                    "schema-valid content assessment. Do not browse, mutate "
                    "state, or cite evidence not supplied.\nNormalized input:\n"
                    + _canonical_json(input_payload)
                ),
                output_schema=CONTENT_ASSESSMENT_OUTPUT_SCHEMA,
                cwd=self.cwd,
                model=self.model,
            )
            worker_output = dict(turn.output)
            result = IntelligenceTaskResult.from_worker_dict(
                {
                    "schema_version": 1,
                    "contract_name": "intelligence_task_result",
                    "contract_version": request.contract_version,
                    "task_type": request.task_type,
                    "task_id": request.task_id,
                    "run_id": request.run_id,
                    "input_digest": request.input_digest,
                    "policy_version": request.policy_version,
                    "action": worker_output.get("action"),
                    "proposals": worker_output.get("proposals"),
                    "uncertainty_codes": worker_output.get("uncertainty_codes"),
                    "rationale": worker_output.get("rationale"),
                    "worker_ref": turn.model_ref,
                }
            )
            return self.queue.complete(request.task_id, result)
        except Exception as exc:
            self.queue.fail(
                request.task_id,
                error_code=type(exc).__name__.casefold(),
                retryable=False,
            )
            raise
