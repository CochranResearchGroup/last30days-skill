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

## Turn 12 | 2026-07-25

Focus: Plan 0011 Packet 6 bounded X stalled-loader recovery.

Authority Consulted:

- Plan 0011 checkpoints P0011-C06A and P0011-C06B
- installed service version 0.2.1, durable job events and acquisition envelopes
- agent-browser access-plan evidence for target `x`
- CodeGraph X acquisition and authentication-probe flow
- TDD, validation, documentation, Graphiti, worktree, commit, push, and
  closeout policies

Decisions And Changes:

- Proved the public resume transition queued the retained X job and advanced it
  from attempt one to attempt two without resetting history.
- Recorded attempt-two events: `operator_resumed`, `lease_acquired`,
  `acquiring`, and a terminal `awaiting_operator/auth_required`.
- Confirmed agent-browser still selects `last30days-facebook`, reports no
  manual action required, and recommends a normal service request.
- Located the deterministic adapter defect: an existing X tab was evaluated
  once and any DOM lacking both authenticated and explicit failure markers was
  treated as signed out.
- Added one reload of `https://x.com/home` plus one recheck for only that
  ambiguous state. Explicit login, checkpoint, and restricted states remain
  terminal and do not reload.
- Bumped the source candidate to service version 0.2.2.

Validation Evidence:

- regression tests cover ambiguous retained-tab recovery and no-reload behavior
  for explicit login and checkpoint states;
- focused X and acquisition-worker tests passed;
- the full Python suite, Python compilation, and `git diff --check` passed.
- commit `fbe7460` is pushed to `origin/main`, the installed copy matches it,
  and service version 0.2.2 is active on schema 12.

State Movement:

- Plan 0011 Packet 6:
  `resume_control_ready -> stalled_loader_recovery_ready`.
- X job attempt: `1 -> 2`; live successful-yield proof remains pending.

Subagent Status And Reconciliation:

- `not_spawned`; current runtime instructions prohibit delegation unless the
  user explicitly requests it, and this was one bounded adapter seam.

Graphiti Write Status:

- checkpoint write required after the final stop-state documentation commit so
  durable memory can cite both immutable source states.

Live Outcome And Stop:

- The retained job could not be resumed again because its truthful
  `max_attempts=2` ceiling was exhausted; it was not reset or widened.
- New final canary job `e6888bd5-37ea-4210-9816-3b6d1e04da6f` acquired once
  under installed version 0.2.2 and ended
  `awaiting_operator/auth_required` at `2026-07-25T22:02:55.354610Z`.
- Its acquisition `work-71ef1fe8d002811c7f10aed4de92f90d` yielded zero items.
- Agent-browser retained one active tab at `https://x.com/` with title
  `x.com/home`.
- The Packet 6 adapter retry ceiling is reached. Do not perform another X
  adapter repair or live attempt without a new plan decision or renewed
  operator-auth evidence.

Next Bounded Action:

- Resume Packet 6 only after the operator confirms the service-owned
  `last30days-facebook` browser—not merely the detached seeding browser—renders
  authenticated X DOM, or after a new plan explicitly authorizes a broader
  agent-browser/profile persistence investigation.

## Turn 13 | 2026-07-25

Focus: Plan 0011 Packet 6 X remote-view routing correction.

Authority Consulted:

- operator evidence that the X tile exposed a broken CDP connection rather
  than Guacamole/RDP
- Plan 0011 checkpoint P0011-C06C and its authenticated-browser stop rule
- agent-browser remote-view acquisition contract and live service state
- CodeGraph X and shared browser-runtime acquisition paths
- TDD, validation, documentation, Graphiti, worktree, commit, push, and
  closeout policies

Decisions And Changes:

- Treated the operator's precise transport observation as renewed evidence
  authorizing one bounded deterministic routing correction.
- Proved the X adapter defaulted to `cdp_screencast` and directly opened a
  headed browser instead of using agent-browser's route-bound remote-view
  acquisition.
- Delegated X acquisition to the shared brokered browser-runtime client,
  carrying target identity `x`, the X start URL, and service/task attribution.
- Changed the X default to `rdp_gateway`. The shared path requests remote
  headed execution, private display isolation, control input, and requires
  `operatorVisible.state=ready`.
- Bumped the source candidate to service version 0.2.3.

