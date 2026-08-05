#!/usr/bin/env python3
"""User-scoped last30days intelligence service and operator client."""

from __future__ import annotations

import argparse
import json
import os
import signal
import shutil
import sys
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path

from lib import service_contracts as contracts
from lib.service_app import initialize_application
from lib.service_client import ServiceClient, ServiceClientError
from lib.service_collection import CollectionSpec, CollectionSpecValidationError
from lib.service_enrichment import EnrichmentService
from lib.service_http import ServiceAlreadyRunningError, UnixServiceServer
from lib.service_graphiti import GraphitiHTTPSink
from lib.service_intelligence import (
    AdapterFailure,
    CodexAppServerClient,
    GitBranchManager,
    GitWorktreeTestExecutor,
    IntelligenceLedger,
    MaintenancePolicy,
    RepairSupervisor,
    StructuredIntelligenceWorkers,
)
from lib.service_intelligence_contracts import ContentAssessmentWorker
from lib.service_retrieval import HybridRetriever, LocalHashEmbeddingProvider
from lib.service_knowledge import GraphProjectionWorker
from lib.service_runtime import (
    AcquisitionLoop,
    AssessmentLoop,
    EnrichmentLoop,
    GraphProjectionLoop,
    build_acquisition_runtime,
)
from lib.service_tick import TickConfigError, TickCoordinator
from lib.service_tick_runtime import build_tick_runtime, default_tick_config_path


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
    embedding_provider = LocalHashEmbeddingProvider()
    retriever = HybridRetriever(db_path, embedding_provider=embedding_provider)
    retriever.initialize()
    retriever.index_legacy_findings()
    os.chmod(db_path, 0o600)
    acquisition = build_acquisition_runtime(db_path, retriever)
    acquisition_loop = AcquisitionLoop(
        acquisition.runner,
        due_scheduler=acquisition.collection_coordinator,
    )
    assessment_loop = None
    assessment_enabled = os.getenv(
        "LAST30DAYS_APP_INTELLIGENCE_ASSESSMENT", ""
    ).strip().casefold() in {
        "1",
        "true",
        "yes",
        "on",
    }
    if assessment_enabled:
        assessment_loop = AssessmentLoop(
            ContentAssessmentWorker(
                acquisition.assessment_queue,
                CodexAppServerClient(
                    codex_path=os.getenv("LAST30DAYS_CODEX_PATH", "codex"),
                    timeout_seconds=min(
                        60.0,
                        float(
                            os.getenv(
                                "LAST30DAYS_APP_INTELLIGENCE_TIMEOUT",
                                "60",
                            )
                        ),
                    ),
                ),
                cwd=Path(__file__).resolve().parent,
                model=os.getenv("LAST30DAYS_APP_INTELLIGENCE_MODEL") or None,
            )
        )
    enrichment_loop = EnrichmentLoop(
        EnrichmentService(
            db_path,
            embedding_provider=embedding_provider,
            extractor_version="generic-entities-v1",
            generic_entity_extraction=True,
            relationship_predicates=(
                "acquired",
                "announced",
                "built",
                "created",
                "integrates",
                "maintains",
                "released",
                "supports",
                "uses",
            ),
        ),
        retriever,
    )
    graph_url = os.getenv("LAST30DAYS_GRAPHITI_URL", "").strip()
    graph_loop = None
    if graph_url:
        graph_loop = GraphProjectionLoop(
            GraphProjectionWorker(
                db_path,
                GraphitiHTTPSink(
                    graph_url,
                    group_prefix=os.getenv(
                        "LAST30DAYS_GRAPHITI_GROUP_PREFIX", "last30days"
                    ),
                    timeout_seconds=min(
                        60.0,
                        float(
                            os.getenv(
                                "LAST30DAYS_GRAPHITI_TIMEOUT_SECONDS", "10"
                            )
                        ),
                    ),
                ),
            ),
            interval_seconds=max(
                1.0,
                float(
                    os.getenv(
                        "LAST30DAYS_GRAPHITI_INTERVAL_SECONDS", "30"
                    )
                ),
            ),
        )
    codex_path = os.getenv("LAST30DAYS_CODEX_PATH", "codex")
    application = initialize_application(
        db_path,
        retriever,
        refresh_scheduler=acquisition.scheduler,
        job_reader=acquisition.supervisor,
        acquisition_sources=acquisition.sources,
        acquisition_readiness=acquisition.source_readiness,
        recurring_collection=True,
        assessment_processing=assessment_enabled,
        collection_coordinator=acquisition.collection_coordinator,
        graph_projection_enabled=graph_loop is not None,
        maintenance_enabled=bool(shutil.which(codex_path)),
        runtime_error=lambda: (
            acquisition_loop.last_error_code
            or enrichment_loop.last_error_code
            or (assessment_loop.last_error_code if assessment_loop else None)
            or (graph_loop.last_error_code if graph_loop else None)
        ),
    )
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
    acquisition_loop.start()
    enrichment_loop.start()
    if assessment_loop is not None:
        assessment_loop.start()
    if graph_loop is not None:
        graph_loop.start()
    try:
        while not stop_event.wait(0.2):
            if not thread.is_alive():
                raise RuntimeError("service listener stopped unexpectedly")
    finally:
        if graph_loop is not None:
            graph_loop.stop(timeout=5)
        if assessment_loop is not None:
            assessment_loop.stop(timeout=5)
        enrichment_loop.stop(timeout=5)
        acquisition_loop.stop(timeout=5)
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
            "request_id": args.request_id or f"cli-{uuid.uuid4()}",
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


