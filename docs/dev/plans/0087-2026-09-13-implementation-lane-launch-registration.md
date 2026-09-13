# Plan 0087 | Implementation Lane Launch Registration

State: OPEN
Lane: P41
Work item: WI-000
Branch: docs/implementation-lane-launch-registration
Target: main
Integration: merge
Roadmap: P41
Plan version: 1
Date: 2026-09-13

## Objective

Publish and register restart-safe Packet 1 launch refs and dedicated worktrees
for WI-002 search, WI-001 isolated runtime, and WI-004 X follows without
starting feature implementation in the coordinator session.

## Current State

- all eight feature/hotfix work items have accepted architecture and are
  `READY` with explicit dependencies;
- no top-level implementation session, feature PR, or implementation custody
  existed at the start of this slice;
- three plan-only refs now exist from canonical `origin/main` and their clean
  dedicated worktrees are staged for session handoff;
- GitHub Issues remain provider-disabled, so repo-local work items and the lane
  catalog remain the coordination ledger.

## Scope

- verify no competing owned-fork branch/PR/worktree exists;
- publish one bounded Packet 1 plan on each feature branch;
- update P33/P34/P35 catalog custody and roadmap handoffs to exact refs/SHAs;
- record shared overlaps and coordinator ownership;
- integrate only the launch registration through a PR.

## Non-Goals

- no feature code, runtime provisioning, installed mutation, provider/browser
  access, schedule, staging, release, or production;
- no GitHub Issue/Project mutation while activation remains disabled;
- no substitution of subagents for the chosen top-level session model.

## Acceptance Criteria

1. Each branch begins at exact canonical `46233ba1` and contains only its
   Packet 1 plan commit.
2. Each remote ref resolves to the recorded checkpoint and each worktree is
   clean, distinct, and on the intended branch.
3. Catalog P33/P34/P35 entries name current plan/ref/branch/custody/dependencies,
   work item, overlaps, and checkpoints.
4. Roadmap/runbook handoffs give one exact start action per session.
5. Plan authority, active planning, active lane, patch, and focused tests pass.

## Execution Packet

- accountable human owner: repository operator;
- execution and coordination owner: coordinator session;
- expected writes: three plan-only feature refs; Plan 0087; ROADMAP.md;
  RUNBOOK.md; active-lanes catalog; plan-authority fixture;
- external effects: owned-fork branch publication and coordinator PR only;
- bounds: three plan commits, one registration commit/PR, one closeout;
- terminal condition: all criteria pass or conflicting custody is recorded;
- review bound: one deterministic reconciliation pass;
- authority: routine repo/Git coordination; tracker/runtime/provider effects
  remain unauthorized.

Subagents: `not_spawned`; top-level lane sessions must be opened separately by
the operator/client and are not emulated with subagents.

## Definition Of Done

The three plan-only refs and clean worktrees have exact shared custody, the
canonical catalog and roadmap point to them, and no implementation or external
effect has started in the coordinator session.

## Current Checkpoint

### Checkpoint P0087-C01 | 2026-09-13

Plan version: 1

State transition: `planned -> active`.

Progress classification: `outcome_progress`; three feature lanes now have
published, bounded, recoverable start refs instead of chat-only handoffs.

Authority classification:

- `inherited_authority` for plan refs, worktrees, catalog, and PR integration;
- `not_authorized` for tracker, feature implementation, runtime, provider,
  schedule, staging, release, or production.

Validation evidence:

- canonical `main == origin/main == 46233ba1` and was clean;
- owned fork had no open PRs and Issues were provider-disabled;
- initial active-lane audit passed with 15 catalog entries;
- launch commits are `05955f75` (WI-002), `8be96fb0` (WI-001), and
  `5d0acd12` (WI-004), each pushed to its exact owned-fork ref;
- final catalog and focused validation remain to run after rendering.

Subagent status and reconciliation:

- `not_spawned`; no implementation work was delegated or started.

Graphiti write status:

- `graphiti_write_pending`; bounded read discovery found no current launch
  state and no write was queued behind degraded ingestion.

Next action:

- validate/integrate this registration, close Plan 0087/P41, then have the
  client open one top-level Codex session in each prepared lane worktree.

## Stop Rules

- stop on any branch/worktree/PR ownership conflict;
- stop before implementation or external/runtime effects;
- stop before tracker mutation without explicit activation authority.
