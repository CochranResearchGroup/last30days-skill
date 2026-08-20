# Plan 0053 | X Authentication Alert Truthfulness

State: OPEN
Roadmap: P08
Plan version: 1
Date: 2026-08-20

## Objective

Prevent an inconclusive X DOM or a recovered historical incident from looking
like a current X authentication failure in Slack, then run one bounded X-only
retry on the exact retained social profile.

## Current State

- installed service 0.3.51/schema 16 is ready and compatible with MCP 4.0.3;
- the Aug 20 recurring X lane succeeded with three accepted posts and resolved
  the Aug 16 `reauthentication_required` incident;
- Slack delivered that resolution while retaining the historical incident type,
  making the healthy recovery look like a fresh authentication error;
- X auth inspection also converts a twice-inconclusive DOM into
  `auth_required` even when it observes no login form, checkpoint, or account
  restriction;
- the exact retained `last30days-facebook` browser is currently ready on
  `https://x.com/home` with a visible Route A window.

## Scope

- add a typed `auth_state_ambiguous` X result for inconclusive DOM evidence;
- preserve `auth_required` only for observed login-form/login-surface evidence;
- render resolved Slack notifications as resolved historical incidents without
  an active-looking `type: reauthentication_required` line;
- add deterministic regressions at both exact seams and update operator docs;
- validate, version, build, install, and verify one service successor;
- preflight and enqueue exactly one X-only receipt-bound retry, then stop at its
  first terminal result.

## Non-Goals

- do not change X selectors, query, item ceiling, profile, browser process,
  LinkedIn/YouTube/Reddit/Facebook state, recurring cadence, retry count, cost,
  model use, or Slack transport;
- do not mark the Aug 16 historical incident as never having occurred;
- do not launch a duplicate browser or authenticate on the user's behalf.

## Acceptance Criteria

1. A minimized test proves ambiguous X auth evidence does not return
   `auth_required`, while a real login form still does.
2. A resolved reauthentication notification leads with resolved state and does
   not render an active-looking `type: reauthentication_required` line or a
   manual sign-in action.
3. Focused and full validation plus reproducible service builds pass.
4. The exact successor installs ready with the prior runtime retained as
   rollback and MCP compatibility preserved.
5. One X-only preflight and tick use the retained named profile, one attempt,
   zero cost/model use, and stop at the first terminal receipt.

## Definition Of Done

- the corrected installed runtime and one X-only terminal retry are recorded in
  this plan and `RUNBOOK.md`; recurring schedule state is unchanged and the
  plan closes without another attempt.

### Checkpoint P0053-C01 | 2026-08-20

Plan version: 1

State transition:

- `x_auth_truthfulness_repro_ready -> validated_runtime_candidate`.

Progress classification:

- `outcome_progress`; minimized regressions now distinguish an inconclusive X
  DOM from an observed login surface and a recovered incident from an active
  Slack alert.

Owned changes:

- X auth classification, safe resolved-notification rendering, focused tests,
  service 0.3.52 identity/manifest, user configuration, and release notes.

Validation evidence:

- both minimized tests failed on the previous behavior and pass after the
  correction; the existing genuine-login regression also passes;
- focused X/incident/runtime/runner/release/package suites and the full test
  suite pass;
- two service 0.3.52 builds are byte-identical at SHA-256
  `437d8822984a512f6206f7f69dc10c1a4d9a57c062c871784657259c6908bcf5`.

Authority classification:

- `inherited_authority`; the operator requested another attempt after
  reporting the contradictory X authentication notice and logged-in browser.

Subagent status and reconciliation:

- `not_spawned`; current orchestration policy prohibits delegation.

Graphiti write status:

- pending validated installed-runtime and terminal-tick closeout.

Remaining acceptance criteria:

- commit and push the exact candidate, transactionally install and verify
  service 0.3.52, then preflight/enqueue one X-only tick and stop at its first
  terminal receipt.

Next action:

- commit the validated source candidate before installing its exact artifact.

Checkpoint P0053-C01 is the current authority.
