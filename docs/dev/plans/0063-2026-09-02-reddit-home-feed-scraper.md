# Plan 0063 | Reddit Home Feed Scraper

State: OPEN
Lane: P23
Branch: feat/reddit-home-feed
Target: main
Integration: fast-forward
Roadmap: P23
Plan version: 12
Date: 2026-09-03

## Objective

Add a deterministic Agent Browser scraper for the authenticated Reddit home
feed that can collect 80 unique canonical posts without applying topic-quality
filtering, while preserving the existing Reddit search capability.

## Current State

- service 0.3.106 is installed and ready on schema 17 with a dedicated Reddit
  home-feed path, 80-item collection capacity, remote-headed CDP control, typed
  network-security blocking, and broker-preserved RDP route-pool selection;
- direct authenticated-profile inspection observed 62 rendered post containers
  and 29 unique canonical post links before the bounded live campaign, proving
  that the profile and Reddit surface were usable;
- the original three-attempt campaign is terminal. It exposed, in order, a Reddit
  local-headless network-security block and two broker launches that discarded
  the configured route-pool hint and fell back to stale Xvfb display `:90`;
- the operator authorized a fresh campaign of up to five reasoned attempts.
  Retry 1, job `ec8ba8ad-888e-4c7b-b041-113993da98d1`, failed in 58 ms before
  Agent Browser enqueued a job because service 0.3.100 sent the route-pool field
  at the MCP tool's top level rather than under action-specific `params`;
- commit `dec7672` corrected that request-contract defect in installed service
  0.3.101. Retry 2 reached Agent Browser, which recorded the configured route-
  pool entry but still used generic `tab_new` auto-launch and stale Xvfb `:90`;
- retries 3 through 5 progressively proved the authenticated Agent Browser
  path, repaired a stale numeric display-allocation alias, and reached a ready,
  authenticated Reddit page. Retry 5 failed at the first evaluation because
  the route-open path had no exact service tab handle;
- commits `a6e7178`, `d69467d`, and `d1ff629` now preserve protected service
  authority, use a replacement-session-scoped display allocation, and follow
  successful `remote_view_open` with brokered `tab_new` handle acquisition;
- after explicit continuation authority, retry 1 of a new five-attempt
  campaign exercised the final handle repair end to end. Run
  `collection-run-c3e462a7f9eb6ce9cace3ce3e0d6ae3a` published 28 unique
  canonical posts from 112 observations with zero ad, spam, structural, or
  date-scope exclusions;
- all 84 rejected observations were duplicates of those 28 posts. Every Agent
  Browser operation succeeded, but three fixed 1,400-pixel scrolls produced
  the same rendered snapshot and the scraper incorrectly treated that as page
  stagnation even though it had not measured viewport progress;
- candidate service 0.3.107 records document-scroll progress in each extraction
  snapshot and stops for stagnation only when neither post observations nor
  the page position/height advances. Four reasoned retries remain, and 80-item
  live proof is still absent;
- commit `c77cbb3` isolates the real MCP/service integration test from the
  operator's configured tick runtime; the complete 2,758-test collection now
  reaches 100% without failures, closing the remaining validation gap;
- all 19 Reddit collection specifications remain disabled, and this plan has
  not enabled or otherwise mutated `daily-default`.

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
7. The current successor campaign uses no more than five Reddit acquisition
   attempts and proves 80 unique canonical posts, or terminates with a typed
   receipt that identifies the exact remaining scraper/provider limitation.
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

### Checkpoint P0063-C05 | 2026-09-02

Plan version: 5

State: `manual_reddit_login_ready_operator_action_pending`

Progress classification: `acceptance_progress`

Authority classification:

- `scope_expansion`; after the protected acquisition path repeatedly vetoed
  its own exact-profile replacement, the operator explicitly directed a forced
  direct launch. The fallback remained limited to the existing
  `last30days-facebook` profile and its already-governed RDP display.

Evidence:

- immediately before launch, exact runtime status reported no live browser,
  PID, DevTools endpoint, or targets; the exact user-data directory had no
  `SingletonLock`, `SingletonSocket`, or `SingletonCookie`, and no process used
  that path;
- display `:11` passed a direct X11 readiness probe. A non-attachable
  `runtime login` then opened `https://www.reddit.com/login/` with the exact
  profile as headed manual PID 7511 and no DevTools port;
