# Plan 0108 | Post Search Packet 2

State: OPEN
Lane: P33
Work item: WI-002
Branch: feat/post-search-v2
Target: main
Integration: merge
Roadmap: P33
Plan version: 1
Date: 2026-09-14
Execution owner: /root/wi002_search_packet2
Coordination owner: /root
Requested model route: gpt-6-astra, high reasoning
Effective runtime model: unknown (not reported by runtime)
Effective reasoning effort: unknown (not reported by runtime)

## Objective

Complete WI-002 Packet 2 by extending the integrated cache-only post search
through author, topic, namespaced collection, observed-time, filter-only,
all-revision, and cross-store identity semantics with stable multi-page
traversal.

## Current State

Packet 1 is integrated at `75e7771e` with strict lexical current-revision
contracts, both storage families, source/access/publication filters, cursor,
HTTP, MCP, and provider-free fixtures. Packet 2 activation is recorded at
P0108-C01; product implementation and acceptance validation have not started.
The coordinator must reconcile the published activation and shared search
contract ownership before issuing the implementation continuation.

## Scope

- implement every Packet 2 filter on both storage adapters before ranking;
- support current/all revision modes and explicit immutable revision identity;
- deduplicate cross-store source-native collisions without losing provenance;
- prove deterministic duplicate-free multi-page traversal pinned to component
  heads, including concurrent fixture publication and stale/mismatched cursors;
- preserve HTTP/MCP parity and `/v1/query` behavior.

## Non-Goals

- no semantic/RRF packet, 10,000-post performance campaign, release/version,
  installed runtime, provider/browser, live data, schedule, or production;
- no WI-003 answer-semantics change.

## Acceptance Criteria

1. Both storage families enforce author, topic, collection, observed-time, and
   filter-only requests before ranking without access widening.
2. Current/all revision and cross-store collision fixtures preserve exact
   identity, revisions, causes, and evidence refs.
3. Multi-page traversal is stable, complete, deterministic, and duplicate-free
   across immutable heads; invalid or stale cursor replay fails closed.
4. Python service and Go MCP focused/compatibility suites pass and `/v1/query`
   remains unchanged.
5. The accepted branch is published for coordinator review with no external
   runtime or provider effect.

## Definition Of Done

All five criteria pass at one published checkpoint suitable for reviewed PR
integration, or one exact blocker is recorded without beginning Packet 3.

## Execution Packet

- accountable human owner: repository operator;
- execution owner: `/root/wi002_search_packet2`, one direct child of coordinator
  `/root`; no nested agents;
- authority inputs: Plan 0107, this Plan 0108, note 0117, closed Plan 0084,
  WI-002, current repository policies, and the coordinator's activation-only
  assignment;
- activation write surface: this plan only;
- intended implementation writes: `service_post_search.py`, search-specific
  portions of `service_contracts.py`, focused search/contract/HTTP fixtures and
  tests, and MCP search-tool validation/tests; Python modules are under
  `skills/last30days/scripts/lib/` and Go tool files under `mcp/internal/tools/`;
- shared overlaps requiring coordinator reconciliation: search schema
  `skills/last30days/schemas/service-contracts-v1.json`, Python contracts,
  `mcp/internal/tools/service_tools.go`, and its tests; shared schemas,
  `mcp/internal/contracts/catalog_generated.go`,
  `service/runtime-manifest.json`, roadmap, runbook, lane catalog, and work-item
  projections remain coordinator-owned;
- compatibility-only consumers: `service_app.py`, `service_http.py`,
  `service_client.py`, and `service_questions.py`; no WI-003 answer-semantics
  edits or `/v1/query` changes;
- implementation validation: focused hermetic Python search, contracts,
  application/HTTP, question-evidence compatibility and retrieval checks,
  followed by Go MCP contract/tool tests and coordinator-owned generated
  artifact reconciliation; no provider, browser, or installed runtime checks;
- bounds: inherit Plan 0107's two implementation attempts, one broad review,
  and one closed-world remediation pass; activation is not an implementation
  attempt or acceptance result;
- terminal condition for this turn: publish this plan-only activation, verify
  exact remote equality and clean local custody, and return to the coordinator.

## Current Checkpoint

### Checkpoint P0108-C01 | 2026-09-14

