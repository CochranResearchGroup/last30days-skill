"""Provider-free read-only adapter tests for service quality Packet 2."""

from __future__ import annotations

import hashlib
import sqlite3
import json
import subprocess
import sys
from pathlib import Path

from dev.last30days.quality import (
    EvaluationCaseV1,
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
)
from tests.test_service_post_search import _seed_post_corpus


def _digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


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
        conn.executemany(
            "INSERT INTO service_query_coverage VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                ("fixture", "reliable browser agents", "reddit", "succeeded", "2026-09-10T00:00:00Z", "2026-09-20T00:00:00Z", None, "job-1", "index-fixture", None, "2026-09-10T00:00:00Z"),
                ("fixture", "reliable browser agents", "x", "partial" if partial else "succeeded", "2026-09-10T00:00:00Z", "2026-09-20T00:00:00Z", None, "job-2", "index-fixture", "truncated" if partial else None, "2026-09-10T00:00:00Z"),
            ],
        )
    return db_path


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


def _real_payloads(db_path: Path):
    fixture = {"fixture_id": "sealed-corpus", "digest": _digest(db_path)}
    cases = [
        {"case_id": "acquisition-real", "axis": "acquisition", "tags": ["provider-free"], "fixture": fixture, "adapter_input": {"profile_id": "fixture", "query": "reliable browser agents", "sources": ["reddit", "x"], "observed_at": "2026-09-11T00:00:00Z"}},
        {"case_id": "corpus-real", "axis": "corpus", "tags": ["provider-free"], "fixture": fixture, "adapter_input": {}},
        {"case_id": "retrieval-real", "axis": "retrieval", "tags": ["provider-free"], "fixture": fixture, "adapter_input": {"query": "reliable browser agents", "profile_id": "fixture", "access_partitions": ["public"], "expected_revision_ids": ["version-legacy-current", "version-tick-public"], "page_size": 1, "filters": {}}},
    ]
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
    }
    policy = {
        "schema_version": "quality_threshold_policy.v1", "policy_id": "service-quality-real-v2", "version": 2,
        "rules": [{"rule_id": f"{axis}-{metric}", "axis": axis, "metric": metric, "scope": "global", "comparator": "gte", "threshold": 1.0, "minimum_denominator": 1, "severity": "blocking", "missing_data": "not_measurable"} for axis, names in metrics.items() for metric in names],
    }
    return evaluation, policy


def test_real_fixture_runner_and_cli_bind_adapter_and_fixture_digests(tmp_path):
    db_path = _sealed_corpus(tmp_path, partial=False)
    evaluation_payload, policy_payload = _real_payloads(db_path)
    evaluation = QualityEvaluationSetV1.from_dict(evaluation_payload)
    policy = QualityThresholdPolicyV1.from_dict(policy_payload)
    request_payload = {
        "schema_version": "quality_evaluation_request.v1", "run_id": "real-fixture-v2",
        "evaluation_set": {"id": evaluation.evaluation_set_id, "digest": evaluation.digest},
        "threshold_policy": {"id": policy.policy_id, "digest": policy.digest},
        "candidate": {"repository_commit": "1" * 40, "service_contract_version": "fixture-v2", "database_schema_version": 0, "index_head": "index:fixture-v2", "embedding_config_digest": "sha256:" + "2" * 64, "ranking_config_digest": "sha256:" + "3" * 64},
        "baseline": None, "evaluator_version": "packet-2-v1", "axes": ["acquisition", "corpus", "retrieval"], "case_ids": [],
        "mode": "provider_free_fixture", "environment": "fixture",
        "limits": {"max_cases": 20, "max_wall_seconds": 10, "max_output_bytes": 100000, "per_case_limit": 20},
    }
    request = QualityEvaluationRequestV1.from_dict(request_payload)
    report = QualityRunnerV1(real_fixture_adapters({"sealed-corpus": db_path})).run(request, evaluation, policy)

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