Validation Evidence:

- regression coverage requires `remote-view open`, `rdp_gateway`, the X start
  URL, and target identity `x`;
- focused X acquisition and acquisition-worker tests passed;
- the full Python suite, Python compilation, and `git diff --check` passed;
- commit `b76bb28` is pushed to `origin/main`;
- the global installed copy exactly matches the committed X adapter and service
  module, and live service version 0.2.3 is ready on schema 12.

Live Route Evidence:

- the broken service-owned browser retained `cdp_screencast` and no
  `remoteViewRouteId`;
- agent-browser reports both Guacamole routes checked out: one by the healthy
  YouTube workspace and one by an orphaned former X reauthentication route;
- `service reconcile` classified that former X route and display allocation as
  orphaned but did not release the pool checkout;
- the installed CLI recommends `service route-pool repair --dry-run` but does
  not expose a `route-pool` subcommand.

State Movement:

- Plan 0011 Packet 6:
  `stalled_loader_recovery_ready -> remote_view_routing_ready`.
- X operator transport:
  `broken_cdp_screencast -> route_bound_guacamole_ready`.

Subagent Status And Reconciliation:

- `not_spawned`; current runtime instructions prohibit delegation unless the
  user explicitly requests it, and this is one bounded adapter seam.

Next Bounded Action:

- authenticate X in the visible Guacamole/RDP browser;
- verify authenticated DOM in the service-owned `last30days-facebook` session;
- run exactly one X content canary only after that human gate clears.

Graphiti Write Status:

- deferred without queueing because the bounded provider-readiness probe
  returned `degraded` with a Codex app-server timeout; the compact checkpoint
  remains in this append-only runbook and should be projected after provider
  recovery.

Live Outcome And Stop:

- agent-browser's MCP `service_request` dry run identified `guacamole:4` as a
  stale former-X route; the narrower
  `service_remote_view_route_release` action released only that route and left
  route B untouched.
- A route-bound `remote-view open` created browser
  `session:last30days-facebook` on display `:10`, route `guacamole:4`, and
  provider `rdp_gateway`.
- The final readback reports browser health `ready`, route state `ready`,
  attachability `attached_ready`, and `operatorVisible.state=ready`.
- After one reload, the tab resolved to `https://x.com/` with the signed-out
  landing DOM: zero authenticated home/navigation markers and one username
  input.
- Stop at the human authentication gate. Do not run an X content canary until
  the operator completes login in this Guacamole/RDP workspace.

## Turn 14 | 2026-07-25

Focus: Plan 0011 Packet 6 recurring-collection acceptance and Packet 7
authority-audit gate.

Authority Consulted:

- Plan 0011 current state, Packet 6 and Packet 7 exit gates, integrated
  acceptance criteria, local attempt bounds, and stop rules
- ROADMAP P01-P06 lane state and RUNBOOK Turn 13
- live service version 0.2.3, schema 12, collection catalog, and durable jobs
- planning, goal execution, roadmap/runbook, validation, Graphiti, worktree,
  commit, push, and closeout policies
- CodeGraph collection specification, due-scheduler, acquisition-loop, and
  persistence paths

Decisions And Changes:

- Identified canonical authority drift: Plan 0011 and roadmap summaries still
  named older installed versions, P04/P05 lacked explicit actionable-plan
  wiring, and no deterministic planning/goal audit existed.
- Added a repo-only authority audit with TDD coverage for open-lane plan
  requirements, exactly one integrated campaign authority, latest checkpoint
  fields, and latest runbook closeout fields.
- Wired Plan 0011 explicitly into P04 and P05 and reconciled current
  source/install/runtime summaries to version 0.2.3.
- Created one bounded public Reddit topic collection spec with assessment
  disabled, immutable spec revisions, a three-item limit, and explicit
  time/network/cost bounds.
- Preserved its first `budget_exhausted` result, revised only its cost ceiling,
  preserved its second `network_budget_exhausted` result, and paused the spec
  at revision 3 when the two-attempt work-unit bound was reached.

Validation Evidence:

- TDD red phase: all three authority-audit tests failed because the audit
  helper did not exist.
- The implemented audit then found four real authority defects: missing P04
  and P05 actionable-plan wiring plus missing subagent and Graphiti fields in
  the latest goal checkpoint.
