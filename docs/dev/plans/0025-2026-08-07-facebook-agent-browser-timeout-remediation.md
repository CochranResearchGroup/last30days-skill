# Plan 0025 | Facebook agent-browser timeout remediation

State: OPEN
Roadmap: P09
Plan version: 3
Date: 2026-08-07

## Objective

Diagnose the exact retained-browser command that causes Facebook collection to
time out before page readback, implement the narrowest source-owned mitigation,
and prove the repaired Facebook lane live without changing the accepted daily
schedule, source set, credentials, cost posture, or browser identity boundary.

## Current State

- P08/Plan 0024 is closed and the installed service-owned daily schedule is
  enabled and ready for the Aug 8 UTC boundary on service 0.3.5/schema 16.
- The latest five Facebook provider attempts are one `agent_browser_error`
  followed by four `agent_browser_timeout` results. The latest attempt took 38
  seconds, observed zero page signals, persisted no rendered page, and accepted
  zero items.
- A red-capable current-state assertion against the latest Facebook provider
  result exits 1 while its safe error code is `agent_browser_timeout`.
- The retained `stored-last30days-social` browser is live and viable, uses the
  canonical `last30days-facebook` profile, and contains a Facebook search tab.
  A read-only tab inventory succeeds but takes about eight seconds.
- Agent-browser service and remote-view doctors report ready/converged runtime
  state. The installed workstation payload reports a binary provenance
  mismatch, but current runtimes converge on the command on `PATH`; this is a
  maintenance finding, not yet proven causal.

## Scope

- capture operation-level timing for the exact acquisition/auth/navigation
  path without exposing credentials or page content;
- add a deterministic regression at the real adapter seam before changing the
  implementation;
- repair only the Facebook/shared agent-browser command behavior that current
  evidence proves faulty;
- build and install one reviewed service candidate if runtime code changes;
- run at most two cumulative bounded live Facebook proofs after offline
  validation; the first has been consumed and one successor proof remains;
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

- The active user goal, `diagnose, plan a mitigation, execute`, is standing
  authority for ordinary diagnosis, code/test/docs changes, candidate install,
  and one bounded live proof inside this existing source and profile boundary.
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

- Critical-path owner: primary agent; active-agent concurrency is one and no
  subagent is authorized or needed.
- Maximum implementation attempts: 2.
- Maximum review/rework cycles: 1.
- Maximum cumulative live Facebook source attempts: 2 after offline
  validation; attempt 1 is consumed and exactly one successor remains.
- Maximum diagnostic browser interaction: one tab-select/auth-read sequence,
  restoring the prior active tab when safe.
- Any repeated identical timeout after the one mitigation attempt is a hard
  stop for this execution window, not permission for retry fanout.

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
