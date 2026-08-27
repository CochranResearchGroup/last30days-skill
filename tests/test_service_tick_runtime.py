"""Production seams for user-scoped manual tick execution."""

from __future__ import annotations

import json
import base64
import sqlite3
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

import pytest

from lib import service_contracts as contracts
from lib.service_tick_builtin_adapters import build_acquisition_adapter_registry
from lib.service_tick_adapters import AdapterRegistry
from lib.service_tick_analysis import default_analysis_adapter_registry
from lib.service_tick_notifications import (
    CommandReceipt,
    _safe_message,
    build_notification_transports,
)
from lib.service_tick_observation import AgentBrowserObservationTransport
from lib.service_tick_runner import ProviderContext
from lib.service_tick_runtime import build_tick_runtime, default_tick_config_path
from lib.service_worker import WorkerExecutionError
from service import build_parser


class FixtureWorker:
    def __init__(self, result_factory):
        self.result_factory = result_factory
        self.requests = []

    def run(self, request):
        self.requests.append(request)
        return self.result_factory(request)


def _context(adapter_type="x_agent_browser", source="x"):
    return ProviderContext(
        tick_id="tick-001",
        execution_attempt_id="attempt-001",
        lane_id="lane-x",
        service_id=source,
        source=source,
        target_id="x-topic",
        selector={
            "query": "open source agents",
            "profile_id": "social-primary",
            "depth": "standard",
        },
        access_partition_id="profile:social-primary",
        retention_class="durable",
        provider_id="x-primary",
        adapter_type=adapter_type,
        limits={
            "attempts": 1,
            "network_requests": 7,
            "wall_seconds": 30,
            "items": 3,
            "cost_cents": 0,
            "model_tokens": 0,
        },
        interval_from="2026-08-03T00:00:00Z",
        interval_to="2026-08-04T00:00:00Z",
    )


def _result(
    request,
    *,
    status="succeeded",
    error=None,
    retry="none",
    attempted_count=None,
    observed_count=None,
    media=False,
    operator_url=None,
    rendered_page=None,
    diagnostics=None,
):
    items = (
        [
            {
                "source_native_id": "x-1",
                "url": "https://x.example.test/x-1",
                "title": "Agent update",
                "text": "An agent update from the isolated worker.",
                "author": "Example",
                "published_at": "2026-08-03T10:00:00Z",
                "metadata": {"surface": "post"},
                **(
                    {
                        "media": [
                            {
                                "source_url": "https://cdn.example.test/image.jpg",
                                "content_base64": base64.b64encode(b"image-bytes").decode("ascii"),
                                "mime_type": "image/jpeg",
                                "media_kind": "image",
                                "alt_text": "A queryable image",
                            }
                        ]
                    }
                    if media
                    else {}
                ),
            }
        ]
        if status in {"succeeded", "partial"}
        else []
    )
    observed = len(items) if observed_count is None else observed_count
    attempted = observed if attempted_count is None else attempted_count
    return contracts.AcquisitionWorkResult.from_dict(
        {
            "schema_version": 1,
            "work_id": request.work_id,
            "job_id": request.job_id,
            "lease_generation": request.lease_generation,
            "source": request.source,
            "adapter": request.adapter,
            "adapter_version": request.adapter_version,
            "status": status,
            "safe_error_code": error,
            "retry_class": retry,
            "retry_after_seconds": None,
            "observed_at": "2026-08-04T12:00:00Z",
            "fetched_at": "2026-08-04T12:00:01Z",
            "items": items,
            "item_count": len(items),
            "cost_cents": 0,
            "diagnostics": diagnostics or (
                {"failure_stage": "authentication"} if error else {}
            ),
            **({"operator_url": operator_url} if operator_url else {}),
            **(
                {
                    "rendered_page_base64": base64.b64encode(rendered_page).decode("ascii"),
                    "rendered_page_mime_type": "image/jpeg",
                }
                if rendered_page
                else {}
            ),
            "network_request_count": 2,
            "attempted_count": attempted,
            "observed_count": observed,
            "accepted_count": len(items),
            "rejected_count": observed - len(items),
        }
    )


