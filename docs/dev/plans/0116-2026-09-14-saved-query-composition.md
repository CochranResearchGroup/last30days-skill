# Plan 0116 | Saved Query Composition Packet 2

State: OPEN
Lane: P40
Work item: WI-006
Branch: feat/saved-query-composition-v2
Target: main
Integration: merge
Roadmap: P40
Plan version: 1
Date: 2026-09-14
Execution owner: /root/wi002_search_packet2
Coordination owner: /root
Requested model route: gpt-6-astra, high reasoning
Effective runtime model: unknown until reported

## Objective

Compose the existing monitor kernel with the real stored-post search contract by
persisting an immutable saved-query version and freezing its exact bounded
evidence view into explicit baseline acceptance.

## Current State

Packet 1's provider-free monitor kernel is integrated. WI-002's search contract
and WI-004's follow contract are available. Packet 2 now supplies immutable
saved-query definitions, a durable cursor-free capture repository, and a real
search view provider alongside the fake provider. Source validation and shared
CLI/MCP/runtime joins are tracked in C02; follow composition and digest/delivery
closure remain separate.

## Scope

- persist immutable saved-query definitions and versions;
- execute the exact query through `PostSearchBackend` in one snapshot lifetime;
- freeze evidence IDs, revisions, partitions, component head, cutoff, and
  coverage rather than persisting a process-local cursor;
- classify new, revised, and unchanged evidence; treat top-k absence as unknown,
  not removal;
- require explicit baseline acceptance and fail closed on stale baseline,
  partial/truncated traversal, cursor expiry/restart, or partition mismatch;
- add narrow local CLI/MCP parity behind coordinator-owned shared joins.

## Non-Goals

No follow view, digest generation, notification delivery, installed schedule,
refresh/acquisition, provider, browser, production, release, issue mutation, or
generated summary.

## Acceptance Criteria

1. Saved-query identity and every version are immutable and schema validated.
2. Search execution freezes exact evidence and coverage without durable cursors.
3. New/revised/unchanged classifications are deterministic and idempotent.
4. Absence, incomplete traversal, stale heads, restart, and partition drift
   never fabricate removals or silently restart from an unpinned view.
5. Baseline movement requires explicit acceptance; replay is side-effect safe.
6. Narrow CLI/MCP fixtures preserve the same contracts with effects disabled.
7. Focused monitor/search, full Python, Go test/vet, audit, and diff checks pass.

## Ownership And Topology

One top-level implementation owner, no children, at most two implementation
attempts, one independent review, and one closed-world remediation. Lane writes
are monitor contracts/kernel, new `service_monitor_views.py`, focused tests and
fixtures, and this plan. Shared app/CLI/MCP contracts, catalogs, manifests, and
authority projections remain coordinator-owned.

## Stop Rules

Stop on missing authoritative head/coverage evidence, unbounded cursor replay,
shared-file custody conflict, upstream search repair, or any provider,
installed-database, schedule, delivery, credential, or live effect.

## Definition Of Done

All seven criteria pass at integration. This closes Packet 2 but not WI-006;
follow composition and digest/delivery/runtime closure remain separately planned.

## Current Checkpoint

### Checkpoint P0116-C01 | 2026-09-14

Plan version: 1

State transition: `PLANNED -> OPEN`; activation only, implementation held.

Progress classification: `blocker_reduction`; the previously unassigned packet
now has an accountable execution owner and an exact publishable custody record.
No product acceptance criterion is claimed complete by this activation.

Custody and topology:

- execution owner: `/root/wi002_search_packet2`, reporting to coordinator
  `/root`, under Plan 0107's temporary parent/worker campaign topology;
- exact worktree:
  `/home/ecochran76/workspace.local/last30days-skill-wi006-v2`;
- branch: `feat/saved-query-composition-v2`, target `main`, integration by merge;
- activation base and pre-edit local HEAD:
  `bf12c730eaa592cf627311aeef36d06810a2e83c`;
- pre-edit worktree was clean. Canonical
  `/home/ecochran76/workspace.local/last30days-skill` remained clean on `main`
  at the same exact SHA, equal to the live `origin/main` readback;
- before publication the lane tracked `origin/main` and no live
  `refs/heads/feat/saved-query-composition-v2` existed. Activation publication
  must establish that lane remote and tracking ref, then verify exact local,
  upstream, and live remote equality;
- requested route: `gpt-6-astra`, high reasoning, as registered in this plan;
  effective model and effort: unknown because the runtime has not reported
  them. The existing agent is reused; its name is not model evidence;
- one lane owner, no children. Subagent status: activation performed by this
  existing campaign worker; no nested agent was spawned. Implementation bounds
  remain two attempts, one independent review, one closed-world remediation;
  this activation consumes no implementation attempt.

Authority classification:

- `inherited_authority` for this turn is limited by the coordinator's explicit
  assignment to editing this plan, validating it, committing, publishing this
  branch, and read-only custody verification;
- implementation is held until coordinator continuation after activation
  integration and shared-lane reconciliation. All seven acceptance criteria
  remain unverified for Packet 2; no product source or test was edited or run;
