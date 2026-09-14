# Plan 0102 | Productization Readiness Prerequisites

State: CLOSED
Lane: P51
Work item: WI-009
Branch: docs/productization-prerequisite-gate
Target: main
Integration: merge
Roadmap: P51
Plan version: 8
Date: 2026-09-13
Execution owner: primary Codex goal thread

## Objective

Clear the accepted review findings and prove a coherent development release
before any new product feature packet begins.

## Current State

- all six ordered packets are accepted. Plans 0103, 0104, and 0105 are closed,
  and WI-009 is `DONE` in repo-local authority;
- question contract repairs, tracker reconciliation/publication, and P35
  reconciliation are integrated through their recorded reviewed pull requests;
- PRs 73 and 74 integrated the exact-owner cache-only runtime at canonical
  `1168c62e0192ff33f71a07482a32b05721fb839a`;
- two fixed-input builds from that exact commit are byte-identical at SHA-256
  `cf64df41ed072b3d87085b537e0cbe4960d56e71d34d70891b386e152d15bff2`;
- exactly one isolated service `0.3.117`/schema 18 runtime passed lifecycle,
  identity, effect-denial, and five-surface synthetic provider-free dogfood,
  then stopped through exact-owner teardown with its evidence retained;
- production remains PID 1428 at service `0.3.116`, schema 17, installed
  manifest `19707a469eb58c21ca4c5b43a0bfbfb6cac4b0f5a5310480b01b1a3f652429e8`,
  and its original unit/config/database/socket identities;
- the durable Packet 4/5 evidence index is
  `docs/dev/notes/0126-2026-09-14-p51-runtime-dogfood-closeout-receipt.json`.

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

Packet 1 completed through PRs 64 and 65. Packet 2 completed through PR 51.
Packet 6 completed through issues #52-#61 and its repo projection through PR
62. Packet 3 completed through PRs 67 and 68. Packets 4 and 5 completed under
Plan 0105 through PRs 70-74 plus the retained build/runtime/dogfood receipts.

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

The prerequisite gate is closed. Select the highest-priority `READY` child
under a new bounded plan; do not infer provider, browser, schedule,
installed-runtime, release, deployment, private-data, or tracker-mutation
authority from this provider-free acceptance.

## Closeout Receipt | 2026-09-14

Plan version: 8

State transition: `PLANNED -> CLOSED`; WI-009 moves `IN_PROGRESS -> DONE`, P51
moves `OPEN -> CLOSED`, and the feature freeze is released.

Acceptance reconciliation:

1. question-contract regressions pass in the comprehensive suite;
2. canonical tracker documentation and issues #52-#61 retain their accepted
   mappings and per-action gates;
3. P35 Packet 1 is integrated at canonical `87858934`;
4. the canonical service `0.3.117` artifact is reproducible and the isolated
   runtime agrees at schema 18/manifest `a0a11ff4...e83c3` while production is
   unchanged;
5. inspectable synthetic-only receipts pass stored search, both question modes,
   saved monitors, quality, and tailored-follow lifecycle;
6. no GitHub issue mutation occurred during Packets 4/5; issue #55 remains open
   and repo-local completion is explicitly distinct from remote issue state;
7. this plan, Plan 0105, WI-009, ROADMAP, RUNBOOK, active lanes, Git, tests,
   artifact, runtime, dogfood, and production readback now agree.

Evidence: `docs/dev/notes/0126-2026-09-14-p51-runtime-dogfood-closeout-receipt.json`.
