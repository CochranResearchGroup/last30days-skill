"""Least-privilege contract for the ordinary service-backed Agent Skill."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills" / "last30days"
SKILL = SKILL_DIR / "SKILL.md"
REFERENCES = SKILL_DIR / "references"


def test_ordinary_skill_is_concise_and_service_info_is_first():
    body = SKILL.read_text(encoding="utf-8")

    assert len(body.splitlines()) <= 300
    assert body.index("`service_info`") < body.index("`query`")
    assert "Call `service_info` first" in body
    assert "least-privilege MCP client" in body


def test_ordinary_skill_names_the_exact_product_surface():
    body = SKILL.read_text(encoding="utf-8")
    tools = {
        "service_info",
        "query",
        "refresh",
        "job_status",
        "topic",
        "temporal_query",
        "profile_history",
        "coverage",
        "collection",
        "maintenance_status",
    }

    for tool in tools:
        assert f"`{tool}`" in body


def test_ordinary_skill_contains_no_compatibility_mechanics():
    body = SKILL.read_text(encoding="utf-8")
    forbidden = {
        "AUTH_TOKEN",
        "CT0",
        "FROM_BROWSER",
        "agent-browser",
        "yt-dlp",
        "last30days.py",
        "service.py",
        "python3 ",
        "--x-handle",
        "allowed-tools: Bash",
    }

    for text in forbidden:
        assert text not in body


def test_progressive_references_are_explicitly_gated():
    body = SKILL.read_text(encoding="utf-8")
    expected = {
        "monitoring.md": "Monitoring is read-only",
        "administration.md": "explicit request",
        "maintenance.md": "Model output is a proposal only",
        "direct-engine-compatibility.md": "explicitly approves",
    }

    for name, marker in expected.items():
        assert f"references/{name}" in body
        assert marker in (REFERENCES / name).read_text(encoding="utf-8")

    fallback = (REFERENCES / "direct-engine-compatibility.md").read_text(
        encoding="utf-8"
    )
    assert "scripts/last30days.py" in fallback
    assert "return to `../SKILL.md`" in fallback
