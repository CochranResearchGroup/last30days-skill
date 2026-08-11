# Plan 0044 | Agent Browser CDP Input Scroll Repair

State: CLOSED
Roadmap: P20
Plan version: 2
Date: 2026-08-11
Predecessor: Plan 0043 version 3/checkpoint P0043-C03

## Objective

Repair agent-browser's selectorless page scroll to use Chromium CDP input-wheel
delivery instead of renderer JavaScript, then prove one installed Facebook-only
tick can publish accepted durable evidence and serve it from the exact named
profile cache.

## Current State

- Last30Days service 0.3.46 and MCP 4.0.3 remain installed ready/compatible at
  schema 16, and the recurring daily schedule is unchanged;
- Plan 0043's exact agent-browser candidate is installed and its evaluation
  deadline repair worked in the live tick while preserving Facebook browser
  PID 13177 and its tabs;
- the sole Plan 0043 tick is terminal and will not be retried. It navigated and
  evaluated successfully, then selectorless scroll operation `r958354` failed
  after 28.49 seconds in `Runtime.evaluate`;
- later tab inventory succeeded, and source inspection binds selectorless
  scroll to JavaScript `window.scrollBy`; the browser-level CDP channel and
  retained profile remain healthy.

## Scope

- continue in the isolated agent-browser worktree at exact installed commit
  `1c1331efefbb41d7c5ba2384089eb2bfbd358f81`;
- add one fake-CDP red/green regression for selectorless page scroll and
  implement the minimal browser-level CDP input-wheel path;
- preserve selector-targeted element scrolling, response contracts, browser
  identity, profile contents, and recurring schedule;
- validate, commit, build, and install one exact dependency candidate through
  the supported browser-preserving path;
- after fresh installed service, database, schedule, and profile preflight,
  consume at most one new Facebook-only tick for the same closed interval;
- on success, prove accepted durable evidence through a named-profile
  cache-only query and reconcile both repositories and installed runtime.

## Non-Goals

- no retry of Plan 0043's tick; no Facebook selector/extraction rewrite,
  timeout increase, browser restart/close, profile reset, login,
  reauthentication, CAPTCHA/checkpoint handling, route mutation, recurring
  schedule mutation, source expansion, fallback, model use, paid request,
  public push, or formal release;
- no generalized interaction refactor or change to selector-targeted scrolling.

## Acceptance Criteria

1. A fake-CDP regression fails against the JavaScript selectorless scroll path
   and passes only when the actual path emits the requested horizontal and
   vertical deltas through `Input.dispatchMouseEvent` type `mouseWheel`.
2. Focused Rust tests pass twice; formatting, strict production Clippy,
   repository-selected validation, and required canonical Rust gates pass.
3. The exact committed candidate installs without restarting or replacing the
   retained Facebook browser, CDP endpoint, or target inventory.
4. Fresh service/database/schedule/profile preflight passes before any provider
   operation.
5. One new Facebook-only tick reaches terminal success with accepted durable
   evidence, and an MCP `cache_only` query with explicit
   `profile_id=last30days-facebook` returns that accepted evidence.
6. Current and rollback databases pass integrity, the daily schedule is
   unchanged, exact tick/provider/snapshot/operation receipts are preserved,
   and both Git repositories are reconciled without touching unrelated state.

## Execution Bounds And Gates

- maximum work-unit attempts: 2; maximum focused rework cycles: 1; one source
  red/green pass, one candidate commit/build/install, and one Facebook tick;
- no live Facebook operation before the dependency candidate is committed,
  validated, installed, and browser-preserving preflight passes;
- stop without retry on profile/browser identity drift, auth/challenge/rate
  evidence, source or integrity failure, terminal tick failure, or any effect
  outside this plan;
- no subagent delegation under the current orchestration restriction.

## Work Graph

| Packet | Outcome | Depends on | Gate |
|---|---|---|---|
| S01 repro | Existing selectorless scroll emits renderer JavaScript | C01 | exact fake-CDP red |
| S02 repair | Selectorless scroll emits browser-level wheel input | S01 | focused green twice |
| S03 candidate | Exact committed dependency candidate | S02 | required source gates |
| S04 install | Browser-preserving runtime convergence | S03 | PID/endpoint/tab proof |
| S05 acceptance | One terminal Facebook tick plus named cache proof | S04 | no retry |
| S06 closeout | Both repos, DBs, schedule, and runtime reconcile | S05 | terminal receipts |

### Checkpoint P0044-C01 | 2026-08-11

Plan version: 1

State transition:

- `terminal_distinct_scroll_failure -> selectorless_scroll_owner_identified`.

Progress classification:

- `blocker_reduction`; the failed browser operation is now bound to one exact
  generic scroll implementation while browser-level CDP health remains proven.

Validation evidence:

- operation `r958354` is action `scroll`, state `failed`, started
  `2026-08-11T05:07:48.245718588Z`, completed
  `2026-08-11T05:08:16.739741811Z`, and reports
  `CDP command timed out: Runtime.evaluate`;
- structural source inspection shows selectorless `interaction::scroll`
  constructs `window.scrollBy(dx, dy)` and calls the fixed typed evaluation
  transport; later `tab_list` success proves the browser-level CDP channel
  remains usable;
- the strongest repair hypothesis is CDP input-wheel delivery. A longer timeout
  is rejected because it only extends the wait on a trivial renderer script;
  Facebook auth/profile failure is rejected by successful navigation,
  evaluation, and later inventory.

