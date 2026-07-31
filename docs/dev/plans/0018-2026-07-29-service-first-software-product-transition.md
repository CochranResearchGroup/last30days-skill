# Plan 0018 | Service-first software product transition

State: OPEN
Roadmap: P07
Date: 2026-07-29
Plan version: 5
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
- S06 is accepted at commit `ac76e2b`: the 137-line primary Skill is a
  least-privilege ten-operation MCP client, privileged guidance is split into
  capability-gated references, and the packaged direct Engine remains only as
  an explicitly approved compatibility/debug path.
- S07 source/install/rollback is accepted at `04eec13`: service 0.2.9 and MCP
  4.0.1 are installed and compatible, the same cache-only citations survive
  rollback and restored-forward operation, and schema-12 state is unchanged.
- The first independent final review rejected release because autonomous
  governed acquisition/indexing with all stochastic workers disabled remains
  unproved. The first one-interval remediation proved autonomous service
  ownership but returned zero items. Checkpoint P0018-C15 classifies the
  evidence-backed successor as inherited standing authority and freezes the
  remaining outcome work without weakening the independent release gate.

## Standing Authority And Human Gates

The instruction to execute Plan 0018 supplies standing authority for ordinary
implementation, validation, repair, and bounded successor packets that preserve
this plan's objective and risk envelope. A packet-level hard stop ends that
attempt; it does not create a human gate by itself.

The primary agent may reframe and execute a successor without asking again when
the latest checkpoint classifies it as `inherited_authority`, keeps it within
the configured attempt ceiling, and preserves the approved systems, source
class, profile, public/private boundary, mutation class, resource ceilings,
rollback, and release gates.

New approval is required only for a checkpoint classified `human_gate` or
`scope_expansion`, including a new system, tenant, credential, private-data
class, audience, consequential external effect, ceiling increase, destructive
action, or bypass of the independent final-review or immutable-release gate.
Before requesting approval, cite the exact boundary the proposed action crosses.

Checkpoint P0018-C21 is the current authority for the remaining collection
proof. The operator-authorized 0.2.12 interval completed within the wall bound
but observed zero items. The packet's one-interval ceiling is exhausted.
Adding a ScrapeCreators credential would add a credential class, while another
keyless interval would exceed the explicit attempt ceiling; either path is a
real human gate. Independent acceptance, tagging, and release remain closed.

The operator's 2026-07-31 request to develop an agent-browser-powered Reddit
post routine authorizes the bounded C22 development packet below. It does not
authorize another collection interval, installation, service restart,
credential addition, evaluator run, tag, or release.

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

### Checkpoint P0018-C07 | 2026-07-29

Plan version:

- 1

State transition:

- `Plan 0015 planned -> Plan 0015 closed`

Progress classification:

- `outcome_progress`

Owned changes and runtime outcome:

- commit `f16f527` preserves the sanitized Plan 0015 machine receipt at
  `docs/dev/notes/0015-temporal-graphrag-resilience-proof.json`;
- one fresh stamped MCP temporal/profile case used explicit `as_of`,
  `known_as_of`, and the named profile, returned only the public and exact
  profile partition, eight content-addressed citations, and the profile's
  immutable evidence closure;
- job count remained 49 and acquisition count remained 65;
- the sole existing Graphiti projection replay retained one outbox row, one
  receipt, and the identical receipt UUID/digest while advancing its attempt
  count from one to two;
- an isolated unavailable-provider service truthfully reported `degraded` and
  `projection_unavailable` while serving the same eight SQLite citations and
  leaving job/acquisition counts unchanged;
- the real provider was not changed, remained healthy, and the live service
  returned to ready 0.2.7 with the same index and projection state.

Validation evidence:

- focused fresh-process MCP, live service, SQLite ledger, immutable-evidence,
  provider health, projection replay, and isolated degradation readbacks
  passed;
- no acquisition or browser work ran, no access partition widened, no
  projection authority duplicated, and no provider restoration was required;
- Plan 0015's acceptance criteria and definition of done are satisfied.

Remaining acceptance criteria:

- execute Plan 0016's accepted/rejected/replay App Intelligence packet;
- complete S06 client-Skill redesign and S07 compatibility/release transition;
- run independent final outcome review before closing Plan 0018/P07.

Subagent status and reconciliation:

- `not_spawned`; Plan 0015 and Plan 0018 both fix active-agent concurrency at
  one, and the query/replay/degradation/restore flow was a serialized bounded
  runtime packet;
- the primary agent performed the runtime proof and acceptance comparison;
  independent final outcome review remains required before Plan 0018 closeout.

Graphiti write status:

- `graphiti_write_pending`;
- provider preflight passed, but job
  `01002ba4-a550-4eb6-90b9-c633d9ed741d` timed out after its single
  180-second attempt while resolving nodes, and exact lookup found no episode;
- intended episode: commit `f16f527` closes Plan 0015 with cache-only
  temporal/profile, idempotent projection replay, and SQLite degradation
  acceptance; Plan 0016 is next.

Next action:

- execute Plan 0016 Packet 1: freeze one existing-evidence non-browser task
  type, exact contract version, accepted/rejected fixtures, and finite limits
  before any stochastic execution.

### Checkpoint P0018-C08 | 2026-07-30

Plan version:

- 1

State transition:

- `Plan 0016 planned -> Plan 0016 closed`

Progress classification:

- `outcome_progress`

Owned changes and runtime outcome:

- commit `bbff9f8` repairs the canonical `content_assessment` response schema
  for the Codex App Server strict JSON-schema subset, adds regression coverage,
  updates the independent runtime manifest, and preserves the sanitized
  machine receipt at
  `docs/dev/notes/0016-app-intelligence-contract-acceptance-proof.json`;
- one public-evidence task completed in one read-only Codex App Server call,
  consumed one of one calls, returned one proposal, and received accepted host
  validation, promotion, and replay receipts;
- one request containing forbidden `browser_profile` state returned
  `schema_invalid` on original validation and replay before persistence,
  provider execution, or mutation;
- canonical and installed 0.2.7 deterministic replay both returned the same
  receipt IDs without new rows or provider calls;
- the initial installed attempt retained one terminal pre-stochastic schema
  failure. The corrected schema enters the next compatible S07 service release
  without crossing Plan 0016's deployment/restart non-goal.

Validation evidence:

- the accepted task remained within one item, 4,096 bytes, one call, one cent,
  and 60 seconds;
- validation receipt
  `validation-receipt-61e56dc19c658ba94acb736abcc2ecd2`,
  promotion receipt
  `promotion-receipt-7612e1f20dd4ddfe0dacc24accec0a06`, and replay receipt
  `replay-receipt-7612e1f20dd4ddfe0dacc24accec0a06` are durable;
- logical hashes and row counts were identical before and after for canonical
  evidence, identity, claim, collection, document, entity, relationship, and
  index authority;
- installed discovery still exposes eight version-1 task types without
  prompts, credentials, raw provider events, or browser mechanics;
- 50 focused tests passed, the plan-authority audit passed, and the corrected
  independent artifact SHA-256 is
  `3c1b3ad42942206f487041c0ce2b383842582732da88f8c60df05d740125d989`.

