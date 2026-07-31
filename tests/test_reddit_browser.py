from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys

import pytest

from lib import reddit_browser
from lib.facebook import BrowserState, BrowserWorkspace


class FakeClient:
    def __init__(self, *, page=None, extracts=None):
        self.page = page or {
            "url": "https://www.reddit.com/search/?q=openclaw&type=posts&sort=new&t=month",
            "title": "openclaw - Reddit Search!",
            "has_posts": True,
        }
        self.extracts = list(extracts or [])
        self.actions = []
        self.requests = []
        self.command_timings = []

    def acquire_workspace(self, request):
        self.requests.append(request)
        return BrowserWorkspace(
            profile_id="last30days-facebook",
            browser_id="browser-1",
            session_name="last30days-reddit",
            target_id="target-1",
        )

    def prepare_site_tab(self, _workspace, _hostname, *, consolidate=False):
        return False

    def act(self, _workspace, action):
        self.actions.append(action)
        return BrowserState(url=action.value if action.operation in {"navigate", "new_tab"} else "")

    def evaluate(self, _workspace, script):
        if script == reddit_browser.PAGE_STATE_SCRIPT:
            return self.page
        return {"candidates": self.extracts}


def _scraper(client, *, limit=3):
    return reddit_browser.RedditBrowserScraper(
        client,
        reddit_browser.browser_request(
            {
                "LAST30DAYS_REDDIT_BROWSER_PROFILE": "last30days-facebook",
                "LAST30DAYS_REDDIT_BROWSER_SESSION": "last30days-reddit",
            },
            timeout=30,
        ),
        limit=limit,
        scrolls=0,
        initial_wait=0,
        scroll_wait=0,
        now=datetime(2026, 7, 31, 12, 0, tzinfo=timezone.utc),
    )


def test_search_normalizes_filters_deduplicates_and_limits_posts():
    client = FakeClient(
        extracts=[
            {
                "title": "OpenClaw agent browser workflow",
                "text": "A reliable OpenClaw workflow for fetching Reddit posts.",
                "permalink": "/r/LocalLLaMA/comments/abc123/openclaw_agent_browser_workflow/",
                "author": "example_author",
                "subreddit": "r/LocalLLaMA",
                "created_at": "2026-07-30T09:15:00.000Z",
                "score": "1.2k",
                "comment_count": "34 comments",
                "dom_shape": "shreddit-post",
                "crosspost": False,
            },
            {
                "title": "Duplicate OpenClaw result",
                "permalink": "https://www.reddit.com/r/LocalLLaMA/comments/abc123/duplicate/",
                "created_at": "2026-07-30T10:00:00Z",
            },
            {
                "title": "OpenClaw history",
                "permalink": "/r/test/comments/old999/history/",
                "created_at": "2026-06-01T00:00:00Z",
            },
            {
                "title": "Unrelated cooking thread",
                "text": "A sourdough recipe.",
                "permalink": "/r/cooking/comments/nope01/recipe/",
                "created_at": "2026-07-30T00:00:00Z",
            },
        ]
    )

    result = _scraper(client).search("openclaw", "2026-07-01", "2026-07-31")

    assert result["error_type"] is None
    assert result["diagnostics"]["accepted_count"] == 1
    assert result["diagnostics"]["rejection_counts"] == {
        "duplicate": 1,
        "outside_date_range": 1,
        "off_topic": 1,
    }
    assert result["items"] == [
        {
            "id": "Rabc123",
            "reddit_id": "abc123",
            "title": "OpenClaw agent browser workflow",
            "text": "A reliable OpenClaw workflow for fetching Reddit posts.",
            "url": "https://www.reddit.com/r/LocalLLaMA/comments/abc123/openclaw_agent_browser_workflow/",
            "author": "example_author",
            "subreddit": "LocalLLaMA",
            "date": "2026-07-30",
            "score": 1200,
            "num_comments": 34,
            "relevance": 1.0,
            "why_relevant": "Reddit post: OpenClaw agent browser workflow",
            "metadata": {
                "extraction": "agent-browser-dom-v1",
                "remote_browser": True,
                "published_at": "2026-07-30T09:15:00+00:00",
                "dom_shape": "shreddit-post",
                "crosspost": False,
            },
        }
    ]
    assert client.actions[0].operation == "new_tab"
    assert client.requests[0].service_name == "last30days"
    assert client.requests[0].agent_name == "reddit-scraper"
    assert client.requests[0].task_name == "reddit-post-search"
    assert client.requests[0].target_service_id == "reddit"
    assert client.requests[0].display_isolation == "private_virtual_display"


