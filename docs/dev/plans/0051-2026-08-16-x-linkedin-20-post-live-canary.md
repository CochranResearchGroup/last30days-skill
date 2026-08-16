# Plan 0051 | X And LinkedIn 20-Post Live Canary

State: CLOSED
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

### Checkpoint P0051-C02 | 2026-08-16

Plan version: 2

State transition:

- `twenty_post_canary_ready_for_install -> twenty_post_canary_terminal_runtime_blocked`.

Progress classification:

- `outcome_progress`; the exact one-shot canary terminalized and isolated the
  failure to retained browser/profile routing before either scraper observed a
  post. The 20-item extraction ceilings therefore remain untested.

Validation evidence:

- artifact SHA-256
  `c2af7dad58015edc3626db3bef0d9745fb9fcf0c7db5bd0841a7f76ecfdf9c78`
  installed service 0.3.50/schema 16 ready with runtime-manifest SHA-256
  `5caa3062cb4d05bb66c283a3075c61885eecb3b6a55b6a34ffc443679c393cf6`
  and 0.3.48 retained for rollback;
- state-free preflight was `ready` for exact tick
  `tick-f2163de9362bb74e7da0ce7f525375fe`, config digest
  `sha256:fd297c9a46b65dc9563fdb3497179c3e39788324665d430b50fddf6d098652e5`,
  exactly X and LinkedIn, one attempt/20 items per lane, and aggregate limits
  2 attempts/100 requests/40 items/240 wall seconds/zero cost and model use;
- the exact tick was enqueued once and terminalized `complete_degraded` with
  two attempts, two requests, 145 provider wall seconds, zero observed,
  accepted, or rejected posts, zero cost, and zero model tokens;
- X consumed its sole attempt and failed `auth_required` after 96 seconds;
  LinkedIn consumed its sole attempt and failed
  `operator_ingress_unavailable` after 49 seconds. Both collections and their
  derivative stages are `blocked_human`; the empty snapshot indexed and
  promoted truthfully;
- the pre-effect access plan claimed reusable browser
  `session:last30days-facebook`, but its CDP endpoint disconnected during X.
  Reconciliation then rebound that session to PID 97392 under profile
  `default`, not `last30days-facebook`, with active lease conflicts and blocked
  profile compatibility. Repeated trace events retained that wrong profile;
  PID 97392 later exited unexpectedly. Fresh service status has no live browser
  for the social profile and reports its allocation available;
- the service opened one critical X and one critical LinkedIn
  `reauthentication_required` incident and delivered both configured Slack
  detection notifications successfully;
- `daily-default` retains config digest
  `sha256:209dcf64968394b1327a93d31309a51fd3ebbb5ddebbfe2f5235e1dbc39e619e`,
  prior tick, next boundary `2026-08-17T00:00:00Z`, 11 timer ticks, and 23
  schedule events. Active attempts are zero, SQLite quick check is `ok`, and
  installed service 0.3.50 remains ready;
- the recurring owner-private config remains revision
  `operator-20260816-increase-x-linkedin-volume-v1`, X/LinkedIn ten each,
  Reddit/Facebook disabled. The temporary 20/20 config and audit projection
  were securely removed.

Authority classification:

- `inherited_authority`; installation and the sole live tick were ordinary
  steps inside the operator's explicit 20/20 test request.

Subagent status and reconciliation:

- `not_spawned`; current orchestration policy prohibits delegation.

Graphiti write status:

- pending closeout write; the durable tick, agent-browser trace, service,
  SQLite, this plan, and runbook remain authoritative.

Next action or stop reason:

- stop without retry. The canary did not test scraper yield; restore and prove
  the exact authenticated `last30days-facebook` browser/profile/route identity
  before proposing a distinct future 20/20 canary.