- The live collection receipts are jobs
  `a0d14a71-5383-402d-8092-69fcf581df14` (`budget_exhausted`) and
  `989b4b90-eff5-4419-848f-5c5b99759325`
  (`network_budget_exhausted`).
- the reconciled authority audit passes with two legitimate open plans,
  exactly one integrated campaign authority, latest runbook Turn 14, and zero
  issues;
- all three focused authority-audit tests, the full Python suite, the full Go
  suite, script compilation, and `git diff --check` pass.

State Movement:

- Plan 0011 Packet 6 timer acceptance:
  `not_configured -> bounded_failure_evidence_preserved_and_paused`.
- Plan 0011 Packet 7 authority acceptance:
  `missing_audit -> deterministic_audit_implemented`.
- Integrated execution authority:
  `summary_drift -> reconciliation_candidate`.

Subagent Status And Reconciliation:

- `not_spawned`; current runtime instructions prohibit delegation unless the
  user explicitly requests it, and the work is a serialized authority and
  timer-control seam.

Graphiti Write Status:

- provider-readiness and compact checkpoint projection remain pending until
  the validated commit exists.

Live Outcome And Stop:

- The public collection spec is disabled and cannot schedule another automatic
  attempt.
- Do not widen its network budget or run a third interval inside this work
  unit. Successful yield and restart recovery require a bounded successor
  decision after the recorded failure evidence is reviewed.
- X remains a separate human-authentication gate in the ready Guacamole/RDP
  workspace.

Next Bounded Action:

- make the authority audit pass against the reconciled repo;
- run focused and broad validation, commit, push, and project the checkpoint
  when Graphiti is healthy;
- then perform an integrated requirement-by-requirement audit and select the
  next unblocked bounded unit without bypassing either stop gate.

## Turn 15 | 2026-07-25

Focus: Plan 0011 Packet 6 shared social-profile acquisition repair.

Authority Consulted:

- Plan 0011 Packet 6 canary gates, local attempt bounds, and adapter-repair
  stop rules
- ROADMAP P01 and P06 current state
- live agent-browser access plan, service state, Guacamole route, browser,
  session, and display readbacks
- durable last30days job, acquisition, work-result, and event records
- TDD, validation, documentation, Graphiti, worktree, commit, push, and
  closeout policies
- CodeGraph shared adapter acquisition, access-plan, and request-construction
  paths

Decisions And Changes:

- Treated fresh Facebook and LinkedIn authenticated DOM as source-specific
  evidence and kept X behind its independent gate.
- Preserved failed Facebook job `74ce82f7-191c-4a41-94e6-1ef7afd18ab9`
  after its two internal attempts rather than submitting another canary.
- Attributed the failure to a deterministic request mismatch: the adapters
  asked the broker for `private_virtual_display` while the retained
  authenticated Guacamole browser is intentionally on `shared_display`.
- Passed the complete remote-view transport contract into access planning and
  selected `shared_display` for X, Facebook, and LinkedIn post/profile
  acquisition.
- Bumped the user-visible service to version 0.2.4, synced the repaired tree
  into the frozen user-scoped install, and restarted the service.

Validation Evidence:

- Live X/Facebook/LinkedIn owner:
  `session:last30days-facebook`, `remote_headed`, display `:10`, provider
  `rdp_gateway`, route `guacamole:4`, health and operator visibility ready.
- Before repair, access planning reported `wait_for_profile_lease`,
  `active_profile_lease_conflict`, and `no_compatible_live_browser`.
- With `shared_display`, the same live plan reports
  `reuse_existing_browser`, shared acquisition mode `tab_new`, and route hints
  for `session:last30days-facebook`.
- The no-navigation adapter acquisition probe reused that exact browser and
  session.
- 88 focused tests pass with 3 skips; the full suite passes with 2,289 tests,
  7 skips, and 6 passing subtests.
- Installed adapter files byte-match the working tree; the restarted service
  reports ready, version 0.2.4, schema 12.
- Facebook job `ecea393f-c445-461d-9528-99c2107190f1` published in one
  attempt with three items from
  `work-d211f861234870f78e05fd069274d3c1`.
- LinkedIn post job `91b55c9f-3827-4046-9c87-0df99ec54f40` failed after two
  internal attempts with `agent_browser_error`; both durable acquisition
  envelopes contain zero items.

