"""Public question composition over real, isolated stored evidence."""

import threading
import time

import pytest
from lib import service_question_contracts as contracts
from lib.service_post_search import PostSearchBackend
from lib.service_questions import QuestionService

from tests.test_service_post_search import _seed_packet_two
from tests.test_service_question_evidence import _question_request, _seed_corpus


def test_question_preserves_every_search_filter_before_selecting_evidence(tmp_path):
    db_path = tmp_path / "questions.db"
    _seed_packet_two(db_path)
    service = QuestionService(db_path, PostSearchBackend(db_path))
    filters = {
        "sources": ["x"],
        "authors": ["bob"],
        "topic_ids": ["7"],
        "collection_refs": ["temporal:schedule:schedule-1"],
        "published_after": "2026-09-07T00:00:00Z",
        "published_before": "2026-09-08T00:00:00Z",
        "observed_after": "2026-09-07T00:00:00Z",
        "observed_before": "2026-09-10T00:00:00Z",
    }
    request = _question_request(filters=filters, answer_mode="evidence_only")
    assert request.filters == filters
    result = service.submit(request, access_partitions=("public",))
    assert result.state == "answered"
    assert [
        ref.version_id
        for statement in result.answer.statements
        for ref in statement.citations
    ] == ["version-tick-new"]
    excluded = service.submit(
        _question_request(
            request_id="excluded",
            filters={**filters, "authors": ["alice"]},
            answer_mode="evidence_only",
        ),
        access_partitions=("public",),
    )
    assert excluded.state == "no_evidence"


@pytest.mark.parametrize("field", ["as_of", "during_from", "during_to", "known_as_of"])
def test_unimplemented_temporal_intent_is_rejected_before_submission(tmp_path, field):
    db_path = tmp_path / "questions.db"
    _seed_corpus(db_path)
    service = QuestionService(db_path, PostSearchBackend(db_path))
    temporal = _question_request().temporal.to_dict()
    temporal[field] = "2026-09-01T00:00:00Z"
    request = _question_request(temporal=temporal)
    with pytest.raises(
        contracts.QuestionContractError, match="unsupported_temporal_intent"
    ):
        service.submit(request, access_partitions=("public",))


def test_public_question_round_trip_is_profile_scoped_and_revision_exact(tmp_path):
    from lib.service_question_application import (
        QuestionApplication,
        QuestionUnavailableError,
    )

    db_path = tmp_path / "questions.db"
    _seed_corpus(db_path)
    app = QuestionApplication(
        db_path,
        PostSearchBackend(db_path),
        access_partitions=lambda profile: ("public", f"profile:{profile}"),
    )
    request = _question_request(profile_id="alice", answer_mode="evidence_only")
    result = app.ask_question(request)
    assert result.state == "answered"
    assert app.question_status(result.question_id, profile_id="alice") == result
    assert app.ask_question(request) == result
    for question_id, profile_id in [
        (result.question_id, "bob"),
        ("question-missing", "alice"),
    ]:
        with pytest.raises(QuestionUnavailableError, match="^question unavailable$"):
            app.question_status(question_id, profile_id=profile_id)
    refs = [
        ref.to_dict()
        for statement in result.answer.statements
        for ref in statement.citations
    ]
    read = app.read_evidence(
        contracts.EvidenceReadRequestV1.from_dict(
            {
                "schema_version": 1,
                "request_id": "read",
                "profile_id": "alice",
                "refs": refs,
                "max_response_bytes": 16384,
            }
        )
    )
    assert [item.status for item in read.items] == ["available", "available"]
    assert {item.ref.version_id for item in read.items} == {
        "version-legacy-current",
        "version-temporal-public",
    }


