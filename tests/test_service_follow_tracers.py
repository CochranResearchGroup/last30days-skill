"""Provider-free native follows through their real collection and route seams."""

import hashlib
import json
import sqlite3
import time
from dataclasses import replace
from pathlib import Path

import pytest
from lib import service_contracts as contracts
from lib.service_acquisition_worker import execute_work
from lib.service_collection import CollectionCoordinator, CollectionSpecValidationError
from lib.service_follow_capabilities import compatibility_trace
from lib.service_job_runner import AcquisitionJobRunner, JobRunnerPolicy
from lib.service_post_search import PostSearchBackend
from lib.service_publication import CorpusPublisher
from lib.service_retrieval import HybridRetriever

from tests.test_service_acquisition_worker import _request
from tests.test_service_collection import NOW, _coordinator, _follow_spec, _spec


def _fixture_coordinator(tmp_path):
    db, supervisor, ledger, scheduler, _ = _coordinator(tmp_path)
    coordinator = CollectionCoordinator(db, scheduler, clock=lambda: NOW,
                                        follow_execution_ready=lambda spec: True)
    return db, supervisor, ledger, scheduler, coordinator


def _native_request(source="reddit", kind="community", value="fixturelab", **overrides):
    spec = _follow_spec(source=source, surface_kind=kind, selector={kind: value})
    context = {
        "collection_spec_id": spec.collection_spec_id,
        "spec_version": spec.spec_version,
        "collection_run_id": "run-fixture",
        "collection_purpose": "tailored_follow",
        "surface_kind": kind,
        "selector": spec.selector,
        "selector_digest": spec.selector_digest,
        "follow_target_id": spec.follow_target_id,
        "attention_class": spec.attention_class,
        "access_partition_id": spec.access_partition_id,
    }
    return _request(
        source=source,
        profile_id=spec.profile_id,
        surface_kind=kind,
        query=spec.query,
        collection_context=context,
        adapter="reddit_keyless" if source == "reddit" else "youtube_ytdlp",
        **overrides,
    )


def test_reddit_community_can_be_created_disabled_with_native_identity(tmp_path):
    _db, _supervisor, _ledger, _scheduler, coordinator = _coordinator(tmp_path)
    spec = _follow_spec(
        source="reddit",
        surface_kind="community",
        selector={"community": "r/FixtureLab"},
    )
    saved = coordinator.put_spec(spec)
    assert saved.selector == {"community": "fixturelab"}
    assert saved.follow_target.canonical_id == "fixturelab"
    assert saved.required_access_method == "keyless"
    assert not saved.enabled
    assert not saved.is_quarantined_follow
    assert coordinator.get_spec(saved.collection_spec_id) == saved


@pytest.mark.parametrize(
    ("source", "kind", "value", "canonical", "method"),
    [
        ("reddit", "user", "u/Fixture-User", "fixture-user", "keyless"),
        (
            "youtube",
            "channel",
            "UCabcdefghijklmnopqrstuv",
            "UCabcdefghijklmnopqrstuv",
            "yt_dlp",
        ),
    ],
)
def test_native_follows_preserve_identity_and_archive_history(
    tmp_path, source, kind, value, canonical, method
):
    _db, _supervisor, _ledger, _scheduler, coordinator = _fixture_coordinator(tmp_path)
    spec = coordinator.put_spec(
        _follow_spec(source=source, surface_kind=kind, selector={kind: value})
    )
    assert spec.follow_target.canonical_id == canonical
    assert spec.required_access_method == method
    enabled = coordinator.set_enabled(spec.collection_spec_id, enabled=True)
    paused = coordinator.set_enabled(spec.collection_spec_id, enabled=False)
    archived = coordinator.archive_spec(spec.collection_spec_id)
    assert [
        spec.spec_version,
        enabled.spec_version,
        paused.spec_version,
        archived.spec_version,
    ] == [1, 2, 3, 4]
    assert (
        len({item.follow_target_id for item in (spec, enabled, paused, archived)}) == 1
    )
    assert not archived.enabled


def test_reddit_native_route_publishes_only_exact_community_posts():
    fixture = json.loads(
        (Path(__file__).parent / "fixtures/follow_reddit_packet2.json").read_text()
    )
    calls = []

    def transport(route, **limits):
        calls.append((route, limits))
        return fixture

    result = execute_work(
        _native_request(), {}, follow_transports={"reddit_community_posts": transport}
    )
    assert result.status is contracts.AcquisitionStatus.SUCCEEDED
    assert result.item_count == 1
    assert result.items[0].source_native_id == "fixture001"
    assert result.network_request_count == 1
    assert calls[0][0] == "https://www.reddit.com/r/fixturelab/new.json?limit=20"
    assert calls[0][1]["maximum_bytes"] == 1_048_576
    assert result.diagnostics["follow_route"] == "reddit_community_posts"


