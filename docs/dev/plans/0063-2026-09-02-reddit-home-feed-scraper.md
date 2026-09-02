# Plan 0063 | Reddit Home Feed Scraper

State: OPEN
Lane: P23
Branch: feat/reddit-home-feed
Target: main
Integration: fast-forward
Roadmap: P23
Plan version: 4
Date: 2026-09-02

## Objective

Add a deterministic Agent Browser scraper for the authenticated Reddit home
feed that can collect 80 unique canonical posts without applying topic-quality
filtering, while preserving the existing Reddit search capability.

## Current State

- `RedditBrowserScraper.search` is limited to Reddit `/search`, caps each DOM
  snapshot at 80 candidates, stops scrolling when raw candidate count reaches
  the requested limit, and applies query-term relevance gates;
- the service acquisition worker already distinguishes `surface_kind=feed` for
  X and LinkedIn but sends every Reddit request through the search access-order
  path;
- prior live Reddit proof established bounded execution and truthful zero-yield
  observability, not successful post retrieval;
- Reddit remains disabled in `daily-default`, and this plan does not enable or
  otherwise mutate that schedule.

## Scope

- introduce a `scrape_reddit_feed` interface beside `search_reddit_browser`;
- route only Reddit `surface_kind=feed` requests to that interface;
- use the existing configured `last30days-facebook` protected profile and the
  shared Agent Browser acquisition module;
- navigate the authenticated Reddit home feed, inspect its rendered DOM, and
  accumulate unique post observations across bounded infinite scrolling;
- canonicalize `/comments/<id>/...` post URLs and preserve legitimate posts
  without topical relevance filtering;
- deterministically exclude Reddit-labeled promoted advertisements and posts
  explicitly marked by Reddit as spam or removed by platform filters;
- classify malformed links, missing timestamps, and unsupported DOM shapes as
  scraper limitations in diagnostics rather than as off-topic content;
- retain date-window enforcement as collection scope rather than quality
  scoring;
- add focused public-interface and worker-routing regressions, then validate,
  package, install, and run one bounded live acceptance campaign.

## Non-Goals

- enabling Reddit in any recurring schedule;
- replacing, weakening, or removing Reddit topic search;
- semantic relevance, ranking, GraphRAG, or subjective quality filtering;
- creating or replacing browser profiles, changing credentials, or inspecting
  unrelated tabs;
- provider writes, votes, comments, subscriptions, or other Reddit mutations;
- changing X, LinkedIn, Facebook, or YouTube acquisition behavior.

## Acceptance Criteria

1. A Reddit feed request reaches `scrape_reddit_feed`; a Reddit topic request
   continues through the existing access-order search path.
2. The public feed interface navigates a verified Reddit home-feed URL and
   returns structurally normalized posts with unique canonical Reddit
   permalinks.
3. Feed acceptance has no topic-overlap gate. It rejects only explicit ads or
   platform-marked spam as content-quality decisions; structural and date
   failures remain separately diagnosed.
4. Infinite-scroll collection deduplicates observations across virtualized DOM
   snapshots, stops after reaching 80 accepted unique posts or a deterministic
   stagnation/scroll/deadline bound, and reports yield and rejection counters.
5. Existing Reddit search regressions remain green and retain their search
   relevance semantics.
6. The full relevant source, worker, contract, packaging, and release suites
   pass; the install artifact is reproducible and the installed service is
   ready on its expected schema.
7. One live campaign uses no more than three Reddit acquisition attempts and
   proves 80 unique canonical posts, or terminates with a typed receipt that
   identifies the exact remaining scraper/provider limitation.
8. After live proof, active work, provider attempts, browser resource leases,
   and database integrity reconcile cleanly; `daily-default` still has Reddit
   disabled.

## Execution Packets

### Packet A | Feed Interface Tracer Bullet

- add one failing public-interface test for a real unrelated Reddit home-feed
  post and make it pass without touching search behavior;
- terminal condition: feed navigation and one canonical item work through the
  new interface.

### Packet B | Deterministic Infinite Scroll And Exclusions

- add one behavior test at a time for cross-snapshot dedupe, promoted/platform
  spam exclusion, structural limitation diagnostics, stagnation, and the
  80-item bound;
- terminal condition: focused Reddit tests pass and search remains unchanged.

### Packet C | Service Routing And Release Candidate

- route Reddit feed work at the acquisition seam, update consumer-facing
  configuration documentation only if a knob changes, run focused then broad
  validation, and build/install the next patch release;
