# Plan 0103 | Question Contract Corrective Packet

State: OPEN
Lane: P51
Work item: WI-009
Branch: fix/question-contract-repair-v1
Target: main
Integration: merge
Roadmap: P51
Plan version: 1
Date: 2026-09-14
Session owner: coordinator Codex thread `01a09f76-8024-7960-a7c5-c0469cf99153`

## Objective

Repair the two accepted question-answering contract defects so malformed
structured worker output and direct evidence-only answers always terminate
durably inside the caller's contract and answer-character budget.

## Current State

- the lane starts from clean canonical `origin/main` at
  `5422fc2bb7d1e39c87e2657c1551d58a525a3e17`;
- `QuestionRunner.run_once` converts `QuestionWorkerError` and
  `QuestionValidationError` into durable outcomes, but a
  `QuestionContractError` raised while constructing a structured answer can
  escape and leave the task `running` until lease expiry;
- direct `answer_mode=evidence_only` copies selected evidence text without
  enforcing the request's total `max_answer_characters` bound;
- the exact regressions are not covered by the currently green broad suite;
- tracker reconciliation and WI-000 through WI-009 publication are complete;
  P35 reconciliation remains serialized behind this packet.

## Scope

- add one public-seam regression proving malformed structured worker output
  produces a safe durable terminal rejection without lease-expiry recovery;
- make the smallest host-owned correction that classifies contract-construction
  failures as non-retryable validation failures without leaking worker output;
- add one public-seam regression proving direct evidence-only answers respect
  the request's total `max_answer_characters` across multiple evidence items;
- enforce that total budget in the direct evidence-only path while preserving
  citation closure, deterministic ordering, and existing structured-worker and
  model-unavailable fallback behavior;
- validate the focused question surface, affected package and MCP surfaces,
  comprehensive Python and Go suites, planning and lane contracts, manifest
  drift, and the published pull-request diff.

## Non-Goals

- no public schema, HTTP route, MCP interface, answer-mode, retry-policy, or
  service-version change;
- no broader question-answer refactor, new synthesis behavior, acquisition,
  follow, monitor, quality, or unrelated product feature;
- no model, provider, browser/profile, network, installed database/runtime,
  staging, production, release, tag, schedule, or deployment effect;
- no GitHub issue mutation, P35 reconciliation, Packet 2, or cross-service
  follows work.

## Acceptance Criteria

1. An `answered` structured-worker result with no statements finishes in a safe
   durable terminal state with a non-retryable error receipt, releases its
   lease, and does not require lease-expiry recovery.
2. A direct evidence-only request with a small `max_answer_characters` and
   multiple selected evidence items returns total statement text no longer than
   that limit while retaining valid citations and deterministic ordering.
3. The two focused regression commands are observed red before their respective
   implementation changes and green afterward.
4. Existing question contracts, evidence retrieval, structured worker,
   service/package, and MCP behavior remain green; `uv run pytest` and
   `go test ./...` pass at the integration candidate.
5. Planning, active-lane, runtime-manifest drift, and `git diff --check` gates
   pass, and the branch is published, self-reviewed, and integrated through a
   normal owned-fork pull request with canonical ancestry verified.

## Expected Write Surface

- `skills/last30days/scripts/lib/service_questions.py`;
- focused question tests under `tests/`;
- this plan and coordinator-owned projections in `ROADMAP.md`, `RUNBOOK.md`,
  `docs/dev/active-lanes.yaml`, and
  `docs/dev/work-items/WI-009-productization-readiness-remediation.md`;
- no service runtime manifest change is expected because the packaged source
  set does not change shape, but manifest drift must still be checked.

## Execution Packet

- accountable human owner: repository operator;
- execution and coordination owner: this top-level Codex session;
- critical path: publish lane registration, one red/green contract-failure
  slice, one red/green evidence-budget slice, affected validation,
  comprehensive validation, published-diff self-check, pull-request merge, and
  canonical readback;
- effect boundary: repository files plus provider-free temporary SQLite state;
- work-unit bound: two implementation attempts per acceptance criterion and
  one infrastructure-only validation retry;
- review bound: one focused closed-world self-review against the five frozen
  criteria and critical regressions introduced by the repairs;
- terminal condition: every criterion is proven at a merged canonical commit,
  or one exact contract, custody, or validation blocker is durably recorded
  without widening scope.

Subagents: not planned or authorized for this packet.

## Definition Of Done

Both accepted defects are regression-locked and corrected through existing
public interfaces, all required provider-free validation passes, the owned-fork
pull request is merged, canonical `main` contains the repair, and P51 is ready
for the separately planned P35 reconciliation packet.

## Current Checkpoint

### Checkpoint P0103-C01 | 2026-09-14

Plan version: 1

State transition: `unplanned -> OPEN`.

Progress classification: `blocker_reduction`; the exact corrective lane now has
bounded ownership, write surfaces, acceptance evidence, effect limits, and a
clean current-main checkout before implementation.

Authority classification:

- `inherited_authority` for provider-free repository edits, tests, validation,
  branch publication, pull-request creation, self-review, and integration;
- `human_gate` for every runtime, provider, browser, release, deployment,
  production, or GitHub issue mutation;
- `scope_expansion` for P35 reconciliation and every unrelated feature packet.

Evidence:

- canonical and lane base are
  `5422fc2bb7d1e39c87e2657c1551d58a525a3e17`;
- all registered worktrees were clean and remote-equal at activation;
- issue #55 is open, uniquely mapped to WI-009, and no pull request overlaps
  this corrective surface;
- CodeGraph is healthy at 376 files, 10,537 nodes, and 26,059 edges and locates
  the two defects at the existing `QuestionRunner` and evidence-only seams;
- Graphiti is healthy but the focused `last30days_skill_main` query returned ten
  older unrelated facts, so current repository and forge evidence remains
  authoritative;
- active-only planning, goal-only planning, and catalog-only lane audits passed
  before activation.

Subagent status: `not_spawned`.

Next action: publish this registration checkpoint, then execute the two
regression-first vertical slices without any runtime or provider effect.
