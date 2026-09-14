"""Real local Git proof, confined to disposable roots and local remotes."""

import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "dev/last30days/scripts"))

from hotfix_control import HotfixError
from hotfix_git_drill import DisposableGitDrill, run_git_drill


def test_disposable_git_drill_proves_priority_reconciliation_and_exact_cleanup(
    tmp_path,
):
    sibling = tmp_path / "unrelated"
    sibling.mkdir()
    (sibling / "keep.txt").write_text("preserve")
    receipt = run_git_drill(tmp_path)
    assert receipt["status"] == "passed"
    assert receipt["base_commit"] == receipt["activation_remote_commit"]
    assert receipt["integration"]["merge_commit"] == receipt["final_main_commit"]
    assert receipt["priority_gate"] == "affected_feature_blocked_before_hotfix"
    assert {lane["disposition"] for lane in receipt["reconciliation"]["lanes"]} == {
        "unaffected",
        "reconciled",
        "paused",
        "superseded",
        "cancelled",
    }
    assert receipt["cleanup"]["verified"] is True
    assert not Path(receipt["fixture_root"]).exists()
    assert list(tmp_path.iterdir()) == [sibling]
    assert (sibling / "keep.txt").read_text() == "preserve"
    assert receipt["effects"] == {"network": False, "runtime": False, "provider": False}


def test_diverged_feature_fails_before_hotfix_creation_and_preserves_checkpoint(
    tmp_path,
):
    fixture = DisposableGitDrill.create(tmp_path)
    fixture.prepare()
    feature = fixture.root / "feature-reconciled"
    old = subprocess.check_output(
        ["git", "-C", str(feature), "rev-parse", "HEAD"], text=True
    ).strip()
    subprocess.run(
        [
            "git",
            "-C",
            str(feature),
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "-c",
            "commit.gpgsign=false",
            "commit",
            "--allow-empty",
            "-m",
            "unpublished fixture change",
        ],
        check=True,
        capture_output=True,
    )
    with pytest.raises(HotfixError, match="diverged_lane"):
        fixture.run()
    assert not (fixture.root / "hotfix-WI-007-fixture").exists()
    cleanup = fixture.cleanup()
    assert cleanup["branch_checkpoints"]["feature/reconciled"] != old
    assert cleanup["verified"]


def test_dirty_cleanup_retains_entire_fixture_until_exact_dirt_is_resolved(tmp_path):
    fixture = DisposableGitDrill.create(tmp_path)
    receipt = fixture.run()
    dirt = fixture.root / "feature-paused" / "keep.txt"
    dirt.write_text("uncommitted evidence")
    with pytest.raises(HotfixError, match="cleanup_dirty_worktree"):
        fixture.cleanup()
    assert dirt.read_text() == "uncommitted evidence"
    assert (fixture.root / "hotfix-WI-007-fixture").is_dir()
    assert receipt["integration"]["merge_commit"] == receipt["final_main_commit"]
    dirt.unlink()  # Exact test-owned fault, then explicit cleanup reconciliation.
    assert fixture.cleanup()["verified"]


@pytest.mark.parametrize("fault", ["symlink", "remote", "hooks", "owner"])
def test_tampered_fixture_cannot_redirect_git_or_cleanup_outside_its_root(
    tmp_path, fault
):
    fixture = DisposableGitDrill.create(tmp_path)
    foreign = tmp_path / "foreign"
    foreign.mkdir()
    sentinel = foreign / "keep"
    sentinel.write_text("preserve")
    if fault == "symlink":
        target = fixture.root / "main" / ".git" / "objects" / "outside"
        target.symlink_to(foreign, target_is_directory=True)
    elif fault == "remote":
        target = fixture.root / "main" / ".git" / "config"
        original = target.read_text()
        target.write_text(original.replace(str(fixture.origin), str(foreign)))
    elif fault == "hooks":
        target = fixture.root / "empty-hooks" / "pre-commit"
        target.write_text("#!/bin/sh\nexit 77\n")
        target.chmod(0o700)
    else:
        target = fixture.root / "owner.json"
        original = target.read_text()
        target.write_text('{"token": "foreign"}')
    with pytest.raises(
        HotfixError,
        match="unsafe_symlink|configuration_changed|hooks_changed|fixture_owner_changed",
    ):
        fixture.prepare()
    assert not (fixture.root / "feature-unaffected").exists()
    assert sentinel.read_text() == "preserve"
    if fault in {"owner", "remote"}:
        target.write_text(original)
    else:
        target.unlink()
    assert fixture.cleanup()["verified"]


def test_factory_rejects_non_temporary_and_symlinked_parents(tmp_path):
    with pytest.raises(HotfixError, match="unsafe_fixture_parent"):
        DisposableGitDrill.create(Path(__file__).resolve().parents[1])
    link = tmp_path / "link"
    link.symlink_to(tmp_path, target_is_directory=True)
    with pytest.raises(HotfixError, match="unsafe_symlink"):
        DisposableGitDrill.create(link)


def test_linked_git_metadata_cannot_redirect_commands_to_a_foreign_repository(tmp_path):
    fixture = DisposableGitDrill.create(tmp_path)
    fixture.prepare()
    metadata = fixture.root / "main/.git/worktrees/feature-unaffected/commondir"
    original = metadata.read_text()
    metadata.write_text(str(tmp_path / "outside.git"))
    with pytest.raises(HotfixError, match="foreign_git_directory"):
        fixture.run()
    metadata.write_text(original)
    assert fixture.cleanup()["verified"]
