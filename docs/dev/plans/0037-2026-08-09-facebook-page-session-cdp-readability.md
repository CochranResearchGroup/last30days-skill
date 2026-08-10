# Plan 0037 | Facebook Page-Session CDP Readability

State: OPEN
Roadmap: P13
Plan version: 4
Date: 2026-08-09
Predecessor: Plan 0036 version 3/checkpoint P0036-C03
Cross-repo evidence: agent-browser code commit `5ecb4d62`

## Objective

Restore bounded Facebook target readability for an inventory-visible rendered
search page, install the verified renderer-isolating Last30Days repair, and then
prove accepted Facebook content through the existing recurring path.

## Current State

- Last30Days service 0.3.42 is installed, ready, synchronized, and fully
  tested after three distinct adaptive candidates were exercised;
- service 0.3.40 proved renderer isolation, exact predecessor closure, home
  navigation, and authentication evaluation, then stalled at the desktop top
  search navigation command even though the page rendered;
- service 0.3.41 changed the target to the posts-only search surface; its
  navigation returned successfully, but the following Runtime evaluation
  stalled on the rendered page;
- service 0.3.42 changed the frozen-target path to one mobile query navigation
  and one composite auth/page/extraction capture. Facebook redirected the
  mobile URL to the desktop posts route, rendered it, and the single Runtime
  capture still stalled;
- browser-level CDP discovery, version, target listing, and attachment remain
  responsive; commands routed into the successfully attached page session do
  not return;
- agent-browser 0.28.0 now carries renderer-side Runtime deadlines,
  browser-level navigation metadata, response-before-health delivery, and a
  same-inode CLI identity fast path at code commit `5ecb4d62`; installed
  executable SHA-256 is
  `17f393c716f63de5008a25045f1ead0a4377efb7936300c8e1bcce2247d5995b`.
  The exact investigation packet is published at
  `agent-browser/docs/dev/notes/2026-08-09-facebook-search-target-cdp-runtime-stall.md`;
- disposable installed proof returned a baseline evaluation in 455 ms, a
  typed infinite-loop failure in 4.546 seconds, and immediate same-target
  recovery in 1.482 seconds. A retained-session control then proved the old
  Facebook target remains frozen but now returns typed three-second job
  timeouts; the original active X tab was restored;
- service 0.3.43 is a validated offline candidate. Shared retained-social
  navigation now uses a 25-second agent-browser job deadline inside its
  30-second Python subprocess deadline, preserving response and cleanup grace;
  the canonical suite passes 2,638 tests, 7 skips, and 6 subtests, and artifact
  SHA-256 is
  `53d1d185c44b46a54280cb444c94ec55c0085d81e6194c3a54fcd151259a4bed`;
- `daily-default` remains enabled with Facebook present, but routine scraping
  is not usable until accepted content is proven. The three-attempt ceiling is
  exhausted; no fourth provider execution is authorized by this plan.

## Scope

- investigate the agent-browser native CDP page-session response path using the
  published no-mutation reproducer and CodeGraph-identified Rust symbols;
- distinguish absent Chromium responses from response correlation, session-ID,
  reader-loop, or pending-map delivery defects;
- add a deterministic regression or bounded isolated live canary that fails
  before the repair and does not use the default runtime profile;
- implement the narrow upstream repair or a downstream renderer-isolating
  recovery contract without browser/profile destruction or automatic retries;
- validate and install the agent-browser successor, re-prove retained-session
  target commands, then install any required Last30 integration update;
- only after those gates, authorize one new fully closed Facebook content proof
  and audit the unchanged daily schedule.

## Non-Goals

- no blind provider retry, default-profile test,
  existing-browser restart/close, storage/cookie clearing, login/logout,
  CAPTCHA/checkpoint interaction, rate-limit induction, schedule change, cost,
  or model use;
- no routine-ready claim from target inventory, title, screenshot, or browser
  health alone;
- no assumption that duplicate daemon sessions or the shared-social profile
  lease caused the page-session failure without a reproducer.

## Acceptance Criteria

1. The Plan 0036 operation ledger and direct page/browser WebSocket results are
   preserved as the source-backed failure contract.
2. A failing regression or isolated-profile canary proves the target session
   can be inventory-visible while `Page` and `Runtime` commands stall.
