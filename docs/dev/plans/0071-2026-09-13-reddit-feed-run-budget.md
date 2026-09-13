# Plan 0071 | Reddit Feed Cumulative Run Budget

State: OPEN
Lane: P28
Branch: fix/ordinary-tick-reconciliation
Target: main
Integration: merge
Roadmap: P28
Plan version: 1
Date: 2026-09-13

## Objective

Make recurring Reddit home-feed acquisition return a typed, diagnostic source
failure before the service worker's hard wall-time kill by applying the shared
Agent Browser cumulative run budget to the complete feed operation.

## Current State

- ordinary timer tick `tick-2a466080dc3c23c429ad788c88757ea4`
  completed degraded after Reddit exhausted its 360-second worker envelope;
- the retained provider result contains `safe_error_code=worker_timeout`, zero
  observations, zero accepted items, and no browser-operation diagnostics;
- Agent Browser 0.28.0 has no matching retained job, trace, incident, or failure
  journal record during the exact provider interval, so the stalled browser
  operation is unknown;
- the shared Last30days browser adapter implements a 105-second cumulative run
  budget, but Reddit feed acquisition does not start or end it. Facebook does.

## Scope

- start the shared cumulative browser budget before Reddit feed acquisition and
  end it on every terminal path;
- add a public-interface regression for the budget lifecycle;
- record the ordinary tick receipt that closes Plan 0062/P08 and Plan 0064/P24;
- version, validate, integrate, install, and identify one exact service 0.3.116
  artifact, then synchronize the frozen user-scoped Skill copy.

## Non-Goals

- no manual tick, provider refresh, browser launch, profile mutation, schedule
  change, or Agent Browser repair;
- no claim about which Agent Browser operation stalled in the September 13
  tick;
- no change to Reddit result, scroll, retry, authentication, or acceptance
  limits.

## Acceptance Criteria

1. `scrape_reddit_feed` starts the browser adapter budget with the configured
   request timeout and ends it on success and typed failure.
2. The production adapter caps cumulative feed browser work at 105 seconds,
   leaving the 360-second service worker enough time to serialize diagnostics
   and release the exact service tab.
3. Focused Reddit, browser-runtime, worker, release, and install tests pass;
   generated runtime-manifest validation and repository governance audits pass.
4. The fork integrates the repair and the exact integrated service 0.3.116 is
   installed ready with its manifest and contract accepted.
5. The frozen user-scoped Skill tree matches the integrated Skill tree, the
   schedule remains enabled for its existing next boundary, active work and
   leases remain zero, and SQLite `quick_check` passes.

## Execution Packet

- owner: primary agent;
- critical path: red test, minimal budget lifecycle repair, provider-free
  validation, fork integration, guarded install, exact runtime readback;
- write surfaces: Reddit adapter, focused test, service version and manifest,
  changelog, plans, roadmap, active-lane catalog, runbook, and receipt note;
- bound: one implementation pass, one closed-world remediation pass, one
  integration, and one guarded install;
- terminal condition: all five criteria pass or one exact fail-closed blocker
  is recorded;
- authority classification: `explicit_authority`; the operator said “plan and
  execute” after selecting Last30days as the sole scope.

Subagent status: `not_spawned`; current orchestration policy prohibits
delegation.

## Definition Of Done

All five criteria have current commit, install, schedule, and database receipts,
or the plan records one exact terminal blocker without widening runtime effects.

## Current Checkpoint

### Checkpoint P0071-C01 | 2026-09-13

Plan version: 1

State transition: `planned -> active`.

Progress classification: `blocker_reduction`; the ordinary receipt and
read-only Agent Browser correlation isolate the missing cumulative budget, and
the public-interface regression failed before the repair and passed after it.

Authority classification:

- `inherited_authority`; the operator's plan-and-execute instruction authorizes
  this bounded provider-free implementation and installation packet.

Acceptance state: criterion 1 passes in the focused tracer test. Broader
validation, integration, installation, and final runtime readback remain.

### Checkpoint P0071-C02 | 2026-09-13

Plan version: 1

State transition: `active -> integration_ready`.

Progress classification: `blocker_reduction`; the source and release candidate
are provider-free validated and ready for the fork workflow.

Authority classification:

- `inherited_authority`; validation and fork integration are ordinary steps in
  the operator-authorized execution packet.

Validation evidence:

- 166 focused Reddit, shared browser-runtime, acquisition-worker,
  service-worker, release, runtime-package, and lifecycle-install tests pass;
- the complete suite passes all 2,774 collected tests with seven expected
  skips;
- the runtime manifest was regenerated canonically for service 0.3.116, and a
  candidate artifact built with SHA-256
  `64b1b2a2d99260c4411762c656a0d670e7e1278a9406a4b9433391247b0c37a0`;
- planning, goal, and repository authority audits pass; `git diff --check`
  passes. Ruff is not installed in the project environment and was not added
  for this bounded repair;
- the active-lane audit retains unrelated pre-existing catalog findings and the
  expected P08 plan/catalog mismatch until this closeout is integrated. No
  unrelated lane was mutated.

Subagent status: `not_spawned`.

Graphiti write status: `not_written`; repository and runtime receipts remain
authoritative.

Next action: commit and publish the candidate, integrate it through the public
fork, then install and verify the exact integrated artifact.
