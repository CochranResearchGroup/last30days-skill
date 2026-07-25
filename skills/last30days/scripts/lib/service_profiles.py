"""Immutable profile history and conservative, reversible identity resolution."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from urllib.parse import urlsplit, urlunsplit

import store

from .service_temporal import sha256_json, stable_temporal_id


_PRESENCE = frozenset({"visible", "not_observed", "observed_absent"})
_VISIBILITY = frozenset({"visible", "restricted", "unknown"})
_OUTCOMES = frozenset(
    {"same_entity", "different_entity", "ambiguous", "insufficient_evidence"}
)


def _canonical_url(value: str) -> str:
    parsed = urlsplit(value.strip())
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("canonical_url must be an absolute HTTP URL")
    return urlunsplit(
        (
            parsed.scheme.casefold(),
            parsed.netloc.casefold(),
            parsed.path.rstrip("/") or "/",
            "",
            "",
        )
    )


def _normalized(value: str | None) -> str:
    return " ".join((value or "").casefold().split())


@dataclass(frozen=True)
class ProfileSection:
    section_kind: str
    ordinal: int
    normalized_text: str
    presence_state: str
    evidence_id: str | None
    visibility: str = "visible"

    def __post_init__(self) -> None:
        if not self.section_kind.strip() or self.ordinal < 0:
            raise ValueError("profile section identity is invalid")
        if self.presence_state not in _PRESENCE:
            raise ValueError("profile section presence_state is invalid")
        if self.visibility not in _VISIBILITY:
            raise ValueError("profile section visibility is invalid")
        if self.presence_state == "visible" and (
            not self.normalized_text.strip() or not self.evidence_id
        ):
            raise ValueError("visible profile sections require text and evidence")
        if self.presence_state != "visible" and self.evidence_id is not None:
            raise ValueError("unobserved profile sections cannot cite evidence")


@dataclass(frozen=True)
class ProfileSnapshot:
    source: str
    native_account_id: str
    canonical_url: str
    account_kind: str
    display_name: str | None
    headline: str | None
    about_text: str | None
    acquisition_id: str
    evidence_id: str
    observed_at: str
    access_partition_id: str
    retention_class: str
    redaction_class: str
    sections: tuple[ProfileSection, ...]
    handle: str | None = None
    valid_from: str | None = None
    declared_links: tuple[str, ...] = ()


@dataclass(frozen=True)
class ProfileChange:
    section_kind: str
    ordinal: int
    prior_text: str
    current_text: str
    prior_evidence_id: str
    current_evidence_id: str


@dataclass(frozen=True)
class ProfilePublication:
    source_account_id: str
    snapshot_id: str
    changes: tuple[ProfileChange, ...]


@dataclass(frozen=True)
class IdentityCandidate:
    candidate_id: str
    left_account_id: str
    right_account_id: str
    reason_codes: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    access_partition_id: str


@dataclass(frozen=True)
class IdentityResolution:
    candidate_id: str
    outcome: str
    confidence: float
    evidence_ids: tuple[str, ...]
    rationale: str
    resolver: str
    task_id: str | None = None


class ProfilePublisher:
    """Project exact profile evidence without mutating earlier snapshots."""

    def __init__(self, db_path: Path) -> None:
        self.db_path = Path(db_path)
        store.init_db(self.db_path)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=5)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("PRAGMA busy_timeout=5000")
        return conn

    def publish_acquisition(self, acquisition_id: str) -> tuple[ProfilePublication, ...]:
        """Project already-committed raw profile pages into profile authority."""
        conn = self._connect()
        try:
            rows = conn.execute(
                """SELECT d.source, d.source_native_id, d.canonical_url,
                          v.title, v.normalized_text, v.source_metadata_json,
                          v.observed_at, v.retention_class, v.redaction_class,
                          v.access_partition_id, v.version_id, c.chunk_id,
                          e.evidence_id
                   FROM documents AS d
                   JOIN document_versions AS v
                     ON v.version_id = d.current_version_id
                   JOIN document_version_chunks AS c
                     ON c.version_id = v.version_id AND c.ordinal = 0
                   JOIN evidence_spans AS e
                     ON e.version_id = v.version_id AND e.chunk_id = c.chunk_id
                    AND e.span_start = 0
                   WHERE v.acquisition_id = ?
                   ORDER BY d.document_id""",
                (acquisition_id,),
            ).fetchall()
            proposals: list[ProfileSnapshot] = []
            for row in rows:
                metadata = json.loads(row["source_metadata_json"])
                if metadata.get("surface_kind") != "profile":
                    continue
                sections: list[ProfileSection] = []
                for raw in metadata.get("sections", []):
                    presence = str(raw.get("presence_state") or "not_observed")
                    text = str(raw.get("text") or "").strip()
                    evidence_id = None
                    if presence == "visible" and text:
                        start = row["normalized_text"].find(text)
                        if start < 0:
                            raise ValueError("profile section is not closed to raw evidence")
                        end = start + len(text)
                        evidence_id = stable_temporal_id(
                            "evidence",
                            {
                                "version_id": row["version_id"],
                                "chunk_id": row["chunk_id"],
                                "span_start": start,
                                "span_end": end,
                                "span_digest": sha256_json(text),
                            },
                        )
                        conn.execute(
                            """INSERT OR IGNORE INTO evidence_spans
                               (evidence_id, version_id, chunk_id, span_start,
                                span_end, span_digest, redaction_class,
                                access_partition_id, created_at)
                               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                            (
                                evidence_id,
                                row["version_id"],
                                row["chunk_id"],
                                start,
                                end,
                                sha256_json(text),
                                row["redaction_class"],
                                row["access_partition_id"],
                                row["observed_at"],
                            ),
                        )
                    sections.append(
                        ProfileSection(
                            str(raw.get("section_kind") or ""),
                            int(raw.get("ordinal") or 0),
                            text,
                            presence,
                            evidence_id,
                            str(raw.get("visibility") or "unknown"),
                        )
                    )
                conn.commit()
                by_kind = {
                    item.section_kind: item.normalized_text
                    for item in sections
                    if item.presence_state == "visible"
                }
                proposals.append(
                    ProfileSnapshot(
                        source=row["source"],
                        native_account_id=row["source_native_id"],
                        canonical_url=row["canonical_url"],
                        account_kind=str(metadata.get("account_kind") or "unknown"),
                        display_name=row["title"],
                        headline=by_kind.get("headline"),
                        about_text=by_kind.get("about"),
                        acquisition_id=acquisition_id,
                        evidence_id=row["evidence_id"],
                        observed_at=row["observed_at"],
                        access_partition_id=row["access_partition_id"],
                        retention_class=row["retention_class"],
                        redaction_class=row["redaction_class"],
                        sections=tuple(sections),
                        handle=metadata.get("handle"),
                        declared_links=tuple(metadata.get("declared_links") or ()),
                    )
                )
        finally:
            conn.close()
        return tuple(self.publish(proposal) for proposal in proposals)

    @staticmethod
    def _assert_evidence(
        conn: sqlite3.Connection,
        evidence_ids: Iterable[str],
        partition_id: str,
    ) -> None:
        for evidence_id in sorted(set(evidence_ids)):
            row = conn.execute(
                """SELECT 1 FROM evidence_spans
                   WHERE evidence_id = ? AND access_partition_id = ?""",
                (evidence_id, partition_id),
            ).fetchone()
            if row is None:
                raise ValueError("profile evidence is missing or crosses partitions")

    def ensure_source_account(
        self,
        *,
        source: str,
        native_account_id: str,
        canonical_url: str,
        account_kind: str,
        handle: str | None,
        display_name: str | None,
        declared_links: tuple[str, ...],
        evidence_ids: tuple[str, ...],
        observed_at: str,
        access_partition_id: str,
        _conn: sqlite3.Connection | None = None,
    ) -> str:
        account_id = stable_temporal_id(
            "account",
            {"source": source.casefold(), "native_account_id": native_account_id},
        )
        canonical = _canonical_url(canonical_url)
        links = tuple(sorted({_canonical_url(item) for item in declared_links}))
        owned = _conn is None
        conn = _conn or self._connect()
        try:
            self._assert_evidence(conn, evidence_ids, access_partition_id)
            conn.execute(
                """INSERT INTO source_accounts
                   (source_account_id, source, native_account_id, handle,
                    canonical_url, account_kind, access_partition_id,
                    first_observed_at, last_observed_at, display_name,
                    declared_links_json, evidence_ids_json)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                   ON CONFLICT(source_account_id) DO UPDATE SET
                     handle = COALESCE(excluded.handle, source_accounts.handle),
                     canonical_url = COALESCE(
                         excluded.canonical_url, source_accounts.canonical_url
                     ),
                     last_observed_at = MAX(
                         excluded.last_observed_at,
                         source_accounts.last_observed_at
                     ),
                     display_name = COALESCE(
                         excluded.display_name, source_accounts.display_name
                     ),
                     declared_links_json = excluded.declared_links_json,
                     evidence_ids_json = excluded.evidence_ids_json""",
                (
                    account_id,
                    source.casefold(),
                    native_account_id,
                    handle,
                    canonical,
                    account_kind,
                    access_partition_id,
                    observed_at,
                    observed_at,
                    display_name,
                    json.dumps(links, separators=(",", ":")),
                    json.dumps(sorted(set(evidence_ids)), separators=(",", ":")),
                ),
            )
            if owned:
                conn.commit()
            return account_id
        finally:
            if owned:
                conn.close()

    def publish(self, proposal: ProfileSnapshot) -> ProfilePublication:
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            evidence_ids = [proposal.evidence_id] + [
                section.evidence_id
                for section in proposal.sections
                if section.evidence_id is not None
            ]
            self._assert_evidence(
                conn, evidence_ids, proposal.access_partition_id
            )
            acquisition = conn.execute(
                """SELECT 1 FROM acquisitions
                   WHERE acquisition_id = ? AND source = ?""",
                (proposal.acquisition_id, proposal.source),
            ).fetchone()
            if acquisition is None:
                raise ValueError("profile acquisition does not match source")
            account_id = self.ensure_source_account(
                source=proposal.source,
                native_account_id=proposal.native_account_id,
                canonical_url=proposal.canonical_url,
                account_kind=proposal.account_kind,
                handle=proposal.handle,
                display_name=proposal.display_name,
                declared_links=proposal.declared_links,
                evidence_ids=(proposal.evidence_id,),
                observed_at=proposal.observed_at,
                access_partition_id=proposal.access_partition_id,
                _conn=conn,
            )
            content = {
                "display_name": proposal.display_name,
                "headline": proposal.headline,
                "about_text": proposal.about_text,
                "sections": [
                    {
                        "kind": item.section_kind,
                        "ordinal": item.ordinal,
                        "text": item.normalized_text,
                        "presence": item.presence_state,
                        "visibility": item.visibility,
                    }
                    for item in proposal.sections
                ],
            }
            content_hash = sha256_json(content)
            snapshot_id = stable_temporal_id(
                "profile_snapshot",
                {"source_account_id": account_id, "content_hash": content_hash},
            )
            prior = conn.execute(
                """SELECT snapshot_id FROM profile_snapshots
                   WHERE source_account_id = ?
                   ORDER BY system_from DESC, rowid DESC LIMIT 1""",
                (account_id,),
            ).fetchone()
            conn.execute(
                """INSERT OR IGNORE INTO profile_snapshots
                   (snapshot_id, source_account_id, acquisition_id, content_hash,
                    display_name, headline, about_text, metadata_json,
                    observed_at, valid_from, valid_to, system_from, system_to,
                    access_partition_id)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, ?, NULL, ?)""",
                (
                    snapshot_id,
                    account_id,
                    proposal.acquisition_id,
                    content_hash,
                    proposal.display_name,
                    proposal.headline,
                    proposal.about_text,
                    json.dumps(
                        {
                            "canonical_url": _canonical_url(proposal.canonical_url),
                            "evidence_id": proposal.evidence_id,
                        },
                        sort_keys=True,
                        separators=(",", ":"),
                    ),
                    proposal.observed_at,
                    proposal.valid_from,
                    proposal.observed_at,
                    proposal.access_partition_id,
                ),
            )
            for item in proposal.sections:
                section_id = stable_temporal_id(
                    "profile_section",
                    {
                        "snapshot_id": snapshot_id,
                        "section_kind": item.section_kind,
                        "ordinal": item.ordinal,
                    },
                )
                conn.execute(
                    """INSERT OR IGNORE INTO profile_snapshot_sections
                       (section_id, snapshot_id, section_kind, ordinal,
                        normalized_text, content_hash, access_partition_id,
                        evidence_id, visibility, presence_state,
                        redaction_class, retention_class)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        section_id,
                        snapshot_id,
                        item.section_kind,
                        item.ordinal,
                        item.normalized_text,
                        sha256_json(item.normalized_text),
                        proposal.access_partition_id,
                        item.evidence_id,
                        item.visibility,
                        item.presence_state,
                        proposal.redaction_class,
                        proposal.retention_class,
                    ),
                )
            conn.execute(
                """INSERT OR IGNORE INTO profile_snapshot_sightings
                   (snapshot_id, acquisition_id, observed_at, access_partition_id)
                   VALUES (?, ?, ?, ?)""",
                (
                    snapshot_id,
                    proposal.acquisition_id,
                    proposal.observed_at,
                    proposal.access_partition_id,
                ),
            )
            changes = self._changes(conn, prior["snapshot_id"] if prior else None, snapshot_id)
            conn.commit()
            return ProfilePublication(account_id, snapshot_id, changes)
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    @staticmethod
    def _changes(
        conn: sqlite3.Connection, prior_id: str | None, current_id: str
    ) -> tuple[ProfileChange, ...]:
        if prior_id is None or prior_id == current_id:
            return ()
        rows = conn.execute(
            """SELECT p.section_kind, p.ordinal, p.normalized_text AS prior_text,
                      c.normalized_text AS current_text,
                      p.evidence_id AS prior_evidence_id,
                      c.evidence_id AS current_evidence_id
               FROM profile_snapshot_sections AS p
               JOIN profile_snapshot_sections AS c
                 ON c.section_kind = p.section_kind AND c.ordinal = p.ordinal
               WHERE p.snapshot_id = ? AND c.snapshot_id = ?
                 AND p.presence_state = 'visible'
                 AND c.presence_state = 'visible'
                 AND p.visibility = 'visible' AND c.visibility = 'visible'
                 AND p.content_hash <> c.content_hash
               ORDER BY p.section_kind, p.ordinal""",
            (prior_id, current_id),
        ).fetchall()
        return tuple(ProfileChange(**dict(row)) for row in rows)

    def record_identity_resolution(
        self, resolution: IdentityResolution
    ) -> IdentityResolution:
        if resolution.outcome not in _OUTCOMES:
            raise ValueError("identity resolution outcome is invalid")
        if not 0 <= resolution.confidence <= 1 or not resolution.rationale.strip():
            raise ValueError("identity resolution confidence or rationale is invalid")
        conn = self._connect()
        try:
            candidate = conn.execute(
                "SELECT * FROM identity_candidates WHERE candidate_id = ?",
                (resolution.candidate_id,),
            ).fetchone()
            if candidate is None:
                raise ValueError("identity candidate does not exist")
            self._assert_evidence(
                conn, resolution.evidence_ids, candidate["access_partition_id"]
            )
            encoded = json.dumps(
                sorted(set(resolution.evidence_ids)), separators=(",", ":")
            )
            existing = conn.execute(
                """SELECT * FROM identity_resolution_outcomes
                   WHERE candidate_id = ?""",
                (resolution.candidate_id,),
            ).fetchone()
            values = (
                resolution.outcome,
                resolution.confidence,
                encoded,
                resolution.rationale,
                resolution.resolver,
                resolution.task_id,
            )
            if existing is not None:
                observed = tuple(existing[key] for key in (
                    "outcome", "confidence", "evidence_ids_json", "rationale",
                    "resolver", "task_id"
                ))
                if observed != values:
                    raise ValueError("identity resolution is terminal and immutable")
                return resolution
            conn.execute(
                """INSERT INTO identity_resolution_outcomes
                   (candidate_id, outcome, confidence, evidence_ids_json,
                    rationale, resolver, task_id, resolved_at,
                    access_partition_id)
                   VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'), ?)""",
                (resolution.candidate_id, *values, candidate["access_partition_id"]),
            )
            conn.execute(
                "UPDATE identity_candidates SET state = 'resolved' "
                "WHERE candidate_id = ?",
                (resolution.candidate_id,),
            )
            conn.commit()
            return resolution
        finally:
            conn.close()


