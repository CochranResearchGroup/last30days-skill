"""Facebook keyword search through an operator-visible agent-browser session.

This module intentionally does not handle Facebook credentials directly. The
operator signs into a persistent agent-browser runtime profile through the
Guacamole/RDP browser view; the engine then reuses that profile and extracts
visible search-result DOM content.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import time
from typing import Any
from urllib.parse import quote_plus

from . import log
from .relevance import token_overlap_relevance as _compute_relevance


DEPTH_CONFIG = {
    "quick": {"results": 8, "scrolls": 1, "timeout": 45},
    "default": {"results": 16, "scrolls": 2, "timeout": 75},
    "deep": {"results": 30, "scrolls": 4, "timeout": 120},
}


EXTRACT_SCRIPT = r"""
(() => {
  const clean = (value) => String(value || "").replace(/\s+/g, " ").trim();
  const articleNodes = Array.from(document.querySelectorAll('[role="article"], div[aria-posinset]'));
  const seen = new Set();
  const items = [];
  const pickUrl = (node) => {
    const anchors = Array.from(node.querySelectorAll('a[href]'));
    const preferred = anchors.find((a) => {
      const href = a.href || "";
      return /\/posts\/|\/permalink\/|story_fbid=|\/groups\/[^/]+\/posts\//.test(href);
    }) || anchors.find((a) => (a.href || "").includes("facebook.com"));
    return preferred ? preferred.href : window.location.href;
  };
  const pickAuthor = (node) => {
    const candidates = Array.from(node.querySelectorAll('h2 a, h3 a, strong a, a[role="link"]'));
    for (const candidate of candidates) {
      const text = clean(candidate.innerText || candidate.textContent);
      if (text && text.length <= 90 && !/^like|comment|share$/i.test(text)) return text;
    }
    return "";
  };
  const parseCount = (text, label) => {
    const re = new RegExp(`(\\d+(?:[,.]\\d+)?\\s*[KkMm]?)\\s+${label}`);
    const match = clean(text).match(re);
    if (!match) return 0;
    const raw = match[1].replace(",", "").toLowerCase();
    const n = parseFloat(raw);
    if (!Number.isFinite(n)) return 0;
    if (raw.endsWith("k")) return Math.round(n * 1000);
    if (raw.endsWith("m")) return Math.round(n * 1000000);
    return Math.round(n);
  };
  for (const node of articleNodes) {
    const text = clean(node.innerText || node.textContent);
    if (text.length < 30) continue;
    const url = pickUrl(node);
    const key = `${url}|${text.slice(0, 160)}`;
    if (seen.has(key)) continue;
    seen.add(key);
    items.push({
      text,
      url,
      author: pickAuthor(node),
      engagement: {
        likes: parseCount(text, "like"),
        comments: parseCount(text, "comment"),
        shares: parseCount(text, "share"),
      },
    });
  }
  const bodyText = clean(document.body ? document.body.innerText : "");
  return {
    url: window.location.href,
    title: document.title,
    login_wall: /log in|sign up|create new account|forgot password/i.test(bodyText) && items.length === 0,
    items,
  };
})()
"""


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
    """Search Facebook in an agent-browser runtime profile and return raw items."""
    config = config or {}
    if not is_agent_browser_available():
        return {"items": [], "error": "agent-browser command is not on PATH"}

    settings = DEPTH_CONFIG.get(depth, DEPTH_CONFIG["default"])
    limit = int(config.get("LAST30DAYS_FACEBOOK_MAX_RESULTS") or settings["results"])
    scrolls = int(config.get("LAST30DAYS_FACEBOOK_SCROLLS") or settings["scrolls"])
    timeout = int(config.get("LAST30DAYS_FACEBOOK_TIMEOUT") or settings["timeout"])
    profile = config.get("LAST30DAYS_FACEBOOK_PROFILE") or "last30days-facebook"
    session = config.get("LAST30DAYS_FACEBOOK_SESSION") or "last30days-facebook"
    browser_build = config.get("LAST30DAYS_FACEBOOK_BROWSER_BUILD") or "stealthcdp_chromium"
    view_provider = config.get("LAST30DAYS_FACEBOOK_VIEW_PROVIDER") or "rdp_gateway"

    url = f"https://www.facebook.com/search/posts?q={quote_plus(topic)}"
    _log(
        "Opening Facebook search via route-bound agent-browser "
        f"profile={profile!r} build={browser_build} provider={view_provider}"
    )
    open_cmd = [
        "agent-browser",
        "--json",
        "--session", session,
        "remote-view", "open", url,
        "--runtime-profile", profile,
        "--browser-build", browser_build,
        "--provider", view_provider,
    ]
    open_result = _run(open_cmd, timeout=timeout)
    if open_result.get("error"):
        return {"items": [], "error": open_result["error"]}
    visible_error = _operator_visible_error(open_result)
    if visible_error:
        return {"items": [], "error": visible_error, "url": url, "profile": profile, "session": session}

    time.sleep(float(config.get("LAST30DAYS_FACEBOOK_INITIAL_WAIT") or 4.0))
    extraction = _extract(session=session, timeout=min(timeout, 30))
    for _ in range(max(0, scrolls)):
        if len(extraction.get("items") or []) >= limit:
            break
        _run(["agent-browser", "--json", "--session", session, "scroll", "down", "1400"], timeout=15)
        time.sleep(float(config.get("LAST30DAYS_FACEBOOK_SCROLL_WAIT") or 2.0))
        extraction = _extract(session=session, timeout=min(timeout, 30))

    if extraction.get("error"):
        return {"items": [], "error": extraction["error"]}
    if extraction.get("login_wall"):
        return {
            "items": [],
            "error": "Facebook login wall detected. Sign into the agent-browser runtime profile first.",
            "url": extraction.get("url") or url,
        }

    items = _parse_items(extraction.get("items") or [], topic, limit=limit)
    return {
        "items": items,
        "url": extraction.get("url") or url,
        "title": extraction.get("title") or "",
        "profile": profile,
        "session": session,
        "from_date": from_date,
        "to_date": to_date,
    }


def _extract(*, session: str, timeout: int) -> dict[str, Any]:
    cmd = ["agent-browser", "--json", "--session", session, "eval", "--stdin"]
    return _run(cmd, timeout=timeout, input_text=EXTRACT_SCRIPT)


def _operator_visible_error(payload: dict[str, Any]) -> str | None:
    """Return a durable handoff error unless agent-browser proved browser visibility."""
    operator_visible = payload.get("operatorVisible")
    if not isinstance(operator_visible, dict):
        return "agent-browser remote-view open did not return operatorVisible proof; refusing CDP-only Facebook success"
    if operator_visible.get("state") == "ready":
        return None
    proof = operator_visible.get("proof")
    display_content = proof.get("displayContent") if isinstance(proof, dict) else None
    display_state = display_content.get("state") if isinstance(display_content, dict) else None
    summary = {
        "state": operator_visible.get("state") or "missing",
        "routeId": operator_visible.get("routeId") or payload.get("routeId"),
        "displayAllocationId": operator_visible.get("displayAllocationId") or payload.get("displayAllocationId"),
        "displayName": operator_visible.get("displayName"),
        "browserId": operator_visible.get("browserId") or payload.get("browserId"),
        "sessionName": operator_visible.get("sessionName") or payload.get("sessionName"),
        "proof": display_state or (proof.get("state") if isinstance(proof, dict) else None) or "missing",
    }
    compact = " ".join(f"{key}={value}" for key, value in summary.items() if value)
    return f"Facebook remote browser is not operator-visible ({compact}); rerun agent-browser remote-view open and sign in through the Guacamole/RDP browser"


def _run(cmd: list[str], *, timeout: int, input_text: str | None = None) -> dict[str, Any]:
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
    except subprocess.TimeoutExpired:
        return {"error": f"agent-browser command timed out after {timeout}s"}
    except OSError as exc:
        return {"error": str(exc)}

    if result.returncode != 0:
        return {"error": (result.stderr or result.stdout or "agent-browser command failed").strip()}
    stdout = (result.stdout or "").strip()
    if not stdout:
        return {}
    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError:
        return {"value": stdout}
    if isinstance(payload, dict) and payload.get("success") is False:
        return {"error": str(payload.get("error") or payload)}
    data = payload.get("data") if isinstance(payload, dict) else payload
    if isinstance(data, str):
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            return {"value": data}
    if isinstance(data, dict):
        value = data.get("value") or data.get("result")
        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return {"value": value}
        if isinstance(value, dict):
            return value
        return data
    return {"value": data}


def _parse_items(raw_items: list[dict[str, Any]], topic: str, *, limit: int) -> list[dict[str, Any]]:
    parsed: list[dict[str, Any]] = []
    seen: set[str] = set()
    for raw in raw_items:
        text = str(raw.get("text") or "").strip()
        if not text:
            continue
        url = str(raw.get("url") or "https://www.facebook.com").strip()
        digest = hashlib.sha1(f"{url}\n{text[:300]}".encode("utf-8")).hexdigest()[:16]
        if digest in seen:
            continue
        seen.add(digest)
        author = str(raw.get("author") or "").strip()
        engagement = _clean_engagement(raw.get("engagement") or {})
        relevance = max(0.3, min(1.0, _compute_relevance(topic, text) + 0.2))
        parsed.append({
            "id": f"FB{digest}",
            "text": text,
            "url": url,
            "author": author,
            "date": None,
            "engagement": engagement,
            "relevance": round(relevance, 2),
            "why_relevant": f"Facebook post: {text[:80]}",
            "metadata": {
                "extraction": "agent-browser-dom",
                "remote_browser": True,
            },
        })
        if len(parsed) >= limit:
            break
    return parsed


def _clean_engagement(raw: dict[str, Any]) -> dict[str, int]:
    cleaned: dict[str, int] = {}
    for key in ("likes", "comments", "shares"):
        try:
            cleaned[key] = max(0, int(raw.get(key) or 0))
        except (TypeError, ValueError):
            cleaned[key] = 0
    return cleaned


def parse_facebook_response(response: dict[str, Any]) -> list[dict[str, Any]]:
    if response.get("error"):
        _log(str(response["error"]))
    items = response.get("items") or []
    if not isinstance(items, list):
        return []
    return [item for item in items if isinstance(item, dict)]
