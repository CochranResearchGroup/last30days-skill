# Plan 0055 | LinkedIn Accepted-Yield Repair

State: OPEN
Roadmap: P08
Plan version: 17
Date: 2026-08-21

## Objective

Make the governed X and LinkedIn browser lanes prioritize reliable retrieval:
honor service-admitted ceilings, pursue unique canonical post permalinks within
bounded scroll budgets, and defer semantic quality decisions until enrichment.

## Current State

- service 0.3.60/schema 16 is installed ready with 0.3.58 retained for
  rollback; the full repository suite passed with 2,677 tests and seven
  expected skips before installation;
- structurally valid short and lexically unmatched X and LinkedIn posts are
  retained with retrieval diagnostics. Only structural invalidity, date range,
  exact duplicate, deterministic promoted/sponsored labels, and deterministic
  navigation noise remain acquisition exclusions;
- topic search remains implemented and fixture-covered, but owner-private
  revision `operator-20260822-x-linkedin-home-feed-v1` disables the recurring
  X and LinkedIn OpenAI topic targets and enables their authenticated home-feed
  targets at the existing ten-item ceilings;
- YouTube retains its OpenAI topic target, Reddit and Facebook remain disabled,
  and `daily-default` is enabled/ready for `2026-08-23T00:00:00Z` on the exact
  full recurring-config digest;
- the one installed feed canary terminalized with zero observed posts because
  both Agent Browser launch-adoption jobs failed at
  `runtime_lifecycle_process_tree_record_missing` before extraction;
- Agent Browser transaction `upgrade-0df91191-ad9b-4eb9-aa85-2f92e9729563`
  is accepted on selected generation `0.28.0-4b975a51aa89-d0782705d5ff`;
  dashboard ingress, operator journey, payload, rollback, convergence, and
  selected-generation readiness are all true;
- the operator explicitly authorized one retry after that acceptance. Manual
  tick `tick-070bfe28cc98550d12f0d940ccdfac2e` used only X and LinkedIn, one
  attempt and ten-item ceiling per lane, zero model/cost budget, and the
  unchanged durable profile `last30days-facebook`;
- Agent Browser's reviewed candidate reconciled the exact absent generation-5
  owner from `closing/owned` to `terminal/satisfied` with absent-process-group
  and absent-profile-lock evidence while preserving `last30days-facebook`;
- the operator authorized one new tick after that repair. Manual tick
  `tick-7224876f30d729e41ff5435b387be4df` again used only X and LinkedIn, one
  attempt and ten-item ceiling per lane, zero model/cost budget, and the same
  durable profile;
- the operator subsequently authorized three separately receipted attempts per
  service at a temporary 20-item ceiling. Both authenticated home feeds were
  reached without authentication or page-signal incidents. X attempts two and
  three each observed 32 cards and accepted 11 unique in-range posts; LinkedIn
  observed 30 cards on every attempt and accepted at most one;
- the 20-item outcome remains unproven. X is bounded by repeated status cards
  before unique yield reaches 20. LinkedIn deterministically identifies five
  sponsored/ad cards, but its remaining candidates are predominantly rejected
  for missing permalink, date, or author metadata. This is a retrieval and
  scraper-normalization blocker, not a semantic quality conclusion;
- all three attempts per service are consumed. The temporary run configuration
  was removed, while the recurring ten-item configuration and `daily-default`
  remain unchanged and ready.

## Scope

- propagate the governed acquisition `item_limit` into `search_linkedin`;
- clamp explicit ceilings to 100 and derive at most eight scrolls at five
  accepted items per scroll budget;
- stop LinkedIn scrolling only when accepted unique yield meets the requested
  ceiling or the bounded scroll budget is exhausted;
- preserve authentication, checkpoint, rate-limit, canonical permalink,
  author, date-window, deterministic promoted/sponsored, navigation-noise,
  media, and exact-duplicate handling;
- retain short-text and absent lexical topic overlap as per-item diagnostics
  without excluding otherwise structurally valid X or LinkedIn posts;
- carry an explicit feed surface through recurring and isolated-worker
  boundaries, navigate the authenticated X and LinkedIn home feeds, and retain
  topic search as an on-demand capability;
- preserve the installed home-feed configuration and admit only the exact
  operator-authorized, service-scoped retry budget.

## Non-Goals

- do not reinterpret deterministically labeled promoted/sponsored cards or
  navigation-only cards as posts;
- do not introduce semantic ranking, GraphRAG judgment, heuristic spam
  classifiers, or content-quality thresholds during acquisition;
- do not change working X accepted-unique pagination;
- do not re-enable Reddit or Facebook, alter `daily-default` cadence, or change
  the recurring ten-item X/LinkedIn ceilings;
- do not add unbounded scrolling, click every `Show more`, launch another
  browser, or use cost/model budgets;
- do not treat a 20-item ceiling as a guarantee that the source exposes 20
  acceptable unique posts within the finite capture window.

## Acceptance Criteria

1. Worker regressions prove the admitted item limit and explicit surface reach
   the appropriate X and LinkedIn browser adapters.
2. Feed fixtures prove direct home navigation without topic lexical filtering,
   while topic-search fixtures remain green.
3. Existing LinkedIn and X auth, structural validation, canonicalization,
   deterministic ad/noise exclusion, media, duplicate, result-limit, and
   service-worker tests remain green; fixtures prove short and lexically
   unmatched posts are retained with diagnostic signals.
4. Focused and full validation plus a deterministic service build pass; the
   exact successor installs ready with the prior verified release retained as
   rollback.
5. Recurring readback proves only X and LinkedIn switch from their OpenAI topic
   targets to authenticated home feeds; cadence and source ceilings remain.
6. At most one X/LinkedIn feed canary uses one attempt per lane, zero cost/model
   use, and stops at its first terminal receipt.
7. A current-generation browser with receipt-bearing lifecycle ownership
   serves a named tab request before any successor feed canary is authorized.

## Execution Bounds

- implementation cycles: three red/green vertical slices;
- review/rework cycles: one;
- live provider attempts: the one X/LinkedIn feed tick is consumed; no retry
  until the terminal-replacement correction is transactionally installed, a
  current-generation browser passes the named-tab gate, and the operator
  supplies fresh attempt authority;
- scroll limits: 100 explicit results and eight scrolls maximum per LinkedIn
  request;
- terminal stops: acceptance met, preflight failure, auth/profile uncertainty,
  worker timeout, provider restriction, or the single live tick terminalizes.

## Owned Write Surfaces

- `skills/last30days/scripts/lib/linkedin.py`;
- `skills/last30days/scripts/lib/x_browser.py`;
- `skills/last30days/scripts/lib/service_acquisition_worker.py`;
- durable tick/collection contracts, worker adapters, and focused source tests;
- service version, runtime manifest, changelog, and release-version tests;
- this plan, `ROADMAP.md`, and append-only `RUNBOOK.md`.

## Definition Of Done

- installed runtime demonstrably observes authenticated X and LinkedIn home
  feed posts under the recurring surface contract, preserves deterministic
  ad/noise exclusion, and retains topic search for on-demand use. This remains
  open on the current-generation browser lifecycle and live feed proof.

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

### Checkpoint P0055-C05 | 2026-08-21

Plan version: 5

State transition:

- `installed_daemon_route_fix_canary_blocked_by_runtime_upgrade -> workstation_topology_recovered_acceptance_receipt_blocked`.

Progress classification:

- `blocker_reduction_with_shared_runtime_acceptance_blocker`; managed runtime
  topology is healthy again, but an accepted workstation transaction still
  does not exist and the provider gate remains closed.

Fresh authority and recovery evidence:

- the operator explicitly authorized workstation-readiness recovery followed
  by exactly one X/LinkedIn 20/20 canary only after all readiness axes were
  true and stable;
