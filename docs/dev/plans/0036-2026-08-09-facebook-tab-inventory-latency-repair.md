# Plan 0036 | Facebook Tab Inventory Latency Repair

State: OPEN
Roadmap: P13
Plan version: 2
Date: 2026-08-09
Predecessor: Plan 0035 version 3/checkpoint P0035-C03

## Objective

Repair the Facebook adapter's reproducibly narrow read-only tab-inventory
deadline, install the bounded successor runtime, then obtain accepted Facebook
content through the already-enabled daily scheduler path without waiting for
natural time.

## Current State

- installed service 0.3.38/schema16 is ready and `daily-default` already
  enables Facebook at an 86,400-second cadence;
- Plan 0035's only tick ended before page inspection: two service reads
  completed in 716 and 4,252 milliseconds, then session tab inventory hit its
  fixed 10-second subprocess deadline at 10,025 milliseconds;
- raw CDP target discovery returns the retained Facebook page, and four exact
  session-scoped inventory reads succeed. Three consecutive measured reads
  take 8.4-8.8 seconds, establishing a narrow deadline rather than a blank or
  logged-out Facebook page;
- a red regression expects a 20-second inventory allowance and currently
  fails because installed/source code supplies 10 seconds;
- the adapter already enforces a separate cumulative 75-second run budget, so
  widening this one read-only operation does not make provider work unbounded.

## Scope

- define an explicit 20-second Facebook session-inventory deadline;
- retain the cumulative 75-second adapter budget and all existing inner job,
  parent worker, request, item, cost, model, auth, challenge, rate-limit,
  quality, provenance, target, cleanup, and schedule gates;
- add deterministic regressions for the selected timeout and cumulative-budget
  clamp, validate the canonical suites, install the successor service, and
  prove source/installed convergence;
- after fresh runtime guards, run one distinct Facebook-only proof through the
  same coordinator/adapter path used by the timer;
- qualify routine automation only if accepted Facebook content and persisted
  provenance satisfy Plan 0035's content contract while the existing schedule
  remains enabled and unchanged.

## Non-Goals

- no browser open/close, unrelated-tab cleanup, profile reassignment, schedule
  or cadence mutation, login/logout, CAPTCHA/checkpoint interaction, rate-limit
  induction, provider fallback, cost, model use, or unbounded retry;
- no reliance on unscoped `--cdp` attachment and no claim that the separately
  observed default-profile lock caused the exact session-scoped timeout;
- no routine-ready claim from configuration, CDP liveness, or tests alone.

## Acceptance Criteria

1. The Plan 0035 terminal operation ledger and three measured exact-session
   probes are preserved as the red-test basis.
2. Auth tab inventory receives at most 20 seconds, while `_invoke()` still
   clamps it to the remaining cumulative 75-second run budget.
3. Focused Facebook tests, source-log visibility, canonical Python suite,
   packaging/docs/authority checks, and installed-skill sync pass.
4. The installed service reports the successor version ready and source,
   installed skill, artifact, manifest, and contract identities converge.
5. One new fully guarded Facebook-only tick persists at least one accepted
   in-window canonical Facebook post with coherent counters and provenance,
   zero cost/model use, and no auth/challenge/rate-limit/integrity signal.
6. `daily-default` remains enabled/ready with Facebook present and its cadence
   unchanged; current/rollback databases are `ok`; the retained browser owner
   and intended tabs are preserved.

## Definition Of Done

- criteria 1-6 have exact tests, hashes, IDs, counters, and runtime readbacks;
- P13 closes only after accepted content proves the installed adapter and
  existing recurring path usable;
- coherent implementation and closeout commits are pushed to `origin/main`.

## Execution Bounds

- primary agent owns the serialized repair, install, and one live proof;
- maximum implementation/rework cycles: two;
- maximum new provider attempts: one, only after installed convergence and
  fresh guards;
- hard stop on failed guard, unexpected browser ownership/lifecycle change,
  auth/challenge/rate-limit signal, nonzero cost/model use, or need to mutate
  the recurring schedule;
- no subagent; deterministic validation and independent runtime readbacks are
  required before the effect boundary.

## Owned Write Surfaces

- Facebook adapter and focused tests;
- version/release/configuration/help surfaces required by the repository;
- Plan 0035 closeout, this plan, P13, RUNBOOK, authority test, and one bounded
  incident/closeout note;
- installed service/skill artifacts and one future provider receipt.

### Checkpoint P0036-C01 | 2026-08-09

