# Plan 0005 | YouTube Media Capability Integration

State: COMPLETE
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

- Implementation commit: `d50bf48` (`feat(youtube): add bounded media
  operations`).
- Focused YouTube, browser, and environment tests passed, including doctor
  state transitions, authenticated/signed-out subscription behavior,
  caption-to-ASR routing, download failure containment, and CLI JSON/exit
  contracts.
- Full validation: `2094 passed, 7 skipped, 6 subtests passed` in 55.20 seconds.
- Distribution: `dist/last30days.skill` built with 102 files; SHA-256
  `0d425d000f930c21f625807c47b9c6ffc71009d892f8920f98827290434350eb`.
- Installed parity: `SKILL.md`, `scripts/youtube_media.py`,
  `scripts/lib/youtube_media.py`, and `scripts/lib/env.py` matched the source
  checkout byte-for-byte after `npx skills add . -g -y`.
- Installed doctor: `yt-dlp 2026.07.04`, Deno, ffmpeg, agent-browser, and
  `/home/ecochran76/workspace.local/transcribe-audio` all reported ready.
- Authenticated browser smoke: the retained hidden-RDP profile returned current
  subscribed videos with `operator_visible_state=ready`.
- Transcript smokes: browser captions produced a 570-word artifact for
  `dC5mZdinwfY`; direct local fallback through `transcribe-audio` produced a
  separate 537-word artifact for the same subscribed-channel video.
- Installed download smoke: `dC5mZdinwfY` downloaded as a single 144p MP4,
  3,625,568 bytes, with playlist expansion disabled.
- Agent Reach `check-update` reported v1.5.0 as current; its YouTube downloader
  remains `yt-dlp`, so this fork now supplies the missing authenticated browser,
  local-ASR, bounded-download, and runtime-doctor interfaces.
- Remote closeout: `origin/main` contains this completion commit and all
  predecessors, including the three Plan 0004 commits (verified after push).