- post-launch runtime readback reports PID 7511 alive in `manual` mode on
  display `:11`. Service status identifies the same PID, profile, and target,
  marks remote control available, and joins it to governed route
  `guacamole:1`;
- durable public handoff `/remote-view/r895695` remains ready for
  `guacamole:1`, its presentation receipt is ready, and a direct public HTTP
  check returned 200. No raw provider URL is exposed;
- no Reddit acquisition attempt, timer change, recurring collection enablement,
  provider mutation, profile replacement, or CDP attachment occurred.

Subagent status: `not_spawned`; current orchestration policy prohibits
delegation.

Graphiti write status: `not_written`; the operator-login checkpoint is
transient and repository/runtime readbacks remain authoritative.

Next action: the operator completes Reddit sign-in through the durable handoff,
closes the manual Chrome window, and reports completion. Then run a bounded
post-close authentication probe before consuming the next Reddit feed attempt.

### Checkpoint P0063-C06 | 2026-09-02

Plan version: 6

State: `service_owned_reddit_handoff_ready_operator_action_pending`

Progress classification: `acceptance_progress`

Authority classification:

- `inherited_authority`; repairing the failed operator presentation remained
  inside the explicitly approved exact-profile manual-login objective.

Evidence:

- C05 overstated the retained `/remote-view/r895695` record as an operational
  handoff. The operator's direct readback proved its claimed frontend session
  had no HTTP route, and dashboard recovery returned
  `operator_presentation_authority_unavailable`; the direct runtime browser had
  only a raw route association, not service-owned presentation authority;
- current scoped doctor readback proves all three Guacamole/RDP routes, public
  ingress, permissions, backend TCP, and display sockets ready. The first
  Route A plan exposed a stale retained allocation collision:
  `remote-view-display:11` recorded display `:10`, so it could not bind Route A
  display `:11`;
- a unique display allocation passed strict route-bound dry-run. The actual
  Route A launch then failed only visible-window ownership proof and correctly
  closed its new browser and rolled back its route lease;
- the controlled Route B retry used the same exact user-data directory, unique
  display allocation `remote-view-display:reddit-login-c05-b`, and existing
  display `:10`. It returned `success=true`, browser PID 90966, route
  `guacamole:2`, opaque handoff `/remote-view/r338548`, and
  `operatorVisible.state=ready`;
- current service readback reports the browser healthy, the route and route-
  pool entry checked out, the display content `browser_window_visible`, the
  selected Reddit target ready, and public operator access HTTP 200. The
  handoff record itself is `ready`, resolves to that browser/session/route, and
  its public endpoint returns HTTP 200;
- authentication has not been inferred from page visibility. No Reddit scrape
  attempt, timer mutation, recurring enablement, provider mutation, profile
  replacement, or unrelated browser interaction occurred.

Subagent status: `not_spawned`; current orchestration policy prohibits
delegation.

Graphiti write status: `not_written`; repository and current service readbacks
remain authoritative for this transient operator handoff.

Next action: the operator opens `/remote-view/r338548`, confirms or completes
Reddit authentication, and reports completion. Then verify the authenticated
surface before the next bounded Reddit feed acquisition.

### Checkpoint P0063-C07 | 2026-09-02

Plan version: 7

State: `broker_route_repaired_live_attempt_ceiling_reached`

Progress classification: `blocker_reduction`

Authority classification:

- `inherited_authority`; authenticated-surface inspection, three bounded
  Reddit-only attempts, deterministic repair, packaging, and installation all
  stayed inside the approved exact-profile, no-provider-mutation, and
  no-schedule-enablement scope. A fourth live attempt was not run because the
  campaign's explicit three-attempt ceiling is reached.

Evidence:

- direct read-only CDP inspection of the service-owned
  `reddit-login-c05-b` browser at `https://www.reddit.com/?feed=home` found no
  login control, 17 account signals, 62 rendered post containers, and 29
  unique canonical post links. The operator independently confirmed that the
  browser was authenticated and reachable from the left rail;
- fresh MCP adapter 4.0.4 readback is compatible with service API 1 and
  database schema 17. The conversation's already-open MCP transport remained
  pinned to adapter 4.0.3, so product operations used fresh processes of the
  installed adapter rather than bypassing the service contract;
- attempt 1, job `af5c6062-f3b2-457c-b0ff-1a9be7edc708`, requested 80 but
  the prior host default reduced it to 50. Reddit returned its network-security
  block page to the local-headless browser, which the prior auth probe
  mislabeled `auth_state_ambiguous`;
