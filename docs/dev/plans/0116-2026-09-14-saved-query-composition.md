# Plan 0116 | Saved Query Composition Packet 2

State: PLANNED
Lane: P40
Work item: WI-006
Branch: feat/saved-query-composition-v2
Target: main
Integration: merge
Roadmap: P40
Plan version: 1
Date: 2026-09-14
Execution owner: unassigned
Coordination owner: /root
Requested model route: gpt-6-astra, high reasoning
Effective runtime model: unknown until reported

## Objective

Compose the existing monitor kernel with the real stored-post search contract by
persisting an immutable saved-query version and freezing its exact bounded
evidence view into explicit baseline acceptance.

## Current State

Packet 1's provider-free monitor kernel is integrated. WI-002's search contract
and WI-004's follow contract are available, but the kernel still consumes a fake
saved-query provider. This packet implements query composition only; follow
composition and digest/delivery closure remain separate.

## Scope

- persist immutable saved-query definitions and versions;
- execute the exact query through `PostSearchBackend` in one snapshot lifetime;
- freeze evidence IDs, revisions, partitions, component head, cutoff, and
  coverage rather than persisting a process-local cursor;
- classify new, revised, and unchanged evidence; treat top-k absence as unknown,
  not removal;
- require explicit baseline acceptance and fail closed on stale baseline,
  partial/truncated traversal, cursor expiry/restart, or partition mismatch;
- add narrow local CLI/MCP parity behind coordinator-owned shared joins.

## Non-Goals

No follow view, digest generation, notification delivery, installed schedule,
refresh/acquisition, provider, browser, production, release, issue mutation, or
generated summary.

## Acceptance Criteria

1. Saved-query identity and every version are immutable and schema validated.
2. Search execution freezes exact evidence and coverage without durable cursors.
3. New/revised/unchanged classifications are deterministic and idempotent.
4. Absence, incomplete traversal, stale heads, restart, and partition drift
   never fabricate removals or silently restart from an unpinned view.
5. Baseline movement requires explicit acceptance; replay is side-effect safe.
6. Narrow CLI/MCP fixtures preserve the same contracts with effects disabled.
7. Focused monitor/search, full Python, Go test/vet, audit, and diff checks pass.

## Ownership And Topology

One top-level implementation owner, no children, at most two implementation
attempts, one independent review, and one closed-world remediation. Lane writes
are monitor contracts/kernel, new `service_monitor_views.py`, focused tests and
fixtures, and this plan. Shared app/CLI/MCP contracts, catalogs, manifests, and
authority projections remain coordinator-owned.

## Stop Rules

Stop on missing authoritative head/coverage evidence, unbounded cursor replay,
shared-file custody conflict, upstream search repair, or any provider,
installed-database, schedule, delivery, credential, or live effect.

## Definition Of Done

All seven criteria pass at integration. This closes Packet 2 but not WI-006;
follow composition and digest/delivery/runtime closure remain separately planned.
