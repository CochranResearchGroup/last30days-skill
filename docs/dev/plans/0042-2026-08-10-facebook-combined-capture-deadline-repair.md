# Plan 0042 | Facebook Combined Capture Deadline Repair

State: OPEN
Roadmap: P18
Plan version: 3
Date: 2026-08-10
Predecessor: Plan 0041 version 4/checkpoint P0041-C04

## Objective

Give the one replacement Facebook query capture enough of the already-approved
adapter budget to complete, while preserving the single-capture, one-successor,
profile, auth, challenge, rate-limit, and no-retry contracts.

## Current State

- service 0.3.45 from pushed commit `150b9d7` is installed ready and MCP 4.0.3
  is compatible at database schema 16;
- Plan 0041's only live tick proved the late acquisition repair: it reused the
  retained browser, inventoried tabs, opened and navigated the exact successor,
  then failed only at the combined query capture after 26.708 seconds;
- `_evaluate_query_capture` currently caps the inner job at 25 seconds and the
  outer waiter at 30 seconds even though the Facebook adapter has 105 seconds
  beneath the unchanged 120-second parent wall. The failed run retained more
  than 50 seconds of unused budget;
- prior retained evidence includes both a successful identical final capture in
  2.332 seconds and deadline failures at roughly 25-30 seconds, making the
  current cap a falsifiable bottleneck rather than proof of logout, checkpoint,
  rate limit, or unusable page content;
- the failed packet is terminal and will not be retried. This successor changes
  the capture deadline contract, advances the service version, and permits one
  final Facebook-only acceptance attempt under the same source/profile limits.

## Scope

- add one red unit proving a 105-second client run gives combined capture a
  45-second inner job deadline inside a 50-second outer waiter;
- change only the combined-capture deadline constants; do not add commands,
  targets, retries, loops, or browser/profile effects;
- version, manifest, document, validate, commit, push, build, and install one
  service candidate;
- run one final Facebook-only tick for the same closed UTC interval after fresh
  service, access-plan, profile, database, schedule, and effect preflights;
- close on the first terminal success or failure and reconcile all authorities.

## Non-Goals

- no browser restart/close, profile reset, login, reauthentication, CAPTCHA,
  checkpoint, tab cleanup, agent-browser mutation, new extraction mechanism,
  provider fallback, schedule, notification, paid provider, model use, ranking,
  or database-schema change;
- no second Plan 0042 tick and no further autonomous successor if its single
  acceptance attempt fails at the same target/capture invariant.

## Acceptance Criteria

1. A focused test is red at 25/30 and green at exactly 45/50 for a client whose
   timeout and remaining run budget can safely cover it.
2. Existing one-capture, one-successor, prepared-result reuse, parent cleanup,
   wrong-profile, auth, challenge, rate-limit, and cross-source tests pass.
3. Service 0.3.46 version, manifest, changelog/configuration, package, Python,
   Go, compilation, generation, authority, and patch gates converge before
   install.
4. The exact pushed commit artifact installs once and reports ready,
   MCP-compatible service 0.3.46/schema 16 with the canonical contract digest.
5. One Facebook-only tick reaches a terminal receipt. Success requires accepted
   durable evidence, promoted Facebook success, and named-profile cache proof;
   failure retains the exact terminal operation sequence without retry.
6. Current and rollback databases pass integrity, the daily schedule is
   unchanged, the retained profile/browser is safe, and Git is aligned/clean.

## Definition Of Done

- criteria 1-6 have exact evidence or the plan closes terminally on its sole
  attempt with no further autonomous successor at the same invariant.

## Execution Bounds And Gates

- maximum work-unit attempts: 2; maximum review/rework cycles: 1; maximum
  hardening-only checkpoints: 1;
- one serialized primary-owned path, one service upgrade, and one Facebook-only
  tick after complete gates;
- the 45/50-second capture remains inside the existing 105-second adapter and
  120-second parent walls; no cost, request, item, or concurrency ceiling grows;
- stop without retry on auth, challenge, rate limit, wrong profile, ambiguous
  owner, unsafe route, browser restart need, integrity failure, or any terminal
  tick result.

## Work Graph

