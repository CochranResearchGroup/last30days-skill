# last30days Product Roadmap

Authority: this file is the canonical product direction, priority map, and lane
catalog. Detailed execution lives under `docs/dev/plans/`; dated work and
decisions live in `RUNBOOK.md`.

## Product Objective

Build a user-scoped, continuously hydrated intelligence service that acquires
posts and profile pages from authenticated and public sources, preserves their
provenance and temporal history, resolves people, organizations, topics, and
events, and answers coherent citation-ready questions without exposing browser
or scraping mechanics to normal agents.

## Priority And Dependency Order

```text
P01 Temporal Corpus Foundation
 ├──> P02 Recurring Acquisition And Coverage
 ├──> P03 Profile And Identity Acquisition
 └──> P04 Temporal Retrieval And GraphRAG
          └──> P05 Agent-Facing Intelligence Product
```

P03 discovery and bounded source experiments may proceed alongside P01, but
large recurring hydration must not outrun immutable revision, provenance,
coverage, and access-control foundations.

## P00 | Productized Content Service MVP

State: CLOSED

Objective: establish the user-scoped cache-first service, durable acquisition
supervisor, semantic and evidence-backed graph indexes, thin MCP surface, and
authenticated social-source hydration.

Current State:

- Plans 0007, 0008, and 0009 are closed with live service, semantic index,
  graph enrichment, and five-source hydration evidence.
- The service is a credible MVP authority, but its catalog remains
  document-centered and does not yet preserve full temporal revisions,
  collection coverage, profile histories, or bitemporal claims.

Plans:

- `docs/dev/plans/0001-2026-07-15-facebook-scraper-implementation.md`
- `docs/dev/plans/0003-2026-07-19-x-agent-browser-scraper.md`
- `docs/dev/plans/0004-2026-07-20-youtube-stealth-browser-transcript-fallback.md`
- `docs/dev/plans/0005-2026-07-20-youtube-media-capability-integration.md`
- `docs/dev/plans/0006-2026-07-23-agent-browser-expert-shared-profile-routing.md`
- `docs/dev/plans/0007-2026-07-24-productized-intelligence-service-mvp.md`
- `docs/dev/plans/0008-2026-07-25-content-service-hydration-readiness.md`
- `docs/dev/plans/0009-2026-07-25-social-source-hydration-recovery.md`

## P01 | Temporal Corpus Foundation

State: PLANNED

Objective: make the corpus safe for long-running hydration by separating stable
content identity from immutable revisions and by preserving what happened,
when it was true, when it was observed, and which collection caused it.

Goal Seeds:

- stable documents plus immutable `document_versions`;
- acquisition, sighting, topic, selector, and collection-spec provenance;
- bitemporal valid-time and system-time semantics;
- reversible entity aliases, merges, splits, and identity assertions;
- evidence-backed claims, claim supersession, conflicts, and event records;
- access partitions for public and authenticated source material;
- migration and replay proof for the existing corpus.

Acceptance Seeds:

- changed posts never overwrite historical text or metadata;
- every derived entity, claim, event, and relationship resolves to exact
  evidence in an immutable document version;
- the service distinguishes unknown, not observed, and observed absent;
- existing content remains queryable through a reversible migration.

Next Plan: create a bounded schema-and-migration plan before enabling broad
recurring hydration.

## P02 | Recurring Acquisition And Coverage

State: PLANNED

Objective: run governed timers that collect bounded recent feed items and
optional topic, poster, channel, or account targets without losing cursor,
coverage, budget, or source-health history.

Goal Seeds:

- typed collection specifications rather than ad hoc cron commands;
- per-source selectors for feeds, topics, posters, channels, profiles, and
  bounded item/time limits;
- durable cursors, watermarks, coverage intervals, gaps, retries, budgets, and
  backoff;
- deduplicated timer and manual-refresh work through the existing supervisor;
- source/profile leases for authenticated browser work;
- retention, redaction, and collection pause/resume controls;
- yield and coverage observability distinct from process health.

Acceptance Seeds:

- each timer run proves which surface and interval it attempted to cover;
- repeated runs are idempotent while edits and new observations remain
  historically visible;
- a normal query never operates a browser or waits on acquisition mechanics;
- authenticated collection cannot cross its configured profile or data
  partition.

Dependencies: P01 foundations must cover the records emitted by timers.

## P03 | Profile And Identity Acquisition

State: OPEN

