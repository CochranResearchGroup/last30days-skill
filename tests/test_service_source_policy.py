"""User-scoped service source and access-order policy tests."""

import pytest

from lib.service_source_policy import (
    ServiceSourcePolicyError,
    load_service_source_policy,
)


def _which(name: str) -> str | None:
    return f"/usr/bin/{name}" if name in {"agent-browser", "yt-dlp"} else None


def test_explicit_source_catalog_and_access_orders_are_preserved():
    config = {
        "LAST30DAYS_SERVICE_SOURCES": "reddit,x,youtube",
        "LAST30DAYS_REDDIT_ACCESS_ORDER": "keyless,agent_browser",
        "LAST30DAYS_X_ACCESS_ORDER": "agent_browser",
        "LAST30DAYS_YOUTUBE_ACCESS_ORDER": "yt_dlp",
    }

    policy = load_service_source_policy(config)

    assert policy.sources == ("reddit", "x", "youtube")
    assert policy.access_order("reddit") == ("keyless", "agent_browser")
    assert policy.source_ready("reddit", config, which=_which) is True
    assert policy.source_ready("x", config, which=_which) is True
    assert policy.source_ready("youtube", config, which=_which) is True


@pytest.mark.parametrize(
    ("config", "message"),
    [
        ({"LAST30DAYS_SERVICE_SOURCES": "reddit,reddit"}, "duplicate"),
        ({"LAST30DAYS_SERVICE_SOURCES": "reddit,unknown"}, "unsupported source"),
        (
            {
                "LAST30DAYS_SERVICE_SOURCES": "reddit",
                "LAST30DAYS_REDDIT_ACCESS_ORDER": "keyless,keyless",
            },
            "duplicate",
        ),
        (
            {
                "LAST30DAYS_SERVICE_SOURCES": "reddit",
                "LAST30DAYS_REDDIT_ACCESS_ORDER": "yt_dlp",
            },
            "unsupported method",
        ),
        (
            {
                "LAST30DAYS_SERVICE_SOURCES": "reddit",
                "LAST30DAYS_REDDIT_ACCESS_ORDER": "",
            },
            "must not be empty",
        ),
    ],
)
def test_invalid_source_policy_fails_closed(config, message):
    with pytest.raises(ServiceSourcePolicyError, match=message):
        load_service_source_policy(config)


def test_explicit_browser_order_is_the_enablement_and_tool_is_still_required():
    config = {
        "LAST30DAYS_SERVICE_SOURCES": "facebook",
        "LAST30DAYS_FACEBOOK_ACCESS_ORDER": "agent_browser",
    }
    policy = load_service_source_policy(config)

    assert policy.source_ready("facebook", config, which=_which) is True
    assert policy.source_ready("facebook", config, which=lambda _name: None) is False


def test_legacy_defaults_preserve_browser_opt_in_and_reddit_paid_tail():
    config = {
        "LAST30DAYS_REDDIT_BROWSER": "1",
        "LAST30DAYS_X_BROWSER": "1",
        "SCRAPECREATORS_API_KEY": "dummy-test-key",
    }
    policy = load_service_source_policy(config)

    assert policy.access_order("reddit") == (
        "keyless",
        "agent_browser",
        "scrapecreators",
    )
    assert policy.source_ready("x", config, which=_which) is True
    assert policy.source_ready("facebook", config, which=_which) is False