3. The repaired path retires the frozen Facebook renderer before successor
   navigation and returns a bounded typed readback after search navigation,
   while browser/profile identity is preserved.
4. Relevant Last30 tests and selected repo validation pass; agent-browser Rust,
   install-doctor, and executable convergence remain required only if that
   upstream repository changes.
5. Any Last30 integration changes pass focused and canonical validation and are
   installed with source/artifact/runtime identity convergence.
6. One newly governed Facebook-only tick persists at least one accepted
   in-window canonical post with coherent provenance and counters, zero
   cost/model use, and no auth/challenge/rate-limit/integrity signal.
7. `daily-default` remains enabled/ready with Facebook present and unchanged
   cadence; databases and retained browser cleanup remain healthy.

## Definition Of Done

- criteria 1-7 have exact commits, tests, artifacts, runtime hashes, tick IDs,
  counters, and post-effect readbacks;
- P13 closes only after accepted content proves recurring automation usable;
- changes are committed and pushed to the appropriate public-fork `main`
  branches.

## Execution Bounds

- primary agent owns serialized cross-repo investigation and reconciliation;
- maximum upstream implementation/rework cycles: two;
- maximum future provider attempts: three, each only after a distinct installed
  adaptation plus fresh guards; never repeat an unchanged build;
- hard stop on need to mutate the current retained browser/profile, inability
  to reproduce without the default profile, auth/challenge/rate-limit signal,
  nonzero cost/model use, or schedule mutation;
- no subagent; current policy forbids unrequested delegation and the live
  browser boundary is serialized.

## Owned Write Surfaces

- agent-browser native CDP response path, focused tests, and required docs if a
  user-visible contract changes;
- Last30 Facebook integration only if the upstream contract requires it;
- this plan, P13, RUNBOOK, authority test, notes, version/install artifacts, and
  one future provider receipt.

### Checkpoint P0037-C01 | 2026-08-09

Plan version: 1

State transition:

- `facebook_page_session_cdp_blocker -> upstream_investigation_ready`.

Progress classification:

- `blocker_reduction`; direct CDP narrowed the failure from browser or routing
  health to commands routed into an already attached page session.

Owned changes:

- published and refined the agent-browser investigation note at commits
  `039e7a12` and `78c088bc`; no source or live runtime change yet.

Validation evidence:

- Graphiti `agent_browser_main` discovery returned eight facts, five nodes,
  and five episodes but no exact prior Facebook target-command stall;
- agent-browser install doctor passes at 0.28.0 with executable SHA-256
  `01965e35f09883522ca281fcd66657a6d8d372dcda8797eca7fe260c6f8b4c9b`;
- CodeGraph locates evaluation at `cli/src/native/browser.rs:1020` and pending
  command/timeout handling in `cli/src/native/cdp/client.rs`;
- browser CDP responds through successful target attachment, while two
  independent page-session commands receive no response.

Subagent status and reconciliation:

- `not_spawned`; the primary owns cross-repo reconciliation.

Authority classification:

- `inherited_authority`; investigation and test design directly advance the
  operator's automated Facebook goal without consuming a new live effect.

Review disposition summary:

- `blocking=1` upstream page-session responsiveness defect, `rejected=0`,
  `needs_evidence=0`, `nonblocking_backlog=0`.

Graphiti write status:

- discovery complete; compact closeout write deferred until this plan has a
  durable repaired or blocked outcome.

Remaining acceptance criteria:

- criteria 2-7.

Next action:

- inspect the native CDP reader and session-correlation path, design the
  smallest isolated regression, and do not touch the retained Facebook browser.

### Checkpoint P0037-C02 | 2026-08-09

Plan version: 2

State transition:

- `upstream_investigation_ready -> downstream_renderer_isolation_red`.

Progress classification:

- `causal_adaptation`; the installed 0.3.39 trace and manual CDP controls show
  the fresh same-site target was allowed to coexist with the wedged predecessor,
  so Chromium could reuse the same Facebook renderer/site process.

Evidence and decision:

- raw page WebSocket and attached browser-session `Runtime.evaluate` both stall
  only for Facebook; LinkedIn, X, preview, and new-tab targets in the same
  browser return normally;
- `open_fresh_site_target` navigates a new Facebook target before cleanup closes
  its predecessor, whereas `replace_active_site_target` already opens
  `about:blank` and closes the exact predecessor before later navigation;
