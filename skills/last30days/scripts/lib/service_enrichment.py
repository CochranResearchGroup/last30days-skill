"""Deterministic enrichment and validation over the service knowledge store.

Provider calls and proposal generation are intentionally outside the database
transaction.  Only validated vectors, evidence-bounded mentions, and
evidence-linked relationships are promoted into authoritative tables.
"""

from __future__ import annotations

import hashlib
import math
import re
import sqlite3
import struct
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping, Sequence

import store

from . import service_contracts as contracts
from .service_retrieval import EmbeddingProvider


@dataclass(frozen=True)
class EntityRule:
    """One explicit entity-resolution rule used by the deterministic extractor."""

    canonical_name: str
    entity_type: str
    aliases: tuple[str, ...] = ()
    confidence: float = 1.0

    def __post_init__(self) -> None:
        if not self.canonical_name.strip():
            raise ValueError("canonical_name must be non-empty")
        if self.entity_type not in contracts.EntityProposal.ENTITY_TYPES:
            raise ValueError("entity_type is not supported")
        if any(not alias.strip() for alias in self.aliases):
            raise ValueError("aliases must be non-empty")
        if not 0 <= self.confidence <= 1:
            raise ValueError("confidence must be between 0 and 1")


@dataclass(frozen=True)
class EmbeddingRunResult:
    """Safe outcome for one retryable embedding batch run."""

    status: str
    model: str | None
    chunks_seen: int
    embeddings_written: int
    error_code: str | None = None


@dataclass(frozen=True)
class EmbeddingRecord:
    """Non-sensitive metadata proving one stored embedding version."""

    chunk_id: str
    model: str
    dimensions: int
    vector_digest: str
    created_at: str


@dataclass(frozen=True)
class ProposalRejection:
    """One deterministic rejection without provider text or private content."""

    proposal_id: str
    error_code: str


@dataclass(frozen=True)
class PromotionResult:
    """Accepted stable IDs and bounded rejection codes for a proposal batch."""

    accepted_ids: tuple[str, ...]
    rejections: tuple[ProposalRejection, ...]

    @property
    def accepted_count(self) -> int:
        return len(self.accepted_ids)

    @property
    def rejected_count(self) -> int:
        return len(self.rejections)


@dataclass(frozen=True)
class EntityMention:
    """Read model for one accepted, evidence-bounded entity mention."""

    document_id: str
    entity_id: str
    canonical_name: str
    entity_type: str
    evidence_chunk_id: str
    evidence_start: int
    evidence_end: int
    evidence_text: str
    extractor_version: str
    confidence: float


@dataclass(frozen=True)
class RelationshipRecord:
    """Read model for one promoted evidence-linked relationship."""

    relationship_id: str
    document_id: str
    subject_entity_id: str
    predicate: str
    object_entity_id: str
    evidence_chunk_id: str
    extractor_version: str
    confidence: float
    validation_state: str


class _InvalidEmbeddingOutput(ValueError):
    pass


def _digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _stable_id(prefix: str, value: str) -> str:
    return f"{prefix}-{_digest(value)[:24]}"


def _normalize_name(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value).casefold()
    return " ".join(normalized.split())


_GENERIC_ENTITY_RE = re.compile(
    r"(?<!\w)(?:"
    r"[A-Z][A-Za-z0-9]*[A-Z][A-Za-z0-9]*"
    r"|[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+"
    r")(?!\w)"
)


def _pack_vector(vector: Sequence[float]) -> bytes:
    return struct.pack(f"<{len(vector)}d", *vector)


def _validated_vectors(
    vectors: Sequence[Sequence[float]],
    *,
    expected_count: int,
    expected_dimensions: int | None,
) -> tuple[list[tuple[float, ...]], int]:
    try:
        count = len(vectors)
    except TypeError as exc:
        raise _InvalidEmbeddingOutput("vectors must be a sequence") from exc
    if count != expected_count:
        raise _InvalidEmbeddingOutput("provider returned the wrong vector count")
    validated: list[tuple[float, ...]] = []
    dimensions = expected_dimensions
    for vector in vectors:
        try:
            values = tuple(float(value) for value in vector)
        except (TypeError, ValueError, OverflowError) as exc:
            raise _InvalidEmbeddingOutput("vector values must be numeric") from exc
        if not values:
            raise _InvalidEmbeddingOutput("vectors must not be empty")
        if dimensions is None:
            dimensions = len(values)
        if len(values) != dimensions:
            raise _InvalidEmbeddingOutput("vector dimensions must be consistent")
        if not all(math.isfinite(value) for value in values):
            raise _InvalidEmbeddingOutput("vector values must be finite")
        validated.append(values)
    if dimensions is None:
        raise _InvalidEmbeddingOutput("no vector dimensions were returned")
    return validated, dimensions


