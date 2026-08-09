# Plan 0033 | Facebook Target Recovery And Manual Qualification

State: OPEN
Roadmap: P13
Plan version: 3
Date: 2026-08-09
Predecessor: Plan 0032 version 3/checkpoint P0032-C04

## Objective

Repair the rendered-but-CDP-unresponsive Facebook target failure, install the
bounded successor, and qualify it for routine attended use with one
source-scoped governed manual tick, or stop with an exact typed blocker.

## Current State

- 0.3.34/schema16 is installed ready with parent-owned hard-timeout tab
  containment and copied Skills synchronized;
- the retained browser PID 63205 is ready with one Facebook, one X, one
  LinkedIn, and one preview tab; active challenge and lease-wait counts are
  zero;
- Plan 0032's sole provider attempt ended at
  `2026-08-09T18:19:59.964036Z` as transient `worker_timeout` with zero
  observed/accepted/rejected candidates and no auth, CAPTCHA, checkpoint,
  rate-limit, or quality rejection;
- Facebook is acquisition-ready but not routine-qualified. The earliest
  successor boundary is `2026-08-09T19:20:00Z`.
- direct read-only diagnosis after that failed tick proved that the retained
  Facebook search page was visibly rendered and had the exact expected URL,
  while trivial `Runtime.evaluate`, the page-state script, and screenshot all
  timed out on that target; a LinkedIn control evaluation succeeded in the
  same browser, isolating the fault to the Facebook target rather than the
  queue, browser, or extraction script.

## Scope

- add a red regression for a rendered Facebook target whose Runtime channel is
  unresponsive;
- replace that exact target once, close the predecessor immediately, and emit
  a typed stage-preserving failure before the parent worker wall if the
  replacement is also unresponsive;
- validate, release, and install the bounded successor without changing
  schedule, provider limits, schema, cost, model, or browser/profile ownership;
- after the fixed boundary, re-read installed service, schedule, database,
  agent-browser install/remote-view, retained browser/profile/tab, challenge,
  queue, lease-wait, and Facebook acquisition readiness;
- create one Facebook-only preflight for the existing interval and limits,
  verify its frozen scope, enqueue exactly once, and poll only its durable
  receipt;
- adjudicate against the accepted-content contract and preserve any typed
  failure without retry.

## Non-Goals

- no browser close, logout, login entry, MFA, CAPTCHA/checkpoint interaction,
  cookie/session mutation, intentional challenge or rate-limit generation;
- no natural scheduler wait, schedule mutation, provider-limit increase,
  fallback, second enqueue, same-build retry, cost/model use, or content dump;
- no readiness claim from installation, tests, or a degraded receipt.

## Acceptance Criteria

1. A regression proves that a rendered-but-Runtime-unresponsive Facebook
   target is replaced exactly once, its predecessor is closed without tab
   growth, and a repeated failure returns `facebook_target_unresponsive` with
   the failing stage before the 120-second parent worker wall.
2. Fresh guards pass after `2026-08-09T19:20:00Z` with the successor/schema16,
   SQLite `ok`, unchanged `daily-default`, Facebook acquisition ready, browser
   PID 63205 viable, exactly four retained live tabs with one Facebook, zero
   active challenge, and zero waiting profile-lease jobs.
3. The matching preflight predicts one Facebook lane/provider/attempt, at most
   50 requests, 120 wall seconds, three items, and zero cost/model use.
4. Exactly one enqueue reaches one terminal provider result; no retry occurs,
   and same-site cleanup preserves one Facebook tab even after hard timeout.
5. Routine usability requires provider success with at least one accepted post
   or a genuine typed empty result after successful bounded extraction. Any
   auth, challenge, rate-limit, timeout, integrity, quality-only zero-yield, or
   unknown result stops without retry.

## Definition Of Done

- criteria 1-4 have exact IDs, timestamps, counters, and current readbacks;
- criterion 5 either closes P13 successfully or records the terminal blocker
  while Facebook remains manual and not routine-qualified;
- plan, roadmap, runbook, runtime, and Git history agree.

## Execution Bounds

- primary agent owns the serialized critical path; no subagent is used;
- one effect-bearing preflight/enqueue pair, one attempt, one Facebook
  provider, and no retry; a deterministic collision with an already-terminal
  tick may be rejected without enqueue and replaced by one fresh closed
  interval preflight;
- do not wait for the natural scheduler; execute manually only after the fixed
  safety boundary and fresh guards;
