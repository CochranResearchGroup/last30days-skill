# Plan 0041 | Facebook Cross-Source Browser Handoff Repair

State: OPEN
Roadmap: P17
Plan version: 3
Date: 2026-08-10
Predecessor: Plan 0040 version 3/checkpoint P0040-C03

## Objective

Repair the recurring tick's X-to-Facebook handoff so a late-completing
service-owned browser operation can reconcile to the one healthy retained
authenticated social browser instead of being recorded as a false acquisition
failure at the bounded CLI wait deadline.

## Current State

- local `main == origin/main` is clean at
  `a4c4c85ca05bab3d11ab87c59dd72915c4b84816`;
- installed Last30days service 0.3.44/schema 16 and MCP 4.0.3 are compatible;
- daily tick `tick-7a0a3d6b44a3434b4c86029bf0dec69b` promoted
  snapshot `tick-snapshot-70fa340dc27534602b3cf50e0ac5c8d2` as
  `complete_degraded`: X succeeded, then Facebook attempt
  `provider-attempt-336afefbb53621e83cf9ee6448ebabfa` failed after a
  39.676-second `remote-view` operation with `agent_browser_error`, zero page
  signals, and zero candidates;
- the retained browser remained healthy and later exposed the expected
  authenticated Facebook search target, so credentials and Facebook page
  usability are not the failure boundary;
- the first red replay disproved the initial alias-rejection hypothesis:
  `_select_target_id` falls back to the retained X tab, so the exact default-
  profile alias path already returns that owner. The actual unhandled seam is
  a failed `remote-view` CLI waiter whose service-owned job has made a ready
  browser visible by the next status read;
- before the repair, `acquire_workspace` gave the remote-view waiter the whole
  cumulative run budget and unconditionally re-raised its generic error. It
  had no time or code path for one read-only late-status reconciliation;
- the focused repair now reserves ten seconds, performs at most one status
  read after only `agent_browser_error` or `agent_browser_timeout`, and accepts
  only an already-ready exact selected-profile owner or the existing narrow
  alias. It never retries or relaunches the browser;
- the service candidate is versioned 0.3.45 with canonical runtime-manifest
  SHA-256 `2cb15a6ea92fae932e0d657fbc27444219eff867b9ca52feac35ba25f8bcacf8`.
  The complete Python suite, Go test/vet, compilation, contract generation,
  release packaging, authority audit, and patch hygiene pass. Installation and
  the one Facebook acceptance effect remain unconsumed;
- current no-launch service and access-plan readbacks show one healthy
  `last30days-facebook` browser and recommend `reuse_existing_browser` with no
  manual action. No profile, browser, tab, lock, schedule, or database mutation
  has occurred during diagnosis.

## Scope

- add one deterministic red regression reproducing a failed remote-view waiter
  followed by an exact ready retained browser in service status;
- preserve a ten-second adapter reserve for one read-only late-status
  reconciliation and accept only a ready exact-profile or existing narrow
  alias owner;
- preserve ambiguity, unhealthy browser, missing CDP, wrong-profile, and
  unrelated-session rejection behavior;
- validate the focused adapter and acquisition-worker surfaces, then widen to
  the repo's applicable candidate gates;
- if shipped service code changes, version, commit, push, install once, and run
  at most one Facebook-only acceptance tick through the retained profile;
- reconcile cache/query evidence, databases, schedule, browser/profile state,
  Git, planning authority, and Graphiti closeout.

## Non-Goals

- no credential, login, reauthentication, CAPTCHA, checkpoint, profile reset,
  browser close, tab cleanup, schedule, notification, paid-provider, ranking,
  or database-schema change;
- no agent-browser repository or installed agent-browser mutation;
- no duplicate profile lane, source fallback, unrelated source acquisition,
  historical tick rewrite, tag, GitHub release, or pull request;
- no second Facebook acceptance attempt after any terminal auth, challenge,
  rate-limit, ownership, integrity, deadline, or content failure.

## Acceptance Criteria

1. A focused regression fails before the repair by re-raising the remote-view
   error even though the next service status contains an exact ready retained
   browser.
2. The smallest adapter change preserves a ten-second reconciliation reserve,
   performs no launch retry, and accepts only an exact ready owner; existing
   alias, ambiguity, wrong-profile, and auth safety tests remain green.
