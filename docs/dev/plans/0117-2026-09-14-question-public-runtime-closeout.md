# Plan 0117 | Question Public Runtime Closeout Packet 4

State: OPEN
Lane: P36
Work item: WI-003
Branch: feat/question-public-runtime-closeout-v1
Target: main
Integration: merge
Roadmap: P36
Plan version: 1
Date: 2026-09-14
Execution owner: /root/wave4_wi003_plan
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

### Checkpoint P0117-C02 | 2026-09-14

Plan version: 1

State transition: `PLANNED -> OPEN`.

Progress classification: `blocker_reduction`; exact isolated custody is
accepted from canonical registration merge `d6cf8252` at
`/home/ecochran76/workspace.local/last30days-skill-wi003-v4` on
`feat/question-public-runtime-closeout-v1`.

Authority classification:

- `inherited_authority`: provider-free implementation, validation, branch
  publication, review, and integration under Plan 0107;
- every external-effect boundary in C01 remains held.

Subagent status and reconciliation:

- `assigned`; `/root/wave4_wi003_plan`, one owner with no children. Shared
  transports, catalogs, versions, manifests, docs, and authority remain
  coordinator-owned.

Next action: publish this activation checkpoint, reconcile canonical custody,
then implement the acceptance criteria test-first within the lane write set.

### Checkpoint P0117-C03 | 2026-09-14

Plan version: 1

State transition: `OPEN -> OPEN`; lane-owned application checkpoint ready for
the coordinator's public transport join, with further bounded acceptance tests
and the repo-only dogfood probe still in progress.

Authority classification: `inherited_authority` for source, synthetic SQLite
fixtures, injected no-provider workers, tests and feature-branch publication.
No shared app/transport/catalog/version/manifest/docs/authority file changed.

Custody: activation `cfe4e719` was fast-forwarded to the freshly fetched
canonical activation `ed84cd29d1cd46aba7dd1999c3a9f9d2a462a7fe` before edits.
The worktree-local graph is absent; it was not initialized. Current source
reads use the exact seams established during the canonical read-only audit.

Acceptance progress:

- the first real-backend tracer failed because five accepted WI-002 filter
  fields were rejected; all eight now use the existing public search parser;
- the temporal tracer failed for all four ignored fields; submission now
  rejects non-null temporal intent with `unsupported_temporal_intent`, while
  the accepted published/observed filters express supported time constraints;
- scoped round-trip and unavailable-model tracers failed on the absent
  application and pending default respectively, then passed with exact profile
  and frozen access-digest checks, immutable evidence reads, targeted queue
  claims, terminal model-unavailable and explicit evidence-only fallback;
- the injected-worker tracer failed on the missing lifecycle, then passed
  bounded pending waits, read-only status polls and truthful failed/successful
  shutdown joins. No real model or provider process runs;
- focused question validation passes 50 tests. One initial test import used
  an incorrect tests-package path, then the seed was corrected to WI-002's
  current topic/sighting fixture; both setup failures are retained here and
  are not represented as product regressions.

Interface for the coordinator:

- `QuestionApplication(db_path, search_backend, *, access_partitions,
  worker=None)` accepts the host's profile-to-partition callback;
- `ask_question(QuestionRequestV1, *, wait_cancelled=None)` and
  `question_status(question_id, *, profile_id)` return `QuestionStatusV1`;
- `read_evidence(EvidenceReadRequestV1)` returns `EvidenceReadResponseV1`;
- `start()` owns at most one injected worker thread; `stop(timeout=5)` returns
  false if that exact thread remains alive. The default unavailable worker
  starts no thread. Status/evidence never execute work;
- `QuestionUnavailableError` has the same message for absent/unauthorized
  identities; map it to a non-leaking 404. `QuestionRuntimeUnavailableError`
  is a safe 503; `QuestionResponseTooLargeError` is a safe size error;
  `QuestionContractError` and `QuestionRequestConflict` retain their existing
  invalid-request/conflict roles;
- serialize typed results with `to_dict()`. Public payloads are checked
  against 131,072 bytes. Client request timeouts must exceed the 30-second
  maximum wait budget without changing the request fingerprint.

Attempt accounting: first implementation attempt remains active; no independent
review, closed-world remediation, or runtime acceptance attempt was consumed.
No children. Effective model and effort remain unknown because they were not
reported by the runtime. TDD and its required codebase-design vocabulary
guided one behavioral tracer at a time behind the application interface.

Next action: publish this coherent application checkpoint for coordinator
transport implementation, then finish bounded lane-owned adversarial/probe
coverage without editing any shared join surface.

### Checkpoint P0117-C04 | 2026-09-14

Plan version: 1

