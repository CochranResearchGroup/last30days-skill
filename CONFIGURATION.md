# Configuration

Everything you can tune in `/last30days` without editing the engine source.
Three layers, in order of how often you'll touch them:

1. **Per-run flags** - what you pass on the command line.
2. **Environment variables and `.env`** - what's enabled across all runs.
3. **Optional trend-monitoring stack** - SQLite store, watchlist, briefings.

Per-client patterns and the experimental beta channel are at the bottom.

> Skip ahead: [Where output is saved](#where-output-is-saved) - [API keys](#api-keys-env) - [Reasoning provider](#reasoning-provider-priority) - [Web search backend](#web-search-backend-priority) - [Trend monitoring](#trend-monitoring-store--watchlist--briefings) - [Per-client patterns](#per-client-patterns) - [Beta channel](#beta-channel)

## Why this document exists

This is a focused **configuration reference** maintained alongside the engine. The runtime contract (the voice rules, the planner protocol, the LAWs the synthesizing model follows) lives in [`skills/last30days/SKILL.md`](skills/last30days/SKILL.md) - that file is authoritative when the two ever differ. This file's job is narrower: surface every knob a user or operator can turn, in one place, kept current with the code so client-facing setups stay reliable. New configuration knobs added to the engine should be reflected here in the same PR.

---

## Where output is saved

| Platform | Default path | Override |
|---|---|---|
| Linux / macOS | `LAST30DAYS_MEMORY_DIR` defaults to `~/Documents/Last30Days/` | set `LAST30DAYS_MEMORY_DIR=/path` |
| Windows | `LAST30DAYS_MEMORY_DIR` defaults to `C:\Users\<you>\Documents\Last30Days\` | set `LAST30DAYS_MEMORY_DIR=C:\path` |

Each run produces one file per topic, slug-named:
`<slug>-raw[-suffix].md`. Same topic + same suffix on the same day overwrites; same topic + same suffix on different days appends a date stamp.

### Recommended `.env` entry

`.env` files don't travel between machines or harnesses, so set `LAST30DAYS_MEMORY_DIR` explicitly in `~/.config/last30days/.env` once per host. The `/last30days` slash command works without it (the SKILL.md wrapper has its own default), but **bare engine invocations** — `python3 scripts/last30days.py ...` from cron jobs, scripts, or agents that bypass the wrapper — silently no-op the file save unless the engine sees the env var. Mirrors the `LAST30DAYS_STORE` env-or-flag convention.

```bash
# ~/.config/last30days/.env  (pick ONE — uncomment the line that matches your OS)
LAST30DAYS_MEMORY_DIR=~/Documents/Last30Days                      # POSIX — defaults to this path when unset
# LAST30DAYS_MEMORY_DIR=C:\Users\<user>\Documents\Last30Days      # Windows
```

The engine's `.env` reader doesn't expand `$HOME` — only the tilde, via `Path().expanduser()` downstream. Use `~/...` or an absolute path; **don't** write the literal string `$HOME/...` into your `.env` (it gets stored verbatim and breaks path resolution).

**Per-run overrides:**

- `--save-dir <path>` - one-off output location. **Flag wins over env var.** If neither flag nor env var is set, the engine does not write a file (DB persistence is independent — see `LAST30DAYS_STORE` below).
- `--output <file>` - write the rendered output to an exact file path, using the format selected by `--emit`.
- `--save-suffix <name>` - distinguish runs of the same topic (e.g. per client: `--save-suffix=acme`).

The footer line `📎 Raw results saved to ${LAST30DAYS_MEMORY_DIR:-$HOME/Documents/Last30Days}/<slug>-raw.md` is the canonical pointer; if it shows backslashes on Windows update past v3.1.1.

---

## API keys (`.env`)

The skill reads keys from a `.env` file. Two locations are supported, in priority order:

1. **`.claude/last30days.env`** in the current project directory (project-scoped) - takes precedence when present.
2. **`~/.config/last30days/.env`** at the user level (global default) - the fallback.

Override the global location with `LAST30DAYS_CONFIG_DIR=/path` (or `LAST30DAYS_CONFIG_DIR=""` for no-config mode). File permissions should be `600` on POSIX hosts - the engine warns on every run if they aren't.

The project-scoped file is the cleanest pattern for **per-client setups**: drop a `.claude/last30days.env` into each client folder (`SCRAPECREATORS_API_KEY`, `INCLUDE_SOURCES`, `LAST30DAYS_MEMORY_DIR`, `BSKY_HANDLE`, etc), `cd` into that folder, and the skill picks up that client's configuration automatically. No wrapper scripts needed for the common case.

**Source-by-source** - what each key unlocks:

| Source | Key(s) | Required for | Free tier |
|---|---|---|---|
| Reddit (public) | none | always on | yes |
| Hacker News | none | always on | yes |
| Polymarket | none | always on | yes |
| GitHub | `gh` CLI installed (uses your GitHub auth) | always on if `gh` present | yes |
| YouTube | `yt-dlp` CLI installed; optional `agent-browser` browser fallback is auto-detected | always on if `yt-dlp` present | yes |
| Digg | `digg-pp-cli` on PATH (auto-installed during first-run setup via `npx -y @mvanhorn/printing-press-library@0.1.16 install digg --cli-only`; binary defaults to `$HOME/.local/bin` — Hermes/OpenClaw agent subprocesses must inherit that dir on PATH for Digg to activate; prior pp-digg installs use the same path) | always on if `digg-pp-cli` on PATH | yes (free, keyless, read-only) |
| X / Twitter | one of: `LAST30DAYS_X_BROWSER=1` plus `agent-browser` and an authenticated profile, `AUTH_TOKEN` + `CT0` (Bird), `XAI_API_KEY`, `XQUIK_API_KEY`, `SCRAPECREATORS_API_KEY`, or `FROM_BROWSER` | X items in results | agent-browser / cookie auth / Bird = free; Xquik / xAI / ScrapeCreators = key-based |
| TikTok | `SCRAPECREATORS_API_KEY` + `INCLUDE_SOURCES` contains `tiktok` | TikTok items | 10K free calls |
| Instagram | `SCRAPECREATORS_API_KEY` + `INCLUDE_SOURCES` contains `instagram` | Instagram Reels | 10K free calls; raise `LAST30DAYS_TRANSCRIPT_TIMEOUT` (default 30s) if SC is slow on your network |
| Threads | `SCRAPECREATORS_API_KEY` + `INCLUDE_SOURCES` contains `threads` | Threads items | 10K free calls |
| Pinterest | `SCRAPECREATORS_API_KEY` + `INCLUDE_SOURCES` contains `pinterest` | Pinterest items | 10K free calls |
| Facebook | `LAST30DAYS_FACEBOOK_BROWSER=1`, `agent-browser` on PATH, and explicit `--search=facebook` | Facebook posts visible to a signed-in route-bound remote browser profile | free; requires operator login in agent-browser/Guacamole/RDP and `operatorVisible.state=ready` proof |
| LinkedIn | `LAST30DAYS_LINKEDIN_BROWSER=1`, `agent-browser` on PATH, and explicit `--search=linkedin` | LinkedIn content posts visible to a signed-in route-bound remote browser profile | free; requires operator login in agent-browser/Guacamole/RDP and `operatorVisible.state=ready` proof |
| Bluesky | `BSKY_HANDLE` + `BSKY_APP_PASSWORD` | Bluesky items | yes (app password at bsky.app) |
| TruthSocial | `TRUTHSOCIAL_TOKEN` | TruthSocial items | yes |
| Web search | one of: `BRAVE_API_KEY`, `EXA_API_KEY`, `SERPER_API_KEY`, `PARALLEL_API_KEY` | `--auto-resolve` and Step 2 supplements | Brave has a free tier; native WebSearch on Claude Code / Codex / Gemini works as a fallback |
| Perplexity Deep Research | `OPENROUTER_API_KEY` | `--deep-research` flag (~$0.90/query) | no |
| Caption-free transcription | Local `transcribe-audio` checkout and `ffmpeg` | `scripts/youtube_media.py transcript` uses it only when captions are unavailable | Local GPU execution; no transcription API key required |
| Jobs / careers pages | none for public ATS pages; web backend improves fallback discovery | `--hiring-signals` and strong Hiring Signals in standard company reports | yes |
| Apify (alternate scraper) | `APIFY_API_TOKEN` | fallback for Reddit/TikTok/Instagram when ScrapeCreators is exhausted | yes (limited) |

**Example `.env` skeleton** (placeholders only - replace with your own values):

```bash
# Reasoning + planning (one provider; see priority below)
GOOGLE_API_KEY=<your-gemini-key>

# Web search backend (one is enough; Brave is the cheapest)
BRAVE_API_KEY=<your-brave-key>

# Optional sources
SCRAPECREATORS_API_KEY=<your-scrapecreators-key>
INCLUDE_SOURCES=tiktok,instagram

# YouTube keeps yt-dlp as its primary path. When a classified transport or
# bot-check failure exhausts it, auto uses one hidden-RDP stealth Chromium lane.
LAST30DAYS_YOUTUBE_BROWSER_FALLBACK=auto
# LAST30DAYS_YOUTUBE_BROWSER_PROFILE=stealthcdp-default
# LAST30DAYS_YOUTUBE_BROWSER_SESSION=last30days-youtube-transcripts
# LAST30DAYS_YOUTUBE_BROWSER_BUILD=stealthcdp_chromium
# LAST30DAYS_YOUTUBE_BROWSER_VIEW_PROVIDER=rdp_gateway
# LAST30DAYS_YOUTUBE_BROWSER_TIMEOUT=75

# X via an authenticated agent-browser profile (opt-in; preferred over API
# backends while enabled). The default profile already used on this workstation
# is shown; use a different registered X profile elsewhere.
LAST30DAYS_X_BROWSER=1
LAST30DAYS_X_BACKEND=browser
# LAST30DAYS_X_BROWSER_PROFILE=last30days-facebook
# LAST30DAYS_X_BROWSER_SESSION=last30days-facebook
# LAST30DAYS_X_BROWSER_BUILD=stealthcdp_chromium
# LAST30DAYS_X_BROWSER_VIEW_PROVIDER=cdp_screencast
# LAST30DAYS_X_BROWSER_TIMEOUT=75
# LAST30DAYS_X_BROWSER_INITIAL_WAIT=2
# LAST30DAYS_X_BROWSER_SCROLL_WAIT=1

# Facebook via agent-browser remote browser (opt-in; no cookies are stored here)
LAST30DAYS_FACEBOOK_BROWSER=1
# Optional overrides; defaults are shown here.
# LAST30DAYS_FACEBOOK_PROFILE=last30days-facebook
# LAST30DAYS_FACEBOOK_SESSION=last30days-facebook
# LAST30DAYS_FACEBOOK_BROWSER_BUILD=stealthcdp_chromium
# LAST30DAYS_FACEBOOK_VIEW_PROVIDER=rdp_gateway
# LAST30DAYS_FACEBOOK_TIMEOUT=75
# LAST30DAYS_FACEBOOK_MAX_RESULTS=16
# LAST30DAYS_FACEBOOK_SCROLLS=2
# LAST30DAYS_FACEBOOK_DEBUG_DIR=~/.local/state/last30days/facebook-debug

# LinkedIn via agent-browser remote browser (opt-in; no cookies are stored here)
LAST30DAYS_LINKEDIN_BROWSER=1
# Optional overrides; defaults are shown here. Set these to an existing shared
# profile/session only when that retained browser already owns the LinkedIn login.
# LAST30DAYS_LINKEDIN_PROFILE=last30days-linkedin
# LAST30DAYS_LINKEDIN_SESSION=last30days-linkedin
# LAST30DAYS_LINKEDIN_BROWSER_BUILD=stealthcdp_chromium
# LAST30DAYS_LINKEDIN_VIEW_PROVIDER=rdp_gateway
# LAST30DAYS_LINKEDIN_TIMEOUT=75
# LAST30DAYS_LINKEDIN_MAX_RESULTS=16
# LAST30DAYS_LINKEDIN_SCROLLS=1
# LAST30DAYS_LINKEDIN_MIN_ACTION_DELAY=4
# LAST30DAYS_LINKEDIN_MAX_ACTIONS_PER_MINUTE=6
# LAST30DAYS_LINKEDIN_DEBUG_DIR=~/.local/state/last30days/linkedin-debug

# The scraper resolves browser, tab, route, and display identity from current
# agent-browser service state. Route IDs and display allocations are runtime
# leases, not durable configuration. It opens the remote Facebook workspace only
# when no matching retained operator-visible browser exists, then navigates each
# query through Facebook's Search control or a verified service-owned tab.
# LinkedIn reuses one retained site tab, spaces user-like browser actions by
# at least four seconds, and stops immediately on search-limit, throttling,
# temporary-restriction, or unusual-activity warnings. A command is successful
# only when profile/auth/search readbacks pass and every
# emitted item has a canonical post permalink, author, in-range date, and useful text.
# Debug artifacts contain timings, assertions, counts, and item lengths only;
# they exclude cookies, operator URLs, raw HTML, and private page text.

X, Facebook, and LinkedIn browser failures are typed so operator action is unambiguous:

| Error type | Meaning / action |
|---|---|
| `auth_required` | Open the returned current operator URL and sign in to the configured profile. |
| `checkpoint_required` | Complete the site's security checkpoint in the operator-visible browser. |
| `rate_limited` | The X account or search lane is restricted; stop and retry after the platform cooldown. |
| `operator_ingress_unavailable` | Repair public Guacamole/dashboard ingress before retrying authentication. |
| `profile_mismatch` | The selected agent-browser session is attached to a different profile. |
| `route_stale` | Refresh or repair current agent-browser route-display service state. |
| `navigation_mismatch` | The site did not reach the exact requested query/filter state; no items are emitted. |
| `extraction_empty` | A verified search page contained no candidate cards. |
| `quality_gate_failed` | Candidates existed, but none were canonical, dated, relevant posts. |
| `search_unavailable` | X rendered a temporary error page instead of results. |

# X authentication (one option only)
AUTH_TOKEN=<your-auth-token>
CT0=<your-ct0-token>
# OR xAI API key (paid)
# XAI_API_KEY=<your-xai-key>
# OR Xquik key-based X search
# XQUIK_API_KEY=<your-xquik-key>
# OR cookie-jar (free; logs in via your browser session).
# Unset = Firefox + Safari (silent). FROM_BROWSER=auto also tries the Chromium
# family (Chrome, Brave, Edge, Vivaldi, Opera, Arc, Chromium). On macOS it may
# prompt for Keychain access on the browser that actually holds your X cookies;
# on Linux it uses libsecret or Chromium's local fallback key. Or name a single
# browser, e.g. brave/edge. On Windows only Firefox is supported.
# FROM_BROWSER=firefox

# Bluesky
BSKY_HANDLE=<your-handle>.bsky.social
BSKY_APP_PASSWORD=<your-app-password>
```

After editing: `chmod 600 ~/.config/last30days/.env` (or `chmod 600 .claude/last30days.env` if using the project-scoped variant).

**Troubleshooting:** if a source you expected to see isn't appearing in results, run `python3 scripts/last30days.py --diagnose`. It prints a per-source availability report (which keys were detected, which CLIs are installed, which backends are reachable) without running a full search.

### YouTube media operations

The companion runtime exposes bounded, single-video operations for agents. Run
these commands from the installed `last30days` skill directory:

```bash
python3 scripts/youtube_media.py --json doctor
python3 scripts/youtube_media.py --json subscriptions --limit 12
python3 scripts/youtube_media.py --json transcript "YOUTUBE_URL" --output-dir /tmp/transcripts
python3 scripts/youtube_media.py --json download "YOUTUBE_URL" --output-dir /tmp/videos --max-height 1080
```

`subscriptions` uses the retained `stealthcdp-default` hidden-RDP browser and
requires that profile to be signed into YouTube. `transcript` tries the existing
caption stack first and invokes local `transcribe-audio` only when captions are
unavailable. `download` processes one video, disables playlist expansion, and
caps resolution at the requested height.

Set `LAST30DAYS_TRANSCRIBE_AUDIO_DIR` when the local checkout is not available
as `../transcribe-audio` or `~/workspace.local/transcribe-audio`:

```bash
LAST30DAYS_TRANSCRIBE_AUDIO_DIR=/path/to/transcribe-audio
```

The `doctor` operation executes `yt-dlp --version` and reports Node/Deno,
`ffmpeg`, agent-browser, and transcribe-audio readiness without downloading
media.

### YouTube caption language and browser fallback

`LAST30DAYS_YT_SUB_LANGS` is a comma-separated preference order for YouTube
captions. The default is `en,es,pt`. Languages are attempted one at a time and
the first available caption wins, so a rate limit or failure on a translated
lower-priority track cannot discard a caption already obtained in a preferred
language.

```bash
LAST30DAYS_YT_SUB_LANGS=en,es,pt
```

`LAST30DAYS_YOUTUBE_BROWSER_FALLBACK` controls the bounded fallback used after
a classified `yt-dlp` or direct-HTTP transport failure:

- `auto` (default) uses it only when `agent-browser` is on the engine
  subprocess PATH.
- `1` enables it when `agent-browser` is available.
- `0` disables it.

The fallback resolves `targetServiceId=youtube`, uses the retained profile and
session knobs shown above, and requests `stealthcdp_chromium` in headed
`remote_headed` mode with `private_virtual_display` isolation and an
`rdp_gateway` operator view. Agent-browser currently realizes a checked-out RDP
route on its hidden XRDP desktop and records that bound display as
`shared_display`; it never uses the ambient visible desktop. Browser work is serialized even when normal
caption fetches run concurrently. It reads caption metadata from the watch
page and fetches timed text inside that page's Chromium context; browser
cookies, storage, raw HTML, and caption URLs are never exported to Python.
Confirmed caption absence does not launch the browser. The companion
`transcript` operation routes those videos to the local `transcribe-audio`
workflow.

### Encrypted credential sources (Keychain / pass)

If you'd rather not keep keys in a plaintext `.env`, the loader has two
encrypted sources that decrypt secrets transiently at call time (never written
to disk, never logged). Both are **lowest-priority and additive** — an explicit
`.env` or process-env value always overrides them, so you can mix and match. The
`pass` source is only consulted for keys still missing after the higher-priority
sources, so a box that merely has `pass` installed pays no decrypt cost when
everything is already in `.env`.

| Platform | Source | Store keys with | Lookup convention |
|---|---|---|---|
| macOS | Keychain | `scripts/setup-keychain.sh` | service name `last30days-<KEY>` |
| Linux / Unix (anywhere `pass` exists, incl. macOS) | [`pass`(1)](https://www.passwordstore.org/) | `scripts/setup-pass.sh` | pass path `last30days/<KEY>` |

```bash
# macOS Keychain
./scripts/setup-keychain.sh                 # interactive; --list / --delete KEY

# pass(1) — Linux/Unix analog
./scripts/setup-pass.sh                      # interactive; --list / --delete KEY
./scripts/setup-pass.sh SCRAPECREATORS_API_KEY   # just one key
```

The `pass` source honors `PASSWORD_STORE_DIR`. If your store organizes secrets
under a different prefix, point the loader at it with `LAST30DAYS_PASS_PREFIX`
(works from your `.env` too, and must match where `setup-pass.sh` wrote them).
The prefix is used verbatim, so keep the trailing separator:

```bash
export LAST30DAYS_PASS_PREFIX="secrets/last30days/"   # default: last30days/
```

Both sources cover the same key set as the `.env` skeleton above.

### Bluesky app-password format and search host

`BSKY_APP_PASSWORD` should be a 19-char app password in `xxxx-xxxx-xxxx-xxxx` format (lowercase alphanumeric, three hyphens). Generate one at <https://bsky.app/settings/app-passwords>. The AT Protocol's `createSession` endpoint also accepts your main account login password, but that's bad hygiene — main passwords have no scope (an app password can be limited to non-DM access) and can't be revoked individually.

The skill defaults to `api.bsky.app` for `searchPosts`, which is the canonical authenticated AppView. The previous default `public.api.bsky.app` is the unauthenticated public mirror and is currently blocked by BunnyCDN for `searchPosts` regardless of auth header (verified 2026-05-04). If Bluesky migrates infrastructure again, override the host without a code change by setting `BSKY_SEARCH_HOST` in your `.env`:

```bash
BSKY_SEARCH_HOST=api.bsky.app   # default — change only if Bluesky moves
```

### Default source set (`LAST30DAYS_DEFAULT_SEARCH`)

By default the engine decides the source set per query (everything available, minus `EXCLUDE_SOURCES`). To pin a **fixed** source set for every run without passing `--search` each time — and without patching `SKILL.md`, which a release would overwrite — set:

```bash
LAST30DAYS_DEFAULT_SEARCH=reddit,x,youtube,hn
```

Accepts the same comma-separated names and aliases as `--search` (`web` → grounding, `hn` → hackernews, `bsky` → bluesky). Precedence: an explicit `--search` on the command line always wins; `LAST30DAYS_DEFAULT_SEARCH` applies only when the flag is omitted; when neither is set, per-query behavior is unchanged. `INCLUDE_SOURCES` / `EXCLUDE_SOURCES` keep their existing additive/subtractive roles on whichever set is selected.

---

## Reasoning provider priority

`/last30days` needs one reasoning model for planning + reranking when you don't pass `--plan` yourself. Auto-detect priority (set `LAST30DAYS_REASONING_PROVIDER=<name>` to pin one):

1. **Gemini** - `GOOGLE_API_KEY` / `GEMINI_API_KEY` / `GOOGLE_GENAI_API_KEY`
2. **OpenAI** - `OPENAI_API_KEY` (or Codex auth at `~/.codex/auth.json`)
3. **xAI** - `XAI_API_KEY`
4. **OpenRouter** - `OPENROUTER_API_KEY` (also unlocks `--deep-research`)
5. **Local / deterministic** - always available, lowest quality

When you invoke `/last30days` from Claude Code, Codex, or Gemini, the host model **is** the reasoning provider for plan + synthesis - you don't need any of the keys above unless you also run the script headlessly (cron, CI, watchlist).

---

## Web search backend priority

The search-source preference ladder, strict best-to-floor:

1. **Host-native search** - Claude Code's `WebSearch`, and the equivalents on Codex / Gemini. Best results; used automatically on hosts that have it. Signalled to the engine via `LAST30DAYS_NATIVE_SEARCH=1` (the skill sets this for you when your host has a native search tool) so the engine does not run a worse search underneath it.
2. **Paid engine backend** - one of `BRAVE_API_KEY`, `EXA_API_KEY`, `SERPER_API_KEY`, `PARALLEL_API_KEY`, auto-detected in that order. Override per-run with `--web-backend=<name>`.
3. **Keyless engine floor** - zero-key web search (DuckDuckGo, plus an optional SearXNG instance) and zero-key page fetch (Jina Reader). Runs only when the host has **no** native search **and** no paid key is set, so headless/cron and hosts without a built-in search tool still get general-web coverage. Force it explicitly with `--web-backend=keyless`.

Relevant env vars:

| Var | Effect |
| --- | --- |
| `LAST30DAYS_NATIVE_SEARCH=1` | Tells the engine your host has native search; suppresses the keyless floor. Set automatically by the skill on capable hosts. Leave unset on hosts without a native search tool so the floor runs. |
| `LAST30DAYS_SEARXNG_URL=<base-url>` | Optional. A SearXNG instance used as the keyless-search fallback rung when DuckDuckGo returns nothing. |

Privacy note: the keyless floor sends the query (to DuckDuckGo / your SearXNG instance) and any fetched URL (to Jina Reader) to those third parties. It is intended for public-research use; results may be cached snapshots. It never runs when native search or a paid backend is in play.

Visible quality difference between hosts with vs without native search or a configured backend. If your client setup produces thinner results than yours, this is usually why.

---

### `--hiring-signals` flag

Use `--hiring-signals` for a focused company hiring-signal report:

```bash
python3 skills/last30days/scripts/last30days.py "Listen Labs" --hiring-signals
```

The engine treats public jobs/careers postings as evidence of focus or priority shifts, not exact roadmap predictions. Standard company runs may include Hiring Signals automatically when multiple current roles support the same interpretation; weak or unavailable hiring evidence is omitted.

---

## Trend monitoring (`--store` + watchlist + briefings)

The default behavior - one slug-named file per topic, overwritten on rerun - is the snapshot mode. For continuous monitoring, the repo ships three components most users miss:

### `--store` flag

Adding `--store` to any run persists every finding to a SQLite database (default at `~/.local/share/last30days/research.db`). Findings dedupe on the `source_url` column (UNIQUE constraint), so the same URL across runs updates the existing row instead of creating a duplicate. The markdown file still saves; the SQLite is the time-series substrate.

**Always-on alternative:** set `LAST30DAYS_STORE=1` in your `.env` instead of remembering `--store` on every invocation. The flag still works as before; the env var is purely additive. Same hybrid pattern as `LAST30DAYS_DEBUG` — works whether shell-exported or in `.env`.

Relevant tables: `topics`, `research_runs`, `findings`, `settings`. Schema: [`scripts/store.py`](skills/last30days/scripts/store.py).

### `watchlist.py` - recurring topics

[`scripts/watchlist.py`](skills/last30days/scripts/watchlist.py) manages topics that should be researched on a schedule. Subcommands: `add`, `remove`, `list`, `run-one`, `run-all`, `config`. Built-in delivery to Slack incoming webhooks (`hooks.slack.com/...`) or any HTTPS endpoint, fired only when new findings appear.

Two-step flow (the watchlist holds the topic; an external scheduler invokes the run):

```bash
# 1. Add the topic to the watchlist
#    Default schedule daily 8am; --weekly switches to Mondays 8am
python3 scripts/watchlist.py add "british airways middle east" --weekly

# 2. Configure delivery and budget (optional)
python3 scripts/watchlist.py config delivery "https://hooks.slack.com/services/..."
python3 scripts/watchlist.py config budget 5.00

# 3. Trigger via cron / Task Scheduler / GitHub Actions
python3 scripts/watchlist.py run-one "british airways middle east"
# or run every enabled topic, gated by daily_budget
python3 scripts/watchlist.py run-all
```

The schedule field stored on each topic is metadata - the actual cron / Task Scheduler invocation is your responsibility. Watchlist runs hardcode `--quick` and `--lookback-days 90` when spawning the underlying engine.

### `briefing.py` - daily / weekly digests

[`scripts/briefing.py`](skills/last30days/scripts/briefing.py) reads the SQLite store and emits structured data the agent then synthesizes into prose. Modes: `generate` (daily), `generate --weekly`, `show [--date DATE]` (display a saved briefing). Briefs save to `~/.local/share/last30days/briefs/`.

### Recommended cadence pattern

| Step | Cadence | Command |
|---|---|---|
| Baseline | one-time per topic | `/last30days "<topic>" --days=30 --store` |
| Add to watchlist | one-time per topic | `python3 scripts/watchlist.py add "<topic>" --weekly` |
| Recurring run | daily or weekly (external scheduler) | `python3 scripts/watchlist.py run-all` |
| Digest | weekly | `python3 scripts/briefing.py generate --weekly` |

---

## Per-client patterns

The skill is built to flex around different client environments. Four patterns that compose well:

### 1. Per-client `.claude/last30days.env` (preferred when you cd into client folders)

The simplest pattern when each client has its own working directory: drop a `.claude/last30days.env` into the client folder. The skill picks it up automatically (see [API keys](#api-keys-env) for the lookup priority). Typical contents:

```bash
LAST30DAYS_MEMORY_DIR=C:\Users\<you>\Clients\acme\Research\Last30Days
SCRAPECREATORS_API_KEY=<acme-scoped-key-or-shared>
INCLUDE_SOURCES=tiktok,instagram
BSKY_HANDLE=<acme-bluesky-handle>.bsky.social
```

`cd` into the client folder, run `/last30days <topic>` as normal, no flags or wrappers. Combine with `--save-suffix=<client-slug>` per run if you also need to differentiate filenames within that folder.

### 2. Per-client save dir + suffix wrapper

For workflows where you don't `cd` into a client folder (running from anywhere, scripted batches), a tiny shell function isolates each client's research without engine changes.

PowerShell example:

```powershell
function Run-L30D-Client {
    param([string]$ClientSlug, [Parameter(ValueFromRemainingArguments=$true)]$Args)
    $env:LAST30DAYS_MEMORY_DIR = "C:\Users\$env:USERNAME\Clients\$ClientSlug\Research\Last30Days"
    /last30days @Args --save-suffix=$ClientSlug
}
# Usage: Run-L30D-Client acme "british airways middle east"
```

Bash example:

```bash
l30d-client() {
    local client=$1; shift
    LAST30DAYS_MEMORY_DIR="$HOME/Clients/$client/Research/Last30Days" \
        /last30days "$@" --save-suffix="$client"
}
# Usage: l30d-client acme "british airways middle east"
```

### 3. Custom category-peer subreddits

[`scripts/lib/categories.py`](skills/last30days/scripts/lib/categories.py) holds a table of `(category_id, trigger_keywords, peer_subreddits)`. If a client lives in a vertical that isn't covered (legal-tech, real-estate-tech, B2B HR SaaS), add a row. Pure data, no logic.

Section 2a of `SKILL.md` documents the merging rule the skill applies when your topic matches a category.

### 4. Pre-built `--competitors-plan` JSON

For competitor-vs-comparisons that recur, a pre-written JSON skeleton per client industry saves real time:

```json
{
  "Competitor B": {
    "x_handle": "competitor_b_handle",
    "subreddits": ["sub1", "sub2"],
    "github_user": "competitor-b-org",
    "context": "Founded 2019, focused on ..."
  },
  "Competitor C": { ... }
}
```

Pass as `--competitors-plan @client/competitors-plan.json` (or as a string). See `SKILL.md` section "If QUERY_TYPE = COMPARISON" for the full schema.

---

## Beta channel

Experimental customizations live on a private companion repo (`mvanhorn/last30days-skill-private`) installed as `/last30days-beta`. Never ship beta-only changes to the public marketplace without a review PR against the public repo. Workflow guide: `BETA.md` in the private repo.

This is the right home for client-specific changes you don't intend to upstream - custom category rows, internal subreddit lists, per-vertical plan templates.

---

## Cross-references

- The CLI flag surface: `python3 scripts/last30days.py --help`
- The skill contract (voice, LAWs, pre-flight protocol): [`skills/last30days/SKILL.md`](skills/last30days/SKILL.md)
- Shared package vocabulary and engine/harness terminology: [`CONCEPTS.md`](CONCEPTS.md)
- Contributor guidance: [`CONTRIBUTORS.md`](CONTRIBUTORS.md)
