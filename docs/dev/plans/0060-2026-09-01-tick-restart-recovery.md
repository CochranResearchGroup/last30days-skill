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
- the exact `last30days-facebook` profile remains selected, but current Agent
  Browser status has zero runtime hosts and zero compatible live browsers;
- recurring X and LinkedIn provider manifests now declare three attempts,
  aggregate limits admit their full bounded retry budget, and service 0.3.91
  is installed ready with the schedule rebound to the exact config digest.

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

### Checkpoint P0060-C03 | 2026-09-01

Plan version: 1

State: `restart_repair_installed_agent_browser_runtime_host_blocked`

Progress classification: `blocker_reduction`

Authority classification:

- `inherited_authority`

Installed and schedule evidence:

- commit `89ac5f8d931f2183067c1aa7e2e57c6e7d9a9c93` is published at
  `origin/fix/tick-restart-recovery` and its complete canonical test suite
  passed;
- the first installer readiness check failed because the owner-private config
  change correctly paused `daily-default` at `schedule_config_replaced`; its
  attempted 0.3.90 rollback could not parse provider attempt limit three;
- the already-staged exact 0.3.91 release was selected without a second build
  or installer transaction, and the established full-config-digest guarded
  rebind moved exactly one paused `daily-default` row from digest
  `sha256:9238e351363d0e4d37fa965c748df53012ae9a217231901fef60a720413ad417`
  to validated digest
  `sha256:b2ec0ed2eecc7d0e1fa1b6fa97595bf6fbfeb51d44db9f99d4a5884986856c3e`;
- backup
  `/home/ecochran76/.local/share/last30days/backups/research-pre-retry3-rebind-20260901.db`
  and the live database each pass `quick_check`;
- service 0.3.91 is ready on schema 16 and runtime-manifest SHA-256
  `a6509a82b743c7eef0b1cb7156901aca9b2c0263508c527dc9253094463d4c90`;
  `daily-default` is ready with its prior tick and unchanged next boundary
  `2026-09-02T00:00:00Z`.

LinkedIn verification evidence:

- the one authorized 20-item installed LinkedIn feed worker completed in 2.3
  seconds with transient `agent_browser_error`, failure stage
  `workspace_acquisition`, zero attempted/observed/accepted/rejected posts, and
  message `agent-browser service request returned no result`;
- direct Agent Browser jobs readback fails with
  `Runtime host endpoint metadata is incomplete; preserving evidence and
  refusing a duplicate host`;
- direct Agent Browser status reports one dashboard, zero runtime hosts,
  `runtime_host_count_not_one`, runtime state `degraded`, partial process
  observation, and unavailable browser process inventory;
- exact-profile access planning still selects `last30days-facebook`, reports
  no identity or acquisition blocker, but finds zero compatible live browsers;
  owner generation 69 is terminal with process absence proven.

Interpretation:

- this post-install failure occurs before LinkedIn navigation or DOM
  extraction. It is an Agent Browser runtime-host availability failure, not
  evidence of a LinkedIn scraper, authentication, or content-quality defect;
- the attempt budget stopped after the first terminal receipt. No browser
  launch, force-replacement, second provider attempt, or profile mutation was
  performed by this checkpoint.

Subagent status: `not_spawned`

Graphiti write status: `not_written`; repository and exact runtime receipts are
the durable evidence surfaces available in this session.

Next action: restore exactly one healthy Agent Browser runtime host outside this
repository, then request a fresh bounded LinkedIn retry. Do not change LinkedIn
selectors or quality gates from this pre-navigation failure.

### Checkpoint P0060-C04 | 2026-09-01

Plan version: 1

State: `authorized_linkedin_retry_confirms_runtime_host_blocker`

Progress classification: `blocker_confirmation`

Authority classification:

- `explicit_authority`; the operator requested one fresh retry after the Agent
  Browser upgrade.

Retry evidence:

- Last30days `service_info` was called first and reports installed service
  0.3.91 ready and compatible on schema 16 with runtime-manifest SHA-256
  `a6509a82b743c7eef0b1cb7156901aca9b2c0263508c527dc9253094463d4c90`;
- the exact worker-shaped Agent Browser access plan selects
  `last30days-facebook` by registered LinkedIn authentication, reports zero
  compatible live browsers, and permits replacement of terminal owner
  generation 69 with process absence proven;
- the one authorized 20-item LinkedIn home-feed retry
  `plan0060-linkedin-postinstall-2` terminated in 2.3 seconds with transient
  `agent_browser_error` at `workspace_acquisition`; attempted, observed,
  accepted, rejected, scroll, refresh, and reload counts are all zero;
- the Agent Browser `tab_new` service request consumed 2.1 seconds and returned
  no result. Direct jobs readback still fails with `Runtime host endpoint
  metadata is incomplete; preserving evidence and refusing a duplicate host`;
- post-attempt Agent Browser status reports selected generation
  `0.28.0-fa99bc026aa4-a04fbee7185d`, one dashboard, zero runtime hosts,
  `runtime_host_count_not_one`, degraded lifecycle readiness, and unavailable
  browser process observation.

Isolation evidence:

- `daily-default` remains enabled and ready at config digest
  `sha256:b2ec0ed2eecc7d0e1fa1b6fa97595bf6fbfeb51d44db9f99d4a5884986856c3e`,
  retains last tick `tick-56318fada747d408976df141ab17a0ef`, and retains the
  next boundary `2026-09-02T00:00:00Z` with no runtime error;
- active tick attempts, provider attempts, and resource leases are zero, and
  the live SQLite database passes `quick_check`;
- no LinkedIn page was navigated, inspected, or scraped; no second retry,
  Agent Browser cleanup, alternate profile, schedule mutation, or service
  installation was performed.

Subagent status: `not_spawned`

Graphiti write status: `not_written`; the repository checkpoint and live
runtime receipt are the durable evidence surfaces.

Next action: Agent Browser must restore exactly one runtime host and complete
its endpoint metadata. Retry LinkedIn only after that census reads one host;
do not change LinkedIn selectors from this pre-navigation failure.
