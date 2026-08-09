# Plan 0033 | Facebook 0.3.34 Manual Qualification

State: OPEN
Roadmap: P13
Plan version: 1
Date: 2026-08-09
Predecessor: Plan 0032 version 3/checkpoint P0032-C04

## Objective

Qualify installed service 0.3.34 for routine attended Facebook use with one
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

## Scope

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

1. Fresh guards pass after `2026-08-09T19:20:00Z` with 0.3.34/schema16,
   SQLite `ok`, unchanged `daily-default`, Facebook acquisition ready, browser
   PID 63205 viable, exactly four retained live tabs with one Facebook, zero
   active challenge, and zero waiting profile-lease jobs.
2. The matching preflight predicts one Facebook lane/provider/attempt, at most
   50 requests, 120 wall seconds, three items, and zero cost/model use.
3. Exactly one enqueue reaches one terminal provider result; no retry occurs,
   and same-site cleanup preserves one Facebook tab even after hard timeout.
4. Routine usability requires provider success with at least one accepted post
   or a genuine typed empty result after successful bounded extraction. Any
   auth, challenge, rate-limit, timeout, integrity, quality-only zero-yield, or
   unknown result stops without retry.

## Definition Of Done

- criteria 1-3 have exact IDs, timestamps, counters, and current readbacks;
- criterion 4 either closes P13 successfully or records the terminal blocker
  while Facebook remains manual and not routine-qualified;
- plan, roadmap, runbook, runtime, and Git history agree.

## Execution Bounds

- primary agent owns the serialized critical path; no subagent is used;
- one preflight/enqueue pair, one attempt, one Facebook provider, and no retry;
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
