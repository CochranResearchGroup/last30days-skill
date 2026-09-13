<!-- last30days-work-item:WI-006 -->
# Turn searches and follows into saved monitors and digests

State: READY
Priority: P2
Lane: MCP
Parent: WI-000
Blocked by: WI-002 Packet 1 for monitor kernel/query tracer; WI-004 Packet 1 for follow tracer; WI-002 and WI-004 closeout for final acceptance

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

After WI-002 Packet 1 integrates, assign one independent top-level session,
create `feat/saved-monitors-v1` from current `origin/main`, register custody,
and execute Packet 1 only: immutable monitor/run/baseline contracts, fake view
provider, comparison, acceptance, lifecycle, and replay tests. Do not refresh,
scrape, schedule an installed service, or deliver externally.
