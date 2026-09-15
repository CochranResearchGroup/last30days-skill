"""Sealed contracts for provider-free acceptance campaigns."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, replace
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Mapping, Protocol


SCHEMA_VERSION = 1
SAFE_ID_CHARS = frozenset("abcdefghijklmnopqrstuvwxyz0123456789_-.:")


class ContractError(ValueError):
    """Raised when an acceptance contract is unsafe or inconsistent."""


class EvidenceTier(str, Enum):
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"


def require_safe_id(value: str, field_name: str) -> str:
    if (
        not isinstance(value, str)
        or not value
        or len(value) > 128
        or value[0] not in "abcdefghijklmnopqrstuvwxyz0123456789"
        or any(char not in SAFE_ID_CHARS for char in value)
    ):
        raise ContractError(f"{field_name} must be a safe identifier")
    return value


@dataclass(frozen=True)
class AdapterCase:
    case_id: str
    adapter_id: str
    source: str
    transport: str
    fixture_path: str
    expected_item_count: int = 1
    accounting_confidence: str = "exact"

    def __post_init__(self) -> None:
        for name in ("case_id", "adapter_id", "source", "transport"):
            require_safe_id(getattr(self, name), name)
        if self.transport not in {"http", "command", "browser"}:
            raise ContractError("transport is unsupported")
        if self.expected_item_count < 0:
            raise ContractError("expected_item_count must be nonnegative")
        if self.accounting_confidence not in {"exact", "opaque_request_equivalent"}:
            raise ContractError("accounting_confidence is unsupported")
        path = Path(self.fixture_path)
        if path.is_absolute() or ".." in path.parts:
            raise ContractError("fixture_path must be repository relative")


@dataclass(frozen=True)
class AcceptanceCatalog:
    cases: tuple[AdapterCase, ...]

    def __post_init__(self) -> None:
        case_ids = [case.case_id for case in self.cases]
        adapter_ids = [case.adapter_id for case in self.cases]
        if len(case_ids) != len(set(case_ids)):
            raise ContractError("duplicate case_id")
        if len(adapter_ids) != len(set(adapter_ids)):
            raise ContractError("duplicate adapter_id")


@dataclass(frozen=True)
class CampaignSpec:
    campaign_id: str
    case_ids: tuple[str, ...]
    tiers: tuple[EvidenceTier, ...] = tuple(EvidenceTier)
    max_requests_per_case: int = 1
    max_items_per_case: int = 3
    wall_timeout_seconds: int = 30
    effect_class: str = "provider_free"

    def __post_init__(self) -> None:
        require_safe_id(self.campaign_id, "campaign_id")
        if not self.case_ids or len(self.case_ids) != len(set(self.case_ids)):
            raise ContractError("case_ids must be unique and non-empty")
        if not self.tiers or len(self.tiers) != len(set(self.tiers)):
            raise ContractError("tiers must be unique and non-empty")
        if any(tier not in set(EvidenceTier) for tier in self.tiers):
            raise ContractError("tier is unsupported")
        if self.effect_class != "provider_free":
            raise ContractError("P0-P3 campaigns must be provider_free")
        if not 1 <= self.max_requests_per_case <= 10:
            raise ContractError("max_requests_per_case is outside bounds")
        if not 1 <= self.max_items_per_case <= 100:
            raise ContractError("max_items_per_case is outside bounds")
        if not 1 <= self.wall_timeout_seconds <= 300:
            raise ContractError("wall_timeout_seconds is outside bounds")


@dataclass(frozen=True)
class SealedCase:
    case: AdapterCase
    fixture_sha256: str


@dataclass(frozen=True)
class SealedPlan:
    schema_version: int
    campaign_id: str
    cases: tuple[SealedCase, ...]
    tiers: tuple[str, ...]
    effect_class: str
    max_requests_per_case: int
    max_items_per_case: int
    wall_timeout_seconds: int
    catalog_sha256: str
    source_sha256: str
    plan_sha256: str


@dataclass(frozen=True)
class ExecutionGrant:
    plan_sha256: str
    effect_class: str
    case_ids: tuple[str, ...]
    tiers: tuple[str, ...]
    max_requests_per_case: int
    max_items_per_case: int
    wall_timeout_seconds: int

    @classmethod
    def for_plan(cls, plan: SealedPlan) -> "ExecutionGrant":
        return cls(
            plan_sha256=plan.plan_sha256,
            effect_class=plan.effect_class,
            case_ids=tuple(item.case.case_id for item in plan.cases),
            tiers=plan.tiers,
            max_requests_per_case=plan.max_requests_per_case,
            max_items_per_case=plan.max_items_per_case,
            wall_timeout_seconds=plan.wall_timeout_seconds,
        )


@dataclass(frozen=True)
class TransportObservation:
    outcome: str
    transport_success: bool
    item_count: int
    request_count: int
    safe_reason_code: str | None
    accounting_confidence: str
    raw_safe_sha256: str
    details: Mapping[str, Any] = field(default_factory=dict)


class TransportTracer(Protocol):
    def __call__(self, case: SealedCase, *, item_limit: int) -> TransportObservation: ...


class JoinRunner(Protocol):
    def __call__(
        self, case: SealedCase, tracer: TransportTracer, *, item_limit: int
    ) -> tuple[TransportObservation, Mapping[str, Any]]: ...


@dataclass(frozen=True)
class AcceptanceDependencies:
    tracers: Mapping[str, TransportTracer]
    join_runner: JoinRunner
    resolution_probe: Callable[[str], None] | None = None

    def tracer(self, transport: str) -> TransportTracer:
        if self.resolution_probe is not None:
            self.resolution_probe(transport)
        try:
            return self.tracers[transport]
        except KeyError as exc:
            raise ContractError(f"missing tracer: {transport}") from exc


@dataclass(frozen=True)
class SampleReceipt:
    case_id: str
    adapter_id: str
    source: str
    tier: str
    fixture_sha256: str
    outcome: str
    transport_success: bool
    content_yield: bool
    item_count: int
    request_count: int
    accounting_confidence: str
    safe_reason_code: str | None
    redaction: str
    teardown: Mapping[str, Any]
    evidence: Mapping[str, Any]


@dataclass(frozen=True)
class AcceptanceReceipt:
    schema_version: int
    campaign_id: str
    plan_sha256: str
    catalog_sha256: str
    source_sha256: str
    effect_class: str
    grant_sha256: str
    samples: tuple[SampleReceipt, ...]
    first_failure: Mapping[str, str] | None
    observed_budgets: Mapping[str, int]
    effect_census: Mapping[str, int]
    receipt_sha256: str

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["samples"] = [asdict(sample) for sample in self.samples]
        return payload

    def with_digest(self, value: str) -> "AcceptanceReceipt":
        return replace(self, receipt_sha256=value)


@dataclass(frozen=True)
class AcceptanceVerdict:
    accepted: bool
    safe_reason_codes: tuple[str, ...]
    verified_samples: int
    expected_samples: int
