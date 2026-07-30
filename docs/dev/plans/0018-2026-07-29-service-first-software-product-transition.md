# Plan 0018 | Service-first software product transition

State: OPEN
Roadmap: P07
Date: 2026-07-29
Predecessors: Plans 0007, 0010, and 0011
Consumes acceptance packets: Plans 0014, 0015, and 0016

## Product Decision

`last30days` is becoming an independently installed intelligence software
product. Its durable service, corpus, schedulers, source adapters, App
Intelligence supervisor, and MCP server are the product. Agent Skills are
optional client packages that teach agents how to discover, query, monitor, and
administer that product.

The current installable Skill and request-scoped Engine remain compatibility
and operator/debug surfaces during migration. They are not the future control
plane, state authority, or primary runtime.

## Objective

Move the implemented intelligence-service substrate out of the conceptual and
distribution shadow of `skills/last30days/` and establish it as first-class
software with:

- an independently installable and upgradeable user-scoped daemon;
- a stable MCP product contract for ordinary agents;
- deterministic acquisition, scheduling, state, budgets, retries, leases,
  validation, publication, and replay;
- bounded App Intelligence workers for assessment, identity resolution,
  retrieval evaluation, and adapter maintenance;
- optional Skills that consume MCP rather than teaching ordinary agents how to
  operate scrapers.

## Current State

- The daemon, scheduler, corpus, App Intelligence supervisor, and Python
  service client are implemented under `skills/last30days/scripts/`.
- `npx skills add` freezes that tree under
  `~/.agents/skills/last30days`, and the current systemd unit executes
  `service.py` from that frozen Skill copy.
- `skills/last30days/scripts/install-service.sh` writes and immediately
  restarts the user unit, but it has no release directory, loaded-version
  receipt, upgrade transaction, or rollback target.
- The MCP adapter is a separate Go binary, but
  `mcp/scripts/sync-service-runtime.sh` copies the complete installable Skill
  into the MCP bundle and `BootstrapPackagedService` may directly detach its
  packaged `service.py`.
- The Go client already fails closed on the exact
  `X-Last30days-Contract-SHA256` response header. The service also reports
  service version 0.2.7 and database schema 12, but there is no explicit
  client/service API-version compatibility result or loaded-runtime revision.
- Plan 0014 closed at its restart bound after repairing stale due replay and
  per-spec overlap. Revision 9 is disabled, all revision-8 service jobs are
  terminal, and no timer proof is active.

## User Experience Contract

An ordinary querying agent should spend its context on questions such as:

- what has changed, what is trending, and what evidence supports it;
- how fresh and complete the service's coverage is;
- which sources are degraded or awaiting operator action;
- what the service knows about a topic, person, organization, or event at a
  requested time.

It should not spend its context on:

- choosing scraper CLIs or browser backends;
- locating cookies, tabs, displays, profiles, or route identifiers;
- coordinating source retries, pagination, leases, or budgets;
- rebuilding indexes or deciding whether a stochastic proposal may publish.

Those mechanics belong to deterministic software. Stochastic workers may
classify evidence, propose relationships, evaluate retrieval, or diagnose a
repeated failure, but the host validates every proposal and owns every state
transition.

## Target Product Boundary

```text
Agents and applications
  |
  +-- last30 MCP client contract
  |     query, temporal query, dossiers, trends, coverage, jobs,
  |     governed refresh/collection requests, maintenance status
  |
  +-- optional Agent Skills
        query/synthesis skill
        monitoring skill
        operator/admin skill
        bounded maintenance skill
            |
            v
last30 Intelligence Service
  deterministic control plane
    service lifecycle, policy, schedules, jobs, leases, budgets,
    retries, access partitions, validation, publication, replay
  acquisition adapters
    Reddit, X, YouTube, Facebook, LinkedIn, web, and future sources
  intelligence data plane
    immutable evidence, temporal corpus, semantic index,
    authoritative SQLite state, rebuildable GraphRAG projection
  App Intelligence supervisor
    bounded schema-validated workers; no direct authority mutation
```

