# Plan 0051 | X And LinkedIn 20-Post Live Canary

State: OPEN
Roadmap: P08
Plan version: 1
Date: 2026-08-16

## Objective

Install the validated X/LinkedIn scraper candidate, then run exactly one
receipt-only tick with an accepted-item ceiling of 20 for X and 20 for
LinkedIn and report truthful observed, accepted, rejected, timing, and failure
evidence.

## Current State

- pushed source commit `97bfe41` packages service 0.3.50 with LinkedIn's
  activity-URN recovery plus X quoted-post/media-context extraction and
  content-free rejected-candidate receipts;
- installed service 0.3.48/schema 16 is ready, SQLite quick check is `ok`, and
  the recurring owner-private configuration still enables only YouTube, X,
  and LinkedIn with Reddit/Facebook disabled;
- the durable recurring X and LinkedIn ceilings remain ten each. This canary
  will use a separate owner-private temporary config and manual schedule
  identity, leaving `daily-default` and its bound digest unchanged;
- no provider attempt is authorized beyond the one X lane and one LinkedIn
  lane in this plan.

## Scope

- build and transactionally install exact service 0.3.50 with rollback
  retention and post-install readiness proof;
- derive one owner-private temporary config that changes only its revision,
  X and LinkedIn item ceilings from ten to 20, and aggregate item ceiling from
  23 to 43;
- preflight exactly X and LinkedIn under schedule identity
  `plan-0051-x-linkedin-20-canary` over the completed Aug 15-16 UTC interval;
- permit one attempt, 50 requests, 120 wall seconds, zero cost, and zero model
  tokens per lane; stop at the first terminal receipt;
- read back provider, rejection, derivative, database, installed-service, and
  recurring-schedule evidence, then securely remove the temporary config.

## Non-Goals

- do not persist 20-item ceilings into `daily-default`, re-enable Reddit or
  Facebook, run YouTube, change topic/depth/profile/browser routing, retry a
  failed lane, send an ad hoc notification, or promise 20 accepted posts;
- do not repair any new source or derivative failure discovered by this
  canary.

## Acceptance Criteria

1. Service 0.3.50 installs ready with schema 16 and a retained rollback
   release.
2. State-free preflight binds exactly X and LinkedIn, one attempt and 20 items
   per lane, aggregate limits of two attempts, 100 requests, 40 items, 240 wall
   seconds, zero cost, and zero model tokens.
3. Enqueue consumes that exact prospective tick once and reaches one terminal
   receipt without retry or fallback.
4. Source-local observed, accepted, rejected, rejection-receipt, timing, and
   failure evidence is reported without treating ceilings as guaranteed yield.
5. `daily-default`, its config digest and next boundary remain unchanged;
   SQLite and installed service remain healthy and the temporary config is
   removed.

## Definition Of Done

- exact 0.3.50 installed evidence and one terminal 20/20 two-lane receipt are
  reconciled into this plan, P08, and the runbook; no second provider attempt
  or recurring-config mutation occurs.

### Checkpoint P0051-C01 | 2026-08-16

Plan version: 1

State transition:

- `live_repair_accepted -> twenty_post_canary_ready_for_install`.

Progress classification:

- `outcome_progress`; exact source, browser, runtime, and one-tick bounds are
  established before the installed-runtime mutation.

Validation evidence:

- branch `main` is clean and exactly synchronized to `origin/main` at pushed
  commit `97bfe41`; source candidate 0.3.50 passed the full Python suite, X and
  release/package tests, Go tests, plan-authority audit, and diff check;
- installed service 0.3.48/schema 16 reports ready and SQLite quick check is
  `ok`; the private recurring config remains mode 0600 with Reddit/Facebook
  disabled and X/LinkedIn at ten items;
- agent-browser access plans select authenticated profile
  `last30days-facebook`, recommend reusing retained browser
  `session:last30days-facebook`, require no manual action or seeding, and
  report compatible/passed Chromium capability evidence for both targets;
- policy selector, active planning audit, and goal-only audit pass.

Authority classification:

- `inherited_authority`; the operator explicitly requested trying 20 X posts
  and 20 LinkedIn posts in one tick.

Subagent status:

- `not_spawned`; current orchestration policy prohibits delegation.

Next action or stop reason:

- build and install exact service 0.3.50, derive and validate the temporary
  20/20 config, preflight exactly one two-lane tick, enqueue it once, and stop
  at its first terminal receipt.
