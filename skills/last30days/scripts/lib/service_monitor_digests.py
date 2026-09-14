"""Immutable monitor projections and deterministic, bounded evidence digests."""

import json

from . import service_monitor_contracts as c
from .service_monitor_views import _digest, _json
from .service_monitors import MonitorKernelError


class MonitorRecords:
    """Hash-verified append-only projections scoped by kind and access partition."""

    def __init__(self, repository):
        self.repository = repository
        conn = repository._connect()
        try:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS service_monitor_records (
                    kind TEXT NOT NULL, record_id TEXT NOT NULL,
                    partition_id TEXT NOT NULL, owner_id TEXT NOT NULL,
                    payload_json TEXT NOT NULL, payload_sha256 TEXT NOT NULL,
                    PRIMARY KEY(kind, record_id)
                );
                CREATE TRIGGER IF NOT EXISTS monitor_records_no_update
                BEFORE UPDATE ON service_monitor_records BEGIN
                    SELECT RAISE(ABORT, 'monitor record is immutable'); END;
                CREATE TRIGGER IF NOT EXISTS monitor_records_no_delete
                BEFORE DELETE ON service_monitor_records BEGIN
                    SELECT RAISE(ABORT, 'monitor record is immutable'); END;
            """)
        finally:
            conn.close()

    def get(self, kind, key, partition):
        conn = self.repository._connect()
        try:
            row = conn.execute(
                "SELECT * FROM service_monitor_records WHERE kind=? AND record_id=? AND partition_id=?",
                (kind, key, partition),
            ).fetchone()
        finally:
            conn.close()
        if row is None:
            raise KeyError("monitor record unavailable")
        payload = json.loads(row["payload_json"])
        if _digest(payload) != row["payload_sha256"]:
            raise MonitorKernelError(
                c.MonitorErrorCode.IMMUTABLE_CONFLICT,
                "monitor record integrity failure",
            )
        return payload

    def put(self, kind, key, partition, owner, payload):
        conn = self.repository._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute(
                "SELECT * FROM service_monitor_records WHERE kind=? AND record_id=?",
                (kind, key),
            ).fetchone()
            if row:
                if (
                    row["payload_sha256"] != _digest(payload)
                    or row["partition_id"] != partition
                    or row["owner_id"] != owner
                ):
                    raise MonitorKernelError(
                        c.MonitorErrorCode.IMMUTABLE_CONFLICT,
                        "immutable monitor record conflict",
                    )
            else:
                conn.execute(
                    "INSERT INTO service_monitor_records VALUES (?, ?, ?, ?, ?, ?)",
                    (kind, key, partition, owner, _json(payload), _digest(payload)),
                )
            conn.commit()
        finally:
            conn.close()
        return self.get(kind, key, partition)


def baseline_refs(repository, records, baseline_id, partition):
    baseline = repository.get_baseline(baseline_id)
    wanted = {(item.evidence_id, item.version_id) for item in baseline.evidence}
    found = {}
    current = baseline_id
    # Upgrade old Packet 1/2 baselines lazily, without an unbounded history walk.
    for _ in range(100):
        if not current or not wanted - found.keys():
            break
        try:
            receipt = records.get("baseline_refs", current, partition)
            hits = receipt["evidence_refs"]
            next_id = None
        except KeyError:
            prior = repository.get_baseline(current)
            if prior.access_partition_id != partition:
                raise KeyError("baseline unavailable")
            hits = repository.capture_receipt(prior.snapshot_id)["evidence_refs"]
            conn = repository._connect()
            try:
                row = conn.execute(
                    "SELECT run_id FROM service_monitor_baselines WHERE baseline_id=?",
                    (current,),
                ).fetchone()
            finally:
                conn.close()
            next_id = repository.get_run(row[0]).prior_baseline_id
        for hit in hits:
            key = (hit["post_id"], hit["revision_id"])
            if key in wanted and key not in found:
                found[key] = hit
        current = next_id
    if wanted - found.keys():
        raise MonitorKernelError(
            c.MonitorErrorCode.VIEW_UNAVAILABLE,
            "bounded baseline evidence history unavailable",
        )
    return found


def prepare_digest(repository, records, run, spec, *, max_bytes=65_536):
    try:
        return records.get("digest", run.run_id, spec.access_partition_id)
    except KeyError:
        pass
    receipt = repository.capture_receipt(run.snapshot_id)
    snapshot = receipt["snapshot"]
    refs = {
        (hit["post_id"], hit["revision_id"]): hit for hit in receipt["evidence_refs"]
    }
    prior_head = None
    if run.prior_baseline_id:
        prior = repository.get_baseline(run.prior_baseline_id)
        prior_head = prior.evidence_head_id
        prior_refs = baseline_refs(
            repository, records, run.prior_baseline_id, spec.access_partition_id
        )
        # Current captures win for same-version provenance; keep every prior
        # version needed by revised/removed entries, including top-k absences.
        refs = {**prior_refs, **refs}
    candidate = repository.get_baseline(run.candidate_baseline_id)
    candidate_hits = [
        refs[(item.evidence_id, item.version_id)] for item in candidate.evidence
    ]
    baseline_receipt = {"evidence_refs": candidate_hits}
    if (
        len(candidate_hits) > 10_000
        or len(_json(baseline_receipt).encode()) > 2_097_152
    ):
        raise MonitorKernelError(
            c.MonitorErrorCode.VIEW_UNAVAILABLE, "baseline evidence exceeds bound"
        )
    records.put(
        "baseline_refs",
        candidate.baseline_id,
        spec.access_partition_id,
        spec.monitor_id,
        baseline_receipt,
    )
    comparison = run.comparison
    result = {
        "schema_version": 1,
        "digest_id": "digest-" + _digest([run.run_id, "deterministic_v1"])[:32],
        "run_id": run.run_id,
        "monitor_id": run.monitor_id,
        "access_partition_id": spec.access_partition_id,
        "renderer_version": "deterministic_v1",
        "comparator_version": comparison.comparator_version,
        "comparison_status": comparison.status.value,
        "prior_baseline_id": run.prior_baseline_id,
        "candidate_baseline_id": run.candidate_baseline_id,
        "prior_head_id": prior_head,
        "current_head_id": snapshot["evidence_head_id"],
        "knowledge_cutoff": snapshot["knowledge_cutoff"],
        "coverage_start": snapshot["coverage_start"],
        "coverage_end": snapshot["coverage_end"],
        "coverage": snapshot["coverage"],
        "coverage_scope": "bounded_cache_view_only",
        "prior_count": comparison.prior_count,
        "current_count": comparison.current_count,
        "counts": {kind.value: len(comparison.by_kind(kind)) for kind in c.ChangeKind},
        "omitted_count": len(comparison.changes),
        "entries": [],
    }
    for change in comparison.changes:
        links = []
        causes = set()
        for version in dict.fromkeys(
            (change.prior_version_id, change.current_version_id)
        ):
            if version is None:
                continue
            hit = refs.get((change.evidence_id, version))
            if hit is None or hit["access_partition_id"] != spec.access_partition_id:
                raise MonitorKernelError(
                    c.MonitorErrorCode.VIEW_UNAVAILABLE, "digest evidence unavailable"
                )
            links.append(hit["evidence_ref"])
            causes.update(hit["collection_refs"])
        entry = {
            **change.to_dict(),
            "evidence_refs": links,
            "collection_refs": sorted(causes),
        }
        result["entries"].append(entry)
        result["omitted_count"] -= 1
        if (
            len(result["entries"]) > spec.max_items
            or len(_json(result).encode()) > max_bytes
        ):
            result["entries"].pop()
            result["omitted_count"] += 1
            break
    if len(_json(result).encode()) > max_bytes:
        raise MonitorKernelError(
            c.MonitorErrorCode.VIEW_UNAVAILABLE, "digest exceeds byte bound"
        )
    return records.put(
        "digest", run.run_id, spec.access_partition_id, spec.monitor_id, result
    )
