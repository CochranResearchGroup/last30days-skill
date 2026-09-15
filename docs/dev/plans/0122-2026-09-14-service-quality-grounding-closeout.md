# Plan 0122 | Service Quality Grounding Closeout

State: CLOSED
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

### Checkpoint P0122-C03 | 2026-09-14

Plan version: 1

State transition: `OPEN -> ready_for_independent_review`.

Progress classification: `provider_free_implementation_complete`; the real
fixture registry now supplies `QuestionGroundingAdapter`. It reads only the
candidate-bound sealed fixture and measures request/retrieval/answer digest
correlation, citation equality and dereference, partition closure, declared
partial/stale coverage, expected outcomes, and the provider-free receipt. It
does not assess semantic entailment or production quality.

Acceptance evidence:

- TDD started with an import failure before the adapter existed; the focused
  real-adapter suite now passes `9` tests, including supported, no-evidence,
  conflicting, partial/stale, tampered-correlation/citation/dereference,
  partition-leakage, malformed-answer, unknown-partition, candidate-mismatch,
  and unsealed-fixture paths.
- `uv run pytest tests/test_service_quality.py tests/test_service_quality_real_adapters.py tests/test_service_question_evidence.py tests/test_service_questions.py tests/test_service_question_application.py tests/test_service_post_search.py tests/test_service_supervisor.py tests/test_service_publication.py -q` passed `102` tests.
- `POST_SEARCH_PERFORMANCE=1 uv run pytest tests/test_service_post_search_performance.py -q`, compilation, and `git diff --check` passed.
- `uv run pytest tests/test_hermes_skillignore.py tests/test_plugin_contract.py tests/test_build_skill_artifact.py -q` passed `7` package-boundary tests.
- A full-suite attempt is blocked outside this lane by
  `tests/test_hotfix_runtime_drill.py::test_upgrade_baseline_uses_disposable_installer_and_cleans_owned_processes`: the asserted baseline is `0.3.117` while current metadata is `0.3.118`. No version or runtime-drill change was made here.

Effect receipt: zero network requests, model calls, browser actions, runtime
mutations, provider calls, installed-database access, or live effects; all
fixtures were temporary local SQLite files and adapters opened their owned
reads query-only.

Ownership/reconciliation: lane-only files changed. Coordinator joins remain
independent review, shared authority/roadmap reconciliation, and any canonical
integration/DONE decision. The full-suite version-baseline discrepancy is a
coordinator-owned gate, not authorization to alter the runtime drill.

Next action: review this isolated branch with the recorded non-lane full-suite
gate, then integrate only after the coordinator's joined acceptance.

### Checkpoint P0122-C04 | 2026-09-14

Plan version: 1

State transition: `ready_for_independent_review -> reviewed_accepted`.

Progress classification: `joined_acceptance`; the grounding adapter is present
at joined head `5c6fa0210b7d3d18b82a10ab7c5e4377a21cbce6`, and the independent
review's durable-correlation and resolver-boundary findings are closed.

Authority classification:

- `inherited_authority` covered only provider-free fixture, adapter, test, and
  integration work;
- every provider, model, browser, live-data, installed-runtime, release,
  deployment, delivery, and issue-mutation boundary remained held.

Acceptance evidence:

- repeated citations resolve once and score per occurrence; more than twenty
  unique citations resolve in bounded batches;
- stored request, retrieval, task, and answer identities and digests are
  correlated with decoded immutable records;
- the independent joined re-review passed all four remediation probes and `59`
  focused tests without rerunning either packaged dogfood acceptance.

Subagent status and reconciliation: `joined`; the implementation owner and
independent reviewer are complete, with no children or excluded effects.

Next action: pass the corrected full suite, merge the reviewed integration PR,
then reconcile WI-008 and this plan to terminal state.

### Checkpoint P0122-C05 | 2026-09-14

Plan version: 1

State transition: `reviewed_accepted -> CLOSED`.

Progress classification: `outcome_progress`; the corrected grounding adapter
joined through reviewed PR 95 at canonical merge
`ffb561df79e0bb457dac46012a01a11757d5d307`, the corrected full suite passed,
and Plan 0107 repeated structural-grounding acceptance on canonical source
`448d0797`.

Authority classification:

- `inherited_authority` covered review, validation, canonical integration and
  repo-local closure;
- model/judge, provider, production-sample, installed-runtime and tracker
  effects remained prohibited and unused.

Acceptance disposition: all four real read-only axes pass; the final joined
quality phase reported zero network, model, browser, database-write or runtime
mutation effects and fixture SHA-256
`ec9db571b1fd0adf21081d2888037fa05eee981d00a7791110a038e5a0271f45`.
This is structural evidence correlation and citation closure, not semantic
entailment or production-quality proof. WI-008 is `DONE`; active plan is none.
