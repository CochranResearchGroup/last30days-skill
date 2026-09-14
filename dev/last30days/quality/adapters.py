"""Read-only, digest-pinned Packet 2 quality adapters.

These adapters only open synthetic SQLite fixtures in SQLite query-only mode.
They never initialize a service, publish an index, repair data, or make a
network/model/browser request.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Mapping, Sequence

from lib import service_contracts as service_contracts
from lib.service_post_search import PostSearchBackend

from .contracts import (
    ContractValidationError,
    EvaluationCaseV1,
    EvidenceHeadV1,
    FakeOutcomeV1,
    MetricInputV1,
)


def _digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _digest_json(value: object) -> str:
    encoded = json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def _stored_version_digest(row: sqlite3.Row) -> str | None:
    try:
        metadata = json.loads(row["metadata_json"])
        if not isinstance(metadata, dict):
            return None
        if row["family"] == "legacy":
            payload = {
                "source_native_id": row["source_native_id"],
                "url": row["canonical_url"],
                "title": row["title"],
                "text": row["normalized_text"],
                "author": row["author"],
                "published_at": row["published_at"],
                "metadata": metadata,
            }
            media = json.loads(row["media_json"])
            if not isinstance(media, list):
                return None
            if media:
                payload["media"] = media
        else:
            media = metadata.pop("media", [])
            if not isinstance(media, list):
                return None
            payload = {
                "title": row["title"],
                "text": row["normalized_text"],
                "author": row["author"],
                "published_at": row["published_at"],
                "metadata": metadata,
                "media": media,
            }
        return _digest_json(payload)
    except (TypeError, ValueError):
        return None


def _outcome(
    *,
    state: str,
    metrics: Sequence[MetricInputV1],
    failure_codes: Sequence[str] = (),
    observed_refs: Sequence[str],
) -> FakeOutcomeV1:
    return FakeOutcomeV1(
        state=state,
        metrics=tuple(sorted(metrics, key=lambda metric: metric.name)),
        baseline_metrics=None,
        failure_codes=tuple(sorted(set(failure_codes))),
        observed_refs=tuple(sorted(set(observed_refs))),
    )


class FixtureCatalog:
    """Maps reviewed fixture identities to local read-only files."""

    def __init__(
        self,
        fixtures: Mapping[str, Path],
        *,
        candidate: EvidenceHeadV1 | None = None,
    ) -> None:
        self._fixtures = {fixture_id: Path(path) for fixture_id, path in fixtures.items()}
        self._candidate = candidate

    def resolve(self, case: EvaluationCaseV1) -> Path:
        if case.fixture is None:
            raise ContractValidationError("real adapter requires a fixture reference")
        path = self._fixtures.get(case.fixture.fixture_id)
        if path is None:
            raise ContractValidationError("fixture is not registered")
        if not path.is_file():
            raise ContractValidationError("fixture is unavailable")
        if _digest(path) != case.fixture.digest:
            raise ContractValidationError("fixture_digest_mismatch")
        for suffix in ("-wal", "-journal"):
            companion = Path(str(path) + suffix)
            if companion.is_file() and companion.stat().st_size:
                raise ContractValidationError("fixture_not_sealed")
        if self._candidate is not None:
            try:
                with sqlite3.connect(
                    path.resolve().as_uri() + "?mode=ro&immutable=1", uri=True
                ) as conn:
                    rows = conn.execute(
                        "SELECT key, value FROM quality_fixture_metadata"
                    ).fetchall()
            except sqlite3.Error as exc:
                raise ContractValidationError("fixture_candidate_unverified") from exc
            metadata = {str(key): str(value) for key, value in rows}
            expected = {
                key: str(value) for key, value in self._candidate.to_dict().items()
            }
            if metadata != expected:
                raise ContractValidationError("fixture_candidate_mismatch")
        return path


class _ReadOnlyAdapter:
    axis: str

    def __init__(self, catalog: FixtureCatalog) -> None:
        self._catalog = catalog

    def _path(self, case: EvaluationCaseV1) -> tuple[Path | None, str | None]:
        if case.axis != self.axis:
            raise ContractValidationError("adapter received a case for another axis")
        try:
            return self._catalog.resolve(case), None
        except ContractValidationError as exc:
            if str(exc) in {
                "fixture_digest_mismatch",
                "fixture_not_sealed",
                "fixture_candidate_unverified",
                "fixture_candidate_mismatch",
            }:
                return None, str(exc)
            raise

    @staticmethod
    def _connect(path: Path) -> sqlite3.Connection:
        conn = sqlite3.connect(
            path.resolve().as_uri() + "?mode=ro&immutable=1", uri=True
        )
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA query_only=ON")
        return conn

    def _mismatch(self, case: EvaluationCaseV1, code: str) -> FakeOutcomeV1:
        return _outcome(
            state="incomplete",
            metrics=(),
            failure_codes=(code,),
            observed_refs=(f"fixture:{case.fixture.fixture_id}",),  # type: ignore[union-attr]
        )


class CorpusIntegrityAdapter(_ReadOnlyAdapter):
    axis = "corpus"

    def evaluate(self, case: EvaluationCaseV1, *, result_limit: int) -> FakeOutcomeV1:
        path, failure = self._path(case)
        if path is None:
            return self._mismatch(case, failure or "fixture_unavailable")
        try:
            with self._connect(path) as conn:
                versions = conn.execute(
                    "SELECT 'legacy' family, v.content_hash, d.source_native_id, "
                    "d.canonical_url, v.title, v.normalized_text, v.author, "
                    "v.published_at, v.source_metadata_json metadata_json, v.media_json "
                    "FROM document_versions v LEFT JOIN documents d "
                    "ON d.document_id=v.document_id "
                    "UNION ALL SELECT 'temporal' family, v.content_hash, r.source_native_id, "
                    "r.canonical_url, v.title, v.normalized_text, v.author, "
                    "v.published_at, v.metadata_json, NULL media_json "
                    "FROM service_source_versions v LEFT JOIN service_source_records r "
                    "ON r.record_id=v.record_id"
                ).fetchall()
                current = conn.execute(
                    "SELECT COUNT(*) FROM documents d JOIN document_versions v "
                    "ON v.version_id=d.current_version_id "
                    "AND v.document_id=d.document_id "
                    "UNION ALL SELECT COUNT(*) FROM service_source_records r "
                    "JOIN service_source_versions v ON v.version_id=r.current_version_id "
                    "AND v.record_id=r.record_id"
                ).fetchall()
                origins = conn.execute(
                    "SELECT source, canonical_url FROM documents "
                    "UNION ALL SELECT source, canonical_url FROM service_source_records"
                ).fetchall()
                partition_rows = conn.execute(
                    "SELECT d.access_partition_id origin_partition, v.access_partition_id version_partition "
                    "FROM document_versions v LEFT JOIN documents d "
                    "ON d.document_id=v.document_id "
                    "UNION ALL SELECT r.access_partition_id origin_partition, v.access_partition_id version_partition "
                    "FROM service_source_versions v LEFT JOIN service_source_records r "
                    "ON r.record_id=v.record_id"
                ).fetchall()
        except (sqlite3.Error, TypeError, ValueError):
            return _outcome(
                state="incomplete",
                metrics=(MetricInputV1("fixture_available", 0, 1, 0),),
                failure_codes=("corpus_fixture_invalid",),
                observed_refs=(f"fixture:{case.fixture.fixture_id}",),  # type: ignore[union-attr]
            )
        version_total = len(versions)
        origin_total = len(origins)
        digest_valid = 0
        owner_valid = 0
        for row in versions:
            if row["canonical_url"] is None:
                continue
            owner_valid += 1
            digest_valid += _stored_version_digest(row) == row["content_hash"]
        provenance_valid = sum(
            bool(row["source"]) and bool(row["canonical_url"]) for row in origins
        )
        unique_origins = len({(row["source"], row["canonical_url"]) for row in origins})
        current_valid = sum(int(row[0]) for row in current) + owner_valid
        partition_valid = sum(
            row["origin_partition"] == row["version_partition"] for row in partition_rows
        )
        metrics = (
            MetricInputV1("access_partition_closure", partition_valid, len(partition_rows) or None, 0),
            MetricInputV1("canonical_identity_uniqueness", unique_origins, origin_total or None, 0),
            MetricInputV1("content_digest_validity", digest_valid, version_total or None, 0),
            MetricInputV1(
                "current_revision_closure",
                current_valid,
                (origin_total + version_total) or None,
                0,
            ),
            MetricInputV1("provenance_completeness", provenance_valid, origin_total or None, 0),
        )
        passed = all(metric.denominator and metric.numerator == metric.denominator for metric in metrics)
        return _outcome(
            state="passed" if passed else "failed",
            metrics=metrics,
            failure_codes=() if passed else ("corpus_integrity_failed",),
            observed_refs=(f"fixture:{case.fixture.fixture_id}",),  # type: ignore[union-attr]
        )


class AcquisitionCoverageAdapter(_ReadOnlyAdapter):
    axis = "acquisition"

    def evaluate(self, case: EvaluationCaseV1, *, result_limit: int) -> FakeOutcomeV1:
        path, failure = self._path(case)
        if path is None:
            return self._mismatch(case, failure or "fixture_unavailable")
        values = case.adapter_input or {}
        sources = values.get("sources")
        if not isinstance(sources, list) or not sources:
            return _outcome(
                state="not_measurable",
                metrics=(MetricInputV1("coverage_rate", 0, None, 0),),
                failure_codes=("unknown_coverage_denominator",),
                observed_refs=(f"fixture:{case.fixture.fixture_id}",),  # type: ignore[union-attr]
            )
        if not all(isinstance(source, str) and source for source in sources):
            raise ContractValidationError("coverage sources must be non-empty strings")
        profile_id, query, observed_at = (
            values.get("profile_id"),
            values.get("query"),
            values.get("observed_at"),
        )
        if not all(isinstance(value, str) and value for value in (profile_id, query, observed_at)):
            raise ContractValidationError("coverage input is incomplete")
        placeholders = ",".join("?" for _ in sources)
        try:
            with self._connect(path) as conn:
                rows = conn.execute(
                    f"SELECT source, status, fresh_until FROM service_query_coverage "
                    f"WHERE profile_id=? AND normalized_query=? AND source IN ({placeholders})",
                    [profile_id, query, *sources],
                ).fetchall()
        except sqlite3.Error:
            return _outcome(
                state="incomplete",
                metrics=(MetricInputV1("coverage_rate", 0, len(sources), 0),),
                failure_codes=("coverage_fixture_invalid",),
                observed_refs=(f"fixture:{case.fixture.fixture_id}",),  # type: ignore[union-attr]
            )
        by_source = {row["source"]: row for row in rows}
        succeeded = sum(
            row is not None and row["status"] == "succeeded" and row["fresh_until"] >= observed_at
            for row in (by_source.get(source) for source in sources)
        )
        partial = any(row is not None and row["status"] == "partial" for row in by_source.values())
        stale = any(row is not None and row["fresh_until"] < observed_at for row in by_source.values())
        complete = succeeded == len(sources)
        failures = [] if complete else ["partial_coverage" if partial else "coverage_incomplete"]
        if stale:
            failures.append("stale_coverage")
        return _outcome(
            state="passed" if complete else "failed",
            metrics=(MetricInputV1("coverage_rate", succeeded, len(sources), 0),),
            failure_codes=failures,
            observed_refs=(f"fixture:{case.fixture.fixture_id}",),  # type: ignore[union-attr]
        )


class PostSearchQualityAdapter(_ReadOnlyAdapter):
    axis = "retrieval"

    def evaluate(self, case: EvaluationCaseV1, *, result_limit: int) -> FakeOutcomeV1:
        path, failure = self._path(case)
        if path is None:
            return self._mismatch(case, failure or "fixture_unavailable")
        values = case.adapter_input or {}
        required = {"query", "profile_id", "access_partitions", "expected_revision_ids", "page_size", "filters"}
        if set(values) != required:
            raise ContractValidationError("post-search adapter input has unsupported fields")
        query, profile_id = values["query"], values["profile_id"]
        partitions, expected, page_size, filters = values["access_partitions"], values["expected_revision_ids"], values["page_size"], values["filters"]
        if not isinstance(query, str) or not isinstance(profile_id, str):
            raise ContractValidationError("post-search query and profile_id must be strings")
        if not isinstance(partitions, list) or not isinstance(expected, list) or not isinstance(page_size, int):
            raise ContractValidationError("post-search adapter input is invalid")
        if not isinstance(filters, dict):
            raise ContractValidationError("post-search filters must be an object")
        if not all(isinstance(item, str) and item for item in [*partitions, *expected]):
            raise ContractValidationError("post-search adapter identities must be strings")
        request = service_contracts.PostSearchRequest.from_dict(
            {
                "schema_version": 1,
                "request_id": f"quality-{case.case_id}",
                "query": query,
                "profile_id": profile_id,
                "page_size": page_size,
                "cursor": None,
                "filters": filters,
            }
        )
        try:
            backend = PostSearchBackend(path)
            first = backend.search(request, access_partitions=tuple(partitions))
            second = (
                backend.search(
                    service_contracts.PostSearchRequest.from_dict(
                        {**request.to_dict(), "cursor": first.next_cursor}
                    ),
                    access_partitions=tuple(partitions),
                )
                if first.next_cursor
                else None
            )
        except (sqlite3.Error, ValueError, service_contracts.ContractValidationError):
            return _outcome(
                state="incomplete",
                metrics=(MetricInputV1("expected_revision_recall", 0, len(expected) or None, 0),),
                failure_codes=("retrieval_fixture_invalid",),
                observed_refs=(f"fixture:{case.fixture.fixture_id}",),  # type: ignore[union-attr]
            )
        hits = [*first.hits, *(second.hits if second else ())]
        revisions = {hit.revision_id for hit in hits}
        expected_set = set(expected)
        authorization = sum(hit.access_partition_id in set(partitions) for hit in hits)
        provenance = sum(hit.evidence_ref.version_id == hit.revision_id for hit in hits)
        no_duplicates = len({hit.post_id for hit in hits}) == len(hits)
        metrics = (
            MetricInputV1("authorization_precision", authorization, len(hits) or None, 0),
            MetricInputV1("expected_revision_recall", len(revisions & expected_set), len(expected_set) or None, 0),
            MetricInputV1("pagination_stability", int(no_duplicates), 1, 0),
            MetricInputV1("provenance_closure", provenance, len(hits) or None, 0),
        )
        passed = all(metric.denominator and metric.numerator == metric.denominator for metric in metrics)
        return _outcome(
            state="passed" if passed else "failed",
            metrics=metrics,
            failure_codes=() if passed else ("retrieval_expectation_failed",),
            observed_refs=(f"fixture:{case.fixture.fixture_id}",),  # type: ignore[union-attr]
        )


def real_fixture_adapters(
    fixtures: Mapping[str, Path], *, candidate: EvidenceHeadV1
):
    """Return Packet 2 adapters while retaining the deferred fake grounding axis."""

    from .runner import default_fake_adapters

    catalog = FixtureCatalog(fixtures, candidate=candidate)
    adapters = default_fake_adapters()
    adapters.update(
        {
            "acquisition": AcquisitionCoverageAdapter(catalog),
            "corpus": CorpusIntegrityAdapter(catalog),
            "retrieval": PostSearchQualityAdapter(catalog),
        }
    )
    return adapters
