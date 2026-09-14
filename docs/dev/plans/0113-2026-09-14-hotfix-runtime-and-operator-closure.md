# Plan 0113 | Hotfix Runtime And Operator Closure

State: PLANNED
Lane: P38
Work item: WI-007
Branch: feat/hotfix-runtime-drill-v1
Target: main
Integration: merge
Roadmap: P38
Plan version: 1
Date: 2026-09-14
Execution owner: unassigned until activation
Coordination owner: /root
Requested model route: gpt-6-astra, high reasoning
Effective runtime model: unknown until reported

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

