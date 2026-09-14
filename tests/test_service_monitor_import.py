"""Explicit legacy exports create disabled drafts and discard channel secrets."""

import json

import pytest
from lib.service_monitors import MonitorKernelError

from tests.test_service_monitor_application import command, composition


def test_legacy_export_import_is_idempotent_and_never_copies_webhook(tmp_path):
    app, _, _ = composition(tmp_path)
    exported = {
        "source_locator": "fixture:legacy-export-1",
        "topic": {
            "id": "7",
            "query": "browser agents",
            "interval_seconds": 3600,
            "webhook_url": "https://example.invalid/secret-token",
            "enabled": True,
        },
    }
    result = command(app, "import_legacy", export=exported)
    assert result["monitor"]["lifecycle_state"] == "disabled"
    assert result["delivery"]["mode"] == "disabled"
    assert result["unmapped_fields"] == ["enabled", "webhook_url"]
    assert command(app, "import_legacy", export=exported) == result
    assert "secret-token" not in json.dumps(result)
    assert b"secret-token" not in app.db_path.read_bytes()
    exported["topic"]["query"] = "different query"
    with pytest.raises(MonitorKernelError):
        command(app, "import_legacy", export=exported)
