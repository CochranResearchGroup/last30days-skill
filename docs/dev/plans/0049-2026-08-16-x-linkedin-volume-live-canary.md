# Plan 0049 | X And LinkedIn Volume Live Canary

State: OPEN
Roadmap: P08
Plan version: 1
Date: 2026-08-16

## Objective

Run exactly one receipt-only manual canary against the newly increased X and
LinkedIn lanes, then report truthful observed, accepted, rejected, timing, and
failure evidence without consuming or changing the recurring daily schedule.

## Current State

- Plan 0048 installed X and LinkedIn ten-item ceilings with X using
  `x_agent_browser` and LinkedIn using topic/content
  `linkedin_agent_browser`;
- the service and SQLite are healthy, `daily-default` remains ready for the
  Aug 17 UTC boundary, and no provider attempt is active;
- exact two-lane preflight C01 is ready but has not been enqueued.

## Scope

- use schedule identity `plan-0049-x-linkedin-volume-canary` for the completed
  `2026-08-15T00:00:00Z` to `2026-08-16T00:00:00Z` interval;
- select exactly X and LinkedIn from private config revision
  `operator-20260816-increase-x-linkedin-volume-v1`;
- permit exactly one provider attempt per lane, ten accepted items per lane,
  50 requests and 120 wall seconds per lane, zero cost, and zero model tokens;
- stop after the first terminal tick receipt, including partial success,
  source-local failure, or fail-closed refusal.

## Non-Goals

- do not retry, run YouTube/Reddit/Facebook, change configuration, change the
  browser/profile, send an ad hoc message, or alter `daily-default`.

## Acceptance Criteria

1. The preflight binds exactly two lanes and the expected limits to a unique
   prospective tick ID.
2. Enqueue consumes that exact tick once and reaches a durable terminal state
   without retry or fallback.
3. Source-local observed/accepted/rejected counts and failure/timing evidence
   are read back from SQLite and reported without overstating the ten-item
   ceilings as guaranteed yield.
4. `daily-default` retains its config digest, next boundary, prior tick, and
   ready state; timer ticks and schedule events do not change.

## Definition Of Done

- exactly one preflight-matching tick is terminal, both source receipts and
  post-effect scheduler invariants are recorded, the plan and P08 close, and
  the result is reported to the operator without retry.

### Checkpoint P0049-C01 | 2026-08-16

Plan version: 1

State transition:

- `higher_volume_x_linkedin_schedule -> canary_ready`.

Progress classification:

- `outcome_progress`; exact live-canary guards are satisfied and no provider
  effect has occurred yet.

Validation evidence:

- preflight status is `ready` for prospective tick
  `tick-c4f042016a7f05f7f076fa195c2d6c98`, config digest
  `sha256:84837d211822d569906b979ef776da79e8c798b15142d687567cace3fe49c3b6`;
- manifest contains exactly `x_agent_browser` and
  `linkedin_agent_browser`, one attempt and ten items each, aggregate two
  attempts, 100 requests, 20 items, 240 wall seconds, zero cost/model use;
- service 0.3.47/schema 16 is active/ready, SQLite quick check is `ok`, no
  provider attempt is active, and `daily-default` is ready for
  `2026-08-17T00:00:00Z` before effect.

Authority classification:

- `inherited_authority`; the operator explicitly requested trying the new X
  and LinkedIn volume now and receiving a report.

Subagent status:

- `not_spawned`; current orchestration policy prohibits delegation.

Next action or stop reason:

- enqueue the exact preflight once, poll only that tick to a terminal receipt,
  read back its two source outcomes and post-effect scheduler invariants, then
  stop without retry.
