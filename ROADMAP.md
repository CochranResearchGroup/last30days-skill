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

P08 Governed Recurring All-Source Tick
  └──> schedules only the terminal tick unit accepted by P07/Plan 0023

P09 Facebook Agent-Browser Timeout Remediation
  └──> repairs the truthful Facebook gap observed by P08 without changing its schedule
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
   is closed at its terminally accepted version 28/C76 product transition.
8. `docs/dev/plans/0023-2026-08-04-durable-all-source-intelligence-tick-mvp.md`
   is closed at its terminal manual all-source tick and ordinary-query proof.
9. `docs/dev/plans/0024-2026-08-06-governed-recurring-all-source-tick.md`
   is closed at its terminal service-owned daily recurrence proof.
10. `docs/dev/plans/0025-2026-08-07-facebook-agent-browser-timeout-remediation.md`
    is cancelled after its bounded proof reached a Facebook checkpoint rather
    than the repeated pre-render timeout.
11. `docs/dev/plans/0026-2026-08-07-recurring-browser-reauthentication-notifications.md`
    is the open successor for verified routine browser handoff and notification.

The 2026-07-29 architecture direction made Plan 0018 the governing successor
after Plan 0014's terminal timer result. Plan 0018 is now `CLOSED` at its
independently accepted version 28/C76 service-product and source-evidence
boundary. Plans 0023/P07 is `CLOSED`; Plan 0024/P08 is `OPEN` for the bounded
Plan 0057 semantic-sidecar and volume-canary successor; Plan 0025/P09 is
`CANCELLED` as superseded; Plan 0026/P10 is `OPEN` under the operator's
explicit recurring handoff and Slack-notification authority.
Plans 0013 and 0017 remain planned and outside this transition critical path;
Plans 0015 and 0016 are closed foundations.

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

State: CLOSED

Objective: complete the transition from a Skill package with supporting
scripts to independently installed intelligence software whose durable service
and first-class MCP contract are the primary product, with optional Skills as
least-privilege agent clients.

Current State:

- P07 is terminally closed by Plan 0023 version 20/C52. Plan 0018 is closed at its
  terminally accepted version 28/C76 predecessor boundary. Installed service
  0.3.0/schema 15 is ready with 62 documents, 62 current-version embeddings, active index
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
  repair and exact bounded recheck. Plan 0023/C08 records the same evaluator's
  terminal `FAIL` after the single C07 rework. Exact commit `4f1e642`, evidence
  commit `8f222d9`, and artifact
  `8217c994d54cbba2ced9b65261ce3149caff1ed86e4006f75ab0cca1a00ff92b`
  preserve typed partial evidence and correctly block human-gated lanes, so
  that original finding is closed. The candidate is nevertheless stopped:
  agent-browser `view_takeover` returns a viewer lease without the external URL
  invented by the fixture, DNS latency can consume the wall deadline before a
  stale timeout reaches urllib, and the validated address is not pinned across
  urllib's second resolution. Its staged provider results,
  raw-first replay, terminal-lane recovery, durable snapshot reconstruction,
  typed image/video-thumbnail carriage, programmatic rendered-page capture,
  and acknowledgment-gated external agent-browser route remain useful local
  T07 foundations, but they do not close the real observation/media bridge.
  The exact rebuild and isolated install/rollback/roll-forward proof passed;
  the installed runtime remains 0.2.29/schema 12. C07's sole review/rework
  cycle is exhausted. C09 records the operator's explicit approval of version
  2 and opens one bounded local packet: `view_takeover` supplies lease proof
  while the retained ready stream supplies the external route, and media
  retrieval must connect to its admitted address under one recomputed wall
  deadline. The packet has two implementation attempts, one fresh independent
  review plus at most one consolidated rework, and no implementation
  delegation. User-config readback, live T08 acceptance, installation, Guac
  observation, recurrence, push, publication, and release actions remain
  closed. C10 then corrects one pre-implementation assumption from direct
  agent-browser source: `view_takeover` has no durable viewer-lease collection
  side effect. The exact contract is the dashboard path—resolve the retained
  stream URL, require accepted takeover identity and returned lease metadata,
  then use that retained URL. C11 binds the repaired implementation at exact
  commit `6402d16`, reproducible artifact
  `ea91dd5897a2b67911e9b60683ef5896d168ceda045d5e15fdff3d9f2683a8ba`,
  full-suite and isolated lifecycle evidence, and receipt 0041. The candidate
  now awaits one fresh independent review; all real install, user-config,
  provider, notification, Guac, recurrence, publication, and cost gates remain
  closed. C12 records that review's terminal PASS with no blocking, high-
  severity, regression, or rework finding at receipt 0042. The V2 local repair
  is accepted; Plan 0023 remains open at the separate human gate for exact
  candidate installation, real user-scoped configuration, and the manual live
  T08 tick. Recurrence remains prohibited. C13 opens one local prerequisite:
  a side-effect-free `tick preflight` readback that uses the enqueue
  identity/admission machinery while exposing only sanitized config, lane,
  provider, resource, budget, and notification readiness evidence. It changes
  the install candidate, so it must be rebuilt, lifecycle-proven, and
  independently reviewed before live authority. C14 implements that seam,
  shares enqueue identity/admission logic, digests config-defined identities,
  performs sequential readiness without sending, and repairs the canonical
  loader's previously hidden rejection of optional observation config. Full
  candidate validation and exact artifact proof are in progress. C15 records a
  complete green local matrix, including the repaired clock-rollback receipt
  edge, and makes the exact candidate ready for commit, reproducible build,
  isolated lifecycle proof, and independent review. C16 binds exact commit
  `0fa63c0`, reproducible artifact
  `32107a9dd13de7f548f1456cf5a91d7dfe414c3ef63b58129c295bd033b0a9ea`,
  schema-15 lifecycle proof, and receipt 0043. C17 records that review's
  terminal FAIL: preflight did not reject enabled uninstalled OCR/sidecar
  adapters or malformed observation ports before notification readiness. The
  single authorized consolidated repair is now locally GREEN: state-free
  admission shares the exact installed analysis registry with the runner and
  rejects malformed observation authorities before readiness. Full validation,
  complete Python, Go, compilation, package, JSON, diff, and authority matrix
  is green at C19. C20 binds exact commit `9442be9`, reproducible artifact
  `b0f3cbb6d05c183983fc33d7510057b768573a61f20fb1e5aeb7a308bfc890f2`,
  schema-15 isolated lifecycle proof, and receipt 0044 for the sole bounded
  recheck. C21 records terminal PASS with no remaining finding at receipt
  0045. The sanitized preflight prerequisite is locally accepted; Plan 0023
  remains OPEN at the explicit human gate for exact real install, sanitized
  user-config preflight/readback, and separately gated manual T08. Recurrence
  remains prohibited. The operator authorized the reviewed install/preflight
  Phase A at C22, but pre-mutation `diagnose` failed closed on an installed
  database-schema/readiness mismatch. One read-only installed-state diagnostic
  proved the installed state healthy but reproduced a real rollback defect:
  exact 0.2.29 cannot start after schema 12→15 migration, while prior lifecycle
  receipts used a synthetic old artifact built from schema-15 code. C23 opens
  one bounded transactional database-snapshot/rollback repair. C24 records a
  GREEN exact historical-artifact rollback and roll-forward candidate with
  release-bound owner-private database state. C25 records the complete green
  Python/Go/lifecycle/compile/shell/diff/authority matrix. C26 binds exact
  commit `8d649e2`, installer hash, unchanged artifacts, exact historical
  replay, real read-only diagnose, and receipt 0046 for one independent review.
  That review returned terminal FAIL before real mutation: readiness did not
  compare the running runtime-manifest identity, and recovery database restore
  could proceed after an unconfirmed stop. C27 opens the one authorized
  consolidated rework with adversarial manifest and failed-stop tests. C28
  records those cases GREEN, 11 lifecycle and 21 affected integration tests,
  the complete Python/Go/shell/compile/diff/authority matrix, exact historical
  rollback/roll-forward replay, and unchanged real 0.2.29/schema-12 readback.
  C29 binds immutable commit `1a53f67`, installer hash, unchanged artifacts,
  and replacement receipt 0047 for the sole terminal recheck. That recheck
  returned PASS with no finding and is bound in receipt 0048. C30 admits the
  one already-authorized exact 0.3.0 upgrade plus strict installed/rollback
  readback; real rollback, config preflight, and every live/recurrence gate
  remain closed during that install packet. C31 records the one exact upgrade
  PASS: installed current/previous are 0.3.0/0.2.29, schema 15 is ready with
  unchanged 62/62 corpus/index completeness, and the exact schema-12 rollback
  state is digest-bound, integrity `ok`, and owner-private. Receipt 0049 binds
  the result. The next admitted Phase A action is sanitized config preflight
  without provider or notification sends. That one preflight failed closed at
  C32 because the required user-scoped `tick-config-v1.json` is absent. No
  config content, readiness call, provider, send, state, Guac, or timer action
  occurred; installed 0.3.0 and exact rollback remain healthy. Creating the
  missing operator-particular document is a new human gate. The operator then
  explicitly approved deriving it from Plan 0018 Version 28 and the agreed
  sequential notification policy, with all particulars retained only in user
  config. C34 records an owner-private mode-0600 config and sanitized preflight
  PASS: five admitted lanes/proofs, primary non-message readiness, configured
  fallback truthfully not checked after first-ready stop, and zero tick rows,
  providers, sends, artifacts, Guac leases, or timers. Receipt 0051 binds only
  digests/counts/readiness. T08 and recurrence remain separate human gates.
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

