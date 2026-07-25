"""Cache-backed hybrid retrieval over the intelligence-service schema.

The module owns projection of legacy findings into schema-v3 records and
returns transport-independent, citation-ready evidence contracts.  It does
not acquire content or invoke source adapters.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import sqlite3
import struct
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Protocol, Sequence

import store

from .service_contracts import EvidenceItem, SCHEMA_VERSION


_TOKEN_RE = re.compile(r"\w+", re.UNICODE)
_CHUNKER_VERSION = "legacy-whole-document-v1"
_TRANSFORMATION_VERSION = "legacy-finding-v1"


class EmbeddingProvider(Protocol):
    """Minimal injected embedding boundary used by indexing and querying."""

    model: str

    def embed(self, texts: Sequence[str]) -> Sequence[Sequence[float]]:
        """Return one finite vector for each input text."""


@dataclass(frozen=True)
class LocalHashEmbeddingProvider:
    """Dependency-free, deterministic local embedding baseline for the MVP."""

    model: str = "local-hash-v1"
    dimensions: int = 256
    cost_cents_per_call: int = 0

    def __post_init__(self) -> None:
        if self.dimensions < 32:
            raise ValueError("local embedding dimensions must be at least 32")

    def embed(self, texts: Sequence[str]) -> Sequence[Sequence[float]]:
        vectors: list[tuple[float, ...]] = []
        for text in texts:
            tokens = [token.casefold() for token in _TOKEN_RE.findall(text)]
            features = list(tokens)
            for token in tokens:
                padded = f"^{token}$"
                features.extend(
                    padded[index : index + 3]
                    for index in range(max(0, len(padded) - 2))
                )
            values = [0.0] * self.dimensions
            for feature in features:
                digest = hashlib.sha256(feature.encode("utf-8")).digest()
                index = int.from_bytes(digest[:4], "big") % self.dimensions
                values[index] += 1.0 if digest[4] & 1 else -1.0
            magnitude = math.sqrt(sum(value * value for value in values))
            if magnitude:
                values = [value / magnitude for value in values]
            vectors.append(tuple(values))
        return vectors


@dataclass(frozen=True)
class FusionConfig:
    """Versioned deterministic reciprocal-rank-fusion configuration."""

    version: str = "rrf-v1"
    rank_constant: int = 60
    lexical_weight: float = 1.0
    semantic_weight: float = 1.0
    graph_weight: float = 0.75
    candidate_limit: int = 100

    def __post_init__(self) -> None:
        if not self.version.strip():
            raise ValueError("fusion version must be non-empty")
        if self.rank_constant < 0:
            raise ValueError("rank_constant must not be negative")
        if (
            self.lexical_weight < 0
            or self.semantic_weight < 0
            or self.graph_weight < 0
        ):
            raise ValueError("fusion weights must not be negative")
        if (
            self.lexical_weight == 0
            and self.semantic_weight == 0
            and self.graph_weight == 0
        ):
            raise ValueError("at least one fusion weight must be positive")
        if self.candidate_limit < 1:
            raise ValueError("candidate_limit must be positive")


@dataclass(frozen=True)
class IndexingStats:
    """Observable result of projecting legacy records into the service index."""

    findings_seen: int
    documents_indexed: int
    chunks_indexed: int
    embeddings_indexed: int
    index_version: str


@dataclass(frozen=True)
class RetrievalSnapshot:
    """Evidence and the immutable index version read in one transaction."""

    index_version: str
    evidence: list[EvidenceItem]


def _sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _stable_id(prefix: str, value: str) -> str:
    return f"{prefix}-{_sha256(value)[:24]}"


def _first_nonempty(*values: object, fallback: str) -> str:
    for value in values:
        if isinstance(value, str) and value.strip():
            return value.strip()
    return fallback


def _validate_vectors(
    vectors: Sequence[Sequence[float]],
    *,
    expected_count: int,
) -> list[tuple[float, ...]]:
    if len(vectors) != expected_count:
        raise ValueError(
            f"embedding provider returned {len(vectors)} vectors "
            f"for {expected_count} texts"
        )
    validated: list[tuple[float, ...]] = []
    dimensions: int | None = None
    for vector in vectors:
        values = tuple(float(value) for value in vector)
        if not values:
            raise ValueError("embedding vectors must not be empty")
        if dimensions is None:
            dimensions = len(values)
        elif len(values) != dimensions:
            raise ValueError("embedding vectors must have consistent dimensions")
        if not all(math.isfinite(value) for value in values):
            raise ValueError("embedding vectors must contain finite values")
        validated.append(values)
    return validated


def _pack_vector(vector: Sequence[float]) -> bytes:
    return struct.pack(f"<{len(vector)}d", *vector)


def _unpack_vector(payload: bytes, dimensions: int) -> tuple[float, ...] | None:
    if dimensions < 1 or len(payload) != dimensions * 8:
        return None
    try:
        return struct.unpack(f"<{dimensions}d", payload)
    except struct.error:
        return None


def _cosine(left: Sequence[float], right: Sequence[float]) -> float | None:
    if len(left) != len(right) or not left:
        return None
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if left_norm == 0 or right_norm == 0:
        return None
    similarity = sum(a * b for a, b in zip(left, right)) / (left_norm * right_norm)
    return max(-1.0, min(1.0, similarity))


class HybridRetriever:
    """Deep retrieval interface hiding schema, FTS, vector, and fusion mechanics."""

    def __init__(
        self,
        db_path: Path,
        *,
        embedding_provider: EmbeddingProvider | None = None,
        fusion: FusionConfig = FusionConfig(),
    ) -> None:
        self.db_path = Path(db_path)
        self.embedding_provider = embedding_provider
        self.fusion = fusion

    @property
    def ranking_version(self) -> str:
        """Return the replay key for the active deterministic ranker."""

        return self.fusion.version

    def set_embedding_provider(
        self, provider: EmbeddingProvider | None
    ) -> None:
        """Configure the shared query provider after lexical startup indexing."""
        self.embedding_provider = provider

    def current_index_version(self) -> str | None:
        """Return the latest published immutable corpus/ranker snapshot."""
        conn = self._connect()
        try:
            row = conn.execute(
                """SELECT index_version
                   FROM service_index_head
                   WHERE singleton_id = 1"""
            ).fetchone()
            return row["index_version"] if row is not None else None
        finally:
            conn.close()

    def initialize(self) -> None:
        """Create or migrate the authoritative database."""

        store.init_db(self.db_path)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=5)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("PRAGMA busy_timeout=5000")
        return conn

    def index_legacy_findings(self) -> IndexingStats:
        """Idempotently project every legacy finding into v3 service records."""

        self.initialize()
        conn = self._connect()
        documents_indexed = 0
        chunks_indexed = 0
        try:
            rows = conn.execute(
                """SELECT f.*, r.run_date
                   FROM findings AS f
                   LEFT JOIN research_runs AS r ON r.id = f.run_id
                   WHERE f.source_url IS NOT NULL
                     AND trim(f.source_url) != ''
                     AND f.dismissed = 0
                   ORDER BY f.id"""
            ).fetchall()
            conn.execute("BEGIN IMMEDIATE")
            for row in rows:
                source = row["source"]
                url = row["source_url"]
                title = _first_nonempty(row["source_title"], fallback=url)
                text = _first_nonempty(
                    row["content"],
                    row["summary"],
                    title,
                    fallback=url,
                )
                fetched_at = (
                    row["last_seen"]
                    or row["first_seen"]
                    or row["run_date"]
                    or "1970-01-01T00:00:00Z"
                )
                published_at = row["first_seen"] or row["run_date"]
                finding_key = f"{row['id']}:{url}"
                job_id = _stable_id("legacy-job", str(row["run_id"] or row["id"]))
                acquisition_id = _stable_id("legacy-acq", finding_key)
                document_id = _stable_id("doc", url)
                chunk_id = _stable_id("chunk", f"{document_id}:0")
                content_hash = f"sha256:{_sha256(text)}"

                conn.execute(
                    """INSERT OR IGNORE INTO service_jobs
                       (job_id, job_type, dedupe_key, state, query_request_id,
                        attempts, max_attempts, budget_cents, created_at, updated_at)
                       VALUES (?, 'legacy_import', ?, 'published', ?, 1, 1, 0, ?, ?)""",
                    (
                        job_id,
                        f"legacy-run:{row['run_id'] or row['id']}",
                        f"legacy-query:{row['topic_id'] or 'unscoped'}",
                        fetched_at,
                        fetched_at,
                    ),
                )
                conn.execute(
                    """INSERT OR IGNORE INTO acquisitions
                       (acquisition_id, job_id, profile_id, source, adapter,
                        adapter_version, query_text, status, observed_at, fetched_at,
                        content_hash, retention_class, redaction_class, item_count)
                       VALUES (?, ?, 'legacy', ?, 'legacy_store', '1', ?,
                               'succeeded', ?, ?, ?, 'cache', 'public', 1)""",
                    (
                        acquisition_id,
                        job_id,
                        source,
                        title,
                        fetched_at,
                        fetched_at,
                        content_hash,
                    ),
                )
                inserted = conn.execute(
                    """INSERT OR IGNORE INTO documents
                       (document_id, acquisition_id, source, source_native_id,
                        canonical_url, title, author, normalized_text, content_hash,
                        published_at, fetched_at, retention_class, redaction_class,
                        transformation_version)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                               'cache', 'public', ?)""",
                    (
                        document_id,
                        acquisition_id,
                        source,
                        f"legacy-finding-{row['id']}",
                        url,
                        title,
                        row["author"],
                        text,
                        content_hash,
                        published_at,
                        fetched_at,
                        _TRANSFORMATION_VERSION,
                    ),
                ).rowcount
                documents_indexed += inserted
                inserted_chunk = conn.execute(
                    """INSERT OR IGNORE INTO document_chunks
                       (chunk_id, document_id, ordinal, text, content_hash,
                        chunker_version)
                       VALUES (?, ?, 0, ?, ?, ?)""",
                    (
                        chunk_id,
                        document_id,
                        text,
                        content_hash,
                        _CHUNKER_VERSION,
                    ),
                ).rowcount
                chunks_indexed += inserted_chunk
                conn.execute(
                    """INSERT OR IGNORE INTO document_sightings
                       (document_id, acquisition_id, topic_id, observed_at)
                       VALUES (?, ?, ?, ?)""",
                    (document_id, acquisition_id, row["topic_id"], fetched_at),
                )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

        embeddings_indexed = self.embed_pending_chunks()
        index_version = self._publish_index()
        return IndexingStats(
            findings_seen=len(rows),
            documents_indexed=documents_indexed,
            chunks_indexed=chunks_indexed,
            embeddings_indexed=embeddings_indexed,
            index_version=index_version,
        )

    def _publish_index(self) -> str:
        """Publish a content-addressed corpus/ranker manifest for replay."""
        conn = self._connect()
        try:
            documents = conn.execute(
                """SELECT document_id, content_hash
                   FROM documents
                   ORDER BY document_id"""
            ).fetchall()
            chunk_count = conn.execute(
                "SELECT COUNT(*) FROM document_chunks"
            ).fetchone()[0]
            embedding_model = (
                self.embedding_provider.model
                if self.embedding_provider is not None
                else None
            )
            embedding_rows = (
                conn.execute(
                    """SELECT chunk_id, model, dimensions, vector
                       FROM chunk_embeddings
                       WHERE model = ?
                       ORDER BY chunk_id, model""",
                    (embedding_model,),
                ).fetchall()
                if embedding_model is not None
                else []
            )
            entity_rows = conn.execute(
                """SELECT document_id, entity_id, evidence_chunk_id, evidence_start
                   FROM document_entities
                   WHERE validation_state = 'accepted'
                   ORDER BY document_id, entity_id, evidence_chunk_id,
                            evidence_start"""
            ).fetchall()
            alias_rows = conn.execute(
                """SELECT DISTINCT ea.normalized_alias, ea.entity_id
                   FROM entity_aliases AS ea
                   JOIN document_entities AS de ON de.entity_id = ea.entity_id
                   WHERE de.validation_state = 'accepted'
                   ORDER BY ea.normalized_alias, ea.entity_id"""
            ).fetchall()
            relationship_rows = conn.execute(
                """SELECT r.relationship_id, r.subject_entity_id, r.predicate,
                          r.object_entity_id, re.evidence_chunk_id,
                          re.evidence_start, re.evidence_end, re.span_hash,
                          r.confidence
                   FROM relationships AS r
                   JOIN relationship_evidence AS re
                     ON re.relationship_id = r.relationship_id
                    AND re.ordinal = 0
                   WHERE r.validation_state = 'accepted'
                   ORDER BY r.relationship_id"""
            ).fetchall()
            ranking_config = {
                "version": self.fusion.version,
                "rank_constant": self.fusion.rank_constant,
                "lexical_weight": self.fusion.lexical_weight,
                "semantic_weight": self.fusion.semantic_weight,
                "graph_weight": self.fusion.graph_weight,
                "candidate_limit": self.fusion.candidate_limit,
            }
            embedding_manifest = [
                [
                    row["chunk_id"],
                    row["model"],
                    row["dimensions"],
                    row["vector"].hex(),
                    hashlib.sha256(row["vector"]).hexdigest(),
                ]
                for row in embedding_rows
            ]
            graph_manifest = {
                "entities": [
                    [
                        row["document_id"],
                        row["entity_id"],
                        row["evidence_chunk_id"],
                        row["evidence_start"],
                    ]
                    for row in entity_rows
                ],
                "aliases": [
                    [row["normalized_alias"], row["entity_id"]]
                    for row in alias_rows
                ],
                "relationships": [
                    [
                        row["relationship_id"],
                        row["subject_entity_id"],
                        row["predicate"],
                        row["object_entity_id"],
                        row["evidence_chunk_id"],
                        row["evidence_start"],
                        row["evidence_end"],
                        row["span_hash"],
                        row["confidence"],
                    ]
                    for row in relationship_rows
                ],
            }
            embedding_manifest_json = json.dumps(
                embedding_manifest,
                ensure_ascii=False,
                separators=(",", ":"),
                sort_keys=True,
            )
            graph_manifest_json = json.dumps(
                graph_manifest,
                ensure_ascii=False,
                separators=(",", ":"),
                sort_keys=True,
            )
            embedding_manifest_hash = (
                _sha256(embedding_manifest_json) if embedding_manifest else None
            )
            graph_manifest_hash = (
                _sha256(graph_manifest_json)
                if entity_rows or alias_rows or relationship_rows
                else None
            )
            manifest = {
                "documents": [
                    [row["document_id"], row["content_hash"]]
                    for row in documents
                ],
                "embedding_model": embedding_model,
                "embeddings": embedding_manifest,
                "graph": graph_manifest,
                "ranking": ranking_config,
            }
            manifest_json = json.dumps(
                manifest,
                ensure_ascii=False,
                allow_nan=False,
                separators=(",", ":"),
                sort_keys=True,
            )
            index_version = f"index-{_sha256(manifest_json)[:24]}"
            now = datetime.now(timezone.utc).isoformat()
            conn.execute("BEGIN IMMEDIATE")
            conn.execute(
                """INSERT OR IGNORE INTO index_versions
                   (index_version, parent_version, ranking_config_json,
                    document_count, chunk_count, embedding_model,
                    created_at, published_at, embedding_manifest_hash,
                    graph_manifest_hash)
                   VALUES (?, NULL, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    index_version,
                    json.dumps(
                        ranking_config,
                        allow_nan=False,
                        separators=(",", ":"),
                        sort_keys=True,
                    ),
                    len(documents),
                    chunk_count,
                    embedding_model,
                    now,
                    now,
                    embedding_manifest_hash,
                    graph_manifest_hash,
                ),
            )
            conn.executemany(
                """INSERT OR IGNORE INTO index_documents
                   (index_version, document_id, content_hash)
                   VALUES (?, ?, ?)""",
                [
                    (index_version, row["document_id"], row["content_hash"])
                    for row in documents
                ],
            )
            conn.executemany(
                """INSERT OR IGNORE INTO index_chunk_embeddings
                   (index_version, chunk_id, model, dimensions, vector, vector_hash)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                [
                    (
                        index_version,
                        chunk_id,
                        model,
                        dimensions,
                        bytes.fromhex(vector_hex),
                        vector_hash,
                    )
                    for chunk_id, model, dimensions, vector_hex, vector_hash
                    in embedding_manifest
                ],
            )
            conn.executemany(
                """INSERT OR IGNORE INTO index_entity_aliases
                   (index_version, normalized_alias, entity_id)
                   VALUES (?, ?, ?)""",
                [
                    (
                        index_version,
                        row["normalized_alias"],
                        row["entity_id"],
                    )
                    for row in alias_rows
                ],
            )
            conn.executemany(
                """INSERT OR IGNORE INTO index_document_entities
                   (index_version, document_id, entity_id, evidence_chunk_id,
                    evidence_start)
                   VALUES (?, ?, ?, ?, ?)""",
                [
                    (
                        index_version,
                        row["document_id"],
                        row["entity_id"],
                        row["evidence_chunk_id"],
                        row["evidence_start"],
                    )
                    for row in entity_rows
                ],
            )
            conn.executemany(
                """INSERT OR IGNORE INTO index_relationships
                   (index_version, relationship_id, subject_entity_id, predicate,
                    object_entity_id, evidence_chunk_id, evidence_start,
                    evidence_end, span_hash, confidence)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                [
                    (
                        index_version,
                        row["relationship_id"],
                        row["subject_entity_id"],
                        row["predicate"],
                        row["object_entity_id"],
                        row["evidence_chunk_id"],
                        row["evidence_start"],
                        row["evidence_end"],
                        row["span_hash"],
                        row["confidence"],
                    )
                    for row in relationship_rows
                ],
            )
            conn.execute(
                """INSERT INTO service_index_head
                   (singleton_id, index_version, activated_at)
                   VALUES (1, ?, ?)
                   ON CONFLICT(singleton_id) DO UPDATE SET
                       index_version = excluded.index_version,
                       activated_at = excluded.activated_at""",
                (index_version, now),
            )
            conn.commit()
            return index_version
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def publish_index(self) -> str:
        """Publish and return the content-addressed current corpus snapshot."""
        return self._publish_index()

    def embed_pending_chunks(self) -> int:
        """Embed chunks missing the configured model, returning the insert count."""

        provider = self.embedding_provider
        if provider is None:
            return 0
        model = provider.model
        if not isinstance(model, str) or not model.strip():
            raise ValueError("embedding provider model must be a non-empty string")

        conn = self._connect()
        try:
            rows = conn.execute(
                """SELECT c.chunk_id, c.text
                   FROM document_chunks AS c
                   LEFT JOIN chunk_embeddings AS e
                     ON e.chunk_id = c.chunk_id AND e.model = ?
                   WHERE e.chunk_id IS NULL
                   ORDER BY c.chunk_id""",
                (model,),
            ).fetchall()
            if not rows:
                return 0
            vectors = _validate_vectors(
                provider.embed([row["text"] for row in rows]),
                expected_count=len(rows),
            )
            created_at = datetime.now(timezone.utc).isoformat()
            conn.execute("BEGIN IMMEDIATE")
            inserted = 0
            for row, vector in zip(rows, vectors):
                inserted += conn.execute(
                    """INSERT OR IGNORE INTO chunk_embeddings
                       (chunk_id, model, dimensions, vector, created_at)
                       VALUES (?, ?, ?, ?, ?)""",
                    (
                        row["chunk_id"],
                        model,
                        len(vector),
                        _pack_vector(vector),
                        created_at,
                    ),
                ).rowcount
            conn.commit()
            return inserted
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def search(
        self,
        query: str,
        *,
        sources: Sequence[str] | None = None,
        top_k: int = 8,
        snippet_chars: int = 320,
    ) -> list[EvidenceItem]:
        """Return evidence from one immutable published index snapshot."""
        return self.search_snapshot(
            query,
            sources=sources,
            top_k=top_k,
            snippet_chars=snippet_chars,
        ).evidence

    def search_snapshot(
        self,
        query: str,
        *,
        sources: Sequence[str] | None = None,
        top_k: int = 8,
        snippet_chars: int = 320,
    ) -> RetrievalSnapshot:
        """Return deterministic hits and their exact published index version."""

        if top_k < 1:
            raise ValueError("top_k must be positive")
        if snippet_chars < 32:
            raise ValueError("snippet_chars must be at least 32")
        terms = _TOKEN_RE.findall(query)
        if not terms:
            return RetrievalSnapshot(
                self.current_index_version() or "index-empty",
                [],
            )
        match_query = " OR ".join(f'"{term.replace(chr(34), chr(34) * 2)}"' for term in terms)
        source_values = tuple(dict.fromkeys(sources or ()))

        where_source = ""
        params: list[object] = [match_query]
        if source_values:
            placeholders = ",".join("?" for _ in source_values)
            where_source = f" AND d.source IN ({placeholders})"
            params.extend(source_values)
        params.append(min(self.fusion.candidate_limit, max(top_k, 1) * 10))

        conn = self._connect()
        try:
            conn.execute("BEGIN")
            index_row = conn.execute(
                """SELECT index_version
                   FROM service_index_head
                   WHERE singleton_id = 1"""
            ).fetchone()
            if index_row is None:
                return RetrievalSnapshot("index-empty", [])
            index_version = index_row["index_version"]
            params.insert(0, index_version)
            lexical_rows = conn.execute(
                f"""SELECT d.*, c.chunk_id, c.text AS chunk_text,
                           bm25(documents_fts, 3.0, 1.0, 1.0) AS lexical_bm25
                    FROM documents_fts
                    JOIN documents AS d ON d.rowid = documents_fts.rowid
                    JOIN index_documents AS ix
                      ON ix.document_id = d.document_id
                     AND ix.index_version = ?
                    JOIN document_chunks AS c
                      ON c.document_id = d.document_id AND c.ordinal = 0
                    WHERE documents_fts MATCH ?{where_source}
                    ORDER BY lexical_bm25, d.document_id
                    LIMIT ?""",
                params,
            ).fetchall()

            semantic_rows: list[sqlite3.Row] = []
            query_vector: tuple[float, ...] | None = None
            if self.embedding_provider is not None:
                try:
                    query_vector = _validate_vectors(
                        self.embedding_provider.embed([query]),
                        expected_count=1,
                    )[0]
                    semantic_params: list[object] = [
                        index_version,
                        self.embedding_provider.model,
                    ]
                    semantic_source = ""
                    if source_values:
                        placeholders = ",".join("?" for _ in source_values)
                        semantic_source = f" AND d.source IN ({placeholders})"
                        semantic_params.extend(source_values)
                    semantic_rows = conn.execute(
                        f"""SELECT d.*, c.chunk_id, c.text AS chunk_text,
                                   ie.dimensions, ie.vector
                            FROM index_chunk_embeddings AS ie
                            JOIN document_chunks AS c ON c.chunk_id = ie.chunk_id
                            JOIN documents AS d ON d.document_id = c.document_id
                            JOIN index_documents AS ix
                              ON ix.document_id = d.document_id
                             AND ix.index_version = ie.index_version
                            WHERE ie.index_version = ?
                              AND ie.model = ?{semantic_source}
                            ORDER BY d.document_id, c.ordinal""",
                        semantic_params,
                    ).fetchall()
                except Exception:
                    query_vector = None
                    semantic_rows = []

            graph_rows: list[sqlite3.Row] = []
            graph_scores: dict[str, float] = {}
            try:
                normalized_values = tuple(
                    dict.fromkeys(
                        [
                            " ".join(query.split()).casefold(),
                            *(term.casefold() for term in terms),
                        ]
                    )
                )[:4]
                seed_ids: list[str] = []
                for normalized in normalized_values:
                    matches = conn.execute(
                        """SELECT DISTINCT entity_id
                           FROM index_entity_aliases
                           WHERE index_version = ?
                             AND normalized_alias = ?
                           ORDER BY entity_id""",
                        (index_version, normalized),
                    ).fetchall()
                    unique = tuple(
                        dict.fromkeys(row["entity_id"] for row in matches)
                    )
                    if len(unique) == 1:
                        seed_ids.append(unique[0])
                seed_ids = list(dict.fromkeys(seed_ids))[:4]
                if seed_ids:
                    seed_placeholders = ",".join("?" for _ in seed_ids)
                    graph_source = ""
                    graph_params: list[object] = [
                        index_version,
                        index_version,
                        *seed_ids,
                        *seed_ids,
                    ]
                    if source_values:
                        source_placeholders = ",".join(
                            "?" for _ in source_values
                        )
                        graph_source = (
                            f" AND d.source IN ({source_placeholders})"
                        )
                        graph_params.extend(source_values)
                    graph_params.append(
                        min(32, self.fusion.candidate_limit)
                    )
                    graph_rows = conn.execute(
                        f"""SELECT d.*, c.chunk_id, c.text AS chunk_text,
                                   ir.confidence AS graph_confidence,
                                   ir.relationship_id
                            FROM index_relationships AS ir
                            JOIN document_chunks AS c
                              ON c.chunk_id = ir.evidence_chunk_id
                            JOIN documents AS d
                              ON d.document_id = c.document_id
                            JOIN index_documents AS ix
                              ON ix.document_id = d.document_id
                             AND ix.index_version = ?
                            WHERE ir.index_version = ?
                              AND (
                                  ir.subject_entity_id IN ({seed_placeholders})
                                  OR ir.object_entity_id IN ({seed_placeholders})
                              ){graph_source}
                            ORDER BY ir.confidence DESC, ir.relationship_id,
                                     d.document_id
                            LIMIT ?""",
                        graph_params,
                    ).fetchall()
                    for row in graph_rows:
                        document_id = row["document_id"]
                        graph_scores[document_id] = max(
                            graph_scores.get(document_id, 0.0),
                            float(row["graph_confidence"]),
                        )
            except sqlite3.Error:
                graph_rows = []
                graph_scores = {}
        finally:
            conn.close()

        candidates: dict[str, sqlite3.Row] = {}
        lexical_ranks: dict[str, int] = {}
        for rank, row in enumerate(lexical_rows, start=1):
            candidates[row["document_id"]] = row
            lexical_ranks[row["document_id"]] = rank

        semantic_scores: dict[str, float] = {}
        semantic_candidate_rows: dict[str, sqlite3.Row] = {}
        if query_vector is not None:
            for row in semantic_rows:
                vector = _unpack_vector(row["vector"], row["dimensions"])
                similarity = _cosine(query_vector, vector) if vector is not None else None
                if similarity is None or similarity <= 0:
                    continue
                document_id = row["document_id"]
                previous = semantic_scores.get(document_id)
                if previous is None or similarity > previous:
                    semantic_scores[document_id] = similarity
                    semantic_candidate_rows[document_id] = row
            semantic_order = sorted(
                semantic_scores,
                key=lambda document_id: (
                    -semantic_scores[document_id],
                    document_id,
                ),
            )[: self.fusion.candidate_limit]
            semantic_ranks = {
                document_id: rank
                for rank, document_id in enumerate(semantic_order, start=1)
            }
            for document_id in semantic_order:
                candidates.setdefault(document_id, semantic_candidate_rows[document_id])
        else:
            semantic_ranks = {}

        graph_ranks: dict[str, int] = {}
        for row in graph_rows:
            candidates.setdefault(row["document_id"], row)
        graph_order = sorted(
            graph_scores,
            key=lambda document_id: (
                -graph_scores[document_id],
                document_id,
            ),
        )
        graph_ranks = {
            document_id: rank
            for rank, document_id in enumerate(graph_order, start=1)
        }

        maximum_fused = 0.0
        if lexical_ranks:
            maximum_fused += self.fusion.lexical_weight / (
                self.fusion.rank_constant + 1
            )
        if semantic_ranks:
            maximum_fused += self.fusion.semantic_weight / (
                self.fusion.rank_constant + 1
            )
        if graph_ranks:
            maximum_fused += self.fusion.graph_weight / (
                self.fusion.rank_constant + 1
            )

        ranked: list[tuple[float, float, int, str, sqlite3.Row]] = []
        for document_id, row in candidates.items():
            fused_raw = 0.0
            lexical_rank = lexical_ranks.get(document_id)
            if lexical_rank is not None:
                fused_raw += self.fusion.lexical_weight / (
                    self.fusion.rank_constant + lexical_rank
                )
            semantic_rank = semantic_ranks.get(document_id)
            if semantic_rank is not None:
                fused_raw += self.fusion.semantic_weight / (
                    self.fusion.rank_constant + semantic_rank
                )
            graph_rank = graph_ranks.get(document_id)
            if graph_rank is not None:
                fused_raw += self.fusion.graph_weight / (
                    self.fusion.rank_constant + graph_rank
                )
            ranked.append(
                (
                    fused_raw / maximum_fused if maximum_fused else 0.0,
                    semantic_scores.get(document_id, 0.0),
                    lexical_rank or 2_147_483_647,
                    document_id,
                    row,
                )
            )
        ranked.sort(key=lambda item: (-item[0], -item[1], item[2], item[3]))

        hits: list[EvidenceItem] = []
        for fused, semantic, lexical_rank, _, row in ranked[:top_k]:
            lexical = 0.0 if lexical_rank == 2_147_483_647 else 1.0 / lexical_rank
            text = row["chunk_text"].strip()
            snippet = text if len(text) <= snippet_chars else text[: snippet_chars - 1].rstrip() + "…"
            hits.append(
                EvidenceItem(
                    schema_version=SCHEMA_VERSION,
                    evidence_id=_stable_id(
                        "evidence", f"{row['document_id']}:{row['chunk_id']}"
                    ),
                    document_id=row["document_id"],
                    source=row["source"],
                    source_native_id=row["source_native_id"],
                    url=row["canonical_url"],
                    title=row["title"],
                    snippet=snippet,
                    author=row["author"],
                    published_at=row["published_at"],
                    fetched_at=row["fetched_at"],
                    acquisition_id=row["acquisition_id"],
                    content_hash=row["content_hash"],
                    scores={
                        "lexical": min(1.0, lexical),
                        "semantic": max(0.0, min(1.0, semantic)),
                        "graph": max(
                            0.0,
                            min(1.0, graph_scores.get(row["document_id"], 0.0)),
                        ),
                        "recency": 0.0,
                        "fused": max(0.0, min(1.0, fused)),
                    },
                    media=json.loads(row["media_json"]),
                )
            )
        return RetrievalSnapshot(index_version, hits)
