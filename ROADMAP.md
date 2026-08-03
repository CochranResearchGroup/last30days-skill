# last30days Product Roadmap

Authority: this file is the canonical product direction, priority map, and lane
catalog. Detailed execution lives under `docs/dev/plans/`; dated work and
decisions live in `RUNBOOK.md`.

## Product Objective

Build `last30days` as a user-scoped, independently installed intelligence
software product. Its durable service, corpus, schedulers, acquisition
adapters, App Intelligence supervisor, and MCP server are the product. Agent
Skills are optional clients that help agents discover, query, monitor, and
administer the service; they are not the workflow authority or primary
runtime.

The service continuously acquires posts and profile pages from authenticated
and public sources, preserves provenance and temporal history, resolves people,
organizations, topics, and events, and answers citation-ready questions
without exposing browser or scraping mechanics to ordinary agents.
Deterministic supervisors own collection, state, budgets, validation,
publication, and replay. Bounded App Intelligence workers assess evidence,
propose identity and claim associations, evaluate retrieval, and diagnose or
repair adapters.

## Product Boundary Decision | 2026-07-29

The repository began as an installable Skill with supporting scripts. That
packaging is now a compatibility surface around an emerging software product,
not the target architecture.

- **Product:** the independently versioned last30 Intelligence Service and its
  first-class MCP contract.
- **Deterministic authority:** service lifecycle, source configuration,
  schedules, jobs, leases, cursors, budgets, retries, access partitions,
  immutable evidence, indexes, validation, publication, and replay.
- **Stochastic assistance:** bounded schema-validated App Intelligence
  assessment, identity proposals, retrieval evaluation, and adapter
  diagnosis/repair under host policy.
- **Agent clients:** optional Skills for query/synthesis, monitoring,
  administration, and bounded maintenance.
- **Compatibility path:** the request-scoped Engine and current Skill package
  remain portable operator/debug fallbacks during migration.

Ordinary querying agents should ask what the service knows, what changed, how
fresh and complete coverage is, and which capabilities are degraded. They
should not choose scraper backends, manage browser sessions, locate cookies or
tabs, coordinate retries, or rebuild indexes.

## Priority And Dependency Order

```text
P01 Temporal Corpus Foundation
 ├──> P02 Recurring Acquisition And Coverage
 ├──> P03 Profile And Identity Acquisition
 └──> P04 Temporal Retrieval And GraphRAG
          └──> P05 Agent-Facing Intelligence Product
P06 App Intelligence Control Plane
 ├──> supports P02 intake assessment
 ├──> supports P03 identity resolution
 ├──> supports P04 enrichment and evaluation
 └──> supports bounded adapter maintenance across all lanes

P07 Service-First Software Productization
  ├──> establishes independent service package and lifecycle
  ├──> makes MCP the primary agent/application contract
  ├──> composes P01-P06 behind deterministic software authority
  └──> reduces Skills to optional least-privilege clients
```

P03 discovery and bounded source experiments may proceed alongside P01, but
large recurring hydration must not outrun immutable revision, provenance,
coverage, and access-control foundations.

## Integrated Foundation Milestone | 2026-07-25

Plans 0010 and 0011 are closed. The installed service is ready at version
0.2.7/schema 12 with immutable temporal evidence, governed collection,
source-neutral profiles, bitemporal retrieval, durable Graphiti projection,
ten compact MCP tools, and discoverable bounded App Intelligence contracts.
Bounded Facebook, X, LinkedIn post, and LinkedIn company-profile canaries
published through retained authenticated Guacamole/RDP browsers.

This milestone closes the integrated implementation plan, not the product
roadmap. P01-P06 remain roadmap lanes. Plan 0014 is now the actionable open
packet for public-source timer durability; Plans 0015 and 0016 follow for
temporal/GraphRAG resilience and App Intelligence contract acceptance. No
recurring authenticated timer was enabled by closeout.

## Successor Implementation Queue | 2026-07-26 Review

The roadmap review converts the post-reboot handoff priorities into bounded
successor plans without reopening Plans 0010 or 0011:

1. `docs/dev/plans/0012-2026-07-26-post-reboot-social-route-canary.md`
   is now closed successfully. Agent-browser P78/Plan 0078 restored durable
   Guacamole fixtures, two accessible route displays, and a successful
   recurring interlock. Agent-browser P81 then repaired retained route-state
   projection at commit `ffda60dd`: stable route A now resolves to
   `guacamole:1` on `:11`, and a no-launch normal route-open proof selects that
   canonical binding. The authorized fresh Plan 0012 attempt then proved an
   operator-visible browser on `guacamole:1`/`:11`, but the post-open inventory
   contained only the X tab. The packet stopped before DOM probes because the
   required Facebook and LinkedIn tabs were not restored, and no canary or
   reserved request ID was consumed. Plan Revision 2 now authorizes the bounded
   workaround: create exactly one missing Facebook tab and one missing
   LinkedIn tab on the still-ready canonical browser, then continue the
   signal-only probes and serialized canaries without another browser, profile,
   or route launch. That tab repair succeeded. Revision 3 replaces the
   full-page-text checkpoint classifier after it returned the contradictory X
   result `authenticated: true` and `checkpoint: true`; resumed probes now use
   only source-specific URL and DOM-control signals. All three corrected probes
   passed, and the serialized X, Facebook, and LinkedIn canaries published 2,
   3, and 3 durable items.
