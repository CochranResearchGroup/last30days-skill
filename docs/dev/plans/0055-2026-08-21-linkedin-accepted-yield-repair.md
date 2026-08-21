# Plan 0055 | LinkedIn Accepted-Yield Repair

State: OPEN
Roadmap: P08
Plan version: 4
Date: 2026-08-21

## Objective

Make the governed LinkedIn browser lane honor the service-admitted item ceiling
and pursue accepted unique post permalinks within a bounded scroll budget.

## Current State

- installed service 0.3.58/schema 16 is ready and MCP 4.0.3-compatible;
- the LinkedIn item-limit and accepted-unique pagination correction is installed,
  and 0.3.58 preserves the unique retained daemon session route for follow-on
  browser controls instead of reattaching under the service-session alias;
- freshly authorized terminal tick `tick-a678da2c70bded995195a865f8100f0f`
  failed before either scraper observed a post while agent-browser workstation
  runtime admission was transferring during a nonterminal upgrade;
- the upgrade candidate later failed activation and preserved the old selected
  generation, but workstation readiness remains false because runtime
  convergence is not ready;
- no X or LinkedIn candidate reached quality, duplicate, permalink, or
  sponsored/promoted classification in the fresh canary. The installed daemon
  route fix therefore remains deterministic-test proven but live-unexercised.

## Scope

- propagate the governed acquisition `item_limit` into `search_linkedin`;
- clamp explicit ceilings to 100 and derive at most eight scrolls at five
  accepted items per scroll budget;
- stop LinkedIn scrolling only when accepted unique yield meets the requested
  ceiling or the bounded scroll budget is exhausted;
- preserve existing authentication, checkpoint, rate-limit, permalink, author,
  date, sponsored, relevance, media, and duplicate gates;
- advance one service release, validate/build/install it transactionally, and
  run at most one receipt-only X/LinkedIn 20/20 canary without changing the
  recurring schedule.

## Non-Goals

- do not weaken LinkedIn quality gates or reinterpret sponsored cards as posts;
- do not change working X accepted-unique pagination;
- do not re-enable Reddit or Facebook, alter `daily-default`, or change the
  recurring ten-item X/LinkedIn ceilings;
- do not add unbounded scrolling, click every `Show more`, launch another
  browser, or use cost/model budgets;
- do not treat a 20-item ceiling as a guarantee that the source exposes 20
  acceptable unique posts within the finite capture window.

## Acceptance Criteria

1. A worker regression proves the admitted LinkedIn item limit reaches the
   browser search interface.
2. An explicit 20-item LinkedIn request receives a bounded four-scroll budget,
   while direct calls retain existing depth/config behavior.
3. A repeated-card regression proves the scraper continues until 20 accepted
   unique permalinks are found or four scrolls are consumed.
4. Existing LinkedIn and X auth, quality, canonicalization, media, duplicate,
   result-limit, and service-worker tests remain green.
5. Focused and full validation plus a deterministic service build pass; the
   exact successor installs ready with the prior verified release retained as
   rollback.
6. At most one X/LinkedIn canary uses 20-item ceilings, one attempt per lane,
   zero cost/model use, and stops at its first terminal receipt; recurring
   configuration and cadence remain unchanged.

## Execution Bounds

- implementation cycles: three red/green vertical slices;
- review/rework cycles: one;
- live provider attempts: one X/LinkedIn tick after installed-runtime gates;
- scroll limits: 100 explicit results and eight scrolls maximum per LinkedIn
  request;
- terminal stops: acceptance met, preflight failure, auth/profile uncertainty,
  worker timeout, provider restriction, or the single live tick terminalizes.

## Owned Write Surfaces

- `skills/last30days/scripts/lib/linkedin.py`;
- `skills/last30days/scripts/lib/service_acquisition_worker.py`;
- focused LinkedIn and worker tests;
- service version, runtime manifest, changelog, and release-version tests;
- this plan, `ROADMAP.md`, and append-only `RUNBOOK.md`.

## Definition Of Done

- installed runtime demonstrably honors a service-requested LinkedIn ceiling
  through accepted-unique bounded pagination, the one terminal canary is
  receipted, and recurring source/schedule state is unchanged.

### Checkpoint P0055-C01 | 2026-08-21

Plan version: 1

State transition:

- `linkedin_raw_card_limit_observed -> validated_source_correction`.