- hard stop on failed guard, auth/challenge/rate-limit evidence, ownership
  ambiguity, schedule/database drift, nonzero cost/model use, or private output.

## Owned Write Surfaces

- one durable tick/provider receipt in the installed service database;
- this plan, `ROADMAP.md`, `RUNBOOK.md`, and one bounded receipt note.

### Checkpoint P0033-C01 | 2026-08-09

Plan version: 1

State transition:

- `timeout_cleanup_installed_gated -> awaiting_manual_safety_boundary`.

Progress classification:

- `blocker_reduction`; the next proof can test content acquisition without
  reintroducing the proven hard-timeout tab leak.

Validation evidence:

- Plan 0032/C04 binds exact implementation, validation, artifact,
  installation, and retained-browser evidence.

Subagent status and reconciliation:

- none; the later proof is one serialized effect boundary.

Authority classification:

- `inherited_authority`, subject to the fixed time and fresh-readiness gates.

Graphiti write status:

- predecessor terminal write job `a0434981-fa1f-451d-838e-39f908205545`
  timed out once during node resolution after 90 seconds and was not retried.

Next action:

- at or after `2026-08-09T19:20:00Z`, run fresh no-launch guards and, only if
  they pass, one matching preflight/enqueue pair without retry.

### Checkpoint P0033-C02 | 2026-08-09

Plan version: 2

State transition:

- `awaiting_manual_safety_boundary -> target_recovery_repair`.

Progress classification:

- `blocker_reduction`; the failed proof is no longer treated as slow page
  rendering because same-browser controls isolate a wedged Facebook target
  execution channel.

Validation evidence:

- the exact Facebook URL/title remained available through tab inventory;
- Facebook page-state evaluation took 25,035 ms and timed out, a trivial
  evaluation also timed out, and screenshot failed with a CDP internal error;
- a LinkedIn evaluation in browser PID 63205 completed in about 650 ms.

Subagent status and reconciliation:

- none; diagnosis and repair remain on the serialized critical path.

Authority classification:

- `inherited_authority`; repair, install, and exactly one later manual proof
  remain within the unchanged goal and safety bounds.

Next action:

- land a red regression, implement exact-target replacement plus bounded typed
  failure receipts, validate and install the successor, then run fresh guards
  and at most one Facebook-only proof without retry.

Collision guard:

- the first post-install preflight reused the predecessor interval and
  deterministically resolved to already-terminal tick
  `tick-c9a6b9e9e30d22fbe01328ab1e7ee6d8`; it was not enqueued and consumed no
  provider attempt. Use one latest fully closed 24-hour interval preflight for
  the sole effect-bearing pair.

### Checkpoint P0033-C03 | 2026-08-09

Plan version: 3

State transition:

- `target_recovery_repair -> retained_owner_acquisition_repair`.

Progress classification:

- `blocker_reduction`; the sole 0.3.35 proof ended before Facebook page work
  and exposed a distinct retained-owner selection defect.

Live receipt:

- tick `tick-b5aa065db0a567dd5e29e3851d1b1858`, execution attempt
  `tick-attempt-00d9c50d77c3233d8ca086e2547fe4e4`, and provider attempt
  `provider-attempt-1a06176af35b4e729bd95914bcaacc16` each ran once;
- the provider failed transiently as `agent_browser_error` after six wall
  seconds and one network request with zero observed/accepted/rejected items,
  zero cost/model tokens, no quality rejections, no page signals, and no
  operator handoff;
- browser operations were two successful service reads followed by one failed
  `remote-view` operation. No retry or fallback occurred.

Root cause and repair:

- the exact retained owner was rejected because its optional CDP screencast
  viewer was unavailable even though the ready browser exposed a live local
  `cdpEndpoint`; acquisition therefore attempted an unnecessary remote-view
  launch and never reached Facebook;
- a red regression now binds ready `cdpEndpoint` evidence to the existing
  exact-profile-alias, reciprocal-owner, and target-presence safeguards.

Subagent status and reconciliation:

- none; the primary preserved the serialized provider boundary and performed
  the source-backed repair.

Authority classification:

- `inherited_authority` for the offline repair, validation, release, and
  install; the consumed provider attempt does not authorize another proof.

Graphiti write status:

- deferred until the repaired installed runtime and durable Git closeout are
  exact; no live-result retry is permitted.

Next action:

- installed 0.3.37 carries the retained-owner repair plus consistent typed
  replacement-navigation failure. Do not run a second Facebook proof in this
  checkpoint; the next proof remains manual and separately guarded.