2. `docs/dev/plans/0013-2026-07-26-youtube-transcript-media-acceptance.md`
   is the planned YouTube transcript, bounded media, downstream handoff, and
   cleanup acceptance packet.
3. `docs/dev/plans/0014-2026-07-26-recurring-collection-timer-durability.md`
   is the planned two-interval public-source timer/restart/pause proof.
4. `docs/dev/plans/0015-2026-07-26-temporal-retrieval-graphrag-resilience.md`
   is closed successfully: fresh-client cache-only temporal/profile access,
   idempotent replay of the sole projection, and isolated provider-unavailable
   SQLite fallback passed without access widening or acquisition enqueue.
5. `docs/dev/plans/0016-2026-07-26-app-intelligence-contract-acceptance.md`
   is the planned accepted/rejected envelope and deterministic replay packet.
6. `docs/dev/plans/0017-2026-07-26-canonical-profile-selection-regression.md`
   is the planned identity-first, ambiguity-safe profile-selection regression
   packet.
7. `docs/dev/plans/0018-2026-07-29-service-first-software-product-transition.md`
   is the planned product transition from Skill-first packaging to independent
   intelligence software with a first-class MCP contract and optional client
   Skills.

The 2026-07-29 architecture direction makes Plan 0018 the governing successor
after Plan 0014 reaches a terminal timer result. Plan 0014 is `CLOSED` at its
typed restart-bound blocker after repairing stale due replay and missing
per-spec backpressure. Plan 0018 is now `OPEN` with the bounded
service-package/lifecycle and MCP-boundary packet that makes later acceptance
work service-product validation rather than Skill features. Plans 0013 and
0017 remain planned and outside this transition critical path. Plan 0015 is
now closed under Plan 0018; Plan 0016 is the next transition packet.

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

State: CLOSED

Objective: make the corpus safe for long-running hydration by separating stable
content identity from immutable revisions and by preserving what happened,
when it was true, when it was observed, and which collection caused it.

Current State:

- Plan 0011 Packets 1 through 5 are complete at commits `f14b0fa`,
  `0454e5a`, `4ae5095`, `22c8db1`, and `6c6e751`; Packet 6 source is complete
  at `0e7938a`.
- Additive schema version 12 now establishes immutable document versions,
  append-or-reuse publication, version-scoped evidence and enrichment,
  access partitions, governed recurring collection, post-publication
  assessment, authoritative index snapshots, evidence-backed temporal
  claims/events, recorded retrieval evaluations, and durable graph projection
  receipts.
- The installed service runs version 0.2.7 on schema 12, a fresh MCP client
  discovers ten compact tools, and concrete Graphiti outbox delivery passed.
- X profile authentication is restored. The first canary retry exposed that
  `force_refresh` coalesced onto the retained `awaiting_operator` job without a
  public resume path. Version 0.2.1 installed that guarded transition and
  performed attempt two, which exposed a second deterministic defect: the X
  auth probe classified an authenticated retained tab's stalled loading DOM as
  `auth_required` without reloading it. Version 0.2.2 installed one bounded
  reload for only an ambiguous DOM, but the final bounded X canary still ended
  `awaiting_operator/auth_required`; its retained tab read back as
  `https://x.com/` with title `x.com/home`.
- New operator evidence proved that the service-owned X tile was a broken CDP
  screencast rather than a Guacamole/RDP browser. Version 0.2.3 corrects the
  deterministic acquisition contract: X uses agent-browser's route-bound
  remote-view path, defaults to `rdp_gateway`, and requires operator-visible
  readiness. The stale route was released through the supported MCP control
  plane and the X workspace now has route/browser/display agreement on
  Guacamole route `guacamole:4`.
- Service version 0.2.6 contains the shared social-display repair plus stable
  acquisition failure evidence and typed adapter-repair gating; the repair
  contract commit is pushed at `c52918e`, and the current X login detector is
  pushed at `ad1abd4`. The prior route-bound X repair is pushed at `b76bb28`
  and its canonical checkpoint at `e685844`.
- A prior live X probe on the exact retained Guacamole/RDP browser rendered
  the current root sign-in surface and exposed a legacy-selector defect.
  Version 0.2.6 added a root-route plus multi-signal signed-out detector.
  After operator recovery and refresh, agent-browser target readiness now
  records a fresh authenticated retained-browser probe with four
  quality-gated posts. The content-service X canary remains pending.
- The first bounded live recurring-collection acceptance spec preserved two
  typed fail-closed outcomes (`budget_exhausted`, then
  `network_budget_exhausted`) and was paused at immutable spec revision 3 after
  reaching the two-attempt plan bound. Successor revision 4 raised only the
  measured network-request cap and published interval jobs
  `f36014c9-8749-41af-b483-a950099b3db7` and
  `15719900-3b9d-46ec-a8f7-6ef9cf68fecb` on consecutive minute boundaries,
  with a service restart between them. Revision 5 is paused after the proof,
  establishing timer execution, durable deduplication, and restart recovery
  without leaving the acceptance cadence active.
