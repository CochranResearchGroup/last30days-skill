"""Provider-free acceptance tests for the repo-only service quality tracer."""

from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

from dev.last30days.quality import (
    ContractValidationError,
    ExitCode,
    QualityEvaluationRequestV1,
    QualityEvaluationReportV1,
    QualityEvaluationSetV1,
    QualityRunnerV1,
    QualityThresholdPolicyV1,
    canonical_digest,
    default_fake_adapters,
    render_report_json,
    render_report_markdown,
)


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures" / "service_quality"
CLI = ROOT / "dev" / "last30days" / "scripts" / "evaluate_service_quality.py"


def _evaluation_set_payload() -> dict[str, object]:
    return {
        "schema_version": "quality_evaluation_set.v1",
        "evaluation_set_id": "service-quality-packet-1",
        "version": 1,
        "description": "Synthetic four-axis tracer fixtures.",
        "source_status": "synthetic",
        "source_licenses": [
            {
                "source": "web",
                "status": "synthetic",
                "license": "synthetic-no-third-party-content",
            }
        ],
        "created_date": "2026-09-13",
        "reviewed_date": "2026-09-13",
        "cases": [
            {
                "case_id": "acquisition-pass",
                "axis": "acquisition",
                "tags": ["positive"],
                "outcome": {
                    "state": "passed",
                    "metrics": [
                        {
                            "name": "coverage_rate",
                            "numerator": 4,
                            "denominator": 4,
                            "excluded": 0,
                        }
                    ],
                    "failure_codes": [],
                    "observed_refs": ["receipt:synthetic-acquisition"],
                },
            }
        ],
    }


def test_evaluation_set_is_strict_canonical_and_deterministically_identified():
    payload = _evaluation_set_payload()

    evaluation_set = QualityEvaluationSetV1.from_dict(payload)

    assert evaluation_set.digest == canonical_digest(payload)
    assert evaluation_set.to_dict() == payload
    assert QualityEvaluationSetV1.from_dict(copy.deepcopy(payload)).digest == evaluation_set.digest

    payload["unexpected"] = True
    with pytest.raises(ContractValidationError, match="unknown fields"):
        QualityEvaluationSetV1.from_dict(payload)


def _threshold_policy_payload() -> dict[str, object]:
    return {
        "schema_version": "quality_threshold_policy.v1",
        "policy_id": "service-quality-packet-1",
        "version": 1,
        "rules": [
            {
                "rule_id": "acquisition-coverage-floor",
                "axis": "acquisition",
                "metric": "coverage_rate",
                "scope": "global",
                "comparator": "gte",
                "threshold": 1.0,
                "minimum_denominator": 1,
                "severity": "blocking",
                "missing_data": "not_measurable",
            }
        ],
    }


def _evidence_head() -> dict[str, object]:
    return {
        "repository_commit": "1" * 40,
        "service_contract_version": "fixture-v1",
        "database_schema_version": 0,
        "index_head": "index:synthetic-v1",
        "embedding_config_digest": "sha256:" + "2" * 64,
        "ranking_config_digest": "sha256:" + "3" * 64,
    }


def _request_payload(
    evaluation_set: QualityEvaluationSetV1,
    policy: QualityThresholdPolicyV1,
) -> dict[str, object]:
    return {
        "schema_version": "quality_evaluation_request.v1",
        "run_id": "packet-1-pass",
        "evaluation_set": {
            "id": evaluation_set.evaluation_set_id,
            "digest": evaluation_set.digest,
        },
        "threshold_policy": {"id": policy.policy_id, "digest": policy.digest},
        "candidate": _evidence_head(),
        "baseline": None,
        "evaluator_version": "packet-1-v1",
        "axes": ["acquisition", "corpus", "retrieval", "grounding"],
        "case_ids": [],
        "mode": "provider_free_fixture",
        "environment": "fixture",
        "limits": {
            "max_cases": 100,
            "max_wall_seconds": 10,
            "max_output_bytes": 100000,
            "per_case_limit": 20,
        },
    }


