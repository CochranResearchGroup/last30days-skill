"""Quality-gated LinkedIn content search through a retained agent-browser profile.

LinkedIn credentials remain in the operator-managed browser profile. This
module verifies workspace identity, authentication, query navigation, and post
quality without reading or returning cookie values or raw page HTML.
"""

from __future__ import annotations

from collections import Counter, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import time
from typing import Any, Literal, Protocol
from urllib.parse import parse_qs, unquote, urlencode, urlsplit, urlunsplit

from . import dates, facebook as browser_runtime, log
from .relevance import token_overlap_relevance as _compute_relevance


DEPTH_CONFIG = {
    "quick": {"results": 8, "scrolls": 0, "timeout": 45},
    "default": {"results": 16, "scrolls": 1, "timeout": 75},
    "deep": {"results": 30, "scrolls": 2, "timeout": 120},
}

DEFAULT_MIN_ACTION_DELAY = 4.0
DEFAULT_MAX_ACTIONS_PER_MINUTE = 6

ERROR_TYPES = browser_runtime.ERROR_TYPES
BrowserWorkspaceRequest = browser_runtime.BrowserWorkspaceRequest
BrowserWorkspace = browser_runtime.BrowserWorkspace
BrowserSnapshot = browser_runtime.BrowserSnapshot
BrowserAction = browser_runtime.BrowserAction
BrowserState = browser_runtime.BrowserState
LinkedInScraperFailure = browser_runtime.FacebookScraperFailure


AUTH_SCRIPT = r"""
(() => {
  const body = (document.body?.innerText || "").slice(0, 12000);
  const cookieNames = new Set(document.cookie.split(";").map((part) => part.split("=", 1)[0].trim()));
  const loginForm = Boolean(document.querySelector(
    'input[name="session_key"], input[name="session_password"], form.login__form, a[href*="/uas/login"]'
  ));
  const globalNav = document.querySelector('#global-nav, nav[aria-label="Primary Navigation"]');
  const authenticatedNav = Boolean(globalNav) || ["/mynetwork", "/messaging/", "/notifications/"]
    .every((path) => document.querySelector(`nav a[href*="${path}"], a[href*="${path}"]`));
  const checkpoint = /checkpoint|security verification|enter the code|verify your identity|challenge\//i.test(
    `${location.href}\n${body}`
  );
  return {
    url: location.href,
    title: document.title,
    login_form: loginForm,
    checkpoint,
    authenticated_dom: authenticatedNav && !loginForm && !checkpoint,
    has_li_at: cookieNames.has("li_at")
  };
})()
"""


PAGE_STATE_SCRIPT = r"""
(() => {
  const clean = (value) => String(value || "").replace(/\s+/g, " ").trim();
  const fullBody = clean(document.body?.innerText || "");
  const body = fullBody.slice(0, 24000);
  const search = document.querySelector(
    'input[placeholder="Search"], input[aria-label="Search"], input[placeholder*="looking for"]'
  );
  const heading = Array.from(document.querySelectorAll('h1, h2, [role="heading"]'))
    .map((node) => clean(node.innerText || node.textContent))
    .find((text) => /search|results|posts/i.test(text)) || "";
  const filterText = Array.from(document.querySelectorAll('[role="tab"], [role="button"], a'))
    .map((node) => clean(node.innerText || node.textContent)).join(" ");
  const contentCards = document.querySelectorAll(
    '[data-view-name="feed-full-update"], [data-urn^="urn:li:activity:"], .feed-shared-update-v2, main [role="listitem"]'
  );
  const rateLimitReason =
    /commercial use limit|you.?ve reached[^.]{0,80}search limit|out of searches|maximum number of searches/i.test(fullBody)
      ? "search_limit"
      : /too many requests|request limit reached/i.test(fullBody)
        ? "too_many_requests"
        : /account (?:has been|is) temporarily restricted|temporarily restricted your account/i.test(fullBody)
          ? "temporary_restriction"
          : /we.?ve detected unusual activity|automated activity (?:on|from) your account/i.test(fullBody)
            ? "unusual_activity"
            : "";
  return {
    url: location.href,
    title: document.title,
    heading,
    query_value: clean(search?.value || ""),
    has_content_filters: /posts|date posted|sort by|content/i.test(filterText),
    has_content_cards: contentCards.length > 0,
    no_results: /no results|we couldn't find|try searching for something else/i.test(body),
    login_page: Boolean(document.querySelector(
      'input[name="session_key"], input[name="session_password"], form.login__form'
    )) || /\/uas\/login/.test(location.pathname),
    checkpoint: /checkpoint|security verification|enter the code|verify your identity|challenge\//i.test(
      `${location.href} ${body}`
    ),
    rate_limited: Boolean(rateLimitReason),
    rate_limit_reason: rateLimitReason,
    error_page: /something went wrong|page not found|temporarily unavailable|service unavailable/i.test(body)
  };
})()
"""


