"""Host-owned validation and publication of acquisition worker proposals."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from . import service_contracts as contracts
from .service_retrieval import HybridRetriever
from .service_store import EnvelopeConflictError, ServiceStore
from .service_temporal import access_partition_id, stable_temporal_id


_BROWSER_SOURCES = frozenset({"x", "facebook", "linkedin"})


def _digest(value: object) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return f"sha256:{hashlib.sha256(encoded).hexdigest()}"


def _stable_id(namespace: str, value: str) -> str:
    digest = hashlib.sha256(f"{namespace}:{value}".encode("utf-8")).hexdigest()
    return f"{namespace}-{digest[:32]}"


def _media_from_metadata(metadata: dict[str, object]) -> list[dict[str, object]]:
    raw = metadata.get("media")
    if not isinstance(raw, list):
        return []
    return contracts._validate_media(raw)


@dataclass(frozen=True)
class PublicationStats:
    acquisition_inserted: bool
    documents_inserted: int
    chunks_inserted: int
    sightings_inserted: int
    stored_count: int
    deduplicated_count: int


@dataclass(frozen=True)
class CorpusEvidenceSnapshot:
    document_count: int
    embedding_count: int
    index_version: str | None

    def to_dict(self) -> dict[str, object]:
        return {
            "document_count": self.document_count,
            "embedding_count": self.embedding_count,
            "index_version": self.index_version,
        }


class PublicationLeaseError(RuntimeError):
    """Raised when a result no longer belongs to the live acquisition lease."""


class CorpusPublisher:
    """Deep module owning envelope validation, corpus projection, and snapshots."""

    def __init__(
        self,
        db_path: Path,
        retriever: HybridRetriever,
        *,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self.db_path = Path(db_path)
        self.retriever = retriever
        self.ledger = ServiceStore(self.db_path)
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    def evidence_snapshot(self) -> CorpusEvidenceSnapshot:
        conn = self._connect()
        try:
            document_count = int(
                conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
            )
            head = conn.execute(
                "SELECT index_version FROM service_index_head WHERE singleton_id = 1"
            ).fetchone()
            index_version = str(head["index_version"]) if head is not None else None
            embedding_count = (
                int(
                    conn.execute(
                        "SELECT COUNT(*) FROM index_chunk_embeddings "
                        "WHERE index_version = ?",
                        (index_version,),
                    ).fetchone()[0]
                )
                if index_version is not None
                else 0
            )
            return CorpusEvidenceSnapshot(
                document_count=document_count,
                embedding_count=embedding_count,
                index_version=index_version,
            )
        finally:
            conn.close()

    def indexed_item_count(self, acquisition_id: str, index_version: str) -> int:
        conn = self._connect()
        try:
            return int(
                conn.execute(
                    """SELECT COUNT(DISTINCT dvs.version_id)
                       FROM document_version_sightings AS dvs
                       JOIN index_document_versions AS iv
                         ON iv.version_id = dvs.version_id
                        AND iv.index_version = ?
                       WHERE dvs.acquisition_id = ?""",
                    (index_version, acquisition_id),
                ).fetchone()[0]
            )
        finally:
            conn.close()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=5)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("PRAGMA busy_timeout=5000")
        return conn

    def _now(self) -> str:
        value = self._clock()
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("clock must return a timezone-aware datetime")
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")

    def _put_envelope(
        self,
        conn: sqlite3.Connection,
        contract_name: str,
        envelope_id: str,
        envelope: contracts.ContractEnvelope,
    ) -> None:
        payload_json, digest = self.ledger._canonical_payload(envelope)
        existing = conn.execute(
            """SELECT payload_sha256 FROM service_envelopes
               WHERE envelope_type = ? AND envelope_id = ?""",
            (contract_name, envelope_id),
        ).fetchone()
        if existing is not None:
            if existing["payload_sha256"] != digest:
                raise EnvelopeConflictError(
                    f"immutable envelope conflict: {contract_name}/{envelope_id}"
                )
            return
        conn.execute(
            """INSERT INTO service_envelopes
               (envelope_type, envelope_id, schema_version,
                payload_json, payload_sha256)
               VALUES (?, ?, ?, ?, ?)""",
            (
                contract_name,
                envelope_id,
                envelope.schema_version,
                payload_json,
                digest,
            ),
        )

    @staticmethod
    def _assert_live_lease(
        conn: sqlite3.Connection,
        request: contracts.AcquisitionWorkRequest,
        *,
        worker_id: str,
        now: str,
    ) -> None:
        row = conn.execute(
            """SELECT state, lease_owner, lease_generation, lease_expires_at
               FROM service_jobs WHERE job_id = ?""",
            (request.job_id,),
        ).fetchone()
        if (
            row is None
            or row["state"] != contracts.JobState.ACQUIRING.value
            or row["lease_owner"] != worker_id
            or row["lease_generation"] != request.lease_generation
            or row["lease_expires_at"] is None
            or row["lease_expires_at"] <= now
        ):
            raise PublicationLeaseError("acquisition result lease is no longer current")

    @staticmethod
    def _assert_matching(
        request: contracts.AcquisitionWorkRequest,
        result: contracts.AcquisitionWorkResult,
    ) -> None:
        expected = (
            request.work_id,
            request.job_id,
            request.lease_generation,
            request.source,
            request.adapter,
            request.adapter_version,
        )
        observed = (
            result.work_id,
            result.job_id,
            result.lease_generation,
            result.source,
            result.adapter,
            result.adapter_version,
        )
        if observed != expected:
            raise contracts.ContractValidationError(
                "acquisition result does not match its work request"
            )
        if result.item_count > request.item_limit:
            raise contracts.ContractValidationError(
                "acquisition result exceeds its item limit"
            )
        if result.cost_cents > request.cost_budget_cents:
            raise contracts.ContractValidationError(
                "acquisition result exceeds its cost limit"
            )

    def record_result(
        self,
        request: contracts.AcquisitionWorkRequest,
        result: contracts.AcquisitionWorkResult,
        *,
        worker_id: str,
        retention_class: str | None = None,
        redaction_class: str | None = None,
    ) -> PublicationStats:
        """Ledger one result and idempotently project its validated content."""
        self._assert_matching(request, result)
        content_hash = _digest([item.to_dict() for item in result.items])
        classification = contracts.RedactionClass(
            redaction_class
            or (
                contracts.RedactionClass.AUTHENTICATED.value
                if result.source in _BROWSER_SOURCES
                else contracts.RedactionClass.PUBLIC.value
            )
        )
        retention = contracts.RetentionClass(
            retention_class or contracts.RetentionClass.CACHE.value
        )
        acquisition = contracts.AcquisitionEnvelope.from_dict(
            {
                "schema_version": contracts.SCHEMA_VERSION,
                "acquisition_id": result.work_id,
                "job_id": result.job_id,
                "profile_id": request.profile_id,
                "source": result.source,
                "adapter": result.adapter,
                "adapter_version": result.adapter_version,
                "query": request.query,
                "status": result.status.value,
                "observed_at": result.observed_at,
                "fetched_at": result.fetched_at,
                "artifact_ref": (
                    f"service-envelope:{result.CONTRACT_NAME}/{result.work_id}"
                ),
                "content_hash": content_hash,
                "retention_class": retention.value,
                "redaction_class": classification.value,
                "item_count": result.item_count,
                "diagnostics_ref": (
                    f"service-envelope:{result.CONTRACT_NAME}/{result.work_id}"
                ),
            }
        )
        conn = self._connect()
        documents_inserted = 0
        chunks_inserted = 0
        sightings_inserted = 0
        try:
            conn.execute("BEGIN IMMEDIATE")
            self._assert_live_lease(
                conn,
                request,
                worker_id=worker_id,
                now=self._now(),
            )
            self._put_envelope(
                conn, request.CONTRACT_NAME, request.work_id, request
            )
            self._put_envelope(
                conn, result.CONTRACT_NAME, result.work_id, result
            )
            self._put_envelope(
                conn,
                acquisition.CONTRACT_NAME,
                acquisition.acquisition_id,
                acquisition,
            )
            acquisition_inserted = bool(
                conn.execute(
                    """INSERT OR IGNORE INTO acquisitions
                       (acquisition_id, job_id, profile_id, source, adapter,
                        adapter_version, query_text, status, observed_at, fetched_at,
                        artifact_ref, content_hash, retention_class, redaction_class,
                        item_count, diagnostics_ref)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        acquisition.acquisition_id,
                        acquisition.job_id,
                        acquisition.profile_id,
                        acquisition.source,
                        acquisition.adapter,
                        acquisition.adapter_version,
                        acquisition.query,
                        acquisition.status.value,
                        acquisition.observed_at,
                        acquisition.fetched_at,
                        acquisition.artifact_ref,
                        acquisition.content_hash,
                        acquisition.retention_class.value,
                        acquisition.redaction_class.value,
                        acquisition.item_count,
                        acquisition.diagnostics_ref,
                    ),
                ).rowcount
            )
            partition_id = access_partition_id(
                classification.value, acquisition.profile_id
            )
            conn.execute(
                """INSERT OR IGNORE INTO access_partitions (
                       partition_id, partition_kind, profile_id, created_at
                   ) VALUES (?, ?, ?, ?)""",
                (
                    partition_id,
                    (
                        "public"
                        if classification is contracts.RedactionClass.PUBLIC
                        else "authenticated"
                    ),
                    (
                        None
                        if classification is contracts.RedactionClass.PUBLIC
                        else acquisition.profile_id
                    ),
                    acquisition.fetched_at,
                ),
            )
            collection = conn.execute(
                """SELECT collection_spec_id, collection_run_id,
                          access_partition_id
                   FROM collection_runs
                   WHERE job_id = ?
                   ORDER BY scheduled_for, collection_run_id
                   LIMIT 1""",
                (result.job_id,),
            ).fetchone()
            if (
                collection is not None
                and collection["access_partition_id"] != partition_id
            ):
                raise RuntimeError("collection run access partition conflict")
            for item in result.items:
                proposed_document_id = _stable_id(
                    "doc", f"{result.source}:{item.url}"
                )
                item_hash = _digest(item.to_dict())
                metadata_json = json.dumps(
                    item.metadata,
                    ensure_ascii=False,
                    allow_nan=False,
                    separators=(",", ":"),
                    sort_keys=True,
                )
                media_json = json.dumps(
                    _media_from_metadata(item.metadata),
                    ensure_ascii=False,
                    allow_nan=False,
                    separators=(",", ":"),
                    sort_keys=True,
                )
                row = conn.execute(
                    """SELECT document_id, content_hash, current_version_id
                       FROM documents
                       WHERE canonical_url = ?
                          OR (source = ? AND source_native_id = ?)
                       ORDER BY CASE WHEN canonical_url = ? THEN 0 ELSE 1 END
                       LIMIT 1""",
                    (
                        item.url,
                        result.source,
                        item.source_native_id,
                        item.url,
                    ),
                ).fetchone()
                inserted = 0
                if row is None:
                    inserted = conn.execute(
                    """INSERT OR IGNORE INTO documents
                       (document_id, acquisition_id, source, source_native_id,
                        canonical_url, title, author, normalized_text, content_hash,
                        published_at, fetched_at, retention_class, redaction_class,
                        transformation_version, source_metadata_json, media_json,
                        access_partition_id)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        proposed_document_id,
                        acquisition.acquisition_id,
                        result.source,
                        item.source_native_id,
                        item.url,
                        item.title,
                        item.author,
                        item.text,
                        item_hash,
                        item.published_at,
                        result.fetched_at,
                        retention.value,
                        classification.value,
                        "service-worker-v1",
                        metadata_json,
                        media_json,
                        partition_id,
                    ),
                    ).rowcount
                documents_inserted += inserted
                row = conn.execute(
                    """SELECT document_id, content_hash, current_version_id
                       FROM documents
                       WHERE canonical_url = ?
                          OR (source = ? AND source_native_id = ?)
                       ORDER BY CASE WHEN canonical_url = ? THEN 0 ELSE 1 END
                       LIMIT 1""",
                    (
                        item.url,
                        result.source,
                        item.source_native_id,
                        item.url,
                    ),
                ).fetchone()
                if row is None:
                    raise RuntimeError("document projection was not persisted")
                document_id = row["document_id"]
                proposed_version_id = stable_temporal_id(
                    "version",
                    {
                        "document_id": document_id,
                        "content_hash": item_hash,
                    },
                )
                conn.execute(
                    """INSERT OR IGNORE INTO document_versions (
                           version_id, document_id, acquisition_id, content_hash,
                           title, author, normalized_text, source_metadata_json,
                           media_json, published_at, valid_from, valid_to,
                           observed_at, fetched_at, system_from, system_to,
                           retention_class, redaction_class, access_partition_id,
                           transformation_version
                       ) VALUES (
                           ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL,
                           ?, ?, ?, NULL, ?, ?, ?, 'service-worker-v1'
                       )""",
                    (
                        proposed_version_id,
                        document_id,
                        acquisition.acquisition_id,
                        item_hash,
                        item.title,
                        item.author,
                        item.text,
                        metadata_json,
                        media_json,
                        item.published_at,
                        item.published_at,
                        acquisition.observed_at,
                        acquisition.fetched_at,
                        acquisition.fetched_at,
                        retention.value,
                        classification.value,
                        partition_id,
                    ),
                )
                version = conn.execute(
                    """SELECT version_id, access_partition_id
                       FROM document_versions
                       WHERE document_id = ? AND content_hash = ?""",
                    (document_id, item_hash),
                ).fetchone()
                if version is None:
                    raise RuntimeError("document version was not persisted")
                version_id = version["version_id"]
                if version["access_partition_id"] != partition_id:
                    raise RuntimeError("document version access partition conflict")

                version_chunk = conn.execute(
                    """SELECT chunk_id
                       FROM document_version_chunks
                       WHERE version_id = ? AND ordinal = 0""",
                    (version_id,),
                ).fetchone()
                text_hash = _digest(item.text)
                if version_chunk is None:
                    version_chunk_id = stable_temporal_id(
                        "vchunk",
                        {"version_id": version_id, "ordinal": 0},
                    )
                    conn.execute(
                        """INSERT INTO document_version_chunks (
                               chunk_id, version_id, document_id, ordinal, text,
                               content_hash, chunker_version, access_partition_id
                           ) VALUES (?, ?, ?, 0, ?, ?, 'service-chunker-v1', ?)""",
                        (
                            version_chunk_id,
                            version_id,
                            document_id,
                            item.text,
                            text_hash,
                            partition_id,
                        ),
                    )
                else:
                    version_chunk_id = version_chunk["chunk_id"]
                evidence_id = stable_temporal_id(
                    "evidence",
                    {
                        "version_id": version_id,
                        "chunk_id": version_chunk_id,
                        "span_start": 0,
                        "span_end": len(item.text),
                        "span_digest": text_hash,
                    },
                )
                conn.execute(
                    """INSERT OR IGNORE INTO evidence_spans (
                           evidence_id, version_id, chunk_id, span_start,
                           span_end, span_digest, redaction_class,
                           access_partition_id, created_at
                       ) VALUES (?, ?, ?, 0, ?, ?, ?, ?, ?)""",
                    (
                        evidence_id,
                        version_id,
                        version_chunk_id,
                        len(item.text),
                        text_hash,
                        classification.value,
                        partition_id,
                        acquisition.fetched_at,
                    ),
                )
                conn.execute(
                    """INSERT OR IGNORE INTO document_version_sightings (
                           version_id, acquisition_id, topic_id,
                           collection_spec_id, collection_run_id, observed_at,
                           access_partition_id
                       ) VALUES (?, ?, NULL, ?, ?, ?, ?)""",
                    (
                        version_id,
                        acquisition.acquisition_id,
                        (
                            collection["collection_spec_id"]
                            if collection is not None
                            else None
                        ),
                        (
                            collection["collection_run_id"]
                            if collection is not None
                            else None
                        ),
                        acquisition.observed_at,
                        partition_id,
                    ),
                )

                chunk_id = _stable_id("chunk", f"{document_id}:0")
                if row["current_version_id"] != version_id:
                    conn.execute(
                        """UPDATE documents
                           SET acquisition_id = ?, source = ?, source_native_id = ?,
                               canonical_url = ?, title = ?, author = ?,
                               normalized_text = ?, content_hash = ?,
                               published_at = ?, fetched_at = ?,
                               retention_class = ?, redaction_class = ?,
                               transformation_version = 'service-worker-v1',
                               source_metadata_json = ?, media_json = ?,
                               current_version_id = ?, access_partition_id = ?
                           WHERE document_id = ?""",
                        (
                            acquisition.acquisition_id,
                            result.source,
                            item.source_native_id,
                            item.url,
                            item.title,
                            item.author,
                            item.text,
                            item_hash,
                            item.published_at,
                            result.fetched_at,
                            retention.value,
                            classification.value,
                            metadata_json,
                            media_json,
                            version_id,
                            partition_id,
                            document_id,
                        ),
                    )
                    conn.execute(
                        """INSERT INTO document_chunks
                           (chunk_id, document_id, ordinal, text, content_hash,
                            chunker_version, document_version_id)
                           VALUES (?, ?, 0, ?, ?, 'service-chunker-v1', ?)
                           ON CONFLICT(chunk_id) DO UPDATE SET
                               text = excluded.text,
                               content_hash = excluded.content_hash,
                               chunker_version = excluded.chunker_version,
                               document_version_id =
                                   excluded.document_version_id""",
                        (chunk_id, document_id, item.text, text_hash, version_id),
                    )
                else:
                    chunks_inserted += conn.execute(
                        """INSERT OR IGNORE INTO document_chunks
                           (chunk_id, document_id, ordinal, text, content_hash,
                            chunker_version, document_version_id)
                           VALUES (?, ?, 0, ?, ?, 'service-chunker-v1', ?)""",
                        (chunk_id, document_id, item.text, text_hash, version_id),
                    ).rowcount
                sightings_inserted += conn.execute(
                    """INSERT OR IGNORE INTO document_sightings
                       (document_id, acquisition_id, topic_id, observed_at)
                       VALUES (?, ?, NULL, ?)""",
                    (document_id, acquisition.acquisition_id, result.observed_at),
                ).rowcount
            stored_count = int(
                conn.execute(
                    """SELECT COUNT(*) FROM document_version_sightings
                       WHERE acquisition_id = ?""",
                    (acquisition.acquisition_id,),
                ).fetchone()[0]
            )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
        return PublicationStats(
            acquisition_inserted=acquisition_inserted,
            documents_inserted=documents_inserted,
            chunks_inserted=chunks_inserted,
            sightings_inserted=sightings_inserted,
            stored_count=stored_count,
            deduplicated_count=max(0, result.item_count - documents_inserted),
        )

    def publish_index(self) -> str:
        """Complete pending embeddings and publish the current corpus manifest."""
        self.retriever.embed_pending_chunks()
        return self.retriever.publish_index()
