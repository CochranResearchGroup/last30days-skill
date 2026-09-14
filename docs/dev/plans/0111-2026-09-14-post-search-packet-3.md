# Plan 0111 | Bounded Hybrid Post Search Packet 3

State: OPEN
Lane: P33
Work item: WI-002
Branch: feat/post-search-v3
Target: main
Integration: merge
Roadmap: P33
Plan version: 1
Date: 2026-09-14
Execution owner: /root/wi002_packet3_planning
Coordination owner: /root
Requested model route: gpt-6-astra, high reasoning
Effective runtime model: unknown (not reported by runtime)
Effective reasoning effort: unknown (not reported by runtime)

## Objective

Complete WI-002 Packet 3 with provider-free semantic candidates,
deterministic reciprocal-rank fusion, reproducible explanations, bounded
responses and coverage diagnostics, plus measured 10,000-post local evidence.

## Current State

Packets 1-2 are integrated through PRs 36 and 79. Both storage families,
complete filters, current/all revisions, cross-store identity, and stable
snapshot pagination exist. Packet 3 source acceptance is complete at
P0111-C02: local stored-vector ranking, reproducible RRF, byte-bounded pages,
public transport parity, and the frozen 10,000-post measurement pass.
Generated catalog/runtime-manifest reconciliation, independent review, joined
validation, and integration remain coordinator-owned; the plan stays OPEN.

Implementation resumed on coordinator assignment after activation PR 82 at
`5471e928b1f4c7867ea15de1d4e203b3315bb6e4`; merging exact `origin/main` was a
fast-forward retaining activation ancestry. Search-specific shared sections
listed below are now assigned; generated artifacts remain coordinator-owned.

## Frozen Measurement Gate | 2026-09-14

Before product edits, the synthetic 5,000-legacy/5,000-temporal current-post
fixture measured first page **0.468072 seconds**, cursor page **0.008679
seconds**, peak process RSS **88,348 KiB**, and first response **18,888 bytes**.
The database SHA-256 is
`1905f0a5684ff9538f3588702040e80aa926517e0d4c891c831921a9524d8c9f`.
Environment: CPython 3.12.13, Linux 6.6.87.2 WSL2 x86_64, glibc 2.39.
Command: `POST_SEARCH_PERFORMANCE=1 uv run pytest
tests/test_service_post_search_performance.py --override-ini addopts='' -q -s`.
Two fixture-construction failures (import path and duplicate synthetic URL)
preceded the valid baseline; neither reached search measurement.

Freeze before implementation: first page <= **5.0 seconds**, retained cursor
page <= **0.1 seconds**, peak complete measurement-process RSS <= **262,144
KiB**, complete UTF-8 response <= **131,072 bytes**. The roughly tenfold
first-page margin accommodates reading/validating 10,000 stored vectors;
the threefold memory ceiling is a bounded process gate, not serialized cache
size. One baseline and one final sample are the primary measurement; one
diagnostic rerun is allowed only after a declared failure. No percentile,
large-text, all-revision, production latency, or semantic-quality claim follows
from this short-text fixture. Correctness, resources, and evidence integrity
receive separate verdicts; a resource failure does not erase valid correctness
tests. Schema/source-data drift invalidates the affected benchmark comparison;
database mutation invalidates its effect-free verdict.

## Scope

- rank authorized prefiltered candidates through lexical and local deterministic
  semantic channels without creating embeddings or inheriting provider access;
- fuse independently ordered channels through a versioned deterministic RRF
  contract with reproducible component ranks, scores, and stable tie breaks;
- preserve exact revision/evidence identity, access partitions, retained cursor
  inputs, and explicit semantic coverage/degradation for both storage families;
- fit complete UTF-8 responses beneath the existing transport bound without
  skipping hits across budget-shortened pages;
- baseline first, then freeze and prove explicit latency/RSS budgets on one
  opt-in synthetic 10,000-post fixture split across both families;
- keep Python, HTTP, MCP, Skill, and configuration guidance aligned.

## Non-Goals

No materialized unified index, schema migration, general provider embedding
plumbing, durable cursor redesign, WI-003 answer change, release/version,
installed runtime, provider/browser, schedule, staging, or production effect.

## Acceptance Criteria

1. Semantic-only, lexical-only, dual-channel, tied, zero-vector, and missing or
   mismatched-vector fixtures reproduce deterministic RRF order and coverage.
2. Unauthorized and filtered-out candidates never reach either ranker; current/
   all collisions cannot promote stale matching revisions.
