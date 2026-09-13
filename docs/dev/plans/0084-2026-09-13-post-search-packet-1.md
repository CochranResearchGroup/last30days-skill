# Plan 0084 | Post Search Packet 1 Contract Tracer

State: PLANNED
Lane: P33
Work item: WI-002
Branch: feat/post-search-v1
Target: main
Integration: merge
Roadmap: P33
Plan version: 1
Date: 2026-09-13

## Objective

Ship WI-002 Packet 1 as one provider-free tracer from stable search contract
through both storage families, service HTTP, Go MCP `search_posts`, and an
end-to-end fixture.

## Current State

- Plan 0076 and note 0117 are the accepted architecture;
- the service has `/v1/query`, retrieval snapshots, immutable document
  versions, access partitions, collection sightings, and Go MCP transport, but
  no dedicated post-search product contract;
- this launch ref contains only this plan and has not started implementation;
- GitHub Issues remain disabled, so WI-002 is the durable work-item locator.

## Scope

- freeze request/response and evidence-reference schemas plus cursor codec;
- implement lexical current-revision search in temporal and legacy stores;
- support source, access-partition, and publication-time filters;
- expose `/v1/posts/search` and MCP `search_posts` without changing
  `/v1/query`;
- add one provider-free end-to-end fixture and compatibility tests.

## Non-Goals

- no semantic/RRF ranking, broad filter matrix, performance campaign, answer
  synthesis, installed runtime, provider/browser access, staging, or release;
- no GitHub tracker mutation until activation is explicitly authorized.

## Acceptance Criteria

1. The same strict contract is enforced at Python service and Go MCP edges.
2. Both storage families return deterministic current-revision results and
   immutable evidence refs under exact partition/source/time filters.
3. Stable opaque cursor replay neither skips nor duplicates rows and rejects
   query/filter/head drift.
4. One provider-free fixture crosses contract, storage, app, HTTP, and MCP.
5. Existing `/v1/query` and focused retrieval/publication suites remain green.

## Execution Packet

- accountable human owner: repository operator;
- execution owner: next top-level Codex session opened in this worktree;
- coordination owner: coordinator session for shared schemas, roadmap,
  runbook, lane catalog, and WI-003/WI-008 joins;
- expected writes: service contracts/retrieval/store/app/HTTP, Go MCP
  contracts/tools, focused fixtures/tests, configuration/docs required by the
  public surface, and this branch-local plan/runbook checkpoint;
- inputs: Plan 0076, note 0117, WI-002, current `origin/main`;
- validation: focused Python/Go contract and end-to-end tests, code generation
  drift checks, plan/lane audits, and published-commit readback;
- terminal condition: all five criteria pass and a PR is integration-ready, or
  one exact blocker is recorded without widening scope;
- review bound: at most one risk-triggered drift-discovery pass and one
  closed-world remediation pass;
- authority: provider-free source implementation, tests, branch publication,
  and PR preparation; no installed/live/provider/tracker effects.

Subagents: optional only for bounded, disjoint support under the lane owner;
no nested delegation without a plan revision.

## Start Checklist

- fetch and prove this branch/worktree matches its registered checkpoint;
- reread AGENTS.md and relevant policies, Plan 0076, note 0117, and WI-002;
- run Graphiti discovery and CodeGraph impact on shared contract surfaces;
- change plan state to `OPEN`, record the runtime-reported owner/model when
  available, and publish the first recoverable checkpoint before coding;
- reconcile any new overlapping branch/PR with the coordinator.

## Stop Rules

- stop before installed runtime, live data/provider, staging, release, or
  production mutation;
- stop before changing `/v1/query` or WI-003 answer semantics;
- stop and reconcile if current `origin/main` or another lane owns an
  overlapping shared contract.

## Next Action

Open one independent top-level Codex session in
`/home/ecochran76/workspace.local/last30days-skill-wi002`, take custody of this
plan, register its `OPEN/ACTIVE_WORKTREE` transition through the coordinator,
and implement only the contract/catalog/cursor lexical tracer.
