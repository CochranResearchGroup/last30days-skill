"""Provider-free fake-axis runner and deterministic report renderers."""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import Mapping, Protocol

from .contracts import (
    AXES,
    STATES,
    ContractValidationError,
    EvidenceHeadV1,
    EvaluationCaseV1,
    FakeOutcomeV1,
    MetricInputV1,
    QualityEvaluationRequestV1,
    QualityEvaluationSetV1,
    QualityThresholdPolicyV1,
    ThresholdRuleV1,
    canonical_digest,
    canonical_json,
)


class ExitCode(IntEnum):
    PASS = 0
    QUALITY_FAILURE = 2
    INVALID_INPUT = 3
    INCOMPLETE = 4


@dataclass(frozen=True)
class ComparisonV1:
    candidate_value: float | None
    baseline_value: float | None
    absolute_delta: float | None
    baseline_numerator: int | None
    baseline_denominator: int | None
    baseline_excluded: int | None

    def to_dict(self) -> dict[str, object]:
        return {
            "candidate_value": self.candidate_value,
            "baseline_value": self.baseline_value,
            "absolute_delta": self.absolute_delta,
            "baseline_numerator": self.baseline_numerator,
            "baseline_denominator": self.baseline_denominator,
            "baseline_excluded": self.baseline_excluded,
        }


@dataclass(frozen=True)
class MetricResultV1:
    metric_id: str
    name: str
    numerator: int
    denominator: int | None
    excluded: int
    value: float | None
    state: str
    threshold_rule_id: str
    threshold: float
    comparator: str
    minimum_denominator: int
    missing_data: str
    severity: str
    comparison: ComparisonV1

    def to_dict(self) -> dict[str, object]:
        return {
            "metric_id": self.metric_id,
            "name": self.name,
            "numerator": self.numerator,
            "denominator": self.denominator,
            "excluded": self.excluded,
            "value": self.value,
            "state": self.state,
            "threshold_rule_id": self.threshold_rule_id,
            "threshold": self.threshold,
            "comparator": self.comparator,
            "minimum_denominator": self.minimum_denominator,
            "missing_data": self.missing_data,
            "severity": self.severity,
            "comparison": self.comparison.to_dict(),
        }


@dataclass(frozen=True)
class ArtifactRefV1:
    artifact_id: str
    role: str
    media_type: str
    digest: str

    def to_dict(self) -> dict[str, object]:
        return {
            "artifact_id": self.artifact_id,
            "role": self.role,
            "media_type": self.media_type,
            "digest": self.digest,
        }


@dataclass(frozen=True)
class CaseResultV1:
    case_id: str
    axis: str
    state: str
    metrics: tuple[MetricResultV1, ...]
    failure_codes: tuple[str, ...]
    observed_refs: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "case_id": self.case_id,
            "axis": self.axis,
            "state": self.state,
            "metrics": [metric.to_dict() for metric in self.metrics],
            "failure_codes": list(self.failure_codes),
            "observed_refs": list(self.observed_refs),
        }


@dataclass(frozen=True)
class AxisResultV1:
    axis: str
    state: str
    case_ids: tuple[str, ...]
    metrics: tuple[MetricResultV1, ...]
    failure_codes: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "axis": self.axis,
            "state": self.state,
            "case_ids": list(self.case_ids),
            "metrics": [metric.to_dict() for metric in self.metrics],
            "failure_codes": list(self.failure_codes),
        }


@dataclass(frozen=True)
class EffectReceiptV1:
    schema_version: str = "quality_effect_receipt.v1"
    mode: str = "provider_free_fixture"
    network_requests: int = 0
    model_calls: int = 0
    browser_actions: int = 0
    database_reads: int = 0
    database_writes: int = 0
    runtime_mutations: int = 0
    external_dependencies: tuple[str, ...] = ()

    @property
    def digest(self) -> str:
        return canonical_digest(self.to_dict())

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "mode": self.mode,
            "network_requests": self.network_requests,
            "model_calls": self.model_calls,
            "browser_actions": self.browser_actions,
            "database_reads": self.database_reads,
            "database_writes": self.database_writes,
            "runtime_mutations": self.runtime_mutations,
            "external_dependencies": list(self.external_dependencies),
        }


@dataclass(frozen=True)
class CleanupReceiptV1:
    temporary_worktrees_created: int = 0
    processes_started: int = 0
    clean: bool = True

    def to_dict(self) -> dict[str, object]:
        return {
            "temporary_worktrees_created": self.temporary_worktrees_created,
            "processes_started": self.processes_started,
            "clean": self.clean,
        }


