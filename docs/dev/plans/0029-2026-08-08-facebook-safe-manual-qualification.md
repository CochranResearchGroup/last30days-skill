# Plan 0029 | Facebook Safe Manual Qualification

State: CANCELLED
Roadmap: P13
Plan version: 4
Date: 2026-08-08
Predecessor: Plan 0028 version 10/checkpoint P0028-C10

## Objective

Qualify the repaired Facebook adapter for routine attended use through a
source-scoped governed manual tick, while adding explicit fail-closed handling
for an organically encountered Facebook temporary block or frequency limit.

## Current State

- installed service 0.3.30/schema16 is ready and Facebook is acquisition-ready;
- manual tick `tick-f273eb12d642b31d49a7f12959b93b87` proved one successful
  Facebook attempt with 19 observed, two accepted, and 17 truthfully rejected
  candidates;
- the manual tick CLI currently expands every enabled target, so another
  Facebook qualification attempt would unnecessarily exercise Reddit,
  YouTube, X, and LinkedIn;
- `rate_limit_detected` is already a typed Facebook error, but the DOM adapter
  does not currently recognize the corresponding temporary-block or
  action-frequency page state;
- the installed daily schedule remains enabled and is not changed by this
  plan. Qualification execution remains manual and does not wait for a natural
  boundary;
- the one 0.3.29 qualification tick was consumed and stopped fail-closed as
  `complete_degraded`: both post-navigation page-state evaluations reached the
  25-second caller bound, producing `agent_browser_timeout`, zero observed
  candidates, and no auth, checkpoint, CAPTCHA, or rate-limit signal;
- browser PID 63205 remains ready and retained, with 18 valid tabs. No same-build
  retry is permitted;
- two read-only evaluations against the already-open search page reached their
  five-second diagnostic and 20-second production worker bounds without
  navigation or page mutation, so the bounded successor now accepts exact
  active-tab URL/query/filter identity after a post-navigation eval timeout and
  defers content classification to extraction. It does not infer authenticated
  or rate-limit state from URL identity;
- the 0.3.30 successor is installed and offline-validated, but its one live
  qualification tick ran once as
  `tick-2e63a98ad3b92830bee87e61b07cfdf5` and failed before a typed provider
  result was staged. It opened one fresh target after two retained-target
  switch timeouts, navigated, evaluated, and scrolled without any login,
  checkpoint, CAPTCHA, or rate-limit signal, then collapsed to
  `workerexecutionerror` with zero observed/accepted/rejected items;
- criterion 9 was not satisfied and both candidate live-attempt bounds are
  consumed. This plan is cancelled unsuccessfully; Plan 0030 owns the
  item-bound execution and typed worker-receipt successor.

## Scope

- add a repeatable `--service` selector to manual tick `preflight` and
  `enqueue`, deriving a frozen config in which only already-enabled targets for
  the selected service remain enabled;
- bind the selected scope into the frozen config digest, tick identity, lane
  manifest, budgets, and durable receipt without changing timer behavior;
- detect Facebook temporary-block and action-frequency-limit surfaces from
  bounded structural/page signals before navigation and after navigation, and
  stop as `rate_limit_detected` without retry or operator-auth handoff;
- retain sanitized rate-limit reason codes, never raw page text;
- replace the post-navigation proof's unbounded layout-forcing DOM reads with
  bounded `textContent` and capped structural reads so a large Facebook search
  DOM cannot consume the entire evaluation deadline;
- validate, build, install one immutable successor, and consume at most one
  Facebook-only manual qualification tick after a no-state preflight.

## Non-Goals

- no logout, cookie deletion, session expiry, credential entry, MFA, CAPTCHA,
  checkpoint, consent, or account-recovery interaction;
- no attempt to manufacture, simulate against Facebook, or intentionally
  provoke a rate limit, temporary block, login requirement, or challenge;
- no automatic retry, rapid repeated live probe, extra scroll depth, increased
  provider budget, browser/profile launch, tab closure, or retained-session
  cleanup;
- no schedule cadence/source-set mutation, paid/model use, test notification,
  formal release, tag, upstream pull request, or unrelated source repair;
- no claim of unattended durability from fixture tests or one additional live
  proof.

## Acceptance Criteria

1. Manual `tick preflight` and `tick enqueue` accept one or more repeated
   `--service` values; the same scope yields the same tick/lane identity in
   preflight and enqueue.
2. The selector can only disable work: an unknown service, duplicate selector,
   service without an enabled target, or empty selection fails before a tick,
   provider attempt, browser command, or notification; preflight remains
   database-free.
