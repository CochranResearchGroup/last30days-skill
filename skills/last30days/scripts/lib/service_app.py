"""Cache-first application module behind local transport adapters."""

from __future__ import annotations

import hashlib
import json
import os
import re
import sqlite3
from collections.abc import Callable, Mapping, Sequence
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Protocol

import store

from . import service_contracts as contracts
from .service_collection import CollectionCoordinator, CollectionSpec
from .service_intelligence_contracts import TaskContractRegistry
from .service_knowledge import TemporalKnowledgeQuery
from .service_supervisor import InvalidTransitionError


SERVICE_VERSION = os.environ.get("LAST30DAYS_SERVICE_VERSION", "0.2.27")
PRODUCT_IDENTITY = "last30days"
SERVICE_API_VERSION = 1
DEFAULT_FRESH_SECONDS = 24 * 60 * 60


def _runtime_manifest_sha256() -> str | None:
    configured = os.environ.get("LAST30DAYS_RUNTIME_MANIFEST_PATH")
    candidates = []
    if configured:
        candidates.append(Path(configured))
    resolved = Path(__file__).resolve()
    candidates.extend(
        (
            resolved.parents[2] / "runtime-manifest.json",
            resolved.parents[4] / "service" / "runtime-manifest.json",
        )
    )
    for path in candidates:
        try:
            if path.is_file() and not path.is_symlink():
                return hashlib.sha256(path.read_bytes()).hexdigest()
        except OSError:
            continue
    return None


