<!-- last30days-work-item:WI-003 -->
# Answer agent questions through an evidence-rich MCP surface

State: READY
Priority: P1
Lane: MCP
Parent: WI-000
Blocked by: WI-002 Packet 1 contract integration; final acceptance by WI-002 closeout
Architecture: docs/dev/notes/0120-2026-09-13-agent-question-answering-mcp-architecture.md
Implementation plan seed: docs/dev/plans/0079-2026-09-13-agent-question-answering-mcp-architecture-and-lane-handoff.md
Last closed plan: docs/dev/plans/0091-2026-09-13-agent-question-answering-packet-1.md
Current plan: docs/dev/plans/0096-2026-09-13-agent-question-evidence-tracer-packet-2.md
Branch: feat/agent-question-evidence-v2
Owner: unassigned independent top-level Codex session

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

Packet 1 integrated through PR 41 as canonical merge `6d5eb5d9`. Before any
new implementation, integrate the Plan 0096 registration and assign its clean
dedicated worktree to one independent top-level Codex session. Packet 2 is only
real search/evidence composition and immutable dereference; keep model
execution, public MCP transport, providers, installed runtimes, staging, and
production behind their own explicit gates.
