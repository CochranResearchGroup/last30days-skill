"""Provider-free product tests for stored-post search."""

import json
import base64
import sqlite3
import threading
from pathlib import Path

import pytest

from lib import service_contracts as contracts
from lib.service_post_search import PostSearchBackend
from lib.service_retrieval import HybridRetriever
from lib.service_app import initialize_application
from lib.service_client import ServiceClient
from lib.service_client import ServiceClientError
from lib.service_http import UnixServiceServer


FIXTURE = json.loads(
    (Path(__file__).parent / "fixtures" / "post_search_packet1.json").read_text(
        encoding="utf-8"
    )
)


def _request_payload(**overrides):
    payload = json.loads(json.dumps(FIXTURE["service_request"]))
    payload.update(overrides)
    return payload


def test_post_search_request_round_trips_the_strict_packet_one_contract():
    payload = _request_payload()

    request = contracts.PostSearchRequest.from_dict(payload)

    assert request.to_dict() == {
        **payload,
        "revision_mode": "current",
        "sort": "relevance",
    }

    with pytest.raises(contracts.ContractValidationError, match="unknown fields"):
        contracts.PostSearchRequest.from_dict({**payload, "semantic": True})

    with pytest.raises(contracts.ContractValidationError, match="published_after"):
        contracts.PostSearchRequest.from_dict(
            _request_payload(
                filters={
                    "published_after": "2026-09-14T00:00:00Z",
                    "published_before": "2026-09-13T00:00:00Z",
                }
            )
        )

    with pytest.raises(contracts.ContractValidationError, match="lexical token"):
        contracts.PostSearchRequest.from_dict(_request_payload(query="---"))

    with pytest.raises(contracts.ContractValidationError, match="profile_id"):
        contracts.PostSearchRequest.from_dict(
            _request_payload(profile_id="invalid profile")
        )


def test_post_search_schema_matches_the_runtime_contract():
    catalog = contracts.load_post_search_schema_catalog()
    request_schema = catalog["contracts"]["post_search_request"]

    assert set(request_schema["properties"]) == set(_request_payload()) | {
        "revision_mode",
        "sort",
    }
    assert set(request_schema["properties"]["filters"]["properties"]) == {
        "sources",
        "published_after",
        "published_before",
        "authors",
        "topic_ids",
        "collection_refs",
        "observed_after",
        "observed_before",
    }


def _seed_post_corpus(db_path):
    HybridRetriever(db_path).initialize()
    conn = sqlite3.connect(db_path)
    conn.execute(
        """INSERT INTO documents (
               document_id, acquisition_id, source, source_native_id,
               canonical_url, title, author, normalized_text, content_hash,
               published_at, fetched_at, retention_class, redaction_class,
               transformation_version, current_version_id, access_partition_id,
               source_metadata_json, media_json
           ) VALUES (
               'doc-legacy', 'acq-fixture', 'reddit', 'reddit-1',
               'https://reddit.example/1', 'Legacy browser post', 'alice',
               'stale browser draft', 'sha256:legacy-old',
               '2026-09-05T12:00:00Z', '2026-09-05T12:01:00Z', 'cache',
               'public', 'fixture-v1', 'version-legacy-current', 'public', '{}', '[]'
           )"""
    )
    for version_id, text, content_hash, system_from in (
        (
            "version-legacy-old",
            "stale browser draft",
            "sha256:legacy-old",
            "2026-09-05T12:01:00Z",
        ),
        (
            "version-legacy-current",
            "reliable browser agents from legacy storage",
            "sha256:legacy-current",
            "2026-09-06T12:01:00Z",
        ),
    ):
        conn.execute(
            """INSERT INTO document_versions (
                   version_id, document_id, acquisition_id, content_hash, title,
                   author, normalized_text, source_metadata_json, media_json,
                   published_at, valid_from, valid_to, observed_at, fetched_at,
                   system_from, system_to, retention_class, redaction_class,
                   access_partition_id, transformation_version
               ) VALUES (?, 'doc-legacy', 'acq-fixture', ?, 'Legacy browser post',
                         'alice', ?, '{}', '[]', '2026-09-05T12:00:00Z',
                         '2026-09-05T12:00:00Z', NULL, '2026-09-05T12:01:00Z',
                         '2026-09-05T12:01:00Z', ?, NULL, 'cache', 'public',
                         'public', 'fixture-v1')""",
            (version_id, content_hash, text, system_from),
        )
    for record_id, version_id, partition, text in (
        (
            "record-tick-public",
            "version-tick-public",
            "public",
            "reliable browser agents from temporal storage",
        ),
        (
            "record-tick-private",
            "version-tick-private",
            "profile:other",
            "reliable browser agents private",
        ),
    ):
        conn.execute(
            """INSERT INTO service_source_records (
                   record_id, service_id, source, source_native_id, canonical_url,
                   access_partition_id, current_version_id, created_at
               ) VALUES (?, 'x-service', 'x', ?, ?, ?, ?, '2026-09-07T12:01:00Z')""",
            (
                record_id,
                record_id,
                f"https://x.example/{record_id}",
                partition,
                version_id,
            ),
        )
        conn.execute(
            """INSERT INTO service_source_versions (
                   version_id, record_id, provider_attempt_id, content_hash,
                   title, normalized_text, author, published_at, metadata_json,
                   observed_at, access_partition_id, retention_class, created_at
               ) VALUES (?, ?, 'attempt-fixture', ?, 'Temporal browser post', ?,
                         'bob', '2026-09-07T12:00:00Z', '{}',
                         '2026-09-07T12:01:00Z', ?, 'cache',
                         '2026-09-07T12:01:00Z')""",
            (version_id, record_id, f"sha256:{version_id}", text, partition),
        )
    conn.commit()
    conn.close()


