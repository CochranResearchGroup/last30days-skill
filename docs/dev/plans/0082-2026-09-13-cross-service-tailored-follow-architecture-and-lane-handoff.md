# Plan 0082 | Cross-Service Tailored Follow Architecture And Lane Handoff

State: OPEN
Lane: P39
Work item: WI-005
Branch: docs/cross-service-tailored-follow-architecture
Target: main
Integration: merge
Roadmap: P39
Plan version: 1
Date: 2026-09-13

## Objective

Turn WI-005 into a restart-safe `READY` implementation lane by selecting a
provider-native follow-target and capability contract that preserves WI-004 X
identity while adding honest Reddit and YouTube extension points.

## Current State

- WI-005 began as a repo-local `TRIAGE` draft blocked broadly by WI-004;
- current collection selectors are global and current adapter capabilities are
  too coarse to prove source-target support;
- the selected seam is a closed provider capability registry plus a
  discriminated target envelope on WI-004's shared collection authority;
- no implementation, tracker, runtime, schedule, browser, or provider action
  has begun.

## Scope

- use advisory Graphiti recall and current CodeGraph/source evidence;
- define stable provider-native identity, resolution, capability discovery,
  lifecycle, scheduling, receipts, provenance, migration, and safe failures;
- preserve accepted X follow identity and history;
- define provider-free Reddit community/user and YouTube channel tracers;
- update WI-005 to `READY` with exact dependency and owner handoff;
- integrate the architecture through the owned public fork.

## Non-Goals

- no product implementation or provider-specific parser/route;
- no GitHub Issues, Project, label, or setting mutation;
- no installed Skill/service/database, schedule, browser/profile, provider,
  staging, deployment, or production mutation;
- no claim that every source supports the same targets or cadence.

## Acceptance Criteria

1. Current global-selector and coarse-capability gaps are evidenced.
2. One contract separates shared collection semantics from provider-native
   target identity, validation, resolution, access, and routing.
3. X identities migrate unchanged; invalid legacy combinations remain readable
   but fail closed for future scheduling.
4. Delivery packets cover registry/compatibility, Reddit, YouTube, discovery,
   lifecycle, replay, overlap, and access with provider-free fixtures.
5. WI-005 is `READY`, P39 and the runbook point here, and authority validation
   passes without tracker or runtime mutation.

## Execution Packet

- owner: coordinator session;
- critical path: advisory recall, structural evidence, architecture synthesis,
  work-item handoff, validation, and public-fork integration;
- write surfaces: Plan 0082, P39, WI-005, one architecture note, one JSON
  handoff, runbook, and active-lane catalog;
- external effects: Git branch publication and PR integration only;
- bounds: two focused memory reads, three CodeGraph rounds, one synthesis pass,
  one integration, and one closeout;
- terminal condition: all five criteria pass or an unresolved safety boundary
  is recorded without starting implementation;
- authority classification: `inherited_authority` for the approved follows
  planning lane; all tracker/runtime/provider effects remain unauthorized.

Subagent status: `not_spawned`; policy directs direct shared-interface
exploration and no parallel implementation is authorized in this session.

## Definition Of Done

The architecture and machine handoff are integrated, WI-005 is ready for one
independent top-level lane session after its exact WI-004 dependency, and all
current Git/tracker/runtime boundaries are recorded.

## Current Checkpoint

### Checkpoint P0082-C01 | 2026-09-13

Plan version: 1

State transition: `planned -> active`.

Progress classification: `outcome_progress`; the cross-service follow problem
is reduced to an exact provider-native capability contract and vertical plan.

Authority classification:

- `inherited_authority` for read-only investigation and repo artifacts;
- `not_authorized` for tracker, product implementation, installed runtime,
  collection, browser/profile, provider, schedule, staging, or production.

Validation evidence:

- canonical `main` was clean and equal to `origin/main` at `d20b8254` before
  this dedicated architecture worktree was created;
- bounded Graphiti discovery recovered the accepted Plan 0011 collection
  foundation and a prior LinkedIn people/company proposal, treated as advisory;
- CodeGraph is healthy at 353 files, 9,793 nodes, and 23,275 edges;
- current source exposes the global selector table, five-source access policy,
  coarse adapter registry, and provider-specific routing seams;
- provider-free repository validation remains to run after rendering.

Subagent status and reconciliation:

- `not_spawned`; evidence was gathered and reconciled by the coordinator.

Graphiti write status:

- `graphiti_write_pending`; the known degraded ingestion path previously
  failed in node deduplication without an episode UUID, so no duplicate write
  was queued.

Next action:

- validate and integrate this architecture packet, close Plan 0082/P39
  planning work, and retain the exact WI-004 Packet 1 dependency.

## Stop Rules

- stop before product implementation or provider-specific route work;
- stop before GitHub tracker mutation without explicit operator authority;
- stop before any installed/runtime/browser/provider/schedule mutation;
- stop if X identity preservation or an exact capability state cannot be
  demonstrated provider-free.
