<!-- last30days-work-item:WI-007 -->
# Keep a priority production hotfix path available

State: TRIAGE
Priority: P1
Lane: Hotfix
Parent: WI-000
Blocked by: WI-001

## Problem

A production regression needs a path that cannot be blocked by feature WIP or
confused with ordinary lane deployment authority.

## Outcome / Proposed Solution

A production-impacting defect can move from intake through a current-main fix,
priority validation, staged acceptance, deployment gate, and rollback receipt
without being queued behind feature lanes.

## Acceptance Evidence

- a provider-free drill starts from current `origin/main` in a dedicated
  branch/worktree and records the stable work-item locator;
- the drill identifies affected feature lanes and proves their reconciliation
  point after integration;
- targeted regression, staging identity, production authorization, deployment
  readback, and rollback are distinct gates;
- the reserved hotfix slot does not increase the three-feature WIP limit;
- cleanup preserves exact Git and runtime receipts.

## Non-Goals

No production mutation during the drill and no blanket authority for future
deployments, retries, or provider effects.
