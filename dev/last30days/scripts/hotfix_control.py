"""WI-007 provider-free control plane. Records are evidence, never effect authority.

No adapter here performs I/O. Only the separate disposable Git drill owns Git
effects. Runtime/release/production adapters deliberately do not exist.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass, fields
from datetime import datetime
from pathlib import PurePosixPath
from typing import Literal, get_args, get_origin, get_type_hints


class HotfixError(ValueError):
    """Invalid evidence or transition; the previous state remains intact."""


def digest(value: object) -> str:
    if isinstance(value, Record):
        value = value.to_dict()
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _valid_type(value: object, annotation: object) -> bool:
    origin = get_origin(annotation)
    if origin is Literal:
        return any(
            type(value) is type(choice) and value == choice
            for choice in get_args(annotation)
        )
    if origin is tuple:
        return type(value) is tuple and all(
            _valid_type(item, get_args(annotation)[0]) for item in value
        )
    return type(value) is annotation


def _paths(values: tuple[str, ...]):
    if not values or len(set(values)) != len(values):
        raise HotfixError("invalid_surfaces")
    for value in values:
        path = PurePosixPath(value)
        if (
            not value
            or path.is_absolute()
            or ".." in path.parts
            or ".git" in path.parts
            or "\\" in value
            or str(path) != value
            or value == "."
        ):
            raise HotfixError("invalid_surface")


@dataclass(frozen=True, kw_only=True)
class Record:
    schema_version: Literal[1] = 1
    mode: Literal["drill"] = "drill"

    def __post_init__(self) -> None:
        for name, annotation in get_type_hints(type(self)).items():
            value = getattr(self, name)
            if not _valid_type(value, annotation):
                raise HotfixError(f"invalid_type:{name}")
            strings = (
                (value,)
                if isinstance(value, str)
                else value
                if isinstance(value, tuple)
                else ()
            )
            if any(
                isinstance(item, str) and (not item.strip() or item != item.strip())
                for item in strings
            ):
                raise HotfixError(f"invalid_text:{name}")
            if name.endswith("_commit") and not re.fullmatch(r"[0-9a-f]{40}", value):
                raise HotfixError(f"invalid_commit:{name}")
            if name.endswith("_digest") and not re.fullmatch(r"[0-9a-f]{64}", value):
                raise HotfixError(f"invalid_digest:{name}")

    def to_dict(self) -> dict:
        return json.loads(json.dumps(asdict(self)))

    @classmethod
    def from_dict(cls, payload: dict):
        if type(payload) is not dict or set(payload) != {
            field.name for field in fields(cls)
        }:
            raise HotfixError("record_fields_mismatch")
        data = dict(payload)
        for name, annotation in get_type_hints(cls).items():
            if get_origin(annotation) is tuple and type(data[name]) is list:
                element = get_args(annotation)[0]
                data[name] = tuple(
                    element.from_dict(item)
                    if isinstance(element, type) and issubclass(element, Record)
                    else item
                    for item in data[name]
                )
        return cls(**data)


@dataclass(frozen=True, kw_only=True)
class HotfixCaseV1(Record):
    work_item: str
    incident: str
    reporter: str
    observed_at: str
    expected: str
    observed: str
    evidence: str
    production_identity: str
    impact: Literal["incorrect", "unsafe", "unavailable", "unverified"]
    surfaces: tuple[str, ...]
    overlaps: tuple[str, ...]
    containment: str
    rollback_commit: str
    rollback_evidence: str
    non_goals: str
    stop_conditions: str

    def __post_init__(self):
        super().__post_init__()
        _paths(self.surfaces)
        if len(set(self.overlaps)) != len(self.overlaps) or any(
            not item.strip() for item in self.overlaps
        ):
            raise HotfixError("invalid_overlaps")
        if not re.fullmatch(r"WI-[0-9]+", self.work_item):
            raise HotfixError("invalid_work_item")
        try:
            if datetime.fromisoformat(self.observed_at).tzinfo is None:
                raise ValueError
        except ValueError as error:
            raise HotfixError("invalid_observed_at") from error


@dataclass(frozen=True, kw_only=True)
class FeatureLaneV1(Record):
    lane: str
    head_commit: str
    remote_commit: str
    surfaces: tuple[str, ...]
    status: Literal["active", "paused", "superseded", "cancelled"] = "active"

    def __post_init__(self):
        super().__post_init__()
        _paths(self.surfaces)


@dataclass(frozen=True, kw_only=True)
class GitSnapshotV1(Record):
    main_commit: str
    remote_commit: str
    clean: bool
    lanes: tuple[FeatureLaneV1, ...] = ()
    active_hotfixes: int = 0


@dataclass(frozen=True, kw_only=True)
class HotfixCandidateV1(Record):
    case_digest: str
    base_commit: str
    head_commit: str
    changed_files: tuple[str, ...]
    regression_before: str
    regression_after: str
    focused_tests: tuple[str, ...]
    fallback_tests: tuple[str, ...]
    compatibility: str
    rollback_commit: str
    review: str
    blocking_findings: tuple[str, ...]

    def __post_init__(self):
        super().__post_init__()
        _paths(self.changed_files)
        if not self.focused_tests or not self.fallback_tests:
            raise HotfixError("missing_validation")


@dataclass(frozen=True, kw_only=True)
class HotfixIntegrationReceiptV1(Record):
    candidate_digest: str
    base_commit: str
    head_commit: str
    merge_commit: str
    target_commit: str
    priority_review: str
    ancestry_verified: bool


@dataclass(frozen=True, kw_only=True)
class LaneDispositionV1(Record):
    lane: str
    disposition: Literal[
        "unaffected", "reconciled", "paused", "superseded", "cancelled"
    ]
    old_commit: str
    new_commit: str
    integrated_commit: str
    validation: str


@dataclass(frozen=True, kw_only=True)
class HotfixReconciliationReportV1(Record):
    merge_commit: str
    lanes: tuple[LaneDispositionV1, ...]


@dataclass(frozen=True, kw_only=True)
class HotfixStagingReceiptV1(Record):
    integrated_commit: str
    artifact_digest: str
    manifest_digest: str
    identity: str
    validation: str
    rollback_verified: bool
    effects_disabled: bool


@dataclass(frozen=True, kw_only=True)
class HotfixDeploymentAuthorizationV1(Record):
    integrated_commit: str
    artifact_digest: str
    target: str
    operator: str
    rollback_commit: str
    attempt_limit: Literal[1]
    window: str
    stop_conditions: str


@dataclass(frozen=True, kw_only=True)
class HotfixDeploymentReceiptV1(Record):
    integrated_commit: str
    artifact_digest: str
    target: str
    attempt: Literal[1]
    evidence: str


@dataclass(frozen=True, kw_only=True)
class HotfixVerificationReceiptV1(Record):
    integrated_commit: str
    artifact_digest: str
    target: str
    ready: bool
    integrity_verified: bool
    regression_fixed: bool
    effects_disabled: bool
    evidence: str


@dataclass(frozen=True, kw_only=True)
class HotfixRollbackReceiptV1(Record):
    integrated_commit: str
    rollback_commit: str
    target: str
    attempt: Literal[1]
    ready: bool
    integrity_verified: bool
    effects_disabled: bool
    evidence: str


@dataclass(frozen=True, kw_only=True)
class HotfixCloseoutReceiptV1(Record):
    case_digest: str
    outcome: Literal["fixed", "rolled_back", "cancelled", "blocked"]
    cleanup_verified: bool
    evidence: str
    residual_risks: str


def _overlap(left, right):
    return any(
        a == b or a.startswith(b + "/") or b.startswith(a + "/")
        for a in left
        for b in right
    )


class FakeGitAdapter:
    """Frozen custody evidence for control-plane tests, without Git effects."""

    def __init__(self, snapshot: GitSnapshotV1):
        if type(snapshot) is not GitSnapshotV1:
            raise HotfixError("invalid_snapshot")
        self._snapshot = snapshot

    def snapshot(self):
        return self._snapshot


class FakeReviewAdapter:
    """Turn a synthetic regression verdict into an explicitly drill-only review."""

    def candidate(
        self,
        case: HotfixCaseV1,
        snapshot: GitSnapshotV1,
        *,
        head_commit: str,
        changed_files: tuple[str, ...],
        regression_passed: bool,
    ):
        if regression_passed is not True:
            raise HotfixError("regression_failed")
        return HotfixCandidateV1(
            case_digest=digest(case),
            base_commit=snapshot.main_commit,
            head_commit=head_commit,
            changed_files=changed_files,
            regression_before="fixture://regression-before",
            regression_after="fixture://regression-after",
            focused_tests=("fixture-regression",),
            fallback_tests=("fixture-contracts",),
            compatibility="fixture compatibility only",
            rollback_commit=case.rollback_commit,
            review="fixture://review",
            blocking_findings=(),
        )


class FakeRuntimeAdapter:
    """Generate synthetic drill evidence only; never build, install, or spawn."""

    def __init__(self, *, integrated_commit: str, rollback_commit: str):
        self.commit = integrated_commit
        self.rollback_commit = rollback_commit
        self.artifact = digest({"fixture_commit": integrated_commit})

    def staging(self):
        return HotfixStagingReceiptV1(
            integrated_commit=self.commit,
            artifact_digest=self.artifact,
            manifest_digest=digest("fixture-manifest"),
            identity="fixture-staging",
            validation="fixture://staging",
            rollback_verified=True,
            effects_disabled=True,
        )

    def authorization(self):
        return HotfixDeploymentAuthorizationV1(
            integrated_commit=self.commit,
            artifact_digest=self.artifact,
            target="fixture-production",
            operator="fixture-operator",
            rollback_commit=self.rollback_commit,
            attempt_limit=1,
            window="fixture-window",
            stop_conditions="fixture failure",
        )

    def deployment(self):
        return HotfixDeploymentReceiptV1(
            integrated_commit=self.commit,
            artifact_digest=self.artifact,
            target="fixture-production",
            attempt=1,
            evidence="fixture://deployment",
        )

    def verification(self):
        return HotfixVerificationReceiptV1(
            integrated_commit=self.commit,
            artifact_digest=self.artifact,
            target="fixture-production",
            ready=True,
            integrity_verified=True,
            regression_fixed=True,
            effects_disabled=True,
            evidence="fixture://verification",
        )

    def rollback(self):
        return HotfixRollbackReceiptV1(
            integrated_commit=self.commit,
            rollback_commit=self.rollback_commit,
            target="fixture-production",
            attempt=1,
            ready=True,
            integrity_verified=True,
            effects_disabled=True,
            evidence="fixture://rollback",
        )


class HotfixController:
    """One in-memory reserved slot; every transition validates before recording."""

    def __init__(self):
        self._state = "dormant"
        self._history: list[dict] = []
        self._case: HotfixCaseV1 | None = None
        self._base_commit: str | None = None
        self._lanes: tuple[FeatureLaneV1, ...] = ()
        self._conflicts: dict[str, str] = {}
        self._candidate: HotfixCandidateV1 | None = None
        self._integration: HotfixIntegrationReceiptV1 | None = None
        self._reconciliation: HotfixReconciliationReportV1 | None = None
        self._staging: HotfixStagingReceiptV1 | None = None
        self._authorization: HotfixDeploymentAuthorizationV1 | None = None

    @property
    def state(self):
        return self._state

    @property
    def history(self):
        return tuple(json.loads(json.dumps(self._history)))

    @property
    def resources(self):
        return ()

    @property
    def live_authority(self):
        return False

    @property
    def base_commit(self):
        return self._base_commit

    @property
    def conflicts(self):
        return dict(self._conflicts)

    @property
    def feature_wip(self):
        return sum(lane.status == "active" for lane in self._lanes)

    def _require(self, *states):
        if self.state not in states:
            raise HotfixError(f"transition_denied:{self.state}")

    def _record(self, state, evidence):
        entry = {
            "sequence": len(self._history) + 1,
            "previous_digest": digest(self._history[-1]) if self._history else None,
            "state": state,
            "evidence": evidence.to_dict()
            if isinstance(evidence, Record)
            else evidence,
        }
        self._history.append(entry)
        self._state = state

    def report(self, case: HotfixCaseV1):
        self._require("dormant")
        if type(case) is not HotfixCaseV1:
            raise HotfixError("invalid_case")
        self._case = case
        self._record("reported", case)

    def qualify(self):
        self._require("reported")
        if (
            self._case.impact == "unverified"
            or self._case.expected == self._case.observed
        ):
            raise HotfixError("ambiguous_case")
        self._record("qualified", {"case_digest": digest(self._case)})

    def activate(self, snapshot: GitSnapshotV1):
        self._require("qualified")
        if type(snapshot) is not GitSnapshotV1:
            raise HotfixError("invalid_snapshot")
        if snapshot.main_commit != snapshot.remote_commit:
            raise HotfixError("stale_base")
        if not snapshot.clean:
            raise HotfixError("dirty_main")
        if snapshot.active_hotfixes != 0:
            raise HotfixError("hotfix_slot_occupied")
        if sum(lane.status == "active" for lane in snapshot.lanes) > 3:
            raise HotfixError("feature_wip_exceeded")
        names = [lane.lane for lane in snapshot.lanes]
        if len(set(names)) != len(names):
            raise HotfixError("duplicate_lane")
        if any(lane.head_commit != lane.remote_commit for lane in snapshot.lanes):
            raise HotfixError("diverged_lane")
        conflicts = {
            lane.lane: "paused"
            if _overlap(self._case.surfaces, lane.surfaces)
            else "unaffected"
            for lane in snapshot.lanes
        }
        if set(self._case.overlaps) != {
            name for name, state in conflicts.items() if state == "paused"
        }:
            raise HotfixError("unregistered_overlap")
        self._lanes = snapshot.lanes
        self._conflicts = conflicts
        self._base_commit = snapshot.main_commit
        self._record("active", snapshot)

    def candidate(self, receipt: HotfixCandidateV1):
        self._require("active")
        if type(receipt) is not HotfixCandidateV1:
            raise HotfixError("invalid_candidate")
        if (
            receipt.case_digest != digest(self._case)
            or receipt.base_commit != self.base_commit
            or receipt.rollback_commit != self._case.rollback_commit
            or receipt.head_commit == receipt.base_commit
            or receipt.blocking_findings
            or not set(receipt.changed_files).issubset(self._case.surfaces)
        ):
            raise HotfixError("candidate_mismatch")
        self._candidate = receipt
        self._record("fix_ready", receipt)

    def integrate(self, receipt: HotfixIntegrationReceiptV1):
        self._require("fix_ready")
        if type(receipt) is not HotfixIntegrationReceiptV1:
            raise HotfixError("invalid_integration")
        if (
            receipt.candidate_digest != digest(self._candidate)
            or receipt.base_commit != self.base_commit
            or receipt.head_commit != self._candidate.head_commit
            or receipt.target_commit != receipt.merge_commit
            or not receipt.ancestry_verified
        ):
            raise HotfixError("integration_mismatch")
        self._integration = receipt
        self._record("integrated", receipt)

    def reconcile(self, receipt: HotfixReconciliationReportV1):
        self._require("integrated")
        if type(receipt) is not HotfixReconciliationReportV1:
            raise HotfixError("invalid_reconciliation")
        original = {lane.lane: lane for lane in self._lanes}
        if (
            receipt.merge_commit != self._integration.merge_commit
            or len(receipt.lanes) != len(original)
            or {lane.lane for lane in receipt.lanes} != set(original)
        ):
            raise HotfixError("reconciliation_incomplete")
        for lane in receipt.lanes:
            if (
                lane.old_commit != original[lane.lane].head_commit
                or lane.integrated_commit != receipt.merge_commit
            ):
                raise HotfixError("reconciliation_identity_mismatch")
            if (
                lane.disposition == "unaffected"
                and self._conflicts[lane.lane] != "unaffected"
            ):
                raise HotfixError("affected_lane_unreconciled")
            if lane.disposition == "reconciled" and lane.new_commit == lane.old_commit:
                raise HotfixError("reconciliation_missing_advance")
        self._reconciliation = receipt
        self._record("integrated", receipt)

    def stage(self, receipt: HotfixStagingReceiptV1):
        self._require("integrated")
        if type(receipt) is not HotfixStagingReceiptV1 or self._reconciliation is None:
            raise HotfixError("missing_reconciliation_or_staging")
        if (
            receipt.integrated_commit != self._integration.merge_commit
            or not receipt.rollback_verified
            or not receipt.effects_disabled
        ):
            raise HotfixError("staging_mismatch")
        self._staging = receipt
        self._record("staging_accepted", receipt)

    def authorize(self, receipt: HotfixDeploymentAuthorizationV1):
        self._require("staging_accepted")
        if type(receipt) is not HotfixDeploymentAuthorizationV1:
            raise HotfixError("invalid_authorization")
        if (
            receipt.integrated_commit != self._staging.integrated_commit
            or receipt.artifact_digest != self._staging.artifact_digest
            or receipt.rollback_commit != self._case.rollback_commit
        ):
            raise HotfixError("authorization_mismatch")
        self._authorization = receipt
        self._record("deploy_authorized", receipt)

    def _deployment_matches(self, receipt):
        return (
            receipt.integrated_commit == self._authorization.integrated_commit
            and receipt.artifact_digest == self._authorization.artifact_digest
            and receipt.target == self._authorization.target
        )

    def deploy(self, receipt: HotfixDeploymentReceiptV1):
        self._require("deploy_authorized")
        if type(
            receipt
        ) is not HotfixDeploymentReceiptV1 or not self._deployment_matches(receipt):
            raise HotfixError("deployment_mismatch")
        self._record("deployed", receipt)

    def verify(self, receipt: HotfixVerificationReceiptV1):
        self._require("deployed")
        if type(
            receipt
        ) is not HotfixVerificationReceiptV1 or not self._deployment_matches(receipt):
            raise HotfixError("verification_mismatch")
        passed = all(
            (
                receipt.ready,
                receipt.integrity_verified,
                receipt.regression_fixed,
                receipt.effects_disabled,
            )
        )
        self._record("deployed_verified" if passed else "verification_failed", receipt)

    def rollback(self, receipt: HotfixRollbackReceiptV1):
        self._require("deployed", "verification_failed", "deployed_verified")
        if (
            type(receipt) is not HotfixRollbackReceiptV1
            or receipt.integrated_commit != self._authorization.integrated_commit
            or receipt.rollback_commit != self._authorization.rollback_commit
            or receipt.target != self._authorization.target
        ):
            raise HotfixError("rollback_mismatch")
        passed = all(
            (receipt.ready, receipt.integrity_verified, receipt.effects_disabled)
        )
        self._record("rolled_back" if passed else "blocked", receipt)

    def close(self, receipt: HotfixCloseoutReceiptV1):
        self._require("deployed_verified", "rolled_back", "blocked", "cancelled")
        if type(receipt) is not HotfixCloseoutReceiptV1:
            raise HotfixError("invalid_closeout")
        expected = "fixed" if self.state == "deployed_verified" else self.state
        if (
            receipt.case_digest != digest(self._case)
            or receipt.outcome != expected
            or not receipt.cleanup_verified
        ):
            raise HotfixError("closeout_mismatch")
        self._record("closed", receipt)

    def stop(self, state: Literal["blocked", "cancelled"], evidence: str):
        self._require(
            "reported",
            "qualified",
            "active",
            "fix_ready",
            "integrated",
            "staging_accepted",
            "deploy_authorized",
        )
        if (
            state not in {"blocked", "cancelled"}
            or type(evidence) is not str
            or not evidence.strip()
        ):
            raise HotfixError("invalid_disposition")
        self._record(state, {"evidence": evidence})
