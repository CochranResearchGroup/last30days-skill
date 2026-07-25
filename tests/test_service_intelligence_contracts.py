"""Common deterministic App Intelligence contracts and content assessment."""

from __future__ import annotations

import json
import sqlite3

from lib import service_contracts
from lib.service_intelligence_contracts import (
    ContentAssessmentQueue,
    IntelligenceTaskRequest,
    IntelligenceTaskResult,
    TaskContractRegistry,
    ValidatorCode,
)
from lib.service_store import ServiceStore


def _request(**overrides):
    payload = {
        "schema_version": 1,
        "contract_name": "intelligence_task_request",
        "contract_version": 1,
        "task_type": "content_assessment",
        "task_id": "task-001",
        "job_id": "job-001",
        "run_id": "run-001",
        "idempotency_key": "assessment:v1:abc",
        "input_artifact_ref": "artifact:input",
        "input_digest": "sha256:" + "a" * 64,
        "evidence_refs": [
            {
                "evidence_id": "evidence-001",
                "version_id": "version-001",
                "chunk_id": "chunk-001",
                "content_digest": "sha256:" + "b" * 64,
                "observed_at": "2026-07-25T12:00:00Z",
                "valid_from": None,
                "valid_to": None,
                "access_partition_id": "public",
            }
        ],
        "source_version_ids": ["version-001"],
        "corpus_version": "index-001",
        "policy_version": "content-assessment-v1",
        "worker_config_ref": "worker:default",
        "access_partition_id": "public",
        "redaction_class": "public",
        "requested_at": "2026-07-25T12:00:00Z",
        "allowed_actions": ["record_assessment"],
        "limits": {
            "max_items": 10,
            "max_bytes": 65536,
            "max_calls": 1,
            "max_cost_cents": 5,
            "wall_timeout_seconds": 60,
        },
    }
    payload.update(overrides)
    return IntelligenceTaskRequest.from_dict(payload)


def test_common_task_contract_round_trip_and_registry_are_strict():
    request = _request()
    assert IntelligenceTaskRequest.from_dict(request.to_dict()) == request
    assert (
        TaskContractRegistry.default().request("content_assessment", 1)
        is IntelligenceTaskRequest
    )
    assert (
        service_contracts.parse_envelope(
            "intelligence_task_request", request.to_dict()
        )
        == request
    )

    invalid = request.to_dict()
    invalid["browser_profile"] = "must-never-cross-contract"
    result = IntelligenceTaskRequest.validate(invalid)
    assert result.value == ValidatorCode.SCHEMA_INVALID.value


def test_result_correlation_and_evidence_closure_use_stable_codes():
    request = _request()
    result = IntelligenceTaskResult.from_worker_dict(
        {
            "schema_version": 1,
            "contract_name": "intelligence_task_result",
            "contract_version": 1,
            "task_type": "content_assessment",
            "task_id": "task-001",
            "run_id": "run-001",
            "input_digest": request.input_digest,
            "policy_version": request.policy_version,
            "action": "record_assessment",
            "proposals": [
                {
                    "proposal_kind": "content_signal",
                    "proposal_key": "signal:novel",
                    "confidence": 0.8,
                    "evidence_ids": ["evidence-not-supplied"],
                    "payload": {
                        "content_type": "post",
                        "novelty": "novel",
                        "relevance": "high",
                        "follow_up_priority": "normal",
                    },
                }
            ],
            "uncertainty_codes": [],
            "rationale": "The supplied post contains a new implementation detail.",
            "worker_ref": "openai-codex:gpt-5.5",
        }
    )

    receipt = TaskContractRegistry.default().validate_result(request, result)
    assert receipt.accepted is False
    assert receipt.validator_codes == (ValidatorCode.UNKNOWN_EVIDENCE.value,)


def test_profile_change_and_identity_contracts_only_accept_host_candidates():
    registry = TaskContractRegistry.default()
    assert registry.request("profile_change_assessment", 1) is IntelligenceTaskRequest
    assert registry.request("identity_resolution", 1) is IntelligenceTaskRequest

    request = _request(
        task_type="identity_resolution",
        policy_version="identity-resolution-v1",
        allowed_actions=["record_identity_resolution"],
    )
    valid = IntelligenceTaskResult.from_worker_dict(
        {
            "schema_version": 1,
            "contract_name": "intelligence_task_result",
            "contract_version": 1,
            "task_type": "identity_resolution",
            "task_id": request.task_id,
            "run_id": request.run_id,
            "input_digest": request.input_digest,
            "policy_version": request.policy_version,
            "action": "record_identity_resolution",
            "proposals": [
                {
                    "proposal_kind": "identity_resolution",
                    "proposal_key": "identity-candidate-001",
                    "confidence": 0.45,
                    "evidence_ids": ["evidence-001"],
                    "payload": {
                        "candidate_id": "identity-candidate-001",
                        "outcome": "ambiguous",
                    },
                }
            ],
            "uncertainty_codes": ["shared_evidence"],
            "rationale": "The bounded evidence does not distinguish the accounts.",
            "worker_ref": "openai-codex:gpt-5.5",
        }
    )
    assert registry.validate_result(request, valid).accepted is True

    invalid = IntelligenceTaskResult.from_worker_dict(
        {
            **{
                key: value
                for key, value in valid.to_dict().items()
                if key != "output_digest"
            },
            "proposals": [
                {
                    **valid.proposals[0].to_dict(),
                    "payload": {
                        "candidate_id": "model-invented-candidate",
                        "outcome": "same_entity",
                    },
                }
            ],
        }
    )
    receipt = registry.validate_result(request, invalid)
    assert receipt.accepted is False
    assert ValidatorCode.SCHEMA_INVALID.value in receipt.validator_codes


