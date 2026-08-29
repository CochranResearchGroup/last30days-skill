# Plan 0056 | X/LinkedIn Target And Authentication Reliability Repair

State: OPEN
Lane: P08
Branch: fix/x-linkedin-failure-cause-evidence
Target: main
Integration: fast-forward
Roadmap: P08
Plan version: 17
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
  therefore not established as per-tab attribution authority;
- the generic Agent Browser lifecycle client, workspace/value objects, typed
  failures, and target-coherence helpers currently live in `facebook.py`.
  X, LinkedIn, Reddit, YouTube, and cleanup code import that Facebook module as
  their shared runtime. The behavior is shared, but the module ownership is
  misleading and creates cross-provider coupling;
- the operator has now authorized the provider-free P7 implementation,
  architecture repair, validation, and merge if successful. This authority
  does not install a successor, invoke Agent Browser, or admit a provider tick.
- P7 is now integrated at `699ef3e637fde797d1eab9b44734ee86cd939ca5`;
  the operator has separately authorized P8: build and install one exact
  successor, then run one schedule-disabled combined home-feed tick with one
  X attempt and one LinkedIn attempt, each capped at 20 accepted items. Stop at
  the first terminal receipt without changing Agent Browser or the recurring
  configuration.
- P8 installed exact service 0.3.73 and consumed its sole combined tick. Both
  lanes terminalized before page observation: X exposed an untyped adapter
  exception that the worker collapsed at `adapter_execution`; LinkedIn exposed
  a typed `agent_browser_error` at `workspace_acquisition`. Neither receipt is
  authentication or content-quality evidence;
- the operator has now authorized the bounded C10 successor: repair those two
  Last30days evidence-loss paths, validate and install one exact successor,
  then run one schedule-disabled combined home-feed tick with one X and one
  LinkedIn attempt, each capped at 20 accepted items. This does not authorize
  Agent Browser implementation/state changes or recurring-config mutation;
- C10 installed service 0.3.74 and consumed its sole combined tick. The new
  durable cause evidence proves both lanes hit an unhandled
  `subprocess.TimeoutExpired` in Last30days' direct broker-request wrapper,
  before browser-operation evidence or post observation. This is a common
  Last30days timeout-translation defect, not logout, feed exhaustion, content
  filtering, or an Agent Browser health finding.
- direct Agent Browser inspection on 2026-08-26 proves the retained
  `handoff-356556ee1fe03a25` command lane is responsive, but the live browser
  is currently attributed to profile `default`, not the intended
  `last30days-facebook` profile. A direct command that omitted the explicit
  runtime profile contributed the current default-profile attachment and is
  not authentication evidence for the intended profile;
- retained service trace proves the C11 X and LinkedIn requests waited on the
  exclusive `last30days-facebook` lease held by that handoff for 30,232 ms and
  30,280 ms respectively. Agent Browser did not classify the handoff browser
  as compatible with the requested profile, so the broker attempted a waiting
  launch rather than attributed tab reuse;
- Last30days' direct broker acquisition calls `_invoke_service_request()`
  outside `_invoke()`'s existing `subprocess.TimeoutExpired` translator. Its
  outer deadline therefore hid the broker's typed lease-conflict result as a
  generic adapter exception.
- current Agent Browser 0.28.0 source and installed behavior prove that
  ordinary `tab list` intentionally omits CDP `targetId` and `sessionId`;
  those diagnostic identifiers require `tab list --verbose`;
- Last30days currently accepts the authoritative synchronous
  `serviceTabHandle`, then calls ordinary `tab list` and requires the omitted
  `targetId` before it will run the handle-scoped readiness probe. The test
  double incorrectly supplied verbose-only fields to the ordinary surface;
- Agent Browser's service-client contract explicitly requires consumers to
  keep the returned `serviceTabHandle` for follow-on work and not rediscover
  raw targets, sessions, or DevTools identity after brokered acquisition;
- the operator has authorized P9: repair that Last30days contract, validate
  and install one exact successor if required by the service boundary, then
  run one schedule-disabled combined home-feed tick with one X attempt and one
  LinkedIn attempt, each capped at 20 accepted items. Agent Browser state and
  recurring configuration remain outside the packet.
- P10 installed service 0.3.76 and terminalized tick
  `tick-d844d848bf526237a683b506af6dad9a`. Both provider attempts succeeded:
  X reached 20 unique canonical status URLs, while LinkedIn reached 14 unique
  canonical activity URLs from 117 observations. LinkedIn rejected 77
  duplicate observations, 22 deterministic sponsored/ad observations, and
  four unknown cards without permalinks; the remaining acceptance gap is
  bounded infinite-scroll depth, not Agent Browser acquisition,
  authentication, admission of metadata-gap posts, canonical deduplication,
  or optional-media failure propagation.

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
  bounded-yield failures in the durable provider receipt;