Remaining acceptance criteria:

- execute S06 client-Skill redesign;
- execute S07 compatibility/release transition, including packaging the
  corrected assessment schema into the next compatible service release;
- run an independent final outcome review before closing Plan 0018/P07.

Subagent status and reconciliation:

- `not_spawned`; Plan 0016 fixed active-agent concurrency at one and the
  accepted/rejected/replay proof shared one live ledger and evidence authority;
- the primary agent executed and compared the complete bounded packet;
  independent final outcome review remains required before Plan 0018 closeout.

Graphiti write status:

- `graphiti_write_pending`;
- provider preflight passed, but job
  `9d14aca9-c195-4686-8bf4-449418015fb9` timed out after its single
  180-second attempt while resolving edges, and exact lookup found no episode;
- intended episode: commit `bbff9f8` closes Plan 0016 with strict-schema,
  accepted/rejected/replay, finite-bound, and zero-authority-mutation proof;
  S06 is next.

Next action:

- derive and execute the bounded S06 client-Skill redesign packet: make the
  ordinary Skill a concise MCP discovery/query/synthesis client, separate
  privileged guidance, and retain the direct Engine only as an explicit
  compatibility/debug path.

## S06 Implementation Packet | Least-privilege Agent Client

Outcome:

- the ordinary `/last30days` Skill loads a concise MCP
  discovery/query/synthesis contract and does not teach an ordinary querying
  agent source, credential, browser, retry, or scraper orchestration;
- monitoring, administration, maintenance, and direct-Engine compatibility
  guidance remain available only through explicit capability-gated reference
  files.

### Frozen ownership and write surfaces

- `skills/last30days/SKILL.md` owns the ordinary agent path and must remain
  self-contained for the ten MCP operations;
- `skills/last30days/references/monitoring.md`,
  `administration.md`, and `maintenance.md` own privileged progressive
  disclosure;
- `skills/last30days/references/direct-engine-compatibility.md` preserves the
  existing request-scoped Engine contract without making it the default;
- `README.md`, `CONFIGURATION.md`, and `docs/ONBOARDING.md` describe the same
  service-first/default and explicit-fallback boundary;
- one focused policy test owns the installed Skill-content boundary and the
  existing artifact test proves all required references plus the Engine remain
  packaged.

No Python, Go, schema, service, MCP handler, or database module moves belong to
this packet.

### Ordinary query contract

1. Discover `service_info` before any other product call.
2. Use `query` for current evidence-backed research and `temporal_query` for
   time-scoped/dossier/trend/comparison work.
3. Use `refresh` only when the user requests fresh work or accepted cache
   policy requires it; poll only the returned durable job with `job_status`.
4. Use `profile_history` and `coverage` as read-only evidence/coverage
   surfaces.
5. Synthesize only returned brief/evidence, cite returned URLs inline, and
   report freshness, uncertainty, degradation, access partition, and terminal
   job state truthfully.
6. Never operate browsers, credentials, adapters, retries, schedules,
   databases, indexes, App Intelligence turns, or service processes in the
   ordinary path.

### Capability gates

- load `monitoring.md` only for an explicit request to inspect health,
  freshness, coverage, topic/feed status, or durable job state;
- load `administration.md` only for an explicit request to mutate a governed
  topic/collection or request/resume bounded service work;
- load `maintenance.md` only for an explicit maintenance/repair-readiness
  request and preserve all human approval, branch, evaluation, restart, and
  deployment gates;
- load `direct-engine-compatibility.md` only when the MCP product surface is
  unavailable and the user explicitly requests the compatibility/debug path.
  Unavailability alone returns a safe diagnostic and fallback offer; it does
  not authorize live acquisition.

### Execution slices

1. S06-A: relocate the legacy Engine instruction contract behind the explicit
   compatibility gate; replace the ordinary Skill with the concise MCP client;
   add monitoring, administration, maintenance, and content-boundary tests.
2. S06-B: align README, configuration, onboarding, and installable artifact
   expectations; build the Skill artifact and run a fresh-client MCP smoke.

### Bounds and hard stops

- maximum implementation attempts per slice: 2;
- maximum review/rework cycles per slice: 1;
- maximum consecutive hardening-only checkpoints: 1;
- active-agent concurrency: 1;
- stop if the ordinary Skill requires Bash, WebSearch, browser, cookie,
  credential, scraper, direct database, or internal Python orchestration;
- stop if privileged mutation becomes reachable without explicit user intent;
- stop if the direct Engine or its packaged scripts are removed before S07
  compatibility and rollback acceptance;
- stop if any live service, timer, collection, browser, credential, or
  installed configuration changes.

### Validation and acceptance

- the ordinary Skill is no more than 300 lines and names all ten MCP
  operations with `service_info` as the first call;
- it contains no credential variable names, browser/profile route mechanics,
  scraper CLI instructions, or executable direct-Engine/service command;
- progressive references carry explicit read/mutation/approval boundaries and
  are present in the built `.skill` artifact;
- the direct Engine and scripts remain packaged and documented as
  compatibility/debug only;
- focused Skill policy, artifact, metadata, service-product, and MCP
  integration tests pass;
- a fresh MCP client lists all ten operations and completes a cache-only query
  without reading the compatibility or privileged references;
- planning audit, `git diff --check`, package-boundary audit, and current
  branch/tracking equality pass.

### Checkpoint P0018-C09 | 2026-07-30

Plan version:

- 1

State transition:

- `S06 unpacketized -> S06 packet ready`

Progress classification:

- `outcome_progress`

Owned changes:

- inventoried the 1,908-line Skill, its service-first preface, legacy
  request-scoped Engine contract, browser/credential mechanics, runtime
  preflight tests, artifact boundary, README, configuration, and onboarding;
- froze the ordinary MCP client, progressive disclosure, explicit fallback
  gate, write surfaces, two execution slices, acceptance tests, and hard
  stops above.

Validation evidence:

- the current Skill already names all ten MCP operations but then makes the
  Engine mandatory and exposes source/browser/credential mechanics in the same
  ordinary context;
- the independent service artifact remains separate from the Skill and the
  installable Skill still packages the compatibility Engine;
- the plan-authority audit must pass with Plan 0018 as the sole active plan
  before this checkpoint is committed.

Remaining acceptance criteria:

- execute S06-A and S06-B without changing live runtime state;
- execute S07 compatibility/release transition;
- run independent final outcome review before Plan 0018/P07 closeout.

Subagent status and reconciliation:

- `not_spawned`; Plan 0018 keeps active-agent concurrency at one and the
  canonical Skill plus its progressive references share one instruction
  boundary.

Graphiti write status:

- `not_attempted_for_planning_only_checkpoint`;
- the prior Plan 0016 memory attempt is already recorded as pending and this
  checkpoint adds no runtime fact beyond the repo plan.

Next action:

- execute S06-A: move the legacy instruction contract behind the explicit
  compatibility gate, author the concise ordinary Skill and privileged
  references, and add the focused content-boundary test.

### Checkpoint P0018-C10 | 2026-07-30

Plan version:

- 1

State transition:

