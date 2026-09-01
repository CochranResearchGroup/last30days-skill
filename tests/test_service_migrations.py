"""Migration safety tests for the intelligence-service schema."""

import sqlite3
from concurrent.futures import ThreadPoolExecutor

import pytest

import store


def test_init_db_refuses_a_database_from_a_newer_service_schema(tmp_path):
    db_path = tmp_path / "future.db"
    conn = sqlite3.connect(db_path)
    conn.execute(
        """CREATE TABLE schema_version (
               version INTEGER PRIMARY KEY,
               applied_at TEXT DEFAULT (datetime('now'))
           )"""
    )
    conn.execute("INSERT INTO schema_version(version) VALUES (999)")
    conn.commit()
    conn.close()

    with pytest.raises(store.SchemaVersionError, match="newer schema version"):
        store.init_db(db_path)


def test_v8_migration_preserves_legacy_data_and_creates_service_authority(tmp_path):
    db_path = tmp_path / "legacy.db"
    conn = sqlite3.connect(db_path)
    conn.executescript(store.SCHEMA_V1)
    conn.executescript(store.SCHEMA_V1_DEFAULTS)
    conn.execute(
        "INSERT INTO topics(name, search_queries, schedule) VALUES (?, ?, ?)",
        ("Existing Topic", '["existing query"]', "0 8 * * *"),
    )
    conn.commit()
    conn.close()

    store.init_db(db_path)

    conn = sqlite3.connect(db_path)
    assert conn.execute("SELECT MAX(version) FROM schema_version").fetchone()[0] == 17
    assert conn.execute("SELECT name FROM topics").fetchone()[0] == "Existing Topic"
    tables = {
        row[0]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type IN ('table', 'view')"
        )
    }
    assert {
        "service_envelopes",
        "service_jobs",
        "service_job_events",
        "acquisitions",
        "documents",
        "documents_fts",
        "document_chunks",
        "chunk_embeddings",
        "entities",
        "relationships",
        "index_versions",
        "index_documents",
        "index_chunk_embeddings",
        "index_entity_aliases",
        "index_document_entities",
        "index_relationships",
        "relationship_evidence",
        "service_query_coverage",
        "service_decisions",
        "service_eval_results",
        "service_ai_artifacts",
        "service_model_calls",
        "service_maintenance_runs",
        "service_approvals",
        "service_index_head",
        "access_partitions",
        "document_versions",
        "document_version_sightings",
        "document_version_chunks",
        "document_version_embeddings",
        "document_version_entities",
        "document_version_relationships",
        "document_version_relationship_evidence",
        "index_document_versions",
        "index_document_version_embeddings",
        "index_document_version_entities",
        "index_document_version_relationships",
        "evidence_spans",
        "source_accounts",
        "profile_snapshots",
        "profile_snapshot_sightings",
        "identity_assertions",
        "identity_candidates",
        "identity_resolution_outcomes",
        "temporal_claims",
        "temporal_events",
        "collection_specs",
        "collection_runs",
        "collection_coverage_intervals",
        "collection_gaps",
        "collection_cursors",
        "collection_spec_revisions",
        "collection_schedule_state",
        "collection_run_triggers",
        "collection_run_attempts",
        "collection_profile_leases",
        "collection_source_health",
        "collection_assessment_batches",
        "service_intelligence_tasks",
        "service_intelligence_validation_receipts",
        "service_intelligence_promotion_receipts",
        "service_intelligence_replay_receipts",
        "graph_projection_outbox",
        "graph_projection_receipts",
        "temporal_retrieval_cases",
        "temporal_retrieval_evaluations",
        "service_ticks",
        "service_tick_attempts",
        "service_tick_lanes",
        "service_tick_schedules",
        "service_tick_schedule_events",
    } <= tables
    job_columns = {
        row[1] for row in conn.execute("PRAGMA table_info(service_jobs)")
    }
    assert {"not_before_at", "spent_cents", "lease_generation"} <= job_columns
    document_columns = {
        row[1] for row in conn.execute("PRAGMA table_info(documents)")
    }
    assert {"source_metadata_json", "media_json"} <= document_columns
    assert conn.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    assert conn.execute("PRAGMA foreign_key_check").fetchall() == []
    conn.close()