Plan version: 1

State transition:

- `tab_inventory_latency_blocker -> deterministic_repair_ready`.

Progress classification:

- `blocker_reduction`; the exact read-only command now reproduces the latency
  margin defect without another Facebook provider attempt.

Owned changes:

- added one red regression specifying a 20-second inventory allowance; no
  production code, runtime, browser, or schedule change yet.

Validation evidence:

- the Plan 0035 tick timed out at `tab` after 10,025 milliseconds;
- exact session inventory succeeded three consecutive times in 8.4-8.8
  seconds with four tabs and the Facebook home page active;
- `uv run pytest tests/test_facebook.py -k
  auth_tab_inventory_allows_observed_service_latency -q` fails `20 != 10`.

Subagent status and reconciliation:

- `not_spawned`; the primary owns this serialized repair.

Authority classification:

- `inherited_authority`; the repair directly addresses the terminal Plan 0035
  blocker without consuming a provider or browser effect.

Review disposition summary:

- `blocking=1` red regression, `rejected=0`, `needs_evidence=0`,
  `nonblocking_backlog=0`.

Graphiti write status:

- deferred until installed/runtime outcome is source-backed.

Remaining acceptance criteria:

- criteria 2-6.

Next action:

- implement the narrow timeout change, prove the cumulative clamp, and run the
  focused regression before broader validation.

### Checkpoint P0036-C02 | 2026-08-09

Plan version: 2

State transition:

- `deterministic_repair_ready -> installed_live_guard_ready`.

Progress classification:

- `outcome_progress`; the narrow repair is committed, fully validated,
  installed, synchronized, and re-read from the current runtime.

Owned changes:

- introduced `TAB_INVENTORY_TIMEOUT_SECONDS=20` only for the authentication
  session inventory call; retained `_invoke()`'s cumulative-budget clamp;
- versioned and installed service 0.3.39, refreshed the deterministic runtime
  manifest, and synchronized the frozen installed Skill copy;
- no provider, browser, tab, profile, challenge, or schedule effect occurred.

Validation evidence:

- red regression failed `20 != 10` before implementation; both the selected
  timeout and remaining-run-budget clamp regressions pass afterward;
- focused Facebook, release/runtime, authority, and source-log suites pass;
  canonical validation passes 2,631 tests, 7 skips, and 6 subtests;
- implementation commit `4ee8972` is pushed to `origin/main`;
- artifact `last30days-service-0.3.39.tar.gz` has SHA-256
  `fbfa1bbc9a1727372d6d96b8fcadb14aa72eb40f344bd554841fe5c73023858e`;
- installed 0.3.39/schema16 is ready at runtime-manifest SHA-256
  `6093ddc3231692ebb1d72d3d1869a7226fac0a61f10be0c9766e80ac48848bae`
  and contract SHA-256
  `fe8727fbe0d4e2f6775f49a6fc958369fe4877ba812bae4ef69121b88f12e2f1`;
- source, installed Skill, and installed service Facebook files are identical
  at SHA-256
  `0851bda99d1c57ad0ceac50f40cb6df0f93b153d00708f02aece2a337c46955e`;
- current and 0.3.38 rollback SQLite quick checks are `ok`;
  `daily-default` remains enabled/ready at 86,400 seconds with next boundary
  `2026-08-10T00:00:00Z`;
- retained PID 63205 is ready with `lastError=null`, four intended tabs, and
  one active Facebook home target. An unrelated lifecycle-only dashboard job
  uses no browser/profile; queue depth and profile-lease waiters are zero.

Subagent status and reconciliation:

- `not_spawned`; the primary independently ran every validation and runtime
  readback.

Authority classification:

- `inherited_authority`; source, artifact, install, and sync are the exact C01
  repair packet and consume no provider attempt.

Review disposition summary:

- `blocking=0`, `rejected=0`, `needs_evidence=0`,
  `nonblocking_backlog=0` for the deterministic repair;
- routine content qualification remains the sole outstanding gate.

Graphiti write status:

- deferred until the live proof reaches a terminal source-backed outcome.

Remaining acceptance criteria:

- criteria 5-6 require one fresh preflight, one provider result, and final
  schedule/browser/database readbacks.

Next action:

- publish this installed checkpoint, run fresh guards and a new distinct
  Facebook-only preflight, then enqueue that exact tick once without waiting
  for the natural scheduler.

## Stop Rules

Stop on any execution-bound violation. A failed future provider result is
terminal for this plan and is not retried automatically.
