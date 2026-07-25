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

## Turn 7 | 2026-07-25

Focus: Plan 0011 Packet 3 governed recurring collection and post-publication
assessment.

Authority Consulted:

- Plan 0011 Packet 3 and Plan 0010 common/content-assessment contracts
- `$tdd`, `$app-intelligence-automation`, and `graphiti-discovery`
- collection, supervisor, publisher, runtime, CLI, and contract seams through
  CodeGraph
- Graphiti, documentation, validation, goal-execution, worktree, commit, push,
  and closeout policies

Decisions And Changes:

- Added immutable typed collection-spec revisions for feed, topic, poster,
  channel, account, and profile surfaces.
- Added durable schedules, timer/manual claims, interval runs and attempts,
  cursors, watermarks, coverage, gaps, source health, yield, backoff, and
  authenticated profile leases.
- Froze each run to its originating spec revision and qualified refresh-job
  deduplication by collection spec and revision.
- Enforced per-spec item, wall-time, network, budget, retention, redaction,
  and access-partition policy in the host-owned acquisition path.
- Added the Plan 0010 common stochastic-task kernel plus bounded
  `content_assessment` evidence, validation, promotion, replay, queue, and
  worker contracts.
- Kept raw corpus publication transactional and prior to assessment enqueue;
  assessment failure or disablement cannot fail or roll back acquisition.
- Added user-facing collection configuration, service discovery capabilities,
  and CLI put/list/run/pause/resume surfaces, but did not install or enable
  timers.

Validation Evidence:

- source commit: `4ae5095`;
- focused collection, App Intelligence, publication, job-runner, migration,
  contract, runtime, and service-app suites passed;
- full `uv run pytest -q` passed;
- `go generate ./...`, `go test ./...`, and `go vet ./...` passed under
  `mcp/`;
- regression fixtures prove coalescing, spec-qualified isolation,
  frozen-revision execution, policy bounds, lease exclusion, coverage and
  gap history, assessment-failure independence, and disabled-AI operation.

State Movement:

- Plan 0011 Packet 3: `active -> complete`.
- Plan 0011 Packet 4: `pending -> ready`.
- P02 remains `PLANNED`; its source implementation is complete but the lane
  does not become operational until installed timer rollout in Packet 6.
- P01 and P03 remain `OPEN`; P04-P06 remain at their roadmap states.

Subagent Status And Reconciliation:

- `not_spawned`; Packet 3 crossed one coupled migration, supervisor,
  publication, and contract boundary, with CodeGraph used for structural
  exploration.

Graphiti Write Status:

- Packet 2 completed as job `b9f1c8a7-ce57-4258-9a40-197d6e844a99`,
  episode `d1a64575-0ff2-4339-928b-235c8bdf7833`;
- Packet 3 checkpoint write is processing as job
  `63ca548a-3d24-4757-a3c0-1c3ccf5ba62a` in
  `last30days_skill_main`; it remained in node resolution at checkpoint and
  its final episode UUID must be recorded at the next checkpoint.

Next Bounded Action:

- Execute Plan 0011 Packet 4: add immutable source-neutral profile snapshots,
  start with bounded LinkedIn people/company acquisition, generate
  deterministic identity candidates, and attach conservative Plan 0010
  identity-resolution proposals without model-direct merges.

## Turn 8 | 2026-07-25

Focus: Plan 0011 Packet 4 immutable profiles and reversible cross-service
identity.

Authority Consulted:

- Plan 0011 Packet 4 and Plan 0010 profile-change/identity joins
- `$tdd`, `$app-intelligence-automation`, and `graphiti-discovery`
- profile schema/publication, collection routing, acquisition worker,
  LinkedIn retained-browser, and intelligence contract seams through CodeGraph
- documentation, validation, Graphiti, commit, push, and closeout policies

Decisions And Changes:

- Added schema version 11 profile sightings, immutable section evidence,
  visibility/presence semantics, deterministic identity candidates, and
  terminal resolution outcomes.
- Added source-neutral profile publication strictly after raw immutable corpus
  publication, with exact section spans and conservative change comparison.
- Added exact-URL LinkedIn people/company acquisition through the retained
  authenticated agent-browser profile. Auth/checkpoint state stops before
  navigation; messages, connections, invitations, and unrelated private
  surfaces are excluded.
- Added deterministic cross-service account candidates from canonical URLs,
  declared links, normalized names/handles, and existing evidence.
- Added Plan 0010 profile-change and identity validators. Model output can only
  assess host-created candidates and cannot directly merge identities.
