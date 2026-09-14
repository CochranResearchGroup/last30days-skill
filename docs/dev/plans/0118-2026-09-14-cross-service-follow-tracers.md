# Plan 0118 | Cross-Service Follow Tracers Packet 2

State: OPEN
Lane: P39
Work item: WI-005
Branch: feat/cross-service-follow-tracers-v1
Target: main
Integration: merge
Roadmap: P39
Plan version: 1
Date: 2026-09-14
Execution owner: /root/wave4_wi005_plan
Coordination owner: /root
Requested model route: gpt-6-astra, high reasoning
Effective runtime model: unknown until reported

## Objective

Implement provider-free native Reddit community/user and YouTube channel follow
tracers through the real collection, acquisition, publication, provenance, and
authorized search paths while preserving exact X and legacy compatibility.

## Current State

Plan 0115 closed the capability registry, exact X identity, identity-bound
compatibility evidence, and scheduler-isolated legacy quarantine. Reddit and
YouTube targets remain truthfully unavailable and their existing acquisition
paths flatten tailored intent into generic search/feed behavior.

## Scope

- add canonical Reddit community/user and YouTube channel-ID target contracts;
- extend capabilities with operation, identity, route, cadence, support, and
  dependency-readiness metadata;
- implement small fixture-backed native route/response validators with injected
  transports and no generic-search fallback;
- traverse disabled spec, lifecycle, coordinator, frozen worker request,
  provider route, publication, sighting provenance, and authorized cache query;
- preserve distinct native identity alongside stable follow target identity;
- retain exact X bytes/history and quarantine malformed historical rows.

## Non-Goals

No live locator resolution, provider/network call, handle/custom-URL lookup,
public-partition policy change, browser, installed runtime, real schedule,
release/deployment, issue mutation, fresh-runtime closeout, or other service
target contracts.

## Acceptance Criteria

1. Reddit community/user and YouTube channel selectors canonicalize strictly;
   unsupported/unresolved forms and route mismatches fail closed.
2. Success, zero yield, malformed/unavailable target, dependency absence,
   timeout/rate limit, pagination bounds, authorization, and replay are
   deterministic through injected production route code.
3. Lifecycle/revision/coalescing semantics and old-revision completion remain
   exact; readiness changes never activate a target.
4. X identities/history and general collections remain unchanged; malformed
   legacy rows remain readable/quarantined and cannot starve healthy due work.
5. Publication preserves all follow/general sightings without duplicating one
   source-native content version; exact follow filtering and negative partition
   cases pass.
6. Capability discovery and lifecycle/query results agree across existing
   service boundaries; a frozen 10,000-sighting baseline is retained.
7. Focused/full Python, Go test/vet, generated-contract/package checks, audits,
   and diff checks pass at the joined head.

## Ownership And Topology

One top-level implementation owner, no children, at most two implementation
attempts, one independent review, and one closed-world remediation. Lane writes
are follow capabilities/collection/acquisition, two small provider tracer
modules, focused fixtures/tests, and this plan. Shared contracts, job runner,
app/HTTP/client/CLI/MCP, catalogs, manifests, product docs, and authority are
coordinator-owned and serialized after Plan 0117's shared join.

## Stop Rules

Stop on changed X identity, history rewrites, generic-search fallback,
readiness masquerading as support, unbounded work, public access-policy change,
unregistered shared edits, or any required provider/browser/live locator/
installed runtime/schedule effect.

## Definition Of Done

All seven criteria pass and Packet 2 is integrated. WI-005 remains `READY` for
one separately bounded fresh-runtime closeout; this packet alone is not DONE.

## Current Checkpoint

### Checkpoint P0118-C01 | 2026-09-14

Plan version: 1

State transition: `unplanned -> PLANNED`; registration only.

Progress classification: `blocker_reduction`; provider-native fixture tracer
work is bounded without claiming adapter availability or runtime acceptance.

Authority classification:

- `inherited_authority`: Plan 0107 covers provider-free plan, activation,
  implementation, review, integration, and repo-local closeout;
- `human_gate`: provider/network/browser/live-locator, installed-runtime,
  schedule, staging, production, release, deployment, and issue effects.

Subagent status and reconciliation:

- `joined`; one read-only planning specialist returned this scope. No
  implementation owner exists until activation.

Next action: integrate registration, publish exact lane custody, reconcile it,
then assign one owner while reserving shared joins for the coordinator.

### Checkpoint P0118-C02 | 2026-09-14

Plan version: 1

State transition: `PLANNED -> OPEN`.

Progress classification: `blocker_reduction`; exact isolated custody is
accepted from canonical registration merge `d6cf8252` at
`/home/ecochran76/workspace.local/last30days-skill-wi005-v2` on
`feat/cross-service-follow-tracers-v1`.

Authority classification:

- `inherited_authority`: provider-free implementation, validation, branch
  publication, review, and integration under Plan 0107;
- every external-effect boundary in C01 remains held.

Subagent status and reconciliation:

- `assigned`; `/root/wave4_wi005_plan`, one owner with no children. Shared
  service/public transport, generated artifacts, docs, and authority remain
  coordinator-owned.

Next action: publish this activation checkpoint, reconcile canonical custody,
then implement both fixture tracers test-first within the lane write set.