def test_multiword_search_rejects_one_term_matches_and_keeps_full_coverage():
    client = FakeClient(
        page={
            "url": "https://www.reddit.com/search/?q=Claude+Code&type=posts&sort=new&t=month",
            "title": "Claude Code - Reddit Search!",
            "query_value": "Claude Code",
            "has_posts": True,
        },
        extracts=[
            {
                "title": "Why bundled HTMLs from Claude Design?",
                "permalink": "/r/ClaudeAI/comments/claude1/design/",
                "subreddit": "r/ClaudeAI",
                "created_at": "2026-07-30T09:15:00Z",
            },
            {
                "title": "Minimalism from Visual Studio to VS Code",
                "permalink": "/r/programming/comments/code001/minimalism/",
                "subreddit": "r/programming",
                "created_at": "2026-07-30T09:16:00Z",
            },
            {
                "title": "Claude workflows for writing Code safely",
                "permalink": "/r/ClaudeAI/comments/full001/workflow/",
                "subreddit": "r/ClaudeAI",
                "created_at": "2026-07-30T09:17:00Z",
            },
        ]
    )

    result = _scraper(client).search("Claude Code", "2026-07-01", "2026-07-31")

    assert result["error_type"] is None
    assert [item["reddit_id"] for item in result["items"]] == ["full001"]
    assert result["diagnostics"]["rejection_counts"] == {
        "partial_query_match": 2
    }


def test_agent_browser_query_requires_both_terms_across_title_and_body():
    client = FakeClient(
        page={
            "url": "https://www.reddit.com/search/?q=agent+browser&type=posts&sort=new&t=month",
            "title": "agent browser - Reddit Search!",
            "query_value": "agent browser",
            "has_posts": True,
        },
        extracts=[
            {
                "title": "A coding agent writes documentation",
                "permalink": "/r/agents/comments/agent01/docs/",
                "subreddit": "r/agents",
                "created_at": "2026-07-30T09:15:00Z",
            },
            {
                "title": "Browser performance improvements",
                "permalink": "/r/browsers/comments/browser1/performance/",
                "subreddit": "r/browsers",
                "created_at": "2026-07-30T09:16:00Z",
            },
            {
                "title": "An agent workflow",
                "text": "The browser provides the controlled interface.",
                "permalink": "/r/agents/comments/both001/workflow/",
                "subreddit": "r/agents",
                "created_at": "2026-07-30T09:17:00Z",
            },
        ],
    )

    result = _scraper(client).search("agent browser", "2026-07-01", "2026-07-31")

    assert [item["reddit_id"] for item in result["items"]] == ["both001"]
    assert result["diagnostics"]["rejection_counts"] == {
        "partial_query_match": 2
    }


def test_only_partial_multiword_matches_return_a_typed_quality_failure():
    client = FakeClient(
        page={
            "url": "https://www.reddit.com/search/?q=Claude+Code&type=posts&sort=new&t=month",
            "title": "Claude Code - Reddit Search!",
            "query_value": "Claude Code",
            "has_posts": True,
        },
        extracts=[
            {
                "title": "Claude Design workflow",
                "permalink": "/r/ClaudeAI/comments/partial1/design/",
                "subreddit": "r/ClaudeAI",
                "created_at": "2026-07-30T09:15:00Z",
            },
            {
                "title": "VS Code configuration",
                "permalink": "/r/programming/comments/partial2/config/",
                "subreddit": "r/programming",
                "created_at": "2026-07-30T09:16:00Z",
            },
        ],
    )

    result = _scraper(client).search("Claude Code", "2026-07-01", "2026-07-31")

    assert result["items"] == []
    assert result["error_type"] == "quality_gate_failed"
    assert result["diagnostics"]["rejection_counts"] == {
        "partial_query_match": 2
    }


def test_rate_limit_page_returns_typed_failure_without_extracting():
    client = FakeClient(
        page={
            "url": "https://www.reddit.com/search/?q=openclaw",
            "title": "Whoa there, pardner!",
            "rate_limited": True,
            "rate_limit_reason": "whoa_there",
        }
    )

    result = _scraper(client).search("openclaw", "2026-07-01", "2026-07-31")

    assert result["items"] == []
    assert result["error_type"] == "rate_limit_detected"
    assert result["diagnostics"]["failure_stage"] == "navigation"


