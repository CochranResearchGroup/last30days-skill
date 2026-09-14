# Plan 0111 | Bounded Hybrid Post Search Packet 3

State: PLANNED
Lane: P33
Work item: WI-002
Branch: feat/post-search-v3
Target: main
Integration: merge
Roadmap: P33
Plan version: 1
Date: 2026-09-14
Execution owner: unassigned until activation
Coordination owner: /root
Requested model route: gpt-6-astra, high reasoning
Effective runtime model: unknown until reported

## Objective

Complete WI-002 Packet 3 with provider-free semantic candidates,
deterministic reciprocal-rank fusion, reproducible explanations, bounded
responses and coverage diagnostics, plus measured 10,000-post local evidence.

## Current State

Packets 1-2 are integrated through PRs 36 and 79. Both storage families,
complete filters, current/all revisions, cross-store identity, and stable
snapshot pagination exist. Ranking remains lexical-only; the existing 10,000
candidate and 32 MiB limits are admission controls, not performance evidence.

## Scope

- rank authorized prefiltered candidates through lexical and local deterministic
  semantic channels without creating embeddings or inheriting provider access;
- fuse independently ordered channels through a versioned deterministic RRF
  contract with reproducible component ranks, scores, and stable tie breaks;
- preserve exact revision/evidence identity, access partitions, retained cursor
  inputs, and explicit semantic coverage/degradation for both storage families;
- fit complete UTF-8 responses beneath the existing transport bound without
  skipping hits across budget-shortened pages;
- baseline first, then freeze and prove explicit latency/RSS budgets on one
  opt-in synthetic 10,000-post fixture split across both families;
- keep Python, HTTP, MCP, Skill, and configuration guidance aligned.

## Non-Goals

No materialized unified index, schema migration, general provider embedding
plumbing, durable cursor redesign, WI-003 answer change, release/version,
installed runtime, provider/browser, schedule, staging, or production effect.

## Acceptance Criteria

1. Semantic-only, lexical-only, dual-channel, tied, zero-vector, and missing or
   mismatched-vector fixtures reproduce deterministic RRF order and coverage.
2. Unauthorized and filtered-out candidates never reach either ranker; current/
   all collisions cannot promote stale matching revisions.
3. Cursor pages pin ranking inputs and remain stable across publication or
   semantic metadata change; existing tamper/access/expiry cases stay green.
4. Complete serialized responses fit the transport limit or fail with one
   stable bounded error; concatenated shortened pages equal logical order.
5. Python application/HTTP and fresh Go MCP clients agree, WI-003 evidence and
   `/v1/query` compatibility remain green, and no effectful call is admitted.
6. A durably recorded baseline precedes the frozen 10,000-post latency/RSS
   budget, and the final opt-in fixture meets it without erasing correctness
   evidence on a performance failure.
7. The exact clean branch checkpoint is published for coordinator review.

## Execution Packet

- one top-level implementation owner, no children; two implementation attempts,
  one independent broad review, and one closed-world remediation pass;
- lane-owned writes: post-search backend or narrow ranking module, focused
  search/ranking/performance fixtures and tests, this plan;
- coordinator-assigned overlaps: search-specific Python contract/schema, app
  wiring only if required, MCP search tool/tests, and search guidance;
- coordinator-exclusive: generated catalogs, runtime manifest, roadmap,
  runbook, active lanes, and work-item state;
- terminal condition: published source acceptance for Packet 3 or one exact
  recorded blocker; do not begin Packet 4.

## Definition Of Done

All seven criteria pass at one published checkpoint suitable for joined review,
or one exact blocker is recorded without widening the packet.

