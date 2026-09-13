# Plan 0085 | Isolated Development Runtime Packet 1 Identity Tracer

State: OPEN
Lane: P34
Work item: WI-001
Branch: feat/isolated-dev-runtime-v1
Target: main
Integration: merge
Roadmap: P34
Plan version: 1
Date: 2026-09-13

## Objective

Ship WI-001 Packet 1 as a provider-free runtime-identity tracer: one strict
lane descriptor, deterministic isolated paths, collision/deny-list checks, and
a read-only doctor that starts no process.

## Current State

- Plan 0077 and note 0118 are the accepted architecture;
- production has one managed user service, socket, database, config, logs, and
  identity; no staging or per-lane runtime has been provisioned;
- registered launch checkpoint `8be96fb07baed08c68b8935f405e7a7f70877795`
  was verified clean and reconciled by merge with `origin/main` at
  `b92160a600ee93f2b3bb21899d7e6f31cbb3a0ae`;
- the lane was reconciled again by merge commit
  `94c27c737e08e9f5cbacb4f6c9ecf3b742ba3764` with canonical `origin/main`
  `4f322e0a3c2d4795305c3bdfb853de27fae1c558` before Packet 1 implementation;
- Packet 1's repo-only identity tracer and provider-free acceptance tests are
  implemented without runtime-state mutation;
- GitHub Issues remain disabled, so WI-001 is the work-item locator.

## Scope

- implement the strict `LaneRuntimeDescriptorV1` model;
- derive config, database, socket/port, log, state, artifact, and service names
  deterministically from a safe lane ID;
- reject production/staging aliases, traversal, collisions, broad paths,
  inherited credentials/schedules, and unverifiable ownership;
- expose a read-only provider-free doctor and synthetic fixture.

## Non-Goals

- no `up`/`down`, process start/stop, systemd/container mutation, database
  copy, secret import, browser/provider access, staging, install, or deploy;
- no GitHub tracker mutation until explicit activation authority.

## Acceptance Criteria

1. A valid descriptor deterministically names every mutable runtime surface.
2. Production/staging paths, identifiers, sockets, databases, credentials,
   schedules, and collisions fail closed.
3. Doctor reports exact readiness/reasons without creating files or processes.
4. Two synthetic lanes prove distinct identities and paths provider-free.
5. Focused package, policy, and path-safety tests pass.

## Execution Packet

- accountable human owner: repository operator;
- execution owner: top-level Codex thread/session
  `01a09caa-90aa-78d0-af02-59d9a7d80eea`;
- runtime-reported model: unavailable; the session environment exposed no
  effective model identity, so none is inferred;
- coordination owner: coordinator session for catalog/runtime joins;
- expected writes: repo-only descriptor/doctor modules, CLI/dev helper surface,
  focused tests/fixtures, configuration/docs if a user-facing knob is added,
  and branch-local plan/runbook checkpoints;
- inputs: Plan 0077, note 0118, WI-001, current `origin/main`;
- validation: descriptor/doctor/collision/no-write tests, package boundary,
  policy/lane audits, and published-commit readback;
- terminal condition: five criteria pass and PR is integration-ready, or one
  exact blocker is recorded without process/runtime mutation;
- review bound: one drift-discovery pass and one closed-world remediation pass;
- authority: provider-free source/tests/branch/PR only.

Subagents: optional for bounded support under the lane owner; no nested
delegation without a plan revision.

## Start Checklist

- verify registered branch/worktree/checkpoint and current `origin/main`;
- reread AGENTS.md, relevant policies, Plan 0077, note 0118, and WI-001;
- run Graphiti discovery and CodeGraph impact for installer/service identity;
- transition to `OPEN`, record runtime-reported owner/model when available, and
  publish the first recoverable checkpoint before coding;
- reconcile shared CLI/config/docs overlaps with the coordinator.

## Stop Rules

- stop before any process, service, socket, database, installed config, or
  credential mutation;
- stop before staging/production or provider/browser access;
- stop and reconcile overlapping runtime/install work.

## Activation Checkpoint

### Checkpoint P0085-C01 | 2026-09-13