- `docs/dev/plans/0023-2026-08-04-durable-all-source-intelligence-tick-mvp.md`
  is the terminally closed manual-tick authority. It freezes the manual all-source tick as
  the first MVP: config-driven services and targets, raw-first durable
  evidence, terminal lane/stage accounting, incidents and notification
  failover, protected rendered-page artifacts, OCR and semantic image
  sidecars, cross-source derived cataloging, coherent hybrid query snapshots,
  recovery/replay, and a manual acceptance gate. It explicitly excludes timer
  enablement. Checkpoint C04 validates the deterministic provider, evidence,
  media/analysis, incident, catalog, query, and reconstructable-receipt join.
  The T07 provider/raw crash seam and Phase A install/config preflight are now
  accepted. Checkpoint C42 records exact transactional installation of reviewed
  service 0.3.1 and a matching side-effect-free sanitized preflight. The next
  terminal 0.3.4 result proves the bounded manual tick, derivative pipeline,
  promoted ordinary-query head, and exact receipt reconstruction. Timers remain
  a separate later goal requiring a new governed plan.
- `docs/dev/plans/0018-2026-07-29-service-first-software-product-transition.md`
  is the closed predecessor authority. Service distribution, MCP compatibility,
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

- preserve P07/Plan 0023 as closed predecessor authority; execute the separately
  governed P08/Plan 0024 recurrence lane without reopening this plan.

## P08 | Governed Recurring All-Source Tick

State: OPEN

Objective: enable one service-owned daily UTC schedule that calls only the
durable all-source tick accepted by Plan 0023, then prove one bounded automatic
tick, restart-safe deduplication, next-boundary continuity, and fail-closed
pause controls.

Current State:

- Plan 0062 version 6/C09 is the current actionable P08 plan. Service 0.3.96 is
  installed ready with schema 17 and X's finite 40-scroll allowance. Saved recurring
  revision `operator-20260901-x-linkedin-80-v1` requests 80 X and 80 LinkedIn
  posts, retains three attempts for each, and provides 360 seconds per social
  attempt. The exact guarded digest rebind preserved the September 2 boundary,
  prior tick, and ready schedule without admitting work. P0062-B will observe
  the resulting ordinary tick. The operator subsequently authorized one
  immediate manual X-and-LinkedIn-only acceptance tick under the same saved
  limits. That tick failed before scraping: two X attempts hit the unproven
  stale-session identity gate because the reviewed fresh-session recovery
  switch was absent, then schema 16 rejected retry ordinal 2 despite the saved
  three-attempt limit and aborted before LinkedIn. Schema 17 is installed and
  production-proven: the one successor acceptance tick reached all three X and
  LinkedIn attempts before terminalizing degraded with zero active residue.
  Agent Browser now truthfully reports `profile_capability_required`; Last30days
  did not possess or transmit that capability. Service 0.3.94 source now reads
  only an absolute, same-user 0600 nonsymlink capability file and sends the raw
  value ephemerally to both MCP planning and execution without placing it in
  argv, stable target config, logs, receipts, or service state. Service 0.3.94
  and MCP 4.0.4 are installed from merged main, and a fresh adapter reports
  schema-17 compatibility. The already-open Codex connector required targeted
  termination and did not hot-restart. After reconnect, the operator explicitly
  authorized the remaining registration, private configuration, and one live
  tick. The existing `last30days` grant was rotated in place without creating a
  duplicate principal; its replacement capability is owner-private, wired into
  the restarted ready service. The one authorized manual tick nevertheless
  bypassed those settings because the direct CLI process does not load the
  systemd `EnvironmentFile`; all six attempts followed the old unauthenticated
  route and observed zero items. Cleanup is complete and the ordinary service
  timer has both settings in its live process environment. Follow-up diagnosis
  repaired two Last30days routing defects, capability-rejoined the exact live
  profile browser, and installed service 0.3.96. Manual tick
  `tick-2fa1622b2c62fbd54a9880e456dbcbb9` then accepted 80 distinct canonical X
  posts and 80 distinct canonical LinkedIn posts with both lanes successful,
  clean lease/database cleanup, and unchanged September 3 schedule continuity.
  Plan 0062 C09 now owns observation of that ordinary scheduled tick; manual
  acceptance does not by itself close recurring-scheduler acceptance.
  Current authority:
  `docs/dev/plans/0062-2026-09-01-recurring-x-linkedin-80-item-volume.md`.
- Plan 0060 version 1/C06 is CLOSED after installing service 0.3.91 with finite
  active-tick drain semantics and genuine three-attempt transient retry budgets
  for recurring X and LinkedIn. The exact-digest schedule rebind preserved the September 2
  boundary. After Agent Browser restored one ready runtime host, the reviewed
  exact-profile fresh-session path bypassed an unproven stale session identity
  without changing profiles. The terminal LinkedIn verification accepted 20/20
  unique canonical posts in 88.3 seconds after 10 non-stagnant scrolls while
  deterministically excluding 53 sponsored-ad observations and deduplicating
  110 repeated observations. P08 remains open for the next ordinary scheduled
  tick. Current authority:
  `docs/dev/plans/0060-2026-09-01-tick-restart-recovery.md`.
- Plan 0061 version 1/C01 is CANCELLED before its scheduled boundary because
  the operator replaced its unchanged-configuration premise with the 80+80
  recurring target now owned by Plan 0062. It admitted no tick. Historical
  authority:
  `docs/dev/plans/0061-2026-09-01-next-ordinary-tick-observation.md`.
- Plan 0059 version 1/C01 closes a schedule-disabled 80+80 live capacity
  canary on installed service 0.3.90. LinkedIn accepted 80 unique canonical
  posts in one attempt after 29 scrolls while deterministically excluding 367
  sponsored-ad observations. X's unmodified 32-scroll attempt accepted 78 and
  remained non-stagnant; one transparent process-local 36-scroll retry accepted
  80. Recurring configuration, disabled specs, exact profile identity,
  schedule, and databases remained unchanged. The experiment proves live
  capacity but not an installed X 80-item guarantee; a persistent X ceiling
  change requires a new implementation decision. Current authority:
  `docs/dev/plans/0059-2026-08-31-x-linkedin-80-post-live-canary.md`.
- Plan 0058 version 3/C03 closes the retrieval-throughput successor with exact
  service 0.3.90 installed and live authenticated acceptance at X 40/40 and
  LinkedIn 40/40. The repair keeps one Agent Browser MCP control process alive
  across the complete scrape, uses the reviewed fresh-session override only
  when no compatible exact-profile browser is live, and calibrates X's bounded
  feed allowance to the observed two-new-posts-per-scroll floor. LinkedIn
  deterministically excluded 101 sponsored-ad observations. Recurring source
  configuration is unchanged: X and LinkedIn feeds enabled, Reddit and
  Facebook disabled, and YouTube unchanged. Current authority:
  `docs/dev/plans/0058-2026-08-31-x-linkedin-feed-throughput-repair.md`.
- Plan 0058 version 2/C02 validates service 0.3.88 for the bounded
  retrieval-throughput repair
  after Plan 0057's terminal 40+40 baseline accepted X 24/40 and LinkedIn
  12/40. The successor targets X's fixed eight-scroll feed ceiling and
  LinkedIn's exact-control-gated stagnant-snapshot stop, preserves deterministic
  ad/spam filtering and recurring configuration, and authorizes exactly one
  new schedule-disabled 40+40 acceptance canary after installation. The X
  provider-free proof reaches 40 after 12 of its 14 allowed scrolls, and the
  LinkedIn proof reaches 40 after crossing one control-free stagnant snapshot
  boundary while preserving its global 32-scroll ceiling. Current
  authority: `docs/dev/plans/0058-2026-08-31-x-linkedin-feed-throughput-repair.md`.
- Plan 0057 version 29/C29 consumes and reconciles the one-shot 40+40 canary.
  Authenticated direct passes through exact retained browser
  `session:last30days-force-20260831-c29` accepted 24 unique canonical X posts
  and 12 unique canonical LinkedIn posts. X reached its eight-scroll production
  bound with only duplicate rejections; LinkedIn stopped at four stagnant
  snapshots after deterministically excluding four unique sponsored ads. The
  40-item values are ceilings rather than guaranteed yield, criterion 8 is
  satisfied by the attempted terminal result, Plan 0057 is CLOSED, and P08
  returns to CLOSED. A future higher-yield repair belongs in a new bounded plan.
- Plan 0057 keeps P08 open after service 0.3.80's successor tick proved X 20/20
  but LinkedIn 5/20. All 15 unlinked observations were structurally broad
  list-item chrome without post actions or timestamps; the actual early stop
  was the two-snapshot stagnation guard after only two scrolls. Version 7/C07
  validates and installs service 0.3.81 with a finite four-snapshot LinkedIn
  tolerance. Version 8/C08 reconciles the ready schema-16 runtime, unchanged
  recurring schedule/config, released leases, healthy SQLite, and clean Git.
  The explicit three-attempt LinkedIn live ceiling is reached; another provider
  attempt requires a renewed budget, and conditional 40+40 remains gated.
- Plan 0057 version 9/C09 records the operator's renewed live budget: exactly
  one schedule-disabled 20+20 canary on installed service 0.3.81, followed by
  exactly one 40+40 canary only if both 20-item lanes pass. Recurring settings,
  Reddit/Facebook state, and Agent Browser remain outside the mutation scope.
- Plan 0057 version 10/C10 records that the renewed 20+20 canary failed before
  observation: X navigation hit Agent Browser's process mutation lock and the
  LinkedIn `tab_new` job remains queued while that control plane reports busy.
  The retained browser is still viable/ready. The 40+40 precondition is false;
  no 40-item tick was created and Agent Browser mutation remains out of scope.
- Plan 0057 version 11/C11 records the operator-reported Agent Browser upgrade
  and explicit retry authority. The old queued job is absent, lock diagnostics
  are clear, and both no-launch access plans select the existing durable social
  profile without acquisition, lifecycle, or manual-auth blockers. One fresh
  20+20 canary is ready; 40+40 remains conditional on both lanes passing.