## Architectural Invariants

1. The service continues running, collecting, indexing, and serving MCP when no
   Skill is loaded and when App Intelligence is disabled.
2. MCP handlers are thin service clients. They never embed acquisition logic or
   launch request-scoped scraper/browser processes.
3. Ordinary query tools are cache-first and never operate browsers.
4. Refresh and collection requests create or join durable host-owned jobs;
   agents do not orchestrate their internal steps.
5. SQLite and immutable artifacts remain authoritative. Semantic and GraphRAG
   indexes are versioned, rebuildable projections.
6. Browser sessions, credentials, cookies, route/display mechanics, raw model
   events, and prompts do not enter ordinary agent responses.
7. App Intelligence outputs are proposals under strict schemas, finite
   reservations, evidence closure, validators, promotion policy, and replay
   receipts.
8. Skills depend on the MCP capability contract, not internal Python module,
   database, browser, or adapter layouts.

## Migration Workstreams

### S01 | Software package and lifecycle boundary

- define the service runtime package outside the installable Skill payload;
- establish versioned install, upgrade, migration, start, stop, readiness,
  diagnostics, and rollback contracts;
- keep one user-scoped daemon and database authority;
- decide repository split only after the logical package boundary is proven.

### S02 | First-class MCP product surface

- version the compact agent-facing capability catalog;
- separate ordinary query tools from governed operator controls;
- add response contracts for freshness, coverage, degradation, uncertainty,
  index/corpus version, access partition, and terminal job state;
- prove that a fresh MCP client needs no Skill-specific scraping knowledge.

### S03 | Deterministic acquisition and timed service

- move source scheduling, adapter selection, authentication-state
  classification, leases, budgets, retries, backoff, cursor/watermark state,
  and publication entirely behind service contracts;
- preserve manual refresh as a durable job request rather than an agent-run
  scraping workflow;
- finish Plan 0014 timer/restart/pause acceptance as one service-control proof.

### S04 | Temporal RAG and GraphRAG data plane

- preserve immutable source evidence and bitemporal query semantics;
- keep local authoritative retrieval usable when semantic or graph providers
  degrade;
- version and replay all derived projections;
- execute Plan 0015 as a service/MCP resilience proof, not as a Skill feature.

### S05 | App Intelligence control plane

- run bounded assessment, identity, retrieval-evaluation, and adapter
  maintenance workers only through the deterministic supervisor;
- normalize all adapters into one ledger and disallow adapter-to-adapter
  control;
- execute Plan 0016 as proof that accepted, rejected, and replayed stochastic
  envelopes cannot bypass host authority.

### S06 | Agent client and Skill redesign

- make the primary `last30days` Skill a concise MCP discovery, query, and
  synthesis client;
- split privileged monitoring, administration, and maintenance guidance into
  explicit optional Skills or capability-gated modes;
- remove scraper selection, browser wrangling, credential mechanics, and
  source retry orchestration from the ordinary agent path;
- keep the direct Engine documented as a portable compatibility/debug path
  until service distribution reaches parity.

### S07 | Compatibility and release transition

- define migration from existing Skill-first installs without losing profiles,
  corpus state, schedules, ledgers, or indexes;
- publish independent service and client compatibility versions;
- add telemetry-free local diagnostics for stale client/service contracts;
- deprecate request-scoped primary operation only after cross-harness MCP
  acceptance and rollback are proven.

## Sequencing

```text
Plan 0014 terminal timer result
  -> architecture packet: S01 package/lifecycle + S02 MCP boundary
       -> Plan 0015 service/RAG resilience
       -> Plan 0016 App Intelligence authority
       -> S06 client Skill redesign
       -> S07 compatibility and release transition
```

Opening this plan required the S01/S02 architecture packet below with exact
file/package ownership, compatibility constraints, install topology, version
handshake, tests, and rollback. The packet does not begin by moving files.

## First Implementation Packet | S01/S02 Service distribution and handshake

Outcome:

- install, upgrade, start, diagnose, and roll back one independently versioned
  service artifact whose loaded version is provable through MCP;
