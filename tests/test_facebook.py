import json
import os
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock
from urllib.parse import urlsplit

from lib import facebook, normalize, pipeline


FIXTURES = Path(__file__).parent / "fixtures" / "facebook"
NOW = datetime(2026, 7, 15, 12, 0, tzinfo=timezone.utc)


def fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def request(**overrides):
    values = {
        "profile_id": "last30days-facebook",
        "session_name": "last30days-facebook",
        "browser_build": "stealthcdp_chromium",
        "view_provider": "rdp_gateway",
        "timeout": 30,
    }
    values.update(overrides)
    return facebook.BrowserWorkspaceRequest(**values)


def access_plan(*, profile_id="last30days-facebook", shared_owner=None, remote_view=True):
    reuse = {"recommendedAction": "launch_new_browser"}
    if shared_owner:
        browser_id, session_name = shared_owner
        reuse = {
            "recommendedAction": "reuse_existing_browser",
            "sharedAcquisition": {
                "mode": "tab_new",
                "browserId": browser_id,
                "sessionName": session_name,
            },
        }
    return {
        "selectedProfile": {"id": profile_id},
        "decision": {
            "profileReuse": reuse,
            "launchPosture": {"remoteViewRecommended": remote_view},
        },
    }


class FakeAgentBrowserClient:
    def __init__(self, *, page=None, candidates=None, auth=None, snapshots=None):
        self.workspace = facebook.BrowserWorkspace(
            profile_id="last30days-facebook",
            browser_id="browser-1",
            session_name="last30days-facebook",
            target_id="target-1",
            route_id="route-1",
            operator_url="https://operator.example/opaque-token",
            operator_visible_state="ready",
        )
        self.auth = auth or facebook.FacebookAuthState(authenticated=True, has_c_user=True, has_xs=True)
        self.page = page or fixture("mixed_search.json")["page"]
        self.candidates = candidates if candidates is not None else fixture("mixed_search.json")["candidates"]
        self.snapshots = list(snapshots or [
            facebook.BrowserSnapshot(refs={"e1": {"role": "combobox", "name": "Search Facebook"}}),
            facebook.BrowserSnapshot(refs={"e2": {"role": "button", "name": "Recent posts"}}),
        ])
        self.actions = []
        self.closed_site_targets = []
        self.acquisitions = 0
        self.ingress_ready = True
        self.command_timings = [{"operation": "snapshot", "duration_ms": 4, "status": "ok"}]

    def acquire_workspace(self, workspace_request):
        self.acquisitions += 1
        if workspace_request.profile_id != self.workspace.profile_id:
            raise facebook.FacebookScraperFailure("profile_mismatch", "wrong profile")
        return self.workspace

    def inspect_auth(self, workspace):
        return self.auth

    def snapshot(self, workspace):
        return self.snapshots.pop(0) if self.snapshots else facebook.BrowserSnapshot()

    def act(self, workspace, action):
        self.actions.append(action)
        if action.operation == "click" and "filters=" not in self.page["url"]:
            self.page["url"] += f"&filters={facebook.RECENT_POSTS_FILTER}"
        if action.operation in {"navigate", "new_tab"} and action.value:
            self.page["url"] = action.value
        return facebook.BrowserState()

    def evaluate(self, workspace, script):
        if script == facebook.PAGE_STATE_SCRIPT:
            return dict(self.page)
        if script == facebook.EXTRACT_SCRIPT:
            return {"url": self.page["url"], "title": self.page["title"], "candidates": self.candidates}
        raise AssertionError("unexpected script")

    def evaluate_navigation_state(self, workspace, script):
        return self.evaluate(workspace, script)

    def replace_active_site_target(self, workspace, hostname):
        self.closed_site_targets.append(hostname)
        self.act(workspace, facebook.BrowserAction("new_tab", value="about:blank"))
        return True

    def operator_ingress_ready(self, operator_url):
        return self.ingress_ready


def make_scraper(client, **overrides):
    values = {"limit": 20, "scrolls": 0, "initial_wait": 0, "scroll_wait": 0, "now": NOW}
    values.update(overrides)
    return facebook.FacebookScraper(client, request(), **values)


class FacebookAvailabilityTests(unittest.TestCase):
    def test_facebook_is_not_available_by_default(self):
        self.assertNotIn("facebook", pipeline.available_sources({}, requested_sources=["facebook"]))

    def test_facebook_requires_enable_flag_and_agent_browser(self):
        config = {"LAST30DAYS_FACEBOOK_BROWSER": "1"}
        with mock.patch("shutil.which", return_value="/usr/bin/agent-browser"):
            self.assertIn("facebook", pipeline.available_sources(config, requested_sources=["facebook"]))

    def test_facebook_must_be_requested(self):
        config = {"LAST30DAYS_FACEBOOK_BROWSER": "1"}
        with mock.patch("shutil.which", return_value="/usr/bin/agent-browser"):
            self.assertNotIn("facebook", pipeline.available_sources(config))