def test_v8_migration_backfills_an_immutable_current_document_version(tmp_path):
    db_path = tmp_path / "temporal-v7.db"
    conn = sqlite3.connect(db_path)
    conn.executescript(store.SCHEMA_V1)
    conn.executescript(store.SCHEMA_V1_DEFAULTS)
    for version in range(2, 8):
        conn.executescript(store.MIGRATIONS[version])
        conn.execute("INSERT INTO schema_version(version) VALUES (?)", (version,))
    conn.execute(
        """INSERT INTO service_jobs (
               job_id, job_type, dedupe_key, state, query_request_id,
               max_attempts, created_at, updated_at
           ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            "job-existing",
            "refresh",
            "existing",
            "complete",
            "request-existing",
            3,
            "2026-07-24T10:00:00+00:00",
            "2026-07-24T10:00:00+00:00",
        ),
    )
    conn.execute(
        """INSERT INTO acquisitions (
               acquisition_id, job_id, profile_id, source, adapter,
               adapter_version, query_text, status, observed_at, fetched_at,
               retention_class, redaction_class
           ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            "acq-existing",
            "job-existing",
            "profile-linkedin",
            "linkedin",
            "agent-browser",
            "1",
            "existing feed",
            "success",
            "2026-07-24T10:00:00+00:00",
            "2026-07-24T10:01:00+00:00",
            "standard",
            "authenticated",
        ),
    )
    conn.execute(
        """INSERT INTO documents (
               document_id, acquisition_id, source, source_native_id,
               canonical_url, title, author, normalized_text, content_hash,
               published_at, fetched_at, retention_class, redaction_class,
               transformation_version, source_metadata_json, media_json
           ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            "doc-existing",
            "acq-existing",
            "linkedin",
            "post-1",
            "https://www.linkedin.com/posts/1",
            "Existing post",
            "Ada Example",
            "A durable historical observation.",
            "sha256-existing",
            "2026-07-24T09:00:00+00:00",
            "2026-07-24T10:01:00+00:00",
            "standard",
            "authenticated",
            "normalize-v1",
            '{"handle":"ada"}',
            "[]",
        ),
    )
    conn.execute(
        """INSERT INTO document_chunks (
               chunk_id, document_id, ordinal, text, content_hash,
               chunker_version
           ) VALUES (?, ?, ?, ?, ?, ?)""",
        (
            "chunk-existing",
            "doc-existing",
            0,
            "A durable historical observation.",
            "sha256-existing",
            "chunk-v1",
        ),
    )
    conn.execute(
        """INSERT INTO document_sightings (
               document_id, acquisition_id, observed_at
           ) VALUES (?, ?, ?)""",
        (
            "doc-existing",
            "acq-existing",
            "2026-07-24T10:00:00+00:00",
        ),
    )
    conn.commit()
    conn.close()

    store.init_db(db_path)

    conn = sqlite3.connect(db_path)
    assert conn.execute("SELECT MAX(version) FROM schema_version").fetchone()[0] == 17
    version = conn.execute(
        """SELECT v.document_id, v.content_hash, v.access_partition_id,
                  v.system_from, v.system_to
           FROM document_versions AS v
           JOIN documents AS d ON d.current_version_id = v.version_id
           WHERE d.document_id = ?""",
        ("doc-existing",),
    ).fetchone()
    assert version == (
        "doc-existing",
        "sha256-existing",
        "profile:profile-linkedin",
        "2026-07-24T10:01:00+00:00",
        None,
    )
    assert conn.execute(
        """SELECT document_version_id
           FROM document_chunks
           WHERE chunk_id = 'chunk-existing'"""
    ).fetchone()[0] == conn.execute(
        "SELECT current_version_id FROM documents WHERE document_id = 'doc-existing'"
    ).fetchone()[0]
    assert conn.execute(
        """SELECT version_id, acquisition_id, observed_at
           FROM document_version_sightings"""
    ).fetchone() == (
        conn.execute(
            "SELECT current_version_id FROM documents WHERE document_id = 'doc-existing'"
        ).fetchone()[0],
        "acq-existing",
        "2026-07-24T10:00:00+00:00",
    )
    version_id = conn.execute(
        "SELECT current_version_id FROM documents WHERE document_id = 'doc-existing'"
    ).fetchone()[0]
    version_chunk_id = conn.execute(
        "SELECT chunk_id FROM document_version_chunks WHERE version_id = ?",
        (version_id,),
    ).fetchone()[0]
    with pytest.raises(sqlite3.IntegrityError, match="immutable"):
        conn.execute(
            "UPDATE document_versions SET title = 'rewritten' WHERE version_id = ?",
            (version_id,),
        )
    with pytest.raises(sqlite3.IntegrityError, match="immutable"):
        conn.execute(
            """UPDATE document_version_chunks
               SET text = 'rewritten'
               WHERE chunk_id = ?""",
            (version_chunk_id,),
        )
    conn.rollback()
    conn.execute("PRAGMA foreign_keys=ON")
    with pytest.raises(sqlite3.IntegrityError, match="FOREIGN KEY"):
        conn.execute(
            """INSERT INTO evidence_spans (
                   evidence_id, version_id, chunk_id, span_start, span_end,
                   span_digest, redaction_class, access_partition_id,
                   created_at
               ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                "evidence-wrong-partition",
                version_id,
                version_chunk_id,
                0,
                1,
                "sha256-span",
                "public",
                "public",
                "2026-07-24T10:02:00+00:00",
            ),
        )
    assert conn.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    assert conn.execute("PRAGMA foreign_key_check").fetchall() == []
    conn.close()