3. Cursor pages pin ranking inputs and remain stable across publication or
   semantic metadata change; existing tamper/access/expiry cases stay green.
4. Complete serialized responses fit the transport limit or fail with one
   stable bounded error; concatenated shortened pages equal logical order.
5. Python application/HTTP and fresh Go MCP clients agree, WI-003 evidence and
   `/v1/query` compatibility remain green, and no effectful call is admitted.
6. A durably recorded baseline precedes the frozen 10,000-post latency/RSS
   budget, and the final opt-in fixture meets it without erasing correctness
   evidence on a performance failure.
7. The exact clean branch checkpoint is published for coordinator review.

## Execution Packet

- one top-level implementation owner, no children; two implementation attempts,
  one independent broad review, and one closed-world remediation pass;
- lane-owned writes: post-search backend or narrow ranking module, focused
  search/ranking/performance fixtures and tests, this plan;
- coordinator-assigned overlaps: search-specific Python contract/schema, app
  wiring only if required, MCP search tool/tests, and search guidance;
- coordinator-exclusive: generated catalogs, runtime manifest, roadmap,
  runbook, active lanes, and work-item state;
- terminal condition: published source acceptance for Packet 3 or one exact
  recorded blocker; do not begin Packet 4.

## Definition Of Done

All seven criteria pass at one published checkpoint suitable for joined review,
or one exact blocker is recorded without widening the packet.

## Current Checkpoint

### Checkpoint P0111-C01 | 2026-09-14

Plan version: 1

State transition: `planned -> activation_published`; plan state is `OPEN`.

Progress classification: `hardening`; execution custody and the activation
boundary are recorded. This checkpoint claims no product acceptance result.

Authority classification:

- `inherited_authority` under Plan 0107 and the coordinator's activation-only
  assignment permits editing this plan, validation, one coherent commit, and
  publication to `origin/feat/post-search-v3`;
- the accountable human owner is the repository operator; execution owner is
  `/root/wi002_packet3_planning`, a direct child of coordinator `/root`;
- this assignment stops after publication readback. No source implementation,
  shared-authority edit, benchmark, runtime, provider/browser, schedule, issue,
  release, staging, production, or durable-memory write is included.

Base and custody evidence:

- assigned worktree:
  `/home/ecochran76/workspace.local/last30days-skill-wi002-v3`;
- branch: `feat/post-search-v3`; initial clean HEAD:
  `7f65c4285146e8d4dabd417617584fe7042a582f`, the PR 81 Wave 2 registration merge;
- a fresh `git ls-remote --heads origin main feat/post-search-v3` returned
  `refs/heads/main` at that exact base and no existing Packet 3 remote branch;
- `origin` is `CochranResearchGroup/last30days-skill`; `upstream` push is
  disabled. The publication target is exactly `refs/heads/feat/post-search-v3`;
- the canonical worktree remains reserved for coordinator-owned `main`.
  Its fresh readback was clean `main` at the exact base above. No checkout,
  ref custody, or default-branch reassignment is performed here.

Inputs and validation boundary:

- Plan 0107, this Plan 0111, WI-002, architecture note 0117, and the closed
  Plans 0084/0108 provide the execution and acceptance authority;
- planning, documentation, Git/worktree, commit/publication, validation,
  work-item, operating-model, model-selection, and collaborative-workflow
  policies were reread for this activation;
- current repository authorities are sufficient for this bounded activation:
  Graphiti discovery is `skip`; prior read-only planning inspected the current
  backend and public contract with CodeGraph and found the lexical-only gap;
- activation validation consists of the plan-authority audit, `git diff
  --check`, exact one-file diff inspection, and post-push clean worktree plus
  local/remote SHA equality. Product tests and benchmarks are intentionally
  unrun; no product or performance acceptance is implied.
- `python dev/last30days/scripts/audit_plan_authority.py` passed with zero
  issues against the existing canonical projection (two active plans);
  `git diff --check` passed, and direct diff inspection confirmed this plan
  alone changes with the required owner, `OPEN` state, and activation bounds.
  Canonical activation projection remains the coordinator's next join.

Overlap and dependency handoff:

- the lane will own the backend or narrow ranking module and focused tests;
- before product execution, the coordinator assigns search-specific sections
  of `service_contracts.py`, `post-search-contracts-v1.json`, optional app
  wiring, `mcp/internal/tools/service_tools.go` and its tests, and search
  paragraphs in `SKILL.md` and `CONFIGURATION.md`;
