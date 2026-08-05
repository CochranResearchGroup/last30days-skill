"""Typed source-adapter boundary tests for the isolated worker process."""

import io
import base64
import json
from types import SimpleNamespace
import sys

from pathlib import Path

from lib import service_contracts as contracts
from lib import service_acquisition_worker
from lib.service_acquisition_worker import execute_work, load_profile_config
from lib.service_tick_http import (
    DeadlinePinnedMediaTransport,
    MediaDeadlineExceeded,
    PinnedMediaResponse,
    UnsafeMediaDestination,
)


def _request(**overrides):
    values = {
        "schema_version": 1,
        "work_id": "work-x-001",
        "job_id": "job-001",
        "lease_generation": 1,
        "attempt": 1,
        "profile_id": "research",
        "source": "x",
        "query": "cache service",
        "from_date": "2026-06-24",
        "to_date": "2026-07-24",
        "depth": "standard",
        "adapter": "x_agent_browser",
        "adapter_version": "1",
        "wall_timeout_seconds": 90,
        "item_limit": 20,
        "network_request_limit": 50,
        "cost_budget_cents": 25,
    }
    values.update(overrides)
    return contracts.AcquisitionWorkRequest.from_dict(values)


def test_worker_preserves_operator_failure_type_without_browser_leases():
    rendered_page = b"rendered-auth-challenge"

    def fake_adapter(_request, _config):
        return {
            "items": [],
            "error": "login required at a private operator URL",
            "error_type": "auth_required",
            "operator_url": "https://operator.example/private",
            "rendered_page_base64": base64.b64encode(rendered_page).decode("ascii"),
            "rendered_page_mime_type": "image/jpeg",
            "session": "secret-session",
            "diagnostics": {
                "accepted_count": 0,
                "failure_stage": "authentication",
                "route_id": "secret-route",
            },
        }

    result = execute_work(
        _request(),
        {"LAST30DAYS_X_BROWSER_PROFILE": "x-authenticated"},
        adapters={"x_agent_browser": fake_adapter},
    )

    assert result.status is contracts.AcquisitionStatus.AWAITING_OPERATOR
    assert result.retry_class is contracts.RetryClass.OPERATOR
    assert result.safe_error_code == "auth_required"
    assert result.diagnostics["accepted_count"] == 0
    assert result.diagnostics["failure_stage"] == "authentication"
    assert result.diagnostics["failure_signature"].startswith("sha256:")
    serialized = result.to_dict()
    assert serialized["operator_url"] == "https://operator.example/private"
    assert result.rendered_page == rendered_page
    assert result.rendered_page_mime_type == "image/jpeg"
    assert "secret-session" not in str(serialized)
    assert "secret-route" not in str(serialized)


def test_worker_fetches_bounded_image_bytes_into_the_typed_item_contract():
    image = b"small-image-bytes"

    class Transport:
        def get(self, _url, *, deadline, maximum_bytes, before_connect):
            assert deadline > 0
            assert maximum_bytes >= len(image)
            before_connect()
            return PinnedMediaResponse(
                status=200,
                headers={"content-type": "image/jpeg"},
                content=image,
            )

    def fake_adapter(_request, _config):
        return {
            "items": [
                {
                    "id": "X-media",
                    "text": "A post with a queryable image.",
                    "url": "https://x.com/example/status/media",
                    "date": "2026-07-23",
                    "metadata": {
                        "media": [
                            {
                                "kind": "image",
                                "url": "https://pbs.twimg.com/media/example.jpg",
                                "mime_type": "image/jpeg",
                                "alt_text": "A rendered chart",
                            }
                        ]
                    },
                }
            ],
            "diagnostics": {"accepted_count": 1},
        }

    result = execute_work(
        _request(network_request_limit=2),
        {},
        adapters={"x_agent_browser": fake_adapter},
        media_transport=Transport(),
    )

    assert result.status is contracts.AcquisitionStatus.SUCCEEDED
    assert result.network_request_count == 1
    assert len(result.items[0].media) == 1
    media = result.items[0].media[0]
    assert base64.b64decode(media.content_base64) == image
    assert media.media_kind == "image"
    assert media.alt_text == "A rendered chart"


