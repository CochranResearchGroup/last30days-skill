from __future__ import annotations

from dataclasses import asdict, replace
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import urllib.request

import pytest

from dev.last30days.provider_acceptance.contracts import ContractError
from dev.last30days.provider_acceptance.readiness import (
    AUDIT_STATE,
    NEXT_GATE,
    ReadinessGrant,
    _digest,
    audit_capabilities,
    capability_catalog,
    receipt_from_dict,
    seal_readiness_plan,
    verify_audit_receipt,
    verify_readiness_grant,
    verify_readiness_plan,
)
from dev.last30days.scripts.provider_readiness import main as readiness_main


ROOT = Path(__file__).resolve().parents[2]
NOW = datetime(2026, 9, 15, 18, 0, tzinfo=timezone.utc)


def test_capability_catalog_covers_exactly_eight_adapters():
    catalog = capability_catalog()
    assert len(catalog) == 8
    assert {item.adapter_id for item in catalog} == {
        "x_agent_browser",
        "facebook_agent_browser",
        "linkedin_agent_browser",
        "linkedin_profile_agent_browser",
        "youtube_ytdlp",
        "reddit_keyless",
        "reddit_agent_browser",
        "reddit_scrapecreators",
    }
    assert {item.adapter_id for item in catalog if item.readiness_only} == {
        "x_agent_browser",
        "facebook_agent_browser",
        "linkedin_agent_browser",
        "linkedin_profile_agent_browser",
        "reddit_agent_browser",
    }


def test_audit_is_effect_free_under_external_tripwires(monkeypatch):
    def deny(*_args, **_kwargs):
        raise AssertionError("external dependency was touched")

    monkeypatch.setattr(os, "getenv", deny)
    monkeypatch.setattr(shutil, "which", deny)
    monkeypatch.setattr(socket, "getaddrinfo", deny)
    monkeypatch.setattr(socket.socket, "connect", deny)
    monkeypatch.setattr(socket.socket, "connect_ex", deny)
    monkeypatch.setattr(subprocess, "Popen", deny)
    monkeypatch.setattr(urllib.request, "urlopen", deny)

    receipt = audit_capabilities(repo_root=ROOT, now=NOW)
    accepted, reasons = verify_audit_receipt(receipt, repo_root=ROOT)
    assert accepted, reasons
    assert receipt.state == AUDIT_STATE
    assert receipt.selected_case_id is None
    assert all(value == 0 for value in receipt.effect_census.values())


def test_receipt_round_trip_and_tamper_detection():
    receipt = audit_capabilities(repo_root=ROOT, now=NOW)
    decoded = receipt_from_dict(receipt.to_dict())
    assert verify_audit_receipt(decoded, repo_root=ROOT) == (True, ())

    forged = receipt.to_dict()
    forged["capabilities"][0]["readiness_only"] = False
    forged["receipt_sha256"] = ""
    forged["receipt_sha256"] = _digest(forged)
    accepted, reasons = verify_audit_receipt(receipt_from_dict(forged), repo_root=ROOT)
    assert not accepted
    assert "capability_catalog_mismatch" in reasons


def test_receipt_rejects_effect_or_selected_case_even_after_rehash():
    receipt = audit_capabilities(repo_root=ROOT, now=NOW)
    forged = receipt.to_dict()
    forged["selected_case_id"] = "x-browser"
    forged["effect_census"]["browser_actions"] = 1
    forged["receipt_sha256"] = ""
    forged["receipt_sha256"] = _digest(forged)
    accepted, reasons = verify_audit_receipt(receipt_from_dict(forged), repo_root=ROOT)
    assert not accepted
    assert "effect_state_mismatch" in reasons
    assert "effect_boundary_violation" in reasons


def test_receipt_decoder_rejects_ambiguous_boolean_types():
    forged = audit_capabilities(repo_root=ROOT, now=NOW).to_dict()
    forged["schema_version"] = True
    with pytest.raises(ContractError, match="type_mismatch"):
        receipt_from_dict(forged)

    forged = audit_capabilities(repo_root=ROOT, now=NOW).to_dict()
    forged["capabilities"][0]["readiness_only"] = 1
    with pytest.raises(ContractError, match="type_mismatch"):
        receipt_from_dict(forged)


def test_cli_audit_verify_and_exclusive_receipt(tmp_path, capsys):
    receipt_path = tmp_path / "audit.json"
    assert readiness_main(["audit", "--output", str(receipt_path)]) == 0
    audit_output = json.loads(capsys.readouterr().out)
    assert audit_output["accepted"] is True
    initial_bytes = receipt_path.read_bytes()

    assert readiness_main(["verify", "--receipt", str(receipt_path)]) == 0
    verify_output = json.loads(capsys.readouterr().out)
    assert verify_output == audit_output

    with pytest.raises(SystemExit, match="2"):
        readiness_main(["audit", "--output", str(receipt_path)])
    assert receipt_path.read_bytes() == initial_bytes


