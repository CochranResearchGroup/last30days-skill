# Plan 0012 | Post-reboot social route and canary acceptance

State: OPEN
Roadmap: P03
Date: 2026-07-26
Predecessors: Plans 0002, 0009, and 0011

## Objective

Restore and prove the canonical retained profile's operator-visible
Guacamole/RDP route after reboot, then run one serialized X, Facebook, and
LinkedIn authentication and acquisition canary without converting a route
failure into a false account-authentication diagnosis.

## Current State

- The installed service is active and ready at version 0.2.7/schema 12.
- Identity-specific X, Facebook, and LinkedIn lookups select
  `last30days-facebook` with `authenticated_target`.
- The persisted profile appears intact, but no live retained browser or usable
  display route has been proved after reboot.
- The reviewed handoff contains exact read-only preflight, route, signal-only
  DOM probe, acquisition, polling, serialization, and stop commands.
- No live browser, route, login, authentication, acquisition, or timer mutation
  was authorized by the planning request that created this plan.

## Scope

- establish current service, profile, route, browser, display, and remote-view
  truth without navigation;
- stop at an explicit operator gate before route or browser mutation;
- reconcile the canonical profile once and prove one operator-visible
  Guacamole/RDP route;
- probe authentication using only signal counts and page identity, without
  returning private page text;
- submit at most one new single-use canary for X, Facebook, and LinkedIn, in
  that order, waiting for each terminal outcome before continuing;
- preserve job, acquisition, stage, operation, stable-signature, item,
  immutable-version, sighting, and projection receipts;
- classify a terminal failure as route recovery, authentication, adapter,
  publication, or quality gate.

## Non-Goals

- login, checkpoint, CAPTCHA, credential, cookie, message, invitation,
  connection, or account-setting action;
- profile cleanup, migration, or duplicate deletion;
- concurrent social acquisition;
- recurring authenticated timers;
- broad adapter repair or a second canary after a stable failure;
- treating service readiness, profile persistence, or a healthy process as
  proof of live route or source yield.

## Dependencies And Owned Surfaces

- Authority: `ROADMAP.md`, this plan, `RUNBOOK.md`, and
  `docs/dev/notes/2026-07-26-post-reboot-fresh-session-handoff.md`.
- Runtime dependencies: installed last30days service, canonical agent-browser
  profile, Guacamole/XRDP infrastructure, and current operator authorization.
- Expected writes: runtime route/browser state only after authorization,
  last30days job/acquisition ledgers, and closeout receipts in this plan and
  `RUNBOOK.md`.
- Source-code writes are not authorized by this packet. A verified code defect
  requires a successor repair plan.

## Deterministic And Stochastic Boundaries

- Deterministic supervisors own profile selection, route reconciliation,
  canary request identity, budgets, publication, terminal state, and evidence.
- Browser DOM inspection is signal-only and may not return private content.
- No App Intelligence worker may operate the browser, declare authentication,
  retry a failed job, or publish authoritative corpus state.

## Execution Graph

```text
S01 read-only preflight
  -> S02 explicit operator authorization gate
  -> S03 one route reconciliation and operator-visible proof
  -> S04 X signal probe and canary
  -> S05 Facebook signal probe and canary
  -> S06 LinkedIn signal probe and canary
  -> S07 durable receipt and closeout
```

Any unavailable route, proved auth gate, stable adapter signature, failed
publication, or nonterminal job at its bound transitions directly to a blocked
checkpoint. It does not loop to an earlier work unit.

## Execution Bounds

- maximum implementation attempts per work unit: 1;
- maximum review/rework cycles: 1;
- maximum consecutive hardening-only checkpoints: 1;
- checkpoint after preflight, before runtime mutation, and after every
  terminal source outcome;
- active-agent concurrency: 1; delegation decision is `not_spawned` because
  the shared retained profile and live route are a serialized critical path;
- one route reconcile and one new single-use request ID per source;
- no automatic retry, caller-ID reuse, or source continuation after the first
  stable failure.

## Gates And Stop Conditions

- Stop before S03 without explicit current-session operator authorization.
- Stop if route, browser, display, and operator-visible remote view do not
  agree.
- Stop and request operator action only when a live DOM probe proves a login or
  challenge surface.
- Stop after the first `failed` or `awaiting_operator` canary and preserve its
  complete safe evidence envelope.
- Stop rather than repair if source changes would exceed the documented write
  surface.
- Keep authenticated timers disabled throughout.

## Acceptance Criteria

- the exact canonical profile, browser/session, display, route, and remote-view
  identifiers agree and the route is operator-visible;
- each authorized source probe distinguishes authenticated, signed-out,
  challenge, ambiguous, and route-unavailable states without private text;
- X, Facebook, and LinkedIn each produce one terminal, uniquely keyed canary
  receipt in serialized order;
- successful canaries bind durable items to immutable versions, sightings, and
  the current projection/index receipt;
- failures retain enough stage and stable-signature evidence to classify the
  blocker without speculation or broad retry;
- commit, push, installed-service, and live-runtime states are reported
  separately.

## Validation

