"""Independent service, MCP, and optional Skill release identities."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

from lib.skill_meta import read_skill_version


ROOT = Path(__file__).resolve().parents[1]


def _json(relative: str) -> dict[str, object]:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def _contract_generator():
    path = ROOT / "mcp/scripts/generate-contracts.py"
    spec = importlib.util.spec_from_file_location("mcp_contract_generator", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_v4_release_versions_are_independent_and_explicit():
    assert read_skill_version(ROOT / "skills/last30days/SKILL.md") == "4.0.0"
    assert _json(".claude-plugin/plugin.json")["version"] == "4.0.0"
    assert _json(".claude-plugin/marketplace.json")["plugins"][0]["version"] == "4.0.0"
    assert _json("gemini-extension.json")["version"] == "4.0.0"

    assert _json("mcp/manifest.json")["version"] == "4.0.3"

    service_version = (ROOT / "service/VERSION").read_text(encoding="utf-8").strip()
    runtime_manifest = _json("service/runtime-manifest.json")
    assert service_version == "0.3.73"
    assert runtime_manifest["service_version"] == service_version


def test_mcp_release_identity_is_locked_to_canonical_contract():
    manifest = _json("mcp/manifest.json")
    release_lock = _json("mcp/compatibility-releases.json")
    catalog_path = ROOT / "skills/last30days/schemas/service-contracts-v1.json"
    catalog_raw = catalog_path.read_bytes()
    catalog = json.loads(catalog_raw)

    current = [
        release
        for release in release_lock["releases"]
        if release["adapter_version"] == manifest["version"]
    ]
    assert len(current) == 1
    assert current[0] == {
        "adapter_version": "4.0.3",
        "contract_schema_version": catalog["schema_version"],
        "contract_sha256": hashlib.sha256(catalog_raw).hexdigest(),
        "service_api": catalog["compatibility"]["service_api"],
        "database_schema": catalog["compatibility"]["database_schema"],
    }


def test_contract_generator_rejects_unreleased_or_ambiguous_identity():
    generator = _contract_generator()
    catalog_raw = (
        ROOT / "skills/last30days/schemas/service-contracts-v1.json"
    ).read_bytes()
    catalog = json.loads(catalog_raw)
    manifest = _json("mcp/manifest.json")
    release_lock = _json("mcp/compatibility-releases.json")

    assert generator.validate_release_lock(
        catalog_raw=catalog_raw,
        catalog=catalog,
        manifest=manifest,
        release_lock=release_lock,
    )["adapter_version"] == "4.0.3"

    missing = copy.deepcopy(release_lock)
    missing["releases"] = missing["releases"][:-1]
    with pytest.raises(ValueError, match="exactly one compatibility release"):
        generator.validate_release_lock(
            catalog_raw=catalog_raw,
            catalog=catalog,
            manifest=manifest,
            release_lock=missing,
        )

    duplicate = copy.deepcopy(release_lock)
    duplicate["releases"].append(copy.deepcopy(duplicate["releases"][-1]))
    with pytest.raises(ValueError, match="exactly one compatibility release"):
        generator.validate_release_lock(
            catalog_raw=catalog_raw,
            catalog=catalog,
            manifest=manifest,
            release_lock=duplicate,
        )

    mismatched = copy.deepcopy(release_lock)
    mismatched["releases"][-1]["contract_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="does not match the canonical catalog"):
        generator.validate_release_lock(
            catalog_raw=catalog_raw,
            catalog=catalog,
            manifest=manifest,
            release_lock=mismatched,
        )


def test_mcp_builds_stamp_the_manifest_version_not_the_git_tag():
    installer = (ROOT / "mcp/scripts/install-codex.sh").read_text(encoding="utf-8")
    workflow = (ROOT / ".github/workflows/release.yml").read_text(encoding="utf-8")

    assert 'python3 "${MCP_ROOT}/scripts/generate-contracts.py"' in installer
    for text in (installer, workflow):
        assert "mcp/manifest.json" in text or '"${MCP_ROOT}/manifest.json"' in text
        assert "-X main.Version=${MCP_VERSION}" in text
    assert "main.Version=${{ github.ref_name }}" not in workflow


def test_agent_client_manifests_request_no_source_credentials():
    skill = (ROOT / "skills/last30days/SKILL.md").read_text(encoding="utf-8")
    gemini = _json("gemini-extension.json")
    source_secrets = {
        "AUTH_TOKEN",
        "CT0",
        "SCRAPECREATORS_API_KEY",
        "OPENAI_API_KEY",
        "XAI_API_KEY",
    }

    assert all(secret not in skill for secret in source_secrets)
    env_names = {setting["envVar"] for setting in gemini["settings"]}
    assert source_secrets.isdisjoint(env_names)
