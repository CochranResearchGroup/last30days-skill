#!/usr/bin/env python3
"""Run the repo-only deterministic provider-free service quality tracer."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
SKILL_SCRIPTS = ROOT / "skills" / "last30days" / "scripts"
if str(SKILL_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SKILL_SCRIPTS))

from dev.last30days.quality import (  # noqa: E402
    ContractValidationError,
    ExitCode,
    QualityEvaluationRequestV1,
    QualityEvaluationSetV1,
    QualityRunnerV1,
    QualityThresholdPolicyV1,
    canonical_json,
    default_fake_adapters,
    real_fixture_adapters,
    render_report_json,
    render_report_markdown,
)


def _no_duplicate_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ContractValidationError(f"JSON object has duplicate field: {key}")
        result[key] = value
    return result


def _load_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_no_duplicate_object)
    except json.JSONDecodeError as exc:
        raise ContractValidationError(f"{path.name} is not valid JSON: {exc.msg}") from exc


def _error_payload(classification: str, code: str, detail: str) -> str:
    return canonical_json(
        {
            "schema_version": "quality_error.v1",
            "classification": classification,
            "code": code,
            "detail": detail,
        }
    ) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run sealed provider-free service quality fixtures"
    )
    parser.add_argument("--evaluation-set", type=Path, required=True)
    parser.add_argument("--threshold-policy", type=Path, required=True)
    parser.add_argument("--request", type=Path, required=True)
    parser.add_argument(
        "--fixture",
        action="append",
        default=[],
        metavar="ID=PATH",
        help="sealed local SQLite fixture; repeat for each fixture id",
    )
    parser.add_argument("--emit", choices=("json", "markdown"), default="json")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        evaluation_set = QualityEvaluationSetV1.from_dict(
            _load_json(args.evaluation_set)
        )
        threshold_policy = QualityThresholdPolicyV1.from_dict(
            _load_json(args.threshold_policy)
        )
        request = QualityEvaluationRequestV1.from_dict(_load_json(args.request))
        fixtures: dict[str, Path] = {}
        for raw in args.fixture:
            fixture_id, separator, fixture_path = raw.partition("=")
            if not separator or not fixture_id or not fixture_path or fixture_id in fixtures:
                raise ContractValidationError("--fixture must be unique ID=PATH")
            fixtures[fixture_id] = Path(fixture_path)
        adapters = real_fixture_adapters(fixtures) if fixtures else default_fake_adapters()
        report = QualityRunnerV1(adapters).run(
            request, evaluation_set, threshold_policy
        )
        rendered = (
            render_report_json(report)
            if args.emit == "json"
            else render_report_markdown(report)
        )
        if len(rendered.encode("utf-8")) > request.limits.max_output_bytes:
            sys.stdout.write(
                _error_payload(
                    "incomplete",
                    "output_limit_exceeded",
                    "rendered report exceeds request.limits.max_output_bytes",
                )
            )
            return int(ExitCode.INCOMPLETE)
        sys.stdout.write(rendered)
        return int(report.exit_code)
    except ContractValidationError as exc:
        sys.stdout.write(_error_payload("invalid", "contract_validation", str(exc)))
        return int(ExitCode.INVALID_INPUT)
    except OSError as exc:
        sys.stdout.write(_error_payload("incomplete", "input_unavailable", str(exc)))
        return int(ExitCode.INCOMPLETE)


if __name__ == "__main__":
    raise SystemExit(main())
