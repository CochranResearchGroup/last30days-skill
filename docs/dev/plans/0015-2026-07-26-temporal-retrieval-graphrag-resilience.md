# Plan 0015 | Temporal retrieval and GraphRAG resilience

State: PLANNED
Roadmap: P04
Supports: P05
Date: 2026-07-26
Predecessor: Plan 0011
Transition authority: Plan 0018

## Objective

Prove from a fresh MCP client that cache-only temporal/profile retrieval does
not enqueue acquisition and that Graphiti projection replay is idempotent while
SQLite-only evidence retrieval remains usable during projection-provider
unavailability.

This is a service-product acceptance packet under Plan 0018. It does not add a
Skill feature or permit an agent to operate retrieval providers, graph
maintenance, or acquisition mechanics.

## Current State

- Version 0.2.7 exposes cache-only temporal, dossier, timeline, trend, profile,
  coverage, collection, and maintenance contracts through ten MCP tools.
- Integrated acceptance proved one cache-only query and one durable Graphiti
  projection receipt.
- Broader `as_of` plus profile filtering, projection replay, and an intentional
  provider-unavailable fallback have not been accepted as one successor packet.

## Scope

- snapshot current job, index, projection, and evidence state;
- issue one fresh-client cache-only topic query with temporal `as_of` and
  profile/access filters;
- verify exact immutable citations and no acquisition enqueue;
- replay one existing projection idempotently and verify Graphiti readback;
- exercise the documented provider-unavailable path without broad new graph
  writes;
- prove deterministic SQLite evidence retrieval remains citation-complete.

## Non-Goals

- live acquisition, browser operation, broad graph backfill, schema migration,
  ranking redesign, or LightRAG adoption;
- deleting or rewriting Graphiti history;
- claiming identical graph and local ranking when only authority continuity is
  required;
- exposing browser mechanics or raw provider events through MCP.

## Dependencies And Owned Surfaces

- Depends on P01 immutable evidence and P04 temporal/query/projection contracts.
- Supports P05 product acceptance through the existing compact MCP surface.
- Opens only after Plan 0018 freezes the independent service lifecycle and MCP
  client/service compatibility boundary.
- Expected writes are focused retrieval/projection tests, a bounded existing
  projection replay receipt, and closeout docs.

## Execution Graph

```text
R01 baseline snapshot
  -> R02 cache-only temporal/profile query and no-enqueue proof
  -> R03 existing projection replay and read-after-write
  -> R04 provider-unavailable SQLite fallback
  -> R05 restore/readback and closeout
```

## Bounds And Gates

- maximum implementation attempts per packet: 2;
- maximum review/rework cycles: 1;
- maximum hardening-only checkpoints: 1;
- active-agent concurrency: 1;
- one cache-only query case and one existing projection replay;
- Graphiti writes require provider readiness, the allow-listed
  `last30days_skill_main` group, and read-after-write verification;
- stop if acquisition is enqueued, access widens, citations lose immutable
  closure, projection replay duplicates authority, or the provider cannot be
  returned to its prior state.

## Acceptance Criteria

- the cache-only request changes no durable acquisition-job count;
- `as_of` and profile/access filters return the intended temporal slice and
  exact immutable evidence;
- projection replay is idempotent and visible through Graphiti readback;
- during provider unavailability, SQLite evidence retrieval remains usable and
  truthfully reports graph degradation;
- restored status, projection receipt, index version, freshness, coverage,
  access partition, and uncertainty are explicit.

## Validation

- focused temporal retrieval, access-partition, MCP, projection, and fallback
  suites;
- before/after job and projection ledger comparison;
- Graphiti provider readiness and read-after-write checks;
- planning audit and `git diff --check`.

## Definition Of Done

Cache-only temporal/profile retrieval, idempotent projection replay, and
SQLite-only degradation behavior all have current evidence without browser
work or broad graph mutation.
