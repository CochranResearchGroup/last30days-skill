# Plan 0119 | Service Quality Real Adapters Packet 2

State: OPEN
Lane: P37
Work item: WI-008
Branch: feat/service-quality-real-adapters-v1
Target: main
Integration: merge
Roadmap: P37
Plan version: 1
Date: 2026-09-14
Execution owner: /root/wave4_wi008_plan
Coordination owner: /root
Requested model route: gpt-6-astra, high reasoning
Effective runtime model: unknown until reported

## Objective

Replace the fake corpus-integrity, acquisition-coverage, and retrieval quality
axes with digest-pinned read-only adapters over a sealed SQLite corpus and
normalized coverage receipts, while preserving the canonical report and zero-
effect receipt.

## Current State

Packet 1 integrated a deterministic provider-free quality harness with sealed
fake outcomes. WI-002 is `DONE`, unblocking the real PostSearchBackend adapter.
WI-003 is not yet closed, so real answer/citation grounding remains explicitly
deferred rather than inferred from fake evidence.

## Scope

- add strict digest-pinned fixture references to evaluation cases;
- add read-only SQLite corpus-integrity, acquisition-coverage, and post-search
  adapters while preserving fake defaults;
- retain redistribution-safe corpus/coverage/evaluation fixtures and generate
  large performance data during tests rather than committing a large database;
- detect corruption, cross-partition leakage, unknown denominators, partial or
  stale coverage, retrieval/filter/revision/provenance defects, and adapter
  failure without repair or false passes;
- expose one explicit provider-free real-fixture evaluator entrypoint.

## Non-Goals

No answer-grounding adapter, model/judge, provider, browser, live or installed
database/runtime, search implementation change, follow implementation change,
CI/schedule, staging/production, release/deployment, or issue mutation.

## Acceptance Criteria

1. Repeated v2 evaluations are byte-identical and bind request, policy,
   fixture, adapter, and report digests.
2. Integrity detects referential, digest, revision/head, duplicate, provenance,
   and access-partition defects using read-only SQLite.
3. Coverage uses declared opportunity denominators and reports partial,
   unavailable, stale, and unknown denominators truthfully.
4. Real post-search cases cover authorization, filtering, pagination/revision
   stability, provenance/ranking closure, empty/malformed behavior, and a
   deterministic generated performance sample.
5. Adapter crashes, corrupt fixtures, missing pinned heads, and unknown
   denominators cannot produce `passed`.
6. The effect receipt records zero provider, model, browser, runtime mutation,
   schedule, delivery, release, and tracker actions.
7. Focused/full provider-free validation, package checks, audits, and diff
   hygiene pass at the joined head.

## Ownership And Topology

One top-level implementation owner, no children, at most two implementation
attempts, one independent review, and one closed-world remediation. Lane writes
are `dev/last30days/quality/`, the explicit evaluator script, sealed fixtures,
quality tests, and this plan. Search/question/follow implementations, public
transports, catalogs, manifests, and authority projections remain coordinator-
owned. Plan 0119 has no direct implementation-file overlap with Plans 0117 or
0118.

## Stop Rules

Stop if fixtures cannot remain read-only/digest-pinned, a WI-002 contract change
is required, question grounding must be assumed, denominators are unknown but
treated as complete, work exceeds packet bounds, or any external/live/installed
effect is required.

## Definition Of Done

All seven criteria pass and Packet 2 is integrated. WI-008 remains `READY` for
answer-grounding and continuous-closeout work after WI-003; this packet alone
is not DONE.

## Current Checkpoint

### Checkpoint P0119-C01 | 2026-09-14

Plan version: 1

State transition: `unplanned -> PLANNED`; registration only.

Progress classification: `blocker_reduction`; all currently unblocked real
quality axes are bounded without claiming question grounding.

Authority classification:

- `inherited_authority`: Plan 0107 covers provider-free plan, activation,
  implementation, review, integration, and repo-local closeout;
- `human_gate`: provider/model/browser/live/installed runtime, CI/schedule,
  staging, production, release, deployment, and issue effects.

Subagent status and reconciliation:

- `joined`; one read-only planning specialist returned this scope. No
  implementation owner exists until activation.

Next action: integrate registration, publish exact isolated lane custody,
reconcile activation, then assign one owner.

### Checkpoint P0119-C02 | 2026-09-14

Plan version: 1

State transition: `PLANNED -> OPEN`.

