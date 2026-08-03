# Plan 0018 | Service-first software product transition

State: OPEN
Roadmap: P07
Date: 2026-07-29
Plan version: 28
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
  version 0.2.29/schema 12 with 59 documents, 59 stable embeddings, 59 current-
  version embeddings, and active index `index-28418bd968076bba6653223f` at
  59 stable and 59 current-version rows. Rollback is service 0.2.28.
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
- Version 21 is the operator-approved replacement-YouTube successor. Its one
  distinct disabled proof preserved every historical index but stopped on
  three missing current-version embeddings. Version 22 independently closed
  the zero-source sequencing repair on service 0.2.26 at exact 59/59
  completeness. Versions 23-25 established the standing 50-attempt ceiling,
  installed the bounded retry controller and durable X profile/handoff repair,
  then stopped after the fresh X job exhausted both attempts on agent-browser's
  route-bound display proof. Agent-browser P90 is now installed and live-
  proven; Version 26 is the review-first successor for one new X identity.

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

Checkpoint P0018-C74 is the current authority. Service architecture, timer
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
process-ready on schema 12 but version-embedding completeness is 56/59.
Version 22/C54 independently closes the zero-source 0.2.26 repair with 59/59
version completeness. Version 23/C56 independently accepts a bounded successor
for the three remaining proofs. Version 24/C58 authorizes the reviewed 0.2.27
install and proof packet under the standing 50-attempt ceiling. C59's
`awaiting_operator/auth_required` conclusion is superseded by the operator's
correction and the independently accepted 0.2.28 repair. C63 confirms that
repair live: X used `last30days-facebook` and did not request authentication or
manual handoff. Both allowed successor attempts instead stopped on the same
agent-browser `remote_view_open` timeout. LinkedIn remains `not_run`.
Agent-browser P90 subsequently repaired and live-proved the exact route-bound
display path on the installed runtime. Version 26/C64's independent review
found that service 0.2.28 validated the selected X profile without explicitly
passing the durable caller binding into access planning. C65 contains the one
bounded 0.2.29 remediation and received terminal independent PASS. C66
authorized installation of that exact artifact and one fresh X proof under its
reviewed controller. C67 records installed 0.2.29 and the one fresh X identity
published on attempt one as healthy zero yield with no auth or manual handoff,
unchanged 59/59 integrity, and cumulative actual use 29/50. C68 accepts the
fresh independent receipt-review PASS with no critical finding. The next
authorized action is planning and review for a bounded LinkedIn successor;
LinkedIn live execution, recurrence, push, tagging, publication, and release
remain closed.

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

### Checkpoint P0018-C51 | 2026-08-02

Plan version:

- 22

State transition:

- `replacement_youtube_proof_failed_closed -> zero_source_index_sequencing_repair_open`

Progress classification:

- `blocker_reduction`; repair the deterministic production sequence exposed by
  the consumed proof without acquiring any additional external evidence.

Authority classification:

- `inherited_authority`; Plan 0018 standing repair authority permits a bounded,
  reversible service correction after the hard stop. This checkpoint does not
  authorize a source attempt, retry, recurring schedule, release, tag, push, or
  public publication.

Bounded outcome and design:

- make the existing `CorpusPublisher.publish_index()` interface own the full
  preparation-and-publication invariant: configured pending current-version
  embeddings complete before its immutable snapshot is published;
- keep the module interface unchanged. `AcquisitionJobRunner` remains a caller
  of one deep publication operation and does not learn an extra ordering rule;
- add one integration-style regression through the real
  `AcquisitionJobRunner.run_once()` interface with a deterministic local
  embedding adapter. The observable result must be a published job whose index
  contains the new current-version embedding;
- prove the test fails on 0.2.25 before implementation, then apply the minimal
  publisher change and prove it passes;
- advance the package to 0.2.26, run focused and full repository validation,
  build and install through the repo-native installer, and verify service,
  schema, manifest, database integrity, 59/59 current-version completeness,
  immutable pre-existing index rows, and 37 disabled specifications;
- installation may deterministically forward-fill the three already-recorded
  version embeddings and publish a successor index. It may not mutate any
  pre-existing `index_chunk_embeddings` row or execute an acquisition worker.

Owned write surfaces:

- `tests/test_service_job_runner.py`;
- `skills/last30days/scripts/lib/service_publication.py`;
- service version and runtime-package artifacts required by the existing build
  workflow;
- Plan 0018, Roadmap P07, Runbook, and one machine-readable repair receipt.

Acceptance and hard stops:

- RED must identify the missing version embedding through the full runner path;
- GREEN must preserve the single publication interface and existing immutable
  snapshot tests;
- focused tests, full `uv run pytest`, package validation, install verification,
  SQLite `quick_check=ok`/foreign-key zero, manifest verification, exact 59/59
  current-version completeness, historical full-row aggregate equality, config
  mode 0600, and 37 specifications/zero enabled must pass;
- stop immediately on any source execution, pre-existing index-row mutation,
  schema or config drift, failed validation, or incomplete live forward repair;
- one fresh-context read-only final review is required before terminal closeout.
  The primary owns all writes; no implementation delegation is authorized.

Next action:

- commit C51, write exactly one full-runner regression, and capture RED before
  editing product code. Do not run or retry any source.

### Checkpoint P0018-C52 | 2026-08-02

Plan version:

- 22

State transition:

- `zero_source_index_sequencing_repair_open -> zero_source_repair_package_ready`

Progress classification:

- `implementation_complete`; the bounded source correction and repository
  validation pass before live installation.

Authority classification:

- `inherited_authority`; C51 permits one reversible install verification of the
  already-reviewed zero-source repair. All source and release gates remain
  closed.

RED/GREEN and package evidence:

- the new full-runner test failed on unchanged product code because the
  published semantic evidence list was empty;
- the minimal correction makes `CorpusPublisher.publish_index()` call
  `embed_pending_chunks()` before `HybridRetriever.publish_index()` while
  preserving its single existing interface;
- the same test passed, followed by 23 focused runner/publication/retrieval
  tests and 7 service version/runtime-package tests;
- the deterministic runtime manifest was refreshed for service 0.2.26;
- the full repository suite passed with 2,416 tests, 7 skips, and 6 subtests.
  The sole first-pass failure was the plan header's stale version declaration;
  after correcting it to version 22, the authority audit and full suite passed;
- CodeGraph post-edit blast-radius review retains the runner's one-call
  publication flow. No acquisition source or installed runtime was touched.

Next action:

- commit C52 and the package-ready implementation. Then capture exact live
  pre-install hashes, build the reproducible 0.2.26 artifact, install once,
  and verify deterministic forward repair without running a source.

### Checkpoint P0018-C53 | 2026-08-02

Plan version:

- 22

State transition:

- `zero_source_repair_package_ready -> awaiting_zero_source_repair_final_review`

Progress classification:

- `verification_complete`; installed runtime and database evidence satisfy the
  bounded repair gates pending neutral review.

Authority classification:

- `inherited_authority`; the one permitted reversible install is consumed. C53
  authorizes read-only review only and no source, retry, schedule, repair,
  release, tag, push, or publication action.

Install and forward-repair evidence:

- committed implementation `f3a7c9c` built reproducible artifact SHA-256
  `c1e9ba5a2eb0cda88f873cc045eca25d5cfb940ea6072b156b9df7e9b50b2264`;
- the repo-native installer upgraded exactly once to service 0.2.26/schema 12,
  manifest `21564f14a2c87f3d2ee27013470bdc3642e9d70997facebc726b75c92982c1fb`,
  leaving 0.2.25 as rollback;
- startup deterministically added only the three missing current-version
  vectors and one successor index `index-28418bd968076bba6653223f`. Current-
  version completeness is 59/59 and both its stable and version snapshot
  surfaces contain 59 rows;
- all 2,345 rows across the 68 pre-install stable index snapshots retained exact
  aggregate SHA-256
  `d825e7dbd6dc59fd29028faa9a40c2b36843504d664aabe8f137612191e8de5b`.
  The earlier 66-index aggregate also remains the receipt-bound
  `25ef7bff455b6c063cb13096244d2822e7914ccdbde15a1f0bafefea4d796fa4`;
- documents, acquisitions, jobs, and collection runs stayed 59/102/87/50.
  SQLite is `ok`/FK0, service is ready and active/running, config is 0600, and
  all 37 specifications remain disabled;
- machine-readable receipt
  `docs/dev/notes/0032-zero-source-index-sequencing-repair.json` binds the
  RED/GREEN, artifact, manifest, pre/post counts, hashes, versions, and source
  prohibitions.

Delegation status:

- one fresh-context read-only final reviewer must verify code, tests, package,
  receipt 0032, installed runtime, database completeness, historical
  immutability, and zero-source scope. The primary retains all writes.

Next action:

- run exactly one independent final review. On pass, reconcile and close the
  repair checkpoint; on critical finding, stop and classify a new successor.

### Checkpoint P0018-C54 | 2026-08-02

Plan version:

- 22

State transition:

- `awaiting_zero_source_repair_final_review -> zero_source_index_sequencing_repair_complete`

Progress classification:

- `complete`; the bounded production sequencing repair is implemented,
  installed, independently verified, and closed.

Authority classification:

- `inherited_authority`; C54 closes only the zero-source repair. It does not
  increase the consumed 25-attempt ceiling or authorize X, LinkedIn, YouTube,
  Reddit, recurrence, push, tag, publication, or release.

Independent review and reconciliation:

- fresh-context read-only reviewer `/root/v22_final_review` returned `PASS`
  with no critical finding;
- it independently reran 23 focused tests, 7 package/version tests, and the
  full 2,416-test suite with 7 skips and 6 passing subtests;
- it verified the public full-runner regression, one deep publisher interface,
  embed-before-publish ordering, and identical installed/source publisher
  SHA-256 `bfbf2c7526887c5f02099087925fb99323d512812747c85ba6f7896a6ceef208`;
- it reproduced the artifact, manifest, installed/rollback versions, ready and
  active runtime, SQLite integrity, exact 59/59 completeness, active 59/59
  index, both historical aggregate hashes, unchanged 102/87/50 execution
  counts, config 0600, and 37 specs/zero enabled;
- receipt 0032, deterministic authority audit, JSON validation, and diff check
  pass. No rework or additional live action was required.

