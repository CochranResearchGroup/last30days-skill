"""Side-effect-free sanitized admission proof for the manual T08 tick."""

from __future__ import annotations

import json

import pytest

from lib import service_contracts as contracts
from lib import service_tick_runtime
from lib.service_tick import TickConfigError, TickCoordinator
from lib.service_tick_analysis import AnalysisAdapterError
from lib.service_tick_builtin_adapters import build_acquisition_adapter_registry
from lib.service_tick_notifications import CommandReceipt
from lib.service_tick_incidents import NotificationPreflightError
from service import build_parser


def _write_config(path) -> None:
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "config_revision": "preflight-1",
                "services": [
                    {
                        "service_id": "sensitive-service-id",
                        "source": "x",
                        "providers": [
                            {
                                "provider_id": "sensitive-provider-id",
                                "adapter_type": "x_agent_browser",
                                "resource_keys": ["browser:profile:sensitive"],
                                "fallback_on": ["transient"],
                                "credential_ref": "credential-ref:sensitive",
                                "limits": {
                                    "attempts": 1,
                                    "network_requests": 7,
                                    "wall_seconds": 30,
                                    "items": 3,
                                    "cost_cents": 0,
                                    "model_tokens": 0,
                                },
                            }
                        ],
                    }
                ],
                "targets": [
                    {
                        "target_id": "sensitive-target-id",
                        "service_id": "sensitive-service-id",
                        "surface_kind": "topic",
                        "selector": {
                            "query": "operator-sensitive query",
                            "profile_id": "sensitive-profile",
                        },
                        "access_partition_id": "profile:sensitive",
                        "retention_class": "durable",
                        "enabled": True,
                    }
                ],
                "tick": {
                    "timezone": "UTC",
                    "lateness_seconds": 86400,
                    "aggregate_limits": {
                        "attempts": 1,
                        "network_requests": 7,
                        "wall_seconds": 30,
                        "items": 3,
                        "cost_cents": 0,
                        "model_tokens": 0,
                    },
                },
                "artifacts": {
                    "root": str(path.parent / "operator-artifacts"),
                    "retention_days": 30,
                    "encryption_adapter": None,
                },
                "analysis": {
                    "ocr_enabled": True,
                    "ocr_adapter_type": "provider_output_ocr_v1",
                    "semantic_sidecars_enabled": True,
                    "semantic_sidecar_adapter_type": (
                        "provider_output_semantic_sidecar_v1"
                    ),
                },
                "notifications": {
                    "transports": [
                        {
                            "transport_id": "sensitive-transport-id",
                            "adapter_type": "slack_receipts",
                            "credential_ref": "credential-ref:ops",
                            "routing": {
                                "workspace": "sensitive-workspace",
                                "channel_ref": "sensitive-recipient",
                            },
                        }
                    ],
                    "reminder_seconds": 3600,
                },
                "observation": {
                    "adapter_type": "agent_browser_service",
                    "service_base_url": "https://agent-browser.example.invalid",
                },
                "query": {
                    "embedding_space": "local-hash-v1",
                    "fusion_version": "rrf-v1",
                },
            }
        ),
        encoding="utf-8",
    )


def _request():
    return contracts.TickRequest.from_dict(
        {
            "schema_version": 1,
            "schedule_id": "manual-default",
            "interval_from": "2026-08-03T00:00:00Z",
            "interval_to": "2026-08-04T00:00:00Z",
            "trigger": "manual",
        }
    )


class ReadyCommands:
    def __init__(self) -> None:
        self.calls = []

    def __call__(self, argv, *, input_text=None, timeout_seconds=30):
        self.calls.append((tuple(argv), input_text, timeout_seconds))
        return CommandReceipt(0, "{}", "")


class FailoverCommands:
    def __init__(self, *, fallback_ready: bool) -> None:
        self.calls = []
        self.fallback_ready = fallback_ready

    def __call__(self, argv, *, input_text=None, timeout_seconds=30):
        self.calls.append((tuple(argv), input_text, timeout_seconds))
        if argv[0] == "slack-receipts":
            return CommandReceipt(1, "", "unavailable")
        if argv[0] == "gws":
            return CommandReceipt(0 if self.fallback_ready else 1, "{}", "")
        raise AssertionError(f"unexpected readiness command: {argv}")


def _add_email_fallback(config_path) -> None:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    config["notifications"]["transports"].append(
        {
            "transport_id": "sensitive-fallback-transport-id",
            "adapter_type": "gws_email",
            "credential_ref": "credential-ref:gws",
            "routing": {
                "recipient": "sensitive-email@example.invalid",
                "subject_prefix": "sensitive subject",
            },
        }
    )
    config_path.write_text(json.dumps(config), encoding="utf-8")


