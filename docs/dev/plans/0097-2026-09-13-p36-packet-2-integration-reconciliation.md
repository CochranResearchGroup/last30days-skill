# Plan 0097 | P36 Packet 2 Integration Reconciliation

State: CLOSED
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

## Definition Of Done

The exact feature ancestry plus the partition-join repair and current source
manifest are merged through a reviewed PR, canonical main is clean and
remote-equal, and all plan, lane, work-item, validation, and non-effect claims
are reconciled to that merge receipt.

## Current Checkpoint

### Checkpoint P0097-C01 | 2026-09-13

Plan version: 1

State transition: `unplanned -> OPEN`.

Progress classification: `blocker_reduction`; integration custody and the sole
accepted review finding are frozen before source reconciliation.

Authority classification:

- `inherited_authority` for exact feature integration, closed-world repair,
  source-manifest refresh, validation, repository projections, and fork PR;
- `human_gate` for all installed/runtime/provider/release/production effects
  and for P35;
- `scope_expansion` for Packet 3 worker or Packet 4 public transport behavior.

Next action: publish this plan checkpoint, merge exact feature checkpoint
`4e937017`, and execute only the closed-world partition-join remediation and
coordinator-owned joins above.

### Checkpoint P0097-C02 | 2026-09-13

Plan version: 1

State transition: `integration_pending -> integration_validated`; Plan 0097
remains `OPEN` pending owned-fork review and canonical merge.

Progress classification: `outcome_progress`; the exact Packet 2 ancestry and
the coordinator's closed-world remediation are joined at a clean published
candidate.

Authority classification:

- `inherited_authority` for publishing the immutable-candidate projection and
  opening/merging the owned-fork integration PR;
- `human_gate` remains in force for P35 and every installed/runtime/provider/
  release/production effect;
- `scope_expansion` remains in force for Packet 3 and Packet 4 behavior.

Integration and validation evidence:

- feature checkpoint `4e9370178bb7340c7269a34b46549a1b67644735` is preserved
  through merge `5b4b42c4`;
- the parent/version partition test failed with both rows exposed as
  `available`, then passed after both SQL joins required equal partitions;
- the source manifest contains the additive resolver and current hashes for
  both changed question modules;
- 6 focused and 54 affected tests pass; all 2,844 collected repository tests
  pass with the existing seven skips; Python compilation, plan authority,
  active planning, and patch-hygiene checks pass;
- two service `0.3.116` source packages are byte-identical at SHA-256
  `bfaa5fe7ba3d91f7da63a47041362ccfb9626befd361dc4b37756c9a40e23ccb`;
- integration checkpoint `ddcb4201fc75463fa0aba59925343ed2530036ea` is
  clean and remote-equal.

Boundary evidence: no installed runtime/database, provider, browser, model,
public HTTP/MCP, schedule, delivery, release, tracker, staging, production, or
P35 effect occurred.

Next action: publish this projection branch, validate the lane catalog against
the immutable integration ref, then open the owned-fork integration PR.

### Checkpoint P0097-C03 | 2026-09-13

Plan version: 1

State transition: `OPEN -> CLOSED`.

Progress classification: `outcome_progress`; PR 45 merged the reviewed Packet
2 candidate into canonical main.

Authority classification:

- `inherited_authority` for the closeout-only canonical projections and Git
  readback;
- `human_gate` remains in force for P35 and every installed/runtime/provider/
  release/production effect;
- `scope_expansion` remains in force for Packet 3 and Packet 4 behavior.

Integration receipt:

- PR 45 merged as canonical commit
  `e4823ac72532b1c2c87442ca76419827b2cfb268`;
- that merge contains exact feature checkpoint `4e937017` and validated
  integration checkpoint `ddcb4201`;
- P36 and P47 are integrated, and WI-003 returns to `READY` for a separately
  planned Packet 3.

Boundary evidence: no installed runtime/database, provider, browser, model,
public HTTP/MCP, schedule, delivery, release, tracker, staging, production, or
P35 effect occurred.

Next action: merge the closeout-only projection PR, verify canonical main is
clean and remote-equal, then plan Packet 3 separately if the operator continues
the P36 lane.
