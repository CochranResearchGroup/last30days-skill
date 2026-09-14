"""Provider-free scoring of stored, exact-version source embeddings.

Only the built-in local hash space is queried. Nothing here creates corpus
embeddings, initializes a database, or accepts a network-capable provider.
"""

from __future__ import annotations

import hashlib
import json
import math
import sqlite3
import struct

from .service_contracts import ContractValidationError
from .service_retrieval import LocalHashEmbeddingProvider

RANKING_VERSION = "post-rrf-v1"
RRF_K = 60
MAX_VECTOR_ROWS = 20_000
MAX_VECTOR_BYTES = 32_768


def attach_semantic(
    conn: sqlite3.Connection, rows: list[dict], query: str | None
) -> dict:
    """Score only already filtered, resolved post representatives in one read txn."""
    encoder = LocalHashEmbeddingProvider()
    query_vector = encoder.embed([query])[0] if query else None
    coverage = {
        "model": encoder.model,
        "dimensions": encoder.dimensions,
        "mode": "stored_vectors_local_query" if query else "browse",
        "families": {},
    }
    for family in ("legacy", "temporal"):
        selected = {
            row["version_id"]: row for row in rows if row["storage_family"] == family
        }
        counts = {
            "eligible": len(selected),
            "available": 0,
            "missing": 0,
            "incompatible": 0,
            "invalid": 0,
            "zero_vector": 0,
        }
        coverage["families"][family] = counts
        for row in selected.values():
            row["semantic_score"] = 0.0
            row["semantic_state"] = "missing" if query else "not_requested"
            row["semantic_inputs"] = []
        if not selected or not query:
            continue
        placeholders = ",".join("?" for _ in selected)
        if family == "legacy":
            sql = f"""SELECT c.version_id, c.access_partition_id, c.chunk_id AS locator,
                e.model, e.dimensions,
                CASE WHEN length(e.vector)<={MAX_VECTOR_BYTES} THEN e.vector END AS vector,
                e.vector_hash AS expected_hash
                FROM document_version_chunks c JOIN document_version_embeddings e
                ON e.chunk_id=c.chunk_id JOIN document_versions v ON v.version_id=c.version_id
                AND v.access_partition_id=c.access_partition_id WHERE c.version_id IN ({placeholders})
                ORDER BY c.version_id, c.chunk_id, e.model LIMIT {MAX_VECTOR_ROWS + 1}"""
        else:
            sql = f"""SELECT json_extract(e.provenance_json, '$.version_id') AS version_id,
                e.access_partition_id, e.source, e.text,
                json_extract(e.provenance_json, '$.url') AS url,
                e.snapshot_id || ':' || e.entry_id || ':' || e.channel AS locator,
                s.embedding_space AS model, s.embedding_dimension AS dimensions,
                CASE WHEN length(e.embedding_json)<={MAX_VECTOR_BYTES} THEN e.embedding_json END AS vector,
                NULL AS expected_hash
                FROM service_tick_query_entries e JOIN service_tick_query_snapshots s
                ON s.snapshot_id=e.snapshot_id
                JOIN service_source_versions v ON v.version_id=json_extract(CASE WHEN json_valid(e.provenance_json) THEN e.provenance_json ELSE '{{}}' END, '$.version_id')
                AND v.access_partition_id=e.access_partition_id
                WHERE json_valid(e.provenance_json)
                AND json_extract(e.provenance_json, '$.version_id') IN ({placeholders})
                AND s.state IN ('promoted','superseded') AND s.promoted_at IS NOT NULL
                AND e.channel IN ('lexical_source','semantic_source')
                ORDER BY version_id, e.snapshot_id, e.entry_id, e.channel
                LIMIT {MAX_VECTOR_ROWS + 1}"""
        for index, candidate in enumerate(conn.execute(sql, tuple(selected)), 1):
            if index > MAX_VECTOR_ROWS:
                raise ContractValidationError(
                    "semantic_snapshot_too_large: narrow filters"
                )
            row = selected[candidate["version_id"]]
            if candidate["access_partition_id"] != row["access_partition_id"]:
                continue
            if family == "temporal" and (
                candidate["source"] != row["source"]
                or candidate["url"] != row["canonical_url"]
                or candidate["text"] != f"{row['title']}\n{row['normalized_text']}"
            ):
                continue
            payload = candidate["vector"]
            raw = payload if isinstance(payload, bytes) else str(payload).encode()
            vector_hash = hashlib.sha256(raw).hexdigest()
            reference = {
                "locator": candidate["locator"],
                "vector_sha256": vector_hash,
                "model": candidate["model"],
                "dimensions": candidate["dimensions"],
            }
            row["semantic_inputs"].append(reference)
            state, similarity = "available", 0.0
            if (
                candidate["model"] != encoder.model
                or candidate["dimensions"] != encoder.dimensions
            ):
                state = "incompatible"
            else:
                try:
                    if family == "legacy":
                        if (
                            len(payload) != encoder.dimensions * 8
                            or vector_hash != candidate["expected_hash"]
                        ):
                            raise ValueError("invalid vector bytes")
                        vector = struct.unpack(f"<{encoder.dimensions}d", payload)
                    else:
                        vector = json.loads(payload)
                    if (
                        not isinstance(vector, (list, tuple))
                        or len(vector) != encoder.dimensions
                    ):
                        raise ValueError("invalid vector shape")
                    if any(
                        isinstance(value, bool)
                        or not isinstance(value, (float, int))
                        or not math.isfinite(value)
                        for value in vector
                    ):
                        raise ValueError("nonfinite vector")
                    norm = math.sqrt(sum(value * value for value in vector))
                    if not math.isfinite(norm):
                        raise ValueError("invalid vector norm")
                    if norm == 0:
                        state = "zero_vector"
                    else:
                        similarity = max(
                            -1.0,
                            min(
                                1.0,
                                sum(a * b for a, b in zip(query_vector, vector)) / norm,
                            ),
                        )
                except (
                    ValueError,
                    TypeError,
                    OverflowError,
                    RecursionError,
                    struct.error,
                ):
                    state = "invalid"
            # Prefer usable evidence; within a channel take the best chunk,
            # breaking cosine ties on the immutable stored locator.
            priorities = {
                "missing": 0,
                "incompatible": 1,
                "invalid": 2,
                "zero_vector": 3,
                "available": 4,
            }
            if priorities[state] > priorities[row["semantic_state"]]:
                row["semantic_state"] = state
            if state == "available" and similarity > row["semantic_score"]:
                row["semantic_score"] = similarity
                row["semantic_evidence"] = reference
        for row in selected.values():
            counts[row["semantic_state"]] += 1
    return coverage
