# Plan 0117 | Question Public Runtime Closeout Packet 4

State: PLANNED
Lane: P36
Work item: WI-003
Branch: feat/question-public-runtime-closeout-v1
Target: main
Integration: merge
Roadmap: P36
Plan version: 1
Date: 2026-09-14
Execution owner: unassigned until activation
Coordination owner: /root
Requested model route: gpt-6-astra, high reasoning
Effective runtime model: unknown until reported

## Objective

Close WI-003 provider-free by completing the scoped question/evidence contract,
additive HTTP/CLI/MCP transports, bounded worker lifecycle, and fresh-client
isolated-runtime acceptance over the closed WI-002 search surface.

## Current State

Question contracts, durable queue/answer state, evidence resolution, and
adversarial Packet 1-3 tests are integrated. WI-002 and WI-001 are `DONE`.
Remaining gaps are full search-filter propagation, explicit temporal handling,
profile/partition authorization for status/evidence reads, bounded wait and
model-unavailable behavior, public schemas/transports, and exact runtime proof.

## Scope

- propagate all eight accepted WI-002 filters without widening search;
- honor supported temporal constraints and reject unsupported non-null intent;
- authorize status and citation reads before revealing existence or content;
- compose bounded evidence-only/unavailable-model and injected fake-worker test
  paths without a production fake switch;
- expose additive question/status/evidence HTTP, Python client, CLI, and MCP
  contracts within the existing 128 KiB transport envelope;
- prove search-to-question-to-status-to-citation read in one exact versioned
  isolated development artifact with exact-owner teardown.

## Non-Goals

No provider/model canary, browser, acquisition, installed service/database,
schedule, delivery, staging, production, release publication, deployment,
issue mutation, semantic quality judgment, or WI-005/WI-006/WI-008 work.

## Acceptance Criteria

1. All WI-002 filters are preserved and enforced before evidence selection;
   unsupported temporal meaning fails explicitly.
2. Cross-profile status/evidence access, guessed IDs, malformed refs, and
   changed digests fail without existence or content leakage.
3. Durable replay, pending waits, cancellation, retries, and client timeouts
   are bounded; status/evidence reads never execute work.
4. HTTP, Python client, CLI, and MCP discovery/annotations are equivalent and
   every response fits the 128 KiB envelope.
5. Both storage families cover supported, contradictory, stale, partial,
   empty, unsupported-claim, unavailable-model, fallback, truncation, and
   immutable-revision cases.
6. Fresh-client isolated-runtime acceptance binds source, artifact, versions,
   schema/catalog/manifest digests, process identity, expected ledger-only
   writes, unchanged corpus/acquisition/schedule/delivery state, and teardown.
7. Focused/full Python, Go test/vet, generation, package/lifecycle,
   reproducibility, audits, and diff checks pass at the joined head.

## Ownership And Topology

One top-level implementation owner, no children, at most two implementation
attempts, one independent review, one closed-world remediation, and one
infrastructure-only validation retry. Lane-owned writes are question contracts,
question service/application composition, focused fixtures/tests, repo-only
dogfood/receipt, and this plan. Shared app/HTTP/client/CLI/MCP, catalogs,
versions, manifests, product docs, and authority projections are coordinator-
owned and serialized against Plan 0118.

## Stop Rules

Stop on ambiguous process/custody identity, partition leakage, ignored temporal
intent, unbounded wait/retry, response overflow, artifact/source mismatch,
unregistered shared edits, or any required real provider/model/browser/
credential/installed/live effect.

## Definition Of Done

All seven criteria pass at an independently reviewed canonical merge and WI-003
is truthfully eligible for `DONE` without claiming semantic-quality or live-
model acceptance.

## Current Checkpoint

### Checkpoint P0117-C01 | 2026-09-14

Plan version: 1

State transition: `unplanned -> PLANNED`; registration only.

Progress classification: `blocker_reduction`; the final WI-003 packet is
bounded and dependency-ready, but has no branch/worktree custody yet.

Authority classification:

- `inherited_authority`: Plan 0107 covers this provider-free plan,
  activation, implementation, review, integration, and repo-local closeout;
- `human_gate`: every provider/model canary, browser, live/installed runtime,
  schedule, staging, production, release, deployment, and issue mutation.

Subagent status and reconciliation:

- `joined`; one read-only planning specialist returned this scope. No
  implementation agent is assigned until registration integrates.

Next action: integrate registration, create and publish exact isolated lane
custody from canonical main, reconcile activation, then assign one owner.
