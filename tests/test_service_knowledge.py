"""Evidence-backed claims/events, temporal query, and graph outbox tests."""

import sqlite3

from tests.test_service_profiles import _seed_evidence

from lib.service_knowledge import (
    ClaimProposal,
    EventProposal,
    GraphProjectionWorker,
    KnowledgePublisher,
    TemporalKnowledgeQuery,
    classify_temporal_query,
)
from lib.service_retrieval import HybridRetriever


class RecordingGraph:
    def __init__(self, *, fail=False):
        self.fail = fail
        self.calls = []

    def upsert(self, *, aggregate_kind, aggregate_id, payload, partition_id):
        if self.fail:
            raise RuntimeError("graph unavailable")
        self.calls.append((aggregate_kind, aggregate_id, payload, partition_id))
        return f"receipt:{aggregate_kind}:{aggregate_id}"


def test_late_evidence_distinguishes_world_time_from_knowledge_time(tmp_path):
    db_path = tmp_path / "knowledge.db"
    _seed_evidence(db_path)
    publisher = KnowledgePublisher(db_path)
    person = publisher.ensure_entity("Ada Lovelace", "person", aliases=("Ada",))

    claim = publisher.promote_claim(
        ClaimProposal(
            subject_entity_id=person,
            predicate="affiliated_with",
            object_value={"organization": "Analytical Engine Society"},
            confidence=0.9,
            validation_state="accepted",
            valid_from="2026-01-01T00:00:00Z",
            valid_to=None,
            observed_at="2026-07-25T12:00:00Z",
            system_from="2026-07-25T12:00:01Z",
            evidence_ids=("evidence-profile",),
            access_partition_id="profile:linkedin-primary",
            extractor_version="profile-change-v1",
        )
    )

    query = TemporalKnowledgeQuery(db_path)
    assert [item["claim_id"] for item in query.query(
        "Who was Ada affiliated with as of February 2026?",
        access_partitions=("profile:linkedin-primary",),
        as_of="2026-02-01T00:00:00Z",
    )["claims"]] == [claim]
    assert query.query(
        "Who was Ada affiliated with as of February 2026?",
        access_partitions=("profile:linkedin-primary",),
        as_of="2026-02-01T00:00:00Z",
    )["evidence"][0]["canonical_url"] == "https://www.linkedin.com/in/ada"
    assert query.query(
        "What did we know about Ada in February 2026?",
        access_partitions=("profile:linkedin-primary",),
        known_as_of="2026-02-01T00:00:00Z",
    )["claims"] == []


def test_temporal_query_fuses_authorized_corpus_candidates(tmp_path):
    db_path = tmp_path / "fusion.db"
    _seed_evidence(db_path)
    retriever = HybridRetriever(db_path)
    index_version = retriever.publish_index()
    assert retriever.search_snapshot(
        "Analytical Engines", access_partitions=("public",)
    ).evidence == []

    result = TemporalKnowledgeQuery(db_path, retriever=retriever).query(
        "Analytical Engines",
        access_partitions=("profile:linkedin-primary",),
    )
    assert result["index_version"] == index_version
    assert [item["document_id"] for item in result["corpus_evidence"]] == [
        "doc-profile"
    ]

    query = TemporalKnowledgeQuery(db_path)
    case_id = query.record_case(
        "Analytical Engines as of 2026",
        access_partitions=("profile:linkedin-primary",),
        expected_evidence_ids=("evidence-profile",),
        as_of="2026-01-01T00:00:00Z",
    )
    accepted = query.evaluate_case(
        case_id,
        policy_version="temporal-ranker-v1",
        returned_evidence_ids=("evidence-profile",),
        returned_access_partitions=("profile:linkedin-primary",),
        temporal_correct=True,
    )
    assert accepted["accepted"] is True
    rejected = query.evaluate_case(
        case_id,
        policy_version="temporal-ranker-v2",
        returned_evidence_ids=(),
        returned_access_partitions=("public",),
        temporal_correct=False,
    )
    assert rejected["validation_codes"] == [
        "missing_expected_evidence",
        "temporal_filter_mismatch",
        "access_partition_widened",
    ]


def test_conflicts_events_and_graph_projection_are_replayable(tmp_path):
    db_path = tmp_path / "graph.db"
    _seed_evidence(db_path)
    publisher = KnowledgePublisher(db_path)
    person = publisher.ensure_entity("Ada Lovelace", "person")
    first = publisher.promote_claim(
        ClaimProposal(
            subject_entity_id=person,
            predicate="location",
            object_value={"name": "London"},
            confidence=0.8,
            validation_state="accepted",
            valid_from="2026-01-01T00:00:00Z",
            valid_to=None,
            observed_at="2026-07-25T12:00:00Z",
            system_from="2026-07-25T12:00:01Z",
            evidence_ids=("evidence-profile",),
            access_partition_id="profile:linkedin-primary",
            extractor_version="extract-v1",
        )
    )
    second = publisher.promote_claim(
        ClaimProposal(
            subject_entity_id=person,
            predicate="location",
            object_value={"name": "Paris"},
            confidence=0.7,
            validation_state="accepted",
            valid_from="2026-01-01T00:00:00Z",
            valid_to=None,
            observed_at="2026-07-25T12:00:00Z",
            system_from="2026-07-25T12:00:02Z",
            evidence_ids=("evidence-profile",),
            access_partition_id="profile:linkedin-primary",
            extractor_version="extract-v1",
        )
    )
    event = publisher.promote_event(
        EventProposal(
            event_type="affiliation_change",
            title="Ada joined the Analytical Engine Society",
            description=None,
            event_time_from="2026-01-01T00:00:00Z",
            event_time_to=None,
            observed_at="2026-07-25T12:00:00Z",
            system_from="2026-07-25T12:00:02Z",
            entity_roles=((person, "person"),),
            evidence_ids=("evidence-profile",),
            access_partition_id="profile:linkedin-primary",
            extractor_version="extract-v1",
        )
    )
    publisher.record_conflict(first, second, "contradictory_value")

    assert classify_temporal_query("Show Ada's timeline") == "timeline"
    assert classify_temporal_query("Compare Ada and Babbage") == "comparison"
    query = TemporalKnowledgeQuery(db_path).query(
        "Show Ada's timeline",
        access_partitions=("profile:linkedin-primary",),
    )
    assert {item["claim_id"] for item in query["claims"]} == {first, second}
    assert [item["event_id"] for item in query["events"]] == [event]
    assert len(query["conflicts"]) == 1

    failing = GraphProjectionWorker(db_path, RecordingGraph(fail=True))
    assert failing.deliver(limit=100) == {"published": 0, "failed": 3}
    sink = RecordingGraph()
    worker = GraphProjectionWorker(db_path, sink)
    assert worker.deliver(limit=100) == {"published": 3, "failed": 0}
    assert worker.rebuild() == 3
    assert len(sink.calls) == 6

    conn = sqlite3.connect(db_path)
    assert conn.execute(
        "SELECT COUNT(*) FROM graph_projection_receipts"
    ).fetchone()[0] == 3
    conn.close()