- remove the Agent Skill as the distribution and lifecycle authority without
  moving service implementation modules during this packet.

### Frozen package ownership

New service-product surfaces:

- `service/VERSION` owns the service release version;
- `service/runtime-manifest.json` owns an explicit allowlist and SHA-256
  manifest for the runtime payload;
- `service/scripts/build-runtime.sh` builds a reproducible
  `last30days-service-<version>` artifact from the current canonical
  `scripts/`, `schemas/`, and required metadata only;
- `service/scripts/install.sh` owns install, upgrade, readiness, rollback, and
  release retention;
- `service/systemd/last30days.service.in` owns the managed user-unit template.

Existing implementation authority during this packet:

- `skills/last30days/scripts/service.py`,
  `skills/last30days/scripts/store.py`, the service and acquisition modules
  under `skills/last30days/scripts/lib/`, and
  `skills/last30days/schemas/` remain canonical source;
- `skills/last30days/scripts/install-service.sh` becomes a compatibility
  delegator and no longer renders a unit whose `ExecStart` points into a Skill
  install;
- `mcp/scripts/sync-service-runtime.sh` consumes the independent service
  artifact and must not copy `SKILL.md`, Skill docs, or the complete Skill
  tree;
- `mcp/internal/service/client.go` owns transport and compatibility checks;
- `mcp/internal/contracts/`, `mcp/internal/tools/`, and
  `mcp/cmd/last30days-pp-mcp/` own generated contract facts, safe MCP
  presentation, and the stamped MCP adapter version.

No Python module moves are allowed in this packet. The artifact boundary is
proved before source ownership is relocated.

### Install and lifecycle topology

The Linux user-scoped layout is frozen as:

```text
$XDG_DATA_HOME/last30days/
  research.db                         durable authority, unchanged
  service/
    releases/<service-version>/       immutable verified runtime
    current -> releases/<version>     atomically selected release
    previous -> releases/<version>    one rollback target
$XDG_CONFIG_HOME/last30days/.env      owner-scoped configuration, unchanged
$XDG_CONFIG_HOME/systemd/user/
  last30days.service                  stable managed unit
$XDG_RUNTIME_DIR/last30days/
  service.sock                        owner-private transport, unchanged
```

The unit executes the `current` service release through a stable
`last30days-service` launcher. Upgrade stages and verifies a new immutable
release, records the prior target, atomically switches `current`, restarts once,
and accepts the upgrade only after readiness reports the expected version,
contract digest, and database schema. Failure restores `previous`, restarts,
and proves readiness. Packet one permits no database migration and therefore
freezes schema 12 for rollback safety.

The MCP adapter may carry the same independently built service artifact as an
installation payload, but it must install/start it through the managed service
control path. It may not detach raw `service.py`, copy a Skill tree, or become
the daemon owner.

### Version handshake

`GET /v1/service-info` and the MCP `service_info` result must expose:

- product identity `last30days`;
- semantic `service_version`;
- integer `service_api_version`, initially 1;
- `contract_schema_version` and `contract_sha256`;
- `database_schema_version`;
- immutable `runtime_manifest_sha256`;
- MCP adapter version and its supported service API range;
- compatibility state `compatible` or one safe typed incompatibility reason.

The response header contract digest remains mandatory. The Go client performs
the service-info handshake before any ordinary or operator tool call and fails
closed on product mismatch, unsupported API version, contract digest mismatch,
or database schema outside its declared range. `service_info` remains
available for safe diagnostics and reports both sides of the mismatch without
paths, credentials, prompts, browser state, or raw subprocess output.

### Compatibility and rollback constraints

- existing service v0.2.7/schema-12 state, socket, configuration, profiles,
  schedules, ledgers, corpus, and indexes are preserved in place;
- the first independent release must read the current database without
  migration and return the same ten MCP operations;
- exact contract-digest validation remains fail closed until an explicit
  additive compatibility policy is separately planned;
- the Skill-first installer and current MCPB stay usable as rollback inputs
  until the independent service passes live installation and restart proof;
