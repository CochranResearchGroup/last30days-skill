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
HTTP, MCP, and provider-free fixtures. Packet 2 source implementation and
focused acceptance are complete at P0108-C02. The coordinator has accepted
the shared search-contract boundary and bounded process-local cursor design.
Generated catalog/runtime-manifest reconciliation and the complete joined Go
suite remain coordinator-owned gates before integration; this plan stays OPEN.

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
- implementation writes: `service_post_search.py`, search-specific
  portions of `service_contracts.py`, focused search/contract/HTTP fixtures and
  tests, and MCP search-tool validation/tests; Python modules are under
  `skills/last30days/scripts/lib/` and Go tool files under `mcp/internal/tools/`;
- shared overlaps reconciled by the coordinator: the dedicated search schema
  `skills/last30days/schemas/post-search-contracts-v1.json`, Python contracts,
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
- current terminal condition: publish the source acceptance checkpoint, verify
  exact remote equality and clean local custody, and return the generated-join
  gate to the coordinator without opening a PR or starting Packet 3.

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

### Checkpoint P0108-C02 | 2026-09-14

Plan version: 1

State transition: `activation_published -> source_acceptance_met_pending_generated_join`.

Progress classification: `outcome_progress`; Packet 2 filters, revision
identity, deduplication, stable traversal, and public boundaries now have
provider-free implementation evidence. Full integration acceptance is pending
the explicitly coordinator-owned generated-artifact join.

Authority classification:

- `inherited_authority`: coordinator continuation authorized post-search
  source, search-only schema/MCP edits, focused fixtures, validation, necessary
  public guidance, branch checkpoint and publication;
- generated catalog and runtime manifest remain coordinator-owned; the
  coordinator directed publication without them and will generate once after
  joining P33/P35;
- no PR/merge, roadmap/runbook/lane/work-item edits, service installation,
  provider/browser/live data, issue, staging, production, release, or deployment.

Base and custody:

- freshly fetched `origin/main` was
  `8a3b726918bcb5055db2294c897691a2171fa24c` (activation PR 78);
- merged without rewriting activation ancestry as
  `d5b18db06cad52de2abd0c4ffc6163f6807a445e`;
- pre-implementation worktree was clean; the source tree matched that exact
  main base, with only this branch-local plan differing;
- worktree/branch and execution owner remain those in P0108-C01.

Implemented contract and acceptance evidence:

1. Both SQL adapters enforce authorized partitions, exact authors/sources,
   explicit topics, namespaced collection causes, inclusive publication and
   observation bounds before ranking. Null/omitted query is allowed only with
   a narrowing filter; missing filter evidence excludes the version. Legacy
   topics/causes use partition-matched version sightings. Temporal topics use
   explicit string `topic_ids` in immutable version metadata; collection causes
   use partition-matched tick/lane facts. Observation ranges match one recorded
   observation in the interval; the returned observed time is the latest
   retained observation.
2. `revision_mode=current|all` and all three declared sort modes are exposed
   at Python/HTTP/MCP boundaries. Native post identity includes access partition
   and falls back to URL only when native identity is absent. Current cross-store
   collisions choose the latest-observed current representative, then stable
   family/version ties; every contributing immutable ref is retained in
   `evidence_refs`. All mode groups replicas only by post/content hash and
   preserves distinct hashes. The primary `revision_id` continues to equal its
   `evidence_ref.version_id`, preserving WI-003 compatibility.
3. Immutable process-local search snapshots retain ordered hits and component
   digests. Cursors bind request, authorized partition set, modes, page size,
   component heads, and exact sort position. Concurrent publication leaves
   retained pagination unchanged; tampering, mismatched requests/access, expired
   heads, restart, or FIFO eviction fail closed. HTTP returns safe
   `409 cursor_stale` for unretained heads. No source DB write or migration is
   needed; read connections use SQLite `mode=ro` and `query_only`.
