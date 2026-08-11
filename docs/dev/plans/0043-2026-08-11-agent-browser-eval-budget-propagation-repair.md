# Plan 0043 | Agent Browser Eval Budget Propagation Repair

State: CLOSED
Roadmap: P19
Plan version: 3
Date: 2026-08-11
Predecessor: Plan 0042 version 4/checkpoint P0042-C04

## Objective

Repair the owning agent-browser evaluation deadline chain so a positive global
`--job-timeout-ms` above 30 seconds reaches both Chromium's renderer deadline
and the CDP transport, then prove one installed Last30Days Facebook tick can
publish accepted evidence without changing the retained profile or recurring
schedule.

## Current State

- Last30Days service 0.3.46 and MCP 4.0.3 are installed ready/compatible at
  schema 16; Plan 0042's sole tick is terminal and will not be retried;
- that tick passed acquisition, retained-tab selection, target replacement,
  and navigation, then its final eval returned `agent_browser_error` after
  31.810 seconds even though the caller supplied a 45-second job deadline;
- current agent-browser source caps every renderer evaluation at 25,000 ms and
  routes it through `CdpClient::send_command`, whose fixed transport deadline
  is 30 seconds. Plan 0097 introduced both limits before callers could carry a
  longer global job deadline;
- a socket-backed virtual-time regression delayed a response to virtual second
  31 and captured the current fixed-transport failure. Tokio virtual time could
  not deterministically order kernel WebSocket delivery, so the durable test
  seam binds both deadlines in the request contract consumed by production;
- the primary agent-browser checkout is on an unpushed architecture branch
  with an unrelated untracked build directory. Any source repair must use a
  separate worktree based on its exact current HEAD so installed architecture
  behavior is preserved and user state remains untouched.

## Scope

- create one isolated agent-browser worktree from exact commit `baaed508`;
- add one red public BrowserManager/fake-CDP regression for a 45-second caller,
  virtual 31-second response, and 44.75-second renderer deadline;
- change only evaluation deadline propagation at the owning browser/CDP seam;
- run focused and required agent-browser validation, commit the isolated
  candidate, build and install it through the repo-supported browser-preserving
  path, and verify retained browser identity;
- after fresh Last30Days/service/database/schedule/profile preflight, consume at
  most one new Facebook-only tick for the same closed interval and reconcile
  both repositories.

## Non-Goals

- no browser restart/close, profile reset, login, reauthentication, CAPTCHA,
  checkpoint, tab cleanup, route mutation, recurring-schedule mutation, source
  expansion, provider fallback, model use, paid request, or formal public
  release;
- no retry of Plan 0042's tick and no change to non-evaluation CDP command
  deadlines;
- no edits in the dirty primary agent-browser checkout.

## Acceptance Criteria

1. The exact fake-CDP regression is red because current evaluation transport
   fails at 30 seconds and renderer parameters cap at 24.75 seconds.
2. One minimal agent-browser repair makes a 45-second evaluation send a
   44.75-second renderer deadline and use a covering caller-selected transport
   deadline through one deterministic request contract consumed by the actual
   CDP call.
3. Focused Rust, format, strict production Clippy, validation selection, and
   all required touched-surface gates pass from the isolated worktree.
4. The exact committed candidate installs without restarting or replacing the
   retained `last30days-facebook` browser, and install/runtime doctors pass.
5. One new Facebook-only tick reaches terminal success with accepted durable
   evidence and a named-profile cache readback; any terminal failure stops
   without retry and preserves its exact operation receipt.
6. Current and rollback databases pass integrity, the daily schedule is
   unchanged, both repositories are reconciled, and no unrelated dirty state is
   modified.

## Definition Of Done

- criteria 1-6 have current source, commit, installed-runtime, and live receipt
  evidence; completion is not inferred from unit tests or installation alone.

## Execution Bounds And Gates

- maximum work-unit attempts: 2; maximum focused rework cycles: 1; one isolated
  agent-browser worktree, one installed candidate, and one Facebook-only tick;
- no live Facebook operation before the dependency candidate is committed,
  validated, installed, and browser-preserving preflight passes;
- stop on profile/browser identity drift, auth/challenge/rate-limit evidence,
  unsafe route, integrity failure, browser restart need, validation failure,
  terminal tick failure, or any effect outside this plan.

## Work Graph

| Packet | Outcome | Depends on | Gate |
|---|---|---|---|
| B01 repro | Current 30-second transport fails virtual second-31 response | C01 | exact red test |
| B02 repair | Caller budget reaches renderer and CDP transport | B01 | focused green |
| B03 candidate | Isolated committed agent-browser candidate | B02 | required gates |
| B04 install | Browser-preserving exact candidate convergence | B03 | doctors and PID/tab proof |
| B05 acceptance | One terminal Facebook tick plus cache proof | B04 | no retry |
| B06 closeout | Both repos and runtime reconciled | B05 | terminal receipts |

### Checkpoint P0043-C01 | 2026-08-11

Plan version: 1

State transition:

- `terminal_acceptance_failure -> downstream_deadline_owner_identified`.

Progress classification:

- `blocker_reduction`; the prior generic 31.810-second failure now maps to two
  exact fixed agent-browser deadlines below the supplied caller budget.

Validation evidence:

- CodeGraph identifies `MAX_RUNTIME_EVALUATION_TIMEOUT_MS = 25_000` in
  `cli/src/native/browser.rs`, `DEFAULT_COMMAND_TIMEOUT = 30s` in
  `cli/src/native/cdp/client.rs`, and `evaluate_with_timeout` calling the fixed
  `send_command` path;
- current Plan 0097 records that the renderer cap was introduced to fit beneath
  the then-fixed CDP transport. No Graphiti fact contradicted current source;
- installed Last30Days tick and provider receipts bind the live failure to the
  final eval after all earlier browser operations succeeded.

Subagent status and reconciliation:

- `not_spawned`; developer policy requires primary-owned exploration.

Authority classification:

- `inherited_authority`; the active user goal continues after the prior packet
  stop, and this successor changes the owning implementation strategy without
  retrying the failed tick or widening source/profile/data/effect ceilings.

Review disposition summary:

- `blocking=1` fixed renderer/transport deadlines violate the positive global
  job-timeout contract; `needs_evidence=3` red/green, installed convergence,
  live acceptance; `rejected=0`; `nonblocking_backlog=0`.

Graphiti write status:

- discovery completed in `agent_browser_main`; durable write deferred until a
  validated terminal outcome.

Next action:

- create the exact-head isolated worktree and run the one virtual-time
  fake-CDP regression red before changing source.

### Checkpoint P0043-C02 | 2026-08-11

Plan version: 2

State transition:

- `downstream_deadline_owner_identified -> focused_dependency_repair_green`.

Progress classification:

- `blocker_reduction`; both undersized deadlines now derive from the positive
  caller budget at the production evaluation seam.

Validation evidence:

- the original delayed-response regression failed exactly with
  `CDP command timed out: Runtime.evaluate` before the source repair;
- its paused-time real-socket form was nondeterministic under scheduler and
  kernel delivery ordering, so it was removed from the permanent suite after
  preserving the red receipt;
- the deterministic request regression proves a 45,000 ms caller carries a
  44,750 ms Chromium deadline and a 45,000 ms CDP transport deadline;
- the existing fake-CDP integration proves the production path sends the
  renderer deadline, and all 35 browser tests passed twice serially.

Subagent status and reconciliation:

- `not_spawned`; current orchestration policy prohibits delegation.

Authority classification:

- `inherited_authority`; source work remains inside the isolated dependency
  worktree and no installed browser or Facebook effect has occurred.

Review disposition summary:

- `blocking=0` at the focused source seam; `needs_evidence=3` broader source
  gates, exact installed convergence, and the one live acceptance tick;
  `rejected=0`; `nonblocking_backlog=0`.

Graphiti write status:

- deferred until the terminal installed and downstream outcome.

Next action:

- run the agent-browser selected and Rust quality gates, commit and build the
  exact candidate, then perform the one browser-preserving install.

### Checkpoint P0043-C03 | 2026-08-11

Plan version: 3

State transition:

- `focused_dependency_repair_green -> terminal_distinct_scroll_failure`.

Progress classification:

- `blocker_reduction`; the evaluation deadline mismatch is removed from the
  exact installed runtime, and the one bounded tick exposed a different
  selectorless scroll owner.

Validation evidence:

- agent-browser exact commit
  `1c1331efefbb41d7c5ba2384089eb2bfbd358f81` passed selected validation,
  formatting, strict production Clippy, 35 focused browser tests twice, and the
  canonical Rust runner with 1,042 parallel-safe tests plus every serialized
  partition;
- supported installation produced executable SHA-256
  `071b7a6e3e58c87f3fd1decaaeb40d691f666a7d8f311894e4f30558c233bbf2`
  while retaining Facebook browser PID 13177, its exact CDP endpoint, and six
  target IDs;
- the sole tick `tick-c29795374e8948dfacd36e1fd2cd6b1e` completed degraded
  after navigation and evaluation succeeded; exact operation `r958354` then
  failed selectorless scroll after 28.49 seconds with
  `CDP command timed out: Runtime.evaluate`;
- a later tab inventory succeeded, rejecting browser death, profile loss, and
  transport-wide failure. The tick was not retried and no cache-success claim
  was made.

Subagent status and reconciliation:

- `not_spawned`; current orchestration policy prohibits delegation.

Authority classification:

- `inherited_authority`; successor Plan 0044 changes the owning scroll
  implementation while preserving the goal, source, profile, data, schedule,
  and one-attempt effect boundaries.

Review disposition summary:

- `blocking=1` selectorless scroll relies on renderer JavaScript and timed out
  while browser-level CDP stayed healthy; `needs_evidence=3` red/green wheel
  command, installed convergence, and one live acceptance tick; `rejected=2`
  browser/profile death and auth/rate failure; `nonblocking_backlog=0`.

Graphiti write status:

- deferred until the terminal successor outcome.

Next action:

- close P19/Plan 0043 without retry and execute Plan 0044/P20's bounded CDP
  input-wheel dependency repair.
