"""Provider-neutral Agent Browser workspace lifecycle.

This module owns broker acquisition, attributed target coherence, page control,
and exact release. Provider modules add site-specific authentication and
extraction without owning the shared browser runtime.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
import math
import os
from pathlib import Path
import queue
import re
import shutil
import stat
import subprocess
import threading
import time
from typing import Any, Literal, Protocol
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

from . import agent_browser_config, log


MAX_RUN_BUDGET_SECONDS = 105
REMOTE_VIEW_RECONCILIATION_RESERVE_SECONDS = 10
TAB_INVENTORY_TIMEOUT_SECONDS = 20
SERVICE_EVALUATE_MAX_RETURN_BYTES = 1_048_576
SERVICE_TAB_READY_TIMEOUT_MS = 15_000
SERVICE_TAB_READY_OUTER_TIMEOUT_SECONDS = 30
PROFILE_CAPABILITY_FILE_ENV = "LAST30DAYS_AGENT_BROWSER_PROFILE_CAPABILITY_FILE"
MAX_PROFILE_CAPABILITY_BYTES = 4_096
ERROR_TYPES = {
    "agent_browser_missing",
    "profile_mismatch",
    "route_stale",
    "auth_required",
    "auth_state_ambiguous",
    "checkpoint_required",
    "rate_limit_detected",
    "operator_ingress_unavailable",
    "navigation_mismatch",
    "search_unavailable",
    "extraction_empty",
    "quality_gate_failed",
    "facebook_target_unresponsive",
    "agent_browser_timeout",
    "agent_browser_error",
}
RATE_LIMIT_REASONS = frozenset(
    {"temporary_block", "action_frequency_limit", "unspecified"}
)


@dataclass(frozen=True)
class BrowserWorkspaceRequest:
    profile_id: str
    session_name: str
    browser_build: str
    view_provider: str
    timeout: int
    browser_id_hint: str = ""
    route_id_hint: str = ""
    route_pool_entry_id_hint: str = ""
    start_url: str = "about:blank"
    service_name: str = "last30days"
    agent_name: str = "last30days"
    task_name: str = "browser-workspace"
    target_service_id: str = ""
    browser_host: str = "remote_headed"
    display_isolation: str = "private_virtual_display"
    control_input_provider: str = "manual_attached_desktop"
    constrain_presentation: bool = False
    allow_duplicate_profile_lane: bool = False


@dataclass(frozen=True)
class BrowserWorkspace:
    profile_id: str
    browser_id: str
    session_name: str
    target_id: str = ""
    route_id: str = ""
    display_allocation_id: str = ""
    operator_url: str = ""
    operator_visible_state: str = "missing"


@dataclass(frozen=True)
class BrowserSnapshot:
    refs: dict[str, dict[str, Any]] = field(default_factory=dict)
    text: str = ""


@dataclass(frozen=True)
class BrowserAction:
    operation: Literal[
        "fill", "press", "click", "wait", "navigate", "new_tab", "scroll"
    ]
    target: str = ""
    value: str = ""


@dataclass(frozen=True)
class BrowserState:
    url: str = ""
    title: str = ""


class AgentBrowserRuntimeFailure(RuntimeError):
    def __init__(
        self,
        error_type: str,
        message: str,
        *,
        operator_url: str = "",
        reason_code: str = "",
    ) -> None:
        if error_type not in ERROR_TYPES:
            error_type = "agent_browser_error"
        super().__init__(message)
        self.error_type = error_type
        self.operator_url = operator_url
        if error_type == "rate_limit_detected":
            self.reason_code = (
                reason_code if reason_code in RATE_LIMIT_REASONS else "unspecified"
            )
        elif re.fullmatch(r"[a-z][a-z0-9_]{0,63}", reason_code):
            self.reason_code = reason_code
        else:
            self.reason_code = ""


class AgentBrowserClient(Protocol):
    def acquire_workspace(
        self,
        request: BrowserWorkspaceRequest,
        *,
        access_plan: dict[str, Any] | None = None,
        target_service_id: str | None = None,
    ) -> BrowserWorkspace: ...
    def prepare_operator_handoff(
        self, workspace: BrowserWorkspace, request: BrowserWorkspaceRequest
    ) -> BrowserWorkspace: ...
    def snapshot(self, workspace: BrowserWorkspace) -> BrowserSnapshot: ...
    def act(self, workspace: BrowserWorkspace, action: BrowserAction) -> BrowserState: ...
    def evaluate(self, workspace: BrowserWorkspace, script: str) -> dict[str, Any]: ...
    def evaluate_navigation_state(
        self, workspace: BrowserWorkspace, script: str
    ) -> dict[str, Any]: ...
    def release_workspace(self) -> None: ...


class CliAgentBrowserClient:
    """Typed adapter for the installed Agent Browser service and JSON CLI."""

    def __init__(
        self,
        *,
        timeout: int,
        job_timeout_ms: int | None = None,
        profile_capability_file: str | os.PathLike[str] | None = None,
    ) -> None:
        self.timeout = timeout
        self.job_timeout_ms = job_timeout_ms or timeout * 1000
        if self.job_timeout_ms <= 0:
            raise ValueError("agent-browser job timeout must be positive")
        self.command_timings: list[dict[str, Any]] = []
        self._prepared_sites: set[tuple[str, str]] = set()
        self._run_deadline: float | None = None
        self._requested_profile_id = ""
        configured_capability_file = (
            profile_capability_file
            if profile_capability_file is not None
            else os.environ.get(PROFILE_CAPABILITY_FILE_ENV)
        )
        self._profile_capability_file = (
            Path(configured_capability_file)
            if configured_capability_file
            else None
        )
        self._profile_capability = ""
        self._service_request_route: dict[str, Any] | None = None
        self._service_tab_handle: dict[str, Any] | None = None
        self._service_tab_url = ""
        self._mcp_process: subprocess.Popen[str] | None = None
        self._mcp_responses: queue.Queue[dict[str, Any]] = queue.Queue()
        self._mcp_response_cache: dict[int, dict[str, Any]] = {}
        self._mcp_request_id = 1
        self._mcp_stderr_lines: list[str] = []

    def begin_run_budget(self, timeout: int) -> None:
        """Bound cumulative adapter work so parent timeout cleanup still runs."""
        self._run_deadline = time.monotonic() + max(
            1, min(timeout, MAX_RUN_BUDGET_SECONDS)
        )

    def end_run_budget(self) -> None:
        self._run_deadline = None

    def acquire_workspace(
        self,
        request: BrowserWorkspaceRequest,
        *,
        access_plan: dict[str, Any] | None = None,
        target_service_id: str | None = None,
    ) -> BrowserWorkspace:
        self._requested_profile_id = request.profile_id
        self._service_request_route = None
        self._service_tab_handle = None
        self._service_tab_url = ""
        requested_target_service_id = target_service_id or request.target_service_id
        if access_plan is None:
            access_plan = self._resolve_access_plan(
                request,
                target_service_id=requested_target_service_id,
            )
        elif not self._profile_capability:
            self._profile_capability = self._read_profile_capability()
        selected_profile = agent_browser_config.selected_profile_id(access_plan)
        if not selected_profile:
            raise AgentBrowserRuntimeFailure(
                "auth_required",
                "agent-browser has no authenticated profile registered for "
                f"{requested_target_service_id}",
            )
        if selected_profile != request.profile_id:
            raise AgentBrowserRuntimeFailure(
                "profile_mismatch",
                f"agent-browser selected {requested_target_service_id} profile "
                f"{selected_profile!r}, not {request.profile_id!r}",
            )
        try:
            agent_browser_config.record_access_plan(access_plan, requested_target_service_id)
        except OSError as exc:
            _log(f"Could not record user-scoped agent-browser configuration: {_redact(str(exc))}")

        decision = access_plan.get("decision")
        profile_reuse = (
            decision.get("profileReuse") if isinstance(decision, dict) else None
        )
        service_request_record = (
            decision.get("serviceRequest") if isinstance(decision, dict) else None
        )
        broker_request = (
            service_request_record.get("request")
            if isinstance(service_request_record, dict)
            else None
        )
        compatible_live_browser_count = (
            profile_reuse.get("compatibleLiveBrowserCount", 0)
            if isinstance(profile_reuse, dict)
            else 0
        )
        route_bound_cold_launch = (
            request.browser_host == "remote_headed"
            and bool(request.route_pool_entry_id_hint)
            and compatible_live_browser_count == 0
        )
        if (
            isinstance(service_request_record, dict)
            and service_request_record.get("available") is True
            and service_request_record.get("blockedByAcquisition") is not True
            and service_request_record.get("blockedByLifecycleOwner") is not True
            and isinstance(broker_request, dict)
            and broker_request.get("action") == "tab_new"
            and not route_bound_cold_launch
        ):
            self._service_request_route = dict(broker_request)
            shared_acquisition = (
                profile_reuse.get("sharedAcquisition")
                if isinstance(profile_reuse, dict)
                else None
            )
            same_profile_browser_ids = (
                profile_reuse.get("sameProfileLiveBrowserIds")
                if isinstance(profile_reuse, dict)
                else None
            )
            active_lease_session_ids = (
                profile_reuse.get("activeLeaseSessionIds")
                if isinstance(profile_reuse, dict)
                else None
            )
            route_browser_id = str(
                broker_request.get("browserId")
                or (
                    profile_reuse.get("reusableBrowserId")
                    if isinstance(profile_reuse, dict)
                    else ""
                )
                or (
                    shared_acquisition.get("browserId")
                    if isinstance(shared_acquisition, dict)
                    else ""
                )
                or (
                    same_profile_browser_ids[0]
                    if isinstance(same_profile_browser_ids, list)
                    and len(same_profile_browser_ids) == 1
                    else ""
                )
                or ""
            )
            route_session_name = str(
                broker_request.get("sessionName")
                or (
                    profile_reuse.get("reusableSessionName")
                    if isinstance(profile_reuse, dict)
                    else ""
                )
                or (
                    shared_acquisition.get("sessionName")
                    if isinstance(shared_acquisition, dict)
                    else ""
                )
                or (
                    active_lease_session_ids[0]
                    if isinstance(active_lease_session_ids, list)
                    and len(active_lease_session_ids) == 1
                    else ""
                )
                or ""
            )
            self._service_request_route.update(
                {
                    "action": "tab_new",
                    "serviceName": request.service_name,
                    "agentName": request.agent_name,
                    "taskName": request.task_name,
                    "targetServiceIds": [requested_target_service_id],
                    "browserBuild": request.browser_build,
                    "runtimeProfile": selected_profile,
                    "profileLeasePolicy": "wait",
                    "url": request.start_url,
                }
            )
            if request.allow_duplicate_profile_lane:
                self._service_request_route["allowDuplicateProfileLane"] = True
            if request.route_pool_entry_id_hint:
                route_params = self._service_request_route.get("params")
                if not isinstance(route_params, dict):
                    route_params = {}
                else:
                    route_params = dict(route_params)
                route_params["routePoolEntryId"] = request.route_pool_entry_id_hint
                self._service_request_route["params"] = route_params
            if route_browser_id and route_session_name:
                self._service_request_route.update(
                    {
                        "browserId": route_browser_id,
                        "sessionName": route_session_name,
                    }
                )
            if (
                request.allow_duplicate_profile_lane
                and compatible_live_browser_count == 0
            ):
                self._service_request_route.pop("browserId", None)
                if not str(broker_request.get("sessionName") or ""):
                    self._service_request_route["sessionName"] = request.session_name
            broker_timeout = min(request.timeout, 30)
            broker_started = time.monotonic()
            try:
                acquired = self._invoke_service_request(
                    dict(self._service_request_route),
                    timeout=broker_timeout,
                )
            except subprocess.TimeoutExpired as exc:
                self.command_timings.append(
                    {
                        "operation": "service_request:tab_new",
                        "duration_ms": _elapsed_ms(broker_started),
                        "status": "timed_out",
                    }
                )
                raise AgentBrowserRuntimeFailure(
                    "agent_browser_timeout",
                    f"agent-browser broker request timed out after {broker_timeout}s",
                    reason_code="broker_service_request_timeout",
                ) from exc
            except (OSError, AgentBrowserRuntimeFailure):
                self.command_timings.append(
                    {
                        "operation": "service_request:tab_new",
                        "duration_ms": _elapsed_ms(broker_started),
                        "status": "failed",
                    }
                )
                raise
            self.command_timings.append(
                {
                    "operation": "service_request:tab_new",
                    "duration_ms": _elapsed_ms(broker_started),
                    "status": "ok",
                }
            )
            service_tab_handle = acquired.get("serviceTabHandle")
            if not isinstance(service_tab_handle, dict):
                raise AgentBrowserRuntimeFailure(
                    "agent_browser_error",
                    "agent-browser broker tab acquisition returned no service tab handle",
                    reason_code="broker_service_tab_handle_missing",
                )
            browser_id = str(service_tab_handle.get("browserId") or "")
            session_name = str(service_tab_handle.get("sessionName") or "")
            target_id = str(service_tab_handle.get("targetId") or "")
            if not browser_id or not session_name or not target_id:
                raise AgentBrowserRuntimeFailure(
                    "agent_browser_error",
                    "agent-browser broker tab handle is missing target ownership",
                    reason_code="broker_service_tab_ownership_missing",
                )
            if service_tab_handle.get("valid") is False:
                raise AgentBrowserRuntimeFailure(
                    "agent_browser_error",
                    "agent-browser broker tab handle is not valid",
                    reason_code="broker_service_tab_handle_invalid",
                )
            self._service_tab_handle = dict(service_tab_handle)
            self._service_tab_url = str(acquired.get("url") or request.start_url)
            self._service_request_route.update(
                {"browserId": browser_id, "sessionName": session_name}
            )
            self._invoke(
                ["--session", session_name, "tab", "handle-ready"],
                timeout=min(request.timeout, SERVICE_TAB_READY_OUTER_TIMEOUT_SECONDS),
            )
            return BrowserWorkspace(
                profile_id=selected_profile,
                browser_id=browser_id,
                session_name=session_name,
                target_id=target_id,
                operator_visible_state="not_required",
            )
        if (
            isinstance(profile_reuse, dict)
            and profile_reuse.get("recommendedAction") == "wait_for_profile_lease"
        ):
            raise AgentBrowserRuntimeFailure(
                "agent_browser_error",
                "agent-browser access plan requires wait_for_profile_lease",
                reason_code="profile_lease_wait_required",
            )

        shared_route = agent_browser_config.shared_acquisition_route(
            access_plan,
            expected_profile_id=selected_profile,
        )

        status = self._invoke(["service", "status"], timeout=min(request.timeout, 30))
        state = status.get("service_state") if isinstance(status.get("service_state"), dict) else status
        sessions = state.get("sessions") if isinstance(state, dict) else {}
        browsers = state.get("browsers") if isinstance(state, dict) else {}
        tabs = state.get("tabs") if isinstance(state, dict) else {}
        shared_owner = agent_browser_config.shared_profile_owner(
            access_plan,
            state if isinstance(state, dict) else {},
            expected_profile_id=selected_profile,
        )
        if (
            not shared_owner
            and isinstance(state, dict)
            and agent_browser_config.needs_runtime_profile_owner_resolution(
                state,
                expected_profile_id=selected_profile,
            )
        ):
            try:
                runtime_status = self._invoke(
                    [
                        "--runtime-profile",
                        selected_profile,
                        "runtime",
                        "status",
                    ],
                    timeout=min(request.timeout, 30),
                )
            except AgentBrowserRuntimeFailure:
                runtime_status = {}
            selected_profile_record = access_plan.get("selectedProfile")
            expected_user_data_dir = (
                str(selected_profile_record.get("userDataDir") or "")
                if isinstance(selected_profile_record, dict)
                else ""
            )
            shared_owner = agent_browser_config.runtime_profile_owner(
                state,
                runtime_status,
                expected_profile_id=selected_profile,
                expected_user_data_dir=expected_user_data_dir,
            )
        if shared_owner:
            browser = shared_owner["browser"]
            service_session_name = shared_owner["session_name"]
            command_session_name = shared_owner.get("command_session_name") or ""
            owner_session_name = command_session_name or service_session_name
            owner_session = (
                sessions.get(service_session_name)
                if isinstance(sessions, dict)
                else None
            )
            if _session_has_ambiguous_browser_ownership(
                owner_session,
                shared_owner["browser_id"],
            ) and not shared_owner.get("command_session_name"):
                owner_session_name = self._bind_exact_cdp_session(
                    browser=browser,
                    browser_id=shared_owner["browser_id"],
                    request=request,
                )
            else:
                decision = access_plan.get("decision")
                service_request_record = (
                    decision.get("serviceRequest")
                    if isinstance(decision, dict)
                    else None
                )
                service_request = (
                    service_request_record.get("request")
                    if isinstance(service_request_record, dict)
                    else None
                )
                self._service_request_route = dict(service_request or {})
                self._service_request_route.update(
                    {
                        "serviceName": request.service_name,
                        "agentName": request.agent_name,
                        "taskName": request.task_name,
                        "targetServiceIds": [requested_target_service_id],
                        "browserBuild": request.browser_build,
                        "runtimeProfile": selected_profile,
                        "browserId": shared_owner["browser_id"],
                        "sessionName": owner_session_name,
                        "profileLeasePolicy": "wait",
                    }
                )
                acquired = self._invoke(
                    [
                        "--session",
                        owner_session_name,
                        "tab",
                        "new",
                        request.start_url,
                    ],
                    timeout=min(request.timeout, 30),
                )
                service_tab_handle = acquired.get("serviceTabHandle")
                if not isinstance(service_tab_handle, dict):
                    raise AgentBrowserRuntimeFailure(
                        "agent_browser_error",
                        "agent-browser retained tab acquisition returned no service tab handle",
                    )
                self._service_tab_handle = dict(service_tab_handle)
                self._service_tab_url = request.start_url
                self._invoke(
                    ["--session", owner_session_name, "tab", "handle-ready"],
                    timeout=min(
                        request.timeout,
                        SERVICE_TAB_READY_OUTER_TIMEOUT_SECONDS,
                    ),
                )
            stream = _ready_operator_stream(browser, request.view_provider)
            return BrowserWorkspace(
                profile_id=selected_profile,
                browser_id=shared_owner["browser_id"],
                session_name=owner_session_name,
                target_id=str(
                    (self._service_tab_handle or {}).get("targetId")
                    or shared_owner["target_id"]
                ),
                route_id=str(stream.get("id") or ""),
                operator_url=_operator_url(stream),
                operator_visible_state="ready" if stream else "not_required",
            )

        if shared_route:
            return BrowserWorkspace(
                profile_id=selected_profile,
                browser_id=shared_route["browser_id"],
                session_name=shared_route["session_name"],
                operator_visible_state="not_required",
            )

        session = sessions.get(request.session_name) if isinstance(sessions, dict) else None
        browser: dict[str, Any] | None = None
        browser_id = ""
        target_id = ""
        launch_session_name = request.session_name
        owner_session_name = request.session_name
        if route_bound_cold_launch and isinstance(broker_request, dict):
            planned_session_name = str(broker_request.get("sessionName") or "")
            if planned_session_name:
                launch_session_name = planned_session_name
                owner_session_name = planned_session_name

        aliased_owner = _exact_retained_default_owner(
            session_name=request.session_name,
            selected_profile=selected_profile,
            target_service_id=requested_target_service_id,
            sessions=sessions,
            browsers=browsers,
            tabs=tabs,
        )
        if aliased_owner:
            browser = aliased_owner["browser"]
            browser_id = aliased_owner["browser_id"]
            target_id = aliased_owner["target_id"]
            owner_session_name = aliased_owner["session_name"]

        if isinstance(session, dict) and browser is None:
            observed_profile = str(session.get("profileId") or "")
            if not observed_profile or observed_profile == selected_profile:
                browser_ids = session.get("browserIds") or []
                if browser_ids:
                    browser_id = str(browser_ids[0])
                    candidate = browsers.get(browser_id) if isinstance(browsers, dict) else None
                    if isinstance(candidate, dict) and candidate.get("health") == "ready":
                        browser = candidate
                        target_id = _select_target_id(session, tabs)
            else:
                # A retained CLI session name is not a browser identity. Keep
                # the unrelated browser alive and open the broker-selected
                # profile on a deterministic, profile-scoped session lane.
                launch_session_name = _profile_scoped_session_name(
                    sessions, request.session_name, selected_profile
                )

        if browser:
            # A ready retained CDP browser is sufficient for ordinary collection.
            # The requested operator stream is prepared later, on demand, only
            # after authentication or checkpoint inspection requires a human.
            stream = _ready_operator_stream(browser, request.view_provider)
            return BrowserWorkspace(
                profile_id=request.profile_id,
                browser_id=browser_id,
                session_name=owner_session_name,
                target_id=target_id,
                route_id=str(stream.get("id") or ""),
                operator_url=_operator_url(stream),
                operator_visible_state="ready" if stream else "not_required",
            )

        decision = access_plan.get("decision") if isinstance(access_plan, dict) else {}
        launch_posture = (
            decision.get("launchPosture") if isinstance(decision, dict) else {}
        )
        remote_view_recommended = (
            launch_posture.get("remoteViewRecommended", True)
            if isinstance(launch_posture, dict)
            else True
        )
        reconcile_late_open = (
            remote_view_recommended
            and requested_target_service_id == "facebook"
        )
        if remote_view_recommended:
            cmd = [
                "--session", launch_session_name,
                "remote-view", "open", request.start_url,
                "--browser-build", request.browser_build,
                "--browser-host", request.browser_host,
                "--view-stream-provider", request.view_provider,
                "--control-input-provider", request.control_input_provider,
                "--display-isolation", request.display_isolation,
                "--session-name", launch_session_name,
                "--service-name", request.service_name,
                "--agent-name", request.agent_name,
                "--task-name", request.task_name,
                "--job-timeout-ms", str(self.job_timeout_ms),
            ]
            if browser:
                cmd.extend(["--browser-id", browser_id])
            else:
                cmd.extend(["--runtime-profile", selected_profile])

            route_entry = _select_live_route_entry(state, request) if not browser else ""
            if route_entry:
                cmd.extend(["--route-pool-entry-id", route_entry])
        else:
            cmd = [
                "--runtime-profile", selected_profile,
                "--session", launch_session_name,
                "--headed",
                "--browser-build", request.browser_build,
                "open", request.start_url,
                "--service-name", request.service_name,
                "--agent-name", request.agent_name,
                "--task-name", request.task_name,
            ]

        open_timeout = max(
            request.timeout, (self.job_timeout_ms + 999) // 1000 + 5
        )
        if reconcile_late_open and self._run_deadline is not None:
            remaining_seconds = max(
                1, int(self._run_deadline - time.monotonic())
            )
            open_timeout = min(
                open_timeout,
                max(
                    1,
                    remaining_seconds
                    - REMOTE_VIEW_RECONCILIATION_RESERVE_SECONDS,
                ),
            )

        try:
            opened = self._invoke(
                cmd,
                timeout=open_timeout,
            )
        except AgentBrowserRuntimeFailure as exc:
            newly_selected_lane = not isinstance(
                sessions.get(launch_session_name) if isinstance(sessions, dict) else None,
                dict,
            )
            startup_profile_race = (
                not remote_view_recommended
                and newly_selected_lane
                and exc.error_type == "agent_browser_error"
                and "runtimeProfile=none profile=none" in str(exc)
            )
            if startup_profile_race:
                # Current agent-browser can leave a just-created empty daemon
                # lane unprofiled before its first guarded open. Since this
                # lane was absent from the pre-launch status, it owns no
                # browser or user data and is safe to close and retry once.
                self._invoke(
                    ["--session", launch_session_name, "close"],
                    timeout=min(request.timeout, 30),
                )
                time.sleep(0.5)
                opened = self._invoke(
                    cmd,
                    timeout=max(request.timeout, (self.job_timeout_ms + 999) // 1000 + 5),
                )
            elif reconcile_late_open and exc.error_type in {
                "agent_browser_error",
                "agent_browser_timeout",
            }:
                reconciled = self._reconcile_workspace_after_failed_open(
                    request=request,
                    access_plan=access_plan,
                    selected_profile=selected_profile,
                    target_service_id=requested_target_service_id,
                    launch_session_name=launch_session_name,
                )
                if reconciled is not None:
                    return reconciled
                if re.search(
                    r"route_|display.*(?:stale|unavailable|mismatch)|no .*x11 socket",
                    str(exc),
                    re.I,
                ):
                    raise AgentBrowserRuntimeFailure("route_stale", str(exc)) from exc
                raise
            elif exc.error_type == "agent_browser_error" and re.search(
                r"route_|display.*(?:stale|unavailable|mismatch)|no .*x11 socket", str(exc), re.I
            ):
                raise AgentBrowserRuntimeFailure("route_stale", str(exc)) from exc
            else:
                raise

        visible = opened.get("operatorVisible") if isinstance(opened.get("operatorVisible"), dict) else {}
        visible_state = str(
            visible.get("state") or ("not_required" if not remote_view_recommended else "missing")
        )
        if remote_view_recommended and visible_state != "ready":
            error_type = "navigation_mismatch" if visible_state == "wrong_tab" else "route_stale"
            raise AgentBrowserRuntimeFailure(
                error_type,
                f"agent-browser remote view is not ready (operatorVisible.state={visible_state})",
                operator_url=_operator_url(opened),
            )

        observed_profile = str(
            opened.get("profileId") or visible.get("profileId") or request.profile_id
        )
        if observed_profile != request.profile_id:
            raise AgentBrowserRuntimeFailure(
                "profile_mismatch",
                f"agent-browser opened profile {observed_profile!r}, not {request.profile_id!r}",
                operator_url=_operator_url(opened),
            )
        return BrowserWorkspace(
            profile_id=observed_profile,
            browser_id=str(opened.get("browserId") or visible.get("browserId") or browser_id),
            session_name=str(opened.get("sessionName") or visible.get("sessionName") or launch_session_name),
            target_id=str(opened.get("targetId") or visible.get("targetId") or target_id),
            route_id=str(opened.get("routeId") or visible.get("routeId") or ""),
            display_allocation_id=str(
                opened.get("displayAllocationId") or visible.get("displayAllocationId") or ""
            ),
            operator_url=_operator_url(opened),
            operator_visible_state=visible_state,
        )

    def _resolve_access_plan(
        self,
        request: BrowserWorkspaceRequest,
        *,
        target_service_id: str,
        constrain_presentation: bool | None = None,
    ) -> dict[str, Any]:
        """Plan through authenticated MCP when a private capability is configured."""
        include_presentation = (
            request.constrain_presentation
            if constrain_presentation is None
            else constrain_presentation
        )
        self._profile_capability = self._read_profile_capability()
        if self._profile_capability:
            arguments: dict[str, Any] = {
                "serviceName": request.service_name,
                "agentName": request.agent_name,
                "taskName": request.task_name,
                "targetServiceIds": [target_service_id],
                "url": request.start_url,
                "runtimeProfile": request.profile_id,
                "browserBuild": request.browser_build,
            }
            if include_presentation:
                arguments.update(
                    {
                        "browserHost": request.browser_host,
                        "viewStreamProvider": request.view_provider,
                        "controlInputProvider": request.control_input_provider,
                        "displayIsolation": request.display_isolation,
                    }
                )
            return self._invoke_mcp_tool(
                "service_access_plan",
                arguments,
                timeout=min(request.timeout, 30),
            )

        access_plan_args = [
            "service", "access-plan",
            "--service-name", request.service_name,
            "--agent-name", request.agent_name,
            "--task-name", request.task_name,
            "--target-service-id", target_service_id,
            "--runtime-profile", request.profile_id,
            "--url", request.start_url,
            "--browser-build", request.browser_build,
        ]
        if include_presentation:
            access_plan_args.extend(
                [
                    "--browser-host", request.browser_host,
                    "--view-stream-provider", request.view_provider,
                    "--control-input-provider", request.control_input_provider,
                    "--display-isolation", request.display_isolation,
                ]
            )
        return self._invoke(
            access_plan_args,
            timeout=min(request.timeout, 30),
        )

    def _read_profile_capability(self) -> str:
        path = self._profile_capability_file
        if path is None:
            return ""
        failure = AgentBrowserRuntimeFailure(
            "agent_browser_error",
            "configured Agent Browser profile capability is unavailable",
            reason_code="profile_capability_unavailable",
        )
        if not path.is_absolute():
            raise failure
        flags = (
            os.O_RDONLY
            | getattr(os, "O_CLOEXEC", 0)
            | getattr(os, "O_NOFOLLOW", 0)
        )
        try:
            descriptor = os.open(path, flags)
        except OSError as exc:
            raise failure from exc
        try:
            metadata = os.fstat(descriptor)
            if (
                not stat.S_ISREG(metadata.st_mode)
                or metadata.st_uid != os.geteuid()
                or metadata.st_mode & 0o077
                or metadata.st_size > MAX_PROFILE_CAPABILITY_BYTES
            ):
                raise failure
            chunks: list[bytes] = []
            remaining = MAX_PROFILE_CAPABILITY_BYTES + 1
            while remaining:
                chunk = os.read(descriptor, remaining)
                if not chunk:
                    break
                chunks.append(chunk)
                remaining -= len(chunk)
            encoded = b"".join(chunks)
        except OSError as exc:
            raise failure from exc
        finally:
            os.close(descriptor)
        if len(encoded) > MAX_PROFILE_CAPABILITY_BYTES:
            raise failure
        try:
            capability = encoded.decode("utf-8").strip()
        except UnicodeDecodeError as exc:
            raise failure from exc
        if (
            len(capability) < 32
            or any(character.isspace() for character in capability)
        ):
            raise failure
        return capability

    def _bind_exact_cdp_session(
        self,
        *,
        browser: dict[str, Any],
        browser_id: str,
        request: BrowserWorkspaceRequest,
    ) -> str:
        """Attach a deterministic CLI lane when one owner names several browsers."""
        endpoint = str(browser.get("cdpEndpoint") or "")
        port = _loopback_cdp_port(endpoint)
        if port is None:
            raise AgentBrowserRuntimeFailure(
                "agent_browser_error",
                "ambiguous retained browser owner has no loopback CDP endpoint",
            )
        binding = hashlib.sha256(
            f"{browser_id}\n{endpoint}".encode("utf-8")
        ).hexdigest()[:16]
        session_name = f"last30days-bound-{binding}"
        attached = self._invoke(
            [
                "--session",
                session_name,
                "--runtime-profile",
                request.profile_id,
                "--cdp",
                str(port),
                "tab",
                "list",
            ],
            timeout=min(request.timeout, 30),
        )
        if not isinstance(attached.get("tabs"), list):
            raise AgentBrowserRuntimeFailure(
                "agent_browser_error",
                "exact retained browser attachment returned no tab inventory",
            )
        return session_name

    def _reconcile_workspace_after_failed_open(
        self,
        *,
        request: BrowserWorkspaceRequest,
        access_plan: dict[str, Any],
        selected_profile: str,
        target_service_id: str,
        launch_session_name: str,
    ) -> BrowserWorkspace | None:
        """Accept one late ready browser after the bounded CLI wait fails.

        A service-owned remote-view job can complete after its CLI waiter exits.
        This read-only reconciliation never relaunches or retries the request; it
        accepts only a ready browser already attached to the exact selected
        profile or the narrow retained-default alias compatibility path.
        """
        try:
            status = self._invoke(
                ["service", "status"],
                timeout=min(
                    request.timeout,
                    REMOTE_VIEW_RECONCILIATION_RESERVE_SECONDS,
                ),
            )
        except AgentBrowserRuntimeFailure:
            return None

        state = (
            status.get("service_state")
            if isinstance(status.get("service_state"), dict)
            else status
        )
        if not isinstance(state, dict):
            return None
        sessions = state.get("sessions")
        browsers = state.get("browsers")
        tabs = state.get("tabs")
        if not isinstance(sessions, dict) or not isinstance(browsers, dict):
            return None

        shared_owner = agent_browser_config.shared_profile_owner(
            access_plan,
            state,
            expected_profile_id=selected_profile,
        )
        if shared_owner:
            browser = shared_owner["browser"]
            return _browser_workspace_from_retained_owner(
                request=request,
                browser=browser,
                browser_id=shared_owner["browser_id"],
                session_name=shared_owner["session_name"],
                target_id=shared_owner["target_id"],
            )

        aliased_owner = _exact_retained_default_owner(
            session_name=request.session_name,
            selected_profile=selected_profile,
            target_service_id=target_service_id,
            sessions=sessions,
            browsers=browsers,
            tabs=tabs,
        )
        if aliased_owner:
            return _browser_workspace_from_retained_owner(
                request=request,
                browser=aliased_owner["browser"],
                browser_id=aliased_owner["browser_id"],
                session_name=aliased_owner["session_name"],
                target_id=aliased_owner["target_id"],
            )

        candidate_session_names = dict.fromkeys(
            (launch_session_name, request.session_name)
        )
        for candidate_session_name in candidate_session_names:
            session = sessions.get(candidate_session_name)
            if not isinstance(session, dict):
                continue
            observed_profile = str(session.get("profileId") or "")
            if observed_profile != selected_profile:
                continue
            for browser_id in session.get("browserIds") or ():
                browser_id = str(browser_id or "")
                browser = browsers.get(browser_id)
                if not isinstance(browser, dict) or browser.get("health") != "ready":
                    continue
                browser_profile = str(
                    browser.get("profileId") or browser.get("runtimeProfile") or ""
                )
                if browser_profile != selected_profile:
                    continue
                return _browser_workspace_from_retained_owner(
                    request=request,
                    browser=browser,
                    browser_id=browser_id,
                    session_name=candidate_session_name,
                    target_id=_select_target_id(
                        session, tabs, target_service_id
                    ),
                )
        return None

    def prepare_operator_handoff(
        self,
        workspace: BrowserWorkspace,
        request: BrowserWorkspaceRequest,
    ) -> BrowserWorkspace:
        """Expose the retained browser only after remote-control readiness proof."""
        doctor = self._invoke(
            ["doctor", "remote-view"], timeout=min(request.timeout, 30)
        )
        remote_control = (
            doctor.get("remoteControl")
            if isinstance(doctor.get("remoteControl"), dict)
            else {}
        )
        if remote_control.get("status") != "ready":
            raise AgentBrowserRuntimeFailure(
                "operator_ingress_unavailable",
                "agent-browser remote control is not ready for manual authentication",
            )

        command = [
            "--session", workspace.session_name,
            "remote-view", "open", request.start_url,
            "--browser-id", workspace.browser_id,
            "--browser-build", request.browser_build,
            "--browser-host", request.browser_host,
            "--view-stream-provider", request.view_provider,
            "--control-input-provider", request.control_input_provider,
            "--display-isolation", request.display_isolation,
            "--session-name", workspace.session_name,
            "--service-name", request.service_name,
            "--agent-name", request.agent_name,
            "--task-name", request.task_name,
            "--job-timeout-ms", str(self.job_timeout_ms),
        ]
        opened = self._invoke(
            command,
            timeout=max(request.timeout, (self.job_timeout_ms + 999) // 1000 + 5),
        )
        visible = (
            opened.get("operatorVisible")
            if isinstance(opened.get("operatorVisible"), dict)
            else {}
        )
        visible_state = str(visible.get("state") or "missing")
        operator_url = _operator_url(opened)
        parsed = urlsplit(operator_url)
        external_https = (
            parsed.scheme == "https"
            and bool(parsed.hostname)
            and parsed.hostname.casefold() not in {"localhost", "127.0.0.1", "::1"}
        )
        if visible_state != "ready" or not external_https:
            raise AgentBrowserRuntimeFailure(
                "operator_ingress_unavailable",
                "agent-browser did not provide a ready external operator handoff",
            )
        observed_profile = str(
            opened.get("profileId") or visible.get("profileId") or workspace.profile_id
        )
        if observed_profile != workspace.profile_id:
            raise AgentBrowserRuntimeFailure(
                "profile_mismatch",
                f"agent-browser opened profile {observed_profile!r}, not {workspace.profile_id!r}",
            )
        return BrowserWorkspace(
            profile_id=observed_profile,
            browser_id=str(opened.get("browserId") or visible.get("browserId") or workspace.browser_id),
            session_name=str(opened.get("sessionName") or visible.get("sessionName") or workspace.session_name),
            target_id=str(opened.get("targetId") or visible.get("targetId") or workspace.target_id),
            route_id=str(opened.get("routeId") or visible.get("routeId") or workspace.route_id),
            display_allocation_id=str(
                opened.get("displayAllocationId")
                or visible.get("displayAllocationId")
                or workspace.display_allocation_id
            ),
            operator_url=operator_url,
            operator_visible_state=visible_state,
        )

    def snapshot(self, workspace: BrowserWorkspace) -> BrowserSnapshot:
        raw = self._invoke(
            ["--session", workspace.session_name, "snapshot", "-i", "--compact"],
            timeout=min(self.timeout, 30),
        )
        refs = raw.get("refs") if isinstance(raw.get("refs"), dict) else {}
        return BrowserSnapshot(refs=refs, text=str(raw.get("snapshot") or ""))

    def snapshot_and_evaluate(
        self,
        workspace: BrowserWorkspace,
        script: str,
    ) -> tuple[BrowserSnapshot, dict[str, Any]]:
        """Run dependent read-only page reads through one daemon queue job."""
        raw = self._invoke(
            [
                "--session", workspace.session_name,
                "batch", "--dependent", "--bail", "--json",
            ],
            timeout=min(self.timeout, 30),
            input_text=json.dumps([
                ["snapshot", "-i", "--compact"],
                ["eval", script],
            ]),
        )
        results = raw.get("results") if isinstance(raw.get("results"), list) else []
        if len(results) != 2 or any(
            not isinstance(entry, dict) or entry.get("success") is not True
            for entry in results
        ):
            raise AgentBrowserRuntimeFailure(
                "agent_browser_error",
                "agent-browser dependent read batch returned an incomplete result",
            )
        snapshot_raw = results[0].get("result")
        evaluation_raw = results[1].get("result")
        snapshot_raw = snapshot_raw if isinstance(snapshot_raw, dict) else {}
        evaluation_raw = evaluation_raw if isinstance(evaluation_raw, dict) else {}
        evaluated = evaluation_raw.get("result")
        evaluated = evaluated if isinstance(evaluated, dict) else evaluation_raw
        refs = snapshot_raw.get("refs") if isinstance(snapshot_raw.get("refs"), dict) else {}
        return (
            BrowserSnapshot(refs=refs, text=str(snapshot_raw.get("snapshot") or "")),
            evaluated,
        )

    def act(self, workspace: BrowserWorkspace, action: BrowserAction) -> BrowserState:
        prefix = ["--session", workspace.session_name]
        command_timeout = min(self.timeout, 30)
        if action.operation == "wait":
            try:
                delay = max(0.0, float(action.value or "0") / 1000.0)
            except ValueError:
                delay = 0.0
            time.sleep(min(delay, 10.0))
            return BrowserState()
        if action.operation == "fill":
            args = ["fill", action.target, action.value]
        elif action.operation == "press":
            args = ["press", action.value]
        elif action.operation == "click":
            args = ["click", action.target]
        elif action.operation == "navigate":
            outer_timeout = min(self.timeout, MAX_RUN_BUDGET_SECONDS)
            if self._run_deadline is not None:
                outer_timeout = max(
                    1,
                    min(
                        outer_timeout,
                        math.ceil(self._run_deadline - time.monotonic()),
                    ),
                )
            inner_timeout_ms = min(
                self.job_timeout_ms,
                max(1_000, (outer_timeout - 5) * 1_000),
            )
            command_timeout = outer_timeout
            prefix.extend(["--job-timeout-ms", str(inner_timeout_ms)])
            args = ["open", action.value]
        elif action.operation == "new_tab":
            args = ["tab", "new", action.value]
        elif action.operation == "scroll":
            args = ["scroll", "down", action.value or "1400"]
        else:  # pragma: no cover - Literal guards production callers
            raise AgentBrowserRuntimeFailure("agent_browser_error", f"unsupported browser action: {action.operation}")
        raw = self._invoke(prefix + args, timeout=command_timeout)
        return BrowserState(url=str(raw.get("url") or ""), title=str(raw.get("title") or ""))

    def prepare_site_tab(
        self,
        workspace: BrowserWorkspace,
        hostname: str,
        *,
        consolidate: bool = False,
        require_active: bool = False,
        close_timeout: int | None = None,
        ignore_close_failures: bool = False,
    ) -> bool:
        """Select a usable site tab and optionally close same-site duplicates."""
        cache_key = (workspace.session_name, hostname)
        if (
            isinstance(self._service_tab_handle, dict)
            and _url_matches_hostname(self._service_tab_url, hostname)
        ):
            self._prepared_sites.add(cache_key)
            return True
        if cache_key in self._prepared_sites and not consolidate and not require_active:
            return True
        raw = self._invoke(
            ["--session", workspace.session_name, "tab", "list"],
            timeout=min(self.timeout, 30),
        )
        tabs = raw.get("tabs") if isinstance(raw.get("tabs"), list) else []
        matches = [
            tab for tab in tabs
            if isinstance(tab, dict) and _url_matches_hostname(str(tab.get("url") or ""), hostname)
        ]
        if not matches:
            return False
        active = next((tab for tab in matches if tab.get("active")), None)
        if require_active and active is None:
            _log(
                f"Retained {hostname} targets are inactive; "
                "opening a fresh target before page-domain evaluation"
            )
            return False
        selected = active or matches[-1]
        try:
            selected_index = int(selected.get("index"))
        except (TypeError, ValueError):
            return False
        if not selected.get("active"):
            self._invoke(
                ["--session", workspace.session_name, "tab", str(selected_index)],
                timeout=min(self.timeout, 30),
            )
        if consolidate:
            duplicate_indexes = []
            for tab in matches:
                try:
                    index = int(tab.get("index"))
                except (TypeError, ValueError):
                    continue
                if index != selected_index:
                    duplicate_indexes.append(index)
            for index in sorted(duplicate_indexes, reverse=True):
                try:
                    self._invoke(
                        ["--session", workspace.session_name, "tab", "close", str(index)],
                        timeout=min(self.timeout, close_timeout or 30),
                    )
                except AgentBrowserRuntimeFailure as exc:
                    if not ignore_close_failures:
                        raise
                    _log(
                        f"Best-effort close skipped site tab index={index}: "
                        f"{_redact(str(exc))}"
                    )
        self._prepared_sites.add(cache_key)
        return True

    def evaluate(self, workspace: BrowserWorkspace, script: str) -> dict[str, Any]:
        outer_timeout = min(self.timeout, 25)
        inner_timeout_ms = min(
            self.job_timeout_ms,
            20_000,
            max(1_000, (outer_timeout - 5) * 1_000),
        )
        raw = self._invoke(
            [
                "--session",
                workspace.session_name,
                "--job-timeout-ms",
                str(inner_timeout_ms),
                "eval",
                "--stdin",
            ],
            timeout=outer_timeout,
            input_text=script,
        )
        result = raw.get("result") if isinstance(raw.get("result"), dict) else raw
        return result if isinstance(result, dict) else {"value": result}

    def evaluate_navigation_state(
        self,
        workspace: BrowserWorkspace,
        script: str,
    ) -> dict[str, Any]:
        """Use a short page-state probe so one bounded successor remains possible."""
        outer_timeout = min(self.timeout, 12)
        inner_timeout_ms = min(
            self.job_timeout_ms,
            3_000,
            max(250, (outer_timeout - 2) * 1_000),
        )
        raw = self._invoke(
            [
                "--session",
                workspace.session_name,
                "--job-timeout-ms",
                str(inner_timeout_ms),
                "eval",
                "--stdin",
            ],
            timeout=outer_timeout,
            input_text=script,
        )
        result = raw.get("result") if isinstance(raw.get("result"), dict) else raw
        return result if isinstance(result, dict) else {"value": result}

    def operator_ingress_ready(self, operator_url: str) -> bool:
        if not operator_url:
            return False
        request = Request(operator_url, method="HEAD", headers={"User-Agent": "last30days-ingress-probe/1"})
        try:
            with urlopen(request, timeout=min(self.timeout, 5)) as response:
                return int(response.status) < 500
        except HTTPError as exc:
            return exc.code < 500
        except (OSError, URLError, ValueError):
            return False

    def _service_request_arguments(
        self,
        args: list[str],
        input_text: str | None,
    ) -> dict[str, Any] | None:
        route = self._service_request_route
        if not isinstance(route, dict) or "--session" not in args:
            return None
        session_index = args.index("--session")
        if session_index + 1 >= len(args):
            return None
        if args[session_index + 1] != route.get("sessionName"):
            return None

        tokens: list[str] = []
        job_timeout_ms = self.job_timeout_ms
        index = 0
        while index < len(args):
            token = args[index]
            if token in {"--session", "--runtime-profile", "--job-timeout-ms"}:
                if token == "--job-timeout-ms" and index + 1 < len(args):
                    try:
                        job_timeout_ms = int(args[index + 1])
                    except ValueError:
                        pass
                index += 2
                continue
            tokens.append(token)
            index += 1
        if not tokens:
            return None

        request = {
            key: value
            for key, value in route.items()
            if key not in {"action", "params", "url", "jobTimeoutMs"}
        }
        request["jobTimeoutMs"] = job_timeout_ms
        request["params"] = {}
        if tokens[:2] == ["tab", "handle-ready"] and isinstance(
            self._service_tab_handle, dict
        ):
            request.update(
                {
                    "action": "ui_action",
                    "timeoutMs": SERVICE_TAB_READY_TIMEOUT_MS,
                    "maxTextBytes": 1_024,
                    "uiAction": {
                        "maxActions": 1,
                        "steps": [
                            {
                                "type": "wait",
                                "function": "() => document.readyState !== 'loading'",
                                "timeout": SERVICE_TAB_READY_TIMEOUT_MS,
                            }
                        ],
                    },
                }
            )
        elif tokens[:2] == ["tab", "list"]:
            request["action"] = "tab_list"
        elif tokens[:2] == ["tab", "new"]:
            request["action"] = "tab_new"
            request["url"] = tokens[2] if len(tokens) > 2 else "about:blank"
        elif tokens[:2] == ["tab", "close"]:
            request["action"] = "tab_close"
            if len(tokens) > 2:
                request["params"] = {"index": int(tokens[2])}
        elif tokens[:2] == ["tab", "handle-release"] and isinstance(
            self._service_tab_handle, dict
        ):
            request["action"] = "tab_handle_release"
        elif tokens[0] == "tab" and len(tokens) > 1:
            request["action"] = "tab_switch"
            request["params"] = {"index": int(tokens[1])}
        elif tokens[:2] == ["eval", "--stdin"]:
            request.update(
                {
                    "action": "evaluate",
                    "script": input_text or "",
                    "returnByValue": True,
                    "timeoutMs": job_timeout_ms,
                    "maxReturnBytes": SERVICE_EVALUATE_MAX_RETURN_BYTES,
                }
            )
        elif tokens[0] == "open" and len(tokens) > 1:
            request["action"] = "navigate"
            request["url"] = tokens[1]
            request["params"] = {
                "url": tokens[1],
                "waitUntil": "domcontentloaded",
            }
        elif tokens[0] == "scroll":
            request["action"] = "scroll"
            request["params"] = {
                "direction": tokens[1] if len(tokens) > 1 else "down",
                "amount": float(tokens[2]) if len(tokens) > 2 else 300,
            }
        else:
            return None
        if (
            isinstance(self._service_tab_handle, dict)
            and request["action"]
            in {
                "evaluate",
                "navigate",
                "scroll",
                "tab_handle_release",
                "ui_action",
            }
        ):
            request["serviceTabHandle"] = dict(self._service_tab_handle)
        return request

    def release_workspace(self) -> None:
        """Release this client's attributed tab without closing the shared browser."""
        if not isinstance(self._service_tab_handle, dict):
            self._close_mcp_session()
            self._profile_capability = ""
            return
        route = self._service_request_route or {}
        session_name = str(route.get("sessionName") or "")
        if not session_name:
            self._close_mcp_session()
            self._profile_capability = ""
            raise AgentBrowserRuntimeFailure(
                "agent_browser_error",
                "agent-browser service tab handle has no retained session route",
            )
        try:
            self._invoke(
                ["--session", session_name, "tab", "handle-release"],
                timeout=min(self.timeout, 30),
            )
        finally:
            self._service_tab_handle = None
            self._service_tab_url = ""
            self._prepared_sites = {
                key for key in self._prepared_sites if key[0] != session_name
            }
            self._close_mcp_session()
            self._profile_capability = ""

    def _invoke_service_request(
        self,
        arguments: dict[str, Any],
        *,
        timeout: int,
    ) -> dict[str, Any]:
        return self._invoke_mcp_tool(
            "service_request",
            arguments,
            timeout=timeout,
        )

    def _invoke_mcp_tool(
        self,
        name: str,
        arguments: dict[str, Any],
        *,
        timeout: int,
    ) -> dict[str, Any]:
        self._ensure_mcp_session(timeout)
        request_id = self._mcp_request_id
        self._mcp_request_id += 1
        ephemeral_arguments = dict(arguments)
        if (
            name in {"service_access_plan", "service_request"}
            and self._profile_capability
        ):
            ephemeral_arguments["profileCapability"] = self._profile_capability
        self._write_mcp_message(
            {
                "jsonrpc": "2.0",
                "id": request_id,
                "method": "tools/call",
                "params": {"name": name, "arguments": ephemeral_arguments},
            }
        )
        response = self._wait_for_mcp_response(request_id, timeout)
        if not isinstance(response, dict) or response.get("error"):
            raise AgentBrowserRuntimeFailure(
                "agent_browser_error", "agent-browser MCP tool returned no result"
            )
        tool_result = response.get("result")
        if not isinstance(tool_result, dict):
            raise AgentBrowserRuntimeFailure(
                "agent_browser_error", "agent-browser MCP tool failed"
            )
        content = tool_result.get("content")
        text_content = next(
            (
                entry.get("text")
                for entry in content or []
                if isinstance(entry, dict) and isinstance(entry.get("text"), str)
            ),
            "",
        )
        try:
            payload = json.loads(text_content)
        except json.JSONDecodeError as exc:
            raise AgentBrowserRuntimeFailure(
                "agent_browser_error", "agent-browser MCP tool returned malformed JSON"
            ) from exc
        if not isinstance(payload, dict):
            raise AgentBrowserRuntimeFailure(
                "agent_browser_error", "agent-browser MCP tool returned malformed JSON"
            )
        if tool_result.get("isError") is True or payload.get("success") is False:
            message = _redact(
                str(payload.get("error") or "agent-browser MCP tool failed")
            )
            reason_match = re.match(r"^([a-z][a-z0-9_]{0,63})(?::|\b)", message)
            raise AgentBrowserRuntimeFailure(
                "agent_browser_error",
                message,
                reason_code=reason_match.group(1) if reason_match else "",
            )
        data = payload.get("data", payload)
        return data if isinstance(data, dict) else {"value": data}

    def _ensure_mcp_session(self, timeout: int) -> None:
        process = self._mcp_process
        if process is not None and process.poll() is None:
            return
        self._close_mcp_session()
        self._mcp_responses = queue.Queue()
        self._mcp_response_cache = {}
        self._mcp_request_id = 2
        self._mcp_stderr_lines = []
        process = subprocess.Popen(
            ["agent-browser", "mcp", "serve"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            encoding="utf-8",
            errors="replace",
        )
        self._mcp_process = process
        if process.stdin is None or process.stdout is None or process.stderr is None:
            self._close_mcp_session()
            raise AgentBrowserRuntimeFailure(
                "agent_browser_error",
                "agent-browser MCP session did not expose stdio",
            )
        threading.Thread(
            target=self._read_mcp_stdout,
            args=(process, self._mcp_responses),
            daemon=True,
            name="last30days-agent-browser-mcp-stdout",
        ).start()
        threading.Thread(
            target=self._read_mcp_stderr,
            args=(process, self._mcp_stderr_lines),
            daemon=True,
            name="last30days-agent-browser-mcp-stderr",
        ).start()
        self._write_mcp_message(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2025-03-26",
                    "capabilities": {},
                    "clientInfo": {"name": "last30days", "version": "1"},
                },
            }
        )
        initialized = self._wait_for_mcp_response(1, timeout)
        if initialized.get("error"):
            self._close_mcp_session()
            raise AgentBrowserRuntimeFailure(
                "agent_browser_error",
                "agent-browser MCP initialization failed",
            )
        self._write_mcp_message(
            {
                "jsonrpc": "2.0",
                "method": "notifications/initialized",
                "params": {},
            }
        )

    def _write_mcp_message(self, message: dict[str, Any]) -> None:
        process = self._mcp_process
        if process is None or process.stdin is None or process.poll() is not None:
            raise AgentBrowserRuntimeFailure(
                "agent_browser_error", "agent-browser MCP session is not running"
            )
        try:
            process.stdin.write(json.dumps(message, separators=(",", ":")) + "\n")
            process.stdin.flush()
        except (BrokenPipeError, OSError) as exc:
            self._close_mcp_session()
            raise AgentBrowserRuntimeFailure(
                "agent_browser_error", "agent-browser MCP session closed unexpectedly"
            ) from exc

    def _wait_for_mcp_response(
        self, request_id: int, timeout: int
    ) -> dict[str, Any]:
        cached = self._mcp_response_cache.pop(request_id, None)
        if cached is not None:
            return cached
        deadline = time.monotonic() + max(1, timeout)
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                self._close_mcp_session()
                raise subprocess.TimeoutExpired("agent-browser mcp serve", timeout)
            try:
                response = self._mcp_responses.get(timeout=remaining)
            except queue.Empty as exc:
                self._close_mcp_session()
                raise subprocess.TimeoutExpired(
                    "agent-browser mcp serve", timeout
                ) from exc
            if response.get("_mcp_eof") is True:
                message = "agent-browser MCP session exited before responding"
                if self._mcp_stderr_lines:
                    message = _redact(_cli_error_message(self._mcp_stderr_lines[-1]))
                self._close_mcp_session()
                raise AgentBrowserRuntimeFailure("agent_browser_error", message)
            response_id = response.get("id")
            if response_id == request_id:
                return response
            if isinstance(response_id, int):
                self._mcp_response_cache[response_id] = response

    def _read_mcp_stdout(
        self,
        process: subprocess.Popen[str],
        responses: queue.Queue[dict[str, Any]],
    ) -> None:
        stdout = process.stdout
        if stdout is None:
            responses.put({"_mcp_eof": True})
            return
        try:
            try:
                for line in stdout:
                    try:
                        response = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if isinstance(response, dict):
                        responses.put(response)
            except (OSError, ValueError):
                pass
        finally:
            responses.put({"_mcp_eof": True})

    def _read_mcp_stderr(
        self, process: subprocess.Popen[str], stderr_lines: list[str]
    ) -> None:
        stderr = process.stderr
        if stderr is None:
            return
        try:
            for line in stderr:
                cleaned = line.strip()
                if cleaned:
                    stderr_lines.append(cleaned)
                    del stderr_lines[:-20]
        except (OSError, ValueError):
            pass

    def _close_mcp_session(self) -> None:
        process = self._mcp_process
        self._mcp_process = None
        if process is None:
            return
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=2)
        for stream in (process.stdin, process.stdout, process.stderr):
            try:
                if stream is not None:
                    stream.close()
            except OSError:
                pass

    def _invoke(
        self,
        args: list[str],
        *,
        timeout: int,
        input_text: str | None = None,
    ) -> dict[str, Any]:
        started = time.monotonic()
        effective_timeout = timeout
        if self._run_deadline is not None:
            remaining = self._run_deadline - started
            if remaining <= 0:
                self._record_timing(args, started, "budget_exhausted")
                raise AgentBrowserRuntimeFailure(
                    "agent_browser_timeout",
                    "Agent Browser adapter run budget was exhausted",
                )
            effective_timeout = max(1, min(timeout, math.ceil(remaining)))
        command_args = list(args)
        if (
            self._requested_profile_id
            and "--session" in command_args
            and "--runtime-profile" not in command_args
        ):
            session_index = command_args.index("--session")
            command_args[session_index + 2:session_index + 2] = [
                "--runtime-profile",
                self._requested_profile_id,
            ]
        service_request = self._service_request_arguments(command_args, input_text)
        if service_request is not None:
            try:
                data = self._invoke_service_request(
                    service_request,
                    timeout=effective_timeout,
                )
            except subprocess.TimeoutExpired as exc:
                self._record_timing(args, started, "timed_out")
                raise AgentBrowserRuntimeFailure(
                    "agent_browser_timeout",
                    f"agent-browser operation timed out after {effective_timeout}s",
                ) from exc
            except OSError as exc:
                self._record_timing(args, started, "failed")
                raise AgentBrowserRuntimeFailure(
                    "agent_browser_error", _redact(str(exc))
                ) from exc
            except AgentBrowserRuntimeFailure:
                self._record_timing(args, started, "failed")
                raise
            self._record_timing(args, started, "ok")
            return data
        cmd = ["agent-browser", "--json", *command_args]
        try:
            result = subprocess.run(
                cmd,
                input=input_text,
                capture_output=True,
                text=True,
                timeout=effective_timeout,
                encoding="utf-8",
                errors="replace",
            )
        except subprocess.TimeoutExpired as exc:
            self._record_timing(args, started, "timed_out")
            raise AgentBrowserRuntimeFailure(
                "agent_browser_timeout",
                f"agent-browser operation timed out after {effective_timeout}s",
            ) from exc
        except OSError as exc:
            self._record_timing(args, started, "failed")
            raise AgentBrowserRuntimeFailure("agent_browser_error", _redact(str(exc))) from exc

        output = (result.stdout or "").strip()
        self._record_timing(args, started, "ok" if result.returncode == 0 else "failed")
        if result.returncode != 0:
            message = _redact(_cli_error_message(result.stderr or output))
            raise AgentBrowserRuntimeFailure("agent_browser_error", message)
        if not output:
            return {}
        try:
            payload = json.loads(output)
        except json.JSONDecodeError as exc:
            raise AgentBrowserRuntimeFailure("agent_browser_error", "agent-browser returned malformed JSON") from exc
        if not isinstance(payload, dict):
            raise AgentBrowserRuntimeFailure("agent_browser_error", "agent-browser returned a non-object JSON payload")
        if payload.get("success") is False:
            raise AgentBrowserRuntimeFailure(
                "agent_browser_error", _redact(str(payload.get("error") or "agent-browser command failed"))
            )
        data = payload.get("data", payload)
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                return {"value": data}
        if not isinstance(data, dict):
            return {"value": data}
        value = data.get("value")
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                pass
        if isinstance(value, dict):
            return value
        return data

    def _record_timing(self, args: list[str], started: float, status: str) -> None:
        self.command_timings.append({
            "operation": _command_operation(args),
            "duration_ms": _elapsed_ms(started),
            "status": status,
        })




