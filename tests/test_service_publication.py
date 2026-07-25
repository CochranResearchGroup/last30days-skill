"""Idempotent host-side publication tests for worker proposals."""

import sqlite3
from datetime import datetime, timezone

from lib import service_contracts as contracts
from lib.service_publication import CorpusPublisher, PublicationLeaseError
from lib.service_retrieval import HybridRetriever
from lib.service_supervisor import RefreshSupervisor


def _work_request():
    return contracts.AcquisitionWorkRequest.from_dict(
        {
            "schema_version": 1,
            "work_id": "work-001",
            "job_id": "job-001",
            "lease_generation": 1,
            "attempt": 1,
            "profile_id": "default",
            "source": "reddit",
            "query": "cache service",
            "from_date": "2026-06-24",
            "to_date": "2026-07-24",
            "depth": "standard",
            "adapter": "reddit_api",
            "adapter_version": "1",
            "wall_timeout_seconds": 90,
            "item_limit": 20,
            "network_request_limit": 50,
            "cost_budget_cents": 25,
        }
    )


def _work_result():
    return contracts.AcquisitionWorkResult.from_dict(
        {
            "schema_version": 1,
            "work_id": "work-001",
            "job_id": "job-001",
            "lease_generation": 1,
            "source": "reddit",
            "adapter": "reddit_api",
            "adapter_version": "1",
            "status": "succeeded",
            "safe_error_code": None,
            "retry_class": "none",
            "retry_after_seconds": None,
            "observed_at": "2026-07-24T12:00:00Z",
            "fetched_at": "2026-07-24T12:00:01Z",
            "items": [
                {
                    "source_native_id": "post-001",
                    "url": "https://reddit.example/r/agents/1",
                    "title": "Cache-backed service",
                    "text": "Agents query cited evidence without browser mechanics.",
                    "author": "researcher",
                    "published_at": "2026-07-23T12:00:00Z",
                    "metadata": {
                        "engagement": {"score": 5},
                        "media": [
                            {
                                "kind": "image",
                                "url": "https://i.redd.it/cache-service.png",
                                "preview_url": None,
                                "mime_type": "image/png",
                                "width": 1200,
                                "height": 630,
                                "duration_seconds": None,
                                "alt_text": "Architecture diagram",
                            }
                        ],
                    },
                }
            ],
            "item_count": 1,
            "cost_cents": 2,
            "diagnostics": {"accepted_count": 1},
        }
    )


def test_publisher_validates_and_idempotently_projects_worker_content(tmp_path):
    db_path = tmp_path / "research.db"
    supervisor = RefreshSupervisor(db_path)
    supervisor.initialize()
    conn = sqlite3.connect(db_path)
    conn.execute(
        """INSERT INTO service_jobs
           (job_id, job_type, dedupe_key, state, query_request_id,
            attempts, max_attempts, budget_cents, spent_cents, lease_generation,
            lease_owner, lease_expires_at, created_at, updated_at)
           VALUES ('job-001', 'refresh', 'dedupe', 'acquiring', 'query-001',
                   1, 2, 25, 0, 1, 'publisher-test', '2026-07-24T12:05:00Z',
                   '2026-07-24T12:00:00Z', '2026-07-24T12:00:00Z')"""
    )
    conn.commit()
    conn.close()
    retriever = HybridRetriever(db_path)
    publisher = CorpusPublisher(
        db_path,
        retriever,
        clock=lambda: datetime(2026, 7, 24, 12, 0, tzinfo=timezone.utc),
    )

    first = publisher.record_result(
        _work_request(), _work_result(), worker_id="publisher-test"
    )
    second = publisher.record_result(
        _work_request(), _work_result(), worker_id="publisher-test"
    )
    index_version = publisher.publish_index()

    assert first.documents_inserted == 1
    assert second.documents_inserted == 0
    assert index_version.startswith("index-")
    snapshot = retriever.search_snapshot("browser mechanics")
    assert snapshot.index_version == index_version
    assert [item.url for item in snapshot.evidence] == [
        "https://reddit.example/r/agents/1"
    ]
    assert snapshot.evidence[0].media == [
        {
            "kind": "image",
            "url": "https://i.redd.it/cache-service.png",
            "preview_url": None,
            "mime_type": "image/png",
            "width": 1200,
            "height": 630,
            "duration_seconds": None,
            "alt_text": "Architecture diagram",
        }
    ]
    conn = sqlite3.connect(db_path)
    assert conn.execute("SELECT COUNT(*) FROM acquisitions").fetchone()[0] == 1
    assert conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0] == 1
    assert conn.execute("SELECT COUNT(*) FROM document_sightings").fetchone()[0] == 1
    assert conn.execute(
        "SELECT json_array_length(media_json) FROM documents"
    ).fetchone()[0] == 1
    conn.close()