EXTRACT_SCRIPT = r"""
(() => {
  const clean = (value) => String(value || "").replace(/[ \t]+/g, " ").trim();
  const body = clean(document.body?.innerText || "");
  const rateLimitReason =
    /commercial use limit|you.?ve reached[^.]{0,80}search limit|out of searches|maximum number of searches/i.test(body)
      ? "search_limit"
      : /too many requests|request limit reached/i.test(body)
        ? "too_many_requests"
        : /account (?:has been|is) temporarily restricted|temporarily restricted your account/i.test(body)
          ? "temporary_restriction"
          : /we.?ve detected unusual activity|automated activity (?:on|from) your account/i.test(body)
            ? "unusual_activity"
            : "";
  const main = document.querySelector('main, [role="main"], .scaffold-layout__main');
  if (!main) return {
    url: location.href, title: document.title, candidates: [],
    rate_limited: Boolean(rateLimitReason), rate_limit_reason: rateLimitReason
  };
  const selectors = [
    '[data-view-name="feed-full-update"]',
    '[data-urn^="urn:li:activity:"]',
    '.feed-shared-update-v2',
    'li.reusable-search__result-container',
    'main [role="listitem"]'
  ];
  const nodes = [];
  const nodeSet = new Set();
  for (const selector of selectors) {
    for (const node of main.querySelectorAll(selector)) {
      if (nodeSet.has(node)) continue;
      if (nodes.some((existing) => existing.contains(node))) continue;
      nodeSet.add(node);
      nodes.push(node);
    }
  }
  const count = (value, labels) => {
    const text = clean(value);
    for (const label of labels) {
      const match = text.match(new RegExp(`(\\d+(?:[,.]\\d+)?\\s*[KkMm]?)\\s+${label}`, "i"));
      if (!match) continue;
      const raw = match[1].replace(/,/g, "").toLowerCase();
      const number = Number.parseFloat(raw);
      if (!Number.isFinite(number)) return 0;
      return Math.round(number * (raw.endsWith("k") ? 1000 : raw.endsWith("m") ? 1000000 : 1));
    }
    return 0;
  };
  const candidates = [];
  const seen = new Set();
  for (const node of nodes) {
    const text = (node.innerText || node.textContent || "").trim();
    if (!text) continue;
    const anchors = Array.from(node.querySelectorAll('a[href]'));
    const permalink = anchors.find((anchor) =>
      /\/feed\/update\/urn:li:activity:\d+|\/posts\/[^/?#]+/i.test(anchor.href || "")
    );
    const authorNode = node.querySelector(
      '.update-components-actor__name, .feed-shared-actor__name, [data-view-name="feed-actor-name"]'
    ) || anchors.find((anchor) => /\/in\/|\/company\//.test(anchor.href || ""));
    const timeNode = node.querySelector(
      'time, .update-components-actor__sub-description, .feed-shared-actor__sub-description'
    );
    const timestampText = (text.split("\n").map(clean).find((line) =>
      /^(?:\d+\s*(?:s|m|h|d|w|mo)|\d+\s+(?:second|minute|hour|day|week|month)s?)(?:\s*•.*)?$/i.test(line)
    ) || "");
    const actionText = Array.from(node.querySelectorAll('button, [aria-label]'))
      .map((item) => `${item.getAttribute('aria-label') || ''} ${item.innerText || ''}`)
      .join(" ");
    const urn = node.getAttribute('data-urn') || node.dataset?.urn || "";
    const key = `${permalink?.href || urn}|${text.slice(0, 240)}`;
    if (seen.has(key)) continue;
    seen.add(key);
    candidates.push({
      text,
      url: permalink?.href || "",
      urn,
      author: clean(authorNode?.innerText || authorNode?.textContent || ""),
      author_url: authorNode?.href || authorNode?.closest?.('a[href]')?.href || "",
      timestamp: clean(
        timeNode?.getAttribute?.('datetime') ||
        timeNode?.getAttribute?.('aria-label') ||
        timeNode?.getAttribute?.('title') ||
        timeNode?.innerText || timeNode?.textContent || timestampText
      ),
      sponsored: /(^|\n)\s*(promoted|sponsored)\s*($|\n)/i.test(text),
      engagement: {
        likes: count(`${actionText} ${text}`, ["reactions?", "likes?"]),
        comments: count(`${actionText} ${text}`, ["comments?"]),
        shares: count(`${actionText} ${text}`, ["reposts?", "shares?"])
      }
    });
  }
  return {
    url: location.href, title: document.title, candidates,
    rate_limited: Boolean(rateLimitReason), rate_limit_reason: rateLimitReason
  };
})()
"""