Remaining campaign gate:

- the repair is complete, but the cumulative source-attempt ceiling is fully
  consumed at 25. The three unexecuted proof identities—one X and two LinkedIn
  cases—remain closed. Any successor must separately request the exact attempt
  ceiling increase and retain one-attempt/no-retry, serial execution, global
  integrity stops, and independent receipt review. Recurrence remains a later
  separate gate even if those proofs pass.

Next action:

- commits `f3a7c9c` and `7f11000` close the repair and receipt. Graphiti job
  `1dfbe360-4e08-4dab-92e4-fa7d6e09b3b5` timed out on its single 120-second
  ingestion attempt and is `graphiti_write_pending` for the next non-trivial
  closeout. Do not retry it now. Stop at the remaining-proof human gate.

## Version 23 | Remaining X and LinkedIn evidence-completion successor

### Bounded outcome and requested authority

Complete the version-18 observability evidence set with exactly three fresh,
serialized, disabled-specification proofs: one X topic, one LinkedIn topic,
and one LinkedIn profile. Each proof must use the already configured exact
`agent_browser` method and existing `last30days-facebook` profile, publish a
complete immutable receipt, and leave every specification disabled.

This successor is review-first and is not live authority. The terminated
Version 19 packet and consumed replacement-YouTube successor leave the
cumulative source-attempt ceiling fully allocated at 25. Before any submission,
the operator must explicitly raise only that ceiling from 25 to 28 for the
three named identities. The existing cumulative maxima remain 67 accepted
items, 1,157 governed requests, 2,280 wall seconds, zero cents, zero
assessment/model calls, and acquisition concurrency one: Version 19 already
reserved the three remaining cases' worst-case item, request, and wall usage,
but its terminated live authority cannot be silently reused as three new
attempt identities.

The proposed approval does not authorize YouTube or Reddit, a retry or replay,
recurrence, an enabled specification, a selector/method/profile/access-order
change, credential work, service installation, database repair, browser-session
cleanup, push, tag, publication, or release. Recurring enablement remains a
separate later human gate even if all three proofs pass.

### Exact identities and execution controller

Use the existing specifications without revision, in this order:

1. `p0018-v17-x-browser-manual`, X topic `OpenAI`;
2. `p0018-v17-linkedin-topic-browser-manual`, LinkedIn topic `OpenAI`;
3. `p0018-v17-linkedin-profile-browser-manual`, LinkedIn profile
   `https://www.linkedin.com/company/openai/`.

For each specification, use the distinct daily cadence boundary
`2026-08-02T00:00:00Z`, covering `2026-08-01T00:00:00Z` through
`2026-08-02T00:00:00Z`. Current readback shows no run owns any of those three
spec/interval identities. Before each submission, re-read the exact spec,
latest run, enabled state, browser-profile ownership, service/systemd status,
config mode, SQLite checks, corpus/current-version completeness, active-index
membership, and cumulative usage.

The primary agent alone operates the service and browser profile. Hard-code
manual supervisor `max_attempts=1`; do not retry, replay, or substitute a
cadence boundary after a failed, deduplicated, skipped, or incomplete identity.
Keep the target and all other specifications disabled before, during, and after
each proof. Serialize browser work on `last30days-facebook`; verify the prior
lease is released before advancing.

### Evidence and acceptance contract

Receipt `docs/dev/notes/0033-remaining-x-linkedin-evidence-completion.json`
must bind all three proposed identities plus the previously consumed evidence:

- run, job, acquisition, attempt, selector/spec, interval, and immutable
  envelope identities and digests;
- exact attempted, observed, accepted, rejected, stored, deduplicated, and
  indexed counts; governed requests within 50 per proof; zero cost; one attempt
  per identity; and terminal wall time within 120 seconds per proof;
- exact adapter variant and attempted/selected `agent_browser` provenance;
- pre/post documents, stable and current-version embeddings, active-index
  stable/version membership, SQLite, config-mode, enabled-spec, and execution
  counts;
- deterministic membership digests proving every pre-existing immutable index
  row remains byte-identical;
- cumulative actual/reserved use against the 28/67/1,157/2,280/zero envelope;
- truthful per-lane classification as content yield, deduplicated yield,
  healthy zero yield, quality rejection, method rejection, or failure.

Acceptance does not require content yield, but only non-empty accepted/stored
content supports current selector yield. Missing evidence is `not_proven`,
never zero or success. Final acceptance requires all three identities terminal
without retry; all immutable envelopes and count invariants complete; service
0.2.26/schema 12 ready and systemd active/running; 59 documents with 59 stable
and 59 current-version embeddings; a complete active index; unchanged
historical membership; SQLite `quick_check=ok` with zero foreign-key rows;
config mode 0600; 37 specifications with zero enabled; and one fresh-context
independent final receipt review with no critical finding.

### Work graph, bounds, and hard stops

| State | Authorized action | Exit condition |
| --- | --- | --- |
| `awaiting_remaining_evidence_plan_review` | plan/docs and read-only Git/runtime/database checks | one fresh reviewer passes after at most one consolidated remediation |
| `awaiting_remaining_evidence_operator_gate` | no live or browser mutation | operator explicitly approves the exact 25-to-28 ceiling increase and three identities |
| `remaining_evidence_authorized` | three exact disabled manual proofs, serialized, one attempt each | all three identities terminal or the first global stop fires |
| `awaiting_remaining_evidence_final_review` | receipt/docs and read-only validation only | one fresh reviewer passes or fails |
| `awaiting_recurring_enable_gate` | no schedule mutation | a later separately reviewed packet receives explicit approval |

One pre-live plan review, three serial work-unit attempts, zero retries, one
terminal receipt review, and at most one consolidated remediation per review
are the hard bounds. A source-local failure records that terminal identity and
may advance only when service integrity, browser ownership, cumulative limits,
and every global invariant remain sound. No failed identity is retried.

Stop the full packet immediately on any acquisition before the exact operator
approval; enabled specification; unexpected source or access method; retry,
replay, duplicate interval, or out-of-order proof; ambiguous browser ownership;
inability to enforce one-attempt supervision; cumulative ceiling breach;
nonzero cost or assessment/model use; service/schema/manifest/source-install
drift; config-mode or rollback drift; SQLite failure; document loss; stable or
current-version completeness below 59/59; incomplete active index; any change
to a pre-existing immutable index row; missing immutable evidence; or an
unresolved critical review finding.

Delegation is limited to one fresh-context read-only plan review and one
fresh-context read-only final receipt review. The primary agent owns plan
integration, all live and browser commands, receipt construction, validation,
and final judgment. The plan review gets one pass plus at most one consolidated
remediation; a failed final review stops for split, reframe, or escalation.

### Checkpoint P0018-C55 | 2026-08-02

Plan version:

- 23

State transition:

- `zero_source_index_sequencing_repair_complete -> awaiting_remaining_evidence_plan_review`

Progress classification:

- `blocker_reduction`; the three remaining cases now have one inspectable,
  bounded successor whose authority request and terminal stops are explicit.

Authority classification:

- `human_gate`; C55 authorizes planning, deterministic validation, and
  read-only review only. It does not raise the 25-attempt ceiling or authorize
  a source, browser, specification, schedule, credential, service, database,
  memory, push, tag, publication, or release mutation.

Current evidence and arithmetic:

- `HEAD` and `origin/main` both resolve to handoff commit `c6ee0be`; the
  worktree began clean and the deterministic authority audit passed with Plan
  0018 as the sole active plan;
- installed service 0.2.26/schema 12 is ready and systemd active/running with
  manifest `21564f14a2c87f3d2ee27013470bdc3642e9d70997facebc726b75c92982c1fb`,
  rollback 0.2.25, 59 documents, 59 stable/current-version embeddings, and
  active index `index-28418bd968076bba6653223f` at 59/59 rows;
- SQLite `quick_check` is `ok`, foreign-key check is empty, config is mode
  0600, acquisitions/jobs/collection runs remain 102/87/50, and all 37
  specifications are disabled;
- each target spec remains disabled on profile `last30days-facebook`, uses a
  daily schedule and item limit three, and has only its legacy
  `2026-07-31T00:00:00Z` through `2026-08-01T00:00:00Z` run. The proposed
  `2026-08-02T00:00:00Z` boundaries are distinct and unowned;
- raising attempts from 25 to 28 crosses an explicit cumulative ceiling and
  therefore requires new operator approval. The previously reserved
  item/request/wall maxima remain sufficient and unchanged.

Delegation decision:

- `spawned`; one fresh-context read-only reviewer will inspect the current
  plan, Roadmap P07, Runbook, receipts 0031/0032, Git, live service/database
  state, identity uniqueness, arithmetic, and gate semantics. The primary
  retains every write and all live-operation authority.

Graphiti write status:

- prior job `1dfbe360-4e08-4dab-92e4-fa7d6e09b3b5` remains
  `graphiti_write_pending`; C55 does not retry it before the required plan
  review.

Next action:

- validate and commit this docs-only checkpoint, then obtain one independent
  plan review. On pass after at most one consolidated remediation, advance to
  `awaiting_remaining_evidence_operator_gate` and ask the operator for the
  exact 25-to-28 ceiling increase. Do not run a source or browser command.

### Checkpoint P0018-C56 | 2026-08-02

Plan version:

- 23

State transition:

- `awaiting_remaining_evidence_plan_review -> awaiting_remaining_evidence_operator_gate`

Progress classification:

- `blocker_reduction`; the bounded successor passed its one-review/one-
  remediation contract and is ready for an exact operator decision.

Authority classification:

- `human_gate`; independent review does not raise the cumulative attempt
  ceiling. X and both LinkedIn proofs remain prohibited until the operator
  explicitly approves the named three identities and exact 25-to-28 increase.
  Reddit, YouTube, recurrence, retry/replay, and every other live or release
  action remain closed.

Independent review and remediation:

- fresh-context read-only reviewer `/root/v23_plan_review` returned one
  consolidated `FAIL`: Roadmap P07 called the replacement proof's historical
  56/59 post-state current even though its leading authority sentence and live
  state were 59/59;
- the single permitted remediation at commit `2d0dc73` changed only that
  wording to historical and restated C54's exact current 59/59 completeness;
