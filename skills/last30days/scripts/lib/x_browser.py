"""Quality-gated X search through an authenticated agent-browser profile."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
import re
import time
from typing import Any
from urllib.parse import parse_qs, quote, unquote, urlsplit

from . import agent_browser_config, facebook as browser_runtime, log
from .relevance import token_overlap_relevance as _compute_relevance


DEPTH_CONFIG = {
    "quick": {"results": 8, "scrolls": 0, "timeout": 45},
    "default": {"results": 16, "scrolls": 1, "timeout": 75},
    "deep": {"results": 30, "scrolls": 2, "timeout": 120},
}

BrowserWorkspaceRequest = browser_runtime.BrowserWorkspaceRequest
BrowserWorkspace = browser_runtime.BrowserWorkspace
BrowserAction = browser_runtime.BrowserAction
BrowserState = browser_runtime.BrowserState
BrowserSnapshot = browser_runtime.BrowserSnapshot

ERROR_TYPES = {
    "agent_browser_missing",
    "profile_mismatch",
    "route_stale",
    "auth_required",
    "checkpoint_required",
    "rate_limited",
    "navigation_mismatch",
    "search_unavailable",
    "extraction_empty",
    "quality_gate_failed",
    "agent_browser_timeout",
    "agent_browser_error",
}


class XBrowserFailure(RuntimeError):
    def __init__(self, error_type: str, message: str, *, operator_url: str = "") -> None:
        super().__init__(message)
        self.error_type = error_type if error_type in ERROR_TYPES else "agent_browser_error"
        self.operator_url = operator_url


AUTH_SCRIPT = r"""
(() => {
  const body = (document.body?.innerText || "").slice(0, 12000);
  const checkpointUrl = /\/(?:i\/flow|account\/access|challenge)(?:\/|$|\?)/i.test(location.href);
  const checkpointBody = /verify your identity|confirm your identity|security checkpoint|complete this challenge to continue/i.test(body);
  const authenticatedDom = Boolean(
    document.querySelector('[data-testid="SideNav_AccountSwitcher_Button"], nav[aria-label="Primary"]')
  );
  return {
    url: location.href,
    title: document.title,
    login_form: Boolean(document.querySelector('a[href="/login"], input[autocomplete="username"]')),
    checkpoint: checkpointUrl || (!authenticatedDom && checkpointBody),
    restricted: /account (?:is|has been) (?:locked|suspended)|unusual activity|rate limit exceeded/i.test(body),
    authenticated_dom: authenticatedDom
  };
})()
"""


PAGE_STATE_SCRIPT = r"""
(() => {
  const body = (document.body?.innerText || "").slice(0, 24000);
  const search = document.querySelector('[data-testid="SearchBox_Search_Input"], input[aria-label="Search query"]');
  const latest = Array.from(document.querySelectorAll('[role="tab"]')).find((node) =>
    /latest/i.test(node.innerText || node.textContent || "")
  );
  const authenticatedDom = Boolean(
    document.querySelector('[data-testid="SideNav_AccountSwitcher_Button"], nav[aria-label="Primary"]')
  );
  const checkpointBody = /verify your identity|confirm your identity|security checkpoint|complete this challenge to continue/i.test(body);
  return {
    url: location.href,
    title: document.title,
    query_value: String(search?.value || "").trim(),
    latest_selected: Boolean(latest && latest.getAttribute("aria-selected") === "true") ||
      new URL(location.href).searchParams.get("f") === "live",
    article_count: document.querySelectorAll("article").length,
    no_results: /no results|try searching for something else/i.test(body),
    login_page: Boolean(document.querySelector('a[href="/login"], input[autocomplete="username"]')),
    checkpoint: /\/(?:i\/flow|account\/access|challenge)(?:\/|$|\?)/i.test(location.href) ||
      (!authenticatedDom && checkpointBody),
    restricted: /account (?:is|has been) (?:locked|suspended)|unusual activity|rate limit exceeded/i.test(body),
    error_page: /something went wrong|try reloading|temporarily unavailable/i.test(body)
  };
})()
"""


EXTRACT_SCRIPT = r"""
(() => ({
  url: location.href,
  title: document.title,
  candidates: Array.from(document.querySelectorAll("article")).map((article) => {
    const time = article.querySelector("time[datetime]");
    const status = time?.closest('a[href*="/status/"]') || article.querySelector('a[href*="/status/"]');
    const text = article.querySelector('[data-testid="tweetText"]')?.innerText || "";
    const metric = (testId) => {
      const node = article.querySelector(`[data-testid="${testId}"]`);
      return String(node?.getAttribute("aria-label") || node?.innerText || "").trim();
    };
    return {
      text,
      url: status?.href || "",
      author_handle: (status?.pathname || "").split("/").filter(Boolean)[0] || "",
      timestamp: time?.getAttribute("datetime") || "",
      promoted: /(^|\n)Promoted($|\n)/i.test(article.innerText || ""),
      engagement: {
        replies: metric("reply"),
        reposts: metric("retweet"),
        likes: metric("like"),
        bookmarks: metric("bookmark"),
        views: String(article.querySelector('a[href$="/analytics"]')?.innerText || "").trim()
      },
      media: [
        ...Array.from(article.querySelectorAll('[data-testid="tweetPhoto"] img, img[src*="pbs.twimg.com/media"]'))
          .map((image) => ({
            kind: "image", url: image.currentSrc || image.src || "",
            preview_url: null, mime_type: null,
            width: image.naturalWidth || null, height: image.naturalHeight || null,
            duration_seconds: null, alt_text: image.alt || null
          })),
        ...Array.from(article.querySelectorAll("video"))
          .map((video) => ({
            kind: "video", url: status?.href || "",
            preview_url: video.poster || null, mime_type: null,
            width: video.videoWidth || null, height: video.videoHeight || null,
            duration_seconds: Number.isFinite(video.duration) ? Math.round(video.duration) : null,
            alt_text: null
          }))
      ].filter((asset) => asset.url)
    };
  })
}))()
"""


SCROLL_SCRIPT = r"""
(() => {
  window.scrollBy({top: Math.max(window.innerHeight * 1.8, 1200), behavior: "instant"});
  return {scrollY: window.scrollY, article_count: document.querySelectorAll("article").length};
})()
"""


@dataclass(frozen=True)
class XAuthState:
    authenticated: bool
    login_form: bool = False
    checkpoint: bool = False
    restricted: bool = False
    url: str = ""


@dataclass(frozen=True)
class XPageState:
    url: str
    title: str
    query_value: str = ""
    latest_selected: bool = False
    article_count: int = 0
    no_results: bool = False
    login_page: bool = False
    checkpoint: bool = False
    restricted: bool = False
    error_page: bool = False


@dataclass
class XRunDiagnostics:
    rejection_counts: Counter[str] = field(default_factory=Counter)
    accepted_count: int = 0
    duration_ms: int = 0

    def as_dict(self) -> dict[str, Any]:
        return {
            "rejection_counts": dict(self.rejection_counts),
            "accepted_count": self.accepted_count,
            "duration_ms": self.duration_ms,
        }


class CliAgentBrowserClient(browser_runtime.CliAgentBrowserClient):
    def acquire_workspace(self, request: BrowserWorkspaceRequest) -> BrowserWorkspace:
        access_plan = self._invoke(
            [
                "service", "access-plan",
                "--service-name", "last30days",
                "--agent-name", "x-scraper",
                "--task-name", "x-search",
                "--target-service-id", "x",
                "--url", "https://x.com/search",
            ],
            timeout=min(request.timeout, 30),
        )
        selected = access_plan.get("selectedProfile")
        selected_profile = str(selected.get("id") or "") if isinstance(selected, dict) else ""
        if not selected_profile:
            raise XBrowserFailure(
                "auth_required",
                "agent-browser has no authenticated profile registered for X",
            )
        if selected_profile != request.profile_id:
            raise XBrowserFailure(
                "profile_mismatch",
                f"agent-browser selected X profile {selected_profile!r}, not {request.profile_id!r}",
            )
        try:
            agent_browser_config.record_access_plan(access_plan, "x")
        except OSError as exc:
            _log(f"Could not record user-scoped agent-browser configuration: {exc}")
        decision = access_plan.get("decision") if isinstance(access_plan.get("decision"), dict) else {}
        if decision.get("manualActionRequired") or decision.get("manualSeedingRequired"):
            raise XBrowserFailure(
                "auth_required",
                "agent-browser reports that the selected X profile requires operator authentication",
            )

        shared_route = agent_browser_config.shared_acquisition_route(
            access_plan,
            expected_profile_id=selected_profile,
        )
        if shared_route:
            return BrowserWorkspace(
                profile_id=selected_profile,
                browser_id=shared_route["browser_id"],
                session_name=shared_route["session_name"],
                operator_visible_state="not_required",
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
            self.prepare_site_tab(
                BrowserWorkspace(
                    selected_profile,
                    shared_owner["browser_id"],
                    shared_owner["session_name"],
                ),
                "x.com",
                consolidate=True,
            )
            stream = browser_runtime._ready_operator_stream(browser, request.view_provider)
            return BrowserWorkspace(
                profile_id=selected_profile,
                browser_id=shared_owner["browser_id"],
                session_name=shared_owner["session_name"],
                target_id=shared_owner["target_id"],
                route_id=str(stream.get("id") or ""),
                operator_url=str(stream.get("externalUrl") or stream.get("url") or ""),
                operator_visible_state="ready" if stream else "not_required",
            )

        session = sessions.get(request.session_name) if isinstance(sessions, dict) else None
        browser = None
        browser_id = ""
        target_id = ""
        if isinstance(session, dict):
            observed_profile = str(session.get("profileId") or "")
            if not observed_profile or observed_profile == selected_profile:
                browser_ids = session.get("browserIds") or []
                if browser_ids:
                    browser_id = str(browser_ids[0])
                    candidate = browsers.get(browser_id) if isinstance(browsers, dict) else None
                    if isinstance(candidate, dict) and candidate.get("health") == "ready":
                        browser = candidate
                        target_id = browser_runtime._select_target_id(session, tabs)

        if browser:
            self.prepare_site_tab(
                BrowserWorkspace(selected_profile, browser_id, request.session_name),
                "x.com",
                consolidate=True,
            )
            stream = browser_runtime._ready_operator_stream(browser, request.view_provider)
            return BrowserWorkspace(
                profile_id=selected_profile,
                browser_id=browser_id,
                session_name=request.session_name,
                target_id=target_id,
                route_id=str(stream.get("id") or ""),
                operator_url=str(stream.get("externalUrl") or stream.get("url") or ""),
                operator_visible_state="ready" if stream else "not_required",
            )

        profile = selected.get("userDataDir") if isinstance(selected, dict) else ""
        launch = decision.get("launchPosture") if isinstance(decision.get("launchPosture"), dict) else {}
        command = [
            "--session", request.session_name,
            "--runtime-profile", selected_profile,
            "--browser-build", request.browser_build,
            "--browser-host", str(launch.get("browserHost") or "local_headed"),
            "--view-stream-provider", request.view_provider,
            "--leave-open",
        ]
        if profile:
            command.extend(["--profile", str(profile)])
        command.extend(["open", "https://x.com/home"])
        opened = self._invoke(command, timeout=request.timeout)
        visible = opened.get("operatorVisible") if isinstance(opened.get("operatorVisible"), dict) else {}
        visible_state = str(visible.get("state") or "not_required")
        observed_profile = str(opened.get("profileId") or visible.get("profileId") or selected_profile)
        if observed_profile != selected_profile:
            raise XBrowserFailure(
                "profile_mismatch",
                f"agent-browser opened profile {observed_profile!r}, not {selected_profile!r}",
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

    def inspect_auth(self, workspace: BrowserWorkspace) -> XAuthState:
        if not self.prepare_site_tab(workspace, "x.com", consolidate=True):
            self.act(workspace, BrowserAction("new_tab", value="https://x.com/home"))
            self.act(workspace, BrowserAction("wait", value="2500"))
            self._prepared_sites.add((workspace.session_name, "x.com"))
        raw = self.evaluate(workspace, AUTH_SCRIPT)
        return XAuthState(
            authenticated=bool(raw.get("authenticated_dom")),
            login_form=bool(raw.get("login_form")),
            checkpoint=bool(raw.get("checkpoint")),
            restricted=bool(raw.get("restricted")),
            url=str(raw.get("url") or ""),
        )


class XBrowserScraper:
    def __init__(
        self,
        client: Any,
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
        self.limit = limit
        self.scrolls = scrolls
        self.initial_wait = initial_wait
        self.scroll_wait = scroll_wait
        self.now = now or datetime.now(timezone.utc)

    def search(self, topic: str, from_date: str, to_date: str) -> dict[str, Any]:
        started = time.monotonic()
        diagnostics = XRunDiagnostics()
        workspace = self.client.acquire_workspace(self.request)
        auth = self.client.inspect_auth(workspace)
        if auth.checkpoint:
            raise XBrowserFailure(
                "checkpoint_required",
                "X requires an operator security checkpoint",
                operator_url=workspace.operator_url,
            )
        if auth.restricted:
            raise XBrowserFailure(
                "rate_limited",
                "X reports that the authenticated account is restricted or rate limited",
                operator_url=workspace.operator_url,
            )
        if not auth.authenticated:
            raise XBrowserFailure("auth_required", "X authentication is required")
        query = _dated_query(topic, from_date, to_date)
        search_url = _search_url(query)
        retained = self.client.prepare_site_tab(workspace, "x.com", consolidate=True)
        self.client.act(
            workspace,
            BrowserAction("navigate" if retained else "new_tab", value=search_url),
        )
        self.client.act(
            workspace,
            BrowserAction("wait", value=str(max(0, round(self.initial_wait * 1000)))),
        )
        page = _page_state(self.client.evaluate(workspace, PAGE_STATE_SCRIPT))
        if page.checkpoint:
            raise XBrowserFailure("checkpoint_required", "X search opened a security checkpoint")
        if page.restricted:
            raise XBrowserFailure("rate_limited", "X search reported an account restriction or rate limit")
        if page.login_page:
            raise XBrowserFailure("auth_required", "X search redirected to login")
        if page.error_page:
            raise XBrowserFailure("search_unavailable", "X search returned a temporary error page")
        if not _page_matches_query(page, query):
            raise XBrowserFailure("navigation_mismatch", "X search state did not match the requested query")
        raw = list(self.client.evaluate(workspace, EXTRACT_SCRIPT).get("candidates") or [])
        for _ in range(self.scrolls):
            if len(raw) >= self.limit:
                break
            self.client.evaluate(workspace, SCROLL_SCRIPT)
            self.client.act(
                workspace,
                BrowserAction("wait", value=str(max(0, round(self.scroll_wait * 1000)))),
            )
            raw.extend(self.client.evaluate(workspace, EXTRACT_SCRIPT).get("candidates") or [])
        if not raw and not page.no_results:
            raise XBrowserFailure(
                "extraction_empty",
                "Verified X search page contained no post articles",
            )
        items = _quality_gate(raw, topic, from_date, to_date, diagnostics)
        items = _dedupe_items(items)[: self.limit]
        diagnostics.duration_ms = round((time.monotonic() - started) * 1000)
        diagnostics.accepted_count = len(items)
        error_type = "quality_gate_failed" if raw and not items else None
        return {
            "items": items,
            "error": "X candidates were found, but none passed the post quality gate" if error_type else None,
            "error_type": error_type,
            "url": page.url,
            "title": page.title,
            "profile": workspace.profile_id,
            "session": workspace.session_name,
            "diagnostics": diagnostics.as_dict(),
        }


def search_x_browser(
    topic: str,
    from_date: str,
    to_date: str,
    *,
    depth: str = "default",
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    config = config or {}
    settings = DEPTH_CONFIG.get(depth, DEPTH_CONFIG["default"])
    request = BrowserWorkspaceRequest(
        profile_id=str(config.get("LAST30DAYS_X_BROWSER_PROFILE") or "last30days-facebook"),
        session_name=str(config.get("LAST30DAYS_X_BROWSER_SESSION") or "last30days-facebook"),
        browser_build=str(config.get("LAST30DAYS_X_BROWSER_BUILD") or "stealthcdp_chromium"),
        view_provider=str(config.get("LAST30DAYS_X_BROWSER_VIEW_PROVIDER") or "cdp_screencast"),
        timeout=int(config.get("LAST30DAYS_X_BROWSER_TIMEOUT") or settings["timeout"]),
    )
    client = CliAgentBrowserClient(timeout=request.timeout)
    scraper = XBrowserScraper(
        client,
        request,
        limit=settings["results"],
        scrolls=settings["scrolls"],
        initial_wait=float(config.get("LAST30DAYS_X_BROWSER_INITIAL_WAIT") or 2),
        scroll_wait=float(config.get("LAST30DAYS_X_BROWSER_SCROLL_WAIT") or 1),
        now=config.get("_NOW"),
    )
    try:
        return scraper.search(topic, from_date, to_date)
    except XBrowserFailure as exc:
        _log(f"Failed error_type={exc.error_type} message={exc}")
        return {
            "items": [],
            "error": str(exc),
            "error_type": exc.error_type,
            "profile": request.profile_id,
            "session": request.session_name,
            "diagnostics": {"rejection_counts": {}, "accepted_count": 0, "duration_ms": 0},
        }
    except browser_runtime.FacebookScraperFailure as exc:
        error_type = exc.error_type if exc.error_type in ERROR_TYPES else "agent_browser_error"
        _log(f"Failed error_type={error_type} message={exc}")
        return {
            "items": [],
            "error": str(exc),
            "error_type": error_type,
            "profile": request.profile_id,
            "session": request.session_name,
            "diagnostics": {"rejection_counts": {}, "accepted_count": 0, "duration_ms": 0},
        }


def parse_x_browser_response(response: dict[str, Any]) -> list[dict[str, Any]]:
    if response.get("error"):
        _log(f"X browser error ({response.get('error_type')}): {response['error']}")
        return []
    return list(response.get("items") or [])


def _dated_query(topic: str, from_date: str, to_date: str) -> str:
    return f"{topic.strip()} since:{from_date} until:{to_date}".strip()


def _search_url(query: str) -> str:
    return f"https://x.com/search?q={quote(query)}&src=typed_query&f=live"


def _page_state(raw: dict[str, Any]) -> XPageState:
    return XPageState(
        url=str(raw.get("url") or ""),
        title=str(raw.get("title") or ""),
        query_value=str(raw.get("query_value") or ""),
        latest_selected=bool(raw.get("latest_selected")),
        article_count=int(raw.get("article_count") or 0),
        no_results=bool(raw.get("no_results")),
        login_page=bool(raw.get("login_page")),
        checkpoint=bool(raw.get("checkpoint")),
        restricted=bool(raw.get("restricted")),
        error_page=bool(raw.get("error_page")),
    )


def _page_matches_query(page: XPageState, query: str) -> bool:
    parsed = urlsplit(page.url)
    observed = unquote((parse_qs(parsed.query).get("q") or [""])[0])
    lane = (parse_qs(parsed.query).get("f") or [""])[0]
    return (
        parsed.hostname in {"x.com", "www.x.com", "twitter.com", "www.twitter.com"}
        and parsed.path.rstrip("/") == "/search"
        and observed == query
        and page.query_value == query
        and lane == "live"
        and page.latest_selected
        and not page.login_page
        and not page.checkpoint
        and not page.restricted
        and not page.error_page
    )


def _quality_gate(
    candidates: list[dict[str, Any]],
    topic: str,
    from_date: str,
    to_date: str,
    diagnostics: XRunDiagnostics,
) -> list[dict[str, Any]]:
    items = []
    for index, raw in enumerate(candidates):
        url = _canonical_status_url(str(raw.get("url") or ""))
        text = re.sub(r"\s+", " ", str(raw.get("text") or "")).strip()
        handle = str(raw.get("author_handle") or "").lstrip("@")
        date = _iso_date(str(raw.get("timestamp") or ""))
        reason = None
        if not url:
            reason = "missing_permalink"
        elif not handle:
            reason = "missing_author"
        elif len(text) < 30:
            reason = "insufficient_text"
        elif raw.get("promoted"):
            reason = "promoted"
        elif not date or not (from_date <= date <= to_date):
            reason = "out_of_range"
        elif _compute_relevance(topic, text) <= 0:
            reason = "off_topic"
        if reason:
            diagnostics.rejection_counts[reason] += 1
            continue
        items.append({
            "id": f"X{index + 1}",
            "text": text[:1000],
            "url": url,
            "author_handle": handle,
            "date": date,
            "engagement": _normalize_engagement(raw.get("engagement")),
            "why_relevant": "Authenticated X search result",
            "relevance": _compute_relevance(topic, text),
            "metadata": {
                "extraction": "agent-browser-dom-v1",
                "date_confidence": "high",
                "media": list(raw.get("media") or [])[:16],
            },
        })
    return items


def _canonical_status_url(value: str) -> str | None:
    match = re.search(r"https?://(?:www\.)?(?:x|twitter)\.com/([^/?#]+)/status/(\d+)", value, re.I)
    if not match:
        return None
    return f"https://x.com/{match.group(1)}/status/{match.group(2)}"


def _dedupe_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    deduped = []
    for item in items:
        url = str(item.get("url") or "")
        if not url or url in seen:
            continue
        seen.add(url)
        deduped.append(item)
    return deduped


def _normalize_engagement(value: Any) -> dict[str, int]:
    raw = value if isinstance(value, dict) else {}
    return {
        key: _metric_count(raw.get(key))
        for key in ("replies", "reposts", "likes", "bookmarks", "views")
    }


def _metric_count(value: Any) -> int:
    if isinstance(value, (int, float)):
        return max(0, round(value))
    text = str(value or "").strip().upper().replace(",", "")
    match = re.search(r"(\d+(?:\.\d+)?)\s*([KMB])?", text)
    if not match:
        return 0
    multiplier = {"K": 1_000, "M": 1_000_000, "B": 1_000_000_000}.get(
        match.group(2) or "", 1
    )
    return max(0, round(float(match.group(1)) * multiplier))


def _iso_date(value: str) -> str | None:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).date().isoformat()
    except (TypeError, ValueError):
        return None


def _log(message: str) -> None:
    log.source_log("X/browser", message, tty_only=False)
