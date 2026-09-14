# Plan 0096 | Agent Question Evidence Tracer Packet 2

State: OPEN
Lane: P36
Work item: WI-003
Branch: feat/agent-question-evidence-v2
Target: main
Integration: merge
Roadmap: P36
Plan version: 2
Date: 2026-09-13
Session owner: Codex `/root` (runtime-reported canonical task identity; no
separate thread UUID exposed to this session)

## Objective

Compose Packet 1's durable question workflow with the real federated
`PostSearchBackend`, freeze its exact current-revision evidence, and provide a
provider-free immutable evidence reader across legacy and temporal storage.

## Current State

- Packet 1 is integrated through PR 41 and supplies strict question, answer,
  citation, retrieval, queue, lease, replay, and validation contracts;
- P33 supplies the real cache-only federated `PostSearchBackend` across
  `document_versions` and `service_source_versions`;
- `QuestionService` already accepts the backend protocol but has only fake-
  backend proof, and no public component can dereference a frozen citation;
- service HTTP routes, MCP tools, model execution, installed runtimes, and
  provider acquisition remain outside this packet.

## Scope

- exercise `QuestionService` against the real `service_post_search` backend and
  freeze exact search-head, component-head, ordered-hit, version, digest,
  access-partition, coverage, truncation, and byte-budget evidence;
- add strict versioned request/item/response contracts for reading 1-20 exact
  question citations with a bounded response size;
- implement one read-only evidence resolver for both immutable storage
  families, preserving requested order and returning source/native identity,
  canonical URL, author, title, bounded text, publication/observation/system
  timing, metadata, collection/topic causes when present, and provenance that
  the current schema can prove;
- make missing, mismatched, or unauthorized citations indistinguishable as
  `unavailable`, never drift a citation to a current revision, and truncate
  only at item boundaries with explicit omitted refs;
- add provider-free fixtures and focused regression tests over both storage
  families, historical revisions, partition closure, changed digests/URLs,
  pagination/head drift, and response budgets.

## Non-Goals

- no service route, client, MCP tool, Go adapter, generated public contract
  catalog, Skill guidance, configuration, changelog, release, or version bump;
- no structured answer worker, model call, semantic entailment claim, temporal
  claim/event attachment, prompt construction, or Packet 3 behavior;
- no source refresh, browser/provider, follow, schedule, delivery, tracker,
  installed runtime/database, staging, deployment, or production effect;
- no P35 pull-request action and no alteration of its branch or gate.

## Acceptance Criteria

1. A real SQLite fixture proves the question service consumes the federated
   post-search backend and freezes exact legacy and temporal citations plus
   search/coverage receipts before any worker execution.
2. Evidence-read contracts reject unknown, duplicate, malformed, oversized,
   or mixed-profile inputs and serialize deterministically.
3. The resolver returns only the exact cited immutable revision inside the
   caller's authorized partitions and verifies storage family, version,
   content digest, source URL, and partition before exposing content.
4. Missing, changed, cross-partition, wrong-family, and unauthorized refs share
   the same non-leaking unavailable result; request-order and item-boundary
   truncation are deterministic and report every omitted ref.
5. Focused question/search/store tests, affected compatibility tests,
   compilation, runtime source-package build, plan/lane audits, and the
   comprehensive provider-free suite pass at one clean remote-equal checkpoint.

## Expected Write Surface

- `skills/last30days/scripts/lib/service_question_contracts.py`;
- `skills/last30days/scripts/lib/service_questions.py` and/or one narrowly
  owned additive question-evidence module;
- focused test fixtures and tests under `tests/`;
- this branch-local Plan 0096 only until coordinator reconciliation.

`service/runtime-manifest.json`, ROADMAP.md, RUNBOOK.md, work items, the active-
lane catalog, public HTTP/MCP surfaces, and generated compatibility artifacts
remain coordinator-owned joins.

## Execution Packet

- accountable human owner: repository operator;
- execution owner: one independent top-level Codex session;
- critical path: red tests, real-backend composition, immutable resolver,
  adversarial partition/digest/budget tests, comprehensive validation, clean
  publication, coordinator handoff;
