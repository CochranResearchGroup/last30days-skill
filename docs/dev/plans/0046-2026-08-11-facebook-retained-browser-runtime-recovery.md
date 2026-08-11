# Plan 0046 | Facebook Retained Browser Runtime Recovery

State: OPEN
Roadmap: P22
Plan version: 1
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
- browser PID 13177 and endpoint
  `ws://127.0.0.1:38770/devtools/browser/00317084-6844-44c8-b1a3-c63555867ced`
  remain live on profile `last30days-facebook`; the two failed Facebook tabs
  were closed and three unrelated targets remain attached;
- a final browser-preserving daemon handoff returned a successful evaluation
  from the active preview target, while both the failed tick target and a fresh
  same-profile Facebook target timed out on target control;
- the same Facebook CDP input/target-control invariant has failed the Plan 0110
  live scroll proof and the sole Plan 0044 and Plan 0045 ticks. The configured
  repeated-no-progress bound therefore requires a human gate before changing
  browser runtime state;
- accepted Facebook evidence and explicit named-profile cache proof remain
  unmet. No tick, restart, replacement build, or provider effect is authorized
  by opening this plan.

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

- current state is `awaiting_human_gate`; plan creation is documentation only;
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

- pending the durable blocked-state checkpoint.

Next action:

- wait for explicit authority to execute R02-R05; take no further browser or
  provider action meanwhile.

## Definition Of Done

- criteria 1-5 have current human-gate, live-runtime, receipt, cache, and
  reconciliation evidence. A source test, restart, or successful scroll alone
  is not completion.