def test_worker_rejects_private_media_destinations_before_network():
    def fake_adapter(_request, _config):
        return {
            "items": [
                {
                    "id": "private-media",
                    "text": "An item with an unsafe media destination.",
                    "url": "https://example.test/private-media",
                    "date": "2026-07-23",
                    "metadata": {
                        "media": [
                            {
                                "kind": "image",
                                "url": "https://127.0.0.1/private.jpg",
                                "mime_type": "image/jpeg",
                            }
                        ]
                    },
                }
            ]
        }

    socket_calls = []
    transport = DeadlinePinnedMediaTransport(
        socket_factory=lambda *_args: socket_calls.append(True),
    )
    result = execute_work(
        _request(network_request_limit=2),
        {},
        adapters={"x_agent_browser": fake_adapter},
        media_transport=transport,
    )

    assert result.status is contracts.AcquisitionStatus.PARTIAL
    assert result.safe_error_code == "unsafe_media_url"
    assert result.network_request_count == 0
    assert result.items[0].media == []
    assert socket_calls == []


def test_worker_rejects_redirects_to_private_media_destinations():
    def fake_adapter(_request, _config):
        return {
            "items": [
                {
                    "id": "redirect-media",
                    "text": "An item whose media redirects to a private host.",
                    "url": "https://example.test/redirect-media",
                    "date": "2026-07-23",
                    "metadata": {
                        "media": [
                            {
                                "kind": "image",
                                "url": "https://cdn.example.test/start.jpg",
                                "mime_type": "image/jpeg",
                            }
                        ]
                    },
                }
            ]
        }

    media_calls = []

    class Transport:
        def get(self, url, *, deadline, maximum_bytes, before_connect):
            del deadline, maximum_bytes
            media_calls.append(url)
            if url == "https://127.0.0.1/private.jpg":
                raise UnsafeMediaDestination("unsafe media destination")
            before_connect()
            return PinnedMediaResponse(
                status=302,
                headers={"location": "https://127.0.0.1/private.jpg"},
                content=b"",
            )

    result = execute_work(
        _request(network_request_limit=2),
        {},
        adapters={"x_agent_browser": fake_adapter},
        media_transport=Transport(),
    )

    assert result.status is contracts.AcquisitionStatus.PARTIAL
    assert result.safe_error_code == "unsafe_media_url"
    assert result.network_request_count == 1
    assert result.items[0].media == []
    assert media_calls == [
        "https://cdn.example.test/start.jpg",
        "https://127.0.0.1/private.jpg",
    ]


def test_worker_stops_media_fetches_at_the_remaining_wall_budget():
    class MediaResponse:
        status = 200
        headers = {"Content-Type": "image/jpeg"}

        def __init__(self, url):
            self.url = url

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def read(self, _limit=-1):
            return b"bounded-image"

        def geturl(self):
            return self.url

    def fake_adapter(_request, _config):
        return {
            "items": [
                {
                    "id": "wall-budget-media",
                    "text": "An item with two media references.",
                    "url": "https://example.test/wall-budget-media",
                    "date": "2026-07-23",
                    "metadata": {
                        "media": [
                            {
                                "kind": "image",
                                "url": "https://cdn.example.test/one.jpg",
                                "mime_type": "image/jpeg",
                            },
                            {
                                "kind": "image",
                                "url": "https://cdn.example.test/two.jpg",
                                "mime_type": "image/jpeg",
                            },
                        ]
                    },
                }
            ]
        }

    deadlines = []

    class Transport:
        def get(self, url, *, deadline, maximum_bytes, before_connect):
            del maximum_bytes
            deadlines.append(deadline)
            if len(deadlines) > 1:
                raise MediaDeadlineExceeded("media wall deadline exhausted")
            before_connect()
            return PinnedMediaResponse(
                status=200,
                headers={"content-type": "image/jpeg"},
                content=MediaResponse(url).read(),
            )

    result = execute_work(
        _request(network_request_limit=3, wall_timeout_seconds=1),
        {},
        adapters={"x_agent_browser": fake_adapter},
        media_transport=Transport(),
        monotonic_clock=lambda: 100.0,
    )

    assert result.status is contracts.AcquisitionStatus.PARTIAL
    assert result.safe_error_code == "wall_time_budget_exhausted"
    assert result.network_request_count == 1
    assert len(result.items[0].media) == 1
    assert deadlines == [101.0, 101.0]


