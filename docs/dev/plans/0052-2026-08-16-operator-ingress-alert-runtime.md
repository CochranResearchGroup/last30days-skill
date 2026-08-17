# Plan 0052 | Operator-Ingress Alert Runtime Correction

State: CLOSED
Roadmap: P08
Plan version: 2
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

### Checkpoint P0052-C01 | 2026-08-16

Plan version: 2

State transition:

- `operator_ingress_alert_runtime_candidate -> installed_alert_taxonomy_accepted`.

Progress classification:

- `outcome_progress`; the installed runtime now distinguishes an unavailable
  operator route from an observed provider authentication failure.

Validation evidence:

- exact pushed candidate `f378ab4` produced two byte-identical service 0.3.51
  artifacts at SHA-256
  `1c0144eea45ea7c51387a9b06a25e9812f6b0cba2b610d2ca2f0185ae6bac633`;
- focused release/package/incident/runner/runtime validation passes 63 tests;
  the terminal full suite passes 2,655 tests, seven skips, and six subtests;
  the active planning audit and `git diff --check` pass;
- transactional upgrade reports service 0.3.51/schema 16 ready with runtime
  manifest SHA-256
  `3cd3ae1113f728d00d9fac8324c1cfc1fe00b80475ae127b5afcadafa44b47cf`,
  unchanged contract SHA-256
  `fe8727fbe0d4e2f6775f49a6fc958369fe4877ba812bae4ef69121b88f12e2f1`,
  and 0.3.50 retained as rollback;
- fresh MCP readback is `compatible` on adapter 4.0.3. The managed systemd
  unit is active/running, SQLite `quick_check` is `ok`, and all 51 recorded
  execution attempts are terminal (49 complete, two failed);
- direct import from the installed `current` release maps
  `operator_ingress_unavailable -> provider_degraded` with summary
  `authentication state was not determined`, while `auth_required` and
  `checkpoint_required` still map to `reauthentication_required`;
- `daily-default` remains enabled/ready after its Aug 17 tick terminalized
  `complete_degraded`; its next boundary is Aug 18. No collection tick,
  browser action, source-config change, or notification delivery was performed
  by this packet.

Authority classification:

- `explicit_authority`; the operator directly requested the runtime upgrade
  after reviewing the false LinkedIn logout alert diagnosis.

Subagent status and reconciliation:

- `not_spawned`; current orchestration policy prohibits delegation.

Graphiti write status:

- not added because this correction and every acceptance receipt are already
  durable in the pushed plan, runbook, artifact, and installed-service state.

Next action or stop reason:

- stop. Preserve service 0.3.51; independently restore and prove the exact
  `last30days-facebook` browser/profile/route before any future social canary.
