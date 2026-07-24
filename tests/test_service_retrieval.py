"""Behavior tests for the cache-backed hybrid retrieval module."""

from __future__ import annotations

import sqlite3

from lib import service_contracts
from lib.service_enrichment import EnrichmentService
from lib.service_retrieval import FusionConfig, HybridRetriever


def _seed_legacy_finding(
    db_path,
    *,
    source: str,
    url: str,
    title: str,
    content: str,
    summary: str = "",
) -> None:
    conn = sqlite3.connect(db_path)
    try:
        topic_id = conn.execute(
            "INSERT INTO topics (name) VALUES (?)",
            (f"topic-{source}-{title}",),
        ).lastrowid
        run_id = conn.execute(
            """INSERT INTO research_runs (topic_id, run_date, status)
               VALUES (?, '2026-07-24T12:00:00Z', 'completed')""",
            (topic_id,),
        ).lastrowid
        conn.execute(
            """INSERT INTO findings
               (run_id, topic_id, source, source_url, source_title, author,
                content, summary, first_seen, last_seen)
               VALUES (?, ?, ?, ?, ?, 'researcher', ?, ?,
                       '2026-07-24T12:00:00Z', '2026-07-24T12:05:00Z')""",
            (run_id, topic_id, source, url, title, content, summary),
        )
        conn.commit()
    finally:
        conn.close()


def test_indexes_legacy_findings_idempotently_and_returns_cited_fts_hits(tmp_path):
    db_path = tmp_path / "research.db"
    retriever = HybridRetriever(db_path)
    retriever.initialize()
    _seed_legacy_finding(
        db_path,
        source="reddit",
        url="https://reddit.example/agent-browser",
        title="Shared browser profiles",
        content="Agent browser profile sharing prevents duplicate Chromium sessions.",
    )

    first = retriever.index_legacy_findings()
    second = retriever.index_legacy_findings()
    hits = retriever.search("duplicate Chromium", top_k=3)

    assert first.documents_indexed == 1
    assert second.documents_indexed == 0
    assert first.index_version == second.index_version
    conn = sqlite3.connect(db_path)
    assert conn.execute(
        "SELECT COUNT(*) FROM index_documents WHERE index_version = ?",
        (first.index_version,),
    ).fetchone()[0] == 1
    conn.close()
    assert len(hits) == 1
    assert hits[0].source == "reddit"
    assert hits[0].url == "https://reddit.example/agent-browser"
    assert hits[0].acquisition_id
    assert hits[0].content_hash
    assert "duplicate Chromium" in hits[0].snippet
    assert hits[0].scores["lexical"] > 0
    assert hits[0].scores["semantic"] == 0
    assert (
        service_contracts.EvidenceItem.from_dict(hits[0].to_dict()).to_dict()
        == hits[0].to_dict()
    )


class _KeywordEmbedder:
    model = "keyword-test-v1"

    def embed(self, texts):
        vectors = []
        for text in texts:
            lowered = text.lower()
            vectors.append(
                [
                    1.0 if "apple" in lowered or "orchard" in lowered else 0.0,
                    1.0 if "vehicle" in lowered or "motor" in lowered else 0.0,
                ]
            )
        return vectors


def test_exact_semantic_search_finds_nonlexical_matches(tmp_path):
    db_path = tmp_path / "semantic.db"
    retriever = HybridRetriever(db_path, embedding_provider=_KeywordEmbedder())
    retriever.initialize()
    _seed_legacy_finding(
        db_path,
        source="youtube",
        url="https://youtube.example/apples",
        title="Growing fruit",
        content="Apple trees need patient seasonal pruning.",
    )
    _seed_legacy_finding(
        db_path,
        source="youtube",
        url="https://youtube.example/vehicles",
        title="Machine maintenance",
        content="Vehicle motors benefit from regular oil changes.",
    )

    indexed = retriever.index_legacy_findings()
    replayed = retriever.index_legacy_findings()
    hits = retriever.search("orchard harvest", top_k=1)

    assert indexed.embeddings_indexed == 2
    assert replayed.embeddings_indexed == 0
    assert hits[0].url == "https://youtube.example/apples"
    assert hits[0].scores["semantic"] == 1.0
    assert hits[0].scores["lexical"] == 0.0


def test_async_embedding_publish_creates_new_frozen_snapshot(tmp_path):
    db_path = tmp_path / "async-semantic.db"
    lexical = HybridRetriever(db_path)
    lexical.initialize()
    _seed_legacy_finding(
        db_path,
        source="youtube",
        url="https://youtube.example/apples",
        title="Growing fruit",
        content="Apple trees need patient seasonal pruning.",
    )
    lexical_version = lexical.index_legacy_findings().index_version
    semantic = HybridRetriever(
        db_path, embedding_provider=_KeywordEmbedder()
    )

    assert semantic.embed_pending_chunks() == 1
    semantic_version = semantic.publish_index()

    assert semantic_version != lexical_version
    conn = sqlite3.connect(db_path)
    assert conn.execute(
        """SELECT COUNT(*) FROM index_chunk_embeddings
           WHERE index_version = ?""",
        (lexical_version,),
    ).fetchone()[0] == 0
    assert conn.execute(
        """SELECT COUNT(*) FROM index_chunk_embeddings
           WHERE index_version = ?""",
        (semantic_version,),
    ).fetchone()[0] == 1
    conn.close()