def test_worker_does_not_connect_when_dns_consumes_the_wall_deadline():
    now = [100.0]
    socket_calls = []

    def fake_adapter(_request, _config):
        return {
            "items": [
                {
                    "id": "dns-wall-budget-media",
                    "text": "An item whose media DNS consumes the tick deadline.",
                    "url": "https://example.test/dns-wall-budget-media",
                    "date": "2026-07-23",
                    "metadata": {
                        "media": [
                            {
                                "kind": "image",
                                "url": "https://cdn.example.test/one.jpg",
                                "mime_type": "image/jpeg",
                            }
                        ]
                    },
                }
            ]
        }

    def resolve_after_deadline(*_args, **_kwargs):
        now[0] = 101.1
        return [(2, 1, 6, "", ("93.184.216.34", 443))]

    transport = DeadlinePinnedMediaTransport(
        resolver=resolve_after_deadline,
        socket_factory=lambda *_args: socket_calls.append(True),
        monotonic_clock=lambda: now[0],
    )
    result = execute_work(
        _request(network_request_limit=2, wall_timeout_seconds=1),
        {},
        adapters={"x_agent_browser": fake_adapter},
        media_transport=transport,
        monotonic_clock=lambda: now[0],
    )

    assert result.status is contracts.AcquisitionStatus.PARTIAL
    assert result.safe_error_code == "wall_time_budget_exhausted"
    assert result.network_request_count == 0
    assert result.items[0].media == []
    assert socket_calls == []


def test_worker_reapplies_pinned_transport_to_each_redirect_hop():
    image = b"redirected-image"

    def fake_adapter(_request, _config):
        return {
            "items": [
                {
                    "id": "redirected-pinned-media",
                    "text": "An item whose image uses one safe redirect.",
                    "url": "https://example.test/redirected-pinned-media",
                    "date": "2026-07-23",
                    "metadata": {
                        "media": [
                            {
                                "kind": "image",
                                "url": "https://cdn.example.test/start.jpg",
                                "mime_type": "image/jpeg",
                            }
                        ]
                    },
                }
            ]
        }

    class Transport:
        def __init__(self):
            self.calls = []

        def get(self, url, *, deadline, maximum_bytes, before_connect):
            self.calls.append((url, deadline, maximum_bytes))
            before_connect()
            if url.endswith("/start.jpg"):
                return PinnedMediaResponse(
                    status=302,
                    headers={"location": "https://media.example.test/final.jpg"},
                    content=b"",
                )
            return PinnedMediaResponse(
                status=200,
                headers={"content-type": "image/jpeg"},
                content=image,
            )

    transport = Transport()
    result = execute_work(
        _request(network_request_limit=3, wall_timeout_seconds=1),
        {},
        adapters={"x_agent_browser": fake_adapter},
        media_transport=transport,
        monotonic_clock=lambda: 100.0,
    )

    assert result.status is contracts.AcquisitionStatus.SUCCEEDED
    assert result.network_request_count == 2
    assert base64.b64decode(result.items[0].media[0].content_base64) == image
    assert [call[0] for call in transport.calls] == [
        "https://cdn.example.test/start.jpg",
        "https://media.example.test/final.jpg",
    ]
    assert {call[1] for call in transport.calls} == {101.0}


def test_worker_keeps_the_item_when_pinned_media_connection_fails():
    def fake_adapter(_request, _config):
        return {
            "items": [
                {
                    "id": "unavailable-media",
                    "text": "An item whose optional image host is unavailable.",
                    "url": "https://example.test/unavailable-media",
                    "date": "2026-07-23",
                    "metadata": {
                        "media": [
                            {
                                "kind": "image",
                                "url": "https://cdn.example.test/unavailable.jpg",
                                "mime_type": "image/jpeg",
                            }
                        ]
                    },
                }
            ]
        }

    class Transport:
        def get(self, _url, *, deadline, maximum_bytes, before_connect):
            del deadline, maximum_bytes
            before_connect()
            raise OSError("connection unavailable")

    result = execute_work(
        _request(network_request_limit=2),
        {},
        adapters={"x_agent_browser": fake_adapter},
        media_transport=Transport(),
    )

    assert result.status is contracts.AcquisitionStatus.SUCCEEDED
    assert result.safe_error_code is None
    assert result.network_request_count == 1
    assert result.items[0].media == []