class FacebookCliAdapterTests(unittest.TestCase):
    def test_unresponsive_auth_recovery_prepares_one_query_capture(self):
        client = facebook.CliAgentBrowserClient(timeout=45, job_timeout_ms=120_000)
        workspace = facebook.BrowserWorkspace(
            profile_id="last30days-facebook",
            browser_id="browser-1",
            session_name="shared-social",
        )
        query_url = facebook._search_url("OpenAI", recent=True)
        tabs = {"tabs": [{"index": 3, "active": True, "url": query_url}]}
        timeout = facebook.FacebookScraperFailure(
            "agent_browser_timeout", "retained target did not respond"
        )
        capture = {
            "auth": {"authenticated_dom": True, "has_c_user": True, "has_xs": True},
            "page": {"url": query_url, "title": "OpenAI - Search Results"},
            "extraction": {"candidates": [{"text": "OpenAI field report"}]},
        }
        client.prepare_query_capture_url(query_url)

        with mock.patch.object(client, "_invoke", return_value=tabs), mock.patch.object(
            client, "_probe_retained_facebook_auth", side_effect=timeout
        ), mock.patch.object(
            client, "replace_active_site_target", return_value=True
        ), mock.patch.object(client, "act") as act, mock.patch.object(
            client, "_evaluate_query_capture", return_value=capture
        ) as evaluate:
            auth = client.inspect_auth(workspace)

        self.assertTrue(auth.authenticated)
        act.assert_called_once_with(
            workspace, facebook.BrowserAction("navigate", value=query_url)
        )
        evaluate.assert_called_once_with(workspace)
        self.assertEqual(capture["page"], client.prepared_query_page(workspace))
        self.assertEqual(
            capture["extraction"],
            client.consume_prepared_query_extraction(workspace),
        )
        self.assertIsNone(client.prepared_query_page(workspace))

    def test_observed_replacement_auth_then_later_open_keeps_recovery_budget(self):
        class ObservedAuthRecoveryClient(facebook.CliAgentBrowserClient):
            def __init__(self):
                super().__init__(timeout=45, job_timeout_ms=120_000)
                self.remaining = 105
                self.auth_evaluations = 0
                self.commands = []

            def _consume(self, seconds):
                if seconds > self.remaining:
                    raise facebook.FacebookScraperFailure(
                        "agent_browser_timeout",
                        f"observed operation exceeded remaining {self.remaining}s budget",
                    )
                self.remaining -= seconds

            def _invoke(self, args, *, timeout, input_text=None):
                self.commands.append(args)
                if args[-2:] == ["tab", "list"]:
                    self._consume(3 if self.auth_evaluations == 0 else 9)
                    return {"tabs": [{
                        "index": 0,
                        "active": True,
                        "url": "https://www.facebook.com/",
                    }]}
                if "eval" in args:
                    self.auth_evaluations += 1
                    if self.auth_evaluations == 1:
                        self._consume(15)
                        raise facebook.FacebookScraperFailure(
                            "agent_browser_timeout",
                            "retained target did not respond",
                        )
                    self._consume(9)
                    return {
                        "authenticated_dom": True,
                        "has_c_user": True,
                        "has_xs": True,
                    }
                if args[-3:-1] == ["tab", "new"]:
                    self._consume(9)
                    return {"url": args[-1]}
                if len(args) >= 3 and args[-3:-1] == ["tab", "close"]:
                    self._consume(9)
                    return {}
                if "open" in args:
                    self._consume(17 if args[-1] == "https://www.facebook.com/" else 15)
                    return {"url": args[-1]}
                return {}

        client = ObservedAuthRecoveryClient()
        workspace = facebook.BrowserWorkspace(
            profile_id="last30days-facebook",
            browser_id="browser-1",
            session_name="shared-social",
        )

        auth = client.inspect_auth(workspace)
        client.act(
            workspace,
            facebook.BrowserAction(
                "navigate",
                value=facebook._search_url("robotic lawn mower", recent=True),
            ),
        )

        self.assertTrue(auth.authenticated)
        self.assertGreaterEqual(client.remaining, 15)
        replacement_commands = client.commands[2:6]
        self.assertEqual(
            [
                ["--session", "shared-social", "tab", "list"],
                ["--session", "shared-social", "tab", "new", "about:blank"],
                ["--session", "shared-social", "tab", "close", "0"],
                [
                    "--session",
                    "shared-social",
                    "--job-timeout-ms",
                    "25000",
                    "open",
                    "https://www.facebook.com/",
                ],
            ],
            replacement_commands,
        )

    def test_run_budget_exhaustion_stops_before_another_browser_command(self):
        client = facebook.CliAgentBrowserClient(timeout=30)
        client._run_deadline = 10.0

        with mock.patch.object(facebook.time, "monotonic", return_value=11.0), mock.patch.object(
            facebook.subprocess, "run"
        ) as run:
            with self.assertRaises(facebook.FacebookScraperFailure) as raised:
                client._invoke(["--session", "shared-social", "tab", "list"], timeout=30)

        self.assertEqual("agent_browser_timeout", raised.exception.error_type)
        self.assertIn("run budget", str(raised.exception))
        run.assert_not_called()

    def test_auth_tab_inventory_allows_observed_service_latency(self):
        client = facebook.CliAgentBrowserClient(timeout=45)
        workspace = facebook.BrowserWorkspace(
            profile_id="last30days-facebook",
            browser_id="browser-1",
            session_name="last30days-facebook",
        )
        auth = facebook.FacebookAuthState(authenticated=True, has_c_user=True)

        with mock.patch.object(client, "_invoke", return_value={"tabs": []}) as invoke, mock.patch.object(
            client, "_inspect_auth_on_fresh_target", return_value=auth
        ):
            observed = client.inspect_auth(workspace)

        self.assertEqual(auth, observed)
        self.assertEqual(20, invoke.call_args.kwargs["timeout"])

    def test_tab_inventory_allowance_remains_clamped_by_run_budget(self):
        client = facebook.CliAgentBrowserClient(timeout=45)
        client._run_deadline = 17.1
        completed = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout='{"success": true, "data": {"tabs": []}}',
            stderr="",
        )

        with mock.patch.object(facebook.time, "monotonic", side_effect=[10.0, 10.1]), mock.patch.object(
            facebook.subprocess, "run", return_value=completed
        ) as run:
            client._invoke(
                ["--session", "last30days-facebook", "tab", "list"],
                timeout=facebook.TAB_INVENTORY_TIMEOUT_SECONDS,
            )

        self.assertEqual(8, run.call_args.kwargs["timeout"])

    def test_replace_active_site_target_opens_successor_then_closes_exact_predecessor(self):
        client = facebook.CliAgentBrowserClient(timeout=30)
        workspace = facebook.BrowserWorkspace(
            profile_id="last30days-facebook",
            browser_id="browser-1",
            session_name="last30days-facebook",
        )
        listed = {
            "tabs": [
                {"index": 2, "active": False, "url": "https://example.com/"},
                {"index": 3, "active": True, "url": "https://www.facebook.com/search/top/?q=OpenAI"},
            ]
        }
        with mock.patch.object(client, "_invoke", side_effect=[listed, {}, {}]) as invoke:
            self.assertTrue(client.replace_active_site_target(workspace, "facebook.com"))

        self.assertEqual(
            [
                ["--session", workspace.session_name, "tab", "list"],
                ["--session", workspace.session_name, "tab", "new", "about:blank"],
                ["--session", workspace.session_name, "tab", "close", "3"],
            ],
            [call.args[0] for call in invoke.call_args_list],
        )
        self.assertEqual(
            facebook.TAB_INVENTORY_TIMEOUT_SECONDS,
            invoke.call_args_list[0].kwargs["timeout"],
        )

    def test_evaluate_orders_inner_job_timeout_before_subprocess_deadline(self):
        client = facebook.CliAgentBrowserClient(timeout=30)
        workspace = facebook.BrowserWorkspace(
            profile_id="last30days-facebook",
            browser_id="browser-1",
            session_name="last30days-facebook",
        )
        with mock.patch.object(client, "_invoke", return_value={"result": {}}) as invoke:
            client.evaluate(workspace, "document.title")

        command = invoke.call_args.args[0]
        inner_ms = int(command[command.index("--job-timeout-ms") + 1])
        outer_seconds = invoke.call_args.kwargs["timeout"]
        self.assertEqual(20_000, inner_ms)
        self.assertGreater(outer_seconds * 1000, inner_ms)
        self.assertGreaterEqual(outer_seconds * 1000 - inner_ms, 5_000)

    def test_navigation_evaluation_preserves_one_recovery_reserve(self):
        client = facebook.CliAgentBrowserClient(timeout=45, job_timeout_ms=120_000)
        workspace = facebook.BrowserWorkspace(
            profile_id="last30days-facebook",
            browser_id="browser-1",
            session_name="shared-social",
        )
        with mock.patch.object(client, "_invoke", return_value={"result": {}}) as invoke:
            client.evaluate_navigation_state(workspace, facebook.PAGE_STATE_SCRIPT)

        command = invoke.call_args.args[0]
        self.assertEqual("3000", command[command.index("--job-timeout-ms") + 1])
        self.assertEqual(12, invoke.call_args.kwargs["timeout"])

    def test_combined_query_capture_uses_available_adapter_budget(self):
        client = facebook.CliAgentBrowserClient(timeout=105, job_timeout_ms=105_000)
        workspace = facebook.BrowserWorkspace(
            profile_id="last30days-facebook",
            browser_id="browser-1",
            session_name="last30days-facebook",
        )
        with mock.patch.object(
            client,
            "_invoke",
            return_value={"result": {"auth": {}, "page": {}, "extraction": {}}},
        ) as invoke:
            client._evaluate_query_capture(workspace)

        command = invoke.call_args.args[0]
        self.assertEqual("45000", command[command.index("--job-timeout-ms") + 1])
        self.assertEqual(50, invoke.call_args.kwargs["timeout"])


    def test_extract_script_does_not_rescan_every_ancestor_subtree(self):
        self.assertNotIn("parent.querySelectorAll(actionSelector)", facebook.EXTRACT_SCRIPT)

    def test_extract_script_models_current_action_cards_and_rendered_glyph_time(self):
        self.assertIn(
            "const actionSelector = '[aria-label^=\"Actions for this post\"]'",
            facebook.EXTRACT_SCRIPT,
        )
        self.assertIn("const renderedGlyphText", facebook.EXTRACT_SCRIPT)
        self.assertIn("isTimestampLabel(renderedGlyphText(a))", facebook.EXTRACT_SCRIPT)
        self.assertIn("isSponsoredLabel(renderedGlyphText(a))", facebook.EXTRACT_SCRIPT)

    def test_checkpoint_text_is_gated_by_missing_authenticated_dom(self):
        for script in (facebook.AUTH_SCRIPT, facebook.PAGE_STATE_SCRIPT):
            self.assertIn("const authenticatedDom", script)
            self.assertIn(
                "checkpointPath || checkpointForm || (!authenticatedDom && checkpointBody)",
                script,
            )
            self.assertNotIn("two-factor authentication", script)

    def test_rate_limit_scripts_require_structural_block_surface(self):
        for script in (facebook.AUTH_SCRIPT, facebook.PAGE_STATE_SCRIPT):
            self.assertIn("rate_limited", script)
            self.assertIn("rate_limit_reason", script)
            self.assertIn("!hasPostActions", script)
        self.assertIn("rate_limited", facebook.EXTRACT_SCRIPT)
        self.assertIn("rate_limit_reason", facebook.EXTRACT_SCRIPT)

    def test_page_state_scripts_bound_layout_free_surface_reads(self):
        for script in (
            facebook.AUTH_SCRIPT,
            facebook.PAGE_STATE_SCRIPT,
            facebook.EXTRACT_SCRIPT,
        ):
            self.assertIn("surface?.textContent", script)
            self.assertIn(".slice(0, 40000)", script)
            self.assertNotIn("document.body?.innerText", script)

        self.assertIn(".slice(0, 64)", facebook.PAGE_STATE_SCRIPT)
        self.assertNotIn(
            "'[role=\"tab\"], [role=\"button\"], a'",
            facebook.PAGE_STATE_SCRIPT,
        )

    def test_rate_limited_auth_is_explicit_and_overrides_cookie_evidence(self):
        auth = facebook._facebook_auth_state(
            {
                "authenticated_dom": True,
                "has_c_user": True,
                "rate_limited": True,
                "rate_limit_reason": "temporary_block",
            }
        )

        self.assertFalse(auth.authenticated)
        self.assertTrue(auth.rate_limited)
        self.assertTrue(facebook._facebook_auth_is_explicit(auth))

    def test_prepare_operator_handoff_requires_doctor_and_visible_ready_proof(self):
        client = facebook.CliAgentBrowserClient(timeout=5, job_timeout_ms=120_000)
        workspace = facebook.BrowserWorkspace(
            profile_id="last30days-facebook",
            browser_id="browser-1",
            session_name="stored-last30days-social",
            target_id="target-1",
            operator_visible_state="not_required",
        )
        opened = {
            "browserId": "browser-1",
            "sessionName": "stored-last30days-social",
            "targetId": "target-1",
            "routeId": "route-1",
            "operatorVisible": {
                "state": "ready",
                "browserId": "browser-1",
                "sessionName": "stored-last30days-social",
                "targetId": "target-1",
                "routeId": "route-1",
                "externalUrl": "https://operator.example/guacamole/client-1",
            },
        }

        with mock.patch.object(
            client,
            "_invoke",
            side_effect=[{"status": "ready", "remoteControl": {"status": "ready"}}, opened],
        ) as invoke:
            prepared = client.prepare_operator_handoff(workspace, request())

        self.assertEqual("ready", prepared.operator_visible_state)
        self.assertEqual(
            "https://operator.example/guacamole/client-1", prepared.operator_url
        )
        self.assertEqual(["doctor", "remote-view"], invoke.call_args_list[0].args[0])
        command = invoke.call_args_list[1].args[0]
        self.assertIn("remote-view", command)
        self.assertEqual("browser-1", command[command.index("--browser-id") + 1])
        self.assertEqual(
            "stored-last30days-social",
            command[command.index("--session-name") + 1],
        )

    def test_prepare_operator_handoff_stops_when_remote_control_is_not_ready(self):
        client = facebook.CliAgentBrowserClient(timeout=5)
        workspace = facebook.BrowserWorkspace(
            profile_id="last30days-facebook",
            browser_id="browser-1",
            session_name="stored-last30days-social",
            operator_visible_state="not_required",
        )
        with mock.patch.object(
            client,
            "_invoke",
            return_value={
                "status": "ready",
                "remoteControl": {"status": "needs_browser_launch_prerequisites"},
            },
        ) as invoke, self.assertRaisesRegex(
            facebook.FacebookScraperFailure, "remote control is not ready"
        ):
            client.prepare_operator_handoff(workspace, request())

        self.assertEqual(1, invoke.call_count)

    @mock.patch.object(
        facebook.CliAgentBrowserClient,
        "_invoke",
    )
    def test_prepare_operator_handoff_rejects_nonready_or_local_routes(self, invoke):
        client = facebook.CliAgentBrowserClient(timeout=5)
        workspace = facebook.BrowserWorkspace(
            profile_id="last30days-facebook",
            browser_id="browser-1",
            session_name="stored-last30days-social",
            operator_visible_state="not_required",
        )
        invoke.side_effect = [
            {"status": "ready", "remoteControl": {"status": "ready"}},
            {
                "browserId": "browser-1",
                "operatorVisible": {
                    "state": "ready",
                    "externalUrl": "https://localhost/client/manual-auth",
                },
            },
        ]

        with self.assertRaisesRegex(
            facebook.FacebookScraperFailure, "ready external operator handoff"
        ):
            client.prepare_operator_handoff(workspace, request())

    def test_access_plan_receives_the_requested_remote_view_transport(self):
        client = facebook.CliAgentBrowserClient(timeout=5)
        plan = access_plan(shared_owner=("browser-1", "shared-social"))
        status = {"service_state": {"sessions": {}, "browsers": {}, "tabs": {}}}

        with mock.patch.object(
            client, "_invoke", side_effect=[plan, status]
        ) as invoke, mock.patch.object(
            facebook.agent_browser_config, "record_access_plan"
        ):
            client.acquire_workspace(request(display_isolation="shared_display"))

        command = invoke.call_args_list[0].args[0]
        self.assertEqual("shared_display", command[command.index("--display-isolation") + 1])
        self.assertEqual("remote_headed", command[command.index("--browser-host") + 1])
        self.assertEqual("rdp_gateway", command[command.index("--view-stream-provider") + 1])
        self.assertEqual(
            "manual_attached_desktop",
            command[command.index("--control-input-provider") + 1],
        )

    def test_prepare_site_tab_selects_one_and_closes_only_same_site_duplicates(self):
        client = facebook.CliAgentBrowserClient(timeout=5)
        workspace = facebook.BrowserWorkspace(
            profile_id="last30days-facebook",
            browser_id="browser-1",
            session_name="shared-social",
        )
        tabs = {"tabs": [
            {"index": 0, "active": False, "url": "https://www.facebook.com/search/top?q=one"},
            {"index": 1, "active": False, "url": "https://www.facebook.com/search/top?q=two"},
            {"index": 2, "active": False, "url": "https://www.facebook.com/search/top?q=three"},
            {"index": 3, "active": True, "url": "https://www.linkedin.com/feed/"},
        ]}
        with mock.patch.object(client, "_invoke", side_effect=[tabs, {}, {}, {}]) as invoke:
            self.assertTrue(client.prepare_site_tab(workspace, "facebook.com", consolidate=True))
        self.assertEqual(
            [
                ["--session", "shared-social", "tab", "list"],
                ["--session", "shared-social", "tab", "2"],
                ["--session", "shared-social", "tab", "close", "1"],
                ["--session", "shared-social", "tab", "close", "0"],
            ],
            [call.args[0] for call in invoke.call_args_list],
        )

    def test_navigate_action_reuses_current_tab(self):
        client = facebook.CliAgentBrowserClient(timeout=30, job_timeout_ms=120_000)
        workspace = facebook.BrowserWorkspace(
            profile_id="last30days-facebook", browser_id="browser-1", session_name="shared-social"
        )
        with mock.patch.object(client, "_invoke", return_value={}) as invoke:
            client.act(workspace, facebook.BrowserAction("navigate", value="https://www.facebook.com/"))
        self.assertEqual(
            [
                "--session",
                "shared-social",
                "--job-timeout-ms",
                "25000",
                "open",
                "https://www.facebook.com/",
            ],
            invoke.call_args.args[0],
        )
        self.assertEqual(30, invoke.call_args.kwargs["timeout"])

    def test_auth_inspection_opens_facebook_tab_when_shared_owner_has_none(self):
        client = facebook.CliAgentBrowserClient(timeout=5)
        workspace = facebook.BrowserWorkspace(
            profile_id="last30days-facebook",
            browser_id="browser-1",
            session_name="shared-social",
        )
        with mock.patch.object(
            client,
            "_invoke",
            side_effect=[
                {"tabs": [
                    {"index": 0, "active": True, "url": "https://x.com/home"},
                ]},
                {},
                {"authenticated_dom": True, "has_c_user": True, "has_xs": True},
            ],
        ) as invoke:
            auth = client.inspect_auth(workspace)

        self.assertTrue(auth.authenticated)
        self.assertEqual(
            [
                "--session",
                "shared-social",
                "tab",
                "new",
                "https://www.facebook.com/",
            ],
            invoke.call_args_list[1].args[0],
        )
        self.assertIn("eval", invoke.call_args_list[2].args[0])

    def test_auth_inspection_skips_frozen_target_and_reuses_responsive_retained_target(self):
        client = facebook.CliAgentBrowserClient(timeout=8)
        workspace = facebook.BrowserWorkspace(
            profile_id="last30days-facebook",
            browser_id="browser-1",
            session_name="shared-social",
        )
        retained_tabs = {"tabs": [
            {
                "index": 5,
                "active": False,
                "url": "https://www.facebook.com/search/top/?q=OpenAI",
            },
            {"index": 7, "active": True, "url": "https://www.facebook.com/"},
        ]}

        eval_count = 0

        def invoke(args, **_kwargs):
            nonlocal eval_count
            if args[-2:] == ["tab", "list"]:
                return retained_tabs
            if "eval" in args:
                eval_count += 1
                if eval_count == 1:
                    raise facebook.FacebookScraperFailure(
                        "agent_browser_timeout", "retained target did not respond"
                    )
                return {"authenticated_dom": True, "has_c_user": True}
            return {}

        with mock.patch.object(
            client,
            "_invoke",
            side_effect=invoke,
        ) as invoke:
            auth = client.inspect_auth(workspace)

        self.assertTrue(auth.authenticated)
        commands = [call.args[0] for call in invoke.call_args_list]
        self.assertNotIn("new", [part for command in commands for part in command])
        self.assertIn(
            ["--session", "shared-social", "--job-timeout-ms", "3000", "tab", "5"],
            commands,
        )
        self.assertEqual(2, sum("eval" in command for command in commands))

    def test_auth_inspection_reuses_active_facebook_target_before_page_enable(self):
        client = facebook.CliAgentBrowserClient(timeout=5)
        workspace = facebook.BrowserWorkspace(
            profile_id="last30days-facebook",
            browser_id="browser-1",
            session_name="shared-social",
        )
        refreshed_tabs = {"tabs": [
            {
                "index": 0,
                "active": False,
                "url": "https://www.facebook.com/search/top/?q=OpenAI",
            },
            {"index": 1, "active": True, "url": "https://www.facebook.com/"},
        ]}

        def invoke(args, **_kwargs):
            if args[-2:] == ["tab", "list"]:
                return refreshed_tabs
            if "eval" in args:
                return {"authenticated_dom": True, "has_c_user": True, "has_xs": True}
            return {}

        with mock.patch.object(client, "_invoke", side_effect=invoke) as invoked:
            auth = client.inspect_auth(workspace)

        self.assertTrue(auth.authenticated)
        commands = [call.args[0] for call in invoked.call_args_list]
        self.assertNotIn("new", [part for command in commands for part in command])
        self.assertFalse(any(command[-2:] == ["tab", "1"] for command in commands))

    def test_auth_inspection_recovers_all_frozen_retained_targets_on_one_fresh_target(self):
        client = facebook.CliAgentBrowserClient(timeout=8)
        workspace = facebook.BrowserWorkspace(
            profile_id="last30days-facebook",
            browser_id="browser-1",
            session_name="shared-social",
        )
        tabs = {"tabs": [
            {"index": 0, "active": True, "url": "https://www.facebook.com/"},
        ]}
        eval_count = 0

        def invoke(args, **_kwargs):
            nonlocal eval_count
            if args[-2:] == ["tab", "list"]:
                return tabs
            if "eval" in args:
                eval_count += 1
                if eval_count == 1:
                    raise facebook.FacebookScraperFailure(
                        "agent_browser_timeout", "retained target did not respond"
                    )
                return {"authenticated_dom": True, "has_c_user": True}
            return {}

        with mock.patch.object(client, "_invoke", side_effect=invoke) as invoked:
            auth = client.inspect_auth(workspace)

        self.assertTrue(auth.authenticated)
        commands = [call.args[0] for call in invoked.call_args_list]
        self.assertIn(
            ["--session", "shared-social", "tab", "new", "about:blank"],
            commands,
        )
        self.assertIn(
            ["--session", "shared-social", "tab", "close", "0"],
            commands,
        )
        self.assertTrue(any("open" in command for command in commands))
        self.assertEqual(2, sum("eval" in command for command in commands))

    def test_replacement_auth_timeout_is_typed_as_target_unresponsive(self):
        client = facebook.CliAgentBrowserClient(timeout=30)
        workspace = facebook.BrowserWorkspace(
            profile_id="last30days-facebook",
            browser_id="browser-1",
            session_name="shared-social",
        )
        tabs = {"tabs": [
            {"index": 0, "active": True, "url": "https://www.facebook.com/"},
        ]}
        timeout = facebook.FacebookScraperFailure(
            "agent_browser_timeout", "target Runtime did not respond"
        )

        with mock.patch.object(client, "_invoke", return_value=tabs), mock.patch.object(
            client, "_probe_retained_facebook_auth", side_effect=timeout
        ), mock.patch.object(
            client, "replace_active_site_target", return_value=True
        ), mock.patch.object(client, "act"), mock.patch.object(
            client, "_evaluate_auth_probe", side_effect=timeout
        ):
            with self.assertRaises(facebook.FacebookScraperFailure) as raised:
                client.inspect_auth(workspace)

        self.assertEqual("facebook_target_unresponsive", raised.exception.error_type)

    def test_replacement_navigation_timeout_is_typed_as_target_unresponsive(self):
        client = facebook.CliAgentBrowserClient(timeout=30)
        workspace = facebook.BrowserWorkspace(
            profile_id="last30days-facebook",
            browser_id="browser-1",
            session_name="shared-social",
        )
        timeout = facebook.FacebookScraperFailure(
            "agent_browser_timeout", "replacement navigation did not respond"
        )

        with mock.patch.object(
            client, "replace_active_site_target", return_value=True
        ), mock.patch.object(client, "act"), mock.patch.object(
            client, "_evaluate_auth_probe", side_effect=timeout
        ):
            with self.assertRaises(facebook.FacebookScraperFailure) as raised:
                client._inspect_auth_on_fresh_target(
                    workspace,
                    replace_existing=True,
                )

        self.assertEqual("facebook_target_unresponsive", raised.exception.error_type)

    def test_successor_open_timeout_is_typed_as_target_unresponsive(self):
        client = facebook.CliAgentBrowserClient(timeout=30)
        workspace = facebook.BrowserWorkspace(
            profile_id="last30days-facebook",
            browser_id="browser-1",
            session_name="shared-social",
        )
        timeout = facebook.FacebookScraperFailure(
            "agent_browser_timeout", "successor open did not respond"
        )

        with mock.patch.object(
            client, "replace_active_site_target", side_effect=timeout
        ):
            with self.assertRaises(facebook.FacebookScraperFailure) as raised:
                client._inspect_auth_on_fresh_target(
                    workspace,
                    replace_existing=True,
                )

        self.assertEqual("facebook_target_unresponsive", raised.exception.error_type)

    def test_auth_inspection_caps_frozen_retained_targets_before_fresh_probe(self):
        client = facebook.CliAgentBrowserClient(timeout=30)
        workspace = facebook.BrowserWorkspace(
            profile_id="last30days-facebook",
            browser_id="browser-1",
            session_name="shared-social",
        )
        tabs = {
            "tabs": [
                {
                    "index": index,
                    "active": False,
                    "url": f"https://www.facebook.com/search/top/?q=OpenAI&n={index}",
                }
                for index in range(8)
            ]
        }

        def invoke(args, **_kwargs):
            if args[-2:] == ["tab", "list"]:
                return tabs
            if len(args) >= 2 and args[-2] == "tab" and args[-1].isdigit():
                raise facebook.FacebookScraperFailure(
                    "agent_browser_timeout", "retained target did not respond"
                )
            if "eval" in args:
                return {"authenticated_dom": True, "has_c_user": True}
            return {}

        with mock.patch.object(client, "_invoke", side_effect=invoke) as invoked:
            auth = client.inspect_auth(workspace)

        self.assertTrue(auth.authenticated)
        commands = [call.args[0] for call in invoked.call_args_list]
        retained_selections = [
            call
            for call in invoked.call_args_list
            if len(call.args[0]) >= 2
            and call.args[0][-2] == "tab"
            and call.args[0][-1].isdigit()
        ]
        self.assertEqual(2, len(retained_selections))
        self.assertTrue(
            all(call.kwargs["timeout"] == 15 for call in retained_selections)
        )
        self.assertIn(
            ["--session", "shared-social", "tab", "new", "about:blank"],
            commands,
        )
        self.assertIn(
            ["--session", "shared-social", "tab", "close", "7"],
            commands,
        )
        self.assertTrue(any("open" in command for command in commands))

    def test_fresh_auth_probe_gets_extended_bounded_deadlines(self):
        client = facebook.CliAgentBrowserClient(timeout=45, job_timeout_ms=120_000)
        workspace = facebook.BrowserWorkspace(
            profile_id="last30days-facebook",
            browser_id="browser-1",
            session_name="shared-social",
        )

        with mock.patch.object(client, "act") as act, mock.patch.object(
            client,
            "_invoke",
            return_value={"authenticated_dom": True, "has_c_user": True},
        ) as invoke:
            auth = client._inspect_auth_on_fresh_target(workspace)

        self.assertTrue(auth.authenticated)
        command = invoke.call_args.args[0]
        self.assertEqual("30000", command[command.index("--job-timeout-ms") + 1])
        self.assertEqual(45, invoke.call_args.kwargs["timeout"])
        self.assertGreaterEqual(
            invoke.call_args.kwargs["timeout"] * 1000
            - int(command[command.index("--job-timeout-ms") + 1]),
            10_000,
        )
        act.assert_called_once_with(
            workspace,
            facebook.BrowserAction("new_tab", value="https://www.facebook.com/"),
        )

    def test_retained_auth_probe_gets_queue_aware_outer_grace(self):
        client = facebook.CliAgentBrowserClient(timeout=45, job_timeout_ms=120_000)
        workspace = facebook.BrowserWorkspace(
            profile_id="last30days-facebook",
            browser_id="browser-1",
            session_name="shared-social",
        )

        with mock.patch.object(
            client,
            "_invoke",
            return_value={"authenticated_dom": True, "has_c_user": True},
        ) as invoke:
            result = client._evaluate_auth_probe(workspace)

        self.assertTrue(result["authenticated_dom"])
        command = invoke.call_args.args[0]
        self.assertEqual("3000", command[command.index("--job-timeout-ms") + 1])
        self.assertEqual(15, invoke.call_args.kwargs["timeout"])

    def test_wait_action_is_local_and_bounded(self):
        client = facebook.CliAgentBrowserClient(timeout=5)
        workspace = facebook.BrowserWorkspace(
            profile_id="last30days-facebook",
            browser_id="browser-1",
            session_name="last30days-facebook",
        )
        with mock.patch("lib.facebook.time.sleep") as sleep, mock.patch.object(
            client, "_invoke"
        ) as invoke:
            state = client.act(workspace, facebook.BrowserAction("wait", value="2000"))
        sleep.assert_called_once_with(2.0)
        invoke.assert_not_called()
        self.assertEqual(facebook.BrowserState(), state)

    def test_dependent_batch_combines_snapshot_and_evaluation(self):
        client = facebook.CliAgentBrowserClient(timeout=30)
        workspace = facebook.BrowserWorkspace(
            profile_id="last30days-facebook",
            browser_id="browser-1",
            session_name="shared-social",
        )
        batch_result = {
            "results": [
                {"success": True, "result": {"refs": {"e1": {}}, "snapshot": "visible text"}},
                {"success": True, "result": {"result": {"candidates": [{"id": "one"}]}}},
            ],
        }
        with mock.patch.object(client, "_invoke", return_value=batch_result) as invoke:
            snapshot, evaluated = client.snapshot_and_evaluate(
                workspace, facebook.EXTRACT_SCRIPT
            )

        self.assertEqual("visible text", snapshot.text)
        self.assertEqual([{"id": "one"}], evaluated["candidates"])
        self.assertIn("batch", invoke.call_args.args[0])
        commands = json.loads(invoke.call_args.kwargs["input_text"])
        self.assertEqual("snapshot", commands[0][0])
        self.assertEqual("eval", commands[1][0])

    def test_malformed_json_is_typed(self):
        completed = subprocess.CompletedProcess([], 0, stdout="not json", stderr="")
        with mock.patch("subprocess.run", return_value=completed):
            with self.assertRaises(facebook.FacebookScraperFailure) as raised:
                facebook.CliAgentBrowserClient(timeout=5)._invoke(["service", "status"], timeout=5)
        self.assertEqual("agent_browser_error", raised.exception.error_type)
        self.assertIn("malformed JSON", str(raised.exception))

    def test_cli_failure_redacts_cookie_values(self):
        completed = subprocess.CompletedProcess([], 1, stdout="", stderr="failed c_user=secret xs=secret2")
        with mock.patch("subprocess.run", return_value=completed):
            with self.assertRaises(facebook.FacebookScraperFailure) as raised:
                facebook.CliAgentBrowserClient(timeout=5)._invoke(["service", "status"], timeout=5)
        self.assertNotIn("secret", str(raised.exception))
        self.assertIn("[REDACTED]", str(raised.exception))

    def test_cli_failure_extracts_json_error_message(self):
        completed = subprocess.CompletedProcess(
            [], 1, stdout='{"success":false,"data":null,"error":"route_display_unavailable: :14 missing"}', stderr=""
        )
        with mock.patch("subprocess.run", return_value=completed):
            with self.assertRaises(facebook.FacebookScraperFailure) as raised:
                facebook.CliAgentBrowserClient(timeout=5)._invoke(["remote-view", "open"], timeout=5)
        self.assertEqual("route_display_unavailable: :14 missing", str(raised.exception))

    def test_timeout_is_typed(self):
        with mock.patch("subprocess.run", side_effect=subprocess.TimeoutExpired("agent-browser", 5)):
            with self.assertRaises(facebook.FacebookScraperFailure) as raised:
                facebook.CliAgentBrowserClient(timeout=5)._invoke(["service", "status"], timeout=5)
        self.assertEqual("agent_browser_timeout", raised.exception.error_type)

    def test_profile_mismatch_is_rejected_before_remote_open(self):
        client = facebook.CliAgentBrowserClient(timeout=5)
        with mock.patch.object(
            client, "_invoke", return_value=access_plan(profile_id="default")
        ) as invoke:
            with self.assertRaises(facebook.FacebookScraperFailure) as raised:
                client.acquire_workspace(request())
        self.assertEqual("profile_mismatch", raised.exception.error_type)
        invoke.assert_called_once()

    def test_stale_route_hint_cannot_override_current_service_state(self):
        client = facebook.CliAgentBrowserClient(timeout=5)
        status = {
            "service_state": {
                "sessions": {}, "browsers": {}, "tabs": {},
                "routePool": {
                    "route-current": {"state": "available", "routeId": "route:current", "readiness": {"state": "ready"}},
                    "route-stale": {"state": "available", "routeId": "route:stale", "readiness": {"state": "stale"}},
                },
            }
        }
        opened = {
            "profileId": "last30days-facebook", "browserId": "browser-1", "targetId": "target-1",
            "routeId": "route:current", "operatorVisible": {"state": "ready"},
        }
        with mock.patch.object(
            client, "_invoke", side_effect=[access_plan(), status, opened]
        ) as invoke, mock.patch.object(facebook.agent_browser_config, "record_access_plan"):
            workspace = client.acquire_workspace(request(route_pool_entry_id_hint="route-stale"))
        command = invoke.call_args_list[2].args[0]
        self.assertIn("route-current", command)
        self.assertNotIn("route-stale", command)
        self.assertEqual("route:current", workspace.route_id)

    def test_checked_out_ready_route_is_not_reused_as_a_launch_hint(self):
        state = {
            "routePool": {
                "route-busy": {
                    "state": "checked_out",
                    "routeId": "route:busy",
                    "readiness": {"state": "ready"},
                },
            },
        }
        self.assertEqual("", facebook._select_live_route_entry(state, request()))

    def test_ready_retained_browser_is_reused_without_remote_open(self):
        client = facebook.CliAgentBrowserClient(timeout=5)
        status = {
            "service_state": {
                "sessions": {
                    "default": {"profileId": "qbo-soylei", "browserIds": ["browser-qbo"]},
                    "last30days-facebook": {
                        "profileId": "last30days-facebook",
                        "browserIds": ["browser-1"],
                        "tabIds": ["target:t1"],
                    },
                },
                "browsers": {
                    "browser-qbo": {"profileId": "qbo-soylei", "health": "ready"},
                    "browser-1": {
                    "profileId": "last30days-facebook",
                    "health": "ready", "viewStreams": [{
                        "id": "route-1", "provider": "rdp_gateway", "externalUrl": "https://operator.example/token",
                        "readiness": {"state": "ready"},
                    }]
                }},
                "tabs": {"target:t1": {"targetId": "t1", "url": "https://www.facebook.com/"}},
            }
        }
        plan = access_plan(shared_owner=("browser-1", "last30days-facebook"))
        with mock.patch.object(
            client, "_invoke", side_effect=[plan, status, plan, status]
        ) as invoke, mock.patch.object(facebook.agent_browser_config, "record_access_plan"):
            first = client.acquire_workspace(request(session_name="default"))
            second = client.acquire_workspace(request(session_name="default"))
        self.assertEqual(first.browser_id, second.browser_id)
        self.assertEqual("last30days-facebook", first.session_name)
        self.assertEqual("t1", first.target_id)
        self.assertEqual("https://operator.example/token", first.operator_url)
        self.assertEqual(4, invoke.call_count)

    def test_access_plan_route_hints_fall_back_when_status_has_no_live_owner(self):
        client = facebook.CliAgentBrowserClient(timeout=5)
        plan = access_plan(shared_owner=("browser-1", "shared-social"))
        status = {"service_state": {"sessions": {}, "browsers": {}, "tabs": {}}}

        with mock.patch.object(
            client, "_invoke", side_effect=[plan, status]
        ) as invoke, mock.patch.object(
            facebook.agent_browser_config, "record_access_plan"
        ):
            workspace = client.acquire_workspace(request(session_name="default"))

        self.assertEqual("browser-1", workspace.browser_id)
        self.assertEqual("shared-social", workspace.session_name)
        self.assertEqual("not_required", workspace.operator_visible_state)
        self.assertEqual(2, invoke.call_count)

    def test_ready_retained_browser_without_rdp_stream_defers_operator_handoff(self):
        client = facebook.CliAgentBrowserClient(timeout=5)
        status = {
            "service_state": {
                "sessions": {
                    "last30days-facebook": {
                        "profileId": "",
                        "browserIds": ["session:last30days-facebook"],
                        "tabIds": ["target:t1"],
                    },
                },
                "browsers": {
                    "session:last30days-facebook": {
                        "profileId": "",
                        "health": "ready",
                        "viewStreams": [
                            {
                                "id": "cdp-screencast",
                                "provider": "cdp_screencast",
                                "url": "ws://127.0.0.1/example",
                            },
                        ],
                    },
                },
                "tabs": {
                    "target:t1": {
                        "targetId": "t1",
                        "url": "https://www.facebook.com/",
                    },
                },
            },
        }
        with mock.patch.object(
            client, "_invoke", side_effect=[access_plan(), status]
        ) as invoke, mock.patch.object(
            facebook.agent_browser_config, "record_access_plan"
        ):
            workspace = client.acquire_workspace(request())

        self.assertEqual("session:last30days-facebook", workspace.browser_id)
        self.assertEqual("last30days-facebook", workspace.session_name)
        self.assertEqual("t1", workspace.target_id)
        self.assertEqual("not_required", workspace.operator_visible_state)
        self.assertEqual("", workspace.operator_url)
        self.assertEqual(2, invoke.call_count)

    def test_exact_retained_session_with_default_profile_alias_is_reused(self):
        client = facebook.CliAgentBrowserClient(timeout=5)
        status = {
            "service_state": {
                "sessions": {
                    "last30days-facebook": {
                        "profileId": "default",
                        "browserIds": ["session:last30days-facebook"],
                        "tabIds": ["target:facebook"],
                    },
                },
                "browsers": {
                    "session:last30days-facebook": {
                        "profileId": "default",
                        "health": "ready",
                        "activeSessionIds": ["last30days-facebook"],
                        "viewStreams": [
                            {
                                "id": "cdp-screencast",
                                "provider": "cdp_screencast",
                                "readiness": {"state": "ready"},
                            },
                        ],
                    },
                },
                "tabs": {
                    "target:facebook": {
                        "targetId": "facebook",
                        "url": "https://www.facebook.com/search/posts?q=OpenAI",
                    },
                },
            },
        }

        with mock.patch.object(
            client, "_invoke", side_effect=[access_plan(), status]
        ) as invoke, mock.patch.object(
            facebook.agent_browser_config, "record_access_plan"
        ):
            workspace = client.acquire_workspace(request())

        self.assertEqual("session:last30days-facebook", workspace.browser_id)
        self.assertEqual("last30days-facebook", workspace.session_name)
        self.assertEqual("facebook", workspace.target_id)
        self.assertEqual("last30days-facebook", workspace.profile_id)
        self.assertEqual(2, invoke.call_count)

    def test_remote_view_failure_reconciles_a_late_ready_retained_browser(self):
        client = facebook.CliAgentBrowserClient(timeout=40, job_timeout_ms=40_000)
        client._run_deadline = 50.0
        initial_status = {
            "service_state": {
                "sessions": {},
                "browsers": {},
                "tabs": {},
                "routePool": {},
            },
        }
        late_status = {
            "service_state": {
                "sessions": {
                    "last30days-facebook": {
                        "profileId": "last30days-facebook",
                        "browserIds": ["session:last30days-facebook"],
                        "tabIds": ["target:facebook"],
                    },
                },
                "browsers": {
                    "session:last30days-facebook": {
                        "profileId": "last30days-facebook",
                        "health": "ready",
                        "activeSessionIds": ["last30days-facebook"],
                        "cdpEndpoint": (
                            "ws://127.0.0.1:37539/devtools/browser/example"
                        ),
                    },
                },
                "tabs": {
                    "target:facebook": {
                        "targetId": "facebook",
                        "url": "https://www.facebook.com/search/posts?q=OpenAI",
                    },
                },
            },
        }
        failed_open = facebook.FacebookScraperFailure(
            "agent_browser_error",
            "service_state_lock_timeout",
        )

        with mock.patch.object(
            facebook.time, "monotonic", return_value=10.0
        ), mock.patch.object(
            client,
            "_invoke",
            side_effect=[access_plan(), initial_status, failed_open, late_status],
        ) as invoke, mock.patch.object(
            facebook.agent_browser_config, "record_access_plan"
        ):
            workspace = client.acquire_workspace(request(timeout=40))

        self.assertEqual("session:last30days-facebook", workspace.browser_id)
        self.assertEqual("last30days-facebook", workspace.session_name)
        self.assertEqual("facebook", workspace.target_id)
        self.assertEqual("last30days-facebook", workspace.profile_id)
        self.assertEqual(30, invoke.call_args_list[2].kwargs["timeout"])
        self.assertEqual(["service", "status"], invoke.call_args_list[-1].args[0])
        self.assertEqual(10, invoke.call_args_list[-1].kwargs["timeout"])
        self.assertEqual(4, invoke.call_count)

    def test_remote_view_failure_does_not_accept_a_late_wrong_profile(self):
        client = facebook.CliAgentBrowserClient(timeout=40, job_timeout_ms=40_000)
        client._run_deadline = 50.0
        initial_status = {
            "service_state": {
                "sessions": {},
                "browsers": {},
                "tabs": {},
                "routePool": {},
            },
        }
        late_status = {
            "service_state": {
                "sessions": {
                    "last30days-facebook": {
                        "profileId": "default",
                        "browserIds": ["browser-default"],
                    },
                },
                "browsers": {
                    "browser-default": {
                        "profileId": "default",
                        "health": "ready",
                    },
                },
                "tabs": {},
            },
        }
        failed_open = facebook.FacebookScraperFailure(
            "agent_browser_error",
            "service_state_lock_timeout",
        )

        with mock.patch.object(
            facebook.time, "monotonic", return_value=10.0
        ), mock.patch.object(
            client,
            "_invoke",
            side_effect=[access_plan(), initial_status, failed_open, late_status],
        ), mock.patch.object(
            facebook.agent_browser_config, "record_access_plan"
        ), self.assertRaises(facebook.FacebookScraperFailure) as raised:
            client.acquire_workspace(request(timeout=40))

        self.assertIs(failed_open, raised.exception)

    def test_exact_default_profile_alias_reuses_ready_browser_cdp_endpoint_without_viewer(self):
        sessions = {
            "last30days-facebook": {
                "profileId": "default",
                "browserIds": ["session:last30days-facebook"],
                "tabIds": ["target:facebook"],
            },
        }
        browsers = {
            "session:last30days-facebook": {
                "profileId": "default",
                "health": "ready",
                "activeSessionIds": ["last30days-facebook"],
                "cdpEndpoint": "ws://127.0.0.1:37539/devtools/browser/example",
                "viewStreams": [
                    {
                        "provider": "cdp_screencast",
                        "readOnly": True,
                        "readiness": {
                            "state": "unavailable",
                            "reason": "missing_stream_server",
                        },
                    },
                ],
            },
        }
        tabs = {
            "target:facebook": {
                "targetId": "facebook",
                "url": "https://www.facebook.com/search/top/?q=OpenAI",
            },
        }

        owner = facebook._exact_retained_default_owner(
            session_name="last30days-facebook",
            selected_profile="last30days-facebook",
            target_service_id="facebook",
            sessions=sessions,
            browsers=browsers,
            tabs=tabs,
        )

        self.assertIsNotNone(owner)
        self.assertEqual("session:last30days-facebook", owner["browser_id"])
        self.assertEqual("last30days-facebook", owner["session_name"])
        self.assertEqual("facebook", owner["target_id"])

    def test_exact_default_profile_alias_forwards_to_retained_owner_session(self):
        client = facebook.CliAgentBrowserClient(timeout=5)
        status = {
            "service_state": {
                "sessions": {
                    "last30days-facebook": {
                        "profileId": "default",
                        "browserIds": ["session:plan0058"],
                        "tabIds": ["target:facebook"],
                    },
                    "plan0058": {
                        "profileId": "default",
                        "browserIds": ["session:plan0058"],
                        "tabIds": ["target:facebook"],
                    },
                },
                "browsers": {
                    "session:plan0058": {
                        "profileId": "default",
                        "health": "ready",
                        "activeSessionIds": ["plan0058"],
                        "viewStreams": [
                            {
                                "id": "cdp-screencast",
                                "provider": "cdp_screencast",
                                "readiness": {"state": "ready"},
                            },
                        ],
                    },
                },
                "tabs": {
                    "target:facebook": {
                        "targetId": "facebook",
                        "url": "https://www.facebook.com/search/posts?q=OpenAI",
                    },
                },
            },
        }

        with mock.patch.object(
            client, "_invoke", side_effect=[access_plan(), status]
        ) as invoke, mock.patch.object(
            facebook.agent_browser_config, "record_access_plan"
        ):
            workspace = client.acquire_workspace(request())

        self.assertEqual("session:plan0058", workspace.browser_id)
        self.assertEqual("plan0058", workspace.session_name)
        self.assertEqual("facebook", workspace.target_id)
        self.assertEqual("last30days-facebook", workspace.profile_id)
        self.assertEqual(2, invoke.call_count)

    def test_default_profile_alias_rejects_ambiguous_active_owners(self):
        sessions = {
            "last30days-facebook": {
                "profileId": "default",
                "browserIds": ["session:plan0058"],
                "tabIds": ["target:facebook"],
            },
            "plan0058": {
                "profileId": "default",
                "browserIds": ["session:plan0058"],
            },
            "other-owner": {
                "profileId": "default",
                "browserIds": ["session:plan0058"],
            },
        }
        browsers = {
            "session:plan0058": {
                "profileId": "default",
                "health": "ready",
                "activeSessionIds": ["plan0058", "other-owner"],
                "viewStreams": [
                    {
                        "provider": "cdp_screencast",
                        "readiness": {"state": "ready"},
                    },
                ],
            },
        }
        tabs = {
            "target:facebook": {
                "targetId": "facebook",
                "url": "https://www.facebook.com/",
            },
        }

        self.assertIsNone(
            facebook._exact_retained_default_owner(
                session_name="last30days-facebook",
                selected_profile="last30days-facebook",
                target_service_id="facebook",
                sessions=sessions,
                browsers=browsers,
                tabs=tabs,
            )
        )

    def test_wrong_profile_on_requested_session_uses_profile_scoped_lane(self):
        client = facebook.CliAgentBrowserClient(timeout=5, job_timeout_ms=120_000)
        status = {
            "service_state": {
                "sessions": {
                    "last30days-facebook": {
                        "profileId": "default",
                        "browserIds": ["browser-default"],
                    },
                },
                "browsers": {
                    "browser-default": {"profileId": "default", "health": "ready"},
                },
                "tabs": {},
                "routePool": {},
            },
        }
        opened = {
            "profileId": "last30days-facebook",
            "browserId": "browser-facebook",
            "sessionName": "last30days-facebook--last30days-facebook",
            "targetId": "target-facebook",
            "operatorVisible": {"state": "ready"},
        }
        with mock.patch.object(
            client, "_invoke", side_effect=[access_plan(), status, opened]
        ) as invoke, mock.patch.object(
            facebook.agent_browser_config, "record_access_plan"
        ), mock.patch("lib.facebook.time.sleep") as sleep:
            workspace = client.acquire_workspace(request())

        command = invoke.call_args_list[2].args[0]
        self.assertEqual(
            "last30days-facebook--last30days-facebook",
            command[command.index("--session") + 1],
        )
        self.assertEqual(
            "last30days-facebook--last30days-facebook",
            command[command.index("--session-name") + 1],
        )
        self.assertEqual("120000", command[command.index("--job-timeout-ms") + 1])
        self.assertEqual(125, invoke.call_args_list[2].kwargs["timeout"])
        self.assertEqual("last30days-facebook--last30days-facebook", workspace.session_name)

    def test_profile_scoped_lane_skips_retained_wrong_profile_placeholder(self):
        sessions = {
            "last30days-facebook--last30days-facebook": {"profileId": ""},
            "last30days-facebook--last30days-facebook--2": {"profileId": "default"},
        }
        self.assertEqual(
            "last30days-facebook--last30days-facebook--3",
            facebook._profile_scoped_session_name(
                sessions, "last30days-facebook", "last30days-facebook"
            ),
        )

    def test_access_plan_without_remote_view_uses_local_headed_profile_lane(self):
        client = facebook.CliAgentBrowserClient(timeout=5)
        status = {"service_state": {"sessions": {}, "browsers": {}, "tabs": {}}}
        opened = {"url": "https://www.facebook.com/", "title": "Facebook"}
        with mock.patch.object(
            client,
            "_invoke",
            side_effect=[access_plan(remote_view=False), status, opened],
        ) as invoke, mock.patch.object(
            facebook.agent_browser_config, "record_access_plan"
        ), mock.patch("lib.facebook.time.sleep") as sleep:
            workspace = client.acquire_workspace(request())

        command = invoke.call_args_list[2].args[0]
        self.assertIn("open", command)
        self.assertNotIn("remote-view", command)
        self.assertIn("--headed", command)
        self.assertEqual("not_required", workspace.operator_visible_state)

    def test_new_local_lane_recovers_empty_daemon_profile_startup_race(self):
        client = facebook.CliAgentBrowserClient(timeout=5)
        status = {"service_state": {"sessions": {}, "browsers": {}, "tabs": {}}}
        startup_error = facebook.FacebookScraperFailure(
            "agent_browser_error",
            "active session 'last30days-facebook' is using runtimeProfile=none profile=none",
        )
        opened = {"url": "https://www.facebook.com/", "title": "Facebook"}
        with mock.patch.object(
            client,
            "_invoke",
            side_effect=[
                access_plan(remote_view=False),
                status,
                startup_error,
                {},
                opened,
            ],
        ) as invoke, mock.patch.object(
            facebook.agent_browser_config, "record_access_plan"
        ), mock.patch("lib.facebook.time.sleep") as sleep:
            workspace = client.acquire_workspace(request())

        self.assertEqual(
            ["--session", "last30days-facebook", "close"],
            invoke.call_args_list[3].args[0],
        )
        self.assertEqual(invoke.call_args_list[2].args[0], invoke.call_args_list[4].args[0])
        sleep.assert_called_once_with(0.5)
        self.assertEqual("not_required", workspace.operator_visible_state)


