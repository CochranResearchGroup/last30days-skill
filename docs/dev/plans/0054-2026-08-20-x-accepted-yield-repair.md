# Plan 0054 | X Accepted-Yield Repair

State: CLOSED
Roadmap: P08
Plan version: 5
Date: 2026-08-20

## Objective

Make the governed X browser lane pursue the service-requested accepted-item
ceiling within a bounded scroll budget, without weakening the existing post
quality gate.

## Current State

- installed service 0.3.53/schema 16 is ready and compatible with MCP 4.0.3,
  with 0.3.52 retained as rollback;
- X-only tick `tick-0fb90267ebbec47e0fe769aa3b485bdc`
  observed 13 card captures, accepted five, and rejected eight;
- item-level retained-tab inspection accounts for the eight rejections as five
  genuinely short replies, two off-topic results, and one repeated canonical
  status across extraction snapshots;
- the service now propagates `request.item_limit` into `search_x_browser`,
  clamps explicit ceilings to 100, derives a proportional bounded scroll
  budget, and stops when accepted unique yield meets the requested ceiling;
- the sole guarded canary is terminal `complete_degraded`: the broker first
  launched exact profile `last30days-facebook`, then rebound that logical
  session to the unrelated default-profile browser before auth classification;
- the resulting X login screenshot proves only that the default profile was
  logged out. It does not prove the named social profile lost authentication,
  and the 20-item accepted-yield loop was not reached.
- the separately bounded agent-browser owner-transfer repair installed
  generation `0.28.0-0ed74f1decdb-36f3d74f834d` and preserved one exact
  social-profile browser owner;
- terminal successor tick `tick-9ff2c6e630de77dbe199eca6e52d0847`
  reached X extraction without an auth incident, observed 33 captures, found
  20 unique linked posts, accepted 13, and exhausted the bounded capture loop;
  its 20 rejections were 13 repeated accepted-status captures, three linked
  short posts, and four linked off-topic posts, with zero promoted or
  missing-permalink failures.

## Scope

- add a minimized red regression for a first X capture filled with legitimate
  quality rejections followed by acceptable posts after scrolling;
- propagate the service acquisition `item_limit` into the X browser adapter;
- derive a bounded X scroll budget from an explicit requested item ceiling;
- stop scrolling when the requested accepted unique yield is met or the
  bounded scroll budget is exhausted, not merely when raw cards reach the
  ceiling;
- preserve bounded, content-free rejection diagnostics and existing canonical
  permalink, date, promotion, relevance, and text-quality gates;
- update affected runtime/configuration/release authorities, validate, build,
  install one successor, and run at most one X-only acceptance canary without
  changing the recurring schedule.

## Non-Goals

- do not accept short replies, thread-only mentions, unrelated quote posts,
  promoted posts, missing permalinks, or out-of-range posts;
- do not change LinkedIn, YouTube, Reddit, or Facebook behavior;
- do not change the retained profile, browser identity, Slack transport,
  recurring source configuration, cadence, retry count, cost, or model use;
- do not add unbounded permalink expansion, click every `Show more` control, or
  launch a duplicate browser.

## Acceptance Criteria

1. A minimized regression fails on the old raw-card stop and passes when a
   later capture supplies enough accepted unique X posts.
2. The service X adapter passes `request.item_limit` into `search_x_browser`,
   and the scraper clamps the explicit ceiling to a documented safe bound.
3. Explicit 10- and 20-item ceilings receive proportionate bounded scroll
   budgets while direct non-service calls preserve depth defaults.
4. Existing X quality, auth, canonical identity, quote/media context, rejection
   receipt, and result-limit tests remain green.
5. Focused and full validation plus reproducible service builds pass, and the
   exact successor installs ready with the previous runtime retained as
   rollback.
6. At most one X-only canary uses the exact retained social profile, a 20-item
   ceiling, one attempt, zero cost/model use, and stops at its first terminal
   receipt; recurring schedule state remains unchanged.

## Execution Bounds

- work-unit attempts: two;
- review/rework cycles: one;
- hardening checkpoints: two;
- live provider attempts: one X-only canary after installed-runtime gates;
- terminal stops: acceptance met, named-profile/runtime preflight fails, worker
  timeout, browser/auth uncertainty, or cumulative bound reached.

