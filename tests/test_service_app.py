"""Behavioral tests for the cache-first intelligence application."""

import json
from datetime import datetime, timezone
from types import SimpleNamespace

from lib import service_contracts as contracts
from lib.service_app import CacheQueryApplication
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
    )

    info = app.service_info()

    assert "durable_refresh" in info.capabilities
    assert info.sources["x"]["acquisition_ready"] is True
    assert info.sources["youtube"]["acquisition_ready"] is False
    assert info.sources["youtube"]["acquisition_status"] == "configured"
    assert info.sources["x"]["indexed_documents"] == 0


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