- terminal condition: exact installed runtime identity is ready and matches
  the validated source artifact.

### Packet D | Bounded Live Proof

- inspect only the Reddit surface in the existing configured profile, run at
  most three attempts for one 80-item feed campaign, and reconcile durable
  receipts and cleanup;
- terminal condition: 80 unique canonical posts are proven or a typed terminal
  blocker is recorded without enabling the timer.

## Ownership And Bounds

- critical-path owner: primary Codex agent;
- parallel work: none; current orchestration policy prohibits delegation;
- owned code surfaces:
  `skills/last30days/scripts/lib/reddit_browser.py`,
  `skills/last30days/scripts/lib/service_acquisition_worker.py`, and their
  focused tests;
- owned authority surfaces: this plan, P23 in `ROADMAP.md`, the chronological
  `RUNBOOK.md` entry, and the P23 active-lane registration;
- live bounds: one exact profile, one provider, 80 requested items, three total
  acquisition attempts, no schedule enablement, no provider mutation;
- review bound: one primary review and one closed-world remediation pass for
  accepted blocking findings;
- stop conditions: acceptance met, operator authentication is genuinely
  required, the exact profile cannot be safely acquired, or remaining work
  would expand beyond Reddit feed retrieval.

## Definition Of Done

The installed service can retrieve 80 unique canonical posts from the Reddit
home feed within the approved bounds, retains Reddit search, truthfully records
ads/spam and scraper limitations, leaves the recurring Reddit lane disabled,
and publishes source, test, install, live-receipt, cleanup, and plan/runbook
evidence.

### Checkpoint P0063-C01 | 2026-09-02

Plan version: 1

State: `authorized_plan_opened`

Progress classification: `acceptance_progress`

Authority classification:

- `scope_expansion`; the operator approved the proposed feed interface,
  existing configured profile, deterministic exclusions, 80-item live proof,
  and three-attempt bound.

Evidence:

- current source and CodeGraph show Reddit has only a topic-search browser path,
  while X and LinkedIn already route `surface_kind=feed` to dedicated methods;
- exact Graphiti episodes confirm prior Reddit work proved relevance semantics
  and healthy-zero execution, not successful content retrieval;
- branch `feat/reddit-home-feed` is isolated at base `f5a191a` so the still-open
  P08 scheduled-tick gate remains unchanged.

Subagent status: `not_spawned`.

Graphiti write status: `pending`; defer the required compact write until the
first validated implementation checkpoint rather than storing plan-only churn.

Next action: execute Packet A with one red/green public-interface test for an
unrelated legitimate home-feed post and its canonical permalink.

### Checkpoint P0063-C02 | 2026-09-02

Plan version: 2

State: `release_candidate_validated_live_retry_exhausted`

Progress classification: `acceptance_progress`

Authority classification:

- `inherited_authority`; implementation, validation, packaging, and the three
  live attempts stayed inside the approved Reddit-only profile, item, attempt,
  and no-schedule-mutation bounds.

Evidence:

- commit `dc7a10e0510a4674201accb963d23ea7a9640bb7` adds direct Reddit
  `surface_kind=feed` dispatch, authenticated home-feed navigation, canonical
  permalink normalization, virtualized cross-snapshot deduplication, finite
  100-item/40-scroll/three-stagnant-snapshot bounds, and separate ad/spam,
  structural-limitation, date-scope, and duplicate diagnostics;
- feed acquisition uses the exact `last30days-facebook` profile with a
  `local_headless` CDP posture, so ordinary retrieval does not depend on an
  RDP/Xvfb presentation route. Topic search retains its prior public-first
  access order and relevance semantics;
- focused Reddit, acquisition-worker, plan-authority, release, and runtime-
  package suites pass. The broad suite excluding the known MCP fixture teardown
  timeout passes with 2,746 tests, seven skips, and nine subtests; MCP Go tests,
  Python compilation, authority audit, manifest refresh, reproducible build,
  and `git diff --check` pass;
- service artifact `last30days-service-0.3.97.tar.gz` has SHA-256
  `afbf6338cc2fa67fed284d9fc424a0beb2491496f0c6cf520a8428d73aaa071b`;
- live attempt 1 stopped before tab acquisition because Chrome PID 84749 held
  the exact profile but was absent from Agent Browser service ownership;
  supported exact-session close released that blank/new-tab-only process;
- live attempt 2 stopped before Chrome because a stale protected Xvfb process
  on display `:90` caused three internal remote-headed launch failures;
