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

CREATE TABLE IF NOT EXISTS index_documents (
    index_version TEXT NOT NULL REFERENCES index_versions(index_version) ON DELETE CASCADE,
    document_id TEXT NOT NULL REFERENCES documents(document_id) ON DELETE CASCADE,
    content_hash TEXT NOT NULL,
    PRIMARY KEY (index_version, document_id)
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
}


def _connect(db_path: Optional[Path] = None) -> sqlite3.Connection:
    """Open a connection with WAL mode and row factory."""
    path = db_path or _get_db_path()
    conn = sqlite3.connect(str(path), timeout=5)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout=5000")
    conn.execute("PRAGMA journal_mode=WAL")
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