class JobResumeConflictError(RuntimeError):
    """Raised when an operator resume does not apply to the current job state."""


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

    def resume_after_operator(self, job_id: str) -> contracts.JobRecord: ...


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
        recurring_collection: bool = False,
        assessment_processing: bool = False,
        collection_coordinator: CollectionCoordinator | None = None,
        graph_projection_enabled: bool = False,
        maintenance_enabled: bool = False,
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
        self.recurring_collection = recurring_collection
        self.assessment_processing = assessment_processing
        self.collection_coordinator = collection_coordinator
        self.graph_projection_enabled = graph_projection_enabled
        self.maintenance_enabled = maintenance_enabled
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
                   JOIN service_index_head AS ih
                     ON ih.index_version = iv.index_version
                    AND ih.singleton_id = 1
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
        if self.recurring_collection:
            capabilities.extend(
                ("recurring_collection", "interval_coverage", "assessment_queue")
            )
        if self.assessment_processing:
            capabilities.append("content_assessment")
        capabilities.extend(
            (
                "temporal_query",
                "profile_history",
                "event_timeline",
                "entity_dossier",
                "event_dossier",
                "trend_query",
                "coverage_query",
            )
        )
        if self.graph_projection_enabled:
            capabilities.append("graph_projection")
        if self.maintenance_enabled:
            capabilities.append("bounded_adapter_maintenance")
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
                "product": PRODUCT_IDENTITY,
                "service_version": SERVICE_VERSION,
                "service_api_version": SERVICE_API_VERSION,
                "contract_schema_version": contracts.SCHEMA_VERSION,
                "contract_sha256": contracts.SCHEMA_CATALOG_SHA256,
                "database_schema_version": self._database_schema_version(),
                "runtime_manifest_sha256": _runtime_manifest_sha256(),
                "mcp_adapter_version": None,
                "mcp_supported_service_api_min": None,
                "mcp_supported_service_api_max": None,
                "mcp_supported_database_schema_min": None,
                "mcp_supported_database_schema_max": None,
                "compatibility_state": "mcp_client_not_declared",
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

    @staticmethod
    def _access_partitions(profile_id: object) -> tuple[str, ...]:
        if not isinstance(profile_id, str) or not profile_id:
            raise contracts.ContractValidationError("profile_id is required")
        if re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,127}", profile_id) is None:
            raise contracts.ContractValidationError("profile_id is invalid")
        if profile_id == "default":
            return ("public",)
        return ("public", f"profile:{profile_id}")

    def _generated_at(self) -> str:
        return (
            self.clock()
            .astimezone(timezone.utc)
            .isoformat()
            .replace("+00:00", "Z")
        )

    @staticmethod
    def _bounded_text(
        payload: Mapping[str, object],
        name: str,
        *,
        required: bool = False,
        maximum: int = 4096,
    ) -> str | None:
        value = payload.get(name)
        if value is None and not required:
            return None
        if not isinstance(value, str) or not value.strip() or len(value) > maximum:
            raise contracts.ContractValidationError(f"{name} is invalid")
        return value.strip()

    def _projection_status(self, conn: sqlite3.Connection) -> dict[str, object]:
        rows = conn.execute(
            """SELECT state, COUNT(*) AS count
               FROM graph_projection_outbox GROUP BY state"""
        ).fetchall()
        counts = {str(row["state"]): int(row["count"]) for row in rows}
        latest = conn.execute(
            """SELECT projection_receipt, published_at
               FROM graph_projection_receipts
               ORDER BY published_at DESC, outbox_id DESC LIMIT 1"""
        ).fetchone()
        return {
            "enabled": self.graph_projection_enabled,
            "pending": counts.get("pending", 0),
            "failed": counts.get("failed", 0),
            "published": counts.get("published", 0),
            "latest_receipt": latest["projection_receipt"] if latest else None,
            "latest_published_at": latest["published_at"] if latest else None,
        }

    def _intelligence_status(self, conn: sqlite3.Connection) -> dict[str, object]:
        rows = conn.execute(
            """SELECT state, COUNT(*) AS count
               FROM service_intelligence_tasks GROUP BY state"""
        ).fetchall()
        counts = {str(row["state"]): int(row["count"]) for row in rows}
        return {
            "enabled": self.maintenance_enabled,
            "contract_catalog": TaskContractRegistry.default().catalog(),
            "task_states": counts,
            "validation_receipts": int(
                conn.execute(
                    "SELECT COUNT(*) FROM service_intelligence_validation_receipts"
                ).fetchone()[0]
            ),
            "promotion_receipts": int(
                conn.execute(
                    "SELECT COUNT(*) FROM service_intelligence_promotion_receipts"
                ).fetchone()[0]
            ),
            "replay_receipts": int(
                conn.execute(
                    "SELECT COUNT(*) FROM service_intelligence_replay_receipts"
                ).fetchone()[0]
            ),
            "repair_policy": {
                "failure_signature_required": True,
                "branch_isolation_required": True,
                "evaluation_required": True,
                "approval_required": True,
                "autonomous_deploy": False,
            },
        }

    def _profile_history(
        self,
        *,
        partitions: tuple[str, ...],
        source: str | None,
        handle: str | None,
        limit: int,
    ) -> list[dict[str, object]]:
        placeholders = ",".join("?" for _ in partitions)
        where = [f"a.access_partition_id IN ({placeholders})"]
        args: list[object] = list(partitions)
        if source is not None:
            where.append("a.source = ?")
            args.append(source)
        if handle is not None:
            where.append("(a.handle = ? OR a.native_account_id = ?)")
            args.extend((handle, handle))
        conn = self._connect()
        try:
            accounts = conn.execute(
                f"""SELECT * FROM source_accounts AS a
                    WHERE {' AND '.join(where)}
                    ORDER BY a.last_observed_at DESC, a.source_account_id
                    LIMIT ?""",
                (*args, limit),
            ).fetchall()
            output: list[dict[str, object]] = []
            for account in accounts:
                snapshots = conn.execute(
                    """SELECT * FROM profile_snapshots
                       WHERE source_account_id = ? AND access_partition_id = ?
                       ORDER BY observed_at DESC, snapshot_id""",
                    (
                        account["source_account_id"],
                        account["access_partition_id"],
                    ),
                ).fetchall()
                snapshot_items: list[dict[str, object]] = []
                for snapshot in snapshots:
                    sections = conn.execute(
                        """SELECT section_kind, ordinal, normalized_text,
                                  evidence_id, visibility, presence_state,
                                  redaction_class, retention_class
                           FROM profile_snapshot_sections
                           WHERE snapshot_id = ? AND access_partition_id = ?
                           ORDER BY section_kind, ordinal""",
                        (snapshot["snapshot_id"], snapshot["access_partition_id"]),
                    ).fetchall()
                    item = dict(snapshot)
                    item["metadata"] = json.loads(str(item.pop("metadata_json")))
                    item["sections"] = [dict(row) for row in sections]
                    snapshot_items.append(item)
                account_item = dict(account)
                account_item["declared_links"] = json.loads(
                    str(account_item.pop("declared_links_json"))
                )
                account_item["evidence_ids"] = json.loads(
                    str(account_item.pop("evidence_ids_json"))
                )
                account_item["snapshots"] = snapshot_items
                output.append(account_item)
            return output
        finally:
            conn.close()

    def _coverage(
        self, *, partitions: tuple[str, ...]
    ) -> dict[str, list[dict[str, object]]]:
        placeholders = ",".join("?" for _ in partitions)
        conn = self._connect()
        try:
            collections = conn.execute(
                f"""SELECT collection_spec_id, name, source, surface_kind,
                           profile_id, schedule, item_limit, enabled,
                           spec_version, access_partition_id, updated_at
                    FROM collection_specs
                    WHERE access_partition_id IN ({placeholders})
                    ORDER BY name, collection_spec_id""",
                partitions,
            ).fetchall()
            coverage = conn.execute(
                f"""SELECT * FROM collection_coverage_intervals
                    WHERE access_partition_id IN ({placeholders})
                    ORDER BY recorded_at DESC, coverage_id LIMIT 200""",
                partitions,
            ).fetchall()
            gaps = conn.execute(
                f"""SELECT * FROM collection_gaps
                    WHERE access_partition_id IN ({placeholders})
                    ORDER BY detected_at DESC, gap_id LIMIT 200""",
                partitions,
            ).fetchall()
            return {
                "collections": [dict(row) for row in collections],
                "coverage": [dict(row) for row in coverage],
                "gaps": [dict(row) for row in gaps],
            }
        finally:
            conn.close()

    def intelligence(self, payload: Mapping[str, object]) -> dict[str, object]:
        """Serve compact cache-only temporal product operations."""
        action = payload.get("action")
        allowed: dict[str, frozenset[str]] = {
            "temporal_query": frozenset(
                {
                    "action",
                    "query",
                    "profile_id",
                    "response_mode",
                    "as_of",
                    "during_from",
                    "during_to",
                    "known_as_of",
                }
            ),
            "profile_history": frozenset(
                {"action", "profile_id", "source", "handle", "limit"}
            ),
            "coverage": frozenset({"action", "profile_id"}),
            "maintenance_status": frozenset({"action", "profile_id"}),
            "collection": frozenset(
                {
                    "action",
                    "profile_id",
                    "operation",
                    "spec",
                    "collection_spec_id",
                    "scheduled_for",
                }
            ),
        }
        if not isinstance(action, str) or action not in allowed:
            raise contracts.ContractValidationError("intelligence action is invalid")
        if set(payload) - allowed[action]:
            raise contracts.ContractValidationError(
                "intelligence request contains unknown fields"
            )
        partitions = self._access_partitions(payload.get("profile_id", "default"))
        base: dict[str, object] = {
            "schema_version": contracts.SCHEMA_VERSION,
            "action": action,
            "access_partitions": list(partitions),
        }
        if action == "temporal_query":
            query = self._bounded_text(payload, "query", required=True)
            assert query is not None
            response_mode = payload.get("response_mode", "evidence")
            if response_mode not in {
                "evidence",
                "brief",
                "timeline",
                "entity_dossier",
                "event_dossier",
                "trend",
                "comparison",
            }:
                raise contracts.ContractValidationError("response_mode is invalid")
            as_of = self._bounded_text(payload, "as_of", maximum=64)
            known_as_of = self._bounded_text(
                payload, "known_as_of", maximum=64
            )
            during_from = self._bounded_text(
                payload, "during_from", maximum=64
            )
            during_to = self._bounded_text(payload, "during_to", maximum=64)
            if (during_from is None) != (during_to is None):
                raise contracts.ContractValidationError(
                    "during_from and during_to must be supplied together"
                )
            result = TemporalKnowledgeQuery(
                self.db_path, retriever=self.retriever
            ).query(
                query,
                access_partitions=partitions,
                as_of=as_of,
                during=(during_from, during_to)
                if during_from and during_to
                else None,
                known_as_of=known_as_of,
            )
            conn = self._connect()
            try:
                projection = self._projection_status(conn)
            finally:
                conn.close()
            return {
                **base,
                **result,
                "response_mode": response_mode,
                "cache_only": True,
                "freshness": {"generated_at": self._generated_at()},
                "projection": {
                    "graph_enabled": projection["enabled"],
                    "pending": projection["pending"],
                    "failed": projection["failed"],
                    "latest_receipt": projection["latest_receipt"],
                },
            }
        if action == "profile_history":
            source = self._bounded_text(payload, "source", maximum=64)
            handle = self._bounded_text(payload, "handle", maximum=256)
            limit = payload.get("limit", 20)
            if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 100:
                raise contracts.ContractValidationError("limit is invalid")
            return {
                **base,
                "cache_only": True,
                "profiles": self._profile_history(
                    partitions=partitions,
                    source=source,
                    handle=handle,
                    limit=limit,
                ),
            }
        if action == "coverage":
            return {**base, **self._coverage(partitions=partitions)}
        if action == "maintenance_status":
            conn = self._connect()
            try:
                return {
                    **base,
                    "app_intelligence": self._intelligence_status(conn),
                    "graph_projection": self._projection_status(conn),
                }
            finally:
                conn.close()

        if self.collection_coordinator is None:
            raise RuntimeError("collection authority is unavailable")
        operation = payload.get("operation")
        if operation == "list":
            visible = [
                item
                for item in self.collection_coordinator.list_specs()
                if isinstance(item.get("spec"), Mapping)
                and item["spec"].get("access_partition_id") in partitions
            ]
            return {
                **base,
                "operation": operation,
                "collections": visible,
            }
        if operation == "put":
            spec_payload = payload.get("spec")
            if not isinstance(spec_payload, Mapping):
                raise contracts.ContractValidationError("spec is required")
            spec = CollectionSpec.from_dict(spec_payload)
            if spec.access_partition_id not in partitions:
                raise contracts.ContractValidationError(
                    "collection spec is outside the authorized partition"
                )
            return {
                **base,
                "operation": operation,
                "collection": self.collection_coordinator.put_spec(spec).to_dict(),
            }
        collection_spec_id = self._bounded_text(
            payload, "collection_spec_id", required=True, maximum=128
        )
        assert collection_spec_id is not None
        existing_spec = self.collection_coordinator.get_spec(collection_spec_id)
        if existing_spec.access_partition_id not in partitions:
            raise contracts.ContractValidationError(
                "collection spec is outside the authorized partition"
            )
        if operation in {"pause", "resume"}:
            spec = self.collection_coordinator.set_enabled(
                collection_spec_id, enabled=operation == "resume"
            )
            return {
                **base,
                "operation": operation,
                "collection": spec.to_dict(),
            }
        if operation == "run":
            scheduled_for = self._bounded_text(
                payload, "scheduled_for", maximum=64
            ) or self._generated_at()
            run = self.collection_coordinator.enqueue_interval(
                collection_spec_id,
                scheduled_for=scheduled_for,
                trigger="manual",
            )
            return {**base, "operation": operation, "run": run.to_dict()}
        raise contracts.ContractValidationError("collection operation is invalid")

    def job(self, job_id: str) -> contracts.JobRecord:
        if (
            self.job_reader is None
            or not isinstance(job_id, str)
            or re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,127}", job_id) is None
        ):
            raise KeyError("job not found")
        return self.job_reader.get_job(job_id)

    def resume_job(self, job_id: str) -> contracts.JobRecord:
        if (
            self.job_reader is None
            or not isinstance(job_id, str)
            or re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,127}", job_id) is None
        ):
            raise KeyError("job not found")
        try:
            return self.job_reader.resume_after_operator(job_id)
        except InvalidTransitionError as exc:
            raise JobResumeConflictError(str(exc)) from exc

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
    recurring_collection: bool = False,
    assessment_processing: bool = False,
    collection_coordinator: CollectionCoordinator | None = None,
    graph_projection_enabled: bool = False,
    maintenance_enabled: bool = False,
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
        recurring_collection=recurring_collection,
        assessment_processing=assessment_processing,
        collection_coordinator=collection_coordinator,
        graph_projection_enabled=graph_projection_enabled,
        maintenance_enabled=maintenance_enabled,
        runtime_error=runtime_error,
    )
