# Plan 0086 | X Tailored Follows Packet 1 Contract Tracer

State: OPEN
Lane: P35
Work item: WI-004
Branch: feat/x-tailored-follows-v1
Target: main
Integration: merge
Roadmap: P35
Plan version: 1
Date: 2026-09-13
Execution owner: top-level Codex session `01a09caa-90d6-7350-a8ce-72d7ced7ef12`
Runtime-reported model: unavailable

## Objective

Ship WI-004 Packet 1 as a provider-free collection-contract tracer covering
purpose, attention, lifecycle, canonical X targets, deterministic follow
identity, inactive creation, migration, get/list/archive, and persistence.

## Current State

- Plan 0078 and note 0119 are the accepted architecture;
- collection scheduling and immutable revisions exist, but tailored-follow
  purpose/attention/lifecycle, X list routing, and typed target identity do not;
- the registered launch checkpoint
  `5d0acd12845aad940d89522749d37651e1ed0ff2` was clean and equal locally and
  remotely before this branch merged current `origin/main` at
  `b92160a600ee93f2b3bb21899d7e6f31cbb3a0ae`;
- the branch was reconciled again with canonical `origin/main` at
  `4f322e0a3c2d4795305c3bdfb853de27fae1c558` before implementation;
- Packet 1 acceptance is implemented and validated at implementation commit
  `29631a48a8ae4ea1c867df5c5b242a4dee9c605d`; the plan remains `OPEN` pending
  review and integration;
- GitHub Issues remain disabled, so WI-004 is the work-item locator.

## Scope

- evolve `CollectionSpec` compatibly with purpose, attention, and lifecycle;
- implement canonical X feed/topic/account/list selector validation and
  deterministic partition-bound target IDs;
- create tailored follows disabled by default;
- implement additive/idempotent migration plus get/list/archive semantics;
- prove persistence, immutable revisions, duplicate prevention, and safe
  validation with temporary databases.

## Non-Goals

- no acquisition-work context, account/list browser route, scheduler priority,
  installed database migration, job/schedule start, browser/provider access,
  staging, release, or production;
- no cross-service abstraction from WI-005 and no tracker mutation.

## Acceptance Criteria

1. Legacy specs round-trip with unchanged identity and explicit safe defaults.
2. New X targets enforce exact canonical selectors and stable partition-bound
   follow IDs; malformed/noncanonical/public-partition inputs fail closed.
3. Creation is inactive, versions are immutable, duplicate active targets are
   rejected, and archive is an irreversible tombstone rather than deletion.
4. Get/list/archive expose exact lifecycle/history in temporary stores.
5. Focused migration/collection/service contract tests pass without a job or
   browser start.

## Execution Packet

- accountable human owner: repository operator;
- execution owner: next top-level Codex session opened in this worktree;
- coordination owner: coordinator for shared contracts, catalog, and WI-002/
  WI-005 joins;
- expected writes: collection models/coordinator, migration, service contracts/
  app/CLI, focused persistence tests, generated Go contract only if required,
  relevant configuration/docs, and branch-local checkpoints;
- inputs: Plan 0078, note 0119, WI-004, current `origin/main`;
- validation: focused migration/collection/service tests, no-effect fixtures,
  policy/lane audits, generated-contract drift, published-commit readback;
- terminal condition: all criteria pass and PR is integration-ready, or one
  exact blocker is recorded without runtime/provider effects;
- review bound: one drift-discovery pass and one closed-world remediation pass;
- authority: provider-free source/tests/branch/PR only.

Subagents: optional for bounded support under lane owner; no nested delegation
without plan revision.

## Current Checkpoint

### Checkpoint P0086-C01 | 2026-09-13

Plan version: 1

State transition: `planned -> open`.

Progress classification: `blocker_reduction`; the registered branch was
reconciled with current `origin/main`, lane ownership was recorded, and a
recoverable activation checkpoint is ready for publication. No Packet 1 code
or test implementation began.

Authority classification:

- `inherited_authority` for fetch, branch reconciliation, branch-local plan
  activation, validation, commit, and branch publication;
- `not_authorized` for shared-authority edits, tracker effects, jobs, timers,
  installed databases, browsers/profiles, providers, staging, production, or
  Packet 1 implementation during this activation turn.

Execution evidence:

- runtime thread/session owner:
  `01a09caa-90d6-7350-a8ce-72d7ced7ef12`;
- runtime-reported model: unavailable;
- launch checkpoint `5d0acd12845aad940d89522749d37651e1ed0ff2`
  matched local and remote branch custody with a clean worktree;
- fetched `origin/main` resolved to
  `b92160a600ee93f2b3bb21899d7e6f31cbb3a0ae` and was merged without a
  conflict or lane-authored change to coordinator-owned authorities;
- Graphiti was healthy in `last30days_skill_main`; its focused query returned
  no WI-004/P35-specific fact, so Plan 0078, note 0119, WI-004, and current Git
  remain authoritative;
- the worktree-local CodeGraph index contains 356 files, 9,834 nodes, and
  26,067 edges; focused exploration confirmed the collection model,
  coordinator, service contract/application, migration, and focused test seams
  for the later Packet 1 implementation.

Subagent status: `not_spawned`; this activation turn explicitly prohibited
subagents.

Graphiti write status: `not_attempted`; this activation-only turn authorized
read discovery and branch publication, not a Graphiti ingestion job.

