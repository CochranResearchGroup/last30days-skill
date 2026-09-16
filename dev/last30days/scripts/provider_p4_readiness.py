#!/usr/bin/env python3
"""Prepare, execute, or verify WI-010's one-shot X P4 readiness probe."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dev.last30days.provider_acceptance.p4_readiness import (  # noqa: E402
    execute_x_readiness,
    packet_from_dict,
    prepare_x_packet,
    receipt_from_dict,
    verify_receipt,
)


def _exclusive_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("x", encoding="utf-8") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
            stream.write("\n")
    except FileExistsError as exc:
        raise SystemExit(f"output already exists: {path}") from exc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    prepare = commands.add_parser("prepare")
    prepare.add_argument("--target-config", type=Path, required=True)
    prepare.add_argument("--output", type=Path, required=True)
    execute = commands.add_parser("execute")
    execute.add_argument("--packet", type=Path, required=True)
    execute.add_argument("--target-config", type=Path, required=True)
    execute.add_argument("--output", type=Path, required=True)
    verify = commands.add_parser("verify")
    verify.add_argument("--packet", type=Path, required=True)
    verify.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args(argv)

    if args.command == "prepare":
        packet = prepare_x_packet(
            target_config_path=args.target_config,
            repo_root=ROOT,
        )
        _exclusive_json(args.output, packet.to_dict())
        print(json.dumps({"prepared": True, "case_id": packet.plan.case_id}))
        return 0

    packet = packet_from_dict(json.loads(args.packet.read_text(encoding="utf-8")))
    if args.command == "execute":
        receipt = execute_x_readiness(
            packet,
            target_config_path=args.target_config,
            repo_root=ROOT,
        )
        _exclusive_json(args.output, receipt.to_dict())
    else:
        receipt = receipt_from_dict(
            json.loads(args.receipt.read_text(encoding="utf-8"))
        )
    verified, reasons = verify_receipt(receipt, packet, repo_root=ROOT)
    print(
        json.dumps(
            {
                "verified": verified,
                "state": receipt.state,
                "safe_reason_code": receipt.safe_reason_code,
                "teardown_completed": receipt.teardown_completed,
                "safe_reason_codes": reasons,
            },
            sort_keys=True,
        )
    )
    if not verified:
        return 1
    if args.command == "execute" and receipt.state != "READY":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