class FacebookNavigationAndAuthTests(unittest.TestCase):
    def test_search_navigation_uses_post_specific_surface(self):
        parsed = urlsplit(facebook._search_url("OpenAI", recent=True))

        self.assertEqual("m.facebook.com", parsed.hostname)
        self.assertEqual("/search/posts/", parsed.path)
        self.assertTrue(facebook._recent_filter_active(parsed.geturl()))

    def test_prepared_query_capture_avoids_later_target_commands(self):
        class PreparedCaptureClient(FakeAgentBrowserClient):
            def __init__(self):
                super().__init__()
                self.prepared_url = ""
                self.capture_consumed = False

            def prepare_query_capture_url(self, url):
                self.prepared_url = url
                self.page["url"] = url

            def prepared_query_page(self, workspace):
                return dict(self.page)

            def consume_prepared_query_extraction(self, workspace):
                self.capture_consumed = True
                return {"candidates": list(self.candidates)}

            def act(self, workspace, action):
                if action.operation in {"navigate", "new_tab"}:
                    raise AssertionError("prepared capture must avoid later target commands")
                return super().act(workspace, action)

            def evaluate(self, workspace, script):
                raise AssertionError("prepared capture must avoid later Runtime evaluation")

        client = PreparedCaptureClient()

        result = make_scraper(client).search(
            "robotic lawn mower", "2026-06-15", "2026-07-15"
        )

        self.assertIsNone(result["error_type"])
        self.assertEqual(facebook._search_url("robotic lawn mower", recent=True), client.prepared_url)
        self.assertTrue(client.capture_consumed)

    def test_observed_retained_eval_timeout_recovers_within_adapter_budget(self):
        class ObservedNavigationRecoveryClient(FakeAgentBrowserClient):
            def __init__(self):
                super().__init__()
                self.remaining = 105
                self.navigation_evaluations = 0

            def _consume(self, seconds):
                if seconds > self.remaining:
                    raise facebook.FacebookScraperFailure(
                        "agent_browser_timeout",
                        f"observed operation exceeded remaining {self.remaining}s budget",
                    )
                self.remaining -= seconds

            def acquire_workspace(self, workspace_request):
                self._consume(3)
                return super().acquire_workspace(workspace_request)

            def inspect_auth(self, workspace):
                self._consume(18)
                return super().inspect_auth(workspace)

            def act(self, workspace, action):
                if action.operation == "navigate":
                    self._consume(15)
                elif action.operation == "wait":
                    self._consume(2)
                return super().act(workspace, action)

            def evaluate(self, workspace, script):
                if script == facebook.PAGE_STATE_SCRIPT:
                    self.navigation_evaluations += 1
                    if self.navigation_evaluations == 1:
                        self._consume(25)
                        raise facebook.FacebookScraperFailure(
                            "agent_browser_timeout",
                            "retained query target did not respond",
                        )
                    self._consume(8)
                elif script == facebook.EXTRACT_SCRIPT:
                    self._consume(8)
                return super().evaluate(workspace, script)

            def evaluate_navigation_state(self, workspace, script):
                self.navigation_evaluations += 1
                self._consume(10 if self.navigation_evaluations == 1 else 8)
                if self.navigation_evaluations == 1:
                    raise facebook.FacebookScraperFailure(
                        "agent_browser_timeout",
                        "retained query target did not respond",
                    )
                return dict(self.page)

            def inspect_active_page(self, workspace):
                self._consume(9)
                return dict(self.page)

            def replace_active_site_target(self, workspace, hostname):
                self._consume(9)
                return super().replace_active_site_target(workspace, hostname)

        client = ObservedNavigationRecoveryClient()

        result = make_scraper(client).search(
            "robotic lawn mower", "2026-06-15", "2026-07-15"
        )

        self.assertIsNone(result["error_type"])
        self.assertEqual(2, client.navigation_evaluations)
        self.assertGreaterEqual(client.remaining, 3)
        self.assertEqual(
            ["navigate", "new_tab", "navigate"],
            [action.operation for action in client.actions[:3]],
        )
        self.assertEqual("about:blank", client.actions[1].value)

    def test_default_depth_reserves_bounded_renderer_replacement_budget(self):
        self.assertEqual(105, facebook.DEPTH_CONFIG["default"]["timeout"])
        self.assertEqual(105, facebook.MAX_RUN_BUDGET_SECONDS)

    def test_auth_rate_limit_stops_without_handoff_or_navigation(self):
        client = FakeAgentBrowserClient(
            auth=facebook.FacebookAuthState(
                authenticated=False,
                rate_limited=True,
                rate_limit_reason="temporary_block",
            )
        )
        client.prepare_operator_handoff = mock.Mock()

        result = make_scraper(client).search(
            "robotic lawn mower", "2026-06-15", "2026-07-15"
        )

        self.assertEqual("rate_limit_detected", result["error_type"])
        self.assertEqual(
            "temporary_block", result["diagnostics"]["rate_limit_reason"]
        )
        self.assertEqual(
            ["facebook_rate_limit_temporary_block"],
            result["diagnostics"]["page_signals"],
        )
        self.assertEqual([], client.actions)
        client.prepare_operator_handoff.assert_not_called()

    def test_navigation_rate_limit_stops_without_recovery_or_handoff(self):
        page = dict(fixture("mixed_search.json")["page"])
        page.update(
            {
                "rate_limited": True,
                "rate_limit_reason": "action_frequency_limit",
            }
        )
        client = FakeAgentBrowserClient(page=page)
        client.prepare_operator_handoff = mock.Mock()

        result = make_scraper(client).search(
            "robotic lawn mower", "2026-06-15", "2026-07-15"
        )

        self.assertEqual("rate_limit_detected", result["error_type"])
        self.assertEqual(
            "action_frequency_limit",
            result["diagnostics"]["rate_limit_reason"],
        )
        self.assertEqual(
            ["navigate"], [action.operation for action in client.actions]
        )
        client.prepare_operator_handoff.assert_not_called()

    def test_empty_extraction_rate_limit_stops_without_scroll_or_retry(self):
        class RateLimitedExtractionClient(FakeAgentBrowserClient):
            def evaluate(self, workspace, script):
                if script == facebook.EXTRACT_SCRIPT:
                    return {
                        "url": self.page["url"],
                        "title": self.page["title"],
                        "candidates": [],
                        "rate_limited": True,
                        "rate_limit_reason": "temporary_block",
                    }
                return super().evaluate(workspace, script)

        client = RateLimitedExtractionClient()
        client.prepare_operator_handoff = mock.Mock()

        result = make_scraper(client).search(
            "robotic lawn mower", "2026-06-15", "2026-07-15"
        )

        self.assertEqual("rate_limit_detected", result["error_type"])
        self.assertEqual(
            "temporary_block", result["diagnostics"]["rate_limit_reason"]
        )
        self.assertEqual(
            ["navigate"], [action.operation for action in client.actions]
        )
        client.prepare_operator_handoff.assert_not_called()

    def test_checkpoint_prepares_missing_operator_handoff_on_demand(self):
        state = fixture("checkpoint.json")
        client = FakeAgentBrowserClient(auth=facebook.FacebookAuthState(**state["auth"]))
        client.workspace = facebook.BrowserWorkspace(
            profile_id="last30days-facebook",
            browser_id="browser-1",
            session_name="stored-last30days-social",
            target_id="target-1",
            operator_visible_state="not_required",
        )
        ready = facebook.BrowserWorkspace(
            profile_id="last30days-facebook",
            browser_id="browser-1",
            session_name="stored-last30days-social",
            target_id="target-1",
            route_id="route-1",
            operator_url="https://operator.example/guacamole/client-1",
            operator_visible_state="ready",
        )
        client.prepare_operator_handoff = mock.Mock(return_value=ready)

        result = make_scraper(client).search(
            "robotic lawn mower", "2026-06-15", "2026-07-15"
        )

        self.assertEqual("checkpoint_required", result["error_type"])
        self.assertEqual(ready.operator_url, result["operator_url"])
        client.prepare_operator_handoff.assert_called_once_with(
            client.workspace, request()
        )

    def test_checkpoint_still_notifies_when_operator_handoff_is_not_ready(self):
        state = fixture("checkpoint.json")
        client = FakeAgentBrowserClient(auth=facebook.FacebookAuthState(**state["auth"]))
        client.workspace = facebook.BrowserWorkspace(
            profile_id="last30days-facebook",
            browser_id="browser-1",
            session_name="stored-last30days-social",
            operator_visible_state="not_required",
        )
        client.prepare_operator_handoff = mock.Mock(
            side_effect=facebook.FacebookScraperFailure(
                "operator_ingress_unavailable",
                "agent-browser remote control is not ready for manual authentication",
            )
        )

        result = make_scraper(client).search(
            "robotic lawn mower", "2026-06-15", "2026-07-15"
        )

        self.assertEqual("checkpoint_required", result["error_type"])
        self.assertNotIn("operator_url", result)

    def test_logged_out_fixture_returns_auth_required_with_operator_url(self):
        state = fixture("logged_out.json")
        client = FakeAgentBrowserClient(auth=facebook.FacebookAuthState(**state["auth"]))
        result = make_scraper(client).search("robotic lawn mower", "2026-06-15", "2026-07-15")
        self.assertEqual("auth_required", result["error_type"])
        self.assertEqual("https://operator.example/opaque-token", result["operator_url"])
        self.assertEqual([], result["items"])

    def test_checkpoint_fixture_returns_typed_failure(self):
        state = fixture("checkpoint.json")
        client = FakeAgentBrowserClient(auth=facebook.FacebookAuthState(**state["auth"]))
        result = make_scraper(client).search("robotic lawn mower", "2026-06-15", "2026-07-15")
        self.assertEqual("checkpoint_required", result["error_type"])

    def test_unavailable_operator_ingress_has_typed_failure_and_no_stale_url(self):
        state = fixture("logged_out.json")
        client = FakeAgentBrowserClient(auth=facebook.FacebookAuthState(**state["auth"]))
        client.ingress_ready = False
        result = make_scraper(client).search("robotic lawn mower", "2026-06-15", "2026-07-15")
        self.assertEqual("operator_ingress_unavailable", result["error_type"])
        self.assertNotIn("operator_url", result)

    def test_home_page_after_same_target_navigation_is_rejected(self):
        state = fixture("authenticated_home.json")
        client = FakeAgentBrowserClient(page=state["page"], candidates=[])
        result = make_scraper(client).search("robotic lawn mower", "2026-06-15", "2026-07-15")
        self.assertEqual("navigation_mismatch", result["error_type"])
        self.assertEqual([], result["items"])
        self.assertIn("navigate", [action.operation for action in client.actions])

    def test_query_navigation_uses_verified_recent_url_on_fresh_auth_target(self):
        client = FakeAgentBrowserClient()
        result = make_scraper(client).search("robotic lawn mower", "2026-06-15", "2026-07-15")
        self.assertIsNone(result["error_type"])
        self.assertEqual(["navigate"], [action.operation for action in client.actions[:1]])
        self.assertIn("filters=", client.actions[0].value)

    def test_query_navigation_reuses_the_fresh_authenticated_facebook_target(self):
        client = FakeAgentBrowserClient()
        client.prepare_site_tab = mock.Mock(return_value=True)

        result = make_scraper(client).search(
            "robotic lawn mower", "2026-06-15", "2026-07-15"
        )

        self.assertIsNone(result["error_type"])
        self.assertEqual("navigate", client.actions[0].operation)
        self.assertNotIn("new_tab", [action.operation for action in client.actions])
        client.prepare_site_tab.assert_called_once_with(
            client.workspace,
            "facebook.com",
            consolidate=True,
            require_active=False,
            close_timeout=30,
            ignore_close_failures=True,
        )

    def test_query_navigation_timeout_recovers_once_on_a_fresh_query_target(self):
        class TimeoutOnceClient(FakeAgentBrowserClient):
            def __init__(self):
                super().__init__()
                self.navigation_attempts = 0

            def act(self, workspace, action):
                if action.operation == "navigate":
                    self.navigation_attempts += 1
                    if self.navigation_attempts == 1:
                        self.actions.append(action)
                        raise facebook.FacebookScraperFailure(
                            "agent_browser_error",
                            "Operation timed out. The page may still be loading or the element may not exist.",
                        )
                return super().act(workspace, action)

        client = TimeoutOnceClient()

        result = make_scraper(client).search(
            "robotic lawn mower", "2026-06-15", "2026-07-15"
        )

        self.assertIsNone(result["error_type"])
        self.assertEqual(
            ["navigate", "new_tab", "navigate"],
            [action.operation for action in client.actions[:3]],
        )
        self.assertEqual("about:blank", client.actions[1].value)
        self.assertEqual(client.actions[0].value, client.actions[2].value)

    def test_query_navigation_non_timeout_failure_does_not_open_a_recovery_target(self):
        class DisconnectedClient(FakeAgentBrowserClient):
            def act(self, workspace, action):
                if action.operation == "navigate":
                    self.actions.append(action)
                    raise facebook.FacebookScraperFailure(
                        "agent_browser_error", "browser connection closed"
                    )
                return super().act(workspace, action)

        client = DisconnectedClient()

        result = make_scraper(client).search(
            "robotic lawn mower", "2026-06-15", "2026-07-15"
        )

        self.assertEqual("agent_browser_error", result["error_type"])
        self.assertEqual(["navigate"], [action.operation for action in client.actions])

    def test_repeated_query_navigation_timeout_stops_after_one_fresh_target(self):
        class AlwaysTimeoutClient(FakeAgentBrowserClient):
            def act(self, workspace, action):
                if action.operation == "navigate":
                    self.actions.append(action)
                    raise facebook.FacebookScraperFailure(
                        "agent_browser_timeout", "agent-browser operation timed out after 30s"
                    )
                return super().act(workspace, action)

        client = AlwaysTimeoutClient()
        client.prepare_site_tab = mock.Mock(return_value=True)

        result = make_scraper(client).search(
            "robotic lawn mower", "2026-06-15", "2026-07-15"
        )

        self.assertEqual("facebook_target_unresponsive", result["error_type"])
        self.assertEqual("navigation", result["diagnostics"]["failure_stage"])
        self.assertEqual(
            ["navigate", "new_tab", "navigate"],
            [action.operation for action in client.actions],
        )
        self.assertEqual("about:blank", client.actions[1].value)
        self.assertEqual(client.actions[0].value, client.actions[2].value)
        client.prepare_site_tab.assert_called_once_with(
            client.workspace,
            "facebook.com",
            consolidate=True,
            require_active=False,
            close_timeout=30,
            ignore_close_failures=True,
        )

    def test_page_state_timeout_reads_once_on_a_fresh_query_target(self):
        class PageStateTimeoutOnceClient(FakeAgentBrowserClient):
            def __init__(self):
                super().__init__()
                self.page_state_evaluations = 0

            def evaluate(self, workspace, script):
                if script == facebook.PAGE_STATE_SCRIPT:
                    self.page_state_evaluations += 1
                    if self.page_state_evaluations == 1:
                        raise facebook.FacebookScraperFailure(
                            "agent_browser_timeout",
                            "agent-browser operation timed out after 20s",
                        )
                return super().evaluate(workspace, script)

        client = PageStateTimeoutOnceClient()

        result = make_scraper(client).search(
            "robotic lawn mower", "2026-06-15", "2026-07-15"
        )

        self.assertIsNone(result["error_type"])
        self.assertEqual(2, client.page_state_evaluations)
        self.assertEqual(
            ["navigate", "new_tab", "navigate"],
            [action.operation for action in client.actions[:3]],
        )
        self.assertEqual("about:blank", client.actions[1].value)
        self.assertEqual(client.actions[0].value, client.actions[2].value)

    def test_page_state_timeout_with_matching_tab_identity_uses_fresh_target(self):
        class PageStateTimeoutWithTabIdentityClient(FakeAgentBrowserClient):
            def __init__(self):
                super().__init__()
                self.page_state_evaluations = 0
                self.tab_identity_reads = 0

            def evaluate(self, workspace, script):
                if script == facebook.PAGE_STATE_SCRIPT:
                    self.page_state_evaluations += 1
                    if self.page_state_evaluations == 1:
                        raise facebook.FacebookScraperFailure(
                            "agent_browser_timeout",
                            "agent-browser operation timed out after 20s",
                        )
                return super().evaluate(workspace, script)

            def inspect_active_page(self, workspace):
                self.tab_identity_reads += 1
                return dict(self.page)

        client = PageStateTimeoutWithTabIdentityClient()

        result = make_scraper(client).search(
            "robotic lawn mower", "2026-06-15", "2026-07-15"
        )

        self.assertIsNone(result["error_type"])
        self.assertEqual(2, client.page_state_evaluations)
        self.assertEqual(0, client.tab_identity_reads)
        self.assertEqual(
            ["navigate", "new_tab", "navigate"],
            [action.operation for action in client.actions[:3]],
        )
        self.assertEqual("about:blank", client.actions[1].value)
        self.assertEqual(client.actions[0].value, client.actions[2].value)

    def test_repeated_page_state_timeout_stops_after_one_fresh_target(self):
        class PageStateAlwaysTimeoutClient(FakeAgentBrowserClient):
            def __init__(self):
                super().__init__()
                self.page_state_evaluations = 0

            def evaluate(self, workspace, script):
                if script == facebook.PAGE_STATE_SCRIPT:
                    self.page_state_evaluations += 1
                    raise facebook.FacebookScraperFailure(
                        "agent_browser_timeout",
                        "agent-browser operation timed out after 20s",
                    )
                return super().evaluate(workspace, script)

        client = PageStateAlwaysTimeoutClient()

        result = make_scraper(client).search(
            "robotic lawn mower", "2026-06-15", "2026-07-15"
        )

        self.assertEqual("facebook_target_unresponsive", result["error_type"])
        self.assertEqual("navigation", result["diagnostics"]["failure_stage"])
        self.assertEqual(2, client.page_state_evaluations)
        self.assertEqual(["facebook.com"], client.closed_site_targets)
        self.assertEqual(
            ["navigate", "new_tab", "navigate"],
            [action.operation for action in client.actions],
        )

    def test_page_state_non_timeout_failure_does_not_open_a_recovery_target(self):
        class PageStateDisconnectedClient(FakeAgentBrowserClient):
            def evaluate(self, workspace, script):
                if script == facebook.PAGE_STATE_SCRIPT:
                    raise facebook.FacebookScraperFailure(
                        "agent_browser_error", "browser connection closed"
                    )
                return super().evaluate(workspace, script)

        client = PageStateDisconnectedClient()

        result = make_scraper(client).search(
            "robotic lawn mower", "2026-06-15", "2026-07-15"
        )

        self.assertEqual("agent_browser_error", result["error_type"])
        self.assertEqual(
            ["navigate"],
            [action.operation for action in client.actions],
        )

    def test_dated_dom_extraction_does_not_require_accessibility_snapshot(self):
        client = FakeAgentBrowserClient()
        client.snapshot_and_evaluate = mock.Mock(
            side_effect=facebook.FacebookScraperFailure(
                "agent_browser_timeout", "interactive snapshot timed out"
            )
        )

        result = make_scraper(client).search(
            "robotic lawn mower", "2026-06-15", "2026-07-15"
        )

        self.assertIsNone(result["error_type"])
        self.assertEqual(1, len(result["items"]))
        client.snapshot_and_evaluate.assert_not_called()

    def test_undated_dom_candidates_survive_snapshot_timeout(self):
        candidates = [
            {
                "candidate_source": "action_card",
                "url": "https://www.facebook.com/example/posts/1",
                "text": "robotic lawn mower field note",
                "author": "Example",
                "timestamp": "",
                "engagement": {},
                "media": [],
            }
        ]
        client = FakeAgentBrowserClient(candidates=candidates)
        client.snapshot_and_evaluate = mock.Mock(
            side_effect=facebook.FacebookScraperFailure(
                "agent_browser_timeout", "interactive snapshot timed out"
            )
        )

        result = make_scraper(client).search(
            "robotic lawn mower", "2026-06-15", "2026-07-15"
        )

        self.assertNotEqual("agent_browser_timeout", result["error_type"])
        client.snapshot_and_evaluate.assert_called_once_with(
            client.workspace, facebook.EXTRACT_SCRIPT
        )

    def test_cleanup_timeout_does_not_mask_valid_query_result(self):
        client = FakeAgentBrowserClient()
        client.prepare_site_tab = mock.Mock(side_effect=facebook.FacebookScraperFailure(
            "agent_browser_timeout", "predecessor tab did not close"
        ))

        result = make_scraper(client).search(
            "robotic lawn mower", "2026-06-15", "2026-07-15"
        )

        self.assertIsNone(result["error_type"])
        self.assertEqual(1, len(result["items"]))
        self.assertEqual(1, client.prepare_site_tab.call_count)

    def test_cleanup_timeout_does_not_mask_original_query_failure(self):
        class DisconnectedClient(FakeAgentBrowserClient):
            def act(self, workspace, action):
                if action.operation == "navigate":
                    raise facebook.FacebookScraperFailure(
                        "agent_browser_error", "browser connection closed"
                    )
                return super().act(workspace, action)

        client = DisconnectedClient()
        client.prepare_site_tab = mock.Mock(side_effect=facebook.FacebookScraperFailure(
            "agent_browser_timeout", "duplicate target did not close"
        ))

        result = make_scraper(client).search(
            "robotic lawn mower", "2026-06-15", "2026-07-15"
        )

        self.assertEqual("agent_browser_error", result["error_type"])
        self.assertIn("browser connection closed", result["error"])
        self.assertEqual(1, client.prepare_site_tab.call_count)

    def test_recent_posts_filter_does_not_require_switch_click(self):
        client = FakeAgentBrowserClient(snapshots=[
            facebook.BrowserSnapshot(refs={"e1": {"role": "combobox", "name": "Search Facebook"}}),
            facebook.BrowserSnapshot(refs={"e2": {"role": "switch", "name": "Recent posts"}}),
        ])
        result = make_scraper(client).search(
            "robotic lawn mower", "2026-06-15", "2026-07-15"
        )
        self.assertIsNone(result["error_type"])
        self.assertNotIn("click", [action.operation for action in client.actions])
        self.assertIn("filters=", client.actions[0].value)

    def test_checked_recent_posts_switch_is_not_toggled_off(self):
        page = dict(fixture("mixed_search.json")["page"])
        page["url"] += "&filters=recent"
        client = FakeAgentBrowserClient(page=page, snapshots=[
            facebook.BrowserSnapshot(refs={"e1": {"role": "combobox", "name": "Search Facebook"}}),
            facebook.BrowserSnapshot(
                refs={"e2": {"role": "switch", "name": "Recent posts"}},
                text='- switch "Recent posts" [checked=true, ref=e2]',
            ),
        ])
        result = make_scraper(client).search(
            "robotic lawn mower", "2026-06-15", "2026-07-15"
        )
        self.assertIsNone(result["error_type"])
        self.assertNotIn("click", [action.operation for action in client.actions])

    def test_explicit_no_results_is_a_valid_empty_result(self):
        state = fixture("no_results.json")
        client = FakeAgentBrowserClient(page=state["page"], candidates=[])
        result = make_scraper(client).search("robotic lawn mower", "2026-06-15", "2026-07-15")
        self.assertIsNone(result["error_type"])
        self.assertEqual([], result["items"])


