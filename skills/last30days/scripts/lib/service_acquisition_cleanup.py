"""Source-owned cleanup entrypoint for a hard-killed acquisition worker."""

from __future__ import annotations

import json
import sys
from collections.abc import Mapping

from .facebook import BrowserWorkspace, CliAgentBrowserClient


def cleanup_facebook_tabs(payload: Mapping[str, object]) -> bool:
    required = {"schema_version", "profile_id", "session_name", "browser_id"}
    if set(payload) != required or payload.get("schema_version") != 1:
        raise ValueError("cleanup request shape is invalid")
    fields = {}
    for name in ("profile_id", "session_name", "browser_id"):
        value = payload.get(name)
        if not isinstance(value, str) or not value.strip() or len(value) > 256:
            raise ValueError(f"cleanup request {name} is invalid")
        fields[name] = value.strip()
    client = CliAgentBrowserClient(timeout=30)
    return client.prepare_site_tab(
        BrowserWorkspace(
            profile_id=fields["profile_id"],
            browser_id=fields["browser_id"],
            session_name=fields["session_name"],
        ),
        "facebook.com",
        consolidate=True,
        require_active=False,
        close_timeout=30,
        ignore_close_failures=True,
    )


def main() -> int:
    try:
        raw = sys.stdin.buffer.read(4097)
        if len(raw) > 4096:
            raise ValueError("cleanup request exceeds its size bound")
        payload = json.loads(raw.decode("utf-8"))
        if not isinstance(payload, Mapping):
            raise ValueError("cleanup request must be an object")
        cleanup_facebook_tabs(payload)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
