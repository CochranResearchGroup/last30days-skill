# Plan 0025 | Facebook agent-browser timeout remediation

State: OPEN
Roadmap: P09
Plan version: 13
Date: 2026-08-07

## Objective

Diagnose the exact retained-browser command that causes Facebook collection to
time out before page readback, implement the narrowest source-owned mitigation,
and prove the repaired Facebook lane live without changing the accepted daily
schedule, source set, credentials, cost posture, or browser identity boundary.

## Current State

- Installed service 0.3.10/schema16 is ready and the service-owned
  `daily-default` schedule remains enabled/ready for the Aug 8 UTC boundary.
- The inactive-target repair and extraction retry repair are validated. The
  first live proof reached Facebook and accepted one post; the second proved a
  narrower active-but-stale target failure after auth and navigation.
- S07 work `p0025-facebook-live-20260807-05` removed cleanup from the critical
  path and authenticated on a fresh target, but direct creation of a query tab
  again timed out at its first page-state evaluation after 30.039 seconds.
- This repeats C04's post-query evaluation invariant at the configured bound.
  Further live work is human-gated. Offline S08 now supplies exact service
  0.3.11, using the only live-proven path that reached extraction: create and
  evaluate a fresh home target for auth, then navigate that same known-healthy
  target to the query. The candidate is built and validated but not installed.
- Plan version 4's `human_gate` classification is superseded by C05 after a
  current policy reread: renewable work windows are not consumable approval
  tokens when blocker reduction is proven and the approved envelope is
  unchanged.

## Scope

- capture operation-level timing for the exact acquisition/auth/navigation
  path without exposing credentials or page content;
- add a deterministic regression at the real adapter seam before changing the
  implementation;
- repair only the Facebook/shared agent-browser command behavior that current
  evidence proves faulty;
- preserve the installed 0.3.10 service while building one reviewed offline
  0.3.11 candidate;
- prepare one offline S08 regression-backed candidate; do not install it or run
  another Facebook proof without explicit operator authority after the repeated
  post-query evaluation invariant;
- preserve and verify daily schedule, disabled legacy specs, database
  integrity, browser/profile reuse, zero cost/model use, and next-boundary
  continuity.

## Non-Goals

- no new source, provider, credential, account, profile, browser process, route,
  cadence, notification, retry fanout, schema, or acquisition architecture;
- no Facebook authentication, checkpoint, or manual operator interaction;
- no repair of unrelated agent-browser retained state or installation drift;
- no change to relevance, timestamp, permalink, or publication quality gates
  unless the timeout diagnosis proves one is directly involved;
- no broad source-suite redesign or reopening of P08/Plan 0024.

## Authority And Gates

- The active user goal, `diagnose, plan a mitigation, execute`, remains standing
  authority for ordinary offline diagnosis, code/test/docs changes, and
  deterministic candidate preparation inside this existing source boundary.
- C11 classifies another installation or live Facebook proof as a `human_gate`
  after the repeated post-query evaluation invariant. Exact 0.3.11 may not be
  installed and no Facebook command may run without explicit operator
  authority.
- Stop before any login, checkpoint, consent, challenge, new credential,
  duplicate browser/profile lane, destructive cleanup, paid request, external
  communication, or change to the daily schedule.
- Preserve fail-closed provider results. A timeout becoming an auth, challenge,
  integrity, or quality-gate failure is not a successful repair.

## Acceptance Criteria

1. One operation-level reproducer identifies the exact timed-out command or
   proves a specific timeout-budget interaction with current evidence.
2. A regression test at the `CliAgentBrowserClient`/`FacebookScraper` seam goes
   red on the reproduced pattern and green after the mitigation.
3. The mitigation reuses the canonical retained profile/browser and does not
   open a duplicate profile lane or weaken auth/page/quality validation.
4. Focused Facebook, worker, provider, config, and source-log tests pass; wider
   validation is proportional to the touched runtime surface.
5. The terminal bounded live Facebook proof returns verified search-page
   navigation plus DOM candidate/item evidence, does not return
   `agent_browser_timeout` or exhaust the worker wall budget, and any accepted
   items still pass the existing quality gate.