- extract a deep `agent_browser_runtime` module that owns provider-neutral
  acquisition, readiness, control, evaluation, release, value objects, and
  typed runtime failures. Facebook keeps only Facebook auth/query behavior;
  X, LinkedIn, Reddit, YouTube, and cleanup code depend directly on the new
  provider-neutral interface. Preserve narrow Facebook compatibility exports
  only where needed by existing callers while making the new module canonical.

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
| P3 | P2 | Meaningful-page and evidence-bound authentication gates preserve transient retrieval failures without false logout | X/LinkedIn adapters and focused tests | auth truth-table and same-handle reprobe cases pass |
| P4 | P3 | Durable receipt and notification semantics preserve the exact failure boundary | worker/tick adapter and incident tests as required | no ambiguous case becomes reauthentication |
| P5 | P4 | Focused, package, complete-suite, reproducible-build, and installed-runtime acceptance | version/release surfaces if code changes ship | exact successor is ready with rollback retained |
| P6 | P5 plus current bounded authority | Up to three schedule-disabled combined 20/20 acceptance ticks within the five-cycle total budget | temporary private config and durable runtime receipts only | both lanes prove 20/20 or the fifth cycle terminalizes |
| P7 | P6 terminal evidence plus current implementation authority | Red/green post-create settling, request-attribution contract, and provider-neutral runtime extraction | `agent_browser_runtime.py`, provider adapters/imports, compatibility seam, focused fixtures | delayed X inventory and inherited-trace LinkedIn cases pass; true target/session/hostname mismatches fail closed; no non-Facebook provider imports Facebook as its runtime |
| P8 | P7 plus fresh install/live authority | Validated successor and one schedule-disabled combined 20/20 acceptance tick | release surfaces and temporary private tick config only | both lanes prove 20/20 or the one authorized receipt terminalizes |
| P9 | current Agent Browser handle contract plus P8 terminal evidence | Remove raw post-broker target rediscovery, prove handle-scoped readiness against realistic ordinary-tab inventory, install one exact successor, and run one bounded combined 20/20 tick | `agent_browser_runtime.py`, focused tests, release/install surfaces, temporary private tick config, durable receipts | both lanes prove 20/20 or the single authorized combined receipt terminalizes |
| P10 | P9 terminal receipt plus standing goal authority | Preserve legitimate LinkedIn feed posts across recoverable metadata gaps, deduplicate by canonical activity URL, isolate optional media failure, install one exact successor, and run one changed-input combined 20/20 acceptance tick | `linkedin.py`, acquisition worker, focused tests, release/install surfaces, temporary private tick config, durable receipts | both lanes prove 20 unique accepted posts or the single P10 combined receipt terminalizes |
| P11 | P10 terminal receipt plus standing goal authority | Make LinkedIn home-feed scrolling accepted-yield-aware within the existing finite action and wall-clock bounds, install one exact successor, and spend the final changed-input combined 20/20 attempt | `linkedin.py`, focused tests, release/install surfaces, temporary private tick config, durable receipts | both lanes prove 20 unique accepted posts or the final bounded receipt terminalizes |

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

### 2b. Provider-neutral runtime ownership

- Move provider-neutral lifecycle value objects, the typed runtime failure,
  acquisition/readiness/control/release client behavior, and shared identity/
  route helpers into `lib/agent_browser_runtime.py`.
- Keep the module deep: its public interface represents an attributed browser
  workspace and hides broker/CLI mechanics. Do not split it into one-method
  wrappers or duplicate lifecycle logic in provider modules.
- Make Facebook's CLI client a provider-specific subclass containing only its
  query-capture and Facebook authentication probes. Existing Facebook imports
  may be served by compatibility aliases, but the canonical definitions and
  all other provider imports must resolve to `agent_browser_runtime`.
- Preserve public behavior and error codes at process boundaries. The rename is
  architectural ownership, not a receipt-schema or provider-policy change.

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
- **Post-create feedback loop:** one focused shared-runtime test selection
  first fails on delayed target visibility and inherited-trace LinkedIn
  attribution, then passes with injected sleeping/clock control. The same
  selection retains immediate-failure cases for conflicting session and
  non-empty foreign hostname.
- **Architecture boundary:** provider import tests prove X, LinkedIn, Reddit,
  YouTube, and cleanup code resolve the provider-neutral runtime rather than
  importing Facebook. Existing Facebook compatibility callers remain green.
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
- P7 implementation, architecture repair, provider-free validation, commit,
  push, and integration to `origin/main` are authorized by the operator's
  current request. A successor install and P8 live acceptance still require a
  fresh bounded authority packet with explicit provider-effect ceilings;
- scroll ceiling: existing maximum eight per lane;
- no-progress bound: two consecutive implementation checkpoints require a
  local split or tactic change before continuation;
- hard stops: broker wait/incompatibility, target-identity mismatch, explicit
  login/checkpoint/restriction, blank state after the single reprobe, test or
  build failure, install mismatch, preflight failure, or first live terminal
  receipt.

## Owned Write Surfaces

- `skills/last30days/scripts/lib/agent_browser_config.py`;
- `skills/last30days/scripts/lib/agent_browser_runtime.py` provider-neutral
  browser-client boundary;
- `skills/last30days/scripts/lib/facebook.py` provider-specific adapter and
  compatibility exports;
- `skills/last30days/scripts/lib/x_browser.py`;
- `skills/last30days/scripts/lib/linkedin.py`;
- `skills/last30days/scripts/lib/reddit_browser.py`;
- `skills/last30days/scripts/lib/youtube_yt.py`;
- `skills/last30days/scripts/lib/youtube_media.py`;
- `skills/last30days/scripts/lib/service_acquisition_cleanup.py`;
- worker/tick/incident adapters only if required to preserve safe evidence;
- focused tests and fixtures for the named contracts;
- service version, changelog, runtime manifest, package/release tests if an
  installable successor is produced;
- this plan, `ROADMAP.md`, and append-only `RUNBOOK.md`.

## Dependencies And Gates

- installed Agent Browser access-plan and service-request schemas are external
  contracts; Last30days consumes them but does not repair that runtime;
