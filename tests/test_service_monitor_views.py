"""Saved query composition through durable, provider-free interfaces."""

import copy
from datetime import datetime, timezone
from dataclasses import replace
import json
import sqlite3

import pytest

from lib import service_monitor_contracts as contracts
from lib.service_monitor_views import SavedQueryRepository, SavedQueryViewProvider
from lib.service_monitors import MonitorKernelError, MonitorKernel
from lib.service_post_search import PostSearchBackend
from lib import service_contracts as search_contracts
from tests.test_service_post_search import _seed_post_corpus


def _definition(version=1, **search_changes):
    return contracts.SavedQueryDefinitionV1.from_dict({
        "schema_version": 1,
        "saved_query_id": "query-browser",
        "version": version,
        "access_partition_id": "public",
        "search": {
            "profile_id": "default", "query": None,
            "filters": {"sources": ["reddit"]},
            "page_size": 1, "sort": "observed_desc", "revision_mode": "current",
            **search_changes,
        },
    })


def test_saved_query_versions_are_immutable_partition_bound_and_restart_safe(tmp_path):
    repository = SavedQueryRepository(tmp_path / "monitors.db")
    repository.initialize()
    definition = _definition()
    repository.save(definition)
    repository.save(definition)
    reloaded = SavedQueryRepository(repository.db_path).get(definition.view_ref, "public")
    assert reloaded == definition
    exported = reloaded.to_dict()
    exported["search"]["filters"]["sources"].append("x")
    assert reloaded.to_dict() == definition.to_dict()
    with pytest.raises(MonitorKernelError) as conflict:
        repository.save(_definition(query="changed"))
    assert conflict.value.code is contracts.MonitorErrorCode.IMMUTABLE_CONFLICT
    with pytest.raises(MonitorKernelError):
        repository.save(_definition(3))
    repository.save(_definition(2, query="browser"))
    assert repository.get(definition.view_ref, "public") == definition
    with pytest.raises(MonitorKernelError) as denied:
        repository.get(definition.view_ref, "profile:other")
    assert denied.value.code is contracts.MonitorErrorCode.PARTITION_MISMATCH
    bad = copy.deepcopy(definition.to_dict())
    bad["search"]["cursor"] = "opaque"
    with pytest.raises(contracts.MonitorContractError):
        contracts.SavedQueryDefinitionV1.from_dict(bad)
    for field in ("saved_query_id",):
        unbounded = definition.to_dict()
        unbounded[field] = "q" * 129
        with pytest.raises(contracts.MonitorContractError, match="at most 128"):
            contracts.SavedQueryDefinitionV1.from_dict(unbounded)
    unbounded_ref = definition.view_ref.to_dict()
    unbounded_ref["saved_query_id"] = "q" * 129
    with pytest.raises(contracts.MonitorContractError, match="at most 128"):
        contracts.SavedQueryViewRefV1.from_dict(unbounded_ref)
    longest_partition = definition.to_dict()
    longest_partition["access_partition_id"] = "profile:" + "p" * 128
    assert (
        contracts.SavedQueryDefinitionV1.from_dict(longest_partition)
        .access_partition_id
        == longest_partition["access_partition_id"]
    )


def _composition(tmp_path, **options):
    corpus = tmp_path / "corpus.db"
    _seed_post_corpus(corpus)
    repository = SavedQueryRepository(tmp_path / "monitors.db")
    repository.initialize()
    definition = _definition(filters={"sources": ["reddit", "x"]})
    repository.save(definition)
    backend = PostSearchBackend(corpus, clock=lambda: datetime(2026, 9, 14, tzinfo=timezone.utc))
    provider = SavedQueryViewProvider(repository, backend, **options)
    kernel = MonitorKernel(repository, provider, clock=lambda: "2026-09-14T00:00:00Z")
    spec = contracts.MonitorSpecV1.from_dict({
        "schema_version": 1, "monitor_id": "monitor-browser", "revision": 1,
        "name": "Browser changes", "view_ref": definition.view_ref.to_dict(),
        "access_partition_id": "public", "lifecycle_state": "disabled",
        "comparison_policy": "stable_evidence_v1", "cadence_seconds": 3600,
        "max_items": 100, "retention_days": 90, "created_by": "fixture",
        "created_at": "2026-09-14T00:00:00Z",
    })
    kernel.create(spec)
    kernel.activate(spec.monitor_id, actor="fixture")
    return repository, definition, backend, provider, kernel


