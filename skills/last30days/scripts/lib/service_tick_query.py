"""Immutable tick query snapshots with filter-first multi-channel fusion."""

from __future__ import annotations

import hashlib
import json
import math
import re
import sqlite3
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Protocol

import store


Clock = Callable[[], datetime]
_CHANNELS = frozenset(
    {
        "lexical_source",
        "source_alt_text",
        "ocr",
        "semantic_source",
        "semantic_sidecar",
        "catalog",
    }
)
_SEMANTIC_CHANNELS = frozenset(
    {"semantic_source", "semantic_sidecar", "catalog"}
)
_CHANNEL_ORDER = (
    "lexical_source",
    "source_alt_text",
    "ocr",
    "semantic_source",
    "semantic_sidecar",
    "catalog",
)
_RRF_K = 60
_TOKEN = re.compile(r"[a-z0-9]+")


class EmbeddingProvider(Protocol):
    model: str

    def embed(self, texts: Sequence[str]) -> Sequence[Sequence[float]]: ...


def _canonical_json(value: object) -> str:
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def _digest(value: object) -> str:
    return "sha256:" + hashlib.sha256(_canonical_json(value).encode()).hexdigest()


def _stable_id(prefix: str, value: object) -> str:
    return f"{prefix}-{hashlib.sha256(_canonical_json(value).encode()).hexdigest()[:32]}"


def _text(value: object, field: str, maximum: int = 65_536) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > maximum:
        raise ValueError(f"{field} must be a bounded non-empty string")
    return value


def _now(clock: Clock) -> str:
    value = clock()
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("clock must return a timezone-aware datetime")
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _vector(values: Sequence[object], field: str) -> tuple[float, ...]:
    vector = tuple(float(value) for value in values)
    if not vector or len(vector) > 65_536 or any(not math.isfinite(value) for value in vector):
        raise ValueError(f"{field} must be a bounded finite vector")
    return vector


def _cosine(left: Sequence[float], right: Sequence[float]) -> float:
    if len(left) != len(right):
        raise ValueError("embedding dimensions do not match")
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if not left_norm or not right_norm:
        return 0.0
    return sum(a * b for a, b in zip(left, right, strict=True)) / (
        left_norm * right_norm
    )


@dataclass(frozen=True)
class CatalogMember:
    member_id: str
    source: str
    relationship: str
    evidence_ref: str
    access_partition_id: str
    confidence: float

    def __post_init__(self) -> None:
        _text(self.member_id, "member_id", 128)
        _text(self.source, "source", 64)
        _text(self.relationship, "relationship", 64)
        _text(self.evidence_ref, "evidence_ref", 512)
        _text(self.access_partition_id, "access_partition_id", 256)
        if (
            isinstance(self.confidence, bool)
            or not isinstance(self.confidence, (int, float))
            or not 0 <= float(self.confidence) <= 1
        ):
            raise ValueError("catalog confidence must be between zero and one")

    def to_dict(self) -> dict[str, object]:
        return {
            "member_id": self.member_id,
            "source": self.source,
            "relationship": self.relationship,
            "evidence_ref": self.evidence_ref,
            "access_partition_id": self.access_partition_id,
            "confidence": float(self.confidence),
        }


@dataclass(frozen=True)
class SnapshotEntry:
    entry_id: str
    channel: str
    source: str
    access_partition_id: str
    published_at: str
    text: str
    provenance: dict[str, object]

    def __post_init__(self) -> None:
        _text(self.entry_id, "entry_id", 128)
        if self.channel not in _CHANNELS:
            raise ValueError("snapshot channel is unsupported")
        _text(self.source, "source", 64)
        _text(self.access_partition_id, "access_partition_id", 256)
        _text(self.published_at, "published_at", 64)
        _text(self.text, "text")
        if not isinstance(self.provenance, dict):
            raise ValueError("provenance must be an object")


