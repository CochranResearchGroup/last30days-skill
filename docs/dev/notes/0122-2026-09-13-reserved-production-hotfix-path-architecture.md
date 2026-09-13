# Reserved Production Hotfix Path Architecture

Date: 2026-09-13
Work item: WI-007
Plan: 0081
Repository checkpoint: `0950077e53c6a39e47df1385bf5ae32bec4f3dca`
Investigation mode: stable local Git repository, release/hotfix architecture
and mixed code/docs synthesis, hybrid structure-first retrieval

## Decision

Reserve one dormant hotfix lane that activates only for a qualified
production-impacting defect. It owns no permanent branch, worktree, runtime, or
deployment authority while idle. On activation it creates one short-lived
`hotfix/<work-item>-<slug>` branch and worktree from exact current
`origin/main`, registers custody at the earliest safe checkpoint, and receives
priority review and integration ahead of conflicting feature work.

The path is a state machine with separate proof boundaries:

`reported -> qualified -> active -> fix_ready -> integrated -> staging_accepted
-> deploy_authorized -> deployed_verified -> closed`

Failure may transition to `reframed`, `blocked`, `rolled_back`, or `cancelled`.
Source integration, release build, staging acceptance, deployment authority,
production mutation, production verification, and rollback are never collapsed
into one “shipped” state.

Packet 1 is a provider-free drill of the control plane. It may begin before the
isolated runtime lane is implemented. Staging execution and any real deployment
remain gated by WI-001 and explicit action-specific authority.

## Current Evidence

- canonical `main` is clean and synchronized with the owned public fork;
- the installed production service remains active/running on PID 24968 and
  reports `0.3.116`, schema 17, ready state, 167 documents, and immutable index
  head `index-e51e8df608f7374bd1d89b9b`;
- `service/scripts/build-runtime.sh` verifies a canonical content manifest and
  produces a reproducible versioned tarball when `SOURCE_DATE_EPOCH` is fixed;
- `service/scripts/install.sh` already owns user-scoped install, upgrade,
  status, diagnose, start/stop, readiness, release retention, database
  snapshots, deliberate rollback, and failed-upgrade restoration;
- installer tests exercise clean install, upgrade, rollback, rollback-forward,
  schema mismatch, corrupt rollback metadata, and recovery failures using an
  isolated fake user manager;
- current policy already reserves one hotfix slot outside the three-feature
  WIP limit, requires current-main start and priority integration, and requires
  affected feature branches to reconcile afterward;
- no durable incident qualification, hotfix manifest, conflict-freeze receipt,
  promotion ledger, staging receipt, deployment authorization record, or
  post-hotfix reconciliation report binds those pieces together.

Graphiti discovery recovered older reproducible artifact and rollback proofs,
but their installed versions are stale. Current source, tests, Git, and live
read-only runtime evidence are authoritative here.

## Activation And Qualification Contract

A hotfix lane activates only when `HotfixCaseV1` exists with:

- schema version, stable work-item/incident locator, reporter, and observed
  time;
- concise expected versus observed behavior and current reproducer evidence;
- affected production service/API/schema/manifest identities;
- impact class, affected users/functions, and uncertainty;
- suspected write surfaces and feature-lane overlaps;
- immediate containment status and whether external effects are continuing;
- rollback target/readiness snapshot if a deployed regression is suspected;
- explicit non-goals, stop conditions, and authority classification.

Qualification requires current evidence that production behavior is degraded,
incorrect, unsafe, or materially unavailable. A speculative feature request,
test-only failure, stale report, or unverified provider symptom stays in normal
triage. Security-sensitive incidents use the private security route; they are
never copied into public issues or ordinary runbook text.

The coordinator is activation controller. It records `qualified` or a bounded
non-hotfix disposition. GitHub issue publication is optional until tracker
activation; the stable repo-local work-item locator remains sufficient.

## Custody, Priority, And Concurrency

On activation:

1. fetch the owned fork and prove canonical `main == origin/main`;
2. inspect registered worktrees/branches and current production identity;
3. create the hotfix branch/worktree from that exact commit;
4. register lane ID, branch, target, checkpoint, overlaps, affected lanes,
   integration mode, incident locator, and effect gates;
5. publish the first coherent recoverable checkpoint;
6. pause only feature work whose write surface or acceptance evidence conflicts.

The hotfix slot does not count against the three-feature WIP limit. There is at
most one active production hotfix lane unless a new plan explicitly proves
independent systems and integration surfaces. A second incident is joined,
queued, or escalated; it does not silently create another production mutation
controller.

