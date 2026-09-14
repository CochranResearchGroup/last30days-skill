# Plan 0097 | P36 Packet 2 Integration Reconciliation

State: OPEN
Lane: P47
Work item: WI-003
Branch: integration/p36-packet2-reconciliation
Target: main
Integration: merge
Roadmap: P47
Plan version: 1
Date: 2026-09-13
Session owner: coordinator Codex session

## Objective

Review and integrate exact P36 Packet 2 checkpoint
`4e9370178bb7340c7269a34b46549a1b67644735`, close one partition-integrity
finding, refresh the source runtime manifest, and reconcile all canonical
planning projections without producing an installed or live runtime effect.

## Current State

- canonical `main` is clean and remote-equal at
  `62f187298182ec319b448ee2de0f936c55cb2ea7`;
- the feature branch is clean and remote-equal at exact checkpoint
  `4e9370178bb7340c7269a34b46549a1b67644735`;
- delegated validation reports 5 focused, 53 affected, and 2,843 comprehensive
  tests collected with 2,836 passed and 7 skipped;
- primary review accepts the immutable-version and fail-closed design but finds
  that both version-to-parent joins must also require equal access partitions;
- `service/runtime-manifest.json`, RUNBOOK, roadmap, work item, and lane catalog
  remain coordinator-owned joins.

## Scope

- merge the exact feature checkpoint without rebase or history rewrite;
- add one regression proving mismatched parent/version partitions are
  unavailable, then constrain both legacy and temporal parent joins;
- correct Plan 0096's session owner to the exact runtime thread identifier;
- refresh and commit the source runtime manifest for changed/additive modules;
- run focused, affected, comprehensive, compilation, package, planning, lane,
  and patch-hygiene validation;
- reconcile Plan 0096/P36/WI-003 and close this integration plan through the
  fork's protected-main pull-request workflow.

## Non-Goals

- no public HTTP/MCP tool, model worker, provider, browser, acquisition,
  installed runtime/database, schedule, delivery, tracker, staging,
  production, release, or version effect;
- no P35 pull-request, merge, branch, worktree, or gate change;
- no Packet 3 or Packet 4 implementation.

## Acceptance Criteria

1. Exact feature checkpoint `4e937017` is preserved in integration ancestry.
2. Both evidence storage families fail closed when the immutable version and
   its parent identity row disagree on access partition.
3. The source manifest is current and the reproducible runtime package builds
   twice with one digest; nothing is installed.
4. Focused and comprehensive repository tests, compilation, planning, lane,
   and patch-hygiene checks pass on the integration candidate.
5. Canonical projections close Plan 0096/P36 Packet 2 and P47, return WI-003 to
   `READY`, and name Packet 3 as a separate future planning action.

## Execution Packet

- owner: coordinator Codex session;
- critical path: plan checkpoint, exact merge, closed-world remediation,
  manifest refresh, validation, projection closeout, PR merge, canonical
  readback;
- retry bound: one remediation pass and one infrastructure-only retry per
  validation tier;
- terminal condition: all five criteria pass at one merged canonical commit or
  the exact blocking gate is recorded without widening scope.

## Current Checkpoint

### Checkpoint P0097-C01 | 2026-09-13

State transition: `unplanned -> OPEN`.

Progress classification: `blocker_reduction`; integration custody and the sole
accepted review finding are frozen before source reconciliation.

Next action: publish this plan checkpoint, merge exact feature checkpoint
`4e937017`, and execute only the closed-world partition-join remediation and
coordinator-owned joins above.
