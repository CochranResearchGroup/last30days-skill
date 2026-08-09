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
import math
from pathlib import Path
import re
import shutil
import subprocess
import time
from typing import Any, Literal, Protocol
from urllib.parse import parse_qs, unquote, urlencode, urlsplit, urlunsplit
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from . import agent_browser_config, dates, log
from .relevance import token_overlap_relevance as _compute_relevance


DEPTH_CONFIG = {
    "quick": {"results": 8, "scrolls": 1, "timeout": 45},
    "default": {"results": 16, "scrolls": 2, "timeout": 75},
    "deep": {"results": 30, "scrolls": 4, "timeout": 120},
}

MAX_RUN_BUDGET_SECONDS = 75

ERROR_TYPES = {
    "agent_browser_missing",
    "profile_mismatch",
    "route_stale",
    "auth_required",
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

RECENT_POSTS_FILTER = (
    "eyJyZWNlbnRfcG9zdHM6MCI6IntcIm5hbWVcIjpcInJlY2VudF9wb3N0c1wiLFwiYXJnc1wiOlwiXCJ9In0="
)

AUTH_SCRIPT = r"""
(() => {
  const surface = document.querySelector('[role="dialog"], [role="main"], main') || document.body;
  const body = String(surface?.textContent || "").slice(0, 40000);
  const cookieNames = new Set(document.cookie.split(";").map((part) => part.split("=", 1)[0].trim()));
  const loginForm = Boolean(document.querySelector('input[name="email"], input[name="pass"], form[action*="login"]'));
  const search = document.querySelector('[aria-label="Search Facebook"], input[placeholder="Search Facebook"]');
  const authenticatedDom = Boolean(search) && !loginForm;
  const checkpointPath = /\/(?:checkpoint|two_step_verification)(?:\/|$)/i.test(location.pathname);
  const checkpointForm = Boolean(document.querySelector(
    'form[action*="checkpoint"], form[action*="two_step_verification"], [data-testid*="checkpoint"]'
  ));
  const checkpointBody = /security check|required to confirm your identity|enter (?:the|your) (?:security )?code/i.test(body);
  const checkpoint = checkpointPath || checkpointForm || (!authenticatedDom && checkpointBody);
  const headings = Array.from(document.querySelectorAll('h1, h2, [role="heading"]'))
    .slice(0, 64)
    .map((node) => String(node.textContent || "").replace(/\s+/g, " ").trim());
  const hasPostActions = Boolean(document.querySelector('[aria-label^="Actions for this post"]'));
  const temporaryBlockHeading = headings.some((text) =>
    /^(?:you(?:['\u2019]re| are) )?temporarily blocked[.!]?$/i.test(text)
  );
  const frequencyLimitCopy = /we limit how often you can (?:post|comment|do other things)|to prevent any misuse, we limit how often/i.test(body);
  const rateLimited = temporaryBlockHeading || (frequencyLimitCopy && !hasPostActions);
  return {
    url: location.href,
    title: document.title,
    login_form: loginForm,
    checkpoint,
    authenticated_dom: authenticatedDom && !checkpoint && !rateLimited,
    rate_limited: rateLimited,
    rate_limit_reason: temporaryBlockHeading ? "temporary_block" : (rateLimited ? "action_frequency_limit" : ""),
    has_c_user: cookieNames.has("c_user"),
    has_xs: cookieNames.has("xs")
  };
})()
"""

PAGE_STATE_SCRIPT = r"""
(() => {
  const clean = (value) => String(value || "").replace(/\s+/g, " ").trim();
  const surface = document.querySelector('[role="dialog"], [role="main"], main') || document.body;
  const body = clean(String(surface?.textContent || "").slice(0, 40000)).slice(0, 20000);
  const search = document.querySelector('[aria-label="Search Facebook"], input[placeholder="Search Facebook"]');
  const loginPage = Boolean(document.querySelector('input[name="email"], input[name="pass"], form[action*="login"]'));
  const authenticatedDom = Boolean(search) && !loginPage;
  const checkpointPath = /\/(?:checkpoint|two_step_verification)(?:\/|$)/i.test(location.pathname);
  const checkpointForm = Boolean(document.querySelector(
    'form[action*="checkpoint"], form[action*="two_step_verification"], [data-testid*="checkpoint"]'
  ));
  const checkpointBody = /security check|required to confirm your identity|enter (?:the|your) (?:security )?code/i.test(body);
  const headings = Array.from(document.querySelectorAll('h1, h2, [role="heading"]'))
    .slice(0, 64)
    .map((node) => clean(node.textContent));
  const heading = headings.find((text) => /search|result/i.test(text)) || "";
  const hasPostActions = Boolean(document.querySelector('[aria-label^="Actions for this post"]'));
  const temporaryBlockHeading = headings.some((text) =>
    /^(?:you(?:['\u2019]re| are) )?temporarily blocked[.!]?$/i.test(text)
  );
  const frequencyLimitCopy = /we limit how often you can (?:post|comment|do other things)|to prevent any misuse, we limit how often/i.test(body);
  const rateLimited = temporaryBlockHeading || (frequencyLimitCopy && !hasPostActions);
  const filterText = Array.from(document.querySelectorAll('[role="tab"], a[href*="/search/"]'))
    .slice(0, 64)
    .map((node) => clean(node.textContent)).join(" ").slice(0, 12000);
  return {
    url: location.href,
    title: document.title,
    heading,
    query_value: clean(search?.value || search?.textContent || ""),
    has_search_filters: /posts|recent posts|people|groups|pages/i.test(filterText),
    no_results: /no results|we didn't find|couldn't find|try different keywords/i.test(body),
    login_page: loginPage,
    checkpoint: checkpointPath || checkpointForm || (!authenticatedDom && checkpointBody),
    rate_limited: rateLimited,
    rate_limit_reason: temporaryBlockHeading ? "temporary_block" : (rateLimited ? "action_frequency_limit" : ""),
    error_page: /something went wrong|this content isn't available|temporarily unavailable/i.test(body)
  };
})()
"""

EXTRACT_SCRIPT = r"""
(() => {
  const clean = (value) => String(value || "").replace(/[ \t]+/g, " ").trim();
  const main = document.querySelector('[role="main"]') || document.querySelector('main');
  const surface = document.querySelector('[role="dialog"]') || main || document.body;
  const body = String(surface?.textContent || "").slice(0, 40000).replace(/\s+/g, " ").trim().slice(0, 20000);
  const headings = Array.from(document.querySelectorAll('h1, h2, [role="heading"]'))
    .slice(0, 64)
    .map((node) => String(node.textContent || "").replace(/\s+/g, " ").trim());
  const hasPostActions = Boolean(document.querySelector('[aria-label^="Actions for this post"]'));
  const temporaryBlockHeading = headings.some((text) =>
    /^(?:you(?:['\u2019]re| are) )?temporarily blocked[.!]?$/i.test(text)
  );
  const frequencyLimitCopy = /we limit how often you can (?:post|comment|do other things)|to prevent any misuse, we limit how often/i.test(body);
  const rateLimited = temporaryBlockHeading || (frequencyLimitCopy && !hasPostActions);
  const rateLimitReason = temporaryBlockHeading ? "temporary_block" : (rateLimited ? "action_frequency_limit" : "");
  if (!main) return {url: location.href, title: document.title, candidates: [], rate_limited: rateLimited, rate_limit_reason: rateLimitReason};
  const labelClean = (value) => String(value || "")
    .replace(/\u034f/g, "")
    .replace(/\s+/g, " ")
    .trim();
  const renderedGlyphText = (node) => {
    if (!node) return "";
    const bounds = node.getBoundingClientRect?.();
    const leaves = Array.from(node.querySelectorAll("*")).filter(
      (element) => !element.children.length &&
        String(element.textContent || "").replace(/\u034f/g, "").length
    );
    if (!bounds || !leaves.length) {
      return labelClean(node.innerText || node.textContent || "");
    }
    const glyphs = leaves.map((element) => {
      const rect = element.getBoundingClientRect();
      const style = getComputedStyle(element);
      return {
        text: String(element.textContent || "").replace(/\u034f/g, ""),
        left: rect.left,
        top: rect.top,
        right: rect.right,
        bottom: rect.bottom,
        display: style.display,
        visibility: style.visibility,
        opacity: Number.parseFloat(style.opacity || "1"),
      };
    }).filter((glyph) =>
      glyph.text && glyph.right > glyph.left && glyph.bottom > glyph.top &&
      glyph.display !== "none" && glyph.visibility !== "hidden" &&
      glyph.opacity !== 0 && glyph.left >= bounds.left - 1 &&
      glyph.right <= bounds.right + 1 && glyph.top >= bounds.top - 1 &&
      glyph.bottom <= bounds.bottom + 1
    );
    if (!glyphs.length) return labelClean(node.innerText || node.textContent || "");
    glyphs.sort((left, right) =>
      Math.abs(left.top - right.top) > 2
        ? left.top - right.top
        : left.left - right.left
    );
    return labelClean(glyphs.map((glyph) => glyph.text).join(""));
  };
  const isTimestampLabel = (value) => {
    const label = labelClean(value);
    return /^(?:just now|now|today|yesterday)(?: at \d{1,2}:\d{2} [AP]M)?$/i.test(label) ||
      /^\d+\s*[mhdwy]$/i.test(label) ||
      /^(?:about )?\d+\s+(?:minutes?|hours?|days?|weeks?|months?|years?) ago$/i.test(label) ||
      /^(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?) \d{1,2}(?:, \d{4})?(?: at \d{1,2}:\d{2} [AP]M)?$/i.test(label);
  };
  const isSponsoredLabel = (value) =>
    /^(?:ad|sponsored|paid partnership)$/i.test(labelClean(value));
  const actionSelector = '[aria-label^="Actions for this post"]';
  const actionNodes = Array.from(main.querySelectorAll(actionSelector));
  const actionOwnerCounts = new Map();
  for (const action of actionNodes) {
    let cursor = action;
    while (cursor.parentElement && main.contains(cursor.parentElement)) {
      cursor = cursor.parentElement;
      actionOwnerCounts.set(cursor, (actionOwnerCounts.get(cursor) || 0) + 1);
    }
  }
  const rootForAction = (action) => {
    let root = action;
    let cursor = action;
    while (cursor.parentElement && main.contains(cursor.parentElement)) {
      const parent = cursor.parentElement;
      if (actionOwnerCounts.get(parent) !== 1) break;
      root = parent;
      cursor = parent;
    }
    return root;
  };
  const actionRoots = actionNodes.map((action) => ({
    action,
    node: action.closest('[role="article"], div[aria-posinset]') || rootForAction(action),
  }));
  const fallbackNodes = Array.from(main.querySelectorAll('[role="article"], div[aria-posinset]'))
    .filter((node) =>
      !node.querySelector(actionSelector) &&
      !actionRoots.some(({node: root}) => root.contains(node))
    );
  const nodes = [
    ...actionRoots.map(({action, node}, index) => ({action, node, source: "action_card", index})),
    ...fallbackNodes.map((node) => ({action: null, node, source: "semantic_fallback"})),
  ];
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
  for (const entry of nodes) {
    const {action, node, source, index} = entry;
    const text = (node.innerText || node.textContent || "").trim();
    if (!text) continue;
    const anchors = Array.from(node.querySelectorAll('a[href]'));
    const permalink = anchors.find((a) => /\/posts\/|\/permalink(?:\.php|\/)|story_fbid=|\/groups\/[^/]+\/posts\//.test(a.href || ""));
    const timestamp = anchors.find((a) =>
      a.querySelector('abbr, time') || a.getAttribute('data-utime') ||
      isTimestampLabel(a.getAttribute('title')) ||
      isTimestampLabel(a.getAttribute('aria-label')) ||
      isTimestampLabel(renderedGlyphText(a))
    );
    const actionLabel = action?.getAttribute("aria-label") || "";
    const actionAuthor = actionLabel.match(/^Actions for this post by (.+)$/)?.[1] || "";
    const authorNode = (actionAuthor
      ? anchors.find((a) => clean(a.innerText || a.textContent) === clean(actionAuthor))
      : null) ||
      node.querySelector('h2 a, h3 a, [role="heading"] a, strong a, a[role="link"]');
    const timestampNode = timestamp?.querySelector('abbr, time') || timestamp;
    const url = permalink?.href || "";
    const key = source === "action_card"
      ? `action-card:${index}`
      : `${url}|${text.slice(0, 240)}`;
    if (seen.has(key)) continue;
    seen.add(key);
    candidates.push({
      text,
      url,
      author: clean(
        actionAuthor || authorNode?.innerText || authorNode?.textContent ||
        authorNode?.getAttribute?.("aria-label") || ""
      ),
      author_url: authorNode?.href || "",
      media_urls: anchors
        .map((anchor) => anchor.href || "")
        .filter((href) => /\/photo\/?\?|[?&](?:fbid|set)=/.test(href)),
      media: [
        ...Array.from(node.querySelectorAll('[data-visualcompletion="media-vc-image"] img, img[src*="scontent"]'))
          .map((image) => ({
            kind: "image", url: image.currentSrc || image.src || "",
            preview_url: null, mime_type: null,
            width: image.naturalWidth || null, height: image.naturalHeight || null,
            duration_seconds: null, alt_text: image.alt || null
          })),
        ...Array.from(node.querySelectorAll("video"))
          .map((video) => ({
            kind: "video", url: url || location.href,
            preview_url: video.poster || null, mime_type: null,
            width: video.videoWidth || null, height: video.videoHeight || null,
            duration_seconds: Number.isFinite(video.duration) ? Math.round(video.duration) : null,
            alt_text: null
          }))
      ].filter((asset) => asset.url),
      action_label: actionLabel,
      candidate_source: source,
      timestamp: labelClean(
        timestampNode?.getAttribute?.("datetime") ||
        timestampNode?.getAttribute?.("data-utime") ||
        timestampNode?.getAttribute?.("title") ||
        (isTimestampLabel(timestampNode?.getAttribute?.("aria-label"))
          ? timestampNode?.getAttribute?.("aria-label") : "") ||
        renderedGlyphText(timestampNode)
      ),
      is_comment: source === "semantic_fallback" && Boolean(node.parentElement?.closest?.('[role="article"]')),
      sponsored: anchors.some((a) => isSponsoredLabel(renderedGlyphText(a))) ||
        /(^|\n)\s*(sponsored|paid partnership)\s*($|\n)/i.test(text),
      engagement: {
        likes: count(text, "likes?"),
        comments: count(text, "comments?"),
        shares: count(text, "shares?")
      }
    });
  }
  return {url: location.href, title: document.title, candidates, rate_limited: rateLimited, rate_limit_reason: rateLimitReason};
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
    start_url: str = "https://www.facebook.com/"
    service_name: str = "last30days"
    agent_name: str = "facebook-scraper"
    task_name: str = "facebook-search"
    target_service_id: str = "facebook"
    browser_host: str = "remote_headed"
    display_isolation: str = "private_virtual_display"
    control_input_provider: str = "manual_attached_desktop"


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
    rate_limited: bool = False
    rate_limit_reason: str = ""
    url: str = ""


def _facebook_auth_state(raw: dict[str, Any]) -> FacebookAuthState:
    login_form = bool(raw.get("login_form"))
    checkpoint = bool(raw.get("checkpoint"))
    has_c_user = bool(raw.get("has_c_user"))
    rate_limited = bool(raw.get("rate_limited"))
    rate_limit_reason = str(raw.get("rate_limit_reason") or "")
    return FacebookAuthState(
        authenticated=(bool(raw.get("authenticated_dom")) or has_c_user)
        and not login_form
        and not checkpoint
        and not rate_limited,
        login_form=login_form,
        checkpoint=checkpoint,
        has_c_user=has_c_user,
        has_xs=bool(raw.get("has_xs")),
        rate_limited=rate_limited,
        rate_limit_reason=(
            rate_limit_reason
            if rate_limit_reason in RATE_LIMIT_REASONS
            else ("unspecified" if rate_limited else "")
        ),
        url=str(raw.get("url") or ""),
    )


def _facebook_auth_is_explicit(auth: FacebookAuthState) -> bool:
    return auth.authenticated or auth.login_form or auth.checkpoint or auth.rate_limited


@dataclass(frozen=True)
class BrowserSnapshot:
    refs: dict[str, dict[str, Any]] = field(default_factory=dict)
    text: str = ""


@dataclass(frozen=True)
class BrowserAction:
    operation: Literal["fill", "press", "click", "wait", "navigate", "new_tab", "scroll"]
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
    rate_limited: bool = False
    rate_limit_reason: str = ""
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
    media: list[dict[str, Any]] = field(default_factory=list)
    rejection_reasons: list[str] = field(default_factory=list)


@dataclass
class FacebookRunDiagnostics:
    candidate_counts: Counter[str] = field(default_factory=Counter)
    rejection_counts: Counter[str] = field(default_factory=Counter)
    accepted_count: int = 0
    duration_ms: int = 0
    rate_limit_reason: str = ""
    failure_stage: str = ""

    def as_dict(self) -> dict[str, Any]:
        result = {
            "candidate_counts": dict(self.candidate_counts),
            "rejection_counts": dict(self.rejection_counts),
            "accepted_count": self.accepted_count,
            "duration_ms": self.duration_ms,
        }
        if self.rate_limit_reason:
            result["rate_limit_reason"] = self.rate_limit_reason
        if self.failure_stage:
            result["failure_stage"] = self.failure_stage
        return result


class FacebookScraperFailure(RuntimeError):
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
        self.reason_code = (
            reason_code
            if reason_code in RATE_LIMIT_REASONS
            else ("unspecified" if error_type == "rate_limit_detected" else "")
        )


class AgentBrowserClient(Protocol):
    def acquire_workspace(self, request: BrowserWorkspaceRequest) -> BrowserWorkspace: ...
    def prepare_operator_handoff(
        self, workspace: BrowserWorkspace, request: BrowserWorkspaceRequest
    ) -> BrowserWorkspace: ...
    def inspect_auth(self, workspace: BrowserWorkspace) -> FacebookAuthState: ...
    def snapshot(self, workspace: BrowserWorkspace) -> BrowserSnapshot: ...
    def act(self, workspace: BrowserWorkspace, action: BrowserAction) -> BrowserState: ...
    def evaluate(self, workspace: BrowserWorkspace, script: str) -> dict[str, Any]: ...


class CliAgentBrowserClient:
    """Typed adapter for the installed agent-browser JSON CLI."""

    def __init__(self, *, timeout: int, job_timeout_ms: int | None = None) -> None:
        self.timeout = timeout
        self.job_timeout_ms = job_timeout_ms or timeout * 1000
        if self.job_timeout_ms <= 0:
            raise ValueError("agent-browser job timeout must be positive")
        self.command_timings: list[dict[str, Any]] = []
        self._prepared_sites: set[tuple[str, str]] = set()
        self._run_deadline: float | None = None

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
        requested_target_service_id = target_service_id or request.target_service_id
        if access_plan is None:
            access_plan = self._invoke(
                [
                    "service", "access-plan",
                    "--service-name", request.service_name,
                    "--agent-name", request.agent_name,
                    "--task-name", request.task_name,
                    "--target-service-id", requested_target_service_id,
                    "--url", request.start_url,
                    "--browser-build", request.browser_build,
                    "--browser-host", request.browser_host,
                    "--view-stream-provider", request.view_provider,
                    "--control-input-provider", request.control_input_provider,
                    "--display-isolation", request.display_isolation,
                ],
                timeout=min(request.timeout, 30),
            )
        selected_profile = agent_browser_config.selected_profile_id(access_plan)
        if not selected_profile:
            raise FacebookScraperFailure(
                "auth_required",
                "agent-browser has no authenticated profile registered for "
                f"{requested_target_service_id}",
            )
        if selected_profile != request.profile_id:
            raise FacebookScraperFailure(
                "profile_mismatch",
                f"agent-browser selected {requested_target_service_id} profile "
                f"{selected_profile!r}, not {request.profile_id!r}",
            )
        try:
            agent_browser_config.record_access_plan(access_plan, requested_target_service_id)
        except OSError as exc:
            _log(f"Could not record user-scoped agent-browser configuration: {_redact(str(exc))}")

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
        if shared_owner:
            browser = shared_owner["browser"]
            stream = _ready_operator_stream(browser, request.view_provider)
            return BrowserWorkspace(
                profile_id=selected_profile,
                browser_id=shared_owner["browser_id"],
                session_name=shared_owner["session_name"],
                target_id=shared_owner["target_id"],
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

        try:
            opened = self._invoke(
                cmd,
                timeout=max(request.timeout, (self.job_timeout_ms + 999) // 1000 + 5),
            )
        except FacebookScraperFailure as exc:
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
            elif exc.error_type == "agent_browser_error" and re.search(
                r"route_|display.*(?:stale|unavailable|mismatch)|no .*x11 socket", str(exc), re.I
            ):
                raise FacebookScraperFailure("route_stale", str(exc)) from exc
            else:
                raise

        visible = opened.get("operatorVisible") if isinstance(opened.get("operatorVisible"), dict) else {}
        visible_state = str(
            visible.get("state") or ("not_required" if not remote_view_recommended else "missing")
        )
        if remote_view_recommended and visible_state != "ready":
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
            session_name=str(opened.get("sessionName") or visible.get("sessionName") or launch_session_name),
            target_id=str(opened.get("targetId") or visible.get("targetId") or target_id),
            route_id=str(opened.get("routeId") or visible.get("routeId") or ""),
            display_allocation_id=str(
                opened.get("displayAllocationId") or visible.get("displayAllocationId") or ""
            ),
            operator_url=_operator_url(opened),
            operator_visible_state=visible_state,
        )

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
            raise FacebookScraperFailure(
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
            raise FacebookScraperFailure(
                "operator_ingress_unavailable",
                "agent-browser did not provide a ready external operator handoff",
            )
        observed_profile = str(
            opened.get("profileId") or visible.get("profileId") or workspace.profile_id
        )
        if observed_profile != workspace.profile_id:
            raise FacebookScraperFailure(
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

    def inspect_auth(self, workspace: BrowserWorkspace) -> FacebookAuthState:
        listed = self._invoke(
            ["--session", workspace.session_name, "tab", "list"],
            timeout=min(self.timeout, 10),
        )
        tabs = listed.get("tabs") if isinstance(listed.get("tabs"), list) else []
        matches = [
            tab for tab in tabs
            if isinstance(tab, dict)
            and _url_matches_hostname(str(tab.get("url") or ""), "facebook.com")
        ]
        if matches:
            try:
                return self._probe_retained_facebook_auth(workspace, matches)
            except FacebookScraperFailure as exc:
                if exc.error_type != "agent_browser_timeout":
                    raise
                _log(
                    "All retained Facebook targets were unresponsive; "
                    "inspecting authentication once on a fresh blank target"
                )

        return self._inspect_auth_on_fresh_target(
            workspace,
            replace_existing=bool(matches),
        )

    def _inspect_auth_on_fresh_target(
        self,
        workspace: BrowserWorkspace,
        *,
        replace_existing: bool = False,
    ) -> FacebookAuthState:
        if replace_existing:
            if not self.replace_active_site_target(workspace, "facebook.com"):
                raise FacebookScraperFailure(
                    "facebook_target_unresponsive",
                    "Could not replace the unresponsive retained Facebook target",
                )

        try:
            self.act(
                workspace,
                BrowserAction(
                    "navigate" if replace_existing else "new_tab",
                    value="https://www.facebook.com/",
                ),
            )
            raw = self._evaluate_auth_probe(workspace, fresh_target=True)
        except FacebookScraperFailure as exc:
            if replace_existing and exc.error_type == "agent_browser_timeout":
                raise FacebookScraperFailure(
                    "facebook_target_unresponsive",
                    "Facebook replacement target did not respond to bounded authentication inspection",
                ) from exc
            raise
        auth = _facebook_auth_state(raw)
        if not _facebook_auth_is_explicit(auth):
            raise FacebookScraperFailure(
                "agent_browser_error",
                "Facebook authentication state remained ambiguous on a responsive target",
            )
        return auth

    def _probe_retained_facebook_auth(
        self,
        workspace: BrowserWorkspace,
        matches: list[dict[str, Any]],
    ) -> FacebookAuthState:
        """Use bounded probes to skip frozen retained targets without claiming logout."""
        def tab_index(tab: dict[str, Any]) -> int:
            try:
                return int(tab.get("index"))
            except (TypeError, ValueError):
                return -1

        candidates = sorted(
            (tab for tab in matches if tab_index(tab) >= 0),
            key=lambda tab: (0 if tab.get("active") else 1, -tab_index(tab)),
        )[:2]
        saw_responsive_ambiguous = False
        for tab in candidates:
            index = tab_index(tab)
            try:
                if not tab.get("active"):
                    self._invoke(
                        [
                            "--session",
                            workspace.session_name,
                            "--job-timeout-ms",
                            "3000",
                            "tab",
                            str(index),
                        ],
                            timeout=min(self.timeout, 15),
                    )
                auth = _facebook_auth_state(self._evaluate_auth_probe(workspace))
            except FacebookScraperFailure as exc:
                _log(
                    f"Skipping unresponsive retained Facebook tab index={index}: "
                    f"{exc.error_type}"
                )
                continue
            if _facebook_auth_is_explicit(auth):
                self._prepared_sites.add((workspace.session_name, "facebook.com"))
                return auth
            saw_responsive_ambiguous = True

        if saw_responsive_ambiguous:
            raise FacebookScraperFailure(
                "agent_browser_error",
                "Responsive retained Facebook targets did not expose explicit authentication evidence",
            )
        raise FacebookScraperFailure(
            "agent_browser_timeout",
            "No retained Facebook target responded to bounded authentication inspection",
        )

    def _evaluate_auth_probe(
        self,
        workspace: BrowserWorkspace,
        *,
        fresh_target: bool = False,
    ) -> dict[str, Any]:
        outer_timeout = min(self.timeout, 45 if fresh_target else 15)
        inner_timeout_ms = min(
            self.job_timeout_ms,
            30_000 if fresh_target else 3_000,
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
            input_text=AUTH_SCRIPT,
        )
        result = raw.get("result") if isinstance(raw.get("result"), dict) else raw
        return result if isinstance(result, dict) else {"value": result}

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
            raise FacebookScraperFailure(
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
            args = ["open", action.value]
        elif action.operation == "new_tab":
            args = ["tab", "new", action.value]
        elif action.operation == "scroll":
            args = ["scroll", "down", action.value or "1400"]
        else:  # pragma: no cover - Literal guards production callers
            raise FacebookScraperFailure("agent_browser_error", f"unsupported browser action: {action.operation}")
        raw = self._invoke(prefix + args, timeout=min(self.timeout, 30))
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
                except FacebookScraperFailure as exc:
                    if not ignore_close_failures:
                        raise
                    _log(
                        f"Best-effort close skipped Facebook tab index={index}: "
                        f"{_redact(str(exc))}"
                    )
        self._prepared_sites.add(cache_key)
        return True

    def replace_active_site_target(
        self,
        workspace: BrowserWorkspace,
        hostname: str,
    ) -> bool:
        """Open one blank successor and close only the active wedged site target."""
        listed = self._invoke(
            ["--session", workspace.session_name, "tab", "list"],
            timeout=min(self.timeout, 10),
        )
        tabs = listed.get("tabs") if isinstance(listed.get("tabs"), list) else []
        matches = [
            tab
            for tab in tabs
            if isinstance(tab, dict)
            and _url_matches_hostname(str(tab.get("url") or ""), hostname)
        ]
        active = next((tab for tab in matches if tab.get("active")), None)
        predecessor = active or (matches[-1] if matches else None)
        if not isinstance(predecessor, dict):
            return False
        try:
            predecessor_index = int(predecessor.get("index"))
        except (TypeError, ValueError):
            return False

        self._invoke(
            ["--session", workspace.session_name, "tab", "new", "about:blank"],
            timeout=min(self.timeout, 30),
        )
        try:
            self._invoke(
                [
                    "--session",
                    workspace.session_name,
                    "tab",
                    "close",
                    str(predecessor_index),
                ],
                timeout=min(self.timeout, 30),
            )
        except FacebookScraperFailure as exc:
            raise FacebookScraperFailure(
                "facebook_target_unresponsive",
                "The unresponsive Facebook predecessor target could not be closed",
            ) from exc
        self._prepared_sites.discard((workspace.session_name, hostname))
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

    def inspect_active_page(self, workspace: BrowserWorkspace) -> dict[str, Any]:
        """Read active page identity without requiring Runtime evaluation."""
        raw = self._invoke(
            ["--session", workspace.session_name, "tab", "list"],
            timeout=min(self.timeout, 15),
        )
        tabs = raw.get("tabs") if isinstance(raw.get("tabs"), list) else []
        active = next(
            (tab for tab in tabs if isinstance(tab, dict) and tab.get("active")),
            None,
        )
        if not isinstance(active, dict):
            raise FacebookScraperFailure(
                "agent_browser_error",
                "agent-browser did not report an active tab for navigation readback",
            )
        url = str(active.get("url") or "")
        title = str(active.get("title") or "")
        query_value = (parse_qs(urlsplit(url).query).get("q") or [""])[0]
        return {
            "url": url,
            "title": title,
            "heading": title,
            "query_value": query_value,
            "has_search_filters": _recent_filter_active(url),
        }

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
        started = time.monotonic()
        effective_timeout = timeout
        if self._run_deadline is not None:
            remaining = self._run_deadline - started
            if remaining <= 0:
                self._record_timing(args, started, "budget_exhausted")
                raise FacebookScraperFailure(
                    "agent_browser_timeout",
                    "Facebook adapter run budget was exhausted",
                )
            effective_timeout = max(1, min(timeout, math.ceil(remaining)))
        cmd = ["agent-browser", "--json", *args]
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
            raise FacebookScraperFailure(
                "agent_browser_timeout",
                f"agent-browser operation timed out after {effective_timeout}s",
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
        begin_run_budget = getattr(self.client, "begin_run_budget", None)
        if callable(begin_run_budget):
            begin_run_budget(self.request.timeout)
        try:
            diagnostics.failure_stage = "workspace_acquisition"
            _log(f"Acquiring agent-browser workspace profile={self.request.profile_id!r}")
            workspace = self.client.acquire_workspace(self.request)
            _log(
                "Workspace acquired "
                f"profile={workspace.profile_id!r} browser={workspace.browser_id!r} "
                f"operator_visible={workspace.operator_visible_state}"
            )
            diagnostics.failure_stage = "authentication"
            auth = self.client.inspect_auth(workspace)
            _log(
                "Authentication inspected "
                f"authenticated={auth.authenticated} login_form={auth.login_form} checkpoint={auth.checkpoint}"
            )
            if auth.rate_limited:
                raise FacebookScraperFailure(
                    "rate_limit_detected",
                    "Facebook reported a temporary activity limit",
                    reason_code=auth.rate_limit_reason,
                )
            if auth.checkpoint:
                workspace = self._prepare_operator_handoff(workspace)
                raise FacebookScraperFailure(
                    "checkpoint_required",
                    "Facebook requires an operator checkpoint",
                    operator_url=workspace.operator_url,
                )
            if not auth.authenticated:
                workspace = self._prepare_operator_handoff(workspace)
                ingress_probe = getattr(self.client, "operator_ingress_ready", None)
                if (
                    workspace.operator_url
                    and callable(ingress_probe)
                    and not ingress_probe(workspace.operator_url)
                ):
                    raise FacebookScraperFailure(
                        "operator_ingress_unavailable",
                        "Facebook operator handoff URL is unavailable",
                    )
                raise FacebookScraperFailure(
                    "auth_required",
                    "Facebook authentication is required in the retained agent-browser profile",
                    operator_url=workspace.operator_url,
                )

            diagnostics.failure_stage = "navigation"
            page = self._navigate(workspace, topic)
            if page.no_results:
                diagnostics.duration_ms = _elapsed_ms(started)
                diagnostics.failure_stage = ""
                return self._result([], None, None, workspace, page, diagnostics, from_date, to_date)

            if self.initial_wait:
                time.sleep(self.initial_wait)
            diagnostics.failure_stage = "extraction"
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
            diagnostics.failure_stage = "quality_gate"
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
            diagnostics.failure_stage = ""
            return self._result(items, None, None, workspace, page, diagnostics, from_date, to_date)
        except FacebookScraperFailure as exc:
            diagnostics.duration_ms = _elapsed_ms(started)
            if exc.error_type == "rate_limit_detected":
                diagnostics.rate_limit_reason = exc.reason_code
            _log(f"Failed stage error_type={exc.error_type} message={exc}")
            return self._result(
                [], exc.error_type, str(exc), workspace, page, diagnostics, from_date, to_date,
                operator_url=exc.operator_url,
            )
        finally:
            end_run_budget = getattr(self.client, "end_run_budget", None)
            if callable(end_run_budget):
                end_run_budget()
            if workspace is not None:
                self._best_effort_cleanup(workspace)

    def _prepare_operator_handoff(
        self, workspace: BrowserWorkspace
    ) -> BrowserWorkspace:
        if workspace.operator_visible_state == "ready" and workspace.operator_url:
            return workspace
        prepare = getattr(self.client, "prepare_operator_handoff", None)
        if not callable(prepare):
            return workspace
        try:
            return prepare(workspace, self.request)
        except FacebookScraperFailure as exc:
            if exc.error_type not in {
                "operator_ingress_unavailable",
                "route_stale",
            }:
                raise
            _log(
                "Operator handoff unavailable; preserving the source auth incident "
                f"without a link: {_redact(str(exc))}"
            )
            return workspace

    def _navigate(self, workspace: BrowserWorkspace, topic: str) -> FacebookPageState:
        recent_search_url = _search_url(topic, recent=True)
        _log(f"Navigating query={topic!r} strategy=fresh_authenticated_target")
        for attempt in range(2):
            try:
                self.client.act(
                    workspace,
                    BrowserAction("navigate", value=recent_search_url),
                )
                self.client.act(workspace, BrowserAction("wait", value="2000"))
                page = _page_state(self.client.evaluate(workspace, PAGE_STATE_SCRIPT))
                break
            except FacebookScraperFailure as exc:
                if not _is_navigation_timeout(exc):
                    raise
                identity_matches = False
                identity_read = getattr(self.client, "inspect_active_page", None)
                if attempt == 0 and callable(identity_read):
                    identity_page = _page_state(identity_read(workspace))
                    identity_matches = _page_matches_query(
                        identity_page, topic
                    ) and _recent_filter_active(
                        identity_page.url
                    )
                if attempt > 0:
                    raise FacebookScraperFailure(
                        "facebook_target_unresponsive",
                        "Facebook replacement target did not respond to bounded navigation readback",
                    ) from exc
                if identity_matches:
                    _log(
                        "Search page Runtime read timed out; active tab identity "
                        "matched, but the unresponsive target still requires one "
                        "fresh-target retry"
                    )
                else:
                    _log(
                        "Search target open/read timed out; "
                        "retrying once on a fresh blank target"
                    )
                replace_target = getattr(self.client, "replace_active_site_target", None)
                if not callable(replace_target):
                    raise FacebookScraperFailure(
                        "facebook_target_unresponsive",
                        "Facebook client cannot replace the unresponsive target",
                    ) from exc
                try:
                    replaced = replace_target(workspace, "facebook.com")
                except FacebookScraperFailure as replacement_exc:
                    if replacement_exc.error_type == "facebook_target_unresponsive":
                        raise
                    raise FacebookScraperFailure(
                        "facebook_target_unresponsive",
                        "Facebook target replacement did not complete",
                    ) from replacement_exc
                if not replaced:
                    raise FacebookScraperFailure(
                        "facebook_target_unresponsive",
                        "No active Facebook target was available for bounded replacement",
                    ) from exc

        _log(f"Navigation readback requested={recent_search_url!r} final={page.url!r}")
        if page.rate_limited:
            raise FacebookScraperFailure(
                "rate_limit_detected",
                "Facebook reported a temporary activity limit during search",
                reason_code=page.rate_limit_reason,
            )
        if page.checkpoint:
            prepared = self._prepare_operator_handoff(workspace)
            raise FacebookScraperFailure(
                "checkpoint_required", "Facebook checkpoint appeared during search navigation",
                operator_url=prepared.operator_url,
            )
        if page.login_page:
            prepared = self._prepare_operator_handoff(workspace)
            raise FacebookScraperFailure(
                "auth_required", "Facebook session became logged out during search navigation",
                operator_url=prepared.operator_url,
            )
        if page.error_page:
            raise FacebookScraperFailure("search_unavailable", "Facebook returned an error page")
        if not _page_matches_query(page, topic):
            raise FacebookScraperFailure(
                "navigation_mismatch",
                f"Facebook final page does not match requested query {topic!r}: {page.url}",
            )
        if not _recent_filter_active(page.url):
            raise FacebookScraperFailure(
                "navigation_mismatch",
                f"Facebook Recent-posts filter did not apply for query {topic!r}: {page.url}",
            )
        return page

    def _best_effort_cleanup(self, workspace: BrowserWorkspace) -> None:
        prepare_site_tab = getattr(self.client, "prepare_site_tab", None)
        if not callable(prepare_site_tab):
            return
        try:
            prepared = prepare_site_tab(
                workspace,
                "facebook.com",
                consolidate=True,
                require_active=False,
                close_timeout=30,
                ignore_close_failures=True,
            )
        except FacebookScraperFailure as exc:
            _log(f"Best-effort Facebook tab cleanup did not complete: {_redact(str(exc))}")
            return
        if not prepared:
            _log("Best-effort Facebook tab cleanup found no reusable query target")

    def _extract(self, workspace: BrowserWorkspace) -> list[dict[str, Any]]:
        extracted: list[dict[str, Any]] = []
        paired_read = getattr(self.client, "snapshot_and_evaluate", None)
        paired_timeout_fallback = False
        for attempt in range(3):
            if attempt == 0:
                # The DOM extractor normally carries its own timestamp evidence.
                # Avoid making the substantially heavier accessibility snapshot
                # a prerequisite for the ordinary successful path.
                snapshot = BrowserSnapshot()
                raw = self.client.evaluate(workspace, EXTRACT_SCRIPT)
            elif callable(paired_read):
                try:
                    snapshot, raw = paired_read(workspace, EXTRACT_SCRIPT)
                except FacebookScraperFailure as exc:
                    if exc.error_type != "agent_browser_timeout":
                        raise
                    _log(
                        "Timed-out accessibility snapshot; falling back to the "
                        "same-target DOM extraction read"
                    )
                    paired_read = None
                    paired_timeout_fallback = True
                    snapshot = BrowserSnapshot()
                    raw = self.client.evaluate(workspace, EXTRACT_SCRIPT)
            elif paired_timeout_fallback:
                snapshot = BrowserSnapshot()
                raw = self.client.evaluate(workspace, EXTRACT_SCRIPT)
            else:
                snapshot = self.client.snapshot(workspace)
                raw = self.client.evaluate(workspace, EXTRACT_SCRIPT)
            candidates = raw.get("candidates") or []
            if raw.get("rate_limited") is True:
                raise FacebookScraperFailure(
                    "rate_limit_detected",
                    "Facebook reported a temporary activity limit during extraction",
                    reason_code=str(raw.get("rate_limit_reason") or ""),
                )
            extracted = [candidate for candidate in candidates if isinstance(candidate, dict)]
            _merge_accessible_timestamps(extracted, snapshot.text, self.now)
            action_cards = [
                candidate for candidate in extracted
                if candidate.get("candidate_source") == "action_card"
            ]
            if not action_cards or any(
                _parse_facebook_date(str(candidate.get("timestamp") or ""), self.now)[0]
                for candidate in extracted
            ):
                return extracted
            if attempt < 2:
                time.sleep(1.0)
        return extracted

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
                    "media": candidate.media[:16],
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
        diagnostic_data = diagnostics.as_dict()
        command_timings = getattr(self.client, "command_timings", [])
        if isinstance(command_timings, list):
            operations = [
                {
                    "operation": str(entry.get("operation") or "unknown")[:64],
                    "duration_ms": max(0, int(entry.get("duration_ms") or 0)),
                    "status": str(entry.get("status") or "unknown")[:32],
                }
                for entry in command_timings[-12:]
                if isinstance(entry, dict)
            ]
            diagnostic_data["command_count"] = len(command_timings)
            diagnostic_data["browser_operations"] = operations
        page_signals = []
        if page.url and _page_matches_query(page, self._topic):
            page_signals.append("facebook_search_page")
        if diagnostics.rate_limit_reason:
            page_signals.append(
                f"facebook_rate_limit_{diagnostics.rate_limit_reason}"
            )
        diagnostic_data["page_signals"] = page_signals
        result: dict[str, Any] = {
            "items": items,
            "error": error,
            "error_type": error_type,
            "url": page.url,
            "title": page.title,
            "profile": self.request.profile_id,
            "session": self.request.session_name,
            "workspace": workspace_data,
            "diagnostics": diagnostic_data,
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
        display_isolation=str(
            config.get("LAST30DAYS_AGENT_BROWSER_DISPLAY_ISOLATION")
            or "shared_display"
        ),
    )
    scraper = FacebookScraper(
        CliAgentBrowserClient(
            timeout=timeout,
            **(
                {
                    "job_timeout_ms": int(
                        config["LAST30DAYS_AGENT_BROWSER_JOB_TIMEOUT_MS"]
                    )
                }
                if config.get("LAST30DAYS_AGENT_BROWSER_JOB_TIMEOUT_MS")
                else {}
            ),
        ),
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


def _search_url(topic: str, *, recent: bool = False) -> str:
    query = {"q": topic}
    if recent:
        query["filters"] = RECENT_POSTS_FILTER
    return f"https://www.facebook.com/search/top/?{urlencode(query)}"


def _recent_filter_active(value: str) -> bool:
    filters = parse_qs(urlsplit(value).query).get("filters") or []
    return RECENT_POSTS_FILTER in filters


def _page_state(raw: dict[str, Any]) -> FacebookPageState:
    fields = {key: raw.get(key) for key in FacebookPageState.__dataclass_fields__}
    fields["url"] = str(fields.get("url") or "")
    fields["title"] = str(fields.get("title") or "")
    fields["heading"] = str(fields.get("heading") or "")
    fields["query_value"] = str(fields.get("query_value") or "")
    for key in (
        "has_search_filters",
        "no_results",
        "login_page",
        "checkpoint",
        "rate_limited",
        "error_page",
    ):
        fields[key] = bool(fields.get(key))
    reason = str(fields.get("rate_limit_reason") or "")
    fields["rate_limit_reason"] = (
        reason
        if reason in RATE_LIMIT_REASONS
        else ("unspecified" if fields["rate_limited"] else "")
    )
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


def _snapshot_ref_checked(snapshot: BrowserSnapshot, ref: str) -> bool:
    ref_name = re.escape(ref.lstrip("@"))
    for line in snapshot.text.splitlines():
        if re.search(rf"\bref={ref_name}\]", line):
            return "checked=true" in line.casefold()
    return False


def _candidate_from_raw(raw: dict[str, Any], now: datetime) -> FacebookCandidate:
    sponsored = bool(raw.get("sponsored"))
    source_url = str(raw.get("url") or "")
    canonical_url = _canonical_post_url(source_url) or _recover_media_permalink(raw)
    kind = _classify_candidate(
        source_url, sponsored, canonical_url, is_comment=bool(raw.get("is_comment"))
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
        media=[
            item
            for item in list(raw.get("media") or [])[:16]
            if isinstance(item, dict)
        ],
    )


def _accessible_post_timestamps(
    snapshot_text: str, now: datetime
) -> list[tuple[str, str]]:
    """Pair accessible timestamp names with post authors in snapshot order."""
    recent_links: list[str] = []
    results: list[tuple[str, str]] = []
    for line in snapshot_text.splitlines():
        link = re.search(r'^\s*-\s+link\s+"([^"]+)"', line)
        if link:
            label = link.group(1).strip()
            if _parse_facebook_date(label, now)[0]:
                recent_links.append(label)
                recent_links = recent_links[-4:]
        action = re.search(r'Actions for this post by ([^"]+)', line)
        if action and recent_links:
            results.append((action.group(1).strip(), recent_links.pop()))
    return results


def _merge_accessible_timestamps(
    candidates: list[dict[str, Any]], snapshot_text: str, now: datetime
) -> None:
    timestamps_by_author: dict[str, list[str]] = {}
    for author, timestamp in _accessible_post_timestamps(snapshot_text, now):
        timestamps_by_author.setdefault(author.casefold(), []).append(timestamp)
    for candidate in candidates:
        if _parse_facebook_date(str(candidate.get("timestamp") or ""), now)[0]:
            continue
        author = str(candidate.get("author") or "").strip().casefold()
        labels = timestamps_by_author.get(author) or []
        if labels:
            candidate["timestamp"] = labels.pop(0)


def _recover_media_permalink(raw: dict[str, Any]) -> str | None:
    """Recover a stable post URL from author and media links in Comet cards."""
    author_url = str(raw.get("author_url") or "")
    owner = _facebook_owner_from_profile_url(author_url)
    if not owner:
        return None
    media_urls = raw.get("media_urls") or []
    for value in media_urls:
        parsed = urlsplit(str(value or ""))
        if (parsed.hostname or "").lower() not in {"facebook.com", "www.facebook.com", "m.facebook.com"}:
            continue
        query = parse_qs(parsed.query)
        post_id = ""
        for set_value in query.get("set", []):
            match = re.fullmatch(r"(?:pcb|gm)\.(\d+)", set_value)
            if match:
                post_id = match.group(1)
                break
        if not post_id:
            post_id = next(iter(query.get("fbid", [])), "")
        if not post_id or not post_id.isdigit():
            continue
        if owner.isdigit():
            return _canonical_post_url(
                f"https://www.facebook.com/permalink.php?story_fbid={post_id}&id={owner}"
            )
        return _canonical_post_url(f"https://www.facebook.com/{owner}/posts/{post_id}")
    return None


def _facebook_owner_from_profile_url(value: str) -> str:
    parsed = urlsplit(value)
    if (parsed.hostname or "").lower() not in {"facebook.com", "www.facebook.com", "m.facebook.com"}:
        return ""
    query = parse_qs(parsed.query)
    if parsed.path.rstrip("/") == "/profile.php":
        owner = next(iter(query.get("id", [])), "")
        return owner if owner.isdigit() else ""
    parts = [part for part in parsed.path.split("/") if part]
    if not parts or parts[0].casefold() in {
        "groups", "photo", "permalink.php", "search", "stories", "story.php", "watch"
    }:
        return ""
    return parts[0]


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
    if re.fullmatch(r"yesterday(?:\s+at\s+\d{1,2}:\d{2}\s+[ap]m)?", lowered):
        return (now - timedelta(days=1)).date().isoformat(), "med"
    if re.fullmatch(r"today(?:\s+at\s+\d{1,2}:\d{2}\s+[ap]m)?", lowered):
        return now.date().isoformat(), "med"
    shorthand = re.fullmatch(r"(\d+)\s*([mhdwy])", lowered)
    if shorthand:
        amount = int(shorthand.group(1))
        delta = {
            "m": timedelta(minutes=amount),
            "h": timedelta(hours=amount),
            "d": timedelta(days=amount),
            "w": timedelta(weeks=amount),
            "y": timedelta(days=365 * amount),
        }[shorthand.group(2)]
        return (now - delta).date().isoformat(), "med"
    article_relative = re.fullmatch(
        r"(?:about\s+)?an?\s+(minute|hour|day|week|month|year)\s+ago", lowered
    )
    if article_relative:
        unit = article_relative.group(1)
        delta = {
            "minute": timedelta(minutes=1),
            "hour": timedelta(hours=1),
            "day": timedelta(days=1),
            "week": timedelta(weeks=1),
            "month": timedelta(days=30),
            "year": timedelta(days=365),
        }[unit]
        return (now - delta).date().isoformat(), "med"
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
    for fmt in (
        "%B %d, %Y", "%b %d, %Y", "%B %d", "%b %d",
        "%B %d at %I:%M %p", "%b %d at %I:%M %p",
    ):
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
        "·",
    }
    raw_lines = [re.sub(r"[ \t]+", " ", line).strip() for line in value.splitlines()]
    lines: list[str] = []
    index = 0
    while index < len(raw_lines):
        if len(raw_lines[index]) <= 1:
            end = index
            while end < len(raw_lines) and len(raw_lines[end]) <= 1:
                end += 1
            if end - index >= 5:
                index = end
                continue
        cleaned = raw_lines[index]
        index += 1
        normalized = cleaned.casefold().rstrip(":")
        if not cleaned or normalized in noise or normalized.startswith("comment as "):
            continue
        if re.fullmatch(r"\d+(?:[,.]\d+)?[KkMm]?", cleaned) or re.fullmatch(
            r"\d+(?:[,.]\d+)?[KkMm]?\s+(?:comments?|reactions?|shares?)", cleaned, re.I
        ):
            continue
        cleaned = re.sub(r"\s*(?:…|\.\.\.)?\s*See more\s*$", "", cleaned, flags=re.I)
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
    raise FacebookScraperFailure(
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


def _is_navigation_timeout(exc: FacebookScraperFailure) -> bool:
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
