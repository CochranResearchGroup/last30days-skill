# Plan 0018 | Service-first software product transition

State: OPEN
Roadmap: P07
Date: 2026-07-29
Plan version: 21
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

- The independent managed service is the installed runtime authority at
  version 0.2.25/schema 12 with 59 documents, 59 embeddings, and active index
  `index-b5cd4d63810e8d5333a0aa93`. Rollback remains service 0.2.24.
- The service publishes its exact contract, API, schema, runtime-manifest,
  source-readiness, and active-index facts. The MCP adapter performs the
  fail-closed compatibility handshake before ordinary operations.
- User-scoped configuration owns the five-source catalog, ordered access
  chains, browser timeout, display isolation, profile, and session policy. All
  37 collection specifications are disabled, including the five version-17
  manual-canary specifications.
- A timer-owned public Reddit interval on 0.2.14 published one durable version
  and advanced the active index with assessment disabled and no connected
  acquisition agent. The specification is paused and remained quiescent.
- Service architecture, timer ownership, durable publication/indexing, and
  rollback are accepted foundations. Source/access-method validation is now an
  orthogonal evidence campaign whose individual results cannot reopen those
  accepted foundations absent a shared-runtime regression.
- S06 is accepted at commit `ac76e2b`: the 137-line primary Skill is a
  least-privilege ten-operation MCP client, privileged guidance is split into
  capability-gated references, and the packaged direct Engine remains only as
  an explicitly approved compatibility/debug path.
- S07 source/install/rollback is accepted at `04eec13`: service 0.2.9 and MCP
  4.0.1 are installed and compatible, the same cache-only citations survive
  rollback and restored-forward operation, and schema-12 state is unchanged.
- The earlier independent final-review rejection on missing durable timed yield
  is superseded by C27's installed 0.2.14 proof. A fresh final review is still
  required before any push/tag/publication/release action.
- Plans 0020-0022 repaired and live-validated the Reddit browser relevance
  gate: 7/7 accepted posts were manually relevant, multiword partials were
  rejected, all four calls stayed under 55 seconds, and browser cleanup passed.
  This proves the adapter candidate, not timer-owned durable publication.
- The configured browser-method campaign is complete at C37. X topic and
  LinkedIn topic/profile published through exact `agent_browser` provenance;
  YouTube `yt_dlp` and Reddit keyless are accepted production methods;
  Facebook and Reddit browser are transport-ready but quality-rejected.
- Agent-browser commit `11a276fb` is installed and executable-converged. Its
  duplicate-profile-pressure warning is not readiness-impacting and does not
  authorize cleanup of unrelated default or LitScout sessions.
- Version 17's first live gate published 10 items across four lanes; Reddit
  failed before source execution under superseded service 0.2.21. After the
  version-18 observability successor, C42 live-proved that 0.2.22 child-boundary
  repair on service 0.2.24: one keyless attempt, six governed requests, a
  complete immutable zero-yield receipt, and unchanged 59/59 corpus/index
  state. Recurring production collection is not authorized, and no
  specification is enabled.
- The C42 recurring-gate assessment failed closed: the four yielding version-17
  receipts predate the version-18 observability contract, and the separately
  authorized Reddit successor makes six consumed manual attempts. Version 19
  therefore requires four fresh disabled observability proofs and explicitly
  rebaselines cumulative ceilings before recurring enablement can be
  reconsidered.
- Version 19 consumed only its YouTube proof before stopping globally. The
  bounded run succeeded with three deduplicated items and complete
  observability, but updating mutable legacy chunk embeddings cascaded deletion
  into the previously published immutable index. X and both LinkedIn proofs
  were not run. Version 20 repairs index immutability without source traffic
  and stops before any replacement proof. C46 accepted the independently
  reviewed repair: current publication is complete at 59/59 while the two
  damaged 56-row historical indexes remain unchanged as defect evidence.
- Version 21 is the operator-approved, independently reviewed-before-live
  replacement-YouTube successor. It authorizes one distinct disabled proof at
  the unconsumed `2026-08-02T12:00:00Z` cadence boundary, one attempt, no retry,
  and no X, LinkedIn, or recurring work.

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

Checkpoint P0018-C50 is the current authority. Service architecture, timer
ownership, and durable publication/indexing are accepted foundations. The
version-18 observability successor and the separately authorized fresh Reddit
proof are complete. The five specifications remain disabled, the Reddit proof
was healthy zero-yield rather than content yield, and the first recurring-gate
assessment failed closed. Version 19 terminated at its global integrity stop
after one YouTube attempt. Version 20 is complete. The operator's 2026-08-02
approval and independent plan review authorized one Version 21 proof. That
identity consumed one attempt and stopped globally because three new current
YouTube versions lack version embeddings. Every pre-existing index remained
byte-identical. Independent review accepted the failed-closed receipt. C50 is
`replacement_youtube_proof_failed_closed`; installed service 0.2.25 remains
process-ready on schema 12 but version-embedding
completeness is 56/59. X, LinkedIn,
recurring enablement, independent final review, push, tagging, publication,
and release remain closed.

The operator's later 2026-07-31 instruction to continue through the remaining
configured services, explicitly including X, Facebook, and LinkedIn,
satisfies the live and authenticated packet gates for AM02-AM06. Execution
remains serial and bounded by C28: one interval per case, one implementation
attempt and one review/rework cycle per packet, no credential addition or
export, and no account mutation, push, review bypass, tag, publication, or
release.

The operator's 2026-07-31 request to develop an agent-browser-powered Reddit
post routine authorizes the bounded C22 development packet below. It does not
authorize another collection interval, installation, service restart,
credential addition, evaluator run, tag, or release.

The operator's later 2026-07-31 instruction authorizes the bounded C24 packet:
make the service source catalog and per-source access/fallback order user-scope
configuration, build the resulting successor service, perform one managed
upgrade/restart, and run one timer-owned public Reddit proof. This authority
does not add a credential, private source, paid/model call, second interval,
push, independent acceptance bypass, tag, publication, or release.

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

The definition of done does not require every optional access method to pass a
live canary. The installed service foundation must remain truthful when an
individual method is unaccepted, unavailable, degraded, or disabled; method
acceptance is tracked independently by the C28 matrix.

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

### Execution Packet P0018-C24 | 2026-07-31

Plan version:

- 6

Bounded outcome:

- replace the daemon's hard-coded default polling catalog and Reddit-specific
  fallback selection with one strict user-scope source-policy contract;
- build the resulting successor service, install it through the managed
  release transaction, and run exactly one timer-owned public Reddit interval
  with assessment disabled;
- accept the packet only if the timer publishes at least one durable item and
  advances documents/version/index without an agent orchestrating acquisition.

Changed assumption:

- Reddit is one source in a multi-source service; proving its adapter does not
  justify a source-specific control-plane exception;
- the effective polled source set and every currently supported service access
  method/order must be derived from `~/.config/last30days/.env` (or
  `LAST30DAYS_CONFIG_DIR`) with safe defaults, strict validation, and truthful
  readiness diagnostics.

Owned write surfaces:

- one shared service-source policy module plus the runtime and isolated worker
  seams that consume it;
- focused service runtime/worker/config tests;
- `service/VERSION`, runtime manifest, unreleased changelog, and
  `CONFIGURATION.md`;
- Plan 0018, `ROADMAP.md`, `RUNBOOK.md`, and bounded transition/live receipts;
- the user-scoped last30days `.env`, managed release symlinks/unit, and one
  existing-or-successor public Reddit collection specification.

Configuration contract:

- `LAST30DAYS_SERVICE_SOURCES` is the ordered, comma-separated enabled service
  source catalog;
- `LAST30DAYS_<SOURCE>_ACCESS_ORDER` is the ordered, comma-separated access
  chain for each enabled source;
- supported initial methods are Reddit `keyless`, `agent_browser`, and
  `scrapecreators`; X/Facebook/LinkedIn `agent_browser`; and YouTube `yt_dlp`;
- unknown sources/methods, duplicates, empty enabled-source method chains, and
  methods assigned to the wrong source fail closed without exposing secrets;
- existing per-method credentials, profile/build/session, timeout, and browser
  settings remain user-scope inputs; runtime leases remain non-config state;
- defaults preserve current behavior, while the live packet explicitly sets
  all five current service sources and excludes paid Reddit fallback.

Implementation and validation bounds:

- one implementation pass and one remediation pass;
- active-agent concurrency one; `not_spawned` because runtime, worker,
  packaging, config docs, and live transition form one critical path;
- targeted policy/runtime/worker/package/lifecycle tests, complete deterministic
  pytest, reproducible artifact, planning audit, and clean diff before install;
- reserve service 0.2.14 because the configuration contract is consumer- and
  operator-visible beyond the already-built uninstalled 0.2.13 candidate;
- no schema migration; schema 12 remains the rollback boundary.

Live transition packet:

1. record current unit, release links, service-info, database integrity,
   document/version/index counts, collection state, agent-browser doctors,
   access plan, selected profile lease state, and redacted config keys;
2. commit the reviewed 0.2.14 source/artifact/transition receipt before runtime
   mutation;
3. update the user `.env` atomically with explicit five-source policy and
   Reddit `keyless,agent_browser`, preserving secrets and mode 0600;
4. install/restart 0.2.14 through `service/scripts/install.sh`; require exact
   version/manifest/contract/schema readiness and 0.2.12 rollback availability;
5. create or revise one disabled public/default-profile Reddit topic spec with
   three-item, 120-second, 50-request, 100-cent outer bounds and assessment
   disabled; enable it for exactly one timer-owned interval, then pause it;
6. require one terminal run/attempt, zero model calls, browser fallback proof,
   at least one durable item and document/version, and active-index advance;
7. close only the plan-owned browser lane and verify route readiness.

Hard stops and rollback:

- stop before install on source-policy ambiguity, validation failure, artifact
  drift, dirty worktree, config mode/parse failure, route/profile conflict, or
  service 0.2.14 readiness mismatch;
- restore the pre-edit user config and roll back to 0.2.12 on transition or
  readiness failure;
- after a successful transition, stop and preserve 0.2.14 on acquisition
  timeout, typed adapter failure, zero yield, publication/index non-advance, or
  cleanup failure; do not spend a second interval;
- no credential addition, authenticated/private Reddit access, paid fallback,
  App Intelligence/model work, push, tag, publication, or release.

Authority classification:

- `human_gate` satisfied by the operator's instruction to do the managed
  transition now while making all service polling/access policy user-config
  driven;
- independent final review and immutable release remain separate gates.

Terminal condition:

- close with source-policy and live durable-yield acceptance plus verified
  rollback posture, or checkpoint the first hard stop with unused authority
  expired and production truth preserved.

### Checkpoint P0018-C25 | 2026-07-31

Plan version:

- 6

State transition:

- `browser adapter validated -> user-configured timed-service packet ready`

Progress classification:

- `outcome_progress`

Validation evidence:

- Plan 0022 passed four current public Reddit queries with 7/7 manual relevance,
  9 partial-query rejections, 67.291-second minimum start spacing, 54.304-second
  maximum adapter duration, and complete named-lane cleanup;
- current installed service remains ready at 0.2.12/schema 12 with 50 documents
  and active index `index-4f096317e15c57da386466f2`;
- structural review found collection specs already select a source and profile,
  but `build_acquisition_runtime()` still defaults from `SOURCE_ADAPTERS` and
  `_reddit_adapter()` embeds its fallback sequence;
- the worktree was clean before this planning packet.

Subagent status and reconciliation:

- `not_spawned`; concurrency remains one.

Graphiti write status:

- pending the implementation/live outcome checkpoint.

Authority classification:

- `human_gate`; the operator satisfied this gate for C24 in the current
  session.

Next action:

- implement and validate the shared user-scope source-policy contract; do not
  mutate user config or installed runtime until its reviewed commit exists.

### Checkpoint P0018-C26 | 2026-07-31

Plan version:

- 6

State transition:

- `C24 implementation planned -> 0.2.14 source and artifact validated`

Progress classification:

- `outcome_progress`

Validation evidence:

- the shared policy strictly resolves the ordered enabled-source catalog and
  per-source access chains, and the runtime readiness catalog and isolated
  worker both consume that policy;