@dataclass(frozen=True)
class QualityEvaluationReportV1:
    schema_version: str
    report_id: str
    report_digest: str
    run_id: str
    request_digest: str
    evaluation_set: ArtifactRefV1
    threshold_policy: ArtifactRefV1
    candidate: dict[str, object]
    baseline: dict[str, object] | None
    evaluator_version: str
    environment: str
    state: str
    blocking_decision: str
    exit_code: ExitCode
    axes: tuple[AxisResultV1, ...]
    case_results: tuple[CaseResultV1, ...]
    effect_receipt: EffectReceiptV1
    artifacts: tuple[ArtifactRefV1, ...]
    errors: tuple[str, ...]
    truncated: bool
    cleanup: CleanupReceiptV1

    def _body_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "run_id": self.run_id,
            "request_digest": self.request_digest,
            "evaluation_set": self.evaluation_set.to_dict(),
            "threshold_policy": self.threshold_policy.to_dict(),
            "candidate": self.candidate,
            "baseline": self.baseline,
            "evaluator_version": self.evaluator_version,
            "environment": self.environment,
            "state": self.state,
            "blocking_decision": self.blocking_decision,
            "exit_code": int(self.exit_code),
            "axes": [axis.to_dict() for axis in self.axes],
            "case_results": [case.to_dict() for case in self.case_results],
            "effect_receipt": self.effect_receipt.to_dict(),
            "artifacts": [artifact.to_dict() for artifact in self.artifacts],
            "errors": list(self.errors),
            "truncated": self.truncated,
            "cleanup": self.cleanup.to_dict(),
        }

    def to_dict(self) -> dict[str, object]:
        return {
            **self._body_dict(),
            "report_id": self.report_id,
            "report_digest": self.report_digest,
        }

    @classmethod
    def from_dict(cls, raw: object) -> QualityEvaluationReportV1:
        """Strictly parse and authenticate a canonical report."""

        return _parse_report(raw)


class AxisAdapterV1(Protocol):
    axis: str

    def evaluate(self, case: EvaluationCaseV1, *, result_limit: int) -> FakeOutcomeV1:
        """Evaluate one sealed case without external effects."""


def _object(raw: object, context: str, fields: set[str]) -> Mapping[str, object]:
    if not isinstance(raw, Mapping) or any(not isinstance(key, str) for key in raw):
        raise ContractValidationError(f"{context} must be an object")
    keys = set(raw)
    if keys != fields:
        unknown = keys - fields
        missing = fields - keys
        detail = []
        if unknown:
            detail.append(f"unknown fields: {', '.join(sorted(unknown))}")
        if missing:
            detail.append(f"missing fields: {', '.join(sorted(missing))}")
        raise ContractValidationError(f"{context} has {'; '.join(detail)}")
    return raw


def _array(raw: object, context: str) -> list[object]:
    if not isinstance(raw, list):
        raise ContractValidationError(f"{context} must be an array")
    return raw


def _text(raw: object, context: str) -> str:
    if not isinstance(raw, str) or not raw:
        raise ContractValidationError(f"{context} must be a non-empty string")
    return raw


def _int(raw: object, context: str) -> int:
    if isinstance(raw, bool) or not isinstance(raw, int) or raw < 0:
        raise ContractValidationError(f"{context} must be a non-negative integer")
    return raw


def _optional_float(raw: object, context: str) -> float | None:
    if raw is None:
        return None
    if isinstance(raw, bool) or not isinstance(raw, (int, float)):
        raise ContractValidationError(f"{context} must be numeric or null")
    return float(raw)


def _artifact_from_dict(raw: object, context: str) -> ArtifactRefV1:
    payload = _object(raw, context, {"artifact_id", "role", "media_type", "digest"})
    digest = _text(payload["digest"], f"{context}.digest")
    if not digest.startswith("sha256:") or len(digest) != 71:
        raise ContractValidationError(f"{context}.digest is invalid")
    return ArtifactRefV1(
        artifact_id=_text(payload["artifact_id"], f"{context}.artifact_id"),
        role=_text(payload["role"], f"{context}.role"),
        media_type=_text(payload["media_type"], f"{context}.media_type"),
        digest=digest,
    )


