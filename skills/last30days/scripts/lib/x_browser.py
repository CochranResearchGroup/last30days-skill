"""Quality-gated X search through an authenticated agent-browser profile."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
import re
import time
from typing import Any
from urllib.parse import parse_qs, quote, unquote, urlsplit

from . import agent_browser_config, agent_browser_runtime as browser_runtime, log
from .relevance import token_overlap_relevance as _compute_relevance


DEPTH_CONFIG = {
    "quick": {"results": 8, "scrolls": 0, "timeout": 45},
    "default": {"results": 16, "scrolls": 1, "timeout": 75},
    "deep": {"results": 30, "scrolls": 2, "timeout": 120},
}
MAX_EXPLICIT_RESULTS = 100
MAX_EXPLICIT_SCROLLS = 8
ACCEPTED_ITEMS_PER_SCROLL_BUDGET = 5
MAX_EXPLICIT_FEED_SCROLLS = 32
FEED_ACCEPTED_ITEMS_PER_SCROLL_BUDGET = 2
MAX_STAGNANT_SCROLLS = 2

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
    "auth_state_ambiguous",
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
    def __init__(
        self,
        error_type: str,
        message: str,
        *,
        operator_url: str = "",
        reason_code: str = "",
    ) -> None:
        super().__init__(message)
        self.error_type = error_type if error_type in ERROR_TYPES else "agent_browser_error"
        self.operator_url = operator_url
        self.reason_code = reason_code


AUTH_SCRIPT = r"""
(() => {
  const body = (document.body?.innerText || "").slice(0, 12000);
  const checkpointUrl = /\/(?:i\/flow|account\/access|challenge)(?:\/|$|\?)/i.test(location.href);
  const checkpointBody = /verify your identity|confirm your identity|security checkpoint|complete this challenge to continue/i.test(body);
  const authenticatedDom = Boolean(
    document.querySelector('[data-testid="SideNav_AccountSwitcher_Button"], nav[aria-label="Primary"]')
  );
  const rootSignedOut = /^\/?$/.test(location.pathname) &&
    /happening now/i.test(body) &&
    /continue with (?:google|apple)|email or username/i.test(body);
  return {
    url: location.href,
    title: document.title,
    login_form: Boolean(document.querySelector('a[href="/login"], input[autocomplete="username"]')) ||
      rootSignedOut,
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
  const rootSignedOut = /^\/?$/.test(location.pathname) &&
    /happening now/i.test(body) &&
    /continue with (?:google|apple)|email or username/i.test(body);
  return {
    url: location.href,
    title: document.title,
    query_value: String(search?.value || "").trim(),
    latest_selected: Boolean(latest && latest.getAttribute("aria-selected") === "true") ||
      new URL(location.href).searchParams.get("f") === "live",
    article_count: document.querySelectorAll("article").length,
    no_results: /no results|try searching for something else/i.test(body),
    login_page: Boolean(document.querySelector('a[href="/login"], input[autocomplete="username"]')) ||
      rootSignedOut,
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
    const clean = (value) => String(value || "").replace(/\s+/g, " ").trim();
    const time = article.querySelector("time[datetime]");
    const status = time?.closest('a[href*="/status/"]') || article.querySelector('a[href*="/status/"]');
    const textNodes = Array.from(article.querySelectorAll('[data-testid="tweetText"]'));
    const text = clean(textNodes[0]?.innerText || "").slice(0, 2000);
    const quotedText = textNodes.slice(1)
      .map((node) => clean(node.innerText || ""))
      .filter(Boolean)
      .join("\n\n")
      .slice(0, 2000);
    const metric = (testId) => {
      const node = article.querySelector(`[data-testid="${testId}"]`);
      return String(node?.getAttribute("aria-label") || node?.innerText || "").trim();
    };
    const media = [
      ...Array.from(article.querySelectorAll('[data-testid="tweetPhoto"] img, img[src*="pbs.twimg.com/media"]'))
        .map((image) => ({
          kind: "image", url: image.currentSrc || image.src || "",
          preview_url: null, mime_type: null,
          width: image.naturalWidth || null, height: image.naturalHeight || null,
          duration_seconds: null, alt_text: clean(image.alt || "") || null
        })),
      ...Array.from(article.querySelectorAll("video"))
        .map((video) => ({
          kind: "video", url: status?.href || "",
          preview_url: video.poster || null, mime_type: null,
          width: video.videoWidth || null, height: video.videoHeight || null,
          duration_seconds: Number.isFinite(video.duration) ? Math.round(video.duration) : null,
          alt_text: null
        }))
    ].filter((asset) => asset.url);
    const mediaAltText = [...new Set(media
      .map((asset) => clean(asset.alt_text || ""))
      .filter((value) => value && !/^(?:image|photo|video|media)$/i.test(value))
    )].slice(0, 8);
    const contextText = [quotedText, ...mediaAltText].filter(Boolean).join("\n").slice(0, 2000);
    return {
      text,
      context_text: contextText,
      quoted_text: quotedText,
      media_alt_text: mediaAltText,
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
      media
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
    rejected_candidates: list[dict[str, Any]] = field(default_factory=list)
    candidate_count: int = 0
    accepted_count: int = 0
    duration_ms: int = 0
    scroll_count: int = 0
    unique_observation_count: int = 0
    stagnant_scrolls: int = 0

    def reject(
        self,
        reason: str,
        *,
        source_native_id: str = "",
        text_length: int = 0,
        context_length: int = 0,
        has_quote_context: bool = False,
        media_count: int = 0,
    ) -> None:
        self.rejection_counts[reason] += 1
        if len(self.rejected_candidates) >= 32:
            return
        self.rejected_candidates.append({
            "reason": reason,
            "source_native_id": source_native_id,
            "text_length": max(0, text_length),
            "context_length": max(0, context_length),
            "has_quote_context": has_quote_context,
            "media_count": max(0, media_count),
        })

    def as_dict(self) -> dict[str, Any]:
        return {
            "rejection_counts": dict(self.rejection_counts),
            "rejected_candidates": list(self.rejected_candidates),
            "candidate_count": self.candidate_count,
            "accepted_count": self.accepted_count,
            "duration_ms": self.duration_ms,
            "scroll_count": self.scroll_count,
            "unique_observation_count": self.unique_observation_count,
            "stagnant_scrolls": self.stagnant_scrolls,
        }


class CliAgentBrowserClient(browser_runtime.CliAgentBrowserClient):
    def acquire_workspace(self, request: BrowserWorkspaceRequest) -> BrowserWorkspace:
        access_plan = self._invoke(
            [
                "service", "access-plan",
                "--service-name", "last30days",
                "--agent-name", "x-scraper",
                "--task-name", request.task_name or "x-search",
                "--target-service-id", "x",
                "--runtime-profile", request.profile_id,
                "--url", request.start_url or "https://x.com/search",
                "--browser-build", request.browser_build,
                "--browser-host", request.browser_host,
                "--view-stream-provider", request.view_provider,
                "--control-input-provider", request.control_input_provider,
                "--display-isolation", request.display_isolation,
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
        decision = access_plan.get("decision") if isinstance(access_plan.get("decision"), dict) else {}
        if decision.get("manualActionRequired") or decision.get("manualSeedingRequired"):
            raise XBrowserFailure(
                "auth_required",
                "agent-browser reports that the selected X profile requires operator authentication",
            )
        try:
            return super().acquire_workspace(
                request,
                access_plan=access_plan,
                target_service_id="x",
            )
        except browser_runtime.AgentBrowserRuntimeFailure as exc:
            raise XBrowserFailure(
                exc.error_type,
                str(exc),
                operator_url=exc.operator_url,
                reason_code=exc.reason_code,
            ) from exc

    def inspect_auth(self, workspace: BrowserWorkspace) -> XAuthState:
        if not self.prepare_site_tab(workspace, "x.com", consolidate=True):
            self.act(workspace, BrowserAction("new_tab", value="https://x.com/home"))
            self.act(workspace, BrowserAction("wait", value="2500"))
            self._prepared_sites.add((workspace.session_name, "x.com"))
        raw = self.evaluate(workspace, AUTH_SCRIPT)
        auth = _auth_state(raw)
        if not (
            auth.authenticated
            or auth.login_form
            or auth.checkpoint
            or auth.restricted
        ):
            # X can retain an authenticated tab on a non-terminal loading
            # screen after profile startup. Reload once before treating that
            # ambiguous DOM as proof that operator authentication is required.
            self.act(workspace, BrowserAction("navigate", value="https://x.com/home"))
            self.act(workspace, BrowserAction("wait", value="2500"))
            raw = self.evaluate(workspace, AUTH_SCRIPT)
            auth = _auth_state(raw)
        return auth


def _auth_state(raw: dict[str, Any]) -> XAuthState:
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
        self.failure_stage = "workspace_acquisition"

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
        if auth.login_form:
            raise XBrowserFailure(
                "auth_required",
                "X authentication is required",
                operator_url=workspace.operator_url,
            )
        if not auth.authenticated:
            raise XBrowserFailure(
                "auth_state_ambiguous",
                "X authentication state could not be determined from the rendered page",
                operator_url=workspace.operator_url,
            )
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
            raise XBrowserFailure(
                "checkpoint_required",
                "X search opened a security checkpoint",
                operator_url=workspace.operator_url,
            )
        if page.restricted:
            raise XBrowserFailure("rate_limited", "X search reported an account restriction or rate limit")
        if page.login_page:
            raise XBrowserFailure(
                "auth_required",
                "X search redirected to login",
                operator_url=workspace.operator_url,
            )
        if page.error_page:
            raise XBrowserFailure("search_unavailable", "X search returned a temporary error page")
        if not _page_matches_query(page, query):
            raise XBrowserFailure("navigation_mismatch", "X search state did not match the requested query")
        raw = list(self.client.evaluate(workspace, EXTRACT_SCRIPT).get("candidates") or [])
        for _ in range(self.scrolls):
            if _accepted_unique_count(raw, topic, from_date, to_date) >= self.limit:
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
        diagnostics.candidate_count = len(raw)
        quality_items = _quality_gate(raw, topic, from_date, to_date, diagnostics)
        deduped_items = _dedupe_items(quality_items, diagnostics)
        result_limit_count = max(0, len(deduped_items) - self.limit)
        if result_limit_count:
            for item in deduped_items[self.limit:]:
                _record_item_rejection(diagnostics, "result_limit", item)
        items = deduped_items[: self.limit]
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

    def feed(self, from_date: str, to_date: str) -> dict[str, Any]:
        """Collect structurally valid posts from the authenticated home feed."""
        started = time.monotonic()
        diagnostics = XRunDiagnostics()
        self.failure_stage = "workspace_acquisition"
        workspace = self.client.acquire_workspace(self.request)
        self.failure_stage = "authentication"
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
        if auth.login_form:
            raise XBrowserFailure(
                "auth_required",
                "X authentication is required",
                operator_url=workspace.operator_url,
            )
        if not auth.authenticated:
            raise XBrowserFailure(
                "auth_state_ambiguous",
                "X authentication state could not be determined from the rendered page",
                operator_url=workspace.operator_url,
            )
        self.failure_stage = "navigation"
        feed_url = "https://x.com/home"
        retained = self.client.prepare_site_tab(workspace, "x.com", consolidate=True)
        self.client.act(
            workspace,
            BrowserAction("navigate" if retained else "new_tab", value=feed_url),
        )
        self.client.act(
            workspace,
            BrowserAction("wait", value=str(max(0, round(self.initial_wait * 1000)))),
        )
        page = _page_state(self.client.evaluate(workspace, PAGE_STATE_SCRIPT))
        if page.checkpoint:
            raise XBrowserFailure(
                "checkpoint_required",
                "X feed opened a security checkpoint",
                operator_url=workspace.operator_url,
            )
        if page.restricted:
            raise XBrowserFailure("rate_limited", "X feed reported an account restriction or rate limit")
        if page.login_page:
            raise XBrowserFailure(
                "auth_required",
                "X feed redirected to login",
                operator_url=workspace.operator_url,
            )
        if page.error_page:
            raise XBrowserFailure("search_unavailable", "X feed returned a temporary error page")
        if not _page_matches_feed(page):
            raise XBrowserFailure("navigation_mismatch", "X feed state did not match the authenticated home feed")
        self.failure_stage = "extraction"
        raw = list(self.client.evaluate(workspace, EXTRACT_SCRIPT).get("candidates") or [])
        seen_observations = {_candidate_observation_key(item) for item in raw}
        diagnostics.unique_observation_count = len(seen_observations)
        stagnant_scrolls = 0
        for _ in range(self.scrolls):
            if _accepted_unique_count(
                raw, "", from_date, to_date, surface_kind="feed"
            ) >= self.limit:
                break
            self.client.evaluate(workspace, SCROLL_SCRIPT)
            diagnostics.scroll_count += 1
            self.client.act(
                workspace,
                BrowserAction("wait", value=str(max(0, round(self.scroll_wait * 1000)))),
            )
            batch = list(
                self.client.evaluate(workspace, EXTRACT_SCRIPT).get("candidates") or []
            )
            new_observations = {
                _candidate_observation_key(item) for item in batch
            } - seen_observations
            seen_observations.update(new_observations)
            raw.extend(batch)
            stagnant_scrolls = 0 if new_observations else stagnant_scrolls + 1
            diagnostics.unique_observation_count = len(seen_observations)
            diagnostics.stagnant_scrolls = stagnant_scrolls
            if stagnant_scrolls >= MAX_STAGNANT_SCROLLS:
                break
        if not raw:
            raise XBrowserFailure(
                "extraction_empty",
                "Verified X home feed contained no post articles",
            )
        diagnostics.candidate_count = len(raw)
        self.failure_stage = "quality_gate"
        quality_items = _quality_gate(
            raw, "", from_date, to_date, diagnostics, surface_kind="feed"
        )
        deduped_items = _dedupe_items(quality_items, diagnostics)
        result_limit_count = max(0, len(deduped_items) - self.limit)
        if result_limit_count:
            for item in deduped_items[self.limit:]:
                _record_item_rejection(diagnostics, "result_limit", item)
        items = deduped_items[: self.limit]
        diagnostics.duration_ms = round((time.monotonic() - started) * 1000)
        diagnostics.accepted_count = len(items)
        error_type = "quality_gate_failed" if raw and not items else None
        return {
            "items": items,
            "error": "X feed candidates were found, but none passed the post quality gate" if error_type else None,
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
    limit: int | None = None,
) -> dict[str, Any]:
    config = config or {}
    stable = agent_browser_config.load_target_config("x")
    settings = DEPTH_CONFIG.get(depth, DEPTH_CONFIG["default"])
    result_limit = (
        settings["results"]
        if limit is None
        else max(1, min(MAX_EXPLICIT_RESULTS, int(limit)))
    )
    scrolls = settings["scrolls"]
    if limit is not None:
        scrolls = max(
            scrolls,
            min(
                MAX_EXPLICIT_SCROLLS,
                (result_limit + ACCEPTED_ITEMS_PER_SCROLL_BUDGET - 1)
                // ACCEPTED_ITEMS_PER_SCROLL_BUDGET,
            ),
        )
    request = BrowserWorkspaceRequest(
        profile_id=str(
            config.get("LAST30DAYS_X_BROWSER_PROFILE")
            or stable.get("profile_id")
            or "last30days-facebook"
        ),
        session_name=str(config.get("LAST30DAYS_X_BROWSER_SESSION") or "last30days-facebook"),
        browser_build=str(
            config.get("LAST30DAYS_X_BROWSER_BUILD")
            or stable.get("browser_build")
            or "stealthcdp_chromium"
        ),
        view_provider=str(
            config.get("LAST30DAYS_X_BROWSER_VIEW_PROVIDER")
            or stable.get("view_stream_provider")
            or "rdp_gateway"
        ),
        timeout=int(config.get("LAST30DAYS_X_BROWSER_TIMEOUT") or settings["timeout"]),
        start_url="https://x.com/home",
        service_name="last30days",
        agent_name="x-scraper",
        task_name="x-search",
        target_service_id="x",
        display_isolation=str(
            config.get("LAST30DAYS_AGENT_BROWSER_DISPLAY_ISOLATION")
            or stable.get("display_isolation")
            or "shared_display"
        ),
        browser_host=str(stable.get("browser_host") or "remote_headed"),
        control_input_provider=str(
            stable.get("control_input_provider") or "manual_attached_desktop"
        ),
        allow_duplicate_profile_lane=browser_runtime.config_flag(
            config.get("LAST30DAYS_AGENT_BROWSER_ALLOW_DUPLICATE_PROFILE_LANE")
        ),
    )
    client = CliAgentBrowserClient(
        timeout=request.timeout,
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
    scraper = XBrowserScraper(
        client,
        request,
        limit=result_limit,
        scrolls=scrolls,
        initial_wait=float(config.get("LAST30DAYS_X_BROWSER_INITIAL_WAIT") or 2),
        scroll_wait=float(config.get("LAST30DAYS_X_BROWSER_SCROLL_WAIT") or 1),
        now=config.get("_NOW"),
    )
    try:
        return scraper.search(topic, from_date, to_date)
    except XBrowserFailure as exc:
        _log(f"Failed error_type={exc.error_type} message={exc}")
        diagnostics = {"rejection_counts": {}, "accepted_count": 0, "duration_ms": 0}
        if exc.reason_code:
            diagnostics["failure_reason_code"] = exc.reason_code
        if exc.operator_url:
            diagnostics["operator_url"] = exc.operator_url
        return {
            "items": [],
            "error": str(exc),
            "error_type": exc.error_type,
            "profile": request.profile_id,
            "session": request.session_name,
            "operator_url": exc.operator_url or None,
            "diagnostics": diagnostics,
        }
    except browser_runtime.AgentBrowserRuntimeFailure as exc:
        error_type = exc.error_type if exc.error_type in ERROR_TYPES else "agent_browser_error"
        _log(f"Failed error_type={error_type} message={exc}")
        operator_url = str(getattr(exc, "operator_url", "") or "")
        diagnostics = {"rejection_counts": {}, "accepted_count": 0, "duration_ms": 0}
        if exc.reason_code:
            diagnostics["failure_reason_code"] = exc.reason_code
        if operator_url:
            diagnostics["operator_url"] = operator_url
        return {
            "items": [],
            "error": str(exc),
            "error_type": error_type,
            "profile": request.profile_id,
            "session": request.session_name,
            "operator_url": operator_url or None,
            "diagnostics": diagnostics,
        }
    finally:
        try:
            client.release_workspace()
        except browser_runtime.AgentBrowserRuntimeFailure as exc:
            _log(f"Best-effort X service tab release did not complete: {exc}")


def scrape_x_feed(
    from_date: str,
    to_date: str,
    *,
    depth: str = "default",
    config: dict[str, Any] | None = None,
    limit: int | None = None,
) -> dict[str, Any]:
    """Scrape the authenticated X home feed without applying a topic query."""
    config = config or {}
    stable = agent_browser_config.load_target_config("x")
    settings = DEPTH_CONFIG.get(depth, DEPTH_CONFIG["default"])
    result_limit = (
        settings["results"]
        if limit is None
        else max(1, min(MAX_EXPLICIT_RESULTS, int(limit)))
    )
    scrolls = settings["scrolls"]
    if limit is not None:
        scrolls = min(
            MAX_EXPLICIT_FEED_SCROLLS,
            max(
                MAX_EXPLICIT_SCROLLS,
                (
                    result_limit
                    + FEED_ACCEPTED_ITEMS_PER_SCROLL_BUDGET
                    - 1
                )
                // FEED_ACCEPTED_ITEMS_PER_SCROLL_BUDGET,
            ),
        )
    request = BrowserWorkspaceRequest(
        profile_id=str(
            config.get("LAST30DAYS_X_BROWSER_PROFILE")
            or stable.get("profile_id")
            or "last30days-facebook"
        ),
        session_name=str(config.get("LAST30DAYS_X_BROWSER_SESSION") or "last30days-facebook"),
        browser_build=str(
            config.get("LAST30DAYS_X_BROWSER_BUILD")
            or stable.get("browser_build")
            or "stealthcdp_chromium"
        ),
        view_provider=str(
            config.get("LAST30DAYS_X_BROWSER_VIEW_PROVIDER")
            or stable.get("view_stream_provider")
            or "rdp_gateway"
        ),
        timeout=int(config.get("LAST30DAYS_X_BROWSER_TIMEOUT") or settings["timeout"]),
        start_url="https://x.com/home",
        service_name="last30days",
        agent_name="x-scraper",
        task_name="x-feed",
        target_service_id="x",
        display_isolation=str(
            config.get("LAST30DAYS_AGENT_BROWSER_DISPLAY_ISOLATION")
            or stable.get("display_isolation")
            or "shared_display"
        ),
        browser_host=str(stable.get("browser_host") or "remote_headed"),
        control_input_provider=str(
            stable.get("control_input_provider") or "manual_attached_desktop"
        ),
        allow_duplicate_profile_lane=browser_runtime.config_flag(
            config.get("LAST30DAYS_AGENT_BROWSER_ALLOW_DUPLICATE_PROFILE_LANE")
        ),
    )
    client = CliAgentBrowserClient(
        timeout=request.timeout,
        **(
            {"job_timeout_ms": int(config["LAST30DAYS_AGENT_BROWSER_JOB_TIMEOUT_MS"])}
            if config.get("LAST30DAYS_AGENT_BROWSER_JOB_TIMEOUT_MS")
            else {}
        ),
    )
    scraper = XBrowserScraper(
        client,
        request,
        limit=result_limit,
        scrolls=scrolls,
        initial_wait=float(config.get("LAST30DAYS_X_BROWSER_INITIAL_WAIT") or 2),
        scroll_wait=float(config.get("LAST30DAYS_X_BROWSER_SCROLL_WAIT") or 1),
        now=config.get("_NOW"),
    )
    try:
        return scraper.feed(from_date, to_date)
    except XBrowserFailure as exc:
        _log(f"Failed error_type={exc.error_type} message={exc}")
        diagnostics = _failure_diagnostics(scraper, client, exc.operator_url)
        if exc.reason_code:
            diagnostics["failure_reason_code"] = exc.reason_code
        return {
            "items": [],
            "error": str(exc),
            "error_type": exc.error_type,
            "profile": request.profile_id,
            "session": request.session_name,
            "operator_url": exc.operator_url or None,
            "diagnostics": diagnostics,
        }
    except browser_runtime.AgentBrowserRuntimeFailure as exc:
        error_type = exc.error_type if exc.error_type in ERROR_TYPES else "agent_browser_error"
        _log(f"Failed error_type={error_type} message={exc}")
        operator_url = str(getattr(exc, "operator_url", "") or "")
        diagnostics = _failure_diagnostics(scraper, client, operator_url)
        if exc.reason_code:
            diagnostics["failure_reason_code"] = exc.reason_code
        return {
            "items": [],
            "error": str(exc),
            "error_type": error_type,
            "profile": request.profile_id,
            "session": request.session_name,
            "operator_url": operator_url or None,
            "diagnostics": diagnostics,
        }
    finally:
        try:
            client.release_workspace()
        except browser_runtime.AgentBrowserRuntimeFailure as exc:
            _log(f"Best-effort X service tab release did not complete: {exc}")


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


def _page_matches_feed(page: XPageState) -> bool:
    parsed = urlsplit(page.url)
    return (
        parsed.hostname in {"x.com", "www.x.com", "twitter.com", "www.twitter.com"}
        and parsed.path.rstrip("/") == "/home"
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
    *,
    surface_kind: str = "topic",
) -> list[dict[str, Any]]:
    items = []
    for index, raw in enumerate(candidates):
        url = _canonical_status_url(str(raw.get("url") or ""))
        text = re.sub(r"\s+", " ", str(raw.get("text") or "")).strip()
        context_text = re.sub(
            r"\s+", " ", str(raw.get("context_text") or "")
        ).strip()[:2000]
        evidence_text = f"{text} {context_text}".strip()
        handle = str(raw.get("author_handle") or "").lstrip("@")
        date = _iso_date(str(raw.get("timestamp") or ""))
        relevance = (
            _compute_relevance(topic, evidence_text)
            if surface_kind == "topic"
            else 0.5
        )
        retrieval_signals: list[str] = []
        if len(evidence_text) < 30:
            retrieval_signals.append("short_text")
        if surface_kind == "topic" and relevance <= 0:
            retrieval_signals.append("no_lexical_topic_overlap")
        reason = None
        if not url:
            reason = "missing_permalink"
        elif not handle:
            reason = "missing_author"
        elif raw.get("promoted"):
            reason = "promoted"
        elif not date or not (from_date <= date <= to_date):
            reason = "out_of_range"
        if reason:
            media = raw.get("media")
            diagnostics.reject(
                reason,
                source_native_id=url.rsplit("/", 1)[-1] if url else "",
                text_length=len(text),
                context_length=len(context_text),
                has_quote_context=bool(str(raw.get("quoted_text") or "").strip()),
                media_count=len(media) if isinstance(media, list) else 0,
            )
            continue
        rendered_text = (
            f"{text}\n\nAttached context: {context_text}" if context_text else text
        ).strip()[:1000]
        items.append({
            "id": f"X{index + 1}",
            "source_native_id": url.rsplit("/", 1)[-1],
            "text": rendered_text,
            "url": url,
            "author_handle": handle,
            "date": date,
            "engagement": _normalize_engagement(raw.get("engagement")),
            "why_relevant": (
                "Authenticated X search result"
                if surface_kind == "topic"
                else "Authenticated X home feed post"
            ),
            "relevance": relevance,
            "metadata": {
                "extraction": "agent-browser-dom-v1",
                "date_confidence": "high",
                "retrieval_signals": retrieval_signals,
                "media": list(raw.get("media") or [])[:16],
                "quoted_text": str(raw.get("quoted_text") or "")[:1000],
                "media_alt_text": [
                    str(value)[:500]
                    for value in list(raw.get("media_alt_text") or [])[:8]
                    if str(value).strip()
                ],
            },
        })
    return items


def _accepted_unique_count(
    candidates: list[dict[str, Any]],
    topic: str,
    from_date: str,
    to_date: str,
    *,
    surface_kind: str = "topic",
) -> int:
    """Preview accepted unique yield without mutating the run diagnostics."""
    preview = XRunDiagnostics()
    return len(
        _dedupe_items(
            _quality_gate(
                candidates,
                topic,
                from_date,
                to_date,
                preview,
                surface_kind=surface_kind,
            )
        )
    )


def _candidate_observation_key(candidate: dict[str, Any]) -> str:
    """Identify one rendered status across overlapping virtualized snapshots."""
    canonical_url = _canonical_status_url(str(candidate.get("url") or ""))
    if canonical_url:
        return canonical_url
    return "\n".join(
        (
            str(candidate.get("author_handle") or "").casefold().strip(),
            str(candidate.get("timestamp") or "").strip(),
            re.sub(r"\s+", " ", str(candidate.get("text") or "")).casefold()[:500],
        )
    )


def _canonical_status_url(value: str) -> str | None:
    match = re.search(r"https?://(?:www\.)?(?:x|twitter)\.com/([^/?#]+)/status/(\d+)", value, re.I)
    if not match:
        return None
    return f"https://x.com/{match.group(1)}/status/{match.group(2)}"


def _dedupe_items(
    items: list[dict[str, Any]],
    diagnostics: XRunDiagnostics | None = None,
) -> list[dict[str, Any]]:
    seen: set[str] = set()
    deduped = []
    for item in items:
        url = str(item.get("url") or "")
        if not url or url in seen:
            if diagnostics is not None:
                _record_item_rejection(diagnostics, "duplicate_status", item)
            continue
        seen.add(url)
        deduped.append(item)
    return deduped


def _record_item_rejection(
    diagnostics: XRunDiagnostics,
    reason: str,
    item: dict[str, Any],
) -> None:
    metadata = item.get("metadata")
    metadata = metadata if isinstance(metadata, dict) else {}
    quoted_text = str(metadata.get("quoted_text") or "").strip()
    media_alt_text = metadata.get("media_alt_text")
    media_alt_text = media_alt_text if isinstance(media_alt_text, list) else []
    context_length = len(
        " ".join(
            value
            for value in [
                quoted_text,
                *(str(value).strip() for value in media_alt_text),
            ]
            if value
        )
    )
    media = metadata.get("media")
    diagnostics.reject(
        reason,
        source_native_id=str(item.get("source_native_id") or ""),
        text_length=len(str(item.get("text") or "")),
        context_length=context_length,
        has_quote_context=bool(quoted_text),
        media_count=len(media) if isinstance(media, list) else 0,
    )


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


def _failure_diagnostics(
    scraper: XBrowserScraper,
    client: Any,
    operator_url: str,
) -> dict[str, Any]:
    diagnostics: dict[str, Any] = {
        "rejection_counts": {},
        "accepted_count": 0,
        "duration_ms": 0,
        "failure_stage": scraper.failure_stage,
        "browser_operations": _bounded_browser_operations(
            getattr(client, "command_timings", [])
        ),
    }
    if operator_url:
        diagnostics["operator_url"] = operator_url
    return diagnostics


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


def _log(message: str) -> None:
    log.source_log("X/browser", message, tty_only=False)
