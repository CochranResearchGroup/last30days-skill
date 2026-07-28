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

### Checkpoint P0012-C03 | 2026-07-27

Plan version:

- 1

State transition:

- `authorized_blocked_route_preflight ->
  blocked_route_preflight_committed_pushed`

Progress classification:

- `outcome_progress`

Owned changes:

- receipt-only closeout for checkpoint commit, push, validation, and Graphiti
  terminal state.

Validation evidence:

- route-blocker checkpoint commit `2b26e23` is pushed to `origin/main`;
- planning authority audit passed with exactly Plan 0012 open and zero issues;
- `tests/test_plan_authority_audit.py` passed all four tests;
- `git diff --check` passed.

Subagent status and reconciliation:

- `not_spawned`; the checkpoint remained one coupled authority surface.

Graphiti write status:

- provider readiness passed;
- job `a1362f2a-c444-4b0e-abdf-5ba1ee97de71` was queued in
  `last30days_skill_main`;
- it reached `graphiti_extracting_edges` but timed out after its bounded
  180-second attempt with no episode UUID;
- the terminal job reports `retryable: false`. Do not enqueue a duplicate
  episode; inspect or explicitly recover this exact dead-letter job first.

Remaining acceptance criteria:

- unchanged from checkpoint P0012-C02.

Stop reason:

- the route packet is truthfully blocked and durably backed up; the next
  authorized work must be a bounded route-pool/display allocation repair, not
  a repeat of the failed route-open attempt.

### Checkpoint P0012-C04 | 2026-07-27

Plan version:

- 1

State transition:

- `blocked_route_preflight_committed_pushed ->
  route_recovery_diagnosed_awaiting_repair_authorization`

Progress classification:

- `blocker_reduction`

Owned changes:

- read-only diagnosis of the live Guacamole route substrate and the
  agent-browser convergence controller;
- agent-browser P78/Plan 0078 repair planning;
- last30days plan, roadmap, and runbook checkpoint receipts only.

Validation evidence:

- report-only route-pool readiness proved zero live Guacamole RDP connections,
  zero permissions, and next action
  `provision_second_guacamole_rdp_connection`;
- route-display inspection proved no live route displays or X11 sockets;
- PostgreSQL logs and filesystem timestamps bind a fresh `initdb` to
  2026-07-27 11:46:23 UTC; the reason the persistent bind directory was empty
  remains unresolved;
- the recurring agent-browser runtime interlock is enabled but its latest
  receipt is unsuccessful and selected no remedy;
- CodeGraph source tracing proved the convergence controller ensures schema
  readiness but does not handle the fixture-provisioning next action before
  its display-restoration branch;
- the remote-view preflight correctly failed closed before browser creation.

Failure classification:

- `route_fixture_recovery`;
- the stronger current evidence supersedes the narrower missing-display
  hypothesis while preserving the conclusion that this is not source
  authentication failure.

Successor repair authority:

- agent-browser
  `docs/dev/plans/0078-2026-07-27-guacamole-route-fixture-recovery-interlock-plan.md`;
- the packet is planned and requires explicit execution authorization before
  source, installed-runtime, or live route mutation.

Subagent status and reconciliation:

- `not_spawned`; diagnosis used CodeGraph and one serialized live route
  substrate, and no delegation was requested.

Graphiti write status:

- agent-browser Graphiti discovery was advisory and current repo/runtime
  evidence remained authoritative;
- closeout memory writes, if provider-ready, occur only after the planning
  commits are durable and must not duplicate the non-retryable Plan 0012
  blocker episode.

Remaining acceptance criteria:

- unchanged from checkpoint P0012-C02.

Stop reason:

- Plan 0012 prohibits source-code repair and another route attempt in this
  packet. P78/Plan 0078 must be separately authorized, implemented, and prove
  ready remote control before Plan 0012 can request a new route-open
  authorization.

Next action:

- review and explicitly authorize agent-browser Plan 0078 Packet A; do not
  provision routes, open displays, launch a browser, or run canaries yet.

### Checkpoint P0012-C05 | 2026-07-27

Plan version:

- 1

State transition:

- `route_recovery_diagnosed_awaiting_repair_authorization ->
  repair_plan_committed_pushed_awaiting_authorization`

Progress classification:

- `outcome_progress`

Owned changes:

- receipt-only closeout for the cross-repo planning commits, push parity,
  focused validation, and Graphiti terminal result.

Validation evidence:

- agent-browser P78/Plan 0078 is committed and pushed at `6d5cc908`;
- this Plan 0012 diagnosis checkpoint is committed and pushed at `e7c2368`;
- both repositories were clean and local, tracking, and remote main refs
  agreed after push;
