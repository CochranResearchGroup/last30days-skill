"""Deterministic Packet 4 retrieval evaluation gates over the real engine."""

import sqlite3
from types import SimpleNamespace

from lib import service_contracts as contracts
from lib.service_enrichment import EntityRule, EnrichmentService
from lib.service_eval import RetrievalEvalCase, run_retrieval_eval
from lib.service_retrieval import HybridRetriever


class JudgedEmbedder:
    model = "judged-fixture-v1"
    cost_cents_per_call = 0

    def embed(self, texts):
        vectors = []
        for text in texts:
            lowered = text.casefold()
            if "apple" in lowered or "orchard" in lowered:
                vectors.append([1.0, 0.0, 0.0])
            elif "quartz" in lowered:
                vectors.append([0.0, 1.0, 0.0])
            else:
                vectors.append([0.0, 0.0, 1.0])
        return vectors


def _seed_finding(db_path, *, url, title, content):
    conn = sqlite3.connect(db_path)
    topic_id = conn.execute(
        "INSERT INTO topics(name) VALUES (?)", (title,)
    ).lastrowid
    run_id = conn.execute(
        """INSERT INTO research_runs(topic_id, run_date, status)
           VALUES (?, '2026-07-24T12:00:00Z', 'completed')""",
        (topic_id,),
    ).lastrowid
    conn.execute(
        """INSERT INTO findings
           (run_id, topic_id, source, source_url, source_title, content,
            first_seen, last_seen)
           VALUES (?, ?, 'web', ?, ?, ?, '2026-07-24T12:00:00Z',
                   '2026-07-24T12:00:00Z')""",
        (run_id, topic_id, url, title, content),
    )
    conn.commit()
    conn.close()


def test_real_offline_corpus_gates_precision_recall_graph_latency_and_cost(tmp_path):
    db_path = tmp_path / "eval.db"
    retriever = HybridRetriever(db_path, embedding_provider=JudgedEmbedder())
    retriever.initialize()
    _seed_finding(
        db_path,
        url="https://example.test/lexical",
        title="Exact terminology",
        content="Quartz instrumentation has a unique exact term.",
    )
    _seed_finding(
        db_path,
        url="https://example.test/semantic",
        title="Fruit cultivation",
        content="Apple trees need patient seasonal pruning.",
    )
    _seed_finding(
        db_path,
        url="https://example.test/graph",
        title="Product provenance",
        content="OpenAI created ChatGPT.",
    )
    retriever.index_legacy_findings()
    conn = sqlite3.connect(db_path)
    graph_doc = conn.execute(
        """SELECT document_id FROM documents
           WHERE canonical_url = 'https://example.test/graph'"""
    ).fetchone()[0]
    lexical_doc = conn.execute(
        """SELECT document_id FROM documents
           WHERE canonical_url = 'https://example.test/lexical'"""
    ).fetchone()[0]
    semantic_doc = conn.execute(
        """SELECT document_id FROM documents
           WHERE canonical_url = 'https://example.test/semantic'"""
    ).fetchone()[0]
    graph_chunk = conn.execute(
        "SELECT chunk_id FROM document_chunks WHERE document_id = ?",
        (graph_doc,),
    ).fetchone()[0]
    conn.close()
    enrichment = EnrichmentService(
        db_path,
        entity_rules=(
            EntityRule("OpenAI", "organization"),
            EntityRule("ChatGPT", "product"),
        ),
    )
    enrichment.extract_and_promote_entities()
    mentions = {
        mention.canonical_name: mention.entity_id
        for mention in enrichment.entity_mentions(graph_doc)
    }
    promoted = enrichment.promote_relationships(
        [
            contracts.RelationshipProposal.from_dict(
                {
                    "schema_version": 1,
                    "proposal_id": "eval-relationship",
                    "document_id": graph_doc,
                    "evidence_chunk_id": graph_chunk,
                    "evidence_start": 0,
                    "evidence_end": len("OpenAI created ChatGPT."),
                    "subject_entity_id": mentions["OpenAI"],
                    "predicate": "created",
                    "object_entity_id": mentions["ChatGPT"],
                    "extractor_version": "eval-relations-v1",
                    "confidence": 1.0,
                }
            )
        ]
    )
    assert promoted.accepted_count == 1
    retriever.publish_index()
    cases = (
        RetrievalEvalCase("lexical", "quartz", (lexical_doc,), top_k=3),
        RetrievalEvalCase(
            "semantic",
            "orchard",
            (semantic_doc,),
            lane="semantic",
            top_k=3,
        ),
        RetrievalEvalCase(
            "graph",
            "OpenAI",
            (graph_doc,),
            lane="graph",
            top_k=3,
        ),
    )

    report = run_retrieval_eval(retriever, cases, max_cost_cents=0)

    assert report.passed is True
    assert report.precision_at_k == 1.0
    assert report.recall_at_k == 1.0
    assert report.graph_precision_at_k == 1.0
    assert report.cost_cents == 0
    assert report.lane_passes == {"lexical": 1, "semantic": 1, "graph": 1}


def test_false_positives_fail_the_precision_gate():
    expected = SimpleNamespace(
        document_id="expected",
        scores={"lexical": 1.0, "semantic": 0.0, "graph": 0.0},
    )
    false_hits = [
        SimpleNamespace(
            document_id=f"false-{index}",
            scores={"lexical": 1.0, "semantic": 0.0, "graph": 0.0},
        )
        for index in range(4)
    ]

    class NoisyRetriever:
        embedding_provider = None

        def search_snapshot(self, *args, **kwargs):
            return SimpleNamespace(
                index_version="index-noisy",
                evidence=[expected, *false_hits],
            )

    report = run_retrieval_eval(
        NoisyRetriever(),
        [RetrievalEvalCase("noisy", "query", ("expected",), top_k=5)],
    )

    assert report.precision_at_k == 0.2
    assert report.recall_at_k == 1.0
    assert report.passed is False
