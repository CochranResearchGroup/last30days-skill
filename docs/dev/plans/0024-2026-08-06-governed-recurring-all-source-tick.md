# Plan 0024 | Governed recurring all-source tick

State: OPEN
Roadmap: P08
Date: 2026-08-06
Plan version: 1
Predecessor: Plan 0023 version 20/checkpoint P0023-C52

## Stable Goal

Enable one user-scoped daily UTC schedule that invokes the exact durable
all-source tick accepted by Plan 0023, then prove one timer-owned tick,
restart-safe deduplication, next-boundary continuity, ordinary-query promotion,
and fail-closed pause controls without creating a second acquisition path.

## Current State

- operator `ok go` explicitly authorizes this separately governed timer-
  enablement slice after Plan 0023 and P07 closed;
- origin/main and the clean local worktree agree at terminal Plan 0023 commit
  `895d460ebad2ec14f75d6e6027b43371dd2e4fbe`;
- installed service 0.3.4/schema15 and MCP 4.0.1 are ready and compatible;
- SQLite integrity is `ok`; all three existing ticks are terminal, no tick or
  execution attempt is active, and no timer-owned tick exists;
- all 42 predecessor collection specifications remain disabled and no
  `last30days` systemd timer exists;
- user config revision `p0023-c48-local-analysis-v1` retains five enabled
  targets, UTC timezone, 86,400-second lateness, aggregate limits
  5 attempts/250 requests/15 items/600 wall seconds/zero cost/zero model
  tokens, and two notification transports;
- Plan 0023 used 15 of the standing cumulative 50 provider-attempt ceiling;
- `TickCoordinator.enqueue_tick()` is the accepted deep interface and accepts
  `trigger=timer`, but `build_tick_runtime()` is manual-only and the service
  daemon constructs no tick scheduler or tick recovery loop;
- the existing recurring `CollectionCoordinator` is a predecessor per-spec
  refresh-job scheduler and must not be reused as a second all-source path.

## Product Decision

Recurrence is service-owned, config-driven, and thin. A dedicated
`TickScheduleCoordinator` derives one cadence-aligned `TickRequest` and calls
only the existing `TickCoordinator.enqueue_tick()`. The existing runner,
provider registry, lane expansion, budgets, raw-first evidence, incidents,
derivatives, catalog, terminal snapshot, and ordinary query head remain
unchanged.

The first supported schedule is one daily UTC schedule anchored at midnight.
The scheduler may admit only the latest completed boundary, never fan out a
catch-up backlog. On first activation it may enqueue that latest boundary only
when it is within the frozen tick lateness bound. It then advances durable
state to the next boundary before another admission. A restart resumes an
incomplete timer tick by its existing identity before considering a new due
boundary.

## Scope

1. extend the user-scoped tick configuration with one optional strict schedule
   object: `enabled`, `schedule_id`, `interval_seconds`, and `anchor_seconds`;
2. add durable schedule state/events and schema migration 16;
3. add a deep `TickScheduleCoordinator` that performs boundary calculation,
   at-most-one catch-up, immutable request construction, pending-tick recovery,
   and idempotent state advancement;
4. add a dedicated service-owned `TickScheduleLoop` with bounded polling and
   health projection;
5. expose sanitized read-only schedule status through the installed CLI/API;
6. preserve backward compatibility by treating an absent schedule object as
   disabled;
7. cut, reproduce, independently review, and transactionally install one
   service patch candidate;
8. revise only the private config revision and schedule object, enable one
   daily UTC schedule, admit at most one timer tick during activation proof,
   restart once after terminalization, and prove no duplicate boundary;
9. leave the accepted daily schedule enabled only if all closeout invariants
   pass; otherwise pause it fail-closed and preserve exact receipts.

## Non-Goals

- no second provider, source, target, credential, profile, tenant, recipient,
  notification transport, artifact class, or private-data class;
- no legacy collection-spec enablement or conversion of 42 predecessor specs;
- no per-source timer, cron job, browser-launching timer, systemd timer, or
  independent lookback;
- no catch-up backfill, more than one newly admitted historical boundary, or
  replay of multiple missed intervals;
- no change to provider order, item/request/wall/cost/model limits, OCR,
  semantic sidecars, incidents, Guacamole gates, cataloging, query fusion, or
  access partitions;
- no paid provider/model use, human observation, release, tag, upstream push,
  public publication, or destructive cleanup;
- no claim that every lane must succeed; source-local failures remain truthful
  degraded coverage under the Plan 0023 contract.

## Architecture And Owned Write Surfaces

Expected implementation writes are limited to:

- `skills/last30days/scripts/lib/service_tick_schedule.py` for schedule state
  and coordination;
- `service_store.py` for schema-16 durable tables;
- `service_tick.py`, `service_tick_runtime.py`, `service_runtime.py`,
  `service.py`, and the narrow application/HTTP/contracts surfaces needed for
  construction and sanitized status;
