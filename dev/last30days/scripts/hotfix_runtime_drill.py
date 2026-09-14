"""WI-007 disposable installer drill. No operational deployment interface."""

from __future__ import annotations

import ctypes
import hashlib
import io
import json
import os
import platform
import re
import shutil
import signal
import socket
import socketserver
import sqlite3
import struct
import subprocess
import sys
import tarfile
import tempfile
import threading
import time
import uuid
from pathlib import Path

import hotfix_control as control
from hotfix_git_drill import run_git_drill

HELPER = Path(__file__).with_name("hotfix_fixture_runtime.py")
SCENARIOS = (
    "upgrade",
    "failed_upgrade",
    "rollback",
    "rollback_forward",
    "recovery_failure",
)
RUNTIME_PATHS = (
    "service",
    "skills/last30days/scripts/lib",
    "skills/last30days/scripts/service.py",
    "skills/last30days/scripts/store.py",
    "skills/last30days/schemas",
)


class DrillError(ValueError):
    """Evidence or ownership could not be established; stop without retry."""

    receipt: dict | None = None


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _git(root: Path, *args: str) -> bytes:
    result = subprocess.run(
        [
            "/usr/bin/git",
            "-c",
            "core.fsmonitor=false",
            "-c",
            "core.hooksPath=/dev/null",
            "-C",
            str(root),
            *args,
        ],
        env={
            "PATH": "/usr/bin:/bin",
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_TERMINAL_PROMPT": "0",
            "GIT_OPTIONAL_LOCKS": "0",
        },
        capture_output=True,
        check=False,
        timeout=15,
    )
    if result.returncode:
        raise DrillError("source_git_failed")
    return result.stdout


def _plain(path: Path) -> None:
    if not path.is_absolute() or any(p.is_symlink() for p in (path, *path.parents)):
        raise DrillError("unsafe_path")


def preflight(
    source: Path,
    source_commit: str,
    previous_commit: str,
    *,
    environment: dict[str, str] | None = None,
) -> dict:
    """Read-only exact source and policy validation. Never fetch or build."""
    source = Path(source)
    _plain(source)
    metadata = source / ".git"
    if not metadata.is_dir() or metadata.is_symlink():
        raise DrillError("standalone_source_clone_required")
    if any(
        (metadata / name).exists()
        for name in (
            "commondir",
            "objects/info/alternates",
            "objects/info/http-alternates",
        )
    ):
        raise DrillError("foreign_git_metadata")
    if any(path.is_symlink() for path in metadata.rglob("*")):
        raise DrillError("foreign_git_metadata")
    config = (metadata / "config").read_text()
    if re.search(r"(?im)^\s*\[(?:include|includeIf)\b|^\s*worktree\s*=", config):
        raise DrillError("foreign_git_configuration")
    if not all(
        re.fullmatch(r"[0-9a-f]{40}", c) for c in (source_commit, previous_commit)
    ):
        raise DrillError("invalid_commit")
    if _git(source, "rev-parse", "HEAD").decode().strip() != source_commit:
        raise DrillError("source_commit_mismatch")
    if _git(source, "status", "--porcelain", "--untracked-files=all"):
        raise DrillError("dirty_source")
    if (
        _git(source, "rev-parse", "refs/remotes/origin/main").decode().strip()
        != source_commit
    ):
        raise DrillError("stale_source")
    _git(source, "merge-base", "--is-ancestor", previous_commit, source_commit)
    ambient = dict(os.environ if environment is None else environment)
    if any(
        re.search(r"TOKEN|PASSWORD|SECRET|API_KEY|CREDENTIAL|COOKIE", key)
        or key.startswith(("LAST30DAYS_", "BROWSER_", "AWS_", "AZURE_", "GOOGLE_"))
        or key in {"PYTHONPATH", "PYTHONHOME", "LD_PRELOAD", "LD_LIBRARY_PATH"}
        for key in ambient
    ):
        raise DrillError("ambient_credentials_or_config")
    manifests = {}
    for role, commit in (("candidate", source_commit), ("previous", previous_commit)):
        raw = _git(source, "show", f"{commit}:service/runtime-manifest.json")
        manifest = json.loads(raw)
        version = _git(source, "show", f"{commit}:service/VERSION").decode().strip()
        if manifest.get("service_version") != version:
            raise DrillError("manifest_version_mismatch")
        for entry in manifest["files"]:
            relative = Path(entry["source"])
            if relative.is_absolute() or ".." in relative.parts:
                raise DrillError("unsafe_manifest_path")
            if role == "candidate":
                _plain(source / relative)
            if (
                _sha(_git(source, "show", f"{commit}:{relative.as_posix()}"))
                != entry["sha256"]
            ):
                raise DrillError("manifest_drift")
        contract_digest = _sha(
            _git(
                source,
                "show",
                f"{commit}:skills/last30days/schemas/service-contracts-v1.json",
            )
        )
        manifests[role] = {
            "commit": commit,
            "version": version,
            "manifest_sha256": _sha(raw),
            "contract_sha256": contract_digest,
            "fixture_schema": 18 if role == "candidate" else 17,
        }
    if manifests["candidate"]["version"] == manifests["previous"]["version"]:
        raise DrillError("distinct_committed_versions_required")
    return {
        "schema_version": 1,
        "mode": "drill",
        "work_item": "WI-007",
        "source_root": str(source),
        "sources": manifests,
        "operational_authority": False,
    }