def test_worker_captures_problem_page_through_agent_browser_without_guac_lease(
    monkeypatch,
):
    calls = []

    def run(argv, **_kwargs):
        calls.append(tuple(argv))
        output = service_acquisition_worker.Path(
            argv[argv.index("screenshot") + 1]
        )
        output.write_bytes(b"agent-browser-rendered-page")
        return SimpleNamespace(returncode=0, stdout="{}", stderr="")

    monkeypatch.setattr(service_acquisition_worker.subprocess, "run", run)

    result = execute_work(
        _request(),
        {},
        adapters={
            "x_agent_browser": lambda _request, _config: {
                "items": [],
                "error_type": "auth_required",
                "session": "last30days-facebook",
                "operator_url": "https://guac.example.test/client/session-1",
                "diagnostics": {"failure_stage": "authentication"},
            }
        },
    )

    assert result.rendered_page == b"agent-browser-rendered-page"
    assert result.rendered_page_mime_type == "image/jpeg"
    assert len(calls) == 1
    assert "screenshot" in calls[0]
    assert "remote-view" not in calls[0]
    assert "view_takeover" not in calls[0]


def test_worker_failure_signature_is_stable_across_attempts_and_job_ids():
    def fake_adapter(_request, _config):
        return {
            "items": [],
            "error_type": "agent_browser_error",
            "diagnostics": {
                "failure_stage": "authentication",
                "browser_operations": [
                    {"operation": "tab", "status": "failed", "duration_ms": 41}
                ],
            },
        }

    first = execute_work(
        _request(),
        {},
        adapters={"x_agent_browser": fake_adapter},
    )
    second = execute_work(
        _request(work_id="work-x-002", job_id="job-002", attempt=2),
        {},
        adapters={"x_agent_browser": fake_adapter},
    )

    assert first.diagnostics["failure_signature"] == second.diagnostics["failure_signature"]
    assert first.diagnostics["failure_stage"] == "authentication"
    assert first.diagnostics["browser_operations"][0]["operation"] == "tab"


def test_worker_normalizes_publishable_items_into_the_versioned_result():
    def fake_adapter(_request, _config):
        return {
            "items": [
                {
                    "id": "X1",
                    "text": "A cache-backed intelligence service keeps browser mechanics away.",
                    "url": "https://x.com/example/status/1",
                    "author_handle": "example",
                    "date": "2026-07-23",
                    "engagement": {"likes": 4},
                    "why_relevant": "Direct evidence",
                    "relevance": 1.0,
                    "metadata": {
                        "date_confidence": "high",
                        "media": [
                            {
                                "kind": "image",
                                "url": "https://pbs.twimg.com/media/example.jpg",
                                "preview_url": None,
                                "mime_type": "image/jpeg",
                                "width": None,
                                "height": None,
                                "duration_seconds": None,
                                "alt_text": "Example",
                            }
                        ],
                    },
                }
            ],
            "diagnostics": {"accepted_count": 1},
        }

    result = execute_work(
        _request(),
        {},
        adapters={"x_agent_browser": fake_adapter},
    )

    assert result.status is contracts.AcquisitionStatus.SUCCEEDED
    assert result.retry_class is contracts.RetryClass.NONE
    assert result.item_count == 1
    assert result.items[0].url == "https://x.com/example/status/1"
    assert "cache-backed" in result.items[0].text
    assert result.items[0].metadata["media"][0]["kind"] == "image"
    assert result.diagnostics["attempted_access_methods"] == ["agent_browser"]
    assert result.diagnostics["selected_access_method"] == "agent_browser"
    assert result.diagnostics["adapter_variant"] == "x_agent_browser"