- state transition: `PLANNED -> OPEN`;
- progress classification: `outcome_progress`; the registered lane is owned,
  reconciled, and recoverably ready for Packet 1 implementation;
- authority classification: `inherited_authority` for this branch-local plan,
  Git reconciliation, validation, commit, and push; `not_authorized` for shared
  coordinator state, runtime/provider/tracker effects, or Packet 1 code in this
  activation turn;
- starting checkpoint: local, remote, and registered
  `8be96fb07baed08c68b8935f405e7a7f70877795`, with a clean worktree;
- reconciliation: merge commit
  `08997a972a0ec543fbefa328174ffa325575c422` incorporates `origin/main`
  `b92160a600ee93f2b3bb21899d7e6f31cbb3a0ae`; protected coordinator paths are
  byte-equal to that remote main;
- discovery: Graphiti was healthy but returned no relevant WI-001/P34 facts;
  CodeGraph could not inspect this worktree because it has no `.codegraph/`
  index, and activation scope did not authorize initialization;
- validation: focused plan-authority tests and repo-native plan authority audit
  pass; the general planning audit reports only the expected branch-local
  ROADMAP/RUNBOOK wiring findings reserved to the coordinator;
- Graphiti write status: `not_written`; this activation expressly forbids
  database mutation;
- remaining acceptance: all five Packet 1 criteria remain unimplemented.

## Next Action

Resume this independent top-level lane in
`/home/ecochran76/workspace.local/last30days-skill-wi001` on
`feat/isolated-dev-runtime-v1`; verify the published activation checkpoint and
clean local/remote equality, then implement only Packet 1's strict descriptor,
deterministic paths, collision/environment-deny checks, read-only `doctor`, and
provider-free fixtures without starting or mutating any runtime.

### Checkpoint P0085-C02 | 2026-09-13

Plan version: 1

State transition:

- `implementation -> awaiting_review`; Plan 0085 remains `OPEN` until review
  and integration because this lane is not authorized to merge its own PR.

Progress classification:

- `outcome_progress`; all five Packet 1 acceptance criteria pass locally.

Authority classification:

- `inherited_authority`; the operator authorized repo-only Packet 1 source,
  tests, plan checkpoint, commit, push, and PR publication. Runtime, database,
  provider, schedule, tracker, staging, production, and merge effects remain
  outside this packet.

Owned changes:

- `dev/last30days/scripts/lane_runtime.py` adds the strict canonical
  `LaneRuntimeDescriptorV1`, deterministic isolated path/environment/offline
  Tick derivation, stable fail-closed reason codes, and read-only `doctor`;
- `tests/test_lane_runtime.py` proves deterministic no-write output, two-lane
  separation, strict descriptor/Tick integrity, environment denial, production
  containment, path/symlink/socket/owner collisions, and Git custody gates;
- this Plan 0085 checkpoint records reconciliation and acceptance evidence.

Validation evidence:

- `uv run pytest tests/test_lane_runtime.py -q`: 22 passed;
- `uv run pytest tests/test_service_runtime_package.py
  tests/test_secret_hygiene.py -q`: 10 passed;
- the helper exposes `doctor` only and its passing-path test verifies that no
  state or runtime root is created; no process or socket is opened.

Subagent status and reconciliation:

- `not_spawned`; the operator prohibited subagents for this packet;
- `ROADMAP.md`, `RUNBOOK.md`, `docs/dev/active-lanes.yaml`, and WI-001 remain
  byte-equal to `origin/main` after reconciliation.

Graphiti write status:

- `not_written`; discovery was read-only and the operator expressly excluded
  database mutation from Packet 1.

Remaining acceptance criteria:

- none within Packet 1; Packet 2 lifecycle/effect-gate work, installed-runtime
  validation, and staging/production operations were not attempted.

Effects:

- repository source, tests, and this branch-local plan only; no installed
  runtime, process, service, socket, database, configuration, credential,
  provider, schedule, tracker, staging, or production state was mutated.

Next action:

- publish the validated commit, open a PR from
  `feat/isolated-dev-runtime-v1` to `CochranResearchGroup/last30days-skill`
  `main`, verify the remote ref and PR head, then stop without merging.

Checkpoint P0085-C02 is the current authority.
