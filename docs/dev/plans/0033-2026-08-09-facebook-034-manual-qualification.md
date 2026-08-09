# Plan 0033 | Facebook Target Recovery And Manual Qualification

State: CLOSED
Roadmap: P13
Plan version: 5
Date: 2026-08-09
Predecessor: Plan 0032 version 3/checkpoint P0032-C04

## Objective

Repair the rendered-but-CDP-unresponsive Facebook target failure, install the
bounded successor, and qualify it for routine attended use with one
source-scoped governed manual tick, or stop with an exact typed blocker.

## Current State

- 0.3.37/schema16 is installed ready with target recovery, retained-owner
  acquisition, parent-owned hard-timeout tab containment, and copied Skills
  synchronized;
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
- the operator-authorized C04 window consumed three distinct manual ticks.
  All three reached Facebook through the retained owner and terminated with
  zero candidates: two as `agent_browser_timeout` and one as
  `facebook_target_unresponsive`;
- each result used one request, 83-84 wall seconds, zero items/cost/model
  tokens, and carried no auth, CAPTCHA, checkpoint, rate-limit, page-signal,
  or quality-rejection evidence;
- final cleanup preserves browser PID 63205 ready with four live tabs and one
  Facebook home target. Facebook remains manual and not routine-qualified;
  no fourth tick is authorized by this plan.

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
- create up to three Facebook-only preflights for distinct fully closed
  intervals with the existing limits, verify each frozen scope, enqueue each
  at most once, and poll only its durable receipt;
- adjudicate each result against the accepted-content contract, stop early on
  accepted content or genuine typed empty extraction, and preserve every typed
  failure without same-tick retry.

## Non-Goals

- no browser close, logout, login entry, MFA, CAPTCHA/checkpoint interaction,
  cookie/session mutation, intentional challenge or rate-limit generation;
- no natural scheduler wait, schedule mutation, provider-limit increase,
  fallback, more than three new enqueues, same-tick retry, cost/model use, or
  content dump;
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
4. Up to three new enqueues on distinct fully closed intervals each reach one
   terminal provider result; no tick is enqueued twice, and same-site cleanup
   preserves one Facebook tab even after hard timeout.
5. Routine usability requires provider success with at least one accepted post
   or a genuine typed empty result after successful bounded extraction. Any
   auth, challenge, rate-limit, timeout, integrity, quality-only zero-yield, or
   unknown result is preserved exactly. Accepted content, a genuine typed empty
   extraction, auth/challenge/rate-limit evidence, or safety/integrity drift
   stops the attempt loop immediately.

## Definition Of Done

- criteria 1-4 have exact IDs, timestamps, counters, and current readbacks;
- criterion 5 either closes P13 successfully or records the terminal blocker
  while Facebook remains manual and not routine-qualified;
- plan, roadmap, runbook, runtime, and Git history agree.

## Execution Bounds

- primary agent owns the serialized critical path; no subagent is used;
- at most three new effect-bearing preflight/enqueue pairs, one attempt and one
  Facebook provider per distinct tick, and no same-tick retry; a deterministic
  collision with an already-terminal tick may be rejected without enqueue and
  replaced by another fresh closed interval preflight within the three-attempt
  ceiling;
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

- provider readiness returned `degraded` after a 10-second Codex app-server
  `TimeoutError`; no memory job was queued. The compact Plan 0033/C03 repair,
  no-retry proof, and installed 0.3.37 state remain pending for the next
  healthy non-trivial closeout.

Next action:

- installed 0.3.37 carries the retained-owner repair plus consistent typed
  replacement-navigation failure. Do not run a second Facebook proof in this
  checkpoint; the next proof remains manual and separately guarded.

### Checkpoint P0033-C04 | 2026-08-09

Plan version: 4

State transition:

- `retained_owner_acquisition_repair -> bounded_manual_qualification`.

Progress classification:

- `outcome_progress`; the operator explicitly authorized resuming immediately
  with up to three new attempts, superseding C03's checkpoint-local no-second-
  proof boundary without changing the source, limits, tenant, or safety gates.

Current evidence:

- main and `origin/main` both resolve to
  `da542e0075ef78f452127fb065d5996f5de9d241` before the new effect boundary;
