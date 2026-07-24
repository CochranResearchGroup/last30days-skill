"""Integration tests for the durable intelligence-service ledger."""

import pytest

from lib import service_contracts as contracts
from lib.service_store import EnvelopeConflictError, ServiceStore


def test_service_store_round_trips_a_versioned_envelope(tmp_path):
    ledger = ServiceStore(tmp_path / "research.db")
    ledger.initialize()
    payload = {
        "schema_version": 1,
        "event_id": "event-001",
        "job_id": "job-001",
        "sequence": 1,
        "event_type": "job_created",
        "phase": "queued",
        "occurred_at": "2026-07-24T12:00:00Z",
        "payload": {"dedupe_key": "sha256:dedupe123"},
        "redaction_class": "public",
    }
    event = contracts.JobEvent.from_dict(payload)

    ledger.put_envelope("job_event", "event-001", event)

    restored = ledger.get_envelope("job_event", "event-001")
    assert isinstance(restored, contracts.JobEvent)
    assert restored.to_dict() == payload


def _sample_envelopes():
    return {
        "query_request": (
            "query-001",
            {
                "schema_version": 1,
                "request_id": "query-001",
                "profile_id": "default",
                "query": "agent browser reliability",
                "freshness_policy": "prefer_cache",
                "response_mode": "evidence",
                "filters": {},
                "top_k": 8,
                "max_chars": 8192,
                "wait_ms": 0,
            },
        ),
        "evidence_item": (
            "ev-001",
            {
                "schema_version": 1,
                "evidence_id": "ev-001",
                "document_id": "doc-001",
                "source": "reddit",
                "source_native_id": "post-001",
                "url": "https://reddit.com/r/test/1",
                "title": "Evidence",
                "snippet": "A compact cited extract.",
                "author": "author",
                "published_at": None,
                "fetched_at": "2026-07-24T12:00:00Z",
                "acquisition_id": "acq-001",
                "content_hash": "sha256:content",
                "scores": {
                    "lexical": 0.8,
                    "semantic": 0.7,
                    "graph": 0.0,
                    "recency": 0.9,
                    "fused": 0.82,
                },
            },
        ),
        "acquisition_envelope": (
            "acq-001",
            {
                "schema_version": 1,
                "acquisition_id": "acq-001",
                "job_id": "job-001",
                "profile_id": "default",
                "source": "reddit",
                "adapter": "reddit_api",
                "adapter_version": "1",
                "query": "agent browser reliability",
                "status": "succeeded",
                "observed_at": "2026-07-24T12:00:00Z",
                "fetched_at": "2026-07-24T12:00:01Z",
                "artifact_ref": None,
                "content_hash": "sha256:content",
                "retention_class": "cache",
                "redaction_class": "public",
                "item_count": 1,
                "diagnostics_ref": None,
            },
        ),
        "job_record": (
            "job-001",
            {
                "schema_version": 1,
                "job_id": "job-001",
                "job_type": "refresh",
                "dedupe_key": "sha256:dedupe",
                "state": "queued",
                "query_request_id": "query-001",
                "attempts": 0,
                "max_attempts": 2,
                "budget_cents": 100,
                "lease_owner": None,
                "lease_expires_at": None,
                "created_at": "2026-07-24T12:00:00Z",
                "updated_at": "2026-07-24T12:00:00Z",
                "published_index_version": None,
                "error_code": None,
            },
        ),
        "job_event": (
            "event-001",
            {
                "schema_version": 1,
                "event_id": "event-001",
                "job_id": "job-001",
                "sequence": 1,
                "event_type": "job_created",
                "phase": "queued",
                "occurred_at": "2026-07-24T12:00:00Z",
                "payload": {},
                "redaction_class": "public",
            },
        ),
        "decision_record": (
            "decision-001",
            {
                "schema_version": 1,
                "decision_id": "decision-001",
                "job_id": "job-001",
                "loop_name": "entity_extraction",
                "action": "reject",
                "confidence": 0.5,
                "evidence_ids": ["ev-001"],
                "rationale": "Insufficient evidence.",
                "model_ref": "openai:model:extractor-v1",
                "input_ref": "sha256:input",
                "output_ref": "sha256:output",
                "accepted": False,
                "validator_errors": ["insufficient_evidence"],
                "created_at": "2026-07-24T12:01:00Z",
            },
        ),
    }


def test_service_store_round_trips_every_v1_contract(tmp_path):
    ledger = ServiceStore(tmp_path / "all-contracts.db")
    ledger.initialize()

    for contract_name, (envelope_id, payload) in _sample_envelopes().items():
        envelope = contracts.parse_envelope(contract_name, payload)
        ledger.put_envelope(contract_name, envelope_id, envelope)
        restored = ledger.get_envelope(contract_name, envelope_id)
        assert restored.to_dict() == payload


def test_service_store_is_idempotent_but_rejects_id_reuse(tmp_path):
    ledger = ServiceStore(tmp_path / "immutable.db")
    ledger.initialize()
    _, (envelope_id, payload) = next(
        (item for item in _sample_envelopes().items() if item[0] == "job_event")
    )
    event = contracts.JobEvent.from_dict(payload)

    ledger.put_envelope("job_event", envelope_id, event)
    ledger.put_envelope("job_event", envelope_id, event)

    conflicting = contracts.JobEvent.from_dict(
        {**payload, "event_type": "different_event"}
    )
    with pytest.raises(EnvelopeConflictError, match="immutable envelope conflict"):
        ledger.put_envelope("job_event", envelope_id, conflicting)