- generated catalogs, `service/runtime-manifest.json`, roadmap, runbook,
  active-lane catalog, and work-item projections remain coordinator-exclusive;
- WI-003 transport work may consume the frozen search interface, but its
  answer semantics and overlapping shared files are not lane-owned. WI-008
  consumes the accepted ranking/coverage result after integration;
- two implementation attempts, one broad independent review, and one
  closed-world remediation pass remain the inherited execution bounds.
  Activation consumes no implementation attempt.

Model and worker receipt:

- requested route: `gpt-6-astra`, high reasoning, justified by ranking,
  identity, access, and cursor correctness across two storage families;
- effective runtime model and reasoning effort: unknown, not reported;
- one active lane owner; no children spawned. The coordinator owns
  reconciliation and final acceptance of this publication.

Stop and next action:

- stop after reporting the exact publication SHA, clean status, and remote
  equality to the coordinator; do not start product code or Packet 4;
- on resume, verify the published branch and assigned worktree, reread this
  checkpoint and current policies, and obtain the coordinator's reconciled
  implementation assignment and exact shared-surface ownership;
- stop and report any custody mismatch or newly conflicting write ownership;
  no automatic implementation, benchmark, provider, or runtime continuation.

### Checkpoint P0111-C02 | 2026-09-14

Plan version: 1

State transition: `activation_published -> source_acceptance_met_pending_generated_join`.

Progress classification: `outcome_progress`; all Packet 3 source behavior and
measurement criteria have provider-free evidence. Generated/joined acceptance
and integration are not claimed by this checkpoint.

Authority classification:

- `inherited_authority` under Plan 0107 and the coordinator's implementation
  continuation covers source changes, fixture tests, this plan, commit, and
  exact branch publication;
- coordinator explicitly assigned search-specific contracts/schema, MCP and
  guidance sections. A later exact allocation also covered the search-only
  `PostSearchResponseTooLargeError` and sibling HTTP 413 mapping; other HTTP
  endpoint behavior remains unchanged;
- no generated catalog, runtime manifest, roadmap, runbook, active-lane,
  work-item, issue, release, installed runtime, provider/browser, schedule,
  staging, production, or durable-memory write is included.

Custody and scope:

- the assigned worktree and branch remain those in C01;
- freshly fetched `origin/main` resolved to
  `5471e928b1f4c7867ea15de1d4e203b3315bb6e4` (activation PR 82). The merge was
  a fast-forward retaining `f1f5f4dd915e7d6cbf75dccbbf51999b6c25f97f` ancestry;
- no app wiring change was required. The existing backend now imports the
  narrow new `service_post_search_ranking.py` module, which the coordinator
  must include in the regenerated runtime manifest;
- product writes are the backend/ranker, search-specific contracts/schema,
  narrowly allocated HTTP error mapping, MCP search description/test, and
  search guidance. New tests/fixtures cover ranking, public MCP, and opt-in
  performance. Existing source/query/answer semantics are not rewritten.

Acceptance evidence:

1. Legacy exact-version chunk vectors and promoted/superseded temporal
   source-entry vectors are selected only for SQL-filtered, resolved current/
   all post representatives. Temporal matching also verifies source, partition,
   URL, and exact retained source text. Query encoding is always built-in
   `local-hash-v1` with 256 dimensions; it cannot inherit an external provider.
   No corpus embedding is created or written. Missing, mismatched, invalid,
   and zero vectors remain explicit per-family coverage states.
2. `post-rrf-v1` fuses positive lexical and semantic ranks with constant 60.
   Raw scores, component ranks, and stored-vector locator/digest reproduce the
   fused score, which Python validates. Semantic-only and dual-channel results,
   ties, degradation, filtering, stale current replicas, and explicit all-mode
   historical evidence have deterministic fixtures.
3. Search heads bind the selected vector input digests and ranking version.
   Retained cursor pages and coverage survive embedding changes/publication;
   copied public dictionaries cannot mutate the retained head. Existing
   mismatch, expiry, restart, eviction, access, and sort fixtures still pass.
4. The backend fits the entire serialized UTF-8 page, coverage, and cursor to
   131,072 bytes. Multibyte pages shorter than the requested page size traverse
   every result exactly once; even initially final-sized requests retain a
   snapshot when byte limits create pagination. Indivisible provenance fails
   with bounded HTTP 413 `post_search_response_too_large`, without dropping refs.
   Malformed `/v1/query` still returns its existing invalid-contract response.
