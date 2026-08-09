# Plan 0032 | Facebook 0.3.34 Tab Lifecycle Repair And Qualification Closeout

State: CANCELLED
Roadmap: P13
Plan version: 3
Date: 2026-08-09
Predecessor: Plan 0031 version 2/checkpoint P0031-C02

## Objective

Repair Facebook retained-tab lifecycle in service 0.3.33, converge the current
duplicate targets to one reusable Facebook tab, then qualify routine attended
use with one source-scoped governed manual tick or stop with an exact typed
blocker.

## Current State

- 0.3.34 is installed ready on schema 16 and offline-validated;
- the scraper now uses one fresh target after a first post-navigation Runtime
  timeout even when active-tab identity matches;
- the prior attempt completed at `2026-08-09T15:19:06.946157Z`, so the earliest
  authorized 60-minute boundary is `2026-08-09T16:19:07Z`;
- Facebook is not routine-qualified. Installed tests and readiness are not live
  acquisition proof;
- current live inventory contains 19 targets: 16 Facebook, one X, one LinkedIn,
  and one preview. Facebook cleanup runs only on successful paths and disables
  same-site consolidation, so timeout failures leak targets and successful
  attempts preserve duplicates;
- service 0.3.33 repaired ordinary and typed-failure cleanup and the retained
  session was converged to four live tabs. The sole live proof then exhausted
  the hard 120-second worker boundary, which killed the child before its
  `finally` could run and temporarily left a second Facebook target;
- tick `tick-c9a6b9e9e30d22fbe01328ab1e7ee6d8` is terminal
  `complete_degraded`; provider attempt
  `provider-attempt-d666f13ccab3f3e7e5d35ed30a808f29` failed transiently as
  `worker_timeout` with zero observed, accepted, or rejected candidates. The
  duplicate was manually reconverged and the session is back to four tabs.

## Scope

- make Facebook cleanup run after every acquired-workspace outcome without
  masking the provider result, preserve one reusable Facebook target, and close
  only same-site duplicates;
- install and verify service 0.3.33, then re-read service, schedule, database, agent-browser
  install/remote-view, retained browser/profile/tab, challenge, queue, lease,
  and Facebook acquisition readiness without launching a browser;
- create one Facebook-only preflight for the exact intended interval and
  existing limits, verify its frozen scope, then enqueue it exactly once;
- poll only that durable tick receipt and adjudicate against the acceptance
  contract; preserve typed failure evidence without retry.
- add parent-owned post-timeout same-site cleanup after the isolated child has
  been killed and reaped, without altering the terminal worker receipt or
  provider wall accounting; install and verify service 0.3.34.

## Non-Goals

- no logout, credential entry, MFA, CAPTCHA, checkpoint, consent, cookie or
  session mutation, intentional rate-limit/challenge generation, browser
  closure, non-Facebook tab closure, or direct browser navigation beyond the
  later single governed proof;
- no natural scheduler wait, schedule mutation, provider-limit increase,
  fallback, second enqueue in this plan, same-build retry, cost/model use, or
  content dump;
- no routine-usability claim from readiness, tests, or a degraded receipt.

## Acceptance Criteria

1. Every acquired Facebook workspace reaches one best-effort cleanup on success
   or typed failure; cleanup consolidates same-site targets to one reusable tab
   and never masks the original provider result.
2. One governed cleanup reduces the observed live inventory from 16 Facebook
   targets to one and 19 total targets to four, preserving one Facebook, one X,
   one LinkedIn, one preview, and retained browser PID 63205.
3. Fresh guards pass after `2026-08-09T16:19:07Z` with service 0.3.33/schema16,
   Facebook acquisition ready, the retained canonical browser/profile viable,
   zero active challenge, queue/lease depth zero, SQLite `ok`, and unchanged
   `daily-default` schedule identity/cadence.
4. The matching preflight predicts exactly one Facebook lane/provider/attempt,
   at most 50 requests, 120 wall seconds, three items, and zero cost/model use.
5. Exactly one enqueue occurs and reaches one durable terminal provider result;
   no retry or browser-process lifecycle action occurs.
