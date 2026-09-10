# Plan 0063 Agent Browser Tick Incident

Date: 2026-09-09 America/Chicago (`2026-09-10` UTC)

Plan: [0063](../plans/0063-2026-09-09-bounded-tick-and-agent-browser-incident-capture.md)

## Scope And Authority

The operator authorized exactly one additional schedule-disabled Last30days
tick and requested useful Agent Browser troubleshooting notes if browser access
failed. This receipt records that one attempt. It does not authorize a second
tick, Agent Browser repair, profile mutation, supervisor restart, runtime
reconciliation, cleanup, or installation.

Secrets, capability contents, page content, authenticated URLs, cookies, and
credentials are intentionally omitted. Agent Browser request and tab IDs are
retained because they are the correlation keys for its local job/trace ledger.

## Tick Receipt

- Tick: `tick-22c576498aff25c201ec855d75a947ae`
- Schedule ID: `manual-p0063-20260910-030829`
- Interval: `2026-09-09T03:08:29Z` through `2026-09-10T03:08:29Z`
- Created: `2026-09-10T03:09:41.327629Z`
- Terminal: `2026-09-10T03:16:02.619394Z`
- State: `complete_degraded`
- Configuration revision: `operator-20260903-reddit-home-feed-80-v1`
- Configuration digest:
  `sha256:8e3811d5e9b561cfd3f97b3d9897770ee4c623fe9e74a443bc01d86fca4d3449`
- Tick budget consumed: 8/10 attempts, 83/243 items, 60/500 network
  requests, 374/3360 wall seconds, zero model tokens and zero cost.
- Promoted query head:
  `tick-snapshot-43e60f758cdde8a3d188734ed8980859`; completeness is
  X success, YouTube success, LinkedIn failure, Reddit failure.

| Lane | Terminal state | Attempts | Observed | Accepted | Attempt duration |
| --- | --- | ---: | ---: | ---: | ---: |
| X | success | 1 | 254 | 80 | 149.3 s |
| YouTube | success | 1 | 8 | 3 | 2.5 s |
| LinkedIn | failure | 3 | 0 | 0 | 125.5 s |
| Reddit home feed | failure | 3 | 0 | 0 | 101.3 s |

The promoted snapshot contains 80 X and three YouTube lexical-source entries.
No LinkedIn or Reddit source entry was published. X also supplied four OCR,
nine alt-text, and ten semantic-sidecar entries; YouTube supplied three
alt-text and three semantic-sidecar entries.

## Agent Browser Correlation

Every browser request used registered-capability identity for service
`last30days`, profile `last30days-facebook`, runtime lane and browser
`terminal-profile-9f8e03bff56faa5b7aae7a5c`, and policy revision 1.
The successful X lane used this same browser, so this is not evidence of a
total service or profile outage.

### LinkedIn

All three attempts acquired a new tab and navigated. Two terminal failures are
retained by Agent Browser:

| Job | Tab | Failure | Wait | Recourse |
| --- | --- | --- | ---: | --- |
| `mcp-service-request-evaluate-38551e18-0cc8-4763-92d0-643dd3e6d4eb` | `target:911C1958A7ABE73DDF22DF78E4822B68` | `service_state_lock_timeout`, `file_lock_wait` | 2162 ms | `inspect_before_retry` |
| `mcp-service-request-evaluate-4b2dc180-fddc-4b86-ba0b-6d780f2ed14d` | `target:8452544CEB8F424754201C771404D386` | `service_state_lock_timeout`, `file_lock_wait` | 1001 ms | `inspect_before_retry` |

Agent Browser classified both effects as uncertain, recommended
`inspect_job_and_refresh_plan`, exposed job/trace inspection plus access-plan
refresh as safe next actions, and marked `blind_retry` as a hard stop. The
first Last30days attempt ended during extraction with a separate
`agent_browser_error`; its Agent Browser operations show successful tab,
evaluate, and navigation work before the final evaluate failed, but the
provider result did not expose a stable reason code.

### Reddit home feed

Each attempt successfully created a distinct tab. The immediately following
`ui_action` then consumed roughly 29 seconds and failed while enabling the CDP
domain:

