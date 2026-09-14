<!-- last30days-work-item:WI-003 -->
# Answer agent questions through an evidence-rich MCP surface

State: IN_PROGRESS
Priority: P1
Lane: MCP
Parent: WI-000
Blocked by: WI-002 Packet 1 contract integration; final acceptance by WI-002 closeout
Architecture: docs/dev/notes/0120-2026-09-13-agent-question-answering-mcp-architecture.md
Implementation plan seed: docs/dev/plans/0079-2026-09-13-agent-question-answering-mcp-architecture-and-lane-handoff.md
Last closed plan: docs/dev/plans/0099-2026-09-14-p36-packet-3-launch-registration.md
Current plan: docs/dev/plans/0100-2026-09-14-p36-packet-3-integration-reconciliation.md
Branch: docs/p36-packet3-integration
Owner: coordinator Codex thread `01a0860e-b671-7f62-b6ae-6c06a08e6852`

## Problem

Agents can call narrow service tools but lack a coherent question surface that
binds synthesized answers to inspectable cross-service evidence.

## Outcome / Proposed Solution

An agent can ask what is happening across authorized services and receive a
bounded answer plus inspectable supporting posts from the stable retrieval
contract.

## Acceptance Evidence

- MCP discovery exposes compact question, search, and evidence-read tools with
  explicit schemas and pagination;
- answers cite stable stored evidence and distinguish source fact, temporal
  inference, uncertainty, and no-evidence outcomes;
- questions can be constrained by service, account/list/topic, collection,
  and time range;
- access partitions and provider-unavailable cache-only behavior fail closed;
- provider-free contract tests cover contradictory evidence, stale evidence,
  partial results, and unsupported claims;
- one fresh client proves discovery and an end-to-end evidence round trip.

## Non-Goals

No autonomous provider mutation, follow creation, or claim that generated
summaries replace source evidence.

## Next Owner Action

Packet 3 is integration-ready at exact remote checkpoint `75f2342e`; the
provider-free structured-turn adapter, model/effect receipts, citation-closed
validation, fallback, and retry/replay tests are joined into Plan 0100 with a
current source manifest and a fully green 2,860-test collection. Merge the
reviewed integration candidate, return WI-003 to `READY`, and plan Packet 4's
public HTTP/MCP surface separately. Keep real model execution, providers,
installed runtimes, staging, and production behind their own explicit gates.
