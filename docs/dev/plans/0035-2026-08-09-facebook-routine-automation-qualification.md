# Plan 0035 | Facebook Routine Automation Qualification

State: CLOSED
Roadmap: P13
Plan version: 3
Date: 2026-08-09
Predecessor: Plan 0034 version 3/checkpoint P0034-C03

## Objective

Prove installed service 0.3.38 can acquire accepted Facebook content through
one bounded governed manual tick, then qualify the already-enabled
`daily-default` schedule as the recurring automated Facebook path without
waiting for the next natural boundary.

## Current State

- service 0.3.38/schema16 is installed ready and reports Facebook configured,
  acquisition-ready, and indexed;
- `daily-default` is already enabled and ready at an 86,400-second UTC cadence;
  its frozen config contains one enabled Facebook target and the scheduler
  calls the same `TickCoordinator.enqueue_tick()` path as manual enqueue;
- the latest automatic tick at the 2026-08-09 UTC boundary included Facebook
  but failed before the 0.3.38 repair, so recurrence is configured but Facebook
  content capability is not qualified;
- retained browser `session:last30days-facebook`, PID 63205, is ready with one
  Facebook home target plus X, LinkedIn, and preview targets. A separate
  `shared-social` browser also exposes a Facebook tab, but the exact Last30Days
  owner remains unambiguous and remote-view readiness classifies the retained
  duplicate pressure as nonblocking with zero readiness-impacting candidates;
- Plan 0034 installed deterministic repairs for the two Plan 0033 target-loss
  traces and directly proved the retained Facebook home target has complete,
  authenticated DOM state. No post-repair provider tick has run.

## Scope

- bind one new operator-authorized Facebook-only attempt to a distinct fully
  closed interval and matching preflight;
- preserve one provider attempt, 50 network requests, 120 wall seconds, three
  items, zero cost, and zero model-token limits;
- require current service, SQLite, schedule, browser, exact-owner, target,
  challenge, queue, lease, and remote-control guards before enqueue;
- execute the one manual tick through the installed coordinator/runner and
  adjudicate its durable provider receipt against the accepted-content model;
- if and only if accepted Facebook content is persisted with coherent
  provenance and no safety signal, leave the existing `daily-default` schedule
  enabled and record Facebook as routine automated; no schedule mutation is
  needed because Facebook is already an enabled target;
- close with exact runtime, database, browser, schedule, Git, and receipt
  evidence.

## Non-Goals

- no second provider attempt, same-tick retry, provider fallback, natural-time
  wait, cadence/config/limit change, browser process close, unrelated-tab
  cleanup, logout/login, MFA, CAPTCHA/checkpoint interaction, cookie mutation,
  intentional rate-limit generation, private content dump, cost, or model use;
- no claim that configured recurrence alone proves usable scraping;
- no weakening of exact owner/profile/target, auth, challenge, rate-limit,
  quality, provenance, or one-final-Facebook-target gates.

## Acceptance Criteria

1. Fresh guards prove installed 0.3.38/schema16 ready; both SQLite databases
   `ok`; `daily-default` enabled/ready at 86,400 seconds; exact retained owner
   PID 63205 ready with one Facebook target; zero active challenges, queue
   depth, and profile-lease waiters; and effective remote control ready.
2. One matching preflight predicts exactly one Facebook lane, provider, and
   attempt with limits 50 requests, 120 wall seconds, three items, zero cost,
   and zero model tokens for a distinct fully closed interval.
3. The tick runs once and returns one terminal provider result. Routine
   qualification requires `success` or `partial` with at least one accepted
   post, a canonical Facebook permalink, in-window publication time, coherent
   observed/accepted/rejected counts, persisted source version/sighting/index
   evidence, and no auth, CAPTCHA, checkpoint, rate-limit, integrity, or
   quality-only-zero-yield signal.
4. After success, the authoritative config still has Facebook enabled under
   `daily-default`, the schedule remains enabled/ready with the same cadence
   and next boundary, and CodeGraph-backed source evidence confirms timer and
   manual triggers converge on `TickCoordinator.enqueue_tick()` and the same
   adapter registry.
5. Browser cleanup preserves PID 63205 and one Last30Days Facebook target;
   databases remain `ok`; queue and lease pressure return to zero; plan,
   roadmap, runbook, receipt, Git, and runtime agree.

