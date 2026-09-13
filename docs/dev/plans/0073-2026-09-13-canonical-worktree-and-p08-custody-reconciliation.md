# Plan 0073 | Canonical Worktree And P08 Custody Reconciliation

State: CLOSED
Lane: P30
Branch: docs/p08-custody-reconciliation
Target: main
Integration: merge
Roadmap: P30
Plan version: 1
Date: 2026-09-13

## Objective

Restore `main` custody to the canonical repository worktree, preserve and
truthfully archive the divergent P08 branch, and recover its missing historical
plan and receipt artifacts without merging obsolete code or policy snapshots.

## Current State

- `/home/ecochran76/workspace.local/last30days-skill` is clean on `main` at
  `af610bb7e91b5d6038949ae08f8324c30090ba2f`, equal to `origin/main`;
- the former ordinary-tick worktree is clean and detached at the same commit;
- `fix/tick-restart-recovery` is clean and published at `378788ba`, but is not
  an ancestor of `main` even though P08's catalog custody says `INTEGRATED`;
- the branch's retry-recourse implementation was re-applied on the later
  `fix/full-tick-recovery` line and extended on `main`, while nine historical
  P08 plan/receipt files remain absent from `main`;
- exact branch tip `378788ba` is preserved locally and remotely as
  `archive/p08-tick-restart-recovery-20260913`.

## Scope

- add a repo-specific canonical-main-worktree rule to `AGENTS.md` and the
  multi-session operating model;
- restore the nine missing historical P08 plan and receipt files byte-for-byte
  from the retained branch;
- change P08 catalog custody from the false `INTEGRATED` claim to an exact
  `ARCHIVED` ref with a bounded disposition;
- record branch/code equivalence evidence and the remaining pre-existing lane
  catalog findings;
- integrate and close this reconciliation through the public fork.

## Non-Goals

- no wholesale merge, rebase, reset, or deletion of
  `fix/tick-restart-recovery`;
- no adoption of its obsolete embedded policy-selector snapshot;
- no cleanup or reclassification of P23, P25, P26, P27, or P28;
- no source-code, installed Skill, service, browser, provider, schedule,
  credential, database, or runtime mutation.

## Acceptance Criteria

1. The canonical repository path is clean on current `main`, and durable policy
   reserves the declared canonical worktree for default-branch integration.
2. Local and remote archive refs both resolve to P08 tip `378788ba` before any
   original branch cleanup is considered.
3. The nine missing historical artifacts on `main` match the archived branch
   byte-for-byte; the current, more complete Plan 0064 is retained.
4. P08's catalog record reports `ARCHIVED` custody with exact archive refs and
   no false claim that its branch tip is an ancestor of `main`.
5. Focused authority, policy-routing, and active-lane validation passes for the
   touched scope, with unrelated existing catalog findings reported rather
   than silently modified.

## Execution Packet

- owner: primary agent;
- critical path: Git ancestry and semantic comparison, archive publication,
  selective artifact restoration, policy and catalog correction, validation,
  public-fork integration, and closeout;
- write surfaces: `AGENTS.md`, policy 0028, P08 active-lane record, historical
  P08 plans/notes, Plan 0073, `ROADMAP.md`, `RUNBOOK.md`, and authority-test
  expectation;
- bound: one reconciliation pass, one validation/remediation pass, one
  integration, and one closeout;
- terminal condition: all five criteria pass or one exact blocker is recorded;
- authority classification: `inherited_authority`; the operator authorized the
  recommended P08 reconciliation after the canonical-worktree correction.

Subagent status: `not_spawned`; Git custody and shared authority form one
serialized reconciliation path.

## Definition Of Done

All five criteria have exact ref, artifact, policy, catalog, validation, and
integration evidence, or the plan records one terminal blocker without
discarding the retained branch or widening into other catalog lanes.

## Current Checkpoint

### Checkpoint P0073-C01 | 2026-09-13

Plan version: 1

State transition: `planned -> active`.

Progress classification: `blocker_reduction`; canonical main custody is
restored, the divergent branch is safely archived, and the bounded restoration
set is identified.

Authority classification:

- `inherited_authority`; this is the operator-authorized reconciliation.

Validation evidence:

- canonical `main` equals `origin/main` at `af610bb7` with a clean status;
- local and remote archive refs both resolve to
  `378788bab8315ebcae84aac90c88a49c98dff621`;
- Git history and changed-line comparison show the P08 retry-recourse code was
  re-applied by `c960e34c` and extended by later integrated Reddit work; the
  stale branch must not be merged wholesale;
- source reconciliation commit `95f6464d` restores all nine missing artifacts
  byte-for-byte, retains the newer Plan 0064, and changes P08's only audit
  finding to `archived_ref` with no P08 problem;
- 13 focused authority and canonical-guidance tests pass, the plan authority
  audit reports no issues, and `git diff --check` passes. The active-lane audit
  still reports only the pre-existing P23/P25/P26/P27 findings outside scope.

Subagent status and reconciliation:

- `not_spawned`; primary-agent Git evidence is authoritative.

Graphiti write status:

- `not_written`; focused discovery returned older background but no current
  P08 integration receipt, so Git and repository artifacts remain authority.

Next action:

- validate restored artifacts, policy routing, P08 archive custody, and the
  unchanged set of unrelated catalog findings, then integrate through the
  public fork.

### Checkpoint P0073-C02 | 2026-09-13

Plan version: 1

State transition: `active -> closed`.

Progress classification: `verified_outcome`; canonical custody, selective
historical restoration, and P08 archive classification are integrated.

Authority classification:

- `inherited_authority`; public-fork integration and closeout complete the
  operator-authorized reconciliation.

Validation evidence:

- pull request 8 merged source tip
  `1b6fe5e094cf277c29b9e69e066688a11f0db2dd` as
  `abf39f35af9ed6f95f1739bae80cf356cd9896e7` on `origin/main`;
- the canonical worktree fast-forwarded cleanly to that exact merge and is
  clean, on `main`, and equal to `origin/main`;
- both archive refs still resolve to P08 tip `378788ba`; all nine restored
  artifacts remain byte-equal to that archive;
- 13 focused tests and the plan authority audit pass. P08's active-lane result
  is exactly `archived_ref` with no P08 problem; the pre-existing
  P23/P25/P26/P27 findings remain outside scope.

Subagent status and reconciliation:

- `not_spawned`; the primary agent retained end-to-end custody.

Graphiti write status:

- `not_written`; integrated Git and repository receipts are authoritative.

Next action:

- none for P30. Retain the archive and address the remaining catalog lanes as
  separate bounded reconciliation work before deleting historical refs or
  worktrees.