- exact recovery of transaction
  `upgrade-7d44ef27-0421-40da-9c64-570da55b217e` first stopped because its
  candidate process was still live and then because another canonical
  controller held the workstation lock. That controller subsequently
  preserved the old generation;
- one receipt-bearing reconciliation completed after the monitor backoff,
  retained all protected browser state, terminated zero processes, and
  restored a healthy runtime-monitor receipt. The managed interlock timer is
  active and waiting;
- a concurrent agent-browser source-lane install transaction
  `upgrade-76174566-40ae-490d-aeac-f5df3d9b2e27` failed post-commit
  reconciliation with stale-executable and multiple-listener findings, while
  a separate Odollo-owned transaction
  `upgrade-9de3a8a8-e56d-4893-b673-54206750e661` failed candidate activation;
- the bounded selected-payload transaction
  `upgrade-48d69bd0-1408-48f4-a5e4-497b06323f32` also terminalized
  `failed_preserved_old_generation` at revision 7 with
  `candidate_activation_failed`. No manual process kill, owner-registry edit,
  browser rehome, or retained-browser cleanup was performed;
- the agent-browser source worktree is owned by another active lane, is 66
  commits ahead of its remote, and contains an untracked note, so this plan did
  not mutate that repository or compete with its source repair.

Terminal readiness evidence:

- workstation admission is not draining and the selected generation is
  `0.28.0-a02d9e3a8a3a-a4d5bb2702b2`;
- doctor reports exactly one current executable listener/runtime host, one
  dashboard process, one executable generation, zero legacy daemons, no
  multiplicity issues, and a healthy runtime monitor;
- the only doctor issue is `workstation_upgrade_readiness_not_ready`:
  payload, selected generation, dashboard ingress, operator journey, and
  rollback are ready, while `runtimeConvergenceReady=false` because the latest
  transaction is failed rather than accepted;
- no X/LinkedIn preflight, tick, provider attempt, temporary config, incident,
  notification, artifact, derivative, model use, or cost occurred.

Recurring-state and attempt boundary:

- the freshly authorized provider canary was not consumed because the
  workstation gate never became fully ready;
- Reddit and Facebook remain disabled; `daily-default`, cadence, and normal
  ten-item X/LinkedIn ceilings remain unchanged.

Authority classification:

- `human_gate`; recovery and one post-readiness canary were explicitly
  authorized, but the provider portion remains gated and unconsumed.

Subagent status and reconciliation:

- `not_spawned`; current orchestration policy prohibits delegation.

Graphiti write status:

- deferred; this plan, runbook, runtime receipts, and sibling-worktree custody
  readback are sufficient durable evidence for the open checkpoint.

Remaining acceptance criteria:

- the active agent-browser source owner must produce one accepted workstation
  transaction with every readiness axis true and no competing installer;
- only then may the already authorized single X/LinkedIn 20/20 canary proceed
  to its first terminal receipt.

Next action:

- preserve the healthy managed topology and the other owner’s source lane;
  await an accepted workstation transaction, verify stable readiness, then run
  at most the one still-unconsumed provider canary.

Checkpoint P0055-C05 is the current authority.

### Checkpoint P0055-C06 | 2026-08-21

Plan version: 6

State transition:

- `workstation_topology_recovered_acceptance_receipt_blocked -> terminal_canary_confirms_runtime_owner_transition_gap`.

Progress classification:

- `outcome_progress_with_reopened_blocker`; the accepted workstation receipt
  removes upgrade readiness as the cause and the terminal live attempt isolates
  the remaining failure to retained social-browser lifecycle ownership before
  either scraper can observe a post.

Fresh authority and readiness evidence:

- the operator requested another try, authorizing exactly the previously
  unconsumed X/LinkedIn 20/20 canary;
- two consecutive workstation samples and a final pre-enqueue gate agreed on
  accepted transaction `upgrade-3d5cf3e2-72a7-4b85-8de9-d49b67f9c048`,
  selected generation `0.28.0-fb5a8ef317c2-9cf9b4f6919d`, every readiness
  axis true, no admission drain, one runtime host, one dashboard, one
  executable generation, zero legacy daemons, and a healthy runtime monitor;
- no competing workstation installer was present. Both no-launch access plans
  selected authenticated profile `last30days-facebook`, compatible
  `stealthcdp_chromium`, and no manual seeding requirement;
- the access plans also exposed one retained lease with no compatible reusable
  live browser and recommended waiting rather than launching a duplicate.

Preflight and terminal receipt:

- mode-0600 temporary config changed only revision, X and LinkedIn provider
  item ceilings from ten to 20, and aggregate item capacity from 23 to 43;
- source-scoped preflight was `ready` for exact tick
  `tick-acafacd4f3bcd7579ad4797001fc4375` at config digest
  `sha256:5856cb1ee34da53a7693ebe0111c75f07aa5c08181e19b601bfc21c8c1c3f0e4`;
  it bound exactly X and LinkedIn, one attempt and 20 items per lane, aggregate
  two attempts/40 items/100 requests/240 wall seconds, and zero cost/model
  budget;
- the exact tick was enqueued once and terminalized `complete_degraded` in
  about eight seconds. X consumed four provider wall seconds and LinkedIn two;
  each used one attempt and one request with zero attempted, observed,
  accepted, or rejected posts;
- both results are transient `agent_browser_error` with empty page signals and
  rejection counts. X job `r256061` and LinkedIn job `r361567` both failed
  launch with `runtime_lifecycle_existing_owner_requires_explicit_transition`;
- the accepted workstation migration classifies
  `session:last30days-bound-social-20260821` as `external_observed` /
  `manual_preservation` without a receipt, preserves
  `session:last30days-x-upgrade-live-20260820` as route-less
  `manual_preserve_only`, and receipt-adopts only `session:p0204-a06`.
  Therefore the failure is a runtime/session ownership limitation before
  scraper classification, not an ad, permalink, authentication, or legitimate
  post rejection;
- no incident, notification, artifact, derivative, source version, model use,
  or cost was created.

Recurring-state and cleanup evidence:

- the temporary config and directory were removed after terminal readback;
- normal config remains SHA-256
  `ffcfc71a72d2a6696077227436250a863fe7f258b7767bf9a2746226b5733054`;
  Reddit/Facebook remain disabled, `daily-default` remains enabled and ready,
  normal X/LinkedIn ceilings remain ten, and the next boundary is
  `2026-08-22T00:00:00Z`;
- SQLite quick check is `ok`; workstation readiness remains fully true after
  the canary.

Authority classification:

- `human_gate`; the one provider canary authorized by the operator is now
  consumed and terminal. No retry is authorized by this checkpoint.

Subagent status and reconciliation:

- `not_spawned`; current orchestration policy prohibits delegation.

Graphiti write status:

- deferred; plan, runbook, SQLite receipt, agent-browser jobs, accepted
  workstation transaction, and runtime-migration readback are sufficient
  durable evidence.

Remaining acceptance criteria:

- create a receipt-bearing owner/session route for the exact authenticated
  social browser, or route the scraper through an already adopted compatible
  owner, without launching a duplicate profile process;
- deterministically validate acquisition through the first follow-on tab
  command before any later provider attempt.

Next action:

- repair the retained social-browser owner transition without provider work,
  prove one exact controllable browser/profile/session identity across
  acquisition and tab commands, then stop at the live-attempt gate.

Checkpoint P0055-C06 is the current authority.

### Checkpoint P0055-C07 | 2026-08-21

Plan version: 7

State transition:

- `terminal_canary_confirms_runtime_owner_transition_gap -> owner_receipted_stale_tab_route_repaired_retry_withheld`.

Progress classification:

- `blocker_reduction_with_consumed_canary`; browser ownership is receipted and
  the remaining failed attempt isolated then repaired a stale per-tab daemon
  route, but the repaired route has not received another provider attempt.

