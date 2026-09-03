# Plan 0064 | Recurring Reddit Home Feed

State: OPEN
Lane: P24
Branch: feat/recurring-reddit-home-feed
Target: main
Integration: fast-forward
Roadmap: P24
Plan version: 1
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
- `daily-default` is enabled and ready for `2026-09-04T00:00:00Z`, but its
  saved configuration has no enabled Reddit feed target;
- the saved configuration requests X 80/3/360, LinkedIn 80/3/360, and YouTube
  3/1/120 with aggregate limits 163 items, seven attempts, 350 network
  requests, and 2,280 wall seconds;
- the most recent ordinary tick is `complete_degraded`: YouTube succeeded while
  X and LinkedIn failed. P08 continues to own those existing failures; this
  plan does not reinterpret or repair them;
- database integrity is `ok`; active ticks, execution attempts, provider
  attempts, tick resource leases, and collection profile leases are all zero;
- an exact-profile Agent Browser access plan finds the healthy retained
  `last30days-facebook` browser reusable with one compatible live browser,
  zero active claims, an available unblocked service request, and no manual
  seeding requirement.

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