6. Installed service readback, schedule identity/cadence/next boundary,
   database integrity, disabled legacy specs, zero cost/model use, and absence
   of a last30days systemd timer remain unchanged except for the reviewed
   service version when installation is required.
7. ROADMAP, RUNBOOK, plan state, receipt, commit, origin state, and compact
   Graphiti memory agree on the terminal outcome or exact remaining blocker.

## Execution Graph And Bounds

| Packet | Outcome | Depends on | Write surface | Terminal condition |
| --- | --- | --- | --- | --- |
| S01 diagnose | Exact timed command and falsified alternatives | current runtime and DB | plan/runbook plus optional sanitized diagnostic artifact | one ranked hypothesis is proven |
| S02 test and fix | Red regression then narrow green mitigation | S01 | Facebook adapter/tests and config docs only if a knob changes | focused suite passes |
| S03 candidate | Reviewed build/install with rollback retained | S02 | version/release artifacts and installed user service | installed readback matches candidate |
| S04 live proof | One bounded Facebook attempt and invariant readback | S03 | governed runtime evidence only | acceptance passes or hard stop |
| S05 closeout | Terminal authorities, receipt, memory, commit/push | S04 | plan/roadmap/runbook/notes/Graphiti | exact readbacks agree |
| S06 fresh targets | Fresh auth/query targets and one live proof | C04 blocker | Facebook adapter/tests/version plus governed runtime evidence | C08 cleanup blocker recorded |
| S07 deferred cleanup | Page evidence before bounded best-effort consolidation | C08 blocker | Facebook adapter/tests/version plus governed runtime evidence | success closes P09; cleanup cannot mask result |
| S08 same-target navigation | Fresh auth target then same-target query navigation | C11 repeated invariant | offline Facebook adapter/tests/version only | candidate ready; install/live remain human-gated |

- Critical-path owner: primary agent; active-agent concurrency is one and no
  subagent is authorized or needed.
- S08 offline maximum implementation attempts: 1.
- S08 offline maximum review/rework cycles: 1.
- S08 live Facebook source attempts: 0 until explicit operator authority.
- Maximum diagnostic browser interaction: one tab-select/auth-read sequence,
  restoring the prior active tab when safe.
- The repeated post-query evaluation timeout is a `human_gate`; no install that
  would affect the scheduled source lane and no live Facebook command may run
  until explicit operator authority.

## Validation Commands

```bash
uv run pytest tests/test_facebook.py
uv run pytest tests/test_service_worker.py tests/test_service_tick_runner.py
uv run pytest tests/test_source_log_visibility.py
python3 -m compileall -q skills/last30days/scripts/lib
python3 skills/last30days/scripts/service.py status
python3 skills/last30days/scripts/service.py tick schedule status
sqlite3 /home/ecochran76/.local/share/last30days/research.db 'PRAGMA integrity_check;'
```

## Definition Of Done

Plan 0025 closes only when every acceptance criterion has current evidence,
the one bounded live proof no longer returns `agent_browser_timeout`, all P08
schedule and safety invariants remain intact, terminal authorities agree, the
validated slice is committed and pushed to `origin/main`, and one compact
Graphiti episode passes exact readback. A truthful hard stop remains `OPEN`
with the blocker recorded; it is not completion.

### Checkpoint P0025-C01 | 2026-08-07

Plan version: 1

State transition:

- `p08_steady_state_facebook_gap -> facebook_timeout_diagnosis_active`.

Progress classification:

- `outcome_progress`; the repeated transient gap now has a red-capable live
  assertion, ranked falsifiable hypotheses, explicit bounds, and a governed
  remediation path.

Evidence:

- clean `main` at `21ba32d`, matching `origin/main`;
- installed service 0.3.5/schema16 ready; daily schedule enabled/ready for Aug
  8 with no runtime error;
- latest Facebook result `agent_browser_timeout`, 38 wall seconds, zero page
  signals, no rendered page; the fast assertion exits 1;
- retained browser/profile viable and read-only tab inventory succeeds in
  about eight seconds;
- Graphiti discovery returned Plan 0023/0024 and earlier Facebook route history
  as advisory context; current repo/runtime/SQLite evidence is authoritative.