- profile `last30days-facebook` and recurring configuration are preserved;
- the five-cycle install/live direction is exhausted. Plan version 7 authorizes
  only P7 source, tests, and repository integration; P8 installation and live
  effects require fresh bounded authority;
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

At that point, Checkpoint P0056-C06 was the operative authority. Plan 0056 remains `OPEN`
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

### Checkpoint P0056-C07 | 2026-08-26

Plan version: 7

State transition:

- `post_create_settling_and_request_attribution_repair_planned ->
  provider_neutral_runtime_candidate_validation`.

Progress classification:

- `implementation`; the P7 behavior repair and architecture extraction are
  complete in source and are proceeding through provider-free validation.

Authority classification:

- `inherited_authority`; the operator requested the codebase architecture repair,
  tests, and merge if successful. This checkpoint adds no install, browser
  operation, provider attempt, recurring configuration change, incident, or
  notification authority.

Subagent status and reconciliation:

- `not_spawned`; current orchestration policy prohibits delegation.

Evidence:

- the inherited LinkedIn session-trace fixture failed before repair and passed
  after request-local attribution superseded inventory `traceFilter`;
- the delayed X inventory fixture failed before repair and passed after a poll
  bounded to six exact-session reads and five seconds, with one `tab_new` and
  one handle-bound readiness operation;
- `agent_browser_runtime.py` now owns provider-neutral acquisition, target
  coherence, page control, evaluation, and exact release. X, LinkedIn, Reddit,
  YouTube, and cleanup import it directly; Facebook retains provider-specific
  defaults, auth, query capture, and target recovery behind a subclass;
- the affected 322-test provider selection passes, as do the runtime manifest,
  reproducible package, version, release, source-log, and focused architecture
  checks. The first comprehensive run preserved four failures: three stale
  Facebook-test patch targets and the expected pre-C07 plan audit. The three
  test seams and checkpoint declaration were corrected without changing
  production behavior. The canonical rerun then passed with 2,697 tests, seven
  skips, and eight subtests;
- all MCP Go packages pass; CodeGraph is current and resolves the shared base
  in `agent_browser_runtime.py` with provider-specific X, LinkedIn, Facebook,
  and Reddit subclasses; the dirty-tree skill build contains 152 files and the
  deterministic 0.3.72 service artifact SHA-256 is
  `e57cc8af1d34e1da58e63e24fa22d670b4f6653506cdc1c94a9133e0e842b49b`;
- service version remains 0.3.72. The refreshed source manifest is a build
  boundary only and no release artifact was installed. Source checkpoint is
  `a52a5e66354c517e3f35d803a031b7d90364e93d`; Graphiti closeout job
  `b552a94e-ea5f-4da3-b819-4922be10a598` is queued in
  `last30days_skill_main`.

Next action:

- create a source checkpoint, record its immutable hash in the runbook, then
  push and integrate to `origin/main`. Stop before install or any live provider
  attempt.

Checkpoint P0056-C07 is the current authority for implementation and
repository integration. Plan 0056 remains `OPEN` because installed and live
X/LinkedIn 20/20 acceptance are separately gated and unmet.

### Checkpoint P0056-C08 | 2026-08-26

Plan version: 8

State transition:

- `provider_neutral_runtime_candidate_validation ->
  successor_install_and_single_20_20_acceptance_authorized`.

Progress classification:

- `implementation`; the integrated P7 candidate is entering exact release,
  transactional installation, and one bounded live acceptance receipt.

Authority classification:

- `inherited_authority`; the operator said to try again after P7 integration,
  clearing the prior human gate.
  This authorizes one successor install and one schedule-disabled combined
  home-feed tick with a single X attempt and a single LinkedIn attempt, each
  capped at 20 accepted items. It does not authorize a retry, Agent Browser
  changes, profile replacement, recurring-config mutation, incident handling,
  or notification delivery outside the tick contract.

Subagent status and reconciliation:

- `not_spawned`; current orchestration policy prohibits delegation.

Evidence:

- source, `origin/main`, and `origin/fix/linkedin-accepted-yield` agree at
  `699ef3e637fde797d1eab9b44734ee86cd939ca5` before this checkpoint;
- P7 validation passed with 2,697 tests, seven skips, eight subtests, all Go
  packages, and reproducible provider-neutral runtime packaging;
- service 0.3.72 remains the last documented installed identity pending fresh
  installed-runtime readback; the recurring ten-item configuration and daily
  schedule remain outside this packet.

Next action:

- validate and release one exact successor, install it transactionally,
  perform fresh service/database/schedule/config preflight, and admit exactly
  one combined X plus LinkedIn 20/20 tick. Stop at its terminal receipt and
  reconcile all durable counters and unchanged-state proofs.

Checkpoint P0056-C08 is the current authority. Plan 0056 remains `OPEN` until
the bounded installed/live receipt is reconciled.

### Checkpoint P0056-C09 | 2026-08-26

Plan version: 9

State transition:

- `successor_install_and_single_20_20_acceptance_authorized ->
  installed_acceptance_terminal_preobservation_failures`.

Progress classification:

- `blocker_reduction`; the provider-neutral successor is installed and live,
  but the one bounded tick proves two distinct pre-observation failures rather
  than 20/20 acceptance.

Authority classification:

- `human_gate`; the sole P8 tick is consumed. No retry, repair, rollback,
  Agent Browser operation, recurring-config change, incident transition, or
  notification delivery is authorized by this checkpoint.

Subagent status and reconciliation:

- `not_spawned`; current orchestration policy prohibits delegation.

Evidence:

- pushed source checkpoint `d590b6cbc80fb0e101512a10af71229e3f589f0b`
  released service 0.3.73. Four deterministic artifacts agree at SHA-256
  `d89baaa7ca1b0976894d893712b9be883e9293f02d6352f3ab10b42d0cac9266`;
  runtime manifest SHA-256 is
  `eb958fa36f6c86e039005095a1f633cc5eb12b803b95e94492f8c66c6d55b417`;
- the focused release/browser selection, the complete canonical suite with
  2,697 tests, seven skips, and eight subtests, and all MCP Go packages pass;
- exact 0.3.73/schema 16 installed `ready`; 0.3.72 is the verified previous
  release. MCP service readback is compatible and names the same manifest;
- schedule-disabled tick `tick-86c0a6f0d60b4a66301e027d9e4981d5`, execution
  `tick-attempt-052803dc2068e090b7ad2ffdf503eee4`, and sanitized config digest
  `sha256:d7a6c0100212ab8b7e23ecc97d516b9dbd844bc4421bb2146e89a3c8732efbfa`
  terminalized `complete_degraded` after exactly two attempts, 29 wall seconds,
  one accounted network request, zero items, zero model tokens, and zero cost;
- X attempt `provider-attempt-eed3fb9a676701bbefe5edbe689f0393`
  terminalized `adapter_exception` at `adapter_execution`, signature
  `sha256:07bfc774cc33ac79038bada703a8ddaede5886b64e69b5944def5a8dde4b4087`,
  with `0 attempted / 0 observed / 0 accepted / 0 rejected` and no durable
  browser-operation evidence. The acquisition worker's generic exception
  boundary deliberately discards the exception class and message, so this is
  a Last30days observability limit and cannot establish browser or auth cause;
- LinkedIn attempt `provider-attempt-7b37d65cb4011a09e32434766dbc9f68`
  terminalized `agent_browser_error` at `workspace_acquisition`, signature
  `sha256:c1c6d0ff8a494273a826a1aa7bd837ac915fb7e8af0f35670cf007510b365376`,
  at `0/0/0/0`. Its only durable operation is `service/ok` in 73 ms, proving
  the service boundary was reached but not a tab, auth probe, or feed;
- both resource leases have exact release timestamps. SQLite quick check is
  `ok`, with zero active tick attempts, provider attempts, or unreleased
  leases. The tick created zero incidents and zero notifications;
- recurring config SHA-256 remains
  `28212c6a182fc191c2cb09bc0c645b4b9386f497b2f6b00b2025c24e78abf604`.
  `daily-default` remains enabled/ready for `2026-08-27T00:00:00Z` and was not
  advanced by the manual tick.

Next action:

- stop. Under fresh repair authority, first preserve a bounded exception class
  at the X adapter boundary and the specific typed acquisition reason at the
  LinkedIn boundary, then fixture the exact installed paths before considering
  another provider attempt. Do not infer logout, scraper quality, or feed
  exhaustion from either zero-observation receipt.

Checkpoint P0056-C09 is the current authority. Plan 0056 remains `OPEN` because
neither lane reached observation or 20 accepted items.

### Checkpoint P0056-C10 | 2026-08-26

Plan version: 10

State transition:

- `installed_acceptance_terminal_preobservation_failures ->
  failure_cause_repair_active`.

Progress classification:

- `blocker_reduction`; the successor targets only the two verified diagnostic
  blind spots before one bounded installed/live acceptance attempt.

Authority classification:

- `inherited_authority`; the operator explicitly said `ok go` after the
  proposed Last30days repair and single successor 20/20 tick. The packet may
  edit, test, release, install, and invoke that one tick. It may not modify or
  operate Agent Browser itself, change recurring source configuration, retry
  either provider, or infer authentication/content quality before observation.

Subagent status and reconciliation:

- `not_spawned`; current orchestration policy prohibits delegation.

Evidence:

- C09's X result is a deterministic reproducer of exception-class loss at the
  acquisition worker's public adapter boundary;
- C09's LinkedIn result proves a typed workspace-acquisition failure reached
  the durable tick, but its specific normalized acquisition reason did not;
- source and `origin/main` begin this packet clean and equal at
  `ae4264c9072f73dd65f7379d598edd4dcce57a55`; installed 0.3.73 remains the
  pre-repair baseline with 0.3.72 retained.

Controller, bound, and terminal stop:

- controller: primary orchestrator;
- repair loop: one red/green public-boundary slice per evidence-loss path;
- live bound: one X attempt plus one LinkedIn attempt in one schedule-disabled
  tick, 20 accepted-item ceiling per lane, no per-provider retry;
- terminal stop: the first durable terminal receipt, regardless of outcome.

Next action:

- write the X exception-loss regression first, prove it red, then implement
  only bounded normalized cause evidence with no raw exception-message leak.

Checkpoint P0056-C10 is the current authority. Plan 0056 remains `OPEN` until
the exact installed successor and terminal live receipt are reconciled.

### Checkpoint P0056-C11 | 2026-08-26

Plan version: 11

State transition:

- `failure_cause_repair_active ->
  terminal_tick_localized_direct_broker_timeout_translation_gap`.

Progress classification:

- `blocker_reduction`; 20/20 acceptance remains unmet, but both previously
  opaque failures now resolve to the same exact Last30days exception class and
  code path.

Authority classification:

- `human_gate`; the single C10 live tick is consumed. No retry, second install,
  Agent Browser operation or mutation, recurring-config mutation, manual
  incident transition, or notification delivery is authorized.

Subagent status and reconciliation:

- `not_spawned`; current orchestration policy prohibits delegation.

Evidence:

- pushed repair commit `bac91709935da06cbb3e2240ac75e78fb97b254e`
  releases service 0.3.74. The clean artifact SHA-256 is
  `3a259d6712ff11be262b5c48a723ff69a2f2b41b41f27d24230b280345d2667f`
  and installed runtime-manifest SHA-256 is
  `9eef9535471d3b276074c1199ea47a09ba79011d3b93bbe08ef0bfbe19fccb5d`;
- 0.3.74/schema 16 is installed `ready`, exact service/MCP readback is
  compatible, and 0.3.73 is retained as previous;
- affected social/runtime/tick tests pass; the complete canonical suite is
  `2,699 passed / 7 skipped / 8 subtests passed`; all MCP Go packages pass;
  the clean 152-file skill build, service package, and plan audit pass;
- ready preflight predicted tick `tick-1294554510e56c82bbadb2e116b412f2`,
  config digest
  `sha256:ededfa17f4110b291bf4db55ea1ba1d54dcfc6a8d9b3e10b95649c0baed680a6`,
  two attempts, 40 items, 100 requests, 240 seconds, and zero model/cost;
- that exact schedule-disabled tick terminalized `complete_degraded` after one
  execution, exactly two provider attempts, 55 accounted wall seconds, zero
  items, requests, model tokens, and cost;
- X attempt `provider-attempt-78d4fc9e5d4f1f54cfe2bb21b017b2dd`
  failed `adapter_exception/adapter_execution` with reason
  `unexpected_timeout_expired`, signature
  `sha256:b9d8044c7d4b8b3ca18660fc20f5ca71ffd31eb1cb3dbe954b3dfaddd4cf2b91`,
  `0 attempted / 0 observed / 0 accepted / 0 rejected`, 28 seconds, and no
  browser-operation evidence;
- LinkedIn attempt `provider-attempt-031fd74ec725f3e21b6059290186847e`
  failed the same code/stage/reason at `0/0/0/0`, 27 seconds, signature
  `sha256:b59aa4f936945b0ee53ba85a13e46febfecadcf1ffa3a1f0a7258f1690a6aaf4`,
  and no browser-operation evidence;
- source trace shows `acquire_workspace()` directly calls
  `_invoke_service_request()`, whose `subprocess.run(..., timeout=...)` does
  not translate `subprocess.TimeoutExpired`; the exception therefore escapes
  the typed `AgentBrowserRuntimeFailure` boundary into the worker's generic
  adapter catch;
- both exact leases are released; SQLite quick check is `ok`; active tick and
  provider attempts, unreleased leases, incidents, and notifications are all
  zero;
- recurring config SHA-256 remains
  `28212c6a182fc191c2cb09bc0c645b4b9386f497b2f6b00b2025c24e78abf604`.
  `daily-default` remains enabled/ready for `2026-08-28T00:00:00Z`; its normal
  `2026-08-27T00:00:00Z` boundary occurred independently before the manual
  tick and was not modified by this packet.

Next action:

- provider-free only: translate `subprocess.TimeoutExpired` inside the direct
  broker request to typed `agent_browser_timeout` with a normalized reason,
  fixture both acquisition paths, and validate a successor. Another install
  or live tick requires a separately bounded successor packet.

Checkpoint P0056-C11 is the current authority. Plan 0056 remains `OPEN` because
neither lane reached observation or 20 accepted items.

### Checkpoint P0056-C12 | 2026-08-26

Plan version: 12

State transition:

- `terminal_tick_localized_direct_broker_timeout_translation_gap ->
  direct_browser_and_broker_lease_diagnosis_active`.

Progress classification:

- `blocker_reduction`; direct browser commandability, current profile
  attribution, broker lease waits, and the Last30days translation gap are now
  separate evidence boundaries.

Authority classification:

- `inherited_authority`; the operator explicitly requested direct Agent
  Browser page confirmation followed by Last30days instrumentation and actual
  diagnosis. This packet may read the retained browser and service trace and
  implement provider-free Last30days timeout instrumentation. It may not
  close, replace, reconcile, or mutate Agent Browser profiles/browsers, install
  a successor, run another provider tick, or change recurring configuration.

Subagent status and reconciliation:

- `not_spawned`; current orchestration policy prohibits delegation.

Controller, bound, and terminal stop:

- controller: primary orchestrator;
- implementation loop: one red/green public workspace-acquisition regression;
- runtime probes: one bounded direct page read per source and one bounded
  non-waiting MCP lifecycle probe;
- terminal stop: typed timeout instrumentation validated, exact causal report
  written, or a new Agent Browser mutation/install/live-tick gate is reached.

Evidence:

- direct retained-session control completed tab switch, URL/title reads, and
  DOM snapshots in 1-51 ms; bounded X navigation completed in 2,186 ms;
- current live service state records `session:handoff-356556ee1fe03a25` as a
  ready `attached_existing` browser with profile `default`, while the durable
  `last30days-facebook` profile allocation has no browser holder;
- retained trace records X and LinkedIn profile-lease waits of 30,232 ms and
  30,280 ms against that handoff, followed by typed lease-conflict failures;
- the exact Last30days MCP stdio wrapper completed a non-waiting read-only
  `tab_list` request and exited in 148 ms, falsifying an MCP process-exit hang;
- two public-boundary regressions failed before their respective fixes and now
  pass. The affected runtime, X, LinkedIn, acquisition-worker, and tick suites
  pass with 147 tests and two skips in aggregate;
