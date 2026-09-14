<!-- last30days-work-item:WI-004 -->
# Give selected X accounts and lists separate collection attention

State: IN_PROGRESS
Priority: P1
Lane: Follows
Parent: WI-000
GitHub issue: https://github.com/CochranResearchGroup/last30days-skill/issues/56
Blocked by: none
Architecture: docs/dev/notes/0119-2026-09-13-x-tailored-follow-product-architecture.md
Implementation plan seed: docs/dev/plans/0078-2026-09-13-x-tailored-follow-architecture-and-lane-handoff.md
Implementation plan: docs/dev/plans/0086-2026-09-13-x-tailored-follows-packet-1.md
Completed reconciliation plan: docs/dev/plans/0104-2026-09-14-p35-current-main-reconciliation.md
Last completed plan: docs/dev/plans/0109-2026-09-14-tailored-follows-packet-2.md
Active plan: docs/dev/plans/0112-2026-09-14-x-list-and-product-closure.md
Branch: feat/x-tailored-follows-v3

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

Packet 1 is integrated through PR 68 at canonical merge
`87858934c8498dccbdeda549ad73f626dbc143a7`; its validated published head is
`434ac770eb1b6aeda37f455c1a35e3ddb9a69ad0`. WI-009 is now complete, so Packet
2 is eligible for separate planning. This readiness does not authorize a job,
browser, profile/provider, installed database or schedule mutation, or runtime
installation.

Packet 2 was activated at checkpoint `43f041f4` under Plan 0109 and completed
typed X account context propagation, routing, provider-free outcome fixtures,
and multi-cause publication; list routing and every live effect remain outside
that packet.

Packet 2 integrated through PR 79 at canonical `fae31198` after remediation
of legacy-revision and zero-yield review findings. Next work is separately
planned typed X-list routing and lifecycle/scheduler/search closure.

The final provider-free packet is active at published plan-only checkpoint
`69bf4d36`; product work remains held until canonical custody reconciliation.