@dataclass(frozen=True)
class LinkedInAuthState:
    authenticated: bool
    login_form: bool = False
    checkpoint: bool = False
    has_li_at: bool = False
    url: str = ""


@dataclass(frozen=True)
class LinkedInPageState:
    url: str
    title: str
    heading: str = ""
    query_value: str = ""
    has_content_filters: bool = False
    has_content_cards: bool = False
    no_results: bool = False
    login_page: bool = False
    checkpoint: bool = False
    rate_limited: bool = False
    rate_limit_reason: str = ""
    error_page: bool = False


@dataclass
class LinkedInCandidate:
    kind: Literal["post", "ad", "unknown"]
    text: str
    author: str | None
    canonical_url: str | None
    published_at: str | None
    date_confidence: Literal["high", "med", "low"]
    engagement: dict[str, int]
    sponsored: bool
    rejection_reasons: list[str] = field(default_factory=list)


@dataclass
class LinkedInRunDiagnostics:
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


class LinkedInInteractionLimiter:
    """Bound user-like LinkedIn actions within one engine process."""

    def __init__(self, *, min_delay: float, max_actions_per_minute: int) -> None:
        self.min_delay = max(0.0, min_delay)
        self.max_actions_per_minute = max(1, max_actions_per_minute)
        self._events: deque[float] = deque()

    def wait(self) -> None:
        now = time.monotonic()
        while self._events and now - self._events[0] >= 60.0:
            self._events.popleft()
        delay = 0.0
        if self._events:
            delay = max(delay, self.min_delay - (now - self._events[-1]))
        if len(self._events) >= self.max_actions_per_minute:
            delay = max(delay, 60.0 - (now - self._events[0]))
        if delay > 0:
            time.sleep(delay)
            now = time.monotonic()
            while self._events and now - self._events[0] >= 60.0:
                self._events.popleft()
        self._events.append(now)


_INTERACTION_LIMITERS: dict[tuple[str, float, int], LinkedInInteractionLimiter] = {}


def _interaction_limiter(
    session_name: str,
    min_delay: float,
    max_actions_per_minute: int,
) -> LinkedInInteractionLimiter:
    key = (session_name, min_delay, max_actions_per_minute)
    limiter = _INTERACTION_LIMITERS.get(key)
    if limiter is None:
        limiter = LinkedInInteractionLimiter(
            min_delay=min_delay,
            max_actions_per_minute=max_actions_per_minute,
        )
        _INTERACTION_LIMITERS[key] = limiter
    return limiter


class AgentBrowserClient(Protocol):
    def acquire_workspace(self, request: BrowserWorkspaceRequest) -> BrowserWorkspace: ...
    def inspect_auth(self, workspace: BrowserWorkspace) -> LinkedInAuthState: ...
    def snapshot(self, workspace: BrowserWorkspace) -> BrowserSnapshot: ...
    def act(self, workspace: BrowserWorkspace, action: BrowserAction) -> BrowserState: ...
    def evaluate(self, workspace: BrowserWorkspace, script: str) -> dict[str, Any]: ...