## Definition Of Done

- criteria 1-5 have exact IDs, counters, timestamps, hashes, and current
  readbacks;
- P13 closes only if accepted Facebook content proves the installed adapter
  and the existing daily schedule remains ready; otherwise the one-attempt
  blocker is preserved and recurrence is not described as usable;
- the coherent closeout is committed and pushed to `origin/main` and one
  compact Graphiti episode is attempted after provider readiness.

## Execution Bounds

- primary agent owns one serialized preflight/enqueue/adjudication packet;
- maximum work-unit attempts: one live Facebook provider attempt;
- maximum review/rework cycles: one closed-world receipt verification;
- maximum consecutive hardening-only checkpoints: zero;
- hard stop on failed guard, owner ambiguity, auth/challenge/rate-limit signal,
  nonzero cost/model use, unexpected tab growth, timeout/integrity/quality-only
  zero yield, or any need to mutate the schedule/config/browser lifecycle;
- no subagent is used; the deterministic runner remains bounded by the frozen
  tick contract and the primary independently inspects the durable outcome.

## Owned Write Surfaces

- one new tick/provider receipt in the installed current database;
- this plan, P13 in `ROADMAP.md`, `RUNBOOK.md`, the deterministic authority
  test while the plan is active, and one bounded closeout note if needed.

### Checkpoint P0035-C01 | 2026-08-09

Plan version: 1

State transition:

- `post_repair_manual_gate -> bounded_routine_qualification_ready`.

Progress classification:

- `outcome_progress`; the new authority binds the first post-0.3.38 content
  proof and recognizes that recurring Facebook configuration already exists.

Owned changes:

- opened and wired Plan 0035; no provider, browser, schedule, or configuration
  mutation has occurred.

Validation evidence:

- main and `origin/main` both began at `f19699c` with a clean worktree;
- installed status is ready at 0.3.38/schema16; `daily-default` is enabled and
  ready with next boundary `2026-08-10T00:00:00Z`;
- the 2026-08-09 automatic receipt contains one Facebook lane, proving the
  schedule currently includes Facebook, while CodeGraph shows timer admission
  calls the same `TickCoordinator.enqueue_tick()` used by manual enqueue;
- retained owner PID 63205 is ready with four live tabs and one Facebook home
  target; effective remote control is ready.

Subagent status and reconciliation:

- `not_spawned`; the primary owns the serialized effect boundary.

Authority classification:

- `human_gate`; the operator's active goal authorizes one new bounded
  Facebook-only post-repair proof and routine automation qualification.

Review disposition summary:

- no open review findings; configured recurrence is accepted only as setup
  evidence, not as content-success evidence.

Graphiti write status:

- deferred until the effect-bearing packet reaches a durable terminal state.

Remaining acceptance criteria:

- criteria 1-5 require fresh guards, the one live receipt, and closeout.

Next action:

- commit and push this authority checkpoint, then run fresh guards and the one
  matching Facebook-only preflight/enqueue pair if every guard passes.

## Stop Rules

Stop immediately on any execution-bound violation. One failed provider result
is terminal for this plan; diagnose from its durable receipt but do not infer a
second attempt or schedule/browser mutation.

### Checkpoint P0035-C02 | 2026-08-09

Plan version: 2

State transition:

- `bounded_routine_qualification_ready -> live_effect_ready`.

Progress classification:

- `blocker_reduction`; every pre-effect invariant now has a current readback
  and the prospective tick is distinct, fully closed, and exactly scoped.

Owned changes:

- no runtime mutation; one preflight created no state and predicted the frozen
  Facebook-only effect boundary.

Validation evidence:

- installed 0.3.38/schema16 is ready with Facebook configured,
  acquisition-ready, and indexed; runtime manifest is
  `99b2e4c1db862a99855430929d82d5ae5bc5ae092332cf035299e8b337da59b4`;
- current and rollback SQLite quick checks are `ok`;
- `daily-default` remains enabled/ready at 86,400 seconds with next boundary
  `2026-08-10T00:00:00Z` and no runtime error;
- browser `session:last30days-facebook`, PID 63205, is ready with
  `lastError=null`, one Facebook home target and four intentional live tabs;
  active challenge, queued job, running job, and waiting profile-lease counts
  are zero at the final guard;
