"""Temporal corpus identity and compatibility-export tests."""

import json

import pytest

import store
from lib import service_temporal


def test_temporal_ids_are_canonical_and_access_partitions_never_widen():
    left = service_temporal.stable_temporal_id(
        "version", {"document_id": "doc-1", "content_hash": "sha256:abc"}
    )
    right = service_temporal.stable_temporal_id(
        "version", {"content_hash": "sha256:abc", "document_id": "doc-1"}
    )

    assert left == right
    assert left.startswith("version-")
    assert service_temporal.access_partition_id("public", "ignored") == "public"
    assert (
        service_temporal.access_partition_id("authenticated", "linkedin-primary")
        == "profile:linkedin-primary"
    )
    with pytest.raises(ValueError, match="profile_id"):
        service_temporal.access_partition_id("authenticated", "")


def test_schema7_compatibility_export_is_deterministic_and_receipted(tmp_path):
    db_path = tmp_path / "temporal.db"
    output_path = tmp_path / "schema7-replay.json"
    store.init_db(db_path)

    first = service_temporal.schema7_compatibility_export(db_path)
    second = service_temporal.schema7_compatibility_export(db_path)
    receipt = service_temporal.write_schema7_compatibility_export(
        db_path, output_path
    )

    assert first == second
    assert first == json.loads(output_path.read_text(encoding="utf-8"))
    assert first["format"] == "last30days-schema7-replay-v1"
    assert first["database_schema_version"] == 8
    assert first["documents"] == []
    assert receipt == {
        "format": "last30days-schema7-replay-receipt-v1",
        "document_count": 0,
        "payload_sha256": service_temporal.sha256_json(first),
        "output_path": str(output_path),
    }