def test_published_embedding_snapshot_survives_live_vector_replacement(tmp_path):
    class ReplacementEmbedder(_KeywordEmbedder):
        def embed(self, texts):
            vectors = super().embed(texts)
            return [list(reversed(vector)) for vector in vectors]

    db_path = tmp_path / "immutable-semantic.db"
    provider = _KeywordEmbedder()
    retriever = HybridRetriever(db_path, embedding_provider=provider)
    retriever.initialize()
    _seed_legacy_finding(
        db_path,
        source="youtube",
        url="https://youtube.example/apples",
        title="Growing fruit",
        content="Apple trees need patient seasonal pruning.",
    )
    published = retriever.index_legacy_findings().index_version
    before = retriever.search_snapshot("orchard harvest", top_k=1)

    replaced = EnrichmentService(
        db_path, embedding_provider=ReplacementEmbedder()
    ).embed_chunks(replace=True)
    after = retriever.search_snapshot("orchard harvest", top_k=1)

    assert replaced.embeddings_written == 1
    assert before.index_version == after.index_version == published
    assert [item.to_dict() for item in before.evidence] == [
        item.to_dict() for item in after.evidence
    ]


def test_embedding_provider_failure_degrades_to_lexical(tmp_path):
    class FailingEmbedder:
        model = "failing-v1"

        def embed(self, _texts):
            raise RuntimeError("provider unavailable")

    db_path = tmp_path / "semantic-failure.db"
    lexical = HybridRetriever(db_path)
    lexical.initialize()
    _seed_legacy_finding(
        db_path,
        source="reddit",
        url="https://reddit.example/cache",
        title="Durable cache",
        content="Deterministic lexical evidence remains available.",
    )
    lexical.index_legacy_findings()
    retriever = HybridRetriever(db_path, embedding_provider=FailingEmbedder())

    hits = retriever.search("lexical evidence")

    assert [hit.url for hit in hits] == ["https://reddit.example/cache"]
    assert hits[0].scores["semantic"] == 0.0


class _FusionEmbedder:
    model = "fusion-test-v1"

    def embed(self, texts):
        vectors = []
        for text in texts:
            lowered = text.lower()
            if lowered == "hybrid retrieval" or "semantic champion" in lowered:
                vectors.append([1.0, 0.0])
            else:
                vectors.append([0.0, 1.0])
        return vectors


def test_versioned_rrf_is_deterministic_and_applies_source_filters(tmp_path):
    db_path = tmp_path / "fusion.db"
    fusion = FusionConfig(
        version="rrf-test-v7",
        rank_constant=60,
        semantic_weight=2.0,
    )
    retriever = HybridRetriever(
        db_path,
        embedding_provider=_FusionEmbedder(),
        fusion=fusion,
    )
    retriever.initialize()
    _seed_legacy_finding(
        db_path,
        source="reddit",
        url="https://reddit.example/lexical",
        title="Lexical champion",
        content="Hybrid retrieval retrieval retrieval favors exact matching.",
    )
    _seed_legacy_finding(
        db_path,
        source="youtube",
        url="https://youtube.example/semantic",
        title="Semantic champion",
        content="The semantic champion connects hybrid ideas despite different wording.",
    )
    retriever.index_legacy_findings()

    first = retriever.search("hybrid retrieval", top_k=2)
    replay = retriever.search("hybrid retrieval", top_k=2)
    reddit_only = retriever.search(
        "hybrid retrieval",
        sources=["reddit"],
        top_k=2,
    )

    assert retriever.ranking_version == "rrf-test-v7"
    assert [hit.evidence_id for hit in replay] == [
        hit.evidence_id for hit in first
    ]
    assert first[0].source == "youtube"
    assert first[0].scores["lexical"] > 0
    assert first[0].scores["semantic"] == 1.0
    assert [hit.source for hit in reddit_only] == ["reddit"]