def test_post_search_federates_current_revisions_with_immutable_evidence(tmp_path):
    db_path = tmp_path / "post-search.db"
    _seed_post_corpus(db_path)
    backend = PostSearchBackend(db_path)

    response = backend.search(
        contracts.PostSearchRequest.from_dict(_request_payload(page_size=10)),
        access_partitions=("public",),
    )

    assert [hit.storage_family for hit in response.hits] == ["legacy", "temporal"]
    assert {hit.revision_id for hit in response.hits} == set(
        FIXTURE["expected_revision_ids"]
    )
    assert all(hit.access_partition_id == "public" for hit in response.hits)
    assert all(hit.evidence_ref.version_id == hit.revision_id for hit in response.hits)
    assert response.returned == 2
    assert response.next_cursor is None

    source_filtered = backend.search(
        contracts.PostSearchRequest.from_dict(
            _request_payload(filters={"sources": ["reddit"]})
        ),
        access_partitions=("public",),
    )
    assert [hit.revision_id for hit in source_filtered.hits] == [
        "version-legacy-current"
    ]

    time_filtered = backend.search(
        contracts.PostSearchRequest.from_dict(
            _request_payload(filters={"published_after": "2026-09-06T00:00:00Z"})
        ),
        access_partitions=("public",),
    )
    assert [hit.revision_id for hit in time_filtered.hits] == ["version-tick-public"]


def test_post_search_cursor_is_complete_and_rejects_request_drift(tmp_path):
    db_path = tmp_path / "post-search.db"
    _seed_post_corpus(db_path)
    backend = PostSearchBackend(db_path)
    first_request = contracts.PostSearchRequest.from_dict(_request_payload(page_size=1))

    first = backend.search(first_request, access_partitions=("public",))
    assert first.truncated is True
    assert first.next_cursor is not None

    second = backend.search(
        contracts.PostSearchRequest.from_dict(
            _request_payload(
                request_id="post-search-002",
                page_size=1,
                cursor=first.next_cursor,
            )
        ),
        access_partitions=("public",),
    )
    assert second.returned == 1
    assert second.next_cursor is None
    assert first.hits[0].revision_id != second.hits[0].revision_id

    with pytest.raises(
        contracts.ContractValidationError, match="fingerprint does not match"
    ):
        backend.search(
            contracts.PostSearchRequest.from_dict(
                _request_payload(
                    query="different query", page_size=1, cursor=first.next_cursor
                )
            ),
            access_partitions=("public",),
        )

    with pytest.raises(contracts.ContractValidationError, match="cursor"):
        backend.search(
            contracts.PostSearchRequest.from_dict(
                _request_payload(page_size=1, cursor=first.next_cursor + "tamper")
            ),
            access_partitions=("public",),
        )

    conn = sqlite3.connect(db_path)
    conn.execute(
        "UPDATE documents SET current_version_id = 'version-legacy-old' "
        "WHERE document_id = 'doc-legacy'"
    )
    conn.commit()
    conn.close()
    retained = backend.search(
        contracts.PostSearchRequest.from_dict(
            _request_payload(page_size=1, cursor=first.next_cursor)
        ),
        access_partitions=("public",),
    )
    assert retained.hits == second.hits


