"""Shared agent-browser routing and user-scoped configuration helpers."""

from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "last30days.agent-browser-targets.v1"
CONFIG_FILENAME = "agent-browser.json"


def config_path() -> Path:
    override = os.environ.get("LAST30DAYS_CONFIG_DIR")
    directory = Path(override).expanduser() if override else Path.home() / ".config" / "last30days"
    return directory / CONFIG_FILENAME


def selected_profile_id(access_plan: dict[str, Any]) -> str:
    selected = access_plan.get("selectedProfile")
    return str(selected.get("id") or "") if isinstance(selected, dict) else ""


def record_access_plan(
    access_plan: dict[str, Any],
    target_service_id: str,
    *,
    path: Path | None = None,
    recorded_at: datetime | None = None,
) -> Path:
    """Persist stable, non-secret broker configuration for one target."""
    destination = path or config_path()
    destination.parent.mkdir(parents=True, exist_ok=True)

    existing: dict[str, Any] = {}
    if destination.exists():
        try:
            loaded = json.loads(destination.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                existing = loaded
        except (OSError, json.JSONDecodeError):
            existing = {}

    targets = existing.get("targets")
    if not isinstance(targets, dict):
        targets = {}

    targets[target_service_id] = _stable_target_config(
        access_plan,
        recorded_at=recorded_at or datetime.now(timezone.utc),
    )
    payload = {
        "schema_version": SCHEMA_VERSION,
        "targets": targets,
    }
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"

    temporary_name = ""
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=destination.parent,
            prefix=f".{destination.name}.",
            delete=False,
        ) as temporary:
            temporary.write(rendered)
            temporary.flush()
            os.fsync(temporary.fileno())
            temporary_name = temporary.name
        os.chmod(temporary_name, 0o600)
        os.replace(temporary_name, destination)
    finally:
        if temporary_name:
            try:
                Path(temporary_name).unlink()
            except FileNotFoundError:
                pass
    return destination


def shared_profile_owner(
    access_plan: dict[str, Any],
    service_state: dict[str, Any],
    *,
    expected_profile_id: str,
) -> dict[str, Any] | None:
    """Resolve a live retained owner from broker-provided shared-acquisition hints."""
    decision = access_plan.get("decision")
    reuse = decision.get("profileReuse") if isinstance(decision, dict) else {}
    if not isinstance(reuse, dict) or reuse.get("recommendedAction") != "reuse_existing_browser":
        return None

    shared = reuse.get("sharedAcquisition")
    if not isinstance(shared, dict) or shared.get("mode") != "tab_new":
        return None
    browser_id = str(shared.get("browserId") or reuse.get("reusableBrowserId") or "")
    session_name = str(shared.get("sessionName") or reuse.get("reusableSessionName") or "")
    if not browser_id or not session_name:
        return None

    browsers = service_state.get("browsers")
    sessions = service_state.get("sessions")
    tabs = service_state.get("tabs")
    browser = browsers.get(browser_id) if isinstance(browsers, dict) else None
    session = sessions.get(session_name) if isinstance(sessions, dict) else None
    if not isinstance(browser, dict) or browser.get("health") != "ready":
        return None
    observed_profile = str(browser.get("profileId") or browser.get("runtimeProfile") or "")
    if observed_profile and observed_profile != expected_profile_id:
        return None

    target_id = ""
    if isinstance(session, dict) and isinstance(tabs, dict):
        for tab_id in session.get("tabIds") or []:
            tab = tabs.get(tab_id)
            if isinstance(tab, dict):
                target_id = str(tab.get("targetId") or str(tab_id).removeprefix("target:"))
                if target_id:
                    break

    return {
        "browser_id": browser_id,
        "session_name": session_name,
        "target_id": target_id,
        "browser": browser,
    }


def _stable_target_config(
    access_plan: dict[str, Any],
    *,
    recorded_at: datetime,
) -> dict[str, Any]:
    selected = access_plan.get("selectedProfile")
    selected = selected if isinstance(selected, dict) else {}
    decision = access_plan.get("decision")
    decision = decision if isinstance(decision, dict) else {}
    launch = decision.get("launchPosture")
    launch = launch if isinstance(launch, dict) else {}
    reuse = decision.get("profileReuse")
    reuse = reuse if isinstance(reuse, dict) else {}

    return _without_empty_values({
        "browser_build": launch.get("browserBuild"),
        "browser_host": launch.get("browserHost"),
        "client_sharing_policy": reuse.get("clientSharingPolicy"),
        "control_input_provider": launch.get("controlInputProvider"),
        "default_acquisition": reuse.get("defaultAcquisition"),
        "display_isolation": launch.get("displayIsolation"),
        "profile_class": selected.get("profileClass"),
        "profile_id": selected.get("id"),
        "profile_origin": selected.get("profileOrigin"),
        "profile_process_policy": reuse.get("profileProcessPolicy"),
        "recorded_at": recorded_at.astimezone(timezone.utc).isoformat(),
        "view_stream_provider": launch.get("viewStreamProvider"),
    })


def _without_empty_values(values: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in values.items() if value not in (None, "", [], {})}
