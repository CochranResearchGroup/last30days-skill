"""Focused tests for deterministic, evidence-linked service enrichment."""

from __future__ import annotations

import sqlite3

import store
from lib import service_contracts as contracts
from lib.service_enrichment import EntityRule, EnrichmentService


def _seed_chunk(db_path, *, text: str) -> tuple[str, str]:
    store.init_db(db_path)
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            """INSERT INTO service_jobs
               (job_id, job_type, dedupe_key, state, query_request_id,
                attempts, max_attempts, budget_cents, created_at, updated_at)
               VALUES ('job-1', 'test', 'test:job-1', 'published', 'query-1',
                       1, 1, 0, '2026-07-24T12:00:00Z',
                       '2026-07-24T12:00:00Z')"""
        )
        conn.execute(
            """INSERT INTO acquisitions
               (acquisition_id, job_id, profile_id, source, adapter,
                adapter_version, query_text, status, observed_at, fetched_at,
                retention_class, redaction_class, item_count)
               VALUES ('acq-1', 'job-1', 'default', 'web', 'fixture', '1',
                       'fixture', 'succeeded', '2026-07-24T12:00:00Z',
                       '2026-07-24T12:00:00Z', 'cache', 'public', 1)"""
        )
        conn.execute(
            """INSERT INTO documents
               (document_id, acquisition_id, source, source_native_id,
                canonical_url, title, normalized_text, content_hash, fetched_at,
                retention_class, redaction_class, transformation_version)
               VALUES ('doc-1', 'acq-1', 'web', 'native-1',
                       'https://example.test/1', 'Fixture', ?, 'sha256:doc',
                       '2026-07-24T12:00:00Z', 'cache', 'public', 'fixture-v1')""",
            (text,),
        )
        conn.execute(
            """INSERT INTO document_chunks
               (chunk_id, document_id, ordinal, text, content_hash,
                chunker_version)
               VALUES ('chunk-1', 'doc-1', 0, ?, 'sha256:chunk', 'fixture-v1')""",
            (text,),
        )
        conn.commit()
    finally:
        conn.close()
    return "doc-1", "chunk-1"


class _MutableEmbedder:
    def __init__(self, model: str, vector=(1.0, 0.0), *, failure=None):
        self.model = model
        self.vector = vector
        self.failure = failure
        self.calls = 0

    def embed(self, texts):
        self.calls += 1
        if self.failure is not None:
            raise self.failure
        return [self.vector for _ in texts]


def test_versioned_embeddings_coexist_replace_and_remain_idempotent(tmp_path):
    db_path = tmp_path / "embeddings.db"
    _, chunk_id = _seed_chunk(db_path, text="OpenAI created ChatGPT.")
    provider_v1 = _MutableEmbedder("fixture-v1", (1.0, 0.0))
    service = EnrichmentService(db_path, embedding_provider=provider_v1)

    first = service.embed_chunks(batch_size=1)
    replay = service.embed_chunks(batch_size=1)
    provider_v1.vector = (0.0, 2.0)
    replacement = service.embed_chunks(batch_size=1, replace=True)
    provider_v2 = _MutableEmbedder("fixture-v2", (0.5, 0.5))
    second_version = EnrichmentService(
        db_path,
        embedding_provider=provider_v2,
    ).embed_chunks()

    records = service.embedding_records(chunk_id)
    assert first.status == "succeeded" and first.embeddings_written == 1
    assert replay.status == "succeeded" and replay.embeddings_written == 0
    assert provider_v1.calls == 2
    assert replacement.embeddings_written == 1
    assert second_version.embeddings_written == 1
    assert [record.model for record in records] == ["fixture-v1", "fixture-v2"]
    assert records[0].vector_digest != records[1].vector_digest


def test_embedding_provider_disabled_or_failed_is_non_destructive(tmp_path):
    db_path = tmp_path / "embedding-failure.db"
    _, chunk_id = _seed_chunk(db_path, text="Evidence survives provider failure.")

    disabled = EnrichmentService(db_path).embed_chunks()
    failed = EnrichmentService(
        db_path,
        embedding_provider=_MutableEmbedder(
            "broken-v1",
            failure=RuntimeError("provider secret must not leak"),
        ),
    ).embed_chunks()

    assert disabled.status == "disabled"
    assert failed.status == "failed"
    assert failed.error_code == "embedding_provider_error"
    assert "secret" not in repr(failed)
    assert EnrichmentService(db_path).embedding_records(chunk_id) == ()


def test_deterministic_entity_extraction_has_offsets_and_is_idempotent(tmp_path):
    db_path = tmp_path / "entities.db"
    document_id, _ = _seed_chunk(
        db_path,
        text="OpenAI created ChatGPT. OpenAI maintains the product.",
    )
    service = EnrichmentService(
        db_path,
        entity_rules=(
            EntityRule("OpenAI", "organization"),
            EntityRule("ChatGPT", "product"),
        ),
        extractor_version="rules-v7",
    )

    first = service.extract_and_promote_entities()
    replay = service.extract_and_promote_entities()
    mentions = service.entity_mentions(document_id)

    assert first.rejected_count == 0
    assert replay.accepted_ids == first.accepted_ids
    assert len(mentions) == 3
    assert [mention.evidence_text for mention in mentions] == [
        "OpenAI",
        "ChatGPT",
        "OpenAI",
    ]
    assert {mention.extractor_version for mention in mentions} == {"rules-v7"}