- Plan 0057 version 12/C12 records the post-upgrade retry. Both X and LinkedIn
  `tab_new` jobs were rejected before start with
  `existing_session_profile_identity_unproven`. The access plan advertises an
  unblocked launch-new request carrying session name
  `last30days-social-replacement-20260829`, but current service state has no
  session or runtime-owner record for that identity. The durable authenticated
  profile itself remains registered. The 40+40 gate did not open.
- Plan 0057 version 13/C13 records the operator-authorized direct owner repair.
  Read-only preflight proved the exact `last30days-facebook` profile had no
  live Chrome process, singleton lock, service holder, browser, or current
  session. Fresh direct session `last30days-social-direct-20260830-c13` then
  launched that exact profile and is now the sole ready owner at PID `74831`
  with reachable CDP. No X/LinkedIn navigation or Last30days canary ran, so a
  renewed 20+20 attempt still requires explicit authority and 40+40 remains
  gated.
- Plan 0057 version 14/C14 records the renewed schedule-disabled 20+20 canary.
  Tick `tick-cbc7830ca7d65d24a8ccacd3966c9291` failed before observation with
  zero X and zero LinkedIn items because both Agent Browser `tab_new` jobs
  rejected owner generation 57 as `runtime_owner_generation_stale`. Fresh
  no-launch plans now explicitly block on the still-transferring lifecycle
  owner; this is not authentication, infinite-scroll, extraction, or filtering
  evidence. A provider-free Last30days regression now preserves that structured
  failure reason in a version-distinct service 0.3.82 candidate, but that
  candidate is not installed. P08 remains OPEN, 40+40 remains gated, and
  another live retry waits on Agent Browser owner reconciliation plus renewed
  attempt authority.
- Plan 0057 version 15/C15 records the next retry's no-effect preflight. Agent
  Browser transaction `upgrade-4bd5a63e-a613-4997-8853-f61b15fc5ef9` has
  reached revision 10 `candidate_ready`, but old generation
  `0.28.0-ceb8f8a926e6-178c836a535e` remains selected, two owner obligations
  remain, `nextSafeAction=resume`, and runtime admission is still drained. Both
  X and LinkedIn access plans therefore fail before profile selection with
  `runtime_admission_draining`. No provider attempt was consumed; the exact
  20+20 authority remains available once the Agent Browser upgrade owner
  terminalizes the transaction and access plans become executable. P08 remains
  OPEN and 40+40 remains gated.
- Plan 0057 version 16/C16 records that the new Agent Browser workstation
  generation `0.28.0-899c9147e387-94e7829f7efc` is accepted and globally ready,
  closing `runtime_admission_draining`. Both X and LinkedIn still select the
  correct fresh authenticated profile, but owner generation 57 for
  `session:last30days-social-direct-20260830-c13` remains `transferring` with
  no reusable route, so both service requests remain blocked by
  `lifecycle_owner_blocks_replacement`. No provider attempt was consumed; the
  exact 20+20 authority remains available after Agent Browser reconciles that
  profile-specific owner. P08 remains OPEN and 40+40 remains gated.
- Plan 0057 version 17/C17 records that replacement Agent Browser generation
  `0.28.0-733cde7ff22e-04a1b2314f0d` is accepted and globally ready, but both
  feed plans remain blocked by the same generation-57 lifecycle transfer for
  `session:last30days-social-direct-20260830-c13`. The correct profile and fresh
  target readiness are present, but neither plan exposes an executable service
  request. No provider attempt was consumed; the exact 20+20 authority remains
  available after profile-owner reconciliation. P08 remains OPEN and 40+40
  remains gated.
- Plan 0057 version 18/C18 records terminal tick
  `tick-342713d933e6415a940da34f6aa6d7c4`: both no-launch plans finally exposed
  launch-new `tab_new` requests for replacement session
  `handoff-3c307b74ea88da11`, but both jobs failed before start with
  `existing_session_profile_identity_unproven`. X and LinkedIn therefore
  yielded 0/20 and 0/20 without reaching either feed. This is an Agent Browser
  access-plan/service-request contract contradiction, not authentication,
  scrolling, extraction, or filtering evidence. The renewed attempt is
  consumed; P08 remains OPEN and 40+40 remains gated pending an Agent
  Browser-side repair and renewed live authority.
- Plan 0057 version 19/C19 records the operator-authorized stale-lease repair.
  Agent Browser's scoped `last30days` capability now binds the exact existing
  `last30days-facebook` profile to ready browser
  `session:last30days-force-20260831-c20` at owner generation 64. The active
  lease is capability-proven with no blocking identity axes, same-browser X and
  LinkedIn tab acquisition succeeds, and bounded probes reach X Home and the
  LinkedIn Feed. No Last30days attempt was consumed; P08 remains OPEN and 40+40
  remains gated pending renewed authority for one 20+20 canary.
- Plan 0057 version 20/C20 records terminal tick
  `tick-dea48f46dcda2e88caf9d5f2d58bff9e`. LinkedIn reached raw 20/20 with 20
  unique canonical-shaped URLs and successful media, OCR, semantic-sidecar,
  indexing, and promotion stages. X reached 0/20 because its acquired tab's
  navigation exceeded Agent Browser's persisted 25-second job deadline; the
  generation-64 lease stayed healthy and force acquisition was not implicated.
  Five accepted LinkedIn rows are composer chrome and one contains a
  `Promoted` marker, so criterion 7 remains false. P08 stays OPEN and 40+40
  remains gated.
- Plan 0057 version 21/C21 removes the shared adapter's fixed 25-second
  navigation ceiling. Navigation now inherits the bounded source/run budget,
  retains a five-second caller margin, and remains capped by the existing
  105-second cumulative adapter limit. The regression is red/green, affected
  presubmit and canonical Python/MCP Go gates pass, and service 0.3.82 is the
  validated install candidate. No provider attempt was consumed; P08 remains
  OPEN pending the explicitly authorized 20+20 retry.
- Plan 0057 version 22/C22 installs exact service 0.3.82, capability-rebinds the
  same live social browser from expired owner generation 64 to active
  generation 65, and records terminal tick
  `tick-167701135a7f1c282b0610a635a6ea53`. X produced 20 unique canonical
  status posts in one attempt. LinkedIn reached raw 20/20 in one attempt, but
  five accepted rows are deterministic `Start a post` composer chrome, leaving
  only 15 actual feed posts. No accepted item carries a literal promoted or
  sponsored marker. P08 remains OPEN, criterion 7 remains false, and 40+40
  remains gated.
- Plan 0057 version 23/C23 rejects the exact LinkedIn composer-control cluster
  at the candidate-validation seam even when it inherits a canonical-shaped
  activity URL. The regression is red/green; affected and canonical Python,
  MCP Go, package, install, compilation, and governance gates pass; and exact
  service 0.3.83 is installed ready and compatible. P08 remains OPEN pending
  the one authorized LinkedIn-only 20-post proof; 40+40 remains gated.
- Plan 0057 version 24/C24 records terminal LinkedIn-only tick
  `tick-899ad0de3d34aa8ecb0a52b3cce30c9d`. It accepted 20 unique canonical
  activity URLs in one attempt and rejected nine composer-control candidates,
  but three accepted rows were exactly `Sort by: Top`, leaving 17 actual feed
  posts. That exact comment-control family now records
  `sort_control_chrome`; the red/green and complete regression gates pass, and
  exact service 0.3.84 is installed ready. P08 remains OPEN, criterion 7 is
  false, and another LinkedIn proof plus 40+40 require renewed authority.
- exact service 0.3.5/schema16 is installed active/ready with 0.3.4/schema15
  rollback retained and the reviewed contract/runtime hashes current;
- one service-owned daily UTC schedule admitted exactly one Aug 5-6 timer tick,
  which terminalized `complete_degraded` at five attempts, 15 requests, seven
  accepted items, 162 wall seconds, zero cost, and zero model use;
- restart two preserved the same boundary, tick, execution attempt, five
  provider attempts, three schedule events, and promoted ordinary-query
  snapshot with no duplicate work; Aug 7 is the exact next boundary;
- 42 legacy collection specs remain disabled, no last30days systemd timer
  exists, SQLite is healthy, and the daily schedule is enabled/ready;
- independent terminal verification and the complete Python/Go/compile and
  governance validation pass with zero unresolved findings;
- Graphiti episode `539db5b5-4d0e-4470-a81c-68f5826ed14c` is durable and passes
  UUID, grouped, exact-metadata, and fact-search readback;
- the next ordinary Aug 6-7 timer tick also terminalized `complete_degraded`
  with one execution attempt, five provider attempts, seven items, zero cost/
  model use, a promoted snapshot, zero incidents/notifications, and a truthful
  Facebook lane failure; the schedule is ready for Aug 8 and lifetime provider
  attempts are 25/50. The activation proof itself stopped exactly at 20/50;
  this is the distinct first ordinary steady-state boundary.
- on 2026-08-16 the operator temporarily disabled the Reddit and Facebook
  targets after the productivity review. Owner-private revision
  `operator-20260816-increase-x-linkedin-volume-v1` retains exactly YouTube,
  X, and LinkedIn; X now admits up to ten accepted items, while LinkedIn uses
  topic/content search and admits up to ten instead of the single company
  profile record. YouTube remains at three, Reddit/Facebook remain disabled,
  and `daily-default` remains enabled/ready for the same Aug 17 UTC boundary.
  Neither private-config transition admitted a tick or provider attempt.
