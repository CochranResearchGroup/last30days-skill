from datetime import datetime, timezone
import os
from types import SimpleNamespace
from unittest import TestCase, skipUnless
from unittest.mock import patch


NOW = datetime(2026, 7, 19, 12, 0, tzinfo=timezone.utc)


class FakeAgentBrowserClient:
    def __init__(self, *, auth=None, candidates=None):
        self.url = "https://x.com/home"
        self.actions = []
        self.auth = auth
        self.candidates = candidates

    def acquire_workspace(self, request):
        return SimpleNamespace(
            profile_id="last30days-facebook",
            browser_id="browser:x",
            session_name="last30days-facebook",
            target_id="target:x",
            route_id="",
            display_allocation_id="",
            operator_url="",
            operator_visible_state="ready",
        )

    def inspect_auth(self, workspace):
        if self.auth is not None:
            return self.auth
        return SimpleNamespace(
            authenticated=True,
            login_form=False,
            checkpoint=False,
            restricted=False,
            url=self.url,
        )

    def prepare_site_tab(self, workspace, hostname, *, consolidate=False):
        return True

    def snapshot(self, workspace):
        return SimpleNamespace(refs={}, text="")

    def act(self, workspace, action):
        self.actions.append(action)
        if action.operation in {"navigate", "new_tab"}:
            self.url = action.value
        return SimpleNamespace(url=self.url, title="OpenAI - Search / X")

    def evaluate(self, workspace, script):
        from lib import x_browser

        if script == x_browser.PAGE_STATE_SCRIPT:
            return {
                "url": self.url,
                "title": "OpenAI - Search / X",
                "query_value": "OpenAI since:2026-06-20 until:2026-07-20",
                "latest_selected": True,
                "article_count": 1,
                "no_results": False,
                "login_page": False,
                "checkpoint": False,
                "restricted": False,
                "error_page": False,
            }
        if script == x_browser.EXTRACT_SCRIPT:
            return {
                "url": self.url,
                "title": "OpenAI - Search / X",
                "candidates": self.candidates if self.candidates is not None else [
                    {
                        "text": "OpenAI shipped a new Codex workflow for long-running software tasks.",
                        "url": "https://x.com/OpenAI/status/2078123456789012345?ref_src=twsrc%5Etfw",
                        "author_handle": "OpenAI",
                        "timestamp": "2026-07-18T15:30:00.000Z",
                        "promoted": False,
                        "engagement": {
                            "replies": 12,
                            "reposts": 34,
                            "likes": 456,
                            "bookmarks": 7,
                            "views": 8901,
                        },
                    }
                ],
            }
        raise AssertionError("unexpected browser evaluation script")

    def operator_ingress_ready(self, operator_url):
        return True


