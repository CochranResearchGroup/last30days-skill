"""Behavioral tests for the cache-first intelligence application."""

import json
import sqlite3
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from lib import service_contracts as contracts
from lib.service_app import CacheQueryApplication
from lib.service_retrieval import HybridRetriever
from lib.service_store import ServiceStore


class FakeRetriever:
    def __init__(self, evidence):
        self.evidence = evidence
        self.calls = []

    def search_snapshot(
        self, query, *, sources=None, top_k=8, snippet_chars=320
    ):
        self.calls.append(
            {
                "query": query,
                "sources": sources,
                "top_k": top_k,
                "snippet_chars": snippet_chars,
            }
        )
        return SimpleNamespace(
            index_version="index-001",
            evidence=list(self.evidence[:top_k]),
        )


class FakeRefreshScheduler:
    def __init__(self):
        self.requests = []

    def ensure_refresh(self, request):
        self.requests.append(request)
        return f"job-{request.request_id}"

    def cache_status(self, request, fallback):
        del request
        return fallback


class FakeTickSnapshots:
    def __init__(self):
        self.calls = []

    def current_metadata(self):
        return {
            "snapshot_id": "tick-snapshot-001",
            "tick_id": "tick-001",
            "state": "promoted",
            "embedding_space": "local-hash-v1",
            "fusion_version": "rrf-v1",
            "completeness": {"youtube": "success", "facebook": "failure"},
            "coverage_gaps": ["facebook"],
            "interval_from": "2026-08-05T00:00:00Z",
            "interval_to": "2026-08-06T00:00:00Z",
            "promoted_at": "2026-08-06T12:00:00Z",
        }

    def query(self, query, **kwargs):
        self.calls.append({"query": query, **kwargs})
        return (
            SimpleNamespace(
                entry_id="version-youtube-001",
                source="youtube",
                access_partition_id="public",
                text="ChatGPT Voice launch thumbnail",
                matching_channels=(
                    "lexical_source",
                    "source_alt_text",
                    "ocr",
                    "semantic_sidecar",
                ),
                score=0.05,
                provenance={
                    "version_id": "version-youtube-001",
                    "source_native_id": "video-001",
                    "url": "https://youtube.test/watch?v=video-001",
                    "title": "ChatGPT Voice",
                    "published_at": "2026-08-06T10:00:00Z",
                    "matching_entries": {
                        "ocr": ["ocr-001"],
                        "semantic_sidecar": ["sidecar-001"],
                    },
                },
            ),
        )


def test_topic_actions_are_service_owned_and_refresh_is_durable(tmp_path):
    db_path = tmp_path / "research.db"
    ServiceStore(db_path).initialize()
    scheduler = FakeRefreshScheduler()
    app = CacheQueryApplication(
        db_path,
        FakeRetriever([]),
        refresh_scheduler=scheduler,
        clock=lambda: datetime(2026, 7, 24, 12, 0, tzinfo=timezone.utc),
    )

    created = app.topic(
        {
            "action": "create",
            "name": "Browser infrastructure",
            "search_queries": ["agent browser service"],
            "schedule": "0 8 * * *",
        }
    )
    topic_id = created["topics"][0]["topic_id"]
    paused = app.topic({"action": "pause", "topic_id": topic_id})
    resumed = app.topic({"action": "resume", "topic_id": topic_id})
    refreshed = app.topic(
        {"action": "request_refresh", "topic_id": topic_id, "sources": ["reddit"]}
    )

    assert paused["topics"][0]["enabled"] is False
    assert resumed["topics"][0]["enabled"] is True
    assert refreshed["job_id"].startswith("job-topic-")
    assert scheduler.requests[0].filters == {
        "topic_ids": [topic_id],
        "sources": ["reddit"],
    }
    assert app.topic({"action": "list"})["topics"][0]["name"] == (
        "Browser infrastructure"
    )


def _request(**overrides):
    values = {
        "schema_version": 1,
        "request_id": "query-refresh",
        "profile_id": "default",
        "query": "cached query",
        "freshness_policy": "prefer_cache",
        "response_mode": "evidence",
        "filters": {},
        "top_k": 8,
        "max_chars": 8192,
        "wait_ms": 0,
    }
    values.update(overrides)
    return contracts.QueryRequest.from_dict(values)


