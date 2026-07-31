"""Typed source-adapter boundary tests for the isolated worker process."""

from pathlib import Path

from lib import service_contracts as contracts
from lib import service_acquisition_worker
from lib.service_acquisition_worker import execute_work, load_profile_config


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
    def fake_adapter(_request, _config):
        return {
            "items": [],
            "error": "login required at a private operator URL",
            "error_type": "auth_required",
            "operator_url": "https://operator.example/private",
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
    assert "operator.example" not in str(serialized)
    assert "secret-session" not in str(serialized)
    assert "secret-route" not in str(serialized)


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
