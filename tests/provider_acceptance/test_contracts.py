from dataclasses import replace
import json
from pathlib import Path

import pytest

from dev.last30days.provider_acceptance import (
    AcceptanceDependencies,
    CampaignSpec,
    EvidenceTier,
    ExecutionGrant,
    prepare,
    verify,
)
from dev.last30days.provider_acceptance.catalog import default_catalog
from dev.last30days.provider_acceptance.contracts import ContractError
from dev.last30days.provider_acceptance.contracts import TransportObservation


ROOT = Path(__file__).resolve().parents[2]


def _fixtures(tmp_path):
    catalog = default_catalog()
    for case in catalog.cases:
        path = tmp_path / case.fixture_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"items": [{
            "id": case.case_id,
            "url": f"https://x.com/fixture/status/{case.case_id}",
            "text": "Provider-free acceptance fixture.",
            "date": "2026-09-12",
        }]}))
    return catalog


def test_prepare_seals_exactly_eight_adapters_without_dependency_resolution(tmp_path):
    catalog = _fixtures(tmp_path)
    plan = prepare(CampaignSpec("wi010", tuple(case.case_id for case in catalog.cases)), catalog=catalog, repo_root=tmp_path)
    assert len(plan.cases) == 8
    assert len({case.case.adapter_id for case in plan.cases}) == 8
    assert plan.tiers == ("P0", "P1", "P2", "P3")


def test_grant_is_checked_before_dependency_resolution(tmp_path):
    from dev.last30days.provider_acceptance.campaign import execute

    catalog = _fixtures(tmp_path)
    plan = prepare(CampaignSpec("wi010", (catalog.cases[0].case_id,), tiers=(EvidenceTier.P0,)), catalog=catalog, repo_root=tmp_path)
    touched = []
    deps = AcceptanceDependencies({}, lambda *_args, **_kwargs: None, touched.append)
    with pytest.raises(ContractError, match="execution_grant_mismatch"):
        execute(plan, grant=replace(ExecutionGrant.for_plan(plan), effect_class="external"), deps=deps, repo_root=tmp_path)
    assert touched == []


def test_independent_verifier_detects_tampering(tmp_path):
    from dev.last30days.provider_acceptance.campaign import execute
    from dev.last30days.provider_acceptance.campaign import receipt_from_dict

    catalog = _fixtures(tmp_path)
    plan = prepare(CampaignSpec("wi010", (catalog.cases[0].case_id,), tiers=(EvidenceTier.P0, EvidenceTier.P1)), catalog=catalog, repo_root=tmp_path)
    deps = AcceptanceDependencies({}, lambda *_args, **_kwargs: None)
    receipt = execute(plan, grant=ExecutionGrant.for_plan(plan), deps=deps, repo_root=tmp_path)
    assert verify(receipt, plan=plan).accepted
    assert verify(receipt_from_dict(receipt.to_dict()), plan=plan).accepted
    assert not verify(replace(receipt, source_sha256="sha256:tampered"), plan=plan).accepted


def test_recomputed_campaign_and_grant_forgery_is_rejected(tmp_path):
    from dev.last30days.provider_acceptance.campaign import _digest, execute, receipt_from_dict

    catalog = _fixtures(tmp_path)
    plan = prepare(CampaignSpec("wi010", (catalog.cases[0].case_id,), tiers=(EvidenceTier.P0,)), catalog=catalog, repo_root=tmp_path)
    receipt = execute(plan, grant=ExecutionGrant.for_plan(plan), deps=AcceptanceDependencies({}, lambda *_args, **_kwargs: None), repo_root=tmp_path)
    forged = receipt.to_dict()
    forged["campaign_id"] = "forged-campaign"
    forged["grant_sha256"] = "sha256:" + "0" * 64
    forged["receipt_sha256"] = ""
    forged["receipt_sha256"] = _digest(forged)
    assert not verify(receipt_from_dict(forged), plan=plan).accepted


