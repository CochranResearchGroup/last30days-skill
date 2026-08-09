# Plan 0037 | Facebook Page-Session CDP Readability

State: OPEN
Roadmap: P13
Plan version: 1
Date: 2026-08-09
Predecessor: Plan 0036 version 3/checkpoint P0036-C03
Cross-repo evidence: agent-browser commit `78c088bc`

## Objective

Restore bounded CDP command responsiveness for an inventory-visible rendered
Facebook search page, install the verified agent-browser repair, and then prove
accepted Facebook content through the existing recurring Last30Days path.

## Current State

- Last30Days service 0.3.39 fixed the tab inventory margin and is installed,
  ready, synchronized, and fully tested;
- its sole provider proof completed inventory, authentication evaluation,
  search navigation, and fresh-target opening, then failed because both the
  original and successor Facebook search page sessions stopped answering CDP
  target commands;
- browser-level CDP discovery, version, target listing, and attachment remain
  responsive; commands routed into the successfully attached page session do
  not return;
- agent-browser 0.28.0 and its five live daemons are executable-converged.
  The exact investigation packet is published at
  `agent-browser/docs/dev/notes/2026-08-09-facebook-search-target-cdp-runtime-stall.md`;
- `daily-default` remains enabled with Facebook present, but routine scraping
  is not usable until accepted content is proven.

## Scope

- investigate the agent-browser native CDP page-session response path using the
  published no-mutation reproducer and CodeGraph-identified Rust symbols;
- distinguish absent Chromium responses from response correlation, session-ID,
  reader-loop, or pending-map delivery defects;
- add a deterministic regression or bounded isolated live canary that fails
  before the repair and does not use the default runtime profile;
- implement the narrow upstream repair or typed fail-closed responsiveness
  contract without browser/profile destruction or automatic retries;
- validate and install the agent-browser successor, re-prove retained-session
  target commands, then install any required Last30 integration update;
- only after those gates, authorize one new fully closed Facebook content proof
  and audit the unchanged daily schedule.

## Non-Goals

- no longer Last30 outer timeout, blind provider retry, default-profile test,
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
3. The repaired agent-browser returns bounded typed responses for
   `Page.getFrameTree`, trivial `Runtime.evaluate`, eval, and snapshot after
   Facebook search navigation, while browser/profile identity is preserved.
4. Relevant Rust tests, format, Clippy, selected repo validation, install doctor,
   executable convergence, and retained-session readbacks pass.
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
- maximum future provider attempts: one, only after installed upstream and
  downstream convergence plus fresh guards;
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

## Stop Rules

Stop on any execution-bound violation. Do not convert a target-command stall
into a browser restart or provider retry without new explicit authority.