Authority classification:

- `inherited_authority`; the user explicitly authorized diagnosis, mitigation
  planning, and execution within the existing Facebook lane.

Next action:

- time the single bounded tab-select/auth-read sequence, identify the exact
  stall, then add a red regression before implementing the mitigation.

### Checkpoint P0025-C02 | 2026-08-07

Plan version: 2

State transition:

- `facebook_timeout_diagnosis_active -> exact_candidate_ready_for_install`.

Progress classification:

- `outcome_progress`; the exact target-level failure is proven, a regression
  went red, the narrow mitigation is implemented, and the reviewed 0.3.6
  artifact passes focused validation.

Diagnosis:

- a 30-second reproduction selected the inactive retained Facebook tab but did
  not return; evaluation on that target also did not return within the cap;
- the changed-budget probe returned after 35.44 seconds with
  `CDP command timed out: Page.enable`;
- restoring the retained LinkedIn tab succeeded in about eight seconds, while
  service status, tab enumeration, profile selection, and remote-view runtime
  remained ready;
- therefore the failure is the stale inactive Facebook target, with the
  adapter's 30-second clamp masking agent-browser's eventual Page-domain error.

Implementation:

- Facebook auth inspection now reuses a site target only when Facebook is
  already active; otherwise it opens a fresh target inside the same retained
  browser/profile, re-enumerates, consolidates same-site duplicates, and then
  evaluates auth state;
- the shared helper retains its previous default for X, LinkedIn, Reddit, and
  other callers; no browser, profile, route, credential, schema, cadence,
  retry, cost, or quality-gate behavior changes;
- service version advances 0.3.5 to 0.3.6 and the runtime manifest,
  configuration example, changelog, and release assertions agree.

Validation evidence:

- exact new regression first failed and then passed;
- focused Facebook/LinkedIn/X/Reddit/source-log/release/runtime-package/worker/
  tick validation passes 179 tests with three skips;
- compileall, plan-authority audit, manifest/build verification, and diff check
  pass;
- deterministic artifact
  `dist/service/last30days-service-0.3.6.tar.gz` has SHA-256
  `96d0f916ff1a2492090a2d4bbf6e1bb15ca0f7d944ea7c5ff5245d8604b532b1`;
- receipt 0086 records the diagnosis, candidate, validation, and zero live
  source/install effects.

Authority classification:

- `inherited_authority`; exact candidate install, rollback preservation, and
  the one bounded Facebook proof remain inside the approved goal and plan.

Next action:

- commit the exact candidate, install 0.3.6 with 0.3.5 rollback retained, prove
  installed hashes/readiness, then consume the one live Facebook attempt.

### Checkpoint P0025-C03 | 2026-08-07

Plan version: 3

State transition:

- `exact_candidate_ready_for_install -> live_blocker_reduced_performance_rework_active`.

Progress classification:

- `blocker_reduction`; installed service 0.3.6 eliminated the original stale-
  target `Page.enable` timeout and returned a quality-gated Facebook item, but
  redundant extraction retries exhausted the worker's 120-second wall budget.

Evidence:

- installed 0.3.6 is ready on schema 16 with 0.3.5 retained for rollback;
- live work `p0025-facebook-live-20260807-01` reused the canonical retained
  browser/profile, opened and consolidated one fresh Facebook target,
  authenticated, reached the requested Recent-post search URL, observed 17
  candidates, and accepted one item;
- the result no longer reports `agent_browser_timeout`; it terminalized
  `partial` with `wall_time_budget_exhausted` after 120.923 seconds, one
  network action, zero cost/model use, and no duplicate Facebook tab;
- source inspection shows `_extract` retries the paired snapshot/evaluate up to
  three times whenever an undated action card remains, even when another
  extracted post already has a valid timestamp.

Changed assumption and renewed bound:

- replacing the stale target was necessary but not sufficient for a terminal
  in-budget result; the one permitted review/rework cycle is now active;
- the cumulative live-attempt bound advances from one to two, with attempt 1
  consumed and exactly one successor permitted only after a red regression and
  offline validation; all other effect, identity, cost, and schedule bounds
  remain unchanged.

