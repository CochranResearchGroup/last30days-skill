"""Pure sealing, bounded execution, and independent receipt verification."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any, Mapping

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


def _canonical(payload: object) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode()


def _digest(payload: object) -> str:
    return "sha256:" + hashlib.sha256(_canonical(payload)).hexdigest()


def _file_digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _without_digest(payload: Mapping[str, Any], field: str) -> dict[str, Any]:
    value = dict(payload)
    value[field] = ""
    return value


def prepare(
    spec: CampaignSpec,
    *,
    catalog: AcceptanceCatalog,
    repo_root: Path | str = ".",
) -> SealedPlan:
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
        "source_sha256": _digest(source_payload),
        "plan_sha256": "",
    }
    return SealedPlan(
        **{**unsigned, "cases": tuple(cases), "tiers": tuple(unsigned["tiers"]), "plan_sha256": _digest(unsigned)}
    )


def _validate_grant(plan: SealedPlan, grant: ExecutionGrant) -> None:
    expected = ExecutionGrant.for_plan(plan)
    if grant != expected:
        raise ContractError("execution_grant_mismatch")


def _fixture_observation(case: SealedCase, repo_root: Path) -> TransportObservation:
    payload = json.loads((repo_root / case.case.fixture_path).read_text())
    if not isinstance(payload, dict) or not isinstance(payload.get("items"), list):
        return TransportObservation("parser_drift", True, 0, 0, "malformed_output", "exact", _digest(payload))
    count = len(payload["items"])
    return TransportObservation("success", True, count, 0, None, "exact", _digest(payload), {"fixture_replay": True})


def _sample(case: SealedCase, tier: str, observation: TransportObservation, teardown: Mapping[str, Any] | None = None) -> SampleReceipt:
    if observation.item_count < 0 or observation.request_count < 0:
        raise ContractError("negative observed count")
    return SampleReceipt(
        case_id=case.case.case_id,
        adapter_id=case.case.adapter_id,
        source=case.case.source,
        tier=tier,
        fixture_sha256=case.fixture_sha256,
        outcome=observation.outcome,
        transport_success=observation.transport_success,
        content_yield=observation.item_count > 0,
        item_count=observation.item_count,
        request_count=observation.request_count,
        accounting_confidence=observation.accounting_confidence,
        safe_reason_code=observation.safe_reason_code,
        redaction="safe",
        teardown=dict(teardown or {"complete": True, "owner_census": 0}),
        evidence=dict(observation.details) | {"raw_safe_sha256": observation.raw_safe_sha256},
    )


def execute(
    plan: SealedPlan,
    *,
    grant: ExecutionGrant,
    deps: AcceptanceDependencies,
    repo_root: Path | str = ".",
) -> AcceptanceReceipt:
    """Execute only provider-free dependencies after exact grant validation."""
    _validate_grant(plan, grant)
    root = Path(repo_root).resolve()
    samples: list[SampleReceipt] = []
    first_failure = None
    requests = 0
    items = 0
    for case in plan.cases:
        for tier in plan.tiers:
            if tier == EvidenceTier.P0.value:
                observation = TransportObservation("success", True, 0, 0, None, "exact", _digest(asdict(case.case)), {"catalog_sealed": True})
                sample = _sample(case, tier, observation)
            elif tier == EvidenceTier.P1.value:
                sample = _sample(case, tier, _fixture_observation(case, root))
            else:
                tracer = deps.tracer(case.case.transport)
                if tier == EvidenceTier.P2.value:
                    observation = tracer(case, item_limit=plan.max_items_per_case)
                    sample = _sample(case, tier, observation)
                elif tier == EvidenceTier.P3.value:
                    observation, teardown = deps.join_runner(case, tracer, item_limit=plan.max_items_per_case)
                    sample = _sample(case, tier, observation, teardown)
                else:
                    raise ContractError("unsupported evidence tier")
            if sample.request_count > plan.max_requests_per_case or sample.item_count > plan.max_items_per_case:
                raise ContractError("observed budget exhausted")
            requests += sample.request_count
            items += sample.item_count
            samples.append(sample)
            if sample.outcome != "success" and first_failure is None:
                first_failure = {"case_id": sample.case_id, "tier": sample.tier, "safe_reason_code": sample.safe_reason_code or sample.outcome}
    unsigned = {
        "schema_version": SCHEMA_VERSION,
        "campaign_id": plan.campaign_id,
        "plan_sha256": plan.plan_sha256,
        "catalog_sha256": plan.catalog_sha256,
        "source_sha256": plan.source_sha256,
        "effect_class": plan.effect_class,
        "grant_sha256": _digest(asdict(grant)),
        "samples": [asdict(sample) for sample in samples],
        "first_failure": first_failure,
        "observed_budgets": {"requests": requests, "items": items},
        "effect_census": {"credential_resolutions": 0, "external_provider_calls": 0, "real_browser_actions": 0, "installed_runtime_mutations": 0},
        "receipt_sha256": "",
    }
    return AcceptanceReceipt(**{**unsigned, "samples": tuple(samples), "receipt_sha256": _digest(unsigned)})


def verify(receipt: AcceptanceReceipt, *, plan: SealedPlan) -> AcceptanceVerdict:
    """Verify a receipt without resolving or invoking any dependency."""
    reasons: list[str] = []
    payload = receipt.to_dict()
    if _digest(_without_digest(payload, "receipt_sha256")) != receipt.receipt_sha256:
        reasons.append("receipt_digest_mismatch")
    if receipt.plan_sha256 != plan.plan_sha256 or receipt.catalog_sha256 != plan.catalog_sha256 or receipt.source_sha256 != plan.source_sha256:
        reasons.append("sealed_identity_mismatch")
    expected = {(case.case.case_id, tier) for case in plan.cases for tier in plan.tiers}
    observed = {(sample.case_id, sample.tier) for sample in receipt.samples}
    if observed != expected or len(observed) != len(receipt.samples):
        reasons.append("sample_set_mismatch")
    if receipt.effect_class != "provider_free" or any(receipt.effect_census.values()):
        reasons.append("effect_boundary_violation")
    for sample in receipt.samples:
        sealed = next((item for item in plan.cases if item.case.case_id == sample.case_id), None)
        if sealed is None or sample.adapter_id != sealed.case.adapter_id or sample.fixture_sha256 != sealed.fixture_sha256:
            reasons.append("sample_identity_mismatch")
            break
        if sample.request_count > plan.max_requests_per_case or sample.item_count > plan.max_items_per_case:
            reasons.append("sample_budget_exhausted")
            break
        if sample.redaction != "safe" or not sample.teardown.get("complete") or sample.teardown.get("owner_census") != 0:
            reasons.append("unsafe_lifecycle_evidence")
            break
        if sample.outcome != "success":
            reasons.append("sample_not_accepted")
            break
    return AcceptanceVerdict(not reasons, tuple(dict.fromkeys(reasons)), len(observed & expected), len(expected))


def receipt_from_dict(payload: Mapping[str, Any]) -> AcceptanceReceipt:
    """Decode the exact public receipt schema for offline verification."""
    expected = {
        "schema_version", "campaign_id", "plan_sha256", "catalog_sha256",
        "source_sha256", "effect_class", "grant_sha256", "samples",
        "first_failure", "observed_budgets", "effect_census", "receipt_sha256",
    }
    if set(payload) != expected or payload.get("schema_version") != SCHEMA_VERSION:
        raise ContractError("receipt_schema_mismatch")
    raw_samples = payload.get("samples")
    if not isinstance(raw_samples, list):
        raise ContractError("receipt_samples_must_be_array")
    sample_fields = {
        "case_id", "adapter_id", "source", "tier", "fixture_sha256",
        "outcome", "transport_success", "content_yield", "item_count",
        "request_count", "accounting_confidence", "safe_reason_code",
        "redaction", "teardown", "evidence",
    }
    samples = []
    for raw in raw_samples:
        if not isinstance(raw, Mapping) or set(raw) != sample_fields:
            raise ContractError("receipt_sample_schema_mismatch")
        samples.append(SampleReceipt(**raw))
    return AcceptanceReceipt(
        schema_version=payload["schema_version"],
        campaign_id=payload["campaign_id"],
        plan_sha256=payload["plan_sha256"],
        catalog_sha256=payload["catalog_sha256"],
        source_sha256=payload["source_sha256"],
        effect_class=payload["effect_class"],
        grant_sha256=payload["grant_sha256"],
        samples=tuple(samples),
        first_failure=payload["first_failure"],
        observed_budgets=payload["observed_budgets"],
        effect_census=payload["effect_census"],
        receipt_sha256=payload["receipt_sha256"],
    )
