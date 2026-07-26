# Plan 0011 | Integrated temporal intelligence service

State: OPEN
Roadmap: P01
Date: 2026-07-25
Predecessors: Plans 0007 and 0010

## Execution State

Plan version: 1
Critical-path owner: primary agent
Execution branch: `main`
Optimization posture: temporal-authority-first vertical slices with bounded
cross-lane joins

Local goal bounds:

- maximum implementation attempts per packet: 2;
- maximum review/rework cycles per packet: 1;
- maximum consecutive hardening-only checkpoints: 2;
- checkpoint after every validated packet and before installed-runtime or
  authenticated-browser mutation;
- one additive database migration per independently reversible schema packet;
- one bounded live canary per source/surface at rollout, with no login,
  checkpoint, CAPTCHA, credential, message, invitation, or connection action;
- no P02 timer, P03 identity promotion, P04 graph projection, P05 answer, or
  P06 stochastic decision may bypass P01 immutable evidence and access
  authority.

## Objective

Deliver the complete P01-P06 product vision as one user-scoped, continuously
hydrated temporal intelligence service:

- immutable post and profile history with complete acquisition provenance;
- governed recurring feed, topic, poster, channel, account, and profile
  collection;
- evidence-backed people, organization, account, claim, event, and temporal
  relationships;
- temporally coherent lexical, semantic, entity, event, and GraphRAG
  retrieval;
- compact MCP discovery, query, monitoring, and dossier surfaces that hide
  browser and scraper mechanics;
- bounded App Intelligence assessment, identity, evaluation, and adapter
  maintenance attached only where deterministic host contracts permit it.

SQLite remains the authoritative corpus, ledger, and temporal decision store.
Graphiti/FalkorDB and semantic indexes are rebuildable, access-partitioned
projections.

## Authority Correction

Plan 0010 is a component contract plan for P06. It is not the execution
authority for the complete product.

This plan is the integrated campaign authority. It activates Plan 0010 only at
four explicit joins:

1. after immutable publication, for bounded content/profile assessment;
2. after deterministic candidate generation, for identity resolution;
3. after deterministic retrieval cases and evidence are recorded, for
   retrieval evaluation;
4. after deterministic failure grouping and repair eligibility, for adapter
   diagnosis and repair.

Plan 0010 cannot independently define temporal evidence, collection coverage,
profile history, graph authority, or agent-facing query behavior.

## Current State

- Packets 1 through 5 are complete at commits `f14b0fa`, `0454e5a`,
  `4ae5095`, `22c8db1`, and `6c6e751`. Packet 6 source is complete at
  `0e7938a`. Schema version 12 adds governed
  recurring collection, profile/identity evidence, bitemporal claims/events,
  recorded retrieval evaluation, and durable graph projection receipts to the
  additive temporal authority, immutable publication, version-scoped
  enrichment/index projections, and deterministic schema-7 replay export.
- The installed user service now runs version 0.2.3 with exact source/install
  parity for pushed commit `b76bb28` against schema 12. Its fresh MCP client
  discovers ten compact tools, and its concrete loopback Graphiti sink
  previously published a durable outbox canary.
- Packet 6 is awaiting an authenticated-browser human gate: Reddit yielded one
  item, YouTube completed successfully with zero yield, and the X browser is
  now correctly route-bound to Guacamole/RDP but its refreshed service-owned
  DOM is signed out. Facebook and LinkedIn post/profile canaries remain
  intentionally unattempted.
- The first live recurring-collection acceptance unit preserved
  `budget_exhausted` and `network_budget_exhausted` terminal receipts, then
  paused its public Reddit spec at immutable revision 3 when the two-attempt
  packet bound was reached. Successful timer yield and restart recovery remain
  unproven.
- Broad recurring hydration remains gated until the authenticated canaries and
  Packet 7 acceptance complete; isolated Plan 0010 execution remains
  prohibited outside the four integration joins.

## Context And Constraints

### Current architecture

- `store.py` owns additive, transactional SQLite migrations through schema
  version 7.
- `CorpusPublisher.record_result()` creates stable document IDs, but overwrites
  `documents`, the ordinal-zero chunk, and embedding state when content
  changes.
- acquisition envelopes and `document_sightings` retain fetch provenance, but
  chunks, entities, relationships, and index membership still point to the
  mutable document projection.
- `RefreshSupervisor` already owns durable jobs, leases, retries, budgets,
  negative cache, and query-level coverage.
- `EnrichmentLoop` already runs independently from acquisition and query
  paths.
- current retrieval has immutable index snapshots with lexical, semantic, and
  entity/relationship evidence, but no bitemporal version, claim, event,
  profile, or access-partition query semantics.
- topics have schedules, but there is no general collection-spec, cursor,
  watermark, coverage-interval, or timer-run authority.
- authenticated post acquisition exists for X, Facebook, and LinkedIn;
  profiles are not first-class source-neutral evidence.
- Plan 0010 defines the required deterministic envelope around stochastic
  work, but its contracts are not implemented.

### Product constraints

- ordinary query clients never operate a browser, wait on scraping, or receive
  prompts, raw provider events, cookie/profile mechanics, or credentials;
- acquisition success is independent from stochastic enrichment success;
- authenticated evidence never crosses its access partition;
- ambiguous identities and contradictory claims remain inspectable;
- absence is asserted only when collection coverage proves the relevant
  surface was observed;
- migrations preserve current live data and support deterministic replay;
- broad recurring hydration remains gated until immutable revisions,
  provenance, access partitions, and coverage are proven.

## Architecture Brief

### Repository shape

Retain the existing modular Python service and Go MCP. Do not introduce a new
service or top-level application.

Host-owned modules:

- `store.py`: migrations and database initialization only;
- `service_contracts.py` plus the JSON schema catalog: external and durable
  record contracts;
- `service_publication.py`: transactional acquisition-to-authority
  publication;
- new narrow temporal store modules: version/evidence, collection, profile,
  claim/event, graph outbox, and intelligence-task receipts;
- `service_supervisor.py` and scheduler modules: deterministic state, leases,
  budgets, retries, coverage, and timer claims;
- `service_retrieval.py`: deterministic query planning, candidate fusion,
  temporal/access filtering, and evidence assembly;
- `service_intelligence.py`: bounded stochastic workers behind Plan 0010
  validators and ledger;
- `service_app.py` and the Go MCP: compact product-facing discovery and
  transport only.

Adapters continue to return bounded acquisition results. They do not write the
corpus, invoke one another, resolve identities, publish graphs, or control
timers.

### Request and job context

Every acquisition, enrichment, projection, and query carries or derives:

- user/profile and access-partition identity;
- job, collection-run, acquisition, and attempt identity;
- source, adapter, selector, and collection-spec version;
- observed, fetched, published, valid, and system times when applicable;
- policy, transformation, extractor, projection, and contract versions;
- bounded budgets and redaction/retention classes.

### Frontend boundary