def test_youtube_uploads_route_requires_channel_identity_and_bounded_transport():
    fixture = json.loads(
        (Path(__file__).parent / "fixtures/follow_youtube_packet2.json").read_text()
    )
    calls = []

    def transport(route, **limits):
        calls.append((route, limits))
        return fixture

    result = execute_work(
        _native_request("youtube", "channel", "UCabcdefghijklmnopqrstuv"),
        {},
        follow_transports={"youtube_channel_uploads": transport},
    )
    assert result.status is contracts.AcquisitionStatus.SUCCEEDED
    assert result.items[0].source_native_id == "abcDEF123_-"
    assert result.network_request_count == 1
    assert (
        calls[0][0] == "https://www.youtube.com/playlist?list=UUabcdefghijklmnopqrstuv"
    )
    assert calls[0][1]["item_limit"] == 20
    assert result.diagnostics["follow_route"] == "youtube_channel_uploads"


def test_malformed_legacy_native_target_remains_readable_and_cannot_starve_due_work(
    tmp_path,
):
    db, _supervisor, _ledger, _scheduler, coordinator = _fixture_coordinator(tmp_path)
    saved = coordinator.put_spec(
        _follow_spec(
            source="reddit",
            surface_kind="community",
            selector={"community": "fixturelab"},
        )
    )
    legacy = replace(saved, selector={"community": "bad//target"}, enabled=True)
    with sqlite3.connect(db) as conn:
        conn.execute(
            "UPDATE collection_specs SET enabled=1, selector_json=?, follow_target_id=? WHERE collection_spec_id=?",
            (
                json.dumps(legacy.selector),
                legacy.follow_target_id,
                saved.collection_spec_id,
            ),
        )
        conn.execute(
            "UPDATE collection_spec_revisions SET spec_json=?, spec_digest=?, selector_digest=? WHERE collection_spec_id=?",
            (
                json.dumps(legacy.to_dict()),
                legacy.spec_digest,
                legacy.selector_digest,
                saved.collection_spec_id,
            ),
        )
    restored = coordinator.get_spec(saved.collection_spec_id)
    assert restored.selector == legacy.selector
    assert restored.is_quarantined_follow
    healthy = coordinator.put_spec(
        _follow_spec(
            collection_spec_id="healthy-native",
            name="Healthy native",
            source="reddit",
            surface_kind="user",
            selector={"user": "fixture-user"},
        )
    )
    coordinator.set_enabled(healthy.collection_spec_id, enabled=True)
    assert [run.collection_spec_id for run in coordinator.enqueue_due(limit=1)] == [
        healthy.collection_spec_id
    ]
    with pytest.raises(CollectionSpecValidationError):
        coordinator.set_enabled(restored.collection_spec_id, enabled=True)
    assert not coordinator.set_enabled(
        restored.collection_spec_id, enabled=False
    ).enabled
    assert (
        coordinator.archive_spec(restored.collection_spec_id).lifecycle_state
        == "archived"
    )