- removal of packaged runtime bootstrap, source relocation, schema migration,
  timer re-enablement, and Skill redesign are outside this packet.

### Execution slices

1. S01-A: add service version, runtime manifest, reproducible artifact builder,
   and package-boundary tests.
2. S01-B: add versioned installer, stable unit, readiness receipt, atomic
   upgrade/rollback, and fake-user-manager lifecycle tests.
3. S02-A: extend service-info and generated Go contract facts with the explicit
   handshake; add compatible and incompatible client matrices.
4. S02-B: make MCP bootstrap use the managed independent artifact, preserve the
   ten-tool surface, and run process-level service/MCP integration.
5. Migration proof: install over the current schema-12 state, prove the unit no
   longer executes from `.agents/skills`, restart, query through MCP, roll back
   once, and prove corpus/job/timer state unchanged.

### Bounds and hard stops

- maximum implementation attempts per slice: 2;
- maximum review/rework cycles per slice: 1;
- maximum consecutive hardening-only checkpoints: 1;
- active-agent concurrency: 1 unless a later checkpoint explicitly partitions
  non-overlapping files;
- no service implementation module move, database migration, repository split,
  authenticated acquisition, timer enablement, App Intelligence enablement, or
  ordinary Skill redesign;
- stop on artifact contents outside the allowlist, state-path change, more than
  one daemon, contract mismatch presented as healthy, database mutation during
  install/rollback, rollback readiness failure, or loss of any existing MCP
  operation.

### Validation

- artifact reproducibility and manifest verification tests;
- installer rendering, atomic switch, readiness, failed-upgrade, and rollback
  tests with isolated XDG roots and a fake user manager;
- Python service-info and HTTP-header contract tests;
- Go client handshake table tests and generated-contract drift checks;
- `go test ./...`, `go vet ./...`, focused Python service/install/MCP tests,
  and process-level MCP integration;
- live unit `ExecStart`, loaded manifest digest, service-info, database
  integrity, ten-tool catalog, cache-only query, restart, and rollback
  readbacks;
- repo-native planning audit, package-boundary audit, `git diff --check`, clean
  worktree, and local/tracking/remote commit equality.

### Packet acceptance

- a service artifact installs and operates without installing an Agent Skill;
- the live unit resolves through the independent `current` release;
- MCP proves client/service compatibility before serving non-diagnostic tools;
- the Skill tree and MCP adapter contain no independent lifecycle authority;
- one upgrade and rollback preserve schema-12 state and return the same
  evidence-backed cache query;
- unloading or replacing the Skill does not change daemon readiness.

## Non-Goals

- rewriting working adapters merely to change language or framework;
- replacing SQLite authority with Graphiti, LightRAG, or a model-managed store;
- making MCP handlers, Skills, or stochastic workers the workflow authority;
- requiring App Intelligence for acquisition or basic retrieval;
- immediate repository renaming or splitting before package boundaries and
  compatibility are proved;
- removing the direct Engine before service installation and fallback
  contracts reach parity.

## Acceptance Criteria

- a clean service installation is independently versioned, started, upgraded,
  diagnosed, and rolled back without installing an Agent Skill;
- the service continues governed collection and cache serving with no agent
  connected;
- a fresh MCP client can discover, query, inspect freshness/coverage, request
  governed refresh, and poll terminal state without scraper/browser knowledge;
- unloading the Skill does not stop or disable the service;
- disabling all stochastic workers does not stop acquisition, indexing, or
  evidence-backed retrieval;
- App Intelligence accepted/rejected/replay receipts prove deterministic host
  authority and finite bounds;
- GraphRAG degradation preserves citation-ready local retrieval and truthful
  capability status;
- the ordinary Skill path invokes MCP and contains no required instructions
  for direct browser, cookie, route, display, or scraper coordination;
- existing users can migrate without losing durable state, and rollback to the
  previous compatible service/client pair is documented and tested.

## Plan Conversion Gate

The conversion gate was satisfied on 2026-07-29:

1. Plan 0014 closed at its typed restart-bound blocker;
2. current service, installer, MCP bootstrap, contract, and install topology
   were inventoried;
3. the release-root lifecycle and exact fail-closed handshake were frozen;
4. the bounded S01/S02 packet above was derived;
5. the existing single-active-plan audit remains sufficient.

## Definition Of Done

`last30days` is operated and released as intelligence software whose durable
service and MCP interface are the primary product. Skills are optional,
least-privilege agent clients, and direct scraping mechanics are absent from
ordinary agent work.

## Planning Receipt | 2026-07-29

- product-boundary commit `8b32a0f` is pushed to `origin/main`;
- the planning audit passed with Plan 0014 as the sole active plan;
- Graphiti job `54a5ab14-06a4-4384-8dac-fa0f52b39c5b` completed on attempt 1;
- episode `d1da4f3e-a09f-4265-805f-b638103f5951` is visible in
  `last30days_skill_main` with read-after-write ready;
- no installed runtime or collection state changed.

### Checkpoint P0018-C01 | 2026-07-29

Plan version:

- 1

State transition:

- `PLANNED -> OPEN`

Progress classification:

- `outcome_progress`

Owned changes:

- reconciled Plan 0014's terminal blocker;
- inventoried the Skill-owned service, managed-unit installer, MCP packaged
  runtime bootstrap, exact contract-digest check, and version surfaces;
- froze the independent release layout, lifecycle transaction, handshake,
  compatibility constraints, rollback, tests, and five execution slices.

Validation evidence:

- revision 9 is disabled;
- all three revision-8 service jobs are terminal `failed`;
- database integrity is `ok`;
- service source and installed-on-disk scheduler digests match;
- the planning audit must pass with Plan 0018 as the sole active plan before
  this checkpoint is committed.

Remaining acceptance criteria:

- execute S01-A through the migration proof without crossing a hard stop.

Subagent status and reconciliation:

- `not_spawned`; the terminal live proof and successor packet were one
  serialized authority transition.

Graphiti write status:

- job `5dcdf153-0bd7-401a-9368-5c16a19d5b2c` completed on attempt 1;
- episode `80733eb7-85e5-4cd0-810b-4364868d59f9` is visible in
  `last30days_skill_main` with read-after-write ready.

Next action:

- execute S01-A: add the independent version and runtime-manifest boundary with
  reproducible artifact and package-boundary tests.

### Checkpoint P0018-C02 | 2026-07-29

Plan version:

- 1

State transition:

- `S01-A ready -> S01-A complete`

Progress classification:

- `outcome_progress`

Owned changes:

- commit `1a32e61` adds service-owned semantic version `0.2.7`;
- `service/runtime-manifest.json` now owns the canonical file-level SHA-256
  allowlist for the current service, acquisition-library, vendored Bird, and
  schema payload;
- `service/scripts/build-runtime.sh` verifies that manifest and emits a
  normalized reproducible `last30days-service-<version>.tar.gz`;
- package-boundary tests prove manifest drift fails closed, two builds are
  byte-identical, the extracted runtime starts, and Skill prose plus setup and
  install scripts do not enter the service artifact.

Validation evidence:

- 11 focused runtime-package, service-process, service-install, and
  Skill-artifact tests passed;
- the independent artifact digest was
  `bf7b1a0b5b561c911db645f1a152aa9cd4004087969c41c8349bc35c21c0f965`;
- the extracted runtime returned service help from its independent tree;
- the plan-authority audit passed with Plan 0018 as the sole active plan;
- CodeGraph synchronized with no pending changes and `git diff --check`
  passed.

Remaining acceptance criteria:

- execute S01-B, S02-A, S02-B, and the installed migration/rollback proof;
- then execute the remaining Plan 0018 workstreams and acceptance packets
  without treating this first artifact boundary as plan completion.

Subagent status and reconciliation:

- `not_spawned`; packet concurrency remains fixed at one and S01-A's builder,
  manifest, and boundary tests shared one tightly coupled write surface;
- the primary agent performed the bounded implementation and validation
  review; independent final outcome review remains required before packet
  closeout.