def _add_second_service(config_path, *, enabled: bool = True) -> None:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    service = json.loads(json.dumps(config["services"][0]))
    service["service_id"] = "second-service"
    service["providers"][0]["provider_id"] = "second-provider"
    target = json.loads(json.dumps(config["targets"][0]))
    target.update(
        {
            "target_id": "second-target",
            "service_id": "second-service",
            "access_partition_id": "profile:second",
            "enabled": enabled,
        }
    )
    config["services"].append(service)
    config["targets"].append(target)
    config["tick"]["aggregate_limits"] = {
        key: value * 2
        for key, value in config["tick"]["aggregate_limits"].items()
    }
    config_path.write_text(json.dumps(config), encoding="utf-8")


def test_preflight_returns_sanitized_ready_manifest_without_state_writes(tmp_path):
    config_path = tmp_path / "tick-config-v1.json"
    _write_config(config_path)
    commands = ReadyCommands()

    receipt = service_tick_runtime.preflight_tick_runtime(
        _request(),
        config_path=config_path,
        worker=object(),
        command_runner=commands,
    )

    assert receipt["status"] == "ready"
    assert receipt["config_revision"] == "preflight-1"
    assert receipt["schedule_id"] == "manual-default"
    assert receipt["lane_manifest"][0]["target_id_digest"].startswith("sha256:")
    assert receipt["lane_manifest"][0]["providers"][0]["adapter_type"] == (
        "x_agent_browser"
    )
    assert receipt["notification_transports"] == [
        {
            "ordinal": 0,
            "transport_id_digest": receipt["notification_transports"][0][
                "transport_id_digest"
            ],
            "adapter_type": "slack_receipts",
            "routing_digest": receipt["notification_transports"][0][
                "routing_digest"
            ],
            "readiness": "ready",
        }
    ]
    assert len(commands.calls) == 1
    assert "mcp" not in commands.calls[0][0]
    encoded = json.dumps(receipt, sort_keys=True)
    for sensitive in (
        "operator-sensitive query",
        "sensitive-service-id",
        "sensitive-provider-id",
        "sensitive-target-id",
        "sensitive-transport-id",
        "sensitive-fallback-transport-id",
        "sensitive-profile",
        "profile:sensitive",
        "browser:profile:sensitive",
        "credential-ref:sensitive",
        "credential-ref:ops",
        "operator-artifacts",
        "sensitive-workspace",
        "sensitive-recipient",
        "agent-browser.example.invalid",
    ):
        assert sensitive not in encoded
    assert not (tmp_path / "research.db").exists()
    assert not (tmp_path / "operator-artifacts").exists()


def test_preflight_and_enqueue_share_exact_tick_config_and_lane_identity(tmp_path):
    config_path = tmp_path / "tick-config-v1.json"
    _write_config(config_path)
    registry = build_acquisition_adapter_registry(object())
    request = _request()

    preflight = service_tick_runtime.preflight_tick_runtime(
        request,
        config_path=config_path,
        adapter_registry=registry,
        command_runner=ReadyCommands(),
    )
    enqueued = TickCoordinator(
        tmp_path / "research.db",
        config_path=config_path,
        adapter_registry=registry,
    ).enqueue_tick(request)

    assert preflight["tick_id"] == enqueued.tick_id
    assert preflight["config_revision"] == enqueued.config_revision
    assert preflight["config_digest"] == enqueued.config_digest
    assert [lane["lane_id"] for lane in preflight["lane_manifest"]] == [
        lane.lane_id for lane in enqueued.lanes
    ]


def test_service_scoped_preflight_and_enqueue_freeze_same_narrow_identity(tmp_path):
    config_path = tmp_path / "tick-config-v1.json"
    _write_config(config_path)
    _add_second_service(config_path)
    registry = build_acquisition_adapter_registry(object())
    request = _request()

    full = service_tick_runtime.preflight_tick_runtime(
        request,
        config_path=config_path,
        adapter_registry=registry,
        command_runner=ReadyCommands(),
    )
    scoped = service_tick_runtime.preflight_tick_runtime(
        request,
        config_path=config_path,
        adapter_registry=registry,
        command_runner=ReadyCommands(),
        service_ids=("second-service",),
    )
    enqueued = TickCoordinator(
        tmp_path / "research.db",
        config_path=config_path,
        adapter_registry=registry,
        service_ids=("second-service",),
    ).enqueue_tick(request)

    assert len(full["lane_manifest"]) == 2
    assert len(scoped["lane_manifest"]) == 1
    assert scoped["tick_id"] == enqueued.tick_id
    assert scoped["config_digest"] == enqueued.config_digest
    assert scoped["config_digest"] != full["config_digest"]
    assert scoped["tick_id"] != full["tick_id"]
    assert scoped["aggregate_limits"] == {
        "attempts": 1,
        "network_requests": 7,
        "wall_seconds": 30,
        "items": 3,
        "cost_cents": 0,
        "model_tokens": 0,
    }
    assert [lane["lane_id"] for lane in scoped["lane_manifest"]] == [
        lane.lane_id for lane in enqueued.lanes
    ]


