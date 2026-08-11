# Plan 0045 | Facebook Stale Prepared Extraction Refresh

State: CLOSED
Roadmap: P21
Plan version: 2
Date: 2026-08-11
Predecessor: Plan 0044 version 2/checkpoint P0044-C03

## Objective

Honor the configured post-navigation settle wait by refreshing a prepared
Facebook query extraction when its immediate combined capture is empty, then
prove one installed Facebook-only tick can publish accepted durable evidence
and serve it from the exact named-profile cache.

## Current State

- service 0.3.46/schema 16, current and rollback databases, recurring schedule,
  retained browser PID 13177, profile, and installed agent-browser candidate
  remain ready and converged;
- Plan 0044's one tick is terminal and will not be retried. Navigation and the
  immediate combined evaluation succeeded, then an unnecessary scroll stalled
  the Facebook target and produced zero items;
- replacement-target recovery evaluates auth, page, and extraction immediately
  after navigation and stores the combined capture. `FacebookScraper.search()`
  then sleeps `initial_wait`, but `_extract()` reuses even an empty prepared
  extraction instead of performing a fresh DOM read after that wait;
- non-empty prepared extraction remains a valuable single-read fast path and
  must be preserved.

## Scope

- add one deterministic regression in `tests/test_facebook.py` proving an empty
  prepared capture is refreshed after `initial_wait` before any scroll;
- change only the prepared-extraction selection rule so non-empty captures stay
  reusable and empty captures fall through to current `EXTRACT_SCRIPT`;
- preserve authentication, navigation, extraction, quality, budgets, browser
  cleanup, selector-targeted scrolling, and recurring schedule contracts;
- run focused tests, full source validation, commit and push the Last30Days
  change, build/install one service candidate through repository policy, and
  verify exact version/runtime provenance;
- after fresh service/database/schedule/profile preflight, consume at most one
  new Facebook-only tick and require named-profile cache evidence for success.

## Non-Goals

- no agent-browser source change or reinstall, scroll transport variant,
  browser restart/close, profile reset, login, reauthentication, CAPTCHA,
  checkpoint, route mutation, schedule mutation, source expansion, fallback,
  model use, paid request, or retry of Plan 0044's tick;
- no changes to non-empty prepared capture reuse or general extraction scripts.

## Acceptance Criteria

1. The new regression is red because the current empty prepared capture forces
   scroll without a post-wait DOM read.
2. After the repair, empty prepared extraction triggers exactly one current DOM
   read before scroll, while non-empty prepared extraction still avoids later
   target commands.
3. Focused Facebook, service worker/tick, plan audit, full pytest, packaging,
   build, and installer gates pass as required by repository policy.
4. One exact committed/pushed candidate installs as a new service version with
   matching runtime/contract manifests; databases, schedule, profile, and
   browser identity remain safe.
5. One new Facebook-only tick reaches terminal success with accepted durable
   evidence, and MCP `cache_only` with explicit
   `profile_id=last30days-facebook` returns that evidence.
6. Exact tick/provider/snapshot/browser-operation receipts and both repository
   states are reconciled without touching unrelated work.

## Execution Bounds And Gates

- one red/green implementation pass, at most one focused rework, one service
  release/install candidate, and one Facebook tick;
- no provider operation before source gates, exact commit/push, installation,
  and fresh preflight pass;
- stop without retry on validation failure, browser/profile identity drift,
  auth/challenge/rate evidence, integrity failure, terminal tick failure, or any
  effect outside this plan;
- no subagents under the current orchestration restriction.

## Work Graph

| Packet | Outcome | Depends on | Gate |
|---|---|---|---|
| F01 repro | Empty prepared capture forces scroll | C01 | exact unit red |
| F02 repair | Empty capture falls through to fresh DOM read | F01 | focused green |
| F03 candidate | Exact committed/pushed Last30Days release candidate | F02 | full source gates |
| F04 install | Installed service/runtime convergence | F03 | DB/schedule/profile proof |
| F05 acceptance | One terminal tick plus named cache proof | F04 | no retry |
| F06 closeout | Repos/runtime/receipts reconcile | F05 | current evidence |

### Checkpoint P0045-C01 | 2026-08-11

Plan version: 1

State transition:

- `terminal_upstream_stale_capture_failure -> stale_prepared_extraction_identified`.

Progress classification:

- `blocker_reduction`; the scroll is now explained by one stale-read decision
  in Last30Days rather than another browser transport hypothesis.

Validation evidence:

- live operation ordering shows navigate success, combined evaluate success,
  four-second settle, then scroll with no intervening current DOM extraction;