def test_empty_verified_search_is_not_reported_as_successful_negative_coverage():
    result = _scraper(FakeClient(extracts=[])).search(
        "openclaw", "2026-07-01", "2026-07-31"
    )

    assert result["items"] == []
    assert result["error_type"] == "extraction_empty"


def test_explicit_no_results_page_is_distinguished_from_an_empty_extraction():
    client = FakeClient(
        page={
            "url": "https://www.reddit.com/search/?q=openclaw&type=posts",
            "title": "openclaw - Reddit Search!",
            "no_results": True,
            "has_posts": False,
        }
    )

    result = _scraper(client).search("openclaw", "2026-07-01", "2026-07-31")

    assert result["items"] == []
    assert result["error_type"] is None
    assert result["diagnostics"]["verified_no_results"] is True
    assert [action.operation for action in client.actions] == ["new_tab", "wait"]


def test_invalid_or_missing_timestamp_cannot_be_accepted_as_an_in_range_post():
    client = FakeClient(
        extracts=[
            {
                "title": "OpenClaw invalid timestamp",
                "permalink": "/r/agents/comments/badtime/invalid_timestamp/",
                "subreddit": "r/agents",
                "created_at": "not-a-timestamp",
            },
            {
                "title": "OpenClaw missing timestamp",
                "permalink": "/r/agents/comments/notime/missing_timestamp/",
                "subreddit": "r/agents",
            },
        ]
    )

    result = _scraper(client).search("openclaw", "2026-07-01", "2026-07-31")

    assert result["items"] == []
    assert result["error_type"] == "quality_gate_failed"
    assert result["diagnostics"]["rejection_counts"] == {"invalid_timestamp": 2}


def test_invalid_duplicate_does_not_suppress_a_later_valid_post():
    client = FakeClient(
        extracts=[
            {
                "title": "OpenClaw malformed first copy",
                "permalink": "/r/agents/comments/same01/malformed/",
                "subreddit": "r/agents",
                "created_at": "not-a-timestamp",
            },
            {
                "title": "OpenClaw valid later copy",
                "permalink": "/r/agents/comments/same01/valid/",
                "subreddit": "r/agents",
                "created_at": "2026-07-30T09:15:00Z",
            },
        ]
    )

    result = _scraper(client).search("openclaw", "2026-07-01", "2026-07-31")

    assert result["error_type"] is None
    assert [item["reddit_id"] for item in result["items"]] == ["same01"]
    assert result["diagnostics"]["rejection_counts"] == {"invalid_timestamp": 1}


def test_promoted_post_units_are_rejected_before_normalization():
    client = FakeClient(
        extracts=[
            {
                "title": "OpenClaw sponsored agent platform",
                "permalink": "/r/agents/comments/ad1234/sponsored/",
                "subreddit": "r/agents",
                "created_at": "2026-07-30T09:15:00Z",
                "promoted": True,
            }
        ]
    )

    result = _scraper(client).search("openclaw", "2026-07-01", "2026-07-31")

    assert result["items"] == []
    assert result["error_type"] == "quality_gate_failed"
    assert result["diagnostics"]["rejection_counts"] == {"promoted": 1}


def test_post_without_a_title_is_rejected_even_when_body_is_relevant():
    client = FakeClient(
        extracts=[
            {
                "title": "",
                "text": "OpenClaw agent browser details",
                "permalink": "/r/agents/comments/notitle/missing_title/",
                "subreddit": "r/agents",
                "created_at": "2026-07-30T09:15:00Z",
            }
        ]
    )

    result = _scraper(client).search("openclaw", "2026-07-01", "2026-07-31")

    assert result["items"] == []
    assert result["error_type"] == "quality_gate_failed"
    assert result["diagnostics"]["rejection_counts"] == {"missing_title": 1}


@pytest.mark.parametrize(
    "permalink",
    [
        "https://example.com/r/agents/comments/ext123/post/",
        "/r/agents/post-without-comments-id/",
        "javascript:alert(1)",
    ],
)
def test_malformed_or_non_reddit_permalink_is_rejected(permalink):
    client = FakeClient(
        extracts=[
            {
                "title": "OpenClaw invalid permalink",
                "permalink": permalink,
                "subreddit": "r/agents",
                "created_at": "2026-07-30T09:15:00Z",
            }
        ]
    )

    result = _scraper(client).search("openclaw", "2026-07-01", "2026-07-31")

    assert result["items"] == []
    assert result["diagnostics"]["rejection_counts"] == {"invalid_permalink": 1}


