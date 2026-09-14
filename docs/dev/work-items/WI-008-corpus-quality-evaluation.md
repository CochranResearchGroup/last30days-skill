<!-- last30days-work-item:WI-008 -->
# Measure corpus and retrieval quality continuously

State: IN_PROGRESS
Priority: P2
Lane: Quality
Parent: WI-000
GitHub issue: https://github.com/CochranResearchGroup/last30days-skill/issues/60
Blocked by: none for the provider-free grounding/quality closeout packet
Architecture: docs/dev/notes/0121-2026-09-13-corpus-retrieval-and-grounding-quality-architecture.md
Implementation plan seed: docs/dev/plans/0080-2026-09-13-corpus-retrieval-and-grounding-quality-architecture-and-lane-handoff.md
Last closed plan: docs/dev/plans/0119-2026-09-14-service-quality-real-adapters.md
Current plan: docs/dev/plans/0122-2026-09-14-service-quality-grounding-closeout.md
Branch: feat/service-quality-grounding-closeout-v1
Owner: /root/wave4_wi008_plan

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
closes. The plan is `OPEN` at published activation `24614a18`. Keep judge
calls, production samples, providers, installed runtimes, CI changes, staging,
and production behind their own explicit gates.

Packet 2 integrated through reviewed PR 91 as canonical merge `f413458b`.
Digest-pinned immutable fixtures now drive real acquisition, corpus and
PostSearch adapters with candidate-head, content, owner, partition and WAL
closure. WI-008 returns to `READY`; answer-grounding is now dependency-ready
because WI-003 is `DONE`, but requires a separately bounded packet.