@pytest.mark.parametrize(
    ("source", "kind", "value", "route", "fixture_name"),
    [
        ("reddit", "community", "fixturelab", "reddit_community_posts", "reddit"),
        ("reddit", "user", "fixture-user", "reddit_user_posts", "reddit"),
        (
            "youtube",
            "channel",
            "UCabcdefghijklmnopqrstuv",
            "youtube_channel_uploads",
            "youtube",
        ),
    ],
)
def test_native_errors_empty_results_and_usage_are_truthful(
    source, kind, value, route, fixture_name
):
    request = _native_request(source, kind, value)
    fixture = json.loads(
        (
            Path(__file__).parent / f"fixtures/follow_{fixture_name}_packet2.json"
        ).read_text()
    )

    def run(payload):
        return execute_work(
            request, {}, follow_transports={route: lambda *args, **kwargs: payload}
        )

    unavailable = execute_work(request, {})
    assert (unavailable.safe_error_code, unavailable.retry_class.value) == (
        "adapter_unavailable",
        "configuration",
    )
    for status, code, retry in (
        (401, "unauthorized_target", "operator"),
        (403, "unauthorized_target", "operator"),
        (404, "target_unavailable", "permanent"),
        (429, "rate_limited", "rate_limit"),
    ):
        outcome = run({**fixture, "status": status})
        assert (outcome.safe_error_code, outcome.retry_class.value) == (code, retry)
        assert outcome.item_count == 0
    empty = json.loads(json.dumps(fixture))
    if source == "reddit":
        empty["payload"]["data"]["children"] = []
    else:
        empty["payload"]["entries"] = []
    assert run(empty).status is contracts.AcquisitionStatus.SUCCEEDED
    assert run(empty).item_count == 0
    assert (
        run(
            {**fixture, "network_request_count": request.network_request_limit + 1}
        ).safe_error_code
        == "network_budget_exhausted"
    )
    assert (
        run({**fixture, "network_request_count": None}).safe_error_code
        == "validator_failed"
    )
    corrupted = json.loads(json.dumps(fixture))
    if source == "reddit":
        corrupted["payload"]["data"]["children"][0]["data"][
            "subreddit" if kind == "community" else "author"
        ] = "other-target"
    else:
        corrupted["payload"]["entries"][0]["channel_id"] = "UCother-channel-identity0"
    assert run(corrupted).safe_error_code == "route_mismatch"
    assert run(corrupted).item_count == 0


@pytest.mark.parametrize("source", ["reddit", "youtube"])
def test_real_coordinator_worker_publication_replay_and_partition_filtered_sightings(
    tmp_path, source
):
    db, supervisor, ledger, scheduler, coordinator = _fixture_coordinator(tmp_path)
    fixture = json.loads(
        (Path(__file__).parent / f"fixtures/follow_{source}_packet2.json").read_text()
    )
    specs = [
        coordinator.put_spec(
            _follow_spec(
                collection_spec_id=f"native-{kind}",
                name=f"Native {kind}",
                source=source,
                surface_kind=kind,
                selector={kind: value},
                lookback_seconds=604800,
            )
        )
        for kind, value in (
            (("community", "fixturelab"), ("user", "fixture-user"))
            if source == "reddit"
            else (("channel", "UCabcdefghijklmnopqrstuv"),)
        )
    ]
    specs.append(
        coordinator.put_spec(
            _spec(
                collection_spec_id="general-overlap",
                name="General overlap",
                source=source,
                selector={"topic": "fixture"},
                profile_id="x-primary",
                redaction_class="authenticated",
                required_access_method="keyless" if source == "reddit" else "yt_dlp",
                lookback_seconds=604800,
            )
        )
    )
    requests = []

    class Worker:
        def run(self, request):
            requests.append(request)
            if source == "reddit":
                raw = fixture["payload"]["data"]["children"][0]["data"]
                general = {
                    "items": [
                        {
                            "id": raw["id"],
                            "url": "https://www.reddit.com" + raw["permalink"],
                            "title": raw["title"],
                            "selftext": raw["selftext"],
                            "subreddit": raw["subreddit"],
                            "date": "2026-07-23T12:00:00Z",
                            "metadata": {"author": raw["author"]},
                        }
                    ]
                }
            else:
                raw = fixture["payload"]["entries"][0]
                general = {
                    "items": [
                        {
                            "video_id": raw["id"],
                            "url": "https://www.youtube.com/watch?v=" + raw["id"],
                            "title": raw["title"],
                            "description": raw["description"],
                            "channel_name": raw["channel"],
                            "date": "2026-07-23T00:00:00Z",
                            "media": [],
                        }
                    ]
                }
            return execute_work(
                request,
                {},
                clock=lambda: NOW,
                adapters={request.adapter: lambda *args: general},
                follow_transports={
                    "reddit_community_posts": lambda *args, **kwargs: fixture,
                    "reddit_user_posts": lambda *args, **kwargs: fixture,
                    "youtube_channel_uploads": lambda *args, **kwargs: fixture,
                },
            )

    runs = []
    for spec in specs:
        run = coordinator.enqueue_interval(
            spec.collection_spec_id, scheduled_for=NOW.isoformat(), trigger="manual"
        )
        assert (
            coordinator.enqueue_interval(
                spec.collection_spec_id, scheduled_for=NOW.isoformat(), trigger="timer"
            ).collection_run_id
            == run.collection_run_id
        )
        runs.append(run)
    coordinator.set_enabled(specs[0].collection_spec_id, enabled=True)
    coordinator.set_enabled(specs[0].collection_spec_id, enabled=False)
    retriever = HybridRetriever(db)
    runner = AcquisitionJobRunner(
        supervisor,
        ledger,
        CorpusPublisher(db, retriever, clock=lambda: NOW),
        Worker(),
        scheduler,
        JobRunnerPolicy(lease_seconds=121),
        clock=lambda: NOW,
        collection_coordinator=coordinator,
    )
    for index in range(len(specs)):
        assert runner.run_once(worker_id=f"fixture-{index}").state.value == "published"
    assert runner.run_once(worker_id="fixture-replay") is None
    assert requests[0].collection_context.spec_version == 1
    for spec in specs:
        search_request = contracts.PostSearchRequest.from_dict(
            {
                "schema_version": 1,
                "request_id": f"search-{spec.collection_spec_id}",
                "profile_id": "x-primary",
                "query": None,
                "filters": {
                    "collection_refs": [f"legacy:spec:{spec.collection_spec_id}"]
                },
                "page_size": 10,
                "cursor": None,
            }
        )
        found = PostSearchBackend(db).search(
            search_request, access_partitions=(spec.access_partition_id,)
        )
        assert found.returned == 1
        assert set(found.hits[0].collection_refs) >= {
            f"legacy:spec:{entry.collection_spec_id}" for entry in specs
        }
        assert (
            PostSearchBackend(db)
            .search(search_request, access_partitions=("profile:other",))
            .returned
            == 0
        )
    with sqlite3.connect(db) as conn:
        assert conn.execute("SELECT count(*) FROM document_versions").fetchone()[0] == 1
        assert conn.execute(
            "SELECT count(*) FROM document_version_sightings"
        ).fetchone()[0] == len(specs)


