# Plan 0056 | X/LinkedIn Target And Authentication Reliability Repair

State: OPEN
Roadmap: P08
Plan version: 6
Date: 2026-08-25

## Objective

Make the governed X and LinkedIn home-feed lanes evaluate the browser target
that Agent Browser actually attributed to Last30days, distinguish unusable or
ambiguous rendered state from explicit logout, and reach bounded post
observation before making any authentication or content-quality claim.

## Current State

- Plan 0055/C30 and installed service 0.3.69 prove attributed tab creation,
  readiness, bounded evaluation, handle-bound navigation, and X exact release;
- current direct browser readback corroborates the operator's observation that
  the selected `last30days-facebook` browser retains X Home and LinkedIn Feed
  pages, while the terminal tick evaluated newly attributed targets instead;
- the access plan reported `wait_for_profile_lease` for direct profile reuse,
  while its separate `serviceRequest` record was available and unblocked;
  Last30days ignored that broker-provided queued path and instead synthesized
  a route from service status;
- X attempt `provider-attempt-367d5249a31c2eb3de2ce2bf5cbbc75c`
  stopped `auth_state_ambiguous` at `0 attempted / 0 observed / 0 accepted /
  0 rejected`; it did not prove logout;
- LinkedIn attempt
  `provider-attempt-65486b33ad262436e7ed0bda3f85efe6` stopped
  `auth_required` on blank rendered evidence at `0/0/0/0`; its retained target
  later became `browser_missing`, and its handle carried contradictory logical
  and physical browser IDs plus X scraper attribution;
- LinkedIn currently converts absence of its authenticated DOM marker directly
  into `auth_required`, while X already distinguishes ambiguous DOM from an
  explicit login form;
- `auth_state_ambiguous` does not map to a reauthentication incident, but the
  existing notification surface must retain that distinction end to end;
- recurring revision `operator-20260822-x-linkedin-home-feed-v1`, digest
  `28212c6a182fc191c2cb09bc0c645b4b9386f497b2f6b00b2025c24e78abf604`,
  remains unchanged with ten-item X and LinkedIn ceilings. Reddit and Facebook
  remain disabled;
- the operator has now authorized a bounded testing, diagnosis, and repair
  cycle of at most five cycles; each live cycle is one schedule-disabled
  combined tick with one 20-item X attempt and one 20-item LinkedIn attempt;
- all five cycles are consumed. Installed 0.3.72 proves successful broker tab
  creation, handle-bound inventory, and exact release for both lanes, but both
  attempts stop inside Last30days' immediate post-create identity check before
  readiness;
- the X target appears coherently after the immediate check, proving that a
  newly returned handle can precede its target's visible inventory record;
- the LinkedIn target appears on the correct feed URL but carries the retained
  session's X `traceFilter`, while the successful broker request itself names
  the LinkedIn agent, task, and target service. Inventory `traceFilter` is
  therefore not established as per-tab attribution authority.

## Scope

- make the access-plan decision authoritative for whether Last30days may
  acquire or reuse a service-attributed browser target;
- submit an available, unblocked broker-provided `serviceRequest` even when
  direct `profileReuse` recommends waiting; preserve its route hints or fill
  missing browser/session hints only from unique broker-provided
  `profileReuse` evidence, never service status;
- validate a returned `serviceTabHandle` against the exact synchronous broker
  request, selected profile, owner session, target ID, URL hostname, and
  validity before readiness or authentication probes;
- treat the broker-issued handle as the logical browser authority and permit
  tab inventory to expose a distinct physical browser ID or inherited session
  trace. Require exact target, session, and hostname coherence instead of
  inferring equality or per-tab attribution from inventory metadata;
- bounded-poll the exact handle-bound tab inventory after `tab_new` while the
  target is absent or still blank, without issuing another tab request,
  navigating, switching tabs, or broadening the browser/profile scope;
- require meaningful rendered-page evidence after readiness: a target must be
  live, on the requested hostname, non-blank, and carry bounded URL/title/DOM
  signals before authentication classification;
- classify explicit login URL/form as `auth_required`, explicit checkpoint or
  restriction separately, and blank/ambiguous/mismatched evidence as a
  transient retrieval failure that cannot create a reauthentication incident;