3. A scoped tick freezes only already-enabled targets for its selected
   services; its config digest differs from the equivalent all-source tick, and
   scheduler-created ticks remain all-source with unchanged identity.
4. Facebook recognizes bounded temporary-block/action-frequency signals during
   initial authentication inspection, post-navigation page inspection, and an
   empty extraction read; it returns `rate_limit_detected`, makes no recovery
   navigation or handoff, and persists only a stable reason code.
5. Ordinary authenticated feed/search fixtures, posts discussing rate limits,
   login/checkpoint fixtures, and generic error fixtures retain their existing
   classifications.
6. Focused tests, complete suite, compile, formatting/patch checks, planning
   audits, deterministic package/version checks, and reproducible build pass.
7. Exact successor installation preserves schema 16, rollback, database
   integrity, daily schedule identity/cadence, notification routing, disabled
   legacy specs, and zero-cost/model limits.
8. One no-state `--service facebook` preflight predicts exactly one Facebook
   lane and one provider attempt. If current browser ownership/readiness is
   unambiguous and at least 60 minutes have elapsed since the last Facebook
   provider attempt, one matching manual tick may run with one attempt, no
   retries, and existing scroll/request/wall limits.
9. Qualification succeeds only if that tick returns Facebook `success` with at
   least one accepted post, or a genuine typed empty result. Auth, checkpoint,
   rate-limit, zero-observed failure, or quality-only rejection stops the live
   packet without retry.
10. The bounded rework probes the already-open Facebook search page without
    another navigation, scroll, tab, or tick. If Runtime evaluation remains
    unavailable, navigation may proceed only from exact active-tab
    URL/query/filter identity; content auth/checkpoint/rate-limit
    classification remains mandatory at extraction and is never inferred from
    the URL fallback.

## Definition Of Done

- criteria 1-7 have exact repository and installed-runtime evidence;
- criterion 8 is either consumed once under its guards or records the exact
  preflight/browser blocker without weakening the plan;
- criterion 9 is satisfied before routine attended use is called qualified;
- Plan 0029/P13, `ROADMAP.md`, and `RUNBOOK.md` agree with current evidence;
- the bounded change is committed and pushed to `origin/main`; a Graphiti write
  is attempted once after the durable commit, or its exact failure is recorded.

## Execution Bounds

- primary agent owns the serialized critical path; no subagent is used;
- one implementation attempt plus one bounded rework cycle;
- offline red/green tests may use synthetic page-state fixtures but no live
  challenge or rate-limit page is requested;
- one initial candidate version/build/install and one bounded successor rework;
  at most one live Facebook-only tick per candidate, with a new 60-minute gap
  required before any successor tick;
- no same-build live retry and no natural-time wait;
- hard stop on browser ownership ambiguity, login/checkpoint/CAPTCHA,
  organically observed rate limit, nonzero cost/model use, notification send,
  schedule drift, database-integrity failure, or privacy-sensitive output.

## Owned Write Surfaces

- `skills/last30days/scripts/lib/service_tick.py`
- `skills/last30days/scripts/lib/service_tick_runtime.py`
- `skills/last30days/scripts/service.py`
- `skills/last30days/scripts/lib/facebook.py`
- focused tick preflight/CLI and Facebook tests;
- `CONFIGURATION.md`, `CHANGELOG.md`, service version/runtime manifest, and
  relevant operator help;
- this plan, `ROADMAP.md`, `RUNBOOK.md`, and one serial closeout receipt if the
  live packet runs.

### Checkpoint P0029-C01 | 2026-08-08

Plan version: 1

State transition:

- `single_facebook_success -> safe_manual_qualification_in_progress`.

Progress classification:

- `validated_learning`; live/runtime evidence proves the adapter works once,
  while the all-source-only manual interface and missing rate-limit page
  classifier make repeated qualification needlessly broad and insufficiently
  fail-closed.

Validation evidence:

- `main` and `origin/main` match at
  `24474f62e5e11f1c51d5ab5adf0f0933764dce91` with a clean worktree;
- installed service 0.3.28/schema16 reports ready and Facebook
  acquisition-ready;
- current config retains the one-attempt, zero-cost/model Facebook provider and
  the enabled `daily-default` 86,400-second schedule;
- recent durable history contains the accepted Facebook attempt at
  `2026-08-09T01:29:46Z`; no live attempt is used to establish this plan;
