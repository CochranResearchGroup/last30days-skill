<!-- last30days-work-item:WI-003 -->
# Answer agent questions through an evidence-rich MCP surface

State: IN_PROGRESS
Priority: P1
Lane: MCP
Parent: WI-000
Blocked by: WI-002 Packet 1 contract integration; final acceptance by WI-002 closeout
Architecture: docs/dev/notes/0120-2026-09-13-agent-question-answering-mcp-architecture.md
Implementation plan seed: docs/dev/plans/0079-2026-09-13-agent-question-answering-mcp-architecture-and-lane-handoff.md
Current plan: docs/dev/plans/0091-2026-09-13-agent-question-answering-packet-1.md
Branch: feat/agent-question-answer-v1
Owner: Codex 01a09cf4-c89c-7ad2-9b64-8dc95c4cbec6

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

## Ready Handoff

Do not start implementation until WI-002 Packet 1 integrates the stable
`PostSearchBackend`, request/response, search-head, and evidence-ref contracts.
Then assign one independent top-level lane session from current `origin/main`,
create and register `feat/agent-question-answer-v1`, and implement Packet 1
from the architecture note: strict question/answer/citation/status contracts,
migration, durable queue/lease/idempotency, and fake search/worker tests. Do
not invoke a model, source adapter, browser, refresh, follow, schedule,
installed runtime, staging, or production service in Packet 1.
