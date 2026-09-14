# Plan 0104 | P35 Current-Main Reconciliation

State: CLOSED
Lane: P35
Work item: WI-009
Related work item: WI-004
Branch: feat/x-tailored-follows-v1
Target: main
Integration: merge
Roadmap: P51
Plan version: 4
Date: 2026-09-14
Session owner: coordinator Codex thread `01a09f76-8024-7960-a7c5-c0469cf99153`

## Objective

Reconcile the accepted provider-free P35 Packet 1 implementation with current
canonical main, prove that tailored-follow lifecycle contracts coexist with
every subsequently integrated product surface, and integrate the combined tree
without rewriting either line of history or crossing a runtime/provider gate.

## Current State

- canonical `main` is clean and remote-equal at
  `31342c9fed77bacadb3eec00945d0127be73b43e`;
- `feat/x-tailored-follows-v1` is clean and remote-equal at
  `d2c9f8ebfa79e99eb501910c7d606ce3bcbcf07d`, 88 commits behind and 8 commits
  ahead of current `origin/main`;
- Plan 0086 Packet 1 acceptance is complete on the published feature branch,
  including typed feed/topic/account/list targets, deterministic identity,
  inactive creation, additive migration 18, lifecycle reads, archive history,
  and provider-free tests;
- Plan 0103 closed both accepted question-contract defects and is integrated;
- the earlier issue-registry pull-request gate was a category error. Normal
  owned-fork pull requests are in scope under repository integration policy;
- a three-way path audit found one shared changed file since the merge base:
  generated `service/runtime-manifest.json`. It must be regenerated from the
  combined source tree rather than resolved by choosing either side;
- the history-preserving merge completed without a textual conflict and
  deterministic regeneration reproduced the merged manifest byte-for-byte;
  combined tests then exposed three stale integration assertions: two later
  feature tests still name shared schema 17 although P35 adds accepted migration
  18, and the repository-authority fixture still expects only P22 while P35 is
  now correctly active under this plan.

## Scope

- publish this registration and correct the stale P35/P51 plan, roadmap,
  work-item, runbook, and active-lane projections;
- merge current `origin/main` into the published P35 branch with both histories
  preserved and no rebase, force push, or commit rewriting;
- regenerate the runtime manifest deterministically from the combined source
  tree and inspect the complete merge result for semantic loss;
- rerun the Plan 0086 tailored-follow acceptance surface together with the
  subsequently integrated search, questions, monitors, quality, packaging,
  service-app, runtime-manifest, and MCP surfaces;
- run comprehensive Python and Go validation, planning/lane audits, manifest
  validation, diff checks, and a closed-world published-diff self-review;
- integrate through a normal owned-fork pull request and record exact canonical
  ancestry and closeout receipts.

## Non-Goals

- no P35 Packet 2, scheduler prioritization, acquisition execution, collection
  job, provider call, authenticated X canary, browser/profile use, or network
  effect;
- no installed database/runtime mutation, development-runtime provisioning,
  release, tag, deployment, staging, or production change;
- no new product behavior, public contract redesign, unrelated refactor, or
  service-version increment beyond the already accepted P35 source version;
- no GitHub issue mutation, project mutation, or expansion of the WI-009
  authority boundary.

## Acceptance Criteria

1. The feature branch contains an ordinary merge of the exact then-current
   canonical main commit while retaining the published P35 ancestry.
2. The sole expected generated overlap is resolved by deterministic manifest
   regeneration from the combined source; source version, schema, compatibility
   declarations, and manifest hashes agree.
3. Plan 0086 lifecycle/identity/migration acceptance and the later integrated
   search, question, monitor, quality, package, service-app, and MCP behavior
   pass together without contract loss.
4. Full `uv run pytest`, `go test ./...`, `go vet ./...`, planning and lane
   audits, manifest validation, and `git diff --check` pass at the integration
   candidate.
5. The exact remote diff is self-reviewed, the owned-fork pull request is
   merged, canonical main contains both parents, and all governance projections
   close with exact receipts.

## Expected Write Surface

- the existing P35 Packet 1 source, tests, migration, package metadata, and
  service version already present on `feat/x-tailored-follows-v1`;
