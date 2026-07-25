# last30days Runbook

Authority: append-only dated record of material planning, implementation,
runtime, validation, and handoff activity. Product priority remains in
`ROADMAP.md`; executable detail remains in `docs/dev/plans/`.

## Turn 1 | 2026-07-25

Focus: roadmap and durable memory foundation.

Authority Consulted:

- `AGENTS.md`
- `docs/dev/policies/0001-planning-discipline.md`
- `docs/dev/policies/0005-graph-backed-memory-usage.md`
- `docs/dev/policies/0015-goal-execution-governance.md`
- `docs/dev/policies/0018-architecture-guardrails.md`
- `docs/dev/policies/0019-documentation-change-control.md`
- repo-policy-selector deterministic recommendation
- Plans 0002 and 0007-0009

Decisions And Changes:

- Established `ROADMAP.md` as the canonical long-horizon product and priority
  authority.
- Established this file as the append-only turn and checkpoint ledger.
- Added repo-local roadmap/runbook governance and wired it through `AGENTS.md`.
- Reconciled legacy plan metadata and roadmap wiring without rewriting
  historical plan substance.
- Named `last30days_skill_main` as the repository Graphiti group.
- Required a compact Graphiti development-journey write after every
  non-trivial validated slice or durable checkpoint.
- Seeded successor lanes for temporal corpus history, recurring collection,
  first-class profile acquisition, temporal GraphRAG, and agent-facing product
  contracts.
- Classified profile pages as a distinct acquisition surface. LinkedIn people
  and company profiles are the first priority because identity, employment,
  affiliation, and organization facts change independently of posts.

Validation Evidence:

- repo-policy-selector classified the repository as `product-engineering`,
  recommended `repo-product-engineering`, and identified missing
  `roadmap-runbook-governance`.
- Existing Plan 0002 is still `OPEN`; Plans 0007-0009 are `CLOSED`.
- Current content-service schema and source flow were inspected before defining
  the temporal and profile roadmap seeds.

Plans Reconciled:

- `0001-2026-07-15-facebook-scraper-implementation.md`
- `0002-2026-07-15-linkedin-agent-browser-scraper.md`
- `0003-2026-07-19-x-agent-browser-scraper.md`
- `0004-2026-07-20-youtube-stealth-browser-transcript-fallback.md`
- `0005-2026-07-20-youtube-media-capability-integration.md`
- `0006-2026-07-23-agent-browser-expert-shared-profile-routing.md`
- `0007-2026-07-24-productized-intelligence-service-mvp.md`
- `0008-2026-07-25-content-service-hydration-readiness.md`
- `0009-2026-07-25-social-source-hydration-recovery.md`

State Movement:

- P00: `CLOSED`
- P01: `PLANNED`
- P02: `PLANNED`
- P03: `OPEN`
- P04: `PLANNED`
- P05: `PLANNED`

Graphiti Write Status:

- completed in `last30days_skill_main`;
- source commit: `d5ae26c`;
- job: `771c5a21-315b-4a65-b4e5-5382edf8fa6d`;
- episode: `0d4a49b4-1751-4f20-a2f8-1412ceef1645`;
- the first 120-second attempt timed out during edge resolution; the same
  durable job completed on its one bounded retry with a 240-second limit.

Next Bounded Action:

- Draft the P01 temporal corpus schema-and-migration plan before enabling broad
  recurring hydration. Profile-page discovery may proceed in parallel, but its
  storage contract must reuse P01 identity and temporal evidence semantics.

## Turn 2 | 2026-07-25

Focus: App Intelligence responsibilities across recurring acquisition,
cross-service identity, and adapter maintenance.

Authority Consulted:

- `$app-intelligence-automation`
- installed App Intelligence dependency, supervisor, protocol, decision-schema,
  integration-surface, and adapter-composition references
- `ROADMAP.md`
- `skills/last30days/scripts/lib/service_intelligence.py`
- `docs/dev/plans/0007-2026-07-24-productized-intelligence-service-mvp.md`
- planning, goal-execution, architecture, documentation, roadmap/runbook, and
  Graphiti policies

Decisions And Changes:

- Added P06 as the cross-cutting App Intelligence control-plane lane.
- Defined post-publication `content_assessment` as a bounded proposal stage;
  raw acquisition must remain successful and queryable when model work fails.
- Defined cross-service handle/profile association as deterministic candidate
  generation followed by evidence-gated `identity_resolution` proposals.