| Job | Tab | Exact error |
| --- | --- | --- |
| `mcp-service-request-ui_action-a5b9561a-7ce6-48e7-8b84-ddd202560810` | `target:8E083A3D95E39D17A7F68972A58ED65B` | `CDP command timed out: Page.enable` |
| `mcp-service-request-ui_action-229f2444-3449-40c9-aa97-f29fd730b5db` | `target:68089A076902C7CEA2622A9E0FB5C76F` | `CDP command timed out: Page.enable` |
| `mcp-service-request-ui_action-b842ba77-7d41-4aaf-980c-53f741e0de60` | `target:5A98C623E857DA9836D4DE926DD29B19` | `CDP command timed out: Runtime.enable` |

Agent Browser classified all three as `service_job_timed_out`, effect
uncertain, `inspect_before_retry`, with `blind_retry` as a hard stop. The
Last30days adapter consequently reported three identical
`workspace_acquisition` / `agent_browser_timeout` signatures. One Agent Browser
incident and three events are joined to the Reddit trace.

## Runtime Time Ordering

Agent Browser was changing in its independent source/runtime lane during this
observation. Before the tick, workstation admission had cleared after upgrade
transaction `upgrade-bb44488d-b625-4627-8e73-1c7973240c19` terminalized
`failed_preserved_old_generation`; doctor then reported zero runtime hosts and
an inactive `runtime-host` supervisor with a missing manifest.

The post-terminal readback is newer and must be used for follow-up:

- installed Agent Browser version `0.28.0`, selected generation
  `0.28.0-5928ff06d8d0-927b55137ad0`;
- transaction `upgrade-bb08b9a3-3002-4f07-bad4-e79bf57a20a1` has an accepted,
  inactive convergence window;
- multiplicity is `steady_current`: one executable generation, one runtime
  host, one dashboard process, and no legacy daemon;
- reconciliation and the runtime monitor are fresh and healthy, and the
  service reports ready;
- overall runtime lifecycle remains degraded and `install doctor` remains
  unsuccessful because the sole dashboard supervisor is inactive/dead with a
  `port_conflict` (its configured stream port is reachable without matching
  session-stream metadata);
- doctor separately flags the `last30days-facebook` profile lease for
  `owner_generation_or_binding_mismatch` and `unproven_session_authority`.

The current Agent Browser source authority is the independent dirty worktree
on `plan/profile-permissions-and-request-provenance`, published at `bbe12903`
(`fix supervised workstation upgrade completion`). Its Runbook Turn 287 keeps
supervisor replacement and single-runtime convergence open under P116, Plan
0161 owns first-class preserving profile repair/reset, and Plan 0142 already
models intermittent `service_state_lock_timeout` contention and requires
inspect-before-retry recourse. No file in that worktree was changed here.

## Axis Verdicts

- Last30days scheduler: healthy for this bounded operation; the manual ID did
  not alter `daily-default`.
- Provider acquisition: X and YouTube succeeded; LinkedIn and Reddit failed.
- Agent Browser acquisition/execution: partially available, with a proven
  shared-browser X success alongside LinkedIn file-lock contention and Reddit
  CDP-domain enable timeouts.
- Presentation: not exercised or accepted by this headless collection tick.
- Agent Browser maintenance: one current runtime is converged, but doctor is
  still red on supervisor and profile-lease evidence.
- Cleanup: zero active Last30days ticks, zero open tick resource leases, and
  SQLite `quick_check` is `ok`.

## Recommended Agent Browser Follow-Up

Start from the five exact failed job IDs above and the current post-upgrade
generation. Preserve the `inspect_before_retry` boundary. For LinkedIn,
correlate the file-lock holder and critical section against Plan 0142. For
Reddit, compare the three newly created targets and their browser process/CDP
endpoint health at `Page.enable` / `Runtime.enable`; the failure occurs after
tab creation, not before profile access. Reconcile the current
`last30days-facebook` owner-generation/binding and session-authority warnings
through Plan 0161's preserving workflow. Treat supervisor presentation repair
as a separate axis. Only after those current-state checks should a new
Last30days canary be proposed under fresh authority.