def _ticks(pid: int) -> int:
    return int(Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()[19])


def _pidfd(pid: int) -> int:
    if platform.system() != "Linux" or platform.machine() not in {"x86_64", "aarch64"}:
        raise DrillError("pidfd_platform_required")
    libc = ctypes.CDLL(None, use_errno=True)
    result = libc.syscall(434, pid, 0)
    if result < 0:
        raise OSError(ctypes.get_errno(), "pidfd_open")
    return int(result)


def _terminate(pidfd: int):
    libc = ctypes.CDLL(None, use_errno=True)
    if libc.syscall(424, pidfd, signal.SIGTERM, 0, 0) < 0:
        raise OSError(ctypes.get_errno(), "pidfd_send_signal")


class _Fixture:
    def __init__(self, parent: Path):
        parent = Path(parent)
        _plain(parent)
        if (
            not parent.is_dir()
            or parent == Path(tempfile.gettempdir())
            or not parent.is_relative_to(Path(tempfile.gettempdir()))
        ):
            raise DrillError("unsafe_fixture_parent")
        if any((part / ".git").exists() for part in (parent, *parent.parents)):
            raise DrillError("unsafe_fixture_parent")
        if len(os.fsencode(parent)) + 60 > 103:
            raise DrillError("fixture_socket_path_too_long")
        os.close(_pidfd(os.getpid()))
        self.root = Path(tempfile.mkdtemp(prefix="wi007-", dir=parent))
        self.identity = (self.root.stat().st_dev, self.root.stat().st_ino)
        self.token = uuid.uuid4().hex
        (self.root / "owner.json").write_text(json.dumps({"token": self.token}))
        self.children = []
        self.processes = []
        self.commands = []
        self.active = None
        self.scenario = None
        self.fault = "none"
        self.previous_version = ""
        self.manager = self.root / "manager"
        self.manager.write_bytes(f"#!{sys.executable}\n".encode() + HELPER.read_bytes())
        self.manager.chmod(0o700)
        self.manager_sha = _sha(self.manager.read_bytes())
        self.endpoint = self.root / "manager.sock"
        owner = self

        class Handler(socketserver.StreamRequestHandler):
            def handle(self):
                self.connection.settimeout(10)
                try:
                    args = json.loads(self.rfile.readline(4096))
                    message = owner.manage(args)
                    result = {"returncode": 0, "message": message}
                except Exception as error:  # noqa: BLE001 - return every manager failure to the bounded installer
                    result = {"returncode": 1, "message": str(error)}
                self.wfile.write(json.dumps(result).encode() + b"\n")

        self.server = socketserver.UnixStreamServer(str(self.endpoint), Handler)
        os.chmod(self.endpoint, 0o600)
        self.thread = threading.Thread(
            target=self.server.serve_forever, kwargs={"poll_interval": 0.05}
        )
        self.thread.start()

    def owned(self):
        _plain(self.root)
        if (self.root.stat().st_dev, self.root.stat().st_ino) != self.identity:
            raise DrillError("fixture_owner_changed")
        if (self.root / "owner.json").is_symlink() or json.loads(
            (self.root / "owner.json").read_text()
        ) != {"token": self.token}:
            raise DrillError("fixture_owner_changed")
        if (
            self.manager.is_symlink()
            or _sha(self.manager.read_bytes()) != self.manager_sha
        ):
            raise DrillError("foreign_manager")
        for path in self.root.rglob("*"):
            if path.is_symlink() and (
                path.name not in {"current", "previous"}
                or path.parent.name != "service"
                or not path.resolve().is_relative_to(path.parent / "releases")
            ):
                raise DrillError("foreign_fixture_path")

    def environment(self):
        self.owned()
        root = self.scenario
        return {
            "PATH": "/usr/bin:/bin",
            "LANG": "C",
            "LC_ALL": "C",
            "XDG_CONFIG_HOME": str(root / "config"),
            "XDG_DATA_HOME": str(root / "data"),
            "XDG_RUNTIME_DIR": str(root / "run"),
            "LAST30DAYS_PYTHON": sys.executable,
            "PYTHONDONTWRITEBYTECODE": "1",
            "WI007_MANAGER_SOCKET": str(self.endpoint),
        }

    def stop(self):
        if self.active is None:
            return
        process, pidfd, ticks = self.active
        if process.poll() is None:
            if _ticks(process.pid) != ticks:
                raise DrillError("process_identity_changed")
            _terminate(pidfd)
            process.wait(timeout=3)
        os.close(pidfd)
        self.active = None

    def manage(self, args):
        self.owned()
        if not isinstance(args, list) or any(not isinstance(arg, str) for arg in args):
            raise DrillError("invalid_manager_command")
        args = [arg for arg in args if arg not in {"--user", "--no-pager", "--full"}]
        if not args or args[0] not in {
            "start",
            "restart",
            "stop",
            "status",
            "enable",
            "daemon-reload",
        }:
            raise DrillError("invalid_manager_command")
        command = args[0]
        if args != (
            ["daemon-reload"]
            if command == "daemon-reload"
            else [command, "last30days.service"]
        ):
            raise DrillError("invalid_manager_target")
        self.commands.append({"scenario": self.scenario.name, "command": command})
        if command == "stop":
            self.stop()
        elif command in {"start", "restart"}:
            self.stop()
            version = (
                (self.scenario / "data/last30days/service/current/VERSION")
                .read_text()
                .strip()
            )
            if self.fault == "recovery_failure" and command == "start":
                raise DrillError("injected_recovery_failure")
            unhealthy = self.fault != "none" and version != self.previous_version
            schema = 17 if version == self.previous_version else 18
            process = subprocess.Popen(
                [
                    sys.executable,
                    str(self.manager),
                    "serve",
                    str(self.scenario),
                    str(schema),
                    "unhealthy" if unhealthy else "ready",
                ],
                env=self.environment(),
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
            self.children.append(process)
            pidfd = _pidfd(process.pid)
            ticks = _ticks(process.pid)
            self.active = (process, pidfd, ticks)
            self.processes.append(
                {
                    "pid": process.pid,
                    "start_ticks": ticks,
                    "scenario": self.scenario.name,
                }
            )
        elif command == "status" and (
            self.active is None or self.active[0].poll() is not None
        ):
            raise DrillError("fixture_not_running")
        return "active (running)" if self.active else "stopped"

    def install(self, installer: Path, command: str, artifact: Path | None = None):
        self.owned()
        args = [
            "/bin/bash",
            str(installer),
            command,
            "--systemctl",
            str(self.manager),
            "--socket",
            str(self.scenario / "run/service.sock"),
            "--timeout",
            "1",
            "--skill-host-root",
            str(self.scenario / "host-copies"),
        ]
        if artifact is not None:
            args.extend(["--artifact", str(artifact)])
        started = time.monotonic()
        result = subprocess.run(
            args,
            env=self.environment(),
            capture_output=True,
            text=True,
            check=False,
            timeout=15,
        )
        return {
            "command": command,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "elapsed_seconds": round(time.monotonic() - started, 4),
        }

    def observe(self, installer):
        result = self.install(installer, "diagnose")
        if result["returncode"]:
            raise DrillError("fixture_readiness_failed")
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as peer:
            peer.settimeout(1)
            peer.connect(str(self.scenario / "run/service.sock"))
            pid, uid, _gid = struct.unpack(
                "3i", peer.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, 12)
            )
        if (
            self.active is None
            or pid != self.active[0].pid
            or uid != os.geteuid()
            or _ticks(pid) != self.active[2]
        ):
            raise DrillError("fixture_socket_owner_mismatch")
        database = self.scenario / "data/last30days/research.db"
        with sqlite3.connect(database.as_uri() + "?mode=ro", uri=True) as connection:
            integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
            foreign_keys = connection.execute("PRAGMA foreign_key_check").fetchall()
            sentinels = [
                row[0]
                for row in connection.execute(
                    "SELECT value FROM sentinel ORDER BY value"
                )
            ]
            dump = "\n".join(connection.iterdump())
        service = self.scenario / "data/last30days/service"
        return {
            "readiness": json.loads(result["stdout"]),
            "integrity": integrity,
            "socket_peer": {"pid": pid, "uid": uid, "start_ticks": self.active[2]},
            "foreign_keys": foreign_keys,
            "sentinels": sentinels,
            "database_digest": _sha(dump.encode()),
            "current": os.readlink(service / "current"),
            "previous": os.readlink(service / "previous")
            if (service / "previous").is_symlink()
            else None,
        }

    def cleanup(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=3)
        self.stop()
        self.owned()
        if self.thread.is_alive() or any(p.poll() is None for p in self.children):
            raise DrillError("cleanup_process_remaining")
        remaining = []
        for path in Path("/proc").iterdir():
            if path.name.isdigit() and int(path.name) != os.getpid():
                try:
                    if str(self.root).encode() in (path / "cmdline").read_bytes():
                        remaining.append(int(path.name))
                except (FileNotFoundError, ProcessLookupError, PermissionError):
                    continue
        if remaining:
            raise DrillError("cleanup_census_ambiguous")
        # Installer selectors are the only permitted links, contained within
        # their scenario. Never chmod through any link during recursive cleanup.
        for path in self.root.rglob("*"):
            if path.is_symlink() and (
                path.name not in {"current", "previous"}
                or not path.resolve().is_relative_to(path.parent / "releases")
            ):
                raise DrillError("cleanup_foreign_link")
        for path in self.root.rglob("*"):
            if not path.is_symlink():
                os.chmod(path, 0o700 if path.is_dir() else 0o600)
        self.owned()
        shutil.rmtree(self.root)
        return {
            "verified": not self.root.exists(),
            "remaining_processes": remaining,
            "processes": self.processes,
        }