Next action or stop reason: stop after publishing and verifying this activation
checkpoint. Resume in this same worktree and top-level lane session with the
exact instruction in `Next Action` below.

### Checkpoint P0086-C02 | 2026-09-13

Plan version: 1

State: `OPEN`; Packet 1 is acceptance-complete and integration-ready, but is
not integrated and no later packet is authorized by this checkpoint.

Progress classification: `acceptance_progress`; the provider-free collection
contract now represents typed X feed/topic/account/list follows with strict
canonical selectors, deterministic partition-bound target identity, inactive
creation, immutable revisions, duplicate-active-target exclusion, and
irreversible archive history.

Implementation evidence:

- reconciled `origin/main` commit:
  `4f322e0a3c2d4795305c3bdfb853de27fae1c558`;
- reconciliation merge commit:
  `f88a77d192ace590b0fe3699f0058f2ecd2c09ff`;
- Packet 1 implementation commit:
  `29631a48a8ae4ea1c867df5c5b242a4dee9c605d`;
- database migration 18 backfills existing rows to
  `general` / `standard` / `active` with no follow target and adds a partial
  unique index for non-archived tailored-follow identities;
- service compatibility advanced source-side to service `0.3.117`, MCP
  `4.0.5`, and exact database schema `18`; generated contracts and the runtime
  manifest were refreshed, but no artifact was installed or released;
- `get`, default-hidden `list`, `list --include-archived`, and `archive` are
  additive collection operations through the existing application and CLI
  seams; post-search request/response/cursor/MCP search semantics and isolated
  runtime identity were not changed.

Validation evidence:

- `uv run pytest tests/test_service_collection.py tests/test_service_product.py tests/test_service_migrations.py tests/test_service_process.py tests/test_service_contracts.py tests/test_plan_authority_audit.py -q`
  passed (`99 passed`);
- `uv run pytest -q` passed across the full Python suite;
- `go test ./...` passed across all MCP packages;
- `git diff --check` passed;
- the initial broad run exposed only Packet-1-induced stale contract/version
  locks; after advancing the documented compatibility identities and fixtures,
  the full suite passed. The earlier reported broad-test selector-path failure
  was not reproduced.

Effects and authority:

- source, temporary-test databases/artifacts, Git commits, branch publication,
  and PR creation only;
- no live X/provider call, installed database/runtime migration, job, timer,
  browser/profile, tracker, staging, production, tag, release, or deployment;
- coordinator-owned `ROADMAP.md`, `RUNBOOK.md`, `docs/dev/active-lanes.yaml`,
  and shared work-item state were not lane-authored.

Subagent status: `not_spawned`; this execution explicitly prohibited
subagents.

Graphiti closeout: no write was queued. Current Git and this branch-local
checkpoint are the durable authority; the architecture handoff records the
existing degraded Graphiti ingestion attempt, and this packet prohibited
provider effects.

Next action or stop reason: publish this checkpoint, verify local/remote branch
equality, open the exact owned-fork PR to `main`, and stop without merging or
starting Packet 2.

### Checkpoint P0086-C03 | 2026-09-13

Plan version: 1

State: `OPEN`; Packet 1 remains acceptance-complete and published, while PR
creation is policy-blocked before effect.

Gate evidence:

- local and remote `feat/x-tailored-follows-v1` were equal at published C02
  commit `1bba5bd64c263ad9384ce1b2fe4867a1c4c2ec27` before the PR attempt;
- current `origin/main` remained
  `4f322e0a3c2d4795305c3bdfb853de27fae1c558`;
- duplicate preflight returned no existing PR for the branch;
- the exact target resolved to
  `github.com/CochranResearchGroup/last30days-skill`, but
  `docs/dev/forge-issue-targets.json` currently permits only `read`;
- the governed `gh pr create` request was rejected before mutation because the
  target registry did not allow PR creation. No PR exists and no retry or
  workaround was attempted.

Next action or stop reason: stop after publishing this failed-closed receipt.
The coordinator/operator must first update the applicable forge target policy
to allow PR creation for the owned fork (without activating GitHub Issues or
tracker mutation), then resume with the exact instruction below.

## Start Checklist

- verify registered worktree/ref/checkpoint and current `origin/main`;
- reread AGENTS.md, policies, Plan 0078, note 0119, and WI-004;
- run Graphiti discovery and CodeGraph impact for collection/migration seams;
- transition to `OPEN`, record runtime-reported owner/model when available, and
  publish the first recoverable checkpoint before coding;
- reconcile shared collection/filter surfaces with coordinator and WI-002.

## Stop Rules

- stop before any job, timer, installed database, browser/profile, provider,
  staging, release, or production effect;
- stop before WI-005 cross-service semantics or Packet 2 typed acquisition;
- stop and reconcile overlapping collection/migration work.

## Next Action

Resume WI-004 / P35 in
`/home/ecochran76/workspace.local/last30days-skill-wi004` on
`feat/x-tailored-follows-v1` from published checkpoint P0086-C03 after the
applicable forge target policy explicitly allows PR creation for
`github.com/CochranResearchGroup/last30days-skill`; fetch and verify current
`origin/main`, confirm local/remote branch equality, rerun duplicate PR
preflight, then open the Packet 1 PR to `main` and stop without merging. Do not
activate or mutate GitHub Issues/Projects, start Packet 2, or mutate a job,
timer, installed database/runtime, browser/profile, provider, tracker,
staging, production, tag, release, or deployment.
