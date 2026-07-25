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


def test_query_request_rejects_unbounded_request_id():
    payload = {
        "schema_version": 1,
        "request_id": "r" * 129,
        "profile_id": "default",
        "query": "bounded query",
        "freshness_policy": "cache_only",
        "response_mode": "evidence",
        "filters": {},
        "top_k": 8,
        "max_chars": 8192,
        "wait_ms": 0,
    }

    with pytest.raises(contracts.ContractValidationError, match="request_id"):
        contracts.QueryRequest.from_dict(payload)


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
        "media": [],
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


def test_acquisition_work_request_round_trips_bounded_worker_authority():
    payload = {
        "schema_version": 1,
        "work_id": "work-001",
        "job_id": "job-001",
        "lease_generation": 2,
        "attempt": 1,
        "profile_id": "default",
        "source": "facebook",
        "query": "browser service reliability",
        "from_date": "2026-06-24",
        "to_date": "2026-07-24",
        "depth": "standard",
        "adapter": "facebook_agent_browser",
        "adapter_version": "1",
        "wall_timeout_seconds": 90,
        "item_limit": 20,
        "network_request_limit": 50,
        "cost_budget_cents": 25,
    }

    request = contracts.AcquisitionWorkRequest.from_dict(payload)

    assert request.to_dict() == payload


def test_acquisition_work_result_round_trips_sanitized_items_and_retry_state():
    payload = {
        "schema_version": 1,
        "work_id": "work-001",
        "job_id": "job-001",
        "lease_generation": 2,
        "source": "facebook",
        "adapter": "facebook_agent_browser",
        "adapter_version": "1",
        "status": "partial",
        "safe_error_code": "search_unavailable",
        "retry_class": "transient",
        "retry_after_seconds": 30,
        "observed_at": "2026-07-24T12:00:00Z",
        "fetched_at": "2026-07-24T12:00:10Z",
        "items": [
            {
                "source_native_id": "post-001",
                "url": "https://facebook.example/posts/1",
                "title": "Cached service",
                "text": "A useful sanitized post.",
                "author": "Author",
                "published_at": "2026-07-23T12:00:00Z",
                "metadata": {"engagement": 4},
            }
        ],
        "item_count": 1,
        "cost_cents": 3,
        "diagnostics": {"candidate_count": 2, "accepted_count": 1},
    }

    result = contracts.AcquisitionWorkResult.from_dict(payload)

    assert result.to_dict() == payload


def test_acquisition_work_result_rejects_browser_leases_in_diagnostics():
    payload = {
        "schema_version": 1,
        "work_id": "work-unsafe",
        "job_id": "job-001",
        "lease_generation": 1,
        "source": "x",
        "adapter": "x_agent_browser",
        "adapter_version": "1",
        "status": "failed",
        "safe_error_code": "route_stale",
        "retry_class": "transient",
        "retry_after_seconds": 5,
        "observed_at": "2026-07-24T12:00:00Z",
        "fetched_at": "2026-07-24T12:00:01Z",
        "items": [],
        "item_count": 0,
        "cost_cents": 0,
        "diagnostics": {"route_id": "must-not-persist"},
    }

    with pytest.raises(contracts.ContractValidationError, match="forbidden field"):
        contracts.AcquisitionWorkResult.from_dict(payload)


def test_acquisition_work_result_rejects_unsafe_codes_and_naive_timestamps():
    payload = {
        "schema_version": 1,
        "work_id": "work-invalid",
        "job_id": "job-invalid",
        "lease_generation": 1,
        "source": "x",
        "adapter": "x_agent_browser",
        "adapter_version": "1",
        "status": "failed",
        "safe_error_code": "private URL leaked",
        "retry_class": "permanent",
        "retry_after_seconds": None,
        "observed_at": "2026-07-24T12:00:00",
        "fetched_at": "2026-07-24T12:00:01Z",
        "items": [],
        "item_count": 0,
        "cost_cents": 0,
        "diagnostics": {},
    }

    with pytest.raises(contracts.ContractValidationError):
        contracts.AcquisitionWorkResult.from_dict(payload)

    with pytest.raises(contracts.ContractValidationError, match="timezone"):
        contracts.AcquisitionWorkResult.from_dict(
            {
                **payload,
                "safe_error_code": "validator_failed",
            }
        )


