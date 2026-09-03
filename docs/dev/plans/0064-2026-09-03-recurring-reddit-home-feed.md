# Plan 0064 | Recurring Reddit Home Feed

State: OPEN
Lane: P24
Branch: feat/recurring-reddit-home-feed
Target: main
Integration: fast-forward
Roadmap: P24
Plan version: 2
Date: 2026-09-03

## Objective

Activate an authenticated Reddit home-feed lane on the existing
`daily-default` schedule so each ordinary tick requests up to 80 unique
canonical Reddit posts with the same bounded three-attempt reliability posture
as X and LinkedIn.

## Current State

- Plan 0063/C15 proved the installed service 0.3.109 Reddit feed adapter with
  80 accepted, stored, and indexed canonical posts after 25 document-progress
  scrolls;
- `daily-default` is enabled and ready for `2026-09-04T00:00:00Z` under saved
  revision `operator-20260903-reddit-home-feed-80-v1` and validated digest
  `sha256:8e3811d5e9b561cfd3f97b3d9897770ee4c623fe9e74a443bc01d86fca4d3449`;
- the saved configuration now requests Reddit 80/3/360 alongside X 80/3/360,
  LinkedIn 80/3/360, and YouTube 3/1/120 with aggregate limits 243 items, ten
  attempts, 500 network requests, and 3,360 wall seconds;
- the most recent ordinary tick is `complete_degraded`: YouTube succeeded while
  X and LinkedIn failed. P08 continues to own those existing failures; this
  plan does not reinterpret or repair them;
- database integrity is `ok`; active ticks, execution attempts, provider
  attempts, tick resource leases, and collection profile leases are all zero;
- an exact-profile Agent Browser access plan finds the healthy retained
  `last30days-facebook` browser reusable with one compatible live browser,
  zero active claims, an available unblocked service request, and no manual
  seeding requirement;
- the guarded activation affected exactly one schedule row, preserved the next
  boundary and prior tick identity, admitted no tick/provider attempt, and
  retained zero active work or leases with SQLite integrity `ok`;
- private pre-change config and database backups are retained under the
  user-scoped last30days backup directory.

## Scope

- add a dedicated `reddit-home-feed` service entry using
  `reddit_agent_browser`, profile capability reference
  `agent-browser-profile:last30days-facebook`, and the existing serialized
  profile resource key;
- add one enabled `operator-20260903-reddit-home-feed` target with
  `surface_kind=feed`, selector `feed=home`, and authenticated profile access
  partition;
- request 80 items, three transient-only attempts, 360 seconds per attempt,
  and 50 governed top-level source requests;
- raise aggregate limits to 243 items, ten attempts, 500 network requests, and
  3,360 wall seconds without changing cost or model-token limits;
- preflight the exact prospective configuration, save it atomically, and
  rebind only `daily-default` to the validated digest while preserving its
  next boundary and prior tick receipt;
- observe the first ordinary scheduled Reddit lane after activation.

## Non-Goals

- manually enqueueing a tick or collection run;
- changing X, LinkedIn, Facebook, or YouTube targets, limits, selectors, or
  retry behavior;
- changing Reddit acceptance, ad/spam filtering, search capability, browser
  profile identity, authentication, or Agent Browser lifecycle state;
- enabling any historical Plan 0018 or Plan 0063 QA collection specification;
- repairing the existing P08 X/LinkedIn ordinary-tick failures.

## Acceptance Criteria

1. Prospective-config preflight expands exactly four enabled lanes and selects
   `reddit_agent_browser` for the Reddit home-feed lane.
2. Saved readback shows Reddit 80 items, three attempts, 360 seconds, the exact
   `last30days-facebook` capability/resource identity, and aggregate limits
   243/10/500/3,360.
3. The guarded rebind changes only the `daily-default` config digest while
   preserving its enabled ready state, next boundary, last boundary, and last
   tick identity.
4. The configuration/rebind operation admits no tick or provider attempt;
   active work and leases remain zero and SQLite `quick_check` remains `ok`.
5. The installed service restarts ready on service 0.3.109/schema 17 and reports
   Reddit among the frozen enabled adapters for the next ordinary tick.
6. The next ordinary tick records a terminal Reddit provider receipt, after
   which active work and leases return to zero; success yields up to 80 unique
   canonical posts and failure retains one exact typed blocker.

## Execution Packets

### P0064-A | Guarded recurring activation

