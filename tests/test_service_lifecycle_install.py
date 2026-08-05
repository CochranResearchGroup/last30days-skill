"""Transactional independent service installation with a fake user manager."""

from __future__ import annotations

import json
import os
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
CURRENT_VERSION = (ROOT / "service" / "VERSION").read_text(encoding="utf-8").strip()
BUILDER = ROOT / "service" / "scripts" / "build-runtime.sh"
INSTALLER = ROOT / "service" / "scripts" / "install.sh"


def _write_fake_manager(path: Path) -> None:
    path.write_text(
        """#!/usr/bin/env python3
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

args = [arg for arg in sys.argv[1:] if arg != "--user"]
log = Path(os.environ["FAKE_MANAGER_LOG"])
with log.open("a", encoding="utf-8") as handle:
    handle.write(" ".join(args) + "\\n")
pid_path = Path(os.environ["FAKE_MANAGER_PID"])
service_root = Path(os.environ["XDG_DATA_HOME"]) / "last30days" / "service"

def stop():
    if not pid_path.exists():
        return
    pid = int(pid_path.read_text())
    try:
        os.kill(pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    for _ in range(100):
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            break
        time.sleep(0.02)
    pid_path.unlink(missing_ok=True)

command = next((arg for arg in args if arg in {"restart", "start", "stop", "status"}), None)
if command == "stop":
    stop()
elif command in {"restart", "start"}:
    stop()
    version = (service_root / "current" / "VERSION").read_text().strip()
    if version == os.environ.get("FAKE_MANAGER_FAIL_VERSION"):
        raise SystemExit(1)
    process = subprocess.Popen(
        [str(service_root / "last30days-service"), "serve"],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        env=os.environ.copy(),
        start_new_session=True,
    )
    pid_path.write_text(str(process.pid))
elif command == "status":
    if not pid_path.exists():
        raise SystemExit(3)
    pid = int(pid_path.read_text())
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        raise SystemExit(3)
    print("active (running)")
""",
        encoding="utf-8",
    )
    path.chmod(0o755)


def _environment(tmp_path: Path) -> dict[str, str]:
    fake_manager = tmp_path / "fake-systemctl"
    _write_fake_manager(fake_manager)
    runtime = tmp_path / "runtime"
    runtime.mkdir()
    return {
        **os.environ,
        "HOME": str(tmp_path / "home"),
        "XDG_CONFIG_HOME": str(tmp_path / "config"),
        "XDG_DATA_HOME": str(tmp_path / "data"),
        "XDG_RUNTIME_DIR": str(runtime),
        "LAST30DAYS_PYTHON": sys.executable,
        "LAST30DAYS_SYSTEMCTL": str(fake_manager),
        "FAKE_MANAGER_LOG": str(tmp_path / "manager.log"),
        "FAKE_MANAGER_PID": str(tmp_path / "manager.pid"),
    }


def _copy_runtime_sources(target: Path) -> None:
    shutil.copytree(ROOT / "service", target / "service")
    for relative in (
        Path("skills/last30days/scripts/lib"),
        Path("skills/last30days/schemas"),
    ):
        shutil.copytree(ROOT / relative, target / relative)
    scripts = target / "skills" / "last30days" / "scripts"
    scripts.mkdir(parents=True, exist_ok=True)
    for name in ("service.py", "store.py"):
        shutil.copy2(ROOT / "skills/last30days/scripts" / name, scripts / name)


