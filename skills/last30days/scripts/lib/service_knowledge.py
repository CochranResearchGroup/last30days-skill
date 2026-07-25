"""Authoritative temporal claims/events and rebuildable graph projection."""

from __future__ import annotations

import json
import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Protocol

import store

from .service_temporal import sha256_json, stable_temporal_id


@dataclass(frozen=True)
class ClaimProposal:
    subject_entity_id: str
    predicate: str
    object_value: Mapping[str, object] | None
    confidence: float
    validation_state: str
    valid_from: str | None
    valid_to: str | None
    observed_at: str
    system_from: str
    evidence_ids: tuple[str, ...]
    access_partition_id: str
    extractor_version: str
    object_entity_id: str | None = None


@dataclass(frozen=True)
class EventProposal:
    event_type: str
    title: str
    description: str | None
    event_time_from: str | None
    event_time_to: str | None
    observed_at: str
    system_from: str
    entity_roles: tuple[tuple[str, str], ...]
    evidence_ids: tuple[str, ...]
    access_partition_id: str
    extractor_version: str


class GraphSink(Protocol):
    def upsert(
        self,
        *,
        aggregate_kind: str,
        aggregate_id: str,
        payload: Mapping[str, object],
        partition_id: str,
    ) -> str: ...


def classify_temporal_query(query: str) -> str:
    """Classify the temporal intent without model calls."""
    normalized = " ".join(query.casefold().split())
    if re.search(r"\bwhat did (?:we|you) know\b|\bknown as of\b", normalized):
        return "known_as_of"
    if re.search(r"\bas of\b|\bon \w+ \d{4}\b", normalized):
        return "as_of"
    if re.search(r"\bduring\b|\bbetween\b", normalized):
        return "during"
    if "timeline" in normalized or normalized.startswith("when "):
        return "timeline"
    if re.search(r"\btrend(?:s|ing)?\b|\bover time\b", normalized):
        return "trend"
    if re.search(r"\bcompare\b|\bversus\b|\bvs\.?\b", normalized):
        return "comparison"
    if re.search(r"\bevent(?:s)?\b|\bhappened\b", normalized):
        return "event"
    return "entity"