def _job(args: argparse.Namespace) -> int:
    socket_path = Path(args.socket) if args.socket else _default_socket_path()
    client = ServiceClient(socket_path, timeout=args.timeout)
    try:
        job = (
            client.resume_job(args.job_id)
            if args.resume
            else client.job(args.job_id)
        )
    except ServiceClientError as exc:
        print(json.dumps({"status": "error", "message": str(exc)}, sort_keys=True))
        return 1
    print(json.dumps(job.to_dict(), indent=2, sort_keys=True))
    return 0


def _collection_coordinator(args: argparse.Namespace):
    db_path = Path(args.db) if args.db else _default_db_path()
    _prepare_private_data_path(db_path)
    retriever = HybridRetriever(db_path)
    return build_acquisition_runtime(db_path, retriever).collection_coordinator


def _collection(args: argparse.Namespace) -> int:
    coordinator = _collection_coordinator(args)
    if args.collection_action == "put":
        try:
            payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise RuntimeError(
                "collection spec must be a readable JSON file"
            ) from exc
        if not isinstance(payload, dict):
            raise RuntimeError("collection spec must be a JSON object")
        spec = CollectionSpec.from_dict(payload)
        response: object = coordinator.put_spec(spec).to_dict()
    elif args.collection_action == "list":
        response = {
            "schema_version": contracts.SCHEMA_VERSION,
            "collections": coordinator.list_specs(),
        }
    elif args.collection_action in {"pause", "resume"}:
        response = coordinator.set_enabled(
            args.collection_spec_id,
            enabled=args.collection_action == "resume",
        ).to_dict()
    else:
        scheduled_for = args.scheduled_for or datetime.now(
            timezone.utc
        ).isoformat().replace("+00:00", "Z")
        response = coordinator.enqueue_interval(
            args.collection_spec_id,
            scheduled_for=scheduled_for,
            trigger="manual",
            max_attempts=args.max_attempts,
        ).to_dict()
    print(json.dumps(response, indent=2, sort_keys=True))
    return 0