- focused scheduler/runtime/config/recovery/lifecycle tests;
- service version, runtime manifest, schemas/generated MCP catalog, changelog,
  Skill/configuration docs, installer/package assertions, and canonical
  planning/receipt authorities.

The private config and installed runtime are separate gated write surfaces.
No repo file may contain service identities, selectors, access partitions,
profile names, credential references, notification routing, recipients,
artifact paths, or observation endpoints from that config.

## Durable Schedule Contract

`tick.schedule`, when present, contains exactly:

```json
{
  "enabled": false,
  "schedule_id": "daily-default",
  "interval_seconds": 86400,
  "anchor_seconds": 0
}
```

- `interval_seconds` is bounded from 900 through 604,800 seconds;
- `anchor_seconds` is an integer from zero through
  `interval_seconds - 1`, measured from the Unix epoch in UTC;
- the production activation is exactly 86,400 seconds with anchor zero;
- absent configuration is disabled and creates no schedule state;
- config enable/change is loaded only on service construction/restart;
- durable state binds schedule ID, config digest, cadence, anchor, enabled
  state, next interval boundary, last admitted tick, and timestamps;
- durable events bind initialized, admitted, resumed, skipped-stale, paused,
  and config-replaced transitions without private config content.

The coordinator calculates the latest completed aligned boundary. First
activation seeds at most that boundary if its age is within
`tick.lateness_seconds`; otherwise it advances to the next future boundary and
records a sanitized stale-skip event. Once a boundary is admitted, durable
state advances before the provider run. Repeated polls or restarts return the
same tick identity and never duplicate provider work. If a timer tick is
incomplete, recovery runs it before another due interval is considered.

## Work Graph

| Packet | Outcome | Depends on | Terminal gate |
|---|---|---|---|
| S01 design freeze | Open P08/Plan 0024 with runtime baseline, exact bounds, and one fresh independent review | operator authorization, Plan 0023 | reviewed plan or one bounded rework |
| S02 deterministic scheduler | Add config, migration, schedule coordinator/loop/status with public-interface red/green tests | S01 PASS | focused tests, schema migration/replay, no live mutation |
| S03 exact candidate | Cut patch version, manifests/contracts, reproducible artifact, lifecycle/rollback proof, complete suite | S02 | one fresh closed-world candidate review and at most one rework |
| S04 disabled install | Install exact reviewed candidate with schedule absent/disabled and prove unchanged runtime/config/timer state | S03 PASS | installed identity, rollback, SQLite, zero new ticks |
| S05 activation | Revise only private config revision/schedule, restart, and admit at most one automatic timer tick | S04 | cumulative provider attempts no more than 20/50; stop on first hard failure |
| S06 restart and closeout | Restart once after terminal state, prove no duplicate boundary, exact next due, query-head promotion, and enabled daily status | S05 terminal | independent receipt verification, Graphiti, origin push |

S01-S06 are one serialized critical path. No implementation delegation is
planned because config, migration, runtime construction, installation, and
live schedule state overlap tightly. One fresh independent evaluator is
reserved for S01 and one closed-world evaluator pass for the exact candidate/
live receipt under the single goal-level review/rework bound.

## Bounds And Gates

- maximum implementation attempts per packet: 2;
- maximum goal-level review/rework cycles: 1;
- maximum consecutive hardening/no-progress checkpoints: 2;
- checkpoint after every validated packet and before review, install, private-
  config mutation, live activation, restart, closeout, or push;
- active implementation-agent concurrency: 1;
- global active tick concurrency: 1;
- one daily schedule, one enabled schedule ID, and zero legacy enabled specs;
- at most one new timer-owned tick during activation proof;
- at most five new provider attempts, 250 requests, 15 accepted items, 600
  aggregate wall seconds, zero cost, and zero model tokens;
- cumulative provider attempts may rise only from 15 to at most 20 of the
  standing 50 ceiling;
- at most one candidate install and two explicit post-install service restarts
  (activation load and durability proof); installer-owned stop/start is part of
  the one install transaction;
- one existing notification chain may operate only for a real persisted
  incident; no test notification is sent;
- no Guacamole observation lease or human takeover.

The operator's `ok go` is the human gate for this named recurrence objective,
the exact private schedule addition, the bounded source effects of one timer
tick, and leaving the accepted daily schedule enabled. New authorization is
still required for a different cadence, more schedules, wider ceilings,
another source/target/provider/credential/data class, paid use, human
observation, destructive action, public release, tag, or upstream/publication
action beyond the already-standard origin push.

## Hard Stops

Stop and pause/avoid activation on:

- schedule ambiguity, local-time/DST dependence, boundary or config-digest
  drift, more than one catch-up admission, or duplicate timer tick identity;