- the operator then requested one immediate X/LinkedIn test. Plan 0049/C02 ran
  exactly one receipt-only two-lane canary under a distinct manual schedule
  identity. X accepted five of nine observed; LinkedIn accepted three of 12;
  eight durable source versions and a 17-entry tick-query snapshot were
  published. Both providers succeeded; three LinkedIn image semantic-sidecar
  `analysisoutputmissing` results made the tick `complete_degraded` without
  changing `daily-default`.
- Plan 0050 installed service 0.3.48 and ran one fresh two-lane canary. X
  accepted four of seven observed; LinkedIn accepted three of ten and included
  one durable visible `now •` result. LinkedIn `missing_date` fell from six to
  zero; its remaining rejections are duplicate/permalink/type quality. Seven
  source versions and a 25-entry snapshot were published. Three separate
  semantic-sidecar `analysisoutputmissing` results kept the tick
  `complete_degraded` without changing `daily-default`.
- Plan 0051 installed validated service 0.3.50 and admitted the operator's
  exact one-shot X/LinkedIn canary with temporary 20-item ceilings per lane,
  but neither scraper observed a post. The recurring ten-item configuration,
  Reddit/Facebook pause, and `daily-default` remained outside the mutation.
  X failed `auth_required` and
  LinkedIn failed `operator_ingress_unavailable` after agent-browser replaced
  the disconnected named-profile browser with a default-profile process that
  later exited. The tick terminalized `complete_degraded` with zero items;
  recurring config and `daily-default` remain unchanged.
- Plan 0052 installed service 0.3.51 and corrected only the incident taxonomy:
  `operator_ingress_unavailable` now produces `provider_degraded` with an
  explicit statement that authentication was not determined. Genuine auth and
  checkpoint signals remain reauthentication incidents. The Aug 17 recurring
  tick had already terminalized before the one managed restart; no tick,
  browser, source-config, schedule, or notification effect was added.
- Plan 0053 installed service 0.3.52 and made both X auth classification and
  recovered Slack notices evidence-bound. Its one X-only retry succeeded with
  five accepted posts from 13 observed, no retry, incident, notification,
  model use, cost, or recurring-schedule change. The exact social profile and
  Route A are ready; service 0.3.51 remains rollback.

- Plan 0054 closes at version 5/C05 after the separately repaired browser-owner
  boundary allowed one terminal retry. X found 20 unique linked posts, accepted
  13, rejected seven legitimate short/off-topic posts, and deduplicated 13
  repeated captures with zero ads or missing permalinks. The installed 0.3.53
  accepted-yield loop is therefore proven without a recurring-schedule change.
- Plan 0055 owns the successor LinkedIn defect exposed by that same tick. The
  accepted-unique correction and retained daemon-route fix are installed with
  service 0.3.58. Version 6/C06 proves the workstation upgrade is accepted and
  every readiness axis remains true, then consumes the one authorized 20/20
  canary. Both lanes still fail before post observation because the exact
  authenticated social browser is preserved as an external/manual runtime,
  while only a different logical browser received a migration adoption
  receipt. The plan remains open on the explicit owner/session transition; the
  canary is terminal and consumed.
- Plan 0055 version 16/C16 supersedes acquisition-time semantic filtering with
  a retrieval-first contract. Candidate service 0.3.59 retains structurally
  valid, canonical, in-range X and LinkedIn posts when text is short or lacks
  lexical topic overlap, preserving those conditions as diagnostics while
  deterministic promoted/sponsored, navigation-noise, and exact-duplicate
  exclusion remain. Service 0.3.60 is now installed ready, recurring X and
  LinkedIn targets select their authenticated home feeds, and topic search is
  retained for on-demand use. The first feed canary observed no posts because
  both Agent Browser launch-adoption jobs failed with
  `runtime_lifecycle_process_tree_record_missing`. The authorized follow-up
  closed that exact retained browser, repaired the selected host's socket route,
  and installed a ready named runtime lane. One non-provider tab request then
  reached display launch but the selected old generation collided with
  protected live Xvfb display `:90`. Agent Browser transaction
  `upgrade-0df91191-ad9b-4eb9-aa85-2f92e9729563` subsequently accepted the
  repaired current generation with all readiness axes true. The newly
  first authorized X/LinkedIn retry then failed before navigation because the
  Last30days owner registry retained absent browser
  `session:plan0117-final-runtime` as non-terminal `closing` with an owned
  cleanup obligation. Agent Browser's reviewed reconciliation moved that exact
  owner to `terminal/satisfied` while preserving the authenticated profile.
  The next authorized tick still observed zero posts because terminal
  replacement rejected the new `session:last30days-home-feed` logical ID before
  provider navigation. Agent Browser source commit `cd23311e` repairs that
  exact next-generation logical-ID move with collision and transfer guards,
  but it is not installed. Authentication, direct-feed extraction, and
  acceptance therefore remain untested.
- Plan 0055 version 17/C17 supersedes the old pre-navigation gate with current
  direct-feed evidence. Under the operator's exact three-attempt budget per
  service, X reached the home feed twice, observed 32 cards each time, and
  accepted 11 unique in-range posts; its first attempt failed transiently
  before observation. LinkedIn reached the home feed on all three attempts,
  observed 30 cards each time, and accepted 0, 1, and 0 posts. Five LinkedIn
  cards per run were deterministic sponsored/ad exclusions; the dominant
  remaining failures were missing permalink, date, or author metadata. P08 is
  now blocked on Last30days retrieval and normalization, not Agent Browser
  readiness, authentication, or semantic quality filtering. The live retry
  budget is exhausted.
- Plan 0055 version 18/C18 fixture-accepts the Last30days-only retrieval
  repair. Explicit item-limited home-feed runs can use the existing eight-scroll
  ceiling, track canonical identities across virtualized snapshots, and stop
  after two no-progress snapshots. X and LinkedIn fixtures each pass an
  overlapping initial snapshot and reach 20 unique posts on scroll six;
  LinkedIn also recovers canonical activity URL, actor, and relative timestamp
  from current data/ARIA variants. The full repository suite passes. No
  service install or live provider attempt occurred, so installed and live
  20-item acceptance remain open and require fresh authority.
- Plan 0055 version 19/C19 installs exact service 0.3.61 with the repaired feed
  loop and retains 0.3.60 for rollback. The one authorized 20-item X plus
  LinkedIn tick failed before card observation: both attempts returned
  transient `agent_browser_error` and `0/0/0/0` counts, with no auth or page
  signal. Live scraper acceptance remains unproven; recurring configuration,
  profile state, Reddit/Facebook pause, and Agent Browser are unchanged.
- Plan 0055 version 20/C20 diagnoses the retained pre-observation failures
  without invoking Agent Browser or a provider. LinkedIn acquired its workspace
  and then failed its first authentication-stage `tab list`. X cannot be
  localized because its feed wrapper discards failure stage and command
  timings; the tick bridge also drops worker stage/signature for both sources.
  Deterministic replays reproduce both Last30days observability gaps, and exact
  installed/repository hashes exclude 0.3.61 release drift.
- Plan 0055 version 21/C21 fixture-accepts source candidate service 0.3.62.
  X feed failures now retain safe stage and bounded command operations, and
  the durable tick receipt preserves normalized worker stage plus stable
  SHA-256 signature. The complete suite and reproducible service build pass;
  installed service remains 0.3.61 and no provider attempt occurred.
- Plan 0055 version 22/C22 installs exact service 0.3.62 and consumes one
  combined single-attempt 20/20 feed tick. Both X and LinkedIn preserve the new
  safe failure stage/signature and the same `service/ok`, `service/ok`,
  `tab/failed` sequence at authentication. Neither source observed a card;
  20-item acceptance remains blocked on retained-session tab inventory rather
  than scraper content, ads, quality, authentication, or infinite scrolling.
- Plan 0055 version 23/C23 reproduces the exact Last30days route mismatch
  without a provider. Both services resolve to broker owner
  `handoff-17959ea3e226ee61`, which status advertises as ready but whose first
  command fails `runtime_lifecycle_existing_owner_requires_explicit_transition`.
  The configured session remains commandable and passes the existing safe
  exact-default-alias validator for both sources; simple concurrency is ruled
  out. No repair or live retry occurred.
- Plan 0055 version 24/C24 installs service 0.3.63 with the exact lifecycle-
  error alias fallback and consumes one combined 20/20 feed tick. Both lanes
  prove the fallback by moving from broker `tab/failed` to successful alias
  tab/eval operations, but the commandable alias has a different authentication
  state: X renders its login page and LinkedIn is unauthenticated without an
  operator ingress URL. No cards or rejection decisions were reached.
- Plan 0055 version 25/C25 installs service 0.3.64, removes the mismatched alias
  fallback, and proves the upgraded Agent Browser can list and select both feed
  tabs through its service queue on the exact authenticated broker browser.
  The combined 20/20 tick then fails before both authentication evaluations
  because the upgraded `evaluate` action requires a `serviceTabHandle`.
  Neither source observes or rejects a card; this is a Last30days contract-
  adoption gap, not auth, content quality, ad filtering, or infinite scrolling.
- Plan 0055 version 28/C28 installs service 0.3.68 after exactly three combined
  20/20 retries progressively expose the upgraded handle contract's response
  cap, new-tab readiness, and missed lifecycle-event race. All six provider
  attempts remain pre-observation. The final race-free readiness predicate is
  fixture-accepted but not live-accepted because the explicit retry budget is
  exhausted.
- Plan 0055 version 29/C29 consumes exactly one freshly authorized installed
  0.3.68 combined 20/20 tick. X acquires and releases its attributed tab, but
  Last30days' 20-second wrapper expires at the edge of an Agent Browser
  readiness `ui_action` that succeeds after about 18.6 seconds. LinkedIn
  acquires its attributed tab and completes readiness plus authentication
  evaluation, then its handle-bound navigation request is rejected before
  queueing because `waitUntil` is supplied as a forbidden top-level field.
  Both lanes remain pre-observation at `0/0/0/0`.