def test_ordinary_query_uses_promoted_tick_head_with_filter_first_provenance(
    tmp_path,
):
    db_path = tmp_path / "research.db"
    ServiceStore(db_path).initialize()
    legacy = FakeRetriever([])
    tick_snapshots = FakeTickSnapshots()
    app = CacheQueryApplication(
        db_path,
        legacy,
        tick_snapshots=tick_snapshots,
        clock=lambda: datetime(2026, 8, 6, 12, 5, tzinfo=timezone.utc),
    )

    response = app.query(
        _request(
            profile_id="last30days-facebook",
            query="ChatGPT Voice",
            filters={
                "sources": ["youtube"],
                "published_after": "2026-08-05T00:00:00Z",
                "published_before": "2026-08-07T00:00:00Z",
            },
        )
    )

    assert legacy.calls == []
    assert tick_snapshots.calls == [
        {
            "query": "ChatGPT Voice",
            "access_partitions": (
                "public",
                "profile:last30days-facebook",
            ),
            "sources": ["youtube"],
            "published_after": "2026-08-05T00:00:00Z",
            "published_before": "2026-08-07T00:00:00Z",
            "limit": 8,
        }
    ]
    assert response.index_version == "tick-snapshot-001"
    assert response.tick_snapshot == tick_snapshots.current_metadata()
    assert response.evidence[0].access_partition_id == "public"
    assert response.evidence[0].matching_channels == [
        "lexical_source",
        "source_alt_text",
        "ocr",
        "semantic_sidecar",
    ]
    assert response.evidence[0].provenance["matching_entries"] == {
        "ocr": ["ocr-001"],
        "semantic_sidecar": ["sidecar-001"],
    }


def test_warm_cache_query_returns_bounded_evidence_without_refresh(tmp_path):
    db_path = tmp_path / "research.db"
    ServiceStore(db_path).initialize()
    evidence = contracts.EvidenceItem.from_dict(
        {
            "schema_version": 1,
            "evidence_id": "ev-001",
            "document_id": "doc-001",
            "source": "reddit",
            "source_native_id": "post-001",
            "url": "https://reddit.com/r/test/1",
            "title": "Reliable browser acquisition",
            "snippet": "Cached evidence without browser or network mechanics.",
            "author": "author",
            "published_at": "2026-07-23T12:00:00Z",
            "fetched_at": "2026-07-24T11:30:00Z",
            "acquisition_id": "acq-001",
            "content_hash": "sha256:content",
            "scores": {
                "lexical": 0.8,
                "semantic": 0.7,
                "graph": 0.0,
                "recency": 0.95,
                "fused": 0.82,
            },
        }
    )
    retriever = FakeRetriever([evidence])
    app = CacheQueryApplication(
        db_path,
        retriever,
        clock=lambda: datetime(2026, 7, 24, 12, 0, tzinfo=timezone.utc),
    )
    request = contracts.QueryRequest.from_dict(
        {
            "schema_version": 1,
            "request_id": "query-001",
            "profile_id": "default",
            "query": "browser acquisition",
            "freshness_policy": "prefer_cache",
            "response_mode": "evidence",
            "filters": {"sources": ["reddit"]},
            "top_k": 8,
            "max_chars": 8192,
            "wait_ms": 0,
        }
    )

    response = app.query(request)

    assert response.cache_status is contracts.CacheStatus.FRESH
    assert response.job_id is None
    assert [item.evidence_id for item in response.evidence] == ["ev-001"]
    assert retriever.calls == [
        {
            "query": "browser acquisition",
            "sources": ["reddit"],
            "top_k": 8,
            "snippet_chars": 1024,
        }
    ]


def test_default_query_response_stays_within_agent_context_budget(tmp_path):
    db_path = tmp_path / "research.db"
    ServiceStore(db_path).initialize()
    evidence = []
    for index in range(20):
        evidence.append(
            contracts.EvidenceItem.from_dict(
                {
                    "schema_version": 1,
                    "evidence_id": f"ev-{index:03d}",
                    "document_id": f"doc-{index:03d}",
                    "source": "youtube",
                    "source_native_id": f"video-{index:03d}",
                    "url": f"https://youtube.example/watch/{index}",
                    "title": f"Evidence {index}",
                    "snippet": "bounded evidence " * 200,
                    "author": "channel",
                    "published_at": "2026-07-23T12:00:00Z",
                    "fetched_at": "2026-07-24T11:30:00Z",
                    "acquisition_id": f"acq-{index:03d}",
                    "content_hash": f"sha256:{index:064x}",
                    "scores": {
                        "lexical": 0.8,
                        "semantic": 0.7,
                        "graph": 0.0,
                        "recency": 0.95,
                        "fused": 0.82,
                    },
                }
            )
        )
    app = CacheQueryApplication(
        db_path,
        FakeRetriever(evidence),
        clock=lambda: datetime(2026, 7, 24, 12, 0, tzinfo=timezone.utc),
    )
    request = contracts.QueryRequest.from_dict(
        {
            "schema_version": 1,
            "request_id": "query-budget",
            "profile_id": "default",
            "query": "bounded response",
            "freshness_policy": "cache_only",
            "response_mode": "evidence",
            "filters": {},
            "top_k": 8,
            "max_chars": 8192,
            "wait_ms": 0,
        }
    )

    response = app.query(request)
    serialized = json.dumps(
        response.to_dict(),
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )

    assert len(response.evidence) <= 8
    assert len(serialized) <= 8192
    assert response.truncated is True


