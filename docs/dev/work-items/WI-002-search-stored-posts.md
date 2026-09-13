<!-- last30days-work-item:WI-002 -->
# Search and retrieve stored posts as a product surface

State: IN_PROGRESS
Priority: P1
Lane: Search
Parent: WI-000
Blocked by: none
Architecture: docs/dev/notes/0117-2026-09-13-post-search-product-architecture.md
Implementation plan seed: docs/dev/plans/0076-2026-09-13-post-search-architecture-and-lane-handoff.md
Active plan: docs/dev/plans/0084-2026-09-13-post-search-packet-1.md
Branch: feat/post-search-v1

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

Resume the owning top-level session from published checkpoint
`49e9bb02377011b6dc6a28da27b15f0996acd6de` and implement only Packet 1's
strict contract/catalog/cursor lexical tracer. Do not change `/v1/query`,
install a runtime, or use provider/browser access in that packet.
