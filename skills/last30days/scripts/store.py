#!/usr/bin/env python3
"""SQLite research accumulator for last30days.

Stores topics, research runs, and findings with:
- WAL mode for safe concurrent access (cron + user)
- FTS5 full-text search with porter+unicode61 tokenizer
- URL-based dedup with engagement metric updates on re-sighting
- Lightweight schema migrations without external dependencies

Database location: ~/.local/share/last30days/research.db
"""

import argparse
import json
import sqlite3
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

SCRIPT_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(SCRIPT_DIR))

from lib import schema

DB_DIR = Path.home() / ".local" / "share" / "last30days"
DB_PATH = DB_DIR / "research.db"

# Allow override for testing
_db_override = None


class SchemaVersionError(RuntimeError):
    """Raised when the on-disk database is incompatible with this runtime."""


def _get_db_path() -> Path:
    return _db_override or DB_PATH


SCHEMA_V1 = """
PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;
PRAGMA cache_size=-64000;

CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS topics (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    search_queries TEXT,
    schedule TEXT,
    enabled INTEGER DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS research_runs (
    id INTEGER PRIMARY KEY,
    topic_id INTEGER REFERENCES topics(id),
    run_date TEXT NOT NULL,
    source_mode TEXT,
    prompt_tokens INTEGER,
    completion_tokens INTEGER,
    token_cost REAL,
    duration_seconds REAL,
    status TEXT DEFAULT 'completed',
    error_message TEXT,
    findings_new INTEGER DEFAULT 0,
    findings_updated INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS findings (
    id INTEGER PRIMARY KEY,
    run_id INTEGER REFERENCES research_runs(id),
    topic_id INTEGER REFERENCES topics(id),
    source TEXT NOT NULL,
    source_url TEXT UNIQUE,
    source_title TEXT,
    author TEXT,
    content TEXT,
    summary TEXT,
    engagement_score REAL,
    relevance_score REAL,
    first_seen TEXT DEFAULT (datetime('now')),
    last_seen TEXT DEFAULT (datetime('now')),
    sighting_count INTEGER DEFAULT 1,
    dismissed INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_findings_topic ON findings(topic_id, first_seen);
CREATE INDEX IF NOT EXISTS idx_findings_source ON findings(source, topic_id);
CREATE INDEX IF NOT EXISTS idx_findings_url ON findings(source_url);

CREATE VIRTUAL TABLE IF NOT EXISTS findings_fts USING fts5(
    content, summary, source_title, author,
    tokenize='porter unicode61',
    content='findings',
    content_rowid='id'
);

CREATE TRIGGER IF NOT EXISTS findings_ai AFTER INSERT ON findings BEGIN
    INSERT INTO findings_fts(rowid, content, summary, source_title, author)
    VALUES (new.id, new.content, new.summary, new.source_title, new.author);
END;

CREATE TRIGGER IF NOT EXISTS findings_ad AFTER DELETE ON findings BEGIN
    INSERT INTO findings_fts(findings_fts, rowid, content, summary, source_title, author)
    VALUES ('delete', old.id, old.content, old.summary, old.source_title, old.author);
END;

CREATE TRIGGER IF NOT EXISTS findings_au AFTER UPDATE ON findings BEGIN
    INSERT INTO findings_fts(findings_fts, rowid, content, summary, source_title, author)
    VALUES ('delete', old.id, old.content, old.summary, old.source_title, old.author);
    INSERT INTO findings_fts(rowid, content, summary, source_title, author)
    VALUES (new.id, new.content, new.summary, new.source_title, new.author);
END;

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at TEXT DEFAULT (datetime('now'))
);
"""

SCHEMA_V1_DEFAULTS = """
INSERT OR IGNORE INTO schema_version (version) VALUES (1);
INSERT OR IGNORE INTO settings (key, value) VALUES ('daily_budget', '5.00');
INSERT OR IGNORE INTO settings (key, value) VALUES ('delivery_channel', '');
INSERT OR IGNORE INTO settings (key, value) VALUES ('delivery_mode', 'announce');
INSERT OR IGNORE INTO settings (key, value) VALUES ('briefing_format', 'concise');
INSERT OR IGNORE INTO settings (key, value) VALUES ('default_schedule', '0 8 * * *');
"""

_UPDATABLE_RUN_COLUMNS = frozenset({
    "source_mode",
    "prompt_tokens",
    "completion_tokens",
    "token_cost",
    "duration_seconds",
    "status",
    "error_message",
    "findings_new",
    "findings_updated",
})

_UPDATABLE_FINDING_COLUMNS = frozenset({
    "source",
    "source_url",
    "source_title",
    "author",
    "content",
    "summary",
    "engagement_score",
    "relevance_score",
    "last_seen",
    "sighting_count",
    "dismissed",
})

