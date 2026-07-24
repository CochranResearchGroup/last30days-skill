"""Deterministic supervision for bounded stochastic intelligence workers."""

from __future__ import annotations

import hashlib
import json
import os
import re
import select
import shlex
import shutil
import sqlite3
import subprocess
import tempfile
import time
from collections.abc import Callable, Mapping, Sequence, Set
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Protocol

import store

from . import service_contracts as contracts


Clock = Callable[[], datetime]
_RUN_STATES = {
    "pending",
    "investigating",
    "recommended",
    "rejected",
    "branch_creating",
    "branch_ready",
    "evaluating",
    "evaluated",
    "evaluated_failed",
    "awaiting_approval",
    "approved",
}
_REPAIR_ACTIONS = {"apply_patch", "run_tests", "request_context", "stop_no_fix"}
_RISKS = {"low", "medium", "high"}
_GATED_ACTIONS = {"publish", "mutate_live_source_config"}
_CONTRACT_CATALOG = contracts.load_schema_catalog()["contracts"]
_MAX_WORKER_ITEMS = 64
_SECRET_VALUE = re.compile(
    r"(?i)(?:bearer\s+[a-z0-9._-]{12,}|"
    r"(?:api[_ -]?key|password|auth[_ -]?token|sessionid|cookie)\s*[:=]\s*\S+)"
)


def _strict_output_contract_schema(schema: Mapping[str, object]) -> dict[str, object]:
    """Translate canonical contracts to the app-server strict-output subset."""

    translated: dict[str, object] = {}
    for key, value in schema.items():
        if key in {"minLength", "maxLength", "pattern"}:
            continue
        if key == "const":
            translated["enum"] = [value]
            if isinstance(value, bool):
                translated["type"] = "boolean"
            elif isinstance(value, int):
                translated["type"] = "integer"
            elif isinstance(value, float):
                translated["type"] = "number"
            elif isinstance(value, str):
                translated["type"] = "string"
            continue
        if isinstance(value, Mapping):
            translated[key] = _strict_output_contract_schema(value)
        elif isinstance(value, list):
            translated[key] = [
                _strict_output_contract_schema(item)
                if isinstance(item, Mapping)
                else item
                for item in value
            ]
        else:
            translated[key] = value
    return translated


ENRICHMENT_OUTPUT_SCHEMA: dict[str, object] = {
    "type": "object",
    "required": [
        "action",
        "entity_proposals",
        "relationship_proposals",
        "confidence",
        "rationale",
        "evidence_ids",
    ],
    "additionalProperties": False,
    "properties": {
        "action": {"type": "string", "enum": ["propose_enrichment"]},
        "entity_proposals": {
            "type": "array",
            "items": _strict_output_contract_schema(
                _CONTRACT_CATALOG["entity_proposal"]
            ),
        },
        "relationship_proposals": {
            "type": "array",
            "items": _strict_output_contract_schema(
                _CONTRACT_CATALOG["relationship_proposal"]
            ),
        },
        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
        "rationale": {"type": "string"},
        "evidence_ids": {"type": "array", "items": {"type": "string"}},
    },
}

EVALUATION_OUTPUT_SCHEMA: dict[str, object] = {
    "type": "object",
    "required": [
        "action",
        "judgments",
        "confidence",
        "rationale",
        "evidence_ids",
    ],
    "additionalProperties": False,
    "properties": {
        "action": {"type": "string", "enum": ["record_judgments"]},
        "judgments": {
            "type": "array",
            "items": {
                "type": "object",
                "required": [
                    "case_id",
                    "document_id",
                    "relevance",
                    "evidence_ids",
                ],
                "additionalProperties": False,
                "properties": {
                    "case_id": {"type": "string"},
                    "document_id": {"type": "string"},
                    "relevance": {
                        "type": "integer",
                        "minimum": 0,
                        "maximum": 3,
                    },
                    "evidence_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                },
            },
        },
        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
        "rationale": {"type": "string"},
        "evidence_ids": {"type": "array", "items": {"type": "string"}},
    },
}

REPAIR_OUTPUT_SCHEMA: dict[str, object] = {
    "type": "object",
    "required": [
        "action",
        "confidence",
        "target_files",
        "risk",
        "rationale",
        "next_prompt",
    ],
    "additionalProperties": False,
    "properties": {
        "action": {"type": "string", "enum": sorted(_REPAIR_ACTIONS)},
        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
        "target_files": {"type": "array", "items": {"type": "string"}},
        "risk": {"type": "string", "enum": sorted(_RISKS)},
        "rationale": {"type": "string"},
        "next_prompt": {"type": ["string", "null"]},
    },
}


def _utc(clock: Clock) -> str:
    value = clock()
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("clock must return a timezone-aware datetime")
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _canonical(payload: object) -> tuple[str, str]:
    _reject_forbidden_fields(payload)
    try:
        encoded = json.dumps(
            payload,
            allow_nan=False,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )
    except (TypeError, ValueError) as exc:
        raise contracts.ContractValidationError(
            "intelligence artifact must contain valid JSON"
        ) from exc
    return encoded, hashlib.sha256(encoded.encode()).hexdigest()


def _validate_worker_input(
    loop_name: str,
    payload: object,
    *,
    max_input_bytes: int,
) -> tuple[str, frozenset[str]]:
    encoded, _ = _canonical(payload)
    if len(encoded.encode("utf-8")) > max_input_bytes:
        raise ValueError("worker input exceeds its byte limit")
    if _SECRET_VALUE.search(encoded):
        raise ValueError("worker input resembles credential or session material")
    if not isinstance(payload, Mapping):
        raise ValueError("worker input must be an object")
    expected = "chunks" if loop_name == "entity_relationship_enrichment" else "cases"
    if set(payload) != {expected}:
        raise ValueError(f"worker input must contain only {expected}")
    items = payload[expected]
    if not isinstance(items, list) or len(items) > _MAX_WORKER_ITEMS:
        raise ValueError("worker input item count is outside bounds")
    allowed = (
        {"chunk_id", "document_id", "text", "source_url", "content_hash"}
        if expected == "chunks"
        else {"case_id", "query", "expected_document_ids", "evidence_ids"}
    )
    identifiers: set[str] = set()
    for item in items:
        if not isinstance(item, Mapping) or not set(item) <= allowed:
            raise ValueError("worker input item schema is invalid")
        primary = "chunk_id" if expected == "chunks" else "case_id"
        value = item.get(primary)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"worker input item requires {primary}")
        for key, nested in item.items():
            if key.endswith("_id") and isinstance(nested, str) and nested.strip():
                identifiers.add(nested)
            elif key.endswith("_ids") and isinstance(nested, list):
                if any(
                    not isinstance(entry, str) or not entry.strip() for entry in nested
                ):
                    raise ValueError("worker evidence identifiers are invalid")
                identifiers.update(nested)
            elif key == "text" and (
                not isinstance(nested, str) or len(nested.encode("utf-8")) > 8192
            ):
                raise ValueError("worker evidence text is outside bounds")
    return encoded, frozenset(identifiers)


def _output_evidence_ids(loop_name: str, output: Mapping[str, object]) -> set[str]:
    top_level = output.get("evidence_ids", [])
    identifiers = (
        {item for item in top_level if isinstance(item, str)}
        if isinstance(top_level, list)
        else set()
    )
    collection = (
        output.get("entity_proposals", [])
        if loop_name == "entity_relationship_enrichment"
        else output.get("judgments", [])
    )
    if isinstance(collection, list):
        for item in collection:
            if not isinstance(item, Mapping):
                continue
            evidence_fields = (
                ("evidence_chunk_id", "document_id")
                if loop_name == "entity_relationship_enrichment"
                else ("case_id", "document_id", "evidence_ids")
            )
            for key in evidence_fields:
                value = item.get(key)
                if isinstance(value, str):
                    identifiers.add(value)
                elif isinstance(value, list):
                    identifiers.update(entry for entry in value if isinstance(entry, str))
    return identifiers


