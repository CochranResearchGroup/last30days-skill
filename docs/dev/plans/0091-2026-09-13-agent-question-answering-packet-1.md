# Plan 0091 | Agent Question Answering Packet 1

State: CLOSED
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
- Packet 1 now provides strict question contracts, a question-owned migration,
  a durable bounded queue, immutable citation validation, and fake provider-free
  search/worker seams;
- no real model call or MCP question tool has been implemented, and transport
  publication remains outside this packet;
- the implementation is reconciled with exact canonical
  `169a45b86735e1d4ccb48346d0f044f86105d610` through merge commit
  `57d523c1fd5c23848b2e7a4cf9a1d95f01eef787`.

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

## Definition Of Done

All five Packet 1 acceptance criteria pass on the provider-free branch, the
global service/MCP compatibility contract remains unchanged, the accepted
checkpoint is pushed and remote-equal, and review/integration returns to the
coordinator without opening or merging a pull request.

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

### Checkpoint P0091-C02 | 2026-09-13

Plan version: 1

State transition: `implementation_active -> packet_1_acceptance_met`; the plan
remains `OPEN` until coordinator integration.

Progress classification: `verified_outcome`; all five Packet 1 criteria pass
on the reconciled, provider-free branch.

Authority classification:

- `inherited_authority` from the operator's explicit Packet 1 instruction for
  question-specific source, tests, migration, this plan, branch commit, and
  branch push;
- `not_authorized` for models, live search or source adapters, browser,
  providers, refresh, follow, schedules, MCP transport publication, installed
  runtime or database, staging, release, production, tracker, P35, pull-request
  creation, or pull-request integration.

Base, merge, and ref evidence:

- fetched `origin/main` resolved exactly to the coordinator-provided
  `169a45b86735e1d4ccb48346d0f044f86105d610`;
- merge commit `57d523c1fd5c23848b2e7a4cf9a1d95f01eef787`
  preserves parents `c4d985727c39c7cfe2a86a64eae318351eefd5d4`
  and `169a45b86735e1d4ccb48346d0f044f86105d610`, with no rebase or
  history rewrite;
- `ROADMAP.md`, `RUNBOOK.md`, `docs/dev/active-lanes.yaml`, and all work-item
  files remain byte-equal to that fetched `origin/main`.

Owned changes:

- `service_question_contracts.py` defines strict versioned request, answer,
  statement, citation, status, coverage, and safe-error contracts with
  deterministic canonical digests and identities;
- `service_questions.py` defines the fake `PostSearchBackend`, fake no-tool
  worker boundary, frozen retrieval receipts, a question-owned schema-v1
  migration, durable task/attempt/failure ledgers, bounded lease recovery and
  retries, replay/idempotency, host-only evidence/no-evidence completion, and
  immutable citation/correlation validation;
- focused provider-free tests cover deterministic replay, request conflicts,
  head changes, lease expiry, retry exhaustion, transient and unavailable
  workers, supported/conflicting/stale/partial/no-evidence/evidence-only
  answers, partition escape, changed retrievals, fabricated or uncited claims,
  and prompt-injection-shaped evidence as inert data;
- the checked-in source runtime manifest includes the two additive modules so
  later authorized runtime builds remain reproducible; no runtime was
  installed.

Shared-surface reconciliation:

- no edits remain in `service_contracts.py`, `service_store.py`, the global
  `store.py` schema, or `service-contracts-v1.json`; the service/MCP ABI,
  database schema 17, release locks, and P40-owned catalog stay unchanged;
- `service/runtime-manifest.json` is the only shared packaging overlap: it adds
  the two question-specific source files and leaves all pre-existing source
  digests unchanged.

Acceptance evidence:

1. strict contract tests reject unknown or malformed fields and prove stable
   request, evidence, answer, statement, task, and output identities;
2. SQLite fixtures prove one durable question migration, idempotent duplicate
   submission/completion, generation-bound leases, one bounded retry, expiry
   recovery, immutable attempts, and terminal failure receipts;
3. fake search and no-tool worker fixtures exercise every required answer and
   failure state without network, model, browser, provider, or acquisition;
4. answer completion closes every citation over the frozen authorized evidence
   tuple and rejects mismatched heads, digests, partitions, missing citations,
   fabricated references, and changed retrieval records;
5. focused migration, contract, queue, validation, service compatibility,
   release-lock, lifecycle, and reproducible package-build checks pass.

Validation evidence:

- 17 question contract/queue/worker tests passed;
- 121 focused question, migration, compatibility, store, temporal, tick,
  release-lock, and isolated lifecycle tests passed outside the sandbox only
  where temporary Unix sockets and installer fixtures required it;
- the complete 2,821-test repository collection reached 100 percent with one
  unrelated protected-authority failure: `RUNBOOK.md` does not contain a Plan
  0091 locator. The coordinator-owned file is intentionally unchanged; every
  other selected test passed or skipped normally;
- the canonical source-runtime build passed with artifact digest
  `39e247f18b8b5938143a9452b2a12358577bed2012f2e7853ae77c7aa6053bd2`;
- Python bytecode compilation passed. Ruff is not installed in `.venv`, and
  `uv run ruff` had no available executable, so no lint result is claimed.

Remaining criteria and risks:

- no Packet 1 acceptance criterion remains open;
- MCP/HTTP publication, real backend composition, evidence dereference,
  calibrated semantic entailment, model execution, and installed-runtime proof
  remain later packets or coordinator gates;
- the protected RUNBOOK locator is a coordinator reconciliation item and is
  not repaired in this lane.

Subagent status: `not_spawned`; the top-level owner performed implementation
and validation directly as required.

CodeGraph status: `.codegraph/` is absent; it was not initialized. Structural
exploration used only the already identified source seams and narrow current
source reads.

Graphiti status: the runtime doctor was healthy and one bounded read-only
discovery returned no relevant P36/WI-003 history. `not_written`; the operator
forbade installed-runtime/database mutation and repository evidence is
authoritative.

Next action:

- commit and push this accepted Packet 1 checkpoint, verify clean local/remote
  equality, then stop for coordinator reconciliation; do not open or merge a
  pull request or begin Packet 2.

### Checkpoint P0091-C04 | 2026-09-13

State transition: `OPEN -> CLOSED`.

Packet 1 integrated through PR 41 as canonical merge
`6d5eb5d972024cd584bfcc8bf57975f49fa90f45`. The combined branch passed all
62 focused tests and the full 2,838-test repository collection. WI-003 returns
to `READY` for a separately planned Packet 2; no model, MCP publication,
installed-runtime, provider, or production effect occurred.
