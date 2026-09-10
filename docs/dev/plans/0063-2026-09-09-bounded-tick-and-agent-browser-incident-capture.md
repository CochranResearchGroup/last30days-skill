# Plan 0063 | Bounded Tick And Agent Browser Incident Capture

State: OPEN
Roadmap: P08
Plan version: 1
Date: 2026-09-09
Branch: `fix/tick-restart-recovery`
Target: `main`

## Objective

Run exactly one schedule-disabled manual tick under the current saved source
configuration, stop at its first terminal receipt, and preserve enough
structured Agent Browser evidence to diagnose any browser-acquisition failure
without modifying the recurring schedule or the Agent Browser runtime.

## Current State

- installed Last30days service 0.3.113/schema 17 is ready and
  `daily-default` remains enabled for `2026-09-10T00:00:00Z`;
- the September 9 ordinary tick terminalized `complete_degraded`, accepted
  three YouTube items, and failed X, LinkedIn, and Reddit during
  `workspace_acquisition` after three transient attempts each;
- the Agent Browser workstation transaction
  `upgrade-bb44488d-b625-4627-8e73-1c7973240c19` is terminal
  `failed_preserved_old_generation`; admission draining is cleared and an
  exact-profile access plan is currently allowed;
- Agent Browser doctor still reports zero runtime hosts, non-steady
  multiplicity, a stopped `runtime-host` supervisor with `invalid_manifest`,
  and a runtime monitor in backoff;
- the Agent Browser source worktree is an independent dirty active lane on
  `plan/profile-permissions-and-request-provenance`; this plan will not edit,
  install, reconcile, or clean that repository or runtime.

## Scope

- verify the current installed Last30days status, saved schedule, database,
  and exact-profile Agent Browser no-launch access plan;
- preflight one rolling 24-hour manual interval under a distinct schedule ID;
- pass the same two non-secret Agent Browser integration settings held by the
  managed Last30days process into the direct manual-tick parent environment;
- enqueue exactly one tick, poll only that tick, and stop at its first terminal
  receipt;
- capture lane, provider-attempt, failure, job/trace, runtime-census, schedule,
  active-work, database, and Git isolation evidence;
- record the outcome in this plan, `ROADMAP.md`, `RUNBOOK.md`, and one bounded
  incident receipt when Agent Browser blocks acquisition.

## Non-Goals

- repairing, restarting, installing, resuming, or reconciling Agent Browser;
- modifying browser profiles, leases, retained sessions, routes, supervisors,
  or presentation state;
- changing the recurring source configuration, schedule digest, cadence, or
  next boundary;
- enqueueing a second tick or retrying a terminal provider/tick result;
- changing source selectors, item ceilings, retry budgets, or content gates.

## Acceptance Criteria

1. Preflight validates the exact bounded manual request without creating tick
   state.
2. Exactly one manual tick is admitted and reaches one durable terminal state.
3. Every enabled lane has terminal attempt, yield, budget, and failure evidence.
4. Any Agent Browser failure is joined to the narrowest available current
   access-plan, job/trace, supervisor, runtime, and workstation evidence.
5. `daily-default` remains unchanged, active tick/provider attempts return to
   zero, and SQLite `quick_check` passes.
6. The durable plan/runbook/receipt record distinguishes Last30days scheduler,
   provider, Agent Browser acquisition, presentation, and maintenance axes.

## Definition Of Done

The one authorized manual tick is terminal or fails before admission at one
exact external gate, its complete bounded evidence is recorded, recurring
schedule and unrelated browser state are unchanged, and no second attempt is
made.

## Execution Packet

### P0063-A | One tick and terminal reconciliation

- owner: primary agent;
- write surface: one manual tick in the installed Last30days database plus this
  plan, P08 roadmap state, runbook, active-lane catalog, and one incident note;
- terminal condition: the single tick reaches a durable terminal state and all
  six acceptance criteria are reconciled, or one exact external blocker stops
  admission before tick state is created.

## Bounds And Stops

- one preflight and one enqueue only;
- use a distinct schedule ID and a rolling 24-hour interval ending at the
  preflight timestamp;
- do not repair Agent Browser from this consumer plan;
- do not retry after a terminal receipt;
- stop before enqueue if the managed Last30days capability-file path cannot be
  inherited without reading or exposing its secret contents.

### Checkpoint P0063-C01 | 2026-09-09

Plan version: 1

State: `authorized_single_tick_preflight_ready`

Progress classification: `planned_live_observation`

Authority classification:

- `scope_expansion`; the operator requested one additional tick and asked
  for durable Agent Browser troubleshooting notes if acquisition fails.

Evidence:

- installed Last30days and schedule readback;
- September 1 through 9 tick/provider ledger review and SQLite `quick_check`;
- current Agent Browser workstation, doctor, supervisor, resource, and
  exact-profile access-plan readback;
- current Agent Browser Plan 0161/runbook and dirty-worktree custody review;
- current Last30days clean branch and Plan 0062 terminal criterion readback.

Subagent status: `not_spawned`.

Graphiti write status: `not_written`; current repo/runtime evidence is the
authority for this live attempt.

Remaining criteria or stop rule: execute exactly one preflight and one tick,
then reconcile criteria 1 through 6 without Agent Browser repair or retry.

Next action: preflight the distinct rolling interval with managed integration
settings inherited, then enqueue and poll only the resulting tick.
