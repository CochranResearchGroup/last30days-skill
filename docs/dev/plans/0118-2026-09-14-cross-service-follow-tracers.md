# Plan 0118 | Cross-Service Follow Tracers Packet 2

State: OPEN
Lane: P39
Work item: WI-005
Branch: feat/cross-service-follow-tracers-v1
Target: main
Integration: merge
Roadmap: P39
Plan version: 1
Date: 2026-09-14
Execution owner: /root/wave4_wi005_plan
Coordination owner: /root
Requested model route: gpt-6-astra, high reasoning
Effective runtime model: unknown until reported

## Objective

Implement provider-free native Reddit community/user and YouTube channel follow
tracers through the real collection, acquisition, publication, provenance, and
authorized search paths while preserving exact X and legacy compatibility.

## Current State

Plan 0115 closed the capability registry, exact X identity, identity-bound
compatibility evidence, and scheduler-isolated legacy quarantine. Reddit and
YouTube now have fixture-backed native route implementations and truthful
dependency/transport readiness. The source tracer is implemented; shared public
discovery/parity, generated artifacts, joined validation and integration remain
coordinator-owned. Native execution remains unavailable without explicit
injected transport/readiness; no installed or live acquisition is claimed.

## Scope

- add canonical Reddit community/user and YouTube channel-ID target contracts;
- extend capabilities with operation, identity, route, cadence, support, and
  dependency-readiness metadata;
- implement small fixture-backed native route/response validators with injected
  transports and no generic-search fallback;
- traverse disabled spec, lifecycle, coordinator, frozen worker request,
  provider route, publication, sighting provenance, and authorized cache query;
- preserve distinct native identity alongside stable follow target identity;
- retain exact X bytes/history and quarantine malformed historical rows.

## Non-Goals

No live locator resolution, provider/network call, handle/custom-URL lookup,
public-partition policy change, browser, installed runtime, real schedule,
release/deployment, issue mutation, fresh-runtime closeout, or other service
target contracts.

## Acceptance Criteria

1. Reddit community/user and YouTube channel selectors canonicalize strictly;
   unsupported/unresolved forms and route mismatches fail closed.
2. Success, zero yield, malformed/unavailable target, dependency absence,
   timeout/rate limit, pagination bounds, authorization, and replay are
   deterministic through injected production route code.
3. Lifecycle/revision/coalescing semantics and old-revision completion remain
   exact; readiness changes never activate a target.
4. X identities/history and general collections remain unchanged; malformed
   legacy rows remain readable/quarantined and cannot starve healthy due work.
5. Publication preserves all follow/general sightings without duplicating one
   source-native content version; exact follow filtering and negative partition
   cases pass.
6. Capability discovery and lifecycle/query results agree across existing
   service boundaries; a frozen 10,000-sighting baseline is retained.
7. Focused/full Python, Go test/vet, generated-contract/package checks, audits,
   and diff checks pass at the joined head.

## Ownership And Topology

One top-level implementation owner, no children, at most two implementation
attempts, one independent review, and one closed-world remediation. Lane writes
are follow capabilities/collection/acquisition, two small provider tracer
modules, focused fixtures/tests, and this plan. Shared contracts, job runner,
app/HTTP/client/CLI/MCP, catalogs, manifests, product docs, and authority are
coordinator-owned and serialized after Plan 0117's shared join.

## Stop Rules

Stop on changed X identity, history rewrites, generic-search fallback,
readiness masquerading as support, unbounded work, public access-policy change,
unregistered shared edits, or any required provider/browser/live locator/
installed runtime/schedule effect.

## Definition Of Done

All seven criteria pass and Packet 2 is integrated. WI-005 remains `READY` for
one separately bounded fresh-runtime closeout; this packet alone is not DONE.

## Current Checkpoint

### Checkpoint P0118-C01 | 2026-09-14

Plan version: 1

State transition: `unplanned -> PLANNED`; registration only.

Progress classification: `blocker_reduction`; provider-native fixture tracer
work is bounded without claiming adapter availability or runtime acceptance.

Authority classification:

- `inherited_authority`: Plan 0107 covers provider-free plan, activation,
  implementation, review, integration, and repo-local closeout;
- `human_gate`: provider/network/browser/live-locator, installed-runtime,
  schedule, staging, production, release, deployment, and issue effects.

Subagent status and reconciliation:

- `joined`; one read-only planning specialist returned this scope. No
  implementation owner exists until activation.