- Fresh retained-browser DOM probes independently proved Facebook and LinkedIn
  authentication is usable. The first Facebook canary then failed twice with
  `agent_browser_error` before acquisition because the adapter requested a
  private virtual display while the authenticated retained Guacamole browser
  intentionally uses `shared_display`. The adapter now passes the complete
  Guacamole/RDP posture into access planning and requests `shared_display` for
  X, Facebook, and LinkedIn post/profile work. A no-navigation live acquisition
  probe reused `session:last30days-facebook`, and the repaired source is synced
  into the active user-scoped install. The single post-repair Facebook job
  `ecea393f-c445-461d-9528-99c2107190f1` then published three items in one
  attempt. The serialized LinkedIn post canary
  `91b55c9f-3827-4046-9c87-0df99ec54f40` failed after its two internal attempts
  with `agent_browser_error`. A subsequent read-only auth probe succeeded on
  the retained feed tab, but the preserved failure envelopes lack the stage
  evidence needed to attribute a code defect. Version 0.2.5 therefore adds
  stable failure signatures, bounded stage/operation evidence, and
  deterministic App Intelligence triage contracts; the preserved outcome is
  classified `insufficient_evidence -> observe`, and the LinkedIn profile
  canary remains withheld.
- The authorized LinkedIn version 0.2.6 post canary later failed twice at
  `workspace_acquisition` with one stable signature. Its contemporaneous
  broker record planned a new CDP browser rather than the retained shared RDP
  browser. Agent-browser commit `3c08b9b0` repaired daemon-session workspace
  selection and restored the Guacamole route; the same current no-launch
  LinkedIn plan now returns `tab_new` on `session:last30days-facebook`.
- A post-repair retry exposed the remaining user-scoped override:
  `LAST30DAYS_LINKEDIN_VIEW_PROVIDER=cdp_screencast`. It is now
  `rdp_gateway`, loaded by the restarted service, and installed
  no-navigation acquisition proves one-read retained-browser reuse. The
  LinkedIn lane is stopped after the repeated stable failure pending a new
  plan decision.
- The single authorized X content-service canary then failed twice at
  `adapter_result` with one stable signature. A bounded lower-level probe
  proved acquisition selects the healthy retained RDP browser, but the next
  registered-session client command is not attached to it and incorrectly
  attempts to auto-launch the unrelated default profile. Explicit attachment
  to the retained CDP endpoint lists the authenticated X tab. Agent-browser
  commit `68bd8173` now reconnects ordinary registered-session commands to
  their live retained browser, and installed no-navigation validation reports
  X authenticated at `https://x.com/home` while preserving the Guacamole/RDP
  browser. The successor X job
  `b079e12b-0212-4848-8daf-ac9e55fd201a` then published seven items on attempt
  1 through acquisition `work-387f90eb5f74a6d7c7f1c9fe471f9916`. X post
  acceptance now passes. The successor LinkedIn job
  `53623222-316f-404c-886a-959a9abef8fb` then published two items on its second
  internal attempt; the first attempt reached content and missed only its
  quality gate. LinkedIn post acceptance now passes. The exact OpenAI company
  profile run `collection-run-8b4ff51fb0ccabd7b5819dd9e22f4e1f` then
  published one immutable organization snapshot on attempt 1 with conservative
  section-presence semantics. Its collection spec remains timer-disabled.
  Packets 6 and 7 are complete, and Plan 0011 is closed.

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

Active Plan:

- `docs/dev/plans/0011-2026-07-25-integrated-temporal-intelligence-service.md`
  is the closed integrated P01-P06 foundation campaign. Future P01 work needs
  a successor bounded plan rather than reopening Plan 0011.

## P02 | Recurring Acquisition And Coverage

State: PLANNED

Objective: run governed timers that collect bounded recent feed items and
optional topic, poster, channel, or account targets without losing cursor,
coverage, budget, or source-health history.

Current State:

- Plan 0011 Packet 3 is complete at commit `4ae5095`, and installed Packet 6
  acceptance proved timer yield, interval deduplication, and restart recovery.
- Schema version 10 now provides immutable collection-spec revisions, durable
  schedules/runs/attempts/cursors/coverage/gaps, source health and yield,
  authenticated profile leases, and raw-publication-first bounded
  `content_assessment`.
- Collection runs freeze their originating spec revision and enforce
  per-spec item, time, network, budget, retention, redaction, and access
  policy through the deterministic host.
- The bounded public acceptance timer remains paused after its proof.
  Recurring authenticated timers were not enabled; broad hydration is the
  next operational expansion and must proceed spec-by-spec under explicit
  budgets and source/profile leases.
- The first 2026-07-29 Plan 0014 attempt proved stale due-boundary replay and
  was repaired. Revision 2 then proved that a slow active interval could admit
  later due intervals for the same spec. The hard stop fired at three
  revision-8 runs, revision 9 is disabled, and the working tree now suppresses
  timer admission while any run for that spec remains non-terminal.

Goal Seeds:

- typed collection specifications rather than ad hoc cron commands;
- per-source selectors for feeds, topics, posters, channels, profiles, and
  bounded item/time limits;
- durable cursors, watermarks, coverage intervals, gaps, retries, budgets, and
  backoff;
- deduplicated timer and manual-refresh work through the existing supervisor;
- source/profile leases for authenticated browser work;
- retention, redaction, and collection pause/resume controls;
- durable post-publication assessment batches that classify content type,
  novelty, relevance, likely entities, claims, events, and profile changes;
- deterministic cheap-path filtering before model work so every fetched item
  is preserved, but only bounded uncertain or valuable batches consume App
  Intelligence budgets;
- schema-validated assessment proposals that cannot directly mutate collection
  state, corpus authority, ranking weights, or index publication;
- yield and coverage observability distinct from process health.

Acceptance Seeds:

- each timer run proves which surface and interval it attempted to cover;
- repeated runs are idempotent while edits and new observations remain
  historically visible;
- acquisition success is independent of stochastic assessment success; failed
  assessment remains replayable and retryable without refetching;
