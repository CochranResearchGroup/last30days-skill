# Plan 0018 | Service-first software product transition

State: PLANNED
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

Before this plan moves to `OPEN`, derive the S01/S02 architecture packet with
exact file/package ownership, compatibility constraints, install topology,
version handshake, tests, and rollback. Do not begin by moving files.

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

This is a stable transition plan, not yet an implementation packet. To open it:

1. reconcile the terminal outcome of active Plan 0014;
2. inventory current service code that still ships inside
   `skills/last30days/`;
3. freeze the service/client package and version-handshake decision;
4. derive one bounded S01/S02 vertical slice;
5. update the planning audit only if the new product authority requires a
   durable invariant beyond the current single-active-plan rule.

## Definition Of Done

`last30days` is operated and released as intelligence software whose durable
service and MCP interface are the primary product. Skills are optional,
least-privilege agent clients, and direct scraping mechanics are absent from
ordinary agent work.
