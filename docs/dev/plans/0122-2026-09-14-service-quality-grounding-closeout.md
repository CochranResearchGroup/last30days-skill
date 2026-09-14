# Plan 0122 | Service Quality Grounding Closeout

State: OPEN
Lane: P37
Work item: WI-008
Branch: feat/service-quality-grounding-closeout-v1
Target: main
Integration: merge
Roadmap: P37
Plan version: 1
Date: 2026-09-14
Execution owner: unassigned
Coordination owner: /root
Requested model route: gpt-6-astra, high reasoning
Effective runtime model: unknown until reported

## Objective

Close WI-008 provider-free by replacing the remaining fake grounding axis with
a digest-pinned read-only adapter over real durable question, frozen retrieval,
answer, citation and evidence records, explicitly limited to structural
grounding rather than semantic or production quality.

## Current State

Plans 0092 and 0119 are closed, WI-002/WI-003 are `DONE`, and three real
quality axes are accepted. The remaining provider-free gap is real structural
answer grounding over the durable question/evidence records.

## Definition Of Done

All four real axes pass their adversarial acceptance at one reviewed joined
checkpoint, canonical integration is recorded, and WI-008 is reconciled to
`DONE` without a semantic, model or production-quality claim.

## Scope

- add `QuestionGroundingAdapter` to the real-fixture quality adapter registry;
- extend sealed synthetic SQLite fixtures with deterministic evidence-only
  question outcomes across legacy and temporal evidence;
- validate request/retrieval/answer correlation, immutable IDs/digests, citation
  membership/equality/dereference, partition closure, expected outcome and
  required partial/stale uncertainty disclosure;
- emit separate measurable grounding metrics while preserving the canonical
  report and the other three real axes.

## Non-Goals

No semantic entailment judgment, model/judge/provider call, question/search
implementation or public transport change, live/installed database/runtime,
CI/schedule, production sample, release/deployment, delivery or issue mutation.

## Acceptance Criteria

1. Repeated four-axis reports are byte-identical and bind request, policy,
   fixture, candidate, adapter and report digests.
2. Grounding accepts supported/conflicting, partial/stale and no-evidence
   structural outcomes across both storage families.
3. Tampered correlation, fabricated/changed citations, dereference loss,
   partition leakage, missing disclosure, malformed answers, unknown
   denominators, candidate mismatch and unsealed fixtures cannot pass.
4. Acquisition, corpus and retrieval results remain unchanged.
5. Focused grounding/quality/question/evidence/PostSearch tests, generated
   performance, compilation, package/audit/diff and full joined validation pass.
6. The effect receipt remains zero for all external effects and the closeout
   never labels structural citation checks as semantic or production quality.

## Ownership And Topology

One top-level owner, no children, at most two implementation attempts, one
independent joined review and one closed-world remediation. Lane writes are
`dev/last30days/quality/adapters.py`, optional export wiring,
`tests/test_service_quality_real_adapters.py`, and this plan. Coordinator owns
question/evidence/search/public transports, generated artifacts, product docs
and authority projections.

## Stop Rules

Stop if a question/evidence/public-contract edit is required; if the fixture
cannot remain candidate-bound, WAL-free and immutable/query-only; if semantic
judgment requires a model; if unknown/partial/stale evidence would be treated
as complete; or before any excluded effect.

## Next Action

Integrate registration, publish isolated custody and assign one owner.
Successful reviewed canonical integration may move WI-008 to `DONE` without
making a production- or model-quality claim.

### Checkpoint P0122-C01 | 2026-09-14

Plan version: 1

State transition: `unplanned -> PLANNED`.

Progress classification: `blocker_reduction`; WI-003 closure releases the last
real provider-free quality axis while preserving semantic-judgment boundaries.

Authority classification: `inherited_authority` for registration and later
provider-free work; all Non-Goals remain `human_gate` effects.

Subagent status and reconciliation: `joined`; one read-only planner completed.
Implementation owner remains unassigned pending exact custody.

Next action: integrate registration and publish a plan-only activation ref.

### Checkpoint P0122-C02 | 2026-09-14

Plan version: 1

State transition: `PLANNED -> OPEN`.

Progress classification: `implementation_ready`; exact isolated custody is
accepted from canonical registration merge `e0fab676`.

Authority classification:

- `inherited_authority` covers the registered provider-free write set only;
- every external-effect gate remains held.

Subagent status and reconciliation: `assigned`; `/root/wave4_wi008_plan`, one
owner, no children. Implementation waits for activation reconciliation.

Next action: publish this plan-only checkpoint and return exact custody.
