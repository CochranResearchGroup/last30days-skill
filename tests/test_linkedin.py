import json
import os
from datetime import datetime, timezone
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from lib import linkedin, normalize, pipeline, render, schema


NOW = datetime(2026, 7, 15, 12, 0, tzinfo=timezone.utc)


def request(**overrides):
    values = {
        "profile_id": "last30days-linkedin",
        "session_name": "last30days-linkedin",
        "browser_build": "stealthcdp_chromium",
        "view_provider": "rdp_gateway",
        "timeout": 30,
    }
    values.update(overrides)
    return linkedin.BrowserWorkspaceRequest(**values)


def post_candidate(**overrides):
    values = {
        "text": (
            "AgriTech Lab\n"
            "We tested robotic lawn mower navigation in regenerative field plots "
            "and documented practical safety and soil-health observations."
        ),
        "url": "https://www.linkedin.com/feed/update/urn:li:activity:7351200000000000000/?trk=feed",
        "urn": "urn:li:activity:7351200000000000000",
        "author": "AgriTech Lab",
        "author_url": "https://www.linkedin.com/company/agritech-lab/",
        "timestamp": "2d • Edited",
        "sponsored": False,
        "engagement": {"likes": 17, "comments": 3, "shares": 1},
    }
    values.update(overrides)
    return values


class FakeAgentBrowserClient:
    def __init__(self, *, page=None, candidates=None, auth=None, preserve_url=False):
        self.workspace = linkedin.BrowserWorkspace(
            profile_id="last30days-linkedin",
            browser_id="browser-1",
            session_name="last30days-linkedin",
            target_id="target-1",
            route_id="route-1",
            operator_url="https://operator.example/opaque-token",
            operator_visible_state="ready",
        )
        self.auth = auth or linkedin.LinkedInAuthState(authenticated=True, has_li_at=True)
        self.page = page or {
            "url": linkedin._search_url("robotic lawn mower"),
            "title": "robotic lawn mower | Search | LinkedIn",
            "heading": "Search results for robotic lawn mower",
            "query_value": "robotic lawn mower",
            "has_content_filters": True,
            "has_content_cards": True,
            "no_results": False,
            "login_page": False,
            "checkpoint": False,
            "error_page": False,
        }
        self.candidates = candidates if candidates is not None else [post_candidate()]
        self.preserve_url = preserve_url
        self.actions = []
        self.command_timings = [{"operation": "eval", "duration_ms": 3, "status": "ok"}]
        self.ingress_ready = True

    def acquire_workspace(self, workspace_request):
        if workspace_request.profile_id != self.workspace.profile_id:
            raise linkedin.LinkedInScraperFailure("profile_mismatch", "wrong profile")
        return self.workspace

    def inspect_auth(self, workspace):
        return self.auth

    def snapshot(self, workspace):
        return linkedin.BrowserSnapshot()

    def act(self, workspace, action):
        self.actions.append(action)
        if action.operation == "new_tab" and action.value and not self.preserve_url:
            self.page["url"] = action.value
        return linkedin.BrowserState()

    def evaluate(self, workspace, script):
        if script == linkedin.PAGE_STATE_SCRIPT:
            return dict(self.page)
        if script == linkedin.EXTRACT_SCRIPT:
            return {
                "url": self.page["url"],
                "title": self.page["title"],
                "candidates": self.candidates,
            }
        raise AssertionError("unexpected script")

    def operator_ingress_ready(self, operator_url):
        return self.ingress_ready


def make_scraper(client, **overrides):
    values = {"limit": 20, "scrolls": 0, "initial_wait": 0, "scroll_wait": 0, "now": NOW}
    values.update(overrides)
    return linkedin.LinkedInScraper(client, request(), **values)


class LinkedInAvailabilityTests(unittest.TestCase):
    def test_linkedin_is_not_available_by_default(self):
        self.assertNotIn("linkedin", pipeline.available_sources({}, requested_sources=["linkedin"]))

    def test_linkedin_requires_enable_flag_and_agent_browser(self):
        config = {"LAST30DAYS_LINKEDIN_BROWSER": "1"}
        with mock.patch("shutil.which", return_value="/usr/bin/agent-browser"):
            self.assertIn("linkedin", pipeline.available_sources(config, requested_sources=["linkedin"]))

    def test_linkedin_must_be_explicitly_requested(self):
        config = {"LAST30DAYS_LINKEDIN_BROWSER": "1"}
        with mock.patch("shutil.which", return_value="/usr/bin/agent-browser"):
            self.assertNotIn("linkedin", pipeline.available_sources(config))

    def test_pipeline_dispatches_to_linkedin_adapter(self):
        raw = post_candidate()
        with mock.patch("lib.pipeline.linkedin.search_linkedin", return_value={
            "items": [raw], "error": None
        }) as search:
            items, artifact = pipeline._retrieve_stream(
                topic="robotic lawn mower",
                subquery=schema.SubQuery(
                    label="primary",
                    search_query="robotic lawn mower",
                    ranking_query="robotic lawn mower field testing",
                    sources=["linkedin"],
                ),
                source="linkedin",
                config={},
                depth="quick",
                date_range=("2026-06-15", "2026-07-15"),
                runtime=schema.ProviderRuntime(
                    reasoning_provider=None, planner_model=None, rerank_model=None
                ),
                mock=False,
            )
        self.assertEqual([raw], items)
        self.assertEqual({}, artifact)
        search.assert_called_once()