def test_real_search_pages_freeze_provenance_and_replay_without_durable_cursor(tmp_path):
    repository, definition, backend, provider, kernel = _composition(tmp_path)
    snapshot = provider.capture(definition.view_ref, "public", "capture-1")
    assert len(snapshot.evidence) == 2
    assert snapshot.coverage.status is contracts.CoverageStatus.COMPLETE
    receipt = provider.receipt(definition.view_ref, "public", "capture-1")
    assert set(receipt["component_heads"]) == {"legacy", "temporal"}
    assert receipt["pages"] == 2
    assert "cursor" not in json.dumps(receipt)
    assert len(receipt["evidence_refs"]) == 2
    assert snapshot.knowledge_cutoff == "2026-09-14T00:00:00Z"
    first = kernel.evaluate("monitor-browser", snapshot.snapshot_id)
    assert repository.current_baseline("monitor-browser") is None
    assert first == kernel.evaluate("monitor-browser", snapshot.snapshot_id)
    kernel.accept(first.run_id, actor="fixture")
    reopened = SavedQueryViewProvider(SavedQueryRepository(repository.db_path), backend)
    assert reopened.capture(definition.view_ref, "public", "capture-1") == snapshot
    second = provider.capture(definition.view_ref, "public", "capture-2")
    compared = kernel.evaluate("monitor-browser", second.snapshot_id)
    assert len(compared.comparison.by_kind(contracts.ChangeKind.UNCHANGED)) == 2
    assert compared.comparison.by_kind(contracts.ChangeKind.REMOVED) == ()


def test_all_revision_saved_queries_are_explicitly_rejected():
    with pytest.raises(contracts.MonitorContractError, match="revision_mode=current"):
        _definition(revision_mode="all")


@pytest.mark.parametrize("limits", [{"max_items": 1}, {"max_pages": 1}, {"max_bytes": 1}])
def test_partial_first_capture_cannot_establish_an_accepted_baseline(tmp_path, limits):
    repository, definition, _, provider, kernel = _composition(tmp_path, **limits)
    snapshot = provider.capture(definition.view_ref, "public", "limited")
    assert snapshot.coverage.status is contracts.CoverageStatus.PARTIAL
    run = kernel.evaluate("monitor-browser", snapshot.snapshot_id)
    with pytest.raises(MonitorKernelError) as incomplete:
        kernel.accept(run.run_id, actor="fixture")
    assert incomplete.value.code is contracts.MonitorErrorCode.COMPARISON_INCOMPLETE
    assert repository.current_baseline("monitor-browser") is None


def test_an_older_frozen_view_cannot_replace_a_newer_accepted_baseline(tmp_path):
    repository, definition, backend, provider, kernel = _composition(tmp_path)
    first = provider.capture(definition.view_ref, "public", "newer")
    run = kernel.evaluate("monitor-browser", first.snapshot_id)
    kernel.accept(run.run_id, actor="fixture")
    backend.clock = lambda: datetime(2026, 9, 13, tzinfo=timezone.utc)
    older = provider.capture(definition.view_ref, "public", "older")
    stale = kernel.evaluate("monitor-browser", older.snapshot_id)
    with pytest.raises(MonitorKernelError) as error:
        kernel.accept(stale.run_id, actor="fixture")
    assert error.value.code is contracts.MonitorErrorCode.COMPARISON_INCOMPLETE
    assert repository.current_baseline("monitor-browser").baseline_id == run.candidate_baseline_id