Progress classification:

- `outcome_progress`; the live 6/12 receipt is reproduced by minimized tests
  at both the worker boundary and browser capture loop.

Owned changes:

- LinkedIn item-limit propagation, proportional bounded scroll derivation,
  accepted-unique preview, and three focused regressions;
- Plan 0054 terminal reconciliation and Plan 0055 roadmap authority.

Validation evidence:

- the worker regression failed because `limit` was absent, then passed with
  `request.item_limit=20` propagated;
- the constructor regression failed at one scroll instead of four, then passed
  with the proportional bounded budget;
- the repeated-card regression failed at 16 accepted posts after raw count 22,
  then passed at 20 accepted unique posts after the fourth scroll;
- complete LinkedIn, X-browser, and acquisition-worker files pass with two
  expected live-smoke skips.
- focused runtime-package, release-version, source-log, and planning-authority
  suites pass, and the complete `uv run pytest -q` suite passes with expected
  opt-in skips;
- two service 0.3.54 builds are byte-identical at SHA-256
  `adbc281e359599391f7f716b5215e5f894e8a358409404602bd4c075a2a99874`.

Authority classification:

- `inherited_authority`; the operator approved the concrete repair recommended
  after the terminal 20/20 canary analysis.

Subagent status and reconciliation:

- `not_spawned`; current orchestration policy prohibits delegation.

Graphiti write status:

- pending installed-runtime and terminal-canary closeout.

Remaining acceptance criteria:

- commit and push, transactional install, and the single terminal canary
  remain.

Next action:

- commit and push the exact validated service 0.3.54 candidate before
  transactional installation.

### Checkpoint P0055-C02 | 2026-08-21

Plan version: 2

State transition:

- `validated_source_correction -> installed_identity_repair_waiting_fresh_canary_authority`.

Progress classification:

- `outcome_progress_with_live_gate`; pagination and exact browser acquisition
  are installed, but the only authorized canary failed before either scraper
  observed a post.

Runtime and canary evidence:

- source commit `91b6efb7a76f45dddd294bc0456d636dcd3fe40f` delivered the
  LinkedIn 20-item accepted-unique correction in service 0.3.54 and was pushed
  with exact remote readback;
- the single admitted X/LinkedIn 20/20 tick
  `tick-214741d5b5ea42fe21bb106f06dcab0d` terminalized
  `complete_degraded` in eight seconds with both lanes `route_stale`, zero
  observed/accepted/rejected items, zero incidents, and zero notifications;
- diagnosis proved X and LinkedIn were authenticated in physical PID 16807 at
  loopback CDP port 36603 under runtime profile `last30days-facebook`; the
  false auth surface came from an ambiguous retained session and later stale
  service profile labeling, not a logged-out browser;
- Route A was rebound without launching or closing Chrome. Route A now names
  `session:last30days-bound-social-20260821` on display `:10`; unrelated Route
  B remains bound to `session:p0204-a06` on display `:11`;
- service 0.3.57 adds fail-closed runtime identity recovery: runtime profile,
  user-data directory, live/reachable state, and exact loopback CDP port must
  all agree before a stale service browser row may be reused;
- installed 0.3.57 acquisition-only checks now pass for both X and LinkedIn on
  the exact social browser owner. No second tick or scrape was run.

Validation and release evidence:

- minimized regressions cover ambiguous-session exact CDP binding, retained
  profile-label recovery, and rejection of wrong runtime profile, user-data
  directory, or CDP port;
- focused social acquisition suites and the complete `uv run pytest -q` suite
  pass with expected opt-in skips;
- two service 0.3.57 builds and the repository artifact are byte-identical at
  SHA-256
  `d867d5955d4e26387f27cd0c75a1af06a3c757e55f1c198e95ea22363ca09b39`;
- installed service 0.3.57/schema 16 is ready and MCP 4.0.3-compatible with
  runtime manifest SHA-256
  `6388bf82c32a8942d5cce469dd782803bdea5118bc1b0f2d853f284d04981617`;
  service 0.3.56 is retained as rollback.

Authority and recurring-state boundary:

- the version 1 single live-attempt budget is consumed. Another tick requires
  fresh explicit operator authority and is not inferred from source/runtime
  repair work;
- Reddit and Facebook remain disabled; recurring `daily-default`, cadence,
  and ten-item X/LinkedIn ceilings remain unchanged.

