<!-- last30days-work-item:WI-004 -->
# Give selected X accounts and lists separate collection attention

State: IN_PROGRESS
Priority: P1
Lane: Follows
Parent: WI-000
GitHub issue: https://github.com/CochranResearchGroup/last30days-skill/issues/56
Blocked by: WI-009 before Packet 2; Packet 1 reconciliation is active under Plan 0104
Architecture: docs/dev/notes/0119-2026-09-13-x-tailored-follow-product-architecture.md
Implementation plan seed: docs/dev/plans/0078-2026-09-13-x-tailored-follow-architecture-and-lane-handoff.md
Implementation plan: docs/dev/plans/0086-2026-09-13-x-tailored-follows-packet-1.md
Active plan: docs/dev/plans/0104-2026-09-14-p35-current-main-reconciliation.md
Branch: feat/x-tailored-follows-v1

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

## Active Handoff

Packet 1 is acceptance-complete and published at
`d2c9f8ebfa79e99eb501910c7d606ce3bcbcf07d`. Plan 0104 owns its current-main
reconciliation and combined provider-free validation through the normal
pull-request workflow. Do not start Packet 2 or enqueue a job, open a browser,
use a profile/provider, mutate an installed database or schedule, or install a
runtime.