Ownership and route evidence:

- `handoff resume` adopted logical browser
  `session:last30days-x-upgrade-live-20260820` into owner generation 9 with
  receipt
  `owner-transfer-a5913eb8118312b002516d81d7c1cc25c852c979bda44e7f8f708bfd38050bf2`;
  Chrome PID 16807, CDP port 36603, browser UUID
  `a21f8ae7-c39b-4307-a3e0-9528b9d9a190`, profile, and authenticated X and
  LinkedIn targets did not change;
- one candidate-owned blank-tab open/close transaction succeeded immediately
  after transfer. Two stale exclusive service-session aliases were then
  released with `cleanup=detach`; neither browser process was closed;
- X and LinkedIn access plans now report one compatible browser,
  `reuse_existing_browser`, `tab_new`, `duplicatePressure=false`, and
  `duplicateProcessAllowed=false` for
  `session:last30days-owner-repair-20260821-c07`;
- the terminal provider receipt showed the adapters still selected stale tab
  daemon route `handoff-c87d81798683ee75`. Agent-browser jobs `r647723` and
  `r229031` rejected `tab_switch` and `evaluate` respectively with
  `runtime_owner_observation_only: candidate cannot issue browser effects before owner compare-and-swap`;
- retained blank target `5EA7B954B7E85DA5DC177B537C70C2E6` now carries the
  candidate session ID. This makes `_daemon_session_route` return no unique
  stale route, so both installed acquisition clients deterministically return
  browser/session `session:last30days-owner-repair-20260821-c07` /
  `last30days-owner-repair-20260821-c07`;
- through that exact session, X target
  `ED7F37E648270B2D8CCCCD8206832086` switched and evaluated `x.com`, and
  LinkedIn target `DF31B25DA1139FB5010792EF14C70DE3` switched and evaluated
  `www.linkedin.com`.

Terminal canary receipt:

- mode-0600 temporary config changed only revision, X/LinkedIn item ceilings
  from ten to 20, and aggregate config item capacity from 23 to 43;
- preflight was `ready` for exact tick
  `tick-c944e818e7a9fb5af871a285e9177b75` at config digest
  `sha256:58de0d5fc7ad35f6b71b1dd7d0eb2c58b93b8e40b9666832981c72f12275386e`,
  with exactly two attempts, 40 items, 100 requests, 240 wall seconds, and zero
  cost/model budget;
- the tick was enqueued once and terminalized `complete_degraded`. X provider
  attempt `provider-attempt-0339fb5880cfc13176aff39cbf3ee869` and LinkedIn
  attempt `provider-attempt-0eb8400f1d1e0dc2371c40eb69160340` each consumed
  one request and four wall seconds with zero attempted, observed, accepted, or
  rejected posts;
- page signals and rejection counts are empty. The failure occurred before ad,
  permalink, authentication, or post-quality classification. No retry ran.

Recurring-state and final health evidence:

- the temporary config and directory were removed. Normal config remains
  SHA-256 `ffcfc71a72d2a6696077227436250a863fe7f258b7767bf9a2746226b5733054`;
  Reddit/Facebook remain disabled, normal X/LinkedIn ceilings remain ten, and
  `daily-default` is ready for `2026-08-23T00:00:00Z`;
- active tick attempts are zero and SQLite quick check is `ok`;
- workstation admission remains ready with every readiness axis true and no
  drain. Global doctor still reports unrelated `stealthcdp-default` duplicate
  lease pressure plus one cleanup-obligation diagnostic; the exact social
  access plan itself reports zero duplicate pressure, and the receipted social
  lane remains effect-capable.

Authority classification:

- `human_gate`; the operator-authorized 20/20 canary is consumed. The
  post-terminal route repair used no provider attempt and does not authorize a
  second tick.

Subagent status and reconciliation:

- `not_spawned`; current orchestration policy prohibits delegation.

Graphiti write status:

- deferred; this checkpoint, the runbook, SQLite receipt, owner-transfer
  receipt, and agent-browser job records are sufficient durable evidence.

Remaining acceptance criterion:

- run at most one newly authorized X/LinkedIn canary through the now-proven
  candidate session and inspect accepted/rejected post counts; do not infer
  authority from the route repair.

Next action:

- stop. If the operator explicitly requests another attempt, recheck the same
  owner receipt, PID/CDP identity, candidate session route, recurring-config
  digest, and zero active attempts immediately before one bounded tick.

Checkpoint P0055-C07 is superseded by P0055-C08 below.

### Checkpoint P0055-C08 | 2026-08-21

Plan version: 8

State transition:

- `owner_receipted_stale_tab_route_repaired_retry_withheld -> corrected_route_live_canary_succeeds_below_ceiling`.

Progress classification:

- `outcome_progress`; the corrected candidate-owned route produced accepted
  posts from both X and LinkedIn and eliminated the prior pre-observation
  owner-route failure.

Live canary receipt:

- installed service 0.3.58, MCP 4.0.3, database schema 16, and runtime manifest
  `04008504fdae3ea1aafcf74dad793add40a3327312882433449dfbe1ac1cda77`
  were compatible and ready before the attempt;
- both installed acquisition clients resolved browser/session
  `session:last30days-owner-repair-20260821-c07` /
  `last30days-owner-repair-20260821-c07`. Browser PID 16807 remained healthy
  on CDP endpoint
  `ws://127.0.0.1:36603/devtools/browser/a21f8ae7-c39b-4307-a3e0-9528b9d9a190`;
- mode-0600 temporary config changed only revision, aggregate item capacity
  from 23 to 43, and X/LinkedIn item ceilings from ten to 20. Preflight was
  `ready` for exact tick `tick-da3b0c6dbe61301e7371971f9440d9cb`
  at config digest
  `sha256:cf620a72aa45e96e9c5bc906db9d074e57fc0e9b3be35eabe550a8c3fb2d4710`,
  with two attempts, 40 items, 100 requests, 240 wall seconds, and zero
  cost/model budget;
- the tick was enqueued once and no retry ran. X attempt
  `provider-attempt-2d31b58574cae91e6dfe451e8f8d7317` observed 45, accepted
  11, and rejected 34: 15 `duplicate_status`, eight `insufficient_text`, and
  11 `off_topic`;
- LinkedIn attempt `provider-attempt-832c826a68b2818a92b7ba2d5ca2da47`
  observed 15, accepted three, and rejected 12, all `duplicate`. Each accepted
  item has a canonical `/feed/update/urn:li:activity:.../` permalink;
- both provider attempts and lanes are `success`, with no provider failure
  class, incident, coverage gap, authentication signal, or browser error.

Degraded-stage disposition:

- the overall tick is `complete_degraded` because three semantic sidecars for
  the repeated LinkedIn profile-photo asset returned safe error
  `analysisoutputmissing`;
- this occurred after post acceptance and raw publication. Collection, media,
  OCR, lexical indexing, semantic indexing, and head promotion completed, so
  the degraded label is not a scraper, auth, or post-permalink failure.

Recurring-state and final health evidence:

- the temporary config directory was moved to the user trash. Normal config
  remains SHA-256
  `ffcfc71a72d2a6696077227436250a863fe7f258b7767bf9a2746226b5733054`;
  Reddit/Facebook remain disabled, normal X/LinkedIn ceilings remain ten, and
  `daily-default` is ready for `2026-08-23T00:00:00Z`;
- active tick attempts are zero, SQLite quick check is `ok`, and the social
  browser remains `ready` on unchanged PID/CDP identity with four retained
  tabs;
- global workstation upgrade status still reports a separate ambiguous-runtime
  transaction and `runtimeConvergenceReady=false`; the exact service browser
  health and installed-adapter route were nevertheless effect-proven by both
  successful provider attempts. Do not use the canary as acceptance evidence
  for that wider workstation transaction.