def test_worker_emits_exact_request_and_outcome_counts():
    def fake_adapter(_request, _config):
        return {
            "items": [
                {
                    "id": "X1",
                    "text": "Observable acquisition evidence survives the worker seam.",
                    "url": "https://x.com/example/status/observable",
                    "author_handle": "example",
                    "date": "2026-07-23",
                }
            ],
            "_network_request_count": 1,
            "diagnostics": {
                "accepted_count": 1,
                "rejection_counts": {"off_topic": 2},
            },
        }

    result = execute_work(
        _request(),
        {},
        adapters={"x_agent_browser": fake_adapter},
    )

    assert result.network_request_count == 1
    assert result.attempted_count == 3
    assert result.observed_count == 3
    assert result.accepted_count == 1
    assert result.rejected_count == 2


def test_worker_does_not_double_count_aggregate_rejected_candidates():
    def fake_adapter(_request, _config):
        return {
            "items": [
                {
                    "id": "X1",
                    "text": "One accepted candidate remains exact after quality gating.",
                    "url": "https://x.com/example/status/candidate-count",
                    "date": "2026-07-23",
                }
            ],
            "_network_request_count": 1,
            "diagnostics": {
                "candidate_counts": {"post": 3, "rejected": 2},
                "accepted_count": 1,
                "rejection_counts": {"off_topic": 2},
            },
        }

    result = execute_work(
        _request(),
        {},
        adapters={"x_agent_browser": fake_adapter},
    )

    assert result.observed_count == 3
    assert result.accepted_count == 1
    assert result.rejected_count == 2


def test_worker_rejects_opaque_request_usage_over_the_limit():
    result = execute_work(
        _request(network_request_limit=1),
        {},
        adapters={
            "x_agent_browser": lambda _request, _config: {
                "items": [],
                "_network_request_count": 2,
            }
        },
    )

    assert result.status is contracts.AcquisitionStatus.FAILED
    assert result.safe_error_code == "network_budget_exhausted"
    assert result.network_request_count == 2


def test_youtube_adapter_accounts_for_one_opaque_source_request(monkeypatch):
    from lib import youtube_yt

    monkeypatch.setattr(
        youtube_yt,
        "search_youtube",
        lambda *_args, **_kwargs: {"items": []},
    )

    result = service_acquisition_worker._youtube_adapter(_request(), {})

    assert result["_network_request_count"] == 1


def test_browser_adapters_account_for_one_opaque_source_request(monkeypatch):
    from lib import facebook, linkedin, x_browser

    monkeypatch.setattr(
        x_browser, "search_x_browser", lambda *_args, **_kwargs: {"items": []}
    )
    monkeypatch.setattr(
        facebook, "search_facebook", lambda *_args, **_kwargs: {"items": []}
    )
    monkeypatch.setattr(
        linkedin, "search_linkedin", lambda *_args, **_kwargs: {"items": []}
    )
    monkeypatch.setattr(
        linkedin, "acquire_linkedin_profile", lambda *_args, **_kwargs: {"items": []}
    )

    results = (
        service_acquisition_worker._x_adapter(_request(), {}),
        service_acquisition_worker._facebook_adapter(_request(), {}),
        service_acquisition_worker._linkedin_adapter(_request(), {}),
        service_acquisition_worker._linkedin_profile_adapter(_request(), {}),
    )

    assert [item["_network_request_count"] for item in results] == [1, 1, 1, 1]


def test_reddit_adapter_variant_follows_exact_access_method_provenance():
    assert service_acquisition_worker._result_adapter_variant(
        "reddit_api",
        {
            "attempted_access_methods": ["agent_browser"],
            "selected_access_method": None,
        },
    ) == "reddit_agent_browser"
    assert service_acquisition_worker._result_adapter_variant(
        "reddit_api",
        {
            "attempted_access_methods": ["keyless", "agent_browser"],
            "selected_access_method": None,
        },
    ) == "reddit_access_chain"
    assert service_acquisition_worker._result_adapter_variant(
        "reddit_api",
        {
            "attempted_access_methods": ["keyless", "agent_browser"],
            "selected_access_method": "agent_browser",
        },
    ) == "reddit_agent_browser"


def test_explicit_no_results_is_success_for_negative_caching():
    result = execute_work(
        _request(),
        {},
        adapters={"x_agent_browser": lambda _request, _config: {"items": []}},
    )

    assert result.status is contracts.AcquisitionStatus.SUCCEEDED
    assert result.item_count == 0
    assert result.safe_error_code is None