def test_entity_and_relationship_proposals_round_trip_with_evidence():
    entity_payload = {
        "schema_version": 1,
        "proposal_id": "entity-proposal-001",
        "document_id": "doc-001",
        "evidence_chunk_id": "chunk-001",
        "canonical_name": "OpenAI",
        "entity_type": "organization",
        "evidence_start": 0,
        "evidence_end": 6,
        "extractor_version": "deterministic-entities-v1",
        "confidence": 1.0,
    }
    relationship_payload = {
        "schema_version": 1,
        "proposal_id": "relationship-proposal-001",
        "document_id": "doc-001",
        "evidence_chunk_id": "chunk-001",
        "evidence_start": 0,
        "evidence_end": 24,
        "subject_entity_id": "entity-openai",
        "predicate": "created",
        "object_entity_id": "entity-chatgpt",
        "extractor_version": "deterministic-relations-v1",
        "confidence": 0.9,
    }

    assert contracts.EntityProposal.from_dict(entity_payload).to_dict() == entity_payload
    assert (
        contracts.RelationshipProposal.from_dict(relationship_payload).to_dict()
        == relationship_payload
    )


def test_graph_proposals_reject_invalid_offsets_and_self_edges():
    with pytest.raises(contracts.ContractValidationError, match="evidence range"):
        contracts.EntityProposal.from_dict(
            {
                "schema_version": 1,
                "proposal_id": "entity-proposal-invalid",
                "document_id": "doc-001",
                "evidence_chunk_id": "chunk-001",
                "canonical_name": "OpenAI",
                "entity_type": "organization",
                "evidence_start": 6,
                "evidence_end": 6,
                "extractor_version": "deterministic-entities-v1",
                "confidence": 1.0,
            }
        )
    with pytest.raises(contracts.ContractValidationError, match="self-edge"):
        contracts.RelationshipProposal.from_dict(
            {
                "schema_version": 1,
                "proposal_id": "relationship-proposal-invalid",
                "document_id": "doc-001",
                "evidence_chunk_id": "chunk-001",
                "evidence_start": 0,
                "evidence_end": 24,
                "subject_entity_id": "entity-openai",
                "predicate": "related_to",
                "object_entity_id": "entity-openai",
                "extractor_version": "deterministic-relations-v1",
                "confidence": 0.8,
            }
        )


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
        "spent_cents": 25,
        "lease_generation": 1,
        "lease_owner": "worker-001",
        "lease_expires_at": "2026-07-24T12:05:00Z",
        "not_before_at": None,
        "created_at": "2026-07-24T12:00:00Z",
        "updated_at": "2026-07-24T12:00:10Z",
        "published_index_version": None,
        "error_code": None,
    }

    job = contracts.JobRecord.from_dict(payload)

    assert job.to_dict() == payload


def test_job_record_rejects_spend_above_its_budget():
    payload = {
        "schema_version": 1,
        "job_id": "job-budget",
        "job_type": "refresh",
        "dedupe_key": "sha256:budget",
        "state": "queued",
        "query_request_id": "query-budget",
        "attempts": 0,
        "max_attempts": 2,
        "budget_cents": 10,
        "spent_cents": 11,
        "lease_generation": 0,
        "lease_owner": None,
        "lease_expires_at": None,
        "not_before_at": None,
        "created_at": "2026-07-24T12:00:00Z",
        "updated_at": "2026-07-24T12:00:00Z",
        "published_index_version": None,
        "error_code": None,
    }

    with pytest.raises(contracts.ContractValidationError, match="spent_cents"):
        contracts.JobRecord.from_dict(payload)


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
        "query_response",
        "service_info",
        "evidence_item",
        "acquisition_work_request",
        "acquisition_work_result",
        "entity_proposal",
        "relationship_proposal",
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


def test_query_response_round_trips_bounded_evidence_and_freshness():
    payload = {
        "schema_version": 1,
        "request_id": "query-001",
        "index_version": "index-001",
        "cache_status": "fresh",
        "generated_at": "2026-07-24T12:00:00Z",
        "evidence": [],
        "brief": None,
        "job_id": None,
        "diagnostics_available": False,
        "truncated": False,
        "next_cursor": None,
    }

    response = contracts.QueryResponse.from_dict(payload)

    assert response.to_dict() == payload


def test_service_info_round_trips_dynamic_runtime_capabilities():
    payload = {
        "schema_version": 1,
        "service_version": "0.1.0",
        "database_schema_version": 3,
        "status": "ready",
        "capabilities": ["cache_query", "lexical_search", "semantic_search"],
        "sources": {"reddit": {"ready": True, "reason": None}},
        "freshness_policies": [
            "cache_only",
            "prefer_cache",
            "refresh_if_stale",
            "force_refresh",
        ],
        "response_modes": ["evidence", "brief"],
        "limits": {"default_top_k": 8, "max_top_k": 100, "max_chars": 65536},
        "index": {
            "version": "index-001",
            "document_count": 4,
            "embedding_model": None,
        },
        "transport": "unix",
    }

    info = contracts.ServiceInfo.from_dict(payload)

    assert info.to_dict() == payload