@pytest.mark.parametrize(
    "fallback,expected", [("none", "model_unavailable"), ("evidence_only", "answered")]
)
def test_unconfigured_model_finishes_only_the_requested_question(
    tmp_path, fallback, expected
):
    from lib.service_question_application import QuestionApplication

    db_path = tmp_path / "questions.db"
    _seed_corpus(db_path)
    backend = PostSearchBackend(db_path)
    other = QuestionService(db_path, backend)
    pending = other.submit(
        _question_request(request_id="other", profile_id="other"),
        access_partitions=("public",),
    )
    app = QuestionApplication(db_path, backend, access_partitions=lambda _: ("public",))
    result = app.ask_question(
        _question_request(request_id="selected", model_fallback=fallback)
    )
    assert result.state == expected
    assert result.error.code == "model_unavailable"
    assert result.attempt_count == 1
    assert result.error.retryable is False
    assert app.question_status(result.question_id, profile_id="public") == result
    assert other.status(pending.question_id).state == "pending"
    if result.answer:
        assert result.answer.model_invoked is False
        assert result.answer.evidence_only_fallback is True
        assert result.answer.acquisition_performed is False


def test_public_request_ids_are_scoped_to_profile_and_revoked_status_is_hidden(
    tmp_path,
):
    from lib.service_question_application import (
        QuestionApplication,
        QuestionUnavailableError,
    )
    from lib.service_questions import QuestionRequestConflict

    db_path = tmp_path / "questions.db"
    _seed_corpus(db_path)
    scopes = {"alice": ("public", "profile:alice"), "bob": ("public", "profile:bob")}
    app = QuestionApplication(
        db_path, PostSearchBackend(db_path), access_partitions=scopes.__getitem__
    )
    alice = app.ask_question(
        _question_request(profile_id="alice", answer_mode="evidence_only")
    )
    bob = app.ask_question(
        _question_request(profile_id="bob", answer_mode="evidence_only")
    )
    assert alice.question_id != bob.question_id
    with pytest.raises(QuestionRequestConflict):
        app.ask_question(
            _question_request(
                profile_id="alice", question="changed", answer_mode="evidence_only"
            )
        )
    scopes["alice"] = ("public",)
    with pytest.raises(QuestionUnavailableError, match="^question unavailable$"):
        app.question_status(alice.question_id, profile_id="alice")


def test_injected_worker_pending_reads_and_shutdown_are_bounded(tmp_path):
    from lib.service_question_application import (
        QuestionApplication,
        QuestionRuntimeUnavailableError,
    )
    from lib.service_questions import QuestionWorkerError

    class PausedWorker:
        worker_ref = "paused-provider-free-worker"

        def __init__(self):
            self.entered = threading.Event()
            self.release = threading.Event()

        def answer(self, payload):
            self.entered.set()
            assert self.release.wait(5)
            raise QuestionWorkerError(
                "model_unavailable", "fixture unavailable", retryable=False
            )

    db_path = tmp_path / "questions.db"
    _seed_corpus(db_path)
    worker = PausedWorker()
    app = QuestionApplication(
        db_path,
        PostSearchBackend(db_path),
        access_partitions=lambda _: ("public",),
        worker=worker,
    )
    with pytest.raises(QuestionRuntimeUnavailableError):
        app.ask_question(_question_request())
    app.start()
    try:
        limits = {**_question_request().limits.to_dict(), "wait_ms": 20}
        started = time.monotonic()
        pending = app.ask_question(_question_request(limits=limits))
        assert time.monotonic() - started < 1
        assert pending.state in {"pending", "running"}
        assert worker.entered.wait(1)
        before = app.question_status(pending.question_id, profile_id="public")
        assert app.question_status(pending.question_id, profile_id="public") == before
        assert app.stop(timeout=0.01) is False
    finally:
        worker.release.set()
        assert app.stop(timeout=2) is True
    terminal = app.question_status(pending.question_id, profile_id="public")
    assert terminal.state == "model_unavailable"
    assert terminal.attempt_count == 1


