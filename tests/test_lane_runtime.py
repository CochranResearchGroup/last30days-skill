"""Provider-free acceptance tests for the isolated lane runtime tracer."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
CONTROLLER = ROOT / "dev" / "last30days" / "scripts" / "lane_runtime.py"
CONTROLLER_SPEC = importlib.util.spec_from_file_location(
    "lane_runtime_under_test", CONTROLLER
)
assert CONTROLLER_SPEC is not None and CONTROLLER_SPEC.loader is not None
LANE_RUNTIME = importlib.util.module_from_spec(CONTROLLER_SPEC)
sys.modules[CONTROLLER_SPEC.name] = LANE_RUNTIME
CONTROLLER_SPEC.loader.exec_module(LANE_RUNTIME)


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _repo(tmp_path: Path, branch: str = "feat/lane-a") -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.name", "Lane Runtime Fixture")
    _git(repo, "config", "user.email", "fixture@example.invalid")
    (repo / "README.md").write_text("fixture\n", encoding="utf-8")
    _git(repo, "add", "README.md")
    _git(repo, "commit", "-q", "-m", "fixture")
    _git(repo, "switch", "-q", "-c", branch)
    _git(repo, "remote", "add", "origin", "git@github.com:Example/Fixture.git")
    return repo


def _doctor(
    repo: Path,
    state_root: Path,
    runtime_root: Path,
    *,
    environment: dict[str, str] | None = None,
    proposed_environment: dict[str, str] | None = None,
    **overrides: str,
):
    values = {
        "lane": "wi-001",
        "work_item": "WI-001",
        "plan": "0085",
    }
    values.update(overrides)
    command = [
        sys.executable,
        str(CONTROLLER),
        "doctor",
        "--lane",
        values["lane"],
        "--work-item",
        values["work_item"],
        "--plan",
        values["plan"],
        "--worktree",
        str(repo),
        "--state-root",
        str(state_root),
        "--runtime-root",
        str(runtime_root),
    ]
    if proposed_environment is not None:
        command.extend(
            ["--proposed-environment-json", json.dumps(proposed_environment)]
        )
    result = subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        env=environment,
    )
    return result, json.loads(result.stdout)


def _resign_descriptor(descriptor: dict[str, object]) -> None:
    unsigned = {
        key: value
        for key, value in descriptor.items()
        if key != "descriptor_digest"
    }
    descriptor["descriptor_digest"] = hashlib.sha256(
        json.dumps(
            unsigned,
            allow_nan=False,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
    ).hexdigest()


def test_doctor_is_deterministic_and_creates_nothing(tmp_path):
    repo = _repo(tmp_path)
    state_root = tmp_path / "state"
    runtime_root = tmp_path / "run"

    first_result, first = _doctor(repo, state_root, runtime_root)
    second_result, second = _doctor(repo, state_root, runtime_root)

    assert first_result.returncode == second_result.returncode == 0
    assert first == second
    assert first["ok"] is True
    assert first["reasons"] == []
    descriptor = first["descriptor"]
    assert descriptor["schema_version"] == 1
    assert descriptor["runtime_kind"] == "development"
    assert descriptor["lane_id"] == "wi-001"
    assert descriptor["work_item"] == "WI-001"
    assert descriptor["plan"] == "0085"
    assert descriptor["repository_identity"] == "github.com/example/fixture"
    assert descriptor["branch"] == "feat/lane-a"
    assert descriptor["commit"] == _git(repo, "rev-parse", "HEAD")
    assert descriptor["effect_mode"] == "cache_only"
    assert descriptor["credential_policy"] == "deny"
    assert descriptor["schedule_policy"] == "deny"
    assert descriptor["browser_policy"] == "deny"
    assert descriptor["inherited_environment_policy"] == "allowlist"
    assert Path(descriptor["state_root"]).is_relative_to(state_root)
    assert Path(descriptor["socket_path"]).is_relative_to(runtime_root)
    assert not state_root.exists()
    assert not runtime_root.exists()


def test_two_lanes_are_isolated_and_ambient_effect_inputs_are_not_inherited(tmp_path):
    repo = _repo(tmp_path)
    state_root = tmp_path / "state"
    runtime_root = tmp_path / "run"
    ambient = {
        **os.environ,
        "OPENAI_API_KEY": "dummy-secret",
        "AUTH_TOKEN": "dummy-cookie",
        "LAST30DAYS_GRAPHITI_URL": "http://127.0.0.1:9999",
        "LAST30DAYS_APP_INTELLIGENCE_ASSESSMENT": "1",
        "LAST30DAYS_BROWSER_PROFILE": "/forbidden/profile",
        "LAST30DAYS_TICK_SCHEDULE": "enabled",
    }

    first_result, first = _doctor(
        repo, state_root, runtime_root, environment=ambient, lane="wi-001-a"
    )
    second_result, second = _doctor(
        repo, state_root, runtime_root, environment=ambient, lane="wi-001-b"
    )

    assert first_result.returncode == second_result.returncode == 0
    first_descriptor = first["descriptor"]
    second_descriptor = second["descriptor"]
    assert first_descriptor["runtime_id"] != second_descriptor["runtime_id"]
    mutable_paths = (
        "state_root",
        "config_dir",
        "data_dir",
        "database_path",
        "artifacts_dir",
        "log_path",
        "run_dir",
        "socket_path",
        "pid_path",
        "descriptor_path",
        "tick_config_path",
    )
    for field in mutable_paths:
        assert first_descriptor[field] != second_descriptor[field]

    child = first["child_environment"]
    assert child["PATH"] == "/usr/bin:/bin"
    assert child["HOME"] == str(Path(first_descriptor["state_root"]) / "home")
    assert child["LAST30DAYS_EFFECT_MODE"] == "cache_only"
    assert child["LAST30DAYS_CREDENTIAL_POLICY"] == "deny"
    assert child["LAST30DAYS_SCHEDULE_POLICY"] == "deny"
    assert child["LAST30DAYS_BROWSER_POLICY"] == "deny"
    assert not set(ambient).intersection(
        {
            "OPENAI_API_KEY",
            "AUTH_TOKEN",
            "LAST30DAYS_GRAPHITI_URL",
            "LAST30DAYS_APP_INTELLIGENCE_ASSESSMENT",
            "LAST30DAYS_BROWSER_PROFILE",
            "LAST30DAYS_TICK_SCHEDULE",
        }
    ).intersection(child)


def test_doctor_rejects_production_containment_and_overlong_socket(tmp_path):
    repo = _repo(tmp_path)
    home = tmp_path / "home"
    ambient = {
        **os.environ,
        "HOME": str(home),
        "XDG_CONFIG_HOME": str(home / ".config"),
        "XDG_DATA_HOME": str(home / ".local" / "share"),
        "XDG_RUNTIME_DIR": str(tmp_path / "production-run"),
    }

    collision_result, collision = _doctor(
        repo,
        home / ".config" / "last30days",
        tmp_path / "safe-run",
        environment=ambient,
    )
    long_result, long_path = _doctor(
        repo,
        tmp_path / "safe-state",
        tmp_path / ("x" * 120),
        environment=ambient,
    )

    assert collision_result.returncode == long_result.returncode == 2
    assert collision["ok"] is False
    assert "production_path_collision:state_root" in collision["reasons"]
    assert long_path["ok"] is False
    assert "unix_socket_path_too_long" in long_path["reasons"]
    assert not (home / ".config" / "last30days").exists()
    assert not (tmp_path / ("x" * 120)).exists()


def test_doctor_rejects_a_dirty_worktree_without_cleaning_it(tmp_path):
    repo = _repo(tmp_path)
    state_root = tmp_path / "state"
    runtime_root = tmp_path / "run"
    dirty_path = repo / "uncommitted.txt"
    dirty_path.write_text("preserve me\n", encoding="utf-8")

    result, report = _doctor(repo, state_root, runtime_root)

    assert result.returncode == 2
    assert report["ok"] is False
    assert report["reasons"] == ["worktree_not_clean"]
    assert dirty_path.read_text(encoding="utf-8") == "preserve me\n"
    assert not state_root.exists()
    assert not runtime_root.exists()


def test_doctor_rejects_a_symlinked_state_root(tmp_path):
    repo = _repo(tmp_path)
    escaped = tmp_path / "escaped"
    escaped.mkdir()
    state_root = tmp_path / "state-link"
    state_root.symlink_to(escaped, target_is_directory=True)
    runtime_root = tmp_path / "run"

    result, report = _doctor(repo, state_root, runtime_root)

    assert result.returncode == 2
    assert report["ok"] is False
    assert report["reasons"] == ["unsafe_symlink:state_root"]
    assert list(escaped.iterdir()) == []
    assert not runtime_root.exists()


def test_doctor_accepts_only_the_exact_descriptor_schema(tmp_path):
    repo = _repo(tmp_path)
    state_root = tmp_path / "state"
    runtime_root = tmp_path / "run"
    _, initial = _doctor(repo, state_root, runtime_root)
    descriptor = initial["descriptor"]
    descriptor_path = Path(descriptor["descriptor_path"])
    descriptor_path.parent.mkdir(parents=True)
    descriptor_path.write_text(
        json.dumps(descriptor, sort_keys=True) + "\n", encoding="utf-8"
    )

    accepted_result, accepted = _doctor(repo, state_root, runtime_root)
    descriptor_path.write_text(
        json.dumps({**descriptor, "unexpected": True}, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    rejected_result, rejected = _doctor(repo, state_root, runtime_root)

    assert accepted_result.returncode == 0
    assert accepted["ok"] is True
    assert rejected_result.returncode == 2
    assert rejected["ok"] is False
    assert "descriptor_schema_invalid" in rejected["reasons"]

    forged = dict(descriptor)
    forged["tick_config_digest"] = "0" * 64
    _resign_descriptor(forged)
    descriptor_path.write_text(
        json.dumps(forged, sort_keys=True) + "\n", encoding="utf-8"
    )

    forged_result, forged_report = _doctor(repo, state_root, runtime_root)

    assert forged_result.returncode == 2
    assert forged_report["ok"] is False
    assert "descriptor_schema_invalid" in forged_report["reasons"]


def test_doctor_rejects_a_descriptor_owned_by_another_worktree(tmp_path):
    repo = _repo(tmp_path)
    state_root = tmp_path / "state"
    runtime_root = tmp_path / "run"
    _, initial = _doctor(repo, state_root, runtime_root)
    descriptor = initial["descriptor"]
    descriptor_path = Path(descriptor["descriptor_path"])
    descriptor_path.parent.mkdir(parents=True)
    descriptor["worktree"] = str(tmp_path / "foreign-worktree")
    _resign_descriptor(descriptor)
    descriptor_path.write_text(
        json.dumps(descriptor, sort_keys=True) + "\n", encoding="utf-8"
    )

    result, report = _doctor(repo, state_root, runtime_root)

    assert result.returncode == 2
    assert report["ok"] is False
    assert "foreign_descriptor" in report["reasons"]


def test_doctor_rejects_denied_or_non_allowlisted_child_environment_keys(tmp_path):
    repo = _repo(tmp_path)
    state_root = tmp_path / "state"
    runtime_root = tmp_path / "run"
    proposed = {
        "AUTH_TOKEN": "dummy-cookie",
        "LAST30DAYS_GRAPHITI_URL": "http://127.0.0.1:9999",
        "LAST30DAYS_TICK_SCHEDULE": "dummy-tick-enable-marker",
        "SAFE_EXTRA": "dummy-extra-marker",
    }

    result, report = _doctor(
        repo,
        state_root,
        runtime_root,
        proposed_environment=proposed,
    )

    assert result.returncode == 2
    assert report["ok"] is False
    assert report["reasons"] == [
        "environment_key_denied:AUTH_TOKEN",
        "environment_key_denied:LAST30DAYS_GRAPHITI_URL",
        "environment_key_denied:LAST30DAYS_TICK_SCHEDULE",
        "environment_key_not_allowlisted:SAFE_EXTRA",
    ]
    assert all(value not in result.stdout + result.stderr for value in proposed.values())
    assert not state_root.exists()
    assert not runtime_root.exists()


def test_doctor_fails_closed_on_an_existing_runtime_owner_record(tmp_path):
    repo = _repo(tmp_path)
    state_root = tmp_path / "state"
    runtime_root = tmp_path / "run"
    _, initial = _doctor(repo, state_root, runtime_root)
    pid_path = Path(initial["descriptor"]["pid_path"])
    pid_path.parent.mkdir(parents=True)
    pid_path.write_text('{"pid": 424242}\n', encoding="utf-8")

    result, report = _doctor(repo, state_root, runtime_root)

    assert result.returncode == 2
    assert report["ok"] is False
    assert "existing_runtime_owner_unverified" in report["reasons"]
    assert pid_path.read_text(encoding="utf-8") == '{"pid": 424242}\n'


@pytest.mark.parametrize(
    ("path_field", "reason"),
    [
        ("lock_path", "runtime_lock_collision"),
        ("socket_path", "runtime_socket_collision"),
    ],
)
def test_doctor_fails_closed_on_owned_runtime_collisions(
    tmp_path, path_field, reason
):
    repo = _repo(tmp_path)
    state_root = tmp_path / "state"
    runtime_root = tmp_path / "run"
    _, initial = _doctor(repo, state_root, runtime_root)
    collision_path = Path(initial["descriptor"][path_field])
    collision_path.parent.mkdir(parents=True)
    collision_path.write_text("preserve me\n", encoding="utf-8")

    result, report = _doctor(repo, state_root, runtime_root)

    assert result.returncode == 2
    assert report["ok"] is False
    assert reason in report["reasons"]
    assert collision_path.read_text(encoding="utf-8") == "preserve me\n"


def test_socket_owned_by_another_uid_fails_closed(tmp_path, monkeypatch):
    repo = _repo(tmp_path)
    state_root = tmp_path / "state"
    runtime_root = tmp_path / "run"
    descriptor = LANE_RUNTIME.build_descriptor(
        lane_id="wi-001",
        work_item="WI-001",
        plan="0085",
        worktree=repo,
        state_base=state_root,
        runtime_base=runtime_root,
    )
    socket_path = Path(descriptor.socket_path)
    socket_path.parent.mkdir(parents=True)
    socket_path.write_text("synthetic collision\n", encoding="utf-8")
    current_uid = os.geteuid()
    monkeypatch.setattr(LANE_RUNTIME.os, "geteuid", lambda: current_uid + 1)

    reasons = LANE_RUNTIME._descriptor_reasons(descriptor, os.environ)

    assert "runtime_socket_not_owned" in reasons


def test_doctor_rejects_default_branch_custody(tmp_path):
    repo = _repo(tmp_path, branch="main")

    result, report = _doctor(repo, tmp_path / "state", tmp_path / "run")

    assert result.returncode == 2
    assert report["ok"] is False
    assert report["reasons"] == ["reserved_branch"]


def test_doctor_rejects_detached_head_custody(tmp_path):
    repo = _repo(tmp_path)
    _git(repo, "switch", "-q", "--detach", "HEAD")

    result, report = _doctor(repo, tmp_path / "state", tmp_path / "run")

    assert result.returncode == 2
    assert report["ok"] is False
    assert report["reasons"] == ["detached_head"]


def test_doctor_emits_only_a_disabled_tick_fixture_and_rejects_drift(tmp_path):
    repo = _repo(tmp_path)
    state_root = tmp_path / "state"
    runtime_root = tmp_path / "run"
    _, initial = _doctor(repo, state_root, runtime_root)
    fixture = initial["offline_tick_configuration"]

    assert fixture == {
        "schema_version": 1,
        "runtime_id": initial["descriptor"]["runtime_id"],
        "enabled": False,
        "effect_mode": "cache_only",
        "sources": [],
        "schedules": [],
        "credential_policy": "deny",
        "browser_policy": "deny",
    }
    tick_path = Path(initial["descriptor"]["tick_config_path"])
    tick_path.parent.mkdir(parents=True)
    tick_path.write_text(
        json.dumps({**fixture, "enabled": True}, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    result, report = _doctor(repo, state_root, runtime_root)

    assert result.returncode == 2
    assert report["ok"] is False
    assert "tick_configuration_not_controller_owned" in report["reasons"]
    assert json.loads(tick_path.read_text(encoding="utf-8"))["enabled"] is True


def test_doctor_rejects_a_nested_runtime_path_symlink(tmp_path):
    repo = _repo(tmp_path)
    state_root = tmp_path / "state"
    state_root.mkdir()
    escaped = tmp_path / "escaped"
    escaped.mkdir()
    (state_root / "last30days").symlink_to(escaped, target_is_directory=True)

    result, report = _doctor(repo, state_root, tmp_path / "run")

    assert result.returncode == 2
    assert report["ok"] is False
    assert "unsafe_symlink:state_root" in report["reasons"]
    assert list(escaped.iterdir()) == []


def test_doctor_rejects_broad_or_overlapping_roots(tmp_path):
    repo = _repo(tmp_path)

    broad_result, broad = _doctor(repo, Path("/"), tmp_path / "run")
    overlap_result, overlap = _doctor(
        repo, tmp_path / "shared", tmp_path / "shared"
    )

    assert broad_result.returncode == overlap_result.returncode == 2
    assert broad["reasons"] == ["broad_root:state_root"]
    assert overlap["reasons"] == ["runtime_roots_overlap"]


def test_doctor_rejects_runtime_roots_inside_the_worktree(tmp_path):
    repo = _repo(tmp_path)

    result, report = _doctor(
        repo, repo / ".lane-state", tmp_path / "runtime"
    )

    assert result.returncode == 2
    assert report["reasons"] == ["runtime_path_inside_worktree:state_root"]
    assert not (repo / ".lane-state").exists()


@pytest.mark.parametrize(
    "lane_id",
    ["production-blue", "prod-1", "staging-blue", "../escape", "WI-001"],
)
def test_doctor_rejects_reserved_or_unsafe_lane_identifiers(tmp_path, lane_id):
    repo = _repo(tmp_path)

    result, report = _doctor(
        repo, tmp_path / "state", tmp_path / "run", lane=lane_id
    )

    assert result.returncode == 2
    assert report["ok"] is False
    assert report["reasons"] == ["invalid_lane_id"]
