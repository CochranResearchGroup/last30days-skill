# Plan 0040 | X Agent-Browser Boundary Recovery

State: OPEN
Roadmap: P16
Plan version: 2
Date: 2026-08-10
Predecessor: Plan 0039 version 4/checkpoint P0039-C04

## Objective

Recover the exact last30days-to-agent-browser X acquisition boundary so one
tested, profile-safe X attempt either publishes correctly attributed evidence
or closes on a newly retained terminal source condition without retry.

## Current State

- local `main`, `origin/main`, and closeout commit
  `bfc7e4369f905c7e36d548c317ee54b8bb976bfa` align with a clean worktree;
- installed service 0.3.44/schema 16 is ready at `releases/0.3.44` with runtime
  manifest SHA-256
  `c63fe7e8ae771210f1ab91e9d226d0dcab0187e52094b729be5f9716880465bd`
  and canonical contract SHA-256
  `fe8727fbe0d4e2f6775f49a6fc958369fe4877ba812bae4ef69121b88f12e2f1`;
- Plan 0039's sole X tick `tick-e15b1ed57efbb0c618253ecd90429295`
  retained provider attempt `provider-attempt-69155789e4000dbd795a7fb1f586e006`
  as transient `agent_browser_error` before any browser operation or page
  signal, with zero candidates and no retry;
- fresh read-only agent-browser job/event/incident queries show no matching
  failed control-plane action at that tick boundary. The failure therefore
  remains upstream of an accepted service-owned browser operation until a
  red-capable replay proves otherwise;
- the replay is now red: runtime profile `last30days-facebook` claims
  `browserAlive=true` for PID 63205 even though that PID belongs to Codex and
  DevTools port 37539 is unreachable. The retained Chromium `SingletonLock`
  also names PID 63205;
- fresh CodeGraph source proves agent-browser runtime and profile-lock checks
  use `kill(pid, 0)` without process identity or DevTools validation. PID reuse
  therefore turns a stale authenticated-profile lock into a false live owner.
  The required repair is in the agent-browser repository, outside this plan's
  write authority; the X attempt remains unconsumed at a human scope gate.

## Scope

- trace the exact worker -> X adapter -> agent-browser subprocess path and
  retain a bounded local diagnostic cause without leaking subprocess output;
- build and run one deterministic red-capable replay at the narrowest seam
  before choosing a repair;
- rank and test falsifiable hypotheses one prediction at a time;
- implement the smallest last30days-owned repair and regression needed by the
  proven cause, with release/install changes only if shipped runtime code moves;
- after all pre-effect gates pass, consume at most one new X-only service tick
  through the existing profile and source lane;
- reconcile repository, installed runtime, database, schedule, browser lease,
  query receipt, planning authority, Git, and durable-memory closeout evidence.

## Non-Goals

- no browser credential, profile, login, reauthentication, CAPTCHA, checkpoint,
  schedule, timer, notification, paid provider, ranking, or database-schema
  change;
- no mutation in the agent-browser repository or installed agent-browser
  service. If the proven defect lies there, stop with the exact cross-repo
  blocker and request separate authority;
- no unrelated retained-browser cleanup, process termination, historical row
  rewrite, provider fallback, Facebook/LinkedIn/Reddit/YouTube acquisition,
  Git tag, GitHub release, or pull request;
- no second X attempt, including after auth, challenge, rate-limit, ownership,
  budget, deadline, unsafe-route, or terminal content failure.

## Acceptance Criteria

1. A deterministic, fast, agent-runnable replay is observed red on the same
   adapter boundary and exposes a bounded internal cause while preserving the
   public safe error contract.
2. Three to five falsifiable hypotheses are ranked from current evidence and
   tested one prediction at a time; disproved causes remain recorded.
3. The smallest last30days-owned repair has a focused regression that fails
   before and passes after the change, without widening browser/profile scope.
4. Focused tests, applicable full Python and Go suites, contract generation,
   compilation, release/runtime locks, formatting, planning/goal/authority
   audits, and patch hygiene pass before any installation or X attempt.
5. Any changed shipped service/MCP artifact is committed and pushed before one
   bounded install; unchanged artifacts are not reinstalled.
6. Fresh access planning selects the existing authenticated X profile with no
   manual action, duplicate lane, unsafe destination, or provider fallback.
7. At most one X-only service tick reaches a terminal receipt. Success proves
   stable status identity, exact rejection accounting, durable source rows,
   and profile-authorized cache retrieval; failure retains the exact terminal
   cause and newest-source coverage gap without retry.
8. Current and rollback databases pass integrity checks, the recurring
   schedule is unchanged, the retained profile lease is safe, and local
   `main == origin/main` with a clean worktree at closeout.

## Definition Of Done

- criteria 1-8 have exact test, trace, receipt, runtime, identity, query,
  integrity, commit, and push evidence, or this plan closes blocked at the
  explicit cross-repo authority boundary;
- P16 and this plan close only after the one-attempt boundary has a terminal
  disposition and every safe closeout check is reconciled.

## Execution Bounds And Gates

- maximum work-unit attempts: 2; maximum review/rework cycles: 1; maximum
  consecutive hardening-only checkpoints: 2;
- the first live-effect packet may use a non-X no-launch/read-only preflight;
  the only X acquisition effect is one X-only service tick after validation;
- one service install is authorized only if the shipped service changes; one
  MCP install is authorized only if its shipped adapter changes;
- stop without retry on login, checkpoint, CAPTCHA, rate limit, wrong profile,
  unsafe destination, ownership ambiguity, external-repo defect, deadline or
  budget exhaustion, provider fallback, database integrity failure, or need
  for a second X attempt;
