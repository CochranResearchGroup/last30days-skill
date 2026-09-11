# Plan 0066 | Post-Reinstall Bounded Tick

State: OPEN
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
