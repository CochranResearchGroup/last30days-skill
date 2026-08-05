"""User-scoped path and production assembly helpers for manual ticks."""

from __future__ import annotations

import json
import os
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from .service_retrieval import LocalHashEmbeddingProvider
from .service_runtime import build_subprocess_acquisition_worker
from .service_tick import TickCoordinator
from .service_tick_adapters import AdapterRegistry
from .service_tick_builtin_adapters import build_acquisition_adapter_registry
from .service_tick_incidents import IncidentManager
from .service_tick_media import (
    ContentAddressedArtifactStore,
    MediaDerivativePublisher,
)
from .service_tick_notifications import (
    CommandRunner,
    _run_command,
    build_notification_transports,
)
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


def build_tick_runtime(
    db_path: Path,
    *,
    config_path: Path | None = None,
    worker=None,
    adapter_registry: AdapterRegistry | None = None,
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
    query = config.get("query")
    if not isinstance(query, Mapping) or query.get("embedding_space") != "local-hash-v1":
        raise RuntimeError("installed runtime supports embedding_space local-hash-v1")
    artifacts_config = config.get("artifacts")
    notifications_config = config.get("notifications")
    if not isinstance(artifacts_config, Mapping) or not isinstance(
        notifications_config, Mapping
    ):
        raise RuntimeError("tick artifact/notification configuration is incomplete")
    artifact_root_value = artifacts_config.get("root")
    if not isinstance(artifact_root_value, str) or not artifact_root_value.strip():
        raise RuntimeError("tick artifact root is required")
    artifact_root = Path(artifact_root_value).expanduser()
    if not artifact_root.is_absolute():
        raise RuntimeError("tick artifact root must be an absolute user-scoped path")
    if adapter_registry is not None and not isinstance(
        adapter_registry, AdapterRegistry
    ):
        raise TypeError("adapter_registry must be an AdapterRegistry")
    if adapter_registry is None:
        active_worker = worker or build_subprocess_acquisition_worker()
        registry = build_acquisition_adapter_registry(active_worker)
    else:
        registry = adapter_registry
    media = MediaDerivativePublisher(
        db_path,
        ContentAddressedArtifactStore(artifact_root),
        clock=clock,
    )
    incidents = IncidentManager(db_path, media, clock=clock)
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
