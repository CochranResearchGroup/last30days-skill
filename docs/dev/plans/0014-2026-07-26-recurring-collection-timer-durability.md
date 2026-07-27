# Plan 0014 | Recurring collection timer durability

State: PLANNED
Roadmap: P02
Date: 2026-07-26
Predecessor: Plan 0011

## Objective

Prove that one low-risk public-source collection specification survives two
scheduled intervals and a service restart while preserving cursor continuity,
budgets, immutable deduplication, coverage, and an explicit paused terminal
state.

## Current State

- Plan 0011 proved a bounded timer and restart path, then paused the acceptance
  spec.
- No recurring authenticated timer is enabled.
- A successor proof is needed before expanding recurring hydration beyond the
  original acceptance fixture.

## Scope

- create or revise one public-source collection spec with explicit item, time,
  network, cost, retention, and access bounds;
- execute two consecutive due intervals with one service restart between them;
- prove scheduled-run identity, cursor/watermark continuity, deduplication,
  coverage, gaps, source health, and yield;
- pause the spec and verify no later automatic run occurs.

## Non-Goals

- authenticated-source scheduling;
- broad hydration, multiple specs, or production cadence selection;
- changing P01 authority, publication semantics, or access partitions;
- stochastic assessment as a prerequisite for raw publication;
- leaving the acceptance timer enabled.

## Dependencies And Owned Surfaces

- Depends on P01 immutable versions/provenance and existing P02 scheduler
  authority.
- Expected writes are focused scheduler/supervisor tests if a defect is proved,
  one versioned public collection spec, durable run ledgers, and closeout docs.

## Execution Packets

1. Select the public source and freeze the bounded spec revision.
2. Run interval one and preserve its run/job/publication receipt.
3. Restart the service, run interval two, and prove continuity.
4. Pause the spec, prove quiescence, and close out.

## Bounds And Gates

- maximum implementation attempts per packet: 2;
- maximum review/rework cycles: 1;
- maximum hardening-only checkpoints: 1;
- active-agent concurrency: 1;
- exactly one spec, two due intervals, and one planned service restart;
- stop on budget escape, duplicate interval identity, cursor regression,
  cross-partition publication, or inability to pause.

## Acceptance Criteria

- both intervals bind to immutable spec revisions and distinct due boundaries;
- replay of a due boundary returns the same durable run rather than duplicating
  work;
- the restart preserves cursor/watermark and lease safety;
- identical content reuses immutable versions while new observations create
  sightings and coverage;
- health and yield are separately observable;
- the final spec revision is disabled and no later timer job appears.

## Validation

- focused collection, scheduler, supervisor, publication, and restart tests;
- installed-runtime run/job/spec/coverage readbacks;
- planning audit, database integrity checks, and `git diff --check`.

## Definition Of Done

The two-interval restart proof passes and the acceptance spec is durably paused,
or the packet stops at the first typed safety failure with no authenticated
timer enabled.