def test_named_profile_config_is_user_scoped_and_process_env_wins(tmp_path):
    config_root = tmp_path / "last30days"
    profiles = config_root / "profiles"
    profiles.mkdir(parents=True)
    (config_root / ".env").write_text(
        "LAST30DAYS_X_BROWSER_PROFILE=global-x\nSHARED=value\n",
        encoding="utf-8",
    )
    (profiles / "research.env").write_text(
        "LAST30DAYS_X_BROWSER_PROFILE=research-x\n",
        encoding="utf-8",
    )

    config = load_profile_config(
        "research",
        config_root=config_root,
        environ={"SHARED": "process-value"},
    )

    assert config["LAST30DAYS_X_BROWSER_PROFILE"] == "research-x"
    assert config["SHARED"] == "process-value"
    assert Path.cwd() not in (config_root, profiles)


def test_reddit_adapter_is_public_first_and_uses_supported_backup_key(monkeypatch):
    from lib import reddit, reddit_public

    public_depths = []
    paid_calls = []
    monkeypatch.setattr(
        reddit_public,
        "search_reddit_public",
        lambda *_args, depth=None, **_kwargs: public_depths.append(depth) or [],
    )

    def paid(*_args, token=None, **kwargs):
        paid_calls.append((token, kwargs))
        return {"items": []}

    monkeypatch.setattr(reddit, "search_reddit", paid)
    request = _request(
        source="reddit",
        adapter="reddit_api",
        work_id="work-reddit-001",
        item_limit=3,
    )

    result = service_acquisition_worker._reddit_adapter(
        request, {"SCRAPECREATORS_API_KEY": "dummy-test-key"}
    )

    assert result == {
        "items": [],
        "_cost_cents": 1,
        "diagnostics": {
            "attempted_access_methods": ["keyless", "scrapecreators"],
            "selected_access_method": None,
        },
    }
    assert public_depths == ["quick"]
    assert paid_calls == [
        (
            "dummy-test-key",
            {
                "depth": "quick",
                "global_search_limit": 1,
                "subreddit_search_limit": 0,
                "request_timeout": 20,
                "request_retries": 1,
                "min_dns_retries": 1,
            },
        )
    ]


def test_reddit_adapter_returns_public_items_without_paid_fallback(monkeypatch):
    from lib import reddit, reddit_public

    monkeypatch.setattr(
        reddit_public,
        "search_reddit_public",
        lambda *_args, **_kwargs: [{"id": "R1"}],
    )
    paid_calls = []
    monkeypatch.setattr(
        reddit,
        "search_reddit",
        lambda *_args, **_kwargs: paid_calls.append(True),
    )

    result = service_acquisition_worker._reddit_adapter(
        _request(
            source="reddit",
            adapter="reddit_api",
            work_id="work-reddit-public-001",
            item_limit=3,
        ),
        {"SCRAPECREATORS_API_KEY": "dummy-test-key"},
    )

    assert result == {
        "items": [{"id": "R1"}],
        "_cost_cents": 0,
        "diagnostics": {
            "attempted_access_methods": ["keyless"],
            "selected_access_method": "keyless",
        },
    }
    assert paid_calls == []


def test_reddit_keyless_adapter_cannot_fall_through_to_browser_or_paid(monkeypatch):
    from lib import reddit, reddit_browser, reddit_public

    calls = []
    monkeypatch.setattr(
        reddit_public,
        "search_reddit_public",
        lambda *_args, **_kwargs: calls.append("keyless") or [],
    )
    monkeypatch.setattr(
        reddit_browser,
        "search_reddit_browser",
        lambda *_args, **_kwargs: calls.append("agent_browser") or {"items": []},
    )
    monkeypatch.setattr(
        reddit,
        "search_reddit",
        lambda *_args, **_kwargs: calls.append("scrapecreators") or {"items": []},
    )

    result = service_acquisition_worker.execute_work(
        _request(
            source="reddit",
            adapter="reddit_keyless",
            work_id="work-reddit-keyless-only",
            cost_budget_cents=0,
        ),
        {
            "LAST30DAYS_REDDIT_ACCESS_ORDER": "keyless,agent_browser",
            "SCRAPECREATORS_API_KEY": "dummy-test-key",
        },
    )

    assert calls == ["keyless"]
    assert result.status is contracts.AcquisitionStatus.SUCCEEDED
    assert result.cost_cents == 0
    assert result.diagnostics["attempted_access_methods"] == ["keyless"]
    assert result.diagnostics["selected_access_method"] is None
    assert result.diagnostics["adapter_variant"] == "reddit_keyless"