- current source stores the immediate combined extraction during replacement
  auth recovery and `_extract()` uses every prepared dict, including
  `{"candidates": []}`, before considering `self.client.evaluate()`;
- non-empty prepared capture coverage already exists and remains a required
  compatibility gate.

Subagent status and reconciliation:

- `not_spawned`; current orchestration policy prohibits delegation.

Authority classification:

- `inherited_authority`; this bounded successor stays inside the active goal
  and the same source/profile/data/schedule/effect envelope.

Review disposition summary:

- `blocking=1` stale empty prepared extraction; `needs_evidence=3` red/green,
  installed convergence, live acceptance; `rejected=1` another browser
  transport repair; `nonblocking_backlog=0`.

Graphiti write status:

- deferred until terminal validated evidence.

Next action:

- add the exact empty-prepared-capture regression red, preserve the non-empty
  fast path, and implement only the prepared-selection rule.

### Checkpoint P0045-C02 | 2026-08-11

Plan version: 1

State transition:

- `stale_prepared_extraction_identified -> focused_source_candidate_green`.

Progress classification:

- `blocker_reduction`; an empty immediate prepared capture now falls through to
  one current DOM extraction after the configured settle wait, while non-empty
  and rate-limit captures retain the existing single-read path.

Validation evidence:

- the new regression failed exactly because current code tried to scroll before
  a fresh extraction; it now passes and proves exactly one fresh
  `EXTRACT_SCRIPT` read before scroll consideration;
- the existing non-empty prepared-capture test still proves no later target
  command is issued;
- all Facebook tests pass with one expected skip; the expanded Facebook,
  acquisition-worker, tick-runtime, release, runtime-package, and authority
  selection passes, and the authority audit reports exactly Plan 0045/P21 open;
- service source, changelog, configuration, release assertions, and canonical
  runtime manifest converge at 0.3.47. Runtime manifest SHA-256 is
  `7babaa9ac9045def3826e9bd4563cd94e2806838fcb9b17a567c668342125243`.

Subagent status and reconciliation:

- `not_spawned`; current orchestration policy prohibits delegation.

Authority classification:

- `inherited_authority`; only the intended source/release candidate changed and
  no install or browser/provider effect occurred.

Review disposition summary:

- `blocking=0` at the focused source seam; `needs_evidence=3` complete source
  gate, exact install, live acceptance; `rejected=0`;
  `nonblocking_backlog=0`.

Graphiti write status:

- deferred until terminal installed/downstream evidence.

Next action:

- run the complete pre-install validation and build the reproducible 0.3.47
  artifact; do not install unless every required gate passes.

### Checkpoint P0045-C03 | 2026-08-11

Plan version: 1

State transition:

- `focused_source_candidate_green -> install_ready_candidate`.

Progress classification:

- `outcome_progress`; all required source, package, governance, and
  reproducibility gates pass for the bounded 0.3.47 candidate.

Validation evidence:

- full Python gate completed exit 0 across 2,657 collected tests with seven
  expected skips; Go `test ./...` and `vet ./...` pass;
- Python compileall, generated-contract freshness, exact plan authority audit,
  installable Skill artifact build, runtime package tests, and patch hygiene
  pass;
- runtime manifest SHA-256 is
  `7babaa9ac9045def3826e9bd4563cd94e2806838fcb9b17a567c668342125243`;
- two consecutive runtime builds produced exact artifact SHA-256
  `7bf1fe1285caf6ae9727f4a9da8460b19d351298a1009363d999fa96b76ba106`.

Subagent status and reconciliation:

- `not_spawned`; current orchestration policy prohibits delegation.

Authority classification:

- `inherited_authority`; all work remains source/package-only and no install or
  provider effect occurred in this checkpoint.

Review disposition summary:

- `blocking=0` at source/package seams; `needs_evidence=2` exact committed and
  installed convergence plus one live acceptance tick; `rejected=0`;
  `nonblocking_backlog=0`.

Graphiti write status:

- deferred until terminal installed/downstream evidence.

Next action:

- commit and push the exact 0.3.47 candidate, rebuild from that commit, then run
  fresh install preflight and perform the one transactional upgrade.

### Checkpoint P0045-C04 | 2026-08-11

Plan version: 1

State transition:

- `install_ready_candidate -> installed_acceptance_ready`.

Progress classification:

- `outcome_progress`; exact pushed source is installed as service 0.3.47 and
  every gate for the sole downstream acceptance tick is ready.

Validation evidence:

- exact commit `6ed4b784473b9d2af4d3b153055179183af4ed80` is pushed to
  `origin/main`; its clean rebuild retained artifact SHA-256
  `7bf1fe1285caf6ae9727f4a9da8460b19d351298a1009363d999fa96b76ba106`;
