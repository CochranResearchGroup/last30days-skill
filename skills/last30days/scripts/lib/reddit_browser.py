"""Bounded Reddit post discovery through the installed agent-browser service."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
import re
import shutil
import time
from typing import Any, Protocol
from urllib.parse import parse_qs, quote_plus, unquote, urlsplit, urlunsplit

from . import agent_browser_runtime as browser_runtime
from . import log
from .relevance import query_term_coverage, token_overlap_relevance


DEPTH_CONFIG = {
    "quick": {"results": 3, "scrolls": 0, "timeout": 45},
    "default": {"results": 10, "scrolls": 1, "timeout": 75},
    "deep": {"results": 20, "scrolls": 2, "timeout": 110},
}
DOM_SHAPES = frozenset({"search-post-unit", "shreddit-post", "article-permalink"})
MAX_EXPLICIT_RESULTS = 100
MAX_EXPLICIT_FEED_SCROLLS = 40
FEED_ACCEPTED_ITEMS_PER_SCROLL_BUDGET = 2
MAX_STAGNANT_SCROLLS = 3

BrowserWorkspaceRequest = browser_runtime.BrowserWorkspaceRequest
BrowserWorkspace = browser_runtime.BrowserWorkspace
BrowserAction = browser_runtime.BrowserAction
BrowserState = browser_runtime.BrowserState


class RedditBrowserFailure(RuntimeError):
    """Typed terminal failure at the Reddit browser adapter seam."""

    def __init__(self, error_type: str, message: str) -> None:
        super().__init__(message)
        self.error_type = error_type


AUTH_SCRIPT = r"""
(() => {
  const body = (document.body?.innerText || '').slice(0, 12000);
  const cookieNames = new Set(
    document.cookie.split(';').map(part => part.split('=', 1)[0].trim())
  );
  const loginForm = Boolean(document.querySelector(
    'form[action*="/login"], input[name="username"], input[name="password"]'
  ));
  const userMenu = Boolean(document.querySelector(
    '#expand-user-drawer-button, [data-testid="user-drawer-button"], '
      + 'button[aria-label*="user menu" i], faceplate-tracker[noun="user_menu"]'
  ));
  const checkpoint = /(?:captcha|security check|verify you are human)/i.test(
    `${location.href}\n${body}`
  );
  return {
    authenticated: (userMenu || cookieNames.has('reddit_session')) && !loginForm && !checkpoint,
    login_form: loginForm || /\/login\/?(?:[?#]|$)/i.test(location.pathname),
    checkpoint,
  };
})()
"""


PAGE_STATE_SCRIPT = r"""
(() => {
  const text = (document.body?.innerText || '').slice(0, 20000);
  const lower = text.toLowerCase();
  const url = location.href;
  const search = new URL(url).searchParams;
  const hasPosts = Boolean(document.querySelector('shreddit-post, [data-testid="search-post-unit"], article a[href*="/comments/"]'));
  return {
    url,
    title: document.title || '',
    query_value: search.get('q') || '',
    has_posts: hasPosts,
    no_results: /(?:hm\.\.\. we couldn.t find any results|no results)/i.test(text),
    login_page: /\/login\/?(?:[?#]|$)/i.test(location.pathname),
    checkpoint: /(?:captcha|security check|verify you are human)/i.test(lower),
    rate_limited: /(?:whoa there, pardner|you.re doing that too much|too many requests)/i.test(lower),
    rate_limit_reason: lower.includes('whoa there, pardner') ? 'whoa_there' : '',
    error_page: /(?:something went wrong|our cdn was unable|upstream connect error)/i.test(lower),
    interstitial: !hasPosts && /(?:before you continue to reddit|review your privacy choices|consent to continue)/i.test(lower),
  };
})()
"""


EXTRACT_SCRIPT = r"""
(() => {
  const candidates = [];
  const seen = new Set();
  const clean = value => String(value || '').replace(/\s+/g, ' ').trim();
  for (const post of document.querySelectorAll('shreddit-post, [data-testid="search-post-unit"]')) {
    const anchor = post.querySelector('a[data-testid="post-title-text"][href*="/comments/"], a[data-testid="post-title"][href*="/comments/"], a[href*="/comments/"]');
    const permalink = post.getAttribute('permalink') || anchor?.getAttribute('href') || '';
    if (!permalink || seen.has(permalink)) continue;
    seen.add(permalink);
    let context = {};
    const tracker = post.querySelector('search-telemetry-tracker[data-faceplate-tracking-context]');
    try { context = JSON.parse(tracker?.getAttribute('data-faceplate-tracking-context') || '{}'); } catch (_) {}
    const title = post.getAttribute('post-title') || anchor?.getAttribute('aria-label') || anchor?.textContent || context?.post?.title || '';
    const body = post.querySelector('[slot="text-body"], [slot="post-body"], shreddit-post-text-body');
    const counters = [...post.querySelectorAll('[data-testid="search-counter-row"] faceplate-number')];
    const created = post.getAttribute('created-timestamp') || post.querySelector('time[datetime]')?.getAttribute('datetime') || '';
    const promoted = post.hasAttribute('promoted') ||
      post.getAttribute('data-promoted') === 'true' ||
      Boolean(post.querySelector('[aria-label*="promoted" i], [data-testid*="promoted" i]')) ||
      context?.post?.isPromoted === true;
    const platformNotice = post.querySelector(
      '[slot*="removed" i], [data-testid*="removed" i], shreddit-status-message'
    );
    const platformSpam = context?.post?.isSpam === true ||
      context?.post?.spam === true ||
      /(?:this post was |post )?removed by reddit(?:'s|’s) filters/i.test(
        clean(platformNotice?.innerText || platformNotice?.textContent || '')
      );
    const dom_shape = post.matches('shreddit-post') ? 'shreddit-post' : 'search-post-unit';
    const crosspost = post.hasAttribute('is-crosspost') ||
      post.getAttribute('post-type') === 'crosspost' ||
      Boolean(post.querySelector('shreddit-post[slot="crosspost"], [data-testid*="crosspost" i]'));
    candidates.push({
      title: clean(title),
      text: clean(body?.innerText || ''),
      permalink,
      author: clean(post.getAttribute('author') || context?.profile?.name || ''),
      subreddit: clean(post.getAttribute('subreddit-prefixed-name') || context?.subreddit?.name || ''),
      created_at: clean(created),
      score: clean(post.getAttribute('score') || counters[0]?.getAttribute('number') || ''),
      comment_count: clean(post.getAttribute('comment-count') || counters[1]?.getAttribute('number') || ''),
      promoted,
      platform_spam: platformSpam,
      dom_shape,
      crosspost,
    });
  }
  if (!candidates.length) {
    for (const article of document.querySelectorAll('article')) {
      const anchor = article.querySelector('a[href*="/comments/"]');
      const permalink = anchor?.getAttribute('href') || '';
      if (!permalink || seen.has(permalink)) continue;
      seen.add(permalink);
      const time = article.querySelector('time');
      candidates.push({
        title: clean(anchor?.textContent || article.querySelector('h1,h2,h3')?.textContent || ''),
        text: clean(article.innerText || ''),
        permalink,
        author: '',
        subreddit: '',
        created_at: clean(time?.getAttribute('datetime') || ''),
        score: '',
        comment_count: '',
        promoted: /(?:^|\s)promoted(?:\s|$)/i.test(clean(article.innerText || '')),
        platform_spam: false,
        dom_shape: 'article-permalink',
        crosspost: false,
      });
    }
  }
  return {candidates: candidates.slice(0, 80)};
})()
"""


@dataclass(frozen=True)
class RedditPageState:
    url: str
    title: str
    query_value: str = ""
    has_posts: bool = False
    no_results: bool = False
    login_page: bool = False
    checkpoint: bool = False
    rate_limited: bool = False
    rate_limit_reason: str = ""
    error_page: bool = False
    interstitial: bool = False


@dataclass(frozen=True)
class RedditAuthState:
    authenticated: bool = False
    login_form: bool = False
    checkpoint: bool = False


@dataclass
class RedditDiagnostics:
    rejection_counts: Counter[str] = field(default_factory=Counter)
    limitation_counts: Counter[str] = field(default_factory=Counter)
    scope_exclusion_counts: Counter[str] = field(default_factory=Counter)
    duplicate_count: int = 0
    accepted_count: int = 0
    candidate_count: int = 0
    duration_ms: int = 0
    failure_stage: str = "workspace_acquisition"
    verified_no_results: bool = False
    scroll_count: int = 0
    stagnant_scrolls: int = 0
    unique_observation_count: int = 0
    stop_reason: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "candidate_count": self.candidate_count,
            "rejection_counts": dict(self.rejection_counts),
            "limitation_counts": dict(self.limitation_counts),
            "scope_exclusion_counts": dict(self.scope_exclusion_counts),
            "duplicate_count": self.duplicate_count,
            "accepted_count": self.accepted_count,
            "duration_ms": self.duration_ms,
            "verified_no_results": self.verified_no_results,
            "scroll_count": self.scroll_count,
            "stagnant_scrolls": self.stagnant_scrolls,
            "unique_observation_count": self.unique_observation_count,
            "stop_reason": self.stop_reason,
        }


class AgentBrowserClient(Protocol):
    def acquire_workspace(self, request: BrowserWorkspaceRequest) -> BrowserWorkspace: ...
    def inspect_auth(self, workspace: BrowserWorkspace) -> RedditAuthState: ...
    def act(self, workspace: BrowserWorkspace, action: BrowserAction) -> BrowserState: ...
    def evaluate(self, workspace: BrowserWorkspace, script: str) -> dict[str, Any]: ...


class CliAgentBrowserClient(browser_runtime.CliAgentBrowserClient):
    def acquire_workspace(self, request: BrowserWorkspaceRequest) -> BrowserWorkspace:
        return super().acquire_workspace(request, target_service_id="reddit")

    def inspect_auth(self, workspace: BrowserWorkspace) -> RedditAuthState:
        if not self.prepare_site_tab(workspace, "reddit.com", consolidate=True):
            self.act(workspace, BrowserAction("new_tab", value="https://www.reddit.com/"))
            self.act(workspace, BrowserAction("wait", value="2500"))
        raw = self.evaluate(workspace, AUTH_SCRIPT)
        return RedditAuthState(
            authenticated=bool(raw.get("authenticated")),
            login_form=bool(raw.get("login_form")),
            checkpoint=bool(raw.get("checkpoint")),
        )


def search_url(topic: str) -> str:
    return (
        "https://www.reddit.com/search/?q="
        f"{quote_plus(topic.strip())}&type=posts&sort=new&t=month"
    )


def browser_request(
    config: dict[str, Any],
    *,
    timeout: int,
    surface_kind: str = "topic",
) -> BrowserWorkspaceRequest:
    feed_surface = surface_kind == "feed"
    return BrowserWorkspaceRequest(
        profile_id=str(
            config.get("LAST30DAYS_REDDIT_BROWSER_PROFILE") or "last30days-facebook"
        ),
        session_name=str(
            config.get("LAST30DAYS_REDDIT_BROWSER_SESSION") or "last30days-reddit"
        ),
        browser_build=str(
            config.get("LAST30DAYS_REDDIT_BROWSER_BUILD") or "stealthcdp_chromium"
        ),
        view_provider=(
            "cdp_screencast"
            if feed_surface
            else str(
                config.get("LAST30DAYS_REDDIT_BROWSER_VIEW_PROVIDER")
                or "rdp_gateway"
            )
        ),
        timeout=timeout,
        start_url="https://www.reddit.com/",
        agent_name="reddit-scraper",
        task_name=("reddit-home-feed" if feed_surface else "reddit-post-search"),
        target_service_id="reddit",
        browser_host=("local_headless" if feed_surface else "remote_headed"),
        control_input_provider=(
            "cdp_input" if feed_surface else "manual_attached_desktop"
        ),
        display_isolation=str(
            config.get("LAST30DAYS_AGENT_BROWSER_DISPLAY_ISOLATION")
            or "private_virtual_display"
        ),
        constrain_presentation=feed_surface,
        allow_duplicate_profile_lane=browser_runtime.config_flag(
            config.get("LAST30DAYS_AGENT_BROWSER_ALLOW_DUPLICATE_PROFILE_LANE")
        ),
    )


class RedditBrowserScraper:
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
    ) -> None:
        self.client = client
        self.request = request
        self.limit = max(1, limit)
        self.scrolls = max(0, scrolls)
        self.initial_wait = max(0.0, initial_wait)
        self.scroll_wait = max(0.0, scroll_wait)
        self.now = now or datetime.now(timezone.utc)

    def search(self, topic: str, from_date: str, to_date: str) -> dict[str, Any]:
        started = time.monotonic()
        diagnostics = RedditDiagnostics()
        workspace: BrowserWorkspace | None = None
        page = RedditPageState(url="", title="")
        try:
            workspace = self.client.acquire_workspace(self.request)
            diagnostics.failure_stage = "navigation"
            page = self._navigate(workspace, topic)
            if page.no_results:
                diagnostics.verified_no_results = True
                diagnostics.duration_ms = _elapsed_ms(started)
                return self._result([], None, None, workspace, page, diagnostics)
            if self.initial_wait:
                time.sleep(self.initial_wait)
            diagnostics.failure_stage = "extraction"
            raw_candidates = self._extract(workspace)
            for _ in range(self.scrolls):
                if len(raw_candidates) >= self.limit:
                    break
                self.client.act(workspace, BrowserAction("scroll", value="1400"))
                if self.scroll_wait:
                    time.sleep(self.scroll_wait)
                raw_candidates.extend(self._extract(workspace))
                raw_candidates = raw_candidates[:80]
            if not raw_candidates:
                raise RedditBrowserFailure(
                    "extraction_empty",
                    "Verified Reddit search page contained no extractable post cards",
                )
            diagnostics.failure_stage = "quality_gate"
            items = self._quality_gate(raw_candidates, topic, from_date, to_date, diagnostics)
            diagnostics.duration_ms = _elapsed_ms(started)
            if not items:
                return self._result(
                    [],
                    "quality_gate_failed",
                    "Reddit candidates were found, but none passed the post quality gate",
                    workspace,
                    page,
                    diagnostics,
                )
            return self._result(items, None, None, workspace, page, diagnostics)
        except (RedditBrowserFailure, browser_runtime.AgentBrowserRuntimeFailure) as exc:
            diagnostics.duration_ms = _elapsed_ms(started)
            return self._result(
                [], exc.error_type, _safe_error_message(str(exc)), workspace, page, diagnostics
            )

    def feed(self, from_date: str, to_date: str) -> dict[str, Any]:
        """Collect structurally valid posts from the authenticated home feed."""
        started = time.monotonic()
        diagnostics = RedditDiagnostics()
        workspace: BrowserWorkspace | None = None
        page = RedditPageState(url="", title="")
        try:
            workspace = self.client.acquire_workspace(self.request)
            diagnostics.failure_stage = "authentication"
            auth = self.client.inspect_auth(workspace)
            if auth.checkpoint:
                raise RedditBrowserFailure(
                    "checkpoint_required",
                    "Reddit requires an operator security-verification checkpoint",
                )
            if auth.login_form:
                raise RedditBrowserFailure(
                    "auth_required",
                    "Reddit authentication is required in the retained profile",
                )
            if not auth.authenticated:
                raise RedditBrowserFailure(
                    "auth_state_ambiguous",
                    "Reddit authentication state could not be determined from the rendered page",
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
            diagnostics.stop_reason = "scroll_budget"
            for _ in range(self.scrolls):
                if self._accepted_unique_count(raw_candidates, from_date, to_date) >= self.limit:
                    diagnostics.stop_reason = "accepted_limit"
                    break
                self.client.act(workspace, BrowserAction("scroll", value="1400"))
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
                diagnostics.stagnant_scrolls = stagnant_scrolls
                diagnostics.unique_observation_count = len(seen_observations)
                if stagnant_scrolls >= MAX_STAGNANT_SCROLLS:
                    diagnostics.stop_reason = "stagnation_limit"
                    break
            if self._accepted_unique_count(raw_candidates, from_date, to_date) >= self.limit:
                diagnostics.stop_reason = "accepted_limit"
            if not raw_candidates:
                raise RedditBrowserFailure(
                    "extraction_empty",
                    "Verified Reddit home feed contained no extractable post cards",
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
                    "Reddit feed candidates were found, but none passed the structural gate",
                    workspace,
                    page,
                    diagnostics,
                )
            return self._result(items, None, None, workspace, page, diagnostics)
        except (RedditBrowserFailure, browser_runtime.AgentBrowserRuntimeFailure) as exc:
            diagnostics.duration_ms = _elapsed_ms(started)
            return self._result(
                [], exc.error_type, _safe_error_message(str(exc)), workspace, page, diagnostics
            )

    def _accepted_unique_count(
        self,
        raw_candidates: list[dict[str, Any]],
        from_date: str,
        to_date: str,
    ) -> int:
        preview = RedditDiagnostics()
        return len(
            self._quality_gate(
                raw_candidates,
                "",
                from_date,
                to_date,
                preview,
                surface_kind="feed",
            )
        )

    def _navigate(self, workspace: BrowserWorkspace, topic: str) -> RedditPageState:
        desired = search_url(topic)
        prepare = getattr(self.client, "prepare_site_tab", None)
        retained = bool(
            callable(prepare) and prepare(workspace, "reddit.com", consolidate=True)
        )
        self.client.act(
            workspace,
            BrowserAction("navigate" if retained else "new_tab", value=desired),
        )
        self.client.act(workspace, BrowserAction("wait", value="2500"))
        page = _page_state(self.client.evaluate(workspace, PAGE_STATE_SCRIPT))
        if page.rate_limited:
            raise RedditBrowserFailure(
                "rate_limit_detected",
                f"Reddit rate-limit page detected ({page.rate_limit_reason or 'unspecified'})",
            )
        if page.checkpoint:
            raise RedditBrowserFailure(
                "checkpoint_required", "Reddit returned a browser verification challenge"
            )
        if page.login_page:
            raise RedditBrowserFailure(
                "auth_required", "Reddit redirected the public search to login"
            )
        if page.error_page:
            raise RedditBrowserFailure("search_unavailable", "Reddit returned an error page")
        if page.interstitial:
            raise RedditBrowserFailure(
                "interstitial_detected", "Reddit returned a blocking consent interstitial"
            )
        if not _page_matches_query(page, topic):
            raise RedditBrowserFailure(
                "navigation_mismatch",
                f"Reddit final page does not match requested post search: {page.url}",
            )
        return page

    def _navigate_feed(self, workspace: BrowserWorkspace) -> RedditPageState:
        desired = "https://www.reddit.com/"
        prepare = getattr(self.client, "prepare_site_tab", None)
        retained = bool(
            callable(prepare) and prepare(workspace, "reddit.com", consolidate=True)
        )
        self.client.act(
            workspace,
            BrowserAction("navigate" if retained else "new_tab", value=desired),
        )
        self.client.act(workspace, BrowserAction("wait", value="2500"))
        page = _page_state(self.client.evaluate(workspace, PAGE_STATE_SCRIPT))
        for delay_ms in ("3500", "5000"):
            if (
                page.has_posts
                or page.rate_limited
                or page.checkpoint
                or page.login_page
                or page.error_page
                or page.interstitial
            ):
                break
            self.client.act(workspace, BrowserAction("wait", value=delay_ms))
            page = _page_state(self.client.evaluate(workspace, PAGE_STATE_SCRIPT))
        if page.rate_limited:
            raise RedditBrowserFailure(
                "rate_limit_detected",
                f"Reddit rate-limit page detected ({page.rate_limit_reason or 'unspecified'})",
            )
        if page.checkpoint:
            raise RedditBrowserFailure(
                "checkpoint_required", "Reddit returned a browser verification challenge"
            )
        if page.login_page:
            raise RedditBrowserFailure(
                "auth_required", "Reddit redirected the home feed to login"
            )
        if page.error_page:
            raise RedditBrowserFailure("feed_unavailable", "Reddit returned an error page")
        if page.interstitial:
            raise RedditBrowserFailure(
                "interstitial_detected", "Reddit returned a blocking consent interstitial"
            )
        if not _page_matches_feed(page):
            raise RedditBrowserFailure(
                "navigation_mismatch",
                f"Reddit final page does not match the home feed: {page.url}",
            )
        return page

    def _extract(self, workspace: BrowserWorkspace) -> list[dict[str, Any]]:
        raw = self.client.evaluate(workspace, EXTRACT_SCRIPT)
        candidates = raw.get("candidates") if isinstance(raw, dict) else None
        if not isinstance(candidates, list):
            raise RedditBrowserFailure(
                "agent_browser_error", "agent-browser returned malformed Reddit extraction data"
            )
        return [item for item in candidates if isinstance(item, dict)][:80]

    def _quality_gate(
        self,
        raw_candidates: list[dict[str, Any]],
        topic: str,
        from_date: str,
        to_date: str,
        diagnostics: RedditDiagnostics,
        *,
        surface_kind: str = "topic",
    ) -> list[dict[str, Any]]:
        diagnostics.candidate_count = len(raw_candidates)
        items: list[dict[str, Any]] = []
        seen: set[str] = set()
        for raw in raw_candidates:
            if bool(raw.get("promoted")):
                diagnostics.rejection_counts["promoted"] += 1
                continue
            if bool(raw.get("platform_spam")):
                diagnostics.rejection_counts["platform_spam"] += 1
                continue
            canonical = _canonical_post_url(str(raw.get("permalink") or ""))
            reddit_id = _reddit_id(canonical or "")
            if not canonical or not reddit_id:
                if surface_kind == "feed":
                    diagnostics.limitation_counts["invalid_permalink"] += 1
                else:
                    diagnostics.rejection_counts["invalid_permalink"] += 1
                continue
            if reddit_id in seen:
                if surface_kind == "feed":
                    diagnostics.duplicate_count += 1
                else:
                    diagnostics.rejection_counts["duplicate"] += 1
                continue
            title = _clean(str(raw.get("title") or ""))
            text = _clean(str(raw.get("text") or ""))
            if not title:
                if surface_kind == "feed":
                    diagnostics.limitation_counts["missing_title"] += 1
                else:
                    diagnostics.rejection_counts["missing_title"] += 1
                continue
            relevance = 0.5
            if surface_kind == "topic":
                relevance = token_overlap_relevance(topic, f"{title} {text}".strip())
                if relevance <= 0:
                    diagnostics.rejection_counts["off_topic"] += 1
                    continue
                if query_term_coverage(topic, f"{title} {text}".strip()) < 1.0:
                    diagnostics.rejection_counts["partial_query_match"] += 1
                    continue
            published_at = _timestamp(str(raw.get("created_at") or ""))
            if published_at is None:
                if surface_kind == "feed":
                    diagnostics.limitation_counts["invalid_timestamp"] += 1
                else:
                    diagnostics.rejection_counts["invalid_timestamp"] += 1
                continue
            date = published_at.date().isoformat()
            if not (from_date <= date <= to_date):
                if surface_kind == "feed":
                    diagnostics.scope_exclusion_counts["outside_date_range"] += 1
                else:
                    diagnostics.rejection_counts["outside_date_range"] += 1
                continue
            subreddit = str(raw.get("subreddit") or "").strip()
            if subreddit.casefold().startswith("r/"):
                subreddit = subreddit[2:]
            if not subreddit:
                match = re.search(r"/r/([^/]+)/comments/", canonical, re.IGNORECASE)
                subreddit = unquote(match.group(1)) if match else ""
            if not subreddit:
                if surface_kind == "feed":
                    diagnostics.limitation_counts["missing_subreddit"] += 1
                else:
                    diagnostics.rejection_counts["missing_subreddit"] += 1
                continue
            seen.add(reddit_id)
            items.append(
                {
                    "id": f"R{reddit_id}",
                    "reddit_id": reddit_id,
                    "title": title,
                    "text": text,
                    "url": canonical,
                    "author": _clean(str(raw.get("author") or "")),
                    "subreddit": subreddit,
                    "date": date,
                    "score": _count(raw.get("score")),
                    "num_comments": _count(raw.get("comment_count")),
                    "relevance": round(float(relevance), 2),
                    "why_relevant": (
                        "Authenticated Reddit home feed post"
                        if surface_kind == "feed"
                        else f"Reddit post: {title[:80]}"
                    ),
                    "metadata": {
                        "extraction": "agent-browser-dom-v1",
                        "dom_shape": (
                            str(raw.get("dom_shape"))
                            if str(raw.get("dom_shape")) in DOM_SHAPES
                            else "unknown"
                        ),
                        "crosspost": bool(raw.get("crosspost")),
                        "remote_browser": True,
                        "published_at": published_at.isoformat() if published_at else None,
                        **({"surface_kind": "feed"} if surface_kind == "feed" else {}),
                    },
                }
            )
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
        page: RedditPageState,
        diagnostics: RedditDiagnostics,
    ) -> dict[str, Any]:
        details = diagnostics.as_dict()
        operations = list(getattr(self.client, "command_timings", []))[-12:]
        details["command_count"] = len(operations)
        details["browser_operations"] = operations
        if page.no_results:
            details["page_state"] = "verified_no_results"
        elif page.has_posts:
            details["page_state"] = "posts"
        elif error_type:
            details["page_state"] = error_type
        else:
            details["page_state"] = "unknown"
        if error_type:
            details["failure_stage"] = diagnostics.failure_stage
        return {
            "items": items,
            "error": error,
            "error_type": error_type,
            "url": page.url,
            "title": page.title,
            "profile": self.request.profile_id,
            "session": self.request.session_name,
            "workspace": {
                "browser_id": workspace.browser_id,
                "target_id": workspace.target_id,
                "route_id": workspace.route_id,
            }
            if workspace
            else {},
            "diagnostics": details,
        }


def search_reddit_browser(
    topic: str,
    from_date: str,
    to_date: str,
    *,
    depth: str = "default",
    config: dict[str, Any] | None = None,
    limit: int | None = None,
) -> dict[str, Any]:
    config = config or {}
    if shutil.which("agent-browser") is None:
        return {
            "items": [],
            "error": "agent-browser command is not on PATH",
            "error_type": "agent_browser_missing",
        }
    settings = DEPTH_CONFIG.get(depth, DEPTH_CONFIG["default"])
    timeout = max(
        1,
        min(
            settings["timeout"],
            int(
                config.get("LAST30DAYS_REDDIT_BROWSER_TIMEOUT")
                or settings["timeout"]
            ),
        ),
    )
    result_limit = max(
        1,
        min(
            settings["results"],
            int(
                limit
                if limit is not None
                else config.get("LAST30DAYS_REDDIT_BROWSER_MAX_RESULTS")
                or settings["results"]
            ),
        ),
    )
    scrolls = max(
        0,
        min(
            settings["scrolls"],
            int(config.get("LAST30DAYS_REDDIT_BROWSER_SCROLLS") or settings["scrolls"]),
        ),
    )
    scraper = RedditBrowserScraper(
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
        browser_request(config, timeout=timeout),
        limit=result_limit,
        scrolls=scrolls,
        initial_wait=float(config.get("LAST30DAYS_REDDIT_BROWSER_INITIAL_WAIT") or 2.0),
        scroll_wait=float(config.get("LAST30DAYS_REDDIT_BROWSER_SCROLL_WAIT") or 1.5),
    )
    result = scraper.search(topic, from_date, to_date)
    _log(
        f"accepted={len(result.get('items') or [])} "
        f"error_type={result.get('error_type') or 'none'}"
    )
    return result


def scrape_reddit_feed(
    from_date: str,
    to_date: str,
    *,
    depth: str = "default",
    config: dict[str, Any] | None = None,
    limit: int | None = None,
) -> dict[str, Any]:
    """Scrape the authenticated Reddit home feed without a topic query."""
    config = config or {}
    if shutil.which("agent-browser") is None:
        return {
            "items": [],
            "error": "agent-browser command is not on PATH",
            "error_type": "agent_browser_missing",
        }
    settings = DEPTH_CONFIG.get(depth, DEPTH_CONFIG["default"])
    timeout = max(
        1,
        int(config.get("LAST30DAYS_REDDIT_BROWSER_TIMEOUT") or settings["timeout"]),
    )
    result_limit = max(
        1,
        min(
            MAX_EXPLICIT_RESULTS,
            int(
                config.get("LAST30DAYS_REDDIT_BROWSER_MAX_RESULTS")
                or settings["results"]
            ),
        ),
    )
    if limit is not None:
        result_limit = max(1, min(MAX_EXPLICIT_RESULTS, int(limit)))
    scrolls = max(
        0,
        min(
            MAX_EXPLICIT_FEED_SCROLLS,
            int(
                config.get("LAST30DAYS_REDDIT_BROWSER_SCROLLS")
                or settings["scrolls"]
            ),
        ),
    )
    if limit is not None:
        scrolls = max(
            scrolls,
            min(
                MAX_EXPLICIT_FEED_SCROLLS,
                (
                    result_limit
                    + FEED_ACCEPTED_ITEMS_PER_SCROLL_BUDGET
                    - 1
                )
                // FEED_ACCEPTED_ITEMS_PER_SCROLL_BUDGET,
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
    scraper = RedditBrowserScraper(
        client,
        browser_request(config, timeout=timeout, surface_kind="feed"),
        limit=result_limit,
        scrolls=scrolls,
        initial_wait=float(config.get("LAST30DAYS_REDDIT_BROWSER_INITIAL_WAIT") or 2.0),
        scroll_wait=float(config.get("LAST30DAYS_REDDIT_BROWSER_SCROLL_WAIT") or 1.5),
    )
    try:
        result = scraper.feed(from_date, to_date)
        _log(
            f"feed accepted={len(result.get('items') or [])} "
            f"error_type={result.get('error_type') or 'none'}"
        )
        return result
    finally:
        try:
            client.release_workspace()
        except browser_runtime.AgentBrowserRuntimeFailure as exc:
            _log(f"Best-effort Reddit service tab release did not complete: {exc}")


def _page_state(raw: dict[str, Any]) -> RedditPageState:
    return RedditPageState(
        url=str(raw.get("url") or ""),
        title=str(raw.get("title") or ""),
        query_value=str(raw.get("query_value") or ""),
        has_posts=bool(raw.get("has_posts")),
        no_results=bool(raw.get("no_results")),
        login_page=bool(raw.get("login_page")),
        checkpoint=bool(raw.get("checkpoint")),
        rate_limited=bool(raw.get("rate_limited")),
        rate_limit_reason=str(raw.get("rate_limit_reason") or ""),
        error_page=bool(raw.get("error_page")),
        interstitial=bool(raw.get("interstitial")),
    )


def _page_matches_query(page: RedditPageState, topic: str) -> bool:
    parsed = urlsplit(page.url)
    if (parsed.hostname or "").casefold() not in {"reddit.com", "www.reddit.com"}:
        return False
    if parsed.path.rstrip("/") != "/search":
        return False
    query = page.query_value or (parse_qs(parsed.query).get("q") or [""])[0]
    return unquote(query).strip().casefold() == topic.strip().casefold()


def _page_matches_feed(page: RedditPageState) -> bool:
    parsed = urlsplit(page.url)
    return (
        (parsed.hostname or "").casefold() in {"reddit.com", "www.reddit.com"}
        and parsed.path.rstrip("/") in {"", "/best", "/hot"}
        and page.has_posts
    )


def _canonical_post_url(value: str) -> str | None:
    if not value:
        return None
    parsed = urlsplit(value if "://" in value else f"https://www.reddit.com/{value.lstrip('/')}")
    if (parsed.hostname or "").casefold() not in {
        "reddit.com",
        "www.reddit.com",
        "old.reddit.com",
    }:
        return None
    path = re.sub(r"/+", "/", unquote(parsed.path or "/"))
    if not re.search(r"/comments/[A-Za-z0-9]+(?:/|$)", path):
        return None
    path = path.rstrip("/") + "/"
    return urlunsplit(("https", "www.reddit.com", path, "", ""))


def _reddit_id(url: str) -> str:
    match = re.search(r"/comments/([A-Za-z0-9]+)(?:/|$)", url)
    return match.group(1) if match else ""


def _candidate_observation_key(candidate: dict[str, Any]) -> str:
    canonical = _canonical_post_url(str(candidate.get("permalink") or ""))
    if canonical:
        return canonical
    return "\n".join(
        (
            _clean(str(candidate.get("author") or "")).casefold(),
            _clean(str(candidate.get("created_at") or "")),
            _clean(str(candidate.get("title") or "")).casefold()[:500],
        )
    )


def _timestamp(value: str) -> datetime | None:
    value = value.strip()
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _count(value: Any) -> int:
    text = str(value or "").strip().casefold().replace(",", "")
    match = re.search(r"(\d+(?:\.\d+)?)\s*([km]?)", text)
    if not match:
        return 0
    multiplier = {"": 1, "k": 1_000, "m": 1_000_000}[match.group(2)]
    return max(0, round(float(match.group(1)) * multiplier))


def _clean(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def _safe_error_message(value: str) -> str:
    redacted = re.sub(
        r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",
        "[REDACTED]",
        value,
    )
    redacted = re.sub(
        r"(?i)(?:bearer\s+|\[REDACTED\]\s+)[^\s,;]+",
        "[REDACTED]",
        redacted,
    )
    return redacted[:512]


def _elapsed_ms(started: float) -> int:
    return max(0, round((time.monotonic() - started) * 1000))


def _log(message: str) -> None:
    log.source_log("RedditBrowser", message, tty_only=False)