class FacebookCandidateQualityTests(unittest.TestCase):
    def test_mixed_fixture_emits_only_canonical_dated_post(self):
        client = FakeAgentBrowserClient()
        result = make_scraper(client).search("robotic lawn mower", "2026-06-15", "2026-07-15")
        self.assertIsNone(result["error_type"])
        self.assertEqual(1, len(result["items"]))
        item = result["items"][0]
        self.assertEqual("https://www.facebook.com/gardenlab/posts/123456789", item["url"])
        self.assertEqual("2026-07-10", item["date"])
        self.assertEqual("Garden Lab", item["author"])
        self.assertNotIn("Facebook Facebook", item["text"])
        self.assertEqual("agent-browser-dom-v2", item["metadata"]["extraction"])
        counts = result["diagnostics"]["candidate_counts"]
        self.assertEqual(1, counts["post"])
        self.assertGreaterEqual(counts["rejected"], 6)

    def test_relative_and_absolute_dates_resolve(self):
        state = fixture("relative_dates.json")
        client = FakeAgentBrowserClient(page=state["page"], candidates=state["candidates"])
        result = make_scraper(client).search("AI agents", "2026-06-15", "2026-07-15")
        self.assertIsNone(result["error_type"])
        self.assertEqual(["2026-07-12", "2026-07-14"], sorted(item["date"] for item in result["items"]))
        self.assertEqual(
            ("2026-07-15", "med"),
            facebook._parse_facebook_date("about an hour ago", NOW),
        )

    def test_current_rendered_shorthand_and_yesterday_clock_dates_resolve(self):
        self.assertEqual(
            ("2026-07-14", "med"),
            facebook._parse_facebook_date("20h", NOW),
        )
        self.assertEqual(
            ("2026-07-14", "med"),
            facebook._parse_facebook_date("Yesterday at 7:00 AM", NOW),
        )

    def test_live_shape_candidate_with_rendered_timestamp_passes_quality_gate(self):
        candidate = {
            "candidate_source": "action_card",
            "action_label": "Actions for this post by Example Research",
            "author": "Example Research",
            "author_url": "https://www.facebook.com/example-research",
            "media_urls": [
                "https://www.facebook.com/photo/?fbid=1001&set=pcb.2002"
            ],
            "timestamp": "20h",
            "text": (
                "Example Research shared a detailed OpenAI systems field note "
                "with enough substantive content for the post quality gate."
            ),
            "engagement": {"likes": 3, "comments": 1, "shares": 0},
        }
        page = dict(fixture("mixed_search.json")["page"])
        page.update(
            {
                "url": facebook._search_url("OpenAI"),
                "title": "OpenAI - Search Results | Facebook",
                "heading": "Search results for OpenAI",
                "query_value": "OpenAI",
            }
        )
        client = FakeAgentBrowserClient(page=page, candidates=[candidate])

        result = make_scraper(client).search("OpenAI", "2026-07-14", "2026-07-15")

        self.assertIsNone(result["error_type"])
        self.assertEqual(1, len(result["items"]))
        self.assertEqual("2026-07-14", result["items"][0]["date"])

    def test_accessibility_snapshot_pairs_obfuscated_timestamp_with_author(self):
        snapshot = '''
- heading "Minnesota Soil Health Coalition  Follow" [level=3, ref=e26]
  - link "Minnesota Soil Health Coalition" [ref=e31]
- link "a day ago" [ref=e27]
- button "Actions for this post by Minnesota Soil Health Coalition" [ref=e33]
- heading "Regenerative Farming News  Follow" [level=3, ref=e28]
  - link "Regenerative Farming News" [ref=e36]
- link "November 17, 2025" [ref=e29]
- button "Actions for this post by Regenerative Farming News" [ref=e38]
'''
        self.assertEqual(
            [
                ("Minnesota Soil Health Coalition", "a day ago"),
                ("Regenerative Farming News", "November 17, 2025"),
            ],
            facebook._accessible_post_timestamps(snapshot, NOW),
        )

    def test_recovers_page_post_permalink_from_photo_set(self):
        raw = {
            "author_url": "https://www.facebook.com/mnsoilhealth?tracking=removed",
            "media_urls": [
                "https://www.facebook.com/photo/?fbid=1346265997684600&set=pcb.1346266024351264"
            ],
        }
        self.assertEqual(
            "https://www.facebook.com/mnsoilhealth/posts/1346266024351264",
            facebook._recover_media_permalink(raw),
        )

    def test_recovers_numeric_profile_permalink_from_photo_id(self):
        raw = {
            "author_url": "https://www.facebook.com/profile.php?id=61578125507402",
            "media_urls": ["https://www.facebook.com/photo/?fbid=122154486764937516"],
        }
        self.assertEqual(
            "https://www.facebook.com/permalink.php?story_fbid=122154486764937516&id=61578125507402",
            facebook._recover_media_permalink(raw),
        )

    def test_cleans_single_character_timestamp_obfuscation(self):
        raw = """Minnesota Soil Health Coalition
·
1
u
4
7
t
u
0
4
a
1
:
e
0
3
l
t
s
7
h
·
Leading voices discuss regenerative agriculture and soil health.… See more
All reactions:
17
6 shares
Comment as Example User"""
        self.assertEqual(
            "Minnesota Soil Health Coalition\n"
            "Leading voices discuss regenerative agriculture and soil health.",
            facebook._clean_post_text(raw),
        )

    def test_scraper_merges_accessible_date_into_action_card(self):
        candidate = {
            "candidate_source": "action_card",
            "action_label": "Actions for this post by Minnesota Soil Health Coalition",
            "author": "Minnesota Soil Health Coalition",
            "author_url": "https://www.facebook.com/mnsoilhealth",
            "media_urls": [
                "https://www.facebook.com/photo/?fbid=1346265997684600&set=pcb.1346266024351264"
            ],
            "timestamp": "Minnesota Soil Health Coalition, view story",
            "text": "A robotic lawn mower demonstration covers regenerative agriculture and soil health.",
            "engagement": {"likes": 17, "comments": 0, "shares": 6},
        }
        client = FakeAgentBrowserClient(
            candidates=[candidate],
            snapshots=[
                facebook.BrowserSnapshot(
                    text='- link "a day ago" [ref=e27]\n'
                    '- button "Actions for this post by Minnesota Soil Health Coalition" [ref=e33]'
                ),
            ],
        )
        result = make_scraper(client).search(
            "robotic lawn mower", "2026-06-15", "2026-07-15"
        )
        self.assertIsNone(result["error_type"])
        self.assertEqual(1, len(result["items"]))
        self.assertEqual("2026-07-14", result["items"][0]["date"])
        self.assertEqual(
            "https://www.facebook.com/mnsoilhealth/posts/1346266024351264",
            result["items"][0]["url"],
        )

    def test_scraper_retries_until_action_card_timestamp_renders(self):
        candidate = {
            "candidate_source": "action_card",
            "author": "Garden Lab",
            "author_url": "https://www.facebook.com/gardenlab",
            "media_urls": ["https://www.facebook.com/photo/?fbid=1&set=pcb.123456789"],
            "timestamp": "Garden Lab, view story",
            "text": "Garden Lab tested a robotic lawn mower with useful navigation and safety notes.",
        }
        client = FakeAgentBrowserClient(
            candidates=[candidate],
            snapshots=[
                facebook.BrowserSnapshot(
                    text='- link "2 days ago" [ref=e7]\n'
                    '- button "Actions for this post by Garden Lab" [ref=e8]'
                ),
            ],
        )
        with mock.patch("lib.facebook.time.sleep") as sleep:
            result = make_scraper(client).search(
                "robotic lawn mower", "2026-06-15", "2026-07-15"
            )
        self.assertIsNone(result["error_type"])
        self.assertEqual("2026-07-13", result["items"][0]["date"])
        sleep.assert_called_once_with(1.0)

    def test_scraper_does_not_retry_when_another_post_has_a_timestamp(self):
        undated_action_card = {
            "candidate_source": "action_card",
            "author": "Garden Lab",
            "author_url": "https://www.facebook.com/gardenlab",
            "media_urls": ["https://www.facebook.com/photo/?fbid=1&set=pcb.123456789"],
            "timestamp": "Garden Lab, view story",
            "text": "Garden Lab tested a robotic lawn mower with useful navigation and safety notes.",
        }
        dated_post = fixture("mixed_search.json")["candidates"][0]
        client = FakeAgentBrowserClient(candidates=[undated_action_card, dated_post])

        with mock.patch("lib.facebook.time.sleep") as sleep:
            result = make_scraper(client).search(
                "robotic lawn mower", "2026-06-15", "2026-07-15"
            )

        self.assertIsNone(result["error_type"])
        self.assertEqual("2026-07-10", result["items"][0]["date"])
        self.assertEqual(["facebook_search_page"], result["diagnostics"]["page_signals"])
        self.assertEqual(1, result["diagnostics"]["command_count"])
        self.assertEqual("snapshot", result["diagnostics"]["browser_operations"][0]["operation"])
        sleep.assert_not_called()

    def test_all_rejected_returns_quality_summary(self):
        raw = fixture("mixed_search.json")["candidates"][1:]
        client = FakeAgentBrowserClient(candidates=raw)
        result = make_scraper(client).search("robotic lawn mower", "2026-06-15", "2026-07-15")
        self.assertEqual("quality_gate_failed", result["error_type"])
        self.assertEqual([], result["items"])
        self.assertTrue(result["diagnostics"]["rejection_counts"])

    def test_normalize_facebook_item_preserves_quality_metadata(self):
        raw = {
            "id": "FB1", "text": "A useful Facebook post about local robotics grants.",
            "url": "https://www.facebook.com/example/posts/1", "author": "Example Page",
            "date": "2026-01-15", "engagement": {"likes": 5, "comments": 1, "shares": 1},
            "metadata": {"extraction": "agent-browser-dom-v2", "date_confidence": "high"},
        }
        item = normalize.normalize_source_items("facebook", [raw], "2026-01-01", "2026-01-31")[0]
        self.assertEqual("facebook", item.source)
        self.assertEqual("Example Page", item.author)
        self.assertEqual("agent-browser-dom-v2", item.metadata["extraction"])

    def test_parse_response_logs_typed_error(self):
        with mock.patch("lib.facebook._log") as source_log:
            self.assertEqual([], facebook.parse_facebook_response({"error": "login needed", "error_type": "auth_required"}))
        source_log.assert_called_once_with("[auth_required] login needed")

    def test_debug_artifact_is_sanitized(self):
        client = FakeAgentBrowserClient()
        with tempfile.TemporaryDirectory() as directory:
            result = make_scraper(client, debug_dir=directory).search(
                "robotic lawn mower", "2026-06-15", "2026-07-15"
            )
            artifacts = list(Path(directory).glob("facebook-*.json"))
            self.assertEqual(1, len(artifacts))
            text = artifacts[0].read_text(encoding="utf-8")
        self.assertIsNone(result["error_type"])
        self.assertNotIn("opaque-token", text)
        self.assertNotIn("Garden Lab tested", text)
        self.assertNotIn("c_user", text)
        payload = json.loads(text)
        self.assertEqual("robotic lawn mower", payload["query"])
        self.assertEqual("snapshot", payload["command_timings"][0]["operation"])


