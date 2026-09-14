<!-- last30days-work-item:WI-006 -->
# Turn searches and follows into saved monitors and digests

State: READY
Priority: P2
Lane: MCP
Parent: WI-000
GitHub issue: https://github.com/CochranResearchGroup/last30days-skill/issues/59
Blocked by: WI-002 Packet 1 for monitor kernel/query tracer; WI-004 Packet 1 for follow tracer; WI-002 and WI-004 closeout for final acceptance
Last closed plan: docs/dev/plans/0093-2026-09-13-saved-monitors-packet-1.md
Branch: feat/saved-monitors-v1
Owner: Codex 01a09cf4-c89e-7660-9caf-66a78f34ded0

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
