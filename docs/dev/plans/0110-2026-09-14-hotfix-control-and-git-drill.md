# Plan 0110 | Hotfix Control And Git Drill

State: CLOSED
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

Provider-free Packets 1-2 are implemented and validated on
`feat/hotfix-control-v1`: strict in-memory hotfix control and an isolated local
Git integration drill. All five acceptance criteria have evidence within this
provider-free boundary. This plan remains `OPEN` pending coordinator review and
integration. The reserved production slot remains dormant; no real incident,
runtime, release, deployment, rollback, or production mutation occurred.

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

### Checkpoint P0110-C02 | 2026-09-14

Plan version: 1

State transition: `activation_published -> integration_ready`.

Progress classification: `outcome_progress`; Packets 1-2 now have executable
control contracts, real disposable-Git evidence, and focused/fallback validation.

Authority classification:

- `inherited_authority` from Plan 0107 and the coordinator's implementation
  assignment after activation PR 78 merged at
  `8a3b726918bcb5055db2294c897691a2171fa24c`;
- fetched that exact `origin/main` and merged it into this lane as
  `9af758a08b833d2b6b8ee751e5e62c463fe50b90`, preserving activation commit
  `28c721e0612b8e669ab96d8dbe9c8c1b59e4ddb0`. The clean lane contained the
  canonical base with only its previously published plan activation differing;
- authorized effects were lane fetch/merge/publication, the four declared new
  implementation/test files, this plan, and fixture-only Git subprocesses;
- no PR, issue, provider/browser, credential, installed-runtime, service,
  staging, release, deployment, rollback, or production mutation was performed.

Owned changes:

- `dev/last30days/scripts/hotfix_control.py`: strict immutable versioned drill
  records, exact digest/commit linkage, one slot with zero owned resources or
  live authority, explicit source/runtime/disposition transitions, append-only
  evidence history, feature WIP and overlap checks, and fake Git/review/runtime
  adapters;
- `dev/last30days/scripts/hotfix_git_drill.py`: fresh fixture factory beneath
  the OS temporary root, local bare origin, dedicated worktrees, controlled Git
  configuration/environment, current-main branching, priority gate, all five
  feature dispositions, actual conflicting-merge abort, and exact cleanup;
- `tests/test_hotfix_control.py` and `tests/test_hotfix_git_drill.py`: public
  interface tests for the above acceptance boundaries; no shared source,
  installer, release metadata, runtime manifest, or canonical authority edits.

Acceptance evidence:

1. Dormant control owns no resource or live authority. It rejects unverified
   incidents, stale/dirty main, a second occupied hotfix slot, missing rollback
   evidence, unregistered overlap, malformed records, and a fourth active
   feature. Three active features plus one reserved hotfix remain permitted.
2. Candidate, integration, full lane reconciliation, staging, authorization,
   deployment, verification, rollback, and closeout require separate linked
   evidence. Invalid transitions preserve prior state. Failed verification and
   failed rollback remain recorded; rollback has one attempt and cannot loop.
   Cancellation or blocking cannot claim a fixed outcome or bypass cleanup.
3. Disposable Git proof starts at exact local origin/main, rejects conflicting
   feature integration before the hotfix, verifies actual commit ancestry and
   remote readback, and records unaffected, reconciled, paused, superseded, and
   cancelled lanes. Reconciled feature content retains both changes.
4. Unpublished feature divergence fails before hotfix worktree creation. Dirty
   cleanup preserves the full fixture until the exact test-owned dirt is
   resolved. Symlinks, changed owner/configuration/hooks, and redirected linked
   Git metadata fail before further Git actions; unrelated siblings survive.
5. Focused and bounded safe-fallback provider-free validation passed. Canonical
   Git and production process identity remained unchanged by this lane.

Validation evidence:

- TDD used successive red/green public-interface slices. Initial failures
  included absent modules/records, missing overlap/path checks, missing rollback
  transitions, metadata redirection, feature-WIP enforcement, and blank test
  names; each was retained in the execution transcript and resolved against the
  same acceptance contract. No flaky retry was used;
- one implementation attempt, one self-review and one bounded remediation pass;
  the review resolved missing WIP/occupied-slot guards, linked Git metadata
  containment, and empty validation names without changing the write surfaces;
- focused selection: the two new test files, 40 cases; the final result is
  included in the publication readback;