- planned lane writes, not exercised here, are
  `service_monitor_contracts.py`, `service_monitors.py`, new
  `service_monitor_views.py`, focused tests/fixtures, and this plan;
- shared app/CLI/MCP contracts, generated catalogs/runtime manifests,
  `ROADMAP.md`, `RUNBOOK.md`, `docs/dev/active-lanes.yaml`, and work-item
  projections remain coordinator-owned. The current P40 catalog still points
  to closed Packet 1; this checkpoint does not claim globally reconciled
  Packet 2 custody;
- follow composition, digest/delivery, upstream search repair, WI-003 work,
  provider/browser/live data, installed runtime/database, schedule, credentials,
  PR/issue mutation, release/deployment and other effects are outside this turn.
  Live-effect expansion remains a `human_gate`;
- WI-006 final acceptance still waits for WI-002 closeout. WI-004 is closed,
  but its follow composition remains deliberately reserved for Packet 3.

Discovery and validation:

- re-read `AGENTS.md`, policies 0001, 0005-0010, 0012-0013, 0015, 0019,
  0021, 0023, 0025-0029 and 0032, this plan, WI-006, and Plan 0107's current
  Wave 3 registration checkpoint;
- Graphiti discovery: `skip`; current supplied assignment and repo authorities
  suffice for this plan-only activation. CodeGraph/source impact inspection is
  deferred to implementation; no index, runtime or product source was changed;
- Graphiti checkpoint projection is deferred to the coordinator because this
  assignment permits only the plan write and Git publication, with provider
  effects held. No memory or shared RUNBOOK write was attempted;
- `python3 dev/last30days/scripts/audit_plan_authority.py --root .` passed on
  the base and activation diff. `git diff --check` passed; scoped diff
  validation confirms that only this plan changed;
- the generic active planning audit failed already on the exact base with
  four coordinator-owned registration findings: Plan 0114 is not wired in
  ROADMAP or RUNBOOK; Plans 0115 and 0116 are not wired in RUNBOOK. Preserve
  those findings unchanged after the edit; no shared authority was repaired
  from this lane and the generic audit is not claimed passing;
- product Python/Go suites and runtime validation are intentionally not run
  for the activation-only change. Their evidence remains required during
  implementation and coordinator integration.

Next action or stop reason: validate and publish this plan-only activation,
return its exact SHA, clean status and local/upstream/live remote equality,
then stop. Do not start implementation from the plan's OPEN label. On a later
coordinator continuation, re-anchor the integrated base and shared ownership
before the first source edit; retain all plan stop rules.

### Checkpoint P0116-C02 | 2026-09-14

Plan version: 1

State transition: `activation_held -> source_checkpoint`; plan remains `OPEN`
pending coordinator integration and public transport acceptance.

Progress classification: `outcome_progress`; the real saved-query composition
advances acceptance criteria 1-5, with a tested local JSON seam for criterion 6.
No WI-006 completion or public CLI/MCP parity is claimed from local fixtures.

Authority classification:

- `inherited_authority`: coordinator continuation explicitly authorized this
  bounded implementation covering monitor-owned source/tests, local synthetic
  stores, validation, plan update and branch publication only;
- fetched origin and fast-forwarded the existing lane to exact
  `c4251dc12c905e513c9f37119b3442382741f31e`, preserving activation ancestry
  `d764f2579e1e088d8ce4678e14fa5c489c742480`; clean HEAD equaled origin/main
  before source editing;
- owner/worktree/branch remain those in C01. Requested model is
  `gpt-6-astra`, high reasoning; effective model/effort remain runtime-unknown;
- one implementation attempt with incremental TDD, one self-review and bounded
  remediation; no children, provider/browser/live/installed/runtime/schedule,
  delivery, PR or issue effects;
- all shared routes, schemas/catalogs, runtime manifest, roadmap/runbook,
  active-lane and work-item changes remain coordinator-owned.

Implemented source contract:

- `SavedQueryDefinitionV1` strictly validates current-revision queries, stores
  canonical immutable query bytes, excludes transport request IDs/cursors, and
  exposes detached JSON projections. Query versions increase exactly by one;
  query partition and profile identity cannot change across versions;
- `SavedQueryRepository` adds monitor-local immutable query/capture tables to
  the monitor store, without changing the shared corpus schema. Capture IDs
  bind exact query version, partition and resource limits. Pending/failed IDs
  never silently restart; completed captures replay after backend/repository
  reopening without reading the corpus again;
- `SavedQueryViewProvider` consumes real `PostSearchBackend` pages inside one
  retained snapshot lifetime, pins query/head/component/coverage identity, and
  freezes stable post IDs, exact version IDs, complete evidence references,
  source coverage and the first page's UTC knowledge cutoff. Cursors are only
  transient process variables, never durable capture/query/baseline state;
- malformed/nonprogressing traversal, query/head/partition drift, expiry and
  restart fail closed. Truncation or unavailable/degraded semantic coverage is
  partial; complete means this bounded cache view, not provider acquisition
  coverage. No search absence becomes a removal;