- explicit access chains do not append hidden methods; legacy behavior remains
  compatible only when the new policy variables are absent;
- focused policy/runtime/worker/package/version tests pass, followed by the
  complete deterministic pytest suite;
- two service builds produced byte-identical 0.2.14 artifact SHA-256
  `1b29209a31dc5e303bed56d2712d92d4a63d1db6c6b1f425ce32afa4e6de85a5`;
- `CONFIGURATION.md`, the unreleased changelog, version, and canonical runtime
  manifest describe and bind the new contract; schema remains 12.

Subagent status and reconciliation:

- `not_spawned`; concurrency remains one.

Graphiti write status:

- pending the live runtime outcome checkpoint.

Authority classification:

- `human_gate`; the operator-approved live packet remains active, and this
  checkpoint is its required source-validation predecessor.

Next action:

- commit the reviewed 0.2.14 source and evidence, then perform the redacted
  preflight before any user-config or installed-runtime mutation.

### Checkpoint P0018-C27 | 2026-07-31

Plan version:

- 6

State transition:

- `0.2.14 source validated -> configured timed acquisition passed with fallback not exercised`

Progress classification:

- `outcome_progress`

Validation evidence:

- managed upgrade installed ready service 0.2.14 on schema 12 with verified
  0.2.12 rollback and explicit five-source user policy;
- the sole timer-owned spec-version-3 interval published one public Reddit
  item with one attempt, one observation, one stored item, zero actual source
  cost, and zero service model calls;
- document versions advanced `57 -> 58`; active index advanced from
  `index-4f096317e15c57da386466f2` to
  `index-90a8aea59d32c62f3df8bbee`; integrity remained `ok`;
- paused spec version 4 remained disabled with no run growth after the
  post-pause observation window;
- the acquisition envelope had empty diagnostics because `keyless` returned
  the item before `agent_browser`; therefore the interval did not prove the
  fallback despite proving configured timed service acquisition;
- durable receipt:
  `docs/dev/notes/0023-configured-timed-acquisition-receipt.json`.

Hard stop:

- do not run a second interval under C24; preserve healthy 0.2.14 and its
  user-scoped policy;
- agent-browser fallback-specific timer acceptance remains open and requires a
  newly authorized interval or a revised acceptance method that cannot be
  satisfied by the first access method.

Subagent status and reconciliation:

- `not_spawned`; concurrency remained one.

Graphiti write status:

- completed as episode `0056b5a0-1f92-4df1-8382-caae6be51d26` from job
  `f25211c4-b2d4-469a-989f-1b4c315b5e05` in group `last30days_skill`.

Authority classification:

- `human_gate`; the C24 one-interval authority is consumed.

Next action:

- revisit Plan 0018 acceptance design with the operator; do not retry, push,
  tag, publish, or release under this packet.

### Execution Packet P0018-C28 | Independent Access-Method Acceptance

Plan version:

- 7

Bounded outcome:

- accept service-first architecture, timer ownership, durable publication and
  indexing, and rollback as completed Plan 0018 foundations;
- validate each configured source/access-method pair through its own bounded
  packet without creating a global all-method join gate;
- preserve truthful per-method `accepted`, `unaccepted`, `unavailable`,
  `degraded`, or `disabled` state while the service remains operable.

Machine-readable authority:

- `docs/dev/notes/0024-service-access-method-acceptance-matrix.json`;
- the matrix is exhaustive for the effective configured policy at C28:
  Reddit `keyless,agent_browser`; X/Facebook/LinkedIn `agent_browser`; YouTube
  `yt_dlp`;
- Reddit `scrapecreators` is supported but not configured and therefore is not
  a required packet. Enabling it creates a new paid credential/cost-class
  human gate and a successor packet.

Shared controller and invariants:

- the primary agent is the sole critical-path controller; active-agent
  concurrency is one because every live packet mutates the same user config,
  service database, scheduler, and source/profile leases;
- each live case permits one interval, one started acquisition attempt, one
  implementation attempt, and one review/remediation cycle;
- every case uses a distinct disabled specification or a reviewed successor,
  assessment disabled, three-item/120-second/50-request bounds, immediate
  pause after the sole terminal run, and a post-pause quiescence readback;
- before mutation, record service/version/schema/index, database integrity,
  spec/run/model-call counts, effective access order, config mode, source-tool
  readiness, and profile/route/lease state where applicable;
- after mutation, require exact method-attempt evidence from the acquisition
  envelope, terminal run/attempt receipts, durable items/versions/index effect
  when yield exists, unchanged service-model-call count, integrity `ok`, and
  restored user policy;
- a packet failure is terminal for that packet instance. It cannot erase C27's
  accepted service/timer foundation or block unrelated packets unless it proves
  a shared scheduler, database, publication, rollback, or policy regression;
- no packet authorizes push, independent acceptance bypass, tag, publication,
  release, credential addition, private-data expansion, or paid access.

#### P0018-AM01 | Reddit keyless | ACCEPTED

- evidence: C27 run `collection-run-564219083f18bc982339e87913775df8`
  attempted, observed, and stored one public item at zero actual source cost;
- document versions and the active index advanced; the spec was paused with no
  post-pause run growth;
- no further keyless acceptance interval is required.

#### P0018-AM02 | Reddit agent-browser first | READY, LIVE GATE

- temporarily set the effective Reddit order to
  `agent_browser,keyless`, preserving and restoring the reviewed user config;
- run one public/default-profile topic interval under the shared bounds;
- accept the method only when diagnostics prove `agent_browser` was attempted
  first, its typed quality-gated result supplied at least one stored item, and
  the related browser tab, profile lease, display allocation, and route are
  closed or released afterward;
- if agent-browser returns a typed empty/failure and keyless later publishes,
  preserve the service result but mark AM02 rejected; fallback success is not
  browser-method acceptance;
- preflight uses agent-browser install doctor, remote-view doctor, exact
  service access plan, browser-capability preflight when recommended, and
  selected-profile lease/readiness. Retained freshness is not live auth proof,
  though this case remains public and requires no Reddit login;
- authority: human gate before the live user-config mutation and interval.

#### P0018-AM03 | X agent-browser | PLANNED, AUTHENTICATED GATE

- exact order `agent_browser`; one authenticated-redaction topic/account case
  using the broker-selected named profile;
- require current access-plan, target freshness or bounded auth probe, no lease
  conflict, exact browser-method diagnostics, canonical X item identity, and
  durable partition-correct publication;
- authority: human gate for authenticated collection; no cookie/token export or
  new credential is permitted.

#### P0018-AM04 | Facebook agent-browser | PLANNED, AUTHENTICATED GATE

- exact order `agent_browser`; one authenticated-redaction topic/account case
  using the broker-selected named profile;
- require current access-plan, target freshness or bounded auth probe, no lease
  conflict, exact browser-method diagnostics, canonical Facebook item
  identity, and durable partition-correct publication;
- authority: human gate for authenticated collection; no message, friend,
  group-join, reaction, or other account mutation is permitted.

#### P0018-AM05 | LinkedIn agent-browser | PLANNED, AUTHENTICATED GATE

- exact order `agent_browser`; two cases because one method serves distinct
  adapter contracts: one topic/account surface and one exact canonical public
  company-or-person profile URL;
- each case has its own one-interval ceiling and receipt. A case result does not
  substitute for the other;
- require current access-plan/auth proof, no lease conflict, exact method and
  adapter-variant evidence, partition-correct durable publication, and
  `not_observed` semantics for hidden/missing profile sections;
- authority: human gate for authenticated collection; no messages,
  connections, invitations, applications, or account mutation.

#### P0018-AM06 | YouTube yt-dlp | PLANNED, PUBLIC

- exact order `yt_dlp`; one public topic/channel case after proving `yt-dlp` is
  on the service subprocess PATH;
- require exact method diagnostics, canonical video identity, freshness bounds,
  durable publication/index effect when yield exists, and no browser/profile
  activity;
- authority: inherited for one bounded public interval after the read-only
  preflight; stop if the binary is absent or off PATH.

Packet dependency and execution order:

1. AM02 first, because it closes the only method-specific gap exposed by C27;
2. AM06 next as the remaining public no-credential method;
3. AM03, AM04, and AM05 only after their separate authenticated human gates;
4. no join across AM02-AM06 is required for architecture acceptance, a fresh
   independent Plan 0018 review, or truthful release readiness.

### Checkpoint P0018-C28 | 2026-07-31

Plan version:

- 7

State transition:

- `configured timed acquisition passed with fallback not exercised -> service foundation accepted and method matrix active`

Progress classification:

- `outcome_progress`

Validation evidence:

- installed service 0.2.14 remains ready on schema 12 with five configured,
  acquisition-ready sources and active index
  `index-90a8aea59d32c62f3df8bbee`;
- all collection specifications remain disabled after C27;
- current source policy defines exactly six configured source/method pairs;
  ScrapeCreators is supported but absent from the effective Reddit order;
- C27 is sufficient direct evidence for Reddit keyless plus the shared
  scheduler/publication/index foundation; earlier Plans 0021-0022 remain
  adapter-only evidence for the Reddit browser implementation;
- the C28 matrix defines independent gates, bounds, evidence, failure effects,
  and an ordered next packet for every configured method.

Subagent status and reconciliation:

- `not_spawned`; active-agent concurrency remains one because live packets
  share user config, service state, and profile/route leases.

Graphiti write status:

- `timed_out` after one bounded attempt: job
  `247244d6-6162-4247-b7ea-daae687ce459` in group
  `last30days_skill_main` reached the 60-second processing limit before an
  episode UUID was assigned; no retry was attempted.

Authority classification:

- `human_gate`; the operator explicitly directed acceptance of the service
  foundation and creation of independent access-method packets. Live AM02 and
  authenticated method execution retain their packet-specific gates.

Next action:

- validate and commit Plan 0018 version 7 and the C28 matrix; then stop before
  AM02's user-config mutation and one timer interval unless the operator
  separately authorizes live execution.

### Checkpoint P0018-C29 | 2026-07-31

Plan version:

- 8

State transition:

- `method packets gated -> AM02-AM06 authorized for serial live execution`

Progress classification:

- `authority_progress`

Authority and bounds:

- the operator explicitly authorized continuation through the remaining
  configured services, including authenticated X, Facebook, and LinkedIn;
- C28's one-interval-per-case, one implementation attempt, one review/rework
  cycle, serial execution, cost, cleanup, and exact-provenance bounds remained
  unchanged;
- credential addition/export, account mutation, push, review bypass, tag,
  publication, and release remained prohibited.

Validation evidence:

- installed service 0.2.14/schema 12 was ready with all campaign specs absent
  or disabled before mutation;
- CodeGraph identified exact adapter variants for X, Facebook, both LinkedIn
  surfaces, and YouTube, while Reddit aggregate diagnostics required explicit
  ordered-method provenance before AM02 could be adjudicated.

Subagent status and reconciliation:

- `not_spawned`; the shared config, service state, and browser route/profile
  leases required a single serial controller.

Graphiti write status:

- deferred to the campaign checkpoint.

Next action:

- add exact access-method provenance, install the validated successor service,
  and execute AM02-AM06 serially in the C28 matrix order.

### Checkpoint P0018-C30 | 2026-07-31

Plan version:

- 9

State transition:

- `AM02-AM06 authorized -> YouTube accepted, browser methods rejected, live browser successor gate failed`

Progress classification:

- `outcome_progress_with_runtime_hard_stop`

Implementation and live evidence:

- commits `b46d5c5` and `b560ca0` added exact adapter/access-method provenance
  and corrected manual collection jobs to one attempt while timer jobs retain
  the existing two-attempt retry policy;
- installed service 0.2.16/schema 12 is ready with verified 0.2.15 rollback,
  integrity `ok`, zero service model calls, all collection specs disabled, and
  the user access orders restored;
- AM06 accepted: `youtube_ytdlp` attempted and selected `yt_dlp`, observed and
  stored three canonical videos at zero source cost, advanced document counts
  `50 -> 53`, version counts `58 -> 61`, and active index
  `index-90a8aea59d32c62f3df8bbee -> index-0b31b594c3222cb1fa8f6175`;
- AM02 rejected before acquisition because its zero-cent packet could not
  reserve the Reddit adapter's one-cent worst-case budget; neither browser nor
  keyless fallback was attempted;
