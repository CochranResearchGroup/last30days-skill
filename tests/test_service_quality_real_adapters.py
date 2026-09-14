"""Provider-free read-only adapter tests for service quality Packet 2."""

from __future__ import annotations

import hashlib
import json
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

from dev.last30days.quality import (
    ContractValidationError,
    EvaluationCaseV1,
    EvidenceHeadV1,
    QualityEvaluationRequestV1,
    QualityEvaluationSetV1,
    QualityRunnerV1,
    QualityThresholdPolicyV1,
    real_fixture_adapters,
    render_report_json,
)
from dev.last30days.quality.adapters import (
    AcquisitionCoverageAdapter,
    CorpusIntegrityAdapter,
    FixtureCatalog,
    PostSearchQualityAdapter,
    QuestionGroundingAdapter,
)
from lib import service_question_contracts as question_contracts
from lib.service_post_search import PostSearchBackend
from lib.service_questions import QuestionRunner, QuestionService
from tests.test_service_post_search import _seed_post_corpus


def _digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _json_digest(value: object) -> str:
    encoded = json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode()
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def _candidate() -> dict[str, object]:
    return {
        "repository_commit": "1" * 40,
        "service_contract_version": "fixture-v2",
        "database_schema_version": 0,
        "index_head": "index:fixture-v2",
        "embedding_config_digest": "sha256:" + "2" * 64,
        "ranking_config_digest": "sha256:" + "3" * 64,
    }


def _pin_fixture_contents(conn: sqlite3.Connection) -> None:
    triggers = conn.execute(
        "SELECT name, sql FROM sqlite_master WHERE type='trigger' "
        "AND tbl_name IN ('document_versions','service_source_versions')"
    ).fetchall()
    for name, _ in triggers:
        conn.execute(f'DROP TRIGGER "{name}"')
    conn.row_factory = sqlite3.Row
    for row in conn.execute(
        "SELECT v.version_id, d.source_native_id, d.canonical_url, v.title, "
        "v.normalized_text, v.author, v.published_at, v.source_metadata_json, "
        "v.media_json FROM document_versions v "
        "JOIN documents d ON d.document_id=v.document_id"
    ).fetchall():
        payload = {
            "source_native_id": row["source_native_id"],
            "url": row["canonical_url"],
            "title": row["title"],
            "text": row["normalized_text"],
            "author": row["author"],
            "published_at": row["published_at"],
            "metadata": json.loads(row["source_metadata_json"]),
        }
        media = json.loads(row["media_json"])
        if media:
            payload["media"] = media
        conn.execute(
            "UPDATE document_versions SET content_hash=? WHERE version_id=?",
            (_json_digest(payload), row["version_id"]),
        )
    for row in conn.execute(
        "SELECT v.version_id, v.title, v.normalized_text, v.author, "
        "v.published_at, v.metadata_json FROM service_source_versions v"
    ).fetchall():
        metadata = json.loads(row["metadata_json"])
        media = metadata.pop("media", [])
        payload = {
            "title": row["title"],
            "text": row["normalized_text"],
            "author": row["author"],
            "published_at": row["published_at"],
            "metadata": metadata,
            "media": media,
        }
        conn.execute(
            "UPDATE service_source_versions SET content_hash=? WHERE version_id=?",
            (_json_digest(payload), row["version_id"]),
        )
    for _, sql in triggers:
        conn.execute(sql)
    conn.execute(
        "CREATE TABLE quality_fixture_metadata "
        "(key TEXT PRIMARY KEY, value TEXT NOT NULL)"
    )
    conn.executemany(
        "INSERT INTO quality_fixture_metadata VALUES (?, ?)",
        [(key, str(value)) for key, value in _candidate().items()],
    )
    conn.commit()
    conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    conn.execute("PRAGMA journal_mode=DELETE")


def _case(axis: str, fixture: Path, **adapter_input: object) -> EvaluationCaseV1:
    return EvaluationCaseV1.from_dict(
        {
            "case_id": f"{axis}-fixture",
            "axis": axis,
            "tags": ["provider-free", "synthetic"],
            "fixture": {"fixture_id": "sealed-corpus", "digest": _digest(fixture)},
            "adapter_input": adapter_input,
        },
        "case",
    )


