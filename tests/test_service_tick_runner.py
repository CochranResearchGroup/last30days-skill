"""End-to-end deterministic manual tick over in-memory provider adapters."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import datetime, timedelta, timezone

import pytest

from lib import service_contracts as contracts
from lib.service_tick import TickCoordinator
from lib.service_tick_adapters import AdapterRegistry, AdapterSpec
from lib.service_tick_incidents import IncidentManager
from lib.service_tick_media import (
    ContentAddressedArtifactStore,
    MediaDerivativePublisher,
    OcrRegion,
    SemanticSidecar,
)
from lib.service_tick_query import TickSnapshotPublisher
from lib.service_tick_runner import (
    CollectedItem,
    CollectedMedia,
    ProviderResult,
    TickRunner,
)


NOW = datetime(2026, 8, 4, 12, 0, tzinfo=timezone.utc)


class FixtureEmbedding:
    model = "fixture-space-v1"

    def embed(self, texts):
        return [
            [
                float("revenue" in text.casefold()),
                float("chart" in text.casefold()),
                float("agents" in text.casefold()),
            ]
            for text in texts
        ]


class FixtureNotification:
    transport_id = "fixture-notification"

    def __init__(self):
        self.payloads = []

    def readiness(self):
        return True

    def send(self, payload):
        self.payloads.append(payload)
        return "delivery:fixture:1"


def _limits(*, items=10, requests=10, model_tokens=100, attempts=1):
    return {
        "attempts": attempts,
        "network_requests": requests,
        "wall_seconds": 30,
        "items": items,
        "cost_cents": 0,
        "model_tokens": model_tokens,
    }


def _usage(*, items=0, requests=1, wall_seconds=1, model_tokens=0):
    return {
        "attempts": 1,
        "network_requests": requests,
        "wall_seconds": wall_seconds,
        "items": items,
        "cost_cents": 0,
        "model_tokens": model_tokens,
    }


def _provider(provider_id, adapter_type, resource_key):
    return {
        "provider_id": provider_id,
        "adapter_type": adapter_type,
        "resource_keys": [resource_key],
        "fallback_on": [],
        "limits": _limits(),
    }


def _write_config(path):
    services = [
        ("web", "web", "fixture_success", "network:web"),
        ("reddit", "reddit", "fixture_empty", "network:reddit"),
        ("x", "x", "fixture_captcha", "browser:profile-ref:social"),
    ]
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "config_revision": "runner-config-1",
                "services": [
                    {
                        "service_id": service_id,
                        "source": source,
                        "providers": [
                            _provider(
                                f"{service_id}-provider", adapter_type, resource_key
                            )
                        ],
                    }
                    for service_id, source, adapter_type, resource_key in services
                ],
                "targets": [
                    {
                        "target_id": f"{service_id}-target",
                        "service_id": service_id,
                        "surface_kind": "topic",
                        "selector": {"topic": "agents"},
                        "access_partition_id": (
                            "profile:social" if service_id == "x" else "public"
                        ),
                        "retention_class": "durable",
                        "enabled": True,
                    }
                    for service_id, *_ in services
                ],
                "tick": {
                    "timezone": "UTC",
                    "lateness_seconds": 86400,
                    "aggregate_limits": {
                        "attempts": 5,
                        "network_requests": 50,
                        "wall_seconds": 120,
                        "items": 20,
                        "cost_cents": 0,
                        "model_tokens": 200,
                    },
                },
                "artifacts": {
                    "root": str(path.parent / "artifacts"),
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
                            "transport_id": "fixture-notification",
                            "adapter_type": "fixture",
                            "credential_ref": "credential-ref:fixture",
                            "routing": {"recipient_ref": "recipient-ref:fixture"},
                        }
                    ],
                    "reminder_seconds": 3600,
                },
                "query": {
                    "embedding_space": "fixture-space-v1",
                    "fusion_version": "rrf-v1",
                },
            }
        ),
        encoding="utf-8",
    )


def _write_custom_config(
    path,
    services,
    targets,
    *,
    aggregate_limits=None,
    anomaly_rules=None,
    lateness_seconds=86400,
):
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "config_revision": "runner-custom-config-1",
                "services": services,
                "targets": targets,
                "tick": {
                    "timezone": "UTC",
                    "lateness_seconds": lateness_seconds,
                    "aggregate_limits": aggregate_limits or _limits(items=20),
                },
                "artifacts": {
                    "root": str(path.parent / "artifacts"),
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
                    **(
                        {"anomaly_rules": anomaly_rules}
                        if anomaly_rules is not None
                        else {}
                    ),
                },
                "notifications": {
                    "transports": [
                        {
                            "transport_id": "fixture-notification",
                            "adapter_type": "fixture",
                            "credential_ref": "credential-ref:fixture",
                            "routing": {"recipient_ref": "recipient-ref:fixture"},
                        }
                    ],
                    "reminder_seconds": 3600,
                },
                "query": {
                    "embedding_space": "fixture-space-v1",
                    "fusion_version": "rrf-v1",
                },
            }
        ),
        encoding="utf-8",
    )


def _target(service_id, *, partition="public"):
    return {
        "target_id": f"{service_id}-target",
        "service_id": service_id,
        "surface_kind": "topic",
        "selector": {"topic": "agents"},
        "access_partition_id": partition,
        "retention_class": "durable",
        "enabled": True,
    }


def _coordinator(
    tmp_path,
    services,
    targets,
    specs,
    *,
    aggregate_limits=None,
    anomaly_rules=None,
    lateness_seconds=86400,
    clock=None,
    fault_injector=None,
):
    active_clock = clock or (lambda: NOW)
    db_path = tmp_path / "research.db"
    config_path = tmp_path / "tick-config-v1.json"
    _write_custom_config(
        config_path,
        services,
        targets,
        aggregate_limits=aggregate_limits,
        anomaly_rules=anomaly_rules,
        lateness_seconds=lateness_seconds,
    )
    registry = AdapterRegistry(specs)
    artifacts = ContentAddressedArtifactStore(tmp_path / "artifacts")
    media = MediaDerivativePublisher(db_path, artifacts, clock=active_clock)
    incidents = IncidentManager(db_path, media, clock=active_clock)
    snapshots = TickSnapshotPublisher(db_path, FixtureEmbedding(), clock=active_clock)
    notification = FixtureNotification()
    runner = TickRunner(
        db_path,
        registry,
        media=media,
        incidents=incidents,
        snapshots=snapshots,
        notification_transports=(notification,),
        clock=active_clock,
        fault_injector=fault_injector,
    )
    coordinator = TickCoordinator(
        db_path,
        config_path=config_path,
        adapter_registry=registry,
        runner=runner,
        clock=active_clock,
    )
    return coordinator, runner, db_path, config_path, registry, snapshots


def _request(start, end):
    return contracts.TickRequest.from_dict(
        {
            "schema_version": 1,
            "schedule_id": "manual-default",
            "interval_from": start,
            "interval_to": end,
            "trigger": "manual",
        }
    )


def test_manual_tick_runs_every_lane_raw_first_and_publishes_one_degraded_snapshot(
    tmp_path,
):
    db_path = tmp_path / "research.db"
    config_path = tmp_path / "tick-config-v1.json"
    _write_config(config_path)
    call_order = []
    sidecar = SemanticSidecar(
        literal_description="A line chart rises from left to right.",
        observable_entities=("line chart",),
        observable_relationships=("line rises",),
        objects_actions=("line:rising",),
        inferred_context=("may depict increasing revenue",),
        search_terms=("revenue chart",),
        uncertainty=("axis values are unclear",),
        model_provider="fixture-model",
        model_version="1",
        input_refs=("image", "ocr", "alt-text"),
    )

    def success(context):
        call_order.append(context.service_id)
        return ProviderResult.success(
            items=(
                CollectedItem(
                    source_native_id="web-1",
                    url="https://example.test/report",
                    title="Agent revenue report",
                    text="Agents increased quarterly revenue.",
                    author="Example",
                    published_at="2026-08-03T10:00:00Z",
                    media=(
                        CollectedMedia(
                            source_url="https://example.test/chart.png",
                            content=b"rendered-chart-bytes",
                            mime_type="image/png",
                            media_kind="image",
                            alt_text="Revenue chart",
                            ocr_regions=(
                                OcrRegion(0, "Revenue", (0, 0, 100, 30), 0.99),
                            ),
                            detected_language="en",
                            ocr_engine="fixture-ocr",
                            ocr_engine_version="1",
                            semantic_sidecar=sidecar,
                        ),
                    ),
                ),
            ),
            usage={
                "attempts": 1,
                "network_requests": 2,
                "wall_seconds": 1,
                "items": 1,
                "cost_cents": 0,
                "model_tokens": 20,
            },
        )

    def empty(context):
        call_order.append(context.service_id)
        return ProviderResult.empty(
            usage={
                "attempts": 1,
                "network_requests": 1,
                "wall_seconds": 1,
                "items": 0,
                "cost_cents": 0,
                "model_tokens": 0,
            }
        )

    def captcha(context):
        call_order.append(context.service_id)
        return ProviderResult.failure(
            failure_class="challenge",
            safe_error_code="captcha_required",
            page_signals=("captcha_required",),
            rendered_page=b"exact-captcha-page",
            rendered_page_mime_type="image/png",
            usage={
                "attempts": 1,
                "network_requests": 1,
                "wall_seconds": 1,
                "items": 0,
                "cost_cents": 0,
                "model_tokens": 0,
            },
        )

    registry = AdapterRegistry(
        [
            AdapterSpec("fixture_success", frozenset({"collect"}), None, success, "fixture:runner:success"),
            AdapterSpec("fixture_empty", frozenset({"collect"}), None, empty, "fixture:runner:empty"),
            AdapterSpec("fixture_captcha", frozenset({"collect"}), None, captcha, "fixture:runner:captcha"),
        ]
    )
    artifacts = ContentAddressedArtifactStore(tmp_path / "artifacts")
    media = MediaDerivativePublisher(db_path, artifacts, clock=lambda: NOW)
    incidents = IncidentManager(db_path, media, clock=lambda: NOW)
    snapshots = TickSnapshotPublisher(db_path, FixtureEmbedding(), clock=lambda: NOW)
    notification = FixtureNotification()
    runner = TickRunner(
        db_path,
        registry,
        media=media,
        incidents=incidents,
        snapshots=snapshots,
        notification_transports=(notification,),
        clock=lambda: NOW,
    )
    coordinator = TickCoordinator(
        db_path,
        config_path=config_path,
        adapter_registry=registry,
        runner=runner,
        clock=lambda: NOW,
    )
    request = contracts.TickRequest.from_dict(
        {
            "schema_version": 1,
            "schedule_id": "manual-default",
            "interval_from": "2026-08-03T00:00:00Z",
            "interval_to": "2026-08-04T00:00:00Z",
            "trigger": "manual",
        }
    )

    completed = coordinator.enqueue_tick(request)
    repeated = coordinator.enqueue_tick(request)

    assert completed == repeated
    assert call_order == ["web", "reddit", "x"]
    assert completed.state is contracts.TickState.COMPLETE_DEGRADED
    assert {lane.service_id: lane.state.value for lane in completed.lanes} == {
        "reddit": "empty",
        "web": "success",
        "x": "blocked_human",
    }
    assert len(notification.payloads) == 1
    assert len(completed.provider_attempt_ids) == 3
    assert len(completed.resource_lease_ids) == 3
    assert len(completed.source_version_ids) == 1
    assert len(completed.incident_ids) == 1
    assert len(completed.incident_transition_ids) == 1
    assert len(completed.notification_delivery_ids) == 1
    assert completed.anomaly_result_ids == ()
    assert len(completed.artifact_ids) == 2
    assert len(completed.derivative_ids) == 2
    assert completed.catalog_cluster_ids == ()
    assert completed.snapshot_id == snapshots.current().snapshot_id
    assert completed.head_promoted is True
    assert completed.receipt_manifests["evidence"] == [
        {
            "content_hash": completed.receipt_manifests["evidence"][0][
                "content_hash"
            ],
            "version_id": completed.source_version_ids[0],
        }
    ]
    assert completed.receipt_manifests["incident_artifacts"] == [
        {
            "artifact_ref": completed.receipt_manifests["incident_artifacts"][0][
                "artifact_ref"
            ],
            "asset_id": completed.receipt_manifests["incident_artifacts"][0][
                "asset_id"
            ],
            "capture_reason": "detected",
            "incident_artifact_id": completed.receipt_manifests[
                "incident_artifacts"
            ][0]["incident_artifact_id"],
            "incident_id": completed.incident_ids[0],
            "tick_id": completed.tick_id,
        }
    ]
    assert completed.receipt_manifests["events"][0]["event_type"] == "tick_enqueued"
    assert completed.receipt_manifests["events"][-1]["event_type"] == "tick_completed"
    assert completed.receipt_manifests["snapshot"]["snapshot_id"] == completed.snapshot_id
    for name, manifest in completed.receipt_manifests.items():
        encoded = json.dumps(
            manifest,
            allow_nan=False,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
        assert completed.manifest_digests[name] == (
            "sha256:" + hashlib.sha256(encoded).hexdigest()
        )
    unsafe = completed.to_dict()
    unsafe["receipt_manifests"] = {
        **unsafe["receipt_manifests"],
        "events": [{"cookie": "must-not-enter-a-tick-receipt"}],
    }
    with pytest.raises(contracts.ContractValidationError, match="forbidden field"):
        contracts.TickReceipt.from_dict(unsafe)
    assert completed.budget_summary["tick"]["consumed"] == {
        "attempts": 3,
        "cost_cents": 0,
        "items": 1,
        "model_tokens": 20,
        "network_requests": 4,
        "wall_seconds": 3,
    }
    assert set(completed.manifest_digests) == {
        "anomalies",
        "artifacts",
        "budgets",
        "budget_events",
        "catalog",
        "derivatives",
        "evidence",
        "incidents",
        "incident_artifacts",
        "notifications",
        "providers",
        "provider_attempts",
        "provider_results",
        "resource_leases",
        "snapshot",
        "stages",
        "events",
        "execution_attempts",
    }
    assert completed.versions["database_schema"] == "16"
    assert completed.versions["embedding_space"] == "fixture-space-v1"
    assert snapshots.current().tick_id == completed.tick_id
    results = snapshots.query("revenue chart", access_partitions=("public",))
    assert {channel for result in results for channel in result.matching_channels} >= {
        "lexical_source",
        "ocr",
        "semantic_sidecar",
    }
    conn = sqlite3.connect(db_path)
    assert conn.execute(
        "SELECT COUNT(*) FROM service_tick_provider_attempts"
    ).fetchone()[0] == 3
    assert conn.execute(
        "SELECT COUNT(*) FROM service_source_versions"
    ).fetchone()[0] == 1
    assert conn.execute(
        """SELECT COUNT(*) FROM service_tick_stages
           WHERE state IN ('pending', 'running')"""
    ).fetchone()[0] == 0
    assert conn.execute(
        """SELECT event_type FROM service_tick_events
           WHERE tick_id = ? ORDER BY sequence""",
        (completed.tick_id,),
    ).fetchall().index(("raw_published",)) < conn.execute(
        """SELECT event_type FROM service_tick_events
           WHERE tick_id = ? ORDER BY sequence""",
        (completed.tick_id,),
    ).fetchall().index(("derivatives_published",))
    assert conn.execute(
        "SELECT COUNT(*) FROM service_incident_observations"
    ).fetchone()[0] == 0
    assert conn.execute(
        "SELECT COUNT(*) FROM collection_specs WHERE enabled = 1"
    ).fetchone()[0] == 0
    conn.close()


def test_partial_provider_evidence_publishes_raw_before_blocking_the_lane(tmp_path):
    def partial(_context):
        return ProviderResult(
            status="partial",
            items=(
                CollectedItem(
                    source_native_id="x-partial-1",
                    url="https://x.example.test/x-partial-1",
                    title="Evidence before authentication interruption",
                    text="The provider returned this item before requiring a human.",
                    author="Example",
                    published_at="2026-08-03T10:00:00Z",
                ),
            ),
            failure_class="authentication",
            safe_error_code="auth_required",
            operator_url="https://guac.example.test/client/session-partial",
            usage=_usage(items=1),
        )

    coordinator, _, db_path, _, _, _ = _coordinator(
        tmp_path,
        [
            {
                "service_id": "x",
                "source": "x",
                "providers": [
                    _provider("browser", "fixture_partial", "profile:x")
                ],
            }
        ],
        [_target("x", partition="private:x")],
        [
            AdapterSpec(
                "fixture_partial",
                frozenset({"collect"}),
                None,
                partial,
                "fixture:runner:partial",
            )
        ],
    )

    receipt = coordinator.enqueue_tick(
        _request("2026-08-03T00:00:00Z", "2026-08-04T00:00:00Z")
    )

    assert receipt.state is contracts.TickState.COMPLETE_DEGRADED
    assert receipt.lanes[0].state.value == "blocked_human"
    assert len(receipt.source_version_ids) == 1
    conn = sqlite3.connect(db_path)
    assert conn.execute(
        "SELECT state FROM service_tick_provider_attempts"
    ).fetchone() == ("blocked_human",)
    assert conn.execute(
        "SELECT state FROM service_tick_stages WHERE stage_name = 'collection'"
    ).fetchone() == ("blocked_human",)
    assert conn.execute(
        "SELECT COUNT(*) FROM service_tick_events WHERE event_type = 'raw_published'"
    ).fetchone() == (1,)
    conn.close()


def test_configured_fallback_is_sequential_and_a_failed_provider_is_not_retried(
    tmp_path,
):
    calls = []

    def transient(context):
        calls.append(context.provider_id)
        return ProviderResult.failure(
            failure_class="transient",
            safe_error_code="upstream_timeout",
            usage=_usage(),
        )

    def success(context):
        calls.append(context.provider_id)
        return ProviderResult.success(
            items=(
                CollectedItem(
                    source_native_id="fallback-1",
                    url="https://example.test/fallback-1",
                    title="Fallback result",
                    text="A configured fallback succeeded.",
                    author=None,
                    published_at=None,
                ),
            ),
            usage=_usage(items=1),
        )

    services = [
        {
            "service_id": "web",
            "source": "web",
            "providers": [
                {
                    **_provider("primary", "fixture_transient", "network:primary"),
                    "fallback_on": ["transient"],
                },
                _provider("fallback", "fixture_success", "network:fallback"),
            ],
        }
    ]
    coordinator, _, db_path, _, _, _ = _coordinator(
        tmp_path,
        services,
        [_target("web")],
        [
            AdapterSpec("fixture_transient", frozenset({"collect"}), None, transient, "fixture:runner:transient"),
            AdapterSpec("fixture_success", frozenset({"collect"}), None, success, "fixture:runner:success"),
        ],
        aggregate_limits={**_limits(items=10), "attempts": 2},
    )

    receipt = coordinator.enqueue_tick(
        _request("2026-08-03T00:00:00Z", "2026-08-04T00:00:00Z")
    )

    assert receipt.state is contracts.TickState.COMPLETE
    assert calls == ["primary", "fallback"]
    conn = sqlite3.connect(db_path)
    assert conn.execute(
        """SELECT a.state FROM service_tick_provider_attempts AS a
           JOIN service_tick_providers AS p
             ON p.provider_manifest_id = a.provider_manifest_id
           ORDER BY p.provider_ordinal"""
    ).fetchall() == [("failure",), ("success",)]
    conn.close()


def test_cross_source_catalog_clusters_exact_duplicates_without_merging_evidence(
    tmp_path,
):
    def collect(context):
        return ProviderResult.success(
            items=(
                CollectedItem(
                    source_native_id=f"{context.service_id}-native-1",
                    url=f"https://{context.service_id}.example.test/item-1",
                    title="Shared investigation of agents",
                    text="Two services independently preserve this exact report.",
                    author=None,
                    published_at="2026-08-03T10:00:00Z",
                ),
            ),
            usage=_usage(items=1),
        )

    services = [
        {
            "service_id": service_id,
            "source": service_id,
            "providers": [
                _provider(
                    f"{service_id}-provider",
                    "fixture",
                    f"network:{service_id}",
                )
            ],
        }
        for service_id in ("reddit", "web")
    ]
    coordinator, _, db_path, _, _, snapshots = _coordinator(
        tmp_path,
        services,
        [_target("reddit"), _target("web")],
        [
            AdapterSpec(
                "fixture",
                frozenset({"collect"}),
                None,
                collect,
                "fixture:runner:exact-cross-source",
            )
        ],
        aggregate_limits=_limits(items=10, attempts=2),
    )

    receipt = coordinator.enqueue_tick(
        _request("2026-08-03T00:00:00Z", "2026-08-04T00:00:00Z")
    )

    assert receipt.state is contracts.TickState.COMPLETE
    assert len(receipt.source_version_ids) == 2
    assert len(receipt.catalog_cluster_ids) == 1
    assert len(receipt.receipt_manifests["catalog"]["members"]) == 2
    results = snapshots.query("agents", access_partitions=("public",))
    assert any("catalog" in result.matching_channels for result in results)
    conn = sqlite3.connect(db_path)
    assert conn.execute("SELECT COUNT(*) FROM service_source_records").fetchone()[0] == 2
    conn.close()


def test_enabled_image_analysis_fails_independently_when_adapter_output_is_missing(
    tmp_path,
):
    def collect(_context):
        return ProviderResult.success(
            items=(
                CollectedItem(
                    source_native_id="image-without-analysis",
                    url="https://example.test/image-post",
                    title="Image post",
                    text="The source item remains publishable.",
                    author=None,
                    published_at=None,
                    media=(
                        CollectedMedia(
                            source_url="https://example.test/image.png",
                            content=b"image-without-analysis-output",
                            mime_type="image/png",
                            media_kind="image",
                            alt_text="An image awaiting analysis",
                        ),
                    ),
                ),
            ),
            usage=_usage(items=1),
        )

    services = [
        {
            "service_id": "web",
            "source": "web",
            "providers": [_provider("web-provider", "fixture", "network:web")],
        }
    ]
    coordinator, _, _, _, _, snapshots = _coordinator(
        tmp_path,
        services,
        [_target("web")],
        [
            AdapterSpec(
                "fixture",
                frozenset({"collect"}),
                None,
                collect,
                "fixture:runner:missing-analysis-output",
            )
        ],
    )

    receipt = coordinator.enqueue_tick(
        _request("2026-08-03T00:00:00Z", "2026-08-04T00:00:00Z")
    )

    assert receipt.state is contracts.TickState.COMPLETE_DEGRADED
    assert receipt.lanes[0].state.value == "success"
    lane_id = receipt.lanes[0].lane_id
    assert receipt.stage_states[f"lane:{lane_id}:media"] == "success"
    assert receipt.stage_states[f"lane:{lane_id}:ocr"] == "failure"
    assert receipt.stage_states[f"lane:{lane_id}:semantic_sidecar"] == "failure"
    assert [
        item["state"] for item in receipt.receipt_manifests["derivatives"]
    ] == ["failure", "failure"]
    assert snapshots.query("publishable", access_partitions=("public",))


def test_aggregate_budget_exhaustion_terminalizes_only_unstarted_lanes(tmp_path):
    calls = []

    def success(context):
        calls.append(context.service_id)
        return ProviderResult.success(
            items=(
                CollectedItem(
                    source_native_id=f"{context.service_id}-1",
                    url=f"https://example.test/{context.service_id}-1",
                    title=context.service_id,
                    text="Collected inside the admitted aggregate budget.",
                    author=None,
                    published_at=None,
                ),
            ),
            usage=_usage(items=1),
        )

    services = [
        {
            "service_id": service_id,
            "source": service_id,
            "providers": [_provider(f"{service_id}-provider", "fixture", f"network:{service_id}")],
        }
        for service_id in ("alpha", "beta")
    ]
    coordinator, _, _, _, _, _ = _coordinator(
        tmp_path,
        services,
        [_target("alpha"), _target("beta")],
        [AdapterSpec("fixture", frozenset({"collect"}), None, success, "fixture:runner:success")],
        aggregate_limits={**_limits(items=10), "attempts": 1},
    )

    receipt = coordinator.enqueue_tick(
        _request("2026-08-03T00:00:00Z", "2026-08-04T00:00:00Z")
    )

    assert receipt.state is contracts.TickState.COMPLETE_DEGRADED
    assert calls == ["alpha"]
    assert {lane.service_id: lane.state.value for lane in receipt.lanes} == {
        "alpha": "success",
        "beta": "budget_exhausted",
    }
    assert receipt.budget_summary["tick"]["consumed"]["attempts"] == 1


def test_active_tick_defers_a_distinct_tick_without_starting_provider_work(tmp_path):
    calls = []

    def success(context):
        calls.append(context.tick_id)
        return ProviderResult.empty(
            usage=_usage()
        )

    services = [
        {
            "service_id": "web",
            "source": "web",
            "providers": [_provider("web-provider", "fixture", "network:web")],
        }
    ]
    coordinator, runner, db_path, config_path, registry, _ = _coordinator(
        tmp_path,
        services,
        [_target("web")],
        [AdapterSpec("fixture", frozenset({"collect"}), None, success, "fixture:runner:success")],
    )
    queued_only = TickCoordinator(
        db_path,
        config_path=config_path,
        adapter_registry=registry,
        clock=lambda: NOW,
    )
    first = queued_only.enqueue_tick(
        _request("2026-08-02T00:00:00Z", "2026-08-03T00:00:00Z")
    )
    conn = sqlite3.connect(db_path)
    conn.execute(
        "UPDATE service_ticks SET state = 'collecting' WHERE tick_id = ?",
        (first.tick_id,),
    )
    conn.execute(
        """UPDATE service_tick_attempts SET state = 'running',
               lease_owner = 'other-runner',
               lease_expires_at = '2026-08-04T12:10:00Z'
           WHERE tick_id = ?""",
        (first.tick_id,),
    )
    conn.commit()
    conn.close()

    second = coordinator.enqueue_tick(
        _request("2026-08-03T00:00:00Z", "2026-08-04T00:00:00Z")
    )

    assert second.state is contracts.TickState.QUEUED
    assert calls == []
    assert runner is not None


def test_late_overlapping_tick_terminalizes_with_an_exact_coverage_gap(tmp_path):
    calls = []

    def empty(context):
        calls.append(context.tick_id)
        return ProviderResult.empty(usage=_usage())

    services = [
        {
            "service_id": "web",
            "source": "web",
            "providers": [_provider("web-provider", "fixture", "network:web")],
        }
    ]
    coordinator, _, db_path, config_path, registry, _ = _coordinator(
        tmp_path,
        services,
        [_target("web")],
        [AdapterSpec("fixture", frozenset({"collect"}), None, empty, "fixture:runner:empty")],
        lateness_seconds=60,
    )
    queued_only = TickCoordinator(
        db_path,
        config_path=config_path,
        adapter_registry=registry,
        clock=lambda: NOW,
    )
    active = queued_only.enqueue_tick(
        _request("2026-08-03T00:00:00Z", "2026-08-04T00:00:00Z")
    )
    conn = sqlite3.connect(db_path)
    conn.execute(
        "UPDATE service_ticks SET state = 'collecting' WHERE tick_id = ?",
        (active.tick_id,),
    )
    conn.execute(
        """UPDATE service_tick_attempts SET state = 'running',
               lease_owner = 'other-runner',
               lease_expires_at = '2026-08-04T12:10:00Z'
           WHERE tick_id = ?""",
        (active.tick_id,),
    )
    conn.commit()
    conn.close()

    missed = coordinator.enqueue_tick(
        _request("2026-08-02T00:00:00Z", "2026-08-03T00:00:00Z")
    )

    assert missed.state is contracts.TickState.MISSED_DUE_TO_OVERLAP
    assert missed.coverage_gaps == (
        "2026-08-02T00:00:00Z/2026-08-03T00:00:00Z",
    )
    assert {lane.state.value for lane in missed.lanes} == {"failure"}
    assert calls == []


def test_replay_in_a_new_tick_reuses_immutable_version_and_adds_a_sighting(tmp_path):
    def success(_context):
        return ProviderResult.success(
            items=(
                CollectedItem(
                    source_native_id="stable-1",
                    url="https://example.test/stable-1",
                    title="Stable result",
                    text="The same immutable observation.",
                    author=None,
                    published_at=None,
                ),
            ),
            usage=_usage(items=1),
        )

    services = [
        {
            "service_id": "web",
            "source": "web",
            "providers": [_provider("web-provider", "fixture", "network:web")],
        }
    ]
    coordinator, _, db_path, _, _, snapshots = _coordinator(
        tmp_path,
        services,
        [_target("web")],
        [AdapterSpec("fixture", frozenset({"collect"}), None, success, "fixture:runner:success")],
        aggregate_limits=_limits(items=10),
    )

    first = coordinator.enqueue_tick(
        _request("2026-08-02T00:00:00Z", "2026-08-03T00:00:00Z")
    )
    second = coordinator.enqueue_tick(
        _request("2026-08-03T00:00:00Z", "2026-08-04T00:00:00Z")
    )

    assert first.state is contracts.TickState.COMPLETE
    assert second.state is contracts.TickState.COMPLETE
    assert snapshots.current().tick_id == second.tick_id
    conn = sqlite3.connect(db_path)
    assert conn.execute("SELECT COUNT(*) FROM service_source_records").fetchone()[0] == 1
    assert conn.execute("SELECT COUNT(*) FROM service_source_versions").fetchone()[0] == 1
    assert conn.execute("SELECT COUNT(*) FROM service_source_sightings").fetchone()[0] == 2
    conn.close()


def test_exact_later_provider_success_resolves_incident_and_notifies_once(tmp_path):
    observations = ["challenge", "success"]

    def collect(_context):
        outcome = observations.pop(0)
        if outcome == "challenge":
            return ProviderResult.failure(
                failure_class="challenge",
                safe_error_code="captcha_required",
                page_signals=("captcha_required",),
                rendered_page=b"exact-challenge-page",
                rendered_page_mime_type="image/png",
                usage=_usage(),
            )
        return ProviderResult.success(
            items=(
                CollectedItem(
                    source_native_id="x-recovered-1",
                    url="https://x.example.test/x-recovered-1",
                    title="Recovered collection",
                    text="The exact provider lane succeeded after recovery.",
                    author=None,
                    published_at=None,
                ),
            ),
            usage=_usage(items=1),
        )

    services = [
        {
            "service_id": "x",
            "source": "x",
            "providers": [
                _provider("x-provider", "fixture", "browser:profile-ref:social")
            ],
        }
    ]
    coordinator, runner, db_path, _, _, _ = _coordinator(
        tmp_path,
        services,
        [_target("x", partition="profile:social")],
        [AdapterSpec("fixture", frozenset({"collect"}), None, collect, "fixture:runner:collect")],
    )

    failed = coordinator.enqueue_tick(
        _request("2026-08-02T00:00:00Z", "2026-08-03T00:00:00Z")
    )
    recovered = coordinator.enqueue_tick(
        _request("2026-08-03T00:00:00Z", "2026-08-04T00:00:00Z")
    )

    assert failed.state is contracts.TickState.COMPLETE_DEGRADED
    assert recovered.state is contracts.TickState.COMPLETE
    notification = runner.notification_transports[0]
    assert [payload["notification_kind"] for payload in notification.payloads] == [
        "detected",
        "resolved",
    ]
    conn = sqlite3.connect(db_path)
    incident = conn.execute(
        """SELECT state, resolution_execution_id FROM service_incidents
           WHERE incident_type = 'captcha_required'"""
    ).fetchone()
    assert incident[0] == "resolved"
    assert incident[1] in recovered.provider_attempt_ids
    assert conn.execute(
        """SELECT COUNT(*) FROM service_notification_deliveries
           WHERE notification_kind = 'resolved' AND state = 'success'"""
    ).fetchone()[0] == 1
    conn.close()


def test_success_with_persistent_rate_warning_does_not_emit_false_recovery(tmp_path):
    def collect(_context):
        return ProviderResult(
            status="success",
            items=(
                CollectedItem(
                    source_native_id="warning-item",
                    url="https://example.test/warning-item",
                    title="Collected with warning",
                    text="The content is valid while the provider warns about rate limits.",
                    author=None,
                    published_at=None,
                ),
            ),
            usage=_usage(items=1),
            failure_class="rate_limit",
            safe_error_code="rate_limit_warning",
            page_signals=("rate_limit_warning",),
        )

    services = [
        {
            "service_id": "web",
            "source": "web",
            "providers": [_provider("web-provider", "fixture", "network:web")],
        }
    ]
    coordinator, runner, db_path, _, _, _ = _coordinator(
        tmp_path,
        services,
        [_target("web")],
        [
            AdapterSpec(
                "fixture",
                frozenset({"collect"}),
                None,
                collect,
                "fixture:runner:persistent-rate-warning",
            )
        ],
    )

    first = coordinator.enqueue_tick(
        _request("2026-08-02T00:00:00Z", "2026-08-03T00:00:00Z")
    )
    second = coordinator.enqueue_tick(
        _request("2026-08-03T00:00:00Z", "2026-08-04T00:00:00Z")
    )

    assert first.state is contracts.TickState.COMPLETE_DEGRADED
    assert second.state is contracts.TickState.COMPLETE_DEGRADED
    notification = runner.notification_transports[0]
    assert [payload["notification_kind"] for payload in notification.payloads] == [
        "detected"
    ]
    conn = sqlite3.connect(db_path)
    assert conn.execute(
        """SELECT state, occurrence_count FROM service_incidents
           WHERE incident_type = 'rate_limit_warning'"""
    ).fetchone() == ("open", 2)
    assert conn.execute(
        """SELECT COUNT(*) FROM service_incident_transitions
           WHERE transition_type = 'resolved'"""
    ).fetchone()[0] == 0
    conn.close()


def test_statistical_rule_learns_then_degrades_and_resolves_from_exact_lane_runs(
    tmp_path,
):
    yields = [10, 10, 1, 10]

    def collect(context):
        count = yields.pop(0)
        return ProviderResult.success(
            items=tuple(
                CollectedItem(
                    source_native_id=f"stable-{index}",
                    url=f"https://example.test/stable-{index}",
                    title=f"Agent item {index}",
                    text="Agents remain queryable.",
                    author=None,
                    published_at=None,
                )
                for index in range(count)
            ),
            usage=_usage(items=count),
        )

    services = [
        {
            "service_id": "web",
            "source": "web",
            "providers": [_provider("web-provider", "fixture", "network:web")],
        }
    ]
    coordinator, runner, db_path, _, _, _ = _coordinator(
        tmp_path,
        services,
        [_target("web")],
        [AdapterSpec("fixture", frozenset({"collect"}), None, collect, "fixture:runner:collect")],
        aggregate_limits=_limits(items=20),
        anomaly_rules=[
            {
                "rule_id": "yield-collapse",
                "metric": "yield_count",
                "direction": "low",
                "minimum_comparable_ticks": 2,
                "warning_ratio": 0.8,
                "critical_ratio": 0.5,
            }
        ],
    )
    boundaries = (
        ("2026-07-31T00:00:00Z", "2026-08-01T00:00:00Z"),
        ("2026-08-01T00:00:00Z", "2026-08-02T00:00:00Z"),
        ("2026-08-02T00:00:00Z", "2026-08-03T00:00:00Z"),
        ("2026-08-03T00:00:00Z", "2026-08-04T00:00:00Z"),
    )

    receipts = [coordinator.enqueue_tick(_request(start, end)) for start, end in boundaries]

    assert [receipt.state.value for receipt in receipts] == [
        "complete",
        "complete",
        "complete_degraded",
        "complete",
    ]
    notification = runner.notification_transports[0]
    assert [payload["notification_kind"] for payload in notification.payloads] == [
        "detected",
        "resolved",
    ]
    conn = sqlite3.connect(db_path)
    assert conn.execute(
        """SELECT state FROM service_tick_anomaly_results
           ORDER BY rowid"""
    ).fetchall() == [
        ("learning_baseline",),
        ("learning_baseline",),
        ("critical",),
        ("healthy",),
    ]
    assert conn.execute(
        """SELECT state FROM service_incidents
           WHERE incident_type = 'provider_degraded'"""
    ).fetchone()[0] == "resolved"
    conn.close()


def test_provider_result_staging_replays_after_crash_without_a_second_source_call(
    tmp_path,
):
    calls = []
    sidecar = SemanticSidecar(
        literal_description="A revenue chart for an agent product.",
        observable_entities=("revenue chart",),
        observable_relationships=("revenue increases",),
        objects_actions=("line:rising",),
        inferred_context=("quarterly growth",),
        search_terms=("agent revenue",),
        uncertainty=(),
        model_provider="fixture-model",
        model_version="1",
        input_refs=("image", "ocr", "alt-text"),
    )

    def collect(_context):
        calls.append("source-called")
        return ProviderResult.success(
            items=(
                CollectedItem(
                    source_native_id="recovery-1",
                    url="https://example.test/recovery",
                    title="Agent revenue recovery",
                    text="The durable provider result survives a runner crash.",
                    author="Fixture",
                    published_at="2026-08-03T10:00:00Z",
                    media=(
                        CollectedMedia(
                            source_url="https://example.test/recovery.png",
                            content=b"durable-recovery-image",
                            mime_type="image/png",
                            media_kind="image",
                            alt_text="Agent revenue chart",
                            ocr_regions=(
                                OcrRegion(0, "Revenue", (0, 0, 100, 30), 0.99),
                            ),
                            detected_language="en",
                            ocr_engine="fixture-ocr",
                            ocr_engine_version="1",
                            semantic_sidecar=sidecar,
                        ),
                    ),
                ),
            ),
            usage=_usage(items=1, requests=2, model_tokens=20),
        )

    def crash_after_staging(point):
        if point == "provider_result_staged":
            raise SystemExit("synthetic provider/raw boundary crash")

    services = [
        {
            "service_id": "web",
            "source": "web",
            "providers": [_provider("web-provider", "fixture", "network:web")],
        }
    ]
    targets = [_target("web")]
    specs = [
        AdapterSpec(
            "fixture",
            frozenset({"collect"}),
            None,
            collect,
            "fixture:runner:recovery",
        )
    ]
    request = _request("2026-08-03T00:00:00Z", "2026-08-04T00:00:00Z")
    coordinator, _, db_path, _, _, _ = _coordinator(
        tmp_path,
        services,
        targets,
        specs,
        aggregate_limits=_limits(items=20, attempts=2),
        fault_injector=crash_after_staging,
    )

    with pytest.raises(SystemExit, match="provider/raw boundary crash"):
        coordinator.enqueue_tick(request)

    later = NOW + timedelta(hours=1)
    recovered_coordinator, _, _, _, _, recovered_snapshots = _coordinator(
        tmp_path,
        services,
        targets,
        specs,
        aggregate_limits=_limits(items=20, attempts=2),
        clock=lambda: later,
    )
    receipt = recovered_coordinator.enqueue_tick(request)

    assert calls == ["source-called"]
    assert receipt.state is contracts.TickState.COMPLETE
    assert len(receipt.execution_attempt_ids) == 2
    assert len(receipt.provider_attempt_ids) == 1
    assert len(receipt.source_version_ids) == 1
    assert len(receipt.artifact_ids) == 1
    assert len(receipt.derivative_ids) == 2
    assert recovered_snapshots.query(
        "agent revenue",
        access_partitions=("public",),
    )
    conn = sqlite3.connect(db_path)
    assert conn.execute(
        "SELECT COUNT(*) FROM service_tick_provider_results"
    ).fetchone()[0] == 1
    assert conn.execute(
        "SELECT COUNT(*) FROM service_tick_resource_leases WHERE released_at IS NULL"
    ).fetchone()[0] == 0
    conn.close()


def test_recovery_skips_terminal_lanes_and_rebuilds_snapshot_from_durable_evidence(
    tmp_path,
):
    calls = []

    def collect(context):
        calls.append(context.service_id)
        return ProviderResult.success(
            items=(
                CollectedItem(
                    source_native_id=f"{context.service_id}-1",
                    url=f"https://example.test/{context.service_id}",
                    title=f"{context.service_id.title()} durable evidence",
                    text=f"{context.service_id} survives snapshot reconstruction.",
                    author="Fixture",
                    published_at="2026-08-03T10:00:00Z",
                ),
            ),
            usage=_usage(items=1),
        )

    crashed = False

    def crash_after_first_lane(point):
        nonlocal crashed
        if point == "lane_completed" and not crashed:
            crashed = True
            raise SystemExit("synthetic between-lanes crash")

    services = [
        {
            "service_id": service_id,
            "source": service_id,
            "providers": [
                _provider(
                    f"{service_id}-provider",
                    "fixture",
                    f"network:{service_id}",
                )
            ],
        }
        for service_id in ("alpha", "beta")
    ]
    targets = [_target(service_id) for service_id in ("alpha", "beta")]
    specs = [
        AdapterSpec(
            "fixture",
            frozenset({"collect"}),
            None,
            collect,
            "fixture:runner:lane-recovery",
        )
    ]
    request = _request("2026-08-03T00:00:00Z", "2026-08-04T00:00:00Z")
    coordinator, _, db_path, _, _, _ = _coordinator(
        tmp_path,
        services,
        targets,
        specs,
        aggregate_limits=_limits(items=20, attempts=3),
        fault_injector=crash_after_first_lane,
    )

    with pytest.raises(SystemExit, match="between-lanes crash"):
        coordinator.enqueue_tick(request)

    recovered_coordinator, _, _, _, _, snapshots = _coordinator(
        tmp_path,
        services,
        targets,
        specs,
        aggregate_limits=_limits(items=20, attempts=3),
        clock=lambda: NOW + timedelta(hours=1),
    )
    receipt = recovered_coordinator.enqueue_tick(request)

    assert receipt.state is contracts.TickState.COMPLETE
    assert calls == ["alpha", "beta"]
    assert {result.source for result in snapshots.query(
        "durable evidence",
        access_partitions=("public",),
    )} == {"alpha", "beta"}
    conn = sqlite3.connect(db_path)
    assert conn.execute(
        """SELECT COUNT(*) FROM service_tick_events
           WHERE event_type = 'raw_published'"""
    ).fetchone()[0] == 2
    conn.close()