5. A fresh Go MCP process crosses an in-process Python fixture HTTP server and
   returns the same semantic-only post pages as the typed client. Tests use
   temporary synthetic databases and ephemeral fixture sockets; no service
   runtime is provisioned or installed. The MCP child is terminated/waited and
   the fixture server closed. Before/after database readbacks are unchanged.
6. The final primary 10,000-post sample passes every frozen gate:

   | Measure | Baseline | Frozen maximum | Final |
   | --- | ---: | ---: | ---: |
   | First page seconds | 0.468072 | 5.0 | 1.380568 |
   | Retained cursor seconds | 0.008679 | 0.1 | 0.009973 |
   | Peak process RSS KiB | 88,348 | 262,144 | 118,372 |
   | First response UTF-8 bytes | 18,888 | 131,072 | 26,167 |

   Both families have exactly 5,000 available stored-vector posts. The final
   database SHA-256 is
   `47426a386d1d83dea73af521b4a2ba19763a8a161a2423d63c75acb1645c383b`.
   Raw database hashes identify each run, not cross-run corpus equality:
   schema bootstrap stamps `access_partitions.created_at` with `datetime('now')`.
   The same fixed source-row/vector fixture generated both samples; its final
   formatted source SHA-256 is
   `4dedebf32f1d93ee6c5db89522de6e308c24c2116505669202fd217122ef8b73`.
   The final sample ran while focused compatibility tests also ran on the host;
   results are absolute single-sample gates, not a controlled relative-speed
   or percentile claim. No diagnostic benchmark rerun was used.
7. This plan and source acceptance are committed/published to the exact owned
   fork branch, followed by clean worktree and local/upstream/remote equality
   readback. The publication SHA is reported by Git, not embedded into itself.

Validation receipts (performed by this lane owner):

- TDD red/green: semantic-only search first returned no hits; multibyte pages
  first exceeded the transport budget (364,831 bytes); corrupted RRF rank
  first escaped contract validation; the indivisible-provenance HTTP test
  first returned generic `invalid_contract`. Each exact reproducer passed
  after its bounded implementation;
- focused compatibility selection: **147 passed in 13.48 seconds**:
  `uv run pytest tests/test_service_post_search.py
  tests/test_service_post_search_ranking.py tests/test_service_post_search_mcp.py
  tests/test_service_contracts.py tests/test_service_app.py
  tests/test_service_http.py tests/test_service_retrieval.py
  tests/test_service_question_evidence.py tests/test_service_question_contracts.py
  tests/test_skill_service_first_contract.py tests/test_service_supervisor.py
  tests/test_service_intelligence_contracts.py tests/test_service_product.py
  tests/test_source_log_visibility.py --override-ini addopts='' -q`;
- opt-in measurement command above: **1 passed in 2.36 seconds**. Ordinary
  test runs skip this synthetic performance test unless explicitly enabled;
- `go test ./... -skip TestGeneratedPostSearchCatalogIsCurrent` and
  `go vet ./...` passed under `mcp/`. Full `go test ./...` confirmed only the
  expected generated-search-catalog failure. The stale digest is
  `ac42d96af99bef3518af89f9a56522ee178ac71afb975df4f35bf368df23d26e`;
  required digest is
  `d0d5bb58fdb31bcb5b52c8e31129e7f5a857528886827215b5b50b2fcafc827e`;
- focused Ruff F checks on backend/ranker and new Python fixtures/tests passed;
  formatting used a locally cached formatter. `git diff --check` and the
  plan-authority audit passed with zero findings;
- one implementation attempt and one self-review pass used; no children or
  independent review were represented as run. The coordinator owns the
  remaining broad review and generated-artifact join.

Residual limits and stop:

- local hash vectors establish deterministic channel/contract behavior, not
  broad semantic quality. WI-008 remains the quality-evaluation consumer;
- semantic admission is bounded to 20,000 stored vector rows per family and
  bounded vector payloads. Corpus row/retention limits remain 10,000 candidate
  revisions and 32 MiB serialized snapshots; no general process-memory promise
  follows beyond the recorded short-text fixture;
- cursors remain process-local and expire on TTL/eviction/restart. Packet 4
  isolated-runtime closeout, broader quality work, and release/version changes
  are not performed;
- stop at source publication. Coordinator regenerates catalogs and runtime
  manifest once after joining lanes, reviews and validates the exact result,
  and owns any PR/integration. Do not begin Packet 4 or open a PR here.

Graphiti write status: `not_written`; current repository evidence is the
durable authority and the assignment excludes memory/provider effects.