- transactional upgrade installed `releases/0.3.47`, retained 0.3.46 as
  previous, and reports ready/compatible with MCP 4.0.3 at schema 16, runtime
  manifest `7babaa9ac9045def3826e9bd4563cd94e2806838fcb9b17a567c668342125243`,
  and canonical contract
  `fe8727fbe0d4e2f6775f49a6fc958369fe4877ba812bae4ef69121b88f12e2f1`;
- current and 0.3.46 rollback databases return `ok`; schedule `daily-default`
  remains enabled/ready with next boundary `2026-08-12T00:00:00Z`;
- Facebook browser PID 13177, exact endpoint, profile readiness, and acquisition
  readiness remain unchanged;
- preflight for schedule receipt `plan-0045-stale-capture-refresh` is `ready`
  with one attempt, zero cost/model, three-item, 50-request, and 120-second
  limits.

Subagent status and reconciliation:

- `not_spawned`; current orchestration policy prohibits delegation.

Authority classification:

- `inherited_authority`; exact installation and the remaining one Facebook tick
  are the bounded effects explicitly admitted by this plan.

Review disposition summary:

- `blocking=0` through installed preflight; `needs_evidence=1` terminal tick
  with accepted evidence and named-profile cache proof; `rejected=0`;
  `nonblocking_backlog=0`.

Graphiti write status:

- deferred until terminal downstream evidence.

Next action:

- consume the one Facebook-only tick for the closed interval. Stop without
  retry on any terminal failure; on success, run only the named-profile
  cache-only proof and final reconciliation.

## Definition Of Done

- criteria 1-6 have current test, commit, installed-runtime, tick, cache, and
  state-reconciliation evidence; test volume or installation alone is not
  completion.

### Checkpoint P0045-C05 | 2026-08-11

Plan version: 2

State transition:

- `installed_acceptance_ready -> terminal_live_acceptance_failure`.

Progress classification:

- `no_progress`; the installed stale-capture repair is valid at its focused
  source seam, but the sole live tick reached the same retained Facebook CDP
  input failure already observed by the two preceding bounded packets and
  published no evidence.

Validation evidence:

- sole tick `tick-3b374c8eaa1811b8d3eec1bdcec51d37`, execution
  `tick-attempt-4510a301db983aee77b148cecbf743bf`, provider attempt
  `provider-attempt-99c0a0b7cd72cd4ce35803c0a7521686`, and snapshot
  `tick-snapshot-c5a79d397edba1d170153d43efd90234` completed degraded with
  one attempt, one request, 46 wall seconds, and zero observed, accepted, or
  rejected items;
- retained provider diagnostics report replacement `open` success in 6.543
  seconds and `eval` success in 0.666 seconds, followed by selectorless
  `scroll` timing out after 30.042 seconds with safe code
  `agent_browser_timeout`;
- the tick was not retried and named-profile cache acceptance was correctly
  skipped because no durable evidence exists;
- direct diagnosis proved the browser endpoint and tab inventory remained
  reachable, but the Facebook target did not answer raw CDP evaluation. A
  supported daemon handoff preserved browser PID 13177 and the exact endpoint,
  yet a fresh disposable same-profile Facebook target also timed out on target
  selection and evaluation;
- only the failed tick target and disposable diagnostic target were closed.
  A final supported handoff retained PID 13177, the exact endpoint and three
  unrelated targets; the active preview target then evaluated successfully,
  isolating the remaining failure to Facebook target control rather than the
  browser-wide CDP endpoint or profile lease.

Subagent status and reconciliation:

- `not_spawned`; current orchestration policy prohibits delegation.

Authority classification:

- `human_gate`; the same Facebook CDP input/target-control invariant has now
  failed the Plan 0110 live scroll proof and the sole Plan 0044 and Plan 0045
  ticks. Continuing would cross the configured repeated-no-progress bound and
  require a browser restart, alternate browser build, or another materially
  changed runtime strategy.

Review disposition summary:

- `blocking=1` retained Facebook targets become uncontrollable on the current
  Chromium/CDP path; `needs_evidence=1` accepted installed tick plus named
  cache proof; `rejected=1` another blind tick or scroll transport retry;
  `nonblocking_backlog=0`.

Graphiti write status:

- compact closeout memory queued as job
  `2f581f90-1395-47a7-b020-e1e67c42648e` in
  `last30days_skill_main`; queued status is not persistence proof, so repository
  and installed receipts remain authoritative.

Stop reason:

- Plan 0045/P21 closes with acceptance criterion 5 unmet. Do not enqueue
  another Facebook tick or restart/replace the authenticated browser without
  explicit authority for the changed runtime strategy.