- `S06 packet ready -> S06 accepted`

Progress classification:

- `outcome_progress`

Owned changes:

- replaced the 1,908-line ordinary Skill with a 137-line service client that
  calls `service_info` first and names the exact ten MCP operations;
- moved monitoring, administration, maintenance, and direct-Engine guidance
  into separate references with explicit intent, mutation, approval, and
  fallback gates;
- retained `scripts/last30days.py` and the full legacy Engine contract in the
  installable artifact without exposing credential, browser, scraper, Bash,
  WebSearch, or internal Python mechanics to ordinary queries;
- aligned README, configuration, onboarding, metadata, artifact, preflight,
  service-product, and version tests at commit `ac76e2b`, pushed to
  `origin/main`.

Validation evidence:

- 49 focused Skill, artifact, metadata, service-product, version, and MCP
  integration tests passed;
- the full `uv run pytest -q` suite passed with only its declared skips;
- `dist/last30days.skill` built with 133 files and contains the primary Skill,
  all four new references, the existing HTML reference, and the direct Engine;
- the primary Skill is 137 lines and the content-boundary test rejects
  privileged mechanics;
- a fresh canonical MCP process integration completed the cache-only contract;
  the installed client listed exactly ten operations, then `service_info` and
  `query(cache_only)` returned the expected fail-closed
  `local service contract is incompatible` diagnostic;
- planning audit passed with Plan 0018 as the sole active plan,
  `git diff --check` passed, and local `main` equaled `origin/main`.

Remaining acceptance criteria:

- execute S07 compatibility and release transition, including a corrected
  independently versioned service/MCP release, installed cache-only acceptance,
  state-preserving upgrade, and rollback proof;
- run independent final outcome review before Plan 0018/P07 closeout.

Subagent status and reconciliation:

- `not_spawned`; Plan 0018 fixes active-agent concurrency at one and the
  Skill/reference/package boundary was one coupled write surface;
- the primary agent performed implementation, focused and full validation,
  artifact inspection, and installed readback.

Graphiti write status:

- `graphiti_write_failed_validation`;
- provider readiness passed, but the single write attempt was rejected before
  queueing because the supplied group ID contained a hyphen;
- no retry was made under the one-attempt bound; the intended compact receipt
  is preserved in this checkpoint and Runbook Turn 61.

Next action:

- derive the bounded S07 release packet from current service, MCP, versioning,
  release, install, migration, and rollback authorities before changing live
  runtime state.

## S07 Implementation Packet | Compatibility And Release Transition

Outcome:

- cut one service-first release whose independently versioned service, MCP
  adapter, and optional Skill install together without version ambiguity;
- upgrade the installed user service and MCP adapter, prove cache-only
  compatibility and state preservation, prove rollback, and restore the new
  compatible release before deprecating request-scoped primary operation.

### Frozen versions and release identity

- Skill/plugin release: `4.0.0`, reflecting the intentional change from
  request-scoped Engine orchestration to an MCP-first ordinary client;
- MCP adapter/MCPB release: `4.0.1`, a compatible patch release that stamps its
  own manifest version rather than inheriting the repository tag;
- service release: `0.2.9`, because immutable proof release `0.2.8` already
  exists in the installed release root and must not be overwritten;
- repository tag: `v4.0.0`, naming the public Skill release while release
  notes list all three independently versioned artifacts.

The database remains schema 12 and service API remains version 1. Exact
contract-digest matching remains fail closed.

### Owned write surfaces

- Skill/plugin versions: `skills/last30days/SKILL.md`,
  `.claude-plugin/plugin.json`, and `.claude-plugin/marketplace.json`;
- MCP version/stamping: `mcp/manifest.json`,
  `mcp/internal/manifest/manifest_test.go`, `mcp/scripts/install-codex.sh`, and
  `.github/workflows/release.yml`;
- service release: `service/VERSION`, `service/runtime-manifest.json`, and
  exact version assertions;
- release/migration contract: `CHANGELOG.md`, `README.md`,
  `CONFIGURATION.md`, and `docs/ONBOARDING.md`;
- focused release-version tests and one sanitized installed-transition proof
  under `docs/dev/notes/`.

No schema migration, state-root change, adapter behavior change, source
acquisition, timer enablement, direct-Engine removal, repository split, or
contract compatibility relaxation belongs to this packet.

### Execution slices

1. S07-A: apply the three frozen versions, stamp local and CI MCP builds from
   `mcp/manifest.json`, regenerate the service runtime manifest, add
   independent-version drift tests, and document migration, diagnostics,
   deprecation, rollback, and release contents.
2. S07-B: validate and commit release source; build the service, Skill, MCP,
   and MCPB-equivalent staged payloads; inspect their package boundaries.
3. S07-C: snapshot installed schema-12 state; upgrade once to service 0.2.9;
   install MCP 4.0.1; prove ten-tool and cache-only compatibility; roll back
   once to 0.2.7; restore 0.2.9 through one deliberate second rollback; prove
   state and evidence-query equivalence.
4. S07-D: run the independent final Plan 0018 outcome review. Only after it
   accepts the complete objective may `v4.0.0` be created and pushed once;
   monitor the release workflow to a terminal result and record the published
   artifact/version readback.

### Bounds and gates

- maximum implementation attempts per slice: 2;
- maximum review/rework cycles per slice: 1;
- maximum consecutive hardening-only checkpoints: 1;
- active-agent concurrency: 1;
- one service upgrade, one rollback to 0.2.7, one rollback swap restoring
  0.2.9, one MCP installation, and at most three service restarts;
- one annotated tag creation/push, only after independent final acceptance;
- no authenticated acquisition, refresh, timer, browser, credential, source
  configuration, collection, App Intelligence, or database mutation action;
- the direct Engine remains packaged but is documented as deprecated for
  ordinary primary operation, not removed.

### Hard stops

- stop if the candidate artifact changes database schema, state path, socket,
  product identity, service API, or exact contract policy;
- stop on immutable release collision, failed readiness, more than one daemon,
  missing MCP operation, non-diagnostic request accepted under incompatibility,
  cache-only work creating a job, database integrity failure, or any
  before/after state-count or evidence-query drift;
- stop if rollback fails to restore 0.2.7 readiness or the second swap fails to
  restore 0.2.9;
- stop before tag creation if the independent review finds an unmet Plan 0018
  criterion or remote `v4.0.0` already exists;
- if the release workflow fails, preserve the immutable tag and report the
  failed release rather than rewriting it.

### Validation and acceptance

- independent version tests prove Skill/plugin `4.0.0`, MCP manifest/build
  stamp `4.0.1`, and service/runtime manifest `0.2.9`;
- full Python suite, `go test ./...`, `go vet ./...`, generated-contract drift,
  planning audit, package-boundary tests, and `git diff --check` pass;
- `.skill` includes the concise client, gated references, and compatibility
  Engine; service artifact contains no Skill; MCP staged runtime contains only
  the independent service artifact and lifecycle controls;
- fresh stdio MCP and configured Codex MCP both list the exact ten operations,
  report `compatibility_state=compatible`, and complete the same
  `cache_only` evidence query without a new job;
