# Plan 0099 | P36 Packet 3 Launch Registration

State: CLOSED
Lane: P48
Work item: WI-003
Branch: docs/p36-packet3-launch-registration
Target: main
Integration: merge
Roadmap: P48
Plan version: 1
Date: 2026-09-14
Session owner: coordinator Codex session

## Objective

Register one restart-safe, provider-free P36 Packet 3 answer-tracer lane and
hand its dedicated worktree to an independent top-level Codex session without
moving feature implementation into the coordinator.

## Current State

- P36 Packet 2 and its closeout are integrated through PRs 45 and 46 at
  canonical main `20a36f91`;
- WI-003 is `READY` for a separately bounded Packet 3;
- Plan 0098 is published plan-only at `77744112` on
  `feat/agent-question-answer-v3`, based on canonical `20a36f91`;
- the Packet 3 worktree is clean and no competing branch or pull request owns
  its exact intent;
- P35 and the frozen global Skill install remain untouched.

## Scope

- verify exact plan/ref/worktree custody and absence of a competing PR;
- publish the P36/Plan 0098 work-item, roadmap, runbook, and active-lane
  projection from this coordinator branch;
- record coordinator ownership of the source manifest and all public
  service/MCP, compatibility, and release surfaces;
- validate and integrate the registration through the owned public fork;
- launch one independent top-level Codex CLI session in the prepared worktree
  with credential-bearing environment variables removed.

## Non-Goals

- no Packet 3 feature implementation in the coordinator;
- no P35 action and no GitHub Issue/Project mutation;
- no real model, installed Skill/service, browser/provider, refresh, schedule,
  delivery, release, staging, deployment, or production effect;
- no Packet 4 public HTTP/MCP implementation;
- no cleanup of unrelated historical worktrees.

## Acceptance Criteria

1. Plan 0098's branch is clean, remote-equal at exact checkpoint `77744112`,
   based on canonical `20a36f91`, and has no competing pull request.
2. P36, WI-003, and the lane catalog name Plan 0098, its branch/checkpoint,
   owner boundary, dependencies, overlaps, and provider-free effect boundary.
3. Planning, lane-catalog, worktree, Git, and patch validation pass on one
   published registration candidate.
4. The registration merges through one owned-fork pull request and canonical
   main is clean and remote-equal afterward.
5. One independent top-level Codex session accepts the lane, records its exact
   runtime-reported thread identity in Plan 0098, opens the plan, and publishes
   a clean activation checkpoint before implementation.

## Expected Write Surface

- this plan;
- compact coordinator projections in ROADMAP.md, RUNBOOK.md,
  `docs/dev/active-lanes.yaml`, WI-003, and the plan-authority test;
- Plan 0098 only on its separately owned feature branch during activation;
- no feature source or runtime artifact.

## Execution Packet

- accountable human owner: repository operator;
- coordination owner: current coordinator session;
- critical path: freeze coordinator plan, publish registration, validate,
  merge, canonical readback, launch sanitized independent session, reconcile
  activation;
- external effects: Git branch publication and owned-fork PR integration only;
- retry bound: one publication/integration retry and one sanitized session
  replacement if startup fails before feature edits;
- terminal condition: all five criteria pass or exact custody/session-launch
  failure is recorded without starting coordinator feature work.

Subagents: `not_planned`; independent top-level Codex is the selected lane
topology.

## Definition Of Done

Plan 0098 is canonically discoverable at an exact published checkpoint, its
dedicated worktree has one independent top-level owner, and neither the
coordinator nor any installed/runtime/provider/model surface performs feature
work.

## Current Checkpoint

### Checkpoint P0099-C01 | 2026-09-14

Plan version: 1

State transition: `unplanned -> OPEN`.

Progress classification: `outcome_progress`; the provider-free Packet 3
outcome and its independent execution boundary are explicit and recoverable.

Authority classification:

- `inherited_authority` for repository planning, branch publication,
  owned-fork integration, and independent source-only lane launch;
- `human_gate` for P35 and installed/runtime/provider/model/release/production
  effects;
- `scope_expansion` for Packet 4 public service/MCP publication.

Evidence:

- canonical main is clean and remote-equal at
  `20a36f91c866d81e03e4bfc521e1d2d270411d16`;
- Plan 0098's worktree and remote are equal at
  `777441129e47f18e60f7956d765929c5e75e687e`;
- CodeGraph confirms the existing queue, lease, fake runner, validator, and
  structured-turn seams; Graphiti is healthy but returned no relevant P36
  memory, so current repository artifacts are authoritative;
- the two completed Packet 2 worktrees were removed only after clean state,
  remote equality, and main ancestry were verified; their branches remain.

Subagent status: `not_spawned`.

Next action: publish this frozen plan checkpoint, add the compact coordinator
projections, validate and merge the registration, then launch the independent
Packet 3 session.

### Checkpoint P0099-C02 | 2026-09-14

Plan version: 1

State transition: `OPEN -> CLOSED`.

Progress classification: `outcome_progress`; PR 47 merged the registration as
canonical commit `487ec89e7a6c99d07f6623646c659111c5fbd270`, and the assigned
lane published activation checkpoint `063c18b7` before source work.

The independent process later exhausted its Codex usage allowance, so the
coordinator explicitly accepted custody and completed the same bounded packet.
No provider, model, browser, installed-runtime, release, or production effect
occurred.

Next action: Plan 0100 owns exact Packet 3 integration and canonical closeout.
