# Plan 0046 | Facebook Retained Browser Runtime Recovery

State: OPEN
Roadmap: P22
Plan version: 4
Date: 2026-08-11
Predecessor: Plan 0045 version 2/checkpoint P0045-C05

## Objective

After explicit operator authorization for the runtime boundary, perform one
controlled restart of the retained `last30days-facebook` browser on its existing
profile and current installed build, prove Facebook target selection,
evaluation, and selectorless input are responsive before any provider tick,
then consume at most one Facebook-only acceptance tick and require exact
named-profile cache evidence.

## Current State

- service 0.3.47/schema 16 and agent-browser executable SHA-256
  `76b2779ffc65d85f22817c698732e387dffe9cd4f8225f9aaf6b65bba467d3d1`
  remain installed and source-validated;
- the authorized same-profile/current-build restart succeeded and restored
  exactly the three inventoried unrelated targets on browser PID 83786,
  endpoint
  `ws://127.0.0.1:39488/devtools/browser/c574210a-2ee2-4971-8b25-dee038040b41`,
  profile `last30days-facebook`, and the current promoted Chromium build;
- one fresh Facebook target opened and a bounded five-second settle completed,
  but service job `r791343` timed out the first read-only evaluation after
  exactly 10,000 milliseconds. The plan stopped before selectorless input,
  provider preflight, or any tick;
- cleanup job `r186349` closed only the failed Facebook target. X, LinkedIn,
  and preview remain attached; the browser, endpoint, profile, and DevTools are
  live, both databases return `ok`, and `daily-default` is unchanged and ready;
- direct agent-browser inspection of one later disposable Facebook target
  proved the page renderer crashes to Chromium's “Aw, Snap!” surface with
  `Error code: SIGSEGV`. Browser-level target, network, console, and error
  commands remain responsive while renderer-facing title, evaluation,
  accessibility, and page-screenshot commands hang or fail;
- agent-browser still retains that crashed target as lifecycle `ready` and
  records no corresponding crash event or incident. The timeout symptom is
  therefore a renderer crash plus missing target-crash propagation, not a
  Facebook login, challenge, or network-readiness failure;
- Plan 0046 remains open at the failed runtime-smoke gate with its authorized
  packet exhausted. Accepted Facebook evidence and explicit named-profile
  cache proof remain unmet.

## Scope After Human Gate

- preserve the exact retained profile path and inventory the three current
  target URLs before browser shutdown;
- perform at most one supported close/restart of the browser using the current
  installed agent-browser executable and current `stealthcdp_chromium` build;
- restore only the pre-recorded unrelated target URLs, then open one Facebook
  search target on the existing authenticated profile;
- require bounded target selection and evaluation, one selectorless scroll
  smoke with post-input evaluation, and exact PID/endpoint/profile readback
  before permitting provider preflight;
- if every runtime smoke passes, preflight and consume at most one new
  Facebook-only tick, then require accepted durable evidence and MCP
  `cache_only` with explicit `profile_id=last30days-facebook`.

## Non-Goals

- no action before explicit operator authorization; no profile reset, profile
  copy, login, reauthentication, CAPTCHA/checkpoint handling, alternate browser
  build, agent-browser source change, schedule mutation, other source, model,
  paid request, fallback, or retry of any terminal tick;
- no claim that service readiness or a healthy non-Facebook target proves
  Facebook runtime acceptance.

## Acceptance Criteria

1. Explicit operator authority covers the controlled authenticated-browser
   restart and restoration of only the three inventoried unrelated targets.
2. The restarted browser uses the same profile and current build, and exact
   process, endpoint, daemon, manifest, and target inventory reconcile.
3. A fresh Facebook target completes selection, read-only evaluation, one
   selectorless scroll smoke, and post-input evaluation within bounded worker
   deadlines; any timeout stops before provider preflight.
4. One exact preflighted Facebook tick reaches terminal success with accepted
   durable evidence and no retry.
5. MCP `cache_only` with explicit `profile_id=last30days-facebook` returns the
   accepted evidence, and databases, schedule, browser/profile, installed
   runtime, and both repositories reconcile.

## Execution Bounds And Gates

- current state is `runtime_smoke_failed`; the one authorized restart and
  Facebook evaluation smoke are consumed with no provider attempt;
- after authorization: one browser restart, one target restoration pass, one
  Facebook target, one scroll smoke, one service preflight, and one tick;
- stop immediately on auth/challenge/rate evidence, profile or build drift,
  target/input timeout, restoration mismatch, integrity failure, or any effect
  outside this plan;
- no subagents under the current orchestration restriction.

## Work Graph

| Packet | Outcome | Depends on | Gate |
|---|---|---|---|
| R01 authority | Explicit runtime restart authority | C01 | human gate |
| R02 inventory | Exact profile/build/target rollback evidence | R01 | no mutation |
| R03 restart | One same-profile current-build browser restart | R02 | exact convergence |
| R04 smoke | Facebook select/eval/scroll/eval succeeds | R03 | stop on timeout |
| R05 acceptance | One tick plus named cache proof | R04 | no retry |
| R06 closeout | Runtime, receipts, and repositories reconcile | R05 | current evidence |

