"""Bounded exact-profile acquisition tests."""

from types import SimpleNamespace
from unittest.mock import patch

from lib import linkedin


class FakeClient:
    def __init__(self, *, checkpoint=False):
        self.actions = []
        self.checkpoint = checkpoint

    def acquire_workspace(self, request):
        self.request = request
        return SimpleNamespace(
            operator_url="http://operator.invalid",
            profile_id=request.profile_id,
        )

    def inspect_auth(self, workspace):
        return SimpleNamespace(
            authenticated=not self.checkpoint,
            checkpoint=self.checkpoint,
        )

    def prepare_site_tab(self, workspace, hostname, *, consolidate=False):
        return True

    def act(self, workspace, action):
        self.actions.append(action)

    def evaluate(self, workspace, script):
        if script == linkedin.PROFILE_STATE_SCRIPT:
            return {
                "url": "https://www.linkedin.com/in/ada/",
                "login_page": False,
                "checkpoint": False,
                "error_page": False,
            }
        if script == linkedin.PROFILE_EXTRACT_SCRIPT:
            return {
                "display_name": "Ada Lovelace",
                "headline": "Computing pioneer",
                "about": "Analytical Engines",
                "experience": "",
                "education": "",
                "locations": "London",
                "declared_links": ["https://ada.example/"],
            }
        raise AssertionError("unexpected script")


def test_exact_linkedin_profile_is_normalized_without_private_surface_actions():
    client = FakeClient()
    with (
        patch.object(linkedin, "is_agent_browser_available", return_value=True),
        patch.object(linkedin, "CliAgentBrowserClient", return_value=client),
    ):
        result = linkedin.acquire_linkedin_profile(
            "https://www.linkedin.com/in/ada",
            config={"LAST30DAYS_LINKEDIN_PROFILE": "linkedin-primary"},
        )

    assert result["error"] is None
    assert result["items"][0]["metadata"]["surface_kind"] == "profile"
    assert result["items"][0]["metadata"]["account_kind"] == "person"
    assert {action.operation for action in client.actions} <= {"navigate", "wait"}
    assert client.request.task_name == "linkedin-profile-acquisition"


def test_invalid_or_checkpointed_profile_never_navigates():
    assert linkedin.acquire_linkedin_profile(
        "https://www.linkedin.com/messaging/"
    )["error_type"] == "invalid_request"

    client = FakeClient(checkpoint=True)
    with (
        patch.object(linkedin, "is_agent_browser_available", return_value=True),
        patch.object(linkedin, "CliAgentBrowserClient", return_value=client),
    ):
        result = linkedin.acquire_linkedin_profile(
            "https://www.linkedin.com/company/openai/"
        )
    assert result["error_type"] == "checkpoint_required"
    assert client.actions == []
