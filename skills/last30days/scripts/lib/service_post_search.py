"""Cache-only lexical search across both durable stored-post families."""

from __future__ import annotations

import base64
import hashlib
import json
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Mapping, Sequence

from . import service_contracts as contracts


_TOKEN = re.compile(r"[a-z0-9]+")


def _canonical_json(value: object) -> str:
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical_json(value).encode()).hexdigest()


def _stable_id(prefix: str, value: object) -> str:
    return f"{prefix}-{_digest(value)[:32]}"


class PostSearchBackend:
    """Deep search module hiding storage federation and cursor integrity."""

    def __init__(
        self,
        db_path: Path,
        *,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self.db_path = Path(db_path)
        self.clock = clock or (lambda: datetime.now(timezone.utc))

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=5)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA query_only=ON")
        conn.execute("PRAGMA busy_timeout=5000")
        return conn

    @staticmethod
    def _component_heads(
        conn: sqlite3.Connection,
        access_partitions: Sequence[str],
    ) -> dict[str, str]:
        placeholders = ",".join("?" for _ in access_partitions)
        legacy = conn.execute(
            f"""SELECT d.document_id, d.current_version_id
                FROM documents AS d
                WHERE d.access_partition_id IN ({placeholders})
                ORDER BY d.document_id""",
            tuple(access_partitions),
        ).fetchall()
        temporal = conn.execute(
            f"""SELECT record_id, current_version_id
                FROM service_source_records
                WHERE access_partition_id IN ({placeholders})
                ORDER BY record_id""",
            tuple(access_partitions),
        ).fetchall()
        return {
            "legacy": "legacy-head-"
            + _digest([[row[0], row[1]] for row in legacy])[:32],
            "temporal": "temporal-head-"
            + _digest([[row[0], row[1]] for row in temporal])[:32],
        }

    @staticmethod
    def _request_fingerprint(
        request: contracts.PostSearchRequest,
        access_partitions: Sequence[str],
    ) -> str:
        return _digest(
            {
                "schema_version": request.schema_version,
                "profile_id": request.profile_id,
                "query": request.query,
                "filters": request.filters,
                "page_size": request.page_size,
                "access_partitions": sorted(access_partitions),
                "sort": "relevance",
                "revision_mode": "current",
            }
        )

    @staticmethod
    def _encode_cursor(
        *,
        fingerprint: str,
        search_head_id: str,
        last: tuple[float, str, str],
    ) -> str:
        core = {
            "version": 1,
            "fingerprint": fingerprint,
            "search_head_id": search_head_id,
            "last": [last[0], last[1], last[2]],
        }
        envelope = {**core, "checksum": _digest(core)}
        return base64.urlsafe_b64encode(_canonical_json(envelope).encode()).decode().rstrip("=")

    @staticmethod
    def _decode_cursor(cursor: str) -> Mapping[str, object]:
        try:
            padded = cursor + "=" * (-len(cursor) % 4)
            payload = json.loads(base64.urlsafe_b64decode(padded).decode())
        except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise contracts.ContractValidationError("cursor is invalid") from exc
        if not isinstance(payload, dict):
            raise contracts.ContractValidationError("cursor is invalid")
        checksum = payload.pop("checksum", None)
        if checksum != _digest(payload):
            raise contracts.ContractValidationError("cursor checksum is invalid")
        if set(payload) != {"version", "fingerprint", "search_head_id", "last"}:
            raise contracts.ContractValidationError("cursor fields are invalid")
        last = payload["last"]
        if (
            payload["version"] != 1
            or not isinstance(payload["fingerprint"], str)
            or not isinstance(payload["search_head_id"], str)
            or not isinstance(last, list)
            or len(last) != 3
            or isinstance(last[0], bool)
            or not isinstance(last[0], (int, float))
            or not isinstance(last[1], str)
            or not isinstance(last[2], str)
        ):
            raise contracts.ContractValidationError("cursor payload is invalid")
        return payload

    @staticmethod
    def _filter_sql(
        *,
        request: contracts.PostSearchRequest,
        access_partitions: Sequence[str],
        source_column: str,
        partition_column: str,
        published_column: str,
    ) -> tuple[str, list[object]]:
        placeholders = ",".join("?" for _ in access_partitions)
        predicates = [f"{partition_column} IN ({placeholders})"]
        parameters: list[object] = list(access_partitions)
        sources = request.filters.get("sources")
        if sources:
            source_placeholders = ",".join("?" for _ in sources)
            predicates.append(f"{source_column} IN ({source_placeholders})")
            parameters.extend(sources)
        if "published_after" in request.filters:
            predicates.append(f"{published_column} >= ?")
            parameters.append(request.filters["published_after"])
        if "published_before" in request.filters:
            predicates.append(f"{published_column} <= ?")
            parameters.append(request.filters["published_before"])
        return " AND ".join(predicates), parameters

    def _rows(
        self,
        conn: sqlite3.Connection,
        request: contracts.PostSearchRequest,
        access_partitions: Sequence[str],
    ) -> list[sqlite3.Row]:
        legacy_where, legacy_params = self._filter_sql(
            request=request,
            access_partitions=access_partitions,
            source_column="d.source",
            partition_column="v.access_partition_id",
            published_column="v.published_at",
        )
        temporal_where, temporal_params = self._filter_sql(
            request=request,
            access_partitions=access_partitions,
            source_column="r.source",
            partition_column="v.access_partition_id",
            published_column="v.published_at",
        )
        legacy = conn.execute(
            f"""SELECT 'legacy' AS storage_family,
                       d.document_id AS origin_id, d.source, d.source_native_id,
                       d.canonical_url, v.version_id, v.content_hash, v.title,
                       v.author, v.normalized_text, v.published_at,
                       v.observed_at, v.access_partition_id
                FROM documents AS d
                JOIN document_versions AS v
                  ON v.version_id = d.current_version_id
                WHERE {legacy_where}
                  AND v.access_partition_id = d.access_partition_id""",
            legacy_params,
        ).fetchall()
        temporal = conn.execute(
            f"""SELECT 'temporal' AS storage_family,
                       r.record_id AS origin_id, r.source, r.source_native_id,
                       r.canonical_url, v.version_id, v.content_hash, v.title,
                       v.author, v.normalized_text, v.published_at,
                       v.observed_at, v.access_partition_id
                FROM service_source_records AS r
                JOIN service_source_versions AS v
                  ON v.version_id = r.current_version_id
                WHERE {temporal_where}
                  AND v.access_partition_id = r.access_partition_id""",
            temporal_params,
        ).fetchall()
        return [*legacy, *temporal]

    def search(
        self,
        request: contracts.PostSearchRequest,
        *,
        access_partitions: Sequence[str],
    ) -> contracts.PostSearchResponse:
        partitions = tuple(dict.fromkeys(access_partitions))
        if not partitions or not all(
            isinstance(partition, str) and partition for partition in partitions
        ):
            raise contracts.ContractValidationError(
                "authorized access partitions must not be empty"
            )
        fingerprint = self._request_fingerprint(request, partitions)
        conn = self._connect()
        try:
            conn.execute("BEGIN")
            heads = self._component_heads(conn, partitions)
            search_head_id = "search-head-" + _digest(heads)[:32]
            cursor_payload = None
            if request.cursor is not None:
                cursor_payload = self._decode_cursor(request.cursor)
                if cursor_payload["fingerprint"] != fingerprint:
                    raise contracts.ContractValidationError(
                        "cursor request fingerprint does not match"
                    )
                if cursor_payload["search_head_id"] != search_head_id:
                    raise contracts.ContractValidationError("cursor is stale")
            rows = self._rows(conn, request, partitions)
        finally:
            conn.close()

        query_tokens = set(_TOKEN.findall(request.query.casefold()))
        hits: list[contracts.PostSearchHit] = []
        for row in rows:
            candidate = " ".join(
                str(value or "")
                for value in (row["title"], row["author"], row["normalized_text"])
            )
            candidate_tokens = set(_TOKEN.findall(candidate.casefold()))
            score = len(query_tokens & candidate_tokens) / len(query_tokens)
            if score <= 0:
                continue
            identity = {
                "source": row["source"],
                "source_native_id": row["source_native_id"],
                "access_partition_id": row["access_partition_id"],
            }
            hit_payload = {
                "post_id": _stable_id("post", identity),
                "revision_id": str(row["version_id"]),
                "storage_family": str(row["storage_family"]),
                "source": str(row["source"]),
                "source_native_id": str(row["source_native_id"]),
                "url": str(row["canonical_url"]),
                "title": str(row["title"] or row["canonical_url"]),
                "author": str(row["author"]) if row["author"] else None,
                "text": str(row["normalized_text"])[:4096],
                "published_at": (
                    str(row["published_at"]) if row["published_at"] else None
                ),
                "observed_at": str(row["observed_at"]),
                "access_partition_id": str(row["access_partition_id"]),
                "score": score,
                "matching_channels": ["lexical"],
                "evidence_ref": {
                    "storage_family": str(row["storage_family"]),
                    "version_id": str(row["version_id"]),
                    "content_hash": str(row["content_hash"]),
                    "source_url": str(row["canonical_url"]),
                },
            }
            hits.append(contracts.PostSearchHit.from_dict(hit_payload))
        hits.sort(key=lambda hit: (-hit.score, hit.post_id, hit.revision_id))

        if cursor_payload is not None:
            raw_last = cursor_payload["last"]
            assert isinstance(raw_last, list)
            last_key = (-float(raw_last[0]), str(raw_last[1]), str(raw_last[2]))
            hits = [
                hit
                for hit in hits
                if (-hit.score, hit.post_id, hit.revision_id) > last_key
            ]
        truncated = len(hits) > request.page_size
        selected = hits[: request.page_size]
        next_cursor = None
        if truncated and selected:
            last = selected[-1]
            next_cursor = self._encode_cursor(
                fingerprint=fingerprint,
                search_head_id=search_head_id,
                last=(last.score, last.post_id, last.revision_id),
            )
        generated_at = self.clock().astimezone(timezone.utc).isoformat().replace(
            "+00:00", "Z"
        )
        return contracts.PostSearchResponse.from_dict(
            {
                "schema_version": contracts.SCHEMA_VERSION,
                "request_id": request.request_id,
                "search_head_id": search_head_id,
                "generated_at": generated_at,
                "query": request.query,
                "filters": request.filters,
                "sort": "relevance",
                "revision_mode": "current",
                "hits": [hit.to_dict() for hit in selected],
                "returned": len(selected),
                "truncated": truncated,
                "next_cursor": next_cursor,
                "coverage": {
                    "component_heads": heads,
                    "storage_families": ["legacy", "temporal"],
                    "unavailable_filters": [
                        "authors",
                        "collection_refs",
                        "topic_ids",
                        "observed_after",
                        "observed_before",
                    ],
                },
            }
        )