### Checkpoint P0046-C01 | 2026-08-11

Plan version: 1

State transition:

- `repeated_facebook_target_control_failure -> awaiting_human_gate`.

Progress classification:

- `no_progress`; this checkpoint preserves the exact stop boundary and a
  bounded recovery design but does not advance Facebook acceptance.

Validation evidence:

- Plan 0045/C05 provides the terminal tick, raw CDP, handoff, disposable-target,
  cleanup, and non-Facebook control evidence;
- final live state retains browser PID 13177, the exact endpoint, authenticated
  profile, and three unrelated targets with successful active-target
  evaluation.

Subagent status and reconciliation:

- `not_spawned`; current orchestration policy prohibits delegation.

Authority classification:

- `human_gate`; closing and restarting the authenticated retained browser is a
  materially changed runtime effect after three failures at the same invariant.

Review disposition summary:

- `blocking=1` explicit restart authority; `needs_evidence=3` restarted runtime
  convergence, pre-tick Facebook input smoke, tick/cache acceptance;
  `rejected=2` blind tick and alternate scroll retry;
  `nonblocking_backlog=0`.

Graphiti write status:

- compact blocked-state memory queued as job
  `2f581f90-1395-47a7-b020-e1e67c42648e`; queued status is not persistence
  proof.

Next action:

- wait for explicit authority to execute R02-R05; take no further browser or
  provider action meanwhile.

### Checkpoint P0046-C02 | 2026-08-11

Plan version: 2

State transition:

- `awaiting_human_gate -> restart_ready`.

Progress classification:

- `blocker_reduction`; explicit operator authority now covers one controlled
  restart, and the exact pre-mutation inventory and no-launch browser gate are
  captured before browser shutdown.

Validation evidence:

- operator response “ok go” satisfies R01 for this plan's exact bounded
  same-profile/current-build restart; it does not authorize a profile reset,
  alternate build, login flow, or extra tick;
- current browser PID 13177 uses profile
  `/home/ecochran76/.agent-browser/runtime-profiles/last30days-facebook/user-data`,
  Chromium `150.0.7835.0+stealthcdp.3676a7503929`, endpoint
  `ws://127.0.0.1:38770/devtools/browser/00317084-6844-44c8-b1a3-c63555867ced`,
  and installed agent-browser SHA-256
  `76b2779ffc65d85f22817c698732e387dffe9cd4f8225f9aaf6b65bba467d3d1`;
- the exact unrelated target inventory is preview
  `https://previews.ecochran.dyndns.org/a/3afb4a96364a`, LinkedIn
  `https://www.linkedin.com/company/openai/`, and X
  `https://x.com/search?q=OpenAI%20since%3A2026-08-10%20until%3A2026-08-11&src=typed_query&f=live`;
- access-plan selects the exact durable profile, current build,
  `remote_headed`/`rdp_gateway`/`manual_attached_desktop`, and private display
  posture with no naming, monitor, seeding, or challenge gate;
- browser-capability preflight applies validated binding
  `default-stealthcdp-wsl-native` to the exact promoted executable and reports
  `wouldLaunch=false`, `preflight=true`; both databases return `ok`, schedule
  `daily-default` remains enabled/ready, and Git is clean/pushed.

Subagent status and reconciliation:

- `not_spawned`; current orchestration policy prohibits delegation.

Authority classification:

- `inherited_authority`; the explicit human gate covers R02-R04 and at most one
  later R05 tick only after runtime smoke succeeds.

Review disposition summary:

- `blocking=0` for controlled restart readiness; `needs_evidence=3` restarted
  runtime convergence, Facebook input smoke, tick/cache acceptance;
  `rejected=0`; `nonblocking_backlog=0`.

Graphiti write status:

- no new write before runtime outcome; repository checkpoint is authoritative.

Next action:

- commit this restart-ready checkpoint, then execute exactly one supported
  browser close/restart and restore only the three inventoried target URLs.

### Checkpoint P0046-C03 | 2026-08-11

Plan version: 3

State transition:

- `restart_ready -> runtime_smoke_failed`.

Progress classification:

- `no_progress`; the controlled restart and exact restoration succeeded, but
  Facebook target control still failed before input or provider work and no
  acceptance criterion advanced.

Validation evidence:

- close job `r322825` terminated old PID 13177 and endpoint port 38770;
  remote-view job `r190269` launched one replacement browser on the same
  retained profile/current promoted build as PID 83786 with endpoint
  `ws://127.0.0.1:39488/devtools/browser/c574210a-2ee2-4971-8b25-dee038040b41`
  and route `guacamole:1`;