@pytest.mark.parametrize(
    ("adapter_type", "source"),
    (
        ("x_agent_browser", "x"),
        ("facebook_agent_browser", "facebook"),
        ("linkedin_agent_browser", "linkedin"),
        ("linkedin_profile_agent_browser", "linkedin"),
        ("youtube_ytdlp", "youtube"),
        ("reddit_keyless", "reddit"),
        ("reddit_agent_browser", "reddit"),
        ("reddit_scrapecreators", "reddit"),
    ),
)
def test_installed_worker_adapters_preserve_nonzero_normalized_items(
    adapter_type, source
):
    worker = FixtureWorker(lambda request: _result(request))
    registry = build_acquisition_adapter_registry(worker)

    spec = registry.require(adapter_type, source=source, capability="collect")
    result = spec.collect(_context(adapter_type, source))

    assert result.status == "success"
    assert result.items[0].source_native_id == "x-1"
    assert spec.normalization_proof_ref == (
        "fixture:tests/test_service_tick_runtime.py:"
        f"test_installed_worker_adapters_preserve_nonzero_normalized_items:{adapter_type}"
    )
    assert result.usage == {
        "attempts": 1,
        "network_requests": 2,
        "wall_seconds": 1,
        "items": 1,
        "cost_cents": 0,
        "model_tokens": 0,
    }
    request = worker.requests[0]
    assert request.profile_id == "social-primary"
    assert request.query == "open source agents"
    assert request.item_limit == 3
    assert request.network_request_limit == 7
    assert request.wall_timeout_seconds == 30


def test_builtin_adapter_preserves_feed_surface_and_selector():
    worker = FixtureWorker(lambda request: _result(request))
    registry = build_acquisition_adapter_registry(worker)
    context = replace(
        _context(),
        target_id="x-home-feed",
        selector={
            "feed": "home",
            "profile_id": "social-primary",
            "depth": "standard",
        },
        surface_kind="feed",
    )

    registry.require(
        "x_agent_browser", source="x", capability="collect"
    ).collect(context)

    request = worker.requests[0]
    assert request.surface_kind == "feed"
    assert request.query == "home"


def test_builtin_adapter_bridge_preserves_worker_outcome_counts():
    worker = FixtureWorker(
        lambda request: _result(
            request,
            status="partial",
            error="extraction_empty",
            retry="content",
            attempted_count=3,
            observed_count=3,
        )
    )
    registry = build_acquisition_adapter_registry(worker)

    result = registry.require(
        "x_agent_browser", source="x", capability="collect"
    ).collect(_context())

    assert result.outcome_counts == {
        "attempted": 3,
        "observed": 3,
        "accepted": 1,
        "rejected": 2,
    }


def test_builtin_adapter_bridge_preserves_bounded_browser_operation_evidence():
    worker = FixtureWorker(
        lambda request: _result(
            request,
            status="failed",
            error="agent_browser_timeout",
            retry="transient",
            diagnostics={
                "browser_operations": [
                    {
                        "operation": "eval",
                        "status": "timed_out",
                        "duration_ms": 20_012,
                        "url": "https://private.example/secret",
                    }
                ]
            },
        )
    )

    result = build_acquisition_adapter_registry(worker).require(
        "facebook_agent_browser", source="facebook", capability="collect"
    ).collect(_context("facebook_agent_browser", "facebook"))

    assert result.browser_operations == (
        {"operation": "eval", "status": "timed_out", "duration_ms": 20_012},
    )


def test_builtin_adapter_bridge_preserves_safe_failure_stage_and_signature():
    signature = "sha256:" + "a" * 64
    worker = FixtureWorker(
        lambda request: _result(
            request,
            status="failed",
            error="agent_browser_error",
            retry="transient",
            diagnostics={
                "failure_stage": "authentication",
                "failure_reason_code": "service_tab_target_unsettled",
                "failure_signature": signature,
            },
        )
    )

    result = build_acquisition_adapter_registry(worker).require(
        "x_agent_browser", source="x", capability="collect"
    ).collect(_context("x_agent_browser", "x"))

    assert result.failure_stage == "authentication"
    assert result.failure_reason_code == "service_tab_target_unsettled"
    assert result.failure_signature == signature


def test_builtin_adapter_bridge_preserves_bounded_rejection_counts():
    worker = FixtureWorker(
        lambda request: _result(
            request,
            status="failed",
            error="quality_gate_failed",
            retry="content",
            diagnostics={
                "rejection_counts": {
                    "missing_date": 5,
                    "kind_unknown": 3,
                }
            },
        )
    )

    result = build_acquisition_adapter_registry(worker).require(
        "facebook_agent_browser", source="facebook", capability="collect"
    ).collect(_context("facebook_agent_browser", "facebook"))

    assert result.rejection_counts == {
        "missing_date": 5,
        "kind_unknown": 3,
    }