def _sealed_corpus(tmp_path: Path, *, partial: bool = True) -> Path:
    db_path = tmp_path / "quality-fixture.sqlite"
    _seed_post_corpus(db_path)
    with sqlite3.connect(db_path) as conn:
        _pin_fixture_contents(conn)
        conn.executemany(
            "INSERT INTO service_query_coverage VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                ("fixture", "reliable browser agents", "reddit", "succeeded", "2026-09-10T00:00:00Z", "2026-09-20T00:00:00Z", None, "job-1", "index-fixture", None, "2026-09-10T00:00:00Z"),
                ("fixture", "reliable browser agents", "x", "partial" if partial else "succeeded", "2026-09-10T00:00:00Z", "2026-09-20T00:00:00Z", None, "job-2", "index-fixture", "truncated" if partial else None, "2026-09-10T00:00:00Z"),
            ],
        )
    return db_path


def _question_request(
    *,
    request_id: str,
    answer_mode: str = "evidence_only",
    question: str = "reliable browser agents",
    limits: dict[str, object] | None = None,
):
    payload = {
            "schema_version": 1,
            "request_id": request_id,
            "profile_id": "public",
            "question": question,
            "filters": {},
            "temporal": {
                "as_of": None,
                "during_from": None,
                "during_to": None,
                "known_as_of": None,
            },
            "answer_mode": answer_mode,
            "model_fallback": "none",
            "limits": {
                "evidence_limit": 10,
                "max_evidence_bytes": 65536,
                "max_answer_characters": 4096,
                "max_statements": 8,
                "wait_ms": 0,
                "max_evidence_age_seconds": None,
                "max_attempts": 2,
            },
        }
    if limits:
        payload["limits"].update(limits)
    return question_contracts.QuestionRequestV1.from_dict(payload)


def _grounded_fixture(tmp_path: Path):
    db_path = _sealed_corpus(tmp_path, partial=False)
    clock = lambda: datetime(2026, 9, 14, tzinfo=timezone.utc)
    service = QuestionService(db_path, PostSearchBackend(db_path), clock=clock)
    supported = service.submit(
        _question_request(request_id="grounding-supported"),
        access_partitions=("public",),
    )
    no_evidence = service.submit(
        _question_request(
            request_id="grounding-empty", question="unmatched grounded fixture"
        ),
        access_partitions=("public",),
    )
    pending = service.submit(
        _question_request(request_id="grounding-conflict", answer_mode="synthesized"),
        access_partitions=("public",),
    )

    class ConflictWorker:
        worker_ref = "provider-free-conflict-fixture"

        def answer(self, payload):
            return {
                "answer_state": "conflicting_evidence",
                "summary": "The sealed evidence has two structural sources.",
                "statements": [
                    {
                        "text": "The retained fixture preserves both sources.",
                        "statement_kind": "source_fact",
                        "support_state": "mixed",
                        "citation_ids": payload["allowed_citation_ids"],
                        "alternatives": ["legacy", "temporal"],
                    }
                ],
                "uncertainty_codes": ["conflicting_evidence"],
            }

    conflicting = QuestionRunner(service.queue, ConflictWorker(), clock=clock).run_once(
        worker_id="grounding-fixture"
    )
    partial_stale = service.submit(
        _question_request(
            request_id="grounding-partial-stale",
            limits={"max_evidence_bytes": 1024, "max_evidence_age_seconds": 1},
        ),
        access_partitions=("public",),
    )
    assert (
        supported.answer is not None
        and no_evidence.answer is not None
        and conflicting is not None
        and conflicting.answer is not None
        and partial_stale.answer is not None
    )
    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        conn.execute("PRAGMA journal_mode=DELETE")
    return db_path, {
        "supported": supported,
        "no_evidence": no_evidence,
        "conflicting": conflicting,
        "partial_stale": partial_stale,
    }


def _grounding_case(db_path: Path, status) -> EvaluationCaseV1:
    assert status.answer is not None
    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            "SELECT retrieval_json FROM service_question_retrievals "
            "WHERE question_id=?",
            (status.question_id,),
        ).fetchone()
    assert row is not None
    citations = [item["evidence_id"] for item in json.loads(row[0])["evidence"]]
    return _case(
        "grounding",
        db_path,
        question_id=status.question_id,
        profile_id="public",
        access_partitions=["public"],
        expected_answer_id=status.answer.answer_id,
        expected_answer_state=status.answer.answer_state,
        expected_evidence_ids=citations,
        expected_uncertainty_codes=list(status.answer.uncertainty_codes),
    )