Authority classification:

- `inherited_authority`; the regression-backed performance repair, successor
  candidate install, and final bounded proof remain inside the user's active
  diagnosis/mitigation/execution goal and do not add a source, identity, cost,
  credential, cadence, or retry-fanout effect.

Next action:

- prove the mixed dated-post/undated-action-card retry defect red, stop retrying
  once any extracted candidate has a parseable timestamp, publish the exact
  successor candidate, then consume the final bounded live proof.

### Checkpoint P0025-C04 | 2026-08-07

Plan version: 4

State transition:

- `live_blocker_reduced_performance_rework_active -> execution_window_exhausted_navigation_target_blocked`.

Progress classification:

- `blocked_after_blocker_reduction`; service 0.3.7 is installed and its
  extraction retry fix is validated, but the final permitted live proof found
  a distinct post-navigation stale-target timeout and did not satisfy live
  acceptance.

Evidence:

- installed 0.3.7/schema16 is ready; its runtime-manifest digest is
  `576312fbe761419368dee7c8f0a67f9c1af6be032d5281039984a0139a893b15`;
- final work `p0025-facebook-live-20260807-02` reused the canonical retained
  browser/profile; service planning took 0.227/2.834 seconds, tab selection
  8.394 seconds, and authentication evaluation 8.054 seconds;
- query navigation returned successfully in 16.243 seconds, but the immediate
  page-state evaluation timed out at 30.042 seconds, producing failed/transient
  `agent_browser_timeout`, zero candidates, and zero cost;
- `_navigate` currently calls `prepare_site_tab(... consolidate=True)` and
  chooses `navigate` whenever any active Facebook target exists. The proof
  falsifies the assumption that an active target remains page-domain healthy
  after a prior run.
- compact Graphiti job `ccad7cf1-ea9b-407a-ae95-84c9db741f17` timed out after
  120 seconds during node resolution and returned no episode UUID; receipts
  0087-0088 remain the durable source authority and Graphiti readback is
  pending.

Hard stop and remaining remedy:

- both cumulative live attempts, both implementation attempts, and the one
  review/rework cycle are consumed. No third live read or implementation is
  authorized by this execution window;
- the narrow successor hypothesis is to regression-test an active-but-stale
  retained search target and always create/consolidate a fresh Facebook query
  target after auth, instead of navigating the authenticated retained target;
- Plan 0025 remains `OPEN`. Renewing exactly one implementation attempt and one
  final live proof requires explicit operator direction because it expands the
  frozen cumulative bounds.

Authority classification:

- `human_gate`; diagnosis and current-window execution are complete,
  but expanding the exhausted implementation/live-effect caps is a new
  cumulative authority decision.

Next action:

- preserve installed 0.3.7 and all schedule/identity/cost invariants, complete
  offline and installed-state audit, preserve the Graphiti timeout receipt,
  and wait for explicit authority before the fresh-query-target successor
  attempt.

### Checkpoint P0025-C05 | 2026-08-07

Plan version: 5

State transition:

- `execution_window_exhausted_navigation_target_blocked -> fresh_query_target_successor_ready`.

Progress classification:

- `outcome_progress`; current policy and code evidence turn the exact C04
  blocker into one bounded, red-capable successor inside the approved goal.

Evidence and changed assumption:

- current service 0.3.7/schema16 and `daily-default` schedule are ready; the
  worktree is clean and matches `origin/main` at `bbb9de4`;
- policy 0015 states that a hard stop ends a packet, not standing goal
  authority, and that bounds are renewable windows when blocker reduction is
  proven without changing the approved envelope;
- C04 did not repeat the original inactive-target failure or the extraction
  wall-budget failure. It newly proved that an active authenticated Facebook
  target can become Page-domain stale after query navigation;
- the changed assumption is `active same-site target is safe to navigate` ->
  `auth may use a proven active target, but each query needs a fresh target`.

Successor controller and bounds:

- primary agent owns S06; one implementation attempt, one review/rework cycle,
  and one zero-cost live proof after offline/install validation;