def test_recomputed_evidence_digest_forgery_is_rejected(tmp_path):
    from dev.last30days.provider_acceptance.campaign import _digest, execute, receipt_from_dict

    catalog = _fixtures(tmp_path)
    plan = prepare(CampaignSpec("wi010", (catalog.cases[0].case_id,), tiers=(EvidenceTier.P0,)), catalog=catalog, repo_root=tmp_path)
    receipt = execute(plan, grant=ExecutionGrant.for_plan(plan), deps=AcceptanceDependencies({}, lambda *_args, **_kwargs: None), repo_root=tmp_path)
    forged = receipt.to_dict()
    forged["samples"][0]["evidence"]["raw_safe_sha256"] = "sha256:" + "0" * 64
    forged["receipt_sha256"] = ""
    forged["receipt_sha256"] = _digest(forged)
    assert not verify(receipt_from_dict(forged), plan=plan).accepted


def test_recomputed_p3_teardown_forgery_is_rejected(monkeypatch):
    from dev.last30days.provider_acceptance.browser_tracer import BrowserTracer
    from dev.last30days.provider_acceptance.campaign import _digest, execute, receipt_from_dict
    from dev.last30days.provider_acceptance.isolated_join import IsolatedServiceJoin

    catalog = default_catalog()
    case = next(case for case in catalog.cases if case.transport == "browser")
    plan = prepare(CampaignSpec("wi010", (case.case_id,), tiers=(EvidenceTier.P3,)), catalog=catalog, repo_root=ROOT)
    observation = TransportObservation("success", True, case.expected_item_count, 1, None, case.accounting_confidence, "sha256:" + "4" * 64, {"exact_owner_teardown": True, "owner_census": 0})
    monkeypatch.setattr(BrowserTracer, "__call__", lambda *_args, **_kwargs: observation)
    receipt = execute(plan, grant=ExecutionGrant.for_plan(plan), deps=AcceptanceDependencies({"browser": BrowserTracer(ROOT)}, IsolatedServiceJoin()), repo_root=ROOT)
    assert verify(receipt, plan=plan).accepted
    forged = receipt.to_dict()
    forged["samples"][0]["teardown"]["owner_sha256"] = "sha256:" + "0" * 64
    forged["receipt_sha256"] = ""
    forged["receipt_sha256"] = _digest(forged)
    assert not verify(receipt_from_dict(forged), plan=plan).accepted

    forged = receipt.to_dict()
    forged["samples"][0]["teardown"]["socket_closed"] = False
    forged["samples"][0]["teardown"]["teardown_sha256"] = _digest({key: value for key, value in forged["samples"][0]["teardown"].items() if key != "teardown_sha256"})
    forged["receipt_sha256"] = ""
    forged["receipt_sha256"] = _digest(forged)
    assert not verify(receipt_from_dict(forged), plan=plan).accepted


def test_unowned_dependency_fails_closed_without_invocation():
    from dev.last30days.provider_acceptance.campaign import execute
    from dev.last30days.provider_acceptance.isolated_join import IsolatedServiceJoin

    catalog = default_catalog()
    case = next(case for case in catalog.cases if case.adapter_id == "reddit_keyless")
    plan = prepare(CampaignSpec("wi010", (case.case_id,), tiers=(EvidenceTier.P2,)), catalog=catalog, repo_root=ROOT)
    called = []

    def unowned(*_args, **_kwargs):
        called.append(True)

    receipt = execute(plan, grant=ExecutionGrant.for_plan(plan), deps=AcceptanceDependencies({"http": unowned}, IsolatedServiceJoin()), repo_root=ROOT)
    assert called == []
    assert receipt.first_failure["safe_reason_code"] == "unexpected_contracterror"
    assert receipt.effect_census["external_provider_calls"] == 0
    assert not verify(receipt, plan=plan).accepted