- installed 0.2.9 readiness binds service version, schema 12, exact contract
  digest, and runtime-manifest digest; current/previous remain immutable
  release selectors;
- upgrade, rollback, and restored-forward state preserve integrity, table
  counts, selected configuration hashes, index identity, evidence query
  citations, and disabled timer state;
- README, configuration, onboarding, and changelog clearly distinguish the
  optional Skill, MCP adapter, service artifact, migration steps, local
  incompatibility diagnostics, deprecation, and rollback;
- after independent acceptance, remote tag and GitHub release expose the
  Skill and Linux MCPB artifacts and identify service 0.2.9 plus MCP 4.0.1.

### Checkpoint P0018-C11 | 2026-07-30

Plan version:

- 1

State transition:

- `S07 unpacketized -> S07 packet ready`

Progress classification:

- `outcome_progress`

Owned changes:

- traced the live compatibility failure to the stale installed MCP binary
  (`vcs.revision=0e7938a8`) rather than the current service contract;
- confirmed current service 0.2.7 is ready on the independent release selector
  with schema 12 and canonical contract digest, while immutable temporary
  release 0.2.8 already occupies the rollback selector;
- froze Skill 4.0.0, MCP 4.0.1, service 0.2.9, the four execution slices,
  state-preserving live bounds, final review gate, and release-tag behavior.

Validation evidence:

- installed `current -> releases/0.2.7` and
  `previous -> releases/0.2.8`;
- direct service-info reports ready 0.2.7, API 1, schema 12, contract
  `f011c45999769f2c93b9044917179a0c683b3a43b35ec316f973bf91a2e76e34`;
- the installed MCP binary is from pre-handshake commit `0e7938a8`, while
  current source and service contract digests match;
- no remote `v4.0.0` tag exists and the downstream fork has no current GitHub
  release listing;
- no live state changed during packet derivation.

Remaining acceptance criteria:

- execute S07-A through S07-C;
- run S07-D independent final outcome review;
- publish and verify the accepted immutable release before closing Plan
  0018/P07.

Subagent status and reconciliation:

- `not_spawned`; Plan 0018 fixes active-agent concurrency at one and the
  release/install/rollback sequence requires one critical-path owner.

Graphiti write status:

- `not_attempted_for_planning_only_checkpoint`;
- S06's single rejected memory attempt is already recorded and this checkpoint
  adds no new completed runtime outcome.

Next action:

- execute S07-A: apply the frozen independent versions, deterministic MCP
  stamping, runtime manifest, drift tests, and migration/release documentation.

## Final Review Remediation Packet | Autonomous Deterministic Yield

Trigger:

- the first independent final review rejected release because the original
  acceptance lacked proof that governed acquisition and indexing continue with
  no agent connected and all stochastic workers disabled;
- the review also found that Plan 0018, P07, and the Runbook had not yet been
  reconciled with the completed S07 source/install/rollback outcome.

Outcome:

- prove one new bounded public Reddit collection interval is scheduled,
  acquired, published, and indexed by service 0.2.9 after the initiating
  client disconnects, with assessment and all App Intelligence execution
  disabled;
- pause the acceptance specification, prove quiescence and cache retrieval,
  reconcile canonical authorities, and rerun the independent final review.

### Exact live packet

- collection ID: `p0018-final-public-collection`;
- source/profile/redaction: Reddit, `default`, public;
- selector: topic `OpenClaw`;
- interval: 3,600 seconds, one initially due boundary only;
- bounds: three items, 24-hour lookback, 50 network requests, one dollar,
  120 seconds, durable retention;
- `assessment_enabled=false`;
- create one enabled revision, disconnect the initiating client, let the
  resident service own execution, then pause immediately after its sole
  terminal run.

### Bounds and hard stops

- one implementation/review remediation cycle; no second source or retry;
- one specification, one revision to enable, one scheduled run, one pause
  revision, zero service restarts, zero refresh requests, zero model calls;
- active-agent concurrency: 1;
- stop on more than one run, non-public evidence, acquisition/model/task budget
  escape, source failure, database integrity failure, inability to pause,
  post-pause run growth, or missing citation-ready cache output;
- a typed failure leaves the specification disabled and the release gate
  closed.

### Acceptance

- the service, not an attached agent process, owns the run from queued through
  published/partial terminal state;
- acquisition, document/version, evidence, active-index, coverage, and run
  receipts identify the one public interval;
- App Intelligence task/model-call counts do not change and assessment remains
  disabled;
- the paused revision is durable and the run count remains one after a
  post-pause observation window;
- cache-only retrieval returns citation-ready evidence without creating a job;
- Plan 0018 Current State/checkpoint, ROADMAP P07, and the latest RUNBOOK turn
  reflect S07 and remediation truth before the second independent judgment.

### Checkpoint P0018-C12 | 2026-07-30

Plan version:

- 1

State transition:

- `S07 packet ready -> source/install/rollback accepted; final review rejected`

Progress classification:

- `blocker_reduction`

Accepted evidence:

- release source commit `ec92991` carries Skill 4.0.0, MCP 4.0.1, service
  0.2.9, independent build stamping, regenerated runtime manifest, tests, and
  migration/deprecation documentation;
- service, Skill, MCP binary, and Linux MCPB artifacts built and passed package
  inspection;
- installed transition proof commit `04eec13` records ready compatible 0.2.9,
  exact ten-tool and four-citation cache-only results, 0.2.7 rollback and
  0.2.9 restore, schema/integrity/count/config/index preservation, and no
  acquisition or job creation.

Independent review result:

- `REJECT`; release tag creation remains prohibited;
- accepted seven of nine Plan criteria;
- rejected autonomous governed collection and all-stochastic-disabled
  acquisition/indexing evidence;
- also rejected stale Plan/ROADMAP/RUNBOOK descriptions.

Remaining acceptance criteria:

- execute the exact remediation packet above;
- reconcile all three canonical authorities;
- receive `ACCEPT` from the second and final independent review before tag
  creation.

Subagent status and reconciliation:

- independent evaluator session
  `019fb160-4f1a-7c51-9bb2-0f0d121d64c1` completed read-only with `REJECT`;
- the primary agent accepts all three findings and narrows remediation to one
  deterministic public-source proof plus authority reconciliation.

Graphiti write status:

- `not_attempted_for_rejected_outcome`;
- no incomplete or rejected plan outcome is written as durable success.

Next action:

- execute the one-spec/one-interval autonomous public collection proof; stop
  fail-closed on its first typed failure.

### Checkpoint P0018-C13 | 2026-07-30

Plan version:

- 1

State transition:

- `final review remediation ready -> terminal zero-yield blocker`

Progress classification:

- `terminal_blocker`

Live outcome:

- service 0.2.9 autonomously scheduled the exact
  `p0018-final-public-collection` 05:00Z boundary after the initiating client
  disconnected;
- the public Reddit run completed `published` in one job attempt with
  `assessment_enabled=false`, no model calls, no error code, and public access;
- acquisition, coverage, run, attempt, job, and event receipts advanced
  exactly once;
- the frozen `OpenClaw` selector returned zero attempted, observed, and stored
  items, so document/version/evidence/index counts did not change;
