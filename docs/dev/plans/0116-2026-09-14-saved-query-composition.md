# Plan 0116 | Saved Query Composition Packet 2

State: OPEN
Lane: P40
Work item: WI-006
Branch: feat/saved-query-composition-v2
Target: main
Integration: merge
Roadmap: P40
Plan version: 1
Date: 2026-09-14
Execution owner: /root/wi002_search_packet2
Coordination owner: /root
Requested model route: gpt-6-astra, high reasoning
Effective runtime model: unknown until reported

## Objective

Compose the existing monitor kernel with the real stored-post search contract by
persisting an immutable saved-query version and freezing its exact bounded
evidence view into explicit baseline acceptance.

## Current State

Packet 1's provider-free monitor kernel is integrated. WI-002's search contract
and WI-004's follow contract are available, but the kernel still consumes a fake
saved-query provider. This packet implements query composition only; follow
composition and digest/delivery closure remain separate.

## Scope

- persist immutable saved-query definitions and versions;
- execute the exact query through `PostSearchBackend` in one snapshot lifetime;
- freeze evidence IDs, revisions, partitions, component head, cutoff, and
  coverage rather than persisting a process-local cursor;
- classify new, revised, and unchanged evidence; treat top-k absence as unknown,
  not removal;
- require explicit baseline acceptance and fail closed on stale baseline,
  partial/truncated traversal, cursor expiry/restart, or partition mismatch;
- add narrow local CLI/MCP parity behind coordinator-owned shared joins.

## Non-Goals

No follow view, digest generation, notification delivery, installed schedule,
refresh/acquisition, provider, browser, production, release, issue mutation, or
generated summary.

## Acceptance Criteria

1. Saved-query identity and every version are immutable and schema validated.
2. Search execution freezes exact evidence and coverage without durable cursors.
3. New/revised/unchanged classifications are deterministic and idempotent.
4. Absence, incomplete traversal, stale heads, restart, and partition drift
   never fabricate removals or silently restart from an unpinned view.
5. Baseline movement requires explicit acceptance; replay is side-effect safe.
6. Narrow CLI/MCP fixtures preserve the same contracts with effects disabled.
7. Focused monitor/search, full Python, Go test/vet, audit, and diff checks pass.

## Ownership And Topology

One top-level implementation owner, no children, at most two implementation
attempts, one independent review, and one closed-world remediation. Lane writes
are monitor contracts/kernel, new `service_monitor_views.py`, focused tests and
fixtures, and this plan. Shared app/CLI/MCP contracts, catalogs, manifests, and
authority projections remain coordinator-owned.

## Stop Rules

Stop on missing authoritative head/coverage evidence, unbounded cursor replay,
shared-file custody conflict, upstream search repair, or any provider,
installed-database, schedule, delivery, credential, or live effect.

## Definition Of Done

All seven criteria pass at integration. This closes Packet 2 but not WI-006;
follow composition and digest/delivery/runtime closure remain separately planned.

## Current Checkpoint

### Checkpoint P0116-C01 | 2026-09-14

Plan version: 1

State transition: `PLANNED -> OPEN`; activation only, implementation held.

Progress classification: `blocker_reduction`; the previously unassigned packet
now has an accountable execution owner and an exact publishable custody record.
No product acceptance criterion is claimed complete by this activation.

Custody and topology:

- execution owner: `/root/wi002_search_packet2`, reporting to coordinator
  `/root`, under Plan 0107's temporary parent/worker campaign topology;
- exact worktree:
  `/home/ecochran76/workspace.local/last30days-skill-wi006-v2`;
- branch: `feat/saved-query-composition-v2`, target `main`, integration by merge;
- activation base and pre-edit local HEAD:
  `bf12c730eaa592cf627311aeef36d06810a2e83c`;
- pre-edit worktree was clean. Canonical
  `/home/ecochran76/workspace.local/last30days-skill` remained clean on `main`
  at the same exact SHA, equal to the live `origin/main` readback;
- before publication the lane tracked `origin/main` and no live
  `refs/heads/feat/saved-query-composition-v2` existed. Activation publication
  must establish that lane remote and tracking ref, then verify exact local,
  upstream, and live remote equality;
- requested route: `gpt-6-astra`, high reasoning, as registered in this plan;
  effective model and effort: unknown because the runtime has not reported
  them. The existing agent is reused; its name is not model evidence;
- one lane owner, no children. Subagent status: activation performed by this
  existing campaign worker; no nested agent was spawned. Implementation bounds
  remain two attempts, one independent review, one closed-world remediation;
  this activation consumes no implementation attempt.

Authority classification and held evidence:

- `inherited_authority` for this turn is limited by the coordinator's explicit
  assignment to editing this plan, validating it, committing, publishing this
  branch, and read-only custody verification;
- implementation is held until coordinator continuation after activation
  integration and shared-lane reconciliation. All seven acceptance criteria
  remain unverified for Packet 2; no product source or test was edited or run;
- planned lane writes, not exercised here, are
  `service_monitor_contracts.py`, `service_monitors.py`, new
  `service_monitor_views.py`, focused tests/fixtures, and this plan;
- shared app/CLI/MCP contracts, generated catalogs/runtime manifests,
  `ROADMAP.md`, `RUNBOOK.md`, `docs/dev/active-lanes.yaml`, and work-item
  projections remain coordinator-owned. The current P40 catalog still points
  to closed Packet 1; this checkpoint does not claim globally reconciled
  Packet 2 custody;
- follow composition, digest/delivery, upstream search repair, WI-003 work,
  provider/browser/live data, installed runtime/database, schedule, credentials,
  PR/issue mutation, release/deployment and other effects are outside this turn.
  Live-effect expansion remains a `human_gate`;
- WI-006 final acceptance still waits for WI-002 closeout. WI-004 is closed,
  but its follow composition remains deliberately reserved for Packet 3.

Discovery and validation:

- re-read `AGENTS.md`, policies 0001, 0005-0010, 0012-0013, 0015, 0019,
  0021, 0023, 0025-0029 and 0032, this plan, WI-006, and Plan 0107's current
  Wave 3 registration checkpoint;
- Graphiti discovery: `skip`; current supplied assignment and repo authorities
  suffice for this plan-only activation. CodeGraph/source impact inspection is
  deferred to implementation; no index, runtime or product source was changed;
- Graphiti checkpoint projection is deferred to the coordinator because this
  assignment permits only the plan write and Git publication, with provider
  effects held. No memory or shared RUNBOOK write was attempted;
- `python3 dev/last30days/scripts/audit_plan_authority.py --root .` passed on
  the base and activation diff. `git diff --check` passed; scoped diff
  validation confirms that only this plan changed;
- the generic active planning audit failed already on the exact base with
  four coordinator-owned registration findings: Plan 0114 is not wired in
  ROADMAP or RUNBOOK; Plans 0115 and 0116 are not wired in RUNBOOK. Preserve
  those findings unchanged after the edit; no shared authority was repaired
  from this lane and the generic audit is not claimed passing;
- product Python/Go suites and runtime validation are intentionally not run
  for the activation-only change. Their evidence remains required during
  implementation and coordinator integration.

Next action or stop reason: validate and publish this plan-only activation,
return its exact SHA, clean status and local/upstream/live remote equality,
then stop. Do not start implementation from the plan's OPEN label. On a later
coordinator continuation, re-anchor the integrated base and shared ownership
before the first source edit; retain all plan stop rules.
