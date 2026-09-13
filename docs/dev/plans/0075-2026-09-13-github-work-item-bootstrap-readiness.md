# Plan 0075 | GitHub Work-Item Bootstrap Readiness

State: OPEN
Lane: P32
Branch: chore/github-work-item-bootstrap
Target: main
Integration: merge
Roadmap: P32
Plan version: 1
Date: 2026-09-13

## Objective

Make the repository ready for a later, explicitly authorized GitHub Issues and
Project activation by pinning the current policy selector, adopting exact
provider-operation controls, and preparing a reviewable product-lane backlog.

## Current State

- the owned public fork is `CochranResearchGroup/last30days-skill`, current
  viewer permission is `ADMIN`, and GitHub Issues are disabled;
- GitHub Projects are available for the owner, but no Project currently exists;
- existing labels are sufficient for defect, documentation, and feature intent;
- policies 0027 and 0028 establish work-item traceability and the multi-session
  operating model but deliberately leave remote tracker activation gated;
- selector release `v0.1.25` adds the missing model-calibration, forge-reporting,
  GitHub-operation, target-registry, and read-only preflight surfaces;
- no GitHub issue, Project, label, repository setting, runtime, service,
  provider, schedule, credential, or deployment mutation has been made.

## Scope

- upgrade the embedded selector from `v0.1.22` to immutable release `v0.1.25`;
- adopt the three missing repo-local policy modules without duplicating an
  existing module identity;
- add an exact read-only target registry and GitHub issue chooser policy;
- define the proposed Project workflow, activation sequence, and stable
  repo-local issue locators;
- prepare one program draft and eight outcome-oriented child drafts for review;
- validate selector, policy, registry, plan, and catalog authority without any
  external issue-tracker mutation;
- publish and integrate the readiness artifacts through the public fork.

## Non-Goals

- no enabling of GitHub Issues;
- no issue, label, Project, milestone, assignment, comment, or closure mutation;
- no publication against upstream `mvanhorn/last30days-skill`;
- no product feature implementation or runtime provisioning;
- no installed Skill, browser, provider, schedule, credential, database,
  deployment, or production change.

## Acceptance Criteria

1. The embedded selector and install record identify `v0.1.25` and immutable
   source commit `b22b1e9f6ca2e1733a3decd4f68e95660aa9b0bb`.
2. Exactly one repo-local policy exists for each adopted module identity and
   `AGENTS.md` names the correct trigger for policies 0029 through 0031.
3. The registry resolves only the owned public fork, allows read only, maps
   only existing labels, and blocks public security reporting.
4. The tracker contract states the six-state workflow, three-feature-plus-
   hotfix WIP rule, Project fields, and gated activation sequence.
5. WI-000 through WI-008 have unique markers, bounded outcomes, acceptance
   evidence, explicit dependencies, and non-goals; the proposed first portfolio
   respects WIP and shared-surface constraints.
6. Read-only live preflight reports the current target accurately while create
   preflight fails closed; selector tests, policy validation, focused authority
   tests, active-lane audit, and `git diff --check` pass.

## Execution Packet

- owner: primary agent;
- critical path: selector pin, policy adoption, target registry, tracker
  contract, work-item drafts, deterministic validation, public-fork integration;
- write surfaces: embedded selector bundle, `AGENTS.md`, policies 0029-0031,
  tracker/registry/work-item docs, Plan 0075, `ROADMAP.md`, `RUNBOOK.md`, and
  plan-authority expectation;
- external effects: Git branch publication and pull-request integration only;
  GitHub issue-tracker and Project mutations remain prohibited;
- bound: one readiness implementation, one validation/remediation pass, one
  integration, and one closeout;
- terminal condition: all six criteria pass or the exact failed gate is
  recorded without remote tracker mutation;
- authority classification: `inherited_authority`; the user approved the repo
  policy/workflow program, while provider mutations remain separately gated.

Subagent status: `not_spawned`; this shared-governance slice has one serialized
owner and the user did not request delegated execution.

## Definition Of Done

All readiness artifacts are integrated on canonical `main`, remote tracker
state remains unchanged, and the operator has a concise review question whose
answer can authorize or revise the publication phase.

## Current Checkpoint

### Checkpoint P0075-C01 | 2026-09-13

Plan version: 1

State transition: `planned -> active`.

Progress classification: `outcome_progress`; provider-neutral readiness is
implemented locally and external mutations remain behind an explicit gate.

Authority classification:

- `inherited_authority` for repository policy, planning, and review drafts;
- `not_authorized` for Issues, Projects, labels, and repository-setting writes.

Validation evidence:

- canonical `main` was clean and equal to `origin/main` at `2c1eaec7` before
  this dedicated worktree was created;
- live read-only preflight found the owned fork with `ADMIN`, Issues disabled,
  Projects enabled, no owner Projects, and only the standard label set;
- selector installation resolved tag `v0.1.25` to immutable source commit
  `b22b1e9f6ca2e1733a3decd4f68e95660aa9b0bb`;
- the selector reports `already-aligned` with zero validation problems; its 102
  bundled tests and 13 focused repository tests pass;
- plan authority passes with two legitimate active plans, the catalog-only
  lane audit reports zero problems, all nine work-item markers are unique, JSON
  parsing and `git diff --check` pass;
- live read-only preflight reports actor `ecochran76`, role `ADMIN`, the exact
  repository, and the expected disabled-Issues gate; create preflight fails
  closed before mutation.

Subagent status and reconciliation:

- `not_spawned`; primary-agent repository and provider readback is authoritative.

Graphiti write status:

- `not_written`; current repository, Git, and live GitHub readback are the
  authoritative evidence for this bootstrap.

Next action:

- publish and integrate the readiness branch, then ask the operator to accept
  or revise the issue graph before any tracker mutation.