- retain the same browser/profile and open only a fresh tab, consolidate the
  prior Facebook tab, preserve auth/page/quality checks, and stop on login,
  checkpoint, consent, duplicate browser/profile, cost, or same-stage timeout;
- exit success requires terminal in-budget page signal plus quality-gated item
  or truthful empty result and all schedule/database/timer invariants.

Authority classification:

- `inherited_authority`; C04's `human_gate` is superseded because S06 crosses
  no significant-departure boundary and the latest checkpoint showed verified
  blocker reduction rather than repeated no progress.

Next action:

- add and observe red a navigation-seam regression proving an active Facebook
  target must not be reused for a query, then implement fresh-target navigation.

### Checkpoint P0025-C06 | 2026-08-07

Plan version: 6

State transition:

- `fresh_query_target_successor_ready -> fresh_query_target_candidate_ready`.

Progress classification:

- `blocker_reduction`; the exact active-target reuse pattern is regression-
  locked red/green and the deterministic 0.3.8 candidate passes focused and
  cross-source validation without any installed or live effect.

Implementation and evidence:

- the new navigation regression first failed because `_navigate` emitted
  `navigate` when `prepare_site_tab` reported an active Facebook target;
- `_navigate` now always emits `new_tab` for the Recent-post query, waits, then
  requires that fresh target active while consolidating prior same-site tabs
  before page-state evaluation;
- auth inspection remains unchanged and may reuse a proven active target; no
  browser/profile, source, route, credential, quality, schedule, or cost
  behavior changes;
- focused Facebook/cross-source/worker/tick/source-log tests, compileall,
  release/runtime-package tests, authority audit, and diff check pass;
- deterministic artifact `dist/service/last30days-service-0.3.8.tar.gz` has
  SHA-256 `2575b1266a37666fc270a3e5d3fffda64313fc49c933243984bf62f5e887f90c`.

Authority classification:

- `inherited_authority`; candidate commit, install with 0.3.7 rollback, and the
  one S06 live proof remain inside the frozen successor envelope.

Next action:

- commit the exact candidate, install 0.3.8 with rollback retained, verify
  installed hashes/readiness/invariants, then consume the single S06 proof.

### Checkpoint P0025-C07 | 2026-08-07

Plan version: 7

State transition:

- `fresh_query_target_candidate_ready -> collection_target_lifecycle_candidate_ready`.

Progress classification:

- `blocker_reduction`; closed-world review accepted and remediated one critical
  regression before live proof: the prior failed query could leave an active
  but stale target that the next collection would reuse during auth.

Accepted finding and remediation:

- criterion: S06 must remove active-target reuse from the full collection path,
  not only query navigation;
- reproducer: active Facebook target made `inspect_auth` issue `tab list` then
  `eval` instead of `tab new`; the new regression failed on that exact command;
- consequence: a run following C04 could time out during auth before reaching
  the new query-target logic;
- disposition: `blocking`, high confidence, resolved in the one allowed S06
  review/rework cycle;
- auth now unconditionally creates a fresh Facebook home target, requires it
  active, consolidates same-site predecessors, then evaluates auth. Consolidated
  preparation bypasses the site cache so the subsequent fresh query target is
  also enumerated and consolidated rather than falsely accepted from cache.

Validation evidence:

- active-auth-target regression red then green; full Facebook suite passes;
- focused cross-source/worker/tick/source-log suite, compileall, release/runtime-
  package/authority suite, and diff check pass;
- deterministic artifact `dist/service/last30days-service-0.3.9.tar.gz` has
  SHA-256 `2b613e8a60fa66ed0aee7e96608a741c6878cb6a0bdf2fd632f3ea3eaaf0b848`;
- 0.3.8 was installed as an intermediate candidate but received no live proof;
  0.3.7 remains its rollback until exact 0.3.9 installation.

Authority classification:

- `inherited_authority`; this is the one S06 closed-world rework, with the live
  proof still unconsumed and every source/identity/cost/schedule bound unchanged.

Next action:

- commit/install exact 0.3.9 with 0.3.8 rollback retained, verify installed
  readbacks, then consume the single S06 live proof.

### Checkpoint P0025-C08 | 2026-08-07

Plan version: 8