- the comprehensive suite reached `2,690 passed / 7 skipped / 8 subtests` with
  11 expected release-packaging failures because 0.3.74's tracked runtime
  manifest intentionally remains bound to the pre-instrumentation source. A
  direct build confirms the sole gate: `service/runtime-manifest.json is
  stale; run service/scripts/build-runtime.sh --refresh-manifest`;
- active planning audit, `git diff --check`, and Python compilation pass. Ruff
  is unavailable in the repository uv environment;
- source checkpoint `5b2bfaa2a1319cb3fe56e63620357f6334842fd5`
  and its P08 branch-custody proposal are pushed. The exact active-lane audit
  still reads the canonical `origin/main` catalog, where P08 remains projected
  as integrated at `1a74d3674b8da9c44357ce5005c13d8ba362022a`;
  `stale_checkpoint` and `integrated_cleanup_pending` therefore remain a
  default-branch catalog reconciliation gate, not a source-test failure.

Next action:

- cut a separately authorized source successor if this instrumentation should
  enter the release manifest. Before any meaningful live tick, repair or
  reconcile the Agent Browser lifecycle/profile identity through Agent
  Browser's own authority; do not use the current `default` browser as proof
  for `last30days-facebook`.

Checkpoint P0056-C12 is the current authority. Plan 0056 remains `OPEN` because
the intended profile is not currently commandable through a coherent broker
route and neither lane has reached observation or 20 accepted items.

### Checkpoint P0056-C13 | 2026-08-29

Plan version: 13

State transition:

- `direct_browser_and_broker_lease_diagnosis_active ->
  broker_handle_contract_repair_and_single_20_20_acceptance_active`.

Progress classification:

- `blocker_reduction`; current Agent Browser source, history, and live
  readback localize the pre-readiness failure to Last30days consuming the
  wrong tab-inventory surface after successful broker acquisition.

Authority classification:

- `inherited_authority`; the operator explicitly requested planning,
  execution, and a reattempt of the 20+20 test. This packet authorizes the
  Last30days implementation, validation, exact successor installation when
  required, and one schedule-disabled combined tick with one X and one
  LinkedIn attempt capped at 20 accepted items each. It does not authorize an
  Agent Browser implementation or lifecycle change, profile replacement,
  recurring-config mutation, or a second live tick.

Subagent status and reconciliation:

- `not_spawned`; current orchestration policy prohibits delegation.

Controller, bound, and terminal stop:

- controller: primary orchestrator;
- implementation loop: one red/green contract slice plus one focused
  regression repair if validation exposes a directly related failure;
- live bound: one X attempt plus one LinkedIn attempt in one
  schedule-disabled tick, 20 accepted-item ceiling per lane, zero
  model/cost budget, and no per-provider retry;
- terminal stop: both lanes return 20 unique accepted posts, or the first
  combined durable receipt terminalizes and is fully reconciled.

Evidence:

- Agent Browser commit `8ba25fdfcad2405a9c83f42461a807d77adc59c9`
  introduced `tab list --verbose` for diagnostic `targetId` and `sessionId`
  while retaining the ordinary compact inventory;
- current Agent Browser `tab_list(false)` omits those identifiers and its
  service-client contract says broker consumers must use the returned
  `serviceTabHandle` rather than rediscover raw target identity;
- Last30days commit `a52a5e66354c517e3f35d803a031b7d90364e93d`
  introduced `_require_service_tab_identity()`, whose ordinary `tab list`
  request searches for the unavailable `targetId`; its unit fixture returns
  fields the real ordinary surface omits;
- branch and remote agree at
  `f2bd39fd606609d423c1793d03ad28374c9b3a4f` before implementation.

Next action:

- make the realistic broker-handle regression red, remove raw target
  rediscovery from the acquisition path, require handle-scoped readiness,
  then run focused and canonical validation before any install or live tick.

Checkpoint P0056-C13 is the current authority. Plan 0056 remains `OPEN` until
the installed and live 20/20 result is reconciled.

### Checkpoint P0056-C14 | 2026-08-29

Plan version: 14

State transition:

- `broker_handle_contract_repair_and_single_20_20_acceptance_active ->
  x_20_proven_linkedin_collection_budget_blocker_observed`.

Progress classification:

- `partial_acceptance`; the post-broker tab-discovery defect is repaired and
  X reaches the requested ceiling. LinkedIn reaches authenticated feed
  observation and durable publication, but does not reach 20 accepted items.

Authority classification:

- `inherited_authority`; the one combined live tick authorized by
  P9 terminalized. No second live tick, Agent Browser mutation, or recurring
  configuration change is authorized by this checkpoint.

Implementation and validation evidence:

- source commit `cd6bd726a072692c5cd408cb87e92e71a875dc68`
  removes ordinary-tab target rediscovery after broker acquisition, rejects
  an explicitly invalid handle, and sends the first readiness probe through
  the returned `serviceTabHandle`;
- the affected runtime, X, LinkedIn, Facebook, acquisition-worker, cleanup,
  incident, Reddit, and YouTube suites pass; the canonical Python suite passes
  with `2,700 passed / 7 skipped / 6 subtests`; `go test ./...`, release tests,
  active-plan audit, and `git diff --check` pass;
- clean artifact `last30days-service-0.3.75.tar.gz` has SHA-256
  `83abe719a72df4812457acf711c660d745cfe5937c55cd49f4ad27b537f380b9`;
