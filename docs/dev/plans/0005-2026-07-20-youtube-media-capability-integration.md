# Plan 0005 | YouTube Media Capability Integration

State: OPEN
Date: 2026-07-20

## Objective

Close the useful Agent Reach parity gaps in this fork with one bounded YouTube
media interface: authenticated subscription discovery through the retained
hidden-RDP browser, caption-first transcription with local `../transcribe-audio`
fallback, intentional video downloads, and truthful `yt-dlp` runtime doctoring.

## Current State

- YouTube topic search, metadata, and captions use `yt-dlp`.
- Classified transport failures can use the retained hidden-RDP
  `stealthcdp_chromium` browser.
- A cloud Whisper module exists but is not invoked by the engine.
- `../transcribe-audio` is the workstation authority for local ASR but is not
  wired into this skill.
- Authenticated subscription discovery and video download were proven manually,
  not exposed through a shipped skill interface.
- `is_ytdlp_installed()` checks PATH presence, not executable or JavaScript
  runtime readiness.

## Interface And Seam

Add a deep `youtube_media` module and companion runtime script with four public
operations:

1. `doctor` returns structured readiness without downloading media.
2. `subscriptions` returns bounded recent videos from the broker-selected
   authenticated hidden-RDP profile.
3. `transcript <URL>` uses captions first and invokes local transcribe-audio only
   when captions are genuinely unavailable.
4. `download <URL>` downloads one video to an explicit output directory with a
   bounded resolution and no playlist expansion.

The module owns subprocess construction, URL validation, browser extraction,
artifact naming, and structured errors. The script is a thin adapter for the
slash-command runtime.

## Scope And Bounds

- YouTube URLs only; reject ambiguous or non-YouTube URLs.
- One subscription page, at most 50 returned entries.
- One transcript or download URL per invocation.
- Local ASR is serialized and uses `LAST30DAYS_TRANSCRIBE_AUDIO_DIR` when set,
  then bounded workstation/repo discovery.
- Downloads default to MP4 at or below 1080p and always use `--no-playlist`.
- No browser cookies, storage, HTML, or media URLs leave Chromium.
- No CAPTCHA bypass, private-video bypass, playlist mirroring, or bulk archive.
- Primary agent owns the critical path; no subagents are used.

## TDD Slices

1. Runtime doctor reports missing, broken, JS-runtime warning, and ready states.
2. Subscription discovery reports signed-out state and normalized signed-in
   videos through the browser workspace interface.
3. Transcript operation returns captions without ASR and invokes local ASR only
   after confirmed caption absence.
4. Download operation emits a bounded yt-dlp command and returns the concrete
   artifact path.
5. CLI JSON/text rendering preserves structured failure states and exit codes.

## Acceptance Criteria

- The four operations are documented in `SKILL.md` and `CONFIGURATION.md`.
- Doctor verifies `yt-dlp --version`, ffmpeg, Node/Deno, agent-browser, and local
  transcribe-audio availability without media/network mutation.
- Subscriptions require the existing `stealthcdp-default` hidden-RDP profile and
  fail clearly when signed out.
- Transcript uses the existing caption stack first; a successful caption never
  invokes ASR.
- Confirmed caption absence can invoke `../transcribe-audio` and returns a text
  artifact plus provider metadata.
- Video download is single-video, bounded-resolution, no-playlist, and returns a
  concrete file path.
- Tests cover public behavior, command safety, failure containment, and CLI
  contracts.
- Focused tests and the full suite pass.
- The skill artifact builds and the installed copy matches the committed source.
- Live smokes prove authenticated subscription discovery, local-ASR fallback,
  video download, and doctor readiness.
- All commits, including Plan 0004's local commits, are pushed to `origin/main`.

## Definition Of Done

State changes to COMPLETE only after all acceptance criteria have current
source-backed, automated, installed-copy, live-runtime, and remote-push evidence.

## Completion Evidence

Pending.