def _comparison_from_dict(raw: object, context: str) -> ComparisonV1:
    payload = _object(
        raw,
        context,
        {
            "candidate_value",
            "baseline_value",
            "absolute_delta",
            "baseline_numerator",
            "baseline_denominator",
            "baseline_excluded",
        },
    )
    def optional_int(field: str) -> int | None:
        value = payload[field]
        return None if value is None else _int(value, f"{context}.{field}")

    comparison = ComparisonV1(
        candidate_value=_optional_float(payload["candidate_value"], f"{context}.candidate_value"),
        baseline_value=_optional_float(payload["baseline_value"], f"{context}.baseline_value"),
        absolute_delta=_optional_float(payload["absolute_delta"], f"{context}.absolute_delta"),
        baseline_numerator=optional_int("baseline_numerator"),
        baseline_denominator=optional_int("baseline_denominator"),
        baseline_excluded=optional_int("baseline_excluded"),
    )
    baseline_fields = (
        comparison.baseline_numerator,
        comparison.baseline_denominator,
        comparison.baseline_excluded,
    )
    if comparison.baseline_numerator is None:
        if (
            any(value is not None for value in baseline_fields)
            or comparison.baseline_value is not None
        ):
            raise ContractValidationError(f"{context} has a partial baseline")
    else:
        if comparison.baseline_excluded is None:
            raise ContractValidationError(f"{context} has a partial baseline")
        expected_baseline = (
            None
            if comparison.baseline_denominator is None
            else comparison.baseline_numerator / comparison.baseline_denominator
        )
        if comparison.baseline_value != expected_baseline:
            raise ContractValidationError(f"{context}.baseline_value is inconsistent")
    expected_delta = (
        None
        if comparison.candidate_value is None or comparison.baseline_value is None
        else comparison.candidate_value - comparison.baseline_value
    )
    if comparison.absolute_delta != expected_delta:
        raise ContractValidationError(f"{context}.absolute_delta is inconsistent")
    return comparison


def _metric_from_dict(raw: object, context: str) -> MetricResultV1:
    payload = _object(
        raw,
        context,
        {
            "metric_id",
            "name",
            "numerator",
            "denominator",
            "excluded",
            "value",
            "state",
            "threshold_rule_id",
            "threshold",
            "comparator",
            "minimum_denominator",
            "missing_data",
            "severity",
            "comparison",
        },
    )
    denominator_raw = payload["denominator"]
    denominator = (
        None if denominator_raw is None else _int(denominator_raw, f"{context}.denominator")
    )
    state = _text(payload["state"], f"{context}.state")
    if state not in {"passed", "failed", "not_measurable"}:
        raise ContractValidationError(f"{context}.state is invalid")
    comparator = _text(payload["comparator"], f"{context}.comparator")
    minimum_denominator = _int(
        payload["minimum_denominator"], f"{context}.minimum_denominator"
    )
    missing_data = _text(payload["missing_data"], f"{context}.missing_data")
    severity = _text(payload["severity"], f"{context}.severity")
    if (
        comparator not in {"gte", "lte"}
        or minimum_denominator < 1
        or missing_data not in {"fail", "not_measurable", "warn"}
        or severity not in {"blocking", "warning"}
    ):
        raise ContractValidationError(f"{context} threshold metadata is invalid")
    threshold = _optional_float(payload["threshold"], f"{context}.threshold")
    if threshold is None:
        raise ContractValidationError(f"{context}.threshold cannot be null")
    numerator = _int(payload["numerator"], f"{context}.numerator")
    value = _optional_float(payload["value"], f"{context}.value")
    expected_value = None if denominator is None else numerator / denominator
    if value != expected_value:
        raise ContractValidationError(f"{context}.value disagrees with numerator/denominator")
    comparison = _comparison_from_dict(payload["comparison"], f"{context}.comparison")
    if comparison.candidate_value != value:
        raise ContractValidationError(f"{context}.comparison disagrees with value")
    return MetricResultV1(
        metric_id=_text(payload["metric_id"], f"{context}.metric_id"),
        name=_text(payload["name"], f"{context}.name"),
        numerator=numerator,
        denominator=denominator,
        excluded=_int(payload["excluded"], f"{context}.excluded"),
        value=value,
        state=state,
        threshold_rule_id=_text(payload["threshold_rule_id"], f"{context}.threshold_rule_id"),
        threshold=threshold,
        comparator=comparator,
        minimum_denominator=minimum_denominator,
        missing_data=missing_data,
        severity=severity,
        comparison=comparison,
    )


def _strings(raw: object, context: str) -> tuple[str, ...]:
    return tuple(
        _text(item, f"{context}[{index}]")
        for index, item in enumerate(_array(raw, context))
    )


