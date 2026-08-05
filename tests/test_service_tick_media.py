"""Immutable media, OCR, and semantic-sidecar behavior for durable ticks."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone

from lib.service_tick_media import (
    ContentAddressedArtifactStore,
    MediaDerivativePublisher,
    OcrRegion,
    SemanticSidecar,
)


NOW = datetime(2026, 8, 4, 12, 0, tzinfo=timezone.utc)


def test_media_derivatives_are_content_addressed_partition_inheriting_and_citable(
    tmp_path,
):
    db_path = tmp_path / "research.db"
    publisher = MediaDerivativePublisher(
        db_path,
        ContentAddressedArtifactStore(tmp_path / "artifacts"),
        clock=lambda: NOW,
    )

    asset = publisher.store_asset(
        parent_version_id="version-authenticated-post",
        source_url="https://media.example/post/image.png",
        content=b"deterministic-image-bytes",
        mime_type="image/png",
        media_kind="image",
        alt_text="A chart with one rising line",
        access_partition_id="profile:social-primary",
        retention_class="durable",
    )
    repeated = publisher.store_asset(
        parent_version_id="version-authenticated-post",
        source_url="https://media.example/post/image.png",
        content=b"deterministic-image-bytes",
        mime_type="image/png",
        media_kind="image",
        alt_text="A chart with one rising line",
        access_partition_id="profile:social-primary",
        retention_class="durable",
    )
    ocr = publisher.publish_ocr(
        asset.asset_id,
        engine="fixture-ocr",
        engine_version="1",
        detected_language="en",
        regions=(
            OcrRegion(
                ordinal=0,
                text="Revenue",
                bounding_box=(10, 20, 110, 60),
                confidence=0.98,
            ),
        ),
    )
    sidecar = publisher.publish_sidecar(
        asset.asset_id,
        SemanticSidecar(
            literal_description="A blue line rises from left to right.",
            observable_entities=("line chart",),
            observable_relationships=("line rises across chart",),
            objects_actions=("line:rising",),
            inferred_context=("may depict increasing revenue",),
            search_terms=("rising line chart", "revenue chart"),
            uncertainty=("axis values are not legible",),
            model_provider="fixture-model",
            model_version="1",
            input_refs=(asset.asset_id, ocr.derivative_id, "source-alt-text"),
        ),
    )
    citation = publisher.ocr_citation(ocr.derivative_id, region_ordinal=0)

    assert repeated == asset
    assert publisher.artifacts.read(asset.storage_ref) == b"deterministic-image-bytes"
    assert ocr.access_partition_id == sidecar.access_partition_id == (
        "profile:social-primary"
    )
    assert citation == {
        "parent_version_id": "version-authenticated-post",
        "media_asset_id": asset.asset_id,
        "content_hash": asset.content_hash,
        "source_url": "https://media.example/post/image.png",
        "derivative_id": ocr.derivative_id,
        "derivative_version": "fixture-ocr:1",
        "ocr_region_ordinal": 0,
        "ocr_region_confidence": 0.98,
    }
    conn = sqlite3.connect(db_path)
    assert conn.execute("SELECT COUNT(*) FROM service_media_assets").fetchone()[0] == 1
    assert conn.execute(
        "SELECT COUNT(*) FROM service_media_derivatives"
    ).fetchone()[0] == 2
    assert conn.execute("SELECT text FROM service_ocr_regions").fetchone()[0] == (
        "Revenue"
    )
    literal, inferred = conn.execute(
        """SELECT literal_description, inferred_context_json
           FROM service_semantic_sidecars"""
    ).fetchone()
    assert literal == "A blue line rises from left to right."
    assert "may depict increasing revenue" in inferred
    conn.close()