There is no frontend requirement in this campaign. The compact MCP/Unix-socket
API is the product boundary. Any future UI must consume those same contracts
and may not gain direct database, browser, or provider access.

## Temporal Authority Model

### Stable identity and immutable evidence

- `documents` becomes stable source-content identity and current-version
  pointer, not mutable evidence.
- `document_versions` stores immutable title, author, normalized text,
  metadata, media, content hash, publication/valid time, transformation
  version, originating acquisition, access partition, and system interval.
- `document_version_sightings` records every acquisition that observed a
  version, including collection run/spec and observed time.
- `document_chunks` becomes version-scoped; chunk and embedding identity
  includes the immutable version.
- `evidence_spans` binds a version/chunk span, digest, redaction class, and
  access partition for all derived records.
- current-document queries remain available through a deterministic current
  projection; historical and `known_as_of` queries use immutable versions.

### Bitemporal semantics

Records that describe the world carry:

- `valid_from` / `valid_to`: when the assertion is believed true in the source
  world, nullable when unknown;
- `system_from` / `system_to`: when the service accepted the record as current
  knowledge;
- `observed_at`: when a collection saw the evidence;
- `published_at`: when the source says the content was published.

`unknown`, `not_observed`, and `observed_absent` are distinct states.
`observed_absent` requires a successful coverage interval for the relevant
surface and selector.

### Entities, accounts, profiles, claims, and events

- source accounts remain distinct from real-world people and organizations;
- profile snapshots are immutable versioned evidence with section-level spans;
- aliases, identity assertions, merges, and splits are reversible records,
  never destructive rewrites;
- claims and relationships point to one or more evidence spans and retain
  conflicts, supersession, confidence, validation state, and bitemporal scope;
- events retain event time separately from publication, observation, and
  system times.

### Access partitions

Every authoritative and derived record carries an access partition. Public
material uses the public partition; authenticated material uses a named
profile-scoped partition. Candidate generation, enrichment, retrieval,
projection, caching, and MCP responses must preserve or narrow this boundary,
never widen it.

## Dependency Graph And Plan 0010 Attachments

```text
Packet 1: temporal schema and migration
    |
    v
Packet 2: immutable publication and replay
    |\
    | +--> Packet 3: collection specs, timers, coverage
    |          |
    |          +--> Plan 0010 P1 + content assessment contract
    |
    +----> Packet 4: profile snapshots and source accounts
               |
               +--> deterministic identity candidates
                         |
                         +--> Plan 0010 P1/P2 identity contract
    |
    v
Packet 5: claims, events, temporal retrieval, graph outbox
    |
    +--> Plan 0010 retrieval-evaluation compatibility and receipts
    |
    v
Packet 6: MCP product, adapter maintenance, rollout
    |
    +--> Plan 0010 P3/P4 diagnosis, repair, replay, discovery
    |
    v
Packet 7: integrated acceptance and closeout
```

Packets 3 and 4 may proceed in parallel only after Packet 2 closes. Packet 5
joins both. Packet 6 cannot claim product readiness before Packet 5 provides
temporal evidence and retrieval.

## Packets

### Packet 1 | Temporal schema and reversible migration

Owned surfaces:

- `store.py`;
- `service_contracts.py` and `service-contracts-v1.json`;
- a narrow temporal store module;
- migration and contract tests.

Work:

- add access partitions, immutable document versions, version sightings,
  version-scoped chunks/evidence, source accounts, profile snapshots and
  sections, reversible identity assertions, bitemporal claims, claim
  conflicts/supersession, events, evidence links, collection specs/runs,
  coverage intervals/gaps, cursors/watermarks, and graph outbox tables;
- preserve all schema-7 rows and create one immutable baseline version for
  each existing document;
- add stable version/evidence IDs and database constraints preventing
  immutable record mutation or cross-partition evidence links;
- provide a deterministic downgrade/export receipt and replay fixture rather
  than destructive rollback SQL;
- keep current query behavior readable during the migration.

Exit gate:

- schema migration, concurrent initialization, foreign-key, integrity,
  baseline backfill, idempotent replay, newer-schema refusal, and failure
  rollback tests pass;
- every existing document has exactly one baseline immutable version and its
  current pointer resolves.

### Packet 2 | Immutable publication and evidence projection

Owned surfaces:

- `service_publication.py`;
- chunk/entity/relationship enrichment and retrieval compatibility seams;
- focused publication, enrichment, and retrieval tests.

Work:

- replace document overwrite with append-or-reuse immutable version
  publication;
- record every sighting and collection/acquisition provenance;
- make chunks, embeddings, entities, relationships, and evidence spans
  version-scoped;
- preserve idempotency for identical acquisitions and content;
- project current documents for existing query clients without erasing old
  versions;
- rebuild active indexes deterministically from authoritative versions.

Exit gate:

- unchanged content reuses a version and adds only a sighting;
- changed content creates a new immutable version and updates only the current
  pointer;
- prior text, metadata, media, chunks, embeddings, entity links, and evidence
  remain queryable;
- migration plus publication replay produces identical stable IDs and counts.

Plan 0010 remains inactive here; raw evidence must be durable before any
assessment worker runs.

### Packet 3 | Collection specifications, timers, and assessment

Owned surfaces:

- collection contracts/store/scheduler and service supervisor;
- timer installation/configuration surfaces;
- acquisition job runner and service discovery;
- Plan 0010 common kernel and `content_assessment` attachment.

Work:

- define typed collection specs for recent feeds, topics, posters, channels,
  accounts, profiles, selectors, intervals, item/time limits, budgets,
  retention, redaction, and pause/resume state;
- add durable timer claims, collection runs, cursors, watermarks, attempted
  intervals, gaps, source health, yield, and backoff;
- deduplicate timer and manual work through the existing supervisor;
- lease authenticated source/profile work and enforce access partitions;
- publish raw evidence first, then enqueue bounded assessment batches;
- implement Plan 0010 Packet 1 and the content-assessment subset of Packet 2,
  with deterministic cheap-path filtering and replayable failure.

Exit gate:

- repeated timer runs are idempotent while edits and new observations remain
  visible;
- each run proves the attempted surface and interval and distinguishes service
  health from yield;
- assessment failure cannot fail, hide, or roll back acquisition;
- disabled App Intelligence leaves collection and cache querying operational.

### Packet 4 | Profile acquisition and identity

Owned surfaces:

- source-neutral profile contracts/store/publication;
- LinkedIn profile adapter first, then compatible source account surfaces;
- deterministic candidate generation;
- Plan 0010 profile-change and identity-resolution attachment.

Work:

- acquire LinkedIn people and company profiles without messages,
  connections, invitations, or unrelated private surfaces;
- store immutable snapshots, section-level evidence, visibility, redaction,
  retention, valid time, and observed time;
- add analogous bounded channel/profile normalization for YouTube, X,
  Facebook, Reddit, and future adapters;
- generate identity candidates only from canonical URLs, declared links,
  official domains, normalized names/handles, and existing aliases;