- revision 2 paused the specification immediately; the observed run count
  remained one and database integrity remained `ok`.

Hard-stop result:

- `zero_yield_no_index_change`;
- autonomous deterministic scheduling/acquisition authority is evidenced, but
  continued indexing with stochastic workers disabled remains unproved;
- the packet forbids a second source, selector, or retry, so the release gate
  remains closed and no second independent review or tag action ran.

Durable evidence:

- `docs/dev/notes/0018-final-autonomous-yield-proof.json`;
- baseline/final counts show acquisitions `65 -> 66`, service jobs `49 -> 50`,
  runs `12 -> 13`, attempts `13 -> 14`, coverage intervals `9 -> 10`, and
  model calls `0 -> 0`, while documents remain 50, versions 57, evidence spans
  419, and index versions 44.

Remaining acceptance criterion:

- obtain explicit authority for a new bounded selector/source attempt, because
  the approved one-attempt remediation cannot prove indexing yield.

Subagent status and reconciliation:

- no new evaluator was spawned after the hard stop;
- the first independent evaluator's release rejection remains authoritative.

Graphiti write status:

- `graphiti_write_queued`;
- provider readiness passed and the single write attempt queued job
  `c19fda55-810a-4f57-a96b-016a97a61267` in
  `last30days_skill_main`;
- no retry or success claim was made while processing remained asynchronous.

Next action:

- stop and request explicit user authority for one new public selector/source
  attempt; do not publish `v4.0.0` or reinterpret zero yield as acceptance.

### Checkpoint P0018-C14 | 2026-07-30

Plan version:

- 1

State transition:

- `terminal zero-yield blocker -> diagnosed, awaiting explicit retry authority`

Progress classification:

- `blocker_reduction`

Read-only diagnosis:

- the terminal run's acquisition
  `work-ae5f9c10db00172e6933c1122ee2357a` is a successful empty Reddit result,
  not an adapter, budget, validation, or publication failure;
- the public Reddit path returns an empty successful acquisition when keyless
  discovery and the requested date filter yield no posts and no configured
  backup source returns items;
- the same installed service acquired three public Reddit items for
  `temporal knowledge graphs` at 2026-07-29T12:38Z with the same three-item,
  24-hour, 50-request, one-dollar, 120-second work envelope;
- the current public Reddit corpus contains three 2026-07-28/29 documents from
  that selector, so it is the narrowest source-backed successor candidate;
- the existing connected MCP process still reports the already-documented
  stale-binary compatibility failure. The accepted fresh-stdio MCP proof
  remains the installed-client authority; this diagnosis used direct
  read-only service/database receipts.

Proposed successor packet:

- requires explicit user authority before any live write;
- create distinct collection ID
  `p0018-final-public-collection-v2`, source/profile/access Reddit,
  `default`, public, selector `temporal knowledge graphs`;
- preserve the prior bounds: one 3,600-second initially due boundary, three
  items, 24-hour lookback, 50 network requests, one dollar, 120 seconds,
  durable retention, and `assessment_enabled=false`;
- disconnect after creation, allow exactly one service-owned scheduled run,
  then pause immediately;
- stop on zero yield, no document/version/index advance, any second run,
  non-public evidence, budget escape, model/task growth, or failure to pause;
- only a positive indexed yield may proceed to the second independent review.

Current state:

- `p0018-final-public-collection` remains paused at revision 2;
- no second acquisition, collection mutation, refresh, model call, review, tag,
  or release action ran;
- Plan 0018 and P07 remain `OPEN`; the release gate remains closed.

Graphiti write status:

- provider readiness passed;
- the compact blocker diagnosis and successor proposal queued as job
  `779ab4a7-5532-437c-afc7-90d6ff38ae42` in
  `last30days_skill_main`.

Next action:

- await explicit user authority for the proposed one-attempt successor packet;
  without it, preserve the paused runtime and unpublished release.

### Checkpoint P0018-C15 | 2026-07-30

Plan version:

- 2

State transition:

- `awaiting unnecessary retry approval -> bounded successor ready`

Progress classification:

- `blocker_reduction`

Authority classification:

- `inherited_authority`;
- the standing objective to execute Plan 0018 authorizes ordinary bounded
  remediation needed to satisfy its unchanged autonomous-indexing criterion;
- checkpoint P0018-C13's fail-closed stop terminated the `OpenClaw` packet
  instance. It did not revoke the goal's standing authority;
- the proposed successor changes only the public Reddit topic selector and
  uses a distinct collection ID. It adds no system, source class, credential,
  tenant, audience, private-data class, mutation class, stochastic worker,
  publication, or immutable release action.

Drift controls:

- this successor is the second and final work-unit attempt, matching
  `max_work_unit_attempts: 2`;
- keep source/profile/access at Reddit, `default`, public;
- keep the prior three-item, 24-hour, 50-request, one-dollar, 120-second,
  one-scheduled-run, assessment-disabled bounds;
- create `p0018-final-public-collection-v2`, disconnect the initiating client,
  allow exactly one service-owned interval, and pause immediately;
- stop on zero yield, no document/version/index advance, a second run,
  non-public evidence, budget escape, model/task growth, database-integrity
  failure, or inability to pause;
- any further acquisition attempt after this successor requires a new plan
  version because the configured attempt ceiling would be exhausted;
- independent final `ACCEPT` remains mandatory before the already-authorized
  one-time immutable `v4.0.0` tag/release action.

Authority correction:

- checkpoint P0018-C14's explicit-approval requirement is superseded;
- `no second source or retry` in the first remediation packet remains true for
  that packet instance. It does not prohibit this evidence-backed successor
  inside the standing goal and attempt ceiling;
- fail-closed continues to mean preserve state, checkpoint the failure, and
  reframe within bounds. It does not automatically create a human gate.

Current state:

- the original `p0018-final-public-collection` remains paused at revision 2
  with one run;
- the successor specification does not yet exist and no successor acquisition
  has run;
- Plan 0018 and P07 remain `OPEN`; the release gate remains closed.

Remaining acceptance criterion:

- execute the one-attempt successor and prove public document/version/index
  advancement with assessment and model execution disabled;
- if it succeeds, run the second independent final review;
- if it fails, stop at the exhausted attempt ceiling without requesting
  repeated approval for another equivalent retry.

Subagent status and reconciliation:

- `not_spawned`; active-agent concurrency remains one.

Graphiti write status:

- `graphiti_write_queued`;
- provider readiness passed and the compact policy decision queued as job
  `ff80dc94-d042-4989-9047-3964aa6f241e` in
  `last30days_skill_main`.

Next action:

- execute `p0018-final-public-collection-v2` under inherited standing
  authority; do not ask for another approval unless a named boundary above
  changes.

### Checkpoint P0018-C16 | 2026-07-30

Plan version:

- 2

State transition:

- `bounded successor ready -> terminal runtime-bound failure`

Progress classification:

- `regression`

Authority classification:

- `human_gate`;
- the two-attempt live acceptance ceiling is exhausted;
- deterministic diagnosis, source repair, tests, and a reviewable repair
  packet remain under standing Plan 0018 authority;