- allow at most one same-handle, same-target navigation and meaningful-page
  reprobe before an ambiguous authentication result terminalizes;
- release only the exact coherent attributed handle. On identity mismatch,
  preserve the browser and target, record bounded evidence, and fail closed;
- preserve feed pagination, canonical permalink recovery, structural post
  validation, deterministic ad/spam exclusion, and topic-search capability;
- retain enough safe diagnostics to distinguish route selection, target
  attribution, page readiness, authentication classification, extraction, and
  bounded-yield failures in the durable provider receipt.

## Non-Goals

- no Agent Browser implementation, upgrade, lifecycle transition, profile
  replacement, authentication, direct CDP control, or tab cleanup;
- no reuse of an operator-owned tab unless Agent Browser explicitly returns a
  valid service attribution for that exact target;
- no heuristic inference that a Home or Feed title alone proves authentication;
- no GraphRAG, semantic relevance scoring, subjective quality filtering, or
  expansion beyond deterministic ads/spam and structural invalidity;
- no Reddit or Facebook enablement, recurring cadence change, or increase of
  the recurring ten-item X/LinkedIn ceilings;
- no notification delivery or incident closure outside the normal tick
  contract, and no provider attempts beyond the five-cycle repair budget;
- no unbounded scrolling or guarantee based only on a requested item ceiling.

## Required Invariants

1. **Broker authority:** an available and unblocked broker `serviceRequest` is
   the authoritative service-tab route. Missing browser/session hints may be
   filled only from unique `profileReuse` browser and lease-session evidence in
   the same access plan. Only when it is unavailable or blocked does a direct
   `profileReuse` wait terminalize acquisition.
2. **Target identity:** every readiness, navigation, evaluation, scroll, and
   release operation must name the same validated service-tab handle. The
   request-local broker response is attribution authority; retained-session
   inventory trace is diagnostic only unless Agent Browser establishes a
   stronger per-tab contract.
3. **Profile preservation:** the configured `last30days-facebook` profile and
   its existing browser remain untouched on every failure path.
4. **Evidence-bound auth:** only explicit signed-out evidence may produce
   `auth_required`; absence of an authenticated selector is insufficient.
5. **No false incident:** ambiguous, blank, stale, or mismatched target state
   cannot create or refresh a reauthentication incident or notice.
6. **Retrieval first:** no post-quality or infinite-scroll conclusion is
   allowed until the provider receipt records observed candidates.
7. **Exact release:** a caller may release only its coherent attributed target;
   identity disagreement is preserved as evidence rather than repaired by
   guessing or closing broader browser state.

## Execution Graph

| Packet | Depends on | Outcome | Write surface | Terminal condition |
|---|---|---|---|---|
| P1 | C30 evidence | Red fixtures reproduce broker-wait bypass, cross-attributed handle, blank LinkedIn auth, and ambiguous X auth | focused fixtures/tests only | all named defects fail before implementation |
| P2 | P1 | Broker and handle-coherence gates fail closed without touching browser state | `agent_browser_config.py`, shared browser client, focused tests | route and target matrices pass |
| P4 | P3 | Durable receipt and notification semantics preserve the exact failure boundary | worker/tick adapter and incident tests as required | no ambiguous case becomes reauthentication |
| P5 | P4 | Focused, package, complete-suite, reproducible-build, and installed-runtime acceptance | version/release surfaces if code changes ship | exact successor is ready with rollback retained |
| P6 | P5 plus current bounded authority | Up to three schedule-disabled combined 20/20 acceptance ticks within the five-cycle total budget | temporary private config and durable runtime receipts only | both lanes prove 20/20 or the fifth cycle terminalizes |
| P7 | P6 terminal evidence plus fresh implementation authority | Red/green post-create settling and request-attribution contract | shared browser client plus focused fixtures only | delayed X inventory and inherited-trace LinkedIn cases pass while true target/session/hostname mismatches fail closed |
| P8 | P7 plus fresh install/live authority | Validated successor and one schedule-disabled combined 20/20 acceptance tick | release surfaces and temporary private tick config only | both lanes prove 20/20 or the one authorized receipt terminalizes |

Packets P2 through P4 are tightly coupled on the critical path and should be
implemented serially. Provider-free fixture authoring and notification-contract
tests may be prepared independently only when they do not overlap those files.
No subagent delegation is authorized by the current orchestration policy.

