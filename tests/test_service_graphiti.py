"""Concrete local Graphiti projection boundary."""

from __future__ import annotations

import json
import urllib.error

import pytest

from lib.service_graphiti import GraphitiHTTPSink


class FakeResponse:
    def __init__(self, payload, status=201):
        self.payload = payload
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return None

    def read(self, _limit=-1):
        return json.dumps(self.payload).encode()


def test_graphiti_sink_uses_partitioned_stable_nodes_and_health_preflight():
    calls = []

    def opener(request, timeout):
        calls.append((request, timeout))
        if request.full_url.endswith("/healthcheck"):
            return FakeResponse({"status": "healthy"}, 200)
        return FakeResponse({"uuid": json.loads(request.data)["uuid"]}, 201)

    sink = GraphitiHTTPSink(
        "http://127.0.0.1:8829",
        group_prefix="last30days",
        opener=opener,
    )
    first = sink.upsert(
        aggregate_kind="claim",
        aggregate_id="claim-1",
        payload={"claim_id": "claim-1", "predicate": "works_for"},
        partition_id="profile:linkedin-primary",
    )
    second = sink.upsert(
        aggregate_kind="claim",
        aggregate_id="claim-1",
        payload={"claim_id": "claim-1", "predicate": "works_for"},
        partition_id="profile:linkedin-primary",
    )

    assert first == second
    posted = json.loads(calls[1][0].data)
    assert posted["uuid"] == json.loads(calls[3][0].data)["uuid"]
    assert posted["group_id"] == "last30days_profile_linkedin-primary"
    assert posted["name"] == "claim:claim-1"
    assert posted["summary"].startswith("last30days-projection-v1 ")
    assert "profile:linkedin-primary" not in posted["summary"]


def test_graphiti_sink_rejects_non_loopback_and_unhealthy_runtime():
    with pytest.raises(ValueError):
        GraphitiHTTPSink("https://graph.example.com")

    def opener(request, timeout):
        del timeout
        if request.full_url.endswith("/healthcheck"):
            return FakeResponse({"status": "degraded"}, 200)
        raise AssertionError("write must not run")

    sink = GraphitiHTTPSink("http://127.0.0.1:8829", opener=opener)
    with pytest.raises(RuntimeError, match="not healthy"):
        sink.upsert(
            aggregate_kind="event",
            aggregate_id="event-1",
            payload={"event_id": "event-1"},
            partition_id="public",
        )