- safe fallback command: `uv run pytest tests/test_hotfix_control.py
  tests/test_hotfix_git_drill.py tests/test_plan_authority_audit.py
  tests/test_plugin_contract.py
  .codex/skills/repo-policy-selector/tests/test_audit_active_lanes.py
  .codex/skills/repo-policy-selector/tests/test_audit_planning_contract.py
  -k 'not test_current_repository_authority_passes'`;
- safe fallback: **116 passed, 1 deselected in 32.29s**, one serial run,
  measured wall time 32.35s and peak RSS 36,760 KiB. Local bounds are 60 seconds
  focused and 120 seconds fallback; neither was exceeded. This is a selected
  provider-free fallback, not the comprehensive suite or a runtime/release drill;
- the excluded current-repository projection test was run separately and failed
  exactly at its hardcoded `active_plan_count == 2` assertion (`3 == 2`). The
  coordinator explicitly accepted this branch-local projection mismatch and
  owns canonical expectation reconciliation. Its synthetic fixtures ran;
- `audit_plan_authority.py`: passed, three active plans, zero issues;
- offline Ruff format/check, compilation of all four new files, and
  `git diff --check` passed. The initial lint findings (imports, explicit
  subprocess check flag, and dictionary iteration) were corrected.

Fresh disposable-Git acceptance readback:

- fixture base and activation remote:
  `a4c6865ac20dbf5e66d5c28fa11e080ddc2a5c51`;
- hotfix tip: `b106a87f7a5f9ebbb23088143c4a62a71fec1270`;
- merge and final fixture main:
  `ce42b9fbb0095cecf8732bdf40137f40f42aa502`;
- reconciled feature advanced from
  `5efd5881ca720ea9b40c783e1814df2104c9dc16` to
  `57f8cd840b05dd8ef5c8c9496ba1bd97498d9934`;
- complete in-memory receipt digest:
  `ad9774b84b7a3d191511ba1b1568dd05d6bd992e4b778255d8c6945ca37eed07`;
- fresh fixture `/tmp/wi007-acceptance-4q4gmg7b/l30d-hotfix-bmrf910d`
  and its parent were verified absent after cleanup; zero remaining fixture
  worktrees or refs. The temporary proof is reproducible through
  `run_git_drill(parent)` and the checked-in test, not a retained runtime;
- final OS process search found no fixture-root Git process, `git-receive-pack`,
  or `git-upload-pack`. The controller owns zero processes, sockets, databases,
  schedules, credentials, or deployment authority;
- real production read-only baseline/final: `last30days.service` active/running,
  MainPID `1428`, process start monotonic `48933432`, unchanged;
- canonical main stayed clean at
  `8a3b726918bcb5055db2294c897691a2171fa24c`, equal to local origin/main.
  No installed database/content or new live readiness claim is inferred from
  this process identity readback.

Subagent status and reconciliation:

- execution owner `/root/wi007_hotfix_drill`; no nested agents. Effective model
  and effort remain unreported. The coordinator owns final review/integration,
  shared projections, and the exact published source checkpoint.

Graphiti write status:

- `not_written`; no durable-memory write was authorized.

Remaining acceptance criteria:

- none within provider-free Packets 1-2; coordinator PR integration and
  canonical state reconciliation remain pending. WI-007's later Packet 3
  runtime/release drill and Packet 4 operator work remain outside this plan;
- receipt contracts and fake adapters prove simulated state separation. They
  do not authenticate real incidents or authorize any actual deployment.

Next action:

- publish the implementation checkpoint on `origin/feat/hotfix-control-v1` and
  return its exact commit, clean status, remote equality, test receipts, and
  limitations. The coordinator reviews and integrates; this worker does not
  open a PR or change shared authority.

## Stop Rules

- except for explicitly assigned development-lane fetch/merge/publication,
  stop before any non-disposable Git effect, real incident, runtime/process,
  artifact, installed database, provider/browser, issue, release, staging,
  deployment, rollback, or production mutation;
- stop and notify the coordinator before changing shared release, installer,
  manifest, roadmap, runbook, or catalog surfaces.

### Checkpoint P0110-C03 | 2026-09-14

State transition: `integration_ready -> CLOSED`.

Provider-free Packets 1-2 integrated through reviewed owned-fork PR 79 at
canonical merge `fae311987426fcfee681275f0a83b4c53fc7c6a7`. Independent review
reproduced one fixture-containment escape through top-level Git `commondir`;
the remediation now rejects redirects in both main and bare-origin metadata
before any Git mutation, with exact regressions. Hotfix-focused, joined full,
Go, packaging, and authority validation pass. The real slot remains dormant;
Packet 3 runtime/release drill and Packet 4 operator closure remain separate.