class XBrowserSearchTests(TestCase):
    def test_search_emits_a_canonical_dated_relevant_post(self):
        from lib import x_browser

        client = FakeAgentBrowserClient()
        with patch.object(x_browser, "CliAgentBrowserClient", return_value=client):
            result = x_browser.search_x_browser(
                "OpenAI",
                "2026-06-20",
                "2026-07-20",
                depth="quick",
                config={
                    "LAST30DAYS_X_BROWSER_PROFILE": "last30days-facebook",
                    "LAST30DAYS_X_BROWSER_SESSION": "last30days-facebook",
                    "LAST30DAYS_X_BROWSER_INITIAL_WAIT": "0",
                    "LAST30DAYS_X_BROWSER_SCROLL_WAIT": "0",
                    "_NOW": NOW,
                },
            )

        self.assertIsNone(result["error"])
        self.assertEqual("last30days-facebook", result["profile"])
        self.assertEqual(1, len(result["items"]))
        self.assertEqual(
            "https://x.com/OpenAI/status/2078123456789012345",
            result["items"][0]["url"],
        )
        self.assertEqual("OpenAI", result["items"][0]["author_handle"])
        self.assertEqual("2026-07-18", result["items"][0]["date"])
        self.assertEqual(456, result["items"][0]["engagement"]["likes"])

    def test_checkpoint_stops_before_navigation_with_a_typed_failure(self):
        from lib import x_browser

        client = FakeAgentBrowserClient(auth=SimpleNamespace(
            authenticated=False,
            login_form=False,
            checkpoint=True,
            restricted=False,
            url="https://x.com/account/access",
        ))
        with patch.object(x_browser, "CliAgentBrowserClient", return_value=client):
            result = x_browser.search_x_browser(
                "OpenAI",
                "2026-06-20",
                "2026-07-20",
                depth="quick",
                config={"LAST30DAYS_X_BROWSER_PROFILE": "last30days-facebook"},
            )

        self.assertEqual("checkpoint_required", result["error_type"])
        self.assertEqual([], result["items"])
        self.assertEqual([], client.actions)

    def test_all_rejected_articles_return_quality_failure_with_reasons(self):
        from lib import x_browser

        client = FakeAgentBrowserClient(candidates=[{
            "text": "OpenAI sponsored announcement with enough text for the normal length gate.",
            "url": "https://x.com/advertiser/status/2078123456789012345",
            "author_handle": "advertiser",
            "timestamp": "2026-07-18T15:30:00.000Z",
            "promoted": True,
            "engagement": {},
        }])
        with patch.object(x_browser, "CliAgentBrowserClient", return_value=client):
            result = x_browser.search_x_browser(
                "OpenAI",
                "2026-06-20",
                "2026-07-20",
                depth="quick",
                config={"LAST30DAYS_X_BROWSER_PROFILE": "last30days-facebook"},
            )

        self.assertEqual("quality_gate_failed", result["error_type"])
        self.assertEqual([], result["items"])
        self.assertEqual({"promoted": 1}, result["diagnostics"]["rejection_counts"])

    def test_account_restriction_returns_rate_limited_before_navigation(self):
        from lib import x_browser

        client = FakeAgentBrowserClient(auth=SimpleNamespace(
            authenticated=False,
            login_form=False,
            checkpoint=False,
            restricted=True,
            url="https://x.com/home",
        ))
        with patch.object(x_browser, "CliAgentBrowserClient", return_value=client):
            result = x_browser.search_x_browser(
                "OpenAI",
                "2026-06-20",
                "2026-07-20",
                depth="quick",
                config={"LAST30DAYS_X_BROWSER_PROFILE": "last30days-facebook"},
            )

        self.assertEqual("rate_limited", result["error_type"])
        self.assertEqual([], result["items"])
        self.assertEqual([], client.actions)

    def test_agent_browser_cli_failure_is_returned_as_a_typed_source_error(self):
        from lib import facebook, x_browser

        client = FakeAgentBrowserClient()
        client.acquire_workspace = lambda request: (_ for _ in ()).throw(
            facebook.FacebookScraperFailure("agent_browser_error", "browser unavailable")
        )
        with patch.object(x_browser, "CliAgentBrowserClient", return_value=client):
            result = x_browser.search_x_browser(
                "OpenAI",
                "2026-06-20",
                "2026-07-20",
                depth="quick",
                config={"LAST30DAYS_X_BROWSER_PROFILE": "last30days-facebook"},
            )

        self.assertEqual("agent_browser_error", result["error_type"])
        self.assertEqual([], result["items"])


class RecordingCliClient:
    def __init__(self, responses):
        from lib import x_browser

        self._client = x_browser.CliAgentBrowserClient(timeout=45)
        self.responses = list(responses)
        self.calls = []

    def invoke(self, args, *, timeout, input_text=None):
        self.calls.append(list(args))
        if not self.responses:
            raise AssertionError(f"unexpected agent-browser call: {args}")
        return self.responses.pop(0)