def test_worker_entrypoint_accepts_collection_constrained_adapter(monkeypatch):
    request = _request(
        source="reddit",
        adapter="reddit_keyless",
        work_id="work-reddit-keyless-entrypoint",
        network_request_limit=0,
        cost_budget_cents=0,
    )
    stdout = io.StringIO()
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps(request.to_dict())))
    monkeypatch.setattr(sys, "stdout", stdout)
    monkeypatch.setattr(service_acquisition_worker, "load_profile_config", lambda _profile: {})

    assert service_acquisition_worker.main() == 0
    payload = json.loads(stdout.getvalue())
    assert payload["adapter"] == "reddit_keyless"
    assert payload["safe_error_code"] == "network_budget_exhausted"


def test_reddit_adapter_uses_enabled_browser_before_paid_fallback(monkeypatch):
    from lib import reddit, reddit_browser, reddit_public

    monkeypatch.setattr(reddit_public, "search_reddit_public", lambda *_args, **_kwargs: [])
    browser_calls = []
    monkeypatch.setattr(
        reddit_browser,
        "search_reddit_browser",
        lambda *_args, **kwargs: browser_calls.append(kwargs) or {"items": [{"id": "RB1"}]},
    )
    paid_calls = []
    monkeypatch.setattr(reddit, "search_reddit", lambda *_args, **_kwargs: paid_calls.append(True))

    result = service_acquisition_worker._reddit_adapter(
        _request(source="reddit", adapter="reddit_api", work_id="work-reddit-browser", item_limit=3),
        {
            "LAST30DAYS_REDDIT_BROWSER": "true",
            "SCRAPECREATORS_API_KEY": "dummy-test-key",
        },
    )

    assert result == {
        "items": [{"id": "RB1"}],
        "_network_request_count": 1,
        "_cost_cents": 0,
        "diagnostics": {
            "attempted_access_methods": ["keyless", "agent_browser"],
            "selected_access_method": "agent_browser",
        },
    }
    assert browser_calls == [{
        "depth": "quick",
        "config": {
            "LAST30DAYS_REDDIT_BROWSER": "true",
            "SCRAPECREATORS_API_KEY": "dummy-test-key",
        },
        "limit": 3,
    }]
    assert paid_calls == []


def test_reddit_adapter_obeys_explicit_user_access_order(monkeypatch):
    from lib import reddit, reddit_browser, reddit_public

    calls = []
    monkeypatch.setattr(
        reddit_public,
        "search_reddit_public",
        lambda *_args, **_kwargs: calls.append("keyless") or [{"id": "R-public"}],
    )
    monkeypatch.setattr(
        reddit_browser,
        "search_reddit_browser",
        lambda *_args, **_kwargs: calls.append("agent_browser")
        or {"items": [{"id": "R-browser"}]},
    )
    monkeypatch.setattr(
        reddit,
        "search_reddit",
        lambda *_args, **_kwargs: calls.append("scrapecreators")
        or {"items": [{"id": "R-paid"}]},
    )
    monkeypatch.setattr(
        "lib.service_source_policy.shutil.which", lambda name: f"/bin/{name}"
    )

    result = service_acquisition_worker._reddit_adapter(
        _request(source="reddit", adapter="reddit_api", work_id="work-order"),
        {
            "LAST30DAYS_SERVICE_SOURCES": "reddit",
            "LAST30DAYS_REDDIT_ACCESS_ORDER": "agent_browser,keyless",
            "SCRAPECREATORS_API_KEY": "dummy-test-key",
        },
    )

    assert result == {
        "items": [{"id": "R-browser"}],
        "_network_request_count": 1,
        "_cost_cents": 0,
        "diagnostics": {
            "attempted_access_methods": ["agent_browser"],
            "selected_access_method": "agent_browser",
        },
    }
    assert calls == ["agent_browser"]