def test_policy_and_request_contracts_pin_inputs_and_fail_closed():
    evaluation_set = QualityEvaluationSetV1.from_dict(_evaluation_set_payload())
    policy_payload = _threshold_policy_payload()
    policy = QualityThresholdPolicyV1.from_dict(policy_payload)
    request_payload = _request_payload(evaluation_set, policy)

    request = QualityEvaluationRequestV1.from_dict(request_payload)

    assert policy.digest == canonical_digest(policy_payload)
    assert request.digest == canonical_digest(request_payload)
    assert request.evaluation_set.digest == evaluation_set.digest
    assert request.threshold_policy.digest == policy.digest
    assert request.axes == ("acquisition", "corpus", "retrieval", "grounding")

    bad_request = copy.deepcopy(request_payload)
    bad_request["limits"]["unexpected"] = 1  # type: ignore[index]
    with pytest.raises(ContractValidationError, match="unknown fields"):
        QualityEvaluationRequestV1.from_dict(bad_request)


def _four_axis_set_payload() -> dict[str, object]:
    cases = []
    for axis in ("acquisition", "corpus", "grounding", "retrieval"):
        cases.append(
            {
                "case_id": f"{axis}-pass",
                "axis": axis,
                "tags": ["positive", "synthetic"],
                "outcome": {
                    "state": "passed",
                    "metrics": [
                        {
                            "name": "success_rate",
                            "numerator": 4,
                            "denominator": 4,
                            "excluded": 0,
                        }
                    ],
                    "failure_codes": [],
                    "observed_refs": [f"fixture:{axis}-pass"],
                },
            }
        )
    return {
        "schema_version": "quality_evaluation_set.v1",
        "evaluation_set_id": "service-quality-four-axis",
        "version": 1,
        "description": "Synthetic four-axis tracer fixtures.",
        "source_status": "synthetic",
        "source_licenses": [
            {
                "source": source,
                "status": "synthetic",
                "license": "synthetic-no-third-party-content",
            }
            for source in ("bluesky", "reddit", "web", "x", "youtube")
        ],
        "created_date": "2026-09-13",
        "reviewed_date": "2026-09-13",
        "cases": cases,
    }


def _four_axis_policy_payload() -> dict[str, object]:
    return {
        "schema_version": "quality_threshold_policy.v1",
        "policy_id": "service-quality-four-axis",
        "version": 1,
        "rules": [
            {
                "rule_id": f"{axis}-success-floor",
                "axis": axis,
                "metric": "success_rate",
                "scope": "global",
                "comparator": "gte",
                "threshold": 1.0,
                "minimum_denominator": 1,
                "severity": "blocking",
                "missing_data": "not_measurable",
            }
            for axis in ("acquisition", "corpus", "grounding", "retrieval")
        ],
    }


def test_runner_keeps_four_axes_separate_and_renders_deterministically():
    evaluation_set = QualityEvaluationSetV1.from_dict(_four_axis_set_payload())
    policy = QualityThresholdPolicyV1.from_dict(_four_axis_policy_payload())
    request = QualityEvaluationRequestV1.from_dict(
        _request_payload(evaluation_set, policy)
    )
    runner = QualityRunnerV1(default_fake_adapters())

    first = runner.run(request, evaluation_set, policy)
    second = runner.run(request, evaluation_set, policy)

    assert first == second
    assert first.state == "passed"
    assert first.exit_code is ExitCode.PASS
    assert [axis.axis for axis in first.axes] == [
        "acquisition",
        "corpus",
        "retrieval",
        "grounding",
    ]
    assert all(axis.state == "passed" for axis in first.axes)
    assert all(metric.denominator == 4 for axis in first.axes for metric in axis.metrics)
    assert all(metric.threshold_rule_id for axis in first.axes for metric in axis.metrics)
    assert all(metric.minimum_denominator == 1 for axis in first.axes for metric in axis.metrics)
    assert all(
        metric.missing_data == "not_measurable"
        for axis in first.axes
        for metric in axis.metrics
    )
    assert first.effect_receipt.to_dict() == {
        "schema_version": "quality_effect_receipt.v1",
        "mode": "provider_free_fixture",
        "network_requests": 0,
        "model_calls": 0,
        "browser_actions": 0,
        "database_reads": 0,
        "database_writes": 0,
        "runtime_mutations": 0,
        "external_dependencies": [],
    }
    assert render_report_json(first) == render_report_json(second)
    markdown = render_report_markdown(first)
    assert "# Service Quality Report: packet-1-pass" in markdown
    assert markdown.index("Acquisition") < markdown.index("Corpus")
    assert markdown.index("Corpus") < markdown.index("Retrieval")
    assert markdown.index("Retrieval") < markdown.index("Grounding")


