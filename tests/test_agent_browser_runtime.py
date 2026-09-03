import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

from lib import (
    agent_browser_runtime,
    facebook,
    linkedin,
    reddit_browser,
    service_acquisition_cleanup,
    x_browser,
    youtube_media,
    youtube_yt,
)


def _request(
    *,
    url: str,
    agent: str,
    task: str,
    service: str,
    allow_duplicate_profile_lane: bool = False,
    route_pool_entry_id_hint: str = "",
):
    return agent_browser_runtime.BrowserWorkspaceRequest(
        profile_id="last30days-facebook",
        session_name="last30days-facebook",
        browser_build="stealthcdp_chromium",
        view_provider="rdp_gateway",
        timeout=30,
        start_url=url,
        agent_name=agent,
        task_name=task,
        target_service_id=service,
        allow_duplicate_profile_lane=allow_duplicate_profile_lane,
        route_pool_entry_id_hint=route_pool_entry_id_hint,
    )


def _access_plan(*, url: str, agent: str, task: str, service: str):
    browser_id = "session:last30days-facebook--last30days-facebook"
    session_name = "handoff-social"
    return {
        "selectedProfile": {"id": "last30days-facebook"},
        "decision": {
            "serviceRequest": {
                "available": True,
                "blockedByAcquisition": False,
                "blockedByLifecycleOwner": False,
                "request": {
                    "action": "tab_new",
                    "serviceName": "last30days",
                    "agentName": agent,
                    "taskName": task,
                    "targetServiceIds": [service],
                    "runtimeProfile": "last30days-facebook",
                    "profileLeasePolicy": "wait",
                    "url": url,
                },
            },
            "profileReuse": {
                "recommendedAction": "wait_for_profile_lease",
                "compatibleLiveBrowserCount": 0,
                "activeLeaseSessionIds": [session_name],
                "sameProfileLiveBrowserIds": [browser_id],
                "sharedAcquisition": {"mode": None},
            },
        },
    }


