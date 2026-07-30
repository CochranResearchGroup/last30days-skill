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