def _session_has_ambiguous_browser_ownership(
    session: Any,
    expected_browser_id: str,
) -> bool:
    if not isinstance(session, dict):
        return False
    browser_ids = {
        str(browser_id or "")
        for browser_id in session.get("browserIds") or ()
        if str(browser_id or "")
    }
    return expected_browser_id in browser_ids and len(browser_ids) > 1


def _loopback_cdp_port(endpoint: str) -> int | None:
    try:
        parsed = urlsplit(endpoint)
        port = parsed.port
    except ValueError:
        return None
    if (
        parsed.scheme not in {"ws", "wss", "http", "https"}
        or parsed.hostname not in {"127.0.0.1", "localhost", "::1"}
        or port is None
        or not 1 <= port <= 65_535
    ):
        return None
    return port


def _select_target_id(
    session: dict[str, Any], tabs: Any, target_service_id: str = "facebook"
) -> str:
    tab_ids = session.get("tabIds") or []
    if not isinstance(tabs, dict):
        return ""
    for tab_id in tab_ids:
        tab = tabs.get(tab_id)
        if isinstance(tab, dict) and _is_target_service_url(
            str(tab.get("url") or ""), target_service_id
        ):
            return str(tab.get("targetId") or str(tab_id).removeprefix("target:"))
    if tab_ids:
        tab = tabs.get(tab_ids[0])
        if isinstance(tab, dict):
            return str(tab.get("targetId") or str(tab_ids[0]).removeprefix("target:"))
    return ""