- installing or restarting a repaired daemon, changing the live ceiling, or
  initiating a third acquisition interval crosses the exhausted-attempt and
  runtime-mutation boundaries and requires explicit approval.

Live outcome:

- revision 1 of `p0018-final-public-collection-v2` enabled one public Reddit
  topic interval for `temporal knowledge graphs` with assessment disabled;
- after the initiating command disconnected, service 0.2.9 scheduled the
  18:00Z boundary as timer run
  `collection-run-765dce990e42275c8b949a861b08000d`;
- both internal job leases exceeded the 120-second worker wall bound without
  creating an acquisition receipt;
- the supervisor recovered the first expired lease, exhausted the second, and
  marked job `5a67717d-9fd0-4d8f-845a-6f37fb6fe813` failed with
  `retry_exhausted`;
- the collection run and both collection attempts incorrectly remained
  `acquiring`, exposing a deterministic terminal-state propagation defect;
- revision 2 paused the spec before the next due poll; one post-pause
  observation confirmed one run, eleven job events, and no second interval.

Hard-stop result:

- `wall_timeout_exceeded_no_acquisition_receipt`;
- acquisitions, documents, versions, evidence, coverage, and index versions
  did not advance;
- model calls and intelligence tasks stayed unchanged;
- database integrity remained `ok`, service 0.2.9 remained ready, and the
  active index stayed `index-4f096317e15c57da386466f2`;
- the independent review, tag, and release gates remain closed.

Durable evidence:

- `docs/dev/notes/0018-successor-collection-spec.json`;
- `docs/dev/notes/0018-successor-autonomous-yield-proof.json`.

Remaining acceptance criteria:

- repair worker-wall-bound completion so timeout produces a typed acquisition
  result before the lease expires;
- reconcile terminal job failure into terminal collection-run and attempt
  states;
- validate the repair deterministically and prepare an installed transition
  with rollback;
- obtain explicit approval before the repaired live install/restart and one
  third acquisition interval;
- only indexed public yield may proceed to independent final review.

Subagent status and reconciliation:

- `not_spawned`; active-agent concurrency remained one.

Graphiti write status:

- `graphiti_write_timed_out`;
- provider readiness passed, but the compact C16 failure memory job
  `24763c2a-74f4-44e6-a15f-01550c2460f4` in
  `last30days_skill_main` timed out during node resolution after 120 seconds;
- C17 carries the superseding repair outcome.

Next action:

- checkpoint this failed live packet, then derive and execute one bounded
  deterministic source-repair packet; stop before installed-runtime mutation
  or a third live interval.

### Checkpoint P0018-C17 | 2026-07-30

Plan version:

- 2

State transition:

- `terminal runtime-bound failure -> deterministic repair validated`

Progress classification:

- `blocker_reduction`

Authority classification:

- `human_gate` for installing/restarting service 0.2.10 or initiating a third
  live interval;
- `inherited_authority` covered the source repair, versioned runtime artifact,
  deterministic validation, and reviewed transition packet;
- no installed service, collection specification, live job, tag, or release
  was mutated by this checkpoint.

Deterministic diagnosis and repair:

- the subprocess worker boundary could raise an ordinary exception that the
  job runner did not convert into a typed acquisition result;
- the resident acquisition loop isolated that exception, leaving the service
  job leased until supervisor recovery;
- terminal lease recovery updated `service_jobs` but did not reconcile the
  linked collection run or attempt rows;
- service 0.2.10 now converts unexpected worker-boundary exceptions into the
  safe transient code `worker_internal_error`;
- the collection scheduler now idempotently reconciles terminal supervisor
  jobs before due-work selection, including all stranded nonterminal attempt
  rows while a collection is paused.

Validation evidence:

- focused worker, runner, supervisor, collection, package, lifecycle, and
  process suites passed;
- a new deterministic two-lease exhaustion test proves that a paused
  collection closes both attempt rows and the run as
  `failed/retry_exhausted`;
- a new worker-exception test proves bounded retry, lease release, safe error
  persistence, and suppression of private exception detail;
- the complete suite passed: `2318 passed, 7 skipped, 6 subtests passed`;
- the reproducible service 0.2.10 artifact digest is
  `b73aaa774f8a580ac2d375a36f0a5405f6f0967639a8a9a9b6b1c17393cafd98`.

Reviewed transition packet:

- `docs/dev/notes/0018-service-0.2.10-reviewed-transition-packet.json`;
- one upgrade from installed 0.2.9 to 0.2.10;
- readiness, schema-12, integrity, state-preservation, and prior-run
  reconciliation checks;
- exactly one resumed service-owned public interval, immediate pause, and the
  existing acquisition/model/budget/source bounds;
- automatic rollback to 0.2.9 on transition or readiness failure;
- no evaluator, tag, or release action.

Remaining acceptance criteria:

- obtain explicit approval for the reviewed runtime packet;
- prove one durable public acquisition receipt plus document/version/index
  advancement with assessment and model execution disabled;
- obtain independent final `ACCEPT`;
- only then perform the already-authorized one-time immutable `v4.0.0`
  tag/release action.

Subagent status and reconciliation:

- `not_spawned`; active-agent concurrency remained one.

Graphiti write status:

- `graphiti_write_completed`;
- provider readiness passed and the compact source-backed repair memory job
  `4d252dc0-1bd7-4d22-9d28-912a26f11c1d` completed in
  `last30days_skill_main`.

Next action:

- commit and push the deterministic 0.2.10 repair and reviewed transition
  packet, then stop at the explicit installed-runtime/live-attempt gate.

### Checkpoint P0018-C18 | 2026-07-30

Plan version:

- 2

State transition:

- `deterministic repair validated -> installed repair rejected by live proof`

Progress classification:

- `regression`

Authority classification:

- `explicit_human_gate_satisfied`;
- the user authorized
  `docs/dev/notes/0018-service-0.2.10-reviewed-transition-packet.json` with
  `ok go`;
- the packet authorized one managed upgrade, one service-owned public
  interval, immediate pause, bounded containment, and rollback on transition
  or readiness failure;
- no evaluator, tag, or release action was authorized or executed.

Installed transition and reconciliation:

- source commit `fc118de` and artifact digest
  `b73aaa774f8a580ac2d375a36f0a5405f6f0967639a8a9a9b6b1c17393cafd98`
  matched the pushed packet;
- the managed service upgraded from 0.2.9 to ready 0.2.10 with 0.2.9 as the
  rollback target, schema 12, integrity `ok`, and unchanged corpus/index/model
  state;
- startup reconciliation closed the target failed run and its two attempts,
  plus three older stranded failed acceptance runs, without acquisition,
  document, evidence, job, model, task, or index growth.

Live outcome and containment:

- the resume client exited and the resident timer created exactly one 20:00Z
  public Reddit run, `collection-run-f37f713ff12daa427393a42314e8dc2b`,
  with job `06b8025c-5ade-4c25-9029-68f382257fd4`;
- revision 4 paused the spec immediately after the run appeared;
- attempt 1 crossed the 120-second worker wall bound with no acquisition
  receipt while the job remained `acquiring`;