Authority classification:

- `inherited_authority`; source, packaging,
  installation, route reconciliation, and acquisition-only validation were in
  scope, while another live tick requires fresh explicit operator authority.

Subagent status and reconciliation:

- `not_spawned`; current orchestration policy prohibits delegation.

Graphiti write status:

- deferred; plan, runbook, runtime, and tick receipts are the current durable
  evidence surfaces.

Remaining acceptance criteria:

- one freshly authorized X/LinkedIn 20/20 canary must reach the scraper quality
  loops and receipt actual observed, accepted, rejected, duplicate, permalink,
  and sponsored/promoted outcomes before this plan can close.

Next action:

- commit and push service 0.3.57 and the C02 receipts, then wait for fresh
  operator authority for one new 20/20 canary.

Checkpoint P0055-C02 is the current authority.

### Checkpoint P0055-C03 | 2026-08-21

Plan version: 3

State transition:

- `installed_identity_repair_waiting_fresh_canary_authority -> terminal_canary_exposed_runtime_lifecycle_owner_gap`.

Progress classification:

- `outcome_progress_with_new_blocker`; the fresh terminal receipt disproves
  scraper acceptance as the current boundary and identifies the exact runtime
  lifecycle rejection that occurs before post observation.

Fresh authority and preflight evidence:

- the operator explicitly authorized exactly one new X/LinkedIn 20/20 canary;
- installed service 0.3.57 reported ready and compatible with runtime manifest
  SHA-256
  `6388bf82c32a8942d5cce469dd782803bdea5118bc1b0f2d853f284d04981617`;
- direct runtime status proved PID 16807, runtime profile
  `last30days-facebook`, user-data directory identity, loopback CDP port 36603,
  and reachable X and LinkedIn targets;
- installed acquisition-only checks for both sources selected the same exact
  browser and session, `session:last30days-bound-social-20260821`, without
  launching another Chrome process;
- sanitized preflight `tick-e0f09130ba77d4f223bfe8529380d7c8`
  admitted exactly two lanes, one attempt and 20 items per lane, aggregate 40
  items, 100 network requests, 240 wall seconds, and zero cost/model budget.

Terminal receipt and diagnosis:

- tick `tick-e0f09130ba77d4f223bfe8529380d7c8` terminalized
  `complete_degraded` in 14 seconds; X and LinkedIn each receipted
  `agent_browser_error`, transient failure, zero attempted/observed/accepted/
  rejected posts, and empty rejection counts;
- agent-browser jobs `r622853` and `r702708` failed the two attach operations
  with `runtime_lifecycle_existing_owner_requires_explicit_transition`;
- the runtime owner registry still records the physical social process under
  logical browser `session:last30days-x-upgrade-live-20260820` in retained/
  orphaned ownership, while the exact service route and scraper use
  `session:last30days-bound-social-20260821`;
- the acquisition-only probe can recover and return that exact CDP browser, but
  the first scraper tab command re-enters the launch/attach lifecycle and is
  rejected because it does not perform an explicit ownership transition;
- no incidents, notifications, artifacts, source versions, derivatives, or
  model/cost usage were created. Because no post was observed, this canary
  contains no new evidence about ads, missing permalinks, duplicates, or
  acceptance quality.

Recurring-state and cleanup evidence:

- the owner-private temporary canary config was removed after terminal
  readback;
- normal config remains SHA-256
  `ffcfc71a72d2a6696077227436250a863fe7f258b7767bf9a2746226b5733054`;
- Reddit and Facebook remain disabled; `daily-default` remains enabled at one
  day with normal X/LinkedIn ceilings of ten and next boundary
  `2026-08-22T00:00:00Z`;
- the single C03 live attempt is consumed. No retry is authorized by this
  checkpoint.

Authority classification:

- `inherited_authority`; the operator supplied fresh authority for exactly one
  new canary, which is now terminal and exhausted.

Subagent status and reconciliation:

- `not_spawned`; current orchestration policy prohibits delegation.

Graphiti write status:

- deferred; the plan, runbook, database receipt, and agent-browser lifecycle
  jobs are the durable evidence surfaces.

Remaining acceptance criteria:

- repair or reconcile the explicit runtime-owner transition so the same exact
  social browser remains controllable from acquisition through the first tab
  command, then obtain fresh authority for any further live tick.

Next action:

- implement and validate the lifecycle-owner handoff correction without a
  provider retry; do not admit another live canary without fresh explicit
  operator authority.

Checkpoint P0055-C03 is the current authority.

### Checkpoint P0055-C04 | 2026-08-21

Plan version: 4

State transition:

- `terminal_canary_exposed_runtime_lifecycle_owner_gap -> installed_daemon_route_fix_canary_blocked_by_runtime_upgrade`.

Progress classification:

- `blocker_reduction_with_unexercised_live_fix`; the service alias/daemon-route
  defect is corrected and installed, while the single live proof stopped at a
  separate agent-browser workstation-upgrade admission gate.

Implementation and release evidence:

- a public-path regression first reproduced
  `runtime_lifecycle_existing_owner_requires_explicit_transition` when a
  retained service session alias was used for the first follow-on command;
- the adapter now preserves one unique daemon route from service-owned tab
  evidence while retaining the service session for ownership checks. Missing
  or ambiguous route evidence keeps the existing fail-closed path;
- focused Facebook/X/LinkedIn/agent-browser-config suites and the complete
  `uv run pytest -q` suite pass with expected opt-in skips;
- service artifact `last30days-service-0.3.58.tar.gz` has SHA-256
  `80f6917a20dfc881e86ef6a32e771077bd99e3699c083a6e00894f9fd4873b51`;
- installed service 0.3.58/schema 16 is ready and MCP 4.0.3-compatible with
  runtime manifest SHA-256
  `04008504fdae3ea1aafcf74dad793add40a3327312882433449dfbe1ac1cda77`;
  service 0.3.57 is retained as rollback.

Terminal canary evidence:

- sanitized preflight admitted prospective tick
  `tick-a678da2c70bded995195a865f8100f0f`, exactly X and LinkedIn, one attempt
  and 20 items per lane, aggregate 40 items, 100 requests, 240 wall seconds,
  and zero cost/model budget;
- that exact tick terminalized `complete_degraded` in under one second. Both
  lanes returned transient `agent_browser_error` with zero attempted,
  observed, accepted, and rejected posts, empty page signals, and no incident,
  notification, artifact, derivative, source-version, cost, or model effect;
- no agent-browser control job was retained for either provider. Immediate
  control-plane readback reproduced runtime-host admission failure, and
  workstation status showed `admissionDraining=true` while upgrade transaction
  `upgrade-f226f899-9828-4126-aece-40591c203c49` was
  `runtimes_transferring` at revision 5;
- the transaction later terminalized `failed_preserved_old_generation` at
  revision 7 with `candidate_activation_failed`; the old generation was
  preserved, admission draining cleared, but `runtimeConvergenceReady=false`
  leaves workstation readiness false;
- this timing and zero-job evidence classify the canary as blocked before the
  installed daemon-route code path. It does not disprove that fix and contains
  no new post-quality, ad, duplicate, or permalink evidence.

Recurring-state and attempt boundary:

- the owner-private temporary canary config was removed after terminal
  readback;
- normal config remains SHA-256
  `ffcfc71a72d2a6696077227436250a863fe7f258b7767bf9a2746226b5733054`;
  Reddit and Facebook remain disabled, `daily-default` remains enabled daily,
  normal X/LinkedIn ceilings remain ten, and the next boundary is
  `2026-08-22T00:00:00Z`;
- the single C04 live attempt is consumed. No retry is authorized by this
  checkpoint.

Authority classification:

- `human_gate`; the operator supplied fresh explicit authority for the
  daemon-route repair and exactly one post-fix X/LinkedIn 20/20 canary, and
  that live authority is now consumed.

Subagent status and reconciliation:

- `not_spawned`; current orchestration policy prohibits delegation.

Graphiti write status:

- deferred; source commit, installed-runtime receipt, plan, runbook, SQLite
  tick receipt, and workstation-upgrade receipt are the durable evidence.

Remaining acceptance criteria:

- complete or recover the agent-browser workstation upgrade until readiness is
  true, admission is not draining, and one stable retained runtime route is
  available; only a separately authorized later canary can prove the installed
  daemon-route fix and LinkedIn accepted-yield behavior live.

Next action:

- resolve the non-ready agent-browser workstation runtime-convergence state
  without running another provider attempt, then request fresh authority if a
  new live X/LinkedIn canary is still desired.

Checkpoint P0055-C04 is the current authority.
