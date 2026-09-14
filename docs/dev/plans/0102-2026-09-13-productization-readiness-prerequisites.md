# Plan 0102 | Productization Readiness Prerequisites

State: PLANNED
Lane: P51
Work item: WI-009
Branch: docs/productization-prerequisite-gate
Target: main
Integration: merge
Roadmap: P51
Plan version: 3
Date: 2026-09-13
Execution owner: unassigned

## Objective

Clear the accepted review findings and prove a coherent development release
before any new product feature packet begins.

## Current State

- canonical `main` is clean and remote-equal at
  `a9dcacfa01504b058dae7420d899a30db57e26dd`;
- stored-post search, saved monitors, quality tracing, the isolated-runtime
  doctor, and three question-answering packets are integrated in source;
- comprehensive Python and MCP Go tests pass, but focused reproduction found
  that one malformed structured answer escapes the runner and remains leased,
  and the deterministic evidence-only path ignores `max_answer_characters`;
- GitHub Issues are enabled. `AGENTS.md` and `docs/agents/issue-tracker.md`
  initially described them as disabled, but PR 51
  corrected the authority boundary, and WI-000 through WI-009 are now live as
  issues #52 through #61 with exact repo-local mappings;
- P35 tailored follows is clean and remote-equal at
  `d2c9f8ebfa79e99eb501910c7d606ce3bcbcf07d`, but is 75 commits behind the
  reviewed mainline and has no pull request. The prior issue-registry PR gate
  was a category error and is removed by this revision;
- production is the only running service. It reports service `0.3.116`, schema
  17, and installed manifest `19707a469eb58c21ca4c5b43a0bfbfb6cac4b0f5a5310480b01b1a3f652429e8`;
  source also says `0.3.116` but has a different 139-file manifest
  `9494e8129b13875057dade22afb00935748cf4336b80281423d330a192aa0050`.

## Scope And Ordered Packets

1. **Question contract repair.** Convert every contract-construction failure
   from structured worker output into a safe durable terminal rejection and
   enforce the total answer-character bound in the direct evidence-only path.
2. **Tracker authority reconciliation.** Correct the contradictory current-state
   guidance without granting issue or pull-request mutation authority.
3. **P35 reconciliation and integration.** Reconcile tailored follows after the
   corrective mainline lands, rerun combined tests, inspect the published diff,
   and use the normal governed PR path.
4. **Versioned development release.** Assign a new service version, update
   compatibility and release documentation, build a deterministic artifact,
   and provision one isolated development runtime without changing production.
5. **Development dogfood.** Exercise stored-post search, structured and
   evidence-only questions, saved monitors, quality reports, and tailored-follow
   lifecycle against the isolated development runtime. Keep provider/browser
   effects out unless separately authorized.
6. **Tracker publication — completed prerequisite bootstrap.** Under the
   operator's authorization and the narrowly expanded registry, WI-000 through
   WI-009 were published idempotently as issues #52 through #61, read back, and
   mapped without replacing stable `WI-###` locators.

Packet 6 was completed first under the operator's explicit direction so the
tracker can coordinate subsequent work. Packets 1 and 2 may run in parallel on
disjoint write surfaces. Packets 3 through 5 are serialized in that order. A
production hotfix may preempt this sequence.

## Program Prerequisite

Do not activate a new feature packet for WI-001 through WI-006 or WI-008 until
all six packets are accepted and WI-009 is `DONE`. Corrective work named by this
plan and the reserved WI-007 hotfix lane are the only exceptions.

## Non-Goals

- no new product capability beyond closing the accepted findings;
- no production install, migration, schedule, provider, browser/profile, model,
  release, deployment, or tracker mutation beyond the currently authorized
  WI-000 through WI-009 creation and mapped-label application;
- no permanent `develop` branch and no shared development database, socket,
  credentials, logs, or service identity;
- no cleanup or deletion of historical branches or worktrees in this plan.

## Acceptance Criteria

1. Regression tests prove both question defects fail closed and remain inside
   the caller's answer budget; affected and comprehensive suites pass.
2. Canonical tracker documentation matches live GitHub state while preserving
   exact per-action mutation gates.
3. P35 is based on the then-current canonical main, validated with the combined
   product surfaces, and integrated through a pull request with exact receipts.
4. A uniquely versioned source artifact and isolated development runtime have
   matching manifests and runtime readback; production remains unchanged.
5. Development dogfood produces inspectable evidence for all integrated product
   lanes and distinguishes provider-free proof from any separately authorized
   live canary.
6. GitHub issues #52 through #61 preserve unique WI-000 through WI-009 markers,
   expected mapped labels, dependency references, and provider readback; actions
   other than creation and mapped-label application remain gated.
7. ROADMAP, RUNBOOK, work-item, plan, active-lane, Git, test, release, and
   runtime claims agree before the prerequisite gate closes.

## Execution And Ownership

- accountable human owner: repository operator;
- coordination owner: the top-level coordinator session;
- implementation: one short-lived branch/worktree per independently mergeable
  packet, with one top-level lane owner and bounded support subagents only when
  that packet explicitly permits them;
- shared surfaces: the coordinator owns ROADMAP, RUNBOOK, active-lane catalog,
  shared schemas, compatibility manifests, and final reconciliation;
- WIP: remediation packets consume the normal feature capacity; do not launch
  unrelated work to fill unused capacity.

## Validation

- focused regression tests for each accepted defect;
- affected service, contract, migration, packaging, and MCP tests;
- full `uv run pytest` and `go test ./...` at integration and release cuts;
- planning-contract and active-lane audits;
- source-package reproducibility and exact source/install manifest comparison;
- isolated-runtime doctor plus runtime status and dogfood receipts;
- live GitHub preflight and post-write readback for authorized tracker actions;
  pull requests use the normal collaborative workflow.

## Stop Rules

- stop a packet on dirty or ambiguous custody, stale mainline, failed tests,
  manifest/version mismatch, runtime-isolation uncertainty, or missing effect
  authority;
- preserve partial evidence and repair locally within the bounded packet;
- do not let issue enablement imply issue publication, or development proof
  imply staging or production authority.

## Definition Of Done

WI-009 is `DONE`; every criterion has durable evidence; P35 is integrated; a
distinct development runtime matches a uniquely versioned source artifact;
dogfood passes; the authorized governed issues are published and read back;
and the roadmap explicitly releases the feature freeze.

## Next Action

Create and register the bounded Packet 1 corrective lane from current
`origin/main` for the two question-answering defects and tracker-documentation
reconciliation. Do not begin implementation from this planning branch and do
not perform any runtime, provider, release, or deployment mutation as part of
Plan 0102 registration. The registration PR and authorized issue publication
follow their normal governed workflows.