def test_builtin_adapter_bridge_preserves_media_and_agent_browser_incident_evidence():
    success_worker = FixtureWorker(lambda request: _result(request, media=True))
    success = build_acquisition_adapter_registry(success_worker).require(
        "x_agent_browser", source="x", capability="collect"
    ).collect(_context())

    assert success.items[0].media[0].content == b"image-bytes"
    assert success.items[0].media[0].media_kind == "image"

    failure_worker = FixtureWorker(
        lambda request: _result(
            request,
            status="awaiting_operator",
            error="auth_required",
            retry="operator",
            operator_url="https://guac.example.test/client/session-1",
            rendered_page=b"rendered-auth-page",
        )
    )
    failure = build_acquisition_adapter_registry(failure_worker).require(
        "x_agent_browser", source="x", capability="collect"
    ).collect(_context())

    assert failure.operator_url == "https://guac.example.test/client/session-1"
    assert failure.rendered_page == b"rendered-auth-page"
    assert failure.rendered_page_mime_type == "image/jpeg"

    partial_worker = FixtureWorker(
        lambda request: _result(
            request,
            status="partial",
            error="auth_required",
            retry="operator",
            media=True,
            operator_url="https://guac.example.test/client/session-2",
            rendered_page=b"rendered-partial-auth-page",
        )
    )
    partial = build_acquisition_adapter_registry(partial_worker).require(
        "x_agent_browser", source="x", capability="collect"
    ).collect(_context())

    assert partial.status == "partial"
    assert partial.items[0].media[0].content == b"image-bytes"
    assert partial.operator_url == "https://guac.example.test/client/session-2"
    assert partial.rendered_page == b"rendered-partial-auth-page"
    assert partial.rendered_page_mime_type == "image/jpeg"


def test_builtin_adapter_bridge_maps_operator_auth_to_non_retryable_failure():
    worker = FixtureWorker(
        lambda request: _result(
            request,
            status="awaiting_operator",
            error="auth_required",
            retry="operator",
        )
    )
    registry = build_acquisition_adapter_registry(worker)

    result = registry.require(
        "x_agent_browser", source="x", capability="collect"
    ).collect(_context())

    assert result.status == "failure"
    assert result.failure_class == "authentication"
    assert result.safe_error_code == "auth_required"


def test_builtin_adapter_bridge_preserves_typed_worker_timeout():
    def fail(_request):
        raise WorkerExecutionError("worker_timeout", contracts.RetryClass.TRANSIENT)

    registry = build_acquisition_adapter_registry(FixtureWorker(fail))

    result = registry.require(
        "facebook_agent_browser", source="facebook", capability="collect"
    ).collect(_context("facebook_agent_browser", "facebook"))

    assert result.status == "failure"
    assert result.failure_class == "transient"
    assert result.safe_error_code == "worker_timeout"
    assert result.usage == {
        "attempts": 1,
        "network_requests": 0,
        "wall_seconds": 30,
        "items": 0,
        "cost_cents": 0,
        "model_tokens": 0,
    }


def test_default_tick_config_is_always_user_scoped(tmp_path):
    assert default_tick_config_path(
        environ={"LAST30DAYS_CONFIG_DIR": str(tmp_path / "config")},
        home=tmp_path / "home",
    ) == tmp_path / "config" / "tick-config-v1.json"
    assert default_tick_config_path(environ={}, home=tmp_path / "home") == (
        tmp_path / "home" / ".config" / "last30days" / "tick-config-v1.json"
    )