class XBrowserAcquisitionTests(TestCase):
    def test_acquisition_resolves_the_authenticated_x_profile_by_target_identity(self):
        from lib import x_browser

        recorder = RecordingCliClient([
            {
                "selectedProfile": {"id": "last30days-facebook"},
                "decision": {"manualActionRequired": False},
            },
            {"service_state": {"sessions": {}, "browsers": {}, "tabs": {}}},
            {
                "profileId": "last30days-facebook",
                "browserId": "browser:x",
                "sessionName": "last30days-facebook",
                "targetId": "target:x",
                "operatorVisible": {"state": "ready"},
            },
        ])
        recorder._client._invoke = recorder.invoke

        workspace = recorder._client.acquire_workspace(
            x_browser.BrowserWorkspaceRequest(
                profile_id="last30days-facebook",
                session_name="last30days-facebook",
                browser_build="stealthcdp_chromium",
                view_provider="rdp_gateway",
                timeout=45,
            )
        )

        self.assertEqual("last30days-facebook", workspace.profile_id)
        self.assertIn("--target-service-id", recorder.calls[0])
        target_index = recorder.calls[0].index("--target-service-id")
        self.assertEqual("x", recorder.calls[0][target_index + 1])


class XBrowserIntegrationTests(TestCase):
    @patch("shutil.which", return_value="/usr/local/bin/agent-browser")
    def test_explicit_browser_backend_requires_the_opt_in(self, _which):
        from lib import env

        self.assertIsNone(env.get_x_source({"LAST30DAYS_X_BACKEND": "browser"}))
        self.assertEqual(
            "browser",
            env.get_x_source({
                "LAST30DAYS_X_BACKEND": "browser",
                "LAST30DAYS_X_BROWSER": "1",
            }),
        )
        self.assertEqual(
            "browser",
            env.get_x_source({"LAST30DAYS_X_BROWSER": "true", "XAI_API_KEY": "dummy"}),
        )

    def test_pipeline_dispatches_x_to_the_browser_adapter(self):
        from lib import pipeline, schema, x_browser

        response = {"items": [{"url": "https://x.com/OpenAI/status/1"}], "error": None}
        runtime = schema.ProviderRuntime(
            reasoning_provider="local",
            planner_model="deterministic",
            rerank_model="local-score",
            x_search_backend="browser",
        )
        subquery = schema.SubQuery(
            label="primary",
            search_query="OpenAI",
            ranking_query="OpenAI",
            sources=["x"],
            weight=1.0,
        )
        with patch.object(x_browser, "search_x_browser", return_value=response) as search:
            items, artifact = pipeline._retrieve_stream(
                topic="OpenAI",
                subquery=subquery,
                source="x",
                config={"LAST30DAYS_X_BROWSER": "1"},
                depth="quick",
                date_range=("2026-06-20", "2026-07-20"),
                runtime=runtime,
                mock=False,
            )

        self.assertEqual(response["items"], items)
        self.assertEqual({}, artifact)
        search.assert_called_once_with(
            "OpenAI", "2026-06-20", "2026-07-20", depth="quick",
            config={"LAST30DAYS_X_BROWSER": "1"},
        )


@skipUnless(os.getenv("LAST30DAYS_X_BROWSER_LIVE_SMOKE") == "1", "opt-in live X smoke")
class XBrowserLiveSmokeTests(TestCase):
    def test_three_queries_reuse_the_authenticated_profile_and_emit_quality_posts(self):
        from lib import x_browser

        config = {
            "LAST30DAYS_X_BROWSER": "1",
            "LAST30DAYS_X_BROWSER_PROFILE": os.getenv(
                "LAST30DAYS_X_BROWSER_PROFILE", "last30days-facebook"
            ),
            "LAST30DAYS_X_BROWSER_SESSION": os.getenv(
                "LAST30DAYS_X_BROWSER_SESSION", "last30days-facebook"
            ),
            "LAST30DAYS_X_BROWSER_INITIAL_WAIT": "1",
            "LAST30DAYS_X_BROWSER_SCROLL_WAIT": "0",
        }
        sessions = set()
        for topic in ("OpenAI", "regenerative agriculture", "robotic lawn mower"):
            result = x_browser.search_x_browser(
                topic, "2026-06-20", "2026-07-20", depth="quick", config=config
            )
            self.assertIsNone(result.get("error_type"), result)
            self.assertGreater(len(result["items"]), 0, result)
            sessions.add(result["session"])
            for item in result["items"]:
                self.assertIsNotNone(x_browser._canonical_status_url(item["url"]))
                self.assertTrue(item["author_handle"])
                self.assertTrue(item["date"])
        self.assertEqual({config["LAST30DAYS_X_BROWSER_SESSION"]}, sessions)
