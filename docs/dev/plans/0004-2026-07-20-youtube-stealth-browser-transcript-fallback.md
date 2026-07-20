# Plan 0004 | YouTube Stealth Browser Transcript Fallback

State: OPEN
Date: 2026-07-20

## Objective

Add a bounded YouTube transcript fallback that runs inside agent-browser's
headed `stealthcdp_chromium` lane when `yt-dlp` or direct HTTP is blocked.
The headed browser must run on a hidden private display and remain accessible
through the retained Guacamole/RDP operator route.

## Current State

- `yt-dlp` is the primary YouTube search and caption transport.
- Caption languages are attempted sequentially, so a lower-priority translated
  caption failure no longer discards a preferred caption already obtained.
- Hard `yt-dlp` failures currently stop transcript retrieval because the direct
  HTTP fallback has the same non-browser network posture.
- Direct HTTP uses `urllib` to fetch the watch page and timed-text URL.
- The current agent-browser access plan for `serviceName=last30days`,
  `targetServiceId=youtube`, and `browserBuild=stealthcdp_chromium` selects the
  durable `stealthcdp-default` profile with `browserHost=remote_headed`,
  `displayIsolation=private_virtual_display`, and
  `viewStreamProvider=rdp_gateway`.

Still required:

- a browser-context caption extractor
- transport-failure routing and serialized browser reuse
- explicit configuration and runtime-contract documentation
- focused, full-suite, installed-copy, and live RDP-backed validation

## Scope

1. Keep `yt-dlp` as the fast primary path.
2. On a classified hard transport, bot-check, rate-limit, or timeout failure,
   acquire one retained agent-browser workspace using:
   - browser build `stealthcdp_chromium`
   - browser host `remote_headed`
   - display isolation `private_virtual_display`
   - view provider `rdp_gateway`
3. Reuse or create only a YouTube tab in that workspace.
4. Read caption track metadata from the loaded watch page and fetch `json3`
   timed text with browser-native `fetch()` in the same page context.
5. Return only normalized caption text and bounded diagnostics. Never export
   cookies, storage, raw page HTML, or caption URLs.
6. When captions are confirmed absent, do not retry through alternate
   transports. Caption-free ASR remains owned by `../transcribe-audio`.

## Configuration

- `LAST30DAYS_YOUTUBE_BROWSER_FALLBACK=auto|1|0` defaults to `auto`.
  `auto` uses the browser only when `agent-browser` is on subprocess PATH.
- `LAST30DAYS_YOUTUBE_BROWSER_PROFILE` defaults to `stealthcdp-default`.
- `LAST30DAYS_YOUTUBE_BROWSER_SESSION` defaults to
  `last30days-youtube-transcripts`.
- `LAST30DAYS_YOUTUBE_BROWSER_BUILD` defaults to `stealthcdp_chromium`.
- `LAST30DAYS_YOUTUBE_BROWSER_VIEW_PROVIDER` defaults to `rdp_gateway`.
- `LAST30DAYS_YOUTUBE_BROWSER_TIMEOUT` defaults to 75 seconds.

The browser host and display-isolation posture are invariants, not user-facing
knobs in this slice.

## Critical Path And Bounds

The primary agent owns the critical path. No subagent is used.

1. Extend the shared agent-browser workspace request with caller URL/labels and
   explicit hidden-RDP launch posture while preserving Facebook and X defaults.
2. Add the browser transcript extractor and hard-failure routing.
3. Add focused tests for routing, configuration, browser posture, language
   selection, caption absence, and failure containment.
4. Update `SKILL.md`, `CONFIGURATION.md`, changelog, and environment loading.
5. Validate focused tests, full tests, package/install parity, and a live
   browser-backed caption fetch with operator-visible RDP evidence.

Bounds:

- maximum implementation attempts per failing invariant: 2
- maximum review/rework cycles: 1
- maximum consecutive hardening-only checkpoints: 2
- browser transcript work is serialized through one process-local lock
- one browser extraction attempt per video after primary transport exhaustion

## Acceptance Criteria

- A successful `yt-dlp` caption never launches agent-browser.
- Confirmed no-caption results do not launch agent-browser.
- Classified hard `yt-dlp` failures try the browser fallback when enabled.
- Browser acquisition uses `stealthcdp_chromium`, `remote_headed`,
  `private_virtual_display`, and `rdp_gateway` with caller labels and
  `targetServiceId=youtube` semantics.
- The live runtime returns `operatorVisible.state=ready` and an RDP/Guacamole
  operator URL for the retained hidden display.
- Caption selection follows `LAST30DAYS_YT_SUB_LANGS` order.
- Browser extraction returns normalized text without exporting cookies, raw
  HTML, storage state, or timed-text URLs.
- Concurrent transcript workers cannot launch parallel browser work.
- Browser failure remains a per-video failure and does not abort the run.
- `uv run pytest tests/test_youtube_yt.py tests/test_facebook.py
  tests/test_x_browser.py` passes.
- `uv run pytest` passes.
- The built and installed skill match the working-tree implementation.
- A low-volume live smoke proves browser-backed transcript retrieval on the
  hidden RDP-accessible headed Chromium lane.

## Non-Goals

- replacing `yt-dlp` for normal YouTube search or caption retrieval
- bypassing CAPTCHAs or account restrictions
- exporting browser authentication state to Python HTTP clients
- adding bulk browser scraping or parallel browser sessions
- implementing caption-free ASR inside this repository

## Definition Of Done

This plan is complete only when every acceptance criterion has current
automated or live evidence recorded below and no required work remains.

## Completion Evidence

Pending.
