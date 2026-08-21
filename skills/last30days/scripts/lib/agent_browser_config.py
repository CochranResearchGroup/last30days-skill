"""Shared agent-browser routing and user-scoped configuration helpers."""

from __future__ import annotations

import json
import os
import re
from urllib.parse import urlparse
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "last30days.agent-browser-targets.v1"
CONFIG_FILENAME = "agent-browser.json"
_TARGET_ID = re.compile(r"^[a-z][a-z0-9_.-]{0,63}$")
_STABLE_TARGET_FIELDS = frozenset(
    {
        "browser_build",
        "browser_host",
        "client_sharing_policy",
        "control_input_provider",
        "default_acquisition",
        "display_isolation",
        "profile_class",
        "profile_id",
        "profile_origin",
        "profile_process_policy",
        "recorded_at",
        "view_stream_provider",
    }
)


def config_path() -> Path:
    override = os.environ.get("LAST30DAYS_CONFIG_DIR")
    directory = Path(override).expanduser() if override else Path.home() / ".config" / "last30days"
    return directory / CONFIG_FILENAME


def selected_profile_id(access_plan: dict[str, Any]) -> str:
    selected = access_plan.get("selectedProfile")
    return str(selected.get("id") or "") if isinstance(selected, dict) else ""


def load_target_config(
    target_service_id: str,
    *,
    path: Path | None = None,
) -> dict[str, Any]:
    """Load one stable, non-secret target binding from user scope."""
    if not _TARGET_ID.fullmatch(target_service_id):
        return {}
    source = path or config_path()
    try:
        payload = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(payload, dict) or payload.get("schema_version") != SCHEMA_VERSION:
        return {}
    targets = payload.get("targets")
    target = targets.get(target_service_id) if isinstance(targets, dict) else None
    if not isinstance(target, dict):
        return {}
    return {
        str(key): value
        for key, value in target.items()
        if key in _STABLE_TARGET_FIELDS
        and (value is None or isinstance(value, (str, int, float, bool)))
    }


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


def shared_acquisition_route(
    access_plan: dict[str, Any],
    *,
    expected_profile_id: str,
) -> dict[str, str] | None:
    """Return broker-authoritative route hints for an already live shared browser."""
    if selected_profile_id(access_plan) != expected_profile_id:
        return None
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
    return {"browser_id": browser_id, "session_name": session_name}


def shared_profile_owner(
    access_plan: dict[str, Any],
    service_state: dict[str, Any],
    *,
    expected_profile_id: str,
) -> dict[str, Any] | None:
    """Resolve a live retained owner suitable for automated acquisition.

    Human-view requirements can make an otherwise healthy same-profile browser
    incompatible with the requested RDP route. Acquisition may still reuse that
    owner when it exposes writable CDP control; observation remains a separate
    incident-gated concern.
    """
    decision = access_plan.get("decision")
    reuse = decision.get("profileReuse") if isinstance(decision, dict) else {}
    if not isinstance(reuse, dict):
        return None

    browsers = service_state.get("browsers")
    sessions = service_state.get("sessions")
    tabs = service_state.get("tabs")
    if not isinstance(browsers, dict) or not isinstance(sessions, dict):
        return None

    browser_id = ""
    session_name = ""
    shared = reuse.get("sharedAcquisition")
    if (
        reuse.get("recommendedAction") == "reuse_existing_browser"
        and isinstance(shared, dict)
        and shared.get("mode") == "tab_new"
    ):
        browser_id = str(
            shared.get("browserId") or reuse.get("reusableBrowserId") or ""
        )
        session_name = str(
            shared.get("sessionName") or reuse.get("reusableSessionName") or ""
        )
    else:
        for candidate_id in reuse.get("sameProfileLiveBrowserIds") or ():
            candidate_id = str(candidate_id or "")
            candidate = browsers.get(candidate_id)
            if not isinstance(candidate, dict) or candidate.get("health") != "ready":
                continue
            observed_profile = str(
                candidate.get("profileId") or candidate.get("runtimeProfile") or ""
            )
            if observed_profile and observed_profile != expected_profile_id:
                continue
            streams = candidate.get("viewStreams") or ()
            if not any(
                isinstance(stream, dict)
                and stream.get("provider") == "cdp_screencast"
                and stream.get("controlInput") == "cdp_input"
                and stream.get("readOnly") is not True
                for stream in streams
            ):
                continue
            for candidate_session in reuse.get("activeLeaseSessionIds") or ():
                session = sessions.get(str(candidate_session))
                if isinstance(session, dict) and candidate_id in (
                    session.get("browserIds") or ()
                ):
                    browser_id = candidate_id
                    session_name = str(candidate_session)
                    break
            if not session_name:
                for candidate_session, session in sessions.items():
                    if isinstance(session, dict) and candidate_id in (
                        session.get("browserIds") or ()
                    ):
                        browser_id = candidate_id
                        session_name = str(candidate_session)
                        break
            if browser_id and session_name:
                break

    if not browser_id or not session_name:
        return None

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