- owner: primary agent;
- write surfaces: user-scoped tick configuration, exact `daily-default` digest
  binding, Plan 0064, P24 roadmap/catalog state, and append-only runbook;
- terminal condition: acceptance criteria 1 through 5 have current readback;
- hard bound: one prospective config, one atomic config save, one database
  backup, one exact guarded schedule-row rebind, and one service restart.

### P0064-B | First ordinary tick observation

- owner: primary agent;
- dependency: P0064-A accepted and the next UTC daily boundary reached;
- write surfaces: Plan 0064, P24 roadmap/catalog state, and append-only runbook
  only;
- terminal condition: acceptance criterion 6 has a durable terminal receipt.

## Bounds And Stops

- no manual tick, collection run, browser command, or provider attempt;
- stop before mutation if the saved config digest, schedule identity/state,
  next boundary, last tick, active-work census, or database integrity differs
  from the planning readback;
- stop after service shutdown if any active work or lease appears;
- apply the database rebind only when the old digest and every preserved
  schedule field match exactly; a zero-row or multi-row update is failure;
- retain one pre-change private backup and roll back the config plus exact
  schedule binding if restart/readback fails;
- at most two work-unit attempts and one closed-world repair cycle;
- no drift-discovery review pass unless current evidence reveals a new
  consequential mismatch.

## Current Checkpoint

### Checkpoint P0064-C01 | 2026-09-03

Plan version: 1

State: `planned_activation_ready`

Progress classification: `outcome_progress`

Authority classification:

- `inherited_authority`; the operator explicitly authorized recurring Reddit
  scraping, including the required saved-config and schedule-binding mutation.

Evidence:

- Plan 0063/C15 installed/live 80-item acceptance;
- live schedule, config, active-work, SQLite, and exact-profile Agent Browser
  no-effect readbacks described in Current State.

Subagent status and reconciliation:

- `not_spawned`; current orchestration policy prohibits delegation.

Graphiti write status:

- discovery completed in `last30days_skill_main`; older memory confirms
  `daily-default` is the established recurring schedule, while current repo and
  runtime readbacks remain authoritative.

Next action:

- publish P24 registration, preflight the prospective configuration, then
  perform the single guarded activation without admitting a manual tick.

### Checkpoint P0064-C02 | 2026-09-03

Plan version: 2

State: `recurring_reddit_active_awaiting_first_ordinary_tick`

Progress classification: `outcome_progress`

Authority classification:

- `inherited_authority`; the saved-config replacement, exact one-row digest
  rebind, and service restart were ordinary in-scope activation steps.

Evidence:

- installed-runtime preflight returned `ready`, four enabled lane manifests,
  `reddit_agent_browser`, aggregate limits 243/10/500/3,360, and Slack
  notification readiness;
- the saved config reads revision
  `operator-20260903-reddit-home-feed-80-v1`, Reddit target
  `operator-20260903-reddit-home-feed`, authenticated partition/profile, 80
  items, three attempts, and 360 seconds;
- the guarded database update matched exactly one `daily-default` row and moved
  only its digest from
  `sha256:069cf238586388e1e55924083e97161a403dd7fa488a6c2cf45d55fb29500074`
  to
  `sha256:8e3811d5e9b561cfd3f97b3d9897770ee4c623fe9e74a443bc01d86fca4d3449`;
- post-restart schedule readback remains enabled/ready for
  `2026-09-04T00:00:00Z`, preserving last tick
  `tick-56c9c3b9a2f0a9897a09db4f45fe830e`, last boundary
  `2026-09-03T00:00:00Z`, and zero runtime error;
- tick count remains 119 with the latest created at
  `2026-09-03T00:00:02.024013Z`; active ticks, execution attempts, provider
  attempts, tick leases, and collection profile leases are zero;
- all historical Reddit collection specs remain disabled and SQLite
  `quick_check=ok`; service 0.3.109 is active after restart;
- pre-change backups pass integrity/readback at
  `backups/research-pre-reddit-recurring-20260903.db` and
  `backups/tick-config-pre-reddit-recurring-20260903.json` under the private
  last30days data directory.

Subagent status and reconciliation:

- `not_spawned`; current orchestration policy prohibits delegation.

Graphiti write status:

- `graphiti_write_pending`; provider readiness is degraded on a Codex
  app-server `RuntimeError`, so no write was queued. Repository and current
  runtime readbacks remain authoritative.

Next action:

- observe the first ordinary four-lane tick after the September 4 UTC boundary
  and close or checkpoint P24 from its terminal Reddit receipt.
