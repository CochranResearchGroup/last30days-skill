import json
import os
import subprocess
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
    def __init__(
        self,
        *,
        page=None,
        candidates=None,
        candidate_batches=None,
        auth=None,
        preserve_url=False,
    ):
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
        self.candidate_batches = (
            [list(batch) for batch in candidate_batches]
            if candidate_batches is not None
            else None
        )
        self.extraction_count = 0
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
            candidates = self.candidates
            if self.candidate_batches is not None:
                batch_index = min(
                    self.extraction_count, len(self.candidate_batches) - 1
                )
                candidates = self.candidate_batches[batch_index]
                self.extraction_count += 1
            return {
                "url": self.page["url"],
                "title": self.page["title"],
                "candidates": candidates,
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
    def test_home_feed_collects_posts_without_a_topic_query(self):
        page = dict(FakeAgentBrowserClient().page)
        page.update({
            "url": "https://www.linkedin.com/feed/",
            "title": "Feed | LinkedIn",
            "heading": "Feed",
            "query_value": "",
            "has_content_filters": False,
            "has_content_cards": True,
        })
        candidate = post_candidate(
            text="A legitimate home-feed post with no relationship to the retired OpenAI query."
        )
        client = FakeAgentBrowserClient(page=page, candidates=[candidate])

        result = make_scraper(client).feed("2026-06-15", "2026-07-15")

        self.assertIsNone(result["error_type"])
        self.assertEqual("https://www.linkedin.com/feed/", result["url"])
        self.assertEqual(
            "Authenticated LinkedIn home feed post",
            result["items"][0]["why_relevant"],
        )
        self.assertNotIn(
            "no_lexical_topic_overlap",
            result["items"][0]["metadata"]["retrieval_signals"],
        )

    def test_browser_failure_records_stage_and_bounded_operation_evidence(self):
        client = FakeAgentBrowserClient()
        client.command_timings = [
            {"operation": "tab", "duration_ms": 41, "status": "failed"}
        ]
        client.inspect_auth = mock.Mock(
            side_effect=linkedin.LinkedInScraperFailure(
                "agent_browser_error", "browser command failed"
            )
        )

        result = make_scraper(client).search(
            "robotic lawn mower", "2026-06-15", "2026-07-15"
        )

        self.assertEqual("agent_browser_error", result["error_type"])
        self.assertEqual("authentication", result["diagnostics"]["failure_stage"])
        self.assertEqual(
            [{"operation": "tab", "duration_ms": 41, "status": "failed"}],
            result["diagnostics"]["browser_operations"],
        )

    def test_feed_preserves_typed_workspace_acquisition_reason(self):
        client = FakeAgentBrowserClient()
        client.acquire_workspace = mock.Mock(
            side_effect=linkedin.browser_runtime.AgentBrowserRuntimeFailure(
                "agent_browser_error",
                "dynamic route details must not become durable evidence",
                reason_code="service_tab_target_unsettled",
            )
        )

        result = make_scraper(client).feed("2026-06-15", "2026-07-15")

        self.assertEqual("agent_browser_error", result["error_type"])
        self.assertEqual("workspace_acquisition", result["diagnostics"]["failure_stage"])
        self.assertEqual(
            "service_tab_target_unsettled",
            result["diagnostics"]["failure_reason_code"],
        )
        self.assertNotIn("dynamic route details", str(result["diagnostics"]))

    def test_workspace_acquisition_uses_broker_for_linkedin_identity(self):
        client = linkedin.CliAgentBrowserClient(timeout=5)
        expected = linkedin.BrowserWorkspace(
            profile_id="last30days-linkedin",
            browser_id="browser-1",
            session_name="last30days-linkedin",
        )
        with mock.patch.object(
            linkedin.browser_runtime.CliAgentBrowserClient,
            "acquire_workspace",
            return_value=expected,
        ) as acquire:
            actual = client.acquire_workspace(request())

        self.assertEqual(expected, actual)
        acquire.assert_called_once_with(
            mock.ANY,
            target_service_id="linkedin",
        )

    def test_search_registers_linkedin_target_metadata_on_browser_request(self):
        captured = {}

        def scraper_factory(_client, workspace_request, **_kwargs):
            captured["request"] = workspace_request
            return mock.Mock(search=mock.Mock(return_value={"items": [], "error": None}))

        with mock.patch.object(linkedin, "is_agent_browser_available", return_value=True), mock.patch.object(
            linkedin, "LinkedInScraper", side_effect=scraper_factory
        ):
            linkedin.search_linkedin(
                "robotic lawn mower",
                "2026-06-15",
                "2026-07-15",
                depth="quick",
            )

        workspace_request = captured["request"]
        self.assertEqual("linkedin", workspace_request.target_service_id)
        self.assertEqual("linkedin-scraper", workspace_request.agent_name)
        self.assertEqual("linkedin-content-search", workspace_request.task_name)
        self.assertEqual("https://www.linkedin.com/feed/", workspace_request.start_url)
        self.assertEqual("shared_display", workspace_request.display_isolation)

    def test_feed_registers_distinct_home_feed_task_metadata(self):
        captured = {}
        client = mock.Mock()

        def scraper_factory(_client, workspace_request, **_kwargs):
            captured["request"] = workspace_request
            return mock.Mock(feed=mock.Mock(return_value={"items": [], "error": None}))

        with mock.patch.object(
            linkedin, "is_agent_browser_available", return_value=True
        ), mock.patch.object(
            linkedin, "CliAgentBrowserClient", return_value=client
        ), mock.patch.object(
            linkedin, "LinkedInScraper", side_effect=scraper_factory
        ):
            linkedin.scrape_linkedin_feed(
                "2026-06-15",
                "2026-07-15",
                depth="quick",
            )

        workspace_request = captured["request"]
        self.assertEqual("linkedin-home-feed", workspace_request.task_name)
        self.assertEqual("https://www.linkedin.com/feed/", workspace_request.start_url)
        client.release_workspace.assert_called_once_with()

    def test_explicit_twenty_item_limit_has_a_bounded_four_scroll_budget(self):
        captured = {}

        def scraper_factory(_client, _workspace_request, **kwargs):
            captured.update(kwargs)
            return mock.Mock(search=mock.Mock(return_value={"items": [], "error": None}))

        with mock.patch.object(linkedin, "is_agent_browser_available", return_value=True), mock.patch.object(
            linkedin, "LinkedInScraper", side_effect=scraper_factory
        ):
            linkedin.search_linkedin(
                "robotic lawn mower",
                "2026-06-15",
                "2026-07-15",
                depth="default",
                limit=20,
            )

        self.assertEqual(20, captured["limit"])
        self.assertEqual(4, captured["scrolls"])

    def test_feed_twenty_item_limit_uses_the_eight_scroll_safety_ceiling(self):
        captured = {}

        def scraper_factory(_client, _workspace_request, **kwargs):
            captured.update(kwargs)
            return mock.Mock(feed=mock.Mock(return_value={"items": [], "error": None}))

        with mock.patch.object(linkedin, "is_agent_browser_available", return_value=True), mock.patch.object(
            linkedin, "LinkedInScraper", side_effect=scraper_factory
        ):
            linkedin.scrape_linkedin_feed(
                "2026-06-15",
                "2026-07-15",
                depth="default",
                limit=20,
            )

        self.assertEqual(20, captured["limit"])
        self.assertEqual(8, captured["scrolls"])

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

    def test_auth_inspection_opens_linkedin_when_recovered_browser_has_no_site_tab(self):
        client = linkedin.CliAgentBrowserClient(timeout=5)
        workspace = linkedin.BrowserWorkspace(
            profile_id="last30days-facebook",
            browser_id="session:shared-social",
            session_name="shared-social",
        )
        authenticated = {
            "authenticated_dom": True,
            "login_form": False,
            "checkpoint": False,
            "has_li_at": True,
            "url": "https://www.linkedin.com/feed/",
        }
        with mock.patch.object(client, "prepare_site_tab", return_value=False), mock.patch.object(
            client, "act", return_value=linkedin.BrowserState()
        ) as act, mock.patch.object(client, "evaluate", return_value=authenticated):
            auth = client.inspect_auth(workspace)

        self.assertEqual(
            [
                mock.call(
                    workspace,
                    linkedin.BrowserAction("new_tab", value="https://www.linkedin.com/feed/"),
                ),
                mock.call(workspace, linkedin.BrowserAction("wait", value="2500")),
            ],
            act.call_args_list,
        )
        self.assertTrue(auth.authenticated)

    def test_blank_linkedin_auth_probe_reuses_the_same_tab_for_one_reprobe(self):
        client = linkedin.CliAgentBrowserClient(timeout=5)
        workspace = linkedin.BrowserWorkspace(
            profile_id="last30days-facebook",
            browser_id="session:shared-social",
            session_name="shared-social",
            target_id="linkedin-owned",
        )
        blank = {
            "authenticated_dom": False,
            "login_form": False,
            "checkpoint": False,
            "has_li_at": False,
            "url": "https://www.linkedin.com/feed/",
            "title": "",
        }
        authenticated = {
            "authenticated_dom": True,
            "login_form": False,
            "checkpoint": False,
            "has_li_at": False,
            "url": "https://www.linkedin.com/feed/",
            "title": "Feed | LinkedIn",
        }

        with mock.patch.object(
            client, "prepare_site_tab", return_value=True
        ), mock.patch.object(
            client, "act", return_value=linkedin.BrowserState()
        ) as act, mock.patch.object(
            client, "evaluate", side_effect=[blank, authenticated]
        ):
            auth = client.inspect_auth(workspace)

        self.assertTrue(auth.authenticated)
        self.assertEqual(
            [
                mock.call(
                    workspace,
                    linkedin.BrowserAction(
                        "navigate", value="https://www.linkedin.com/feed/"
                    ),
                ),
                mock.call(workspace, linkedin.BrowserAction("wait", value="2500")),
            ],
            act.call_args_list,
        )

    def test_retained_workspace_closes_duplicate_linkedin_tabs_only(self):
        client = linkedin.CliAgentBrowserClient(timeout=5)
        with mock.patch.object(client, "_invoke", side_effect=[
            {"tabs": [
                {"index": 0, "active": False, "url": "https://www.facebook.com/"},
                {"index": 1, "active": True, "url": "https://www.linkedin.com/feed/"},
                {"index": 2, "active": False, "url": "https://www.linkedin.com/search/results/content/"},
            ]},
            {},
        ]) as invoke:
            client._activate_linkedin_tab("shared-social")
        self.assertEqual(
            ["--session", "shared-social", "tab", "close", "2"],
            invoke.call_args_list[1].args[0],
        )

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

    def test_rate_limit_warning_stops_before_extraction(self):
        page = dict(FakeAgentBrowserClient().page)
        page.update({"rate_limited": True, "rate_limit_reason": "search_limit"})
        client = FakeAgentBrowserClient(page=page)
        result = make_scraper(client).search("robotic lawn mower", "2026-06-15", "2026-07-15")
        self.assertEqual("rate_limit_detected", result["error_type"])
        self.assertEqual([], result["items"])

    def test_interaction_limiter_enforces_minimum_action_delay(self):
        limiter = linkedin.LinkedInInteractionLimiter(min_delay=4, max_actions_per_minute=6)
        with mock.patch("lib.linkedin.time.monotonic", side_effect=[100.0, 101.0, 104.0]), mock.patch(
            "lib.linkedin.time.sleep"
        ) as sleep:
            limiter.wait()
            limiter.wait()
        sleep.assert_called_once_with(3.0)

    def test_logged_out_profile_requires_authentication(self):
        client = FakeAgentBrowserClient(
            auth=linkedin.LinkedInAuthState(authenticated=False, login_form=True)
        )
        result = make_scraper(client).search("robotic lawn mower", "2026-06-15", "2026-07-15")
        self.assertEqual("auth_required", result["error_type"])

    def test_blank_feed_auth_evidence_is_ambiguous_not_logged_out(self):
        client = FakeAgentBrowserClient(
            auth=linkedin.LinkedInAuthState(
                authenticated=False,
                login_form=False,
                checkpoint=False,
                url="https://www.linkedin.com/feed/",
            )
        )

        result = make_scraper(client).feed("2026-06-15", "2026-07-15")

        self.assertEqual("auth_state_ambiguous", result["error_type"])

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

    def test_scrolls_until_the_accepted_unique_item_limit_is_reached(self):
        def candidates(start, count):
            return [
                post_candidate(
                    text=(
                        "AgriTech Lab\n"
                        f"Robotic lawn mower field result {index} includes enough "
                        "relevant deployment and safety detail."
                    ),
                    url=(
                        "https://www.linkedin.com/feed/update/urn:li:activity:"
                        f"735120000000000{index:04d}/"
                    ),
                    urn=f"urn:li:activity:735120000000000{index:04d}",
                )
                for index in range(start, start + count)
            ]

        first = candidates(0, 6)
        client = FakeAgentBrowserClient(
            candidate_batches=[
                first,
                first,
                candidates(6, 5),
                candidates(11, 5),
                candidates(16, 4),
            ]
        )

        result = make_scraper(client, limit=20, scrolls=4).search(
            "robotic lawn mower", "2026-06-15", "2026-07-15"
        )

        self.assertEqual(20, len(result["items"]))
        self.assertEqual(4, len([
            action for action in client.actions if action.operation == "scroll"
        ]))
        self.assertEqual(6, result["diagnostics"]["rejection_counts"]["duplicate"])

    def test_home_feed_scrolls_past_overlap_until_twenty_unique_posts(self):
        def candidates(start, count):
            return [
                post_candidate(
                    text=(
                        "Feed Author\n"
                        f"Home feed result {index} includes stable structural metadata."
                    ),
                    url=(
                        "https://www.linkedin.com/feed/update/urn:li:activity:"
                        f"735130000000000{index:04d}/"
                    ),
                    urn=f"urn:li:activity:735130000000000{index:04d}",
                )
                for index in range(start, start + count)
            ]

        page = dict(FakeAgentBrowserClient().page)
        page.update({
            "url": "https://www.linkedin.com/feed/",
            "title": "Feed | LinkedIn",
            "heading": "Feed",
            "query_value": "",
            "has_content_filters": False,
            "has_content_cards": True,
        })
        first = candidates(0, 5)
        client = FakeAgentBrowserClient(page=page, candidate_batches=[
            first,
            first,
            candidates(5, 3),
            candidates(8, 3),
            candidates(11, 3),
            candidates(14, 3),
            candidates(17, 3),
        ])

        result = make_scraper(client, limit=20, scrolls=8).feed(
            "2026-06-15", "2026-07-15"
        )

        self.assertEqual(20, len(result["items"]))
        self.assertEqual(6, len([
            action for action in client.actions if action.operation == "scroll"
        ]))
        self.assertEqual(20, result["diagnostics"]["unique_observation_count"])
        self.assertEqual(6, result["diagnostics"]["scroll_count"])

    def test_home_feed_advances_farther_when_accepted_yield_lags(self):
        posts = [
            post_candidate(
                text=(
                    "Feed Author\n"
                    f"Tall virtualized feed post {index} has a canonical permalink."
                ),
                url=(
                    "https://www.linkedin.com/feed/update/urn:li:activity:"
                    f"735140000000000{index:04d}/"
                ),
                urn=f"urn:li:activity:735140000000000{index:04d}",
            )
            for index in range(24)
        ]
        sponsored = post_candidate(
            text="Sponsored placement",
            url="https://www.linkedin.com/feed/update/urn:li:activity:7351499999999999999/",
            urn="urn:li:activity:7351499999999999999",
            sponsored=True,
        )
        page = dict(FakeAgentBrowserClient().page)
        page.update({
            "url": "https://www.linkedin.com/feed/",
            "title": "Feed | LinkedIn",
            "heading": "Feed",
            "query_value": "",
            "has_content_filters": False,
            "has_content_cards": True,
        })

        class TallVirtualizedFeedClient(FakeAgentBrowserClient):
            def __init__(self):
                super().__init__(page=page)
                self.scroll_offset = 0

            def act(self, workspace, action):
                state = super().act(workspace, action)
                if action.operation == "scroll":
                    self.scroll_offset += int(action.value or 0)
                return state

            def evaluate(self, workspace, script):
                if script == linkedin.EXTRACT_SCRIPT:
                    last_visible = min(
                        len(posts) - 1,
                        max(0, (self.scroll_offset + 2_000) // 1_000),
                    )
                    first_visible = max(0, (self.scroll_offset - 2_000) // 1_000)
                    return {
                        "url": self.page["url"],
                        "title": self.page["title"],
                        "candidates": posts[first_visible:last_visible + 1] + [sponsored],
                    }
                return super().evaluate(workspace, script)

        client = TallVirtualizedFeedClient()
        result = make_scraper(client, limit=20, scrolls=8).feed(
            "2026-06-15", "2026-07-15"
        )

        scrolls = [
            int(action.value or 0)
            for action in client.actions
            if action.operation == "scroll"
        ]
        self.assertEqual(20, len(result["items"]), scrolls)
        self.assertEqual(20, len({item["url"] for item in result["items"]}))
        self.assertLessEqual(len(scrolls), 8)
        self.assertGreater(max(scrolls), 1_400)
        self.assertTrue(all(distance <= 3_200 for distance in scrolls))
        self.assertGreater(result["diagnostics"]["rejection_counts"]["sponsored"], 0)

    def test_home_feed_preserves_permalinked_post_with_missing_author_and_date(self):
        page = dict(FakeAgentBrowserClient().page)
        page.update({
            "url": "https://www.linkedin.com/feed/",
            "title": "Feed | LinkedIn",
            "heading": "Feed",
            "query_value": "",
            "has_content_filters": False,
            "has_content_cards": True,
        })
        candidate = post_candidate(author="", author_url="", timestamp="")

        result = make_scraper(
            FakeAgentBrowserClient(page=page, candidates=[candidate])
        ).feed("2026-06-15", "2026-07-15")

        self.assertIsNone(result["error_type"])
        self.assertEqual(1, len(result["items"]))
        self.assertIsNone(result["items"][0]["author"])
        self.assertIsNone(result["items"][0]["date"])
        self.assertEqual(
            ["missing_author", "missing_date"],
            result["items"][0]["metadata"]["retrieval_signals"],
        )

    def test_home_feed_deduplicates_expanded_text_by_canonical_permalink(self):
        page = dict(FakeAgentBrowserClient().page)
        page.update({
            "url": "https://www.linkedin.com/feed/",
            "title": "Feed | LinkedIn",
            "heading": "Feed",
            "query_value": "",
            "has_content_filters": False,
            "has_content_cards": True,
        })
        collapsed = post_candidate(text="AgriTech Lab\nA permalinked feed post.")
        expanded = post_candidate(
            text=(
                "AgriTech Lab\nA permalinked feed post with expanded body text "
                "after the virtualized card rerendered."
            )
        )

        result = make_scraper(
            FakeAgentBrowserClient(page=page, candidates=[collapsed, expanded])
        ).feed("2026-06-15", "2026-07-15")

        self.assertEqual(1, len(result["items"]))
        self.assertEqual(1, result["diagnostics"]["rejection_counts"]["duplicate"])

    def test_home_feed_reaches_twenty_when_only_ads_are_excluded(self):
        def legitimate(start, count):
            return [
                post_candidate(
                    text=f"Permalinked feed post {index} with useful primary text.",
                    url=(
                        "https://www.linkedin.com/feed/update/urn:li:activity:"
                        f"735140000000000{index:04d}/"
                    ),
                    urn=f"urn:li:activity:735140000000000{index:04d}",
                    author="",
                    author_url="",
                    timestamp="",
                )
                for index in range(start, start + count)
            ]

        ads = [
            post_candidate(
                text=f"Sponsored placement {index}",
                url=(
                    "https://www.linkedin.com/feed/update/urn:li:activity:"
                    f"735150000000000{index:04d}/"
                ),
                urn=f"urn:li:activity:735150000000000{index:04d}",
                sponsored=True,
            )
            for index in range(5)
        ]
        page = dict(FakeAgentBrowserClient().page)
        page.update({
            "url": "https://www.linkedin.com/feed/",
            "title": "Feed | LinkedIn",
            "heading": "Feed",
            "query_value": "",
            "has_content_filters": False,
            "has_content_cards": True,
        })
        first = legitimate(0, 10) + ads
        second = legitimate(0, 20) + ads

        result = make_scraper(
            FakeAgentBrowserClient(page=page, candidate_batches=[first, second]),
            limit=20,
            scrolls=2,
        ).feed("2026-06-15", "2026-07-15")

        self.assertEqual(20, len(result["items"]))
        self.assertEqual(20, len({item["url"] for item in result["items"]}))
        self.assertNotIn("missing_author", result["diagnostics"]["rejection_counts"])
        self.assertNotIn("missing_date", result["diagnostics"]["rejection_counts"])
        self.assertEqual(5, result["diagnostics"]["rejection_counts"]["sponsored"])

    def test_home_feed_keeps_post_media_but_excludes_identity_chrome(self):
        page = dict(FakeAgentBrowserClient().page)
        page.update({
            "url": "https://www.linkedin.com/feed/",
            "title": "Feed | LinkedIn",
            "heading": "Feed",
            "query_value": "",
            "has_content_filters": False,
            "has_content_cards": True,
        })
        candidate_url = (
            "https://www.linkedin.com/feed/update/"
            "urn:li:activity:7351200000000000000/"
        )
        candidate = post_candidate(media=[
            {
                "kind": "image",
                "url": "https://media.licdn.com/dms/image/v2/D5622AQ/post/feedshare-shrink_800/image.jpg",
                "alt_text": "A chart attached to the post",
            },
            {
                "kind": "image",
                "url": "https://media.licdn.com/dms/image/v2/C4E03AQ/profile-displayphoto-shrink_100_100/avatar.jpg",
                "alt_text": None,
            },
            {
                "kind": "image",
                "url": "https://media.licdn.com/dms/image/v2/C4D0BAQ/company-logo_100_100/logo.jpg",
                "alt_text": "Example Company",
            },
            {
                "kind": "image",
                "url": "https://media.licdn.com/dms/image/v2/D4E07AQ/group-logo_image-shrink_48x48/logo.jpg",
                "alt_text": None,
            },
            {
                "kind": "video",
                "url": candidate_url,
                "preview_url": "https://media.licdn.com/dms/image/v2/D5624AQ/post/videocover-low/image.jpg",
                "alt_text": None,
            },
        ])

        result = make_scraper(
            FakeAgentBrowserClient(page=page, candidates=[candidate])
        ).feed("2026-06-15", "2026-07-15")

        self.assertEqual(1, len(result["items"]))
        self.assertEqual(
            [
                "https://media.licdn.com/dms/image/v2/D5622AQ/post/feedshare-shrink_800/image.jpg",
                candidate_url,
            ],
            [item["url"] for item in result["items"][0]["metadata"]["media"]],
        )

    def test_home_feed_stops_after_two_snapshots_without_new_posts(self):
        page = dict(FakeAgentBrowserClient().page)
        page.update({
            "url": "https://www.linkedin.com/feed/",
            "title": "Feed | LinkedIn",
            "heading": "Feed",
            "query_value": "",
            "has_content_filters": False,
            "has_content_cards": True,
        })
        repeated = [post_candidate()]
        client = FakeAgentBrowserClient(
            page=page,
            candidate_batches=[repeated, repeated, repeated],
        )

        result = make_scraper(client, limit=20, scrolls=8).feed(
            "2026-06-15", "2026-07-15"
        )

        self.assertEqual(1, len(result["items"]))
        self.assertEqual(2, len([
            action for action in client.actions if action.operation == "scroll"
        ]))
        self.assertEqual(2, result["diagnostics"]["stagnant_scrolls"])

    def test_recovers_permalink_from_activity_urn(self):
        self.assertEqual(
            "https://www.linkedin.com/feed/update/urn:li:activity:7351200000000000000/",
            linkedin._canonical_post_url("", "urn:li:activity:7351200000000000000"),
        )

    def test_extractor_has_bounded_runtime_activity_urn_fallback(self):
        self.assertIn("activityUrn", linkedin.EXTRACT_SCRIPT)
        self.assertIn("steps < 12000", linkedin.EXTRACT_SCRIPT)
        self.assertIn("activityUrn(node)", linkedin.EXTRACT_SCRIPT)

    def test_extractor_recovers_current_attribute_actor_and_timestamp_variants(self):
        harness = f"""
const tracking = {{
  href: "https://www.linkedin.com/feed/?updateEntityUrn=urn%3Ali%3Aactivity%3A7494999999999999999",
  innerText: "", textContent: "", getAttributeNames() {{ return ["href"]; }},
  getAttribute(name) {{ return name === "href" ? this.href : null; }}
}};
const author = {{
  href: "https://www.linkedin.com/company/example-company/",
  innerText: "", textContent: "", getAttributeNames() {{ return ["aria-label"]; }},
  getAttribute(name) {{ return name === "aria-label" ? "Example Company" : null; }},
  closest() {{ return this; }}, querySelector() {{ return null; }}
}};
const time = {{
  innerText: "", textContent: "",
  getAttribute(name) {{ return name === "aria-label" ? "3h • Edited" : null; }}
}};
const post = {{
  innerText: "Example Company\\n3h • Edited\\nA real feed post with current metadata variants.",
  textContent: "", dataset: {{}}, contains() {{ return false; }}, closest() {{ return this; }},
  getAttributeNames() {{ return ["data-id"]; }},
  getAttribute(name) {{
    return name === "data-id" ? "urn:li:activity:7494999999999999999" : null;
  }},
  querySelector(selector) {{
    if (selector.includes("actor__title")) return author;
    if (selector.startsWith("time")) return time;
    return null;
  }},
  querySelectorAll(selector) {{
    if (selector === "a[href]") return [tracking, author];
    if (selector.includes("[data-urn]")) return [tracking];
    if (selector.startsWith("time")) return [time];
    return [];
  }}
}};
const main = {{querySelectorAll(selector) {{
  return selector === '[data-id^="urn:li:activity:"]' ? [post] : [];
}}}};
const document = {{
  title: "Feed | LinkedIn", body: {{innerText: post.innerText}},
  querySelector(selector) {{
    return selector === 'main, [role="main"], .scaffold-layout__main' ? main : null;
  }}
}};
const location = {{href: "https://www.linkedin.com/feed/"}};
const result = {linkedin.EXTRACT_SCRIPT};
process.stdout.write(JSON.stringify(result));
"""
        completed = subprocess.run(
            ["node", "-e", harness], capture_output=True, text=True, check=False
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        candidate = json.loads(completed.stdout)["candidates"][0]
        self.assertEqual(
            "https://www.linkedin.com/feed/update/urn:li:activity:7494999999999999999/",
            candidate["url"],
        )
        self.assertEqual("Example Company", candidate["author"])
        self.assertEqual("3h • Edited", candidate["timestamp"])

    def test_extractor_prioritizes_runtime_props_over_large_fiber_graph(self):
        harness = f"""
const runtimeTree = (depth, leaf) => {{
  const root = {{}};
  let level = [root];
  for (let index = 0; index < depth; index += 1) {{
    const next = [];
    for (const node of level) {{
      node.left = {{}};
      node.right = {{}};
      next.push(node.left, node.right);
    }}
    level = next;
  }}
  level[level.length - 1].value = leaf;
  return root;
}};
const author = {{
  href: "https://www.linkedin.com/in/example-author/",
  innerText: "Example Author", textContent: "Example Author",
  closest() {{ return this; }}
}};
const post = {{
  innerText: "Feed post\\nExample Author\\nnow •\\nOpenAI update with enough detail",
  textContent: "",
  dataset: {{}},
  contains() {{ return false; }},
  getAttribute() {{ return null; }},
  querySelector() {{ return null; }},
  querySelectorAll(selector) {{
    if (selector === "a[href]") return [author];
    return [];
  }}
}};
post["__reactFiber$fixture"] = runtimeTree(12, "fiber leaf");
post["__reactProps$fixture"] = runtimeTree(
  12,
  "urn:li:activity:7494833904651243523"
);
const main = {{
  querySelectorAll(selector) {{
    return selector === "main [role=\\"listitem\\"]" ? [post] : [];
  }}
}};
const document = {{
  title: "Search | LinkedIn",
  body: {{innerText: post.innerText}},
  querySelector(selector) {{
    return selector === "main, [role=\\"main\\"], .scaffold-layout__main" ? main : null;
  }}
}};
const location = {{href: "https://www.linkedin.com/search/results/content/"}};
const result = {linkedin.EXTRACT_SCRIPT};
process.stdout.write(JSON.stringify(result));
"""
        completed = subprocess.run(
            ["node", "-e", harness],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        result = json.loads(completed.stdout)
        self.assertEqual(
            "urn:li:activity:7494833904651243523",
            result["candidates"][0]["urn"],
        )

    def test_canonicalizes_posts_url_and_drops_tracking(self):
        self.assertEqual(
            "https://www.linkedin.com/posts/example_activity-7351200000000000000-abcd/",
            linkedin._canonical_post_url(
                "https://linkedin.com/posts/example_activity-7351200000000000000-abcd/?utm_source=share"
            ),
        )

    def test_extractor_preserves_literal_now_timestamp(self):
        harness = f"""
const permalink = {{
  href: "https://www.linkedin.com/feed/update/urn:li:activity:7494766621761183744/",
  innerText: "", textContent: ""
}};
const author = {{
  href: "https://www.linkedin.com/in/example-author/",
  innerText: "Example Author", textContent: "Example Author",
  closest() {{ return this; }}
}};
const post = {{
  innerText: "Feed post\\nExample Author\\nnow •\\nOpenAI update with enough detail",
  textContent: "",
  dataset: {{urn: "urn:li:activity:7494766621761183744"}},
  contains() {{ return false; }},
  getAttribute(name) {{
    return name === "data-urn" ? "urn:li:activity:7494766621761183744" : null;
  }},
  querySelector() {{ return null; }},
  querySelectorAll(selector) {{
    return selector === "a[href]" ? [permalink, author] : [];
  }}
}};
const main = {{
  querySelectorAll(selector) {{
    return selector === "main [role=\\"listitem\\"]" ? [post] : [];
  }}
}};
const document = {{
  title: "Search | LinkedIn",
  body: {{innerText: post.innerText}},
  querySelector(selector) {{
    return selector === "main, [role=\\"main\\"], .scaffold-layout__main" ? main : null;
  }}
}};
const location = {{href: "https://www.linkedin.com/search/results/content/"}};
const result = {linkedin.EXTRACT_SCRIPT};
process.stdout.write(JSON.stringify(result));
"""
        completed = subprocess.run(
            ["node", "-e", harness],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        result = json.loads(completed.stdout)
        self.assertEqual("now •", result["candidates"][0]["timestamp"])

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

    def test_short_and_unmatched_posts_are_retained_with_diagnostic_signals(self):
        candidates = [
            post_candidate(text="robotic lawn mower"),
            post_candidate(
                text="Google DeepMind changed its leadership structure and operating model.",
                url="https://www.linkedin.com/feed/update/urn:li:activity:7351200000000000001/",
                urn="urn:li:activity:7351200000000000001",
            ),
        ]
        result = make_scraper(FakeAgentBrowserClient(candidates=candidates)).search(
            "robotic lawn mower", "2026-06-15", "2026-07-15"
        )

        self.assertIsNone(result["error_type"])
        self.assertEqual(2, len(result["items"]))
        self.assertEqual(
            ["short_text"],
            result["items"][0]["metadata"]["retrieval_signals"],
        )
        self.assertEqual(
            ["no_lexical_topic_overlap"],
            result["items"][1]["metadata"]["retrieval_signals"],
        )

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