class EnrichmentService:
    """Deep module for embeddings and evidence-gated graph promotion."""

    def __init__(
        self,
        db_path: Path,
        *,
        embedding_provider: EmbeddingProvider | None = None,
        entity_rules: Sequence[EntityRule] = (),
        extractor_version: str = "entity-rules-v1",
        minimum_confidence: float = 0.5,
        generic_entity_extraction: bool = False,
    ) -> None:
        if not extractor_version.strip():
            raise ValueError("extractor_version must be non-empty")
        if not 0 <= minimum_confidence <= 1:
            raise ValueError("minimum_confidence must be between 0 and 1")
        self.db_path = Path(db_path)
        self.embedding_provider = embedding_provider
        self.entity_rules = tuple(entity_rules)
        self.extractor_version = extractor_version
        self.minimum_confidence = minimum_confidence
        self.generic_entity_extraction = generic_entity_extraction

    def initialize(self) -> None:
        store.init_db(self.db_path)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=5)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("PRAGMA busy_timeout=5000")
        return conn

    def embed_chunks(
        self,
        *,
        batch_size: int = 32,
        replace: bool = False,
    ) -> EmbeddingRunResult:
        """Generate one versioned embedding per chunk without partial publication."""

        if batch_size < 1:
            raise ValueError("batch_size must be positive")
        provider = self.embedding_provider
        if provider is None:
            return EmbeddingRunResult("disabled", None, 0, 0)
        model = getattr(provider, "model", None)
        if not isinstance(model, str) or not model.strip():
            return EmbeddingRunResult(
                "failed",
                None,
                0,
                0,
                "embedding_model_invalid",
            )

        self.initialize()
        conn = self._connect()
        try:
            if replace:
                rows = conn.execute(
                    """SELECT chunk_id, text
                       FROM document_chunks
                       ORDER BY chunk_id"""
                ).fetchall()
            else:
                rows = conn.execute(
                    """SELECT c.chunk_id, c.text
                       FROM document_chunks AS c
                       LEFT JOIN chunk_embeddings AS e
                         ON e.chunk_id = c.chunk_id AND e.model = ?
                       WHERE e.chunk_id IS NULL
                       ORDER BY c.chunk_id""",
                    (model,),
                ).fetchall()
        finally:
            conn.close()
        if not rows:
            return EmbeddingRunResult("succeeded", model, 0, 0)

        pending: list[tuple[str, tuple[float, ...]]] = []
        dimensions: int | None = None
        try:
            for offset in range(0, len(rows), batch_size):
                batch = rows[offset : offset + batch_size]
                raw_vectors = provider.embed([row["text"] for row in batch])
                vectors, dimensions = _validated_vectors(
                    raw_vectors,
                    expected_count=len(batch),
                    expected_dimensions=dimensions,
                )
                pending.extend(
                    (row["chunk_id"], vector)
                    for row, vector in zip(batch, vectors)
                )
        except _InvalidEmbeddingOutput:
            return EmbeddingRunResult(
                "failed",
                model,
                len(rows),
                0,
                "embedding_output_invalid",
            )
        except Exception:
            return EmbeddingRunResult(
                "failed",
                model,
                len(rows),
                0,
                "embedding_provider_error",
            )

        created_at = datetime.now(timezone.utc).isoformat()
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            for chunk_id, vector in pending:
                conn.execute(
                    """INSERT INTO chunk_embeddings
                       (chunk_id, model, dimensions, vector, created_at)
                       VALUES (?, ?, ?, ?, ?)
                       ON CONFLICT(chunk_id, model) DO UPDATE SET
                           dimensions = excluded.dimensions,
                           vector = excluded.vector,
                           created_at = excluded.created_at""",
                    (
                        chunk_id,
                        model,
                        len(vector),
                        _pack_vector(vector),
                        created_at,
                    ),
                )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
        return EmbeddingRunResult(
            "succeeded",
            model,
            len(rows),
            len(pending),
        )

    def embedding_records(self, chunk_id: str) -> tuple[EmbeddingRecord, ...]:
        """Return version metadata without exposing raw vectors."""

        self.initialize()
        conn = self._connect()
        try:
            rows = conn.execute(
                """SELECT chunk_id, model, dimensions, vector, created_at
                   FROM chunk_embeddings
                   WHERE chunk_id = ?
                   ORDER BY model""",
                (chunk_id,),
            ).fetchall()
        finally:
            conn.close()
        return tuple(
            EmbeddingRecord(
                chunk_id=row["chunk_id"],
                model=row["model"],
                dimensions=row["dimensions"],
                vector_digest=hashlib.sha256(row["vector"]).hexdigest(),
                created_at=row["created_at"],
            )
            for row in rows
        )

    def propose_entities(self) -> tuple[contracts.EntityProposal, ...]:
        """Apply explicit rules to chunks and return stable evidence proposals."""

        if not self.entity_rules and not self.generic_entity_extraction:
            return ()
        self.initialize()
        conn = self._connect()
        try:
            chunks = conn.execute(
                """SELECT document_id, chunk_id, text
                   FROM document_chunks
                   ORDER BY document_id, ordinal, chunk_id"""
            ).fetchall()
        finally:
            conn.close()

        proposals: list[contracts.EntityProposal] = []
        seen: set[tuple[str, str, int, int]] = set()
        rules = sorted(
            self.entity_rules,
            key=lambda rule: (
                _normalize_name(rule.canonical_name),
                rule.entity_type,
            ),
        )
        for chunk in chunks:
            for rule in rules:
                aliases = sorted(
                    {rule.canonical_name, *rule.aliases},
                    key=lambda alias: (-len(alias), _normalize_name(alias)),
                )
                entity_key = (
                    f"{rule.entity_type}:{_normalize_name(rule.canonical_name)}"
                )
                for alias in aliases:
                    pattern = re.compile(
                        rf"(?<!\w){re.escape(alias)}(?!\w)",
                        re.IGNORECASE | re.UNICODE,
                    )
                    for match in pattern.finditer(chunk["text"]):
                        dedupe_key = (
                            chunk["chunk_id"],
                            entity_key,
                            match.start(),
                            match.end(),
                        )
                        if dedupe_key in seen:
                            continue
                        seen.add(dedupe_key)
                        proposal_key = ":".join(
                            (
                                chunk["document_id"],
                                chunk["chunk_id"],
                                entity_key,
                                str(match.start()),
                                str(match.end()),
                                self.extractor_version,
                            )
                        )
                        proposals.append(
                            contracts.EntityProposal.from_dict(
                                {
                                    "schema_version": contracts.SCHEMA_VERSION,
                                    "proposal_id": _stable_id(
                                        "entity-proposal", proposal_key
                                    ),
                                    "document_id": chunk["document_id"],
                                    "evidence_chunk_id": chunk["chunk_id"],
                                    "canonical_name": rule.canonical_name,
                                    "entity_type": rule.entity_type,
                                    "evidence_start": match.start(),
                                    "evidence_end": match.end(),
                                    "extractor_version": self.extractor_version,
                                    "confidence": rule.confidence,
                                }
                            )
                        )
            if self.generic_entity_extraction:
                for match in _GENERIC_ENTITY_RE.finditer(chunk["text"]):
                    canonical_name = match.group(0)
                    entity_key = f"topic:{_normalize_name(canonical_name)}"
                    dedupe_key = (
                        chunk["chunk_id"],
                        entity_key,
                        match.start(),
                        match.end(),
                    )
                    if dedupe_key in seen:
                        continue
                    seen.add(dedupe_key)
                    proposal_key = ":".join(
                        (
                            chunk["document_id"],
                            chunk["chunk_id"],
                            entity_key,
                            str(match.start()),
                            str(match.end()),
                            self.extractor_version,
                        )
                    )
                    proposals.append(
                        contracts.EntityProposal.from_dict(
                            {
                                "schema_version": contracts.SCHEMA_VERSION,
                                "proposal_id": _stable_id(
                                    "entity-proposal", proposal_key
                                ),
                                "document_id": chunk["document_id"],
                                "evidence_chunk_id": chunk["chunk_id"],
                                "canonical_name": canonical_name,
                                "entity_type": "topic",
                                "evidence_start": match.start(),
                                "evidence_end": match.end(),
                                "extractor_version": self.extractor_version,
                                "confidence": 1.0,
                            }
                        )
                    )
        proposals.sort(
            key=lambda proposal: (
                proposal.document_id,
                proposal.evidence_chunk_id,
                proposal.evidence_start,
                proposal.canonical_name,
                proposal.proposal_id,
            )
        )
        return tuple(proposals)

    def extract_and_promote_entities(self) -> PromotionResult:
        return self.promote_entities(self.propose_entities())

    def promote_entities(
        self,
        proposals: Sequence[contracts.EntityProposal | Mapping[str, object]],
    ) -> PromotionResult:
        """Validate schema, evidence bounds, and confidence before promotion."""

        self.initialize()
        accepted: list[str] = []
        rejected: list[ProposalRejection] = []
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            for raw_proposal in proposals:
                proposal_id = self._proposal_id(raw_proposal)
                try:
                    proposal = self._entity_proposal(raw_proposal)
                except (contracts.ContractValidationError, TypeError, ValueError):
                    rejected.append(
                        ProposalRejection(proposal_id, "proposal_invalid")
                    )
                    continue
                if proposal.confidence < self.minimum_confidence:
                    rejected.append(
                        ProposalRejection(
                            proposal.proposal_id,
                            "confidence_below_threshold",
                        )
                    )
                    continue
                chunk = conn.execute(
                    """SELECT document_id, text
                       FROM document_chunks
                       WHERE chunk_id = ?""",
                    (proposal.evidence_chunk_id,),
                ).fetchone()
                if chunk is None:
                    rejected.append(
                        ProposalRejection(
                            proposal.proposal_id,
                            "evidence_chunk_not_found",
                        )
                    )
                    continue
                if chunk["document_id"] != proposal.document_id:
                    rejected.append(
                        ProposalRejection(
                            proposal.proposal_id,
                            "evidence_document_mismatch",
                        )
                    )
                    continue
                if proposal.evidence_end > len(chunk["text"]):
                    rejected.append(
                        ProposalRejection(
                            proposal.proposal_id,
                            "evidence_offsets_invalid",
                        )
                    )
                    continue
                evidence_text = chunk["text"][
                    proposal.evidence_start : proposal.evidence_end
                ]
                if not evidence_text.strip():
                    rejected.append(
                        ProposalRejection(
                            proposal.proposal_id,
                            "evidence_span_empty",
                        )
                    )
                    continue

                normalized_name = _normalize_name(proposal.canonical_name)
                entity_id = _stable_id(
                    "entity",
                    f"{proposal.entity_type}:{normalized_name}",
                )
                now = datetime.now(timezone.utc).isoformat()
                conn.execute(
                    """INSERT OR IGNORE INTO entities
                       (entity_id, canonical_name, entity_type, created_at, updated_at)
                       VALUES (?, ?, ?, ?, ?)""",
                    (
                        entity_id,
                        proposal.canonical_name,
                        proposal.entity_type,
                        now,
                        now,
                    ),
                )
                for alias in (proposal.canonical_name, evidence_text):
                    conn.execute(
                        """INSERT OR IGNORE INTO entity_aliases
                           (entity_id, alias, normalized_alias)
                           VALUES (?, ?, ?)""",
                        (entity_id, alias, _normalize_name(alias)),
                    )
                conn.execute(
                    """INSERT INTO document_entities
                       (document_id, entity_id, evidence_chunk_id, evidence_start,
                        evidence_end, extractor_version, confidence,
                        validation_state, proposal_id)
                       VALUES (?, ?, ?, ?, ?, ?, ?, 'accepted', ?)
                       ON CONFLICT(
                           document_id, entity_id, evidence_chunk_id, evidence_start
                       ) DO UPDATE SET
                           evidence_end = excluded.evidence_end,
                           extractor_version = excluded.extractor_version,
                           confidence = excluded.confidence,
                           validation_state = 'accepted',
                           proposal_id = excluded.proposal_id""",
                    (
                        proposal.document_id,
                        entity_id,
                        proposal.evidence_chunk_id,
                        proposal.evidence_start,
                        proposal.evidence_end,
                        proposal.extractor_version,
                        proposal.confidence,
                        proposal.proposal_id,
                    ),
                )
                accepted.append(entity_id)
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
        return PromotionResult(tuple(accepted), tuple(rejected))

    def promote_relationships(
        self,
        proposals: Sequence[
            contracts.RelationshipProposal | Mapping[str, object]
        ],
    ) -> PromotionResult:
        """Promote only relationships backed by a chunk and accepted endpoints."""

        self.initialize()
        accepted: list[str] = []
        rejected: list[ProposalRejection] = []
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            for raw_proposal in proposals:
                proposal_id = self._proposal_id(raw_proposal)
                try:
                    proposal = self._relationship_proposal(raw_proposal)
                except (contracts.ContractValidationError, TypeError, ValueError):
                    rejected.append(
                        ProposalRejection(proposal_id, "proposal_invalid")
                    )
                    continue
                if proposal.confidence < self.minimum_confidence:
                    rejected.append(
                        ProposalRejection(
                            proposal.proposal_id,
                            "confidence_below_threshold",
                        )
                    )
                    continue
                chunk = conn.execute(
                    """SELECT document_id, text
                       FROM document_chunks
                       WHERE chunk_id = ?""",
                    (proposal.evidence_chunk_id,),
                ).fetchone()
                if chunk is None:
                    rejected.append(
                        ProposalRejection(
                            proposal.proposal_id,
                            "evidence_chunk_not_found",
                        )
                    )
                    continue
                if chunk["document_id"] != proposal.document_id:
                    rejected.append(
                        ProposalRejection(
                            proposal.proposal_id,
                            "evidence_document_mismatch",
                        )
                    )
                    continue
                if proposal.evidence_end > len(chunk["text"]):
                    rejected.append(
                        ProposalRejection(
                            proposal.proposal_id,
                            "evidence_offsets_invalid",
                        )
                    )
                    continue
                evidence_text = chunk["text"][
                    proposal.evidence_start : proposal.evidence_end
                ]
                predicate_tokens = tuple(
                    re.findall(r"\w+", proposal.predicate.replace("_", " "))
                )
                evidence_tokens = {
                    token.casefold() for token in re.findall(r"\w+", evidence_text)
                }
                if not predicate_tokens or not all(
                    token.casefold() in evidence_tokens for token in predicate_tokens
                ):
                    rejected.append(
                        ProposalRejection(
                            proposal.proposal_id,
                            "predicate_not_supported_by_evidence",
                        )
                    )
                    continue
                endpoint_mentions = conn.execute(
                    """SELECT DISTINCT entity_id, evidence_start, evidence_end
                       FROM document_entities
                       WHERE document_id = ?
                         AND evidence_chunk_id = ?
                         AND validation_state = 'accepted'
                         AND entity_id IN (?, ?)""",
                    (
                        proposal.document_id,
                        proposal.evidence_chunk_id,
                        proposal.subject_entity_id,
                        proposal.object_entity_id,
                    ),
                ).fetchall()
                endpoint_ids = {row["entity_id"] for row in endpoint_mentions}
                endpoints_covered = all(
                    proposal.evidence_start <= row["evidence_start"]
                    and row["evidence_end"] <= proposal.evidence_end
                    for row in endpoint_mentions
                )
                if len(endpoint_ids) != 2 or not endpoints_covered:
                    rejected.append(
                        ProposalRejection(
                            proposal.proposal_id,
                            "endpoint_mention_not_accepted",
                        )
                    )
                    continue

                relationship_key = ":".join(
                    (
                        proposal.document_id,
                        proposal.evidence_chunk_id,
                        proposal.subject_entity_id,
                        proposal.predicate,
                        proposal.object_entity_id,
                        proposal.extractor_version,
                        str(proposal.evidence_start),
                        str(proposal.evidence_end),
                        _digest(evidence_text),
                    )
                )
                relationship_id = _stable_id("relationship", relationship_key)
                conn.execute(
                    """INSERT INTO relationships
                       (relationship_id, subject_entity_id, predicate,
                        object_entity_id, evidence_chunk_id, extractor_version,
                        confidence, validation_state, created_at, proposal_id,
                        projection_version)
                       VALUES (?, ?, ?, ?, ?, ?, ?, 'accepted', ?, ?, ?)
                       ON CONFLICT(relationship_id) DO UPDATE SET
                           confidence = excluded.confidence,
                           validation_state = 'accepted',
                           proposal_id = excluded.proposal_id,
                           projection_version = excluded.projection_version""",
                    (
                        relationship_id,
                        proposal.subject_entity_id,
                        proposal.predicate,
                        proposal.object_entity_id,
                        proposal.evidence_chunk_id,
                        proposal.extractor_version,
                        proposal.confidence,
                        datetime.now(timezone.utc).isoformat(),
                        proposal.proposal_id,
                        proposal.extractor_version,
                    ),
                )
                conn.execute(
                    """INSERT INTO relationship_evidence
                       (relationship_id, ordinal, evidence_chunk_id,
                        evidence_start, evidence_end, span_hash)
                       VALUES (?, 0, ?, ?, ?, ?)
                       ON CONFLICT(relationship_id, ordinal) DO UPDATE SET
                           evidence_chunk_id = excluded.evidence_chunk_id,
                           evidence_start = excluded.evidence_start,
                           evidence_end = excluded.evidence_end,
                           span_hash = excluded.span_hash""",
                    (
                        relationship_id,
                        proposal.evidence_chunk_id,
                        proposal.evidence_start,
                        proposal.evidence_end,
                        f"sha256:{_digest(evidence_text)}",
                    ),
                )
                accepted.append(relationship_id)
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
        return PromotionResult(tuple(accepted), tuple(rejected))

    def entity_mentions(self, document_id: str) -> tuple[EntityMention, ...]:
        self.initialize()
        conn = self._connect()
        try:
            rows = conn.execute(
                """SELECT de.document_id, de.entity_id, e.canonical_name,
                          e.entity_type, de.evidence_chunk_id, de.evidence_start,
                          de.evidence_end, de.extractor_version, de.confidence,
                          substr(
                              c.text,
                              de.evidence_start + 1,
                              de.evidence_end - de.evidence_start
                          ) AS evidence_text
                   FROM document_entities AS de
                   JOIN entities AS e ON e.entity_id = de.entity_id
                   JOIN document_chunks AS c
                     ON c.chunk_id = de.evidence_chunk_id
                   WHERE de.document_id = ?
                     AND de.validation_state = 'accepted'
                   ORDER BY c.ordinal, de.evidence_start, de.entity_id""",
                (document_id,),
            ).fetchall()
        finally:
            conn.close()
        return tuple(EntityMention(**dict(row)) for row in rows)

    def relationships(
        self,
        document_id: str,
    ) -> tuple[RelationshipRecord, ...]:
        self.initialize()
        conn = self._connect()
        try:
            rows = conn.execute(
                """SELECT r.relationship_id, c.document_id,
                          r.subject_entity_id, r.predicate, r.object_entity_id,
                          r.evidence_chunk_id, r.extractor_version, r.confidence,
                          r.validation_state
                   FROM relationships AS r
                   JOIN document_chunks AS c
                     ON c.chunk_id = r.evidence_chunk_id
                   WHERE c.document_id = ?
                     AND r.validation_state = 'accepted'
                   ORDER BY r.relationship_id""",
                (document_id,),
            ).fetchall()
        finally:
            conn.close()
        return tuple(RelationshipRecord(**dict(row)) for row in rows)

    @staticmethod
    def _proposal_id(proposal: object) -> str:
        if isinstance(proposal, Mapping):
            value = proposal.get("proposal_id")
        else:
            value = getattr(proposal, "proposal_id", None)
        return value if isinstance(value, str) and value else "unknown"

    @staticmethod
    def _entity_proposal(
        proposal: contracts.EntityProposal | Mapping[str, object],
    ) -> contracts.EntityProposal:
        if isinstance(proposal, contracts.EntityProposal):
            return contracts.EntityProposal.from_dict(proposal.to_dict())
        if isinstance(proposal, Mapping):
            return contracts.EntityProposal.from_dict(proposal)
        raise TypeError("entity proposal must be a contract or mapping")

    @staticmethod
    def _relationship_proposal(
        proposal: contracts.RelationshipProposal | Mapping[str, object],
    ) -> contracts.RelationshipProposal:
        if isinstance(proposal, contracts.RelationshipProposal):
            return contracts.RelationshipProposal.from_dict(proposal.to_dict())
        if isinstance(proposal, Mapping):
            return contracts.RelationshipProposal.from_dict(proposal)
        raise TypeError("relationship proposal must be a contract or mapping")