def test_brief_mode_returns_a_bounded_extract_with_evidence_ids(tmp_path):
    db_path = tmp_path / "research.db"
    ServiceStore(db_path).initialize()
    evidence = contracts.EvidenceItem.from_dict(
        {
            "schema_version": 1,
            "evidence_id": "ev-brief",
            "document_id": "doc-brief",
            "source": "reddit",
            "source_native_id": "post-brief",
            "url": "https://reddit.example/brief",
            "title": "Cached finding",
            "snippet": "An extractive brief remains available without a model.",
            "author": "author",
            "published_at": None,
            "fetched_at": "2026-07-24T11:30:00Z",
            "acquisition_id": "acq-brief",
            "content_hash": "sha256:brief",
            "scores": {
                "lexical": 1.0,
                "semantic": 0.0,
                "graph": 0.0,
                "recency": 1.0,
                "fused": 1.0,
            },
        }
    )
    app = CacheQueryApplication(
        db_path,
        FakeRetriever([evidence]),
        clock=lambda: datetime(2026, 7, 24, 12, 0, tzinfo=timezone.utc),
    )
    request = contracts.QueryRequest.from_dict(
        {
            "schema_version": 1,
            "request_id": "query-brief",
            "profile_id": "default",
            "query": "cached finding",
            "freshness_policy": "cache_only",
            "response_mode": "brief",
            "filters": {},
            "top_k": 8,
            "max_chars": 8192,
            "wait_ms": 0,
        }
    )

    response = app.query(request)

    assert response.brief is not None
    assert "[ev-brief]" in response.brief
    assert len(response.brief) <= 2048


def test_cache_miss_schedules_refresh_without_blocking_query(tmp_path):
    db_path = tmp_path / "research.db"
    ServiceStore(db_path).initialize()
    scheduler = FakeRefreshScheduler()
    app = CacheQueryApplication(
        db_path,
        FakeRetriever([]),
        refresh_scheduler=scheduler,
        clock=lambda: datetime(2026, 7, 24, 12, 0, tzinfo=timezone.utc),
    )
    request = _request()

    response = app.query(request)

    assert response.cache_status is contracts.CacheStatus.MISS
    assert response.job_id == "job-query-refresh"
    assert response.diagnostics_available is True
    assert scheduler.requests == [request]


def test_cache_only_never_schedules_refresh(tmp_path):
    db_path = tmp_path / "research.db"
    ServiceStore(db_path).initialize()
    scheduler = FakeRefreshScheduler()
    app = CacheQueryApplication(
        db_path,
        FakeRetriever([]),
        refresh_scheduler=scheduler,
        clock=lambda: datetime(2026, 7, 24, 12, 0, tzinfo=timezone.utc),
    )

    response = app.query(_request(freshness_policy="cache_only"))

    assert response.cache_status is contracts.CacheStatus.MISS
    assert response.job_id is None
    assert scheduler.requests == []


def test_service_discovery_reports_durable_acquisition_sources(tmp_path):
    db_path = tmp_path / "research.db"
    ServiceStore(db_path).initialize()
    app = CacheQueryApplication(
        db_path,
        FakeRetriever([]),
        refresh_scheduler=FakeRefreshScheduler(),
        acquisition_sources=("youtube", "x"),
        acquisition_readiness={"x": True, "youtube": False},
        recurring_collection=True,
        assessment_processing=True,
    )

    info = app.service_info()

    assert info.product == "last30days"
    assert info.service_api_version == 1
    assert info.contract_schema_version == contracts.SCHEMA_VERSION
    assert info.contract_sha256 == contracts.SCHEMA_CATALOG_SHA256
    assert info.runtime_manifest_sha256 is not None
    assert "durable_refresh" in info.capabilities
    assert "recurring_collection" in info.capabilities
    assert "interval_coverage" in info.capabilities
    assert "assessment_queue" in info.capabilities
    assert "content_assessment" in info.capabilities
    assert info.sources["x"]["acquisition_ready"] is True
    assert info.sources["youtube"]["acquisition_ready"] is False
    assert info.sources["youtube"]["acquisition_status"] == "configured"
    assert info.sources["x"]["indexed_documents"] == 0