def _case_from_dict(raw: object, context: str) -> CaseResultV1:
    payload = _object(
        raw,
        context,
        {"case_id", "axis", "state", "metrics", "failure_codes", "observed_refs"},
    )
    axis = _text(payload["axis"], f"{context}.axis")
    state = _text(payload["state"], f"{context}.state")
    if axis not in AXES or state not in STATES:
        raise ContractValidationError(f"{context} axis or state is invalid")
    return CaseResultV1(
        case_id=_text(payload["case_id"], f"{context}.case_id"),
        axis=axis,
        state=state,
        metrics=tuple(
            _metric_from_dict(metric, f"{context}.metrics[{index}]")
            for index, metric in enumerate(_array(payload["metrics"], f"{context}.metrics"))
        ),
        failure_codes=_strings(payload["failure_codes"], f"{context}.failure_codes"),
        observed_refs=_strings(payload["observed_refs"], f"{context}.observed_refs"),
    )


def _axis_from_dict(raw: object, context: str) -> AxisResultV1:
    payload = _object(
        raw, context, {"axis", "state", "case_ids", "metrics", "failure_codes"}
    )
    axis = _text(payload["axis"], f"{context}.axis")
    state = _text(payload["state"], f"{context}.state")
    if axis not in AXES or state not in STATES:
        raise ContractValidationError(f"{context} axis or state is invalid")
    return AxisResultV1(
        axis=axis,
        state=state,
        case_ids=_strings(payload["case_ids"], f"{context}.case_ids"),
        metrics=tuple(
            _metric_from_dict(metric, f"{context}.metrics[{index}]")
            for index, metric in enumerate(_array(payload["metrics"], f"{context}.metrics"))
        ),
        failure_codes=_strings(payload["failure_codes"], f"{context}.failure_codes"),
    )


def _effect_from_dict(raw: object) -> EffectReceiptV1:
    fields = {
        "schema_version",
        "mode",
        "network_requests",
        "model_calls",
        "browser_actions",
        "database_reads",
        "database_writes",
        "runtime_mutations",
        "external_dependencies",
    }
    payload = _object(raw, "report.effect_receipt", fields)
    effect = EffectReceiptV1(
        schema_version=_text(payload["schema_version"], "report.effect_receipt.schema_version"),
        mode=_text(payload["mode"], "report.effect_receipt.mode"),
        network_requests=_int(
            payload["network_requests"], "report.effect_receipt.network_requests"
        ),
        model_calls=_int(payload["model_calls"], "report.effect_receipt.model_calls"),
        browser_actions=_int(payload["browser_actions"], "report.effect_receipt.browser_actions"),
        database_reads=_int(payload["database_reads"], "report.effect_receipt.database_reads"),
        database_writes=_int(payload["database_writes"], "report.effect_receipt.database_writes"),
        runtime_mutations=_int(
            payload["runtime_mutations"], "report.effect_receipt.runtime_mutations"
        ),
        external_dependencies=_strings(
            payload["external_dependencies"], "report.effect_receipt.external_dependencies"
        ),
    )
    if effect != EffectReceiptV1():
        raise ContractValidationError("report.effect_receipt is not provider-free")
    return effect


def _cleanup_from_dict(raw: object) -> CleanupReceiptV1:
    payload = _object(
        raw,
        "report.cleanup",
        {"temporary_worktrees_created", "processes_started", "clean"},
    )
    if not isinstance(payload["clean"], bool):
        raise ContractValidationError("report.cleanup.clean must be boolean")
    return CleanupReceiptV1(
        temporary_worktrees_created=_int(
            payload["temporary_worktrees_created"],
            "report.cleanup.temporary_worktrees_created",
        ),
        processes_started=_int(payload["processes_started"], "report.cleanup.processes_started"),
        clean=payload["clean"],
    )