# Future migrations keyed by version number
MIGRATIONS: Dict[int, str] = {
    2: """
CREATE TABLE IF NOT EXISTS finding_sightings (
    id INTEGER PRIMARY KEY,
    finding_id INTEGER NOT NULL REFERENCES findings(id) ON DELETE CASCADE,
    run_id INTEGER REFERENCES research_runs(id) ON DELETE CASCADE,
    topic_id INTEGER REFERENCES topics(id) ON DELETE CASCADE,
    source TEXT NOT NULL,
    source_url TEXT NOT NULL,
    source_title TEXT,
    engagement_score REAL,
    relevance_score REAL,
    seen_at TEXT DEFAULT (datetime('now')),
    UNIQUE(run_id, finding_id)
);

CREATE INDEX IF NOT EXISTS idx_finding_sightings_run
    ON finding_sightings(run_id, topic_id);
CREATE INDEX IF NOT EXISTS idx_finding_sightings_topic_seen
    ON finding_sightings(topic_id, seen_at);
CREATE INDEX IF NOT EXISTS idx_finding_sightings_url
    ON finding_sightings(source_url);
""",
    3: """
CREATE TABLE IF NOT EXISTS service_envelopes (
    envelope_type TEXT NOT NULL,
    envelope_id TEXT NOT NULL,
    schema_version INTEGER NOT NULL,
    payload_json TEXT NOT NULL,
    payload_sha256 TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    PRIMARY KEY (envelope_type, envelope_id)
);

CREATE TABLE IF NOT EXISTS service_jobs (
    job_id TEXT PRIMARY KEY,
    job_type TEXT NOT NULL,
    dedupe_key TEXT NOT NULL,
    state TEXT NOT NULL,
    query_request_id TEXT NOT NULL,
    attempts INTEGER NOT NULL DEFAULT 0,
    max_attempts INTEGER NOT NULL,
    budget_cents INTEGER NOT NULL DEFAULT 0,
    lease_owner TEXT,
    lease_expires_at TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    published_index_version TEXT,
    error_code TEXT
);

CREATE INDEX IF NOT EXISTS idx_service_jobs_state_created
    ON service_jobs(state, created_at);
CREATE UNIQUE INDEX IF NOT EXISTS idx_service_jobs_active_dedupe
    ON service_jobs(dedupe_key)
    WHERE state IN (
        'queued',
        'planning',
        'acquiring',
        'normalizing',
        'indexing',
        'enriching',
        'validating',
        'awaiting_operator'
    );
CREATE INDEX IF NOT EXISTS idx_service_jobs_lease
    ON service_jobs(lease_expires_at)
    WHERE lease_owner IS NOT NULL;

CREATE TABLE IF NOT EXISTS service_job_events (
    event_id TEXT PRIMARY KEY,
    job_id TEXT NOT NULL REFERENCES service_jobs(job_id) ON DELETE CASCADE,
    sequence INTEGER NOT NULL,
    event_type TEXT NOT NULL,
    phase TEXT NOT NULL,
    occurred_at TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    redaction_class TEXT NOT NULL,
    UNIQUE (job_id, sequence)
);

CREATE TABLE IF NOT EXISTS acquisitions (
    acquisition_id TEXT PRIMARY KEY,
    job_id TEXT NOT NULL REFERENCES service_jobs(job_id) ON DELETE CASCADE,
    profile_id TEXT NOT NULL,
    source TEXT NOT NULL,
    adapter TEXT NOT NULL,
    adapter_version TEXT NOT NULL,
    query_text TEXT NOT NULL,
    status TEXT NOT NULL,
    observed_at TEXT NOT NULL,
    fetched_at TEXT NOT NULL,
    artifact_ref TEXT,
    content_hash TEXT,
    retention_class TEXT NOT NULL,
    redaction_class TEXT NOT NULL,
    item_count INTEGER NOT NULL DEFAULT 0,
    diagnostics_ref TEXT
);

CREATE INDEX IF NOT EXISTS idx_acquisitions_job_source
    ON acquisitions(job_id, source);
CREATE INDEX IF NOT EXISTS idx_acquisitions_content_hash
    ON acquisitions(content_hash)
    WHERE content_hash IS NOT NULL;

CREATE TABLE IF NOT EXISTS documents (
    document_id TEXT PRIMARY KEY,
    acquisition_id TEXT NOT NULL REFERENCES acquisitions(acquisition_id),
    source TEXT NOT NULL,
    source_native_id TEXT NOT NULL,
    canonical_url TEXT NOT NULL,
    title TEXT NOT NULL,
    author TEXT,
    normalized_text TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    published_at TEXT,
    fetched_at TEXT NOT NULL,
    retention_class TEXT NOT NULL,
    redaction_class TEXT NOT NULL,
    transformation_version TEXT NOT NULL,
    UNIQUE (source, source_native_id),
    UNIQUE (canonical_url)
);

CREATE INDEX IF NOT EXISTS idx_documents_source_published
    ON documents(source, published_at);
CREATE INDEX IF NOT EXISTS idx_documents_content_hash
    ON documents(content_hash);

CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts USING fts5(
    title,
    author,
    normalized_text,
    tokenize='porter unicode61',
    content='documents',
    content_rowid='rowid'
);

CREATE TRIGGER IF NOT EXISTS documents_ai AFTER INSERT ON documents BEGIN
    INSERT INTO documents_fts(rowid, title, author, normalized_text)
    VALUES (new.rowid, new.title, new.author, new.normalized_text);
END;

CREATE TRIGGER IF NOT EXISTS documents_ad AFTER DELETE ON documents BEGIN
    INSERT INTO documents_fts(
        documents_fts, rowid, title, author, normalized_text
    )
    VALUES (
        'delete', old.rowid, old.title, old.author, old.normalized_text
    );
END;

CREATE TRIGGER IF NOT EXISTS documents_au AFTER UPDATE ON documents BEGIN
    INSERT INTO documents_fts(
        documents_fts, rowid, title, author, normalized_text
    )
    VALUES (
        'delete', old.rowid, old.title, old.author, old.normalized_text
    );
    INSERT INTO documents_fts(rowid, title, author, normalized_text)
    VALUES (new.rowid, new.title, new.author, new.normalized_text);
END;

CREATE TABLE IF NOT EXISTS document_sightings (
    document_id TEXT NOT NULL REFERENCES documents(document_id) ON DELETE CASCADE,
    acquisition_id TEXT NOT NULL REFERENCES acquisitions(acquisition_id) ON DELETE CASCADE,
    topic_id INTEGER REFERENCES topics(id) ON DELETE SET NULL,
    observed_at TEXT NOT NULL,
    PRIMARY KEY (document_id, acquisition_id)
);

CREATE TABLE IF NOT EXISTS document_chunks (
    chunk_id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL REFERENCES documents(document_id) ON DELETE CASCADE,
    ordinal INTEGER NOT NULL,
    text TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    chunker_version TEXT NOT NULL,
    UNIQUE (document_id, ordinal)
);

CREATE TABLE IF NOT EXISTS chunk_embeddings (
    chunk_id TEXT NOT NULL REFERENCES document_chunks(chunk_id) ON DELETE CASCADE,
    model TEXT NOT NULL,
    dimensions INTEGER NOT NULL,
    vector BLOB NOT NULL,
    created_at TEXT NOT NULL,
    PRIMARY KEY (chunk_id, model)
);

CREATE TABLE IF NOT EXISTS entities (
    entity_id TEXT PRIMARY KEY,
    canonical_name TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS entity_aliases (
    entity_id TEXT NOT NULL REFERENCES entities(entity_id) ON DELETE CASCADE,
    alias TEXT NOT NULL,
    normalized_alias TEXT NOT NULL,
    PRIMARY KEY (entity_id, normalized_alias)
);

CREATE INDEX IF NOT EXISTS idx_entity_aliases_normalized
    ON entity_aliases(normalized_alias);

CREATE TABLE IF NOT EXISTS document_entities (
    document_id TEXT NOT NULL REFERENCES documents(document_id) ON DELETE CASCADE,
    entity_id TEXT NOT NULL REFERENCES entities(entity_id) ON DELETE CASCADE,
    evidence_chunk_id TEXT NOT NULL REFERENCES document_chunks(chunk_id) ON DELETE CASCADE,
    evidence_start INTEGER NOT NULL,
    evidence_end INTEGER NOT NULL,
    extractor_version TEXT NOT NULL,
    confidence REAL NOT NULL,
    validation_state TEXT NOT NULL,
    PRIMARY KEY (document_id, entity_id, evidence_chunk_id, evidence_start)
);

CREATE TABLE IF NOT EXISTS relationships (
    relationship_id TEXT PRIMARY KEY,
    subject_entity_id TEXT NOT NULL REFERENCES entities(entity_id) ON DELETE CASCADE,
    predicate TEXT NOT NULL,
    object_entity_id TEXT NOT NULL REFERENCES entities(entity_id) ON DELETE CASCADE,
    evidence_chunk_id TEXT NOT NULL REFERENCES document_chunks(chunk_id) ON DELETE CASCADE,
    extractor_version TEXT NOT NULL,
    confidence REAL NOT NULL,
    validation_state TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_relationships_subject
    ON relationships(subject_entity_id, predicate);
CREATE INDEX IF NOT EXISTS idx_relationships_object
    ON relationships(object_entity_id, predicate);

CREATE TABLE IF NOT EXISTS index_versions (
    index_version TEXT PRIMARY KEY,
    parent_version TEXT REFERENCES index_versions(index_version),
    ranking_config_json TEXT NOT NULL,
    document_count INTEGER NOT NULL,
    chunk_count INTEGER NOT NULL,
    embedding_model TEXT,
    created_at TEXT NOT NULL,
    published_at TEXT
);

CREATE TABLE IF NOT EXISTS service_decisions (
    decision_id TEXT PRIMARY KEY,
    job_id TEXT NOT NULL REFERENCES service_jobs(job_id) ON DELETE CASCADE,
    loop_name TEXT NOT NULL,
    action TEXT NOT NULL,
    confidence REAL NOT NULL,
    evidence_ids_json TEXT NOT NULL,
    rationale TEXT NOT NULL,
    model_ref TEXT NOT NULL,
    input_ref TEXT NOT NULL,
    output_ref TEXT NOT NULL,
    accepted INTEGER NOT NULL,
    validator_errors_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS service_eval_results (
    eval_id TEXT PRIMARY KEY,
    job_id TEXT REFERENCES service_jobs(job_id) ON DELETE SET NULL,
    index_version TEXT REFERENCES index_versions(index_version) ON DELETE SET NULL,
    suite_name TEXT NOT NULL,
    metrics_json TEXT NOT NULL,
    passed INTEGER NOT NULL,
    artifact_ref TEXT,
    created_at TEXT NOT NULL
);
""",
    4: """
CREATE TABLE IF NOT EXISTS index_documents (
    index_version TEXT NOT NULL REFERENCES index_versions(index_version) ON DELETE CASCADE,
    document_id TEXT NOT NULL REFERENCES documents(document_id) ON DELETE CASCADE,
    content_hash TEXT NOT NULL,
    PRIMARY KEY (index_version, document_id)
);

ALTER TABLE service_jobs ADD COLUMN not_before_at TEXT;
ALTER TABLE service_jobs ADD COLUMN spent_cents INTEGER NOT NULL DEFAULT 0;
ALTER TABLE service_jobs ADD COLUMN lease_generation INTEGER NOT NULL DEFAULT 0;

CREATE TABLE IF NOT EXISTS service_query_coverage (
    profile_id TEXT NOT NULL,
    normalized_query TEXT NOT NULL,
    source TEXT NOT NULL,
    status TEXT NOT NULL,
    fetched_at TEXT NOT NULL,
    fresh_until TEXT NOT NULL,
    retry_after TEXT,
    job_id TEXT REFERENCES service_jobs(job_id) ON DELETE SET NULL,
    index_version TEXT REFERENCES index_versions(index_version) ON DELETE SET NULL,
    error_code TEXT,
    updated_at TEXT NOT NULL,
    PRIMARY KEY (profile_id, normalized_query, source)
);

CREATE INDEX IF NOT EXISTS idx_service_query_coverage_freshness
    ON service_query_coverage(profile_id, normalized_query, fresh_until);
CREATE INDEX IF NOT EXISTS idx_service_query_coverage_retry
    ON service_query_coverage(retry_after)
    WHERE retry_after IS NOT NULL;
""",
    5: """
ALTER TABLE index_versions ADD COLUMN embedding_manifest_hash TEXT;
ALTER TABLE index_versions ADD COLUMN graph_manifest_hash TEXT;
ALTER TABLE document_entities ADD COLUMN proposal_id TEXT;
ALTER TABLE relationships ADD COLUMN proposal_id TEXT;
ALTER TABLE relationships ADD COLUMN projection_version TEXT;

CREATE TABLE IF NOT EXISTS relationship_evidence (
    relationship_id TEXT NOT NULL REFERENCES relationships(relationship_id) ON DELETE CASCADE,
    ordinal INTEGER NOT NULL,
    evidence_chunk_id TEXT NOT NULL REFERENCES document_chunks(chunk_id) ON DELETE CASCADE,
    evidence_start INTEGER NOT NULL CHECK (evidence_start >= 0),
    evidence_end INTEGER NOT NULL CHECK (evidence_end > evidence_start),
    span_hash TEXT NOT NULL,
    PRIMARY KEY (relationship_id, ordinal)
);

CREATE TABLE IF NOT EXISTS index_chunk_embeddings (
    index_version TEXT NOT NULL REFERENCES index_versions(index_version) ON DELETE CASCADE,
    chunk_id TEXT NOT NULL,
    model TEXT NOT NULL,
    dimensions INTEGER NOT NULL,
    vector BLOB NOT NULL,
    vector_hash TEXT NOT NULL,
    PRIMARY KEY (index_version, chunk_id, model),
    FOREIGN KEY (chunk_id, model)
        REFERENCES chunk_embeddings(chunk_id, model) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS index_entity_aliases (
    index_version TEXT NOT NULL REFERENCES index_versions(index_version) ON DELETE CASCADE,
    normalized_alias TEXT NOT NULL,
    entity_id TEXT NOT NULL REFERENCES entities(entity_id) ON DELETE CASCADE,
    PRIMARY KEY (index_version, normalized_alias, entity_id)
);

CREATE TABLE IF NOT EXISTS index_document_entities (
    index_version TEXT NOT NULL REFERENCES index_versions(index_version) ON DELETE CASCADE,
    document_id TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    evidence_chunk_id TEXT NOT NULL,
    evidence_start INTEGER NOT NULL,
    PRIMARY KEY (
        index_version, document_id, entity_id, evidence_chunk_id, evidence_start
    ),
    FOREIGN KEY (document_id, entity_id, evidence_chunk_id, evidence_start)
        REFERENCES document_entities(
            document_id, entity_id, evidence_chunk_id, evidence_start
        ) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS index_relationships (
    index_version TEXT NOT NULL REFERENCES index_versions(index_version) ON DELETE CASCADE,
    relationship_id TEXT NOT NULL REFERENCES relationships(relationship_id) ON DELETE CASCADE,
    subject_entity_id TEXT NOT NULL,
    predicate TEXT NOT NULL,
    object_entity_id TEXT NOT NULL,
    evidence_chunk_id TEXT NOT NULL REFERENCES document_chunks(chunk_id) ON DELETE CASCADE,
    evidence_start INTEGER NOT NULL,
    evidence_end INTEGER NOT NULL,
    span_hash TEXT NOT NULL,
    confidence REAL NOT NULL,
    PRIMARY KEY (index_version, relationship_id)
);
""",
    6: """
CREATE TABLE IF NOT EXISTS service_ai_artifacts (
    artifact_ref TEXT PRIMARY KEY,
    artifact_kind TEXT NOT NULL,
    media_type TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    payload_sha256 TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS service_model_calls (
    call_id TEXT PRIMARY KEY,
    job_id TEXT REFERENCES service_jobs(job_id) ON DELETE SET NULL,
    loop_name TEXT NOT NULL,
    model_ref TEXT NOT NULL,
    input_ref TEXT NOT NULL REFERENCES service_ai_artifacts(artifact_ref),
    output_ref TEXT REFERENCES service_ai_artifacts(artifact_ref),
    event_stream_ref TEXT REFERENCES service_ai_artifacts(artifact_ref),
    thread_id TEXT,
    turn_id TEXT,
    status TEXT NOT NULL,
    error_code TEXT,
    started_at TEXT NOT NULL,
    completed_at TEXT
);

CREATE TABLE IF NOT EXISTS service_maintenance_runs (
    run_id TEXT PRIMARY KEY,
    job_id TEXT NOT NULL REFERENCES service_jobs(job_id) ON DELETE CASCADE,
    adapter TEXT NOT NULL,
    failure_fingerprint TEXT NOT NULL,
    state TEXT NOT NULL,
    attempt_count INTEGER NOT NULL DEFAULT 0,
    rework_count INTEGER NOT NULL DEFAULT 0,
    branch_count INTEGER NOT NULL DEFAULT 0,
    current_branch TEXT,
    thread_id TEXT,
    policy_json TEXT NOT NULL,
    recommendation_ref TEXT REFERENCES service_ai_artifacts(artifact_ref),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE(job_id, adapter, failure_fingerprint)
);

CREATE TABLE IF NOT EXISTS service_approvals (
    approval_id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL REFERENCES service_maintenance_runs(run_id) ON DELETE CASCADE,
    action TEXT NOT NULL,
    status TEXT NOT NULL,
    requested_at TEXT NOT NULL,
    decided_at TEXT,
    decided_by TEXT,
    evidence_ref TEXT NOT NULL REFERENCES service_ai_artifacts(artifact_ref),
    UNIQUE(run_id, action)
);

CREATE INDEX IF NOT EXISTS idx_service_model_calls_job_loop
    ON service_model_calls(job_id, loop_name, started_at);
CREATE INDEX IF NOT EXISTS idx_service_maintenance_state
    ON service_maintenance_runs(state, updated_at);
CREATE INDEX IF NOT EXISTS idx_service_approvals_run
    ON service_approvals(run_id, status);
""",
    7: """
ALTER TABLE documents
    ADD COLUMN source_metadata_json TEXT NOT NULL DEFAULT '{}';
ALTER TABLE documents
    ADD COLUMN media_json TEXT NOT NULL DEFAULT '[]';
CREATE TABLE IF NOT EXISTS service_index_head (
    singleton_id INTEGER PRIMARY KEY CHECK (singleton_id = 1),
    index_version TEXT NOT NULL REFERENCES index_versions(index_version),
    activated_at TEXT NOT NULL
);
""",
    8: """
CREATE TABLE access_partitions (
    partition_id TEXT PRIMARY KEY,
    partition_kind TEXT NOT NULL
        CHECK (partition_kind IN ('public', 'authenticated')),
    profile_id TEXT,
    created_at TEXT NOT NULL,
    CHECK (
        (partition_kind = 'public' AND profile_id IS NULL)
        OR (partition_kind = 'authenticated' AND profile_id IS NOT NULL)
    )
);

INSERT INTO access_partitions (
    partition_id, partition_kind, profile_id, created_at
) VALUES ('public', 'public', NULL, datetime('now'));

INSERT OR IGNORE INTO access_partitions (
    partition_id, partition_kind, profile_id, created_at
)
SELECT DISTINCT
    'profile:' || profile_id,
    'authenticated',
    profile_id,
    datetime('now')
FROM acquisitions
WHERE redaction_class = 'authenticated';

ALTER TABLE documents ADD COLUMN current_version_id TEXT;
ALTER TABLE documents
    ADD COLUMN access_partition_id TEXT NOT NULL DEFAULT 'public';

CREATE TABLE document_versions (
    version_id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL REFERENCES documents(document_id),
    acquisition_id TEXT NOT NULL REFERENCES acquisitions(acquisition_id),
    content_hash TEXT NOT NULL,
    title TEXT NOT NULL,
    author TEXT,
    normalized_text TEXT NOT NULL,
    source_metadata_json TEXT NOT NULL,
    media_json TEXT NOT NULL,
    published_at TEXT,
    valid_from TEXT,
    valid_to TEXT,
    observed_at TEXT NOT NULL,
    fetched_at TEXT NOT NULL,
    system_from TEXT NOT NULL,
    system_to TEXT,
    retention_class TEXT NOT NULL,
    redaction_class TEXT NOT NULL,
    access_partition_id TEXT NOT NULL
        REFERENCES access_partitions(partition_id),
    transformation_version TEXT NOT NULL,
    UNIQUE (document_id, content_hash),
    UNIQUE (version_id, access_partition_id),
    CHECK (valid_to IS NULL OR valid_from IS NULL OR valid_to >= valid_from),
    CHECK (system_to IS NULL OR system_to >= system_from)
);

CREATE INDEX idx_document_versions_document_system
    ON document_versions(document_id, system_from);
CREATE INDEX idx_document_versions_published
    ON document_versions(published_at);
CREATE INDEX idx_document_versions_partition
    ON document_versions(access_partition_id, document_id);

INSERT INTO document_versions (
    version_id, document_id, acquisition_id, content_hash, title, author,
    normalized_text, source_metadata_json, media_json, published_at,
    valid_from, valid_to, observed_at, fetched_at, system_from, system_to,
    retention_class, redaction_class, access_partition_id,
    transformation_version
)
SELECT
    'ver-baseline-' || d.document_id,
    d.document_id,
    d.acquisition_id,
    d.content_hash,
    d.title,
    d.author,
    d.normalized_text,
    d.source_metadata_json,
    d.media_json,
    d.published_at,
    d.published_at,
    NULL,
    COALESCE(
        (
            SELECT MIN(ds.observed_at)
            FROM document_sightings AS ds
            WHERE ds.document_id = d.document_id
        ),
        d.fetched_at
    ),
    d.fetched_at,
    d.fetched_at,
    NULL,
    d.retention_class,
    d.redaction_class,
    CASE
        WHEN d.redaction_class = 'authenticated'
        THEN 'profile:' || a.profile_id
        ELSE 'public'
    END,
    d.transformation_version
FROM documents AS d
JOIN acquisitions AS a ON a.acquisition_id = d.acquisition_id;

UPDATE documents
SET current_version_id = 'ver-baseline-' || document_id,
    access_partition_id = CASE
        WHEN redaction_class = 'authenticated'
        THEN 'profile:' || (
            SELECT a.profile_id
            FROM acquisitions AS a
            WHERE a.acquisition_id = documents.acquisition_id
        )
        ELSE 'public'
    END;

CREATE TRIGGER document_versions_no_update
BEFORE UPDATE ON document_versions
BEGIN
    SELECT RAISE(ABORT, 'document_versions are immutable');
END;

CREATE TRIGGER document_versions_no_delete
BEFORE DELETE ON document_versions
BEGIN
    SELECT RAISE(ABORT, 'document_versions are immutable');
END;

CREATE TABLE document_version_sightings (
    version_id TEXT NOT NULL,
    acquisition_id TEXT NOT NULL
        REFERENCES acquisitions(acquisition_id),
    topic_id INTEGER REFERENCES topics(id) ON DELETE SET NULL,
    collection_spec_id TEXT,
    collection_run_id TEXT,
    observed_at TEXT NOT NULL,
    access_partition_id TEXT NOT NULL,
    FOREIGN KEY (version_id, access_partition_id)
        REFERENCES document_versions(version_id, access_partition_id),
    PRIMARY KEY (version_id, acquisition_id)
);

INSERT INTO document_version_sightings (
    version_id, acquisition_id, topic_id, observed_at, access_partition_id
)
SELECT
    'ver-baseline-' || ds.document_id,
    ds.acquisition_id,
    ds.topic_id,
    ds.observed_at,
    d.access_partition_id
FROM document_sightings AS ds
JOIN documents AS d ON d.document_id = ds.document_id;

CREATE TABLE document_version_chunks (
    chunk_id TEXT PRIMARY KEY,
    version_id TEXT NOT NULL,
    document_id TEXT NOT NULL REFERENCES documents(document_id),
    ordinal INTEGER NOT NULL,
    text TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    chunker_version TEXT NOT NULL,
    access_partition_id TEXT NOT NULL,
    FOREIGN KEY (version_id, access_partition_id)
        REFERENCES document_versions(version_id, access_partition_id),
    UNIQUE (version_id, ordinal),
    UNIQUE (version_id, chunk_id, access_partition_id)
);

INSERT INTO document_version_chunks (
    chunk_id, version_id, document_id, ordinal, text, content_hash,
    chunker_version, access_partition_id
)
SELECT
    'vchunk-baseline-' || c.chunk_id,
    d.current_version_id,
    c.document_id,
    c.ordinal,
    c.text,
    c.content_hash,
    c.chunker_version,
    d.access_partition_id
FROM document_chunks AS c
JOIN documents AS d ON d.document_id = c.document_id;

CREATE TRIGGER document_version_chunks_no_update
BEFORE UPDATE ON document_version_chunks
BEGIN
    SELECT RAISE(ABORT, 'document_version_chunks are immutable');
END;

CREATE TRIGGER document_version_chunks_no_delete
BEFORE DELETE ON document_version_chunks
BEGIN
    SELECT RAISE(ABORT, 'document_version_chunks are immutable');
END;

ALTER TABLE document_chunks ADD COLUMN document_version_id TEXT;

UPDATE document_chunks
SET document_version_id = (
    SELECT d.current_version_id
    FROM documents AS d
    WHERE d.document_id = document_chunks.document_id
);

CREATE TABLE evidence_spans (
    evidence_id TEXT PRIMARY KEY,
    version_id TEXT NOT NULL,
    chunk_id TEXT NOT NULL,
    span_start INTEGER NOT NULL CHECK (span_start >= 0),
    span_end INTEGER NOT NULL CHECK (span_end > span_start),
    span_digest TEXT NOT NULL,
    redaction_class TEXT NOT NULL,
    access_partition_id TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (version_id, chunk_id, access_partition_id)
        REFERENCES document_version_chunks(
            version_id, chunk_id, access_partition_id
        ),
    UNIQUE (evidence_id, access_partition_id),
    UNIQUE (version_id, chunk_id, span_start, span_end)
);

CREATE TRIGGER evidence_spans_no_update
BEFORE UPDATE ON evidence_spans
BEGIN
    SELECT RAISE(ABORT, 'evidence_spans are immutable');
END;

CREATE TRIGGER evidence_spans_no_delete
BEFORE DELETE ON evidence_spans
BEGIN
    SELECT RAISE(ABORT, 'evidence_spans are immutable');
END;

CREATE TABLE source_accounts (
    source_account_id TEXT PRIMARY KEY,
    source TEXT NOT NULL,
    native_account_id TEXT NOT NULL,
    handle TEXT,
    canonical_url TEXT,
    account_kind TEXT NOT NULL,
    access_partition_id TEXT NOT NULL
        REFERENCES access_partitions(partition_id),
    first_observed_at TEXT NOT NULL,
    last_observed_at TEXT NOT NULL,
    UNIQUE (source, native_account_id),
    UNIQUE (source_account_id, access_partition_id)
);

CREATE TABLE profile_snapshots (
    snapshot_id TEXT PRIMARY KEY,
    source_account_id TEXT NOT NULL,
    acquisition_id TEXT NOT NULL REFERENCES acquisitions(acquisition_id),
    content_hash TEXT NOT NULL,
    display_name TEXT,
    headline TEXT,
    about_text TEXT,
    metadata_json TEXT NOT NULL,
    observed_at TEXT NOT NULL,
    valid_from TEXT,
    valid_to TEXT,
    system_from TEXT NOT NULL,
    system_to TEXT,
    access_partition_id TEXT NOT NULL
        REFERENCES access_partitions(partition_id),
    FOREIGN KEY (source_account_id, access_partition_id)
        REFERENCES source_accounts(
            source_account_id, access_partition_id
        ),
    UNIQUE (source_account_id, content_hash),
    UNIQUE (snapshot_id, access_partition_id)
);

CREATE TABLE profile_snapshot_sections (
    section_id TEXT PRIMARY KEY,
    snapshot_id TEXT NOT NULL,
    section_kind TEXT NOT NULL,
    ordinal INTEGER NOT NULL,
    normalized_text TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    access_partition_id TEXT NOT NULL,
    FOREIGN KEY (snapshot_id, access_partition_id)
        REFERENCES profile_snapshots(snapshot_id, access_partition_id),
    UNIQUE (snapshot_id, section_kind, ordinal)
);

CREATE TABLE identity_assertions (
    assertion_id TEXT PRIMARY KEY,
    subject_account_id TEXT NOT NULL,
    object_entity_id TEXT NOT NULL REFERENCES entities(entity_id),
    assertion_kind TEXT NOT NULL,
    confidence REAL NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    validation_state TEXT NOT NULL,
    valid_from TEXT,
    valid_to TEXT,
    system_from TEXT NOT NULL,
    system_to TEXT,
    supersedes_assertion_id TEXT
        REFERENCES identity_assertions(assertion_id),
    access_partition_id TEXT NOT NULL
        REFERENCES access_partitions(partition_id),
    contract_version TEXT NOT NULL,
    FOREIGN KEY (subject_account_id, access_partition_id)
        REFERENCES source_accounts(
            source_account_id, access_partition_id
        ),
    UNIQUE (assertion_id, access_partition_id)
);

CREATE TABLE identity_assertion_evidence (
    assertion_id TEXT NOT NULL,
    evidence_id TEXT NOT NULL,
    access_partition_id TEXT NOT NULL,
    FOREIGN KEY (assertion_id, access_partition_id)
        REFERENCES identity_assertions(assertion_id, access_partition_id),
    FOREIGN KEY (evidence_id, access_partition_id)
        REFERENCES evidence_spans(evidence_id, access_partition_id),
    PRIMARY KEY (assertion_id, evidence_id)
);

CREATE TABLE temporal_claims (
    claim_id TEXT PRIMARY KEY,
    subject_entity_id TEXT NOT NULL REFERENCES entities(entity_id),
    predicate TEXT NOT NULL,
    object_entity_id TEXT REFERENCES entities(entity_id),
    object_value_json TEXT,
    confidence REAL NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    validation_state TEXT NOT NULL,
    valid_from TEXT,
    valid_to TEXT,
    observed_at TEXT NOT NULL,
    system_from TEXT NOT NULL,
    system_to TEXT,
    access_partition_id TEXT NOT NULL
        REFERENCES access_partitions(partition_id),
    extractor_version TEXT NOT NULL,
    CHECK (
        (object_entity_id IS NOT NULL AND object_value_json IS NULL)
        OR (object_entity_id IS NULL AND object_value_json IS NOT NULL)
    ),
    UNIQUE (claim_id, access_partition_id)
);

CREATE TABLE temporal_claim_evidence (
    claim_id TEXT NOT NULL,
    evidence_id TEXT NOT NULL,
    access_partition_id TEXT NOT NULL,
    FOREIGN KEY (claim_id, access_partition_id)
        REFERENCES temporal_claims(claim_id, access_partition_id),
    FOREIGN KEY (evidence_id, access_partition_id)
        REFERENCES evidence_spans(evidence_id, access_partition_id),
    PRIMARY KEY (claim_id, evidence_id)
);

CREATE TABLE claim_conflicts (
    conflict_id TEXT PRIMARY KEY,
    left_claim_id TEXT NOT NULL,
    right_claim_id TEXT NOT NULL,
    conflict_kind TEXT NOT NULL,
    detected_at TEXT NOT NULL,
    resolution_state TEXT NOT NULL,
    access_partition_id TEXT NOT NULL,
    FOREIGN KEY (left_claim_id, access_partition_id)
        REFERENCES temporal_claims(claim_id, access_partition_id),
    FOREIGN KEY (right_claim_id, access_partition_id)
        REFERENCES temporal_claims(claim_id, access_partition_id),
    CHECK (left_claim_id <> right_claim_id),
    UNIQUE (left_claim_id, right_claim_id, conflict_kind)
);

CREATE TABLE claim_supersessions (
    prior_claim_id TEXT NOT NULL,
    successor_claim_id TEXT NOT NULL,
    reason TEXT NOT NULL,
    created_at TEXT NOT NULL,
    access_partition_id TEXT NOT NULL,
    FOREIGN KEY (prior_claim_id, access_partition_id)
        REFERENCES temporal_claims(claim_id, access_partition_id),
    FOREIGN KEY (successor_claim_id, access_partition_id)
        REFERENCES temporal_claims(claim_id, access_partition_id),
    PRIMARY KEY (prior_claim_id, successor_claim_id),
    CHECK (prior_claim_id <> successor_claim_id)
);

CREATE TABLE temporal_events (
    event_id TEXT PRIMARY KEY,
    event_type TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    event_time_from TEXT,
    event_time_to TEXT,
    observed_at TEXT NOT NULL,
    system_from TEXT NOT NULL,
    system_to TEXT,
    access_partition_id TEXT NOT NULL
        REFERENCES access_partitions(partition_id),
    extractor_version TEXT NOT NULL,
    UNIQUE (event_id, access_partition_id)
);

CREATE TABLE temporal_event_entities (
    event_id TEXT NOT NULL REFERENCES temporal_events(event_id),
    entity_id TEXT NOT NULL REFERENCES entities(entity_id),
    role TEXT NOT NULL,
    PRIMARY KEY (event_id, entity_id, role)
);

CREATE TABLE temporal_event_evidence (
    event_id TEXT NOT NULL,
    evidence_id TEXT NOT NULL,
    access_partition_id TEXT NOT NULL,
    FOREIGN KEY (event_id, access_partition_id)
        REFERENCES temporal_events(event_id, access_partition_id),
    FOREIGN KEY (evidence_id, access_partition_id)
        REFERENCES evidence_spans(evidence_id, access_partition_id),
    PRIMARY KEY (event_id, evidence_id)
);

CREATE TABLE collection_specs (
    collection_spec_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    source TEXT NOT NULL,
    surface_kind TEXT NOT NULL,
    selector_json TEXT NOT NULL,
    profile_id TEXT NOT NULL,
    schedule TEXT NOT NULL,
    item_limit INTEGER NOT NULL CHECK (item_limit > 0),
    enabled INTEGER NOT NULL CHECK (enabled IN (0, 1)),
    spec_version INTEGER NOT NULL,
    access_partition_id TEXT NOT NULL
        REFERENCES access_partitions(partition_id),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE (name, spec_version),
    UNIQUE (collection_spec_id, access_partition_id)
);

CREATE TABLE collection_runs (
    collection_run_id TEXT PRIMARY KEY,
    collection_spec_id TEXT NOT NULL,
    job_id TEXT REFERENCES service_jobs(job_id),
    state TEXT NOT NULL,
    claimed_by TEXT,
    lease_generation INTEGER NOT NULL DEFAULT 0,
    scheduled_for TEXT NOT NULL,
    started_at TEXT,
    completed_at TEXT,
    cursor_before TEXT,
    cursor_after TEXT,
    watermark_before TEXT,
    watermark_after TEXT,
    attempted_count INTEGER NOT NULL DEFAULT 0,
    observed_count INTEGER NOT NULL DEFAULT 0,
    stored_count INTEGER NOT NULL DEFAULT 0,
    error_code TEXT,
    access_partition_id TEXT NOT NULL,
    FOREIGN KEY (collection_spec_id, access_partition_id)
        REFERENCES collection_specs(
            collection_spec_id, access_partition_id
        ),
    UNIQUE (collection_run_id, access_partition_id)
);

CREATE INDEX idx_collection_runs_due
    ON collection_runs(state, scheduled_for);

CREATE TABLE collection_coverage_intervals (
    coverage_id TEXT PRIMARY KEY,
    collection_run_id TEXT NOT NULL,
    collection_spec_id TEXT NOT NULL,
    interval_from TEXT,
    interval_to TEXT,
    coverage_state TEXT NOT NULL,
    selector_digest TEXT NOT NULL,
    attempted_count INTEGER NOT NULL,
    observed_count INTEGER NOT NULL,
    access_partition_id TEXT NOT NULL,
    recorded_at TEXT NOT NULL,
    FOREIGN KEY (collection_run_id, access_partition_id)
        REFERENCES collection_runs(collection_run_id, access_partition_id),
    FOREIGN KEY (collection_spec_id, access_partition_id)
        REFERENCES collection_specs(
            collection_spec_id, access_partition_id
        )
);

CREATE TABLE collection_gaps (
    gap_id TEXT PRIMARY KEY,
    collection_spec_id TEXT NOT NULL,
    collection_run_id TEXT,
    gap_kind TEXT NOT NULL,
    interval_from TEXT,
    interval_to TEXT,
    detail_json TEXT NOT NULL,
    status TEXT NOT NULL,
    access_partition_id TEXT NOT NULL,
    detected_at TEXT NOT NULL,
    resolved_at TEXT,
    FOREIGN KEY (collection_spec_id, access_partition_id)
        REFERENCES collection_specs(
            collection_spec_id, access_partition_id
        ),
    FOREIGN KEY (collection_run_id, access_partition_id)
        REFERENCES collection_runs(collection_run_id, access_partition_id)
);

CREATE TABLE collection_cursors (
    collection_spec_id TEXT PRIMARY KEY,
    cursor_value TEXT,
    watermark_value TEXT,
    lease_generation INTEGER NOT NULL DEFAULT 0,
    updated_at TEXT NOT NULL,
    access_partition_id TEXT NOT NULL,
    FOREIGN KEY (collection_spec_id, access_partition_id)
        REFERENCES collection_specs(
            collection_spec_id, access_partition_id
        )
);

CREATE TABLE graph_projection_outbox (
    outbox_id TEXT PRIMARY KEY,
    aggregate_kind TEXT NOT NULL,
    aggregate_id TEXT NOT NULL,
    operation TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    payload_sha256 TEXT NOT NULL,
    access_partition_id TEXT NOT NULL
        REFERENCES access_partitions(partition_id),
    state TEXT NOT NULL,
    attempt_count INTEGER NOT NULL DEFAULT 0,
    not_before_at TEXT,
    created_at TEXT NOT NULL,
    published_at TEXT,
    error_code TEXT,
    UNIQUE (aggregate_kind, aggregate_id, operation, payload_sha256)
);

CREATE INDEX idx_graph_projection_outbox_ready
    ON graph_projection_outbox(state, not_before_at, created_at);
""",
    9: """
CREATE TABLE document_version_embeddings (
    chunk_id TEXT NOT NULL
        REFERENCES document_version_chunks(chunk_id),
    model TEXT NOT NULL,
    dimensions INTEGER NOT NULL,
    vector BLOB NOT NULL,
    vector_hash TEXT NOT NULL,
    created_at TEXT NOT NULL,
    PRIMARY KEY (chunk_id, model)
);

CREATE TABLE document_version_entities (
    version_id TEXT NOT NULL,
    entity_id TEXT NOT NULL REFERENCES entities(entity_id),
    evidence_id TEXT NOT NULL,
    extractor_version TEXT NOT NULL,
    confidence REAL NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    validation_state TEXT NOT NULL,
    proposal_id TEXT,
    access_partition_id TEXT NOT NULL,
    FOREIGN KEY (version_id, access_partition_id)
        REFERENCES document_versions(version_id, access_partition_id),
    FOREIGN KEY (evidence_id, access_partition_id)
        REFERENCES evidence_spans(evidence_id, access_partition_id),
    PRIMARY KEY (version_id, entity_id, evidence_id)
);

CREATE INDEX idx_document_version_entities_entity
    ON document_version_entities(entity_id, version_id);

CREATE TABLE document_version_relationships (
    relationship_id TEXT PRIMARY KEY,
    version_id TEXT NOT NULL,
    subject_entity_id TEXT NOT NULL REFERENCES entities(entity_id),
    predicate TEXT NOT NULL,
    object_entity_id TEXT NOT NULL REFERENCES entities(entity_id),
    extractor_version TEXT NOT NULL,
    confidence REAL NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    validation_state TEXT NOT NULL,
    proposal_id TEXT,
    created_at TEXT NOT NULL,
    access_partition_id TEXT NOT NULL,
    FOREIGN KEY (version_id, access_partition_id)
        REFERENCES document_versions(version_id, access_partition_id),
    UNIQUE (relationship_id, access_partition_id)
);

CREATE INDEX idx_document_version_relationships_subject
    ON document_version_relationships(subject_entity_id, predicate, version_id);
CREATE INDEX idx_document_version_relationships_object
    ON document_version_relationships(object_entity_id, predicate, version_id);

CREATE TABLE document_version_relationship_evidence (
    relationship_id TEXT NOT NULL,
    evidence_id TEXT NOT NULL,
    ordinal INTEGER NOT NULL,
    access_partition_id TEXT NOT NULL,
    FOREIGN KEY (relationship_id, access_partition_id)
        REFERENCES document_version_relationships(
            relationship_id, access_partition_id
        ),
    FOREIGN KEY (evidence_id, access_partition_id)
        REFERENCES evidence_spans(evidence_id, access_partition_id),
    PRIMARY KEY (relationship_id, ordinal),
    UNIQUE (relationship_id, evidence_id)
);

CREATE TABLE index_document_versions (
    index_version TEXT NOT NULL
        REFERENCES index_versions(index_version) ON DELETE CASCADE,
    document_id TEXT NOT NULL REFERENCES documents(document_id),
    version_id TEXT NOT NULL REFERENCES document_versions(version_id),
    content_hash TEXT NOT NULL,
    access_partition_id TEXT NOT NULL
        REFERENCES access_partitions(partition_id),
    PRIMARY KEY (index_version, document_id)
);

CREATE TABLE index_document_version_embeddings (
    index_version TEXT NOT NULL
        REFERENCES index_versions(index_version) ON DELETE CASCADE,
    chunk_id TEXT NOT NULL,
    model TEXT NOT NULL,
    dimensions INTEGER NOT NULL,
    vector BLOB NOT NULL,
    vector_hash TEXT NOT NULL,
    PRIMARY KEY (index_version, chunk_id, model),
    FOREIGN KEY (chunk_id, model)
        REFERENCES document_version_embeddings(chunk_id, model)
);

CREATE TABLE index_document_version_entities (
    index_version TEXT NOT NULL
        REFERENCES index_versions(index_version) ON DELETE CASCADE,
    version_id TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    evidence_id TEXT NOT NULL,
    PRIMARY KEY (index_version, version_id, entity_id, evidence_id),
    FOREIGN KEY (version_id, entity_id, evidence_id)
        REFERENCES document_version_entities(version_id, entity_id, evidence_id)
);

CREATE TABLE index_document_version_relationships (
    index_version TEXT NOT NULL
        REFERENCES index_versions(index_version) ON DELETE CASCADE,
    relationship_id TEXT NOT NULL
        REFERENCES document_version_relationships(relationship_id),
    evidence_id TEXT NOT NULL REFERENCES evidence_spans(evidence_id),
    PRIMARY KEY (index_version, relationship_id, evidence_id)
);
""",
    10: """
ALTER TABLE collection_runs ADD COLUMN interval_from TEXT;
ALTER TABLE collection_runs ADD COLUMN interval_to TEXT;
ALTER TABLE collection_runs ADD COLUMN trigger_kind TEXT;
ALTER TABLE collection_runs ADD COLUMN spec_version INTEGER;

CREATE UNIQUE INDEX idx_collection_runs_spec_interval
    ON collection_runs(collection_spec_id, interval_from, interval_to);

CREATE TABLE collection_spec_revisions (
    collection_spec_id TEXT NOT NULL,
    spec_version INTEGER NOT NULL CHECK (spec_version > 0),
    spec_json TEXT NOT NULL,
    spec_digest TEXT NOT NULL,
    selector_digest TEXT NOT NULL,
    access_partition_id TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (collection_spec_id, access_partition_id)
        REFERENCES collection_specs(collection_spec_id, access_partition_id),
    PRIMARY KEY (collection_spec_id, spec_version),
    UNIQUE (spec_digest)
);

CREATE TABLE collection_schedule_state (
    collection_spec_id TEXT PRIMARY KEY,
    next_due_at TEXT NOT NULL,
    last_scheduled_at TEXT,
    consecutive_failures INTEGER NOT NULL DEFAULT 0,
    retry_after TEXT,
    lease_owner TEXT,
    lease_generation INTEGER NOT NULL DEFAULT 0,
    lease_expires_at TEXT,
    access_partition_id TEXT NOT NULL,
    FOREIGN KEY (collection_spec_id, access_partition_id)
        REFERENCES collection_specs(collection_spec_id, access_partition_id)
);

CREATE INDEX idx_collection_schedule_due
    ON collection_schedule_state(next_due_at, retry_after);

CREATE TABLE collection_run_triggers (
    collection_run_id TEXT NOT NULL,
    trigger_kind TEXT NOT NULL CHECK (trigger_kind IN ('timer', 'manual')),
    requested_at TEXT NOT NULL,
    access_partition_id TEXT NOT NULL,
    FOREIGN KEY (collection_run_id, access_partition_id)
        REFERENCES collection_runs(collection_run_id, access_partition_id),
    PRIMARY KEY (collection_run_id, trigger_kind)
);

CREATE TABLE collection_run_attempts (
    collection_run_id TEXT NOT NULL,
    attempt INTEGER NOT NULL CHECK (attempt > 0),
    job_id TEXT REFERENCES service_jobs(job_id),
    state TEXT NOT NULL,
    started_at TEXT NOT NULL,
    completed_at TEXT,
    error_code TEXT,
    access_partition_id TEXT NOT NULL,
    FOREIGN KEY (collection_run_id, access_partition_id)
        REFERENCES collection_runs(collection_run_id, access_partition_id),
    PRIMARY KEY (collection_run_id, attempt)
);

CREATE TABLE collection_profile_leases (
    profile_id TEXT PRIMARY KEY,
    collection_run_id TEXT NOT NULL,
    lease_owner TEXT NOT NULL,
    lease_generation INTEGER NOT NULL,
    lease_expires_at TEXT NOT NULL,
    access_partition_id TEXT NOT NULL,
    FOREIGN KEY (collection_run_id, access_partition_id)
        REFERENCES collection_runs(collection_run_id, access_partition_id)
);

CREATE INDEX idx_collection_profile_leases_expiry
    ON collection_profile_leases(lease_expires_at);

CREATE TABLE collection_source_health (
    collection_spec_id TEXT NOT NULL,
    source TEXT NOT NULL,
    process_state TEXT NOT NULL,
    yield_state TEXT NOT NULL,
    last_status TEXT NOT NULL,
    last_attempted_count INTEGER NOT NULL DEFAULT 0,
    last_observed_count INTEGER NOT NULL DEFAULT 0,
    consecutive_failures INTEGER NOT NULL DEFAULT 0,
    retry_after TEXT,
    error_code TEXT,
    updated_at TEXT NOT NULL,
    access_partition_id TEXT NOT NULL,
    FOREIGN KEY (collection_spec_id, access_partition_id)
        REFERENCES collection_specs(collection_spec_id, access_partition_id),
    PRIMARY KEY (collection_spec_id, source)
);

CREATE TABLE collection_assessment_batches (
    assessment_batch_id TEXT PRIMARY KEY,
    collection_run_id TEXT NOT NULL,
    collection_spec_id TEXT NOT NULL,
    acquisition_id TEXT,
    task_id TEXT,
    state TEXT NOT NULL,
    item_count INTEGER NOT NULL DEFAULT 0,
    error_code TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    access_partition_id TEXT NOT NULL,
    FOREIGN KEY (collection_run_id, access_partition_id)
        REFERENCES collection_runs(collection_run_id, access_partition_id),
    FOREIGN KEY (collection_spec_id, access_partition_id)
        REFERENCES collection_specs(collection_spec_id, access_partition_id),
    UNIQUE (collection_run_id, acquisition_id)
);

CREATE TABLE service_intelligence_tasks (
    task_id TEXT PRIMARY KEY,
    task_type TEXT NOT NULL,
    contract_version INTEGER NOT NULL,
    idempotency_key TEXT NOT NULL UNIQUE,
    job_id TEXT REFERENCES service_jobs(job_id),
    run_id TEXT,
    input_digest TEXT NOT NULL,
    access_partition_id TEXT NOT NULL
        REFERENCES access_partitions(partition_id),
    request_json TEXT NOT NULL,
    request_digest TEXT NOT NULL,
    state TEXT NOT NULL,
    attempt_count INTEGER NOT NULL DEFAULT 0,
    lease_owner TEXT,
    lease_generation INTEGER NOT NULL DEFAULT 0,
    lease_expires_at TEXT,
    result_json TEXT,
    output_digest TEXT,
    error_code TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX idx_service_intelligence_tasks_ready
    ON service_intelligence_tasks(state, task_type, created_at);

CREATE TABLE service_intelligence_validation_receipts (
    validation_receipt_id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL REFERENCES service_intelligence_tasks(task_id),
    accepted INTEGER NOT NULL CHECK (accepted IN (0, 1)),
    validator_codes_json TEXT NOT NULL,
    input_digest TEXT NOT NULL,
    output_digest TEXT NOT NULL,
    policy_version TEXT NOT NULL,
    validator_version TEXT NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE (task_id, output_digest, validator_version)
);

CREATE TABLE service_intelligence_promotion_receipts (
    promotion_receipt_id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL REFERENCES service_intelligence_tasks(task_id),
    validation_receipt_id TEXT NOT NULL
        REFERENCES service_intelligence_validation_receipts(validation_receipt_id),
    accepted_ids_json TEXT NOT NULL,
    rejection_codes_json TEXT NOT NULL,
    prior_authority_version TEXT,
    resulting_authority_version TEXT,
    idempotency_outcome TEXT NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE (task_id, validation_receipt_id)
);

CREATE TABLE service_intelligence_replay_receipts (
    replay_receipt_id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL REFERENCES service_intelligence_tasks(task_id),
    validation_receipt_id TEXT NOT NULL
        REFERENCES service_intelligence_validation_receipts(validation_receipt_id),
    request_digest TEXT NOT NULL,
    output_digest TEXT NOT NULL,
    policy_version TEXT NOT NULL,
    replay_state TEXT NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE (task_id, validation_receipt_id)
);
""",
}