Graphiti write status:

- `graphiti_write_pending`;
- job `2c6e899b-b6e8-4442-a105-7b375476316f` timed out after its single
  180-second attempt while resolving nodes, and exact episode lookup returned
  no visible match;
- intended episode: commit `1a32e61` completed S01-A with the verified
  independent artifact boundary and S01-B is next.

Next action:

- execute S01-B: add the versioned release installer, stable managed unit,
  readiness receipt, atomic upgrade/rollback and release retention with
  isolated fake-user-manager lifecycle tests.

### Checkpoint P0018-C03 | 2026-07-29

Plan version:

- 1

State transition:

- `S01-B ready -> S01-B complete`

Progress classification:

- `outcome_progress`

Owned changes:

- commit `e2f966b` adds the repo-owned transactional service installer and
  stable managed user-unit template;
- install and upgrade verify every artifact payload digest, stage immutable
  versioned releases, switch `current` and `previous` atomically, restart once,
  and accept only exact service-version, contract-digest, schema-12 readiness;
- failed upgrades restore and prove the prior release, failed initial installs
  leave no selected or staged release, deliberate rollback swaps the two
  verified targets, and release retention preserves the active pair;
- the stable launcher resolves only the independent release tree, the unit
  contains no Agent Skill path, and the installer preserves existing
  owner-scoped configuration while creating an empty `0600` environment file
  when none exists;
- identical legacy-index publication no longer mutates `activated_at`, so
  restart, upgrade, and rollback preserve the complete schema-12 database
  dump.

Validation evidence:

- 175 `tests/test_service_*.py` tests passed;
- clean install, upgrade, manual rollback, failed-upgrade restoration, failed
  initial install, lifecycle controls, retention, full database-dump equality,
  schema version, and integrity were exercised with isolated XDG roots and a
  fake user manager;
- `systemd-analyze verify` passed for the rendered unit;
- `bash -n`, `git diff --check`, the plan-authority audit, and CodeGraph sync
  passed;
- the rebuilt independent artifact SHA-256 is
  `ff897b30c277759641c173cb6d81264c529c2c84ab663de5cb2fb9428c1de5a0`;
- commit `e2f966b` is pushed to `origin/main`.

Remaining acceptance criteria:

- execute S02-A, S02-B, and the installed migration/rollback proof;
- then execute the remaining Plan 0018 workstreams and acceptance packets
  without treating the independent lifecycle as the complete product
  transition.

Subagent status and reconciliation:

- `not_spawned`; packet concurrency remains fixed at one and the installer,
  unit, readiness transaction, and lifecycle tests shared one coupled write
  surface;
- the primary agent performed the bounded implementation and validation
  review; independent final outcome review remains required before packet
  closeout.

Graphiti write status:

- `graphiti_write_pending`;
- provider readiness passed, but job
  `98c0cb19-a8bf-49c9-a5ab-cf33901412d9` timed out after its single
  180-second attempt while resolving edges, and exact episode lookup returned
  no visible match;
- intended episode: commit `e2f966b` completed S01-B with the verified
  transactional service lifecycle and S02-A is next.

Next action:

- execute S02-A: extend service-info and generated Go contract facts with the
  explicit product/API/contract/database/runtime/MCP compatibility handshake
  and add compatible plus typed-incompatible client matrices.

### Checkpoint P0018-C04 | 2026-07-29

Plan version:

- 1

State transition:

- `S02-A ready -> S02-A complete`

Progress classification:

- `outcome_progress`

Owned changes:

- commit `f261d9c` makes `/v1/service-info` the explicit compatibility
  handshake for the independent service product and generated Go MCP client;
- the handshake now declares product, semantic service version, service API
  version, contract schema version and digest, database schema version,
  runtime-manifest digest, MCP adapter version and supported API/database
  ranges, plus a typed compatibility state;
- the Go adapter performs the handshake before ordinary endpoint calls and
  fails closed before the target request on product, API, contract, database,
  runtime-manifest, or malformed-handshake incompatibility;