def test_old_reddit_permalink_is_canonicalized_and_tracking_query_is_removed():
    client = FakeClient(
        extracts=[
            {
                "title": "OpenClaw canonical URL",
                "permalink": "https://old.reddit.com/r/agents/comments/canon1/post/?utm_source=test#fragment",
                "subreddit": "r/agents",
                "created_at": "2026-07-30T09:15:00Z",
            }
        ]
    )

    result = _scraper(client).search("openclaw", "2026-07-01", "2026-07-31")

    assert result["items"][0]["url"] == (
        "https://www.reddit.com/r/agents/comments/canon1/post/"
    )


def test_article_fallback_derives_subreddit_from_the_canonical_permalink():
    client = FakeClient(
        extracts=[
            {
                "title": "OpenClaw article fallback",
                "text": "OpenClaw agent browser details",
                "permalink": "/r/agents/comments/fallback/article_fallback/",
                "created_at": "2026-07-30T09:15:00Z",
                "score": "Vote",
                "comment_count": "hidden",
            }
        ]
    )

    result = _scraper(client).search("openclaw", "2026-07-01", "2026-07-31")

    assert result["error_type"] is None
    assert result["items"][0]["subreddit"] == "agents"
    assert result["items"][0]["score"] == 0
    assert result["items"][0]["num_comments"] == 0


@pytest.mark.parametrize(
    ("score", "comments", "expected_score", "expected_comments"),
    [
        ("123", "45", 123, 45),
        ("1,234", "5,678 comments", 1234, 5678),
        ("1.2K", "2.5k", 1200, 2500),
        ("1.5M", "2m", 1_500_000, 2_000_000),
        ("Vote", "hidden", 0, 0),
        ("", None, 0, 0),
    ],
)
def test_engagement_forms_are_normalized_to_nonnegative_integers(
    score, comments, expected_score, expected_comments
):
    client = FakeClient(
        extracts=[
            {
                "title": "OpenClaw engagement metrics",
                "permalink": "/r/agents/comments/count01/metrics/",
                "subreddit": "r/agents",
                "created_at": "2026-07-30T09:15:00Z",
                "score": score,
                "comment_count": comments,
            }
        ]
    )

    result = _scraper(client).search("openclaw", "2026-07-01", "2026-07-31")

    assert result["error_type"] is None
    assert result["items"][0]["score"] == expected_score
    assert result["items"][0]["num_comments"] == expected_comments


@pytest.mark.parametrize(
    ("timestamp", "accepted"),
    [
        ("2026-07-01T00:00:00Z", True),
        ("2026-07-31T23:59:59Z", True),
        ("2026-07-01T01:30:00+02:00", False),
        ("2026-08-01T01:30:00+02:00", True),
    ],
)
def test_date_range_is_inclusive_after_utc_offset_normalization(timestamp, accepted):
    client = FakeClient(
        extracts=[
            {
                "title": "OpenClaw UTC boundary",
                "permalink": "/r/agents/comments/date01/boundary/",
                "subreddit": "r/agents",
                "created_at": timestamp,
            }
        ]
    )

    result = _scraper(client).search("openclaw", "2026-07-01", "2026-07-31")

    assert bool(result["items"]) is accepted
    assert result["error_type"] == (None if accepted else "quality_gate_failed")


@pytest.mark.parametrize(
    "dom_shape", ["search-post-unit", "shreddit-post", "article-permalink"]
)
def test_supported_dom_shape_is_preserved_as_bounded_extraction_evidence(dom_shape):
    client = FakeClient(
        extracts=[
            {
                "title": "OpenClaw DOM shape",
                "permalink": f"/r/agents/comments/{dom_shape.replace('-', '')}/shape/",
                "subreddit": "r/agents",
                "created_at": "2026-07-30T09:15:00Z",
                "dom_shape": dom_shape,
            }
        ]
    )

    result = _scraper(client).search("openclaw", "2026-07-01", "2026-07-31")

    assert result["error_type"] is None
    assert result["items"][0]["metadata"]["dom_shape"] == dom_shape


