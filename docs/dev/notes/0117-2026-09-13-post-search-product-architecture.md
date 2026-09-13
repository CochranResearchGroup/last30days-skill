# Post Search Product Architecture

Date: 2026-09-13
Work item: WI-002
Plan: 0076
Repository checkpoint: `9ff37a72a813d4ce8140647079900d0186c08f9e`
Investigation mode: stable local Git repository, architecture and mixed
code/docs synthesis, hybrid structure-first retrieval

## Decision

Add a distinct, cache-only post-search contract at `POST /v1/posts/search` and
an agent-facing `search_posts` MCP tool. Preserve `/v1/query` unchanged until
WI-003 deliberately composes evidence retrieval and question answering.

The new surface searches the durable post corpus across both current storage
families:

- `documents` / immutable `document_versions`, including topic and collection
  sightings and the existing lexical/semantic index;
- `service_source_records` / immutable `service_source_versions`, including
  tick sightings, lane targets, and retained promoted/superseded query entries.

Normalize both through one `PostSearchBackend`, apply access and user filters
before ranking, deduplicate on source-native identity, and produce one stable
cursor bound to immutable search heads and a request fingerprint.

## Why A Separate Surface

The current `/v1/query` contract serves a different promise: it chooses either
the promoted terminal tick snapshot or the legacy retrieval head according to
head recency, can schedule acquisition under non-cache policies, and may return
an extractive brief. Extending it in place would combine corpus browsing,
refresh policy, answer preparation, and backward-compatibility changes.

`/v1/posts/search` is always cache-only and post-oriented. It creates a stable
foundation that WI-003 can consume without changing existing query behavior or
accidentally acquiring from providers.

## Current Evidence

- Live installed service `0.3.116`, database schema 17, and MCP adapter `4.0.4`
  are compatible and ready. Service-info reports 167 indexed documents with
  167 local-hash embeddings across five sources.
- A cache-only live query returned evidence from promoted tick snapshot
  `tick-snapshot-948d2a9abf16af93bf70b8f50be752b7` and always returned
  `next_cursor: null`.
- `CacheQueryApplication.query` selects the promoted tick snapshot when it is
  not older than the legacy retrieval head; the two corpora are alternatives,
  not a federated result set.
- `QueryRequest` accepts only sources, topic IDs, and publication bounds.
  `CacheQueryApplication.query` passes only sources and publication bounds to
  `TickSnapshotPublisher.query`; topic IDs are not applied on that path.
- `TickSnapshotPublisher.query` filters access partition, source, and published
  time before scoring. It ranks lexical token overlap and semantic cosine
  candidates with deterministic RRF, then truncates to a limit without a
  cursor.
- The legacy schema already retains author, source-native identity, canonical
  URL, immutable versions, topic IDs, collection spec/run IDs, and observation
  times. The tick schema retains the equivalent source identity, immutable
  versions and sightings, tick schedule, target, lane, and observation facts.

Graphiti discovery in `last30days_skill_main` recovered the prior decisions
that ordinary query uses the promoted tick head when present and that
collection specs already model feed, topic, poster, channel, account, and
profile surfaces. Current code and live service readback verified those leads.

## Contract V1

### Request

- `schema_version`, `request_id`, and authorized `profile_id`;
- optional non-empty `query`;
- `filters` with exact allowed fields:
  - `sources`;
  - `authors`;
  - namespaced `collection_refs`;
  - `topic_ids`;
  - `published_after` / `published_before`;
  - `observed_after` / `observed_before`;
- `revision_mode`: `current` by default or explicit `all`;
- `sort`: `relevance` by default, with `published_desc` and `observed_desc`;
- `page_size` from 1 through 100;
- optional opaque `cursor`.

At least one of `query` or a narrowing filter is required. Filter-only browse
is valid. Unknown fields, invalid ranges, empty access partitions, and cursor
request mismatches fail closed.

### Response

- immutable `search_head_id`, normalized request ID, generated time, and
  applied filter/revision/sort metadata;
- ordered post hits with stable `post_id`, `revision_id`, source-native ID,
  canonical URL, title, author, bounded text, published and observed times,
  access partition, matching channels, namespaced collection causes, topic
  IDs, score components, and exact evidence/provenance references;
- `returned`, `truncated`, and an opaque `next_cursor` or null;
- corpus coverage metadata that distinguishes legacy index head, tick snapshot
  coverage, unavailable fields, and known source gaps.

