#!/usr/bin/env python3
"""Read-only identity tracer for isolated last30days development runtimes.

Packet 1 intentionally exposes only ``doctor``.  It derives and validates a
lane descriptor without creating files, opening sockets, or starting services.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from dataclasses import asdict, dataclass, fields
from pathlib import Path
from typing import Mapping, Sequence
from urllib.parse import urlparse


SCHEMA_VERSION = 1
RUNTIME_KIND = "development"
EFFECT_MODE = "cache_only"
_LANE_PATTERN = re.compile(r"^[a-z][a-z0-9-]{0,31}$")
_LOCATOR_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]{0,127}$")
_COMMIT_PATTERN = re.compile(r"^[0-9a-f]{40}$")
_RESERVED_LANES = frozenset(
    {"default", "develop", "main", "master", "prod", "production", "stage", "staging"}
)
_PROPOSED_ENV_ALLOWLIST = frozenset({"LANG", "LC_ALL", "LC_CTYPE", "TZ"})
_DENIED_ENV_PATTERN = re.compile(
    r"(?:^|_)(?:API_?KEY|AUTH|BROWSER|COOKIE|CREDENTIAL|GRAPHITI|NOTIFICATION|"
    r"ASSESSMENT|PASSWORD|PROFILE|PROVIDER|SCHEDULE|SECRET|TICK|TOKEN)(?:_|$)"
)


def canonical_json(value: object) -> str:
    """Return the single canonical JSON encoding used by descriptor digests."""

    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def _digest(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _run_git(worktree: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=worktree,
        check=False,
        capture_output=True,
        text=True,
        timeout=10,
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip().splitlines()
        raise ValueError(detail[-1] if detail else f"git {' '.join(args)} failed")
    return result.stdout.strip()


def _current_branch(worktree: Path) -> str:
    result = subprocess.run(
        ["git", "symbolic-ref", "--quiet", "--short", "HEAD"],
        cwd=worktree,
        check=False,
        capture_output=True,
        text=True,
        timeout=10,
    )
    if result.returncode == 1:
        raise ValueError("detached_head")
    if result.returncode != 0:
        raise ValueError("branch_identity_unavailable")
    return result.stdout.strip()


def normalize_repository_identity(remote: str) -> str:
    """Normalize an HTTPS or SSH Git remote into a stable host/path identity."""

    value = remote.strip()
    if re.fullmatch(r"[^/@:]+@[^/:]+:.+", value):
        _, tail = value.split("@", 1)
        host, path = tail.split(":", 1)
    else:
        parsed = urlparse(value)
        if parsed.scheme not in {"http", "https", "ssh"} or not parsed.hostname:
            raise ValueError("origin remote must be an absolute HTTPS or SSH URL")
        host = parsed.hostname
        path = parsed.path.lstrip("/")
    path = path.removesuffix(".git").strip("/")
    if not host or not path or "/" not in path:
        raise ValueError("origin remote must identify a hosted repository")
    return f"{host.lower()}/{path.lower()}"


@dataclass(frozen=True)
class LaneRuntimeDescriptorV1:
    """Strict, canonical identity for one development runtime lane."""

    schema_version: int
    runtime_kind: str
    runtime_id: str
    lane_id: str
    work_item: str
    plan: str
    repository_identity: str
    worktree: str
    branch: str
    commit: str
    committed_at: str
    state_root: str
    config_dir: str
    data_dir: str
    database_path: str
    artifacts_dir: str
    log_dir: str
    log_path: str
    run_dir: str
    socket_path: str
    pid_path: str
    lock_path: str
    descriptor_path: str
    tick_config_path: str
    tick_config_digest: str
    startup_receipt_path: str
    status_receipt_path: str
    service_name: str
    effect_mode: str
    credential_policy: str
    schedule_policy: str
    browser_policy: str
    inherited_environment_policy: str
    created_at: str
    updated_at: str
    descriptor_digest: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> LaneRuntimeDescriptorV1:
        expected = {field.name for field in fields(cls)}
        if set(payload) != expected:
            raise ValueError("descriptor_schema_invalid")
        if payload.get("schema_version") != SCHEMA_VERSION:
            raise ValueError("descriptor_schema_invalid")
        string_fields = expected - {"schema_version"}
        if any(
            not isinstance(payload.get(name), str) or not payload[name]
            for name in string_fields
        ):
            raise ValueError("descriptor_schema_invalid")
        if payload.get("runtime_kind") != RUNTIME_KIND:
            raise ValueError("descriptor_schema_invalid")
        if payload.get("effect_mode") != EFFECT_MODE:
            raise ValueError("descriptor_schema_invalid")
        if any(
            payload.get(name) != expected_value
            for name, expected_value in (
                ("credential_policy", "deny"),
                ("schedule_policy", "deny"),
                ("browser_policy", "deny"),
                ("inherited_environment_policy", "allowlist"),
            )
        ):
            raise ValueError("descriptor_schema_invalid")
        commit = payload.get("commit")
        digest = payload.get("descriptor_digest")
        if not isinstance(commit, str) or not _COMMIT_PATTERN.fullmatch(commit):
            raise ValueError("descriptor_schema_invalid")
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise ValueError("descriptor_schema_invalid")
        runtime_id = payload.get("runtime_id")
        tick_config_digest = payload.get("tick_config_digest")
        if (
            not isinstance(runtime_id, str)
            or not isinstance(tick_config_digest, str)
            or tick_config_digest
            != _digest(build_offline_tick_configuration(runtime_id))
        ):
            raise ValueError("descriptor_schema_invalid")
        unsigned = dict(payload)
        unsigned.pop("descriptor_digest")
        if _digest(unsigned) != digest:
            raise ValueError("descriptor_schema_invalid")
        return cls(**payload)  # type: ignore[arg-type]


def _validated_locator(value: str, name: str) -> str:
    if not _LOCATOR_PATTERN.fullmatch(value) or ".." in value.split("/"):
        raise ValueError(f"{name} is invalid")
    return value


def build_offline_tick_configuration(runtime_id: str) -> dict[str, object]:
    """Return the only Tick configuration permitted for a Packet 1 lane."""

    return {
        "schema_version": 1,
        "runtime_id": runtime_id,
        "enabled": False,
        "effect_mode": EFFECT_MODE,
        "sources": [],
        "schedules": [],
        "credential_policy": "deny",
        "browser_policy": "deny",
    }


def build_descriptor(
    *,
    lane_id: str,
    work_item: str,
    plan: str,
    worktree: Path,
    state_base: Path,
    runtime_base: Path,
) -> LaneRuntimeDescriptorV1:
    """Derive one commit-bound descriptor from an existing clean worktree."""

    if not _LANE_PATTERN.fullmatch(lane_id) or any(
        lane_id == reserved or lane_id.startswith(f"{reserved}-")
        for reserved in _RESERVED_LANES
    ):
        raise ValueError("invalid_lane_id")
    _validated_locator(work_item, "work item")
    _validated_locator(plan, "plan")
    if not (
        worktree.is_absolute()
        and state_base.is_absolute()
        and runtime_base.is_absolute()
    ):
        raise ValueError("worktree and runtime roots must be absolute")
    worktree = worktree.resolve(strict=True)
    top_level = Path(
        _run_git(worktree, "rev-parse", "--show-toplevel")
    ).resolve(strict=True)
    if top_level != worktree:
        raise ValueError("worktree must be the Git top-level directory")
    if _run_git(worktree, "status", "--porcelain=v1", "--untracked-files=all"):
        raise ValueError("worktree_not_clean")
    branch = _current_branch(worktree)
    if branch in _RESERVED_LANES:
        raise ValueError("reserved_branch")
    commit = _run_git(worktree, "rev-parse", "HEAD")
    if not _COMMIT_PATTERN.fullmatch(commit):
        raise ValueError("Git commit identity is invalid")
    committed_at = _run_git(worktree, "show", "-s", "--format=%cI", "HEAD")
    repository_identity = normalize_repository_identity(
        _run_git(worktree, "remote", "get-url", "origin")
    )
    runtime_hash = _digest(
        {"lane_id": lane_id, "repository_identity": repository_identity}
    )[:12]
    runtime_id = f"l30d-{lane_id}-{runtime_hash}"
    tick_configuration = build_offline_tick_configuration(runtime_id)
    state_root = state_base.resolve(strict=False) / "last30days" / "lanes" / runtime_id
    socket_path = runtime_base.resolve(strict=False) / f"l30d-{runtime_hash}.sock"
    config_dir = state_root / "config"
    data_dir = state_root / "data"
    artifacts_dir = state_root / "artifacts"
    log_dir = state_root / "logs"
    run_dir = state_root / "run"
    payload: dict[str, object] = {
        "schema_version": SCHEMA_VERSION,
        "runtime_kind": RUNTIME_KIND,
        "runtime_id": runtime_id,
        "lane_id": lane_id,
        "work_item": work_item,
        "plan": plan,
        "repository_identity": repository_identity,
        "worktree": str(worktree),
        "branch": branch,
        "commit": commit,
        "committed_at": committed_at,
        "state_root": str(state_root),
        "config_dir": str(config_dir),
        "data_dir": str(data_dir),
        "database_path": str(data_dir / "research.db"),
        "artifacts_dir": str(artifacts_dir),
        "log_dir": str(log_dir),
        "log_path": str(log_dir / "service.log"),
        "run_dir": str(run_dir),
        "socket_path": str(socket_path),
        "pid_path": str(run_dir / "service.pid.json"),
        "lock_path": str(run_dir / "controller.lock"),
        "descriptor_path": str(state_root / "descriptor.json"),
        "tick_config_path": str(config_dir / "tick.json"),
        "tick_config_digest": _digest(tick_configuration),
        "startup_receipt_path": str(state_root / "receipts" / "startup.json"),
        "status_receipt_path": str(state_root / "receipts" / "status.json"),
        "service_name": f"last30days-dev-{lane_id}-{runtime_hash}",
        "effect_mode": EFFECT_MODE,
        "credential_policy": "deny",
        "schedule_policy": "deny",
        "browser_policy": "deny",
        "inherited_environment_policy": "allowlist",
        "created_at": committed_at,
        "updated_at": committed_at,
    }
    payload["descriptor_digest"] = _digest(payload)
    return LaneRuntimeDescriptorV1(**payload)  # type: ignore[arg-type]


def build_child_environment(
    descriptor: LaneRuntimeDescriptorV1,
    environ: Mapping[str, str] | None = None,
) -> dict[str, str]:
    """Build a minimal allowlisted environment without copying ambient effects."""

    parent = environ or {}
    state_root = Path(descriptor.state_root)
    child = {
        "HOME": str(state_root / "home"),
        "PATH": "/usr/bin:/bin",
        "PYTHONNOUSERSITE": "1",
        "TMPDIR": str(state_root / "tmp"),
        "XDG_CACHE_HOME": str(state_root / "cache"),
        "XDG_CONFIG_HOME": descriptor.config_dir,
        "XDG_DATA_HOME": descriptor.data_dir,
        "XDG_RUNTIME_DIR": str(Path(descriptor.socket_path).parent),
        "XDG_STATE_HOME": descriptor.state_root,
        "LAST30DAYS_CONFIG_DIR": descriptor.config_dir,
        "LAST30DAYS_SERVICE_DB": descriptor.database_path,
        "LAST30DAYS_SERVICE_SOCKET": descriptor.socket_path,
        "LAST30DAYS_RUNTIME_ID": descriptor.runtime_id,
        "LAST30DAYS_EFFECT_MODE": descriptor.effect_mode,
        "LAST30DAYS_CREDENTIAL_POLICY": descriptor.credential_policy,
        "LAST30DAYS_SCHEDULE_POLICY": descriptor.schedule_policy,
        "LAST30DAYS_BROWSER_POLICY": descriptor.browser_policy,
    }
    for key in ("LANG", "LC_ALL", "LC_CTYPE", "TZ"):
        value = parent.get(key, "").strip()
        if value:
            child[key] = value
    return dict(sorted(child.items()))


def proposed_environment_reasons(proposed: Mapping[str, str]) -> list[str]:
    """Return stable reason codes without exposing any environment values."""

    reasons: list[str] = []
    for key, value in proposed.items():
        if not isinstance(key, str) or not isinstance(value, str) or not key:
            reasons.append("environment_entry_invalid")
        elif _DENIED_ENV_PATTERN.search(key.upper()):
            reasons.append(f"environment_key_denied:{key}")
        elif key not in _PROPOSED_ENV_ALLOWLIST:
            reasons.append(f"environment_key_not_allowlisted:{key}")
    return sorted(set(reasons))


def _is_equal_or_within(candidate: Path, root: Path) -> bool:
    candidate = candidate.resolve(strict=False)
    root = root.resolve(strict=False)
    return candidate == root or candidate.is_relative_to(root)


def _contains_symlink(path: Path) -> bool:
    if not path.is_absolute():
        return False
    current = Path(path.anchor)
    for part in path.parts[1:]:
        current /= part
        if current.is_symlink():
            return True
        if not current.exists():
            break
    return False


def _descriptor_reasons(
    descriptor: LaneRuntimeDescriptorV1,
    environ: Mapping[str, str] | None,
) -> list[str]:
    parent = environ or {}
    home = Path(parent.get("HOME") or Path.home()).expanduser().resolve(strict=False)
    config_home = Path(parent.get("XDG_CONFIG_HOME") or home / ".config")
    data_home = Path(parent.get("XDG_DATA_HOME") or home / ".local" / "share")
    runtime_home_value = parent.get("XDG_RUNTIME_DIR")
    forbidden_roots = [
        (config_home / "last30days").resolve(strict=False),
        (data_home / "last30days").resolve(strict=False),
    ]
    if runtime_home_value:
        forbidden_roots.append(
            (Path(runtime_home_value).expanduser() / "last30days").resolve(
                strict=False
            )
        )
    path_fields = (
        "state_root",
        "config_dir",
        "data_dir",
        "database_path",
        "artifacts_dir",
        "log_dir",
        "log_path",
        "run_dir",
        "socket_path",
        "pid_path",
        "lock_path",
        "descriptor_path",
        "tick_config_path",
        "startup_receipt_path",
        "status_receipt_path",
    )
    reasons: list[str] = []
    for field in path_fields:
        candidate = Path(getattr(descriptor, field))
        if _contains_symlink(candidate):
            reasons.append(f"unsafe_symlink:{field}")
        if any(_is_equal_or_within(candidate, root) for root in forbidden_roots):
            reasons.append(f"production_path_collision:{field}")
    if len(os.fsencode(descriptor.socket_path)) > 103:
        reasons.append("unix_socket_path_too_long")
    if Path(descriptor.pid_path).exists() or Path(descriptor.pid_path).is_symlink():
        reasons.append("existing_runtime_owner_unverified")
    if Path(descriptor.lock_path).exists() or Path(descriptor.lock_path).is_symlink():
        reasons.append("runtime_lock_collision")
    socket_path = Path(descriptor.socket_path)
    if socket_path.exists() or socket_path.is_symlink():
        try:
            if socket_path.lstat().st_uid != os.geteuid():
                reasons.append("runtime_socket_not_owned")
            else:
                reasons.append("runtime_socket_collision")
        except OSError:
            reasons.append("runtime_socket_unverifiable")
    descriptor_path = Path(descriptor.descriptor_path)
    if descriptor_path.exists() or descriptor_path.is_symlink():
        if _contains_symlink(descriptor_path):
            reasons.append("unsafe_symlink:descriptor_path")
        elif not descriptor_path.is_file():
            reasons.append("descriptor_schema_invalid")
        else:
            try:
                raw = descriptor_path.read_bytes()
                if len(raw) > 65_536:
                    raise ValueError("descriptor_schema_invalid")
                stored = json.loads(raw.decode("utf-8"))
                if not isinstance(stored, dict):
                    raise ValueError("descriptor_schema_invalid")
                stored_descriptor = LaneRuntimeDescriptorV1.from_dict(stored)
                if stored_descriptor != descriptor:
                    reasons.append("foreign_descriptor")
            except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError):
                reasons.append("descriptor_schema_invalid")
    tick_config_path = Path(descriptor.tick_config_path)
    if tick_config_path.exists() or tick_config_path.is_symlink():
        if _contains_symlink(tick_config_path) or not tick_config_path.is_file():
            reasons.append("tick_configuration_not_controller_owned")
        else:
            try:
                raw = tick_config_path.read_bytes()
                if len(raw) > 65_536:
                    raise ValueError
                stored_tick = json.loads(raw.decode("utf-8"))
                if stored_tick != build_offline_tick_configuration(
                    descriptor.runtime_id
                ):
                    raise ValueError
            except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError):
                reasons.append("tick_configuration_not_controller_owned")
    return sorted(set(reasons))


def doctor(
    *,
    lane_id: str,
    work_item: str,
    plan: str,
    worktree: Path,
    state_base: Path,
    runtime_base: Path,
    environ: Mapping[str, str] | None = None,
    proposed_environment: Mapping[str, str] | None = None,
) -> dict[str, object]:
    """Return readiness without changing the filesystem or runtime state."""

    root_reasons: list[str] = []
    if state_base.is_absolute() and state_base.resolve(strict=False) == Path("/"):
        root_reasons.append("broad_root:state_root")
    if runtime_base.is_absolute() and runtime_base.resolve(strict=False) == Path("/"):
        root_reasons.append("broad_root:runtime_root")
    if not root_reasons and state_base.is_absolute() and runtime_base.is_absolute():
        resolved_state = state_base.resolve(strict=False)
        resolved_runtime = runtime_base.resolve(strict=False)
        if _is_equal_or_within(resolved_state, resolved_runtime) or _is_equal_or_within(
            resolved_runtime, resolved_state
        ):
            root_reasons.append("runtime_roots_overlap")
        if worktree.is_absolute():
            resolved_worktree = worktree.resolve(strict=False)
            if _is_equal_or_within(resolved_state, resolved_worktree):
                root_reasons.append("runtime_path_inside_worktree:state_root")
            if _is_equal_or_within(resolved_runtime, resolved_worktree):
                root_reasons.append("runtime_path_inside_worktree:runtime_root")
    if root_reasons:
        return {
            "schema_version": SCHEMA_VERSION,
            "ok": False,
            "reasons": sorted(set(root_reasons)),
            "descriptor": None,
            "child_environment": None,
            "offline_tick_configuration": None,
        }
    for label, path in (
        ("worktree", worktree),
        ("state_root", state_base),
        ("runtime_root", runtime_base),
    ):
        if _contains_symlink(path):
            return {
                "schema_version": SCHEMA_VERSION,
                "ok": False,
                "reasons": [f"unsafe_symlink:{label}"],
                "descriptor": None,
                "child_environment": None,
                "offline_tick_configuration": None,
            }
    try:
        descriptor = build_descriptor(
            lane_id=lane_id,
            work_item=work_item,
            plan=plan,
            worktree=worktree,
            state_base=state_base,
            runtime_base=runtime_base,
        )
        child_environment = build_child_environment(descriptor, environ)
        reasons = _descriptor_reasons(descriptor, environ)
        if proposed_environment is not None:
            reasons.extend(proposed_environment_reasons(proposed_environment))
            if not reasons:
                child_environment.update(proposed_environment)
                child_environment = dict(sorted(child_environment.items()))
    except (OSError, subprocess.SubprocessError, ValueError) as exc:
        return {
            "schema_version": SCHEMA_VERSION,
            "ok": False,
            "reasons": [str(exc)],
            "descriptor": None,
            "child_environment": None,
            "offline_tick_configuration": None,
        }
    tick_configuration = build_offline_tick_configuration(descriptor.runtime_id)
    return {
        "schema_version": SCHEMA_VERSION,
        "ok": not reasons,
        "reasons": reasons,
        "descriptor": descriptor.to_dict(),
        "child_environment": child_environment,
        "offline_tick_configuration": tick_configuration,
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Inspect an isolated last30days development runtime identity"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    doctor_parser = subparsers.add_parser(
        "doctor", help="derive and validate a lane descriptor without writing state"
    )
    doctor_parser.add_argument("--lane", required=True)
    doctor_parser.add_argument("--work-item", required=True)
    doctor_parser.add_argument("--plan", required=True)
    doctor_parser.add_argument("--worktree", type=Path, required=True)
    doctor_parser.add_argument("--state-root", type=Path, required=True)
    doctor_parser.add_argument("--runtime-root", type=Path, required=True)
    doctor_parser.add_argument(
        "--proposed-environment-json",
        help="validate optional locale-only child environment additions",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    proposed_environment = None
    if args.proposed_environment_json is not None:
        try:
            decoded = json.loads(args.proposed_environment_json)
            if not isinstance(decoded, dict) or any(
                not isinstance(key, str) or not isinstance(value, str)
                for key, value in decoded.items()
            ):
                raise ValueError
            proposed_environment = decoded
        except (json.JSONDecodeError, ValueError):
            report = {
                "schema_version": SCHEMA_VERSION,
                "ok": False,
                "reasons": ["proposed_environment_json_invalid"],
                "descriptor": None,
                "child_environment": None,
                "offline_tick_configuration": None,
            }
            print(json.dumps(report, indent=2, sort_keys=True))
            return 2
    report = doctor(
        lane_id=args.lane,
        work_item=args.work_item,
        plan=args.plan,
        worktree=args.worktree,
        state_base=args.state_root,
        runtime_base=args.runtime_root,
        environ=os.environ,
        proposed_environment=proposed_environment,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["ok"] else 2


if __name__ == "__main__":
    sys.exit(main())