def _browser_workspace_from_retained_owner(
    *,
    request: BrowserWorkspaceRequest,
    browser: dict[str, Any],
    browser_id: str,
    session_name: str,
    target_id: str,
) -> BrowserWorkspace:
    stream = _ready_operator_stream(browser, request.view_provider)
    return BrowserWorkspace(
        profile_id=request.profile_id,
        browser_id=browser_id,
        session_name=session_name,
        target_id=target_id,
        route_id=str(stream.get("id") or ""),
        operator_url=_operator_url(stream),
        operator_visible_state="ready" if stream else "not_required",
    )


def _is_target_service_url(url: str, target_service_id: str) -> bool:
    hostname = (urlsplit(url).hostname or "").lower()
    service_hosts = {
        "facebook": ("facebook.com",),
        "x": ("x.com", "twitter.com"),
        "linkedin": ("linkedin.com",),
    }
    return any(
        hostname == suffix or hostname.endswith(f".{suffix}")
        for suffix in service_hosts.get(target_service_id, ())
    )


def _exact_retained_default_owner(
    *,
    session_name: str,
    selected_profile: str,
    target_service_id: str,
    sessions: Any,
    browsers: Any,
    tabs: Any,
) -> dict[str, Any] | None:
    """Reuse a target-bearing retained session whose profile label drifted to default.

    This compatibility path is intentionally narrower than ordinary same-profile
    reuse: the configured session and selected profile must have the same name,
    the alias must point to exactly one ready browser with writable CDP, and a live
    tab for the requested service must already exist. When that browser is owned
    by a different active session, exactly one reciprocal owner is required.
    Authentication is still probed before any navigation or extraction.
    """
    if session_name != selected_profile:
        return None
    if not isinstance(sessions, dict) or not isinstance(browsers, dict):
        return None
    session = sessions.get(session_name)
    if not isinstance(session, dict) or str(session.get("profileId") or "") != "default":
        return None
    browser_ids = session.get("browserIds")
    if not isinstance(browser_ids, list) or len(browser_ids) != 1:
        return None
    browser_id = str(browser_ids[0] or "")
    if not browser_id:
        return None
    browser = browsers.get(browser_id)
    if (
        not isinstance(browser, dict)
        or browser.get("health") != "ready"
        or str(browser.get("profileId") or browser.get("runtimeProfile") or "")
        != "default"
    ):
        return None
    canonical_browser_id = f"session:{session_name}"
    active_sessions = browser.get("activeSessionIds")
    owner_session_name = ""
    if isinstance(active_sessions, list):
        reciprocal_owners = []
        for active_session_name in active_sessions:
            active_session_name = str(active_session_name or "")
            active_session = sessions.get(active_session_name)
            if (
                active_session_name
                and isinstance(active_session, dict)
                and browser_id in (active_session.get("browserIds") or ())
            ):
                reciprocal_owners.append(active_session_name)
        if len(reciprocal_owners) != 1:
            return None
        owner_session_name = reciprocal_owners[0]
    elif browser_id == canonical_browser_id:
        owner_session_name = session_name
    else:
        return None
    has_ready_cdp = bool(str(browser.get("cdpEndpoint") or "").strip()) or any(
        isinstance(stream, dict)
        and stream.get("provider") == "cdp_screencast"
        and isinstance(stream.get("readiness"), dict)
        and stream["readiness"].get("state") == "ready"
        for stream in browser.get("viewStreams") or ()
    )
    if not has_ready_cdp:
        return None
    owner_session = sessions.get(owner_session_name)
    target_id = _select_target_id(session, tabs, target_service_id)
    if not target_id and isinstance(owner_session, dict):
        target_id = _select_target_id(owner_session, tabs, target_service_id)
    if not target_id:
        return None
    return {
        "browser": browser,
        "browser_id": browser_id,
        "session_name": owner_session_name,
        "target_id": target_id,
    }


