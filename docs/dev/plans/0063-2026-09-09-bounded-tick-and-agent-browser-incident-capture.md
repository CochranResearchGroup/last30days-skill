# Plan 0063 | Bounded Tick And Agent Browser Incident Capture

State: CLOSED
Roadmap: P08
Plan version: 2
Date: 2026-09-09
Branch: `fix/tick-restart-recovery`
Target: `main`

## Objective

Run exactly one schedule-disabled manual tick under the current saved source
configuration, stop at its first terminal receipt, and preserve enough
structured Agent Browser evidence to diagnose any browser-acquisition failure
without modifying the recurring schedule or the Agent Browser runtime.

## Current State

- the one authorized manual tick
  `tick-22c576498aff25c201ec855d75a947ae` is terminal
  `complete_degraded`: X accepted 80, YouTube accepted three, and LinkedIn and
  Reddit each exhausted three transient Agent Browser attempts;
- LinkedIn reached tabs and navigation but hit two retained
  `service_state_lock_timeout` evaluate failures; Reddit created all three tabs
  before `Page.enable` or `Runtime.enable` timed out;
- the promoted 83-source head, eight provider attempts, exact Agent Browser
  job/trace recourse, and post-terminal runtime evidence are preserved in
  [note 0111](../notes/0111-2026-09-09-plan0063-agent-browser-tick-incident.md);
- `daily-default` remains enabled/ready for `2026-09-11T00:00:00Z`, with the
  intervening ordinary tick—not this manual schedule—recorded at the September
  10 boundary; active ticks and open tick leases are zero and SQLite
  `quick_check` is `ok`;
- newer post-terminal Agent Browser evidence now reports one steady-current
  runtime on generation `0.28.0-5928ff06d8d0-927b55137ad0`, but doctor remains
  unsuccessful on a supervisor `port_conflict` and explicit
  `last30days-facebook` owner-binding/session-authority warnings;
- no second tick or Agent Browser mutation was attempted. The independent
  dirty Agent Browser source lane remains untouched.

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

### Checkpoint P0063-C02 | 2026-09-09

Plan version: 2

State: `bounded_tick_terminal_incident_preserved`

Progress classification: `complete_degraded_observation`

Authority classification:

- `explicit_authority_consumed`; exactly one preflight and one enqueue ran.
  No second tick or Agent Browser repair was attempted.

Evidence:

- manual tick `tick-22c576498aff25c201ec855d75a947ae`, terminal
  `complete_degraded`, with X 80/254, YouTube 3/8, LinkedIn 0/0 after three
  attempts, and Reddit 0/0 after three attempts;
- promoted query head
  `tick-snapshot-43e60f758cdde8a3d188734ed8980859` with 83 lexical source
  entries and truthful per-lane completeness;
- two LinkedIn `service_state_lock_timeout` Agent Browser jobs and three Reddit
  `Page.enable` / `Runtime.enable` timeout jobs, all carrying
  `inspect_before_retry` recourse and a `blind_retry` hard stop;
- post-terminal Agent Browser generation, multiplicity, supervisor, doctor,
  profile-lease, and independent source-worktree readback;
- unchanged recurring schedule authority, zero active ticks, zero open tick
  leases, and SQLite `quick_check=ok`.

Subagent status: `not_spawned`.

Graphiti write status: `not_written`; the current repo receipt and installed
runtime/job ledgers are the authoritative handoff, and no separate external
memory write was necessary for this bounded operation.

Remaining criteria or stop rule: all six acceptance criteria are reconciled.
The Agent Browser defects remain external follow-up under its current Plans
0142, 0161, and P116; a new Last30days canary requires fresh authority.

Next action: hand note 0111's exact job IDs and post-upgrade runtime snapshot to
the Agent Browser lane; do not blind-retry this tick.