State transition:

- `collection_target_lifecycle_candidate_ready -> synchronous_cleanup_timeout_blocked`.

Progress classification:

- `blocker_reduction`; the S06 live proof eliminated auth and query target
  reuse from the failing path and isolated the remaining timeout to synchronous
  predecessor-tab cleanup before page evidence.

Evidence:

- installed 0.3.9/schema16 ready; rollback 0.3.8 retained; schedule, database,
  disabled-spec, nonterminal-attempt, timer, identity, and zero-cost invariants
  passed before the proof;
- work `p0025-facebook-live-20260807-04` reused the canonical browser/profile,
  authenticated without login/checkpoint, and began `fresh_query_tab` strategy;
- command timings: service 0.264/2.830s; auth `tab new` 9.028s, list 8.470s,
  predecessor close 8.561s, eval 8.332s; query `tab new` 8.372s, list 8.083s;
  query-predecessor close timed out at 30.035s;
- result failed/transient `agent_browser_timeout`, zero candidates, one opaque
  network action, zero cost. No page-state evaluation was attempted.

Authority classification:

- `inherited_authority`; the failed S06 packet is closed and its evidence may
  seed a bounded same-envelope successor under policy 0015.

Next action:

- derive S07 so fresh target verification precedes page evidence without
  synchronous cleanup, then perform bounded best-effort cleanup after extraction.

### Checkpoint P0025-C09 | 2026-08-07

Plan version: 9

State transition:

- `synchronous_cleanup_timeout_blocked -> deferred_cleanup_successor_ready`.

Progress classification:

- `outcome_progress`; S07 has a tight deterministic seam and a bounded remedy
  for the exact cleanup-stage failure without weakening page/auth/item gates.

Changed assumption, controller, and bounds:

- changed assumption: same-site consolidation is not safe on the critical path
  merely because the fresh active target is healthy; closing an inactive
  predecessor can block independently;
- primary agent owns one implementation attempt, one review/rework cycle, and
  one zero-cost live proof after offline/install validation;
- auth/query target verification uses `consolidate=False`; page-state and
  extraction run first; final cleanup re-enumerates, keeps the active query
  target, gives each predecessor close a short bound, records failures, and
  never converts useful page/item evidence into a provider failure;
- stop on auth/checkpoint, page mismatch, quality failure, new browser/profile,
  credential/schedule/cost change, or any new critical-path timeout.

Authority classification:

- `inherited_authority`; S07 changes only cleanup ordering and containment
  inside the same approved Facebook/browser/profile/zero-cost envelope. C08
  showed verified blocker reduction, not repetition of the same invariant.

Next action:

- add regressions proving pre-read consolidation is absent and cleanup timeout
  cannot mask an otherwise valid result, then implement the bounded lifecycle.

### Checkpoint P0025-C10 | 2026-08-07

Plan version: 10

State transition:

- `deferred_cleanup_successor_ready -> deferred_cleanup_candidate_ready`.

Progress classification:

- `blocker_reduction`; the exact cleanup failure is regression-locked and the
  deterministic 0.3.10 candidate removes synchronous close from the critical
  auth/query/page-read path.

Implementation and evidence:

- new regression first failed because cleanup ran only once pre-read and no
  contained post-extraction cleanup call existed;
- auth and query target verification now use `consolidate=False`; page-state,
  snapshot/evaluation, and quality processing occur before cleanup;
- final cleanup re-enumerates the active query target, closes predecessors with
  a five-second per-close cap, and catches/logs listing or close failures without
  changing a valid provider result;
- focused Facebook/cross-source/worker/tick/source-log tests, compileall,
  release/runtime/authority tests, and diff check pass;
- artifact `dist/service/last30days-service-0.3.10.tar.gz` has SHA-256
  `900a886cf9974c7f3c3402f63acaf2707787a20d99b1fdd586e1e65226632d69`.

Authority classification:

- `inherited_authority`; commit/install and one S07 live proof remain inside the
  frozen successor; no live attempt has occurred since C08.

Next action:

- commit/install exact 0.3.10 with 0.3.9 rollback retained, verify installed
  invariants, then consume the single S07 proof.