def test_concurrent_initializers_publish_each_schema_version_once(tmp_path):
    db_path = tmp_path / "concurrent.db"

    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(lambda _: store.init_db(db_path), range(8)))

    assert results == [db_path] * 8
    conn = sqlite3.connect(db_path)
    assert conn.execute(
        "SELECT version, COUNT(*) FROM schema_version GROUP BY version ORDER BY version"
    ).fetchall() == [
        (1, 1),
        (2, 1),
        (3, 1),
        (4, 1),
        (5, 1),
        (6, 1),
        (7, 1),
        (8, 1),
        (9, 1),
        (10, 1),
        (11, 1),
        (12, 1),
        (13, 1),
        (14, 1),
        (15, 1),
        (16, 1),
        (17, 1),
    ]
    conn.close()


def test_failed_migration_rolls_back_schema_and_version(tmp_path, monkeypatch):
    db_path = tmp_path / "rollback.db"
    store.init_db(db_path)
    monkeypatch.setitem(
        store.MIGRATIONS,
        18,
        """
        CREATE TABLE should_be_rolled_back (id INTEGER PRIMARY KEY);
        THIS IS NOT VALID SQL;
        """,
    )

    with pytest.raises(sqlite3.OperationalError):
        store.init_db(db_path)

    conn = sqlite3.connect(db_path)
    assert conn.execute(
        "SELECT name FROM sqlite_master WHERE name = 'should_be_rolled_back'"
    ).fetchone() is None
    assert conn.execute("SELECT MAX(version) FROM schema_version").fetchone()[0] == 17
    conn.close()