- CodeGraph traces manual preflight/enqueue through `_prepare_tick` and
  `_expand_lanes`, and confirms scheduler construction uses the same runtime
  without a selector;
- policy selection reports `repo-product-engineering`, fully installed, with no
  missing recommended modules.

Subagent status and reconciliation:

- none; the selector, identity, scheduler invariant, and Facebook classifier
  are one tightly coupled critical path.

Authority classification:

- `inherited_authority`; this implements and tests the requested usability
  upgrades while preserving the explicit no-logout/no-CAPTCHA/no-rate-limit
  boundary and manual-proof rule.

Graphiti write status:

- deferred until a validated implementation or durable blocker exists.

Next action:

- add red selector/identity and Facebook rate-limit classification tests, then
  implement the narrow fail-closed behavior without running Facebook.

### Checkpoint P0029-C02 | 2026-08-08

Plan version: 2

State transition:

- `safe_manual_qualification_in_progress -> navigation_readback_rework`.

Progress classification:

- `validated_blocker`; criteria 1-8 are implemented and installed, while the
  only authorized 0.3.29 live tick disproved criterion 9 with a repeatable
  bounded navigation-readback timeout before candidate observation.

Validation evidence:

- installed 0.3.29/schema16 reports ready with contract SHA-256
  `fe8727fbe0d4e2f6775f49a6fc958369fe4877ba812bae4ef69121b88f12e2f1`
  and runtime-manifest SHA-256
  `a19715668f81cee4cb06a405d6e22055aeff6ed39ffedf90436651aa128352f5`;
- installed preflight predicted exactly tick
  `tick-b870ef9c5dc3be015c7ddce04b6d74f4`, lane
  `tick-lane-348957642ce15c32787c8da050fa2df0`, and one
  `facebook_agent_browser` provider with one attempt, 50 requests, 120
  seconds, three items, and zero cost/model budget;
- provider attempt `provider-attempt-6c22811abf9a8f99f8e65e25917b5542`
  ran once for 111 seconds and failed transiently with
  `agent_browser_timeout`, zero observed/accepted/rejected candidates, and no
  page signal;
- browser operations show successful access-plan/status/tab/auth reads, two
  successful search opens, and exactly two 25-second page-state eval timeouts;
  no second provider attempt or fallback exists;
- daily schedule `daily-default` remains enabled and ready at 86,400 seconds;
  database quick check is `ok`; no model/cost use occurred;
- agent-browser workstation repair converged with no doctor issues,
  `remoteControl.status=ready`, executable SHA-256
  `1be6aa821546c00a753299ff2062cf09f658d32cb33326f594349d4782c80468`,
  and retained browser PID 63205 remained healthy. Its tab count advanced from
  17 to 18 because the adapter's fresh-target navigation recovery opened one
  service-owned tab; no tab or browser was closed.

Subagent status and reconciliation:

- none; the primary traced the post-navigation eval flow through CodeGraph and
  owns the single bounded rework cycle.

Authority classification:

- `inherited_authority`; this rework remains inside the approved adapter
  upgrade and testing scope, preserves all explicit no-logout/no-CAPTCHA/
  no-rate-limit controls, and does not authorize another immediate tick.

Graphiti write status:

- deferred until the bounded rework has durable validation evidence.

Next action:

- add red source-shape and page-state contract tests, replace layout-forcing
  navigation reads with capped layout-free reads, and run one read-only eval
  against the existing search page. Do not navigate, scroll, close a tab, or
  enqueue another tick.

### Checkpoint P0029-C03 | 2026-08-08

Plan version: 3

State transition:

- `navigation_readback_rework -> successor_installed_acceptance_gated`.

Progress classification:

- `validated_learning`; bounded layout-free Runtime reads still timed out, so
  the successor uses exact active-tab identity only to prove navigation while
  retaining content classification at extraction. Offline and installed
  evidence pass; criterion 9 remains unproved.

Validation evidence:

- one five-second diagnostic and one 20-second production read-only evaluation
  of the existing Facebook search page returned service job timeouts. Neither
  command navigated, scrolled, switched or closed a tab, changed browser
  lifecycle, or consumed a provider attempt;
- 0.3.30 adds a tested timeout fallback that parses the active tab inventory,
  requires exact topic query and recent-post filter identity, avoids the fresh-
  tab recovery path when those checks pass, and defers content inspection to
  extraction. A mismatch retains the existing fail-closed recovery behavior;
- focused Facebook, manual-tick, runtime, package, version, and install tests
  pass; the complete suite, compile, patch check, planning audits, and two
  independent reproducible builds pass;