Authority classification:

- `human_gate`; the newly authorized one-shot canary is consumed and terminal.
  No second attempt or scraper mutation is authorized by this receipt.

Subagent status and reconciliation:

- `not_spawned`; current orchestration policy prohibits delegation.

Graphiti write status:

- deferred; this checkpoint, the runbook, SQLite tick receipt, and retained
  browser evidence are the durable source-backed record.

Remaining acceptance criterion:

- the browser-route blocker is resolved. The 20-item ceiling remains a ceiling,
  not a yield guarantee: X accepted 11 after quality/duplicate gates and
  LinkedIn exposed only 15 observed cards, of which 12 were duplicates.

Next action:

- stop at the terminal receipt. If work resumes, inspect the repeated LinkedIn
  card set and X insufficient-text/off-topic rejections as a new bounded
  scraper-analysis packet before changing acceptance gates.

Checkpoint P0055-C08 is superseded by P0055-C09 below.

### Checkpoint P0055-C09 | 2026-08-21

Plan version: 9

State transition:

- `corrected_route_live_canary_succeeds_below_ceiling -> rejection_classes_adjudicated_observability_gap_isolated`.

Progress classification:

- `blocker_reduction`; the underfill is now separated into legitimate duplicate
  suppression, a LinkedIn scroll-progress limitation, and X cases that need
  retained item-level evidence before their quality decision can be trusted.

LinkedIn rejection adjudication:

- the accepted set contains exactly three canonical activity permalinks:
  `urn:li:activity:7496746901808144384`,
  `urn:li:activity:7496747030405459970`, and
  `urn:li:activity:7496746415675670528`;
- for an explicit limit of 20, `search_linkedin` derives four bounded scrolls.
  The retained Agent Browser job sequence confirms one initial extraction and
  four successful scroll/extraction pairs;
- `LinkedInScraper.search` appends every extraction to `raw_candidates`.
  `_quality_gate` first validates permalink, meaningful text, navigation noise,
  author, date, sponsored state, and topic relevance; only candidates with no
  rejection reason reach duplicate detection;
- the durable outcome is 15 observed, three accepted, and 12 duplicates with no
  other rejection class. Therefore the 12 are repeated observations of the
  same three valid, non-sponsored posts, not 12 distinct ads or malformed
  posts;
- disposition: `legitimate_deduplication_with_scraper_progress_limitation`.
  Duplicate suppression is correct, but four successful page-scroll commands
  failed to expose any new unique card.

X rejection adjudication:

- `_quality_gate` validates canonical status permalink, author, evidence-text
  length, promoted state, date range, and topic overlap before `_dedupe_items`
  can emit `duplicate_status`. The 15 duplicate-status observations are
  therefore repeated quality-passing, non-promoted posts; disposition
  `legitimate_deduplication`;
- the 11 `off_topic` items necessarily had canonical permalinks, authors, at
  least 30 evidence characters, non-promoted state, and in-range dates, but the
  extracted tweet, quote, and media-alt evidence contained no `OpenAI` token
  overlap. They may be legitimate X statuses returned because the match lived
  in unextracted card/link context; disposition `needs_evidence` rather than a
  confirmed valid rejection;
- the eight `insufficient_text` items had canonical permalinks and authors but
  fewer than 30 extracted evidence characters. Because this branch precedes
  promoted, date, and relevance checks, the receipt cannot determine whether
  they were ads, out of range, irrelevant, or valid short posts; disposition
  `needs_evidence`.

Durable evidence gap:

- `XRunDiagnostics` retains up to 32 bounded rejected-candidate records with
  reason, native status ID, text/context lengths, quote-context presence, and
  media count;
- `AcquisitionWorkerTickAdapter` copies only `diagnostics.rejection_counts`
  into `ProviderResult`; it does not persist `rejected_candidates`. Agent
  Browser job records retain command success but not evaluate payloads;
- the terminal tick therefore supports aggregate classification but not
  item-level review of the 19 X quality rejects. No source retry or browser
  command was run during this investigation.

Authority classification:

- `inherited_authority`; the operator authorized the bounded rejection review.
  The review changed no scraper code, quality gate, recurring configuration,
  browser state, or provider attempt boundary.

Subagent status and reconciliation:

- `not_spawned`; current orchestration policy prohibits delegation.

Graphiti write status:

- deferred; this checkpoint, the runbook, CodeGraph source readback, SQLite
  receipt, and retained Agent Browser jobs are the durable evidence.

Remaining acceptance criterion:

- preserve bounded rejected-candidate evidence through the tick receipt, then
  adjudicate X cases from exact status IDs before changing any acceptance gate;
- make LinkedIn scroll progress observable by comparing newly discovered
  canonical IDs per scroll and classify a successful scroll with zero new IDs
  as pagination stagnation.

Next action:

- implement one provider-neutral bounded rejection-evidence field from worker
  diagnostics through `ProviderResult` persistence, plus LinkedIn per-scroll
  unique-ID progress diagnostics. Validate with fixtures only before any live
  retry.

Checkpoint P0055-C09 is superseded by P0055-C10 below.

### Checkpoint P0055-C10 | 2026-08-22

Plan version: 10

State transition:

- `rejection_classes_adjudicated_observability_gap_isolated -> retrieval_first_acceptance_candidate_built`.

Progress classification:

- `outcome_progress`; acquisition no longer discards structurally valid X or
  LinkedIn posts merely because their extracted content is short or lacks a
  lexical topic token.

Product decision:

- retrieval reliability now precedes semantic understanding and content
  quality policy;
- current and future acquisition surfaces should preserve canonical, in-range
  posts from search/topic feeds, the operator's home feed, and configured
  profile feeds before GraphRAG or another enrichment layer interprets them;
- acquisition-time exclusion is limited to structural invalidity, exact
  duplicates, deterministic promoted/sponsored labels, and deterministic
  non-post/navigation noise. No heuristic spam classifier was added.

Owned changes:

- X and LinkedIn retain short or lexically unmatched posts and attach bounded
  `short_text` or `no_lexical_topic_overlap` retrieval signals to item metadata;
- canonical permalink, author, requested date window, deterministic
  promoted/sponsored or navigation-noise exclusion, and exact URL
  deduplication remain hard acquisition gates;
- focused pagination fixtures now use deterministically promoted cards when
  proving that accepted-yield scrolling continues past rejected observations;
- service candidate 0.3.59 and its runtime manifest/changelog/version evidence
  were built without installing or adopting the candidate.

Validation evidence:

- focused X, LinkedIn, runtime-package, release-version, and worker validation:
  107 passed and two environment-dependent tests skipped;
- full repository suite reached 2,667 passed, seven skipped, and six subtests
  passed; its sole failure was the expected temporary header/checkpoint version
  mismatch corrected by this checkpoint;
- deterministic service artifact
  `dist/service/last30days-service-0.3.59.tar.gz` built with SHA-256
  `d1b4dcdb79552d197476f521aff2f0436044d154d3e183f4f388622e53e952a2`.

Runtime boundary:

- installed service 0.3.58, recurring X/LinkedIn ten-item ceilings,
  Reddit/Facebook disabled state, schedule cadence, and retained browsers are
  unchanged. No live provider attempt ran.

Authority classification:

- `inherited_authority`; the operator explicitly replaced acquisition-time
  quality filtering with retrieval-first acceptance and deferred GraphRAG and
  quality decisions until coverage is dependable.

Subagent status and reconciliation:

- `not_spawned`; current orchestration policy prohibits delegation.

Graphiti write status:

- `graphiti_write_pending`; provider readiness passed, but job
  `7e9c6475-d08d-4a17-8b79-8206d4586a6e` timed out during edge extraction
  after 120 seconds without creating a visible episode. This checkpoint,
  Runbook Turn 319, commit `e88f80d`, and test/build receipts remain the
  authoritative durable record; retry at the next non-trivial closeout.