def test_v15_migration_preserves_observation_and_adds_viewer_lease_proof(tmp_path):
    db_path = tmp_path / "v14-observation.db"
    conn = sqlite3.connect(db_path)
    conn.executescript(store.SCHEMA_V1)
    conn.executescript(store.SCHEMA_V1_DEFAULTS)
    for version in range(2, 15):
        conn.executescript(store.MIGRATIONS[version])
        conn.execute("INSERT INTO schema_version(version) VALUES (?)", (version,))
    conn.execute(
        """INSERT INTO service_incidents (
               incident_id, fingerprint, first_tick_id, last_tick_id, lane_id,
               source, profile_ref, stage, incident_type, severity, state,
               safe_summary, access_partition_id, occurrence_count,
               first_detected_at, last_detected_at, operator_url
           ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            "incident-legacy",
            "fingerprint-legacy",
            "tick-1",
            "tick-1",
            "lane-1",
            "x",
            "profile:x",
            "collection",
            "reauthentication_required",
            "critical",
            "acknowledged",
            "Authentication is required.",
            "profile:x",
            1,
            "2026-08-04T12:00:00Z",
            "2026-08-04T12:00:00Z",
            "https://guac.example.test/client/legacy",
        ),
    )
    conn.execute(
        """INSERT INTO service_incident_observations (
               observation_request_id, incident_id, public_operator_url,
               requested_at
           ) VALUES (?, ?, ?, ?)""",
        (
            "observation-legacy",
            "incident-legacy",
            "https://guac.example.test/client/legacy",
            "2026-08-04T12:01:00Z",
        ),
    )
    conn.commit()
    conn.close()

    store.init_db(db_path)

    conn = sqlite3.connect(db_path)
    assert conn.execute("SELECT MAX(version) FROM schema_version").fetchone()[0] == 17
    assert conn.execute(
        """SELECT public_operator_url, viewer_lease_id, lease_acquired_at
           FROM service_incident_observations"""
    ).fetchone() == (
        "https://guac.example.test/client/legacy",
        None,
        None,
    )
    conn.close()


def test_v17_migration_preserves_provider_receipts_and_admits_third_attempt(tmp_path):
    db_path = tmp_path / "v16-provider-attempt.db"
    conn = sqlite3.connect(db_path)
    conn.executescript(store.SCHEMA_V1)
    conn.executescript(store.SCHEMA_V1_DEFAULTS)
    for version in range(2, 17):
        conn.executescript(store.MIGRATIONS[version])
        conn.execute("INSERT INTO schema_version(version) VALUES (?)", (version,))
    conn.execute(
        """INSERT INTO service_ticks (
               tick_id, schedule_id, interval_from, interval_to, trigger,
               config_revision, config_digest, config_json, state,
               created_at, updated_at
           ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            "tick-v16",
            "manual-default",
            "2026-08-03T00:00:00Z",
            "2026-08-04T00:00:00Z",
            "manual",
            "config-v16",
            "sha256:config-v16",
            "{}",
            "collecting",
            "2026-08-04T12:00:00Z",
            "2026-08-04T12:00:00Z",
        ),
    )
    conn.execute(
        """INSERT INTO service_tick_attempts (
               execution_attempt_id, tick_id, attempt, state, created_at
           ) VALUES (?, ?, ?, ?, ?)""",
        (
            "execution-v16",
            "tick-v16",
            1,
            "running",
            "2026-08-04T12:00:00Z",
        ),
    )
    conn.execute(
        """INSERT INTO service_tick_lanes (
               lane_id, tick_id, service_id, target_id, access_partition_id,
               service_config_json, target_config_json, lane_digest, state,
               created_at, updated_at
           ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            "lane-v16",
            "tick-v16",
            "x",
            "x-home",
            "profile:x",
            "{}",
            "{}",
            "sha256:lane-v16",
            "ready",
            "2026-08-04T12:00:00Z",
            "2026-08-04T12:00:00Z",
        ),
    )
    conn.execute(
        """INSERT INTO service_tick_providers (
               provider_manifest_id, tick_id, lane_id, provider_ordinal,
               provider_id, adapter_type, normalization_proof_ref,
               resource_keys_json, fallback_on_json, limits_json,
               provider_digest
           ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            "provider-v16",
            "tick-v16",
            "lane-v16",
            0,
            "x-browser",
            "agent_browser",
            "fixture:v16",
            "[]",
            '["transient"]',
            '{"attempts":3}',
            "sha256:provider-v16",
        ),
    )
    conn.execute(
        """INSERT INTO service_tick_provider_attempts (
               provider_attempt_id, tick_id, lane_id, provider_manifest_id,
               execution_attempt_id, retry_ordinal, state, result_digest,
               started_at, completed_at
           ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            "provider-attempt-v16",
            "tick-v16",
            "lane-v16",
            "provider-v16",
            "execution-v16",
            1,
            "failure",
            "sha256:result-v16",
            "2026-08-04T12:00:00Z",
            "2026-08-04T12:01:00Z",
        ),
    )
    conn.execute(
        """INSERT INTO service_tick_provider_results (
               provider_attempt_id, tick_id, lane_id, result_json,
               result_digest, created_at
           ) VALUES (?, ?, ?, ?, ?, ?)""",
        (
            "provider-attempt-v16",
            "tick-v16",
            "lane-v16",
            "{}",
            "sha256:result-v16",
            "2026-08-04T12:01:00Z",
        ),
    )
    conn.commit()
    conn.close()

    store.init_db(db_path)

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys=ON")
    assert conn.execute("SELECT MAX(version) FROM schema_version").fetchone()[0] == 17
    assert conn.execute(
        """SELECT a.retry_ordinal, r.result_digest
           FROM service_tick_provider_attempts AS a
           JOIN service_tick_provider_results AS r USING (provider_attempt_id)"""
    ).fetchone() == (1, "sha256:result-v16")
    conn.execute(
        """INSERT INTO service_tick_provider_attempts (
               provider_attempt_id, tick_id, lane_id, provider_manifest_id,
               execution_attempt_id, retry_ordinal, state, started_at
           ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            "provider-attempt-v17-third",
            "tick-v16",
            "lane-v16",
            "provider-v16",
            "execution-v16",
            2,
            "running",
            "2026-08-04T12:02:00Z",
        ),
    )
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            """INSERT INTO service_tick_provider_attempts (
                   provider_attempt_id, tick_id, lane_id, provider_manifest_id,
                   execution_attempt_id, retry_ordinal, state, started_at
               ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                "provider-attempt-v17-fourth",
                "tick-v16",
                "lane-v16",
                "provider-v16",
                "execution-v16",
                3,
                "running",
                "2026-08-04T12:03:00Z",
            ),
        )
    assert conn.execute("PRAGMA foreign_key_check").fetchall() == []
    conn.close()


def test_applied_v3_database_receives_replay_and_supervisor_schema(tmp_path):
    db_path = tmp_path / "applied-v3.db"
    conn = sqlite3.connect(db_path)
    conn.executescript(store.SCHEMA_V1)
    conn.executescript(store.SCHEMA_V1_DEFAULTS)
    for version in (2, 3):
        conn.executescript(store.MIGRATIONS[version])
        conn.execute("INSERT INTO schema_version(version) VALUES (?)", (version,))
    conn.commit()
    assert conn.execute(
        "SELECT name FROM sqlite_master WHERE name = 'index_documents'"
    ).fetchone() is None
    conn.close()

    store.init_db(db_path)

    conn = sqlite3.connect(db_path)
    assert conn.execute("SELECT MAX(version) FROM schema_version").fetchone()[0] == 17
    assert conn.execute(
        "SELECT name FROM sqlite_master WHERE name = 'index_documents'"
    ).fetchone()[0] == "index_documents"
    assert conn.execute(
        "SELECT name FROM sqlite_master WHERE name = 'service_query_coverage'"
    ).fetchone()[0] == "service_query_coverage"
    assert conn.execute(
        "SELECT name FROM sqlite_master WHERE name = 'index_relationships'"
    ).fetchone()[0] == "index_relationships"
    conn.close()