An opaque cursor contains no authority. It binds the request fingerprint,
authorized partition set, immutable component-head IDs, and the last stable
sort tuple. Replay with a changed request or wider partition set fails. If a
retained immutable head cannot be read, return `cursor_stale`; never silently
continue against a different corpus.

## Identity, Filtering, And Ranking

- Normalize post identity as `(source, source_native_id,
  access_partition_id)`, with canonical URL fallback only when a source-native
  ID is absent. Preserve every immutable revision separately.
- In `current` mode, select the current version from each storage family before
  candidate generation. In `all` mode, return revisions explicitly and never
  collapse distinct content hashes.
- Map legacy collection spec/run sightings and tick schedule/target sightings
  into typed, namespaced `collection_refs`; do not invent one shared provider
  identifier.
- Apply access partition and every user filter in SQL before lexical or
  semantic candidate ranking.
- Fuse lexical and semantic ranks with deterministic RRF. Do not add hidden
  recency weight to relevance; recency is an explicit sort mode. Use stable
  post/revision IDs as final tie-breakers.
- Over-fetch each adapter within a fixed candidate ceiling, normalize and
  deduplicate, then paginate the fused ordered set. Record component ranks and
  matching channels so ranking remains explainable.

## Vertical Delivery Packets

1. Tracer bullet: contract/catalog and cursor codec; lexical current-revision
   adapters for both storage families; source, access, and publication filters;
   `/v1/posts/search`; `search_posts`; one end-to-end provider-free fixture.
2. Complete filtering and identity: author, topic, namespaced collection,
   observed-time, filter-only browse, revision mode, deduplication, and stable
   multi-page traversal.
3. Retrieval quality: semantic candidates, deterministic RRF, ranking
   explanations, response budgets, coverage diagnostics, and a 10,000-post
   local performance fixture with an explicit measured budget.
4. Product closeout: slash-command guidance, service/MCP compatibility
   fixtures, fresh-client local runtime smoke, release/version changes, and a
   restart-safe handoff to WI-003. Staging and production remain separately
   gated behind WI-001 and release authority.

Each packet crosses contract, storage, application, HTTP, MCP, and tests where
needed; no packet may finish as an engine flag or internal repository class
that the slash-command/agent surface cannot use.

## Expected Write Surfaces

- service contracts and generated catalog/digest artifacts;
- search backend/application modules and SQLite migration only if the tracer
  proves an additive index is required;
- HTTP routing and MCP Go adapter/tool tests;
- service retrieval, app, HTTP, contract, and cursor tests;
- `SKILL.md`, configuration only if a user-facing knob is introduced,
  changelog/release metadata, plan, roadmap, runbook, and work-item state.

The lane owner must consult CodeGraph impact before editing these shared
surfaces and must coordinate any contract-schema change with WI-003.

## Acceptance Boundary

Provider-free acceptance requires:

- both storage families appear in one query and access partitions never widen;
- every requested filter is enforced before ranking on both adapters, with
  missing filter values excluding the item; unrequested-field coverage gaps
  remain explicit without fabricated values;
- two-page traversal is complete, deterministic, duplicate-free, and pinned to
  immutable heads while concurrent publication occurs;
- current/all revision behavior and cross-store identity collisions are tested;
- lexical and semantic ranking explanations reproduce from fixture data;
- HTTP and fresh MCP clients return the same bounded contract;
- no search call enqueues acquisition, touches a browser/provider, changes a
  schedule, or mutates production.

Installed development, staging, and production claims require their own
current runtime identity and deployment receipts. This architecture packet
does not authorize those effects.

## Open Questions For The Lane Owner

- Measure whether adapter-level federation meets the frozen 10,000-post local
  budget before adding a materialized unified index.
- Decide the exact latency/memory budget from a baseline on the lane runtime;
  do not invent a threshold before measurement.
- Confirm how long immutable component heads are retained before declaring a
  cursor retention guarantee.

## Skill Friction

The shared `codebase-investigator` skill references two example files under
`../.system/corpus-host-shared/` that are absent from the installed skill tree.
The required core environment, tool, runbook, retrieval, output, and plan
references were available; the missing optional examples did not limit this
investigation.

## State Location

This note and its machine-readable companion are durable in the stable
repository. No bundle or snapshot is needed.