## Repair Design

### 1. Broker-decision gate

- Prefer an available, unblocked broker `serviceRequest` for `tab_new`. Preserve
  broker request hints; when absent, add them only from a unique reusable or
  same-profile live browser plus unique active lease session in the same
  `profileReuse` decision. This queued service route remains authoritative even
  when direct profile reuse reports `wait_for_profile_lease`.
- Treat `wait_for_profile_lease` as terminal only when the broker service
  request is unavailable, blocked, malformed, or absent.
- Remove the current ability for a status-only same-profile CDP row to override
  an incompatible access-plan decision for X or LinkedIn acquisition.
- Preserve the existing narrow runtime/profile resolution paths only when they
  produce a route equivalent to the broker's selected profile and lifecycle
  owner and are covered by an explicit compatibility contract.

### 2. Attributed-target coherence gate

- Validate the tab-new response before storing `_service_tab_handle`.
- Bind expected source hostname, selected profile, logical browser ID, owner
  session, target ID, agent name, task name, and target service into an
  immutable request-local acquisition record. Construct it only from the
  request submitted by this client and the handle returned by that same
  synchronous broker response.
- Do not compare the handle's logical browser ID to tab inventory's physical
  browser ID. The broker-issued handle plus exact live target ID, owner session,
  and hostname form the inventory coherence proof.
- Treat inventory `traceFilter` as diagnostic retained-session metadata. A
  mismatched trace cannot negate a coherent request-local broker handle, and a
  matching trace cannot rescue the wrong target, session, or hostname.
- Require handle validity and live target presence before each first control
  and immediately before release; preserve bounded expected/observed fields in
  diagnostics without cookies, page text, tokens, or private content.

### 2a. Post-create inventory settling

- Replace the one-shot inventory read with an injected-clock, deterministic
  bounded poll on the exact returned session and target. Use at most six
  inventory reads and at most five wall-clock seconds, whichever is reached
  first; tests replace sleeping with a recorder.
- Retry only when the exact target is absent or its URL is empty/about:blank.
  A present non-empty foreign hostname or a present non-empty conflicting
  owner session fails immediately.
- Success requires the exact target ID, no conflicting owner session, and the
  requested hostname. The next operation is then the existing handle-bound
  readiness call; polling itself never navigates or creates another tab.
- Exhaustion raises the existing typed acquisition failure with safe counts
  and the last observed identity state. The caller retains exact-handle release
  behavior and cannot close the shared browser or any unrelated tab.

### 3. Meaningful-page readiness

- Keep document readiness as a transport prerequisite, not an authentication
  signal.
- Add a bounded same-handle page probe requiring the requested hostname, a
  non-blank URL/title or source root, and source-specific rendered evidence.
- Permit one same-handle navigation to the feed URL and one bounded reprobe.
- Return transient `page_state_ambiguous` or a compatible safe code when the
  page remains blank, stale, detached, or attribution-incoherent.

### 4. Authentication truth table

| Evidence | X result | LinkedIn result | Incident |
|---|---|---|---|
| signed-in source DOM | authenticated | authenticated | none |
| explicit login URL/form | `auth_required` | `auth_required` | reauthentication |
| checkpoint/challenge | checkpoint-specific | checkpoint-specific | evidence-matched challenge/reauth |
| restriction/rate limit | restriction-specific | restriction-specific | evidence-matched rate-limit |
| blank/loading/no source DOM | transient ambiguous | transient ambiguous | none |
| stale or mismatched handle | target-attribution failure | target-attribution failure | provider degraded at most, never reauth |

LinkedIn must no longer convert `not authenticated_dom` into
`auth_required` without explicit login evidence. X must preserve its existing
ambiguous result and gain the same meaningful-page prerequisite.

### 5. Receipt and notification integrity

- Preserve safe route decision, target-coherence, meaningful-page, and auth
  state as distinct failure stages/signatures.
- Keep `auth_state_ambiguous`, blank-page, and handle-mismatch codes outside the
  reauthentication incident mapping.
- Verify that an existing reauthentication reminder cannot cite a new
  ambiguous attempt as fresh logout evidence.

## Acceptance Criteria