Objective: treat user, creator, company, channel, and organization profile
pages as first-class temporal evidence surfaces rather than incidental post
metadata.

Current State:

- Plan 0002 provides an open LinkedIn post-search lane and authenticated
  agent-browser substrate.
- Current adapters normalize posts, authors, and URLs, but do not maintain a
  durable profile snapshot/history model.
- LinkedIn profile pages are a priority because they expose employment,
  education, affiliation, headline, location, company, and identity evidence
  that may change independently of posts.

Goal Seeds:

- a source-neutral `profile_snapshot` acquisition contract;
- stable source-account and real-world-entity identity separation;
- section-level evidence and change history for LinkedIn people and company
  profiles;
- analogous channel/profile surfaces for YouTube, X, Facebook, Reddit, and
  future sources;
- explicit visibility, authorization, redaction, and retention metadata;
- profile-to-post, person-to-account, employment, affiliation, and
  organization relationships with evidence and temporal validity;
- conservative change detection that distinguishes page redesign or missing
  sections from actual real-world changes.

Acceptance Seeds:

- profile snapshots are versioned and cite the exact authenticated/public
  acquisition that produced them;
- profile changes produce temporal claims without silently invalidating prior
  history;
- users can ask who a person was affiliated with at a given time and receive
  evidence plus uncertainty;
- profile collection does not scrape messages, connections, invitations, or
  other out-of-scope private surfaces.

Active Plan:

- `docs/dev/plans/0002-2026-07-15-linkedin-agent-browser-scraper.md`
  remains the post-search precursor; a successor profile-acquisition plan is
  required before profile implementation begins.

Dependencies: share P01 identity and temporal evidence contracts.

## P04 | Temporal Retrieval And GraphRAG

State: PLANNED

Objective: answer topic-, person-, organization-, and event-centered questions
over a growing corpus with explicit temporal semantics and citation-ready
evidence.

Goal Seeds:

- deterministic query classification for entity, event, timeline, trend,
  comparison, `as_of`, `during`, and `known_as_of` questions;
- lexical, semantic, entity, event, temporal, and bounded graph candidate
  generation;
- identity resolution and ambiguity-preserving query behavior;
- bitemporal claim filtering, conflict surfacing, and evidence reconciliation;
- time-bucketed trend features, event timelines, source diversity, and
  repeated-sighting signals;
- SQLite remains authoritative; Graphiti/FalkorDB receives a rebuildable,
  access-partitioned temporal projection through a durable outbox;
- LightRAG or global community summaries remain benchmark-gated derived
  alternatives, not unreviewed authorities.

Acceptance Seeds:

- answers distinguish event time, publication time, observation time, and
  knowledge-as-of time;
- every factual statement resolves to one or more immutable evidence spans;
- contradictory claims remain inspectable;
- Graphiti loss or degradation cannot destroy corpus authority or prevent
  deterministic evidence retrieval.

Dependencies: P01 is required; P02 and P03 progressively improve coverage and
identity quality.

## P05 | Agent-Facing Intelligence Product

State: PLANNED

Objective: let agents discover, query, monitor, and evaluate the intelligence
service through compact MCP and skill contracts without browser or scraper
mechanics entering ordinary context.

Goal Seeds:

- compact service discovery for temporal, profile, coverage, and graph
  capabilities;
- evidence, timeline, entity dossier, event dossier, trend, and bounded brief
  response modes;
- explicit freshness, coverage, index version, access partition, and
  uncertainty in every response;
- deterministic evaluation suites for temporal resolution, entity ambiguity,
  event reconstruction, graph contribution, and citation completeness;
- bounded stochastic enrichment and maintenance loops with durable receipts.

Dependencies: grows incrementally with P01-P04 and must not bypass their
authority or access-control contracts.

## Goal-Compatible Plan Conversion

Before moving a lane from `PLANNED` to `OPEN`, create or identify a plan that:

1. preserves the lane objective as its stable goal contract;
2. names one bounded outcome and explicit non-goals;
3. records current evidence, dependencies, gates, and owned write surfaces;
4. splits deterministic control from stochastic proposals;
5. defines measurable acceptance criteria and rollback/replay proof;
6. sets work-unit, review, hardening, and checkpoint bounds;
7. names parallelizable packets and the critical-path owner;
8. records Graphiti and runbook checkpoint requirements;
9. stops when acceptance is met, a hard gate is reached, or remaining work is
   unbounded polish.
