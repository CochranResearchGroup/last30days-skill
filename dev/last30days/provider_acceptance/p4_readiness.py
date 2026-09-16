"""One-shot, source-bound P4 auth-readiness execution for X."""

from __future__ import annotations

import hashlib
import importlib
import json
import re
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Mapping

from .contracts import ContractError
from .readiness import (
    ReadinessGrant,
    SealedReadinessPlan,
    seal_readiness_plan,
    verify_readiness_grant,
    verify_readiness_plan,
)


SCHEMA_VERSION = 1
PACKET_CAMPAIGN_ID = "wi010-x-p4-readiness-v1"
RECEIPT_CAMPAIGN_ID = "wi010-x-p4-readiness-receipt-v1"
TARGET_SCHEMA = "last30days.agent-browser-targets.v1"
CASE_ID = "x-browser"
ADAPTER_ID = "x_agent_browser"
PROVIDER = "x"
MAX_BROWSER_ACTIONS = 4
MAX_REQUEST_EQUIVALENTS = 3
MAX_WALL_SECONDS = 120
ACCOUNTING_CONFIDENCE = "opaque_request_equivalent"
_SOURCE_FILES = (
    "dev/last30days/provider_acceptance/p4_readiness.py",
    "dev/last30days/provider_acceptance/readiness.py",
    "dev/last30days/scripts/provider_p4_readiness.py",
    "skills/last30days/scripts/lib/agent_browser_config.py",
    "skills/last30days/scripts/lib/agent_browser_runtime.py",
    "skills/last30days/scripts/lib/x_browser.py",
)
_SAFE_FAILURES = frozenset(
    {
        "auth_required",
        "auth_state_ambiguous",
        "browser_action_budget_exhausted",
        "checkpoint_required",
        "profile_mismatch",
        "request_equivalent_budget_exhausted",
        "rate_limited",
        "restricted",
        "route_stale",
        "target_unavailable",
        "agent_browser_error",
        "agent_browser_missing",
        "agent_browser_timeout",
        "unknown_failure",
    }
)


@dataclass(frozen=True)
class PreparedP4Packet:
    schema_version: int
    campaign_id: str
    profile_id: str
    target_config_sha256: str
    source_sha256: str
    plan: SealedReadinessPlan
    grant: ReadinessGrant
    grant_sha256: str
    packet_sha256: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "campaign_id": self.campaign_id,
            "profile_id": self.profile_id,
            "target_config_sha256": self.target_config_sha256,
            "source_sha256": self.source_sha256,
            "plan": asdict(self.plan),
            "grant": asdict(self.grant),
            "grant_sha256": self.grant_sha256,
            "packet_sha256": self.packet_sha256,
        }


@dataclass(frozen=True)
class P4ReadinessReceipt:
    schema_version: int
    campaign_id: str
    state: str
    safe_reason_code: str
    provider: str
    adapter_id: str
    case_id: str
    profile_ref: str
    plan_sha256: str
    grant_sha256: str
    source_sha256: str
    target_config_sha256: str
    started_at: str
    finished_at: str
    attempt_count: int
    external_concurrency: int
    browser_actions: int
    request_equivalents: int
    accounting_confidence: str
    authenticated: bool
    login_form: bool
    checkpoint: bool
    restricted: bool
    teardown_completed: bool
    owned_handle_remaining: bool
    operations: tuple[str, ...]
    receipt_sha256: str

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["operations"] = list(self.operations)
        return payload


ClientFactory = Callable[[Mapping[str, Any]], tuple[Any, Any]]


