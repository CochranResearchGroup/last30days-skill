#!/usr/bin/env python3
"""Audit or verify WI-010's provider-free P4 capability matrix."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dev.last30days.provider_acceptance.readiness import (  # noqa: E402
    audit_capabilities,
    receipt_from_dict,
    verify_audit_receipt,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    audit = commands.add_parser("audit", help="execute the effect-free capability audit")
    audit.add_argument("--output", type=Path, required=True)
    verify = commands.add_parser("verify", help="verify a retained audit receipt")
    verify.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args(argv)

    if args.command == "audit":
        if args.output.exists():
            parser.error(f"receipt already exists: {args.output}")
        receipt = audit_capabilities(repo_root=ROOT)
        accepted, reasons = verify_audit_receipt(receipt, repo_root=ROOT)
        if not accepted:
            print(
                json.dumps(
                    {
                        "accepted": False,
                        "state": receipt.state,
                        "safe_reason_codes": reasons,
                    },
                    sort_keys=True,
                )
            )
            return 1
        args.output.parent.mkdir(parents=True, exist_ok=True)
        try:
            with args.output.open("x", encoding="utf-8") as output:
                json.dump(receipt.to_dict(), output, indent=2, sort_keys=True)
                output.write("\n")
        except FileExistsError:
            parser.error(f"receipt already exists: {args.output}")
    else:
        receipt = receipt_from_dict(json.loads(args.receipt.read_text(encoding="utf-8")))
        accepted, reasons = verify_audit_receipt(receipt, repo_root=ROOT)

    print(
        json.dumps(
            {
                "accepted": accepted,
                "state": receipt.state,
                "capabilities": len(receipt.capabilities),
                "eligible": len(receipt.eligible_case_ids),
                "safe_reason_codes": reasons,
                "next_gate": receipt.next_gate,
            },
            sort_keys=True,
        )
    )
    return 0 if accepted else 1


if __name__ == "__main__":
    raise SystemExit(main())
