"""Durable saved queries and cache-only search composition for monitor views."""

from __future__ import annotations

import hashlib
import json
import time
from datetime import datetime
from typing import Protocol, Sequence

from . import service_monitor_contracts as contracts
from . import service_contracts as search_contracts
from .service_monitors import MonitorRepository, MonitorKernelError


def _json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _digest(value: object) -> str:
    return hashlib.sha256(_json(value).encode()).hexdigest()


class SavedQueryRepository(MonitorRepository):
    """Monitor-local query schema; never migrates the read-only search corpus."""

    def initialize(self) -> None:
        super().initialize()
        conn = self._connect()
        try:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS service_monitor_saved_queries (
                    query_id TEXT NOT NULL, version INTEGER NOT NULL CHECK(version > 0),
                    partition_id TEXT NOT NULL, payload_json TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL, PRIMARY KEY(query_id, version)
                );
                CREATE TRIGGER IF NOT EXISTS monitor_saved_queries_no_update
                BEFORE UPDATE ON service_monitor_saved_queries BEGIN
                    SELECT RAISE(ABORT, 'saved query is immutable'); END;
                CREATE TRIGGER IF NOT EXISTS monitor_saved_queries_no_delete
                BEFORE DELETE ON service_monitor_saved_queries BEGIN
                    SELECT RAISE(ABORT, 'saved query is immutable'); END;
                CREATE TABLE IF NOT EXISTS service_monitor_query_captures (
                    snapshot_id TEXT PRIMARY KEY, binding TEXT NOT NULL,
                    state TEXT NOT NULL CHECK(state IN ('pending', 'ready', 'failed')),
                    receipt_json TEXT, receipt_sha256 TEXT, error_code TEXT
                );
                CREATE TRIGGER IF NOT EXISTS monitor_captures_terminal
                BEFORE UPDATE ON service_monitor_query_captures
                WHEN OLD.state != 'pending' OR NEW.snapshot_id != OLD.snapshot_id
                    OR NEW.binding != OLD.binding BEGIN
                    SELECT RAISE(ABORT, 'capture is immutable'); END;
                CREATE TRIGGER IF NOT EXISTS monitor_captures_no_delete
                BEFORE DELETE ON service_monitor_query_captures BEGIN
                    SELECT RAISE(ABORT, 'capture is immutable'); END;
            """)
        finally:
            conn.close()

    def save(self, definition: contracts.SavedQueryDefinitionV1) -> None:
        definition = contracts.SavedQueryDefinitionV1.from_dict(definition.to_dict())
        payload = definition.to_dict()
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            existing = conn.execute(
                "SELECT payload_sha256 FROM service_monitor_saved_queries "
                "WHERE query_id=? AND version=?",
                (definition.saved_query_id, definition.version),
            ).fetchone()
            if existing:
                if existing[0] != _digest(payload):
                    raise MonitorKernelError(contracts.MonitorErrorCode.IMMUTABLE_CONFLICT,
                                             "saved query version already exists")
                return
            prior = conn.execute(
                "SELECT version, partition_id, payload_json FROM service_monitor_saved_queries "
                "WHERE query_id=? ORDER BY version DESC LIMIT 1",
                (definition.saved_query_id,),
            ).fetchone()
            if definition.version != (1 if prior is None else prior["version"] + 1):
                raise MonitorKernelError(contracts.MonitorErrorCode.INVALID_REVISION,
                                         "saved query version must increase by one")
            if prior and (prior["partition_id"] != definition.access_partition_id or
                          json.loads(prior["payload_json"])["search"]["profile_id"] !=
                          payload["search"]["profile_id"]):
                raise MonitorKernelError(contracts.MonitorErrorCode.PARTITION_MISMATCH,
                                         "saved query access identity is immutable")
            conn.execute("INSERT INTO service_monitor_saved_queries VALUES (?, ?, ?, ?, ?)",
                         (definition.saved_query_id, definition.version,
                          definition.access_partition_id, _json(payload), _digest(payload)))
            conn.commit()
        finally:
            conn.close()

    def get(self, ref: contracts.SavedQueryViewRefV1,
            access_partition_id: str) -> contracts.SavedQueryDefinitionV1:
        ref = contracts.SavedQueryViewRefV1.from_dict(ref.to_dict())
        conn = self._connect()
        try:
            row = conn.execute("SELECT * FROM service_monitor_saved_queries "
                               "WHERE query_id=? AND version=?",
                               (ref.saved_query_id, ref.saved_query_version)).fetchone()
        finally:
            conn.close()
        if row is None or row["partition_id"] != access_partition_id:
            raise MonitorKernelError(contracts.MonitorErrorCode.PARTITION_MISMATCH,
                                     "saved query is unavailable in this partition")
        payload = json.loads(row["payload_json"])
        if _digest(payload) != row["payload_sha256"]:
            raise MonitorKernelError(contracts.MonitorErrorCode.IMMUTABLE_CONFLICT,
                                     "saved query digest mismatch")
        return contracts.SavedQueryDefinitionV1.from_dict(payload)

    def begin_capture(self, snapshot_id: str, binding: str) -> bool:
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute("SELECT binding, state, error_code FROM "
                               "service_monitor_query_captures WHERE snapshot_id=?",
                               (snapshot_id,)).fetchone()
            if row:
                if row["binding"] != binding:
                    raise MonitorKernelError(contracts.MonitorErrorCode.IMMUTABLE_CONFLICT,
                                             "capture inputs changed")
                if row["state"] != "ready":
                    raise MonitorKernelError(contracts.MonitorErrorCode.VIEW_UNAVAILABLE,
                                             "capture did not complete; no automatic replay")
                return False
            conn.execute("INSERT INTO service_monitor_query_captures "
                         "(snapshot_id, binding, state) VALUES (?, ?, 'pending')",
                         (snapshot_id, binding))
            conn.commit()
            return True
        finally:
            conn.close()

    def finish_capture(self, snapshot_id: str, *, receipt: dict | None = None,
                       error_code: str | None = None) -> None:
        conn = self._connect()
        try:
            conn.execute("UPDATE service_monitor_query_captures SET state=?, "
                         "receipt_json=?, receipt_sha256=?, error_code=? WHERE snapshot_id=?",
                         ("ready" if receipt is not None else "failed",
                          None if receipt is None else _json(receipt),
                          None if receipt is None else _digest(receipt), error_code, snapshot_id))
            conn.commit()
        finally:
            conn.close()

    def capture_receipt(self, snapshot_id: str) -> dict:
        conn = self._connect()
        try:
            row = conn.execute("SELECT * FROM service_monitor_query_captures "
                               "WHERE snapshot_id=?", (snapshot_id,)).fetchone()
        finally:
            conn.close()
        if row is None or row["state"] != "ready":
            raise MonitorKernelError(contracts.MonitorErrorCode.VIEW_UNAVAILABLE,
                                     "saved query capture is unavailable")
        result = json.loads(row["receipt_json"])
        if _digest(result) != row["receipt_sha256"]:
            raise MonitorKernelError(contracts.MonitorErrorCode.IMMUTABLE_CONFLICT,
                                     "capture receipt digest mismatch")
        return result


class SearchBackend(Protocol):
    def search(self, request: search_contracts.PostSearchRequest, *,
               access_partitions: Sequence[str]) -> search_contracts.PostSearchResponse: ...


class SavedQueryViewProvider:
    """Capture once, then replay durable evidence without retaining search cursors.

    Coverage is completeness of this bounded cache view, not provider acquisition
    coverage. Complete traversal never supplies evidence of removal. Partial
    traversal is retained for inspection but cannot advance a monitor baseline.
    A caller must use a new capture ID for an explicitly requested fresh view.
    max_bytes bounds serialized evidence; source pages are additionally bounded
    to 128 KiB. The time limit is cooperative between synchronous backend calls,
    not a mechanism for interrupting SQLite or a backend in flight.
    """

    def __init__(self, repository: SavedQueryRepository, search_backend: SearchBackend,
                 *, max_items: int = 1000, max_pages: int = 100,
                 max_bytes: int = 2_097_152, max_seconds: float = 10,
                 monotonic=time.monotonic) -> None:
        if any(type(v) is not int or v < 1 for v in (max_items, max_pages, max_bytes)):
            raise contracts.MonitorContractError("capture limits must be positive integers")
        if type(max_seconds) not in (int, float) or not 0 < max_seconds <= 60:
            raise contracts.MonitorContractError("capture time limit must be within 60 seconds")
        if max_items > 10_000 or max_pages > 1000 or max_bytes > 32 * 1024 * 1024:
            raise contracts.MonitorContractError("capture limits exceed the hard ceiling")
        self.repository, self.search_backend = repository, search_backend
        self.max_items, self.max_pages, self.max_bytes = max_items, max_pages, max_bytes
        self.max_seconds, self.monotonic = max_seconds, monotonic

    @staticmethod
    def _snapshot_id(ref, partition, capture_id):
        if not isinstance(capture_id, str) or not 1 <= len(capture_id) <= 128:
            raise contracts.MonitorContractError("capture_id must contain 1 to 128 characters")
        return "query-view-" + _digest([ref.to_dict(), partition, capture_id])[:32]

    def capture(self, ref: contracts.SavedQueryViewRefV1, access_partition_id: str,
                capture_id: str) -> contracts.SavedQueryViewSnapshotV1:
        definition = self.repository.get(ref, access_partition_id)
        snapshot_id = self._snapshot_id(ref, access_partition_id, capture_id)
        limits = {"max_items": self.max_items, "max_pages": self.max_pages,
                  "max_bytes": self.max_bytes, "max_seconds": self.max_seconds}
        binding = _digest({"definition": definition.to_dict(), "limits": limits})
        if not self.repository.begin_capture(snapshot_id, binding):
            return self.read(ref, access_partition_id, snapshot_id)
        try:
            snapshot, receipt = self._capture(definition, snapshot_id, limits)
            self.repository.put_snapshot(snapshot)
            self.repository.finish_capture(snapshot_id, receipt=receipt)
            return snapshot
        except Exception as exc:
            # Do not persist backend exception text: it may contain cursors or IDs.
            code = ("cursor_stale" if isinstance(exc, search_contracts.PostSearchCursorStaleError)
                    else "capture_failed")
            self.repository.finish_capture(snapshot_id, error_code=code)
            if isinstance(exc, MonitorKernelError):
                raise
            raise MonitorKernelError(contracts.MonitorErrorCode.VIEW_UNAVAILABLE,
                                     code) from exc

    def _capture(self, definition, snapshot_id, limits):
        started = self.monotonic()
        request_payload = {**definition.to_dict()["search"], "schema_version": 1,
                           "request_id": snapshot_id, "cursor": None}
        hits, cursors, gaps = [], set(), set()
        identities = set()
        evidence_bytes = 2  # JSON list brackets; each later item adds a comma.
        first = None
        coverage = None
        for page_number in range(1, self.max_pages + 1):
            if self.monotonic() - started >= self.max_seconds:
                raise MonitorKernelError(contracts.MonitorErrorCode.VIEW_UNAVAILABLE,
                                         "capture time limit exceeded")
            request = search_contracts.PostSearchRequest.from_dict(request_payload)
            response = self.search_backend.search(request, access_partitions=(definition.access_partition_id,))
            response = search_contracts.PostSearchResponse.from_dict(response.to_dict())
            if len(_json(response.to_dict()).encode()) > 131_072 or response.returned > request.page_size:
                raise MonitorKernelError(contracts.MonitorErrorCode.VIEW_UNAVAILABLE,
                                         "search page exceeds the bounded contract")
            if any(getattr(response, field) != getattr(request, field)
                   for field in ("request_id", "query", "filters", "sort", "revision_mode")):
                raise MonitorKernelError(contracts.MonitorErrorCode.VIEW_MISMATCH,
                                         "search response changed the saved query")
            components = response.coverage.get("component_heads")
            if (not isinstance(components, dict) or set(components) != {"legacy", "temporal"}
                    or not all(isinstance(v, str) and v for v in components.values())):
                raise MonitorKernelError(contracts.MonitorErrorCode.VIEW_UNAVAILABLE,
                                         "search component heads are unavailable")
            current_coverage = {k: v for k, v in response.coverage.items()
                                if k != "cursor_retention"}
            if first is None:
                first, coverage = response, current_coverage
            elif response.search_head_id != first.search_head_id or current_coverage != coverage:
                raise MonitorKernelError(contracts.MonitorErrorCode.VIEW_MISMATCH,
                                         "search head or coverage changed during traversal")
            if current_coverage.get("unavailable_filters"):
                gaps.add("unavailable_filters")
            semantic = current_coverage.get("semantic", {})
            if request.query is not None:
                families = semantic.get("families", {})
                if set(families) != {"legacy", "temporal"}:
                    raise MonitorKernelError(contracts.MonitorErrorCode.VIEW_UNAVAILABLE,
                                             "semantic coverage is unavailable")
                fields = {"eligible", "available", "missing", "incompatible", "invalid", "zero_vector"}
                if any(not isinstance(counts, dict) or set(counts) != fields
                       or any(type(value) is not int or value < 0 for value in counts.values())
                       or counts["eligible"] != sum(counts[field] for field in fields - {"eligible"})
                       for counts in families.values()):
                    raise MonitorKernelError(contracts.MonitorErrorCode.VIEW_UNAVAILABLE,
                                             "semantic coverage counts are invalid")
                if any(counts.get("available") != counts.get("eligible")
                       for counts in families.values()):
                    gaps.add("semantic_incomplete")
            for hit in response.hits:
                if hit.access_partition_id != definition.access_partition_id:
                    raise MonitorKernelError(contracts.MonitorErrorCode.PARTITION_MISMATCH,
                                             "search evidence is outside the monitor partition")
                if hit.post_id in identities:
                    raise MonitorKernelError(contracts.MonitorErrorCode.VIEW_MISMATCH,
                                             "search traversal repeated a post identity")
                size = len(_json(hit.to_dict()).encode()) + (1 if hits else 0)
                if len(hits) >= self.max_items or evidence_bytes + size > self.max_bytes:
                    gaps.add("capture_limit")
                    break
                hits.append(hit)
                identities.add(hit.post_id)
                evidence_bytes += size
            if "capture_limit" in gaps:
                break
            if response.truncated != (response.next_cursor is not None):
                gaps.add("incomplete_pagination")
                break
            if not response.truncated:
                break
            if not response.hits or response.next_cursor in cursors:
                raise MonitorKernelError(contracts.MonitorErrorCode.VIEW_MISMATCH,
                                         "search pagination made no progress")
            cursors.add(response.next_cursor)
            request_payload["cursor"] = response.next_cursor
        else:
            gaps.add("page_limit")
        if self.monotonic() - started >= self.max_seconds:
            gaps.add("time_limit")
        assert first is not None
        cutoff = first.generated_at
        observations = [hit.observed_at for hit in hits]
        timestamp = lambda value: datetime.fromisoformat(value.replace("Z", "+00:00"))
        if observations and max(map(timestamp, observations)) > timestamp(cutoff):
            raise MonitorKernelError(contracts.MonitorErrorCode.VIEW_MISMATCH,
                                     "evidence is newer than the frozen knowledge cutoff")
        snapshot = contracts.SavedQueryViewSnapshotV1.from_dict({
            "schema_version": 1, "snapshot_id": snapshot_id,
            "view_ref": definition.view_ref.to_dict(),
            "access_partition_id": definition.access_partition_id,
            "evidence_head_id": first.search_head_id, "knowledge_cutoff": cutoff,
            "coverage_start": min(observations, key=timestamp, default=cutoff), "coverage_end": cutoff,
            "coverage": {"status": "partial" if gaps else "complete",
                         "sources": sorted({hit.source for hit in hits}), "gaps": sorted(gaps)},
            "evidence": [{"evidence_id": hit.post_id, "version_id": hit.revision_id,
                          "tombstoned": False} for hit in hits],
        })
        receipt = {"schema_version": 1, "snapshot": snapshot.to_dict(),
                   "definition": definition.to_dict(), "component_heads": first.coverage["component_heads"],
                   "coverage": coverage, "coverage_scope": "bounded_cache_view_only",
                   "pages": page_number, "limits": limits,
                   "evidence_refs": [hit.to_dict() for hit in hits]}
        return snapshot, receipt

    def read(self, ref: contracts.SavedQueryViewRefV1, access_partition_id: str,
             snapshot_id: str) -> contracts.SavedQueryViewSnapshotV1:
        self.repository.get(ref, access_partition_id)
        receipt = self.repository.capture_receipt(snapshot_id)
        snapshot = contracts.SavedQueryViewSnapshotV1.from_dict(receipt["snapshot"])
        if snapshot.view_ref != ref or snapshot.access_partition_id != access_partition_id:
            raise MonitorKernelError(contracts.MonitorErrorCode.VIEW_MISMATCH,
                                     "saved view does not match this query and partition")
        return snapshot

    def receipt(self, ref, access_partition_id, capture_id) -> dict:
        snapshot_id = self._snapshot_id(ref, access_partition_id, capture_id)
        self.read(ref, access_partition_id, snapshot_id)
        return self.repository.capture_receipt(snapshot_id)


def saved_query_command(provider: SavedQueryViewProvider, payload: dict, *,
                        access_partition_id: str) -> dict:
    """Closed JSON command seam; authorization comes from the trusted caller.

    This does not register a CLI/MCP route, initialize stores, schedule work,
    activate a monitor, or accept a baseline. Shared transport joins own routing.
    """
    if not isinstance(payload, dict):
        raise contracts.MonitorContractError("saved query command must be an object")
    action = payload.get("action")
    fields = {"save": {"action", "definition"}, "get": {"action", "view_ref"},
              "capture": {"action", "view_ref", "capture_id"},
              "receipt": {"action", "view_ref", "capture_id"}}
    if not isinstance(action, str) or action not in fields or set(payload) != fields[action]:
        raise contracts.MonitorContractError("invalid saved query action or fields")
    if action == "save":
        definition = contracts.SavedQueryDefinitionV1.from_dict(payload["definition"])
        if definition.access_partition_id != access_partition_id:
            raise MonitorKernelError(contracts.MonitorErrorCode.PARTITION_MISMATCH,
                                     "query definition is outside the authorized partition")
        provider.repository.save(definition)
        return definition.to_dict()
    ref = contracts.SavedQueryViewRefV1.from_dict(payload["view_ref"])
    if action == "get":
        return provider.repository.get(ref, access_partition_id).to_dict()
    if action == "capture":
        return provider.capture(ref, access_partition_id, payload["capture_id"]).to_dict()
    return provider.receipt(ref, access_partition_id, payload["capture_id"])