- attempt 2, job `e7296104-c074-4b85-84e5-6d5d3de2c6e9`, correctly requested
  80 after the host ceiling repair but failed before navigation when generic
  remote-headed acquisition tried stale Xvfb display `:90` three times;
- attempt 3, job `4d501581-1139-4aff-8228-95ea08468414`, also requested 80.
  Although the installed worker read `guacamole-rdp-b`, the broker-first
  `tab_new` branch rebuilt the request without `routePoolEntryId`, again
  selecting display `:90` and failing `agent_browser_error` before navigation;
- commit `28cfab2` adds typed Reddit network-security detection, raises the
  default host item ceiling from 50 to 100, moves feed acquisition to the
  remote-headed RDP posture, accepts exact route hints, and preserves
  `routePoolEntryId` across the broker-first request boundary. The exact
  broker regression failed before the repair and passes afterward;
- the focused Agent Browser, Reddit, worker, collection, job-runner, env,
  release, install, runtime-package, and source-log suites pass. The full suite
  reached 100% with one persistent teardown timeout in
  `test_real_service_mcp_discovery_query_refresh_and_poll`; its isolated rerun
  reproduces the same service-termination timeout and is not presented as a
  green full-suite result;
- service artifact `last30days-service-0.3.100.tar.gz` reproduced byte-for-byte
  with SHA-256
  `4b100b437338289df9f37796b9675d6cef369f822b519fb637e5613dc9ae61ee`.
  Transactional install readback reports service 0.3.100 ready, database schema
  17, contract SHA-256
  `bcbac11ae75e30f52b8d654efabbc965fd9812447093d2f821ae687301cf3025`,
  and runtime-manifest SHA-256
  `44460e4d2a01cbb57c9c4c27c1f397b1d23fb1b8c5759fc055b5a0c5837a330c`;
- an installed-code dry run reads the private configuration and proves
  `browser_host=remote_headed`, `view_provider=rdp_gateway`, configured and
  broker-emitted `routePoolEntryId=guacamole-rdp-b`, and default item limit
  100 without launching a browser or consuming another provider attempt;
- live database `PRAGMA quick_check` is `ok`; the three P0063 collection runs
  and jobs are terminal failed receipts, all 13 Reddit specifications are
  disabled, there is no collection profile lease, and Agent Browser reports no
  live browser for `last30days-facebook`;
- the Agent Browser lifecycle/handoff issue was documented separately in
  commit `47a1040f` on branch
  `docs/reddit-handoff-errors-20260902` for upstream service review.

Subagent status: `not_spawned`; current orchestration policy prohibits
delegation.

Graphiti write status: `not_written`; current repository, database, installed
release, and Agent Browser readbacks are the authoritative evidence.

Next action: obtain one fresh Reddit acquisition attempt, then run the disabled
80-item specification through installed service 0.3.100 and require either 80
unique canonical posts or the next typed terminal limitation. Do not enable the
recurring Reddit lane.

### Checkpoint P0063-C08 | 2026-09-02

Plan version: 8

State: `release_candidate_fully_validated_live_attempt_ceiling_reached`

Progress classification: `acceptance_progress`

Authority classification:

- `inherited_authority`; diagnosing and repairing the repository validation
  failure was an offline, test-only continuation of the approved Reddit release
  candidate. It consumed no provider request or browser acquisition attempt.

Evidence:

- the exact red-capable command
  `uv run pytest tests/test_mcp_service_integration.py::test_real_service_mcp_discovery_query_refresh_and_poll -q`
  reproduced the service-termination timeout twice;
- structural tracing showed the test service inherited
  `~/.config/last30days/tick-config-v1.json`, started a real-config
  `TickScheduleLoop` against its temporary database, and then applied the
  production 900-second graceful drain policy to unintended scheduled work;
- changing only `LAST30DAYS_CONFIG_DIR` to an isolated temporary directory
  made the same test pass in under two seconds, confirming configuration
  inheritance rather than service socket, child-worker, or MCP connection
  leakage as the cause;
- commit `c77cbb3b3a7aa72b8bfef231f1f377c5770957fa` passes that isolated directory
  explicitly to the spawned test service. The exact test passes, and the full
  2,758-test repository collection reaches 100% with no failures and seven
  skips;
- service 0.3.100 remains installed and ready; this test-only repair does not
  alter the reproducible runtime artifact or its previously recorded digest.

Subagent status: `not_spawned`; current orchestration policy prohibits
delegation.