### Checkpoint P0025-C11 | 2026-08-07

Plan version: 11

State transition:

- `deferred_cleanup_candidate_ready -> repeated_post_query_eval_timeout_hard_stop`.

Progress classification:

- `regression`; S07 removed cleanup from the critical path but a fresh direct
  query target repeated C04's post-query page-state evaluation timeout.

Evidence:

- installed 0.3.10/schema16 ready with 0.3.9 rollback retained and every pre-
  proof schedule/database/spec/attempt/timer/cost invariant passing;
- work `p0025-facebook-live-20260807-05` authenticated without login/checkpoint:
  service 0.257/2.735s, auth tab new/list/eval 8.256/8.500/8.213s;
- query tab new/list returned in 8.172/8.186s; immediate page-state eval timed
  out at 30.039s. No cleanup command or extraction ran;
- result failed/transient `agent_browser_timeout`, zero candidates, one request,
  zero cost, same failure signature as earlier adapter-result timeouts.

Authority classification:

- `human_gate`; C04 and S07 now repeat the same post-query evaluation invariant
  at configured live bounds. No additional install/live effect is inherited.

Next action:

- preserve installed 0.3.10 and prepare only an offline regression-backed
  candidate based on the one live strategy that previously reached extraction.

### Checkpoint P0025-C12 | 2026-08-07

Plan version: 12

State transition:

- `repeated_post_query_eval_timeout_hard_stop -> offline_same_target_successor_ready`.

Progress classification:

- `blocker_reduction`; live evidence supports one narrower offline hypothesis
  without crossing the install/live human gate.

Hypothesis and offline bounds:

- C02/S04's first proof reached search extraction after auth created a fresh
  home target and `_navigate` used `open` on that same target; C04 reused an old
  retained target, while S07 directly created a query target and both timed out;
- hypothesis: Facebook's direct query-tab creation path is unreliable for first
  Page-domain evaluation, while navigating a same-run home target that just
  passed auth eval preserves a usable page domain;
- primary owns one offline implementation attempt and one review/rework cycle;
  regression must require `navigate`, prohibit `new_tab` in `_navigate`, and
  retain post-extraction best-effort cleanup;
- no service install, live Facebook command, schedule change, or Graphiti
  success claim is permitted in this packet.

Authority classification:

- `inherited_authority`; offline code/test/artifact preparation is ordinary
  implementation inside the active goal. Installation and live validation
  remain the C11 `human_gate`.

Next action:

- add the same-run auth-target navigation regression red, implement the offline
  successor, and validate a deterministic candidate for operator review.

### Checkpoint P0025-C13 | 2026-08-07

Plan version: 13

State transition:

- `offline_same_target_successor_ready -> offline_same_target_candidate_ready`.

Progress classification:

- `blocker_reduction`; the repeated live failure is regression-locked and an
  exact offline candidate implements the only path that previously reached
  Facebook extraction.

Implementation and evidence:

- the new regression failed because `_navigate` created a separate query tab
  and performed critical-path target preparation; cleanup failure consequently
  masked a valid result;
- service 0.3.11 instead navigates the fresh home target that just passed auth
  evaluation, performs page-state evaluation directly, and retains bounded
  best-effort consolidation only after extraction;
- focused Facebook/worker/tick/source-log/release/runtime/authority tests pass;
  the complete Python suite, MCP Go suite, compileall, and diff checks pass;
- artifact `dist/service/last30days-service-0.3.11.tar.gz` has SHA-256
  `24233313875a388c848701e362d17744b05c6aa6ec52301b02846be907b4745b`;
- current installed readback remains ready service 0.3.10/schema16 with runtime
  manifest SHA-256
  `39e8d5ae20576541cf803f924583abe80391626bd4e2bb7f26dd2781a0e1bba4`.

Authority classification:

- `human_gate`; the offline packet is complete. Installing exact 0.3.11 would
  affect the scheduled lane, and another live Facebook proof would cross C11's
  repeated-invariant boundary.

Next action:

- await explicit operator authority for exact 0.3.11 install with 0.3.10
  rollback retained and one zero-cost canonical-profile Facebook proof.
