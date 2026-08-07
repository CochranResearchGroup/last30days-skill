"""Deterministic incident, notification, and human-observation gates."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta, timezone

import pytest

from lib.service_tick_incidents import (
    IncidentManager,
    IncidentSignal,
    NotificationExhaustedError,
    NotificationPreflightError,
    ObservationGateError,
    ObservationLease,
    classify_provider_issue,
)
from lib.service_tick_media import (
    ContentAddressedArtifactStore,
    MediaDerivativePublisher,
)


NOW = datetime(2026, 8, 4, 12, 0, tzinfo=timezone.utc)


class FixtureTransport:
    def __init__(self, transport_id, *, ready=True, succeeds=True):
        self.transport_id = transport_id
        self.ready = ready
        self.succeeds = succeeds
        self.payloads = []

    def readiness(self):
        return self.ready

    def send(self, payload):
        self.payloads.append(payload)
        if not self.succeeds:
            raise RuntimeError("fixture delivery failure")
        return f"delivery:{self.transport_id}:1"


class FixtureObservationTransport:
    def __init__(self):
        self.calls = []

    def acquire(self, *, incident_id, public_operator_url):
        self.calls.append((incident_id, public_operator_url))
        ordinal = len(self.calls)
        return ObservationLease(
            viewer_lease_id=f"viewer-lease-fresh-{ordinal}",
            public_operator_url=(
                f"https://guac.example.test/client/fresh-session-{ordinal}"
            ),
        )


@pytest.mark.parametrize(
    ("safe_error_code", "page_signals", "expected"),
    [
        ("captcha_required", (), "captcha_required"),
        ("checkpoint_required", (), "captcha_required"),
        ("navigation_failed", ("cloudflare_challenge",), "cloudflare_challenge"),
        ("rate_limit_detected", (), "rate_limit_warning"),
        ("rate_limited", (), "rate_limit_blocked"),
        ("auth_required", (), "reauthentication_required"),
        ("operator_ingress_unavailable", (), "reauthentication_required"),
        ("empty", (), None),
    ],
)
def test_provider_issue_classification_is_deterministic(
    safe_error_code, page_signals, expected
):
    assert classify_provider_issue(safe_error_code, page_signals) == expected


def test_browser_incident_persists_exact_page_then_notifies_by_sequential_failover(
    tmp_path,
):
    artifacts = ContentAddressedArtifactStore(tmp_path / "artifacts")
    manager = IncidentManager(
        tmp_path / "research.db",
        MediaDerivativePublisher(
            tmp_path / "research.db", artifacts, clock=lambda: NOW
        ),
        clock=lambda: NOW,
    )
    rendered_page = b"exact-rendered-browser-screenshot"
    incident = manager.record(
        IncidentSignal(
            tick_id="tick-001",
            lane_id="lane-x",
            source="x",
            profile_ref="profile-ref:social-primary",
            stage="collection",
            incident_type="captcha_required",
            severity="critical",
            safe_summary="Provider requires human verification.",
            access_partition_id="profile:social-primary",
            rendered_page=rendered_page,
            rendered_page_mime_type="image/png",
            operator_url="https://guac.example.test/client/manual-auth",
        )
    )
    first = FixtureTransport("ops-primary", succeeds=False)
    second = FixtureTransport("ops-fallback", succeeds=True)
    third = FixtureTransport("should-not-run", succeeds=True)

    delivery = manager.notify(incident.incident_id, [first, second, third])

    assert delivery.transport_id == "ops-fallback"
    assert len(first.payloads) == len(second.payloads) == 1
    assert third.payloads == []
    assert artifacts.read(incident.protected_artifact_ref) == rendered_page
    serialized_payload = str(second.payloads[0]).lower()
    assert "exact-rendered-browser-screenshot" not in serialized_payload
    assert "cookie" not in serialized_payload
    assert "guacamole" not in serialized_payload
    assert second.payloads[0]["protected_artifact_ref"] == (
        incident.protected_artifact_ref
    )
    assert second.payloads[0]["operator_url"] == (
        "https://guac.example.test/client/manual-auth"
    )


def test_incidents_deduplicate_resolve_exactly_and_gate_external_observation(tmp_path):
    db_path = tmp_path / "research.db"
    observation_transport = FixtureObservationTransport()
    manager = IncidentManager(
        db_path,
        MediaDerivativePublisher(
            db_path,
            ContentAddressedArtifactStore(tmp_path / "artifacts"),
            clock=lambda: NOW,
        ),
        observation_transport=observation_transport,
        clock=lambda: NOW,
    )
    signal = IncidentSignal(
        tick_id="tick-001",
        lane_id="lane-linkedin",
        source="linkedin",
        profile_ref="profile-ref:social-primary",
        stage="collection",
        incident_type="reauthentication_required",
        severity="critical",
        safe_summary="Provider session requires authentication.",
        access_partition_id="profile:social-primary",
        rendered_page=b"rendered-login-page",
        rendered_page_mime_type="image/png",
        operator_url="https://guac.example.test/client/session-1",
    )

    first = manager.record(signal)
    repeated = manager.record(signal)

    assert repeated.incident_id == first.incident_id
    assert repeated.occurrence_count == 2
    with pytest.raises(ObservationGateError, match="acknowledged"):
        manager.request_observation(first.incident_id)
    assert observation_transport.calls == []
    manager.acknowledge(first.incident_id, actor_ref="operator-ref:primary")
    assert manager.request_observation(first.incident_id) == (
        "https://guac.example.test/client/fresh-session-1"
    )
    assert observation_transport.calls == [
        (first.incident_id, "https://guac.example.test/client/session-1")
    ]
    assert manager.request_observation(first.incident_id) == (
        "https://guac.example.test/client/fresh-session-2"
    )
    assert len(observation_transport.calls) == 2
    conn = sqlite3.connect(db_path)
    assert conn.execute(
        "SELECT viewer_lease_id FROM service_incident_observations"
    ).fetchone() == ("viewer-lease-fresh-2",)
    conn.close()
    resolved = manager.resolve(
        first.incident_id,
        successful_execution_id="provider-attempt-recovered",
    )
    assert resolved.state == "resolved"


def test_browser_incident_rejects_local_or_non_https_operator_routes():
    for operator_url in (
        "http://127.0.0.1:19080/session-1",
        "https://localhost/session-1",
    ):
        with pytest.raises(ValueError, match="external HTTPS"):
            IncidentSignal(
                tick_id="tick-001",
                lane_id="lane-x",
                source="x",
                profile_ref="profile-ref:social-primary",
                stage="collection",
                incident_type="captcha_required",
                severity="critical",
                safe_summary="Challenge detected.",
                access_partition_id="profile:social-primary",
                operator_url=operator_url,
            )


def test_notification_exhaustion_persists_incident_and_blocks_later_preflight(
    tmp_path,
):
    db_path = tmp_path / "research.db"
    manager = IncidentManager(
        db_path,
        MediaDerivativePublisher(
            db_path,
            ContentAddressedArtifactStore(tmp_path / "artifacts"),
            clock=lambda: NOW,
        ),
        clock=lambda: NOW,
    )
    incident = manager.record(
        IncidentSignal(
            tick_id="tick-001",
            lane_id="lane-reddit",
            source="reddit",
            profile_ref="profile-ref:public",
            stage="collection",
            incident_type="provider_degraded",
            severity="error",
            safe_summary="Provider failed its bounded acquisition.",
            access_partition_id="public",
        )
    )
    primary = FixtureTransport("ops-primary", ready=True, succeeds=False)
    fallback = FixtureTransport("ops-fallback", ready=False, succeeds=False)

    with pytest.raises(NotificationExhaustedError):
        manager.notify(incident.incident_id, [primary, fallback])
    primary.ready = False
    with pytest.raises(NotificationPreflightError):
        manager.require_notification_readiness([primary, fallback])
    primary.ready = True
    fallback.ready = True
    assert manager.require_notification_readiness([primary, fallback]) == (
        "ops-primary"
    )

    import sqlite3

    conn = sqlite3.connect(db_path)
    assert conn.execute(
        """SELECT COUNT(*) FROM service_notification_deliveries
           WHERE incident_id = ? AND state = 'failed'""",
        (incident.incident_id,),
    ).fetchone()[0] == 2
    assert conn.execute(
        """SELECT COUNT(*) FROM service_incidents
           WHERE incident_type = 'notification_exhausted' AND state = 'open'"""
    ).fetchone()[0] == 1
    conn.close()


def test_notifications_deduplicate_remind_boundedly_and_send_one_resolution(tmp_path):
    current = [NOW]
    db_path = tmp_path / "research.db"
    manager = IncidentManager(
        db_path,
        MediaDerivativePublisher(
            db_path,
            ContentAddressedArtifactStore(tmp_path / "artifacts"),
            clock=lambda: current[0],
        ),
        clock=lambda: current[0],
    )
    signal = IncidentSignal(
        tick_id="tick-001",
        lane_id="lane-x",
        source="x",
        profile_ref="profile-ref:social-primary",
        stage="collection",
        incident_type="captcha_required",
        severity="critical",
        safe_summary="Provider requires human verification.",
        access_partition_id="profile:social-primary",
    )
    incident = manager.record(signal)
    transport = FixtureTransport("ops-primary")

    manager.notify(incident.incident_id, [transport], reminder_seconds=3600)
    manager.record(signal)
    current[0] += timedelta(minutes=30)
    manager.notify(incident.incident_id, [transport], reminder_seconds=3600)
    assert len(transport.payloads) == 1

    current[0] += timedelta(minutes=31)
    manager.notify(incident.incident_id, [transport], reminder_seconds=3600)
    manager.notify(incident.incident_id, [transport], reminder_seconds=3600)
    assert len(transport.payloads) == 2

    manager.resolve(
        incident.incident_id,
        successful_execution_id="provider-attempt-recovered",
    )
    manager.notify(incident.incident_id, [transport], reminder_seconds=3600)
    manager.notify(incident.incident_id, [transport], reminder_seconds=3600)

    assert [payload["notification_kind"] for payload in transport.payloads] == [
        "detected",
        "reminder",
        "resolved",
    ]


def test_meaningful_incident_change_captures_new_exact_rendered_page(tmp_path):
    db_path = tmp_path / "research.db"
    artifacts = ContentAddressedArtifactStore(tmp_path / "artifacts")
    manager = IncidentManager(
        db_path,
        MediaDerivativePublisher(db_path, artifacts, clock=lambda: NOW),
        clock=lambda: NOW,
    )
    first = manager.record(
        IncidentSignal(
            tick_id="tick-001",
            lane_id="lane-x",
            source="x",
            profile_ref="profile-ref:social-primary",
            stage="collection",
            incident_type="captcha_required",
            severity="warning",
            safe_summary="Challenge detected.",
            access_partition_id="profile:social-primary",
            rendered_page=b"first-rendered-page",
            rendered_page_mime_type="image/png",
        )
    )
    changed = manager.record(
        IncidentSignal(
            tick_id="tick-002",
            lane_id="lane-x",
            source="x",
            profile_ref="profile-ref:social-primary",
            stage="collection",
            incident_type="captcha_required",
            severity="critical",
            safe_summary="Challenge now blocks collection.",
            access_partition_id="profile:social-primary",
            rendered_page=b"changed-rendered-page",
            rendered_page_mime_type="image/png",
        )
    )

    assert changed.incident_id == first.incident_id
    assert changed.protected_artifact_ref != first.protected_artifact_ref
    assert artifacts.read(changed.protected_artifact_ref) == b"changed-rendered-page"

    import sqlite3

    conn = sqlite3.connect(db_path)
    assert conn.execute(
        """SELECT COUNT(*) FROM service_incident_transitions
           WHERE incident_id = ? AND transition_type = 'changed'""",
        (first.incident_id,),
    ).fetchone()[0] == 1
    assert conn.execute(
        """SELECT tick_id, artifact_ref FROM service_incident_artifacts
           WHERE incident_id = ? ORDER BY tick_id""",
        (first.incident_id,),
    ).fetchall() == [
        ("tick-001", first.protected_artifact_ref),
        ("tick-002", changed.protected_artifact_ref),
    ]
    conn.close()
