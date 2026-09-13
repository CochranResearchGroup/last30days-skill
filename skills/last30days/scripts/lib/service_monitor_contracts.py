"""Strict immutable contracts for provider-free saved-monitor evaluation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any, ClassVar, Iterable, Mapping


SCHEMA_VERSION = 1
COMPARATOR_VERSION = "stable_evidence_v1"


class MonitorContractError(ValueError):
    """Raised when a monitor contract violates its closed-world schema."""


class MonitorLifecycle(StrEnum):
    DISABLED = "disabled"
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"


class CoverageStatus(StrEnum):
    COMPLETE = "complete"
    PARTIAL = "partial"


class ComparisonStatus(StrEnum):
    BASELINE_ONLY = "baseline_only"
    COMPLETE = "complete"
    INCOMPLETE = "comparison_incomplete"


class ChangeKind(StrEnum):
    NEW = "new"
    REVISED = "revised"
    UNCHANGED = "unchanged"
    REMOVED = "removed"


class DecisionKind(StrEnum):
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class MonitorErrorCode(StrEnum):
    SCHEMA_UNSUPPORTED = "schema_unsupported"
    IMMUTABLE_CONFLICT = "immutable_conflict"
    INVALID_REVISION = "invalid_revision"
    INVALID_LIFECYCLE = "invalid_lifecycle"
    MONITOR_PAUSED = "monitor_paused"
    MONITOR_ARCHIVED = "monitor_archived"
    VIEW_UNAVAILABLE = "view_unavailable"
    VIEW_MISMATCH = "view_mismatch"
    PARTITION_MISMATCH = "partition_mismatch"
    COMPARISON_INCOMPLETE = "comparison_incomplete"
    DECISION_CONFLICT = "decision_conflict"
    STALE_BASELINE = "stale_baseline"


def _object(value: Any, field: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise MonitorContractError(f"{field} must be an object")
    return value


def _exact(payload: Mapping[str, Any], fields: Iterable[str], name: str) -> None:
    expected = set(fields)
    actual = set(payload)
    unknown = sorted(actual - expected)
    missing = sorted(expected - actual)
    if unknown:
        raise MonitorContractError(f"{name} has unknown fields: {unknown}")
    if missing:
        raise MonitorContractError(f"{name} is missing fields: {missing}")


def _text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise MonitorContractError(f"{field} must be a non-empty string")
    return value


def _optional_text(value: Any, field: str) -> str | None:
    if value is None:
        return None
    return _text(value, field)


def _positive_int(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise MonitorContractError(f"{field} must be a positive integer")
    return value


def _non_negative_int(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise MonitorContractError(f"{field} must be a non-negative integer")
    return value


def _timestamp(value: Any, field: str) -> str:
    text = _text(value, field)
    if not text.endswith("Z"):
        raise MonitorContractError(f"{field} must be a UTC timestamp ending in Z")
    try:
        datetime.fromisoformat(text[:-1] + "+00:00")
    except ValueError as exc:
        raise MonitorContractError(f"{field} must be an ISO-8601 timestamp") from exc
    return text


def _schema(value: Any) -> int:
    if value != SCHEMA_VERSION:
        raise MonitorContractError(f"schema_version must be {SCHEMA_VERSION}")
    return SCHEMA_VERSION


def _enum(enum_type: type[StrEnum], value: Any, field: str) -> StrEnum:
    try:
        return enum_type(value)
    except (TypeError, ValueError) as exc:
        raise MonitorContractError(f"{field} is invalid") from exc


@dataclass(frozen=True)
class MonitorErrorV1:
    schema_version: int
    code: MonitorErrorCode
    message: str
    monitor_id: str | None
    run_id: str | None

    FIELDS: ClassVar[tuple[str, ...]] = (
        "schema_version",
        "code",
        "message",
        "monitor_id",
        "run_id",
    )

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> MonitorErrorV1:
        payload = _object(value, "monitor_error")
        _exact(payload, cls.FIELDS, "monitor_error")
        code = _enum(MonitorErrorCode, payload["code"], "error.code")
        assert isinstance(code, MonitorErrorCode)
        return cls(
            schema_version=_schema(payload["schema_version"]),
            code=code,
            message=_text(payload["message"], "error.message"),
            monitor_id=_optional_text(payload["monitor_id"], "monitor_id"),
            run_id=_optional_text(payload["run_id"], "run_id"),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "code": self.code.value,
            "message": self.message,
            "monitor_id": self.monitor_id,
            "run_id": self.run_id,
        }


@dataclass(frozen=True)
class SavedQueryViewRefV1:
    schema_version: int
    view_kind: str
    saved_query_id: str
    saved_query_version: int

    FIELDS: ClassVar[tuple[str, ...]] = (
        "schema_version",
        "view_kind",
        "saved_query_id",
        "saved_query_version",
    )

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> SavedQueryViewRefV1:
        payload = _object(value, "view_ref")
        _exact(payload, cls.FIELDS, "view_ref")
        if payload["view_kind"] != "saved_query":
            raise MonitorContractError("view_kind must be saved_query")
        return cls(
            schema_version=_schema(payload["schema_version"]),
            view_kind="saved_query",
            saved_query_id=_text(payload["saved_query_id"], "saved_query_id"),
            saved_query_version=_positive_int(
                payload["saved_query_version"], "saved_query_version"
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "view_kind": self.view_kind,
            "saved_query_id": self.saved_query_id,
            "saved_query_version": self.saved_query_version,
        }


@dataclass(frozen=True)
class EvidenceVersionV1:
    evidence_id: str
    version_id: str
    tombstoned: bool

    FIELDS: ClassVar[tuple[str, ...]] = (
        "evidence_id",
        "version_id",
        "tombstoned",
    )

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> EvidenceVersionV1:
        payload = _object(value, "evidence")
        _exact(payload, cls.FIELDS, "evidence")
        if not isinstance(payload["tombstoned"], bool):
            raise MonitorContractError("tombstoned must be boolean")
        return cls(
            evidence_id=_text(payload["evidence_id"], "evidence_id"),
            version_id=_text(payload["version_id"], "version_id"),
            tombstoned=payload["tombstoned"],
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "version_id": self.version_id,
            "tombstoned": self.tombstoned,
        }


@dataclass(frozen=True)
class ViewCoverageV1:
    status: CoverageStatus
    sources: tuple[str, ...]
    gaps: tuple[str, ...]

    FIELDS: ClassVar[tuple[str, ...]] = ("status", "sources", "gaps")

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> ViewCoverageV1:
        payload = _object(value, "coverage")
        _exact(payload, cls.FIELDS, "coverage")
        sources = cls._strings(payload["sources"], "sources")
        gaps = cls._strings(payload["gaps"], "gaps")
        status = _enum(CoverageStatus, payload["status"], "coverage.status")
        assert isinstance(status, CoverageStatus)
        if status is CoverageStatus.COMPLETE and gaps:
            raise MonitorContractError("complete coverage cannot contain gaps")
        return cls(status=status, sources=sources, gaps=gaps)

    @staticmethod
    def _strings(value: Any, field: str) -> tuple[str, ...]:
        if not isinstance(value, list):
            raise MonitorContractError(f"coverage.{field} must be a list")
        result = tuple(_text(item, f"coverage.{field}") for item in value)
        if len(set(result)) != len(result):
            raise MonitorContractError(f"coverage.{field} must be unique")
        return result

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "sources": list(self.sources),
            "gaps": list(self.gaps),
        }


@dataclass(frozen=True)
class SavedQueryViewSnapshotV1:
    schema_version: int
    snapshot_id: str
    view_ref: SavedQueryViewRefV1
    access_partition_id: str
    evidence_head_id: str
    knowledge_cutoff: str
    coverage_start: str
    coverage_end: str
    coverage: ViewCoverageV1
    evidence: tuple[EvidenceVersionV1, ...]

    FIELDS: ClassVar[tuple[str, ...]] = (
        "schema_version",
        "snapshot_id",
        "view_ref",
        "access_partition_id",
        "evidence_head_id",
        "knowledge_cutoff",
        "coverage_start",
        "coverage_end",
        "coverage",
        "evidence",
    )

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> SavedQueryViewSnapshotV1:
        payload = _object(value, "view_snapshot")
        _exact(payload, cls.FIELDS, "view_snapshot")
        raw_evidence = payload["evidence"]
        if not isinstance(raw_evidence, list):
            raise MonitorContractError("evidence must be a list")
        evidence = tuple(EvidenceVersionV1.from_dict(item) for item in raw_evidence)
        identities = [item.evidence_id for item in evidence]
        if len(set(identities)) != len(identities):
            raise MonitorContractError("evidence identities must be unique")
        start = _timestamp(payload["coverage_start"], "coverage_start")
        end = _timestamp(payload["coverage_end"], "coverage_end")
        cutoff = _timestamp(payload["knowledge_cutoff"], "knowledge_cutoff")
        if start > end or end > cutoff:
            raise MonitorContractError(
                "coverage_start, coverage_end, and knowledge_cutoff are out of order"
            )
        return cls(
            schema_version=_schema(payload["schema_version"]),
            snapshot_id=_text(payload["snapshot_id"], "snapshot_id"),
            view_ref=SavedQueryViewRefV1.from_dict(payload["view_ref"]),
            access_partition_id=_text(
                payload["access_partition_id"], "access_partition_id"
            ),
            evidence_head_id=_text(payload["evidence_head_id"], "evidence_head_id"),
            knowledge_cutoff=cutoff,
            coverage_start=start,
            coverage_end=end,
            coverage=ViewCoverageV1.from_dict(payload["coverage"]),
            evidence=evidence,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "snapshot_id": self.snapshot_id,
            "view_ref": self.view_ref.to_dict(),
            "access_partition_id": self.access_partition_id,
            "evidence_head_id": self.evidence_head_id,
            "knowledge_cutoff": self.knowledge_cutoff,
            "coverage_start": self.coverage_start,
            "coverage_end": self.coverage_end,
            "coverage": self.coverage.to_dict(),
            "evidence": [item.to_dict() for item in self.evidence],
        }


@dataclass(frozen=True)
class MonitorSpecV1:
    schema_version: int
    monitor_id: str
    revision: int
    name: str
    view_ref: SavedQueryViewRefV1
    access_partition_id: str
    lifecycle_state: MonitorLifecycle
    comparison_policy: str
    cadence_seconds: int
    max_items: int
    retention_days: int
    created_by: str
    created_at: str

    FIELDS: ClassVar[tuple[str, ...]] = (
        "schema_version",
        "monitor_id",
        "revision",
        "name",
        "view_ref",
        "access_partition_id",
        "lifecycle_state",
        "comparison_policy",
        "cadence_seconds",
        "max_items",
        "retention_days",
        "created_by",
        "created_at",
    )

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> MonitorSpecV1:
        payload = _object(value, "monitor_spec")
        _exact(payload, cls.FIELDS, "monitor_spec")
        lifecycle = _enum(
            MonitorLifecycle, payload["lifecycle_state"], "lifecycle_state"
        )
        assert isinstance(lifecycle, MonitorLifecycle)
        comparison_policy = _text(
            payload["comparison_policy"], "comparison_policy"
        )
        if comparison_policy != COMPARATOR_VERSION:
            raise MonitorContractError(
                f"comparison_policy must be {COMPARATOR_VERSION}"
            )
        return cls(
            schema_version=_schema(payload["schema_version"]),
            monitor_id=_text(payload["monitor_id"], "monitor_id"),
            revision=_positive_int(payload["revision"], "revision"),
            name=_text(payload["name"], "name"),
            view_ref=SavedQueryViewRefV1.from_dict(payload["view_ref"]),
            access_partition_id=_text(
                payload["access_partition_id"], "access_partition_id"
            ),
            lifecycle_state=lifecycle,
            comparison_policy=comparison_policy,
            cadence_seconds=_positive_int(
                payload["cadence_seconds"], "cadence_seconds"
            ),
            max_items=_positive_int(payload["max_items"], "max_items"),
            retention_days=_positive_int(
                payload["retention_days"], "retention_days"
            ),
            created_by=_text(payload["created_by"], "created_by"),
            created_at=_timestamp(payload["created_at"], "created_at"),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "monitor_id": self.monitor_id,
            "revision": self.revision,
            "name": self.name,
            "view_ref": self.view_ref.to_dict(),
            "access_partition_id": self.access_partition_id,
            "lifecycle_state": self.lifecycle_state.value,
            "comparison_policy": self.comparison_policy,
            "cadence_seconds": self.cadence_seconds,
            "max_items": self.max_items,
            "retention_days": self.retention_days,
            "created_by": self.created_by,
            "created_at": self.created_at,
        }


@dataclass(frozen=True)
class EvidenceChangeV1:
    kind: ChangeKind
    evidence_id: str
    prior_version_id: str | None
    current_version_id: str | None

    FIELDS: ClassVar[tuple[str, ...]] = (
        "kind",
        "evidence_id",
        "prior_version_id",
        "current_version_id",
    )

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> EvidenceChangeV1:
        payload = _object(value, "change")
        _exact(payload, cls.FIELDS, "change")
        kind = _enum(ChangeKind, payload["kind"], "change.kind")
        assert isinstance(kind, ChangeKind)
        prior = _optional_text(payload["prior_version_id"], "prior_version_id")
        current = _optional_text(
            payload["current_version_id"], "current_version_id"
        )
        valid = {
            ChangeKind.NEW: prior is None and current is not None,
            ChangeKind.REVISED: (
                prior is not None and current is not None and prior != current
            ),
            ChangeKind.UNCHANGED: prior is not None and prior == current,
            ChangeKind.REMOVED: prior is not None and current is None,
        }
        if not valid[kind]:
            raise MonitorContractError(f"invalid versions for {kind.value} change")
        return cls(
            kind=kind,
            evidence_id=_text(payload["evidence_id"], "evidence_id"),
            prior_version_id=prior,
            current_version_id=current,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind.value,
            "evidence_id": self.evidence_id,
            "prior_version_id": self.prior_version_id,
            "current_version_id": self.current_version_id,
        }


@dataclass(frozen=True)
class MonitorComparisonV1:
    schema_version: int
    comparator_version: str
    status: ComparisonStatus
    prior_baseline_id: str | None
    snapshot_id: str
    prior_count: int
    current_count: int
    changes: tuple[EvidenceChangeV1, ...]

    FIELDS: ClassVar[tuple[str, ...]] = (
        "schema_version",
        "comparator_version",
        "status",
        "prior_baseline_id",
        "snapshot_id",
        "prior_count",
        "current_count",
        "changes",
    )

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> MonitorComparisonV1:
        payload = _object(value, "comparison")
        _exact(payload, cls.FIELDS, "comparison")
        if payload["comparator_version"] != COMPARATOR_VERSION:
            raise MonitorContractError(
                f"comparator_version must be {COMPARATOR_VERSION}"
            )
        status = _enum(ComparisonStatus, payload["status"], "comparison.status")
        assert isinstance(status, ComparisonStatus)
        raw_changes = payload["changes"]
        if not isinstance(raw_changes, list):
            raise MonitorContractError("changes must be a list")
        changes = tuple(EvidenceChangeV1.from_dict(item) for item in raw_changes)
        identities = [item.evidence_id for item in changes]
        if len(set(identities)) != len(identities):
            raise MonitorContractError("change identities must be unique")
        if status is ComparisonStatus.INCOMPLETE and any(
            item.kind is ChangeKind.REMOVED for item in changes
        ):
            raise MonitorContractError("incomplete comparison cannot emit removals")
        prior_baseline_id = _optional_text(
            payload["prior_baseline_id"], "prior_baseline_id"
        )
        if status is ComparisonStatus.BASELINE_ONLY:
            if prior_baseline_id is not None or changes:
                raise MonitorContractError(
                    "baseline-only comparison cannot have a prior baseline or changes"
                )
        elif prior_baseline_id is None:
            raise MonitorContractError(
                "non-initial comparison requires a prior baseline"
            )
        return cls(
            schema_version=_schema(payload["schema_version"]),
            comparator_version=COMPARATOR_VERSION,
            status=status,
            prior_baseline_id=prior_baseline_id,
            snapshot_id=_text(payload["snapshot_id"], "snapshot_id"),
            prior_count=_non_negative_int(payload["prior_count"], "prior_count"),
            current_count=_non_negative_int(
                payload["current_count"], "current_count"
            ),
            changes=changes,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "comparator_version": self.comparator_version,
            "status": self.status.value,
            "prior_baseline_id": self.prior_baseline_id,
            "snapshot_id": self.snapshot_id,
            "prior_count": self.prior_count,
            "current_count": self.current_count,
            "changes": [item.to_dict() for item in self.changes],
        }

    def by_kind(self, kind: ChangeKind) -> tuple[EvidenceChangeV1, ...]:
        return tuple(item for item in self.changes if item.kind is kind)


@dataclass(frozen=True)
class MonitorBaselineV1:
    schema_version: int
    baseline_id: str
    monitor_id: str
    monitor_revision: int
    snapshot_id: str
    access_partition_id: str
    evidence_head_id: str
    knowledge_cutoff: str
    evidence: tuple[EvidenceVersionV1, ...]
    created_at: str

    FIELDS: ClassVar[tuple[str, ...]] = (
        "schema_version",
        "baseline_id",
        "monitor_id",
        "monitor_revision",
        "snapshot_id",
        "access_partition_id",
        "evidence_head_id",
        "knowledge_cutoff",
        "evidence",
        "created_at",
    )

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> MonitorBaselineV1:
        payload = _object(value, "baseline")
        _exact(payload, cls.FIELDS, "baseline")
        raw_evidence = payload["evidence"]
        if not isinstance(raw_evidence, list):
            raise MonitorContractError("baseline evidence must be a list")
        evidence = tuple(EvidenceVersionV1.from_dict(item) for item in raw_evidence)
        identities = [item.evidence_id for item in evidence]
        if len(set(identities)) != len(identities):
            raise MonitorContractError("baseline evidence identities must be unique")
        if any(item.tombstoned for item in evidence):
            raise MonitorContractError("baseline evidence cannot contain tombstones")
        return cls(
            schema_version=_schema(payload["schema_version"]),
            baseline_id=_text(payload["baseline_id"], "baseline_id"),
            monitor_id=_text(payload["monitor_id"], "monitor_id"),
            monitor_revision=_positive_int(
                payload["monitor_revision"], "monitor_revision"
            ),
            snapshot_id=_text(payload["snapshot_id"], "snapshot_id"),
            access_partition_id=_text(
                payload["access_partition_id"], "access_partition_id"
            ),
            evidence_head_id=_text(payload["evidence_head_id"], "evidence_head_id"),
            knowledge_cutoff=_timestamp(
                payload["knowledge_cutoff"], "knowledge_cutoff"
            ),
            evidence=evidence,
            created_at=_timestamp(payload["created_at"], "created_at"),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "baseline_id": self.baseline_id,
            "monitor_id": self.monitor_id,
            "monitor_revision": self.monitor_revision,
            "snapshot_id": self.snapshot_id,
            "access_partition_id": self.access_partition_id,
            "evidence_head_id": self.evidence_head_id,
            "knowledge_cutoff": self.knowledge_cutoff,
            "evidence": [item.to_dict() for item in self.evidence],
            "created_at": self.created_at,
        }


@dataclass(frozen=True)
class MonitorRunV1:
    schema_version: int
    run_id: str
    monitor_id: str
    monitor_revision: int
    snapshot_id: str
    prior_baseline_id: str | None
    candidate_baseline_id: str
    comparison: MonitorComparisonV1
    created_at: str

    FIELDS: ClassVar[tuple[str, ...]] = (
        "schema_version",
        "run_id",
        "monitor_id",
        "monitor_revision",
        "snapshot_id",
        "prior_baseline_id",
        "candidate_baseline_id",
        "comparison",
        "created_at",
    )

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> MonitorRunV1:
        payload = _object(value, "monitor_run")
        _exact(payload, cls.FIELDS, "monitor_run")
        comparison = MonitorComparisonV1.from_dict(payload["comparison"])
        prior = _optional_text(payload["prior_baseline_id"], "prior_baseline_id")
        if comparison.prior_baseline_id != prior:
            raise MonitorContractError("run and comparison prior baseline differ")
        if comparison.snapshot_id != payload["snapshot_id"]:
            raise MonitorContractError("run and comparison snapshot differ")
        return cls(
            schema_version=_schema(payload["schema_version"]),
            run_id=_text(payload["run_id"], "run_id"),
            monitor_id=_text(payload["monitor_id"], "monitor_id"),
            monitor_revision=_positive_int(
                payload["monitor_revision"], "monitor_revision"
            ),
            snapshot_id=_text(payload["snapshot_id"], "snapshot_id"),
            prior_baseline_id=prior,
            candidate_baseline_id=_text(
                payload["candidate_baseline_id"], "candidate_baseline_id"
            ),
            comparison=comparison,
            created_at=_timestamp(payload["created_at"], "created_at"),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "run_id": self.run_id,
            "monitor_id": self.monitor_id,
            "monitor_revision": self.monitor_revision,
            "snapshot_id": self.snapshot_id,
            "prior_baseline_id": self.prior_baseline_id,
            "candidate_baseline_id": self.candidate_baseline_id,
            "comparison": self.comparison.to_dict(),
            "created_at": self.created_at,
        }


@dataclass(frozen=True)
class MonitorDecisionV1:
    schema_version: int
    decision_id: str
    monitor_id: str
    run_id: str
    baseline_id: str
    decision: DecisionKind
    decided_by: str
    decided_at: str

    FIELDS: ClassVar[tuple[str, ...]] = (
        "schema_version",
        "decision_id",
        "monitor_id",
        "run_id",
        "baseline_id",
        "decision",
        "decided_by",
        "decided_at",
    )

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> MonitorDecisionV1:
        payload = _object(value, "monitor_decision")
        _exact(payload, cls.FIELDS, "monitor_decision")
        decision = _enum(DecisionKind, payload["decision"], "decision")
        assert isinstance(decision, DecisionKind)
        return cls(
            schema_version=_schema(payload["schema_version"]),
            decision_id=_text(payload["decision_id"], "decision_id"),
            monitor_id=_text(payload["monitor_id"], "monitor_id"),
            run_id=_text(payload["run_id"], "run_id"),
            baseline_id=_text(payload["baseline_id"], "baseline_id"),
            decision=decision,
            decided_by=_text(payload["decided_by"], "decided_by"),
            decided_at=_timestamp(payload["decided_at"], "decided_at"),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "decision_id": self.decision_id,
            "monitor_id": self.monitor_id,
            "run_id": self.run_id,
            "baseline_id": self.baseline_id,
            "decision": self.decision.value,
            "decided_by": self.decided_by,
            "decided_at": self.decided_at,
        }