- Updated Skill, configuration, onboarding, roadmap, and integrated plan
  authorities; installed schema migration and live profile canary remain
  deferred to Packet 6.

Validation Evidence:

- source commit `22c8db1` was pushed to `origin/main`;
- focused Packet 4 suites passed;
- full `uv run pytest -q` passed;
- Python compilation passed;
- `go generate ./...`, `go test ./...`, and `go vet ./...` passed under
  `mcp/`;
- `git diff --check` passed.

State Movement:

- Plan 0011 Packet 4: `active -> complete`.
- Plan 0011 Packet 5: `pending -> ready`.
- P03 remains `OPEN` until temporal affiliation promotion and installed/live
  acceptance; P01 remains `OPEN`; P04-P06 remain at their roadmap states.

Subagent Status And Reconciliation:

- `not_spawned`; Packet 4 was a coupled authority boundary and CodeGraph
  supplied the required structural context.

Graphiti Write Status:

- Packet 3 completed as job `63ca548a-3d24-4757-a3c0-1c3ccf5ba62a`,
  episode `fbda0a6d-9a87-458b-8e50-fa769be670f8`;
- Packet 4 is queued as job `9f721b66-5d0a-40cd-b3eb-36763315e307` in
  `last30days_skill_main`; its final episode UUID remains pending.

Next Bounded Action:

- Execute Plan 0011 Packet 5 claims, events, temporal retrieval, and rebuildable
  access-partitioned Graphiti projection.

## Turn 9 | 2026-07-25

Focus: Plan 0011 Packet 5 temporal claims, events, retrieval, and rebuildable
GraphRAG projection.

Authority Consulted:

- Plan 0011 Packet 5 and Plan 0010 extraction/evaluation joins
- `$tdd`, `$app-intelligence-automation`, and `graphiti-discovery`
- temporal store, retrieval, identity promotion, graph outbox, and
  intelligence contract seams through CodeGraph
- documentation, validation, Graphiti, commit, push, and closeout policies

Decisions And Changes:

- Added schema version 12 graph projection receipts and recorded temporal
  retrieval cases/evaluations.
- Added evidence-backed entity, bitemporal claim/conflict, and event promotion
  constrained to the evidence access partition.
- Added deterministic temporal query classification and independent valid-time
  and knowledge-time filters with exact evidence and source URLs.
- Applied access-partition filtering to lexical, semantic, and graph candidate
  generation.
- Added durable idempotent graph delivery, failure retention, retry receipts,
  and full authoritative replay/rebuild.
- Added bounded knowledge-extraction and retrieval-evaluation validators.
- Promoted validated same-entity outcomes to reversible evidence-linked
  identity assertions.

Validation Evidence:

- source commit `6c6e751` was pushed to `origin/main`;
- focused Packet 5 suites passed;
- full `uv run pytest -q` passed;
- Python compilation passed;
- `go generate ./...`, `go test ./...`, and `go vet ./...` passed under
  `mcp/`;
- `git diff --check` passed.

State Movement:

- Plan 0011 Packet 5: `active -> complete`.
- Plan 0011 Packet 6: `pending -> ready`.
- P04: `PLANNED -> OPEN`.
- P01 and P03 remain `OPEN`; P02, P05, and P06 remain at their roadmap states
  until installed/runtime acceptance.

Subagent Status And Reconciliation:

- `not_spawned`; Packet 5 remained one coupled temporal authority and
  projection boundary, with CodeGraph used for structural exploration.

Graphiti Write Status:

- Packet 4 job `9f721b66-5d0a-40cd-b3eb-36763315e307` timed out after
  180 seconds during graph-record persistence and returned no episode UUID.
- Packet 5 repository evidence is durable; its compact Graphiti checkpoint
  passed provider readiness and is queued as job
  `52525186-f6ba-4e7e-ac1d-8076318740e5` in `last30days_skill_main`.

Next Bounded Action:

- Execute Plan 0011 Packet 6: expose compact temporal/profile/event MCP
  operations, wire concrete local Graphiti delivery, surface bounded adapter
  maintenance, dry-run and install schema 12, then run bounded read-only
  source/profile canaries.

## Turn 10 | 2026-07-25

Focus: Plan 0011 Packet 6 service product, installed rollout, and bounded live
canaries.

Authority Consulted:

- Plan 0011 Packet 6 and its authenticated-browser stop rule
- Plan 0010 adapter diagnosis and repair exclusions
- CodeGraph service, MCP, runtime, retrieval, and graph projection context
- documentation, validation, Graphiti, commit, push, and closeout policies

Decisions And Changes:

- Added compact cache-only temporal, profile, coverage, collection, and
  maintenance operations with host-derived access partitions.
- Expanded the installed MCP to ten tools while excluding browser, cookie,
  prompt, credential, and raw provider-event mechanics from agent context.
- Added a loopback-only Graphiti sink and independent durable outbox delivery.
- Installed service version 0.2.0 from commit `0e7938a`, migrated the live
  corpus from schema 7 to schema 12, and retained a checksummed schema-7
  backup.
- Ran bounded source canaries until X returned the configured human
  authentication gate, then stopped without browser operation or repair.

Validation Evidence:

- source and installed commit `0e7938a`;
- backup
  `/home/ecochran76/.local/share/last30days/backups/research-schema7-20260725T202700Z.db`,
  SHA-256
  `d28f7dfe74a2d14c68777ba3a4bc0bfe822893ea81e904e6f37b84e6f7b41cea`;
- installed service 0.2.0, schema 12, 31 documents, 31 versions, zero missing
  current versions, clean integrity and foreign-key checks;
- a fresh installed MCP client discovered ten tools and representative
  public/profile-scoped calls passed;
- Graphiti outbox canary published in one attempt with receipt
  `graphiti-http-v1:72def667-2ed5-526f-b313-00cba738f400:db720d2a17f1c3fcc9513d953a34d6d6a5237d8ac1a6a5dc686121b41a6330bb`;
- Reddit job `0c62b06f-7c9f-4ae1-a830-5dfb52b32776` published one item;
- YouTube job `055c04ff-df5d-472a-9ef8-91a9dccd1130` completed successfully
  with zero yield;
- X job `3a0a59a7-5729-4547-8702-22f02b3579aa` stopped as
  `awaiting_operator/auth_required`.

State Movement:

- Plan 0011 Packet 6: `active -> awaiting_human_gate`.
- P05 and P06: `PLANNED -> OPEN`.
- P01, P03, and P04 remain `OPEN`; broad hydration remains gated.

Subagent Status And Reconciliation:

- `not_spawned`; the service and installed rollout remained one coupled
  boundary and the human gate prohibited further autonomous canaries.

Next Bounded Action:

- After operator X reauthentication, rerun X and complete bounded Facebook and
  LinkedIn post/profile canaries, prove timer restart recovery, then execute
  Packet 7 independent acceptance and closeout.

## Turn 11 | 2026-07-25

Focus: Plan 0011 Packet 6 X authentication recovery and guarded job resume.

Authority Consulted:

- Plan 0011 Packet 6, checkpoint P0011-C06A, and the authenticated-browser stop
  rule
- current installed service, profile runtime state, durable job events, and
  agent-browser service evidence
- CodeGraph supervisor, application, HTTP, client, and CLI seams
- TDD, codebase-design, documentation, validation, Graphiti, goal-execution,
  worktree, commit, push, and closeout policies

Decisions And Changes:

- Accepted the operator's confirmation that X was authenticated after a page
  refresh, then closed the detached browser cleanly to flush and unlock the
  profile.
- Proved that `force_refresh` joined the old `awaiting_operator` job and did
  not perform a new acquisition.
- Added one public, bounded operator-resume path over the existing supervisor
  transition through the application, HTTP service, Python client, and CLI.
- Kept resume operator-only. It does not open a browser, authenticate, repair
  code, reset attempt counts, or discard the append-only job history.
- Updated the Skill, configuration reference, changelog, roadmap, and Plan 0011
  checkpoint before installed-runtime mutation.

Validation Evidence:

- focused supervisor, refresh, application, HTTP, process, and CLI tests
  passed;
- Python compilation passed;
- `git diff --check` passed;
- installed service remains unchanged at version 0.2.0 pending the next
  candidate commit and install.

State Movement:

- Plan 0011 Packet 6:
  `awaiting_human_gate -> resume_control_ready`.
- X authentication gate: `required -> completed`.
- X live acquisition proof remains pending until the new public transition is
  installed and the retained job performs attempt two.

Subagent Status And Reconciliation:

- `not_spawned`; current runtime instructions prohibit delegation unless the
  user explicitly requests it, and this repair was one coupled
  supervisor-to-operator interface seam.

Graphiti Write Status:

- checkpoint write required after the candidate commit so the source authority
  can include its immutable commit ID.

Next Bounded Action:

- Commit and push the guarded resume candidate, install service version 0.2.1,
  resume retained X job `3a0a59a7-5729-4547-8702-22f02b3579aa`, and require a
  new acquisition attempt before proceeding to Facebook and LinkedIn canaries.