- a normal query never operates a browser or waits on acquisition mechanics;
- authenticated collection cannot cross its configured profile or data
  partition.

Dependencies: P01 foundations must cover the records emitted by timers.

Active Plan:

- `docs/dev/plans/0011-2026-07-25-integrated-temporal-intelligence-service.md`
  is the closed foundation authority. A successor plan must own broad
  hydration enablement and its coverage/yield acceptance.
- `docs/dev/plans/0013-2026-07-26-youtube-transcript-media-acceptance.md`
  is the planned current-yield acceptance packet for YouTube transcript and
  bounded media handling.
- `docs/dev/plans/0014-2026-07-26-recurring-collection-timer-durability.md`
  is closed at its typed restart-bound blocker. Its scheduler repairs are
  pushed, revision 9 is disabled, and a future timer proof is subordinate to
  Plan 0018's independent lifecycle work.

## P03 | Profile And Identity Acquisition

State: PLANNED

Objective: treat user, creator, company, channel, and organization profile
pages as first-class temporal evidence surfaces rather than incidental post
metadata.

Current State:

- Plan 0011 Packet 4 is source-complete at commit `22c8db1`.
- Schema version 11 adds immutable profile sightings and sections with exact
  evidence, visibility/presence state, conservative change detection,
  deterministic cross-service candidates, and durable terminal identity
  outcomes.
- An exact-URL LinkedIn people/company adapter now uses the retained
  authenticated agent-browser profile and stops on auth/checkpoint state
  without touching messages, connections, invitations, or unrelated private
  surfaces.
- Plan 0010 profile-change and identity proposals are schema bounded and may
  only act on host-created evidence and candidate IDs.
- A validated `same_entity` outcome now promotes a reversible,
  evidence-linked identity assertion; claim/event promotion and temporal
  retrieval preserve ambiguity and access partitions.
- The exact OpenAI LinkedIn company-profile canary published one immutable
  organization snapshot with one evidenced visible section and four
  conservative `not_observed` sections. Its collection spec remains disabled.
- Plan 0012 received explicit execution authorization on 2026-07-27. Read-only
  preflight reconfirmed the canonical `last30days-facebook` profile for X,
  Facebook, and LinkedIn, while the single permitted route open failed at
  `service_remote_view_route_preflight` because no display allocation or
  available route-pool entry existed. No browser, DOM probe, acquisition job,
  or authenticated timer was created.
- Agent-browser P78/Plan 0078 subsequently restored and hardened the route
  substrate. A new explicitly authorized Plan 0012 attempt on 2026-07-28
  proved both route displays accessible and the doctor ready at
  `guacamole:1`/`:11`, but normal route-open selected retained legacy
  `guacamole:4`/`:10` and failed display access before browser launch. Lease
  rollback completed; no DOM probe, acquisition job, or timer mutation ran.
- Agent-browser P81 repaired retained route selection so the canonical browser
  opened on `guacamole:1`/`:11`. Plan 0012 then restored the missing Facebook
  and LinkedIn tabs in that same browser, replaced a full-page-text checkpoint
  false positive with structural URL and DOM signals, and published serialized
  X, Facebook, and LinkedIn canaries with 2, 3, and 3 durable items. The
  authenticated timer remains disabled.

Goal Seeds:

- a source-neutral `profile_snapshot` acquisition contract;
- stable source-account and real-world-entity identity separation;
- deterministic identity candidate generation from canonical profile URLs,
  declared links, official domains, names, handles, and existing aliases;
- a bounded App Intelligence `identity_resolution` proposal contract supporting
  `same_entity`, `different_entity`, `ambiguous`, and `insufficient_evidence`
  outcomes;
- cross-service account-to-person and account-to-organization assertions that
  retain all supporting and conflicting evidence instead of silently merging
  records;
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
- ambiguous handle or profile associations remain separate and reviewable;
- users can ask who a person was affiliated with at a given time and receive
  evidence plus uncertainty;
- profile collection does not scrape messages, connections, invitations, or
  other out-of-scope private surfaces.

Active Plan:

- `docs/dev/plans/0002-2026-07-15-linkedin-agent-browser-scraper.md`
  is closed as the historical post-search precursor.
- `docs/dev/plans/0011-2026-07-25-integrated-temporal-intelligence-service.md`
  is the closed profile/identity foundation authority.
- `docs/dev/plans/0012-2026-07-26-post-reboot-social-route-canary.md`
  is the closed serialized route/auth/acquisition acceptance plan with all
  three source canaries published.
- `docs/dev/plans/0017-2026-07-26-canonical-profile-selection-regression.md`
  is the planned identity-first selection and ambiguity regression packet.

Dependencies: share P01 identity and temporal evidence contracts.

## P04 | Temporal Retrieval And GraphRAG

State: PLANNED

Objective: answer topic-, person-, organization-, and event-centered questions
over a growing corpus with explicit temporal semantics and citation-ready
evidence.

Current State:

- Plan 0011 Packet 5 is source-complete at commit `6c6e751`.
- Schema version 12 adds evidence-backed bitemporal claim/event promotion,
  conflict retention, deterministic temporal query classification, independent
  valid-time and knowledge-time filtering, exact evidence closure, recorded
  retrieval cases/evaluations, and durable graph projection receipts.
- Lexical, semantic, and graph candidate selection is access-partitioned.
  SQLite-only evidence retrieval remains operational when graph delivery
  fails, and the projection can be rebuilt by replaying authoritative records.