def _parse_report(raw: object) -> QualityEvaluationReportV1:
    fields = {
        "schema_version",
        "report_id",
        "report_digest",
        "run_id",
        "request_digest",
        "evaluation_set",
        "threshold_policy",
        "candidate",
        "baseline",
        "evaluator_version",
        "environment",
        "state",
        "blocking_decision",
        "exit_code",
        "axes",
        "case_results",
        "effect_receipt",
        "artifacts",
        "errors",
        "truncated",
        "cleanup",
    }
    payload = _object(raw, "report", fields)
    if payload["schema_version"] != "quality_evaluation_report.v1":
        raise ContractValidationError("report.schema_version is unsupported")
    report_digest = _text(payload["report_digest"], "report.report_digest")
    body = dict(payload)
    body.pop("report_id")
    body.pop("report_digest")
    if canonical_digest(body) != report_digest:
        raise ContractValidationError("report digest does not match payload")
    report_id = _text(payload["report_id"], "report.report_id")
    expected_id = f"quality-report-{report_digest.removeprefix('sha256:')[:32]}"
    if report_id != expected_id:
        raise ContractValidationError("report id does not match digest")
    axes = tuple(
        _axis_from_dict(axis, f"report.axes[{index}]")
        for index, axis in enumerate(_array(payload["axes"], "report.axes"))
    )
    if tuple(axis.axis for axis in axes) != tuple(
        axis for axis in AXES if axis in {item.axis for item in axes}
    ):
        raise ContractValidationError("report axes are not canonically ordered")
    exit_raw = _int(payload["exit_code"], "report.exit_code")
    try:
        exit_code = ExitCode(exit_raw)
    except ValueError as exc:
        raise ContractValidationError("report.exit_code is unsupported") from exc
    state = _text(payload["state"], "report.state")
    expected_exit = {
        "passed": ExitCode.PASS,
        "failed": ExitCode.QUALITY_FAILURE,
        "not_measurable": ExitCode.INCOMPLETE,
        "incomplete": ExitCode.INCOMPLETE,
        "invalid": ExitCode.INVALID_INPUT,
    }.get(state)
    if expected_exit is None or exit_code is not expected_exit:
        raise ContractValidationError("report state and exit code disagree")
    blocking_decision = _text(payload["blocking_decision"], "report.blocking_decision")
    if blocking_decision != ("pass" if state == "passed" else "do_not_pass"):
        raise ContractValidationError("report blocking decision disagrees with state")
    candidate = EvidenceHeadV1.from_dict(payload["candidate"], "report.candidate")
    baseline = (
        None
        if payload["baseline"] is None
        else EvidenceHeadV1.from_dict(payload["baseline"], "report.baseline")
    )
    if not isinstance(payload["truncated"], bool):
        raise ContractValidationError("report.truncated must be boolean")
    return QualityEvaluationReportV1(
        schema_version=_text(payload["schema_version"], "report.schema_version"),
        report_id=report_id,
        report_digest=report_digest,
        run_id=_text(payload["run_id"], "report.run_id"),
        request_digest=_text(payload["request_digest"], "report.request_digest"),
        evaluation_set=_artifact_from_dict(payload["evaluation_set"], "report.evaluation_set"),
        threshold_policy=_artifact_from_dict(
            payload["threshold_policy"], "report.threshold_policy"
        ),
        candidate=candidate.to_dict(),
        baseline=None if baseline is None else baseline.to_dict(),
        evaluator_version=_text(payload["evaluator_version"], "report.evaluator_version"),
        environment=_text(payload["environment"], "report.environment"),
        state=state,
        blocking_decision=blocking_decision,
        exit_code=exit_code,
        axes=axes,
        case_results=tuple(
            _case_from_dict(case, f"report.case_results[{index}]")
            for index, case in enumerate(
                _array(payload["case_results"], "report.case_results")
            )
        ),
        effect_receipt=_effect_from_dict(payload["effect_receipt"]),
        artifacts=tuple(
            _artifact_from_dict(artifact, f"report.artifacts[{index}]")
            for index, artifact in enumerate(_array(payload["artifacts"], "report.artifacts"))
        ),
        errors=_strings(payload["errors"], "report.errors"),
        truncated=payload["truncated"],
        cleanup=_cleanup_from_dict(payload["cleanup"]),
    )


@dataclass(frozen=True)
class _SealedFakeAdapter:
    axis: str

    def evaluate(self, case: EvaluationCaseV1, *, result_limit: int) -> FakeOutcomeV1:
        if case.axis != self.axis:
            raise ContractValidationError("fake adapter received a case for another axis")
        if result_limit < len(case.outcome.observed_refs):
            raise RuntimeError("fake_result_limit_exceeded")
        return case.outcome


class FakeAcquisitionAdapter(_SealedFakeAdapter):
    def __init__(self) -> None:
        super().__init__("acquisition")


class FakeCorpusAdapter(_SealedFakeAdapter):
    def __init__(self) -> None:
        super().__init__("corpus")


class FakeRetrievalAdapter(_SealedFakeAdapter):
    def __init__(self) -> None:
        super().__init__("retrieval")


class FakeGroundingAdapter(_SealedFakeAdapter):
    def __init__(self) -> None:
        super().__init__("grounding")


def default_fake_adapters() -> dict[str, AxisAdapterV1]:
    return {
        "acquisition": FakeAcquisitionAdapter(),
        "corpus": FakeCorpusAdapter(),
        "retrieval": FakeRetrievalAdapter(),
        "grounding": FakeGroundingAdapter(),
    }