Graphiti write status: `not_written`; the repository test and commit are the
authoritative evidence for this validation-only checkpoint.

Next action: obtain one fresh Reddit acquisition attempt, then run the disabled
80-item specification through installed service 0.3.100. Keep Reddit disabled
in recurring schedules.

### Checkpoint P0063-C09 | 2026-09-02

Plan version: 9

State: `mcp_route_contract_repaired_retry_campaign_active`

Progress classification: `blocker_reduction`

Authority classification:

- `inherited_authority`; the operator authorized up to five additional Reddit
  attempts provided each retry has an evidence-backed reason. Retry 1 consumed
  one attempt. The repository repair, candidate release build, and installation
  preparation stay within the approved exact-profile, Reddit-only scope.

Evidence:

- retry 1 used disabled specification
  `p0063-reddit-home-feed-live-v4`, collection run
  `collection-run-8a0feed7763c128fa80c96c47e134109`, and job
  `ec8ba8ad-888e-4c7b-b041-113993da98d1`. It failed with
  `agent_browser_error` during `workspace_acquisition`; its only browser
  operation was `service_request:tab_new`, failed after 58 ms, and Agent Browser
  retained no corresponding job;
- the installed Agent Browser 0.28.0 MCP schema admits `params` but does not
  admit top-level `routePoolEntryId`. Its source contract explicitly requires
  route-selection material such as `routePoolEntryId` under `params`;
- the changed regression first failed because the outgoing request contained
  top-level `routePoolEntryId`. Commit `dec7672` now emits
  `params.routePoolEntryId` while preserving existing action parameters;
- `uv run pytest tests/test_agent_browser_runtime.py tests/test_reddit_browser.py
  tests/test_release_versions.py tests/test_service_runtime_package.py -q`
  passes;
- independent service 0.3.101 builds are byte-identical with SHA-256
  `632df028ffb828240d623e998ae79570cf9318e2156aa819d7f20e0a68a9b33a`.

Subagent status: `not_spawned`; current orchestration policy prohibits
delegation.

Graphiti write status: `pending_after_transport_timeout`; job
`78f1ab3e-7f6a-484c-ad18-d1f8fb2c1625` timed out before an episode became
visible. The intended compact C09 episode remains pending for a later closeout;
checkpoint publication and live verification remain the source authorities.

Next action: install service 0.3.101 transactionally, verify exact installed
identity and readiness, then spend retry 2 only after confirming the exact
profile has no live browser or collection lease and the configured RDP route is
ready. Keep Reddit disabled in recurring schedules.

### Checkpoint P0063-C10 | 2026-09-02

Plan version: 10

State: `route_bound_cold_launch_repaired_retry_campaign_active`

Progress classification: `blocker_reduction`

Authority classification:

- `inherited_authority`; retry 2 was evidence-backed by installed service
  0.3.101, a clean exact-profile lane, and a ready RDP route. The subsequent
  diagnosis and 0.3.102 repair are ordinary in-scope remediation. Three of the
  operator-authorized attempts remain.

Evidence:

- retry 2 used disabled specification
  `p0063-reddit-home-feed-live-v5`, collection run
  `collection-run-259f395f5128215dd2a04e6165a2f817`, and job
  `5b48abb8-4802-4cd1-acef-2a21445e3165`;
- Agent Browser job
  `mcp-service-request-tab_new-33ba6452-3ef6-44f0-8302-30bc1b4f24f1`
  proves the repaired request was accepted and retained
  `routePoolEntryId=guacamole-rdp-b`, but generic `tab_new` auto-launch still
  attempted Xvfb display `:90` three times and failed before navigation;
- structural inspection shows Agent Browser's generic `auto_launch` path does
  not resolve route-pool entries, while its `remote_view_open` path owns route-
  pool and display selection. The live route remained available and ready on
  `guacamole:2`, display `:10`;
- the new regression failed before the repair because cold acquisition called
  `service_request:tab_new`. Commit `880b82d` now selects `remote-view open`,
  sends `--route-pool-entry-id guacamole-rdp-b`, and preserves the replacement
  session selected by the access plan;
- focused Agent Browser runtime, Reddit browser, release-version, and runtime-
  package suites pass. Independent service 0.3.102 builds are byte-identical
  with SHA-256
  `b703d9311c01d01f408e55f26f12caa8640dc1e02905378a50dff702a8013d63`.

Subagent status: `not_spawned`; current orchestration policy prohibits
delegation.