@dataclass(frozen=True)
class SnapshotReceipt:
    snapshot_id: str
    tick_id: str
    embedding_space: str
    fusion_version: str
    state: str


@dataclass(frozen=True)
class QueryResult:
    entry_id: str
    source: str
    access_partition_id: str
    text: str
    matching_channels: tuple[str, ...]
    score: float
    provenance: dict[str, object]


class TickSnapshotPublisher:
    def __init__(
        self,
        db_path: Path,
        embedding: EmbeddingProvider,
        *,
        clock: Clock | None = None,
    ) -> None:
        self.db_path = Path(db_path)
        self.embedding = embedding
        self.clock = clock or (lambda: datetime.now(timezone.utc))
        store.init_db(self.db_path)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=5)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    @staticmethod
    def _receipt(row: sqlite3.Row) -> SnapshotReceipt:
        return SnapshotReceipt(
            snapshot_id=str(row["snapshot_id"]),
            tick_id=str(row["tick_id"]),
            embedding_space=str(row["embedding_space"]),
            fusion_version=str(row["fusion_version"]),
            state=str(row["state"]),
        )

    def publish_cluster(
        self,
        tick_id: str,
        *,
        cluster_kind: str,
        label: str,
        rationale: str,
        validator_version: str,
        members: Sequence[CatalogMember],
    ) -> str:
        tick = _text(tick_id, "tick_id", 128)
        kind = _text(cluster_kind, "cluster_kind", 64)
        cluster_label = _text(label, "label", 1_024)
        reason = _text(rationale, "rationale", 4_096)
        validator = _text(validator_version, "validator_version", 128)
        if len(members) < 2 or len(members) > 10_000:
            raise ValueError("catalog cluster must have at least two bounded members")
        member_keys = {(member.member_id, member.source) for member in members}
        if len(member_keys) != len(members):
            raise ValueError("catalog cluster members must be unique")
        partitions = {member.access_partition_id for member in members}
        if len(partitions) != 1:
            raise ValueError("catalog cluster cannot cross access partitions")
        partition = next(iter(partitions))
        payload = {
            "tick_id": tick,
            "cluster_kind": kind,
            "label": cluster_label,
            "rationale": reason,
            "validator_version": validator,
            "access_partition_id": partition,
            "members": sorted(
                (member.to_dict() for member in members),
                key=lambda item: (str(item["source"]), str(item["member_id"])),
            ),
        }
        cluster_digest = _digest(payload)
        cluster_id = _stable_id("catalog-cluster", payload)
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            if conn.execute(
                "SELECT 1 FROM service_ticks WHERE tick_id = ?", (tick,)
            ).fetchone() is None:
                raise KeyError(f"unknown tick: {tick}")
            conn.execute(
                """INSERT OR IGNORE INTO service_catalog_clusters (
                       cluster_id, tick_id, cluster_kind, label, rationale,
                       validator_version, access_partition_id, cluster_digest,
                       created_at
                   ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    cluster_id,
                    tick,
                    kind,
                    cluster_label,
                    reason,
                    validator,
                    partition,
                    cluster_digest,
                    _now(self.clock),
                ),
            )
            for member in members:
                conn.execute(
                    """INSERT OR IGNORE INTO service_catalog_cluster_members (
                           cluster_id, member_id, source, relationship,
                           evidence_ref, access_partition_id, confidence
                       ) VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (
                        cluster_id,
                        member.member_id,
                        member.source,
                        member.relationship,
                        member.evidence_ref,
                        member.access_partition_id,
                        float(member.confidence),
                    ),
                )
            count = int(
                conn.execute(
                    """SELECT COUNT(*) FROM service_catalog_cluster_members
                       WHERE cluster_id = ?""",
                    (cluster_id,),
                ).fetchone()[0]
            )
            if count != len(members):
                raise ValueError("immutable catalog cluster conflict")
            conn.commit()
            return cluster_id
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def stage(
        self,
        tick_id: str,
        *,
        embedding_space: str,
        fusion_version: str,
        completeness: Mapping[str, object],
    ) -> SnapshotReceipt:
        tick = _text(tick_id, "tick_id", 128)
        space = _text(embedding_space, "embedding_space", 128)
        fusion = _text(fusion_version, "fusion_version", 128)
        if fusion != "rrf-v1":
            raise ValueError("unsupported deterministic fusion version")
        if self.embedding.model != space:
            raise ValueError("embedding provider does not match snapshot space")
        if not isinstance(completeness, Mapping):
            raise ValueError("completeness must be an object")
        identity = {
            "tick_id": tick,
            "embedding_space": space,
            "fusion_version": fusion,
            "completeness": dict(completeness),
        }
        snapshot_id = _stable_id("tick-snapshot", identity)
        conn = self._connect()
        try:
            if conn.execute(
                "SELECT 1 FROM service_ticks WHERE tick_id = ?", (tick,)
            ).fetchone() is None:
                raise KeyError(f"unknown tick: {tick}")
            conn.execute(
                """INSERT OR IGNORE INTO service_tick_query_snapshots (
                       snapshot_id, tick_id, embedding_space, fusion_version,
                       completeness_json, snapshot_digest, state, created_at
                   ) VALUES (?, ?, ?, ?, ?, ?, 'staging', ?)""",
                (
                    snapshot_id,
                    tick,
                    space,
                    fusion,
                    _canonical_json(dict(completeness)),
                    _digest(identity),
                    _now(self.clock),
                ),
            )
            row = conn.execute(
                "SELECT * FROM service_tick_query_snapshots WHERE snapshot_id = ?",
                (snapshot_id,),
            ).fetchone()
            conn.commit()
            return self._receipt(row)
        finally:
            conn.close()

    def add_entries(
        self, snapshot_id: str, entries: Sequence[SnapshotEntry]
    ) -> None:
        if not entries:
            return
        embeddings = self.embedding.embed([entry.text for entry in entries])
        if len(embeddings) != len(entries):
            raise ValueError("embedding provider returned the wrong count")
        vectors = tuple(
            _vector(vector, f"embedding[{index}]")
            for index, vector in enumerate(embeddings)
        )
        dimensions = {len(vector) for vector in vectors}
        if len(dimensions) != 1:
            raise ValueError("embedding provider returned mixed dimensions")
        dimension = dimensions.pop()
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            snapshot = conn.execute(
                "SELECT * FROM service_tick_query_snapshots WHERE snapshot_id = ?",
                (snapshot_id,),
            ).fetchone()
            if snapshot is None:
                raise KeyError(f"unknown snapshot: {snapshot_id}")
            if snapshot["state"] != "staging":
                raise ValueError("only a staging snapshot accepts entries")
            if snapshot["embedding_space"] != self.embedding.model:
                raise ValueError("embedding spaces cannot be mixed")
            if snapshot["embedding_dimension"] not in (None, dimension):
                raise ValueError("embedding dimensions cannot be mixed")
            conn.execute(
                """UPDATE service_tick_query_snapshots
                   SET embedding_dimension = COALESCE(embedding_dimension, ?)
                   WHERE snapshot_id = ?""",
                (dimension, snapshot_id),
            )
            for entry, vector in zip(entries, vectors, strict=True):
                payload = {
                    "entry_id": entry.entry_id,
                    "channel": entry.channel,
                    "source": entry.source,
                    "access_partition_id": entry.access_partition_id,
                    "published_at": entry.published_at,
                    "text": entry.text,
                    "provenance": entry.provenance,
                }
                conn.execute(
                    """INSERT OR IGNORE INTO service_tick_query_entries (
                           snapshot_id, entry_id, channel, source,
                           access_partition_id, published_at, text,
                           embedding_json, provenance_json, entry_digest
                       ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        snapshot_id,
                        entry.entry_id,
                        entry.channel,
                        entry.source,
                        entry.access_partition_id,
                        entry.published_at,
                        entry.text,
                        _canonical_json(list(vector)),
                        _canonical_json(entry.provenance),
                        _digest(payload),
                    ),
                )
                row = conn.execute(
                    """SELECT entry_digest FROM service_tick_query_entries
                       WHERE snapshot_id = ? AND entry_id = ? AND channel = ?""",
                    (snapshot_id, entry.entry_id, entry.channel),
                ).fetchone()
                if row["entry_digest"] != _digest(payload):
                    raise ValueError("immutable snapshot entry conflict")
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def promote(self, snapshot_id: str) -> SnapshotReceipt:
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            snapshot = conn.execute(
                "SELECT * FROM service_tick_query_snapshots WHERE snapshot_id = ?",
                (snapshot_id,),
            ).fetchone()
            if snapshot is None:
                raise KeyError(f"unknown snapshot: {snapshot_id}")
            tick = conn.execute(
                "SELECT state FROM service_ticks WHERE tick_id = ?",
                (snapshot["tick_id"],),
            ).fetchone()
            if tick["state"] not in {"complete", "complete_degraded"}:
                raise ValueError("snapshot tick is not terminal")
            incomplete = int(
                conn.execute(
                    """SELECT COUNT(*) FROM service_tick_stages
                       WHERE tick_id = ? AND state IN ('pending', 'running')
                         AND stage_name <> 'head_promotion'""",
                    (snapshot["tick_id"],),
                ).fetchone()[0]
            )
            if incomplete:
                raise ValueError("snapshot has incomplete tick stages")
            now = _now(self.clock)
            conn.execute(
                """UPDATE service_tick_query_snapshots SET state = 'superseded'
                   WHERE state = 'promoted' AND snapshot_id <> ?""",
                (snapshot_id,),
            )
            conn.execute(
                """UPDATE service_tick_query_snapshots
                   SET state = 'promoted', promoted_at = ? WHERE snapshot_id = ?""",
                (now, snapshot_id),
            )
            conn.execute(
                """INSERT INTO service_tick_query_head (
                       singleton_id, snapshot_id, promoted_at
                   ) VALUES (1, ?, ?)
                   ON CONFLICT(singleton_id) DO UPDATE SET
                     snapshot_id = excluded.snapshot_id,
                     promoted_at = excluded.promoted_at""",
                (snapshot_id, now),
            )
            row = conn.execute(
                "SELECT * FROM service_tick_query_snapshots WHERE snapshot_id = ?",
                (snapshot_id,),
            ).fetchone()
            conn.commit()
            return self._receipt(row)
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def current(self) -> SnapshotReceipt:
        conn = self._connect()
        try:
            row = conn.execute(
                """SELECT s.* FROM service_tick_query_head AS h
                   JOIN service_tick_query_snapshots AS s
                     ON s.snapshot_id = h.snapshot_id
                   WHERE h.singleton_id = 1"""
            ).fetchone()
            if row is None:
                raise KeyError("ordinary query head is not initialized")
            return self._receipt(row)
        finally:
            conn.close()

    def query(
        self,
        query: str,
        *,
        access_partitions: Sequence[str],
        sources: Sequence[str] | None = None,
        published_after: str | None = None,
        limit: int = 20,
    ) -> tuple[QueryResult, ...]:
        query_text = _text(query, "query", 4_096)
        if not access_partitions:
            raise ValueError("access_partitions must not be empty")
        if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 100:
            raise ValueError("limit must be between 1 and 100")
        conn = self._connect()
        try:
            head = conn.execute(
                """SELECT h.snapshot_id, s.fusion_version
                   FROM service_tick_query_head AS h
                   JOIN service_tick_query_snapshots AS s
                     ON s.snapshot_id = h.snapshot_id
                   WHERE h.singleton_id = 1"""
            ).fetchone()
            if head is None:
                return ()
            if head["fusion_version"] != "rrf-v1":
                raise ValueError("ordinary query head has unsupported fusion version")
            predicates = ["snapshot_id = ?"]
            parameters: list[object] = [head["snapshot_id"]]
            placeholders = ",".join("?" for _ in access_partitions)
            predicates.append(f"access_partition_id IN ({placeholders})")
            parameters.extend(access_partitions)
            if sources:
                source_placeholders = ",".join("?" for _ in sources)
                predicates.append(f"source IN ({source_placeholders})")
                parameters.extend(sources)
            if published_after is not None:
                predicates.append("published_at >= ?")
                parameters.append(published_after)
            rows = conn.execute(
                "SELECT * FROM service_tick_query_entries WHERE "
                + " AND ".join(predicates),
                parameters,
            ).fetchall()
        finally:
            conn.close()
        query_vector = _vector(self.embedding.embed([query_text])[0], "query embedding")
        query_tokens = set(_TOKEN.findall(query_text.casefold()))
        candidates: dict[str, list[tuple[sqlite3.Row, float, dict[str, object]]]] = {}
        for row in rows:
            if row["channel"] in _SEMANTIC_CHANNELS:
                score = _cosine(query_vector, json.loads(row["embedding_json"]))
            else:
                candidate_tokens = set(_TOKEN.findall(str(row["text"]).casefold()))
                score = (
                    len(query_tokens & candidate_tokens) / len(query_tokens)
                    if query_tokens
                    else 0.0
                )
            if score <= 0:
                continue
            channel = str(row["channel"])
            candidates.setdefault(channel, []).append(
                (row, score, dict(json.loads(row["provenance_json"])))
            )

        fused: dict[
            tuple[str, str, str],
            dict[str, object],
        ] = {}
        for channel in _CHANNEL_ORDER:
            ranked = sorted(
                candidates.get(channel, ()),
                key=lambda item: (-item[1], str(item[0]["entry_id"])),
            )
            for rank, (row, raw_score, provenance) in enumerate(ranked, start=1):
                canonical_id = provenance.get("version_id")
                if not isinstance(canonical_id, str) or not canonical_id:
                    canonical_id = str(row["entry_id"])
                key = (
                    canonical_id,
                    str(row["source"]),
                    str(row["access_partition_id"]),
                )
                bucket = fused.setdefault(
                    key,
                    {
                        "score": 0.0,
                        "channels": set(),
                        "candidates": [],
                        "entries": {},
                    },
                )
                bucket["score"] = float(bucket["score"]) + 1.0 / (_RRF_K + rank)
                bucket["channels"].add(channel)
                bucket["candidates"].append((row, raw_score, provenance))
                bucket["entries"].setdefault(channel, []).append(str(row["entry_id"]))

        results: list[QueryResult] = []
        channel_rank = {channel: index for index, channel in enumerate(_CHANNEL_ORDER)}
        for (canonical_id, source, partition), bucket in fused.items():
            representative = sorted(
                bucket["candidates"],
                key=lambda item: (
                    -item[1],
                    channel_rank[str(item[0]["channel"])],
                    str(item[0]["entry_id"]),
                ),
            )[0]
            row, _, provenance = representative
            combined_provenance = dict(provenance)
            combined_provenance["matching_entries"] = {
                channel: sorted(bucket["entries"][channel])
                for channel in _CHANNEL_ORDER
                if channel in bucket["entries"]
            }
            results.append(
                QueryResult(
                    entry_id=canonical_id,
                    source=source,
                    access_partition_id=partition,
                    text=str(row["text"]),
                    matching_channels=tuple(
                        channel
                        for channel in _CHANNEL_ORDER
                        if channel in bucket["channels"]
                    ),
                    score=float(bucket["score"]),
                    provenance=combined_provenance,
                )
            )
        return tuple(
            sorted(results, key=lambda item: (-item.score, item.entry_id))[:limit]
        )
