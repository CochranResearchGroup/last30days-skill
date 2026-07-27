# last30days Product Roadmap

Authority: this file is the canonical product direction, priority map, and lane
catalog. Detailed execution lives under `docs/dev/plans/`; dated work and
decisions live in `RUNBOOK.md`.

## Product Objective

Build a user-scoped, continuously hydrated intelligence service that acquires
posts and profile pages from authenticated and public sources, preserves their
provenance and temporal history, resolves people, organizations, topics, and
events, and answers coherent citation-ready questions without exposing browser
or scraping mechanics to normal agents. Deterministic supervisors own
collection, state, budgets, validation, and publication; bounded App
Intelligence workers assess evidence, propose identity and claim associations,
and diagnose or repair adapters.

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
roadmap. P01-P06 remain roadmap lanes; only P03 currently has an actionable
open plan, while the other successor lanes are planned. No recurring
authenticated timer was enabled by closeout.

## Successor Implementation Queue | 2026-07-26 Review

The roadmap review converts the post-reboot handoff priorities into bounded
successor plans without reopening Plans 0010 or 0011:

1. `docs/dev/plans/0012-2026-07-26-post-reboot-social-route-canary.md`
   is the `OPEN` critical path. Its authorized 2026-07-27 execution stopped
   fail-closed at the first route preflight because no display allocation or
   available route-pool entry could be selected. Follow-up diagnosis proved
   that Guacamole PostgreSQL reinitialized with zero connection fixtures and
   that the recurring agent-browser interlock has no remedy for the resulting
   provisioning action. Agent-browser P78/Plan 0078 is the separately
   authorization-gated repair packet. No browser or canary was created.
2. `docs/dev/plans/0013-2026-07-26-youtube-transcript-media-acceptance.md`
   is the planned YouTube transcript, bounded media, downstream handoff, and
   cleanup acceptance packet.
3. `docs/dev/plans/0014-2026-07-26-recurring-collection-timer-durability.md`
   is the planned two-interval public-source timer/restart/pause proof.
4. `docs/dev/plans/0015-2026-07-26-temporal-retrieval-graphrag-resilience.md`
   is the planned cache-only temporal/profile and GraphRAG degradation packet,
   supporting both P04 and P05.
5. `docs/dev/plans/0016-2026-07-26-app-intelligence-contract-acceptance.md`
   is the planned accepted/rejected envelope and deterministic replay packet.
6. `docs/dev/plans/0017-2026-07-26-canonical-profile-selection-regression.md`
   is the planned identity-first, ambiguity-safe profile-selection regression
   packet.

The plans are ordered, not jointly authorized. Only Plan 0012 is actionable,
and its live runtime mutation remains separately operator-gated. Plans
0013-0017 stay `PLANNED` until the preceding critical-path result is reconciled
and the next packet is explicitly opened. P01 receives no new implementation
packet in this review because the current acceptance gaps exercise its existing
immutable evidence authority rather than establish a verified new foundation
defect.

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
  is the planned public-source two-interval restart and pause proof.

## P03 | Profile And Identity Acquisition

State: OPEN

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
  is the open serialized route/auth/acquisition acceptance plan, currently
  blocked at its route-recovery gate.
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
  is the planned cache-only retrieval, projection replay, and local-evidence
  fallback acceptance packet.

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
  also owns the planned fresh-client cache-only product acceptance proof.

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
  is the planned accepted/rejected envelope and deterministic replay proof.

Next Bounded Action:

- Complete or truthfully block Plan 0012 before opening Plan 0013. Preserve the
  deterministic joins and do not reopen Plans 0010 or 0011.

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
