from dataclasses import replace
import json

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


def _fixtures(tmp_path):
    catalog = default_catalog()
    for case in catalog.cases:
        path = tmp_path / case.fixture_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"items": [{"id": case.case_id}]}))
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