def needs_runtime_profile_owner_resolution(
    service_state: dict[str, Any],
    *,
    expected_profile_id: str,
) -> bool:
    """Return whether a ready CDP row may carry a stale profile label."""
    browsers = service_state.get("browsers")
    if not isinstance(browsers, dict):
        return False
    for browser in browsers.values():
        if not isinstance(browser, dict) or browser.get("health") != "ready":
            continue
        observed_profile = str(
            browser.get("profileId") or browser.get("runtimeProfile") or ""
        )
        if observed_profile == expected_profile_id:
            continue
        if _loopback_cdp_port(browser.get("cdpEndpoint")) is not None:
            return True
    return False


def runtime_profile_owner(
    service_state: dict[str, Any],
    runtime_status: dict[str, Any],
    *,
    expected_profile_id: str,
    expected_user_data_dir: str = "",
) -> dict[str, Any] | None:
    """Resolve a stale broker row from runtime-profile-owned CDP evidence.

    The runtime-profile status is authoritative for the physical browser. A
    retained browser is accepted only when its exact loopback CDP port matches
    that live runtime and, when available, its user-data directory also agrees.
    """
    if str(runtime_status.get("runtimeProfile") or "") != expected_profile_id:
        return None
    if runtime_status.get("browserAlive") is not True:
        return None
    if runtime_status.get("devtoolsReachable") is not True:
        return None
    try:
        runtime_port = int(runtime_status.get("devtoolsPort") or 0)
    except (TypeError, ValueError):
        return None
    if runtime_port < 1:
        return None
    observed_user_data_dir = str(runtime_status.get("userDataDir") or "")
    if (
        expected_user_data_dir
        and observed_user_data_dir
        and observed_user_data_dir != expected_user_data_dir
    ):
        return None

    browsers = service_state.get("browsers")
    sessions = service_state.get("sessions")
    tabs = service_state.get("tabs")
    if not isinstance(browsers, dict) or not isinstance(sessions, dict):
        return None

    matches: list[tuple[int, str, dict[str, Any]]] = []
    for browser_id, browser in browsers.items():
        if not isinstance(browser, dict) or browser.get("health") != "ready":
            continue
        if _loopback_cdp_port(browser.get("cdpEndpoint")) != runtime_port:
            continue
        streams = browser.get("viewStreams") or ()
        route_ready = any(
            isinstance(stream, dict)
            and stream.get("provider") == "rdp_gateway"
            and isinstance(stream.get("readiness"), dict)
            and stream["readiness"].get("state") == "ready"
            for stream in streams
        )
        matches.append((1 if route_ready else 0, str(browser_id), browser))
    if not matches:
        return None
    _, browser_id, browser = max(matches, key=lambda item: (item[0], item[1]))

    session_name = ""
    for candidate_session in browser.get("activeSessionIds") or ():
        session = sessions.get(str(candidate_session))
        if isinstance(session, dict) and browser_id in (session.get("browserIds") or ()):
            session_name = str(candidate_session)
            break
    if not session_name:
        for candidate_session, session in sessions.items():
            if isinstance(session, dict) and browser_id in (session.get("browserIds") or ()):
                session_name = str(candidate_session)
                break
    if not session_name:
        return None

    target_id = ""
    session = sessions.get(session_name)
    if isinstance(session, dict) and isinstance(tabs, dict):
        for tab_id in session.get("tabIds") or ():
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


def _loopback_cdp_port(value: Any) -> int | None:
    try:
        parsed = urlparse(str(value or ""))
        if parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
            return None
        return parsed.port
    except ValueError:
        return None


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
