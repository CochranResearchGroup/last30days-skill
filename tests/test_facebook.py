import unittest
from unittest import mock

from lib import facebook, normalize, pipeline


class FacebookAvailabilityTests(unittest.TestCase):
    def test_facebook_is_not_available_by_default(self):
        self.assertNotIn("facebook", pipeline.available_sources({}, requested_sources=["facebook"]))

    def test_facebook_requires_enable_flag_and_agent_browser(self):
        config = {"LAST30DAYS_FACEBOOK_BROWSER": "1"}
        with mock.patch("shutil.which", return_value="/usr/bin/agent-browser"):
            sources = pipeline.available_sources(config, requested_sources=["facebook"])
        self.assertIn("facebook", sources)

    def test_facebook_must_be_requested(self):
        config = {"LAST30DAYS_FACEBOOK_BROWSER": "1"}
        with mock.patch("shutil.which", return_value="/usr/bin/agent-browser"):
            sources = pipeline.available_sources(config)
        self.assertNotIn("facebook", sources)


class FacebookParserTests(unittest.TestCase):
    def test_parse_items_builds_stable_items(self):
        raw = [
            {
                "text": "Open research labs are discussing eval harnesses on Facebook this month.",
                "url": "https://www.facebook.com/example/posts/1",
                "author": "Example Page",
                "engagement": {"likes": 12, "comments": 3, "shares": 2},
            },
            {
                "text": "Open research labs are discussing eval harnesses on Facebook this month.",
                "url": "https://www.facebook.com/example/posts/1",
                "author": "Example Page",
                "engagement": {"likes": 12, "comments": 3, "shares": 2},
            },
        ]
        items = facebook._parse_items(raw, "research eval harnesses", limit=10)
        self.assertEqual(1, len(items))
        self.assertTrue(items[0]["id"].startswith("FB"))
        self.assertEqual("Example Page", items[0]["author"])
        self.assertEqual(12, items[0]["engagement"]["likes"])
        self.assertEqual("agent-browser-dom", items[0]["metadata"]["extraction"])

    def test_parse_response_logs_error_and_returns_empty(self):
        with mock.patch("lib.facebook._log") as log:
            self.assertEqual([], facebook.parse_facebook_response({"error": "login wall"}))
        log.assert_called_once_with("login wall")

    def test_normalize_facebook_item(self):
        raw = {
            "id": "FB1",
            "text": "A useful Facebook post about local robotics grants.",
            "url": "https://www.facebook.com/example/posts/1",
            "author": "Example Page",
            "engagement": {"likes": 5, "comments": 1, "shares": 1},
            "metadata": {"extraction": "agent-browser-dom"},
        }
        item = normalize.normalize_source_items("facebook", [raw], "2026-01-01", "2026-01-31")[0]
        self.assertEqual("facebook", item.source)
        self.assertEqual("Example Page", item.author)
        self.assertEqual("agent-browser-dom", item.metadata["extraction"])