def test_unique_entity_seed_adds_bounded_evidence_linked_graph_candidate(tmp_path):
    db_path = tmp_path / "graph.db"
    retriever = HybridRetriever(db_path)
    retriever.initialize()
    _seed_legacy_finding(
        db_path,
        source="reddit",
        url="https://reddit.example/acme",
        title="Acme overview",
        content="Acme builds durable research systems.",
    )
    _seed_legacy_finding(
        db_path,
        source="youtube",
        url="https://youtube.example/nova",
        title="Launch report",
        content="A partnership launched the Nova system this week.",
    )
    lexical_version = retriever.index_legacy_findings().index_version
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        """SELECT d.document_id, d.canonical_url, c.chunk_id
           FROM documents d JOIN document_chunks c ON c.document_id = d.document_id
           ORDER BY d.canonical_url"""
    ).fetchall()
    by_url = {row["canonical_url"]: row for row in rows}
    target = by_url["https://youtube.example/nova"]
    conn.executemany(
        """INSERT INTO entities
           (entity_id, canonical_name, entity_type, created_at, updated_at)
           VALUES (?, ?, ?, '2026-07-24T12:00:00Z', '2026-07-24T12:00:00Z')""",
        [
            ("entity-acme", "Acme", "organization"),
            ("entity-nova", "Nova", "product"),
        ],
    )
    conn.executemany(
        """INSERT INTO entity_aliases(entity_id, alias, normalized_alias)
           VALUES (?, ?, ?)""",
        [
            ("entity-acme", "Acme", "acme"),
            ("entity-nova", "Nova", "nova"),
        ],
    )
    conn.executemany(
        """INSERT INTO document_entities
           (document_id, entity_id, evidence_chunk_id, evidence_start,
            evidence_end, extractor_version, confidence, validation_state)
           VALUES (?, ?, ?, ?, ?, 'deterministic-v1', 1.0, 'accepted')""",
        [
            (target["document_id"], "entity-acme", target["chunk_id"], 2, 13),
            (target["document_id"], "entity-nova", target["chunk_id"], 29, 33),
        ],
    )
    conn.execute(
        """INSERT INTO relationships
           (relationship_id, subject_entity_id, predicate, object_entity_id,
            evidence_chunk_id, extractor_version, confidence, validation_state,
            created_at, projection_version)
           VALUES ('relationship-001', 'entity-acme', 'created', 'entity-nova',
                   ?, 'deterministic-v1', 1.0, 'accepted',
                   '2026-07-24T12:00:00Z', 'graph-v1')""",
        (target["chunk_id"],),
    )
    conn.execute(
        """INSERT INTO relationship_evidence
           (relationship_id, ordinal, evidence_chunk_id, evidence_start,
            evidence_end, span_hash)
           VALUES ('relationship-001', 0, ?, 0, 54, 'sha256:fixture')""",
        (target["chunk_id"],),
    )
    conn.commit()
    conn.close()

    graph_version = retriever.publish_index()
    hits = retriever.search("Acme", top_k=5)
    youtube_only = retriever.search("Acme", sources=["youtube"], top_k=5)

    assert graph_version != lexical_version
    target_hit = next(
        hit for hit in hits if hit.url == "https://youtube.example/nova"
    )
    assert target_hit.scores["graph"] > 0
    graph_score = target_hit.scores["graph"]
    assert [hit.url for hit in youtube_only] == [
        "https://youtube.example/nova"
    ]

    conn = sqlite3.connect(db_path)
    conn.execute(
        """INSERT INTO entities
           (entity_id, canonical_name, entity_type, created_at, updated_at)
           VALUES ('entity-acme-shadow', 'Acme Shadow', 'organization',
                   '2026-07-24T12:00:00Z', '2026-07-24T12:00:00Z')"""
    )
    conn.execute(
        """INSERT INTO entity_aliases(entity_id, alias, normalized_alias)
           VALUES ('entity-acme-shadow', 'Acme', 'acme')"""
    )
    conn.execute(
        """UPDATE relationships SET confidence = 0.01
           WHERE relationship_id = 'relationship-001'"""
    )
    conn.commit()
    conn.close()

    replay = retriever.search_snapshot("Acme", top_k=5)
    replay_target = next(
        hit
        for hit in replay.evidence
        if hit.url == "https://youtube.example/nova"
    )
    assert replay.index_version == graph_version
    assert replay_target.scores["graph"] == graph_score


def test_search_reads_only_documents_in_the_published_index_snapshot(tmp_path):
    db_path = tmp_path / "snapshot.db"
    retriever = HybridRetriever(db_path)
    retriever.initialize()
    _seed_legacy_finding(
        db_path,
        source="reddit",
        url="https://reddit.example/first",
        title="First indexed document",
        content="Snapshot isolation evidence first.",
    )
    first_index = retriever.index_legacy_findings()
    _seed_legacy_finding(
        db_path,
        source="reddit",
        url="https://reddit.example/second",
        title="Second not yet indexed document",
        content="Snapshot isolation evidence second.",
    )

    before_publish = retriever.search("snapshot isolation", top_k=8)
    second_index = retriever.index_legacy_findings()
    after_publish = retriever.search("snapshot isolation", top_k=8)

    assert [hit.url for hit in before_publish] == [
        "https://reddit.example/first"
    ]
    assert second_index.index_version != first_index.index_version
    assert {hit.url for hit in after_publish} == {
        "https://reddit.example/first",
        "https://reddit.example/second",
    }
