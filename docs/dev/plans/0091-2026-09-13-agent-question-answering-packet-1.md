# Plan 0091 | Agent Question Answering Packet 1

State: PLANNED
Lane: P36
Work item: WI-003
Branch: feat/agent-question-answer-v1
Target: main
Integration: merge
Roadmap: P36
Plan version: 1
Date: 2026-09-13
Session owner: unassigned

## Objective

Ship one provider-free question tracer from strict durable request contracts
through queue, lease, idempotency, fake stored-post search, answer status, and
immutable citation/evidence contracts.

## Current State

- P33 Packet 1 is merged and supplies stable post-search request, response,
  search-head, and evidence-reference contracts;
- Plan 0079, note 0120, and WI-003 are the accepted architecture and handoff;
- no question schema, durable queue, answer worker, model call, or MCP question
  tool has been implemented;
- this branch starts from exact canonical 87a8cbac.

## Scope

- define strict question, answer, statement, citation, status, and error
  contracts with deterministic identities and digests;
- add a durable provider-free queue with bounded leases, replay, recovery, and
  idempotent completion;
- compose only through a fake PostSearchBackend and fake no-tool answer worker;
- validate citations against selected immutable evidence and preserve
  supported, mixed, insufficient, contradictory, stale, and partial states;
- add migrations and provider-free contract/replay tests.

## Non-Goals

- no real model, live search/source adapter, browser, refresh, follow, schedule,
  MCP transport publication, installed runtime, staging, release, production,
  or GitHub tracker mutation;
- no changes to P33 search semantics or shared roadmap/runbook/catalog.

## Acceptance Criteria

1. Strict versioned contracts reject unknown fields and produce deterministic
   request, evidence-set, answer, and idempotency identities.
2. Queue claim, lease expiry, retry, replay, and duplicate submission are
   durable and bounded under provider-free tests.
3. Fake search and answer workers exercise supported, conflicting, stale,
   partial, no-evidence, invalid-citation, and unsupported-claim outcomes.
4. Every substantive statement maps to authorized immutable evidence or fails
   closed with an inspectable validation result.
5. Focused migration, contract, queue, validation, and compatibility suites
   pass without network or runtime effects.

## Execution Packet

- accountable human owner: repository operator;
- execution owner: one independent top-level Codex session in this worktree;
- coordination owner: coordinator session for shared service/MCP schemas,
  roadmap, runbook, catalog, and P33/P37 joins;
- expected writes: question contracts, durable repository/queue, fake
  interfaces, migrations, focused fixtures/tests, and this plan;
- inputs: Plan 0079, note 0120, WI-003, merged P33 Packet 1, and current
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
- coordinate any shared-contract overlap before editing it.

## Stop Rules

- stop before any model, provider/browser, installed runtime/database,
  schedule, staging, release, production, or tracker effect;
- stop before MCP transport publication; Packet 1 ends at the provider-free
  durable tracer;
- stop and reconcile if another lane owns an overlapping shared contract.

## Current Checkpoint

No execution checkpoint yet. The plan-only launch ref is awaiting publication
and canonical registration.
