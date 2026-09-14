"""Hybrid search behavior at the public backend seam."""

import json
import sqlite3
import threading

import pytest

from lib.service_contracts import (
    ContractValidationError,
    PostSearchHit,
    PostSearchRequest,
)
from lib.service_post_search import PostSearchBackend
from lib.service_app import initialize_application
from lib.service_client import ServiceClient, ServiceClientError
from lib.service_http import UnixServiceServer
from tests.post_search_fixtures import add_vectors
from tests.post_search_fixtures import seed_large_corpus
from tests.test_service_post_search import _request_payload, _seed_post_corpus
from tests.test_service_post_search import _seed_packet_two


def test_semantic_only_posts_and_dual_channel_scores_are_reproducible(tmp_path):
    db = tmp_path / "search.db"
    _seed_post_corpus(db)
    add_vectors(db, query="automated assistants")
    before = db.read_bytes()
    backend = PostSearchBackend(db)
    response = backend.search(
        PostSearchRequest.from_dict(_request_payload(query="automated assistants")),
        access_partitions=("public",),
    )
    assert {hit.storage_family for hit in response.hits} == {"legacy", "temporal"}
    for rank, hit in enumerate(response.hits, 1):
        assert hit.matching_channels == ("semantic",)
        assert hit.ranking["channels"]["semantic"]["rank"] == rank
        assert hit.ranking["channels"]["semantic"]["score"] == pytest.approx(1)
        assert hit.score == pytest.approx(1 / (60 + rank))
    assert response.coverage["semantic"]["families"]["legacy"]["eligible"] == 1
    assert response.coverage["semantic"]["families"]["temporal"]["eligible"] == 1
    assert db.read_bytes() == before


def test_multibyte_budget_shortened_pages_preserve_every_hit(tmp_path):
    db = tmp_path / "search.db"
    seed_large_corpus(db, count=40)
    # Clone immutable revisions to preserve realistic revision behavior.
    with sqlite3.connect(db) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM document_versions WHERE version_id LIKE 'version-legacy-current%'"
        ).fetchall()
        for row in rows:
            values = {
                **dict(row),
                "version_id": row["version_id"] + "-large",
                "content_hash": row["content_hash"] + "-large",
                "normalized_text": "browser " + "😀" * 4000,
            }
            conn.execute(
                f"INSERT INTO document_versions ({','.join(values)}) VALUES ({','.join('?' for _ in values)})",
                tuple(values.values()),
            )
            conn.execute(
                "UPDATE documents SET current_version_id=? WHERE document_id=?",
                (values["version_id"], values["document_id"]),
            )
    backend = PostSearchBackend(db)
    payload = _request_payload(query="browser", page_size=100)
    first = backend.search(
        PostSearchRequest.from_dict(payload), access_partitions=("public",)
    )
    assert (
        len(
            json.dumps(
                first.to_dict(),
                ensure_ascii=False,
                separators=(",", ":"),
                sort_keys=True,
            ).encode()
        )
        <= 131_072
    )
    assert first.returned < 40 and first.next_cursor
    hits, page = [], first
    while True:
        hits.extend(page.hits)
        assert (
            len(
                json.dumps(
                    page.to_dict(),
                    ensure_ascii=False,
                    separators=(",", ":"),
                    sort_keys=True,
                ).encode()
            )
            <= 131_072
        )
        if not page.next_cursor:
            break
        page = backend.search(
            PostSearchRequest.from_dict({**payload, "cursor": page.next_cursor}),
            access_partitions=("public",),
        )
    assert len(hits) == len({hit.post_id for hit in hits}) == 40
    small_backend = PostSearchBackend(db)
    small, cursor = [], None
    while True:
        page = small_backend.search(
            PostSearchRequest.from_dict({**payload, "page_size": 1, "cursor": cursor}),
            access_partitions=("public",),
        )
        small.extend(page.hits)
        cursor = page.next_cursor
        if not cursor:
            break
    assert hits == small


def test_public_ranking_explanation_rejects_unreproducible_scores(tmp_path):
    db = tmp_path / "search.db"
    _seed_post_corpus(db)
    hit = (
        PostSearchBackend(db)
        .search(
            PostSearchRequest.from_dict(_request_payload()),
            access_partitions=("public",),
        )
        .hits[0]
    )
    payload = hit.to_dict()
    payload["ranking"]["channels"]["lexical"]["rank"] = 999
    with pytest.raises(ContractValidationError, match="ranking"):
        PostSearchHit.from_dict(payload)


@pytest.mark.parametrize(
    "vector,state",
    [
        (None, "missing"),
        ([1.0], "incompatible"),
        ([0.0] * 256, "zero_vector"),
        ([float("nan")] * 256, "invalid"),
    ],
)
def test_semantic_gaps_degrade_to_truthful_lexical_results(tmp_path, vector, state):
    db = tmp_path / "search.db"
    _seed_post_corpus(db)
    add_vectors(db, overrides={"version-legacy-current": vector})
    backend = PostSearchBackend(db)
    result = backend.search(
        PostSearchRequest.from_dict(_request_payload()), access_partitions=("public",)
    )
    legacy = next(hit for hit in result.hits if hit.storage_family == "legacy")
    assert legacy.matching_channels == ("lexical",)
    assert result.coverage["semantic"]["families"]["legacy"][state] == 1
    temporal = next(hit for hit in result.hits if hit.storage_family == "temporal")
    assert temporal.matching_channels == ("lexical", "semantic")
    assert temporal.score == pytest.approx(
        sum(1 / (60 + value["rank"]) for value in temporal.ranking["channels"].values())
    )


