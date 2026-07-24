"""Agent-facing service product contract stays aligned across canonical docs."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_skill_routes_service_tools_before_engine_mechanics():
    text = (ROOT / "skills" / "last30days" / "SKILL.md").read_text()
    service = text.index("# SERVICE-FIRST PATH")
    engine = text.index("# SKILL CONTRACT")

    assert service < engine
    for tool in ("service_info", "query", "refresh", "job_status", "topic"):
        assert f"`{tool}`" in text[service:engine]
    assert "do not run `scripts/last30days.py`" in text[service:engine]
    assert "browser/scraper commands" in text[service:engine]


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
    assert "install-service.sh" in configuration


def test_mcpb_packages_runtime_and_verifies_canonical_contract():
    workflow = (ROOT / ".github" / "workflows" / "release.yml").read_text()
    mcp_readme = (ROOT / "mcp" / "README.md").read_text()
    generator = (
        ROOT / "mcp" / "scripts" / "generate-contracts.py"
    ).read_text()

    assert "sync-service-runtime.sh" in workflow
    assert 'grep -F "runtime/last30days/"' in workflow
    assert 'grep -F "/service.py"' in workflow
    assert "go -C mcp generate ./internal/contracts" in workflow
    assert "may start the one shared daemon" in mcp_readme
    assert "service-contracts-v1.json" in generator
