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

from . import agent_browser_runtime as browser_runtime, dates, log
from .relevance import token_overlap_relevance as _compute_relevance


DEPTH_CONFIG = {
    "quick": {"results": 8, "scrolls": 0, "timeout": 45},
    "default": {"results": 16, "scrolls": 1, "timeout": 75},
    "deep": {"results": 30, "scrolls": 2, "timeout": 120},
}

DEFAULT_MIN_ACTION_DELAY = 4.0
DEFAULT_MAX_ACTIONS_PER_MINUTE = 6
MAX_EXPLICIT_RESULTS = 100
MAX_EXPLICIT_SCROLLS = 8
ACCEPTED_ITEMS_PER_SCROLL_BUDGET = 5
MIN_EXPLICIT_FEED_SCROLLS = 8
MAX_EXPLICIT_FEED_SCROLLS = 32
FEED_SCROLLS_PER_FIVE_ITEMS = 4
MAX_FEED_STAGNANT_SCROLLS = 4
MIN_FEED_SCROLL_PIXELS = 1_400
FEED_SCROLL_PIXELS_PER_REQUIRED_ITEM = 800
MAX_FEED_SCROLL_PIXELS = 3_200

ERROR_TYPES = browser_runtime.ERROR_TYPES
BrowserWorkspaceRequest = browser_runtime.BrowserWorkspaceRequest
BrowserWorkspace = browser_runtime.BrowserWorkspace
BrowserSnapshot = browser_runtime.BrowserSnapshot
BrowserAction = browser_runtime.BrowserAction
BrowserState = browser_runtime.BrowserState
LinkedInScraperFailure = browser_runtime.AgentBrowserRuntimeFailure


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
    '[data-id^="urn:li:activity:"]',
    '.feed-shared-update-v2',
    'li.reusable-search__result-container',
    'main [role="listitem"]'
  ];
  const nodes = [];
  const nodeSet = new Set();
  const rootSelector = [
    '[data-view-name="feed-full-update"]',
    '[data-urn^="urn:li:activity:"]',
    '[data-id^="urn:li:activity:"]',
    '.feed-shared-update-v2',
    'li.reusable-search__result-container'
  ].join(', ');
  const addNode = (rawNode) => {
    const node = rawNode?.closest?.(rootSelector) || rawNode;
    if (!node || nodeSet.has(node)) return;
    if (nodes.some((existing) => existing.contains?.(node))) return;
    for (let index = nodes.length - 1; index >= 0; index -= 1) {
      if (node.contains?.(nodes[index])) {
        nodeSet.delete(nodes[index]);
        nodes.splice(index, 1);
      }
    }
    nodeSet.add(node);
    nodes.push(node);
  };
  for (const selector of selectors) {
    for (const node of main.querySelectorAll(selector)) {
      addNode(node);
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
  const urnFromValue = (value) => {
    if (!value) return "";
    let decoded = String(value);
    try {
      decoded = decodeURIComponent(decoded);
    } catch {
      // Malformed tracking values are ignored in favor of the raw value.
    }
    const urnMatch = decoded.match(/urn:li:activity:(\d+)/i);
    if (urnMatch) return `urn:li:activity:${urnMatch[1]}`;
    const slugMatch = decoded.match(/(?:^|[-_:])activity[-_:](\d{10,})(?:[-_/?#]|$)/i);
    return slugMatch ? `urn:li:activity:${slugMatch[1]}` : "";
  };
  const activityUrn = (node) => {
    const attributeNodes = [
      node,
      ...Array.from(node.querySelectorAll?.(
        '[data-urn], [data-id], [data-entity-urn], [data-view-tracking-scope], a[href]'
      ) || []).slice(0, 160)
    ];
    for (const element of attributeNodes) {
      const values = [
        element?.href,
        ...Array.from(element?.getAttributeNames?.() || []).slice(0, 40)
          .map((name) => element.getAttribute?.(name))
      ];
      for (const value of values) {
        const urn = urnFromValue(value);
        if (urn) return urn;
      }
    }
    const runtimeKeys = Object.keys(node);
    const groups = [
      runtimeKeys.filter((key) => key.startsWith("__reactProps")),
      runtimeKeys.filter((key) => key.startsWith("__reactFiber"))
    ];
    for (const keys of groups) {
      const queue = keys.map((key) => node[key]);
      const seen = new WeakSet();
      let cursor = 0;
      let steps = 0;
      while (cursor < queue.length && steps < 12000) {
        const value = queue[cursor++];
        steps += 1;
        if (typeof value === "string") {
          const urn = urnFromValue(value);
          if (urn) return urn;
          continue;
        }
        if ((!value || typeof value !== "object") && typeof value !== "function") continue;
        if (seen.has(value)) continue;
        seen.add(value);
        for (const key of Object.keys(value).slice(0, 120)) {
          if (key === "return" || key === "_owner") continue;
          try {
            queue.push(value[key]);
          } catch {
            // React runtime values may expose guarded accessors.
          }
        }
      }
    }
    return "";
  };
  const candidates = [];
  const seen = new Set();
  const timestampPattern = /(?:^|\b)(?:now|just now|\d+\s*(?:s|sec|second|m|min|minute|h|hr|hour|d|day|w|week|mo|month|y|yr|year)s?(?:\s+ago)?)(?:\s*[•·]|$)/i;
  for (const node of nodes) {
    const text = (node.innerText || node.textContent || "").trim();
    if (!text) continue;
    const anchors = Array.from(node.querySelectorAll('a[href]'));
    const permalink = anchors.find((anchor) =>
      /\/feed\/update\/urn:li:activity:\d+|\/posts\/[^/?#]+/i.test(
        (() => { try { return decodeURIComponent(anchor.href || ""); } catch { return anchor.href || ""; } })()
      )
    );
    const authorNode = node.querySelector(
      '.update-components-actor__title, .update-components-actor__name, '
      + '.feed-shared-actor__title, .feed-shared-actor__name, '
      + '[data-view-name="feed-actor-name"], [data-view-name*="actor-name"], '
      + '[data-view-name*="actor"] a[href]'
    ) || anchors.find((anchor) => /\/in\/|\/company\//.test(anchor.href || ""));
    const timeNode = node.querySelector(
      'time, [datetime], .update-components-actor__sub-description, '
      + '.feed-shared-actor__sub-description, [data-view-name*="actor"] [aria-label]'
    );
    const timestampText = (text.split("\n").map(clean).find((line) =>
      /^(?:now|just now|\d+\s*(?:s|m|h|d|w|mo)|\d+\s+(?:second|minute|hour|day|week|month)s?)(?:\s*•.*)?$/i.test(line)
    ) || "");
    const timestampAttribute = Array.from(node.querySelectorAll(
      'time, [datetime], [aria-label], [title], a[href]'
    )).slice(0, 160).flatMap((item) => [
      item.getAttribute?.('datetime'), item.getAttribute?.('aria-label'),
      item.getAttribute?.('title'), item.innerText, item.textContent
    ]).map(clean).find((value) => timestampPattern.test(value)) || "";
    const actionText = Array.from(node.querySelectorAll('button, [aria-label]'))
      .map((item) => `${item.getAttribute('aria-label') || ''} ${item.innerText || ''}`)
      .join(" ");
    const urn = urnFromValue(node.getAttribute('data-urn'))
      || urnFromValue(node.dataset?.urn)
      || activityUrn(node);
    const canonicalHref = permalink?.href || (urn
      ? `https://www.linkedin.com/feed/update/${urn}/`
      : "");
    const authorImage = authorNode?.querySelector?.('img[alt]');
    const author = clean(
      authorNode?.innerText || authorNode?.textContent
      || authorNode?.getAttribute?.('aria-label') || authorNode?.getAttribute?.('title')
      || authorImage?.alt || ""
    ).replace(/\s+(?:’s|'s)\s+profile picture$/i, "");
    const media = [
      ...Array.from(node.querySelectorAll(
        '.update-components-image img, .feed-shared-image img, img[src*="media.licdn.com"]'
      )).map((image) => ({
        kind: "image", url: image.currentSrc || image.src || "",
        preview_url: null, mime_type: null,
        width: image.naturalWidth || null, height: image.naturalHeight || null,
        duration_seconds: null, alt_text: image.alt || null
      })),
      ...Array.from(node.querySelectorAll("video")).map((video) => ({
        kind: "video", url: canonicalHref || location.href,
        preview_url: video.poster || null, mime_type: null,
        width: video.videoWidth || null, height: video.videoHeight || null,
        duration_seconds: Number.isFinite(video.duration) ? Math.round(video.duration) : null,
        alt_text: null
      }))
    ].filter((asset) => asset.url);
    const rootShape = node.matches?.(
      '[data-view-name="feed-full-update"], [data-urn^="urn:li:activity:"], '
      + '[data-id^="urn:li:activity:"], .feed-shared-update-v2'
    ) ? "feed_update" : node.matches?.('li.reusable-search__result-container')
      ? "search_result" : node.matches?.('[role="listitem"]')
        ? "listitem_fallback" : "unknown";
    const hasExternalLink = anchors.some((anchor) => {
      try {
        const host = new URL(anchor.href || "", location.href).hostname.toLowerCase();
        return Boolean(host) && host !== "linkedin.com" && host !== "www.linkedin.com";
      } catch {
        return false;
      }
    });
    const key = `${canonicalHref || urn}|${text.slice(0, 240)}`;
    if (seen.has(key)) continue;
    seen.add(key);
    candidates.push({
      text,
      url: canonicalHref,
      urn,
      author,
      author_url: authorNode?.href || authorNode?.closest?.('a[href]')?.href || "",
      timestamp: clean(
        timeNode?.getAttribute?.('datetime') ||
        timeNode?.getAttribute?.('aria-label') ||
        timeNode?.getAttribute?.('title') ||
        timeNode?.innerText || timeNode?.textContent || timestampText || timestampAttribute
      ),
      sponsored: /(^|\n)\s*(promoted|sponsored)\s*($|\n)/i.test(text),
      structural_evidence: {
        root_shape: rootShape,
        has_post_actions: /\b(?:like|react|comment|repost|send)\b/i.test(actionText),
        has_actor: Boolean(authorNode),
        has_timestamp: Boolean(timeNode || timestampText || timestampAttribute),
        has_media: media.length > 0,
        has_any_link: anchors.length > 0,
        has_external_link: hasExternalLink
      },
      engagement: {
        likes: count(`${actionText} ${text}`, ["reactions?", "likes?"]),
        comments: count(`${actionText} ${text}`, ["comments?"]),
        shares: count(`${actionText} ${text}`, ["reposts?", "shares?"])
      },
      media
    });
  }
  return {
    url: location.href, title: document.title, candidates,
    rate_limited: Boolean(rateLimitReason), rate_limit_reason: rateLimitReason
  };
})()
"""

PROFILE_STATE_SCRIPT = r"""
(() => {
  const body = String(document.body?.innerText || "").slice(0, 24000);
  return {
    url: location.href,
    title: document.title,
    login_page: Boolean(document.querySelector(
      'input[name="session_key"], input[name="session_password"], form.login__form'
    )) || /\/uas\/login/.test(location.pathname),
    checkpoint: /checkpoint|security verification|enter the code|verify your identity|challenge\//i.test(
      `${location.href} ${body}`
    ),
    error_page: /page not found|something went wrong|temporarily unavailable/i.test(body)
  };
})()
"""

PROFILE_EXTRACT_SCRIPT = r"""
(() => {
  const clean = (value) => String(value || "").replace(/\s+/g, " ").trim();
  const main = document.querySelector('main, [role="main"], .scaffold-layout__main');
  const section = (labels) => {
    for (const node of Array.from(main?.querySelectorAll('section') || [])) {
      const heading = clean(node.querySelector('h1,h2,h3,[role="heading"]')?.innerText);
      if (labels.some((label) => heading.toLowerCase().includes(label))) {
        return clean(node.innerText);
      }
    }
    return "";
  };
  const name = clean(main?.querySelector('h1')?.innerText);
  const headline = clean(main?.querySelector(
    '.text-body-medium, [data-generated-suggestion-target]'
  )?.innerText);
  return {
    url: location.href,
    display_name: name,
    headline,
    about: section(['about']),
    experience: section(['experience']),
    education: section(['education']),
    locations: clean(main?.querySelector('.text-body-small.inline')?.innerText),
    declared_links: Array.from(main?.querySelectorAll('a[href^="http"]') || [])
      .map((node) => node.href)
      .filter((href) => !/linkedin\.com/.test(href))
      .slice(0, 16)
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
    media: list[dict[str, Any]] = field(default_factory=list)
    rejection_reasons: list[str] = field(default_factory=list)


@dataclass
class LinkedInRunDiagnostics:
    candidate_counts: Counter[str] = field(default_factory=Counter)
    rejection_counts: Counter[str] = field(default_factory=Counter)
    accepted_count: int = 0
    duration_ms: int = 0
    failure_stage: str = "workspace_acquisition"
    scroll_count: int = 0
    unique_observation_count: int = 0
    stagnant_scrolls: int = 0
    failure_reason_code: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "candidate_counts": dict(self.candidate_counts),
            "rejection_counts": dict(self.rejection_counts),
            "accepted_count": self.accepted_count,
            "duration_ms": self.duration_ms,
            "scroll_count": self.scroll_count,
            "unique_observation_count": self.unique_observation_count,
            "stagnant_scrolls": self.stagnant_scrolls,
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
        return super().acquire_workspace(
            request,
            target_service_id="linkedin",
        )

    def inspect_auth(self, workspace: BrowserWorkspace) -> LinkedInAuthState:
        if not self.prepare_site_tab(workspace, "linkedin.com", consolidate=True):
            self.act(
                workspace,
                BrowserAction("new_tab", value="https://www.linkedin.com/feed/"),
            )
            self.act(workspace, BrowserAction("wait", value="2500"))
        raw = self.evaluate(workspace, AUTH_SCRIPT)
        auth = _auth_state(raw)
        if not (auth.authenticated or auth.login_form or auth.checkpoint):
            self.act(
                workspace,
                BrowserAction("navigate", value="https://www.linkedin.com/feed/"),
            )
            self.act(workspace, BrowserAction("wait", value="2500"))
            auth = _auth_state(self.evaluate(workspace, AUTH_SCRIPT))
        return auth

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


def _auth_state(raw: dict[str, Any]) -> LinkedInAuthState:
    return LinkedInAuthState(
        authenticated=bool(raw.get("authenticated_dom")),
        login_form=bool(raw.get("login_form")),
        checkpoint=bool(raw.get("checkpoint")),
        has_li_at=bool(raw.get("has_li_at")),
        url=str(raw.get("url") or ""),
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
        self._surface_kind = "topic"

    def search(self, topic: str, from_date: str, to_date: str) -> dict[str, Any]:
        started = time.monotonic()
        self._topic = topic
        self._surface_kind = "topic"
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
            diagnostics.failure_stage = "authentication"
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
            if auth.login_form:
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
            if not auth.authenticated:
                raise LinkedInScraperFailure(
                    "auth_state_ambiguous",
                    "LinkedIn authentication state could not be determined from the rendered page",
                    operator_url=workspace.operator_url,
                )

            diagnostics.failure_stage = "navigation"
            page = self._navigate(workspace, topic)
            if page.no_results:
                diagnostics.duration_ms = _elapsed_ms(started)
                return self._result([], None, None, workspace, page, diagnostics, from_date, to_date)
            if self.initial_wait:
                time.sleep(self.initial_wait)
            diagnostics.failure_stage = "extraction"
            raw_candidates = self._extract(workspace)
            for _ in range(max(0, self.scrolls)):
                if self._accepted_unique_count(
                    raw_candidates, topic, from_date, to_date
                ) >= self.limit:
                    break
                self._act(workspace, BrowserAction("scroll", value="1400"))
                if self.scroll_wait:
                    time.sleep(self.scroll_wait)
                raw_candidates.extend(self._extract(workspace))
            if not raw_candidates:
                raise LinkedInScraperFailure(
                    "extraction_empty", "Verified LinkedIn content search contained no candidate cards"
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
            diagnostics.failure_reason_code = exc.reason_code
            _log(f"Failed stage error_type={exc.error_type} message={exc}")
            return self._result(
                [], exc.error_type, str(exc), workspace, page, diagnostics, from_date, to_date,
                operator_url=exc.operator_url,
            )

    def feed(self, from_date: str, to_date: str) -> dict[str, Any]:
        """Collect structurally valid posts from the authenticated home feed."""
        started = time.monotonic()
        self._topic = ""
        self._surface_kind = "feed"
        diagnostics = LinkedInRunDiagnostics()
        workspace: BrowserWorkspace | None = None
        page = LinkedInPageState(url="", title="")
        try:
            _log(f"Acquiring agent-browser workspace profile={self.request.profile_id!r}")
            workspace = self.client.acquire_workspace(self.request)
            diagnostics.failure_stage = "authentication"
            auth = self.client.inspect_auth(workspace)
            if auth.checkpoint:
                raise LinkedInScraperFailure(
                    "checkpoint_required",
                    "LinkedIn requires an operator security-verification checkpoint",
                    operator_url=workspace.operator_url,
                )
            if auth.login_form:
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
            if not auth.authenticated:
                raise LinkedInScraperFailure(
                    "auth_state_ambiguous",
                    "LinkedIn authentication state could not be determined from the rendered page",
                    operator_url=workspace.operator_url,
                )
            diagnostics.failure_stage = "navigation"
            page = self._navigate_feed(workspace)
            if self.initial_wait:
                time.sleep(self.initial_wait)
            diagnostics.failure_stage = "extraction"
            raw_candidates = self._extract(workspace)
            seen_observations = {
                _candidate_observation_key(item) for item in raw_candidates
            }
            diagnostics.unique_observation_count = len(seen_observations)
            stagnant_scrolls = 0
            scroll_pixels = MIN_FEED_SCROLL_PIXELS
            for scroll_index in range(max(0, self.scrolls)):
                accepted_before = self._accepted_unique_count(
                    raw_candidates,
                    "",
                    from_date,
                    to_date,
                    surface_kind="feed",
                )
                if accepted_before >= self.limit:
                    break
                remaining_scrolls = max(1, self.scrolls - scroll_index)
                required_items_per_scroll = max(
                    1,
                    (
                        self.limit
                        - accepted_before
                        + remaining_scrolls
                        - 1
                    )
                    // remaining_scrolls,
                )
                scroll_pixels = max(
                    scroll_pixels,
                    min(
                        MAX_FEED_SCROLL_PIXELS,
                        max(
                            MIN_FEED_SCROLL_PIXELS,
                            required_items_per_scroll
                            * FEED_SCROLL_PIXELS_PER_REQUIRED_ITEM,
                        ),
                    ),
                )
                self._act(
                    workspace,
                    BrowserAction("scroll", value=str(scroll_pixels)),
                )
                diagnostics.scroll_count += 1
                if self.scroll_wait:
                    time.sleep(self.scroll_wait)
                batch = self._extract(workspace)
                new_observations = {
                    _candidate_observation_key(item) for item in batch
                } - seen_observations
                seen_observations.update(new_observations)
                raw_candidates.extend(batch)
                stagnant_scrolls = 0 if new_observations else stagnant_scrolls + 1
                diagnostics.unique_observation_count = len(seen_observations)
                diagnostics.stagnant_scrolls = stagnant_scrolls
                if stagnant_scrolls >= MAX_FEED_STAGNANT_SCROLLS:
                    break
            if not raw_candidates:
                raise LinkedInScraperFailure(
                    "extraction_empty", "Verified LinkedIn home feed contained no candidate cards"
                )
            diagnostics.failure_stage = "quality_gate"
            items = self._quality_gate(
                raw_candidates,
                "",
                from_date,
                to_date,
                diagnostics,
                surface_kind="feed",
            )
            diagnostics.duration_ms = _elapsed_ms(started)
            if not items:
                return self._result(
                    [],
                    "quality_gate_failed",
                    "LinkedIn feed candidates were found, but none passed the post quality gate",
                    workspace,
                    page,
                    diagnostics,
                    from_date,
                    to_date,
                )
            return self._result(items, None, None, workspace, page, diagnostics, from_date, to_date)
        except LinkedInScraperFailure as exc:
            diagnostics.duration_ms = _elapsed_ms(started)
            diagnostics.failure_reason_code = exc.reason_code
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

    def _navigate_feed(self, workspace: BrowserWorkspace) -> LinkedInPageState:
        feed_url = "https://www.linkedin.com/feed/"
        prepare_site_tab = getattr(self.client, "prepare_site_tab", None)
        retained_tab = bool(
            callable(prepare_site_tab)
            and prepare_site_tab(workspace, "linkedin.com", consolidate=True)
        )
        operation = "navigate" if retained_tab else "new_tab"
        _log(f"Navigating feed strategy={'reuse_tab' if retained_tab else 'new_tab'}")
        self._act(workspace, BrowserAction(operation, value=feed_url))
        self.client.act(workspace, BrowserAction("wait", value="2500"))
        page = _page_state(self.client.evaluate(workspace, PAGE_STATE_SCRIPT))
        if page.rate_limited:
            raise LinkedInScraperFailure(
                "rate_limit_detected",
                f"LinkedIn warning detected ({page.rate_limit_reason or 'unspecified'}); stopping",
                operator_url=workspace.operator_url,
            )
        if page.checkpoint:
            raise LinkedInScraperFailure(
                "checkpoint_required", "LinkedIn checkpoint appeared during feed navigation",
                operator_url=workspace.operator_url,
            )
        if page.login_page:
            raise LinkedInScraperFailure(
                "auth_required", "LinkedIn session became logged out during feed navigation",
                operator_url=workspace.operator_url,
            )
        if page.error_page:
            raise LinkedInScraperFailure("search_unavailable", "LinkedIn returned an error page")
        if not _page_matches_feed(page):
            raise LinkedInScraperFailure(
                "navigation_mismatch",
                f"LinkedIn final page does not match the authenticated home feed: {page.url}",
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

    def _accepted_unique_count(
        self,
        raw_candidates: list[dict[str, Any]],
        topic: str,
        from_date: str,
        to_date: str,
        *,
        surface_kind: str = "topic",
    ) -> int:
        """Preview accepted unique yield without mutating run diagnostics."""
        return len(
            self._quality_gate(
                raw_candidates,
                topic,
                from_date,
                to_date,
                LinkedInRunDiagnostics(),
                surface_kind=surface_kind,
            )
        )

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
        *,
        surface_kind: str = "topic",
    ) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        seen: set[str] = set()
        for raw in raw_candidates:
            candidate = _candidate_from_raw(raw, self.now)
            diagnostics.candidate_counts[candidate.kind] += 1
            _validate_candidate(
                candidate,
                from_date,
                to_date,
                surface_kind=surface_kind,
            )
            if candidate.rejection_reasons:
                diagnostics.candidate_counts["rejected"] += 1
                diagnostics.rejection_counts.update(candidate.rejection_reasons)
                if "missing_permalink" in candidate.rejection_reasons:
                    _record_missing_permalink_structure(diagnostics, raw)
                continue
            digest = hashlib.sha1(
                candidate.canonical_url.encode("utf-8")
            ).hexdigest()[:16]
            if digest in seen:
                diagnostics.rejection_counts["duplicate"] += 1
                continue
            seen.add(digest)
            relevance = (
                _compute_relevance(topic, candidate.text)
                if surface_kind == "topic"
                else 0.5
            )
            meaningful = re.sub(r"\W+", "", candidate.text, flags=re.UNICODE)
            retrieval_signals: list[str] = []
            if not candidate.author:
                retrieval_signals.append("missing_author")
            if not candidate.published_at or candidate.date_confidence == "low":
                retrieval_signals.append("missing_date")
            if len(meaningful) < 30:
                retrieval_signals.append("short_text")
            if surface_kind == "topic" and relevance <= 0:
                retrieval_signals.append("no_lexical_topic_overlap")
            items.append({
                "id": f"LI{digest}",
                "text": candidate.text,
                "url": candidate.canonical_url,
                "author": candidate.author,
                "date": candidate.published_at,
                "engagement": candidate.engagement,
                "relevance": round(relevance, 2),
                "why_relevant": (
                    f"LinkedIn post: {candidate.text[:80]}"
                    if surface_kind == "topic"
                    else "Authenticated LinkedIn home feed post"
                ),
                "metadata": {
                    "extraction": "agent-browser-dom-v1",
                    "remote_browser": True,
                    "date_confidence": candidate.date_confidence,
                    "retrieval_signals": retrieval_signals,
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
        diagnostics_data = diagnostics.as_dict()
        if error_type:
            diagnostics_data["failure_stage"] = diagnostics.failure_stage
            if diagnostics.failure_reason_code:
                diagnostics_data["failure_reason_code"] = diagnostics.failure_reason_code
            diagnostics_data["browser_operations"] = _bounded_browser_operations(
                getattr(self.client, "command_timings", [])
            )
        result: dict[str, Any] = {
            "items": items,
            "error": error,
            "error_type": error_type,
            "url": page.url,
            "title": page.title,
            "profile": self.request.profile_id,
            "session": self.request.session_name,
            "workspace": workspace_data,
            "diagnostics": diagnostics_data,
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
            "query": self._topic or None,
            "surface_kind": self._surface_kind,
            "requested_url": (
                _search_url(self._topic)
                if self._surface_kind == "topic"
                else "https://www.linkedin.com/feed/"
            ),
            "final_url": page.url,
            "profile": self.request.profile_id,
            "session": self.request.session_name,
            "workspace": result.get("workspace") or {},
            "error_type": result.get("error_type"),
            "page_assertions": {
                "query_matches": (
                    _page_matches_query(page, self._topic)
                    if page.url and self._surface_kind == "topic"
                    else None
                ),
                "feed_matches": (
                    _page_matches_feed(page)
                    if page.url and self._surface_kind == "feed"
                    else None
                ),
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
    limit: int | None = None,
) -> dict[str, Any]:
    """Search LinkedIn and return structurally verified content posts."""
    config = config or {}
    if not is_agent_browser_available():
        return {
            "items": [],
            "error": "agent-browser command is not on PATH",
            "error_type": "agent_browser_missing",
        }
    settings = DEPTH_CONFIG.get(depth, DEPTH_CONFIG["default"])
    result_limit = int(
        config.get("LAST30DAYS_LINKEDIN_MAX_RESULTS") or settings["results"]
    )
    if limit is not None:
        result_limit = max(1, min(MAX_EXPLICIT_RESULTS, int(limit)))
    scrolls = int(config.get("LAST30DAYS_LINKEDIN_SCROLLS") or settings["scrolls"])
    if limit is not None:
        scrolls = max(
            scrolls,
            min(
                MAX_EXPLICIT_SCROLLS,
                (result_limit + ACCEPTED_ITEMS_PER_SCROLL_BUDGET - 1)
                // ACCEPTED_ITEMS_PER_SCROLL_BUDGET,
            ),
        )
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
        start_url="https://www.linkedin.com/feed/",
        agent_name="linkedin-scraper",
        task_name="linkedin-content-search",
        target_service_id="linkedin",
        display_isolation=str(
            config.get("LAST30DAYS_AGENT_BROWSER_DISPLAY_ISOLATION")
            or "shared_display"
        ),
    )
    scraper = LinkedInScraper(
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
        limit=result_limit,
        scrolls=scrolls,
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


def scrape_linkedin_feed(
    from_date: str,
    to_date: str,
    *,
    depth: str = "default",
    config: dict[str, Any] | None = None,
    limit: int | None = None,
) -> dict[str, Any]:
    """Scrape the authenticated LinkedIn home feed without a topic query."""
    config = config or {}
    if not is_agent_browser_available():
        return {
            "items": [],
            "error": "agent-browser command is not on PATH",
            "error_type": "agent_browser_missing",
        }
    settings = DEPTH_CONFIG.get(depth, DEPTH_CONFIG["default"])
    result_limit = int(
        config.get("LAST30DAYS_LINKEDIN_MAX_RESULTS") or settings["results"]
    )
    if limit is not None:
        result_limit = max(1, min(MAX_EXPLICIT_RESULTS, int(limit)))
    scrolls = int(config.get("LAST30DAYS_LINKEDIN_SCROLLS") or settings["scrolls"])
    if limit is not None:
        scrolls = max(
            scrolls,
            min(
                MAX_EXPLICIT_FEED_SCROLLS,
                max(
                    MIN_EXPLICIT_FEED_SCROLLS,
                    (
                        result_limit * FEED_SCROLLS_PER_FIVE_ITEMS
                        + ACCEPTED_ITEMS_PER_SCROLL_BUDGET
                        - 1
                    )
                    // ACCEPTED_ITEMS_PER_SCROLL_BUDGET,
                ),
            ),
        )
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
        start_url="https://www.linkedin.com/feed/",
        agent_name="linkedin-scraper",
        task_name="linkedin-home-feed",
        target_service_id="linkedin",
        display_isolation=str(
            config.get("LAST30DAYS_AGENT_BROWSER_DISPLAY_ISOLATION") or "shared_display"
        ),
    )
    client = CliAgentBrowserClient(
        timeout=timeout,
        **(
            {"job_timeout_ms": int(config["LAST30DAYS_AGENT_BROWSER_JOB_TIMEOUT_MS"])}
            if config.get("LAST30DAYS_AGENT_BROWSER_JOB_TIMEOUT_MS")
            else {}
        ),
    )
    scraper = LinkedInScraper(
        client,
        request,
        limit=result_limit,
        scrolls=scrolls,
        initial_wait=float(config.get("LAST30DAYS_LINKEDIN_INITIAL_WAIT") or 4.0),
        scroll_wait=float(config.get("LAST30DAYS_LINKEDIN_SCROLL_WAIT") or 2.0),
        interaction_limiter=_interaction_limiter(
            request.session_name,
            min_action_delay,
            max_actions_per_minute,
        ),
        debug_dir=str(config.get("LAST30DAYS_LINKEDIN_DEBUG_DIR") or "").strip(),
    )
    try:
        return scraper.feed(from_date, to_date)
    finally:
        try:
            client.release_workspace()
        except browser_runtime.AgentBrowserRuntimeFailure as exc:
            _log(f"Best-effort LinkedIn service tab release did not complete: {exc}")


def acquire_linkedin_profile(
    canonical_url: str,
    *,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Acquire one exact people/company profile without adjacent private surfaces."""
    config = config or {}
    parsed = urlsplit(canonical_url.strip())
    match = re.fullmatch(r"/(in|company)/([A-Za-z0-9_.%-]+)/?", parsed.path)
    if (
        parsed.scheme not in {"http", "https"}
        or (parsed.hostname or "").casefold()
        not in {"linkedin.com", "www.linkedin.com"}
        or match is None
        or parsed.query
        or parsed.fragment
    ):
        return {
            "items": [],
            "error": "an exact LinkedIn people or company URL is required",
            "error_type": "invalid_request",
        }
    if not is_agent_browser_available():
        return {
            "items": [],
            "error": "agent-browser command is not on PATH",
            "error_type": "agent_browser_missing",
        }
    canonical = urlunsplit(
        ("https", "www.linkedin.com", f"/{match.group(1)}/{match.group(2)}/", "", "")
    )
    timeout = int(config.get("LAST30DAYS_LINKEDIN_TIMEOUT") or 75)
    request = BrowserWorkspaceRequest(
        profile_id=str(
            config.get("LAST30DAYS_LINKEDIN_PROFILE") or "last30days-linkedin"
        ),
        session_name=str(
            config.get("LAST30DAYS_LINKEDIN_SESSION") or "last30days-linkedin"
        ),
        browser_build=str(
            config.get("LAST30DAYS_LINKEDIN_BROWSER_BUILD")
            or "stealthcdp_chromium"
        ),
        view_provider=str(
            config.get("LAST30DAYS_LINKEDIN_VIEW_PROVIDER") or "rdp_gateway"
        ),
        timeout=timeout,
        browser_id_hint=str(
            config.get("LAST30DAYS_LINKEDIN_BROWSER_ID") or ""
        ).strip(),
        route_id_hint=str(config.get("LAST30DAYS_LINKEDIN_ROUTE_ID") or "").strip(),
        route_pool_entry_id_hint=str(
            config.get("LAST30DAYS_LINKEDIN_ROUTE_POOL_ENTRY_ID") or ""
        ).strip(),
        start_url=canonical,
        agent_name="linkedin-profile-scraper",
        task_name="linkedin-profile-acquisition",
        target_service_id="linkedin",
        display_isolation=str(
            config.get("LAST30DAYS_AGENT_BROWSER_DISPLAY_ISOLATION")
            or "shared_display"
        ),
    )
    client = CliAgentBrowserClient(
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
    )
    try:
        workspace = client.acquire_workspace(request)
        auth = client.inspect_auth(workspace)
        if auth.checkpoint:
            raise LinkedInScraperFailure(
                "checkpoint_required",
                "LinkedIn requires an operator security-verification checkpoint",
                operator_url=workspace.operator_url,
            )
        if not auth.authenticated:
            raise LinkedInScraperFailure(
                "auth_required",
                "LinkedIn authentication is required in the retained profile",
                operator_url=workspace.operator_url,
            )
        prepare = getattr(client, "prepare_site_tab", None)
        retained = bool(
            callable(prepare) and prepare(workspace, "linkedin.com", consolidate=True)
        )
        client.act(
            workspace,
            BrowserAction("navigate" if retained else "new_tab", value=canonical),
        )
        client.act(workspace, BrowserAction("wait", value="2000"))
        state = client.evaluate(workspace, PROFILE_STATE_SCRIPT)
        if state.get("checkpoint"):
            raise LinkedInScraperFailure(
                "checkpoint_required",
                "LinkedIn checkpoint appeared during profile acquisition",
                operator_url=workspace.operator_url,
            )
        if state.get("login_page"):
            raise LinkedInScraperFailure(
                "auth_required",
                "LinkedIn session became logged out",
                operator_url=workspace.operator_url,
            )
        if state.get("error_page"):
            raise LinkedInScraperFailure("profile_unavailable", "Profile is unavailable")
        final = urlsplit(str(state.get("url") or ""))
        if final.path.rstrip("/") != urlsplit(canonical).path.rstrip("/"):
            raise LinkedInScraperFailure(
                "navigation_mismatch", "LinkedIn final page does not match the profile"
            )
        extracted = client.evaluate(workspace, PROFILE_EXTRACT_SCRIPT)
        display_name = re.sub(
            r"\s+", " ", str(extracted.get("display_name") or "")
        ).strip()
        sections = []
        text_parts = [display_name]
        for kind in ("headline", "about", "experience", "education", "locations"):
            text = re.sub(r"\s+", " ", str(extracted.get(kind) or "")).strip()
            sections.append(
                {
                    "section_kind": kind,
                    "ordinal": 0,
                    "text": text,
                    "presence_state": "visible" if text else "not_observed",
                    "visibility": "visible" if text else "unknown",
                }
            )
            if text:
                text_parts.append(text)
        if not display_name or len(" ".join(text_parts)) < 10:
            raise LinkedInScraperFailure(
                "extraction_empty", "LinkedIn profile contained no usable evidence"
            )
        return {
            "items": [
                {
                    "source_native_id": match.group(2),
                    "url": canonical,
                    "title": display_name,
                    "text": "\n".join(text_parts),
                    "author": display_name,
                    "metadata": {
                        "surface_kind": "profile",
                        "account_kind": (
                            "person" if match.group(1) == "in" else "organization"
                        ),
                        "handle": match.group(2),
                        "sections": sections,
                        "declared_links": [
                            str(item)
                            for item in extracted.get("declared_links", [])
                            if isinstance(item, str)
                        ][:16],
                    },
                }
            ],
            "error": None,
            "diagnostics": {"surface_kind": "profile", "section_count": len(sections)},
        }
    except LinkedInScraperFailure as exc:
        return {
            "items": [],
            "error": str(exc),
            "error_type": exc.error_type,
            "operator_url": exc.operator_url,
        }


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


def _page_matches_feed(page: LinkedInPageState) -> bool:
    parsed = urlsplit(page.url)
    return (
        (parsed.hostname or "").lower() in {"linkedin.com", "www.linkedin.com"}
        and parsed.path.rstrip("/") == "/feed"
        and not page.login_page
        and not page.checkpoint
        and not page.rate_limited
        and not page.error_page
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
        media=[
            item
            for item in list(raw.get("media") or [])[:16]
            if isinstance(item, dict) and _is_post_owned_media(item)
        ],
    )


def _is_post_owned_media(item: dict[str, Any]) -> bool:
    """Reject deterministic LinkedIn identity chrome from post media."""
    references = (item.get("url"), item.get("preview_url"))
    for reference in references:
        if not isinstance(reference, str) or not reference.strip():
            continue
        path = urlsplit(reference).path.casefold()
        if any(
            chrome_marker in path
            for chrome_marker in (
                "profile-displayphoto",
                "company-logo",
                "group-logo",
            )
        ):
            return False
    return True


def _candidate_observation_key(candidate: dict[str, Any]) -> str:
    """Identify one rendered post across overlapping virtualized snapshots."""
    canonical_url = _canonical_post_url(
        str(candidate.get("url") or ""), str(candidate.get("urn") or "")
    )
    if canonical_url:
        return canonical_url
    return "\n".join(
        (
            str(candidate.get("author") or candidate.get("author_url") or "")
            .casefold()
            .strip(),
            str(candidate.get("timestamp") or "").strip(),
            re.sub(r"\s+", " ", str(candidate.get("text") or "")).casefold()[:500],
        )
    )


def _validate_candidate(
    candidate: LinkedInCandidate,
    from_date: str,
    to_date: str,
    *,
    surface_kind: str = "topic",
) -> None:
    if candidate.kind != "post":
        candidate.rejection_reasons.append(f"kind_{candidate.kind}")
    if not candidate.canonical_url:
        candidate.rejection_reasons.append("missing_permalink")
    if _is_composer_chrome(candidate.text):
        candidate.rejection_reasons.append("composer_chrome")
    if _is_sort_control_chrome(candidate.text):
        candidate.rejection_reasons.append("sort_control_chrome")
    if _is_noise_text(candidate.text):
        candidate.rejection_reasons.append("navigation_noise")
    if not candidate.author and surface_kind == "topic":
        candidate.rejection_reasons.append("missing_author")
    if not candidate.published_at or candidate.date_confidence == "low":
        if surface_kind == "topic":
            candidate.rejection_reasons.append("missing_date")
    elif dates.get_date_confidence(candidate.published_at, from_date, to_date) != "high":
        candidate.rejection_reasons.append("outside_date_range")
    if candidate.sponsored:
        candidate.rejection_reasons.append("sponsored")


def _record_missing_permalink_structure(
    diagnostics: LinkedInRunDiagnostics,
    raw: dict[str, Any],
) -> None:
    """Persist only bounded structural counters for rejected feed cards."""
    evidence = raw.get("structural_evidence")
    if not isinstance(evidence, dict):
        diagnostics.rejection_counts["missing_permalink_structure_unavailable"] += 1
        return
    root_shape = evidence.get("root_shape")
    if root_shape in {"feed_update", "search_result", "listitem_fallback", "unknown"}:
        diagnostics.rejection_counts[f"missing_permalink_root_{root_shape}"] += 1
    else:
        diagnostics.rejection_counts["missing_permalink_root_unknown"] += 1
    for signal in (
        "has_post_actions",
        "has_actor",
        "has_timestamp",
        "has_media",
        "has_any_link",
        "has_external_link",
    ):
        if evidence.get(signal) is True:
            diagnostics.rejection_counts[f"missing_permalink_{signal}"] += 1


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


def _is_composer_chrome(value: str) -> bool:
    """Reject LinkedIn's post-composer controls when surfaced as a feed card."""
    lines = tuple(
        re.sub(r"\s+", " ", line).casefold().strip()
        for line in value.splitlines()
        if line.strip()
    )
    return lines == ("start a post", "video", "photo", "write article")


def _is_sort_control_chrome(value: str) -> bool:
    """Reject LinkedIn comment-sort controls inherited by an activity link."""
    normalized = re.sub(r"\s+", " ", value).casefold().strip()
    return normalized in {
        "sort by: top",
        "sort by: most relevant",
        "sort by: recent",
    }


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


def _bounded_browser_operations(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    operations: list[dict[str, Any]] = []
    for item in value[-20:]:
        if not isinstance(item, dict):
            continue
        operation = str(item.get("operation") or "").strip()[:64]
        status = str(item.get("status") or "").strip()[:32]
        duration = item.get("duration_ms")
        if (
            not operation
            or not status
            or isinstance(duration, bool)
            or not isinstance(duration, int)
            or duration < 0
        ):
            continue
        operations.append(
            {
                "operation": operation,
                "duration_ms": duration,
                "status": status,
            }
        )
    return operations


def _elapsed_ms(started: float) -> int:
    return max(0, round((time.monotonic() - started) * 1000))