Next action: integrate registration, publish exact lane custody, reconcile it,
then assign one owner while reserving shared joins for the coordinator.

### Checkpoint P0118-C02 | 2026-09-14

Plan version: 1

State transition: `PLANNED -> OPEN`.

Progress classification: `blocker_reduction`; exact isolated custody is
accepted from canonical registration merge `d6cf8252` at
`/home/ecochran76/workspace.local/last30days-skill-wi005-v2` on
`feat/cross-service-follow-tracers-v1`.

Authority classification:

- `inherited_authority`: provider-free implementation, validation, branch
  publication, review, and integration under Plan 0107;
- every external-effect boundary in C01 remains held.

Subagent status and reconciliation:

- `assigned`; `/root/wave4_wi005_plan`, one owner with no children. Shared
  service/public transport, generated artifacts, docs, and authority remain
  coordinator-owned.

Next action: publish this activation checkpoint, reconcile canonical custody,
then implement both fixture tracers test-first within the lane write set.

### Checkpoint P0118-C03 | 2026-09-14

Plan version: 1

State: `OPEN`; lane-owned source tracer accepted, coordinator joins pending.

Custody and authority:

- implementation fast-forwarded activation `f7ba978d` to canonical
  `ed84cd29`; coordinator-owned native request contract `9ad0dcd0` was
  cherry-picked exactly as `53465c84`, without editing shared files;
- one owner, no children; first implementation attempt. TDD/codebase-design
  skills supplied incremental public-seam tests and injected transport design;
- no provider/network/browser/live locator, installed runtime/database,
  real schedule, release, deployment, or issue mutation occurred;
- requested route remains `gpt-6-astra`, high; effective configuration unknown.

Accepted source evidence:

- canonical Reddit community/user names and YouTube channel IDs retain distinct
  native identity; X target hashes and revision bytes remain unchanged;
- exact Reddit new/submitted and YouTube uploads-playlist routes validate
  frozen selectors, identity digests, partition, provider payload identity,
  dates, byte/item/page/request/time bounds, and measured transport usage;
- injection is `execute_work(..., follow_transports={route: transport})`.
  Transport returns `{status, network_request_count, payload}` and accepts
  exact URL plus deadline, maximum bytes, remaining request bound, and YouTube
  item limit. Missing injection returns `adapter_unavailable`; no default
  network, browser, generic-search fallback, or opaque yt-dlp call is made;
- native collection resume and issuance require explicit
  `CollectionCoordinator(..., follow_execution_ready=predicate)`. The default
  rejects with `transport_not_configured`; tests inject this only into
  disposable stores. Dependency readiness never enables execution;
- Reddit community/user/general overlap publishes one content version with
  three sightings; YouTube channel/general overlap publishes one version with
  two sightings. Replay, frozen old revisions, exact spec filters and negative
  access-partition queries pass through the real production classes;
- malformed historical native targets stay readable and can pause/archive,
  but validation happens before bounded due selection so healthy work is not
  starved. Compatibility tracing does not map incomplete/malformed native rows.

Validation:

- RED then GREEN for native creation, user/channel lifecycle, route execution,
  legacy quarantine, error classification, metadata validation, malformed
  compatibility, and absent-transport resume/issuance;
- real YouTube publication/search exposed a missing timezone; native upload
  dates now emit canonical UTC timestamps and the exact regression passes;
- focused command: `uv run --offline pytest -o addopts='' tests/test_service_follow_tracers.py tests/test_service_follow_capabilities.py tests/test_service_collection.py tests/test_service_acquisition_worker.py tests/test_service_product.py tests/test_service_contracts.py -q`;
- focused result: **153 passed in 16.38 seconds**. The existing canonical
  dependency environment was selected with `UV_PROJECT_ENVIRONMENT`; no
  dependencies were downloaded;
- Ruff passes for the capability/provider modules and focused tests; changed
  Python compiles and `git diff --check` passes;
- fixed `wi005-packet2-10000-v1` fixture retains 10,000 sightings over one
  content version: exact filter 0.019846 seconds and 10,000-row compatibility
  trace 0.064521 seconds. These are a baseline, not performance thresholds;
  unauthorized query returned zero and reorder replay retained the digest;
- baseline input SHA-256:
  `8305dbbbcef7260d190982075a90ad98b4d8899391d657178d3e669d36501271`;
  compatibility digest:
  `sha256:a8ea39e9eb113c13d2f94e9e44839e040934216bf81eaf3f6c54b580ed1ecc16`.

Exact coordinator joins:

