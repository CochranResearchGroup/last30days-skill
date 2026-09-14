# Plan 0106 | WI-001 Runtime Evidence Reconciliation

State: CLOSED
Lane: P34
Work item: WI-001
Evidence plan: docs/dev/plans/0105-2026-09-14-versioned-development-runtime-and-dogfood.md
Branch: docs/wi001-runtime-evidence-closeout
Target: main
Integration: merge
Roadmap: P34
Plan version: 1
Date: 2026-09-14
Session owner: primary Codex goal thread

## Objective

Reconcile the completed P51 runtime evidence against every WI-001 acceptance
criterion, close the stale WI-001/P34 Packet 2 projections, and prepare the
documentation for one reviewed pull request without starting another runtime.

## Current State

- runtime implementation PRs 73 and 74 are integrated at canonical
  `1168c62e0192ff33f71a07482a32b05721fb839a`;
- Plan 0105 and receipt 0126 prove one deterministic service `0.3.117` artifact,
  one isolated cache-only runtime, exact identity/status/teardown, and unchanged
  production;
- Plan 0105 and P51 closed through PR 75 at canonical
  `b2741a866cc6d0a9b198fcf4d1b3716a867803c5`;
- WI-001 and P34 still describe the pre-P51 state in which only the read-only
  doctor existed and a separate lifecycle Packet 2 remained to be planned.

## Scope

- map Plan 0105 and receipt 0126 to all five WI-001 acceptance criteria;
- mark WI-001 `DONE` and P34 `CLOSED` in repo-local authority;
- update P34's catalog disposition while retaining its exact Packet 1 branch
  and integration custody as history;
- restore P51's branch checkpoint to its exact branch tip while retaining the
  canonical implementation merge and validation receipts separately;
- append one runbook reconciliation checkpoint;
- validate the documentation, planning authority, and catalog projections and
  integrate them through one reviewed pull request.

## Non-Goals

- no runtime start, artifact build, provider/browser action, schedule, private
  data, production/staging mutation, release, deployment, or feature work;
- no rewrite of Plans 0077, 0085, or prior runbook history;
- no GitHub issue mutation. Issue 54 remains open because the registry permits
  reads, creation, and existing-label application, but not closure or editing;
- no cleanup or deletion of historical branches, refs, worktrees, or evidence.

## Acceptance Evidence Mapping

1. Deterministic per-lane configuration: two fixed-input builds from exact
   canonical `1168c62e` are byte-identical at artifact SHA-256
   `cf64df41ed072b3d87085b537e0cbe4960d56e71d34d70891b386e152d15bff2`;
   runtime `l30d-p51-dogfood-cdbb3d9fd80b` used its own private configuration,
   database, socket, log, artifact, descriptor, and receipt roots.
2. Fail-closed startup and effect isolation: focused negative tests cover
   production paths, symlinked paths, stale/foreign ownership, duplicate-owner
   collision, and inherited ambient configuration. The child environment was
   credential-free and cache-only, constructed no provider/browser/scheduled
   loops, and denied refresh and mutation before admission.
3. Health and identity: `doctor`, `up`, and `status` bound descriptor digest
   `a7551944051cd59d78b575022d5f4e81afc8663a0b7bbdd7ba2020ec7a8e3c76`,
   PID 859669/start ticks 1166337, Unix peer identity, exact artifact/source
   commit, service `0.3.117`, schema 18, and manifest
   `a0a11ff4be28ac72048f1634221ef59d464802222f0f0ac571a6fe242d1e83c3`.
4. Exact teardown and production preservation: pidfd-bound `down` stopped only
   the verified development owner, removed its socket, retained its evidence,
   and left production alone at PID 1428/start ticks 4893, service `0.3.116`,
   schema 17, and installed manifest
   `19707a469eb58c21ca4c5b43a0bfbfb6cac4b0f5a5310480b01b1a3f652429e8`.
5. Staging remains a separate deployment gate: Plan 0105 explicitly excluded
   staging/production mutation and the runtime operating model continues to
   require separate staging acceptance and deployment authority.

The durable evidence index is
`docs/dev/notes/0126-2026-09-14-p51-runtime-dogfood-closeout-receipt.json`.

## Expected Write Surface

- this plan;
- `docs/dev/work-items/WI-001-isolated-development-runtime.md`;
- P34 in `ROADMAP.md` and `docs/dev/active-lanes.yaml`;
- P51's stale branch-checkpoint field in `docs/dev/active-lanes.yaml`;
- one append-only `RUNBOOK.md` turn.

## Validation And Review

- run the plan-authority test and active/goal planning audits;
- run the catalog-only active-lane audit against the proposed branch commit;
- validate JSON/YAML parsing, exact stale-projection removal, and
  `git diff --check`;
- inspect the published PR diff against this closed evidence set before merge.

Subagents: not used; this is a tightly coupled coordinator-owned authority
reconciliation and the user did not request delegation.

## Definition Of Done

Every WI-001 criterion maps to existing durable P51 evidence, WI-001 is `DONE`,
P34 is `CLOSED`, current projections no longer request a lifecycle Packet 2,
validation passes, and the exact documentation diff is integrated through one
reviewed pull request without starting a runtime.

## Current Checkpoint

### Checkpoint P0106-C01 | 2026-09-14

Plan version: 1

State transition: `unplanned -> CLOSED`.

Progress classification: `outcome_progress`; existing integrated runtime proof
now closes WI-001/P34 rather than being left disconnected from those
authorities.

Authority classification:

- `inherited_authority` for repo-local evidence reconciliation, validation,
  branch publication, pull-request review, and integration;
- `human_gate` for runtime, production/staging, provider/browser, schedule,
  private-data, release, deployment, and GitHub issue mutations;
- `scope_expansion` for any new runtime or feature packet.

Evidence:

- Plan 0105 checkpoint C04 and receipt 0126 satisfy all five mappings above;
- the catalog-only audit exposed P51's branch checkpoint/branch-tip mismatch;
  its exact branch tip is `5c1d6228`, while `1168c62e` remains the distinct
  canonical integration and validation receipt;
- canonical main was clean and remote-equal at `b2741a86` with no open pull
  request before this slice;
- issue 54 readback was `OPEN`; no unsupported issue mutation is included;
- Graphiti was healthy but returned no relevant repository history, so current
  plans, receipts, Git, and runtime readbacks remain authoritative.

Subagent status: `not_spawned`.

Graphiti write status: `not_written`; no explicit memory-write authority exists.

Next action: validate, publish, self-review, and merge this exact documentation
reconciliation; do not start another runtime.