def test_real_grounding_adapter_reads_durable_question_answers_without_effects(tmp_path):
    db_path, statuses = _grounded_fixture(tmp_path)
    adapter = QuestionGroundingAdapter(FixtureCatalog({"sealed-corpus": db_path}))
    before = db_path.read_bytes()

    outcomes = {
        name: adapter.evaluate(_grounding_case(db_path, status), result_limit=20)
        for name, status in statuses.items()
    }

    assert statuses["supported"].answer.answer_state == "answered"
    assert statuses["no_evidence"].answer.answer_state == "no_evidence"
    assert statuses["conflicting"].answer.answer_state == "conflicting_evidence"
    assert statuses["partial_stale"].answer.coverage == {"partial": True, "stale": True}
    assert {
        citation.storage_family
        for statement in statuses["supported"].answer.statements
        for citation in statement.citations
    } == {"legacy", "temporal"}
    assert all(outcome.state == "passed" for outcome in outcomes.values())
    assert db_path.read_bytes() == before


def test_grounding_resolves_reused_citations_per_occurrence(tmp_path):
    db_path = _sealed_corpus(tmp_path, partial=False)
    clock = lambda: datetime(2026, 9, 14, tzinfo=timezone.utc)
    service = QuestionService(db_path, PostSearchBackend(db_path), clock=clock)
    service.submit(
        _question_request(
            request_id="grounding-reused-citation",
            answer_mode="synthesized",
            question="browser agents reliable",
        ),
        access_partitions=("public",),
    )

    class ReusedCitationWorker:
        worker_ref = "provider-free-reused-citation-fixture"

        def answer(self, payload):
            citation_id = payload["allowed_citation_ids"][0]
            return {
                "answer_state": "answered",
                "summary": "Two statements reuse one exact citation.",
                "statements": [
                    {
                        "text": text,
                        "statement_kind": "source_fact",
                        "support_state": "supported",
                        "citation_ids": [citation_id],
                        "alternatives": [],
                    }
                    for text in ("First supported statement.", "Second supported statement.")
                ],
                "uncertainty_codes": [],
            }

    status = QuestionRunner(
        service.queue, ReusedCitationWorker(), clock=clock
    ).run_once(worker_id="grounding-fixture")
    assert status is not None and status.answer is not None
    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        conn.execute("PRAGMA journal_mode=DELETE")
    outcome = QuestionGroundingAdapter(
        FixtureCatalog({"sealed-corpus": db_path})
    ).evaluate(_grounding_case(db_path, status), result_limit=20)
    dereference = next(
        metric for metric in outcome.metrics if metric.name == "citation_dereference"
    )
    assert outcome.state == "passed"
    assert (dereference.numerator, dereference.denominator) == (2, 2)


def test_grounding_resolves_more_than_twenty_distinct_citations_in_batches(tmp_path):
    db_path = _sealed_corpus(tmp_path, partial=False)
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        document = dict(
            conn.execute(
                "SELECT * FROM documents WHERE document_id='doc-legacy'"
            ).fetchone()
        )
        version = dict(
            conn.execute(
                "SELECT * FROM document_versions "
                "WHERE version_id='version-legacy-current'"
            ).fetchone()
        )
        for index in range(21):
            document_id = f"extra-{index}"
            version_id = f"version-extra-{index}"
            url = f"https://example.invalid/{index}"
            cloned_document = {
                **document,
                "document_id": document_id,
                "source_native_id": document_id,
                "canonical_url": url,
                "current_version_id": version_id,
            }
            metadata = json.loads(version["source_metadata_json"])
            content = {
                "source_native_id": document_id,
                "url": url,
                "title": version["title"],
                "text": version["normalized_text"],
                "author": version["author"],
                "published_at": version["published_at"],
                "metadata": metadata,
            }
            media = json.loads(version["media_json"])
            if media:
                content["media"] = media
            cloned_version = {
                **version,
                "document_id": document_id,
                "version_id": version_id,
                "content_hash": _json_digest(content),
            }
            conn.execute(
                f"INSERT INTO documents ({','.join(cloned_document)}) "
                f"VALUES ({','.join('?' for _ in cloned_document)})",
                tuple(cloned_document.values()),
            )
            conn.execute(
                f"INSERT INTO document_versions ({','.join(cloned_version)}) "
                f"VALUES ({','.join('?' for _ in cloned_version)})",
                tuple(cloned_version.values()),
            )
    clock = lambda: datetime(2026, 9, 14, tzinfo=timezone.utc)
    service = QuestionService(db_path, PostSearchBackend(db_path), clock=clock)
    status = service.submit(
        _question_request(
            request_id="grounding-many-citations",
            limits={
                "evidence_limit": 50,
                "max_statements": 50,
                "max_answer_characters": 16000,
            },
        ),
        access_partitions=("public",),
    )
    assert status.answer is not None
    citations = tuple(
        citation
        for statement in status.answer.statements
        for citation in statement.citations
    )
    assert len({citation.evidence_id for citation in citations}) == 23
    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        conn.execute("PRAGMA journal_mode=DELETE")
    outcome = QuestionGroundingAdapter(
        FixtureCatalog({"sealed-corpus": db_path})
    ).evaluate(_grounding_case(db_path, status), result_limit=50)
    assert outcome.state == "passed"