def test_reddit_adapter_preserves_browser_failure_without_paid_fallback(monkeypatch):
    from lib import reddit_browser, reddit_public

    monkeypatch.setattr(reddit_public, "search_reddit_public", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(
        reddit_browser,
        "search_reddit_browser",
        lambda *_args, **_kwargs: {
            "items": [],
            "error": "Reddit returned a challenge page",
            "error_type": "checkpoint_required",
        },
    )

    result = service_acquisition_worker._reddit_adapter(
        _request(source="reddit", adapter="reddit_api", work_id="work-reddit-browser-fail"),
        {"LAST30DAYS_REDDIT_BROWSER": "true"},
    )

    assert result["items"] == []
    assert result["error_type"] == "checkpoint_required"
    assert result["_network_request_count"] == 1
    assert result["_cost_cents"] == 0


def test_reddit_adapter_uses_paid_fallback_after_empty_browser_yield(monkeypatch):
    from lib import reddit, reddit_browser, reddit_public

    monkeypatch.setattr(reddit_public, "search_reddit_public", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(
        reddit_browser,
        "search_reddit_browser",
        lambda *_args, **_kwargs: {"items": [], "error_type": "extraction_empty"},
    )
    paid_calls = []
    monkeypatch.setattr(
        reddit,
        "search_reddit",
        lambda *_args, **_kwargs: paid_calls.append(True) or {"items": [{"id": "RP1"}]},
    )

    result = service_acquisition_worker._reddit_adapter(
        _request(source="reddit", adapter="reddit_api", work_id="work-reddit-paid"),
        {
            "LAST30DAYS_REDDIT_BROWSER": "true",
            "SCRAPECREATORS_API_KEY": "dummy-test-key",
        },
    )

    assert result == {
        "items": [{"id": "RP1"}],
        "_network_request_count": 1,
        "diagnostics": {
            "browser_fallback": {
                "error_type": "extraction_empty",
                "failure_stage": "adapter_result",
            },
            "attempted_access_methods": [
                "keyless",
                "agent_browser",
                "scrapecreators",
            ],
            "selected_access_method": "scrapecreators",
        },
        "_cost_cents": 1,
    }
    assert paid_calls == [True]


def test_reddit_paid_fallback_preserves_typed_browser_outcome_without_raw_error(
    monkeypatch,
):
    from lib import reddit, reddit_browser, reddit_public

    monkeypatch.setattr(reddit_public, "search_reddit_public", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(
        reddit_browser,
        "search_reddit_browser",
        lambda *_args, **_kwargs: {
            "items": [],
            "error": "raw challenge page text must not survive",
            "error_type": "checkpoint_required",
            "diagnostics": {"failure_stage": "navigation", "raw_dom": "secret"},
        },
    )
    monkeypatch.setattr(
        reddit,
        "search_reddit",
        lambda *_args, **_kwargs: {"items": [{"id": "RP1"}]},
    )

    result = service_acquisition_worker._reddit_adapter(
        _request(source="reddit", adapter="reddit_api", work_id="work-reddit-audit"),
        {
            "LAST30DAYS_REDDIT_BROWSER": "true",
            "SCRAPECREATORS_API_KEY": "dummy-test-key",
        },
    )

    assert result["items"] == [{"id": "RP1"}]
    assert result["diagnostics"]["browser_fallback"] == {
        "error_type": "checkpoint_required",
        "failure_stage": "navigation",
    }
    assert "raw challenge" not in repr(result)
    assert "raw_dom" not in repr(result)


def test_zero_network_budget_rejects_work_before_adapter_call():
    calls = []

    result = execute_work(
        _request(network_request_limit=0),
        {},
        adapters={
            "x_agent_browser": lambda _request, _config: calls.append(True)
        },
    )

    assert calls == []
    assert result.status is contracts.AcquisitionStatus.FAILED
    assert result.safe_error_code == "network_budget_exhausted"
    assert result.retry_class is contracts.RetryClass.PERMANENT