Hotfix changes preserve current behavior except for the qualified defect.
Opportunistic refactors, migrations, features, dependency churn, and unrelated
cleanup are excluded. If the smallest safe fix requires a broader migration,
the lane reframes under a new plan before coding continues.

## Fix And Review Contract

`HotfixCandidateV1` binds:

- incident/work-item locator and qualified case digest;
- base, head, and target commits;
- exact changed files and generated artifacts;
- regression reproducer before/after evidence where practical;
- focused and safe-fallback test selections;
- migration/API/config/runtime compatibility assessment;
- release increment requirement and changelog/operator impact;
- rollback compatibility and staged-data preservation result;
- reviewer findings and primary-agent disposition;
- remaining risks and the next exact gate.

The fix is implemented in the dedicated lane and reviewed through a priority PR
to the owned fork's `main`; never upstream. A hotfix does not bypass security,
contract, manifest, or test gates. Review scope is the frozen defect plus
critical regressions introduced by the fix. A clean diff or issue closure is
not acceptance evidence.

If production harm is ongoing, reversible containment may precede the source
fix only under its own explicit authority and receipt. Containment does not
authorize deployment or close the incident.

## Integration And Feature Reconciliation

The coordinator merges the accepted hotfix before conflicting feature PRs.
The merge receipt records PR, source tip, merge commit, target ancestry, and
validation. Every affected feature lane then rebases or merges the integrated
hotfix according to its published/shared state and reruns its affected gates.

`HotfixReconciliationReportV1` lists each registered feature lane as:

- `unaffected`, with evidence;
- `reconciled`, with old/new checkpoint and validation;
- `paused`, with exact conflict/blocker;
- `superseded` or `cancelled`, with disposition.

No affected feature lane may integrate from a pre-hotfix base merely because
its earlier tests passed. Unaffected lanes may continue. Shared roadmap,
runbook, catalog, schema, and release metadata reconciliation remains
coordinator-owned.

## Staging Gate

Staging is a deployment identity, not a Git branch. After WI-001 supplies the
isolated/staging controller, the exact clean integrated commit and reproducible
artifact are installed into the staging identity with separate config root,
database snapshot, socket, logs, credentials/effect policy, and process
identity.

`HotfixStagingReceiptV1` pins:

- integrated commit, version, artifact and runtime-manifest digests;
- source and target schema/API/contract compatibility;
- fixture/snapshot provenance and pre/post integrity counts;
- focused reproducer, presubmit, smoke, restart, and rollback-drill results;
- enabled schedules/providers and evidence that unintended effects stayed off;
- process birth identity, readiness, logs, cleanup, and residual risk.

Provider/browser canaries are not implied by staging. If the defect cannot be
validated without one, it uses a separately authorized serialized canary.

An emergency staging bypass is not a routine flag. It requires explicit
operator authority for the exact deployment, documented consequence of delay,
minimum substitute evidence, a confirmed rollback target, and an immutable
bypass receipt. No architecture or test result grants that authority.

## Release And Deployment Gate

The candidate release must:

- use the repository's next valid semantic version and updated changelog;
- build twice reproducibly from the exact clean integrated commit when
  practical, with artifact digest equality;
- pass runtime-manifest and contract-catalog validation;
- prove database forward migration and retained rollback compatibility;
- retain exact current and previous release/database snapshot identities;
- pass staging acceptance or carry an explicitly authorized bypass receipt.

`HotfixDeploymentAuthorizationV1` names the exact artifact digest, target
service, window, operator, allowed actions, rollback target, attempt/time bound,
and stop conditions. It is action-specific. Merge, build, staging success, or
general goal authority does not substitute for it.

The deployment controller serializes production mutation: preflight readback,
one bounded upgrade attempt, readiness, postcondition checks, and either
acceptance or rollback. No feature lane deploys concurrently.

## Production Verification And Rollback

Before mutation, capture current service/version/API/schema/manifest, process
identity, database quick/FK checks, corpus/index counts and heads, schedule/job
state, rollback release/snapshot integrity, and relevant defect baseline.

After upgrade, require:

- exact installed artifact/version/manifest/contract readback;
- active/running ready process with a new birth identity when restarted;
- database integrity and expected schema;
- preserved corpus/index/coverage counts within declared migration semantics;
- focused defect postcondition and bounded critical smoke;
- unchanged or explicitly intended schedule/provider state;
- no new critical incidents during the observation bound.