- The concrete local Graphiti sink, compact MCP product contracts, installed
  schema-12 migration, and durable live projection canary passed at commit
  `0e7938a`; the current projection reports one published receipt with zero
  pending or failed records.
- Plan 0015 closed at commit `f16f527`: a fresh MCP temporal/profile case
  preserved access partitions and acquisition counts, the sole projection
  replay was idempotent, and an isolated unavailable-provider run preserved
  citation-ready SQLite retrieval while truthfully reporting degradation.

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

Active Plan:

- `docs/dev/plans/0011-2026-07-25-integrated-temporal-intelligence-service.md`
  is the closed temporal retrieval and GraphRAG foundation authority.
- `docs/dev/plans/0015-2026-07-26-temporal-retrieval-graphrag-resilience.md`
  is the closed cache-only retrieval, projection replay, and local-evidence
  fallback acceptance authority.

## P05 | Agent-Facing Intelligence Product

State: PLANNED

Objective: let agents discover, query, monitor, and evaluate the intelligence
service through compact MCP and skill contracts without browser or scraper
mechanics entering ordinary context.

Current State:

- Commit `0e7938a` exposes cache-only temporal queries, dossiers, timeline,
  trend, profile history, coverage, collection control, and maintenance status
  through a ten-tool MCP surface.
- The installed version 0.2.7 service derives authorized partitions from the
  caller profile and keeps prompts, raw model/provider events, browser
  mechanics, cookies, and credentials out of normal responses.
- Fresh installed-client discovery, representative public/profile calls,
  cache-only no-enqueue behavior, authenticated-source canaries, and integrated
  acceptance pass.
- Plan 0015 additionally proved the named-profile `as_of`/`known_as_of` case,
  exact profile evidence closure, no-enqueue behavior, and truthful
  SQLite-backed operation during graph-provider degradation.

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
- MCP discovery and operator diagnostics expose assessment, identity,
  evaluation, and repair readiness without returning prompts, raw model events,
  or browser mechanics to ordinary query clients.

Dependencies: grows incrementally with P01-P04 and must not bypass their
authority or access-control contracts.

Active Plan:

- `docs/dev/plans/0011-2026-07-25-integrated-temporal-intelligence-service.md`
  is the closed installed-MCP foundation and acceptance authority.
- `docs/dev/plans/0015-2026-07-26-temporal-retrieval-graphrag-resilience.md`
  is the closed fresh-client cache-only product acceptance proof.

## P06 | App Intelligence Control Plane

State: PLANNED

Objective: use App Intelligence as bounded stochastic labor behind the existing
host-owned service supervisor for incoming-data assessment, cross-service
identity resolution, retrieval evaluation, and adapter diagnosis and repair.

Current State:

- The four Plan 0010 joins are now attached behind deterministic corpus,
  collection, identity, retrieval-evaluation, and maintenance authority.
- Installed version 0.2.7 maintenance discovery exposes the canonical
  version-1 task registry, validator-enforced finite ranges, task state, and
  safe repair-policy gates without exposing prompts or provider events.
- The first X canary was correctly classified as an operator authentication
  gate and did not trigger automated repair. After the operator authenticated,
  attempt two exposed an adapter defect that deterministically confused X's
  stalled loading DOM with a signed-out state; the bounded maintenance response
  is a tested single reload-and-recheck, not an App Intelligence repair loop.
- Plan 0016 is closed: one bounded public-evidence assessment produced
  host-owned validation, promotion, and replay receipts; a forbidden browser
  field failed before persistence or stochastic execution; installed replay
  returned the same receipt IDs; and canonical authority hashes were
  unchanged.
- The accepted execution exposed a strict response-schema defect before model
  generation. Commit `bbff9f8` repairs the canonical schema and its regression
  coverage; packaging the fix into the next compatible service release is
  retained under P07 S07.

Current Substrate:

- `service_intelligence.py` already provides a durable intelligence ledger,
  schema-gated structured workers, model-call and cost bounds, replay
  artifacts, decisions, evaluations, approvals, Git worktree branches, and a
  bounded repair supervisor.
- Codex app-server readiness passed on 2026-07-25 with Codex CLI 0.145.0,
  stdio, Unix-socket, generated JSON Schema/TypeScript, and authenticated
  WebSocket capabilities. The first implementation remains local stdio JSONL.
- Existing enrichment and retrieval-evaluation leaves demonstrate the
  proposal-plus-validator pattern, but timer assessment and cross-service
  identity resolution do not yet have dedicated schemas or promotion policy.

Control-Plane Contract:

- The deterministic host owns phase, job and run state, input selection,
  evidence IDs, budgets, retries, allowed actions, branch policy, tests/evals,
  approvals, promotion, rollback, publication, and stop rules.
- App Intelligence workers return schema-valid proposals only. Model output
  never directly merges identities, changes canonical claims, operates a
  browser, publishes an index, edits the main worktree, restarts a service, or
  deploys a repair.
- Persist raw provider events separately from normalized supervisor events so
  runs remain auditable and protocol changes can be replayed.
- Every loop records input/output artifacts, provider and model configuration,
  event streams, validator results, decisions, cost reservations, evals,
  approvals, and terminal state.

Loop Seeds:

1. `content_assessment`
   - runs after raw acquisition and immutable publication;
   - accepts bounded document-version batches and exact evidence IDs;
   - proposes content type, novelty, relevance, entity mentions, claims,
     events, profile changes, and follow-up candidates;
   - uses deterministic filters first and does not require one model call per
     fetched item.
