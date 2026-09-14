# Plan 0113 | Hotfix Runtime And Operator Closure

State: OPEN
Lane: P38
Work item: WI-007
Branch: feat/hotfix-runtime-drill-v1
Target: main
Integration: merge
Roadmap: P38
Plan version: 1
Date: 2026-09-14
Execution owner: /root/wi007_packet3_planning
Coordination owner: /root
Requested model route: gpt-6-astra, high reasoning
Effective runtime model: unknown; not reported by runtime
Effective runtime reasoning: unknown; not reported by runtime

## Objective

Complete WI-007 provider-free by composing the reproducible builder and
installer into a disposable release/rollback drill, adding deterministic
preflight/report operator tooling, and proving the reserved real slot returns
to dormant without provisioning operational staging.

## Current State

Provider-free control and Git drills are integrated through PR 79. WI-001
provides an isolated development-runtime pattern, not operational staging.
Builder/installer tests cover low-level lifecycle recovery, but no reusable
hotfix drill binds their artifact, database, process, and receipt identities to
WI-007's state machine.

The assigned lane is activated for plan-only publication. Implementation,
artifact builds, and disposable runtime execution remain held until the
coordinator reconciles the activation and resumes this owner explicitly.

## Scope

- add a repo-only runtime drill using owned temporary roots, synthetic database,
  fake user manager, private sockets, allowlisted environment, and exact
  process ownership;
- build fixed source twice and bind artifact/manifest/source identity without
  changing fixture versions or repository release metadata;
- exercise successful upgrade, failed-upgrade restoration, deliberate rollback,
  rollback-forward, and a truthful terminal recovery failure when needed;
- compose results into existing hotfix receipts without treating simulated Git,
  staging, or authorization as operational proof;
- add read-only preflight/report plus explicit disposable drill commands and
  operator guidance; run one fresh complete provider-free drill and retain its
  bounded receipt bundle.

## Non-Goals

No real incident/hotfix branch, installed user service, operational staging,
production, provider/browser, credentials, release metadata/tag/publication,
GitHub issue, deployment, or rollback effect.

## Acceptance Criteria

1. Preflight rejects dirty/stale source, manifest drift, foreign/redirected
   roots, ambient credentials/config, real manager paths, and identity mismatch
   before mutation.
2. Fixed-input builds are byte-identical and bind to the actual clean source;
   fixture versions never edit release metadata.
3. Installer readbacks prove exact releases, schema, manifest, contract,
   readiness, sentinel restoration, and retained raw failed attempts.
4. Each scenario permits at most one upgrade and one recovery rollback;
   rollback-forward is separately declared rather than an automatic retry.
5. Teardown verifies process owner/birth identity, fresh OS census finds no
   fixture process, and exact cleanup preserves foreign sentinels.
6. Report validation preserves simulated-versus-operational distinctions and
   the final receipt maps every WI-007 criterion with the real slot dormant.
7. Focused lifecycle/package/control tests, one fresh composed drill, full
   provider-free presubmit, authority audits, and diff checks pass.

## Execution Packet

- one top-level implementation owner, no children; two implementation attempts,
  one independent review, one closed-world remediation pass;
- lane-owned writes: new runtime drill/operator entrypoint, focused tests,
  operator doc, bounded receipt, and this plan; narrow existing hotfix module
  changes only when composition proves necessary;
- builder, installer, runtime controller, version/changelog, public contracts,
  generated catalogs, and manifest are reference-only unless a blocker is
  returned to the coordinator; authority projections are coordinator-only;
- terminal condition: published provider-free acceptance making WI-007 eligible
  for repo-local DONE, or one exact blocker. The production hotfix slot is never
  activated by this packet.

## Definition Of Done

All seven criteria pass at one published checkpoint, the durable receipt is
independently verifiable, and no operational staging or production claim is made.

## Current Checkpoint

### Checkpoint P0113-C01 | 2026-09-14