def test_seal_one_exact_browser_case_without_resolution():
    issued = NOW.isoformat().replace("+00:00", "Z")
    expires = (NOW + timedelta(minutes=10)).isoformat().replace("+00:00", "Z")
    plan = seal_readiness_plan(
        case_id="x-browser",
        profile_ref="profile:x-primary-01",
        issued_at=issued,
        expires_at=expires,
        max_browser_actions=4,
        max_request_equivalents=2,
        max_wall_seconds=60,
        repo_root=ROOT,
    )
    assert plan.effect_class == "p4_readiness"
    assert plan.max_attempts == plan.external_concurrency == 1
    grant = ReadinessGrant.for_plan(plan)
    assert plan.accounting_confidence == "opaque_request_equivalent"
    verify_readiness_plan(plan, repo_root=ROOT)
    verify_readiness_grant(
        plan, grant, now=NOW + timedelta(minutes=1), repo_root=ROOT
    )


@pytest.mark.parametrize(
    "profile_ref",
    [
        "",
        "default",
        "profile:default",
        "profile:secret-token",
        "profile:http-route",
        "profile:../escape",
        "/home/user/profile",
        "profile:x,profile:y",
    ],
)
def test_profile_reference_must_be_exact_opaque_and_non_secret(profile_ref):
    with pytest.raises(ContractError):
        seal_readiness_plan(
            case_id="x-browser",
            profile_ref=profile_ref,
            issued_at="2026-09-15T18:00:00Z",
            expires_at="2026-09-15T18:10:00Z",
            max_browser_actions=4,
            max_request_equivalents=2,
            max_wall_seconds=60,
            repo_root=ROOT,
        )


@pytest.mark.parametrize(
    "case_id",
    ["youtube-command", "reddit-keyless-http", "reddit-scrapecreators-http"],
)
def test_content_fetch_only_adapters_cannot_be_sealed_as_p4(case_id):
    with pytest.raises(ContractError, match="no_readiness_only_seam"):
        seal_readiness_plan(
            case_id=case_id,
            profile_ref="profile:bounded-test",
            issued_at="2026-09-15T18:00:00Z",
            expires_at="2026-09-15T18:10:00Z",
            max_browser_actions=4,
            max_request_equivalents=2,
            max_wall_seconds=60,
            repo_root=ROOT,
        )


def test_expiry_and_budget_bounds_fail_closed():
    base = {
        "case_id": "x-browser",
        "profile_ref": "profile:x-primary-01",
        "issued_at": "2026-09-15T18:00:00Z",
        "expires_at": "2026-09-15T18:10:00Z",
        "max_browser_actions": 4,
        "max_request_equivalents": 2,
        "max_wall_seconds": 60,
        "repo_root": ROOT,
    }
    with pytest.raises(ContractError, match="expiry_out_of_bounds"):
        seal_readiness_plan(**{**base, "expires_at": "2026-09-15T18:30:00Z"})
    with pytest.raises(ContractError, match="browser_action_budget"):
        seal_readiness_plan(**{**base, "max_browser_actions": 9})
    with pytest.raises(ContractError, match="request_equivalent_budget"):
        seal_readiness_plan(**{**base, "max_request_equivalents": 0})
    with pytest.raises(ContractError, match="wall_budget"):
        seal_readiness_plan(**{**base, "max_wall_seconds": 121})


def test_grant_mismatch_and_expiry_fail_closed():
    plan = seal_readiness_plan(
        case_id="facebook-browser",
        profile_ref="profile:facebook-primary-01",
        issued_at="2026-09-15T18:00:00Z",
        expires_at="2026-09-15T18:10:00Z",
        max_browser_actions=4,
        max_request_equivalents=2,
        max_wall_seconds=60,
        repo_root=ROOT,
    )
    grant = ReadinessGrant.for_plan(plan)
    with pytest.raises(ContractError, match="grant_mismatch"):
        verify_readiness_grant(
            plan,
            replace(grant, profile_ref="profile:other"),
            now=NOW,
            repo_root=ROOT,
        )
    with pytest.raises(ContractError, match="grant_expired"):
        verify_readiness_grant(
            plan, grant, now=NOW + timedelta(minutes=10), repo_root=ROOT
        )


def test_tampered_plan_and_matching_grant_are_rejected():
    plan = seal_readiness_plan(
        case_id="reddit-browser",
        profile_ref="profile:reddit-primary-01",
        issued_at="2026-09-15T18:00:00Z",
        expires_at="2026-09-15T18:10:00Z",
        max_browser_actions=4,
        max_request_equivalents=2,
        max_wall_seconds=60,
        repo_root=ROOT,
    )
    forged = replace(plan, provider="forged-provider")
    with pytest.raises(ContractError, match="plan_mismatch"):
        verify_readiness_plan(forged, repo_root=ROOT)
    with pytest.raises(ContractError, match="plan_mismatch"):
        verify_readiness_grant(
            forged, ReadinessGrant.for_plan(forged), now=NOW, repo_root=ROOT
        )


def test_next_gate_is_exact_and_no_p4_verdict_exists():
    receipt = audit_capabilities(repo_root=ROOT, now=NOW)
    assert receipt.next_gate == NEXT_GATE
    assert "ready" not in receipt.state.casefold()
    assert "execute" not in {
        name
        for name in dir(
            __import__(
                "dev.last30days.provider_acceptance.readiness", fromlist=["*"]
            )
        )
        if name.startswith("execute")
    }