def test_unicode_worker_answer_over_transport_budget_is_durably_rejected(tmp_path):
    from lib.service_question_application import QuestionApplication

    class OversizedWorker:
        worker_ref = "unicode-fixture"

        def answer(self, payload):
            return {
                "answer_state": "answered",
                "summary": "s",
                "uncertainty_codes": [],
                "statements": [
                    {
                        "text": "😀" * 8190 + str(index),
                        "statement_kind": "source_fact",
                        "support_state": "supported",
                        "citation_ids": payload["allowed_citation_ids"][:1],
                        "alternatives": [],
                    }
                    for index in range(4)
                ],
            }

    db_path = tmp_path / "questions.db"
    _seed_corpus(db_path)
    app = QuestionApplication(
        db_path,
        PostSearchBackend(db_path),
        access_partitions=lambda _: ("public",),
        worker=OversizedWorker(),
    )
    app.start()
    try:
        result = app.ask_question(
            _question_request(
                limits={
                    **_question_request().limits.to_dict(),
                    "max_answer_characters": 32768,
                    "wait_ms": 1000,
                }
            )
        )
        assert result.state == "insufficient_evidence"
        assert result.error.code == "answer_too_large"
        assert result.error.retryable is False
        assert result.answer.statements == ()
        assert len(contracts.canonical_json(result.to_dict()).encode()) <= 131072
        assert app.question_status(result.question_id, profile_id="public") == result
    finally:
        assert app.stop(timeout=2)


@pytest.mark.parametrize(
    "filters,expected",
    [({"authors": ["missing"]}, "no_evidence"), ({}, "insufficient_evidence")],
)
def test_minimum_answer_budget_stays_durable_without_losing_empty_semantics(
    tmp_path, filters, expected
):
    from lib.service_question_application import QuestionApplication

    db_path = tmp_path / "questions.db"
    _seed_corpus(db_path)
    app = QuestionApplication(
        db_path, PostSearchBackend(db_path), access_partitions=lambda _: ("public",)
    )
    result = app.ask_question(
        _question_request(
            filters=filters,
            answer_mode="evidence_only",
            limits={**_question_request().limits.to_dict(), "max_answer_characters": 1},
        )
    )
    assert result.state == expected
    assert (
        len(result.answer.summary)
        + sum(len(item.text) for item in result.answer.statements)
        <= 1
    )
    assert app.question_status(result.question_id, profile_id="public") == result


def test_cancelled_wait_does_not_cancel_or_retry_the_durable_task(tmp_path):
    from lib.service_question_application import QuestionApplication
    from lib.service_questions import QuestionWorkerError

    release = threading.Event()

    class Worker:
        worker_ref = "cancellation-fixture"

        def answer(self, payload):
            assert release.wait(5)
            raise QuestionWorkerError(
                "model_unavailable", "fixture unavailable", retryable=False
            )

    db = tmp_path / "questions.db"
    _seed_corpus(db)
    app = QuestionApplication(
        db,
        PostSearchBackend(db),
        access_partitions=lambda _: ("public",),
        worker=Worker(),
    )
    cancelled = threading.Event()
    cancelled.set()
    app.start()
    try:
        request = _question_request(
            limits={**_question_request().limits.to_dict(), "wait_ms": 30000}
        )
        started = time.monotonic()
        result = app.ask_question(request, wait_cancelled=cancelled)
        assert time.monotonic() - started < 1
        assert result.state in {"pending", "running"}
    finally:
        release.set()
        assert app.stop(timeout=2)
    # Cancellation is only a wait cancellation; it never rewrites the request
    # or grants a retry. An unclaimed task may remain pending at shutdown.
    status = app.question_status(result.question_id, profile_id="public")
    assert status.state in {"pending", "model_unavailable"}
    assert status.attempt_count <= 1


def test_evidence_only_overflow_has_a_readable_terminal_error_receipt(tmp_path):
    from lib.service_question_application import QuestionApplication

    from tests.test_service_questions import FakePostSearchBackend, _hit

    backend = FakePostSearchBackend(
        [
            _hit(
                f"version-{index}",
                text="😀" * 4094 + str(index),
                observed_at="2026-09-12T00:00:00Z",
            )
            for index in range(8)
        ]
    )
    app = QuestionApplication(
        tmp_path / "questions.db", backend, access_partitions=lambda _: ("public",)
    )
    request = _question_request(
        answer_mode="evidence_only",
        limits={
            **_question_request().limits.to_dict(),
            "max_answer_characters": 32768,
            "max_evidence_bytes": 1048576,
        },
    )
    result = app.ask_question(request)
    assert result.state == "insufficient_evidence"
    assert result.error.code == "answer_too_large"
    assert result.answer.error == result.error
    assert result.attempt_count == 0
    assert app.question_status(result.question_id, profile_id="public") == result
