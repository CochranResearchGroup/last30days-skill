#!/usr/bin/env python3
"""User-scoped last30days intelligence service and operator client."""

from __future__ import annotations

import argparse
import json
import os
import signal
import sys
import threading
from pathlib import Path

from lib import service_contracts as contracts
from lib.service_app import initialize_application
from lib.service_client import ServiceClient, ServiceClientError
from lib.service_http import ServiceAlreadyRunningError, UnixServiceServer
from lib.service_retrieval import HybridRetriever


def _default_socket_path() -> Path:
    override = os.getenv("LAST30DAYS_SERVICE_SOCKET")
    if override:
        return Path(override).expanduser()
    runtime_root = os.getenv("XDG_RUNTIME_DIR")
    if not runtime_root:
        candidate = Path("/run/user") / str(os.geteuid())
        if candidate.is_dir():
            runtime_root = str(candidate)
    if not runtime_root:
        raise RuntimeError(
            "XDG_RUNTIME_DIR or LAST30DAYS_SERVICE_SOCKET is required"
        )
    return Path(runtime_root) / "last30days" / "service.sock"


def _default_db_path() -> Path:
    override = os.getenv("LAST30DAYS_SERVICE_DB")
    if override:
        return Path(override).expanduser()
    data_root = os.getenv("XDG_DATA_HOME")
    if data_root:
        return Path(data_root) / "last30days" / "research.db"
    return Path.home() / ".local" / "share" / "last30days" / "research.db"


def _prepare_private_data_path(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(db_path.parent, 0o700)


def _serve(args: argparse.Namespace) -> int:
    socket_path = Path(args.socket) if args.socket else _default_socket_path()
    db_path = Path(args.db) if args.db else _default_db_path()
    os.umask(0o077)
    _prepare_private_data_path(db_path)
    retriever = HybridRetriever(db_path)
    retriever.initialize()
    retriever.index_legacy_findings()
    os.chmod(db_path, 0o600)
    application = initialize_application(db_path, retriever)
    server = UnixServiceServer(socket_path, application)
    stop_event = threading.Event()

    def request_shutdown(signum, frame):
        del signum, frame
        stop_event.set()

    previous_sigterm = signal.signal(signal.SIGTERM, request_shutdown)
    previous_sigint = signal.signal(signal.SIGINT, request_shutdown)
    thread = threading.Thread(
        target=server.serve_forever,
        name="last30days-service",
        daemon=True,
    )
    thread.start()
    try:
        while not stop_event.wait(0.2):
            if not thread.is_alive():
                raise RuntimeError("service listener stopped unexpectedly")
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
        signal.signal(signal.SIGTERM, previous_sigterm)
        signal.signal(signal.SIGINT, previous_sigint)
    return 0


def _status(args: argparse.Namespace) -> int:
    socket_path = Path(args.socket) if args.socket else _default_socket_path()
    client = ServiceClient(socket_path, timeout=args.timeout)
    try:
        payload = client.service_info().to_dict()
    except ServiceClientError as exc:
        print(
            json.dumps(
                {
                    "status": "unavailable",
                    "message": str(exc),
                },
                sort_keys=True,
            )
        )
        return 1
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def _query(args: argparse.Namespace) -> int:
    request = contracts.QueryRequest.from_dict(
        {
            "schema_version": contracts.SCHEMA_VERSION,
            "request_id": args.request_id,
            "profile_id": args.profile,
            "query": args.query,
            "freshness_policy": args.freshness,
            "response_mode": args.response_mode,
            "filters": {"sources": args.source} if args.source else {},
            "top_k": args.top_k,
            "max_chars": args.max_chars,
            "wait_ms": args.wait_ms,
        }
    )
    socket_path = Path(args.socket) if args.socket else _default_socket_path()
    client = ServiceClient(socket_path, timeout=args.timeout)
    try:
        response = client.query(request)
    except ServiceClientError as exc:
        print(json.dumps({"status": "error", "message": str(exc)}, sort_keys=True))
        return 1
    print(json.dumps(response.to_dict(), indent=2, sort_keys=True))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run or query the local last30days intelligence service"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    serve = subparsers.add_parser("serve", help="Run the user-scoped service")
    serve.add_argument("--socket")
    serve.add_argument("--db")
    serve.set_defaults(handler=_serve)

    status = subparsers.add_parser("status", help="Read service capabilities")
    status.add_argument("--socket")
    status.add_argument("--timeout", type=float, default=2.0)
    status.set_defaults(handler=_status)

    query = subparsers.add_parser("query", help="Query cached intelligence")
    query.add_argument("query")
    query.add_argument("--socket")
    query.add_argument("--request-id", default="cli-query")
    query.add_argument("--profile", default="default")
    query.add_argument(
        "--freshness",
        choices=[item.value for item in contracts.FreshnessPolicy],
        default=contracts.FreshnessPolicy.PREFER_CACHE.value,
    )
    query.add_argument(
        "--response-mode",
        choices=[item.value for item in contracts.ResponseMode],
        default=contracts.ResponseMode.EVIDENCE.value,
    )
    query.add_argument("--source", action="append")
    query.add_argument("--top-k", type=int, default=8)
    query.add_argument("--max-chars", type=int, default=8192)
    query.add_argument("--wait-ms", type=int, default=0)
    query.add_argument("--timeout", type=float, default=5.0)
    query.set_defaults(handler=_query)

    return parser


def main() -> int:
    try:
        args = build_parser().parse_args()
        return args.handler(args)
    except ServiceAlreadyRunningError:
        print("last30days service is already running", file=sys.stderr)
        return 3
    except (contracts.ContractValidationError, RuntimeError) as exc:
        print(f"last30days service error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