- the same reviewer returned terminal `PASS` with no remaining critical
  finding. It independently confirmed the exact three specs and execution
  order, distinct proposed intervals, `agent_browser` and
  `last30days-facebook`, serial one-attempt/no-retry controls, zero cost/model
  use, 28/67/1,157/2,280 arithmetic, immutable evidence, global stops, and
  separate recurrence gate;
- its live readbacks reproduced service 0.2.26/schema 12 ready and systemd
  active/running, manifest and rollback, 59/59 current and active-index
  completeness, SQLite `ok`/FK0, config 0600, execution counts 102/87/50,
  37 specs/zero enabled, zero target-interval owners, and zero active profile
  leases;
- commit `80d594b` is the reviewed C55 planning surface; receipt files 0031 and
  0032 remained unchanged. The reviewer made no repo or runtime mutation.

Delegation status and reconciliation:

- `completed`; reviewer handle `/root/v23_plan_review` was fresh-context and
  read-only. The primary accepts the terminal `PASS` after the one bounded
  semantic remediation and retains all future live-operation authority.

Graphiti write status:

- prior C54 job `1dfbe360-4e08-4dab-92e4-fa7d6e09b3b5` remains historical
  timeout evidence. Provider readiness passed and one compact successor episode
  completed on its first attempt as job
  `741995ba-4085-45b3-8975-ab5401eafb43`, episode
  `0266c6d3-904f-4c91-bab4-7d9dbcf93041`. No second submission or manual
  requeue ran.

Next action:

- stop and ask the operator: approve exactly the three named Version 23 proofs
  and raise the cumulative attempt ceiling from 25 to 28, while retaining the
  67-item, 1,157-request, 2,280-second, zero-cost/model, concurrency-one
  envelope and every C55 stop? No source or browser command may run before an
  explicit approval.

## Version 24 | Standing attempt ceiling and bounded manual retries

### Operator authority and bounded outcome

The operator explicitly raised Plan 0018's cumulative source-attempt approval
ceiling from 25 to 50 and requested larger retry budgets so routine transient
failures do not repeatedly return to a human gate. This authority applies only
inside the already approved Plan 0018 goal, sources, authenticated/public data
classes, exact access methods, existing profiles, zero-cost/model boundary,
and concurrency-one controller. It is not permission to spend all 50 attempts
in this packet.

For the three Version 23 proof identities, authorize at most two attempts per
identity: one initial attempt plus one service-owned retry. The packet therefore
adds at most six source attempts and can move cumulative actual use only from
25 to 31. The 50-attempt value is the standing human-approval threshold for
later bounded Plan 0018 successors: a separately planned and reviewed successor
that preserves these exact systems, sources, data classes, profiles, access
methods, cost, integrity, and concurrency constraints need not ask the operator
again merely because it consumes another source attempt below 50.

Retries add worst-case resource exposure beyond Version 23's one-attempt
reservation. Add three retry maxima of three items, 50 governed requests, and
120 seconds. This packet's cumulative maxima are therefore 31 source attempts,
76 accepted items, 1,307 governed requests, 2,640 wall-clock seconds, zero
cents, zero assessment/model calls, and acquisition concurrency one. Exceeding
any packet maximum stops this packet. Reaching cumulative attempt 50 stops all
later source work at a new human gate even when every other invariant passes.

Recurrence, enabled specifications, a new source or identity, selector/method/
profile/access-order change, credential work, service repair, browser-session
cleanup, private-data expansion, nonzero cost/model use, push, tag,
publication, and release remain separate authority. In particular, this
approval does not enable a schedule.

### Required narrow implementation slice

The installed manual collection interface currently hard-codes
`max_attempts=1`; timer runs use two. Add one operator-only
`collection run --max-attempts N` option and thread it through
`CollectionCoordinator.enqueue_interval`. Preserve the public default of one
for manual runs and two for timer runs. Validate the override as an integer in
the closed interval 1 through 2; reject an override on a timer-triggered call.
Do not add the field to collection specifications or broaden the MCP research
surface. Document the operator flag in `CONFIGURATION.md`.

Use test-driven vertical slices:

1. preserve a manual run's observable default of one attempt;
2. prove an explicit manual value of two reaches the durable job record;
3. prove zero, values above two, and timer overrides fail before a run/job is
   created;
4. prove the CLI exposes and forwards `--max-attempts 2` through the public
   operator interface.

After focused and full tests pass, build and install a new patch service
release under the existing version/release policy, restart only the canonical
`last30days.service` unit, and prove source manifest, MCP compatibility,
database schema 12, rollback identity, 59/59 completeness, SQLite/config, and
zero-enabled-spec state before any proof submission. Installation/restart is
authorized only after the implementation and this Version 24 plan pass one
fresh-context read-only review.

### Retry eligibility and controller

Run the same three Version 23 specifications, intervals, order,
`agent_browser` method, and `last30days-facebook` profile. Submit each manual
run with `--max-attempts 2`. The resident service owns both attempts inside the
single immutable run/job identity; the primary agent must not create a second
interval, replay a terminal run, or manually invoke a browser adapter.

Attempt two is eligible only when attempt one fails with exact safe code
`worker_timeout`, `agent_browser_timeout`, `agent_browser_error`, or
`route_stale`, retry class `transient`, and the durable readback proves zero
accepted, stored, deduplicated, and indexed side effects. It is ineligible
after a lease expiry without a complete attempt receipt, content yield,
deduplicated yield, healthy zero yield, quality or method rejection,
authentication/credential failure, selector mismatch, access-scope drift,
database/index/integrity failure, ambiguous publication, or any nonzero or
missing side-effect count. Rate-limit, content, and unexpected internal-worker
classes are explicitly ineligible. An ineligible result terminalizes the lane without
retry and may advance to the next lane only when every global invariant and
profile-lease check passes.

No routine human ping is required for an eligible second attempt or for a
later reviewed successor below cumulative attempt 50. Stop for human authority
on recurrence, credentials/private scope, source/method/profile expansion,
nonzero cost/model use, cumulative attempt 50, or any action outside the
standing Plan 0018 boundary. Stop without asking for a retry on a global
integrity failure, because additional authority cannot make corrupted evidence
acceptable.

Receipt `docs/dev/notes/0033-remaining-x-linkedin-evidence-completion.json`
must add the configured and actual attempt count per job, the retry-eligibility
classification and evidence for each attempt, and cumulative actual/reserved
use against both the 31-attempt packet maximum and 50-attempt standing approval
ceiling. All Version 23 immutable evidence and final-review requirements remain
in force, except its one-attempt/no-retry statements are superseded only by
this section.

### Revised work graph and hard bounds

| State | Authorized action | Exit condition |
| --- | --- | --- |
| `awaiting_retry_policy_plan_review` | plan, code/tests/docs, and read-only Git/runtime/database checks; no install or source work | one fresh reviewer passes after at most one consolidated remediation |
| `remaining_evidence_authorized` | install reviewed patch runtime, then run three exact disabled manual proofs serially with at most two service-owned attempts each | all three identities terminal or the first global stop fires |
| `awaiting_remaining_evidence_final_review` | receipt/docs and read-only validation only | one fresh reviewer passes or fails |
| `awaiting_recurring_enable_gate` | no schedule mutation | a later separately reviewed packet receives explicit approval |

One implementation/review packet, at most one consolidated plan-review
remediation, six maximum source attempts, one terminal receipt review, and at
most one consolidated final-review remediation are the hard bounds. The
primary agent owns all writes, install/runtime commands, proof execution,
receipt construction, and reconciliation. One fresh-context read-only reviewer
audits the implementation/plan before install; another fresh-context read-only
reviewer audits the terminal receipt.

The Version 23 global stops remain, except an eligible service-owned attempt
two and cumulative source attempts through 31 are now expected. Also stop on a
manual retry value other than two, an attempt-three observation, retry without
the eligibility evidence above, timer/spec enablement, installed version or
manifest mismatch after upgrade, or inability to preserve the exact rollback
artifact.

### Checkpoint P0018-C57 | 2026-08-02

Plan version:

- 24

State transition:

- `awaiting_remaining_evidence_operator_gate -> awaiting_retry_policy_plan_review`

Progress classification:

- `blocker_reduction`; the operator gate is consumed, the standing threshold
  is 50, and the requested retry budget is translated into one inspectable
  service-owned retry per remaining identity rather than an unbounded loop.

Authority classification:

- `human_gate`; the operator authorizes the exact standing and
  packet ceilings above. Code/tests/docs may proceed now. Install, restart, and
  live proof work remain conditional on one fresh independent review pass.

Current evidence and design finding:

- `HEAD == origin/main == edc31ec345f9413938b4a8cfeadcdb89b4039d18` and the
  worktree began clean;
- canonical unit `last30days.service` is active/running; installed service
  0.2.26/schema 12 reports ready on manifest
  `21564f14a2c87f3d2ee27013470bdc3642e9d70997facebc726b75c92982c1fb`
  with active index `index-28418bd968076bba6653223f` at 59/59;
- the initial `last30days-service.service` probe was a wrong-unit-name false
  alarm. No runtime drift occurred and the canonical unit readback corrected
  it before planning continued;
- CodeGraph shows `CollectionCoordinator.enqueue_interval` hard-codes manual
  jobs to one attempt and timer jobs to two, so the retry request requires the
  narrow reviewed operator-interface patch above rather than a docs-only
  controller change;
- source candidate service 0.2.27 now preserves the manual default of one,
  accepts only explicit manual values one or two, rejects timer overrides, and
  exposes `collection run --max-attempts {1,2}`. Focused collection/CLI/
  release/runtime-package tests and the complete `uv run pytest` suite pass;
  the deterministic runtime manifest is
  superseded by the remediation manifest recorded below;
- the deterministic authority audit passes with Plan 0018 as the sole active
  plan and latest Runbook Turn 123; `git diff --check` passes;
- all target specifications and recurrence remain disabled. No source, job,
  interval, browser, install, service, or database mutation has run in C57.
- independent reviewer `/root/v23_plan_review` returned one consolidated
  `FAIL`: the first 0.2.27 candidate forwarded two attempts but inherited the
  generic runner's broad rate-limit/transient/content retry decision without
  the Version 24 allowlist and zero-side-effect gate;