class LinkedInNavigationAndAuthTests(unittest.TestCase):
    def test_retained_workspace_reselects_inactive_linkedin_tab(self):
        client = linkedin.CliAgentBrowserClient(timeout=5)
        with mock.patch.object(client, "_invoke", side_effect=[
            {"tabs": [
                {"index": 0, "active": True, "url": "https://www.facebook.com/"},
                {"index": 2, "active": False, "url": "https://www.linkedin.com/feed/"},
            ]},
            {},
        ]) as invoke:
            client._activate_linkedin_tab("shared-social")
        self.assertEqual(
            ["--session", "shared-social", "tab", "2"], invoke.call_args_list[1].args[0]
        )

    def test_retained_workspace_keeps_active_linkedin_tab(self):
        client = linkedin.CliAgentBrowserClient(timeout=5)
        with mock.patch.object(client, "_invoke", return_value={
            "tabs": [{"index": 2, "active": True, "url": "https://www.linkedin.com/feed/"}]
        }) as invoke:
            client._activate_linkedin_tab("shared-social")
        self.assertEqual(1, invoke.call_count)

    def test_search_uses_exact_latest_content_url(self):
        client = FakeAgentBrowserClient()
        result = make_scraper(client).search("robotic lawn mower", "2026-06-15", "2026-07-15")
        self.assertIsNone(result["error_type"])
        navigation = [action for action in client.actions if action.operation == "new_tab"]
        self.assertEqual(1, len(navigation))
        query = navigation[0].value
        self.assertIn("/search/results/content/", query)
        self.assertIn("sortBy=%22date_posted%22", query)

    def test_wrong_sort_is_rejected(self):
        page = dict(FakeAgentBrowserClient().page)
        page["url"] = page["url"].replace("%22date_posted%22", "%22relevance%22")
        client = FakeAgentBrowserClient(page=page, preserve_url=True)
        result = make_scraper(client).search("robotic lawn mower", "2026-06-15", "2026-07-15")
        self.assertEqual("navigation_mismatch", result["error_type"])
        self.assertEqual([], result["items"])

    def test_checkpoint_returns_operator_handoff(self):
        client = FakeAgentBrowserClient(
            auth=linkedin.LinkedInAuthState(authenticated=False, checkpoint=True)
        )
        result = make_scraper(client).search("robotic lawn mower", "2026-06-15", "2026-07-15")
        self.assertEqual("checkpoint_required", result["error_type"])
        self.assertEqual("https://operator.example/opaque-token", result["operator_url"])

    def test_logged_out_profile_requires_authentication(self):
        client = FakeAgentBrowserClient(
            auth=linkedin.LinkedInAuthState(authenticated=False, login_form=True)
        )
        result = make_scraper(client).search("robotic lawn mower", "2026-06-15", "2026-07-15")
        self.assertEqual("auth_required", result["error_type"])

    def test_no_results_is_valid_empty_result(self):
        page = dict(FakeAgentBrowserClient().page)
        page.update({"has_content_cards": False, "no_results": True})
        result = make_scraper(FakeAgentBrowserClient(page=page, candidates=[])).search(
            "robotic lawn mower", "2026-06-15", "2026-07-15"
        )
        self.assertIsNone(result["error_type"])
        self.assertEqual([], result["items"])