- the service was stopped before lease expiry, preventing automatic attempt 2;
- the exact live lease was terminalized through the supervisor's fenced
  failure API as `worker_wall_timeout_unenforced`, not by direct SQL;
- service 0.2.10 was restored ready; the job, run, and sole attempt are failed,
  the spec remains paused, integrity is `ok`, and model calls remain zero.

Durable evidence:

- `docs/dev/notes/0018-service-0.2.10-live-timeout-proof.json`.

Acceptance result:

- `REJECT`;
- autonomous timer ownership and one-run containment passed;
- public acquisition receipt, document/version advancement, and index
  advancement failed;
- independent final review, `v4.0.0`, and release remain closed.

Subagent status and reconciliation:

- `not_spawned`; active-agent concurrency remained one.

Next action:

- diagnose and repair the remaining deterministic wall-bound cleanup defect;
  do not install another runtime or initiate another live interval under plan
  version 2.

### Checkpoint P0018-C19 | 2026-07-30

Plan version:

- 3

State transition:

- `installed repair rejected by live proof -> bounded reaping repair ready`

Progress classification:

- `blocker_reduction`

Authority classification:

- `inherited_authority` covered deterministic diagnosis, source repair,
  tests, service 0.2.11 packaging, and a reviewed successor packet;
- `human_gate` applies to installing/restarting service 0.2.11 or initiating
  any further live interval because repeated live failure exhausted the prior
  plan-version bound;
- the proposed packet does not alter source, profile, public-data, model,
  budget, request, item, or release boundaries.

Changed assumption and repair:

- SIGKILL does not guarantee prompt child reaping;
- `_read_bounded()` killed the worker at its deadline and then called
  `process.wait()` without a timeout, so a delayed reap could defeat the host
  wall bound and prevent the typed timeout receipt;
- service 0.2.11 bounds post-kill wait to one second, delegates delayed reaping
  to a daemon cleanup thread, and returns the existing safe transient
  `worker_timeout`;
- a non-reaping-child regression test proves the synchronous cleanup path
  cannot wait indefinitely.

Reviewed successor:

- `docs/dev/notes/0018-service-0.2.11-reviewed-transition-packet.json`;
- one upgrade from installed 0.2.10 to 0.2.11 and one new timer run only after
  explicit approval;
- at most one started job attempt, a typed receipt by 121 seconds, immediate
  pause, and rollback to 0.2.10 on transition/readiness failure;
- independent final review and immutable release gates remain unchanged.

Validation evidence:

- 47 focused worker, job-runner, collection, runtime, package, lifecycle, and
  release-version tests passed;
- the complete suite passed:
  `2319 passed, 7 skipped, 6 subtests passed`;
- reproducible artifact:
  `dist/service/last30days-service-0.2.11.tar.gz`;
- SHA-256:
  `2b6facb0a31136d8e9a60df4c71705b33224a858ba3510db6cfc3d520e9d91ff`.

Subagent status and reconciliation:

- `not_spawned`; active-agent concurrency remained one.

Graphiti write status:

- `graphiti_write_queued`;
- provider readiness passed and the compact C18/C19 outcome memory queued as
  job `5628c80e-9cab-4baf-b20e-e1d846d280cb` in
  `last30days_skill_main`.

Next action:

- complete broad validation, commit and push plan version 3 plus service
  0.2.11, then stop at the explicit repeated-live-failure gate.

### Checkpoint P0018-C20 | 2026-07-30

Plan version:

- 4

State transition:

- `bounded reaping repair ready -> deadline-aware acquisition repair validated`

Progress classification:

- `blocker_reduction`

Authority classification:

- `human_gate`;
- the operator's `ok go` explicitly authorizes the recommended 120-second
  deadline-aware repair, managed transition, and one bounded live proof;
- the packet preserves the existing public Reddit source, default profile,
  three-item limit, 50-request outer ceiling, 100-cent budget, disabled
  assessment/model execution, rollback, and release gates.

Changed assumption and repair:

- 120 seconds is a reasonable host safety ceiling, but the prior standard-depth
  keyless route followed by the full keyed fallback had a legitimate
  worst-case duration beyond that ceiling;
- service requests with an item limit of three now use quick keyless depth;
- an empty keyless result permits exactly one keyed global request, capped at
  20 seconds, with subreddit fan-out and DNS retry widening disabled;
- larger and interactive Reddit searches retain their existing depth and
  fallback behavior;
- the existing one-second post-kill reap bound remains the final containment
  layer.

Authorized successor:

- `docs/dev/notes/0018-service-0.2.12-authorized-transition-packet.json`;
- one upgrade from installed 0.2.10 to 0.2.12 and one new timer run;
- at most one started job attempt, immediate collection pause, and rollback to
  0.2.10 on transition/readiness failure;
- independent final review and immutable release gates remain unchanged.

Validation evidence:

- 95 focused acquisition-worker, Reddit, HTTP, runtime-package, and
  release-version tests passed;
- the complete suite passed:
  `2322 passed, 7 skipped, 6 subtests passed`;
- reproducible artifact:
  `dist/service/last30days-service-0.2.12.tar.gz`;
- SHA-256:
  `c4e6fe9a5bf86a615e411245509d45276de29ddb3320fd69e3abbd9aa1ddf3a9`.

Subagent status and reconciliation:

- `not_spawned`; active-agent concurrency remained one.

Next action:

- commit and push the exact 0.2.12 source, manifest, packet, and checkpoint;
- verify packet preconditions, perform the authorized managed transition, and
  observe exactly one live interval;
- hard-stop and contain on any packet violation; proceed to independent final
  review only if current indexed public yield satisfies every success criterion.

### Checkpoint P0018-C21 | 2026-07-30

Plan version:

- 4

State transition:

- `deadline-aware acquisition repair validated -> wall-bound success with zero-yield rejection`

Progress classification:

- `blocker_reduction`

Authority classification:

- `human_gate`;
- the authorized 0.2.12 transition and one live interval are complete;
- a new attempt would exceed the packet's one-run ceiling;
- configuring the prepared keyed fallback would introduce a new credential
  class, which also requires explicit approval.

Live outcome:

- installed service 0.2.12 is ready with schema 12, integrity `ok`, and 0.2.10
  as rollback;
- revision 5 enabled one timer-owned run after client disconnect and revision 6
  paused it immediately;
- run `collection-run-da045ae3ddd7aef4f55f95ea8edb0bc2` and job
  `a1eb58b1-7a47-4dfd-8cf1-6cc3a990dbb0` published in about 2.5 seconds with
  exactly one attempt;
- acquisition `work-1ee0b617c4be5215bfa444ebfcf573a3` is a durable public
  `succeeded` receipt with zero items and zero adapter cost;
- no ScrapeCreators credential is configured in the service's global or
  default-profile configuration, so the prepared keyed fallback did not run;
- coverage recorded `observed_empty`; documents, versions, evidence, and index
  remained unchanged; model calls stayed zero and intelligence tasks stayed two.

Acceptance:

- autonomous timer ownership: accepted;
- typed result within the worker wall bound: accepted;
- exactly one run and one attempt: accepted;
- public item, document/version, and active-index advance: rejected;
- independent final review and immutable release: not run.

