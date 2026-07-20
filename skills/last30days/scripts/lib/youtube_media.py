"""Bounded YouTube media operations for the last30days skill."""

from __future__ import annotations

import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable, Optional
from urllib.parse import parse_qs, urlparse

from . import facebook as browser_runtime, subproc, youtube_yt


Runner = Callable[..., subproc.SubprocResult]
_VIDEO_ID_RE = re.compile(r"^[A-Za-z0-9_-]{6,20}$")


_SUBSCRIPTIONS_SCRIPT = r"""
(() => {
  const pageText = document.body?.innerText || "";
  if (pageText.includes("Sign in to see updates from your favorite YouTube channels")) {
    return {state: "signed_out", items: []};
  }
  const limit = __LIMIT__;
  const items = [];
  const seen = new Set();
  for (const card of document.querySelectorAll("ytd-rich-item-renderer, ytd-grid-video-renderer")) {
    const links = Array.from(card.querySelectorAll('a[href*="watch?v="]'));
    const titleLink = links.find((link) => (link.getAttribute("aria-label") || "").trim()) ||
      links.find((link) => (link.textContent || "").trim() && !(link.textContent || "").trim().match(/^\d+:\d/));
    if (!titleLink) continue;
    const url = new URL(titleLink.href, location.origin);
    const videoId = url.searchParams.get("v") || "";
    if (!videoId || seen.has(videoId)) continue;
    seen.add(videoId);
    const lines = (card.innerText || "").split("\n").map((line) => line.trim()).filter(Boolean);
    const title = (titleLink.textContent || "").trim();
    const duration = lines.find((line) => /^\d+:\d/.test(line)) || "";
    const titleIndex = lines.indexOf(title);
    const channel = titleIndex >= 0 ? (lines[titleIndex + 1] || "") : "";
    const published = lines.find((line) => /ago$|Streamed|Premiered/.test(line)) || "";
    items.push({video_id: videoId, title, channel, published, duration,
      url: `https://www.youtube.com/watch?v=${videoId}`});
    if (items.length >= limit) break;
  }
  return {state: items.length ? "ok" : "empty", items};
})()
"""


def _setting(config: Optional[dict], key: str, default: str = "") -> str:
    value = (config or {}).get(key) or os.environ.get(key) or default
    return str(value).strip()


def video_id(url: str) -> str:
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower().rstrip(".")
    if host in {"youtu.be", "www.youtu.be"}:
        candidate = parsed.path.strip("/").split("/", 1)[0]
    elif host == "youtube.com" or host.endswith(".youtube.com"):
        candidate = parse_qs(parsed.query).get("v", [""])[0]
        if not candidate and parsed.path.startswith("/shorts/"):
            candidate = parsed.path.split("/", 3)[2]
    else:
        raise ValueError("a youtube.com or youtu.be video URL is required")
    if not _VIDEO_ID_RE.fullmatch(candidate):
        raise ValueError("the YouTube URL does not contain a valid video id")
    return candidate


def _transcribe_audio_dir(config: Optional[dict]) -> Optional[Path]:
    configured = _setting(config, "LAST30DAYS_TRANSCRIBE_AUDIO_DIR")
    if configured:
        candidate = Path(configured).expanduser()
        return candidate.resolve() if (candidate / "faster_whisper_transcribe.py").is_file() else None
    candidates = [
        Path.cwd().parent / "transcribe-audio",
        Path.home() / "workspace.local" / "transcribe-audio",
    ]
    for candidate in candidates:
        if (candidate / "faster_whisper_transcribe.py").is_file():
            return candidate.resolve()
    return None


def doctor(config: Optional[dict] = None, runner: Runner = subproc.run_with_timeout) -> dict:
    ytdlp = shutil.which("yt-dlp")
    version = ""
    state = "missing"
    reason = "yt-dlp not found on PATH"
    if ytdlp:
        try:
            result = runner(["yt-dlp", "--version"], timeout=10)
            if result.returncode == 0:
                version = (result.stdout or "").strip().splitlines()[0]
                state, reason = "ready", ""
            else:
                state, reason = "broken", (result.stderr or "yt-dlp failed").strip()[:200]
        except Exception as exc:
            state, reason = "broken", type(exc).__name__
    js_runtime = "deno" if shutil.which("deno") else ("node" if shutil.which("node") else "")
    if state == "ready" and not js_runtime:
        state, reason = "warning", "yt-dlp has no Node.js or Deno JavaScript runtime"
    transcribe_dir = _transcribe_audio_dir(config)
    return {
        "ok": state == "ready",
        "youtube": {
            "state": state,
            "reason": reason,
            "yt_dlp_path": ytdlp or "",
            "yt_dlp_version": version,
            "js_runtime": js_runtime,
            "ffmpeg": bool(shutil.which("ffmpeg")),
            "agent_browser": bool(shutil.which("agent-browser")),
        },
        "transcribe_audio": {
            "available": transcribe_dir is not None,
            "path": str(transcribe_dir or ""),
        },
    }


