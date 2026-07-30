# Plan 0014 | Recurring collection timer durability

State: OPEN
Roadmap: P02
Date: 2026-07-26
Predecessor: Plan 0011

## Objective

Prove that one low-risk public-source collection specification survives two
scheduled intervals and a service restart while preserving cursor continuity,
budgets, immutable deduplication, coverage, and an explicit paused terminal
state.

## Current State

- Plan 0011 proved a bounded timer and restart path, then paused the acceptance
  spec.
- No recurring authenticated timer is enabled.
- Installed service version 0.2.7/schema 12 is active and ready.
- No collection spec is currently enabled.
- The existing public Reddit spec
  `acceptance-reddit-temporal-graph` is durably paused at revision 5 with a
  60-second interval, 24-hour lookback, 3-item limit, 120-second wall timeout,
  50-request network limit, $1 budget, durable retention, public redaction,
  and assessment disabled.
- A successor revision-6 proof is needed before expanding recurring hydration
  beyond this original acceptance fixture.

## Scope

- create or revise one public-source collection spec with explicit item, time,
  network, cost, retention, and access bounds;
- execute two consecutive due intervals with one service restart between them;
- prove scheduled-run identity, cursor/watermark continuity, deduplication,
  coverage, gaps, source health, and yield;
- pause the spec and verify no later automatic run occurs.

## Non-Goals

- authenticated-source scheduling;
- broad hydration, multiple specs, or production cadence selection;
- changing P01 authority, publication semantics, or access partitions;
- stochastic assessment as a prerequisite for raw publication;
- leaving the acceptance timer enabled.

## Dependencies And Owned Surfaces

- Depends on P01 immutable versions/provenance and existing P02 scheduler
  authority.
- Expected writes are focused scheduler/supervisor tests if a defect is proved,
  one versioned public collection spec, durable run ledgers, and closeout docs.

## Execution Packets

1. Select the public source and freeze the bounded spec revision.
2. Run interval one and preserve its run/job/publication receipt.
3. Restart the service, run interval two, and prove continuity.
4. Pause the spec, prove quiescence, and close out.

## Bounds And Gates

- maximum implementation attempts per packet: 2;
- maximum review/rework cycles: 1;
- maximum hardening-only checkpoints: 1;
- active-agent concurrency: 1;
- exactly one spec, two due intervals, and one planned service restart;
- stop on budget escape, duplicate interval identity, cursor regression,
  cross-partition publication, or inability to pause.

## Acceptance Criteria

- both intervals bind to immutable spec revisions and distinct due boundaries;
- replay of a due boundary returns the same durable run rather than duplicating
  work;
- the restart preserves cursor/watermark and lease safety;
- identical content reuses immutable versions while new observations create
  sightings and coverage;
- health and yield are separately observable;
- the final spec revision is disabled and no later timer job appears.

## Validation

- focused collection, scheduler, supervisor, publication, and restart tests;
- installed-runtime run/job/spec/coverage readbacks;
- planning audit, database integrity checks, and `git diff --check`.

## Definition Of Done

The two-interval restart proof passes and the acceptance spec is durably paused,
or the packet stops at the first typed safety failure with no authenticated
timer enabled.

### Checkpoint P0014-C01 | 2026-07-29

Plan version:

- 1

State transition:

- `PLANNED -> OPEN`

Progress classification:

- `outcome_progress`

Authority and scope:

- the user explicitly resumed last30days timed service scraping, RAG, and App
  Intelligence development;
- Plan 0014 is the first serialized packet, followed by Plans 0015 and 0016;
- Plans 0013 and 0017 remain planned and out of this requested slice.

Owned work:

- reuse only the existing public Reddit acceptance spec as revision 6;
- execute exactly two distinct 60-second due boundaries with one planned
  `last30days.service` restart between them;
- pause the spec and prove quiescence;
- repair source or tests only if a typed defect is proved within this plan's
  bounded scheduler/supervisor surface.

Current evidence:

- installed service is ready at version 0.2.7/schema 12;
- no collection spec is enabled;
- historical revision 5 is disabled and remains the durable baseline;
- no user-scoped `last30days-social.timer` exists;
- service-owned collection scheduling, rather than an authenticated external
  timer, is the authority for this public-source proof.