2. `identity_resolution`
   - receives deterministic candidate pairs or small candidate sets;
   - proposes person, organization, and source-account associations across
     services;
   - must return supporting evidence, conflicts, confidence, temporal scope,
     and an ambiguity-preserving action;
   - promotion thresholds and human-review gates remain host policy.
3. `adapter_diagnosis`
   - starts only after deterministic health logic groups repeated failures by a
     stable failure signature;
   - classifies code defects separately from authentication checkpoints, rate
     limits, access restrictions, site redesigns, and transient network faults;
   - never treats an operator-authentication requirement as a repairable code
     defect.
4. `adapter_repair`
   - uses persistent Codex app-server threads for bounded investigation,
     optional forks, rollback, streamed events, and structured decisions;
   - performs code changes only in isolated branches/worktrees and uses
     `codex exec` only for stateless leaf review or CI-style jobs;
   - selects a candidate through host-owned focused tests, contract tests,
     replay fixtures, security checks, and an explicitly leased live smoke when
     allowed;
   - requires the configured approval gate before integration, installed-copy
     replacement, service restart, or deployment.

Integration-Surface Seeds:

- Prefer direct structured API calls for high-volume non-repo classification
  and extraction leaves when they meet cost, privacy, and schema requirements.
- Prefer Codex app-server for persistent adapter maintenance requiring repo
  context, file edits, branching, steering, approvals, or rollback.
- Prefer `codex exec --json --output-schema` for isolated stateless leaf jobs
  whose complete argv, events, outputs, and exit status fit one ledger entry.
- Do not allow App Intelligence adapters to call one another directly; the
  host validates one adapter result before invoking another.

Acceptance Seeds:

- timers can publish useful raw evidence when all stochastic workers are
  disabled or degraded;
- every promoted assessment, identity assertion, claim, or event is
  evidence-linked, schema-valid, replayable, and attributable to a versioned
  worker configuration;
- ambiguous identities do not auto-merge and conflicting evidence remains
  visible;
- identical assessment inputs and host policy can replay the recorded decision
  path even when stochastic output itself is not seed-reproducible;
- adapter repair has explicit call, branch, rework, time, cost, write-scope,
  browser, approval, and deployment bounds;
- failed repair evaluation stops, rolls back, requests review, or records a
  verified blocker rather than opening an unbounded repair loop.

Dependencies: P06 reuses the P00 intelligence ledger and supervisor substrate.
Its assessment and identity schemas must align with P01 temporal evidence
authority before recurring P02/P03 hydration depends on them.

Active Plan:

- `docs/dev/plans/0010-2026-07-25-app-intelligence-task-contracts.md`
  is the closed P06 component contract plan.
- `docs/dev/plans/0011-2026-07-25-integrated-temporal-intelligence-service.md`
  is the closed integration authority for its four deterministic joins.
- `docs/dev/plans/0016-2026-07-26-app-intelligence-contract-acceptance.md`
  is the closed accepted/rejected envelope and deterministic replay proof.

## P07 | Service-First Software Productization

State: OPEN

Objective: complete the transition from a Skill package with supporting
scripts to independently installed intelligence software whose durable service
and first-class MCP contract are the primary product, with optional Skills as
least-privilege agent clients.

Current State:

- Current authority is Plan 0018 version 28/C76. Installed service 0.2.29/schema
  12 is ready with 62 documents, 62 current-version embeddings, active index
  `index-d4b3c45667cc2f635c557b85`, rollback 0.2.28, and all 42 specifications
  disabled. The immutable-index repair passed independent review; the two
  already-damaged 56-row historical indexes remain preserved as evidence.
  The operator approved one distinct replacement YouTube proof and raised the
  cumulative attempt ceiling to 25. The one replacement proof preserved every
  pre-existing index but exposed three missing current-version embeddings;
  that proof's historical post-state was 56/59. Independent review accepted the
  failed-closed receipt. C54 independently closes the zero-source repair at
  exact 59/59 current completeness without a source attempt. C56 independently
  accepted the bounded successor for X and both LinkedIn proofs. At C57 the
  operator raised the standing cumulative attempt approval ceiling from 25 to
  50 and authorized one transient-only service retry per remaining proof. The
  six-attempt packet passed independent retry-controller review at maxima
  31/76/1,307/2,640/zero. C58 authorized the exact reviewed 0.2.27 install and
  proof packet. C63 then stopped after the repaired last30days profile binding
  reached agent-browser's route-bound display proof and exhausted both
  attempts. Agent-browser P90 is now installed, provenance-converged, and live-
  proven. C64 opened independent review for one fresh X successor at cumulative
  maximum 30 of 50. That review caught one caller defect: 0.2.28 checked the
  returned profile but did not explicitly pass its durable profile binding to
  access planning. C65 contains the one 0.2.29 remediation and awaits terminal
  recheck. The recheck passed exact commit `dfefca5`; C66 authorizes installing
  that exact 0.2.29 artifact and one fresh X proof at cumulative maximum 30 of
  50. C67 records the installed artifact and a published attempt-one healthy
  zero-yield result with exact `last30days-facebook`, no auth/manual handoff,
  and unchanged 59/59 state. Cumulative actual use is 29/50; fresh independent
  receipt review passed with no critical finding. X evidence is accepted as
  healthy zero yield, not content yield. C69 preserves the immutable lifetime
  total of 29 attempts while resetting the governed proof ledger to epoch
  `p0018-v27-e2` at zero under the operator-approved ceiling of 50. It retires
  the old packet without carrying forward its unused attempts and opens a
  review-only, serial LinkedIn topic/profile observability plan. Independent
  review returned terminal PASS with zero critical finding; C70 authorizes the
  exact disabled topic-then-profile live packet, one identity at a time under
  its hard stops. C71 records both attempt-one terminal outcomes: topic stopped
  source-locally on `quality_gate_failed` with zero accepted items, while
  profile published one accepted item that deduplicated into the unchanged
  59/59 corpus/index. The two attempts used two requests, zero model calls and
  zero cost. C72 accepts terminal independent receipt review after 10/10
  envelope hashes and every live postflight invariant passed. Blinded-yield
  planning is open, but canary execution and recurrence remain prohibited. C73
  fixes five unique disabled specs, executor-blind salted yield commitments,
  one-attempt serial execution, packet ceilings, and reveal-after-terminal
  rules. Independent review's initial evidentiary-command FAIL was corrected in
  one bounded recheck; terminal PASS found no critical issue and C74 authorized
  exact disabled spec materialization plus serial one-attempt execution. C75
  records five terminal one-attempt receipts, seven accepted items, verified
  post-terminal reveal commitments, and 20% hidden class/range accuracy. C76
  accepts terminal independent review after one documented Roadmap authority
  repair and exact bounded recheck. Recurrence and release actions remain
  closed.