Remaining acceptance criteria:

- rerun the authority audit and focused suite after this checkpoint;
- design the next bounded source-neutral surface packet for home-feed,
  topic/search-feed, and configured-profile coverage;
- install or live-test 0.3.59 only under a separately explicit runtime packet.

Next action:

- map the current collection-spec surface model to X and LinkedIn browser
  navigation so the next packet expands retrieval coverage without coupling it
  to semantic ranking or quality thresholds.

Checkpoint P0055-C10 is the current authority.

Checkpoint P0055-C10 is superseded by P0055-C11 below.

### Checkpoint P0055-C11 | 2026-08-22

Plan version: 11

State transition:

- `retrieval_first_acceptance_candidate_built -> authenticated_home_feed_candidate_built`.

Progress classification:

- `outcome_progress`; the source-neutral feed surface now reaches the isolated
  X and LinkedIn workers and each browser adapter can collect directly from the
  authenticated home feed without converting the feed selector into a search.

Product decision:

- retain topic search as an on-demand acquisition capability;
- retire the recurring X and LinkedIn OpenAI topic targets only by replacing
  them with explicit authenticated home-feed targets;
- leave the YouTube OpenAI topic target and disabled Reddit/Facebook targets
  unchanged;
- apply no semantic ranking to home-feed posts. Acquisition continues to
  exclude only structural invalidity, out-of-window items, exact duplicates,
  deterministic promoted/sponsored labels, and deterministic navigation noise.

Owned changes:

- `surface_kind` crosses both durable-tick and recurring-collection worker
  boundaries while legacy topic requests preserve their serialized shape;
- X navigates `https://x.com/home` under task `x-feed`; LinkedIn navigates
  `https://www.linkedin.com/feed/` under task `linkedin-home-feed`;
- feed items receive neutral acquisition relevance and an authenticated-feed
  provenance statement, with no lexical-topic-overlap diagnostic;
- strict tick validation now requires a supported surface and a matching
  selector while retaining the installed `query` alias for topic targets;
- service candidate 0.3.60 supersedes the uninstalled 0.3.59 candidate.

Validation evidence:

- 226 focused tests collected; the focused contract, tick, collection, worker,
  X, LinkedIn, packaging, and release suite passed with two expected
  environment-dependent skips;
- full repository suite: 2,677 passed and seven expected tests skipped;
- deterministic service artifact
  `dist/service/last30days-service-0.3.60.tar.gz` built with SHA-256
  `b45af3b07b10108f9dcd5eba5230cda9378f14b9430a4b5589a2809dc6a18428`.

Runtime boundary:

- installed service remains 0.3.58/schema 16 and ready with runtime manifest
  `04008504fdae3ea1aafcf74dad793add40a3327312882433449dfbe1ac1cda77`;
- recurring configuration, daily schedule, browser state, and provider attempt
  counts are unchanged. No live feed scrape has run at this checkpoint.

Authority classification:

- `inherited_authority`; the operator explicitly selected direct home-feed
  scraping while preserving search capability.

Subagent status and reconciliation:

- `not_spawned`; current orchestration policy prohibits delegation.

Graphiti write status:

- pending installed-runtime closeout; this plan, Runbook Turn 320, source,
  fixtures, and build receipt are the current durable authority.

Remaining acceptance criteria:

- commit and push the exact candidate;
- transactionally install 0.3.60 with 0.3.58 retained for rollback;
- replace only the recurring X and LinkedIn topic targets with explicit home
  feeds and verify schedule/config readback before any bounded feed canary.

Next action:

- execute the reversible installed-runtime/config transition, then run at most
  one X/LinkedIn feed canary and adjudicate its terminal receipt.

Checkpoint P0055-C11 is the current authority.

Checkpoint P0055-C11 is superseded by P0055-C12 below.

### Checkpoint P0055-C12 | 2026-08-22

Plan version: 12

State transition:

- `authenticated_home_feed_candidate_built -> home_feed_runtime_adopted_browser_lifecycle_blocked`.

Progress classification:

- `blocker_reduction`; recurring X and LinkedIn collection now selects the
  authenticated home feeds, while the first installed canary isolated an
  Agent Browser lifecycle-adoption failure before either scraper observed a
  post.

Installed and recurring state:

- exact service 0.3.60/schema 16 is installed ready with runtime-manifest
  SHA-256 `dae4c5ae4da4fdbde820e241a4f41e1f6361ced2f1b39fc4edb9a463de3fbb95`;
  service 0.3.58 remains the `previous` rollback release;
- owner-private revision `operator-20260822-x-linkedin-home-feed-v1` disables
  only the recurring X and LinkedIn OpenAI topic targets and enables
  `operator-20260822-x-home-feed` and
  `operator-20260822-linkedin-home-feed`; the YouTube OpenAI topic target and
  disabled Reddit/Facebook targets are unchanged;
- `daily-default` is enabled/ready on config digest
  `sha256:9238e351363d0e4d37fa965c748df53012ae9a217231901fef60a720413ad417`,
  with next boundary `2026-08-23T00:00:00Z` and no last error;
- config replacement failed closed as designed. The first guarded rebind used
  the scoped canary digest instead of the full recurring digest, was rejected,
  and admitted no tick; the corrected full-digest rebind restored the schedule.
  Both schedule-replacement events remain in append-only history;
- pre-transition database backup
  `/home/ecochran76/.local/share/last30days/backups/research-pre-home-feed-20260822.db`
  and the live database both pass SQLite `quick_check`.

Canary evidence:

- one authorized two-lane feed canary, tick
  `tick-e2c6e03fb5f45d9e7ff9efffa7b7ae7a`, terminalized
  `complete_degraded`; X attempt
  `provider-attempt-8be8c7a110617cb76032717e12523ba6` and LinkedIn attempt
  `provider-attempt-9a735fa1edc59d35c810f02ecdacea4e` each failed transiently
  with safe code `agent_browser_error` and zero attempted, observed, accepted,
  or rejected posts;
- Agent Browser retained jobs `r752042` and `r129542`, submitted during the
  two provider attempts, are failed `launch` jobs with exact error
  `runtime_lifecycle_process_tree_record_missing`. Both lack service, agent,
  and task labels, so the named `x-feed` and `linkedin-home-feed` traces are
  empty;
- current no-launch access plans still select authenticated profile
  `last30days-facebook`, require no manual authentication, and recommend reuse
  of browser `session:last30days-owner-repair-20260821-c07` in session
  `orphan-1d5e6832ce1b475f`. The browser is reported ready and its OS process
  tree is live, but the upgraded runtime cannot adopt it without the missing
  lifecycle ownership record;
- fresh OS readback finds one root Chrome process for that profile and 21
  profile processes using approximately 2.5 GiB RSS. No browser was closed,
  launched, repaired, pruned, or retried.

Interpretation:

- this canary does not evaluate feed extraction or acceptance. The zero yield
  is neither an authentication finding nor a content rejection;
- the Agent Browser upgrade is the direct compatibility boundary: it retained
  the pre-upgrade authenticated process but lacks the process-tree record now
  required for lifecycle adoption;
- topic-search implementation remains installed and tested, but it is no
  longer selected by the recurring X or LinkedIn targets.

Authority classification:

- `inherited_authority`; the operator authorized direct-feed adoption and one
  bounded canary. Closing or relaunching the authenticated browser is a
  separate runtime effect and was not inferred.

Subagent status and reconciliation:

- `not_spawned`; current orchestration policy prohibits delegation.

Graphiti write status:

- pending; this checkpoint, Runbook Turn 321, installed receipts, SQLite
  records, and retained Agent Browser jobs are the current durable authority.

