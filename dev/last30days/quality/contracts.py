"""Strict versioned contracts for the Packet 1 quality tracer."""

from __future__ import annotations

import hashlib
import json
import math
import re
from dataclasses import dataclass
from datetime import date
from typing import Mapping, Sequence


AXES = ("acquisition", "corpus", "retrieval", "grounding")
STATES = ("passed", "failed", "not_measurable", "invalid", "incomplete")
_ID = re.compile(r"^[a-z][a-z0-9._:-]{0,127}$")
_REF = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,255}$")


class ContractValidationError(ValueError):
    """Raised when a versioned quality contract fails closed."""


def canonical_json(value: object) -> str:
    """Return the sole semantic JSON encoding used by Packet 1."""

    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def canonical_digest(value: object) -> str:
    """Return a tagged SHA-256 digest of canonical JSON."""

    return "sha256:" + hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _strict_fields(
    payload: Mapping[str, object],
    *,
    required: set[str],
    optional: set[str] | None = None,
    context: str,
) -> None:
    optional = optional or set()
    keys = set(payload)
    unknown = keys - required - optional
    missing = required - keys
    if unknown:
        raise ContractValidationError(
            f"{context} has unknown fields: {', '.join(sorted(unknown))}"
        )
    if missing:
        raise ContractValidationError(
            f"{context} is missing fields: {', '.join(sorted(missing))}"
        )


def _mapping(value: object, context: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping) or any(not isinstance(key, str) for key in value):
        raise ContractValidationError(f"{context} must be an object")
    return value


def _sequence(value: object, context: str) -> Sequence[object]:
    if not isinstance(value, list):
        raise ContractValidationError(f"{context} must be an array")
    return value


def _string(value: object, context: str, *, identifier: bool = False) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise ContractValidationError(f"{context} must be a non-empty string")
    if identifier and not _ID.fullmatch(value):
        raise ContractValidationError(f"{context} must be a stable identifier")
    return value