def test_semantic_capability_requires_a_live_query_provider(tmp_path):
    class Embedder:
        model = "fixture-v1"

        def embed(self, texts):
            return [[1.0, 0.0] for _ in texts]

    db_path = tmp_path / "semantic-capability.db"
    retriever = HybridRetriever(db_path, embedding_provider=Embedder())
    retriever.initialize()
    conn = sqlite3.connect(db_path)
    topic_id = conn.execute(
        "INSERT INTO topics(name) VALUES ('semantic capability')"
    ).lastrowid
    run_id = conn.execute(
        """INSERT INTO research_runs(topic_id, run_date, status)
           VALUES (?, '2026-07-24T12:00:00Z', 'completed')""",
        (topic_id,),
    ).lastrowid
    conn.execute(
        """INSERT INTO findings
           (run_id, topic_id, source, source_url, source_title, content,
            first_seen, last_seen)
           VALUES (?, ?, 'web', 'https://example.test/semantic', 'Semantic',
                   'semantic evidence', '2026-07-24T12:00:00Z',
                   '2026-07-24T12:00:00Z')""",
        (run_id, topic_id),
    )
    conn.commit()
    conn.close()
    retriever.index_legacy_findings()

    disconnected = CacheQueryApplication(db_path, FakeRetriever([]))
    connected = CacheQueryApplication(db_path, retriever)

    assert "semantic_search" not in disconnected.service_info().capabilities
    assert "semantic_search" in connected.service_info().capabilities


def test_service_discovery_degrades_when_acquisition_loop_reports_failure(tmp_path):
    db_path = tmp_path / "research.db"
    ServiceStore(db_path).initialize()
    app = CacheQueryApplication(
        db_path,
        FakeRetriever([]),
        refresh_scheduler=FakeRefreshScheduler(),
        acquisition_sources=("reddit",),
        runtime_error=lambda: "acquisition_loop_failure",
    )

    assert app.health()["status"] == "degraded"
    assert app.service_info().status is contracts.ServiceStatus.DEGRADED


def test_job_poll_uses_typed_reader_and_rejects_unsafe_ids(tmp_path):
    class Reader:
        def get_job(self, job_id):
            return SimpleNamespace(job_id=job_id)

        def resume_after_operator(self, job_id):
            return SimpleNamespace(job_id=job_id, state="queued")

    db_path = tmp_path / "research.db"
    ServiceStore(db_path).initialize()
    app = CacheQueryApplication(
        db_path,
        FakeRetriever([]),
        job_reader=Reader(),
    )

    assert app.job("job-001").job_id == "job-001"
    assert app.resume_job("job-001").state == "queued"
    with pytest.raises(KeyError):
        app.job("../unsafe")
    with pytest.raises(KeyError):
        app.resume_job("../unsafe")


def test_minimum_response_budget_is_enforced_with_oversized_metadata(tmp_path):
    db_path = tmp_path / "research.db"
    ServiceStore(db_path).initialize()
    evidence = contracts.EvidenceItem.from_dict(
        {
            "schema_version": 1,
            "evidence_id": "ev-large",
            "document_id": "doc-large",
            "source": "web",
            "source_native_id": "native-large",
            "url": "https://example.test/" + ("path/" * 200),
            "title": "Oversized metadata " * 100,
            "snippet": "large evidence " * 100,
            "author": None,
            "published_at": None,
            "fetched_at": "2026-07-24T11:30:00Z",
            "acquisition_id": "acq-large",
            "content_hash": "sha256:large",
            "scores": {
                "lexical": 1.0,
                "semantic": 0.0,
                "graph": 0.0,
                "recency": 1.0,
                "fused": 1.0,
            },
        }
    )
    app = CacheQueryApplication(
        db_path,
        FakeRetriever([evidence]),
        clock=lambda: datetime(2026, 7, 24, 12, 0, tzinfo=timezone.utc),
    )

    response = app.query(_request(max_chars=512, freshness_policy="cache_only"))
    serialized = json.dumps(
        response.to_dict(),
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )

    assert len(serialized) <= 512
    assert response.truncated is True


def test_fresh_empty_coverage_suppresses_refresh_on_a_valid_no_result(tmp_path):
    class FreshEmptyCoverage(FakeRefreshScheduler):
        def cache_status(self, request, fallback):
            del request, fallback
            return contracts.CacheStatus.FRESH

    db_path = tmp_path / "research.db"
    ServiceStore(db_path).initialize()
    scheduler = FreshEmptyCoverage()
    app = CacheQueryApplication(
        db_path,
        FakeRetriever([]),
        refresh_scheduler=scheduler,
        clock=lambda: datetime(2026, 7, 24, 12, 0, tzinfo=timezone.utc),
    )

    response = app.query(_request())

    assert response.cache_status is contracts.CacheStatus.FRESH
    assert response.evidence == []
    assert response.job_id is None
    assert scheduler.requests == []