def _snapshot(source: Path, commit: str, target: Path):
    raw = _git(source, "archive", "--format=tar", commit, *RUNTIME_PATHS)
    target.mkdir()
    with tarfile.open(fileobj=io.BytesIO(raw)) as archive:
        if any(
            not member.isfile() and not member.isdir()
            for member in archive.getmembers()
        ):
            raise DrillError("unsafe_source_archive")
        archive.extractall(target, filter="data")


def run_drill(
    source: Path,
    source_commit: str,
    previous_commit: str,
    *,
    parent: Path,
    scenarios=("upgrade",),
    environment=None,
) -> dict:
    """Run a bounded disposable drill; return retained evidence after teardown."""
    started = time.monotonic()
    checked = preflight(source, source_commit, previous_commit, environment=environment)
    if (
        not scenarios
        or len(set(scenarios)) != len(scenarios)
        or any(name not in SCENARIOS for name in scenarios)
    ):
        raise DrillError("unknown_scenario")
    fixture = _Fixture(parent)
    receipt = {
        **checked,
        "fixture_root": str(fixture.root),
        "scenarios": [],
        "artifacts": {},
        "proof_kind": "real_installer_synthetic_service_and_schema",
        "effects": {
            "provider": False,
            "browser": False,
            "schedule": False,
            "installed_user_service": False,
            "operational_staging": False,
        },
        "real_slot": {"state": "dormant", "resources": [], "live_authority": False},
    }
    failure = None
    try:
        fixture.previous_version = checked["sources"]["previous"]["version"]
        for role, commit in (
            ("previous", previous_commit),
            ("candidate", source_commit),
        ):
            snapshot = fixture.root / role
            _snapshot(source, commit, snapshot)
            artifacts = []
            for number in range(2 if role == "candidate" else 1):
                output = fixture.root / f"build-{role}-{number}"
                subprocess.run(
                    [
                        "/bin/bash",
                        str(snapshot / "service/scripts/build-runtime.sh"),
                        "--repo-root",
                        str(snapshot),
                        "--output-dir",
                        str(output),
                    ],
                    env={
                        "PATH": "/usr/bin:/bin",
                        "LAST30DAYS_PYTHON": sys.executable,
                        "SOURCE_DATE_EPOCH": "0",
                    },
                    check=True,
                    capture_output=True,
                    timeout=30,
                )
                artifact = next(output.glob("*.tar.gz"))
                artifacts.append(artifact)
            hashes = [_sha(path.read_bytes()) for path in artifacts]
            if len(set(hashes)) != 1:
                raise DrillError("nonreproducible_artifact")
            receipt["artifacts"][role] = {
                **checked["sources"][role],
                "sha256": hashes[0],
                "build_sha256": hashes,
                "build_count": len(artifacts),
                "path": str(artifacts[0]),
            }
        # Compose the current controller with immutable committed payloads.
        tool_root = Path(__file__).resolve().parents[3]
        tooling = (
            "service/scripts/install.sh",
            "service/systemd/last30days.service.in",
            "dev/last30days/scripts/hotfix_runtime_drill.py",
            "dev/last30days/scripts/hotfix_fixture_runtime.py",
            "dev/last30days/scripts/hotfix_control.py",
            "dev/last30days/scripts/hotfix_git_drill.py",
        )
        receipt["tooling"] = {
            "commit": _git(tool_root, "rev-parse", "HEAD").decode().strip(),
            "files": {name: _sha((tool_root / name).read_bytes()) for name in tooling},
        }
        installer = fixture.root / "controls/service/scripts/install.sh"
        for name in tooling[:2]:
            target = fixture.root / "controls" / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(tool_root / name, target)
        for name in scenarios:
            if time.monotonic() - started > 60:
                raise DrillError("drill_time_bound")
            fixture.stop()
            fixture.fault = "none"
            fixture.scenario = fixture.root / name
            for directory in ("host-copies", "config", "data", "run"):
                (fixture.scenario / directory).mkdir(parents=True, mode=0o700)
            scenario = {"name": name, "actions": [], "observations": []}
            receipt["scenarios"].append(scenario)
            action = fixture.install(
                installer, "install", Path(receipt["artifacts"]["previous"]["path"])
            )
            scenario["actions"].append(action)
            if action["returncode"]:
                raise DrillError("initial_fixture_install_failed")
            with sqlite3.connect(
                fixture.scenario / "data/last30days/research.db"
            ) as connection:
                connection.execute("INSERT INTO sentinel VALUES ('before-upgrade')")
            scenario["observations"].append(fixture.observe(installer))
            fixture.fault = (
                name if name in {"failed_upgrade", "recovery_failure"} else "none"
            )
            action = fixture.install(
                installer, "upgrade", Path(receipt["artifacts"]["candidate"]["path"])
            )
            scenario["actions"].append(action)
            if (action["returncode"] != 0) != (
                name in {"failed_upgrade", "recovery_failure"}
            ):
                raise DrillError("unexpected_upgrade_outcome")
            if name == "recovery_failure":
                if "readiness was not restored" not in action["stderr"]:
                    raise DrillError("unexpected_recovery_outcome")
                scenario["outcome"] = "blocked"
                continue
            if name in {"rollback", "rollback_forward"}:
                with sqlite3.connect(
                    fixture.scenario / "data/last30days/research.db"
                ) as connection:
                    connection.execute("INSERT INTO sentinel VALUES ('after-upgrade')")
            scenario["observations"].append(fixture.observe(installer))
            if name == "failed_upgrade" and (
                "previous release restored and ready" not in action["stderr"]
                or scenario["observations"][0]["database_digest"]
                != scenario["observations"][-1]["database_digest"]
            ):
                raise DrillError("failed_upgrade_restoration_mismatch")
            if name in {"rollback", "rollback_forward"}:
                for direction in (
                    ("backward", "forward")
                    if name == "rollback_forward"
                    else ("backward",)
                ):
                    action = fixture.install(installer, "rollback")
                    action["direction"] = direction
                    scenario["actions"].append(action)
                    if action["returncode"]:
                        raise DrillError("explicit_rollback_failed")
                    observation = fixture.observe(installer)
                    scenario["observations"].append(observation)
                    expected = scenario["observations"][
                        0 if direction == "backward" else 1
                    ]
                    if (
                        observation["database_digest"] != expected["database_digest"]
                        or observation["readiness"]["service_version"]
                        != expected["readiness"]["service_version"]
                    ):
                        raise DrillError("rollback_identity_mismatch")
            scenario["outcome"] = (
                "restored" if name in {"failed_upgrade", "rollback"} else "verified"
            )
        fixture.stop()
        if tuple(scenarios) == SCENARIOS:
            receipt["git"] = run_git_drill(fixture.root)
        receipt["status"] = "passed"
    except Exception as error:  # noqa: BLE001 - preserve failed drill evidence before exact teardown
        failure = error
        receipt["status"] = "failed"
        receipt["error"] = str(error)
    finally:
        receipt["manager_commands"] = fixture.commands
        try:
            receipt["cleanup"] = fixture.cleanup()
        except Exception as error:  # noqa: BLE001 - preserve uncertain cleanup and its retained root
            failure = error
            receipt["status"] = "failed"
            receipt["cleanup"] = {
                "verified": False,
                "error": str(error),
                "retained_root": str(fixture.root),
            }
    receipt["elapsed_seconds"] = round(time.monotonic() - started, 4)
    if receipt["elapsed_seconds"] > 60:
        failure = DrillError("drill_time_bound")
        receipt["status"] = "failed"
    if not failure and "git" in receipt:
        receipt["controls"] = _compose(receipt)
    receipt["receipt_digest"] = control.digest(receipt)
    if failure:
        error = DrillError(f"drill_failed:{failure}")
        error.receipt = receipt
        raise error from failure
    return receipt