- the single permitted remediation makes explicit manual-two jobs retry only
  the four named safe codes with complete zero accepted/stored/deduplicated/
  indexed evidence, writes that classification into the immutable attempt
  receipt, and fails expired leases without a complete receipt as
  `manual_retry_evidence_missing`. Generic refresh and timer retry behavior is
  unchanged;
- six focused manual-retry cases cover eligible timeout, rate-limit/content
  rejection, unexpected internal error, missing counts, and unreceipted lease
  expiry. Focused collection/job-runner/supervisor/CLI/release/runtime tests and
  the full suite pass after remediation. Refreshed runtime-manifest SHA-256 is
  `560fa57c8a1cd0d0eb0b7c630ddab7d3944ed5725b6c2e6fe6d3790cfd0237cb`.

Delegation decision:

- `pending`; reuse `/root/v23_plan_review` for one bounded read-only review of
  the Version 24 plan and implementation after tests pass. The primary keeps
  the critical-path implementation and all mutation authority local.

Next action:

- commit the one consolidated remediation and return it to the same independent
  reviewer for a terminal recheck. Do not install or run a proof before the
  review passes.

### Checkpoint P0018-C58 | 2026-08-02

Plan version:

- 24

State transition:

- `awaiting_retry_policy_plan_review -> remaining_evidence_authorized`

Progress classification:

- `blocker_reduction`; the reviewed 0.2.27 retry controller is now eligible for
  installation and the three remaining disabled-specification proofs.

Authority classification:

- `human_gate`; the operator's standing 50-attempt approval and six-attempt
  packet passed the required independent review. This checkpoint authorizes
  installation of the exact reviewed artifact and the three Version 24 proofs
  under the 31/76/1,307/2,640/zero packet maxima. It does not authorize push,
  tag, external publication/release, recurrence, or any scope expansion.

Independent review and reconciliation:

- reviewer `/root/v23_plan_review` initially returned one consolidated `FAIL`
  at commit `1a8df29`: the manual-two interface inherited generic broad retry
  classes without the plan's allowlist and zero-side-effect gate;
- the single remediation at `bc2ad45` added the exact allowlist, complete
  zero-side-effect gate and receipt evidence, fail-closed unreceipted lease
  expiry, and focused tests while preserving generic refresh/timer behavior;
- the same reviewer returned terminal `PASS` with no critical finding. It
  independently reproduced all retry classes, receipt fields, default/CLI/
  timer semantics, same-job identity, release metadata, 54 focused tests, full
  suite exit zero, authority audit, and unchanged installed/live state.

Reviewed artifact and install boundary:

- source candidate service is 0.2.27; runtime-manifest SHA-256 is
  `560fa57c8a1cd0d0eb0b7c630ddab7d3944ed5725b6c2e6fe6d3790cfd0237cb`;
- reproducible artifact
  `dist/service/last30days-service-0.2.27.tar.gz` has SHA-256
  `34e71d4b205f9a262647718b5ad9417758e54c879fb05d1eb3a8566fc686402b`;
- installed service remains 0.2.26/schema 12 until the next action. The
  reviewer confirmed SQLite `ok`, 37 specs/zero enabled, zero proposed
  intervals, and zero active profile leases.

Delegation status and reconciliation:

- `completed`; `/root/v23_plan_review` supplied the bounded FAIL/recheck PASS
  sequence. The primary accepted the sole finding and verified the terminal
  result. No delegated write or runtime mutation occurred.

Next action:

- commit C58 locally, install the exact reviewed artifact with rollback
  preservation, validate installed 0.2.27/schema 12 and all invariants, then
  run the three proofs serially. Do not push or enable recurrence.

### Checkpoint P0018-C59 | 2026-08-02

Plan version:

- 24

State transition:

- `remaining_evidence_authorized -> awaiting_x_auth_operator`

Progress classification:

- `human_gate`; exact 0.2.27 is installed and healthy, and the first X proof
  stopped before content processing because the retained browser requires
  manual authentication.

Authority classification:

- `human_gate`; Version 24 authorizes only the four named zero-side-effect
  transient retry classes. `auth_required` is an operator outcome and is not
  retry eligible. The remaining LinkedIn lanes stay `not_run` until the X lane
  closes under a reviewed successor disposition.

Installed and live evidence:

- exact artifact SHA-256
  `34e71d4b205f9a262647718b5ad9417758e54c879fb05d1eb3a8566fc686402b`
  installed service 0.2.27/schema 12 with rollback 0.2.26; canonical systemd
  state is active/running;
- preflight passed SQLite `ok`, zero foreign-key rows, 37 specifications/zero
  enabled, zero active profile leases, and active index
  `index-28418bd968076bba6653223f` at 59/59 across all four governed counts;
- X run `collection-run-fc6cfa3530bb442ff277c09b8b9a2bc0`, job
  `8808aca5-396d-4f9b-bbd5-192af6cad623`, attempt one stopped
  `awaiting_operator/auth_required`. Its immutable receipt records one network
  request, zero attempted/observed/accepted/rejected/stored/deduplicated/
  indexed items, retry ineligible, and complete zero-side-effect counts;
- no retry or LinkedIn attempt ran. Cumulative attempt use is now 26, packet
  use is one of six, and the standing ceiling remains 50;
- corpus/index counts and historical-row digest
  `696f5192e01196942687e53ed66aca28411665314acb4d11d981539a2d6842de`
  remain unchanged. Receipt is
  `docs/dev/notes/0033-remaining-x-linkedin-evidence-completion.json`;
- agent-browser read-only diagnostics show the retained browser and X tab are
  healthy, but its RDP route is detached. The local dashboard at
  `http://127.0.0.1:4848/` recommends
  `service_remote_view_browser_reattach`; public operator ingress was not
  claimed ready.

Next action:

- the operator reattaches the retained browser through the local dashboard,
  authenticates X manually without sharing credentials, and reports
  completion. Do not resume the job, spend attempt two, start LinkedIn, push,
  or enable recurrence until that human action and the exact successor
  disposition are recorded.

### Checkpoint P0018-C60 | 2026-08-02

Plan version:

- 25

State transition:

- `awaiting_x_auth_operator -> x_profile_handoff_regression_active`

Progress classification:

- `blocker_reduction`; operator correction disproves C59's login conclusion.
  X is already authenticated under `last30days-facebook`, and both user-scoped
  configuration surfaces contain that canonical binding.

Authority classification:

- `inherited_authority`; this is one bounded no-source successor repair under
  the standing evidence-completion goal. It may change the X adapter,
  user-scoped stable-config resolver, focused tests, release metadata, and
  governing docs. It may not consume a source attempt, navigate a browser,
  inspect credentials/cookies/private content, install or restart the service,
  resume the held job, run LinkedIn, push, or enable recurrence before one
  independent review pass.

Changed assumption and current evidence:

- `~/.config/last30days/.env` sets X profile/session to
  `last30days-facebook`; `~/.config/last30days/agent-browser.json` records X
  profile `last30days-facebook` and the stable remote-headed/RDP posture;
- `~/.agent-browser/config.json` marks `last30days-facebook` authenticated for
  X, Facebook, and LinkedIn with X readiness `fresh`; the exact no-launch X
  access plan selects it with no manual action or seeding requirement;
- the last30days stable target file is currently write-only: acquisition
  records it but does not load it as the durable fallback;
- the X adapter drops `workspace.operator_url` on `auth_required`, and the
  shared-owner fast path prefers a generic stream URL over agent-browser's
  direct external `publicOperatorUrl`. Therefore C59's localhost dashboard
  handoff was not a valid product outcome.

Bounded execution packet:

1. Add a deterministic red test proving X reads the stable user-scoped target
   profile/posture when per-run overrides are absent.
2. Add a deterministic red test proving an X operator failure retains a direct
   external Guacamole URL and never substitutes a localhost/dashboard URL.
3. Implement the narrow resolver and operator-URL propagation, preserving
   explicit env/per-run precedence and excluding runtime browser/session/route/
   display leases from persistent configuration.
4. Run focused config/X/worker/browser tests, full suite, package boundary,
   manifest/artifact validation, and one independent read-only review.

Bounds and terminal conditions:

- maximum implementation attempts: 2; review/rework cycles: 1; concurrency: 1;
- no network/source attempts, browser navigation, installed-runtime mutation,
  or profile mutation in this packet;
- stop at terminal PASS, a cross-repository agent-browser requirement, an
  unresolved critical review finding, or repeated failure at the bounds.

Next action:

- write and run the two regression tests red, then implement the smallest
  repo-local fix. Do not use or present a localhost dashboard URL as the human
  interaction contract.

Implementation and validation evidence:

- the initial focused loop failed four exact assertions: no stable target
  loader, no X failure `operator_url`, no durable fallback use, and localhost
  URL selected ahead of `publicOperatorUrl`;
- candidate service 0.2.28 adds an allowlisted, schema-checked stable target
  reader; explicit run/environment values remain higher precedence and runtime
  browser/session/route/display state remains excluded;
- X auth/checkpoint failures retain the workspace operator URL in direct and
  service diagnostics; shared-owner acquisition uses only the external
  `publicOperatorUrl`/`externalUrl` chain for human handoff;
- focused config/X/Facebook/worker/release/runtime-package tests pass. The first
  full suite reached 2,430 passed, 7 skipped, and 6 subtests passed with one
  governance-only failure caused by the stale plan header; no product test
  failed;
- runtime-manifest SHA-256 is
  `8b8d66fc9253c973be58b4dc929563a5c4926995976d9e1825114a8db591e365`;
  artifact `dist/service/last30days-service-0.2.28.tar.gz` has SHA-256
  `da506f2b0db4b9a002056839f9bf9bfc024d1b82ac2535155b50c32a28fa72b4`.

Review gate:

- rerun the authority audit and full suite after this header reconciliation,
  commit the bounded candidate locally, then request one independent read-only
  review. Installation, job resume, and source work remain closed pending PASS.

### Checkpoint P0018-C61 | 2026-08-02

Plan version:

- 25

State transition:

- `x_profile_handoff_regression_active -> x_successor_proof_authorized`

Progress classification:

- `blocker_reduction`; independent review returned terminal PASS and exact
  service 0.2.28 is installed healthy with rollback 0.2.27.

Authority classification:

- `inherited_authority`; the prior failed run remains immutable and is not
  resumed. One fresh X successor identity is authorized under the standing
  50-attempt approval, cumulative packet ceiling 31, and remaining five packet
  attempts. No new source, profile, credential, audience, cost, or mutation
  class is introduced.

Review and installed evidence:

- reviewer `/root/v23_plan_review` returned terminal `PASS` on commit
  `1ecad89411fdc3653ef6928a8270e0566ca39a8f` with no critical findings;
- primary full suite passed 2,431 tests, 7 skipped, and 6 subtests; reviewer
  independently passed the full 2,438-test collection, focused tests,
  authority audit, artifact reproducibility, and clean-worktree checks;
- installed service is 0.2.28/schema 12, runtime-manifest SHA-256
  `8b8d66fc9253c973be58b4dc929563a5c4926995976d9e1825114a8db591e365`,
  active/running with rollback 0.2.27 and active index 59/59;
- all 37 collection specifications remain disabled. Exact no-launch X access
  planning selects `last30days-facebook`, reports no manual action/seeding,
  and requests runtime profile `last30days-facebook`.

Successor proof controller:

- command: installed `collection run p0018-v17-x-browser-manual` with
  `--scheduled-for 2026-08-02T21:20:00Z --max-attempts 2`;
- this is one fresh durable run/job identity, not a resume or rewrite of
  `8808aca5-396d-4f9b-bbd5-192af6cad623`;
- attempt two remains restricted to the reviewed four-code transient allowlist
  and complete zero-side-effect receipt gate;
- stop before LinkedIn on auth/checkpoint, route/integrity failure, unexpected
  side effects, or incomplete receipt evidence.

Next action:

- commit this successor authority locally, execute the one X proof serially,
  and inspect its immutable receipt before any further lane.

### Checkpoint P0018-C62 | 2026-08-02

Plan version:

- 25

State transition:

- `x_successor_proof_authorized -> x_distinct_interval_successor_authorized`

Progress classification:

- `no_progress`; the C61 command made no source call. Daily interval
  canonicalization mapped `2026-08-02T21:20:00Z` to the existing Aug 1-2 run
  and returned its immutable held job with attempts still one of two.

Authority classification:

- `inherited_authority`; replace only the scheduled identity with the next
  distinct daily boundary `2026-08-03T00:00:00Z`. It creates the Aug 2-3
  interval, remains inside the same public X/profile/resource envelope, and
  does not resume or rewrite the old job.

Next action:

- run the installed collection once at the corrected distinct boundary and
  inspect the new run/job receipt before LinkedIn.

### Checkpoint P0018-C63 | 2026-08-02

Plan version:

- 25

State transition:

- `x_distinct_interval_successor_authorized -> x_profile_handoff_fixed_remote_view_timeout_stop`

Progress classification:

- `partial_progress_terminal_stop`; the repaired installed service consumed the
  canonical user-scoped `last30days-facebook` binding and did not enter an
  authentication or manual-handoff state. The source lane did not complete:
  both reviewed attempts failed on the same agent-browser `remote_view_open`
  timeout with zero accepted or stored items.

Authority classification:

- `inherited_authority`; terminal hard stop: the fresh successor exhausted its
  two-attempt job budget. Do not resume it, create another source attempt, or
  start LinkedIn. Diagnosis of the
  agent-browser route timeout may proceed read-only under inherited authority;
  any new live proof requires a successor checkpoint.

Immutable evidence:

- receipt `docs/dev/notes/0034-x-profile-handoff-repair-and-successor-stop.json`;
- run `collection-run-83b9f1b2b0125764b077068eef285cdd`, job
  `e227749c-d01e-47c5-a406-0aa9496c4a05`, attempts two/max two, terminal
  `failed/agent_browser_error`;
- both acquisitions used profile `last30days-facebook`; neither reported
  `auth_required` or requested a human handoff;
- both agent-browser operations stopped at `remote_view_open` with the same
  timeout and failure signature;
- counts stayed zero, active index stayed 59/59, database integrity passed,
  and no profile lease remained;
- cumulative attempt count is 28 of the standing 50; this packet used three of
  six attempts and has three unconsumed attempts. LinkedIn is `not_run`.

Next action:

- diagnose the agent-browser `remote_view_open` timeout without another source
  attempt. Do not ask the operator to log in and do not provide a localhost
  handoff URL; any genuine future handoff must use agent-browser's external
  Guacamole URL.

## Version 26 | Installed agent-browser gate and one fresh X successor

### Bounded outcome and inherited authority

Agent-browser P90 has repaired the C63 route-bound visible-window proof and the
exact reviewed executable is installed, provenance-converged, and live-proven.
Authorize one separately reviewed fresh X proof identity under the operator's
standing 50-attempt threshold. This successor stays on the existing disabled
`p0018-v17-x-browser-manual` specification, X topic `OpenAI`, exact
`agent_browser` method, durable `last30days-facebook` profile, zero-cost/model
boundary, and concurrency one.

Do not resume or rewrite run
`collection-run-83b9f1b2b0125764b077068eef285cdd` or job
`e227749c-d01e-47c5-a406-0aa9496c4a05`; their two-attempt budget is exhausted
and immutable. The fresh successor uses scheduled boundary
`2026-08-04T00:00:00Z`, covering the distinct Aug 3-4 interval. Current public
collection readback ends at the Aug 2-3 failed interval, so the proposed
identity is unowned.

Submit the new manual run with `--max-attempts 2`. Attempt two remains service-
owned and eligible only under Version 24's four-code transient allowlist plus
complete zero-side-effect receipt gate. Starting cumulative actual use is 28;
this successor can reach at most 30 of the standing 50. It consumes at most two
of Version 24's three unconsumed packet attempt slots and therefore does not
raise the existing 31-attempt, 76-item, 1,307-request, 2,640-second, zero-cost/
model, concurrency-one maxima. No recurrence or specification enablement is
authorized.

### Installed gate evidence and exact caller contract

- agent-browser source and public fork are at commit `7dd12436`; installed
  executable SHA-256 is
  `a99728c56a57a80bd89ad1bc4e8c8d4a1d1af7bc08e2d52919ea0e384a5d7211`;
- install doctor passes with zero issues, one converged live daemon, a ready
  dashboard, and no stale or diagnostic runtimes;
- remote-view doctor is ready with route displays `:10` and `:11` accessible,
  the route pool ready, and external Guacamole ingress ready;
- one disposable installed-binary Route B gate loaded the existing dashboard
  through `guacamole:2`, returned the direct external Guacamole route, and
  aligned target, route, display, `browser_window_visible`, operator-visible,
  and attachability proof before clean close; post-close doctor stayed ready
  and no route allocation remained;
- the repository fixture harness separately reached the repaired visible-
  window proof but blocked its own in-process HTTP fixture while synchronously
  waiting on the CLI child. That navigation-only harness defect cleaned up and
  is not treated as product-path success or as a source attempt;
- installed last30days service 0.2.28/schema 12 is active/running and ready on
  runtime manifest
  `8b8d66fc9253c973be58b4dc929563a5c4926995976d9e1825114a8db591e365`,
  with active index 59/59 and 37 specifications/zero enabled;
- the exact no-launch access plan must be called with runtime profile
  `last30days-facebook`. With that durable binding it selects the same profile,
  carries X in `authenticatedServiceIds`, carries an X `fresh` readiness row,
  requests remote-headed/RDP/private-display posture, and requires neither
  manual action nor manual seeding. A generic plan without the durable caller
  binding selects the default profile and is not acceptable evidence.

Receipt
`docs/dev/notes/0035-agent-browser-installed-gate-and-x-successor-review.json`
binds this installed gate, caller contract, proposed identity, and attempt
arithmetic.

### Review, execution controller, and hard stops

This is review-first inherited authority. Commit the docs-only candidate and
obtain one fresh-context independent read-only review. On PASS, add a separate
authorization checkpoint before submitting the installed command exactly once:

`last30days-service collection run p0018-v17-x-browser-manual --scheduled-for
2026-08-04T00:00:00Z --max-attempts 2`.

Before submission re-read service/systemd readiness, exact installed manifest,
the target specification and proposed interval owner, all enabled states,
profile leases, SQLite/integrity, corpus/current-version completeness, active-
index membership, agent-browser doctors, explicit runtime-profile access plan,
and cumulative use. Inspect the new immutable run/job receipt to terminal state
before deciding any later lane. LinkedIn remains `not_run` in this packet.

Stop without another source attempt on review failure; identity collision;
profile other than `last30days-facebook`; generic-profile fallback; manual
retry; attempt three; ineligible retry; authentication, checkpoint, selector,
route, display, operator-URL, receipt, database, index, integrity, cost/model,
or ownership drift; missing side-effect counts; enabled specification; or any
cumulative/packet maximum breach. If a genuine human handoff is required,
preserve only agent-browser's direct external Guacamole URL; never return a
localhost or dashboard URL.

### Checkpoint P0018-C64 | 2026-08-02

Plan version:

- 26

State transition:

- `x_profile_handoff_fixed_remote_view_timeout_stop -> awaiting_x_successor_plan_review`

Progress classification:

- `blocker_reduction`; the cross-repository route-bound proof defect is fixed,
  installed, and live-proven without consuming a last30days source attempt.

Authority classification:

- `inherited_authority`; planning, deterministic validation, commit, and one
  fresh-context read-only review are authorized under the standing Plan 0018
  goal and attempt threshold. No source attempt is authorized before PASS and
  a separate pre-live checkpoint.

Current evidence:

- receipt 0035 records the agent-browser source/install identities, both ready
  doctors, successful direct Route B product gate, fixture-only navigation
  limitation, cleanup, and exact durable-profile access-plan result;
- the last30days service remains ready at 0.2.28/schema 12, active/running,
  active index 59/59, all sources ready, and 37 specifications/zero enabled;
- the failed Aug 2-3 X run remains immutable, cumulative use remains 28 of 50,
  and no source attempt, new run, job, interval, profile lease, or schedule
  mutation ran while creating C64.

Delegation decision:

- `pending`; reuse `/root/v23_plan_review` for one bounded fresh-context read-
  only review. The primary retains every write and all runtime/source mutation.

Next action:

- validate and commit C64, then request the independent review. Do not submit
  the Aug 3-4 X identity or start LinkedIn before terminal PASS and a separate
  authorization checkpoint.