_STATE_PRIORITY = {
    "passed": 0,
    "failed": 1,
    "not_measurable": 2,
    "incomplete": 3,
    "invalid": 4,
}


def _worst_state(states: list[str]) -> str:
    return max(states, key=_STATE_PRIORITY.__getitem__) if states else "incomplete"


def _metric_result(
    *,
    axis: str,
    scope_id: str,
    metric: MetricInputV1,
    rule: ThresholdRuleV1,
    baseline_metric: MetricInputV1 | None = None,
) -> MetricResultV1:
    value = None if metric.denominator is None else metric.numerator / metric.denominator
    if metric.denominator is None or metric.denominator < rule.minimum_denominator:
        state = "failed" if rule.missing_data == "fail" else "not_measurable"
    else:
        passed = value >= rule.threshold if rule.comparator == "gte" else value <= rule.threshold
        state = "passed" if passed or rule.severity == "warning" else "failed"
    baseline_value = (
        None
        if baseline_metric is None or baseline_metric.denominator is None
        else baseline_metric.numerator / baseline_metric.denominator
    )
    comparison = ComparisonV1(
        candidate_value=value,
        baseline_value=baseline_value,
        absolute_delta=(
            None if value is None or baseline_value is None else value - baseline_value
        ),
        baseline_numerator=None if baseline_metric is None else baseline_metric.numerator,
        baseline_denominator=None if baseline_metric is None else baseline_metric.denominator,
        baseline_excluded=None if baseline_metric is None else baseline_metric.excluded,
    )
    identity = {
        "axis": axis,
        "scope_id": scope_id,
        "metric": metric.to_dict(),
        "threshold_rule_id": rule.rule_id,
    }
    return MetricResultV1(
        metric_id=f"quality-metric-{canonical_digest(identity).removeprefix('sha256:')[:32]}",
        name=metric.name,
        numerator=metric.numerator,
        denominator=metric.denominator,
        excluded=metric.excluded,
        value=value,
        state=state,
        threshold_rule_id=rule.rule_id,
        threshold=rule.threshold,
        comparator=rule.comparator,
        minimum_denominator=rule.minimum_denominator,
        missing_data=rule.missing_data,
        severity=rule.severity,
        comparison=comparison,
    )


