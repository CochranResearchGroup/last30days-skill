# Plan 0032 | Facebook 0.3.32 Manual Qualification

State: OPEN
Roadmap: P13
Plan version: 1
Date: 2026-08-09
Predecessor: Plan 0031 version 2/checkpoint P0031-C02

## Objective

Qualify installed service 0.3.32 for routine attended Facebook use with one
source-scoped governed manual tick, or stop with an exact typed blocker.

## Current State

- 0.3.32 is installed ready on schema 16 and offline-validated;
- the scraper now uses one fresh target after a first post-navigation Runtime
  timeout even when active-tab identity matches;
- the prior attempt completed at `2026-08-09T15:19:06.946157Z`, so the earliest
  authorized 60-minute boundary is `2026-08-09T16:19:07Z`;
- Facebook is not routine-qualified. Installed tests and readiness are not live
  acquisition proof.

## Scope

- after the time boundary, re-read service, schedule, database, agent-browser
  install/remote-view, retained browser/profile/tab, challenge, queue, lease,
  and Facebook acquisition readiness without launching a browser;
- create one Facebook-only preflight for the exact intended interval and
  existing limits, verify its frozen scope, then enqueue it exactly once;
- poll only that durable tick receipt and adjudicate against the acceptance
  contract; preserve typed failure evidence without retry.

## Non-Goals

- no logout, credential entry, MFA, CAPTCHA, checkpoint, consent, cookie or
  session mutation, intentional rate-limit/challenge generation, browser/tab
  closure, or direct browser navigation;
- no natural scheduler wait, schedule mutation, provider-limit increase,
  fallback, second enqueue, same-build retry, cost/model use, or content dump;
- no routine-usability claim from readiness, tests, or a degraded receipt.

## Acceptance Criteria

1. Fresh guards pass after `2026-08-09T16:19:07Z` with service 0.3.32/schema16,
   Facebook acquisition ready, the retained canonical browser/profile viable,
   zero active challenge, queue/lease depth zero, SQLite `ok`, and unchanged
   `daily-default` schedule identity/cadence.
2. The matching preflight predicts exactly one Facebook lane/provider/attempt,
   at most 50 requests, 120 wall seconds, three items, and zero cost/model use.
3. Exactly one enqueue occurs and reaches one durable terminal provider result;
   no retry or browser lifecycle action occurs.
4. Routine attended usability requires provider success with at least one
   accepted post or a genuine typed empty result after successful bounded
   extraction. Any auth, checkpoint, CAPTCHA, rate-limit, timeout, integrity,
   quality-only zero-yield, or unknown result stops without retry.

## Definition Of Done

- criteria 1-3 have exact IDs, timestamps, counters, and current-state evidence;
- criterion 4 either closes P13 successfully or records the exact terminal
  blocker while keeping Facebook manual and not routine-qualified;
- plan, roadmap, runbook, runtime, and Git history agree.

## Execution Bounds

- primary agent owns the serialized critical path; no subagent is used;
- one preflight/enqueue pair, one attempt, one Facebook provider, and no retry;
- do not wait for the natural scheduler; execute manually only after the fixed
  safety boundary and fresh no-launch guards;
- hard stop on any failed guard, auth/challenge/rate-limit evidence, ownership
  ambiguity, schedule drift, database failure, nonzero cost/model use, or
  privacy-sensitive output.

## Owned Write Surfaces

- durable tick/provider receipts in the installed service database;
- this plan, `ROADMAP.md`, `RUNBOOK.md`, and one bounded evidence note if the
  terminal result materially changes P13.

### Checkpoint P0032-C01 | 2026-08-09

Plan version: 1

State transition:

- `offline_recovery_installed_gated -> awaiting_manual_safety_boundary`.

Progress classification:

- `outcome_progress`; the disproved fallback is repaired and installed, leaving
  one explicit live criterion rather than an offline implementation blocker.

Validation evidence:

- Plan 0031/C02 binds the exact tests, artifact, installation, database,
  schedule, and retained-browser readbacks.

Subagent status and reconciliation:

- none; the later proof is one serialized effect boundary.

Authority classification:

- `inherited_authority`, subject to the explicit time and fresh-readiness gate.

Graphiti write status:

- predecessor terminal write pending after its durable commit.

Next action:

- at or after `2026-08-09T16:19:07Z`, run fresh no-launch guards and, only if
  they all pass, one matching preflight/enqueue pair without retry.