## Owned Write Surfaces

- `skills/last30days/scripts/lib/x_browser.py`;
- `skills/last30days/scripts/lib/service_acquisition_worker.py`;
- focused X and worker tests;
- version, runtime manifest, changelog/configuration docs when required;
- this plan, `ROADMAP.md`, and append-only `RUNBOOK.md`.

## Definition Of Done

- the installed runtime demonstrably honors a service-requested X accepted-item
  ceiling within a bounded capture loop, one terminal canary is recorded, and
  the plan closes without weakening quality or mutating the recurring schedule.

### Checkpoint P0054-C01 | 2026-08-20

Plan version: 1

State transition:

- `installed_x_retry_accepted -> x_accepted_yield_repro_ready`.

Progress classification:

- `outcome_progress`; live item-level evidence separates legitimate quality
  rejections from the adapter's accepted-yield and ceiling-propagation defects.

Owned changes:

- successor plan/roadmap/runbook authorities only; implementation is not yet
  changed at this checkpoint.

Validation evidence:

- installed service 0.3.52 remains ready/compatible;
- the retained X tab exposes all five accepted posts and seven distinct
  rejected posts from the tick window, while the durable receipt supplies the
  eighth repeated-status rejection;
- five rejected posts contain only 3-16 characters of primary text, one is an
  empty reply with an unrelated quote, and one long result has no visible
  query overlap in the rendered search card;
- source tracing proves `request.item_limit` terminates in worker normalization
  instead of controlling `search_x_browser`, whose standard acquisition budget
  remains 16 results and one scroll.

Authority classification:

- `inherited_authority`; the operator asked to address the suspicious X 5/13
  acceptance result.

Subagent status and reconciliation:

- `not_spawned`; current orchestration policy prohibits delegation.

Graphiti write status:

- pending validated installed-runtime and terminal-canary closeout.

Remaining acceptance criteria:

- create the minimized failing regressions, implement the bounded accepted-yield
  correction, validate/build/install the successor, and run no more than the
  single guarded X canary.

Next action:

- make the raw-card early-stop and lost-item-limit regressions fail on the
  current source.

Checkpoint P0054-C01 is the current authority.

### Checkpoint P0054-C02 | 2026-08-20

Plan version: 2

State transition:

- `x_accepted_yield_repro_ready -> validated_runtime_candidate`.

Progress classification:

- `outcome_progress`; the service ceiling now controls X capture, and the
  bounded loop exits on accepted unique yield rather than raw cards.

Owned changes:

- X item-limit propagation, accepted-yield preview, proportional scroll bound,
  focused regressions, service 0.3.53 identity/manifest, changelog, active-plan
  governance fixture, and checkpoint authorities.

Validation evidence:

- three minimized regressions failed on the prior behavior: the worker omitted
  `limit`, and 10/20-item X requests were rejected as unsupported arguments;
- the regressions now pass, including ten initial short rejections followed by
  ten accepted posts after one scroll and a 20-item case bounded at four
  scrolls;
- focused X/worker/runtime/release/logging suites pass with the existing X
  auth, canonical identity, quote/media context, rejection receipt, duplicate,
  and result-limit cases unchanged;
- the complete `uv run pytest -q` suite passes after the active-plan authority
  fixture was advanced from one to the exact two current plans;
- two service 0.3.53 builds are byte-identical at SHA-256
  `5fd5b4f432483bc675119c23a5ebd343ff087ce28a4f83ae7b6181e4addfa872`.

Authority classification:

- `inherited_authority`; implementation remains within the operator-requested
  X acceptance correction and preserves the established runtime envelope.

Subagent status and reconciliation:

- `not_spawned`; current orchestration policy prohibits delegation.

Graphiti write status:

- pending installed-runtime and terminal-canary closeout.

Remaining acceptance criteria:

- commit and push the exact candidate, transactionally install service 0.3.53,
  verify rollback/runtime identity, then preflight and enqueue no more than the
  single X-only 20-item canary.

Next action:

- commit and push the validated source candidate before installation.

Checkpoint P0054-C02 is the current authority.

### Checkpoint P0054-C03 | 2026-08-20

