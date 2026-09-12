# Plan 0070 | Refresh Query Head Integration And Install

State: OPEN
Lane: P27
Branch: fix/refresh-query-head-arbitration
Target: main
Integration: merge
Roadmap: P27
Plan version: 1
Date: 2026-09-12

## Objective

Reconcile the source-qualified 0.3.115 query-head repair with current
`origin/main`, integrate it into the public fork, install the exact integrated
candidate, and prove the existing X publication is cache-query-visible without
another provider refresh.

## Current State

- Plan 0069 is source-qualified at `857ace5`.
- The branch is clean, local-only, 15 commits ahead and two behind current
  `origin/main`; the two target commits are recurring-Reddit documentation.
- Installed service 0.3.114 is ready but still selects the older tick head.

## Scope

- merge current `origin/main` into the clean repair lane while preserving
  existing checkpoints;
- rerun affected and package/install gates after reconciliation;
- publish and integrate through the normal fork workflow;
- install the exact integrated 0.3.115 service and synchronize the frozen
  user-scoped Skill copy;
- verify service identity, systemd state, and one cache-only X readback.

## Non-Goals

- no new X/provider acquisition, recurring tick, schedule change, profile or
  browser mutation, upstream pull request, or formal public release;
- no cleanup or modification of the dirty retry-recovery worktree.

## Acceptance Criteria

1. The reconciled branch is clean and contains current `origin/main`.
2. Required provider-free source and package/install gates pass.
3. The fork target contains the repair through its normal integration path.
4. Installed service reports 0.3.115 with an exact accepted manifest and the
   user-scoped Skill copy matches the integrated source.
5. One cache-only `AI agents` X query selects the newer retrieval index and
   returns its matching published evidence; no refresh occurs.

## Execution Packet

- owner: primary agent;
- critical path: reconcile, validate, integrate, install, cache-only readback;
- write surfaces: this branch, fork refs/PR, user-scoped Skill/service install,
  plan, runbook, and closeout receipt;
- bound: one reconciliation attempt, one validation repair pass, one guarded
  install, and one cache-only acceptance query;
- terminal condition: installed acceptance or one exact fail-closed blocker;
- authority classification: `inherited_authority`; the operator approved the
  recommended integration and installation path with “Ok go”.

Subagent status: `not_spawned`; current orchestration policy prohibits
delegation.

## Definition Of Done

All five acceptance criteria have current commit, runtime, and query receipts,
or the plan records the exact terminal blocker without widening effects.

## Checkpoint P0070-C01 | 2026-09-12

State transition: `active -> integration_ready`.

Progress classification: `blocker_reduction`; current `origin/main` merged
cleanly and 66 affected tests pass on reconciled commit `a168115e`.

Acceptance state: criteria 1-2 pass. Fork integration, Skill/service install,
and cache-only acceptance remain.