def _integer(value: object, context: str, *, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ContractValidationError(f"{context} must be an integer >= {minimum}")
    return value


def _number(value: object, context: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ContractValidationError(f"{context} must be numeric")
    result = float(value)
    if not math.isfinite(result):
        raise ContractValidationError(f"{context} must be finite")
    return result


def _date(value: object, context: str) -> str:
    text = _string(value, context)
    try:
        date.fromisoformat(text)
    except ValueError as exc:
        raise ContractValidationError(f"{context} must be an ISO date") from exc
    return text


def _unique_strings(
    value: object,
    context: str,
    *,
    allowed: Sequence[str] | None = None,
    reference: bool = False,
) -> tuple[str, ...]:
    items = _sequence(value, context)
    result: list[str] = []
    for index, item in enumerate(items):
        text = _string(item, f"{context}[{index}]")
        if allowed is not None and text not in allowed:
            raise ContractValidationError(f"{context}[{index}] is unsupported")
        if reference and not _REF.fullmatch(text):
            raise ContractValidationError(f"{context}[{index}] is not a stable ref")
        result.append(text)
    if len(result) != len(set(result)):
        raise ContractValidationError(f"{context} must not contain duplicates")
    if result != sorted(result):
        raise ContractValidationError(f"{context} must be sorted")
    return tuple(result)


@dataclass(frozen=True)
class MetricInputV1:
    name: str
    numerator: int
    denominator: int | None
    excluded: int

    @classmethod
    def from_dict(cls, raw: object, context: str) -> MetricInputV1:
        payload = _mapping(raw, context)
        _strict_fields(
            payload,
            required={"name", "numerator", "denominator", "excluded"},
            context=context,
        )
        denominator_raw = payload["denominator"]
        denominator = (
            None
            if denominator_raw is None
            else _integer(denominator_raw, f"{context}.denominator", minimum=1)
        )
        numerator = _integer(payload["numerator"], f"{context}.numerator")
        return cls(
            name=_string(payload["name"], f"{context}.name", identifier=True),
            numerator=numerator,
            denominator=denominator,
            excluded=_integer(payload["excluded"], f"{context}.excluded"),
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "numerator": self.numerator,
            "denominator": self.denominator,
            "excluded": self.excluded,
        }


@dataclass(frozen=True)
class FakeOutcomeV1:
    state: str
    metrics: tuple[MetricInputV1, ...]
    baseline_metrics: tuple[MetricInputV1, ...] | None
    failure_codes: tuple[str, ...]
    observed_refs: tuple[str, ...]

    @classmethod
    def from_dict(cls, raw: object, context: str) -> FakeOutcomeV1:
        payload = _mapping(raw, context)
        _strict_fields(
            payload,
            required={"state", "metrics", "failure_codes", "observed_refs"},
            optional={"baseline_metrics"},
            context=context,
        )
        state = _string(payload["state"], f"{context}.state")
        if state not in STATES:
            raise ContractValidationError(f"{context}.state is unsupported")
        metrics = tuple(
            MetricInputV1.from_dict(metric, f"{context}.metrics[{index}]")
            for index, metric in enumerate(_sequence(payload["metrics"], f"{context}.metrics"))
        )
        if not metrics:
            raise ContractValidationError(f"{context}.metrics must not be empty")
        names = [metric.name for metric in metrics]
        if names != sorted(names) or len(names) != len(set(names)):
            raise ContractValidationError(f"{context}.metrics must have sorted unique names")
        if state == "not_measurable" and all(
            metric.denominator is not None for metric in metrics
        ):
            raise ContractValidationError(
                f"{context}.not_measurable requires an unknown denominator"
            )
        baseline_raw = payload.get("baseline_metrics")
        baseline_metrics = (
            None
            if baseline_raw is None
            else tuple(
                MetricInputV1.from_dict(metric, f"{context}.baseline_metrics[{index}]")
                for index, metric in enumerate(
                    _sequence(baseline_raw, f"{context}.baseline_metrics")
                )
            )
        )
        if baseline_metrics is not None:
            baseline_names = [metric.name for metric in baseline_metrics]
            if (
                baseline_names != names
                or baseline_names != sorted(baseline_names)
                or len(baseline_names) != len(set(baseline_names))
            ):
                raise ContractValidationError(
                    f"{context}.baseline_metrics must match candidate metric names"
                )
        if state == "passed" and payload["failure_codes"]:
            raise ContractValidationError(f"{context}.passed cannot contain failure codes")
        if state != "passed" and not payload["failure_codes"]:
            raise ContractValidationError(f"{context}.{state} requires a failure code")
        return cls(
            state=state,
            metrics=metrics,
            baseline_metrics=baseline_metrics,
            failure_codes=_unique_strings(payload["failure_codes"], f"{context}.failure_codes"),
            observed_refs=_unique_strings(
                payload["observed_refs"], f"{context}.observed_refs", reference=True
            ),
        )

    def to_dict(self) -> dict[str, object]:
        result: dict[str, object] = {
            "state": self.state,
            "metrics": [metric.to_dict() for metric in self.metrics],
            "failure_codes": list(self.failure_codes),
            "observed_refs": list(self.observed_refs),
        }
        if self.baseline_metrics is not None:
            result["baseline_metrics"] = [
                metric.to_dict() for metric in self.baseline_metrics
            ]
        return result


@dataclass(frozen=True)
class EvaluationCaseV1:
    case_id: str
    axis: str
    tags: tuple[str, ...]
    outcome: FakeOutcomeV1

    @classmethod
    def from_dict(cls, raw: object, context: str) -> EvaluationCaseV1:
        payload = _mapping(raw, context)
        _strict_fields(
            payload,
            required={"case_id", "axis", "tags", "outcome"},
            context=context,
        )
        axis = _string(payload["axis"], f"{context}.axis")
        if axis not in AXES:
            raise ContractValidationError(f"{context}.axis is unsupported")
        return cls(
            case_id=_string(payload["case_id"], f"{context}.case_id", identifier=True),
            axis=axis,
            tags=_unique_strings(payload["tags"], f"{context}.tags"),
            outcome=FakeOutcomeV1.from_dict(payload["outcome"], f"{context}.outcome"),
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "case_id": self.case_id,
            "axis": self.axis,
            "tags": list(self.tags),
            "outcome": self.outcome.to_dict(),
        }


@dataclass(frozen=True)
class SourceLicenseV1:
    source: str
    status: str
    license: str

    @classmethod
    def from_dict(cls, raw: object, context: str) -> SourceLicenseV1:
        payload = _mapping(raw, context)
        _strict_fields(
            payload,
            required={"source", "status", "license"},
            context=context,
        )
        status = _string(payload["status"], f"{context}.status")
        if status not in {"synthetic", "redistribution_safe"}:
            raise ContractValidationError(f"{context}.status is unsupported")
        return cls(
            source=_string(payload["source"], f"{context}.source", identifier=True),
            status=status,
            license=_string(payload["license"], f"{context}.license"),
        )

    def to_dict(self) -> dict[str, object]:
        return {"source": self.source, "status": self.status, "license": self.license}


@dataclass(frozen=True)
class QualityEvaluationSetV1:
    schema_version: str
    evaluation_set_id: str
    version: int
    description: str
    source_status: str
    source_licenses: tuple[SourceLicenseV1, ...]
    created_date: str
    reviewed_date: str
    cases: tuple[EvaluationCaseV1, ...]
    digest: str

    @classmethod
    def from_dict(cls, raw: object) -> QualityEvaluationSetV1:
        payload = _mapping(raw, "evaluation_set")
        required = {
            "schema_version",
            "evaluation_set_id",
            "version",
            "description",
            "source_status",
            "source_licenses",
            "created_date",
            "reviewed_date",
            "cases",
        }
        _strict_fields(payload, required=required, context="evaluation_set")
        if payload["schema_version"] != "quality_evaluation_set.v1":
            raise ContractValidationError("evaluation_set.schema_version is unsupported")
        if payload["source_status"] not in {"synthetic", "redistribution_safe"}:
            raise ContractValidationError("evaluation_set.source_status is unsupported")
        cases = tuple(
            EvaluationCaseV1.from_dict(case, f"evaluation_set.cases[{index}]")
            for index, case in enumerate(_sequence(payload["cases"], "evaluation_set.cases"))
        )
        if not cases:
            raise ContractValidationError("evaluation_set.cases must not be empty")
        case_ids = [case.case_id for case in cases]
        if case_ids != sorted(case_ids) or len(case_ids) != len(set(case_ids)):
            raise ContractValidationError("evaluation_set cases must have sorted unique ids")
        source_licenses = tuple(
            SourceLicenseV1.from_dict(item, f"evaluation_set.source_licenses[{index}]")
            for index, item in enumerate(
                _sequence(payload["source_licenses"], "evaluation_set.source_licenses")
            )
        )
        source_ids = [item.source for item in source_licenses]
        if (
            not source_ids
            or source_ids != sorted(source_ids)
            or len(source_ids) != len(set(source_ids))
        ):
            raise ContractValidationError(
                "evaluation_set source licenses must have sorted unique sources"
            )
        return cls(
            schema_version="quality_evaluation_set.v1",
            evaluation_set_id=_string(
                payload["evaluation_set_id"],
                "evaluation_set.evaluation_set_id",
                identifier=True,
            ),
            version=_integer(payload["version"], "evaluation_set.version", minimum=1),
            description=_string(payload["description"], "evaluation_set.description"),
            source_status=str(payload["source_status"]),
            source_licenses=source_licenses,
            created_date=_date(payload["created_date"], "evaluation_set.created_date"),
            reviewed_date=_date(payload["reviewed_date"], "evaluation_set.reviewed_date"),
            cases=cases,
            digest=canonical_digest(dict(payload)),
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "evaluation_set_id": self.evaluation_set_id,
            "version": self.version,
            "description": self.description,
            "source_status": self.source_status,
            "source_licenses": [item.to_dict() for item in self.source_licenses],
            "created_date": self.created_date,
            "reviewed_date": self.reviewed_date,
            "cases": [case.to_dict() for case in self.cases],
        }


@dataclass(frozen=True)
class ThresholdRuleV1:
    rule_id: str
    axis: str
    metric: str
    scope: str
    comparator: str
    threshold: float
    minimum_denominator: int
    severity: str
    missing_data: str

    @classmethod
    def from_dict(cls, raw: object, context: str) -> ThresholdRuleV1:
        payload = _mapping(raw, context)
        _strict_fields(
            payload,
            required={
                "rule_id",
                "axis",
                "metric",
                "scope",
                "comparator",
                "threshold",
                "minimum_denominator",
                "severity",
                "missing_data",
            },
            context=context,
        )
        axis = _string(payload["axis"], f"{context}.axis")
        if axis not in AXES:
            raise ContractValidationError(f"{context}.axis is unsupported")
        comparator = _string(payload["comparator"], f"{context}.comparator")
        if comparator not in {"gte", "lte"}:
            raise ContractValidationError(f"{context}.comparator is unsupported")
        severity = _string(payload["severity"], f"{context}.severity")
        if severity not in {"blocking", "warning"}:
            raise ContractValidationError(f"{context}.severity is unsupported")
        missing_data = _string(payload["missing_data"], f"{context}.missing_data")
        if missing_data not in {"fail", "not_measurable", "warn"}:
            raise ContractValidationError(f"{context}.missing_data is unsupported")
        if payload["scope"] != "global":
            raise ContractValidationError(f"{context}.scope is unsupported")
        return cls(
            rule_id=_string(payload["rule_id"], f"{context}.rule_id", identifier=True),
            axis=axis,
            metric=_string(payload["metric"], f"{context}.metric", identifier=True),
            scope="global",
            comparator=comparator,
            threshold=_number(payload["threshold"], f"{context}.threshold"),
            minimum_denominator=_integer(
                payload["minimum_denominator"],
                f"{context}.minimum_denominator",
                minimum=1,
            ),
            severity=severity,
            missing_data=missing_data,
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "rule_id": self.rule_id,
            "axis": self.axis,
            "metric": self.metric,
            "scope": self.scope,
            "comparator": self.comparator,
            "threshold": self.threshold,
            "minimum_denominator": self.minimum_denominator,
            "severity": self.severity,
            "missing_data": self.missing_data,
        }


@dataclass(frozen=True)
class QualityThresholdPolicyV1:
    schema_version: str
    policy_id: str
    version: int
    rules: tuple[ThresholdRuleV1, ...]
    digest: str

    @classmethod
    def from_dict(cls, raw: object) -> QualityThresholdPolicyV1:
        payload = _mapping(raw, "threshold_policy")
        _strict_fields(
            payload,
            required={"schema_version", "policy_id", "version", "rules"},
            context="threshold_policy",
        )
        if payload["schema_version"] != "quality_threshold_policy.v1":
            raise ContractValidationError("threshold_policy.schema_version is unsupported")
        rules = tuple(
            ThresholdRuleV1.from_dict(rule, f"threshold_policy.rules[{index}]")
            for index, rule in enumerate(_sequence(payload["rules"], "threshold_policy.rules"))
        )
        if not rules:
            raise ContractValidationError("threshold_policy.rules must not be empty")
        rule_ids = [rule.rule_id for rule in rules]
        if rule_ids != sorted(rule_ids) or len(rule_ids) != len(set(rule_ids)):
            raise ContractValidationError("threshold_policy rules must have sorted unique ids")
        pairs = [(rule.axis, rule.metric) for rule in rules]
        if len(pairs) != len(set(pairs)):
            raise ContractValidationError("threshold_policy has duplicate axis metrics")
        return cls(
            schema_version="quality_threshold_policy.v1",
            policy_id=_string(payload["policy_id"], "threshold_policy.policy_id", identifier=True),
            version=_integer(payload["version"], "threshold_policy.version", minimum=1),
            rules=rules,
            digest=canonical_digest(dict(payload)),
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "policy_id": self.policy_id,
            "version": self.version,
            "rules": [rule.to_dict() for rule in self.rules],
        }


def _sha256(value: object, context: str) -> str:
    text = _string(value, context)
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", text):
        raise ContractValidationError(f"{context} must be a tagged SHA-256 digest")
    return text


@dataclass(frozen=True)
class ContractRefV1:
    id: str
    digest: str

    @classmethod
    def from_dict(cls, raw: object, context: str) -> ContractRefV1:
        payload = _mapping(raw, context)
        _strict_fields(payload, required={"id", "digest"}, context=context)
        return cls(
            id=_string(payload["id"], f"{context}.id", identifier=True),
            digest=_sha256(payload["digest"], f"{context}.digest"),
        )

    def to_dict(self) -> dict[str, object]:
        return {"id": self.id, "digest": self.digest}


@dataclass(frozen=True)
class EvidenceHeadV1:
    repository_commit: str
    service_contract_version: str
    database_schema_version: int
    index_head: str
    embedding_config_digest: str
    ranking_config_digest: str

    @classmethod
    def from_dict(cls, raw: object, context: str) -> EvidenceHeadV1:
        payload = _mapping(raw, context)
        _strict_fields(
            payload,
            required={
                "repository_commit",
                "service_contract_version",
                "database_schema_version",
                "index_head",
                "embedding_config_digest",
                "ranking_config_digest",
            },
            context=context,
        )
        commit = _string(payload["repository_commit"], f"{context}.repository_commit")
        if not re.fullmatch(r"[0-9a-f]{40}", commit):
            raise ContractValidationError(f"{context}.repository_commit must be a full Git SHA")
        return cls(
            repository_commit=commit,
            service_contract_version=_string(
                payload["service_contract_version"], f"{context}.service_contract_version"
            ),
            database_schema_version=_integer(
                payload["database_schema_version"], f"{context}.database_schema_version"
            ),
            index_head=_string(payload["index_head"], f"{context}.index_head"),
            embedding_config_digest=_sha256(
                payload["embedding_config_digest"], f"{context}.embedding_config_digest"
            ),
            ranking_config_digest=_sha256(
                payload["ranking_config_digest"], f"{context}.ranking_config_digest"
            ),
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "repository_commit": self.repository_commit,
            "service_contract_version": self.service_contract_version,
            "database_schema_version": self.database_schema_version,
            "index_head": self.index_head,
            "embedding_config_digest": self.embedding_config_digest,
            "ranking_config_digest": self.ranking_config_digest,
        }


@dataclass(frozen=True)
class RunLimitsV1:
    max_cases: int
    max_wall_seconds: int
    max_output_bytes: int
    per_case_limit: int

    @classmethod
    def from_dict(cls, raw: object, context: str = "request.limits") -> RunLimitsV1:
        payload = _mapping(raw, context)
        _strict_fields(
            payload,
            required={"max_cases", "max_wall_seconds", "max_output_bytes", "per_case_limit"},
            context=context,
        )
        return cls(
            max_cases=_integer(payload["max_cases"], f"{context}.max_cases", minimum=1),
            max_wall_seconds=_integer(
                payload["max_wall_seconds"], f"{context}.max_wall_seconds", minimum=1
            ),
            max_output_bytes=_integer(
                payload["max_output_bytes"], f"{context}.max_output_bytes", minimum=1024
            ),
            per_case_limit=_integer(
                payload["per_case_limit"], f"{context}.per_case_limit", minimum=1
            ),
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "max_cases": self.max_cases,
            "max_wall_seconds": self.max_wall_seconds,
            "max_output_bytes": self.max_output_bytes,
            "per_case_limit": self.per_case_limit,
        }


@dataclass(frozen=True)
class QualityEvaluationRequestV1:
    schema_version: str
    run_id: str
    evaluation_set: ContractRefV1
    threshold_policy: ContractRefV1
    candidate: EvidenceHeadV1
    baseline: EvidenceHeadV1 | None
    evaluator_version: str
    axes: tuple[str, ...]
    case_ids: tuple[str, ...]
    mode: str
    environment: str
    limits: RunLimitsV1
    digest: str

    @classmethod
    def from_dict(cls, raw: object) -> QualityEvaluationRequestV1:
        payload = _mapping(raw, "request")
        _strict_fields(
            payload,
            required={
                "schema_version",
                "run_id",
                "evaluation_set",
                "threshold_policy",
                "candidate",
                "baseline",
                "evaluator_version",
                "axes",
                "case_ids",
                "mode",
                "environment",
                "limits",
            },
            context="request",
        )
        if payload["schema_version"] != "quality_evaluation_request.v1":
            raise ContractValidationError("request.schema_version is unsupported")
        axes_raw = _sequence(payload["axes"], "request.axes")
        axes = tuple(
            _string(axis, f"request.axes[{index}]")
            for index, axis in enumerate(axes_raw)
        )
        if not axes or len(axes) != len(set(axes)) or any(axis not in AXES for axis in axes):
            raise ContractValidationError("request.axes must contain unique supported axes")
        if axes != tuple(axis for axis in AXES if axis in axes):
            raise ContractValidationError("request.axes must use canonical axis order")
        case_ids = _unique_strings(payload["case_ids"], "request.case_ids")
        if payload["mode"] != "provider_free_fixture" or payload["environment"] != "fixture":
            raise ContractValidationError(
                "request must be provider_free_fixture in fixture environment"
            )
        baseline_raw = payload["baseline"]
        return cls(
            schema_version="quality_evaluation_request.v1",
            run_id=_string(payload["run_id"], "request.run_id", identifier=True),
            evaluation_set=ContractRefV1.from_dict(
                payload["evaluation_set"], "request.evaluation_set"
            ),
            threshold_policy=ContractRefV1.from_dict(
                payload["threshold_policy"], "request.threshold_policy"
            ),
            candidate=EvidenceHeadV1.from_dict(payload["candidate"], "request.candidate"),
            baseline=(
                None
                if baseline_raw is None
                else EvidenceHeadV1.from_dict(baseline_raw, "request.baseline")
            ),
            evaluator_version=_string(payload["evaluator_version"], "request.evaluator_version"),
            axes=axes,
            case_ids=case_ids,
            mode="provider_free_fixture",
            environment="fixture",
            limits=RunLimitsV1.from_dict(payload["limits"]),
            digest=canonical_digest(dict(payload)),
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "run_id": self.run_id,
            "evaluation_set": self.evaluation_set.to_dict(),
            "threshold_policy": self.threshold_policy.to_dict(),
            "candidate": self.candidate.to_dict(),
            "baseline": None if self.baseline is None else self.baseline.to_dict(),
            "evaluator_version": self.evaluator_version,
            "axes": list(self.axes),
            "case_ids": list(self.case_ids),
            "mode": self.mode,
            "environment": self.environment,
            "limits": self.limits.to_dict(),
        }
