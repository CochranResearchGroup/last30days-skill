# Plan 0090 | Next Wave Launch Registration

State: CLOSED
Lane: P44
Work item: WI-000
Branch: docs/next-wave-launch-registration
Target: main
Integration: merge
Roadmap: P44
Plan version: 1
Date: 2026-09-13
Session owner: coordinator

## Objective

Publish and register restart-safe Packet 1 launch refs and dedicated worktrees
for WI-003 agent questions, WI-008 service quality, and the query-only WI-006
monitor kernel without starting feature implementation in the coordinator.

## Current State

- P33 Packet 1 is integrated and unblocks P36 plus the query-only P40 kernel;
- P37 Packet 1 is independently provider-free;
- P35 remains at its explicit pull-request gate, so P40 follow tracing remains
  excluded;
- three clean plan-only feature refs now exist from exact canonical 87a8cbac;
- GitHub Issues remain read-only, so repo-local work items and the active-lane
  catalog remain the coordination ledger.

## Scope

- verify no competing branch, pull request, or worktree owns the three intents;
- publish one bounded Packet 1 plan on each feature branch;
- update P36/P37/P40 catalog custody and roadmap handoffs to exact refs and
  checkpoints;
- correct already-observed catalog evidence drift for P43 and P35 without
  changing their outcome or authority;
- integrate only the launch registration through the owned-fork pull-request
  path;
- launch one independent top-level Codex session per registered feature lane.

## Non-Goals

- no feature code in the coordinator lane;
- no P35 pull-request retry or merge;
- no installed runtime/database, model, browser/provider, schedule, delivery,
  staging, release, deployment, production, or GitHub Issue/Project mutation;
- no cleanup of earlier worktrees or branches.

## Acceptance Criteria

1. Each feature branch begins at exact canonical 87a8cbac and contains only its
   bounded plan-only launch commit.
2. Each remote ref resolves to the recorded checkpoint and each worktree is
   clean, distinct, and on the intended branch.
3. Catalog P36/P37/P40 entries name current plan, ref, branch, custody,
   dependency, work item, overlap, and checkpoint evidence.
4. Roadmap and runbook provide an exact, bounded handoff for each independent
   top-level session and preserve P35's gate.
5. Planning, lane, patch, Git, and published-ref validation pass before launch.

## Execution Packet

- accountable human owner: repository operator;
- execution and coordination owner: this coordinator session;
- expected writes: three plan-only feature refs, this plan, ROADMAP.md,
  RUNBOOK.md, active-lanes catalog, and temporary plan-authority expectation;
- external effects: owned-fork branch publication and coordinator pull request
  only;
- bounds: three plan commits, one registration pull request, three independent
  top-level sessions, and one closeout;
- terminal condition: all five criteria pass or conflicting custody is
  recorded before implementation;
- authority: routine repo/Git coordination; tracker/runtime/provider effects
  remain unauthorized.

Independent sessions are the selected execution model. Collaboration
subagents are not substitutes for these feature-lane owners.

## Current Checkpoint

### Checkpoint P0090-C01 | 2026-09-13

Plan version: 1

State transition: planned -> active.

Progress classification: outcome_progress; the next three Packet 1 scopes are
bounded and their isolated worktrees exist.

Authority classification:

- `inherited_authority` for plan refs, worktrees, catalog, and PR integration;
- `not_authorized` for tracker, feature implementation in this coordinator,
  runtime, provider, schedule, delivery, staging, release, or production.

Owned changes:

- three plan-only feature refs and isolated worktrees;
- this coordinator plan and the proposed roadmap, runbook, lane catalog, and
  planning-audit projection.

Validation evidence:

- canonical main was clean and equal to origin/main at 87a8cbac;
- Graphiti runtime was healthy; bounded discovery returned 8 facts, 6 nodes,
  and 4 older episodes, so current Git remains authoritative;
- no competing local/remote refs or open pull requests existed for the three
  feature branch names;
- three plan-only refs were created and require final catalog validation.

Subagent Status And Reconciliation:

- no collaboration subagents were spawned; independent top-level sessions have
  not yet started.

Graphiti write status:

- not attempted; the read-only result was advisory and current Git supplies
  the launch evidence.

Next action:

- publish this coordinator checkpoint, register the exact three feature refs,
  validate and merge the projection, then launch the sessions.

Remaining acceptance criteria:

- validate the catalog against the published refs, merge the registration
  through the owned-fork pull-request path, and launch the three sessions.

## Definition Of Done

The three plan-only refs and clean worktrees are canonically discoverable,
their independent top-level sessions have exact bounded handoffs, and no
feature or external effect has started in the coordinator lane.

### Checkpoint P0090-C02 | 2026-09-13

Plan version: 1

State transition: `active -> closed`.

Progress classification: `verified_outcome`; the launch registration is merged
and all three independent owners published clean activation checkpoints.

Authority classification:

- `inherited_authority` for ownership reconciliation, canonical projection,
  validation, branch publication, and pull-request integration;
- `not_authorized` for feature implementation in the coordinator, P35 pull
  request action, tracker, runtime, provider, schedule, delivery, staging,
  release, or production effects.

Owned changes:

- canonical P36/P37/P40 plan, work-item, roadmap, runbook, and catalog
  ownership projections;
- this closeout checkpoint and restoration of the repository active-plan test
  to its durable source-plan count.

Validation evidence:

- launch registration PR 39 merged source `4db386ef` as canonical
  `606272ab82ba2c97d833e8b06e2c1ea4092bac85`;
- P36 activation `c4d985727c39c7cfe2a86a64eae318351eefd5d4`,
  P37 activation `be4dec78db686132496b3b173a55ab534c1827a6`,
  and P40 activation `0253e82dfad36877371cbdaaa41e846560cfbc8a`
  are clean and local/remote equal;
- each activation changed only its branch-local plan after merging exact
  canonical main and passed 10 focused plan-authority tests;
- final canonical planning and active-lane audits remain after rendering this
  ownership projection.

Remaining acceptance criteria:

- none for launch registration; each feature plan retains all Packet 1 product
  acceptance criteria for its owning thread.

Subagent status and reconciliation:

- `not_spawned`; three independent top-level Codex threads own P36, P37, and
  P40, and their exact identifiers are recorded in their plans and runbook.

Graphiti write status:

- `not_written`; read-only discovery was advisory and current Git/PR evidence
  is authoritative.

Next action:

- merge this ownership projection, then resume the same three independent
  threads for their bounded provider-free Packet 1 implementations.

## Stop Rules

- stop on any branch, worktree, pull-request, or shared-surface ownership
  conflict;
- stop before feature implementation in the coordinator;
- stop before P35 pull-request action or any tracker/runtime/provider effect.