1. A red fixture matching C30 proves the current code ignores an available
   broker service request and synthesizes status-derived routing; the repair
   submits the broker request without browser/session hints. A separate fixture
   proves wait stops before `tab_new` when no compatible service route exists.
2. Correct broker reuse plus a coherent service-tab handle reaches readiness,
   navigation, authentication, extraction, scrolling, and exact release on one
   target ID; every control carries that same handle.
3. Missing target after the settling bound, `browser_missing`, non-empty wrong
   hostname, conflicting owner session, blank target after the settling bound,
   and stale handle each fail before auth classification and never close a tab
   or browser. A logical-handle/physical-inventory browser-ID difference or
   inherited inventory trace alone is accepted when target, session, hostname,
   and request-local broker ownership agree.
4. X and LinkedIn truth-table fixtures distinguish authenticated, explicit
   login, checkpoint, restriction, blank/loading, and ambiguous states.
5. No blank, ambiguous, or target-mismatch fixture creates or refreshes a
   reauthentication incident or notification; explicit login still does.
6. Existing topic search, feed extraction, canonical permalink, deterministic
   ads/spam, structural validation, accepted-unique scrolling, and exact
   release regressions remain green.
7. Focused tests pass in the fast-feedback tier; the complete canonical suite,
   package boundary, reproducible build, release-version checks, and planning
   audit pass before installation.
8. The exact successor installs ready with contract/runtime/artifact digests
   recorded and at least one verified rollback generation retained.
9. Under separately granted fresh authority, one combined tick uses only X and
   LinkedIn home feeds, one attempt and 20-item ceiling per lane, zero model and
   cost budget, and no recurring-config mutation.
10. Live completion requires both lanes to reach extraction and return 20
    unique canonical structurally valid posts within the existing bounded
    eight-scroll ceiling, with observed, accepted, rejected, duplicate, scroll,
    unique-observation, and stagnation counts preserved. A bounded shortfall is
    truthful evidence but does not close this plan.
11. A deterministic X fixture returns a valid handle, omits its target from the
    first inventories, then exposes the coherent X target; it reaches
    `handle-ready` once without a second `tab_new`.
12. A deterministic LinkedIn fixture returns a LinkedIn-attributed handle whose
    coherent target carries inherited `x-scraper/x-feed` trace metadata; it
    reaches readiness and exact release, while crossed target/session/hostname
    fixtures still fail closed.

## Validation Plan

- **Red-capable focused loop:** targeted cases in
  `tests/test_agent_browser_config.py`, `tests/test_facebook.py`,
  `tests/test_x_browser.py`, `tests/test_linkedin.py`, and
  `tests/test_service_tick_incidents.py`; demonstrate each named regression
  fails before its fix when practical.
- **Post-create feedback loop:** one focused `tests/test_facebook.py` selection
  first fails on delayed target visibility and inherited-trace LinkedIn
  attribution, then passes with injected sleeping/clock control. The same
  selection retains immediate-failure cases for conflicting session and
  non-empty foreign hostname.
- **Boundary integration:** acquisition-worker and tick-adapter tests prove
  failure stage/signature and incident semantics survive process boundaries.
- **Presubmit:** focused social-browser, worker, tick, release/version, package,
  source-log visibility, and planning-contract validation.
- **Comprehensive:** `uv run pytest` plus the canonical Go/package/build checks
  required by the release surface; record exact selections and exclusions.
- **Installed acceptance:** diagnose/readiness, manifest and artifact digests,
  rollback inventory, recurring-config digest, and SQLite integrity.
- **Live acceptance:** opt-in only after fresh authority; one terminal combined
  tick, followed by read-only provider attempts, operations, incidents,
  notifications, resource leases, schedule, and recurring-config readback.

## Execution Bounds

- implementation work units: four, corresponding to P1 through P4;
- implementation attempts per work unit: two;
- review/rework cycles: one closed-world pass against accepted blocking
  findings and critical regressions;
- ambiguous-page reprobes: one navigation plus one re-evaluation on the same
  coherent handle per provider attempt;
- total repair cycles: at most five; Cycles 1 and 2 are provider-free repair
  and release/install validation, while each remaining live cycle permits at
  most one X attempt and one LinkedIn attempt in one combined tick; this bound
  is exhausted and is not reset by Plan version 6;
