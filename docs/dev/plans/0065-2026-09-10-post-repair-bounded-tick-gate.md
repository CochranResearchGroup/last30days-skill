# Plan 0065 | Post-Repair Bounded Tick Gate

State: CLOSED
Roadmap: P08
Plan version: 1
Date: 2026-09-10
Branch: `fix/tick-restart-recovery`
Target: `main`

## Objective

Attempt one additional schedule-disabled Last30days tick after the reported
Agent Browser profile and Last30days repairs, but admit the tick only if both
the installed Last30days preflight and current Agent Browser acquisition plan
are ready.

## Current State

The Last30days preflight is ready, but Agent Browser admission is not. No tick
was enqueued and prospective tick
`tick-a3b3b349d40c412ae32aa8e2a81d613a` does not exist in durable tick state.
Exact X, LinkedIn, and Reddit access-plan reads all fail before profile
selection with `runtime_admission_draining` for transaction
`upgrade-bc9935eb-9425-426b-a8bf-fe8e2d00fc14`.

## Scope

- refresh current Last30days installed, schedule, database, and source state;
- refresh current Agent Browser profile, access-plan, runtime, doctor,
  transaction, and source-plan evidence;
- run at most one Last30days no-state preflight;
- enqueue at most one tick only after current browser acquisition is ready;
- record a no-effect terminal blocker when either admission gate fails.

## Non-Goals

- recovering, rolling back, finalizing, installing, reconciling, restarting,
  or cleaning Agent Browser;
- bypassing admission drain, launching a duplicate profile lane, or changing
  the repaired profile;
- changing the recurring Last30days schedule or source configuration;
- enqueueing when current browser acquisition is known to be blocked.

## Acceptance Criteria

1. The current repaired Last30days build and profile state are read back.
2. One prospective manual interval is preflighted without durable tick state.
3. Agent Browser acquisition readiness is checked for X, LinkedIn, and Reddit.
4. A tick is enqueued only if every admission prerequisite is ready.
5. Schedule, active work, leases, database integrity, and Git custody are
   reconciled at the terminal boundary.

## Definition Of Done

One tick reaches a durable terminal state, or the attempt stops without tick
admission at one current typed external gate. The exact result is preserved and
no unsafe retry or runtime repair is inferred.

### Checkpoint P0065-C01 | 2026-09-10

Plan version: 1

State: `blocked_before_tick_admission`

Progress classification: `no_effect_external_gate`

Authority classification:

- `explicit_authority`; the operator authorized one new attempt after reported
  Agent Browser profile and Last30days repairs. The admission contract did not
  authorize Agent Browser transaction recovery.

Evidence:

- installed Last30days 0.3.114/schema 17 is ready and includes commit
  `dfe69f9`'s structured inspect-before-retry preservation;
- the one no-state preflight for interval `2026-09-10T01:06:23Z` through
  `2026-09-11T01:06:23Z`, schedule
  `manual-p0065-20260911-010623`, returned ready for prospective tick
  `tick-a3b3b349d40c412ae32aa8e2a81d613a`;
- Agent Browser profile `last30days-facebook` is available with no holder,
  browser, tab, conflict session, or doctor warning attached to the profile;
- X, LinkedIn, and Reddit access plans all return
  `runtime_admission_draining` before profile selection;
- transaction `upgrade-bc9935eb-9425-426b-a8bf-fe8e2d00fc14` is revision 12,
  `operator_recovery_required`, stopped on
  `candidate_dashboard_presentation_unproven`, with one outstanding owner
  obligation and `recover` as its next safe effectful action;
- doctor reports two runtime hosts and two executable generations, runtime
  monitor backoff, and active incident
  `generation_gc_blocked_by_active_admission_drain`; the supervisor itself is
  ready and the current profile has no profile-scoped doctor issue;
- the September 11 ordinary timer tick independently reproduced the drain:
  X and LinkedIn failed with `runtime_admission_draining`, Reddit stopped after
  its first Agent Browser failure under the new retry contract, and YouTube
  accepted three items;
- prospective tick count is zero, active ticks and open Last30days resource
  leases are zero, and SQLite `quick_check` is `ok`.

Subagent status: `not_spawned`.

Graphiti write status: `not_written`; discovery was healthy but returned no
current repair episode, so current repo and runtime evidence are authoritative.

Remaining criteria or stop rule: criterion 4 stopped correctly at the external
admission gate; all other criteria are reconciled. No tick was enqueued.

Next action: Agent Browser's owning lane should recover or otherwise terminally
resolve the exact transaction and prove one-runtime steady state. Only then
should Last30days receive fresh authority for another bounded tick.