- AM03, AM04, and both AM05 cases rejected on agent-browser remote-view-open
  timeout/CDP-disconnect failures. AM03 exposed the shared manual retry defect
  by starting two acquisitions against a declared ceiling of one; service
  0.2.16 repairs that controller defect for all future manual packets;
- agent-browser advanced from 0.27.0 to source-free 0.28.0, its workstation
  payload now matches provenance, and both static doctors report ready;
- the required live `remote-view-open` gate nevertheless failed twice because
  retained browser and route/display ownership diverged. The one permitted
  `service_remote_view_browser_reattach` remediation returned `reattached`, but
  the second live gate again reported `reattachable_stale_route` with the
  retained browser degraded;
- no browser successor collection interval was created or started. Exact
  packet, job, acquisition, provenance, and live-gate evidence is preserved in
  `docs/dev/notes/0025-service-access-method-live-campaign-receipt.json`.

Hard stop:

- do not start a successor AM02, AM03, AM04, or AM05 interval while the live
  remote-view-open gate fails, even though static doctors report ready;
- repair or retire the degraded retained agent-browser lane under a separately
  reviewed successor, then require one passing live gate before constructing
  any source successor packet;
- no push, independent-review bypass, tag, publication, or release is
  authorized.

Subagent status and reconciliation:

- `not_spawned`; execution remained serial on shared runtime state.

Graphiti write status:

- `timed_out` after one bounded 60-second attempt during node extraction: job
  `b5d0f937-f902-4957-a26f-414f9934d363` in group
  `last30days_skill_main`; no episode UUID was assigned and no retry was made.

Authority classification:

- `inherited_authority`; the source campaign goal remains active, but the
  runtime packet is at a hard stop because this attempt and its one remediation
  cycle are consumed.

Next action:

- create a bounded agent-browser runtime successor that repairs or retires the
  degraded `last30days-facebook` retained lane, prove
  `pnpm test:remote-view-open-live`, and only then revisit one-interval source
  successors for the rejected browser methods.

### Checkpoint P0018-C31 | 2026-07-31

Plan version:

- 10

State transition:

- `browser successor blocked -> live gate accepted and AM02-AM05 successors ready`

Progress classification:

- `blocker_reduction`

Current evidence:

- agent-browser commit `662050d7` preserves route-owned stream attribution,
  exact service-tab-handle readback, and browser/session/target/profile routing;
- focused client, generated-type, route-confusion, release-fixture, syntax, and
  diff checks pass;
- the one live `pnpm test:remote-view-open-live` rerun passed at artifact
  `/tmp/agent-browser-remote-view-open-live-2026-07-31T23-12-57-008Z`, reading
  `https://www.linkedin.com/` and `LinkedIn: Log In or Sign Up` from the exact
  returned target, with one matching intent tab and cleanup;
- installed last30days service 0.2.16/schema 12 remains ready, all collection
  specs remain disabled, the index remains
  `index-0b31b594c3222cb1fa8f6175`, and user access orders remain restored.

Successor packets and bounds:

- create fresh successor spec IDs; do not reuse failed run identities;
- execute serially in order: Reddit browser, X, Facebook, LinkedIn topic,
  LinkedIn canonical profile;
- each case permits one manual timer-owned interval, one acquisition attempt,
  three items, 120 seconds wall time, 50 network requests, assessment disabled,
  immediate pause, and post-pause quiescence;
- Reddit temporarily uses ordered access `agent_browser,keyless` and a
  100-cent reservation ceiling so the configured first method can actually be
  attempted; restore `keyless,agent_browser` after its case;
- authenticated sources retain `agent_browser` as their sole configured method;
- accept or reject each method independently from exact adapter variant,
  attempted/selected access method, canonical evidence, durable publication,
  and cleanup facts.

Hard stops:

- stop the individual case after its single terminal interval; do not retry a
  failed source case inside C31;
- stop the campaign on cleanup failure, service integrity failure, an
  unexpected credential/account mutation request, or loss of exact method
  provenance;
- no push, independent-review bypass, tag, publication, or release is
  authorized.

Subagent status and reconciliation:

- `not_spawned`; Plan 0018 fixes active-agent concurrency at one and these
  packets share user config, service state, and browser profile/route leases.

Authority classification:

- `inherited_authority`; the repaired live gate satisfies C30's named
  prerequisite, while the operator's existing authorization and C28 ceilings
  continue to cover the source successors.

Next action:

- create and execute the five fresh successor cases serially, restore config,
  persist a machine-readable receipt, and adjudicate each method independently.

### Checkpoint P0018-C32 | 2026-07-31

Plan version:

- 11

State transition:

- `C31 source intervals consumed -> common CLI timeout defect isolated and changed-input successors bounded`

Progress classification:

- `blocker_isolation`

Consumed C31 evidence:

- Reddit published three canonical items through `reddit_api` after exact
  attempted order `agent_browser,keyless` selected `keyless`; browser remains
  rejected independently while the configured fallback chain is accepted;
- X, Facebook, LinkedIn topic, and LinkedIn profile each consumed one attempt
  and failed with `agent_browser_error`;
- agent-browser service evidence shows every browser case launched Chromium
  and opened its requested service URL, then `remote_view_open` terminated at
  approximately 15 seconds and cleanup closed the browser;
- the passing standalone live gate supplied `jobTimeoutMs=300000` through the
  typed client, while the user-facing `remote-view open` CLI exposes no
  equivalent and last30days invokes that CLI;
- user Reddit order is restored to `keyless,agent_browser`, all successor specs
  remain disabled, and no retry is authorized under C31.

Changed-input successor bounds:

- implement agent-browser Plan 0086's CLI exposure of the existing per-request
  timeout contract and wire the last30 browser adapter from user-scoped config;
- one implementation pass and one review/rework cycle across both repos;
- validate the installed CLI before source work;
- after validation, create fresh IDs and execute one serial interval each for
  X, Facebook, LinkedIn topic, and LinkedIn profile with the existing C31 item,
  wall, network, assessment, cleanup, and provenance bounds;
- Reddit browser may receive one fresh browser-only interval only after the
  common timeout repair is proven; preserve its normal user fallback order
  outside that interval;
- stop an individual case after one terminal attempt and classify any distinct
  authentication or extraction result independently.

Hard stops:

- no reuse of C31 run, job, acquisition, or spec identities;
- no credential addition/export, account mutation, push, independent-review
  bypass, release, publication, or tag;
- stop on failed install/runtime convergence, cleanup failure, service
  integrity failure, or loss of exact access-method provenance.

Authority classification:

- `inherited_authority`; C31 completed its allowed attempts, and the common
  per-job timeout is a newly isolated input covered by the operator's standing
  direction to continue through configured services.

Next action:

- complete agent-browser Plan 0086, wire the last30 user-scoped timeout knob,
  validate both repos, and execute the fresh serial source successors.

### Checkpoint P0018-C33 | 2026-07-31

Plan version:

- 12

State transition:

- `per-job timeout installed -> inner target-creation timeout isolated`

Progress classification:

- `blocker_isolation`

Evidence and consumed work:

- service 0.2.17 is installed and ready with user-scoped
  `LAST30DAYS_AGENT_BROWSER_JOB_TIMEOUT_MS=90000`;
- the Reddit browser-only and LinkedIn topic C32 successors each consumed one
  attempt and remained rejected;
- agent-browser job evidence records `timeoutMs=90000`, proving the CLI/config
  repair reached the control plane, while each action still failed after about
  15 seconds;
- both failed actions launched the intended profile/browser and recorded the
  intended site tab before cleanup;
- the remaining X, Facebook, and LinkedIn profile C32 cases were not started,
  avoiding repeated attempts against the same unresolved inner failure.

Changed-input successor:

- agent-browser Plan 0087 creates and attaches a blank target before using the
  existing no-wait destination navigation and target-bound proof path;
- after its focused installed gate passes, create fresh source identities for
  Reddit browser, LinkedIn topic, X, Facebook, and LinkedIn profile, preserving
  C32's one-attempt, item, wall, network, assessment, cleanup, and provenance
  limits;
- preserve Reddit's normal `keyless,agent_browser` user order outside its one
  browser-only interval.

Authority classification:

- `inherited_authority`; this is a distinct inner target-acquisition defect,
  and the operator's configured-services objective remains unchanged.

Next action:

- complete Plan 0087 and run only fresh, changed-input source successors.

### Checkpoint P0018-C34 | 2026-07-31

Plan version:

- 13

State transition:

- `blank-target acquisition accepted -> source lane identity mismatch isolated`

Progress classification:

- `blocker_isolation`

Evidence:

- installed agent-browser hash
  `fb4d62ade6670a4dcf646fc112dc5135d41286f80d7eb2e14400e1db260826ff`
  is converged and passed the exact LinkedIn feed gate in 5.62 seconds with
  blank-target creation, destination readiness, and operator-visible readiness;
- the fresh LinkedIn topic source case then recorded `about:blank` followed by
  the exact feed URL, proving Plan 0087 reached the live source path, but failed
  during later remote-view finalization;
- that source path launched session `default--last30days-facebook`, while the
  passing gate used the durable `last30days-facebook` session;
- no X, Facebook, LinkedIn profile, or Reddit post-Plan-0087 interval has run.

Changed input and bounds:

- explicitly bind X, Facebook, and LinkedIn profile/session selection to
  `last30days-facebook` in the user-scoped config while retaining independent
  source access orders;
- restart service 0.2.17, create one fresh LinkedIn topic identity, and consume
  one attempt under the existing C33 ceilings;
- on acceptance or a distinct post-routing result, adjudicate remaining source
  cases independently; do not reuse consumed identities.

Authority classification:

- `inherited_authority`; this changes only stable user-scoped routing policy
  and preserves the configured-services objective, credentials, and accounts.

Next action:

- run the fresh LinkedIn topic routing successor, then classify the remaining
  source packets from its exact terminal evidence.

### Checkpoint P0018-C35 | 2026-07-31

Plan version:

- 14

State transition:

- `durable session proven -> hard-coded shared-display divergence isolated`

Progress classification:

- `blocker_isolation`

Evidence and successor:

- the C34 LinkedIn topic case used exact durable session
  `last30days-facebook`, created a blank target, navigated to the feed, and
  still failed during remote-view finalization;
- the passing Plan 0087 gate used agent-browser's private-display default,
  whereas Reddit, X, Facebook, and LinkedIn encode display policy inside their
  adapters;
- service 0.2.18 makes display isolation a shared user-scoped browser policy,
  preserving each source's prior default when unset;
- this workstation selects `private_virtual_display`; one fresh LinkedIn topic
  attempt may adjudicate the changed route/display policy before other sources.

Authority classification:

- `inherited_authority`; the change moves a transport choice into the
  user-scoped policy requested by the operator and does not mutate credentials
  or accounts.

Next action:

- validate/install 0.2.18 and execute one fresh LinkedIn topic successor.

### Checkpoint P0018-C36 | 2026-07-31

Plan version:

- 15

State transition:

- `private display applied -> redundant active-target activation isolated`

Progress classification:

- `blocker_isolation`

Evidence and successor:

- service 0.2.18 applied private-display policy and the fresh LinkedIn topic
  target reached exact URL `https://www.linkedin.com/feed/` with title
  `Feed | LinkedIn`;
- remote-view still failed before final proof, and reconciliation recorded
  target discovery degraded during rollback;
- Plan 0088 removes only the redundant target activation when the exact target
  is already active, while retaining real switch behavior and all proof gates;
- no further source interval is authorized until its installed LinkedIn feed
  gate passes; afterward use fresh identities under the existing ceilings.

Authority classification:

- `inherited_authority`; the defect is a distinct exact-target readback issue
  within the already authorized browser transport repair.

Next action:

- complete Plan 0088 and rerun the no-collection LinkedIn feed gate.

### Checkpoint P0018-C37 | 2026-08-01

Plan version:

- 16

State transition:

- `browser handoff blockers removed -> configured source methods adjudicated`

Progress classification:

- `acceptance_and_limit_isolation`

Accepted evidence:

- agent-browser Plans 0086-0089 are closed at commit `11a276fb`; the installed
  cold LinkedIn feed gate passed exact-target, visible-window, and operator
  route proof in 5.5 seconds;