- installed release `releases/0.3.75` is `ready`, database schema 16, runtime
  manifest SHA-256
  `da02581da9c651c12d080f9253a9f861347d70e1d3748269d70ad8df4111cd98`;
  `releases/0.3.74` is retained as the previous release.

Live receipt evidence:

- schedule-disabled tick `tick-1aff45976d98120d147d2035f60ecc09`
  terminalized `complete_degraded` and promoted snapshot
  `tick-snapshot-a3defde49483cc7c16bde90c461ad73c`;
- X terminalized `success`: 38 attempted/observed, 20 accepted, 18 rejected,
  4 network requests, and 36 wall seconds. All 20 accepted records have unique
  canonical `x.com/.../status/...` permalinks;
- LinkedIn terminalized `failure` with a partial result: 117
  attempted/observed, 13 accepted, 104 rejected, 50 network requests, and 86
  wall seconds. Its safe failure is `network_budget_exhausted` at
  `media_fetch`, not authentication or browser acquisition;
- LinkedIn rejection counts are overlapping: duplicate 51, deterministic ad
  kind 22, sponsored 22, missing date 50, missing author 24, missing permalink
  12, and unknown kind 12. The 13 published records carry LinkedIn activity
  permalinks, but one canonical URL was accepted under two fallback native
  identifiers, leaving 12 distinct canonical URLs;
- aggregate usage was 2 attempts, 33 accepted items, 54 network requests, 122
  wall seconds, and zero model tokens/cost. Database integrity is `ok`.

Diagnosis:

- the latest result falsifies Agent Browser authentication and tab discovery
  as the current LinkedIn blocker. Two later boundaries are independently
  wrong: admission rejects observed cards for missing scraped date, author,
  permalink, or kind metadata even though the operator's current policy only
  excludes deterministic ads/spam, and optional media hydration can exhaust
  the provider network budget and turn a published partial result into lane
  failure;
- canonical-URL identity is also not the final dedupe key: the same LinkedIn
  activity permalink was accepted twice under different fallback native IDs;
- reaching a trustworthy LinkedIn 20 requires a separately authorized repair
  that preserves legitimate posts despite recoverable extraction gaps,
  excludes only deterministic ads/spam, collapses identical canonical
  activity URLs before accepted counts are committed, and prevents optional
  media hydration from failing primary post collection.

Next action:

- design a bounded red/green successor for LinkedIn extraction-gap admission,
  canonical-URL deduplication, and primary-item collection versus optional
  media-hydration failure, then seek authority for one new combined acceptance
  tick. Do not increase recurring collection limits or issue another live tick
  from this checkpoint.

Checkpoint P0056-C14 is the current authority. Plan 0056 remains `OPEN` because
X is proven at 20 but LinkedIn is proven only at 13 accepted records and 12
distinct canonical post URLs.

### Checkpoint P0056-C15 | 2026-08-29

Plan version: 15

State transition:

- `x_20_proven_linkedin_collection_budget_blocker_observed ->
  linkedin_retrieval_reliability_successor_active`.

Progress classification:

- `blocker_reduction`; the P9 receipt separates three Last30days defects after
  successful authenticated feed observation: metadata-gap admission,
  canonical-URL identity, and optional-media failure propagation.

Authority classification:

- `inherited_authority`; the operator-approved goal remains a verified 20+20
  tick. Goal-execution policy treats the prior packet's hard stop as ending
  that unchanged attempt, not revoking standing authority for an in-envelope
  changed-input successor. P10 changes implementation semantics before one new
  live tick and does not change systems, profile, audience, data class, cost,
  or recurring configuration.

Subagent status and reconciliation:

- `not_spawned`; current orchestration policy prohibits delegation.

Controller, bound, and terminal stop:

- controller: primary orchestrator;
- implementation loop: at most one red/green slice each for feed admission,
  canonical-URL identity, and optional-media failure isolation, plus one
  directly related repair pass if broader validation exposes a regression;
- live bound: one schedule-disabled combined tick, one X attempt and one
  LinkedIn attempt, 20 accepted-item ceiling per lane, zero model/cost budget,
  and no unchanged-input retry;
- terminal stop: both lanes prove 20 unique accepted posts, or the one P10
  durable receipt terminalizes and is fully reconciled.

Current evidence:

- branch and remote agree at
  `3736bd72375fe53fe708a0d3052a2336d1ee1ae1`; the worktree is clean and
  `origin/main` remains `ef98acf13d22c2422381f7f0b14e0b0da64239cd`;
- installed service 0.3.75 is compatible and ready on schema 16; current
  service discovery reports both X and LinkedIn acquisition-ready;
- current Agent Browser 0.28.0 access plans select profile
  `last30days-facebook`, reuse retained browser
  `session:last30days-social-replacement-20260829`, and report no acquisition,
  lifecycle, lease, policy, or manual-action blocker for either source;
- P9 receipt `tick-1aff45976d98120d147d2035f60ecc09` proves X 20/20 and
  LinkedIn 13 accepted from 117 observed, including one duplicated canonical
  activity URL and terminal `network_budget_exhausted` at `media_fetch`;
- code inspection proves feed quality currently rejects missing author/date,
  deduplicates on URL plus mutable text, and promotes optional media exhaustion
  to the top-level acquisition error even when primary posts were collected.

Next action:

- add one public-boundary LinkedIn feed regression for recoverable metadata
  gaps, make it red and green, then repeat for canonical URL identity and
  optional media isolation before broader validation and release packaging.

Checkpoint P0056-C15 is the current authority. Plan 0056 remains `OPEN` until
one installed P10 receipt proves 20 unique accepted X posts and 20 unique
accepted LinkedIn posts.

