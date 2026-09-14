# Plan 0110 | Hotfix Control And Git Drill

State: OPEN
Lane: P38
Work item: WI-007
Branch: feat/hotfix-control-v1
Target: main
Integration: merge
Roadmap: P38
Plan version: 1
Date: 2026-09-14
Execution owner: /root/wi007_hotfix_drill
Requested model route: gpt-6-astra, high reasoning
Effective runtime model: unknown; not reported by runtime
Effective runtime reasoning: unknown; not reported by runtime

## Objective

Implement WI-007 provider-free Packets 1-2 as a strict dormant hotfix state
machine plus disposable-Git integration drill, without activating a real
incident or touching any installed/runtime/production state.

## Current State

The accepted architecture defines case, candidate, reconciliation, staging,
authorization, deployment, rollback, and closeout boundaries. This development
lane is activated on `feat/hotfix-control-v1`; implementation remains pending.
No hotfix controller, drill, incident branch, runtime, artifact, incident, or
production mutation has been created. The reserved production slot is dormant.

## Scope

- implement strict contracts, transitions, conflict matrix, fake Git/runtime/
  review adapters, dormant-slot, and one-hotfix invariants;
- use disposable repositories/worktrees to prove exact-main branching,
  priority integration receipts, affected-lane pause/reconciliation, divergence
  failure, and exact cleanup;
- distinguish integrated, staging-accepted, deploy-authorized, verified,
  rolled-back, cancelled, and blocked states without granting effects;
- keep every fixture inside its temporary root and network/provider free.

## Non-Goals

- no real incident, hotfix branch, GitHub mutation, build/install, service
  process, staging, deployment, rollback, browser/provider, credential, release,
  schedule, or production action;
- no Packet 3 runtime/release drill or Packet 4 operator closeout.

## Acceptance Criteria

1. Dormant state owns zero resources/authority and activation rejects ambiguous
   case, stale base, dirty main, second hotfix, missing rollback evidence, and
   unregistered overlap.
2. Strict receipts and state transitions prevent integration, staging,
   authorization, deployment, verification, rollback, and closeout from being
   collapsed or skipped.
3. Disposable Git drills prove priority integration and every affected feature
   is classified unaffected, reconciled, paused, superseded, or cancelled.
4. Divergence and cleanup failures fail closed; cleanup targets only exact
   fixture-owned paths/refs.
5. Focused and safe-fallback provider-free suites pass with the real canonical
   repo and production service unchanged.

## Definition Of Done

All five criteria pass at one published checkpoint suitable for reviewed PR
integration, or one exact blocker is recorded without beginning Packet 3.

## Current Checkpoint

### Checkpoint P0110-C01 | 2026-09-14

Plan version: 1

State transition: `planned -> activation_published`.

Progress classification: `blocker_reduction`; execution ownership, bounded
write surfaces, and recoverable lane custody are established for campaign
registration. No product acceptance criterion is claimed complete.

Authority classification:

- `inherited_authority` from Plan 0107 and the coordinator's activation-only
  assignment for reading the current authorities, changing this plan, and
  committing/pushing this plan alone to the owned-fork lane branch;
- implementation remains held until the coordinator reconciles Wave 1 lane
  activation into canonical authority and sends the implementation task;
- no provider/browser, credential, issue, installed/runtime/live, staging,
  release, deployment, rollback, or production effect is authorized here.

Ownership and exact custody:

- execution owner: `/root/wi007_hotfix_drill`, parent coordinator `/root`;
- requested route: `gpt-6-astra`, high reasoning, as recorded in the plan seed;
  effective model and reasoning are unknown because the runtime did not report
  them; no model override or nested agent is requested by this activation;
- worktree: `/home/ecochran76/workspace.local/last30days-skill-wi007-v1`;
- branch: `feat/hotfix-control-v1`, target `main`, integration by reviewed PR;
- exact activation base: `bca720d0406d8a4f6a8d9ac645eceeead20b8432`;
- canonical worktree `/home/ecochran76/workspace.local/last30days-skill` owns
  clean `main`, equal to local `origin/main` and live owned-fork `refs/heads/main`
  at that base before activation;
