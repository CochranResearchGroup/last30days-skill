"""Provider-free contracts for durable evidence-grounded questions."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from lib import service_question_contracts as question_contracts
from lib.service_client import ServiceClient


def _request_payload() -> dict[str, object]:
    return {
        "schema_version": 1,
        "request_id": "question-request-001",
        "profile_id": "public",
        "question": "What changed in browser-agent reliability?",
        "filters": {
            "sources": ["reddit", "x"],
            "published_after": "2026-09-01T00:00:00Z",
        },
        "temporal": {
            "as_of": "2026-09-13T12:00:00Z",
            "during_from": None,
            "during_to": None,
            "known_as_of": None,
        },
        "answer_mode": "synthesized",
        "model_fallback": "none",
        "limits": {
            "evidence_limit": 10,
            "max_evidence_bytes": 65536,
            "max_answer_characters": 4096,
            "max_statements": 8,
            "wait_ms": 0,
            "max_evidence_age_seconds": 604800,
            "max_attempts": 2,
        },
    }


def test_question_request_is_strict_and_has_a_stable_fingerprint():
    payload = _request_payload()

    request = question_contracts.QuestionRequestV1.from_dict(payload)

    assert request.to_dict() == payload
    assert request.request_fingerprint.startswith("sha256:")
    assert request.idempotency_key.startswith("question-request:v1:")
    assert (
        question_contracts.QuestionRequestV1.from_dict(copy.deepcopy(payload))
        == request
    )

    with pytest.raises(question_contracts.QuestionContractError, match="unknown"):
        question_contracts.QuestionRequestV1.from_dict({**payload, "browse": True})

    invalid_range = copy.deepcopy(payload)
    invalid_range["temporal"] = {
        "as_of": None,
        "during_from": "2026-09-14T00:00:00Z",
        "during_to": "2026-09-13T00:00:00Z",
        "known_as_of": None,
    }
    with pytest.raises(
        question_contracts.QuestionContractError, match="during_from"
    ):
        question_contracts.QuestionRequestV1.from_dict(invalid_range)

    invalid_limits = copy.deepcopy(payload)
    invalid_limits["limits"] = {**payload["limits"], "max_attempts": 3}
    with pytest.raises(question_contracts.QuestionContractError, match="max_attempts"):
        question_contracts.QuestionRequestV1.from_dict(invalid_limits)


def test_published_question_limit_bounds_match_runtime_and_client_wait(monkeypatch):
    schema = json.loads(
        (Path(__file__).parents[1] / "skills/last30days/schemas/question-contracts-v1.json").read_text()
    )
    limits = schema["contracts"]["question_request"]["properties"]["limits"]["properties"]
    assert (limits["evidence_limit"]["minimum"], limits["evidence_limit"]["maximum"]) == (1, 50)
    assert (limits["max_evidence_bytes"]["minimum"], limits["max_evidence_bytes"]["maximum"]) == (1024, 1_048_576)
    for evidence_limit, evidence_bytes in ((1, 1024), (50, 1_048_576)):
        payload = copy.deepcopy(_request_payload())
        payload["limits"] = {**payload["limits"], "evidence_limit": evidence_limit, "max_evidence_bytes": evidence_bytes, "wait_ms": 30_000}
        assert question_contracts.QuestionRequestV1.from_dict(payload).to_dict() == payload

    observed = {}
    client = ServiceClient(Path("/tmp/unused-question-test.sock"))
    request = question_contracts.QuestionRequestV1.from_dict({**_request_payload(), "limits": {**_request_payload()["limits"], "wait_ms": 30_000}})
    def fake_request(method, path, payload=None, *, timeout=None):
        observed["timeout"] = timeout
        return {"schema_version": 1, "question_id": "question-001", "state": "pending", "attempt_count": 0, "max_attempts": 2, "lease_generation": 0, "lease_expires_at": None, "answer": None, "error": None}
    monkeypatch.setattr(client, "_request", fake_request)
    client.ask_question(request)
    assert observed["timeout"] == 35.0


def test_answer_statement_citation_status_and_error_contracts_are_closed():
    citation = question_contracts.QuestionCitationV1.from_dict(
        {
            "evidence_id": "question-evidence-001",
            "storage_family": "temporal",
            "version_id": "version-001",
            "content_hash": "sha256:content-001",
            "source_url": "https://x.example/post/1",
            "access_partition_id": "public",
        }
    )
    statement = question_contracts.AnswerStatementV1.create(
        text="The reliability change was observed.",
        statement_kind="source_fact",
        support_state="supported",
        citations=(citation,),
        alternatives=(),
    )
    answer = question_contracts.QuestionAnswerV1.create(
        question_id="question-001",
        request_fingerprint="sha256:request",
        search_head_id="search-head-001",
        evidence_set_id="evidence-set-001",
        answer_state="answered",
        summary="The reliability change was observed.",
        statements=(statement,),
        uncertainty_codes=(),
        coverage={"partial": False, "stale": False},
        worker_ref="fake-answer-worker-v1",
        generated_at="2026-09-13T12:00:00Z",
        input_digest="sha256:input",
        attempt_count=1,
        model_invoked=False,
        evidence_only_fallback=False,
        error=None,
    )

    assert statement.statement_id.startswith("statement-")
    assert answer.answer_id.startswith("answer-")
    assert answer.output_digest.startswith("sha256:")
    assert question_contracts.QuestionAnswerV1.from_dict(answer.to_dict()) == answer

    status = question_contracts.QuestionStatusV1.from_dict(
        {
            "schema_version": 1,
            "question_id": answer.question_id,
            "state": "answered",
            "attempt_count": 1,
            "max_attempts": 2,
            "lease_generation": 1,
            "lease_expires_at": None,
            "answer": answer.to_dict(),
            "error": None,
        }
    )
    assert status.answer == answer
    assert status.to_dict()["answer"] == answer.to_dict()

    error = question_contracts.QuestionErrorV1.from_dict(
        {"code": "invalid_citation", "message": "citation is unavailable", "retryable": False}
    )
    assert error.to_dict()["code"] == "invalid_citation"

    with pytest.raises(question_contracts.QuestionContractError, match="unknown"):
        question_contracts.QuestionAnswerV1.from_dict({**answer.to_dict(), "raw_prompt": "no"})