Plan version: 3

State transition:

- `validated_runtime_candidate -> installed_canary_blocked`.

Progress classification:

- `outcome_progress`; the exact successor is installed and verified, while
  the terminal provider proof remains correctly unconsumed behind two
  independent runtime preflight failures.

Owned changes:

- committed and pushed service 0.3.53 as `267e218` on
  `fix/x-accepted-yield`;
- transactionally installed that exact service with 0.3.52 retained as
  rollback;
- prepared and removed an owner-private, X-only, 20-item, one-attempt canary
  configuration without changing the recurring schedule or creating a tick.

Validation evidence:

- the post-commit service artifact remains byte-identical at SHA-256
  `5fd5b4f432483bc675119c23a5ebd343ff087ce28a4f83ae7b6181e4addfa872`;
- installed service 0.3.53/schema 16 is ready and compatible with MCP 4.0.3 at
  runtime-manifest SHA-256
  `95836f4f0ac7038023ab468b13c8130df01b150fd139c11b839cf4274b8bf0ed`;
- installed imports expose the new `limit` argument, the 100-item and
  eight-scroll bounds, the five-items-per-scroll budget, the accepted-yield
  stop, and worker item-limit propagation;
- both state-free canary preflights stopped because no configured notification
  transport passed readiness; direct Slack verification returned temporary
  DNS failure and Gmail profile readback timed out;
- the browser census maps session `last30days-facebook` onto the unrelated
  exclusive `default` profile/browser rather than the exact retained social
  profile. A service-owned release of the accidental X tab was refused by the
  lease conflict, so no provenance bypass, browser shutdown, or foreign-profile
  mutation occurred;
- no canary tick was enqueued: durable tick count remains 55, active attempts
  remain zero, the latest tick remains
  `tick-0fb90267ebbec47e0fe769aa3b485bdc`, and recurring configuration SHA-256
  remains
  `ffcfc71a72d2a6696077227436250a863fe7f258b7767bf9a2746226b5733054`.

Authority classification:

- `inherited_authority`; installation and the guarded canary attempt remain
  within the operator-requested X acceptance correction, while the failed
  preflight terminates the current provider-effect slice.

Subagent status and reconciliation:

- `not_spawned`; current orchestration policy prohibits delegation.

Graphiti write status:

- `graphiti_write_deferred`; the bounded provider-readiness check returned
  `degraded` with a Codex app-server `TimeoutError`, so no new episode was
  queued.

Remaining acceptance criteria:

- acceptance criterion 6 remains unmet. Restore outbound notification
  readiness and reconcile the exact `last30days-facebook` social-profile
  session without touching the unrelated default browser; only after both
  preflights pass may the one X-only 20-item canary be enqueued.

Next action:

- re-run state-free notification and exact-profile provenance preflights after
  those external/runtime ownership conditions recover. Do not enqueue a tick
  until both pass.

Checkpoint P0054-C03 is the current authority.

### Checkpoint P0054-C04 | 2026-08-20

Plan version: 4

State transition:

- `installed_canary_blocked -> terminal_canary_identity_misrouted`.

Progress classification:

- `outcome_progress`; the one authorized live attempt converted the prior
  readiness ambiguity into a timestamped cross-profile session-rebind proof.

Owned changes:

- pushed the previously local checkpoint commit `5d4f177` after outbound Git
  connectivity recovered;
- derived one owner-private X-only 20-item config, passed state-free preflight,
  enqueued its exact prospective tick once, and removed the temporary config;
- did not retry, modify the recurring schedule, touch the unrelated default
  browser, or mutate either browser profile.

Validation evidence:

- state-free preflight was `ready` for tick
  `tick-4098d184cfee7bfc63fe407b3e2ece98`, exactly one X lane, one attempt,
  20 items, 50 requests, 120 wall seconds, and zero cost/model use; Slack
  readiness passed and Gmail was not needed after the first ready transport;
- the exact no-launch access plan selected `last30days-facebook` by
  `authenticated_target`, found zero holders or conflicts, and the browser
  capability preflight applied the validated WSL stealth-Chromium binding
  without launch;