def test_runtime_accepts_an_explicit_installed_provider_registry_and_absolute_artifacts(
    tmp_path,
):
    config_path = tmp_path / "tick-config-v1.json"
    config = {
        "query": {"embedding_space": "local-hash-v1"},
        "artifacts": {"root": str(tmp_path / "artifacts")},
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
                    "transport_id": "ops-fallback",
                    "adapter_type": "gws_email",
                    "routing": {
                        "recipient": "operator@example.test",
                        "subject_prefix": "tick incident",
                    },
                }
            ]
        },
        "observation": {
            "adapter_type": "agent_browser_service",
            "service_base_url": "http://127.0.0.1:4848",
        },
    }
    config_path.write_text(json.dumps(config), encoding="utf-8")
    registry = AdapterRegistry()
    analysis_registry = default_analysis_adapter_registry()

    runtime = build_tick_runtime(
        tmp_path / "research.db",
        config_path=config_path,
        adapter_registry=registry,
        analysis_registry=analysis_registry,
    )

    assert runtime.runner.registry is registry
    assert runtime.coordinator.adapter_registry is registry
    assert runtime.runner.analysis_registry is analysis_registry
    assert isinstance(
        runtime.runner.incidents.observation_transport,
        AgentBrowserObservationTransport,
    )

    config["artifacts"]["root"] = "relative-artifacts"
    config_path.write_text(json.dumps(config), encoding="utf-8")
    with pytest.raises(RuntimeError, match="absolute"):
        build_tick_runtime(
            tmp_path / "relative.db",
            config_path=config_path,
            adapter_registry=registry,
            analysis_registry=analysis_registry,
        )


class FixtureCommands:
    def __init__(self):
        self.calls = []

    def __call__(self, argv, *, input_text=None, timeout_seconds=30):
        self.calls.append((tuple(argv), input_text, timeout_seconds))
        if tuple(argv[:3]) == ("slack-receipts", "workspaces", "verify"):
            return CommandReceipt(0, "{}", "")
        if "mcp" in argv:
            return CommandReceipt(
                0,
                json.dumps(
                    {
                        "jsonrpc": "2.0",
                        "id": 2,
                        "result": {
                            "content": [
                                {"type": "text", "text": '{"action_id":"42"}'}
                            ]
                        },
                    }
                )
                + "\n",
                "",
            )
        raise AssertionError(f"unexpected command: {argv}")


def test_notification_factory_uses_fixed_adapter_machinery_and_configured_routing():
    commands = FixtureCommands()
    transports = build_notification_transports(
        {
            "transports": [
                {
                    "transport_id": "ops-primary",
                    "adapter_type": "slack_receipts",
                    "credential_ref": "credential-ref:ops",
                    "routing": {
                        "workspace": "default",
                        "channel_ref": "recipient-ref:operator",
                    },
                }
            ],
            "reminder_seconds": 3600,
        },
        command_runner=commands,
    )

    assert transports[0].readiness() is True
    delivery_ref = transports[0].send(
        {
            "incident_id": "incident-001",
            "notification_kind": "detected",
            "notification_sequence": 1,
            "incident_type": "captcha_required",
            "severity": "critical",
            "source": "x",
            "stage": "collection",
            "safe_summary": "Human verification is required.",
            "protected_artifact_ref": "objects/protected/ref",
            "operator_url": "https://guac.example.test/client/manual-auth",
        }
    )

    assert delivery_ref.startswith("slack-receipts:sha256:")
    mcp_input = next(input_text for argv, input_text, _ in commands.calls if "mcp" in argv)
    assert '"name":"messages.send"' in mcp_input
    assert '"workspace":"default"' in mcp_input
    assert '"channel_ref":"recipient-ref:operator"' in mcp_input
    assert '"idempotency_key":"incident-001:detected:1"' in mcp_input
    assert "Open the operator link and complete the manual browser check" in mcp_input
    assert "https://guac.example.test/client/manual-auth" in mcp_input
    assert "credential-ref:ops" not in mcp_input


@pytest.mark.parametrize(
    "operator_url",
    (
        "http://guac.example.test/client/manual-auth",
        "https://localhost/client/manual-auth",
        "https://127.0.0.1/client/manual-auth",
    ),
)
def test_browser_notification_never_renders_an_unsafe_operator_link(operator_url):
    message = _safe_message(
        {
            "incident_id": "incident-unsafe-link",
            "notification_kind": "detected",
            "notification_sequence": 1,
            "incident_type": "reauthentication_required",
            "severity": "critical",
            "source": "facebook",
            "stage": "collection",
            "safe_summary": "Manual authentication is required.",
            "protected_artifact_ref": None,
            "operator_url": operator_url,
        }
    )

    assert operator_url not in message
    assert "operator link is unavailable" in message


