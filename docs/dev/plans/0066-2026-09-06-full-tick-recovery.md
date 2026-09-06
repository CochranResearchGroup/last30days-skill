# Plan 0066 | Full Tick Recovery

State: OPEN
Lane: P26
Branch: fix/full-tick-recovery
Target: fix/installed-service-command
Integration: fast-forward
Plan version: 1
Date: 2026-09-06

## Objective

Repair and retry until one complete all-enabled-source tick succeeds, using at
most five full attempts and waiting at least 300 seconds after terminalization
before starting the next attempt. This is the operator's explicit goal.

## Current State

Service 0.3.110 is installed. Prior diagnosis reproduced a zero-wall-budget
LinkedIn retry contract error that aborts Reddit. LinkedIn lacks a collection
deadline that leaves room for returning results; Reddit has historical
browser-view acquisition failures. No attempt under this new authority has run.

## Scope

One primary owner, serialized work, no delegated agents. Repair admission,
LinkedIn deadline/result handling, and exact-profile Reddit acquisition only as
current evidence requires. Retain the four enabled sources, target selectors,
item ceilings, pacing, privacy, source quality, and aggregate cost limits.
Build/test/install each repair before its bounded live attempt.

## Definition Of Done

A durable terminal `complete` tick with all four enabled lanes successful,
retained evidence and promoted snapshot, healthy post-run service/schedule, and
no abandoned active work. Source changes tested, committed, published, and
installed. Verify every attempt against the durable ledger and 300-second gap.
No weakening acceptance to terminal failure or `complete_degraded`.

## Non-Goals

No unrelated browser/profile cleanup, auth bypass, extra source scope, increased
cost ceilings, weakened scraping pacing, or more than five full tick attempts.
If all five fail, retain the goal as unmet with exact remaining blocker.

## Execution Control

`docs/dev/notes/0066-full-tick-attempts.json` is the attempt ledger. Reserve an
ordinal before enqueue, retain tick identity/process handle, then record the
terminal receipt and next eligible UTC time. No blind retries of an observed
running tick. Checkpoint after each repair/install/attempt cycle. Inherit this
ledger across continuations. Repair work may use the five-minute cooldown.

### Checkpoint P0066-C01 | 2026-09-06

Plan version: 1

- Current authority: five new full attempts, minimum five-minute gaps.
- State: diagnosed -> repair; zero attempts consumed.
- Prior diagnostic turn: outcome_progress (reproduced zero-budget crash).
- Next: fix budget admission and preserve LinkedIn output before worker timeout.

Authority classification:

- `inherited_authority`