### Checkpoint P0056-C16 | 2026-08-29

Plan version: 16

State transition:

- `linkedin_retrieval_reliability_successor_active ->
  validated_service_0_3_76_install_ready`.

Progress classification:

- `blocker_reduction`; all three receipt-proven Last30days defects have
  public-boundary red/green coverage and the comprehensive suite is green.

Authority classification:

- `inherited_authority`; install and one P10 acceptance tick remain inside the
  standing goal and the bounded successor recorded at C15.

Subagent status and reconciliation:

- `not_spawned`; current orchestration policy prohibits delegation.

Implementation evidence:

- source commit `d47493015f4debfe0e098d71aba1f16b2262a57a`
  changes LinkedIn home-feed admission so permalinked posts with missing
  rendered author/date metadata remain primary evidence with explicit
  retrieval signals; topic-search quality behavior remains unchanged;
- canonical LinkedIn activity URLs now define accepted identity and stable
  source-native IDs, so card text expansion cannot create a second accepted
  post;
- optional media errors remain bounded and diagnostic but no longer promote
  to a top-level acquisition failure when primary posts were collected;
  zero-item media failures still fail closed;
- service version advances to 0.3.76 with a refreshed runtime manifest and
  release note.

Validation evidence:

- each new public-boundary tracer bullet failed before its implementation and
  passed afterward: metadata-gap feed admission, canonical-permalink identity,
  and optional-media budget isolation;
- a combined fixture now reaches 20 unique LinkedIn feed posts with missing
  author/date metadata while five deterministic sponsored cards remain
  excluded;
- affected LinkedIn, profile, acquisition-worker, tick-runner, tick-runtime,
  media, incident, and query suites pass;
- the first comprehensive run produced only 11 expected stale-manifest release
  failures with 2,693 passing tests; after service 0.3.76 manifest refresh, the
  canonical suite passes `2,704 passed / 7 skipped / 6 subtests` in 141.23
  seconds;
- `go test ./...`, Python compilation, active-plan audit, and
  `git diff --check` pass.

Next action:

- publish the validated source checkpoint, build clean skill and service
  artifacts, transactionally upgrade the installed service from 0.3.75 to
  0.3.76, verify readiness and rollback retention, then preflight the one P10
  schedule-disabled 20+20 tick.

Checkpoint P0056-C16 is the current authority. Plan 0056 remains `OPEN` pending
installed and live 20+20 evidence.

### Checkpoint P0056-C17 | 2026-08-29

Plan version: 17

State transition:

- `validated_service_0_3_76_install_ready ->
  linkedin_bounded_scroll_yield_successor_active`.

Progress classification:

- `blocker_reduction`; P10 proves both Agent Browser acquisition paths and
  both provider attempts succeed. The remaining LinkedIn deficit is isolated
  to bounded feed depth under virtualized overlap and deterministic ad load.

Authority classification:

- `inherited_authority`; the operator-approved goal remains one verified
  20+20 tick, and the earlier three-attempt budget leaves one changed-input
  attempt after P9 and P10. P11 changes only the LinkedIn feed scroll strategy,
  preserves the same profile, service, item, action, wall-clock, model, cost,
  and recurring-configuration boundaries, and does not mutate Agent Browser.

Subagent status and reconciliation:

- `not_spawned`; current orchestration policy prohibits delegation.

Controller, bound, and terminal stop:

- controller: primary orchestrator;
- implementation loop: one public-boundary red/green slice for accepted-yield-
  aware bounded scrolling, plus one directly related repair pass if validation
  exposes a regression;
- live bound: one final schedule-disabled combined tick with one X attempt and
  one LinkedIn attempt, 20 accepted-item ceiling per lane, zero model/cost
  budget, and no unchanged-input retry;
- terminal stop: both lanes prove 20 unique accepted posts, or the one P11
  durable receipt terminalizes and is fully reconciled.

Current evidence:

- branch and remote agree at
  `3b2285b94fd559949173335a647eadc5365b0698`; the worktree is clean and
  `origin/main` remains `ef98acf13d22c2422381f7f0b14e0b0da64239cd`;
- installed service 0.3.76 is compatible and ready on schema 16 with runtime
  manifest SHA-256
  `40f34491d5fd0482ad3213032662e69cc9040cc0ef9bdf38d8e593f7bed5b94d`;
- P10 tick `tick-d844d848bf526237a683b506af6dad9a` promoted snapshot
  `tick-snapshot-467a41946590146dd239efadee6935f5`: X returned 20 unique
  canonical status URLs; LinkedIn returned 14 unique canonical activity URLs
  from 117 observations, with 77 duplicate, 22 sponsored/ad, and four
  unknown/missing-permalink rejections; both provider attempts are `success`
  and database integrity is `ok`;
- current LinkedIn feed collection allows at most eight 1,400-pixel scrolls,
  and its stagnation counter advances on any new observed card rather than new
  accepted canonical post yield. A new ad or unlinkable card can therefore
  mask flat accepted yield without advancing far enough through the feed.

Next action:

- add one live-shaped public `feed()` regression that remains at 14 under the
  current eight-scroll strategy, make it red and green with accepted-yield-
  aware bounded advancement, then run focused and comprehensive validation
  before packaging and installing one exact successor.

Checkpoint P0056-C17 is the current authority. Plan 0056 remains `OPEN` until
the final installed P11 receipt proves 20 unique accepted X posts and 20
unique accepted LinkedIn posts or terminalizes for durable reconciliation.