- preflight `tick-527ad0a718cb64e9f362f4921cbd2498` covers
  `[2026-08-08T23:00:00Z, 2026-08-09T23:00:00Z)`, predicts exactly lane
  `tick-lane-091f683ba5da383c3f017c2e4e0c3639`, adapter
  `facebook_agent_browser`, one attempt, 50 requests, 120 seconds, three
  items, zero cost, and zero model tokens.

Subagent status and reconciliation:

- `not_spawned`; the primary independently read every guard and owns the
  single enqueue.

Authority classification:

- `inherited_authority`; the enqueue is the exact bounded effect described by
  C01 and crosses no new source, tenant, limit, or safety boundary.

Review disposition summary:

- `blocking=0`, `nonblocking_backlog=0`, `rejected=0`, `needs_evidence=0`;
  the separately owned `shared-social` browser is preserved and excluded.

Graphiti write status:

- deferred until terminal receipt adjudication.

Remaining acceptance criteria:

- execute the one matching enqueue, adjudicate its receipt, and verify
  post-effect schedule/browser/database state.

Next action:

- enqueue `tick-527ad0a718cb64e9f362f4921cbd2498` exactly once with the
  matching interval, schedule ID, and `--service facebook`; poll only its
  durable receipt and do not retry.

### Checkpoint P0035-C03 | 2026-08-09

Plan version: 3

State transition:

- `live_effect_ready -> tab_inventory_latency_blocker`.

Progress classification:

- `blocker_discovery`; the sole post-0.3.38 proof ruled out content success
  and isolated the failure before page evaluation to the session tab inventory.

Owned changes:

- enqueued the exact C02 tick once and wrote one terminal provider receipt;
  no retry, schedule/config mutation, browser lifecycle change, challenge
  action, cost, or model use occurred.

Validation evidence:

- tick `tick-527ad0a718cb64e9f362f4921cbd2498`, execution attempt
  `tick-attempt-c71b2211114969b15919fe2679175443`, and provider attempt
  `provider-attempt-746e9438cb50a275aa04bd6572bcc74c` ended
  `complete_degraded` with safe code `agent_browser_timeout` after 26 seconds;
- the provider used one request and persisted zero observed, accepted,
  rejected, or quality-rejected candidates, zero items, zero cost, and zero
  model tokens. It emitted no auth, CAPTCHA, checkpoint, rate-limit, page, or
  operator-handoff signal;
- its operation ledger is `service=ok/716ms`, `service=ok/4252ms`, then
  `tab=timed_out/10025ms`, proving the 10-second tab inventory deadline failed
  before Facebook DOM inspection;
- after termination, raw CDP discovery returned the intended Facebook target
  immediately. The exact `--session last30days-facebook tab list` command
  then succeeded four times without mutation; three consecutive measured
  probes took 8.4-8.8 seconds each, leaving inadequate jitter margin under the
  installed 10-second adapter deadline;
- an unscoped `--cdp` diagnostic separately failed because `shared-social`
  held the default runtime-profile lock. That is not treated as proof of the
  session-scoped tick failure because the exact session command remained
  correctly routed and responsive;
- `daily-default` remains configured with Facebook enabled. Recurrence is
  configured but not content-qualified, so routine usability is still false.

Subagent status and reconciliation:

- `not_spawned`; the primary ran the effect and independent read-only CDP and
  session diagnostics.

Authority classification:

- `inherited_authority`; receipt adjudication and read-only diagnosis remained
  inside the C02 effect boundary. The plan's one provider attempt is exhausted.

Review disposition summary:

- `blocking=1`: the fixed 10-second read-only inventory deadline is too close
  to the observed 8.4-8.8-second service latency;
- `rejected=1`: default-profile lock contamination is not yet accepted as the
  tick cause because exact session routing now succeeds;
- `needs_evidence=0`, `nonblocking_backlog=0`.

Graphiti write status:

- deferred to the bounded repair successor after its source-backed closeout.

Remaining acceptance criteria:

- criteria 3-5 are not satisfied. Plan 0036 owns the deterministic inventory
  budget repair, installed convergence, and a separately governed proof.

Next action:

- close this one-attempt authority and open Plan 0036. Do not retry the tick or
  change the existing recurring schedule.
