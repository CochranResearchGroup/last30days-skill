# Configuration

Operator configuration for the user-scoped service and the explicitly gated
direct-Engine compatibility path. Ordinary `/last30days` requests use MCP
discovery and do not read these settings.

The compatibility Engine has three configuration layers, in order of how
often an operator touches them:

1. **Per-run flags** - what you pass on the command line.
2. **Environment variables and `.env`** - what's enabled across all runs.
3. **Optional trend-monitoring stack** - SQLite store, watchlist, briefings.

Per-client patterns and the experimental beta channel are at the bottom.

> Skip ahead: [Where output is saved](#where-output-is-saved) - [API keys](#api-keys-env) - [Reasoning provider](#reasoning-provider-priority) - [Web search backend](#web-search-backend-priority) - [Trend monitoring](#trend-monitoring-store--watchlist--briefings) - [Per-client patterns](#per-client-patterns) - [Beta channel](#beta-channel)

## Why this document exists

This is a focused **operator configuration reference** maintained alongside
the service and compatibility Engine. The ordinary agent contract lives in
[`skills/last30days/SKILL.md`](skills/last30days/SKILL.md). Its gated
monitoring, administration, maintenance, and direct-Engine references live
under `skills/last30days/references/`. This file surfaces the knobs an operator
can turn; ordinary research agents discover readiness through `service_info`
and do not inspect these settings.

---

## Service and App Intelligence boundaries

The installed Linux service is the product authority for agents. From a source
checkout, build and install its independently versioned artifact with:

```bash
bash service/scripts/build-runtime.sh
bash service/scripts/install.sh install \
  --artifact dist/service/last30days-service-0.3.10.tar.gz
bash service/scripts/install.sh diagnose
```

The service release lives under
`$XDG_DATA_HOME/last30days/service/releases/<version>`, independently of any
installed Agent Skill. The managed unit resolves the atomic `current` selector
through a stable launcher. A successful install records the loaded service
version, contract digest, schema 16, and runtime-manifest digest in an
owner-readable readiness receipt. Skill-first installation remains a
compatibility path during the migration; refreshing a frozen Skill copy is no
longer the service upgrade contract.

The service handshake publishes product identity, semantic service version,
service API version, contract schema and SHA-256, database schema, and the
loaded runtime-manifest SHA-256. MCP adds its stamped adapter version and
supported service-API/database-schema ranges. `service_info` remains available
when these facts are incompatible and reports one typed compatibility state;
all other MCP operations fail closed before reaching the requested endpoint.

App Intelligence is an operator-owned maintenance capability, not an
environment-variable switch for ordinary queries. The deterministic host sets
the repeated-failure threshold, model-call attempt limit, allowed write roots,
allowed tests, branch count, rework count, and approver identities when it
constructs a maintenance run. The Codex app-server worker receives a strict
schema and read-only sandbox. It may return enrichment, evaluation, or repair
proposals, but it has no publish, deploy, credential, browser-session, or
live-source-configuration mutation tool.

### Durable tick configuration

The durable all-source tick reads one versioned, user-scoped JSON document:

```text
$LAST30DAYS_CONFIG_DIR/tick-config-v1.json
```

When `LAST30DAYS_CONFIG_DIR` is unset, the default is
`~/.config/last30days/tick-config-v1.json`. The canonical schema ships as
`skills/last30days/schemas/tick-config-v1.json`. Keep the runtime document
owner-readable and out of the repository; repo examples and tests use only
sanitized placeholders.

The document defines generic services, targets, ordered provider chains,
resource keys and ceilings, artifact policy, OCR and semantic-sidecar stages,
deterministic anomaly rules, notification transports, and query/index versions.
Enabled targets execute serially in their array order; sanitized preflight and
durable tick receipts preserve that same order.
Adapter types must resolve through the installed adapter registry and carry a
non-zero stable-fixture or bounded-canary normalization proof. Credential and
routing fields are references only: cookies, tokens, raw credentials,
browser/session leases, operator URLs, recipient addresses, tenant IDs, and
profile particulars do not belong in repo data or frozen tick receipts.
`artifacts.root` must be an absolute path in user-scoped storage; relative
paths are rejected before a tick runtime is constructed.

Each tick freezes the validated non-secret config revision and digest. Changing
the config affects only a newly enqueued tick; it does not rewrite an existing
tick. `tick.lateness_seconds` bounds how long a distinct queued interval may
wait behind the singleton active tick; after that bound it terminalizes as
`missed_due_to_overlap` with an exact coverage gap. A notification chain is
required for unattended preflight, but transport order and all routing
particulars remain user configuration.

An optional strict `tick.schedule` object enables one service-owned UTC
cadence through the same durable tick interface:

```json
{
  "tick": {
    "timezone": "UTC",
    "lateness_seconds": 86400,
    "aggregate_limits": {
      "attempts": 5,
      "network_requests": 250,
      "wall_seconds": 600,
      "items": 15,
      "cost_cents": 0,
      "model_tokens": 0
    },
    "schedule": {
      "enabled": false,
      "schedule_id": "daily-default",
      "interval_seconds": 86400,
      "anchor_seconds": 0
    }
  }
}
```

The enclosing document still requires services, targets, artifact, analysis,
notification, and query fields defined by the canonical schema. An absent
schedule is disabled. The first supported production cadence is 86,400 seconds
anchored at Unix-epoch second zero (midnight UTC). The daemon
admits only the latest completed boundary within `lateness_seconds`, never a
catch-up fanout, and advances durable schedule state before invoking the tick.
Restart recovery waits for a live execution lease, then uses the existing
successor-attempt contract after expiry while preserving boundary, tick, lane,
stage, staged-result, and budget identities. Config-digest/cadence drift or an
enqueue failure pauses the schedule fail-closed. No systemd timer, per-source
timer, or legacy collection-spec enablement is created.

Read the sanitized installed state without admitting work:

```bash
python3 skills/last30days/scripts/service.py tick schedule status
```

The corresponding owner-private API is `GET /v1/tick-schedule`. Both expose
only enablement, schedule/cadence, last and next boundary, last tick ID/state,
and a safe runtime error code.

The installed acquisition bridge currently declares the source-specific
adapter types `x_agent_browser`, `facebook_agent_browser`,
`linkedin_agent_browser`, `linkedin_profile_agent_browser`, `youtube_ytdlp`,
`reddit_keyless`, `reddit_agent_browser`, and `reddit_scrapecreators`. A target
selector supplies a bounded `query` (or `topic`, `url`, or `handle`), optional
`depth`, and user-profile reference where the adapter requires one. Browsers
run normally through agent-browser; the tick does not acquire a Guacamole
lease. Human observation remains a separate acknowledged incident action.
Deployments may construct the runtime with another code-owned registry, such
as paid API adapters, and user config may select only adapter types already in
that registry. Configuration never loads an executable, module, or arbitrary
callable.

Configure that explicit observation action in the same user-scoped document,
never in repo data:

```json
{
  "observation": {
    "adapter_type": "agent_browser_service",
    "service_base_url": "http://127.0.0.1:4848"
  }
}
```

This endpoint must expose agent-browser's service API. It is not an operator
handoff URL. Normal collection does not call it. After a browser incident is
persisted, notified, explicitly acknowledged, and explicitly observed, the
runtime resolves the stored external route against one ready agent-browser
stream and posts the code-owned `view_takeover` action. Agent-browser returns
accepted takeover identity and viewer-lease metadata, not a new route. Only
after that proof passes does the runtime hand the human the already-validated
external HTTPS route retained from the ready stream; the lease ID is retained
in the user-scoped incident database.

Enabled image analysis stages also select installed adapter types. The bridge
names `provider_output_ocr_v1` and
`provider_output_semantic_sidecar_v1` accept only bounded typed outputs returned
by an acquisition provider. A deployment with the `tesseract` executable on
the service subprocess `PATH` may instead select `tesseract_cli_v1` for local,
zero-provider OCR. The deterministic
`source_grounded_semantic_sidecar_v1` adapter uses only source alt text and the
completed OCR output; it records no inferred visual entities, relationships,
actions, or context and makes no model call. Set `analysis.ocr_adapter_type`
and `analysis.semantic_sidecar_adapter_type` to installed names when the
corresponding stage is enabled. Set the adapter field to `null` when its stage
is disabled. A missing, off-PATH, broken, or invalid installed adapter fails
preflight before source work. Media can still publish when an individual
derivative fails; the derivative receives an immutable failure receipt and the
terminal tick is degraded.

The source-worker bridge carries bounded fetched bytes for images and video
thumbnails into the content-addressed artifact path. On authentication,
captcha, checkpoint, Cloudflare, and rate-limit failures it captures the
current rendered agent-browser tab programmatically, without opening a remote
view or acquiring a Guacamole observation lease. Deterministic fixtures prove
media, OCR/sidecar, and screenshot carriage. The manual acceptance packet must
still prove those paths for every enabled production adapter; no recurring
schedule is enabled meanwhile.

Media retrieval is HTTPS-only. Each destination and redirect is resolved and
rejected before the next request when any address is private, loopback,
link-local, reserved, or otherwise non-global. Every redirect consumes the
provider network ceiling, and every fetch timeout is capped by the tick's
remaining monotonic wall budget. A rejected or budget-exhausted media fetch is
a typed partial outcome: already normalized source evidence remains queryable
while the affected lane closes truthfully.

`analysis.anomaly_rules` is optional. Each rule names one of `yield_count`,
`rejection_rate`, `latency_seconds`, or `missing_media_rate`, a `low` or `high`
direction, a minimum comparable-tick count, and warning/critical ratios. The
rule remains `learning_baseline` until the minimum exists, then uses the
versioned deterministic median evaluator. Models cannot declare or resolve an
anomaly. For a high-direction metric with a stable zero baseline, zero remains
healthy and the first positive spike is critical; this avoids permanently
learning over rejection or missing-media failures from a zero baseline.

Notification adapters are code-owned while routing is config-owned:

- `slack_receipts` requires routing fields `workspace` and `channel_ref`;
- `gws_email` requires `recipient` and optionally `subject_prefix`.

They are attempted sequentially in document order. Notification payloads
contain safe incident metadata and a protected artifact reference, never the
rendered page bytes or authentication material.

Before a gated manual run, validate the exact prospective interval and print a
sanitized admission manifest with:

```bash
python3 ~/.agents/skills/last30days/scripts/service.py tick preflight \
  --interval-from 2026-08-03T00:00:00Z \
  --interval-to 2026-08-04T00:00:00Z
```

`tick preflight` reads the user-scoped config once and uses the same config
digest, tick identity, adapter registry, enabled-lane expansion, provider
order, normalization proofs, resource ceilings, and notification adapter order
as `tick enqueue`. It performs only ordered non-message notification readiness
checks and stops after the first ready transport. Its JSON contains digests in
place of selectors, access partitions, resource keys, routing values,
credential references, artifact paths, observation endpoints, and recipient
particulars. It creates no database, artifact directory, provider attempt,
incident, message, observation lease, collection specification, or timer. An
invalid config, missing normalization proof, invalid notification adapter, or
fully unavailable notification chain fails before source work.

Run the same explicit interval manually only after the preflight's
`config_digest`, `tick_id`, and bounded manifest have been reviewed:

```bash
python3 ~/.agents/skills/last30days/scripts/service.py tick enqueue \
  --interval-from 2026-08-03T00:00:00Z \
  --interval-to 2026-08-04T00:00:00Z

python3 ~/.agents/skills/last30days/scripts/service.py tick get TICK_ID

python3 ~/.agents/skills/last30days/scripts/service.py tick incident acknowledge \
  INCIDENT_ID --actor-ref OPERATOR_REF
python3 ~/.agents/skills/last30days/scripts/service.py tick incident observe \
  INCIDENT_ID
```

These commands use the user-scoped database/config defaults unless their
documented `--db` or `--config` option is supplied. `tick preflight` has no
database option because it is state-free. `tick enqueue` is manual-only: it
does not create, resume, or enable a collection spec or timer.
`tick incident observe` accepts no URL from the caller. It returns only the
external HTTPS agent-browser operator URL stored with an acknowledged browser
incident; localhost and loopback links fail closed. Screenshot bytes remain a
protected artifact and are never included in notifications.

`publish` and `mutate_live_source_config` always require an explicit approval
record from a configured operator. Approval authorizes only the named action;
it does not execute it. Prompts, inputs, outputs, events, decisions, evals, and
approvals are written to the user-scoped intelligence ledger as
content-addressed, secret-free artifacts. Do not put cookies, tokens,
credentials, browser/profile/session identifiers, operator URLs, raw private
page data, or source configuration secrets in maintenance evidence.

Before enabling an operator workflow, verify the installed app-server
protocol:

```bash
codex app-server generate-json-schema --out /tmp/last30days-codex-schema
```

Run one bounded worker only against an existing durable service job and a
reviewed, normalized public-evidence JSON file:

```bash
python3 ~/.agents/skills/last30days/scripts/service.py intelligence enrich \
  --job-id JOB_ID --input /path/to/public-chunks.json
python3 ~/.agents/skills/last30days/scripts/service.py intelligence evaluate \
  --job-id JOB_ID --input /path/to/judged-cases.json
```

The command reserves its call and cost budget atomically before starting
Codex, includes the bounded public input in the strict-schema turn, and records
failed as well as successful calls. It rejects unknown input fields,
credential-like values, oversized evidence, and output evidence IDs that were
not supplied. Repeating the command after its call bound is consumed fails
closed.

Adapter repair is a separate explicit operator workflow:

```bash
python3 ~/.agents/skills/last30days/scripts/service.py repair investigate \
  --policy /path/to/reviewed-policy.json \
  --job-id JOB_ID --adapter reddit \
  --failure-fingerprint parser-shape-v2 --occurrences 2 \
  --evidence-id EVIDENCE_ID --diagnostic-ref ARTIFACT_REF \
  --parent-branch main

# After the proposed branch has been reviewed and repaired:
python3 ~/.agents/skills/last30days/scripts/service.py repair evaluate \
  --policy /path/to/the-same-reviewed-policy.json \
  --run-id REPAIR_RUN_ID \
  --test "uv run pytest tests/test_reddit.py"
```

The policy JSON must specify every attempt, call, cost, wall-time, input,
branch, rework, write-root, test, and approver bound. It becomes immutable for
the durable run. Branch creation uses a fixed `last30days-repair/` namespace
without checking out the operator worktree. Each exact allowlisted test runs as
argv, never through a shell, in a temporary detached Git worktree that is
removed afterward. The model remains read-only and cannot apply, publish, or
deploy the recommendation.

Normal agent clients should use only the MCP service surface. They should not
start App Intelligence turns, create repair branches, run scraper/browser
commands, or poll maintenance internals.

### Agent-facing versus operator-facing configuration

The primary `/last30days` Skill has no per-run source flags and does not read
source secrets. It calls `service_info`, then uses the ten MCP operations
advertised by the compatible service. Source availability, cache freshness,
coverage, and degradation come from that live response.

The remaining sections are operator-facing:

- service installation, upgrade, rollback, source enablement, and scheduled
  work configure durable software;
- direct CLI flags and Engine environment variables apply only to scripting,
  cron, development, or the explicitly approved compatibility/debug path;
- App Intelligence and repair commands remain privileged maintenance
  operations with their own evidence, budget, branch, evaluation, approval,
  restart, and deployment gates.

An unavailable MCP service is not permission to invoke the Engine. The
ordinary Skill reports the diagnostic and offers the compatibility path; the
user must explicitly choose it before its reference is loaded.

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
| Reddit (public) | none; optional `LAST30DAYS_REDDIT_BROWSER=1` plus `agent-browser` | RSS/Shreddit is always on; browser DOM fallback is opt-in | yes |
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

# Reddit stays keyless/public first. Opt in to a bounded agent-browser DOM
# fallback before the paid ScrapeCreators fallback.
LAST30DAYS_REDDIT_BROWSER=1
# LAST30DAYS_REDDIT_BROWSER_PROFILE=last30days-facebook
# LAST30DAYS_REDDIT_BROWSER_SESSION=last30days-reddit
# LAST30DAYS_REDDIT_BROWSER_BUILD=stealthcdp_chromium
# LAST30DAYS_REDDIT_BROWSER_VIEW_PROVIDER=rdp_gateway
# LAST30DAYS_REDDIT_BROWSER_TIMEOUT=75
# LAST30DAYS_REDDIT_BROWSER_MAX_RESULTS=10
# LAST30DAYS_REDDIT_BROWSER_SCROLLS=1
# LAST30DAYS_REDDIT_BROWSER_INITIAL_WAIT=2
# LAST30DAYS_REDDIT_BROWSER_SCROLL_WAIT=1.5

# YouTube keeps yt-dlp as its primary path. When a classified transport or
# bot-check failure exhausts it, auto uses one hidden-RDP stealth Chromium lane.
LAST30DAYS_YOUTUBE_BROWSER_FALLBACK=auto
# LAST30DAYS_YOUTUBE_BROWSER_PROFILE=stealthcdp-default
# LAST30DAYS_YOUTUBE_BROWSER_SESSION=last30days-youtube-transcripts
# LAST30DAYS_YOUTUBE_BROWSER_BUILD=stealthcdp_chromium
# LAST30DAYS_YOUTUBE_BROWSER_VIEW_PROVIDER=rdp_gateway
# LAST30DAYS_YOUTUBE_BROWSER_TIMEOUT=75

# Shared per-request control-plane timeout for every agent-browser-backed
# source. This is separate from the subprocess timeout above; when unset, each
# source's configured browser timeout is converted to milliseconds.
# LAST30DAYS_AGENT_BROWSER_JOB_TIMEOUT_MS=120000
# Shared display policy for all agent-browser-backed sources. Existing source
# defaults remain in effect when unset.
# LAST30DAYS_AGENT_BROWSER_DISPLAY_ISOLATION=private_virtual_display

# X via an authenticated agent-browser profile (opt-in; preferred over API
# backends while enabled). The default profile already used on this workstation
# is shown; use a different registered X profile elsewhere.
LAST30DAYS_X_BROWSER=1
LAST30DAYS_X_BACKEND=browser
# LAST30DAYS_X_BROWSER_PROFILE=last30days-facebook
# LAST30DAYS_X_BROWSER_SESSION=last30days-facebook
# LAST30DAYS_X_BROWSER_BUILD=stealthcdp_chromium
# LAST30DAYS_X_BROWSER_VIEW_PROVIDER=rdp_gateway
# LAST30DAYS_X_BROWSER_TIMEOUT=75
# LAST30DAYS_X_BROWSER_INITIAL_WAIT=2
# LAST30DAYS_X_BROWSER_SCROLL_WAIT=1

# X acquisition is route-bound through agent-browser remote-view so the
# retained browser is visible and controllable through Guacamole/RDP. It fails
# closed when an operator-ready route is unavailable.

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

# The Reddit, X, Facebook, and LinkedIn scrapers ask agent-browser for an access
# plan by target identity on every
# acquisition. The access plan's retained browserId and sessionName route hints
# override the optional session values above when a compatible shared profile
# owner is already live. Route IDs, browser IDs, session names, tabs, and display
# allocations are runtime leases, not durable configuration.
#
# Stable, non-secret access-plan selections are recorded at:
# ~/.config/last30days/agent-browser.json
# Set LAST30DAYS_CONFIG_DIR to place this file with the rest of the user-scoped
# last30days configuration. X reads that stable target binding as its fallback
# when an explicit per-run/environment value is absent; explicit values still
# win, and every acquisition still revalidates against the live access plan.
# The file records profile/build/host/provider/sharing policy only. It never
# records cookies, credentials, profile paths, operator
# URLs, browser/session IDs, routes, displays, tabs, or page data. The live
# access plan remains authoritative over the recorded file.
#
# Reddit remains public-first: RSS/Shreddit runs before the opt-in browser DOM
# path, and ScrapeCreators remains the final configured fallback. The browser
# routine searches post results only, emits canonical public post URLs, and
# performs no account actions.
# Facebook navigates each query through its Search control or a verified
# service-owned tab in the broker-selected retained profile.
# LinkedIn reuses one retained site tab, spaces user-like browser actions by
# at least four seconds, and stops immediately on search-limit, throttling,
# temporary-restriction, or unusual-activity warnings. A command is successful
# only when profile/auth/search readbacks pass and every
# emitted item has a canonical post permalink, author, in-range date, and useful text.
# Debug artifacts contain timings, assertions, counts, and item lengths only;
# they exclude cookies, operator URLs, raw HTML, and private page text.

Reddit, X, Facebook, and LinkedIn browser failures are typed so operator action is unambiguous. When X genuinely requires human interaction, its safe action uses agent-browser's direct external Guacamole `publicOperatorUrl`; a localhost dashboard or embed URL is diagnostic-only and is not returned as the operator handoff:

| Error type | Meaning / action |
|---|---|
| `auth_required` | Open the returned current operator URL and sign in to the configured profile. |
| `checkpoint_required` | Complete the site's security checkpoint in the operator-visible browser. |
| `rate_limited` | The X account or search lane is restricted; stop and retry after the platform cooldown. |
| `operator_ingress_unavailable` | Repair public Guacamole/dashboard ingress before retrying authentication. |
| `profile_mismatch` | The broker-selected target profile differs from the explicit configured profile constraint. |
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

### User-scoped intelligence service paths

The local cache-query service keeps browser and scraper mechanics behind a
private Unix socket. These optional host-level overrides are intended for
service managers and development:

```bash
# Defaults to $XDG_RUNTIME_DIR/last30days/service.sock
LAST30DAYS_SERVICE_SOCKET=/run/user/1000/last30days/service.sock

# Defaults to $XDG_DATA_HOME/last30days/research.db, or
# ~/.local/share/last30days/research.db when XDG_DATA_HOME is unset.
LAST30DAYS_SERVICE_DB=~/.local/share/last30days/research.db

# Optional local Graphiti graph-service projection. Loopback HTTP only.
LAST30DAYS_GRAPHITI_URL=http://127.0.0.1:8829
LAST30DAYS_GRAPHITI_GROUP_PREFIX=last30days
LAST30DAYS_GRAPHITI_TIMEOUT_SECONDS=10
LAST30DAYS_GRAPHITI_INTERVAL_SECONDS=30
```

Explicit `service.py --socket` and `--db` flags win over these variables. The
runtime directory is owner-only (`0700`), and the socket, lock, and database
are owner-readable/writable only (`0600`). These paths contain no browser
cookies or credentials; authenticated acquisition remains isolated in named
user-scoped profiles.

Build and install the Linux user service independently of an Agent Skill:

```bash
bash service/scripts/build-runtime.sh
bash service/scripts/install.sh install \
  --artifact dist/service/last30days-service-0.2.9.tar.gz
bash service/scripts/install.sh diagnose

service_launcher="${XDG_DATA_HOME:-$HOME/.local/share}/last30days/service/last30days-service"
"$service_launcher" status
"$service_launcher" query "agent browser reliability" --freshness prefer_cache
"$service_launcher" job <job-id>
"$service_launcher" job <job-id> --resume
```

When a durable tick head has been promoted, ordinary `query` responses use
that coherent terminal snapshot rather than the legacy document index. The
response `index_version` is the tick snapshot ID, `tick_snapshot` carries exact
terminal coverage and interval/promotion freshness, and each evidence item
exposes its authorized `access_partition_id`, `matching_channels`, and
provenance. Profile queries include public plus only that named profile
partition; source and published-time filters are applied before retrieval.

Use `job <job-id> --resume` only after the human action recorded by an
`awaiting_operator` job is complete. The service returns that same bounded job
to `queued`, preserves its attempt count and event history, and rejects resume
when the job is in another state or has exhausted its configured attempts. The
resume command does not open a browser, authenticate, or bypass the original
human gate.

### Recurring collection specifications

The same long-running user service owns recurring collection; no separate
per-topic cron process or browser-launching systemd timer is required. The
service polls durable due state every 30 seconds, creates one interval run, and
coalesces a manual request for the same spec and interval onto that run and its
existing refresh job.

Create or revise a specification from a reviewed strict JSON file:

```bash
python3 scripts/service.py collection put --input /path/to/collection.json
python3 scripts/service.py collection list
python3 scripts/service.py collection run spec-reddit-ai
python3 scripts/service.py collection run spec-reddit-ai --max-attempts 2
python3 scripts/service.py collection pause spec-reddit-ai
python3 scripts/service.py collection resume spec-reddit-ai
```

Resuming a paused specification resets its due boundary to the current
interval. Intervals that elapsed while the specification was disabled are not
replayed as catch-up work. Revising an already enabled specification preserves
its existing due boundary.

Manual runs default to one durable job attempt. An operator with a separately
reviewed retry budget may set `--max-attempts 2`; values outside 1-2 are
rejected before a run is created. The second attempt remains service-owned
inside the same immutable run/job identity. It is scheduled only for a
`worker_timeout`, `agent_browser_timeout`, `agent_browser_error`, or
`route_stale` transient whose immutable receipt proves zero accepted, stored,
deduplicated, and indexed side effects. Rate limits, content failures,
unexpected worker errors, missing counts, and expired leases without a
complete receipt fail closed without consuming attempt two. The flag does not enable a
specification, change timer runs, replay a terminal interval, or authorize a
different selector, source, profile, access method, cost, or data scope.

Example:

```json
{
  "schema_version": 1,
  "collection_spec_id": "spec-reddit-ai",
  "name": "Reddit agent intelligence",
  "source": "reddit",
  "surface_kind": "topic",
  "selector": {"topic": "agent intelligence"},
  "profile_id": "default",
  "interval_seconds": 3600,
  "lookback_seconds": 7200,
  "item_limit": 20,
  "wall_timeout_seconds": 90,
  "network_request_limit": 50,
  "budget_cents": 25,
  "required_access_method": "keyless",
  "retention_class": "cache",
  "redaction_class": "public",
  "assessment_enabled": true,
  "enabled": true,
  "spec_version": 1
}
```

`surface_kind` accepts `feed`, `topic`, `poster`, `channel`, `account`, or
`profile`. Its selector must contain exactly the matching key (`feed`, `topic`,
`poster`, `channel`, `account`, or `profile_url`). Item, network, time, cost,
lookback, and cadence bounds are mandatory. X, Facebook, and LinkedIn specs
must use `redaction_class=authenticated`; their named profile is leased so two
collection runs cannot operate the same retained browser profile
concurrently.

Set `required_access_method` when a production specification must use exactly
one method instead of the source-wide fallback order. The allowed method must
belong to the selected source: Reddit accepts `keyless`, `agent_browser`, or
`scrapecreators`; X, Facebook, and LinkedIn accept `agent_browser`; YouTube
accepts `yt_dlp`. The service freezes the constraint with the spec revision,
selects the matching worker adapter and cost reservation, and fails closed on
a source/method mismatch. Historical specifications may omit the field for
backward compatibility and continue to use the configured source access
order.

`collection list` includes the latest completed run as `last_run` when the
installed service has a versioned observability receipt. The receipt binds the
exact governed source-request count; attempted/observed/accepted/rejected/
stored/deduplicated/indexed counts; attempted and selected access method plus
adapter variant; and pre/post document, embedding, and active-index snapshots.
Python HTTP calls count individually. Opaque yt-dlp and browser adapters count
one governed top-level source-search invocation at their adapter seam;
internal navigation, browser assets, and subresource traffic are outside this
governed unit. Legacy
runs remain readable and omit evidence fields they never recorded rather than
reporting inferred zeroes.

For LinkedIn profile collection, `selector.profile_url` must be an exact
canonical `https://www.linkedin.com/in/<slug>/` or
`https://www.linkedin.com/company/<slug>/` URL. The adapter reads only that
people/company page and never messages, connections, invitations, or adjacent
private surfaces. Raw page evidence is committed before immutable
section-level profile projection. Missing or hidden sections are recorded as
`not_observed`, not as real-world removals. App Intelligence may assess a
host-created change or identity candidate, but it cannot invent a candidate or
merge accounts directly.

Every run records its attempted interval, selector digest, attempted/observed/
stored counts, cursor and watermark movement, source process health, yield,
backoff, and any uncovered gap. Service health and content yield are separate:
a healthy zero-result run is `observed_empty`, not a process failure.

Raw immutable document versions and evidence are committed before an optional
`content_assessment` task is queued. The task carries only bounded evidence
references and host-assigned digests; it never receives cookies or browser
mechanics. Assessment failure is recorded independently and cannot roll back,
hide, or fail the acquisition. Turning assessment off leaves recurring
collection and cached queries fully operational.

Stochastic assessment processing is opt-in at user scope:

```bash
LAST30DAYS_APP_INTELLIGENCE_ASSESSMENT=true
LAST30DAYS_CODEX_PATH=codex
LAST30DAYS_APP_INTELLIGENCE_MODEL=
LAST30DAYS_APP_INTELLIGENCE_TIMEOUT=60
```

When disabled, strict assessment tasks remain queued and replayable while
acquisition continues. When enabled, a separate bounded loop claims one task,
materializes only its authorized immutable evidence spans, invokes Codex
app-server with a strict `content_assessment` output schema, and applies the
deterministic evidence/domain/policy validators before recording validation,
promotion, and replay receipts. `LAST30DAYS_APP_INTELLIGENCE_MODEL` is optional
and uses the app-server default when empty. The timeout is seconds and must be
positive; the service caps it at the task contract's 60-second wall-time limit.

Use `service/scripts/install.sh upgrade --artifact <artifact>` for a new
semantic service version. The installer verifies every payload SHA-256, stages
an immutable release, records the old `current` target as `previous`, switches
atomically, and restarts once. It accepts the upgrade only when the service
reports the expected version, exact contract digest, and schema 16. A failed
upgrade restores the prior selectors, restarts, and proves the old release
ready. Use `service/scripts/install.sh rollback` to swap the current and
previous verified releases deliberately; `start`, `stop`, `status`, and
`diagnose` provide the remaining lifecycle controls.

The v4 release uses independent artifact versions: Skill/plugin `4.0.0`, MCP
adapter `4.0.1`, and service `0.2.9`. Upgrade the service first, install the
adapter second, and require `service_info` to report
`compatibility_state=compatible` before updating the optional Skill. Schema 12
needs no migration. A typed incompatibility means one side is stale; it does
not authorize source credentials or direct Engine work in the ordinary path.

Pass `--socket <absolute-path>` to install, upgrade, or diagnose a non-default
owner-private socket. The installer records that same path in the stable unit
and uses it for readiness; otherwise `LAST30DAYS_SERVICE_SOCKET` wins, followed
by `$XDG_RUNTIME_DIR/last30days/service.sock`.

The installer writes `~/.config/systemd/user/last30days.service`, reloads the
user manager, and enables the service. Its unit uses an owner-private umask,
restart-on-failure, `NoNewPrivileges`, and a stable PATH containing
`~/.local/bin` and the reference Linuxbrew paths. It also loads the optional
owner-scoped
`~/.config/last30days/.env`, so the daemon and its acquisition subprocesses
see the same explicit source enablement and profile routing as direct runs.

Register the thin MCP adapter with Codex from a source checkout:

```bash
bash mcp/scripts/install-codex.sh
codex mcp get last30days
```

The installer builds the current checkout, atomically installs
`~/.local/bin/last30days-pp-mcp`, and records the private service socket in the
user-scoped Codex MCP configuration. Re-run it after MCP adapter changes.

Service-enabled MCP clients expose ten compact operations:

- `service_info`: discover readiness, sources, capabilities, and index state;
- `query`: read cached evidence or a compact brief under an explicit freshness
  policy;
- `refresh`: create or join a bounded `force_refresh` job;
- `job_status`: poll the typed durable job record;
- `topic`: list or manage service-owned topics and request scheduled refreshes.
- `temporal_query`: read cache-only evidence, briefs, timelines, entity/event
  dossiers, trends, or comparisons with independent `as_of`, `during`, and
  `known_as_of` bounds;
- `profile_history`: read immutable source-account/profile snapshots and exact
  section evidence without operating a browser;
- `coverage`: inspect authorized collection specs, attempted intervals, yield,
  and unresolved gaps;
- `collection`: list, put, pause, resume, or manually run typed recurring
  collection specs through the durable supervisor;
- `maintenance_status`: read graph delivery and bounded App Intelligence
  receipts/safety gates plus canonical task contract names, versions, and
  validator-enforced limit ranges without prompts, raw provider events, or
  repair execution.

The MCP adapter connects to the same Unix socket. A standalone Linux MCPB
packages the independently versioned service artifact plus its lifecycle
controls and may install/start it through the managed user-service path when
absent. It never detaches raw `service.py` or owns the daemon. A query handler
never launches the request-scoped research engine or operates a browser.

`temporal_query`, `profile_history`, `coverage`, and `maintenance_status` are
read-only and cache-only. The host derives authorized access partitions from
`profile_id`; clients cannot submit an arbitrary partition list. `default`
authorizes public evidence only, while a named profile authorizes public plus
that exact `profile:<id>` partition.

When `LAST30DAYS_GRAPHITI_URL` is set, a separate bounded loop sends accepted
claim/event projections from the SQLite outbox to partition-specific Graphiti
groups. The URL must be loopback HTTP. SQLite remains authoritative; Graphiti
failures are retained in the outbox and surfaced as degraded status without
blocking evidence retrieval. Projection receipts bind the stable graph node,
payload digest, and partition-specific group. The remaining Graphiti variables
set a safe group prefix, request timeout, and delivery cadence.

The service never loads project-directory `.env` files. Its deterministic
supervisor resolves acquisition settings at user scope:

```text
~/.config/last30days/.env
~/.config/last30days/profiles/<profile-id>.env
```

The named profile overlays the user default, and process environment variables
win over both files. Profile IDs may contain letters, digits, `.`, `_`, and
`-`; they are carried in query contracts and never inferred from a client's
working directory. Keep both files owner-only (`chmod 600`). The service stores
only the profile ID, adapter name/version, safe outcome codes, and content
provenance—not cookies, tokens, browser routes, or session payloads.

Choose the service-owned source catalog and each source's ordered access chain
in the user-scoped `~/.config/last30days/.env`:

```bash
LAST30DAYS_SERVICE_SOURCES=reddit,x,facebook,linkedin,youtube
LAST30DAYS_REDDIT_ACCESS_ORDER=keyless,agent_browser
LAST30DAYS_X_ACCESS_ORDER=agent_browser
LAST30DAYS_FACEBOOK_ACCESS_ORDER=agent_browser
LAST30DAYS_LINKEDIN_ACCESS_ORDER=agent_browser
LAST30DAYS_YOUTUBE_ACCESS_ORDER=yt_dlp
```

Catalog order is preserved. Reddit supports `keyless`, `agent_browser`, and
`scrapecreators`; the other supported mappings are X/Facebook/LinkedIn to
`agent_browser` and YouTube to `yt_dlp`. An explicit order is authoritative:
the worker tries only those methods, in that order, and never appends a hidden
paid fallback. A method is ready only when its local prerequisite is present
(`agent-browser` or `yt-dlp` on the service PATH, or
`SCRAPECREATORS_API_KEY`). Empty entries, duplicates, unknown sources, and
methods assigned to the wrong source fail closed during service startup.

When these variables are absent, the service retains the legacy catalog and
enablement behavior for compatibility. Prefer the explicit form for managed
recurring collection so the daemon's effective policy is reviewable without
changing a collection specification.

The MVP acquisition registry supports `reddit`, `x`, `youtube`, `facebook`,
and `linkedin`. Cache queries are served immediately. A stale or missing
`prefer_cache`, `refresh_if_stale`, or `force_refresh` request creates or joins
one durable refresh job; acquisition runs in a bounded subprocess and publishes
successful sources even when another source needs operator authentication or a
retry. `cache_only` never queues work.

Service discovery distinguishes an enabled source (`configured`) from one
that passes a non-mutating local readiness probe (`acquisition_ready`). Reddit's
keyless path is ready by construction; YouTube requires `yt-dlp` on the service
PATH. Browser-backed sources remain `configured` until profile-specific work
proves authentication, so discovery does not mistake an installed
`agent-browser` binary for a usable signed-in session. A background acquisition
loop failure changes service status to `degraded` while cached queries remain
available.

Semantic enrichment uses the dependency-free `local-hash-v1` provider by
default and publishes embeddings asynchronously. Generic deterministic entity
extraction is enabled in the service runtime. Either enrichment lane may
degrade without blocking lexical cache queries; discovery advertises semantic
or graph search only when the current published index and live query provider
can serve it.

Each refresh has a host-owned attempt and cost ceiling. The host reserves the
maximum configured adapter cost before launch (currently one cent for Reddit's
optional ScrapeCreators fallback and zero for the other MVP adapters); workers
cannot raise that ceiling with self-reported usage. The worker also enforces its
request/item/time limits, caps stdout and stderr, and counts direct Python HTTP
attempts against the issued network allowance. External tools remain bounded by
one isolated worker subprocess, the wall timeout, output limits, and process
group cancellation.

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