- installed last30days service 0.2.20/schema 12 is ready with user-scoped
  timeout, display, profile, session, and ordered access-method policy;
- X topic, LinkedIn topic, and LinkedIn profile each published on one attempt
  with exact `agent_browser` selected-method provenance;
- Facebook and Reddit each cleared browser acquisition and authentication but
  failed closed at their content quality gates; neither published;
- Reddit's normal `keyless,agent_browser` order is restored, all campaign
  specs remain disabled, and service model/assessment work remained disabled;
- receipt `docs/dev/notes/0026-configured-browser-service-campaign-receipt.json`
  binds exact runs, jobs, counts, commits, installed versions, and residuals.

Residual limits:

- Facebook's observed cards lacked sufficient author/date/permalink quality
  and included unknown/off-topic shapes;
- Reddit browser found seven candidates, all rejected as off topic; keyless
  remains the production-first method;
- the current agent-browser binary and daemon are converged, while the
  source-free workstation manifest still requires an interactive-sudo refresh;
- no recurring collection was enabled and no push, tag, release, or
  publication authority was inferred.

Authority classification:

- `inherited_authority`; the configured-method campaign objective is complete,
  and source-quality limits are preserved as evidence rather than hidden by
  retries.

Next action:

- revisit the service-first timed-polling product plan using accepted X,
  LinkedIn, YouTube, and Reddit keyless lanes as the initial production set;
  retain Facebook and Reddit browser as observed fallback/diagnostic lanes
  until separate quality improvements pass fresh bounded cases.

## Version 17 | Timed Production Polling Canary Packet

### Stable outcome

Prove that the installed service can run a user-configured, recurring,
timer-owned production canary across the accepted source/method surfaces while
preserving bounded cost, serialized browser ownership, exact provenance,
source-local failure containment, durable no-yield evidence, and reversible
schedule state.

This version is a planning packet only. Its current terminal state is
`awaiting_review`; it does not authorize specification creation, manual source
runs, schedule enablement, or any other live mutation.

### Scope and selector boundary

The canary is limited to five specifications and the selectors already covered
by accepted evidence:

| Lane | Selector/surface | Required production method | Proposed interval | Freshness objective |
| --- | --- | --- | ---: | ---: |
| Reddit topic | `OpenClaw` | `keyless` | 12 hours | terminal receipt within 14 hours |
| YouTube topic | `OpenAI latest` | `yt_dlp` | 12 hours | terminal receipt within 14 hours |
| X topic | `OpenAI` | `agent_browser` | 24 hours | terminal receipt within 26 hours |
| LinkedIn topic | `OpenAI` | `agent_browser` | 24 hours | terminal receipt within 26 hours |
| LinkedIn profile | `https://www.linkedin.com/company/openai/` | `agent_browser` | 24 hours | terminal receipt within 26 hours |

Acceptance of these selectors does not approve arbitrary topics, profiles, or
source-wide content quality. Selector expansion requires a separate bounded
packet and authority classification.

Facebook and Reddit `agent_browser` are excluded from this packet. Reddit may
retain the user order `keyless,agent_browser`, but a production canary result is
publishable only when exact provenance reports `selected_access_method=keyless`.
Selection of `reddit_agent_browser` is a diagnostic terminal result and must
fail closed without publication or weakening the quality gate. If the current
service cannot enforce that per-spec method constraint, the execution packet
must implement and deterministically test the constraint before any live run.

### Per-attempt and cumulative ceilings

Each proposed specification uses:

- `assessment_enabled=false` and `budget_cents=0`;
- `item_limit=3`, `network_request_limit=50`, and
  `wall_timeout_seconds=120`;
- a 24-hour lookback after the initial bounded manual proof;
- existing redaction, retention, profile, and access-order policy only.

The recurring canary lasts 48 hours. Its maximum scheduled attempts are 14:
four each for Reddit and YouTube and two each for X, LinkedIn topic, and
LinkedIn profile. The five pre-enable manual proofs make the packet-wide
maximum 19 acquisition attempts. Manual and scheduled work share cumulative
ceilings of 57 accepted items, 950 network requests, 2,280 wall-clock seconds,
zero assessment/model spend, and one active acquisition at a time. The manual
proofs may consume at most 15 items, 250 requests, and 600 wall-clock seconds;
the scheduled canary may consume the remaining 42 items, 700 requests, and
1,680 seconds. A skipped or overlap-rejected tick consumes its
scheduled-attempt identity and is not replayed automatically.

### Schedule, lease, and attempt policy

- Critical-path owner and timer controller: the primary agent operating the
  installed last30days service; the service remains scheduling authority.
- Active-agent concurrency: one. No subagent may operate the live service,
  user configuration, shared social profile, browser session, or route pool.
- Browser-backed schedules are phase-staggered by at least 20 minutes. Enable
  order, if later authorized, is Reddit, YouTube, X, LinkedIn topic, then
  LinkedIn profile; the last three must never overlap on
  profile/session `last30days-facebook`.
- Before recurring enablement, each newly created disabled specification gets
  at most one manual acquisition attempt. Manual proof identities are distinct
  from historical campaign IDs and from scheduled-attempt identities.
- A lease conflict, already-running specification, or occupied shared profile
  produces a durable skipped/blocked receipt. It must not queue an unbounded
  retry, launch another browser, or steal an unrelated lease.
- Timer retries are disabled for the canary. No failed or skipped attempt is
  retried under the same identity. A changed-input successor requires a durable
  checkpoint and must remain inside the cumulative ceilings.

### Outcome and failure semantics

Service readiness, acquisition transport, content quality, durable
publication, and index projection remain separate judgments:

- `ready=true` proves only acquisition readiness;
- a successful zero-item interval is acceptable only with exact method
  provenance, bounded request/wall evidence, a durable no-yield receipt, and no
  false index-advance claim;
- a non-empty interval is accepted only when all stored items pass the existing
  quality gate, the collection receipt binds observed/stored counts and method
  provenance, and the active index either advances or records a truthful
  no-change/deduplication reason;
- one source's negative yield or quality rejection does not block unrelated
  source lanes;
- two consecutive failed, quality-rejected, provenance-missing, or
  freshness-missed attempts pause only that specification and terminate its
  canary lane;
- two consecutive `accepted_no_yield` results also pause only that lane for
  diagnostic review; they remain truthful no-yield outcomes rather than being
  relabeled as transport or quality failures;
- service integrity failure, database inconsistency, runtime convergence
  failure, ambiguous profile ownership, or inability to disable a schedule
  terminates the entire canary and requires rollback.

No selector widening, access-order mutation, quality-threshold weakening,
credential work, cookie export, account mutation, model assessment, or
Facebook/Reddit-browser repair is allowed to manufacture yield.

### Evidence contract

Every manual or scheduled attempt must preserve a durable collection receipt
binding:

- collection specification ID/version, scheduled/manual attempt identity,
  run ID, job ID, source, surface, and selector digest;
- attempted and selected access method plus concrete adapter variant;
- scheduled, started, terminal, and next-due timestamps;
- item, request, wall-time, and cost usage against ceilings;
- observed, accepted, rejected, stored, deduplicated, and indexed counts;
- pre/post document count, embedding count, and active index version;
- terminal classification: published, accepted_no_yield, quality_rejected,
  method_rejected, skipped_overlap, blocked_lease, failed, or rolled_back.

The 48-hour closeout receipt must reconcile all 14 scheduled identities,
including not-run identities after a lane pauses, without interpreting missing
evidence as success or failure.

### Rollout transitions and gates

| State | Authorized action | Exit condition |
| --- | --- | --- |
| `awaiting_review` | documentation, deterministic tests, read-only live readbacks | one independent review returns no critical finding |
| `awaiting_live_mutation_gate` | no live mutation | explicit operator approval naming disabled-spec creation and five manual proofs |
| `manual_canary` | create five disabled specs and run at most one manual attempt each | all five terminal receipts reconcile; failures stop only their lane unless a global hard stop fires |
| `awaiting_enable_gate` | no schedule enablement | independent receipt review plus explicit operator approval to enable recurring canary schedules |
| `recurring_canary` | phase-staggered enablement within the 48-hour/14-attempt ceiling | all identities terminal, a lane stop fires, or global rollback fires |
| `awaiting_closeout_review` | disable all five specs and reconcile receipt/index state | independent final judgment records accepted, rejected, or blocked outcome |

The manual packet stopped at `manual_canary_blocked`. The first live mutation
gate is consumed; the second live gate is neither ready nor satisfied.
Recurring enablement is prohibited.

### Rollback and hard stops

Rollback means disable all five canary specifications, wait for or reconcile
any already-running bounded job, restore the exact pre-canary user-policy
readback, verify zero enabled specifications, and preserve all receipts and
published evidence. Rollback never deletes collection, run, job, corpus, or
index history.

Stop before live work on any service not ready, runtime not converged,
non-private config mode, pre-existing enabled specification, ambiguous profile
ownership, missing exact provenance, inability to enforce the Reddit-keyless
publication constraint, unavailable rollback, dirty/unowned overlapping
worktree, or changed source/data/credential scope.

### Work units and bounds

1. Review V17 documentation and deterministic audit enforcement. No live
   mutation.
2. After the first explicit human gate, implement any required per-spec method
   constraint, create five disabled specs, and execute five serial manual
   proofs.
3. Review the manual receipt and stop at the enable gate.
4. After the second explicit human gate, enable the phase-staggered 48-hour
   canary, monitor only through service-owned receipts, then disable/reconcile.
5. Run one independent final review and record the Plan 0018 disposition.

Bounds: one implementation attempt and one review/rework cycle per work unit;
one successor packet after a changed-input failure, provided it consumes the
same 19-attempt and resource ceilings; one active acquisition; one durable
checkpoint after each work unit and before either human gate; maximum one
consecutive hardening-only checkpoint. Exhausting a packet-wide ceiling
requires a new human gate. Review failure splits, reframes, or blocks the unit
rather than reopening an unbounded loop.

### Version-17 acceptance and terminal condition

This planning work unit is accepted when Plan 0018, Roadmap P07, the latest
Runbook turn, and the deterministic authority audit agree on version 17/C38;
the packet contains the selector boundary, ceilings, attempt graph, evidence
contract, rollback, and two explicit human gates; current readbacks prove zero
enabled collection specifications; and an independent reviewer reports no
critical finding.

The unit then stops in `awaiting_live_mutation_gate`. Production polling is not
accepted, enabled, or complete merely because this plan is review-ready.

### Checkpoint P0018-C38 | 2026-08-01

Plan version:

- 17

State transition:

- `ready_for_bounded_replan -> awaiting_live_mutation_gate`

Progress classification:

- `outcome_progress`

Authority classification:

- `human_gate`

Owned changes:

- reconciled the Plan 0018 header, Current State, and current-authority
  declaration with installed service 0.2.20 and checkpoint C38;
- defined the plan-only version-17 timed-polling canary, two live-state gates,
  selector boundary, exact-method semantics, packet-wide ceilings, serialized
  schedule/lease policy, outcome classifications, evidence contract, rollback,
  and bounded state transitions;
- strengthened `audit_plan_authority.py` and its focused tests so declared plan
  version and explicit current-checkpoint authority cannot drift from the
  latest checkpoint;
- reconciled Roadmap P07 and the timed-polling handoff's historical Git/audit
  wording; appended Runbook Turn 103 without rewriting prior history.

Validation evidence:

- primary-agent TDD: the two new audit cases failed before implementation and
  passed afterward; seven focused cases passed before authority closeout;
- the strengthened live-repository audit failed closed on the missing C38 with
  exactly the expected version/current-authority findings;
- independent read-only reviewer `/root/v17_independent_review` returned
  `fail` with two bounded findings: missing C38/Runbook wiring and cumulative
  ceilings that did not include five manual proofs;
- the one remediation pass adds this checkpoint/Runbook turn and caps all 19
  manual-plus-scheduled attempts at 57 items, 950 requests, 2,280 wall-clock
  seconds, zero assessment/model spend, and concurrency one;
- final focused tests, authority audit, diff check, and zero-enabled-spec live
  readback are required immediately after this checkpoint is written.

Subagent status and reconciliation:

- `spawned`; `/root/v17_independent_review` ran one fresh-context, read-only
  review with no edits or live mutations and returned terminal verdict `fail`;
  both findings were accepted and addressed in the single bounded remediation
  pass. No second evaluator cycle is authorized.

Remaining acceptance criteria:

- explicit operator approval is required before creating five disabled
  specifications or running any manual source proof;
- after manual receipts reconcile, a second explicit operator approval is
  required before enabling the recurring 48-hour canary;
- production acceptance still requires the executed canary, closeout receipt,
  rollback proof, and one independently reviewed final disposition.

Graphiti write status:

- provider readiness passed, but the one bounded source-backed memory job
  `89c558c6-4456-4fd5-bee2-89ab28717120` timed out after 60 seconds during
  node resolution; no episode UUID was assigned and no retry was made.

Next action:

- stop at `awaiting_live_mutation_gate`. Do not create specifications, run
  acquisitions, enable schedules, or mutate service/browser/user-policy state.

### Checkpoint P0018-C39 | 2026-08-01

Plan version:

- 17

State transition:

- `awaiting_live_mutation_gate -> manual_canary -> manual_canary_blocked`

Progress classification:

- `outcome_progress`

Authority classification:

- `inherited_authority`

Owned changes:

- added backward-compatible `required_access_method` collection constraints,
  exact source/method adapter selection, and method-specific cost reservation;
- built and installed service 0.2.22/schema 12 with rollback retained at
  0.2.20 after the superseded 0.2.21 child-entrypoint failure was repaired;
- regenerated and reinstalled MCP adapter 4.0.1 after full-suite integration
  caught its stale embedded contract digest; client/service compatibility is
  restored without changing the adapter release identity;
- created five fresh version-17 specifications, kept every specification
  disabled, and consumed exactly one serial manual attempt per lane;
- persisted receipt 0027: YouTube, X, LinkedIn topic, and LinkedIn profile
  published 10 total items at zero cost; Reddit failed before source execution
  and was not retried;
- reconciled the independent review failure as a blocked manual canary rather
  than advancing to the enable gate.

Validation evidence:

- 111 relevant service, acquisition, collection, contract, HTTP, runtime,
  version, and package tests passed after the 0.2.22 repair; the focused
  child-boundary regression passed in a 34-test packet;
- the installed service is ready on 0.2.22/schema 12; SQLite `quick_check` is
  `ok`; corpus/index state settled at 59 documents and 59 embeddings;
- 37 specifications exist, including exactly five version-17 canaries, and
  enabled-spec count is zero; user configuration remains mode 0600;
- agent-browser remained executable-converged and reused the retained
  `last30days-facebook` profile without spawning a duplicate browser;
- the initial full suite produced one MCP contract-digest integration failure;
  after regenerating/reinstalling the adapter catalog, the failed integration
  packet and all Go adapter tests passed;
- the final repository suite passed: 2,407 tests, seven skips, and six
  subtests; the authority audit, receipt validation, compilation, and diff
  check also passed;
- `ruff` was unavailable in the repository environment and was not installed.

Independent review and evidence gaps:

- `/root/manual_canary_review` returned terminal `fail` in one read-only pass:
  actual request use, per-run indexed/deduplicated counts and pre/post index
  snapshots are absent; Reddit has no attempted-method provenance because the
  subprocess failed before adapter execution; and repaired 0.2.22 Reddit has
  no live proof;
- receipt 0027 therefore records `enable_gate_ready=false`; the manual-canary
  exit condition was not met and the one-pass review bound requires split,
  reframe, or block rather than another attempt in this packet.

Subagent status and reconciliation:

- `completed`; `/root/manual_canary_review` made no edits or live mutations.
  Its three critical findings were accepted without opening a remediation or
  re-review loop.

Remaining acceptance criteria:

- a bounded successor must add durable actual-request accounting, per-run
  pre/post corpus/index snapshots, and explicit accepted/rejected/stored/
  deduplicated/indexed counts, then obtain authority for one fresh 0.2.22
  Reddit exact-method proof;
- all five manual identities must reconcile before an enablement approval can
  be requested; recurring scheduling, push, tag, publication, and release
  remain prohibited.

Graphiti write status:

- provider readiness passed, but source-backed closeout memory job
  `1a6a8554-6d52-4004-aeb6-cb2803dc2bc4` timed out after 60 seconds during
  node resolution; no episode UUID was assigned and no retry was made.

Next action:

- design a bounded evidence-observability successor packet under standing
  authority. Do not rerun a source attempt or enable any specification until
  that packet classifies and satisfies its live gate.

## Version 18 | Evidence-observability successor

### Bounded outcome

Make one collection run self-reconciling through the existing collection
interface: exact governed source-request usage, observed/accepted/rejected/
stored/deduplicated/indexed counts, exact method provenance, and pre/post
corpus/index snapshots must be durable and returned with the latest run.

This packet may implement, test, build, and install one version-distinct
service successor plus the digest-matched MCP adapter. It may not run a source
acquisition, enable a specification, change a selector/access order/profile,
add credentials, increase any V17 ceiling, push, tag, publish, or release.

### Evidence semantics

- A `network_request_count` is the exact count of governed outbound source
  operations at the adapter seam. Python HTTP calls count individually;
  opaque CLI/browser adapters count one governed top-level source-search
  invocation. Internal browser navigation and asset/subresource traffic outside
  that seam are not represented and are not the unit governed by the ceiling.
- `attempted_count` is the exact number of candidates submitted to the worker
  outcome path. The current worker observes every submitted candidate, so a new
  result binds `attempted_count >= observed_count` and emits equal values;
  legacy results may omit the field rather than receiving an inferred zero.
- `observed_count` is the number of source candidates reported to the worker,
  including adapter-rejected candidates when bounded diagnostics expose them.
- `accepted_count` is the number of items that survive worker normalization
  and the item limit. `rejected_count = observed_count - accepted_count` and
  must never be negative.
- `stored_count` is the number of accepted item sightings durably associated
  with the acquisition. `deduplicated_count` is the accepted count whose
  canonical document already existed. `indexed_count` is the number of those
  accepted items represented in the published immutable index.
- Each run records pre/post document count, embedding count, and active index
  version. Null denotes a legacy run that predates this contract, never zero.
- Attempted/selected access methods and concrete adapter variant are copied
  from the validated worker result into the durable run receipt. Missing new
  evidence fails the live-proof acceptance check rather than being inferred.

### Module and write surfaces

The deep module remains the collection interface. Callers receive a richer
`last_run` receipt from the existing list operation; adapter, publication,
schema, and index mechanics remain implementation details.

Owned write surfaces:

- `service/VERSION`, runtime manifest, and service contract schema;
- acquisition result contract/worker and source adapter wrappers;
- corpus publication statistics, job-runner evidence capture, and schema-12
  immutable observability envelopes surfaced by collection list;
- focused contract, worker, publication, job-runner, collection, migration,
  runtime-package, and MCP compatibility tests;
- `CONFIGURATION.md`, Plan 0018, Roadmap P07, and append-only Runbook.

### Work graph and hard bounds

| Work unit | Dependency | Exit condition |
| --- | --- | --- |
| O01 result accounting | C40 | worker result round-trips exact request and outcome counts; malformed/over-budget evidence fails closed |
| O02 publication/index accounting | O01 | publication and active-index checks produce exact stored/deduplicated/indexed counts |
| O03 durable run receipt | O02 | schema-12 immutable start/final envelopes persist all counts, method provenance, and snapshots; collection list returns the latest receipt |
| O04 packaged runtime | O03 | version-distinct artifact and digest-matched MCP pass install/rollback/readiness checks with zero enabled specs |
| O05 independent review | O04 | one fresh reviewer returns no critical finding or the packet stops split/reframed/blocked |
| G03 Reddit proof gate | O05 | explicit operator approval authorizes exactly one manual run of the existing disabled Reddit spec |

Bounds: one vertical TDD cycle per behavior, one implementation packet, one
independent review, at most one consolidated remediation pass, concurrency
one for runtime mutation, no source attempts, zero source-request usage, zero
assessment/model spend, and rollback to installed service 0.2.22. The fresh
Reddit proof is a later one-attempt/three-item/50-request-unit/120-second/
zero-cost manual packet and is not consumed by this implementation unit.

Delegation decision: critical-path discovery and implementation remain with
the primary agent because the files and schema are tightly coupled. One
fresh-context read-only evaluator is required after deterministic validation;
no parallel implementation lane is authorized.

### Acceptance and terminal state

The implementation packet is accepted only when deterministic tests prove all
new fields through the public collection list interface, legacy rows/results
remain readable, the schema stays at 12 so rollback remains executable, the installed
service/MCP pair is compatible and ready, all specifications remain disabled,
rollback remains available, and one independent review has no critical
finding after at most one remediation pass.

The packet then stops at `awaiting_reddit_proof_gate`. This is not recurring
enablement approval. The later Reddit proof must itself publish a complete
receipt before Plan 0018 can return to enable-gate consideration.

### Checkpoint P0018-C40 | 2026-08-01

Plan version:

- 18

State transition:

- `manual_canary_blocked -> active_implementation`

Progress classification:

- `blocker_reduction`

Authority classification:

- `inherited_authority`

Changed assumption and evidence:

- V17 used `network requests` without naming the governable seam. The opaque
  browser and yt-dlp implementations cannot truthfully expose every internal
  HTTP subrequest; V18 defines and enforces exact governed source operations
  while explicitly excluding unobservable asset/subresource traffic;
- an initial column-migration design was rejected before packaging because a
  schema-13 database would strand the verified 0.2.22 rollback. Versioned
  immutable envelopes provide the same durable receipt without schema drift;
- C39 and receipt 0027 prove the remaining blockers: absent request usage,
  absent exact per-run outcome/index counts and snapshots, and no live 0.2.22
  Reddit exact-method proof.

Owned changes and current evidence:

- plan-only successor definition; repository starts clean at commit
  `a16119e873833056196550c86d0201d3fcfa1b1b`, 39 commits ahead of
  `origin/main`;
- installed service 0.2.22/schema 12 is ready at 59 documents/59 embeddings;
  all 37 specifications, including the five V17 specs, are disabled;
- CodeGraph is healthy with 318 indexed files and identified the worker result,
  corpus publication, job runner, collection persistence, and schema migration
  seams described above.

Subagent status and reconciliation:

- `not_spawned`; discovery/implementation are one tightly coupled critical
  path. A fresh evaluator is reserved for O05.

Graphiti write status:

- deferred to the validated implementation checkpoint; C39's prior write
  timed out and will not be retried as part of planning.

Next action:

- execute O01-O04 with vertical TDD and no live acquisition, then perform the
  one-pass O05 review. Stop before G03.

### Checkpoint P0018-C41 | 2026-08-01

Plan version:

- 18

State transition:

- `active_implementation -> awaiting_reddit_proof_gate`

Progress classification:

- `blocker_reduction`

Authority classification:

- `human_gate`

Changed assumption and evidence:

- the first independent review found that Facebook/LinkedIn aggregate
  `rejected` buckets were being added to their candidate-kind totals and that
  Reddit's opaque browser path did not bind its governed top-level invocation;
- a second bounded review found `attempted_count` still came from optional
  diagnostics and identified the expected stale runtime manifest and authority
  closeout. The single consolidated remediation excludes the aggregate bucket,
  accounts every Reddit browser invocation including failure/fallback, moves
  `attempted_count` into the validated result contract, refreshes the package,
  and reconciles Plan/Roadmap/Runbook authority;
- transparent Reddit keyless and ScrapeCreators HTTP calls remain counted
  individually through the bounded `urllib` seam. Opaque browser/CLI counts are
  explicitly one governed top-level source-search invocation, not raw internal
  navigation or asset traffic.

Owned changes and validation evidence:

- service 0.2.24/schema 12 is installed ready with contract digest
  `3fb7df8ab6d17e1e381090120a7d30c99027cc3d555b1c3bfe7a0eeb84983c6f`
  and runtime-manifest digest
  `667d88dfcc68feb426c322f48a945a1da2a48e29bb4f4009297fc754871179c0`;
- immutable artifact
  `last30days-service-0.2.24.tar.gz` has SHA-256
  `c61e32b95d15a9f4e62a232903982bf32f3c0860e625ee945f9802613dc39042`;