def test_crosspost_with_unicode_title_deleted_author_and_missing_body_is_preserved():
    client = FakeClient(
        page={
            "url": "https://www.reddit.com/search/?q=Caf%C3%A9+agents&type=posts",
            "query_value": "Café agents",
            "has_posts": True,
        },
        extracts=[
            {
                "title": "Café agents — OpenClaw?!",
                "text": "",
                "permalink": "/r/agents/comments/unicode1/cafe_agents/",
                "subreddit": "r/agents",
                "author": "[deleted]",
                "created_at": "2026-07-30T09:15:00Z",
                "crosspost": True,
                "dom_shape": "shreddit-post",
            }
        ]
    )

    result = _scraper(client).search(
        "Café agents", "2026-07-01", "2026-07-31"
    )

    assert result["error_type"] is None
    assert result["items"][0]["title"] == "Café agents — OpenClaw?!"
    assert result["items"][0]["text"] == ""
    assert result["items"][0]["author"] == "[deleted]"
    assert result["items"][0]["metadata"]["crosspost"] is True


@pytest.mark.parametrize(
    ("page", "error_type"),
    [
        ({"url": "https://www.reddit.com/login/", "login_page": True}, "auth_required"),
        (
            {"url": "https://www.reddit.com/search/?q=openclaw", "checkpoint": True},
            "checkpoint_required",
        ),
        (
            {"url": "https://www.reddit.com/search/?q=openclaw", "error_page": True},
            "search_unavailable",
        ),
        (
            {"url": "https://www.reddit.com/search/?q=openclaw", "interstitial": True},
            "interstitial_detected",
        ),
        (
            {"url": "https://example.com/search/?q=openclaw"},
            "navigation_mismatch",
        ),
    ],
)
def test_browser_page_failures_are_typed(page, error_type):
    result = _scraper(FakeClient(page=page)).search(
        "openclaw", "2026-07-01", "2026-07-31"
    )

    assert result["items"] == []
    assert result["error_type"] == error_type


def test_malformed_extraction_is_a_typed_browser_failure():
    class MalformedClient(FakeClient):
        def evaluate(self, _workspace, script):
            if script == reddit_browser.PAGE_STATE_SCRIPT:
                return self.page
            return {"candidates": "not-a-list"}

    result = _scraper(MalformedClient()).search(
        "openclaw", "2026-07-01", "2026-07-31"
    )

    assert result["items"] == []
    assert result["error_type"] == "agent_browser_error"


def test_oversized_candidate_array_is_capped_before_quality_processing():
    extracts = [
        {
            "title": f"OpenClaw result {index}",
            "permalink": f"/r/agents/comments/over{index}/post/",
            "subreddit": "r/agents",
            "created_at": "2026-07-30T09:15:00Z",
        }
        for index in range(1000)
    ]

    result = _scraper(FakeClient(extracts=extracts)).search(
        "openclaw", "2026-07-01", "2026-07-31"
    )

    assert result["error_type"] is None
    assert result["diagnostics"]["candidate_count"] == 80
    assert len(result["items"]) == 3


def test_agent_browser_timeout_is_terminal_and_preserves_the_failure_stage():
    class TimeoutClient(FakeClient):
        def acquire_workspace(self, _request):
            from lib.facebook import FacebookScraperFailure

            raise FacebookScraperFailure(
                "agent_browser_timeout", "agent-browser operation timed out after 30s"
            )

    result = _scraper(TimeoutClient()).search(
        "openclaw", "2026-07-01", "2026-07-31"
    )

    assert result["items"] == []
    assert result["error_type"] == "agent_browser_timeout"
    assert result["diagnostics"]["failure_stage"] == "workspace_acquisition"


@pytest.mark.parametrize(
    "error_type",
    ["agent_browser_error", "agent_browser_timeout", "profile_mismatch", "route_stale"],
)
def test_workspace_crash_timeout_profile_conflict_and_stale_route_are_terminal(
    error_type,
):
    class FailingClient(FakeClient):
        def acquire_workspace(self, _request):
            from lib.facebook import FacebookScraperFailure

            raise FacebookScraperFailure(error_type, "bounded synthetic failure")

    result = _scraper(FailingClient()).search(
        "openclaw", "2026-07-01", "2026-07-31"
    )

    assert result["items"] == []
    assert result["error_type"] == error_type
    assert result["diagnostics"]["failure_stage"] == "workspace_acquisition"


