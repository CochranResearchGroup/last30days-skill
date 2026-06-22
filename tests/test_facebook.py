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


if __name__ == "__main__":
    unittest.main()
