# Plan 0036 | Facebook Tab Inventory Latency Repair

State: OPEN
Roadmap: P13
Plan version: 1
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

## Stop Rules

Stop on any execution-bound violation. A failed future provider result is
terminal for this plan and is not retried automatically.