- The remaining bullets in this Current State block preserve chronological
  implementation history; version phrases such as "installed" or "now" are
  scoped to their historical checkpoint and do not override the first bullet.
- Historical baseline: the then-installed v0.2.20/schema-12 daemon,
  Unix-socket MCP adapter, durable
  collection supervisor, temporal corpus, semantic index, Graphiti projection,
  and App Intelligence contracts already demonstrate most runtime seams.
- Source and distribution are still conceptually anchored under
  `skills/last30days/`, and the successor queue tests features without first
  establishing an explicit independent software lifecycle and client/service
  compatibility contract.
- `CONCEPTS.md`, `README.md`, and the Skill's service-first path already
  describe the service as authority, but that product decision was not
  previously represented as an implementation transition.
- Plan 0018's first S01/S02 packet is accepted: the live unit runs the
  independently versioned release, MCP enforces the compatibility handshake,
  and installed upgrade/rollback preserved the schema-12 state.
- Plans 0015 and 0016 are closed with temporal/GraphRAG resilience plus
  accepted/rejected/replay App Intelligence authority evidence.
- S06 is accepted at `ac76e2b`: the primary Skill is a 137-line MCP client,
  privileged guidance is capability-gated, and the direct Engine remains an
  explicit compatibility/debug path.
- S07 installed the corrected service 0.2.9/MCP 4.0.1 pair and proved
  migration plus rollback, but final release review remains rejected pending
  one autonomous deterministic-yield proof.
- The one authorized public Reddit remediation interval ran autonomously with
  assessment disabled but yielded zero items and no index change. Its spec is
  paused.
- Source service 0.2.13 now has a committed opt-in agent-browser Reddit fallback
  after keyless RSS/Shreddit and before the paid adapter. One public smoke plus
  a same-page remediation proved the current `search-post-unit` DOM extractor,
  but 0.2.13 is not installed and durable indexed yield remains unproved.
- Plan 0019 completed its six-query public matrix and rejected production use:
  browser routing and latency were bounded, but multiword queries admitted
  one-token false positives and manual relevance was 54.5% against a 90% gate.
  The candidate remains uninstalled and no canary or soak ran.
- The bounded successor exhausted both live leases and exposed worker-failure
  persistence plus collection reconciliation defects. Service 0.2.10 repairs
  both paths and passed the complete deterministic suite.
- The approved 0.2.10 upgrade reconciled stranded state and remained ready,
  but its one new timer attempt again exceeded the worker wall bound without a
  receipt. Bounded containment prevented attempt 2. The installed daemon is
  now 0.2.12. Its authorized timer run produced a durable public receipt in
  about 2.5 seconds, proving the deadline repair, but observed zero items and
  did not advance documents or the active index.
- The configured browser-method campaign is closed: X topic, LinkedIn topic,
  and LinkedIn profile published through exact `agent_browser` provenance;
  Facebook and Reddit browser reached their adapters but failed closed on
  content quality. Reddit remains `keyless,agent_browser`, all campaign specs
  are disabled, and the corpus is ready at 56 documents.
- The version-17 first live gate installed service 0.2.22 with an exact
  per-spec access-method constraint and created five fresh disabled canary
  specifications. Four serial manual lanes published 10 total items; Reddit
  failed before source execution under superseded 0.2.21 and was not retried.
  The corpus settled at 59 documents/59 embeddings, all 37 specifications are
  disabled, rollback remains 0.2.20, and MCP adapter 4.0.1 was regenerated and
  reinstalled to restore its embedded contract-digest compatibility.
- Historical C39 result: independent receipt review rejected recurring
  enablement because actual request use, exact per-run index/deduplication
  counts, and a live repaired-Reddit proof were missing. C41-C42 subsequently
  repaired and proved Reddit observability; the other four legacy receipt gaps
  remain the bounded C43 successor scope.

Goal Seeds:

- independently versioned install, upgrade, migration, lifecycle, readiness,
  diagnostics, and rollback;
- stable MCP capability and version handshake for agents and applications;
- service-owned acquisition and timed work with no agent orchestration;
- authoritative temporal evidence plus rebuildable semantic/GraphRAG
  projections;
