# Plan 0022 | Reddit relevance machine-spaced canary

State: CLOSED
Roadmap: P07
Date: 2026-07-31
Plan version: 1
Predecessor: Plan 0021 checkpoint P0021-C03

## Objective

Repeat the four-case public Reddit relevance canary under a fresh operator
authorization, replacing human launch timing with a persistent controller that
enforces a 65-second monotonic start interval and pauses for manual relevance
adjudication between cases.

## Current State

- Plan 0020's complete meaningful-term coverage is implemented and validated
  at source commit `2af08b2`.
- Plan 0021 is cancelled and durably closed: C1 was relevant, C2's rejection
  evidence was timing-invalid, C3/C4 were not run, and cleanup passed.
- The operator explicitly authorized one adjusted retry packet on 2026-07-31.
- Source service 0.2.13 remains uninstalled; installed service 0.2.12 is outside
  this packet's mutation scope.

## Scope And Query Budget

Run exactly once, in order, through the working-tree
`search_reddit_browser` adapter:

1. C1 `openclaw`, quick;
2. C2 `AI agents`, quick;
3. C3 `agent browser`, default;
4. C4 `Claude Code`, quick.

The budget is four searches, one active search, zero retries, zero paid calls,
and zero research-model calls. Each adapter call has a 120-second wall bound.
Unused slots expire on closeout or hard stop.

## Timing Controller

Use one persistent Python process for the whole matrix. It holds the prior
query's `time.monotonic()` start in memory, refuses each later launch until at
least 65 seconds have elapsed, records wall and monotonic start/end evidence,
and waits for an explicit `NEXT` command between cases. `STOP` exits without
launching another query. This creates a five-second safety margin over the
60-second acceptance gate and keeps manual relevance review between requests.

## Preflight Gate

Before C1 require current read-only proof that agent-browser install doctor,
remote-view, route pool, display, and selected access plan are ready; no
`last30days-reddit` session or conflicting lease exists; the worktree contains
only this packet's governed documentation; and service 0.2.13 remains
uninstalled. The optional browser-capability CLI form that failed before
dispatch in Plan 0021 remains advisory and will not be retried.

## Acceptance Criteria

- every accepted C2-C4 item covers all meaningful query terms through literal
  or configured-synonym matching in normalized title/body;
- C3 never accepts an `agent`-only or `browser`-only result, and C4 never
  accepts a `Claude`-only or `Code`-only result;
- partial candidates report `partial_query_match`; zero-overlap candidates
  report `off_topic`;
- all accepted items are public, non-promoted, in range, canonical Reddit post
  URLs, and 100% manually relevant within this bounded sample;
- all calls stay below 120 seconds, observed starts are at least 60 seconds
  apart, and concurrency stays at one;
- zero-yield typed quality-gate results are valid rejection evidence but do not
  prove useful yield;
- the named browser lane is closed and verified afterward; service 0.2.13 stays
  uninstalled and no downstream gate is crossed.

## Hard Stops

Before sending another `NEXT`, stop on any accepted false positive; promoted,
private, noncanonical, or out-of-range acceptance; authentication/checkpoint,
rate-limit, route, lease, navigation, browser-health, or visibility failure;
120-second overrun; spacing/concurrency violation; or any need for credentials,
profile/route mutation, installation, paid/model fallback, proxy, or source
change. Preserve remaining cases as `not_run`, close only the named lane, and
expire unused budget.

## Non-Goals

No source/test change, service install/restart, credential or topology change,
collection, persistence, indexing, scheduling, push, tag, publication, or
release is authorized.

## Work Units And Authority

The primary agent owns the serialized controller, manual review, cleanup, and
receipt. No subagent is used because the browser lane is exclusive and
unrequested delegation is prohibited. Authority classification: `human_gate`.
The user's adjusted retry authorization covers only this four-query packet and
routine cleanup.

## Definition Of Done

Close when all four cases run or a hard stop is preserved; timing, output,
manual relevance, and cleanup are recorded in a redacted JSON receipt; current
governance validation passes; and the outcome is written and verified in
Graphiti.

### Checkpoint P0022-C01 | 2026-07-31

Plan version: 1

State transition: `PLANNED -> OPEN`

Progress classification: `outcome_progress`

Owned changes:

- created the separately authorized successor with machine-enforced monotonic
  spacing and manual review pauses.

