# Plan 0058 | X And LinkedIn Feed Throughput Repair

State: OPEN
Roadmap: P08
Plan version: 2
Date: 2026-08-31

## Objective

Raise bounded authenticated home-feed retrieval from the measured X 24/40 and
LinkedIn 12/40 baseline by scaling X's explicit feed scroll allowance and by
letting LinkedIn renew a stagnant virtualized snapshot without depending on an
exact refresh control, then install the successor and run one schedule-disabled
40+40 canary.

## Current State

- `main` and `origin/main` begin synchronized at
  `0da32d8574c0d34909b03c92c6cad61c9e412d5f` with a clean worktree;
- Plan 0057/C29 is terminal and remains closed. Its direct authenticated proof
  accepted 24 unique canonical X posts after the fixed eight-scroll ceiling and
  12 unique canonical LinkedIn posts after four stagnant snapshots; LinkedIn
  also rejected four unique sponsored ads deterministically;
- auth, checkpoint, and rate-limit evidence were negative for both providers;
  X rejected only duplicate instances, while LinkedIn had no exact `See new
  posts` control to enter its existing renewal path;
- recurring source configuration remains out of scope: X and LinkedIn stay
  enabled, Reddit and Facebook stay disabled, and YouTube is unchanged.

## Scope

- add provider-free regressions for a 40-item X feed whose accepted yield needs
  more than eight scrolls;
- make the explicit X feed scroll budget scale conservatively with requested
  accepted yield while keeping a finite maximum and the stagnation stop;
- add provider-free regressions for a LinkedIn feed that reaches four stagnant
  snapshots without an exact refresh control but exposes later posts after a
  bounded feed renewal;
- replace LinkedIn's one-shot refresh tail with a finite snapshot-epoch loop
  that preserves the global scroll budget, auth/rate-limit gates, positive post
  ownership, canonical dedupe, and deterministic ad rejection;
- expose snapshot-renewal counts in diagnostics;
- validate, version, install, and run exactly one disabled 40-item canary for X
  and one for LinkedIn through the existing authenticated profile.

## Non-Goals

- semantic relevance or quality filtering;
- changes to recurring schedules, source enablement, or profile identity;
- new browser profiles, browser-runtime repairs, or adjudication of the known
  Agent Browser revision race;
- relaxing canonical permalink, post-ownership, ad, spam, auth, checkpoint, or
  rate-limit gates.

## Definition Of Done

1. A provider-free X fixture requiring more than eight scrolls reaches 40
   unique canonical accepted posts within a finite explicit-feed maximum.
2. Existing X stagnation and search-surface budget behavior remain green.
3. A provider-free LinkedIn fixture with no exact refresh control crosses a
   stagnant snapshot boundary and reaches 40 unique canonical accepted posts.
4. LinkedIn renewal consumes one global finite scroll budget and reports click
   versus reload renewal diagnostics.
5. Focused, affected, canonical, compilation, packaging, and governance gates
   pass for an exact versioned successor.
6. The exact successor is transactionally installed and reports ready and MCP
   compatible on schema 16.
7. One newly authorized schedule-disabled 40+40 live canary is reconciled with
   exact accepted counts and deterministic rejection reasons; a below-ceiling
   result is reported truthfully and does not trigger an unbounded retry.
8. Recurring source configuration and the existing authenticated profile remain
   unchanged.

## Execution

1. Record failing public-behavior regressions for the two measured stop modes.
2. Implement the smallest finite budget and snapshot-state-machine changes.
3. Run focused and full validation, then version and transactionally install the
   successor.
4. Run one 40+40 canary and reconcile source-local evidence.
5. Close the plan and P08 only after the exact receipt, Git, and runtime state
   are recorded.

### Checkpoint P0058-C01 | 2026-08-31

State: `retrieval_throughput_red_loop_open`

Plan version:

- 1

Authority classification:

- `inherited_authority`

- opened this successor rather than reopening terminal Plan 0057;
- ranked the fixed X eight-scroll ceiling and LinkedIn's exact-control-gated
  stagnant-snapshot stop as the leading falsifiable causes;
- no production code, installed runtime, recurring configuration, provider
  state, or browser identity has changed at this checkpoint.

### Checkpoint P0058-C02 | 2026-08-31

State: `successor_runtime_candidate_validated`

Plan version:

- 2

Authority classification:

- `inherited_authority`

- the X regression failed at 28/40 under the prior fixed eight-scroll ceiling
  and passes at 40/40 after scaling the 40-item feed request to 14 scrolls;
- the LinkedIn regression failed at 10/40 when four stagnant snapshots had no
  exact refresh control and passes at 40/40 after one bounded same-feed reload;
- LinkedIn keeps one 32-scroll global budget across at most three renewals,
  stops when a renewal adds no new observation, and reports renewal, refresh,
  and reload counts without changing acceptance gates;
- service 0.3.88 and its canonical runtime manifest are prepared. Complete X
  and LinkedIn suites, the full Python suite, release/lifecycle suites, MCP Go
  tests, compilation, authority audit, artifact build, and diff checks pass;
- the exact candidate is not yet installed and no live provider attempt has
  been consumed. Recurring configuration and browser state remain unchanged.