- the last30days planning authority audit passed with exactly Plan 0012 open
  and zero issues;
- all four `tests/test_plan_authority_audit.py` tests passed;
- agent-browser local-runtime convergence and Guacamole PostgreSQL hardening
  guards passed;
- `git diff --check` passed in both repositories.

Subagent status and reconciliation:

- `not_spawned`; the receipt closeout remained one cross-repo authority
  reconciliation surface.

Graphiti write status:

- provider readiness passed;
- job `6022b120-eb35-4bd9-8a50-0079a40b3782` completed in one attempt;
- episode `2e3a6d86-3d53-40b0-b4c9-0db6398d9264` is read-after-write visible in
  `agent_browser_main` and bound to Plan 0078 commit `6d5cc908`;
- no duplicate Plan 0012 blocker episode was queued in
  `last30days_skill_main`.

Remaining acceptance criteria:

- unchanged from checkpoint P0012-C02.

Stop reason:

- diagnosis and successor repair planning are durable, but Plan 0078 execution
  and all live repair remain explicitly unauthorized.

Next action:

- explicitly authorize agent-browser Plan 0078 Packet A, then implement its
  deterministic controller regression before any live fixture recovery.

### Checkpoint P0012-C06 | 2026-07-28

Plan version:

- 1

State transition:

- `repair_plan_committed_pushed_awaiting_authorization ->
  repaired_substrate_verified_route_selection_drift`

Progress classification:

- `blocker_reduction`

Owned changes:

- read-only verification of the repaired agent-browser install, recurring
  interlock, Guacamole route fixtures, route displays, canonical profile, and
  last30days service;
- one explicitly authorized service reconciliation and one explicitly
  authorized route-open attempt;
- Plan 0012, roadmap, and runbook checkpoint receipts only.

Validation evidence:

- agent-browser source, tracking, and remote `main` agree at `76d30999`;
- installed agent-browser reports version `0.27.0`, all seven discovered
  runtimes are converged on the installed executable, and the latest recurring
  interlock completed successfully;
- report-only route readiness is `ready`; route A is live as
  `agent-browser-rdp-a` on `:11`, route B is live as
  `agent-browser-rdp-b` on `:12`, and both displays pass `xdpyinfo`;
- the remote-view doctor reports `status: ready`, `routeId: guacamole:1`,
  `routePoolEntryId: guacamole-rdp-a`, and `displayName: :11`;
- the canonical service profile ID `last30days-facebook` still selects
  `/home/ecochran76/.agent-browser/runtime-profiles/last30days-facebook/user-data`,
  `stealthcdp_chromium`, and X, Facebook, and LinkedIn target readiness;
- installed last30days remains ready at version `0.2.7`, database schema 12;
- the three reserved request IDs remain absent from `service_jobs`;
- the one route-open attempt failed before browser launch because the retained
  selector chose legacy `guacamole:4` with
  `remote-view-display:10`; the display-access helper exited 1 and the lease
  rollback completed;
- the post-failure doctor still selects the live doctor-proven
  `guacamole:1`/`:11` route, while retained service history maps
  `guacamole-rdp-a` to multiple route IDs including `guacamole:4`.

Failure classification:

- `route_selection_state_drift`;
- this is not evidence of X, Facebook, or LinkedIn authentication failure.

Subagent status and reconciliation:

- `not_spawned`; the user requested one serialized retry and Plan 0012 keeps
  one shared-browser critical path.

Graphiti write status:

- provider readiness passed after checkpoint commit `51291e4` was pushed;
- job `35f288b7-7bc6-4419-816e-1f5f00692b47` was queued in
  `last30days_skill_main`;
- it timed out after its bounded 180-second attempt during
  `graphiti_resolving_nodes`, returned no episode UUID, and reports
  `retryable: false`;
- do not enqueue a duplicate; inspect or explicitly recover this exact
  dead-letter job first.

Remaining acceptance criteria:

- prove one canonical live display, route, and operator-visible remote view;
- run signal-only X, Facebook, and LinkedIn authentication probes;
- run one terminal serialized canary for each source and preserve publication
  receipts.

Stop reason:

- Plan 0012 permits one route attempt and requires stopping at the first typed
  failure. No second route open, browser, DOM probe, login action, acquisition
  request, or timer mutation is authorized in this packet.

Next action:

- repair or explicitly override the route-open selector so
  `guacamole-rdp-a` resolves to the current doctor-proven
  `guacamole:1`/`:11` fixture, validate that normal selection path, then
  authorize one new Plan 0012 route attempt.
