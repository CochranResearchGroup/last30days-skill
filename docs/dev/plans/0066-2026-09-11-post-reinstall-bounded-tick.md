# Plan 0066 | Post-Reinstall Bounded Tick

State: CLOSED
Roadmap: P08
Plan version: 1
Date: 2026-09-11
Branch: `fix/tick-restart-recovery`
Target: `main`

## Objective

Run exactly one schedule-disabled Last30days tick after the operator-reported
Agent Browser reinstall, gated by a fresh Last30days preflight and current
Agent Browser acquisition evidence.

## Current State

- Agent Browser runtime admission is no longer draining. The installed
  executable matches the live runtime host, and the latest upgrade transaction
  is accepted.
- X and LinkedIn return executable `launch_new_browser` access plans on profile
  `last30days-facebook`, without an acquisition blocker or identity conflict.
- Reddit also returns an executable service request without an acquisition
  blocker. Its missing target-freshness record produces advisory
  `verify_or_seed_profile_before_authenticated_work` guidance. Last30days uses
  public Reddit search navigation and does not seed or rewrite profile
  freshness, so this plan does not infer profile-mutation authority.
- Last30days 0.3.114/schema 17 remains active with `daily-default` enabled.

## Scope

- run one fresh no-state preflight for one rolling 24-hour interval;
- enqueue that exact request once only if preflight remains ready;
- poll only that tick to its first durable terminal state;
- reconcile provider attempts, Agent Browser evidence, recurring schedule,
  active work, database integrity, installed identity, and Git custody;
- preserve a bounded incident note if any source or runtime degrades.

## Non-Goals

- seeding, repairing, resetting, or updating any Agent Browser profile;
- recovering, installing, restarting, or reconciling Agent Browser;
- changing source configuration, retry budgets, recurring schedule, or next
  boundary;
- enqueueing a second tick or retrying a terminal provider result.

## Acceptance Criteria

1. One exact prospective request passes the installed no-state preflight.
2. Exactly one tick is enqueued and reaches one durable terminal state.
3. Every enabled lane has terminal yield, attempt, budget, and failure evidence.
4. Browser failures, if any, retain typed Agent Browser recourse without an
   inferred profile or runtime mutation.
5. `daily-default` remains unchanged, active work returns to zero, SQLite
   `quick_check` passes, and installed/Git identities are reconciled.

## Definition Of Done

The one authorized tick is terminal, or the attempt stops at one fresh typed
pre-admission gate. Exact evidence is durable and no second attempt occurs.

## Execution Packet

### P0066-A | One post-reinstall tick

- owner: primary agent;
- write surface: one manual tick in installed Last30days state plus this plan,
  P08, the runbook, active-lane catalog, and at most one bounded receipt note;
- stop rule: one failed preflight, one failed enqueue, or the first durable tick
  terminal state.

## Authority And Evidence

- explicit operator authority: try again after Agent Browser was installed;
- current Agent Browser access plans and doctor/runtime readback;
- installed Last30days service, schedule, configuration, and database;
- Plan 0065 no-effect predecessor and Plan 0064 typed-recourse contract.

Subagent status: `not_spawned`; current orchestration policy prohibits
delegation.

Graphiti discovery status: `healthy_but_stale`; current repository and runtime
receipts are authoritative.

### Checkpoint P0066-C01 | 2026-09-11

Plan version: 1

State: `terminal_complete_degraded`

Progress classification: `material_runtime_improvement_with_one_retained_failure`

Evidence:

- the single preflight passed for interval `2026-09-10T10:25:42Z` through
  `2026-09-11T10:25:42Z`, schedule
  `manual-p0066-20260911-102542`, config digest
  `sha256:8e3811d5e9b561cfd3f97b3d9897770ee4c623fe9e74a443bc01d86fca4d3449`,
  and prospective tick `tick-3fe4ae25a3fb7f6dce63e2881fedc504`;
- exactly that tick was enqueued once and terminalized `complete_degraded` at
  `2026-09-11T10:38:08.446345Z`, with head promotion and snapshot
  `tick-snapshot-63666743e2c95ded9a705bc7f7d22612`;
- YouTube accepted 3 of 8 observed items, LinkedIn accepted 52 of 1,472, and
  Reddit accepted 38 of 673. The promoted snapshot contains 93 source versions
  and 16 media artifacts;
- X failed its sole attempt during extraction after 12 successful bounded eval
  operations. Agent Browser job
  `mcp-service-request-evaluate-a45fc2da-b4ec-4d07-bac8-d43dd9528e04`
  failed `service_state_lock_timeout: file lock; waited_ms=1002` while another
  X evaluate job overlapped its recorded interval;
- the X result preserves `effect_uncertain`, `inspect_before_retry`,
  `inspect_job_and_refresh_plan`, and hard stop `blind_retry`; Last30days made
  no second X attempt and the exact tab-handle release succeeded;
- Agent Browser recorded 154 Last30days jobs in the interval: 5 successful and
  1 failed for X, 60 successful for LinkedIn, 87 successful for Reddit, and one
  unattributed successful job. Five successful evaluate jobs have inverted
  `startedAt`/`completedAt` ordering; note 0113 preserves their IDs;
- all Last30days resource leases are released, no tick remains active, the
  recurring schedule is still enabled/ready for `2026-09-12T00:00:00Z`, and
  SQLite `quick_check` is `ok`;
- postflight Agent Browser diagnosis is `ready`; the retained shared browser is
  current and healthy and a fresh X access plan recommends reuse. No profile
  or runtime mutation was performed.

Acceptance reconciliation:

1. satisfied;
2. satisfied;
3. satisfied;
4. satisfied;
5. satisfied.

Remaining gate: X remains unhealthy on a reproducible Agent Browser
service-state lock timeout. This plan authorizes no retry or Agent Browser
repair. Plan 0066 and the bounded observation are closed.