def deterministic_identity_candidates(db_path: Path) -> tuple[IdentityCandidate, ...]:
    """Persist bounded candidates from declared, deterministic account signals."""
    store.init_db(db_path)
    conn = sqlite3.connect(str(db_path), timeout=5)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            "SELECT * FROM source_accounts ORDER BY source_account_id"
        ).fetchall()
        candidates: list[IdentityCandidate] = []
        for index, left in enumerate(rows):
            for right in rows[index + 1 :]:
                if (
                    left["source"] == right["source"]
                    or left["access_partition_id"] != right["access_partition_id"]
                ):
                    continue
                reasons: list[str] = []
                left_links = set(json.loads(left["declared_links_json"]))
                right_links = set(json.loads(right["declared_links_json"]))
                if left["canonical_url"] in right_links or right["canonical_url"] in left_links:
                    reasons.append("declared_link")
                if _normalized(left["display_name"]) and _normalized(
                    left["display_name"]
                ) == _normalized(right["display_name"]):
                    reasons.append("normalized_name")
                if _normalized(left["handle"]) and _normalized(left["handle"]) == _normalized(
                    right["handle"]
                ):
                    reasons.append("normalized_handle")
                if not reasons:
                    continue
                evidence_ids = tuple(
                    sorted(
                        set(json.loads(left["evidence_ids_json"]))
                        | set(json.loads(right["evidence_ids_json"]))
                    )
                )
                candidate_id = stable_temporal_id(
                    "identity_candidate",
                    {
                        "left": left["source_account_id"],
                        "right": right["source_account_id"],
                        "reasons": sorted(reasons),
                    },
                )
                candidate = IdentityCandidate(
                    candidate_id,
                    left["source_account_id"],
                    right["source_account_id"],
                    tuple(sorted(reasons)),
                    evidence_ids,
                    left["access_partition_id"],
                )
                conn.execute(
                    """INSERT OR IGNORE INTO identity_candidates
                       (candidate_id, left_account_id, right_account_id,
                        reason_codes_json, evidence_ids_json, access_partition_id,
                        created_at)
                       VALUES (?, ?, ?, ?, ?, ?, datetime('now'))""",
                    (
                        candidate.candidate_id,
                        candidate.left_account_id,
                        candidate.right_account_id,
                        json.dumps(candidate.reason_codes, separators=(",", ":")),
                        json.dumps(candidate.evidence_ids, separators=(",", ":")),
                        candidate.access_partition_id,
                    ),
                )
                candidates.append(candidate)
        conn.commit()
        return tuple(candidates)
    finally:
        conn.close()