3. Focused Facebook/config/worker tests and all applicable Python, Go,
   generation, compile, formatting, release-lock, planning, goal, authority,
   and diff gates pass before installation.
4. Any changed shipped service artifact has a converged version, manifest,
   changelog/configuration contract, commit, and pushed source identity before
   one supported installation.
5. Fresh no-launch preflight selects the retained authenticated profile with
   one reusable browser, no conflict, no manual action, and no duplicate lane.
6. At most one Facebook-only tick reaches a terminal receipt. Success requires
   browser reuse, authenticated page inspection, durable accepted evidence,
   promoted Facebook success, and cache-only named-profile retrieval; failure
   retains the exact terminal cause without retry.
7. Current and rollback databases pass integrity checks, the daily schedule is
   unchanged, the retained browser/profile remains safe, and local
   `main == origin/main` is clean at closeout.

## Definition Of Done

- criteria 1-7 have exact red/green, candidate, installed-runtime, tick,
  cache, integrity, schedule, browser, Git, and memory evidence; or the plan
  closes at a newly proven external/human gate without consuming a retry;
- P17 and this plan close only after the one-attempt boundary has a terminal
  disposition and all safe closeout checks are reconciled.

## Execution Bounds And Gates

- maximum work-unit attempts: 2; maximum review/rework cycles: 1; maximum
  consecutive hardening-only checkpoints: 2;
- one serialized critical path, no subagent, and one red/green behavior slice
  at a time;
- one service installation only if shipped service code changes, and at most
  one Facebook-only acceptance tick after every deterministic gate passes;
- stop without retry on login, checkpoint, CAPTCHA, rate limit, ambiguous
  owner, wrong profile, unsafe route, external-repo defect, deadline/budget
  exhaustion, provider fallback, database integrity failure, or a need for a
  second Facebook attempt.

## Ranked Initial Hypotheses

1. **Confirmed repair seam:** a failed remote-view CLI waiter is re-raised even
   when the service-owned operation leaves the exact selected-profile browser
   ready; the waiter is also allowed to consume the whole adapter budget.
2. **Disproved:** the exact default-profile alias rejects an X-only retained
   owner. The helper currently falls back to the first retained tab and already
   returns that browser.
3. **Rejected:** Facebook credentials or page usability failed; the retained
   authenticated Facebook result page is currently live.
4. **Confirmed bounded strategy:** one read-only status reconciliation can
   accept a late exact ready browser without a second request, launch, or
   profile lane.

## Work Graph

| Packet | Outcome | Depends on | Gate |
|---|---|---|---|
| B01 red replay | Failed waiter plus late exact ready browser fails deterministically | C01 | focused failing test |
| B02 repair | Ten-second reserve and one exact-owner status reconciliation | B01 | focused red/green |
| B03 candidate | Broad validation and release/install decision | B02 | complete pre-effect gate |
| B04 acceptance | At most one Facebook-only terminal tick and cache proof | B03 | fresh no-launch preflight |
| B05 closeout | Runtime/Git/authority/Graphiti reconciliation | B04 | clean deterministic audits |

## Validation Plan

- focused `tests/test_facebook.py` regression plus existing alias, ambiguity,
  wrong-profile, and first-site-tab tests;
- focused service acquisition-worker tests and applicable complete repository
  candidate gates;
- pre/post installed identity, access plan, browser status, provider attempt,
  snapshot/source rows, cache-only query, database integrity, daily schedule,
  Git ancestry, and worktree readbacks.

### Checkpoint P0041-C01 | 2026-08-10

Plan version: 1

State transition:

- `daily_facebook_transient_failure -> bounded_cross_source_handoff_repair`.

Progress classification:

- `outcome_progress`; the generic browser error is narrowed to one testable
  adapter invariant without touching the authenticated profile or consuming a
  new source attempt.

Validation evidence:

- current repository is clean and aligned at `a4c4c85`;
- the failed Facebook attempt contains one 39.676-second remote-view failure,
  zero page signals, and zero candidates immediately after a successful X
  attempt;
- current retained service state has one ready CDP browser and live X,
  Facebook, and LinkedIn targets; fresh Facebook access planning recommends
  exact browser reuse with no manual action;
- CodeGraph source and existing tests show the alias helper requires a target-
  service tab even though later auth inspection already creates a missing
  Facebook tab for a shared owner.

Subagent status and reconciliation:

- `not_spawned`; the user did not request delegation and this is one serialized
  browser/profile critical path.

Authority classification:

- `inherited_authority`; the active goal `repair the tick` covers bounded
  implementation, validation, one required service installation, and one
  Facebook-only acceptance proof inside the existing profile and source lane.

Review disposition summary:

- `blocking=1` cross-source owner reuse defect; `needs_evidence=3` red proof,
  candidate validation, installed live acceptance; `rejected=1` Facebook auth
  or page failure; `nonblocking_backlog=1` generic late-completion resilience.

Graphiti write status:

- discovery completed in `last30days_skill_main`; one compact write is pending
  a validated repair or terminal outcome.

Next action:

- add and run the focused red regression without launching or changing any
  browser.

### Checkpoint P0041-C02 | 2026-08-10

Plan version: 2

State transition:

- `bounded_cross_source_handoff_repair -> source_candidate_validated`.

Progress classification:

- `outcome_progress`; the first hypothesis was falsified, a narrower observable
  failure seam was reproduced red, and the repair now passes the focused
  adapter/config/worker suite without a browser effect.

Validation evidence:

- the initial X-only alias fixture returned the retained browser before any
  remote-view call, disproving target absence as the launch cause;
- the replacement regression failed by re-raising
  `service_state_lock_timeout` despite a next status response containing the
  exact ready `last30days-facebook` browser;
- after the change, the regression passes and proves a 30-second waiter inside
  a 40-second run, one ten-second status reconciliation, four total adapter
  calls, the exact browser/session/target identity, and no launch retry;
- `tests/test_facebook.py`, `tests/test_agent_browser_config.py`, and
  `tests/test_service_acquisition_worker.py` pass with one expected skip.

Subagent status and reconciliation:

- `not_spawned`; implementation and validation remained on the serialized
  browser/profile path.

Authority classification:

- `inherited_authority`; the source repair remains inside the approved goal,
  profile, source, and one-attempt envelope.

Review disposition summary:

- `blocking=1` installed false-failure seam now repaired in source;
  `needs_evidence=2` broad candidate and installed live acceptance;
  `rejected=2` credentials/page failure and target-absence alias rejection;
  `nonblocking_backlog=0`.

Graphiti write status:

- pending the terminal installed outcome; repository evidence remains the
  current authority.

Next action:

- version the shipped service candidate, refresh its manifest, and run the
  complete pre-install gate.

### Checkpoint P0041-C03 | 2026-08-10

Plan version: 3

State transition:

- `source_candidate_validated -> install_ready_candidate`.

Progress classification:

- `outcome_progress`; the shipped service candidate is versioned, packaged,
  and passes every deterministic pre-install gate after one bounded remediation
  of full-suite findings.

Validation evidence:

- service 0.3.45 runtime manifest SHA-256 is
  `2cb15a6ea92fae932e0d657fbc27444219eff867b9ca52feac35ba25f8bcacf8`;
  reproducible artifact SHA-256 is
  `4cbad60d7582b8e7089628aa93a1186d1e69e93c122e4985d54326db7647a274`;
- the first complete suite exposed two candidate-local regressions: inherited
  Reddit acquisition performed the new status read, and the authority fixture
  still expected zero active plans. Reconciliation was scoped strictly to
  `target_service_id=facebook`, and the fixture now names Plan 0041;
- the final complete Python gate passes with 2,648 tests, seven skips, and six
  passing subtests; Go `test ./...` and `vet ./...`, compileall, contract
  generation, runtime build, authority audit, and `git diff --check` pass;
- the late direct-session path now requires both session and browser profile
  labels to equal the selected profile exactly. Existing broker-authoritative
  shared-owner and narrow default-alias checks remain unchanged.

Subagent status and reconciliation:

- `not_spawned`; the primary agent independently ran and reconciled all gates.

Authority classification:

- `inherited_authority`; one commit/push, supported service upgrade, and one
  Facebook-only terminal acceptance remain inside the active goal envelope.

Review disposition summary:

- `blocking=0`; `needs_evidence=1` installed live acceptance and operational
  closeout; `rejected=2` initial causal hypotheses; `nonblocking_backlog=0`.

Graphiti write status:

- pending terminal installed evidence; no pre-install episode was written.

Next action:

- commit and push the validated 0.3.45 source identity, build the exact commit,
  then perform one supported upgrade and one bounded Facebook-only tick.
