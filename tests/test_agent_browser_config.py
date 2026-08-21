import json
import stat
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from lib import agent_browser_config


def access_plan():
    return {
        "selectedProfile": {
            "id": "last30days-facebook",
            "profileClass": "durable_named",
            "profileOrigin": "agent_browser_owned",
            "userDataDir": "/private/profile/path",
        },
        "decision": {
            "launchPosture": {
                "browserBuild": "stealthcdp_chromium",
                "browserHost": "local_headed",
                "viewStreamProvider": "cdp_screencast",
                "controlInputProvider": "cdp_input",
            },
            "profileReuse": {
                "recommendedAction": "reuse_existing_browser",
                "profileProcessPolicy": "exclusive_process",
                "clientSharingPolicy": "shared_browser_tabs",
                "defaultAcquisition": "tab_new",
                "reusableBrowserId": "session:last30days-facebook",
                "reusableSessionName": "last30days-facebook",
                "sharedAcquisition": {
                    "mode": "tab_new",
                    "browserId": "session:last30days-facebook",
                    "sessionName": "last30days-facebook",
                },
            },
            "serviceRequest": {
                "request": {
                    "browserId": "session:last30days-facebook",
                    "sessionName": "last30days-facebook",
                    "profile": "/private/profile/path",
                    "url": "https://x.com/search",
                },
            },
        },
    }