- Plan 0055 version 30/C30 installs service 0.3.69 and live-proves both C29
  repairs: X completes readiness within the enlarged wrapper and Agent Browser
  queues the schema-valid handle-bound navigation. The one authorized 20/20
  tick still observes zero cards. X ends `auth_state_ambiguous` after neither
  authenticated nor signed-out/challenge selectors match. LinkedIn ends
  `auth_required` from an unconfirmed authenticated-nav probe on blank rendered
  evidence, then exact release exposes contradictory logical-versus-physical
  browser IDs on its handle. These are retrieval/auth-probe and tab-attribution
  limitations, not logout proof or content-quality evidence.

Active Plan:

- `docs/dev/plans/0057-2026-08-29-semantic-sidecar-empty-media-repair.md`
  version 12/C12 is the active source-repair, installed-runtime, 20+20, and
  conditional 40+40 canary authority.

Closed Plan:

- `docs/dev/plans/0056-2026-08-25-x-linkedin-target-auth-reliability-repair.md`
  version 19/C19 is terminal and outcome-complete. Exact service 0.3.77 is
  installed ready with 0.3.76 retained. Tick
  `tick-b5c8a3b8b06e9103e581cdac8456ec67` proves successful X and LinkedIn
  collection lanes with 20 unique canonical posts each, zero model/cost,
  released leases, healthy SQLite, and no recurring-config or Agent Browser
  mutation.

- `docs/dev/plans/0055-2026-08-21-linkedin-accepted-yield-repair.md`
  version 31/C31 is terminal as superseded, not outcome-complete. It preserves
  the accepted-yield, feed-loop, attributed-control, install, and live-canary
  history through service 0.3.69. Its unmet X/LinkedIn 20/20 result and exact
  C30 route/auth blockers transfer unchanged to Plan 0056.

- `docs/dev/plans/0054-2026-08-20-x-accepted-yield-repair.md`
  version 5/C05 is the terminal X accepted-yield and authenticated retry
  authority. It proves 20 unique linked posts reached the bounded quality loop
  under service 0.3.53 and leaves recurring configuration unchanged.

- `docs/dev/plans/0053-2026-08-20-x-auth-alert-truthfulness.md`
  version 2/C02 is the terminal installed-runtime and X-only retry authority.

- `docs/dev/plans/0052-2026-08-16-operator-ingress-alert-runtime.md`
  version 2/C01 is the terminal alert-taxonomy authority. It installs exact
  service 0.3.51, retains 0.3.50 rollback, and proves the installed classifier
  without collection or browser effects.

- `docs/dev/plans/0051-2026-08-16-x-linkedin-20-post-live-canary.md`
  version 2/C02 is the terminal one-shot authority. It proves service 0.3.50
  installation and exact 20/20 preflight/enqueue bounds, but leaves scraper
  yield untested because retained browser/profile routing failed first.

- `docs/dev/plans/0050-2026-08-16-linkedin-literal-now-date-repair.md`
  version 2/C02 is the terminal extraction-repair and live acceptance
  authority. It changes only literal-now retention, installs service 0.3.48,
  and consumes exactly one receipt-only X/LinkedIn canary.

- `docs/dev/plans/0024-2026-08-06-governed-recurring-all-source-tick.md`
  version 12/C12 is the terminal P08 authority. It adds one config-driven
  service-owned scheduler and durable state, permits at most one automatic
  activation tick and five provider attempts (cumulative maximum 20/50), and
  forbids per-source/systemd timers, legacy spec enablement, catch-up fanout,
  cost/model use, Guacamole observation, or a second acquisition path.

- `docs/dev/plans/0047-2026-08-16-temporarily-disable-reddit-facebook-timer-lanes.md`
  version 1/C01 is the terminal operational successor for the exact temporary
  two-source pause. Re-enablement remains an explicit operator action.

- `docs/dev/plans/0048-2026-08-16-increase-x-linkedin-tick-volume.md`
  version 1/C01 is the terminal operational successor for higher recurring X
  and LinkedIn capacity. X and LinkedIn each have a ten-item ceiling;
  LinkedIn now uses topic/content search so the lane can return more than one
  company-profile record.

- `docs/dev/plans/0049-2026-08-16-x-linkedin-volume-live-canary.md`
  version 2/C02 is the terminal live-canary authority: one X and one LinkedIn
  attempt produced eight accepted records with truthful source-quality and
  derivative degradation receipts and no recurring-schedule mutation.

- S02's service 0.3.5/schema16 repository candidate passes the complete
  Python and Go suites plus compile/schema/manifest checks without live or
  private-config mutation; S03 exact commit `2e05b51` produces byte-identical
  artifact hash `efcbec6c58e9...`, and isolated lifecycle/rollback proof passes.
  Closed-world exact-candidate verification is `VERIFIED` with zero findings.
  Exact service 0.3.5/schema16 is installed disabled with rollback retained,
  SQLite healthy, and zero schedule/timer effects. The exact private daily
  schedule admitted one terminal `complete_degraded` Aug 5-6 tick at exactly
  20/50 cumulative attempts and promoted its snapshot. Restart two proves no
  duplicate work and exact Aug 7 continuity. Terminal verification is
  `VERIFIED` with zero findings, durable Graphiti readback passes, and the next
  ordinary daily boundary proves continued service-owned recurrence.

Dependencies:

- consumes P07/Plan 0023's terminal tick, installed lifecycle, rollback,
  immutable evidence, incident, derivative, and ordinary-query contracts;
- preserves P02's legacy scheduler only as historical evidence, not as the
  recurrence implementation for this lane.

Next Bounded Action:

- preserve the terminal retry while the Agent Browser owner repairs the
  access-plan/execution session-identity contradiction; another live 20+20
  attempt requires renewed bounded authority after that repair.

## P09 | Facebook Agent-Browser Timeout Remediation

State: CANCELLED

Objective: diagnose and repair the repeated Facebook `agent_browser_timeout`
that occurs before rendered-page evidence, while preserving P08's accepted
daily schedule, source set, browser identity, cost posture, and fail-closed
quality controls.

Current State:

- cancelled as superseded by P10/Plan 0026 after the bounded P09 proof reached
  `checkpoint_required` instead of `agent_browser_timeout`; P09 grants no
  further Facebook retry and routine handoff is governed only by P10;

- the latest five Facebook attempts are one `agent_browser_error` followed by
  four `agent_browser_timeout` results; the latest took 38 seconds with zero
  page signals and no rendered page;
- the retained canonical browser/profile is viable and still contains a
  Facebook search tab, while a read-only tab inventory takes about eight
  seconds;
- service and remote-view runtime checks are ready/converged; workstation
  payload provenance drift is visible but not proven causal;
- installed service 0.3.6 eliminated the stale-target `Page.enable` timeout in
  live proof, reached the requested search, and accepted one post, but its
  redundant extraction retries exhausted the 120-second worker wall budget;
- that proof is now consumed: auth and navigation commands returned, but the
  immediate post-navigation page-state evaluation timed out at 30.042 seconds;
  Plan 0025 remains open with the exact active-target reuse blocker;
- policy reread supersedes the overconservative C04 human-gate classification:
  S06 is one renewable same-envelope successor with one implementation and one
  zero-cost live proof.
- S06 fresh auth/query targets succeeded through query creation, but synchronous
  predecessor close timed out before page evaluation; S07 defers and bounds
  cleanup after page evidence so cleanup cannot mask a useful result.
- S07 repeated C04's post-query evaluation timeout even on a fresh direct query
  tab. S08 built service 0.3.11 with same-target navigation. After explicit
  operator approval, S09 installed it and consumed one proof; Facebook returned
  `checkpoint_required` during fresh-target authentication before navigation.
- Installed 0.3.11 is ready and the daily schedule is unchanged, but the
  repaired navigation path remains live-unproven. Agent-browser remote-control
  readiness is also blocked by duplicate-profile pressure and workstation-
  payload drift, so no operator handoff is currently claimed ready.

Closed Plan:

- `docs/dev/plans/0025-2026-08-07-facebook-agent-browser-timeout-remediation.md`
  version 14/C14 is the active authority. Installed 0.3.11 is ready with 0.3.10
  retained for rollback. Facebook checkpoint handling and agent-browser
  remote-view drift remediation are a new human gate.

Dependencies:

- consumes P08/Plan 0024's installed service-owned daily tick and must leave
  that recurrence contract unchanged;
- reuses the canonical `last30days-facebook` profile and retained shared
  browser without creating another browser or profile lane.

Next Bounded Action:

- preserve installed 0.3.11 and await explicit authority for a separate
  agent-browser remote-view repair plus literal Facebook checkpoint packet;
  only after operator completion may one post-checkpoint verification be
  derived.

## P11 | Facebook Governed Tick Navigation Recovery

State: CLOSED

Objective: complete Facebook through the ordinary governed manual tick after
explicit authentication when the selected retained target freezes during query
navigation.

Current State:

- manual tick `tick-848f61b8a22d7e603c7e473c16ba5fdf` completed
  `complete_degraded` with seven items and zero cost/model use;
- Facebook skipped two frozen targets and proved authentication on a responsive
  target, then navigation job `r198316` timed out after 25.787 seconds;
- the queue released and later browser commands succeeded. No auth incident,
  notification, browser launch, or tab close occurred.
- installed service 0.3.23 now recovers one frozen navigation, an all-frozen
  retained auth set, and one post-navigation page-state timeout inside the
  retained browser/profile;
- final manual tick `tick-771c7a87e4a65636047b83b478a0bd0e`
  completed the Facebook browser path, observed 18 candidates, and rejected all
  18 under the unchanged post-quality gate. It remained zero-cost with no human
  incident or notification, and retained PID 96078 stayed live.