def test_post_search_crosses_application_http_and_typed_client(tmp_path):
    db_path = tmp_path / "post-search.db"
    socket_path = tmp_path / "runtime" / "service.sock"
    _seed_post_corpus(db_path)
    application = initialize_application(db_path, retriever=object())
    server = UnixServiceServer(socket_path, application)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        response = ServiceClient(socket_path).search_posts(
            contracts.PostSearchRequest.from_dict(_request_payload(page_size=10))
        )
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    assert response.returned == 2
    assert {hit.storage_family for hit in response.hits} == {"legacy", "temporal"}


def _seed_packet_two(db_path):
    _seed_post_corpus(db_path)
    with sqlite3.connect(db_path) as conn:
        conn.execute("""INSERT INTO document_version_sightings
            (version_id, acquisition_id, topic_id, collection_spec_id,
             collection_run_id, observed_at, access_partition_id)
            VALUES ('version-legacy-current', 'acq-fixture', 7, 'spec-1',
                    'run-1', '2026-09-08T12:01:00Z', 'public')""")
        # A private sighting must never become public provenance.
        conn.execute("""INSERT INTO document_version_sightings
            (version_id, acquisition_id, topic_id, collection_spec_id,
             observed_at, access_partition_id)
            VALUES ('version-legacy-current', 'private-acq', 99, 'secret',
                    '2026-09-09T12:01:00Z', 'profile:other')""")
        conn.execute("""INSERT INTO service_ticks
            (tick_id, schedule_id, interval_from, interval_to, trigger,
             config_revision, config_digest, config_json, state, created_at, updated_at)
            VALUES ('tick-1', 'schedule-1', '2026-09-07T00:00:00Z',
                    '2026-09-08T00:00:00Z', 'manual', 'v1', 'digest', '{}',
                    'complete', '2026-09-08T00:00:00Z', '2026-09-08T00:00:00Z')""")
        conn.execute("""INSERT INTO service_tick_lanes
            (lane_id, tick_id, service_id, target_id, access_partition_id,
             service_config_json, target_config_json, lane_digest, state,
             created_at, updated_at)
            VALUES ('lane-1', 'tick-1', 'x-service', 'target-1', 'public',
                    '{}', '{}', 'digest', 'success', '2026-09-08T00:00:00Z',
                    '2026-09-08T00:00:00Z')""")
        conn.execute("""INSERT INTO service_source_sightings
            VALUES ('version-tick-public', 'tick-1', 'lane-1',
                    'attempt-fixture', '2026-09-08T12:01:00Z')""")
        # Immutable temporal topic evidence belongs to the version metadata.
        conn.execute("""INSERT INTO service_source_versions
            SELECT 'version-tick-new', record_id, provider_attempt_id,
                   'sha256:tick-new', title, normalized_text, author, published_at,
                   '{"topic_ids":["7"]}', observed_at, access_partition_id,
                   retention_class, '2026-09-08T12:01:00Z'
            FROM service_source_versions WHERE version_id='version-tick-public'""")
        conn.execute(
            "UPDATE service_source_records SET current_version_id='version-tick-new' WHERE record_id='record-tick-public'"
        )
        conn.execute("""INSERT INTO service_source_sightings
            SELECT 'version-tick-new', tick_id, lane_id, provider_attempt_id, observed_at
            FROM service_source_sightings WHERE version_id='version-tick-public'""")