def _replay_git(entries):
    controller = control.HotfixController()
    for entry in entries:
        state, evidence = entry["state"], entry["evidence"]
        if state == "qualified":
            controller.qualify()
        else:
            method, contract = {
                "reported": (controller.report, control.HotfixCaseV1),
                "active": (controller.activate, control.GitSnapshotV1),
                "fix_ready": (controller.candidate, control.HotfixCandidateV1),
                "integrated": (
                    (controller.reconcile, control.HotfixReconciliationReportV1)
                    if "lanes" in evidence
                    else (controller.integrate, control.HotfixIntegrationReceiptV1)
                ),
            }[state]
            method(contract.from_dict(evidence))
        if controller.history[-1] != entry:
            raise DrillError("git_history_mismatch")
    return controller


def _compose(receipt):
    """Replay synthetic control history, binding actual artifact observations.

    The simulated merge is never claimed as the runtime payload source commit.
    All records remain mode=drill and grant no operational authority.
    """
    git = receipt["git"]
    artifact = receipt["artifacts"]["candidate"]
    histories = {}
    for scenario in receipt["scenarios"]:
        controller = _replay_git(git["history"])
        commit = git["integration"]["merge_commit"]
        target = "fixture-production:" + scenario["name"]
        evidence = "receipt://scenarios/" + scenario["name"]
        identity = {"integrated_commit": commit, "artifact_digest": artifact["sha256"]}
        controller.stage(
            control.HotfixStagingReceiptV1(
                **identity,
                manifest_digest=artifact["manifest_sha256"],
                identity="fixture-staging",
                validation="receipt://scenarios/rollback",
                rollback_verified=True,
                effects_disabled=True,
            )
        )
        controller.authorize(
            control.HotfixDeploymentAuthorizationV1(
                **identity,
                target=target,
                operator="fixture-operator",
                rollback_commit=git["base_commit"],
                attempt_limit=1,
                window="single-disposable-scenario",
                stop_conditions="first failed postcondition",
            )
        )
        controller.deploy(
            control.HotfixDeploymentReceiptV1(
                **identity, target=target, attempt=1, evidence=evidence
            )
        )
        ready = scenario["outcome"] == "verified"
        controller.verify(
            control.HotfixVerificationReceiptV1(
                **identity,
                target=target,
                ready=ready,
                integrity_verified=True,
                regression_fixed=ready,
                effects_disabled=True,
                evidence=evidence,
            )
        )
        if not ready:
            restored = scenario["outcome"] == "restored"
            controller.rollback(
                control.HotfixRollbackReceiptV1(
                    integrated_commit=commit,
                    rollback_commit=git["base_commit"],
                    target=target,
                    attempt=1,
                    ready=restored,
                    integrity_verified=restored,
                    effects_disabled=True,
                    evidence=evidence,
                )
            )
        controller.close(
            control.HotfixCloseoutReceiptV1(
                case_digest=control.digest(git["history"][0]["evidence"]),
                outcome="fixed"
                if ready
                else "rolled_back"
                if scenario["outcome"] == "restored"
                else "blocked",
                cleanup_verified=receipt["cleanup"]["verified"],
                evidence=evidence,
                residual_risks="Synthetic service/schema and incident; no operational staging or deployment proof",
            )
        )
        histories[scenario["name"]] = list(controller.history)
    return histories


