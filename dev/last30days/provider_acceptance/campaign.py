"""Pure sealing, bounded execution, and independent receipt verification."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from skills.last30days.scripts.lib import service_acquisition_worker
from skills.last30days.scripts.lib import service_contracts

from .contracts import (
    SCHEMA_VERSION,
    AcceptanceCatalog,
    AcceptanceDependencies,
    AcceptanceReceipt,
    AcceptanceVerdict,
    CampaignSpec,
    ContractError,
    EvidenceTier,
    ExecutionGrant,
    SampleReceipt,
    SealedCase,
    SealedPlan,
    TransportObservation,
)


_P1_SCENARIOS = ("positive", "zero_yield", "malformed", "provenance", "bounded_error")
_IMPLEMENTATION_ROOT = Path(__file__).resolve().parents[3]
_ALLOWED_EVIDENCE_KEYS = frozenset(
    {
        "raw_safe_sha256", "catalog_sealed", "fixture_replay",
        "normalization_seam", "normalized_result_sha256", "provenance_complete",
        "expected_safe_error_code", "adapter_variant", "loopback", "owned_server",
        "request_method", "request_target_sha256", "server_request_count",
        "exact_owner_cleanup", "exact_owner_teardown", "owner_census",
        "command_argv_sha256", "executable_sha256", "stdout_bytes", "stdout_sha256",
        "invocation_count", "protocol", "route_sha256", "owner_sha256",
        "failure_class", "failure_stage", "production_adapter_invoked", "adapter_seam",
    }
)
_PROHIBITED_FRAGMENTS = (
    "authorization", "cookie", "credential", "password", "secret", "token",
    "environment", "private_text", "browser_route", "profile_path",
)


class _PendingSample(Exception):
    def __init__(self, samples: list[SampleReceipt]) -> None:
        self.samples = samples


def _canonical(payload: object) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode()


def _digest(payload: object) -> str:
    return "sha256:" + hashlib.sha256(_canonical(payload)).hexdigest()


def _file_digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _implementation_digests(root: Path) -> dict[str, str]:
    paths = (
        "dev/last30days/provider_acceptance/contracts.py",
        "dev/last30days/provider_acceptance/catalog.py",
        "dev/last30days/provider_acceptance/campaign.py",
        "dev/last30days/provider_acceptance/http_tracer.py",
        "dev/last30days/provider_acceptance/command_tracer.py",
        "dev/last30days/provider_acceptance/browser_tracer.py",
        "dev/last30days/provider_acceptance/isolated_join.py",
        "dev/last30days/scripts/provider_acceptance.py",
        "skills/last30days/scripts/lib/service_acquisition_worker.py",
        "skills/last30days/scripts/lib/x_browser.py",
        "skills/last30days/scripts/lib/facebook.py",
        "skills/last30days/scripts/lib/linkedin.py",
        "skills/last30days/scripts/lib/reddit_browser.py",
        "skills/last30days/scripts/lib/reddit_keyless.py",
        "skills/last30days/scripts/lib/reddit.py",
        "skills/last30days/scripts/lib/youtube_yt.py",
    )
    return {path: _file_digest(root / path) for path in paths}


def _without_digest(payload: Mapping[str, Any], field: str) -> dict[str, Any]:
    value = dict(payload)
    value[field] = ""
    return value


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _valid_timestamp(value: object) -> bool:
    if not isinstance(value, str) or not value.endswith("Z"):
        return False
    try:
        datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError:
        return False
    return True


def _safe_evidence(details: Mapping[str, Any], raw_safe_sha256: str) -> tuple[dict[str, Any], bool]:
    if not (
        isinstance(raw_safe_sha256, str)
        and raw_safe_sha256.startswith("sha256:")
        and len(raw_safe_sha256) == 71
        and all(char in "0123456789abcdef" for char in raw_safe_sha256[7:])
    ):
        return {}, False
    evidence: dict[str, Any] = {"raw_safe_sha256": raw_safe_sha256}
    for raw_key, value in details.items():
        key = str(raw_key).casefold()
        if key not in _ALLOWED_EVIDENCE_KEYS or any(fragment in key for fragment in _PROHIBITED_FRAGMENTS):
            return {"raw_safe_sha256": raw_safe_sha256}, False
        if isinstance(value, bool) or value is None:
            evidence[key] = value
        elif isinstance(value, int) and not isinstance(value, bool) and 0 <= value <= 2_147_483_647:
            evidence[key] = value
        elif isinstance(value, str) and len(value) <= 256 and not any(fragment in value.casefold() for fragment in _PROHIBITED_FRAGMENTS):
            if key.endswith("sha256") and not value.startswith("sha256:"):
                return {"raw_safe_sha256": raw_safe_sha256}, False
            evidence[key] = value
        else:
            return {"raw_safe_sha256": raw_safe_sha256}, False
    return evidence, True


def prepare(spec: CampaignSpec, *, catalog: AcceptanceCatalog, repo_root: Path | str = ".") -> SealedPlan:
    """Seal exact catalog cases and fixture bytes without resolving transports."""
    selected = {case.case_id: case for case in catalog.cases}
    unknown = sorted(set(spec.case_ids) - set(selected))
    if unknown:
        raise ContractError(f"unknown case_ids: {','.join(unknown)}")
    root = Path(repo_root).resolve()
    cases = []
    for case_id in spec.case_ids:
        case = selected[case_id]
        fixture = (root / case.fixture_path).resolve()
        if root not in fixture.parents or not fixture.is_file():
            raise ContractError(f"fixture unavailable: {case.case_id}")
        cases.append(SealedCase(case, _file_digest(fixture)))
    catalog_payload = [asdict(item) for item in catalog.cases]
    source_payload = [asdict(item.case) | {"fixture_sha256": item.fixture_sha256} for item in cases]
    unsigned = {
        "schema_version": SCHEMA_VERSION,
        "campaign_id": spec.campaign_id,
        "cases": source_payload,
        "tiers": [tier.value for tier in spec.tiers],
        "effect_class": spec.effect_class,
        "max_requests_per_case": spec.max_requests_per_case,
        "max_items_per_case": spec.max_items_per_case,
        "wall_timeout_seconds": spec.wall_timeout_seconds,
        "catalog_sha256": _digest(catalog_payload),
        "source_sha256": _digest({"cases": source_payload, "implementation": _implementation_digests(_IMPLEMENTATION_ROOT)}),
        "plan_sha256": "",
    }
    return SealedPlan(**{**unsigned, "cases": tuple(cases), "tiers": tuple(unsigned["tiers"]), "plan_sha256": _digest(unsigned)})


def _validate_grant(plan: SealedPlan, grant: ExecutionGrant) -> None:
    if grant != ExecutionGrant.for_plan(plan):
        raise ContractError("execution_grant_mismatch")


def _worker_request(case: SealedCase, item_limit: int) -> service_contracts.AcquisitionWorkRequest:
    return service_contracts.AcquisitionWorkRequest.from_dict(
        {
            "schema_version": 1,
            "work_id": f"wi010-replay-{case.case.case_id}",
            "job_id": "wi010-provider-free-p1",
            "lease_generation": 1,
            "attempt": 1,
            "profile_id": "provider-free",
            "source": case.case.source,
            "query": "provider acceptance fixture",
            "from_date": "2026-08-15",
            "to_date": "2026-09-14",
            "depth": "quick",
            "adapter": case.case.adapter_id,
            "adapter_version": "1",
            "wall_timeout_seconds": 10,
            "item_limit": item_limit,
            "network_request_limit": 1,
            "cost_budget_cents": 0,
            "surface_kind": "profile" if case.case.adapter_id == "linkedin_profile_agent_browser" else "topic",
        }
    )


def _run_replay(case: SealedCase, raw: Mapping[str, Any], item_limit: int):
    return service_acquisition_worker.execute_work(
        _worker_request(case, item_limit),
        {},
        adapters={case.case.adapter_id: lambda _request, _config: dict(raw)},
        clock=lambda: datetime(2026, 9, 14, 12, 0, tzinfo=timezone.utc),
    )


def _replay_samples(case: SealedCase, repo_root: Path, item_limit: int) -> list[tuple[str, TransportObservation, bool]]:
    payload = json.loads((repo_root / case.case.fixture_path).read_text())
    if not isinstance(payload, dict) or not isinstance(payload.get("items"), list):
        raise ContractError("sealed fixture schema mismatch")
    items = payload["items"]
    outputs: list[tuple[str, TransportObservation, bool]] = []
    for scenario in _P1_SCENARIOS:
        if scenario in {"positive", "provenance"}:
            raw = {"items": items, "diagnostics": {"accepted_count": len(items)}}
        elif scenario == "zero_yield":
            raw = {"items": [], "diagnostics": {"accepted_count": 0}}
        elif scenario == "malformed":
            raw = {"items": [{"malformed": True}], "error_type": "malformed_output", "diagnostics": {"failure_stage": "fixture_parse"}}
        else:
            raw = {"items": [], "error_type": "rate_limited", "diagnostics": {"failure_stage": "fixture_boundary"}}
        result = _run_replay(case, raw, item_limit)
        provenance = all(item.source_native_id and item.url and item.text for item in result.items)
        if scenario == "positive":
            accepted = result.safe_error_code is None and result.item_count == case.case.expected_item_count
            outcome, expected_error = "success", None
        elif scenario == "zero_yield":
            accepted = result.safe_error_code is None and result.item_count == 0
            outcome, expected_error = "zero_yield", None
        elif scenario == "malformed":
            accepted = result.safe_error_code == "malformed_output" and result.item_count == 0
            outcome, expected_error = "parser_drift", "malformed_output"
        elif scenario == "provenance":
            accepted = result.safe_error_code is None and result.item_count == case.case.expected_item_count and provenance
            outcome, expected_error = "success", None
        else:
            accepted = result.safe_error_code == "rate_limited" and result.item_count == 0
            outcome, expected_error = "bounded_error", "rate_limited"
        safe_result = result.to_dict()
        observation = TransportObservation(
            outcome=outcome,
            transport_success=True,
            item_count=result.item_count,
            request_count=0,
            safe_reason_code=None if accepted else (result.safe_error_code or f"{scenario}_mismatch"),
            accounting_confidence="exact",
            raw_safe_sha256=_digest(safe_result),
            details={
                "fixture_replay": True,
                "normalization_seam": "service_acquisition_worker.execute_work",
                "normalized_result_sha256": _digest(safe_result),
                "provenance_complete": provenance if scenario == "provenance" else None,
                "expected_safe_error_code": expected_error,
            },
        )
        outputs.append((scenario, observation, accepted))
    return outputs


def _sample(case: SealedCase, tier: str, scenario: str, observation: TransportObservation, *, claim_accepted: bool, teardown: Mapping[str, Any] | None = None) -> SampleReceipt:
    evidence, redaction_safe = _safe_evidence(observation.details, observation.raw_safe_sha256)
    if observation.item_count < 0 or observation.request_count < 0:
        claim_accepted = False
    if not redaction_safe:
        claim_accepted = False
    return SampleReceipt(
        case_id=case.case.case_id,
        adapter_id=case.case.adapter_id,
        source=case.case.source,
        tier=tier,
        scenario=scenario,
        fixture_sha256=case.fixture_sha256,
        outcome=observation.outcome if redaction_safe else "redaction_failed",
        claim_accepted=claim_accepted,
        transport_success=observation.transport_success,
        content_yield=observation.item_count > 0,
        item_count=max(0, observation.item_count),
        request_count=max(0, observation.request_count),
        accounting_confidence=observation.accounting_confidence,
        safe_reason_code=observation.safe_reason_code if redaction_safe else "redaction_failed",
        redaction="safe" if redaction_safe else "failed",
        teardown=dict(teardown or {"complete": True, "owner_census": 0}),
        evidence=evidence,
    )


def _failure_observation(exc: Exception) -> TransportObservation:
    name = type(exc).__name__
    return TransportObservation("internal_harness_error", False, 0, 0, f"unexpected_{name.casefold()}", "exact", _digest({"exception_class": name}), {"failure_class": name})


def _expected_sample_keys(plan: SealedPlan) -> set[tuple[str, str, str]]:
    keys = set()
    for case in plan.cases:
        for tier in plan.tiers:
            scenarios = _P1_SCENARIOS if tier == "P1" else {"P0": ("catalog",), "P2": ("owned_transport",), "P3": ("isolated_join",)}[tier]
            keys.update((case.case.case_id, tier, scenario) for scenario in scenarios)
    return keys


def execute(plan: SealedPlan, *, grant: ExecutionGrant, deps: AcceptanceDependencies, repo_root: Path | str = ".") -> AcceptanceReceipt:
    """Execute closed provider-free dependencies after exact grant validation."""
    _validate_grant(plan, grant)
    if "P3" in plan.tiers:
        deps.validate_join_runner()
    root = Path(repo_root).resolve()
    started_at = _timestamp()
    samples: list[SampleReceipt] = []
    first_failure = None
    stopped = False
    for case in plan.cases:
        case_requests = 0
        case_items = 0
        for tier in plan.tiers:
            try:
                if tier == EvidenceTier.P0.value:
                    observation = TransportObservation("success", True, 0, 0, None, "exact", _digest(asdict(case.case)), {"catalog_sealed": True})
                    pending = [_sample(case, tier, "catalog", observation, claim_accepted=True)]
                elif tier == EvidenceTier.P1.value:
                    pending = [_sample(case, tier, scenario, observation, claim_accepted=accepted) for scenario, observation, accepted in _replay_samples(case, root, plan.max_items_per_case)]
                else:
                    if case_requests >= plan.max_requests_per_case:
                        observation = TransportObservation("budget_exhausted", False, 0, 0, "case_request_budget_exhausted", "exact", _digest({"case_id": case.case.case_id, "tier": tier}))
                        pending = [_sample(case, tier, "isolated_join" if tier == "P3" else "owned_transport", observation, claim_accepted=False)]
                        raise _PendingSample(pending)
                    tracer = deps.tracer(case.case.transport)
                    if tier == EvidenceTier.P2.value:
                        observation = tracer(case, item_limit=plan.max_items_per_case)
                        teardown = {"complete": bool(observation.details.get("exact_owner_cleanup") or observation.details.get("exact_owner_teardown")), "owner_census": int(observation.details.get("owner_census", 0))}
                        pending = [_sample(case, tier, "owned_transport", observation, claim_accepted=observation.outcome == "success", teardown=teardown)]
                    elif tier == EvidenceTier.P3.value:
                        observation, teardown = deps.join_runner(case, tracer, item_limit=plan.max_items_per_case)
                        pending = [_sample(case, tier, "isolated_join", observation, claim_accepted=observation.outcome == "success", teardown=teardown)]
                    else:
                        raise ContractError("unsupported evidence tier")
            except _PendingSample as exc:
                pending = exc.samples
            except Exception as exc:
                pending = [_sample(case, tier, "isolated_join" if tier == "P3" else "owned_transport", _failure_observation(exc), claim_accepted=False)]
            for sample in pending:
                case_requests += sample.request_count
                case_items += sample.item_count
                if case_requests > plan.max_requests_per_case or case_items > plan.max_items_per_case:
                    sample = replace(sample, claim_accepted=False, outcome="budget_exhausted", safe_reason_code="case_budget_exhausted")
                samples.append(sample)
                if not sample.claim_accepted and first_failure is None:
                    first_failure = {"case_id": sample.case_id, "tier": sample.tier, "scenario": sample.scenario, "safe_reason_code": sample.safe_reason_code or sample.outcome}
                    stopped = True
                    break
            if stopped:
                break
        if stopped:
            break
    requests = sum(sample.request_count for sample in samples)
    items = sum(sample.item_count for sample in samples)
    owned = sum(sample.request_count for sample in samples if sample.tier in {"P2", "P3"})
    joins = sum(1 for sample in samples if sample.tier == "P3")
    finished_at = _timestamp()
    unsigned = {
        "schema_version": SCHEMA_VERSION,
        "campaign_id": plan.campaign_id,
        "plan_sha256": plan.plan_sha256,
        "catalog_sha256": plan.catalog_sha256,
        "source_sha256": plan.source_sha256,
        "effect_class": plan.effect_class,
        "grant_sha256": _digest(asdict(grant)),
        "started_at": started_at,
        "finished_at": finished_at,
        "planned_budgets": {"requests_per_case": plan.max_requests_per_case, "items_per_case": plan.max_items_per_case, "wall_timeout_seconds": plan.wall_timeout_seconds},
        "samples": [asdict(sample) for sample in samples],
        "first_failure": first_failure,
        "observed_budgets": {"requests": requests, "items": items},
        "effect_census": {"owned_local_requests": owned, "isolated_join_runs": joins, "credential_resolutions": 0, "external_provider_calls": 0, "non_loopback_network_calls": 0, "real_browser_actions": 0, "installed_runtime_mutations": 0, "schedule_mutations": 0, "release_or_deployment_mutations": 0, "tracker_mutations": 0},
        "receipt_sha256": "",
    }
    return AcceptanceReceipt(**{**unsigned, "samples": tuple(samples), "receipt_sha256": _digest(unsigned)})


def verify(receipt: AcceptanceReceipt, *, plan: SealedPlan) -> AcceptanceVerdict:
    """Verify every claim from sealed inputs without resolving any dependency."""
    reasons: list[str] = []
    payload = receipt.to_dict()
    if receipt.schema_version != SCHEMA_VERSION or _digest(_without_digest(payload, "receipt_sha256")) != receipt.receipt_sha256:
        reasons.append("receipt_digest_mismatch")
    expected_grant = ExecutionGrant.for_plan(plan)
    if receipt.campaign_id != plan.campaign_id or receipt.plan_sha256 != plan.plan_sha256 or receipt.catalog_sha256 != plan.catalog_sha256 or receipt.source_sha256 != plan.source_sha256 or receipt.grant_sha256 != _digest(asdict(expected_grant)):
        reasons.append("sealed_identity_mismatch")
    expected_budgets = {"requests_per_case": plan.max_requests_per_case, "items_per_case": plan.max_items_per_case, "wall_timeout_seconds": plan.wall_timeout_seconds}
    if dict(receipt.planned_budgets) != expected_budgets:
        reasons.append("planned_budget_mismatch")
    if not _valid_timestamp(receipt.started_at) or not _valid_timestamp(receipt.finished_at) or receipt.finished_at < receipt.started_at:
        reasons.append("timestamp_invalid")
    expected = _expected_sample_keys(plan)
    observed = {(sample.case_id, sample.tier, sample.scenario) for sample in receipt.samples}
    if observed != expected or len(observed) != len(receipt.samples):
        reasons.append("sample_set_mismatch")
    effect_keys = {"owned_local_requests", "isolated_join_runs", "credential_resolutions", "external_provider_calls", "non_loopback_network_calls", "real_browser_actions", "installed_runtime_mutations", "schedule_mutations", "release_or_deployment_mutations", "tracker_mutations"}
    disallowed_effects = {key: value for key, value in receipt.effect_census.items() if key not in {"owned_local_requests", "isolated_join_runs"} and value}
    if receipt.effect_class != "provider_free" or set(receipt.effect_census) != effect_keys or disallowed_effects:
        reasons.append("effect_boundary_violation")
    requests = sum(sample.request_count for sample in receipt.samples)
    items = sum(sample.item_count for sample in receipt.samples)
    if dict(receipt.observed_budgets) != {"requests": requests, "items": items}:
        reasons.append("observed_budget_mismatch")
    if receipt.effect_census.get("owned_local_requests") != sum(sample.request_count for sample in receipt.samples if sample.tier in {"P2", "P3"}) or receipt.effect_census.get("isolated_join_runs") != sum(1 for sample in receipt.samples if sample.tier == "P3"):
        reasons.append("effect_ledger_mismatch")
    expected_first = next(({"case_id": sample.case_id, "tier": sample.tier, "scenario": sample.scenario, "safe_reason_code": sample.safe_reason_code or sample.outcome} for sample in receipt.samples if not sample.claim_accepted), None)
    if receipt.first_failure != expected_first:
        reasons.append("first_failure_mismatch")
    for sealed in plan.cases:
        case_samples = [sample for sample in receipt.samples if sample.case_id == sealed.case.case_id]
        if sum(sample.request_count for sample in case_samples) > plan.max_requests_per_case or sum(sample.item_count for sample in case_samples) > plan.max_items_per_case:
            reasons.append("case_budget_exhausted")
            break
    expected_outcomes = {"catalog": "success", "positive": "success", "zero_yield": "zero_yield", "malformed": "parser_drift", "provenance": "success", "bounded_error": "bounded_error", "owned_transport": "success", "isolated_join": "success"}
    for sample in receipt.samples:
        sealed = next((item for item in plan.cases if item.case.case_id == sample.case_id), None)
        if sealed is None or sample.adapter_id != sealed.case.adapter_id or sample.source != sealed.case.source or sample.fixture_sha256 != sealed.fixture_sha256:
            reasons.append("sample_identity_mismatch")
            break
        confidence = sealed.case.accounting_confidence if sample.tier in {"P2", "P3"} else "exact"
        evidence, safe = _safe_evidence(sample.evidence, sample.evidence.get("raw_safe_sha256", ""))
        expected_count = (
            0
            if sample.scenario in {"catalog", "zero_yield", "malformed", "bounded_error"}
            else sealed.case.expected_item_count
        )
        if not sample.claim_accepted or sample.outcome != expected_outcomes.get(sample.scenario) or sample.accounting_confidence != confidence or not sample.transport_success or sample.safe_reason_code is not None or sample.item_count != expected_count or sample.content_yield != (sample.item_count > 0) or sample.redaction != "safe" or not safe or evidence != dict(sample.evidence):
            reasons.append("sample_semantics_mismatch")
            break
        if sample.scenario == "provenance" and sample.evidence.get("provenance_complete") is not True:
            reasons.append("provenance_evidence_mismatch")
            break
        if sample.scenario in {"owned_transport", "isolated_join"} and sample.evidence.get("production_adapter_invoked") is not True:
            reasons.append("production_adapter_evidence_mismatch")
            break
        if not sample.teardown.get("complete") or sample.teardown.get("owner_census") != 0:
            reasons.append("unsafe_lifecycle_evidence")
            break
        if sample.tier in {"P0", "P1"} and sample.request_count != 0:
            reasons.append("unexpected_replay_effect")
            break
        if sample.tier in {"P2", "P3"} and sample.request_count != 1:
            reasons.append("transport_accounting_mismatch")
            break
    return AcceptanceVerdict(not reasons, tuple(dict.fromkeys(reasons)), len(observed & expected), len(expected))


def receipt_from_dict(payload: Mapping[str, Any]) -> AcceptanceReceipt:
    """Decode the exact public receipt schema for offline verification."""
    expected = {"schema_version", "campaign_id", "plan_sha256", "catalog_sha256", "source_sha256", "effect_class", "grant_sha256", "started_at", "finished_at", "planned_budgets", "samples", "first_failure", "observed_budgets", "effect_census", "receipt_sha256"}
    if set(payload) != expected or payload.get("schema_version") != SCHEMA_VERSION:
        raise ContractError("receipt_schema_mismatch")
    raw_samples = payload.get("samples")
    if not isinstance(raw_samples, list):
        raise ContractError("receipt_samples_must_be_array")
    sample_fields = {"case_id", "adapter_id", "source", "tier", "scenario", "fixture_sha256", "outcome", "claim_accepted", "transport_success", "content_yield", "item_count", "request_count", "accounting_confidence", "safe_reason_code", "redaction", "teardown", "evidence"}
    samples = []
    for raw in raw_samples:
        if not isinstance(raw, Mapping) or set(raw) != sample_fields:
            raise ContractError("receipt_sample_schema_mismatch")
        samples.append(SampleReceipt(**raw))
    return AcceptanceReceipt(
        schema_version=payload["schema_version"], campaign_id=payload["campaign_id"], plan_sha256=payload["plan_sha256"],
        catalog_sha256=payload["catalog_sha256"], source_sha256=payload["source_sha256"], effect_class=payload["effect_class"],
        grant_sha256=payload["grant_sha256"], started_at=payload["started_at"], finished_at=payload["finished_at"],
        planned_budgets=payload["planned_budgets"], samples=tuple(samples), first_failure=payload["first_failure"],
        observed_budgets=payload["observed_budgets"], effect_census=payload["effect_census"], receipt_sha256=payload["receipt_sha256"],
    )
