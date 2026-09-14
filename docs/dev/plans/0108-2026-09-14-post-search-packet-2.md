# Plan 0108 | Post Search Packet 2

State: PLANNED
Lane: P33
Work item: WI-002
Branch: feat/post-search-v2
Target: main
Integration: merge
Roadmap: P33
Plan version: 1
Date: 2026-09-14
Requested model route: gpt-6-astra, high reasoning
Effective runtime model: unknown until reported

## Objective

Complete WI-002 Packet 2 by extending the integrated cache-only post search
through author, topic, namespaced collection, observed-time, filter-only,
all-revision, and cross-store identity semantics with stable multi-page
traversal.

## Current State

Packet 1 is integrated at `75e7771e` with strict lexical current-revision
contracts, both storage families, source/access/publication filters, cursor,
HTTP, MCP, and provider-free fixtures. This packet has not started.

## Scope

- implement every Packet 2 filter on both storage adapters before ranking;
- support current/all revision modes and explicit immutable revision identity;
- deduplicate cross-store source-native collisions without losing provenance;
- prove deterministic duplicate-free multi-page traversal pinned to component
  heads, including concurrent fixture publication and stale/mismatched cursors;
- preserve HTTP/MCP parity and `/v1/query` behavior.

## Non-Goals

- no semantic/RRF packet, 10,000-post performance campaign, release/version,
  installed runtime, provider/browser, live data, schedule, or production;
- no WI-003 answer-semantics change.

## Acceptance Criteria

1. Both storage families enforce author, topic, collection, observed-time, and
   filter-only requests before ranking without access widening.
2. Current/all revision and cross-store collision fixtures preserve exact
   identity, revisions, causes, and evidence refs.
3. Multi-page traversal is stable, complete, deterministic, and duplicate-free
   across immutable heads; invalid or stale cursor replay fails closed.
4. Python service and Go MCP focused/compatibility suites pass and `/v1/query`
   remains unchanged.
5. The accepted branch is published for coordinator review with no external
   runtime or provider effect.

## Definition Of Done

All five criteria pass at one published checkpoint suitable for reviewed PR
integration, or one exact blocker is recorded without beginning Packet 3.

## Stop Rules

- stop before shared WI-003 answer changes, semantic ranking, runtime, provider,
  schedule, issue, release, staging, or production effects;
- stop and notify the coordinator before editing coordinator-owned projections,
  generated catalogs, or a conflicting shared schema.
