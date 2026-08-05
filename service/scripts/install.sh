#!/usr/bin/env bash
set -euo pipefail

LAST30DAYS_INSTALL_SCRIPT_DIR="$(
  CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd
)"
LAST30DAYS_INSTALL_REPO_ROOT="$(
  CDPATH= cd -- "${LAST30DAYS_INSTALL_SCRIPT_DIR}/../.." && pwd
)"
LAST30DAYS_INSTALL_PYTHON="${LAST30DAYS_PYTHON:-python3}"

exec "${LAST30DAYS_INSTALL_PYTHON}" - "${LAST30DAYS_INSTALL_REPO_ROOT}" "$@" <<'PY'
from __future__ import annotations

import argparse
import hashlib
import http.client
import json
import os
import re
import shlex
import shutil
import socket
import subprocess
import sys
import tarfile
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath


FORMAT = "last30days-service-runtime-v1"
UNIT_NAME = "last30days.service"
DATABASE_SCHEMA_VERSION = 14
SEMVER = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:[-+][0-9A-Za-z.-]+)?$")


def fail(message: str) -> "NoReturn":
    raise SystemExit(f"last30days service install error: {message}")


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def canonical_json(payload: object) -> bytes:
    return (
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def atomic_write(path: Path, raw: bytes, mode: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    with tempfile.NamedTemporaryFile(
        mode="wb", dir=path.parent, prefix=f".{path.name}.", delete=False
    ) as handle:
        handle.write(raw)
        temporary = Path(handle.name)
    os.chmod(temporary, mode)
    os.replace(temporary, path)


def checked_relative(value: str, field: str) -> PurePosixPath:
    path = PurePosixPath(value)
    if path.is_absolute() or not path.parts or ".." in path.parts:
        fail(f"{field} contains an unsafe path")
    return path


def load_archive(
    artifact: Path,
) -> tuple[str, bytes, dict[str, object], dict[str, tuple[bytes, int]]]:
    if not artifact.is_file():
        fail(f"service artifact not found: {artifact}")
    try:
        with tarfile.open(artifact, "r:gz") as archive:
            members = archive.getmembers()
            if not members:
                fail("service artifact is empty")
            if any(
                not member.isfile()
                or member.issym()
                or member.islnk()
                or member.isdev()
                for member in members
            ):
                fail("service artifact may contain only regular files")
            member_names = [member.name for member in members]
            if len(member_names) != len(set(member_names)):
                fail("service artifact contains duplicate member names")
            names = [PurePosixPath(member.name) for member in members]
            roots = {name.parts[0] for name in names if name.parts}
            if len(roots) != 1:
                fail("service artifact must contain one release root")
            release_root = roots.pop()
            manifest_name = f"{release_root}/runtime-manifest.json"
            try:
                manifest_member = archive.getmember(manifest_name)
                manifest_raw = archive.extractfile(manifest_member).read()
                manifest = json.loads(manifest_raw)
            except (KeyError, AttributeError, json.JSONDecodeError) as exc:
                fail(f"service artifact manifest is invalid: {exc}")
            if manifest_raw != canonical_json(manifest):
                fail("service artifact manifest is not canonical")
            if manifest.get("format") != FORMAT:
                fail("service artifact format is unsupported")
            if manifest.get("hash_algorithm") != "sha256":
                fail("service artifact hash algorithm is unsupported")
            version = manifest.get("service_version")
            if not isinstance(version, str) or not SEMVER.fullmatch(version):
                fail("service artifact version is invalid")
            if release_root != f"last30days-service-{version}":
                fail("service artifact root does not match its version")
            entries = manifest.get("files")
            if not isinstance(entries, list) or not entries:
                fail("service artifact file manifest is empty")
            payloads: dict[str, tuple[bytes, int]] = {}
            for entry in entries:
                if not isinstance(entry, dict) or set(entry) != {
                    "path",
                    "sha256",
                    "source",
                }:
                    fail("service artifact file entry is invalid")
                target = checked_relative(str(entry["path"]), "manifest path")
                archive_name = f"{release_root}/{target.as_posix()}"
                try:
                    member = archive.getmember(archive_name)
                    raw = archive.extractfile(member).read()
                except (KeyError, AttributeError) as exc:
                    fail(f"service artifact payload is missing: {target}: {exc}")
                if sha256(raw) != entry["sha256"]:
                    fail(f"service artifact payload digest mismatch: {target}")
                if target.as_posix() in payloads:
                    fail(f"service artifact payload is duplicated: {target}")
                payloads[target.as_posix()] = (raw, member.mode & 0o777)
            expected_names = {
                manifest_name,
                *(
                    f"{release_root}/{path}"
                    for path in payloads
                ),
            }
            if set(member.name for member in members) != expected_names:
                fail("service artifact contains files outside its manifest")
    except (EOFError, OSError, tarfile.TarError) as exc:
        fail(f"unable to read service artifact: {exc}")
    version_raw = payloads.get("VERSION", (b"", 0))[0]
    if version_raw.decode("utf-8", errors="replace").strip() != version:
        fail("service artifact VERSION does not match its manifest")
    return version, manifest_raw, manifest, payloads


def installed_release_is_valid(
    release: Path, manifest_raw: bytes, manifest: dict[str, object]
) -> bool:
    try:
        if (release / "runtime-manifest.json").read_bytes() != manifest_raw:
            return False
        expected = {"runtime-manifest.json"}
        for entry in manifest["files"]:
            relative = checked_relative(str(entry["path"]), "installed path")
            target = release / relative.as_posix()
            if not target.is_file() or target.is_symlink():
                return False
            if sha256(target.read_bytes()) != entry["sha256"]:
                return False
            expected.add(relative.as_posix())
        actual = {
            path.relative_to(release).as_posix()
            for path in release.rglob("*")
            if path.is_file()
        }
        return actual == expected
    except OSError:
        return False


def make_tree_read_only(root: Path) -> None:
    for path in sorted(root.rglob("*"), reverse=True):
        if path.is_file():
            os.chmod(path, 0o555 if path.stat().st_mode & 0o111 else 0o444)
        elif path.is_dir():
            os.chmod(path, 0o555)
    os.chmod(root, 0o555)


def make_tree_removable(root: Path) -> None:
    if not root.exists():
        return
    os.chmod(root, 0o700)
    for path in root.rglob("*"):
        if path.is_dir():
            os.chmod(path, 0o700)
        elif path.is_file():
            os.chmod(path, 0o600)


def stage_release(
    releases: Path,
    version: str,
    manifest_raw: bytes,
    manifest: dict[str, object],
    payloads: dict[str, tuple[bytes, int]],
) -> Path:
    releases.mkdir(parents=True, exist_ok=True, mode=0o700)
    release = releases / version
    if release.exists():
        if not release.is_dir() or release.is_symlink():
            fail(f"release target is unsafe: {release}")
        if not installed_release_is_valid(release, manifest_raw, manifest):
            fail(f"immutable release collision for version {version}")
        return release
    staging = Path(
        tempfile.mkdtemp(prefix=f".stage-{version}.", dir=releases)
    )
    try:
        atomic_write(staging / "runtime-manifest.json", manifest_raw, 0o444)
        for relative, (raw, archived_mode) in payloads.items():
            mode = 0o555 if archived_mode & 0o111 else 0o444
            atomic_write(staging / relative, raw, mode)
        if not installed_release_is_valid(staging, manifest_raw, manifest):
            fail("staged release failed verification")
        make_tree_read_only(staging)
        os.replace(staging, release)
    finally:
        if staging.exists():
            make_tree_removable(staging)
            shutil.rmtree(staging)
    return release


def atomic_symlink(link: Path, relative_target: str | None) -> None:
    if link.exists() and not link.is_symlink():
        fail(f"managed release selector is not a symlink: {link}")
    temporary = link.parent / f".{link.name}.{os.getpid()}"
    temporary.unlink(missing_ok=True)
    if relative_target is None:
        link.unlink(missing_ok=True)
        return
    checked_relative(relative_target, f"{link.name} target")
    os.symlink(relative_target, temporary)
    os.replace(temporary, link)


def selected_release(link: Path, releases: Path) -> str | None:
    if not link.is_symlink():
        if link.exists():
            fail(f"managed release selector is not a symlink: {link}")
        return None
    target = os.readlink(link)
    relative = checked_relative(target, f"{link.name} target")
    if len(relative.parts) != 2 or relative.parts[0] != "releases":
        fail(f"{link.name} does not select a managed release")
    release = releases / relative.parts[1]
    if not release.is_dir() or release.is_symlink():
        fail(f"{link.name} selects a missing or unsafe release")
    return relative.parts[1]


def systemd_quote_value(value: str) -> str:
    if "\n" in value or "\r" in value or "\0" in value:
        fail("managed path contains unsupported characters")
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def systemd_quote(path: Path) -> str:
    return systemd_quote_value(str(path))


def systemd_escape_path(path: Path) -> str:
    value = str(path)
    if not path.is_absolute():
        fail("managed systemd path must be absolute")
    if "\n" in value or "\r" in value or "\0" in value:
        fail("managed path contains unsupported characters")
    safe = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789/._-"
    return "".join(
        chr(byte) if byte in safe else f"\\x{byte:02x}"
        for byte in value.encode("utf-8")
    )


def render_launcher(service_root: Path, python_bin: Path) -> None:
    launcher = service_root / "last30days-service"
    content = f"""#!/bin/sh
set -eu
current={shlex.quote(str(service_root / "current"))}
if [ ! -L "$current" ]; then
  echo "last30days service release is not selected" >&2
  exit 2
fi
version="$(sed -n '1p' "$current/VERSION")"
export LAST30DAYS_SERVICE_VERSION="$version"
export LAST30DAYS_RUNTIME_MANIFEST_PATH="$current/runtime-manifest.json"
exec {shlex.quote(str(python_bin))} "$current/scripts/service.py" "$@"
"""
    atomic_write(launcher, content.encode("utf-8"), 0o755)


def render_unit(
    repo_root: Path,
    unit_path: Path,
    launcher: Path,
    env_file: Path,
    socket_path: Path,
) -> None:
    template_path = repo_root / "service" / "systemd" / "last30days.service.in"
    try:
        template = template_path.read_text(encoding="utf-8")
    except OSError as exc:
        fail(f"unable to read managed unit template: {exc}")
    rendered = template.replace("@LAUNCHER@", systemd_quote(launcher)).replace(
        "@ENV_FILE@", systemd_escape_path(env_file)
    ).replace(
        "@SOCKET_ENV@",
        "Environment="
        + systemd_quote_value(f"LAST30DAYS_SERVICE_SOCKET={socket_path}"),
    )
    if any(
        placeholder in rendered
        for placeholder in ("@LAUNCHER@", "@ENV_FILE@", "@SOCKET_ENV@")
    ):
        fail("managed unit template contains unresolved placeholders")
    atomic_write(unit_path, rendered.encode("utf-8"), 0o600)


def ensure_environment_file(env_file: Path) -> None:
    if env_file.exists() or env_file.is_symlink():
        if not env_file.is_file() or env_file.is_symlink():
            fail(f"managed environment file is unsafe: {env_file}")
        return
    atomic_write(env_file, b"", 0o600)


class UnixHTTPConnection(http.client.HTTPConnection):
    def __init__(self, socket_path: Path, timeout: float):
        super().__init__("localhost", timeout=timeout)
        self.socket_path = socket_path

    def connect(self) -> None:
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.settimeout(self.timeout)
        self.sock.connect(str(self.socket_path))


def release_expectations(release: Path) -> tuple[str, str, str]:
    version = (release / "VERSION").read_text(encoding="utf-8").strip()
    manifest_sha = sha256((release / "runtime-manifest.json").read_bytes())
    contract_sha = sha256(
        (release / "schemas" / "service-contracts-v1.json").read_bytes()
    )
    return version, manifest_sha, contract_sha


def readiness(
    release: Path,
    socket_path: Path,
    timeout: float,
    receipt_path: Path | None,
) -> dict[str, object]:
    version, manifest_sha, contract_sha = release_expectations(release)
    deadline = time.monotonic() + timeout
    last_error = "service did not answer"
    while time.monotonic() < deadline:
        connection = UnixHTTPConnection(
            socket_path, timeout=max(0.1, min(1.0, deadline - time.monotonic()))
        )
        try:
            connection.request(
                "GET", "/v1/service-info", headers={"Accept": "application/json"}
            )
            response = connection.getresponse()
            raw = response.read(131_073)
            header_digest = response.getheader("X-Last30days-Contract-SHA256")
            payload = json.loads(raw.decode("utf-8"))
            if response.status != 200 or not isinstance(payload, dict):
                raise RuntimeError("service-info response is not healthy")
            checks = {
                "service_version": payload.get("service_version") == version,
                "database_schema_version": (
                    payload.get("database_schema_version")
                    == DATABASE_SCHEMA_VERSION
                ),
                "contract_sha256": header_digest == contract_sha,
                "status": payload.get("status") == "ready",
            }
            if not all(checks.values()):
                failed = ", ".join(key for key, passed in checks.items() if not passed)
                raise RuntimeError(f"service readiness mismatch: {failed}")
            receipt = {
                "contract_sha256": contract_sha,
                "database_schema_version": DATABASE_SCHEMA_VERSION,
                "release": f"releases/{version}",
                "runtime_manifest_sha256": manifest_sha,
                "schema_version": 1,
                "service_status": "ready",
                "service_version": version,
                "verified_at": datetime.now(timezone.utc)
                .isoformat()
                .replace("+00:00", "Z"),
            }
            if receipt_path is not None:
                atomic_write(receipt_path, canonical_json(receipt), 0o600)
            return receipt
        except (
            OSError,
            http.client.HTTPException,
            UnicodeDecodeError,
            json.JSONDecodeError,
            RuntimeError,
        ) as exc:
            last_error = str(exc)
            time.sleep(0.1)
        finally:
            connection.close()
    fail(f"readiness failed for {version}: {last_error}")


def manager_command(
    manager: Path, *arguments: str, check: bool = True
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        [str(manager), "--user", *arguments],
        text=True,
        capture_output=True,
        check=False,
    )
    if check and result.returncode:
        detail = result.stderr.strip() or result.stdout.strip() or "no detail"
        fail(f"user manager command failed ({' '.join(arguments)}): {detail}")
    return result


def remove_release(path: Path) -> None:
    if path.is_symlink() or not path.is_dir():
        fail(f"refusing to remove unsafe release path: {path}")
    make_tree_removable(path)
    shutil.rmtree(path)


def enforce_retention(releases: Path, current: str, previous: str | None, retain: int) -> None:
    keep = {current}
    if previous is not None:
        keep.add(previous)
    candidates = sorted(
        (
            path
            for path in releases.iterdir()
            if path.is_dir() and not path.is_symlink() and path.name not in keep
        ),
        key=lambda path: path.stat().st_mtime_ns,
        reverse=True,
    )
    extra_slots = max(0, retain - len(keep))
    for path in candidates[extra_slots:]:
        remove_release(path)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Install and operate the last30days user-scoped service"
    )
    parser.add_argument("default_repo_root", help=argparse.SUPPRESS)
    parser.add_argument(
        "command",
        choices=(
            "install",
            "upgrade",
            "rollback",
            "start",
            "stop",
            "status",
            "diagnose",
        ),
    )
    parser.add_argument("--artifact", type=Path)
    parser.add_argument("--retain", type=int, default=2)
    parser.add_argument("--timeout", type=float, default=15.0)
    parser.add_argument("--systemctl", type=Path)
    parser.add_argument("--socket", type=Path)
    args = parser.parse_args()

    if sys.version_info < (3, 12):
        fail("Python 3.12+ is required")
    if args.retain < 2:
        fail("--retain must be at least 2")
    if not 0 < args.timeout <= 300:
        fail("--timeout must be between 0 and 300 seconds")

    repo_root = Path(args.default_repo_root).resolve()
    home = Path.home()
    data_home = Path(
        os.environ.get("XDG_DATA_HOME", home / ".local" / "share")
    )
    config_home = Path(os.environ.get("XDG_CONFIG_HOME", home / ".config"))
    runtime_home = os.environ.get("XDG_RUNTIME_DIR")
    if not runtime_home:
        fail("XDG_RUNTIME_DIR is required for the owner-private service socket")
    service_root = data_home / "last30days" / "service"
    releases = service_root / "releases"
    current_link = service_root / "current"
    previous_link = service_root / "previous"
    receipt_path = service_root / "readiness.json"
    socket_path = (
        args.socket
        or (
            Path(os.environ["LAST30DAYS_SERVICE_SOCKET"])
            if os.environ.get("LAST30DAYS_SERVICE_SOCKET")
            else None
        )
        or Path(runtime_home) / "last30days" / "service.sock"
    )
    if not socket_path.is_absolute():
        fail("service socket path must be absolute")
    unit_path = config_home / "systemd" / "user" / UNIT_NAME
    env_file = config_home / "last30days" / ".env"
    python_bin = Path(os.environ.get("LAST30DAYS_PYTHON", sys.executable)).resolve()
    manager_value = (
        args.systemctl
        or (
            Path(os.environ["LAST30DAYS_SYSTEMCTL"])
            if os.environ.get("LAST30DAYS_SYSTEMCTL")
            else None
        )
        or (Path(found) if (found := shutil.which("systemctl")) else None)
    )
    if manager_value is None or not manager_value.is_file():
        fail("systemctl is required for the Linux user service")
    manager = manager_value.resolve()

    if args.command == "stop":
        manager_command(manager, "stop", UNIT_NAME)
        return
    if args.command == "status":
        result = manager_command(
            manager, "--no-pager", "--full", "status", UNIT_NAME, check=False
        )
        sys.stdout.write(result.stdout)
        sys.stderr.write(result.stderr)
        raise SystemExit(result.returncode)

    current_name = selected_release(current_link, releases)
    previous_name = selected_release(previous_link, releases)
    if args.command == "diagnose":
        if current_name is None:
            fail("no current service release is selected")
        print(
            json.dumps(
                readiness(
                    releases / current_name,
                    socket_path,
                    args.timeout,
                    None,
                ),
                indent=2,
                sort_keys=True,
            )
        )
        return
    if args.command == "start":
        if current_name is None:
            fail("no current service release is selected")
        manager_command(manager, "start", UNIT_NAME)
        receipt = readiness(
            releases / current_name, socket_path, args.timeout, receipt_path
        )
        print(json.dumps(receipt, indent=2, sort_keys=True))
        return
    if args.command == "rollback":
        if current_name is None or previous_name is None:
            fail("rollback requires current and previous releases")
        if current_name == previous_name:
            fail("rollback target is the current release")
        atomic_symlink(current_link, f"releases/{previous_name}")
        atomic_symlink(previous_link, f"releases/{current_name}")
        try:
            manager_command(manager, "restart", UNIT_NAME)
            receipt = readiness(
                releases / previous_name, socket_path, args.timeout, receipt_path
            )
        except SystemExit as failure:
            atomic_symlink(current_link, f"releases/{current_name}")
            atomic_symlink(previous_link, f"releases/{previous_name}")
            try:
                manager_command(manager, "restart", UNIT_NAME)
                readiness(
                    releases / current_name,
                    socket_path,
                    args.timeout,
                    receipt_path,
                )
            except SystemExit:
                fail("rollback failed and original release readiness was not restored")
            fail(f"rollback failed; original release restored: {failure}")
        enforce_retention(releases, previous_name, current_name, args.retain)
        print(json.dumps(receipt, indent=2, sort_keys=True))
        return

    if args.artifact is None:
        fail(f"{args.command} requires --artifact")
    if args.command == "upgrade" and current_name is None:
        fail("upgrade requires an installed current release")
    version, manifest_raw, manifest, payloads = load_archive(args.artifact.resolve())
    service_root.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(service_root, 0o700)
    releases.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(releases, 0o700)
    ensure_environment_file(env_file)
    render_launcher(service_root, python_bin)
    render_unit(
        repo_root,
        unit_path,
        service_root / "last30days-service",
        env_file,
        socket_path,
    )
    release = stage_release(
        releases, version, manifest_raw, manifest, payloads
    )
    old_current = current_name
    old_previous = previous_name
    if old_current is not None and old_current != version:
        atomic_symlink(previous_link, f"releases/{old_current}")
    atomic_symlink(current_link, f"releases/{version}")
    manager_command(manager, "daemon-reload")
    manager_command(manager, "enable", UNIT_NAME)
    try:
        manager_command(manager, "restart", UNIT_NAME)
        receipt = readiness(release, socket_path, args.timeout, receipt_path)
    except SystemExit as failure:
        if old_current is None:
            manager_command(manager, "stop", UNIT_NAME, check=False)
            atomic_symlink(current_link, None)
            receipt_path.unlink(missing_ok=True)
            remove_release(release)
            fail(f"initial install failed readiness: {failure}")
        atomic_symlink(current_link, f"releases/{old_current}")
        atomic_symlink(
            previous_link,
            f"releases/{old_previous}" if old_previous is not None else None,
        )
        try:
            manager_command(manager, "restart", UNIT_NAME)
            readiness(
                releases / old_current,
                socket_path,
                args.timeout,
                receipt_path,
            )
        except SystemExit:
            fail("upgrade failed and previous release readiness was not restored")
        enforce_retention(
            releases, old_current, old_previous, args.retain
        )
        fail(f"upgrade failed; previous release restored and ready: {failure}")
    selected_previous = selected_release(previous_link, releases)
    enforce_retention(releases, version, selected_previous, args.retain)
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
PY