def test_redaction_rejects_prohibited_observation_details(monkeypatch):
    from dev.last30days.provider_acceptance.campaign import execute
    from dev.last30days.provider_acceptance.http_tracer import HttpTracer
    from dev.last30days.provider_acceptance.isolated_join import IsolatedServiceJoin

    catalog = default_catalog()
    case = next(case for case in catalog.cases if case.adapter_id == "reddit_keyless")
    plan = prepare(CampaignSpec("wi010", (case.case_id,), tiers=(EvidenceTier.P2,)), catalog=catalog, repo_root=ROOT)
    monkeypatch.setattr(HttpTracer, "__call__", lambda *_args, **_kwargs: TransportObservation("success", True, 1, 1, None, "exact", "sha256:" + "1" * 64, {"authorization": "dummy-value"}))
    receipt = execute(plan, grant=ExecutionGrant.for_plan(plan), deps=AcceptanceDependencies({"http": HttpTracer(ROOT)}, IsolatedServiceJoin()), repo_root=ROOT)
    assert receipt.samples[0].redaction == "failed"
    assert "dummy-value" not in json.dumps(receipt.to_dict())
    assert not verify(receipt, plan=plan).accepted


def test_cumulative_request_budget_stops_before_second_transport(monkeypatch):
    from dev.last30days.provider_acceptance.campaign import execute
    from dev.last30days.provider_acceptance.http_tracer import HttpTracer
    from dev.last30days.provider_acceptance.isolated_join import IsolatedServiceJoin

    catalog = default_catalog()
    case = next(case for case in catalog.cases if case.adapter_id == "reddit_keyless")
    plan = prepare(CampaignSpec("wi010", (case.case_id,), tiers=(EvidenceTier.P2, EvidenceTier.P3), max_requests_per_case=1), catalog=catalog, repo_root=ROOT)
    calls = []
    observation = TransportObservation("success", True, 1, 1, None, "exact", "sha256:" + "2" * 64, {"exact_owner_cleanup": True, "owner_census": 0})
    monkeypatch.setattr(HttpTracer, "__call__", lambda *_args, **_kwargs: calls.append(True) or observation)
    receipt = execute(plan, grant=ExecutionGrant.for_plan(plan), deps=AcceptanceDependencies({"http": HttpTracer(ROOT)}, IsolatedServiceJoin()), repo_root=ROOT)
    assert calls == [True]
    assert receipt.samples[-1].safe_reason_code == "case_request_budget_exhausted"
    assert receipt.observed_budgets["requests"] == 1


def test_exception_preserves_finalized_samples_and_first_failure(monkeypatch):
    from dev.last30days.provider_acceptance.campaign import execute
    from dev.last30days.provider_acceptance.http_tracer import HttpTracer
    from dev.last30days.provider_acceptance.isolated_join import IsolatedServiceJoin

    catalog = default_catalog()
    cases = tuple(case for case in catalog.cases if case.transport == "http")
    plan = prepare(CampaignSpec("wi010", tuple(case.case_id for case in cases), tiers=(EvidenceTier.P2,)), catalog=catalog, repo_root=ROOT)
    calls = []

    def trace(_self, case, *, item_limit):
        calls.append(case.case.case_id)
        if len(calls) == 2:
            raise RuntimeError("private failure text")
        return TransportObservation("success", True, 1, 1, None, "exact", "sha256:" + "3" * 64, {"exact_owner_cleanup": True, "owner_census": 0})

    monkeypatch.setattr(HttpTracer, "__call__", trace)
    receipt = execute(plan, grant=ExecutionGrant.for_plan(plan), deps=AcceptanceDependencies({"http": HttpTracer(ROOT)}, IsolatedServiceJoin()), repo_root=ROOT)
    assert len(receipt.samples) == 2
    assert receipt.samples[0].claim_accepted
    assert receipt.first_failure["case_id"] == cases[1].case_id
    assert "private failure text" not in json.dumps(receipt.to_dict())
