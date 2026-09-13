<!-- last30days-work-item:WI-004 -->
# Give selected X accounts and lists separate collection attention

State: READY
Priority: P1
Lane: Follows
Parent: WI-000
Blocked by: none
Architecture: docs/dev/notes/0119-2026-09-13-x-tailored-follow-product-architecture.md
Implementation plan seed: docs/dev/plans/0078-2026-09-13-x-tailored-follow-architecture-and-lane-handoff.md

## Problem

The general X feed scrape cannot express that selected accounts or lists need
different cadence, priority, provenance, and retrieval identity.

## Outcome / Proposed Solution

An operator can define an X account or list follow whose cadence, collection
receipts, and query identity are distinct from the general-feed scrape.

## Acceptance Evidence

- a versioned follow specification identifies target kind, canonical target,
  cadence, priority, enabled state, access partition, and provenance;
- scheduler and acquisition receipts distinguish tailored work from general
  feed work and prevent duplicate concurrent collection;
- pause, resume, update, retry, and delete semantics preserve history and fail
  closed on ambiguous identity;
- stored posts can be filtered by the follow and retain the collection cause;
- provider-free fixtures cover account, list, rate-limit, auth-required,
  deleted target, and idempotent replay paths;
- any authenticated X canary is separately authorized and serialized.

## Non-Goals

No follow action on the X platform itself, no production schedule change, and
no cross-service abstraction until this vertical slice is accepted.

## Ready Handoff

Assign one independent top-level lane session. Start from current
`origin/main`, create a dedicated `feat/x-tailored-follows-v1` worktree,
register its active custody, freeze the account/list fixture corpus, and
implement Packet 1 from the architecture note: compatible collection-purpose,
attention, lifecycle, canonical target identity, migration, get/list/archive,
and provider-free persistence tests. Do not enqueue a job, open a browser, use
a profile/provider, mutate an installed database or schedule, or install a
runtime in Packet 1.