def test_missing_agent_browser_binary_returns_typed_result_without_constructing_client(
    monkeypatch,
):
    monkeypatch.setattr(reddit_browser.shutil, "which", lambda _name: None)

    result = reddit_browser.search_reddit_browser(
        "openclaw", "2026-07-01", "2026-07-31", depth="quick"
    )

    assert result == {
        "items": [],
        "error": "agent-browser command is not on PATH",
        "error_type": "agent_browser_missing",
    }


def test_search_url_is_encoded_and_bounded_to_posts():
    assert reddit_browser.search_url("open claw & agents") == (
        "https://www.reddit.com/search/?q=open+claw+%26+agents&type=posts&sort=new&t=month"
    )


def test_quick_depth_configuration_cannot_exceed_time_scroll_or_result_ceilings(
    monkeypatch,
):
    extracts = [
        {
            "title": f"OpenClaw bounded result {index}",
            "permalink": f"/r/agents/comments/bound{index}/bounded/",
            "subreddit": "r/agents",
            "created_at": "2026-07-30T09:15:00Z",
        }
        for index in range(5)
    ]
    client = FakeClient(extracts=extracts)
    monkeypatch.setattr(reddit_browser.shutil, "which", lambda _name: "/fake/agent-browser")
    monkeypatch.setattr(reddit_browser, "CliAgentBrowserClient", lambda *, timeout: client)

    result = reddit_browser.search_reddit_browser(
        "openclaw",
        "2026-07-01",
        "2026-07-31",
        depth="quick",
        config={
            "LAST30DAYS_REDDIT_BROWSER_TIMEOUT": "999",
            "LAST30DAYS_REDDIT_BROWSER_MAX_RESULTS": "999",
            "LAST30DAYS_REDDIT_BROWSER_SCROLLS": "999",
            "LAST30DAYS_REDDIT_BROWSER_INITIAL_WAIT": "0",
            "LAST30DAYS_REDDIT_BROWSER_SCROLL_WAIT": "0",
        },
    )

    assert result["error_type"] is None
    assert len(result["items"]) == 3
    assert client.requests[0].timeout == 45
    assert [action.operation for action in client.actions].count("scroll") == 0


@pytest.mark.parametrize(
    ("depth", "timeout", "scrolls"),
    [("quick", 45, 0), ("default", 75, 1), ("deep", 110, 2)],
)
def test_each_depth_enforces_its_own_timeout_and_scroll_ceiling(
    monkeypatch, depth, timeout, scrolls
):
    client = FakeClient(
        extracts=[
            {
                "title": "OpenClaw bounded depth",
                "permalink": "/r/agents/comments/depth01/bounded/",
                "subreddit": "r/agents",
                "created_at": "2026-07-30T09:15:00Z",
            }
        ]
    )
    monkeypatch.setattr(reddit_browser.shutil, "which", lambda _name: "/fake/agent-browser")
    monkeypatch.setattr(reddit_browser, "CliAgentBrowserClient", lambda *, timeout: client)

    result = reddit_browser.search_reddit_browser(
        "openclaw",
        "2026-07-01",
        "2026-07-31",
        depth=depth,
        config={
            "LAST30DAYS_REDDIT_BROWSER_TIMEOUT": "999",
            "LAST30DAYS_REDDIT_BROWSER_SCROLLS": "999",
            "LAST30DAYS_REDDIT_BROWSER_INITIAL_WAIT": "0",
            "LAST30DAYS_REDDIT_BROWSER_SCROLL_WAIT": "0",
        },
    )

    assert result["error_type"] is None
    assert client.requests[0].timeout == timeout
    assert [action.operation for action in client.actions].count("scroll") == scrolls