class QualityRunnerV1:
    """Deep Packet 1 interface: validate, evaluate, classify, and report."""

    def __init__(self, adapters: Mapping[str, AxisAdapterV1]) -> None:
        if set(adapters) != set(AXES):
            raise ContractValidationError("runner requires exactly four axis adapters")
        if any(adapters[axis].axis != axis for axis in AXES):
            raise ContractValidationError("runner adapter identity mismatch")
        self._adapters = dict(adapters)
        self._run_requests: dict[str, str] = {}

    def run(
        self,
        request: QualityEvaluationRequestV1,
        evaluation_set: QualityEvaluationSetV1,
        policy: QualityThresholdPolicyV1,
    ) -> QualityEvaluationReportV1:
        prior_digest = self._run_requests.get(request.run_id)
        if prior_digest is not None and prior_digest != request.digest:
            raise ContractValidationError("run_id conflict: request digest changed")
        self._run_requests[request.run_id] = request.digest
        self._validate_pins(request, evaluation_set, policy)
        selected = self._select_cases(request, evaluation_set)
        rules = {(rule.axis, rule.metric): rule for rule in policy.rules}
        case_results: list[CaseResultV1] = []
        for case in selected:
            try:
                outcome = self._adapters[case.axis].evaluate(
                    case, result_limit=request.limits.per_case_limit
                )
                missing_rule = next(
                    (
                        metric.name
                        for metric in outcome.metrics
                        if (case.axis, metric.name) not in rules
                    ),
                    None,
                )
                if missing_rule is not None:
                    raise ContractValidationError(
                        f"threshold policy has no rule for {case.axis}.{missing_rule}"
                    )
                if request.baseline is not None and outcome.baseline_metrics is None:
                    case_results.append(
                        CaseResultV1(
                            case_id=case.case_id,
                            axis=case.axis,
                            state="incomplete",
                            metrics=(),
                            failure_codes=("baseline_metrics_missing",),
                            observed_refs=outcome.observed_refs,
                        )
                    )
                    continue
                baseline_by_name = {
                    metric.name: metric for metric in (outcome.baseline_metrics or ())
                }
                metrics = tuple(
                    _metric_result(
                        axis=case.axis,
                        scope_id=case.case_id,
                        metric=metric,
                        rule=rules[(case.axis, metric.name)],
                        baseline_metric=(
                            None
                            if request.baseline is None
                            else baseline_by_name[metric.name]
                        ),
                    )
                    for metric in outcome.metrics
                )
                metric_state = _worst_state([metric.state for metric in metrics])
                state = _worst_state([outcome.state, metric_state])
                failure_codes = list(outcome.failure_codes)
                failure_codes.extend(
                    f"threshold:{metric.threshold_rule_id}"
                    for metric in metrics
                    if metric.state != "passed"
                )
                case_results.append(
                    CaseResultV1(
                        case_id=case.case_id,
                        axis=case.axis,
                        state=state,
                        metrics=metrics,
                        failure_codes=tuple(sorted(set(failure_codes))),
                        observed_refs=outcome.observed_refs,
                    )
                )
            except ContractValidationError:
                raise
            except Exception as exc:
                case_results.append(
                    CaseResultV1(
                        case_id=case.case_id,
                        axis=case.axis,
                        state="incomplete",
                        metrics=(),
                        failure_codes=(f"adapter_error:{type(exc).__name__}",),
                        observed_refs=(),
                    )
                )

        axes = tuple(
            self._axis_result(axis, case_results, rules)
            for axis in AXES
            if axis in request.axes
        )
        state = _worst_state([axis.state for axis in axes])
        exit_code = {
            "passed": ExitCode.PASS,
            "failed": ExitCode.QUALITY_FAILURE,
            "not_measurable": ExitCode.INCOMPLETE,
            "incomplete": ExitCode.INCOMPLETE,
            "invalid": ExitCode.INVALID_INPUT,
        }[state]
        return self._build_report(
            request=request,
            evaluation_set=evaluation_set,
            policy=policy,
            axes=axes,
            case_results=tuple(case_results),
            state=state,
            exit_code=exit_code,
        )

    @staticmethod
    def _validate_pins(
        request: QualityEvaluationRequestV1,
        evaluation_set: QualityEvaluationSetV1,
        policy: QualityThresholdPolicyV1,
    ) -> None:
        if request.evaluation_set.id != evaluation_set.evaluation_set_id:
            raise ContractValidationError("evaluation set id does not match request")
        if request.evaluation_set.digest != evaluation_set.digest:
            raise ContractValidationError("evaluation set digest does not match request")
        if request.threshold_policy.id != policy.policy_id:
            raise ContractValidationError("threshold policy id does not match request")
        if request.threshold_policy.digest != policy.digest:
            raise ContractValidationError("threshold policy digest does not match request")

    @staticmethod
    def _select_cases(
        request: QualityEvaluationRequestV1,
        evaluation_set: QualityEvaluationSetV1,
    ) -> tuple[EvaluationCaseV1, ...]:
        known = {case.case_id for case in evaluation_set.cases}
        unknown = set(request.case_ids) - known
        if unknown:
            raise ContractValidationError(
                f"request names unknown cases: {', '.join(sorted(unknown))}"
            )
        selected = tuple(
            case
            for case in evaluation_set.cases
            if case.axis in request.axes
            and (not request.case_ids or case.case_id in request.case_ids)
        )
        if len(selected) > request.limits.max_cases:
            raise ContractValidationError("request max_cases is smaller than selected case count")
        return selected

    @staticmethod
    def _axis_result(
        axis: str,
        case_results: list[CaseResultV1],
        rules: Mapping[tuple[str, str], ThresholdRuleV1],
    ) -> AxisResultV1:
        cases = [case for case in case_results if case.axis == axis]
        if not cases:
            return AxisResultV1(
                axis=axis,
                state="incomplete",
                case_ids=(),
                metrics=(),
                failure_codes=("axis_without_cases",),
            )
        metric_names = sorted({metric.name for case in cases for metric in case.metrics})
        aggregate_metrics: list[MetricResultV1] = []
        for name in metric_names:
            inputs = [metric for case in cases for metric in case.metrics if metric.name == name]
            denominator = (
                None
                if any(metric.denominator is None for metric in inputs)
                else sum(
                    int(metric.denominator)
                    for metric in inputs
                    if metric.denominator is not None
                )
            )
            aggregate_metrics.append(
                _metric_result(
                    axis=axis,
                    scope_id="global",
                    metric=MetricInputV1(
                        name=name,
                        numerator=sum(metric.numerator for metric in inputs),
                        denominator=denominator,
                        excluded=sum(metric.excluded for metric in inputs),
                    ),
                    rule=rules[(axis, name)],
                    baseline_metric=(
                        None
                        if all(metric.comparison.baseline_numerator is None for metric in inputs)
                        else MetricInputV1(
                            name=name,
                            numerator=sum(
                                metric.comparison.baseline_numerator or 0 for metric in inputs
                            ),
                            denominator=(
                                None
                                if any(
                                    metric.comparison.baseline_denominator is None
                                    for metric in inputs
                                )
                                else sum(
                                    metric.comparison.baseline_denominator or 0
                                    for metric in inputs
                                )
                            ),
                            excluded=sum(
                                metric.comparison.baseline_excluded or 0 for metric in inputs
                            ),
                        )
                    ),
                )
            )
        state = _worst_state(
            [case.state for case in cases]
            + [metric.state for metric in aggregate_metrics]
        )
        return AxisResultV1(
            axis=axis,
            state=state,
            case_ids=tuple(case.case_id for case in cases),
            metrics=tuple(aggregate_metrics),
            failure_codes=tuple(
                sorted({code for case in cases for code in case.failure_codes})
            ),
        )

    @staticmethod
    def _build_report(
        *,
        request: QualityEvaluationRequestV1,
        evaluation_set: QualityEvaluationSetV1,
        policy: QualityThresholdPolicyV1,
        axes: tuple[AxisResultV1, ...],
        case_results: tuple[CaseResultV1, ...],
        state: str,
        exit_code: ExitCode,
    ) -> QualityEvaluationReportV1:
        evaluation_artifact = ArtifactRefV1(
            artifact_id=evaluation_set.evaluation_set_id,
            role="evaluation_set",
            media_type="application/json",
            digest=evaluation_set.digest,
        )
        policy_artifact = ArtifactRefV1(
            artifact_id=policy.policy_id,
            role="threshold_policy",
            media_type="application/json",
            digest=policy.digest,
        )
        fields = dict(
            schema_version="quality_evaluation_report.v1",
            report_id="",
            report_digest="",
            run_id=request.run_id,
            request_digest=request.digest,
            evaluation_set=evaluation_artifact,
            threshold_policy=policy_artifact,
            candidate=request.candidate.to_dict(),
            baseline=None if request.baseline is None else request.baseline.to_dict(),
            evaluator_version=request.evaluator_version,
            environment=request.environment,
            state=state,
            blocking_decision="pass" if state == "passed" else "do_not_pass",
            exit_code=exit_code,
            axes=axes,
            case_results=case_results,
            effect_receipt=EffectReceiptV1(),
            artifacts=(evaluation_artifact, policy_artifact),
            errors=(),
            truncated=False,
            cleanup=CleanupReceiptV1(),
        )
        unsigned = QualityEvaluationReportV1(**fields)
        report_digest = canonical_digest(unsigned._body_dict())
        return QualityEvaluationReportV1(
            **{
                **fields,
                "report_id": f"quality-report-{report_digest.removeprefix('sha256:')[:32]}",
                "report_digest": report_digest,
            }
        )


