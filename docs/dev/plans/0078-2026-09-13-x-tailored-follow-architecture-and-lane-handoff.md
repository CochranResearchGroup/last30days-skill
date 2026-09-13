# Plan 0078 | X Tailored Follow Architecture And Lane Handoff

State: CLOSED
Lane: P35
Work item: WI-004
Branch: docs/x-tailored-follow-architecture
Target: main
Integration: merge
Roadmap: P35
Plan version: 1
Date: 2026-09-13

## Objective

Turn WI-004 into a restart-safe `READY` implementation lane by mapping current
collection, X acquisition, publication, lifecycle, and agent surfaces;
selecting a compatible tailored-follow contract; and defining vertical
provider-free delivery packets.

## Current State

- WI-004 began as a repo-local `TRIAGE` draft and GitHub Issues remain
  disabled;
- current source proves a mature collection scheduler but no typed X account
  or list acquisition and no archival delete operation;
- the coordinator selected a purpose-typed evolution of `CollectionSpec` plus
  immutable collection context at the acquisition/publication boundary, and
  PR 19 integrated the architecture at
  `ff1fe170f856a92f8118a97f79097ab24480f34e`;
- WI-004 is `READY`; implementation and any runtime/provider use have not
  started;
- no product implementation, runtime provisioning, schedule change, or live
  provider use has begun.

## Scope

- use Graphiti as advisory recall and verify useful decisions against current
  source;
- use CodeGraph to map collection, scheduler, X adapter, work contract,
  publication, storage, CLI, MCP, access, and lifecycle seams;
- define canonical account/list/topic/feed identity, attention, versioning,
  lifecycle, dedupe, provenance, error, and effect rules;
- split implementation into provider-free end-to-end packets;
- update WI-004 to `READY` with one exact next owner action;
- integrate the architecture packet through the owned public fork.

## Non-Goals

- no contract, migration, adapter, scraper, scheduler, CLI, or MCP
  implementation in this architecture slice;
- no installed Skill/runtime, collection spec, database, browser, profile,
  provider, schedule, credential, deployment, staging, or production mutation;
- no GitHub Issues, Project, label, or repository-setting mutation;
- no cross-service follow abstraction, question synthesis, monitor/digest, or
  reassignment of WI-001, WI-002, WI-003, or hotfix capacity.

## Acceptance Criteria

1. Current collection identity, revision, scheduling, concurrency, X routing,
   lifecycle, publication, sightings, access, CLI, and MCP seams are evidenced.
2. One design names purpose, attention, typed target identity, immutable work
   context, lifecycle, cause provenance, dedupe, and safe failure semantics.
3. The existing collection scheduler remains authoritative and the general X
   feed remains independent from tailored follows.
4. Delivery is split into provider-free vertical packets covering account,
   list, lifecycle, replay, overlap, access, auth, rate limit, and deletion.
5. WI-004 is `READY`, P35 and the runbook point here, and plan/canonical
   authority validation passes without remote tracker or runtime mutation.

## Execution Packet

- owner: coordinator session;
- critical path: advisory recall, current structural/source evidence,
  architecture synthesis, work-item handoff, validation, and public-fork
  integration;
- write surfaces: Plan 0078, P35, WI-004, one architecture note, one JSON
  handoff, runbook, and active-lane catalog;
- external effects: Git branch publication and PR integration only;
- bounds: two focused memory reads, four CodeGraph exploration rounds, one
  synthesis/remediation pass, one integration, and one closeout;
- terminal condition: all five criteria pass or the unresolved safety boundary
  is recorded without starting implementation;
- authority classification: `inherited_authority`; this prepares the approved
  follows lane without crossing tracker, runtime, schedule, or provider gates.

Subagent status: `not_spawned`; repo policy directs the coordinator to perform
shared-interface exploration directly, and no parallel implementation began.

## Definition Of Done

The architecture and machine handoff are integrated, WI-004 is ready for one
independent top-level lane session, and current Git/tracker/runtime boundaries
are truthfully recorded.

## Current Checkpoint

### Checkpoint P0078-C01 | 2026-09-13

Plan version: 1

State transition: `planned -> active`.

Progress classification: `outcome_progress`; current collection machinery and
X-specific gaps have been reduced to a compatible vertical delivery contract.

Authority classification:

- `inherited_authority` for read-only investigation and repo artifacts;
- `not_authorized` for tracker, implementation, installed runtime, collection,
  browser/profile, provider, schedule, staging, or production mutations.

Validation evidence:

- canonical `main` was clean and equal to `origin/main` at `16562fef` before
  the dedicated architecture worktree was created;
- Graphiti runtime and bounded discovery reads are healthy; one Plan 0011
  collection-spec source episode was recovered and verified against current
  code;
- CodeGraph is healthy at 353 files, 9,793 nodes, and 23,275 edges and exposed
  the collection, work-contract, X routing, publication, lifecycle, CLI, and
  MCP seams;
- source inspection confirms document-version sightings can preserve multiple
  acquisition causes while the current publisher resolves one collection with
  `LIMIT 1`;
- provider-free repository validation remains to run after this packet is
  fully rendered.

Subagent status and reconciliation:

- `not_spawned`; all evidence was gathered and reconciled by the coordinator.

Graphiti write status:

- `graphiti_write_pending`; a prior exact write retry failed during node
  deduplication with no episode UUID, so this slice does not queue another
  write behind the degraded ingestion path.

Next action:

- validate and integrate this architecture packet, close Plan 0078/P35
  planning work, and hand WI-004 Packet 1 to one independent top-level session.

### Checkpoint P0078-C02 | 2026-09-13

Plan version: 1

State transition: `active -> closed`.

Progress classification: `verified_outcome`; WI-004's typed-target,
evidence-preserving architecture and restart-safe Packet 1 handoff are
integrated.

Authority classification:

- `inherited_authority` for integration and planning closeout;
- `not_authorized` for tracker, implementation runtime, collection, browser/
  profile, provider, schedule, staging, or production mutations.

Validation evidence:

- pull request 19 merged source tip
  `c25caea6382cb9c4a11f8ff5a90331b323564f1a` as
  `ff1fe170f856a92f8118a97f79097ab24480f34e` on `origin/main`;
- canonical `main` fast-forwarded cleanly to that exact merge;
- 62 focused planning/lane-policy tests, plan authority, active planning
  contract, JSON parsing, work-item uniqueness, and patch hygiene pass;
- the new P35 catalog entry is integrated and exact branch custody was
  reconciled without touching installed or production runtime state.

Subagent status and reconciliation:

- `not_spawned`; coordinator-owned architecture evidence is authoritative.

Graphiti write status:

- `graphiti_write_pending`; the prior exact architecture-write retry remains a
  terminal retryable transport failure with no episode UUID. No new write was
  queued behind that degraded ingestion path.

Next action:

- assign WI-004 Packet 1 to one independent top-level lane session starting
  from current `origin/main`; create and register its dedicated
  `feat/x-tailored-follows-v1` branch/worktree before implementation.