class KnowledgePublisher:
    """Promote validated proposals only when every fact closes to evidence."""

    def __init__(self, db_path: Path) -> None:
        self.db_path = Path(db_path)
        store.init_db(self.db_path)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=5)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("PRAGMA busy_timeout=5000")
        return conn

    @staticmethod
    def _assert_evidence(
        conn: sqlite3.Connection, evidence_ids: tuple[str, ...], partition_id: str
    ) -> None:
        if not evidence_ids:
            raise ValueError("knowledge promotion requires evidence")
        rows = conn.execute(
            f"""SELECT evidence_id FROM evidence_spans
                WHERE access_partition_id = ?
                  AND evidence_id IN ({','.join('?' for _ in evidence_ids)})""",
            (partition_id, *evidence_ids),
        ).fetchall()
        if {row["evidence_id"] for row in rows} != set(evidence_ids):
            raise ValueError("knowledge evidence is missing or crosses partitions")

    @staticmethod
    def _enqueue(
        conn: sqlite3.Connection,
        *,
        aggregate_kind: str,
        aggregate_id: str,
        payload: Mapping[str, object],
        partition_id: str,
        created_at: str,
    ) -> None:
        payload_json = json.dumps(
            payload, allow_nan=False, ensure_ascii=False, separators=(",", ":"), sort_keys=True
        )
        outbox_id = stable_temporal_id(
            "graph_outbox",
            {
                "aggregate_kind": aggregate_kind,
                "aggregate_id": aggregate_id,
                "payload_sha256": sha256_json(payload),
            },
        )
        conn.execute(
            """INSERT OR IGNORE INTO graph_projection_outbox
               (outbox_id, aggregate_kind, aggregate_id, operation,
                payload_json, payload_sha256, access_partition_id, state,
                created_at)
               VALUES (?, ?, ?, 'upsert', ?, ?, ?, 'pending', ?)""",
            (
                outbox_id,
                aggregate_kind,
                aggregate_id,
                payload_json,
                sha256_json(payload),
                partition_id,
                created_at,
            ),
        )

    def ensure_entity(
        self, canonical_name: str, entity_type: str, *, aliases: tuple[str, ...] = ()
    ) -> str:
        if not canonical_name.strip() or not entity_type.strip():
            raise ValueError("entity name and type are required")
        entity_id = stable_temporal_id(
            "entity",
            {
                "canonical_name": " ".join(canonical_name.casefold().split()),
                "entity_type": entity_type.casefold(),
            },
        )
        conn = self._connect()
        try:
            conn.execute(
                """INSERT OR IGNORE INTO entities
                   (entity_id, canonical_name, entity_type, created_at, updated_at)
                   VALUES (?, ?, ?, datetime('now'), datetime('now'))""",
                (entity_id, canonical_name.strip(), entity_type.casefold()),
            )
            for alias in sorted({canonical_name, *aliases}):
                normalized = " ".join(alias.casefold().split())
                if normalized:
                    conn.execute(
                        """INSERT OR IGNORE INTO entity_aliases
                           (entity_id, alias, normalized_alias)
                           VALUES (?, ?, ?)""",
                        (entity_id, alias.strip(), normalized),
                    )
            conn.commit()
            return entity_id
        finally:
            conn.close()

    def promote_claim(self, proposal: ClaimProposal) -> str:
        if not 0 <= proposal.confidence <= 1:
            raise ValueError("claim confidence is invalid")
        if (proposal.object_entity_id is None) == (proposal.object_value is None):
            raise ValueError("claim requires exactly one object form")
        object_json = (
            json.dumps(
                proposal.object_value,
                allow_nan=False,
                ensure_ascii=False,
                separators=(",", ":"),
                sort_keys=True,
            )
            if proposal.object_value is not None
            else None
        )
        identity = {
            "subject": proposal.subject_entity_id,
            "predicate": proposal.predicate,
            "object_entity": proposal.object_entity_id,
            "object_value": proposal.object_value,
            "valid_from": proposal.valid_from,
            "valid_to": proposal.valid_to,
            "evidence_ids": sorted(proposal.evidence_ids),
        }
        claim_id = stable_temporal_id("claim", identity)
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            self._assert_evidence(
                conn, proposal.evidence_ids, proposal.access_partition_id
            )
            conn.execute(
                """INSERT OR IGNORE INTO temporal_claims
                   (claim_id, subject_entity_id, predicate, object_entity_id,
                    object_value_json, confidence, validation_state, valid_from,
                    valid_to, observed_at, system_from, system_to,
                    access_partition_id, extractor_version)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, ?, ?)""",
                (
                    claim_id,
                    proposal.subject_entity_id,
                    proposal.predicate,
                    proposal.object_entity_id,
                    object_json,
                    proposal.confidence,
                    proposal.validation_state,
                    proposal.valid_from,
                    proposal.valid_to,
                    proposal.observed_at,
                    proposal.system_from,
                    proposal.access_partition_id,
                    proposal.extractor_version,
                ),
            )
            for evidence_id in sorted(set(proposal.evidence_ids)):
                conn.execute(
                    """INSERT OR IGNORE INTO temporal_claim_evidence
                       (claim_id, evidence_id, access_partition_id)
                       VALUES (?, ?, ?)""",
                    (claim_id, evidence_id, proposal.access_partition_id),
                )
            self._enqueue(
                conn,
                aggregate_kind="claim",
                aggregate_id=claim_id,
                payload={
                    "claim_id": claim_id,
                    "subject_entity_id": proposal.subject_entity_id,
                    "predicate": proposal.predicate,
                    "object_entity_id": proposal.object_entity_id,
                    "object_value": proposal.object_value,
                    "valid_from": proposal.valid_from,
                    "valid_to": proposal.valid_to,
                    "system_from": proposal.system_from,
                    "evidence_ids": sorted(proposal.evidence_ids),
                },
                partition_id=proposal.access_partition_id,
                created_at=proposal.system_from,
            )
            conn.commit()
            return claim_id
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def promote_event(self, proposal: EventProposal) -> str:
        event_id = stable_temporal_id(
            "event",
            {
                "event_type": proposal.event_type,
                "title": proposal.title,
                "event_time_from": proposal.event_time_from,
                "event_time_to": proposal.event_time_to,
                "entity_roles": sorted(proposal.entity_roles),
                "evidence_ids": sorted(proposal.evidence_ids),
            },
        )
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            self._assert_evidence(
                conn, proposal.evidence_ids, proposal.access_partition_id
            )
            conn.execute(
                """INSERT OR IGNORE INTO temporal_events
                   (event_id, event_type, title, description, event_time_from,
                    event_time_to, observed_at, system_from, system_to,
                    access_partition_id, extractor_version)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, NULL, ?, ?)""",
                (
                    event_id,
                    proposal.event_type,
                    proposal.title,
                    proposal.description,
                    proposal.event_time_from,
                    proposal.event_time_to,
                    proposal.observed_at,
                    proposal.system_from,
                    proposal.access_partition_id,
                    proposal.extractor_version,
                ),
            )
            for entity_id, role in sorted(set(proposal.entity_roles)):
                conn.execute(
                    """INSERT OR IGNORE INTO temporal_event_entities
                       (event_id, entity_id, role) VALUES (?, ?, ?)""",
                    (event_id, entity_id, role),
                )
            for evidence_id in sorted(set(proposal.evidence_ids)):
                conn.execute(
                    """INSERT OR IGNORE INTO temporal_event_evidence
                       (event_id, evidence_id, access_partition_id)
                       VALUES (?, ?, ?)""",
                    (event_id, evidence_id, proposal.access_partition_id),
                )
            self._enqueue(
                conn,
                aggregate_kind="event",
                aggregate_id=event_id,
                payload={
                    "event_id": event_id,
                    "event_type": proposal.event_type,
                    "title": proposal.title,
                    "event_time_from": proposal.event_time_from,
                    "event_time_to": proposal.event_time_to,
                    "entity_roles": [list(item) for item in proposal.entity_roles],
                    "evidence_ids": sorted(proposal.evidence_ids),
                },
                partition_id=proposal.access_partition_id,
                created_at=proposal.system_from,
            )
            conn.commit()
            return event_id
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def record_conflict(
        self, left_claim_id: str, right_claim_id: str, conflict_kind: str
    ) -> str:
        left, right = sorted((left_claim_id, right_claim_id))
        conflict_id = stable_temporal_id(
            "claim_conflict",
            {"left": left, "right": right, "kind": conflict_kind},
        )
        conn = self._connect()
        try:
            rows = conn.execute(
                """SELECT claim_id, access_partition_id FROM temporal_claims
                   WHERE claim_id IN (?, ?)""",
                (left, right),
            ).fetchall()
            if len(rows) != 2 or len({row["access_partition_id"] for row in rows}) != 1:
                raise ValueError("claim conflict requires one authorized partition")
            partition_id = rows[0]["access_partition_id"]
            conn.execute(
                """INSERT OR IGNORE INTO claim_conflicts
                   (conflict_id, left_claim_id, right_claim_id, conflict_kind,
                    detected_at, resolution_state, access_partition_id)
                   VALUES (?, ?, ?, ?, datetime('now'), 'open', ?)""",
                (conflict_id, left, right, conflict_kind, partition_id),
            )
            conn.commit()
            return conflict_id
        finally:
            conn.close()


