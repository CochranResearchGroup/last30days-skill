# Plan 0081 | Reserved Production Hotfix Path Architecture And Lane Handoff

State: CLOSED
Lane: P38
Work item: WI-007
Branch: docs/production-hotfix-path-architecture
Target: main
Integration: merge
Roadmap: P38
Plan version: 1
Date: 2026-09-13

## Objective

Turn WI-007 into a restart-safe `READY` implementation lane by mapping current
Git, release, installer, readiness, rollback, and runtime seams; defining a
dormant reserved hotfix state machine; and specifying provider-free drills plus
exact staging/deployment authority gates.

## Current State

- WI-007 is a repo-local `TRIAGE` draft broadly blocked by WI-001;
- policy reserves a hotfix slot and current release machinery supports
  reproducible artifacts and snapshot-backed rollback;
- no durable contract joins incident qualification, priority custody,
  feature-lane reconciliation, staging, deployment authorization, production
  verification, rollback, and closeout;
- no drill, implementation, staging runtime, release, or production mutation
  has begun.

## Scope

- use Graphiti as advisory recall and verify relevant release/rollback claims
  against current source, tests, Git, and live read-only production state;
- use CodeGraph and targeted script inspection to map health, readiness,
  builder, installer, rollback, compatibility, and test seams;
- define strict hotfix case, candidate, reconciliation, staging,
  authorization, deployment, rollback, and closeout contracts;
- define dormant/active custody, priority, WIP, conflict, and reconciliation
  semantics;
- split implementation into provider-free control-plane, Git, and runtime
  drills with exact WI-001 joins;
- update WI-007 to `READY` with Packets 1-2 unblocked and later gates precise;
- integrate the architecture packet through the owned public fork.

## Non-Goals

- no hotfix controller, contract, fixture, test, build, release, install,
  staging, deployment, or rollback implementation in this architecture slice;
- no incident declaration, GitHub issue, provider/browser, credential, service,
  process, schedule, installed database, production sample, or production
  mutation;
- no permanent hotfix branch/worktree/runtime and no blanket deploy authority.

## Acceptance Criteria

1. Current branch/integration, builder, installer, readiness, rollback, and
   runtime seams and gaps are evidenced from current authority.
2. One design names activation, priority, custody, candidate, reconciliation,
   staging, authorization, deployment, verification, rollback, and closeout
   contracts.
3. Dormant capacity, feature WIP, conflicting-lane pause, current-main start,
   priority integration, and post-hotfix reconciliation are explicit.
4. Delivery is split into provider-free packets with exact WI-001 and real-
   incident authority gates.
5. WI-007 is `READY`, P38 and the runbook point here, and planning/custody
   validation passes without tracker/runtime/production mutation.

## Execution Packet

- owner: coordinator session;
- critical path: advisory recall, current structural/script/live read-only
  evidence, architecture synthesis, dependency handoff, validation, and
  public-fork integration;
- write surfaces: Plan 0081, P38, WI-007, one architecture note, one JSON
  handoff, runbook, active-lane catalog, and active-plan test expectation;
- external effects: Git branch publication and PR integration only;
- bounds: two focused memory reads, four structural exploration rounds, one
  live read-only service status, one synthesis/remediation pass, one
  integration, and one closeout;
- terminal condition: all five criteria pass or an unresolved safety/interface
  boundary is recorded without starting implementation;
- authority classification: `inherited_authority`; this prepares the approved
  reserved hotfix lane without crossing tracker, incident, implementation,
  runtime, staging, deployment, rollback, or provider gates.

Subagent status: `not_spawned`; shared-interface investigation and custody
design remain coordinator-owned.

## Definition Of Done

The architecture and machine handoff are integrated, WI-007 provider-free
Packets 1-2 are ready for a separately owned top-level session, and staging,
incident, deployment, rollback, and production gates are explicit.

## Current Checkpoint

### Checkpoint P0081-C01 | 2026-09-13

Plan version: 1

State transition: `planned -> active`.

Progress classification: `outcome_progress`; existing policy and release
mechanisms have been joined into an executable, evidence-bounded hotfix path.

Authority classification:

- `inherited_authority` for read-only investigation and repo artifacts;
- `not_authorized` for tracker, incident declaration, implementation, release,
  installed runtime/database, browser/provider, schedule, staging, deployment,
  rollback, or production mutations.

Validation evidence:

- canonical `main` was clean and equal to `origin/main` at `0950077e` before
  the dedicated architecture worktree was created;
- Graphiti runtime is healthy and returned older source-backed artifact and
  rollback history, treated as advisory due to stale installed versions;
- CodeGraph is current at 353 files, 9,793 nodes, and 23,275 edges; targeted
  source inspection verified the builder, installer, readiness, rollback, and
  lifecycle-test seams;
- live read-only status reports PID 24968, service `0.3.116`, schema 17, ready,
  immutable index head, and 167 indexed documents;
- provider-free repository validation remains to run after this packet is
  fully rendered.

Subagent status and reconciliation:

- `not_spawned`; all evidence was gathered and reconciled by the coordinator.

Graphiti write status:

- `graphiti_write_pending`; Plans 0076-0080 already await recovery of the
  degraded ingestion path, so no new write is queued.

Next action:

- validate and integrate this architecture packet, close Plan 0081/P38
  planning work, and hand provider-free Packet 1 to a separate top-level lane
  session.

### Checkpoint P0081-C02 | 2026-09-13

Plan version: 1

State transition: `active -> closed`.

Progress classification: `outcome_progress`; the reserved hotfix architecture
and handoff are integrated while the slot remains dormant and zero-resource.

Authority classification:

- `inherited_authority` for public-fork integration and repository closeout;
- `not_authorized` for tracker, incident declaration, implementation, release,
  installed runtime/database, provider/browser, schedule, staging, deployment,
  rollback, or production mutations.

Validation evidence:

- architecture source tip `5842be158597db699a614b61a94753c6b474324c`
  merged through pull request 25 as
  `4feb4524bdeed0730cfecee45a1c72460363fd58`;
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

- retain WI-007/P38 as dormant reserved capacity; assign its provider-free
  Packet 1 to a separate top-level lane session when portfolio priority allows,
  or activate the real hotfix path only for a qualified incident.