State Movement:

- Shared social-profile acquisition:
  `display_constraint_mismatch -> retained_browser_reuse_ready`.
- Facebook live acceptance:
  `terminal_adapter_failure_preserved -> published_three_items`.
- LinkedIn live acceptance:
  `auth_proven_canary_withheld -> post_adapter_failure_preserved`.

Subagent Status And Reconciliation:

- `not_spawned`; current runtime instructions prohibit delegation unless the
  user explicitly requests it, and this work is one serialized shared-profile
  routing seam.

Graphiti Write Status:

- deferred after a second provider-readiness timeout from the Codex app-server;
  no write was queued while provider readiness was degraded.

Live Outcome And Stop:

- No second pre-repair Facebook job was run. The one post-repair Facebook
  verification succeeded, and no further Facebook job is authorized.
- The one LinkedIn post canary exhausted its two internal attempts. Do not
  submit another LinkedIn post job or run the LinkedIn profile canary without a
  new bounded repair decision.
- X remains gated on authenticated DOM in the same service-owned Guacamole/RDP
  browser.

Next Bounded Action:

- diagnose the preserved LinkedIn post failure without another live canary;
- define a bounded source-specific repair decision before changing code or
  authorizing another LinkedIn attempt;
- keep the LinkedIn profile canary withheld until the post adapter clears.

## Turn 16 | 2026-07-25

Focus: Plan 0011 Packet 6 deterministic adapter-failure evidence and App
Intelligence repair gating.

Authority Consulted:

- Plan 0011 Packet 6 canary gates and Plan 0010 Packet 3 adapter-repair
  contracts
- app-intelligence-automation decision schemas and adapter composition
  guidance
- live retained LinkedIn browser/auth readbacks
- TDD, validation, documentation, Graphiti, worktree, commit, push, and
  closeout policies
- CodeGraph task-contract registry and result-validation paths

Decisions And Changes:

- A no-navigation LinkedIn probe succeeded through tab discovery, tab
  selection, authentication inspection, and DOM evaluation on the retained
  feed.
- The preserved failed canary contains no stage or operation evidence, so it
  does not justify a code-defect or site-change classification.
- Acquisition failures now receive a stable host-computed signature from safe
  error dimensions and retain a bounded stage plus sanitized browser operation
  timings when available.
- Added strict contracts for adapter failure triage, repair recommendation, and
  branch decision. Host validation permits only `site_change` and
  `code_defect` to route into code repair.

Validation Evidence:

- 41 focused tests pass with 1 skip.
- The full suite passes with 2,293 tests, 7 skips, and 6 passing subtests.
- Stable-signature tests vary attempt and job identifiers while retaining the
  same signature.
- Contract tests reject auth-to-code-repair routing, parent-directory target
  paths, and branch selection without a branch identifier.
- The authority audit passes with 2 active plans, 1 campaign plan, Turn 16
  current, and zero issues.
- Commit `c52918e` is pushed to `origin/main`; the installed service source
  byte-matches it and the restarted service reports ready, version 0.2.5,
  schema 12.

State Movement:

- LinkedIn failure attribution:
  `untyped_agent_browser_error -> insufficient_evidence_observe`.
- Adapter repair governance:
  `caller_supplied_failure_fingerprint -> host_computed_typed_triage`.

Subagent Status And Reconciliation:

- `not_spawned`; current runtime instructions prohibit delegation unless the
  user explicitly requests it, and this work is one coupled
  diagnostics/contract seam.

Live Outcome And Stop:

- No LinkedIn post or profile canary was run.
- The profile canary remains withheld. A future version 0.2.5 failure can be
  correlated and classified before any repair automation is authorized.

Graphiti Write Status:

- provider readiness remains degraded with a Codex app-server timeout; no
  write was queued.

Next Bounded Action:

- resume Packet 6 under a newly bounded live decision that uses version
  0.2.5 failure evidence.

## Turn 17 | 2026-07-25

Focus: Plan 0011 Packet 6 recurring collection and restart recovery.

Authority Consulted:

- Plan 0011 Packet 6 timer acceptance gates and two-attempt stop rule
- live collection specification, schedule, job, service, and index readbacks
- validation, Graphiti, worktree, commit, push, and closeout policies

Decisions And Changes:

- Preserved exhausted collection revision 3 and created successor revision 4
  with the same interval, lookback, item, cost, and wall-time limits.
- Raised only the network-request limit from 10 to 50 based on the prior typed
  budget failure.
- Restarted the service only after the first successor job reached published.
- Paused the one-minute cadence as immutable revision 5 immediately after the
  post-restart scheduled interval published.

Validation Evidence:

- Job `f36014c9-8749-41af-b483-a950099b3db7` published in one attempt for one
  cent before restart.
- The restarted version 0.2.5 service returned active, ready, schema 12.
- Timer job `15719900-3b9d-46ec-a8f7-6ef9cf68fecb` published in one attempt
  for one cent at the next scheduled minute.
- Re-resolving that boundary returned the same collection run/job, proving
  durable interval deduplication.
- The schedule reports zero consecutive failures; revision 5 is disabled.

State Movement:

- Recurring timer acceptance:
  `typed_budget_failure -> consecutive_published_intervals`.
- Restart recovery:
  `unproven -> scheduled_interval_published_after_restart`.

Subagent Status And Reconciliation:

- `not_spawned`; current runtime instructions prohibit delegation unless the
  user explicitly requests it, and this work is one serialized timer/restart
  seam.

Graphiti Write Status:

- deferred; provider readiness remains degraded with a Codex app-server
  timeout, so no write was queued.

Live Outcome And Stop:

- Timer/restart acceptance is complete.
- The acceptance collection is paused and must not be resumed.
- X and LinkedIn retain their independent browser/canary gates.

Next Bounded Action:

- verify X authenticated DOM in the exact service-owned Guacamole/RDP browser,
  then choose one bounded X canary or record the typed blocker.

## Turn 18 | 2026-07-25

Focus: Plan 0011 Packet 6 X auth attribution and modern login detector.

Authority Consulted:

- Plan 0011 X browser gate and one-canary stop rule
- agent-browser profile lookup, access plan, browser, tab, route, and operator
  visibility readbacks
- installed X adapter auth contract and live safe DOM landmarks
- TDD, validation, Graphiti, worktree, commit, push, and closeout policies
- CodeGraph X auth detector, workspace acquisition, and search paths

Decisions And Changes:

- Agent-browser selected `last30days-facebook` by X target identity and reused
  `session:last30days-facebook` on display `:10`, Guacamole route 4,
  `rdp_gateway`, and `shared_display`.
- The current page is conclusively X's signed-out root surface, not a
  checkpoint, restriction, or transient load failure.
- The adapter also had a deterministic defect: its legacy selectors did not
  type the modern root login form, so it performed an unnecessary ambiguous
  refresh.
- Added a root-route plus multi-signal modern sign-in detector to both auth and
  search-page state scripts.

Validation Evidence:

- Live page evidence includes “Happening now”, provider continuation buttons,
  and “Email or username”, with no authenticated primary navigation.
- The pre-fix adapter returned all terminal flags false after its bounded
  refresh, reproducing the classification defect.
- The targeted regression failed before implementation, then the X and
  acquisition-worker suite passed 22 tests with 1 skip.
- The full suite passes with 2,294 tests, 7 skips, and 6 passing subtests.
- Commit `ad1abd4` is pushed to `origin/main`, the installed X adapter
  byte-matches it, and the restarted service reports ready, version 0.2.6,
  schema 12.
- The installed post-fix probe returns `login_form=true` in one evaluation
  without fallback navigation.
- No X content canary ran.

State Movement:

- X auth attribution:
  `ambiguous_adapter_result -> genuine_operator_auth_gate`.
- X login classification:
  `modern_root_form_unrecognized -> typed_login_form`.

Subagent Status And Reconciliation:

- `not_spawned`; current runtime instructions prohibit delegation unless the
  user explicitly requests it, and this work is one serialized auth/detector
  seam.

Graphiti Write Status:

- deferred; provider readiness remains degraded with a Codex app-server
  timeout, so no write was queued.

Live Outcome And Stop:

- The existing Guacamole/RDP browser remains visible and controllable.
- X content acquisition is stopped until the operator restores auth in that
  exact browser.
- No duplicate profile or browser lane is authorized.

Next Bounded Action:

- advance the independent LinkedIn evidence lane while X waits at the
  operator gate.

## Turn 19 | 2026-07-25