- the assigned worktree was clean at the same base and initially tracked
  `origin/main`; the activation publication establishes
  `origin/feat/hotfix-control-v1` as its upstream;
- the exact activation commit is the commit containing this checkpoint and is
  returned to the coordinator with verified remote equality for cataloging.

Inputs and discovery:

- read current AGENTS.md and required policies 0001, 0005, 0006, 0007, 0012,
  0013, 0015, 0019, 0021, 0023, 0025, 0026, 0027, 0028, 0029, and 0032, plus
  commit/integration policies 0008-0010; read Plans 0107, 0110, 0081, note 0122
  and its JSON companion, and WI-007;
- Graphiti discovery: `skip`; current supplied authorities suffice for this
  bounded activation. Older architecture runtime readbacks are historical and
  are not asserted as current production evidence;
- the lane worktree has no CodeGraph index. Read-only exploration used the
  canonical index at the identical base; indexed reference files have no diff
  between lane HEAD and canonical main. No index initialization was performed;
- canonical CodeGraph reports 376 files, 10,596 nodes, 26,335 edges, up to date,
  with an older-engine rebuild advisory. Its cross-worktree warning is bounded
  by the exact base/read-only reference comparison above;
- no `Hotfix` symbol was found. Exploration of `lane_runtime.py`,
  `test_lane_runtime.py`, and `test_service_runtime_package.py` exposes existing
  fail-closed custody/root checks and reproducible artifact boundaries;
- impact of `build_descriptor` includes seven symbols in `lane_runtime.py`:
  itself, `doctor`, `up`, `main`, `_expected_descriptor`, `status`, and `down`.
  These are reference-only; Packets 1-2 will not change or invoke runtime
  lifecycle behavior.

Planned write surfaces and overlap:

- this activation changes only this Plan 0110 file;
- subsequent implementation intends new repo-only
  `dev/last30days/scripts/hotfix_control.py` and
  `dev/last30days/scripts/hotfix_git_drill.py`, with
  `tests/test_hotfix_control.py` and `tests/test_hotfix_git_drill.py`, plus this
  plan's execution evidence;
- no expected product-source overlap with WI-002 or WI-004. No write is
  planned to shipped skill/service source, public contracts, runtime controller,
  installer, release metadata, service manifest, or CI;
- ROADMAP, RUNBOOK, active-lanes, work-item records, generated catalogs, and
  any shared-schema decisions remain coordinator-owned.

Validation evidence:

- verified clean lane and canonical status, exact base equality, registered
  worktree/branch custody, correct origin public-fork URL, upstream push disabled,
  and live remote main equality before the plan edit;
- `python3 dev/last30days/scripts/audit_plan_authority.py` passed with three
  active plans and zero issues; `git diff --check` passed and the diff contains
  this plan alone. Final commit and remote equality are returned with the
  activation receipt;
- source tests and disposable Git drills are intentionally not run during
  plan-only activation. Product acceptance, runtime, and production claims
  remain unverified.

Subagent status and reconciliation:

- this is the coordinator's single delegated WI-007 lane; no child agents are
  spawned. The coordinator owns final integration and shared-state reconciliation.

Graphiti write status:

- `not_written`; this assignment authorizes a plan-only repository activation,
  and no durable-memory write was authorized.

Next action and terminal condition:

- stop this activation after publishing the plan-only checkpoint and returning
  exact SHA, clean status, remote equality, and intended source overlap list;
- after coordinator registration, implement the smallest Packet 1 contracts,
  state transitions and fake-adapter fixture, then Packet 2 disposable-Git proof
  within the four named implementation files;
- carry Plan 0107's maximum two implementation attempts, one broad review and
  one closed-world remediation pass per packet; checkpoint each validated
  packet and stop on an exact unresolved blocker rather than extending scope;
- every future drill Git ref/worktree and cleanup target must remain within
  its explicitly owned temporary root. Real lane publication is development
  custody, not a production hotfix drill or incident activation.

## Stop Rules

- stop before any non-disposable Git effect, real incident, runtime/process,
  artifact, installed database, provider/browser, issue, release, staging,
  deployment, rollback, or production mutation;
- stop and notify the coordinator before changing shared release, installer,
  manifest, roadmap, runbook, or catalog surfaces.