Plan version: 1

State transition: `planned -> activation_published`; plan state is `OPEN`.

Progress classification: `hardening`; execution ownership, custody, and the
implementation boundary are durable. No Packet 2 acceptance criterion is
claimed complete.

Authority classification:

- `inherited_authority` for this plan-only activation, commit, and push to
  `origin/feat/post-search-v2`. The current assignment ends after activation
  publication. Plan 0107 preserves the broader provider-free campaign authority;
  this checkpoint does not expand its effect boundary.

Base and custody evidence:

- assigned checkout:
  `/home/ecochran76/workspace.local/last30days-skill-wi002-v2`;
- branch: `feat/post-search-v2`; initial local HEAD and merge base with freshly
  fetched `origin/main`: `bca720d0406d8a4f6a8d9ac645eceeead20b8432`;
- canonical checkout `/home/ecochran76/workspace.local/last30days-skill`
  retains clean `main` at the same SHA, equal to `origin/main`;
- the base integrated the campaign through owned-fork PR 77; initial lane
  status was clean and `origin/feat/post-search-v2` did not yet exist;
- remote destination: `CochranResearchGroup/last30days-skill`, exact branch
  `refs/heads/feat/post-search-v2`; the activation commit is identified by the
  published branch readback rather than a self-referential SHA in this file.

Discovery evidence:

- all required policies and the five authority inputs above were read;
- Graphiti discovery skill used read-only doctor and one three-fact search in
  `last30days_skill_main`; doctor was healthy and the returned July/August
  facts did not establish current Packet 2 decisions, so current repo evidence
  remained authoritative;
- lane CodeGraph status reported no `.codegraph/` index; no initialization was
  performed. With coordinator concurrence, canonical CodeGraph was used at the
  identical clean source base. Its status reported 376 files, 10,596 nodes,
  and 26,335 edges without a staleness warning;
- canonical exploration of `PostSearchBackend`, `PostSearchRequest`, and
  `search_posts` found the application -> backend path and separate HTTP search
  route. Packet 1 accepts only source/publication filters, requires query,
  selects current revisions, and rejects a cursor after component-head drift;
- impact of `PostSearchBackend` covered 21 symbols, including the application,
  search tests, question-evidence tests, HTTP/product/app tests, and the service
  entrypoint; `PostSearchRequest` impact covered seven symbols including
  contract serialization and retrieval/supervisor/intelligence tests;
- `service_questions.py` consumes the search request and evidence refs. Preserve
  those defaults and exact provenance while extending the search contract;
  coordinate shared schemas before coding.

Validation evidence:

- pre-edit plan-authority audit passed with zero issues; the first post-edit
  run rejected an inline authority label, which was reformatted to the expected
  standalone heading without changing authority;
- corrected post-edit plan-authority audit passed with three active plans and
  zero issues; `git diff --check` passed and only this plan changed;
- activation validation is the plan-authority audit, `git diff --check`, an
  exact one-file staged diff, and post-push clean status/remote SHA equality;
- product tests are intentionally not run for this documentation-only
  activation; no product source or tests are changed, and no implementation
  acceptance result is implied.

Subagent status and reconciliation: this lane is the coordinator's active
bounded worker `/root/wi002_search_packet2`; no children were spawned. The
coordinator owns acceptance of this activation and all shared projections.
Requested route remains `gpt-6-astra` with high reasoning as specified by the
packet; effective model and effort are unknown because no runtime readback
reported them.

Graphiti write status: `not_written`; activation scope permits discovery and
one plan edit, not a durable-memory/provider write. This repository checkpoint
is the durable authority; no runbook or memory projection was edited.

Material blockers: none for plan-only activation. Shared schema ownership and
coordinator projection reconciliation must be resolved before product edits.

Next action: return the exact published activation SHA, clean status, remote
equality, and overlap list to the coordinator. Resume the bounded Packet 2
implementation only after the coordinator reconciles activation and assigns
the shared contract boundary; do not begin Packet 3.

## Stop Rules

- stop before shared WI-003 answer changes, semantic ranking, runtime, provider,
  schedule, issue, release, staging, or production effects;
- stop and notify the coordinator before editing coordinator-owned projections,
  generated catalogs, or a conflicting shared schema.
