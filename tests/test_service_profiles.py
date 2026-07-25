"""First-class profile history and reversible identity tests."""

import sqlite3
import json

import store
from lib.service_profiles import (
    IdentityResolution,
    ProfilePublisher,
    ProfileSection,
    ProfileSnapshot,
    deterministic_identity_candidates,
)


def _seed_evidence(db_path):
    store.init_db(db_path)
    conn = sqlite3.connect(db_path)
    metadata = json.dumps(
        {
            "surface_kind": "profile",
            "account_kind": "person",
            "handle": "ada",
            "declared_links": ["https://ada.example/"],
            "sections": [
                {
                    "section_kind": "about",
                    "ordinal": 0,
                    "text": "Analytical Engines",
                    "presence_state": "visible",
                    "visibility": "visible",
                }
            ],
        },
        separators=(",", ":"),
        sort_keys=True,
    )
    conn.execute(
        """INSERT INTO service_jobs
           (job_id, job_type, dedupe_key, state, query_request_id, attempts,
            max_attempts, budget_cents, spent_cents, lease_generation,
            created_at, updated_at)
           VALUES ('job-profile', 'refresh', 'profile', 'succeeded', 'q', 1,
                   2, 0, 0, 1, '2026-07-25T12:00:00Z',
                   '2026-07-25T12:00:00Z')"""
    )
    conn.execute(
        """INSERT INTO acquisitions
           (acquisition_id, job_id, profile_id, source, adapter,
            adapter_version, query_text, status, observed_at, fetched_at,
            retention_class, redaction_class, item_count)
           VALUES ('acq-profile', 'job-profile', 'linkedin-primary',
                   'linkedin', 'linkedin_profile_agent_browser', '1',
                   'https://www.linkedin.com/in/ada', 'succeeded',
                   '2026-07-25T12:00:00Z', '2026-07-25T12:00:01Z',
                   'durable', 'authenticated', 1)"""
    )
    conn.execute(
        """INSERT INTO access_partitions
           (partition_id, partition_kind, profile_id, created_at)
           VALUES ('profile:linkedin-primary', 'authenticated',
                   'linkedin-primary', '2026-07-25T12:00:01Z')"""
    )
    conn.execute(
        """INSERT INTO documents
           (document_id, acquisition_id, source, source_native_id,
            canonical_url, title, normalized_text, content_hash, fetched_at,
            retention_class, redaction_class, transformation_version,
            source_metadata_json, media_json, access_partition_id)
           VALUES ('doc-profile', 'acq-profile', 'linkedin', 'ada',
                   'https://www.linkedin.com/in/ada', 'Ada Lovelace',
                   'Ada Lovelace Analytical Engines', 'doc-hash',
                   '2026-07-25T12:00:01Z', 'durable', 'authenticated',
                   'profile-v1', ?, '[]', 'profile:linkedin-primary')""",
        (metadata,),
    )
    conn.execute(
        """INSERT INTO document_versions
           (version_id, document_id, acquisition_id, content_hash, title,
            normalized_text, source_metadata_json, media_json, observed_at,
            fetched_at, system_from, retention_class, redaction_class,
            access_partition_id, transformation_version)
           VALUES ('version-profile', 'doc-profile', 'acq-profile',
                   'version-hash', 'Ada Lovelace',
                   'Ada Lovelace Analytical Engines', ?, '[]',
                   '2026-07-25T12:00:00Z', '2026-07-25T12:00:01Z',
                   '2026-07-25T12:00:01Z', 'durable', 'authenticated',
                   'profile:linkedin-primary', 'profile-v1')""",
        (metadata,),
    )
    conn.execute(
        "UPDATE documents SET current_version_id = 'version-profile' "
        "WHERE document_id = 'doc-profile'"
    )
    conn.execute(
        """INSERT INTO document_version_chunks
           (chunk_id, version_id, document_id, ordinal, text, content_hash,
            chunker_version, access_partition_id)
           VALUES ('chunk-profile', 'version-profile', 'doc-profile', 0,
                   'Ada Lovelace Analytical Engines', 'chunk-hash',
                   'profile-v1', 'profile:linkedin-primary')"""
    )
    conn.execute(
        """INSERT INTO document_chunks
           (chunk_id, document_id, ordinal, text, content_hash,
            chunker_version, document_version_id)
           VALUES ('current-chunk-profile', 'doc-profile', 0,
                   'Ada Lovelace Analytical Engines', 'chunk-hash',
                   'profile-v1', 'version-profile')"""
    )
    conn.execute(
        """INSERT INTO evidence_spans
           (evidence_id, version_id, chunk_id, span_start, span_end,
            span_digest, redaction_class, access_partition_id, created_at)
           VALUES ('evidence-profile', 'version-profile', 'chunk-profile',
                   0, 31, 'span-hash', 'authenticated',
                   'profile:linkedin-primary', '2026-07-25T12:00:01Z')"""
    )
    conn.commit()
    conn.close()


def _snapshot(*, headline="Computing pioneer", about_presence="visible"):
    return ProfileSnapshot(
        source="linkedin",
        native_account_id="ada",
        canonical_url="https://www.linkedin.com/in/ada",
        account_kind="person",
        display_name="Ada Lovelace",
        headline=headline,
        about_text="Analytical Engines",
        acquisition_id="acq-profile",
        evidence_id="evidence-profile",
        observed_at="2026-07-25T12:00:00Z",
        access_partition_id="profile:linkedin-primary",
        retention_class="durable",
        redaction_class="authenticated",
        sections=(
            ProfileSection("headline", 0, headline, "visible", "evidence-profile"),
            ProfileSection(
                "about",
                0,
                "Analytical Engines" if about_presence == "visible" else "",
                about_presence,
                "evidence-profile" if about_presence == "visible" else None,
            ),
        ),
    )


