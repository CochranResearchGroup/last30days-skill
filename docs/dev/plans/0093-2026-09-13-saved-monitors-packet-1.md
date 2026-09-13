# Plan 0093 | Saved Monitors Packet 1

State: PLANNED
Lane: P40
Work item: WI-006
Branch: feat/saved-monitors-v1
Target: main
Integration: merge
Roadmap: P40
Plan version: 1
Date: 2026-09-13
Session owner: unassigned

## Objective

Ship a provider-free monitor kernel with immutable specs, runs, accepted
baselines, fake saved-query views, deterministic comparison, lifecycle, and
replay semantics without scraping, scheduling, follow tracing, or delivery.

## Current State

- P33 Packet 1 is merged and supplies the stable query/evidence contract needed
  by the monitor kernel;
- P35 Packet 1 is not integrated, so every follow-view surface remains outside
  this packet;
- Plan 0083, note 0124, and WI-006 are the accepted architecture and handoff;
- no durable monitor, run, baseline, comparison, digest, or delivery authority
  exists;
- this branch starts from exact canonical 87a8cbac.

## Scope

- implement immutable monitor-spec, run, baseline, view-snapshot, comparison,
  acceptance, lifecycle, and error contracts;
- add a fake saved-query view provider using stable evidence identity/version,
  access partition, coverage, cutoff, and frozen head;
- compare new, revised, unchanged, and explicitly tombstoned evidence while
  treating top-k absence or incomplete coverage as non-removal;
- advance a baseline only after explicit acceptance and make replay
  deterministic and idempotent;
- add migrations and provider-free lifecycle/comparison/replay tests.

## Non-Goals

- no follow-view contract or tracer, digest delivery, channel adapter, live
  query, refresh, scrape, browser/provider, installed runtime/database,
  scheduler, staging, release, production, or GitHub tracker mutation;
- no shared roadmap/runbook/catalog edits from this lane.

## Acceptance Criteria

1. Strict immutable contracts freeze monitor/view revisions, partition,
   evidence head, cutoff, coverage, prior baseline, and comparator version.
2. Identical frozen inputs replay to the same run and candidate baseline.
3. Only explicit acceptance advances the baseline; failure or rejection does
   not.
4. New, revised, unchanged, explicit removal, incomplete comparison, archive,
   pause, and partition mismatch are distinct and fail closed.
5. Focused migration, lifecycle, comparison, acceptance, and replay tests pass
   without network, schedule, delivery, runtime, or follow dependencies.

## Execution Packet

- accountable human owner: repository operator;
- execution owner: one independent top-level Codex session in this worktree;
- coordination owner: coordinator session for shared search/follow schemas,
  catalog, roadmap/runbook, MCP, notification, and release joins;
- expected writes: monitor contracts, durable repository/kernel, fake query
  view provider, migrations, focused fixtures/tests, and this plan;
- inputs: Plan 0083, note 0124, WI-006, merged P33 Packet 1, and current
  origin/main;
- terminal condition: all five criteria pass and a published PR-ready
  checkpoint exists, or one exact blocker is recorded without widening scope;
- authority: provider-free source, tests, branch publication, and PR
  preparation only.

## Start Checklist

- verify exact base, clean worktree, remote custody, and no overlapping PR;
- reread AGENTS.md and relevant planning, Git, validation, architecture, and
  multi-session policies;
- use read-only Graphiti discovery and CodeGraph impact where available;
- transition this plan to OPEN, record the runtime session identity, and push
  that planning checkpoint before implementation;
- coordinate any shared search-contract overlap before editing it.

## Stop Rules

- stop before follow tracing until P35 Packet 1 integrates;
- stop before digest delivery, notification/channel work, live query,
  refresh/scrape, provider/browser, installed runtime/database, schedule,
  staging, release, production, or tracker effects;
- stop and reconcile if another lane owns an overlapping shared contract.

## Current Checkpoint

No execution checkpoint yet. The plan-only launch ref is awaiting publication
and canonical registration.