- contract, worker, publication, job-runner, collection, runtime-package,
  release-version, and MCP integration tests pass. The final complete
  repository suite passed 2,414 tests with seven skips and six subtests;
  authority audit, Python compilation, Go tests, and `git diff --check` pass;
- managed rollback 0.2.24 -> 0.2.23 -> 0.2.24 stayed ready on schema 12. The
  earlier 0.2.22 rollback proof and retained release remain valid; no schema
  migration occurred;
- installed corpus/index state remains 59 documents, 59 embeddings, 16
  relationships, and `index-8c968b3c270aa6c2b5abcbac`; SQLite quick check is
  `ok`; all 37 collection specifications remain disabled;
- no source acquisition, assessment/model call, credential change, schedule
  enablement, push, tag, publication, or release occurred.

Subagent status and reconciliation:

- `completed`; the two bounded read-only review outputs were reconciled as one
  consolidated defect set and one remediation pass. The post-remediation
  follow-up returned `PASS` with no remaining critical findings. Candidate
  double-counting, Reddit opaque request accounting, contract-bound attempted
  count, stale package evidence, and authority drift were repaired without
  widening scope.

Graphiti write status:

- provider readiness passed and closeout job
  `5f2842b3-0778-4736-a771-882c559b3f3e` completed in
  `last30days_skill_main` as episode
  `ea56fe0f-5dca-49ba-bfaf-56415a6982d6`; it is not a live-source gate.

Next action:

- stop at G03. Explicit operator approval may authorize exactly one manual run
  of disabled specification `p0018-v17-reddit-keyless-manual` on the 0.2.24
  observability runtime: one attempt, at most three items, at most 50 governed
  request units, at most 120 seconds, and zero cost. Keep the specification
  disabled before and after. Recurring enablement remains unauthorized.

### Checkpoint P0018-C42 | 2026-08-01

Plan version:

- 18

State transition:

- `awaiting_reddit_proof_gate -> reddit_proof_complete -> awaiting_recurring_enable_gate`

Progress classification:

- `outcome_progress`

Authority classification:

- `human_gate`; the Reddit proof gate is consumed, and any recurring
  enablement remains a new human gate

Authority and bounded execution:

- the operator explicitly replied `approved`, authorizing exactly one manual
  run of existing disabled specification
  `p0018-v17-reddit-keyless-manual`;
- a preflight at `2026-08-01T20:14:47Z` cadence-deduplicated to the prior failed
  interval, created no job or source attempt, and consumed zero requests. The
  next unique 12-hour boundary, `2026-08-02T00:00:00Z`, created the sole proof
  run with supervisor `max_attempts=1`;
- no selector, access order, profile, credential, ceiling, schedule-enable
  state, assessment setting, or cost authority changed.

Proof evidence:

- durable receipt `docs/dev/notes/0028-reddit-observability-live-proof.json`
  binds run `collection-run-14988c98b0a5932538dd772c265e58d1`, job
  `b3a63856-b6af-4d3f-aefa-ed649103382d`, and acquisition
  `work-6fcbe254bc0644e1b6c4a4a3af35eebd`;
- service 0.2.24/schema 12 exercised adapter variant `reddit_keyless`, proving
  the constrained child-boundary repair introduced in 0.2.22. It made six of
  50 governed requests, accepted zero of three allowed items, completed in
  2.082 of 120 seconds, spent zero cents, and ran one attempt with no retry;
- exact attempted/observed/accepted/rejected/stored/deduplicated/indexed counts
  are all zero. Attempted method is `keyless`; selected method is truthfully
  null because no candidate yielded. This is healthy zero-yield, not content
  yield and not evidence for arbitrary Reddit selectors;
- immutable attempt-start, acquisition-result, and run-receipt hashes
  recomputed exactly. Public `collection list` returns the complete receipt;
  pre/post snapshots both bind 59 documents, 59 embeddings, and
  `index-8c968b3c270aa6c2b5abcbac`;
- SQLite `quick_check` is `ok`; service remains ready; all 37 specifications,
  including the target, remain disabled.

Independent review:

- `/root/reddit_proof_review` returned `PASS` with no critical findings. It
  confirmed the fresh execution/observability proof is complete, distinguished
  healthy zero-yield from content yield, and preserved recurring enablement as
  a separate human gate.

Graphiti write status:

- provider readiness passed and source-backed closeout job
  `429ae2f9-e63b-422b-98bf-87501a7b134e` was queued in
  `last30days_skill_main` and remained running after its 90-second server-side
  window at the final bounded observation; no retry was made. This asynchronous
  memory status does not weaken the live service receipt.

Next action:

- stop. The observability-successor and fresh Reddit-proof objective is
  complete. Do not run another source attempt or enable any specification.
  Any recurring canary requires a separately reviewed packet and explicit
  operator approval; push, tag, publication, and release remain closed.

## Version 19 | Five-lane evidence-completion successor

### Bounded outcome

Complete the version-18 observability evidence set for the four yielding
version-17 lanes without rerunning Reddit or enabling recurrence. Run exactly
one fresh, serialized, disabled-specification proof for YouTube topic, X topic,
LinkedIn topic, and LinkedIn profile. Each proof must publish the complete
request, outcome, provenance, and pre/post snapshot receipt now proven by C42.

The legacy version-17 attempts remain consumed historical evidence. They are
not rewritten, inferred complete, or retried. The new proofs are distinct
successor identities. This packet may create durable run/job/acquisition,
corpus/index, and receipt state produced by the four existing selectors. It may
not run Reddit, change a selector, method, profile, credential, access order,
quality threshold, assessment setting, or service release; enable any schedule;
push, tag, publish, or release; or touch unrelated browser sessions.

### Authority and cumulative ceilings

The operator's 2026-08-01 `ok go`, given immediately after the failed recurring
gate assessment and its exact successor recommendation, authorizes this
four-proof packet and the following cumulative ceiling rebaseline. Live work
remains conditional on one independent plan review returning no critical
finding after at most one consolidated remediation pass.

The packet accounts for all work conservatively:

| Evidence class | Attempts | Accepted items | Governed requests | Wall seconds |
| --- | ---: | ---: | ---: | ---: |
| five legacy V17 manual identities | 5 | 10 actual | 250 reserved because actual use is unreconcilable | 51.939 actual |
| C42 Reddit observability successor | 1 | 0 actual | 6 actual | 2.082 actual |
| four V19 evidence-completion proofs | 4 | 12 maximum | 200 maximum | 480 maximum |
| later 48-hour recurring canary, still gated | 14 | 42 maximum | 700 maximum | 1,680 maximum |
| rebaselined cumulative envelope | 24 | 64 | 1,156 | 2,280 |

Cost remains zero cents, assessment/model calls remain zero, and active
acquisition concurrency remains one. The wall envelope retains the V17 2,280
second ceiling because the exact legacy and C42 usage plus both future maxima
sum to 2,214.021 seconds. The attempt, item, and request ceilings increase only
to cover the consumed successor and four new proofs while preserving the
planned 14 scheduled identities. A future recurring packet may tighten these
ceilings from exact V19 usage but may not exceed them without another human
gate.

### Proof identities and execution order

Use the existing disabled version-17 specifications without revision:

1. `p0018-v17-youtube-ytdlp-manual` using exact `yt_dlp`;
2. `p0018-v17-x-browser-manual` using exact `agent_browser`;
3. `p0018-v17-linkedin-topic-browser-manual` using exact `agent_browser`;
4. `p0018-v17-linkedin-profile-browser-manual` using exact `agent_browser`.

Select one fresh cadence boundary per specification that cannot deduplicate to
an existing run. Before each submission, re-read the latest run and enabled
state. Set supervisor `max_attempts=1`; do not retry or replay a failed,
deduplicated, skipped, or incomplete identity. Keep every specification
disabled before and after its proof. Browser-backed work is serialized on
`last30days-facebook`; confirm the prior lease is released before advancing.
No subagent may operate the service, browser profile, or live proof commands.

### Evidence and acceptance contract

Each fresh proof must expose through public `collection list` and immutable
schema-12 envelopes:

- distinct run, job, acquisition, and attempt identities plus selector/spec
  digests and exact scheduled interval;
- exact governed request count within 50, zero cost, one attempt, and terminal
  wall time within 120 seconds;
- attempted, observed, accepted, rejected, stored, deduplicated, and indexed
  counts with their invariants satisfied;
- attempted and selected access methods plus concrete adapter variant;
- exact pre/post document count, embedding count, and active index version;
- truthful yield classification: content yield, deduplicated yield, healthy
  zero yield, quality rejection, method rejection, or failure.

Receipt `docs/dev/notes/0029-timed-polling-observability-completion-receipt.json`
must bind all four new proofs, the C42 Reddit proof, the five consumed legacy
identities, cumulative actual/reserved usage, current enabled-spec count, and
every immutable payload digest. Missing evidence is `not_proven`, never zero or
success. Content yield is not required for process proof, but only a non-empty
accepted/stored result supports current selector yield.

### Work graph, review, and hard stops

| State | Authorized action | Exit condition |
| --- | --- | --- |
| `awaiting_evidence_completion_review` | docs, deterministic validation, read-only runtime checks | one independent reviewer returns no critical finding |
| `evidence_completion_authorized` | four exact disabled manual proofs, serialized, no retry | all four identities terminal or a global stop fires |
| `awaiting_five_lane_review` | no source or schedule mutation | receipt 0029 and live state independently reviewed |
| `awaiting_recurring_enable_gate` | no schedule mutation | a later explicit operator approval covers a reviewed recurring packet |

Global hard stops are service/database integrity failure, any enabled
specification, private config mode drift, runtime non-convergence affecting the
owned browser lane, ambiguous `last30days-facebook` ownership, inability to
enforce exact method or one-attempt supervision, missing immutable receipt,
ceiling breach, credential/data-scope change, or inability to preserve
rollback. A source-local failure records that terminal identity and may allow
the next unrelated lane only when service integrity, ownership, and cumulative
ceilings remain sound. No failed lane is retried.

Delegation is deliberately limited to two fresh-context read-only reviews:
one before live work and one after receipt reconciliation. The primary agent
owns plan integration, all live commands, receipt construction, validation,
and final judgment. Each review has one pass; the plan review permits at most
one consolidated remediation, while a failed final evidence review stops the
packet split, reframed, or blocked.

### Checkpoint P0018-C43 | 2026-08-01

Plan version:

- 19

State transition:

- `awaiting_recurring_enable_gate -> awaiting_evidence_completion_review`

Progress classification:

- `blocker_reduction`

Authority classification:

- `human_gate`; the operator's `ok go` authorizes the exact four-proof
  successor and cumulative rebaseline above, conditional on independent plan
  review. Recurring enablement remains a separate unconsumed human gate.

Current evidence and changed assumption:

- independent recurring-gate assessment returned `FAIL`: four yielding legacy
  receipts prove 10 stored items but not the version-18 request/count/snapshot
  contract; Reddit proves complete healthy-zero-yield observability but no
  current content yield;
- five original manual attempts plus the C42 successor consume six identities,
  so the planned 14 scheduled identities no longer fit V17's maximum 19;
- C43 treats legacy identities as consumed and reserves their full 250-request
  allowance rather than inventing actual usage. The cumulative envelope is
  rebaselined to 24 attempts, 64 items, 1,156 requests, 2,280 seconds, zero
  cost/model use, and concurrency one;
- current readbacks show service 0.2.24/schema 12 ready, config mode 0600,
  59 documents/59 embeddings, authority audit passing, and all 37
  specifications disabled.

Subagent status and reconciliation:

- `completed`; fresh-context read-only reviewer `/root/v19_plan_review`
  returned `FAIL` with one consolidated authority-drift finding: Roadmap P07
  still presented v0.2.20/C39 facts as current. The single permitted
  remediation marked that progression historical and added current
  0.2.24/C42/C43 authority. Scope, arithmetic, exact methods, evidence,
  attempt controls, serialization, hard stops, and the separate recurring gate
  were otherwise sound. No delegated writer or live operator was authorized.

Graphiti write status:

- deferred until the reviewed plan checkpoint or terminal evidence checkpoint;
  the C42 asynchronous write is not retried by this packet.

Next action:

- independently review Version 19/C43. If it passes after at most one bounded
  remediation, write a durable reviewed checkpoint and commit it before any
  source request. Otherwise stop without live mutation.

### Checkpoint P0018-C44 | 2026-08-01

Plan version:

- 19

State transition:

- `awaiting_evidence_completion_review -> evidence_completion_authorized`

Progress classification:

- `blocker_reduction`

Authority classification:

- `human_gate`; the operator-approved four-proof successor may run
  within Version 19's exact cumulative envelope. Recurring enablement remains
  a separate unconsumed human gate.

Independent review and remediation:

- fresh-context reviewer `/root/v19_plan_review` returned one consolidated
  `FAIL`: Roadmap P07 retained superseded v0.2.20/C39 facts as current state;
- the one permitted remediation added explicit current 0.2.24/C42/C43
  authority and marked the remaining progression historical;
- the same reviewer returned `PASS` after remediation with no remaining
  critical finding. It confirmed the 24-attempt/64-item/1,156-request/2,280-
  second arithmetic, exact methods and selectors, evidence contract,
  one-attempt/no-retry policy, browser serialization, hard stops, and separate
  recurring gate;
- `git diff --check` and the deterministic authority audit pass with one active
  plan, latest Runbook Turn 107, and zero issues.

Current containment:

- no source, schedule, service, config, credential, or browser mutation has
  occurred in Version 19;
- service 0.2.24/schema 12 remains ready, config is mode 0600, corpus/index is
  59/59, and all 37 specifications remain disabled.

Subagent status and reconciliation:

- `completed`; `/root/v19_plan_review` was read-only and made no edits or live
  mutations. Its sole finding was accepted and repaired in the bounded pass;
  its post-remediation verdict is the independent plan acceptance evidence.

Graphiti write status:

- deferred to the terminal evidence checkpoint so the durable memory can bind
  actual proof outcomes; no prior job was retried.

Next action:

- commit C44 as the pre-live checkpoint. Then execute the four existing
  disabled specifications serially in the named order with one attempt each,
  no retry, and no schedule enablement. Stop on a global hard stop.

## Version 20 | Immutable index-membership remediation

### Trigger and bounded outcome

Version 19's first proof published YouTube run
`collection-run-b813953558bd3f2098bffb15f14168b1` on one attempt with one
governed request and three accepted, stored, deduplicated items. Its receipt
recorded 59 embeddings before publication and 56 afterward. Read-only database
evidence then showed both the new index and the previously published
`index-8c968b3c270aa6c2b5abcbac` at 56 embedding rows with identical membership
digests. The old index had been mutated after publication, violating the
immutable snapshot contract even though SQLite checks and service readiness
remained healthy.

Repair the existing retrieval/publication deep module so a content-version
update refreshes the mutable current embedding without deleting the parent row
referenced by historical index snapshots. Preserve historical index rows and
publish a complete successor index for the new current document versions.
Remain on schema 12 and retain rollback to service 0.2.24.

### Scope and non-goals

Owned write surfaces are:

- `skills/last30days/scripts/lib/service_publication.py` and
  `service_retrieval.py` at the existing chunk/version embedding seam;
- one vertical public-path regression in existing publication/retrieval tests;
- service version/runtime package evidence and only the governing
  Plan/Roadmap/Runbook/receipt surfaces.

Do not add an endpoint, schema migration, alternate index lifecycle, source
attempt, schedule change, selector/method/profile change, credential work,
assessment/model call, data deletion, push, tag, publication, or release.
Do not reconstruct or silently rewrite the already-mutated historical index;
receipt 0029 preserves that defect as evidence. The repaired service must
prevent future mutation and publish forward from current authoritative corpus
state.

### Design and test contract

The module interface remains `CorpusPublisher.record_result()`,
`HybridRetriever.embed_pending_chunks()`, `publish_index()`, and service status.
The implementation must:

- stop deleting a mutable `chunk_embeddings` parent whose foreign-key cascade
  removes copied rows from every historical `index_chunk_embeddings` snapshot;
- treat a new current document version without its version embedding as
  pending even when the stable legacy chunk already has an embedding;
- upsert the stable current embedding in place, insert the version-specific
  embedding, and leave every previously published index row byte-identical;
- publish a new index whose embedding membership covers the current corpus and
  whose semantic query observes the changed current text.

The tracer test must fail on 0.2.24 by proving that publishing changed content
reduces or mutates the old index. It passes only when the old index count and
membership digest remain unchanged, the new index retains full embedding
membership, current version embedding exists, and retrieval returns the new
content. Add only the next test needed if the tracer exposes another invariant.

### Work graph and bounds

| Work unit | Dependency | Exit condition |
| --- | --- | --- |
| I01 vertical RED | C45 | one public publication/retrieval regression fails for historical index mutation |
| I02 minimal GREEN | I01 | parent deletion is removed and current/version embeddings refresh without historical mutation |
| I03 package/install | I02 | focused and full suites pass; version-distinct schema-12 artifact installs ready with rollback 0.2.24 retained |
| I04 independent review | I03 | one fresh reviewer returns no critical finding after at most one remediation pass |

One implementation packet, one vertical TDD cycle per revealed behavior, one
review/rework cycle, zero source requests, zero model/assessment spend, and
runtime mutation concurrency one. A schema change, rollback failure, corpus
count loss, enabled specification, database integrity failure, package digest
mismatch, or unresolved critical review finding stops the packet.

### Acceptance and terminal state

Acceptance requires deterministic proof that historical index rows no longer
change after a current-version update; current and version embeddings refresh;
the full repository suite, package checks, authority audit, and SQLite checks
pass; a version-distinct service is installed ready on schema 12; all 37 specs
remain disabled; and independent review passes.

The packet then stops at `awaiting_replacement_youtube_proof_gate`. The consumed
Version 19 YouTube identity is never retried. A distinct replacement proof
would raise the cumulative envelope from 24 to 25 attempts and therefore
requires explicit operator approval. X, LinkedIn, and recurring enablement
remain prohibited until that successor gate is satisfied.

### Checkpoint P0018-C45 | 2026-08-02

Plan version:

- 20

State transition:

- `evidence_completion_authorized -> global_integrity_stop -> active_index_immutability_remediation`

Progress classification:

- `blocker_reduction`

Authority classification:

- `inherited_authority`; the no-source deterministic repair preserves Plan
  0018's approved system, data, mutation, cost, and rollback envelope. It does
  not authorize a replacement source attempt or increase a live ceiling.

Evidence and containment:

- receipt `docs/dev/notes/0029-timed-polling-observability-completion-receipt.json`
  binds the YouTube run, all immutable envelope digests, exact counts and
  provenance, the 59-to-56 embedding regression, identical current membership
  hashes for old/new indexes, and three `not_run` lanes;
- the hard stop fired before X or LinkedIn submission. One attempt, one
  governed request, three accepted items, 1.942 seconds, and zero cost were
  consumed; no retry ran;
- service 0.2.24/schema 12 remains process-ready, SQLite `quick_check` is `ok`,
  foreign-key check is empty, corpus remains 59 documents, active index reports
  56 embeddings, and all 37 specifications remain disabled;
- structural diagnosis identified the narrow failure: publication deletes the
  stable chunk embedding before changing a version, and
  `index_chunk_embeddings` uses an `ON DELETE CASCADE` foreign key to that
  mutable parent.

Delegation decision:

- `not_spawned` for the tightly coupled RED/GREEN implementation; the primary
  agent owns the deep module and package/install path. One fresh-context
  read-only reviewer is reserved for I04.

Graphiti write status:

- deferred to the terminal remediation checkpoint; no memory is written from
  the unreviewed diagnosis.

Next action:

- commit receipt 0029 and C45, then execute I01-I03 with vertical TDD and zero
  source traffic. Stop before any replacement proof.

### Checkpoint P0018-C46 | 2026-08-02

Plan version:

- 20

State transition:

- `active_index_immutability_remediation -> awaiting_replacement_youtube_proof_gate`

Progress classification:

- `blocker_reduction`

Authority classification:

- `human_gate`; the deterministic repair is complete. A distinct replacement
  YouTube proof would raise the cumulative ceiling from 24 to 25 attempts and
  therefore requires explicit operator approval. X, both LinkedIn lanes, and
  recurring enablement remain prohibited.

Implementation and evidence:

- implementation commit
  `358d041856b978b5ae2956a44f07c6f22981e8de` removes stable-parent deletion,
  recognizes missing current-version embeddings as pending, updates the stable
  embedding in place, and inserts version embeddings without changing the
  existing public interfaces or schema 12;
- the public-path regression first reproduced the cascade and now proves that
  a changed current version leaves the published historical membership
  unchanged, receives stable and version embeddings, publishes a complete new
  index, and returns the changed text;
- service 0.2.25 installed ready with artifact SHA-256
  `d8791fcdfe66bf20f14f84292b843e2ef39db904eb35df3a331cb95c1bb34400`,
  runtime manifest
  `15f816afd3a84fdac036b895d1c912696e5e320b0dfbb1fd7e465200215bdf90`,
  unchanged contract digest
  `3fb7df8ab6d17e1e381090120a7d30c99027cc3d555b1c3bfe7a0eeb84983c6f`,
  and rollback release 0.2.24 retained;
- active index `index-b5cd4d63810e8d5333a0aa93` contains 59 documents
  and 59 embeddings. Both already-damaged historical indexes remain at 56
  rows and were not reconstructed or silently rewritten;
- receipt `docs/dev/notes/0030-index-immutability-remediation.json` binds the
  cause, repair, installed state, validation, preserved damage, source
  containment, and successor gate.

Validation and review:

- full suite: 2,415 passed, 7 skipped, and 6 subtests passed; focused tests,
  Python compilation, Go tests, package checks, SQLite quick/foreign-key
  checks, and deterministic authority audit passed;
- fresh-context reviewer `/root/v20_index_review` returned `PASS` with zero
  critical findings and independently confirmed source/install equality,
  59 current embeddings, preserved 56-row damaged history, 59-row successor
  index, rollback 0.2.24, zero enabled specs, and no post-stop source run;
- all 37 specifications remain disabled. No YouTube retry, X/LinkedIn proof,
  recurring interval, schema change, credential mutation, push, tag,
  publication, or release occurred.

Graphiti write status:

- one provider-ready write was queued in `last30days_skill_main` as job
  `053ba077-eb9d-4a7e-9bd9-699228d9d9f0`; no retry is authorized or run.

Next action:

- stop at `awaiting_replacement_youtube_proof_gate`. If the operator explicitly
  approves the 25-attempt ceiling, design/review one distinct replacement
  YouTube proof before reconsidering X, LinkedIn, or recurrence.

## Version 21 | Replacement YouTube immutable-index proof

### Bounded outcome and authority

Run exactly one distinct manual proof through existing disabled specification
`p0018-v17-youtube-ytdlp-manual` on installed service 0.2.25/schema 12. The
proof must exercise exact `yt_dlp` publication after the immutable-index repair
while proving that every already-published index snapshot remains unchanged
and the new active index is complete for current document versions.

The operator's 2026-08-02 `om approved`, replying to the exact C46 gate,
authorizes this single proof and raises the cumulative attempt ceiling from 24
to 25. It also authorizes the proof-local existing specification ceilings:
three accepted items, 50 governed requests, 120 wall seconds, zero cents, zero
assessment/model calls, and acquisition concurrency one. Reconciliation of
the previously consumed YouTube proof to its exact actual use sets the
cumulative envelope to 25 attempts, 67 accepted items, 1,157 governed
requests, 2,280 wall seconds, zero cost/model calls, and concurrency one.

Live work remains conditional on one fresh-context read-only plan review with
no critical finding after at most one consolidated remediation. The user did
not authorize X, LinkedIn, Reddit, recurring enablement, configuration or
credential change, selector/method revision, service upgrade, push, tag,
publication, or release.

### Exact identity and execution controller

Use the existing specification without revision:

- collection specification: `p0018-v17-youtube-ytdlp-manual`;
- source/surface/selector: YouTube topic `OpenAI latest`;
- required and expected selected method: `yt_dlp`;
- scheduled boundary: `2026-08-02T12:00:00Z`;
- expected interval: `2026-08-01T12:00:00Z` through
  `2026-08-02T12:00:00Z`;