def _url_matches_hostname(url: str, hostname: str) -> bool:
    try:
        observed = (urlsplit(url).hostname or "").lower()
    except ValueError:
        return False
    expected = hostname.lower().lstrip(".")
    return observed == expected or observed.endswith(f".{expected}")


def _ready_operator_stream(browser: dict[str, Any], provider: str) -> dict[str, Any]:
    for stream in browser.get("viewStreams") or []:
        readiness = stream.get("readiness") if isinstance(stream, dict) else None
        if (
            isinstance(stream, dict)
            and stream.get("provider") == provider
            and isinstance(readiness, dict)
            and readiness.get("state") == "ready"
        ):
            return stream
    return {}


def _has_ready_operator_stream(browser: dict[str, Any], provider: str) -> bool:
    return bool(_ready_operator_stream(browser, provider))


def _select_live_route_entry(state: Any, request: BrowserWorkspaceRequest) -> str:
    route_pool = state.get("routePool") if isinstance(state, dict) else None
    if not isinstance(route_pool, dict):
        return ""
    candidates: list[tuple[str, dict[str, Any]]] = []
    for entry_id, entry in route_pool.items():
        readiness = entry.get("readiness") if isinstance(entry, dict) else None
        if not isinstance(entry, dict) or not isinstance(readiness, dict):
            continue
        if readiness.get("state") != "ready":
            continue
        candidates.append((str(entry_id), entry))
    for entry_id, entry in candidates:
        if request.route_pool_entry_id_hint and entry_id == request.route_pool_entry_id_hint:
            return entry_id
        if request.route_id_hint and str(entry.get("routeId") or "") == request.route_id_hint:
            return entry_id
    for entry_id, entry in candidates:
        if entry.get("state") == "available":
            return entry_id
    # A ready route can still be checked out by another browser. Omitting the
    # hint lets agent-browser allocate or report capacity truthfully; passing a
    # checked-out route causes an owner-mismatch failure.
    return ""