class CliAgentBrowserClient(browser_runtime.CliAgentBrowserClient):
    """LinkedIn-specific workspace acquisition over the shared JSON CLI adapter."""

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
                raise LinkedInScraperFailure(
                    "profile_mismatch",
                    f"agent-browser session {request.session_name!r} uses profile "
                    f"{observed_profile!r}, not {request.profile_id!r}",
                )
            browser_ids = session.get("browserIds") or []
            if browser_ids:
                browser_id = str(browser_ids[0])
                candidate = browsers.get(browser_id) if isinstance(browsers, dict) else None
                if isinstance(candidate, dict) and candidate.get("health") == "ready":
                    browser = candidate
                    target_id = _select_target_id(session, tabs)

        if browser and browser_runtime._has_ready_operator_stream(browser, request.view_provider):
            self._activate_linkedin_tab(request.session_name)
            stream = browser_runtime._ready_operator_stream(browser, request.view_provider)
            return BrowserWorkspace(
                profile_id=request.profile_id,
                browser_id=browser_id,
                session_name=request.session_name,
                target_id=target_id,
                route_id=str(stream.get("id") or ""),
                operator_url=str(stream.get("externalUrl") or stream.get("url") or ""),
                operator_visible_state="ready",
            )

        command = [
            "--session", request.session_name,
            "remote-view", "open", "https://www.linkedin.com/feed/",
            "--browser-build", request.browser_build,
            "--view-stream-provider", request.view_provider,
            "--session-name", request.session_name,
            "--service-name", "last30days",
            "--agent-name", "linkedin-scraper",
            "--task-name", "linkedin-content-search",
        ]
        if browser:
            command.extend(["--browser-id", browser_id])
        else:
            command.extend(["--runtime-profile", request.profile_id])
        route_entry = browser_runtime._select_live_route_entry(state, request)
        if route_entry:
            command.extend(["--route-pool-entry-id", route_entry])

        try:
            opened = self._invoke(command, timeout=request.timeout)
        except LinkedInScraperFailure as exc:
            if exc.error_type == "agent_browser_error" and re.search(
                r"route_|display.*(?:stale|unavailable|mismatch)|no .*x11 socket", str(exc), re.I
            ):
                raise LinkedInScraperFailure("route_stale", str(exc)) from exc
            raise

        visible = opened.get("operatorVisible") if isinstance(opened.get("operatorVisible"), dict) else {}
        visible_state = str(visible.get("state") or "missing")
        if visible_state != "ready":
            error_type = "navigation_mismatch" if visible_state == "wrong_tab" else "route_stale"
            raise LinkedInScraperFailure(
                error_type,
                f"agent-browser remote view is not ready (operatorVisible.state={visible_state})",
                operator_url=browser_runtime._operator_url(opened),
            )
        observed_profile = str(opened.get("profileId") or visible.get("profileId") or request.profile_id)
        if observed_profile != request.profile_id:
            raise LinkedInScraperFailure(
                "profile_mismatch",
                f"agent-browser opened profile {observed_profile!r}, not {request.profile_id!r}",
                operator_url=browser_runtime._operator_url(opened),
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
            operator_url=browser_runtime._operator_url(opened),
            operator_visible_state=visible_state,
        )

    def inspect_auth(self, workspace: BrowserWorkspace) -> LinkedInAuthState:
        self.prepare_site_tab(workspace, "linkedin.com", consolidate=True)
        raw = self.evaluate(workspace, AUTH_SCRIPT)
        return LinkedInAuthState(
            authenticated=bool(raw.get("authenticated_dom")),
            login_form=bool(raw.get("login_form")),
            checkpoint=bool(raw.get("checkpoint")),
            has_li_at=bool(raw.get("has_li_at")),
            url=str(raw.get("url") or ""),
        )

    def _activate_linkedin_tab(self, session_name: str) -> None:
        """Select a retained LinkedIn tab before site-specific auth inspection."""
        self.prepare_site_tab(
            BrowserWorkspace(
                profile_id="",
                browser_id="",
                session_name=session_name,
            ),
            "linkedin.com",
            consolidate=True,
        )