@pytest.mark.parametrize(
    ("table", "column"),
    [
        ("service_question_requests", "request_digest"),
        ("service_question_retrievals", "retrieval_digest"),
        ("service_question_answers", "output_digest"),
        ("service_question_tasks", "answer_id"),
    ],
)
def test_grounding_rejects_corrupt_durable_scalar_receipts(tmp_path, table, column):
    db_path, statuses = _grounded_fixture(tmp_path)
    status = statuses["supported"]
    with sqlite3.connect(db_path) as conn:
        triggers = conn.execute(
            "SELECT name, sql FROM sqlite_master WHERE type='trigger' AND tbl_name=?",
            (table,),
        ).fetchall()
        for name, _ in triggers:
            conn.execute(f'DROP TRIGGER "{name}"')
        key = "question_id" if table != "service_question_requests" else "request_id"
        identity = (
            status.question_id
            if key == "question_id"
            else json.loads(
                conn.execute(
                    "SELECT request_json FROM service_question_requests "
                    "JOIN service_question_retrievals USING (request_id) "
                    "WHERE question_id=?",
                    (status.question_id,),
                ).fetchone()[0]
            )["request_id"]
        )
        conn.execute(
            f"UPDATE {table} SET {column}=? WHERE {key}=?",
            ("sha256:corrupt", identity),
        )
        for _, sql in triggers:
            conn.execute(sql)
    outcome = QuestionGroundingAdapter(
        FixtureCatalog({"sealed-corpus": db_path})
    ).evaluate(_grounding_case(db_path, status), result_limit=20)
    correlation = next(
        metric for metric in outcome.metrics if metric.name == "answer_correlation"
    )
    assert outcome.state == "failed"
    assert correlation.numerator == 0