def test_generic_entity_extraction_is_available_without_configured_rules(tmp_path):
    db_path = tmp_path / "generic-entities.db"
    document_id, _ = _seed_chunk(
        db_path,
        text="OpenAI created ChatGPT.",
    )
    service = EnrichmentService(
        db_path,
        extractor_version="generic-entities-v1",
        generic_entity_extraction=True,
    )

    result = service.extract_and_promote_entities()
    mentions = service.entity_mentions(document_id)

    assert result.rejected_count == 0
    assert {mention.evidence_text for mention in mentions} == {
        "OpenAI",
        "ChatGPT",
    }
    assert {mention.entity_type for mention in mentions} == {"topic"}


def test_deterministic_relationship_extraction_requires_explicit_predicate(tmp_path):
    db_path = tmp_path / "deterministic-relationships.db"
    document_id, _ = _seed_chunk(
        db_path,
        text="OpenAI created ChatGPT. Anthropic and Claude are also mentioned.",
    )
    service = EnrichmentService(
        db_path,
        extractor_version="generic-entities-v1",
        generic_entity_extraction=True,
        relationship_predicates=("created",),
    )

    service.extract_and_promote_entities()
    result = service.extract_and_promote_relationships()
    relationships = service.relationships(document_id)

    assert result.accepted_count == 1
    assert result.rejected_count == 0
    assert [(item.predicate, item.validation_state) for item in relationships] == [
        ("created", "accepted")
    ]


def test_relationship_promotion_requires_evidence_and_accepted_mentions(tmp_path):
    db_path = tmp_path / "relationships.db"
    document_id, chunk_id = _seed_chunk(
        db_path,
        text="OpenAI created ChatGPT.",
    )
    service = EnrichmentService(
        db_path,
        entity_rules=(
            EntityRule("OpenAI", "organization"),
            EntityRule("ChatGPT", "product"),
        ),
    )
    service.extract_and_promote_entities()
    mentions = service.entity_mentions(document_id)
    ids = {mention.canonical_name: mention.entity_id for mention in mentions}

    valid = contracts.RelationshipProposal.from_dict(
        {
            "schema_version": contracts.SCHEMA_VERSION,
            "proposal_id": "rel-valid",
            "document_id": document_id,
            "evidence_chunk_id": chunk_id,
            "evidence_start": 0,
            "evidence_end": len("OpenAI created ChatGPT."),
            "subject_entity_id": ids["OpenAI"],
            "predicate": "created",
            "object_entity_id": ids["ChatGPT"],
            "extractor_version": "relationship-rules-v1",
            "confidence": 0.9,
        }
    )
    missing_chunk = {
        **valid.to_dict(),
        "proposal_id": "rel-missing-chunk",
        "evidence_chunk_id": "missing",
    }
    missing_mention = {
        **valid.to_dict(),
        "proposal_id": "rel-missing-mention",
        "object_entity_id": "entity-not-mentioned",
    }

    accepted = service.promote_relationships([valid])
    replay = service.promote_relationships([valid])
    rejected = service.promote_relationships([missing_chunk, missing_mention])
    unsupported = service.promote_relationships(
        [
            {
                **valid.to_dict(),
                "proposal_id": "rel-unsupported",
                "predicate": "owns",
            }
        ]
    )
    relationships = service.relationships(document_id)

    assert accepted.accepted_count == 1
    assert replay.accepted_ids == accepted.accepted_ids
    assert rejected.accepted_count == 0
    assert rejected.rejected_count == 2
    assert {item.error_code for item in rejected.rejections} == {
        "evidence_chunk_not_found",
        "endpoint_mention_not_accepted",
    }
    assert len(relationships) == 1
    assert relationships[0].validation_state == "accepted"
    assert unsupported.accepted_count == 0
    assert (
        unsupported.rejections[0].error_code
        == "predicate_not_supported_by_evidence"
    )
    conn = sqlite3.connect(db_path)
    try:
        relationship = conn.execute(
            """SELECT proposal_id, projection_version
               FROM relationships
               WHERE relationship_id = ?""",
            (relationships[0].relationship_id,),
        ).fetchone()
        evidence = conn.execute(
            """SELECT evidence_chunk_id, evidence_start, evidence_end, span_hash
               FROM relationship_evidence
               WHERE relationship_id = ?""",
            (relationships[0].relationship_id,),
        ).fetchone()
    finally:
        conn.close()
    assert relationship == ("rel-valid", "relationship-rules-v1")
    assert evidence[:3] == (chunk_id, 0, len("OpenAI created ChatGPT."))
    assert evidence[3].startswith("sha256:")

    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            """INSERT INTO document_chunks
               (chunk_id, document_id, ordinal, text, content_hash, chunker_version)
               VALUES ('chunk-2', ?, 1, 'ChatGPT', 'sha256:chunk-2', 'fixture-v1')""",
            (document_id,),
        )
        conn.execute(
            """UPDATE document_entities
               SET evidence_chunk_id = 'chunk-2', evidence_start = 0, evidence_end = 7
               WHERE entity_id = ?""",
            (ids["ChatGPT"],),
        )
        conn.commit()
    finally:
        conn.close()
    wrong_chunk = {
        **valid.to_dict(),
        "proposal_id": "rel-endpoints-split",
    }

    split_result = service.promote_relationships([wrong_chunk])

    assert split_result.accepted_count == 0
    assert split_result.rejections[0].error_code == "endpoint_mention_not_accepted"