- the monitor kernel accepts either real or fake view readers. Acceptance now
  rejects partial first baselines and older-cutoff comparisons, closing two
  defects demonstrated by RED tests. New/revised/unchanged evidence and prior
  accepted-baseline compare-and-set remain deterministic;
- default capture bounds are 1,000 evidence items, 100 pages, 2 MiB serialized
  evidence and 10 seconds; hard configurable ceilings are 10,000 items, 1,000
  pages, 32 MiB evidence and 60 seconds. Source pages are capped at 128 KiB.
  Deadline checks are cooperative between synchronous calls, not cancellation
  of an in-flight backend/SQLite call. Receipts add bounded page metadata to
  the evidence-byte budget;
- per coordinator decision, `revision_mode=all` is rejected with typed
  `MonitorContractError`; the comparator has one current version per stable
  post. Future all-revision semantics require a separately bounded evolution.

Discovery, review and validation evidence:

- re-read current AGENTS, applicable planning/validation/testing/custody/model
  policies and this plan. TDD, CodeGraph and deep-module design skills guided
  the small save/capture/read interface and real-backend behavior tests;
- canonical CodeGraph supplied current search, monitor-contract and transport
  context/impact; source bodies omitted by capped output were read directly.
  Search response/request callers include question adapters and MCP tests;
  no upstream search, question, or shared transport implementation was edited;
- RED evidence: missing query module/provider/command seam, partial initial
  acceptance, older-cutoff acceptance and unreported semantic incompleteness.
  Each passed after its corresponding implementation; fixture import/SQL
  setup errors were corrected without changing product acceptance;
- focused tier: `uv run pytest tests/test_service_monitor_views.py
  tests/test_service_monitors.py tests/test_service_post_search.py
  tests/test_service_post_search_ranking.py tests/test_service_post_search_mcp.py
  -o addopts='' -q` passed, 79 tests in 10.73 seconds;
- `go test ./...` and `go vet ./...` passed in `mcp/`;
- repo-native plan authority audit, generic active planning audit and
  `git diff --check` passed. C01's registration-wiring findings are resolved
  by the coordinator's integrated base, not by edits from this lane;
- full safe Python suite: `uv run pytest -o addopts='' -q` ran once and
  completed in 158.48 seconds: 3,007 passed, 8 skipped, 14 subtests passed,
  11 failed. Eight failures are in `test_service_lifecycle_install.py` and
  three in `test_service_runtime_package.py`; they are the unchanged generated
  runtime-manifest gate, whose build failure states
  `service/runtime-manifest.json is stale; run service/scripts/build-runtime.sh --refresh-manifest`.
  This is not a full-suite pass. The coordinator must regenerate/review the
  integrated manifest and repeat the package/lifecycle/full acceptance checks;
- self-review/remediation checked immutable replay, no persisted cursors,
  access isolation, malformed/pending traversal, semantic denominator validity,
  bounded evidence accounting and numeric fractional timestamp ordering.
  Independent joined review is still coordinator-owned;
- Graphiti projection remains deferred to coordinator closeout; no provider
  effect or shared RUNBOOK write was performed by this source lane.

Exact coordinator-owned joins required for criterion 6:

- proposed CLI command family: `service.py saved-query` with actions `save`,
  `get`, `capture`, `receipt`; proposed MCP tool: `saved_query` with the same
  closed action payloads. These names are join proposals, not existing public
  routes. Add routing in `service.py`, application/client/HTTP as appropriate,
  and `mcp/internal/tools/service_tools.go` plus Go/Python boundary fixtures;
- both transports should call
  `service_monitor_views.saved_query_command(provider, payload,
  access_partition_id=trusted_partition)`; never accept the authorized partition
  as an untrusted outer command field. `save` takes `definition` and returns
  `SavedQueryDefinitionV1.to_dict()`; `get` takes `view_ref` and returns that
  same typed definition; `capture` takes `view_ref`/`capture_id` and returns
  `SavedQueryViewSnapshotV1.to_dict()`; `receipt` takes those same keys and
  returns the hash-verified frozen receipt;
- initialize `SavedQueryRepository` only against the explicitly owned monitor
  store, construct `SavedQueryViewProvider` with the existing cache-only search
  backend, and inject it into `MonitorKernel`. Do not wire acquisition,
  scheduling or delivery as a side effect;
- monitor evaluation uses `MonitorKernel.evaluate(monitor_id, snapshot_id)`
  returning `MonitorRunV1`; explicit accept/reject use existing kernel methods
  returning `MonitorDecisionV1`. Transport routing must preserve trusted actor
  and partition checks; saving/capturing must not activate or accept a monitor;
- register schemas/discovery and refresh the shared runtime manifest to include
  `service_monitor_views.py`; prove actual local CLI/MCP parity in the integrated
  isolated fixture join. The current test proves JSON command equivalence only.

Next action or stop reason: publish the coherent source plus this plan after
the completed single full-suite run, verify clean local/upstream/
live remote equality, and stop for coordinator shared joins and independent
integration review. No follow, digest, delivery or upstream search expansion.