- bounded App Intelligence behind deterministic host policy and replay;
- query/synthesis, monitoring, admin, and maintenance Skills that consume MCP
  without depending on internal adapters or browser mechanics;
- state-preserving migration from current Skill-first installations.

Acceptance Seeds:

- service operation does not depend on a loaded Skill or connected agent;
- fresh MCP clients query and govern durable jobs without scraper knowledge;
- acquisition and evidence retrieval continue when App Intelligence is
  disabled;
- ordinary Skill instructions require no browser, cookie, tab, route, display,
  or scraper coordination;
- client/service upgrades and rollback preserve corpus, profiles, schedules,
  ledgers, and indexes.

Dependencies: consumes the proven P01-P06 seams without making their derived
indexes or stochastic workers authoritative.

Active Plan:

- `docs/dev/plans/0018-2026-07-29-service-first-software-product-transition.md`
  is the open transition authority. Service distribution, MCP compatibility,
  client-Skill redesign, timer ownership, durable publication/indexing, and
  rollback are accepted foundations on installed service 0.2.29/schema 12.
  Plan version 27 preserves the version-18 contract-bound request and outcome
  counts, immutable
  schema-12 start/final receipts, pre/post corpus/index snapshots, and public
  `collection list` `last_run` evidence. Checkpoint C42 records the separately
  authorized Reddit keyless proof as complete: one attempt, six governed
  requests, healthy zero yield, exact immutable receipt and unchanged 59/59
  snapshots. The first recurring-gate assessment failed because the other four
  yielding receipts predate that evidence contract and the planned 14
  scheduled identities no longer fit the consumed attempt ceiling. All 37
  specifications remain disabled. C44 accepted the independently reviewed,
  operator-approved four-proof evidence-completion successor, but its first
  YouTube proof triggered the global integrity stop when historical index
  embedding membership mutated from 59 to 56. Version 20/C46 closes the
  no-source remediation on installed service 0.2.25 and stops at a separate
  replacement-YouTube human gate. Version 21/C49 records that exact proof as a
  global integrity stop: historical snapshots stayed immutable, but three new
  current versions were published without version embeddings. Version 22/C51
  opens the bounded deterministic repair, and C54 closes it on 0.2.26 at
  59/59. C56 independently accepted the three remaining X/LinkedIn proof plan.
  Version 24/C57 consumes the operator gate, establishes the standing
  50-attempt approval threshold, and opens the review-first implementation of
  a manual `--max-attempts 2` control. C58 records the bounded initial FAIL,
  one remediation, and terminal PASS. C59 installs exact 0.2.27 and records
  the first X attempt stopping `awaiting_operator/auth_required` with zero
  side effects and no retry. C60/Version 25 records the operator correction:
  the canonical X profile is already authenticated, while the repo failed to
  consume its durable binding and dropped agent-browser's external Guacamole
  handoff URL. Candidate 0.2.28 repairs those seams without a source attempt;
  C61 records terminal review PASS and exact healthy installation. Its proposed
  timestamp canonicalized to the old held daily interval without executing;
  C62 corrects the fresh X successor to the distinct Aug 2-3 interval. C63
  proves the repaired `last30days-facebook` binding live without an auth or
  manual-handoff incident, then stops terminally after both allowed attempts
  hit the same agent-browser `remote_view_open` timeout. LinkedIn remains
  `not_run`. Agent-browser P90 is now installed and direct-route live-proven;
  C64 opened the review-first checkpoint for one fresh Aug 3-4 X identity.
  C65 records the review FAIL and one bounded 0.2.29 remediation that forwards
  the explicit durable `last30days-facebook` binding. C66 records terminal PASS
  and authorizes exact installation plus the single fresh X proof. C67 records
  that proof as attempt-one healthy zero yield with unchanged 59/59 integrity.
  C68 accepts its fresh independent receipt review with no critical finding.
  C69 starts governed budget epoch `p0018-v27-e2` at zero without rewriting the
  immutable lifetime total of 29, retires the Version 24 packet at four of six,
  and independently reviews a maximum-four-attempt serial LinkedIn
  topic/profile observability successor. C70 records terminal PASS and opens
  that exact topic-then-profile packet. C71 records two attempt-one receipts,
  unchanged 59/59 integrity, two epoch requests, one accepted/deduplicated
  profile item, and zero cost/model calls. C72 accepts its independent final
  review. Version 28/C73 records a sealed, review-first blinded-yield successor
  across Reddit, YouTube, X, Facebook, and LinkedIn. The preparer retains
  private predictions/nonces; the executor sees only public selectors and
  commitments. C74 records the blind terminal review PASS and opens the exact
  live packet. C75 records all five one-attempt terminal receipts and the
  post-terminal reveal: Reddit healthy-zero, YouTube/X/Facebook accepted
  3/3/1, and LinkedIn source-local `agent_browser_error`. All commitments
  verify; only YouTube's hidden forecast matched, for 20% class/range accuracy.
  C76 accepts the terminal independent recheck with zero critical findings.
  Recurring enablement remains a later gate.

Next Bounded Action:

- Version 28 is terminally accepted. Before any recurring collection decision,
  reconcile a new successor plan against the accepted source-local outcomes,
  failed 20% forecast calibration, current 62/62 index, and 42/0 spec state.
  Keep source attempts, recurrence, push, tag, publication, and release closed
  until that separate gate is reviewed and explicitly opened.

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
