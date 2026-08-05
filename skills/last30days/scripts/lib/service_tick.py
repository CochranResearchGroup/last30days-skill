"""Durable all-source tick coordination behind one small public interface."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from collections.abc import Callable, Mapping, Sequence
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import store

from . import service_contracts as contracts
from .service_tick_adapters import (
    AdapterRegistry,
    AdapterRegistryError,
    default_adapter_registry,
)


Clock = Callable[[], datetime]
_CONFIG_FIELDS = frozenset(
    {
        "schema_version",
        "config_revision",
        "services",
        "targets",
        "tick",
        "artifacts",
        "analysis",
        "notifications",
        "observation",
        "query",
    }
)
_REQUIRED_CONFIG_FIELDS = _CONFIG_FIELDS - {"observation"}
_ZERO_USAGE = {
    "attempts": 0,
    "network_requests": 0,
    "wall_seconds": 0,
    "items": 0,
    "cost_cents": 0,
    "model_tokens": 0,
}
_GLOBAL_STAGES = ("catalog", "head_promotion", "lexical_index", "semantic_index")
_BASE_LANE_STAGES = ("collection", "media")
_LIMIT_FIELDS = frozenset(
    {
        "attempts",
        "network_requests",
        "wall_seconds",
        "items",
        "cost_cents",
        "model_tokens",
    }
)
_FALLBACK_CLASSES = frozenset(
    {
        "transient",
        "authentication",
        "challenge",
        "rate_limit",
        "policy",
        "budget",
        "access_partition",
        "integrity",
        "configuration",
        "permanent",
    }
)


class TickConfigError(ValueError):
    """Raised when user-scoped tick configuration is not strict and safe."""


class TickIntegrityError(RuntimeError):
    """Raised before a corrupted immutable tick record can be consumed."""


def _canonical_json(value: object) -> str:
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def _digest(value: object) -> str:
    return "sha256:" + hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _stable_id(prefix: str, value: object) -> str:
    digest = hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()
    return f"{prefix}-{digest[:32]}"


def _bounded_text(value: object, field: str, maximum: int = 128) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > maximum:
        raise TickConfigError(f"{field} must be a bounded non-empty string")
    return value


def _object(value: object, field: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise TickConfigError(f"{field} must be an object")
    return dict(value)


def _array(value: object, field: str, *, maximum: int = 100_000) -> list[Any]:
    if not isinstance(value, list) or len(value) > maximum:
        raise TickConfigError(f"{field} must be a bounded array")
    return list(value)


def _exact_fields(
    value: object,
    field: str,
    *,
    required: frozenset[str],
    optional: frozenset[str] = frozenset(),
) -> dict[str, Any]:
    payload = _object(value, field)
    missing = sorted(required - payload.keys())
    unknown = sorted(payload.keys() - required - optional)
    if missing:
        raise TickConfigError(f"{field} missing fields: {', '.join(missing)}")
    if unknown:
        raise TickConfigError(f"{field} unknown fields: {', '.join(unknown)}")
    return payload


def _integer(
    value: object, field: str, *, minimum: int, maximum: int
) -> int:
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or not minimum <= value <= maximum
    ):
        raise TickConfigError(f"{field} must be between {minimum} and {maximum}")
    return value


def _positive_number(value: object, field: str) -> float:
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not 0 < float(value) <= 1_000_000
    ):
        raise TickConfigError(f"{field} must be a bounded positive number")
    return float(value)


def _string_list(
    value: object,
    field: str,
    *,
    maximum_items: int,
    maximum_length: int,
) -> tuple[str, ...]:
    values = _array(value, field, maximum=maximum_items)
    normalized = tuple(
        _bounded_text(item, f"{field}[{index}]", maximum_length)
        for index, item in enumerate(values)
    )
    if len(set(normalized)) != len(normalized):
        raise TickConfigError(f"{field} must not contain duplicates")
    return normalized


def _validate_limits(value: object, field: str, *, provider: bool) -> None:
    limits = _exact_fields(value, field, required=_LIMIT_FIELDS)
    _integer(
        limits["attempts"],
        f"{field}.attempts",
        minimum=1,
        maximum=2 if provider else 1_000,
    )
    _integer(
        limits["network_requests"],
        f"{field}.network_requests",
        minimum=0,
        maximum=1_000_000,
    )
    _integer(
        limits["wall_seconds"],
        f"{field}.wall_seconds",
        minimum=1,
        maximum=86_400,
    )
    _integer(limits["items"], f"{field}.items", minimum=0, maximum=1_000_000)
    _integer(
        limits["cost_cents"],
        f"{field}.cost_cents",
        minimum=0,
        maximum=10_000_000,
    )
    _integer(
        limits["model_tokens"],
        f"{field}.model_tokens",
        minimum=0,
        maximum=100_000_000,
    )


def _validate_observation_config(
    config: Mapping[str, Any],
) -> dict[str, Any] | None:
    raw_observation = config.get("observation")
    if raw_observation is None:
        return None
    observation = _exact_fields(
        raw_observation,
        "observation",
        required=frozenset({"adapter_type", "service_base_url"}),
    )
    if observation["adapter_type"] != "agent_browser_service":
        raise TickConfigError("observation.adapter_type is not installed")
    service_base_url = _bounded_text(
        observation["service_base_url"],
        "observation.service_base_url",
        4_096,
    )
    if any(
        ord(character) < 32 or ord(character) == 127
        for character in service_base_url
    ):
        raise TickConfigError("observation.service_base_url is invalid")
    try:
        parsed = urlparse(service_base_url)
        port = parsed.port
    except ValueError as exc:
        raise TickConfigError("observation.service_base_url is invalid") from exc
    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.hostname
        or (port is not None and not 1 <= port <= 65_535)
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
    ):
        raise TickConfigError("observation.service_base_url is invalid")
    return observation


def _validate_config_shape(config: Mapping[str, Any]) -> None:
    for service_index, raw_service in enumerate(
        _array(config["services"], "services", maximum=256)
    ):
        service_field = f"services[{service_index}]"
        service = _exact_fields(
            raw_service,
            service_field,
            required=frozenset({"service_id", "source", "providers"}),
        )
        _bounded_text(service["service_id"], f"{service_field}.service_id")
        _bounded_text(service["source"], f"{service_field}.source", 64)
        providers = _array(
            service["providers"], f"{service_field}.providers", maximum=16
        )
        if not providers:
            raise TickConfigError(f"{service_field}.providers must not be empty")
        for provider_index, raw_provider in enumerate(providers):
            provider_field = f"{service_field}.providers[{provider_index}]"
            provider = _exact_fields(
                raw_provider,
                provider_field,
                required=frozenset(
                    {
                        "provider_id",
                        "adapter_type",
                        "resource_keys",
                        "fallback_on",
                        "limits",
                    }
                ),
                optional=frozenset({"credential_ref"}),
            )
            _bounded_text(provider["provider_id"], f"{provider_field}.provider_id")
            _bounded_text(
                provider["adapter_type"], f"{provider_field}.adapter_type"
            )
            if "credential_ref" in provider:
                _bounded_text(
                    provider["credential_ref"],
                    f"{provider_field}.credential_ref",
                    256,
                )
            _string_list(
                provider["resource_keys"],
                f"{provider_field}.resource_keys",
                maximum_items=32,
                maximum_length=256,
            )
            fallback_on = _string_list(
                provider["fallback_on"],
                f"{provider_field}.fallback_on",
                maximum_items=16,
                maximum_length=64,
            )
            unknown_fallback = sorted(set(fallback_on) - _FALLBACK_CLASSES)
            if unknown_fallback:
                raise TickConfigError(
                    f"{provider_field}.fallback_on contains unknown classes: "
                    + ", ".join(unknown_fallback)
                )
            _validate_limits(
                provider["limits"], f"{provider_field}.limits", provider=True
            )

    targets = _array(config["targets"], "targets")
    if not targets:
        raise TickConfigError("targets must not be empty")
    for target_index, raw_target in enumerate(targets):
        target_field = f"targets[{target_index}]"
        target = _exact_fields(
            raw_target,
            target_field,
            required=frozenset(
                {
                    "target_id",
                    "service_id",
                    "surface_kind",
                    "selector",
                    "access_partition_id",
                    "retention_class",
                    "enabled",
                }
            ),
        )
        for key, maximum in (
            ("target_id", 128),
            ("service_id", 128),
            ("surface_kind", 64),
            ("access_partition_id", 256),
            ("retention_class", 64),
        ):
            _bounded_text(target[key], f"{target_field}.{key}", maximum)
        _object(target["selector"], f"{target_field}.selector")
        if not isinstance(target["enabled"], bool):
            raise TickConfigError(f"{target_field}.enabled must be boolean")

    tick = _exact_fields(
        config["tick"],
        "tick",
        required=frozenset({"timezone", "lateness_seconds", "aggregate_limits"}),
    )
    _bounded_text(tick["timezone"], "tick.timezone", 128)
    _integer(
        tick["lateness_seconds"],
        "tick.lateness_seconds",
        minimum=0,
        maximum=604_800,
    )
    _validate_limits(tick["aggregate_limits"], "tick.aggregate_limits", provider=False)

    artifacts = _exact_fields(
        config["artifacts"],
        "artifacts",
        required=frozenset({"root", "retention_days", "encryption_adapter"}),
    )
    _bounded_text(artifacts["root"], "artifacts.root", 4_096)
    _integer(
        artifacts["retention_days"],
        "artifacts.retention_days",
        minimum=1,
        maximum=36_500,
    )
    if artifacts["encryption_adapter"] is not None:
        _bounded_text(
            artifacts["encryption_adapter"], "artifacts.encryption_adapter", 128
        )

    analysis = _exact_fields(
        config["analysis"],
        "analysis",
        required=frozenset(
            {
                "ocr_enabled",
                "ocr_adapter_type",
                "semantic_sidecars_enabled",
                "semantic_sidecar_adapter_type",
            }
        ),
        optional=frozenset({"anomaly_rules"}),
    )
    if not all(
        isinstance(analysis[field], bool)
        for field in ("ocr_enabled", "semantic_sidecars_enabled")
    ):
        raise TickConfigError("analysis stage flags must be boolean")
    for enabled_field, adapter_field in (
        ("ocr_enabled", "ocr_adapter_type"),
        ("semantic_sidecars_enabled", "semantic_sidecar_adapter_type"),
    ):
        adapter_type = analysis[adapter_field]
        if analysis[enabled_field] is True:
            _bounded_text(adapter_type, f"analysis.{adapter_field}", 128)
        elif adapter_type is not None:
            raise TickConfigError(
                f"analysis.{adapter_field} must be null when its stage is disabled"
            )
    anomaly_ids: set[str] = set()
    for index, raw_rule in enumerate(
        _array(analysis.get("anomaly_rules", []), "analysis.anomaly_rules", maximum=64)
    ):
        field = f"analysis.anomaly_rules[{index}]"
        rule = _exact_fields(
            raw_rule,
            field,
            required=frozenset(
                {
                    "rule_id",
                    "metric",
                    "direction",
                    "minimum_comparable_ticks",
                    "warning_ratio",
                    "critical_ratio",
                }
            ),
        )
        rule_id = _bounded_text(rule["rule_id"], f"{field}.rule_id", 48)
        if rule_id in anomaly_ids:
            raise TickConfigError("analysis.anomaly_rules rule_id must be unique")
        anomaly_ids.add(rule_id)
        if rule["metric"] not in {
            "yield_count",
            "rejection_rate",
            "latency_seconds",
            "missing_media_rate",
        }:
            raise TickConfigError(f"{field}.metric is unsupported")
        if rule["direction"] not in {"low", "high"}:
            raise TickConfigError(f"{field}.direction is unsupported")
        _integer(
            rule["minimum_comparable_ticks"],
            f"{field}.minimum_comparable_ticks",
            minimum=2,
            maximum=1_000,
        )
        warning = _positive_number(rule["warning_ratio"], f"{field}.warning_ratio")
        critical = _positive_number(
            rule["critical_ratio"], f"{field}.critical_ratio"
        )
        if rule["direction"] == "low" and critical > warning:
            raise TickConfigError(
                f"{field}.critical_ratio must not exceed warning_ratio"
            )
        if rule["direction"] == "high" and critical < warning:
            raise TickConfigError(
                f"{field}.critical_ratio must not be below warning_ratio"
            )

    notifications = _exact_fields(
        config["notifications"],
        "notifications",
        required=frozenset({"transports", "reminder_seconds"}),
    )
    transports = _array(
        notifications["transports"], "notifications.transports", maximum=16
    )
    if not transports:
        raise TickConfigError("notifications.transports must not be empty")
    for transport_index, raw_transport in enumerate(transports):
        transport_field = f"notifications.transports[{transport_index}]"
        transport = _exact_fields(
            raw_transport,
            transport_field,
            required=frozenset(
                {"transport_id", "adapter_type", "credential_ref", "routing"}
            ),
        )
        for key, maximum in (
            ("transport_id", 128),
            ("adapter_type", 128),
            ("credential_ref", 256),
        ):
            _bounded_text(transport[key], f"{transport_field}.{key}", maximum)
        routing = _object(transport["routing"], f"{transport_field}.routing")
        if not 1 <= len(routing) <= 16:
            raise TickConfigError(f"{transport_field}.routing must be bounded")
        for key, value in routing.items():
            _bounded_text(key, f"{transport_field}.routing key", 128)
            _bounded_text(value, f"{transport_field}.routing.{key}", 256)
    _integer(
        notifications["reminder_seconds"],
        "notifications.reminder_seconds",
        minimum=60,
        maximum=31_536_000,
    )

    _validate_observation_config(config)

    query = _exact_fields(
        config["query"],
        "query",
        required=frozenset({"embedding_space", "fusion_version"}),
    )
    _bounded_text(query["embedding_space"], "query.embedding_space", 128)
    _bounded_text(query["fusion_version"], "query.fusion_version", 128)


def _timestamp(clock: Clock) -> str:
    value = clock()
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("clock must return a timezone-aware datetime")
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _freeze_non_secret(value: object) -> object:
    """Remove runtime-only credential locators from the immutable snapshot."""
    if isinstance(value, Mapping):
        return {
            str(key): _freeze_non_secret(item)
            for key, item in value.items()
            if key != "credential_ref"
        }
    if isinstance(value, list):
        return [_freeze_non_secret(item) for item in value]
    return value


def _load_config(path: Path) -> tuple[dict[str, Any], str, str]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise TickConfigError(f"unable to load tick config: {path}") from exc
    config = _object(payload, "tick config")
    missing = sorted(_REQUIRED_CONFIG_FIELDS - config.keys())
    unknown = sorted(config.keys() - _CONFIG_FIELDS)
    if missing:
        raise TickConfigError(f"tick config missing fields: {', '.join(missing)}")
    if unknown:
        raise TickConfigError(f"tick config contains unknown fields: {', '.join(unknown)}")
    if config["schema_version"] != contracts.SCHEMA_VERSION:
        raise TickConfigError(
            f"tick config schema_version must be {contracts.SCHEMA_VERSION}"
        )
    try:
        contracts._reject_forbidden_ledger_fields(config, "tick_config")
        _canonical_json(config)
    except (contracts.ContractValidationError, TypeError, ValueError) as exc:
        raise TickConfigError(str(exc)) from exc
    _validate_config_shape(config)
    revision = _bounded_text(config["config_revision"], "config_revision")
    frozen = _object(_freeze_non_secret(config), "frozen tick config")
    return frozen, revision, _digest(frozen)


def _expand_lanes(
    config: Mapping[str, Any], *, tick_id: str, adapter_registry: AdapterRegistry
) -> tuple[dict[str, Any], ...]:
    services: dict[str, dict[str, Any]] = {}
    for index, raw in enumerate(_array(config["services"], "services")):
        service = _object(raw, f"services[{index}]")
        service_id = _bounded_text(
            service.get("service_id"), f"services[{index}].service_id"
        )
        if service_id in services:
            raise TickConfigError(f"duplicate service_id: {service_id}")
        source = _bounded_text(
            service.get("source"), f"services[{index}].source", 64
        )
        providers = _array(service.get("providers"), f"services[{index}].providers")
        if not providers:
            raise TickConfigError(f"services[{index}].providers must not be empty")
        provider_ids: set[str] = set()
        for provider_index, raw_provider in enumerate(providers):
            provider = _object(
                raw_provider, f"services[{index}].providers[{provider_index}]"
            )
            provider_id = _bounded_text(
                provider.get("provider_id"),
                f"services[{index}].providers[{provider_index}].provider_id",
            )
            if provider_id in provider_ids:
                raise TickConfigError(f"duplicate provider_id: {provider_id}")
            provider_ids.add(provider_id)
            adapter_type = _bounded_text(
                provider.get("adapter_type"),
                f"services[{index}].providers[{provider_index}].adapter_type",
            )
            try:
                spec = adapter_registry.require(
                    adapter_type, source=source, capability="collect"
                )
                if spec.normalization_proof_ref is None:
                    raise AdapterRegistryError(
                        f"adapter lacks normalization proof: {adapter_type}"
                    )
            except AdapterRegistryError as exc:
                raise TickConfigError(str(exc)) from exc
        services[service_id] = service

    lanes: list[dict[str, Any]] = []
    seen_targets: set[str] = set()
    for index, raw in enumerate(_array(config["targets"], "targets")):
        target = _object(raw, f"targets[{index}]")
        target_id = _bounded_text(
            target.get("target_id"), f"targets[{index}].target_id"
        )
        if target_id in seen_targets:
            raise TickConfigError(f"duplicate target_id: {target_id}")
        seen_targets.add(target_id)
        enabled = target.get("enabled")
        if not isinstance(enabled, bool):
            raise TickConfigError(f"targets[{index}].enabled must be boolean")
        if not enabled:
            continue
        service_id = _bounded_text(
            target.get("service_id"), f"targets[{index}].service_id"
        )
        service = services.get(service_id)
        if service is None:
            raise TickConfigError(
                f"target {target_id} references unknown service {service_id}"
            )
        access_partition_id = _bounded_text(
            target.get("access_partition_id"),
            f"targets[{index}].access_partition_id",
            256,
        )
        identity = {
            "tick_id": tick_id,
            "service_id": service_id,
            "target_id": target_id,
            "access_partition_id": access_partition_id,
        }
        lanes.append(
            {
                **identity,
                "lane_id": _stable_id("tick-lane", identity),
                "service": service,
                "target": target,
                "lane_digest": _digest(
                    {"service": service, "target": target, "identity": identity}
                ),
            }
        )
    if not lanes:
        raise TickConfigError("tick config must enable at least one target")
    return tuple(
        sorted(lanes, key=lambda lane: (lane["service_id"], lane["target_id"]))
    )


def _prepare_tick(
    config_path: Path,
    request: contracts.TickRequest,
    adapter_registry: AdapterRegistry,
) -> tuple[dict[str, Any], str, str, str, tuple[dict[str, Any], ...]]:
    """Load once and derive the immutable identity shared by preflight/enqueue."""
    if not isinstance(request, contracts.TickRequest):
        raise TypeError("request must be a TickRequest")
    config, config_revision, config_digest = _load_config(config_path)
    identity = {
        "schedule_id": request.schedule_id,
        "interval_from": request.interval_from,
        "interval_to": request.interval_to,
        "config_revision": config_revision,
        "config_digest": config_digest,
    }
    tick_id = _stable_id("tick", identity)
    lanes = _expand_lanes(
        config,
        tick_id=tick_id,
        adapter_registry=adapter_registry,
    )
    return config, config_revision, config_digest, tick_id, lanes


def _lane_stage_names(config: Mapping[str, Any]) -> tuple[str, ...]:
    analysis = _object(config["analysis"], "analysis")
    stages = list(_BASE_LANE_STAGES)
    if analysis.get("ocr_enabled") is True:
        stages.append("ocr")
    if analysis.get("semantic_sidecars_enabled") is True:
        stages.append("semantic_sidecar")
    return tuple(sorted(stages))


def _ensure_execution_attempt(
    conn: sqlite3.Connection,
    *,
    tick_id: str,
    now: str,
    maximum_attempts: int,
) -> str:
    latest = conn.execute(
        """SELECT * FROM service_tick_attempts
           WHERE tick_id = ? ORDER BY attempt DESC LIMIT 1""",
        (tick_id,),
    ).fetchone()
    if latest is None:
        attempt = 1
    elif latest["state"] == "queued":
        return str(latest["execution_attempt_id"])
    elif (
        latest["state"] == "running"
        and latest["lease_expires_at"] is not None
        and latest["lease_expires_at"] <= now
    ):
        conn.execute(
            """UPDATE service_tick_attempts
               SET state = 'expired', completed_at = ?, error_code = 'lease_expired',
                   lease_owner = NULL, lease_expires_at = NULL
               WHERE execution_attempt_id = ? AND state = 'running'""",
            (now, latest["execution_attempt_id"]),
        )
        conn.execute(
            """UPDATE service_tick_stages
               SET state = 'pending', execution_attempt_id = NULL,
                   started_at = NULL, updated_at = ?
               WHERE tick_id = ? AND state = 'running'""",
            (now, tick_id),
        )
        conn.execute(
            """UPDATE service_tick_provider_attempts
               SET state = CASE
                       WHEN EXISTS (
                           SELECT 1 FROM service_tick_provider_results AS r
                           WHERE r.provider_attempt_id =
                                 service_tick_provider_attempts.provider_attempt_id
                       ) THEN 'result_staged'
                       ELSE 'failure'
                   END,
                   failure_class = CASE
                       WHEN EXISTS (
                           SELECT 1 FROM service_tick_provider_results AS r
                           WHERE r.provider_attempt_id =
                                 service_tick_provider_attempts.provider_attempt_id
                       ) THEN NULL
                       ELSE 'execution_interrupted'
                   END,
                   completed_at = CASE
                       WHEN EXISTS (
                           SELECT 1 FROM service_tick_provider_results AS r
                           WHERE r.provider_attempt_id =
                                 service_tick_provider_attempts.provider_attempt_id
                       ) THEN NULL
                       ELSE ?
                   END
               WHERE tick_id = ? AND state = 'running'""",
            (now, tick_id),
        )
        conn.execute(
            """UPDATE service_tick_resource_leases
               SET released_at = ?
               WHERE tick_id = ? AND released_at IS NULL""",
            (now, tick_id),
        )
        attempt = int(latest["attempt"]) + 1
        if attempt > maximum_attempts:
            conn.execute(
                """UPDATE service_ticks
                   SET state = 'failed', updated_at = ? WHERE tick_id = ?""",
                (now, tick_id),
            )
            return str(latest["execution_attempt_id"])
        conn.execute(
            """UPDATE service_ticks
               SET state = 'queued', updated_at = ? WHERE tick_id = ?""",
            (now, tick_id),
        )
        sequence = int(
            conn.execute(
                """SELECT COALESCE(MAX(sequence), 0) + 1
                   FROM service_tick_events WHERE tick_id = ?""",
                (tick_id,),
            ).fetchone()[0]
        )
        event_identity = {"tick_id": tick_id, "sequence": sequence}
        conn.execute(
            """INSERT INTO service_tick_events (
                   event_id, tick_id, sequence, event_type,
                   execution_attempt_id, payload_json, occurred_at
               ) VALUES (?, ?, ?, 'attempt_recovered', ?, ?, ?)""",
            (
                _stable_id("tick-event", event_identity),
                tick_id,
                sequence,
                latest["execution_attempt_id"],
                _canonical_json(
                    {
                        "expired_attempt": int(latest["attempt"]),
                        "next_attempt": attempt,
                    }
                ),
                now,
            ),
        )
    elif latest["state"] == "expired":
        attempt = int(latest["attempt"]) + 1
    else:
        return str(latest["execution_attempt_id"])

    execution_attempt_id = _stable_id(
        "tick-attempt", {"tick_id": tick_id, "attempt": attempt}
    )
    conn.execute(
        """INSERT OR IGNORE INTO service_tick_attempts (
               execution_attempt_id, tick_id, attempt, state, created_at
           ) VALUES (?, ?, ?, 'queued', ?)""",
        (execution_attempt_id, tick_id, attempt, now),
    )
    return execution_attempt_id


class TickCoordinator:
    """Deep module owning durable tick identity and immutable lane expansion."""

    def __init__(
        self,
        db_path: Path,
        *,
        config_path: Path,
        adapter_registry: AdapterRegistry | None = None,
        runner: object | None = None,
        clock: Clock | None = None,
    ) -> None:
        self.db_path = Path(db_path)
        self.config_path = Path(config_path)
        self.adapter_registry = adapter_registry or default_adapter_registry()
        self.runner = runner
        self.clock = clock or (lambda: datetime.now(timezone.utc))
        store.init_db(self.db_path)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=5)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("PRAGMA busy_timeout=5000")
        return conn

    def enqueue_tick(self, request: contracts.TickRequest) -> contracts.TickReceipt:
        config, config_revision, config_digest, tick_id, lanes = _prepare_tick(
            self.config_path,
            request,
            self.adapter_registry,
        )
        now = _timestamp(self.clock)

        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            conn.execute(
                """INSERT OR IGNORE INTO service_ticks (
                       tick_id, schedule_id, interval_from, interval_to, trigger,
                       config_revision, config_digest, config_json, state,
                       created_at, updated_at
                   ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'queued', ?, ?)""",
                (
                    tick_id,
                    request.schedule_id,
                    request.interval_from,
                    request.interval_to,
                    request.trigger.value,
                    config_revision,
                    config_digest,
                    _canonical_json(config),
                    now,
                    now,
                ),
            )
            execution_attempt_id = _ensure_execution_attempt(
                conn,
                tick_id=tick_id,
                now=now,
                maximum_attempts=int(
                    _object(
                        _object(config["tick"], "tick").get("aggregate_limits"),
                        "tick.aggregate_limits",
                    )["attempts"]
                ),
            )
            for lane in lanes:
                conn.execute(
                    """INSERT OR IGNORE INTO service_tick_lanes (
                           lane_id, tick_id, service_id, target_id,
                           access_partition_id, service_config_json,
                           target_config_json, lane_digest, state,
                           created_at, updated_at
                       ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'ready', ?, ?)""",
                    (
                        lane["lane_id"],
                        tick_id,
                        lane["service_id"],
                        lane["target_id"],
                        lane["access_partition_id"],
                        _canonical_json(lane["service"]),
                        _canonical_json(lane["target"]),
                        lane["lane_digest"],
                        now,
                        now,
                    ),
                )
            for stage_name in _GLOBAL_STAGES:
                stage_identity = {
                    "tick_id": tick_id,
                    "stage_scope": "global",
                    "scope_id": tick_id,
                    "stage_name": stage_name,
                }
                conn.execute(
                    """INSERT OR IGNORE INTO service_tick_stages (
                           stage_id, tick_id, lane_id, stage_scope, scope_id,
                           stage_name, state, updated_at
                       ) VALUES (?, ?, NULL, 'global', ?, ?, 'pending', ?)""",
                    (
                        _stable_id("tick-stage", stage_identity),
                        tick_id,
                        tick_id,
                        stage_name,
                        now,
                    ),
                )
            for lane in lanes:
                for stage_name in _lane_stage_names(config):
                    stage_identity = {
                        "tick_id": tick_id,
                        "stage_scope": "lane",
                        "scope_id": lane["lane_id"],
                        "stage_name": stage_name,
                    }
                    conn.execute(
                        """INSERT OR IGNORE INTO service_tick_stages (
                               stage_id, tick_id, lane_id, stage_scope, scope_id,
                               stage_name, state, updated_at
                           ) VALUES (?, ?, ?, 'lane', ?, ?, 'pending', ?)""",
                        (
                            _stable_id("tick-stage", stage_identity),
                            tick_id,
                            lane["lane_id"],
                            lane["lane_id"],
                            stage_name,
                            now,
                        ),
                    )
                providers = _array(
                    lane["service"].get("providers"),
                    f"service {lane['service_id']} providers",
                )
                for ordinal, raw_provider in enumerate(providers):
                    provider = _object(
                        raw_provider,
                        f"service {lane['service_id']} provider {ordinal}",
                    )
                    provider_id = _bounded_text(
                        provider.get("provider_id"), "provider_id"
                    )
                    adapter_type = _bounded_text(
                        provider.get("adapter_type"), "adapter_type"
                    )
                    spec = self.adapter_registry.require(
                        adapter_type,
                        source=str(lane["service"]["source"]),
                        capability="collect",
                    )
                    normalization_proof_ref = spec.normalization_proof_ref
                    if normalization_proof_ref is None:
                        raise TickConfigError(
                            f"adapter lacks normalization proof: {adapter_type}"
                        )
                    limits = _object(provider.get("limits"), "provider limits")
                    manifest_identity = {
                        "lane_id": lane["lane_id"],
                        "provider_id": provider_id,
                    }
                    provider_manifest_id = _stable_id(
                        "tick-provider", manifest_identity
                    )
                    conn.execute(
                        """INSERT OR IGNORE INTO service_tick_providers (
                               provider_manifest_id, tick_id, lane_id,
                               provider_ordinal, provider_id, adapter_type,
                               normalization_proof_ref,
                               resource_keys_json, fallback_on_json, limits_json,
                               provider_digest
                           ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                        (
                            provider_manifest_id,
                            tick_id,
                            lane["lane_id"],
                            ordinal,
                            provider_id,
                            adapter_type,
                            normalization_proof_ref,
                            _canonical_json(provider.get("resource_keys", [])),
                            _canonical_json(provider.get("fallback_on", [])),
                            _canonical_json(limits),
                            _digest(
                                {
                                    **provider,
                                    "normalization_proof_ref": normalization_proof_ref,
                                }
                            ),
                        ),
                    )
                    budget_identity = {
                        "tick_id": tick_id,
                        "scope_kind": "provider",
                        "scope_id": provider_manifest_id,
                    }
                    conn.execute(
                        """INSERT OR IGNORE INTO service_tick_budgets (
                               budget_id, tick_id, scope_kind, scope_id,
                               limit_json, consumed_json, budget_digest, updated_at
                           ) VALUES (?, ?, 'provider', ?, ?, ?, ?, ?)""",
                        (
                            _stable_id("tick-budget", budget_identity),
                            tick_id,
                            provider_manifest_id,
                            _canonical_json(limits),
                            _canonical_json(_ZERO_USAGE),
                            _digest(limits),
                            now,
                        ),
                    )
            aggregate_limits = _object(
                _object(config["tick"], "tick").get("aggregate_limits"),
                "tick.aggregate_limits",
            )
            tick_budget_identity = {
                "tick_id": tick_id,
                "scope_kind": "tick",
                "scope_id": tick_id,
            }
            conn.execute(
                """INSERT OR IGNORE INTO service_tick_budgets (
                       budget_id, tick_id, scope_kind, scope_id,
                       limit_json, consumed_json, budget_digest, updated_at
                   ) VALUES (?, ?, 'tick', ?, ?, ?, ?, ?)""",
                (
                    _stable_id("tick-budget", tick_budget_identity),
                    tick_id,
                    tick_id,
                    _canonical_json(aggregate_limits),
                    _canonical_json(_ZERO_USAGE),
                    _digest(aggregate_limits),
                    now,
                ),
            )
            conn.execute(
                """INSERT OR IGNORE INTO service_tick_events (
                       event_id, tick_id, sequence, event_type,
                       execution_attempt_id, payload_json, occurred_at
                   ) VALUES (?, ?, 1, 'tick_enqueued', ?, ?, ?)""",
                (
                    _stable_id("tick-event", {"tick_id": tick_id, "sequence": 1}),
                    tick_id,
                    execution_attempt_id,
                    _canonical_json({"state": "queued"}),
                    now,
                ),
            )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
        if self.runner is not None:
            run = getattr(self.runner, "run", None)
            if not callable(run):
                raise TypeError("runner must provide run(tick_id)")
            run(tick_id)
        return self.get_tick(tick_id)

    def get_tick(self, tick_id: str) -> contracts.TickReceipt:
        tick_id = _bounded_text(tick_id, "tick_id")
        conn = self._connect()
        try:
            tick = conn.execute(
                "SELECT * FROM service_ticks WHERE tick_id = ?", (tick_id,)
            ).fetchone()
            if tick is None:
                raise KeyError(f"unknown tick: {tick_id}")
            attempts = conn.execute(
                """SELECT execution_attempt_id, tick_id, attempt, state,
                          created_at, started_at, completed_at, error_code,
                          lease_generation, lease_expires_at
                   FROM service_tick_attempts
                   WHERE tick_id = ? ORDER BY attempt""",
                (tick_id,),
            ).fetchall()
            lanes = conn.execute(
                """SELECT lane_id, service_id, target_id, access_partition_id,
                          service_config_json, target_config_json, lane_digest,
                          state
                   FROM service_tick_lanes
                   WHERE tick_id = ? ORDER BY service_id, target_id, lane_id""",
                (tick_id,),
            ).fetchall()
            stages = conn.execute(
                """SELECT stage_id, lane_id, stage_scope, scope_id, stage_name,
                          state, input_digest, output_digest,
                          execution_attempt_id, started_at, completed_at, updated_at
                   FROM service_tick_stages WHERE tick_id = ?
                   ORDER BY stage_scope, scope_id, stage_name""",
                (tick_id,),
            ).fetchall()
            budgets = conn.execute(
                """SELECT budget_id, scope_kind, scope_id, limit_json,
                          consumed_json, budget_digest, updated_at
                   FROM service_tick_budgets WHERE tick_id = ?
                   ORDER BY scope_kind, scope_id""",
                (tick_id,),
            ).fetchall()
            budget_events = conn.execute(
                """SELECT budget_event_id, budget_id, execution_attempt_id,
                          provider_attempt_id, delta_json,
                          resulting_consumed_json, idempotency_key, created_at
                   FROM service_tick_budget_events WHERE tick_id = ?
                   ORDER BY created_at, budget_event_id""",
                (tick_id,),
            ).fetchall()
            providers = conn.execute(
                """SELECT provider_manifest_id, lane_id, provider_ordinal,
                          provider_id, adapter_type, normalization_proof_ref,
                          resource_keys_json, fallback_on_json, limits_json,
                          provider_digest
                   FROM service_tick_providers WHERE tick_id = ?
                   ORDER BY lane_id, provider_ordinal""",
                (tick_id,),
            ).fetchall()
            provider_attempts = conn.execute(
                """SELECT provider_attempt_id, lane_id, provider_manifest_id,
                          execution_attempt_id, retry_ordinal, state,
                          failure_class, fallback_reason, result_digest,
                          outcome_counts_json,
                          started_at, completed_at
                   FROM service_tick_provider_attempts
                   WHERE tick_id = ? ORDER BY started_at, provider_attempt_id""",
                (tick_id,),
            ).fetchall()
            provider_results = conn.execute(
                """SELECT provider_attempt_id, tick_id, lane_id, result_digest,
                          created_at
                   FROM service_tick_provider_results WHERE tick_id = ?
                   ORDER BY provider_attempt_id""",
                (tick_id,),
            ).fetchall()
            resource_leases = conn.execute(
                """SELECT lease_id, lane_id, provider_attempt_id, resource_key,
                          lease_generation, acquired_at, lease_expires_at, released_at
                   FROM service_tick_resource_leases WHERE tick_id = ?
                   ORDER BY lease_id""",
                (tick_id,),
            ).fetchall()
            incidents = conn.execute(
                """SELECT DISTINCT i.incident_id, i.fingerprint, i.first_tick_id,
                          i.last_tick_id, i.lane_id, i.source, i.profile_ref,
                          i.stage, i.incident_type, i.severity, i.state,
                          i.safe_summary, i.access_partition_id,
                          i.protected_asset_id, i.protected_artifact_ref,
                          i.occurrence_count, i.first_detected_at,
                          i.last_detected_at, i.acknowledged_at,
                          i.acknowledged_by_ref, i.resolved_at,
                          i.resolution_execution_id
                   FROM service_incidents AS i
                   JOIN service_incident_transitions AS t
                     ON t.incident_id = i.incident_id
                   WHERE t.tick_id = ? ORDER BY i.incident_id""",
                (tick_id,),
            ).fetchall()
            incident_transitions = conn.execute(
                """SELECT transition_id, incident_id, sequence, transition_type,
                          from_state, to_state, safe_payload_json, occurred_at
                   FROM service_incident_transitions WHERE tick_id = ?
                   ORDER BY incident_id, sequence""",
                (tick_id,),
            ).fetchall()
            incident_artifacts = conn.execute(
                """SELECT incident_artifact_id, incident_id, tick_id, asset_id,
                          artifact_ref, capture_reason
                   FROM service_incident_artifacts WHERE tick_id = ?
                   ORDER BY incident_artifact_id""",
                (tick_id,),
            ).fetchall()
            notification_deliveries = conn.execute(
                """SELECT delivery_attempt_id, incident_id, notification_kind,
                          notification_sequence, transport_ordinal, transport_id,
                          state, safe_error_code, delivery_ref, payload_digest,
                          attempted_at
                   FROM service_notification_deliveries WHERE tick_id = ?
                   ORDER BY delivery_attempt_id""",
                (tick_id,),
            ).fetchall()
            artifacts = conn.execute(
                """SELECT asset_id, parent_version_id, source_url, content_hash,
                          mime_type, media_kind, alt_text, byte_size, storage_ref,
                          access_partition_id, retention_class, bytes_present
                   FROM service_media_assets
                   WHERE asset_id IN (
                       SELECT a.asset_id FROM service_media_assets AS a
                       JOIN service_source_versions AS v
                         ON v.version_id = a.parent_version_id
                       JOIN service_tick_provider_attempts AS p
                         ON p.provider_attempt_id = v.provider_attempt_id
                       WHERE p.tick_id = ?
                       UNION
                       SELECT ia.asset_id FROM service_incident_artifacts AS ia
                       WHERE ia.tick_id = ?
                   ) ORDER BY asset_id""",
                (tick_id, tick_id),
            ).fetchall()
            artifact_ids = [row["asset_id"] for row in artifacts]
            if artifact_ids:
                placeholders = ",".join("?" for _ in artifact_ids)
                derivatives = conn.execute(
                    f"""SELECT derivative_id, asset_id, derivative_kind,
                                derivative_version, input_digest, output_digest,
                                access_partition_id, retention_class, state
                        FROM service_media_derivatives
                        WHERE asset_id IN ({placeholders})
                        ORDER BY derivative_id""",
                    artifact_ids,
                ).fetchall()
            else:
                derivatives = []
            evidence = conn.execute(
                """SELECT DISTINCT v.version_id, v.content_hash
                   FROM service_source_versions AS v
                   JOIN service_source_sightings AS s
                     ON s.version_id = v.version_id
                   WHERE s.tick_id = ? ORDER BY v.version_id""",
                (tick_id,),
            ).fetchall()
            catalog = conn.execute(
                """SELECT cluster_id, cluster_kind, label, rationale,
                          validator_version, access_partition_id, cluster_digest
                   FROM service_catalog_clusters WHERE tick_id = ?
                   ORDER BY cluster_id""",
                (tick_id,),
            ).fetchall()
            catalog_members = conn.execute(
                """SELECT m.cluster_id, m.member_id, m.source, m.relationship,
                          m.evidence_ref, m.access_partition_id, m.confidence
                   FROM service_catalog_cluster_members AS m
                   JOIN service_catalog_clusters AS c
                     ON c.cluster_id = m.cluster_id
                   WHERE c.tick_id = ?
                   ORDER BY m.cluster_id, m.member_id, m.source""",
                (tick_id,),
            ).fetchall()
            anomalies = conn.execute(
                """SELECT result_id, rule_id, metric, state, result_digest
                   FROM service_tick_anomaly_results WHERE tick_id = ?
                   ORDER BY result_id""",
                (tick_id,),
            ).fetchall()
            snapshot = conn.execute(
                """SELECT * FROM service_tick_query_snapshots
                   WHERE tick_id = ? ORDER BY created_at DESC, snapshot_id DESC
                   LIMIT 1""",
                (tick_id,),
            ).fetchone()
            snapshot_entries = (
                conn.execute(
                    """SELECT entry_id, channel, source, access_partition_id,
                              published_at, provenance_json, entry_digest
                       FROM service_tick_query_entries WHERE snapshot_id = ?
                       ORDER BY entry_id, channel""",
                    (snapshot["snapshot_id"],),
                ).fetchall()
                if snapshot is not None
                else []
            )
            events = conn.execute(
                """SELECT event_id, sequence, event_type, execution_attempt_id,
                          lane_id, payload_json, occurred_at
                   FROM service_tick_events WHERE tick_id = ?
                   ORDER BY sequence""",
                (tick_id,),
            ).fetchall()
            head = conn.execute(
                "SELECT snapshot_id FROM service_tick_query_head WHERE singleton_id = 1"
            ).fetchone()
        finally:
            conn.close()
        try:
            frozen_config = json.loads(tick["config_json"])
        except (TypeError, json.JSONDecodeError) as exc:
            raise TickIntegrityError("frozen config is not canonical JSON") from exc
        if _digest(frozen_config) != tick["config_digest"]:
            raise TickIntegrityError("frozen config digest does not match")
        for lane in lanes:
            try:
                service = json.loads(lane["service_config_json"])
                target = json.loads(lane["target_config_json"])
            except (TypeError, json.JSONDecodeError) as exc:
                raise TickIntegrityError("frozen lane is not canonical JSON") from exc
            identity = {
                "tick_id": tick_id,
                "service_id": lane["service_id"],
                "target_id": lane["target_id"],
                "access_partition_id": lane["access_partition_id"],
            }
            if _digest(
                {"service": service, "target": target, "identity": identity}
            ) != lane["lane_digest"]:
                raise TickIntegrityError(
                    f"frozen lane digest does not match: {lane['lane_id']}"
                )

        def _manifest_rows(
            rows: Sequence[sqlite3.Row], *, json_fields: Sequence[str] = ()
        ) -> list[dict[str, object]]:
            manifest: list[dict[str, object]] = []
            for row in rows:
                item = dict(row)
                for field in json_fields:
                    raw = item.get(field)
                    if raw is None:
                        continue
                    try:
                        item[field.removesuffix("_json")] = json.loads(str(raw))
                    except json.JSONDecodeError as exc:
                        raise TickIntegrityError(
                            f"receipt manifest contains invalid JSON: {field}"
                        ) from exc
                    del item[field]
                manifest.append(item)
            return manifest

        snapshot_manifest: dict[str, object] = {}
        if snapshot is not None:
            snapshot_manifest = dict(snapshot)
            try:
                snapshot_manifest["completeness"] = json.loads(
                    str(snapshot_manifest.pop("completeness_json"))
                )
            except json.JSONDecodeError as exc:
                raise TickIntegrityError(
                    "snapshot completeness is not canonical JSON"
                ) from exc
            snapshot_manifest["entries"] = _manifest_rows(
                snapshot_entries, json_fields=("provenance_json",)
            )
        receipt_manifests: dict[str, object] = {
            "execution_attempts": _manifest_rows(attempts),
            "events": _manifest_rows(events, json_fields=("payload_json",)),
            "stages": _manifest_rows(stages),
            "budgets": _manifest_rows(
                budgets, json_fields=("limit_json", "consumed_json")
            ),
            "budget_events": _manifest_rows(
                budget_events,
                json_fields=("delta_json", "resulting_consumed_json"),
            ),
            "providers": _manifest_rows(
                providers,
                json_fields=("resource_keys_json", "fallback_on_json", "limits_json"),
            ),
            "provider_attempts": _manifest_rows(
                provider_attempts, json_fields=("outcome_counts_json",)
            ),
            "provider_results": _manifest_rows(provider_results),
            "resource_leases": _manifest_rows(resource_leases),
            "evidence": _manifest_rows(evidence),
            "artifacts": _manifest_rows(artifacts),
            "derivatives": _manifest_rows(derivatives),
            "incidents": {
                "records": _manifest_rows(incidents),
                "transitions": _manifest_rows(
                    incident_transitions, json_fields=("safe_payload_json",)
                ),
            },
            "incident_artifacts": _manifest_rows(incident_artifacts),
            "notifications": _manifest_rows(notification_deliveries),
            "anomalies": _manifest_rows(anomalies),
            "catalog": {
                "clusters": _manifest_rows(catalog),
                "members": _manifest_rows(catalog_members),
            },
            "snapshot": snapshot_manifest,
        }
        return contracts.TickReceipt.from_dict(
            {
                "schema_version": contracts.SCHEMA_VERSION,
                "tick_id": tick["tick_id"],
                "schedule_id": tick["schedule_id"],
                "interval_from": tick["interval_from"],
                "interval_to": tick["interval_to"],
                "trigger": tick["trigger"],
                "config_revision": tick["config_revision"],
                "config_digest": tick["config_digest"],
                "state": tick["state"],
                "execution_attempt_ids": [
                    row["execution_attempt_id"] for row in attempts
                ],
                "lanes": [
                    {
                        "schema_version": contracts.SCHEMA_VERSION,
                        "lane_id": row["lane_id"],
                        "service_id": row["service_id"],
                        "target_id": row["target_id"],
                        "access_partition_id": row["access_partition_id"],
                        "state": row["state"],
                    }
                    for row in lanes
                ],
                "stage_states": {
                    f"{row['stage_scope']}:{row['scope_id']}:{row['stage_name']}": row[
                        "state"
                    ]
                    for row in stages
                },
                "budget_summary": {
                    (
                        "tick"
                        if row["scope_kind"] == "tick"
                        else f"{row['scope_kind']}:{row['scope_id']}"
                    ): {
                        "limits": json.loads(row["limit_json"]),
                        "consumed": json.loads(row["consumed_json"]),
                        "digest": row["budget_digest"],
                    }
                    for row in budgets
                },
                "provider_attempt_ids": [
                    row["provider_attempt_id"] for row in provider_attempts
                ],
                "resource_lease_ids": [row["lease_id"] for row in resource_leases],
                "source_version_ids": [row["version_id"] for row in evidence],
                "incident_ids": [row["incident_id"] for row in incidents],
                "incident_transition_ids": [
                    row["transition_id"] for row in incident_transitions
                ],
                "notification_delivery_ids": [
                    row["delivery_attempt_id"] for row in notification_deliveries
                ],
                "anomaly_result_ids": [row["result_id"] for row in anomalies],
                "artifact_ids": artifact_ids,
                "derivative_ids": [row["derivative_id"] for row in derivatives],
                "catalog_cluster_ids": [row["cluster_id"] for row in catalog],
                "snapshot_id": snapshot["snapshot_id"] if snapshot is not None else None,
                "head_promoted": bool(
                    snapshot is not None
                    and head is not None
                    and head["snapshot_id"] == snapshot["snapshot_id"]
                ),
                "manifest_digests": {
                    name: _digest(value)
                    for name, value in receipt_manifests.items()
                },
                "receipt_manifests": receipt_manifests,
                "coverage_gaps": (
                    [f"{tick['interval_from']}/{tick['interval_to']}"]
                    if tick["state"] == "missed_due_to_overlap"
                    else []
                ),
                "versions": {
                    "contract_schema": str(contracts.SCHEMA_VERSION),
                    "database_schema": str(max(store.MIGRATIONS)),
                    "tick_runner": "tick-runner-v1",
                    "anomaly_evaluator": "deterministic-median-v1",
                    "adapter_types": ",".join(
                        sorted({str(row["adapter_type"]) for row in providers})
                    ),
                    "embedding_space": str(
                        snapshot["embedding_space"]
                        if snapshot is not None
                        else frozen_config["query"]["embedding_space"]
                    ),
                    "fusion_version": str(
                        snapshot["fusion_version"]
                        if snapshot is not None
                        else frozen_config["query"]["fusion_version"]
                    ),
                    "derivative_versions": (
                        ",".join(
                            sorted({str(row["derivative_version"]) for row in derivatives})
                        )
                        or "none"
                    ),
                },
                "created_at": tick["created_at"],
                "updated_at": tick["updated_at"],
            }
        )
