"""Deterministic host execution of one already-frozen durable tick."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlparse

from .service_tick_anomalies import AnomalyMonitor, AnomalyRule
from .service_tick_analysis import (
    AnalysisAdapterRegistry,
    MediaAnalysisInput,
    OcrAnalysis,
    default_analysis_adapter_registry,
)
from .service_tick_adapters import (
    AdapterRegistry,
    AdapterRegistryError,
    next_provider_ordinal,
    should_retry_provider,
)
from .service_tick_incidents import (
    IncidentManager,
    IncidentSignal,
    NotificationExhaustedError,
    NotificationTransport,
    classify_provider_issue,
    provider_issue_summary,
)
from .service_tick_media import (
    MediaDerivativePublisher,
    OcrRegion,
    SemanticSidecar,
)
from .service_tick_query import CatalogMember, SnapshotEntry, TickSnapshotPublisher
from .service_tick import order_lanes_by_target_config


Clock = Callable[[], datetime]
FaultInjector = Callable[[str], None]
_USAGE_FIELDS = frozenset(
    {
        "attempts",
        "network_requests",
        "wall_seconds",
        "items",
        "cost_cents",
        "model_tokens",
    }
)
_TICK_TERMINAL = frozenset(
    {"complete", "complete_degraded", "failed", "missed_due_to_overlap"}
)
_BLOCKING_INCIDENTS = frozenset(
    {
        "captcha_required",
        "cloudflare_challenge",
        "rate_limit_blocked",
        "reauthentication_required",
    }
)


def _canonical_json(value: object) -> str:
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def _digest(value: object) -> str:
    return "sha256:" + hashlib.sha256(_canonical_json(value).encode()).hexdigest()


def _stable_id(prefix: str, value: object) -> str:
    return f"{prefix}-{hashlib.sha256(_canonical_json(value).encode()).hexdigest()[:32]}"


def _text(value: object, field: str, maximum: int = 65_536) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > maximum:
        raise ValueError(f"{field} must be a bounded non-empty string")
    return value


def _now(clock: Clock) -> tuple[datetime, str]:
    value = clock()
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("clock must return a timezone-aware datetime")
    utc = value.astimezone(timezone.utc)
    return utc, utc.isoformat().replace("+00:00", "Z")


def _usage(value: Mapping[str, object]) -> dict[str, int]:
    if set(value) != _USAGE_FIELDS:
        raise ValueError("provider usage fields are incomplete or unknown")
    result: dict[str, int] = {}
    for field in sorted(_USAGE_FIELDS):
        observed = value[field]
        if isinstance(observed, bool) or not isinstance(observed, int) or observed < 0:
            raise ValueError(f"provider usage {field} must be non-negative")
        result[field] = observed
    if result["attempts"] != 1:
        raise ValueError("each provider result must consume exactly one attempt")
    return result


@dataclass(frozen=True)
class CollectedMedia:
    source_url: str
    content: bytes
    mime_type: str
    media_kind: str
    alt_text: str | None
    ocr_regions: tuple[OcrRegion, ...] = ()
    detected_language: str | None = None
    ocr_engine: str | None = None
    ocr_engine_version: str | None = None
    semantic_sidecar: SemanticSidecar | None = None

    def __post_init__(self) -> None:
        _text(self.source_url, "media.source_url", 4_096)
        if not isinstance(self.content, bytes) or not self.content:
            raise ValueError("media content must be non-empty bytes")
        _text(self.mime_type, "media.mime_type", 256)
        if self.media_kind not in {"image", "video_thumbnail"}:
            raise ValueError("collected media kind is unsupported")
        if self.ocr_regions and (not self.ocr_engine or not self.ocr_engine_version):
            raise ValueError("OCR regions require an engine and version")


@dataclass(frozen=True)
class CollectedItem:
    source_native_id: str
    url: str
    title: str
    text: str
    author: str | None
    published_at: str | None
    media: tuple[CollectedMedia, ...] = ()
    metadata: dict[str, object] | None = None

    def __post_init__(self) -> None:
        _text(self.source_native_id, "source_native_id", 512)
        _text(self.url, "url", 4_096)
        _text(self.title, "title", 2_048)
        _text(self.text, "text")
        if self.author is not None:
            _text(self.author, "author", 1_024)
        if self.published_at is not None:
            _text(self.published_at, "published_at", 64)
        if self.metadata is not None and not isinstance(self.metadata, dict):
            raise ValueError("item metadata must be an object")


@dataclass(frozen=True)
class ProviderResult:
    status: str
    items: tuple[CollectedItem, ...]
    usage: dict[str, int]
    failure_class: str | None = None
    safe_error_code: str | None = None
    failure_stage: str | None = None
    failure_reason_code: str | None = None
    failure_signature: str | None = None
    page_signals: tuple[str, ...] = ()
    rendered_page: bytes | None = None
    rendered_page_mime_type: str | None = None
    operator_url: str | None = None
    outcome_counts: dict[str, int] | None = None
    browser_operations: tuple[dict[str, object], ...] = ()
    rejection_counts: dict[str, int] | None = None

    def __post_init__(self) -> None:
        if self.status not in {"success", "partial", "empty", "failure"}:
            raise ValueError("provider result status is unsupported")
        normalized = _usage(self.usage)
        object.__setattr__(self, "usage", normalized)
        if self.status in {"success", "partial"} and not self.items:
            raise ValueError("successful or partial provider result must contain items")
        if self.status not in {"success", "partial"} and self.items:
            raise ValueError("empty or failed provider result cannot contain items")
        if normalized["items"] != len(self.items):
            raise ValueError("provider item usage does not match result items")
        if self.status in {"partial", "failure"}:
            _text(self.failure_class, "failure_class", 64)
            _text(self.safe_error_code, "safe_error_code", 64)
        if self.failure_stage is not None:
            stage = _text(self.failure_stage, "failure_stage", 64)
            if any(
                character not in "abcdefghijklmnopqrstuvwxyz0123456789_"
                for character in stage
            ):
                raise ValueError("failure stage must be a normalized safe identifier")
        if self.failure_reason_code is not None:
            reason = _text(self.failure_reason_code, "failure_reason_code", 64)
            if any(
                character not in "abcdefghijklmnopqrstuvwxyz0123456789_"
                for character in reason
            ):
                raise ValueError("failure reason must be a normalized safe identifier")
        if self.failure_signature is not None:
            signature = _text(self.failure_signature, "failure_signature", 71)
            digest = signature.removeprefix("sha256:")
            if (
                not signature.startswith("sha256:")
                or len(digest) != 64
                or any(character not in "0123456789abcdef" for character in digest)
            ):
                raise ValueError("failure signature must be a lowercase SHA-256 identifier")
        if self.rendered_page is not None and not self.rendered_page_mime_type:
            raise ValueError("rendered page bytes require a MIME type")
        if self.operator_url is not None:
            _text(self.operator_url, "operator_url", 4_096)
            parsed = urlparse(self.operator_url)
            if (
                parsed.scheme != "https"
                or not parsed.hostname
                or parsed.hostname.casefold() in {"localhost", "127.0.0.1", "::1"}
            ):
                raise ValueError("operator URL must be an external HTTPS URL")
        counts = self.outcome_counts
        if counts is None:
            counts = {
                "attempted": len(self.items),
                "observed": len(self.items),
                "accepted": len(self.items),
                "rejected": 0,
            }
        if set(counts) != {"attempted", "observed", "accepted", "rejected"}:
            raise ValueError("provider outcome count fields are incomplete or unknown")
        normalized_counts: dict[str, int] = {}
        for field, value in counts.items():
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise ValueError(f"provider outcome count {field} must be non-negative")
            normalized_counts[field] = value
        if (
            normalized_counts["attempted"] < normalized_counts["observed"]
            or normalized_counts["observed"]
            != normalized_counts["accepted"] + normalized_counts["rejected"]
            or normalized_counts["accepted"] != len(self.items)
        ):
            raise ValueError("provider outcome counts are inconsistent")
        object.__setattr__(self, "outcome_counts", normalized_counts)
        if len(self.browser_operations) > 12:
            raise ValueError("provider browser operation evidence exceeds the bound")
        for operation in self.browser_operations:
            if not isinstance(operation, dict) or not operation:
                raise ValueError("provider browser operation evidence must be objects")
            if set(operation) - {"operation", "status", "duration_ms", "error_type"}:
                raise ValueError("provider browser operation evidence has unknown fields")
            _text(operation.get("operation"), "browser operation", 64)
            if operation.get("status") not in {"ok", "failed", "timed_out"}:
                raise ValueError("provider browser operation status is unsupported")
            duration_ms = operation.get("duration_ms")
            if (
                isinstance(duration_ms, bool)
                or not isinstance(duration_ms, int)
                or not 0 <= duration_ms <= 600_000
            ):
                raise ValueError("provider browser operation duration is invalid")
            if operation.get("error_type") is not None:
                _text(operation.get("error_type"), "browser operation error type", 64)
        rejection_counts = self.rejection_counts or {}
        if len(rejection_counts) > 32:
            raise ValueError("provider rejection count evidence exceeds the bound")
        normalized_rejections: dict[str, int] = {}
        for reason, count in rejection_counts.items():
            _text(reason, "provider rejection reason", 64)
            if (
                isinstance(count, bool)
                or not isinstance(count, int)
                or not 0 <= count <= 1_000_000
            ):
                raise ValueError("provider rejection count is invalid")
            normalized_rejections[reason] = count
        object.__setattr__(self, "rejection_counts", normalized_rejections)

    @classmethod
    def success(
        cls, *, items: tuple[CollectedItem, ...], usage: Mapping[str, object]
    ) -> ProviderResult:
        return cls(status="success", items=items, usage=dict(usage))

    @classmethod
    def empty(cls, *, usage: Mapping[str, object]) -> ProviderResult:
        return cls(status="empty", items=(), usage=dict(usage))

    @classmethod
    def failure(
        cls,
        *,
        failure_class: str,
        safe_error_code: str,
        usage: Mapping[str, object],
        page_signals: tuple[str, ...] = (),
        rendered_page: bytes | None = None,
        rendered_page_mime_type: str | None = None,
        operator_url: str | None = None,
    ) -> ProviderResult:
        return cls(
            status="failure",
            items=(),
            usage=dict(usage),
            failure_class=failure_class,
            safe_error_code=safe_error_code,
            page_signals=page_signals,
            rendered_page=rendered_page,
            rendered_page_mime_type=rendered_page_mime_type,
            operator_url=operator_url,
        )


@dataclass(frozen=True)
class ProviderContext:
    tick_id: str
    execution_attempt_id: str
    lane_id: str
    service_id: str
    source: str
    target_id: str
    selector: dict[str, object]
    access_partition_id: str
    retention_class: str
    provider_id: str
    adapter_type: str
    limits: dict[str, int]
    interval_from: str
    interval_to: str
    surface_kind: str = "topic"


class TickBudgetExceeded(RuntimeError):
    pass


class TickBudgetAdmissionExhausted(RuntimeError):
    pass


class TickRunner:
    def __init__(
        self,
        db_path: Path,
        registry: AdapterRegistry,
        *,
        media: MediaDerivativePublisher,
        incidents: IncidentManager,
        snapshots: TickSnapshotPublisher,
        notification_transports: Sequence[NotificationTransport],
        analysis_registry: AnalysisAdapterRegistry | None = None,
        clock: Clock | None = None,
        fault_injector: FaultInjector | None = None,
    ) -> None:
        self.db_path = Path(db_path)
        self.registry = registry
        self.media = media
        self.incidents = incidents
        self.snapshots = snapshots
        self.notification_transports = tuple(notification_transports)
        self.analysis_registry = analysis_registry or default_analysis_adapter_registry()
        self.clock = clock or (lambda: datetime.now(timezone.utc))
        self.fault_injector = fault_injector or (lambda _point: None)
        self.anomalies = AnomalyMonitor(self.db_path, clock=self.clock)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=5)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("PRAGMA busy_timeout=5000")
        return conn

    def _serialize_provider_result(
        self, result: ProviderResult, *, access_partition_id: str
    ) -> dict[str, object]:
        def serialize_media(media: CollectedMedia) -> dict[str, object]:
            storage_ref, content_hash = self.media.artifacts.put(
                media.content, access_partition_id=access_partition_id
            )
            return {
                "source_url": media.source_url,
                "storage_ref": storage_ref,
                "content_hash": content_hash,
                "mime_type": media.mime_type,
                "media_kind": media.media_kind,
                "alt_text": media.alt_text,
                "ocr_regions": [region.to_dict() for region in media.ocr_regions],
                "detected_language": media.detected_language,
                "ocr_engine": media.ocr_engine,
                "ocr_engine_version": media.ocr_engine_version,
                "semantic_sidecar": (
                    media.semantic_sidecar.to_dict()
                    if media.semantic_sidecar is not None
                    else None
                ),
            }

        rendered_page = None
        if result.rendered_page is not None:
            storage_ref, content_hash = self.media.artifacts.put(
                result.rendered_page, access_partition_id=access_partition_id
            )
            rendered_page = {
                "storage_ref": storage_ref,
                "content_hash": content_hash,
                "mime_type": result.rendered_page_mime_type,
            }
        return {
            "status": result.status,
            "items": [
                {
                    "source_native_id": item.source_native_id,
                    "url": item.url,
                    "title": item.title,
                    "text": item.text,
                    "author": item.author,
                    "published_at": item.published_at,
                    "metadata": item.metadata,
                    "media": [serialize_media(media) for media in item.media],
                }
                for item in result.items
            ],
            "usage": result.usage,
            "failure_class": result.failure_class,
            "safe_error_code": result.safe_error_code,
            "failure_stage": result.failure_stage,
            "failure_reason_code": result.failure_reason_code,
            "failure_signature": result.failure_signature,
            "page_signals": list(result.page_signals),
            "rendered_page": rendered_page,
            "operator_url": result.operator_url,
            "outcome_counts": result.outcome_counts,
            "browser_operations": list(result.browser_operations),
            "rejection_counts": result.rejection_counts,
        }

    def _restore_provider_result(self, payload: Mapping[str, object]) -> ProviderResult:
        def stored_bytes(value: object) -> bytes:
            if not isinstance(value, Mapping):
                raise ValueError("persisted artifact reference must be an object")
            storage_ref = _text(value.get("storage_ref"), "storage_ref", 4_096)
            expected_hash = _text(value.get("content_hash"), "content_hash", 128)
            content = self.media.artifacts.read(storage_ref)
            observed_hash = "sha256:" + hashlib.sha256(content).hexdigest()
            if observed_hash != expected_hash:
                raise ValueError("persisted provider artifact hash mismatch")
            return content

        def restore_sidecar(value: object) -> SemanticSidecar | None:
            if value is None:
                return None
            if not isinstance(value, Mapping):
                raise ValueError("persisted semantic sidecar must be an object")
            return SemanticSidecar(
                literal_description=value.get("literal_description"),
                observable_entities=tuple(value.get("observable_entities", ())),
                observable_relationships=tuple(
                    value.get("observable_relationships", ())
                ),
                objects_actions=tuple(value.get("objects_actions", ())),
                inferred_context=tuple(value.get("inferred_context", ())),
                search_terms=tuple(value.get("search_terms", ())),
                uncertainty=tuple(value.get("uncertainty", ())),
                model_provider=value.get("model_provider"),
                model_version=value.get("model_version"),
                input_refs=tuple(value.get("input_refs", ())),
            )

        def restore_media(value: object) -> CollectedMedia:
            if not isinstance(value, Mapping):
                raise ValueError("persisted media must be an object")
            regions = []
            for raw_region in value.get("ocr_regions", ()):
                if not isinstance(raw_region, Mapping):
                    raise ValueError("persisted OCR region must be an object")
                regions.append(
                    OcrRegion(
                        ordinal=raw_region.get("ordinal"),
                        text=raw_region.get("text"),
                        bounding_box=tuple(raw_region.get("bounding_box", ())),
                        confidence=raw_region.get("confidence"),
                    )
                )
            return CollectedMedia(
                source_url=value.get("source_url"),
                content=stored_bytes(value),
                mime_type=value.get("mime_type"),
                media_kind=value.get("media_kind"),
                alt_text=value.get("alt_text"),
                ocr_regions=tuple(regions),
                detected_language=value.get("detected_language"),
                ocr_engine=value.get("ocr_engine"),
                ocr_engine_version=value.get("ocr_engine_version"),
                semantic_sidecar=restore_sidecar(value.get("semantic_sidecar")),
            )

        items = []
        for raw_item in payload.get("items", ()):
            if not isinstance(raw_item, Mapping):
                raise ValueError("persisted provider item must be an object")
            items.append(
                CollectedItem(
                    source_native_id=raw_item.get("source_native_id"),
                    url=raw_item.get("url"),
                    title=raw_item.get("title"),
                    text=raw_item.get("text"),
                    author=raw_item.get("author"),
                    published_at=raw_item.get("published_at"),
                    media=tuple(
                        restore_media(media) for media in raw_item.get("media", ())
                    ),
                    metadata=raw_item.get("metadata"),
                )
            )
        rendered = payload.get("rendered_page")
        return ProviderResult(
            status=payload.get("status"),
            items=tuple(items),
            usage=dict(payload.get("usage", {})),
            failure_class=payload.get("failure_class"),
            safe_error_code=payload.get("safe_error_code"),
            failure_stage=payload.get("failure_stage"),
            failure_reason_code=payload.get("failure_reason_code"),
            failure_signature=payload.get("failure_signature"),
            page_signals=tuple(payload.get("page_signals", ())),
            rendered_page=stored_bytes(rendered) if rendered is not None else None,
            rendered_page_mime_type=(
                rendered.get("mime_type") if isinstance(rendered, Mapping) else None
            ),
            operator_url=payload.get("operator_url"),
            outcome_counts=dict(payload.get("outcome_counts", {})),
            browser_operations=tuple(payload.get("browser_operations", ())),
            rejection_counts=dict(payload.get("rejection_counts", {})),
        )

    def _event(
        self,
        conn: sqlite3.Connection,
        *,
        tick_id: str,
        event_type: str,
        attempt_id: str,
        lane_id: str | None = None,
        payload: Mapping[str, object] | None = None,
    ) -> None:
        sequence = int(
            conn.execute(
                """SELECT COALESCE(MAX(sequence), 0) + 1
                   FROM service_tick_events WHERE tick_id = ?""",
                (tick_id,),
            ).fetchone()[0]
        )
        conn.execute(
            """INSERT INTO service_tick_events (
                   event_id, tick_id, sequence, event_type,
                   execution_attempt_id, lane_id, payload_json, occurred_at
               ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                _stable_id("tick-event", {"tick_id": tick_id, "sequence": sequence}),
                tick_id,
                sequence,
                event_type,
                attempt_id,
                lane_id,
                _canonical_json(dict(payload or {})),
                _now(self.clock)[1],
            ),
        )

    def _claim(self, conn: sqlite3.Connection, tick: sqlite3.Row) -> str:
        attempt = conn.execute(
            """SELECT * FROM service_tick_attempts
               WHERE tick_id = ? ORDER BY attempt DESC LIMIT 1""",
            (tick["tick_id"],),
        ).fetchone()
        if attempt is None or attempt["state"] != "queued":
            raise RuntimeError("tick does not have a queued execution attempt")
        now_dt, now = _now(self.clock)
        config = json.loads(tick["config_json"])
        wall_limit = int(config["tick"]["aggregate_limits"]["wall_seconds"])
        expires = (now_dt + timedelta(seconds=wall_limit)).isoformat().replace(
            "+00:00", "Z"
        )
        updated = conn.execute(
            """UPDATE service_tick_attempts
               SET state = 'running', started_at = ?, lease_owner = 'tick-runner',
                   lease_generation = lease_generation + 1,
                   lease_expires_at = ?
               WHERE execution_attempt_id = ? AND state = 'queued'""",
            (now, expires, attempt["execution_attempt_id"]),
        )
        if updated.rowcount != 1:
            raise RuntimeError("tick attempt claim lost")
        conn.execute(
            "UPDATE service_ticks SET state = 'preflight', updated_at = ? WHERE tick_id = ?",
            (now, tick["tick_id"]),
        )
        self._event(
            conn,
            tick_id=tick["tick_id"],
            event_type="preflight_started",
            attempt_id=attempt["execution_attempt_id"],
        )
        return str(attempt["execution_attempt_id"])

    def _stage(
        self,
        conn: sqlite3.Connection,
        *,
        tick_id: str,
        stage_name: str,
        state: str,
        attempt_id: str,
        lane_id: str | None,
    ) -> None:
        now = _now(self.clock)[1]
        conn.execute(
            """UPDATE service_tick_stages
               SET state = ?, execution_attempt_id = ?,
                   started_at = CASE WHEN ? = 'running'
                                     THEN COALESCE(started_at, ?) ELSE started_at END,
                   completed_at = CASE WHEN ? NOT IN ('pending', 'running')
                                       THEN ? ELSE completed_at END,
                   updated_at = ?
               WHERE tick_id = ? AND stage_name = ?
                 AND ((? IS NULL AND lane_id IS NULL) OR lane_id = ?)""",
            (
                state,
                attempt_id,
                state,
                now,
                state,
                now,
                now,
                tick_id,
                stage_name,
                lane_id,
                lane_id,
            ),
        )

    def _consume(
        self,
        conn: sqlite3.Connection,
        *,
        tick_id: str,
        provider_manifest_id: str,
        attempt_id: str,
        provider_attempt_id: str,
        usage: Mapping[str, int],
    ) -> None:
        budgets = conn.execute(
            """SELECT * FROM service_tick_budgets
               WHERE tick_id = ? AND (
                   (scope_kind = 'tick' AND scope_id = ?)
                   OR (scope_kind = 'provider' AND scope_id = ?)
               ) ORDER BY scope_kind""",
            (tick_id, tick_id, provider_manifest_id),
        ).fetchall()
        if len(budgets) != 2:
            raise RuntimeError("tick/provider budgets are incomplete")
        now = _now(self.clock)[1]
        for budget in budgets:
            idempotency_key = f"usage:{provider_attempt_id}"
            if conn.execute(
                """SELECT 1 FROM service_tick_budget_events
                   WHERE budget_id = ? AND idempotency_key = ?""",
                (budget["budget_id"], idempotency_key),
            ).fetchone():
                continue
            limits = json.loads(budget["limit_json"])
            consumed = json.loads(budget["consumed_json"])
            resulting = {
                field: int(consumed[field]) + int(usage[field])
                for field in sorted(_USAGE_FIELDS)
            }
            exceeded = [
                field for field in sorted(_USAGE_FIELDS)
                if resulting[field] > int(limits[field])
            ]
            if exceeded:
                raise TickBudgetExceeded(
                    f"{budget['scope_kind']} budget exceeded: {', '.join(exceeded)}"
                )
            conn.execute(
                """UPDATE service_tick_budgets
                   SET consumed_json = ?, updated_at = ? WHERE budget_id = ?""",
                (_canonical_json(resulting), now, budget["budget_id"]),
            )
            conn.execute(
                """INSERT INTO service_tick_budget_events (
                       budget_event_id, tick_id, budget_id, execution_attempt_id,
                       provider_attempt_id, delta_json, resulting_consumed_json,
                       idempotency_key, created_at
                   ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    _stable_id(
                        "budget-event",
                        {"budget_id": budget["budget_id"], "key": idempotency_key},
                    ),
                    tick_id,
                    budget["budget_id"],
                    attempt_id,
                    provider_attempt_id,
                    _canonical_json(dict(usage)),
                    _canonical_json(resulting),
                    idempotency_key,
                    now,
                ),
            )

    def _admitted_limits(
        self,
        conn: sqlite3.Connection,
        *,
        tick_id: str,
        provider_manifest_id: str,
    ) -> dict[str, int]:
        budgets = conn.execute(
            """SELECT * FROM service_tick_budgets
               WHERE tick_id = ? AND (
                   (scope_kind = 'tick' AND scope_id = ?)
                   OR (scope_kind = 'provider' AND scope_id = ?)
               ) ORDER BY scope_kind""",
            (tick_id, tick_id, provider_manifest_id),
        ).fetchall()
        if len(budgets) != 2:
            raise RuntimeError("tick/provider budgets are incomplete")
        remaining_by_budget = []
        for budget in budgets:
            limits = json.loads(budget["limit_json"])
            consumed = json.loads(budget["consumed_json"])
            remaining_by_budget.append(
                {
                    field: int(limits[field]) - int(consumed[field])
                    for field in _USAGE_FIELDS
                }
            )
        admitted = {
            field: min(remaining[field] for remaining in remaining_by_budget)
            for field in _USAGE_FIELDS
        }
        if admitted["attempts"] < 1:
            raise TickBudgetAdmissionExhausted("attempt budget is exhausted")
        return admitted

    def _acquire_resources(
        self,
        conn: sqlite3.Connection,
        *,
        tick_id: str,
        lane_id: str,
        provider_attempt_id: str,
        resource_keys: Sequence[str],
        lease_expires_at: str,
    ) -> None:
        now = _now(self.clock)[1]
        for resource_key in resource_keys:
            identity = {
                "provider_attempt_id": provider_attempt_id,
                "resource_key": resource_key,
            }
            try:
                conn.execute(
                    """INSERT INTO service_tick_resource_leases (
                           lease_id, tick_id, lane_id, provider_attempt_id,
                           resource_key, lease_owner, lease_generation,
                           acquired_at, lease_expires_at
                       ) VALUES (?, ?, ?, ?, ?, 'tick-runner', 1, ?, ?)""",
                    (
                        _stable_id("resource-lease", identity),
                        tick_id,
                        lane_id,
                        provider_attempt_id,
                        resource_key,
                        now,
                        lease_expires_at,
                    ),
                )
            except sqlite3.IntegrityError as exc:
                raise RuntimeError(f"resource is already leased: {resource_key}") from exc

    def _release_resources(
        self, conn: sqlite3.Connection, *, provider_attempt_id: str
    ) -> None:
        conn.execute(
            """UPDATE service_tick_resource_leases SET released_at = ?
               WHERE provider_attempt_id = ? AND released_at IS NULL""",
            (_now(self.clock)[1], provider_attempt_id),
        )

    def _provider_attempt(
        self,
        conn: sqlite3.Connection,
        *,
        tick: sqlite3.Row,
        lane: sqlite3.Row,
        provider: sqlite3.Row,
        attempt_id: str,
        retry_ordinal: int,
    ) -> tuple[
        str,
        ProviderResult,
        list[SnapshotEntry],
        list[tuple[CollectedMedia, str]],
    ]:
        prior = conn.execute(
            """SELECT p.*, r.result_json, r.result_digest AS staged_result_digest
               FROM service_tick_provider_attempts AS p
               JOIN service_tick_provider_results AS r
                 ON r.provider_attempt_id = p.provider_attempt_id
               WHERE p.lane_id = ? AND p.provider_manifest_id = ?
                 AND p.retry_ordinal = ?
               ORDER BY p.started_at, p.provider_attempt_id LIMIT 1""",
            (
                lane["lane_id"],
                provider["provider_manifest_id"],
                retry_ordinal,
            ),
        ).fetchone()
        if prior is not None:
            payload = json.loads(prior["result_json"])
            if not isinstance(payload, dict) or _digest(payload) != prior[
                "staged_result_digest"
            ]:
                raise ValueError("persisted provider result digest mismatch")
            if prior["result_digest"] != prior["staged_result_digest"]:
                raise ValueError("provider attempt result digest mismatch")
            observed = self._restore_provider_result(payload)
            return self._finalize_provider_result(
                conn,
                tick=tick,
                lane=lane,
                provider_attempt_id=str(prior["provider_attempt_id"]),
                observed=observed,
                attempt_id=attempt_id,
                emit_raw_event=prior["state"] == "result_staged",
            )

        admitted_limits = self._admitted_limits(
            conn,
            tick_id=str(tick["tick_id"]),
            provider_manifest_id=str(provider["provider_manifest_id"]),
        )
        provider_attempt_id = _stable_id(
            "provider-attempt",
            {
                "execution_attempt_id": attempt_id,
                "lane_id": lane["lane_id"],
                "provider_manifest_id": provider["provider_manifest_id"],
                "retry_ordinal": retry_ordinal,
            },
        )
        now = _now(self.clock)[1]
        conn.execute(
            """INSERT INTO service_tick_provider_attempts (
                   provider_attempt_id, tick_id, lane_id, provider_manifest_id,
                   execution_attempt_id, retry_ordinal, state, started_at
               ) VALUES (?, ?, ?, ?, ?, ?, 'running', ?)""",
            (
                provider_attempt_id,
                tick["tick_id"],
                lane["lane_id"],
                provider["provider_manifest_id"],
                attempt_id,
                retry_ordinal,
                now,
            ),
        )
        attempt = conn.execute(
            """SELECT lease_expires_at FROM service_tick_attempts
               WHERE execution_attempt_id = ?""",
            (attempt_id,),
        ).fetchone()
        resources = tuple(json.loads(provider["resource_keys_json"]))
        self._acquire_resources(
            conn,
            tick_id=tick["tick_id"],
            lane_id=lane["lane_id"],
            provider_attempt_id=provider_attempt_id,
            resource_keys=resources,
            lease_expires_at=attempt["lease_expires_at"],
        )
        conn.commit()
        service = json.loads(lane["service_config_json"])
        target = json.loads(lane["target_config_json"])
        context = ProviderContext(
            tick_id=str(tick["tick_id"]),
            execution_attempt_id=attempt_id,
            lane_id=str(lane["lane_id"]),
            service_id=str(lane["service_id"]),
            source=str(service["source"]),
            target_id=str(lane["target_id"]),
            selector=dict(target["selector"]),
            access_partition_id=str(lane["access_partition_id"]),
            retention_class=str(target["retention_class"]),
            provider_id=str(provider["provider_id"]),
            adapter_type=str(provider["adapter_type"]),
            limits=admitted_limits,
            interval_from=str(tick["interval_from"]),
            interval_to=str(tick["interval_to"]),
            surface_kind=str(target["surface_kind"]),
        )
        spec = self.registry.require(
            context.adapter_type, source=context.source, capability="collect"
        )
        observed = spec.collect(context)
        if not isinstance(observed, ProviderResult):
            raise TypeError("adapter runner must return ProviderResult")
        exceeded = [
            field
            for field in sorted(_USAGE_FIELDS)
            if int(observed.usage[field]) > int(admitted_limits[field])
        ]
        if exceeded:
            raise RuntimeError(
                "adapter exceeded admitted limits: " + ", ".join(exceeded)
            )
        serialized = self._serialize_provider_result(
            observed, access_partition_id=str(lane["access_partition_id"])
        )
        serialized_digest = _digest(serialized)
        conn.execute("BEGIN IMMEDIATE")
        try:
            self._consume(
                conn,
                tick_id=tick["tick_id"],
                provider_manifest_id=provider["provider_manifest_id"],
                attempt_id=attempt_id,
                provider_attempt_id=provider_attempt_id,
                usage=observed.usage,
            )
            conn.execute(
                """INSERT INTO service_tick_provider_results (
                       provider_attempt_id, tick_id, lane_id, result_json,
                       result_digest, created_at
                   ) VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    provider_attempt_id,
                    tick["tick_id"],
                    lane["lane_id"],
                    _canonical_json(serialized),
                    serialized_digest,
                    _now(self.clock)[1],
                ),
            )
            conn.execute(
                """UPDATE service_tick_provider_attempts
                   SET state = 'result_staged', failure_class = NULL,
                       result_digest = ?, outcome_counts_json = ?
                   WHERE provider_attempt_id = ?""",
                (
                    serialized_digest,
                    _canonical_json(observed.outcome_counts),
                    provider_attempt_id,
                ),
            )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        self.fault_injector("provider_result_staged")
        return self._finalize_provider_result(
            conn,
            tick=tick,
            lane=lane,
            provider_attempt_id=provider_attempt_id,
            observed=observed,
            attempt_id=attempt_id,
            emit_raw_event=True,
        )

    def _finalize_provider_result(
        self,
        conn: sqlite3.Connection,
        *,
        tick: sqlite3.Row,
        lane: sqlite3.Row,
        provider_attempt_id: str,
        observed: ProviderResult,
        attempt_id: str,
        emit_raw_event: bool,
    ) -> tuple[
        str,
        ProviderResult,
        list[SnapshotEntry],
        list[tuple[CollectedMedia, str]],
    ]:
        entries: list[SnapshotEntry] = []
        media_work: list[tuple[CollectedMedia, str]] = []
        conn.execute("BEGIN IMMEDIATE")
        try:
            if observed.status in {"success", "partial"}:
                entries, media_work = self._publish_raw(
                    conn,
                    tick=tick,
                    lane=lane,
                    provider_attempt_id=provider_attempt_id,
                    result=observed,
                    attempt_id=attempt_id,
                    emit_event=emit_raw_event,
                )
            attempt_state = observed.status
            if observed.status == "partial":
                incident_type = classify_provider_issue(
                    observed.safe_error_code, observed.page_signals
                )
                attempt_state = (
                    "blocked_human"
                    if incident_type in _BLOCKING_INCIDENTS
                    else "failure"
                )
            conn.execute(
                """UPDATE service_tick_provider_attempts
                   SET state = ?, failure_class = ?, outcome_counts_json = ?,
                       completed_at = ? WHERE provider_attempt_id = ?""",
                (
                    attempt_state,
                    observed.failure_class,
                    _canonical_json(observed.outcome_counts),
                    _now(self.clock)[1],
                    provider_attempt_id,
                ),
            )
            self._release_resources(conn, provider_attempt_id=provider_attempt_id)
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        self.fault_injector("provider_raw_committed")
        return provider_attempt_id, observed, entries, media_work

    def _publish_raw(
        self,
        conn: sqlite3.Connection,
        *,
        tick: sqlite3.Row,
        lane: sqlite3.Row,
        provider_attempt_id: str,
        result: ProviderResult,
        attempt_id: str,
        emit_event: bool = True,
    ) -> tuple[list[SnapshotEntry], list[tuple[CollectedMedia, str]]]:
        service = json.loads(lane["service_config_json"])
        target = json.loads(lane["target_config_json"])
        source = str(service["source"])
        observed_at = _now(self.clock)[1]
        entries: list[SnapshotEntry] = []
        media_work: list[tuple[CollectedMedia, str]] = []
        for item in result.items:
            record_identity = {
                "service_id": lane["service_id"],
                "source_native_id": item.source_native_id,
                "access_partition_id": lane["access_partition_id"],
            }
            record_id = _stable_id("source-record", record_identity)
            media_manifest = [
                {
                    "source_url": media.source_url,
                    "content_hash": "sha256:"
                    + hashlib.sha256(media.content).hexdigest(),
                    "media_kind": media.media_kind,
                    "alt_text": media.alt_text,
                }
                for media in item.media
            ]
            version_payload = {
                "title": item.title,
                "text": item.text,
                "author": item.author,
                "published_at": item.published_at,
                "metadata": item.metadata or {},
                "media": media_manifest,
            }
            content_hash = _digest(version_payload)
            version_id = _stable_id(
                "source-version",
                {"record_id": record_id, "content_hash": content_hash},
            )
            conn.execute(
                """INSERT OR IGNORE INTO service_source_records (
                       record_id, service_id, source, source_native_id,
                       canonical_url, access_partition_id, created_at
                   ) VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    record_id,
                    lane["service_id"],
                    source,
                    item.source_native_id,
                    item.url,
                    lane["access_partition_id"],
                    observed_at,
                ),
            )
            for media in item.media:
                self.media.store_asset_in_transaction(
                    conn,
                    parent_version_id=version_id,
                    source_url=media.source_url,
                    content=media.content,
                    mime_type=media.mime_type,
                    media_kind=media.media_kind,
                    alt_text=media.alt_text,
                    access_partition_id=str(lane["access_partition_id"]),
                    retention_class=str(target["retention_class"]),
                )
            conn.execute(
                """INSERT OR IGNORE INTO service_source_versions (
                       version_id, record_id, provider_attempt_id, content_hash,
                       title, normalized_text, author, published_at, metadata_json,
                       observed_at, access_partition_id, retention_class, created_at
                   ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    version_id,
                    record_id,
                    provider_attempt_id,
                    content_hash,
                    item.title,
                    item.text,
                    item.author,
                    item.published_at,
                    _canonical_json(
                        {**(item.metadata or {}), "media": media_manifest}
                    ),
                    observed_at,
                    lane["access_partition_id"],
                    target["retention_class"],
                    observed_at,
                ),
            )
            conn.execute(
                """UPDATE service_source_records SET current_version_id = ?
                   WHERE record_id = ?""",
                (version_id, record_id),
            )
            conn.execute(
                """INSERT OR IGNORE INTO service_source_sightings (
                       version_id, tick_id, lane_id, provider_attempt_id, observed_at
                   ) VALUES (?, ?, ?, ?, ?)""",
                (
                    version_id,
                    tick["tick_id"],
                    lane["lane_id"],
                    provider_attempt_id,
                    observed_at,
                ),
            )
            entries.append(
                SnapshotEntry(
                    entry_id=version_id,
                    channel="lexical_source",
                    source=source,
                    access_partition_id=str(lane["access_partition_id"]),
                    published_at=item.published_at or observed_at,
                    text=f"{item.title}\n{item.text}",
                    provenance={
                        "record_id": record_id,
                        "version_id": version_id,
                        "url": item.url,
                    },
                )
            )
            media_work.extend((media, version_id) for media in item.media)
        if emit_event:
            self._event(
                conn,
                tick_id=tick["tick_id"],
                event_type="raw_published",
                attempt_id=attempt_id,
                lane_id=lane["lane_id"],
                payload={
                    "item_count": len(result.items),
                    "provider_attempt_id": provider_attempt_id,
                },
            )
        return entries, media_work

    def _publish_media(
        self,
        *,
        tick: sqlite3.Row,
        lane: sqlite3.Row,
        source: str,
        media_work: Sequence[tuple[CollectedMedia, str]],
    ) -> tuple[list[SnapshotEntry], dict[str, str]]:
        target = json.loads(lane["target_config_json"])
        config = json.loads(tick["config_json"])
        analysis = config["analysis"]
        entries: list[SnapshotEntry] = []
        observed_states: dict[str, list[str]] = {"media": []}
        if analysis["ocr_enabled"]:
            observed_states["ocr"] = []
        if analysis["semantic_sidecars_enabled"]:
            observed_states["semantic_sidecar"] = []
        observed_at = _now(self.clock)[1]
        for media, version_id in media_work:
            try:
                asset = self.media.store_asset(
                    parent_version_id=version_id,
                    source_url=media.source_url,
                    content=media.content,
                    mime_type=media.mime_type,
                    media_kind=media.media_kind,
                    alt_text=media.alt_text,
                    access_partition_id=str(lane["access_partition_id"]),
                    retention_class=str(target["retention_class"]),
                )
            except Exception:
                observed_states["media"].append("failure")
                for stage_name in ("ocr", "semantic_sidecar"):
                    if stage_name in observed_states:
                        observed_states[stage_name].append("failure")
                continue
            observed_states["media"].append("success")
            if media.alt_text:
                entries.append(
                    SnapshotEntry(
                        entry_id=asset.asset_id,
                        channel="source_alt_text",
                        source=source,
                        access_partition_id=asset.access_partition_id,
                        published_at=observed_at,
                        text=media.alt_text,
                        provenance={
                            "version_id": version_id,
                            "asset_id": asset.asset_id,
                            "source_url": media.source_url,
                        },
                    )
                )
            analysis_input = MediaAnalysisInput(
                source_url=media.source_url,
                content=media.content,
                mime_type=media.mime_type,
                media_kind=media.media_kind,
                alt_text=media.alt_text,
                provided_ocr_regions=media.ocr_regions,
                provided_ocr_language=media.detected_language,
                provided_ocr_engine=media.ocr_engine,
                provided_ocr_engine_version=media.ocr_engine_version,
                provided_semantic_sidecar=media.semantic_sidecar,
            )
            ocr_receipt = None
            if analysis["ocr_enabled"]:
                ocr_adapter_type = str(analysis["ocr_adapter_type"])
                try:
                    proposed_ocr = self.analysis_registry.require(
                        ocr_adapter_type, capability="ocr"
                    ).analyze(analysis_input)
                    if not isinstance(proposed_ocr, OcrAnalysis):
                        raise TypeError("OCR adapter returned an invalid result")
                    ocr_receipt = self.media.publish_ocr(
                        asset.asset_id,
                        engine=proposed_ocr.engine,
                        engine_version=proposed_ocr.engine_version,
                        detected_language=proposed_ocr.detected_language,
                        regions=proposed_ocr.regions,
                    )
                    analysis_input = analysis_input.with_ocr(proposed_ocr)
                    observed_states["ocr"].append(ocr_receipt.state)
                    text = "\n".join(region.text for region in proposed_ocr.regions)
                    if text:
                        entries.append(
                            SnapshotEntry(
                                entry_id=ocr_receipt.derivative_id,
                                channel="ocr",
                                source=source,
                                access_partition_id=ocr_receipt.access_partition_id,
                                published_at=observed_at,
                                text=text,
                                provenance={
                                    "version_id": version_id,
                                    "asset_id": asset.asset_id,
                                    "derivative_id": ocr_receipt.derivative_id,
                                },
                            )
                        )
                except Exception as exc:
                    self.media.publish_failure(
                        asset.asset_id,
                        derivative_kind="ocr",
                        adapter_type=ocr_adapter_type,
                        safe_error_code=type(exc).__name__.casefold(),
                        input_refs=(asset.asset_id,),
                    )
                    observed_states["ocr"].append("failure")
            if analysis["semantic_sidecars_enabled"]:
                sidecar_adapter_type = str(
                    analysis["semantic_sidecar_adapter_type"]
                )
                input_refs = [asset.asset_id]
                if ocr_receipt is not None:
                    input_refs.append(ocr_receipt.derivative_id)
                if media.alt_text:
                    input_refs.append(f"source-alt-text:{asset.asset_id}")
                try:
                    proposed = self.analysis_registry.require(
                        sidecar_adapter_type, capability="semantic_sidecar"
                    ).analyze(analysis_input)
                    if not isinstance(proposed, SemanticSidecar):
                        raise TypeError(
                            "semantic sidecar adapter returned an invalid result"
                        )
                    sidecar = SemanticSidecar(
                        literal_description=proposed.literal_description,
                        observable_entities=proposed.observable_entities,
                        observable_relationships=proposed.observable_relationships,
                        objects_actions=proposed.objects_actions,
                        inferred_context=proposed.inferred_context,
                        search_terms=proposed.search_terms,
                        uncertainty=proposed.uncertainty,
                        model_provider=proposed.model_provider,
                        model_version=proposed.model_version,
                        input_refs=tuple(input_refs),
                    )
                    receipt = self.media.publish_sidecar(asset.asset_id, sidecar)
                    observed_states["semantic_sidecar"].append(receipt.state)
                    entries.append(
                        SnapshotEntry(
                            entry_id=receipt.derivative_id,
                            channel="semantic_sidecar",
                            source=source,
                            access_partition_id=receipt.access_partition_id,
                            published_at=observed_at,
                            text="\n".join(
                                (
                                    sidecar.literal_description,
                                    *sidecar.search_terms,
                                    *sidecar.inferred_context,
                                )
                            ),
                            provenance={
                                "version_id": version_id,
                                "asset_id": asset.asset_id,
                                "derivative_id": receipt.derivative_id,
                                "input_refs": list(sidecar.input_refs),
                            },
                        )
                    )
                except Exception as exc:
                    self.media.publish_failure(
                        asset.asset_id,
                        derivative_kind="semantic_sidecar",
                        adapter_type=sidecar_adapter_type,
                        safe_error_code=type(exc).__name__.casefold(),
                        input_refs=tuple(input_refs),
                    )
                    observed_states["semantic_sidecar"].append("failure")

        stage_states: dict[str, str] = {}
        for stage_name, states in observed_states.items():
            if "failure" in states:
                stage_states[stage_name] = "failure"
            elif "success" in states:
                stage_states[stage_name] = "success"
            elif "empty" in states or not states:
                stage_states[stage_name] = "empty"
            else:
                stage_states[stage_name] = "unsupported"
        return entries, stage_states

    def _snapshot_entries_for_tick(self, tick_id: str) -> list[SnapshotEntry]:
        conn = self._connect()
        try:
            source_rows = conn.execute(
                """SELECT DISTINCT v.version_id, v.title, v.normalized_text,
                          v.published_at, v.access_partition_id, s.observed_at,
                          r.record_id, r.source, r.canonical_url
                   FROM service_source_sightings AS s
                   JOIN service_source_versions AS v ON v.version_id = s.version_id
                   JOIN service_source_records AS r ON r.record_id = v.record_id
                   WHERE s.tick_id = ?
                   ORDER BY v.version_id""",
                (tick_id,),
            ).fetchall()
            asset_rows = conn.execute(
                """SELECT DISTINCT a.asset_id, a.parent_version_id, a.source_url,
                          a.alt_text, a.access_partition_id, a.created_at, r.source
                   FROM service_media_assets AS a
                   JOIN service_source_versions AS v
                     ON v.version_id = a.parent_version_id
                   JOIN service_source_sightings AS s
                     ON s.version_id = v.version_id
                   JOIN service_source_records AS r ON r.record_id = v.record_id
                   WHERE s.tick_id = ? AND a.alt_text IS NOT NULL
                   ORDER BY a.asset_id""",
                (tick_id,),
            ).fetchall()
            derivative_rows = conn.execute(
                """SELECT DISTINCT d.derivative_id, d.derivative_kind,
                          d.output_json, d.access_partition_id, d.created_at,
                          a.asset_id, a.parent_version_id, r.source
                   FROM service_media_derivatives AS d
                   JOIN service_media_assets AS a ON a.asset_id = d.asset_id
                   JOIN service_source_versions AS v
                     ON v.version_id = a.parent_version_id
                   JOIN service_source_sightings AS s
                     ON s.version_id = v.version_id
                   JOIN service_source_records AS r ON r.record_id = v.record_id
                   WHERE s.tick_id = ? AND d.state = 'success'
                   ORDER BY d.derivative_id""",
                (tick_id,),
            ).fetchall()
        finally:
            conn.close()

        entries = [
            SnapshotEntry(
                entry_id=str(row["version_id"]),
                channel="lexical_source",
                source=str(row["source"]),
                access_partition_id=str(row["access_partition_id"]),
                published_at=str(row["published_at"] or row["observed_at"]),
                text=f'{row["title"]}\n{row["normalized_text"]}',
                provenance={
                    "record_id": str(row["record_id"]),
                    "version_id": str(row["version_id"]),
                    "url": str(row["canonical_url"]),
                },
            )
            for row in source_rows
        ]
        entries.extend(
            SnapshotEntry(
                entry_id=str(row["asset_id"]),
                channel="source_alt_text",
                source=str(row["source"]),
                access_partition_id=str(row["access_partition_id"]),
                published_at=str(row["created_at"]),
                text=str(row["alt_text"]),
                provenance={
                    "version_id": str(row["parent_version_id"]),
                    "asset_id": str(row["asset_id"]),
                    "source_url": str(row["source_url"]),
                },
            )
            for row in asset_rows
        )
        for row in derivative_rows:
            output = json.loads(row["output_json"])
            if not isinstance(output, dict):
                raise ValueError("persisted derivative output must be an object")
            if row["derivative_kind"] == "ocr":
                channel = "ocr"
                text = str(output.get("normalized_full_text") or "")
                provenance: dict[str, object] = {
                    "version_id": str(row["parent_version_id"]),
                    "asset_id": str(row["asset_id"]),
                    "derivative_id": str(row["derivative_id"]),
                }
            elif row["derivative_kind"] == "semantic_sidecar":
                channel = "semantic_sidecar"
                text = "\n".join(
                    str(value)
                    for value in (
                        output.get("literal_description"),
                        *output.get("search_terms", ()),
                        *output.get("inferred_context", ()),
                    )
                    if value
                )
                provenance = {
                    "version_id": str(row["parent_version_id"]),
                    "asset_id": str(row["asset_id"]),
                    "derivative_id": str(row["derivative_id"]),
                    "input_refs": list(output.get("input_refs", ())),
                }
            else:
                continue
            if text:
                entries.append(
                    SnapshotEntry(
                        entry_id=str(row["derivative_id"]),
                        channel=channel,
                        source=str(row["source"]),
                        access_partition_id=str(row["access_partition_id"]),
                        published_at=str(row["created_at"]),
                        text=text,
                        provenance=provenance,
                    )
                )
        return entries

    def _publish_catalog(
        self, *, tick_id: str, entries: Sequence[SnapshotEntry]
    ) -> list[SnapshotEntry]:
        groups: dict[tuple[str, str], list[SnapshotEntry]] = {}
        for entry in entries:
            if entry.channel != "lexical_source":
                continue
            normalized_text = " ".join(entry.text.casefold().split())
            identity = _digest({"normalized_text": normalized_text})
            groups.setdefault((entry.access_partition_id, identity), []).append(entry)

        catalog_entries: list[SnapshotEntry] = []
        for (partition, _), candidates in sorted(groups.items()):
            sources = {entry.source for entry in candidates}
            if len(sources) < 2:
                continue
            members = tuple(
                CatalogMember(
                    member_id=entry.entry_id,
                    source=entry.source,
                    relationship="exact_normalized_text",
                    evidence_ref=str(
                        entry.provenance.get("url") or entry.entry_id
                    ),
                    access_partition_id=partition,
                    confidence=1.0,
                )
                for entry in sorted(
                    candidates, key=lambda item: (item.source, item.entry_id)
                )
            )
            label = candidates[0].text.splitlines()[0][:1_024]
            rationale = (
                "Deterministic exact normalized-text match across "
                f"{len(sources)} services."
            )
            cluster_id = self.snapshots.publish_cluster(
                tick_id,
                cluster_kind="exact_duplicate",
                label=label,
                rationale=rationale,
                validator_version="exact-normalized-text-v1",
                members=members,
            )
            catalog_entries.append(
                SnapshotEntry(
                    entry_id=cluster_id,
                    channel="catalog",
                    source="catalog",
                    access_partition_id=partition,
                    published_at=max(entry.published_at for entry in candidates),
                    text=f"{label}\n{rationale}",
                    provenance={
                        "version_id": cluster_id,
                        "cluster_id": cluster_id,
                        "member_version_ids": [
                            member.member_id for member in members
                        ],
                        "member_sources": sorted(sources),
                    },
                )
            )
        return catalog_entries

    def _incident(
        self,
        *,
        tick: sqlite3.Row,
        lane: sqlite3.Row,
        source: str,
        result: ProviderResult,
    ) -> str | None:
        incident_type = classify_provider_issue(
            result.safe_error_code, result.page_signals
        )
        if incident_type is None:
            return None
        receipt = self.incidents.record(
            IncidentSignal(
                tick_id=str(tick["tick_id"]),
                lane_id=str(lane["lane_id"]),
                source=source,
                profile_ref=str(lane["access_partition_id"]),
                stage="collection",
                incident_type=incident_type,
                severity=(
                    "warning" if incident_type == "rate_limit_warning" else "critical"
                ),
                safe_summary=provider_issue_summary(
                    result.safe_error_code, incident_type
                ),
                access_partition_id=str(lane["access_partition_id"]),
                rendered_page=result.rendered_page,
                rendered_page_mime_type=result.rendered_page_mime_type,
                operator_url=result.operator_url,
            )
        )
        try:
            config = json.loads(tick["config_json"])
            self.incidents.notify(
                receipt.incident_id,
                self.notification_transports,
                reminder_seconds=int(config["notifications"]["reminder_seconds"]),
            )
        except NotificationExhaustedError:
            pass
        return incident_type

    def _evaluate_anomalies(
        self,
        *,
        tick: sqlite3.Row,
        lane: sqlite3.Row,
        source: str,
        result: ProviderResult,
        provider_attempt_id: str,
    ) -> None:
        config = json.loads(tick["config_json"])
        rules = config["analysis"].get("anomaly_rules", [])
        if not rules:
            return
        item_count = len(result.items)
        metrics = {
            "yield_count": float(item_count),
            "rejection_rate": (
                result.outcome_counts["rejected"]
                / result.outcome_counts["observed"]
                if result.outcome_counts["observed"]
                else 0.0
            ),
            "latency_seconds": float(result.usage["wall_seconds"]),
            "missing_media_rate": (
                sum(not item.media for item in result.items) / item_count
                if item_count
                else 0.0
            ),
        }
        reminder_seconds = int(config["notifications"]["reminder_seconds"])
        for raw_rule in rules:
            rule = AnomalyRule.from_dict(raw_rule)
            evaluated = self.anomalies.record(
                tick_id=str(tick["tick_id"]),
                lane_id=str(lane["lane_id"]),
                source=source,
                profile_ref=str(lane["access_partition_id"]),
                rule=rule,
                current_value=metrics[rule.metric],
            )
            stage = f"anomaly:{rule.rule_id}"
            if evaluated.state in {"warning", "critical"}:
                receipt = self.incidents.record(
                    IncidentSignal(
                        tick_id=str(tick["tick_id"]),
                        lane_id=str(lane["lane_id"]),
                        source=source,
                        profile_ref=str(lane["access_partition_id"]),
                        stage=stage,
                        incident_type="provider_degraded",
                        severity=(
                            "warning" if evaluated.state == "warning" else "error"
                        ),
                        safe_summary=(
                            f"Deterministic anomaly rule {rule.rule_id} is "
                            f"{evaluated.state}."
                        ),
                        access_partition_id=str(lane["access_partition_id"]),
                    )
                )
                try:
                    self.incidents.notify(
                        receipt.incident_id,
                        self.notification_transports,
                        reminder_seconds=reminder_seconds,
                    )
                except NotificationExhaustedError:
                    pass
            elif evaluated.state == "healthy":
                try:
                    self.incidents.resolve_matching(
                        source=source,
                        profile_ref=str(lane["access_partition_id"]),
                        stage=stage,
                        successful_execution_id=provider_attempt_id,
                        transports=self.notification_transports,
                        reminder_seconds=reminder_seconds,
                    )
                except NotificationExhaustedError:
                    pass

    def _run_lane(
        self,
        *,
        tick: sqlite3.Row,
        lane: sqlite3.Row,
        attempt_id: str,
    ) -> tuple[str, list[SnapshotEntry]]:
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            self._stage(
                conn,
                tick_id=tick["tick_id"],
                stage_name="collection",
                state="running",
                attempt_id=attempt_id,
                lane_id=lane["lane_id"],
            )
            conn.commit()
        finally:
            conn.close()
        service = json.loads(lane["service_config_json"])
        source = str(service["source"])
        providers = None
        lane_stage_names: tuple[str, ...] = ()
        conn = self._connect()
        try:
            providers = conn.execute(
                """SELECT * FROM service_tick_providers
                   WHERE lane_id = ? ORDER BY provider_ordinal""",
                (lane["lane_id"],),
            ).fetchall()
            lane_stage_names = tuple(
                str(row["stage_name"])
                for row in conn.execute(
                    """SELECT stage_name FROM service_tick_stages
                       WHERE lane_id = ? ORDER BY stage_name""",
                    (lane["lane_id"],),
                ).fetchall()
            )
        finally:
            conn.close()
        ordinal = 0
        entries: list[SnapshotEntry] = []
        final_result: ProviderResult | None = None
        final_provider_attempt_id: str | None = None
        final_entries: list[SnapshotEntry] = []
        final_media_work: list[tuple[CollectedMedia, str]] = []
        budget_exhausted = False
        while ordinal < len(providers):
            provider = providers[ordinal]
            retry_ordinal = 0
            while True:
                conn = self._connect()
                try:
                    try:
                        (
                            provider_attempt_id,
                            result,
                            attempt_entries,
                            attempt_media_work,
                        ) = self._provider_attempt(
                            conn,
                            tick=tick,
                            lane=lane,
                            provider=provider,
                            attempt_id=attempt_id,
                            retry_ordinal=retry_ordinal,
                        )
                    except TickBudgetAdmissionExhausted:
                        budget_exhausted = True
                        break
                finally:
                    conn.close()
                if budget_exhausted:
                    break
                final_result = result
                final_provider_attempt_id = provider_attempt_id
                final_entries = attempt_entries
                final_media_work = attempt_media_work
                if (
                    result.status in {"success", "empty"}
                    and classify_provider_issue(
                        result.safe_error_code, result.page_signals
                    )
                    is None
                ):
                    config = json.loads(tick["config_json"])
                    self.incidents.resolve_matching(
                        source=source,
                        profile_ref=str(lane["access_partition_id"]),
                        stage="collection",
                        successful_execution_id=provider_attempt_id,
                        transports=self.notification_transports,
                        reminder_seconds=int(
                            config["notifications"]["reminder_seconds"]
                        ),
                    )
                    break
                if should_retry_provider(
                    {
                        "limits": json.loads(provider["limits_json"]),
                        "fallback_on": json.loads(provider["fallback_on_json"]),
                    },
                    failure_class=str(result.failure_class),
                    retry_ordinal=retry_ordinal,
                ):
                    retry_ordinal += 1
                    continue
                next_ordinal = next_provider_ordinal(
                    [
                        {"fallback_on": json.loads(row["fallback_on_json"])}
                        for row in providers
                    ],
                    current_ordinal=ordinal,
                    failure_class=str(result.failure_class),
                )
                if next_ordinal is not None:
                    ordinal = next_ordinal
                break
            if budget_exhausted:
                break
            if final_result is not None and final_result.status != "failure":
                break
            if ordinal == provider["provider_ordinal"]:
                break
        if budget_exhausted:
            conn = self._connect()
            try:
                conn.execute("BEGIN IMMEDIATE")
                for stage_name in lane_stage_names:
                    self._stage(
                        conn,
                        tick_id=tick["tick_id"],
                        stage_name=stage_name,
                        state="budget_exhausted",
                        attempt_id=attempt_id,
                        lane_id=lane["lane_id"],
                    )
                conn.execute(
                    """UPDATE service_tick_lanes SET state = 'budget_exhausted',
                           updated_at = ? WHERE lane_id = ?""",
                    (_now(self.clock)[1], lane["lane_id"]),
                )
                self._event(
                    conn,
                    tick_id=tick["tick_id"],
                    event_type="lane_budget_exhausted",
                    attempt_id=attempt_id,
                    lane_id=lane["lane_id"],
                )
                conn.commit()
                return "budget_exhausted", []
            except Exception:
                conn.rollback()
                raise
            finally:
                conn.close()
        if final_result is None or final_provider_attempt_id is None:
            raise RuntimeError("lane executed no provider")

        self._evaluate_anomalies(
            tick=tick,
            lane=lane,
            source=source,
            result=final_result,
            provider_attempt_id=final_provider_attempt_id,
        )

        lane_state = "failure"
        incident_type = self._incident(
            tick=tick, lane=lane, source=source, result=final_result
        )
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            if final_result.status in {"success", "partial"}:
                entries = final_entries
                media_work = final_media_work
                lane_state = (
                    "success"
                    if final_result.status == "success"
                    else "blocked_human"
                    if incident_type in _BLOCKING_INCIDENTS
                    else "failure"
                )
                self._stage(
                    conn,
                    tick_id=tick["tick_id"],
                    stage_name="collection",
                    state=lane_state,
                    attempt_id=attempt_id,
                    lane_id=lane["lane_id"],
                )
                conn.commit()
                derivative_entries, derivative_stage_states = self._publish_media(
                    tick=tick,
                    lane=lane,
                    source=source,
                    media_work=media_work,
                )
                entries.extend(derivative_entries)
                conn.execute("BEGIN IMMEDIATE")
                self._event(
                    conn,
                    tick_id=tick["tick_id"],
                    event_type="derivatives_published",
                    attempt_id=attempt_id,
                    lane_id=lane["lane_id"],
                    payload={
                        "entry_count": len(derivative_entries),
                        "stage_states": derivative_stage_states,
                    },
                )
                for stage_name, stage_state in derivative_stage_states.items():
                    self._stage(
                        conn,
                        tick_id=tick["tick_id"],
                        stage_name=stage_name,
                        state=stage_state,
                        attempt_id=attempt_id,
                        lane_id=lane["lane_id"],
                    )
            elif final_result.status == "empty":
                lane_state = "empty"
                for stage_name in lane_stage_names:
                    self._stage(
                        conn,
                        tick_id=tick["tick_id"],
                        stage_name=stage_name,
                        state="empty",
                        attempt_id=attempt_id,
                        lane_id=lane["lane_id"],
                    )
            else:
                lane_state = (
                    "blocked_human"
                    if incident_type in _BLOCKING_INCIDENTS
                    else "failure"
                )
                for stage_name in lane_stage_names:
                    self._stage(
                        conn,
                        tick_id=tick["tick_id"],
                        stage_name=stage_name,
                        state=lane_state,
                        attempt_id=attempt_id,
                        lane_id=lane["lane_id"],
                    )
            conn.execute(
                """UPDATE service_tick_lanes SET state = ?, updated_at = ?
                   WHERE lane_id = ?""",
                (lane_state, _now(self.clock)[1], lane["lane_id"]),
            )
            conn.commit()
            return lane_state, entries
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _fail(self, tick_id: str, attempt_id: str, error_code: str) -> None:
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            now = _now(self.clock)[1]
            conn.execute(
                """UPDATE service_tick_resource_leases SET released_at = ?
                   WHERE released_at IS NULL AND provider_attempt_id IN (
                       SELECT provider_attempt_id FROM service_tick_provider_attempts
                       WHERE execution_attempt_id = ?
                   )""",
                (now, attempt_id),
            )
            conn.execute(
                """UPDATE service_tick_provider_attempts
                   SET state = 'failure', failure_class = 'integrity', completed_at = ?
                   WHERE execution_attempt_id = ? AND state = 'running'""",
                (now, attempt_id),
            )
            conn.execute(
                """UPDATE service_tick_stages SET state = 'failure',
                       completed_at = ?, updated_at = ?
                   WHERE tick_id = ? AND state IN ('pending', 'running')""",
                (now, now, tick_id),
            )
            conn.execute(
                """UPDATE service_tick_lanes SET state = 'failure', updated_at = ?
                   WHERE tick_id = ? AND state = 'ready'""",
                (now, tick_id),
            )
            conn.execute(
                "UPDATE service_ticks SET state = 'failed', updated_at = ? WHERE tick_id = ?",
                (now, tick_id),
            )
            conn.execute(
                """UPDATE service_tick_attempts SET state = 'failed',
                       completed_at = ?, error_code = ?, lease_owner = NULL,
                       lease_expires_at = NULL WHERE execution_attempt_id = ?""",
                (now, error_code[:64], attempt_id),
            )
            self._event(
                conn,
                tick_id=tick_id,
                event_type="tick_failed",
                attempt_id=attempt_id,
                payload={"error_code": error_code[:64]},
            )
            conn.commit()
        finally:
            conn.close()

    def run(self, tick_id: str) -> None:
        conn = self._connect()
        attempt_id = ""
        try:
            conn.execute("BEGIN IMMEDIATE")
            tick = conn.execute(
                "SELECT * FROM service_ticks WHERE tick_id = ?", (tick_id,)
            ).fetchone()
            if tick is None:
                raise KeyError(f"unknown tick: {tick_id}")
            if tick["state"] in _TICK_TERMINAL:
                conn.commit()
                return
            now = _now(self.clock)[1]
            active = conn.execute(
                """SELECT 1 FROM service_tick_attempts AS a
                   JOIN service_ticks AS t ON t.tick_id = a.tick_id
                   WHERE a.tick_id <> ? AND a.state = 'running'
                     AND (a.lease_expires_at IS NULL OR a.lease_expires_at > ?)
                     AND t.state NOT IN (
                         'complete', 'complete_degraded', 'failed',
                         'missed_due_to_overlap'
                     )
                   LIMIT 1""",
                (tick_id, now),
            ).fetchone()
            if active is not None:
                config = json.loads(tick["config_json"])
                lateness_seconds = int(config["tick"]["lateness_seconds"])
                interval_end = datetime.fromisoformat(
                    str(tick["interval_to"]).replace("Z", "+00:00")
                )
                now_dt = datetime.fromisoformat(now.replace("Z", "+00:00"))
                if (now_dt - interval_end).total_seconds() > lateness_seconds:
                    attempt = conn.execute(
                        """SELECT execution_attempt_id FROM service_tick_attempts
                           WHERE tick_id = ? AND state = 'queued'
                           ORDER BY attempt DESC LIMIT 1""",
                        (tick_id,),
                    ).fetchone()
                    if attempt is None:
                        raise RuntimeError("overlap tick lacks a queued attempt")
                    attempt_id = str(attempt["execution_attempt_id"])
                    conn.execute(
                        """UPDATE service_tick_attempts
                           SET state = 'missed_due_to_overlap', completed_at = ?,
                               error_code = 'missed_due_to_overlap'
                           WHERE execution_attempt_id = ?""",
                        (now, attempt_id),
                    )
                    conn.execute(
                        """UPDATE service_tick_stages
                           SET state = 'failure', completed_at = ?, updated_at = ?
                           WHERE tick_id = ? AND state = 'pending'""",
                        (now, now, tick_id),
                    )
                    conn.execute(
                        """UPDATE service_tick_lanes SET state = 'failure', updated_at = ?
                           WHERE tick_id = ? AND state = 'ready'""",
                        (now, tick_id),
                    )
                    conn.execute(
                        """UPDATE service_ticks
                           SET state = 'missed_due_to_overlap', updated_at = ?
                           WHERE tick_id = ?""",
                        (now, tick_id),
                    )
                    self._event(
                        conn,
                        tick_id=tick_id,
                        event_type="missed_due_to_overlap",
                        attempt_id=attempt_id,
                        payload={
                            "interval_from": tick["interval_from"],
                            "interval_to": tick["interval_to"],
                        },
                    )
                conn.commit()
                return
            attempt_id = self._claim(conn, tick)
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

        try:
            self.incidents.require_notification_readiness(
                self.notification_transports
            )
            conn = self._connect()
            try:
                conn.execute("BEGIN IMMEDIATE")
                tick = conn.execute(
                    "SELECT * FROM service_ticks WHERE tick_id = ?", (tick_id,)
                ).fetchone()
                frozen_config = json.loads(tick["config_json"])
                analysis = frozen_config["analysis"]
                if analysis["ocr_enabled"]:
                    self.analysis_registry.require(
                        str(analysis["ocr_adapter_type"]), capability="ocr"
                    )
                if analysis["semantic_sidecars_enabled"]:
                    self.analysis_registry.require(
                        str(analysis["semantic_sidecar_adapter_type"]),
                        capability="semantic_sidecar",
                    )
                conn.execute(
                    "UPDATE service_ticks SET state = 'collecting', updated_at = ? WHERE tick_id = ?",
                    (_now(self.clock)[1], tick_id),
                )
                lanes = conn.execute(
                    """SELECT * FROM service_tick_lanes
                       WHERE tick_id = ? ORDER BY service_id, target_id""",
                    (tick_id,),
                ).fetchall()
                lanes = order_lanes_by_target_config(lanes, frozen_config)
                conn.commit()
            finally:
                conn.close()
            all_entries: list[SnapshotEntry] = []
            lane_states: dict[str, str] = {}
            for lane in lanes:
                if lane["state"] == "ready":
                    state, entries = self._run_lane(
                        tick=tick, lane=lane, attempt_id=attempt_id
                    )
                    self.fault_injector("lane_completed")
                else:
                    state = str(lane["state"])
                    entries = []
                lane_states[str(lane["service_id"])] = state
                all_entries.extend(entries)

            all_entries = self._snapshot_entries_for_tick(tick_id)
            catalog_entries = self._publish_catalog(
                tick_id=tick_id, entries=all_entries
            )
            all_entries.extend(catalog_entries)

            conn = self._connect()
            try:
                conn.execute("BEGIN IMMEDIATE")
                now = _now(self.clock)[1]
                conn.execute(
                    "UPDATE service_ticks SET state = 'cataloging', updated_at = ? WHERE tick_id = ?",
                    (now, tick_id),
                )
                self._stage(
                    conn,
                    tick_id=tick_id,
                    stage_name="catalog",
                    state="success" if catalog_entries else "empty",
                    attempt_id=attempt_id,
                    lane_id=None,
                )
                conn.execute(
                    "UPDATE service_ticks SET state = 'indexing', updated_at = ? WHERE tick_id = ?",
                    (now, tick_id),
                )
                conn.commit()
            finally:
                conn.close()
            config = json.loads(tick["config_json"])
            snapshot = self.snapshots.stage(
                tick_id,
                embedding_space=str(config["query"]["embedding_space"]),
                fusion_version=str(config["query"]["fusion_version"]),
                completeness=lane_states,
            )
            self.snapshots.add_entries(snapshot.snapshot_id, all_entries)
            conn = self._connect()
            try:
                anomaly_degraded = bool(
                    conn.execute(
                        """SELECT 1 FROM service_tick_anomaly_results
                           WHERE tick_id = ? AND state IN ('warning', 'critical')
                           LIMIT 1""",
                        (tick_id,),
                    ).fetchone()
                )
                incident_degraded = bool(
                    conn.execute(
                        """SELECT 1 FROM service_incidents
                           WHERE last_tick_id = ? AND state <> 'resolved'
                           LIMIT 1""",
                        (tick_id,),
                    ).fetchone()
                )
                stage_degraded = bool(
                    conn.execute(
                        """SELECT 1 FROM service_tick_stages
                           WHERE tick_id = ?
                             AND state IN ('failure', 'blocked_human',
                                           'budget_exhausted')
                           LIMIT 1""",
                        (tick_id,),
                    ).fetchone()
                )
            finally:
                conn.close()
            degraded = anomaly_degraded or incident_degraded or stage_degraded or any(
                state not in {"success", "empty"} for state in lane_states.values()
            )
            terminal_state = "complete_degraded" if degraded else "complete"
            conn = self._connect()
            try:
                conn.execute("BEGIN IMMEDIATE")
                for stage_name in ("lexical_index", "semantic_index"):
                    self._stage(
                        conn,
                        tick_id=tick_id,
                        stage_name=stage_name,
                        state="success",
                        attempt_id=attempt_id,
                        lane_id=None,
                    )
                self._stage(
                    conn,
                    tick_id=tick_id,
                    stage_name="head_promotion",
                    state="running",
                    attempt_id=attempt_id,
                    lane_id=None,
                )
                conn.execute(
                    "UPDATE service_ticks SET state = ?, updated_at = ? WHERE tick_id = ?",
                    (terminal_state, _now(self.clock)[1], tick_id),
                )
                conn.commit()
            finally:
                conn.close()
            self.snapshots.promote(snapshot.snapshot_id)
            conn = self._connect()
            try:
                conn.execute("BEGIN IMMEDIATE")
                now = _now(self.clock)[1]
                self._stage(
                    conn,
                    tick_id=tick_id,
                    stage_name="head_promotion",
                    state="success",
                    attempt_id=attempt_id,
                    lane_id=None,
                )
                conn.execute(
                    """UPDATE service_tick_attempts SET state = 'complete',
                           completed_at = ?, lease_owner = NULL,
                           lease_expires_at = NULL WHERE execution_attempt_id = ?""",
                    (now, attempt_id),
                )
                self._event(
                    conn,
                    tick_id=tick_id,
                    event_type="tick_completed",
                    attempt_id=attempt_id,
                    payload={"state": terminal_state},
                )
                conn.commit()
            finally:
                conn.close()
        except Exception as exc:
            self._fail(tick_id, attempt_id, type(exc).__name__.casefold())