def test_resolved_browser_notification_does_not_repeat_a_stale_operator_link():
    message = _safe_message(
        {
            "incident_id": "incident-resolved",
            "notification_kind": "resolved",
            "notification_sequence": 3,
            "incident_type": "captcha_required",
            "severity": "critical",
            "source": "facebook",
            "stage": "collection",
            "safe_summary": "The browser session recovered.",
            "protected_artifact_ref": None,
            "operator_url": "https://guac.example.test/client/stale",
        }
    )

    assert "https://guac.example.test/client/stale" not in message
    assert "browser incident resolved" in message


def test_resolved_reauthentication_notification_is_not_an_active_auth_alert():
    message = _safe_message(
        {
            "incident_id": "incident-resolved-auth",
            "notification_kind": "resolved",
            "notification_sequence": 3,
            "incident_type": "reauthentication_required",
            "severity": "critical",
            "source": "x",
            "stage": "collection",
            "safe_summary": "Provider reported reauthentication_required.",
            "protected_artifact_ref": None,
            "operator_url": "https://guac.example.test/client/stale",
        }
    )

    assert "status: resolved" in message
    assert "previous incident type: reauthentication_required" in message
    assert "type: reauthentication_required" not in message.splitlines()
    assert "complete the manual browser check" not in message


def test_production_manual_runtime_executes_without_creating_a_schedule(tmp_path):
    config_path = tmp_path / "tick-config-v1.json"
    config_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "config_revision": "runtime-1",
                "services": [
                    {
                        "service_id": "x",
                        "source": "x",
                        "providers": [
                            {
                                "provider_id": "x-primary",
                                "adapter_type": "x_agent_browser",
                                "resource_keys": ["browser:profile:social-primary"],
                                "fallback_on": [],
                                "credential_ref": "profile-ref:social-primary",
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
                        "target_id": "x-topic",
                        "service_id": "x",
                        "surface_kind": "topic",
                        "selector": {
                            "query": "open source agents",
                            "profile_id": "social-primary",
                            "depth": "standard",
                        },
                        "access_partition_id": "profile:social-primary",
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
                    "root": str(tmp_path / "artifacts"),
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
                            "transport_id": "ops-primary",
                            "adapter_type": "slack_receipts",
                            "credential_ref": "credential-ref:ops",
                            "routing": {
                                "workspace": "default",
                                "channel_ref": "recipient-ref:operator",
                            },
                        }
                    ],
                    "reminder_seconds": 3600,
                },
                "query": {
                    "embedding_space": "local-hash-v1",
                    "fusion_version": "rrf-v1",
                },
            }
        ),
        encoding="utf-8",
    )
    worker = FixtureWorker(lambda request: _result(request))
    commands = FixtureCommands()
    now = datetime(2026, 8, 4, 12, 0, tzinfo=timezone.utc)
    db_path = tmp_path / "research.db"
    runtime = build_tick_runtime(
        db_path,
        config_path=config_path,
        worker=worker,
        command_runner=commands,
        clock=lambda: now,
    )

    receipt = runtime.coordinator.enqueue_tick(
        contracts.TickRequest.from_dict(
            {
                "schema_version": 1,
                "schedule_id": "manual-default",
                "interval_from": "2026-08-03T00:00:00Z",
                "interval_to": "2026-08-04T00:00:00Z",
                "trigger": "manual",
            }
        )
    )

    assert receipt.state.value == "complete"
    assert len(worker.requests) == 1
    conn = sqlite3.connect(db_path)
    assert conn.execute(
        "SELECT COUNT(*) FROM collection_specs WHERE enabled = 1"
    ).fetchone()[0] == 0
    conn.close()


def test_service_cli_exposes_manual_tick_and_explicit_incident_gate_actions():
    parser = build_parser()
    enqueue = parser.parse_args(
        [
            "tick",
            "enqueue",
            "--interval-from",
            "2026-08-03T00:00:00Z",
            "--interval-to",
            "2026-08-04T00:00:00Z",
        ]
    )
    get = parser.parse_args(["tick", "get", "tick-001"])
    schedule_status = parser.parse_args(["tick", "schedule", "status"])
    observe = parser.parse_args(
        ["tick", "incident", "observe", "incident-001"]
    )

    assert enqueue.tick_action == "enqueue"
    assert enqueue.schedule_id == "manual-default"
    assert get.tick_action == "get"
    assert schedule_status.tick_action == "schedule"
    assert schedule_status.schedule_action == "status"
    assert observe.incident_action == "observe"
    assert not hasattr(observe, "operator_url")
