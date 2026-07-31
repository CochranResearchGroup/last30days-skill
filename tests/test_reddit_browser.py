from __future__ import annotations

from datetime import datetime, timezone

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
        self.command_timings = []

    def acquire_workspace(self, _request):
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
            },
        }
    ]
    assert client.actions[0].operation == "new_tab"


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


def test_search_url_is_encoded_and_bounded_to_posts():
    assert reddit_browser.search_url("open claw & agents") == (
        "https://www.reddit.com/search/?q=open+claw+%26+agents&type=posts&sort=new&t=month"
    )
