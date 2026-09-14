"""Read-only WI-007 preflight/report and an explicit disposable drill command."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path

from hotfix_runtime_drill import SCENARIOS, DrillError, preflight, report, run_drill


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("preflight", "drill"):
        command = commands.add_parser(name)
        command.add_argument("--source-root", type=Path, required=True)
        command.add_argument("--source-commit", required=True)
        command.add_argument("--previous-commit", required=True)
        if name == "drill":
            command.add_argument(
                "--output",
                type=Path,
                required=True,
                help="New JSON receipt file; existing files are never overwritten",
            )
    commands.add_parser("report").add_argument("receipt", type=Path)
    args = parser.parse_args(argv)
    output_fd = None
    parent = None
    result = None
    status = 0
    try:
        if args.command == "report":
            if args.receipt.stat().st_size > 1_000_000:
                raise DrillError("receipt_too_large")
            result = report(json.loads(args.receipt.read_text()))
        else:
            result = preflight(
                args.source_root, args.source_commit, args.previous_commit
            )
            if args.command == "drill":
                output = args.output.absolute()
                if output.suffix != ".json" or any(
                    p.is_symlink() for p in (output, *output.parents)
                ):
                    raise DrillError("unsafe_receipt_path")
                output_fd = os.open(
                    output, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600
                )
                parent = Path(tempfile.mkdtemp(prefix="wi007-drill-"))
                result = run_drill(
                    args.source_root,
                    args.source_commit,
                    args.previous_commit,
                    parent=parent,
                    scenarios=SCENARIOS,
                )
                report(result)
    except (DrillError, OSError, ValueError) as error:
        status = 1
        result = getattr(error, "receipt", None) or {
            "status": "failed",
            "error": str(error),
        }
    finally:
        if parent is not None and not any(parent.iterdir()):
            parent.rmdir()
        if output_fd is not None:
            with os.fdopen(output_fd, "w") as handle:
                json.dump(result, handle, indent=2, sort_keys=True)
                handle.write("\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return status


if __name__ == "__main__":
    raise SystemExit(main())