def _install_fake_agent_browser(tmp_path: Path, monkeypatch, *, scenario="new") -> Path:
    executable = tmp_path / "agent-browser"
    log_path = tmp_path / "commands.jsonl"
    executable.write_text(
        f"#!{sys.executable}\n"
        + r'''import json
import os
import sys
import time

log_path = os.environ["FAKE_AGENT_BROWSER_LOG"]
try:
    with open(log_path, encoding="utf-8") as handle:
        prior = [json.loads(line) for line in handle if line.strip()]
except FileNotFoundError:
    prior = []
args = sys.argv[1:]
with open(log_path, "a", encoding="utf-8") as handle:
    handle.write(json.dumps(args) + "\n")
index = len(prior)
if os.environ.get("FAKE_AGENT_BROWSER_SLEEP_AT") == str(index):
    time.sleep(5)
if os.environ.get("FAKE_AGENT_BROWSER_FAIL_AT") == str(index):
    print("Authorization: Bearer secret-token-123 private@example.test", file=sys.stderr)
    raise SystemExit(17)
if os.environ.get("FAKE_AGENT_BROWSER_MALFORMED_AT") == str(index):
    print("{malformed")
    raise SystemExit(0)

scenario = os.environ.get("FAKE_AGENT_BROWSER_SCENARIO", "new")
if args[1:3] == ["service", "access-plan"]:
    data = {
        "selectedProfile": {"id": "last30days-facebook"},
        "decision": {"launchPosture": {"remoteViewRecommended": True}},
    }
elif args[1:3] == ["service", "status"]:
    if scenario == "retained":
        data = {"service_state": {
            "sessions": {"last30days-reddit": {
                "profileId": "last30days-facebook",
                "browserIds": ["browser-retained"],
                "tabIds": ["target:retained"],
            }},
            "browsers": {"browser-retained": {
                "health": "ready",
                "profileId": "last30days-facebook",
                "viewStreams": [{
                    "provider": "rdp_gateway",
                    "readiness": {"state": "ready"},
                    "id": "guacamole:retained",
                }],
            }},
            "tabs": {"target:retained": {
                "targetId": "retained",
                "url": "https://www.reddit.com/search/?q=old",
            }},
        }}
    elif scenario == "unrelated":
        data = {"service_state": {
            "sessions": {"last30days-reddit": {
                "profileId": "unrelated-profile",
                "browserIds": ["browser-unrelated"],
            }},
            "browsers": {"browser-unrelated": {
                "health": "ready", "profileId": "unrelated-profile"
            }},
            "tabs": {},
        }}
    else:
        data = {"service_state": {"sessions": {}, "browsers": {}, "tabs": {}}}
elif "remote-view" in args and "open" in args:
    session = args[args.index("--session") + 1]
    data = {
        "profileId": "last30days-facebook",
        "browserId": "browser-new",
        "sessionName": session,
        "targetId": "target-new",
        "routeId": "guacamole:new",
        "operatorVisible": {"state": "ready"},
    }
elif args[-2:] == ["tab", "list"]:
    tabs = [] if scenario != "retained" else [{
        "index": 0,
        "active": True,
        "url": "https://www.reddit.com/search/?q=old",
    }]
    data = {"tabs": tabs}
elif "eval" in args:
    eval_number = sum("eval" in previous for previous in prior)
    if eval_number == 0:
        data = {"result": {
            "url": "https://www.reddit.com/search/?q=openclaw&type=posts&sort=new&t=month",
            "title": "openclaw - Reddit Search!",
            "query_value": "openclaw",
            "has_posts": True,
        }}
    else:
        data = {"result": {"candidates": [{
            "title": "OpenClaw browser routine",
            "permalink": "/r/agents/comments/cli001/browser_routine/",
            "subreddit": "r/agents",
            "created_at": "2026-07-30T09:15:00Z",
            "score": "1.2K",
            "comment_count": "34",
            "dom_shape": "shreddit-post",
        }]}}
else:
    data = {"url": args[-1] if args else ""}
print(json.dumps({"success": True, "data": data}))
''',
        encoding="utf-8",
    )
    executable.chmod(0o755)
    monkeypatch.setenv("PATH", f"{tmp_path}{os.pathsep}{os.environ['PATH']}")
    monkeypatch.setenv("FAKE_AGENT_BROWSER_LOG", str(log_path))
    monkeypatch.setenv("FAKE_AGENT_BROWSER_SCENARIO", scenario)
    monkeypatch.setattr(
        reddit_browser.browser_runtime.agent_browser_config,
        "record_access_plan",
        lambda *_args, **_kwargs: tmp_path / "unused.json",
    )
    monkeypatch.setattr(reddit_browser.time, "sleep", lambda _seconds: None)
    return log_path


def _fake_cli_search():
    return reddit_browser.search_reddit_browser(
        "openclaw",
        "2026-07-01",
        "2026-07-31",
        depth="quick",
        config={
            "LAST30DAYS_REDDIT_BROWSER_INITIAL_WAIT": "0",
            "LAST30DAYS_REDDIT_BROWSER_SCROLL_WAIT": "0",
        },
    )


