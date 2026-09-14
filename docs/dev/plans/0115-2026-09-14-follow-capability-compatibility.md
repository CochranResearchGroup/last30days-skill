# Plan 0115 | Follow Capability And Compatibility Packet 1

State: OPEN
Lane: P39
Work item: WI-005
Branch: feat/cross-service-follow-capabilities-v1
Target: main
Integration: merge
Roadmap: P39
Plan version: 1
Date: 2026-09-14
Execution owner: /root/wi004_packet3_planning
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

## Current Checkpoint

### Checkpoint P0115-C01 | 2026-09-14

Plan version: 1

State transition: `PLANNED -> OPEN`.

Progress classification: `blocker_reduction`; this activation assigns one
recoverable provider-free owner and freezes the registry/compatibility boundary.
No product source, test, fixture, generated artifact, shared authority, or
runtime state changed.

Custody:

- execution owner: `/root/wi004_packet3_planning` in
  `/home/ecochran76/workspace.local/last30days-skill-wi005-v1` on
  `feat/cross-service-follow-capabilities-v1`;
- exact registered base and pre-edit `HEAD`:
  `bf12c730eaa592cf627311aeef36d06810a2e83c`;
- this worktree was clean at preflight. The activation commit must be published
  to its same-named owned-fork branch and its exact remote equality verified
  before any implementation resumes.

Authority and held implementation boundary:

- inherited authority covers only this branch-local plan activation, later
  provider-free source/tests, branch publication, bounded review, and
  coordinator integration under Plan 0107 and WI-005;
- this activation authorizes no product implementation. The next implementation
  turn must re-read current overlaps and use only the declared registry,
  collection, fixture, and focused-test surfaces;
- human gates remain for provider/browser/profile access, locator resolution,
  live data, jobs or schedule starts, installed databases/runtimes, release,
  deployment, rollback, and issue mutation;
- coordinator-owned shared contracts/schemas, generated catalog/runtime
  manifest, public MCP/CLI discovery, and `ROADMAP.md`, `RUNBOOK.md`,
  work-item, and active-lane projections are held out of this lane.

Prepared implementation evidence and dependencies:

- WI-004 and Plan 0112 are closed provider-free upstream authority; this plan's
  bounded purpose is the next registry/compatibility tracer, not a Reddit or
  YouTube acquisition implementation;
- the frozen plan records the live source seam: global collection surface
  validation, an X-only tailored-follow admission boundary, and generic Reddit
  and YouTube query routes. A closed capability/compatibility seam is required
  before later provider tracers can begin;
- P39/WI-005 coordinator projections must reconcile stale WI-004 dependency
  wording before any implementation activation. No migration, SQLite fixture,
  service process, provider, or runtime was created or run in this checkpoint.

Topology and model:

- one top-level owner, no children, no delegated review or implementation in
  this activation; Plan 0107 retains its two implementation attempts, one
  broad independent review, and one closed-world remediation bound;
- requested route is `gpt-6-astra` at high reasoning because identity
  preservation and fail-closed compatibility are consequential shared-boundary
  work; effective runtime model and effort are `unknown` until reported.

Validation and stop:

- activation validation is policy/plan-scope inspection, clean preflight,
  `git diff --check`, scoped plan-only diff review, commit, push, and exact
  local/upstream/live-remote equality. Product suites are intentionally held
  because no product file changes;
- stop after publishing this checkpoint. Do not create a pull request, mutate
  WI-005 or GitHub, or begin Packet 1 until a subsequent explicit implementation
  assignment from current canonical coordination authority.