Progress classification: `blocker_reduction`; exact isolated custody is
accepted from canonical registration merge `d6cf8252` at
`/home/ecochran76/workspace.local/last30days-skill-wi008-v2` on
`feat/service-quality-real-adapters-v1`.

Authority classification:

- `inherited_authority`: provider-free implementation, validation, branch
  publication, review, and integration under Plan 0107;
- every external-effect boundary in C01 remains held.

Subagent status and reconciliation:

- `assigned`; `/root/wave4_wi008_plan`, one owner with no children. Public
  transports, generated artifacts, docs, and authority remain coordinator-
  owned.

Next action: publish this activation checkpoint, reconcile canonical custody,
then implement the read-only adapters test-first within the lane write set.

### Checkpoint P0119-C03 | 2026-09-14

Plan version: 1

State transition: `OPEN -> OPEN`; Packet 2 implementation checkpoint accepted
on the isolated lane, pending independent review and coordinator integration.

Progress classification: `implementation_ready_for_review`; real acquisition, corpus, and
retrieval adapters bind their digest-pinned synthetic SQLite fixture and
adapter identity into the deterministic v2 report. Coverage fails closed for
partial, stale, unavailable, and unknown opportunity evidence; corpus checks
digest, current-revision, canonical-identity, provenance, and partition
closure; retrieval exercises the existing PostSearchBackend's authorization,
source filter, page cursor, revision, and provenance contracts.

Validation receipt:

- red test: real-adapter import was absent before implementation;
- `uv run pytest tests/test_service_quality.py tests/test_service_quality_real_adapters.py -q` -> `13 passed`;
- `POST_SEARCH_PERFORMANCE=1 uv run pytest tests/test_service_post_search_performance.py -q` -> `1 passed`;
- `uv run python -m compileall -q dev/last30days/quality dev/last30days/scripts/evaluate_service_quality.py` -> pass;
- `git diff --check` -> pass.

Broader compatibility receipt:

- `uv run pytest tests/test_service_quality.py tests/test_service_quality_real_adapters.py tests/test_service_post_search.py tests/test_service_supervisor.py tests/test_service_publication.py -q` -> `59 passed`.

The complete non-integration suite was started once but this execution
environment detached before retaining its terminal output; it is not claimed
as passed and remains a review/integration validation gate.

Authority classification:

- `inherited_authority`; all implementation and validation used only sealed,
  provider-free repository fixtures and read-only database access.

Effect receipt: provider, model, browser, live/installed service, runtime,
CI, schedule, release, deployment, and tracker effects remain zero. The
fixture adapter opens only a supplied synthetic SQLite path with `mode=ro` and
`PRAGMA query_only=ON`; it performs no repair or write.

Deferred gate: WI-003 remains unresolved. Answer/citation grounding is neither
evaluated nor implied by this packet, and WI-008 cannot transition to `DONE`.

Coordination exception: the active-plan audit remains false only because its
coordinator-owned `RUNBOOK.md` wiring has not yet been added for Plans 0117,
0118, and 0119. This lane did not edit that authority surface.

Next action: independent provider-free review, coordinator runbook
reconciliation, then merge-only integration if all lane and authority checks
remain accepted.

### Checkpoint P0119-C04 | 2026-09-14

Plan version: 1

State transition: `OPEN -> integration_ready`; plan remains `OPEN` until the
owned-fork PR merge and canonical reconciliation.

Progress classification: `blocker_reduction`; joined review converted three
false-pass paths into explicit failed/incomplete results and bound reports to
the exact verified fixture candidate.

Authority classification:

- `inherited_authority` covered sealed provider-free fixtures, read-only
  evaluation, tests, review and owned-fork publication;
- network, provider, model, browser, live/installed runtime, schedule, release,
  deployment and tracker effects remained zero.

Review and remediation evidence:

- actual canonical content hashes are recomputed, historical/current owner and
  partition closure are verified, and corrupt or dangling revisions fail;
- nonempty SQLite WAL/journal companions are rejected and reads use immutable,
  query-only connections, so the pinned main-file digest is the data read;
- fixture metadata binds all six candidate-head fields, and the runner rejects
  an adapter/request candidate mismatch before evaluation;
- the initial six-finding joined review returned `PASS` at exact checkpoint
  `c8bf22b09981a18fe970d1dc8cf92b70a71b6adb` after focused remediation;
- focused real-adapter regressions and the complete 3,086-test Python suite
  pass. The full Go suite and vet pass.

Next action: integrate this reviewed Packet 2 head. WI-008 remains `READY`, not
`DONE`; answer-grounding and wider quality closure remain later bounded work.