- the 0.3.39 operations consumed about 68 of the cumulative 75 seconds before
  cleanup, leaving insufficient room for inventory, blank successor, exact
  close, navigation, readback, and extraction;
- therefore the next candidate restores renderer-isolating replacement order
  and raises only the default bounded adapter allowance to 105 seconds beneath
  the unchanged 120-second parent worker boundary.

Authority classification:

- `inherited_authority`; the operator authorized up to three adaptive attempts
  and explicitly rejected waiting for natural time.

Review disposition summary:

- `blocking=1` renderer-isolating recovery not yet implemented, `rejected=0`,
  `needs_evidence=0`, `nonblocking_backlog=0`.

Remaining acceptance criteria:

- criteria 2-7.

Next action:

- land the red recovery-order and budget regressions, implement the narrow
  downstream repair, validate and install it, then consume at most one new
  governed attempt on that distinct build.

### Checkpoint P0037-C03 | 2026-08-09

Plan version: 2

State transition:

- `downstream_renderer_isolation_red -> service_0_3_40_candidate_validated`.

Progress classification:

- `implementation_complete`; the candidate retires the exact stalled target
  behind an `about:blank` successor before navigating back to Facebook, and
  bounds the adapter to the parent worker minus a 15-second cleanup reserve.

Owned changes:

- default Facebook/adaptor maximum `75 -> 105` seconds;
- service worker maps 120-second parents to 105, 90-second parents to 75, and
  preserves explicit lower values;
- authentication and navigation recovery both use blank successor, exact
  predecessor close, then navigation; the superseded same-site-open primitive
  is removed;
- service version `0.3.39 -> 0.3.40`, runtime manifest, configuration,
  changelog, and release-version contracts are synchronized.

Validation evidence:

- the three red regressions independently failed on the old 10-second
  replacement inventory, 75-second budget, and same-site successor order;
- focused Facebook, acquisition-worker, release-version, and runtime-package
  suites pass;
- canonical suite passes with `2635 passed, 7 skipped, 6 subtests passed` in
  121.02 seconds;
- `git diff --check` passes.

Authority classification:

- `inherited_authority`; this is the first distinct adaptive candidate under
  the operator's maximum-three-attempt bound.

Review disposition summary:

- `blocking=1` install and governed proof pending, `rejected=0`,
  `needs_evidence=0`, `nonblocking_backlog=0`.

Remaining acceptance criteria:

- criteria 3 and 5-7; criterion 4's Last30 validation portion passes and no
  agent-browser source changed.

Next action:

- commit and push the candidate, build and install service 0.3.40, re-prove
  source/artifact/runtime convergence, then run one governed adaptive attempt.

### Checkpoint P0037-C04 | 2026-08-10

Plan version: 2

State transition:

- `service_0_3_40_candidate_validated -> attempt_1_search_surface_blocker`.

Progress classification:

- `later_blocker`; the first adaptive attempt proved renderer-isolating
  replacement and responsive authentication, then the `/search/top/` surface
  itself stalled its target command channel.

Attempt evidence:

- installed timer tick `tick-a572e3424d4ca75b9f7bcf1031686c2e`, execution
  `tick-attempt-66b671aae8c22623c5ea417aba8754c3`, Facebook provider
  `provider-attempt-7fd8386100cbbf5a6d48006bf9ecfe3a`;
- result digest
  `sha256:3cff15cb048c26eae72e823b7b3b534f88dd42f9722b4bedf62f718bbad75593`,
  `facebook_target_unresponsive`, 111 seconds, one opaque request, zero items,
  cost, model tokens, auth, challenge, rate-limit, or quality signal;
- operations completed service access, 20-second inventory, blank successor,
  exact predecessor close, Facebook-home navigation, and authentication eval;
  the later search `open` alone timed out at 30,041 milliseconds;
- exact session inventory then showed a rendered `OpenAI - Search Results`
  target at the requested URL. Independent raw page-WebSocket
  `Runtime.evaluate` timed out, while `Page.captureScreenshot` returned an
  immediate CDP internal error.

Attempt-2 adaptation:

- replace the generic `/search/top/` plus encoded post filter with Facebook's
  already-supported post-specific `/search/posts/` route while preserving the
  recent-post filter, query/readback gate, auth, one-successor bound, and
  extraction/quality contracts;