Closed Plan:

- `docs/dev/plans/0027-2026-08-08-facebook-governed-tick-navigation-recovery.md`
  version 4/C04 is the terminal authority.

Next Bounded Action:

- preserve Plan 0027 as browser-recovery history. P12/Plan 0028 owns the
  disproven scraper-yield claim and must define live scrapable content before
  changing extraction or quality semantics.

## P12 | Facebook Live Content Model And Scraper Repair

State: CLOSED

Objective: define scrapable Facebook post content against the current retained,
authenticated site and repair the governed adapter until it accepts real posts
or proves a genuine empty result.

Current State:

- installed service 0.3.28/schema16 is ready with reproducible artifact SHA-256
  `d2718d01e4c1f0a0c431557008b23e4d5cb5d2294cdbea7a7588ce1e460e20d7`;
- governed manual tick `tick-f273eb12d642b31d49a7f12959b93b87`
  accepts Facebook: 19 observed, two accepted, 17 rejected, with exact bounded
  rejection counters and every browser operation successful;
- the authenticated canonical owner remains ready as PID 63205 on
  `session:last30days-facebook` with 17 tabs; no duplicate owner or tab closure
  occurred;
- complete validation passes with 2,600 tests, seven skips, six subtests, and
  reproducible build/install, manifest, authority, compile, and patch checks;
- X's separate 17-of-17 `out_of_range` quality rejection remains truthful
  nonblocking backlog and leaves the aggregate tick `complete_degraded` without
  weakening Facebook acceptance.

Closed Plan:

- `docs/dev/plans/0028-2026-08-08-facebook-live-content-model-and-scraper-repair.md`
  version 10/C10 is the terminal accepted authority.

Dependencies:

- consumes P11's retained-browser recovery and P08's governed manual-tick path;
- preserves the canonical authenticated profile, zero-cost posture, recurring
  schedule, and no-browser-lifecycle-mutation boundary.

Closeout:

- commit and push the accepted Plan 0028 slice. Treat X date-quality repair as
  a separate successor only if the operator prioritizes it.

## P13 | Facebook Routine Automation Qualification

State: CLOSED

Objective: qualify the repaired Facebook adapter for recurring unattended use
through the existing governed daily schedule, with bounded manual proof and
explicit fail-closed handling for authentication, challenge, rate-limit, and
content-integrity states.

Current State:

- installed 0.3.30 added source-scoped manual ticks, bounded organic rate-limit
  classification, and exact active-tab identity fallback when post-navigation
  Runtime evaluation is unavailable; its preflight predicts exactly one
  Facebook lane;
- the one authorized 0.3.29 qualification tick stopped fail-closed after two
  post-navigation page-state eval timeouts, with zero observed candidates and
  no auth, checkpoint, CAPTCHA, or rate-limit signal;
- both a five-second diagnostic and a 20-second production read-only Runtime
  evaluation of the existing search page timed out. The tested successor
  therefore proves navigation from exact URL/query/filter identity and defers
  content classification to extraction without treating URL state as auth or
  rate-limit proof;
- its sole successor tick failed at the isolated worker boundary after two
  bounded retained-tab switch timeouts, one fresh target, successful
  navigation/evaluations, and two scrolls. It staged no provider result and
  observed zero candidates; Plan 0029 is cancelled unsuccessfully;
- the sole guarded 0.3.31 tick preserved a typed transient
  `agent_browser_timeout` receipt but accepted zero posts and had no quality
  rejections. Exact active-tab identity bypassed the one fresh-target recovery,
  so extraction retried the same Runtime-unresponsive target;
- Plan 0030 is cancelled unsuccessfully. Plan 0031 closed after installing the
  bounded 0.3.32 repair that makes the first Runtime timeout use one fresh
  target;
- exact inventory found 16 Facebook targets among browser PID 63205's 19 tabs.
  Facebook cleanup was success-only and disabled same-site consolidation, so
  Plan 0032 now owns service 0.3.33 lifecycle repair and exact duplicate
  convergence before the live proof;
- 0.3.33 converged the live session to one Facebook target, but the sole proof
  ended as typed `worker_timeout` after 120 seconds with zero observed or
  quality-rejected candidates. Hard child termination bypassed its `finally`
  and left one new duplicate, which was manually reconverged. Plan 0032 now
  owned 0.3.34 parent-side timeout cleanup and closed unsuccessfully for live
  qualification;
- 0.3.35 installed exact-target replacement and a cumulative adapter budget.
  Its sole proof terminated in six seconds instead of the 120-second worker
  wall, but failed before Facebook page work because retained-owner selection
  ignored a live browser `cdpEndpoint` when its optional screencast viewer was
  unavailable and attempted an unnecessary remote-view launch;
- 0.3.36 repaired that acquisition decision while preserving exact alias,
  reciprocal-owner, ready-browser, and Facebook-target gates. Installed
  0.3.37/schema16 also types replacement-home-navigation timeouts consistently.
  A newly authorized three-attempt window then reached Facebook through the
  retained owner on every tick but produced no extraction: ticks
  `tick-6533102fc41c30e1227efceb3c1352d3`,
  `tick-ee4ebcb380a4afab75ab0860e14f2a32`, and
  `tick-55cdd0111fa36439694ae4c661bd7cfc` ended as two
  `agent_browser_timeout` results and one
  `facebook_target_unresponsive` result after 83-84 seconds each. All used one
  request with zero candidates, cost, model use, quality rejections, page
  signals, or auth/challenge/rate-limit evidence;
- Plan 0034 reproduced both terminal traces as deterministic budget failures.
  Installed 0.3.38 bounds navigation-only page-state evaluation, opens one
  recovery target directly at the verified URL, removes the redundant local
  wait, and defers same-site duplicate closure to guaranteed cleanup. The
  canonical suite passes 2,629 tests; a read-only direct CDP probe confirms the
  retained Facebook home target is complete and authenticated;
- final cleanup leaves PID 63205 ready with four intentional live tabs and one
  Facebook home target. Facebook remains manual and not routine-qualified;
  the three-attempt ceiling is exhausted and no fourth tick is authorized;
- Plan 0035 is the newly authorized one-attempt post-0.3.38 qualification.
  `daily-default` already contains an enabled Facebook target and calls the
  same coordinator/runner path as manual enqueue, so accepted content will
  qualify the existing recurring path without a schedule mutation or natural
  boundary wait;
- Plan 0035's sole tick ended before page inspection when a session tab
  inventory operation reached its fixed 10-second deadline at 10,025
  milliseconds. Three exact read-only repetitions succeeded in 8.4-8.8
  seconds, proving insufficient jitter margin while Facebook remained live;
- Plan 0036 owns a narrow 20-second read-only inventory allowance under the
  unchanged cumulative 75-second adapter budget, installed convergence, and
  one separately guarded content proof;
- Plan 0036 installed that repair as service 0.3.39 and cleared inventory and
  authentication, but its sole proof exposed a deeper boundary: the rendered
  Facebook search page is inventory-visible while commands routed into its
  attached CDP page session do not return;
- Plan 0037 owns the source-backed agent-browser page-session investigation,
  and its three adaptive downstream proofs are now exhausted. Installed
  0.3.40 isolated the renderer, 0.3.41 moved to posts-only search, and 0.3.42
  reduced recovery to one mobile composite capture; every rendered Facebook
  search target still stopped answering page-session Runtime commands. The
  exact upstream handoff is maintained in the agent-browser repository;
- agent-browser code commit `5ecb4d62` is now installed and converged with
  renderer-side Runtime deadlines, browser-level navigation metadata,
  response-before-health delivery, and faster same-inode CLI dispatch.
  Last30Days 0.3.43 is installed ready with rollback 0.3.42 preserved:
  navigation uses a 25-second inner job deadline beneath a 30-second outer
  deadline, and the canonical suite passes 2,638 tests. The schedule,
  databases, and retained four-tab browser are healthy. No fourth provider
  attempt was consumed;
- newly authorized tick `tick-10a32ce87a38790b8894ed9ab2ec2435`
  completed through the existing Facebook daily target: five posts observed,
  two accepted, three rejected, three requests, 32 seconds, zero cost/model
  use, no fallback, and no auth/challenge/CAPTCHA/rate-limit/integrity signal;
- both accepted posts carry high-confidence `2026-08-10` dates, canonical
  permalinks, authors, immutable source/version provenance, and promoted
  snapshot `tick-snapshot-edacb2efdce06eaf2def9d41607d1c20`;
- `daily-default` remains enabled/ready at 86,400 seconds with next boundary
  `2026-08-11T00:00:00Z`; current and rollback databases are healthy, and PID
  63205 remains ready with exactly four live tabs, one Facebook tab, and no
  active challenge, job, or lease. Facebook routine automation is qualified.

Closed Plan:

- `docs/dev/plans/0037-2026-08-09-facebook-page-session-cdp-readability.md`
  closed at version 5/C12 after the upstream repair, installed convergence,
  and one bounded routine-automation proof all passed.

Closed Repair Plan:

- `docs/dev/plans/0034-2026-08-09-facebook-post-navigation-target-loss-repair.md`
  closed at version 3/C03 after installing service 0.3.38. Plan 0033 closed at
  version 5/C05 with the exact three-attempt blocker; any later live proof
  remains a separate human gate with a new explicit attempt ceiling.
- `docs/dev/plans/0035-2026-08-09-facebook-routine-automation-qualification.md`
  closed at version 3/C03 after its one authorized tick isolated the inventory
  deadline blocker without accepted content.
- `docs/dev/plans/0036-2026-08-09-facebook-tab-inventory-latency-repair.md`
  closed at version 3/C03 after installed 0.3.39 cleared inventory and its sole
  tick isolated the Facebook CDP page-session blocker.

Dependencies:

- consumes P12's accepted content model and P08's governed manual tick;
- preserves P10's human reauthentication workflow, the existing recurring
  schedule, canonical retained browser/profile, and zero-cost posture.

Closeout:

- retain ordinary `daily-default` operation. Repair the installed MCP
  adapter's schema-16 compatibility in a separate client-contract maintenance
  slice; it did not affect the direct installed-service acceptance proof.

## P14 | MCP Schema-16 Adapter Convergence

State: CLOSED

Objective: restore the installed MCP handshake for service schema 16 and make
future adapter contract changes fail closed unless they receive a new,
explicitly bound adapter release identity.

Current State:

- installed adapter 4.0.2 now advertises schema 16-16 and returns `compatible`
  against ready service 0.3.43/schema 16;
- the release lock preserves 4.0.1/schema-15 history and binds 4.0.2 to the
  exact schema-16 catalog digest and service/database ranges;
- contract generation and installation fail closed on a missing, duplicate,
  or mismatched current release identity;
- a fresh installed `maintenance_status` read succeeds. Existing connector
  processes retain their old process image until session/connector restart;
  service, schedule, databases, browser state, and acquisition were unchanged.

Closed Plan:

- `docs/dev/plans/0038-2026-08-10-mcp-schema16-adapter-convergence.md`

Dependencies:

- consumes P13's exact incompatible discovery receipt and preserves service
  0.3.43, database schema 16, recurring schedule, and browser state.

Closeout:

- Plan 0038 closed at version 3/C03. Installed binary SHA-256
  `4336d24aedf067a54745407b9e8a1dfe2280c0ce1ea17f3f81efef9f8de5ebbc`
  reports adapter 4.0.2, `compatible`, schema 16-16, and admits
  `maintenance_status` through a fresh process.

## P15 | X Retrieval Identity And Cache Repair

State: CLOSED

Objective: make authenticated X collection retain stable status-level
provenance and remain retrievable through a profile-authorized cache-only MCP
query after unrelated source-only head promotion.

Current State:

- implementation commit `6a77d4823e43580f677415ecbd1e914110f3fccb`
  is pushed; service 0.3.44/schema 16 and MCP 4.0.3 are installed, compatible,
  and bind the canonical contract digest;
- stable X status identity, exact rejection accounting, source-aware terminal
  snapshot selection, partition-safe retrieval, and profile-aware query and
  refresh pass the complete candidate gate and fresh review;
- the one authorized X tick ended `complete_degraded` with retained
  `agent_browser_error`, zero browser operations/page signals, and no retry.
  Its promoted `x=failure` snapshot is the exact cache-only query target, which
  returns zero evidence plus an X coverage gap instead of stale prior results;
- runtime, schedule, browser lease, current database, and rollback database
  closeout readbacks are healthy. Plan 0039 closes at version 4/C04; a future
  live retry or browser repair is a separately authorized successor.

Closed Plan:

- `docs/dev/plans/0039-2026-08-10-x-retrieval-identity-and-cache-repair.md`

Dependencies:

- consumes P08's durable tick/query substrate, P13's installed service, and
  P14's release-lock discipline while preserving schema 16 and the existing
  retained browser/profile lane.

Closeout:

- Plan 0039 closed at version 4/C04. The exact implementation, installation,
  live terminal receipt, no-retry decision, and remaining browser-source
  blocker are recorded there and in RUNBOOK Turn 267.

## P16 | X Agent-Browser Boundary Recovery

State: CLOSED

Objective: recover the exact last30days-to-agent-browser X boundary and consume
at most one tested, profile-safe X acceptance attempt.

Current State:

- the agent-browser process-identity repair is installed and the stale PID
  replay now reports the historical browser as non-live;
- MCP adapter 4.0.3 is compatible with installed service 0.3.44/schema 16;
- Plan 0040's sole acceptance tick completed successfully with three accepted
  X items, no retry or fallback, and a promoted named-profile snapshot;
- current and rollback databases pass integrity checks, the recurring schedule
  is unchanged, and the authenticated profile remains live with an available
  lease and no waiter.

Active Plan:

- `docs/dev/plans/0040-2026-08-10-x-agent-browser-boundary-recovery.md`

Dependencies:

- consumes P15's stable X identity, exact rejection accounting, source-aware
  query behavior, and retained failure receipt while preserving P08/P13/P14
  service, schema, release-lock, and schedule contracts.

Closeout:

- Plan 0040 closed at version 3/C03. The installed identities, single live
  receipt, cache-only proof, and operational reconciliation are recorded there
  and in RUNBOOK Turn 270.

## P17 | Facebook Cross-Source Browser Handoff Repair

State: CLOSED

Objective: make the recurring X-to-Facebook sequence reconcile a late-completed
service operation to the one retained authenticated social browser instead of
recording a false failure at the CLI wait deadline.

Current State:

- the daily tick's X lane succeeded, then Facebook failed before page
  inspection after a 39.676-second remote-view operation;
- the retained browser and authenticated Facebook result page are healthy, so
  credentials and page usability are not the broken boundary;
- the first red fixture disproved the default-profile alias hypothesis: that
  path already returns the X-owned browser. A replacement red replay proved
  the adapter re-raises a failed remote-view waiter even when the next service
  status contains the exact ready browser;
- source now reserves ten seconds for one read-only status reconciliation,
  accepts only an exact ready retained owner, and performs no retry or relaunch;
- service 0.3.45 is installed from pushed commit `150b9d7`; the late
  reconciliation repair moved the sole acceptance attempt past acquisition,
  retained-browser reuse, tab inventory, target replacement, and navigation;
- the tick then failed at the 25-second combined capture deadline after 26.708
  seconds. Plan 0041 closed without retry and transferred only that newly
  exposed deadline mismatch to P18/Plan 0042.

Closed Plan:

- `docs/dev/plans/0041-2026-08-10-facebook-cross-source-browser-handoff-repair.md`

Dependencies:

- consumes P16's installed agent-browser identity repair and P08/P13/P14's
  durable tick, service, schema, release-lock, and schedule contracts while
  preserving the single authenticated social profile lane.

Closeout:

- Plan 0041 closed at version 4/C04 with installed acquisition blocker
  reduction and an exact terminal capture failure.

## P18 | Facebook Combined Capture Deadline Repair

State: CLOSED

Objective: allocate the existing 105/120-second Facebook adapter/parent budget
to the one combined replacement-page capture without adding commands, targets,
retries, or browser/profile effects.

Current State:

- exact pushed commit `321a4807` is installed as service 0.3.46 and MCP 4.0.3
  is ready/compatible at schema 16;
- the 45/50 deadline change passed all source gates, but the sole installed
  tick `tick-9262e44d7769b0b0146e7c82cb3d6e38` completed degraded after 54
  seconds with the final eval failing at 31.810 seconds and zero evidence;
- the tick was not retried. Databases, recurring schedule, retained profile,
  installed service, and Git remain safe and reconciled.

Closed Plan:

- `docs/dev/plans/0042-2026-08-10-facebook-combined-capture-deadline-repair.md`

Dependencies:

- consumes P17's installed late-acquisition reconciliation and the existing
  one-successor/single-capture contracts without changing browser ownership or
  parent resource ceilings.

Closeout:

- Plan 0042 closed at version 4/C04 with a terminal acceptance failure and no
  authorized retry or further autonomous successor at the same invariant.

## P22 | Facebook Retained Browser Runtime Recovery

State: OPEN

Objective: after explicit operator authority, perform one controlled restart
of the retained Facebook browser on its existing profile/current build, prove
Facebook target and input responsiveness before provider work, then permit at
most one acceptance tick and named-profile cache proof.

Current State:

- the operator-authorized same-profile/current-build restart succeeded as one
  replacement browser, PID 83786, on the retained profile and current build;
- Chrome restored exactly X, LinkedIn, and preview. A fresh Facebook target
  opened and settled, but read-only evaluation job `r791343` timed out at the
  exact 10-second worker boundary;
- fail-closed handling stopped before scroll, provider preflight, or tick and
  closed only the Facebook target. The three unrelated targets, live browser,
  databases, schedule, service, and repository remain safe; accepted Facebook
  evidence and named-profile cache proof remain unmet;
- direct agent-browser inspection now proves the Facebook renderer reaches an
  “Aw, Snap!” crash with `SIGSEGV`. Browser-level network and target commands
  continue, but renderer-facing commands hang; agent-browser incorrectly keeps
  the crashed tab `ready` and records no crash event or incident;
- a bounded matrix now shows both filtered and unfiltered authenticated
  `/search/posts/` crash before renderer commands, while Facebook home works on
  the same retained profile and a clean unauthenticated profile works on the
  same build. The remaining fault boundary is authenticated posts-search plus
  retained site state/build interaction, not the filter or generic CDP path;
- retained Chromium stderr identifies Blink `line_breaker.cc:4102` DCHECK
  aborts as the direct renderer failure. Final reconciliation then found PID
  83786 and port 39488 gone, and a nominal inventory read attached the Facebook
  session name to a default-profile browser. That association was invalid and
  no recovery was attempted;
- the operator-authorized Chromium successor installed Chromium 153 artifact
  `153.0.8003.0+stealthcdp.86aec912997e`. Exact preflight and process proof now
  bind retained profile/session `last30days-facebook` and PID 39672 to that
  artifact. One filtered authenticated search reached its Facebook title but
  aborted at a new Blink `inline_item_result.cc:55` consistency DCHECK
  (`222 vs. 3`); agent-browser again reported only a probe timeout. The exact
  failed tab was closed, the retained browser and unrelated tabs remain live,
  and no provider or tick ran.
- the later ordinary Aug 15-16 timer completed its Facebook browser operations,
  observed 11 candidates, and rejected all at the unchanged quality gate. The
  operator then requested Facebook and Reddit be disabled for now; Plan 0047
  applied that exact source pause without changing daily cadence or admitting
  a transition tick.