def _artifact(
    tmp_path: Path, version: str, *, source_root: Path = ROOT
) -> Path:
    if version != CURRENT_VERSION:
        source_root = tmp_path / f"source-{version}"
        _copy_runtime_sources(source_root)
        (source_root / "service" / "VERSION").write_text(
            version + "\n", encoding="utf-8"
        )
        subprocess.run(
            [
                "bash",
                str(BUILDER),
                "--repo-root",
                str(source_root),
                "--refresh-manifest",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
    output = tmp_path / f"build-{version}"
    result = subprocess.run(
        [
            "bash",
            str(BUILDER),
            "--repo-root",
            str(source_root),
            "--output-dir",
            str(output),
        ],
        check=True,
        capture_output=True,
        text=True,
        env={**os.environ, "SOURCE_DATE_EPOCH": "0"},
    )
    return Path(result.stdout.strip().split("  ", 1)[1])


def _run(
    env: dict[str, str],
    command: str,
    *,
    artifact: Path | None = None,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    arguments = ["bash", str(INSTALLER), command, "--timeout", "8"]
    if artifact is not None:
        arguments.extend(["--artifact", str(artifact)])
    return subprocess.run(
        arguments,
        env=env,
        check=check,
        capture_output=True,
        text=True,
        timeout=20,
    )


def _stop(env: dict[str, str]) -> None:
    subprocess.run(
        [env["LAST30DAYS_SYSTEMCTL"], "--user", "stop", "last30days.service"],
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )


def test_clean_install_uses_independent_current_release_and_receipt(tmp_path):
    env = _environment(tmp_path)
    artifact = _artifact(tmp_path, CURRENT_VERSION)
    try:
        result = _run(env, "install", artifact=artifact)
        receipt = json.loads(result.stdout)
        service_root = Path(env["XDG_DATA_HOME"]) / "last30days" / "service"
        env_file = Path(env["XDG_CONFIG_HOME"]) / "last30days/.env"
        unit = (
            Path(env["XDG_CONFIG_HOME"])
            / "systemd/user/last30days.service"
        ).read_text()

        assert (service_root / "current").readlink() == Path(
            f"releases/{CURRENT_VERSION}"
        )
        assert not (service_root / "previous").exists()
        assert receipt["service_version"] == CURRENT_VERSION
        assert receipt["database_schema_version"] == 15
        assert receipt["service_status"] == "ready"
        assert receipt == json.loads(
            (service_root / "readiness.json").read_text(encoding="utf-8")
        )
        assert str(service_root / "last30days-service") in unit
        assert ".agents/skills" not in unit
        assert "skills/last30days" not in unit
        assert str(env_file) in unit
        assert (
            f"LAST30DAYS_SERVICE_SOCKET={env['XDG_RUNTIME_DIR']}"
            "/last30days/service.sock"
        ) in unit
        assert env_file.read_bytes() == b""
        assert env_file.stat().st_mode & 0o777 == 0o600
        assert "UMask=0077" in unit
        assert "NoNewPrivileges=true" in unit
        assert (
            service_root / f"releases/{CURRENT_VERSION}/scripts/service.py"
        ).is_file()
        assert not (
            service_root / f"releases/{CURRENT_VERSION}/SKILL.md"
        ).exists()
        assert (
            sqlite3.connect(
                Path(env["XDG_DATA_HOME"]) / "last30days/research.db"
            )
            .execute("SELECT MAX(version) FROM schema_version")
            .fetchone()[0]
            == 15
        )
        diagnosed = json.loads(_run(env, "diagnose").stdout)
        assert diagnosed["service_version"] == CURRENT_VERSION
        _run(env, "stop")
        assert not Path(env["FAKE_MANAGER_PID"]).exists()
        restarted = json.loads(_run(env, "start").stdout)
        assert restarted["service_version"] == CURRENT_VERSION
        status = _run(env, "status")
        assert "active (running)" in status.stdout
    finally:
        _stop(env)


def test_upgrade_manual_rollback_and_failed_upgrade_restore_state(tmp_path):
    env = _environment(tmp_path)
    first = _artifact(tmp_path, "0.2.7")
    second = _artifact(tmp_path, "0.2.8")
    failed = _artifact(tmp_path, "0.2.9")
    service_root = Path(env["XDG_DATA_HOME"]) / "last30days" / "service"
    db_path = Path(env["XDG_DATA_HOME"]) / "last30days/research.db"
    try:
        _run(env, "install", artifact=first)
        connection = sqlite3.connect(db_path)
        connection.execute(
            "INSERT INTO topics(name) VALUES ('installer-state-sentinel')"
        )
        connection.commit()
        before_dump = "\n".join(connection.iterdump())
        connection.close()

        upgraded = json.loads(_run(env, "upgrade", artifact=second).stdout)
        assert upgraded["service_version"] == "0.2.8"
        assert (service_root / "current").readlink() == Path("releases/0.2.8")
        assert (service_root / "previous").readlink() == Path("releases/0.2.7")

        rolled_back = json.loads(_run(env, "rollback").stdout)
        assert rolled_back["service_version"] == "0.2.7"
        assert (service_root / "current").readlink() == Path("releases/0.2.7")
        assert (service_root / "previous").readlink() == Path("releases/0.2.8")

        failed_env = {**env, "FAKE_MANAGER_FAIL_VERSION": "0.2.9"}
        failure = _run(
            failed_env, "upgrade", artifact=failed, check=False
        )
        assert failure.returncode != 0
        assert "previous release restored and ready" in failure.stderr
        assert (service_root / "current").readlink() == Path("releases/0.2.7")
        assert (service_root / "previous").readlink() == Path("releases/0.2.8")
        assert sorted(path.name for path in (service_root / "releases").iterdir()) == [
            "0.2.7",
            "0.2.8",
        ]
        connection = sqlite3.connect(db_path)
        assert connection.execute(
            "SELECT COUNT(*) FROM topics WHERE name = 'installer-state-sentinel'"
        ).fetchone()[0] == 1
        assert connection.execute(
            "SELECT MAX(version) FROM schema_version"
        ).fetchone()[0] == 15
        assert connection.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
        after_dump = "\n".join(connection.iterdump())
        connection.close()
        assert after_dump == before_dump
    finally:
        _stop(env)


def test_failed_initial_install_leaves_no_selected_or_staged_release(tmp_path):
    env = _environment(tmp_path)
    artifact = _artifact(tmp_path, "0.2.9")
    failed_env = {**env, "FAKE_MANAGER_FAIL_VERSION": "0.2.9"}
    service_root = Path(env["XDG_DATA_HOME"]) / "last30days" / "service"

    failure = _run(failed_env, "install", artifact=artifact, check=False)

    assert failure.returncode != 0
    assert "initial install failed readiness" in failure.stderr
    assert not (service_root / "current").exists()
    assert not (service_root / "previous").exists()
    assert not (service_root / "readiness.json").exists()
    assert list((service_root / "releases").iterdir()) == []
    assert not Path(env["FAKE_MANAGER_PID"]).exists()


def test_installer_rejects_unverified_or_underspecified_operations(tmp_path):
    env = _environment(tmp_path)
    artifact = _artifact(tmp_path, "0.2.7")
    tampered = tmp_path / "tampered.tar.gz"
    tampered.write_bytes(artifact.read_bytes()[:-100])

    no_artifact = _run(env, "install", check=False)
    rollback = _run(env, "rollback", check=False)
    invalid_artifact = _run(env, "install", artifact=tampered, check=False)
    bad_retention = subprocess.run(
        [
            "bash",
            str(INSTALLER),
            "install",
            "--artifact",
            str(artifact),
            "--retain",
            "1",
        ],
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )

    assert no_artifact.returncode != 0
    assert "requires --artifact" in no_artifact.stderr
    assert rollback.returncode != 0
    assert "rollback requires current and previous releases" in rollback.stderr
    assert invalid_artifact.returncode != 0
    assert "unable to read service artifact" in invalid_artifact.stderr
    assert bad_retention.returncode != 0
    assert "--retain must be at least 2" in bad_retention.stderr
