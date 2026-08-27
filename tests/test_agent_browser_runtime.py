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


def _request(*, url: str, agent: str, task: str, service: str):
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
    def _acquire(self, *, url, agent, task, service, inventories, service_actions=None):
        client = agent_browser_runtime.CliAgentBrowserClient(timeout=5)
        browser_id = "session:last30days-facebook--last30days-facebook"
        session_name = "handoff-social"
        target_id = f"{service}-owned"
        handle = {
            "handleId": f"tab-handle-{service}",
            "browserId": browser_id,
            "sessionName": session_name,
            "targetId": target_id,
        }
        plan = _access_plan(url=url, agent=agent, task=task, service=service)
        inventory_queue = list(inventories)
        service_actions = service_actions if service_actions is not None else []

        def service_request(arguments, **_kwargs):
            service_actions.append(arguments["action"])
            if arguments["action"] == "tab_new":
                return {"serviceTabHandle": handle, "url": url}
            if arguments["action"] == "tab_list":
                return {"tabs": inventory_queue.pop(0)}
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

    def test_delayed_target_inventory_settles_before_readiness(self):
        target = {
            "targetId": "x-owned",
            "sessionId": "handoff-social",
            "url": "https://x.com/home",
        }
        with mock.patch.object(agent_browser_runtime.time, "sleep") as sleep:
            workspace, actions = self._acquire(
                url="https://x.com/home",
                agent="x-scraper",
                task="x-feed",
                service="x",
                inventories=[[], [target]],
            )

        self.assertEqual("x-owned", workspace.target_id)
        self.assertEqual(["tab_new", "tab_list", "tab_list", "ui_action"], actions)
        sleep.assert_called_once_with(
            agent_browser_runtime.SERVICE_TARGET_INVENTORY_POLL_SECONDS
        )

    def test_inherited_session_trace_does_not_override_request_attribution(self):
        target = {
            "targetId": "linkedin-owned",
            "sessionId": "handoff-social",
            "url": "https://www.linkedin.com/feed/",
            "traceFilter": {"agentName": "x-scraper", "taskName": "x-feed"},
        }
        workspace, actions = self._acquire(
            url="https://www.linkedin.com/feed/",
            agent="linkedin-scraper",
            task="linkedin-home-feed",
            service="linkedin",
            inventories=[[target]],
        )

        self.assertEqual("linkedin-owned", workspace.target_id)
        self.assertEqual(["tab_new", "tab_list", "ui_action"], actions)

    def test_conflicting_session_or_hostname_fails_before_readiness(self):
        cases = (
            ({"sessionId": "wrong-session", "url": "https://x.com/home"}, "session"),
            ({"sessionId": "handoff-social", "url": "https://example.com/"}, "URL"),
        )
        for identity, expected_message in cases:
            with self.subTest(identity=identity):
                actions = []
                target = {"targetId": "x-owned", **identity}
                with self.assertRaises(
                    agent_browser_runtime.AgentBrowserRuntimeFailure
                ) as raised:
                    self._acquire(
                        url="https://x.com/home",
                        agent="x-scraper",
                        task="x-feed",
                        service="x",
                        inventories=[[target]],
                        service_actions=actions,
                    )
                self.assertIn(expected_message, str(raised.exception))
                self.assertEqual(["tab_new", "tab_list"], actions)

    def test_absent_target_stops_at_bounded_inventory_reads(self):
        actions = []
        with mock.patch.object(agent_browser_runtime.time, "sleep") as sleep:
            with self.assertRaises(
                agent_browser_runtime.AgentBrowserRuntimeFailure
            ) as raised:
                self._acquire(
                    url="https://x.com/home",
                    agent="x-scraper",
                    task="x-feed",
                    service="x",
                    inventories=[[]]
                    * agent_browser_runtime.SERVICE_TARGET_INVENTORY_MAX_READS,
                    service_actions=actions,
                )

        self.assertIn("did not settle", str(raised.exception))
        self.assertEqual(
            "service_tab_target_unsettled", raised.exception.reason_code
        )
        self.assertEqual(
            agent_browser_runtime.SERVICE_TARGET_INVENTORY_MAX_READS,
            actions.count("tab_list"),
        )
        self.assertEqual(1, actions.count("tab_new"))
        self.assertNotIn("ui_action", actions)
        self.assertEqual(
            agent_browser_runtime.SERVICE_TARGET_INVENTORY_MAX_READS - 1,
            sleep.call_count,
        )

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