- supervisor: hard-coded manual `max_attempts=1`, no retry or replay;
- specification state: disabled before, during, and after the proof.

Before submission, re-read service status, exact spec, latest run, config mode,
SQLite checks, current corpus/index counts, and membership digests for the two
damaged historical indexes plus current index
`index-b5cd4d63810e8d5333a0aa93`. Verify no run already owns the exact interval.
The primary agent alone operates the service. A reviewer may inspect only.

### Evidence and acceptance contract

Receipt `docs/dev/notes/0031-replacement-youtube-index-proof.json` must bind:

- run, job, acquisition, attempt, selector/spec, and immutable envelope
  identities and digests;
- exact attempted/observed/accepted/rejected/stored/deduplicated/indexed counts,
  exact governed request count within 50, zero cost, one attempt, and terminal
  wall time within 120 seconds;
- exact `youtube_ytdlp` adapter variant and attempted/selected `yt_dlp` method;
- pre/post document, stable/current-version embedding, active-index, SQLite,
  and enabled-spec counts;
- pre/post row counts and deterministic membership digests for the two damaged
  historical indexes and the repaired pre-proof current index;
- whether the run created an updated document version and a complete successor
  active index without changing any prior snapshot.

Acceptance requires at least one accepted, stored, and deduplicated item so the
live publication path is exercised; unchanged row counts and membership
digests for every pre-existing index; 59 documents and 59 stable/current-
version embeddings after publication; a complete new active index; SQLite
`quick_check=ok` with zero foreign-key rows; all 37 specs disabled; and one
independent final receipt review with no critical finding. Healthy zero yield,
quality rejection, missing provenance/envelopes, unchanged active index without
an updated version, or incomplete embeddings is truthful `not_proven`, never a
pass, and receives no retry.

### Work graph and hard stops

| State | Authorized action | Exit condition |
| --- | --- | --- |
| `awaiting_replacement_youtube_plan_review` | docs, deterministic audit, read-only runtime checks | one independent reviewer passes |
| `replacement_youtube_proof_authorized` | one exact manual submission and observation | terminal receipt or first hard stop |
| `awaiting_replacement_youtube_final_review` | receipt/docs and read-only validation only | independent receipt review passes or fails |
| `awaiting_remaining_evidence_plan` | no live mutation | later bounded successor is reviewed and authorized |

Global hard stops are any enabled spec, service/schema/runtime-manifest drift,
config-mode drift, duplicate interval identity, inability to enforce exact
method or one attempt, request/wall/cost ceiling breach, SQLite failure,
document loss, stable/current-version embedding incompleteness, any change to a
pre-existing index's membership, missing immutable evidence, rollback loss, or
unreviewed critical finding. The consumed V19 identity is never retried. X,
LinkedIn, Reddit, and recurrence remain prohibited regardless of proof outcome.

Delegation is limited to one fresh-context read-only plan review and one
fresh-context read-only final receipt review. The primary owns all planning
integration, live commands, receipt construction, validation, and judgment.
Each review has one pass; the plan review permits at most one consolidated
remediation, and a failed final review stops without reopening the proof.

### Checkpoint P0018-C47 | 2026-08-02

Plan version:

- 21

State transition:

- `awaiting_replacement_youtube_proof_gate -> awaiting_replacement_youtube_plan_review`

Progress classification:

- `blocker_reduction`

Authority classification:

- `human_gate`; the operator explicitly approved the distinct replacement
  YouTube proof and 25-attempt cumulative ceiling. The proof-local standard
  limits and reconciled cumulative item/request ceilings above are part of that
  single approved proof. No other live lane or recurrence is authorized.

Current evidence and containment:

- service 0.2.25/schema 12 is ready with runtime manifest
  `15f816afd3a84fdac036b895d1c912696e5e320b0dfbb1fd7e465200215bdf90`,
  59 documents, 59 embeddings, and active index
  `index-b5cd4d63810e8d5333a0aa93` at 59 embedding rows;
- damaged historical indexes `index-8c968b3c270aa6c2b5abcbac` and
  `index-761f40d7055bbc84a4018cd1` remain at 56 rows; config mode is 0600,
  SQLite quick check is `ok`, foreign-key check is empty, and all 37 specs are
  disabled;
- the exact `2026-08-02T12:00:00Z` boundary is the next unconsumed 12-hour
  cadence boundary after the V19 `2026-08-02T00:00:00Z` identity and is not in
  the future at checkpoint time;
- no source, schedule, service, config, credential, database, browser, push,
  tag, publication, or release mutation occurred while opening C47.

Delegation decision:

- `spawned`; one fresh-context read-only reviewer will inspect only the Plan,
  Roadmap, Runbook, receipts 0029/0030, live readbacks, and arithmetic. The
  primary retains the serialized critical path and all write/live authority.

Graphiti write status:

- deferred to the reviewed pre-live or terminal proof checkpoint; C46 job
  `053ba077-eb9d-4a7e-9bd9-699228d9d9f0` is not retried.

Next action:

- run one independent plan review. On pass after at most one consolidated
  remediation, persist and commit the pre-live checkpoint before submission.
  On fail, stop with all specifications disabled.

### Checkpoint P0018-C48 | 2026-08-02

Plan version:

- 21

State transition:

- `awaiting_replacement_youtube_plan_review -> replacement_youtube_proof_authorized`

Progress classification:

- `blocker_reduction`

Authority classification:

- `human_gate`; the operator-approved single proof passed its required
  independent plan review. This checkpoint authorizes only the exact C47
  YouTube identity within the 25-attempt cumulative envelope.

Independent review and current evidence:

- fresh-context reviewer `/root/v21_plan_review` returned `PASS` in one pass
  with no critical finding and no edits or runtime mutations;
- the reviewer independently confirmed scope, exact `yt_dlp` selector/method,
  one-attempt/no-retry behavior, 25/67/1,157/2,280 cumulative arithmetic,
  immutable-index acceptance, healthy-zero-yield `not_proven` semantics,
  hard stops, and prohibition of X, LinkedIn, Reddit, and recurrence;
- its readbacks confirmed service 0.2.25/schema 12 ready, runtime manifest
  `15f816afd3a84fdac036b895d1c912696e5e320b0dfbb1fd7e465200215bdf90`,
  59 documents, 59 stable embeddings, 59 current-version embeddings, active
  index `index-b5cd4d63810e8d5333a0aa93` at 59 rows, both damaged historical
  indexes at 56 rows, SQLite `ok`/zero foreign-key rows, config 0600, and 37
  specs with zero enabled;
- exact interval `2026-08-01T12:00:00Z` through `2026-08-02T12:00:00Z`
  has zero existing runs. The reviewer confirmed the boundary is past and the
  V19 run remains the newest target-spec identity;
- deterministic authority audit and `git diff --check` pass with Plan/Roadmap/
  Runbook aligned at Version 21/C47 before this reviewed checkpoint.

Delegation status and reconciliation:

- `completed`; the reviewer was read-only and its `PASS` is accepted as the
  required pre-live review. The primary independently verified the audit,
  arithmetic, and live preflight and retains all live-operation authority.

Graphiti write status:

- deferred to the terminal proof checkpoint; no prior memory job is retried.

Next action:

- commit C48, repeat the exact preflight, then submit only
  `p0018-v17-youtube-ytdlp-manual` at `2026-08-02T12:00:00Z`. Observe it to one
  terminal state, persist receipt 0031, and do not retry.

### Checkpoint P0018-C49 | 2026-08-02

Plan version:

- 21

State transition:

- `replacement_youtube_proof_authorized -> global_integrity_stop -> awaiting_replacement_youtube_final_review`

Progress classification:

- `regression`; the prior historical-cascade defect did not recur, but the
  production job path exposed a distinct current-version embedding gap.

Authority classification:

- `inherited_authority`; this checkpoint records and reviews the consumed
  identity only. It authorizes no retry, source, schedule, service repair,
  configuration change, or recurrence.

Execution and integrity evidence:

- committed pre-live authority `5946d0d` submitted only boundary
  `2026-08-02T12:00:00Z`, producing run
  `collection-run-779569ba5d104c1809c26f145a7b541b`, job
  `df2b728e-9f14-4d55-8679-71f5830ab1d3`, and acquisition
  `work-aa9680b95971f28413c5a47370008845`;
- one attempt completed in 1.772 seconds with one governed request, zero cost,
  exact `youtube_ytdlp`/`yt_dlp`, counts 8 attempted/observed, 3 accepted,
  5 rejected, and 3 stored/deduplicated/indexed;
- the aggregate full-row hash for all 66 pre-existing indexes remained
  `25ef7bff455b6c063cb13096244d2822e7914ccdbde15a1f0bafefea4d796fa4`.
  Both damaged 56-row indexes and repaired pre-proof 59-row index retained
  their exact individual hashes;
- the job published `index-d86e2cfdbbafaf5728fe1dd8`, after which active
  service state advanced to `index-e7d905148e9b02e077e1759e`. Both contain
  59 stable snapshot embeddings but only 56 current-version snapshot
  embeddings;
- three updated YouTube documents now point to current version chunks with no
  `document_version_embeddings` row. Stable embeddings remain 59, current-
  version completeness is 56, SQLite remains `ok`/FK0, config is 0600, and all
  37 specs remain disabled;
- receipt `docs/dev/notes/0031-replacement-youtube-index-proof.json` binds all
  identities, immutable envelopes, counts, hashes, missing versions, and the
  hard stop. No retry or other source ran.

Read-only structural diagnosis:

- CodeGraph proves `AcquisitionJobRunner.run_once()` records content and then
  calls `CorpusPublisher.publish_index()`, which delegates directly to
  `HybridRetriever.publish_index()` without `embed_pending_chunks()`;
- `embed_pending_chunks()` has production use only through legacy bootstrap;
  its other callers are tests. The 0.2.25 regression manually invoked the
  primitive, so it did not cover live job-runner ordering;
- a successor repair must be zero-source, use a full job-runner RED/GREEN test,
  complete version embeddings before index publication, preserve all existing
  index rows, and remain separately checkpointed. C49 itself does not authorize
  that repair.

Delegation status:

- one fresh-context read-only final reviewer is required to verify receipt
  0031, live state, the hard-stop classification, and the diagnosis. The
  primary owns all writes and no live operation may resume.

Graphiti write status:

- deferred until the failed proof is independently reviewed; no prior job is
  retried.

Next action:

- independently review receipt 0031 and C49. On pass, commit the fail-closed
  checkpoint and classify a bounded zero-source successor under standing
  authority. Do not run or retry any source.

### Checkpoint P0018-C50 | 2026-08-02

Plan version:

- 21

State transition:

- `awaiting_replacement_youtube_final_review -> replacement_youtube_proof_failed_closed`

Progress classification:

- `blocker_reduction`; independent review establishes the exact production
  sequencing defect and preserves truthful terminal evidence for the consumed
  proof.

Authority classification:

- `inherited_authority`; C50 closes review of the consumed proof. It authorizes
  no repair or source operation by itself.

Independent review and reconciliation:

- fresh-context reviewer `/root/v21_final_review` returned `PASS` in one
  read-only pass with no critical finding;
- it independently reproduced the one-run/one-attempt/no-retry scope, 1.772-
  second wall time, one request, zero cost, exact 8/8/3/5/3/3/3 counts,
  `youtube_ytdlp`/`yt_dlp` provenance, and all six envelope hashes;
- it reproduced the aggregate pre-existing index-row hash
  `25ef7bff455b6c063cb13096244d2822e7914ccdbde15a1f0bafefea4d796fa4`,
  bound-index hashes/counts, both new 59-stable/56-version index snapshots,
  and exactly three missing current YouTube version embeddings;
- it verified service 0.2.25/schema 12, manifest digest, SQLite `ok`/FK0,
  config 0600, 37 specs/zero enabled, no other source or recurrence, and the
  CodeGraph production-caller gap;
- JSON validation, deterministic authority audit, and `git diff --check` pass.
  The review authorizes no repair or source run.

Graphiti write status:

- deferred to the separately classified repair or terminal campaign
  checkpoint; no prior job was retried.

Next action:

- commit C50. Then classify one zero-source full-job-runner TDD successor under
  standing Plan 0018 repair authority. Do not retry or run any source.