@pytest.mark.parametrize(
    "filters,expected",
    [
        ({"authors": ["alice"]}, {"legacy"}),
        ({"authors": ["bob"]}, {"temporal"}),
        ({"authors": ["absent"]}, set()),
        ({"topic_ids": ["7"]}, {"legacy", "temporal"}),
        ({"topic_ids": ["99"]}, set()),
        ({"collection_refs": ["legacy:spec:spec-1"]}, {"legacy"}),
        ({"collection_refs": ["legacy:run:run-1"]}, {"legacy"}),
        ({"collection_refs": ["temporal:schedule:schedule-1"]}, {"temporal"}),
        ({"collection_refs": ["temporal:target:x-service:target-1"]}, {"temporal"}),
        ({"collection_refs": ["legacy:spec:secret"]}, set()),
        ({"observed_after": "2026-09-08T12:00:00Z"}, {"legacy", "temporal"}),
        ({"observed_before": "2026-09-07T00:00:00Z"}, {"legacy"}),
        ({"authors": ["alice"], "topic_ids": ["7"], "sources": ["x"]}, set()),
    ],
)
def test_packet_two_filters_and_browse_are_applied_in_both_stores(
    tmp_path, filters, expected
):
    db = tmp_path / "search.db"
    _seed_packet_two(db)
    request = contracts.PostSearchRequest.from_dict(
        _request_payload(query=None, filters=filters)
    )
    response = PostSearchBackend(db).search(request, access_partitions=("public",))
    assert {hit.storage_family for hit in response.hits} == expected
    assert all(hit.score == 0 and not hit.matching_channels for hit in response.hits)
    assert all("99" not in hit.topic_ids for hit in response.hits)
    assert all("legacy:spec:secret" not in hit.collection_refs for hit in response.hits)


def test_packet_two_all_revisions_and_cross_store_collision_keep_provenance(tmp_path):
    db = tmp_path / "search.db"
    _seed_packet_two(db)
    with sqlite3.connect(db) as conn:
        conn.execute("""INSERT INTO service_source_records VALUES
            ('replica', 'reddit-service', 'reddit', 'reddit-1',
             'https://reddit.example/1', 'public', 'replica-v1', '2026-09-06T12:01:00Z')""")
        conn.execute("""INSERT INTO service_source_versions
            SELECT 'replica-v1', 'replica', 'fixture-attempt', content_hash,
                   title, normalized_text, author, published_at, '{}', observed_at,
                   access_partition_id, retention_class, system_from
            FROM document_versions WHERE version_id='version-legacy-current'""")
    backend = PostSearchBackend(db)
    current = backend.search(
        contracts.PostSearchRequest.from_dict(
            _request_payload(query=None, filters={"sources": ["reddit"]})
        ),
        access_partitions=("public",),
    )
    assert current.returned == 1
    assert {ref.version_id for ref in current.hits[0].evidence_refs} == {
        "version-legacy-current",
        "replica-v1",
    }
    assert current.hits[0].collection_refs == ("legacy:run:run-1", "legacy:spec:spec-1")
    revisions = backend.search(
        contracts.PostSearchRequest.from_dict(
            _request_payload(
                query=None, filters={"sources": ["reddit"]}, revision_mode="all"
            )
        ),
        access_partitions=("public",),
    )
    assert revisions.returned == 2
    assert len({hit.post_id for hit in revisions.hits}) == 1
    assert {hit.evidence_ref.content_hash for hit in revisions.hits} == {
        "sha256:legacy-old",
        "sha256:legacy-current",
    }


def test_packet_two_cursor_survives_publication_but_not_eviction_or_restart(tmp_path):
    db = tmp_path / "search.db"
    _seed_packet_two(db)
    backend = PostSearchBackend(db, snapshot_capacity=1)
    payload = _request_payload(
        query=None,
        filters={"sources": ["reddit", "x"]},
        revision_mode="all",
        page_size=1,
    )
    first = backend.search(
        contracts.PostSearchRequest.from_dict(payload), access_partitions=("public",)
    )
    with sqlite3.connect(db) as conn:
        conn.execute("""INSERT INTO service_source_versions
            SELECT 'published-later', record_id, provider_attempt_id,
                   'sha256:later', title, normalized_text, author, published_at,
                   metadata_json, observed_at, access_partition_id,
                   retention_class, '2026-09-10T00:00:00Z'
            FROM service_source_versions WHERE version_id='version-tick-public'""")
        conn.execute(
            "UPDATE service_source_records SET current_version_id='published-later' WHERE record_id='record-tick-public'"
        )
    hits = list(first.hits)
    page = first
    while page.next_cursor:
        page = backend.search(
            contracts.PostSearchRequest.from_dict(
                {**payload, "cursor": page.next_cursor}
            ),
            access_partitions=("public",),
        )
        assert page.search_head_id == first.search_head_id
        hits.extend(page.hits)
    assert len(hits) == len({(hit.post_id, hit.revision_id) for hit in hits}) == 4
    assert "published-later" not in {hit.revision_id for hit in hits}
    replay = contracts.PostSearchRequest.from_dict(
        {**payload, "cursor": first.next_cursor}
    )
    with pytest.raises(contracts.ContractValidationError, match="cursor_stale"):
        PostSearchBackend(db).search(replay, access_partitions=("public",))
    with pytest.raises(contracts.ContractValidationError, match="fingerprint"):
        backend.search(replay, access_partitions=("public", "profile:other"))
    backend.search(
        contracts.PostSearchRequest.from_dict({**payload, "query": "browser"}),
        access_partitions=("public",),
    )
    with pytest.raises(contracts.ContractValidationError, match="cursor_stale"):
        backend.search(replay, access_partitions=("public",))


