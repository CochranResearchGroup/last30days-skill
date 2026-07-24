"""Cache-first application module behind local transport adapters."""

from __future__ import annotations

import json
import hashlib
import re
import sqlite3
from collections.abc import Callable, Mapping, Sequence
from datetime import datetime, timezone
from pathlib import Path
from typing import Protocol

import store

from . import service_contracts as contracts


SERVICE_VERSION = "0.1.0"
DEFAULT_FRESH_SECONDS = 24 * 60 * 60


class RetrievalBackend(Protocol):
    def search_snapshot(
        self,
        query: str,
        *,
        sources: Sequence[str] | None = None,
        top_k: int = 8,
        snippet_chars: int = 320,
    ) -> RetrievalSnapshot: ...


class RetrievalSnapshot(Protocol):
    index_version: str
    evidence: list[contracts.EvidenceItem]


class RefreshScheduler(Protocol):
    def ensure_refresh(self, request: contracts.QueryRequest) -> str | None: ...

    def cache_status(
        self,
        request: contracts.QueryRequest,
        fallback: contracts.CacheStatus,
    ) -> contracts.CacheStatus: ...


class JobReader(Protocol):
    def get_job(self, job_id: str) -> contracts.JobRecord: ...


class CacheQueryApplication:
    """Deep application interface for health, discovery, and bounded queries."""

    def __init__(
        self,
        db_path: Path,
        retriever: RetrievalBackend,
        *,
        refresh_scheduler: RefreshScheduler | None = None,
        job_reader: JobReader | None = None,
        acquisition_sources: Sequence[str] = (),
        acquisition_readiness: Mapping[str, bool] | None = None,
        runtime_error: Callable[[], str | None] | None = None,
        clock: Callable[[], datetime] | None = None,
        fresh_seconds: int = DEFAULT_FRESH_SECONDS,
    ):
        self.db_path = Path(db_path)
        self.retriever = retriever
        self.refresh_scheduler = refresh_scheduler
        self.job_reader = job_reader
        self.acquisition_sources = tuple(sorted(set(acquisition_sources)))
        self.acquisition_readiness = dict(acquisition_readiness or {})
        self.runtime_error = runtime_error or (lambda: None)
        self.clock = clock or (lambda: datetime.now(timezone.utc))
        self.fresh_seconds = fresh_seconds

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=5)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("PRAGMA busy_timeout=5000")
        return conn

    def _database_schema_version(self) -> int:
        conn = self._connect()
        try:
            row = conn.execute(
                "SELECT MAX(version) AS version FROM schema_version"
            ).fetchone()
            return int(row["version"] or 0)
        finally:
            conn.close()

    def _index_info(self) -> dict[str, object]:
        conn = self._connect()
        try:
            latest = conn.execute(
                """SELECT iv.index_version, iv.document_count, iv.embedding_model,
                          (
                              SELECT COUNT(*)
                              FROM index_chunk_embeddings AS ice
                              WHERE ice.index_version = iv.index_version
                          ) AS embedding_count,
                          (
                              SELECT COUNT(*)
                              FROM index_relationships AS ir
                              WHERE ir.index_version = iv.index_version
                          ) AS relationship_count
                   FROM index_versions AS iv
                   WHERE iv.published_at IS NOT NULL
                   ORDER BY iv.published_at DESC, iv.rowid DESC
                   LIMIT 1"""
            ).fetchone()
            document_count = conn.execute(
                "SELECT COUNT(*) FROM documents"
            ).fetchone()[0]
        finally:
            conn.close()
        if latest is not None:
            return {
                "version": latest["index_version"],
                "document_count": latest["document_count"],
                "embedding_model": latest["embedding_model"],
                "embedding_count": latest["embedding_count"],
                "relationship_count": latest["relationship_count"],
            }
        return {
            "version": "index-empty" if not document_count else "legacy-v3",
            "document_count": document_count,
            "embedding_model": None,
            "embedding_count": 0,
            "relationship_count": 0,
        }

    def _source_info(self) -> dict[str, object]:
        conn = self._connect()
        try:
            rows = conn.execute(
                """SELECT source, COUNT(*) AS document_count
                   FROM documents
                   GROUP BY source
                   ORDER BY source"""
            ).fetchall()
        finally:
            conn.close()
        sources = {
            row["source"]: {
                "ready": True,
                "indexed_documents": row["document_count"],
                "configured": row["source"] in self.acquisition_sources,
                "acquisition_ready": self.acquisition_readiness.get(
                    row["source"], False
                ),
                "acquisition_status": (
                    "cache_only"
                    if row["source"] not in self.acquisition_sources
                    else "ready"
                    if self.acquisition_readiness.get(row["source"], False)
                    else "configured"
                ),
            }
            for row in rows
        }
        for source in self.acquisition_sources:
            sources.setdefault(
                source,
                {
                    "ready": True,
                    "indexed_documents": 0,
                    "configured": True,
                    "acquisition_ready": self.acquisition_readiness.get(
                        source, False
                    ),
                    "acquisition_status": (
                        "ready"
                        if self.acquisition_readiness.get(source, False)
                        else "configured"
                    ),
                },
            )
        return sources

    def health(self) -> dict[str, object]:
        schema_version = self._database_schema_version()
        return {
            "status": "degraded" if self.runtime_error() else "ready",
            "service_version": SERVICE_VERSION,
            "schema_version": contracts.SCHEMA_VERSION,
            "database_schema_version": schema_version,
        }

    def service_info(self) -> contracts.ServiceInfo:
        index = self._index_info()
        capabilities = ["cache_query", "lexical_search"]
        if self.refresh_scheduler is not None and self.acquisition_sources:
            capabilities.append("durable_refresh")
        semantic_provider = getattr(self.retriever, "embedding_provider", None)
        if (
            semantic_provider is not None
            and index["embedding_model"] is not None
            and index["embedding_count"]
        ):
            capabilities.append("semantic_search")
        if index["relationship_count"]:
            capabilities.append("graph_search")
        return contracts.ServiceInfo.from_dict(
            {
                "schema_version": contracts.SCHEMA_VERSION,
                "service_version": SERVICE_VERSION,
                "database_schema_version": self._database_schema_version(),
                "status": "degraded" if self.runtime_error() else "ready",
                "capabilities": capabilities,
                "sources": self._source_info(),
                "freshness_policies": [
                    item.value for item in contracts.FreshnessPolicy
                ],
                "response_modes": [item.value for item in contracts.ResponseMode],
                "limits": {
                    "default_top_k": 8,
                    "max_top_k": 100,
                    "max_chars": 65536,
                },
                "index": index,
                "transport": "unix",
            }
        )

    def job(self, job_id: str) -> contracts.JobRecord:
        if (
            self.job_reader is None
            or not isinstance(job_id, str)
            or re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,127}", job_id) is None
        ):
            raise KeyError("job not found")
        return self.job_reader.get_job(job_id)

    @staticmethod
    def _topic_row(row: sqlite3.Row) -> dict[str, object]:
        try:
            search_queries = json.loads(row["search_queries"] or "[]")
        except json.JSONDecodeError:
            search_queries = []
        return {
            "topic_id": str(row["id"]),
            "name": row["name"],
            "search_queries": search_queries,
            "schedule": row["schedule"],
            "enabled": bool(row["enabled"]),
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }

    def topic(self, payload: Mapping[str, object]) -> dict[str, object]:
        """Apply one bounded operator topic action through the service authority."""
        action = payload.get("action")
        if action not in {
            "list",
            "create",
            "update",
            "pause",
            "resume",
            "request_refresh",
        }:
            raise contracts.ContractValidationError("invalid topic action")
        conn = self._connect()
        try:
            if action == "list":
                rows = conn.execute("SELECT * FROM topics ORDER BY name").fetchall()
                return {
                    "schema_version": contracts.SCHEMA_VERSION,
                    "action": action,
                    "topics": [self._topic_row(row) for row in rows],
                    "job_id": None,
                }

            topic_id = payload.get("topic_id")
            name = payload.get("name")
            if action == "create":
                if not isinstance(name, str) or not name.strip() or len(name) > 256:
                    raise contracts.ContractValidationError(
                        "topic create requires a bounded name"
                    )
                queries = payload.get("search_queries", [])
                if (
                    not isinstance(queries, list)
                    or len(queries) > 32
                    or any(
                        not isinstance(item, str)
                        or not item.strip()
                        or len(item) > 4096
                        for item in queries
                    )
                ):
                    raise contracts.ContractValidationError(
                        "search_queries must contain bounded strings"
                    )
                schedule = payload.get("schedule", "0 8 * * *")
                if (
                    not isinstance(schedule, str)
                    or not schedule.strip()
                    or len(schedule) > 128
                ):
                    raise contracts.ContractValidationError("invalid topic schedule")
                conn.execute(
                    """INSERT INTO topics (name, search_queries, schedule, enabled)
                       VALUES (?, ?, ?, 1)""",
                    (
                        name.strip(),
                        json.dumps(queries, separators=(",", ":"), ensure_ascii=False),
                        schedule.strip(),
                    ),
                )
                conn.commit()
                topic_id = str(conn.execute("SELECT last_insert_rowid()").fetchone()[0])

            if not isinstance(topic_id, str) or not topic_id.isdecimal():
                raise contracts.ContractValidationError(
                    "topic action requires a numeric topic_id"
                )
            row = conn.execute(
                "SELECT * FROM topics WHERE id = ?", (int(topic_id),)
            ).fetchone()
            if row is None:
                raise KeyError("topic not found")

            if action == "update":
                updates: list[str] = []
                values: list[object] = []
                if "name" in payload:
                    if (
                        not isinstance(name, str)
                        or not name.strip()
                        or len(name) > 256
                    ):
                        raise contracts.ContractValidationError("invalid topic name")
                    updates.append("name = ?")
                    values.append(name.strip())
                if "search_queries" in payload:
                    queries = payload["search_queries"]
                    if (
                        not isinstance(queries, list)
                        or len(queries) > 32
                        or any(
                            not isinstance(item, str)
                            or not item.strip()
                            or len(item) > 4096
                            for item in queries
                        )
                    ):
                        raise contracts.ContractValidationError(
                            "invalid topic search_queries"
                        )
                    updates.append("search_queries = ?")
                    values.append(
                        json.dumps(queries, separators=(",", ":"), ensure_ascii=False)
                    )
                if "schedule" in payload:
                    schedule = payload["schedule"]
                    if (
                        not isinstance(schedule, str)
                        or not schedule.strip()
                        or len(schedule) > 128
                    ):
                        raise contracts.ContractValidationError(
                            "invalid topic schedule"
                        )
                    updates.append("schedule = ?")
                    values.append(schedule.strip())
                if not updates:
                    raise contracts.ContractValidationError(
                        "topic update requires a mutable field"
                    )
                updates.append("updated_at = datetime('now')")
                conn.execute(
                    f"UPDATE topics SET {', '.join(updates)} WHERE id = ?",
                    (*values, int(topic_id)),
                )
                conn.commit()
            elif action in {"pause", "resume"}:
                conn.execute(
                    """UPDATE topics
                       SET enabled = ?, updated_at = datetime('now')
                       WHERE id = ?""",
                    (1 if action == "resume" else 0, int(topic_id)),
                )
                conn.commit()

            row = conn.execute(
                "SELECT * FROM topics WHERE id = ?", (int(topic_id),)
            ).fetchone()
            assert row is not None
            job_id = None
            if action == "request_refresh":
                if self.refresh_scheduler is None:
                    raise RuntimeError("durable refresh is unavailable")
                topic = self._topic_row(row)
                queries = topic["search_queries"]
                query = (
                    queries[0]
                    if isinstance(queries, list) and queries
                    else str(topic["name"])
                )
                sources = payload.get("sources", [])
                if not isinstance(sources, list):
                    raise contracts.ContractValidationError(
                        "sources must be an array"
                    )
                request_seed = json.dumps(
                    {
                        "topic_id": topic_id,
                        "query": query,
                        "sources": sources,
                        "at": self.clock().isoformat(),
                    },
                    sort_keys=True,
                    separators=(",", ":"),
                )
                request = contracts.QueryRequest.from_dict(
                    {
                        "schema_version": contracts.SCHEMA_VERSION,
                        "request_id": "topic-"
                        + hashlib.sha256(request_seed.encode()).hexdigest()[:24],
                        "profile_id": "default",
                        "query": query,
                        "freshness_policy": "force_refresh",
                        "response_mode": "evidence",
                        "filters": {
                            "topic_ids": [topic_id],
                            **({"sources": sources} if sources else {}),
                        },
                        "top_k": 8,
                        "max_chars": 8192,
                        "wait_ms": 0,
                    }
                )
                job_id = self.refresh_scheduler.ensure_refresh(request)
            return {
                "schema_version": contracts.SCHEMA_VERSION,
                "action": action,
                "topics": [self._topic_row(row)],
                "job_id": job_id,
            }
        finally:
            conn.close()

    @staticmethod
    def _parse_timestamp(value: str) -> datetime:
        normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
        parsed = datetime.fromisoformat(normalized)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)

    def _cache_status(
        self, evidence: Sequence[contracts.EvidenceItem]
    ) -> contracts.CacheStatus:
        if not evidence:
            return contracts.CacheStatus.MISS
        newest = max(self._parse_timestamp(item.fetched_at) for item in evidence)
        age = (self.clock().astimezone(timezone.utc) - newest).total_seconds()
        return (
            contracts.CacheStatus.FRESH
            if age <= self.fresh_seconds
            else contracts.CacheStatus.STALE
        )

    @staticmethod
    def _fit_response_budget(
        evidence: Sequence[contracts.EvidenceItem], max_chars: int
    ) -> tuple[list[contracts.EvidenceItem], bool]:
        selected: list[contracts.EvidenceItem] = []
        used = 512
        for item in evidence:
            encoded_size = len(
                json.dumps(
                    item.to_dict(),
                    ensure_ascii=False,
                    separators=(",", ":"),
                    sort_keys=True,
                )
            )
            if selected and used + encoded_size > max_chars:
                return selected, True
            if not selected and used + encoded_size > max_chars:
                available = max(1, max_chars - used - encoded_size + len(item.snippet))
                truncated_item = contracts.EvidenceItem.from_dict(
                    {**item.to_dict(), "snippet": item.snippet[:available]}
                )
                return [truncated_item], True
            selected.append(item)
            used += encoded_size
        return selected, False

    @staticmethod
    def _extractive_brief(
        evidence: Sequence[contracts.EvidenceItem], max_chars: int
    ) -> str | None:
        if not evidence:
            return None
        lines: list[str] = []
        used = 0
        for item in evidence:
            line = f"- [{item.evidence_id}] {item.title}: {item.snippet}"
            remaining = max_chars - used
            if remaining <= 0:
                break
            if len(line) > remaining:
                line = line[: max(1, remaining - 1)].rstrip() + "…"
            lines.append(line)
            used += len(line) + 1
        return "\n".join(lines) or None

    @staticmethod
    def _serialized_length(payload: dict[str, object]) -> int:
        return len(
            json.dumps(
                payload,
                ensure_ascii=False,
                separators=(",", ":"),
                sort_keys=True,
            )
        )

    def _enforce_exact_budget(
        self,
        payload: dict[str, object],
        evidence: list[contracts.EvidenceItem],
        max_chars: int,
        brief_limit: int,
    ) -> tuple[list[contracts.EvidenceItem], str | None, bool]:
        """Fit the complete public response, including metadata, to its contract."""
        selected = list(evidence)
        brief = payload["brief"]
        truncated = bool(payload["truncated"])

        def update_payload() -> None:
            payload["evidence"] = [item.to_dict() for item in selected]
            payload["brief"] = brief
            payload["truncated"] = truncated

        def trim_brief() -> None:
            nonlocal brief, truncated
            while isinstance(brief, str) and self._serialized_length(payload) > max_chars:
                overflow = self._serialized_length(payload) - max_chars
                keep = max(0, len(brief) - max(1, overflow))
                brief = brief[:keep].rstrip() or None
                truncated = True
                update_payload()

        update_payload()
        trim_brief()
        while selected and self._serialized_length(payload) > max_chars:
            selected.pop()
            brief = self._extractive_brief(selected, brief_limit)
            truncated = True
            update_payload()
            trim_brief()
        if self._serialized_length(payload) > max_chars:
            raise RuntimeError("response metadata exceeds the requested response budget")
        return selected, brief if isinstance(brief, str) else None, truncated

    def query(self, request: contracts.QueryRequest) -> contracts.QueryResponse:
        sources = request.filters.get("sources")
        snippet_chars = min(
            1024, max(128, request.max_chars // max(1, request.top_k))
        )
        snapshot = self.retriever.search_snapshot(
            request.query,
            sources=sources,
            top_k=request.top_k,
            snippet_chars=snippet_chars,
        )
        evidence = snapshot.evidence
        cache_status = self._cache_status(evidence)
        if self.refresh_scheduler is not None:
            cache_status = self.refresh_scheduler.cache_status(
                request,
                cache_status,
            )
        job_id = None
        if (
            self.refresh_scheduler is not None
            and request.freshness_policy
            in {
                contracts.FreshnessPolicy.PREFER_CACHE,
                contracts.FreshnessPolicy.REFRESH_IF_STALE,
                contracts.FreshnessPolicy.FORCE_REFRESH,
            }
            and (
                cache_status is not contracts.CacheStatus.FRESH
                or request.freshness_policy
                is contracts.FreshnessPolicy.FORCE_REFRESH
            )
        ):
            job_id = self.refresh_scheduler.ensure_refresh(request)
        bounded_evidence, truncated = self._fit_response_budget(
            evidence, request.max_chars
        )
        brief = None
        if request.response_mode is contracts.ResponseMode.BRIEF:
            brief = self._extractive_brief(
                bounded_evidence,
                min(2048, request.max_chars // 4),
            )
            if brief is not None:
                bounded_evidence, budget_truncated = self._fit_response_budget(
                    evidence,
                    max(512, request.max_chars - len(brief)),
                )
                truncated = truncated or budget_truncated
        payload: dict[str, object] = {
            "schema_version": contracts.SCHEMA_VERSION,
            "request_id": request.request_id,
            "index_version": snapshot.index_version,
            "cache_status": cache_status.value,
            "generated_at": self.clock()
            .astimezone(timezone.utc)
            .isoformat()
            .replace("+00:00", "Z"),
            "evidence": [item.to_dict() for item in bounded_evidence],
            "brief": brief,
            "job_id": job_id,
            "diagnostics_available": job_id is not None,
            "truncated": truncated,
            "next_cursor": None,
        }
        bounded_evidence, brief, truncated = self._enforce_exact_budget(
            payload,
            bounded_evidence,
            request.max_chars,
            min(2048, request.max_chars // 4),
        )
        payload["evidence"] = [item.to_dict() for item in bounded_evidence]
        payload["brief"] = brief
        payload["truncated"] = truncated
        return contracts.QueryResponse.from_dict(payload)


def initialize_application(
    db_path: Path,
    retriever: RetrievalBackend,
    *,
    refresh_scheduler: RefreshScheduler | None = None,
    job_reader: JobReader | None = None,
    acquisition_sources: Sequence[str] = (),
    acquisition_readiness: Mapping[str, bool] | None = None,
    runtime_error: Callable[[], str | None] | None = None,
) -> CacheQueryApplication:
    """Initialize schema once and return the transport-independent application."""
    store.init_db(db_path)
    return CacheQueryApplication(
        db_path,
        retriever,
        refresh_scheduler=refresh_scheduler,
        job_reader=job_reader,
        acquisition_sources=acquisition_sources,
        acquisition_readiness=acquisition_readiness,
        runtime_error=runtime_error,
    )