def _canonical(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")


def _digest(value: object) -> str:
    return "sha256:" + hashlib.sha256(_canonical(value)).hexdigest()


def _timestamp(value: datetime | None = None) -> str:
    current = value or datetime.now(timezone.utc)
    if current.tzinfo is None:
        raise ContractError("timestamp_must_be_timezone_aware")
    return current.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _source_digest(repo_root: Path) -> str:
    return _digest(
        {
            relative: "sha256:"
            + hashlib.sha256((repo_root / relative).read_bytes()).hexdigest()
            for relative in _SOURCE_FILES
        }
    )


def _load_target(path: Path) -> tuple[str, str, dict[str, Any]]:
    try:
        raw = path.read_bytes()
        payload = json.loads(raw)
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError("x_target_config_unavailable") from exc
    if not isinstance(payload, dict) or payload.get("schema_version") != TARGET_SCHEMA:
        raise ContractError("x_target_config_invalid")
    targets = payload.get("targets")
    target = targets.get("x") if isinstance(targets, dict) else None
    if not isinstance(target, dict):
        raise ContractError("x_target_binding_missing")
    profile_id = target.get("profile_id")
    if not isinstance(profile_id, str) or not profile_id:
        raise ContractError("x_target_profile_missing")
    safe_target = {
        key: target.get(key)
        for key in (
            "browser_build",
            "browser_host",
            "control_input_provider",
            "display_isolation",
            "profile_id",
            "view_stream_provider",
        )
        if isinstance(target.get(key), (str, int, float, bool))
    }
    return profile_id, "sha256:" + hashlib.sha256(raw).hexdigest(), safe_target


def _unsigned_packet(packet: PreparedP4Packet) -> dict[str, Any]:
    payload = packet.to_dict()
    payload["packet_sha256"] = ""
    return payload


def prepare_x_packet(
    *,
    target_config_path: Path | str,
    repo_root: Path | str = ".",
    now: datetime | None = None,
) -> PreparedP4Packet:
    """Read one stable non-secret X binding and seal a short-lived P4 grant."""
    current = now or datetime.now(timezone.utc)
    issued_at = _timestamp(current)
    expires_at = _timestamp(current + timedelta(minutes=10))
    profile_id, config_digest, _target = _load_target(Path(target_config_path))
    plan = seal_readiness_plan(
        case_id=CASE_ID,
        profile_ref=f"profile:{profile_id}",
        issued_at=issued_at,
        expires_at=expires_at,
        max_browser_actions=MAX_BROWSER_ACTIONS,
        max_request_equivalents=MAX_REQUEST_EQUIVALENTS,
        max_wall_seconds=MAX_WALL_SECONDS,
        max_cost_cents=0,
        repo_root=repo_root,
    )
    grant = ReadinessGrant.for_plan(plan)
    grant_sha256 = _digest(asdict(grant))
    source_sha256 = _source_digest(Path(repo_root).resolve())
    unsigned = {
        "schema_version": SCHEMA_VERSION,
        "campaign_id": PACKET_CAMPAIGN_ID,
        "profile_id": profile_id,
        "target_config_sha256": config_digest,
        "source_sha256": source_sha256,
        "plan": asdict(plan),
        "grant": asdict(grant),
        "grant_sha256": grant_sha256,
        "packet_sha256": "",
    }
    return PreparedP4Packet(
        schema_version=SCHEMA_VERSION,
        campaign_id=PACKET_CAMPAIGN_ID,
        profile_id=profile_id,
        target_config_sha256=config_digest,
        source_sha256=source_sha256,
        plan=plan,
        grant=grant,
        grant_sha256=grant_sha256,
        packet_sha256=_digest(unsigned),
    )


def verify_packet(
    packet: PreparedP4Packet,
    *,
    target_config_path: Path | str,
    repo_root: Path | str = ".",
    now: datetime,
) -> dict[str, Any]:
    if packet.schema_version != SCHEMA_VERSION or packet.campaign_id != PACKET_CAMPAIGN_ID:
        raise ContractError("p4_packet_identity_mismatch")
    if packet.packet_sha256 != _digest(_unsigned_packet(packet)):
        raise ContractError("p4_packet_digest_mismatch")
    if packet.grant_sha256 != _digest(asdict(packet.grant)):
        raise ContractError("p4_grant_digest_mismatch")
    if packet.source_sha256 != _source_digest(Path(repo_root).resolve()):
        raise ContractError("p4_source_digest_mismatch")
    verify_readiness_grant(
        packet.plan,
        packet.grant,
        now=now,
        repo_root=repo_root,
    )
    if (
        packet.plan.case_id != CASE_ID
        or packet.plan.adapter_id != ADAPTER_ID
        or packet.plan.provider != PROVIDER
        or packet.plan.max_browser_actions != MAX_BROWSER_ACTIONS
        or packet.plan.max_request_equivalents != MAX_REQUEST_EQUIVALENTS
        or packet.plan.max_wall_seconds != MAX_WALL_SECONDS
        or packet.plan.accounting_confidence != ACCOUNTING_CONFIDENCE
    ):
        raise ContractError("p4_packet_scope_mismatch")
    profile_id, config_digest, target = _load_target(Path(target_config_path))
    if (
        profile_id != packet.profile_id
        or packet.plan.profile_ref != f"profile:{profile_id}"
        or config_digest != packet.target_config_sha256
    ):
        raise ContractError("p4_target_binding_mismatch")
    return target


def _live_client_factory(fields: Mapping[str, Any]) -> tuple[Any, Any]:
    skill_scripts = Path(fields["repo_root"]) / "skills/last30days/scripts"
    if str(skill_scripts) not in sys.path:
        sys.path.insert(0, str(skill_scripts))
    runtime = importlib.import_module("lib.agent_browser_runtime")
    x_browser = importlib.import_module("lib.x_browser")
    request = runtime.BrowserWorkspaceRequest(
        profile_id=fields["profile_id"],
        session_name=f"last30days-x-p4-{fields['plan_tag']}",
        browser_build=fields["browser_build"],
        view_provider=fields["view_provider"],
        timeout=MAX_WALL_SECONDS,
        start_url="https://x.com/home",
        service_name="last30days",
        agent_name="x-readiness-probe",
        task_name="x-auth-readiness",
        target_service_id="x",
        display_isolation=fields["display_isolation"],
        browser_host=fields["browser_host"],
        control_input_provider=fields["control_input_provider"],
        constrain_presentation=True,
        allow_duplicate_profile_lane=False,
    )
    return x_browser.CliAgentBrowserClient(timeout=MAX_WALL_SECONDS), request


def _safe_failure(exc: BaseException) -> str:
    if isinstance(exc, (ImportError, ModuleNotFoundError)):
        return "agent_browser_missing"
    candidate = str(getattr(exc, "reason_code", "") or getattr(exc, "error_type", ""))
    return candidate if candidate in _SAFE_FAILURES else "unknown_failure"


def _safe_operations(client: Any | None) -> tuple[str, ...]:
    timings = getattr(client, "command_timings", ()) if client is not None else ()
    operations: list[str] = []
    for timing in timings if isinstance(timings, (list, tuple)) else ():
        if not isinstance(timing, Mapping):
            continue
        operation = re.sub(r"[^a-z0-9_.-]+", "_", str(timing.get("operation") or ""))
        status = re.sub(r"[^a-z0-9_.-]+", "_", str(timing.get("status") or ""))
        if operation and status:
            operations.append(f"{operation}:{status}"[:96])
        if len(operations) == 32:
            break
    return tuple(operations)


def execute_x_readiness(
    packet: PreparedP4Packet,
    *,
    target_config_path: Path | str,
    repo_root: Path | str = ".",
    now: datetime | None = None,
    client_factory: ClientFactory | None = None,
) -> P4ReadinessReceipt:
    """Consume exactly one grant for auth inspection; never enter X search."""
    started = now or datetime.now(timezone.utc)
    target = verify_packet(
        packet,
        target_config_path=target_config_path,
        repo_root=repo_root,
        now=started,
    )
    root = Path(repo_root).resolve()
    factory = client_factory or _live_client_factory
    fields = {
        "repo_root": root,
        "profile_id": packet.profile_id,
        "plan_tag": packet.plan.plan_sha256.split(":", 1)[-1][:12],
        "browser_build": str(target.get("browser_build") or "stealthcdp_chromium"),
        "view_provider": str(target.get("view_stream_provider") or "rdp_gateway"),
        "display_isolation": str(target.get("display_isolation") or "shared_display"),
        "browser_host": str(target.get("browser_host") or "remote_headed"),
        "control_input_provider": str(
            target.get("control_input_provider") or "manual_attached_desktop"
        ),
    }
    monotonic_started = time.monotonic()
    client: Any | None = None
    request: Any | None = None
    browser_actions = 0
    request_equivalents = 0
    attempt_count = 0
    authenticated = login_form = checkpoint = restricted = False
    teardown_completed = False
    owned_handle_remaining = False
    reason = "unknown_failure"
    state = "FAILED"
    end_budget: Any | None = None
    try:
        client, request = factory(fields)
        original_act = getattr(client, "act")
        original_prepare_site_tab = getattr(client, "prepare_site_tab", None)

        def counted_act(workspace: Any, action: Any) -> Any:
            nonlocal browser_actions, request_equivalents
            next_actions = browser_actions + 1
            next_requests = request_equivalents + (
                1
                if getattr(action, "operation", "") in {"new_tab", "navigate"}
                else 0
            )
            if next_actions > packet.plan.max_browser_actions:
                raise ContractError("browser_action_budget_exhausted")
            if next_requests > packet.plan.max_request_equivalents:
                raise ContractError("request_equivalent_budget_exhausted")
            browser_actions = next_actions
            request_equivalents = next_requests
            return original_act(workspace, action)

        client.act = counted_act
        if callable(original_prepare_site_tab):
            def bounded_prepare_site_tab(
                workspace: Any, hostname: str, **kwargs: Any
            ) -> Any:
                kwargs["consolidate"] = False
                return original_prepare_site_tab(workspace, hostname, **kwargs)

            client.prepare_site_tab = bounded_prepare_site_tab
        begin_budget = getattr(client, "begin_run_budget", None)
        end_budget = getattr(client, "end_run_budget", None)
        if callable(begin_budget):
            begin_budget(packet.plan.max_wall_seconds)
        attempt_count = 1
        request_equivalents = 1
        workspace = client.acquire_workspace(request)
        if getattr(workspace, "profile_id", "") != packet.profile_id:
            raise ContractError("profile_mismatch")
        auth = client.inspect_auth(workspace)
        authenticated = bool(getattr(auth, "authenticated", False))
        login_form = bool(getattr(auth, "login_form", False))
        checkpoint = bool(getattr(auth, "checkpoint", False))
        restricted = bool(getattr(auth, "restricted", False))
        if authenticated and not (login_form or checkpoint or restricted):
            state, reason = "READY", "authenticated"
        elif login_form:
            state, reason = "NOT_READY", "auth_required"
        elif checkpoint:
            state, reason = "NOT_READY", "checkpoint_required"
        elif restricted:
            state, reason = "NOT_READY", "restricted"
        else:
            state, reason = "NOT_READY", "auth_state_ambiguous"
    except Exception as exc:  # preserve the first terminal attempt safely
        reason = _safe_failure(exc)
        if isinstance(exc, ContractError):
            reason = str(exc) if str(exc) in _SAFE_FAILURES else reason
        state = "FAILED"
    finally:
        try:
            if client is not None:
                client.release_workspace()
            teardown_completed = True
        except Exception:
            teardown_completed = False
        if callable(end_budget):
            try:
                end_budget()
            except Exception:
                teardown_completed = False
        owned_handle_remaining = (
            client is not None
            and getattr(client, "_service_tab_handle", None) is not None
        )
    if not teardown_completed or owned_handle_remaining:
        state = "FAILED"
        reason = "teardown_incomplete"
    finished = started + timedelta(seconds=max(0.0, time.monotonic() - monotonic_started))
    unsigned = {
        "schema_version": SCHEMA_VERSION,
        "campaign_id": RECEIPT_CAMPAIGN_ID,
        "state": state,
        "safe_reason_code": reason,
        "provider": PROVIDER,
        "adapter_id": ADAPTER_ID,
        "case_id": CASE_ID,
        "profile_ref": packet.plan.profile_ref,
        "plan_sha256": packet.plan.plan_sha256,
        "grant_sha256": packet.grant_sha256,
        "source_sha256": _source_digest(root),
        "target_config_sha256": packet.target_config_sha256,
        "started_at": _timestamp(started),
        "finished_at": _timestamp(finished),
        "attempt_count": attempt_count,
        "external_concurrency": 1,
        "browser_actions": browser_actions,
        "request_equivalents": request_equivalents,
        "accounting_confidence": ACCOUNTING_CONFIDENCE,
        "authenticated": authenticated,
        "login_form": login_form,
        "checkpoint": checkpoint,
        "restricted": restricted,
        "teardown_completed": teardown_completed,
        "owned_handle_remaining": owned_handle_remaining,
        "operations": _safe_operations(client),
        "receipt_sha256": "",
    }
    return P4ReadinessReceipt(**{**unsigned, "receipt_sha256": _digest(unsigned)})


def verify_receipt(
    receipt: P4ReadinessReceipt,
    packet: PreparedP4Packet,
    *,
    repo_root: Path | str = ".",
) -> tuple[bool, tuple[str, ...]]:
    reasons: list[str] = []
    try:
        verify_readiness_plan(packet.plan, repo_root=repo_root)
        if packet.grant != ReadinessGrant.for_plan(packet.plan):
            raise ContractError("readiness_grant_mismatch")
        if packet.packet_sha256 != _digest(_unsigned_packet(packet)):
            raise ContractError("p4_packet_digest_mismatch")
        if packet.grant_sha256 != _digest(asdict(packet.grant)):
            raise ContractError("p4_grant_digest_mismatch")
        if packet.source_sha256 != _source_digest(Path(repo_root).resolve()):
            raise ContractError("p4_source_digest_mismatch")
    except ContractError:
        reasons.append("packet_verification_failed")
    payload = receipt.to_dict()
    supplied_digest = payload.pop("receipt_sha256")
    payload["receipt_sha256"] = ""
    if supplied_digest != _digest(payload):
        reasons.append("receipt_digest_mismatch")
    if (
        receipt.schema_version != SCHEMA_VERSION
        or receipt.campaign_id != RECEIPT_CAMPAIGN_ID
        or receipt.provider != PROVIDER
        or receipt.adapter_id != ADAPTER_ID
        or receipt.case_id != CASE_ID
    ):
        reasons.append("receipt_identity_mismatch")
    if (
        receipt.profile_ref != packet.plan.profile_ref
        or receipt.plan_sha256 != packet.plan.plan_sha256
        or receipt.grant_sha256 != packet.grant_sha256
        or receipt.target_config_sha256 != packet.target_config_sha256
    ):
        reasons.append("receipt_binding_mismatch")
    if receipt.source_sha256 != _source_digest(Path(repo_root).resolve()):
        reasons.append("source_digest_mismatch")
    if (
        not isinstance(receipt.attempt_count, int)
        or isinstance(receipt.attempt_count, bool)
        or receipt.attempt_count not in {0, 1}
        or not isinstance(receipt.external_concurrency, int)
        or isinstance(receipt.external_concurrency, bool)
        or receipt.external_concurrency != 1
        or not isinstance(receipt.browser_actions, int)
        or isinstance(receipt.browser_actions, bool)
        or not 0 <= receipt.browser_actions
        or receipt.browser_actions > packet.plan.max_browser_actions
        or not isinstance(receipt.request_equivalents, int)
        or isinstance(receipt.request_equivalents, bool)
        or not 0 <= receipt.request_equivalents
        or receipt.request_equivalents > packet.plan.max_request_equivalents
        or receipt.accounting_confidence != ACCOUNTING_CONFIDENCE
    ):
        reasons.append("budget_mismatch")
    try:
        started_at = datetime.fromisoformat(receipt.started_at.replace("Z", "+00:00"))
        finished_at = datetime.fromisoformat(receipt.finished_at.replace("Z", "+00:00"))
        if finished_at < started_at or (
            finished_at - started_at
        ).total_seconds() > packet.plan.max_wall_seconds:
            raise ValueError
    except (TypeError, ValueError):
        reasons.append("timestamp_or_wall_budget_invalid")
    if len(receipt.operations) > 32 or any(
        not re.fullmatch(r"[a-z0-9_.-]+:[a-z0-9_.-]+", operation)
        for operation in receipt.operations
    ):
        reasons.append("operation_evidence_invalid")
    if not receipt.teardown_completed or receipt.owned_handle_remaining:
        reasons.append("teardown_incomplete")
    expected_ready = (
        receipt.authenticated
        and not receipt.login_form
        and not receipt.checkpoint
        and not receipt.restricted
        and receipt.safe_reason_code == "authenticated"
    )
    if (receipt.state == "READY") != expected_ready:
        reasons.append("readiness_state_mismatch")
    if receipt.state in {"READY", "NOT_READY"} and receipt.attempt_count != 1:
        reasons.append("attempt_state_mismatch")
    expected_not_ready_reason = (
        "auth_required"
        if receipt.login_form
        else "checkpoint_required"
        if receipt.checkpoint
        else "restricted"
        if receipt.restricted
        else "auth_state_ambiguous"
    )
    if receipt.state == "NOT_READY" and receipt.safe_reason_code != expected_not_ready_reason:
        reasons.append("not_ready_reason_mismatch")
    if receipt.state not in {"READY", "NOT_READY", "FAILED"}:
        reasons.append("receipt_state_invalid")
    return not reasons, tuple(dict.fromkeys(reasons))


def packet_from_dict(payload: Mapping[str, Any]) -> PreparedP4Packet:
    expected_fields = {
        "schema_version",
        "campaign_id",
        "profile_id",
        "target_config_sha256",
        "source_sha256",
        "plan",
        "grant",
        "grant_sha256",
        "packet_sha256",
    }
    if set(payload) != expected_fields:
        raise ContractError("p4_packet_schema_mismatch")
    try:
        return PreparedP4Packet(
            schema_version=payload["schema_version"],
            campaign_id=payload["campaign_id"],
            profile_id=payload["profile_id"],
            target_config_sha256=payload["target_config_sha256"],
            source_sha256=payload["source_sha256"],
            plan=SealedReadinessPlan(**payload["plan"]),
            grant=ReadinessGrant(**payload["grant"]),
            grant_sha256=payload["grant_sha256"],
            packet_sha256=payload["packet_sha256"],
        )
    except (KeyError, TypeError) as exc:
        raise ContractError("p4_packet_schema_mismatch") from exc


def receipt_from_dict(payload: Mapping[str, Any]) -> P4ReadinessReceipt:
    if set(payload) != set(P4ReadinessReceipt.__dataclass_fields__):
        raise ContractError("p4_receipt_schema_mismatch")
    bool_fields = {
        "authenticated",
        "login_form",
        "checkpoint",
        "restricted",
        "teardown_completed",
        "owned_handle_remaining",
    }
    int_fields = {
        "schema_version",
        "attempt_count",
        "external_concurrency",
        "browser_actions",
        "request_equivalents",
    }
    if any(not isinstance(payload[field], bool) for field in bool_fields):
        raise ContractError("p4_receipt_type_mismatch")
    if any(
        not isinstance(payload[field], int) or isinstance(payload[field], bool)
        for field in int_fields
    ):
        raise ContractError("p4_receipt_type_mismatch")
    operations = payload.get("operations")
    if not isinstance(operations, list) or not all(
        isinstance(operation, str) for operation in operations
    ):
        raise ContractError("p4_receipt_type_mismatch")
    try:
        return P4ReadinessReceipt(
            **{
                **payload,
                "operations": tuple(operations),
            }
        )
    except (KeyError, TypeError) as exc:
        raise ContractError("p4_receipt_schema_mismatch") from exc