def _reject_forbidden_fields(value: object, path: str = "artifact") -> None:
    if isinstance(value, Mapping):
        for key, nested in value.items():
            normalized = str(key).strip().casefold().replace("-", "_")
            if normalized in contracts.FORBIDDEN_LEDGER_FIELDS:
                raise contracts.ContractValidationError(
                    f"forbidden field in intelligence artifact: {path}.{key}"
                )
            _reject_forbidden_fields(nested, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, nested in enumerate(value):
            _reject_forbidden_fields(nested, f"{path}[{index}]")


def _stable_id(prefix: str, payload: object) -> str:
    _, digest = _canonical(payload)
    return f"{prefix}-{digest[:24]}"


@dataclass(frozen=True)
class AppServerTurn:
    model_ref: str
    thread_id: str
    turn_id: str
    output: Mapping[str, object]
    events: Sequence[Mapping[str, object]]


class AppServerWorker(Protocol):
    def structured_turn(
        self,
        *,
        prompt: str,
        output_schema: Mapping[str, object],
        cwd: Path,
        model: str | None = None,
        thread_id: str | None = None,
    ) -> AppServerTurn: ...


@dataclass(frozen=True)
class WorkerDecision:
    decision_id: str
    accepted: bool
    validator_errors: tuple[str, ...]
    input_ref: str
    output_ref: str
    event_stream_ref: str


@dataclass(frozen=True)
class AdapterFailure:
    job_id: str
    adapter: str
    failure_fingerprint: str
    occurrences: int
    evidence_ids: tuple[str, ...]
    diagnostic_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        for field in (self.job_id, self.adapter, self.failure_fingerprint):
            if not isinstance(field, str) or not field.strip():
                raise ValueError("adapter failure fields must be non-empty")
        if self.occurrences < 1:
            raise ValueError("failure occurrences must be positive")


@dataclass(frozen=True)
class MaintenancePolicy:
    repeated_failure_threshold: int
    max_investigation_attempts: int
    max_rework: int
    max_branches: int
    allowed_write_roots: tuple[str, ...]
    allowed_tests: tuple[str, ...]
    allowed_approvers: tuple[str, ...]
    max_model_calls_per_job_loop: int = 2
    wall_timeout_seconds: int = 300
    max_input_bytes: int = 65_536
    reserved_cost_cents_per_call: int = 1
    cost_budget_cents: int = 2

    def __post_init__(self) -> None:
        if not 2 <= self.repeated_failure_threshold <= 100:
            raise ValueError("repeated failure threshold must be between 2 and 100")
        if not 1 <= self.max_investigation_attempts <= 5:
            raise ValueError("investigation attempts must be between 1 and 5")
        if not 0 <= self.max_rework <= 3:
            raise ValueError("max rework must be between 0 and 3")
        if not 0 <= self.max_branches <= 3:
            raise ValueError("max branches must be between 0 and 3")
        if not 1 <= self.max_model_calls_per_job_loop <= 5:
            raise ValueError("model call limit must be between 1 and 5")
        if not 1 <= self.wall_timeout_seconds <= 1800:
            raise ValueError("wall timeout must be between 1 and 1800 seconds")
        if not 1024 <= self.max_input_bytes <= 1_048_576:
            raise ValueError("input byte limit must be between 1024 and 1048576")
        if not 1 <= self.reserved_cost_cents_per_call <= 10_000:
            raise ValueError("reserved call cost must be positive")
        if (
            self.cost_budget_cents < self.reserved_cost_cents_per_call
            or self.cost_budget_cents > 50_000
        ):
            raise ValueError("maintenance cost budget is outside bounds")
        for values in (
            self.allowed_write_roots,
            self.allowed_tests,
            self.allowed_approvers,
        ):
            if not values or any(
                not isinstance(value, str) or not value.strip() for value in values
            ):
                raise ValueError("maintenance allowlists must be non-empty")
        for root in self.allowed_write_roots:
            path = PurePosixPath(root)
            if path.is_absolute() or ".." in path.parts:
                raise ValueError("write roots must be safe repo-relative paths")

    def to_dict(self) -> dict[str, object]:
        return {
            "repeated_failure_threshold": self.repeated_failure_threshold,
            "max_investigation_attempts": self.max_investigation_attempts,
            "max_rework": self.max_rework,
            "max_branches": self.max_branches,
            "allowed_write_roots": list(self.allowed_write_roots),
            "allowed_tests": list(self.allowed_tests),
            "allowed_approvers": list(self.allowed_approvers),
            "max_model_calls_per_job_loop": self.max_model_calls_per_job_loop,
            "wall_timeout_seconds": self.wall_timeout_seconds,
            "max_input_bytes": self.max_input_bytes,
            "reserved_cost_cents_per_call": self.reserved_cost_cents_per_call,
            "cost_budget_cents": self.cost_budget_cents,
            "gated_actions": sorted(_GATED_ACTIONS),
        }


@dataclass(frozen=True)
class RepairResult:
    run_id: str
    decision_id: str
    accepted: bool
    validator_errors: tuple[str, ...]
    recommendation_ref: str


@dataclass(frozen=True)
class TestOutcome:
    __test__ = False

    command: str
    passed: bool
    metrics: Mapping[str, object]
    output: Mapping[str, object]


@dataclass(frozen=True)
class EvaluationResult:
    eval_id: str
    passed: bool
    artifact_ref: str


class BranchManager(Protocol):
    def create(self, run_id: str, parent_branch: str) -> str: ...


class TestExecutor(Protocol):
    def run(self, command: str, *, cwd: Path, branch: str) -> TestOutcome: ...


def _subprocess_environment() -> dict[str, str]:
    allowed = {
        "HOME",
        "PATH",
        "LANG",
        "LC_ALL",
        "XDG_CACHE_HOME",
        "XDG_CONFIG_HOME",
        "XDG_DATA_HOME",
        "XDG_STATE_HOME",
    }
    return {key: value for key, value in os.environ.items() if key in allowed}


class GitBranchManager:
    """Concrete branch creator; never checks out or modifies the operator tree."""

    def __init__(self, *, cwd: Path, git_path: str = "git", timeout_seconds: int = 30):
        self.cwd = Path(cwd).resolve()
        self.git_path = git_path
        self.timeout_seconds = timeout_seconds

    def create(self, run_id: str, parent_branch: str) -> str:
        if not re.fullmatch(r"repair-run-[a-f0-9]{24}", run_id):
            raise ValueError("maintenance run ID is invalid")
        branch = f"last30days-repair/{run_id.removeprefix('repair-run-')}"
        subprocess.run(
            [self.git_path, "check-ref-format", "--branch", parent_branch],
            cwd=self.cwd,
            env=_subprocess_environment(),
            check=True,
            capture_output=True,
            text=True,
            timeout=self.timeout_seconds,
        )
        subprocess.run(
            [self.git_path, "branch", branch, parent_branch],
            cwd=self.cwd,
            env=_subprocess_environment(),
            check=True,
            capture_output=True,
            text=True,
            timeout=self.timeout_seconds,
        )
        return branch


class GitWorktreeTestExecutor:
    """Runs an allowlisted argv command in a temporary detached worktree."""

    def __init__(
        self,
        *,
        git_path: str = "git",
        timeout_seconds: int = 600,
        state_root: Path | None = None,
    ):
        self.git_path = git_path
        self.timeout_seconds = timeout_seconds
        self.state_root = (
            Path(state_root)
            if state_root is not None
            else Path(
                os.getenv(
                    "XDG_STATE_HOME",
                    os.fspath(Path.home() / ".local" / "state"),
                )
            )
            / "last30days"
            / "repair-worktrees"
        )

    def run(self, command: str, *, cwd: Path, branch: str) -> TestOutcome:
        argv = shlex.split(command)
        if not argv:
            raise ValueError("test command is empty")
        self.state_root.mkdir(parents=True, exist_ok=True, mode=0o700)
        worktree = Path(tempfile.mkdtemp(prefix="run-", dir=self.state_root))
        added = False
        try:
            subprocess.run(
                [self.git_path, "worktree", "add", "--detach", os.fspath(worktree), branch],
                cwd=Path(cwd).resolve(),
                env=_subprocess_environment(),
                check=True,
                capture_output=True,
                text=True,
                timeout=30,
            )
            added = True
            completed = subprocess.run(
                argv,
                cwd=worktree,
                env=_subprocess_environment(),
                check=False,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
            )
            return TestOutcome(
                command=command,
                passed=completed.returncode == 0,
                metrics={"exit_code": completed.returncode},
                output={
                    "stdout_tail": completed.stdout[-4096:],
                    "stderr_tail": completed.stderr[-4096:],
                },
            )
        finally:
            if added:
                subprocess.run(
                    [self.git_path, "worktree", "remove", "--force", os.fspath(worktree)],
                    cwd=Path(cwd).resolve(),
                    env=_subprocess_environment(),
                    check=False,
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
            shutil.rmtree(worktree, ignore_errors=True)


class IntelligenceLedger:
    """SQLite authority for artifacts, calls, decisions, evals, and approvals."""

    def __init__(self, db_path: Path, *, clock: Clock | None = None):
        self.db_path = Path(db_path)
        self.clock = clock or (lambda: datetime.now(timezone.utc))
        store.init_db(self.db_path)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=5)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("PRAGMA busy_timeout=5000")
        return conn

    def put_artifact(
        self,
        payload: object,
        *,
        kind: str,
        media_type: str = "application/json",
    ) -> str:
        if not kind.strip() or not media_type.strip():
            raise ValueError("artifact metadata must be non-empty")
        payload_json, digest = _canonical(payload)
        artifact_ref = f"sha256:{digest}"
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute(
                """SELECT payload_sha256, payload_json
                   FROM service_ai_artifacts WHERE artifact_ref = ?""",
                (artifact_ref,),
            ).fetchone()
            if row is not None:
                if (
                    row["payload_sha256"] != digest
                    or row["payload_json"] != payload_json
                ):
                    raise RuntimeError("immutable artifact conflict")
            else:
                conn.execute(
                    """INSERT INTO service_ai_artifacts
                       (artifact_ref, artifact_kind, media_type, payload_json,
                        payload_sha256, created_at)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (
                        artifact_ref,
                        kind,
                        media_type,
                        payload_json,
                        digest,
                        _utc(self.clock),
                    ),
                )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
        return artifact_ref

    def get_artifact(self, artifact_ref: str) -> object:
        conn = self._connect()
        try:
            row = conn.execute(
                """SELECT payload_json, payload_sha256
                   FROM service_ai_artifacts WHERE artifact_ref = ?""",
                (artifact_ref,),
            ).fetchone()
        finally:
            conn.close()
        if row is None:
            raise KeyError("artifact not found")
        digest = hashlib.sha256(row["payload_json"].encode()).hexdigest()
        if digest != row["payload_sha256"] or artifact_ref != f"sha256:{digest}":
            raise RuntimeError("artifact integrity check failed")
        return json.loads(row["payload_json"])

    def record_model_call(
        self,
        *,
        job_id: str,
        loop_name: str,
        turn: AppServerTurn,
        input_ref: str,
        output_ref: str,
        event_stream_ref: str,
        status: str = "succeeded",
        error_code: str | None = None,
    ) -> str:
        call_payload = {
            "job_id": job_id,
            "loop_name": loop_name,
            "model_ref": turn.model_ref,
            "input_ref": input_ref,
            "output_ref": output_ref,
            "event_stream_ref": event_stream_ref,
            "thread_id": turn.thread_id,
            "turn_id": turn.turn_id,
        }
        call_id = _stable_id("model-call", call_payload)
        now = _utc(self.clock)
        conn = self._connect()
        try:
            conn.execute(
                """INSERT OR IGNORE INTO service_model_calls
                   (call_id, job_id, loop_name, model_ref, input_ref, output_ref,
                    event_stream_ref, thread_id, turn_id, status, error_code,
                    started_at, completed_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    call_id,
                    job_id,
                    loop_name,
                    turn.model_ref,
                    input_ref,
                    output_ref,
                    event_stream_ref,
                    turn.thread_id,
                    turn.turn_id,
                    status,
                    error_code,
                    now,
                    now,
                ),
            )
            conn.commit()
        finally:
            conn.close()
        return call_id

    def reserve_model_call(
        self,
        *,
        job_id: str,
        loop_name: str,
        input_ref: str,
        max_calls: int,
        reserved_cost_cents: int,
        cost_budget_cents: int,
    ) -> str:
        now = _utc(self.clock)
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            count = conn.execute(
                """SELECT COUNT(*) AS count FROM service_model_calls
                   WHERE job_id = ? AND loop_name = ?""",
                (job_id, loop_name),
            ).fetchone()["count"]
            if count >= max_calls or (count + 1) * reserved_cost_cents > cost_budget_cents:
                raise RuntimeError("model call bound or cost budget exhausted")
            call_id = _stable_id(
                "model-call",
                {
                    "job_id": job_id,
                    "loop_name": loop_name,
                    "input_ref": input_ref,
                    "ordinal": count + 1,
                },
            )
            conn.execute(
                """INSERT INTO service_model_calls
                   (call_id, job_id, loop_name, model_ref, input_ref, output_ref,
                    event_stream_ref, thread_id, turn_id, status, error_code,
                    started_at, completed_at)
                   VALUES (?, ?, ?, 'pending', ?, NULL, NULL, NULL, NULL,
                           'running', NULL, ?, NULL)""",
                (call_id, job_id, loop_name, input_ref, now),
            )
            conn.commit()
            return call_id
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def complete_model_call(
        self,
        call_id: str,
        *,
        turn: AppServerTurn,
        output_ref: str,
        event_stream_ref: str,
    ) -> None:
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            if conn.execute(
                """UPDATE service_model_calls
                   SET model_ref = ?, output_ref = ?, event_stream_ref = ?,
                       thread_id = ?, turn_id = ?, status = 'succeeded',
                       completed_at = ?
                   WHERE call_id = ? AND status = 'running'""",
                (
                    turn.model_ref,
                    output_ref,
                    event_stream_ref,
                    turn.thread_id,
                    turn.turn_id,
                    _utc(self.clock),
                    call_id,
                ),
            ).rowcount != 1:
                raise RuntimeError("model call reservation is not active")
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def fail_model_call(
        self,
        call_id: str,
        *,
        error_code: str,
        event_stream_ref: str,
    ) -> None:
        safe_code = re.sub(r"[^a-z0-9_.-]+", "_", error_code.casefold())[:64]
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            if conn.execute(
                """UPDATE service_model_calls
                   SET status = 'failed', error_code = ?, event_stream_ref = ?,
                       completed_at = ?
                   WHERE call_id = ? AND status = 'running'""",
                (
                    safe_code or "model_call_failed",
                    event_stream_ref,
                    _utc(self.clock),
                    call_id,
                ),
            ).rowcount != 1:
                raise RuntimeError("model call reservation is not active")
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def record_decision(
        self,
        *,
        job_id: str,
        loop_name: str,
        action: str,
        confidence: float,
        evidence_ids: Sequence[str],
        rationale: str,
        model_ref: str,
        input_ref: str,
        output_ref: str,
        accepted: bool,
        validator_errors: Sequence[str],
    ) -> contracts.DecisionRecord:
        seed = {
            "job_id": job_id,
            "loop_name": loop_name,
            "action": action,
            "input_ref": input_ref,
            "output_ref": output_ref,
        }
        decision = contracts.DecisionRecord.from_dict(
            {
                "schema_version": contracts.SCHEMA_VERSION,
                "decision_id": _stable_id("decision", seed),
                "job_id": job_id,
                "loop_name": loop_name,
                "action": action,
                "confidence": confidence,
                "evidence_ids": list(evidence_ids),
                "rationale": rationale or "No model rationale was accepted.",
                "model_ref": model_ref,
                "input_ref": input_ref,
                "output_ref": output_ref,
                "accepted": accepted,
                "validator_errors": list(validator_errors),
                "created_at": _utc(self.clock),
            }
        )
        conn = self._connect()
        try:
            conn.execute(
                """INSERT OR IGNORE INTO service_decisions
                   (decision_id, job_id, loop_name, action, confidence,
                    evidence_ids_json, rationale, model_ref, input_ref,
                    output_ref, accepted, validator_errors_json, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    decision.decision_id,
                    decision.job_id,
                    decision.loop_name,
                    decision.action,
                    decision.confidence,
                    json.dumps(decision.evidence_ids, separators=(",", ":")),
                    decision.rationale,
                    decision.model_ref,
                    decision.input_ref,
                    decision.output_ref,
                    int(decision.accepted),
                    json.dumps(
                        decision.validator_errors,
                        separators=(",", ":"),
                    ),
                    decision.created_at,
                ),
            )
            conn.commit()
        finally:
            conn.close()
        return decision

    def replay_calls(self, job_id: str) -> list[dict[str, object]]:
        conn = self._connect()
        try:
            rows = conn.execute(
                """SELECT * FROM service_model_calls
                   WHERE job_id = ? ORDER BY rowid""",
                (job_id,),
            ).fetchall()
        finally:
            conn.close()
        return [dict(row) for row in rows]

    def begin_or_get_run(
        self,
        failure: AdapterFailure,
        policy: MaintenancePolicy,
    ) -> sqlite3.Row:
        run_id = _stable_id(
            "repair-run",
            {
                "job_id": failure.job_id,
                "adapter": failure.adapter,
                "failure_fingerprint": failure.failure_fingerprint,
            },
        )
        now = _utc(self.clock)
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            if conn.execute(
                "SELECT 1 FROM service_jobs WHERE job_id = ?",
                (failure.job_id,),
            ).fetchone() is None:
                raise KeyError("maintenance job not found")
            conn.execute(
                """INSERT OR IGNORE INTO service_maintenance_runs
                   (run_id, job_id, adapter, failure_fingerprint, state,
                    policy_json, created_at, updated_at)
                   VALUES (?, ?, ?, ?, 'pending', ?, ?, ?)""",
                (
                    run_id,
                    failure.job_id,
                    failure.adapter,
                    failure.failure_fingerprint,
                    _canonical(policy.to_dict())[0],
                    now,
                    now,
                ),
            )
            row = conn.execute(
                "SELECT * FROM service_maintenance_runs WHERE run_id = ?",
                (run_id,),
            ).fetchone()
            if row is not None and row["policy_json"] != _canonical(policy.to_dict())[0]:
                raise RuntimeError("maintenance policy is immutable for an existing run")
            conn.commit()
            assert row is not None
            return row
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def claim_investigation(
        self,
        run_id: str,
        *,
        max_attempts: int,
    ) -> sqlite3.Row:
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute(
                "SELECT * FROM service_maintenance_runs WHERE run_id = ?",
                (run_id,),
            ).fetchone()
            if row is None:
                raise KeyError("maintenance run not found")
            if row["attempt_count"] >= max_attempts:
                raise RuntimeError("investigation attempt bound exhausted")
            if row["state"] not in {"pending", "rejected"}:
                raise RuntimeError("maintenance run is not claimable")
            conn.execute(
                """UPDATE service_maintenance_runs
                   SET state = 'investigating', attempt_count = ?, updated_at = ?
                   WHERE run_id = ?""",
                (row["attempt_count"] + 1, _utc(self.clock), run_id),
            )
            claimed = conn.execute(
                "SELECT * FROM service_maintenance_runs WHERE run_id = ?",
                (run_id,),
            ).fetchone()
            conn.commit()
            assert claimed is not None
            return claimed
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def claim_branch(self, run_id: str, *, max_branches: int) -> sqlite3.Row:
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute(
                "SELECT * FROM service_maintenance_runs WHERE run_id = ?",
                (run_id,),
            ).fetchone()
            if row is None:
                raise KeyError("maintenance run not found")
            if row["state"] != "recommended":
                raise RuntimeError("only an accepted recommendation may branch")
            if row["branch_count"] >= max_branches:
                raise RuntimeError("branch bound exhausted")
            conn.execute(
                """UPDATE service_maintenance_runs
                   SET state = 'branch_creating', branch_count = ?,
                       updated_at = ? WHERE run_id = ?""",
                (row["branch_count"] + 1, _utc(self.clock), run_id),
            )
            claimed = conn.execute(
                "SELECT * FROM service_maintenance_runs WHERE run_id = ?",
                (run_id,),
            ).fetchone()
            conn.commit()
            assert claimed is not None
            return claimed
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def claim_evaluation(self, run_id: str, *, max_rework: int) -> sqlite3.Row:
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute(
                "SELECT * FROM service_maintenance_runs WHERE run_id = ?",
                (run_id,),
            ).fetchone()
            if row is None:
                raise KeyError("maintenance run not found")
            if row["state"] not in {"branch_ready", "evaluated", "evaluated_failed"}:
                raise RuntimeError("repair branch is not ready for evaluation")
            is_rework = row["state"] in {"evaluated", "evaluated_failed"}
            if is_rework and row["rework_count"] >= max_rework:
                raise RuntimeError("rework bound exhausted")
            next_rework = row["rework_count"] + (1 if is_rework else 0)
            conn.execute(
                """UPDATE service_maintenance_runs
                   SET state = 'evaluating', rework_count = ?,
                       updated_at = ? WHERE run_id = ?""",
                (next_rework, _utc(self.clock), run_id),
            )
            claimed = conn.execute(
                "SELECT * FROM service_maintenance_runs WHERE run_id = ?",
                (run_id,),
            ).fetchone()
            conn.commit()
            assert claimed is not None
            return claimed
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def run(self, run_id: str) -> sqlite3.Row:
        conn = self._connect()
        try:
            row = conn.execute(
                "SELECT * FROM service_maintenance_runs WHERE run_id = ?",
                (run_id,),
            ).fetchone()
        finally:
            conn.close()
        if row is None:
            raise KeyError("maintenance run not found")
        return row

    def update_run(self, run_id: str, **updates: object) -> sqlite3.Row:
        allowed = {
            "state",
            "attempt_count",
            "rework_count",
            "branch_count",
            "current_branch",
            "thread_id",
            "recommendation_ref",
        }
        if not updates or not set(updates) <= allowed:
            raise ValueError("invalid maintenance run update")
        if "state" in updates and updates["state"] not in _RUN_STATES:
            raise ValueError("invalid maintenance state")
        sets = [f"{field} = ?" for field in updates]
        values = list(updates.values())
        sets.append("updated_at = ?")
        values.extend([_utc(self.clock), run_id])
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            if (
                conn.execute(
                    f"""UPDATE service_maintenance_runs
                        SET {", ".join(sets)} WHERE run_id = ?""",
                    values,
                ).rowcount
                != 1
            ):
                raise KeyError("maintenance run not found")
            row = conn.execute(
                "SELECT * FROM service_maintenance_runs WHERE run_id = ?",
                (run_id,),
            ).fetchone()
            conn.commit()
            assert row is not None
            return row
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def record_eval(
        self,
        *,
        run_id: str,
        job_id: str,
        metrics: Mapping[str, object],
        passed: bool,
        artifact_ref: str,
    ) -> str:
        eval_id = _stable_id(
            "eval",
            {"run_id": run_id, "metrics": dict(metrics), "passed": passed},
        )
        conn = self._connect()
        try:
            conn.execute(
                """INSERT OR IGNORE INTO service_eval_results
                   (eval_id, job_id, index_version, suite_name, metrics_json,
                    passed, artifact_ref, created_at)
                   VALUES (?, ?, NULL, ?, ?, ?, ?, ?)""",
                (
                    eval_id,
                    job_id,
                    f"adapter-repair:{run_id}",
                    _canonical(dict(metrics))[0],
                    int(passed),
                    artifact_ref,
                    _utc(self.clock),
                ),
            )
            conn.commit()
        finally:
            conn.close()
        return eval_id

    def request_approval(self, run_id: str, action: str) -> str:
        if action not in _GATED_ACTIONS:
            raise ValueError("action does not use the human approval gate")
        run = self.run(run_id)
        if run["state"] != "evaluated":
            raise RuntimeError("repair must have a current passing evaluation")
        conn = self._connect()
        try:
            evaluation = conn.execute(
                """SELECT eval_id, passed, artifact_ref FROM service_eval_results
                   WHERE suite_name = ? ORDER BY rowid DESC LIMIT 1""",
                (f"adapter-repair:{run_id}",),
            ).fetchone()
        finally:
            conn.close()
        if evaluation is None or not evaluation["passed"]:
            raise RuntimeError("repair evaluation did not pass")
        binding = {
            "run_id": run_id,
            "action": action,
            "recommendation_ref": run["recommendation_ref"],
            "evaluation_id": evaluation["eval_id"],
            "evaluation_ref": evaluation["artifact_ref"],
            "branch": run["current_branch"],
        }
        evidence_ref = self.put_artifact(binding, kind="approval:binding")
        approval_id = _stable_id(
            "approval",
            {"run_id": run_id, "action": action, "evidence_ref": evidence_ref},
        )
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            existing = conn.execute(
                """SELECT evidence_ref FROM service_approvals
                   WHERE run_id = ? AND action = ?""",
                (run_id, action),
            ).fetchone()
            if existing is not None and existing["evidence_ref"] != evidence_ref:
                raise RuntimeError("approval binding changed; create a new maintenance run")
            conn.execute(
                """INSERT INTO service_approvals
                   (approval_id, run_id, action, status, requested_at, evidence_ref)
                   VALUES (?, ?, ?, 'pending', ?, ?)
                   ON CONFLICT(run_id, action) DO NOTHING""",
                (approval_id, run_id, action, _utc(self.clock), evidence_ref),
            )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
        self.update_run(run_id, state="awaiting_approval")
        return approval_id

    def decide_approval(
        self,
        approval_id: str,
        *,
        approved: bool,
        decided_by: str,
        allowed_approvers: Sequence[str],
        expected_policy: Mapping[str, object],
    ) -> None:
        if decided_by not in allowed_approvers:
            raise PermissionError("approval actor is not allowlisted")
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute(
                """SELECT a.run_id, a.status, r.policy_json
                   FROM service_approvals a
                   JOIN service_maintenance_runs r ON r.run_id = a.run_id
                   WHERE a.approval_id = ?""",
                (approval_id,),
            ).fetchone()
            if row is None:
                raise KeyError("approval not found")
            if row["status"] != "pending":
                raise RuntimeError("approval was already decided")
            if row["policy_json"] != _canonical(dict(expected_policy))[0]:
                raise RuntimeError("maintenance policy does not match the durable run")
            conn.execute(
                """UPDATE service_approvals
                   SET status = ?, decided_at = ?, decided_by = ?
                   WHERE approval_id = ?""",
                (
                    "approved" if approved else "rejected",
                    _utc(self.clock),
                    decided_by,
                    approval_id,
                ),
            )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
        self.update_run(
            row["run_id"],
            state="approved" if approved else "rejected",
        )

    def action_authorized(self, run_id: str, action: str) -> bool:
        if action not in _GATED_ACTIONS:
            return False
        conn = self._connect()
        try:
            row = conn.execute(
                """SELECT status, evidence_ref FROM service_approvals
                   WHERE run_id = ? AND action = ?""",
                (run_id, action),
            ).fetchone()
        finally:
            conn.close()
        if row is None or row["status"] != "approved" or not row["evidence_ref"]:
            return False
        binding = self.get_artifact(row["evidence_ref"])
        if not isinstance(binding, Mapping):
            return False
        run = self.run(run_id)
        return (
            binding.get("run_id") == run_id
            and binding.get("action") == action
            and binding.get("recommendation_ref") == run["recommendation_ref"]
            and binding.get("branch") == run["current_branch"]
        )


def _base_output_errors(
    output: Mapping[str, object],
    *,
    required: Set[str],
    optional: Set[str] = frozenset(),
) -> list[str]:
    if not isinstance(output, Mapping):
        return ["output_schema_invalid"]
    if set(output) - required - optional or required - set(output):
        return ["output_schema_invalid"]
    confidence = output.get("confidence")
    if (
        isinstance(confidence, bool)
        or not isinstance(confidence, (int, float))
        or not 0 <= float(confidence) <= 1
    ):
        return ["output_schema_invalid"]
    if not isinstance(output.get("rationale"), str) or not str(
        output["rationale"]
    ).strip():
        return ["output_schema_invalid"]
    evidence = output.get("evidence_ids")
    if not isinstance(evidence, list) or any(
        not isinstance(item, str) or not item.strip() for item in evidence
    ):
        return ["output_schema_invalid"]
    return []


def _safe_confidence(output: Mapping[str, object]) -> float:
    value = output.get("confidence")
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not 0 <= float(value) <= 1
    ):
        return 0
    return float(value)


def _validate_enrichment(output: Mapping[str, object]) -> list[str]:
    errors = _base_output_errors(
        output,
        required={
            "action",
            "entity_proposals",
            "relationship_proposals",
            "confidence",
            "rationale",
            "evidence_ids",
        },
    )
    if errors or output.get("action") != "propose_enrichment":
        return ["output_schema_invalid"]
    entities = output.get("entity_proposals")
    relationships = output.get("relationship_proposals")
    if not isinstance(entities, list) or not isinstance(relationships, list):
        return ["output_schema_invalid"]
    try:
        for proposal in entities:
            contracts.EntityProposal.from_dict(proposal)
        for proposal in relationships:
            contracts.RelationshipProposal.from_dict(proposal)
    except (contracts.ContractValidationError, TypeError, ValueError):
        return ["proposal_schema_invalid"]
    return []


def _validate_evaluation(output: Mapping[str, object]) -> list[str]:
    errors = _base_output_errors(
        output,
        required={
            "action",
            "judgments",
            "confidence",
            "rationale",
            "evidence_ids",
        },
    )
    if errors or output.get("action") != "record_judgments":
        return ["output_schema_invalid"]
    judgments = output.get("judgments")
    if not isinstance(judgments, list):
        return ["output_schema_invalid"]
    required = {"case_id", "document_id", "relevance", "evidence_ids"}
    for judgment in judgments:
        if not isinstance(judgment, Mapping) or set(judgment) != required:
            return ["judgment_schema_invalid"]
        relevance = judgment["relevance"]
        if (
            isinstance(relevance, bool)
            or not isinstance(relevance, int)
            or not 0 <= relevance <= 3
        ):
            return ["judgment_schema_invalid"]
        if any(
            not isinstance(judgment[field], str) or not judgment[field].strip()
            for field in ("case_id", "document_id")
        ):
            return ["judgment_schema_invalid"]
        if not isinstance(judgment["evidence_ids"], list):
            return ["judgment_schema_invalid"]
    return []


class StructuredIntelligenceWorkers:
    """Schema-gated enrichment and evaluation leaves with replay receipts."""

    def __init__(
        self,
        ledger: IntelligenceLedger,
        client: AppServerWorker,
        *,
        cwd: Path,
        model: str | None = None,
        max_calls_per_job_loop: int = 1,
        max_input_bytes: int = 65_536,
        reserved_cost_cents_per_call: int = 1,
        cost_budget_cents: int = 1,
    ):
        if not 1 <= max_calls_per_job_loop <= 5:
            raise ValueError("structured worker call bound must be between 1 and 5")
        if not 1024 <= max_input_bytes <= 1_048_576:
            raise ValueError("structured worker input bound is invalid")
        if reserved_cost_cents_per_call < 1 or cost_budget_cents < 1:
            raise ValueError("structured worker cost bounds must be positive")
        self.ledger = ledger
        self.client = client
        self.cwd = Path(cwd)
        self.model = model
        self.max_calls_per_job_loop = max_calls_per_job_loop
        self.max_input_bytes = max_input_bytes
        self.reserved_cost_cents_per_call = reserved_cost_cents_per_call
        self.cost_budget_cents = cost_budget_cents

    def enrich(self, *, job_id: str, input_payload: object) -> WorkerDecision:
        return self._run(
            job_id=job_id,
            loop_name="entity_relationship_enrichment",
            input_payload=input_payload,
            output_schema=ENRICHMENT_OUTPUT_SCHEMA,
            validator=_validate_enrichment,
            prompt=(
                "Return only schema-valid evidence-linked entity and relationship "
                "proposals. Do not mutate service state."
            ),
        )

    def evaluate(self, *, job_id: str, input_payload: object) -> WorkerDecision:
        return self._run(
            job_id=job_id,
            loop_name="retrieval_evaluation_judgment",
            input_payload=input_payload,
            output_schema=EVALUATION_OUTPUT_SCHEMA,
            validator=_validate_evaluation,
            prompt=(
                "Return only schema-valid relevance judgments tied to supplied "
                "evidence IDs. Do not change thresholds or publish results."
            ),
        )

    def _run(
        self,
        *,
        job_id: str,
        loop_name: str,
        input_payload: object,
        output_schema: Mapping[str, object],
        validator: Callable[[Mapping[str, object]], list[str]],
        prompt: str,
    ) -> WorkerDecision:
        input_json, supplied_evidence = _validate_worker_input(
            loop_name,
            input_payload,
            max_input_bytes=self.max_input_bytes,
        )
        input_ref = self.ledger.put_artifact(
            {
                "payload": input_payload,
                "prompt": prompt,
                "output_schema": dict(output_schema),
                "cwd": os.fspath(self.cwd),
                "model": self.model,
            },
            kind=f"{loop_name}:input",
        )
        call_id = self.ledger.reserve_model_call(
            job_id=job_id,
            loop_name=loop_name,
            input_ref=input_ref,
            max_calls=self.max_calls_per_job_loop,
            reserved_cost_cents=self.reserved_cost_cents_per_call,
            cost_budget_cents=self.cost_budget_cents,
        )
        try:
            turn = self.client.structured_turn(
                prompt=(
                    f"{prompt}\nInput artifact: {input_ref}\n"
                    f"Normalized public input JSON:\n{input_json}"
                ),
                output_schema=output_schema,
                cwd=self.cwd,
                model=self.model,
            )
        except Exception as exc:
            failure_ref = self.ledger.put_artifact(
                [{"type": "model_call_failed", "error_code": type(exc).__name__}],
                kind=f"{loop_name}:events",
                media_type="application/jsonl",
            )
            self.ledger.fail_model_call(
                call_id,
                error_code=type(exc).__name__,
                event_stream_ref=failure_ref,
            )
            raise
        output = dict(turn.output)
        output_ref = self.ledger.put_artifact(
            output,
            kind=f"{loop_name}:output",
        )
        event_ref = self.ledger.put_artifact(
            list(turn.events),
            kind=f"{loop_name}:events",
            media_type="application/jsonl",
        )
        self.ledger.complete_model_call(
            call_id,
            turn=turn,
            output_ref=output_ref,
            event_stream_ref=event_ref,
        )
        errors = validator(output)
        if _output_evidence_ids(loop_name, output) - supplied_evidence:
            errors = [*errors, "evidence_not_supplied"]
        decision = self.ledger.record_decision(
            job_id=job_id,
            loop_name=loop_name,
            action=str(output.get("action") or "invalid_output"),
            confidence=_safe_confidence(output),
            evidence_ids=output.get("evidence_ids", [])
            if isinstance(output.get("evidence_ids"), list)
            else [],
            rationale=str(output.get("rationale") or "Output failed validation."),
            model_ref=turn.model_ref,
            input_ref=input_ref,
            output_ref=output_ref,
            accepted=not errors,
            validator_errors=errors,
        )
        return WorkerDecision(
            decision.decision_id,
            decision.accepted,
            tuple(decision.validator_errors),
            input_ref,
            output_ref,
            event_ref,
        )


def _safe_target(
    target: str,
    allowed_roots: Sequence[str],
) -> bool:
    path = PurePosixPath(target)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        return False
    return any(
        path == PurePosixPath(root) or PurePosixPath(root) in path.parents
        for root in allowed_roots
    )


def _validate_repair(
    output: Mapping[str, object],
    policy: MaintenancePolicy,
) -> list[str]:
    required = {
        "action",
        "confidence",
        "target_files",
        "risk",
        "rationale",
        "next_prompt",
    }
    if set(output) != required:
        return ["output_schema_invalid"]
    if output.get("action") not in _REPAIR_ACTIONS:
        return ["action_not_allowed"]
    confidence = output.get("confidence")
    if (
        isinstance(confidence, bool)
        or not isinstance(confidence, (int, float))
        or not 0 <= float(confidence) <= 1
    ):
        return ["output_schema_invalid"]
    if output.get("risk") not in _RISKS:
        return ["output_schema_invalid"]
    if not isinstance(output.get("rationale"), str) or not str(
        output["rationale"]
    ).strip():
        return ["output_schema_invalid"]
    targets = output.get("target_files")
    if not isinstance(targets, list) or len(targets) > 16:
        return ["target_scope_invalid"]
    if any(
        not isinstance(target, str)
        or not _safe_target(target, policy.allowed_write_roots)
        for target in targets
    ):
        return ["target_scope_invalid"]
    return []


class RepairSupervisor:
    """Host-owned adapter repair state machine; it has no publish operation."""

    def __init__(
        self,
        ledger: IntelligenceLedger,
        client: AppServerWorker,
        policy: MaintenancePolicy,
        *,
        cwd: Path,
        branch_manager: BranchManager,
        test_executor: TestExecutor,
        model: str | None = None,
    ):
        self.ledger = ledger
        self.client = client
        self.policy = policy
        self.cwd = Path(cwd)
        self.branch_manager = branch_manager
        self.test_executor = test_executor
        self.model = model
        client_timeout = getattr(client, "timeout_seconds", policy.wall_timeout_seconds)
        if client_timeout > policy.wall_timeout_seconds:
            raise ValueError("app-server timeout exceeds maintenance policy")

    @staticmethod
    def run_id_for(failure: AdapterFailure) -> str:
        return _stable_id(
            "repair-run",
            {
                "job_id": failure.job_id,
                "adapter": failure.adapter,
                "failure_fingerprint": failure.failure_fingerprint,
            },
        )

    def _run(self, run_id: str) -> sqlite3.Row:
        row = self.ledger.run(run_id)
        if row["policy_json"] != _canonical(self.policy.to_dict())[0]:
            raise RuntimeError("maintenance policy does not match the durable run")
        return row

    def investigate(self, failure: AdapterFailure) -> RepairResult:
        if failure.occurrences < self.policy.repeated_failure_threshold:
            raise RuntimeError("failure has not reached the investigation threshold")
        row = self.ledger.begin_or_get_run(failure, self.policy)
        row = self.ledger.claim_investigation(
            row["run_id"],
            max_attempts=self.policy.max_investigation_attempts,
        )
        attempt = row["attempt_count"]
        input_payload = {
            "run_id": row["run_id"],
            "job_id": failure.job_id,
            "adapter": failure.adapter,
            "failure_fingerprint": failure.failure_fingerprint,
            "occurrences": failure.occurrences,
            "evidence_ids": list(failure.evidence_ids),
            "diagnostic_refs": list(failure.diagnostic_refs),
            "policy": self.policy.to_dict(),
            "attempt": attempt,
        }
        prompt = (
            "You advise a deterministic repair supervisor. Inspect only the "
            "referenced failure evidence and return one repair recommendation. "
            "Do not deploy, publish, mutate live source configuration, request "
            "credentials, or execute a control action."
        )
        input_ref = self.ledger.put_artifact(
            {
                "payload": input_payload,
                "prompt": prompt,
                "output_schema": REPAIR_OUTPUT_SCHEMA,
                "cwd": os.fspath(self.cwd),
                "model": self.model,
            },
            kind="adapter_repair:input",
        )
        call_id = self.ledger.reserve_model_call(
            job_id=failure.job_id,
            loop_name="adapter_failure_investigation",
            input_ref=input_ref,
            max_calls=self.policy.max_model_calls_per_job_loop,
            reserved_cost_cents=self.policy.reserved_cost_cents_per_call,
            cost_budget_cents=self.policy.cost_budget_cents,
        )
        try:
            turn = self.client.structured_turn(
                prompt=(
                    f"{prompt}\nInput artifact: {input_ref}\n"
                    "Redacted failure input JSON:\n"
                    f"{_canonical(input_payload)[0]}"
                ),
                output_schema=REPAIR_OUTPUT_SCHEMA,
                cwd=self.cwd,
                model=self.model,
                thread_id=row["thread_id"],
            )
        except Exception as exc:
            failure_ref = self.ledger.put_artifact(
                [{"type": "model_call_failed", "error_code": type(exc).__name__}],
                kind="adapter_repair:events",
                media_type="application/jsonl",
            )
            self.ledger.fail_model_call(
                call_id,
                error_code=type(exc).__name__,
                event_stream_ref=failure_ref,
            )
            self.ledger.update_run(row["run_id"], state="rejected")
            raise
        output = dict(turn.output)
        output_ref = self.ledger.put_artifact(
            output,
            kind="adapter_repair:recommendation",
        )
        event_ref = self.ledger.put_artifact(
            list(turn.events),
            kind="adapter_repair:events",
            media_type="application/jsonl",
        )
        self.ledger.complete_model_call(
            call_id,
            turn=turn,
            output_ref=output_ref,
            event_stream_ref=event_ref,
        )
        errors = _validate_repair(output, self.policy)
        decision = self.ledger.record_decision(
            job_id=failure.job_id,
            loop_name="adapter_failure_investigation",
            action=str(output.get("action") or "invalid_output"),
            confidence=_safe_confidence(output),
            evidence_ids=failure.evidence_ids,
            rationale=str(output.get("rationale") or "Output failed validation."),
            model_ref=turn.model_ref,
            input_ref=input_ref,
            output_ref=output_ref,
            accepted=not errors,
            validator_errors=errors,
        )
        self.ledger.update_run(
            row["run_id"],
            state="recommended" if decision.accepted else "rejected",
            thread_id=turn.thread_id,
            recommendation_ref=output_ref,
        )
        return RepairResult(
            row["run_id"],
            decision.decision_id,
            decision.accepted,
            tuple(decision.validator_errors),
            output_ref,
        )

    def prepare_branch(self, run_id: str, *, parent_branch: str) -> str:
        self._run(run_id)
        self.ledger.claim_branch(
            run_id,
            max_branches=self.policy.max_branches,
        )
        try:
            branch = self.branch_manager.create(run_id, parent_branch)
        except Exception:
            self.ledger.update_run(run_id, state="rejected")
            raise
        if not isinstance(branch, str) or not branch.strip():
            self.ledger.update_run(run_id, state="rejected")
            raise RuntimeError("branch manager returned an invalid branch")
        self.ledger.update_run(
            run_id,
            state="branch_ready",
            current_branch=branch,
        )
        return branch

    def evaluate(
        self,
        run_id: str,
        *,
        commands: Sequence[str],
    ) -> EvaluationResult:
        if not commands or any(
            command not in self.policy.allowed_tests for command in commands
        ):
            raise ValueError("test command is not allowlisted")
        self._run(run_id)
        row = self.ledger.claim_evaluation(run_id, max_rework=self.policy.max_rework)
        try:
            outcomes = [
                self.test_executor.run(
                    command,
                    cwd=self.cwd,
                    branch=row["current_branch"],
                )
                for command in commands
            ]
        except Exception:
            self.ledger.update_run(run_id, state="evaluated_failed")
            raise
        artifact = {
            "run_id": run_id,
            "branch": row["current_branch"],
            "outcomes": [
                {
                    "command": outcome.command,
                    "passed": outcome.passed,
                    "metrics": dict(outcome.metrics),
                    "output": dict(outcome.output),
                }
                for outcome in outcomes
            ],
        }
        artifact_ref = self.ledger.put_artifact(
            artifact,
            kind="adapter_repair:evaluation",
        )
        passed = all(outcome.passed for outcome in outcomes)
        metrics = {
            "test_count": len(outcomes),
            "passed_count": sum(outcome.passed for outcome in outcomes),
            "rework_count": row["rework_count"],
        }
        eval_id = self.ledger.record_eval(
            run_id=run_id,
            job_id=row["job_id"],
            metrics=metrics,
            passed=passed,
            artifact_ref=artifact_ref,
        )
        self.ledger.update_run(
            run_id,
            state="evaluated" if passed else "evaluated_failed",
        )
        return EvaluationResult(eval_id, passed, artifact_ref)

    def request_approval(self, run_id: str, action: str) -> str:
        row = self._run(run_id)
        if row["state"] != "evaluated":
            raise RuntimeError("repair must have a current passing evaluation")
        return self.ledger.request_approval(run_id, action)

    def decide_approval(
        self,
        approval_id: str,
        *,
        approved: bool,
        decided_by: str,
    ) -> None:
        self.ledger.decide_approval(
            approval_id,
            approved=approved,
            decided_by=decided_by,
            allowed_approvers=self.policy.allowed_approvers,
            expected_policy=self.policy.to_dict(),
        )

    def action_authorized(self, run_id: str, action: str) -> bool:
        self._run(run_id)
        return self.ledger.action_authorized(run_id, action)


class CodexAppServerClient:
    """Bounded stdio JSONL client generated against the installed protocol."""

    def __init__(
        self,
        *,
        codex_path: str = "codex",
        timeout_seconds: float = 300,
    ):
        if timeout_seconds <= 0 or timeout_seconds > 1800:
            raise ValueError("app-server timeout must be between 0 and 1800")
        self.codex_path = codex_path
        self.timeout_seconds = timeout_seconds

    def structured_turn(
        self,
        *,
        prompt: str,
        output_schema: Mapping[str, object],
        cwd: Path,
        model: str | None = None,
        thread_id: str | None = None,
    ) -> AppServerTurn:
        if not Path(cwd).is_absolute():
            raise ValueError("app-server cwd must be absolute")
        process = subprocess.Popen(
            [self.codex_path, "app-server", "--stdio"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            bufsize=1,
            env=self._environment(),
        )
        events: list[Mapping[str, object]] = []
        deadline = time.monotonic() + self.timeout_seconds
        try:
            self._send(
                process,
                {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {
                        "clientInfo": {
                            "name": "last30days-maintenance",
                            "version": "1",
                        }
                    },
                },
            )
            self._read_response(process, 1, events, deadline)
            self._send(
                process,
                {
                    "jsonrpc": "2.0",
                    "method": "initialized",
                    "params": {},
                },
            )
            active_thread = thread_id
            model_ref = model or "configured-default"
            if active_thread is None:
                self._send(
                    process,
                    {
                        "jsonrpc": "2.0",
                        "id": 2,
                        "method": "thread/start",
                        "params": {
                            "cwd": os.fspath(cwd),
                            "model": model,
                            "sandbox": "read-only",
                            "approvalPolicy": "never",
                            "ephemeral": False,
                        },
                    },
                )
                thread_result = self._read_response(process, 2, events, deadline)
                thread = thread_result["result"]["thread"]
                active_thread = thread["id"]
                model_ref = str(thread_result["result"].get("model") or model_ref)
            else:
                self._send(
                    process,
                    {
                        "jsonrpc": "2.0",
                        "id": 2,
                        "method": "thread/resume",
                        "params": {
                            "threadId": active_thread,
                            "cwd": os.fspath(cwd),
                        },
                    },
                )
                thread_result = self._read_response(process, 2, events, deadline)
                model_ref = str(thread_result["result"].get("model") or model_ref)
            self._send(
                process,
                {
                    "jsonrpc": "2.0",
                    "id": 3,
                    "method": "turn/start",
                    "params": {
                        "threadId": active_thread,
                        "input": [{"type": "text", "text": prompt}],
                        "cwd": os.fspath(cwd),
                        "approvalPolicy": "never",
                        "outputSchema": dict(output_schema),
                    },
                },
            )
            turn_result = self._read_response(process, 3, events, deadline)
            turn_id = turn_result["result"]["turn"]["id"]
            output = self._read_turn_output(process, turn_id, events, deadline)
            return AppServerTurn(
                model_ref=model_ref,
                thread_id=active_thread,
                turn_id=turn_id,
                output=output,
                events=tuple(events),
            )
        finally:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)

    @staticmethod
    def _environment() -> dict[str, str]:
        allowed = {
            "HOME",
            "PATH",
            "LANG",
            "LC_ALL",
            "XDG_CONFIG_HOME",
            "XDG_DATA_HOME",
            "CODEX_HOME",
        }
        return {key: value for key, value in os.environ.items() if key in allowed}

    @staticmethod
    def _send(
        process: subprocess.Popen[str],
        payload: Mapping[str, object],
    ) -> None:
        if process.stdin is None:
            raise RuntimeError("app-server stdin unavailable")
        process.stdin.write(json.dumps(payload, separators=(",", ":")) + "\n")
        process.stdin.flush()

    def _next(
        self,
        process: subprocess.Popen[str],
        deadline: float,
    ) -> Mapping[str, object]:
        if process.stdout is None:
            raise RuntimeError("app-server stdout unavailable")
        while time.monotonic() < deadline:
            ready, _, _ = select.select(
                [process.stdout],
                [],
                [],
                min(0.2, max(0, deadline - time.monotonic())),
            )
            if not ready:
                if process.poll() is not None:
                    break
                continue
            line = process.stdout.readline()
            if line:
                payload = json.loads(line)
                if isinstance(payload, Mapping):
                    return payload
        raise RuntimeError("Codex app-server response timed out")

    def _read_response(
        self,
        process: subprocess.Popen[str],
        request_id: int,
        events: list[Mapping[str, object]],
        deadline: float,
    ) -> Mapping[str, object]:
        while True:
            payload = self._next(process, deadline)
            if payload.get("id") == request_id:
                if payload.get("jsonrpc") not in {None, "2.0"}:
                    raise RuntimeError("Codex app-server returned invalid JSON-RPC")
                if "error" in payload:
                    raise RuntimeError("Codex app-server request failed")
                if not isinstance(payload.get("result"), Mapping):
                    raise RuntimeError("Codex app-server returned invalid result")
                return payload
            events.append(payload)

    def _read_turn_output(
        self,
        process: subprocess.Popen[str],
        turn_id: str,
        events: list[Mapping[str, object]],
        deadline: float,
    ) -> Mapping[str, object]:
        final_text: str | None = None
        turn_error: str | None = None
        while True:
            payload = self._next(process, deadline)
            events.append(payload)
            method = payload.get("method")
            params = payload.get("params")
            discovered = self._completed_agent_text(payload, turn_id)
            if discovered is not None:
                final_text = discovered
            if isinstance(params, Mapping):
                if method == "error":
                    error = params.get("error")
                    if isinstance(error, Mapping):
                        turn_error = str(
                            error.get("message")
                            or error.get("codexErrorInfo")
                            or "turn failed"
                        )[:256]
                    else:
                        turn_error = "turn failed"
                turn = params.get("turn")
                completed_id = (
                    turn.get("id") if isinstance(turn, Mapping) else params.get("turnId")
                )
                if method == "turn/completed" and completed_id == turn_id:
                    break
        if final_text is None:
            if turn_error is not None:
                raise RuntimeError(f"Codex app-server turn failed: {turn_error}")
            methods = [
                str(event.get("method"))
                for event in events
                if event.get("method") is not None
            ]
            raise RuntimeError(
                "Codex app-server returned no structured output; event methods: "
                + ",".join(methods[-12:])
            )
        try:
            output = json.loads(final_text)
        except json.JSONDecodeError as exc:
            raise RuntimeError("Codex app-server output was not JSON") from exc
        if not isinstance(output, Mapping):
            raise RuntimeError("Codex app-server output was not an object")
        return output

    @staticmethod
    def _completed_agent_text(
        payload: Mapping[str, object],
        turn_id: str,
    ) -> str | None:
        if payload.get("method") != "item/completed":
            return None
        params = payload.get("params")
        if not isinstance(params, Mapping) or params.get("turnId") != turn_id:
            return None
        item = params.get("item")
        if (
            not isinstance(item, Mapping)
            or item.get("type") != "agentMessage"
            or not isinstance(item.get("text"), str)
        ):
            return None
        return item["text"]