@pytest.mark.parametrize(
    ("source", "kind", "selector", "code"),
    [
        ("reddit", "community", "r/r/fixturelab", "malformed_target"),
        ("reddit", "community", "fixture/lab", "malformed_target"),
        ("reddit", "user", "u/u/fixture-user", "malformed_target"),
        ("reddit", "user", "fixture user", "malformed_target"),
        ("youtube", "channel", "@fixture", "unresolved_target"),
        (
            "youtube",
            "channel",
            "https://www.youtube.com/c/fixture",
            "unresolved_target",
        ),
        ("youtube", "channel", "UCshort", "malformed_target"),
    ],
)
def test_native_selector_errors_do_not_resolve_locators(source, kind, selector, code):
    with pytest.raises(CollectionSpecValidationError, match=code):
        _follow_spec(source=source, surface_kind=kind, selector={kind: selector})


def test_forged_frozen_context_and_disallowed_access_never_reach_transport():
    request = _native_request()
    calls = []

    def transport(*args, **kwargs):
        calls.append(args)
        raise AssertionError("No transport call is allowed")

    for field, value, code in (
        ("selector_digest", "sha256:forged", "route_mismatch"),
        ("follow_target_id", "follow-target-forged", "route_mismatch"),
    ):
        forged = replace(
            request,
            collection_context=replace(request.collection_context, **{field: value}),
        )
        result = execute_work(
            forged, {}, follow_transports={"reddit_community_posts": transport}
        )
        assert result.safe_error_code == code
    assert (
        execute_work(
            replace(request, profile_id="other"),
            {},
            follow_transports={"reddit_community_posts": transport},
        ).safe_error_code
        == "unauthorized_target"
    )
    assert (
        execute_work(
            request,
            {"LAST30DAYS_REDDIT_ACCESS_ORDER": "scrapecreators"},
            follow_transports={"reddit_community_posts": transport},
        ).safe_error_code
        == "unauthorized_target"
    )
    assert calls == []


def test_reddit_pagination_is_bounded_and_never_retries_a_cycle():
    request = _native_request(network_request_limit=2)
    fixture = json.loads(
        (Path(__file__).parent / "fixtures/follow_reddit_packet2.json").read_text()
    )
    fixture["payload"]["data"]["after"] = "t3_fixture001"
    calls = []

    def transport(route, **kwargs):
        calls.append(route)
        return fixture

    result = execute_work(
        request, {}, follow_transports={"reddit_community_posts": transport}
    )
    assert result.safe_error_code == "pagination_cycle"
    assert result.item_count == 0
    assert len(calls) == 2
    assert "after=t3_fixture001" in calls[1]