Graphiti write status: `graphiti_write_pending`; the prior compact C09 write
timed out in job `78f1ab3e-7f6a-484c-ad18-d1f8fb2c1625`. Intended summary:
Plan 0063 C10 replaces generic `tab_new` cold launch with route-bound
`remote_view_open` in commit `880b82d`; three retries remain.

Next action: install service 0.3.102 transactionally, verify its exact identity
plus clean exact-profile and route state, then spend retry 3 with a new disabled
80-item specification. Keep Reddit disabled in recurring schedules.

### Checkpoint P0063-C11 | 2026-09-02

Plan version: 11

State: `authenticated_route_and_exact_handle_repaired_attempt_ceiling_reached`

Progress classification: `blocker_reduction`

Authority classification:

- `inherited_authority`; retries 3, 4, and 5 each followed a distinct live
  failure with a focused red/green repair and preflight. The five-attempt
  allowance is now exhausted, so service 0.3.106 was installed and validated
  without submitting a sixth collection run.

Evidence:

- retry 3 used disabled specification `p0063-reddit-home-feed-live-v6`, run
  `collection-run-e3e4a93eca1eb48fce3ecf6179de9df7`, and job
  `5e9445f6-9142-4a10-a490-85e4dc1e2196`. Agent Browser reached
  `remote_view_open` on `guacamole-rdp-b` but rejected the direct CLI path with
  `existing_session_profile_identity_unproven`;
- commit `a6e7178` moved route opening into authenticated `service_request`,
  preserving the protected principal authority and reviewed
  `allowDuplicateProfileLane` override;
- retry 4 used disabled specification `p0063-reddit-home-feed-live-v7`, run
  `collection-run-4216a1d89238daec3eacf3b531b15aca`, and job
  `c9df0168-aa13-4256-bdfb-2f13a8f7b163`. Agent Browser then reported
  `route_pool_target_mismatch` because retained allocation
  `remote-view-display:10` incorrectly named display `:11`, while route B
  correctly targeted live display `:10`;
- commit `d69467d` binds the route display to a fresh allocation ID scoped by
  the broker-selected replacement session. A live no-effect Agent Browser
  preflight returned `status=planned`, exact route `guacamole-rdp-b`, the
  session-scoped allocation, and zero blockers;
- retry 5 used disabled specification `p0063-reddit-home-feed-live-v8`, run
  `collection-run-a15de07b9397bee8683a459f61229fa7`, and job
  `9c015092-94e5-425c-a658-224e337e9a6f`. Agent Browser's
  `remote_view_open` succeeded, route B became ready, and a live browser for
  `last30days-facebook` exposed an active Reddit home-feed tab. The run failed
  at its first evaluation because route opening did not return a service tab
  handle and `tab_list` is discovery-only;
- direct handle-scoped evaluation of that retained tab proved
  `authenticated=true`, `login_form=false`, `checkpoint=false`, and
  `network_blocked=false` without scrolling or extracting posts;
- commit `d1ff629` follows successful route opening with authenticated,
  browser/session-routed `tab_new`, validates the returned handle, and makes it
  authoritative for subsequent evaluation. The exact regression failed before
  this repair and passes afterward;
- installed service 0.3.106 is ready with schema 17, contract SHA-256
  `bcbac11ae75e30f52b8d654efabbc965fd9812447093d2f821ae687301cf3025`,
  runtime-manifest SHA-256
  `cd0703c5096cb8b675f756605e8f56bdf325d4775c18b4024417ce6c9b605d5a`,
  and reproducible artifact SHA-256
  `a71acb60f20268690de9d40b43985ab8b9e2f9aca794a8ee8e3878b83feab9a6`;
- the complete repository suite passes with 2,753 tests, seven skips, and nine
  passing subtests after the final exact-handle repair;
- database `PRAGMA quick_check` is `ok`; all 18 Reddit specifications are
  disabled and no recurring Reddit schedule was enabled.

Subagent status: `not_spawned`; current orchestration policy prohibits
delegation.

Graphiti write status: `graphiti_write_pending`; the prior compact checkpoint
job `78f1ab3e-7f6a-484c-ad18-d1f8fb2c1625` timed out. Current commits, installed
identity, database receipts, and Agent Browser jobs remain authoritative.

Next action: obtain explicit authority for one additional disabled 80-item
collection attempt against installed service 0.3.106. Do not enable the
recurring Reddit lane.
