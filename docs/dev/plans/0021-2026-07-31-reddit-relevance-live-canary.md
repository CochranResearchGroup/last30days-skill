# Plan 0021 | Reddit relevance live canary

State: CANCELLED
Roadmap: P07
Date: 2026-07-31
Plan version: 1
Predecessor: Plan 0020 checkpoint P0020-C02

## Objective

Validate the repaired Reddit agent-browser relevance gate against current
public Reddit search results with exactly four authorized, serialized queries,
then close the browser and decide whether the source candidate is suitable for
a separately gated installation review.

## Current State

- Plan 0020 implemented and fully validated complete meaningful-term coverage
  at source commit `2af08b2`.
- Source service 0.2.13 remains uninstalled; the installed service remains
  0.2.12 and is outside this canary's mutation scope.
- The operator explicitly approved the four-query budget on 2026-07-31.
- No query in this plan has started. Read-only route, install, access-plan, and
  session readiness remain to be checked.

## Scope

Owned write surfaces:

- this plan, `ROADMAP.md`, `RUNBOOK.md`, the plan-authority test, and one
  redacted machine-readable canary receipt;
- one named agent-browser session/profile lane already established for public
  Reddit validation: `last30days-reddit` / `last30days-facebook`;
- at most four public Reddit searches through the working-tree
  `search_reddit_browser` adapter.

## Non-Goals

- installing, upgrading, restarting, or reconfiguring the last30days service;
- changing source, tests, relevance semantics, browser topology, credentials,
  profiles, routes, proxies, or CAPTCHA handling;
- enabling keyless, paid, model-backed, or App Intelligence fallback;
- collection, persistence, indexing, canary scheduling, or soak testing;
- push, tag, publication, or release.

## Query Matrix And Bounds

Run in this order with one active query, no retry, and at least 60 seconds
between query starts:

1. C1 `openclaw`, quick depth, single-word compatibility control;
2. C2 `AI agents`, quick depth, synonym-capable multiword case;
3. C3 `agent browser`, default depth, repaired Plan 0019 false-positive case;
4. C4 `Claude Code`, quick depth, repaired Plan 0019 false-positive case.

Each query has one attempt and a 120-second outer wall bound. The cumulative
budget is four Reddit searches, one active query, zero automatic retries, zero
paid calls, and zero research-model calls. Unused budget expires at closeout.

## Preflight Gate

Before C1, require current read-only evidence that:

- the worktree contains only this plan packet's owned documentation changes;
- agent-browser install doctor and remote-view doctor are ready with no
  readiness-impacting issue;
- the selected access plan identifies the intended profile, browser build,
  remote-headed route, manual desktop control, and usable display posture;
- no active `last30days-reddit` session or conflicting profile lease exists;
- `agent-browser` is on PATH and source service 0.2.13 remains uninstalled.

Preflight failure consumes zero queries and closes the attempt fail-closed.

## Acceptance Criteria

- every accepted C2-C4 item covers every meaningful query term by literal or
  configured-synonym match across normalized title and body;
- no C3 item matching only `agent` or only `browser` is accepted;
- no C4 item matching only `Claude` or only `Code` is accepted;
- C1 preserves usable single-word behavior when current public results exist;
- any partial candidate is rejected as `partial_query_match`, while zero
  overlap remains `off_topic`;
- all accepted items are public, non-promoted, in range, canonical Reddit post
  URLs, and manually judged relevant at a 100% canary threshold;
- every query remains below 120 seconds, starts are spaced by at least 60
  seconds, and query concurrency never exceeds one;
- cleanup removes only the named session/browser/tab and leaves the selected
  route available;
- service 0.2.13 remains uninstalled and no downstream gate is crossed.

Current-result volatility may produce zero accepted items. A typed
`quality_gate_failed` result with partial-query diagnostics is valid rejection
evidence, but does not by itself prove useful live yield. Record synonym-backed
acceptance as observed or not observed rather than fabricating it.

## Hard Stops

Stop immediately without retry or successor traffic on:

- any accepted false positive or promoted/private/noncanonical result;
- checkpoint, authentication, rate-limit, navigation-mismatch, route-loss,
  lease-conflict, browser-health, or operator-visibility failure;
- a query exceeding 120 seconds or a concurrency/spacing violation;
- any need for credential, profile, route, install, service, paid-source,
  model, proxy, or source-code mutation;
- unsafe or overlapping worktree changes.

After a hard stop, close only the plan-owned browser lane, preserve the
evidence, mark remaining cases `not_run`, and close or cancel this plan without
spending unused query budget.

## Work Units And Authority

Critical-path owner: primary agent. Queries, review, and cleanup are serialized.
No subagent is used because browser/session ownership is exclusive and the
developer policy prohibits unrequested delegation.