- P7 planning is authorized by the operator's repair-planning request. P7
  implementation, a successor install, and P8 live acceptance require a fresh
  bounded authority packet with explicit implementation and provider-effect
  ceilings;
- scroll ceiling: existing maximum eight per lane;
- no-progress bound: two consecutive implementation checkpoints require a
  local split or tactic change before continuation;
- hard stops: broker wait/incompatibility, target-identity mismatch, explicit
  login/checkpoint/restriction, blank state after the single reprobe, test or
  build failure, install mismatch, preflight failure, or first live terminal
  receipt.

## Owned Write Surfaces

- `skills/last30days/scripts/lib/agent_browser_config.py`;
- `skills/last30days/scripts/lib/facebook.py` shared browser-client boundary;
- `skills/last30days/scripts/lib/x_browser.py`;
- `skills/last30days/scripts/lib/linkedin.py`;
- worker/tick/incident adapters only if required to preserve safe evidence;
- focused tests and fixtures for the named contracts;
- service version, changelog, runtime manifest, package/release tests if an
  installable successor is produced;
- this plan, `ROADMAP.md`, and append-only `RUNBOOK.md`.

## Dependencies And Gates

- installed Agent Browser access-plan and service-request schemas are external
  contracts; Last30days consumes them but does not repair that runtime;
- profile `last30days-facebook` and recurring configuration are preserved;
- the five-cycle implementation/install/live direction is exhausted. Plan
  version 6 does not renew it; P7/P8 effects require fresh bounded authority;
- no direct browser or profile mutation is an escape hatch for a failed
  Last30days contract.

## Definition Of Done

- provider-free evidence proves authoritative broker routing, coherent target
  ownership, meaningful-page readiness, evidence-bound authentication, exact
  release, and truthful notification behavior;
- the exact installed successor is ready and rollback-safe;
- one separately authorized combined 20/20 tick observes and returns 20 unique
  canonical structurally valid posts from both X and LinkedIn within bounded
  scrolling, with no false authentication incident or recurring-config change;
- Plan 0056 closes only when all three boundaries—fixture, installed runtime,
  and live 20/20 outcome—have current receipts.

### Checkpoint P0056-C01 | 2026-08-25

Plan version: 1

State transition:

- `control_contract_repaired_auth_probe_and_route_attribution_blocked ->
  bounded_target_auth_reliability_successor_open`.

Progress classification:

- `blocker_reduction`; C30 evidence is converted into a bounded repair design
  with explicit routing, target, readiness, auth, incident, and live-acceptance
  contracts. No implementation or provider effect occurred.

Authority classification:

- `inherited_authority`; the operator requested repair planning. This packet
  authorizes planning artifacts only and grants no live provider attempt.

Subagent status and reconciliation:

- `not_spawned`; current orchestration policy prohibits delegation.

Evidence:

- current service/browser readback, C30 tick and target receipts, CodeGraph
  source/call-path inspection, and the clean planning-contract audit;
- implementation and live acceptance remain unrun.

Next action:

- execute P1: add the four red-capable provider-free regressions and stop at
  their exact failing assertions before changing production routing or auth
  behavior.

Checkpoint P0056-C01 is the current authority.

### Checkpoint P0056-C02 | 2026-08-25

Plan version: 2

State transition:

- `bounded_target_auth_reliability_successor_open ->
  provider_free_target_auth_contract_green`.

Progress classification:

- `blocker_reduction`; the shared browser boundary now follows the broker's
  available queued service request, validates returned target identity and
  attribution before readiness, and stops when no service route is available.

Authority classification:

- `inherited_authority`; the operator authorized up to five testing,
  diagnosis, and repair cycles to restore both 20-item feed ticks.

Subagent status and reconciliation:

- `not_spawned`; current orchestration policy prohibits delegation.

Evidence:

- red/green regressions cover broker service-request precedence, browser and
  session coherence, agent/task attribution, LinkedIn ambiguous auth, and one
  same-tab LinkedIn reprobe;
- X now normalizes shared-browser acquisition failures through its typed error
  boundary, and the obsolete status-only lease-wait bypass fixture now proves
  fail-closed behavior;
- the focused browser/config/incident selection passes with 203 tests and
  three expected skips.

Next action:

- complete Cycle 2 comprehensive validation, release/version updates,
  reproducible build, transactional install, and installed-runtime preflight.

Checkpoint P0056-C02 is the current authority.

### Checkpoint P0056-C03 | 2026-08-25

Plan version: 3

State transition:

- `provider_free_target_auth_contract_green ->
  installed_logical_physical_identity_rejection_localized`.

Progress classification:

- `blocker_reduction`; installed service 0.3.70 and one combined 20/20 tick
  prove the false-logout repair while localizing both pre-readiness failures to
  Last30days' new tab-inventory coherence probe.

Authority classification:

- `inherited_authority`; Cycles 2 and 3 are consumed within the operator's
  five-cycle testing and repair budget.

Subagent status and reconciliation:

- `not_spawned`; current orchestration policy prohibits delegation.

Evidence:

- pushed commit `992de763c99339e6bca11f3464cb4bd153cd7323` built three
  identical 0.3.70 artifacts at SHA-256
  `f9b190b3c8df4b7a09d933b4531067d505119719a629745b5211e1e717916456`;
- the complete canonical suite passed with 2,693 tests, seven skips, and six
  subtests before installation; 0.3.70 installed ready on schema 16 with
  0.3.68 and 0.3.69 retained;
- tick `tick-1af6ef03e10052f44592a6d9448b3c9f` used one 20-item
  attempt per lane and terminalized `complete_degraded` at `0/0/0/0` for X and
  LinkedIn, with `workspace_acquisition` / `agent_browser_error`, one recorded
  service operation each, zero incidents, and zero notifications;
- the recorded operation is the new handle-bound tab inventory probe. A red
  provider-free case then reproduced rejection when the broker handle's
  logical browser ID differs from the tab record's physical browser ID; the
  repaired case passes while the wrong-agent/task case still fails closed.

Next action:

- release and install service 0.3.71, then consume Cycle 4's single combined
  20/20 tick and inspect its first terminal receipt.

Checkpoint P0056-C03 is the current authority.

### Checkpoint P0056-C04 | 2026-08-25

Plan version: 4

State transition:

- `installed_logical_physical_identity_rejection_localized ->
  broker_reuse_route_hint_omission_repaired`.

Progress classification:

- `blocker_reduction`; Cycle 4 disproved the local identity-gate hypothesis,
  and read-only Agent Browser receipts identified the actual common blocker as
  omitted broker reuse route hints on all four live requests.

Authority classification:

- `inherited_authority`; Cycle 4 is consumed and Cycle 5 remains for the final
  validated successor plus combined 20/20 acceptance tick.

Subagent status and reconciliation:

- `not_spawned`; current orchestration policy prohibits delegation.

Evidence:

- installed service 0.3.71 repeated the exact X and LinkedIn source-specific
  failure signatures at `workspace_acquisition`, `0/0/0/0`, with one service
  operation and no incident/notification;
- Agent Browser service receipts for both Cycle 3 and Cycle 4 show every
  `tab_new` failed its duplicate-profile-lane guard and explicitly requested
  the access-plan browserId/sessionName reuse hints;
- the access plan provides one same-profile live logical browser and one active
  lease session. A red/green regression now requires those exact broker fields
  on the queued request without reading service status or allowing a duplicate
  profile lane;
- the 0.3.71 logical/physical comparison removal was not causal but remains a
  valid distinction; exact target/session/hostname/attribution gates remain.

Next action:

- validate, release, and install service 0.3.72, then consume the final Cycle 5
  combined tick. The five-cycle budget terminalizes at that receipt whether or
  not both lanes reach 20.

Checkpoint P0056-C04 is the current authority.

### Checkpoint P0056-C05 | 2026-08-25

Plan version: 5

State transition:

- `broker_reuse_route_hint_omission_repaired ->
  five_cycle_budget_exhausted_post_create_coherence_blocked`.

Progress classification:

- `blocker_reduction`; the final successor proves browser reuse routing, tab
  creation, inventory, and exact release for both lanes, but the five-cycle
  budget ends before readiness, auth, observation, or 20/20 acceptance.

Authority classification:

- `human_gate`; all five operator-authorized cycles are consumed. No sixth
  provider attempt is authorized by this plan.

Subagent status and reconciliation:

- `not_spawned`; current orchestration policy prohibits delegation.