@pytest.mark.parametrize(
    ("service_ids", "message"),
    [
        (("missing-service",), "unknown service"),
        (("sensitive-service-id", "sensitive-service-id"), "duplicate service"),
    ],
)
def test_service_scoped_preflight_rejects_invalid_selection_without_readiness(
    tmp_path, service_ids, message
):
    config_path = tmp_path / "tick-config-v1.json"
    _write_config(config_path)
    commands = ReadyCommands()

    with pytest.raises(TickConfigError, match=message):
        service_tick_runtime.preflight_tick_runtime(
            _request(),
            config_path=config_path,
            worker=object(),
            command_runner=commands,
            service_ids=service_ids,
        )

    assert commands.calls == []


def test_service_scoped_preflight_rejects_service_without_enabled_target(tmp_path):
    config_path = tmp_path / "tick-config-v1.json"
    _write_config(config_path)
    _add_second_service(config_path, enabled=False)
    commands = ReadyCommands()

    with pytest.raises(TickConfigError, match="no enabled target"):
        service_tick_runtime.preflight_tick_runtime(
            _request(),
            config_path=config_path,
            worker=object(),
            command_runner=commands,
            service_ids=("second-service",),
        )

    assert commands.calls == []


def test_preflight_preserves_configured_target_order(tmp_path):
    config_path = tmp_path / "tick-config-v1.json"
    _write_config(config_path)
    payload = json.loads(config_path.read_text(encoding="utf-8"))
    first_service = payload["services"][0]
    first_service["service_id"] = "z-source"
    second_service = json.loads(json.dumps(first_service))
    second_service["service_id"] = "a-source"
    payload["services"] = [first_service, second_service]
    first_target = payload["targets"][0]
    first_target.update({"target_id": "z-target", "service_id": "z-source"})
    second_target = json.loads(json.dumps(first_target))
    second_target.update({"target_id": "a-target", "service_id": "a-source"})
    payload["targets"] = [first_target, second_target]
    config_path.write_text(json.dumps(payload), encoding="utf-8")
    registry = build_acquisition_adapter_registry(object())
    request = _request()

    preflight = service_tick_runtime.preflight_tick_runtime(
        request,
        config_path=config_path,
        adapter_registry=registry,
        command_runner=ReadyCommands(),
    )
    enqueued = TickCoordinator(
        tmp_path / "research.db",
        config_path=config_path,
        adapter_registry=registry,
    ).enqueue_tick(request)

    assert [lane["lane_id"] for lane in preflight["lane_manifest"]] == [
        lane.lane_id for lane in enqueued.lanes
    ]


def test_service_cli_exposes_side_effect_free_tick_preflight():
    args = build_parser().parse_args(
        [
            "tick",
            "preflight",
            "--interval-from",
            "2026-08-03T00:00:00Z",
            "--interval-to",
            "2026-08-04T00:00:00Z",
            "--config",
            "/tmp/tick-config-v1.json",
        ]
    )

    assert args.tick_action == "preflight"
    assert args.schedule_id == "manual-default"
    assert args.config == "/tmp/tick-config-v1.json"
    assert not hasattr(args, "db")


def test_service_cli_exposes_repeatable_manual_service_scope():
    args = build_parser().parse_args(
        [
            "tick",
            "preflight",
            "--interval-from",
            "2026-08-03T00:00:00Z",
            "--interval-to",
            "2026-08-04T00:00:00Z",
            "--service",
            "facebook",
            "--service",
            "x",
        ]
    )

    assert args.service_ids == ["facebook", "x"]