- live attempt 3 used the corrected local-headless posture, acquired the exact
  profile, passed the bounded authentication probe, and navigated to
  `https://www.reddit.com/`, but the old 2.5-second page probe observed no post
  cards and returned `navigation_mismatch`;
- the final offline remediation now waits deterministically for asynchronous
  post cards for up to 11 seconds and has a red/green regression. The agreed
  three-attempt live budget is exhausted, so 80-item proof remains pending;
- exact attempt cleanup closed the cold-launched browser and runtime status
  reports no live browser or profile lock. No timer, recurring collection, or
  provider state was enabled or changed.

Subagent status: `not_spawned`.

Graphiti write status: `queued_unverified`; readiness passed and job
`851d9fb5-5cc1-419d-a3fa-0e725d720c5d` accepted the compact checkpoint, but
the follow-up status read lost Graphiti transport before visibility could be
confirmed. Repository source and this checkpoint remain authoritative.

Next action: install and diagnose service 0.3.97 from the validated artifact,
then obtain a fresh bounded live-attempt budget for the final 80-item proof.

### Checkpoint P0063-C03 | 2026-09-02

Plan version: 3

State: `installed_live_proof_pending_fresh_budget`

Progress classification: `acceptance_progress`

Authority classification:

- `inherited_authority`; installing and auditing the already-validated release
  stayed inside Packet C. No additional Reddit acquisition attempt, schedule
  mutation, provider mutation, or profile replacement occurred.

Evidence:

- the transactional installer advanced `current` to service 0.3.97 while
  retaining 0.3.96 as `previous`; installed MCP readback reports service
  0.3.97, adapter 4.0.4, database schema 17, status `ready`, and compatibility
  state `compatible`;
- installed `reddit_browser.py` and `service_acquisition_worker.py` SHA-256
  values exactly match commit `dc7a10e0510a4674201accb963d23ea7a9640bb7`;
- both live service databases return `ok` from `PRAGMA quick_check`;
- all ten existing Reddit collection specifications remain disabled. The
  service-owned daily schedule remains ready at its unchanged one-day cadence;
- exact `last30days-facebook` runtime status reports no browser process, no
  DevTools endpoint or targets, and no retained profile owner after cleanup;
- the Graphiti checkpoint job was read back as terminal `failed` with a
  transport `TimeoutError` during node extraction. No duplicate memory job or
  retry was queued; repository and installed-state evidence remain
  authoritative.

Subagent status: `not_spawned`.

Graphiti write status: `failed_transport`; job
`851d9fb5-5cc1-419d-a3fa-0e725d720c5d` created no visible episode.

Next action: obtain a fresh explicit live-attempt budget, then run one bounded
Reddit-only campaign against installed service 0.3.97 to prove 80 unique
canonical posts or preserve the next typed terminal limitation.

### Checkpoint P0063-C04 | 2026-09-02

Plan version: 4

State: `manual_login_blocked_by_agent_browser_identity_veto`

Progress classification: `blocked_progress`

Authority classification:

- `inherited_authority`; the operator requested an exact-profile Guacamole/RDP
  login surface. All actions were limited to protected acquisition, route
  presentation, and exact recovery planning for `last30days-facebook`.

Evidence:

- capability status reports one active `last30days` grant for the exact
  profile, and scoped remote-view doctor reports the RDP/Guacamole stack ready;
- the capability-authenticated access plan selects `last30days-facebook`, the
  exact terminal owner session, and `supersede_terminal_owner`, with process
  absence and profile-lock release proven;
- both generic and exact-session `service_profile_manual_seeding_acquire`
  requests failed before Chrome launch with
  `existing_session_profile_identity_unproven`; each route/display lease was
  fully rolled back;
- protected `service_profile_acquire` failed with
  `profile_acquisition_daemon_route_mismatch`. The supported recovery planner
  then sealed a single `supersede_terminal_owner` action for generation 73,
  but applying that exact plan again failed with
  `existing_session_profile_identity_unproven`;
- final runtime readback reports no browser PID, DevTools endpoint, targets, or
  profile lock. No durable recovery receipt exists, no operator handoff URL was
  produced, and no Reddit acquisition attempt ran.

Subagent status: `not_spawned`.

Graphiti write status: `not_written`; the repository receipt is authoritative
and the prior Graphiti write path remains failed on transport timeout.

Next action: repair Agent Browser so protected terminal-owner supersession can
complete on its authority-derived daemon route, then request the Reddit manual-
seeding handoff again and require `operatorVisible.state=ready` before sharing
its durable `/remote-view/<handoff-id>` URL.