def _tick(args: argparse.Namespace) -> int:
    db_path = Path(args.db) if args.db else _default_db_path()
    config_path = Path(args.config) if args.config else default_tick_config_path()
    _prepare_private_data_path(db_path)
    if args.tick_action == "get":
        coordinator = TickCoordinator(db_path, config_path=config_path)
        response = coordinator.get_tick(args.tick_id)
        payload = response.to_dict()
    elif args.tick_action == "enqueue":
        runtime = build_tick_runtime(db_path, config_path=config_path)
        response = runtime.coordinator.enqueue_tick(
            contracts.TickRequest.from_dict(
                {
                    "schema_version": contracts.SCHEMA_VERSION,
                    "schedule_id": args.schedule_id,
                    "interval_from": args.interval_from,
                    "interval_to": args.interval_to,
                    "trigger": "manual",
                }
            )
        )
        payload = response.to_dict()
    else:
        runtime = build_tick_runtime(db_path, config_path=config_path)
        incidents = runtime.runner.incidents
        if args.incident_action == "get":
            payload = incidents.get(args.incident_id).to_dict()
        elif args.incident_action == "acknowledge":
            payload = incidents.acknowledge(
                args.incident_id,
                actor_ref=args.actor_ref,
            ).to_dict()
        else:
            payload = {
                "incident_id": args.incident_id,
                "public_operator_url": incidents.request_observation(
                    args.incident_id,
                    public_operator_url=args.operator_url,
                ),
            }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def _intelligence(args: argparse.Namespace) -> int:
    db_path = Path(args.db) if args.db else _default_db_path()
    input_path = Path(args.input).resolve()
    if not input_path.is_file():
        raise RuntimeError("intelligence input file does not exist")
    try:
        payload = json.loads(input_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError("intelligence input must be a readable JSON file") from exc
    client = CodexAppServerClient(
        codex_path=args.codex,
        timeout_seconds=args.timeout,
    )
    workers = StructuredIntelligenceWorkers(
        IntelligenceLedger(db_path),
        client,
        cwd=Path(args.cwd).resolve(),
        model=args.model,
        max_calls_per_job_loop=args.max_calls,
        max_input_bytes=args.max_input_bytes,
        reserved_cost_cents_per_call=args.reserved_cost_cents,
        cost_budget_cents=args.cost_budget_cents,
    )
    decision = (
        workers.enrich(job_id=args.job_id, input_payload=payload)
        if args.mode == "enrich"
        else workers.evaluate(job_id=args.job_id, input_payload=payload)
    )
    print(
        json.dumps(
            {
                "decision_id": decision.decision_id,
                "accepted": decision.accepted,
                "validator_errors": list(decision.validator_errors),
                "input_ref": decision.input_ref,
                "output_ref": decision.output_ref,
                "event_stream_ref": decision.event_stream_ref,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if decision.accepted else 4


def _maintenance_policy(path: str) -> MaintenancePolicy:
    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError("maintenance policy must be a readable JSON file") from exc
    if not isinstance(payload, dict):
        raise RuntimeError("maintenance policy must be an object")
    expected = {
        "repeated_failure_threshold",
        "max_investigation_attempts",
        "max_rework",
        "max_branches",
        "allowed_write_roots",
        "allowed_tests",
        "allowed_approvers",
        "max_model_calls_per_job_loop",
        "wall_timeout_seconds",
        "max_input_bytes",
        "reserved_cost_cents_per_call",
        "cost_budget_cents",
    }
    if set(payload) != expected:
        raise RuntimeError("maintenance policy fields are invalid")
    for field in ("allowed_write_roots", "allowed_tests", "allowed_approvers"):
        if not isinstance(payload[field], list):
            raise RuntimeError("maintenance policy allowlists must be arrays")
        payload[field] = tuple(payload[field])
    return MaintenancePolicy(**payload)


def _repair(args: argparse.Namespace) -> int:
    db_path = Path(args.db) if args.db else _default_db_path()
    cwd = Path(args.cwd).resolve()
    policy = _maintenance_policy(args.policy)
    supervisor = RepairSupervisor(
        IntelligenceLedger(db_path),
        CodexAppServerClient(
            codex_path=args.codex,
            timeout_seconds=min(args.timeout, policy.wall_timeout_seconds),
        ),
        policy,
        cwd=cwd,
        branch_manager=GitBranchManager(cwd=cwd),
        test_executor=GitWorktreeTestExecutor(
            timeout_seconds=args.test_timeout,
        ),
        model=args.model,
    )
    if args.repair_action == "investigate":
        result = supervisor.investigate(
            AdapterFailure(
                job_id=args.job_id,
                adapter=args.adapter,
                failure_fingerprint=args.failure_fingerprint,
                occurrences=args.occurrences,
                evidence_ids=tuple(args.evidence_id),
                diagnostic_refs=tuple(args.diagnostic_ref),
            )
        )
        branch = None
        if result.accepted and args.parent_branch:
            branch = supervisor.prepare_branch(
                result.run_id,
                parent_branch=args.parent_branch,
            )
        payload = {
            "run_id": result.run_id,
            "decision_id": result.decision_id,
            "accepted": result.accepted,
            "validator_errors": list(result.validator_errors),
            "recommendation_ref": result.recommendation_ref,
            "branch": branch,
        }
        code = 0 if result.accepted else 4
    else:
        evaluation = supervisor.evaluate(args.run_id, commands=tuple(args.test))
        payload = {
            "run_id": args.run_id,
            "eval_id": evaluation.eval_id,
            "passed": evaluation.passed,
            "artifact_ref": evaluation.artifact_ref,
        }
        code = 0 if evaluation.passed else 4
    print(json.dumps(payload, indent=2, sort_keys=True))
    return code


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
    query.add_argument(
        "--request-id",
        help="Caller-supplied idempotency key; generated when omitted",
    )
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

    job = subparsers.add_parser("job", help="Poll a durable refresh job")
    job.add_argument("job_id")
    job.add_argument(
        "--resume",
        action="store_true",
        help="Resume one awaiting-operator job after the human gate clears",
    )
    job.add_argument("--socket")
    job.add_argument("--timeout", type=float, default=5.0)
    job.set_defaults(handler=_job)

    collection = subparsers.add_parser(
        "collection",
        help="Configure or inspect governed recurring collection",
    )
    collection_subparsers = collection.add_subparsers(
        dest="collection_action", required=True
    )
    collection_put = collection_subparsers.add_parser(
        "put", help="Create or revise a collection spec from strict JSON"
    )
    collection_put.add_argument("--input", required=True)
    collection_put.add_argument("--db")
    collection_put.set_defaults(handler=_collection)
    collection_list = collection_subparsers.add_parser(
        "list", help="List collection specs and timer status"
    )
    collection_list.add_argument("--db")
    collection_list.set_defaults(handler=_collection)
    for action in ("pause", "resume"):
        command = collection_subparsers.add_parser(action)
        command.add_argument("collection_spec_id")
        command.add_argument("--db")
        command.set_defaults(handler=_collection)
    collection_run = collection_subparsers.add_parser(
        "run", help="Enqueue one manual interval through timer deduplication"
    )
    collection_run.add_argument("collection_spec_id")
    collection_run.add_argument("--scheduled-for")
    collection_run.add_argument("--max-attempts", type=int, choices=(1, 2))
    collection_run.add_argument("--db")
    collection_run.set_defaults(handler=_collection)

    tick = subparsers.add_parser(
        "tick",
        help="Run or inspect one durable manual all-source tick",
    )
    tick_subparsers = tick.add_subparsers(dest="tick_action", required=True)
    tick_enqueue = tick_subparsers.add_parser(
        "enqueue",
        help="Execute one explicit UTC interval; does not create a timer",
    )
    tick_enqueue.add_argument("--interval-from", required=True)
    tick_enqueue.add_argument("--interval-to", required=True)
    tick_enqueue.add_argument("--schedule-id", default="manual-default")
    tick_enqueue.add_argument("--config")
    tick_enqueue.add_argument("--db")
    tick_enqueue.set_defaults(handler=_tick)
    tick_get = tick_subparsers.add_parser("get", help="Read one durable tick receipt")
    tick_get.add_argument("tick_id")
    tick_get.add_argument("--config")
    tick_get.add_argument("--db")
    tick_get.set_defaults(handler=_tick)
    tick_incident = tick_subparsers.add_parser(
        "incident",
        help="Read or explicitly advance a persisted human incident gate",
    )
    incident_subparsers = tick_incident.add_subparsers(
        dest="incident_action",
        required=True,
    )
    for action in ("get", "acknowledge", "observe"):
        command = incident_subparsers.add_parser(action)
        command.add_argument("incident_id")
        command.add_argument("--config")
        command.add_argument("--db")
        command.set_defaults(handler=_tick)
    incident_subparsers.choices["acknowledge"].add_argument(
        "--actor-ref",
        required=True,
    )
    incident_subparsers.choices["observe"].add_argument(
        "--operator-url",
        required=True,
        help="Direct external agent-browser Guacamole HTTPS URL",
    )

    intelligence = subparsers.add_parser(
        "intelligence",
        help="Run one operator-owned bounded enrichment or evaluation turn",
    )
    intelligence.add_argument("mode", choices=("enrich", "evaluate"))
    intelligence.add_argument("--job-id", required=True)
    intelligence.add_argument("--input", required=True)
    intelligence.add_argument("--db")
    intelligence.add_argument("--cwd", default=os.getcwd())
    intelligence.add_argument("--codex", default="codex")
    intelligence.add_argument("--model")
    intelligence.add_argument("--timeout", type=float, default=300)
    intelligence.add_argument("--max-calls", type=int, default=1)
    intelligence.add_argument("--max-input-bytes", type=int, default=65_536)
    intelligence.add_argument("--reserved-cost-cents", type=int, default=1)
    intelligence.add_argument("--cost-budget-cents", type=int, default=1)
    intelligence.set_defaults(handler=_intelligence)

    repair = subparsers.add_parser(
        "repair",
        help="Run the operator-owned bounded adapter-repair supervisor",
    )
    repair_subparsers = repair.add_subparsers(dest="repair_action", required=True)
    for action in ("investigate", "evaluate"):
        command = repair_subparsers.add_parser(action)
        command.add_argument("--policy", required=True)
        command.add_argument("--db")
        command.add_argument("--cwd", default=os.getcwd())
        command.add_argument("--codex", default="codex")
        command.add_argument("--model")
        command.add_argument("--timeout", type=float, default=300)
        command.add_argument("--test-timeout", type=int, default=600)
        command.set_defaults(handler=_repair)
    investigate = repair_subparsers.choices["investigate"]
    investigate.add_argument("--job-id", required=True)
    investigate.add_argument("--adapter", required=True)
    investigate.add_argument("--failure-fingerprint", required=True)
    investigate.add_argument("--occurrences", type=int, required=True)
    investigate.add_argument("--evidence-id", action="append", default=[])
    investigate.add_argument("--diagnostic-ref", action="append", default=[])
    investigate.add_argument("--parent-branch")
    evaluate = repair_subparsers.choices["evaluate"]
    evaluate.add_argument("--run-id", required=True)
    evaluate.add_argument("--test", action="append", required=True)

    return parser


def main() -> int:
    try:
        args = build_parser().parse_args()
        return args.handler(args)
    except ServiceAlreadyRunningError:
        print("last30days service is already running", file=sys.stderr)
        return 3
    except (
        contracts.ContractValidationError,
        CollectionSpecValidationError,
        TickConfigError,
        RuntimeError,
    ) as exc:
        print(f"last30days service error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