class LinkedInCandidateQualityTests(unittest.TestCase):
    def test_accepts_canonical_dated_relevant_post(self):
        result = make_scraper(FakeAgentBrowserClient()).search(
            "robotic lawn mower", "2026-06-15", "2026-07-15"
        )
        self.assertIsNone(result["error_type"])
        self.assertEqual(1, len(result["items"]))
        item = result["items"][0]
        self.assertEqual(
            "https://www.linkedin.com/feed/update/urn:li:activity:7351200000000000000/",
            item["url"],
        )
        self.assertEqual("2026-07-13", item["date"])
        self.assertEqual("AgriTech Lab", item["author"])

    def test_recovers_permalink_from_activity_urn(self):
        self.assertEqual(
            "https://www.linkedin.com/feed/update/urn:li:activity:7351200000000000000/",
            linkedin._canonical_post_url("", "urn:li:activity:7351200000000000000"),
        )

    def test_canonicalizes_posts_url_and_drops_tracking(self):
        self.assertEqual(
            "https://www.linkedin.com/posts/example_activity-7351200000000000000-abcd/",
            linkedin._canonical_post_url(
                "https://linkedin.com/posts/example_activity-7351200000000000000-abcd/?utm_source=share"
            ),
        )

    def test_compact_relative_dates(self):
        self.assertEqual(("2026-07-15", "med"), linkedin._parse_linkedin_date("3h • Edited", NOW))
        self.assertEqual(("2026-07-08", "med"), linkedin._parse_linkedin_date("1w", NOW))
        self.assertEqual(("2026-06-15", "med"), linkedin._parse_linkedin_date("1mo", NOW))

    def test_rejects_sponsored_non_post_and_out_of_range_cards(self):
        candidates = [
            post_candidate(sponsored=True, text="Promoted robotic lawn mower product announcement with details."),
            post_candidate(url="https://www.linkedin.com/in/example/", urn=""),
            post_candidate(timestamp="2mo"),
        ]
        result = make_scraper(FakeAgentBrowserClient(candidates=candidates)).search(
            "robotic lawn mower", "2026-06-15", "2026-07-15"
        )
        self.assertEqual("quality_gate_failed", result["error_type"])
        counts = result["diagnostics"]["rejection_counts"]
        self.assertGreaterEqual(counts["sponsored"], 1)
        self.assertGreaterEqual(counts["missing_permalink"], 1)
        self.assertGreaterEqual(counts["outside_date_range"], 1)

    def test_normalization_preserves_linkedin_metadata(self):
        raw = {
            "id": "LI1",
            "text": "A useful LinkedIn post about agricultural robotics deployment.",
            "url": "https://www.linkedin.com/feed/update/urn:li:activity:1/",
            "author": "Example Labs",
            "date": "2026-01-15",
            "engagement": {"likes": 5, "comments": 1, "shares": 1},
            "metadata": {"extraction": "agent-browser-dom-v1", "date_confidence": "high"},
        }
        item = normalize.normalize_source_items("linkedin", [raw], "2026-01-01", "2026-01-31")[0]
        self.assertEqual("linkedin", item.source)
        self.assertEqual("Example Labs", item.author)
        self.assertEqual("agent-browser-dom-v1", item.metadata["extraction"])

    def test_rendering_registers_linkedin_label_and_engagement(self):
        self.assertEqual("LinkedIn", render.SOURCE_LABELS["linkedin"])
        self.assertEqual(
            [("likes", "react"), ("comments", "cmt"), ("shares", "repost")],
            render.ENGAGEMENT_DISPLAY["linkedin"],
        )
        self.assertTrue(any(source == "linkedin" for source, *_ in render._FOOTER_SOURCES))

    def test_debug_artifact_is_sanitized(self):
        client = FakeAgentBrowserClient()
        with tempfile.TemporaryDirectory() as directory:
            result = make_scraper(client, debug_dir=directory).search(
                "robotic lawn mower", "2026-06-15", "2026-07-15"
            )
            artifacts = list(Path(directory).glob("linkedin-*.json"))
            self.assertEqual(1, len(artifacts))
            text = artifacts[0].read_text(encoding="utf-8")
        self.assertIsNone(result["error_type"])
        self.assertNotIn("opaque-token", text)
        self.assertNotIn("We tested robotic", text)
        self.assertNotIn("li_at", text)
        payload = json.loads(text)
        self.assertEqual("robotic lawn mower", payload["query"])


@unittest.skipUnless(
    os.getenv("LAST30DAYS_LINKEDIN_LIVE_SMOKE") == "1", "opt-in live LinkedIn smoke"
)
class LinkedInLiveSmokeTests(unittest.TestCase):
    def test_three_queries_reuse_profile_and_emit_only_quality_posts(self):
        config = {
            "LAST30DAYS_LINKEDIN_PROFILE": os.getenv(
                "LAST30DAYS_LINKEDIN_PROFILE", "last30days-linkedin"
            ),
            "LAST30DAYS_LINKEDIN_SESSION": os.getenv(
                "LAST30DAYS_LINKEDIN_SESSION", "last30days-linkedin"
            ),
            "LAST30DAYS_LINKEDIN_SCROLLS": "0",
            "LAST30DAYS_LINKEDIN_INITIAL_WAIT": "1",
        }
        browser_ids = set()
        for topic in ("regenerative agriculture", "AI agents", "robotic lawn mower"):
            result = linkedin.search_linkedin(
                topic, "2026-06-15", "2026-07-15", depth="quick", config=config
            )
            self.assertIsNone(result.get("error_type"), result)
            browser_ids.add(result["workspace"]["browser_id"])
            for item in result["items"]:
                self.assertIsNotNone(linkedin._canonical_post_url(item["url"]))
                self.assertTrue(item["author"])
                self.assertTrue(item["date"])
        self.assertEqual(1, len(browser_ids))


if __name__ == "__main__":
    unittest.main()
