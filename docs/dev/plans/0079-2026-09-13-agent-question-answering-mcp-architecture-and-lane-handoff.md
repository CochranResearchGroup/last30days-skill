# Plan 0079 | Agent Question Answering MCP Architecture And Lane Handoff

State: CLOSED
Lane: P36
Work item: WI-003
Branch: docs/agent-question-answer-architecture
Target: main
Integration: merge
Roadmap: P36
Plan version: 1
Date: 2026-09-13

## Objective

Turn WI-003 into a restart-safe `READY` dependent implementation lane by
mapping current MCP, query, temporal evidence, model-worker, access, and
transport seams; choosing an evidence-grounded question contract; and defining
vertical provider-free delivery packets and exact WI-002 joins.

## Current State

- WI-003 is a repo-local `TRIAGE` draft blocked by WI-002 and GitHub Issues
  remain disabled;
- current MCP query surfaces retrieve evidence and deterministic temporal
  records but do not synthesize validated answers or dereference citations;
- the coordinator selected a durable question workflow over WI-002
  `search_posts`, with a separate structured answer contract and explicit
  model/acquisition effect receipts;
- no product implementation, model invocation, runtime provisioning, or
  provider use has begun.

## Scope

- use Graphiti as advisory recall and verify relevant decisions against current
  source and live read-only service state;
- use CodeGraph to map MCP registration, query/temporal retrieval, evidence,
  structured model worker, persistence, HTTP, client, access, budget, and
  compatibility seams;
- define question, answer, status, citation-read, coverage, freshness,
  contradiction, idempotency, validation, and effect contracts;
- define exact dependency joins and shared-file ownership with WI-002;
- split implementation into provider-free end-to-end packets;
- update WI-003 to `READY` while retaining its precise WI-002 blocker;
- integrate the architecture packet through the owned public fork.

## Non-Goals

- no question/search/evidence contract, schema, queue, worker, endpoint, MCP,
  prompt, or runtime implementation in this architecture slice;
- no source refresh, follow creation, schedule, notification, browser, model,
  provider, credential, installed Skill/runtime, database, staging, deployment,
  or production mutation;
- no GitHub Issues, Project, label, or repository-setting mutation;
- no redefinition of WI-002 search or WI-008 quality ownership.

## Acceptance Criteria

1. Current MCP/query/temporal/evidence/model/access/transport seams and exact
   gaps are evidenced from current source and live read-only status.
2. One design names strict request, frozen retrieval, answer statements,
   citations, evidence read, status, durability, validation, model, and effect
   contracts.
3. Stale, partial, contradictory, empty, unsupported, unavailable, and
   cross-partition cases have distinct fail-closed behavior.
4. Delivery is split into provider-free vertical packets with explicit WI-002
   dependency joins and coordinator-owned shared surfaces.
5. WI-003 is `READY` but correctly blocked, P36 and the runbook point here, and
   planning/custody validation passes without tracker/runtime/provider mutation.

## Execution Packet

- owner: coordinator session;
- critical path: advisory recall, current structural/source and live read-only
  evidence, architecture synthesis, dependency handoff, validation, and
  public-fork integration;
- write surfaces: Plan 0079, P36, WI-003, one architecture note, one JSON
  handoff, runbook, active-lane catalog, and active-plan test expectation;
- external effects: Git branch publication and PR integration only;
- bounds: two focused memory reads, four CodeGraph exploration rounds, one
  live read-only service status, one synthesis/remediation pass, one
  integration, and one closeout;
- terminal condition: all five criteria pass or an unresolved safety/interface
  boundary is recorded without starting implementation;
- authority classification: `inherited_authority`; this prepares the approved
  MCP lane without crossing the WI-002 join, tracker, model, runtime, or
  provider gates.

Subagent status: `not_spawned`; repo policy directs the coordinator to perform
shared-interface exploration directly, and no parallel implementation began.

## Definition Of Done

The architecture and machine handoff are integrated, WI-003 is ready behind an
exact WI-002 dependency, and current Git/tracker/runtime/model boundaries are
truthfully recorded.

## Current Checkpoint

### Checkpoint P0079-C01 | 2026-09-13

Plan version: 1

State transition: `planned -> active`.

Progress classification: `outcome_progress`; current retrieval, evidence, and
worker seams have been reduced to a compatible durable question workflow.

Authority classification:

- `inherited_authority` for read-only investigation and repo artifacts;
- `not_authorized` for tracker, implementation, model, installed runtime,
  browser/provider, collection/schedule, staging, or production mutations.

Validation evidence:

- canonical `main` was clean and equal to `origin/main` at `4687a074` before
  the dedicated architecture worktree was created;
- Graphiti runtime is healthy; bounded discovery returned three facts and two
  cited Plan 0011/App Intelligence episodes, verified against current source;
- CodeGraph is healthy at 353 files, 9,793 nodes, and 23,275 edges and exposed
  the MCP, query, temporal, evidence, worker, persistence, and transport seams;
- live read-only service status reports `0.3.116`, schema 17, ready state, and
  167 indexed documents across five sources;
- provider-free repository validation remains to run after this packet is
  fully rendered.

Subagent status and reconciliation:

- `not_spawned`; all evidence was gathered and reconciled by the coordinator.

Graphiti write status:

- `graphiti_write_pending`; Plans 0076-0078 already await recovery of the
  degraded ingestion path, so no new write is queued in this slice.

Next action:

- validate and integrate this architecture packet, close Plan 0079/P36
  planning work, and retain the WI-002 Packet 1 gate in the lane handoff.

### Checkpoint P0079-C02 | 2026-09-13

Plan version: 1

State transition: `active -> closed`.

Progress classification: `outcome_progress`; the architecture and machine
handoff are integrated, while implementation remains correctly unstarted and
dependency-gated.

Authority classification:

- `inherited_authority` for public-fork integration and repository closeout;
- `not_authorized` for tracker, implementation, model, installed runtime,
  browser/provider, collection/schedule, staging, or production mutations.

Validation evidence:

- architecture source tip `96ae270827ec65d79e9665661c9e0811b748b89e`
  merged through pull request 21 as
  `3c94c01c6c43f883c762b2cb674fabc416297992`;
- canonical `main` was fast-forwarded to the exact merge before this isolated
  closeout branch was created;
- 62 focused policy tests, plan authority, active-lane catalog, active planning
  contract, JSON parsing, and patch hygiene passed on the architecture packet;
- final closeout validation remains to run after the state reconciliation is
  rendered.

Subagent status and reconciliation:

- `not_spawned`; coordinator-owned architecture and merge receipts are
  authoritative.

Graphiti write status:

- `graphiti_write_pending`; no additional write was attempted while the known
  ingestion path remains degraded.

Next action:

- keep WI-003/P36 planned until WI-002 Packet 1 integrates its stable search
  and evidence-ref contracts, then assign WI-003 Packet 1 to a separate
  top-level lane session from then-current `origin/main`.
