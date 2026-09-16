"""Provider-free P4 capability audit and exact readiness-plan sealing."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Mapping

from .contracts import ContractError


SCHEMA_VERSION = 1
CAMPAIGN_ID = "wi010-p4-capability-audit-v1"
AUDIT_STATE = "AUDITED_NOT_RUN"
NEXT_GATE = "exact_profile_reference_and_external_p4_authority_required"
_PROFILE_REF = re.compile(r"^profile:[a-z0-9][a-z0-9._-]{2,63}$")
_HASH_FILES = (
    "dev/last30days/provider_acceptance/readiness.py",
    "dev/last30days/scripts/provider_readiness.py",
    "skills/last30days/scripts/lib/x_browser.py",
    "skills/last30days/scripts/lib/facebook.py",
    "skills/last30days/scripts/lib/linkedin.py",
    "skills/last30days/scripts/lib/reddit_browser.py",
    "skills/last30days/scripts/lib/reddit_public.py",
    "skills/last30days/scripts/lib/reddit.py",
    "skills/last30days/scripts/lib/youtube_yt.py",
    "skills/last30days/scripts/lib/service_acquisition_worker.py",
    "skills/last30days/scripts/lib/service_source_policy.py",
)
_EFFECT_KEYS = (
    "credential_resolutions",
    "environment_reads",
    "executable_resolutions",
    "browser_workspace_acquisitions",
    "browser_actions",
    "dns_queries",
    "socket_connections",
    "http_requests",
    "subprocesses",
    "external_provider_calls",
    "installed_runtime_mutations",
    "schedule_mutations",
    "release_or_deployment_mutations",
    "tracker_mutations",
)


@dataclass(frozen=True)
class ReadinessCapability:
    case_id: str
    adapter_id: str
    provider: str
    source_path: str
    seam_symbol: str
    readiness_only: bool
    dependency_class: str
    next_gate: str
    rationale_code: str


@dataclass(frozen=True)
class ReadinessAuditReceipt:
    schema_version: int
    campaign_id: str
    state: str
    created_at: str
    catalog_sha256: str
    source_sha256: str
    capabilities: tuple[ReadinessCapability, ...]
    eligible_case_ids: tuple[str, ...]
    selected_case_id: str | None
    next_gate: str
    effect_census: Mapping[str, int]
    receipt_sha256: str

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["capabilities"] = [asdict(item) for item in self.capabilities]
        payload["eligible_case_ids"] = list(self.eligible_case_ids)
        return payload


@dataclass(frozen=True)
class SealedReadinessPlan:
    schema_version: int
    campaign_id: str
    effect_class: str
    case_id: str
    adapter_id: str
    provider: str
    profile_ref: str
    issued_at: str
    expires_at: str
    max_attempts: int
    external_concurrency: int
    max_browser_actions: int
    max_request_equivalents: int
    max_wall_seconds: int
    max_cost_cents: int
    accounting_confidence: str
    catalog_sha256: str
    source_sha256: str
    plan_sha256: str


@dataclass(frozen=True)
class ReadinessGrant:
    plan_sha256: str
    effect_class: str
    case_id: str
    adapter_id: str
    provider: str
    profile_ref: str
    expires_at: str
    max_attempts: int
    external_concurrency: int
    max_browser_actions: int
    max_request_equivalents: int
    max_wall_seconds: int
    max_cost_cents: int
    accounting_confidence: str

    @classmethod
    def for_plan(cls, plan: SealedReadinessPlan) -> "ReadinessGrant":
        return cls(
            plan_sha256=plan.plan_sha256,
            effect_class=plan.effect_class,
            case_id=plan.case_id,
            adapter_id=plan.adapter_id,
            provider=plan.provider,
            profile_ref=plan.profile_ref,
            expires_at=plan.expires_at,
            max_attempts=plan.max_attempts,
            external_concurrency=plan.external_concurrency,
            max_browser_actions=plan.max_browser_actions,
            max_request_equivalents=plan.max_request_equivalents,
            max_wall_seconds=plan.max_wall_seconds,
            max_cost_cents=plan.max_cost_cents,
            accounting_confidence=plan.accounting_confidence,
        )


def capability_catalog() -> tuple[ReadinessCapability, ...]:
    browser_gate = "exact_profile_reference_and_external_p4_authority_required"
    content_gate = "no_readiness_only_seam_requires_separate_p5_design"
    return (
        ReadinessCapability(
            "x-browser",
            "x_agent_browser",
            "x",
            "skills/last30days/scripts/lib/x_browser.py",
            "CliAgentBrowserClient.inspect_auth",
            True,
            "real_browser_profile",
            browser_gate,
            "auth_inspection_precedes_content_search",
        ),
        ReadinessCapability(
            "facebook-browser",
            "facebook_agent_browser",
            "facebook",
            "skills/last30days/scripts/lib/facebook.py",
            "CliAgentBrowserClient.inspect_auth",
            True,
            "real_browser_profile",
            browser_gate,
            "bounded_auth_inspection_precedes_content_search",
        ),
        ReadinessCapability(
            "linkedin-post-browser",
            "linkedin_agent_browser",
            "linkedin",
            "skills/last30days/scripts/lib/linkedin.py",
            "CliAgentBrowserClient.inspect_auth",
            True,
            "real_browser_profile",
            browser_gate,
            "auth_inspection_precedes_post_search",
        ),
        ReadinessCapability(
            "linkedin-profile-browser",
            "linkedin_profile_agent_browser",
            "linkedin",
            "skills/last30days/scripts/lib/linkedin.py",
            "CliAgentBrowserClient.inspect_auth",
            True,
            "real_browser_profile",
            browser_gate,
            "shared_auth_inspection_precedes_profile_acquisition",
        ),
        ReadinessCapability(
            "youtube-command",
            "youtube_ytdlp",
            "youtube",
            "skills/last30days/scripts/lib/youtube_yt.py",
            "search_youtube",
            False,
            "provider_subprocess",
            content_gate,
            "entrypoint_immediately_executes_content_search",
        ),
        ReadinessCapability(
            "reddit-keyless-http",
            "reddit_keyless",
            "reddit",
            "skills/last30days/scripts/lib/reddit_public.py",
            "search_reddit_public",
            False,
            "public_http",
            content_gate,
            "entrypoint_immediately_fetches_content",
        ),
        ReadinessCapability(
            "reddit-browser",
            "reddit_agent_browser",
            "reddit",
            "skills/last30days/scripts/lib/reddit_browser.py",
            "CliAgentBrowserClient.inspect_auth",
            True,
            "real_browser_profile",
            browser_gate,
            "auth_inspection_precedes_content_search",
        ),
        ReadinessCapability(
            "reddit-scrapecreators-http",
            "reddit_scrapecreators",
            "reddit",
            "skills/last30days/scripts/lib/reddit.py",
            "search_reddit",
            False,
            "credentialed_paid_http",
            content_gate,
            "key_presence_is_not_auth_readiness_and_request_fetches_content",
        ),
    )


def _canonical(payload: object) -> bytes:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")


def _digest(payload: object) -> str:
    return "sha256:" + hashlib.sha256(_canonical(payload)).hexdigest()


def _file_digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _catalog_digest() -> str:
    return _digest([asdict(item) for item in capability_catalog()])


def _source_digest(repo_root: Path) -> str:
    return _digest({path: _file_digest(repo_root / path) for path in _HASH_FILES})


def _timestamp(now: datetime | None = None) -> str:
    value = now or datetime.now(timezone.utc)
    if value.tzinfo is None:
        raise ContractError("timestamp_must_be_timezone_aware")
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _parse_timestamp(value: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ContractError("timestamp_must_be_rfc3339_utc")
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise ContractError("timestamp_must_be_rfc3339_utc") from exc
    return parsed


def _unsigned_receipt(receipt: ReadinessAuditReceipt) -> dict[str, Any]:
    payload = receipt.to_dict()
    payload["receipt_sha256"] = ""
    return payload


def audit_capabilities(
    *, repo_root: Path | str = ".", now: datetime | None = None
) -> ReadinessAuditReceipt:
    """Create an effect-free source-bound capability receipt."""
    root = Path(repo_root).resolve()
    catalog = capability_catalog()
    unsigned = {
        "schema_version": SCHEMA_VERSION,
        "campaign_id": CAMPAIGN_ID,
        "state": AUDIT_STATE,
        "created_at": _timestamp(now),
        "catalog_sha256": _catalog_digest(),
        "source_sha256": _source_digest(root),
        "capabilities": [asdict(item) for item in catalog],
        "eligible_case_ids": sorted(
            item.case_id for item in catalog if item.readiness_only
        ),
        "selected_case_id": None,
        "next_gate": NEXT_GATE,
        "effect_census": {key: 0 for key in _EFFECT_KEYS},
        "receipt_sha256": "",
    }
    return ReadinessAuditReceipt(
        **{
            **unsigned,
            "capabilities": catalog,
            "eligible_case_ids": tuple(unsigned["eligible_case_ids"]),
            "receipt_sha256": _digest(unsigned),
        }
    )


def verify_audit_receipt(
    receipt: ReadinessAuditReceipt, *, repo_root: Path | str = "."
) -> tuple[bool, tuple[str, ...]]:
    """Verify the audit without importing or invoking any production adapter."""
    root = Path(repo_root).resolve()
    reasons: list[str] = []
    try:
        _parse_timestamp(receipt.created_at)
    except ContractError:
        reasons.append("timestamp_invalid")
    if receipt.schema_version != SCHEMA_VERSION or receipt.campaign_id != CAMPAIGN_ID:
        reasons.append("schema_or_campaign_mismatch")
    if receipt.state != AUDIT_STATE or receipt.selected_case_id is not None:
        reasons.append("effect_state_mismatch")
    catalog = capability_catalog()
    if tuple(receipt.capabilities) != catalog:
        reasons.append("capability_catalog_mismatch")
    expected_eligible = tuple(
        sorted(item.case_id for item in catalog if item.readiness_only)
    )
    if tuple(receipt.eligible_case_ids) != expected_eligible:
        reasons.append("eligible_case_set_mismatch")
    if receipt.catalog_sha256 != _catalog_digest():
        reasons.append("catalog_digest_mismatch")
    if receipt.source_sha256 != _source_digest(root):
        reasons.append("source_digest_mismatch")
    if receipt.next_gate != NEXT_GATE:
        reasons.append("next_gate_mismatch")
    if dict(receipt.effect_census) != {key: 0 for key in _EFFECT_KEYS}:
        reasons.append("effect_boundary_violation")
    if receipt.receipt_sha256 != _digest(_unsigned_receipt(receipt)):
        reasons.append("receipt_digest_mismatch")
    return not reasons, tuple(dict.fromkeys(reasons))


def _validate_profile_ref(profile_ref: str) -> None:
    if not isinstance(profile_ref, str) or not _PROFILE_REF.fullmatch(profile_ref):
        raise ContractError("profile_reference_must_be_exact_and_opaque")
    lowered = profile_ref.split(":", 1)[1].casefold()
    if any(
        fragment in lowered
        for fragment in (
            "default",
            "secret",
            "token",
            "password",
            "cookie",
            "http",
            "file",
            "..",
        )
    ):
        raise ContractError("profile_reference_is_not_safe")


def seal_readiness_plan(
    *,
    case_id: str,
    profile_ref: str,
    issued_at: str,
    expires_at: str,
    max_browser_actions: int,
    max_request_equivalents: int,
    max_wall_seconds: int,
    max_cost_cents: int = 0,
    repo_root: Path | str = ".",
) -> SealedReadinessPlan:
    """Seal one exact P4 plan without resolving its profile or dependencies."""
    selected = next(
        (item for item in capability_catalog() if item.case_id == case_id), None
    )
    if selected is None:
        raise ContractError("unknown_readiness_case")
    if not selected.readiness_only:
        raise ContractError("adapter_has_no_readiness_only_seam")
    _validate_profile_ref(profile_ref)
    issued = _parse_timestamp(issued_at)
    expires = _parse_timestamp(expires_at)
    if expires <= issued or expires - issued > timedelta(minutes=15):
        raise ContractError("readiness_grant_expiry_out_of_bounds")
    budgets = (max_browser_actions, max_request_equivalents, max_wall_seconds)
    if any(not isinstance(value, int) or isinstance(value, bool) for value in budgets):
        raise ContractError("readiness_budget_must_be_integer")
    if not 1 <= max_browser_actions <= 8:
        raise ContractError("browser_action_budget_out_of_bounds")
    if not 1 <= max_request_equivalents <= 4:
        raise ContractError("request_equivalent_budget_out_of_bounds")
    if not 1 <= max_wall_seconds <= 120:
        raise ContractError("wall_budget_out_of_bounds")
    if max_cost_cents != 0:
        raise ContractError("readiness_cost_budget_must_be_zero")
    root = Path(repo_root).resolve()
    unsigned = {
        "schema_version": SCHEMA_VERSION,
        "campaign_id": "wi010-p4-readiness-v1",
        "effect_class": "p4_readiness",
        "case_id": selected.case_id,
        "adapter_id": selected.adapter_id,
        "provider": selected.provider,
        "profile_ref": profile_ref,
        "issued_at": issued_at,
        "expires_at": expires_at,
        "max_attempts": 1,
        "external_concurrency": 1,
        "max_browser_actions": max_browser_actions,
        "max_request_equivalents": max_request_equivalents,
        "max_wall_seconds": max_wall_seconds,
        "max_cost_cents": max_cost_cents,
        "accounting_confidence": "opaque_request_equivalent",
        "catalog_sha256": _catalog_digest(),
        "source_sha256": _source_digest(root),
        "plan_sha256": "",
    }
    return SealedReadinessPlan(**{**unsigned, "plan_sha256": _digest(unsigned)})


def verify_readiness_plan(
    plan: SealedReadinessPlan, *, repo_root: Path | str = "."
) -> None:
    """Reconstruct a sealed plan and reject any forged or stale field."""
    try:
        expected = seal_readiness_plan(
            case_id=plan.case_id,
            profile_ref=plan.profile_ref,
            issued_at=plan.issued_at,
            expires_at=plan.expires_at,
            max_browser_actions=plan.max_browser_actions,
            max_request_equivalents=plan.max_request_equivalents,
            max_wall_seconds=plan.max_wall_seconds,
            max_cost_cents=plan.max_cost_cents,
            repo_root=repo_root,
        )
    except (AttributeError, ContractError, TypeError) as exc:
        raise ContractError("readiness_plan_invalid") from exc
    if plan != expected:
        raise ContractError("readiness_plan_mismatch")


def verify_readiness_grant(
    plan: SealedReadinessPlan,
    grant: ReadinessGrant,
    *,
    now: datetime,
    repo_root: Path | str = ".",
) -> None:
    verify_readiness_plan(plan, repo_root=repo_root)
    if grant != ReadinessGrant.for_plan(plan):
        raise ContractError("readiness_grant_mismatch")
    if now.tzinfo is None:
        raise ContractError("timestamp_must_be_timezone_aware")
    current = now.astimezone(timezone.utc)
    if current >= _parse_timestamp(plan.expires_at):
        raise ContractError("readiness_grant_expired")


def receipt_from_dict(payload: Mapping[str, Any]) -> ReadinessAuditReceipt:
    fields = {
        "schema_version",
        "campaign_id",
        "state",
        "created_at",
        "catalog_sha256",
        "source_sha256",
        "capabilities",
        "eligible_case_ids",
        "selected_case_id",
        "next_gate",
        "effect_census",
        "receipt_sha256",
    }
    if set(payload) != fields:
        raise ContractError("readiness_receipt_schema_mismatch")
    raw_capabilities = payload.get("capabilities")
    if not isinstance(raw_capabilities, list):
        raise ContractError("readiness_capabilities_must_be_array")
    capability_fields = set(ReadinessCapability.__dataclass_fields__)
    capabilities = []
    for raw in raw_capabilities:
        if not isinstance(raw, Mapping) or set(raw) != capability_fields:
            raise ContractError("readiness_capability_schema_mismatch")
        for field_name in capability_fields - {"readiness_only"}:
            if not isinstance(raw[field_name], str):
                raise ContractError("readiness_capability_type_mismatch")
        if not isinstance(raw["readiness_only"], bool):
            raise ContractError("readiness_capability_type_mismatch")
        capabilities.append(ReadinessCapability(**raw))
    eligible = payload.get("eligible_case_ids")
    if not isinstance(eligible, list) or not all(
        isinstance(item, str) for item in eligible
    ):
        raise ContractError("eligible_case_ids_must_be_array")
    effects = payload.get("effect_census")
    if (
        not isinstance(effects, Mapping)
        or set(effects) != set(_EFFECT_KEYS)
        or any(
            not isinstance(value, int) or isinstance(value, bool)
            for value in effects.values()
        )
    ):
        raise ContractError("readiness_effect_census_must_be_object")
    string_fields = (
        "campaign_id",
        "state",
        "created_at",
        "catalog_sha256",
        "source_sha256",
        "next_gate",
        "receipt_sha256",
    )
    if not isinstance(payload["schema_version"], int) or isinstance(
        payload["schema_version"], bool
    ):
        raise ContractError("readiness_receipt_type_mismatch")
    if any(not isinstance(payload[field], str) for field in string_fields):
        raise ContractError("readiness_receipt_type_mismatch")
    if payload["selected_case_id"] is not None and not isinstance(
        payload["selected_case_id"], str
    ):
        raise ContractError("readiness_receipt_type_mismatch")
    return ReadinessAuditReceipt(
        schema_version=payload["schema_version"],
        campaign_id=payload["campaign_id"],
        state=payload["state"],
        created_at=payload["created_at"],
        catalog_sha256=payload["catalog_sha256"],
        source_sha256=payload["source_sha256"],
        capabilities=tuple(capabilities),
        eligible_case_ids=tuple(eligible),
        selected_case_id=payload["selected_case_id"],
        next_gate=payload["next_gate"],
        effect_census=dict(effects),
        receipt_sha256=payload["receipt_sha256"],
    )
