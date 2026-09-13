# Plan 0091 | Agent Question Answering Packet 1

State: OPEN
Lane: P36
Work item: WI-003
Branch: feat/agent-question-answer-v1
Target: main
Integration: merge
Roadmap: P36
Plan version: 1
Date: 2026-09-13
Session owner: Codex thread 01a09cf4-c89c-7ad2-9b64-8dc95c4cbec6

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

### Checkpoint P0091-C01 | 2026-09-13

Plan version: 1

State transition: `PLANNED -> OPEN`.

Progress classification: `outcome_progress`; the independent lane now has
clean, reconciled, recoverable custody and is ready for Packet 1 implementation
after coordinator integration of this ownership checkpoint.

Authority classification:

- `explicit_authority` for activation-only Git reconciliation, this
  branch-local plan update, validation, commit, and branch push;
- `not_authorized` in this turn for feature code, shared coordinator surfaces,
  work-item changes, providers, browser, installed runtime, schedules, tracker,
  staging, production, pull-request creation, or pull-request integration.

Base, merge, and ref evidence:

- before reconciliation, local and remote
  `feat/agent-question-answer-v1` were clean and equal at
  `856fb385137c679f06616384109a0f639e37d0f5`, whose merge base with fetched
  `origin/main` was the registered launch base
  `87a8cbac467f979237f85b7e9a96946a2f137613`;
- fetched `origin/main` resolved to
  `606272ab82ba2c97d833e8b06e2c1ea4092bac85`, four commits ahead of that
  merge base;
- merge commit `35c7a29574866e10606e888c2992f9782b099fb9`
  preserves both parents in order: lane checkpoint
  `856fb385137c679f06616384109a0f639e37d0f5` and `origin/main`
  `606272ab82ba2c97d833e8b06e2c1ea4092bac85`;
- the merge resolved automatically with only expected documentation ancestry;
  `ROADMAP.md`, `RUNBOOK.md`, `docs/dev/active-lanes.yaml`, WI-003, Plan 0079,
  and note 0120 remain byte-equal to fetched `origin/main`;
- no open pull request targets this branch at activation time.

Owned changes:

- only this Plan 0091 file changes after the ancestry merge: plan state,
  runtime-reported session owner, and this activation checkpoint;
- no feature source, tests, shared contracts, installed runtime, provider, or
  coordinator-owned authority was edited by this activation.

Validation evidence:

- `.venv/bin/python -m pytest tests/test_plan_authority_audit.py -q` passed all
  10 tests;
- `.venv/bin/python dev/last30days/scripts/audit_plan_authority.py` passed with
  zero issues and current main-authority counts unchanged;
- the active-only planning-contract audit reports only the expected
  branch-local findings that this newly `OPEN` plan is not yet wired into
  coordinator-owned `ROADMAP.md` and `RUNBOOK.md`; those surfaces are outside
  this activation and remain byte-equal to `origin/main` for coordinator
  ownership integration;
- `git diff --check` passed and the owned diff against `origin/main` contains
  only this Plan 0091 file; post-push local/remote equality is the terminal
  readback required for handoff.

Remaining acceptance criteria:

- all five Packet 1 criteria remain unimplemented and unvalidated; feature
  implementation may begin only after the coordinator integrates ownership.

Subagent status and reconciliation:

- `not_spawned`; activation custody, ancestry reconciliation, and the sole
  plan edit were performed directly by the independent top-level lane owner.

Graphiti status:

- runtime doctor was healthy for MCP, FalkorDB persistence, and Inspector;
  one bounded read of `last30days_skill_main` returned five facts, three nodes,
  and three episodes but no relevant P36/WI-003 activation recall;
- `not_written`; discovery was advisory and read-only, and activation grants no
  Graphiti/database mutation authority.

Next action:

- commit and push this activation checkpoint, verify the local and remote
  branch tips are equal, then stop for coordinator ownership integration; do
  not implement Packet 1 or open or merge a pull request in this turn.
