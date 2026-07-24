"""Behavior tests for the cache-backed hybrid retrieval module."""

from __future__ import annotations

import sqlite3

from lib import service_contracts
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