def test_profile_publication_is_immutable_and_missing_sections_are_not_changes(tmp_path):
    db_path = tmp_path / "profiles.db"
    _seed_evidence(db_path)
    publisher = ProfilePublisher(db_path)

    first = publisher.publish(_snapshot())
    repeated = publisher.publish(_snapshot())
    missing = publisher.publish(_snapshot(about_presence="not_observed"))
    changed = publisher.publish(_snapshot(headline="Mathematician"))

    assert first.snapshot_id == repeated.snapshot_id
    assert missing.changes == ()
    assert [item.section_kind for item in changed.changes] == ["headline"]

    conn = sqlite3.connect(db_path)
    assert conn.execute("SELECT COUNT(*) FROM profile_snapshots").fetchone()[0] == 3
    assert conn.execute(
        "SELECT COUNT(*) FROM profile_snapshot_sightings"
    ).fetchone()[0] == 3
    assert conn.execute(
        "SELECT COUNT(*) FROM profile_snapshot_sections "
        "WHERE presence_state = 'not_observed'"
    ).fetchone()[0] == 1
    conn.close()


def test_raw_profile_publication_precedes_profile_projection(tmp_path):
    db_path = tmp_path / "raw-profile.db"
    _seed_evidence(db_path)

    publications = ProfilePublisher(db_path).publish_acquisition("acq-profile")

    assert len(publications) == 1
    conn = sqlite3.connect(db_path)
    section = conn.execute(
        """SELECT s.normalized_text, s.evidence_id, e.span_start, e.span_end
           FROM profile_snapshot_sections AS s
           JOIN evidence_spans AS e ON e.evidence_id = s.evidence_id"""
    ).fetchone()
    assert section == ("Analytical Engines", section[1], 13, 31)
    conn.close()


def test_identity_candidates_are_deterministic_and_resolution_is_terminal(tmp_path):
    db_path = tmp_path / "identity.db"
    _seed_evidence(db_path)
    publisher = ProfilePublisher(db_path)
    left = publisher.publish(_snapshot()).source_account_id

    right = publisher.ensure_source_account(
        source="x",
        native_account_id="ada-x",
        canonical_url="https://x.com/ada",
        account_kind="person",
        handle="ada",
        display_name="Ada Lovelace",
        declared_links=("https://www.linkedin.com/in/ada",),
        evidence_ids=("evidence-profile",),
        observed_at="2026-07-25T12:00:00Z",
        access_partition_id="profile:linkedin-primary",
    )
    candidates = deterministic_identity_candidates(db_path)
    assert len(candidates) == 1
    assert {candidates[0].left_account_id, candidates[0].right_account_id} == {
        left,
        right,
    }
    assert "declared_link" in candidates[0].reason_codes

    resolution = publisher.record_identity_resolution(
        IdentityResolution(
            candidate_id=candidates[0].candidate_id,
            outcome="ambiguous",
            confidence=0.45,
            evidence_ids=("evidence-profile",),
            rationale="Name and declared link agree, but evidence is shared.",
            resolver="app_intelligence",
            task_id="task-identity-1",
        )
    )
    assert resolution.outcome == "ambiguous"
    assert publisher.record_identity_resolution(resolution) == resolution


def test_same_entity_resolution_promotes_reversible_evidence_linked_assertions(tmp_path):
    db_path = tmp_path / "identity-promotion.db"
    _seed_evidence(db_path)
    publisher = ProfilePublisher(db_path)
    publisher.publish(_snapshot())
    publisher.ensure_source_account(
        source="x",
        native_account_id="ada-x",
        canonical_url="https://x.com/ada",
        account_kind="person",
        handle="ada",
        display_name="Ada Lovelace",
        declared_links=("https://www.linkedin.com/in/ada",),
        evidence_ids=("evidence-profile",),
        observed_at="2026-07-25T12:00:00Z",
        access_partition_id="profile:linkedin-primary",
    )
    candidate = deterministic_identity_candidates(db_path)[0]
    publisher.record_identity_resolution(
        IdentityResolution(
            candidate_id=candidate.candidate_id,
            outcome="same_entity",
            confidence=0.95,
            evidence_ids=("evidence-profile",),
            rationale="The declared link and account names agree.",
            resolver="operator_review",
        )
    )
    conn = sqlite3.connect(db_path)
    conn.execute(
        """INSERT INTO entities
           (entity_id, canonical_name, entity_type, created_at, updated_at)
           VALUES ('entity-ada', 'Ada Lovelace', 'person',
                   '2026-07-25T12:00:00Z', '2026-07-25T12:00:00Z')"""
    )
    conn.commit()
    conn.close()

    assertion_ids = publisher.promote_identity_assertions(
        candidate.candidate_id,
        entity_id="entity-ada",
        system_from="2026-07-25T12:00:01Z",
    )
    assert len(assertion_ids) == 2
    publisher.close_identity_assertion(
        assertion_ids[0], system_to="2026-07-26T00:00:00Z"
    )
    conn = sqlite3.connect(db_path)
    assert conn.execute(
        "SELECT COUNT(*) FROM identity_assertion_evidence"
    ).fetchone()[0] == 2
    assert conn.execute(
        "SELECT system_to FROM identity_assertions WHERE assertion_id = ?",
        (assertion_ids[0],),
    ).fetchone()[0] == "2026-07-26T00:00:00Z"
    conn.close()