Remaining acceptance criteria:

- transactionally replace the pre-upgrade retained browser with one launched
  under the current Agent Browser generation while preserving the durable
  profile and rollback evidence;
- prove a named service/task tab request before admitting another provider
  attempt, then run at most one explicitly authorized two-lane feed canary;
- only after posts are observed, evaluate direct-feed extraction coverage and
  deterministic ad/spam exclusion.

Next action:

- obtain operator authority for the authenticated-browser close/relaunch
  boundary. Do not retry X or LinkedIn acquisition against the unrecoverable
  lifecycle record.

Checkpoint P0055-C12 is superseded by P0055-C13 below.

### Checkpoint P0055-C13 | 2026-08-23

Plan version: 13

State transition:

- `home_feed_runtime_adopted_browser_lifecycle_blocked -> home_feed_browser_closed_shared_runtime_launch_state_blocked`.

Progress classification:

- `blocker_reduction`; the pre-upgrade browser and profile lease are now gone,
  and the remaining failure is isolated to the selected shared runtime host's
  stale launch state before Chrome starts.

Authorized runtime effects and evidence:

- the operator authorized a transactional close/relaunch of only the
  `last30days-facebook` browser plus one named non-provider tab proof; no X or
  LinkedIn provider attempt was authorized or run;
- fresh runtime census found current Agent Browser generation
  `0.28.0-aa21c5fe8a6d-25828e3b8aed`, one runtime-host PID `32617`, one
  dashboard PID `68960`, and no runtime multiplicity issue;
- the retained logical browser was `session:plan0117-final-runtime`, with
  active daemon browser `session:handoff-f0bb26b7965a9989`, Chrome root PID
  `27742`, profile `last30days-facebook`, and owner-generation 5 receipt
  `owner-transfer-b11d5204a7b6ba821c3d17ff6e1086e2e0b45a55a5f9f95a54db869ee2bc491c`;
- a route-hinted `service_browser_close` succeeded for the active daemon
  browser. Fresh OS readback finds neither PID `27742` nor any process using
  the exact Last30days profile path; the broker reports zero active leases,
  zero same-profile live browsers, and `launch_new_browser`;
- the no-launch capability job
  `mcp-service-browser-capability-preflight-c1cf9ffd-221e-47f9-a5a4-a78ad7ddc4f3`
  succeeded for the durable profile and private-display request.

Launch blocker:

- four bounded `tab_new` paths were attempted only after materially different
  routing state: default MCP lane, selected `runtime-host`, scoped named lane,
  and that lane with an explicit route hint. Jobs
  `mcp-service-request-tab_new-7091ab47-1052-4c12-8eef-bd6250d336c2`,
  `mcp-service-request-tab_new-5e427d52-7f1f-4a35-8292-9b622b53803b`,
  `mcp-service-request-tab_new-4bbbf22f-965d-462c-8cb6-b0e8583cf299`, and
  `mcp-service-request-tab_new-a90fca53-56b8-4fce-8402-4e7a249e3f3d`
  all failed in approximately one tenth of a second against the same dead CDP
  endpoint `127.0.0.1:37725` before creating a browser, display allocation, or
  named tab handle;
- the selected host is current and live, but its environment is bound to
  runtime profile `default`. That profile's `runtime-state.json` contains a
  null `browserPid`, while the current parser requires a `u32`; runtime status
  and service observation therefore report `runtime_profile_unavailable`;
- the default profile points at an unrelated AuraCall user-data directory.
  This plan did not rewrite, delete, or relaunch that shared identity;
- the scoped `last30days-home-feed` supervisor lane proved the existing host
  could publish its port, but systemd correctly rejected a duplicate host
  start because PID `32617` already owned the lane. The lane was removed, port
  `37366` was released, the unit failure flag was reset without starting or
  stopping a process, and the pre-existing runtime-host listener on `37365`
  remains. No temporary Last30days browser or profile process remains.

Interpretation:

- the original lifecycle-adoption blocker is resolved by the successful close;
- launch and named-tab acceptance remain unproven. The failure occurs before
  site navigation, so it is not X authentication, feed retrieval, scraping,
  acceptance filtering, or content quality evidence;
- repairing the shared host/default runtime state can affect other Agent
  Browser consumers and exceeds the approved single-profile restart boundary.

Authority classification:

- `human_gate`; every effect remained inside the approved
  Last30days browser/lane scope, and the shared-host repair boundary was not
  inferred.

Subagent status and reconciliation:

- `not_spawned`; current orchestration policy prohibits delegation.

Graphiti write status:

- pending; this checkpoint, Runbook Turn 322, retained Agent Browser jobs,
  owner registry, process census, and supervisor receipts are authoritative.

Remaining acceptance criteria:

- transactionally repair or replace the selected shared runtime host so a
  service request does not inherit the invalid unrelated `default` runtime
  state or dead CDP port;
- relaunch `last30days-facebook` on a private display and prove one named tab
  request;
- request fresh authority before any X or LinkedIn provider canary.

Next action:

- obtain operator authority for the shared Agent Browser runtime-host repair.
  Do not edit the unrelated default/AuraCall profile manually, and do not run
  another provider or tab attempt until the host state changes.

Checkpoint P0055-C13 is the current authority.

Checkpoint P0055-C13 is superseded by P0055-C14 below.

### Checkpoint P0055-C14 | 2026-08-23

Plan version: 14

State transition:

- `home_feed_browser_closed_shared_runtime_launch_state_blocked -> shared_runtime_route_repaired_upgrade_operator_journey_blocked`.

Progress classification:

- `blocker_reduction`; shared-host routing and named-lane readiness are now
  proven, while browser creation is isolated to an old-generation X display
  allocator collision and the candidate upgrade's independent presentation
  gate.

Authorized runtime effects and evidence:

- the operator authorized shared Agent Browser runtime repair plus one named
  non-provider tab proof. No X, LinkedIn, Reddit, or Facebook navigation or
  provider acquisition was run;
- failed transaction
  `upgrade-53125e3b-5a0f-42c4-b41f-74bd1346cc29` was recovered to
  `failed_preserved_old_generation`, admission draining cleared, and a reviewed
  workstation reconcile removed only the unselected failed candidate
  generation;
- the selected host was rebound through runtime-only systemd drop-in
  `/run/user/1000/systemd/user/agent-browser-runtime-host.service.d/10-selected-ingress.conf`
  to its persisted socket directory. Host PID `61217` is active on the exact
  hashed runtime-host socket; named lane `last30days-home-feed` is ready and
  stream-reachable on port `37366`;
- access-plan selects durable profile `last30days-facebook`, reports zero
  active leases or compatible live browsers, and recommends
  `launch_new_browser`. Browser capability preflight succeeded with the
  promoted WSL stealth Chromium executable.

Named-tab result:

- the sole non-provider `service_request` job
  `mcp-service-request-tab_new-9ab16f7d-e464-48eb-b9af-0c304dfcf974`
  reached remote-headed private-display launch, then exhausted its three
  internal launch attempts because Xvfb exited after each attempt selected
  display `:90`;
- live Xvfb PID `30094` owns abstract socket `@/tmp/.X11-unix/X90` without a
  filesystem socket. Service resources classifies it as `protected` due
  retained display allocation
  `display:private_virtual_display:session-last30days-facebook`, so it was not
  killed or reclaimed;
- the current Agent Browser source allocator checks both the X lock PID and
  live X process and would skip the collision. The selected older generation
  remains installed and does not demonstrate that behavior.

Upgrade result:

- the old installer rejected the unrelated `default/runtime-state.json` null
  PID before mutation. A current candidate parser read the record safely, and
  the active AuraCall browser using its referenced profile path was preserved;
