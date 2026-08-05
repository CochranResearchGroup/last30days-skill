"""Behavioral tests for the durable all-source tick interface."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import pytest

from lib import service_contracts as contracts
from lib.service_tick import TickConfigError, TickCoordinator, TickIntegrityError
from lib.service_tick_adapters import (
    AdapterRegistry,
    AdapterSpec,
    next_provider_ordinal,
    should_retry_provider,
)


NOW = datetime(2026, 8, 4, 12, 0, tzinfo=timezone.utc)
ROOT = Path(__file__).resolve().parents[1]


def _write_config(path) -> None:
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "config_revision": "config-001",
                "services": [
                    {
                        "service_id": "reddit",
                        "source": "reddit",
                        "providers": [
                            {
                                "provider_id": "reddit-keyless",
                                "adapter_type": "reddit_keyless",
                                "resource_keys": ["network:reddit"],
                                "fallback_on": ["transient"],
                                "limits": {
                                    "attempts": 1,
                                    "network_requests": 50,
                                    "wall_seconds": 120,
                                    "items": 20,
                                    "cost_cents": 0,
                                    "model_tokens": 0,
                                },
                            }
                        ],
                    }
                ],
                "targets": [
                    {
                        "target_id": "reddit-openai",
                        "service_id": "reddit",
                        "surface_kind": "topic",
                        "selector": {"topic": "OpenAI"},
                        "access_partition_id": "public",
                        "retention_class": "durable",
                        "enabled": True,
                    }
                ],
                "tick": {
                    "timezone": "UTC",
                    "lateness_seconds": 86400,
                    "aggregate_limits": {
                        "attempts": 5,
                        "network_requests": 250,
                        "wall_seconds": 600,
                        "items": 100,
                        "cost_cents": 0,
                        "model_tokens": 0,
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
                            "transport_id": "ops-primary",
                            "adapter_type": "slack_receipts",
                            "credential_ref": "credential-ref:ops-primary",
                            "routing": {
                                "tenant_ref": "tenant-ref:default",
                                "recipient_ref": "recipient-ref:operator",
                            },
                        }
                    ],
                    "reminder_seconds": 3600,
                },
                "query": {
                    "embedding_space": "local-hash-v1",
                    "fusion_version": "rrf-v1",
                },
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def test_enqueue_tick_freezes_interval_config_and_enabled_lanes(tmp_path):
    config_path = tmp_path / "tick-config-v1.json"
    _write_config(config_path)
    coordinator = TickCoordinator(
        tmp_path / "research.db",
        config_path=config_path,
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

    created = coordinator.enqueue_tick(request)
    repeated = coordinator.enqueue_tick(request)

    assert created == repeated == coordinator.get_tick(created.tick_id)
    assert created.state is contracts.TickState.QUEUED
    assert created.config_revision == "config-001"
    assert created.config_digest.startswith("sha256:")
    assert len(created.execution_attempt_ids) == 1
    assert [lane.to_dict() for lane in created.lanes] == [
        {
            "schema_version": 1,
            "lane_id": created.lanes[0].lane_id,
            "service_id": "reddit",
            "target_id": "reddit-openai",
            "access_partition_id": "public",
            "state": "ready",
        }
    ]


def test_tick_contracts_are_published_in_the_golden_catalog():
    catalog = contracts.load_schema_catalog()
    request_payload = {
        "schema_version": 1,
        "schedule_id": "manual-default",
        "interval_from": "2026-08-03T00:00:00Z",
        "interval_to": "2026-08-04T00:00:00Z",
        "trigger": "manual",
    }

    assert catalog["compatibility"]["database_schema"] == {"min": 14, "max": 14}
    assert {
        "tick_request",
        "tick_lane_receipt",
        "tick_receipt",
    } <= set(catalog["contracts"])
    assert contracts.parse_envelope("tick_request", request_payload).to_dict() == (
        request_payload
    )


def test_user_scoped_tick_config_schema_is_packaged_without_operator_particulars():
    schema_path = ROOT / "skills/last30days/schemas/tick-config-v1.json"

    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    serialized = json.dumps(schema, sort_keys=True).lower()

    assert schema["$id"] == "last30days://schemas/tick-config-v1.json"
    assert schema["properties"]["schema_version"] == {"const": 1}
    assert schema["required"] == [
        "schema_version",
        "config_revision",
        "services",
        "targets",
        "tick",
        "artifacts",
        "analysis",
        "notifications",
        "query",
    ]
    assert "@eric" not in serialized
    assert "ecochran76@gmail.com" not in serialized
    assert "last30-facebook" not in serialized


def test_enqueue_tick_persists_frozen_stages_provider_order_and_budgets(tmp_path):
    config_path = tmp_path / "tick-config-v1.json"
    _write_config(config_path)
    db_path = tmp_path / "research.db"
    coordinator = TickCoordinator(
        db_path,
        config_path=config_path,
        clock=lambda: NOW,
    )
    tick = coordinator.enqueue_tick(
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

    conn = sqlite3.connect(db_path)
    config_json = conn.execute(
        "SELECT config_json FROM service_ticks WHERE tick_id = ?", (tick.tick_id,)
    ).fetchone()[0]
    stages = conn.execute(
        """SELECT stage_scope, stage_name, state
           FROM service_tick_stages
           WHERE tick_id = ? ORDER BY stage_scope, stage_name""",
        (tick.tick_id,),
    ).fetchall()
    providers = conn.execute(
        """SELECT provider_ordinal, provider_id, adapter_type,
                  normalization_proof_ref
           FROM service_tick_providers
           WHERE tick_id = ? ORDER BY provider_ordinal""",
        (tick.tick_id,),
    ).fetchall()
    budgets = conn.execute(
        """SELECT scope_kind, limit_json, consumed_json
           FROM service_tick_budgets
           WHERE tick_id = ? ORDER BY scope_kind, scope_id""",
        (tick.tick_id,),
    ).fetchall()
    conn.close()

    assert "credential-ref:ops-primary" not in config_json
    assert stages == [
        ("global", "catalog", "pending"),
        ("global", "head_promotion", "pending"),
        ("global", "lexical_index", "pending"),
        ("global", "semantic_index", "pending"),
        ("lane", "collection", "pending"),
        ("lane", "media", "pending"),
        ("lane", "ocr", "pending"),
        ("lane", "semantic_sidecar", "pending"),
    ]
    assert providers == [
        (
            0,
            "reddit-keyless",
            "reddit_keyless",
            "fixture:tests/test_service_tick_runtime.py:"
            "test_installed_worker_adapters_preserve_nonzero_normalized_items:"
            "reddit_keyless",
        )
    ]
    assert [row[0] for row in budgets] == ["provider", "tick"]
    assert all(json.loads(row[2]) == {
        "attempts": 0,
        "cost_cents": 0,
        "items": 0,
        "model_tokens": 0,
        "network_requests": 0,
        "wall_seconds": 0,
    } for row in budgets)


def test_restart_recovers_expired_attempt_under_the_same_tick_identity(tmp_path):
    config_path = tmp_path / "tick-config-v1.json"
    _write_config(config_path)
    db_path = tmp_path / "research.db"
    request = contracts.TickRequest.from_dict(
        {
            "schema_version": 1,
            "schedule_id": "manual-default",
            "interval_from": "2026-08-03T00:00:00Z",
            "interval_to": "2026-08-04T00:00:00Z",
            "trigger": "manual",
        }
    )
    first = TickCoordinator(
        db_path, config_path=config_path, clock=lambda: NOW
    ).enqueue_tick(request)
    conn = sqlite3.connect(db_path)
    conn.execute(
        """UPDATE service_ticks
           SET state = 'collecting', updated_at = '2026-08-04T12:00:00Z'
           WHERE tick_id = ?""",
        (first.tick_id,),
    )
    conn.execute(
        """UPDATE service_tick_attempts
           SET state = 'running', started_at = '2026-08-04T12:00:00Z',
               lease_owner = 'worker-crashed', lease_generation = 1,
               lease_expires_at = '2026-08-04T12:00:30Z'
           WHERE execution_attempt_id = ?""",
        (first.execution_attempt_ids[0],),
    )
    conn.execute(
        """UPDATE service_tick_stages
           SET state = 'running', execution_attempt_id = ?,
               started_at = '2026-08-04T12:00:00Z'
           WHERE tick_id = ? AND stage_name = 'collection'""",
        (first.execution_attempt_ids[0], first.tick_id),
    )
    conn.commit()
    conn.close()

    restarted = TickCoordinator(
        db_path,
        config_path=config_path,
        clock=lambda: datetime(2026, 8, 4, 12, 1, tzinfo=timezone.utc),
    )
    recovered = restarted.enqueue_tick(request)
    repeated = restarted.enqueue_tick(request)

    assert recovered.tick_id == first.tick_id
    assert repeated == recovered
    assert len(recovered.execution_attempt_ids) == 2
    conn = sqlite3.connect(db_path)
    assert conn.execute(
        """SELECT attempt, state, lease_owner, lease_expires_at
           FROM service_tick_attempts WHERE tick_id = ? ORDER BY attempt""",
        (first.tick_id,),
    ).fetchall() == [
        (1, "expired", None, None),
        (2, "queued", None, None),
    ]
    assert conn.execute(
        """SELECT state, execution_attempt_id, started_at
           FROM service_tick_stages
           WHERE tick_id = ? AND stage_name = 'collection'""",
        (first.tick_id,),
    ).fetchone() == ("pending", None, None)
    assert conn.execute(
        """SELECT event_type FROM service_tick_events
           WHERE tick_id = ? ORDER BY sequence""",
        (first.tick_id,),
    ).fetchall() == [("tick_enqueued",), ("attempt_recovered",)]
    conn.close()


def test_get_tick_fails_closed_when_frozen_config_is_tampered(tmp_path):
    config_path = tmp_path / "tick-config-v1.json"
    _write_config(config_path)
    db_path = tmp_path / "research.db"
    coordinator = TickCoordinator(
        db_path, config_path=config_path, clock=lambda: NOW
    )
    tick = coordinator.enqueue_tick(
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
    conn = sqlite3.connect(db_path)
    conn.execute(
        "UPDATE service_ticks SET config_json = '{\"tampered\":true}' WHERE tick_id = ?",
        (tick.tick_id,),
    )
    conn.commit()
    conn.close()

    with pytest.raises(TickIntegrityError, match="config digest"):
        coordinator.get_tick(tick.tick_id)


def test_tick_services_are_admitted_by_installed_adapter_registry_not_source_matrix(
    tmp_path,
):
    config_path = tmp_path / "tick-config-v1.json"
    _write_config(config_path)
    payload = json.loads(config_path.read_text(encoding="utf-8"))
    payload["services"][0] = {
        **payload["services"][0],
        "service_id": "custom-forum",
        "source": "custom_forum",
        "providers": [
            {
                **payload["services"][0]["providers"][0],
                "provider_id": "custom-paid",
                "adapter_type": "fixture_paid_api",
            }
        ],
    }
    payload["targets"][0]["service_id"] = "custom-forum"
    config_path.write_text(json.dumps(payload), encoding="utf-8")
    registry = AdapterRegistry(
        [
            AdapterSpec(
                adapter_type="fixture_paid_api",
                capabilities=frozenset({"collect"}),
                source_kinds=None,
                normalization_proof_ref="fixture:test-service-tick:custom-paid",
            )
        ]
    )
    coordinator = TickCoordinator(
        tmp_path / "research.db",
        config_path=config_path,
        adapter_registry=registry,
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

    created = coordinator.enqueue_tick(request)

    assert created.lanes[0].service_id == "custom-forum"
    payload["services"][0]["providers"][0]["adapter_type"] = "not_installed"
    payload["config_revision"] = "config-002"
    config_path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(TickConfigError, match="not installed"):
        coordinator.enqueue_tick(request)


def test_installed_adapter_without_nonzero_normalization_proof_is_not_admitted(
    tmp_path,
):
    config_path = tmp_path / "tick-config-v1.json"
    _write_config(config_path)
    payload = json.loads(config_path.read_text(encoding="utf-8"))
    payload["services"][0]["providers"][0]["adapter_type"] = "unproven_adapter"
    config_path.write_text(json.dumps(payload), encoding="utf-8")
    coordinator = TickCoordinator(
        tmp_path / "research.db",
        config_path=config_path,
        adapter_registry=AdapterRegistry(
            [AdapterSpec("unproven_adapter", frozenset({"collect"}))]
        ),
        clock=lambda: NOW,
    )

    with pytest.raises(TickConfigError, match="normalization proof"):
        coordinator.enqueue_tick(
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


def test_tick_config_rejects_unregistered_executable_fields_before_enqueue(tmp_path):
    config_path = tmp_path / "tick-config-v1.json"
    _write_config(config_path)
    payload = json.loads(config_path.read_text(encoding="utf-8"))
    payload["services"][0]["providers"][0]["command"] = ["unsafe-program"]
    config_path.write_text(json.dumps(payload), encoding="utf-8")
    db_path = tmp_path / "research.db"
    coordinator = TickCoordinator(
        db_path, config_path=config_path, clock=lambda: NOW
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

    with pytest.raises(TickConfigError, match="unknown fields.*command"):
        coordinator.enqueue_tick(request)
    conn = sqlite3.connect(db_path)
    assert conn.execute("SELECT COUNT(*) FROM service_ticks").fetchone()[0] == 0
    conn.close()


def test_provider_fallback_is_sequential_and_retry_is_transient_only():
    providers = [
        {"fallback_on": ["transient"], "limits": {"attempts": 2}},
        {"fallback_on": ["rate_limit"], "limits": {"attempts": 2}},
        {"fallback_on": [], "limits": {"attempts": 1}},
    ]

    assert next_provider_ordinal(
        providers, current_ordinal=0, failure_class="transient"
    ) == 1
    assert next_provider_ordinal(
        providers, current_ordinal=0, failure_class="authentication"
    ) is None
    assert next_provider_ordinal(
        providers, current_ordinal=1, failure_class="rate_limit"
    ) == 2
    assert next_provider_ordinal(
        providers, current_ordinal=2, failure_class="transient"
    ) is None
    assert should_retry_provider(
        providers[0], failure_class="transient", retry_ordinal=0
    )
    assert not should_retry_provider(
        providers[0], failure_class="authentication", retry_ordinal=0
    )
    assert not should_retry_provider(
        providers[0], failure_class="transient", retry_ordinal=1
    )