def test_failed_result_is_ledgered_without_becoming_searchable(tmp_path):
    db_path = tmp_path / "research.db"
    supervisor = RefreshSupervisor(db_path)
    supervisor.initialize()
    conn = sqlite3.connect(db_path)
    conn.execute(
        """INSERT INTO service_jobs
           (job_id, job_type, dedupe_key, state, query_request_id,
            attempts, max_attempts, budget_cents, spent_cents, lease_generation,
            lease_owner, lease_expires_at, created_at, updated_at)
           VALUES ('job-001', 'refresh', 'dedupe', 'acquiring', 'query-001',
                   1, 2, 25, 0, 1, 'publisher-test', '2026-07-24T12:05:00Z',
                   '2026-07-24T12:00:00Z', '2026-07-24T12:00:00Z')"""
    )
    conn.commit()
    conn.close()
    failed = contracts.AcquisitionWorkResult.from_dict(
        {
            **_work_result().to_dict(),
            "status": "failed",
            "safe_error_code": "rate_limited",
            "retry_class": "rate_limit",
            "retry_after_seconds": 60,
            "items": [],
            "item_count": 0,
        }
    )
    publisher = CorpusPublisher(
        db_path,
        HybridRetriever(db_path),
        clock=lambda: datetime(2026, 7, 24, 12, 0, tzinfo=timezone.utc),
    )

    stats = publisher.record_result(
        _work_request(), failed, worker_id="publisher-test"
    )

    assert stats.documents_inserted == 0
    assert publisher.publish_index().startswith("index-")


def test_stale_generation_cannot_publish_after_lease_reclaim(tmp_path):
    db_path = tmp_path / "research.db"
    RefreshSupervisor(db_path).initialize()
    conn = sqlite3.connect(db_path)
    conn.execute(
        """INSERT INTO service_jobs
           (job_id, job_type, dedupe_key, state, query_request_id,
            attempts, max_attempts, budget_cents, spent_cents, lease_generation,
            lease_owner, lease_expires_at, created_at, updated_at)
           VALUES ('job-001', 'refresh', 'dedupe', 'acquiring', 'query-001',
                   2, 2, 25, 0, 2, 'new-worker', '2026-07-24T12:05:00Z',
                   '2026-07-24T12:00:00Z', '2026-07-24T12:00:00Z')"""
    )
    conn.commit()
    conn.close()
    publisher = CorpusPublisher(
        db_path,
        HybridRetriever(db_path),
        clock=lambda: datetime(2026, 7, 24, 12, 0, tzinfo=timezone.utc),
    )

    try:
        publisher.record_result(
            _work_request(), _work_result(), worker_id="old-worker"
        )
    except PublicationLeaseError:
        pass
    else:
        raise AssertionError("stale generation was allowed to publish")

    conn = sqlite3.connect(db_path)
    assert conn.execute("SELECT COUNT(*) FROM acquisitions").fetchone()[0] == 0
    assert conn.execute("SELECT COUNT(*) FROM service_envelopes").fetchone()[0] == 0
    conn.close()


def test_changed_content_replaces_current_projection_and_preserves_history(tmp_path):
    db_path = tmp_path / "research.db"
    RefreshSupervisor(db_path).initialize()
    conn = sqlite3.connect(db_path)
    for job_id, dedupe in (("job-001", "dedupe-1"), ("job-002", "dedupe-2")):
        conn.execute(
            """INSERT INTO service_jobs
               (job_id, job_type, dedupe_key, state, query_request_id,
                attempts, max_attempts, budget_cents, spent_cents,
                lease_generation, lease_owner, lease_expires_at,
                created_at, updated_at)
               VALUES (?, 'refresh', ?, 'acquiring', 'query-001',
                       1, 2, 25, 0, 1, 'publisher-test',
                       '2026-07-24T12:05:00Z',
                       '2026-07-24T12:00:00Z', '2026-07-24T12:00:00Z')""",
            (job_id, dedupe),
        )
    conn.commit()
    conn.close()
    retriever = HybridRetriever(db_path)
    publisher = CorpusPublisher(
        db_path,
        retriever,
        clock=lambda: datetime(2026, 7, 24, 12, 0, tzinfo=timezone.utc),
    )
    publisher.record_result(
        _work_request(), _work_result(), worker_id="publisher-test"
    )
    second_request = contracts.AcquisitionWorkRequest.from_dict(
        {
            **_work_request().to_dict(),
            "work_id": "work-002",
            "job_id": "job-002",
        }
    )
    new_text = "Agents now query revised semantic evidence from the durable cache."
    second_result = contracts.AcquisitionWorkResult.from_dict(
        {
            **_work_result().to_dict(),
            "work_id": "work-002",
            "job_id": "job-002",
            "fetched_at": "2026-07-24T12:02:00Z",
            "items": [
                {
                    **_work_result().items[0].to_dict(),
                    "text": new_text,
                }
            ],
        }
    )

    publisher.record_result(
        second_request, second_result, worker_id="publisher-test"
    )
    publisher.publish_index()

    conn = sqlite3.connect(db_path)
    row = conn.execute(
        "SELECT normalized_text, acquisition_id FROM documents"
    ).fetchone()
    assert row == (new_text, "work-002")
    assert conn.execute("SELECT COUNT(*) FROM acquisitions").fetchone()[0] == 2
    assert conn.execute("SELECT COUNT(*) FROM document_sightings").fetchone()[0] == 2
    conn.close()
    assert [item.url for item in retriever.search("revised semantic")] == [
        "https://reddit.example/r/agents/1"
    ]