- one stale internal acceptance session was closed through Agent Browser's
  exact lifecycle command. Its browser process remains preserve-only under the
  named persistent acceptance profile and was not signaled manually;
- subsequent candidate upgrades reached the shadow-dashboard stage, but
  transaction `upgrade-698bb291-9084-4756-8faf-0d6fd8f118ba` and independently
  owned concurrent transaction
  `upgrade-339e80a8-975a-4c2d-94c5-44f339d3afa0` both terminalized
  `failed_preserved_old_generation` with stop reason
  `candidate_dashboard_presentation_unproven` after no authenticated candidate
  journey receipt was committed within five minutes;
- stable ingress and operator journey remained ready on generation
  `0.28.0-aa21c5fe8a6d-25828e3b8aed`; candidate backends were rolled back and
  no provider state changed.

Interpretation:

- Agent Browser is not globally unhealthy: dashboard ingress, the selected
  runtime host, exact socket route, named lane, access-plan, and capability
  preflight are operational;
- browser acquisition remains unaccepted because the installed generation's
  private-display allocator collides with protected `:90`. Upgrading to the
  repaired allocator requires an independently authenticated operator journey
  against the shadow dashboard during the transaction window;
- this is pre-navigation runtime evidence, not X or LinkedIn authentication,
  feed retrieval, scrape, acceptance-filter, or quality evidence.

Authority classification:

- `human_gate`; the runtime repair authority was consumed, but the mandatory
  authenticated shadow-dashboard acceptance receipt cannot be fabricated or
  inferred.

Subagent status and reconciliation:

- `not_spawned`; current orchestration policy prohibits delegation.

Graphiti write status:

- pending; this checkpoint, Runbook Turn 323, transaction receipts, current
  process census, and supervisor status are authoritative.

Remaining acceptance criteria:

- rerun the current transactional upgrade while an operator authenticates the
  candidate dashboard and commits its exact presentation receipt inside the
  five-minute window;
- after the candidate is selected, rerun one named non-provider tab proof and
  confirm it allocates a display other than protected `:90`;
- request fresh authority before any X or LinkedIn provider canary.

Next action:

- schedule one attended Agent Browser upgrade acceptance window. Do not kill
  protected Xvfb PID `30094`, edit the unrelated default/AuraCall profile, or
  run a provider request before the candidate generation is accepted.

Checkpoint P0055-C14 is the current authority.

Checkpoint P0055-C14 is superseded by P0055-C15 below.

### Checkpoint P0055-C15 | 2026-08-23

Plan version: 15

State transition:

- `shared_runtime_route_repaired_upgrade_operator_journey_blocked -> current_generation_accepted_stale_profile_lifecycle_owner_blocked`.

Progress classification:

- `blocker_reduction`; the workstation upgrade is accepted and current, and
  the remaining pre-navigation failure is isolated to the Last30days
  profile's stale lifecycle-owner record.

Authorized runtime effects and evidence:

- the operator directed a retry only after Agent Browser was actually ready
  and explicitly required preservation of the existing authenticated profile;
- transaction `upgrade-0df91191-ad9b-4eb9-aa85-2f92e9729563` is terminal
  `accepted` on generation `0.28.0-4b975a51aa89-d0782705d5ff`. All readiness
  axes are true and runtime multiplicity is steady at one dashboard, one
  runtime host, zero legacy daemons, and one executable generation;
- access-plan selected existing durable profile `last30days-facebook`, with
  authenticated target evidence for X and LinkedIn, zero active leases, zero
  compatible live same-profile browsers, and `launch_new_browser`. No profile
  was created, replaced, reseeded, or discarded;
- preflight for schedule
  `plan-0055-x-linkedin-home-feed-retry-20260823` was `ready` for exactly two
  attempts, ten items per lane, no fallback, zero model tokens, and zero cost;
- manual tick `tick-070bfe28cc98550d12f0d940ccdfac2e` terminalized
  `complete_degraded`. X attempt
  `provider-attempt-6ba4a89057e065f33575ea8b6d1c3804` and LinkedIn attempt
  `provider-attempt-855c0d0ca3c88a8eb77499642c4d02c0` each failed
  transiently with safe code `agent_browser_error` and zero attempted,
  observed, accepted, or rejected posts;
- Agent Browser jobs `r974493` and `r232569` both failed
  `remote_view_open` with exact blocker
  `runtime_lifecycle_existing_owner_requires_explicit_transition`; their
  route/display leases rolled back cleanly;
- the profile identity's owner registry still names
  `session:plan0117-final-runtime`, owner generation 5, while the matching
  lifecycle record remains `closing` with cleanup obligation `owned` and
  process group PID `27742`. Fresh process readback finds PID `27742` absent.

Interpretation:

- the upgrade itself is no longer the blocker and the installed Last30days
  service is using the selected current Agent Browser executable;
- the failure precedes provider navigation. It does not test login state,
  direct-feed retrieval, scraper extraction, deterministic ad/spam exclusion,
  or acceptance quality;
- access-plan availability and the lifecycle registry disagree: the broker
  sees no live browser or lease, while lifecycle launch admission still sees a
  non-terminal owner. That record requires an explicit reviewed lifecycle
  transition; silently deleting it or launching under a different profile is
  outside this retry.

Authority classification:

- `human_gate`; the authorized retry is consumed. No second tick, profile
  replacement, or lifecycle-registry mutation is inferred.

Subagent status and reconciliation:

- `not_spawned`; current orchestration policy prohibits delegation.

Graphiti write status:

- pending; this checkpoint, Runbook Turn 324, the durable tick, Agent Browser
  jobs, and current owner/lifecycle registries are authoritative.

Remaining acceptance criteria:

- complete the supported explicit transition that terminalizes the absent
  generation-5 Last30days owner and satisfies its cleanup obligation without
  replacing the authenticated profile;
- after current access-plan and owner-registry agreement, request fresh
  authority for at most one X/LinkedIn feed tick and inspect observed,
  accepted, and deterministic rejection counts.

Next action:

- use Agent Browser's reviewed lifecycle transition or exact-owner cleanup
  path for `session:plan0117-final-runtime`; do not edit the registry file by
  hand, discard `last30days-facebook`, or retry provider acquisition first.

Checkpoint P0055-C15 is the current authority.

Checkpoint P0055-C15 is superseded by P0055-C16 below.

### Checkpoint P0055-C16 | 2026-08-23

Plan version: 16

State transition:

- `current_generation_accepted_stale_profile_lifecycle_owner_blocked -> stale_lifecycle_reconciled_terminal_replacement_source_repaired_install_gate`.

Progress classification:

- `blocker_reduction`; exact lifecycle convergence is proven live, and the
  newly exposed logical-ID replacement defect is repaired and validated in
  Agent Browser source. Installed and provider acceptance remain open.

Authorized runtime effects and evidence:

- Agent Browser candidate reconciliation moved the exact generation-5
  `session:plan0117-final-runtime` lifecycle from `closing/owned` to
  `terminal/satisfied` with evidence
  `service_reconcile_process_group_absent:27742` and
  `service_reconcile_profile_lock_absent`. Owner identity and durable profile
  `last30days-facebook` were preserved;
- access planning then returned `launch_new_browser` with no owner conflict or
  manual action;
- the operator authorized exactly one new X plus LinkedIn tick. Preflight for
  `plan-0055-x-linkedin-home-feed-post-lifecycle-reconcile-20260823` was ready
  for tick `tick-7224876f30d729e41ff5435b387be4df`, one attempt and ten items per
  lane, no fallback, zero model tokens, and zero cost;
- the tick terminalized `complete_degraded`. X attempt
  `provider-attempt-4f283f8d3ba840785db7b3c56739d4b9` and LinkedIn attempt
  `provider-attempt-3e94e5755a39268fd3ffca355acb4d61` each report zero
  attempted, observed, accepted, or rejected posts;