@pytest.mark.parametrize("mode", ["restart", "expired", "head", "partition", "query", "duplicate"])
def test_interrupted_or_drifting_traversal_is_terminal_not_implicitly_retried(tmp_path, mode):
    repository, definition, backend, _, kernel = _composition(tmp_path)
    elapsed = [0.0]
    backend.monotonic = lambda: elapsed[0]
    original = backend.search

    class InterruptedSearch:
        def search(self, request, *, access_partitions):
            if mode == "restart" and request.cursor:
                return PostSearchBackend(backend.db_path).search(request, access_partitions=access_partitions)
            if mode == "expired" and request.cursor:
                elapsed[0] = 901
            response = original(request, access_partitions=access_partitions)
            if request.cursor:
                if mode == "head":
                    response = replace(response, search_head_id="unexpected-head")
                if mode == "query":
                    response = replace(response, query="unrequested")
                if mode == "partition":
                    response = replace(response, hits=(replace(response.hits[0], access_partition_id="private"),))
                if mode == "duplicate":
                    response = replace(response, hits=(first_hit[0],))
            else:
                first_hit.append(response.hits[0])
            return response

    first_hit = []
    provider = SavedQueryViewProvider(repository, InterruptedSearch())
    with pytest.raises(MonitorKernelError):
        provider.capture(definition.view_ref, "public", "interrupted")
    # A fresh process with a healthy backend must not silently rerun this ID.
    fresh = SavedQueryViewProvider(SavedQueryRepository(repository.db_path), backend)
    with pytest.raises(MonitorKernelError, match="no automatic replay"):
        fresh.capture(definition.view_ref, "public", "interrupted")
    assert repository.current_baseline("monitor-browser") is None
    assert b'next_cursor' not in repository.db_path.read_bytes()


def test_new_revised_and_absent_posts_compare_without_inventing_removal(tmp_path):
    repository, definition, backend, provider, kernel = _composition(tmp_path)
    first = provider.capture(definition.view_ref, "public", "before")
    initial = kernel.evaluate("monitor-browser", first.snapshot_id)
    kernel.accept(initial.run_id, actor="fixture")
    with sqlite3.connect(backend.db_path) as conn:
        conn.execute("""INSERT INTO service_source_versions
            SELECT 'revised-v2', record_id, provider_attempt_id,
                   'sha256:revised-v2', title, normalized_text, author, published_at,
                   metadata_json, observed_at, access_partition_id, retention_class,
                   '2026-09-12T00:00:00Z'
            FROM service_source_versions WHERE version_id='version-tick-public'""")
        conn.execute("UPDATE service_source_records SET current_version_id='revised-v2' "
                     "WHERE record_id='record-tick-public'")
        conn.execute("""INSERT INTO service_source_records
            SELECT 'new-record', service_id, source, 'new-native-id',
                   'https://x.example/new', access_partition_id, 'new-version', created_at
            FROM service_source_records WHERE record_id='record-tick-public'""")
        conn.execute("""INSERT INTO service_source_versions
            SELECT 'new-version', 'new-record', provider_attempt_id, 'sha256:new', title,
                   normalized_text, author, published_at, metadata_json, observed_at,
                   access_partition_id, retention_class, '2026-09-12T00:00:00Z'
            FROM service_source_versions WHERE version_id='version-tick-public'""")
        # No current searchable version is absence, not a tombstone.
        conn.execute("UPDATE documents SET current_version_id=NULL WHERE document_id='doc-legacy'")
    after = provider.capture(definition.view_ref, "public", "after")
    run = kernel.evaluate("monitor-browser", after.snapshot_id)
    assert len(run.comparison.by_kind(contracts.ChangeKind.NEW)) == 1
    assert len(run.comparison.by_kind(contracts.ChangeKind.REVISED)) == 1
    assert run.comparison.by_kind(contracts.ChangeKind.REMOVED) == ()
    kernel.accept(run.run_id, actor="fixture")
    assert len(repository.current_baseline("monitor-browser").evidence) == 3


def test_search_corpus_is_read_only_and_query_capture_partition_is_exact(tmp_path):
    _, definition, backend, provider, _ = _composition(tmp_path)
    before = backend.db_path.read_bytes()
    snapshot = provider.capture(definition.view_ref, "public", "read-only")
    assert backend.db_path.read_bytes() == before
    with pytest.raises(MonitorKernelError) as denied:
        provider.read(definition.view_ref, "profile:other", snapshot.snapshot_id)
    assert denied.value.code is contracts.MonitorErrorCode.PARTITION_MISMATCH


