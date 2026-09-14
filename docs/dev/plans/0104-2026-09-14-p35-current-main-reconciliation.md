# Plan 0104 | P35 Current-Main Reconciliation

State: OPEN
Lane: P35
Work item: WI-009
Related work item: WI-004
Branch: feat/x-tailored-follows-v1
Target: main
Integration: merge
Roadmap: P51
Plan version: 1
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
  combined source tree rather than resolved by choosing either side.

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
- no new behavior file is expected. Any source conflict or failed invariant
  outside the generated manifest requires a plan revision before repair.

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