Rollback is mandatory on readiness, integrity, compatibility, manifest,
critical-smoke, or declared stop-condition failure when safe rollback remains
possible. The existing installer is the mutation mechanism; orchestration does
not reimplement its atomic switch or database restoration.

Rollback verification repeats installed identity, process readiness, database
integrity, corpus/index counts, schedule/job state, and original-behavior
readback. If rollback itself cannot restore a safe ready state, stop further
automation and report the exact terminal state; do not loop upgrades.

## Evidence And Closeout Contract

`HotfixCloseoutReceiptV1` includes:

- case, candidate, PR, merge, release, staging, authorization, deployment, and
  rollback locators as applicable;
- before/after production identities and observations;
- all validation tiers actually run and explicit exclusions;
- affected feature reconciliation results;
- incident outcome: fixed, contained, rolled_back, not_reproduced, cancelled,
  or blocked;
- remaining risks, follow-up items, cleanup, and exact final Git/runtime state.

The work item closes only when source, integration, runtime disposition,
feature reconciliation, and cleanup agree. A rolled-back fix may close the
deployment attempt but not falsely claim the defect fixed.

## Vertical Delivery Packets

1. Control-plane drill: strict case/candidate/reconciliation/staging/
   authorization/deployment/closeout contracts; state transitions; conflict
   matrix; fake Git/runtime/review adapters; dormant-slot and one-hotfix
   invariants; provider-free tests. No branch, process, artifact, or service is
   created by the test fixture outside its temporary root.
2. Repository integration drill: use disposable Git repositories/worktrees to
   prove current-main branching, priority integration receipts, affected-lane
   pause/reconcile, divergence failure, and exact cleanup. No GitHub mutation.
3. Runtime/release drill: after WI-001 supplies staging identity, compose the
   existing reproducible builder and installer against a fake user manager and
   disposable database; prove staging, failed upgrade restoration, rollback,
   rollback-forward, and receipt parity without installed or production state.
4. Operator surface and closeout: document incident activation and exact
   commands, add deterministic preflight/report tooling, run one fresh full
   provider-free drill, and retain the lane dormant. A real incident,
   deployment, canary, or production rollback remains event- and authority-
   specific rather than a prerequisite for the drill.

## Expected Write Surfaces

- repo-only hotfix contracts/controller and tests under `dev/last30days/` and
  `tests/`;
- existing build/install interfaces only through composition, with changes
  limited to proven gaps;
- fixture Git repositories, fake user-manager/runtime adapters, and bounded
  receipts;
- operator docs and release/checklist guidance;
- plan, roadmap, runbook, work item, and active-lane custody.

The lane owner must coordinate roadmap/runbook/catalog, CI, release metadata,
service manifest, installer, and shared-schema edits with the coordinator.

## Provider-Free Acceptance Boundary

- dormant state owns no branch, worktree, process, port/socket, database,
  credential, schedule, or deploy authority;
- activation rejects stale base, dirty canonical state, ambiguous incident,
  second active hotfix, missing rollback evidence, and unregistered overlap;
- a simulated hotfix starts from exact default-ref, integrates before a
  conflicting feature, and forces that feature through explicit reconciliation;
- staging, deploy authorization, deployment, verification, and rollback remain
  separate states and receipts;
- fake install/upgrade/readiness failure/rollback paths preserve or restore the
  exact disposable database and release identities;
- timeouts and ambiguous operations reconcile before retry; no loop exceeds
  one deployment plus one rollback attempt in the drill;
- final cleanup removes only exact test-owned worktrees/processes/artifacts and
  leaves canonical Git plus the real production service unchanged;
- no test uses GitHub writes, network, provider/browser, credential, installed
  Skill/runtime/database, schedule, staging, or production mutation.

## Open Questions For The Lane Owner

- Freeze the smallest conflict-matrix fixture covering unaffected, overlapping,
  diverged, and already-integrated feature branches.
- Measure provider-free Git and fake-installer drill time before setting the
  blocking presubmit budget.
- Decide whether the operator-facing preflight remains one repo-only command or
  is projected into the future runtime controller after WI-001 acceptance.

## Graphiti Write Status

`graphiti_write_pending`: Plans 0076-0080 already await recovery of the known
degraded ingestion path. This architecture does not queue another write.

## Skill Friction

The shared `codebase-investigator` optional example files remain absent. The
core references and current source evidence were sufficient.

## State Location

This note and its machine-readable companion are durable in the stable Git
repository. No bundle or snapshot is needed.