### Checkpoint P0018-C65 | 2026-08-02

Plan version:

- 26

State transition:

- `awaiting_x_successor_plan_review -> awaiting_x_successor_remediation_recheck`

Progress classification:

- `blocker_reduction`; independent review caught that the installed 0.2.28 X
  caller still relied on ambient broker selection before a live attempt, and
  the one bounded remediation now binds the requested profile explicitly.

Authority classification:

- `inherited_authority`; code, tests, release candidate construction, docs,
  commit, and terminal read-only recheck remain inside the same approved X/
  profile/service mutation class. Installation and source work remain closed
  until recheck PASS and a separate pre-live checkpoint.

Independent review and exact defect:

- reviewer `/root/v23_plan_review` returned one consolidated `FAIL` at exact
  commit `1f6b6c4`: `CliAgentBrowserClient.acquire_workspace` passed X target,
  browser, display, and stream hints to `agent-browser service access-plan`,
  but omitted `--runtime-profile request.profile_id`;
- service 0.2.28 therefore compared the broker's returned selection with
  `last30days-facebook` but did not durably constrain planning to that profile.
  Ambient target configuration happened to select the correct row, which is
  insufficient under Version 26's exact caller contract;
- the reviewer passed all other authority, identity, arithmetic, retry,
  runtime, cleanup, integrity, and external-handoff checks and performed no
  mutation or source/browser action.

One bounded remediation:

- the public adapter-boundary regression adds an exact assertion that the
  access-plan command contains `--runtime-profile last30days-facebook`;
- red command
  `uv run pytest tests/test_x_browser.py -q -k
  acquisition_resolves_the_authenticated_x_profile_by_target_identity`
  failed because the flag was absent;
- the minimal implementation forwards `request.profile_id` in that access-plan
  call; the same command then passed, and the full X test file passed;
- service candidate is 0.2.29 with runtime-manifest SHA-256
  `32bff26cf96a277a1c3d9bdf59c5fcc0ed7235eeb744dcad5cdcb11e2d22902a`;
  reproducible artifact
  `dist/service/last30days-service-0.2.29.tar.gz` has SHA-256
  `b623e4c95c577356758b7745f105cb887ddd420e1d950ab6040ce298dbbaa17d`;
- focused X/release/runtime-package tests pass. The complete suite passes with
  2,431 tests, 7 skipped, and 6 subtests. Authority audit, JSON validation, and
  `git diff --check` remain required on the committed candidate;
- installed service remains unchanged at 0.2.28. No install, restart, source,
  browser, profile, schedule, run, job, interval, lease, database, or index
  mutation occurred in the remediation.

Delegation status and reconciliation:

- `remediation_ready`; return the exact committed candidate to
  `/root/v23_plan_review` for the single terminal recheck. The one allowed
  remediation cycle is consumed; any remaining critical finding stops this
  packet for split or reframe.

Next action:

- validate and commit C65, then request the terminal independent recheck. Do
  not install 0.2.29 or submit the Aug 3-4 X identity before PASS and a separate
  pre-live authorization checkpoint.

### Checkpoint P0018-C66 | 2026-08-02

Plan version:

- 26

State transition:

- `awaiting_x_successor_remediation_recheck -> x_successor_install_and_proof_authorized`

Progress classification:

- `blocker_reduction`; the durable caller binding now has one independent
  terminal PASS and an exact installable artifact.

Authority classification:

- `inherited_authority`; install exact reviewed service 0.2.29 with rollback
  preservation, validate every preflight invariant, then submit the one fresh
  Aug 3-4 X identity under the Version 26 controller. This does not authorize a
  second run identity, manual retry, LinkedIn, recurrence, push, tag,
  publication, or release.

Terminal independent recheck:

- reviewer `/root/v23_plan_review` returned `TERMINAL PASS` on exact clean
  commit `dfefca5fb43e178e7e27369ef09dfba1fe918a30` with no remaining critical
  finding;
- the reviewer independently proved the access-plan command forwards
  `request.profile_id` as `--runtime-profile` before validating the broker's
  selected profile, while preserving the mismatch guard;
- it reproduced the regression's red/green sensitivity, focused tests, full
  suite exit zero, manifest/artifact contents and hashes, authority audit,
  JSON, diff, and clean-worktree checks;
- its live readback kept installed service 0.2.28/schema 12 ready on 59/59,
  37 specs/zero enabled, SQLite `ok`/FK0, zero profile leases, zero proposed-
  interval owners, exact `last30days-facebook` fresh/no-manual access planning,
  and healthy agent-browser install/remote-view convergence;
- no install, browser, source, collection, config, service, database, or index
  mutation occurred during review.

Exact install and live boundary:

- install only artifact
  `dist/service/last30days-service-0.2.29.tar.gz`, SHA-256
  `b623e4c95c577356758b7745f105cb887ddd420e1d950ab6040ce298dbbaa17d`,
  runtime manifest
  `32bff26cf96a277a1c3d9bdf59c5fcc0ed7235eeb744dcad5cdcb11e2d22902a`;
- require installed 0.2.29/schema 12 active/running and ready with rollback
  0.2.28, exact manifest, SQLite/integrity, 59 current-version embedding
  documents, active index 59/59, 37 specs/zero enabled, zero leases, zero
  proposed-interval owners, and both agent-browser doctors ready;
- require the explicit no-launch access plan with runtime profile
  `last30days-facebook` to select that profile with X fresh/authenticated and no
  manual action or seeding;
- only then submit installed `collection run p0018-v17-x-browser-manual
  --scheduled-for 2026-08-04T00:00:00Z --max-attempts 2` once and inspect its
  immutable run/job/attempt evidence to terminal state before any new plan.

Delegation status and reconciliation:

- `completed_pass`; the same reviewer supplied the bounded FAIL/rework/
  terminal-PASS sequence. The primary reproduced the defect and red/green fix,
  ran the complete suite, and accepts the terminal result. All writes and live
  operations remain primary-owned.

Next action:

- commit C66 locally, install exact 0.2.29, validate installed and external-
  route invariants, then submit the one X successor exactly once. Stop on the
  first Version 26 hard stop and do not start LinkedIn.

### Checkpoint P0018-C67 | 2026-08-02

Plan version:

- 26

State transition:

- `x_successor_install_and_proof_authorized -> awaiting_x_successor_final_review`

Progress classification:

- `blocker_reduction`; exact installed service 0.2.29 forwarded the durable
  `last30days-facebook` binding, agent-browser completed its route-bound display
  operation, and the fresh X identity published on attempt one. The result is
  healthy zero yield, not content yield.

Authority classification:

- `inherited_authority`; receipt/docs and read-only validation only until one
  fresh independent reviewer passes or fails. Do not submit LinkedIn, retry X,
  enable recurrence, push, tag, publish, or release.

Installed and live evidence:

- exact artifact `dist/service/last30days-service-0.2.29.tar.gz`, SHA-256
  `b623e4c95c577356758b7745f105cb887ddd420e1d950ab6040ce298dbbaa17d`,
  installed ready on schema 12 and runtime-manifest SHA-256
  `32bff26cf96a277a1c3d9bdf59c5fcc0ed7235eeb744dcad5cdcb11e2d22902a`;
  rollback is 0.2.28;
- the installed no-launch access plan selected durable profile
  `last30days-facebook`, retained fresh authenticated X evidence, and requested
  no manual action or seeding;
- the one authorized command created run
  `collection-run-256fafac6f64847cbca3130a4dede6aa`, job
  `e0cd5bc1-1ca7-4cbb-8a47-d800eee2c004`, for the distinct Aug 3-4 interval;
- attempt one published successfully. Acquisition work
  `work-3b7037305a19b79d55dd6a64468f4617` succeeded through `x_agent_browser`
  with zero items and one governed network request. No retry, model call, cost,
  auth request, manual handoff, or operator URL occurred;
- agent-browser job `r936025` completed `remote_view_open` on
  `guacamole-rdp-a`, route `guacamole:1`, display
  `remote-view-display:10`, with no error;
- immutable attempt-start and collection-receipt envelope SHA-256 values are
  `38d0039e049f422e32a831e4b8e526a8d8f1a1e01e8809ab9a4a9e8dd4b6ae93`
  and `95102331f60023bce5d29b06ebd331af390511bdeeb698c53e5a14795f9c0616`;
- pre/post corpus and index snapshots remain identical: SQLite `ok`, FK0,
  59 documents, 59 current-version embedding documents, active index
  `index-28418bd968076bba6653223f` at 59/59, 37 specifications/zero enabled,
  zero profile leases, and exactly one owner for the successor interval;
- cumulative actual attempts move 28 to 29 of 50. Version 24 packet use moves
  three to four of six, leaving two. LinkedIn topic and profile remain
  `not_run`.

Receipt and review boundary:

- `docs/dev/notes/0036-x-successor-healthy-zero-yield.json` is the machine-
  readable terminal receipt;
- one fresh-context independent reviewer must verify exact runtime identity,
  route evidence, immutable run/job/attempt/acquisition evidence, attempt
  arithmetic, and unchanged database/index/spec/lease state;
- this result proves the repaired route/profile/caller path and a healthy
  zero-yield terminal outcome. It does not prove current X selector content
  yield.

Next action:

- commit C67 locally and request the one fresh read-only final receipt review.
  Stop before LinkedIn.

### Checkpoint P0018-C68 | 2026-08-02

Plan version:

- 26

State transition:

- `awaiting_x_successor_final_review -> x_successor_evidence_accepted`

Progress classification:

- `acceptance`; the independently reviewed X result closes the repaired
  profile/caller/agent-browser route packet as healthy zero yield. It does not
  claim current selector content yield.

Authority classification:

- `inherited_authority`; planning, deterministic validation, and read-only
  review for a bounded LinkedIn successor are permitted. No LinkedIn live run,
  X retry, recurrence, push, tag, publication, or release is authorized by
  this checkpoint.

Fresh independent final review:

- reviewer `/root/v26_x_final_review` returned `TERMINAL PASS` on exact clean
  commit `ecaf40d` with zero critical findings and no runtime/source mutation;
- the reviewer independently matched installed service 0.2.29/schema 12,
  exact manifest/artifact/rollback, active/running readiness, agent-browser
  source/install identities, both ready doctors, and successful job `r936025`
  on `guacamole:1`/`remote-view-display:10`;
