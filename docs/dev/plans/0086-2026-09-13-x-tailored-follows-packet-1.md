# Plan 0086 | X Tailored Follows Packet 1 Contract Tracer

State: PLANNED
Lane: P35
Work item: WI-004
Branch: feat/x-tailored-follows-v1
Target: main
Integration: merge
Roadmap: P35
Plan version: 1
Date: 2026-09-13

## Objective

Ship WI-004 Packet 1 as a provider-free collection-contract tracer covering
purpose, attention, lifecycle, canonical X targets, deterministic follow
identity, inactive creation, migration, get/list/archive, and persistence.

## Current State

- Plan 0078 and note 0119 are the accepted architecture;
- collection scheduling and immutable revisions exist, but tailored-follow
  purpose/attention/lifecycle, X list routing, and typed target identity do not;
- this launch ref contains only this plan and has not started implementation;
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

Open one independent top-level Codex session in
`/home/ecochran76/workspace.local/last30days-skill-wi004`, take custody of this
plan, register its `OPEN/ACTIVE_WORKTREE` transition through the coordinator,
and implement only the contract/migration/lifecycle tracer.
