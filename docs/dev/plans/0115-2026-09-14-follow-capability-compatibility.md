# Plan 0115 | Follow Capability And Compatibility Packet 1

State: PLANNED
Lane: P39
Work item: WI-005
Branch: feat/cross-service-follow-capabilities-v1
Target: main
Integration: merge
Roadmap: P39
Plan version: 1
Date: 2026-09-14
Execution owner: unassigned
Coordination owner: /root
Requested model route: gpt-6-astra, high reasoning
Effective runtime model: unknown until reported

## Objective

Establish the provider-neutral tailored-follow identity foundation by replacing
the X-only hard gate with a closed capability registry and compatible
`FollowTargetV1` seam while preserving every accepted X identity and historical
row.

## Current State

WI-004 is `DONE`. The shared collection model has global surface validation but
tailored follows still admit only X, while Reddit and YouTube acquisition paths
flatten targets into generic queries. Provider-specific tracers must not fan out
until capability and legacy compatibility semantics are frozen.

## Scope

- add a closed `(source, target_kind)` capability registry and validators;
- derive an embedded/discriminated follow target from existing X specs without
  changing follow IDs, selectors, partitions, revisions, or history;
- declare Reddit community/user and YouTube channel unavailable with stable
  `adapter_not_implemented` results; keep Facebook/LinkedIn unsupported;
- quarantine provider-invalid legacy tailored targets while preserving reads,
  pause, and archive;
- add an additive idempotent compatibility tracer with deterministic counts and
  digest over disposable SQLite fixtures.

## Non-Goals

No Reddit/YouTube acquisition, locator resolution, browser/profile, real
adapter call, enabled installed follow, schedule/job, MCP publication, provider,
release, deployment, issue mutation, or WI-006 implementation.

## Acceptance Criteria

1. Duplicate capabilities, missing validators, and unknown source/kind fail closed.
2. Existing X feed/topic/account/list identities and immutable history are exact.
3. Declared unavailable and unsupported providers remain distinguishable.
4. General collections remain readable and unaffected.
5. Invalid legacy tailored targets are readable/quarantined, cannot enable,
   revise, or schedule, and can still pause/archive.
6. Compatibility tracing is additive, idempotent, deterministic, and bounded.
7. Existing collection lifecycle/X tests plus focused and joined validation pass.

## Ownership And Topology

One top-level implementation owner, no children, at most two implementation
attempts, one independent review, and one closed-world remediation. Lane writes
are `service_follow_capabilities.py`, `service_collection.py`, focused tests,
fixtures, and this plan. Shared contracts, schemas, catalogs, manifest, public
MCP/CLI discovery, and authority projections remain coordinator-owned.

## Stop Rules

Stop if existing X identity digests change, historical rows require rewriting,
a shared contract must change before coordinator disposition, or any real
provider/runtime/schedule effect is needed. Stop after Packet 1 acceptance; do
not begin provider tracers.

## Definition Of Done

This plan closes when all seven criteria pass at integration. It advances but
does not complete WI-005; later Reddit/YouTube tracers and public closure remain.