- it matched the run, job, attempt, acquisition, all five recomputed envelope
  hashes, zero content counts, one request, zero model calls/cost, and retry
  class `none`;
- live access planning selected `last30days-facebook` with X fresh, no manual
  action/seeding, and no auth/manual/operator-URL terminal evidence;
- SQLite `ok`/FK0, 37 specs/zero enabled, zero leases, 59/59 current embedding
  and active-index completeness, one interval owner, and no later LinkedIn
  attempt all passed;
- cumulative actual arithmetic 28 to 29 of 50 and Version 24 packet use three
  to four of six, leaving two, passed independently.

Accepted result and remaining boundary:

- receipt `docs/dev/notes/0036-x-successor-healthy-zero-yield.json` is accepted
  as the terminal source-backed record;
- X is not retried. LinkedIn topic and profile remain `not_run`; all 37
  specifications remain disabled;
- because the Version 24 packet has only two attempts remaining, the next
  successor must explicitly allocate those attempts, preserve serial
  execution and the standing ceiling 50, receive independent review, and stop
  before any live run unless separately authorized by a later checkpoint.

Next action:

- derive the bounded review-first LinkedIn topic/profile successor from the
  accepted X receipt. Do not execute it in this checkpoint.

## Version 27 | Reset proof-budget epoch and complete zero-yield observability

Version 27 consumes the operator's explicit request to reset the budget
counters, finish the remaining zero-yield observability passes, and then plan
and execute blinded-yield service canaries. The reset starts a new governed
ledger epoch; it does not delete, rewrite, renumber, or conceal any immutable
service run, attempt, receipt, or historical plan evidence.

Budget epoch `p0018-v27-e2`:

- lifetime actual attempt evidence remains 29 and is reported beside, not
  inside, the reset epoch;
- the Version 24 packet retires at four of six attempts used. Its two unused
  attempts do not carry into the new epoch;
- epoch counters start at zero with ceilings of 50 attempts, 150 accepted
  items, 2,500 governed requests, 6,000 wall seconds, zero cost, zero model
  calls, and concurrency one;
- this LinkedIn observability packet reserves no more than four attempts, six
  accepted items, 100 governed requests, 240 wall seconds, zero cost, zero
  model calls, and concurrency one.

Remaining observability controller:

1. Execute the disabled LinkedIn topic specification first, then the disabled
   LinkedIn profile specification, both for the fresh Aug 3-4 interval and
   each submitted once with service-owned `--max-attempts 2`.
2. The service may consume attempt two only for `worker_timeout`,
   `agent_browser_timeout`, `agent_browser_error`, or `route_stale` after a
   complete attempt with zero side effects. Manual requeue and attempt three
   are forbidden.
3. Before the first lane, close only the currently owned X browser session for
   `last30days-facebook`. Do not clean unrelated default, LitScout, retained-
   display, route, or browser state.
4. Before each lane, require installed service 0.2.29/schema 12 ready, SQLite
   `ok`/FK0, 59/59 current embedding and active-index completeness, 37 specs
   with zero enabled, zero service profile leases, no owner for the proposed
   identity, exact `agent_browser` access planning on
   `last30days-facebook`, fresh authenticated source evidence, ready remote
   view, and no manual action or seeding.
5. Poll the service-owned job to a terminal immutable receipt. Proceed from
   topic to profile only if the first lane preserves every global integrity
   invariant. Healthy zero yield is a successful observability result; it is
   not content-yield proof.
6. If human interaction becomes necessary, expose only the direct external
   Guacamole client URL supplied by agent-browser. A localhost or local
   dashboard URL is never an operator handoff.

The blinded-yield canary campaign is a distinct successor packet. It may be
planned after both observability lanes reach terminal evidence, but no canary
source operation is authorized until that plan has a sealed expectation
contract, independent review, and its own pre-live checkpoint.

### Checkpoint P0018-C69 | 2026-08-03

Plan version:

- 27

State transition:

- `x_successor_evidence_accepted -> awaiting_linkedin_observability_plan_review`

Progress classification:

- `authority_and_budget_reset`; the remaining zero-yield observability work is
  bounded under a fresh counter epoch without altering historical evidence.

Authority classification:

- `human_gate`; the operator explicitly authorized the
  reset and requested execution, but this checkpoint permits documentation,
  deterministic validation, and one fresh independent read-only review only.
  No LinkedIn browser/source run is permitted before review PASS and a separate
  pre-live checkpoint.

Machine-readable controller:

- `docs/dev/notes/0037-budget-epoch-reset-and-linkedin-observability-plan.json`
  records the epoch, immutable lifetime total, retired packet, fresh counters,
  lane budgets, retry allowlist, installed-service facts, owned browser
  transition, handoff contract, and pending review.

Hard stops:

- stop on review FAIL, a preflight mismatch, an existing interval owner,
  source/profile mismatch, auth staleness, non-external handoff, unauthorized
  retry, receipt/hash incompleteness, database/index mutation outside the
  lane's published items, cost/model activity, or any global integrity failure;
- keep recurrence, all specification enablement, X retry, push, tag,
  publication, release, and blinded-yield execution closed.

Next action:

- validate and commit C69 locally, obtain one fresh independent read-only
  plan review, and stop before live work unless it passes and C70 explicitly
  opens the two serialized LinkedIn lanes.

### Checkpoint P0018-C70 | 2026-08-03

Plan version:

- 27

State transition:

- `awaiting_linkedin_observability_plan_review -> linkedin_observability_live_authorized`

Progress classification:

- `blocker_reduction`; the fresh budget epoch and two-lane controller passed
  independent review with no critical finding.

Authority classification:

- `human_gate`; the operator's explicit execute instruction plus the C69
  terminal review PASS authorizes the exact serialized disabled LinkedIn topic
  then profile packet. Authority is consumed one submitted identity at a time.

Fresh independent plan review:

- reviewer `/root/v27_linkedin_plan_review` returned `TERMINAL PASS` on exact
  clean commit `971d045d72fc` with zero critical findings and no mutation;
- it matched epoch `p0018-v27-e2` at 0/50, immutable lifetime evidence 29,
  retired Version 24 use four of six with zero carry, per-lane max two and
  packet max four attempts, exact service-only retry allowlist, zero-side-
  effect retry precondition, serial ordering, and all closed non-goals;
- it independently matched installed service 0.2.29/schema 12, exact manifest
  and rollback, active/running readiness, SQLite `ok`/FK0, 59/59 current and
  active-index completeness, 37 specs/zero enabled, zero service profile
  leases, and zero proposed-interval owners;
- both disabled specs use exact `agent_browser`, profile
  `last30days-facebook`, and their expected selectors and 50-request/120-second
  limits;
- the exact LinkedIn no-launch access plan selected the fresh authenticated
  profile with no manual action/seeding or duplicate pressure. It correctly
  waits on the one owned X lease, whose ready route exposes the direct external
  Guacamole URL rather than the localhost embed URL.

Exact live controller:

1. Revalidate service, database, index, specification, interval-owner,
   agent-browser doctor, profile, and external-route facts.
2. Close only session `last30days-facebook`, currently owned by
   `last30days/x-scraper/x-search`, then require its lease to clear. Do not use
   `--all`, garbage collection, retained-state pruning, or unrelated cleanup.
3. Submit `p0018-v17-linkedin-topic-browser-manual` once for
   `2026-08-04T00:00:00Z` with `--max-attempts 2`; poll its service-owned job
   to terminal evidence and stop on any Version 27 hard stop.
4. Only if topic preserves every global invariant, require its profile lease
   to clear and submit the profile spec with the same timestamp and attempt
   bound once. Do not manually requeue either identity.
5. Record both terminal outcomes and epoch consumption, then require one fresh
   independent final receipt review before accepting the packet or planning
   blinded-yield canaries.

Next action:

- commit C70 locally, revalidate the exact preflight, close only the owned X
  session, and execute the topic lane. Keep the profile lane conditional on
  topic integrity and stop before blinded-yield planning until both lanes have
  terminal evidence.

### Checkpoint P0018-C71 | 2026-08-03

Plan version:

- 27

State transition:

- `linkedin_observability_live_authorized -> awaiting_linkedin_observability_final_review`

Progress classification:

- `blocker_reduction`; both remaining observability identities reached complete
  immutable attempt-one terminal receipts without a retry or global integrity
  stop.

Authority classification:

- `inherited_authority`; live source/browser work is closed. Receipt writing,
  deterministic readback, and one fresh independent final review only. Do not
  start blinded-yield planning or any additional source identity before review
  disposition.

Execution evidence:

- after exact preflight, only the owned X session was closed. Topic then
  launched on exact `last30days-facebook` with owner
  `last30days/linkedin-scraper/linkedin-content-search`, fresh auth, no manual
  action/seeding, and a ready external Guacamole route;
- topic run `collection-run-86b8d0fa7f2823b99b4e9838ac7ba27e`, job
  `9e006339-ed8d-4911-af2e-6b304bc99003`, and acquisition
  `work-debb7bd3b1a952b265eb8f8846cd7659` stopped attempt one as source-local
  `quality_gate_failed`: 12 attempted/observed/rejected, zero accepted/stored/
  deduplicated/indexed, one request, zero model calls/cost, and no eligible
  retry. Its start and final receipts preserve identical 59/59 snapshots;
- the owned topic session was closed. Profile preflight again selected the
  exact fresh profile with zero active lease, zero duplicate pressure, no
  manual action/seeding, and zero proposed owner;
- profile run `collection-run-e85a7898dd4a2f96e655f95abf2f14e5`, job
  `4184639c-1c2a-422c-ac02-774e62bba259`, and acquisition
  `work-eb40d12041e553b3d7c5ba82ecd497dc` published on attempt one through
  `linkedin_profile_agent_browser`: one attempted/observed/accepted/stored/
  deduplicated/indexed, one request, zero model calls/cost, and no retry. The
  accepted profile material deduplicated into the existing corpus, leaving the
  active index unchanged at 59/59;
- the final owned profile session was closed. SQLite remains `ok`/FK0, all 37
  specs remain disabled, service profile leases are zero, current-version
  embeddings remain 59/59, and no owned agent-browser session/browser remains.