- Chrome session restoration recovered exactly the inventoried X, LinkedIn,
  and preview URLs. Facebook target job `r59050` opened target
  `D25F9564EFB877A6C4A1E0A2CA66F3EA`, and settle job `r50676` completed;
- read-only evaluation job `r791343` entered `timed_out` with
  `Service job timed out after 10000ms`. The hard stop prevented the planned
  scroll, provider preflight, and tick, so request and provider-attempt counts
  for this plan are zero;
- cleanup job `r186349` closed only that Facebook target. Final inventory is
  exactly X, LinkedIn, and preview; PID 83786, the endpoint, DevTools, and the
  retained profile remain live. Service 0.3.47/schema 16 is ready, current and
  rollback SQLite quick checks return `ok`, and `daily-default` remains
  enabled/ready for `2026-08-12T00:00:00Z`.

Subagent status and reconciliation:

- `not_spawned`; current orchestration policy prohibits delegation.

Authority classification:

- `inherited_authority`; the operator-authorized restart and smoke were used
  exactly once. The fail-closed evaluation boundary forbids completing R04 or
  entering R05 in this plan.

Review disposition summary:

- `blocking=1` Facebook read-only evaluation remains unresponsive after the
  same-profile/current-build restart; `needs_evidence=2` accepted tick and
  named-profile cache proof; `rejected=2` scroll after failed eval and provider
  tick without smoke; `nonblocking_backlog=0`.

Graphiti write status:

- after pushed outcome commit `a968de4`, one source-backed memory write was
  queued as job `80d3d5cf-e848-42cf-870c-02a692f3e444` in
  `last30days_skill_main`; queued status is not persistence proof, so the
  repository and retained service receipts remain authoritative.

Next action or stop reason:

- stop this packet and keep the plan open at its explicit failed-smoke gate. Do
  not repeat the restart, evaluation, scroll, or tick under its exhausted
  bounds; a materially different, explicitly bounded plan revision or
  successor packet must own any continuation.

### Checkpoint P0046-C04 | 2026-08-11

Plan version: 4

State transition:

- `runtime_smoke_failed -> renderer_crash_diagnosed`.

Progress classification:

- `blocker_reduction`; direct visual and CDP-domain evidence narrows the
  generic target timeout to a Facebook renderer `SIGSEGV` and a separate
  agent-browser crash-observability gap.

Validation evidence:

- the operator explicitly requested direct inspection through agent-browser;
  access-plan selected the retained `last30days-facebook` profile/current
  build and prohibited a duplicate process, so the live browser was reused;
- one disposable Facebook target
  `9E9366B2790499B37A715DD70EF889DC` opened and settled. Agent-browser page
  screenshot failed immediately with `CDP error (Page.captureScreenshot):
  Internal error`; `get title` and accessibility snapshot timed out at bounded
  10-second job deadlines, matching the prior evaluation timeout;
- agent-browser Console and Errors returned successfully with empty collections,
  while Network returned current successful Facebook CSS, JavaScript, image,
  XHR, and post-image traffic. This excludes absent connectivity and shows the
  page reached authenticated search-content loading before failure;
- because agent-browser's page-screenshot path was itself broken, one ephemeral
  capture of its confirmed remote display `:10` showed Chromium's “Aw, Snap!”
  page and exact `Error code: SIGSEGV`. The image was intentionally kept out of
  Git because it came from an authenticated browser surface;
- retained service state incorrectly reported the crashed tab lifecycle as
  `ready`, with no matching event or incident. Closing tab index 3 succeeded,
  and final inventory again contains exactly the unrelated X, LinkedIn, and
  preview tabs on live PID 83786.

Subagent status and reconciliation:

- `not_spawned`; current orchestration policy prohibits delegation.

Authority classification:

- `inherited_authority`; the user's direct inspection request authorized one
  read-only disposable-tab diagnostic and cleanup, not reload, login, browser
  substitution, source repair, scroll, provider work, or tick execution.

Review disposition summary:

- `blocking=2` Facebook renderer `SIGSEGV` and missing crash propagation;
  `needs_evidence=2` accepted tick and named-profile cache proof; `rejected=3`
  login/challenge explanation, network-readiness explanation, and another tick;
  `nonblocking_backlog=0`.

Graphiti write status:

- after pushed diagnosis commit `153009a`, one source-backed memory write was
  queued as job `2fd1bff1-0ab5-49e6-a8f6-da9d116d40a8` in
  `last30days_skill_main`; queued status is not persistence proof, so live
  receipts and the repository checkpoint remain authoritative.

Next action or stop reason:

- stop at diagnosis. Before any further Facebook tick, a bounded agent-browser
  repair must surface renderer target crashes immediately and the promoted
  Chromium/Facebook `SIGSEGV` must be reproduced and resolved without reusing
  this exhausted browser/tick packet.

## Definition Of Done

- criteria 1-5 have current human-gate, live-runtime, receipt, cache, and
  reconciliation evidence. A source test, restart, or successful scroll alone
  is not completion.