- `DEFAULT_FOLLOW_CAPABILITIES.catalog(config, which=...)` returns
  `{schema_version: 1, registry_digest, targets}`. Rows separate declared
  `state`/`reason_code`, `dependency_readiness`, and `execution_readiness`;
  native transport readiness remains `unavailable:transport_not_configured`;
- publish that same catalog through the chosen service-info/collection,
  CLI/HTTP/MCP projections. Preserve native safe errors rather than flattening
  unavailable, unresolved, unsupported, malformed and unauthorized outcomes;
- preserve the shared selector additions already supplied; no additional
  job-runner edit was needed for the source tracer;
- update product docs, regenerate contract catalog/Go constants/runtime
  manifest, run joined full Python/Go/package/public-parity validation, review,
  and integrate. None of these shared files was independently edited here;
- fresh isolated-runtime closure remains a separately bounded WI-005 gate.

### Checkpoint P0118-C04 | 2026-09-14

Plan version: 1

State: `OPEN`; provider-free lane source and evidence handed to coordinator.

Progress classification: `outcome_progress`; native acquisition, lifecycle,
publication, provenance and partitioned query tracers are implemented and
validated at source checkpoint `3b539c7537c225d33845b4ff7c4c624df6b7de19`.

Authority classification:

- `inherited_authority`: lane-owned provider-free implementation, disposable
  test fixtures, tests, plan evidence, and owned-branch publication;
- no provider/browser/live locator, installed runtime/database, real schedule,
  release/deployment, issue, or shared-authority mutation is authorized.

Validation evidence:

- full command `uv run --offline pytest -o addopts='' -q` completed once:
  **3,045 passed, 8 skipped, 14 subtests passed, 12 failed in 251.33 seconds**;
- eleven failures are in `test_service_lifecycle_install.py` (eight) and
  `test_service_runtime_package.py` (three), all gated by the coordinator-owned
  stale `service/runtime-manifest.json`. The manifest was not refreshed here;
- one failure was `test_current_repository_authority_passes`, whose exact
  finding was `latest checkpoint P0118-C03 is missing Authority classification`.
  This checkpoint supplies that required explicit classification. The focused
  authority audit is rerun before publication rather than masking the initial
  full-run failure;
- `go test ./...` and `go vet ./...` pass from `mcp/`;
- the separate active planning-contract audit identifies precisely three
  coordinator-owned missing full-filename RUNBOOK links for Plans 0117, 0118
  and 0119. That shared file remains untouched in this lane;
- source checkpoint was clean and equal to the live owned-fork branch;
  the post-suite OS readback found no surviving process matching this lane or
  its exact `pytest-531` fixture root;
- serialized registry digest is
  `sha256:6a3b4f00c0b61caee91f6eebca3008c37b57a5bba25682cacea29a52b5c82f97`.

Subagent status and reconciliation:

- `joined`: one assigned implementation owner completed the first attempt;
  no children or independent lane reviewer were spawned. The coordinator owns
  shared public parity, generated artifacts, independent joined review,
  integration, and final acceptance.

Next action: join the C03 catalog/error projection contract, repair shared
runbook wiring, refresh generated contracts/runtime manifest, run final joined
acceptance and review, and integrate. Keep WI-005 open for its separately
bounded fresh isolated-runtime closeout.

### Checkpoint P0118-C05 | 2026-09-14

Plan version: 1

State transition: `OPEN -> integration_ready`; plan remains `OPEN` pending the
owned-fork PR merge and canonical reconciliation.

Progress classification: `outcome_progress`; the Reddit and YouTube native
tracers, capability discovery, public projections, generated artifacts and
joined validation are complete.

Authority classification:

- `inherited_authority` covered only provider-free implementation, fixtures,
  validation, review and owned-fork publication;
- no provider/browser/live locator, installed runtime/database, real schedule,
  release/deployment or tracker mutation occurred.

Joined evidence:

- reviewer reproduction found that Reddit could invoke transport with a zero
  remaining request budget; checkpoint `c8bf22b0` now stops before invocation
  and the independent replay observed exactly one call with budget `[2]`;
- focused follow tests, the full 3,086-test Python suite, all Go tests, vet,
  packaging checks and independent joined review pass;
- public HTTP, Python and MCP capability discovery preserve separate declared,
  dependency and execution readiness states.

Next action: integrate the reviewed head. WI-005 remains `READY`, not `DONE`,
because its separately authorized fresh-runtime closeout is outside this packet.
