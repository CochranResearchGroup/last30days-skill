"""Hard-timeout acquisition cleanup stays bounded and source-owned."""

from unittest import mock

import pytest

from lib import service_acquisition_cleanup


def _payload(**overrides):
    payload = {
        "schema_version": 1,
        "profile_id": "last30days-facebook",
        "session_name": "last30days-facebook",
        "browser_id": "session:last30days-facebook",
    }
    payload.update(overrides)
    return payload


def test_cleanup_consolidates_facebook_and_preserves_browser():
    client = mock.Mock()
    with mock.patch.object(
        service_acquisition_cleanup,
        "CliAgentBrowserClient",
        return_value=client,
    ) as client_type:
        result = service_acquisition_cleanup.cleanup_facebook_tabs(_payload())

    assert result is client.prepare_site_tab.return_value
    client_type.assert_called_once_with(timeout=30)
    client.prepare_site_tab.assert_called_once_with(
        service_acquisition_cleanup.BrowserWorkspace(
            profile_id="last30days-facebook",
            browser_id="session:last30days-facebook",
            session_name="last30days-facebook",
        ),
        "facebook.com",
        consolidate=True,
        require_active=False,
        close_timeout=30,
        ignore_close_failures=True,
    )


def test_cleanup_rejects_unknown_or_unbounded_fields():
    with pytest.raises(ValueError, match="shape"):
        service_acquisition_cleanup.cleanup_facebook_tabs(
            _payload(extra="not allowed")
        )
    with pytest.raises(ValueError, match="profile_id"):
        service_acquisition_cleanup.cleanup_facebook_tabs(
            _payload(profile_id="x" * 257)
        )