Evidence:

- pushed commit `f16591471a51d8b87c36b3ba916828381aa678cf` built three
  identical 0.3.72 artifacts at SHA-256
  `9a3c2ad1b327f86f2c97f3604dea1b1243a44a79bcf426911300788413d9588c`;
- installed 0.3.72/schema 16 is ready with runtime-manifest SHA-256
  `89f191bf1c66d0d1c4b7c772ca57b26cc4088c60a1a414e09c7263889f364713`;
- the complete canonical suite passed with 2,693 tests, seven skips, and six
  subtests before installation;
- final tick `tick-4b14711aaec1d762ccae04313bbd23f3`, config digest
  `sha256:9f7221e9c718eeb64b4971e45e334c153da92c73decdf17c16a59ea034829106`,
  terminalized `complete_degraded`; X attempt
  `provider-attempt-267b1db2a0d2fcb8ab3cf26b78bac25e` and LinkedIn
  attempt `provider-attempt-a3e7c946115be90704f9c49255e0b32c` remain
  `workspace_acquisition` / `agent_browser_error` at `0/0/0/0`;
- unlike Cycles 3 and 4, both `tab_new` requests succeeded, both handle-bound
  `tab_list` requests succeeded, and both exact handle releases succeeded. The
  remaining failure is Last30days' immediate post-create coherence check;
- X target `93BF3F2CFE650EAC33B286624CC66AC7` later appears with the
  correct X agent/task and URL, consistent with an immediate inventory/readiness
  race. LinkedIn target `95E0C28F3F413D1308467584A89A1BC7` later appears
  on the right URL but inherits the retained session's `x-scraper/x-feed`
  trace despite the successful LinkedIn-attributed service request;
- the final tick created zero incidents and zero notifications. SQLite quick
  check is `ok`, with zero active execution attempts, provider attempts, or
  unreleased resource leases. Recurring config SHA-256 remains
  `28212c6a182fc191c2cb09bc0c645b4b9386f497b2f6b00b2025c24e78abf604`;
  daily schedule remains enabled and ready for `2026-08-27T00:00:00Z`.

Next action:

- stop. A future fresh authority packet should fixture-drive a bounded
  post-create inventory poll and decide whether per-tab service-request
  attribution, rather than retained-session `traceFilter`, is the correct
  LinkedIn ownership proof before any further live attempt.

Checkpoint P0056-C05 is the current authority. Plan 0056 remains `OPEN`
because the required X and LinkedIn 20/20 outcome was not achieved.

### Checkpoint P0056-C06 | 2026-08-25

Plan version: 6

State transition:

- `five_cycle_budget_exhausted_post_create_coherence_blocked ->
  post_create_settling_and_request_attribution_repair_planned`.

Progress classification:

- `blocker_reduction`; Cycle 5 evidence is converted into a bounded,
  red-capable repair packet that preserves cross-request isolation without
  treating retained-session trace metadata as per-tab ownership proof.

Authority classification:

- `inherited_authority`; the operator requested repair planning only. No code,
  install, provider attempt, browser operation, or recurring configuration
  change is authorized or performed by this checkpoint.

Subagent status and reconciliation:

- `not_spawned`; current orchestration policy prohibits delegation.

Evidence:

- current source performs one immediate handle-bound `tab list`, then rejects
  a missing target or mismatched inventory `traceFilter` before `handle-ready`;
- Cycle 5 later-target evidence proves delayed X inventory coherence and a
  coherent LinkedIn feed target with retained-session X trace despite the
  successful LinkedIn-attributed broker request;
- the planned feedback loop uses at most six exact-session inventory reads and
  five seconds, treats only absent/blank target state as transient, and keeps
  session/hostname conflicts fail-fast;
- branch and origin agree at
  `ab46af78a76513cc9569593b0bba4d24b4013800` before this planning update;
  installed service remains 0.3.72 and no runtime effect is part of this slice.

Next action:

- under fresh bounded implementation authority, execute P7 test-first. Do not
  install or run another combined 20/20 tick until its focused and canonical
  provider-free validation is green and a separate live-effect ceiling is
  explicit.

Checkpoint P0056-C06 is the current planning authority. Plan 0056 remains
`OPEN`; the five-cycle live/repair budget remains exhausted.
