<!-- last30days-work-item:WI-003 -->
# Answer agent questions through an evidence-rich MCP surface

State: IN_PROGRESS
Priority: P1
Lane: MCP
Parent: WI-000
GitHub issue: https://github.com/CochranResearchGroup/last30days-skill/issues/57
Blocked by: WI-002 Packet 1 contract integration; final acceptance by WI-002 closeout
Architecture: docs/dev/notes/0120-2026-09-13-agent-question-answering-mcp-architecture.md
Implementation plan seed: docs/dev/plans/0079-2026-09-13-agent-question-answering-mcp-architecture-and-lane-handoff.md
Last closed plan: docs/dev/plans/0100-2026-09-14-p36-packet-3-integration-reconciliation.md
Current plan: docs/dev/plans/0117-2026-09-14-question-public-runtime-closeout.md
Branch: feat/question-public-runtime-closeout-v1
Owner: /root/wave4_wi003_plan

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

Packet 3 integrated through PR 48 as canonical merge `d41e1a6e`. Plan 0117
now registers Packet 4's full filters, authorization, bounded lifecycle,
public HTTP/CLI/MCP surface, and fresh isolated-runtime acceptance. It remains
`OPEN` at published activation `cfe4e719`. Keep real model
execution, providers, installed runtimes, staging, and production behind their
own explicit gates.