def test_grounding_adapter_rejects_tampered_citations_and_unlabeled_coverage(tmp_path):
    db_path, statuses = _grounded_fixture(tmp_path)
    supported = statuses["supported"]
    partial_stale = statuses["partial_stale"]
    assert supported.answer is not None and partial_stale.answer is not None
    with sqlite3.connect(db_path) as conn:
        triggers = conn.execute(
            "SELECT name, sql FROM sqlite_master WHERE type='trigger' "
            "AND tbl_name='service_question_answers'"
        ).fetchall()
        for name, _ in triggers:
            conn.execute(f'DROP TRIGGER "{name}"')
        answer = supported.answer
        statement = answer.statements[0]
        changed = question_contracts.QuestionCitationV1.from_dict(
            {**statement.citations[0].to_dict(), "content_hash": "sha256:changed"}
        )
        rewritten_statement = question_contracts.AnswerStatementV1.create(
            text=statement.text,
            statement_kind=statement.statement_kind,
            support_state=statement.support_state,
            citations=(changed,),
            alternatives=statement.alternatives,
        )
        values = answer.to_dict()
        for key in ("schema_version", "answer_id", "output_digest", "cache_only", "acquisition_performed"):
            values.pop(key)
        rewritten = question_contracts.QuestionAnswerV1.create(
            **{**values, "statements": (rewritten_statement,), "input_digest": "tampered-input"}
        )
        conn.execute(
            "UPDATE service_question_answers SET answer_json=?, output_digest=? WHERE answer_id=?",
            (question_contracts.canonical_json(rewritten.to_dict()), rewritten.output_digest, answer.answer_id),
        )
        answer = partial_stale.answer
        values = answer.to_dict()
        for key in ("schema_version", "answer_id", "output_digest", "cache_only", "acquisition_performed"):
            values.pop(key)
        unlabeled = question_contracts.QuestionAnswerV1.create(
            **{
                **values,
                "statements": answer.statements,
                "uncertainty_codes": (),
            }
        )
        conn.execute(
            "UPDATE service_question_answers SET answer_json=?, output_digest=? WHERE answer_id=?",
            (question_contracts.canonical_json(unlabeled.to_dict()), unlabeled.output_digest, answer.answer_id),
        )
        for _, sql in triggers:
            conn.execute(sql)
    adapter = QuestionGroundingAdapter(FixtureCatalog({"sealed-corpus": db_path}))
    tampered = adapter.evaluate(_grounding_case(db_path, supported), result_limit=20)
    unlabeled = adapter.evaluate(_grounding_case(db_path, partial_stale), result_limit=20)
    leaked_case = _grounding_case(db_path, statuses["conflicting"])
    leaked = adapter.evaluate(
        EvaluationCaseV1.from_dict(
            {
                **leaked_case.to_dict(),
                "adapter_input": {
                    **leaked_case.adapter_input,
                    "access_partitions": ["private"],
                },
            },
            "leaked_case",
        ),
        result_limit=20,
    )
    with sqlite3.connect(db_path) as conn:
        triggers = conn.execute(
            "SELECT name, sql FROM sqlite_master WHERE type='trigger' "
            "AND tbl_name='service_question_answers'"
        ).fetchall()
        for name, _ in triggers:
            conn.execute(f'DROP TRIGGER \"{name}\"')
        conn.execute(
            "UPDATE service_question_answers SET answer_json=? WHERE answer_id=?",
            ('{"schema_version":1}', statuses["no_evidence"].answer.answer_id),
        )
        for _, sql in triggers:
            conn.execute(sql)
    malformed = adapter.evaluate(
        _grounding_case(db_path, statuses["no_evidence"]), result_limit=20
    )
    unknown_partitions_case = EvaluationCaseV1.from_dict(
        {
            **_grounding_case(db_path, statuses["conflicting"]).to_dict(),
            "adapter_input": {
                **_grounding_case(db_path, statuses["conflicting"]).adapter_input,
                "access_partitions": [],
            },
        },
        "unknown_partitions_case",
    )

    assert tampered.state == "failed"
    assert tampered.failure_codes == ("grounding_structure_failed",)
    assert next(metric for metric in tampered.metrics if metric.name == "citation_dereference").numerator == 0
    assert unlabeled.state == "failed"
    assert unlabeled.failure_codes == ("grounding_structure_failed",)
    assert leaked.state == "failed"
    assert leaked.failure_codes == ("grounding_structure_failed",)
    assert malformed.state == "incomplete"
    assert malformed.failure_codes == ("grounding_fixture_invalid",)
    with pytest.raises(ContractValidationError, match="access partitions"):
        adapter.evaluate(unknown_partitions_case, result_limit=20)


def test_real_adapters_are_read_only_digest_pinned_and_inspectable(tmp_path):
    db_path = _sealed_corpus(tmp_path)
    catalog = FixtureCatalog({"sealed-corpus": db_path})
    before = db_path.read_bytes()

    corpus = CorpusIntegrityAdapter(catalog).evaluate(
        _case("corpus", db_path), result_limit=20
    )
    coverage = AcquisitionCoverageAdapter(catalog).evaluate(
        _case(
            "acquisition",
            db_path,
            profile_id="fixture",
            query="reliable browser agents",
            sources=["reddit", "x"],
            observed_at="2026-09-11T00:00:00Z",
        ),
        result_limit=20,
    )
    retrieval = PostSearchQualityAdapter(catalog).evaluate(
        _case(
            "retrieval",
            db_path,
            query="reliable browser agents",
            profile_id="fixture",
            access_partitions=["public"],
            expected_revision_ids=["version-legacy-current", "version-tick-public"],
            page_size=1,
            filters={},
        ),
        result_limit=20,
    )

    assert corpus.state == "passed"
    assert {metric.name for metric in corpus.metrics} == {
        "content_digest_validity",
        "canonical_identity_uniqueness",
        "current_revision_closure",
        "provenance_completeness",
        "access_partition_closure",
    }
    assert coverage.state == "failed"
    assert coverage.failure_codes == ("partial_coverage",)
    assert coverage.metrics[0].denominator == 2
    assert retrieval.state == "passed"
    assert {metric.name for metric in retrieval.metrics} == {
        "authorization_precision",
        "expected_revision_recall",
        "pagination_stability",
        "provenance_closure",
    }
    assert db_path.read_bytes() == before


