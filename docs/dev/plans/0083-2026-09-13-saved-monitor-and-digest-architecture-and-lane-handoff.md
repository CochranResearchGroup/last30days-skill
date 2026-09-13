# Plan 0083 | Saved Monitor And Digest Architecture And Lane Handoff

State: CLOSED
Lane: P40
Work item: WI-006
Branch: docs/saved-monitors-digests-architecture
Target: main
Integration: merge
Roadmap: P40
Plan version: 1
Date: 2026-09-13

## Objective

Turn WI-006 into a restart-safe `READY` lane by defining cache-only saved
monitors, accepted baselines, evidence-grounded deterministic digests, and a
separately gated idempotent delivery boundary.

## Current State

- WI-006 is a repo-local `TRIAGE` draft blocked by WI-002 and WI-004;
- retrieval snapshots, temporal versions, collection sightings, and durable
  notification patterns exist, but no monitor/baseline/digest contract does;
- legacy watchlists rerun acquisition and send webhooks without durable effect
  receipts, so they are not the product authority;
- no implementation, tracker, runtime, schedule, or delivery action has begun.

## Scope

- map retrieval heads, evidence history, collection causes, watchlists, and
  notification receipts;
- define monitor/view identity, immutable runs, accepted baseline, change
  classes, coverage, digest evidence, delivery idempotency, access, retention,
  lifecycle, and legacy import;
- split work into dependency-aware provider-free vertical packets;
- update WI-006 to `READY` and integrate architecture through the owned fork.

## Non-Goals

- no monitor/digest implementation, legacy migration, model call, or channel
  integration;
- no GitHub Issues/Project mutation while tracker activation is disabled;
- no installed runtime, schedule, browser/provider, notification, staging,
  deployment, or production mutation.

## Acceptance Criteria

1. Current reusable seams and legacy watchlist gaps are evidenced.
2. One contract freezes view/head/baseline identity and defines safe change
   semantics without rescraping.
3. Digests bind every entry to evidence and delivery is a distinct durable,
   idempotent, disabled-by-default effect.
4. Provider-free packets expose exact WI-002/WI-004/WI-001 joins and optional
   WI-003 synthesis without false removals or duplicate delivery.
5. WI-006 is `READY`, P40/runbook/catalog agree, and validation passes.

## Execution Packet

- accountable owner: coordinator session;
- coordination owner: coordinator session for roadmap, runbook, catalog, shared
  schemas, and integration joins;
- write surfaces: Plan 0083, P40, WI-006, note/JSON, runbook, active-lane
  catalog, and plan-authority fixture;
- external effects: Git branch publication and PR integration only;
- bounds: two focused memory reads, two CodeGraph rounds, one synthesis, one
  integration, and one closeout;
- terminal condition: all criteria pass or the unresolved boundary is recorded
  without implementation;
- authority: inherited for repo planning/integration; tracker/runtime/provider/
  schedule/delivery effects not authorized.

Subagent status: `not_spawned`; this is a tightly coupled coordinator-owned
shared-contract architecture slice.

## Definition Of Done

Architecture and machine handoff are integrated, dependencies are exact, and
one independent top-level implementation session can restart from the plan.

## Current Checkpoint

### Checkpoint P0083-C01 | 2026-09-13

Plan version: 1

State transition: `planned -> active`.

Progress classification: `outcome_progress`; monitor, baseline, comparison,
digest, and delivery semantics are reduced to a bounded vertical contract.

Authority classification:

- `inherited_authority` for investigation and repo artifacts;
- `not_authorized` for tracker, implementation, installed runtime, schedules,
  provider/browser, notification, staging, deployment, or production.

Validation evidence:

- canonical `main` and `origin/main` were reconciled at `8d3c50a2` after the
  concurrent policy v0.1.26 rollout, before edits;
- relevant updated policies, including collaborative development workflow,
  were reread; GitHub tracker activation remains explicitly disabled by policy
  and operator boundary, so the durable repo-local WI remains the locator;
- bounded Graphiti discovery found advisory notification receipts;
- CodeGraph at the current healthy index verified retrieval snapshots, query
  heads, watchlist, incident receipt, and transport seams;
- provider-free validation remains to run after rendering.

Subagent status and reconciliation:

- `not_spawned`; no parallel lane was opened.

Graphiti write status:

- `graphiti_write_pending`; no duplicate write was queued behind degraded
  ingestion.

Next action:

- validate/integrate this architecture, close Plan 0083/P40 planning work, and
  retain the exact WI-002/WI-004 implementation gates.

### Checkpoint P0083-C02 | 2026-09-13

Plan version: 1

State transition: `active -> closed`.

Progress classification: `verified_outcome`; the architecture and restart-safe
handoff are integrated while implementation remains dependency-gated.

Authority classification:

- `inherited_authority` for public-fork integration and repo closeout;
- `not_authorized` for tracker, implementation, runtime, schedule, provider/
  browser, notification, staging, deployment, or production.

Validation evidence:

- source tip `c959c15ebf134e120e5ae481bc1177336db69c41` merged through
  pull request 29 as `3333410742f5e1115657d1cc64d6c41fe0faaea1`;
- canonical `main` was fast-forwarded to the exact merge before this isolated
  closeout worktree was created;
- 62 focused tests plus plan-authority, active-planning, active-lane, JSON, and
  patch checks passed on the architecture packet;
- final integrated audits remain to run after this reconciliation.

Subagent status and reconciliation:

- `not_spawned`; coordinator evidence and merge receipts are authoritative.

Graphiti write status:

- `graphiti_write_pending`; no additional write was attempted.

Next action:

- retain WI-006/P40 as planned until WI-002 Packet 1 integrates, then assign
  Packet 1 to a separate top-level lane session and register its custody.

## Stop Rules

- stop before implementation, acquisition, delivery, or installed runtime use;
- stop before tracker mutation without explicit activation authority;
- stop if baseline advancement, removal evidence, partition safety, or delivery
  idempotency cannot be demonstrated provider-free.