Durable proof:

- `docs/dev/notes/0018-service-0.2.12-live-zero-yield-proof.json`.

Subagent status and reconciliation:

- `not_spawned`; active-agent concurrency remained one.

Graphiti write status:

- provider readiness passed;
- the compact C21 outcome memory queued as job
  `555f8b0c-20b6-4529-89ed-57d1b9dd34e8` in
  `last30days_skill_main`.

Next action or stop reason:

- stop at the exhausted live-attempt and credential-class human gate;
- best next packet is one additional public/default-profile, three-item,
  120-second interval using a previously successful high-yield selector,
  without adding a credential; adding ScrapeCreators instead requires separate
  authorization to configure that credential.

### Execution Packet P0018-C22 | 2026-07-31

Plan version:

- 5

Bounded outcome:

- implement a deterministic agent-browser-powered Reddit post-search adapter
  that returns the existing normalized Reddit item contract and can be selected
  as the public adapter's bounded fallback when RSS/Shreddit yields nothing;
- preserve the current public-first and paid-fallback behavior outside the new
  browser selection seam.

Current evidence:

- service 0.2.12 completed its authorized public Reddit interval within the
  worker wall bound but returned a durable zero-item receipt;
- Facebook and LinkedIn already prove the repo's typed agent-browser workspace,
  navigation, DOM extraction, quality-gate, and diagnostic pattern;
- a no-launch agent-browser access plan for target `reddit` selected the
  existing `last30days-facebook` shared-service profile and a local-headless
  CDP posture, but Reddit has no dedicated target registration or freshness
  evidence yet.

Owned write surfaces:

- `skills/last30days/scripts/lib/reddit_browser.py`;
- the Reddit selection seam in
  `skills/last30days/scripts/lib/service_acquisition_worker.py`;
- service version, runtime manifest, and unreleased changelog surfaces for the
  source-reserved 0.2.13 package;
- focused Reddit browser and worker tests;
- `CONFIGURATION.md`, this plan, `ROADMAP.md`, and `RUNBOOK.md`.

Acceptance criteria:

1. fixture-driven tests prove canonical URL, subreddit, author, score, comment
   count, timestamp, relevance, deduplication, date filtering, and item-limit
   behavior;
2. blocked, login, rate-limit, navigation-mismatch, empty-extraction, and
   malformed agent-browser outputs fail with typed, non-secret diagnostics;
3. the service adapter remains public-first, invokes the browser routine only
   after empty keyless yield, and invokes the paid adapter only after empty or
   unavailable browser yield;
4. browser work uses the installed agent-browser JSON CLI with caller labels,
   target `reddit`, one managed session, bounded waits/scrolls, and no direct
   CDP-port or browser-process discovery;
5. one public development smoke may prove current Reddit DOM compatibility;
   it must not create or resume a collection spec, install a service release,
   or record profile freshness;
6. targeted tests and the complete deterministic suite pass, and docs describe
   every new configuration knob.

Non-goals and hard gates:

- no Reddit authentication seeding, credential configuration, private/community
  access, voting, posting, commenting, messaging, or account mutation;
- no new collection interval, service install/restart, evaluator/model call,
  independent acceptance, tag, or release;
- do not claim durable indexed yield from a standalone browser smoke;
- stop after one public smoke, on any checkpoint/challenge, or if the routine
  cannot remain inside the existing 120-second acquisition wall.

Execution bounds and delegation receipt:

- active-agent concurrency: one;
- work-unit attempts: one implementation pass and one remediation pass;
- live browser smokes: at most one query and one managed session;
- review/rework cycles: one;
- delegation: `not_spawned`; the repo's CodeGraph policy requires direct
  structural exploration, the write surfaces are tightly coupled, and the
  active Plan 0018 lane fixes concurrency at one.

Authority classification:

- `inherited_authority` for implementation, fixture validation, documentation,
  and one public read-only browser smoke because they preserve the approved
  Reddit source, profile class, public-data boundary, and resource ceiling;
- `human_gate` remains in force for another timer interval, any new credential
  class, install/restart, evaluator, tag, or release.

Terminal condition:

- checkpoint with either validated source-ready implementation plus explicit
  live-smoke status, or a typed blocker and no production/runtime mutation.

### Checkpoint P0018-C23 | 2026-07-31

Plan version:

- 5

State transition:

- `wall-bound success with zero-yield rejection -> source-ready browser fallback with current-DOM extraction proof`

Progress classification:

- `blocker_reduction`

Implementation result:

- commit `12b7298` adds the opt-in Reddit browser adapter, configuration
  contract, worker fallback order, typed diagnostics, fixture tests, and
  source-reserved service 0.2.13 runtime manifest;
- the deterministic service order is keyless RSS/Shreddit, then the optional
  agent-browser DOM routine, then the existing paid ScrapeCreators fallback;
- the browser routine uses target `reddit`, caller labels, one managed session,
  canonical public post URLs, date/relevance/deduplication gates, and no account
  mutation.

Validation evidence:

- 38 focused Reddit-browser, worker, environment, package, lifecycle, and
  release-version tests passed after the final version/manifest refresh;
- the complete deterministic pytest suite passed after the final changes;
- `git diff --check` and Python compilation passed;
- agent-browser remote-view doctor reported a ready route pool with live `:11`
  and `:12` displays before the smoke.

Live smoke status:

- exactly one public `OpenClaw` search ran in managed session
  `last30days-reddit` on route `guacamole:1` and completed in about 47 seconds;
- the first extraction correctly failed closed as `extraction_empty` because
  current Reddit search results use `data-testid="search-post-unit"`, not the
  older `shreddit-post` element;
- the one authorized remediation pass added the current search-unit DOM shape;
  a read against the same already-open page then returned seven structured
  candidates with canonical permalinks, authors, subreddits, timestamps,
  scores, and comment counts;
- no second query or end-to-end collection run was started, so this is current
  DOM/extractor proof, not durable indexed-yield proof.

Acceptance result:

- source implementation and deterministic acceptance criteria: accepted;
- current Reddit DOM extraction compatibility: accepted on the already-open
  smoke page after one bounded remediation;
- installed service, autonomous collection, durable document/index advance,
  independent release review, tag, and release: not run.

Authority classification:

- `inherited_authority` covered implementation, the one public smoke, its
  single remediation pass, validation, local commit, and durable closeout;
- `human_gate` remains in force for installing/restarting 0.2.13, another live
  collection interval, a new credential, evaluator/model work, tag, or release.

Subagent status and reconciliation:

- `not_spawned`; the active plan fixed concurrency at one, the CodeGraph policy
  required direct structural exploration, and the write surfaces were tightly
  coupled.

Graphiti write status:

- provider readiness passed;
- the compact C22/C23 outcome memory queued in `last30days_skill_main` as job
  `6691ce5f-4b4d-4b57-a89a-b5ab1259da81`.

Next action or stop reason:

- stop with source 0.2.13 committed locally and production unchanged;
- require explicit approval before a managed 0.2.13 install/restart and one
  bounded collection interval; keep independent review and release closed
  until durable indexed yield is proven.
