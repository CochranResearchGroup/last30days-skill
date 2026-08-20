# Plan 0054 | X Accepted-Yield Repair

State: OPEN
Roadmap: P08
Plan version: 2
Date: 2026-08-20

## Objective

Make the governed X browser lane pursue the service-requested accepted-item
ceiling within a bounded scroll budget, without weakening the existing post
quality gate.

## Current State

- installed service 0.3.52/schema 16 is ready and compatible with MCP 4.0.3;
- X-only tick `tick-0fb90267ebbec47e0fe769aa3b485bdc`
  observed 13 card captures, accepted five, and rejected eight;
- item-level retained-tab inspection accounts for the eight rejections as five
  genuinely short replies, two off-topic results, and one repeated canonical
  status across extraction snapshots;
- the acquisition request carries its accepted-item ceiling as
  `request.item_limit`, but `_x_adapter` does not pass that ceiling to
  `search_x_browser`;
- the standard X scraper therefore retains its independent 16-item depth cap
  and one-scroll budget, and its early-stop condition measures raw card count
  rather than accepted unique posts.

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