class TemporalKnowledgeQuery:
    """Deterministic temporal/access filtering over authoritative records."""

    def __init__(self, db_path: Path, *, retriever=None) -> None:
        self.db_path = Path(db_path)
        self.retriever = retriever
        store.init_db(self.db_path)

    def query(
        self,
        query_text: str,
        *,
        access_partitions: tuple[str, ...],
        as_of: str | None = None,
        during: tuple[str, str] | None = None,
        known_as_of: str | None = None,
    ) -> dict[str, object]:
        if not access_partitions:
            raise ValueError("at least one access partition is required")
        placeholders = ",".join("?" for _ in access_partitions)
        claim_where = [f"c.access_partition_id IN ({placeholders})"]
        claim_args: list[object] = list(access_partitions)
        if as_of is not None:
            claim_where.extend(
                ["(c.valid_from IS NULL OR c.valid_from <= ?)", "(c.valid_to IS NULL OR c.valid_to > ?)"]
            )
            claim_args.extend((as_of, as_of))
        if during is not None:
            claim_where.extend(
                ["(c.valid_to IS NULL OR c.valid_to >= ?)", "(c.valid_from IS NULL OR c.valid_from <= ?)"]
            )
            claim_args.extend(during)
        if known_as_of is not None:
            claim_where.extend(
                ["c.system_from <= ?", "(c.system_to IS NULL OR c.system_to > ?)"]
            )
            claim_args.extend((known_as_of, known_as_of))
        conn = sqlite3.connect(str(self.db_path), timeout=5)
        conn.row_factory = sqlite3.Row
        try:
            claims = conn.execute(
                f"""SELECT c.*, e.canonical_name AS subject_name,
                           GROUP_CONCAT(ce.evidence_id) AS evidence_ids
                    FROM temporal_claims AS c
                    JOIN entities AS e ON e.entity_id = c.subject_entity_id
                    JOIN temporal_claim_evidence AS ce ON ce.claim_id = c.claim_id
                    WHERE {' AND '.join(claim_where)}
                    GROUP BY c.claim_id
                    ORDER BY COALESCE(c.valid_from, c.observed_at), c.claim_id""",
                claim_args,
            ).fetchall()
            event_where = [f"ev.access_partition_id IN ({placeholders})"]
            event_args: list[object] = list(access_partitions)
            if as_of is not None:
                event_where.extend(
                    [
                        "(ev.event_time_from IS NULL OR ev.event_time_from <= ?)",
                        "(ev.event_time_to IS NULL OR ev.event_time_to >= ?)",
                    ]
                )
                event_args.extend((as_of, as_of))
            if during is not None:
                event_where.extend(
                    [
                        "(ev.event_time_to IS NULL OR ev.event_time_to >= ?)",
                        "(ev.event_time_from IS NULL OR ev.event_time_from <= ?)",
                    ]
                )
                event_args.extend(during)
            if known_as_of is not None:
                event_where.extend(
                    ["ev.system_from <= ?", "(ev.system_to IS NULL OR ev.system_to > ?)"]
                )
                event_args.extend((known_as_of, known_as_of))
            events = conn.execute(
                f"""SELECT ev.*, GROUP_CONCAT(ee.evidence_id) AS evidence_ids
                    FROM temporal_events AS ev
                    JOIN temporal_event_evidence AS ee ON ee.event_id = ev.event_id
                    WHERE {' AND '.join(event_where)}
                    GROUP BY ev.event_id
                    ORDER BY COALESCE(ev.event_time_from, ev.observed_at), ev.event_id""",
                event_args,
            ).fetchall()
            claim_ids = [row["claim_id"] for row in claims]
            conflicts = (
                conn.execute(
                    f"""SELECT * FROM claim_conflicts
                        WHERE left_claim_id IN ({','.join('?' for _ in claim_ids)})
                           OR right_claim_id IN ({','.join('?' for _ in claim_ids)})
                        ORDER BY conflict_id""",
                    (*claim_ids, *claim_ids),
                ).fetchall()
                if claim_ids
                else []
            )
            evidence_ids = sorted(
                {
                    evidence_id
                    for row in (*claims, *events)
                    for evidence_id in str(row["evidence_ids"]).split(",")
                    if evidence_id
                }
            )
            evidence = (
                conn.execute(
                    f"""SELECT e.evidence_id, e.version_id, e.chunk_id,
                               e.span_start, e.span_end, e.span_digest,
                               e.redaction_class, e.access_partition_id,
                               v.document_id, v.observed_at, v.published_at,
                               v.valid_from, v.valid_to, v.system_from,
                               v.system_to, d.canonical_url
                        FROM evidence_spans AS e
                        JOIN document_versions AS v
                          ON v.version_id = e.version_id
                        JOIN documents AS d ON d.document_id = v.document_id
                        WHERE e.evidence_id IN (
                            {','.join('?' for _ in evidence_ids)}
                        )
                        ORDER BY e.evidence_id""",
                    evidence_ids,
                ).fetchall()
                if evidence_ids
                else []
            )
        finally:
            conn.close()

        def decoded(row: sqlite3.Row) -> dict[str, object]:
            item = dict(row)
            if "object_value_json" in item and item["object_value_json"] is not None:
                item["object_value"] = json.loads(str(item.pop("object_value_json")))
            if item.get("evidence_ids"):
                item["evidence_ids"] = sorted(set(str(item["evidence_ids"]).split(",")))
            return item

        corpus_evidence: list[dict[str, object]] = []
        index_version = None
        if self.retriever is not None:
            snapshot = self.retriever.search_snapshot(
                query_text,
                access_partitions=access_partitions,
            )
            index_version = snapshot.index_version
            corpus_evidence = [
                item.to_dict() if hasattr(item, "to_dict") else dict(item)
                for item in snapshot.evidence
            ]
        return {
            "query_kind": classify_temporal_query(query_text),
            "query_text": query_text,
            "as_of": as_of,
            "during": list(during) if during else None,
            "known_as_of": known_as_of,
            "access_partitions": list(access_partitions),
            "index_version": index_version,
            "corpus_evidence": corpus_evidence,
            "claims": [decoded(row) for row in claims],
            "events": [decoded(row) for row in events],
            "conflicts": [dict(row) for row in conflicts],
            "evidence": [dict(row) for row in evidence],
        }

    def record_case(
        self,
        query_text: str,
        *,
        access_partitions: tuple[str, ...],
        expected_evidence_ids: tuple[str, ...],
        as_of: str | None = None,
        during: tuple[str, str] | None = None,
        known_as_of: str | None = None,
    ) -> str:
        if not expected_evidence_ids or not access_partitions:
            raise ValueError("retrieval cases require evidence and partitions")
        conn = sqlite3.connect(str(self.db_path), timeout=5)
        conn.row_factory = sqlite3.Row
        try:
            rows = conn.execute(
                f"""SELECT evidence_id FROM evidence_spans
                    WHERE access_partition_id IN (
                        {','.join('?' for _ in access_partitions)}
                    ) AND evidence_id IN (
                        {','.join('?' for _ in expected_evidence_ids)}
                    )""",
                (*access_partitions, *expected_evidence_ids),
            ).fetchall()
            if {row["evidence_id"] for row in rows} != set(expected_evidence_ids):
                raise ValueError("retrieval case evidence is unavailable")
            payload = {
                "query_text": query_text,
                "query_kind": classify_temporal_query(query_text),
                "as_of": as_of,
                "during": list(during) if during else None,
                "known_as_of": known_as_of,
                "access_partitions": sorted(set(access_partitions)),
                "expected_evidence_ids": sorted(set(expected_evidence_ids)),
            }
            case_id = stable_temporal_id("retrieval_case", payload)
            conn.execute(
                """INSERT OR IGNORE INTO temporal_retrieval_cases
                   (case_id, query_text, query_kind, as_of, during_from,
                    during_to, known_as_of, access_partitions_json,
                    expected_evidence_ids_json, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))""",
                (
                    case_id,
                    query_text,
                    payload["query_kind"],
                    as_of,
                    during[0] if during else None,
                    during[1] if during else None,
                    known_as_of,
                    json.dumps(payload["access_partitions"], separators=(",", ":")),
                    json.dumps(
                        payload["expected_evidence_ids"], separators=(",", ":")
                    ),
                ),
            )
            conn.commit()
            return case_id
        finally:
            conn.close()

    def evaluate_case(
        self,
        case_id: str,
        *,
        policy_version: str,
        returned_evidence_ids: tuple[str, ...],
        returned_access_partitions: tuple[str, ...],
        temporal_correct: bool,
    ) -> dict[str, object]:
        conn = sqlite3.connect(str(self.db_path), timeout=5)
        conn.row_factory = sqlite3.Row
        try:
            case = conn.execute(
                "SELECT * FROM temporal_retrieval_cases WHERE case_id = ?",
                (case_id,),
            ).fetchone()
            if case is None:
                raise ValueError("retrieval case does not exist")
            expected = set(json.loads(case["expected_evidence_ids_json"]))
            allowed = set(json.loads(case["access_partitions_json"]))
            returned = set(returned_evidence_ids)
            recall = len(expected & returned) / len(expected)
            access_safe = set(returned_access_partitions) <= allowed
            codes = []
            if recall < 1:
                codes.append("missing_expected_evidence")
            if not temporal_correct:
                codes.append("temporal_filter_mismatch")
            if not access_safe:
                codes.append("access_partition_widened")
            metrics = {
                "evidence_recall": recall,
                "temporal_correct": temporal_correct,
                "access_safe": access_safe,
            }
            result_digest = sha256_json(
                {
                    "returned_evidence_ids": sorted(returned),
                    "returned_access_partitions": sorted(
                        set(returned_access_partitions)
                    ),
                    "metrics": metrics,
                }
            )
            evaluation_id = stable_temporal_id(
                "retrieval_evaluation",
                {
                    "case_id": case_id,
                    "policy_version": policy_version,
                    "result_digest": result_digest,
                },
            )
            conn.execute(
                """INSERT OR IGNORE INTO temporal_retrieval_evaluations
                   (evaluation_id, case_id, policy_version, result_digest,
                    metrics_json, accepted, validation_codes_json, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))""",
                (
                    evaluation_id,
                    case_id,
                    policy_version,
                    result_digest,
                    json.dumps(metrics, sort_keys=True, separators=(",", ":")),
                    int(not codes),
                    json.dumps(codes, separators=(",", ":")),
                ),
            )
            conn.commit()
            return {
                "evaluation_id": evaluation_id,
                "accepted": not codes,
                "validation_codes": codes,
                "metrics": metrics,
            }
        finally:
            conn.close()


