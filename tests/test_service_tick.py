"""Behavioral tests for the durable all-source tick interface."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from lib import service_contracts as contracts
from lib.service_tick import TickConfigError, TickCoordinator, TickIntegrityError
from lib.service_tick_schedule import TickScheduleCoordinator
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


def test_enqueue_receipt_preserves_configured_target_order(tmp_path):
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

    receipt = TickCoordinator(
        tmp_path / "research.db", config_path=config_path, clock=lambda: NOW
    ).enqueue_tick(
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

    assert [lane.service_id for lane in receipt.lanes] == ["z-source", "a-source"]


def test_tick_config_accepts_exact_optional_schedule(tmp_path):
    config_path = tmp_path / "tick-config-v1.json"
    _write_config(config_path)
    payload = json.loads(config_path.read_text(encoding="utf-8"))
    payload["tick"]["schedule"] = {
        "enabled": False,
        "schedule_id": "daily-default",
        "interval_seconds": 86_400,
        "anchor_seconds": 0,
    }
    config_path.write_text(json.dumps(payload), encoding="utf-8")

    receipt = TickCoordinator(
        tmp_path / "research.db", config_path=config_path, clock=lambda: NOW
    ).enqueue_tick(
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

    assert receipt.state is contracts.TickState.QUEUED


@pytest.mark.parametrize(
    ("schedule_patch", "message"),
    [
        ({"unexpected": True}, "unknown fields: unexpected"),
        ({"enabled": "yes"}, "enabled must be boolean"),
        ({"interval_seconds": 899}, "interval_seconds must be between"),
        ({"anchor_seconds": 86_400}, "anchor_seconds must be between"),
    ],
)
def test_tick_config_rejects_malformed_schedule_before_state(
    tmp_path, schedule_patch, message
):
    config_path = tmp_path / "tick-config-v1.json"
    _write_config(config_path)
    payload = json.loads(config_path.read_text(encoding="utf-8"))
    schedule = {
        "enabled": False,
        "schedule_id": "daily-default",
        "interval_seconds": 86_400,
        "anchor_seconds": 0,
    }
    schedule.update(schedule_patch)
    payload["tick"]["schedule"] = schedule
    config_path.write_text(json.dumps(payload), encoding="utf-8")
    db_path = tmp_path / "research.db"

    with pytest.raises(TickConfigError, match=message):
        TickScheduleCoordinator(
            db_path,
            tick_coordinator=TickCoordinator(
                db_path, config_path=config_path, clock=lambda: NOW
            ),
            config_path=config_path,
            clock=lambda: NOW,
        )

    conn = sqlite3.connect(db_path)
    try:
        assert conn.execute("SELECT COUNT(*) FROM service_ticks").fetchone()[0] == 0
        assert conn.execute(
            "SELECT COUNT(*) FROM service_tick_schedules"
        ).fetchone()[0] == 0
    finally:
        conn.close()


def test_disabled_tick_schedule_reports_inert_status(tmp_path):
    config_path = tmp_path / "tick-config-v1.json"
    _write_config(config_path)
    payload = json.loads(config_path.read_text(encoding="utf-8"))
    payload["tick"]["schedule"] = {
        "enabled": False,
        "schedule_id": "daily-default",
        "interval_seconds": 86_400,
        "anchor_seconds": 0,
    }
    config_path.write_text(json.dumps(payload), encoding="utf-8")
    tick_coordinator = TickCoordinator(
        tmp_path / "research.db", config_path=config_path, clock=lambda: NOW
    )

    status = TickScheduleCoordinator(
        tmp_path / "research.db",
        tick_coordinator=tick_coordinator,
        config_path=config_path,
        clock=lambda: NOW,
    ).poll()

    assert status == {
        "schema_version": 1,
        "enabled": False,
        "schedule_id": "daily-default",
        "interval_seconds": 86_400,
        "anchor_seconds": 0,
        "state": "disabled",
        "next_boundary": None,
        "last_boundary": None,
        "last_tick_id": None,
        "last_tick_state": None,
        "runtime_error": None,
    }


def test_enabled_tick_schedule_admits_latest_due_boundary_once(tmp_path):
    config_path = tmp_path / "tick-config-v1.json"
    _write_config(config_path)
    payload = json.loads(config_path.read_text(encoding="utf-8"))
    payload["tick"]["schedule"] = {
        "enabled": True,
        "schedule_id": "daily-default",
        "interval_seconds": 86_400,
        "anchor_seconds": 0,
    }
    config_path.write_text(json.dumps(payload), encoding="utf-8")
    tick_coordinator = TickCoordinator(
        tmp_path / "research.db", config_path=config_path, clock=lambda: NOW
    )
    schedule = TickScheduleCoordinator(
        tmp_path / "research.db",
        tick_coordinator=tick_coordinator,
        config_path=config_path,
        clock=lambda: NOW,
    )

    first = schedule.poll()
    repeated = schedule.poll()
    receipt = tick_coordinator.get_tick(str(first["last_tick_id"]))

    assert repeated == first
    assert first == {
        "schema_version": 1,
        "enabled": True,
        "schedule_id": "daily-default",
        "interval_seconds": 86_400,
        "anchor_seconds": 0,
        "state": "active",
        "next_boundary": "2026-08-05T00:00:00Z",
        "last_boundary": "2026-08-04T00:00:00Z",
        "last_tick_id": receipt.tick_id,
        "last_tick_state": "queued",
        "runtime_error": None,
    }
    assert receipt.interval_from == "2026-08-03T00:00:00Z"
    assert receipt.interval_to == "2026-08-04T00:00:00Z"
    assert receipt.trigger is contracts.TickTrigger.TIMER
    assert len(receipt.execution_attempt_ids) == 1
    conn = sqlite3.connect(tmp_path / "research.db")
    try:
        assert conn.execute(
            """SELECT event_type FROM service_tick_schedule_events
               WHERE schedule_id = 'daily-default' ORDER BY sequence"""
        ).fetchall() == [("initialized",), ("admitted",), ("tick_bound",)]
    finally:
        conn.close()


def test_tick_schedule_waits_for_live_recovery_lease(tmp_path):
    config_path = tmp_path / "tick-config-v1.json"
    _write_config(config_path)
    payload = json.loads(config_path.read_text(encoding="utf-8"))
    payload["tick"]["schedule"] = {
        "enabled": True,
        "schedule_id": "daily-default",
        "interval_seconds": 86_400,
        "anchor_seconds": 0,
    }
    config_path.write_text(json.dumps(payload), encoding="utf-8")
    db_path = tmp_path / "research.db"
    tick_coordinator = TickCoordinator(
        db_path, config_path=config_path, clock=lambda: NOW
    )
    schedule = TickScheduleCoordinator(
        db_path,
        tick_coordinator=tick_coordinator,
        config_path=config_path,
        clock=lambda: NOW,
    )
    admitted = schedule.poll()
    tick_id = str(admitted["last_tick_id"])
    lease_expires_at = (NOW + timedelta(minutes=5)).isoformat().replace(
        "+00:00", "Z"
    )
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            """UPDATE service_tick_attempts
               SET state = 'running', lease_expires_at = ?
               WHERE tick_id = ?""",
            (lease_expires_at, tick_id),
        )
        conn.execute(
            "UPDATE service_ticks SET state = 'collecting' WHERE tick_id = ?",
            (tick_id,),
        )
        conn.commit()
    finally:
        conn.close()

    recovered = TickScheduleCoordinator(
        db_path,
        tick_coordinator=TickCoordinator(
            db_path, config_path=config_path, clock=lambda: NOW
        ),
        config_path=config_path,
        clock=lambda: NOW,
    ).poll()

    assert recovered["state"] == "recovery_waiting"
    assert recovered["last_tick_id"] == tick_id
    assert recovered["last_tick_state"] == "collecting"
    assert len(tick_coordinator.get_tick(tick_id).execution_attempt_ids) == 1


def test_tick_schedule_recovers_expired_lease_before_new_boundary(tmp_path):
    config_path = tmp_path / "tick-config-v1.json"
    _write_config(config_path)
    payload = json.loads(config_path.read_text(encoding="utf-8"))
    payload["tick"]["schedule"] = {
        "enabled": True,
        "schedule_id": "daily-default",
        "interval_seconds": 86_400,
        "anchor_seconds": 0,
    }
    config_path.write_text(json.dumps(payload), encoding="utf-8")
    db_path = tmp_path / "research.db"
    first_coordinator = TickCoordinator(
        db_path, config_path=config_path, clock=lambda: NOW
    )
    first = TickScheduleCoordinator(
        db_path,
        tick_coordinator=first_coordinator,
        config_path=config_path,
        clock=lambda: NOW,
    ).poll()
    tick_id = str(first["last_tick_id"])
    conn = sqlite3.connect(db_path)
    try:
        before_stage_ids = {
            row[0]
            for row in conn.execute(
                "SELECT stage_id FROM service_tick_stages WHERE tick_id = ?",
                (tick_id,),
            ).fetchall()
        }
        attempt_id = conn.execute(
            """SELECT execution_attempt_id FROM service_tick_attempts
               WHERE tick_id = ? ORDER BY attempt DESC LIMIT 1""",
            (tick_id,),
        ).fetchone()[0]
        conn.execute(
            """UPDATE service_tick_attempts
               SET state = 'running', started_at = '2026-08-04T12:00:00Z',
                   lease_owner = 'worker-crashed', lease_generation = 1,
                   lease_expires_at = '2026-08-04T12:00:30Z'
               WHERE execution_attempt_id = ?""",
            (attempt_id,),
        )
        conn.execute(
            "UPDATE service_ticks SET state = 'collecting' WHERE tick_id = ?",
            (tick_id,),
        )
        conn.execute(
            """UPDATE service_tick_stages
               SET state = 'running', execution_attempt_id = ?,
                   started_at = '2026-08-04T12:00:00Z'
               WHERE tick_id = ? AND stage_name = 'collection'""",
            (attempt_id, tick_id),
        )
        conn.commit()
    finally:
        conn.close()
    restarted_at = datetime(2026, 8, 4, 12, 1, tzinfo=timezone.utc)
    restarted_coordinator = TickCoordinator(
        db_path, config_path=config_path, clock=lambda: restarted_at
    )

    recovered_status = TickScheduleCoordinator(
        db_path,
        tick_coordinator=restarted_coordinator,
        config_path=config_path,
        clock=lambda: restarted_at,
    ).poll()
    recovered = restarted_coordinator.get_tick(tick_id)

    assert recovered_status["last_tick_id"] == tick_id
    assert recovered_status["last_boundary"] == "2026-08-04T00:00:00Z"
    assert len(recovered.execution_attempt_ids) == 2
    conn = sqlite3.connect(db_path)
    try:
        assert {
            row[0]
            for row in conn.execute(
                "SELECT stage_id FROM service_tick_stages WHERE tick_id = ?",
                (tick_id,),
            ).fetchall()
        } == before_stage_ids
        assert conn.execute(
            """SELECT event_type FROM service_tick_schedule_events
               WHERE schedule_id = 'daily-default' ORDER BY sequence DESC LIMIT 1"""
        ).fetchone()[0] == "resumed"
    finally:
        conn.close()


def test_tick_schedule_pauses_when_bound_config_is_replaced(tmp_path):
    config_path = tmp_path / "tick-config-v1.json"
    _write_config(config_path)
    payload = json.loads(config_path.read_text(encoding="utf-8"))
    payload["tick"]["schedule"] = {
        "enabled": True,
        "schedule_id": "daily-default",
        "interval_seconds": 86_400,
        "anchor_seconds": 0,
    }
    config_path.write_text(json.dumps(payload), encoding="utf-8")
    db_path = tmp_path / "research.db"
    first_coordinator = TickCoordinator(
        db_path, config_path=config_path, clock=lambda: NOW
    )
    first = TickScheduleCoordinator(
        db_path,
        tick_coordinator=first_coordinator,
        config_path=config_path,
        clock=lambda: NOW,
    ).poll()
    payload["config_revision"] = "config-002"
    config_path.write_text(json.dumps(payload), encoding="utf-8")

    replaced = TickScheduleCoordinator(
        db_path,
        tick_coordinator=TickCoordinator(
            db_path, config_path=config_path, clock=lambda: NOW
        ),
        config_path=config_path,
        clock=lambda: NOW,
    ).poll()

    assert replaced["state"] == "paused"
    assert replaced["runtime_error"] == "schedule_config_replaced"
    assert replaced["last_tick_id"] == first["last_tick_id"]
    assert len(
        first_coordinator.get_tick(str(first["last_tick_id"])).execution_attempt_ids
    ) == 1


def test_disabling_an_existing_tick_schedule_persists_pause_without_new_tick(tmp_path):
    config_path = tmp_path / "tick-config-v1.json"
    _write_config(config_path)
    payload = json.loads(config_path.read_text(encoding="utf-8"))
    payload["tick"]["schedule"] = {
        "enabled": True,
        "schedule_id": "daily-default",
        "interval_seconds": 86_400,
        "anchor_seconds": 0,
    }
    config_path.write_text(json.dumps(payload), encoding="utf-8")
    db_path = tmp_path / "research.db"
    first_coordinator = TickCoordinator(
        db_path, config_path=config_path, clock=lambda: NOW
    )
    first = TickScheduleCoordinator(
        db_path,
        tick_coordinator=first_coordinator,
        config_path=config_path,
        clock=lambda: NOW,
    ).poll()
    payload["config_revision"] = "config-002"
    payload["tick"]["schedule"]["enabled"] = False
    config_path.write_text(json.dumps(payload), encoding="utf-8")

    disabled = TickScheduleCoordinator(
        db_path,
        tick_coordinator=TickCoordinator(
            db_path, config_path=config_path, clock=lambda: NOW
        ),
        config_path=config_path,
        clock=lambda: NOW,
    ).poll()

    conn = sqlite3.connect(db_path)
    try:
        row = conn.execute(
            """SELECT enabled, state, last_tick_id
               FROM service_tick_schedules WHERE schedule_id = 'daily-default'"""
        ).fetchone()
        tick_count = conn.execute("SELECT COUNT(*) FROM service_ticks").fetchone()[0]
        last_event = conn.execute(
            """SELECT event_type FROM service_tick_schedule_events
               WHERE schedule_id = 'daily-default' ORDER BY sequence DESC LIMIT 1"""
        ).fetchone()[0]
    finally:
        conn.close()

    assert disabled["enabled"] is False
    assert disabled["state"] == "paused"
    assert disabled["last_tick_id"] == first["last_tick_id"]
    assert row == (0, "paused", first["last_tick_id"])
    assert tick_count == 1
    assert last_event == "paused"


def test_replacing_schedule_identity_pauses_without_admitting_second_tick(tmp_path):
    config_path = tmp_path / "tick-config-v1.json"
    _write_config(config_path)
    payload = json.loads(config_path.read_text(encoding="utf-8"))
    payload["tick"]["schedule"] = {
        "enabled": True,
        "schedule_id": "daily-default",
        "interval_seconds": 86_400,
        "anchor_seconds": 0,
    }
    config_path.write_text(json.dumps(payload), encoding="utf-8")
    db_path = tmp_path / "research.db"
    first = TickScheduleCoordinator(
        db_path,
        tick_coordinator=TickCoordinator(
            db_path, config_path=config_path, clock=lambda: NOW
        ),
        config_path=config_path,
        clock=lambda: NOW,
    ).poll()
    payload["config_revision"] = "config-002"
    payload["tick"]["schedule"]["schedule_id"] = "daily-replacement"
    config_path.write_text(json.dumps(payload), encoding="utf-8")

    replacement = TickScheduleCoordinator(
        db_path,
        tick_coordinator=TickCoordinator(
            db_path, config_path=config_path, clock=lambda: NOW
        ),
        config_path=config_path,
        clock=lambda: NOW,
    ).poll()

    conn = sqlite3.connect(db_path)
    try:
        enabled_count = conn.execute(
            "SELECT COUNT(*) FROM service_tick_schedules WHERE enabled = 1"
        ).fetchone()[0]
        tick_count = conn.execute("SELECT COUNT(*) FROM service_ticks").fetchone()[0]
    finally:
        conn.close()

    assert replacement["schedule_id"] == "daily-replacement"
    assert replacement["enabled"] is False
    assert replacement["state"] == "paused"
    assert replacement["runtime_error"] == "schedule_config_replaced"
    assert replacement["last_tick_id"] == first["last_tick_id"]
    assert enabled_count == 0
    assert tick_count == 1


def test_tick_schedule_skips_catchup_fanout_to_latest_completed_boundary(tmp_path):
    config_path = tmp_path / "tick-config-v1.json"
    _write_config(config_path)
    payload = json.loads(config_path.read_text(encoding="utf-8"))
    payload["tick"]["schedule"] = {
        "enabled": True,
        "schedule_id": "daily-default",
        "interval_seconds": 86_400,
        "anchor_seconds": 0,
    }
    config_path.write_text(json.dumps(payload), encoding="utf-8")
    db_path = tmp_path / "research.db"
    current = [NOW]
    tick_coordinator = TickCoordinator(
        db_path, config_path=config_path, clock=lambda: current[0]
    )
    schedule = TickScheduleCoordinator(
        db_path,
        tick_coordinator=tick_coordinator,
        config_path=config_path,
        clock=lambda: current[0],
    )
    first = schedule.poll()
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            "UPDATE service_ticks SET state = 'complete' WHERE tick_id = ?",
            (first["last_tick_id"],),
        )
        conn.execute(
            """UPDATE service_tick_attempts
               SET state = 'complete', completed_at = '2026-08-04T12:01:00Z'
               WHERE tick_id = ?""",
            (first["last_tick_id"],),
        )
        conn.commit()
    finally:
        conn.close()
    current[0] = datetime(2026, 8, 7, 12, 0, tzinfo=timezone.utc)

    latest = schedule.poll()
    receipt = tick_coordinator.get_tick(str(latest["last_tick_id"]))

    assert latest["last_boundary"] == "2026-08-07T00:00:00Z"
    assert latest["next_boundary"] == "2026-08-08T00:00:00Z"
    assert receipt.interval_from == "2026-08-06T00:00:00Z"
    assert receipt.interval_to == "2026-08-07T00:00:00Z"


def test_tick_schedule_pauses_after_enqueue_failure_without_retry_loop(tmp_path):
    class BrokenRunner:
        def __init__(self):
            self.calls = 0

        def run(self, tick_id):
            assert tick_id
            self.calls += 1
            raise RuntimeError("fixture runner failed")

    config_path = tmp_path / "tick-config-v1.json"
    _write_config(config_path)
    payload = json.loads(config_path.read_text(encoding="utf-8"))
    payload["tick"]["schedule"] = {
        "enabled": True,
        "schedule_id": "daily-default",
        "interval_seconds": 86_400,
        "anchor_seconds": 0,
    }
    config_path.write_text(json.dumps(payload), encoding="utf-8")
    db_path = tmp_path / "research.db"
    runner = BrokenRunner()
    schedule = TickScheduleCoordinator(
        db_path,
        tick_coordinator=TickCoordinator(
            db_path,
            config_path=config_path,
            clock=lambda: NOW,
            runner=runner,
        ),
        config_path=config_path,
        clock=lambda: NOW,
    )

    with pytest.raises(RuntimeError, match="fixture runner failed"):
        schedule.poll()
    first_status = schedule.status()
    repeated_status = schedule.poll()

    assert first_status["state"] == "paused"
    assert first_status["runtime_error"] == "tick_enqueue_failed"
    assert repeated_status == first_status
    assert runner.calls == 1


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

    assert catalog["compatibility"]["database_schema"] == {"min": 16, "max": 16}
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
    schedule = schema["properties"]["tick"]["properties"]["schedule"]
    assert schedule["additionalProperties"] is False
    assert schedule["required"] == [
        "enabled",
        "schedule_id",
        "interval_seconds",
        "anchor_seconds",
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