Focus: Plan 0011 Packet 6 bounded LinkedIn version 0.2.6 post canary decision.

Authority Consulted:

- Plan 0011 checkpoints C06G through C06I
- installed service version 0.2.6 and retained LinkedIn/X tab evidence
- version 0.2.5+ stable failure diagnostics and typed adapter triage contracts
- validation, Graphiti, worktree, commit, push, and closeout policies

Decisions And Changes:

- Authorized one LinkedIn post canary with caller key
  `p0011-c06j-linkedin-post-v026`, topic `OpenAI`, and the retained
  `last30days-facebook` browser.
- Preserved the service's two-attempt ceiling and prohibited another job,
  duplicate browser lane, or profile canary unless the post job publishes.

Validation Evidence:

- The prior read-only LinkedIn auth probe succeeded on the retained feed tab.
- Service version 0.2.6 is active and ready on schema 12.
- X is independently stopped at its operator-auth gate.

State Movement:

- LinkedIn post acceptance:
  `insufficient_failure_evidence -> one_diagnostic_canary_authorized`.

Subagent Status And Reconciliation:

- `not_spawned`; current runtime instructions prohibit delegation unless the
  user explicitly requests it, and this is one serialized shared-browser
  canary.

Graphiti Write Status:

- deferred; provider readiness remains degraded with a Codex app-server
  timeout, so no write was queued.

Live Outcome And Stop:

- No canary has run at this checkpoint.
- Published, failed, and awaiting-operator outcomes have explicit stop
  branches in Plan 0011 C06J.

Next Bounded Action:

- commit the decision, submit the one keyed LinkedIn post query, and preserve
  its durable terminal evidence.

## Turn 20 | 2026-07-25

Focus: reconcile the executed LinkedIn canary and repaired agent-browser route
authority.

Authority Consulted:

- Plan 0011 checkpoint C06J and current durable service jobs/acquisition
  envelopes
- installed agent-browser access planning, retained browser, profile
  readiness, and rendered Guacamole proof
- agent-browser commits `3c08b9b0` and `047f0c7d`
- planning, validation, documentation, Graphiti, worktree, commit, push, and
  closeout policies

Decisions And Changes:

- The C06J job had already executed before the current CLI replay; its caller
  key is terminal and must not be reused.
- Both attempts failed at workspace acquisition with the same stable
  signature before any LinkedIn auth or page evaluation.
- The failure-time broker record selected a new CDP lane. The repaired current
  broker plan instead selects the retained shared browser, Guacamole/RDP, and
  `tab_new`.
- Authorized one newly keyed post-repair LinkedIn post canary. The profile
  canary remains gated on successful post publication.
- Corrected stale X authority: fresh agent-browser readiness records an
  authenticated retained-browser probe with four accepted posts, while the
  content-service X canary remains pending.

Validation Evidence:

- job `c2efdf4b-193a-403e-93bf-8cae4ec3ef72` is terminal failed after two
  internal attempts with `agent_browser_error`;
- both acquisition envelopes use signature
  `sha256:c1c6d0ff8a494273a826a1aa7bd837ac915fb7e8af0f35670cf007510b365376`
  and stage `workspace_acquisition`;
- current LinkedIn access planning returns
  `session:last30days-facebook`, `tab_new`, `rdp_gateway`,
  `manual_attached_desktop`, and `shared_display`;
- installed `shared_acquisition_route()` returns the exact retained browser
  and session hints;
- last30days service v0.2.6/schema 12 and its ten-tool MCP surface are ready.

State Movement:

- LinkedIn post acceptance:
  `diagnostic_canary_authorized -> external_route_failure_attributed`.
- Shared-browser dependency:
  `new_cdp_lane_planned -> retained_rdp_tab_reuse_proven`.
- X browser gate:
  `operator_auth_pending -> authenticated_probe_fresh`.

Subagent Status And Reconciliation:

- `not_spawned`; current runtime instructions prohibit delegation unless the
  user explicitly requests it, and this is one serialized shared-browser
  lane.

Graphiti Write Status:

- deferred; the latest provider readiness check timed out, so no write was
  queued.

Next Bounded Action:

- commit and push this corrected authority, run the one C06K LinkedIn post
  canary, and follow only its recorded terminal branch.

## Turn 21 | 2026-07-25