State transition: `application_checkpoint -> lane_source_accepted_pending_join`;
plan remains `OPEN` because public transport, generated artifacts, exact-runtime
acceptance, independent review and canonical integration are coordinator joins.

Progress classification: `outcome_progress`; the provider-free host interface,
adversarial public-application tests and reusable runtime probe are complete.

Authority classification:

- `inherited_authority` covers the assigned question source/tests, repo-only
  probe, plan and feature publication under Plan 0107;
- all shared app/HTTP/client/CLI/MCP, schema/catalog, version/manifest, product
  docs and portfolio authority files remain coordinator-owned and unchanged;
- no provider, model, browser, installed service/database, live data, schedule,
  delivery, release, deployment or issue mutation occurred. No isolated service
  process was started by this lane; injected workers ran only in test threads.

Source evidence and regression mapping:

- first coherent source checkpoint `a9cfa8b12e64745dc768b086484bccce6d442bed`
  was published clean and live-remote-equal for the coordinator's transport join;
- public request identifiers now use a host-derived profile namespace. The
  reproducer first leaked the other profile's request-id collision, then passed
  independent profile admission, same-profile conflict and revoked-scope denial;
- an otherwise valid Unicode worker answer first exceeded the 128 KiB public
  envelope. It now persists a compact, non-retryable `answer_too_large` result
  with a 4 KiB status-envelope reserve; the immutable result remains readable;
- evidence-only overflow first returned an answer error without the matching
  task error. Host completion now persists the same terminal failure receipt;
- one-character direct answers remain durable; no-evidence results retain
  `no_evidence`. Unsupported temporal meanings remain explicit errors and all
  eight accepted search filters are preserved;
- wait cancellation ends only the bounded caller wait. It does not rewrite
  the durable request, grant retries or pretend to terminate worker execution;
- the new question probe verifies flat strict discovery, six question cases,
  exact HTTP/MCP answer/status/evidence parity, profile denial, temporal denial,
  expected question-ledger-only writes, immutable reads after restart and exact
  runtime/MCP ownership teardown. Its two-cycle runtime path is prepared but
  unrun until the coordinator's joined artifact exists;
- probe integrity tests reject a forged answer digest and distinguish expected
  question-ledger writes from corpus mutation. Its real HTTP/fresh-MCP test is
  explicitly skipped while the coordinator-owned client method is absent and
  will execute automatically against the joined source.

Validation:

- `uv run pytest tests/test_service_question_application.py
  tests/test_question_dogfood.py tests/test_service_question_contracts.py
  tests/test_service_question_evidence.py tests/test_service_questions.py
  tests/test_service_question_worker.py tests/test_service_post_search.py
  tests/test_service_post_search_ranking.py tests/test_service_monitor_views.py
  --override-ini addopts='' -q`: 128 passed, one coordinator-transport skip in
  24.81 seconds;
- the 15 application cases and existing Packet 1-3/corrective tests exercise
  current real search/storage plus deterministic injected workers;
- offline Ruff 0.16.7 checks the four new application/probe/test files; direct
  Python compilation and `git diff --check` pass;
- the first plan audit found C03's inline authority wording did not match the
  auditor's latest-checkpoint header contract. This append supplies the exact
  required header without rewriting historical evidence;
- full Python, Go, catalog generation, package/lifecycle, reproducible builds
  and runtime acceptance remain joined-head gates. The source manifest is
  intentionally untouched and cannot yet package the new application module.

Coordinator joins and exact next action:

1. Merge this lane's published tip without rewriting its accepted ancestry.
   Public method/exception types remain those recorded at C03; internal request
   ID namespacing and durable size rejection do not change the transport shape.
2. Join the shared transports, public contract catalog, compatible adapter
   identity, source manifest, Skill/configuration guidance and CLI. Current
   Python join `6f445309` was reported by the coordinator and was not modified
   or claimed validated by this lane.
3. Run `tests/test_question_dogfood.py` after the complete HTTP/MCP join; its
   guarded test must pass rather than skip. Build and publish one exact clean
   source artifact, then run `dev/last30days/scripts/question_dogfood.py` with
   that artifact, exact worktree, and fresh isolated state/runtime roots. The
   probe rejects existing lane state and writes its raw receipt under the
   isolated controller's receipts directory. Retain that receipt in the
   repo-approved receipts path with digest and exact source/artifact identity.
4. Complete the full joined validation and independent review, preserve failed
   receipts, verify teardown with a fresh OS census, integrate through the
   owned-fork PR workflow and reconcile WI-003 only then.

WI-003 is acceptance-eligible after those joins and evidence pass. It is not
`DONE` from this source checkpoint alone. Effective model/effort remain unknown.
No children; one implementation attempt used; independent review and its one
closed-world remediation remain coordinator-owned and unconsumed here.
