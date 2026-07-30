#!/usr/bin/env bash
set -euo pipefail

LAST30DAYS_BUILD_SCRIPT_DIR="$(
  CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd
)"
LAST30DAYS_BUILD_REPO_ROOT="$(
  CDPATH= cd -- "${LAST30DAYS_BUILD_SCRIPT_DIR}/../.." && pwd
)"
LAST30DAYS_BUILD_PYTHON="${LAST30DAYS_PYTHON:-python3}"

exec "${LAST30DAYS_BUILD_PYTHON}" - "${LAST30DAYS_BUILD_REPO_ROOT}" "$@" <<'PY'
from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import os
import re
import sys
import tarfile
import tempfile
from pathlib import Path, PurePosixPath


FORMAT = "last30days-service-runtime-v1"
SEMVER = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:[-+][0-9A-Za-z.-]+)?$")


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def source_inventory(repo_root: Path) -> list[tuple[Path, PurePosixPath]]:
    fixed = [
        (repo_root / "service" / "VERSION", PurePosixPath("VERSION")),
        (
            repo_root / "skills" / "last30days" / "scripts" / "service.py",
            PurePosixPath("scripts/service.py"),
        ),
        (
            repo_root / "skills" / "last30days" / "scripts" / "store.py",
            PurePosixPath("scripts/store.py"),
        ),
    ]
    trees = [
        (
            repo_root / "skills" / "last30days" / "scripts" / "lib",
            PurePosixPath("scripts/lib"),
        ),
        (
            repo_root / "skills" / "last30days" / "schemas",
            PurePosixPath("schemas"),
        ),
    ]
    inventory = list(fixed)
    for source_root, target_root in trees:
        if not source_root.is_dir():
            raise SystemExit(f"runtime source directory is missing: {source_root}")
        for source in sorted(source_root.rglob("*")):
            if source.is_symlink():
                raise SystemExit(f"runtime source must not be a symlink: {source}")
            if not source.is_file():
                continue
            relative = source.relative_to(source_root)
            if "__pycache__" in relative.parts or source.suffix == ".pyc":
                continue
            inventory.append((source, target_root / PurePosixPath(relative.as_posix())))
    inventory.sort(key=lambda item: item[1].as_posix())
    return inventory


def checked_version(repo_root: Path) -> str:
    version_path = repo_root / "service" / "VERSION"
    try:
        version = version_path.read_text(encoding="utf-8").strip()
    except OSError as exc:
        raise SystemExit(f"unable to read service version: {version_path}") from exc
    if not SEMVER.fullmatch(version):
        raise SystemExit("service/VERSION must contain one semantic version")
    return version


def manifest_payload(repo_root: Path) -> dict[str, object]:
    files = []
    for source, target in source_inventory(repo_root):
        if not source.is_file():
            raise SystemExit(f"runtime source file is missing: {source}")
        raw = source.read_bytes()
        files.append(
            {
                "path": target.as_posix(),
                "sha256": digest(raw),
                "source": source.relative_to(repo_root).as_posix(),
            }
        )
    return {
        "files": files,
        "format": FORMAT,
        "hash_algorithm": "sha256",
        "service_version": checked_version(repo_root),
    }


def canonical_json(payload: dict[str, object]) -> bytes:
    return (
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def refresh_manifest(repo_root: Path) -> Path:
    manifest_path = repo_root / "service" / "runtime-manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    raw = canonical_json(manifest_payload(repo_root))
    with tempfile.NamedTemporaryFile(
        mode="wb",
        dir=manifest_path.parent,
        prefix=".runtime-manifest.",
        delete=False,
    ) as handle:
        handle.write(raw)
        temporary = Path(handle.name)
    os.chmod(temporary, 0o644)
    os.replace(temporary, manifest_path)
    return manifest_path


def load_verified_manifest(repo_root: Path) -> tuple[dict[str, object], bytes]:
    manifest_path = repo_root / "service" / "runtime-manifest.json"
    try:
        raw = manifest_path.read_bytes()
        payload = json.loads(raw)
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"unable to load runtime manifest: {manifest_path}") from exc
    if raw != canonical_json(payload):
        raise SystemExit(
            "service/runtime-manifest.json is not canonical; "
            "run service/scripts/build-runtime.sh --refresh-manifest"
        )
    expected = manifest_payload(repo_root)
    if payload != expected:
        raise SystemExit(
            "service/runtime-manifest.json is stale; "
            "run service/scripts/build-runtime.sh --refresh-manifest"
        )
    return payload, raw


def add_bytes(
    archive: tarfile.TarFile,
    name: str,
    raw: bytes,
    *,
    mode: int,
    mtime: int,
) -> None:
    info = tarfile.TarInfo(name=name)
    info.size = len(raw)
    info.mode = mode
    info.mtime = mtime
    info.uid = 0
    info.gid = 0
    info.uname = ""
    info.gname = ""
    archive.addfile(info, io.BytesIO(raw))


def build(repo_root: Path, output_dir: Path, source_date_epoch: int) -> Path:
    manifest, manifest_raw = load_verified_manifest(repo_root)
    version = str(manifest["service_version"])
    release_root = f"last30days-service-{version}"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{release_root}.tar.gz"
    with tempfile.NamedTemporaryFile(
        mode="wb", dir=output_dir, prefix=f".{release_root}.", delete=False
    ) as raw_handle:
        temporary = Path(raw_handle.name)
        with gzip.GzipFile(
            filename="",
            mode="wb",
            fileobj=raw_handle,
            mtime=source_date_epoch,
        ) as compressed:
            with tarfile.open(
                fileobj=compressed,
                mode="w",
                format=tarfile.GNU_FORMAT,
            ) as archive:
                payloads = [
                    (
                        PurePosixPath("runtime-manifest.json"),
                        manifest_raw,
                        0o644,
                    )
                ]
                for entry in manifest["files"]:
                    source = repo_root / str(entry["source"])
                    target = PurePosixPath(str(entry["path"]))
                    if target.is_absolute() or ".." in target.parts:
                        raise SystemExit(f"unsafe runtime target path: {target}")
                    mode = 0o755 if source.stat().st_mode & 0o111 else 0o644
                    payloads.append((target, source.read_bytes(), mode))
                for target, raw, mode in sorted(
                    payloads, key=lambda item: item[0].as_posix()
                ):
                    add_bytes(
                        archive,
                        f"{release_root}/{target.as_posix()}",
                        raw,
                        mode=mode,
                        mtime=source_date_epoch,
                    )
    os.chmod(temporary, 0o644)
    os.replace(temporary, output_path)
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build the independently versioned last30days service runtime"
    )
    parser.add_argument("default_repo_root", help=argparse.SUPPRESS)
    parser.add_argument("--repo-root", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--refresh-manifest", action="store_true")
    args = parser.parse_args()

    repo_root = (args.repo_root or Path(args.default_repo_root)).resolve()
    if args.refresh_manifest:
        path = refresh_manifest(repo_root)
        print(path)
        return
    raw_epoch = os.environ.get("SOURCE_DATE_EPOCH", "0")
    try:
        source_date_epoch = int(raw_epoch)
    except ValueError as exc:
        raise SystemExit("SOURCE_DATE_EPOCH must be an integer") from exc
    if source_date_epoch < 0:
        raise SystemExit("SOURCE_DATE_EPOCH must be non-negative")
    output_dir = (
        args.output_dir.resolve()
        if args.output_dir
        else repo_root / "dist" / "service"
    )
    output_path = build(repo_root, output_dir, source_date_epoch)
    print(f"{digest(output_path.read_bytes())}  {output_path}")


if __name__ == "__main__":
    main()
PY
