# Plan 0065 Post-Repair Admission Blocker

Date: 2026-09-10 America/Chicago (`2026-09-11` UTC)

Plan: [0065](../plans/0065-2026-09-10-post-repair-bounded-tick-gate.md)

## Result

The reported repairs are materially present, but the new manual tick was not
admitted because a later Agent Browser workstation transaction left global
runtime admission draining.

- Last30days service: 0.3.114, schema 17, ready.
- Last30days repair: commit `dfe69f9` preserves Agent Browser terminal recourse
  and stops same-provider blind retry.
- Profile: `last30days-facebook` is available with zero holders, browsers,
  tabs, conflicts, waiting jobs, or profile-scoped doctor issues.
- Preflight: ready for prospective tick
  `tick-a3b3b349d40c412ae32aa8e2a81d613a` under manual schedule
  `manual-p0065-20260911-010623` and the unchanged saved configuration digest
  `sha256:8e3811d5e9b561cfd3f97b3d9897770ee4c623fe9e74a443bc01d86fca4d3449`.
- Durable tick admission: not attempted; the prospective tick ID is absent.

## Exact Agent Browser Gate

X, LinkedIn, and Reddit no-launch access plans all returned:

```text
runtime_admission_draining: transaction
upgrade-bc9935eb-9425-426b-a8bf-fe8e2d00fc14 is transferring runtime
ownership
```

Transaction inspection is newer and more specific:

- revision: 12;
- state and terminal result: `operator_recovery_required`;
- stop reason: `candidate_dashboard_presentation_unproven`;
- candidate generation: `0.28.0-6057ce460890-9a601028e745`;
- old/current selected generation: `0.28.0-cf47afe1c587-a50f7b20bc11`;
- runtime census: stable;
- runtime handoff: committed but source not finalized;
- outstanding owner obligations: one;
- rollback ready: true;
- safe actions: inspect and recover; next safe action: recover.

Current doctor/runtime evidence:

- two runtime hosts and two executable generations;
- multiplicity state `drift`, not steady;
- reconciliation not ready;
- runtime monitor in backoff after six consecutive failures;
- active runtime incident reason
  `generation_gc_blocked_by_active_admission_drain`;
- supervisor ready with no supervisor issue;
- no `last30days-facebook` profile-scoped doctor issue;
- service-state lock diagnostics have no active holder and no file or process
  timeout in the current process-local window.

This is a runtime-maintenance/admission blocker, not evidence that the repaired
profile is still broken. Operator presentation was not requested by the
Last30days tick, although the upgrade transaction's own stop reason concerns
candidate dashboard presentation.

## Corroborating Timer Evidence

The independent September 11 `daily-default` tick
`tick-038549394cbc2489554f3327fab78d04` terminalized
`complete_degraded` before this manual preflight. YouTube accepted three items;
X failed once and LinkedIn failed three times on
`runtime_admission_draining`. Reddit stopped after its first Agent Browser
failure, demonstrating that the Last30days 0.3.114 retry-recourse repair is
active. That timer result is corroboration only; it is not the requested manual
attempt.

## Safe Handoff

The Agent Browser owning lane should inspect and recover or terminally resolve
transaction `upgrade-bc9935eb-9425-426b-a8bf-fe8e2d00fc14`, then verify one
runtime host, one executable generation, cleared admission drain, and successful
no-launch access plans for the three social targets. Do not treat profile
availability alone as sufficient admission proof. No Last30days tick, profile
mutation, browser launch, or Agent Browser recovery was performed here.
