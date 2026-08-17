# Plan 0052 | Operator-Ingress Alert Runtime Correction

State: OPEN
Roadmap: P08
Plan version: 1
Date: 2026-08-16

## Objective

Stop an unavailable Guacamole/dashboard route from being reported as proof
that LinkedIn or another browser-backed provider is logged out, then build and
transactionally install the correction as service 0.3.51.

## Current State

- service 0.3.50/schema 16 is installed, ready, and compatible with MCP 4.0.3;
- Plan 0051 recorded LinkedIn `operator_ingress_unavailable`, but the incident
  classifier converted that exact runtime failure into
  `reauthentication_required` and delivered a misleading Slack alert;
- genuine `auth_required` and `checkpoint_required` signals must continue to
  produce reauthentication incidents;
- the worktree was clean at pushed `origin/main` commit `efb8a84` before this
  isolated repair branch was created.

## Scope

- classify `operator_ingress_unavailable` as existing incident type
  `provider_degraded` rather than `reauthentication_required`;
- retain the exact route failure in the safe notification summary and state
  explicitly that authentication was not determined;
- update deterministic tests and operator-facing error guidance;
- build, validate, commit, push, and transactionally install service 0.3.51;
- verify installed identity, rollback identity, compatibility, schedule health,
  and database integrity after the one managed restart.

## Non-Goals

- do not open a provider page, inspect cookies, authenticate, repair the
  browser profile/route, or run a collection tick;
- do not change source enablement, recurring ceilings, cadence, budgets,
  selectors, retries, schemas, MCP/Skill versions, or notification transports;
- do not retroactively rewrite the already-delivered Plan 0051 incident.

## Acceptance Criteria

1. Deterministic classification proves route ingress maps to
   `provider_degraded`, while authentication and checkpoint signals retain
   `reauthentication_required`.
2. The generated notification summary for ingress failure says authentication
   was not determined and does not request sign-in.
3. Focused incident/runner/runtime tests, the full suite, package tests, and two
   reproducible service builds pass for exact service 0.3.51.
4. The transactional installer retains 0.3.50 as rollback and reports installed
   0.3.51/schema 16 ready with exact artifact and runtime-manifest identities.
5. MCP compatibility, SQLite integrity, and the recurring schedule remain
   healthy, with no collection tick or browser mutation performed.

## Definition Of Done

- the exact committed and pushed 0.3.51 artifact is installed and ready; its
  validation and postflight receipts are recorded here and in `RUNBOOK.md`,
  P08 is reconciled, and this plan is `CLOSED`.