def report(receipt: dict) -> dict:
    """Validate a complete retained receipt without executing or fetching anything."""
    try:
        unsigned = {k: v for k, v in receipt.items() if k != "receipt_digest"}
        if receipt["receipt_digest"] != control.digest(unsigned):
            raise DrillError("receipt_digest_mismatch")
        if (
            receipt["mode"] != "drill"
            or receipt["work_item"] != "WI-007"
            or receipt["operational_authority"] is not False
            or receipt["status"] != "passed"
            or receipt["proof_kind"] != "real_installer_synthetic_service_and_schema"
            or receipt["real_slot"]
            != {"state": "dormant", "resources": [], "live_authority": False}
            or receipt["effects"]
            != {
                "provider": False,
                "browser": False,
                "schedule": False,
                "installed_user_service": False,
                "operational_staging": False,
            }
        ):
            raise DrillError("operational_or_failed_receipt")
        if tuple(row["name"] for row in receipt["scenarios"]) != SCENARIOS:
            raise DrillError("incomplete_scenarios")
        if (
            not receipt["cleanup"]["verified"]
            or receipt["cleanup"]["remaining_processes"]
        ):
            raise DrillError("cleanup_incomplete")
        for role in ("candidate", "previous"):
            artifact = receipt["artifacts"][role]
            if any(
                artifact[key] != value
                for key, value in receipt["sources"][role].items()
            ):
                raise DrillError("artifact_source_mismatch")
            if not re.fullmatch(r"[0-9a-f]{64}", artifact["sha256"]):
                raise DrillError("artifact_digest_invalid")
            if artifact["build_sha256"] != [artifact["sha256"]] * (
                2 if role == "candidate" else 1
            ):
                raise DrillError("build_digest_mismatch")
        if receipt["artifacts"]["candidate"]["build_count"] != 2:
            raise DrillError("reproducibility_unproved")
        for scenario in receipt["scenarios"]:
            name = scenario["name"]
            actions, observations = scenario["actions"], scenario["observations"]
            commands = [action["command"] for action in actions]
            expected_commands = ["install", "upgrade"] + (
                ["rollback"] * (2 if name == "rollback_forward" else 1)
                if name in {"rollback", "rollback_forward"}
                else []
            )
            if commands != expected_commands or len(observations) != (
                1 if name == "recovery_failure" else len(commands)
            ):
                raise DrillError("attempt_or_observation_mismatch")
            for index, action in enumerate(actions):
                failure = index == 1 and name in {"failed_upgrade", "recovery_failure"}
                if (action["returncode"] != 0) != failure:
                    raise DrillError("action_result_mismatch")
            for index, observation in enumerate(observations):
                role = (
                    "previous"
                    if index == 0 or name == "failed_upgrade" or index == 2
                    else "candidate"
                )
                expected = receipt["artifacts"][role]
                if (
                    observation["integrity"] != "ok"
                    or observation["foreign_keys"]
                    or observation["readiness"]["service_version"]
                    != expected["version"]
                    or observation["readiness"]["runtime_manifest_sha256"]
                    != expected["manifest_sha256"]
                    or observation["readiness"]["contract_sha256"]
                    != expected["contract_sha256"]
                    or observation["readiness"]["database_schema_version"]
                    != expected["fixture_schema"]
                    or observation["readiness"]["service_status"] != "ready"
                    or observation["current"] != "releases/" + expected["version"]
                ):
                    raise DrillError("observation_identity_mismatch")
                peer = observation["socket_peer"]
                if not any(
                    record["pid"] == peer["pid"]
                    and record["start_ticks"] == peer["start_ticks"]
                    and record["scenario"] == name
                    for record in receipt["cleanup"]["processes"]
                ):
                    raise DrillError("socket_process_identity_mismatch")
            if (
                name == "failed_upgrade"
                and observations[0]["database_digest"]
                != observations[1]["database_digest"]
            ):
                raise DrillError("restoration_digest_mismatch")
            if (
                name in {"rollback", "rollback_forward"}
                and observations[0]["database_digest"]
                != observations[2]["database_digest"]
            ):
                raise DrillError("rollback_digest_mismatch")
            if (
                name == "rollback_forward"
                and observations[1]["database_digest"]
                != observations[3]["database_digest"]
            ):
                raise DrillError("forward_digest_mismatch")
            expected_outcome = (
                "blocked"
                if name == "recovery_failure"
                else "restored"
                if name in {"failed_upgrade", "rollback"}
                else "verified"
            )
            if scenario["outcome"] != expected_outcome:
                raise DrillError("outcome_mismatch")
        git = receipt["git"]
        if (
            not git["cleanup"]["verified"]
            or git["base_commit"] != git["activation_remote_commit"]
            or git["integration"]["merge_commit"] != git["final_main_commit"]
        ):
            raise DrillError("git_evidence_incomplete")
        if receipt["controls"] != _compose(receipt):
            raise DrillError("control_history_mismatch")
        if not 0 < receipt["elapsed_seconds"] <= 60:
            raise DrillError("drill_time_bound")
    except (KeyError, TypeError, ValueError, IndexError) as error:
        if isinstance(error, DrillError):
            raise
        raise DrillError("invalid_receipt") from error
    return {
        "status": "passed",
        "mode": "drill",
        "done_eligible": True,
        "work_item": "WI-007",
        "receipt_digest": receipt["receipt_digest"],
        "operational_authority": False,
        "limitations": "Synthetic incident/service/schema; production unchanged is a scope claim, not a live health readback",
    }