| Packet | Outcome | Depends on | Gate |
|---|---|---|---|
| B01 deadline red | Existing capture emits 25/30 instead of 45/50 | C01 | focused failing test |
| B02 repair | Deadline-only change, focused green | B01 | no command-count change |
| B03 candidate | 0.3.46 complete validation and source identity | B02 | pre-install gates |
| B04 acceptance | One terminal Facebook tick and cache proof | B03 | exact installed commit |
| B05 closeout | Runtime/Git/Graphiti reconciliation | B04 | terminal receipt |

### Checkpoint P0042-C01 | 2026-08-10

Plan version: 1

State transition:

- `terminal_capture_failure -> bounded_capture_deadline_repair`.

Progress classification:

- `blocker_reduction`; predecessor acquisition now works and the remaining
  failure is narrowed to a single under-allocated inner/outer capture boundary.

Validation evidence:

- exact installed provider attempt and operation timings are recorded above;
- current source fixes combined capture at 25,000 ms inside 30 seconds while
  105/120 seconds are already authorized; no new browser action is required;
- historical same-path success proves the capture can return valid evidence,
  while current and older failures cluster at the configured deadline.

Subagent status and reconciliation:

- `not_spawned`; user did not request delegation and the sole browser/profile
  lane remains serialized.

Authority classification:

- `inherited_authority`; goal governance treats the changed deadline strategy
  as one bounded successor inside the same system, source, profile, data,
  effect, cost, and cumulative two-attempt envelope.

Review disposition summary:

- `blocking=1` capture deadline mismatch; `needs_evidence=3` red/green,
  candidate, installed terminal tick; `rejected=0`; `nonblocking_backlog=0`.

Graphiti write status:

- pending terminal outcome; no duplicate intermediate episode is queued.

Next action:

- add and run the exact 45/50 deadline regression before changing source.

### Checkpoint P0042-C02 | 2026-08-10

Plan version: 2

State transition:

- `bounded_capture_deadline_repair -> source_candidate_implemented`.

Progress classification:

- `blocker_reduction`; the exact 25/30 deadline mismatch is red, and the only
  runtime change gives the same single capture 45/50 within unchanged parent
  budgets.

Validation evidence:

- the focused regression failed at the old 25,000 ms value and passes at
  exactly 45,000 ms inner/50 seconds outer;
- expanded Facebook, release, runtime-package, acquisition-worker, Reddit, and
  tick suites pass with 297 tests plus one expected skip;
- service version, runtime manifest, changelog, and configuration now converge
  at 0.3.46. No runtime install or browser effect has occurred.

Subagent status and reconciliation:

- `not_spawned`; all work remains serialized in the primary lane.

Graphiti write status:

- pending terminal installed outcome.

Authority classification:

- `inherited_authority`; the implementation changes only the deadline strategy
  already authorized by C01 and remains within every existing effect and
  resource ceiling.

Next action:

- run the complete pre-install validation gate and produce the exact candidate
  artifact before any installation.

### Checkpoint P0042-C03 | 2026-08-10

Plan version: 3

State transition:

- `source_candidate_implemented -> install_ready_candidate`.

Progress classification:

- `forward_progress`; all source, package, governance, and reproducibility gates
  pass for the bounded service 0.3.46 candidate.

Validation evidence:

- full Python gate: 2,649 passed, seven skipped, six subtests passed;
- Go `test ./...` and `vet ./...`, Python compileall, generated-contract
  freshness, authority audit, runtime build, and patch hygiene pass;
- runtime manifest SHA-256 is
  `9da5958a7e28e2857f533012954f97a8753f98eee8a292efc1e72519335d6e59`;
  reproducible service artifact SHA-256 is
  `b0d7d01e5a0cc89afcd142f2828cafe7ab4388c6a9191ac6f3a90fc5fdda8e51`.

Subagent status and reconciliation:

- `not_spawned`; the candidate and live lane remain primary-owned and
  serialized.

Graphiti write status:

- pending terminal installed outcome.

Authority classification:

- `inherited_authority`; the candidate exactly implements the authorized C01
  deadline strategy and has not yet created an external runtime effect.

Next action:

- commit and push service 0.3.46 source, rebuild the exact commit artifact, and
  perform the one supported upgrade only after fresh preflight.
