import hashlib
from dataclasses import replace
from pathlib import Path

import pytest

from dev.last30days.provider_acceptance.campaign import prepare
from dev.last30days.provider_acceptance.campaign import execute, verify
from dev.last30days.provider_acceptance.catalog import default_catalog
from dev.last30days.provider_acceptance.command_tracer import CommandTracer
from dev.last30days.provider_acceptance.contracts import (
    AcceptanceDependencies,
    AdapterCase,
    CampaignSpec,
    ContractError,
    EvidenceTier,
    ExecutionGrant,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


def _youtube_case():
    plan = prepare(
        CampaignSpec(
            "wi010-command-focused",
            ("youtube-command",),
            tiers=(EvidenceTier.P2,),
        ),
        catalog=default_catalog(),
        repo_root=REPO_ROOT,
    )
    return plan.cases[0]


def test_command_tracer_uses_one_owned_fake_executable_and_worker_normalization():
    observation = CommandTracer(REPO_ROOT)(_youtube_case(), item_limit=1)

    assert observation.outcome == "success"
    assert observation.transport_success
    assert observation.item_count == 1
    assert observation.request_count == 1
    assert observation.accounting_confidence == "opaque_request_equivalent"
    assert observation.safe_reason_code is None
    assert observation.raw_safe_sha256.startswith("sha256:")
    assert observation.details["normalization_seam"] == (
        "service_acquisition_worker.execute_work"
    )
    assert observation.details["invocation_count"] == 1
    assert observation.details["stdout_bytes"] <= 65_536
    assert observation.details["exact_owner_cleanup"] is True
    assert observation.details["owner_census"] == 0
    for field in (
        "command_argv_sha256",
        "executable_sha256",
        "stdout_sha256",
        "normalized_result_sha256",
    ):
        assert observation.details[field].startswith("sha256:")
    assert "provider free acquisition boundaries" not in str(observation.details)


def test_command_tracer_produces_an_independently_verifiable_p2_receipt():
    plan = prepare(
        CampaignSpec(
            "wi010-command-receipt",
            ("youtube-command",),
            tiers=(EvidenceTier.P2,),
        ),
        catalog=default_catalog(),
        repo_root=REPO_ROOT,
    )
    receipt = execute(
        plan,
        grant=ExecutionGrant.for_plan(plan),
        deps=AcceptanceDependencies(
            {"command": CommandTracer(REPO_ROOT)},
            lambda *_args, **_kwargs: None,
        ),
        repo_root=REPO_ROOT,
    )

    verdict = verify(receipt, plan=plan)
    assert verdict.accepted
    assert verdict.verified_samples == verdict.expected_samples == 1
    assert receipt.samples[0].request_count == 1
    assert receipt.samples[0].evidence["invocation_count"] == 1


def test_command_tracer_rejects_non_owned_transport_before_invocation():
    sealed = _youtube_case()
    wrong = replace(
        sealed,
        case=AdapterCase(
            "youtube-command",
            "youtube_ytdlp",
            "youtube",
            "http",
            sealed.case.fixture_path,
            accounting_confidence="opaque_request_equivalent",
        ),
    )

    with pytest.raises(ContractError, match="rejects non-owned transport"):
        CommandTracer(REPO_ROOT)(wrong, item_limit=1)


def test_command_tracer_rejects_fixture_drift_before_invocation(tmp_path):
    sealed = _youtube_case()
    fixture = tmp_path / sealed.case.fixture_path
    fixture.parent.mkdir(parents=True)
    fixture.write_text('{"items":[],"transport":{}}', encoding="utf-8")

    with pytest.raises(ContractError, match="fixture digest mismatch"):
        CommandTracer(tmp_path)(sealed, item_limit=1)


def test_command_tracer_fails_closed_on_bounded_stdout(tmp_path):
    fixture = tmp_path / "youtube.json"
    fixture.write_text(
        '{"items":[{"video_id":"id","title":"' + ("x" * 66_000)
        + '","url":"https://www.youtube.com/watch?v=id"}],'
        '"transport":{"query":"bounded","from_date":"2026-08-15",'
        '"to_date":"2026-09-14","expected_argv":['
        '"--ignore-config","--no-cookies-from-browser","ytsearch8:bounded",'
        '"--flat-playlist","--dump-json","--no-warnings","--no-download"]}}',
        encoding="utf-8",
    )
    digest = "sha256:" + hashlib.sha256(fixture.read_bytes()).hexdigest()
    sealed = replace(
        _youtube_case(),
        case=AdapterCase(
            "youtube-command",
            "youtube_ytdlp",
            "youtube",
            "command",
            "youtube.json",
            accounting_confidence="opaque_request_equivalent",
        ),
        fixture_sha256=digest,
    )

    observation = CommandTracer(tmp_path)(sealed, item_limit=1)

    assert observation.outcome == "bounded_output_exceeded"
    assert not observation.transport_success
    assert observation.item_count == 0
    assert observation.request_count == 1
    assert observation.safe_reason_code == "bounded_output_exceeded"
    assert observation.details["stdout_bytes"] == 0
    assert observation.details["invocation_count"] == 1
    assert observation.details["exact_owner_cleanup"] is True