def test_degraded_semantic_coverage_is_retained_but_not_accepted(tmp_path):
    repository, _, _, provider, kernel = _composition(tmp_path)
    definition = _definition(2, query="browser", filters={"sources": ["reddit", "x"]})
    repository.save(definition)
    snapshot = provider.capture(definition.view_ref, "public", "missing-vectors")
    assert snapshot.coverage.status is contracts.CoverageStatus.PARTIAL
    assert "semantic_incomplete" in snapshot.coverage.gaps
    receipt = provider.receipt(definition.view_ref, "public", "missing-vectors")
    assert receipt["coverage"]["semantic"]["families"]["legacy"]["missing"] == 1


def test_local_command_payloads_round_trip_the_same_saved_view(tmp_path):
    repository, definition, backend, provider, _ = _composition(tmp_path)
    from lib.service_monitor_views import saved_query_command
    payload = {"action": "capture", "view_ref": definition.view_ref.to_dict(),
               "capture_id": "transport-fixture"}
    # JSON-compatible local command seam for coordinator-owned CLI/MCP joins.
    direct = saved_query_command(provider, payload, access_partition_id="public")
    json_client = saved_query_command(provider, json.loads(json.dumps(payload)),
                                      access_partition_id="public")
    assert direct == json_client
    with pytest.raises(contracts.MonitorContractError):
        saved_query_command(provider, {**payload, "access_partition_id": "private"},
                            access_partition_id="public")


@pytest.mark.parametrize("mode", ["truncated", "unavailable_filter", "deadline", "process_loss"])
def test_incomplete_coverage_and_interrupted_capture_keep_acceptance_closed(tmp_path, mode):
    repository, definition, backend, _, kernel = _composition(tmp_path)
    times = [0.0]

    class LimitedSearch:
        def search(self, request, *, access_partitions):
            if mode == "process_loss":
                raise KeyboardInterrupt("simulated process interruption")
            response = backend.search(request, access_partitions=access_partitions)
            if mode == "truncated":
                response = replace(response, next_cursor=None)
            if mode == "unavailable_filter":
                response = replace(response, coverage={**response.coverage, "unavailable_filters": ["source"]})
            if mode == "deadline":
                times[0] = 11.0
            return response

    provider = SavedQueryViewProvider(repository, LimitedSearch(), monotonic=lambda: times[0])
    if mode in ("process_loss", "deadline"):
        with pytest.raises(KeyboardInterrupt if mode == "process_loss" else MonitorKernelError):
            provider.capture(definition.view_ref, "public", "incomplete")
        with pytest.raises(MonitorKernelError, match="no automatic replay"):
            SavedQueryViewProvider(repository, backend).capture(definition.view_ref, "public", "incomplete")
    else:
        snapshot = provider.capture(definition.view_ref, "public", "incomplete")
        assert snapshot.coverage.status is contracts.CoverageStatus.PARTIAL
        run = kernel.evaluate("monitor-browser", snapshot.snapshot_id)
        with pytest.raises(MonitorKernelError):
            kernel.accept(run.run_id, actor="fixture")
    assert repository.current_baseline("monitor-browser") is None


def test_empty_complete_query_and_changed_capture_limits_are_explicit(tmp_path):
    repository, _, backend, provider, _ = _composition(tmp_path)
    definition = _definition(2, filters={"sources": ["youtube"]})
    repository.save(definition)
    snapshot = provider.capture(definition.view_ref, "public", "empty")
    assert snapshot.evidence == ()
    assert snapshot.coverage.status is contracts.CoverageStatus.COMPLETE
    with pytest.raises(MonitorKernelError, match="capture inputs changed"):
        SavedQueryViewProvider(repository, backend, max_items=1).capture(
            definition.view_ref, "public", "empty")


def test_fractional_timestamp_order_is_numeric_not_lexical():
    with pytest.raises(contracts.MonitorContractError, match="out of order"):
        contracts.SavedQueryViewSnapshotV1.from_dict({
            "schema_version": 1, "snapshot_id": "fractional", "view_ref": _definition().view_ref.to_dict(),
            "access_partition_id": "public", "evidence_head_id": "head",
            "knowledge_cutoff": "2026-09-14T00:00:00Z",
            "coverage_start": "2026-09-14T00:00:00.1Z", "coverage_end": "2026-09-14T00:00:00Z",
            "coverage": {"status": "complete", "sources": [], "gaps": []}, "evidence": [],
        })