def _profile_scoped_session_name(
    sessions: Any,
    requested_name: str,
    selected_profile: str,
) -> str:
    """Choose a deterministic free session lane without closing another profile."""
    existing = sessions if isinstance(sessions, dict) else {}
    stem = f"{requested_name}--{selected_profile}"
    for sequence in range(1, 101):
        candidate = stem if sequence == 1 else f"{stem}--{sequence}"
        session = existing.get(candidate)
        if not isinstance(session, dict):
            return candidate
        observed_profile = str(session.get("profileId") or "")
        if observed_profile == selected_profile:
            return candidate
    raise AgentBrowserRuntimeFailure(
        "agent_browser_error",
        f"no free agent-browser session lane for profile {selected_profile!r}",
    )


def _operator_url(payload: dict[str, Any]) -> str:
    descriptor = payload.get("routeDescriptor") if isinstance(payload.get("routeDescriptor"), dict) else {}
    visible = payload.get("operatorVisible") if isinstance(payload.get("operatorVisible"), dict) else {}
    return str(
        payload.get("publicOperatorUrl")
        or descriptor.get("publicOperatorUrl")
        or payload.get("externalUrl")
        or descriptor.get("externalUrl")
        or visible.get("publicOperatorUrl")
        or visible.get("externalUrl")
        or ""
    )