def _connect(db_path: Optional[Path] = None) -> sqlite3.Connection:
    """Open a connection with WAL mode and row factory."""
    path = db_path or _get_db_path()
    conn = sqlite3.connect(str(path), timeout=5)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout=5000")
    deadline = time.monotonic() + 5
    while True:
        try:
            conn.execute("PRAGMA journal_mode=WAL")
            break
        except sqlite3.OperationalError as exc:
            if "locked" not in str(exc).lower() or time.monotonic() >= deadline:
                conn.close()
                raise
            time.sleep(0.01)
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db(db_path: Optional[Path] = None) -> Path:
    """Create database and tables if they don't exist. Returns the DB path."""
    path = db_path or _get_db_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    conn = _connect(path)
    try:
        conn.executescript(SCHEMA_V1)
        conn.executescript(SCHEMA_V1_DEFAULTS)
        _run_migrations(conn)
        conn.commit()
    finally:
        conn.close()

    return path


def _run_migrations(conn: sqlite3.Connection):
    """Apply pending schema migrations."""
    latest = max(MIGRATIONS, default=1)
    current = conn.execute(
        "SELECT MAX(version) FROM schema_version"
    ).fetchone()[0] or 0
    if current > latest:
        raise SchemaVersionError(
            f"database has newer schema version {current}; "
            f"this runtime supports up to {latest}"
        )

    for version in sorted(MIGRATIONS.keys()):
        try:
            conn.execute("BEGIN IMMEDIATE")
            current = conn.execute(
                "SELECT MAX(version) FROM schema_version"
            ).fetchone()[0] or 0
            if current > latest:
                raise SchemaVersionError(
                    f"database has newer schema version {current}; "
                    f"this runtime supports up to {latest}"
                )
            if version <= current:
                conn.commit()
                continue
            _execute_script_transactionally(conn, MIGRATIONS[version])
            conn.execute(
                "INSERT INTO schema_version (version) VALUES (?)", (version,)
            )
            conn.commit()
        except Exception:
            conn.rollback()
            raise


