# Plan 0077 | Isolated Development Runtime Architecture And Lane Handoff

State: CLOSED
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
- the coordinator selected a repo-only controller plus a service-side
  cache-only effect gate, and PR 16 integrated the architecture at
  `187129cd7f67487a3de81901a3c214e64557f039`;
- WI-001 is `READY`; implementation and runtime provisioning have not started.

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

### Checkpoint P0077-C02 | 2026-09-13

Plan version: 1

State transition: `active -> closed`.

Progress classification: `verified_outcome`; WI-001's fail-closed architecture
and restart-safe Packet 1 handoff are integrated.

Authority classification:

- `inherited_authority` for integration and planning closeout;
- `not_authorized` for tracker, implementation runtime, process, provider,
  staging, or production mutation.

Validation evidence:

- pull request 16 merged source tip
  `6498f38af705bc1a308f47eb18af014c2fa819da` as
  `187129cd7f67487a3de81901a3c214e64557f039` on `origin/main`;
- canonical `main` fast-forwarded cleanly to that exact merge;
- 62 focused planning/lane-policy tests, plan authority, JSON parsing,
  work-item uniqueness, and patch hygiene pass;
- Graphiti provider preflight passed, but the exact pending Plan 0076 retry job
  `a1ac5f6c-ee50-4388-87bb-7ab3f036c91b` failed with a retryable transport
  timeout during node deduplication; `episode_uuid` is null and exact readback
  found no episode;
- no Plan 0077 write was queued behind the degraded ingestion path, and no
  installed or production runtime state changed.

Subagent status and reconciliation:

- `not_spawned`; coordinator-owned architecture evidence is authoritative.

Graphiti write status:

- `graphiti_write_pending`; Plan 0076 remains pending after the bounded retry,
  and the compact Plan 0077 architecture episode is also pending. Retry only
  through a later readiness, exact-find, single-write, poll, and readback flow.

Next action:

- assign WI-001 Packet 1 to one independent top-level lane session starting
  from current `origin/main`; create and register its dedicated branch/worktree
  before implementation.