def test_digest_mismatch_and_unknown_coverage_denominator_fail_closed(tmp_path):
    db_path = _sealed_corpus(tmp_path)
    catalog = FixtureCatalog({"sealed-corpus": db_path})
    digest_mismatch = EvaluationCaseV1.from_dict(
        {
            "case_id": "corpus-bad-digest",
            "axis": "corpus",
            "tags": ["provider-free"],
            "fixture": {"fixture_id": "sealed-corpus", "digest": "sha256:" + "0" * 64},
            "adapter_input": {},
        },
        "case",
    )
    unknown = _case(
        "acquisition",
        db_path,
        profile_id="fixture",
        query="reliable browser agents",
        sources=[],
        observed_at="2026-09-11T00:00:00Z",
    )

    bad_outcome = CorpusIntegrityAdapter(catalog).evaluate(digest_mismatch, result_limit=20)
    unknown_outcome = AcquisitionCoverageAdapter(catalog).evaluate(unknown, result_limit=20)

    assert bad_outcome.state == "incomplete"
    assert bad_outcome.failure_codes == ("fixture_digest_mismatch",)
    assert unknown_outcome.state == "not_measurable"
    assert unknown_outcome.metrics[0].denominator is None


def test_partition_mismatch_and_source_filter_remain_inspectable(tmp_path):
    db_path = _sealed_corpus(tmp_path, partial=False)
    filtered = PostSearchQualityAdapter(FixtureCatalog({"sealed-corpus": db_path})).evaluate(
        _case(
            "retrieval",
            db_path,
            query="reliable browser agents",
            profile_id="fixture",
            access_partitions=["public"],
            expected_revision_ids=["version-legacy-current"],
            page_size=20,
            filters={"sources": ["reddit"]},
        ),
        result_limit=20,
    )
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """INSERT INTO service_source_records (
                record_id, service_id, source, source_native_id, canonical_url,
                access_partition_id, current_version_id, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                "record-cross-partition",
                "x-service",
                "reddit",
                "cross-partition",
                "https://reddit.example/1",
                "profile:other",
                "version-tick-public",
                "2026-09-07T12:01:00Z",
            ),
        )
    corrupted = CorpusIntegrityAdapter(FixtureCatalog({"sealed-corpus": db_path})).evaluate(
        _case("corpus", db_path), result_limit=20
    )

    assert filtered.state == "passed"
    assert corrupted.state == "failed"
    assert corrupted.failure_codes == ("corpus_integrity_failed",)
    metrics = {metric.name: metric for metric in corrupted.metrics}
    assert metrics["canonical_identity_uniqueness"].numerator < metrics["canonical_identity_uniqueness"].denominator


def _real_payloads(db_path: Path, *, grounding_status=None):
    fixture = {"fixture_id": "sealed-corpus", "digest": _digest(db_path)}
    cases = [
        {"case_id": "acquisition-real", "axis": "acquisition", "tags": ["provider-free"], "fixture": fixture, "adapter_input": {"profile_id": "fixture", "query": "reliable browser agents", "sources": ["reddit", "x"], "observed_at": "2026-09-11T00:00:00Z"}},
        {"case_id": "corpus-real", "axis": "corpus", "tags": ["provider-free"], "fixture": fixture, "adapter_input": {}},
        {"case_id": "retrieval-real", "axis": "retrieval", "tags": ["provider-free"], "fixture": fixture, "adapter_input": {"query": "reliable browser agents", "profile_id": "fixture", "access_partitions": ["public"], "expected_revision_ids": ["version-legacy-current", "version-tick-public"], "page_size": 1, "filters": {}}},
    ]
    if grounding_status is not None:
        cases.append(_grounding_case(db_path, grounding_status).to_dict())
    cases.sort(key=lambda case: case["case_id"])
    evaluation = {
        "schema_version": "quality_evaluation_set.v1", "evaluation_set_id": "service-quality-real-v2",
        "version": 2, "description": "Synthetic sealed SQLite real-adapter cases.",
        "source_status": "synthetic", "source_licenses": [{"source": "reddit", "status": "synthetic", "license": "synthetic-no-third-party-content"}],
        "created_date": "2026-09-14", "reviewed_date": "2026-09-14", "cases": cases,
    }
    metrics = {
        "acquisition": ["coverage_rate"],
        "corpus": ["access_partition_closure", "canonical_identity_uniqueness", "content_digest_validity", "current_revision_closure", "provenance_completeness"],
        "retrieval": ["authorization_precision", "expected_revision_recall", "pagination_stability", "provenance_closure"],
        "grounding": ["answer_correlation", "citation_closure", "citation_dereference", "citation_partition_closure", "coverage_disclosure", "expected_answer_outcome", "provider_free_receipt"],
    }
    policy = {
        "schema_version": "quality_threshold_policy.v1", "policy_id": "service-quality-real-v2", "version": 2,
        "rules": sorted(
            [{"rule_id": f"{axis}-{metric}", "axis": axis, "metric": metric, "scope": "global", "comparator": "gte", "threshold": 1.0, "minimum_denominator": 1, "severity": "blocking", "missing_data": "not_measurable"} for axis, names in metrics.items() for metric in names],
            key=lambda rule: rule["rule_id"],
        ),
    }
    return evaluation, policy


def test_real_fixture_runner_and_cli_bind_adapter_and_fixture_digests(tmp_path):
    db_path, statuses = _grounded_fixture(tmp_path)
    evaluation_payload, policy_payload = _real_payloads(
        db_path, grounding_status=statuses["supported"]
    )
    evaluation = QualityEvaluationSetV1.from_dict(evaluation_payload)
    policy = QualityThresholdPolicyV1.from_dict(policy_payload)
    request_payload = {
        "schema_version": "quality_evaluation_request.v1", "run_id": "real-fixture-v2",
        "evaluation_set": {"id": evaluation.evaluation_set_id, "digest": evaluation.digest},
        "threshold_policy": {"id": policy.policy_id, "digest": policy.digest},
        "candidate": _candidate(),
        "baseline": None, "evaluator_version": "packet-2-v1", "axes": ["acquisition", "corpus", "retrieval", "grounding"], "case_ids": [],
        "mode": "provider_free_fixture", "environment": "fixture",
        "limits": {"max_cases": 20, "max_wall_seconds": 10, "max_output_bytes": 100000, "per_case_limit": 20},
    }
    request = QualityEvaluationRequestV1.from_dict(request_payload)
    report = QualityRunnerV1(real_fixture_adapters({"sealed-corpus": db_path}, candidate=request.candidate)).run(request, evaluation, policy)

    assert report.state == "passed"
    assert render_report_json(report) == render_report_json(report)
    artifacts = {artifact.role: artifact for artifact in report.artifacts}
    assert artifacts["sealed_fixture"].digest == _digest(db_path)
    assert artifacts["adapter_identity"].digest.startswith("sha256:")
    assert report.effect_receipt.network_requests == report.effect_receipt.model_calls == 0
    assert report.effect_receipt.browser_actions == report.effect_receipt.runtime_mutations == 0

    evaluation_path = tmp_path / "evaluation.json"
    policy_path = tmp_path / "policy.json"
    request_path = tmp_path / "request.json"
    for path, payload in ((evaluation_path, evaluation_payload), (policy_path, policy_payload), (request_path, request_payload)):
        path.write_text(json.dumps(payload), encoding="utf-8")
    command = [sys.executable, str(Path(__file__).parents[1] / "dev/last30days/scripts/evaluate_service_quality.py"), "--evaluation-set", str(evaluation_path), "--threshold-policy", str(policy_path), "--request", str(request_path), "--fixture", f"sealed-corpus={db_path}"]
    first = subprocess.run(command, capture_output=True, text=True, check=False)
    second = subprocess.run(command, capture_output=True, text=True, check=False)
    assert first.returncode == second.returncode == 0
    assert first.stdout == second.stdout


def test_corpus_integrity_recomputes_hashes_and_checks_version_owners(tmp_path):
    db_path = _sealed_corpus(tmp_path)
    with sqlite3.connect(db_path) as conn:
        trigger = conn.execute("SELECT sql FROM sqlite_master WHERE name='document_versions_no_update'").fetchone()[0]
        conn.execute("DROP TRIGGER document_versions_no_update")
        conn.execute("UPDATE document_versions SET content_hash='sha256:garbage' WHERE version_id='version-legacy-current'")
        conn.execute(trigger)
    outcome = CorpusIntegrityAdapter(FixtureCatalog({"sealed-corpus": db_path})).evaluate(_case("corpus", db_path), result_limit=20)
    assert outcome.state == "failed"
    assert next(metric for metric in outcome.metrics if metric.name == "content_digest_validity").numerator < 4

    owner_dir = tmp_path / "owner"
    owner_dir.mkdir()
    db_path = _sealed_corpus(owner_dir)
    with sqlite3.connect(db_path) as conn:
        trigger = conn.execute("SELECT sql FROM sqlite_master WHERE name='document_versions_no_update'").fetchone()[0]
        conn.execute("DROP TRIGGER document_versions_no_update")
        conn.execute("UPDATE document_versions SET document_id='absent-parent' WHERE version_id='version-legacy-current'")
        conn.execute(trigger)
    outcome = CorpusIntegrityAdapter(FixtureCatalog({"sealed-corpus": db_path})).evaluate(_case("corpus", db_path), result_limit=20)
    assert outcome.state == "failed"
    assert next(metric for metric in outcome.metrics if metric.name == "current_revision_closure").numerator < 6


def test_fixture_with_unpinned_wal_is_rejected(tmp_path):
    db_path = _sealed_corpus(tmp_path)
    writer = sqlite3.connect(db_path)
    try:
        writer.execute("PRAGMA journal_mode=WAL")
        writer.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        case = _case("corpus", db_path)
        writer.execute("CREATE TABLE unreviewed(value TEXT)")
        writer.commit()
        outcome = CorpusIntegrityAdapter(FixtureCatalog({"sealed-corpus": db_path})).evaluate(case, result_limit=20)
        assert outcome.state == "incomplete"
        assert outcome.failure_codes == ("fixture_not_sealed",)
    finally:
        writer.close()


def test_real_adapter_candidate_must_match_sealed_fixture_metadata(tmp_path):
    db_path = _sealed_corpus(tmp_path, partial=False)
    evaluation_payload, policy_payload = _real_payloads(db_path)
    wrong = EvidenceHeadV1.from_dict({**_candidate(), "index_head": "index:does-not-exist"}, "candidate")
    request_payload = {
        "schema_version": "quality_evaluation_request.v1", "run_id": "wrong-head",
        "evaluation_set": {"id": evaluation_payload["evaluation_set_id"], "digest": QualityEvaluationSetV1.from_dict(evaluation_payload).digest},
        "threshold_policy": {"id": policy_payload["policy_id"], "digest": QualityThresholdPolicyV1.from_dict(policy_payload).digest},
        "candidate": wrong.to_dict(), "baseline": None, "evaluator_version": "packet-2-v1",
        "axes": ["retrieval"], "case_ids": [], "mode": "provider_free_fixture", "environment": "fixture",
        "limits": {"max_cases": 20, "max_wall_seconds": 10, "max_output_bytes": 100000, "per_case_limit": 20},
    }
    request = QualityEvaluationRequestV1.from_dict(request_payload)
    report = QualityRunnerV1(real_fixture_adapters({"sealed-corpus": db_path}, candidate=wrong)).run(
        request, QualityEvaluationSetV1.from_dict(evaluation_payload), QualityThresholdPolicyV1.from_dict(policy_payload)
    )
    assert report.state == "incomplete"
    assert report.blocking_decision == "do_not_pass"
    assert report.case_results[0].failure_codes == ("fixture_candidate_mismatch",)

    verified = EvidenceHeadV1.from_dict(_candidate(), "candidate")
    with pytest.raises(ContractValidationError, match="request.candidate"):
        QualityRunnerV1(
            real_fixture_adapters({"sealed-corpus": db_path}, candidate=verified)
        ).run(
            request,
            QualityEvaluationSetV1.from_dict(evaluation_payload),
            QualityThresholdPolicyV1.from_dict(policy_payload),
        )