def test_knowledge_extraction_and_retrieval_evaluation_are_bounded_proposals():
    registry = TaskContractRegistry.default()
    assert registry.request("knowledge_extraction", 1) is IntelligenceTaskRequest
    assert registry.request("retrieval_evaluation", 1) is IntelligenceTaskRequest

    request = _request(
        task_type="retrieval_evaluation",
        policy_version="retrieval-evaluation-v1",
        allowed_actions=["record_retrieval_evaluation"],
    )
    result = IntelligenceTaskResult.from_worker_dict(
        {
            "schema_version": 1,
            "contract_name": "intelligence_task_result",
            "contract_version": 1,
            "task_type": request.task_type,
            "task_id": request.task_id,
            "run_id": request.run_id,
            "input_digest": request.input_digest,
            "policy_version": request.policy_version,
            "action": "record_retrieval_evaluation",
            "proposals": [
                {
                    "proposal_kind": "retrieval_evaluation",
                    "proposal_key": "case-001",
                    "confidence": 0.9,
                    "evidence_ids": ["evidence-001"],
                    "payload": {
                        "case_id": "case-001",
                        "verdict": "pass",
                        "evidence_recall": 1.0,
                        "temporal_correct": True,
                        "access_safe": True,
                    },
                }
            ],
            "uncertainty_codes": [],
            "rationale": "All expected evidence was returned in the right interval.",
            "worker_ref": "openai-codex:gpt-5.5",
        }
    )
    assert registry.validate_result(request, result).accepted is True


def test_content_assessment_queue_is_idempotent_and_replayable(tmp_path):
    db_path = tmp_path / "research.db"
    ServiceStore(db_path).initialize()
    queue = ContentAssessmentQueue(db_path)
    request = _request(job_id=None, run_id="run-001")

    first = queue.enqueue(request)
    second = queue.enqueue(request)
    assert first.task_id == second.task_id

    conn = sqlite3.connect(db_path)
    try:
        count = conn.execute(
            "SELECT COUNT(*) FROM service_intelligence_tasks"
        ).fetchone()[0]
        stored = conn.execute(
            "SELECT request_json FROM service_intelligence_tasks"
        ).fetchone()[0]
    finally:
        conn.close()
    assert count == 1
    assert json.loads(stored) == request.to_dict()

    result = IntelligenceTaskResult.from_worker_dict(
        {
            "schema_version": 1,
            "contract_name": "intelligence_task_result",
            "contract_version": 1,
            "task_type": "content_assessment",
            "task_id": request.task_id,
            "run_id": request.run_id,
            "input_digest": request.input_digest,
            "policy_version": request.policy_version,
            "action": "record_assessment",
            "proposals": [
                {
                    "proposal_kind": "content_signal",
                    "proposal_key": "signal:novel",
                    "confidence": 0.8,
                    "evidence_ids": ["evidence-001"],
                    "payload": {
                        "content_type": "post",
                        "novelty": "novel",
                        "relevance": "high",
                        "follow_up_priority": "normal",
                    },
                }
            ],
            "uncertainty_codes": [],
            "rationale": "The supplied evidence contains a new implementation detail.",
            "worker_ref": "openai-codex:gpt-5.5",
        }
    )
    receipt = queue.complete(request.task_id, result)
    replay = queue.complete(request.task_id, result)

    assert receipt.accepted is True
    assert replay == receipt
    conn = sqlite3.connect(db_path)
    try:
        state = conn.execute(
            "SELECT state FROM service_intelligence_tasks"
        ).fetchone()[0]
        validation_count = conn.execute(
            "SELECT COUNT(*) FROM service_intelligence_validation_receipts"
        ).fetchone()[0]
        promotion = conn.execute(
            """SELECT accepted_ids_json, idempotency_outcome
               FROM service_intelligence_promotion_receipts"""
        ).fetchone()
        replay_count = conn.execute(
            "SELECT COUNT(*) FROM service_intelligence_replay_receipts"
        ).fetchone()[0]
    finally:
        conn.close()
    assert state == "completed"
    assert json.loads(promotion[0]) == ["signal:novel"]
    assert promotion[1] == "created"
    assert validation_count == 1
    assert replay_count == 1
