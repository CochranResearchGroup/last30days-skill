"""Tests for the claude.ai .skill artifact boundary."""

import os
import subprocess
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "dist" / "last30days.skill"


def test_build_skill_excludes_skillignore_entries() -> None:
    subprocess.run(
        ["bash", "dev/last30days/scripts/build-skill.sh"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        env={**os.environ, "LAST30DAYS_BUILD_ALLOW_DIRTY": "1"},
    )

    with zipfile.ZipFile(ARTIFACT) as archive:
        names = set(archive.namelist())

    assert "last30days/SKILL.md" in names
    assert "last30days/scripts/last30days.py" in names
    assert "last30days/scripts/store.py" in names
    assert "last30days/scripts/watchlist.py" in names
    assert any(name.startswith("last30days/scripts/lib/") for name in names)

    excluded_prefixes = {
        "last30days/assets/",
        "last30days/agents/",
    }
    excluded_files = {
        "last30days/scripts/build-skill.sh",
        "last30days/scripts/compare.sh",
        "last30days/scripts/evaluate_search_quality.py",
        "last30days/scripts/test_device_auth.py",
        "last30days/scripts/test-v1-vs-v2.sh",
        "last30days/scripts/verify_v3.py",
    }

    assert not any(
        name.startswith(prefix)
        for name in names
        for prefix in excluded_prefixes
    )
    assert names.isdisjoint(excluded_files)
