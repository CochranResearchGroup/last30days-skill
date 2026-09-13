<!-- last30days-work-item:WI-006 -->
# Turn searches and follows into saved monitors and digests

State: TRIAGE
Priority: P2
Lane: MCP
Parent: WI-000
Blocked by: WI-002, WI-004

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