def test_packet_two_public_contract_parity_and_stale_error(tmp_path):
    fixture = json.loads(
        (Path(__file__).parent / "fixtures/post_search_packet2.json").read_text()
    )
    args = fixture["mcp_arguments"]
    payload = _request_payload(
        query=None,
        filters={
            key: value
            for key, value in args.items()
            if key not in {"page_size", "sort", "revision_mode"}
        },
        page_size=args["page_size"],
        sort=args["sort"],
        revision_mode=args["revision_mode"],
    )
    db = tmp_path / "search.db"
    _seed_packet_two(db)
    app = initialize_application(db, retriever=object())
    ticks = [0.0]
    app.post_search_backend = PostSearchBackend(
        db, snapshot_ttl_seconds=1, monotonic=lambda: ticks[0]
    )
    server = UnixServiceServer(tmp_path / "runtime/service.sock", app)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    before = db.read_bytes()
    try:
        client = ServiceClient(server.socket_path)
        first = client.search_posts(contracts.PostSearchRequest.from_dict(payload))
        second = client.search_posts(
            contracts.PostSearchRequest.from_dict(
                {**payload, "cursor": first.next_cursor}
            )
        )
        assert {hit.revision_id for hit in (*first.hits, *second.hits)} == set(
            fixture["expected_version_ids"]
        )
        assert first.revision_mode == "all" and first.sort == "observed_desc"
        ticks[0] = 1.0
        with pytest.raises(ServiceClientError, match="cursor_stale"):
            client.search_posts(
                contracts.PostSearchRequest.from_dict(
                    {**payload, "cursor": first.next_cursor}
                )
            )
        with pytest.raises(ServiceClientError, match="invalid_contract"):
            client._request("POST", "/v1/posts/search", {**payload, "filters": {}})
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
    assert db.read_bytes() == before


@pytest.mark.parametrize("sort", ["relevance", "published_desc", "observed_desc"])
def test_packet_two_sort_pages_equal_one_shot_with_missing_publication(tmp_path, sort):
    db = tmp_path / "search.db"
    _seed_packet_two(db)
    with sqlite3.connect(db) as conn:
        conn.execute("""INSERT INTO service_source_versions
            SELECT 'no-publication', record_id, provider_attempt_id,
                   'sha256:no-publication', title, normalized_text, author, NULL,
                   metadata_json, observed_at, access_partition_id, retention_class,
                   '2026-09-10T00:00:00Z'
            FROM service_source_versions WHERE version_id='version-tick-public'""")
    backend = PostSearchBackend(db)
    payload = _request_payload(
        query=None, filters={"sources": ["reddit", "x"]}, revision_mode="all", sort=sort
    )
    expected = backend.search(
        contracts.PostSearchRequest.from_dict({**payload, "page_size": 100}),
        access_partitions=("public",),
    )
    hits, cursor = [], None
    while True:
        page = backend.search(
            contracts.PostSearchRequest.from_dict(
                {**payload, "page_size": 1, "cursor": cursor}
            ),
            access_partitions=("public",),
        )
        hits.extend(page.hits)
        cursor = page.next_cursor
        if cursor is None:
            break
    assert hits == list(expected.hits)
    if sort == "published_desc":
        assert hits[-1].published_at is None


