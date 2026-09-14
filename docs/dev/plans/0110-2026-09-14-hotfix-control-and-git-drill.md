# Plan 0110 | Hotfix Control And Git Drill

State: PLANNED
Lane: P38
Work item: WI-007
Branch: feat/hotfix-control-v1
Target: main
Integration: merge
Roadmap: P38
Plan version: 1
Date: 2026-09-14
Requested model route: gpt-6-astra, high reasoning
Effective runtime model: unknown until reported

## Objective

Implement WI-007 provider-free Packets 1-2 as a strict dormant hotfix state
machine plus disposable-Git integration drill, without activating a real
incident or touching any installed/runtime/production state.

## Current State

The accepted architecture defines case, candidate, reconciliation, staging,
authorization, deployment, rollback, and closeout boundaries. No controller,
drill, branch, runtime, artifact, incident, or production mutation exists.

## Scope

- implement strict contracts, transitions, conflict matrix, fake Git/runtime/
  review adapters, dormant-slot, and one-hotfix invariants;
- use disposable repositories/worktrees to prove exact-main branching,
  priority integration receipts, affected-lane pause/reconciliation, divergence
  failure, and exact cleanup;
- distinguish integrated, staging-accepted, deploy-authorized, verified,
  rolled-back, cancelled, and blocked states without granting effects;
- keep every fixture inside its temporary root and network/provider free.

## Non-Goals

- no real incident, hotfix branch, GitHub mutation, build/install, service
  process, staging, deployment, rollback, browser/provider, credential, release,
  schedule, or production action;
- no Packet 3 runtime/release drill or Packet 4 operator closeout.

## Acceptance Criteria

1. Dormant state owns zero resources/authority and activation rejects ambiguous
   case, stale base, dirty main, second hotfix, missing rollback evidence, and
   unregistered overlap.
2. Strict receipts and state transitions prevent integration, staging,
   authorization, deployment, verification, rollback, and closeout from being
   collapsed or skipped.
3. Disposable Git drills prove priority integration and every affected feature
   is classified unaffected, reconciled, paused, superseded, or cancelled.
4. Divergence and cleanup failures fail closed; cleanup targets only exact
   fixture-owned paths/refs.
5. Focused and safe-fallback provider-free suites pass with the real canonical
   repo and production service unchanged.

## Definition Of Done

All five criteria pass at one published checkpoint suitable for reviewed PR
integration, or one exact blocker is recorded without beginning Packet 3.

## Stop Rules

- stop before any non-disposable Git effect, real incident, runtime/process,
  artifact, installed database, provider/browser, issue, release, staging,
  deployment, rollback, or production mutation;
- stop and notify the coordinator before changing shared release, installer,
  manifest, roadmap, runbook, or catalog surfaces.