Budget accounting:

- epoch `p0018-v27-e2` consumed two of 50 attempts, one of 150 accepted items,
  two of 2,500 governed requests, 125.774 of 6,000 wall seconds, zero cost,
  zero model calls, and concurrency one. Immutable lifetime attempt evidence
  advances from 29 to 31;
- neither unused service attempt was consumed or carried into a new packet.

Receipt and review boundary:

- `docs/dev/notes/0038-linkedin-observability-completion-receipt.json` records
  both lanes, all ten immutable envelope hashes, exact counters, snapshots,
  browser ownership transitions, cleanup, and postflight state;
- one fresh-context independent reviewer must recompute the envelope hashes,
  verify run/job/attempt/acquisition identities and arithmetic, and match live
  postflight state before the packet is accepted.

Next action:

- validate and commit C71 locally, then obtain one fresh independent read-only
  final receipt review. Do not plan or execute blinded-yield canaries before
  that review reaches terminal PASS.

### Checkpoint P0018-C72 | 2026-08-03

Plan version:

- 27

State transition:

- `awaiting_linkedin_observability_final_review -> linkedin_observability_evidence_accepted`

Progress classification:

- `acceptance`; the remaining observability packet is independently verified
  and the fresh budget epoch accounting is accepted.

Authority classification:

- `inherited_authority`; planning, deterministic preparation, sealed
  expectation construction, and fresh independent review for a blinded-yield
  service-canary successor are open. No canary source/browser execution is
  authorized until that successor has its own reviewed pre-live checkpoint.

Fresh independent final review:

- reviewer `/root/v27_linkedin_final_review` returned `TERMINAL PASS` on exact
  clean commit `2651c8751ca5a00c2b95365a315ba6db59fe90ef` with zero critical
  findings;
- it recomputed all ten SHA-256 values directly from stored envelope payloads,
  matched every run/job/attempt/acquisition binding and count, verified one
  attempt per identity with no unauthorized retry, and reproduced 125.774342
  wall seconds, two requests, one accepted item, zero model calls/cost, epoch
  use 2/50, and lifetime movement 29 to 31;
- topic's zero-yield `quality_gate_failed` and profile's one accepted/stored/
  deduplicated/indexed publication were classified truthfully with unchanged
  59/59 snapshots;
- live service/runtime/database/index/spec/lease facts matched and persisted
  agent-browser state contained no exact `last30days-facebook` session or
  browser. No manual/local-dashboard handoff or later source action occurred;
- the agent-browser session/browser CLI diagnostic hung and was terminated;
  direct persisted-state inspection supplied the exact final absence proof.
  The primary's authority audit and focused authority test remain green.

Accepted result and successor boundary:

- receipt 0038 is accepted. The zero-yield observability backlog is complete;
  recurrence remains closed and no result is promoted into a timer schedule;
- the next successor must define “blinded yield” precisely, precommit expected
  identities or yield outcomes without exposing the reveal to the executor,
  use only already configured source services and credentials, remain serial
  and disabled, fit epoch `p0018-v27-e2` remaining ceilings, receive fresh
  independent review, and create a separate live authorization checkpoint;
- no canary plan may treat a selector chosen after viewing current source
  results as blinded, and no reveal may be opened before all submitted canary
  identities reach terminal receipts.

Next action:

- commit C72 locally, then derive the review-first blinded-yield service-canary
  successor with a sealed expectation contract. Stop before live canaries.

## Version 28 | Sealed blinded-yield canaries across configured services

Version 28 defines a genuine executor-blinded canary packet for exactly the
five already configured source services. A fresh expectation preparer selected
private outcome classes and accepted-yield ranges from prior immutable evidence
without source traffic, salted each reveal with a random 32-byte nonce, and
returned only public specifications and SHA-256 commitments. The primary
executor has not seen predictions, ranges, nonces, or hints.

Blinding protocol:

1. The public plan fixes five unique disabled specs and execution order Reddit,
   YouTube, X, Facebook, LinkedIn. All use the OpenAI selector; LinkedIn uses
   the exact OpenAI company profile.
2. Each hidden reveal is compact UTF-8 JSON with exact ordered keys
   `collection_spec_id`, `predicted_class`, `accepted_min`, `accepted_max`,
   and `nonce_hex`. Its SHA-256 is committed before any spec mutation or source
   run. A combined hash commits the ordered set.
3. The preparer `/root/v28_blind_commit_preparer` retains all reveal objects
   privately. Neither the executor nor plan reviewer receives them.
4. Reveal is forbidden until every submitted lane is terminal or explicitly
   blocked/skipped. The primary then requests the exact reveal, recomputes all
   hashes, classifies actual outcomes, and measures prediction/range matches.
5. Commitment failure is a terminal integrity stop. Actual source-local
   failure is data and does not invalidate blinding; global integrity failure
   stops the remaining packet before reveal.

Execution controller:

- materialize exactly the five reviewed specs from receipt 0039's artifacts,
  require 37 to 42 specs with zero enabled and exact readback, and leave them
  disabled as evidence;
- run each unique Aug 3-4 identity once with `--max-attempts 1`. No manual or
  service retry exists in this packet;
- execute serially and stop after each receipt to verify service, SQLite,
  current-version embedding and active-index integrity, budgets, method
  provenance, spec state, profile lease, and immutable envelopes;
- a source-local terminal may advance to the next service when every global
  invariant holds. Any global failure stops the packet;
- before X, Facebook, and LinkedIn, require exact target access planning on
  `last30days-facebook`, fresh target readiness, no manual action/seeding,
  duplicate pressure false, and no conflicting lease. Close only the packet-
  owned session between browser lanes;
- if human interaction becomes necessary, expose only agent-browser's direct
  external Guacamole URL. Never expose a localhost/dashboard URL, never reveal
  expectations during a handoff, and do not clean unrelated state.

Packet ceilings are five attempts, 15 accepted items, 250 governed requests,
600 wall seconds, zero cost, zero model calls, and concurrency one. Starting
epoch use is 2/50 attempts, one accepted item, two requests, and 125.774
seconds; maximum post-packet use is 7/50 attempts, 16 accepted items, 252
requests, 725.774 seconds, zero cost/model calls, and lifetime attempts 36.

### Checkpoint P0018-C73 | 2026-08-03

Plan version:

- 28

State transition:

- `linkedin_observability_evidence_accepted -> awaiting_blinded_yield_canary_plan_review`

Progress classification:

- `experiment_design`; public selectors, immutable spec artifacts, hidden
  salted expectations, per-lane commitments, combined commitment, execution
  order, budgets, and reveal rules are fixed before source work.

Authority classification:

- `human_gate`; the operator explicitly requested planning and execution, but
  this checkpoint permits documentation, deterministic validation, and one
  fresh independent read-only plan review only. No spec materialization,
  source/browser run, or reveal is authorized before PASS and C74.

Machine-readable controller:

- `docs/dev/notes/0039-blinded-yield-canary-plan.json` records the public
  controller and opaque commitments;
- exact valid `CollectionSpec` payloads live under
  `docs/dev/notes/0039-blinded-yield-specs/`. Scheduled time and max attempts
  are execution-controller fields, not invalid spec-schema additions.

Closed scope:

- no new service, source, credential, tenant, profile, selector expansion,
  recurring schedule, spec enablement, assessment/model call, concurrency,
  retry, push, tag, publication, release, or unrelated cleanup;
- no source observation was used to choose expectations and no reveal is
  stored in the repo at C73.

Next action:

- validate and commit C73 locally, obtain one fresh independent review of the
  public controller without reveal access, and stop before spec materialization
  unless it passes and C74 opens the exact packet.

### Checkpoint P0018-C74 | 2026-08-03

Plan version:

- 28

State transition:

- `awaiting_blinded_yield_canary_plan_review -> blinded_yield_canary_live_authorized`

Progress classification:

- `blocker_reduction`; the public blinded controller passed independent review
  after one bounded evidentiary-command remediation. The reviewer remained
  blind and found no plan contradiction.

Authority classification:

- `human_gate`; the operator's explicit execute instruction, fixed sealed
  commitments, and terminal plan PASS authorize exact spec materialization and
  the five one-attempt serial identities. Authority is consumed one lane at a
  time and ends before reveal evaluation/final acceptance.

Independent review sequence:

- reviewer `/root/v28_canary_plan_review` initially returned an evidentiary
  `FAIL`, not a plan contradiction: its parser environment lacked the service
  module, its JSON command used a no-output expression, and SQLite/profile
  checks were incomplete;
- one bounded recheck on unchanged clean commit `c2245fe` used exact commands
  and returned `TERMINAL PASS` with zero critical findings;
- all five JSON artifacts parsed and passed `CollectionSpec.from_dict`; file
  hashes, five 64-hex commitments, combined commitment, execution order,
  budgets, methods/profiles/selectors/redaction, lifecycle, reveal gate, hard
  stops, and closed non-goals passed;
- SQLite `ok`/FK0, 37 specs/zero enabled, zero leases, zero V28 specs/runs, 59
  current-version embedding documents, installed service 0.2.29/schema 12 exact
  manifest and active index 59/59, five ready sources, and exact absence of the
  selected profile session/browser passed;
- reviewer received no reveal and performed no mutation, browser/source action,
  preparer contact, or profile lifecycle action.

Exact pre-live sequence:

1. Revalidate the same global state and recompute artifact/commitment hashes.
2. Materialize the five artifacts in execution order through installed
   `collection put`; after every put require disabled exact readback. Before
   source work require exactly 42 specs/zero enabled and zero V28 runs.
3. Submit Reddit once at `2026-08-04T00:00:00Z --max-attempts 1`, poll to
   immutable terminal receipt, validate integrity, then repeat for YouTube.
4. For X, Facebook, and LinkedIn, perform the exact per-target no-launch profile
   gate immediately before submission and close only the packet-owned session
   after its terminal receipt. Continue after source-local outcomes only while
   all global invariants hold.
5. After the fifth terminal/blocked lane, stop source/browser work and request
   the preparer's exact reveal. Do not reveal earlier for any reason.

Next action:

- commit C74 locally, revalidate preflight, materialize exact disabled specs,
  prove 42/0 with zero V28 runs, then execute Reddit first. Stop immediately on
  any Version 28 hard stop.