class LinkedInScraper:
    def __init__(
        self,
        client: AgentBrowserClient,
        request: BrowserWorkspaceRequest,
        *,
        limit: int,
        scrolls: int,
        initial_wait: float,
        scroll_wait: float,
        interaction_limiter: LinkedInInteractionLimiter | None = None,
        now: datetime | None = None,
        debug_dir: str = "",
    ) -> None:
        self.client = client
        self.request = request
        self.limit = limit
        self.scrolls = scrolls
        self.initial_wait = initial_wait
        self.scroll_wait = scroll_wait
        self.interaction_limiter = interaction_limiter
        self.now = now or datetime.now(timezone.utc)
        self.debug_dir = debug_dir
        self._topic = ""

    def search(self, topic: str, from_date: str, to_date: str) -> dict[str, Any]:
        started = time.monotonic()
        self._topic = topic
        diagnostics = LinkedInRunDiagnostics()
        workspace: BrowserWorkspace | None = None
        page = LinkedInPageState(url="", title="")
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
                raise LinkedInScraperFailure(
                    "checkpoint_required",
                    "LinkedIn requires an operator security-verification checkpoint",
                    operator_url=workspace.operator_url,
                )
            if not auth.authenticated:
                ingress_probe = getattr(self.client, "operator_ingress_ready", None)
                if callable(ingress_probe) and not ingress_probe(workspace.operator_url):
                    raise LinkedInScraperFailure(
                        "operator_ingress_unavailable", "LinkedIn operator handoff URL is unavailable"
                    )
                raise LinkedInScraperFailure(
                    "auth_required",
                    "LinkedIn authentication is required in the retained agent-browser profile",
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
                self._act(workspace, BrowserAction("scroll", value="1400"))
                if self.scroll_wait:
                    time.sleep(self.scroll_wait)
                raw_candidates.extend(self._extract(workspace))
            if not raw_candidates:
                raise LinkedInScraperFailure(
                    "extraction_empty", "Verified LinkedIn content search contained no candidate cards"
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
                    "LinkedIn candidates were found, but none passed the post quality gate",
                    workspace,
                    page,
                    diagnostics,
                    from_date,
                    to_date,
                )
            return self._result(items, None, None, workspace, page, diagnostics, from_date, to_date)
        except LinkedInScraperFailure as exc:
            diagnostics.duration_ms = _elapsed_ms(started)
            _log(f"Failed stage error_type={exc.error_type} message={exc}")
            return self._result(
                [], exc.error_type, str(exc), workspace, page, diagnostics, from_date, to_date,
                operator_url=exc.operator_url,
            )

    def _navigate(self, workspace: BrowserWorkspace, topic: str) -> LinkedInPageState:
        search_url = _search_url(topic)
        prepare_site_tab = getattr(self.client, "prepare_site_tab", None)
        retained_tab = bool(
            callable(prepare_site_tab)
            and prepare_site_tab(workspace, "linkedin.com", consolidate=True)
        )
        strategy = "reuse_tab" if retained_tab else "new_tab"
        _log(f"Navigating query={topic!r} strategy={strategy}")
        operation = "navigate" if retained_tab else "new_tab"
        self._act(workspace, BrowserAction(operation, value=search_url))
        self.client.act(workspace, BrowserAction("wait", value="2500"))
        page = _page_state(self.client.evaluate(workspace, PAGE_STATE_SCRIPT))
        _log(f"Navigation readback requested={search_url!r} final={page.url!r}")
        if page.rate_limited:
            raise LinkedInScraperFailure(
                "rate_limit_detected",
                f"LinkedIn warning detected ({page.rate_limit_reason or 'unspecified'}); stopping",
                operator_url=workspace.operator_url,
            )
        if page.checkpoint:
            raise LinkedInScraperFailure(
                "checkpoint_required", "LinkedIn checkpoint appeared during search navigation",
                operator_url=workspace.operator_url,
            )
        if page.login_page:
            raise LinkedInScraperFailure(
                "auth_required", "LinkedIn session became logged out during search navigation",
                operator_url=workspace.operator_url,
            )
        if page.error_page:
            raise LinkedInScraperFailure("search_unavailable", "LinkedIn returned an error page")
        if not _page_matches_query(page, topic):
            raise LinkedInScraperFailure(
                "navigation_mismatch",
                f"LinkedIn final page does not match requested latest-content query {topic!r}: {page.url}",
            )
        return page

    def _extract(self, workspace: BrowserWorkspace) -> list[dict[str, Any]]:
        raw = self.client.evaluate(workspace, EXTRACT_SCRIPT)
        if raw.get("rate_limited"):
            raise LinkedInScraperFailure(
                "rate_limit_detected",
                f"LinkedIn warning detected ({raw.get('rate_limit_reason') or 'unspecified'}); stopping",
                operator_url=workspace.operator_url,
            )
        candidates = raw.get("candidates") or []
        return [candidate for candidate in candidates if isinstance(candidate, dict)]

    def _act(self, workspace: BrowserWorkspace, action: BrowserAction) -> BrowserState:
        if self.interaction_limiter and action.operation in {
            "navigate", "new_tab", "scroll", "click", "fill", "press"
        }:
            self.interaction_limiter.wait()
        return self.client.act(workspace, action)

    def _quality_gate(
        self,
        raw_candidates: list[dict[str, Any]],
        topic: str,
        from_date: str,
        to_date: str,
        diagnostics: LinkedInRunDiagnostics,
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
                "id": f"LI{digest}",
                "text": candidate.text,
                "url": candidate.canonical_url,
                "author": candidate.author,
                "date": candidate.published_at,
                "engagement": candidate.engagement,
                "relevance": round(relevance, 2),
                "why_relevant": f"LinkedIn post: {candidate.text[:80]}",
                "metadata": {
                    "extraction": "agent-browser-dom-v1",
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
        page: LinkedInPageState,
        diagnostics: LinkedInRunDiagnostics,
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

    def _write_debug_artifact(self, result: dict[str, Any], page: LinkedInPageState) -> None:
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
                "has_content_filters": page.has_content_filters,
                "has_content_cards": page.has_content_cards,
                "no_results": page.no_results,
                "login_page": page.login_page,
                "checkpoint": page.checkpoint,
                "rate_limited": page.rate_limited,
                "rate_limit_reason": page.rate_limit_reason,
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
            destination = directory / f"linkedin-{self.now.strftime('%Y%m%dT%H%M%SZ')}-{digest}.json"
            destination.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        except OSError as exc:
            _log(f"Could not write sanitized LinkedIn debug artifact: {browser_runtime._redact(str(exc))}")


def _log(message: str) -> None:
    log.source_log("LinkedIn", message, tty_only=False)


def is_agent_browser_available() -> bool:
    return shutil.which("agent-browser") is not None


def search_linkedin(
    topic: str,
    from_date: str,
    to_date: str,
    *,
    depth: str = "default",
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Search LinkedIn and return only verified, quality-gated content posts."""
    config = config or {}
    if not is_agent_browser_available():
        return {
            "items": [],
            "error": "agent-browser command is not on PATH",
            "error_type": "agent_browser_missing",
        }
    settings = DEPTH_CONFIG.get(depth, DEPTH_CONFIG["default"])
    timeout = int(config.get("LAST30DAYS_LINKEDIN_TIMEOUT") or settings["timeout"])
    min_action_delay = float(
        config.get("LAST30DAYS_LINKEDIN_MIN_ACTION_DELAY") or DEFAULT_MIN_ACTION_DELAY
    )
    max_actions_per_minute = int(
        config.get("LAST30DAYS_LINKEDIN_MAX_ACTIONS_PER_MINUTE")
        or DEFAULT_MAX_ACTIONS_PER_MINUTE
    )
    request = BrowserWorkspaceRequest(
        profile_id=str(config.get("LAST30DAYS_LINKEDIN_PROFILE") or "last30days-linkedin"),
        session_name=str(config.get("LAST30DAYS_LINKEDIN_SESSION") or "last30days-linkedin"),
        browser_build=str(config.get("LAST30DAYS_LINKEDIN_BROWSER_BUILD") or "stealthcdp_chromium"),
        view_provider=str(config.get("LAST30DAYS_LINKEDIN_VIEW_PROVIDER") or "rdp_gateway"),
        timeout=timeout,
        browser_id_hint=str(config.get("LAST30DAYS_LINKEDIN_BROWSER_ID") or "").strip(),
        route_id_hint=str(config.get("LAST30DAYS_LINKEDIN_ROUTE_ID") or "").strip(),
        route_pool_entry_id_hint=str(
            config.get("LAST30DAYS_LINKEDIN_ROUTE_POOL_ENTRY_ID") or ""
        ).strip(),
    )
    scraper = LinkedInScraper(
        CliAgentBrowserClient(timeout=timeout),
        request,
        limit=int(config.get("LAST30DAYS_LINKEDIN_MAX_RESULTS") or settings["results"]),
        scrolls=int(config.get("LAST30DAYS_LINKEDIN_SCROLLS") or settings["scrolls"]),
        initial_wait=float(config.get("LAST30DAYS_LINKEDIN_INITIAL_WAIT") or 4.0),
        scroll_wait=float(config.get("LAST30DAYS_LINKEDIN_SCROLL_WAIT") or 2.0),
        interaction_limiter=_interaction_limiter(
            request.session_name,
            min_action_delay,
            max_actions_per_minute,
        ),
        debug_dir=str(config.get("LAST30DAYS_LINKEDIN_DEBUG_DIR") or "").strip(),
    )
    return scraper.search(topic, from_date, to_date)


def parse_linkedin_response(response: dict[str, Any]) -> list[dict[str, Any]]:
    if response.get("error"):
        prefix = f"[{response.get('error_type')}] " if response.get("error_type") else ""
        _log(prefix + str(response["error"]))
    items = response.get("items") or []
    if not isinstance(items, list):
        return []
    return [item for item in items if isinstance(item, dict)]


def _search_url(topic: str) -> str:
    return "https://www.linkedin.com/search/results/content/?" + urlencode({
        "keywords": topic,
        "origin": "GLOBAL_SEARCH_HEADER",
        "sortBy": '"date_posted"',
    })


def _page_state(raw: dict[str, Any]) -> LinkedInPageState:
    fields = {key: raw.get(key) for key in LinkedInPageState.__dataclass_fields__}
    for key in ("url", "title", "heading", "query_value", "rate_limit_reason"):
        fields[key] = str(fields.get(key) or "")
    for key in (
        "has_content_filters", "has_content_cards", "no_results", "login_page",
        "checkpoint", "rate_limited", "error_page",
    ):
        fields[key] = bool(fields.get(key))
    return LinkedInPageState(**fields)


def _page_matches_query(page: LinkedInPageState, topic: str) -> bool:
    parsed = urlsplit(page.url)
    if (parsed.hostname or "").lower() not in {"linkedin.com", "www.linkedin.com"}:
        return False
    if not re.match(r"^/search/results/content/?$", parsed.path):
        return False
    query = parse_qs(parsed.query)
    observed = (query.get("keywords") or [""])[0].strip()
    if observed.casefold() != topic.strip().casefold():
        return False
    sort_by = (query.get("sortBy") or [""])[0].strip('"').casefold()
    if sort_by != "date_posted":
        return False
    evidence = f"{page.title} {page.heading} {page.query_value}".casefold()
    query_readback = topic.strip().casefold() in evidence
    return query_readback and (
        page.has_content_filters or page.has_content_cards or page.no_results
    )


def _candidate_from_raw(raw: dict[str, Any], now: datetime) -> LinkedInCandidate:
    sponsored = bool(raw.get("sponsored"))
    canonical_url = _canonical_post_url(str(raw.get("url") or ""), str(raw.get("urn") or ""))
    published_at, confidence = _parse_linkedin_date(str(raw.get("timestamp") or ""), now)
    text = _clean_post_text(str(raw.get("text") or ""))
    author = _clean_author(str(raw.get("author") or "")) or _author_from_url(
        str(raw.get("author_url") or "")
    )
    kind: Literal["post", "ad", "unknown"] = (
        "ad" if sponsored else "post" if canonical_url else "unknown"
    )
    return LinkedInCandidate(
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
    candidate: LinkedInCandidate, topic: str, from_date: str, to_date: str
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


def _canonical_post_url(value: str, urn: str = "") -> str | None:
    if not value and re.fullmatch(r"urn:li:activity:\d+", urn):
        value = f"https://www.linkedin.com/feed/update/{urn}/"
    if not value:
        return None
    parsed = urlsplit(value)
    if (parsed.hostname or "").lower() not in {"linkedin.com", "www.linkedin.com"}:
        return None
    path = re.sub(r"/+", "/", unquote(parsed.path or "/"))
    if re.fullmatch(r"/feed/update/urn:li:activity:\d+/?", path, re.I):
        path = path.rstrip("/") + "/"
    elif re.fullmatch(r"/posts/[A-Za-z0-9_.%-]+/?", path):
        path = path.rstrip("/") + "/"
    else:
        return None
    return urlunsplit(("https", "www.linkedin.com", path, "", ""))


def _parse_linkedin_date(
    value: str, now: datetime
) -> tuple[str | None, Literal["high", "med", "low"]]:
    raw = re.sub(r"\s*[•·].*$", "", value).strip()
    if not raw:
        return None, "low"
    parsed = dates.parse_date(raw)
    if parsed:
        return parsed.date().isoformat(), "high"
    lowered = raw.casefold()
    if lowered in {"now", "just now"}:
        return now.date().isoformat(), "med"
    relative = re.fullmatch(
        r"(?:about\s+)?(\d+)\s*(m|min|minute|h|hr|hour|d|day|w|week|mo|month|y|yr|year)s?(?:\s+ago)?",
        lowered,
    )
    if not relative:
        return None, "low"
    amount = int(relative.group(1))
    unit = relative.group(2)
    if unit in {"m", "min", "minute"}:
        delta = timedelta(minutes=amount)
    elif unit in {"h", "hr", "hour"}:
        delta = timedelta(hours=amount)
    elif unit in {"d", "day"}:
        delta = timedelta(days=amount)
    elif unit in {"w", "week"}:
        delta = timedelta(weeks=amount)
    elif unit in {"mo", "month"}:
        delta = timedelta(days=30 * amount)
    else:
        delta = timedelta(days=365 * amount)
    return (now - delta).date().isoformat(), "med"


def _clean_post_text(value: str) -> str:
    noise = {
        "like", "comment", "repost", "send", "see more", "follow", "connect",
        "linkedin", "promoted", "sponsored", "activate to view larger image",
    }
    lines: list[str] = []
    for line in value.splitlines():
        cleaned = re.sub(r"[ \t]+", " ", line).strip()
        normalized = cleaned.casefold().rstrip(":")
        if not cleaned or normalized in noise:
            continue
        if re.fullmatch(r"\d+(?:[,.]\d+)?[KkMm]?", cleaned) or re.fullmatch(
            r"\d+(?:[,.]\d+)?[KkMm]?\s+(?:comments?|reactions?|reposts?)", cleaned, re.I
        ):
            continue
        if re.fullmatch(r"\d+\s*(?:m|h|d|w|mo|y)(?:\s*[•·].*)?", cleaned, re.I):
            continue
        cleaned = re.sub(r"\s*(?:…|\.\.\.)?\s*see more\s*$", "", cleaned, flags=re.I)
        lines.append(cleaned)
    return "\n".join(lines).strip()


def _clean_author(value: str) -> str | None:
    cleaned = re.sub(r"\s+", " ", value).strip()
    cleaned = re.sub(r"\s+(?:1st|2nd|3rd)\s*$", "", cleaned, flags=re.I)
    if not cleaned or cleaned.casefold() in {"linkedin", "like", "comment", "repost"}:
        return None
    return cleaned[:160]


def _author_from_url(value: str) -> str | None:
    parsed = urlsplit(value)
    if (parsed.hostname or "").lower() not in {"linkedin.com", "www.linkedin.com"}:
        return None
    match = re.match(r"^/(?:in|company)/([^/?#]+)/?", parsed.path)
    return match.group(1).replace("-", " ") if match else None


def _is_noise_text(value: str) -> bool:
    lowered = value.casefold().strip()
    return not lowered or lowered.startswith((
        "people you may know", "jobs you may be interested in", "recommended for you",
    ))


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
        if isinstance(tab, dict) and "linkedin.com" in str(tab.get("url") or ""):
            return str(tab.get("targetId") or str(tab_id).removeprefix("target:"))
    if tab_ids:
        tab = tabs.get(tab_ids[0])
        if isinstance(tab, dict):
            return str(tab.get("targetId") or str(tab_ids[0]).removeprefix("target:"))
    return ""


def _elapsed_ms(started: float) -> int:
    return max(0, round((time.monotonic() - started) * 1000))
