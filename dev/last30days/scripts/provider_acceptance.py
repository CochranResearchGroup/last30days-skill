#!/usr/bin/env python3
"""Run or independently verify WI-010's provider-free P0-P3 campaign."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dev.last30days.provider_acceptance import (  # noqa: E402
    AcceptanceDependencies,
    CampaignSpec,
    ExecutionGrant,
    default_catalog,
    execute,
    prepare,
    verify,
)
from dev.last30days.provider_acceptance.browser_tracer import BrowserTracer  # noqa: E402
from dev.last30days.provider_acceptance.campaign import receipt_from_dict  # noqa: E402
from dev.last30days.provider_acceptance.command_tracer import CommandTracer  # noqa: E402
from dev.last30days.provider_acceptance.http_tracer import HttpTracer  # noqa: E402
from dev.last30days.provider_acceptance.isolated_join import IsolatedServiceJoin  # noqa: E402


def _plan():
    catalog = default_catalog()
    spec = CampaignSpec("wi010-provider-free-p0-p3", tuple(case.case_id for case in catalog.cases))
    return prepare(spec, catalog=catalog, repo_root=ROOT)


def _dependencies() -> AcceptanceDependencies:
    return AcceptanceDependencies(
        {
            "http": HttpTracer(ROOT),
            "command": CommandTracer(ROOT),
            "browser": BrowserTracer(ROOT),
        },
        IsolatedServiceJoin(),
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    run = subparsers.add_parser("run", help="execute the provider-free campaign")
    run.add_argument("--output", type=Path, required=True)
    check = subparsers.add_parser("verify", help="verify a receipt without transport")
    check.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args(argv)
    plan = _plan()
    if args.command == "run":
        receipt = execute(plan, grant=ExecutionGrant.for_plan(plan), deps=_dependencies(), repo_root=ROOT)
        verdict = verify(receipt, plan=plan)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(receipt.to_dict(), indent=2, sort_keys=True) + "\n")
    else:
        receipt = receipt_from_dict(json.loads(args.receipt.read_text()))
        verdict = verify(receipt, plan=plan)
    print(json.dumps({"accepted": verdict.accepted, "safe_reason_codes": verdict.safe_reason_codes, "verified_samples": verdict.verified_samples, "expected_samples": verdict.expected_samples}, sort_keys=True))
    return 0 if verdict.accepted else 1


if __name__ == "__main__":
    raise SystemExit(main())