class FacebookCommandTests(unittest.TestCase):
    def test_search_returns_error_when_agent_browser_missing(self):
        with mock.patch("lib.facebook.shutil.which", return_value=None):
            result = facebook.search_facebook("topic", "2026-01-01", "2026-01-31")
        self.assertIn("agent-browser", result["error"])
        self.assertEqual([], result["items"])

    def test_search_uses_route_bound_remote_view_open(self):
        calls = []

        def fake_run(cmd, *, timeout, input_text=None):
            calls.append(cmd)
            if cmd[:4] == ["agent-browser", "--json", "--session", "last30days-facebook"] and cmd[4:6] == ["remote-view", "open"]:
                return {
                    "status": "opened",
                    "routeId": "route-a",
                    "displayAllocationId": "display-a",
                    "operatorVisible": {
                        "state": "ready",
                        "routeId": "route-a",
                        "displayAllocationId": "display-a",
                        "proof": {"displayContent": {"state": "browser_window_visible"}},
                    },
                }
            if cmd[-3:] == ["scroll", "down", "1400"]:
                return {}
            if cmd[-2:] == ["eval", "--stdin"]:
                return {"items": [{"text": "Facebook item about robotics grants", "url": "https://www.facebook.com/p/1"}]}
            return {}

        with mock.patch("lib.facebook.shutil.which", return_value="/usr/bin/agent-browser"), \
             mock.patch("lib.facebook._run", side_effect=fake_run), \
             mock.patch("lib.facebook.time.sleep"):
            result = facebook.search_facebook(
                "robotics grants",
                "2026-01-01",
                "2026-01-31",
                config={"LAST30DAYS_FACEBOOK_SCROLLS": "0"},
            )

        self.assertEqual(1, len(result["items"]))
        open_cmd = calls[0]
        self.assertEqual("remote-view", open_cmd[4])
        self.assertEqual("open", open_cmd[5])
        self.assertIn("--runtime-profile", open_cmd)
        self.assertIn("last30days-facebook", open_cmd)
        self.assertIn("--browser-build", open_cmd)
        self.assertIn("stealthcdp_chromium", open_cmd)
        self.assertIn("--provider", open_cmd)
        self.assertIn("rdp_gateway", open_cmd)
        self.assertNotIn("--browser-host", open_cmd)
        self.assertNotIn("open", open_cmd[:5])

    def test_search_can_reuse_retained_browser_route(self):
        calls = []

        def fake_run(cmd, *, timeout, input_text=None):
            calls.append(cmd)
            if cmd[:4] == ["agent-browser", "--json", "--session", "default"] and cmd[4:6] == ["remote-view", "open"]:
                return {
                    "status": "opened",
                    "routeId": "guacamole:4",
                    "displayAllocationId": "remote-view-display:14",
                    "operatorVisible": {
                        "state": "ready",
                        "routeId": "guacamole:4",
                        "displayAllocationId": "remote-view-display:14",
                        "proof": {"displayContent": {"state": "browser_window_visible"}},
                    },
                }
            if cmd[-2:] == ["eval", "--stdin"]:
                return {"items": [{"text": "Facebook item about retained browser reuse", "url": "https://www.facebook.com/p/2"}]}
            return {}

        with mock.patch("lib.facebook.shutil.which", return_value="/usr/bin/agent-browser"), \
             mock.patch("lib.facebook._run", side_effect=fake_run), \
             mock.patch("lib.facebook.time.sleep"):
            result = facebook.search_facebook(
                "retained browser reuse",
                "2026-01-01",
                "2026-01-31",
                config={
                    "LAST30DAYS_FACEBOOK_SESSION": "default",
                    "LAST30DAYS_FACEBOOK_BROWSER_ID": "session:default",
                    "LAST30DAYS_FACEBOOK_DISPLAY_ALLOCATION_ID": "remote-view-display:14",
                    "LAST30DAYS_FACEBOOK_ROUTE_ID": "guacamole:4",
                    "LAST30DAYS_FACEBOOK_SCROLLS": "0",
                },
            )

        self.assertEqual(1, len(result["items"]))
        open_cmd = calls[0]
        self.assertIn("--browser-id", open_cmd)
        self.assertIn("session:default", open_cmd)
        self.assertIn("--display-allocation-id", open_cmd)
        self.assertIn("remote-view-display:14", open_cmd)
        self.assertIn("--route-id", open_cmd)
        self.assertIn("guacamole:4", open_cmd)
        self.assertNotIn("--runtime-profile", open_cmd)

    def test_search_rejects_terminal_only_remote_view(self):
        def fake_run(cmd, *, timeout, input_text=None):
            return {
                "status": "opened",
                "routeId": "route-terminal",
                "displayAllocationId": "display-terminal",
                "operatorVisible": {
                    "state": "terminal_only",
                    "routeId": "route-terminal",
                    "displayAllocationId": "display-terminal",
                    "proof": {"displayContent": {"state": "terminal_only"}},
                },
            }

        with mock.patch("lib.facebook.shutil.which", return_value="/usr/bin/agent-browser"), \
             mock.patch("lib.facebook._run", side_effect=fake_run):
            result = facebook.search_facebook("topic", "2026-01-01", "2026-01-31")

        self.assertEqual([], result["items"])
        self.assertIn("not operator-visible", result["error"])
        self.assertIn("terminal_only", result["error"])


if __name__ == "__main__":
    unittest.main()