Subagent status:

- `not_spawned`; one collection spec and one service restart form a serialized
  critical path.

Graphiti write status:

- deferred until the first terminal implementation checkpoint.

Next action:

- create revision 6 with the frozen public bounds, run interval one, preserve
  its terminal receipts, restart the service, and then run interval two.

### Checkpoint P0014-C02 | 2026-07-29

Plan version:

- 1

State transition:

- `open_ready -> blocked_stale_due_replay_fixed_awaiting_live_retry_authorization`

Progress classification:

- `blocker_reduction`

Runtime evidence:

- enabling revision 6 preserved a stale `2026-07-26T02:39:00Z` schedule
  boundary from the previously paused specification;
- the scheduler therefore created four revision-6 runs rather than the
  authorized two: one stale catch-up boundary, the manual
  `2026-07-29T12:36:00Z` boundary, and timer boundaries at 12:37 and 12:38;
- all four runs published, spent no more than one cent each, and stayed in the
  public partition, but the stale catch-up and extra timer boundary violated
  this packet's exact-two-run bound;
- revision 7 paused the specification at
  `2026-07-29T12:38:43.505007Z`;
- at `2026-07-29T12:40:15Z`, more than one interval later, the durable run
  count remained unchanged, the latest scheduled boundary remained 12:38,
  and revision 7 remained disabled;
- the database integrity check returned `ok`.

Defect and repair:

- `CollectionCoordinator.put_spec()` preserved
  `collection_schedule_state.next_due_at` for every spec revision, including a
  disabled-to-enabled transition;
- the source now resets `next_due_at` to the current floored boundary only when
  resuming a paused specification;
- ordinary edits to an already enabled specification continue to preserve the
  existing due boundary;
- a regression test advances a paused specification by three days and proves
  that resume creates only the current interval rather than replaying paused
  boundaries;
- the focused collection and product suites pass 17 tests.

Stop reason:

- the live packet stopped at its first hard-bound failure;
- no additional live retry, install synchronization, or service restart is
  authorized by this exact-two-interval packet;
- the installed v0.2.7 service therefore remains paused on revision 7 and does
  not yet contain the working-tree repair.

Remaining acceptance:

- synchronize the reviewed repair into the installed skill;
- execute a newly authorized two-interval proof with the single restart placed
  between the two boundaries;
- pause and re-prove quiescence before closing Plan 0014.

Subagent status:

- `not_spawned`; diagnosis, repair, and validation remained one serialized
  scheduler path.

Graphiti write status:

- pending source commit and push.

Next action:

- validate, commit, and push the repair checkpoint; then await explicit
  authority for a fresh live retry packet before installing or restarting the
  service.

### Checkpoint P0014-C03 | 2026-07-29

Plan version:

- 1

State transition:

- `blocked_stale_due_replay_fixed_awaiting_live_retry_authorization ->
  blocked_stale_due_replay_fixed_awaiting_live_retry_authorization`

Progress classification:

- `closeout`

Closeout evidence:

- repair commit `d190696` is pushed to `origin/main`;
- local `HEAD`, tracking `main`, and remote `main` agree;
- Graphiti job `cd855bca-36c4-4b79-acdc-43abb47262f1` completed on attempt 1;
- episode `99aa1e6c-14c9-41fc-9976-1fd92294d4c2` is visible in
  `last30days_skill_main` with read-after-write ready.

Next action:

- await explicit authority for the fresh live install/restart retry described
  in Checkpoint P0014-C02.

### Checkpoint P0014-C04 | 2026-07-29

Plan version:

- 2

State transition:

- `blocked_stale_due_replay_fixed_awaiting_live_retry_authorization ->
  open_retry_authorized`

Progress classification:

- `blocker_reduction`

Authority:

- the user explicitly directed completion of the narrow Plan 0014 timer retry
  before opening Plan 0018's first implementation packet.

Current installed evidence:

- the active systemd unit imports
  `~/.agents/skills/last30days/scripts/service.py`;
- the installed skill is a frozen directory, not a working-tree symlink;
- the installed and repaired `service_collection.py` SHA-256 digests differ;
- installed service v0.2.7/schema 12 is ready;
- revision 7 remains disabled and no collection is enabled.