- implement Plan 0010 profile-change and identity contracts;
- retain supporting and conflicting evidence; never model-direct a canonical
  merge.

Exit gate:

- repeated snapshots preserve history and real changes create temporal claims;
- missing/redesigned sections do not become confirmed real-world changes;
- `same_entity`, `different_entity`, `ambiguous`, and
  `insufficient_evidence` are durable, reviewable terminal outcomes;
- cross-service account assertions remain reversible and evidence-linked.

### Packet 5 | Claims, events, temporal retrieval, and GraphRAG

Owned surfaces:

- claim/event promotion and temporal query planning;
- `service_retrieval.py`, evaluation fixtures, and index publication;
- Graphiti/FalkorDB outbox and projection worker;
- Plan 0010 extraction and retrieval-evaluation attachment.

Work:

- promote evidence-backed entities, claims, events, roles, and relationships
  with conflicts, supersession, uncertainty, and bitemporal scope;
- classify entity, event, timeline, trend, comparison, `as_of`, `during`, and
  `known_as_of` queries deterministically;
- fuse lexical, semantic, entity, event, temporal, and bounded graph
  candidates while preserving access partitions and identity ambiguity;
- return event, publication, observation, and knowledge times explicitly;
- project accepted temporal records to Graphiti/FalkorDB through a durable,
  idempotent, access-partitioned outbox with read-after-write receipts;
- rebuild the graph projection from SQLite and remain operational when
  Graphiti is unavailable;
- use Plan 0010 structured extraction only for bounded proposals and attach
  retrieval evaluation to recorded cases/evidence.

Exit gate:

- every answer fact resolves to immutable evidence;
- `as_of` and `known_as_of` produce demonstrably different results when
  evidence arrived late;
- conflicts and ambiguous identities remain visible;
- deleting the graph projection and replaying the outbox reconstructs it;
- graph degradation does not prevent deterministic evidence retrieval.

### Packet 6 | Agent-facing MCP, maintenance, and rollout

Owned surfaces:

- service contracts/application/HTTP and Go MCP;
- operator diagnostics and configuration docs;
- Plan 0010 adapter triage/repair and service-discovery attachment;
- installed user service and timer units.

Work:

- expose compact discovery plus evidence, temporal query, timeline, entity
  dossier, event dossier, trend, coverage, collection, and bounded brief
  operations without browser mechanics;
- include freshness, attempted coverage, index/projection version, access
  partition, uncertainty, and citations in responses;
- expose safe App Intelligence task readiness and receipts without prompts or
  raw provider events;
- implement Plan 0010 adapter failure triage, bounded branch repair,
  host-owned evaluation, replay, and explicit approval gates;
- install/restart the user-scoped service and timer units only after repository
  tests and migration dry-runs pass;
- run one bounded canary for each configured post/profile surface.

Exit gate:

- a fresh MCP client discovers the intended compact capabilities and answers
  temporal/profile/event questions without operating a browser;
- timers hydrate through typed specs and recover across restart;
- auth/checkpoint/rate-limit/access/transient failures never trigger code
  repair;
- installed runtime, database, timers, MCP, and Graphiti projection report
  versions bound to the candidate commit.

### Packet 7 | Integrated acceptance and closeout

Owned surfaces:

- golden/adversarial fixtures, full validation, runbook, roadmap,
  configuration, Skill guidance, and Graphiti development memory.

Work:

- run migration, replay, idempotency, temporal, absence, access, ambiguity,
  conflict, timer, restart, graph-loss, MCP, App Intelligence, and adapter
  safety suites;
- measure source yield separately from process health and model quality
  separately from deterministic validation correctness;
- independently audit every acceptance criterion against current repository,
  installed runtime, database, timer, MCP, and projection evidence;
- close Plans 0010 and 0011 only when their respective criteria are proven;
- commit in reviewable packet structure, push `origin/main`, and record exact
  Graphiti receipts.

Exit gate:

- every criterion below has direct current-state proof and no required work
  remains.

## Integrated Acceptance Criteria

### P01 temporal corpus

- changed posts and profiles never overwrite historical content or metadata;
- every derived entity, identity assertion, claim, event, and relationship
  closes to exact immutable evidence in the authorized partition;
- valid, publication, observation, and system times are distinct;
- unknown, not observed, and observed absent are distinguishable;
- schema-7 data remains queryable after an idempotent reversible migration.

### P02 collection and coverage

- typed bounded specs cover feeds, topics, posters, channels, accounts, and
  profiles;
- timers persist cursor, watermark, attempted intervals, gaps, retries,
  backoff, budgets, leases, health, and yield across restart;
- timer/manual work deduplicates and authenticated work cannot cross profiles;
- stochastic assessment is post-publication, bounded, replayable, and
  optional.

### P03 profiles and identity

- people, organization, company, creator, channel, and account profiles are
  first-class versioned evidence;
- LinkedIn people/company history supports temporal affiliation questions;
- account-to-person/organization assertions preserve support, conflict,
  ambiguity, review, merges, and splits;
- private messages, connections, invitations, and unrelated surfaces remain
  out of scope.

### P04 temporal retrieval and GraphRAG

- entity, event, timeline, trend, comparison, `as_of`, `during`, and
  `known_as_of` questions return coherent evidence-backed results;
- lexical, semantic, temporal, entity/event, and bounded graph signals are
  inspectable;
- contradictory claims and ambiguous identity paths are surfaced;
- Graphiti/FalkorDB is rebuildable from SQLite and its loss cannot destroy
  authority or block evidence retrieval.

### P05 agent-facing product

- normal agents discover and query compact MCP tools without scraping or
  browser mechanics entering ordinary context;
- responses expose citations, freshness, coverage, uncertainty,
  access-partition scope, and relevant projection versions;
- cache-only queries never enqueue acquisition or model work.

### P06 App Intelligence

- every stochastic task uses strict versioned Plan 0010 contracts, finite
  budgets, evidence closure, stable validator codes, idempotent promotion, and
  replay receipts;
- ambiguous identities never auto-merge;
- acquisition and deterministic retrieval remain operational with workers
  disabled;
- adapter maintenance is failure-signature-gated, branch-isolated,
  evaluation-bounded, approval-gated, and unable to deploy autonomously.

### Repository and runtime

- focused and full Python and Go suites pass;
- planning and goal audits pass;
- `CONFIGURATION.md`, Skill guidance, schema catalog, roadmap, runbook,
  installed runtime, and MCP discovery agree;
- local HEAD equals `origin/main`, installed/runtime versions are proven, and
  the worktree is clean.

## Testing Strategy

- use red-green-refactor for each migration and behavioral seam;
- keep pure ID, temporal, candidate, and validator tests DB-free;
- use temporary SQLite databases for migration, replay, publication,
  partition, restart, and projection integration tests;
- use deterministic fake adapters/workers for timer, assessment, identity,
  graph, and repair state machines;
- use real local Graphiti only for bounded projection canaries after outbox
  tests pass;