- Agent Browser jobs `r923698` and `r841495` both failed
  `remote_view_open` with
  `runtime_lifecycle_terminal_replacement_rejected`. The prior terminal owner
  is `session:plan0117-final-runtime`; the replacement service lane is
  `session:last30days-home-feed`;
- X browser PID `50724` and LinkedIn browser PID `53490` each exited through
  polite close. Both profile locks were released and both route/display lease
  allocations rolled back;
- Agent Browser branch `fix/reconcile-absent-closing-lifecycle` is published at
  commit `cd23311e`. Its terminal replacement moves a satisfied lifecycle to a
  collision-free new logical ID at exactly the next generation, rejects
  pending transfers and duplicate profile lifecycle records, retains one
  cleanup obligation, and recomputes the launch identity. All 12 lifecycle
  tests, all 50 Service Health tests, strict Clippy, formatting, documentation,
  and diff checks pass.

Interpretation:

- the installed Agent Browser upgrade is healthy and the stale closing record
  is no longer the blocker;
- the new failure still precedes provider navigation and post extraction. It
  provides no evidence about X or LinkedIn login state, feed retrieval,
  scraper extraction, deterministic ad/spam exclusion, or acceptance quality;
- the source repair is not installed. Installing it is a new governed Agent
  Browser transaction, not an implicit continuation of the already accepted
  upgrade.

Authority classification:

- `human_gate`; the authorized tick is consumed. No second provider tick or
  new transactional Agent Browser installation is inferred.

Subagent status and reconciliation:

- `not_spawned`; current orchestration policy prohibits delegation.

Graphiti write status:

- pending; provider readiness passed and job
  `0360a5ed-fa86-4f5e-a9d8-aa8e02586ed8` was queued in
  `last30days_skill_main`, but it remained in node resolution past its nominal
  180-second budget and grouped readback was still operation-locked. Do not
  duplicate the episode; poll this exact job at the next non-trivial closeout.
  This checkpoint, Runbook Turn 325, the durable tick/attempt rows, Agent
  Browser jobs, and published repair branch remain authoritative.

Remaining acceptance criteria:

- transactionally install and accept the published Agent Browser correction;
- prove one named non-provider tab can advance the preserved profile to the
  new service logical browser ID and close cleanly;
- after that gate, request fresh authority for at most one X/LinkedIn feed tick
  and inspect observed, accepted, duplicate, permalink, and deterministic
  promoted/sponsored counts.

Next action:

- obtain explicit authority for one governed Agent Browser installation of the
  validated `cd23311e` repair. Do not rerun provider acquisition first or alter
  `last30days-facebook`.

Checkpoint P0055-C16 is the current authority.

Checkpoint P0055-C16 is superseded by P0055-C17 below.

### Checkpoint P0055-C17 | 2026-08-23

Plan version: 17

State transition:

- `stale_lifecycle_reconciled_terminal_replacement_source_repaired_install_gate -> direct_feed_retrieval_proven_accepted_yield_blocked`.

Progress classification:

- `outcome_progress`; both authenticated feeds are now reached and card
  observation is proven, replacing the prior pre-navigation blocker with exact
  X unique-yield and LinkedIn metadata-recovery defects.

Authority and bounds:

- the operator explicitly directed one successful 20-item feed scrape from X
  and LinkedIn with a retry budget of three per service;
- orchestration interpreted that as at most three total separately receipted
  provider attempts per service, stopped each service immediately on 20
  accepted items, and admitted no fallback, model tokens, or cost;
- each manual tick selected only one already-enabled authenticated home-feed
  target through exact profile `last30days-facebook` and used a temporary
  20-item, one-attempt configuration. The recurring configuration was not
  edited;
- the interval was `2026-08-23T01:46:47Z` through
  `2026-08-24T01:46:47Z`.

X evidence:

- attempt 1, tick `tick-63a759d636523f00289cae6f4f9072b0`, failed
  transiently before observation with `agent_browser_error` and counts
  `0/0/0/0` attempted/observed/accepted/rejected;
- attempt 2, tick `tick-5d9db7821c19ef162e451c10e10f4d49`, observed 32
  cards, accepted 11, and rejected 21: 18 repeated status captures and three
  out-of-range posts;
- attempt 3, tick `tick-3241236cb5e57f70da4213f6a117d08b`, observed 32
  cards, accepted 11, and rejected 21: 20 repeated status captures and one
  out-of-range post;
- neither successful acquisition attempt reported a page signal, auth code,
  or provider incident. X did not reach 20 accepted unique posts.

LinkedIn evidence:

- attempt 1, tick `tick-25cd8e4845ff61a7de52451906c6c1ef`, observed 30
  cards and accepted zero;
- attempt 2, tick `tick-3fe1ad0761900acc65ba917f0578d29c`, observed 30
  cards and accepted one;
- attempt 3, tick `tick-75ed12d871b50ceae1ab3afffeed6a52`, observed 30
  cards and accepted zero;
- every run deterministically identified five sponsored/ad cards. Overlapping
  rejection diagnostics consistently reported 20 missing dates, ten missing
  authors, nine missing permalinks, and nine unknown kinds, plus date-window
  and duplicate exclusions. No page signal or auth code was present;
- LinkedIn did not reach 20 accepted posts. The non-ad deficit is a scraper and
  normalization limitation until exact card-level evidence proves otherwise.

Installed state and cleanup:

- all six ticks are terminal `complete_degraded` with durable provider-attempt
  rows in `/home/ecochran76/.local/share/last30days/research.db`;
- `daily-default` is `ready`, has no runtime error or active tick, and retains
  its existing enabled recurring schedule;
- the temporary configuration was removed. The installed
  `tick-config-v1.json` retains revision
  `operator-20260822-x-linkedin-home-feed-v1` and SHA-256
  `28212c6a182fc191c2cb09bc0c645b4b9386f497b2f6b00b2025c24e78abf604`.

Interpretation:

- this packet does not satisfy the requested 20-item outcome for either
  service;
- X retrieval is functional but is not scrolling deeply enough past repeated
  cards to produce 20 unique in-range posts;
- LinkedIn feed observation is functional, and deterministic ad detection is
  working, but permalink/date/author extraction fails on most non-ad cards;
- these are Last30days scraper defects. They do not justify an Agent Browser
  upgrade, alternate profile, authentication warning, semantic topic filter,
  or reclassification of unknown cards as spam.

Authority classification:

- `inherited_authority`; the operator explicitly authorized the two services,
  20-item target, and three-attempt bound. That bound is now exhausted.

Subagent status and reconciliation:

- `not_spawned`; current orchestration policy prohibits delegation.

Graphiti write status:

- prior C16 job `0360a5ed-fa86-4f5e-a9d8-aa8e02586ed8` is now completed as
  episode `4b72ebf7-7600-4d29-92ac-3dcc091f9170`;
- C17 compact episode job `eceb0d15-4d25-4d73-9799-d86450a1e6a7` is queued
  in `last30days_skill_main` from source checkpoint `51c7ef4`. Poll that exact
  job at the next non-trivial closeout; do not enqueue a duplicate.

Remaining acceptance criteria:

- make X continue bounded unique-card retrieval beyond repeated status cards
  until 20 unique accepted posts or the explicit scroll ceiling;
- recover canonical LinkedIn post permalinks plus date and author metadata
  from the observed home-feed card variants, retaining only deterministic
  sponsored/ad, navigation-noise, exact-duplicate, date, and true structural
  exclusions;
- validate with provider-free fixtures before requesting any new live retry
  budget.

Next action:

- implement one Last30days-only source packet for X unique-scroll completion
  and LinkedIn card metadata recovery. Do not modify Agent Browser, profiles,
  authentication state, recurring schedule, or run another live attempt.

Checkpoint P0055-C17 is the current authority.