Authority classification: `human_gate`. The user's `ok go` authorizes only the
four-query matrix and routine cleanup described here. It does not authorize
installation, collection, persistence, push, tag, or release.

## Definition Of Done

Close `CLOSED` when all four cases run or a hard stop is preserved, the named
browser lane is cleaned up, a redacted receipt records consumed and unused
budget plus manual relevance evidence, current plan/governance validation
passes, and the outcome is written and verified in Graphiti.

### Checkpoint P0021-C01 | 2026-07-31

Plan version: 1

State transition: `PLANNED -> OPEN`

Progress classification: `outcome_progress`

Owned changes:

- created and wired the four-query live canary authority.

Validation evidence:

- Plan 0020 is closed at validated implementation commit `2af08b2`;
- the worktree was clean before this planning packet;
- the operator explicitly approved the proposed four-query budget.

Subagent status and reconciliation:

- `not_spawned`; live browser ownership remains serialized.

Remaining acceptance criteria:

- all preflight, live query, manual relevance, timing, cleanup, receipt,
  Graphiti, and governance gates remain.

Graphiti write status:

- pending live outcome closeout.

Authority classification:

- `human_gate`

Next action: run only the read-only preflight; launch C1 only if every gate is
ready.

### Checkpoint P0021-C02 | 2026-07-31

Plan version: 1

State transition: `ready -> active`

Progress classification: `outcome_progress`

Owned changes:

- completed the zero-query read-only live preflight.

Validation evidence:

- agent-browser 0.27.0 install doctor returned `success=true`, zero issues,
  converged runtimes, a ready patched Chromium manifest, and no resource
  cleanup candidates;
- remote-view doctor returned overall, remote-control, route-pool, display
  access, and public ingress readiness, with route A on `guacamole:1` / `:10`;
- access-plan selected `last30days-facebook`, `stealthcdp_chromium`,
  `remote_headed`, `rdp_gateway`, manual desktop control, and private display
  isolation with zero active leases and no duplicate pressure;
- no `last30days-reddit` session existed;
- installed service diagnosis remained ready at 0.2.12/schema 12;
- the optional browser-capability preflight command rejected its own documented
  argument form before dispatch, but the required install doctor and access
  plan independently reported compatible profile and passed validation
  evidence; no browser or query was launched by that advisory command.

Subagent status and reconciliation:

- `not_spawned`; live ownership remains serialized.

Remaining acceptance criteria:

- C1-C4, manual relevance review, cleanup, receipt, Graphiti, and closeout
  governance remain.

Graphiti write status:

- pending live outcome closeout.

Authority classification:

- `human_gate`

Next action: run C1 `openclaw` quick once, then preserve at least 60 seconds
before C2 if no hard stop fires.

### Checkpoint P0021-C03 | 2026-07-31

Plan version: 1

State transition: `active -> cancelled`

Progress classification: `regression`

Owned changes:

- ran C1 and C2 through the repaired working-tree adapter;
- stopped the matrix on the query-start spacing violation;
- closed and verified cleanup of the named browser lane;
- recorded the bounded outcome in
  `docs/dev/notes/0021-reddit-relevance-live-canary-receipt.json`.

Validation evidence:

- C1 `openclaw` started at `2026-07-31T15:52:03-05:00`, completed in
  47,307 ms, accepted 3/7, and all 3 accepted items were manually relevant;
- C2 `AI agents` started at `2026-07-31T15:52:59-05:00`, only 56 seconds after
  C1, violating the 60-second minimum; it completed in 37,766 ms with zero
  accepted items, two `partial_query_match` rejections, and two `off_topic`
  rejections;
- C3 and C4 were not run; two of four query slots expired unused;
- named-session close returned `closed=true`; grouped session, browser, and
  Reddit-tab read-backs were empty; remote-view doctor returned ready with
  route A available on `guacamole:1`;
- no service install/restart, collection, persistence, credential, paid call,
  research-model call, source change, push, tag, publication, or release ran.

Subagent status and reconciliation:

- `not_spawned`; the primary agent owned all live work and review.

Remaining acceptance criteria:

- the full four-query canary, C3/C4 false-positive checks, and compliant timing
  proof remain unverified; this cancelled packet grants no retry authority.

Graphiti write status:

- completed and verified in `last30days_skill_main` as episode
  `c72ef904-547b-468b-a477-f8a374803429` (job
  `41d7186f-5843-43b8-9c6a-51e826f9c976`); exact episode retrieval and fact
  search both returned the Plan 0021 outcome.

Authority classification:

- `human_gate`

Next action: keep source service 0.2.13 uninstalled and do not spend the expired
query budget. Return active execution to Plan 0018; any new Reddit canary must
be separately proposed and approved.
