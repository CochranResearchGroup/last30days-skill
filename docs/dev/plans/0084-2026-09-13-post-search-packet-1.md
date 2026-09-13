# Plan 0084 | Post Search Packet 1 Contract Tracer

State: OPEN
Lane: P33
Work item: WI-002
Branch: feat/post-search-v1
Target: main
Integration: merge
Roadmap: P33
Plan version: 1
Date: 2026-09-13
Session owner: Codex thread 01a09caa-9116-7453-8914-5cd7d7ce0fca
Runtime model: unknown (not reported by runtime)

## Objective

Ship WI-002 Packet 1 as one provider-free tracer from stable search contract
through both storage families, service HTTP, Go MCP `search_posts`, and an
end-to-end fixture.

## Current State

- Plan 0076 and note 0117 are the accepted architecture;
- the service has `/v1/query`, retrieval snapshots, immutable document
  versions, access partitions, collection sightings, and Go MCP transport, but
  no dedicated post-search product contract;
- the registered launch checkpoint has been reconciled with current
  `origin/main` at `4f322e0a3c2d4795305c3bdfb853de27fae1c558`;
- Packet 1 acceptance is met on the branch: the strict schema, federated
  current-revision lexical backend, cursor, HTTP/client seam, MCP tool, shared
  fixture, source runtime manifest, and public guidance are implemented;
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
  public surface, and this branch-local plan checkpoint;
- inputs: Plan 0076, note 0117, WI-002, current `origin/main`;
- validation: focused Python/Go contract and end-to-end tests, code generation
  drift checks, plan/lane audits, and published-commit readback;
- terminal condition: all five criteria pass and a PR is integration-ready, or
  one exact blocker is recorded without widening scope;
- review bound: at most one risk-triggered drift-discovery pass and one
  closed-world remediation pass;
- authority: provider-free source implementation, tests, branch publication,
  and PR preparation; no installed/live/provider/tracker effects.

Subagents: `not_spawned`; this lane was executed directly by its independent
top-level owner as required by the activation instruction.

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

## Current Checkpoint

### Checkpoint P0084-C02 | 2026-09-13

Plan version: 1

State transition: `implementation_active -> packet_1_acceptance_met`; the plan
remains `OPEN` until integration.

Progress classification: `verified_outcome`; all five Packet 1 acceptance
criteria pass on the reconciled branch.

Authority classification:

- `explicit_authority` for Packet 1 source, tests, documentation, branch push,
  and a pull request to `CochranResearchGroup/last30days-skill:main`;
- `not_authorized` for CollectionSpec, tailored-follow lifecycle/migrations,
  isolated-runtime identity, installed runtime, providers, schedules, tracker,
  release, staging, production, or PR merge.

Validation evidence:

- branch merge base is current `origin/main`
  `4f322e0a3c2d4795305c3bdfb853de27fae1c558` with no unresolved divergence;
- `uv run pytest -q` passed the complete repository suite after the public MCP
  surface assertion was updated;
- the focused Packet 1 plus adjacent service/retrieval/publication/package
  selection passed, including the real Go MCP-to-Python Unix-socket smoke;
- `GOCACHE=/tmp/last30days-wi002-go-cache go test ./...`, `go vet ./...`, and
  `go build ./cmd/last30days-pp-mcp` passed under `mcp/`;
- two consecutive generator reads produced
  `722990d4c486fe545184092408e7e7c6c6136f2628dfecaba26f311d19337470`
  for `catalog_generated.go`; `git diff --check` and the plan-authority audit
  passed.

Effects and boundaries:

- source-only: no installed runtime, provider/browser, schedule, tracker,
  staging, production, or live database was read or mutated;
- `/v1/query`, answer semantics, collection/follow semantics, database schema,
  adapter/service versions, and release locks are unchanged;
- the checked-in source runtime manifest was refreshed so a later authorized
  build includes the new search module and schema; no runtime was installed.

Remaining bounded risks:

- Packet 1 is intentionally lexical/current-revision only; author, topic,
  collection, observed-time, filter-only browsing, all-revision traversal, and
  cross-store deduplication remain Packet 2;
- semantic/RRF quality, response-budget/performance evidence, release/version
  changes, and an installed fresh-client smoke remain Packets 3 and 4;
- cursors conservatively fail stale after any authorized component-head change,
  even when the changed row would not match the current filters.

Subagent status and reconciliation:

- `not_spawned`; implementation and validation were performed by the owning
  top-level session.

Graphiti write status:

- `not_written`; discovery was read-only and advisory, while this activation
  explicitly prohibited installed/live/provider state mutation. This durable
  repository checkpoint is authoritative.

Next action:

- commit and push this accepted packet, open but do not merge the fork-main PR,
  and hand review/integration back to the coordinator; do not start Packet 2.

## Next Action

Review and integrate the Packet 1 pull request into `main`. After integration,
the coordinator may register a separately bounded Packet 2 continuation; this
session must not begin it under the current authority.