- use authenticated browser profiles only for final leased read-only source
  canaries.

## Rollout And Rollback

1. commit and push each validated packet;
2. dry-run migrations against a copy of the installed database;
3. stop timers before installed database migration;
4. create a timestamped SQLite backup and record its digest;
5. install the candidate Skill/service, migrate once, and verify readbacks;
6. enable timers one collection spec and source at a time;
7. enable stochastic workers only after raw publication and replay proof;
8. enable Graphiti outbox delivery only after SQLite-only retrieval passes.

Rollback means stop timers/workers, restore the prior installed code and
database backup, and retain the failed candidate database/artifacts for audit.
Never attempt destructive down-migration of immutable history.

## Delegation And Reconciliation

Planning checkpoint: `not_spawned`. The authority correction, dependency
ordering, roadmap, and shared plan files are one critical-path write surface;
parallel exploration would duplicate already indexed architecture context.

For implementation, reconsider delegation at every packet. Packets 3 and 4
are the first intended parallel lanes after Packet 2 freezes temporal
contracts. Any delegated lane must own disjoint files, return a runtime handle
and tests, and remain advisory until the primary agent reconciles it against
the canonical schema and full suite.

## Checkpoints

### Checkpoint P0011-C00 | 2026-07-25

Plan version: 1

State transition: `planned -> active`

Progress classification: `outcome_progress`

Owned changes:

- established Plan 0011 as the integrated P01-P06 campaign authority;
- subordinated Plan 0010 to four explicit stochastic attachment points;
- made immutable temporal evidence the critical path before timers, identity,
  graph projection, or agent-facing claims.

Validation evidence:

- current schema and publication flow were inspected with CodeGraph;
- schema 7 uses mutable `documents` and document-scoped chunks/evidence;
- current changed-content publication overwrites document and chunk
  projections while retaining only envelope/sighting history.

Subagent status and reconciliation:

- `not_spawned`; planning authority and shared documentation are one coupled
  critical-path surface.

Remaining acceptance criteria:

- all Packet 1 through Packet 7 gates and integrated acceptance criteria.

Next action:

- implement Packet 1 temporal schema and reversible migration using
  test-first schema-7 backfill and replay fixtures.

### Checkpoint P0011-C01 | 2026-07-25

Plan version: 1

State transition: `packet_1_active -> packet_1_complete`; `packet_2_ready`

Progress classification: `outcome_progress`

Owned changes:

- added additive schema version 8 with access partitions, immutable document
  versions and sightings, version-scoped chunks/evidence, profile/account and
  reversible identity authorities, bitemporal claims/events, collection
  coverage/cursors, and a graph-projection outbox;
- backfilled every schema-7 document into one immutable baseline version and
  preserved the current document/chunk compatibility projections;
- added a partition-safe temporal evidence contract plus generated Go catalog
  compatibility;
- added canonical temporal IDs and a deterministic schema-7 compatibility
  export with a content-addressed receipt;
- removed wall-clock drift from the process-level freshness fixture discovered
  by full-suite validation.

Validation evidence:

- source commit: `f14b0fa`;
- migration, contract, temporal-store, service-store, publication, and
  retrieval focused suites passed;
- the full Python suite passed;
- `go generate ./...`, `go test ./...`, and `go vet ./...` passed;
- active planning and goal-only audits passed with no problems;
- `PRAGMA integrity_check`, `PRAGMA foreign_key_check`, concurrent
  initialization, migration rollback, immutable-write rejection, and
  cross-partition evidence rejection are covered and passed.

Subagent status and reconciliation:

- `not_spawned`; Packet 1 owned one coupled migration/contract boundary and
  CodeGraph supplied the required structural context without a parallel
  exploration lane.

Remaining acceptance criteria:

- Packet 2 through Packet 7 and their integrated acceptance gates;
- installed-runtime migration remains intentionally deferred to Packet 6.

Next action:

- execute Packet 2 by replacing mutable changed-content publication with
  idempotent immutable version/sighting/chunk/evidence publication while
  preserving current retrieval compatibility.

### Checkpoint P0011-C02 | 2026-07-25

Plan version: 1

State transition: `packet_2_active -> packet_2_complete`; `packet_3_ready`

Progress classification: `outcome_progress`

Owned changes:

- changed corpus publication from mutable overwrite to append-or-reuse
  immutable document versions with a sighting for each acquisition;
- made changed content advance only the current document pointer while prior
  text, chunks, evidence, embeddings, entity links, and relationships remain
  attached to their original immutable version;
- added version-scoped embedding, entity, relationship, and relationship
  evidence projections without removing schema-7 current-document
  compatibility;
- changed index publication to derive authoritative snapshots from immutable
  current versions and their version-scoped enrichment;
- preserved deterministic stable IDs and idempotent replay for identical
  acquisitions.

Validation evidence:

- source commit: `0454e5a`;
- focused migration, temporal-store, publication, enrichment, retrieval,
  evaluation, store, and service-app suites passed;
- the full Python suite passed;
- `go test ./...` and `go vet ./...` passed;
- changed-content tests prove two immutable versions while identical replay
  retains one version and sighting;
- retrieval and enrichment tests prove historical projections survive a
  current-version change.

Subagent status and reconciliation:

- `not_spawned`; Packet 2 remained within the coupled publication,
  enrichment, and index boundary established by Packet 1, with CodeGraph used
  for structural context.

Durable memory:

- Packet 1 completed on retry as job
  `2342cdaa-5068-4f1b-95e7-f487e59a5e78`, episode
  `15ffb6f1-6360-4895-a845-b6a3681f4d1e`;
- Packet 2 was queued as job `b9f1c8a7-ce57-4258-9a40-197d6e844a99`
  in `last30days_skill_main` and completed as episode
  `d1a64575-0ff2-4339-928b-235c8bdf7833`.

Remaining acceptance criteria:

- Packet 3 through Packet 7 and their integrated acceptance gates;
- installed-runtime migration remains intentionally deferred to Packet 6.

Next action:

- execute Packet 3 by defining typed collection specifications and durable
  timer/run/coverage state, then attach Plan 0010 content assessment strictly
  after raw evidence publication.

### Checkpoint P0011-C03 | 2026-07-25

Plan version: 1

State transition: `packet_3_active -> packet_3_complete`; `packet_4_ready`

Progress classification: `outcome_progress`

Owned changes:

- added strict immutable collection-spec revisions for feed, topic, poster,
  channel, account, and profile surfaces with explicit selectors, schedules,
  bounds, budgets, retention, redaction, assessment, and pause state;
- added durable schedules, timer/manual claims, interval runs, attempts,
  cursors, watermarks, coverage, gaps, source health, yield, backoff, and
  authenticated profile leases;
- froze every run to its originating spec revision and qualified supervisor
  deduplication by collection spec and revision;
- implemented the Plan 0010 common task kernel and bounded
  `content_assessment` queue, worker, evidence closure, validation, promotion,
  and replay receipts;
