"""Behavioral tests for the versioned intelligence-service contracts."""

import pytest

from lib import service_contracts as contracts


def test_query_request_round_trips_the_public_v1_contract():
    payload = {
        "schema_version": 1,
        "request_id": "query-001",
        "profile_id": "default",
        "query": "agent browser reliability",
        "freshness_policy": "prefer_cache",
        "response_mode": "evidence",
        "filters": {
            "sources": ["reddit", "x"],
            "published_after": "2026-06-24T00:00:00Z",
        },
        "top_k": 8,
        "max_chars": 8192,
        "wait_ms": 0,
    }

    request = contracts.QueryRequest.from_dict(payload)

    assert request.to_dict() == payload


def test_evidence_item_round_trips_citation_and_rank_provenance():
    payload = {
        "schema_version": 1,
        "evidence_id": "ev-001",
        "document_id": "doc-001",
        "source": "youtube",
        "source_native_id": "video-001",
        "url": "https://www.youtube.com/watch?v=video-001",
        "title": "Reliable agent browsing",
        "snippet": "A bounded extract from the indexed transcript.",
        "author": "Example Channel",
        "published_at": "2026-07-20T12:00:00Z",
        "fetched_at": "2026-07-24T12:00:00Z",
        "acquisition_id": "acq-001",
        "content_hash": "sha256:abc123",
        "scores": {
            "lexical": 0.8,
            "semantic": 0.9,
            "graph": 0.2,
            "recency": 0.95,
            "fused": 0.87,
        },
    }

    evidence = contracts.EvidenceItem.from_dict(payload)

    assert evidence.to_dict() == payload


def test_acquisition_envelope_round_trips_without_browser_or_secret_state():
    payload = {
        "schema_version": 1,
        "acquisition_id": "acq-001",
        "job_id": "job-001",
        "profile_id": "default",
        "source": "x",
        "adapter": "agent_browser",
        "adapter_version": "1",
        "query": "agent browser reliability",
        "status": "succeeded",
        "observed_at": "2026-07-24T12:00:00Z",
        "fetched_at": "2026-07-24T12:00:10Z",
        "artifact_ref": "sha256:artifact123",
        "content_hash": "sha256:content123",
        "retention_class": "cache",
        "redaction_class": "authenticated",
        "item_count": 6,
        "diagnostics_ref": None,
    }

    envelope = contracts.AcquisitionEnvelope.from_dict(payload)

    assert envelope.to_dict() == payload
    assert not {
        "cookies",
        "credentials",
        "operator_url",
        "browser_id",
        "session_name",
    } & envelope.to_dict().keys()


def test_job_record_round_trips_supervisor_state_and_bounds():
    payload = {
        "schema_version": 1,
        "job_id": "job-001",
        "job_type": "refresh",
        "dedupe_key": "sha256:dedupe123",
        "state": "acquiring",
        "query_request_id": "query-001",
        "attempts": 1,
        "max_attempts": 2,
        "budget_cents": 100,
        "lease_owner": "worker-001",
        "lease_expires_at": "2026-07-24T12:05:00Z",
        "created_at": "2026-07-24T12:00:00Z",
        "updated_at": "2026-07-24T12:00:10Z",
        "published_index_version": None,
        "error_code": None,
    }

    job = contracts.JobRecord.from_dict(payload)

    assert job.to_dict() == payload


def test_job_event_round_trips_append_only_replay_data():
    payload = {
        "schema_version": 1,
        "event_id": "event-001",
        "job_id": "job-001",
        "sequence": 3,
        "event_type": "phase_started",
        "phase": "acquiring",
        "occurred_at": "2026-07-24T12:00:10Z",
        "payload": {"sources": ["reddit", "x"], "attempt": 1},
        "redaction_class": "restricted",
    }

    event = contracts.JobEvent.from_dict(payload)

    assert event.to_dict() == payload


def test_decision_record_round_trips_model_proposal_and_host_validation():
    payload = {
        "schema_version": 1,
        "decision_id": "decision-001",
        "job_id": "job-001",
        "loop_name": "entity_relationship_extraction",
        "action": "promote_relationship",
        "confidence": 0.91,
        "evidence_ids": ["ev-001"],
        "rationale": "The relationship is explicitly supported by the evidence.",
        "model_ref": "openai:gpt-5-mini:extractor-v1",
        "input_ref": "sha256:input123",
        "output_ref": "sha256:output123",
        "accepted": True,
        "validator_errors": [],
        "created_at": "2026-07-24T12:01:00Z",
    }

    decision = contracts.DecisionRecord.from_dict(payload)

    assert decision.to_dict() == payload


def test_schema_catalog_is_the_golden_contract_for_every_v1_envelope():
    catalog = contracts.load_schema_catalog()

    assert catalog["schema_version"] == 1
    assert set(catalog["contracts"]) == {
        "query_request",
        "evidence_item",
        "acquisition_envelope",
        "job_record",
        "job_event",
        "decision_record",
    }
    assert catalog["contracts"]["query_request"]["properties"][
        "freshness_policy"
    ]["enum"] == [
        "cache_only",
        "prefer_cache",
        "refresh_if_stale",
        "force_refresh",
    ]


def test_parse_envelope_dispatches_by_contract_name_and_rejects_unknown_types():
    payload = {
        "schema_version": 1,
        "event_id": "event-001",
        "job_id": "job-001",
        "sequence": 1,
        "event_type": "job_created",
        "phase": "queued",
        "occurred_at": "2026-07-24T12:00:00Z",
        "payload": {},
        "redaction_class": "public",
    }

    event = contracts.parse_envelope("job_event", payload)

    assert isinstance(event, contracts.JobEvent)
    assert event.to_dict() == payload
    with pytest.raises(contracts.ContractValidationError, match="unknown contract"):
        contracts.parse_envelope("browser_session", payload)


def test_event_payload_rejects_secret_and_browser_lease_fields():
    payload = {
        "schema_version": 1,
        "event_id": "event-unsafe",
        "job_id": "job-001",
        "sequence": 2,
        "event_type": "source_failed",
        "phase": "acquiring",
        "occurred_at": "2026-07-24T12:00:10Z",
        "payload": {
            "safe_error": "authentication required",
            "nested": {"cookie": "must-not-enter-the-ledger"},
        },
        "redaction_class": "restricted",
    }

    with pytest.raises(contracts.ContractValidationError, match="forbidden field"):
        contracts.JobEvent.from_dict(payload)