def _run_modified_outcome(
    *,
    state: str,
    numerator: int,
    denominator: int | None,
):
    set_payload = _four_axis_set_payload()
    acquisition = set_payload["cases"][0]  # type: ignore[index]
    acquisition["outcome"]["state"] = state  # type: ignore[index]
    acquisition["outcome"]["failure_codes"] = (  # type: ignore[index]
        [] if state == "passed" else [state]
    )
    metric = acquisition["outcome"]["metrics"][0]  # type: ignore[index]
    metric["numerator"] = numerator
    metric["denominator"] = denominator
    evaluation_set = QualityEvaluationSetV1.from_dict(set_payload)
    policy = QualityThresholdPolicyV1.from_dict(_four_axis_policy_payload())
    request = QualityEvaluationRequestV1.from_dict(
        _request_payload(evaluation_set, policy)
    )
    return QualityRunnerV1(default_fake_adapters()).run(
        request, evaluation_set, policy
    )


def test_quality_failure_and_unknown_denominator_cannot_pass():
    failed = _run_modified_outcome(state="passed", numerator=3, denominator=4)
    unknown = _run_modified_outcome(
        state="not_measurable", numerator=0, denominator=None
    )

    assert failed.state == "failed"
    assert failed.exit_code is ExitCode.QUALITY_FAILURE
    assert failed.blocking_decision == "do_not_pass"
    assert "threshold:acquisition-success-floor" in failed.case_results[0].failure_codes

    assert unknown.state == "not_measurable"
    assert unknown.exit_code is ExitCode.INCOMPLETE
    assert unknown.blocking_decision == "do_not_pass"
    assert unknown.axes[0].metrics[0].value is None


def test_adapter_crash_is_an_inspectable_incomplete_result():
    evaluation_set = QualityEvaluationSetV1.from_dict(_four_axis_set_payload())
    policy = QualityThresholdPolicyV1.from_dict(_four_axis_policy_payload())
    request = QualityEvaluationRequestV1.from_dict(
        _request_payload(evaluation_set, policy)
    )

    class CrashingAcquisitionAdapter:
        axis = "acquisition"

        def evaluate(self, case, *, result_limit):
            raise RuntimeError("synthetic crash")

    adapters = default_fake_adapters()
    adapters["acquisition"] = CrashingAcquisitionAdapter()
    report = QualityRunnerV1(adapters).run(request, evaluation_set, policy)

    assert report.state == "incomplete"
    assert report.exit_code is ExitCode.INCOMPLETE
    assert report.case_results[0].state == "incomplete"
    assert report.case_results[0].failure_codes == ("adapter_error:RuntimeError",)
    assert report.axes[0].state == "incomplete"


def test_run_id_is_immutable_within_a_runner():
    evaluation_set = QualityEvaluationSetV1.from_dict(_four_axis_set_payload())
    policy = QualityThresholdPolicyV1.from_dict(_four_axis_policy_payload())
    request_payload = _request_payload(evaluation_set, policy)
    request = QualityEvaluationRequestV1.from_dict(request_payload)
    runner = QualityRunnerV1(default_fake_adapters())
    runner.run(request, evaluation_set, policy)

    changed = copy.deepcopy(request_payload)
    changed["evaluator_version"] = "packet-1-v2"
    conflicting_request = QualityEvaluationRequestV1.from_dict(changed)

    with pytest.raises(ContractValidationError, match="run_id conflict"):
        runner.run(conflicting_request, evaluation_set, policy)