Active Plan:

- `docs/dev/plans/0046-2026-08-11-facebook-retained-browser-runtime-recovery.md`

Dependencies:

- consumes P21's exact terminal receipts and preserves the current service,
  profile, build, schedule, source, data, and cost boundaries.

Next Action:

- Plan 0046 remains open but operator-paused at version 8/C08 in
  `facebook_timer_lane_temporarily_disabled`. Do not repair, re-enable, or run
  another Facebook acceptance attempt until the operator explicitly resumes
  this lane; when resumed, re-anchor to the latest quality-gate result before
  choosing browser versus extraction work.

## P21 | Facebook Stale Prepared Extraction Refresh

State: CLOSED

Objective: refresh an empty immediate prepared query extraction after the
configured settle wait before deciding whether Facebook scrolling is needed,
then prove one installed tick publishes and serves accepted evidence.

Current State:

- exact pushed commit `6ed4b784` remains installed ready/compatible as service
  0.3.47, and its focused stale-empty-capture regression plus all source,
  package, and runtime gates pass;
- sole tick `tick-3b374c8eaa1811b8d3eec1bdcec51d37` completed degraded after
  the replacement page opened and evaluated successfully but selectorless
  scroll timed out after 30.042 seconds. It consumed one attempt, one request,
  and 46 wall seconds with zero evidence and was not retried;
- browser-preserving handoff and a fresh disposable same-profile target proved
  Facebook target control remains unresponsive while the browser endpoint,
  profile, unrelated targets, and active preview evaluation remain healthy;
- the repeated-no-progress bound fired across the Plan 0110 live scroll proof
  and the sole Plan 0044 and Plan 0045 ticks. Accepted evidence and the named
  cache proof remain unmet.

Closed Plan:

- `docs/dev/plans/0045-2026-08-11-facebook-stale-prepared-extraction-refresh.md`

Dependencies:

- preserves P17-P20's acquisition, deadline, retained-browser, and generic
  scroll contracts; changes only Last30Days prepared extraction freshness.

Next Action:

- Plan 0046/P22 records the bounded same-profile restart strategy at a human
  gate. Do not perform it or enqueue another tick without explicit authority.

## P20 | Agent Browser CDP Input Scroll Repair

State: CLOSED

Objective: move selectorless page scrolling from renderer JavaScript to
browser-level CDP input-wheel delivery, then prove one installed Facebook tick
publishes and serves accepted evidence.

Current State:

- exact agent-browser commit `a954bc95` passed focused, real-Chrome, and
  canonical Rust gates and installed as SHA-256
  `76b2779ffc65d85f22817c698732e387dffe9cd4f8225f9aaf6b65bba467d3d1`;
- the one live tick reached `Input.dispatchMouseEvent`, which the Facebook
  target did not acknowledge while browser inventory stayed healthy;
- Last30Days source diagnosis identified the stale empty prepared query capture
  that forces this unnecessary scroll; P21 now owns the remaining acceptance.

Closed Plan:

- `docs/dev/plans/0044-2026-08-11-agent-browser-cdp-input-scroll-repair.md`

Closeout:

- Plan 0044 closed at version 2/C03 with a valid installed generic scroll
  repair and a distinct Last30Days upstream stale-read blocker.

## P19 | Agent Browser Eval Budget Propagation Repair

State: CLOSED

Objective: propagate a positive global agent-browser evaluation job deadline
through both Chromium's renderer and the CDP transport, then prove one installed
Facebook tick publishes accepted evidence.

Current State:

- exact agent-browser commit `1c1331ef` passed all required gates and installed
  as SHA-256 `071b7a6e3e58c87f3fd1decaaeb40d691f666a7d8f311894e4f30558c233bbf2`
  without replacing Facebook browser PID 13177 or its targets;
- the one bounded tick exercised the repaired evaluation successfully and then
  stopped on the distinct selectorless scroll failure now owned by P20;
- the tick is terminal, was not retried, and produced no accepted evidence or
  cache-success claim.

Closed Plan:

- `docs/dev/plans/0043-2026-08-11-agent-browser-eval-budget-propagation-repair.md`

Dependencies:

- consumed P17-P18 and agent-browser P109 without changing their retained-state
  contracts.

Closeout:

- Plan 0043 closed at version 3/C03 with verified deadline blocker reduction
  and a distinct successor scroll owner.

## P10 | Recurring Browser Reauthentication Notifications

State: CLOSED

Objective: treat browser authentication expiry as an ordinary governed
operating state by preparing a verified agent-browser handoff and sending the
operator a safe actionable link through the configured notification chain.

Current State:

- service 0.3.13/schema16 is installed ready and carries safe external
  operator links through the existing incident/reminder/resolution chain;
- default-tenant Slack `@eric` delivery is proven by one labeled validation
  receipt, while schedule, database, rollback, and zero-cost invariants hold;
- installed service 0.3.20/schema16 repairs checkpoint taxonomy,
  authenticated-feed false positives, direct-first DOM extraction, command
  timeout layering, deferred operator-view acquisition, and frozen retained-tab
  selection. The final proof navigated and extracted without a human incident
  or browser timeout, then returned a truthful content-quality result.
- the later governed manual tick confirmed false auth remained repaired but
  exposed a successor query-navigation timeout now owned by P11/Plan 0027.

Open Plan:

- `docs/dev/plans/0026-2026-08-07-recurring-browser-reauthentication-notifications.md`
  version 12/C12 is closed with service 0.3.20 installed and the bounded
  Facebook proof complete.

Dependencies:

- preserves P08's daily schedule and consumes P09's verified Facebook
  checkpoint evidence without retrying Facebook acquisition;
- uses child-owned Slack Receipts and the canonical agent-browser
  `last30days-facebook` retained profile/browser lane.

Next Bounded Action:

- let the normal daily schedule consume service 0.3.20. Treat a future login or
  checkpoint notice as valid only when a bounded responsive probe supplies
  explicit human-gate evidence.

## P23 | Reddit Home Feed Scraper

State: CLOSED

Objective: add a deterministic authenticated Reddit home-feed scraper that
collects 80 unique canonical posts while preserving topic search and excluding
only explicit ads and platform-marked spam as content-quality decisions.

Current State:

- Plan 0063 version 15/C15 is outcome-complete. Installed service 0.3.109
  retains Reddit topic search and adds deterministic authenticated home-feed
  acquisition with exact-profile planning, canonical links, finite scrolling,
  and explicit ad/spam, structural, date-scope, duplicate, and scroll-progress
  diagnostics;
- run `collection-run-a5ace8c0bc857b17b1936245b21b17aa`, job
  `3c7a87f3-bc88-48e0-8cc4-39816aa11888`, proves 80 accepted, stored, and
  indexed posts from the authenticated feed. All 80 canonical URLs and their
  URL-derived Reddit IDs are distinct;
- the scraper reached the accepted limit after 25 document-progress scrolls
  with zero no-progress scrolls, structural limitations, date exclusions, or
  content-quality rejections. Exact service-tab release succeeded, the retained
  browser is healthy/reusable, active profile leases are zero, and SQLite
  integrity is `ok`;
- all 22 Reddit collection specifications remain disabled and `daily-default`
  was not changed. The comprehensive repository lane passes with 2,755 tests,
  seven expected skips, and nine passing subtests.

Active Plan:

- none; Plan 0063/C15 satisfied the authenticated 80-item Reddit home-feed
  objective and closed the lane.

Closed Plan:

- `docs/dev/plans/0063-2026-09-02-reddit-home-feed-scraper.md`
  version 15/C15 is terminal and outcome-complete on installed service 0.3.109.

Dependencies:

- consumes the published Agent Browser session-recovery fixes on
  `fix/tick-restart-recovery` without changing P08's schedule acceptance;
- preserves existing Reddit topic search and source-access policy.

Next Action:

- none for P23. Adding Reddit to a recurring schedule remains separate future
  scope and requires an explicit plan and authorization.

## P24 | Recurring Reddit Home Feed

State: OPEN

Objective: activate the proven authenticated Reddit home-feed adapter on the
existing `daily-default` schedule for up to 80 unique canonical posts per
ordinary tick.

Current State:

- Plan 0063/C15 proved 80 accepted/stored/indexed Reddit feed posts on installed
  service 0.3.109;
- the operator explicitly authorized recurring Reddit activation;
- `daily-default` is enabled and ready for `2026-09-04T00:00:00Z` with Reddit
  active at 80 items, three transient-only attempts, and 360 seconds per
  attempt;
- saved revision `operator-20260903-reddit-home-feed-80-v1` passed installed
  preflight and exact post-restart readback with four enabled lanes and
  aggregate limits 243/10/500/3,360;
- the one-row digest rebind preserved schedule/tick identity, admitted no work,
  and left all active-work and lease counts zero with SQLite integrity `ok`.
- manual tick `tick-98e14987fc5e9a7b7b63f8b8ea1abb95` proved Reddit and
  LinkedIn at 80 distinct linked posts each on their first attempts, plus three
  YouTube items; X alone failed before observation on all three retries with
  `existing_session_profile_identity_unproven`;
- the manual tick promoted its degraded snapshot and left the recurring
  schedule, database integrity, and all active-work/lease counters healthy.

Active Plan:

- `docs/dev/plans/0064-2026-09-03-recurring-reddit-home-feed.md` version 3/C03.

Dependencies:

- depends on closed P23/Plan 0063 installed Reddit feed acceptance;
- runs alongside P08 without changing its X/LinkedIn implementation branch or
  adjudicating its remaining ordinary-tick failures.

Next Action:

- observe the first ordinary four-lane tick after the September 4 UTC boundary
  and adjudicate its terminal Reddit provider receipt.

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
