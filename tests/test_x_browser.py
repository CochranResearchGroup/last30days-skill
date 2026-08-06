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
        self.requests = []
        self.auth = auth
        self.candidates = candidates

    def acquire_workspace(self, request):
        self.requests.append(request)
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
                            "likes": "1.2K Likes",
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
    def test_uses_stable_user_scoped_x_profile_when_run_override_is_absent(self):
        from lib import x_browser

        client = FakeAgentBrowserClient()
        with (
            patch.object(x_browser, "CliAgentBrowserClient", return_value=client),
            patch.object(
                x_browser.agent_browser_config,
                "load_target_config",
                return_value={
                    "profile_id": "last30days-facebook",
                    "browser_build": "stealthcdp_chromium",
                    "browser_host": "remote_headed",
                    "view_stream_provider": "rdp_gateway",
                    "display_isolation": "private_virtual_display",
                },
            ),
        ):
            result = x_browser.search_x_browser(
                "OpenAI",
                "2026-06-20",
                "2026-07-20",
                depth="quick",
                config={
                    "LAST30DAYS_X_BROWSER_INITIAL_WAIT": "0",
                    "LAST30DAYS_X_BROWSER_SCROLL_WAIT": "0",
                    "_NOW": NOW,
                },
            )

        self.assertIsNone(result["error"])
        self.assertEqual("last30days-facebook", client.requests[0].profile_id)
        self.assertEqual("private_virtual_display", client.requests[0].display_isolation)

    def test_auth_gate_returns_the_direct_external_guacamole_url(self):
        from lib import x_browser

        external_url = "https://agent-browser.example/guacamole/#/client/direct-x"
        client = FakeAgentBrowserClient(auth=SimpleNamespace(
            authenticated=False,
            login_form=True,
            checkpoint=False,
            restricted=False,
            url="https://x.com/i/flow/login",
        ))
        original_acquire = client.acquire_workspace

        def acquire(request):
            workspace = original_acquire(request)
            workspace.operator_url = external_url
            return workspace

        client.acquire_workspace = acquire
        with patch.object(x_browser, "CliAgentBrowserClient", return_value=client):
            result = x_browser.search_x_browser(
                "OpenAI",
                "2026-06-20",
                "2026-07-20",
                depth="quick",
                config={"LAST30DAYS_X_BROWSER_PROFILE": "last30days-facebook"},
            )

        self.assertEqual("auth_required", result["error_type"])
        self.assertEqual(external_url, result["operator_url"])
        self.assertEqual(external_url, result["diagnostics"]["operator_url"])
        self.assertNotIn("127.0.0.1", result["operator_url"])

    def test_checkpoint_detection_does_not_treat_generic_challenge_copy_as_auth(self):
        from lib import x_browser

        self.assertNotIn("/challenge|checkpoint|", x_browser.AUTH_SCRIPT)
        self.assertIn("complete this challenge to continue", x_browser.AUTH_SCRIPT)
        self.assertIn("!authenticatedDom && checkpointBody", x_browser.AUTH_SCRIPT)
        self.assertIn("!authenticatedDom && checkpointBody", x_browser.PAGE_STATE_SCRIPT)

    def test_current_root_login_surface_is_classified_without_ambiguous_reload(self):
        from lib import x_browser

        for script in (x_browser.AUTH_SCRIPT, x_browser.PAGE_STATE_SCRIPT):
            self.assertIn("rootSignedOut", script)
            self.assertIn("happening now", script.casefold())
            self.assertIn("email or username", script.casefold())
            self.assertIn("rootSignedOut", script[script.index("login_"):])

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
                    "LAST30DAYS_AGENT_BROWSER_DISPLAY_ISOLATION": "shared_display",
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
        self.assertEqual(1200, result["items"][0]["engagement"]["likes"])
        self.assertEqual("rdp_gateway", client.requests[0].view_provider)
        self.assertEqual("shared_display", client.requests[0].display_isolation)
        self.assertEqual("https://x.com/home", client.requests[0].start_url)
        self.assertEqual("x", client.requests[0].target_service_id)

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
    def test_auth_probe_reloads_once_when_retained_x_tab_is_ambiguous(self):
        from lib import x_browser

        client = x_browser.CliAgentBrowserClient(timeout=45)
        workspace = x_browser.BrowserWorkspace(
            profile_id="last30days-facebook",
            browser_id="session:last30days-facebook",
            session_name="last30days-facebook",
        )
        responses = [
            {"tabs": [{"index": 0, "active": True, "url": "https://x.com/home"}]},
            {
                "url": "https://x.com/home",
                "authenticated_dom": False,
                "login_form": False,
                "checkpoint": False,
                "restricted": False,
            },
            {"url": "https://x.com/home", "title": "Home / X"},
            {
                "url": "https://x.com/home",
                "authenticated_dom": True,
                "login_form": False,
                "checkpoint": False,
                "restricted": False,
            },
        ]
        with (
            patch.object(client, "_invoke", side_effect=responses) as invoke,
            patch.object(x_browser.time, "sleep"),
        ):
            auth = client.inspect_auth(workspace)

        self.assertTrue(auth.authenticated)
        self.assertEqual(
            ["--session", "last30days-facebook", "open", "https://x.com/home"],
            invoke.call_args_list[2].args[0],
        )
        self.assertEqual(4, invoke.call_count)

    def test_auth_probe_does_not_reload_an_explicit_login_page(self):
        from lib import x_browser

        client = x_browser.CliAgentBrowserClient(timeout=45)
        workspace = x_browser.BrowserWorkspace(
            profile_id="last30days-facebook",
            browser_id="session:last30days-facebook",
            session_name="last30days-facebook",
        )
        responses = [
            {"tabs": [{"index": 0, "active": True, "url": "https://x.com/i/flow/login"}]},
            {
                "url": "https://x.com/i/flow/login",
                "authenticated_dom": False,
                "login_form": True,
                "checkpoint": False,
                "restricted": False,
            },
        ]
        with patch.object(client, "_invoke", side_effect=responses) as invoke:
            auth = client.inspect_auth(workspace)

        self.assertFalse(auth.authenticated)
        self.assertTrue(auth.login_form)
        self.assertEqual(2, invoke.call_count)

    def test_auth_probe_does_not_reload_an_explicit_checkpoint(self):
        from lib import x_browser

        client = x_browser.CliAgentBrowserClient(timeout=45)
        workspace = x_browser.BrowserWorkspace(
            profile_id="last30days-facebook",
            browser_id="session:last30days-facebook",
            session_name="last30days-facebook",
        )
        responses = [
            {"tabs": [{"index": 0, "active": True, "url": "https://x.com/account/access"}]},
            {
                "url": "https://x.com/account/access",
                "authenticated_dom": False,
                "login_form": False,
                "checkpoint": True,
                "restricted": False,
            },
        ]
        with patch.object(client, "_invoke", side_effect=responses) as invoke:
            auth = client.inspect_auth(workspace)

        self.assertFalse(auth.authenticated)
        self.assertTrue(auth.checkpoint)
        self.assertEqual(2, invoke.call_count)

    def test_auth_probe_opens_x_tab_when_shared_profile_has_none(self):
        from lib import x_browser

        client = x_browser.CliAgentBrowserClient(timeout=45)
        workspace = x_browser.BrowserWorkspace(
            profile_id="last30days-facebook",
            browser_id="session:last30days-facebook",
            session_name="last30days-facebook",
        )
        responses = [
            {"tabs": [{"index": 0, "active": True, "url": "https://www.linkedin.com/feed/"}]},
            {},
            {"authenticated_dom": True, "login_form": False, "checkpoint": False},
        ]
        with patch.object(client, "_invoke", side_effect=responses) as invoke:
            auth = client.inspect_auth(workspace)

        self.assertTrue(auth.authenticated)
        self.assertEqual(
            ["--session", "last30days-facebook", "tab", "new", "https://x.com/home"],
            invoke.call_args_list[1].args[0],
        )

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

        with patch.object(x_browser.agent_browser_config, "record_access_plan"):
            workspace = recorder._client.acquire_workspace(
                x_browser.BrowserWorkspaceRequest(
                    profile_id="last30days-facebook",
                    session_name="last30days-facebook",
                    browser_build="stealthcdp_chromium",
                    view_provider="rdp_gateway",
                    timeout=45,
                    display_isolation="shared_display",
                )
            )

        self.assertEqual("last30days-facebook", workspace.profile_id)
        self.assertIn("--target-service-id", recorder.calls[0])
        target_index = recorder.calls[0].index("--target-service-id")
        self.assertEqual("x", recorder.calls[0][target_index + 1])
        runtime_profile_index = recorder.calls[0].index("--runtime-profile")
        self.assertEqual(
            "last30days-facebook",
            recorder.calls[0][runtime_profile_index + 1],
        )
        display_index = recorder.calls[0].index("--display-isolation")
        self.assertEqual("shared_display", recorder.calls[0][display_index + 1])
        self.assertEqual("remote-view", recorder.calls[2][2])
        self.assertEqual("open", recorder.calls[2][3])
        self.assertIn("--view-stream-provider", recorder.calls[2])
        provider_index = recorder.calls[2].index("--view-stream-provider")
        self.assertEqual("rdp_gateway", recorder.calls[2][provider_index + 1])

    def test_acquisition_uses_broker_shared_owner_over_configured_session(self):
        from lib import x_browser

        plan = {
            "selectedProfile": {"id": "last30days-facebook"},
            "decision": {
                "manualActionRequired": False,
                "profileReuse": {
                    "recommendedAction": "reuse_existing_browser",
                    "sharedAcquisition": {
                        "mode": "tab_new",
                        "browserId": "session:last30days-facebook",
                        "sessionName": "last30days-facebook",
                    },
                },
            },
        }
        status = {
            "service_state": {
                "sessions": {
                    "default": {"profileId": "qbo-soylei", "browserIds": ["session:default"]},
                    "last30days-facebook": {
                        "profileId": "last30days-facebook",
                        "browserIds": ["session:last30days-facebook"],
                        "tabIds": ["target:x"],
                    },
                },
                "browsers": {
                    "session:last30days-facebook": {
                        "profileId": "last30days-facebook",
                        "health": "ready",
                    },
                },
                "tabs": {"target:x": {"targetId": "x", "url": "https://x.com/home"}},
            },
        }
        recorder = RecordingCliClient([plan, status])
        recorder._client._invoke = recorder.invoke

        with patch.object(x_browser.agent_browser_config, "record_access_plan"):
            workspace = recorder._client.acquire_workspace(
                x_browser.BrowserWorkspaceRequest(
                    profile_id="last30days-facebook",
                    session_name="default",
                    browser_build="stealthcdp_chromium",
                    view_provider="cdp_screencast",
                    timeout=45,
                )
            )

        self.assertEqual("session:last30days-facebook", workspace.browser_id)
        self.assertEqual("last30days-facebook", workspace.session_name)
        self.assertEqual("x", workspace.target_id)
        self.assertEqual(2, len(recorder.calls))

    def test_acquisition_reuses_cdp_owner_when_human_view_route_is_incompatible(self):
        from lib import x_browser

        plan = {
            "selectedProfile": {"id": "last30days-facebook"},
            "decision": {
                "manualActionRequired": False,
                "profileReuse": {
                    "recommendedAction": "wait_for_profile_lease",
                    "activeLeaseSessionIds": ["stored-last30days-social"],
                    "sameProfileLiveBrowserIds": [
                        "session:stored-last30days-social"
                    ],
                    "sharedAcquisition": {
                        "mode": None,
                        "browserId": None,
                        "sessionName": None,
                    },
                },
            },
        }
        status = {
            "service_state": {
                "sessions": {
                    "stored-last30days-social": {
                        "profileId": "last30days-facebook",
                        "browserIds": ["session:stored-last30days-social"],
                        "tabIds": ["target:x"],
                    },
                },
                "browsers": {
                    "session:stored-last30days-social": {
                        "profileId": "last30days-facebook",
                        "health": "ready",
                        "viewStreams": [
                            {
                                "provider": "cdp_screencast",
                                "controlInput": "cdp_input",
                                "readOnly": False,
                            }
                        ],
                    },
                },
                "tabs": {"target:x": {"targetId": "x", "url": "https://x.com/home"}},
            },
        }
        recorder = RecordingCliClient([plan, status])
        recorder._client._invoke = recorder.invoke

        with patch.object(x_browser.agent_browser_config, "record_access_plan"):
            workspace = recorder._client.acquire_workspace(
                x_browser.BrowserWorkspaceRequest(
                    profile_id="last30days-facebook",
                    session_name="last30days-facebook",
                    browser_build="stealthcdp_chromium",
                    view_provider="rdp_gateway",
                    control_input_provider="manual_attached_desktop",
                    timeout=45,
                )
            )

        self.assertEqual("session:stored-last30days-social", workspace.browser_id)
        self.assertEqual("stored-last30days-social", workspace.session_name)
        self.assertEqual("x", workspace.target_id)
        self.assertEqual("not_required", workspace.operator_visible_state)
        self.assertEqual(2, len(recorder.calls))

    def test_shared_owner_prefers_direct_external_guacamole_url(self):
        from lib import x_browser

        external_url = "https://agent-browser.example/guacamole/#/client/direct-x"
        plan = {
            "selectedProfile": {"id": "last30days-facebook"},
            "decision": {
                "manualActionRequired": False,
                "profileReuse": {
                    "recommendedAction": "reuse_existing_browser",
                    "sharedAcquisition": {
                        "mode": "tab_new",
                        "browserId": "session:last30days-facebook",
                        "sessionName": "last30days-facebook",
                    },
                },
            },
        }
        status = {
            "service_state": {
                "sessions": {
                    "last30days-facebook": {
                        "profileId": "last30days-facebook",
                        "browserIds": ["session:last30days-facebook"],
                        "tabIds": ["target:x"],
                    },
                },
                "browsers": {
                    "session:last30days-facebook": {
                        "profileId": "last30days-facebook",
                        "health": "ready",
                        "viewStreams": [{
                            "id": "guacamole:1",
                            "provider": "rdp_gateway",
                            "url": "http://127.0.0.1:8092/guacamole/#/client/local",
                            "publicOperatorUrl": external_url,
                            "readiness": {"state": "ready"},
                        }],
                    },
                },
                "tabs": {"target:x": {"targetId": "x", "url": "https://x.com/home"}},
            },
        }
        recorder = RecordingCliClient([plan, status])
        recorder._client._invoke = recorder.invoke

        with patch.object(x_browser.agent_browser_config, "record_access_plan"):
            workspace = recorder._client.acquire_workspace(
                x_browser.BrowserWorkspaceRequest(
                    profile_id="last30days-facebook",
                    session_name="last30days-facebook",
                    browser_build="stealthcdp_chromium",
                    view_provider="rdp_gateway",
                    timeout=45,
                )
            )

        self.assertEqual(external_url, workspace.operator_url)
        self.assertNotIn("127.0.0.1", workspace.operator_url)


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