- committed raw corpus evidence before assessment enqueue and isolated
  assessment failure from acquisition state;
- added service discovery and operator CLI surfaces for collection
  put/list/run/pause/resume while leaving installed timers disabled.

Validation evidence:

- source commit: `4ae5095`;
- focused collection, App Intelligence, publication, job-runner, migration,
  contract, runtime, and service-app suites passed;
- full `uv run pytest -q` passed;
- `go generate ./...`, `go test ./...`, and `go vet ./...` passed;
- regression fixtures prove timer/manual coalescing, distinct-spec job
  isolation, frozen-revision policy, per-spec bounds and retention,
  authenticated-profile lease exclusion, retry history, gap resolution,
  raw-publication survival under assessment failure, and disabled-AI
  operation.

Subagent status and reconciliation:

- `not_spawned`; Packet 3 shared the collection migration, supervisor,
  publisher, and contract boundary, and CodeGraph supplied structural context.

Durable memory:

- Packet 2 completed as job `b9f1c8a7-ce57-4258-9a40-197d6e844a99`,
  episode `d1a64575-0ff2-4339-928b-235c8bdf7833`;
- Packet 3 was submitted as job
  `63ca548a-3d24-4757-a3c0-1c3ccf5ba62a` in
  `last30days_skill_main`; it remained in node resolution at checkpoint and
  its final episode UUID must be recorded at the next checkpoint.

Remaining acceptance criteria:

- Packet 4 through Packet 7 and their integrated acceptance gates;
- installed-runtime migration, timer enablement, and live canaries remain
  intentionally deferred to Packet 6.

Next action:

- execute Packet 4 by publishing immutable source-neutral profile snapshots,
  beginning with bounded LinkedIn people/company surfaces, then attach
  deterministic identity candidates and conservative Plan 0010 identity
  resolution.

### Checkpoint P0011-C04 | 2026-07-25

Plan version: 1

State transition: `packet_4_active -> packet_4_complete`; `packet_5_ready`

Progress classification: `outcome_progress`

Owned changes:

- added schema version 11 immutable profile sightings and section evidence
  with visibility, redaction, retention, and
  `visible`/`not_observed`/`observed_absent` presence semantics;
- added source-neutral profile publication after raw immutable evidence,
  conservative comparable-section changes, and exact section-span closure;
- routed exact LinkedIn people/company profile collection through the retained
  authenticated agent-browser profile while excluding messages, connections,
  invitations, and unrelated private surfaces;
- added deterministic cross-service candidates from canonical URLs, declared
  links, normalized names/handles, and recorded account evidence;
- added durable terminal `same_entity`, `different_entity`, `ambiguous`, and
  `insufficient_evidence` outcomes without destructive merges;
- attached Plan 0010 profile-change and identity-resolution validators only to
  host-created evidence and candidate IDs.

Validation evidence:

- source commit: `22c8db1`;
- focused profile, LinkedIn profile, App Intelligence contract, acquisition
  worker, job runner, collection, runtime, migration, and temporal suites
  passed;
- full `uv run pytest -q` passed;
- Python compilation passed;
- `go generate ./...`, `go test ./...`, and `go vet ./...` passed under
  `mcp/`;
- `git diff --check` passed;
- regression fixtures prove immutable replay, missing-section non-change,
  exact section evidence, deterministic candidates, terminal outcomes,
  checkpoint-before-navigation, and prohibited-surface exclusion.

Subagent status and reconciliation:

- `not_spawned`; Packet 4 crossed one profile publication, adapter, identity,
  and contract boundary, with CodeGraph supplying structural exploration.

Durable memory:

- Packet 3 completed as job `63ca548a-3d24-4757-a3c0-1c3ccf5ba62a`,
  episode `fbda0a6d-9a87-458b-8e50-fa769be670f8`;
- Packet 4 was queued as job `9f721b66-5d0a-40cd-b3eb-36763315e307`
  in `last30days_skill_main`; record its episode UUID after completion.

Remaining acceptance criteria:

- Packet 5 through Packet 7 and their integrated acceptance gates;
- profile-to-entity assertions and temporal affiliation claims remain Packet 5
  promotion work;
- installed-runtime migration, timer enablement, and live profile canary remain
  intentionally deferred to Packet 6.

Next action:

- execute Packet 5 by promoting evidence-backed claims/events and implementing
  temporal retrieval plus rebuildable access-partitioned Graphiti projection.

### Checkpoint P0011-C05 | 2026-07-25

Plan version: 1

State transition: `packet_5_active -> packet_5_complete`; `packet_6_ready`

Progress classification: `outcome_progress`

Owned changes:

- added schema version 12 graph projection receipts plus recorded temporal
  retrieval cases and deterministic evaluation receipts;
- added evidence-backed entity, bitemporal claim, conflict, and event
  promotion with same-partition evidence closure;
- added deterministic entity, event, timeline, trend, comparison, `as_of`,
  `during`, and `known_as_of` classification and independently filtered valid
  and knowledge time;
- fused access-partitioned lexical, semantic, and graph candidates while
  returning exact evidence records, source URLs, and temporal dimensions;
- added an idempotent graph outbox worker with delivery receipts, retained
  failures, and authoritative replay/rebuild behavior;
- attached bounded Plan 0010 knowledge-extraction and retrieval-evaluation
  proposals to host-created evidence and recorded cases;
- promoted validated same-entity outcomes into reversible, evidence-linked
  identity assertions.

Validation evidence:

- source commit: `6c6e751`;
- focused temporal knowledge, retrieval, App Intelligence, identity, graph
  degradation, retry, and rebuild suites passed;
- full `uv run pytest -q` passed;
- Python compilation passed;
- `go generate ./...`, `go test ./...`, and `go vet ./...` passed under
  `mcp/`;
- `git diff --check` passed;
- regression fixtures prove late-evidence `as_of`/`known_as_of` divergence,
  exact evidence URLs, conflict visibility, access-partition filtering,
  deterministic evaluation codes, and SQLite-only operation during graph
  failure.

Subagent status and reconciliation:

- `not_spawned`; Packet 5 crossed one temporal authority, retrieval, identity,
  and projection boundary, with CodeGraph supplying structural exploration.

Durable memory:

- Packet 4 job `9f721b66-5d0a-40cd-b3eb-36763315e307` timed out after
  180 seconds while persisting graph records and produced no episode UUID;
  repository commits and validation remain the checkpoint authority.
- Packet 5 was queued as job `52525186-f6ba-4e7e-ac1d-8076318740e5` in
  `last30days_skill_main`; record its terminal result at the next checkpoint.

Remaining acceptance criteria:

- Packet 6 and Packet 7 plus their integrated acceptance gates;
- concrete local Graphiti sink wiring and read-after-write canary remain
  Packet 6 rollout work;
- installed-runtime migration, timer enablement, MCP discovery, and bounded
  live source canaries remain intentionally deferred to Packet 6.

