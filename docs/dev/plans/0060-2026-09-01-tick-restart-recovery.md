# Plan 0060 | Tick Restart Recovery

State: OPEN
Roadmap: P08
Plan version: 1
Date: 2026-09-01
Branch: `fix/tick-restart-recovery`
Target: `main`

## Objective

Prevent a planned Last30days service restart from converting an active
recurring provider worker into a terminal `worker_exit_nonzero` lane failure,
then give the recurring X and LinkedIn providers three bounded attempts for
ordinary transient failures.

## Current State

- the September 1 timer fired normally and completed `complete_degraded`;
- X accepted 10/10 and YouTube accepted 3/3;
- the LinkedIn worker started at `2026-09-01T00:00:40.238257Z`, the installed
  service files changed at `00:02:07.707Z`, the worker returned transient
  `worker_exit_nonzero` at `00:02:10.867488Z`, and the replacement service
  started at `00:02:11Z`;
- the exact `last30days-facebook` Agent Browser profile currently has one
  compatible retained browser and no acquisition or lifecycle blocker;
- recurring X and LinkedIn provider manifests now declare three attempts and
  aggregate limits admit their full bounded retry budget; installation of
  service 0.3.91 is still pending.

## Scope

- add a deterministic regression for shutdown while a scheduled tick provider
  is active;
- make service shutdown drain an active tick under a finite timeout while
  preserving child workers during the drain;
- keep the timer from enqueuing new work after shutdown begins;
- set recurring X and LinkedIn provider attempt limits to three;
- preserve Reddit and Facebook disabled state, YouTube behavior, exact profile
  identity, source item ceilings, and deterministic ad/spam filtering;
- install and verify one exact candidate only after repository validation;
- run one bounded LinkedIn verification after installation.

## Non-Goals

- changing feed selectors, scroll ceilings, semantic filtering, or accepted
  content policy;
- modifying Agent Browser lifecycle ownership or creating another browser
  profile;
- changing the daily boundary or enabling Reddit or Facebook;
- treating an interrupted deployment as evidence of LinkedIn authentication
  or scraper failure.

## Acceptance Criteria

1. A service-stop regression proves an active tick can finish without its
   worker being terminated by the restart path.
2. Shutdown remains bounded and reports a truthful non-drained result when the
   configured deadline expires.
3. The installed user unit signals the main service first and retains a finite
   stop timeout sufficient for the application drain.
4. Recurring X and LinkedIn provider manifests each allow three attempts while
   all source enablement and item ceilings remain unchanged.
5. Focused service-runtime, tick, install, and configuration tests pass before
   broader validation.
6. The installed service is ready and compatible, the next timer boundary is
   unchanged, and one bounded LinkedIn verification returns a terminal receipt.

## Definition Of Done

- planned service restarts preserve an in-flight tick worker for a finite drain;
- the recurring X and LinkedIn providers can each consume up to three transient
  attempts without exceeding aggregate tick limits;
- repository validation, installed readiness, schedule continuity, and one
  post-install LinkedIn receipt satisfy the acceptance criteria above.

## Execution Packets

### P0060-A | Red regressions

- owner: primary agent;
- write surface: focused runtime/install/config tests only;
- terminal condition: the restart-drain and retry-budget assertions fail on
  the current implementation for the expected reasons.

### P0060-B | Restart-safe implementation

- owner: primary agent;
- write surface: service runtime/shutdown and installed unit generation;
- terminal condition: focused regressions pass with a finite drain bound.

### P0060-C | Recurring configuration and live acceptance

- owner: primary agent;
- write surface: recurring configuration, version/changelog when required,
  plan, roadmap, runbook, and installed artifact;
- terminal condition: repository validation passes, installation is ready,
  and one bounded LinkedIn verification is terminal.

## Bounds And Stops

- at most two implementation attempts for the restart seam;
- one install candidate and one post-install LinkedIn verification;
- no Agent Browser cleanup, profile replacement, or duplicate-profile lane;
- stop before installation if focused or comprehensive validation is red;
- stop the live verification on its first terminal receipt.

### Checkpoint P0060-C01 | 2026-09-01

Plan version: 1

State: `diagnosed_and_planned`

Progress classification: `blocker_reduction`

Authority classification:

- `inherited_authority`

Evidence:

- durable tick receipt `tick-56318fada747d408976df141ab17a0ef`;
- installed service/unit mtime `2026-09-01T00:02:07.707Z` and process start
  `2026-09-01T00:02:11Z`;
- current exact-profile Agent Browser access plan and retained LinkedIn tab;
- code paths `SubprocessAcquisitionRunner.run`, `TickScheduleLoop.stop`,
  `_serve`, and `should_retry_provider`.

Subagent status: `not_spawned`

Next action: add the two red regressions before changing runtime behavior.

### Checkpoint P0060-C02 | 2026-09-01

Plan version: 1

State: `validated_candidate_ready_to_install`

Progress classification: `blocker_reduction`

Authority classification:

- `inherited_authority`

Evidence:

- restart-drain and systemd-unit regressions failed against the prior behavior
  and pass against the candidate;
- provider-config regression accepts attempts three, rejects attempts four,
  and proves retry ordinals zero and one are eligible only for transient
  failures;
- saved recurring revision `operator-20260901-x-linkedin-retry3-v1` retains
  one attempt for Reddit, YouTube, and Facebook, sets three for X and LinkedIn,
  and budgets seven aggregate attempts, 350 requests, and 840 wall seconds;
- final artifact
  `dist/service/last30days-service-0.3.91.tar.gz` has SHA-256
  `2c18e919c4fbe6fa97690dff5ca595e89558f078ed7f84a85ef00258485b589f`;
- focused validation and the complete canonical `uv run pytest -q` suite pass.

Subagent status: `not_spawned`

Graphiti write status: `pending_closeout`

Next action: commit and publish the candidate checkpoint, then consume the one
authorized install and bounded LinkedIn verification.