4. Focused Python compatibility and Go behavior/vet checks pass. `/v1/query`
   and WI-003 answer implementation are unchanged. The complete Go suite has
   the one known generated-search-catalog failure described below.
5. This coherent source plus plan checkpoint is published to the same owned
   fork branch for coordinator review. Publication proves source custody only;
   no external runtime/provider acceptance is claimed.

Validation receipts (performed directly by the lane owner):

- TDD red: the first two new filter/browse cases failed at the Packet 1
  required-query boundary before implementation; the repaired selection passed;
- final focused Python selection: **134 passed in 10.25 seconds**, command:
  `uv run pytest tests/test_service_post_search.py tests/test_service_contracts.py tests/test_service_app.py tests/test_service_http.py tests/test_service_retrieval.py tests/test_service_question_evidence.py tests/test_service_question_contracts.py tests/test_skill_service_first_contract.py tests/test_service_supervisor.py tests/test_service_intelligence_contracts.py tests/test_service_product.py tests/test_source_log_visibility.py --override-ini addopts='' -q`;
- `go test ./...` under `mcp/`: all behavior packages passed; only
  `TestGeneratedPostSearchCatalogIsCurrent` failed because generation is reserved
  for the coordinator. Existing digest:
  `420c8437d213fb67438a79ad4830f28352ad29c1b6db7dc72dc2f93842265ff4`;
  expected dedicated search-schema digest:
  `ac42d96af99bef3518af89f9a56522ee178ac71afb975df4f35bf368df23d26e`;
- `go test ./... -skip TestGeneratedPostSearchCatalogIsCurrent` and
  `go vet ./...` passed. The explicit exclusion is not a full-suite pass;
- one self-review/remediation pass added strict malformed-cursor type checks,
  read-only opening of nonexistent databases, safe public stale errors, and
  bounded retention tests. No independent review was represented as run;
- focused Ruff F checks for the backend and search tests passed; the broader
  contract-file check exposed two pre-existing out-of-scope F402 findings,
  while the two new shadowed names were repaired;
- plan-authority audit passed with zero findings; `git diff --check` passed;
- tests used temporary fixture databases and ephemeral test sockets only.
  No installed or development runtime was provisioned or operated.

Bounds and residual risks:

- one implementation attempt and one self-review/remediation pass used; no
  subagents or retry loop;
- snapshots are process-local, expire at 900 seconds without refresh, and use
  FIFO bounds of 16 heads / 32 MiB of serialized hits. These are serialized-data
  bounds, not a measured process-memory ceiling. More than 10,000 filtered
  candidate revisions fails closed and requires narrower filters;
- process restart/eviction deliberately loses pagination continuity. This is
  an explicit Packet 4 retention/documentation consideration, not a durable
  cursor promise; public guidance now states it;
- Packet 3 semantic/RRF, response budgets, and 10,000-post performance evidence
  remain unimplemented; no performance claim is made from the retention limit;
- topics/causes absent from retained source evidence are not inferred;
- generated catalog/runtime manifest must be reconciled and the complete
  joined suite rerun before the coordinator can claim integration acceptance.

Subagent status and reconciliation: `/root/wi002_search_packet2` completed the
bounded source work directly; no children. Requested model/effort and unknown
effective runtime configuration remain as recorded in C01.

Graphiti write status: `not_written`; prior bounded discovery had no useful
current Packet 2 recall, so this continuation used verified repo authorities.
Provider/memory writes remain outside this assignment.

Next action: coordinator reviews this source checkpoint, combines the lanes,
regenerates the catalog and runtime manifest once, verifies full joined
validation, and handles the owned-fork PR/integration. Do not begin Packet 3.

## Stop Rules

- stop before shared WI-003 answer changes, semantic ranking, runtime, provider,
  schedule, issue, release, staging, or production effects;
- stop and notify the coordinator before editing coordinator-owned projections,
  generated catalogs, or a conflicting shared schema.
