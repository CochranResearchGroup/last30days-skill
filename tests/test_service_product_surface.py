"""Agent-facing service product contract stays aligned across canonical docs."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_skill_routes_service_tools_before_engine_mechanics():
    skill_root = ROOT / "skills" / "last30days"
    text = (skill_root / "SKILL.md").read_text()
    compatibility = (
        skill_root / "references" / "direct-engine-compatibility.md"
    ).read_text()

    for tool in ("service_info", "query", "refresh", "job_status", "topic"):
        assert f"`{tool}`" in text
    assert "scripts/last30days.py" not in text
    assert "browser/scraper commands" not in text
    assert "explicitly approves this compatibility path" in compatibility
    assert "perform live external acquisition" in compatibility
    assert "scripts/last30days.py" in compatibility


def test_operator_docs_name_the_same_thin_service_surface():
    configuration = (ROOT / "CONFIGURATION.md").read_text()
    concepts = (ROOT / "CONCEPTS.md").read_text()
    onboarding = (ROOT / "docs" / "ONBOARDING.md").read_text()

    for tool in ("service_info", "query", "refresh", "job_status", "topic"):
        assert f"`{tool}`" in configuration
        assert f"`{tool}`" in onboarding
    assert "never launch a request-scoped research subprocess" in " ".join(
        concepts.split()
    )
    assert "service/scripts/build-runtime.sh" in configuration
    assert "service/scripts/install.sh" in configuration
    assert "Agent Skill is optional" in (ROOT / "README.md").read_text()


def test_mcpb_packages_runtime_and_verifies_canonical_contract():
    workflow = (ROOT / ".github" / "workflows" / "release.yml").read_text()
    mcp_readme = (ROOT / "mcp" / "README.md").read_text()
    generator = (
        ROOT / "mcp" / "scripts" / "generate-contracts.py"
    ).read_text()

    assert "sync-service-runtime.sh" in workflow
    assert 'grep -E "runtime/service/scri[p]ts/install[.]sh"' in workflow
    assert 'grep -F "runtime/service/artifacts/last30days-service-"' in workflow
    assert 'tar -tzf "${artifact}"' in workflow
    assert 'grep -E "/scri[p]ts/service[.]py"' in workflow
    assert 'if tar -tzf "${artifact}" | grep -F "/SKILL.md"' in workflow
    assert "go -C mcp generate ./internal/contracts" in workflow
    assert "managed user-service installer" in mcp_readme
    assert "does not detach" in mcp_readme
    assert "service-contracts-v1.json" in generator