def _commands(log_path: Path) -> list[list[str]]:
    return [json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines()]


def test_fake_cli_exercises_the_real_subprocess_contract_in_bounded_order(
    tmp_path, monkeypatch
):
    log_path = _install_fake_agent_browser(tmp_path, monkeypatch)

    result = _fake_cli_search()

    commands = _commands(log_path)
    assert result["error_type"] is None
    assert [item["reddit_id"] for item in result["items"]] == ["cli001"]
    assert result["diagnostics"]["page_state"] == "posts"
    assert result["diagnostics"]["command_count"] == 7
    assert len(result["diagnostics"]["browser_operations"]) == 7
    assert [command[1:3] for command in commands[:2]] == [
        ["service", "access-plan"],
        ["service", "status"],
    ]
    assert "remote-view" in commands[2] and "open" in commands[2]
    assert commands[3][-2:] == ["tab", "list"]
    assert commands[4][-3:-1] == ["tab", "new"]
    assert commands[5][-2:] == ["eval", "--stdin"]
    assert commands[6][-2:] == ["eval", "--stdin"]
    assert len(commands) == 7
    access = commands[0]
    assert access[access.index("--target-service-id") + 1] == "reddit"
    assert access[access.index("--display-isolation") + 1] == "private_virtual_display"
    assert all(
        token.casefold() not in {"cdp", "process", "ps"}
        for command in commands
        for token in command
    )


def test_fake_cli_reuses_a_ready_retained_session_without_open_or_close(
    tmp_path, monkeypatch
):
    log_path = _install_fake_agent_browser(tmp_path, monkeypatch, scenario="retained")

    result = _fake_cli_search()

    commands = _commands(log_path)
    assert result["error_type"] is None
    assert result["workspace"]["browser_id"] == "browser-retained"
    assert not any("remote-view" in command or "close" in command for command in commands)
    assert all(
        command[command.index("--session") + 1] == "last30days-reddit"
        for command in commands
        if "--session" in command
    )


def test_fake_cli_does_not_replace_an_unrelated_named_session_owner(
    tmp_path, monkeypatch
):
    log_path = _install_fake_agent_browser(tmp_path, monkeypatch, scenario="unrelated")

    result = _fake_cli_search()

    commands = _commands(log_path)
    assert result["error_type"] is None
    assert not any("close" in command for command in commands)
    opened = next(command for command in commands if "remote-view" in command)
    assert opened[opened.index("--session") + 1] != "last30days-reddit"
    assert "last30days-facebook" in opened[opened.index("--session") + 1]


@pytest.mark.parametrize("failure_index", range(7))
def test_fake_cli_failure_at_each_command_boundary_is_terminal_and_redacted(
    tmp_path, monkeypatch, failure_index
):
    log_path = _install_fake_agent_browser(tmp_path, monkeypatch)
    monkeypatch.setenv("FAKE_AGENT_BROWSER_FAIL_AT", str(failure_index))

    result = _fake_cli_search()

    assert result["error_type"] == "agent_browser_error"
    assert "secret-token-123" not in str(result)
    assert "private@example.test" not in str(result)
    assert len(_commands(log_path)) == failure_index + 1


def test_fake_cli_malformed_json_is_terminal_without_follow_on_commands(
    tmp_path, monkeypatch
):
    log_path = _install_fake_agent_browser(tmp_path, monkeypatch)
    monkeypatch.setenv("FAKE_AGENT_BROWSER_MALFORMED_AT", "0")

    result = _fake_cli_search()

    assert result["error_type"] == "agent_browser_error"
    assert "malformed JSON" in result["error"]
    assert len(_commands(log_path)) == 1


def test_fake_cli_timeout_is_propagated_and_kills_the_command_fixture(
    tmp_path, monkeypatch
):
    log_path = _install_fake_agent_browser(tmp_path, monkeypatch)
    monkeypatch.setenv("FAKE_AGENT_BROWSER_SLEEP_AT", "0")

    result = reddit_browser.search_reddit_browser(
        "openclaw",
        "2026-07-01",
        "2026-07-31",
        depth="quick",
        config={"LAST30DAYS_REDDIT_BROWSER_TIMEOUT": "1"},
    )

    assert result["error_type"] == "agent_browser_timeout"
    assert "after 1s" in result["error"]
    assert len(_commands(log_path)) == 1
