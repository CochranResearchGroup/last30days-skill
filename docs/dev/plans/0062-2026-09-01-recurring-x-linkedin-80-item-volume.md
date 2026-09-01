# Plan 0062 | Recurring X And LinkedIn 80-Item Volume

State: OPEN
Roadmap: P08
Plan version: 1
Date: 2026-09-01
Branch: `fix/tick-restart-recovery`
Target: `main`

## Objective

Update the existing `daily-default` timer to request 80 unique canonical X
home-feed posts and 80 unique canonical LinkedIn home-feed posts on every tick,
with enough installed scroll and wall-time budget to make those limits real.

## Current State

- the timer requests 10 X and 10 LinkedIn items with three attempts per source;
- Reddit and Facebook are disabled, while YouTube remains enabled for 3 items;
- the installed X scraper caps explicit feed requests at 32 scrolls, which
  previously accepted 78/80 while still yielding new posts;
- a bounded 36-scroll X canary accepted 80/80, and LinkedIn accepted 80/80 in
  289.453 seconds after 29 scrolls;
- `daily-default` is ready for `2026-09-02T00:00:00Z` and no tick or provider
  attempt is active.

## Scope

- raise X and LinkedIn provider item limits from 10 to 80;
- retain three attempts for X and LinkedIn and existing source enablement;
- raise X's finite explicit-feed allowance to the two-posts-per-scroll 80-item
  bound;
- raise X and LinkedIn provider wall-time budgets to 360 seconds and update the
  aggregate item and wall-time budgets consistently;
- build, validate, and install one version-distinct service artifact;
- rebind only the paused `daily-default` row from the old exact config digest to
  the new validated digest while preserving its next boundary;
- observe the next ordinary scheduled tick under the resulting configuration.

## Non-Goals

- manually triggering a tick in this slice;
- changing Reddit, Facebook, or YouTube enablement or selectors;
- changing the authenticated browser profile, content acceptance rules,
  deterministic ad/spam filtering, or retry count;
- operating or repairing Agent Browser lifecycle state.

## Acceptance Criteria

1. Saved configuration reads back X `items=80`, LinkedIn `items=80`, both with
   `attempts=3` and `wall_seconds=360`.
2. Aggregate limits admit all enabled work: 7 attempts, 163 items, 350 network
   requests, and 2,280 wall seconds.
3. Installed X explicit-feed policy permits 40 scrolls and a deterministic
   two-new-posts-per-scroll fixture reaches 80 unique items.
4. Service 0.3.92 is installed, ready, and bound to its exact runtime manifest.
5. `daily-default` remains enabled and ready at the unchanged September 2
   boundary under the new exact config digest, with no tick admitted by the
   configuration/rebind operation.
6. The next ordinary tick has terminal provider receipts for X, LinkedIn, and
   YouTube, after which active attempts and leases return to zero and SQLite
   `quick_check` passes.

## Definition Of Done

The timer, installed service, and schedule read back acceptance criteria 1
through 5 without admitting a manual tick, and the next ordinary scheduled
tick subsequently satisfies acceptance criterion 6 or records one exact
external blocker.

## Execution Packets

### P0062-A | Deterministic capacity and configuration change

- owner: primary agent;
- write surfaces: X feed bound, focused regression, service release identity,
  owner-private tick config, Plan 0061/0062, P08 roadmap state, and runbook;
- terminal condition: acceptance criteria 1 through 5 have current readback.

### P0062-B | Ordinary scheduled-tick observation

- owner: primary agent;
- write surfaces: Plan 0062, P08 roadmap state, and append-only runbook only;
- dependency: P0062-A accepted and the September 2 boundary reached;
- terminal condition: acceptance criterion 6 has a durable readback or one
  exact external blocker is recorded.

## Bounds And Stops

- one release build/installation transaction and one exact schedule rebind;
- no manual tick enqueue or provider attempt during P0062-A;
- no more than the already-configured three attempts per X or LinkedIn lane;
- preserve the exact `last30days-facebook` profile and all deterministic
  exclusions;
- stop if the schedule row, prior digest, next boundary, or active-work census
  differs from the pre-mutation readback.

### Checkpoint P0062-C01 | 2026-09-01

Plan version: 1

State: `implementation_active`

Progress classification: `outcome_progress`

Authority classification:

- `inherited_authority`; the operator directed the recurring timer to collect
  80 unique X and 80 unique LinkedIn posts.

Evidence:

- live service 0.3.91 is ready and compatible on schema 16;
- the current saved timer requests 10/10 with 120-second provider ceilings;
- Plan 0059's live canary proved X 80 at 36 scrolls and LinkedIn 80 in 289.453
  seconds, while the installed 32-scroll X pass stopped at 78 without
  stagnation.

Subagent status: `not_spawned`

Graphiti write status: `not_written`; current repository and runtime evidence
are sufficient.

Next action: validate and install the bounded capacity change, save the 80+80
configuration, then perform the exact guarded schedule rebind without
admitting a tick.
