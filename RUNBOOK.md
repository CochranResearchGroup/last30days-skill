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