- run the planning authority audit before runtime work and at closeout;
- verify current Git and installed-service state independently;
- use the exact handoff command packet and single-use request IDs;
- inspect terminal jobs and durable publication records;
- run focused tests only if a successor code repair is separately authorized.

## Definition Of Done

The canonical route is operator-visible and all three serialized canaries
publish with durable evidence, or the plan is truthfully checkpointed as
blocked at the first typed terminal gate. No authenticated recurring timer is
left enabled.

## Initial Checkpoint

### Checkpoint P0012-C00 | 2026-07-26

Plan version:

- 1

State transition:

- `unplanned_handoff_packet -> ready_awaiting_operator_authorization`

Progress classification:

- `blocker_reduction`

Owned changes:

- successor plan and roadmap/runbook wiring only.

Validation evidence:

- post-reboot handoff review is repaired and pushed at `bab7271`;
- installed service readiness and canonical profile selection were verified;
- live route/display remains unproved after reboot.

Subagent status and reconciliation:

- `not_spawned`; planning authority is one coupled documentation surface and
  future runtime work is serialized through one shared browser.

Graphiti write status:

- required after this planning slice has a durable commit.

Remaining acceptance criteria:

- all S01-S07 criteria above.

Next action:

- obtain explicit operator authorization, then execute S01-S03 and stop at the
  first gate.

### Checkpoint P0012-C01 | 2026-07-26

Plan version:

- 1

State transition:

- `ready_awaiting_operator_authorization ->
  planning_committed_awaiting_operator_authorization`

Progress classification:

- `outcome_progress`

Owned changes:

- Plan 0002 closure, Plans 0012-0017, roadmap successor queue, and runbook
  planning/receipt entries.

Validation evidence:

- planning commit `d8e17a5` is pushed to `origin/main`;
- planning authority audit passed with exactly Plan 0012 open and zero issues;
- `tests/test_plan_authority_audit.py` passed all four tests;
- `git diff --check` passed;
- no live Plan 0012 runtime mutation was executed.

Subagent status and reconciliation:

- `not_spawned`; the planning authority stayed on one coupled documentation
  surface.

Graphiti write status:

- `graphiti_write_pending`;
- provider preflight passed, but job
  `b7148b8a-9777-4074-b550-5fac0a0538bd` timed out on its first bounded attempt
  and failed after one exact-job requeue because the Codex app-server exited
  without a response;
- no episode UUID was created. Verify that exact dead-letter state before any
  future retry and do not enqueue another write in this closeout.

Remaining acceptance criteria:

- all S01-S07 criteria above.

Next action:

- wait for explicit current-session operator authorization before executing
  Plan 0012 preflight and route work.

### Checkpoint P0012-C02 | 2026-07-27

Plan version:

- 1

State transition:

- `planning_committed_awaiting_operator_authorization ->
  authorized_blocked_route_preflight`

Progress classification:

- `blocker_reduction`

Owned changes:

- one read-only runtime preflight;
- one authorized service reconciliation;
- one authorized canonical route-open attempt;
- roadmap, plan, and runbook checkpoint receipts only.

Validation evidence:

- the planning authority audit passed with exactly Plan 0012 open and zero
  issues;
- local `main`, tracking `origin/main`, and the remote-tracking ref agreed at
  `d63e7c5` before runtime work;
- `last30days.service` was enabled, active, and ready at version 0.2.7/schema
  12 with 43 documents;
- identity-specific X, Facebook, and LinkedIn lookups each selected
  `last30days-facebook` with `authenticated_target`;
- the read-only remote-view doctor proved zero live RDP connections and zero
  accessible route displays while the Guacamole/XRDP backend and public
  ingress remained reachable;
- the single authorized `agent-browser service reconcile --json` completed
  and retained `guacamole:4` as orphaned because display `:10` had no socket;
- the single authorized route-open attempt failed before browser creation with
  `service_remote_view_route_preflight requires displayAllocationId, a browser
  with displayAllocationId, or an available route pool entry`;
- the post-failure profile readback still had zero browser IDs, zero session
  holders, `routeAvailable: false`, and recommendation `launch`;
- `last30days-social.timer` was not installed and was inactive.

Failure classification:

- `route_recovery`;
- this is not evidence of X, Facebook, or LinkedIn authentication failure.

Subagent status and reconciliation:

- `not_spawned`; Plan 0012 declares one serialized shared-browser critical
  path, and the operator did not request delegation.

Graphiti write status:

- required after this checkpoint has a durable commit;
- intended group: `last30days_skill_main`;
- intended episode: Plan 0012 stopped fail-closed at the post-reboot route
  preflight before browser or acquisition work.

Remaining acceptance criteria:

- prove one canonical live display, route, and operator-visible remote view;
- run signal-only X, Facebook, and LinkedIn authentication probes;
- run one terminal serialized canary for each source and preserve publication
  receipts.

Stop reason:

- the plan permits one route attempt and requires stopping at the first typed
  failure. No second route, browser, DOM probe, login action, or acquisition
  request is authorized in this packet.

Next action:

- diagnose and repair the missing route-pool/display allocation under a
  separately reviewed bounded packet, then resume Plan 0012 with new explicit
  authorization rather than retrying this attempt in place.
