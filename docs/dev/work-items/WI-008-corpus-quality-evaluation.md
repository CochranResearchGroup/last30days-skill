<!-- last30days-work-item:WI-008 -->
# Measure corpus and retrieval quality continuously

State: READY
Priority: P2
Lane: Quality
Parent: WI-000
GitHub issue: https://github.com/CochranResearchGroup/last30days-skill/issues/60
Blocked by: none for Packet 1; retrieval acceptance by WI-002 closeout; grounding integration by WI-003 Packet 3 and acceptance by WI-003 closeout
Architecture: docs/dev/notes/0121-2026-09-13-corpus-retrieval-and-grounding-quality-architecture.md
Implementation plan seed: docs/dev/plans/0080-2026-09-13-corpus-retrieval-and-grounding-quality-architecture-and-lane-handoff.md
Last closed plan: docs/dev/plans/0092-2026-09-13-service-quality-packet-1.md
Current plan: docs/dev/plans/0119-2026-09-14-service-quality-real-adapters.md (planned)
Branch: feat/service-quality-real-adapters-v1 (planned; custody not yet published)
Owner: unassigned until activation

## Problem

Retrieval can appear healthy while provenance, freshness, coverage, dedupe, or
grounding quality silently regresses across sources.

## Outcome / Proposed Solution

Maintainers can see provenance completeness, freshness, duplication, coverage,
retrieval relevance, and source-specific failure rates before those defects
silently degrade agent answers.

## Acceptance Evidence

- a versioned provider-free evaluation set covers supported services, sparse
  evidence, revisions, duplicates, and known hard queries;
- reports separate acquisition coverage, corpus integrity, retrieval quality,
  and answer grounding;
- thresholds and denominators are explicit, failed cases remain inspectable,
  and comparisons bind to code/config/index versions;
- no metric is labeled production quality without a current production-bound
  sample and receipt;
- regression output is suitable for CI and human review.

## Non-Goals

No automatic model promotion, data deletion, or live-provider expansion based
only on a score.

## Next Owner Action

Packet 1 integrated through PR 41 as canonical merge `6d5eb5d9`. Plan 0119
now registers read-only real-fixture corpus-integrity, acquisition-coverage,
and PostSearch quality adapters; grounding remains deferred until WI-003
closes. The plan remains `PLANNED` until exact custody is published. Keep judge
calls, production samples, providers, installed runtimes, CI changes, staging,
and production behind their own explicit gates.