Focus: repair the stale user-scoped LinkedIn provider override and stop the
repeated-failure lane.

Authority Consulted:

- Plan 0011 checkpoint C06K
- C06K durable job and acquisition envelopes
- user-scoped last30days environment and active service process environment
- installed adapter defaults and no-navigation workspace acquisition
- current agent-browser LinkedIn access plan and retained RDP browser

Decisions And Changes:

- The one authorized C06K job failed with the same stable signature as C06J.
- The remaining cause was not LinkedIn authentication: the user-scoped service
  still overrode the repo's RDP default with `cdp_screencast`.
- Updated the user-scoped override to `rdp_gateway` and restarted the service.
- Proved the installed adapter now returns the retained browser after one
  service read without calling `remote-view`.
- Activated the repeated-failure stop rule for LinkedIn and authorized one
  independent X content-service canary against its fresh authenticated
  retained profile.

Validation Evidence:

- C06K job `19a5860d-eea1-4552-993f-65f563041756` is terminal failed after two
  internal attempts;
- both new envelopes retain stage `workspace_acquisition` and signature
  `sha256:c1c6d0ff8a494273a826a1aa7bd837ac915fb7e8af0f35670cf007510b365376`;
- the active service process reports
  `LAST30DAYS_LINKEDIN_VIEW_PROVIDER=rdp_gateway`;
- v0.2.6/schema 12 returned ready after restart;
- installed no-navigation acquisition selected
  `session:last30days-facebook` with one successful service operation and no
  remote-view operation.

State Movement:

- LinkedIn route attribution:
  `external_route_failure -> stale_user_provider_override`.
- LinkedIn acceptance:
  `post_repair_retry_failed -> repeated_failure_stop`.
- X acceptance:
  `authenticated_probe_fresh -> one_service_canary_authorized`.

Subagent Status And Reconciliation:

- `not_spawned`; current runtime instructions prohibit delegation unless the
  user explicitly requests it, and this is one serialized shared-browser
  lane.

Graphiti Write Status:

- deferred; provider readiness remains degraded and no write was queued.

Next Bounded Action:

- commit and push this checkpoint, run the one C06L X canary, and follow only
  its terminal branch.

## Turn 22 | 2026-07-25

Focus: attribute the failed X service canary and authorize a registered-session
control-plane repair.

Authority Consulted:

- Plan 0011 checkpoint C06L
- C06L durable job and acquisition envelopes
- installed X adapter and shared browser runtime
- current agent-browser X access plan, service state, and CLI control paths

Decisions And Changes:

- The one authorized C06L X job failed after two internal attempts with one
  stable `adapter_result` signature.
- Workspace acquisition itself selects the correct healthy retained browser.
- The next registered-session client command is not attached to that browser;
  it attempts to launch the unrelated default profile and collides with
  `auracall-corel`.
- A distinct diagnostic client attached explicitly to the retained CDP
  endpoint can list the authenticated X tab, proving this is neither an X auth
  failure nor a Guacamole/RDP failure.
- Authorized a bounded agent-browser registered-session reconnection repair,
  its install verification, and one no-navigation X auth readback. No further
  social content job is authorized.

Validation Evidence:

- C06L job `1bcc32c3-9fd4-480f-a8ef-aaac25a5354a` is terminal failed with
  signature
  `sha256:d540fd31eda485872f608d59bcf715cadfd4ae0f60cd53962c7321a7687ed3c7`;
- acquisition returns `session:last30days-facebook`;
- registered-session tab selection fails on default-profile auto-launch;
- explicit retained-CDP attachment lists `https://x.com/home`;
- service state retains a viable RDP browser on Guacamole route `guacamole:4`.

State Movement:

- X acceptance:
  `one_service_canary_authorized -> stable_client_attachment_failure`.
- Shared browser attribution:
  `possible_adapter_result_bug -> registered_session_not_attached`.
- Repair authority:
  `diagnosis_only -> bounded_agent_browser_repair_authorized`.

Subagent Status And Reconciliation:

- `not_spawned`; current runtime instructions prohibit delegation unless the
  user explicitly requests it.

Graphiti Write Status:

- deferred; provider readiness remains degraded and no write was queued.

Next Bounded Action:

- commit and push C06M, repair agent-browser test-first, install it, and run
  only the authorized no-navigation X authentication readback.
