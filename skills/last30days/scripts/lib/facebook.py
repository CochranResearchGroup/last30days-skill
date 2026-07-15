"""Quality-gated Facebook search through a retained agent-browser workspace.

Facebook credentials remain in the operator-managed browser profile. This
module owns workspace verification, navigation, extraction, and post quality;
it never reads or returns browser cookie values or raw page HTML.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import time
from typing import Any, Literal, Protocol
from urllib.parse import parse_qs, quote_plus, unquote, urlencode, urlsplit, urlunsplit
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from . import dates, log
from .relevance import token_overlap_relevance as _compute_relevance


DEPTH_CONFIG = {
    "quick": {"results": 8, "scrolls": 1, "timeout": 45},
    "default": {"results": 16, "scrolls": 2, "timeout": 75},
    "deep": {"results": 30, "scrolls": 4, "timeout": 120},
}

ERROR_TYPES = {
    "agent_browser_missing",
    "profile_mismatch",
    "route_stale",
    "auth_required",
    "checkpoint_required",
    "operator_ingress_unavailable",
    "navigation_mismatch",
    "search_unavailable",
    "extraction_empty",
    "quality_gate_failed",
    "agent_browser_timeout",
    "agent_browser_error",
}

AUTH_SCRIPT = r"""
(() => {
  const body = (document.body?.innerText || "").slice(0, 12000);
  const cookieNames = new Set(document.cookie.split(";").map((part) => part.split("=", 1)[0].trim()));
  const loginForm = Boolean(document.querySelector('input[name="email"], input[name="pass"], form[action*="login"]'));
  const search = document.querySelector('[aria-label="Search Facebook"], input[placeholder="Search Facebook"]');
  const checkpoint = /checkpoint|security check|confirm your identity|two-factor authentication/i.test(`${location.href}\n${body}`);
  return {
    url: location.href,
    title: document.title,
    login_form: loginForm,
    checkpoint,
    authenticated_dom: Boolean(search) && !loginForm && !checkpoint,
    has_c_user: cookieNames.has("c_user"),
    has_xs: cookieNames.has("xs")
  };
})()
"""

PAGE_STATE_SCRIPT = r"""
(() => {
  const clean = (value) => String(value || "").replace(/\s+/g, " ").trim();
  const body = clean(document.body?.innerText || "").slice(0, 20000);
  const search = document.querySelector('[aria-label="Search Facebook"], input[placeholder="Search Facebook"]');
  const heading = Array.from(document.querySelectorAll('h1, h2, [role="heading"]'))
    .map((node) => clean(node.innerText || node.textContent))
    .find((text) => /search|result/i.test(text)) || "";
  const filterText = Array.from(document.querySelectorAll('[role="tab"], [role="button"], a'))
    .map((node) => clean(node.innerText || node.textContent)).join(" ");
  return {
    url: location.href,
    title: document.title,
    heading,
    query_value: clean(search?.value || search?.textContent || ""),
    has_search_filters: /posts|recent posts|people|groups|pages/i.test(filterText),
    no_results: /no results|we didn't find|couldn't find|try different keywords/i.test(body),
    login_page: Boolean(document.querySelector('input[name="email"], input[name="pass"], form[action*="login"]')),
    checkpoint: /checkpoint|security check|confirm your identity|two-factor authentication/i.test(`${location.href} ${body}`),
    error_page: /something went wrong|this content isn't available|temporarily unavailable/i.test(body)
  };
})()
"""

EXTRACT_SCRIPT = r"""
(() => {
  const clean = (value) => String(value || "").replace(/[ \t]+/g, " ").trim();
  const main = document.querySelector('[role="main"]') || document.querySelector('main');
  if (!main) return {url: location.href, title: document.title, candidates: []};
  const nodes = Array.from(main.querySelectorAll('[role="article"], div[aria-posinset]'));
  const candidates = [];
  const seen = new Set();
  const count = (text, label) => {
    const match = clean(text).match(new RegExp(`(\\d+(?:[,.]\\d+)?\\s*[KkMm]?)\\s+${label}`, "i"));
    if (!match) return 0;
    const raw = match[1].replace(/,/g, "").toLowerCase();
    const value = Number.parseFloat(raw);
    if (!Number.isFinite(value)) return 0;
    return Math.round(value * (raw.endsWith("k") ? 1000 : raw.endsWith("m") ? 1000000 : 1));
  };
  for (const node of nodes) {
    const text = (node.innerText || node.textContent || "").trim();
    if (!text) continue;
    const anchors = Array.from(node.querySelectorAll('a[href]'));
    const permalink = anchors.find((a) => /\/posts\/|\/permalink(?:\.php|\/)|story_fbid=|\/groups\/[^/]+\/posts\//.test(a.href || ""));
    const timestamp = anchors.find((a) => a.querySelector('abbr, time') || a.getAttribute('aria-label') || a.getAttribute('data-utime'));
    const authorNode = node.querySelector('h2 a, h3 a, strong a, a[role="link"]');
    const timestampNode = timestamp?.querySelector('abbr, time') || timestamp;
    const url = permalink?.href || "";
    const key = `${url}|${text.slice(0, 240)}`;
    if (seen.has(key)) continue;
    seen.add(key);
    candidates.push({
      text,
      url,
      author: clean(authorNode?.innerText || authorNode?.textContent || ""),
      timestamp: clean(
        timestampNode?.getAttribute?.("datetime") ||
        timestampNode?.getAttribute?.("data-utime") ||
        timestampNode?.getAttribute?.("aria-label") ||
        timestampNode?.getAttribute?.("title") ||
        timestampNode?.innerText || timestampNode?.textContent || ""
      ),
      is_comment: Boolean(node.parentElement?.closest?.('[role="article"]')),
      sponsored: /(^|\n)\s*(sponsored|paid partnership)\s*($|\n)/i.test(text),
      engagement: {
        likes: count(text, "likes?"),
        comments: count(text, "comments?"),
        shares: count(text, "shares?")
      }
    });
  }
  return {url: location.href, title: document.title, candidates};
})()
"""


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
class FacebookAuthState:
    authenticated: bool
    login_form: bool = False
    checkpoint: bool = False
    has_c_user: bool = False
    has_xs: bool = False
    url: str = ""


@dataclass(frozen=True)
class BrowserSnapshot:
    refs: dict[str, dict[str, Any]] = field(default_factory=dict)
    text: str = ""


@dataclass(frozen=True)
class BrowserAction:
    operation: Literal["fill", "press", "click", "wait", "new_tab", "scroll"]
    target: str = ""
    value: str = ""


@dataclass(frozen=True)
class BrowserState:
    url: str = ""
    title: str = ""


@dataclass(frozen=True)
class FacebookPageState:
    url: str
    title: str
    heading: str = ""
    query_value: str = ""
    has_search_filters: bool = False
    no_results: bool = False
    login_page: bool = False
    checkpoint: bool = False
    error_page: bool = False


@dataclass
class FacebookCandidate:
    kind: Literal["post", "page", "group", "ad", "story", "recommendation", "unknown"]
    text: str
    author: str | None
    canonical_url: str | None
    published_at: str | None
    date_confidence: Literal["high", "med", "low"]
    engagement: dict[str, int]
    sponsored: bool
    rejection_reasons: list[str] = field(default_factory=list)


@dataclass
class FacebookRunDiagnostics:
    candidate_counts: Counter[str] = field(default_factory=Counter)
    rejection_counts: Counter[str] = field(default_factory=Counter)
    accepted_count: int = 0
    duration_ms: int = 0

    def as_dict(self) -> dict[str, Any]:
        return {
            "candidate_counts": dict(self.candidate_counts),
            "rejection_counts": dict(self.rejection_counts),
            "accepted_count": self.accepted_count,
            "duration_ms": self.duration_ms,
        }


class FacebookScraperFailure(RuntimeError):
    def __init__(self, error_type: str, message: str, *, operator_url: str = "") -> None:
        if error_type not in ERROR_TYPES:
            error_type = "agent_browser_error"
        super().__init__(message)
        self.error_type = error_type
        self.operator_url = operator_url


class AgentBrowserClient(Protocol):
    def acquire_workspace(self, request: BrowserWorkspaceRequest) -> BrowserWorkspace: ...
    def inspect_auth(self, workspace: BrowserWorkspace) -> FacebookAuthState: ...
    def snapshot(self, workspace: BrowserWorkspace) -> BrowserSnapshot: ...
    def act(self, workspace: BrowserWorkspace, action: BrowserAction) -> BrowserState: ...
    def evaluate(self, workspace: BrowserWorkspace, script: str) -> dict[str, Any]: ...


class CliAgentBrowserClient:
    """Typed adapter for the installed agent-browser JSON CLI."""

    def __init__(self, *, timeout: int) -> None:
        self.timeout = timeout
        self.command_timings: list[dict[str, Any]] = []

    def acquire_workspace(self, request: BrowserWorkspaceRequest) -> BrowserWorkspace:
        status = self._invoke(["service", "status"], timeout=min(request.timeout, 30))
        state = status.get("service_state") if isinstance(status.get("service_state"), dict) else status
        sessions = state.get("sessions") if isinstance(state, dict) else {}
        browsers = state.get("browsers") if isinstance(state, dict) else {}
        tabs = state.get("tabs") if isinstance(state, dict) else {}
        session = sessions.get(request.session_name) if isinstance(sessions, dict) else None
        browser: dict[str, Any] | None = None
        browser_id = ""
        target_id = ""

        if isinstance(session, dict):
            observed_profile = str(session.get("profileId") or "")
            if observed_profile and observed_profile != request.profile_id:
                raise FacebookScraperFailure(
                    "profile_mismatch",
                    f"agent-browser session {request.session_name!r} uses profile {observed_profile!r}, not {request.profile_id!r}",
                )
            browser_ids = session.get("browserIds") or []
            if browser_ids:
                browser_id = str(browser_ids[0])
                candidate = browsers.get(browser_id) if isinstance(browsers, dict) else None
                if isinstance(candidate, dict) and candidate.get("health") == "ready":
                    browser = candidate
                    target_id = _select_target_id(session, tabs)

        if browser and _has_ready_operator_stream(browser, request.view_provider):
            stream = _ready_operator_stream(browser, request.view_provider)
            return BrowserWorkspace(
                profile_id=request.profile_id,
                browser_id=browser_id,
                session_name=request.session_name,
                target_id=target_id,
                route_id=str(stream.get("id") or ""),
                operator_url=str(stream.get("externalUrl") or stream.get("url") or ""),
                operator_visible_state="ready",
            )

        cmd = [
            "--session", request.session_name,
            "remote-view", "open", "https://www.facebook.com/",
            "--browser-build", request.browser_build,
            "--view-stream-provider", request.view_provider,
            "--session-name", request.session_name,
            "--service-name", "last30days",
            "--agent-name", "facebook-scraper",
            "--task-name", "facebook-search",
        ]
        if browser:
            cmd.extend(["--browser-id", browser_id])
        else:
            cmd.extend(["--runtime-profile", request.profile_id])

        route_entry = _select_live_route_entry(state, request)
        if route_entry:
            cmd.extend(["--route-pool-entry-id", route_entry])

        try:
            opened = self._invoke(cmd, timeout=request.timeout)
        except FacebookScraperFailure as exc:
            if exc.error_type == "agent_browser_error" and re.search(
                r"route_|display.*(?:stale|unavailable|mismatch)|no .*x11 socket", str(exc), re.I
            ):
                raise FacebookScraperFailure("route_stale", str(exc)) from exc
            raise

        visible = opened.get("operatorVisible") if isinstance(opened.get("operatorVisible"), dict) else {}
        visible_state = str(visible.get("state") or "missing")
        if visible_state != "ready":
            error_type = "navigation_mismatch" if visible_state == "wrong_tab" else "route_stale"
            raise FacebookScraperFailure(
                error_type,
                f"agent-browser remote view is not ready (operatorVisible.state={visible_state})",
                operator_url=_operator_url(opened),
            )

        observed_profile = str(
            opened.get("profileId") or visible.get("profileId") or request.profile_id
        )
        if observed_profile != request.profile_id:
            raise FacebookScraperFailure(
                "profile_mismatch",
                f"agent-browser opened profile {observed_profile!r}, not {request.profile_id!r}",
                operator_url=_operator_url(opened),
            )
        return BrowserWorkspace(
            profile_id=observed_profile,
            browser_id=str(opened.get("browserId") or visible.get("browserId") or browser_id),
            session_name=str(opened.get("sessionName") or visible.get("sessionName") or request.session_name),
            target_id=str(opened.get("targetId") or visible.get("targetId") or target_id),
            route_id=str(opened.get("routeId") or visible.get("routeId") or ""),
            display_allocation_id=str(
                opened.get("displayAllocationId") or visible.get("displayAllocationId") or ""
            ),
            operator_url=_operator_url(opened),
            operator_visible_state=visible_state,
        )

    def inspect_auth(self, workspace: BrowserWorkspace) -> FacebookAuthState:
        raw = self.evaluate(workspace, AUTH_SCRIPT)
        return FacebookAuthState(
            authenticated=bool(raw.get("authenticated_dom")),
            login_form=bool(raw.get("login_form")),
            checkpoint=bool(raw.get("checkpoint")),
            has_c_user=bool(raw.get("has_c_user")),
            has_xs=bool(raw.get("has_xs")),
            url=str(raw.get("url") or ""),
        )

    def snapshot(self, workspace: BrowserWorkspace) -> BrowserSnapshot:
        raw = self._invoke(
            ["--session", workspace.session_name, "snapshot", "-i", "--compact"],
            timeout=min(self.timeout, 30),
        )
        refs = raw.get("refs") if isinstance(raw.get("refs"), dict) else {}
        return BrowserSnapshot(refs=refs, text=str(raw.get("snapshot") or ""))

    def act(self, workspace: BrowserWorkspace, action: BrowserAction) -> BrowserState:
        prefix = ["--session", workspace.session_name]
        if action.operation == "fill":
            args = ["fill", action.target, action.value]
        elif action.operation == "press":
            args = ["press", action.value]
        elif action.operation == "click":
            args = ["click", action.target]
        elif action.operation == "wait":
            args = ["wait", action.value]
        elif action.operation == "new_tab":
            args = ["tab", "new", action.value]
        elif action.operation == "scroll":
            args = ["scroll", "down", action.value or "1400"]
        else:  # pragma: no cover - Literal guards production callers
            raise FacebookScraperFailure("agent_browser_error", f"unsupported browser action: {action.operation}")
        raw = self._invoke(prefix + args, timeout=min(self.timeout, 30))
        return BrowserState(url=str(raw.get("url") or ""), title=str(raw.get("title") or ""))

    def evaluate(self, workspace: BrowserWorkspace, script: str) -> dict[str, Any]:
        raw = self._invoke(
            ["--session", workspace.session_name, "eval", "--stdin"],
            timeout=min(self.timeout, 30),
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

    def _invoke(
        self,
        args: list[str],
        *,
        timeout: int,
        input_text: str | None = None,
    ) -> dict[str, Any]:
        cmd = ["agent-browser", "--json", *args]
        started = time.monotonic()
        try:
            result = subprocess.run(
                cmd,
                input=input_text,
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding="utf-8",
                errors="replace",
            )
        except subprocess.TimeoutExpired as exc:
            self._record_timing(args, started, "timed_out")
            raise FacebookScraperFailure(
                "agent_browser_timeout", f"agent-browser operation timed out after {timeout}s"
            ) from exc
        except OSError as exc:
            self._record_timing(args, started, "failed")
            raise FacebookScraperFailure("agent_browser_error", _redact(str(exc))) from exc

        output = (result.stdout or "").strip()
        self._record_timing(args, started, "ok" if result.returncode == 0 else "failed")
        if result.returncode != 0:
            message = _redact(_cli_error_message(result.stderr or output))
            raise FacebookScraperFailure("agent_browser_error", message)
        if not output:
            return {}
        try:
            payload = json.loads(output)
        except json.JSONDecodeError as exc:
            raise FacebookScraperFailure("agent_browser_error", "agent-browser returned malformed JSON") from exc
        if not isinstance(payload, dict):
            raise FacebookScraperFailure("agent_browser_error", "agent-browser returned a non-object JSON payload")
        if payload.get("success") is False:
            raise FacebookScraperFailure(
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


class FacebookScraper:
    def __init__(
        self,
        client: AgentBrowserClient,
        request: BrowserWorkspaceRequest,
        *,
        limit: int,
        scrolls: int,
        initial_wait: float,
        scroll_wait: float,
        now: datetime | None = None,
        debug_dir: str = "",
    ) -> None:
        self.client = client
        self.request = request
        self.limit = limit
        self.scrolls = scrolls
        self.initial_wait = initial_wait
        self.scroll_wait = scroll_wait
        self.now = now or datetime.now(timezone.utc)
        self.debug_dir = debug_dir
        self._topic = ""

    def search(self, topic: str, from_date: str, to_date: str) -> dict[str, Any]:
        started = time.monotonic()
        self._topic = topic
        diagnostics = FacebookRunDiagnostics()
        workspace: BrowserWorkspace | None = None
        page = FacebookPageState(url="", title="")
        try:
            _log(f"Acquiring agent-browser workspace profile={self.request.profile_id!r}")
            workspace = self.client.acquire_workspace(self.request)
            _log(
                "Workspace acquired "
                f"profile={workspace.profile_id!r} browser={workspace.browser_id!r} "
                f"operator_visible={workspace.operator_visible_state}"
            )
            auth = self.client.inspect_auth(workspace)
            _log(
                "Authentication inspected "
                f"authenticated={auth.authenticated} login_form={auth.login_form} checkpoint={auth.checkpoint}"
            )
            if auth.checkpoint:
                raise FacebookScraperFailure(
                    "checkpoint_required",
                    "Facebook requires an operator checkpoint",
                    operator_url=workspace.operator_url,
                )
            if not auth.authenticated:
                ingress_probe = getattr(self.client, "operator_ingress_ready", None)
                if callable(ingress_probe) and not ingress_probe(workspace.operator_url):
                    raise FacebookScraperFailure(
                        "operator_ingress_unavailable",
                        "Facebook operator handoff URL is unavailable",
                    )
                raise FacebookScraperFailure(
                    "auth_required",
                    "Facebook authentication is required in the retained agent-browser profile",
                    operator_url=workspace.operator_url,
                )

            page = self._navigate(workspace, topic)
            if page.no_results:
                diagnostics.duration_ms = _elapsed_ms(started)
                return self._result([], None, None, workspace, page, diagnostics, from_date, to_date)

            if self.initial_wait:
                time.sleep(self.initial_wait)
            raw_candidates = self._extract(workspace)
            for _ in range(max(0, self.scrolls)):
                if len(raw_candidates) >= self.limit:
                    break
                self.client.act(workspace, BrowserAction("scroll", value="1400"))
                if self.scroll_wait:
                    time.sleep(self.scroll_wait)
                raw_candidates.extend(self._extract(workspace))

            if not raw_candidates:
                raise FacebookScraperFailure(
                    "extraction_empty", "Verified Facebook search page contained no candidate cards"
                )
            items = self._quality_gate(raw_candidates, topic, from_date, to_date, diagnostics)
            diagnostics.duration_ms = _elapsed_ms(started)
            _log(
                f"Candidates={dict(diagnostics.candidate_counts)} "
                f"rejections={dict(diagnostics.rejection_counts)} accepted={len(items)} "
                f"duration_ms={diagnostics.duration_ms}"
            )
            if not items:
                return self._result(
                    [],
                    "quality_gate_failed",
                    "Facebook candidates were found, but none passed the post quality gate",
                    workspace,
                    page,
                    diagnostics,
                    from_date,
                    to_date,
                )
            return self._result(items, None, None, workspace, page, diagnostics, from_date, to_date)
        except FacebookScraperFailure as exc:
            diagnostics.duration_ms = _elapsed_ms(started)
            _log(f"Failed stage error_type={exc.error_type} message={exc}")
            return self._result(
                [], exc.error_type, str(exc), workspace, page, diagnostics, from_date, to_date,
                operator_url=exc.operator_url,
            )

    def _navigate(self, workspace: BrowserWorkspace, topic: str) -> FacebookPageState:
        search_url = _search_url(topic)
        snapshot = self.client.snapshot(workspace)
        search_ref = _find_ref(snapshot, role={"combobox", "textbox"}, name="Search Facebook")
        strategy = "search_control" if search_ref else "new_tab"
        _log(f"Navigating query={topic!r} strategy={strategy}")
        if search_ref:
            self.client.act(workspace, BrowserAction("fill", target=search_ref, value=topic))
            self.client.act(workspace, BrowserAction("press", value="Enter"))
        else:
            self.client.act(workspace, BrowserAction("new_tab", value=search_url))
        self.client.act(workspace, BrowserAction("wait", value="2000"))
        page = _page_state(self.client.evaluate(workspace, PAGE_STATE_SCRIPT))

        if not _page_matches_query(page, topic) and search_ref:
            _log(f"Search-control navigation mismatch final_url={page.url!r}; retrying with new tab")
            self.client.act(workspace, BrowserAction("new_tab", value=search_url))
            self.client.act(workspace, BrowserAction("wait", value="2000"))
            page = _page_state(self.client.evaluate(workspace, PAGE_STATE_SCRIPT))

        _log(f"Navigation readback requested={search_url!r} final={page.url!r}")
        if page.checkpoint:
            raise FacebookScraperFailure(
                "checkpoint_required", "Facebook checkpoint appeared during search navigation",
                operator_url=workspace.operator_url,
            )
        if page.login_page:
            raise FacebookScraperFailure(
                "auth_required", "Facebook session became logged out during search navigation",
                operator_url=workspace.operator_url,
            )
        if page.error_page:
            raise FacebookScraperFailure("search_unavailable", "Facebook returned an error page")
        if not _page_matches_query(page, topic):
            raise FacebookScraperFailure(
                "navigation_mismatch",
                f"Facebook final page does not match requested query {topic!r}: {page.url}",
            )

        refreshed = self.client.snapshot(workspace)
        recent_ref = _find_ref(refreshed, role={"button", "link", "tab"}, name="Recent posts")
        if recent_ref:
            self.client.act(workspace, BrowserAction("click", target=recent_ref))
            self.client.act(workspace, BrowserAction("wait", value="1000"))
            filtered = _page_state(self.client.evaluate(workspace, PAGE_STATE_SCRIPT))
            if _page_matches_query(filtered, topic):
                page = filtered
        return page

    def _extract(self, workspace: BrowserWorkspace) -> list[dict[str, Any]]:
        raw = self.client.evaluate(workspace, EXTRACT_SCRIPT)
        candidates = raw.get("candidates") or []
        return [candidate for candidate in candidates if isinstance(candidate, dict)]

    def _quality_gate(
        self,
        raw_candidates: list[dict[str, Any]],
        topic: str,
        from_date: str,
        to_date: str,
        diagnostics: FacebookRunDiagnostics,
    ) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        seen: set[str] = set()
        for raw in raw_candidates:
            candidate = _candidate_from_raw(raw, self.now)
            diagnostics.candidate_counts[candidate.kind] += 1
            _validate_candidate(candidate, topic, from_date, to_date)
            if candidate.rejection_reasons:
                diagnostics.candidate_counts["rejected"] += 1
                diagnostics.rejection_counts.update(candidate.rejection_reasons)
                continue
            digest = hashlib.sha1(
                f"{candidate.canonical_url}\n{candidate.text[:300]}".encode("utf-8")
            ).hexdigest()[:16]
            if digest in seen:
                diagnostics.rejection_counts["duplicate"] += 1
                continue
            seen.add(digest)
            relevance = _compute_relevance(topic, candidate.text)
            items.append({
                "id": f"FB{digest}",
                "text": candidate.text,
                "url": candidate.canonical_url,
                "author": candidate.author,
                "date": candidate.published_at,
                "engagement": candidate.engagement,
                "relevance": round(relevance, 2),
                "why_relevant": f"Facebook post: {candidate.text[:80]}",
                "metadata": {
                    "extraction": "agent-browser-dom-v2",
                    "remote_browser": True,
                    "date_confidence": candidate.date_confidence,
                },
            })
            if len(items) >= self.limit:
                break
        diagnostics.accepted_count = len(items)
        return items

    def _result(
        self,
        items: list[dict[str, Any]],
        error_type: str | None,
        error: str | None,
        workspace: BrowserWorkspace | None,
        page: FacebookPageState,
        diagnostics: FacebookRunDiagnostics,
        from_date: str,
        to_date: str,
        *,
        operator_url: str = "",
    ) -> dict[str, Any]:
        workspace_data: dict[str, str] = {}
        if workspace:
            workspace_data = {
                "browser_id": workspace.browser_id,
                "target_id": workspace.target_id,
                "route_id": workspace.route_id,
            }
        result: dict[str, Any] = {
            "items": items,
            "error": error,
            "error_type": error_type,
            "url": page.url,
            "title": page.title,
            "profile": self.request.profile_id,
            "session": self.request.session_name,
            "workspace": workspace_data,
            "diagnostics": diagnostics.as_dict(),
            "from_date": from_date,
            "to_date": to_date,
        }
        handoff = operator_url or (workspace.operator_url if workspace else "")
        if handoff and error_type in {"auth_required", "checkpoint_required"}:
            result["operator_url"] = handoff
        self._write_debug_artifact(result, page)
        return result

    def _write_debug_artifact(self, result: dict[str, Any], page: FacebookPageState) -> None:
        if not self.debug_dir:
            return
        artifact = {
            "query": self._topic,
            "requested_url": _search_url(self._topic),
            "final_url": page.url,
            "profile": self.request.profile_id,
            "session": self.request.session_name,
            "workspace": result.get("workspace") or {},
            "error_type": result.get("error_type"),
            "page_assertions": {
                "query_matches": _page_matches_query(page, self._topic) if page.url else False,
                "has_search_filters": page.has_search_filters,
                "no_results": page.no_results,
                "login_page": page.login_page,
                "checkpoint": page.checkpoint,
                "error_page": page.error_page,
            },
            "diagnostics": result.get("diagnostics") or {},
            "accepted_items": [
                {"id": item.get("id"), "date": item.get("date"), "text_chars": len(str(item.get("text") or ""))}
                for item in result.get("items") or []
            ],
            "command_timings": list(getattr(self.client, "command_timings", [])),
        }
        try:
            directory = Path(self.debug_dir).expanduser()
            directory.mkdir(parents=True, exist_ok=True)
            digest = hashlib.sha1(self._topic.encode("utf-8")).hexdigest()[:10]
            destination = directory / f"facebook-{self.now.strftime('%Y%m%dT%H%M%SZ')}-{digest}.json"
            destination.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        except OSError as exc:
            _log(f"Could not write sanitized Facebook debug artifact: {_redact(str(exc))}")


def _log(msg: str) -> None:
    log.source_log("Facebook", msg, tty_only=False)


def is_agent_browser_available() -> bool:
    return shutil.which("agent-browser") is not None


def search_facebook(
    topic: str,
    from_date: str,
    to_date: str,
    *,
    depth: str = "default",
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Search Facebook and return only verified, quality-gated post items."""
    config = config or {}
    if not is_agent_browser_available():
        return {
            "items": [],
            "error": "agent-browser command is not on PATH",
            "error_type": "agent_browser_missing",
        }
    settings = DEPTH_CONFIG.get(depth, DEPTH_CONFIG["default"])
    timeout = int(config.get("LAST30DAYS_FACEBOOK_TIMEOUT") or settings["timeout"])
    request = BrowserWorkspaceRequest(
        profile_id=str(config.get("LAST30DAYS_FACEBOOK_PROFILE") or "last30days-facebook"),
        session_name=str(config.get("LAST30DAYS_FACEBOOK_SESSION") or "last30days-facebook"),
        browser_build=str(config.get("LAST30DAYS_FACEBOOK_BROWSER_BUILD") or "stealthcdp_chromium"),
        view_provider=str(config.get("LAST30DAYS_FACEBOOK_VIEW_PROVIDER") or "rdp_gateway"),
        timeout=timeout,
        browser_id_hint=str(config.get("LAST30DAYS_FACEBOOK_BROWSER_ID") or "").strip(),
        route_id_hint=str(config.get("LAST30DAYS_FACEBOOK_ROUTE_ID") or "").strip(),
        route_pool_entry_id_hint=str(config.get("LAST30DAYS_FACEBOOK_ROUTE_POOL_ENTRY_ID") or "").strip(),
    )
    scraper = FacebookScraper(
        CliAgentBrowserClient(timeout=timeout),
        request,
        limit=int(config.get("LAST30DAYS_FACEBOOK_MAX_RESULTS") or settings["results"]),
        scrolls=int(config.get("LAST30DAYS_FACEBOOK_SCROLLS") or settings["scrolls"]),
        initial_wait=float(config.get("LAST30DAYS_FACEBOOK_INITIAL_WAIT") or 4.0),
        scroll_wait=float(config.get("LAST30DAYS_FACEBOOK_SCROLL_WAIT") or 2.0),
        debug_dir=str(config.get("LAST30DAYS_FACEBOOK_DEBUG_DIR") or "").strip(),
    )
    return scraper.search(topic, from_date, to_date)


def parse_facebook_response(response: dict[str, Any]) -> list[dict[str, Any]]:
    if response.get("error"):
        prefix = f"[{response.get('error_type')}] " if response.get("error_type") else ""
        _log(prefix + str(response["error"]))
    items = response.get("items") or []
    if not isinstance(items, list):
        return []
    return [item for item in items if isinstance(item, dict)]


def _search_url(topic: str) -> str:
    return f"https://www.facebook.com/search/top/?q={quote_plus(topic)}"


def _page_state(raw: dict[str, Any]) -> FacebookPageState:
    fields = {key: raw.get(key) for key in FacebookPageState.__dataclass_fields__}
    fields["url"] = str(fields.get("url") or "")
    fields["title"] = str(fields.get("title") or "")
    fields["heading"] = str(fields.get("heading") or "")
    fields["query_value"] = str(fields.get("query_value") or "")
    for key in ("has_search_filters", "no_results", "login_page", "checkpoint", "error_page"):
        fields[key] = bool(fields.get(key))
    return FacebookPageState(**fields)


def _page_matches_query(page: FacebookPageState, topic: str) -> bool:
    parsed = urlsplit(page.url)
    if parsed.hostname not in {"facebook.com", "www.facebook.com", "m.facebook.com"}:
        return False
    if not re.match(r"^/search/(?:top|posts)/?", parsed.path):
        return False
    observed = parse_qs(parsed.query).get("q", [""])[0].strip()
    if observed.casefold() != topic.strip().casefold():
        return False
    evidence = f"{page.title} {page.heading} {page.query_value}".casefold()
    query_readback = topic.strip().casefold() in evidence
    return query_readback and (page.has_search_filters or page.no_results)


def _find_ref(snapshot: BrowserSnapshot, *, role: set[str], name: str) -> str | None:
    expected = name.casefold()
    for ref, details in snapshot.refs.items():
        if str(details.get("role") or "").casefold() not in role:
            continue
        if str(details.get("name") or "").strip().casefold() == expected:
            return f"@{ref.lstrip('@')}"
    return None


def _candidate_from_raw(raw: dict[str, Any], now: datetime) -> FacebookCandidate:
    sponsored = bool(raw.get("sponsored"))
    canonical_url = _canonical_post_url(str(raw.get("url") or ""))
    kind = _classify_candidate(
        str(raw.get("url") or ""), sponsored, canonical_url, is_comment=bool(raw.get("is_comment"))
    )
    published_at, confidence = _parse_facebook_date(str(raw.get("timestamp") or ""), now)
    text = _clean_post_text(str(raw.get("text") or ""))
    author = _clean_author(str(raw.get("author") or "")) or _author_from_url(canonical_url)
    return FacebookCandidate(
        kind=kind,
        text=text,
        author=author,
        canonical_url=canonical_url,
        published_at=published_at,
        date_confidence=confidence,
        engagement=_clean_engagement(raw.get("engagement") or {}),
        sponsored=sponsored,
    )


def _validate_candidate(
    candidate: FacebookCandidate, topic: str, from_date: str, to_date: str
) -> None:
    if candidate.kind != "post":
        candidate.rejection_reasons.append(f"kind_{candidate.kind}")
    if not candidate.canonical_url:
        candidate.rejection_reasons.append("missing_permalink")
    meaningful = re.sub(r"\W+", "", candidate.text, flags=re.UNICODE)
    if len(meaningful) < 30:
        candidate.rejection_reasons.append("text_too_short")
    if _is_noise_text(candidate.text):
        candidate.rejection_reasons.append("navigation_noise")
    if not candidate.author:
        candidate.rejection_reasons.append("missing_author")
    if not candidate.published_at or candidate.date_confidence == "low":
        candidate.rejection_reasons.append("missing_date")
    elif dates.get_date_confidence(candidate.published_at, from_date, to_date) != "high":
        candidate.rejection_reasons.append("outside_date_range")
    if candidate.sponsored:
        candidate.rejection_reasons.append("sponsored")
    if _compute_relevance(topic, candidate.text) <= 0:
        candidate.rejection_reasons.append("off_topic")


def _canonical_post_url(value: str) -> str | None:
    if not value:
        return None
    parsed = urlsplit(value)
    host = (parsed.hostname or "").lower()
    if host not in {"facebook.com", "www.facebook.com", "m.facebook.com"}:
        return None
    path = re.sub(r"/+", "/", unquote(parsed.path or "/"))
    query = parse_qs(parsed.query)
    keep: dict[str, str] = {}
    if re.search(r"/(?:posts|permalink)/[^/?#]+", path) or re.search(
        r"/groups/[^/]+/posts/[^/?#]+", path
    ):
        pass
    elif path.rstrip("/") == "/permalink.php" and query.get("story_fbid") and query.get("id"):
        keep = {"story_fbid": query["story_fbid"][0], "id": query["id"][0]}
    elif query.get("story_fbid") and query.get("id"):
        path = "/permalink.php"
        keep = {"story_fbid": query["story_fbid"][0], "id": query["id"][0]}
    else:
        return None
    path = path.rstrip("/") or "/"
    return urlunsplit(("https", "www.facebook.com", path, urlencode(keep), ""))


def _classify_candidate(
    value: str, sponsored: bool, canonical_url: str | None, *, is_comment: bool = False
) -> str:
    if sponsored:
        return "ad"
    if is_comment:
        return "unknown"
    if canonical_url:
        return "post"
    parsed = urlsplit(value)
    path = parsed.path.lower()
    if "/stories/" in path or "/story.php" in path:
        return "story"
    if re.match(r"^/groups/[^/]+/?$", path):
        return "group"
    if path and path != "/" and not path.startswith("/search/"):
        return "page"
    if path.startswith("/search/"):
        return "recommendation"
    return "unknown"


def _parse_facebook_date(value: str, now: datetime) -> tuple[str | None, Literal["high", "med", "low"]]:
    raw = value.strip()
    if not raw:
        return None, "low"
    if re.fullmatch(r"\d{9,13}", raw):
        timestamp = int(raw)
        if len(raw) == 13:
            timestamp //= 1000
        try:
            return datetime.fromtimestamp(timestamp, tz=timezone.utc).date().isoformat(), "high"
        except (OverflowError, OSError, ValueError):
            return None, "low"
    parsed = dates.parse_date(raw)
    if parsed:
        return parsed.date().isoformat(), "high"
    lowered = raw.casefold()
    if lowered in {"just now", "now"}:
        return now.date().isoformat(), "med"
    if lowered == "yesterday":
        return (now - timedelta(days=1)).date().isoformat(), "med"
    relative = re.search(
        r"(?:about\s+)?(\d+)\s*(minute|min|hour|hr|day|week|month|year)s?\s+ago", lowered
    )
    if relative:
        amount = int(relative.group(1))
        unit = relative.group(2)
        if unit in {"minute", "min"}:
            delta = timedelta(minutes=amount)
        elif unit in {"hour", "hr"}:
            delta = timedelta(hours=amount)
        elif unit == "day":
            delta = timedelta(days=amount)
        elif unit == "week":
            delta = timedelta(weeks=amount)
        elif unit == "month":
            delta = timedelta(days=30 * amount)
        else:
            delta = timedelta(days=365 * amount)
        return (now - delta).date().isoformat(), "med"
    for fmt in ("%B %d, %Y", "%b %d, %Y", "%B %d at %I:%M %p", "%b %d at %I:%M %p"):
        try:
            parsed_label = datetime.strptime(raw, fmt)
        except ValueError:
            continue
        if "%Y" not in fmt:
            parsed_label = parsed_label.replace(year=now.year)
            if parsed_label.date() > now.date() + timedelta(days=1):
                parsed_label = parsed_label.replace(year=now.year - 1)
        return parsed_label.date().isoformat(), "med"
    return None, "low"


def _clean_post_text(value: str) -> str:
    value = re.sub(r"(?:\bFacebook\b[\s·|]*){2,}", " ", value, flags=re.I)
    value = re.sub(r"\b(?:[A-Za-z]\s+){5,}[A-Za-z]\b", " ", value)
    noise = {
        "like", "comment", "share", "send", "see more", "all reactions", "follow",
        "suggested for you", "people you may know", "facebook",
    }
    lines: list[str] = []
    for line in value.splitlines():
        cleaned = re.sub(r"[ \t]+", " ", line).strip()
        if not cleaned or cleaned.casefold() in noise:
            continue
        lines.append(cleaned)
    return "\n".join(lines).strip()


def _clean_author(value: str) -> str | None:
    cleaned = re.sub(r"\s+", " ", value).strip()
    if not cleaned or cleaned.casefold() in {"facebook", "like", "comment", "share"}:
        return None
    return cleaned[:120]


def _author_from_url(value: str | None) -> str | None:
    if not value:
        return None
    parts = [part for part in urlsplit(value).path.split("/") if part]
    if not parts or parts[0] in {"groups", "permalink.php"}:
        return None
    return parts[0]


def _is_noise_text(value: str) -> bool:
    lowered = value.casefold().strip()
    return not lowered or lowered.startswith(("suggested for you", "people you may know", "stories"))


def _clean_engagement(raw: dict[str, Any]) -> dict[str, int]:
    cleaned: dict[str, int] = {}
    for key in ("likes", "comments", "shares"):
        try:
            cleaned[key] = max(0, int(raw.get(key) or 0))
        except (TypeError, ValueError):
            cleaned[key] = 0
    return cleaned


def _select_target_id(session: dict[str, Any], tabs: Any) -> str:
    tab_ids = session.get("tabIds") or []
    if not isinstance(tabs, dict):
        return ""
    for tab_id in tab_ids:
        tab = tabs.get(tab_id)
        if isinstance(tab, dict) and "facebook.com" in str(tab.get("url") or ""):
            return str(tab.get("targetId") or str(tab_id).removeprefix("target:"))
    if tab_ids:
        tab = tabs.get(tab_ids[0])
        if isinstance(tab, dict):
            return str(tab.get("targetId") or str(tab_ids[0]).removeprefix("target:"))
    return ""


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
    return candidates[0][0] if candidates else ""


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
    for key in ("c_user", "xs", "cookie", "authorization", "token", "password"):
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


def _command_operation(args: list[str]) -> str:
    for token in ("service", "remote-view", "snapshot", "eval", "fill", "press", "click", "wait", "tab", "scroll"):
        if token in args:
            return token
    return "unknown"
