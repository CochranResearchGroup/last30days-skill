"""Agent-facing temporal product behavior."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone

import pytest

from lib import service_contracts as contracts
from lib.service_app import CacheQueryApplication
from lib.service_collection import CollectionCoordinator, CollectionSpec
from lib.service_retrieval import HybridRetriever
from lib.service_store import ServiceStore


class FakeScheduler:
    def __init__(self, ledger):
        self.ledger = ledger
        self.supervisor = None


def _app(tmp_path, *, coordinator=None):
    db_path = tmp_path / "research.db"
    ServiceStore(db_path).initialize()
    retriever = HybridRetriever(db_path)
    retriever.initialize()
    return CacheQueryApplication(
        db_path,
        retriever,
        collection_coordinator=coordinator,
        graph_projection_enabled=True,
        maintenance_enabled=True,
        clock=lambda: datetime(2026, 7, 25, 12, 0, tzinfo=timezone.utc),
    )


def test_temporal_product_query_is_cache_only_and_partition_scoped(tmp_path):
    app = _app(tmp_path)

    result = app.intelligence(
        {
            "action": "temporal_query",
            "query": "What did we know about Acme as of July 2026?",
            "profile_id": "linkedin-primary",
            "response_mode": "timeline",
            "as_of": "2026-07-01T00:00:00Z",
            "known_as_of": "2026-07-25T00:00:00Z",
        }
    )

    assert result["action"] == "temporal_query"
    assert result["response_mode"] == "timeline"
    assert result["cache_only"] is True
    assert result["access_partitions"] == [
        "public",
        "profile:linkedin-primary",
    ]
    assert result["query_kind"] == "known_as_of"
    assert result["freshness"]["generated_at"] == "2026-07-25T12:00:00Z"
    assert result["projection"]["graph_enabled"] is True


def test_profile_history_never_widens_an_authenticated_partition(tmp_path):
    app = _app(tmp_path)
    conn = sqlite3.connect(app.db_path)
    try:
        conn.execute(
            """INSERT INTO access_partitions
               (partition_id, partition_kind, profile_id, created_at)
               VALUES ('profile:linkedin-primary', 'authenticated',
                       'linkedin-primary', '2026-07-25T00:00:00Z')"""
        )
        conn.execute(
            """INSERT INTO source_accounts
               (source_account_id, source, native_account_id, handle,
                canonical_url, account_kind, access_partition_id,
                first_observed_at, last_observed_at, display_name,
                declared_links_json, evidence_ids_json)
               VALUES ('acct-li', 'linkedin', 'alice', 'alice',
                       'https://www.linkedin.com/in/alice/', 'person',
                       'profile:linkedin-primary', '2026-07-01T00:00:00Z',
                       '2026-07-25T00:00:00Z', 'Alice', '[]', '[]')"""
        )
        conn.execute(
            """INSERT INTO service_jobs
               (job_id, job_type, dedupe_key, state, query_request_id,
                attempts, max_attempts, budget_cents, created_at, updated_at)
               VALUES ('job-li', 'refresh', 'dedupe-li', 'completed',
                       'request-li', 1, 1, 0,
                       '2026-07-25T00:00:00Z', '2026-07-25T00:00:01Z')"""
        )
        conn.execute(
            """INSERT INTO acquisitions
               (acquisition_id, job_id, profile_id, source, adapter,
                adapter_version, query_text, status, observed_at, fetched_at,
                retention_class, redaction_class, item_count)
               VALUES ('acq-li', 'job-li', 'linkedin-primary', 'linkedin',
                       'linkedin-browser', 'v1', 'alice', 'succeeded',
                       '2026-07-25T00:00:00Z', '2026-07-25T00:00:01Z',
                       'cache', 'authenticated', 1)"""
        )
        conn.execute(
            """INSERT INTO profile_snapshots
               (snapshot_id, source_account_id, acquisition_id, content_hash,
                display_name, headline, about_text, metadata_json, observed_at,
                valid_from, valid_to, system_from, system_to,
                access_partition_id)
               VALUES ('snap-li', 'acct-li', 'acq-li', 'hash-li', 'Alice',
                       'Engineer', NULL, '{}', '2026-07-25T00:00:01Z',
                       NULL, NULL, '2026-07-25T00:00:01Z', NULL,
                       'profile:linkedin-primary')"""
        )
        conn.execute(
            """INSERT INTO source_accounts
               (source_account_id, source, native_account_id, handle,
                canonical_url, account_kind, access_partition_id,
                first_observed_at, last_observed_at, display_name,
                declared_links_json, evidence_ids_json)
               VALUES ('acct-public', 'linkedin', 'public', 'public',
                       'https://www.linkedin.com/in/public/', 'person',
                       'public', '2026-07-01T00:00:00Z',
                       '2026-07-25T00:00:00Z', 'Public', '[]', '[]')"""
        )
        conn.commit()
    finally:
        conn.close()

    private = app.intelligence(
        {
            "action": "profile_history",
            "profile_id": "linkedin-primary",
            "source": "linkedin",
            "handle": "alice",
        }
    )
    public = app.intelligence(
        {
            "action": "profile_history",
            "profile_id": "default",
            "source": "linkedin",
            "handle": "alice",
        }
    )

    assert private["profiles"][0]["source_account_id"] == "acct-li"
    assert public["profiles"] == []


def test_coverage_and_operational_status_are_compact_and_read_only(tmp_path):
    app = _app(tmp_path)

    coverage = app.intelligence(
        {"action": "coverage", "profile_id": "default"}
    )
    status = app.intelligence(
        {"action": "maintenance_status", "profile_id": "default"}
    )

    assert coverage == {
        "schema_version": contracts.SCHEMA_VERSION,
        "action": "coverage",
        "access_partitions": ["public"],
        "collections": [],
        "coverage": [],
        "gaps": [],
    }
    assert status["action"] == "maintenance_status"
    assert status["app_intelligence"]["enabled"] is True
    assert status["app_intelligence"]["contract_catalog"] == {
        "request_contract": {
            "name": "intelligence_task_request",
            "version": 1,
        },
        "result_contract": {
            "name": "intelligence_task_result",
            "version": 1,
        },
        "task_contracts": [
            {"task_type": "adapter_failure_triage", "version": 1},
            {"task_type": "adapter_repair_recommendation", "version": 1},
            {"task_type": "branch_decision", "version": 1},
            {"task_type": "content_assessment", "version": 1},
            {"task_type": "identity_resolution", "version": 1},
            {"task_type": "knowledge_extraction", "version": 1},
            {"task_type": "profile_change_assessment", "version": 1},
            {"task_type": "retrieval_evaluation", "version": 1},
        ],
        "limit_ranges": {
            "max_items": {"minimum": 1, "maximum": 100},
            "max_bytes": {"minimum": 1024, "maximum": 1_048_576},
            "max_calls": {"minimum": 0, "maximum": 5},
            "max_cost_cents": {"minimum": 0, "maximum": 10_000},
            "wall_timeout_seconds": {"minimum": 1, "maximum": 3600},
        },
    }
    assert status["graph_projection"]["enabled"] is True
    assert status["graph_projection"]["pending"] == 0
    assert "prompts" not in json.dumps(status).casefold()


def test_intelligence_rejects_unknown_fields_and_partition_injection(tmp_path):
    app = _app(tmp_path)
    with pytest.raises(contracts.ContractValidationError):
        app.intelligence(
            {
                "action": "coverage",
                "profile_id": "default",
                "access_partitions": ["profile:other"],
            }
        )
