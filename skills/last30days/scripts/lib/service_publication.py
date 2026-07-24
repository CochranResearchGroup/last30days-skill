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


@dataclass(frozen=True)
class PublicationStats:
    acquisition_inserted: bool
    documents_inserted: int
    chunks_inserted: int
    sightings_inserted: int


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
    ) -> PublicationStats:
        """Ledger one result and idempotently project its validated content."""
        self._assert_matching(request, result)
        content_hash = _digest([item.to_dict() for item in result.items])
        classification = (
            contracts.RedactionClass.AUTHENTICATED
            if result.source in _BROWSER_SOURCES
            else contracts.RedactionClass.PUBLIC
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
                "retention_class": contracts.RetentionClass.CACHE.value,
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
            for item in result.items:
                proposed_document_id = _stable_id(
                    "doc", f"{result.source}:{item.url}"
                )
                item_hash = _digest(item.to_dict())
                row = conn.execute(
                    """SELECT document_id, content_hash
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
                        transformation_version)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'cache', ?, ?)""",
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
                        classification.value,
                        "service-worker-v1",
                    ),
                    ).rowcount
                documents_inserted += inserted
                row = conn.execute(
                    """SELECT document_id, content_hash
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
                chunk_id = _stable_id("chunk", f"{document_id}:0")
                text_hash = _digest(item.text)
                if row["content_hash"] != item_hash:
                    conn.execute(
                        """UPDATE documents
                           SET acquisition_id = ?, source = ?, source_native_id = ?,
                               canonical_url = ?, title = ?, author = ?,
                               normalized_text = ?, content_hash = ?,
                               published_at = ?, fetched_at = ?,
                               redaction_class = ?,
                               transformation_version = 'service-worker-v1'
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
                            classification.value,
                            document_id,
                        ),
                    )
                    conn.execute(
                        "DELETE FROM chunk_embeddings WHERE chunk_id = ?",
                        (chunk_id,),
                    )
                    conn.execute(
                        """INSERT INTO document_chunks
                           (chunk_id, document_id, ordinal, text, content_hash,
                            chunker_version)
                           VALUES (?, ?, 0, ?, ?, 'service-chunker-v1')
                           ON CONFLICT(chunk_id) DO UPDATE SET
                               text = excluded.text,
                               content_hash = excluded.content_hash,
                               chunker_version = excluded.chunker_version""",
                        (chunk_id, document_id, item.text, text_hash),
                    )
                else:
                    chunks_inserted += conn.execute(
                        """INSERT OR IGNORE INTO document_chunks
                           (chunk_id, document_id, ordinal, text, content_hash,
                            chunker_version)
                           VALUES (?, ?, 0, ?, ?, 'service-chunker-v1')""",
                        (chunk_id, document_id, item.text, text_hash),
                    ).rowcount
                sightings_inserted += conn.execute(
                    """INSERT OR IGNORE INTO document_sightings
                       (document_id, acquisition_id, topic_id, observed_at)
                       VALUES (?, ?, NULL, ?)""",
                    (document_id, acquisition.acquisition_id, result.observed_at),
                ).rowcount
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
        )

    def publish_index(self) -> str:
        """Publish the deterministic current corpus manifest after projections."""
        return self.retriever.publish_index()