- Required ambiguity-preserving identity outcomes and prohibited model-directed
  canonical merges.
- Split adapter maintenance into deterministic failure grouping,
  `adapter_diagnosis`, isolated `adapter_repair`, host-owned evals, and explicit
  integration/deployment gates.
- Assigned direct structured API calls to high-volume non-repo leaves, Codex
  app-server to persistent repo-aware maintenance, and `codex exec` to
  stateless CI-style leaves.

Validation Evidence:

- `check_codex_app_server.py --json` passed for Codex CLI 0.145.0.
- Current app-server capabilities include stdio, Unix transport, generated JSON
  Schema/TypeScript, and authenticated WebSocket options; local stdio remains
  the chosen first transport.
- CodeGraph confirmed the existing intelligence ledger, structured enrichment
  and evaluation workers, repair supervisor, Git branch manager, and Codex
  app-server client are current reusable seams.

State Movement:

- P00-P05: unchanged.
- P06: `PLANNED`.

Graphiti Write Status:

- `graphiti_write_pending`;
- source commit: `35f49ce`;
- target group: `last30days_skill_main`;
- provider preflight returned `degraded` with a bounded Codex app-server
  `TimeoutError`, so no ingestion job was queued;
- intended episode: P06 establishes host-supervised content assessment,
  evidence-gated cross-service identity resolution, and bounded adapter
  diagnosis/repair using the existing intelligence ledger and app-server
  substrate;
- retry this exact development-journey write at the next non-trivial closeout
  after provider readiness returns `ok`.

Next Bounded Action:

- Include P06 contracts in the P01 successor plan: define the temporal
  authority consumed by assessment and identity proposals, then specify
  concrete loop schemas, budgets, promotion thresholds, evals, and stop rules
  before timers depend on stochastic processing.

## Turn 3 | 2026-07-25

Focus: versioned App Intelligence task contracts for deterministic host
processing.

Authority Consulted:

- `$app-intelligence-automation`
- App Intelligence supervisor, decision-schema, and adapter-composition
  references
- `ROADMAP.md`
- `skills/last30days/schemas/service-contracts-v1.json`
- `skills/last30days/scripts/lib/service_contracts.py`
- `skills/last30days/scripts/lib/service_intelligence.py`
- `skills/last30days/scripts/lib/service_enrichment.py`
- planning, goal-execution, parallel-plan, documentation, validation,
  closeout, commit/push, roadmap/runbook, and Graphiti policies

Decisions And Changes:

- Created
  `docs/dev/plans/0010-2026-07-25-app-intelligence-task-contracts.md` as the
  goal-compatible P06 contract execution authority.
- Made the model explicitly stochastic while requiring deterministic host
  validation, promotion, rejection, idempotency, and recorded-output replay.
- Defined a common request/result kernel plus evidence, validation, promotion,
  decision, and replay receipts.
- Defined ordered schema, correlation, evidence, domain, policy, and promotion
  validation stages with stable machine-readable error codes.
- Cataloged bounded contracts for content assessment, profile changes,
  entity/claim/event extraction, identity resolution, retrieval evaluation,
  adapter failure triage, repair recommendation, and branch decisions.
- Kept acquisition success independent from assessment and prohibited
  model-directed identity merges, browsing, publication, main-worktree edits,
  service restarts, and deployments.
- Split implementation into a common critical-path packet, two separable
  domain packets, supervisor/storage integration, and one bounded acceptance
  packet.

Validation Evidence:

- CodeGraph confirmed strict existing structured-output schemas, durable
  decision recording, bounded model calls, proposal rejection codes, repair
  states, branch isolation, tests/evals, and approval gates.
- The canonical schema catalog currently exposes acquisition, query, evidence,
  entity, relationship, job, and decision contracts but not the proposed
  shared intelligence task or receipt contracts.
- The full planning-contract audit and goal-only audit both passed with no
  problems; Plan 0010 is valid and wired into both roadmap and runbook.
- `git diff --check` passed before source commit `7e3daa6`.

State Movement:

- P00-P05: unchanged.
- P06: remains `PLANNED`; Plan 0010 is the active execution authority but no
  runtime contract implementation has started.

Graphiti Write Status:

- completed in `last30days_skill_main`;
- provider readiness passed through Codex app-server;
- the exact Turn 2 pending P06 checkpoint completed as job
  `35f37572-7aa9-4560-8edf-b55cd1a739ee`, episode
  `19f4e81f-733a-4b7f-9bb1-d74c321e1fa7`; its first 120-second attempt timed
  out and its one bounded 240-second retry completed;
- the Plan 0010 checkpoint completed on its first attempt as job
  `a0a1b824-2cf3-4667-84fb-eb683022dbaf`, episode
  `10635374-5e39-4271-a468-1f521f23a344`;
- both episodes passed Graphiti read-after-write visibility checks.

Next Bounded Action:

- Execute Plan 0010 Packet 1: add the common task envelope, evidence and
  receipt schemas, canonical digests, idempotency keys, stable validator codes,
  and compatibility adapters before any domain worker or timer depends on
  stochastic output.

## Turn 4 | 2026-07-25

Focus: correct execution authority from isolated P06 contracts to the complete
P01-P06 temporal intelligence product.

Authority Consulted:

- user correction that App Intelligence is only one part of the service
- `define-architecture`
- `$app-intelligence-automation`
- `ROADMAP.md`
- Plan 0010
- current schema, publisher, supervisor, enrichment, retrieval, application,
  MCP, and migration seams through CodeGraph
- planning, goal-execution, architecture, documentation, validation,
  branch/commit, roadmap/runbook, and subagent policies

Decisions And Changes:

- Created
  `docs/dev/plans/0011-2026-07-25-integrated-temporal-intelligence-service.md`
  as the integrated P01-P06 campaign and execution authority.
- Moved P01 from `PLANNED` to `OPEN`; immutable temporal evidence is the
  critical path.
- Kept Plan 0010 as a P06 component and attached it only after immutable
  publication, deterministic identity candidates, recorded retrieval cases,
  and deterministic adapter failure grouping.
- Defined seven bounded packets spanning temporal migration, immutable
  publication, timers/coverage, profiles/identity, claims/events/GraphRAG,
  MCP/maintenance/rollout, and integrated acceptance.
- Preserved SQLite as authority and Graphiti/FalkorDB as a rebuildable,
  access-partitioned outbox projection.

Validation Evidence:

- CodeGraph confirmed schema version 7 stores mutable current document content,
  document-scoped chunks/evidence, and immutable index snapshots.
- `CorpusPublisher.record_result()` currently updates document text, metadata,
  media, and the ordinal-zero chunk when content changes, so current source
  evidence is not yet immutable.
- Existing acquisitions, envelopes, sightings, durable jobs, leases, budgets,
  negative cache, enrichment loop, and index publication remain reusable
  foundations.
- Planning, goal, and diff validation remain required before checkpoint
  commit.

State Movement:

- P01: `PLANNED -> OPEN`.
- P02, P04, P05, and P06: remain `PLANNED`.
- P03: remains `OPEN`.
- Plan 0010: remains `PLANNED` and subordinate to Plan 0011 attachment gates.
- Plan 0011: `OPEN`.

Graphiti Write Status:

- pending validation and source commit;
- record the integrated authority and temporal critical-path decision in
  `last30days_skill_main` after the checkpoint commit.

Next Bounded Action:

- Execute Plan 0011 Packet 1 with a test-first schema-7-to-temporal migration,
  baseline version backfill, immutable evidence constraints, and idempotent
  replay proof.

## Turn 5 | 2026-07-25

Focus: Plan 0011 Packet 1 temporal schema and reversible migration.

Authority Consulted:

- Plan 0011 Packet 1 and checkpoint contract
- `$tdd`
- `store.py`, service contracts, schema catalog, and current publication seams
  through CodeGraph
- Graphiti, documentation, validation, goal-execution, worktree, commit, push,
  and closeout policies

Decisions And Changes:

- Added additive database schema version 8 without migrating the installed
  runtime.
- Kept `documents` as the stable current projection while making
  `document_versions`, version sightings, version-scoped chunks, and evidence
  spans the immutable historical authority.
- Added access-partition constraints so authenticated evidence and its derived
  records cannot be linked through a public or different-profile partition.
- Established schema authorities needed by later packets for source accounts,
  profile snapshots, reversible identity assertions, bitemporal claims and
  events, collection specs/runs/coverage/cursors, and Graphiti outbox delivery.
- Added a strict `temporal_evidence_ref` public contract and regenerated the Go
  catalog hash consumed by MCP.
- Added canonical temporal identifiers and a deterministic schema-7
  compatibility export/receipt instead of destructive down-migration SQL.
