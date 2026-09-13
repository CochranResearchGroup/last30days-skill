# Plan 0076 | Post Search Architecture And Lane Handoff

State: OPEN
Lane: P33
Work item: WI-002
Branch: docs/post-search-architecture
Target: main
Integration: merge
Roadmap: P33
Plan version: 1
Date: 2026-09-13

## Objective

Turn WI-002 into a restart-safe `READY` implementation lane by mapping the
current stored-post/query architecture, choosing a compatible product seam,
and defining vertical delivery packets with acceptance evidence.

## Current State

- WI-002 exists as a repo-local `TRIAGE` draft and GitHub Issues remain disabled;
- current source and live runtime prove two durable storage families, a mature
  query/MCP surface, and exact gaps in federation, filtering, and pagination;
- the coordinator has selected an additive cache-only post-search seam that
  preserves current `/v1/query` behavior;
- the architecture note and machine-readable handoff are prepared but not yet
  integrated.

## Scope

- use Graphiti as advisory recall and verify its useful claims against current
  source and live read-only service state;
- use CodeGraph to trace the current query flow and blast radius;
- inventory storage identity, provenance, filter, ranking, pagination, HTTP,
  MCP, access, and compatibility boundaries;
- choose the v1 product contract and vertical tracer-bullet sequence;
- update WI-002 to `READY` with one exact next owner action;
- integrate the architecture packet through the owned public fork.

## Non-Goals

- no feature implementation, schema migration, generated contract change, or
  installed Skill/runtime change;
- no acquisition, provider/browser access, schedule, credential, deployment,
  staging, or production mutation;
- no GitHub Issues, Project, label, or repository-setting mutation;
- no reassignment of WI-001, WI-003, WI-004, or hotfix capacity.

## Acceptance Criteria

1. Current query selection, data stores, filters, pagination, ranking,
   provenance, access boundaries, and live installed identity are evidenced.
2. One architecture decision names the endpoint/MCP seam, request/response,
   cross-store identity, filtering, ranking, cursor, and compatibility rules.
3. Delivery is split into end-to-end vertical packets rather than disconnected
   storage, engine, HTTP, or documentation layers.
4. Provider-free acceptance covers both stores, access, filters, pagination,
   concurrent publication, revisions, dedupe, ranking, and transport parity.
5. WI-002 is `READY`, P33 and the runbook point to this plan, and plan/canonical
   authority validation passes without remote tracker or runtime mutation.

## Execution Packet

- owner: coordinator session;
- critical path: advisory recall, current structural/source evidence, live
  read-only verification, architecture synthesis, work-item handoff, validation,
  and public-fork integration;
- write surfaces: Plan 0076, P33, WI-002, one architecture note, one JSON
  handoff, runbook, and active-plan test expectation;
- external effects: Git branch publication and PR integration only;
- bounds: two focused memory episodes, three CodeGraph exploration rounds, one
  live cache-only query, one synthesis/remediation pass, one integration, and
  one closeout;
- terminal condition: all five criteria pass or the unresolved architecture
  decision is recorded without starting implementation;
- authority classification: `inherited_authority`; this prepares the approved
  search/retrieval lane without crossing the tracker or runtime gate.

Subagent status: `not_spawned`; repo policy directs the coordinator to perform
shared-interface exploration directly, and no parallel implementation began.

## Definition Of Done

The architecture and machine handoff are integrated, WI-002 is ready for one
independent top-level lane session, and current Git/tracker/runtime boundaries
are truthfully recorded.

## Current Checkpoint

### Checkpoint P0076-C01 | 2026-09-13

Plan version: 1

State transition: `planned -> active`.

Progress classification: `outcome_progress`; the current architecture has
been reduced to a compatible vertical delivery contract.

Authority classification:

- `inherited_authority` for read-only investigation and repo artifacts;
- `not_authorized` for tracker, provider, installed runtime, or deployment
  mutations.

Validation evidence:

- Graphiti runtime is healthy; discovery returned eight facts, five nodes, and
  five episode previews in `last30days_skill_main`, with two cited episodes
  expanded and verified against the repository;
- CodeGraph is healthy with 353 files, 9,793 nodes, and 23,275 edges; focused
  query-flow inspection identified the exact current seams and blast radius;
- live service readback reports service `0.3.116`, schema 17, MCP `4.0.4`, 167
  indexed documents/embeddings, and a compatible ready state;
- one cache-only live query confirmed promoted-snapshot selection, bounded
  evidence, and absent pagination without acquisition;
- 13 focused policy/authority tests pass; plan authority reports exactly the
  two legitimate open plans with zero issues;
- both JSON authority files parse, all nine work-item markers remain unique,
  and `git diff --check` passes.

Subagent status and reconciliation:

- `not_spawned`; all evidence was gathered and reconciled by the coordinator.

Graphiti write status:

- `pending_closeout`; repo policy requires one compact source-backed episode
  after this architecture decision is durably integrated.

Next action:

- integrate the architecture packet, close Plan 0076/P33 planning work, write
  and verify one compact Graphiti episode, then hand WI-002 to one independent
  top-level lane session.