- any call path that bypasses `TickCoordinator.enqueue_tick()`;
- pending timer work that is not resumed before a new boundary;
- more than one active tick, more than one live proof tick, or cumulative
  provider attempts above 20;
- stale boundary older than the frozen lateness bound;
- source/target/provider/config expansion, enabled legacy spec, non-zero
  cost/model usage, unrequested Guac/human route, notification without a
  persisted incident, or timer state that cannot be paused;
- SQLite, migration, rollback, access-partition, immutable evidence,
  derivative, snapshot, ordinary-query, or installed identity failure;
- a blocking independent finding that remains after the single rework cycle;
- two consecutive no-progress/hardening checkpoints.

## Acceptance Criteria

1. Absent/disabled schedule config creates no durable schedule and no timer
   work; strict malformed or unknown schedule fields fail before source work.
2. The only recurrence path constructs `TickRequest(trigger=timer)` and calls
   the existing `TickCoordinator.enqueue_tick()` deep interface.
3. UTC cadence/anchor calculation is deterministic across restart and permits
   at most the latest completed boundary within the lateness window.
4. Schedule state advances durably before provider execution; poll/restart
   replay cannot duplicate a boundary, tick, attempt, budget event, evidence,
   artifact, derivative, notification, or snapshot promotion.
5. An incomplete timer tick resumes by the same tick/attempt/stage identities
   before a new due boundary is admitted.
6. Singleton overlap preserves Plan 0023's queued/lateness and
   `missed_due_to_overlap` semantics with an exact coverage receipt.
7. Service health and read-only CLI/API status expose only schedule ID,
   enabled state, cadence, next/last boundary, last tick ID/state, and runtime
   error—never private config content.
8. One exact candidate migrates and rolls back without loss; disabled install
   creates zero schedule/tick/source side effects.
9. Installed activation admits at most one automatic daily timer tick under
   the exact five-lane zero-cost/model envelope and terminalizes truthfully.
10. The terminal timer tick promotes one coherent ordinary-query snapshot with
    exact coverage/freshness, partitions, matching channels, and provenance.
11. One post-terminal service restart preserves the same boundary/tick receipt,
    creates no duplicate attempt, and retains the next daily due boundary.
12. All 42 legacy specs remain disabled, no systemd timer is created, and the
    service-owned daily schedule is left enabled only after every gate passes;
    otherwise it is paused with exact failure evidence.
13. The terminal receipt reconstructs schedule/config/tick identities, due
    boundaries, provider/budget/stage/evidence/derivative/snapshot results,
    restart state, and ordinary-client proof.
14. One independent drift-discovery review and closed-world remediation
    verification leave zero unresolved accepted blocking findings.

## Definition Of Done

Plan 0024 closes only when the exact service-owned daily UTC recurrence path is
implemented, installed, activated, and live-proven through at most one timer-
owned tick; restart/idempotency and next-boundary continuity are current;
ordinary clients see its promoted terminal snapshot; the daily schedule is
truthfully enabled or fail-closed paused; all legacy specs remain disabled;
the accepted finding ledger is reconciled; Graphiti memory is durable; and the
terminal chain is pushed to origin main.

Checkpoint P0024-C01 is the current authority.

### Checkpoint P0024-C01 | 2026-08-06

Plan version: 1

State transition:

- `p08_unplanned -> design_freeze_awaiting_independent_review`.

Progress classification:

- `outcome_progress`; the operator-authorized recurrence objective is now a
  bounded repo-native lane and plan with an exact architecture, live ceiling,
  pause path, and definition of done.

Validation evidence:

- CodeGraph is healthy at 342 files, 8,957 nodes, and 20,139 edges;
- structural inspection proves the service daemon constructs only the legacy
  per-spec scheduler, while `TickCoordinator.enqueue_tick()` is the accepted
  synchronous deep interface and `build_tick_runtime()` remains manual-only;
- current installed/runtime/config/SQLite/spec/timer readbacks match the
  Current State above;
- the repo-policy selector reports product-engineering, balanced,
  `repo-product-engineering`, and `already-aligned`.

Subagent status and reconciliation:

- `not_spawned` during plan construction because architecture, bounds, and
  canonical-doc wiring were one critical path; one fresh independent S01
  reviewer is the next bounded unit.

Review disposition summary:

- no findings yet; discovery budget is one broad plan/candidate review and one
  closed-world verification after primary adjudication.

Graphiti write status:

- deferred until the design is independently accepted or terminally stopped.

Authority classification:

- `human_gate`; operator `ok go` explicitly opens the separately governed
  recurrence objective and its bounded live activation envelope.

Next action:

- commit C01/receipt 0074, run planning/goal audits, and submit the frozen plan
  plus current runtime evidence to one fresh independent evaluator before code
  or timer mutation.