- `service/runtime-manifest.json`, regenerated from the combined tree;
- Plan 0086 and this plan plus coordinator-owned projections in `ROADMAP.md`,
  `RUNBOOK.md`, `docs/dev/active-lanes.yaml`, and WI-004/WI-009;
- three narrow compatibility assertions in `tests/test_service_questions.py`,
  `tests/test_service_monitors.py`, and `tests/test_plan_authority_audit.py`;
- no behavior file is expected. Any source conflict or failed invariant outside
  the generated manifest and named compatibility assertions requires another
  plan revision before repair.

## Execution Packet

- accountable human owner: repository operator;
- execution and coordination owner: this top-level Codex session;
- critical path: registration, published-branch baseline, current-main merge,
  deterministic manifest reconciliation, focused and comprehensive validation,
  remote-diff self-review, pull-request merge, and canonical closeout;
- effect boundary: repository files plus provider-free disposable test state;
- work-unit bound: two conflict-resolution attempts and one infrastructure-only
  validation retry; no semantic repair outside the named scope without a plan
  revision;
- review bound: one closed-world self-review against the five frozen criteria
  and the exact remote comparison;
- terminal condition: every criterion is proven at a merged canonical commit,
  or one exact ancestry, contract, custody, or validation blocker is durably
  recorded without widening scope.

Subagents: not planned or authorized for this packet.

## Definition Of Done

P35 Packet 1 is integrated on canonical main with both histories preserved,
the combined provider-free product surface is green, Plans 0086 and 0104 are
closed with exact receipts, and P51 can advance to its separately authorized
versioned development-runtime packet.

## Current Checkpoint

### Checkpoint P0104-C01 | 2026-09-14

Plan version: 1

State transition: `unplanned -> OPEN`.

Progress classification: `blocker_reduction`; the stale P35 integration
candidate now has current custody, a proven one-file overlap, bounded conflict
semantics, combined acceptance requirements, and an executable integration
path.

Authority classification:

- `inherited_authority` for provider-free repository reconciliation, tests,
  branch publication, pull-request creation, self-review, and integration;
- `human_gate` for every installed runtime, provider, browser, release,
  deployment, production, or GitHub issue mutation;
- `scope_expansion` for Packet 2 and every unrelated feature.

Evidence:

- canonical main and the published feature branch are clean and remote-equal at
  the exact commits named above, with divergence `88 behind / 8 ahead`;
- the exact merge base is `75e7771e006f52847e8e47c1059b2b2000fb8ac7`;
- path comparison from that merge base found 61 main-only changed files, 26
  feature-only changed files, and only `service/runtime-manifest.json` in both;
- the owned fork has no open pull request and WI-009 remains open;
- CodeGraph and Graphiti discovery were healthy; current repository and Git
  evidence, rather than older advisory memory, establish this packet;
- active-only planning, goal-only planning, and catalog-only lane audits passed
  before activation.

Subagent status: `not_spawned`.

Next action: publish this registration checkpoint, then baseline and reconcile
the exact published P35 branch with current canonical main.

### Checkpoint P0104-C02 | 2026-09-14

Plan version: 2

State transition: `OPEN -> OPEN`; the current-main merge is complete and the
packet remains in compatibility reconciliation.

Progress classification: `outcome_progress`; both histories and all product
sources merged without semantic intervention, the generated manifest was
reproduced exactly, and the first combined run reduced the remaining work to
three explicit stale assertions.

Authority classification:

- `inherited_authority` remains the controlling classification for repository
  reconciliation; named external effects remain `human_gate`, and Packet 2 or
  unrelated features remain `scope_expansion`.

Evidence:

- merge commit `397db7779a8c6a4a59d1d14a53972321f06c78ac` has exact parents
  `d2c9f8ebfa79e99eb501910c7d606ce3bcbcf07d` and
  `4bb03b5fe583b37a4f354a644b55d3cd9ecd3f84`;
- the pre-merge P35 focused baseline passed all 99 tests;
- `build-runtime.sh --refresh-manifest` left manifest blob
  `2855fee00f1f1b1ea3d1ac7ca44eef33c8a68a3d` unchanged after the merge;
