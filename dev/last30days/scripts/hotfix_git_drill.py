"""Disposable, network-free Git proof for WI-007 Packets 1-2.

The factory accepts a directory under the OS temporary root, never an existing
repository. All repositories, refs, worktrees, hooks and Git configuration are
created inside a fresh owned child. No shell, host Git configuration, runtime,
provider, release or installed state is used.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import uuid
from pathlib import Path

from hotfix_control import (
    FeatureLaneV1,
    GitSnapshotV1,
    HotfixCandidateV1,
    HotfixCaseV1,
    HotfixController,
    HotfixError,
    HotfixIntegrationReceiptV1,
    HotfixReconciliationReportV1,
    LaneDispositionV1,
    digest,
)


def _no_symlinks(path: Path):
    if any(part.is_symlink() for part in (path, *path.parents)):
        raise HotfixError("unsafe_symlink")


class DisposableGitDrill:
    """Own one generated fixture, with exact readback before any mutation."""

    @classmethod
    def create(cls, parent: Path):
        parent = Path(parent)
        _no_symlinks(parent)
        temporary = Path(tempfile.gettempdir()).resolve()
        if (
            not parent.is_absolute()
            or not parent.is_dir()
            or parent.resolve() == temporary
            or not parent.resolve().is_relative_to(temporary)
            or any(
                (ancestor / ".git").exists() for ancestor in (parent, *parent.parents)
            )
        ):
            raise HotfixError("unsafe_fixture_parent")
        self = cls()
        self.root = Path(tempfile.mkdtemp(prefix="l30d-hotfix-", dir=parent))
        self._identity = (self.root.stat().st_dev, self.root.stat().st_ino)
        self._token = uuid.uuid4().hex
        (self.root / "owner.json").write_text(json.dumps({"token": self._token}))
        self.git_binary = shutil.which("git")
        if not self.git_binary:
            raise HotfixError("git_unavailable")
        self._worktrees: dict[str, Path] = {}
        self._branches: set[str] = set()
        self._closed = False
        self._integrated = False
        self._reconciled: set[str] = set()
        self._lanes: tuple[FeatureLaneV1, ...] | None = None
        self._config_hashes: dict[Path, str] = {}
        self._env = {
            "PATH": "/usr/bin:/bin",
            "LANG": "C",
            "LC_ALL": "C",
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_TERMINAL_PROMPT": "0",
            "GIT_ALLOW_PROTOCOL": "file",
            "GIT_AUTHOR_NAME": "Fixture",
            "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
            "GIT_COMMITTER_NAME": "Fixture",
            "GIT_COMMITTER_EMAIL": "fixture@example.invalid",
            "GIT_AUTHOR_DATE": "2026-09-14T00:00:00+00:00",
            "GIT_COMMITTER_DATE": "2026-09-14T00:00:00+00:00",
        }
        (self.root / "empty-hooks").mkdir()
        (self.root / "empty-template").mkdir()
        self.main = self.root / "main"
        self.origin = self.root / "origin.git"
        self.main.mkdir()
        self.origin.mkdir()
        self._git(
            self.origin,
            "init",
            "--bare",
            "--initial-branch=main",
            f"--template={self.root / 'empty-template'}",
        )
        self._git(
            self.main,
            "init",
            "--initial-branch=main",
            f"--template={self.root / 'empty-template'}",
        )
        self._git(self.main, "remote", "add", "origin", str(self.origin))
        (self.main / "app.py").write_text(
            'VALUE = "broken"\n' + "\n" * 20 + "FEATURE = False\n"
        )
        (self.main / "notes.txt").write_text("fixture notes\n")
        self._git(self.main, "add", "app.py", "notes.txt")
        self._git(self.main, "commit", "-m", "fixture baseline")
        self._git(self.main, "push", "origin", "main")
        self.base = self._git(self.main, "rev-parse", "HEAD")
        return self

    def _owned(self):
        if self._closed:
            raise HotfixError("fixture_closed")
        _no_symlinks(self.root)
        if (self.root.stat().st_dev, self.root.stat().st_ino) != self._identity:
            raise HotfixError("fixture_identity_changed")
        marker = self.root / "owner.json"
        if marker.is_symlink() or json.loads(marker.read_text()) != {
            "token": self._token
        }:
            raise HotfixError("fixture_owner_changed")
        if any(path.is_symlink() for path in self.root.rglob("*")):
            raise HotfixError("unsafe_symlink")
        if any((self.root / "empty-hooks").iterdir()):
            raise HotfixError("hooks_changed")
        # These are the fixture's fixed common metadata roots. A top-level
        # commondir is never created by the drill and could redirect refs,
        # objects, worktree records, or receive-pack writes elsewhere before a
        # later linked-worktree check observes the changed layout.
        for metadata_root in (self.main / ".git", self.origin):
            common = metadata_root / "commondir"
            if common.exists() or common.is_symlink():
                raise HotfixError("foreign_git_directory")
        metadata_root = self.root / "main" / ".git" / "worktrees"
        if metadata_root.is_dir():
            for metadata in metadata_root.iterdir():
                common = metadata / "commondir"
                backlink = metadata / "gitdir"
                if (
                    not common.is_file()
                    or common.read_text().strip() != "../.."
                    or not backlink.is_file()
                    or Path(backlink.read_text().strip())
                    not in {path / ".git" for path in self._worktrees.values()}
                ):
                    raise HotfixError("foreign_git_directory")
        for config, expected in self._config_hashes.items():
            if not config.is_file() or digest(config.read_text()) != expected:
                raise HotfixError("configuration_changed")

    def _git(self, cwd: Path, *args: str, allowed=(0,)):
        self._owned()
        if cwd not in {self.main, self.origin, *self._worktrees.values()}:
            raise HotfixError("foreign_git_target")
        _no_symlinks(cwd)
        if not cwd.resolve().is_relative_to(self.root):
            raise HotfixError("foreign_git_target")
        # Linked-worktree metadata may only point at this fixture's main Git dir.
        dotgit = cwd / ".git"
        if dotgit.is_symlink():
            raise HotfixError("foreign_git_directory")
        if dotgit.is_file():
            pointer = dotgit.read_text().strip()
            if not pointer.startswith("gitdir: "):
                raise HotfixError("foreign_git_directory")
            target = Path(pointer[8:])
            _no_symlinks(target)
            if not target.resolve().is_relative_to(self.main / ".git" / "worktrees"):
                raise HotfixError("foreign_git_directory")
        result = subprocess.run(
            [
                self.git_binary,
                "-c",
                f"core.hooksPath={self.root / 'empty-hooks'}",
                "-c",
                "commit.gpgSign=false",
                "-c",
                "tag.gpgSign=false",
                "-c",
                "protocol.allow=never",
                "-c",
                "protocol.file.allow=always",
                *args,
            ],
            cwd=cwd,
            env=self._env,
            text=True,
            capture_output=True,
            check=False,
            timeout=10,
        )
        if result.returncode not in allowed:
            raise HotfixError(
                f"git_failed:{args[0]}:{result.returncode}:{result.stderr.strip()}"
            )
        for config in (self.main / ".git" / "config", self.origin / "config"):
            if config.exists():
                self._config_hashes[config] = digest(config.read_text())
        return result.stdout.strip()

    def _worktree(self, branch: str):
        path = self.root / branch.replace("/", "-")
        if branch in self._branches or path.exists():
            raise HotfixError("duplicate_fixture_branch")
        self._git(self.main, "worktree", "add", "-b", branch, str(path), self.base)
        self._worktrees[branch] = path
        self._branches.add(branch)
        return path

    def _head(self, path):
        return self._git(path, "rev-parse", "HEAD")

    def _feature(self, name):
        path = self._worktree(f"feature/{name}")
        if name == "unaffected":
            (path / "notes.txt").write_text("fixture independent update\n")
            surfaces = ("notes.txt",)
        else:
            content = (path / "app.py").read_text()
            if name == "reconciled":
                content = content.replace("FEATURE = False", "FEATURE = True")
            else:
                content = content.replace('"broken"', f'"feature-{name}"')
            (path / "app.py").write_text(content)
            surfaces = ("app.py",)
        self._git(path, "add", "--all")
        self._git(path, "commit", "-m", f"fixture feature {name}")
        self._git(path, "push", "origin", f"feature/{name}")
        head = self._head(path)
        return FeatureLaneV1(
            lane=name,
            head_commit=head,
            remote_commit=head,
            surfaces=surfaces,
            status=name if name in {"superseded", "cancelled"} else "active",
        )

    def prepare(self):
        """Create the fixed conflict matrix once; return current Git evidence."""
        if self._lanes is None:
            self._lanes = tuple(
                self._feature(name)
                for name in (
                    "unaffected",
                    "reconciled",
                    "paused",
                    "superseded",
                    "cancelled",
                )
            )
        return GitSnapshotV1(
            main_commit=self._head(self.main),
            remote_commit=self._git(self.origin, "rev-parse", "refs/heads/main"),
            clean=not bool(self._git(self.main, "status", "--porcelain")),
            lanes=tuple(
                FeatureLaneV1(
                    lane=lane.lane,
                    head_commit=self._head(self._worktrees[f"feature/{lane.lane}"]),
                    remote_commit=self._git(
                        self.origin, "rev-parse", f"refs/heads/feature/{lane.lane}"
                    ),
                    surfaces=lane.surfaces,
                    status=lane.status,
                )
                for lane in self._lanes
            ),
        )

    def integrate_feature(self, name):
        """Conflicting features cannot jump the priority/reconciliation gate."""
        if name != "unaffected" and (
            not self._integrated or name not in self._reconciled
        ):
            raise HotfixError("affected_feature_requires_hotfix_reconciliation")
        if f"feature/{name}" not in self._branches:
            raise HotfixError("unknown_feature")
        self._git(self.main, "merge", "--no-ff", "--no-edit", f"feature/{name}")

    def run(self):
        snapshot = self.prepare()
        lanes = snapshot.lanes
        case = HotfixCaseV1(
            work_item="WI-007",
            incident="fixture-incident",
            reporter="fixture-operator",
            observed_at="2026-09-14T00:00:00+00:00",
            expected="VALUE is correct",
            observed="VALUE is broken",
            evidence="fixture://app.py/before",
            production_identity="fixture-service/v1",
            impact="incorrect",
            surfaces=("app.py",),
            overlaps=tuple(lane.lane for lane in lanes if lane.lane != "unaffected"),
            containment="effects disabled",
            rollback_commit=self.base,
            rollback_evidence="fixture://base-tree",
            non_goals="No live effects",
            stop_conditions="Any unowned effect",
        )
        controller = HotfixController()
        controller.report(case)
        controller.qualify()
        remote = snapshot.remote_commit
        controller.activate(snapshot)
        if snapshot.main_commit != self.base:
            raise HotfixError("stale_fixture_base")
        try:
            self.integrate_feature("reconciled")
        except HotfixError as error:
            if str(error) != "affected_feature_requires_hotfix_reconciliation":
                raise
        else:
            raise HotfixError("priority_gate_failed")
        hotfix = self._worktree("hotfix/WI-007-fixture")
        if self._head(hotfix) != remote:
            raise HotfixError("hotfix_base_mismatch")
        source = hotfix / "app.py"
        if source.read_text().splitlines()[0] != 'VALUE = "broken"':
            raise HotfixError("regression_not_reproduced")
        source.write_text(
            source.read_text().replace('VALUE = "broken"', 'VALUE = "correct"')
        )
        self._git(hotfix, "add", "app.py")
        self._git(hotfix, "commit", "-m", "fixture WI-007 correction")
        head = self._head(hotfix)
        self._git(hotfix, "push", "origin", "hotfix/WI-007-fixture")
        candidate = HotfixCandidateV1(
            case_digest=digest(case),
            base_commit=self.base,
            head_commit=head,
            changed_files=tuple(
                self._git(hotfix, "diff", "--name-only", self.base, head).splitlines()
            ),
            regression_before="fixture://VALUE-broken",
            regression_after="fixture://VALUE-correct",
            focused_tests=("fixture-value-check",),
            fallback_tests=("fixture-tree-check",),
            compatibility="fixture schema unchanged",
            rollback_commit=self.base,
            review="fixture://priority-review",
            blocking_findings=(),
        )
        controller.candidate(candidate)
        if source.read_text().splitlines()[0] != 'VALUE = "correct"':
            raise HotfixError("regression_persists")
        if (
            self._head(self.main) != self.base
            or self._git(self.origin, "rev-parse", "refs/heads/main") != self.base
            or self._git(self.origin, "rev-parse", "refs/heads/hotfix/WI-007-fixture")
            != head
        ):
            raise HotfixError("integration_custody_changed")
        self._git(self.main, "merge", "--no-ff", "--no-edit", "hotfix/WI-007-fixture")
        merge = self._head(self.main)
        self._git(self.main, "merge-base", "--is-ancestor", head, merge)
        self._git(self.main, "push", "origin", "main")
        integration = HotfixIntegrationReceiptV1(
            candidate_digest=digest(candidate),
            base_commit=self.base,
            head_commit=head,
            merge_commit=merge,
            target_commit=self._git(self.origin, "rev-parse", "refs/heads/main"),
            priority_review="fixture://priority-review",
            ancestry_verified=True,
        )
        controller.integrate(integration)
        self._integrated = True
        dispositions = []
        for lane in lanes:
            path = self._worktrees[f"feature/{lane.lane}"]
            if lane.lane == "reconciled":
                self._git(path, "merge", "--no-ff", "--no-edit", merge)
                self._git(path, "merge-base", "--is-ancestor", merge, "HEAD")
                contents = (path / "app.py").read_text()
                if (
                    'VALUE = "correct"' not in contents
                    or "FEATURE = True" not in contents
                ):
                    raise HotfixError("feature_regression")
                self._git(path, "push", "origin", f"feature/{lane.lane}")
                self._reconciled.add(lane.lane)
            elif lane.lane == "paused":
                self._git(path, "merge", "--no-ff", "--no-edit", merge, allowed=(1,))
                if not self._git(path, "diff", "--name-only", "--diff-filter=U"):
                    raise HotfixError("expected_conflict_missing")
                self._git(path, "merge", "--abort")
            dispositions.append(
                LaneDispositionV1(
                    lane=lane.lane,
                    disposition=lane.lane,
                    old_commit=lane.head_commit,
                    new_commit=self._head(path),
                    integrated_commit=merge,
                    validation=f"fixture://{lane.lane}-disposition",
                )
            )
        reconciliation = HotfixReconciliationReportV1(
            merge_commit=merge, lanes=tuple(dispositions)
        )
        controller.reconcile(reconciliation)
        self.receipt = {
            "schema_version": 1,
            "mode": "drill",
            "work_item": "WI-007",
            "status": "passed",
            "fixture_root": str(self.root),
            "base_commit": self.base,
            "activation_remote_commit": remote,
            "final_main_commit": self._head(self.main),
            "priority_gate": "affected_feature_blocked_before_hotfix",
            "integration": integration.to_dict(),
            "reconciliation": reconciliation.to_dict(),
            "history": controller.history,
            "effects": {"network": False, "runtime": False, "provider": False},
        }
        return self.receipt

    def cleanup(self):
        self._owned()
        # Check the complete cleanup set first; a dirty or foreign member blocks
        # every deletion, preserving all evidence for diagnosis.
        expected = {str(self.main), *(str(path) for path in self._worktrees.values())}
        inventory = self._git(self.main, "worktree", "list", "--porcelain")
        actual = {
            line[9:] for line in inventory.splitlines() if line.startswith("worktree ")
        }
        if actual != expected:
            raise HotfixError("cleanup_worktree_inventory_mismatch")
        for path in (self.main, *self._worktrees.values()):
            if self._git(path, "status", "--porcelain", "--untracked-files=all"):
                raise HotfixError("cleanup_dirty_worktree")
        # Reject symlinks anywhere, including Git metadata, before recursive removal.
        if any(path.is_symlink() for path in self.root.rglob("*")):
            raise HotfixError("cleanup_symlink")
        checkpoints = {
            branch: self._head(path) for branch, path in self._worktrees.items()
        }
        for path in self._worktrees.values():
            self._git(self.main, "worktree", "remove", str(path))
        final_inventory = self._git(self.main, "worktree", "list", "--porcelain")
        if {
            line[9:]
            for line in final_inventory.splitlines()
            if line.startswith("worktree ")
        } != {str(self.main)}:
            raise HotfixError("cleanup_residual_worktree")
        root = str(self.root)
        self._owned()
        shutil.rmtree(self.root)
        self._closed = True
        if Path(root).exists():
            raise HotfixError("cleanup_residual_root")
        return {
            "verified": True,
            "root": root,
            "branch_checkpoints": checkpoints,
            "remaining_worktrees": [],
            "remaining_refs": [],
        }


def run_git_drill(parent: Path) -> dict:
    fixture = DisposableGitDrill.create(parent)
    receipt = fixture.run()
    receipt["cleanup"] = fixture.cleanup()
    return receipt
