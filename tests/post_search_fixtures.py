"""Synthetic stored embeddings; no providers, source data, or service runtime."""

import hashlib
import json
import sqlite3
import struct

from lib.service_retrieval import LocalHashEmbeddingProvider
from tests.test_service_post_search import _seed_post_corpus

STAMP = "2026-09-10T00:00:00Z"


def add_vectors(db, *, query="reliable browser agents", overrides=None):
    """Persist fixture vectors for public current versions in both stores."""
    vector = LocalHashEmbeddingProvider().embed([query])[0]
    overrides = overrides or {}
    with sqlite3.connect(db) as conn:
        conn.execute(
            """INSERT OR IGNORE INTO service_tick_query_snapshots VALUES
            ('search-fixture', 'tick-fixture', 'local-hash-v1', 256,
             'rrf-v1', '{}', 'fixture-digest', 'promoted', ?, ?)""",
            (STAMP, STAMP),
        )
        for family, origins, versions, key in (
            ("legacy", "documents", "document_versions", "document_id"),
            (
                "temporal",
                "service_source_records",
                "service_source_versions",
                "record_id",
            ),
        ):
            rows = conn.execute(
                f"""SELECT v.version_id, v.{key}, v.content_hash, v.title,
                    v.normalized_text, o.source, o.canonical_url, v.access_partition_id
                    FROM {origins} o JOIN {versions} v ON v.version_id=o.current_version_id
                    WHERE v.access_partition_id='public'"""
            ).fetchall()
            for (
                version,
                origin,
                content_hash,
                title,
                text,
                source,
                url,
                partition,
            ) in rows:
                selected = overrides.get(version, vector)
                if selected is None:
                    continue
                if family == "legacy":
                    packed = struct.pack(f"<{len(selected)}d", *selected)
                    conn.execute(
                        "INSERT INTO document_version_chunks VALUES (?, ?, ?, 0, ?, ?, 'fixture', ?)",
                        (version, version, origin, text, content_hash, partition),
                    )
                    conn.execute(
                        "INSERT INTO document_version_embeddings VALUES (?, 'local-hash-v1', ?, ?, ?, ?)",
                        (
                            version,
                            len(selected),
                            packed,
                            hashlib.sha256(packed).hexdigest(),
                            STAMP,
                        ),
                    )
                else:
                    conn.execute(
                        "INSERT INTO service_tick_query_entries VALUES ('search-fixture', ?, 'lexical_source', ?, ?, ?, ?, ?, ?, ?)",
                        (
                            version,
                            source,
                            partition,
                            STAMP,
                            f"{title}\n{text}",
                            json.dumps(selected),
                            json.dumps({"version_id": version, "url": url}),
                            content_hash,
                        ),
                    )


def seed_large_corpus(db, count=10_000):
    _seed_post_corpus(db)
    with sqlite3.connect(db) as conn:
        conn.row_factory = sqlite3.Row
        for origins, versions, key, origin, version, source in (
            (
                "documents",
                "document_versions",
                "document_id",
                "doc-legacy",
                "version-legacy-current",
                "reddit",
            ),
            (
                "service_source_records",
                "service_source_versions",
                "record_id",
                "record-tick-public",
                "version-tick-public",
                "x",
            ),
        ):
            template_origin = dict(
                conn.execute(
                    f"SELECT * FROM {origins} WHERE {key}=?", (origin,)
                ).fetchone()
            )
            template_version = dict(
                conn.execute(
                    f"SELECT * FROM {versions} WHERE version_id=?", (version,)
                ).fetchone()
            )
            for index in range(1, count // 2):
                origin_id, version_id = f"{origin}-{index}", f"{version}-{index}"
                values = {
                    **template_origin,
                    key: origin_id,
                    "current_version_id": version_id,
                    "source_native_id": origin_id,
                    "canonical_url": f"https://{source}.example/fixture/{index}",
                }
                conn.execute(
                    f"INSERT INTO {origins} ({','.join(values)}) VALUES ({','.join('?' for _ in values)})",
                    tuple(values.values()),
                )
                values = {
                    **template_version,
                    key: origin_id,
                    "version_id": version_id,
                    "content_hash": f"sha256:{version_id}",
                }
                conn.execute(
                    f"INSERT INTO {versions} ({','.join(values)}) VALUES ({','.join('?' for _ in values)})",
                    tuple(values.values()),
                )
    add_vectors(db)