- the prior `tick-b5aa065db0a567dd5e29e3851d1b1858` remains historical and
  does not consume the newly authorized three-attempt window.

Subagent status and reconciliation:

- none; the primary owns the serialized preflight, enqueue, adjudication, and
  cleanup checks.

Authority classification:

- `human_gate`; direct operator instruction authorizes at most three new
  Facebook-only manual attempts now, without waiting for natural time.

Controller and exit condition:

- the primary runs distinct fully closed intervals serially and stops at the
  first accepted-content or genuine typed-empty result, any auth/CAPTCHA/
  checkpoint/rate-limit evidence, any safety/integrity drift, or after three
  terminal attempts.

Next action:

- run fresh installed-service, database, schedule, browser, tab, challenge,
  queue, lease, and acquisition guards; if all pass, execute attempt one.

### Checkpoint P0033-C05 | 2026-08-09

Plan version: 5

State transition:

- `bounded_manual_qualification -> terminal_typed_blocker`;
- plan state `OPEN -> CLOSED`; P13 remains open through successor Plan 0034.

Progress classification:

- `no_progress` on content qualification but `outcome_progress` on diagnosis:
  the three-attempt bound proves that 0.3.37 reaches and reuses the retained
  browser correctly, while Facebook targets still lose the page execution or
  navigation channel before extraction can observe a candidate.

Live receipts:

- attempt 1: tick `tick-6533102fc41c30e1227efceb3c1352d3`, execution
  `tick-attempt-6340cc7d9750a9dfc29869584e4ebf72`, provider
  `provider-attempt-94143dedb9602c74c4af1eb14082a7be`, result digest
  `sha256:03bc373e812b927f24dc0b479da7b113212e45d94d609383ed5d2dbdc8581280`,
  typed `agent_browser_timeout`, 83 wall seconds;
- attempt 2: tick `tick-ee4ebcb380a4afab75ab0860e14f2a32`, execution
  `tick-attempt-eb36e207ac68962474976d421cf3b2a4`, provider
  `provider-attempt-89bc548a46c6bac53f81fdb5fca793e1`, result digest
  `sha256:a16f2140b5612a75c925e3778cebe0d4b60c307e9a9a8efc14fd8bcd3a1c3468`,
  typed `facebook_target_unresponsive`, 84 wall seconds;
- attempt 3: tick `tick-55cdd0111fa36439694ae4c661bd7cfc`, execution
  `tick-attempt-868995e4837cbaa22a49258307ec92dc`, provider
  `provider-attempt-0ae6046304b7826f18e711e9627ea314`, result digest
  `sha256:7b79a954c20fa4add9e314e094c580faaae958375c5e1666e919ead3f6734e65`,
  typed `agent_browser_timeout`, 83 wall seconds.

Shared outcome evidence:

- every result consumed one attempt and one network request, with outcome
  counts `0/0/0/0`, zero items/cost/model tokens, empty rejections and page
  signals, and no operator handoff;
- attempt 2 successfully navigated the expected OpenAI search URL before its
  evaluation timed out; attempts 1 and 3 recovered through a fresh home target
  and then timed out on a later open. This is page-execution/navigation failure,
  not retained-owner selection or quality-gate rejection;
- final installed service 0.3.37/schema16 and `daily-default` are ready,
  both SQLite quick checks are `ok`, browser PID 63205 is ready with one
  Facebook plus X, LinkedIn, and preview tabs, and active challenge count is
  zero.

Subagent status and reconciliation:

- none; the primary executed and adjudicated all three attempts serially.

Authority classification:

- `human_gate`; the operator-authorized three-attempt ceiling is exhausted.
  No fourth effect-bearing tick may be inferred from this checkpoint.

Graphiti write status:

- provider readiness passed and one compact episode was queued as job
  `9fb0552f-5cb3-42d4-95f5-fc26a44c3ae5` in
  `last30days_skill_main`; no duplicate write was queued.

Next action or stop reason:

- stop live qualification. Plan 0034 may build a deterministic offline
  regression and repair for repeated post-navigation Facebook target loss;
  any later live proof requires a new explicit attempt ceiling.