@unittest.skipUnless(os.getenv("LAST30DAYS_FACEBOOK_LIVE_SMOKE") == "1", "opt-in live Facebook smoke")
class FacebookLiveSmokeTests(unittest.TestCase):
    def test_three_queries_reuse_profile_and_emit_only_quality_posts(self):
        config = {
            "LAST30DAYS_FACEBOOK_PROFILE": os.getenv("LAST30DAYS_FACEBOOK_PROFILE", "last30days-facebook"),
            "LAST30DAYS_FACEBOOK_SESSION": os.getenv("LAST30DAYS_FACEBOOK_SESSION", "last30days-facebook"),
            "LAST30DAYS_FACEBOOK_SCROLLS": "0",
            "LAST30DAYS_FACEBOOK_INITIAL_WAIT": "1",
        }
        browser_ids = set()
        for topic in (
            "regenerative agriculture farming soil health",
            "AI agents",
            "robotic lawn mower",
        ):
            result = facebook.search_facebook(topic, "2026-06-15", "2026-07-15", depth="quick", config=config)
            self.assertIsNone(result.get("error_type"), result)
            browser_ids.add(result["workspace"]["browser_id"])
            for item in result["items"]:
                self.assertIsNotNone(facebook._canonical_post_url(item["url"]))
                self.assertTrue(item["author"])
                self.assertTrue(item["date"])
        self.assertEqual(1, len(browser_ids))


if __name__ == "__main__":
    unittest.main()
