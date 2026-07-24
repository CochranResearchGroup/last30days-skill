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


def test_v5_migration_preserves_legacy_data_and_creates_service_authority(tmp_path):
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
    assert conn.execute("SELECT MAX(version) FROM schema_version").fetchone()[0] == 5
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
    } <= tables
    job_columns = {
        row[1] for row in conn.execute("PRAGMA table_info(service_jobs)")
    }
    assert {"not_before_at", "spent_cents", "lease_generation"} <= job_columns
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
    ).fetchall() == [(1, 1), (2, 1), (3, 1), (4, 1), (5, 1)]
    conn.close()


def test_failed_migration_rolls_back_schema_and_version(tmp_path, monkeypatch):
    db_path = tmp_path / "rollback.db"
    store.init_db(db_path)
    monkeypatch.setitem(
        store.MIGRATIONS,
        6,
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
    assert conn.execute("SELECT MAX(version) FROM schema_version").fetchone()[0] == 5
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
    assert conn.execute("SELECT MAX(version) FROM schema_version").fetchone()[0] == 5
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
