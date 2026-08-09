# Plan 0031 | Facebook Runtime Timeout Fresh-Target Recovery

State: CLOSED
Roadmap: P13
Plan version: 2
Date: 2026-08-09
Predecessor: Plan 0030 version 2/checkpoint P0030-C02

## Objective

Prevent an exact active-tab identity read from bypassing Facebook's single
fresh-target recovery after a post-navigation Runtime timeout, then build,
install, and verify service 0.3.32 without another live Facebook tick.

## Current State

- the sole guarded 0.3.31 Facebook tick preserved a typed transient provider
  failure and exhausted no quality candidates;
- its first post-navigation Runtime read timed out, active-tab inventory proved
  the exact requested URL/query/filter, and the scraper then attempted
  extraction on that same Runtime-unresponsive target;
- extraction timed out too. The retained browser remained ready at PID 63205
  with 19 tabs and no auth, CAPTCHA, checkpoint, rate-limit, or lifecycle event;
- the existing two-attempt navigation loop already has the required bounded
  fresh-target action and terminal repeated-timeout behavior. Only the exact
  identity shortcut is unsafe.

## Scope

- retain active-tab identity as bounded diagnostic evidence after the first
  Runtime timeout but never as permission to extract from that target;
- open exactly one `about:blank` target and replay navigation plus page-state
  evaluation once; a repeated timeout remains terminal;
- update the focused regression, release identity, runtime manifest, changelog,
  governing plan/roadmap/runbook, and one serial evidence note;
- run focused and full validation, reproducible builds, exact installation,
  installed-state readbacks, and skill-copy synchronization.

## Non-Goals

- no live Facebook tick, natural-schedule wait, retry of the consumed 0.3.31
  tick, schedule mutation, provider-limit increase, additional scroll,
  fallback provider, notification test, cost/model use, or content retention;
- no logout, credential entry, MFA, checkpoint, CAPTCHA, consent, cookie or
  session mutation, intentional rate-limit/challenge generation, browser/tab
  closure, or browser launch;
- no routine-usability claim from offline validation or installation.

## Acceptance Criteria

1. An exact identity read after the first page-state Runtime timeout still
   opens one fresh blank target and replays navigation/readback once.
2. A successful second read proceeds normally; a second Runtime timeout stops
   as `agent_browser_timeout` with no third target or attempt.
3. Non-timeout failures remain terminal without recovery, and existing
   navigation, extraction, quality, auth, rate-limit, and item-limit semantics
   do not change.
4. Focused Facebook tests, the complete Python and Go suites, compileall,
   release/runtime/package/plan audits, patch checks, and two reproducible
   0.3.32 builds pass.
5. Exact 0.3.32 installation preserves schema 16, database integrity,
   schedule identity/cadence, Facebook readiness, rollback, zero-cost posture,
   retained browser PID 63205, and the pre-install 19-tab count.
6. Facebook remains manual and not routine-qualified. A later proof requires a
   fresh no-launch readiness gate, matching preflight, at least 60 minutes from
   the consumed attempt, one enqueue, and no retry.

## Definition Of Done

- criteria 1-5 have exact repository and installed-runtime evidence;
- this plan closes as offline-qualified while criterion 6 remains the explicit
  P13 live gate;
- plan, roadmap, runbook, receipt note, installed runtime, Git history, and one
  bounded Graphiti write attempt agree.

## Execution Bounds

- primary agent owns the serialized critical path; no subagent is used;
- one implementation/build/install candidate and one remediation cycle;
- zero live Facebook ticks and zero direct browser operations in this packet;
- hard stop on challenge/auth/rate-limit evidence, browser/profile ownership
  ambiguity, schedule drift, database failure, nonzero cost/model use, or an
  unsafe dirty worktree.

## Owned Write Surfaces

- `skills/last30days/scripts/lib/facebook.py`;
- `tests/test_facebook.py`;
- service version, runtime manifest, changelog, predecessor/current plans,
  `ROADMAP.md`, `RUNBOOK.md`, and one serial evidence note.

### Checkpoint P0031-C01 | 2026-08-09

Plan version: 1

State transition:

- `live_qualification_rejected -> offline_recovery_repair_active`.

Progress classification:

- `blocker_reduction`; the consumed receipt identifies the exact fallback
  branch and an existing bounded recovery mechanism.

Validation evidence:

- live receipt and agent-browser operation sequence are frozen in Plan 0030
  checkpoint C02; CodeGraph traces `_facebook_adapter` into
  `FacebookScraper._navigate` and confirms the identity shortcut bypasses the
  fresh-target branch;
- the worktree began clean at `3f71b530997dd6623a7d50fa8bda81ac18650342`.

Subagent status and reconciliation:

- none; source, focused regression, release, and installation are one
  serialized contract path.

Authority classification:

- `inherited_authority`; this bounded offline successor preserves the approved
  objective, safety controls, systems, limits, and live-effect boundary.

Graphiti write status:

- pending one compact post-commit attempt after terminal validation.

Next action:

- change the identity-timeout regression first, implement the minimal fallback
  repair, then widen validation before build/install.

### Checkpoint P0031-C02 | 2026-08-09

Plan version: 2

State transition:

- `offline_recovery_repair_active -> offline_recovery_installed_gated`;
- `OPEN -> CLOSED` successfully for the bounded offline objective.

Progress classification:

- `blocker_reduction`; exact identity can no longer route extraction onto a
  target whose Runtime just timed out.

Validation evidence:

- the matching-identity regression now requires exactly two page-state reads
  and action prefix `navigate, wait, new_tab, navigate, wait`; the repeated
  timeout and non-timeout terminal regressions pass unchanged;
- focused Facebook/worker/runtime/release/package tests pass; the complete
  Python suite, all Go MCP packages, compileall, plan audit, runtime package,
  and patch checks pass;
- two independent 0.3.32 builds are byte-identical at SHA-256
  `fe673ab03c165b3e61a360bb9d801d60e3e90a4c12a307f21e9a99f275eeb82d`;
- installed 0.3.32/schema16 is ready with contract SHA-256
  `fe8727fbe0d4e2f6775f49a6fc958369fe4877ba812bae4ef69121b88f12e2f1`
  and runtime-manifest SHA-256
  `5170c1d37ab280d772bfb9dab17f71bf90aa71d3485be48cd093f9c7f813ea33`;
- SQLite quick check is `ok`; releases 0.3.29 through 0.3.32 are retained;
  `daily-default` is enabled/ready at 86,400 seconds with next boundary
  `2026-08-10T00:00:00Z`; Facebook is acquisition-ready;
- browser `session:last30days-facebook`, PID 63205, remains ready/viable with
  19 tabs, queue depth zero, and waiting profile-lease depth zero. The packet
  opened, navigated, or closed no browser or tab;
- `npx skills add . -g -y` refreshed both copied skills across supported hosts;
  PromptScript's two truthful unsupported-global-install results were the only
  reported failures.

Subagent status and reconciliation:

- none; the primary independently implemented and verified the serialized
  critical path.

Authority classification:

- `inherited_authority`; the offline successor stayed inside all standing
  systems, effect, safety, provider, cost, and resource bounds.

Graphiti write status:

- pending one compact source-backed attempt after the durable commit.

Next action:

- Plan 0032 owns one later guarded 0.3.32 Facebook-only proof. It may not run
  before `2026-08-09T16:19:07Z`, must use a fresh matching no-launch preflight,
  and cannot be retried.
