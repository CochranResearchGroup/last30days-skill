# Plan 0112 | X List And Product Closure

State: PLANNED
Lane: P35
Work item: WI-004
Branch: feat/x-tailored-follows-v3
Target: main
Integration: merge
Roadmap: P35
Plan version: 1
Date: 2026-09-14
Execution owner: unassigned until activation
Coordination owner: /root
Requested model route: gpt-5.6-terra, medium reasoning
Effective runtime model: unknown until reported

## Objective

Complete WI-004 provider-free by adding typed X-list acquisition and closing
scheduler, lifecycle, MCP, exact-follow search, readiness, and documentation
semantics without a real browser, schedule, or installed runtime.

## Current State

Packets 1-2 are integrated through PRs 68 and 79. Typed feed/topic/account/list
specs, immutable account context, account routing, lifecycle persistence, and
multi-cause publication exist. List work is still rejected/falls through;
scheduler aging and full MCP lifecycle parity remain incomplete.

## Scope

- add strict list-ID work dispatch and canonical `/i/lists/<id>` fixture route;
- cover list success, truthful empty, unavailable/private, auth/rate-limit,
  identity mismatch, bounded scroll, replay, and feed/account/list overlap;
- make oldest due time dominate scheduling and attention priority break only
  equal-due ties, preserving backoff, no-overlap, and profile leases;
- expose get/archive/include-archived parity through the existing MCP collection
  tool and prove CLI/app/MCP lifecycle agreement;
- prove exact partition-safe follow search through existing
  `legacy:spec:<collection_spec_id>` references without a new search field;
- update bounded operator/runtime guidance and complete provider-free presubmit.

## Non-Goals

No new collection migration or top-level API, WI-005 cross-service semantics,
real browser/profile/provider, installed database/runtime, schedule start,
release, staging, deployment, or live canary.

## Acceptance Criteria

1. Frozen list context reaches only the list adapter and cannot validate as
   account/topic/search work.
2. Synthetic outcomes preserve typed zero-yield/failure semantics, bounded
   work, and idempotent replay.
3. One native post seen by feed/account/list stays one content version with
   three exact sightings and partition-safe exact-follow search.
4. Scheduler tests prove oldest-due ordering, equal-due priority, and unchanged
   backoff/no-overlap/profile-lease controls.
5. CLI, app, and MCP agree on list/get/pause/resume/run/archive and archived
   default visibility.
6. Focused Python/Go suites, full Python presubmit, generated artifact join,
   runtime manifest, authority audits, and diff checks pass provider-free.
7. The exact clean branch is published and WI-004 has no remaining
   provider-free acceptance gap after coordinator integration.

## Execution Packet

- one top-level implementation owner, no children; two implementation attempts,
  one independent review, and one closed-world remediation pass;
- lane-owned writes: list acquisition/browser route, collection scheduler,
  focused Python fixtures/tests, MCP collection tool/tests, narrow docs, plan;
- shared contract/publication/search edits require coordinator reconciliation;
  generated catalog/manifest and authority projections are coordinator-only;
- terminal condition: published final provider-free WI-004 source acceptance or
  one exact blocker; do not begin WI-005.

## Definition Of Done

All seven criteria pass at an integration-ready checkpoint and coordinator
evidence can truthfully close WI-004 without any live canary.

