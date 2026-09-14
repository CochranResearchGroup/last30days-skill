<!-- last30days-work-item:WI-007 -->
# Keep a priority production hotfix path available

State: READY
Priority: P1
Lane: Hotfix
Parent: WI-000
GitHub issue: https://github.com/CochranResearchGroup/last30days-skill/issues/61
Blocked by: none for Packets 1-2; staging/runtime drill by WI-001; real deployment by incident-specific operator authority
Architecture: docs/dev/notes/0122-2026-09-13-reserved-production-hotfix-path-architecture.md
Implementation plan seed: docs/dev/plans/0081-2026-09-13-reserved-production-hotfix-path-architecture-and-lane-handoff.md
Last completed plan: docs/dev/plans/0110-2026-09-14-hotfix-control-and-git-drill.md
Active plan: none
Branch: none

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

## Ready Handoff

Assign one independent top-level lane session. Start from current
`origin/main`, create and register `feat/production-hotfix-path-v1`, and
implement Packet 1 from the architecture note: strict case, candidate,
reconciliation, staging, authorization, deployment, and closeout contracts;
state transitions; conflict matrix; fake Git/runtime/review adapters; dormant-
slot and single-hotfix invariants; and provider-free tests. Do not declare an
incident, create an actual hotfix branch, build/install a release, start or
signal a service, use GitHub Issues/provider/browser/credentials, or touch
staging/production in Packet 1.

Provider-free Packets 1-2 were activated at checkpoint `28c721e0` under Plan
0110 and completed strict control contracts plus disposable-Git drills; the
real reserved slot remains dormant and owns no resource or effect.

Provider-free Packets 1-2 integrated through PR 79 at canonical `fae31198`
after closing the independent-review containment finding. Next work is a
separately planned isolated runtime/release drill; the real slot stays dormant.