Subagent status and reconciliation:

- `not_spawned`; current orchestration policy prohibits delegation.

Authority classification:

- `inherited_authority`; the active goal permits this bounded successor and one
  new tick because the owning implementation strategy changed without widening
  the approved systems, source, profile, data, schedule, or effect ceiling.

Review disposition summary:

- `blocking=1` selectorless JavaScript scroll; `needs_evidence=3` source
  red/green, installed convergence, live acceptance; `rejected=2` longer wait
  and auth/profile failure; `nonblocking_backlog=0`.

Graphiti write status:

- deferred until a terminal validated outcome.

Next action:

- add the exact fake-CDP wheel regression red, implement only the selectorless
  scroll transport change, and stop before install unless every source gate
  passes.

### Checkpoint P0044-C02 | 2026-08-11

Plan version: 1

State transition:

- `selectorless_scroll_owner_identified -> dependency_candidate_installed`.

Progress classification:

- `blocker_reduction`; selectorless page scroll now uses browser-level wheel
  input in the exact installed runtime and the retained Facebook lane survived
  the executable handoff.

Validation evidence:

- the fake-CDP regression was red against `Runtime.evaluate`, then passed twice
  with `Input.dispatchMouseEvent`, type `mouseWheel`, exact session routing, and
  both deltas;
- all 11 interaction tests and the existing real-Chrome scroll e2e passed
  twice; formatting, strict production Clippy, selected validation, patch
  checks, and the canonical Rust runner passed 1,043 parallel-safe tests with
  57 ignored plus every serialized partition;
- exact commit `a954bc95023b16e2bee5c9d6dfe369915e748f0c` installed as
  SHA-256 `76b2779ffc65d85f22817c698732e387dffe9cd4f8225f9aaf6b65bba467d3d1`;
- Facebook browser PID 13177 and endpoint
  `ws://127.0.0.1:38770/devtools/browser/00317084-6844-44c8-b1a3-c63555867ced`
  were retained, workstation provenance matches, and runtime convergence is
  `converged`;
- install doctor has only the pre-existing nonblocking duplicate-profile
  warning; service resources report zero candidates and zero
  readiness-impacting candidates.

Subagent status and reconciliation:

- `not_spawned`; current orchestration policy prohibits delegation.

Authority classification:

- `inherited_authority`; the one candidate installation is complete and the
  remaining provider attempt stays inside the original Facebook/profile/data
  ceiling.

Review disposition summary:

- `blocking=0` at source/install seams; `needs_evidence=2` fresh Last30Days
  preflight and one terminal tick plus cache proof; `rejected=1` duplicate
  warning as an acceptance blocker because it has zero readiness impact;
  `nonblocking_backlog=0`.

Graphiti write status:

- deferred until terminal downstream evidence.

Next action:

- run exact installed service, database, schedule, and profile preflight; only
  if all gates pass, consume Plan 0044's one Facebook-only tick.

### Checkpoint P0044-C03 | 2026-08-11

Plan version: 2

State transition:

- `dependency_candidate_installed -> terminal_upstream_stale_capture_failure`.

Progress classification:

- `blocker_reduction`; the generic selectorless scroll repair is installed and
  proven, while the terminal tick revealed the Last30Days stale prepared
  extraction that unnecessarily forces the live Facebook target into scroll.

Validation evidence:

- fresh preflight was `ready`, both current and rollback databases returned
  `ok`, Facebook acquisition and profile/browser health were ready, and the
  recurring schedule remained unchanged;
- the sole tick `tick-877ca3d32b5e6c335d60b585fc631985`, execution
  `tick-attempt-c993973488088fbd9741f4d9a0728535`, provider attempt
  `provider-attempt-f707213d4b51646f759db74f02f38799`, and snapshot
  `tick-snapshot-d5cb7ff1f0e49cbce2a1b4de889287e2` are terminal with zero
  accepted items and no retry;
- navigation and initial evaluation succeeded; exact wheel job `r213109` then
  failed after 28.37 seconds with
  `CDP command timed out: Input.dispatchMouseEvent`, while later tab inventory
  remained responsive;
- source readback proves the replacement-target combined query capture extracts
  immediately after navigation. `search()` then sleeps four seconds but
  `_extract()` accepts the stale empty prepared dict, skips a fresh DOM read,
  and forces scroll. The post-wait extraction contract is therefore not being
  honored.

Subagent status and reconciliation:

- `not_spawned`; current orchestration policy prohibits delegation.

Authority classification:

- `inherited_authority`; successor Plan 0045 changes only Last30Days extraction
  freshness and preserves all existing systems, source/profile/data/schedule,
  install, and one-attempt ceilings.

Review disposition summary:

- `blocking=1` stale empty prepared extraction bypasses the post-wait DOM read;
  `needs_evidence=3` red/green contract, installed service convergence, and one
  downstream acceptance tick; `rejected=1` another browser transport variant;
  `nonblocking_backlog=0`.

Graphiti write status:

- deferred until terminal successor evidence.

Next action:

- close P20/Plan 0044 without retry and execute Plan 0045/P21's bounded stale
  prepared-extraction refresh.

## Definition Of Done

- criteria 1-6 have current source, commit, installed-runtime, durable tick,
  and cache evidence; tests or installation alone do not satisfy completion.