- Corrected a process test whose fixed 2026-07-24 fixture had aged from fresh
  to stale; it now asserts the intended behavior independently of wall time.

Validation Evidence:

- source commit: `f14b0fa`;
- focused migration, contract, temporal-store, service-store, publication, and
  retrieval suites passed;
- full `uv run pytest -q` passed;
- `go generate ./...`, `go test ./...`, and `go vet ./...` passed under
  `mcp/`;
- active planning and goal-only audits passed with no problems;
- migration tests prove schema-7 baseline backfill, concurrent initialization,
  transactional failure rollback, newer-schema refusal, integrity and foreign
  keys, immutable version/chunk rejection, and cross-partition evidence
  rejection.

State Movement:

- Plan 0011 Packet 1: `active -> complete`.
- Plan 0011 Packet 2: `pending -> ready`.
- P01: remains `OPEN`; installed runtime migration is deferred to Packet 6.
- P02-P06: unchanged; broad hydration and isolated stochastic execution remain
  gated.

Subagent Status And Reconciliation:

- `not_spawned`; Packet 1 was one coupled schema/contract boundary, and
  CodeGraph provided the structural context without a duplicative exploration
  lane.

Graphiti Write Status:

- the Turn 4 integrated-authority write completed as job
  `951c2b7b-fbd5-46c5-acc0-dcba4470bd38`, episode
  `35fa5b93-dbf9-442a-9b39-b4908717c4f4`;
- Packet 1 checkpoint write queued as job
  `2342cdaa-5068-4f1b-95e7-f487e59a5e78` in
  `last30days_skill_main`; record its episode UUID after completion.

Next Bounded Action:

- Execute Plan 0011 Packet 2: change publication to append or reuse immutable
  versions and sightings, create version-scoped chunks/evidence, maintain the
  current projection, and prove replay plus changed-content history.

## Turn 6 | 2026-07-25

Focus: Plan 0011 Packet 2 immutable publication and evidence projection.

Authority Consulted:

- Plan 0011 Packet 2 and checkpoint contract
- `$tdd`
- publication, enrichment, retrieval, and migration seams through CodeGraph
- Graphiti, documentation, validation, goal-execution, worktree, commit, push,
  and closeout policies

Decisions And Changes:

- Replaced mutable changed-content publication with append-or-reuse immutable
  document versions and per-acquisition sightings.
- Kept the stable `documents` row as the schema-7 compatibility projection;
  changed content advances its current pointer without altering prior
  immutable text or metadata.
- Added version-scoped embedding, entity, relationship, and relationship
  evidence projections and preserved exact evidence spans.
- Published authoritative index snapshots from current immutable versions
  while retaining legacy current-document index tables for existing clients.
- Left the installed service on schema 7; installed database migration remains
  owned by Packet 6.

Validation Evidence:

- source commit: `0454e5a`;
- focused migration, temporal-store, publication, enrichment, retrieval,
  evaluation, store, and service-app suites passed;
- full `uv run pytest -q` passed;
- `go test ./...` and `go vet ./...` passed under `mcp/`;
- identical replay, changed-content history, historical enrichment retention,
  and authoritative index projection tests passed.

State Movement:

- Plan 0011 Packet 2: `active -> complete`.
- Plan 0011 Packet 3: `pending -> ready`.
- P01: remains `OPEN` through installed migration and integrated acceptance.
- P02-P06: remain at their roadmap states; Packet 3 is ready under the
  integrated Plan 0011 authority, while broad hydration and isolated
  stochastic execution remain gated.

Subagent Status And Reconciliation:

- `not_spawned`; Packet 2 was one coupled publication/enrichment/index
  boundary and CodeGraph supplied the structural context.

Graphiti Write Status:

- Packet 1 job `2342cdaa-5068-4f1b-95e7-f487e59a5e78` completed on its
  bounded retry as episode `15ffb6f1-6360-4895-a845-b6a3681f4d1e`;
- Packet 2 checkpoint write is queued as job
  `b9f1c8a7-ce57-4258-9a40-197d6e844a99` in
  `last30days_skill_main`; record its episode UUID after completion.

Next Bounded Action:

- Execute Plan 0011 Packet 3: add typed collection specifications, durable
  timer claims/runs/cursors/coverage/gaps, authenticated profile leases, and
  raw-publication-first Plan 0010 content assessment.