Revision-2 execution bounds:

- synchronize the reviewed source at commit `d190696` or later into the
  installed skill while revision 7 remains disabled;
- perform one pre-proof activation restart so the daemon loads the repaired
  scheduler;
- enable only `acceptance-reddit-temporal-graph` as revision 8 with the frozen
  public bounds;
- measure exactly two distinct 60-second due boundaries;
- perform exactly one durability restart after interval one is terminal and
  before interval two is claimed;
- pause immediately after interval two reaches a terminal state and prove more
  than one interval of quiescence;
- maximum service lifecycle restarts in Revision 2: 2 total, consisting of one
  pre-proof activation restart and one restart inside the measured
  two-interval proof;
- no authenticated source, browser, profile, App Intelligence assessment, or
  second collection spec may be enabled.

Hard stops:

- stop on a stale catch-up boundary, more than two revision-8 runs, duplicate
  interval identity, non-public partition, budget escape, restart recovery
  failure, database-integrity failure, or inability to pause.

Subagent status:

- `not_spawned`; installation, two due boundaries, and the intervening restart
  are one serialized critical path.

Graphiti write status:

- deferred to the terminal Plan 0014 checkpoint.

Next action:

- validate and commit this Revision-2 activation, synchronize the installed
  skill, perform the pre-proof restart, and verify scheduler digest and service
  readiness before enabling revision 8.

### Checkpoint P0014-C05 | 2026-07-29

Plan version:

- 3

State transition:

- `open_retry_authorized -> open_final_retry_backpressure_repair`

Progress classification:

- `blocker_reduction`

Revision-2 result:

- synchronized the repaired working tree into the frozen installed Skill and
  verified identical source and installed scheduler digests;
- performed the authorized pre-proof activation restart and confirmed service
  v0.2.7/schema 12 ready;
- enabled only the bounded public acceptance spec as revision 8;
- the first run remained active long enough for the scheduler to create runs
  for the next two due boundaries;
- stopped at the hard bound after exactly three revision-8 runs existed and
  immediately paused the spec as revision 9;
- did not perform the durability restart and did not enable an authenticated
  source, assessment, browser profile, or second collection spec;
- database integrity remained `ok`.

Root cause and repair:

- `CollectionCoordinator.enqueue_due()` considered only the due time and retry
  delay; it did not suppress a due interval while the same spec already had a
  non-terminal collection run;
- add deterministic per-spec backpressure by excluding specs with collection
  runs outside terminal states `published`, `partial`, and `failed`;
- focused regression coverage advances the clock across multiple overdue
  boundaries, proves no second run appears while the first is active, marks
  the first terminal, admits exactly one successor, and again suppresses
  overlap.

Revision-3 execution bounds:

- this is the second and final implementation attempt allowed by the plan;
- validate and commit the backpressure repair, synchronize the installed
  Skill, and perform one pre-proof activation restart;
- enable only `acceptance-reddit-temporal-graph` as revision 10 with the same
  frozen public bounds;
- measure exactly two distinct 60-second due boundaries;
- perform exactly one durability restart after interval one is claimed and
  before interval two is claimed; the restart may recover interval one, but
  per-spec backpressure must prevent interval two until interval one is
  terminal;
- pause revision 10 immediately after interval two appears, allow that already
  admitted run to finish, and prove more than one interval of quiescence;
- maximum lifecycle restarts in Revision 3: two total, one activation restart
  and one durability restart inside the measured proof;
- no authenticated source, browser, profile, App Intelligence assessment, or
  second collection spec may be enabled.

Hard stops:

- stop on more than two revision-10 runs, overlapping non-terminal runs,
  duplicate interval identity, non-public partition, budget escape, restart
  recovery failure, database-integrity failure, or inability to pause;
- if Revision 3 fails, close Plan 0014 truthfully at the typed blocker without
  another live attempt.

Subagent status:

- `not_spawned`; source repair and the live service proof are one serialized
  critical path.

Graphiti write status:

- deferred to the terminal Plan 0014 checkpoint.

Next action:

- validate and commit the backpressure repair, synchronize the installed
  Skill, perform the activation restart, and execute Revision 3.
