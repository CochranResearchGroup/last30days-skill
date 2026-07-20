#!/usr/bin/env python3
"""Companion YouTube media operations for the last30days agent skill."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(SCRIPT_DIR))

from lib import env, youtube_media  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit structured JSON")
    sub = parser.add_subparsers(dest="operation", required=True)
    sub.add_parser("doctor")
    subscriptions = sub.add_parser("subscriptions")
    subscriptions.add_argument("--limit", type=int, default=12)
    transcript = sub.add_parser("transcript")
    transcript.add_argument("url")
    transcript.add_argument("--output-dir", default=".")
    download = sub.add_parser("download")
    download.add_argument("url")
    download.add_argument("--output-dir", default=".")
    download.add_argument("--max-height", type=int, default=1080)
    return parser


def run(args: argparse.Namespace) -> dict:
    config = env.get_config()
    if args.operation == "doctor":
        return youtube_media.doctor(config)
    if args.operation == "subscriptions":
        return youtube_media.subscriptions(args.limit, config)
    if args.operation == "transcript":
        return youtube_media.transcript(args.url, args.output_dir, config)
    if args.operation == "download":
        return youtube_media.download(args.url, args.output_dir, args.max_height)
    raise AssertionError(args.operation)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = run(args)
    except (ValueError, OSError) as exc:
        result = {"ok": False, "error": type(exc).__name__, "detail": str(exc)}
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif result.get("ok"):
        if result.get("path"):
            print(result["path"])
        elif result.get("items") is not None:
            for item in result["items"]:
                print(f"{item.get('title', '')}\t{item.get('channel', '')}\t{item.get('url', '')}")
        else:
            print("ready")
    else:
        print(result.get("error") or result.get("youtube", {}).get("reason") or "not ready", file=sys.stderr)
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
