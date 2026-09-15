import hashlib
import json
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
from lib import service_acquisition_worker


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
    assert observation.details["adapter_seam"] == (
        "service_acquisition_worker._youtube_adapter"
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


def test_command_tracer_calls_production_adapter_with_exact_argv_and_ignores_poison_path(
    tmp_path, monkeypatch
):
    poison_dir = tmp_path / "poison-bin"
    poison_dir.mkdir()
    poison_marker = tmp_path / "poison-ran"
    poison = poison_dir / "yt-dlp"
    poison.write_text(
        f"#!/bin/sh\nprintf poisoned > {poison_marker}\n",
        encoding="utf-8",
    )
    poison.chmod(0o700)
    monkeypatch.setenv("PATH", str(poison_dir))
    monkeypatch.setenv("LAST30DAYS_YOUTUBE_SSH_HOST", "poison-host")

    calls = []
    production_adapter = service_acquisition_worker._youtube_adapter

    def spy(request, config):
        calls.append((request.adapter, request.source))
        return production_adapter(request, config)

    monkeypatch.setattr(service_acquisition_worker, "_youtube_adapter", spy)
    observation = CommandTracer(REPO_ROOT)(_youtube_case(), item_limit=1)

    fixture = json.loads(
        (REPO_ROOT / "tests/provider_acceptance/fixtures/youtube.json").read_text()
    )
    encoded_argv = json.dumps(
        fixture["transport"]["expected_argv"],
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode()
    assert calls == [("youtube_ytdlp", "youtube")]
    assert not poison_marker.exists()
    assert observation.transport_success
    assert observation.details["invocation_count"] == 1
    assert observation.details["command_argv_sha256"] == (
        "sha256:" + hashlib.sha256(encoded_argv).hexdigest()
    )


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
        '"--flat-playlist","--dump-json","--no-warnings","--no-download"],'
        '"stdout_items":[{"id":"id","title":"' + ("x" * 66_000)
        + '","url":"https://www.youtube.com/watch?v=id"}]}}',
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
