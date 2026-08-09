# Plan 0030 | Facebook Tick Item-Bound And Worker Receipt Repair

State: OPEN
Roadmap: P13
Plan version: 1
Date: 2026-08-09
Predecessor: Plan 0029 version 4/checkpoint P0029-C04

## Objective

Make governed Facebook manual ticks honor their admitted item bound during
collection and preserve typed isolated-worker failures, then qualify the new
candidate without expanding browser interaction, provider limits, or retry
authority.

## Current State

- Plan 0029's sole 0.3.30 successor tick failed after authenticated navigation,
  extraction, and two scrolls but before a typed provider result was staged;
- the service admitted three items while `_facebook_adapter` left the scraper
  at its default 16-result target, causing its two-scroll loop to continue
  after an initial extraction had already run;
- `AcquisitionWorkerTickAdapter` allowed a typed `WorkerExecutionError` to
  escape into the generic tick integrity handler, losing the worker's safe
  code and retry class;
- service 0.3.31 now constrains Facebook search to the admitted item limit and
  maps typed worker-boundary failures into durable provider failures;
- 0.3.31 is installed ready on schema 16. No 0.3.31 Facebook tick has run.

## Scope

- pass `AcquisitionWorkRequest.item_limit` into Facebook's existing bounded
  maximum-result configuration;
- preserve `WorkerExecutionError.code` and retry-class taxonomy at the tick
  provider bridge, accounting a timeout against the full admitted wall bound;
- add focused contract regressions, run complete validation, build one
  reproducible successor, and install it without browser lifecycle work;
- keep Facebook ticks manual until a later bounded live proof succeeds.

## Non-Goals

- no logout, credential entry, MFA, CAPTCHA, checkpoint, consent, cookie or
  session mutation, or intentional rate-limit/challenge generation;
- no same-build retry, immediate live tick, natural-schedule wait, schedule
  mutation, provider-limit increase, additional scroll depth, fallback
  provider, notification test, cost/model use, or browser/tab closure;
- no claim that offline validation or installation proves the Facebook adapter
  usable.

## Acceptance Criteria

1. A Facebook acquisition request with item limit three invokes the scraper
   with maximum results three, while retaining one opaque-request accounting.
2. A typed isolated-worker timeout returns provider failure class `transient`,
   safe code `worker_timeout`, one attempt, the full admitted wall usage, and
   zero unknown network/item/cost/model usage instead of failing tick integrity.
3. Focused Facebook/worker/runtime tests, full Python and Go suites, compile,
   release/package/plan audits, patch checks, and two reproducible builds pass.
4. Exact 0.3.31 installation preserves schema 16, contract identity, database
   integrity, daily schedule identity/cadence, Facebook readiness, rollback
   releases, zero-cost posture, and retained browser PID 63205.
5. Live qualification remains manual. After at least 60 minutes from the
   0.3.30 attempt and a fresh no-launch readiness/preflight gate, at most one
   0.3.31 Facebook-only tick may run with one attempt and existing limits.
6. Routine attended usability requires that later tick to return Facebook
   success with at least one accepted post or a genuine typed empty result.
   Any other result stops without retry.

## Definition Of Done

- criteria 1-4 have exact repository and installed-runtime evidence;
- criterion 5 is consumed once or records its exact safety/readiness blocker;
- criterion 6 is true before P13 or this plan closes successfully;
- plan, roadmap, runbook, receipt note, installed runtime, and Git history
  agree; one Graphiti write is attempted after the durable commit.

## Execution Bounds

- primary agent owns the serialized critical path; no subagent is used;
- one 0.3.31 implementation/build/install candidate and no live tick in the
  current repair packet;
- any later live proof is a manual tick, not the natural scheduler, and must
  satisfy the 60-minute gap plus the existing no-launch guards;
- hard stop on login/checkpoint/CAPTCHA, organic rate limit, ownership
  ambiguity, nonzero cost/model use, schedule drift, database-integrity
  failure, or privacy-sensitive output.

## Owned Write Surfaces

- `skills/last30days/scripts/lib/service_acquisition_worker.py`;
- `skills/last30days/scripts/lib/service_tick_builtin_adapters.py`;
- focused acquisition-worker and tick-runtime tests;
- service version, runtime manifest, changelog, this plan, predecessor plan,
  `ROADMAP.md`, `RUNBOOK.md`, and one serial evidence note.

### Checkpoint P0030-C01 | 2026-08-09

Plan version: 1

State transition:

- `live_qualification_rejected -> item_bound_successor_installed_gated`.

Progress classification:

- `validated_learning`; the live trace exposed a request-bound mismatch and an
  observability gap. Both are repaired and installed without another browser
  effect, but usability remains unproved.

Validation evidence:

- focused Facebook/acquisition-worker/tick-runtime tests pass;
- the complete Python suite, all Go MCP packages, compileall, release/runtime
  package/plan audits, and patch checks pass;
- two independent 0.3.31 runtime builds are byte-identical at SHA-256
  `298958b365932b0fa811d78f94cb3fa71c1fb305e4ba4820d9a60d8d39a57f34`;
- installed 0.3.31/schema16 is ready with contract SHA-256
  `fe8727fbe0d4e2f6775f49a6fc958369fe4877ba812bae4ef69121b88f12e2f1`
  and runtime-manifest SHA-256
  `15f389ece20f1a5bf9064adfc64e2c604661d1dc587cd91f9672f72bad3e6edf`;
- database quick check is `ok`; releases 0.3.28 through 0.3.31 are retained;
  browser PID 63205 remains ready and no browser/tab was opened or closed by
  the repair/install packet.

Subagent status and reconciliation:

- none; item-bound execution and the provider bridge form one serialized
  contract path.

Authority classification:

- `inherited_authority`; this is the smallest offline successor supported by
  the failed tick evidence and does not consume a new live effect boundary.

Graphiti write status:

- deferred until the validated repository commit exists.

Next action:

- commit and push the 0.3.31 successor, write the compact source-backed
  Graphiti memory, then stop. A future manual proof must recheck the 60-minute
  gap and all no-launch readiness guards.