- the tick terminalized `complete_degraded` after one request and 11 seconds,
  with zero observed, accepted, or rejected cards and X lane
  `blocked_human`; incident
  `incident-edab7eb0cdc74e9c37e74ac80db6e890` reopened and its Slack state
  change notification succeeded;
- agent-browser first launched PID 56863 under exact profile/session
  `last30days-facebook` and opened `https://x.com/home` on Route B. Three
  seconds later it recorded the same logical session as attached to unrelated
  default-profile PID 80220 with conflict session `default` and
  `profile_compatibility_missing_or_blocked`;
- the retained 1047x490 incident image is the X sign-in page captured after
  that rebind. It is valid evidence that the routed default context was logged
  out, but invalid evidence that the named social profile requires auth;
- recurring config SHA-256 remains
  `ffcfc71a72d2a6696077227436250a863fe7f258b7767bf9a2746226b5733054`,
  `daily-default` remains ready for `2026-08-21T00:00:00Z`, and the temporary
  config is absent.

Authority classification:

- `inherited_authority`; the operator explicitly requested another guarded
  attempt, which consumed the plan's sole live-provider allowance.

Subagent status and reconciliation:

- `not_spawned`; current orchestration policy prohibits delegation.

Graphiti write status:

- provider readiness recovered and one compact source-backed Plan 0054 episode
  was queued as job `606a8781-25bb-4052-a5b3-e3197a192904` after the checkpoint
  commit became durable;
- the job timed out after 60 seconds during extraction, created no episode,
  and is non-retryable. Git planning and runtime receipts remain authoritative;
  no duplicate Graphiti write was queued.

Remaining acceptance criteria:

- criteria 1-5 remain met and criterion 6's single terminal canary is now
  recorded. The definition-of-done live yield proof remains unmet because the
  request never reached X card extraction under the selected profile;
- the live-attempt bound is consumed. No additional X tick is permitted under
  this plan.

Next action:

- do not retry scraping. Diagnose and repair the agent-browser logical-session
  rebind from exact profile `last30days-facebook` to profile `default` as a
  separately bounded runtime-ownership slice, preserving PID 80220 and the
  unrelated `odollo-payment-terms` browser.

Checkpoint P0054-C04 is the current authority.

### Checkpoint P0054-C05 | 2026-08-21

Plan version: 5

State transition:

- `terminal_canary_identity_misrouted -> closed_runtime_accepted_yield_proven`.

Progress classification:

- `outcome_progress`; the separately repaired browser-owner boundary allowed
  one operator-authorized terminal retry to exercise the installed X capture
  loop under the intended authenticated profile.

Owned changes:

- no additional Plan 0054 source change; the already-installed service 0.3.53
  X accepted-yield implementation was exercised after the agent-browser
  ownership repair;
- the one temporary 20/20 canary configuration was removed, and recurring
  source configuration and `daily-default` remained unchanged.

Validation evidence:

- tick `tick-9ff2c6e630de77dbe199eca6e52d0847` terminalized once as
  `complete_degraded`; its X lane and collection/media/OCR/semantic stages all
  succeeded and snapshot `tick-snapshot-1812a46c3db186a590131ceea96aa651`
  was promoted;
- X observed 33 capture rows, accepted 13 unique posts, and rejected 13
  duplicate-status captures, three insufficient-text posts, and four
  off-topic posts. All seven non-duplicate rejections had canonical status
  links and authors; zero were promoted or missing permalinks;
- no X auth incident, notification, retry, cost, model use, or recurring-
  schedule mutation occurred.

Authority classification:

- `inherited_authority`; the operator explicitly authorized the terminal
  retry after the separately bounded browser-owner repair completed.

Subagent status and reconciliation:

- `not_spawned`; current orchestration policy prohibits delegation.

Graphiti write status:

- deferred; repository, installed-runtime, and durable tick receipts remain
  the canonical closeout evidence.

Remaining acceptance criteria:

- none. Criteria 1-6 and the definition of done are satisfied within the
  bounded-yield contract; the ceiling is a maximum pursued within a finite
  scroll budget, not a guarantee that 20 posts pass quality gates.

Next action:

- close Plan 0054. LinkedIn item-limit propagation and accepted-unique
  pagination continue under successor Plan 0055.

Checkpoint P0054-C05 is the terminal authority.
