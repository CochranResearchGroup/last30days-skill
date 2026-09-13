<!-- last30days-work-item:WI-002 -->
# Search and retrieve stored posts as a product surface

State: READY
Priority: P1
Lane: Search
Parent: WI-000
Blocked by: none
Architecture: docs/dev/notes/0117-2026-09-13-post-search-product-architecture.md
Implementation plan seed: docs/dev/plans/0076-2026-09-13-post-search-architecture-and-lane-handoff.md

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

## Ready Handoff

Assign one independent top-level lane session. Start from current
`origin/main`, create a dedicated `feat/post-search-v1` worktree, register its
active custody, measure the provider-free 10,000-post baseline, and implement
Packet 1 from the architecture note. Do not change `/v1/query`, install a
runtime, or use provider/browser access in that packet.