Plan version: 1

State transition: `planned -> activation_published`.

Progress classification: `blocker_reduction`; exact execution ownership and
recoverable branch custody are established. All seven implementation acceptance
criteria remain unproved by this activation.

Authority classification:

- `inherited_authority` from Plan 0107 and the coordinator's activation-only
  assignment covers reading current policy/evidence, editing only this plan,
  validating the document, committing, and publishing its assigned branch;
- implementation and all build/runtime execution are held until coordinator
  activation reconciliation and a separate resume instruction;
- every installed-service, operational-staging, production, provider/browser,
  credential, schedule, issue, release publication, deployment, and operational
  rollback effect remains outside this assignment.

Ownership and custody:

- execution owner: `/root/wi007_packet3_planning`; coordinator: `/root`;
- worktree: `/home/ecochran76/workspace.local/last30days-skill-wi007-v2`;
- branch: `feat/hotfix-runtime-drill-v1`; target: `main`; integration by
  coordinator-owned reviewed pull request to the owned public fork;
- exact activation base: `7f65c4285146e8d4dabd417617584fe7042a582f`;
- initial lane checkout is clean at that base. Canonical
  `/home/ecochran76/workspace.local/last30days-skill` owns clean `main`, equal
  to local `origin/main` and live owned-fork `refs/heads/main` at the same base;
- publication establishes `origin/feat/hotfix-runtime-drill-v1`; the exact
  checkpoint is the commit containing this activation, returned with verified
  live remote equality and clean status. No historical custody is changed.

Inputs, evidence, and overlaps:

- re-read current planning, Git/commit/integration, documentation, validation,
  goal, active-lane, subagent, work-item, operating-model, model-routing, and
  collaborative-workflow policies before activation;
- current Plan 0107, Plan 0113, and WI-007 preserve the provider-free boundary;
  the prior read-only audit inspected note 0122 and its JSON companion, closed
  Plan 0110, WI-001/Plan 0106/receipt 0126, and current builder/installer tests;
- WI-001 acceptance supplies development isolation, not operational staging.
  This activation makes no current production identity or runtime-health claim;
- this checkpoint writes only this plan. Prospective implementation owns
  repo-only hotfix drill/operator code, focused tests, operator guidance, and
  bounded receipts, with narrow existing hotfix-module changes when required;
- no expected implementation overlap with concurrent search/follows packets.
  Builder, installer, lane runtime, manifest, release metadata, public schemas,
  generated catalogs, and CI remain reference-only pending coordinator
  disposition of any demonstrated blocker; shared authority is coordinator-only;
- requested route remains `gpt-6-astra`, high reasoning for installer recovery,
  containment, and receipt-identity composition. Effective model and reasoning
  are unknown; no runtime override or child is requested;
- Graphiti discovery is skipped because exact current authorities and the
  completed bounded audit suffice. Graphiti write status: `not_written`.

Validation and next action:

- plan-authority audit passed: two active authority plans, zero issues;
  goal-only planning audit passed; this plan's filename, state, lane, and
  current-state checks passed; inspected one-file diff and `git diff --check`
  passed;
- active planning audit failed only on six shared-projection findings: each of
  Plans 0111, 0112, and 0113 is not wired in ROADMAP.md and RUNBOOK.md. These
  findings are reported to the coordinator for activation reconciliation;
  this plan-only assignment does not change those shared files or claim the
  active audit passed;
- no implementation tests, builds, installer commands, service starts/stops,
  providers, or operational checks run during activation;
- publish the one-file activation, verify local/upstream/live-remote equality,
  and return its exact SHA. Then wait for the coordinator to reconcile the
  activation and resume this same lane owner.

Stop condition: do not implement, build, run a fixture/runtime, mutate shared
authority, open a pull request, change issue state, or spawn children during
this activation. Stop on unexpected dirt, branch/base mismatch, or publication
divergence and return the exact evidence to the coordinator.