def render_report_json(report: QualityEvaluationReportV1) -> str:
    """Render authoritative canonical JSON with one terminating newline."""

    return canonical_json(report.to_dict()) + "\n"


def render_report_markdown(report: QualityEvaluationReportV1) -> str:
    """Render a deterministic human projection of the authoritative report."""

    lines = [
        f"# Service Quality Report: {report.run_id}",
        "",
        f"State: `{report.state}`",
        f"Blocking decision: `{report.blocking_decision}`",
        f"Exit code: `{int(report.exit_code)}`",
        f"Report: `{report.report_id}`",
        f"Report digest: `{report.report_digest}`",
        f"Environment: `{report.environment}`",
        "",
        "## Axes",
        "",
    ]
    for axis in report.axes:
        lines.extend([f"### {axis.axis.title()}", "", f"State: `{axis.state}`", ""])
        for metric in axis.metrics:
            value = "not measurable" if metric.value is None else f"{metric.value:.6f}"
            lines.append(
                f"- `{metric.name}`: {metric.numerator}/{metric.denominator} "
                f"(excluded {metric.excluded}), value {value}, "
                f"threshold `{metric.comparator} {metric.threshold}` via "
                f"`{metric.threshold_rule_id}` (minimum denominator "
                f"{metric.minimum_denominator}, missing `{metric.missing_data}`) — "
                f"`{metric.state}`"
            )
        if not axis.metrics:
            lines.append("- No measurable metrics.")
        lines.append("")
    lines.extend(
        [
            "## Effects",
            "",
            "- Provider-free fixture mode; zero network, model, browser, database, "
            "or runtime effects.",
            "",
        ]
    )
    return "\n".join(lines)