- combined focused validation failed only two assertions expecting shared
  schema 17 instead of accepted P35 schema 18 and one
  repository-authority assertion expecting one active plan instead of the
  correct P22 plus P35 set;
- the underlying migrations, tailored-follow behavior, and later product
  behavior did not fail.

Subagent status: `not_spawned`.

Next action: update only the three named compatibility assertions, rerun the
combined suite, then proceed to comprehensive validation.

### Checkpoint P0104-C03 | 2026-09-14

Plan version: 3

State transition: `OPEN -> OPEN`; the reconciled branch is
`INTEGRATION_READY` pending publication and pull-request integration.

Progress classification: `outcome_progress`; all provider-free behavior,
compatibility, comprehensive validation, and history-preservation criteria are
satisfied on the combined tree.

Authority classification:

- `inherited_authority` remains the controlling classification for repository
  validation and normal pull-request integration; named external effects remain
  `human_gate`, and Packet 2 or unrelated features remain `scope_expansion`.

Evidence:

- merge commit `397db7779a8c6a4a59d1d14a53972321f06c78ac` retains exact P35 and
  canonical-main parents, and deterministic manifest regeneration remained
  byte-identical;
- the three stale compatibility assertions first reproduced exactly, then pass
  after only schema-18 and active-P35 authority expectations were corrected;
- the combined 20-module product slice passes, covering tailored follows,
  migration, search, retrieval, questions, monitors, quality, app/runtime,
  package, MCP integration, Skill routing, and plan authority;
- comprehensive `uv run pytest -q` passes with seven expected skips and no
  failure; every MCP package passes `go test ./...` and `go vet ./...`;
- the first Go commands were invoked from the repository root and failed only
  because the Go module lives under `mcp/`; the immediate module-root rerun
  passed without a repository change;
- repository plan authority passes with exactly P22 and P35 active; manifest
  refresh, `git diff --check`, and goal-only planning checks pass.

Subagent status: `not_spawned`.

Remaining acceptance criteria: publish the exact branch tip, update canonical
lane custody to that immutable remote checkpoint, self-review and merge the
owned-fork pull request, and record canonical ancestry and closeout receipts.

Next action: commit and publish this integration-ready checkpoint, then update
the canonical lane catalog to the exact remote tip before opening the feature
pull request.

### Checkpoint P0104-C04 | 2026-09-14

Plan version: 4

State transition: `OPEN -> CLOSED`; custody advances from
`INTEGRATION_READY` to `INTEGRATED` through PR 68 at
`87858934c8498dccbdeda549ad73f626dbc143a7`.

Progress classification: `outcome_progress`; all five acceptance criteria are
proven on canonical main and P35 Packet 1 is complete without crossing an
external-effect boundary.

Authority classification:

- `inherited_authority` covered the completed provider-free reconciliation and
  normal pull-request integration; installed runtime, provider, browser,
  release, deployment, production, and GitHub issue mutations remain
  `human_gate`, while P35 Packet 2 remains `scope_expansion`.

Evidence:

- canonical catalog PR 67 bound `INTEGRATION_READY` custody, validation, remote
  equality, and the reconciled manifest overlap to exact feature tip
  `434ac770eb1b6aeda37f455c1a35e3ddb9a69ad0`;
- remote PR 68 read back `MERGEABLE/CLEAN` with exact head `434ac770`, 32 changed
  files, the expected Packet 1 implementation and compatibility surface, and
  no failing required check;
- GitHub read back PR 68 `MERGED` at `2026-09-14T11:08:09Z` with merge commit
  `87858934c8498dccbdeda549ad73f626dbc143a7`;
- Git proves both the published feature head and its original accepted
  checkpoint `d2c9f8eb` are ancestors of current canonical main;
- the baseline, reproduced compatibility failures, focused/combined tests,
  comprehensive Python and Go validation, manifest regeneration, planning,
  lane, plan-authority, and diff evidence from C01-C03 remains bound to the
  integrated head.

Subagent status: `not_spawned`.

Next action: close the canonical projections and advance P51 to a separately
planned versioned development-runtime packet; do not begin P35 Packet 2.
