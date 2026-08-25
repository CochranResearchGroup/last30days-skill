"""Independent service runtime artifact boundary and reproducibility."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "service" / "scripts" / "build-runtime.sh"
MANIFEST = ROOT / "service" / "runtime-manifest.json"
VERSION = ROOT / "service" / "VERSION"
MCP_SYNC = ROOT / "mcp" / "scripts" / "sync-service-runtime.sh"


def _build(output_dir: Path, *, repo_root: Path = ROOT) -> Path:
    result = subprocess.run(
        [
            "bash",
            str(BUILDER),
            "--repo-root",
            str(repo_root),
            "--output-dir",
            str(output_dir),
        ],
        check=True,
        capture_output=True,
        text=True,
        env={**os.environ, "SOURCE_DATE_EPOCH": "0"},
    )
    return Path(result.stdout.strip().split("  ", 1)[1])


def test_runtime_manifest_is_explicit_current_and_skill_free():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    entries = manifest["files"]
    paths = [entry["path"] for entry in entries]
    sources = [entry["source"] for entry in entries]

    assert manifest["format"] == "last30days-service-runtime-v1"
    assert manifest["hash_algorithm"] == "sha256"
    assert manifest["service_version"] == VERSION.read_text().strip() == "0.3.68"
    assert paths == sorted(paths)
    assert len(paths) == len(set(paths))
    assert len(sources) == len(set(sources))
    assert paths[:4] == [
        "VERSION",
        "schemas/service-contracts-v1.json",
        "schemas/tick-config-v1.json",
        "scripts/lib/__init__.py",
    ]
    assert "scripts/service.py" in paths
    assert "scripts/store.py" in paths
    assert any(path.startswith("scripts/lib/vendor/bird-search/") for path in paths)
    assert all("SKILL.md" not in path for path in paths)
    assert all("install-service.sh" not in path for path in paths)
    assert all("setup-" not in path for path in paths)
    for entry in entries:
        raw = (ROOT / entry["source"]).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == entry["sha256"]


def test_runtime_artifact_is_reproducible_verified_and_executable(tmp_path):
    first = _build(tmp_path / "first")
    second = _build(tmp_path / "second")
    assert first.read_bytes() == second.read_bytes()

    version = VERSION.read_text().strip()
    release_root = f"last30days-service-{version}"
    with tarfile.open(first, "r:gz") as archive:
        members = archive.getmembers()
        names = [member.name for member in members]
        assert names == sorted(names)
        assert all(member.uid == member.gid == 0 for member in members)
        assert all(member.mtime == 0 for member in members)
        assert f"{release_root}/SKILL.md" not in names
        assert f"{release_root}/scripts/install-service.sh" not in names
        archive.extractall(tmp_path / "extracted", filter="data")

    runtime_root = tmp_path / "extracted" / release_root
    artifact_manifest = json.loads(
        (runtime_root / "runtime-manifest.json").read_text(encoding="utf-8")
    )
    for entry in artifact_manifest["files"]:
        raw = (runtime_root / entry["path"]).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == entry["sha256"]
    result = subprocess.run(
        [sys.executable, str(runtime_root / "scripts" / "service.py"), "--help"],
        cwd=runtime_root,
        check=True,
        capture_output=True,
        text=True,
    )
    assert "Run or query the local last30days intelligence service" in result.stdout


def test_builder_fails_closed_when_manifest_or_payload_drifts(tmp_path):
    copied = tmp_path / "repo"
    for relative in (
        Path("service"),
        Path("skills/last30days/scripts/lib"),
        Path("skills/last30days/schemas"),
    ):
        shutil.copytree(ROOT / relative, copied / relative)
    scripts = copied / "skills" / "last30days" / "scripts"
    scripts.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / "skills/last30days/scripts/service.py", scripts / "service.py")
    shutil.copy2(ROOT / "skills/last30days/scripts/store.py", scripts / "store.py")
    with (scripts / "service.py").open("a", encoding="utf-8") as handle:
        handle.write("\n# drift\n")

    result = subprocess.run(
        [
            "bash",
            str(BUILDER),
            "--repo-root",
            str(copied),
            "--output-dir",
            str(tmp_path / "output"),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert "runtime-manifest.json is stale" in result.stderr
    assert not (tmp_path / "output").exists()


def test_mcp_runtime_stages_only_independent_artifact_and_controls(tmp_path):
    runtime = tmp_path / "runtime"
    result = subprocess.run(
        [
            "bash",
            str(MCP_SYNC),
            "--repo-root",
            str(ROOT),
            "--runtime-dir",
            str(runtime),
        ],
        check=True,
        capture_output=True,
        text=True,
        env={**os.environ, "SOURCE_DATE_EPOCH": "0"},
    )

    service = runtime / "service"
    artifact = next((service / "artifacts").glob("last30days-service-*.tar.gz"))
    files = {
        path.relative_to(runtime).as_posix()
        for path in runtime.rglob("*")
        if path.is_file()
    }
    assert files == {
        f"service/artifacts/{artifact.name}",
        "service/VERSION",
        "service/scripts/install.sh",
        "service/systemd/last30days.service.in",
    }
    assert "independent service payload" in result.stdout
    assert not any(path.name == "SKILL.md" for path in runtime.rglob("*"))
    with tarfile.open(artifact, "r:gz") as archive:
        names = archive.getnames()
    assert any(name.endswith("/scripts/service.py") for name in names)
    assert not any(name.endswith("/SKILL.md") for name in names)