class AgentBrowserConfigTests(unittest.TestCase):
    def test_loads_stable_user_scoped_target_configuration(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "agent-browser.json"
            path.write_text(
                json.dumps(
                    {
                        "schema_version": agent_browser_config.SCHEMA_VERSION,
                        "targets": {
                            "x": {
                                "profile_id": "last30days-facebook",
                                "browser_build": "stealthcdp_chromium",
                                "browser_host": "remote_headed",
                                "view_stream_provider": "rdp_gateway",
                                "display_isolation": "private_virtual_display",
                                "runtime_browser_id": "must-not-load",
                            }
                        },
                    }
                ),
                encoding="utf-8",
            )

            target = agent_browser_config.load_target_config("x", path=path)

        self.assertEqual("last30days-facebook", target["profile_id"])
        self.assertEqual("rdp_gateway", target["view_stream_provider"])
        self.assertNotIn("runtime_browser_id", target)

    def test_records_only_stable_user_scoped_target_configuration(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "agent-browser.json"
            agent_browser_config.record_access_plan(
                access_plan(),
                "x",
                path=path,
                recorded_at=datetime(2026, 7, 23, 12, 0, tzinfo=timezone.utc),
            )
            payload = json.loads(path.read_text(encoding="utf-8"))

        target = payload["targets"]["x"]
        self.assertEqual("last30days-facebook", target["profile_id"])
        self.assertEqual("shared_browser_tabs", target["client_sharing_policy"])
        self.assertEqual("tab_new", target["default_acquisition"])
        serialized = json.dumps(payload)
        for forbidden in (
            "browserId",
            "sessionName",
            "routeId",
            "displayAllocationId",
            "userDataDir",
            "/private/profile/path",
            "https://x.com/search",
        ):
            self.assertNotIn(forbidden, serialized)

    def test_user_scoped_file_is_mode_0600_and_preserves_other_targets(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "agent-browser.json"
            path.write_text(
                json.dumps({"schema_version": "old", "targets": {"facebook": {"profile_id": "fb"}}}),
                encoding="utf-8",
            )
            agent_browser_config.record_access_plan(access_plan(), "x", path=path)
            payload = json.loads(path.read_text(encoding="utf-8"))
            mode = stat.S_IMODE(path.stat().st_mode)

        self.assertEqual(0o600, mode)
        self.assertEqual("fb", payload["targets"]["facebook"]["profile_id"])
        self.assertEqual("last30days-facebook", payload["targets"]["x"]["profile_id"])

    def test_shared_owner_uses_broker_hints_not_caller_session(self):
        owner = agent_browser_config.shared_profile_owner(
            access_plan(),
            {
                "sessions": {
                    "default": {"profileId": "qbo-soylei", "browserIds": ["session:default"]},
                    "last30days-facebook": {
                        "profileId": "last30days-facebook",
                        "browserIds": ["session:last30days-facebook"],
                        "tabIds": ["target:x"],
                    },
                },
                "browsers": {
                    "session:default": {"profileId": "qbo-soylei", "health": "ready"},
                    "session:last30days-facebook": {
                        "profileId": "last30days-facebook",
                        "health": "ready",
                    },
                },
                "tabs": {"target:x": {"targetId": "x"}},
            },
            expected_profile_id="last30days-facebook",
        )

        self.assertEqual("session:last30days-facebook", owner["browser_id"])
        self.assertEqual("last30days-facebook", owner["session_name"])
        self.assertEqual("x", owner["target_id"])

    def test_incompatible_human_route_reuses_only_writable_cdp_owner(self):
        plan = {
            "decision": {
                "profileReuse": {
                    "recommendedAction": "wait_for_profile_lease",
                    "activeLeaseSessionIds": ["stored-social"],
                    "sameProfileLiveBrowserIds": ["browser:social"],
                }
            }
        }
        state = {
            "sessions": {
                "stored-social": {
                    "browserIds": ["browser:social"],
                    "tabIds": ["target:x"],
                }
            },
            "browsers": {
                "browser:social": {
                    "profileId": "last30days-facebook",
                    "health": "ready",
                    "viewStreams": [
                        {
                            "provider": "cdp_screencast",
                            "controlInput": "cdp_input",
                            "readOnly": False,
                        }
                    ],
                }
            },
            "tabs": {"target:x": {"targetId": "x"}},
        }

        owner = agent_browser_config.shared_profile_owner(
            plan,
            state,
            expected_profile_id="last30days-facebook",
        )
        self.assertEqual("browser:social", owner["browser_id"])

        state["browsers"]["browser:social"]["viewStreams"][0]["readOnly"] = True
        self.assertIsNone(
            agent_browser_config.shared_profile_owner(
                plan,
                state,
                expected_profile_id="last30days-facebook",
            )
        )

    def test_runtime_profile_owner_requires_exact_cdp_and_user_data_identity(self):
        state = {
            "sessions": {
                "bound-social": {
                    "browserIds": ["browser:social"],
                    "tabIds": ["target:x"],
                }
            },
            "browsers": {
                "browser:social": {
                    "profileId": "default",
                    "health": "ready",
                    "cdpEndpoint": "ws://127.0.0.1:36603/devtools/browser/social",
                }
            },
            "tabs": {"target:x": {"targetId": "x"}},
        }
        runtime_status = {
            "runtimeProfile": "last30days-facebook",
            "browserAlive": True,
            "devtoolsReachable": True,
            "devtoolsPort": 36603,
            "userDataDir": "/profiles/last30days-facebook/user-data",
        }

        owner = agent_browser_config.runtime_profile_owner(
            state,
            runtime_status,
            expected_profile_id="last30days-facebook",
            expected_user_data_dir="/profiles/last30days-facebook/user-data",
        )
        self.assertEqual("browser:social", owner["browser_id"])
        self.assertEqual("bound-social", owner["session_name"])

        for field, wrong_value in (
            ("devtoolsPort", 36604),
            ("userDataDir", "/profiles/default/user-data"),
            ("runtimeProfile", "default"),
        ):
            mismatched = {**runtime_status, field: wrong_value}
            self.assertIsNone(
                agent_browser_config.runtime_profile_owner(
                    state,
                    mismatched,
                    expected_profile_id="last30days-facebook",
                    expected_user_data_dir="/profiles/last30days-facebook/user-data",
                ),
                field,
            )

    def test_shared_acquisition_route_uses_authoritative_access_plan_hints(self):
        route = agent_browser_config.shared_acquisition_route(
            access_plan(),
            expected_profile_id="last30days-facebook",
        )

        self.assertEqual(
            {
                "browser_id": "session:last30days-facebook",
                "session_name": "last30days-facebook",
            },
            route,
        )
