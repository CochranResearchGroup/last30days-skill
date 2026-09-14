<!-- last30days-work-item:WI-002 -->
# Search and retrieve stored posts as a product surface

State: READY
Priority: P1
Lane: Search
Parent: WI-000
GitHub issue: https://github.com/CochranResearchGroup/last30days-skill/issues/53
Blocked by: none
Architecture: docs/dev/notes/0117-2026-09-13-post-search-product-architecture.md
Implementation plan seed: docs/dev/plans/0076-2026-09-13-post-search-architecture-and-lane-handoff.md
Last completed plan: docs/dev/plans/0111-2026-09-14-post-search-packet-3.md
Planned plan: docs/dev/plans/0114-2026-09-14-post-search-runtime-closeout.md
Branch: main

## Problem

Scraped posts exist durably, but consumers do not yet have one post-oriented,
evidence-preserving product contract for finding and filtering them.

## Outcome / Proposed Solution

A user or agent can query the existing scraped-post corpus through one stable
service contract and receive ranked post-level results with temporal and
source provenance.

## Acceptance Evidence

- one end-to-end query crosses the supported stored corpus rather than raw
  scrape files;
- lexical and semantic retrieval have deterministic provider-free fixtures;
- filters cover service, author/account, collection, topic, and observed or
  published time where the corpus has that evidence;
- results preserve stable identity, revision, source URL, collection cause,
  and ranking explanation without fabricating missing fields;
- pagination, deduplication, empty results, malformed queries, and access
  partitions are tested at the public service boundary;
- slash-command and direct service documentation show the same contract.

## Non-Goals

No new live scraping, automatic follow scheduling, or free-form synthesized
answers in this slice.

## Active Handoff

Packet 1 merged through PR 36 as `75e7771e006f52847e8e47c1059b2b2000fb8ac7`.
The coordinator should register a separate Packet 2 plan before adding the
broader filter matrix, all-revision traversal, or cross-store deduplication.
Do not change `/v1/query` or use provider/browser access under Packet 1.

Packet 2 was activated at checkpoint `0d06d8e2` under Plan 0108 and completed
the broader filter matrix, revision traversal, cross-store identity, stable
pagination, and focused public-boundary compatibility.

Packet 2 integrated through PR 79 at canonical `fae31198` after independent
review and joined acceptance. Next work is a separately planned Packet 3 for
semantic/RRF ranking and bounded 10,000-post performance evidence.

Packet 3 is active at published plan-only checkpoint `f1f5f4dd`; product work
remains held until the coordinator integrates this custody projection.

Packet 3 integrated through reviewed PR 83 as canonical merge `5aec7324` from
source acceptance `971f9ea9`. Hybrid ranking, semantic coverage, bounded
pagination, public MCP parity, and the frozen 10,000-post performance gate pass.
WI-002 returns to `READY` for a separately planned Packet 4 isolated-runtime
and fresh-client product closeout; no provider or installed-runtime authority
is implied.

Plan 0114 now freezes that final provider-free closeout. It remains `PLANNED`
until exact branch/worktree custody is published and reconciled.
