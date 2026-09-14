"""Operator-visible isolation and recovery proof for the disposable hotfix drill."""

import copy
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "dev/last30days/scripts"))


@pytest.fixture(scope="module")
def source_repository(tmp_path_factory):
    root = tmp_path_factory.mktemp("hotfix-source")
    env = {
        "PATH": "/usr/bin:/bin",
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": os.devnull,
    }

    def git(*args):
        return (
            subprocess.check_output(["git", "-C", str(root), *args], env=env)
            .decode()
            .strip()
        )

    subprocess.run(
        [
            "git",
            "clone",
            "--quiet",
            "--no-hardlinks",
            "--no-checkout",
            str(ROOT),
            str(root),
        ],
        env=env,
        check=True,
    )
    commit = git("rev-parse", "refs/remotes/origin/main")
    git("-c", "core.hooksPath=/dev/null", "checkout", "--quiet", "--detach", commit)
    return root, commit, "94d4852fabd56e09f399ec77816ff25a690e294a"


def test_preflight_rejects_stale_source_without_creating_state(
    source_repository, tmp_path
):
    from hotfix_runtime_drill import DrillError, preflight

    before = list(tmp_path.iterdir())
    with pytest.raises(DrillError, match="source_commit_mismatch"):
        preflight(source_repository[0], "0" * 40, "1" * 40, environment={})
    assert list(tmp_path.iterdir()) == before


@pytest.fixture
def short_root():
    with tempfile.TemporaryDirectory(prefix="wi007-test-") as directory:
        yield Path(directory)


def test_upgrade_baseline_uses_disposable_installer_and_cleans_owned_processes(
    source_repository, short_root
):
    from hotfix_runtime_drill import run_drill

    sentinel = short_root / "foreign.txt"
    sentinel.write_text("preserve")
    receipt = run_drill(
        *source_repository, parent=short_root, scenarios=("upgrade",), environment={}
    )
    assert receipt["status"] == "passed"
    assert receipt["scenarios"][0]["name"] == "upgrade"
    assert (
        receipt["scenarios"][0]["observations"][-1]["readiness"]["service_version"]
        == "0.3.118"
    )
    assert receipt["cleanup"]["remaining_processes"] == []
    assert not Path(receipt["fixture_root"]).exists()
    assert list(short_root.iterdir()) == [sentinel]


def test_failed_upgrade_restores_the_exact_disposable_database(
    source_repository, short_root
):
    from hotfix_runtime_drill import run_drill

    receipt = run_drill(
        *source_repository,
        parent=short_root,
        scenarios=("failed_upgrade",),
        environment={},
    )
    scenario = receipt["scenarios"][0]
    assert scenario["actions"][-1]["returncode"] != 0
    assert "previous release restored and ready" in scenario["actions"][-1]["stderr"]
    assert (
        scenario["observations"][0]["database_digest"]
        == scenario["observations"][-1]["database_digest"]
    )
    assert scenario["observations"][-1]["readiness"]["service_version"] == "0.3.116"


@pytest.mark.parametrize("name", ["rollback", "rollback_forward"])
def test_explicit_rollback_directions_preserve_the_matching_schema_and_data(
    source_repository, short_root, name
):
    from hotfix_runtime_drill import run_drill

    receipt = run_drill(
        *source_repository, parent=short_root, scenarios=(name,), environment={}
    )
    observations = receipt["scenarios"][0]["observations"]
    assert observations[0]["database_digest"] == observations[2]["database_digest"]
    assert observations[2]["sentinels"] == ["before-upgrade"]
    if name == "rollback_forward":
        assert observations[1]["database_digest"] == observations[3]["database_digest"]
        assert observations[3]["sentinels"] == ["after-upgrade", "before-upgrade"]


def test_terminal_recovery_failure_is_retained_without_a_second_attempt(
    source_repository, short_root
):
    from hotfix_runtime_drill import run_drill

    receipt = run_drill(
        *source_repository,
        parent=short_root,
        scenarios=("recovery_failure",),
        environment={},
    )
    scenario = receipt["scenarios"][0]
    assert scenario["outcome"] == "blocked"
    assert len(scenario["actions"]) == 2
    assert "readiness was not restored" in scenario["actions"][-1]["stderr"]
    assert receipt["cleanup"]["remaining_processes"] == []


def test_full_report_replays_control_gates_and_rejects_relabelled_evidence(
    source_repository, short_root
):
    from hotfix_control import digest
    from hotfix_runtime_drill import SCENARIOS, DrillError, report, run_drill

    receipt = run_drill(
        *source_repository, parent=short_root, scenarios=SCENARIOS, environment={}
    )
    assert report(receipt)["done_eligible"] is True
    assert receipt["real_slot"] == {
        "state": "dormant",
        "resources": [],
        "live_authority": False,
    }
    assert receipt["git"]["cleanup"]["verified"] is True
    for history in receipt["controls"].values():
        states = [entry["state"] for entry in history]
        assert states[-1] == "closed"
        assert (
            states.index("staging_accepted")
            < states.index("deploy_authorized")
            < states.index("deployed")
        )
    for mutate in (
        lambda r: r.update(operational_authority=True),
        lambda r: r["artifacts"]["candidate"].update(commit="f" * 40),
        lambda r: r["scenarios"][1]["observations"][-1].update(
            database_digest="f" * 64
        ),
        lambda r: r["controls"]["upgrade"].pop(),
        lambda r: r["scenarios"][0]["observations"][-1]["readiness"].update(
            contract_sha256="f" * 64
        ),
    ):
        bad = copy.deepcopy(receipt)
        mutate(bad)
        bad["receipt_digest"] = digest(
            {k: v for k, v in bad.items() if k != "receipt_digest"}
        )
        with pytest.raises(DrillError):
            report(bad)


