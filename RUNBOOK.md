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