- the primary agent owns all code, install, live-effect, reconciliation, and
  closeout boundaries. No subagent is spawned under the current execution
  instruction.

## Ranked Initial Hypotheses

1. **Confirmed:** stale managed-runtime and Chromium lock metadata names a PID
   now reused by an unrelated process; PID-only liveness falsely blocks launch
   before the first accepted browser action.
2. **Disproved:** the service subprocess PATH resolves the same executable,
   `/home/ecochran76/.local/bin/agent-browser` 0.28.0.
3. **Disproved:** the exact X access-plan argument set succeeds under the
   installed service's minimal environment and selects the intended profile.
4. **Not causal:** the exact remote-view dry-run and capability preflight pass;
   they do not execute the profile-lock check reached by live launch.

## Work Graph

| Packet | Outcome | Depends on | Gate |
|---|---|---|---|
| B01 red replay | Exact adapter-boundary failure and bounded cause | C01 | deterministic red command/test |
| B02 diagnosis | One ranked hypothesis confirmed; others disproved | B01 | single-prediction traces |
| B03 repair | Smallest last30days-owned fix and regression | B02 | focused red/green suite |
| B04 candidate | Broad validation and version/install decision | B03 | complete pre-effect gate |
| B05 acceptance | At most one X-only terminal tick and cache proof | B04 | fresh preflight and receipts |
| B06 closeout | Runtime/Git/authority/Graphiti reconciliation | B05 | clean deterministic audits |

All packets remain on one serialized critical path because they share the sole
browser/profile lane and one-attempt effect budget.

## Validation Plan

- exact adapter replay with controlled subprocess fixtures and bounded error
  assertions; focused `test_x_browser` and acquisition-worker regressions;
- unchanged-source checks for service contracts and query/cache behavior;
- applicable complete Python/Go, generation, compile, formatting, release,
  runtime, policy, authority, and diff gates;
- pre/post effect service identity, access plan, provider preflight, tick and
  provider rows, snapshot/source rows, cache-only query, database integrity,
  schedule, retained-browser resources, Git ancestry, and worktree readbacks.

### Checkpoint P0040-C01 | 2026-08-10

Plan version: 1

State transition:

- `installed_terminal_live_blocker -> bounded_boundary_diagnostic`.

Progress classification:

- `outcome_progress`; the operator authorized a bounded successor, the closed
  predecessor remains immutable, and read-only service history narrows the
  first red replay to the subprocess adapter before accepted browser work.

Validation evidence:

- clean `main == origin/main` at
  `bfc7e4369f905c7e36d548c317ee54b8bb976bfa`;
- installed service diagnose reports ready 0.3.44/schema 16 and the canonical
  release/runtime/contract identities above;
- retained agent-browser jobs/events/incidents since the failed tick contain no
  corresponding failed last30days control-plane action.

Subagent status and reconciliation:

- `not_spawned`; current execution instructions keep this serialized diagnosis
  with the primary agent.

Authority classification:

- `inherited_authority`; the operator's `ok go` authorizes this successor and
  at most one new X-only acceptance attempt after a tested repair.

Review disposition summary:

- `blocking=1` unclassified adapter-boundary failure;
  `needs_evidence=3` red replay, confirmed cause, terminal acceptance;
  `nonblocking_backlog=0`, `rejected=0`.

Graphiti write status:

- pending a validated diagnostic or terminal outcome in group
  `last30days_skill_main`; repository and retained runtime evidence remain
  authoritative.

Next action:

- run the deterministic adapter replay red, then test the ranked hypotheses one
  prediction at a time without consuming the X acceptance attempt.

### Checkpoint P0040-C02 | 2026-08-10

Plan version: 2

State transition:

- `bounded_boundary_diagnostic -> confirmed_external_repository_defect`.

Progress classification:

- `outcome_progress`; the failure is no longer a generic adapter error. Exact
  runtime state, OS identity, lock metadata, and source agree on PID-reuse
  misclassification in agent-browser's managed-profile lock boundary.

Validation evidence:

- the deterministic no-launch predicate requiring a non-live runtime or
  reachable DevTools exits 1: agent-browser reports `browserAlive=true` and
  `devtoolsReachable=false` for profile `last30days-facebook`;
- PID 63205 accepts signal 0 but `/proc/63205/cmdline` identifies Codex, while
  the profile's runtime-state and `SingletonLock` still identify 63205 as the
  historical browser PID and port 37539 has no listener;
- CodeGraph source shows `runtime_status_with_user_data_dir`,
  `ensure_profile_not_in_use`, and `cleanup_stale_profile_lock` depend on
  `kill(pid, 0)` liveness. The first two accept the reused PID as live and the
  cleanup path refuses to remove the stale lock;
- exact service-environment PATH, X access plan, browser-capability preflight,
  and remote-view dry-run all pass. No browser launch, X request, install,
  cleanup, database change, or schedule change occurred.

Subagent status and reconciliation:

- `not_spawned`; diagnosis stayed on the serialized critical path.

Authority classification:

- `scope_expansion`; repairing PID/process-identity validation and
  stale lock cleanup requires writes and validation in
  `/home/ecochran76/workspace.local/agent-browser`, which this plan explicitly
  excluded and the operator has not separately authorized.

Review disposition summary:

- `blocking=1 confirmed_external_repository_defect`;
  `rejected=2` PATH and access-plan causes;
  `needs_evidence=2` cross-repo repair and one terminal X acceptance;
  `nonblocking_backlog=0`.

Graphiti write status:

- pending the repair or terminal blocked closeout; exact repository and runtime
  evidence is retained here without speculative memory writes.

Next action:

- obtain operator authority for the agent-browser repair, or close P16 at this
  exact external-repository gate without consuming the X attempt.