def _redact(value: str) -> str:
    redacted = value
    for key in (
        "c_user",
        "xs",
        "cookie",
        "authorization",
        "profilecapability",
        "capability",
        "token",
        "password",
    ):
        redacted = re.sub(
            rf"(?i)({re.escape(key)}\s*[:=]\s*)[^\s,;}}]+", r"\1[REDACTED]", redacted
        )
    return redacted


def _cli_error_message(value: str) -> str:
    text = (value or "agent-browser command failed").strip()
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return text
    if isinstance(payload, dict):
        return str(payload.get("error") or payload.get("message") or "agent-browser command failed")
    return text


def _elapsed_ms(started: float) -> int:
    return max(0, round((time.monotonic() - started) * 1000))


def _is_navigation_timeout(exc: AgentBrowserRuntimeFailure) -> bool:
    if exc.error_type == "agent_browser_timeout":
        return True
    if exc.error_type != "agent_browser_error":
        return False
    message = str(exc).casefold()
    return "timed out" in message or "timeout" in message or "timed_out" in message


def _command_operation(args: list[str]) -> str:
    for token in ("service", "remote-view", "snapshot", "eval", "open", "fill", "press", "click", "wait", "tab", "scroll"):
        if token in args:
            return token
    return "unknown"


def _log(msg: str) -> None:
    log.source_log("Agent Browser", msg, tty_only=False)


def is_agent_browser_available() -> bool:
    return shutil.which("agent-browser") is not None


def config_flag(value: object) -> bool:
    """Parse an opt-in boolean config value without truthifying arbitrary text."""
    if isinstance(value, bool):
        return value
    return str(value or "").strip().casefold() in {"1", "true", "yes", "on"}
