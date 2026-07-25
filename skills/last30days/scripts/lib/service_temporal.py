"""Deterministic identities and compatibility exports for the temporal corpus."""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from pathlib import Path
from typing import Any, Mapping


_ID_NAMESPACE = re.compile(r"^[a-z][a-z0-9_]{0,31}$")


def _canonical_json(value: object) -> str:
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def sha256_json(value: object) -> str:
    """Return a portable digest for one JSON-compatible value."""
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def stable_temporal_id(namespace: str, identity: Mapping[str, Any]) -> str:
    """Build a stable opaque identifier from canonical identity fields."""
    if not _ID_NAMESPACE.fullmatch(namespace):
        raise ValueError("namespace must be a bounded lowercase identifier")
    if not identity:
        raise ValueError("identity must not be empty")
    return f"{namespace}-{sha256_json(dict(identity))[:32]}"


def access_partition_id(redaction_class: str, profile_id: str) -> str:
    """Map source visibility to the narrowest authoritative partition."""
    if redaction_class == "public":
        return "public"
    if redaction_class not in {"authenticated", "restricted"}:
        raise ValueError(f"unsupported redaction_class: {redaction_class}")
    if not profile_id.strip():
        raise ValueError("profile_id is required for non-public material")
    return f"profile:{profile_id}"


def schema7_compatibility_export(db_path: Path) -> dict[str, object]:
    """Export current temporal projections as deterministic schema-7 replay rows."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        database_schema_version = int(
            conn.execute("SELECT MAX(version) FROM schema_version").fetchone()[0]
        )
        rows = conn.execute(
            """SELECT
                   d.document_id,
                   v.acquisition_id,
                   d.source,
                   d.source_native_id,
                   d.canonical_url,
                   v.title,
                   v.author,
                   v.normalized_text,
                   v.content_hash,
                   v.published_at,
                   v.fetched_at,
                   v.retention_class,
                   v.redaction_class,
                   v.transformation_version,
                   v.source_metadata_json,
                   v.media_json
               FROM documents AS d
               JOIN document_versions AS v
                 ON v.version_id = d.current_version_id
               ORDER BY d.document_id"""
        ).fetchall()
    finally:
        conn.close()

    documents = []
    for row in rows:
        record = dict(row)
        record["source_metadata"] = json.loads(record.pop("source_metadata_json"))
        record["media"] = json.loads(record.pop("media_json"))
        documents.append(record)
    return {
        "format": "last30days-schema7-replay-v1",
        "database_schema_version": database_schema_version,
        "documents": documents,
    }


def write_schema7_compatibility_export(
    db_path: Path, output_path: Path
) -> dict[str, object]:
    """Atomically write a replay export and return its content-addressed receipt."""
    payload = schema7_compatibility_export(db_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = output_path.with_name(f".{output_path.name}.tmp")
    temporary_path.write_text(
        f"{_canonical_json(payload)}\n",
        encoding="utf-8",
    )
    temporary_path.replace(output_path)
    return {
        "format": "last30days-schema7-replay-receipt-v1",
        "document_count": len(payload["documents"]),
        "payload_sha256": sha256_json(payload),
        "output_path": str(output_path),
    }
