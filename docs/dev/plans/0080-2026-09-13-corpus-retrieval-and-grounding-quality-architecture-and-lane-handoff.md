# Plan 0080 | Corpus Retrieval And Grounding Quality Architecture And Lane Handoff

State: CLOSED
Lane: P37
Work item: WI-008
Branch: docs/corpus-quality-architecture
Target: main
Integration: merge
Roadmap: P37
Plan version: 1
Date: 2026-09-13

## Objective

Turn WI-008 into a restart-safe `READY` implementation lane by mapping current
evaluation, retrieval, revision, provenance, coverage, evidence, and judgment
seams; defining a four-axis denominator-aware quality contract; and splitting
delivery into provider-free packets with exact WI-002/WI-003 joins.

## Current State

- WI-008 is a repo-local `TRIAGE` draft blocked broadly by WI-002;
- current evaluators separately cover part of the slash-command pipeline, a
  narrow service retriever, and proposal-shaped model judgments;
- no unified versioned evaluation set, threshold policy, report, effect
  receipt, or continuous execution topology exists;
- no product implementation, evaluator run, judge call, runtime provisioning,
  or provider use has begun.

## Scope

- use Graphiti as advisory recall and verify useful claims against current
  source, tests, artifacts, and live read-only service state;
- use CodeGraph to map evaluator, retrieval, coverage, revision, evidence,
  provenance, structured-judgment, artifact, and test seams;
- define evaluation-set, threshold-policy, run, report, metric, artifact,
  comparison, effect, and exit contracts;
- keep acquisition, corpus, retrieval, and grounding axes separately
  inspectable with explicit denominators;
- define provider-free blocking, periodic comprehensive, and optional
  observation tiers;
- define exact dependency joins and ownership with WI-002 and WI-003;
- split implementation into provider-free vertical packets;
- update WI-008 to `READY` with Packet 1 unblocked and later joins precise;
- integrate the architecture packet through the owned public fork.

## Non-Goals

- no evaluator, fixture corpus, schema, metric, report, command, CI, service,
  MCP, or runtime implementation in this architecture slice;
- no live source refresh, browser, model judge, credential, installed Skill or
  database, schedule, staging, deployment, production sample, or production
  mutation;
- no automatic model/ranker promotion, threshold change, data repair/deletion,
  or GitHub Issues mutation;
- no redefinition of WI-002 search or WI-003 answer contracts.

## Acceptance Criteria

1. Current evaluator/retrieval/coverage/revision/evidence/judgment seams and
   exact gaps are evidenced from current source and live read-only status.
2. One design names strict set, threshold, run, report, axis, metric,
   denominator, artifact, comparison, effect, and exit contracts.
3. Fixture, development, staging, production-sample, and optional-judge claims
   remain distinct and fail closed on missing or incomplete evidence.
4. Delivery is split into provider-free packets with explicit WI-002/WI-003
   joins and coordinator-owned shared surfaces.
5. WI-008 is `READY`, P37 and the runbook point here, and planning/custody
   validation passes without tracker/runtime/provider mutation.

## Execution Packet

- owner: coordinator session;
- critical path: advisory recall, current structural/source and live read-only
  evidence, architecture synthesis, dependency handoff, validation, and
  public-fork integration;
- write surfaces: Plan 0080, P37, WI-008, one architecture note, one JSON
  handoff, runbook, active-lane catalog, and active-plan test expectation;
- external effects: Git branch publication and PR integration only;
- bounds: two focused memory reads, four CodeGraph exploration rounds, one
  live read-only service status, one synthesis/remediation pass, one
  integration, and one closeout;
- terminal condition: all five criteria pass or an unresolved safety/interface
  boundary is recorded without starting implementation;
- authority classification: `inherited_authority`; this prepares the approved
  quality lane without crossing tracker, implementation, judge, runtime,
  provider, sample, staging, or production gates.

Subagent status: `not_spawned`; repo policy directs the coordinator to perform
shared-interface exploration directly, and no parallel implementation began.

## Definition Of Done

The architecture and machine handoff are integrated, WI-008 Packet 1 is ready
for a separately owned top-level session, and later WI-002/WI-003 joins plus
runtime/provider boundaries are truthfully recorded.

## Current Checkpoint

### Checkpoint P0080-C01 | 2026-09-13

Plan version: 1

State transition: `planned -> active`.

Progress classification: `outcome_progress`; fragmented evaluation seams have
been reduced to one replayable four-axis quality workflow.

Authority classification:

- `inherited_authority` for read-only investigation and repo artifacts;
- `not_authorized` for tracker, implementation, judge, installed runtime,
  browser/provider, production sample, schedule, staging, or production
  mutations.

Validation evidence:

- canonical `main` was clean and equal to `origin/main` at `aa7db908` before
  the dedicated architecture worktree was created;
- Graphiti runtime is healthy; bounded discovery returned the immutable-
  revision rule and older coverage/relevance sources, verified against current
  source where used;
- CodeGraph is current at 353 files, 9,793 nodes, and 23,275 edges and exposed
  the evaluator, retrieval, coverage, revision, evidence, judgment, and test
  seams;
- live read-only service status reports PID 24968, service `0.3.116`, schema
  17, ready state, immutable index head, and 167 indexed documents;
- provider-free repository validation remains to run after this packet is
  fully rendered.

Subagent status and reconciliation:

- `not_spawned`; all evidence was gathered and reconciled by the coordinator.

Graphiti write status:

- `graphiti_write_pending`; Plans 0076-0079 already await recovery of the
  degraded ingestion path, so no new write is queued in this slice.

Next action:

- validate and integrate this architecture packet, close Plan 0080/P37
  planning work, and hand provider-free Packet 1 to a separate top-level lane
  session.

### Checkpoint P0080-C02 | 2026-09-13

Plan version: 1

State transition: `active -> closed`.

Progress classification: `outcome_progress`; the quality architecture and
machine handoff are integrated, while provider-free implementation remains
correctly unstarted.

Authority classification:

- `inherited_authority` for public-fork integration and repository closeout;
- `not_authorized` for tracker, implementation, evaluator execution, judge,
  installed runtime/database, provider/browser, production sample, schedule,
  CI, staging, or production mutations.

Validation evidence:

- architecture source tip `081dcb654cf84a4bf40e7af77c2e5620ef3f3c0c`
  merged through pull request 23 as
  `6d5827e0c8f594d74bb5f043a9ea005bf711a3bd`;
- canonical `main` was fast-forwarded to the exact merge before this isolated
  closeout branch was created;
- 62 focused policy tests, plan authority, active planning contract, JSON
  parsing, and patch hygiene passed on the architecture packet;
- final closeout validation and default-ref catalog audit remain to run after
  this state reconciliation is rendered.

Subagent status and reconciliation:

- `not_spawned`; coordinator-owned architecture and merge receipts are
  authoritative.

Graphiti write status:

- `graphiti_write_pending`; no additional write was attempted while the known
  ingestion path remains degraded.

Next action:

- assign WI-008 Packet 1 to one separate top-level lane session from current
  `origin/main`, create and register `feat/service-quality-v1`, and keep the
  packet strictly provider-free.
