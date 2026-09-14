# Plan 0095 | P36 Packet 2 Launch Registration

State: CLOSED
Lane: P46
Work item: WI-003
Branch: docs/p36-packet2-launch-registration
Target: main
Integration: merge
Roadmap: P46
Plan version: 1
Date: 2026-09-13
Session owner: coordinator

## Objective

Register one restart-safe, provider-free P36 Packet 2 evidence-tracer lane and
hand its dedicated worktree to an independent top-level Codex session without
starting feature implementation in the coordinator.

## Current State

- Plans 0091-0094 and their three Packet 1 features are integrated and closed;
- WI-003 is `READY` for its next bounded packet;
- Plan 0096 is published plan-only at
  `07f96129` on `feat/agent-question-evidence-v2`, based on canonical
  `d4e3cd65`;
- P35 remains at its independent pull-request authorization gate;
- the global Skill install is a stale frozen copy and remains outside this
  source-only launch.

## Scope

- verify exact plan/ref/worktree custody and absence of a competing PR;
- publish the P36/Plan0096 work-item, roadmap, runbook, and active-lane
  projection from a coordinator-owned publication branch;
- record shared manifest/authority ownership and Packet 3/4 boundaries;
- validate and integrate the registration through the owned public fork;
- launch one independent top-level Codex CLI session in the prepared worktree.

## Non-Goals

- no Packet 2 feature implementation in the coordinator;
- no P35 action and no GitHub Issue/Project mutation;
- no installed Skill/service, model, browser/provider, refresh, schedule,
  delivery, release, staging, deployment, or production effect;
- no old-worktree or branch cleanup.

## Acceptance Criteria

1. The Packet 2 plan branch is clean, remote-equal, and based on exact
   canonical `d4e3cd65` with no competing pull request.
2. P36, WI-003, and the active-lane catalog name Plan 0096, its exact branch,
   checkpoint, dependencies, overlap ownership, and effect boundary.
3. Planning, lane-catalog, worktree, Git, and patch validation pass on the
   published registration ref.
4. The registration merges through one owned-fork pull request and canonical
   main is clean and remote-equal afterward.
5. One independent top-level Codex session accepts the lane, records its
   runtime-reported session identity in Plan 0096, opens the plan, and publishes
   a clean activation checkpoint before implementation.

## Execution Packet

- accountable human owner: repository operator;
- coordination owner: current coordinator session;
- expected writes: this plan, P36, WI-003, RUNBOOK.md, active-lane catalog,
  and temporary plan-authority test expectation;
- external effects: Git branch publication and owned-fork PR integration only;
- critical path: freeze coordinator ref, publish registration projection,
  validate, merge, canonical readback, launch independent session;
- terminal condition: all five criteria pass or exact custody/session-launch
  failure is recorded without starting feature work.

Subagent status: `not_spawned`; independent top-level Codex is the selected
lane topology.

## Definition Of Done

Plan 0096 is canonically discoverable at an exact published checkpoint, its
dedicated worktree has one independent top-level owner, and neither the
coordinator nor any installed/runtime/provider surface performs feature work.

## Current Checkpoint

### Checkpoint P0095-C01 | 2026-09-13

Plan version: 1

State transition: `unplanned -> OPEN`.

Progress classification: `outcome_progress`; the next evidence tracer and its
independent execution boundary are explicit and recoverable.

Authority classification:

- `inherited_authority` for routine repository planning, branch publication,
  owned-fork integration, and independent source-only lane launch;
- `human_gate` for P35 and installed/runtime/provider/release/production
  effects;
- `scope_expansion` for Packet 3 worker or Packet 4 public transport behavior.

Evidence:

- canonical main is clean and remote-equal at
  `d4e3cd65f4a6ba79196ba47721245d5ade687322`;
- Plan 0096's dedicated feature worktree is clean and its plan-only branch is
  remote-equal at `07f96129`;
- CodeGraph is current and confirms the real search protocol seam and both
  immutable version stores; Graphiti is healthy but returned only older MCP
  history, so current repository artifacts are authoritative.

Subagent status: `not_spawned`.

Next action: publish this frozen coordinator checkpoint, create the
publication projection, validate and merge it, then launch the independent
Packet 2 session.

### Checkpoint P0095-C02 | 2026-09-13

Plan version: 1

State transition: `OPEN -> CLOSED`.

Progress classification: `verified_outcome`; the registration is canonical and
the replacement independent owner published a clean activation checkpoint
before feature implementation.

Authority classification:

- `inherited_authority` for registration integration, canonical readback, and
  independent source-only session launch;
- all previously named human gates and scope-expansion boundaries remain.

Evidence:

- PR 43 merged the registration as canonical
  `5004df7f228059b2d2c154f1414de83fae16cfd5`;
- canonical main was fast-forwarded cleanly and verified equal to origin/main;
- replacement top-level Codex thread
  `01a09d44-49bf-73b2-a613-aee72c98f471` merged canonical main without
  rebasing, opened Plan 0096, and published activation
  `e566724c461aaf488020b1dc811dadcf44d6b72c` remote-equal;
- the interrupted predecessor `01a09d41-e047-76c3-92b5-229017168752` was
  stopped during preflight after exposing inherited credential values in its
  transcript and made no feature or plan edit; the replacement process was
  launched with those variables removed and has not repeated the exposure;
- activation authority tests and patch hygiene passed; Plan 0096's expected
  branch-local RUNBOOK wiring finding is resolved by this coordinator closeout.

Subagent status: `not_spawned`; the feature owner is a separate top-level
Codex CLI session.

Next action: integrate this activation projection while the independent owner
executes only Plan 0096; rotate the exposed credentials outside repository
scope, and do not place their values in any further transcript or artifact.