@pytest.mark.parametrize(
    "key", ["OPENAI_API_KEY", "LAST30DAYS_SYSTEMCTL", "PYTHONPATH", "BROWSER_PROFILE"]
)
def test_preflight_denies_ambient_credentials_and_manager_configuration(
    source_repository, key
):
    from hotfix_runtime_drill import DrillError, preflight

    with pytest.raises(DrillError, match="ambient_credentials_or_config"):
        preflight(*source_repository, environment={key: "fixture-denied"})


def test_preflight_denies_dirty_source_and_drill_denies_redirected_roots(
    source_repository, short_root
):
    from hotfix_runtime_drill import DrillError, preflight, run_drill

    source, *_ = source_repository
    dirt = source / "untracked-fixture"
    dirt.write_text("do not build")
    try:
        with pytest.raises(DrillError, match="dirty_source"):
            preflight(*source_repository, environment={})
    finally:
        dirt.unlink()
    link = short_root / "redirect"
    link.symlink_to(short_root, target_is_directory=True)
    with pytest.raises(DrillError, match="unsafe_path"):
        run_drill(*source_repository, parent=link, environment={})
    assert list(short_root.iterdir()) == [link]


@pytest.mark.parametrize("metadata", ["commondir", "objects/info/alternates"])
def test_preflight_rejects_external_git_metadata_before_git_runs(
    source_repository, tmp_path, metadata
):
    from hotfix_runtime_drill import DrillError, preflight

    root, *_ = source_repository
    redirect = root / ".git" / metadata
    redirect.write_text(str(tmp_path / "foreign.git") + "\n")
    try:
        with pytest.raises(DrillError, match="foreign_git_metadata"):
            preflight(*source_repository, environment={})
    finally:
        redirect.unlink()


def test_preflight_rejects_git_directory_pointer_files(tmp_path):
    from hotfix_runtime_drill import DrillError, preflight

    (tmp_path / ".git").write_text("gitdir: /foreign/repository\n")
    with pytest.raises(DrillError, match="standalone_source_clone_required"):
        preflight(tmp_path, "a" * 40, "b" * 40, environment={})


def _installer_python(raw=None):
    text = raw or (ROOT / "service/scripts/install.sh").read_text()
    source = text.split("<<'PY'\n", 1)[1].rsplit("\nPY", 1)[0]
    namespace = {"__name__": "installer_contract_test"}
    exec(compile(source, "installer-python", "exec"), namespace)  # noqa: S102 - fixed repo-owned embedded Python, import guard preserved
    return namespace


def test_installer_explicit_host_root_preserves_default_host_and_default_compatibility(
    tmp_path, monkeypatch
):
    namespace = _installer_python()
    default_root = tmp_path / "default-host"
    selected_root = tmp_path / "selected-host"
    release = tmp_path / "release"
    (release / "scripts").mkdir(parents=True)
    (release / "scripts/service.py").write_text("new entrypoint")
    for root in (default_root, selected_root):
        skill = root / ".agents/skills/last30days"
        (skill / "scripts").mkdir(parents=True)
        (skill / "SKILL.md").write_text("name: last30days\n")
        (skill / "scripts/service.py").write_text("old entrypoint")
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: default_root))
    namespace["refresh_skill_entrypoints"](release, selected_root)
    assert (
        selected_root / ".agents/skills/last30days/scripts/service.py"
    ).read_text() == "new entrypoint"
    assert (
        default_root / ".agents/skills/last30days/scripts/service.py"
    ).read_text() == "old entrypoint"
    namespace["refresh_skill_entrypoints"](release)
    assert (
        default_root / ".agents/skills/last30days/scripts/service.py"
    ).read_text() == "new entrypoint"


@pytest.mark.parametrize("kind", ["relative", "foreign_owner", "symlink", "shared"])
def test_installer_rejects_unsafe_explicit_host_root_before_creating_state(
    tmp_path, kind
):
    target = tmp_path / "selected"
    target.mkdir(mode=0o700)
    if kind == "relative":
        target = Path("relative")
    elif kind == "foreign_owner":
        target = Path("/")
    elif kind == "symlink":
        link = tmp_path / "redirect"
        link.symlink_to(target)
        target = link
    else:
        target.chmod(0o777)
    result = subprocess.run(
        [
            "bash",
            str(ROOT / "service/scripts/install.sh"),
            "diagnose",
            "--skill-host-root",
            str(target),
        ],
        env={"PATH": "/usr/bin:/bin", "LAST30DAYS_PYTHON": sys.executable},
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0
    assert (
        "--skill-host-root must be an absolute, owner-private directory"
        in result.stderr
    )
    assert not (tmp_path / "data").exists()


def test_operator_preflight_is_read_only_and_report_rejects_invalid_receipts(
    source_repository, tmp_path
):
    script = ROOT / "dev/last30days/scripts/hotfix_operator.py"
    source, commit, previous = source_repository
    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "preflight",
            "--source-root",
            str(source),
            "--source-commit",
            commit,
            "--previous-commit",
            previous,
        ],
        env={"PATH": "/usr/bin:/bin"},
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["sources"]["candidate"]["commit"] == commit
    invalid = tmp_path / "invalid.json"
    invalid.write_text("{}")
    result = subprocess.run(
        [sys.executable, str(script), "report", str(invalid)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 1
    assert json.loads(result.stdout)["status"] == "failed"