- both 0.3.30 builds and the installed artifact have SHA-256
  `56bde95e7e707f07e94f8cf2149e28bd647358129390e7c67cfc0d0c677c5290`;
- installed 0.3.30/schema16 reports ready with contract SHA-256
  `fe8727fbe0d4e2f6775f49a6fc958369fe4877ba812bae4ef69121b88f12e2f1`
  and runtime-manifest SHA-256
  `d762fd55a3b080dc3da36da528843199338e416a7b7503bf494bb80f07d6bcad`;
- releases 0.3.28, 0.3.29, and 0.3.30 are retained; database quick check is
  `ok`; `daily-default` remains enabled and ready at 86,400 seconds;
- installed preflight remains deterministic at tick
  `tick-b870ef9c5dc3be015c7ddce04b6d74f4`, lane
  `tick-lane-348957642ce15c32787c8da050fa2df0`, one Facebook attempt,
  50 requests, 120 seconds, three items, and zero cost/model budget;
- agent-browser install doctor reports no issues and converged runtime;
  retained browser PID 63205 remains viable with 18 tabs;
- `npx skills add . -g -y` refreshed the frozen `last30days` and
  `repo-policy-selector` install copies for supported hosts; PromptScript
  truthfully reported that it does not support global Skill installation.

Subagent status and reconciliation:

- none; the primary owns the serialized repair and acceptance gate.

Authority classification:

- `inherited_authority`; exact-tab identity is a narrower navigation proof,
  not an authentication or content-success shortcut, and the required live
  qualification remains unchanged.

Graphiti write status:

- provider readiness passed and the compact source-backed memory for durable
  implementation commit `2c0009998f059cc7d6263fbece8773821bc1ad3b` was
  queued once as job `362d75af-7773-474b-a911-854f9f54f0de` in group
  `last30days`; no duplicate write was attempted.

Next action:

- after `2026-08-09T04:48:46Z`, recheck installed service/browser ownership and
  run at most one 0.3.30 Facebook-only manual tick. Do not wait on the natural
  scheduler, bypass the 60-minute gap, or retry a failed successor attempt.

### Checkpoint P0029-C04 | 2026-08-09

Plan version: 4

State transition:

- `successor_installed_acceptance_gated -> live_qualification_rejected`;
- `OPEN -> CANCELLED`.

Progress classification:

- `validated_blocker`; the sole 0.3.30 successor tick reached authenticated
  Facebook navigation and extraction work but failed at the isolated worker
  boundary before it could stage a typed provider result. Criterion 9 remains
  false and this plan's live bounds are exhausted.

Validation evidence:

- preflight and enqueue agreed on tick
  `tick-2e63a98ad3b92830bee87e61b07cfdf5`, lane
  `tick-lane-2666c4eddc6a94664d2f7083050e972d`, one
  `facebook_agent_browser` attempt, 50 requests, 120 seconds, three items, and
  zero cost/model budget;
- execution attempt `tick-attempt-029f02fdf5e58957fa41b58346e90eab`
  and provider attempt `provider-attempt-296bd9c8c3a600c379f566d7a884dab3`
  ran once from `2026-08-09T14:14:42Z` through `14:16:32Z`; the tick failed as
  `workerexecutionerror`, the provider attempt retained failure class
  `integrity`, and no provider result was staged;
- retained agent-browser jobs show two bounded three-second tab-switch
  timeouts, one successful fresh tab, successful authentication/page
  evaluations, successful navigation, and two successful scrolls. The trace
  ends before the final extraction read; no logout, login form, checkpoint,
  CAPTCHA, rate-limit event, incident, notification, fallback, cost, or model
  use was observed;
- browser PID 63205 remained ready. Its tab count advanced from 18 to 19
  because the adapter opened the one fresh recovery target; no browser or tab
  was closed;
- `daily-default` remained enabled/ready at 86,400 seconds and SQLite
  `quick_check` remained `ok`.

Subagent status and reconciliation:

- none; the primary ran and adjudicated the serialized live packet.

Authority classification:

- `inherited_authority`; the single tick was the already-authorized manual
  proof. No retry or new provider effect was consumed after failure.

Graphiti write status:

- deferred to the durable Plan 0030 successor commit so the superseding
  evidence can use the canonical `last30days_skill_main` group.

Next action:

- execute Plan 0030's offline item-bound and typed worker-receipt repair. Any
  future live proof remains manual, requires a fresh 60-minute gap, and cannot
  retry this 0.3.30 tick.
