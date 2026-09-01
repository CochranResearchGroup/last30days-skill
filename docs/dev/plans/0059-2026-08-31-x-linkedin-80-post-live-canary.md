# Plan 0059 | X And LinkedIn 80-Post Live Canary

State: CLOSED
Roadmap: P08
Plan version: 1
Date: 2026-08-31

## Objective

Run one schedule-disabled authenticated home-feed canary targeting 80 accepted
canonical posts from X and 80 from LinkedIn through installed service 0.3.90,
then report exact yield, scroll depth, deterministic exclusions, retained
browser state, and recurring-configuration invariants.

## Scope

- use only the existing `last30days-facebook` authenticated profile;
- run installed-runtime direct feed collection without publishing or storing
  provider rows;
- allow one bounded corrective X retry when the default finite ceiling stops
  within two items of the target while still yielding new observations;
- preserve all permalink, ownership, dedupe, ad/spam, auth, checkpoint, and
  rate-limit gates;
- verify the recurring timer, disabled canary specs, database integrity, and
  retained-browser state after the run.

## Non-Goals

- changing recurring source enablement, item limits, schedules, or collection
  specs;
- modifying or reinstalling Last30days or Agent Browser;
- creating another browser profile or duplicate live profile process;
- changing semantic relevance or quality filtering;
- persisting an 80-item X scroll ceiling without a separate implementation
  decision.

## Definition Of Done

1. LinkedIn either reaches 80 unique canonical accepted posts or returns one
   terminal bounded receipt with its exact stop reason.
2. X either reaches 80 under the installed finite policy or, if the 32-scroll
   ceiling alone stops at 78 or 79 with no stagnation, receives at most one
   transparent process-local retry capped at 36 scrolls.
3. Every accepted item counted by the canary has a unique canonical provider
   permalink.
4. Deterministic ad, duplicate, structural, and result-limit exclusions remain
   visible in diagnostics.
5. The recurring config digest, source enablement, disabled canary specs,
   schedule state, database integrity, and exact browser profile remain
   unchanged.

## Execution

1. Call the live service discovery surface and require compatibility.
2. Run X once at `limit=80` through the installed scraper.
3. Run LinkedIn once at `limit=80` through the installed scraper.
4. If and only if X stops at the 32-scroll ceiling within two items while
   still discovering new observations, run one process-local 36-scroll retry.
5. Reconcile runtime and repository evidence and close the bounded canary.

### Checkpoint P0059-C01 | 2026-08-31

State: `bounded_80x80_canary_complete`

Authority classification:

- `explicit_authority`

Outcome:

- live service discovery reported ready and compatible on service 0.3.90,
  database schema 16, contract
  `fe8727fbe0d4e2f6775f49a6fc958369fe4877ba812bae4ef69121b88f12e2f1`,
  and runtime manifest
  `28a9ae91e54f2b8b1e33773928f70010954d0132cbce874df4012e3ecce18027`;
- X attempt one accepted 78 unique canonical posts after all 32 installed
  scrolls. It observed 78 unique posts, remained non-stagnant, and rejected
  only 164 duplicate sightings. This is a finite-ceiling result, not an auth,
  navigation, extraction, or quality-gate failure;
- the authorized bounded X retry raised only the in-process maximum to 36.
  It accepted 80 unique canonical posts after 36 scrolls, observed 82 unique
  posts, rejected 180 duplicate sightings, and excluded two surplus posts at
  the result limit. No installed file or saved configuration changed;
- LinkedIn accepted 80 unique canonical posts after 29 scrolls in 289.453
  seconds. It observed 102 unique candidates, rejected 367 sponsored-ad
  observations and 1,159 duplicate sightings, and needed no snapshot renewal,
  feed refresh, or reload;
- both successful source receipts returned the correct authenticated feed
  title and URL with no typed error;
- recurring revision `operator-20260822-x-linkedin-home-feed-v1` retains digest
  `sha256:9238e351363d0e4d37fa965c748df53012ae9a217231901fef60a720413ad417`.
  X and LinkedIn feeds remain enabled, Reddit and Facebook remain disabled,
  and YouTube is unchanged;
- `canary-x-feed-40-c28` and `canary-linkedin-feed-40-c28` remain disabled at
  version 1. The daily schedule remains ready with next boundary
  `2026-09-02T00:00:00Z`;
- Agent Browser reports one compatible live browser for the exact profile,
  zero active leases, no duplicate pressure, no blocking identity axes,
  lifecycle `ready`, owner generation 69, and
  `recommended_action=reuse_existing_browser`;
- SQLite `quick_check` is `ok` for `research.db`, `service.db`, and
  `service.sqlite3`;
- the 80+80 retrieval capability is proven live, but installed X policy still
  caps explicit requests at 32 scrolls and produced only 78 in its unmodified
  attempt. Persistently supporting this exact target requires a separately
  reviewed X budget change.

