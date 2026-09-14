"""Read-only post federation with bounded, immutable in-process search heads."""

from __future__ import annotations

import base64
import hashlib
import json
import math
import re
import sqlite3
import threading
import time
from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Sequence

from . import service_contracts as contracts

_TOKEN = re.compile(r"[a-z0-9]+")
MAX_SNAPSHOT_ROWS = 10_000
MAX_RETAINED_BYTES = 32 * 1024 * 1024


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
    """Filter in SQL, rank once, and retain bounded immutable result heads.

    Heads expire after 15 minutes or FIFO eviction (16 heads / 32 MiB by
    default), and never survive a restart. A cursor is a locator, not authority.
    No search writes to the source database or acquires provider data.
    """

    def __init__(
        self,
        db_path: Path,
        *,
        clock: Callable[[], datetime] | None = None,
        snapshot_capacity: int = 16,
        snapshot_ttl_seconds: float = 900,
        monotonic: Callable[[], float] = time.monotonic,
    ) -> None:
        if snapshot_capacity < 1 or snapshot_ttl_seconds <= 0:
            raise ValueError("snapshot retention limits must be positive")
        self.db_path = Path(db_path)
        self.clock = clock or (lambda: datetime.now(timezone.utc))
        self.snapshot_capacity = snapshot_capacity
        self.snapshot_ttl_seconds = snapshot_ttl_seconds
        self.monotonic = monotonic
        self._snapshots: OrderedDict[tuple[str, str], tuple] = OrderedDict()
        self._snapshot_lock = threading.Lock()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(
            self.db_path.resolve().as_uri() + "?mode=ro", uri=True, timeout=5
        )
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA query_only=ON")
        conn.execute("PRAGMA busy_timeout=5000")
        return conn

    @staticmethod
    def _request_fingerprint(
        request: contracts.PostSearchRequest, partitions: Sequence[str]
    ) -> str:
        payload = request.to_dict()
        payload.pop("request_id")
        payload.pop("cursor")
        payload["access_partitions"] = sorted(partitions)
        return _digest(payload)

    @staticmethod
    def _encode_cursor(
        fingerprint: str, head: str, components: dict, last: tuple
    ) -> str:
        core = {
            "version": 2,
            "fingerprint": fingerprint,
            "search_head_id": head,
            "component_heads": components,
            "last": list(last),
        }
        envelope = {**core, "checksum": _digest(core)}
        return (
            base64.urlsafe_b64encode(_canonical_json(envelope).encode())
            .decode()
            .rstrip("=")
        )

    @staticmethod
    def _decode_cursor(cursor: str) -> dict:
        try:
            payload = json.loads(
                base64.b64decode(
                    cursor + "=" * (-len(cursor) % 4), altchars=b"-_", validate=True
                )
            )
            if not isinstance(payload, dict):
                raise ValueError("not an object")
            checksum = payload.pop("checksum", None)
            if checksum != _digest(payload) or set(payload) != {
                "version",
                "fingerprint",
                "search_head_id",
                "component_heads",
                "last",
            }:
                raise ValueError("invalid envelope")
            if (
                payload["version"] != 2
                or not isinstance(payload["fingerprint"], str)
                or not isinstance(payload["search_head_id"], str)
            ):
                raise ValueError("invalid identity")
            if not isinstance(payload["component_heads"], dict) or set(
                payload["component_heads"]
            ) != {"legacy", "temporal"}:
                raise ValueError("invalid component heads")
            if not all(
                isinstance(value, str) for value in payload["component_heads"].values()
            ):
                raise ValueError("invalid component identity")
            if not isinstance(payload["last"], list) or len(payload["last"]) != 3:
                raise ValueError("invalid position")
            last = payload["last"]
            if (
                isinstance(last[0], bool)
                or not isinstance(last[0], (int, float))
                or not math.isfinite(last[0])
                or not all(isinstance(value, str) for value in last[1:])
            ):
                raise ValueError("invalid position types")
            return payload
        except (ValueError, TypeError, UnicodeDecodeError, RecursionError) as exc:
            raise contracts.ContractValidationError("cursor is invalid") from exc

    @staticmethod
    def _filter_sql(
        request: contracts.PostSearchRequest, partitions: Sequence[str]
    ) -> tuple[str, list]:
        predicates = [
            "access_partition_id IN (" + ",".join("?" for _ in partitions) + ")"
        ]
        params: list = list(partitions)
        for field, column in (("sources", "source"), ("authors", "author")):
            if field in request.filters:
                values = request.filters[field]
                predicates.append(f"{column} IN ({','.join('?' for _ in values)})")
                params.extend(values)
        for field in ("topic_ids", "collection_refs"):
            if field in request.filters:
                values = request.filters[field]
                predicates.append(
                    f"EXISTS (SELECT 1 FROM json_each({field}) WHERE value IN ({','.join('?' for _ in values)}))"
                )
                params.extend(values)
        for prefix in ("published", "observed"):
            bounds = []
            for suffix, op in (("after", ">="), ("before", "<=")):
                key = f"{prefix}_{suffix}"
                if key in request.filters:
                    column = "value" if prefix == "observed" else "published_at"
                    bounds.append(f"julianday({column}) {op} julianday(?)")
                    params.append(request.filters[key])
            if bounds:
                predicate = " AND ".join(bounds)
                if prefix == "observed":
                    predicate = f"EXISTS (SELECT 1 FROM json_each(observations) WHERE {predicate})"
                predicates.append(predicate)
        return " AND ".join(predicates), params

    def _rows(
        self,
        conn: sqlite3.Connection,
        request: contracts.PostSearchRequest,
        partitions: Sequence[str],
    ) -> list[dict]:
        """Missing filter evidence excludes a version before scoring or dedupe.

        Legacy topics/causes use partition-matched version sightings. Temporal
        topics use explicit string topic_ids in immutable metadata; causes use
        partition-matched tick sightings. Observed bounds match one observation.
        """
        where, params = self._filter_sql(request, partitions)
        result = []
        for family in ("legacy", "temporal"):
            if family == "legacy":
                origins, versions, origin_key = (
                    "documents",
                    "document_versions",
                    "document_id",
                )
                sightings = """SELECT s.observed_at, CAST(s.topic_id AS TEXT) AS topic_id,
                    'legacy:spec:' || s.collection_spec_id AS spec_ref,
                    'legacy:run:' || s.collection_run_id AS run_ref
                    FROM document_version_sightings s
                    WHERE s.version_id = v.version_id AND s.access_partition_id = v.access_partition_id"""
                topics = f"SELECT topic_id AS value FROM ({sightings}) WHERE topic_id IS NOT NULL"
                refs = f"SELECT spec_ref AS value FROM ({sightings}) WHERE spec_ref IS NOT NULL UNION SELECT run_ref FROM ({sightings}) WHERE run_ref IS NOT NULL"
            else:
                origins, versions, origin_key = (
                    "service_source_records",
                    "service_source_versions",
                    "record_id",
                )
                sightings = """SELECT s.observed_at, 'temporal:schedule:' || t.schedule_id AS schedule_ref,
                    'temporal:target:' || l.service_id || ':' || l.target_id AS target_ref,
                    'temporal:tick:' || s.tick_id AS tick_ref, 'temporal:lane:' || s.lane_id AS lane_ref
                    FROM service_source_sightings s
                    JOIN service_tick_lanes l ON l.lane_id=s.lane_id AND l.tick_id=s.tick_id
                    JOIN service_ticks t ON t.tick_id=s.tick_id
                    WHERE s.version_id=v.version_id AND l.access_partition_id=v.access_partition_id"""
                topics = """SELECT value FROM json_each(CASE WHEN json_valid(v.metadata_json)
                    AND json_type(v.metadata_json, '$.topic_ids') = 'array'
                    THEN json_extract(v.metadata_json, '$.topic_ids') ELSE '[]' END)
                    WHERE type='text' AND length(value) BETWEEN 1 AND 128"""
                refs = " UNION ".join(
                    f"SELECT {name}_ref AS value FROM ({sightings})"
                    for name in ("schedule", "target", "tick", "lane")
                )
            revision_join = (
                "v.version_id = o.current_version_id"
                if request.revision_mode == "current"
                else f"v.{origin_key}=o.{origin_key}"
            )
            rows = conn.execute(
                f"""WITH candidates AS (
                SELECT '{family}' AS storage_family, o.{origin_key} AS origin_id,
                    o.source, NULLIF(o.source_native_id, '') AS source_native_id,
                    o.canonical_url, v.version_id, v.content_hash, v.title,
                    v.author, v.normalized_text, v.published_at, v.observed_at,
                    v.access_partition_id,
                    (SELECT json_group_array(value) FROM ({topics})) AS topic_ids,
                    (SELECT json_group_array(value) FROM ({refs})) AS collection_refs,
                    (SELECT json_group_array(observed_at) FROM (
                        SELECT v.observed_at AS observed_at UNION SELECT observed_at FROM ({sightings})
                    )) AS observations
                FROM {origins} o JOIN {versions} v ON {revision_join}
                WHERE v.access_partition_id=o.access_partition_id
            ) SELECT * FROM candidates WHERE {where} ORDER BY origin_id, version_id
              LIMIT {MAX_SNAPSHOT_ROWS + 1}""",
                params,
            ).fetchall()
            result.extend(dict(row) for row in rows)
            if len(result) > MAX_SNAPSHOT_ROWS:
                raise contracts.ContractValidationError(
                    "search_snapshot_too_large: narrow filters"
                )
        return result

    @staticmethod
    def _sort_key(hit: contracts.PostSearchHit, sort: str) -> tuple:
        if sort == "relevance":
            value = -hit.score
        else:
            timestamp = (
                hit.published_at if sort == "published_desc" else hit.observed_at
            )
            value = (
                -datetime.fromisoformat(timestamp.replace("Z", "+00:00")).timestamp()
                if timestamp
                else 1e20
            )
        return value, hit.post_id, hit.revision_id

    def _rank(
        self, rows: list[dict], request: contracts.PostSearchRequest
    ) -> tuple[contracts.PostSearchHit, ...]:
        tokens = set(_TOKEN.findall((request.query or "").casefold()))
        groups: dict[tuple, list] = {}
        for row in rows:
            identity = {
                "source": row["source"],
                "source_native_id": row["source_native_id"],
                "access_partition_id": row["access_partition_id"],
            }
            if not row["source_native_id"]:
                identity["canonical_url"] = row["canonical_url"]
            row["post_id"] = _stable_id("post", identity)
            key = (
                (row["post_id"], row["content_hash"])
                if request.revision_mode == "all"
                else (row["post_id"],)
            )
            groups.setdefault(key, []).append(row)
        hits = []
        for group in groups.values():
            # Resolve current conflicts before scoring so a stale matching
            # replica cannot replace a newer nonmatching current revision.
            group.sort(
                key=lambda row: (
                    -datetime.fromisoformat(
                        row["observed_at"].replace("Z", "+00:00")
                    ).timestamp(),
                    row["storage_family"],
                    row["version_id"],
                )
            )
            row = group[0]
            candidate = " ".join(
                str(row[field] or "")
                for field in ("title", "author", "normalized_text")
            )
            score = (
                len(tokens & set(_TOKEN.findall(candidate.casefold()))) / len(tokens)
                if tokens
                else 0.0
            )
            if tokens and score == 0:
                continue
            refs = [
                {
                    "storage_family": r["storage_family"],
                    "version_id": r["version_id"],
                    "content_hash": r["content_hash"],
                    "source_url": r["canonical_url"],
                }
                for r in group
            ]
            observations = [
                value for r in group for value in json.loads(r["observations"])
            ]
            observed = max(
                observations,
                key=lambda value: datetime.fromisoformat(value.replace("Z", "+00:00")),
            )
            hits.append(
                contracts.PostSearchHit.from_dict(
                    {
                        "post_id": row["post_id"],
                        "revision_id": row["version_id"],
                        "storage_family": row["storage_family"],
                        "source": row["source"],
                        "source_native_id": row["source_native_id"],
                        "url": row["canonical_url"],
                        "title": row["title"] or row["canonical_url"],
                        "author": row["author"] or None,
                        "text": row["normalized_text"][:4096],
                        "published_at": row["published_at"],
                        "observed_at": observed,
                        "access_partition_id": row["access_partition_id"],
                        "score": score,
                        "matching_channels": ["lexical"] if tokens else [],
                        "evidence_ref": refs[0],
                        "evidence_refs": refs,
                        "collection_refs": sorted(
                            {
                                value
                                for r in group
                                for value in json.loads(r["collection_refs"])
                            }
                        ),
                        "topic_ids": sorted(
                            {
                                value
                                for r in group
                                for value in json.loads(r["topic_ids"])
                            }
                        ),
                    }
                )
            )
        return tuple(sorted(hits, key=lambda hit: self._sort_key(hit, request.sort)))

    def _expire(self, now: float) -> None:
        for key, snapshot in list(self._snapshots.items()):
            if now - snapshot[0] >= self.snapshot_ttl_seconds:
                del self._snapshots[key]

    def search(
        self, request: contracts.PostSearchRequest, *, access_partitions: Sequence[str]
    ) -> contracts.PostSearchResponse:
        request = contracts.PostSearchRequest.from_dict(request.to_dict())
        if not access_partitions or not all(
            isinstance(p, str) and p for p in access_partitions
        ):
            raise contracts.ContractValidationError(
                "authorized access partitions must not be empty"
            )
        partitions = tuple(sorted(set(access_partitions)))
        fingerprint = self._request_fingerprint(request, partitions)
        cursor = (
            self._decode_cursor(request.cursor) if request.cursor is not None else None
        )
        if cursor and cursor["fingerprint"] != fingerprint:
            raise contracts.ContractValidationError(
                "cursor request fingerprint does not match"
            )
        if cursor:
            head = cursor["search_head_id"]
            with self._snapshot_lock:
                self._expire(self.monotonic())
                snapshot = self._snapshots.get((head, fingerprint))
            if snapshot is None:
                raise contracts.PostSearchCursorStaleError(
                    "cursor_stale: search head is no longer retained"
                )
            _, components, hits, _ = snapshot
            if cursor["component_heads"] != components:
                raise contracts.ContractValidationError(
                    "cursor component heads do not match"
                )
        else:
            conn = self._connect()
            try:
                conn.execute("BEGIN")
                rows = self._rows(conn, request, partitions)
            finally:
                conn.close()
            components = {
                family: _stable_id(
                    f"{family}-head", [r for r in rows if r["storage_family"] == family]
                )
                for family in ("legacy", "temporal")
            }
            head = _stable_id("search-head", components)
            hits = self._rank(rows, request)
            if len(hits) > request.page_size:
                size = len(_canonical_json([hit.to_dict() for hit in hits]).encode())
                if size > MAX_RETAINED_BYTES:
                    raise contracts.ContractValidationError(
                        "search_snapshot_too_large: narrow filters"
                    )
                with self._snapshot_lock:
                    now = self.monotonic()
                    self._expire(now)
                    key = (head, fingerprint)
                    if key not in self._snapshots:
                        while self._snapshots and (
                            len(self._snapshots) >= self.snapshot_capacity
                            or sum(snapshot[3] for snapshot in self._snapshots.values())
                            + size
                            > MAX_RETAINED_BYTES
                        ):
                            self._snapshots.popitem(last=False)
                        self._snapshots[key] = (now, components, hits, size)
        offset = 0
        if cursor:
            positions = [list(self._sort_key(hit, request.sort)) for hit in hits]
            try:
                offset = positions.index(cursor["last"]) + 1
            except ValueError as exc:
                raise contracts.ContractValidationError(
                    "cursor position is invalid"
                ) from exc
        selected = hits[offset : offset + request.page_size]
        truncated = offset + len(selected) < len(hits)
        next_cursor = (
            self._encode_cursor(
                fingerprint,
                head,
                components,
                self._sort_key(selected[-1], request.sort),
            )
            if truncated
            else None
        )
        return contracts.PostSearchResponse.from_dict(
            {
                "schema_version": contracts.SCHEMA_VERSION,
                "request_id": request.request_id,
                "search_head_id": head,
                "generated_at": self.clock()
                .astimezone(timezone.utc)
                .isoformat()
                .replace("+00:00", "Z"),
                "query": request.query,
                "filters": request.filters,
                "sort": request.sort,
                "revision_mode": request.revision_mode,
                "hits": [hit.to_dict() for hit in selected],
                "returned": len(selected),
                "truncated": truncated,
                "next_cursor": next_cursor,
                "coverage": {
                    "component_heads": dict(components),
                    "storage_families": ["legacy", "temporal"],
                    "unavailable_filters": [],
                    "temporal_topics": "explicit_version_metadata_only",
                    "cursor_retention": {
                        "scope": "backend_process",
                        "capacity": self.snapshot_capacity,
                        "ttl_seconds": self.snapshot_ttl_seconds,
                        "max_bytes": MAX_RETAINED_BYTES,
                    },
                },
            }
        )