@pytest.mark.parametrize("source", ["reddit", "youtube"])
def test_native_timeout_and_zero_budget_do_not_fall_back(source):
    request = (
        _native_request()
        if source == "reddit"
        else _native_request("youtube", "channel", "UCabcdefghijklmnopqrstuv")
    )
    route = (
        "reddit_community_posts" if source == "reddit" else "youtube_channel_uploads"
    )
    calls = []

    def timeout(*args, **kwargs):
        calls.append(args)
        raise TimeoutError

    result = execute_work(request, {}, follow_transports={route: timeout})
    assert result.safe_error_code == "wall_time_budget_exhausted"
    assert len(calls) == 1
    result = execute_work(
        replace(request, network_request_limit=0),
        {},
        follow_transports={route: timeout},
    )
    assert result.safe_error_code == "network_budget_exhausted"
    assert len(calls) == 1


def test_frozen_10000_sighting_filter_and_compatibility_baseline(tmp_path):
    test_real_coordinator_worker_publication_replay_and_partition_filtered_sightings(
        tmp_path, "reddit"
    )
    db = tmp_path / "research.db"
    with sqlite3.connect(db) as conn:
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON")
        acquisition = dict(
            conn.execute(
                "SELECT * FROM acquisitions ORDER BY acquisition_id LIMIT 1"
            ).fetchone()
        )
        sighting = dict(
            conn.execute(
                "SELECT * FROM document_version_sightings ORDER BY acquisition_id LIMIT 1"
            ).fetchone()
        )
        acquisition_columns = tuple(acquisition)
        sighting_columns = tuple(sighting)
        for index in range(9997):
            acquisition["acquisition_id"] = sighting["acquisition_id"] = (
                f"baseline-acquisition-{index:05}"
            )
            conn.execute(
                f"INSERT INTO acquisitions ({','.join(acquisition_columns)}) VALUES ({','.join('?' for _ in acquisition_columns)})",
                tuple(acquisition[column] for column in acquisition_columns),
            )
            conn.execute(
                f"INSERT INTO document_version_sightings ({','.join(sighting_columns)}) VALUES ({','.join('?' for _ in sighting_columns)})",
                tuple(sighting[column] for column in sighting_columns),
            )
        assert (
            conn.execute("SELECT count(*) FROM document_version_sightings").fetchone()[
                0
            ]
            == 10000
        )
    request = contracts.PostSearchRequest.from_dict(
        {
            "schema_version": 1,
            "request_id": "baseline-search",
            "profile_id": "x-primary",
            "query": None,
            "filters": {"collection_refs": ["legacy:spec:native-community"]},
            "page_size": 10,
            "cursor": None,
        }
    )
    started = time.perf_counter()
    found = PostSearchBackend(db).search(
        request, access_partitions=("profile:x-primary",)
    )
    filter_seconds = time.perf_counter() - started
    assert found.returned == 1
    assert (
        PostSearchBackend(db)
        .search(request, access_partitions=("profile:other",))
        .returned
        == 0
    )
    rows = [
        {
            "collection_spec_id": f"compat-{index:05}",
            "collection_purpose": "tailored_follow",
            "source": "x",
            "surface_kind": "account",
            "selector_digest": "sha256:fixture",
        }
        for index in range(10000)
    ]
    started = time.perf_counter()
    evidence = compatibility_trace(rows)
    compatibility_seconds = time.perf_counter() - started
    assert evidence["mapped"] == 10000
    assert compatibility_trace(reversed(rows)) == evidence
    print(
        json.dumps(
            {
                "fixture": "wi005-packet2-10000-v1",
                "sightings": 10000,
                "content_versions": 1,
                "filter_seconds": round(filter_seconds, 6),
                "compatibility_seconds": round(compatibility_seconds, 6),
                "compatibility_digest": evidence["digest"],
                "input_sha256": hashlib.sha256(
                    json.dumps(rows, sort_keys=True).encode()
                ).hexdigest(),
            },
            sort_keys=True,
        )
    )


def test_native_transport_absence_denies_resume_and_manual_issuance(tmp_path):
    _db, _supervisor, _ledger, _scheduler, coordinator = _coordinator(tmp_path)
    spec = coordinator.put_spec(_follow_spec(source="reddit", surface_kind="community", selector={"community": "fixturelab"}))
    with pytest.raises(CollectionSpecValidationError, match="transport_not_configured"):
        coordinator.set_enabled(spec.collection_spec_id, enabled=True)
    with pytest.raises(CollectionSpecValidationError, match="transport_not_configured"):
        coordinator.enqueue_interval(spec.collection_spec_id, scheduled_for=NOW.isoformat(), trigger="manual")
    assert coordinator.get_spec(spec.collection_spec_id).enabled is False