class GraphProjectionWorker:
    """Deliver the SQLite outbox; graph loss never changes corpus authority."""

    def __init__(self, db_path: Path, sink: GraphSink) -> None:
        self.db_path = Path(db_path)
        self.sink = sink
        store.init_db(self.db_path)

    def deliver(self, *, limit: int = 100) -> dict[str, int]:
        conn = sqlite3.connect(str(self.db_path), timeout=5)
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """SELECT * FROM graph_projection_outbox
               WHERE state IN ('pending', 'failed')
               ORDER BY created_at, outbox_id LIMIT ?""",
            (limit,),
        ).fetchall()
        published = failed = 0
        try:
            for row in rows:
                try:
                    receipt = self.sink.upsert(
                        aggregate_kind=row["aggregate_kind"],
                        aggregate_id=row["aggregate_id"],
                        payload=json.loads(row["payload_json"]),
                        partition_id=row["access_partition_id"],
                    )
                    conn.execute(
                        """UPDATE graph_projection_outbox
                           SET state = 'published', attempt_count = attempt_count + 1,
                               published_at = datetime('now'), error_code = NULL
                           WHERE outbox_id = ?""",
                        (row["outbox_id"],),
                    )
                    conn.execute(
                        """INSERT INTO graph_projection_receipts
                           (outbox_id, projection_receipt, aggregate_kind,
                            aggregate_id, access_partition_id, published_at)
                           VALUES (?, ?, ?, ?, ?, datetime('now'))
                           ON CONFLICT(outbox_id) DO UPDATE SET
                             projection_receipt = excluded.projection_receipt,
                             published_at = excluded.published_at""",
                        (
                            row["outbox_id"],
                            receipt,
                            row["aggregate_kind"],
                            row["aggregate_id"],
                            row["access_partition_id"],
                        ),
                    )
                    conn.commit()
                    published += 1
                except Exception:
                    conn.execute(
                        """UPDATE graph_projection_outbox
                           SET state = 'failed', attempt_count = attempt_count + 1,
                               error_code = 'projection_unavailable'
                           WHERE outbox_id = ?""",
                        (row["outbox_id"],),
                    )
                    conn.commit()
                    failed += 1
            return {"published": published, "failed": failed}
        finally:
            conn.close()

    def rebuild(self) -> int:
        conn = sqlite3.connect(str(self.db_path), timeout=5)
        try:
            count = conn.execute(
                "SELECT COUNT(*) FROM graph_projection_outbox"
            ).fetchone()[0]
            conn.execute(
                """UPDATE graph_projection_outbox
                   SET state = 'pending', not_before_at = NULL,
                       published_at = NULL, error_code = NULL"""
            )
            conn.commit()
        finally:
            conn.close()
        outcome = self.deliver(limit=max(1, count))
        if outcome["failed"]:
            raise RuntimeError("graph rebuild did not complete")
        return outcome["published"]