def test_preflight_checks_notification_readiness_in_sequential_failover_order(
    tmp_path,
):
    config_path = tmp_path / "tick-config-v1.json"
    _write_config(config_path)
    _add_email_fallback(config_path)
    commands = FailoverCommands(fallback_ready=True)

    receipt = service_tick_runtime.preflight_tick_runtime(
        _request(),
        config_path=config_path,
        worker=object(),
        command_runner=commands,
    )

    assert [item["readiness"] for item in receipt["notification_transports"]] == [
        "unavailable",
        "ready",
    ]
    assert [call[0][0] for call in commands.calls] == ["slack-receipts", "gws"]
    encoded = json.dumps(receipt, sort_keys=True)
    assert "sensitive-email@example.invalid" not in encoded
    assert "sensitive subject" not in encoded


def test_preflight_fails_closed_when_notification_chain_is_unavailable(tmp_path):
    config_path = tmp_path / "tick-config-v1.json"
    _write_config(config_path)
    _add_email_fallback(config_path)

    with pytest.raises(
        NotificationPreflightError,
        match="no configured notification transport passed readiness",
    ):
        service_tick_runtime.preflight_tick_runtime(
            _request(),
            config_path=config_path,
            worker=object(),
            command_runner=FailoverCommands(fallback_ready=False),
        )


def test_preflight_stops_readiness_checks_after_first_ready_transport(tmp_path):
    config_path = tmp_path / "tick-config-v1.json"
    _write_config(config_path)
    _add_email_fallback(config_path)
    commands = ReadyCommands()

    receipt = service_tick_runtime.preflight_tick_runtime(
        _request(),
        config_path=config_path,
        worker=object(),
        command_runner=commands,
    )

    assert [item["readiness"] for item in receipt["notification_transports"]] == [
        "ready",
        "not_checked",
    ]
    assert len(commands.calls) == 1


def test_preflight_rejects_invalid_observation_endpoint_before_readiness(tmp_path):
    config_path = tmp_path / "tick-config-v1.json"
    _write_config(config_path)
    config = json.loads(config_path.read_text(encoding="utf-8"))
    config["observation"]["service_base_url"] = "file:///tmp/not-a-service"
    config_path.write_text(json.dumps(config), encoding="utf-8")
    commands = ReadyCommands()

    with pytest.raises(TickConfigError, match="observation.service_base_url"):
        service_tick_runtime.preflight_tick_runtime(
            _request(),
            config_path=config_path,
            worker=object(),
            command_runner=commands,
        )

    assert commands.calls == []


@pytest.mark.parametrize(
    ("enabled_field", "adapter_field", "capability"),
    [
        ("ocr_enabled", "ocr_adapter_type", "ocr"),
        (
            "semantic_sidecars_enabled",
            "semantic_sidecar_adapter_type",
            "semantic_sidecar",
        ),
    ],
)
def test_preflight_rejects_enabled_uninstalled_analysis_adapters_without_effects(
    tmp_path,
    enabled_field,
    adapter_field,
    capability,
):
    config_path = tmp_path / "tick-config-v1.json"
    _write_config(config_path)
    config = json.loads(config_path.read_text(encoding="utf-8"))
    config["analysis"][enabled_field] = True
    config["analysis"][adapter_field] = "not_installed_analysis"
    config_path.write_text(json.dumps(config), encoding="utf-8")
    commands = ReadyCommands()

    with pytest.raises(
        AnalysisAdapterError,
        match=(
            "analysis adapter is not installed: "
            f"not_installed_analysis/{capability}"
        ),
    ):
        service_tick_runtime.preflight_tick_runtime(
            _request(),
            config_path=config_path,
            worker=object(),
            command_runner=commands,
        )

    assert commands.calls == []
    assert not (tmp_path / "research.db").exists()
    assert not (tmp_path / "operator-artifacts").exists()


@pytest.mark.parametrize(
    "service_base_url",
    [
        "https://agent-browser.example.invalid:notaport",
        "https://agent-browser.example.invalid:70000",
        "https://agent-browser.example.invalid/retained\nstream",
    ],
)
def test_preflight_rejects_malformed_observation_authority_without_effects(
    tmp_path,
    service_base_url,
):
    config_path = tmp_path / "tick-config-v1.json"
    _write_config(config_path)
    config = json.loads(config_path.read_text(encoding="utf-8"))
    config["observation"]["service_base_url"] = service_base_url
    config_path.write_text(json.dumps(config), encoding="utf-8")
    commands = ReadyCommands()

    with pytest.raises(TickConfigError, match="observation.service_base_url"):
        service_tick_runtime.preflight_tick_runtime(
            _request(),
            config_path=config_path,
            worker=object(),
            command_runner=commands,
        )

    assert commands.calls == []
    assert not (tmp_path / "research.db").exists()
    assert not (tmp_path / "operator-artifacts").exists()
