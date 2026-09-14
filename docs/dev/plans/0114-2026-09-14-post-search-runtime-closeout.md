# Plan 0114 | Post Search Runtime Closeout Packet 4

State: PLANNED
Lane: P33
Work item: WI-002
Branch: feat/post-search-runtime-closeout-v1
Target: main
Integration: merge
Roadmap: P33
Plan version: 1
Date: 2026-09-14
Execution owner: unassigned
Coordination owner: /root
Requested model route: gpt-5.6-terra, medium reasoning
Effective runtime model: unknown until reported

## Objective

Close WI-002 provider-free by proving the integrated stored-post search product
through a fresh MCP client against an exact versioned isolated development
runtime, with stable HTTP/MCP behavior, immutable evidence, and exact teardown.

## Current State

Plans 0108 and 0111 are integrated. Search already supports both storage
families, full filters, revisions, deduplication, deterministic hybrid ranking,
bounded pagination, HTTP/MCP parity fixtures, and a frozen 10,000-post
performance sample. Remaining acceptance is versioned isolated-runtime and
fresh-client product proof, not another ranking redesign.

## Scope

- add a repo-only search dogfood probe reusable against an isolated runtime;
- prove fresh MCP discovery and typed HTTP/MCP equivalence across both stores;
- exercise filters, revisions, dedupe, empty/malformed/partition behavior,
  retained pagination, publication, restart-stale cursors, and read-only state;
- bind runtime artifact, source commit, schema, manifest, and contract digests;
- retain a bounded acceptance receipt and finish search guidance if needed.

## Non-Goals

No ranking tuning, new embedding provider, live acquisition, browser, installed
service, staging, production, release publication, schedule, issue mutation, or
WI-003 question transport.

## Acceptance Criteria

1. Fresh MCP discovery exposes `search_posts` against the exact runtime build.
2. HTTP and MCP return equivalent stable evidence across both storage families.
3. Full filters, current/all revisions, dedupe, empty/malformed requests, and
   access partitions pass at the public boundary.
4. Pagination survives publication and fails `cursor_stale` after restart.
5. Corpus, acquisition, and schedule state are unchanged by every probe.
6. Runtime identity and teardown receipts prove the exact artifact/source and
   an empty owned-process census.
7. Focused, package, full Python, Go test/vet, audits, and diff checks pass.

## Ownership And Topology

One top-level implementation owner, no children, at most two implementation
attempts, one independent review, and one closed-world remediation. Lane writes
are a repo-only search probe, focused acceptance fixtures/tests, branch-local
plan, and narrow search guidance. Catalogs, manifests, version metadata, shared
authority, and integration remain coordinator-owned.

## Stop Rules

Stop on ambiguous runtime/process custody, source or artifact mismatch, shared
transport changes required for WI-003, cursor semantics drift, provider/live
effects, or a need to rerun the frozen performance experiment without a
demonstrated invalidation.

## Definition Of Done

All seven criteria pass at a reviewed integrated checkpoint and WI-002 is
truthfully eligible for `DONE` without claiming installed or live acceptance.