- this is a distinct surface adaptation, not an unchanged retry. A red route
  regression must fail before implementation.

Authority classification:

- `inherited_authority`; attempt 1 of the operator's maximum three is consumed.

Review disposition summary:

- `blocking=1` post-specific surface candidate not yet implemented,
  `rejected=0`, `needs_evidence=0`, `nonblocking_backlog=0`.

Remaining acceptance criteria:

- criteria 3 and 5-7.

Next action:

- land the red `/search/posts/` contract, version and validate service 0.3.41,
  wait only for the already-running timer tick to terminate before install,
  then consume attempt 2 on the distinct installed build.

### Checkpoint P0037-C05 | 2026-08-10

Plan version: 2

State transition:

- `attempt_1_search_surface_blocker -> service_0_3_41_candidate_validated`.

Progress classification:

- `implementation_complete`; the post-specific search route is the only
  behavioral delta from installed 0.3.40.

Owned changes:

- `_search_url` now emits `https://www.facebook.com/search/posts/` with the
  unchanged encoded recent-post filter;
- added a route/host/filter regression that failed on `/search/top/` before
  implementation;
- service version `0.3.40 -> 0.3.41`, runtime manifest, changelog, and release
  contracts are synchronized.

Validation evidence:

- focused Facebook, acquisition-worker, release-version, and runtime-package
  suites pass;
- canonical suite passes with `2636 passed, 7 skipped, 6 subtests passed` in
  126.24 seconds;
- attempt 1 terminated `complete_degraded`; the daily schedule returned to
  ready with next boundary `2026-08-11T00:00:00Z` and no runtime error;
- `git diff --check` passes.

Authority classification:

- `inherited_authority`; attempt 2 remains unconsumed until 0.3.41 is installed
  and converged.

Review disposition summary:

- `blocking=1` install and attempt-2 proof pending, `rejected=0`,
  `needs_evidence=0`, `nonblocking_backlog=0`.

Remaining acceptance criteria:

- criteria 3 and 5-7.

Next action:

- commit and push 0.3.41, build/install/sync it, run fresh guards and one
  Facebook-only manual tick for attempt 2.

### Checkpoint P0037-C06 | 2026-08-10

Plan version: 2

State transition:

- `service_0_3_41_candidate_validated -> attempt_2_runtime_channel_blocker`.

Progress classification:

- `later_blocker`; attempt 2 proved post-specific navigation completes but a
  later Runtime read still cannot fit or respond on the desktop search target.

Attempt evidence:

- tick `tick-e5176a8fc531b4e66ea85a71a1cc1a1b`, execution
  `tick-attempt-50f713dc4658f0f25f0b76605447bdd8`, provider
  `provider-attempt-a33d51f782a4824250b83ee637759692`;
- result digest
  `sha256:982f2f8fe9e15354ca594e9df90563fd071250796f7bb544c19cef8fdbc5ab86`,
  `facebook_target_unresponsive`, 110 seconds, one request, zero items/cost/model
  and no auth/challenge/rate-limit/quality signal;
- blank replacement, exact close, home navigation/auth eval, and later
  `/search/posts/` navigation all succeeded; only the navigation-state eval was
  clamped to the final 6,053 milliseconds and timed out;
- post-effect inventory showed the correct rendered post-search URL. An
  independent raw Runtime evaluation still did not respond in 15 seconds, so
  a clock-only extension is rejected for attempt 3.

Attempt-3 adaptation:

- use the authenticated mobile post-search surface
  `m.facebook.com/search/posts/`, which is live and redirects unauthenticated
  callers only to its corresponding login route;
- on the already-required frozen-target replacement path, navigate the blank
  successor directly to that query and execute one bounded composite Runtime
  capture containing authentication, page-state, and extraction results;
- cache that capture through navigation and first extraction so no later target
  command is required. Normal responsive retained-target behavior remains
  unchanged.

Authority classification:

- `inherited_authority`; attempt 2 of 3 is consumed and the final attempt must
  use this distinct installed adaptation.

Review disposition summary:

- `blocking=1` mobile single-capture candidate not yet implemented,
  `rejected=1` longer clock alone, `needs_evidence=0`,
  `nonblocking_backlog=0`.

Remaining acceptance criteria:

- criteria 3 and 5-7.

Next action:

- land red mobile-route and single-capture regressions, implement/version/test
  the candidate, then consume the third and final governed attempt only after
  installed convergence.

### Checkpoint P0037-C07 | 2026-08-10

Plan version: 2

State transition:

- `attempt_2_runtime_channel_blocker -> service_0_3_42_candidate_validated`.

Progress classification:

- `implementation_complete`; the final candidate removes every post-capture
  target command from the frozen-target path rather than extending a deadline.

Owned changes:

- prepared mobile recent-post query URLs are strictly host/path/filter checked;
- frozen-target authentication recovery performs blank successor, exact close,
  one mobile query navigation, and one 25-second inner/30-second outer composite
  capture containing auth, page, and extraction objects;
- cached page state satisfies navigation validation and cached extraction feeds
  the existing timestamp merge and quality gate, then is consumed and cleared;
- run begin/end clears cached state, and ordinary responsive-target behavior
  retains its existing commands;
- service version `0.3.41 -> 0.3.42`, manifest, changelog, and release contracts
  are synchronized.

Validation evidence:

- all three final-candidate regressions failed independently before the change
  and pass after it;
- focused Facebook, acquisition-worker, release-version, and runtime-package
  suites pass;
- canonical suite passes with `2638 passed, 7 skipped, 6 subtests passed` in
  156.88 seconds;
- `git diff --check` passes.

Authority classification:

- `inherited_authority`; attempt 3 remains unconsumed until exact installed
  convergence and fresh guards pass.

Review disposition summary:

- `blocking=1` install and final proof pending, `rejected=1` clock-only retry,
  `needs_evidence=0`, `nonblocking_backlog=0`.

Remaining acceptance criteria:

- criteria 3 and 5-7.

Next action:

- commit/push, build/install/sync 0.3.42, run fresh guards, then consume the
  third and final Facebook-only attempt.

### Checkpoint P0037-C08 | 2026-08-10

Plan version: 3

State transition:

- `service_0_3_42_candidate_validated -> attempt_limit_exhausted_upstream_blocker`.

Progress classification:

- `bounded_execution_complete`; all three authorized adaptive attempts were
  consumed, Facebook accepted-content qualification remains unmet, and no
  fourth attempt is authorized.

Adaptive evidence:

1. Installed 0.3.40 used a blank successor, exact predecessor close, Facebook
   home navigation, and auth evaluation before desktop `/search/top/`.
   Tick `tick-a572e3424d4ca75b9f7bcf1031686c2`, provider
   `provider-attempt-7fd8386100cbbf5a6d48006bf9ecfe3a`, completed the home
   and auth operations, then its search navigation reached the 30-second
   deadline. The rendered search target remained visible afterward.
2. Installed 0.3.41 changed only to `/search/posts/`. Tick
   `tick-e5176a8fc531b4e66ea85a71a1cc1a1b`, provider
   `provider-attempt-a33d51f782a4824250b83ee637759692`, returned successfully
   from the posts navigation, then its Runtime evaluation exhausted the
   remaining budget. An independent 15-second raw Runtime probe also received
   no response, rejecting a clock-only adaptation.
3. Installed 0.3.42 used `m.facebook.com/search/posts/` and one composite
   auth/page/extraction capture so no later target command was needed. Tick
   `tick-a87325ff165fe62787566f5785cde32c`, provider
   `provider-attempt-556a632cf7e995cfa8c3fbf079200478`, opened the mobile
   query successfully; Facebook redirected it to the rendered desktop posts
   route, and the sole composite Runtime call timed out after 30,044 ms.

Terminal receipt:

- final execution `tick-attempt-d211546ca63615ad81310689eea4bae4`, lane
  `tick-lane-536734a97fb6fb7e2906cc1f855742d1`, result digest
  `sha256:38afd9666ed249d71bc2af341bbdf3c160edca8f5b9e0dd8c86979e0d8442bc5`;
- terminal code `facebook_target_unresponsive`, 105 seconds, one request,
  zero observed/attempted/accepted/rejected items, cost, or model use, and no
  auth, challenge, CAPTCHA, rate-limit, or quality signal;
