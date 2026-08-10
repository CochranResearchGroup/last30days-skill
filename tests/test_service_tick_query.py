"""Tick-bound catalog and multi-channel snapshot publication."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone

import pytest

from lib import service_contracts as contracts
from lib.service_tick import TickCoordinator
from lib.service_tick_adapters import AdapterRegistry, AdapterSpec
from lib.service_tick_query import (
    CatalogMember,
    SnapshotEntry,
    TickSnapshotPublisher,
)


NOW = datetime(2026, 8, 4, 12, 0, tzinfo=timezone.utc)


class FixtureEmbedding:
    model = "fixture-space-v1"

    def embed(self, texts):
        return [
            [
                float("revenue" in text.casefold()),
                float("chart" in text.casefold()),
                float("browser" in text.casefold()),
            ]
            for text in texts
        ]


def _config(path):
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "config_revision": "query-config-1",
                "services": [
                    {
                        "service_id": "web",
                        "source": "web",
                        "providers": [
                            {
                                "provider_id": "web-keyless",
                                "adapter_type": "keyless",
                                "resource_keys": ["network:web"],
                                "fallback_on": [],
                                "limits": {
                                    "attempts": 1,
                                    "network_requests": 10,
                                    "wall_seconds": 30,
                                    "items": 10,
                                    "cost_cents": 0,
                                    "model_tokens": 0,
                                },
                            }
                        ],
                    }
                ],
                "targets": [
                    {
                        "target_id": "web-topic",
                        "service_id": "web",
                        "surface_kind": "topic",
                        "selector": {"topic": "revenue"},
                        "access_partition_id": "public",
                        "retention_class": "durable",
                        "enabled": True,
                    }
                ],
                "tick": {
                    "timezone": "UTC",
                    "lateness_seconds": 86400,
                    "aggregate_limits": {
                        "attempts": 2,
                        "network_requests": 20,
                        "wall_seconds": 60,
                        "items": 20,
                        "cost_cents": 0,
                        "model_tokens": 0,
                    },
                },
                "artifacts": {
                    "root": str(path.parent / "artifacts"),
                    "retention_days": 30,
                    "encryption_adapter": None,
                },
                "analysis": {
                    "ocr_enabled": True,
                    "ocr_adapter_type": "provider_output_ocr_v1",
                    "semantic_sidecars_enabled": True,
                    "semantic_sidecar_adapter_type": (
                        "provider_output_semantic_sidecar_v1"
                    ),
                },
                "notifications": {
                    "transports": [
                        {
                            "transport_id": "fixture",
                            "adapter_type": "fixture",
                            "credential_ref": "credential-ref:fixture",
                            "routing": {"recipient_ref": "recipient-ref:fixture"},
                        }
                    ],
                    "reminder_seconds": 3600,
                },
                "query": {
                    "embedding_space": "fixture-space-v1",
                    "fusion_version": "rrf-v1",
                },
            }
        ),
        encoding="utf-8",
    )


def test_staging_is_invisible_until_terminal_atomic_promotion_and_filters_run_first(
    tmp_path,
):
    config_path = tmp_path / "tick-config-v1.json"
    _config(config_path)
    db_path = tmp_path / "research.db"
    coordinator = TickCoordinator(
        db_path,
        config_path=config_path,
        adapter_registry=AdapterRegistry(
            [
                AdapterSpec(
                    "keyless",
                    frozenset({"collect"}),
                    frozenset({"web"}),
                    normalization_proof_ref="fixture:tick-query:web-keyless",
                )
            ]
        ),
        clock=lambda: NOW,
    )
    tick = coordinator.enqueue_tick(
        contracts.TickRequest.from_dict(
            {
                "schema_version": 1,
                "schedule_id": "manual-default",
                "interval_from": "2026-08-03T00:00:00Z",
                "interval_to": "2026-08-04T00:00:00Z",
                "trigger": "manual",
            }
        )
    )
    snapshots = TickSnapshotPublisher(db_path, FixtureEmbedding(), clock=lambda: NOW)
    cluster_id = snapshots.publish_cluster(
        tick.tick_id,
        cluster_kind="corroboration",
        label="Two services report rising revenue",
        rationale="Both records independently describe the same reported trend.",
        validator_version="cluster-validator-v1",
        members=(
            CatalogMember(
                member_id="version-web",
                source="web",
                relationship="supports",
                evidence_ref="evidence-web",
                access_partition_id="public",
                confidence=0.9,
            ),
            CatalogMember(
                member_id="version-reddit",
                source="reddit",
                relationship="supports",
                evidence_ref="evidence-reddit",
                access_partition_id="public",
                confidence=0.8,
            ),
        ),
    )
    staged = snapshots.stage(
        tick.tick_id,
        embedding_space="fixture-space-v1",
        fusion_version="rrf-v1",
        completeness={"web": "success"},
    )
    snapshots.add_entries(
        staged.snapshot_id,
        [
            SnapshotEntry(
                entry_id="source-public",
                channel="lexical_source",
                source="web",
                access_partition_id="public",
                published_at="2026-08-03T10:00:00Z",
                text="Quarterly revenue increased.",
                provenance={"version_id": "version-public"},
            ),
            SnapshotEntry(
                entry_id="ocr-private",
                channel="ocr",
                source="linkedin",
                access_partition_id="profile:private",
                published_at="2026-08-03T11:00:00Z",
                text="Confidential revenue chart",
                provenance={"derivative_id": "ocr-private"},
            ),
            SnapshotEntry(
                entry_id="sidecar-public",
                channel="semantic_sidecar",
                source="web",
                access_partition_id="public",
                published_at="2026-08-03T10:00:00Z",
                text="A chart showing rising revenue.",
                provenance={
                    "version_id": "version-public",
                    "derivative_id": "sidecar-public",
                },
            ),
        ],
    )

    assert snapshots.query("revenue chart", access_partitions=("public",)) == ()
    with pytest.raises(ValueError, match="terminal"):
        snapshots.promote(staged.snapshot_id)
    conn = sqlite3.connect(db_path)
    assert conn.execute(
        """SELECT member_id, source FROM service_catalog_cluster_members
           WHERE cluster_id = ? ORDER BY source""",
        (cluster_id,),
    ).fetchall() == [("version-reddit", "reddit"), ("version-web", "web")]
    conn.execute(
        "UPDATE service_ticks SET state = 'complete_degraded' WHERE tick_id = ?",
        (tick.tick_id,),
    )
    conn.execute(
        """UPDATE service_tick_stages SET state = 'success', completed_at = ?,
                  updated_at = ? WHERE tick_id = ?""",
        ("2026-08-04T12:00:00Z", "2026-08-04T12:00:00Z", tick.tick_id),
    )
    conn.commit()
    conn.close()

    snapshots.promote(staged.snapshot_id)
    results = snapshots.query(
        "revenue chart",
        access_partitions=("public",),
        sources=("web",),
    )

    assert [result.entry_id for result in results] == ["version-public"]
    assert results[0].matching_channels == (
        "lexical_source",
        "semantic_sidecar",
    )
    assert results[0].provenance["matching_entries"] == {
        "lexical_source": ["source-public"],
        "semantic_sidecar": ["sidecar-public"],
    }
    assert all(result.access_partition_id == "public" for result in results)
    assert all(result.source == "web" for result in results)
    assert snapshots.current().snapshot_id == staged.snapshot_id


def test_source_filter_selects_latest_terminal_snapshot_covering_that_source(tmp_path):
    config_path = tmp_path / "tick-config-v1.json"
    _config(config_path)
    db_path = tmp_path / "research.db"
    coordinator = TickCoordinator(
        db_path,
        config_path=config_path,
        adapter_registry=AdapterRegistry(
            [
                AdapterSpec(
                    "keyless",
                    frozenset({"collect"}),
                    frozenset({"web"}),
                    normalization_proof_ref="fixture:tick-query:web-keyless",
                )
            ]
        ),
        clock=lambda: NOW,
    )
    snapshots = TickSnapshotPublisher(db_path, FixtureEmbedding(), clock=lambda: NOW)

    def terminal_tick(schedule_id, interval_from, interval_to):
        tick = coordinator.enqueue_tick(
            contracts.TickRequest.from_dict(
                {
                    "schema_version": 1,
                    "schedule_id": schedule_id,
                    "interval_from": interval_from,
                    "interval_to": interval_to,
                    "trigger": "manual",
                }
            )
        )
        conn = sqlite3.connect(db_path)
        conn.execute(
            "UPDATE service_ticks SET state = 'complete' WHERE tick_id = ?",
            (tick.tick_id,),
        )
        conn.execute(
            """UPDATE service_tick_stages SET state = 'success', completed_at = ?,
                      updated_at = ? WHERE tick_id = ?""",
            ("2026-08-04T12:00:00Z", "2026-08-04T12:00:00Z", tick.tick_id),
        )
        conn.commit()
        conn.close()
        return tick

    x_tick = terminal_tick(
        "manual-x", "2026-08-01T00:00:00Z", "2026-08-02T00:00:00Z"
    )
    x_snapshot = snapshots.stage(
        x_tick.tick_id,
        embedding_space="fixture-space-v1",
        fusion_version="rrf-v1",
        completeness={"facebook": "empty", "x": "success"},
    )
    snapshots.add_entries(
        x_snapshot.snapshot_id,
        [
            SnapshotEntry(
                entry_id="version-x-current",
                channel="lexical_source",
                source="x",
                access_partition_id="profile:last30days-facebook",
                published_at="2026-08-01T12:00:00Z",
                text="OpenAI status evidence",
                provenance={"version_id": "version-x-current"},
            )
        ],
    )
    snapshots.promote(x_snapshot.snapshot_id)

    facebook_tick = terminal_tick(
        "manual-facebook", "2026-08-02T00:00:00Z", "2026-08-03T00:00:00Z"
    )
    facebook_snapshot = snapshots.stage(
        facebook_tick.tick_id,
        embedding_space="fixture-space-v1",
        fusion_version="rrf-v1",
        completeness={"facebook": "success"},
    )
    snapshots.add_entries(
        facebook_snapshot.snapshot_id,
        [
            SnapshotEntry(
                entry_id="version-facebook-current",
                channel="lexical_source",
                source="facebook",
                access_partition_id="profile:last30days-facebook",
                published_at="2026-08-02T12:00:00Z",
                text="OpenAI Facebook evidence",
                provenance={"version_id": "version-facebook-current"},
            )
        ],
    )
    snapshots.promote(facebook_snapshot.snapshot_id)

    assert snapshots.current_metadata()["snapshot_id"] == facebook_snapshot.snapshot_id
    selected = snapshots.current_metadata(sources=("x",))
    assert selected["snapshot_id"] == x_snapshot.snapshot_id
    assert selected["tick_id"] == x_tick.tick_id
    assert selected["interval_from"] == "2026-08-01T00:00:00Z"
    assert selected["interval_to"] == "2026-08-02T00:00:00Z"
    assert selected["promoted_at"] == "2026-08-04T12:00:00Z"
    assert snapshots.current_metadata(sources=("facebook", "x"))["snapshot_id"] == (
        x_snapshot.snapshot_id
    )
    assert snapshots.query(
        "OpenAI",
        access_partitions=("public",),
        sources=("x",),
        snapshot_id=selected["snapshot_id"],
    ) == ()
    assert snapshots.query(
        "OpenAI",
        access_partitions=("public", "profile:another-profile"),
        sources=("x",),
        snapshot_id=selected["snapshot_id"],
    ) == ()
    results = snapshots.query(
        "OpenAI",
        access_partitions=("public", "profile:last30days-facebook"),
        sources=("x",),
        snapshot_id=selected["snapshot_id"],
    )
    assert [result.entry_id for result in results] == ["version-x-current"]

    failed_tick = terminal_tick(
        "manual-x-failed", "2026-08-03T00:00:00Z", "2026-08-04T00:00:00Z"
    )
    failed_snapshot = snapshots.stage(
        failed_tick.tick_id,
        embedding_space="fixture-space-v1",
        fusion_version="rrf-v1",
        completeness={"x": "failure"},
    )
    snapshots.promote(failed_snapshot.snapshot_id)

    failed = snapshots.current_metadata(sources=("x",))
    assert failed["snapshot_id"] == failed_snapshot.snapshot_id
    assert failed["coverage_gaps"] == ["x"]
    assert snapshots.query(
        "OpenAI",
        access_partitions=("public", "profile:last30days-facebook"),
        sources=("x",),
        snapshot_id=failed["snapshot_id"],
    ) == ()

    empty_tick = terminal_tick(
        "manual-x-empty", "2026-08-04T00:00:00Z", "2026-08-05T00:00:00Z"
    )
    empty_snapshot = snapshots.stage(
        empty_tick.tick_id,
        embedding_space="fixture-space-v1",
        fusion_version="rrf-v1",
        completeness={"x": "empty"},
    )
    snapshots.promote(empty_snapshot.snapshot_id)

    empty = snapshots.current_metadata(sources=("x",))
    assert empty["snapshot_id"] == empty_snapshot.snapshot_id
    assert empty["coverage_gaps"] == []
    assert empty["interval_from"] == "2026-08-04T00:00:00Z"
    assert empty["interval_to"] == "2026-08-05T00:00:00Z"
    assert snapshots.query(
        "OpenAI",
        access_partitions=("public", "profile:last30days-facebook"),
        sources=("x",),
        snapshot_id=empty["snapshot_id"],
    ) == ()
