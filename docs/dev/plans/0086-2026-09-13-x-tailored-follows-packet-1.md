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
- this plan is now owned and `OPEN`, but Packet 1 implementation has not
  started;
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
`feat/x-tailored-follows-v1` from the published P0086-C01 checkpoint; reread
AGENTS.md and the applicable policies, fetch and reconcile current
`origin/main`, rerun focused Graphiti and CodeGraph discovery, reconcile shared
collection/service-contract ownership with the coordinator and WI-002, then
implement only Plan 0086 Packet 1's provider-free
contract/migration/get/list/archive/persistence tracer. Do not start a job,
timer, installed-database migration, browser/profile, provider call, staging,
production, tracker mutation, WI-005 semantics, or Packet 2.