def test_semantic_cursor_pins_vectors_and_public_payload_cannot_mutate_snapshot(
    tmp_path,
):
    db = tmp_path / "search.db"
    _seed_post_corpus(db)
    add_vectors(db)
    backend = PostSearchBackend(db)
    payload = _request_payload(page_size=1)
    first = backend.search(
        PostSearchRequest.from_dict(payload), access_partitions=("public",)
    )
    replay = PostSearchRequest.from_dict({**payload, "cursor": first.next_cursor})
    expected = backend.search(replay, access_partitions=("public",))
    first.coverage["semantic"]["families"]["legacy"]["available"] = 999
    first.hits[0].ranking["channels"].clear()
    with sqlite3.connect(db) as conn:
        conn.execute("UPDATE document_version_embeddings SET model='other-model'")
        conn.execute("UPDATE service_tick_query_entries SET embedding_json='[]'")
    retained = backend.search(replay, access_partitions=("public",))
    assert retained.hits == expected.hits and retained.coverage == expected.coverage
    fresh = backend.search(
        PostSearchRequest.from_dict(payload), access_partitions=("public",)
    )
    assert fresh.search_head_id != first.search_head_id
    assert fresh.coverage["semantic"]["families"]["legacy"]["incompatible"] == 1
    assert fresh.coverage["semantic"]["families"]["temporal"]["invalid"] == 1


def test_every_filter_excludes_vectors_before_scoring_and_candidate_admission(
    tmp_path, monkeypatch
):
    from lib import service_post_search_ranking

    db = tmp_path / "search.db"
    _seed_packet_two(db)
    add_vectors(db)
    # A selected legacy version with two vectors exceeds this fixture gate;
    # choosing only the temporal version must never admit those legacy inputs.
    with sqlite3.connect(db) as conn:
        conn.execute(
            "INSERT INTO document_version_embeddings SELECT chunk_id, 'other-model', dimensions, vector, vector_hash, created_at FROM document_version_embeddings"
        )
    monkeypatch.setattr(service_post_search_ranking, "MAX_VECTOR_ROWS", 1)
    filters = {
        "authors": ["bob"],
        "sources": ["x"],
        "topic_ids": ["7"],
        "collection_refs": ["temporal:target:x-service:target-1"],
        "published_after": "2026-09-07T00:00:00Z",
        "published_before": "2026-09-08T00:00:00Z",
        "observed_after": "2026-09-08T12:00:00Z",
        "observed_before": "2026-09-08T13:00:00Z",
    }
    result = PostSearchBackend(db).search(
        PostSearchRequest.from_dict(_request_payload(filters=filters)),
        access_partitions=("public",),
    )
    assert [hit.revision_id for hit in result.hits] == ["version-tick-new"]
    assert result.hits[0].matching_channels == ("lexical", "semantic")
    assert result.coverage["semantic"]["families"]["legacy"]["eligible"] == 0
    with pytest.raises(ContractValidationError, match="semantic_snapshot_too_large"):
        PostSearchBackend(db).search(
            PostSearchRequest.from_dict(_request_payload()),
            access_partitions=("public",),
        )


def test_current_collision_does_not_resurrect_stale_semantic_match(tmp_path):
    db = tmp_path / "search.db"
    _seed_post_corpus(db)
    add_vectors(db, query="orchard harvest")
    with sqlite3.connect(db) as conn:
        conn.execute("""INSERT INTO service_source_records VALUES
            ('replica', 'reddit-service', 'reddit', 'reddit-1', 'https://reddit.example/1',
             'public', 'new-replica', '2026-09-10T00:00:00Z')""")
        conn.execute("""INSERT INTO service_source_versions
            SELECT 'new-replica', 'replica', provider_attempt_id, 'new-content', title,
                   normalized_text, author, published_at, metadata_json,
                   '2026-09-10T00:00:00Z', access_partition_id, retention_class, created_at
            FROM service_source_versions WHERE version_id='version-tick-public'""")
    payload = _request_payload(query="orchard harvest", filters={"sources": ["reddit"]})
    current = PostSearchBackend(db).search(
        PostSearchRequest.from_dict(payload), access_partitions=("public",)
    )
    assert current.returned == 0
    revisions = PostSearchBackend(db).search(
        PostSearchRequest.from_dict({**payload, "revision_mode": "all"}),
        access_partitions=("public",),
    )
    assert [hit.revision_id for hit in revisions.hits] == ["version-legacy-current"]
    assert revisions.hits[0].evidence_ref.version_id == revisions.hits[0].revision_id


def test_hybrid_http_parity_and_indivisible_provenance_budget_error(tmp_path):
    db = tmp_path / "search.db"
    _seed_post_corpus(db)
    add_vectors(db)
    app = initialize_application(db, retriever=object())
    server = UnixServiceServer(tmp_path / "runtime/service.sock", app)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    request = PostSearchRequest.from_dict(_request_payload())
    before = db.read_bytes()
    try:
        client = ServiceClient(server.socket_path)
        assert client.search_posts(request).hits == app.search_posts(request).hits
        assert db.read_bytes() == before
        with sqlite3.connect(db) as conn:
            for index in range(150):
                conn.execute(
                    """INSERT INTO document_version_sightings
                    (version_id, acquisition_id, collection_spec_id, observed_at, access_partition_id)
                    VALUES ('version-legacy-current', ?, ?, '2026-09-10T00:00:00Z', 'public')""",
                    (f"acq-{index}", str(index) + "x" * 1000),
                )
        with pytest.raises(ServiceClientError, match="post_search_response_too_large"):
            client.search_posts(
                PostSearchRequest.from_dict(
                    _request_payload(filters={"sources": ["reddit"]})
                )
            )
        # This new mapping is search-only; malformed ordinary query remains
        # the established invalid-contract response.
        with pytest.raises(
            ServiceClientError, match="invalid_contract: request contract is invalid"
        ):
            client._request("POST", "/v1/query", {})
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