def subscriptions(
    limit: int = 12,
    config: Optional[dict] = None,
    client: Optional[Any] = None,
) -> dict:
    limit = max(1, min(int(limit), 50))
    timeout = int(_setting(config, "LAST30DAYS_YOUTUBE_BROWSER_TIMEOUT", "75"))
    request = browser_runtime.BrowserWorkspaceRequest(
        profile_id=_setting(config, "LAST30DAYS_YOUTUBE_BROWSER_PROFILE", "stealthcdp-default"),
        session_name=_setting(config, "LAST30DAYS_YOUTUBE_BROWSER_SESSION", "last30days-youtube-transcripts"),
        browser_build=_setting(config, "LAST30DAYS_YOUTUBE_BROWSER_BUILD", "stealthcdp_chromium"),
        view_provider=_setting(config, "LAST30DAYS_YOUTUBE_BROWSER_VIEW_PROVIDER", "rdp_gateway"),
        timeout=timeout,
        start_url="https://www.youtube.com/feed/subscriptions",
        service_name="last30days",
        agent_name="youtube-media",
        task_name="youtube-subscriptions",
        browser_host="remote_headed",
        display_isolation="private_virtual_display",
        control_input_provider="manual_attached_desktop",
    )
    browser_client = client or youtube_yt._YouTubeBrowserClient(timeout=timeout)
    try:
        with youtube_yt._YOUTUBE_BROWSER_LOCK:
            workspace = browser_client.acquire_workspace(request)
            retained = browser_client.prepare_site_tab(workspace, "youtube.com", consolidate=True)
            browser_client.act(workspace, browser_runtime.BrowserAction(
                "navigate" if retained else "new_tab", value=request.start_url
            ))
            browser_client.act(workspace, browser_runtime.BrowserAction("wait", value="3000"))
            result = browser_client.evaluate(
                workspace, _SUBSCRIPTIONS_SCRIPT.replace("__LIMIT__", str(limit))
            )
    except Exception as exc:
        return {"ok": False, "error": "browser_subscription_discovery_failed", "detail": type(exc).__name__, "items": []}
    state = str(result.get("state") or "unknown")
    if state == "signed_out":
        return {"ok": False, "error": "youtube_sign_in_required", "items": []}
    items = list(result.get("items") or [])[:limit]
    return {
        "ok": state == "ok",
        "error": "" if state == "ok" else "no_subscription_videos_found",
        "items": items,
        "operator_visible_state": getattr(workspace, "operator_visible_state", None),
    }


def _write_transcript(text: str, output_dir: str, vid: str) -> str:
    directory = Path(output_dir).expanduser().resolve()
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{vid}.transcript.txt"
    path.write_text(text.strip() + "\n", encoding="utf-8")
    return str(path)


def local_asr(video_url: str, config: Optional[dict] = None) -> Optional[dict]:
    repo = _transcribe_audio_dir(config)
    if repo is None or not shutil.which("yt-dlp"):
        return None
    with tempfile.TemporaryDirectory(prefix="l30d-youtube-asr-") as work:
        audio_template = str(Path(work) / "source.%(ext)s")
        download = subproc.run_with_timeout([
            "yt-dlp", "--ignore-config", "--no-playlist", "-f", "bestaudio",
            "-x", "--audio-format", "mp3", "-o", audio_template, "--", video_url,
        ], timeout=1800)
        if download.returncode != 0:
            return None
        audio_files = sorted(Path(work).glob("source.*"))
        if not audio_files:
            return None
        python = repo / ".venv" / "bin" / "python"
        executable = str(python) if python.is_file() else sys.executable
        result = subproc.run_with_timeout([
            executable, str(repo / "faster_whisper_transcribe.py"), str(audio_files[0]),
            "--text-output", "--output-dir", work, "--no-speaker-labels",
        ], timeout=3600)
        if result.returncode != 0:
            return None
        transcripts = sorted(Path(work).glob("* Transcript.txt"))
        if not transcripts:
            return None
        text = transcripts[0].read_text(encoding="utf-8").strip()
        return {"text": text, "provider": "transcribe-audio", "source": str(repo)} if text else None


def transcript(
    url: str,
    output_dir: str,
    config: Optional[dict] = None,
    caption_fetcher: Callable[..., Optional[str]] = youtube_yt.fetch_transcript,
    asr_fetcher: Callable[..., Optional[dict]] = local_asr,
) -> dict:
    vid = video_id(url)
    status: dict[str, Any] = {}
    with tempfile.TemporaryDirectory(prefix="l30d-youtube-captions-") as work:
        text = caption_fetcher(vid, work, status=status, config=config)
    provider = "captions"
    asr = None
    if not text:
        asr = asr_fetcher(url, config=config)
        text = str((asr or {}).get("text") or "").strip()
        provider = str((asr or {}).get("provider") or "transcribe-audio")
    if not text:
        return {"ok": False, "error": "transcript_unavailable", "video_id": vid, "status": status}
    path = _write_transcript(text, output_dir, vid)
    return {"ok": True, "video_id": vid, "provider": provider, "path": path, "words": len(text.split())}


def download(
    url: str,
    output_dir: str,
    max_height: int = 1080,
    runner: Runner = subproc.run_with_timeout,
) -> dict:
    vid = video_id(url)
    height = max(144, min(int(max_height), 2160))
    directory = Path(output_dir).expanduser().resolve()
    directory.mkdir(parents=True, exist_ok=True)
    command = [
        "yt-dlp", "--ignore-config", "--no-playlist", "--restrict-filenames",
        "-f", f"bv*[height<={height}]+ba/b[height<={height}]",
        "--merge-output-format", "mp4", "--print", "after_move:filepath",
        "-o", str(directory / "%(title).180B [%(id)s].%(ext)s"), "--", url,
    ]
    try:
        result = runner(command, timeout=3600)
    except Exception as exc:
        return {"ok": False, "error": "video_download_failed", "detail": type(exc).__name__, "video_id": vid, "command": command}
    path = (result.stdout or "").strip().splitlines()[-1] if (result.stdout or "").strip() else ""
    if result.returncode != 0 or not path or not Path(path).is_file():
        return {"ok": False, "error": "video_download_failed", "detail": (result.stderr or "")[-300:], "video_id": vid, "command": command}
    return {"ok": True, "video_id": vid, "path": path, "command": command}
