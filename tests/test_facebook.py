import json
import os
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

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
        if action.operation == "new_tab" and action.value:
            self.page["url"] = action.value
        return facebook.BrowserState()

    def evaluate(self, workspace, script):
        if script == facebook.PAGE_STATE_SCRIPT:
            return dict(self.page)
        if script == facebook.EXTRACT_SCRIPT:
            return {"url": self.page["url"], "title": self.page["title"], "candidates": self.candidates}
        raise AssertionError("unexpected script")

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
        status = {
            "service_state": {
                "sessions": {"last30days-facebook": {"profileId": "default", "browserIds": ["browser-1"]}},
                "browsers": {"browser-1": {"health": "ready"}},
                "tabs": {},
            }
        }
        with mock.patch.object(client, "_invoke", return_value=status) as invoke:
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
        with mock.patch.object(client, "_invoke", side_effect=[status, opened]) as invoke:
            workspace = client.acquire_workspace(request(route_pool_entry_id_hint="route-stale"))
        command = invoke.call_args_list[1].args[0]
        self.assertIn("route-current", command)
        self.assertNotIn("route-stale", command)
        self.assertEqual("route:current", workspace.route_id)

    def test_ready_retained_browser_is_reused_without_remote_open(self):
        client = facebook.CliAgentBrowserClient(timeout=5)
        status = {
            "service_state": {
                "sessions": {"last30days-facebook": {
                    "profileId": "last30days-facebook", "browserIds": ["browser-1"], "tabIds": ["target:t1"]
                }},
                "browsers": {"browser-1": {
                    "health": "ready", "viewStreams": [{
                        "id": "route-1", "provider": "rdp_gateway", "externalUrl": "https://operator.example/token",
                        "readiness": {"state": "ready"},
                    }]
                }},
                "tabs": {"target:t1": {"targetId": "t1", "url": "https://www.facebook.com/"}},
            }
        }
        with mock.patch.object(client, "_invoke", return_value=status) as invoke:
            first = client.acquire_workspace(request())
            second = client.acquire_workspace(request())
        self.assertEqual(first.browser_id, second.browser_id)
        self.assertEqual("t1", first.target_id)
        self.assertEqual(2, invoke.call_count)


class FacebookNavigationAndAuthTests(unittest.TestCase):
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

    def test_home_page_after_both_navigation_strategies_is_rejected(self):
        state = fixture("authenticated_home.json")
        client = FakeAgentBrowserClient(page=state["page"], candidates=[])
        result = make_scraper(client).search("robotic lawn mower", "2026-06-15", "2026-07-15")
        self.assertEqual("navigation_mismatch", result["error_type"])
        self.assertEqual([], result["items"])
        self.assertIn("new_tab", [action.operation for action in client.actions])

    def test_query_navigation_uses_accessible_search_control(self):
        client = FakeAgentBrowserClient()
        result = make_scraper(client).search("robotic lawn mower", "2026-06-15", "2026-07-15")
        self.assertIsNone(result["error_type"])
        self.assertEqual(["fill", "press", "wait"], [action.operation for action in client.actions[:3]])
        self.assertEqual("robotic lawn mower", client.actions[0].value)

    def test_recent_posts_switch_is_activated(self):
        client = FakeAgentBrowserClient(snapshots=[
            facebook.BrowserSnapshot(refs={"e1": {"role": "combobox", "name": "Search Facebook"}}),
            facebook.BrowserSnapshot(refs={"e2": {"role": "switch", "name": "Recent posts"}}),
        ])
        result = make_scraper(client).search(
            "robotic lawn mower", "2026-06-15", "2026-07-15"
        )
        self.assertIsNone(result["error_type"])
        clicks = [action for action in client.actions if action.operation == "click"]
        self.assertEqual(["@e2"], [action.target for action in clicks])

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
                facebook.BrowserSnapshot(refs={"e1": {"role": "combobox", "name": "Search Facebook"}}),
                facebook.BrowserSnapshot(),
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
                facebook.BrowserSnapshot(refs={"e1": {"role": "combobox", "name": "Search Facebook"}}),
                facebook.BrowserSnapshot(),
                facebook.BrowserSnapshot(),
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
