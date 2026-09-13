"""Provider-free product tests for stored-post search."""

import json
import sqlite3
import threading
from pathlib import Path

import pytest

from lib import service_contracts as contracts
from lib.service_post_search import PostSearchBackend
from lib.service_retrieval import HybridRetriever
from lib.service_app import initialize_application
from lib.service_client import ServiceClient
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

    assert request.to_dict() == payload

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

    assert set(request_schema["properties"]) == set(_request_payload())
    assert set(request_schema["properties"]["filters"]["properties"]) == {
        "sources",
        "published_after",
        "published_before",
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
    assert [hit.revision_id for hit in time_filtered.hits] == [
        "version-tick-public"
    ]


def test_post_search_cursor_is_complete_and_rejects_request_or_head_drift(tmp_path):
    db_path = tmp_path / "post-search.db"
    _seed_post_corpus(db_path)
    backend = PostSearchBackend(db_path)
    first_request = contracts.PostSearchRequest.from_dict(
        _request_payload(page_size=1)
    )

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
    with pytest.raises(contracts.ContractValidationError, match="cursor is stale"):
        backend.search(
            contracts.PostSearchRequest.from_dict(
                _request_payload(page_size=1, cursor=first.next_cursor)
            ),
            access_partitions=("public",),
        )


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
