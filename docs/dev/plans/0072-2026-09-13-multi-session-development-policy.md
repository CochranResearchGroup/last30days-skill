# Plan 0072 | Multi-Session Development Policy

State: CLOSED
Lane: P29
Branch: docs/multi-session-development-policy
Target: main
Integration: merge
Roadmap: P29
Plan version: 1
Date: 2026-09-13

## Objective

Make the agreed multi-session development philosophy durable and discoverable
for every new repository agent while repairing the current policy-entry drift.

## Current State

- repository policy already governs plans, worktrees, integration, active
  lanes, testing, runtimes, and reconciliation, but it does not define the
  top-level coordinator/lane-session model as one coherent operating contract;
- `AGENTS.md` points to 26 nonexistent policy paths, `0027` through `0052`,
  which duplicate the identities already present in `0001` through `0026`;
- GitHub Issues is the intended future coordination surface but is not enabled,
  configured, or authorized for mutation in this slice.

## Scope

- remove dangling duplicate policy pointers from `AGENTS.md`;
- adopt tracker-neutral work-item traceability with an explicit GitHub
  transition gate;
- add a repository-specific multi-session development operating model;
- route new agents to the operating model from `AGENTS.md`;
- record the decision in the roadmap and runbook and validate the repository
  authority contract.

## Non-Goals

- no GitHub Issues, Projects, labels, templates, or branch-protection changes;
- no production, staging, development, browser, provider, schedule, service,
  installation, or credential mutation;
- no feature-lane implementation and no permanent `develop` branch;
- no rewrite of existing policies beyond repairing their stale wire-in.

## Acceptance Criteria

1. Exactly one existing file is wired for every adopted policy identity and no
   `AGENTS.md` policy pointer is dangling.
2. Durable policy defines coordinator and lane-session ownership, shallow
   subagent use, three-feature-plus-hotfix capacity, branch/worktree discipline,
   shared-authority ownership, runtime isolation, serialized live canaries, and
   restart-safe request-to-closeout flow.
3. Work-item policy distinguishes roadmap, tracker, plan, lane catalog,
   review, Git, test, deployment, and receipt authority and truthfully gates
   the future GitHub transition.
4. Planning, repository-authority, and policy-routing validation pass without
   touching an installed or live runtime.

## Execution Packet

- owner: primary agent;
- critical path: policy fit review, routing repair, durable policy and plan,
  deterministic validation, public-fork integration;
- write surfaces: `AGENTS.md`, two policy files, Plan 0072, `ROADMAP.md`,
  `RUNBOOK.md`, and the plan-authority expectation test;
- bound: one documentation implementation pass, one validation/remediation
  pass, and one integration pass;
- terminal condition: all four criteria pass or one exact blocker is recorded;
- authority classification: `inherited_authority`; the operator explicitly
  requested creation or modification of repository policy.

Subagent status: `not_spawned`; this is one tightly coupled shared-authority
policy slice with no useful independent write lane.

## Definition Of Done

The policy and routing are internally consistent, deterministically validated,
and integrated into the public fork's `main`, or the plan records one exact
terminal blocker without enabling the external tracker or mutating a runtime.

## Current Checkpoint

### Checkpoint P0072-C01 | 2026-09-13

Plan version: 1

State transition: `planned -> active`.

Progress classification: `outcome_progress`; the philosophy is expressed in
one durable operating-model policy, tracker transition is truthful, and stale
routing is repaired on the source candidate.

Authority classification:

- `inherited_authority`; the operator requested this repo-policy change.

Validation evidence:

- policy pointers, plan authority, documentation syntax, and Git diff checks
  pass on the source candidate.

Subagent status and reconciliation:

- `not_spawned`; the primary agent owns this shared-authority edit.

Graphiti write status:

- `not_written`; repository policy, plan, and runbook are the authoritative
  durable record.

Next action:

- integrate the validated documentation candidate through the public fork,
  record the exact merge receipt, and close Plan 0072/P29 before using the new
  model to bootstrap the work-item tracker.

### Checkpoint P0072-C02 | 2026-09-13

Plan version: 1

State transition: `active -> closed`.

Progress classification: `verified_outcome`; the policy source is integrated
into the public fork and all acceptance criteria pass.

Authority classification:

- `inherited_authority`; public-fork integration and durable closeout complete
  the operator-requested policy change.

Validation evidence:

- pull request 6 merged source commit `901c5216fb0045961d29ba877f9c45acd94e7107`
  as `84eb9ee002fc47f0be2e680c93d88792ccfc989d` on `origin/main`;
- the source commit is an ancestor of current `origin/main`;
- focused plan-authority and canonical-guidance tests pass, the authority audit
  reports no issues, every wired policy path exists, policy filename identities
  are unique, and `git diff --check` passes.

Subagent status and reconciliation:

- `not_spawned`; the primary agent retained ownership through integration and
  closeout.

Graphiti write status:

- `not_written`; integrated repository policy, this plan, and the runbook are
  the authoritative record.

Next action:

- none for P29. A separately authorized successor may enable and configure the
  GitHub work-item surface before the first parallel product lanes open.
