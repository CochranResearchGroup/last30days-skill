# Plan 0027 | Facebook Governed Tick Navigation Recovery

State: OPEN
Roadmap: P11
Plan version: 1
Date: 2026-08-08
Predecessor: Plan 0026 version 12/checkpoint P0026-C12

## Objective

Make the installed Facebook adapter complete through the normal governed manual
tick path when authentication is explicit but the selected retained target
freezes during query navigation.

## Current State

- service 0.3.20/schema16 is installed ready and correctly avoids false login,
  checkpoint, and CAPTCHA notices;
- explicit manual tick `tick-848f61b8a22d7e603c7e473c16ba5fdf`
  completed `complete_degraded` with seven items, five bounded attempts, 14
  requests, 66 wall seconds, zero cost, zero model tokens, a promoted snapshot,
  zero incidents, and zero notifications;
- Facebook auth inspection skipped two frozen retained targets, selected one
  responsive target, and proved authentication in 500 ms;
- query navigation job `r198316` then failed after 25.787 seconds with the
  page-operation timeout. The queue released normally and later tab, eval, and
  LinkedIn navigation jobs succeeded;
- retained browser PID 96078 and all eight tabs remain live. No browser or tab
  was opened or closed by the manual tick.

## Scope

- add a bounded navigation/readback recovery path for a target that freezes
  after explicit authentication;
- preserve typed auth/checkpoint handling, the retained exact profile, bounded
  command deadlines, zero-cost posture, and durable browser-operation evidence;
- prove the successor with one explicit manual governed tick rather than
  waiting for a natural schedule boundary.

## Non-Goals

- no automated login, MFA, CAPTCHA, checkpoint, or credential handling;
- no blind retry without a code or runtime-state change;
- no retained-tab cleanup, browser restart, duplicate profile, schedule change,
  provider expansion, paid/model use, or notification test message;
- no formal release, tag, upstream pull request, or unrelated repository
  cleanup.

## Acceptance Criteria

1. A navigation timeout after explicit authentication cannot become an auth or
   checkpoint incident.
2. Recovery is bounded, preserves the retained browser/profile, and either
   reaches verified query-page readback or returns the exact typed navigation
   blocker.
3. The following agent-browser command is not delayed by abandoned navigation
   work.
4. Focused and complete validation, immutable service build/install, patch and
   plan-authority checks pass.
5. One distinct manual governed tick completes with truthful Facebook lane
   evidence, zero cost/model use, no false human incident, and no retained-tab
   closure.

## Execution Bounds

- one red navigation-recovery contract and one implementation pass;
- at most one focused rework after deterministic validation;
- one immutable service successor install;
- one distinct manual tick only after preflight and installed readback;
- hard stop on a real login/checkpoint, browser ownership drift, nonzero cost,
  notification misroute, or repeated same-signature navigation failure.

## Owned Write Surfaces

- `skills/last30days/scripts/lib/facebook.py` and focused tests;
- exact service version/runtime manifest and changelog if implementation lands;
- `ROADMAP.md`, `RUNBOOK.md`, and this plan.

### Checkpoint P0027-C01 | 2026-08-08

Plan version: 1

State transition:

- `plan0026_direct_adapter_proof -> governed_manual_tick_navigation_blocker`.

Progress classification:

- `validated_learning`; the explicit manual gate rejected a premature claim
  that direct adapter proof alone established governed-tick reliability.

Validation evidence:

- preflight predicted the exact manual tick, five provider lanes, aggregate
  zero-cost limits, and trigger `manual` before state creation;
- the durable tick and provider result localize Facebook to an authenticated
  retained target followed by one failed `open` operation, while the queue and
  remaining browser-backed lane stayed healthy;
- provider outcome is `agent_browser_error/transient`, not auth, checkpoint, or
  CAPTCHA, and no incident or notification was created.

Subagent status and reconciliation:

- none; the primary owns the tightly coupled adapter/runtime path.

Authority classification:

- `inherited_authority`; the operator explicitly required manual proof now and
  forbade waiting for natural time.

Graphiti write status:

- not written; the repository plan, roadmap, runbook, durable tick, and browser
  job records are the current source-backed authorities for this bounded
  blocker.

Next action:

- commit and push the completed false-auth and timeout repair with this exact
  blocker preserved; derive the red navigation-recovery contract before any
  additional Facebook or all-source manual tick.

## Definition Of Done

- all acceptance criteria have current commit-bound and installed-runtime
  evidence;
- P11, this plan, and the latest runbook agree;
- exact remote commit and installed artifact identities are recorded;
- no unrelated worktree artifacts are included.