def _execute_script_transactionally(
    conn: sqlite3.Connection, script: str
) -> None:
    """Execute a SQL script without sqlite3.executescript's implicit commit."""
    statement = ""
    for line in script.splitlines():
        statement += line + "\n"
        if sqlite3.complete_statement(statement):
            sql = statement.strip()
            if sql:
                conn.execute(sql)
            statement = ""
    if statement.strip():
        raise sqlite3.OperationalError("incomplete migration SQL statement")


# --- Topics ---


def add_topic(
    name: str,
    search_queries: Optional[List[str]] = None,
    schedule: str = "0 8 * * *",
) -> Dict[str, Any]:
    """Add a topic to the watchlist. Returns the topic dict."""
    init_db()
    conn = _connect()
    try:
        queries_json = json.dumps(search_queries) if search_queries else None
        conn.execute(
            """INSERT INTO topics (name, search_queries, schedule)
               VALUES (?, ?, ?)
               ON CONFLICT(name) DO UPDATE SET
                   search_queries = excluded.search_queries,
                   schedule = excluded.schedule,
                   updated_at = datetime('now')""",
            (name, queries_json, schedule),
        )
        conn.commit()
        row = conn.execute(
            "SELECT * FROM topics WHERE name = ?", (name,)
        ).fetchone()
        return dict(row)
    finally:
        conn.close()


