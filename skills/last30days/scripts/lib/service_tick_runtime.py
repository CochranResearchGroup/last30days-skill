"""User-scoped path and production assembly helpers for manual ticks."""

from __future__ import annotations

import json
import os
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from . import service_contracts as contracts
from .service_retrieval import LocalHashEmbeddingProvider
from .service_runtime import build_subprocess_acquisition_worker
from .service_tick import (
    TickCoordinator,
    _array,
    _bounded_text,
    _digest,
    _object,
    _prepare_tick,
    _validate_observation_config,
)
from .service_tick_adapters import AdapterRegistry
from .service_tick_analysis import (
    AnalysisAdapterRegistry,
    default_analysis_adapter_registry,
)
from .service_tick_builtin_adapters import build_acquisition_adapter_registry
from .service_tick_incidents import IncidentManager, NotificationPreflightError
from .service_tick_media import (
    ContentAddressedArtifactStore,
    MediaDerivativePublisher,
)
from .service_tick_notifications import (
    CommandRunner,
    _run_command,
    build_notification_transports,
)
from .service_tick_observation import AgentBrowserObservationTransport
from .service_tick_query import TickSnapshotPublisher
from .service_tick_runner import TickRunner


def default_tick_config_path(
    *,
    environ: Mapping[str, str] | None = None,
    home: Path | None = None,
) -> Path:
    process_env = os.environ if environ is None else environ
    override = process_env.get("LAST30DAYS_CONFIG_DIR")
    if override:
        root = Path(override).expanduser()
    elif process_env.get("XDG_CONFIG_HOME"):
        root = Path(process_env["XDG_CONFIG_HOME"]) / "last30days"
    else:
        root = (home or Path.home()) / ".config" / "last30days"
    return root / "tick-config-v1.json"


@dataclass(frozen=True)
class TickRuntime:
    coordinator: TickCoordinator
    runner: TickRunner
    snapshots: TickSnapshotPublisher


def _validate_runtime_config(
    config: Mapping[str, object],
    *,
    analysis_registry: AnalysisAdapterRegistry,
) -> tuple[Mapping[str, object], Mapping[str, object], object]:
    query = config.get("query")
    if not isinstance(query, Mapping) or query.get("embedding_space") != "local-hash-v1":
        raise RuntimeError("installed runtime supports embedding_space local-hash-v1")
    artifacts_config = config.get("artifacts")
    analysis_config = config.get("analysis")
    notifications_config = config.get("notifications")
    observation_config = _validate_observation_config(config)
    if (
        not isinstance(artifacts_config, Mapping)
        or not isinstance(analysis_config, Mapping)
        or not isinstance(notifications_config, Mapping)
    ):
        raise RuntimeError(
            "tick artifact/analysis/notification configuration is incomplete"
        )
    for enabled_field, adapter_field, capability in (
        ("ocr_enabled", "ocr_adapter_type", "ocr"),
        (
            "semantic_sidecars_enabled",
            "semantic_sidecar_adapter_type",
            "semantic_sidecar",
        ),
    ):
        if analysis_config.get(enabled_field) is True:
            analysis_registry.require(
                str(analysis_config.get(adapter_field)), capability=capability
            )
    artifact_root_value = artifacts_config.get("root")
    if not isinstance(artifact_root_value, str) or not artifact_root_value.strip():
        raise RuntimeError("tick artifact root is required")
    artifact_root = Path(artifact_root_value).expanduser()
    if not artifact_root.is_absolute():
        raise RuntimeError("tick artifact root must be an absolute user-scoped path")
    return artifacts_config, notifications_config, observation_config


def _runtime_registry(*, worker, adapter_registry: AdapterRegistry | None) -> AdapterRegistry:
    if adapter_registry is not None and not isinstance(
        adapter_registry, AdapterRegistry
    ):
        raise TypeError("adapter_registry must be an AdapterRegistry")
    if adapter_registry is not None:
        return adapter_registry
    active_worker = worker or build_subprocess_acquisition_worker()
    return build_acquisition_adapter_registry(active_worker)


def _runtime_analysis_registry(
    analysis_registry: AnalysisAdapterRegistry | None,
) -> AnalysisAdapterRegistry:
    if analysis_registry is not None and not isinstance(
        analysis_registry, AnalysisAdapterRegistry
    ):
        raise TypeError("analysis_registry must be an AnalysisAdapterRegistry")
    return analysis_registry or default_analysis_adapter_registry()