- final operation ledger: service 259 ms ok; service 1,974 ms ok; tab 8,657 ms
  ok; retained-target eval 11,356 ms failed; replacement inventory 9,369 ms
  ok; blank target 10,601 ms ok; exact close 9,774 ms ok; mobile query open
  17,096 ms ok; composite eval 30,044 ms timed out;
- post-effect PID 63205 remains ready with the four intended tabs, exactly one
  rendered Facebook posts-search target, zero challenges, and zero active
  profile leases. `daily-default` remains ready and unchanged, with next due
  time `2026-08-11T00:00:00Z`.

Manual investigation disposition:

- the primary sent raw `Runtime.evaluate` commands directly to page WebSocket
  endpoints and attached browser-WebSocket sessions; Facebook did not respond
  within 15-18 seconds while LinkedIn, X, preview, and a new tab returned;
- `Page.captureScreenshot` on the Facebook target returned an immediate CDP
  internal error. Browser discovery, target inventory, and attachment remained
  responsive, excluding a browser-wide CDP outage and the provider parser;
- deterministic execution supplied durable receipts, but it was not treated
  as causal proof. Each next candidate was selected from the preceding
  operation ledger plus these direct CDP controls.

Authority classification:

- `human_gate`; the inherited attempt limit is exhausted, so a fresh operator
  ceiling and an upstream
  agent-browser/Chromium Facebook target-runtime repair are required before
  another provider proof.

Review disposition summary:

- `blocking=1` Facebook-only page-session Runtime responsiveness,
  `rejected=1` longer clock alone, `needs_evidence=0`,
  `nonblocking_backlog=0`.

Remaining acceptance criteria:

- criteria 3 and 5-7 remain unmet; Facebook routine automation is not usable.

Next action:

- reproduce and repair the Facebook search target's page-session Runtime
  response path in agent-browser with a disposable authenticated fixture. Do
  not restart or clear the retained profile, and do not enqueue another
  Last30Days Facebook provider execution under this exhausted authority.

### Checkpoint P0037-C09 | 2026-08-10

Plan version: 4

State transition:

- `attempt_limit_exhausted_upstream_blocker -> upstream_repair_consumed_candidate_validated`.

Progress classification:

- `blocker_reduction`; the upstream renderer, response-delivery, and CLI
  boundaries are repaired and installed, and Last30Days now preserves an
  explicit five-second response-and-cleanup interval around navigation.

Evidence:

- agent-browser code commit `5ecb4d62`, installed executable SHA-256
  `17f393c716f63de5008a25045f1ead0a4377efb7936300c8e1bcce2247d5995b`,
  ready doctors, and converged runtime inventory;
- direct retained-session control returned typed three-second timeouts for the
  already-frozen Facebook target and successfully restored the original X tab;
- the navigation-deadline regression failed red on the old command shape, then
  passed with a 25-second inner job and 30-second outer subprocess deadline;
- the first canonical run found one shared-X expectation still bound to the old
  command. It was accepted as blocking, corrected, and closed-world
  verification passed 2,638 tests, 7 skips, and 6 subtests;
- exact service 0.3.43 artifact SHA-256 is
  `53d1d185c44b46a54280cb444c94ec55c0085d81e6194c3a54fcd151259a4bed`;
  no provider attempt, navigation, tab open/close, schedule mutation, cost, or
  model use occurred in this packet.

Subagent status and reconciliation:

- `not_spawned`; policy and the serialized browser boundary keep this work
  with the primary agent.

Authority classification:

- `inherited_authority` for implementation, validation, publication, and exact
  candidate installation; `human_gate` remains for any fourth Facebook
  provider execution because the operator's three-attempt ceiling is exhausted.

Review disposition summary:

- `blocking=0`, `rejected=1` longer-clock-only retry,
  `needs_evidence=0`, `nonblocking_backlog=0`.

Remaining acceptance criteria:

- criteria 3 and 5 require exact installed Last30Days convergence; criteria 6
  and 7 require one newly authorized Facebook content proof and post-effect
  schedule, database, and browser readbacks.

Next action:

- commit and push the validated 0.3.43 candidate, install that exact artifact,
  synchronize the frozen Skill copy, and re-prove runtime convergence. Do not
  enqueue a Facebook provider until a fresh attempt ceiling is explicit.

## Stop Rules

Stop on any execution-bound violation. Do not convert a target-command stall
into a browser restart or provider retry without new explicit authority.