6. Routine attended usability requires provider success with at least one
   accepted post or a genuine typed empty result after successful bounded
   extraction. Any auth, checkpoint, CAPTCHA, rate-limit, timeout, integrity,
   quality-only zero-yield, or unknown result stops without retry.
7. After a hard Facebook worker timeout, the parent preserves the exact typed
   `worker_timeout` result and budget receipt while bounded cleanup converges
   same-site targets to one; other sources and non-timeout results do not invoke
   that cleanup. Exact 0.3.34 installation preserves schema 16, schedule,
   database integrity, browser PID, and zero-cost posture.

## Definition Of Done

- criteria 1-5 have exact IDs, timestamps, counters, and current-state evidence;
- criterion 6 records the exact terminal blocker and keeps Facebook manual and
  not routine-qualified;
- criterion 7 closes this plan's repair/containment responsibility and opens a
  distinct later proof only after a fresh safety boundary;
- plan, roadmap, runbook, runtime, and Git history agree.

## Execution Bounds

- primary agent owns the serialized critical path; no subagent is used;
- one preflight/enqueue pair, one attempt, one Facebook provider, and no retry;
- close only verified duplicate `facebook.com` targets while preserving one
  reusable Facebook target and every other-site target;
- do not wait for the natural scheduler; execute manually only after the fixed
  safety boundary and fresh no-launch guards;
- hard stop on any failed guard, auth/challenge/rate-limit evidence, ownership
  ambiguity, schedule drift, database failure, nonzero cost/model use, or
  privacy-sensitive output.
- no second live proof in this plan; the next proof is a successor packet no
  earlier than 60 minutes after `2026-08-09T18:19:59.964036Z`.

## Owned Write Surfaces

- durable tick/provider receipts in the installed service database;
- this plan, `ROADMAP.md`, `RUNBOOK.md`, and one bounded evidence note if the
  terminal result materially changes P13.

### Checkpoint P0032-C01 | 2026-08-09

Plan version: 1

State transition:

- `offline_recovery_installed_gated -> awaiting_manual_safety_boundary`.

Progress classification:

- `outcome_progress`; the disproved fallback is repaired and installed, leaving
  one explicit live criterion rather than an offline implementation blocker.

Validation evidence:

- Plan 0031/C02 binds the exact tests, artifact, installation, database,
  schedule, and retained-browser readbacks.

Subagent status and reconciliation:

- none; the later proof is one serialized effect boundary.

Authority classification:

- `inherited_authority`, subject to the explicit time and fresh-readiness gate.

Graphiti write status:

- predecessor terminal write pending after its durable commit.

Next action:

- repair, validate, install, and converge the retained Facebook tab lifecycle;
  then run fresh no-launch guards and, only if they all pass, one matching
  preflight/enqueue pair without retry.

### Checkpoint P0032-C02 | 2026-08-09

Plan version: 2

State transition:

- `awaiting_manual_safety_boundary -> tab_lifecycle_repair_required`.

Progress classification:

- `constraint_progress`; exact inventory disproved the assumption that retained
  targets were bounded and reusable between attempts.

Validation evidence:

- retained browser PID 63205 is ready with 19 live targets: 16 Facebook, one X,
  one LinkedIn, and one preview;
- source inspection shows Facebook cleanup is absent from typed failure paths
  and calls same-site preparation with `consolidate=False` on success.

Authority classification:

- `scope_expansion`; user authorized closing verified same-site duplicates after use or
  reuse an existing tab, while preserving the retained browser and unrelated
  service tabs.

Next action:

- land service 0.3.33 with finally-bound same-site consolidation, prove its
  behavior offline, install it, and converge 16 Facebook targets to one before
  consuming the single live qualification attempt.

### Checkpoint P0032-C03 | 2026-08-09

Plan version: 3

State transition:

- `tab_lifecycle_repair_required -> hard_worker_timeout_cleanup_required`.

Progress classification:

- `validated_learning`; 0.3.33 fixed ordinary cleanup and live inventory
  convergence, while the sole proof isolated hard child termination as the
  remaining tab-lifecycle gap.

Validation evidence:

- installed 0.3.33/schema16 was ready with runtime-manifest SHA-256
  `f659ee7edbd1bdf670522c2a8b4239b5b933ba0ce4bff01c4475cc9f22995b1f`;
- exact cleanup reduced 16 Facebook targets to one and 19 total tabs to four,
  preserving X, LinkedIn, preview, and browser PID 63205;
- the sole preflight predicted tick
  `tick-c9a6b9e9e30d22fbe01328ab1e7ee6d8`, lane
  `tick-lane-7585fee26be08c222491d8dc8f16845d`, one provider attempt,
  50 requests, 120 seconds, three items, and zero cost/model use;
- provider attempt `provider-attempt-d666f13ccab3f3e7e5d35ed30a808f29`
  completed once as transient `worker_timeout`, consumed 120 wall seconds,
  and observed/accepted/rejected `0/0/0`; rejection counts were empty;
- hard termination prevented child `finally`, temporarily producing two
  Facebook tabs. Exact manual cleanup restored one Facebook and four total;
  browser PID 63205 remains ready and queue/lease-wait depths are zero.

Subagent status and reconciliation:

- none; the primary owns the serialized timeout-containment repair.

Authority classification:

- `inherited_authority`; this successor changes only cleanup after the consumed
  attempt and cannot create another provider call.

Graphiti write status:

- deferred until the 0.3.34 repair is durable and installed.

Next action:

- add a bounded, non-masking parent timeout cleanup hook; validate and install
  0.3.34; close Plan 0032 unsuccessfully for live qualification and open one
  later no-retry proof after `2026-08-09T19:20:00Z`.

### Checkpoint P0032-C04 | 2026-08-09

Plan version: 3

State transition:

- `hard_worker_timeout_cleanup_required -> timeout_cleanup_installed_gated`;
- `OPEN -> CANCELLED` unsuccessfully for live qualification.

Progress classification:

- `blocker_reduction`; hard timeout can no longer leave its bounded Facebook
  recovery target uncontained, while the consumed proof remains rejected.

Validation evidence:

- the parent kills and reaps the timed-out acquisition worker before invoking
  one isolated source-owned cleanup subprocess; only the exact
  `facebook_agent_browser`/Facebook pair is eligible;
- cleanup validates a 4,096-byte exact request, consolidates only
  `facebook.com` targets, retains one reusable target, uses 30-second browser
  command bounds, and never replaces the original `worker_timeout` result;
- the source-isolation process canary proves the long-lived service does not
  import Facebook acquisition code;
- 2,620 Python tests passed with 7 skips and 6 subtests; all Go MCP packages,
  compileall, runtime/package/release/authority checks, and patch checks passed;
- two 0.3.34 artifacts are byte-identical at SHA-256
  `f1c3043abec18df159f46f8af75b7c4e619b5d4e7bef090de60315f6e59873ad`;
- installed 0.3.34/schema16 is ready with contract SHA-256
  `fe8727fbe0d4e2f6775f49a6fc958369fe4877ba812bae4ef69121b88f12e2f1`
  and runtime-manifest SHA-256
  `e2d31ce5c6d9d5257eea3317deaa96901aae7737cdb04142c3ff1bc57a0d3231`;
- SQLite is `ok`; `daily-default` remains enabled/ready at 86,400 seconds;
  retained browser PID 63205 is ready with exactly four tabs: one Facebook,
  one X, one LinkedIn, and one preview; lease-wait depth is zero;
- copied Skill installs were refreshed across supported hosts; PromptScript's
  two unsupported global-install results remain truthful.

Subagent status and reconciliation:

- none; the primary implemented, validated, installed, and reconciled the
  serialized repair.

Authority classification:

- `inherited_authority`; no second provider call, retry, schedule change,
  browser close, cost, model use, or external communication occurred.

Graphiti write status:

- one compact source-backed write was queued as job
  `a0434981-fa1f-451d-838e-39f908205545` after provider readiness passed, then
  timed out once during node resolution after 90 seconds; it is non-retryable,
  so no duplicate write was attempted.

Next action:

- Plan 0033 owns one later guarded 0.3.34 proof after
  `2026-08-09T19:20:00Z`; do not wait for the natural scheduler or rerun the
  consumed Plan 0032 tick.