Next action:

- execute Packet 6 compact service/MCP operations, concrete graph delivery,
  bounded adapter-maintenance discovery, installed migration, and one
  read-only canary per configured post/profile surface.

### Checkpoint P0011-C06A | 2026-07-25

Plan version: 1

State transition: `packet_6_active -> packet_6_awaiting_human_gate`

Progress classification: `outcome_progress`

Owned changes:

- added compact cache-only evidence, brief, timeline, entity dossier, event
  dossier, trend, comparison, profile-history, coverage, collection, and
  maintenance operations under `/v1/intelligence`;
- derived access partitions from the caller profile and rejected arbitrary
  partition widening;
- expanded the Go MCP from five to ten tools while keeping browser, prompt,
  provider-event, cookie, and credential mechanics outside ordinary clients;
- added a loopback-only concrete Graphiti HTTP sink, deterministic
  partition-scoped node identity, durable outbox delivery, and receipts;
- exposed safe maintenance readiness and repair-policy gates without allowing
  authentication, access, rate-limit, checkpoint, or transient failures to
  become repair candidates;
- installed service version 0.2.0 from commit `0e7938a`, migrated the live
  database from schema 7 to schema 12 after a successful dry run, and enabled
  the user-scoped Graphiti projection loop.

Validation evidence:

- source and installed commit: `0e7938a`;
- pre-migration backup:
  `/home/ecochran76/.local/share/last30days/backups/research-schema7-20260725T202700Z.db`,
  SHA-256
  `d28f7dfe74a2d14c68777ba3a4bc0bfe822893ea81e904e6f37b84e6f7b41cea`;
- installed database reports schema 12, 31 documents, 31 document versions,
  zero missing current versions, `integrity_check=ok`, and no foreign-key
  violations;
- a fresh installed MCP client discovered all ten tools and successfully
  called service info, temporal query, coverage, named-profile history, and
  maintenance status;
- installed Graphiti outbox canary `canary-plan0011-p6` published in one
  attempt with receipt
  `graphiti-http-v1:72def667-2ed5-526f-b313-00cba738f400:db720d2a17f1c3fcc9513d953a34d6d6a5237d8ac1a6a5dc686121b41a6330bb`;
- Reddit job `0c62b06f-7c9f-4ae1-a830-5dfb52b32776` published one item;
- YouTube job `055c04ff-df5d-472a-9ef8-91a9dccd1130` published successfully
  with zero yield, preserving the distinction between health and yield;
- X job `3a0a59a7-5729-4547-8702-22f02b3579aa` stopped after one attempt as
  `awaiting_operator` with `auth_required` and no repair or browser action.

Subagent status and reconciliation:

- `not_spawned`; Packet 6 remained a coupled service, installed-runtime, and
  rollout boundary, with CodeGraph used for structural exploration.

Durable memory:

- provider readiness passed and checkpoint P0011-C06A was queued as job
  `e1a2d508-e2f2-4efb-9a6f-b28049750e34` in
  `last30days_skill_main`; record its terminal result at the next checkpoint.

Remaining acceptance criteria:

- operator reauthentication of the configured X agent-browser profile,
  followed by one bounded X canary;
- bounded Facebook post plus LinkedIn post/profile canaries;
- timer restart/recovery proof and the complete Packet 6 exit gate;
- Packet 7 independent integrated acceptance and closeout.

Next action:

- after the operator restores X authentication, rerun the X canary, continue
  with Facebook and LinkedIn post/profile canaries, then execute Packet 7.

### Checkpoint P0011-C06B | 2026-07-25

Plan version: 1

State transition: `packet_6_awaiting_human_gate -> packet_6_resume_control_ready`

Progress classification: `blocker_reduction`

Owned changes:

- confirmed the configured `last30days-facebook` profile was authenticated for
  X after the operator refreshed the stalled page;
- closed the detached no-CDP browser cleanly so Chromium could flush the
  profile and release its process lock;
- proved the first `force_refresh` retry coalesced onto the retained
  `awaiting_operator` job and returned cached evidence without performing a
  new acquisition;
- exposed the supervisor's existing bounded `resume_after_operator`
  transition through the application, Unix-socket HTTP service, Python client,
  and `service.py job <job-id> --resume`;
- preserved the original job ID, attempts, event history, and configured
  attempt ceiling while rejecting missing, non-awaiting, and exhausted jobs;
- documented the operator-only resume workflow in the Skill, configuration
  reference, and changelog.

Validation evidence:

- the X profile's manual browser PID `592914` exited cleanly and runtime status
  reported `browser_alive=false`;
- the initial retry returned retained job
  `3a0a59a7-5729-4547-8702-22f02b3579aa`, confirming the missing public resume
  transition rather than a new authentication result;
- focused supervisor, refresh, application, HTTP, process, and CLI tests
  passed;
- Python compilation and `git diff --check` passed.

Subagent status and reconciliation:

- `not_spawned`; the active runtime instruction prohibits delegation unless
  the user explicitly requests it, and this repair was one coupled
  supervisor-to-operator interface seam.

Remaining acceptance criteria:

- install service version 0.2.1 from the candidate commit and resume the
  retained X job through the public CLI;
- prove the resumed X acquisition against the authenticated profile;
- complete bounded Facebook post plus LinkedIn post/profile canaries;
- prove recurring collection restart recovery and complete the Packet 6 exit
  gate;
- execute Packet 7 independent integrated acceptance and closeout.

Next action:

- commit and install the guarded resume candidate, resume the retained X job,
  and require a new acquisition attempt before counting the canary.

### Checkpoint P0011-C06C | 2026-07-25

Plan version: 1

State transition:
`packet_6_resume_control_ready -> packet_6_stalled_loader_recovery_ready`

Progress classification: `blocker_reduction`

Owned changes:

- installed service version 0.2.1 and resumed retained X job
  `3a0a59a7-5729-4547-8702-22f02b3579aa` through the public CLI;
- preserved its append-only history while attempt count advanced from one to
  two;
- recorded attempt two returning `awaiting_operator/auth_required`;
- confirmed the agent-browser broker still selected
  `last30days-facebook`, required no manual action, and reported no compatible
  live browser after the failed attempt;
- traced the X adapter and proved its retained-tab auth probe evaluated the DOM
  once, with no recovery for a non-terminal loading screen;
- added a single reload-and-recheck for only an ambiguous X auth DOM;
- preserved immediate terminal handling for explicit login, checkpoint, and
  restricted-account evidence;
- bumped the candidate service version to 0.2.2 and documented the behavior.

Validation evidence:

- job events 7 through 12 prove the public resume, lease generation two,
  attempt two, acquisition, and typed operator stop;
- agent-browser access-plan selected `last30days-facebook` and reported
  `manualActionRequired=false`;
- focused X auth-probe and acquisition-worker tests passed;
- the full Python suite, Python compilation, and `git diff --check` passed.

Subagent status and reconciliation:

- `not_spawned`; the active runtime instruction prohibits delegation unless
  the user explicitly requests it, and the repair remained one bounded
  adapter seam.

Remaining acceptance criteria:

- resolve the recorded X authenticated-browser gate under a newly authorized
  plan slice;
- after successful X publication, complete bounded Facebook post plus LinkedIn
  post/profile canaries;
- prove recurring collection restart recovery and complete the Packet 6 exit
  gate;
- execute Packet 7 independent integrated acceptance and closeout.

Stop rule:

- the next X result is the final Packet 6 adapter retry. If it returns another
  terminal failure, checkpoint the typed evidence and stop rather than
  widening repair scope.

Next action:

- install version 0.2.2, run one newly keyed final X canary because the retained
  job has truthfully exhausted its attempt ceiling, and inspect the resulting
  acquisition and publication receipts.

Live outcome:

- commit `fbe7460` was pushed to `origin/main`, copied into the global install,
  and activated as service version 0.2.2 on schema 12;
- retained job `3a0a59a7-5729-4547-8702-22f02b3579aa` remained preserved at
  `attempts=2`, `max_attempts=2` and was not reset;
- final canary job `e6888bd5-37ea-4210-9816-3b6d1e04da6f` acquired once and
  ended `awaiting_operator/auth_required` at
  `2026-07-25T22:02:55.354610Z`;
- acquisition `work-71ef1fe8d002811c7f10aed4de92f90d` recorded zero items;
- the service-owned agent-browser session retained one active tab at
  `https://x.com/` with title `x.com/home`;
- the checkpoint stop rule is now active. Packet 6 must not widen adapter work
  or run another X canary without a new plan decision or renewed evidence that
  the service-owned browser renders authenticated X DOM.

### Checkpoint P0011-C06D | 2026-07-25

Plan version: 1

State transition:
`packet_6_stalled_loader_recovery_ready -> packet_6_remote_view_routing_ready`

Progress classification: `blocker_reduction`

Renewed evidence:

- the operator inspected the service-owned X tile and identified its transport
  as a broken CDP connection rather than the required Guacamole/RDP workspace;
- live agent-browser state confirmed `viewStream.provider=cdp_screencast`, no
  `remoteViewRouteId`, and no operator-ready RDP attachment;
- this deterministic transport mismatch, rather than a new content attempt,
  authorizes one bounded routing correction under the prior stop rule.

Owned changes:

- changed X's default view provider from `cdp_screencast` to `rdp_gateway`;
- replaced X's direct headed-browser launch and partial reuse logic with the
  shared brokered remote-view acquisition path;
- supplied target identity `x`, `https://x.com/home`, and service, agent, and
  task attribution to the shared request;
- inherited route-bound `remote-view open`, remote-headed execution, private
  display isolation, control input, safe shared-owner handling, and
  operator-visible readiness validation;
- bumped the candidate service version to 0.2.3 and updated the user-facing
  configuration contract.

Validation evidence:

- regression tests require the X request to carry `rdp_gateway`, its canonical
  start URL, and target identity;
- acquisition regression tests require a route-bound `remote-view open`
  command and reject regression to the direct CDP launch;
- focused X and acquisition-worker tests, the full Python suite, compilation,
  and `git diff --check` passed; installed-runtime and live remote-view proof
  remain pending at this checkpoint.

Live control-plane blocker:

- agent-browser reports one healthy Guacamole route occupied by YouTube and
  one stale former-X route whose route and display allocation are orphaned
  while its pool entry remains checked out;
- `service reconcile` did not release that checkout;
- the installed CLI recommends `service route-pool repair --dry-run` but
  rejects `route-pool` as an unknown subcommand.

Live outcome:

- commit `b76bb28` was pushed to `origin/main`, copied into the global skill
  installation, and activated as service version 0.2.3 on schema 12;
- the installed adapter and service module exactly match the committed source;
- agent-browser's MCP `service_request` dry run classified
  `guacamole:4` as a stale former-X route;
- the narrower `service_remote_view_route_release` action released only
  `guacamole:4`, preserving route B;
- route-bound `remote-view open` created
  `session:last30days-facebook` on display `:10`, route `guacamole:4`, and
  provider `rdp_gateway`;
- browser, display, route, Guacamole access, and operator visibility all read
  back `ready`, with attachability `attached_ready`;
- after one reload, the X tab resolved to the signed-out landing DOM with zero
  authenticated home/navigation markers and one username input.
- the Graphiti provider-readiness probe returned `degraded` after a Codex
  app-server timeout, so no memory write was queued; this checkpoint remains
  the durable source for later projection.

Stop rule:

- do not start another X content canary or create a duplicate browser against
  the retained profile;
- require the operator to authenticate in the now-visible Guacamole/RDP
  workspace, then verify authenticated DOM in that same service-owned browser
  before exactly one canary.

Next action:

- await operator authentication in the visible X Guacamole/RDP workspace,
  verify the same service-owned browser, then execute one bounded X canary.

### Checkpoint P0011-C06E | 2026-07-25

Plan version: 1

State transition:
`packet_6_remote_view_routing_ready -> packet_6_authority_audit_ready`

Progress classification: `blocker_reduction`

Owned changes:

- added a deterministic repo-only roadmap, runbook, and active-goal authority
  audit with TDD coverage;
- required every open roadmap lane to resolve to a current actionable plan and
  exactly one plan to own integrated campaign execution;
- required the latest integrated checkpoint and runbook turn to carry the
  governance fields needed for durable `/goal` continuation;
- wired Plan 0011 explicitly into P04 and P05 and reconciled stale installed
  version summaries to live service version 0.2.3;
- created one bounded public Reddit topic collection spec, preserved immutable
  revisions and two typed terminal budget failures, then paused it at revision
  3 after the work-unit attempt ceiling.

Validation evidence:

- the TDD red phase failed because the audit helper did not exist;
- after implementation, the audit found four real authority defects rather
  than passing on document presence alone;
- live job `a0d14a71-5383-402d-8092-69fcf581df14` terminated
  `budget_exhausted`;
- live job `989b4b90-eff5-4419-848f-5c5b99759325` terminated
  `network_budget_exhausted`;
- the reconciled authority audit passes with two legitimate open plans,
  exactly one integrated campaign authority, latest runbook Turn 14, and zero
  issues;
- all three focused authority-audit tests, the full Python suite, the full Go
  suite, script compilation, and `git diff --check` pass.

Subagent status and reconciliation:

- `not_spawned`; current runtime instructions prohibit delegation unless the
  user explicitly requests it, and this is one serialized authority seam.

Remaining acceptance criteria:

- prove one successful recurring collection interval and restart recovery
  through a bounded successor unit rather than widening the exhausted unit;
- authenticate X in the visible service-owned Guacamole/RDP browser and run
  one bounded canary;
- complete bounded Facebook post plus LinkedIn post/profile canaries;
- execute Packet 7 independent integrated acceptance and closeout.

Graphiti write status:

- provider readiness and compact checkpoint projection remain pending until a
  validated commit exists.

Stop rule:

- do not run a third interval or widen the paused acceptance spec in this work
  unit;
- do not run an X canary until authenticated DOM is verified in the same
  service-owned browser.

Next action:

- make the new authority audit pass, run focused and broad validation, commit
  and push the reconciled checkpoint, then select the next unblocked bounded
  acceptance unit.

### Checkpoint P0011-C06F | 2026-07-25

Plan version: 1

State transition:
`packet_6_authority_audit_ready -> packet_6_shared_social_route_repaired`

Progress classification: `blocker_reduction`

Owned changes:

- independently verified authenticated Facebook and LinkedIn DOM in the
  retained `last30days-facebook` browser without treating X state as evidence
  for either source;
- preserved Facebook job `74ce82f7-191c-4a41-94e6-1ef7afd18ab9` and its two
  failed acquisition envelopes instead of retrying past the source canary
  boundary;
- proved the failure was a deterministic transport-constraint mismatch:
  access planning requested `private_virtual_display` while the healthy
  route-bound browser on Guacamole route `guacamole:4` uses
  `shared_display`;
- changed the shared social adapters to pass browser host, stream provider,
  input provider, and display isolation into access planning and to request
  `shared_display` for X, Facebook, and LinkedIn post/profile work;
- synced the repaired source into the user-scoped skill install and restarted
  the ready version 0.2.4 service.

Validation evidence:

- Facebook canary acquisitions
  `work-79f5d13ac6f0776e7ed99b1ee2a67548` and
  `work-e7c7248c0ce5bf78469b9897955dca04` both failed with
  `agent_browser_error` before producing items;
- the live access plan changed from `wait_for_profile_lease` with
  `no_compatible_live_browser` under `private_virtual_display` to
  `reuse_existing_browser` with `tab_new` under `shared_display`;
- a no-navigation acquisition probe returned profile
  `last30days-facebook`, browser `session:last30days-facebook`, and session
  `last30days-facebook`;
- 88 focused social-adapter tests pass with 3 skips;
- the full Python suite passes with 2,289 tests, 7 skips, and 6 passing
  subtests;
- the installed Facebook, LinkedIn, and X adapter sources byte-match the
  working tree and `last30days.service` is active and ready on schema 12;
- post-repair Facebook job `ecea393f-c445-461d-9528-99c2107190f1`
  succeeded in one attempt, published three items from acquisition
  `work-d211f861234870f78e05fd069274d3c1`, and advanced the index to
  `index-d0a49fe879e63367952ba219`;
- serialized LinkedIn post job `91b55c9f-3827-4046-9c87-0df99ec54f40`
  failed after two internal attempts with `agent_browser_error`; acquisitions
  `work-3422d06582f77b811ff0cd2dafd30a87` and
  `work-925085bcda3576aea42397e369a20307` produced zero items.

Subagent status and reconciliation:

- `not_spawned`; current runtime instructions prohibit delegation unless the
  user explicitly requests it, and this is one serialized shared-profile
  routing seam.

Remaining acceptance criteria:

- diagnose and repair the preserved LinkedIn post failure before authorizing
  another LinkedIn live attempt;
- keep the LinkedIn profile canary withheld until the post adapter clears;
- prove one successful recurring collection interval and restart recovery
  through a bounded successor unit;
- restore and prove X authentication in the same Guacamole/RDP browser before
  any X canary;
- execute Packet 7 independent integrated acceptance and closeout.

Graphiti write status:

- deferred after a second provider-readiness timeout from the Codex app-server;
  no write was queued while the provider was degraded.

Stop rule:

- do not submit another Facebook job; the one post-repair verification
  succeeded;
- do not submit another LinkedIn post job or run the LinkedIn profile canary
  without a new bounded repair decision;
- do not run an X canary until authenticated DOM is verified in the same
  service-owned browser.

Next action:

- diagnose the preserved LinkedIn failure from deterministic artifacts and
  code, then record a new bounded repair decision or stop at the typed blocker.

### Checkpoint P0011-C06G | 2026-07-25

Plan version: 1

State transition:
`packet_6_linkedin_failure_preserved -> packet_6_failure_triage_bounded`

Progress classification: `blocker_reduction`

Owned changes:

- ran a read-only LinkedIn auth probe against the retained browser; tab
  discovery, selection, authentication inspection, and DOM evaluation all
  succeeded on the authenticated feed without navigation;
- determined that the two preserved LinkedIn acquisition envelopes do not
  contain enough stage or operation evidence to attribute a site change or
  code defect;
- added host-computed acquisition failure signatures that remain stable across
  job and attempt identifiers and preserve only bounded safe diagnostics;
- added LinkedIn failure-stage and browser-operation evidence without
  retaining DOM, cookies, tokens, or raw exception text;
- added strict App Intelligence contracts for `adapter_failure_triage`,
  `adapter_repair_recommendation`, and `branch_decision`.

Deterministic routing decision:

- the preserved LinkedIn failure is
  `insufficient_evidence -> repair_eligible=false -> observe`;
- only `site_change` and `code_defect` may route to `code_repair`;
- authentication, checkpoint, rate-limit, access restriction, transient,
  configuration, and insufficient-evidence outcomes cannot enter code repair.

Validation evidence:

- focused acquisition-worker, LinkedIn, and App Intelligence contract suite:
  41 passed, 1 skipped;
- failure-signature tests prove stability across distinct attempts and job
  identifiers;
- contract tests reject auth-to-code-repair routing, unsafe repository paths,
  and incoherent branch selections.

Subagent status and reconciliation:

- `not_spawned`; current runtime instructions prohibit delegation unless the
  user explicitly requests it, and this is one coupled diagnostics/contract
  seam.

Live canary decision:

- no new LinkedIn post job was submitted;
- the LinkedIn profile canary remains withheld;
- a future failure produced by version 0.2.5 can be compared by stable
  signature and deterministically classified before repair automation runs.

Remaining acceptance criteria:

- install and activate version 0.2.5 from a pushed commit;
- prove one successful recurring collection interval and restart recovery;
- verify X authenticated DOM before its bounded canary;
- clear LinkedIn post and profile acceptance under a newly bounded live
  decision;
- execute Packet 7 independent integrated acceptance and closeout.

Graphiti write status:

- remains deferred until provider readiness is healthy; no write is queued
  against a degraded provider.

Next action:

- validate, install, and activate version 0.2.5;
- resume Packet 6 only with a newly bounded live decision that uses the new
  failure evidence, then complete recurring timer/restart proof and Packet 7.

## Stop Rules

Stop autonomous execution at an unresolved migration-integrity failure,
cross-partition leak, destructive history rewrite, authenticated-browser human
gate, Graphiti write approval gate, unowned dirty worktree, repeated failure
of the same packet after two attempts, failed bounded review after one rework,
or two consecutive hardening-only checkpoints. Split or reframe oversized work
instead of weakening an acceptance criterion.
