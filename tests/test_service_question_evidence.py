"""Provider-free evidence tracing for durable agent questions."""

import json
import sqlite3

import pytest

from lib import service_question_contracts as question_contracts
from lib.service_post_search import PostSearchBackend
from lib.service_question_evidence import QuestionEvidenceResolver
from lib.service_questions import QuestionService
from lib.service_retrieval import HybridRetriever


def _seed_corpus(db_path):
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
               'https://reddit.example/current', 'Legacy post', 'alice',
               'reliable browser current', 'sha256:legacy-current',
               '2026-09-05T12:00:00Z', '2026-09-05T12:01:00Z', 'cache',
               'public', 'fixture-v1', 'version-legacy-current', 'public',
               '{}', '[]'
           )"""
    )
    for version_id, text, content_hash, system_from in (
        (
            "version-legacy-old",
            "reliable browser historical",
            "sha256:legacy-old",
            "2026-09-04T12:01:00Z",
        ),
        (
            "version-legacy-current",
            "reliable browser current",
            "sha256:legacy-current",
            "2026-09-05T12:01:00Z",
        ),
    ):
        conn.execute(
            """INSERT INTO document_versions (
                   version_id, document_id, acquisition_id, content_hash, title,
                   author, normalized_text, source_metadata_json, media_json,
                   published_at, valid_from, valid_to, observed_at, fetched_at,
                   system_from, system_to, retention_class, redaction_class,
                   access_partition_id, transformation_version
               ) VALUES (?, 'doc-legacy', 'acq-fixture', ?, 'Legacy post',
                         'alice', ?, '{"kind":"legacy"}', '[]',
                         '2026-09-05T12:00:00Z', '2026-09-05T12:00:00Z', NULL,
                         '2026-09-05T12:01:00Z', '2026-09-05T12:02:00Z', ?,
                         NULL, 'cache', 'public', 'public', 'fixture-v1')""",
            (version_id, content_hash, text, system_from),
        )
    for record_id, version_id, partition, text, url in (
        (
            "record-temporal-public",
            "version-temporal-public",
            "public",
            "reliable browser temporal",
            "https://x.example/current",
        ),
        (
            "record-temporal-private",
            "version-temporal-private",
            "profile:other",
            "reliable browser private",
            "https://x.example/private",
        ),
    ):
        conn.execute(
            """INSERT INTO service_source_records (
                   record_id, service_id, source, source_native_id, canonical_url,
                   access_partition_id, current_version_id, created_at
               ) VALUES (?, 'x-service', 'x', ?, ?, ?, ?,
                         '2026-09-07T12:01:00Z')""",
            (record_id, record_id, url, partition, version_id),
        )
        conn.execute(
            """INSERT INTO service_source_versions (
                   version_id, record_id, provider_attempt_id, content_hash,
                   title, normalized_text, author, published_at, metadata_json,
                   observed_at, access_partition_id, retention_class, created_at
               ) VALUES (?, ?, 'attempt-fixture', ?, 'Temporal post', ?, 'bob',
                         '2026-09-07T12:00:00Z', '{"kind":"temporal"}',
                         '2026-09-07T12:01:00Z', ?, 'cache',
                         '2026-09-07T12:02:00Z')""",
            (version_id, record_id, f"sha256:{version_id}", text, partition),
        )
    conn.execute(
        """INSERT INTO document_version_sightings (
               version_id, acquisition_id, topic_id, collection_spec_id,
               collection_run_id, observed_at, access_partition_id
           ) VALUES ('version-legacy-old', 'acq-fixture', 42, 'collection:legacy',
                     'run-legacy', '2026-09-05T12:01:00Z', 'public')"""
    )
    conn.execute(
        """INSERT INTO service_tick_lanes (
               lane_id, tick_id, service_id, target_id, access_partition_id,
               service_config_json, target_config_json, lane_digest, state,
               created_at, updated_at
           ) VALUES ('lane-fixture', 'tick-fixture', 'x-service', 'target-fixture',
                     'public', '{}', ?,
                     'lane-digest', 'success', '2026-09-07T12:01:00Z',
                     '2026-09-07T12:02:00Z')""",
        (
            json.dumps(
                {
                    "collection_refs": ["collection:temporal"],
                    "topic_ids": ["topic-7"],
                }
            ),
        ),
    )
    conn.execute(
        """INSERT INTO service_source_sightings (
               version_id, tick_id, lane_id, provider_attempt_id, observed_at
           ) VALUES ('version-temporal-public', 'tick-fixture', 'lane-fixture',
                     'attempt-fixture', '2026-09-07T12:01:00Z')"""
    )
    conn.commit()
    conn.close()


def _question_request(**overrides):
    payload = {
        "schema_version": 1,
        "request_id": "question-real-backend-001",
        "profile_id": "public",
        "question": "What changed in reliable browser behavior?",
        "filters": {"sources": ["reddit", "x"]},
        "temporal": {
            "as_of": None,
            "during_from": None,
            "during_to": None,
            "known_as_of": None,
        },
        "answer_mode": "synthesized",
        "model_fallback": "none",
        "limits": {
            "evidence_limit": 10,
            "max_evidence_bytes": 65536,
            "max_answer_characters": 4096,
            "max_statements": 8,
            "wait_ms": 0,
            "max_evidence_age_seconds": None,
            "max_attempts": 2,
        },
    }
    payload.update(overrides)
    return question_contracts.QuestionRequestV1.from_dict(payload)


def test_question_service_freezes_real_federated_search_before_worker(tmp_path):
    db_path = tmp_path / "question-evidence.db"
    _seed_corpus(db_path)
    service = QuestionService(db_path, PostSearchBackend(db_path))

    status = service.submit(_question_request(), access_partitions=("public",))

    assert status.state == "pending"
    conn = sqlite3.connect(db_path)
    retrieval = json.loads(
        conn.execute(
            "SELECT retrieval_json FROM service_question_retrievals"
        ).fetchone()[0]
    )
    conn.close()
    assert retrieval["cache_only"] is True
    assert retrieval["acquisition_performed"] is False
    assert retrieval["search_head_id"].startswith("search-head-")
    assert set(retrieval["coverage"]["search"]["component_heads"]) == {
        "legacy",
        "temporal",
    }
    assert [item["storage_family"] for item in retrieval["evidence"]] == [
        "legacy",
        "temporal",
    ]
    assert {item["version_id"] for item in retrieval["evidence"]} == {
        "version-legacy-current",
        "version-temporal-public",
    }
    assert all(
        item["access_partition_id"] == "public" for item in retrieval["evidence"]
    )
    assert retrieval["coverage"]["byte_truncated"] is False
    assert retrieval["search_receipt"] == {
        "search_head_id": retrieval["search_head_id"],
        "component_heads": retrieval["coverage"]["search"]["component_heads"],
        "ordered_evidence_ids": [
            item["evidence_id"] for item in retrieval["evidence"]
        ],
        "returned": 2,
        "truncated": False,
        "next_cursor": None,
        "coverage": retrieval["coverage"]["search"],
    }
    assert retrieval["selection_receipt"] == {
        "evidence_limit": 10,
        "max_evidence_bytes": 65536,
        "selected_count": 2,
        "selected_bytes": len(
            question_contracts.canonical_json(retrieval["evidence"]).encode()
        ),
        "byte_truncated": False,
    }


def _citation(
    evidence_id=None,
    *,
    storage_family="legacy",
    version_id="version-legacy-current",
    content_hash="sha256:legacy-current",
    source_url="https://reddit.example/current",
    access_partition_id="public",
):
    core = {
        "storage_family": storage_family,
        "version_id": version_id,
        "content_hash": content_hash,
        "source_url": source_url,
        "access_partition_id": access_partition_id,
    }
    return {
        "evidence_id": evidence_id
        or question_contracts.stable_id("question-evidence", core),
        **core,
    }


def _read_request(**overrides):
    payload = {
        "schema_version": 1,
        "request_id": "evidence-read-001",
        "profile_id": "public",
        "refs": [_citation()],
        "max_response_bytes": 65536,
    }
    payload.update(overrides)
    return payload


def test_evidence_read_contracts_are_strict_partition_closed_and_deterministic():
    payload = _read_request()
    request = question_contracts.EvidenceReadRequestV1.from_dict(payload)

    assert request.to_dict() == payload
    assert question_contracts.EvidenceReadRequestV1.from_dict(
        request.to_dict()
    ) == request
    assert question_contracts.canonical_json(request.to_dict()) == (
        question_contracts.canonical_json(request.to_dict())
    )

    invalid_payloads = [
        {**payload, "unknown": True},
        _read_request(refs=[]),
        _read_request(refs=[_citation(str(index)) for index in range(21)]),
        _read_request(refs=[_citation(), _citation()]),
        _read_request(
            refs=[_citation(), _citation("different-id-for-the-same-ref")]
        ),
        _read_request(
            refs=[
                _citation(
                    (f"evidence-{index}-" + ("x" * 100)),
                    version_id=f"version-{index}",
                    content_hash=f"sha256:{index}",
                )
                for index in range(20)
            ],
            max_response_bytes=512,
        ),
        _read_request(max_response_bytes=131073),
        _read_request(refs=[{**_citation(), "storage_family": "current"}]),
        _read_request(
            profile_id="alpha",
            refs=[_citation(access_partition_id="profile:beta")],
        ),
    ]
    for invalid in invalid_payloads:
        with pytest.raises(question_contracts.QuestionContractError):
            question_contracts.EvidenceReadRequestV1.from_dict(invalid)

    unavailable = question_contracts.EvidenceReadItemV1.from_dict(
        {"ref": _citation(), "status": "unavailable", "evidence": None}
    )
    response_payload = {
        "schema_version": 1,
        "request_id": request.request_id,
        "items": [unavailable.to_dict()],
        "omitted_refs": [],
        "truncated": False,
    }
    response = question_contracts.EvidenceReadResponseV1.from_dict(
        {
            **response_payload,
            "response_bytes": _serialized_response_size(response_payload),
        }
    )
    assert question_contracts.EvidenceReadResponseV1.from_dict(
        response.to_dict()
    ) == response

    with pytest.raises(question_contracts.QuestionContractError):
        question_contracts.EvidenceReadItemV1.from_dict(
            {"ref": _citation(), "status": "available", "evidence": None}
        )
    with pytest.raises(question_contracts.QuestionContractError):
        question_contracts.EvidenceReadResponseV1.from_dict(
            {**response.to_dict(), "extra": "rejected"}
        )
    with pytest.raises(question_contracts.QuestionContractError):
        question_contracts.EvidenceReadResponseV1.from_dict(
            {**response.to_dict(), "response_bytes": response.response_bytes + 1}
        )


def test_evidence_resolver_reads_exact_legacy_and_temporal_versions_in_order(tmp_path):
    db_path = tmp_path / "question-evidence.db"
    _seed_corpus(db_path)
    request = question_contracts.EvidenceReadRequestV1.from_dict(
        _read_request(
            refs=[
                _citation(
                    storage_family="legacy",
                    version_id="version-legacy-old",
                    content_hash="sha256:legacy-old",
                ),
                _citation(
                    storage_family="temporal",
                    version_id="version-temporal-public",
                    content_hash="sha256:version-temporal-public",
                    source_url="https://x.example/current",
                ),
            ]
        )
    )

    response = QuestionEvidenceResolver(db_path).read(
        request, access_partitions=("public",)
    )

    assert response.truncated is False
    assert response.omitted_refs == ()
    assert [item.ref.evidence_id for item in response.items] == [
        ref.evidence_id for ref in request.refs
    ]
    assert [item.status for item in response.items] == ["available", "available"]
    legacy = response.items[0].evidence
    temporal = response.items[1].evidence
    assert legacy is not None and temporal is not None
    assert legacy["version_id"] == "version-legacy-old"
    assert legacy["text"] == "reliable browser historical"
    assert legacy["canonical_url"] == "https://reddit.example/current"
    assert legacy["access_partition_id"] == "public"
    assert legacy["metadata"] == {"kind": "legacy"}
    assert legacy["collection_refs"] == ["collection:legacy"]
    assert legacy["topic_ids"] == ["42"]
    assert legacy["provenance"]["document_id"] == "doc-legacy"
    assert temporal["version_id"] == "version-temporal-public"
    assert temporal["text"] == "reliable browser temporal"
    assert temporal["metadata"] == {"kind": "temporal"}
    assert temporal["collection_refs"] == ["collection:temporal"]
    assert temporal["topic_ids"] == ["topic-7"]
    assert temporal["provenance"]["record_id"] == "record-temporal-public"
    assert response.response_bytes == len(
        question_contracts.canonical_json(response.to_dict()).encode()
    )
    assert response.response_bytes <= request.max_response_bytes
    with pytest.raises(question_contracts.QuestionContractError):
        question_contracts.EvidenceReadItemV1.from_dict(
            {
                **response.items[0].to_dict(),
                "evidence": {**legacy, "unknown": True},
            }
        )


def test_evidence_resolver_collapses_all_ref_failures_to_unavailable(tmp_path):
    db_path = tmp_path / "question-evidence.db"
    _seed_corpus(db_path)
    conn = sqlite3.connect(db_path)
    conn.execute(
        """UPDATE service_source_records
              SET canonical_url = 'https://x.example/changed'
            WHERE record_id = 'record-temporal-public'"""
    )
    conn.execute(
        """INSERT INTO document_versions (
               version_id, document_id, acquisition_id, content_hash, title,
               author, normalized_text, source_metadata_json, media_json,
               published_at, valid_from, valid_to, observed_at, fetched_at,
               system_from, system_to, retention_class, redaction_class,
               access_partition_id, transformation_version
           ) VALUES ('version-legacy-oversized', 'doc-legacy', 'acq-fixture',
                     'sha256:legacy-oversized', ?, 'alice', 'bounded text', '{}',
                     '[]', '2026-09-05T12:00:00Z', NULL, NULL,
                     '2026-09-05T12:01:00Z', '2026-09-05T12:02:00Z',
                     '2026-09-05T12:02:00Z', NULL, 'cache', 'public', 'public',
                     'fixture-v1')""",
        ("x" * 4097,),
    )
    conn.commit()
    conn.close()
    refs = [
        _citation(
            version_id="version-missing",
            content_hash="sha256:missing",
        ),
        _citation(content_hash="sha256:changed"),
        _citation(source_url="https://reddit.example/changed"),
        _citation(
            storage_family="temporal",
            version_id="version-legacy-current",
            content_hash="sha256:legacy-current",
        ),
        _citation(
            storage_family="temporal",
            version_id="version-temporal-public",
            content_hash="sha256:version-temporal-public",
            source_url="https://x.example/current",
        ),
        _citation(
            storage_family="temporal",
            version_id="version-temporal-private",
            content_hash="sha256:version-temporal-private",
            source_url="https://x.example/private",
            access_partition_id="profile:other",
        ),
        _citation(
            storage_family="temporal",
            version_id="version-temporal-private",
            content_hash="sha256:version-temporal-private",
            source_url="https://x.example/private",
            access_partition_id="public",
        ),
        _citation(
            version_id="version-legacy-oversized",
            content_hash="sha256:legacy-oversized",
        ),
    ]
    request = question_contracts.EvidenceReadRequestV1.from_dict(
        _read_request(profile_id="other", refs=refs)
    )

    response = QuestionEvidenceResolver(db_path).read(
        request, access_partitions=("public",)
    )

    assert response.truncated is False
    assert [item.status for item in response.items] == ["unavailable"] * len(refs)
    assert all(item.evidence is None for item in response.items)
    assert [item.ref.evidence_id for item in response.items] == [
        ref.evidence_id for ref in request.refs
    ]


def test_evidence_resolver_rejects_parent_version_partition_mismatches(tmp_path):
    db_path = tmp_path / "question-evidence.db"
    _seed_corpus(db_path)
    conn = sqlite3.connect(db_path)
    conn.execute(
        "UPDATE documents SET access_partition_id = 'profile:other' "
        "WHERE document_id = 'doc-legacy'"
    )
    conn.execute(
        "UPDATE service_source_records SET access_partition_id = 'profile:other' "
        "WHERE record_id = 'record-temporal-public'"
    )
    conn.commit()
    conn.close()
    refs = [
        _citation(),
        _citation(
            storage_family="temporal",
            version_id="version-temporal-public",
            content_hash="sha256:version-temporal-public",
            source_url="https://x.example/current",
        ),
    ]
    request = question_contracts.EvidenceReadRequestV1.from_dict(
        _read_request(refs=refs)
    )

    response = QuestionEvidenceResolver(db_path).read(
        request, access_partitions=("public",)
    )

    assert [item.status for item in response.items] == ["unavailable", "unavailable"]
    assert all(item.evidence is None for item in response.items)


def _serialized_response_size(payload):
    measured = 2
    while True:
        updated = len(
            question_contracts.canonical_json(
                {**payload, "response_bytes": measured}
            ).encode()
        )
        if updated == measured:
            return updated
        measured = updated


def test_evidence_response_budget_truncates_only_at_item_boundaries(tmp_path):
    db_path = tmp_path / "question-evidence.db"
    _seed_corpus(db_path)
    refs = [
        _citation(
            version_id="version-legacy-old", content_hash="sha256:legacy-old"
        ),
        _citation(),
        _citation(
            storage_family="temporal",
            version_id="version-temporal-public",
            content_hash="sha256:version-temporal-public",
            source_url="https://x.example/current",
        ),
    ]
    resolver = QuestionEvidenceResolver(db_path)
    full = resolver.read(
        question_contracts.EvidenceReadRequestV1.from_dict(
            _read_request(refs=refs)
        ),
        access_partitions=("public",),
    )
    one_item_payload = {
        "schema_version": 1,
        "request_id": "evidence-read-001",
        "items": [full.items[0].to_dict()],
        "omitted_refs": [ref["evidence_id"] for ref in refs[1:]],
        "truncated": True,
    }
    one_item_budget = _serialized_response_size(one_item_payload)

    response = resolver.read(
        question_contracts.EvidenceReadRequestV1.from_dict(
            _read_request(refs=refs, max_response_bytes=one_item_budget)
        ),
        access_partitions=("public",),
    )

    assert len(response.items) == 1
    assert response.items[0].ref.evidence_id == refs[0]["evidence_id"]
    assert response.omitted_refs == tuple(ref["evidence_id"] for ref in refs[1:])
    assert response.truncated is True
    assert response.response_bytes == one_item_budget
