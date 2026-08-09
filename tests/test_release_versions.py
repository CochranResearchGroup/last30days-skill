"""Independent service, MCP, and optional Skill release identities."""

from __future__ import annotations

import json
from pathlib import Path

from lib.skill_meta import read_skill_version


ROOT = Path(__file__).resolve().parents[1]


def _json(relative: str) -> dict[str, object]:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def test_v4_release_versions_are_independent_and_explicit():
    assert read_skill_version(ROOT / "skills/last30days/SKILL.md") == "4.0.0"
    assert _json(".claude-plugin/plugin.json")["version"] == "4.0.0"
    assert _json(".claude-plugin/marketplace.json")["plugins"][0]["version"] == "4.0.0"
    assert _json("gemini-extension.json")["version"] == "4.0.0"

    assert _json("mcp/manifest.json")["version"] == "4.0.1"

    service_version = (ROOT / "service/VERSION").read_text(encoding="utf-8").strip()
    runtime_manifest = _json("service/runtime-manifest.json")
    assert service_version == "0.3.38"
    assert runtime_manifest["service_version"] == service_version


def test_mcp_builds_stamp_the_manifest_version_not_the_git_tag():
    installer = (ROOT / "mcp/scripts/install-codex.sh").read_text(encoding="utf-8")
    workflow = (ROOT / ".github/workflows/release.yml").read_text(encoding="utf-8")

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
