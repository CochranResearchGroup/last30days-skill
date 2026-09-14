# Plan 0098 | Agent Question Answer Tracer Packet 3

State: OPEN
Lane: P36
Work item: WI-003
Branch: feat/agent-question-answer-v3
Target: main
Integration: merge
Roadmap: P36
Plan version: 3
Date: 2026-09-14
Session owner: coordinator Codex thread `01a0860e-b671-7f62-b6ae-6c06a08e6852`

## Objective

Complete the provider-free structured-answer boundary over Packet 2's frozen
retrieval by adding one no-tool structured-turn adapter, truthful model/effect
receipts, deterministic answer validation, and durable bounded worker behavior
for supported, conflicting, stale, partial, empty, unavailable, and rejected
answers.

## Current State

- Packet 1 supplies strict question/answer/status contracts, deterministic
  identifiers, SQLite queue/lease/replay state, a fake-worker `QuestionRunner`,
  and citation-closure validation;
- Packet 2 composes the real federated cache-only search backend and resolves
  exact immutable evidence across both storage families with partition closure;
- `QuestionRunner` currently accepts only a mapping-returning fake worker,
  records `model_invoked: false`, and `QuestionQueue.complete` rejects every
  model-invoked answer;
- the existing structured-turn client returns runtime-reported model identity,
  but there is no question-specific adapter, output schema, inert evidence
  prompt, or provider-free proof of its request boundary;
- service routes, MCP registration, installed runtimes, real model execution,
  provider acquisition, staging, and production remain outside this packet.

## Scope

- define a strict question-worker input/output seam and JSON output schema that
  accepts only `answer_from_evidence` over the frozen question, coverage, and
  allowed citation IDs;
- add a question-specific structured-turn adapter with canonical prompt
  construction, explicit untrusted-evidence delimiters, bounded source text,
  no retrieval/browser/provider/tool authority, and runtime-reported worker or
  model identity in the durable receipt;
- extend deterministic completion so fake and structured workers truthfully
  distinguish model invocation without allowing a worker to control correlation,
  digests, partitions, retry state, or acquisition receipts;
- implement explicit evidence-only fallback for configured model unavailability
  without retrying provider acquisition or presenting fallback as synthesis;
- harden validator behavior for unknown/fabricated citations, changed immutable
  refs, uncited assertions, statement-kind/support mismatches, omitted conflict
  sides, missing stale/partial labels, malformed or oversized output, and
  prompt-injection-shaped evidence;
- preserve bounded leases, one transient retry under the request's existing
  maximum, terminal validation failures, idempotent replay, and append-only
  failure/answer receipts;
- add provider-free tests using deterministic fake structured-turn clients;
  no model process or network call may run.

## Non-Goals

- no service HTTP route, client method, Go MCP schema/handler, generated public
  contract catalog, Skill guidance, configuration, changelog, version, release,
  or compatibility publication;
- no real Codex/model invocation or acceptance canary, and no claim that a
  protocol-only fake proves the installed model runtime;
- no source refresh, browser/provider, follow, schedule, notification, tracker,
  installed Skill/service/database, staging, deployment, or production effect;
- no P35 pull-request, merge, branch, worktree, or gate change;
- no semantic-entailment claim beyond deterministic structural grounding;
  calibrated grounding quality remains WI-008 ownership.

## Acceptance Criteria

1. A deterministic fake structured-turn client proves the exact prompt, output
   schema, no-tool/effect boundary, model identity receipt, and host-owned
   correlation/digest fields without starting a model or network process.
2. Valid supported and conflicting answers persist with exact immutable
   citations; stale and partial answers require their explicit uncertainty
   labels, and prompt-injection-shaped evidence remains inert input data.
3. Fabricated, changed, cross-partition, uncited, mislabeled, malformed,
   oversized, and conflict-collapsing outputs fail closed with safe durable
   terminal receipts and no leaked worker payload.
4. Model-unavailable handling distinguishes terminal unavailability from the
   request's explicit evidence-only fallback; transient failure receives no
   more than the already bounded retry and replay cannot duplicate an answer.
5. Focused question tests, affected service tests, compilation, source-runtime
   packaging, planning/lane checks, and the comprehensive provider-free suite
   pass at one clean remote-equal checkpoint suitable for coordinator review.

## Expected Write Surface

- `skills/last30days/scripts/lib/service_questions.py`;
- `skills/last30days/scripts/lib/service_question_contracts.py` only if the
  already versioned answer receipt needs a truthful additive model identity;
- one narrowly owned additive question-worker module under
  `skills/last30days/scripts/lib/` if separation improves the boundary;
- focused tests under `tests/` and this branch-local plan;
- `service/runtime-manifest.json`, ROADMAP.md, RUNBOOK.md, WI-003, and the
  active-lane catalog remain coordinator-owned integration joins.

## Execution Packet

- accountable human owner: repository operator;
- execution owner: one independent top-level Codex session;
- critical path: activation checkpoint, acceptance-level red fixtures,
  structured adapter, host validation/effects, fallback/retry/replay cases,
  comprehensive validation, clean publication, coordinator review;
- effect boundary: repository source plus provider-free temporary SQLite and
  deterministic fake clients only;
- retry bound: two implementation attempts per acceptance unit and one
  infrastructure-only validation retry;
- review bound: one focused self-review against the five frozen criteria;
- terminal condition: all criteria pass at one clean remote-equal checkpoint,
  or one exact contract/safety blocker is recorded without widening scope.

Subagents: not planned. The top-level owner may use one bounded support agent
only after revising this plan with a disjoint scope, result path, and one-level
fan-out.

## Definition Of Done

