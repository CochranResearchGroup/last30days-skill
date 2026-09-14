<!-- last30days-work-item:WI-006 -->
# Turn searches and follows into saved monitors and digests

State: READY
Priority: P2
Lane: MCP
Parent: WI-000
GitHub issue: https://github.com/CochranResearchGroup/last30days-skill/issues/59
Blocked by: none for the next provider-free packet
Last closed plan: docs/dev/plans/0116-2026-09-14-saved-query-composition.md
Active plan: docs/dev/plans/0121-2026-09-14-monitor-digest-product-closeout.md
Branch: feat/monitor-digest-product-closeout-v1
Owner: unassigned

## Problem

Users must currently repeat retrieval manually and cannot receive an
idempotent account of what changed since an accepted prior view.

## Outcome / Proposed Solution

A user can save a query or follow view, detect evidence-backed changes, and
receive a reviewable digest without re-scraping or duplicating prior items.

## Acceptance Evidence

- monitor state stores query/follow version, cursor, cadence, access partition,
  and delivery preference;
- change detection is idempotent and distinguishes new, revised, removed, and
  unchanged evidence;
- digest output links every statement to stored evidence and records its
  coverage window;
- retries cannot redeliver an accepted digest unless explicitly requested;
- delivery remains disabled in fixtures and requires separate channel-specific
  authority for live notification.

## Non-Goals

No unsolicited alerts, hidden schedules, or notification-channel integration
without its own work item and effect gate.

## Selected Architecture

A saved monitor references an immutable query or follow view, compares only
frozen cache evidence against the last explicitly accepted baseline, and
prepares an evidence-linked deterministic digest. Delivery is a separate
disabled-by-default durable intent with exact idempotency and authority.

Authority:

- `docs/dev/notes/0124-2026-09-13-saved-monitor-and-digest-product-architecture.md`
- `docs/dev/plans/0083-2026-09-13-saved-monitor-and-digest-architecture-and-lane-handoff.md`

## Next Owner Action

Packet 1 integrated through PR 41 as canonical merge `6d5eb5d9`. Before any
new implementation, write and register a separately bounded packet from
current `origin/main` for query-view composition. Follow tracing remains gated
by P35 integration; refresh, scraping, installed scheduling, and delivery
remain separately authorized effects.

Plan 0116 registers Packet 2 for immutable saved-query composition over the
accepted WI-002 search contract. WI-004 is now DONE, but follow composition is
still deliberately reserved for Packet 3. Plan 0116 remains `PLANNED` until
exact branch/worktree custody is published and reconciled.

Activation checkpoint `d764f257` is published and awaits coordinator custody
reconciliation before implementation begins.

Packet 2 integrated through reviewed PR 87 as canonical merge `d2f15ed6`.
Immutable saved queries now capture and replay bounded current-revision search
views through strict local CLI/HTTP/MCP parity, with explicit baseline
acceptance and no schedule or delivery side effect. WI-002 is `DONE`; WI-006
returns to `READY` for separately planned follow composition and deterministic
digest/delivery-intent packets.
