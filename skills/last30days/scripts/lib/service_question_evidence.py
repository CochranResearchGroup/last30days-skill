"""Immutable, partition-closed evidence reads for frozen question citations."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Mapping, Sequence

from . import service_question_contracts as contracts


_MAX_TEXT_CHARACTERS = 32_768


def _connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path), timeout=5)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA query_only=ON")
    conn.execute("PRAGMA busy_timeout=5000")
    return conn


def _json_object(value: str) -> dict[str, Any]:
    parsed = json.loads(value)
    if not isinstance(parsed, dict):
        raise ValueError("stored metadata must be an object")
    return parsed


def _json_list(value: str) -> list[Any]:
    parsed = json.loads(value)
    if not isinstance(parsed, list):
        raise ValueError("stored media must be a list")
    return parsed


def _response_size(payload: Mapping[str, Any]) -> int:
    measured = 2
    while True:
        candidate = {**payload, "response_bytes": measured}
        updated = len(contracts.canonical_json(candidate).encode())
        if updated == measured:
            return updated
        measured = updated


class QuestionEvidenceResolver:
    """Resolve exact version locators without consulting mutable current heads."""

    def __init__(self, db_path: Path) -> None:
        self.db_path = Path(db_path)

    def read(
        self,
        request: contracts.EvidenceReadRequestV1,
        *,
        access_partitions: Sequence[str],
    ) -> contracts.EvidenceReadResponseV1:
        partitions = tuple(dict.fromkeys(access_partitions))
        if not partitions or not all(
            isinstance(partition, str) and partition for partition in partitions
        ):
            raise contracts.QuestionContractError(
                "authorized access partitions must not be empty"
            )
        authorized = set(partitions)
        conn = _connect(self.db_path)
        try:
            resolved = tuple(
                self._resolve(conn, ref, authorized=authorized) for ref in request.refs
            )
        finally:
            conn.close()

        selected: list[contracts.EvidenceReadItemV1] = []
        for index, item in enumerate(resolved):
            candidate_items = [*selected, item]
            omitted = [ref.evidence_id for ref in request.refs[index + 1 :]]
            payload = {
                "schema_version": contracts.QUESTION_SCHEMA_VERSION,
                "request_id": request.request_id,
                "items": [candidate.to_dict() for candidate in candidate_items],
                "omitted_refs": omitted,
                "truncated": bool(omitted),
            }
            if _response_size(payload) > request.max_response_bytes:
                break
            selected.append(item)

        omitted_refs = tuple(
            ref.evidence_id for ref in request.refs[len(selected) :]
        )
        payload = {
            "schema_version": contracts.QUESTION_SCHEMA_VERSION,
            "request_id": request.request_id,
            "items": [item.to_dict() for item in selected],
            "omitted_refs": list(omitted_refs),
            "truncated": bool(omitted_refs),
        }
        response_bytes = _response_size(payload)
        if response_bytes > request.max_response_bytes:
            raise contracts.QuestionContractError(
                "max_response_bytes is too small for the response envelope"
            )
        return contracts.EvidenceReadResponseV1.from_dict(
            {**payload, "response_bytes": response_bytes}
        )

    def _resolve(
        self,
        conn: sqlite3.Connection,
        ref: contracts.QuestionCitationV1,
        *,
        authorized: set[str],
    ) -> contracts.EvidenceReadItemV1:
        unavailable = contracts.EvidenceReadItemV1(
            ref=ref, status="unavailable", evidence=None
        )
        citation_core = {
            key: value
            for key, value in ref.to_dict().items()
            if key != "evidence_id"
        }
        if (
            ref.access_partition_id not in authorized
            or ref.evidence_id
            != contracts.stable_id("question-evidence", citation_core)
        ):
            return unavailable
        try:
            if ref.storage_family == "legacy":
                evidence = self._legacy(conn, ref)
            elif ref.storage_family == "temporal":
                evidence = self._temporal(conn, ref)
            else:
                evidence = None
            if evidence is None:
                return unavailable
            return contracts.EvidenceReadItemV1.from_dict(
                {"ref": ref.to_dict(), "status": "available", "evidence": evidence}
            )
        except (json.JSONDecodeError, ValueError):
            return unavailable

    @staticmethod
    def _legacy(
        conn: sqlite3.Connection, ref: contracts.QuestionCitationV1
    ) -> dict[str, Any] | None:
        row = conn.execute(
            """SELECT d.document_id, d.source, d.source_native_id,
                      d.canonical_url, v.version_id, v.acquisition_id,
                      v.content_hash, v.title, v.author, v.normalized_text,
                      v.source_metadata_json, v.media_json, v.published_at,
                      v.valid_from, v.valid_to, v.observed_at, v.fetched_at,
                      v.system_from, v.system_to, v.retention_class,
                      v.redaction_class, v.access_partition_id,
                      v.transformation_version
                 FROM document_versions AS v
                 JOIN documents AS d
                   ON d.document_id = v.document_id
                  AND d.access_partition_id = v.access_partition_id
                WHERE v.version_id = ? AND v.access_partition_id = ?""",
            (ref.version_id, ref.access_partition_id),
        ).fetchone()
        if row is None or not QuestionEvidenceResolver._matches(row, ref):
            return None
        sightings = conn.execute(
            """SELECT acquisition_id, topic_id, collection_spec_id,
                      collection_run_id, observed_at
                 FROM document_version_sightings
                WHERE version_id = ? AND access_partition_id = ?
                ORDER BY acquisition_id""",
            (ref.version_id, ref.access_partition_id),
        ).fetchall()
        collection_refs = sorted(
            {
                str(item["collection_spec_id"])
                for item in sightings
                if item["collection_spec_id"]
            }
        )
        topic_ids = sorted(
            {
                str(item["topic_id"])
                for item in sightings
                if item["topic_id"] is not None
            }
        )
        text = str(row["normalized_text"])
        return {
            "storage_family": "legacy",
            "version_id": str(row["version_id"]),
            "source": str(row["source"]),
            "source_native_id": str(row["source_native_id"]),
            "canonical_url": str(row["canonical_url"]),
            "author": str(row["author"]) if row["author"] is not None else None,
            "title": str(row["title"]),
            "text": text[:_MAX_TEXT_CHARACTERS],
            "text_truncated": len(text) > _MAX_TEXT_CHARACTERS,
            "content_hash": str(row["content_hash"]),
            "access_partition_id": str(row["access_partition_id"]),
            "published_at": row["published_at"],
            "observed_at": str(row["observed_at"]),
            "fetched_at": str(row["fetched_at"]),
            "valid_from": row["valid_from"],
            "valid_to": row["valid_to"],
            "system_from": str(row["system_from"]),
            "system_to": row["system_to"],
            "created_at": None,
            "metadata": _json_object(str(row["source_metadata_json"])),
            "media": _json_list(str(row["media_json"])),
            "collection_refs": collection_refs,
            "topic_ids": topic_ids,
            "provenance": {
                "document_id": str(row["document_id"]),
                "acquisition_id": str(row["acquisition_id"]),
                "retention_class": str(row["retention_class"]),
                "redaction_class": str(row["redaction_class"]),
                "transformation_version": str(row["transformation_version"]),
                "sightings": [dict(item) for item in sightings],
            },
        }

    @staticmethod
    def _temporal(
        conn: sqlite3.Connection, ref: contracts.QuestionCitationV1
    ) -> dict[str, Any] | None:
        row = conn.execute(
            """SELECT r.record_id, r.service_id, r.source, r.source_native_id,
                      r.canonical_url, v.version_id, v.provider_attempt_id,
                      v.content_hash, v.title, v.normalized_text, v.author,
                      v.published_at, v.metadata_json, v.observed_at,
                      v.access_partition_id, v.retention_class, v.created_at
                 FROM service_source_versions AS v
                 JOIN service_source_records AS r
                   ON r.record_id = v.record_id
                  AND r.access_partition_id = v.access_partition_id
                WHERE v.version_id = ? AND v.access_partition_id = ?""",
            (ref.version_id, ref.access_partition_id),
        ).fetchone()
        if row is None or not QuestionEvidenceResolver._matches(row, ref):
            return None
        sightings = conn.execute(
            """SELECT s.tick_id, s.lane_id, s.provider_attempt_id,
                      s.observed_at, l.target_id, l.target_config_json
                 FROM service_source_sightings AS s
                 JOIN service_tick_lanes AS l ON l.lane_id = s.lane_id
                WHERE s.version_id = ? AND l.access_partition_id = ?
                ORDER BY s.tick_id, s.lane_id""",
            (ref.version_id, ref.access_partition_id),
        ).fetchall()
        metadata = _json_object(str(row["metadata_json"]))
        collection_refs: set[str] = set()
        topic_ids: set[str] = set()
        provenance_sightings: list[dict[str, Any]] = []
        for item in sightings:
            target = _json_object(str(item["target_config_json"]))
            QuestionEvidenceResolver._collect_causes(
                target, collection_refs=collection_refs, topic_ids=topic_ids
            )
            provenance_sightings.append(
                {
                    "tick_id": item["tick_id"],
                    "lane_id": item["lane_id"],
                    "provider_attempt_id": item["provider_attempt_id"],
                    "observed_at": item["observed_at"],
                    "target_id": item["target_id"],
                }
            )
        QuestionEvidenceResolver._collect_causes(
            metadata, collection_refs=collection_refs, topic_ids=topic_ids
        )
        text = str(row["normalized_text"])
        media = metadata.get("media", [])
        if not isinstance(media, list):
            media = []
        return {
            "storage_family": "temporal",
            "version_id": str(row["version_id"]),
            "source": str(row["source"]),
            "source_native_id": str(row["source_native_id"]),
            "canonical_url": str(row["canonical_url"]),
            "author": str(row["author"]) if row["author"] is not None else None,
            "title": str(row["title"]),
            "text": text[:_MAX_TEXT_CHARACTERS],
            "text_truncated": len(text) > _MAX_TEXT_CHARACTERS,
            "content_hash": str(row["content_hash"]),
            "access_partition_id": str(row["access_partition_id"]),
            "published_at": row["published_at"],
            "observed_at": str(row["observed_at"]),
            "fetched_at": None,
            "valid_from": None,
            "valid_to": None,
            "system_from": None,
            "system_to": None,
            "created_at": str(row["created_at"]),
            "metadata": metadata,
            "media": media,
            "collection_refs": sorted(collection_refs),
            "topic_ids": sorted(topic_ids),
            "provenance": {
                "record_id": str(row["record_id"]),
                "service_id": str(row["service_id"]),
                "provider_attempt_id": str(row["provider_attempt_id"]),
                "retention_class": str(row["retention_class"]),
                "sightings": provenance_sightings,
            },
        }

    @staticmethod
    def _matches(row: sqlite3.Row, ref: contracts.QuestionCitationV1) -> bool:
        return (
            str(row["version_id"]) == ref.version_id
            and str(row["content_hash"]) == ref.content_hash
            and str(row["canonical_url"]) == ref.source_url
            and str(row["access_partition_id"]) == ref.access_partition_id
        )

    @staticmethod
    def _collect_causes(
        value: Mapping[str, Any], *, collection_refs: set[str], topic_ids: set[str]
    ) -> None:
        for singular, plural, target in (
            ("collection_ref", "collection_refs", collection_refs),
            ("collection_spec_id", "collection_spec_ids", collection_refs),
            ("topic_id", "topic_ids", topic_ids),
        ):
            item = value.get(singular)
            if isinstance(item, (str, int)) and not isinstance(item, bool):
                target.add(str(item))
            items = value.get(plural)
            if isinstance(items, list):
                target.update(
                    str(entry)
                    for entry in items
                    if isinstance(entry, (str, int)) and not isinstance(entry, bool)
                )