The provider-free question worker boundary produces only host-validated,
citation-closed, effect-truthful durable answer states at a clean published
checkpoint, while public transport, real model execution, and runtime effects
remain separately gated.

## Current Checkpoint

### Checkpoint P0098-C01 | 2026-09-14

Plan version: 1

State transition: `unplanned -> PLANNED`.

Progress classification: `outcome_progress`; Packet 3 now has one bounded
structured-answer outcome, exact adversarial proof, and explicit Packet 4 and
real-model boundaries.

Authority classification:

- `inherited_authority` for provider-free repository implementation after the
  coordinator integrates this lane registration;
- `human_gate` for P35 and every installed/runtime/provider/model/release/
  production effect;
- `scope_expansion` for Packet 4 public HTTP/MCP publication.

Evidence:

- base is exact canonical
  `20a36f91c866d81e03e4bfc521e1d2d270411d16`;
- CodeGraph is current at 374 files, 10,484 nodes, and 25,886 edges and confirms
  the existing queue, lease, runner, validator, and structured-turn seams;
- Graphiti is healthy but returned unrelated OpenClaw history, so current
  source, Plan 0079, note 0120, and closed Plans 0091/0096 are authoritative;
- no Packet 3 source implementation has begun.

Subagent status: `not_spawned`; this is a plan-only launch checkpoint.

Next action: validate and publish this plan-only branch, let the coordinator
register it on canonical main, then assign one independent top-level Codex
session to open and execute Packet 3.

### Checkpoint P0098-C02 | 2026-09-14

Plan version: 2

State transition: `PLANNED -> OPEN`.

Progress classification: `blocker_reduction`; the assigned top-level lane
owner has accepted custody, reconciled the published feature branch with the
current canonical remote target by merge, and established the provider-free
pre-implementation baseline.

Authority classification:

- `inherited_authority` for the branch-local provider-free implementation,
  deterministic fake-client tests, validation, commits, and publication;
- `human_gate` remains in force for every provider/model/runtime/browser,
  installed-state, release, staging, and production effect;
- `scope_expansion` remains in force for Packet 4 public HTTP/MCP/client and
  generated-catalog publication.

Evidence:

- runtime-reported owner thread is
  `01a09d89-319b-7120-aba7-78d1221f06d4`;
- the previously clean and remote-equal feature tip was
  `777441129e47f18e60f7956d765929c5e75e687e`;
- fetched `origin/main` is
  `487ec89e7a6c99d07f6623646c659111c5fbd270` and was merged without rebase or
  history rewriting at `7215a33ae77c879fa5626867e4d52da0d402b827`;
- focused pre-implementation question validation passed: 23 tests across
  `test_service_question_contracts.py`, `test_service_question_evidence.py`,
  and `test_service_questions.py`;
- activation validation passed 33 tests across the focused question suites and
  `test_plan_authority_audit.py`, and the goal-only planning contract passed;
- the active-only planning audit retained one coordinator-owned join:
  `plan not wired in RUNBOOK.md: 0098-2026-09-14-agent-question-answer-tracer-packet-3.md`;
  this lane does not own or edit `RUNBOOK.md`;
- the first CodeGraph status check reported the worktree as not initialized;
  this is classified as an infrastructure failure and retained rather than
  represented as a source or acceptance failure.

Subagent status: `not_spawned`; no delegation is authorized for this packet.

Next action: initialize the expected worktree-local CodeGraph derived state,
add acceptance-level red fixtures, and implement the bounded structured-answer
adapter and host validation without any real model or provider effect.

### Checkpoint P0098-C03 | 2026-09-14

Plan version: 3

State transition: `OPEN -> OPEN`; custody transferred from independent Codex
thread `01a09d89-319b-7120-aba7-78d1221f06d4` to coordinator Codex thread
`01a0860e-b671-7f62-b6ae-6c06a08e6852` after the independent process exhausted
its Codex usage allowance.

Progress classification: `outcome_progress`; acceptance tests and the bounded
implementation now pass the focused question surface without any provider,
model, browser, network, installed-state, or runtime effect.

Authority classification remains unchanged from P0098-C02.

Evidence:

- the independent lane published activation clean and remote-equal at
  `063c18b70474df28a7b5409c4de5f50c7e72d38a` before beginning source work;
- its process then stopped with an explicit usage-limit error after writing the
  first uncommitted acceptance-test draft; that draft was preserved;
- the coordinator reproduced the required red state as a collection failure
  because `lib.service_question_worker` did not yet exist;
- the implementation adds a typed structured-turn result, runtime-reported
  model identity, exact no-tool output schema, untrusted-evidence prompt
  boundary, citation-closed validation, safe terminal rejection receipts,
  explicit evidence-only fallback, and one bounded transient retry;
- 39 focused tests now pass across the new structured-worker suite and the
  existing question contract, evidence, and runner suites;
- the affected intelligence and plan-authority tests pass; three runtime-package
  tests retain the expected checksum/build failure because the runtime manifest
  is a coordinator-owned integration join and does not yet include the changed
  packaged service file;
- direct compilation of both changed service modules passes;
- adversarial fixtures cover fabricated, cross-partition, and changed-content
  citation identifiers, uncited claims, mismatched support labels, unexpected
  fields, changed action, malformed and oversized output, collapsed conflict
  sides, missing partial/stale labels, unavailable models, and duplicate replay;
- the prior owner initialized worktree-local CodeGraph derived state without
  first asking the operator as required when `.codegraph/` is absent. The index
  is untracked derived state, but the missing authorization question is retained
  here as a process-discipline deviation.

Subagent status: `not_spawned`; no subagents were used.

Next action: publish this implementation checkpoint, run affected and full
provider-free validation, then close the feature plan at the exact accepted
remote-equal checkpoint for coordinator integration.