def remove_topic(name: str) -> bool:
    """Remove a topic from the watchlist. Returns True if found."""
    init_db()
    conn = _connect()
    try:
        row = conn.execute(
            "SELECT id FROM topics WHERE name = ?", (name,)
        ).fetchone()
        if not row:
            return False
        topic_id = row["id"]
        # Delete findings and runs for this topic
        conn.execute("DELETE FROM findings WHERE topic_id = ?", (topic_id,))
        conn.execute("DELETE FROM research_runs WHERE topic_id = ?", (topic_id,))
        conn.execute("DELETE FROM topics WHERE id = ?", (topic_id,))
        conn.commit()
        return True
    finally:
        conn.close()


def list_topics() -> List[Dict[str, Any]]:
    """List all topics with stats."""
    init_db()
    conn = _connect()
    try:
        rows = conn.execute(
            """SELECT t.*,
                      (SELECT COUNT(*) FROM findings WHERE topic_id = t.id) as finding_count,
                      (SELECT MAX(run_date) FROM research_runs WHERE topic_id = t.id) as last_run,
                      (SELECT status FROM research_runs WHERE topic_id = t.id
                       ORDER BY created_at DESC LIMIT 1) as last_status
               FROM topics t
               ORDER BY t.name"""
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_topic(name: str) -> Optional[Dict[str, Any]]:
    """Get a topic by name."""
    init_db()
    conn = _connect()
    try:
        row = conn.execute(
            "SELECT * FROM topics WHERE name = ?", (name,)
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


# --- Research Runs ---


def record_run(
    topic_id: int,
    source_mode: str = "both",
    status: str = "completed",
    error_message: Optional[str] = None,
    duration_seconds: float = 0,
    prompt_tokens: int = 0,
    completion_tokens: int = 0,
    token_cost: float = 0,
) -> int:
    """Record a research run. Returns the run ID."""
    conn = _connect()
    try:
        cursor = conn.execute(
            """INSERT INTO research_runs
               (topic_id, run_date, source_mode, status, error_message,
                duration_seconds, prompt_tokens, completion_tokens, token_cost)
               VALUES (?, datetime('now'), ?, ?, ?, ?, ?, ?, ?)""",
            (
                topic_id, source_mode, status, error_message,
                duration_seconds, prompt_tokens, completion_tokens, token_cost,
            ),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def update_run(run_id: int, **kwargs):
    """Update a research run's fields."""
    conn = _connect()
    try:
        invalid_columns = sorted(set(kwargs) - _UPDATABLE_RUN_COLUMNS)
        if invalid_columns:
            raise ValueError(
                f"Invalid run update fields: {', '.join(invalid_columns)}"
            )
        sets = ", ".join(f"{k} = ?" for k in kwargs)
        values = list(kwargs.values()) + [run_id]
        conn.execute(f"UPDATE research_runs SET {sets} WHERE id = ?", values)
        conn.commit()
    finally:
        conn.close()


def get_latest_completed_runs(topic_id: int, limit: int = 2) -> List[Dict[str, Any]]:
    """Return newest completed runs for a topic."""
    conn = _connect()
    try:
        rows = conn.execute(
            """SELECT * FROM research_runs
               WHERE topic_id = ? AND status = 'completed'
               ORDER BY id DESC
               LIMIT ?""",
            (topic_id, limit),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


# --- Findings ---


def store_findings(
    run_id: int,
    topic_id: int,
    findings: List[Dict[str, Any]],
) -> Dict[str, int]:
    """Store findings with URL-based dedup. Returns counts of new/updated."""
    # Collect findings that have a URL, preserving order.
    with_urls: List[tuple[str, Dict[str, Any]]] = []
    for f in findings:
        url = f.get("source_url") or f.get("url")
        if url:
            with_urls.append((url, f))

    if not with_urls:
        conn = _connect()
        try:
            conn.execute(
                "UPDATE research_runs SET findings_new = 0, findings_updated = 0 WHERE id = ?",
                (run_id,),
            )
            conn.commit()
        finally:
            conn.close()
        return {"new": 0, "updated": 0}

    conn = _connect()
    try:
        # Single batch SELECT to find existing findings by URL.
        urls = [url for url, _ in with_urls]
        placeholders = ",".join("?" for _ in urls)
        rows = conn.execute(
            f"SELECT id, source_url, engagement_score FROM findings WHERE source_url IN ({placeholders})",
            urls,
        ).fetchall()
        existing_by_url = {row["source_url"]: row for row in rows}

        update_rows: List[tuple] = []
        insert_rows: List[tuple] = []

        for url, f in with_urls:
            existing = existing_by_url.get(url)
            new_engagement = f.get("engagement_score", 0)
            if existing:
                update_rows.append((
                    max(new_engagement, existing["engagement_score"] or 0),
                    run_id,
                    existing["id"],
                ))
            else:
                insert_rows.append((
                    run_id,
                    topic_id,
                    f.get("source", "unknown"),
                    url,
                    f.get("source_title") or f.get("title", ""),
                    f.get("author", ""),
                    f.get("content") or f.get("text", ""),
                    f.get("summary", ""),
                    new_engagement,
                    f.get("relevance_score", 0),
                ))

        if update_rows:
            conn.executemany(
                """UPDATE findings SET
                       last_seen = datetime('now'),
                       sighting_count = sighting_count + 1,
                       engagement_score = ?,
                       run_id = ?
                   WHERE id = ?""",
                update_rows,
            )
        if insert_rows:
            conn.executemany(
                """INSERT INTO findings
                   (run_id, topic_id, source, source_url, source_title,
                    author, content, summary, engagement_score, relevance_score)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                insert_rows,
            )

        new_count = len(insert_rows)
        updated_count = len(update_rows)
        _record_sightings(conn, run_id, topic_id, with_urls, existing_by_url)
        conn.execute(
            "UPDATE research_runs SET findings_new = ?, findings_updated = ? WHERE id = ?",
            (new_count, updated_count, run_id),
        )
        conn.commit()
    finally:
        conn.close()

    return {"new": new_count, "updated": updated_count}


def _record_sightings(
    conn: sqlite3.Connection,
    run_id: int,
    topic_id: int,
    findings_with_urls: List[tuple[str, Dict[str, Any]]],
    existing_by_url: Optional[Dict[str, sqlite3.Row]] = None,
) -> None:
    """Record the findings observed during this run.

    The aggregate findings table keeps one row per URL and updates that row on
    re-sighting. This ledger preserves the run/topic membership needed for
    watchlist deltas and dossiers.
    """
    if not findings_with_urls:
        return

    by_url = {url: finding for url, finding in findings_with_urls}
    rows_by_url = dict(existing_by_url or {})

    missing_urls = [url for url in by_url if url not in rows_by_url]
    if missing_urls:
        placeholders = ",".join("?" for _ in missing_urls)
        rows = conn.execute(
            f"SELECT id, source_url FROM findings WHERE source_url IN ({placeholders})",
            missing_urls,
        ).fetchall()
        rows_by_url.update({row["source_url"]: row for row in rows})

    sighting_rows = []
    for url, finding in by_url.items():
        row = rows_by_url.get(url)
        if row is None:
            continue
        sighting_rows.append((
            row["id"],
            run_id,
            topic_id,
            finding.get("source", "unknown"),
            url,
            finding.get("source_title") or finding.get("title", ""),
            finding.get("engagement_score", 0),
            finding.get("relevance_score", 0),
        ))

    if not sighting_rows:
        return

    conn.executemany(
        """INSERT INTO finding_sightings
           (finding_id, run_id, topic_id, source, source_url, source_title,
            engagement_score, relevance_score)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)
           ON CONFLICT(run_id, finding_id) DO UPDATE SET
             topic_id = excluded.topic_id,
             source = excluded.source,
             source_url = excluded.source_url,
             source_title = excluded.source_title,
             engagement_score = excluded.engagement_score,
             relevance_score = excluded.relevance_score""",
        sighting_rows,
    )


def get_sightings_for_run(topic_id: int, run_id: int) -> List[Dict[str, Any]]:
    """Return findings observed for a topic during a specific run."""
    conn = _connect()
    try:
        rows = conn.execute(
            """SELECT * FROM finding_sightings
               WHERE topic_id = ? AND run_id = ?
               ORDER BY id""",
            (topic_id, run_id),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def compute_topic_delta(topic_id: int) -> Dict[str, Any]:
    """Compare the latest completed watchlist run with the previous run."""
    runs = get_latest_completed_runs(topic_id, limit=2)
    topic = _get_topic_by_id(topic_id)
    topic_name = topic["name"] if topic else str(topic_id)
    if len(runs) < 2:
        return {
            "topic": topic_name,
            "status": "insufficient_history",
            "message": "Need at least two completed runs to compute a delta.",
        }

    current_run, previous_run = runs[0], runs[1]
    current = _sightings_by_url(get_sightings_for_run(topic_id, current_run["id"]))
    previous = _sightings_by_url(get_sightings_for_run(topic_id, previous_run["id"]))

    current_urls = set(current)
    previous_urls = set(previous)
    new_urls = sorted(current_urls - previous_urls)
    continued_urls = sorted(current_urls & previous_urls)
    dropped_urls = sorted(previous_urls - current_urls)

    findings = {
        "new": [current[url] for url in new_urls],
        "continued": [current[url] for url in continued_urls],
        "dropped": [previous[url] for url in dropped_urls],
    }

    return {
        "topic": topic_name,
        "status": "ok",
        "current_run_id": current_run["id"],
        "previous_run_id": previous_run["id"],
        "new": len(new_urls),
        "continued": len(continued_urls),
        "dropped": len(dropped_urls),
        "sources": _delta_source_counts(findings),
        "findings": findings,
    }


def _get_topic_by_id(topic_id: int) -> Optional[Dict[str, Any]]:
    conn = _connect()
    try:
        row = conn.execute("SELECT * FROM topics WHERE id = ?", (topic_id,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def _sightings_by_url(sightings: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Index sightings by stable URL identity for run-to-run delta comparisons.

    URL-less sightings are intentionally excluded because there is no stable
    cross-run identity to classify them as new, continued, or dropped.
    """
    return {
        sighting["source_url"]: sighting
        for sighting in sightings
        if sighting.get("source_url")
    }


def _delta_source_counts(
    findings: Dict[str, List[Dict[str, Any]]]
) -> Dict[str, Dict[str, int]]:
    sources = sorted({
        finding.get("source") or "unknown"
        for group in findings.values()
        for finding in group
    })
    counts = {
        source: {"new": 0, "continued": 0, "dropped": 0}
        for source in sources
    }
    for group_name, group in findings.items():
        for finding in group:
            source = finding.get("source") or "unknown"
            counts[source][group_name] += 1
    return counts


def get_new_findings(
    topic_id: int,
    since: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Get findings for a topic, optionally since a date."""
    conn = _connect()
    try:
        if since:
            rows = conn.execute(
                """SELECT * FROM findings
                   WHERE topic_id = ? AND first_seen >= ? AND dismissed = 0
                   ORDER BY first_seen DESC""",
                (topic_id, since),
            ).fetchall()
        else:
            rows = conn.execute(
                """SELECT * FROM findings
                   WHERE topic_id = ? AND dismissed = 0
                   ORDER BY first_seen DESC""",
                (topic_id,),
            ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def search_findings(query: str, limit: int = 20) -> List[Dict[str, Any]]:
    """FTS5 search across all findings with BM25 ranking."""
    conn = _connect()
    try:
        rows = conn.execute(
            """SELECT f.*, bm25(findings_fts) as rank, t.name as topic_name
               FROM findings_fts
               JOIN findings f ON f.id = findings_fts.rowid
               LEFT JOIN topics t ON t.id = f.topic_id
               WHERE findings_fts MATCH ?
               ORDER BY rank
               LIMIT ?""",
            (query, limit),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def update_finding(finding_id: int, **kwargs):
    """Update a finding's fields."""
    conn = _connect()
    try:
        invalid_columns = sorted(set(kwargs) - _UPDATABLE_FINDING_COLUMNS)
        if invalid_columns:
            raise ValueError(
                f"Invalid finding update fields: {', '.join(invalid_columns)}"
            )
        sets = ", ".join(f"{k} = ?" for k in kwargs)
        values = list(kwargs.values()) + [finding_id]
        conn.execute(f"UPDATE findings SET {sets} WHERE id = ?", values)
        conn.commit()
    finally:
        conn.close()


def delete_finding(finding_id: int):
    """Delete a finding."""
    conn = _connect()
    try:
        conn.execute("DELETE FROM findings WHERE id = ?", (finding_id,))
        conn.commit()
    finally:
        conn.close()


def dismiss_finding(finding_id: int):
    """Mark a finding as dismissed."""
    update_finding(finding_id, dismissed=1)


# --- Cost Tracking ---


def get_daily_cost(date: Optional[str] = None) -> float:
    """Get total token cost for a given day (default: today)."""
    conn = _connect()
    try:
        if not date:
            date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        row = conn.execute(
            """SELECT COALESCE(SUM(token_cost), 0) as total
               FROM research_runs
               WHERE date(run_date) = date(?)""",
            (date,),
        ).fetchone()
        return row["total"]
    finally:
        conn.close()


# --- Settings ---


def get_setting(key: str, default: Optional[str] = None) -> Optional[str]:
    """Get a setting value."""
    init_db()
    conn = _connect()
    try:
        row = conn.execute(
            "SELECT value FROM settings WHERE key = ?", (key,)
        ).fetchone()
        return row["value"] if row else default
    finally:
        conn.close()


def set_setting(key: str, value: str):
    """Set a setting value."""
    init_db()
    conn = _connect()
    try:
        conn.execute(
            """INSERT INTO settings (key, value, updated_at)
               VALUES (?, ?, datetime('now'))
               ON CONFLICT(key) DO UPDATE SET
                   value = excluded.value,
                   updated_at = datetime('now')""",
            (key, value),
        )
        conn.commit()
    finally:
        conn.close()


# --- Stats ---


def get_stats() -> Dict[str, Any]:
    """Get overall database stats."""
    conn = _connect()
    try:
        topic_count = conn.execute("SELECT COUNT(*) FROM topics WHERE enabled = 1").fetchone()[0]
        finding_count = conn.execute("SELECT COUNT(*) FROM findings").fetchone()[0]

        week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%d")
        runs_7d = conn.execute(
            "SELECT COUNT(*) FROM research_runs WHERE run_date >= ?", (week_ago,)
        ).fetchone()[0]
        successful_7d = conn.execute(
            "SELECT COUNT(*) FROM research_runs WHERE run_date >= ? AND status = 'completed'",
            (week_ago,),
        ).fetchone()[0]
        failed_7d = conn.execute(
            "SELECT COUNT(*) FROM research_runs WHERE run_date >= ? AND status = 'failed'",
            (week_ago,),
        ).fetchone()[0]
        cost_7d = conn.execute(
            "SELECT COALESCE(SUM(token_cost), 0) FROM research_runs WHERE run_date >= ?",
            (week_ago,),
        ).fetchone()[0]

        # Source breakdown
        sources = {}
        for row in conn.execute(
            "SELECT source, COUNT(*) as cnt FROM findings GROUP BY source"
        ).fetchall():
            sources[row["source"]] = row["cnt"]

        db_path = _get_db_path()
        db_size = db_path.stat().st_size if db_path.exists() else 0

        return {
            "topics_active": topic_count,
            "total_findings": finding_count,
            "db_size_bytes": db_size,
            "runs_7d": runs_7d,
            "successful_7d": successful_7d,
            "failed_7d": failed_7d,
            "cost_7d": cost_7d,
            "sources": sources,
            "daily_budget": get_setting("daily_budget", "5.00"),
        }
    finally:
        conn.close()


def get_trending(days: int = 7) -> List[Dict[str, Any]]:
    """Get topics ranked by recent finding activity."""
    conn = _connect()
    try:
        since = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
        rows = conn.execute(
            """SELECT t.name, t.id,
                      COUNT(f.id) as new_findings,
                      COALESCE(SUM(f.engagement_score), 0) as total_engagement
               FROM topics t
               LEFT JOIN findings f ON f.topic_id = t.id AND f.first_seen >= ?
               WHERE t.enabled = 1
               GROUP BY t.id
               ORDER BY new_findings DESC""",
            (since,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def finding_from_candidate(candidate: schema.Candidate) -> Dict[str, Any]:
    """Convert a ranked candidate into a persisted finding."""
    primary_item = schema.candidate_primary_item(candidate)
    corroborating_sources = [
        source for source in schema.candidate_sources(candidate)
        if source and source != candidate.source
    ]
    summary = candidate.explanation or candidate.snippet or ""
    if corroborating_sources:
        prefix = f"Also seen in: {', '.join(corroborating_sources)}."
        summary = f"{prefix} {summary}".strip()
    body = (
        primary_item.body
        if primary_item and primary_item.body
        else candidate.snippet or candidate.title
    )
    author = primary_item.author if primary_item and primary_item.author else ""
    return {
        "source": candidate.source or "unknown",
        "source_url": candidate.url,
        "source_title": candidate.title,
        "author": author,
        "content": body,
        "summary": summary,
        "engagement_score": candidate.engagement or 0,
        "relevance_score": candidate.final_score or candidate.rerank_score or candidate.local_relevance,
    }


def findings_from_report(
    report: schema.Report,
    *,
    limit: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Convert report into persisted findings.

    Uses ranked candidates (post-rerank) when available for quality scores and explanations.
    Supplements with raw items from items_by_source for HN/PM that didn't rank highly
    but are valuable for watchlist persistence. When ranked_candidates is empty
    (degraded path — rerank failed or was skipped), falls back to supplementing
    all sources from items_by_source so findings aren't silently dropped.
    """
    findings = []
    seen_urls = set()

    for candidate in report.ranked_candidates:
        findings.append(finding_from_candidate(candidate))
        seen_urls.add(candidate.url)

    supplement_sources = (
        list(report.items_by_source)
        if not report.ranked_candidates
        else ["hackernews", "polymarket"]
    )
    for source_name in supplement_sources:
        if source_name not in report.items_by_source:
            continue
        for item in report.items_by_source[source_name]:
            if item.url in seen_urls:
                continue
            findings.append({
                "source": source_name,
                "source_url": item.url,
                "source_title": item.title,
                "author": item.author or "",
                "content": item.body or "",
                "summary": item.snippet or (item.body[:500] if item.body else ""),
                "engagement_score": item.engagement_score or 0.0,
                "relevance_score": item.local_relevance or 0.5,
            })
            seen_urls.add(item.url)

    return findings[:limit] if limit is not None else findings


# --- CLI interface ---


def _cli_query(args):
    """Handle CLI query command."""
    topic = get_topic(args.topic)
    if not topic:
        print(json.dumps({"error": f"Topic not found: {args.topic}"}))
        return

    since = None
    if args.since:
        # Parse duration like "7d", "30d". Use UTC to match SQLite's
        # datetime('now') which writes first_seen in UTC.
        days = int(args.since.rstrip("d"))
        since = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")

    findings = get_new_findings(topic["id"], since)
    print(json.dumps({"topic": topic["name"], "findings": findings, "count": len(findings)}, default=str))


def _cli_search(args):
    """Handle CLI search command."""
    results = search_findings(args.query, limit=args.limit)
    print(json.dumps({"query": args.query, "results": results, "count": len(results)}, default=str))


def _cli_trending(args):
    """Handle CLI trending command."""
    results = get_trending(args.days)
    print(json.dumps({"trending": results}, default=str))


def _cli_stats(args):
    """Handle CLI stats command."""
    stats = get_stats()
    print(json.dumps(stats, default=str))


def main():
    parser = argparse.ArgumentParser(description="Query the last30days research database")
    sub = parser.add_subparsers(dest="command")

    # query
    q = sub.add_parser("query", help="Query findings for a topic")
    q.add_argument("topic", help="Topic name")
    q.add_argument("--since", help="Duration like '7d' or '30d'")
    q.set_defaults(func=_cli_query)

    # search
    s = sub.add_parser("search", help="Full-text search across findings")
    s.add_argument("query", help="Search query")
    s.add_argument("--limit", type=int, default=20, help="Max results")
    s.set_defaults(func=_cli_search)

    # trending
    t = sub.add_parser("trending", help="Show trending topics")
    t.add_argument("--days", type=int, default=7, help="Look back N days")
    t.set_defaults(func=_cli_trending)

    # stats
    st = sub.add_parser("stats", help="Show database stats")
    st.set_defaults(func=_cli_stats)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Ensure DB exists
    init_db()
    args.func(args)


if __name__ == "__main__":
    main()