- diagnostic service-info remains available for typed incompatibility while
  undeclared private fields are excluded from the exposed mismatch receipt;
- raw non-MCP HTTP clients receive the typed `mcp_client_not_declared` state.

Validation evidence:

- 176 `tests/test_service_*.py` tests passed;
- all Go tests and `go vet ./...` passed, including the compatible and complete
  typed-incompatible matrix;
- the process-level MCP integration test passed and proved declared product,
  API, adapter, database range, compatibility state, and runtime digest;
- 14 focused contract and product-surface tests passed;
- Python compilation, `git diff --check`, the plan-authority audit, and
  CodeGraph sync passed;
- the rebuilt independent artifact SHA-256 is
  `ca2106f38493fb341e757b10aed34693f74d8dfe904600200f7aff93bbaf88df`;
- commit `f261d9c` is pushed to `origin/main`.

Remaining acceptance criteria:

- execute S02-B and the installed migration/rollback proof;
- then execute the remaining Plan 0018 workstreams and acceptance packets
  without treating the compatibility handshake as the complete product
  transition.

Subagent status and reconciliation:

- `not_spawned`; packet concurrency remains fixed at one and the generated
  contracts, service handshake, Go client gate, and compatibility matrices
  shared one coupled write surface;
- the primary agent performed the bounded implementation and validation
  review; independent final outcome review remains required before packet
  closeout.

Graphiti write status:

- `graphiti_write_complete`;
- provider readiness passed and job
  `78868888-2c74-47e2-b164-1640473250ce` completed on its first attempt;
- episode `74112175-999e-4fe3-af63-bd3fe9d9d690` records commit `f261d9c`,
  the verified compatibility handshake, and S02-B as the next bounded action.

Next action:

- execute S02-B: package only the independent service artifact and lifecycle
  controls with the MCP release, and replace raw detached Python bootstrap
  ownership with the managed service install/start path.

### Checkpoint P0018-C05 | 2026-07-29

Plan version:

- 1

State transition:

- `S02-B ready -> S02-B complete`

Progress classification:

- `outcome_progress`

Owned changes:

- commit `ae79e56` replaces the MCPB's copied Agent Skill tree with an exact
  four-file independent service payload: semantic version, reproducible
  artifact, managed installer, and stable user-unit template;
- the release workflow verifies the compressed artifact contains the service
  entry point and no `SKILL.md`, then verifies the MCPB contains the installer
  and independently versioned artifact;
- Go bootstrap resolves exactly one packaged artifact and synchronously invokes
  the managed installer transaction with the requested owner-private socket;
- bootstrap no longer starts, detaches, or releases a raw Python child and the
  MCP adapter does not become daemon owner;
- the installer records the exact socket in the stable unit and uses the same
  path for readiness, while its sanitized MCP environment preserves only the
  bounded lifecycle and state-path controls it requires;
- all ten MCP operations remain present and the adapter still has no dependency
  on the legacy engine package.

Validation evidence:

- the full repository suite passed with 2,306 tests, 7 skips, and 6 subtests;
- all Go tests and `go vet ./...` passed;
- the real Python-service/Go-MCP process integration passed with the complete
  ten-tool surface;
- isolated packaging proved that no Skill prose or tree enters the MCP runtime
  or independent artifact;
- fake-manager lifecycle tests proved the stable managed unit, exact socket,
  readiness, install, upgrade, failure restoration, and rollback behavior;
- `bash -n`, `git diff --check`, the plan-authority audit, and CodeGraph sync
  passed;
- the MCP binary dependency graph contains no `internal/engine`;
- the independent artifact SHA-256 remains
  `ca2106f38493fb341e757b10aed34693f74d8dfe904600200f7aff93bbaf88df`;
- commit `ae79e56` is pushed to `origin/main`.

Remaining acceptance criteria:

- execute the installed schema-12 migration/restart/MCP/rollback proof while
  preserving corpus, job, schedule, timer, and database state;
- then execute the remaining Plan 0018 workstreams and acceptance packets.

Subagent status and reconciliation:

