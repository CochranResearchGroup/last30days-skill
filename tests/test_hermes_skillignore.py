from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "skills" / "last30days"


def _skillignore_entries() -> set[str]:
    text = (SKILL_ROOT / ".skillignore").read_text(encoding="utf-8")
    return {
        line.strip()
        for line in text.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }


def test_skill_dir_excludes_non_runtime_scan_surface() -> None:
    entries = _skillignore_entries()

    assert entries == set()
    assert not (SKILL_ROOT / "assets").exists()
    assert not (SKILL_ROOT / "agents").exists()
    assert not (SKILL_ROOT / "scripts" / "build-skill.sh").exists()
    assert not (SKILL_ROOT / "scripts" / "compare.sh").exists()
    assert not (SKILL_ROOT / "scripts" / "evaluate_search_quality.py").exists()
    assert not (SKILL_ROOT / "scripts" / "test_device_auth.py").exists()
    assert not (SKILL_ROOT / "scripts" / "test-v1-vs-v2.sh").exists()
    assert not (SKILL_ROOT / "scripts" / "verify_v3.py").exists()


def test_hermes_skillignore_keeps_runtime_contract_scannable() -> None:
    entries = _skillignore_entries()

    assert "SKILL.md" not in entries
    assert "scripts/last30days.py" not in entries
    assert "scripts/lib/" not in entries
