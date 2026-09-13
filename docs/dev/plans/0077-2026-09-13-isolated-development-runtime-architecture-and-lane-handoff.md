# Plan 0077 | Isolated Development Runtime Architecture And Lane Handoff

State: OPEN
Lane: P34
Work item: WI-001
Branch: docs/isolated-dev-runtime-architecture
Target: main
Integration: merge
Roadmap: P34
Plan version: 1
Date: 2026-09-13

## Objective

Turn WI-001 into a restart-safe `READY` implementation lane by mapping the
current service/install/runtime boundaries, choosing a fail-closed development
lifecycle, and defining vertical delivery packets with provider-free evidence.

## Current State

- WI-001 is a repo-local `TRIAGE` draft and GitHub Issues remain disabled;
- the production service is healthy, but no staging or isolated lane runtime
  has been provisioned or claimed;
- current code provides independent DB/socket arguments but inherits config,
  source readiness, credentials, and optional runtime features from the host;
- the coordinator has selected a repo-only controller plus a service-side
  cache-only effect gate; implementation has not started.

## Scope

- use Graphiti as advisory recall and verify useful claims against current code
  and live read-only runtime state;
- use CodeGraph to map service bootstrap, configuration, source readiness,
  process, health, and install seams;
- define identity, path, environment, effect, collision, lifecycle, teardown,
  production, and staging boundaries;
- split implementation into vertical provider-free packets;
- update WI-001 to `READY` with one exact next owner action;
- integrate the architecture packet through the owned public fork.

## Non-Goals

- no controller or service implementation in this architecture slice;
- no service install, restart, signal, process, database, browser, provider,
  schedule, credential, deployment, staging, or production mutation;
- no GitHub Issues, Project, label, or repository-setting mutation;
- no permanent `develop` branch or reassignment of other product lanes.

## Acceptance Criteria

1. Current production identity, service startup, DB/socket/config, source
   readiness, optional loop, and installer boundaries are evidenced.
2. One design names deterministic lane identity and paths, strict environment
   and effect policies, process proof, collision detection, health/status, and
   exact-target teardown.
3. Production remains untouched and staging is defined as a separate later
   deployment identity rather than a Git branch.
4. Delivery is split into provider-free vertical packets, with explicit tests
   for two concurrent lanes, request denial, PID reuse, and production
   noninterference.
5. WI-001 is `READY`, P34 and the runbook point here, and plan/canonical
   authority validation passes without runtime or tracker mutation.

## Execution Packet

- owner: coordinator session;
- critical path: advisory recall, current structural/source evidence, live
  read-only verification, architecture synthesis, work-item handoff,
  validation, and public-fork integration;
- write surfaces: Plan 0077, P34, WI-001, one architecture note, one JSON
  handoff, runbook, and active-lane catalog;
- external effects: Git branch publication and PR integration only;
- bounds: two focused memory reads, four CodeGraph exploration rounds, one
  live read-only service census, one synthesis/remediation pass, one
  integration, and one closeout;
- terminal condition: all five criteria pass or the unresolved safety boundary
  is recorded without starting implementation;
- authority classification: `inherited_authority`; this prepares the approved
  runtime lane without crossing tracker, installed-runtime, or provider gates.

Subagent status: `not_spawned`; repo policy directs the coordinator to perform
shared-interface exploration directly, and no parallel implementation began.

## Definition Of Done

The architecture and machine handoff are integrated, WI-001 is ready for one
independent top-level lane session, and runtime/tracker/production boundaries
are truthfully recorded.

## Current Checkpoint

### Checkpoint P0077-C01 | 2026-09-13

Plan version: 1

State transition: `planned -> active`.

Progress classification: `outcome_progress`; current runtime seams and hazards
have been reduced to a fail-closed vertical delivery contract.

Authority classification:

- `inherited_authority` for read-only investigation and repo artifacts;
- `not_authorized` for tracker, installed runtime, process, provider, staging,
  or production mutations.

Validation evidence:

- canonical `main` was clean and equal to `origin/main` at `b71e6523` before
  the dedicated architecture worktree was created;
- Graphiti is healthy and one bounded source-backed service-first episode was
  retrieved from `last30days_skill_main`;
- CodeGraph is healthy at 353 files, 9,793 nodes, and 23,275 edges and exposed
  the service, config, source-policy, HTTP, client, and runtime seams;
- live read-only evidence identifies active production PID `24968`, exact unit,
  launcher, environment file, socket, service `0.3.116`, schema 17, and ready
  status;
- no installed/runtime/provider/production mutation was performed.

Subagent status and reconciliation:

- `not_spawned`; all evidence was gathered and reconciled by the coordinator.

Graphiti write status:

- `pending_closeout`; one compact episode is due after durable integration.

Next action:

- validate and integrate this architecture packet, then close Plan 0077/P34
  planning work and hand WI-001 Packet 1 to one independent top-level session.