class AgentBrowserRuntimeTests(unittest.TestCase):
    @staticmethod
    def _mcp_process(*responses):
        process = mock.Mock()
        process.poll.return_value = None
        process.stdin = mock.Mock()
        process.stdout = iter(
            json.dumps(response) + "\n" for response in responses
        )
        process.stderr = iter(())
        process.wait.return_value = 0
        return process

    def test_scrape_access_plan_does_not_force_operator_presentation_constraints(self):
        client = agent_browser_runtime.CliAgentBrowserClient(timeout=5)
        request = _request(
            url="https://www.linkedin.com/feed/",
            agent="linkedin-scraper",
            task="linkedin-home-feed",
            service="linkedin",
        )
        plan = _access_plan(
            url=request.start_url,
            agent=request.agent_name,
            task=request.task_name,
            service=request.target_service_id,
        )
        invocations = []

        def invoke(args, **_kwargs):
            invocations.append(args)
            return plan

        with (
            mock.patch.object(client, "_invoke", side_effect=invoke),
            mock.patch.object(
                client,
                "_invoke_service_request",
                side_effect=agent_browser_runtime.AgentBrowserRuntimeFailure(
                    "agent_browser_error", "stop after access plan"
                ),
            ),
            mock.patch.object(
                agent_browser_runtime.agent_browser_config, "record_access_plan"
            ),
            self.assertRaises(agent_browser_runtime.AgentBrowserRuntimeFailure),
        ):
            client.acquire_workspace(request)

        access_plan_args = invocations[0]
        self.assertNotIn("--browser-host", access_plan_args)
        self.assertNotIn("--view-stream-provider", access_plan_args)
        self.assertNotIn("--control-input-provider", access_plan_args)
        self.assertNotIn("--display-isolation", access_plan_args)

    def test_private_profile_capability_authenticates_plan_and_requests_ephemerally(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            capability_path = Path(temporary_directory) / "last30days.cap"
            capability = "synthetic-last30days-profile-capability-secret-v1"
            capability_path.write_text(capability + "\n", encoding="utf-8")
            os.chmod(capability_path, 0o600)
            client = agent_browser_runtime.CliAgentBrowserClient(
                timeout=5,
                profile_capability_file=capability_path,
            )
            request = _request(
                url="https://x.com/home",
                agent="x-scraper",
                task="x-feed",
                service="x",
            )
            plan = _access_plan(
                url=request.start_url,
                agent=request.agent_name,
                task=request.task_name,
                service=request.target_service_id,
            )
            handle = {
                "browserId": "session:terminal-profile-safe",
                "sessionName": "terminal-profile-safe",
                "targetId": "x-owned",
            }
            messages = []

            def response(data):
                return {
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps({"success": True, "data": data}),
                            }
                        ]
                    }
                }

            with (
                mock.patch.object(client, "_ensure_mcp_session"),
                mock.patch.object(
                    client,
                    "_write_mcp_message",
                    side_effect=lambda message: messages.append(message),
                ),
                mock.patch.object(
                    client,
                    "_wait_for_mcp_response",
                    side_effect=[
                        response(plan),
                        response(
                            {"serviceTabHandle": handle, "url": request.start_url}
                        ),
                        response({"ok": True}),
                    ],
                ),
                mock.patch.object(
                    agent_browser_runtime.agent_browser_config, "record_access_plan"
                ),
            ):
                workspace = client.acquire_workspace(request)

            self.assertEqual("x-owned", workspace.target_id)
            self.assertEqual(
                ["service_access_plan", "service_request", "service_request"],
                [message["params"]["name"] for message in messages],
            )
            self.assertTrue(
                all(
                    message["params"]["arguments"].get("profileCapability")
                    == capability
                    for message in messages
                )
            )
            self.assertNotIn("profileCapability", client._service_request_route)
            self.assertNotIn(capability, json.dumps(client.command_timings))

    def test_profile_capability_file_rejects_symlink_and_open_permissions(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            capability_path = directory / "capability"
            capability_path.write_text(
                "synthetic-last30days-profile-capability-secret-v1\n",
                encoding="utf-8",
            )
            os.chmod(capability_path, 0o644)
            client = agent_browser_runtime.CliAgentBrowserClient(
                timeout=5,
                profile_capability_file=capability_path,
            )
            with self.assertRaises(
                agent_browser_runtime.AgentBrowserRuntimeFailure
            ) as open_permissions:
                client._read_profile_capability()
            self.assertEqual(
                "profile_capability_unavailable", open_permissions.exception.reason_code
            )

            os.chmod(capability_path, 0o600)
            symlink_path = directory / "capability-link"
            symlink_path.symlink_to(capability_path)
            client = agent_browser_runtime.CliAgentBrowserClient(
                timeout=5,
                profile_capability_file=symlink_path,
            )
            with self.assertRaises(
                agent_browser_runtime.AgentBrowserRuntimeFailure
            ) as symlink:
                client._read_profile_capability()
            self.assertEqual(
                "profile_capability_unavailable", symlink.exception.reason_code
            )

    def test_profile_capability_is_redacted_from_defensive_error_text(self):
        self.assertEqual(
            "profileCapability=[REDACTED]",
            agent_browser_runtime._redact("profileCapability=super-secret-value"),
        )

    def _acquire(
        self,
        *,
        url,
        agent,
        task,
        service,
        service_actions=None,
        handle_overrides=None,
    ):
        client = agent_browser_runtime.CliAgentBrowserClient(timeout=5)
        browser_id = "session:last30days-facebook--last30days-facebook"
        session_name = "handoff-social"
        target_id = f"{service}-owned"
        handle = {
            "handleId": f"tab-handle-{service}",
            "browserId": browser_id,
            "sessionName": session_name,
            "targetId": target_id,
            **(handle_overrides or {}),
        }
        plan = _access_plan(url=url, agent=agent, task=task, service=service)
        service_actions = service_actions if service_actions is not None else []

        def service_request(arguments, **_kwargs):
            service_actions.append(arguments["action"])
            if arguments["action"] == "tab_new":
                return {"serviceTabHandle": handle, "url": url}
            if arguments["action"] == "ui_action":
                self.assertEqual(handle, arguments["serviceTabHandle"])
                return {"ok": True}
            raise AssertionError(f"unexpected service action: {arguments}")

        def invoke(args, **_kwargs):
            if args[:2] == ["service", "access-plan"]:
                return plan
            arguments = client._service_request_arguments(args, None)
            self.assertIsNotNone(arguments)
            return service_request(arguments)

        with mock.patch.object(
            client, "_invoke", side_effect=invoke
        ), mock.patch.object(
            client, "_invoke_service_request", side_effect=service_request
        ), mock.patch.object(
            agent_browser_runtime.agent_browser_config, "record_access_plan"
        ):
            workspace = client.acquire_workspace(
                _request(url=url, agent=agent, task=task, service=service)
            )
        return workspace, service_actions

    def test_broker_handle_is_authoritative_without_raw_target_rediscovery(self):
        workspace, actions = self._acquire(
            url="https://x.com/home",
            agent="x-scraper",
            task="x-feed",
            service="x",
        )

        self.assertEqual("x-owned", workspace.target_id)
        self.assertEqual(["tab_new", "ui_action"], actions)

    def test_broker_request_preserves_route_pool_entry_hint(self):
        client = agent_browser_runtime.CliAgentBrowserClient(timeout=5)
        request = _request(
            url="https://www.reddit.com/",
            agent="reddit-scraper",
            task="reddit-home-feed",
            service="reddit",
            route_pool_entry_id_hint="guacamole-rdp-b",
        )
        plan = _access_plan(
            url=request.start_url,
            agent=request.agent_name,
            task=request.task_name,
            service=request.target_service_id,
        )
        plan["decision"]["serviceRequest"]["request"]["params"] = {
            "provider": "rdp_gateway"
        }
        captured = {}

        def service_request(arguments, **_kwargs):
            captured.update(arguments)
            raise agent_browser_runtime.AgentBrowserRuntimeFailure(
                "agent_browser_error", "stop after request capture"
            )

        with (
            mock.patch.object(client, "_resolve_access_plan", return_value=plan),
            mock.patch.object(
                client, "_invoke_service_request", side_effect=service_request
            ),
            mock.patch.object(
                agent_browser_runtime.agent_browser_config, "record_access_plan"
            ),
            self.assertRaises(agent_browser_runtime.AgentBrowserRuntimeFailure),
        ):
            client.acquire_workspace(request)

        self.assertNotIn("routePoolEntryId", captured)
        self.assertEqual(
            "guacamole-rdp-b",
            captured["params"]["routePoolEntryId"],
        )
        self.assertEqual("rdp_gateway", captured["params"]["provider"])

    def test_reviewed_duplicate_profile_lane_override_reaches_broker(self):
        client = agent_browser_runtime.CliAgentBrowserClient(timeout=5)
        request = _request(
            url="https://x.com/home",
            agent="x-scraper",
            task="x-feed",
            service="x",
            allow_duplicate_profile_lane=True,
        )
        plan = _access_plan(
            url=request.start_url,
            agent=request.agent_name,
            task=request.task_name,
            service=request.target_service_id,
        )
        plan["decision"]["serviceRequest"]["request"]["sessionName"] = (
            "terminal-profile-fresh"
        )
        captured = []
        handle = {
            "browserId": "session:last30days-force",
            "sessionName": "last30days-force",
            "targetId": "x-owned",
        }

        def service_request(arguments, **_kwargs):
            captured.append(arguments)
            if arguments["action"] == "tab_new":
                return {"serviceTabHandle": handle, "url": request.start_url}
            return {"ok": True}

        def invoke(args, **_kwargs):
            if args[:2] == ["service", "access-plan"]:
                return plan
            arguments = client._service_request_arguments(args, None)
            self.assertIsNotNone(arguments)
            return service_request(arguments)

        with (
            mock.patch.object(client, "_invoke", side_effect=invoke),
            mock.patch.object(
                client, "_invoke_service_request", side_effect=service_request
            ),
            mock.patch.object(
                agent_browser_runtime.agent_browser_config, "record_access_plan"
            ),
        ):
            client.acquire_workspace(request)

        self.assertIs(True, captured[0]["allowDuplicateProfileLane"])
        self.assertEqual("terminal-profile-fresh", captured[0]["sessionName"])
        self.assertNotIn("browserId", captured[0])

    def test_reviewed_override_still_reuses_one_compatible_live_browser(self):
        client = agent_browser_runtime.CliAgentBrowserClient(timeout=5)
        request = _request(
            url="https://x.com/home",
            agent="x-scraper",
            task="x-feed",
            service="x",
            allow_duplicate_profile_lane=True,
        )
        plan = _access_plan(
            url=request.start_url,
            agent=request.agent_name,
            task=request.task_name,
            service=request.target_service_id,
        )
        plan["decision"]["profileReuse"]["compatibleLiveBrowserCount"] = 1
        captured = []
        handle = {
            "browserId": "session:last30days-facebook--last30days-facebook",
            "sessionName": "handoff-social",
            "targetId": "x-owned",
        }

        def service_request(arguments, **_kwargs):
            captured.append(arguments)
            if arguments["action"] == "tab_new":
                return {"serviceTabHandle": handle, "url": request.start_url}
            return {"ok": True}

        def invoke(args, **_kwargs):
            if args[:2] == ["service", "access-plan"]:
                return plan
            arguments = client._service_request_arguments(args, None)
            self.assertIsNotNone(arguments)
            return service_request(arguments)

        with (
            mock.patch.object(client, "_invoke", side_effect=invoke),
            mock.patch.object(
                client, "_invoke_service_request", side_effect=service_request
            ),
            mock.patch.object(
                agent_browser_runtime.agent_browser_config, "record_access_plan"
            ),
        ):
            client.acquire_workspace(request)

        self.assertEqual(
            "session:last30days-facebook--last30days-facebook",
            captured[0]["browserId"],
        )
        self.assertEqual("handoff-social", captured[0]["sessionName"])

    def test_direct_broker_timeout_is_typed_at_workspace_acquisition(self):
        client = agent_browser_runtime.CliAgentBrowserClient(timeout=5)
        request = _request(
            url="https://x.com/home",
            agent="x-scraper",
            task="x-feed",
            service="x",
        )
        plan = _access_plan(
            url=request.start_url,
            agent=request.agent_name,
            task=request.task_name,
            service=request.target_service_id,
        )

        with (
            mock.patch.object(client, "_invoke", return_value=plan),
            mock.patch.object(
                client,
                "_invoke_service_request",
                side_effect=subprocess.TimeoutExpired("agent-browser mcp serve", 5),
            ),
            mock.patch.object(
                agent_browser_runtime.agent_browser_config, "record_access_plan"
            ),
            self.assertRaises(
                agent_browser_runtime.AgentBrowserRuntimeFailure
            ) as raised,
        ):
            client.acquire_workspace(request)

        self.assertEqual("agent_browser_timeout", raised.exception.error_type)
        self.assertEqual(
            "broker_service_request_timeout", raised.exception.reason_code
        )
        self.assertEqual(
            [
                {
                    "operation": "service_request:tab_new",
                    "duration_ms": mock.ANY,
                    "status": "timed_out",
                }
            ],
            client.command_timings,
        )

    def test_broker_error_preserves_structured_lifecycle_reason(self):
        client = agent_browser_runtime.CliAgentBrowserClient(timeout=5)
        error = (
            "runtime_owner_generation_stale: daemon is no longer the "
            "effect-capable browser owner"
        )
        process = self._mcp_process(
            {"jsonrpc": "2.0", "id": 1, "result": {}},
            {
                "jsonrpc": "2.0",
                "id": 2,
                "result": {
                    "isError": True,
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(
                                {"success": False, "error": error}
                            ),
                        }
                    ],
                },
            },
        )

        with (
            mock.patch.object(
                agent_browser_runtime.subprocess,
                "Popen",
                return_value=process,
            ),
            self.assertRaises(
                agent_browser_runtime.AgentBrowserRuntimeFailure
            ) as raised,
        ):
            client._invoke_service_request(
                {"action": "tab_new", "serviceName": "last30days"}, timeout=5
            )

        self.assertEqual("agent_browser_error", raised.exception.error_type)
        self.assertEqual(
            "runtime_owner_generation_stale", raised.exception.reason_code
        )
        self.assertEqual(error, str(raised.exception))

    def test_broker_requests_share_one_live_mcp_process(self):
        client = agent_browser_runtime.CliAgentBrowserClient(timeout=5)
        process = self._mcp_process(
            {"jsonrpc": "2.0", "id": 1, "result": {}},
            {
                "jsonrpc": "2.0",
                "id": 2,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(
                                {"success": True, "data": {"step": 1}}
                            ),
                        }
                    ]
                },
            },
            {
                "jsonrpc": "2.0",
                "id": 3,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(
                                {"success": True, "data": {"step": 2}}
                            ),
                        }
                    ]
                },
            },
        )

        with mock.patch.object(
            agent_browser_runtime.subprocess, "Popen", return_value=process
        ) as popen:
            first = client._invoke_service_request(
                {"action": "tab_new", "serviceName": "last30days"},
                timeout=5,
            )
            second = client._invoke_service_request(
                {"action": "evaluate", "serviceName": "last30days"},
                timeout=5,
            )

        self.assertEqual({"step": 1}, first)
        self.assertEqual({"step": 2}, second)
        popen.assert_called_once()
        self.assertEqual(4, process.stdin.write.call_count)
        process.terminate.assert_not_called()

    def test_x_workspace_acquisition_preserves_broker_timeout_reason(self):
        client = x_browser.CliAgentBrowserClient(timeout=5)
        request = _request(
            url="https://x.com/home",
            agent="x-scraper",
            task="x-feed",
            service="x",
        )
        plan = _access_plan(
            url=request.start_url,
            agent=request.agent_name,
            task=request.task_name,
            service=request.target_service_id,
        )

        with (
            mock.patch.object(client, "_invoke", return_value=plan),
            mock.patch.object(
                client,
                "_invoke_service_request",
                side_effect=subprocess.TimeoutExpired("agent-browser mcp serve", 5),
            ),
            mock.patch.object(
                agent_browser_runtime.agent_browser_config, "record_access_plan"
            ),
            self.assertRaises(x_browser.XBrowserFailure) as raised,
        ):
            client.acquire_workspace(request)

        self.assertEqual("agent_browser_timeout", raised.exception.error_type)
        self.assertEqual(
            "broker_service_request_timeout", raised.exception.reason_code
        )

    def test_linkedin_broker_handle_reaches_handle_scoped_readiness(self):
        workspace, actions = self._acquire(
            url="https://www.linkedin.com/feed/",
            agent="linkedin-scraper",
            task="linkedin-home-feed",
            service="linkedin",
        )

        self.assertEqual("linkedin-owned", workspace.target_id)
        self.assertEqual(["tab_new", "ui_action"], actions)

    def test_invalid_broker_handle_fails_before_readiness(self):
        actions = []
        with self.assertRaises(
            agent_browser_runtime.AgentBrowserRuntimeFailure
        ) as raised:
            self._acquire(
                url="https://x.com/home",
                agent="x-scraper",
                task="x-feed",
                service="x",
                service_actions=actions,
                handle_overrides={"valid": False},
            )

        self.assertEqual(
            "broker_service_tab_handle_invalid", raised.exception.reason_code
        )
        self.assertEqual(["tab_new"], actions)

    def test_non_facebook_providers_depend_on_provider_neutral_runtime(self):
        for module in (x_browser, linkedin, reddit_browser, youtube_yt, youtube_media):
            self.assertIs(agent_browser_runtime, module.browser_runtime)
        self.assertIs(
            agent_browser_runtime.CliAgentBrowserClient,
            service_acquisition_cleanup.CliAgentBrowserClient,
        )
        self.assertTrue(
            issubclass(facebook.CliAgentBrowserClient, agent_browser_runtime.CliAgentBrowserClient)
        )