Validation evidence:

- Plan 0021 closure is committed at `6709502`, and its verified Graphiti
  durability is committed at `cc9f0ad`;
- the operator explicitly authorized one adjusted retry packet.

Subagent status and reconciliation:

- `not_spawned`; browser ownership remains serialized.

Remaining acceptance criteria:

- current preflight, C1-C4, manual relevance, timing, cleanup, receipt,
  Graphiti, and closeout governance remain.

Graphiti write status:

- pending live outcome closeout.

Authority classification:

- `human_gate`

Next action: run only the current read-only preflight and commit it before
starting the persistent controller.

### Checkpoint P0022-C02 | 2026-07-31

Plan version: 1

State transition: `ready -> active`

Progress classification: `outcome_progress`

Owned changes:

- completed the fresh zero-query read-only preflight.

Validation evidence:

- agent-browser 0.27.0 install doctor returned `success=true`, zero issues,
  converged runtimes, ready patched Chromium, and zero resource candidates;
- remote-view doctor returned overall and remote-control `ready`; both route
  pool entries were ready, including route A `guacamole:1` on display `:10`;
- access planning explicitly selected profile `last30days-facebook` with
  `stealthcdp_chromium`, `remote_headed`, `rdp_gateway`,
  `manual_attached_desktop`, and `private_virtual_display`; active leases were
  zero and duplicate pressure was false;
- no retained session named `last30days-reddit` and no retained Reddit tab
  existed; one unrelated custom-profile browser was active without a route and
  does not share the selected profile;
- installed service status was ready at 0.2.12/schema 12, confirming source
  service 0.2.13 remains uninstalled;
- the governed worktree was clean before this checkpoint.

Subagent status and reconciliation:

- `not_spawned`; live browser ownership remains serialized.

Remaining acceptance criteria:

- C1-C4, manual relevance, timing, cleanup, receipt, Graphiti, and closeout
  governance remain.

Graphiti write status:

- pending live outcome closeout.

Authority classification:

- `human_gate`

Next action: start the persistent controller, send `NEXT` for C1 once, inspect
the result, and continue only if no hard stop fires.

### Checkpoint P0022-C03 | 2026-07-31

Plan version: 1

State transition: `active -> closed`

Progress classification: `outcome_progress`

Owned changes:

- completed all four machine-spaced queries and manual adjudication;
- closed and verified the named browser lane;
- recorded `docs/dev/notes/0022-reddit-relevance-machine-spaced-canary-receipt.json`.

Validation evidence:

- C1 `openclaw`: 45,083 ms, 7 candidates, 3 accepted, 3/3 relevant;
- C2 `AI agents`: 39,828 ms, 7 candidates, 1 accepted, 1/1 relevant,
  3 partial and 3 off-topic rejections;
- C3 `agent browser`: 54,304 ms, 19 candidates, zero accepted, 5 partial and
  14 off-topic rejections; typed `quality_gate_failed` proved live rejection
  but not useful yield;
- C4 `Claude Code`: 37,141 ms, 7 candidates, 3 accepted, 3/3 relevant, one
  partial and one off-topic rejection;
- monotonic start gaps were 70.764, 68.261, and 67.291 seconds; concurrency was
  one and every call stayed below 120 seconds;
- four wrapper/controller startup defects occurred before any adapter call;
  two were orchestration construction errors and two were process startup/input
  errors; all consumed zero queries and opened no browser;
- named close returned `closed=true`; no matching session/browser/Reddit tab
  remained; route A `guacamole:1` / `:10` and remote control remained ready;
- no install/restart, collection, persistence, credential, paid/model fallback,
  source change, push, tag, publication, or release occurred.

Subagent status and reconciliation:

- `not_spawned`; the primary agent owned execution and review.

Remaining acceptance criteria:

- none for this canary; installation and downstream gates remain separate.

Graphiti write status:

- completed and verified in `last30days_skill_main` as episode
  `4c176bc9-ff7a-435e-af6f-703d6a77247a` (job
  `8640b7a4-d8f6-4f33-8293-9bf62b0a6ccc`); exact episode retrieval, exact
  metadata lookup, and fact search returned the Plan 0022 outcome.

Authority classification:

- `standing_goal`

Next action: preserve service 0.2.13 as uninstalled and return to Plan 0018
S07; any installation, push, tag, publication, or release remains separately
gated.
