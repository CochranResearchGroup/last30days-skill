<!-- last30days-work-item:WI-008 -->
# Measure corpus and retrieval quality continuously

State: IN_PROGRESS
Priority: P2
Lane: Quality
Parent: WI-000
Blocked by: none for Packet 1; retrieval acceptance by WI-002 closeout; grounding integration by WI-003 Packet 3 and acceptance by WI-003 closeout
Architecture: docs/dev/notes/0121-2026-09-13-corpus-retrieval-and-grounding-quality-architecture.md
Implementation plan seed: docs/dev/plans/0080-2026-09-13-corpus-retrieval-and-grounding-quality-architecture-and-lane-handoff.md
Current plan: docs/dev/plans/0092-2026-09-13-service-quality-packet-1.md
Branch: feat/service-quality-v1
Owner: Codex 01a09cf4-c89d-7b41-901a-37648171312a

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

## Ready Handoff

Assign one independent top-level lane session. Start from current
`origin/main`, create and register `feat/service-quality-v1`, and implement
Packet 1 from the architecture note: strict evaluation-set, threshold-policy,
request/report, metric/result, effect, and artifact contracts; deterministic
IDs/digests; fake four-axis adapters; JSON/Markdown projection; CLI exit
semantics; and provider-free self-tests. Do not start a service, call a judge,
read a live database, use a provider/browser, install a runtime, edit CI, or
touch staging/production in Packet 1.