def test_packet_two_filters_precede_ranking_and_snapshot_bounds_fail_closed(
    tmp_path, monkeypatch
):
    from lib import service_post_search

    db = tmp_path / "search.db"
    _seed_packet_two(db)

    class ObservedBackend(PostSearchBackend):
        def _rank(self, rows, request):
            assert all(
                row["author"] == "alice" and row["access_partition_id"] == "public"
                for row in rows
            )
            return super()._rank(rows, request)

    request = contracts.PostSearchRequest.from_dict(
        _request_payload(filters={"authors": ["alice"]})
    )
    assert (
        ObservedBackend(db).search(request, access_partitions=("public",)).returned == 1
    )
    broad = contracts.PostSearchRequest.from_dict(_request_payload(page_size=1))
    monkeypatch.setattr(service_post_search, "MAX_SNAPSHOT_ROWS", 1)
    with pytest.raises(
        contracts.ContractValidationError, match="search_snapshot_too_large"
    ):
        PostSearchBackend(db).search(broad, access_partitions=("public",))
    monkeypatch.setattr(service_post_search, "MAX_SNAPSHOT_ROWS", 10000)
    monkeypatch.setattr(service_post_search, "MAX_RETAINED_BYTES", 1)
    with pytest.raises(
        contracts.ContractValidationError, match="search_snapshot_too_large"
    ):
        PostSearchBackend(db).search(broad, access_partitions=("public",))


@pytest.mark.parametrize(
    "overrides",
    [
        {"query": None, "filters": {}},
        {"query": ""},
        {"revision_mode": "latest"},
        {"sort": ""},
        {"filters": {"authors": []}},
        {"filters": {"topic_ids": ["7", "7"]}},
        {"filters": {"collection_refs": ["unscoped"]}},
        {"filters": {"observed_after": None}},
        {
            "filters": {
                "observed_after": "2026-09-09T00:00:00Z",
                "observed_before": "2026-09-08T00:00:00Z",
            }
        },
    ],
)
def test_packet_two_invalid_contracts_are_rejected(overrides):
    with pytest.raises(contracts.ContractValidationError):
        contracts.PostSearchRequest.from_dict(_request_payload(**overrides))


def test_packet_two_url_fallback_and_private_native_collision(tmp_path):
    db = tmp_path / "search.db"
    _seed_packet_two(db)
    with sqlite3.connect(db) as conn:
        conn.execute(
            "UPDATE service_source_records SET source_native_id='' WHERE record_id='record-tick-public'"
        )
        conn.execute(
            "UPDATE service_source_records SET source_native_id='', canonical_url='https://x.example/same', source='reddit' WHERE record_id='record-tick-private'"
        )
        conn.execute(
            "UPDATE documents SET source_native_id='' WHERE document_id='doc-legacy'"
        )
    request = contracts.PostSearchRequest.from_dict(
        _request_payload(query=None, filters={"sources": ["reddit", "x"]})
    )
    hits = (
        PostSearchBackend(db)
        .search(request, access_partitions=("public", "profile:other"))
        .hits
    )
    assert len(hits) == len({hit.post_id for hit in hits}) == 3
    assert all(hit.source_native_id is None for hit in hits)


def test_packet_two_missing_database_is_not_created_and_cursor_types_fail_closed(
    tmp_path,
):
    from lib.service_post_search import _canonical_json, _digest

    db = tmp_path / "missing.db"
    request = contracts.PostSearchRequest.from_dict(_request_payload(page_size=1))
    with pytest.raises(sqlite3.OperationalError):
        PostSearchBackend(db).search(request, access_partitions=("public",))
    assert not db.exists()
    _seed_packet_two(db)
    backend = PostSearchBackend(db)
    page = backend.search(request, access_partitions=("public",))
    decoded = backend._decode_cursor(page.next_cursor)
    for key, value in (
        ("last", [True, "post", "version"]),
        ("component_heads", {"legacy": "forged", "temporal": "forged"}),
    ):
        core = {**decoded, key: value}
        forged = (
            base64.urlsafe_b64encode(
                _canonical_json({**core, "checksum": _digest(core)}).encode()
            )
            .decode()
            .rstrip("=")
        )
        with pytest.raises(contracts.ContractValidationError, match="cursor"):
            backend.search(
                contracts.PostSearchRequest.from_dict(
                    _request_payload(page_size=1, cursor=forged)
                ),
                access_partitions=("public",),
            )