def test_comparison_binds_candidate_and_baseline_heads_and_values():
    set_payload = _four_axis_set_payload()
    acquisition = set_payload["cases"][0]  # type: ignore[index]
    acquisition["outcome"]["baseline_metrics"] = [  # type: ignore[index]
        {
            "name": "success_rate",
            "numerator": 3,
            "denominator": 4,
            "excluded": 0,
        }
    ]
    evaluation_set = QualityEvaluationSetV1.from_dict(set_payload)
    policy = QualityThresholdPolicyV1.from_dict(_four_axis_policy_payload())
    request_payload = _request_payload(evaluation_set, policy)
    request_payload["axes"] = ["acquisition"]
    request_payload["case_ids"] = ["acquisition-pass"]
    baseline = _evidence_head()
    baseline["repository_commit"] = "4" * 40
    request_payload["baseline"] = baseline
    request = QualityEvaluationRequestV1.from_dict(request_payload)

    report = QualityRunnerV1(default_fake_adapters()).run(
        request, evaluation_set, policy
    )

    comparison = report.axes[0].metrics[0].comparison
    assert report.candidate["repository_commit"] == "1" * 40
    assert report.baseline["repository_commit"] == "4" * 40  # type: ignore[index]
    assert comparison.candidate_value == 1.0
    assert comparison.baseline_value == 0.75
    assert comparison.absolute_delta == 0.25
    assert comparison.baseline_numerator == 3
    assert comparison.baseline_denominator == 4
    assert QualityEvaluationReportV1.from_dict(
        json.loads(render_report_json(report))
    ) == report


def test_report_contract_round_trips_and_rejects_tampering():
    evaluation_set = QualityEvaluationSetV1.from_dict(_four_axis_set_payload())
    policy = QualityThresholdPolicyV1.from_dict(_four_axis_policy_payload())
    request = QualityEvaluationRequestV1.from_dict(
        _request_payload(evaluation_set, policy)
    )
    report = QualityRunnerV1(default_fake_adapters()).run(
        request, evaluation_set, policy
    )
    payload = json.loads(render_report_json(report))

    assert QualityEvaluationReportV1.from_dict(payload) == report

    payload["blocking_decision"] = "do_not_pass"
    with pytest.raises(ContractValidationError, match="digest"):
        QualityEvaluationReportV1.from_dict(payload)


def _cli(evaluation_set: Path, request: Path, *, emit: str = "json"):
    return subprocess.run(
        [
            sys.executable,
            str(CLI),
            "--evaluation-set",
            str(evaluation_set),
            "--threshold-policy",
            str(FIXTURES / "threshold-policy.v1.json"),
            "--request",
            str(request),
            "--emit",
            emit,
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def test_sealed_fixtures_and_cli_replay_all_exit_classes(tmp_path):
    passing = _cli(
        FIXTURES / "evaluation-set-pass.v1.json",
        FIXTURES / "request-pass.v1.json",
    )
    replay = _cli(
        FIXTURES / "evaluation-set-pass.v1.json",
        FIXTURES / "request-pass.v1.json",
    )
    failing = _cli(
        FIXTURES / "evaluation-set-edge.v1.json",
        FIXTURES / "request-fail.v1.json",
    )
    incomplete = _cli(
        FIXTURES / "evaluation-set-edge.v1.json",
        FIXTURES / "request-edge.v1.json",
    )

    assert passing.returncode == ExitCode.PASS
    assert passing.stdout == replay.stdout
    pass_report = QualityEvaluationReportV1.from_dict(json.loads(passing.stdout))
    assert pass_report.state == "passed"
    assert failing.returncode == ExitCode.QUALITY_FAILURE
    assert json.loads(failing.stdout)["state"] == "failed"
    assert incomplete.returncode == ExitCode.INCOMPLETE
    edge = json.loads(incomplete.stdout)
    assert edge["state"] == "incomplete"
    observed_codes = {
        code for case in edge["case_results"] for code in case["failure_codes"]
    }
    assert {
        "axis_skipped",
        "cross_partition_leakage",
        "digest_mismatch",
        "duplicate_identity",
        "empty_result",
        "evaluator_crash",
        "malformed_cursor",
        "no_evidence",
        "partial_acquisition",
        "stale_head",
        "unsupported_claim",
    } <= observed_codes

    invalid_request = json.loads((FIXTURES / "request-pass.v1.json").read_text())
    invalid_request["unexpected"] = True
    invalid_path = tmp_path / "invalid-request.json"
    invalid_path.write_text(json.dumps(invalid_request), encoding="utf-8")
    invalid = _cli(FIXTURES / "evaluation-set-pass.v1.json", invalid_path)
    assert invalid.returncode == ExitCode.INVALID_INPUT
    assert json.loads(invalid.stdout)["schema_version"] == "quality_error.v1"

    markdown = _cli(
        FIXTURES / "evaluation-set-pass.v1.json",
        FIXTURES / "request-pass.v1.json",
        emit="markdown",
    )
    assert markdown.returncode == ExitCode.PASS
    assert "# Service Quality Report: service-quality-pass-v1" in markdown.stdout