- `not_spawned`; packet concurrency remains fixed at one and the packaging,
  bootstrap, installer socket, workflow, tests, and docs shared one coupled
  product boundary;
- the primary agent performed the bounded implementation and validation
  review; independent final outcome review remains required before packet
  closeout.

Graphiti write status:

- `graphiti_write_pending`;
- the required provider preflight returned `degraded` with a bounded app-server
  `TimeoutError`, so policy prohibited queueing a memory write;
- intended episode: commit `ae79e56` completed S02-B with an independent
  MCP-packaged artifact and managed bootstrap; installed migration proof is
  next.

Next action:

- execute the migration proof against the current user-scoped schema-12 state:
  snapshot durable and service state, install the independent release through
  the managed path, prove unit/socket/version and all ten MCP operations,
  restart, roll back once, and prove state invariants unchanged.

### Checkpoint P0018-C06 | 2026-07-29

Plan version:

- 1

State transition:

- `migration proof ready -> first S01/S02 packet accepted`

Progress classification:

- `outcome_progress`

Owned changes and live outcome:

- commit `462ca42` preserves the sanitized machine-readable receipt at
  `docs/dev/notes/0018-installed-service-migration-proof.json`;
- the live legacy Skill-executed service was stopped only after a coherent
  schema-12, integrity, daemon, unit, timer, configuration, and logical
  database baseline was captured;
- independent release 0.2.7 installed through the managed transaction and the
  live unit now resolves through
  `.local/share/last30days/service/last30days-service`, not
  `.agents/skills`;
- restart changed the main PID, restored exact readiness, and retained exactly
  one daemon;
- a fresh stamped MCP client listed all ten operations, reported a compatible
  service/API/schema/runtime handshake, and returned the same evidence-backed
  cache-only query;
- one source-equivalent temporary 0.2.8 artifact upgraded successfully and
  deliberate rollback restored 0.2.7 readiness, leaving 0.2.8 as the managed
  previous target.

Validation evidence:

- database integrity remained `ok`, schema remained 12, and the complete
  logical database SHA-256 was identical before and after:
  `004586df10a6c93ac9f633d003ac40a97eb6ef1dd5a9a12d5cfc833d27c4d95f`;
- document, version, index, job, job-event, collection-spec,
  schedule-state, collection-run, attempt, and Graphiti-outbox counts were
  identical;
- owner configuration SHA-256 remained
  `7b32076759f0e743838249a88ba30efbe4c26003d59059bae3c86265a468619f`;
- no last30days timer unit existed before or after the proof;
- final state is active service 0.2.7, `current -> releases/0.2.7`,
  `previous -> releases/0.2.8`, one daemon, compatible MCP, and no hard-stop
  violation;
- the private ephemeral database backup and temporary proof fixtures were
  removed after the committed receipt and successful invariant comparison.

Remaining acceptance criteria:

- execute the Plan 0015 temporal retrieval/GraphRAG resilience packet;
- execute the Plan 0016 App Intelligence authority packet;
- complete S06 client-Skill redesign and S07 compatibility/release transition,
  then run an independent final outcome review before closing Plan 0018/P07.

Subagent status and reconciliation:

- `not_spawned`; Plan 0018 fixes active-agent concurrency at one and the live
  baseline/install/restart/MCP/upgrade/rollback sequence was one ordered state
  transaction;
- the primary agent performed the live proof and invariant comparison;
  independent final outcome review remains required before Plan 0018 closeout.

Graphiti write status:

- `graphiti_write_pending`;
- the next provider preflight passed, but the single allowed job
  `5a150399-0e46-4f59-8606-e3ae99b00021` timed out after 180 seconds while
  resolving nodes, and exact episode lookup returned no visible match;
- intended episode: commits `ae79e56` and `462ca42` completed S02-B and the
  installed first-packet migration proof without state loss; Plan 0015 is next.

Next action:

- execute Plan 0015 R01: snapshot current job, index, projection, evidence, and
  provider state for the one bounded temporal retrieval/GraphRAG resilience
  packet under Plan 0018.