- effect boundary: repository source and provider-free temporary SQLite only;
- retry bound: two implementation attempts before local replan;
- review bound: one focused self-review against these five criteria;
- terminal condition: all five criteria pass at a clean published checkpoint,
  or one exact contract/safety blocker is recorded without widening scope.

Subagents: not planned. The top-level lane owner may use one bounded support
agent only if the plan is first revised with a disjoint scope and result path.

## Definition Of Done

The real federated search and immutable evidence-read path are proven end to
end in provider-free fixtures, every citation remains partition-closed and
revision-stable, the branch is clean and remote-equal, and the coordinator has
an exact integration handoff without any public transport or runtime effect.

## Current Checkpoint

### Checkpoint P0096-C01 | 2026-09-13

Plan version: 1

State transition: `unplanned -> PLANNED`.

Progress classification: `outcome_progress`; Packet 2 has one bounded evidence
tracer, exact source seams, acceptance checks, and external-effect stops.

Authority classification:

- `inherited_authority` for provider-free repository implementation after the
  coordinator integrates this lane registration;
- `human_gate` for P35 pull-request action and any installed/runtime/provider/
  release/production effect;
- `scope_expansion` for Packet 3 worker behavior or Packet 4 HTTP/MCP surface.

Evidence:

- base is exact canonical `d4e3cd65f4a6ba79196ba47721245d5ade687322`;
- CodeGraph is current at 372 files, 10,433 nodes, and 25,653 edges and confirms
  `QuestionService.submit` already consumes a `PostSearchBackend` protocol;
- the concrete backend reads current revisions from both storage families,
  while both version tables are immutable and retain the exact fields needed
  for dereference;
- Graphiti was healthy but returned only older MCP history, so current source,
  Plans 0079/0091, and note 0120 remain authoritative.

Subagent status: `not_spawned`; this is a plan-only launch checkpoint.

Next action: publish this plan-only branch, let the coordinator register it on
canonical main, then assign one independent top-level Codex session to open and
execute Packet 2. Do not implement on the coordinator session.

### Checkpoint P0096-C02 | 2026-09-13

Plan version: 2

State transition: `PLANNED -> OPEN`.

Progress classification: `blocker_reduction`; the replacement independent lane
owner accepted custody and established the required recoverable activation
boundary before feature work.

Authority classification:

- `inherited_authority` for the Plan 0096 provider-free repository changes and
  temporary SQLite fixtures;
- `human_gate` remains in force for pull requests and all installed/runtime,
  provider, browser, model, schedule, delivery, staging, production, release,
  and tracker effects;
- `scope_expansion` remains in force for Packet 3 worker behavior, Packet 4
  public HTTP/MCP surfaces, and every coordinator-owned join.

Evidence:

- replacement owner identity is Codex `/root`, the canonical task identity
  reported by this runtime; the runtime exposes no separate thread UUID to the
  session;
- the interrupted predecessor was stopped during preflight after printing
  credential-bearing environment variables and made no feature or plan edits;
  no environment, credential store, auth file, shell history, or prior
  transcript was inspected during replacement activation;
- the worktree was clean on `feat/agent-question-evidence-v2` at exact merge
  `a28e08138312f61f094841d72c2a664cff0f32b0`, whose parents are the plan-only
  checkpoint `07f961290acf9ab6fece4ebb9b4c9c6c7560acc5` and integrated
  `origin/main` `5004df7f228059b2d2c154f1414de83fae16cfd5`;
- remote `refs/heads/feat/agent-question-evidence-v2` remained exactly
  `07f961290acf9ab6fece4ebb9b4c9c6c7560acc5` before this activation update;
- Graphiti was healthy but returned no current P36/Plan 0096 evidence, so the
  plan, WI-003, repository source, Git refs, and tests remain authoritative;
- the worktree-local ignored CodeGraph index was initialized and is current at
  372 files, 10,431 nodes, and 28,362 edges.

Subagent status: `not_spawned`; replacement execution remains single-owner as
required.

Next action: validate and publish this plan-only activation checkpoint, verify
remote equality, then begin Packet 2 with one acceptance-level red/green tracer
at a time.