def preflight_tick_runtime(
    request: contracts.TickRequest,
    *,
    config_path: Path | None = None,
    worker=None,
    adapter_registry: AdapterRegistry | None = None,
    analysis_registry: AnalysisAdapterRegistry | None = None,
    command_runner: CommandRunner = _run_command,
) -> dict[str, object]:
    """Validate one prospective manual tick without creating runtime state."""
    config_file = Path(config_path or default_tick_config_path())
    registry = _runtime_registry(worker=worker, adapter_registry=adapter_registry)
    config, config_revision, config_digest, tick_id, lanes = _prepare_tick(
        config_file,
        request,
        registry,
    )
    active_analysis_registry = _runtime_analysis_registry(analysis_registry)
    _, notifications_config, _ = _validate_runtime_config(
        config,
        analysis_registry=active_analysis_registry,
    )

    raw_transports = _array(
        notifications_config.get("transports"), "notification transports"
    )
    transports = build_notification_transports(
        notifications_config,
        command_runner=command_runner,
    )
    notification_receipts: list[dict[str, object]] = []
    ready_found = False
    for ordinal, (raw_transport, transport) in enumerate(
        zip(raw_transports, transports, strict=True)
    ):
        transport_config = _object(
            raw_transport, f"notification transports[{ordinal}]"
        )
        readiness = "not_checked"
        if not ready_found:
            try:
                ready_found = bool(transport.readiness())
            except Exception:
                ready_found = False
            readiness = "ready" if ready_found else "unavailable"
        notification_receipts.append(
            {
                "ordinal": ordinal,
                "transport_id_digest": _digest(
                    _bounded_text(
                        transport_config.get("transport_id"), "transport_id"
                    )
                ),
                "adapter_type": _bounded_text(
                    transport_config.get("adapter_type"), "adapter_type"
                ),
                "routing_digest": _digest(
                    _object(transport_config.get("routing"), "notification routing")
                ),
                "readiness": readiness,
            }
        )
    if not ready_found:
        raise NotificationPreflightError(
            "no configured notification transport passed readiness"
        )

    lane_manifest: list[dict[str, object]] = []
    for lane in lanes:
        provider_receipts: list[dict[str, object]] = []
        providers = _array(
            lane["service"].get("providers"),
            f"service {lane['service_id']} providers",
        )
        for ordinal, raw_provider in enumerate(providers):
            provider = _object(
                raw_provider,
                f"service {lane['service_id']} provider {ordinal}",
            )
            adapter_type = _bounded_text(
                provider.get("adapter_type"), "adapter_type"
            )
            spec = registry.require(
                adapter_type,
                source=str(lane["service"]["source"]),
                capability="collect",
            )
            if spec.normalization_proof_ref is None:
                raise RuntimeError(f"adapter lacks normalization proof: {adapter_type}")
            resource_keys = _array(provider.get("resource_keys"), "resource_keys")
            provider_receipts.append(
                {
                    "ordinal": ordinal,
                    "provider_id_digest": _digest(
                        _bounded_text(provider.get("provider_id"), "provider_id")
                    ),
                    "adapter_type": adapter_type,
                    "normalization_proof_ref": spec.normalization_proof_ref,
                    "resource_key_digests": [
                        _digest(_bounded_text(key, "resource_key", 256))
                        for key in resource_keys
                    ],
                    "fallback_on": list(
                        _array(provider.get("fallback_on"), "fallback_on")
                    ),
                    "limits": _object(provider.get("limits"), "provider limits"),
                    "provider_digest": _digest(
                        {
                            **provider,
                            "normalization_proof_ref": spec.normalization_proof_ref,
                        }
                    ),
                }
            )
        lane_manifest.append(
            {
                "lane_id": lane["lane_id"],
                "service_id_digest": _digest(lane["service_id"]),
                "target_id_digest": _digest(lane["target_id"]),
                "access_partition_digest": _digest(lane["access_partition_id"]),
                "lane_digest": lane["lane_digest"],
                "providers": provider_receipts,
            }
        )

    aggregate_limits = _object(
        _object(config["tick"], "tick").get("aggregate_limits"),
        "tick.aggregate_limits",
    )
    return {
        "schema_version": contracts.SCHEMA_VERSION,
        "status": "ready",
        "tick_id": tick_id,
        "schedule_id": request.schedule_id,
        "interval_from": request.interval_from,
        "interval_to": request.interval_to,
        "trigger": request.trigger.value,
        "config_revision": config_revision,
        "config_digest": config_digest,
        "lane_manifest": lane_manifest,
        "aggregate_limits": aggregate_limits,
        "notification_transports": notification_receipts,
    }


def build_tick_runtime(
    db_path: Path,
    *,
    config_path: Path | None = None,
    worker=None,
    adapter_registry: AdapterRegistry | None = None,
    analysis_registry: AnalysisAdapterRegistry | None = None,
    command_runner: CommandRunner = _run_command,
    clock: Callable[[], datetime] | None = None,
) -> TickRuntime:
    """Assemble one manual-only tick from installed code and user config."""
    config_file = Path(config_path or default_tick_config_path())
    try:
        config = json.loads(config_file.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"unable to read tick configuration: {config_file}") from exc
    if not isinstance(config, Mapping):
        raise RuntimeError("tick configuration must be an object")
    active_analysis_registry = _runtime_analysis_registry(analysis_registry)
    artifacts_config, notifications_config, observation_config = (
        _validate_runtime_config(
            config,
            analysis_registry=active_analysis_registry,
        )
    )
    artifact_root_value = artifacts_config["root"]
    artifact_root = Path(artifact_root_value).expanduser()
    registry = _runtime_registry(worker=worker, adapter_registry=adapter_registry)
    media = MediaDerivativePublisher(
        db_path,
        ContentAddressedArtifactStore(artifact_root),
        clock=clock,
    )
    observation_transport = None
    if isinstance(observation_config, Mapping):
        observation_transport = AgentBrowserObservationTransport(
            str(observation_config["service_base_url"])
        )
    incidents = IncidentManager(
        db_path,
        media,
        observation_transport=observation_transport,
        clock=clock,
    )
    snapshots = TickSnapshotPublisher(
        db_path,
        LocalHashEmbeddingProvider(),
        clock=clock,
    )
    transports = build_notification_transports(
        notifications_config,
        command_runner=command_runner,
    )
    runner = TickRunner(
        db_path,
        registry,
        media=media,
        incidents=incidents,
        snapshots=snapshots,
        notification_transports=transports,
        analysis_registry=active_analysis_registry,
        clock=clock,
    )
    coordinator = TickCoordinator(
        db_path,
        config_path=config_file,
        adapter_registry=registry,
        runner=runner,
        clock=clock,
    )
    return TickRuntime(coordinator=coordinator, runner=runner, snapshots=snapshots)
