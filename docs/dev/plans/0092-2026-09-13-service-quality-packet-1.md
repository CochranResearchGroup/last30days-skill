# Plan 0092 | Service Quality Packet 1

State: OPEN
Lane: P37
Work item: WI-008
Branch: feat/service-quality-v1
Target: main
Integration: merge
Roadmap: P37
Plan version: 1
Date: 2026-09-13
Session owner: Codex thread/session `01a09cf4-c89d-7b41-901a-37648171312a`

## Objective

Ship a deterministic provider-free quality tracer with strict evaluation-set,
threshold, run, metric, artifact, effect, report, renderer, and exit contracts
across four separately inspectable fake axes.

## Current State

- Plan 0080, note 0121, and WI-008 are the accepted architecture and handoff;
- fragmented evaluators exist, but no unified versioned set, denominator-aware
  threshold policy, canonical report, or four-axis runner exists;
- Packet 1 has no product dependency and may use fake adapters exclusively;
- this branch starts from exact canonical 87a8cbac.

## Scope

- implement strict evaluation-set, threshold-policy, request, report, metric,
  result, effect, artifact, and comparison contracts;
- derive deterministic IDs and semantic digests from canonical inputs;
- add fake acquisition, corpus, retrieval, and grounding axis adapters;
- render authoritative JSON and a deterministic Markdown projection;
- define distinct pass, quality-failure, invalid-input, and incomplete-run exit
  semantics;
- add provider-free self-tests and sealed fixtures.

## Non-Goals

- no service process, real database, WI-002/WI-003 adapter integration, model
  judge, browser/provider, installed runtime, CI edit, production sample,
  schedule, staging, release, production, or GitHub tracker mutation;
- no automatic threshold, fixture, baseline, model, or ranking promotion.

## Acceptance Criteria

1. All versioned contracts are strict, canonical, and deterministically
   identified.
2. Four fake axes remain separately measurable with explicit numerators,
   denominators, exclusions, thresholds, and missing-data behavior.
3. JSON and Markdown agree on ordering, states, metrics, and the aggregate
   blocking decision.
4. Skipped, crashed, invalid, unknown-denominator, or incomplete blocking axes
   cannot yield a passing exit.
5. Provider-free fixture and CLI self-tests replay without network, runtime,
   judge, or writable external state.

## Execution Packet

- accountable human owner: repository operator;
- execution owner: one independent top-level Codex session in this worktree;
- coordination owner: coordinator session for shared schemas, catalog, CI,
  roadmap/runbook, and later WI-002/WI-003 joins;
- expected writes: repo-only quality modules and CLI, reviewed fixtures,
  focused tests, small public docs if required, and this plan;
- inputs: Plan 0080, note 0121, WI-008, and current origin/main;
- terminal condition: all five criteria pass and a published PR-ready
  checkpoint exists, or one exact blocker is recorded without widening scope;
- authority: provider-free source, tests, branch publication, and PR
  preparation only.

## Start Checklist

- verify exact base, clean worktree, remote custody, and no overlapping PR;
- reread AGENTS.md and relevant planning, Git, validation, architecture, and
  multi-session policies;
- use read-only Graphiti discovery and CodeGraph impact where available;
- transition this plan to OPEN, record the runtime session identity, and push
  that planning checkpoint before implementation;
- keep generated artifacts ignored and fixtures reviewed.

## Stop Rules

- stop before service, database, judge, provider/browser, installed runtime,
  CI, production sample, schedule, staging, release, production, or tracker
  effects;
- stop before real WI-002/WI-003 adapter integration;
- stop and reconcile shared schemas or CI surfaces with the coordinator.

## Current Checkpoint

### Checkpoint P0092-C01 | 2026-09-13

- state transition: `PLANNED -> OPEN`;
- progress classification: `outcome_progress`; the registered WI-008 lane is
  independently owned, reconciled to current `origin/main`, and recoverably
  ready for coordinator ownership integration before Packet 1 implementation;
- authority classification: `inherited_authority` for this branch-local plan,
  Git reconciliation, focused validation, commit, and push; `not_authorized`
  for feature implementation in this activation turn or for coordinator-owned
  shared schemas, CI, runtime, provider/browser, judge, production sample,
  schedule, tracker, staging, production, or P35 effects;
- starting checkpoint: local and remote
  `feat/service-quality-v1` were clean and equal at
  `37638af57a9e01af42a177e13c57b87794649518`, created from merge base
  `87a8cbac467f979237f85b7e9a96946a2f137613`;
- reconciliation: fetched `origin/main`
  `606272ab82ba2c97d833e8b06e2c1ea4092bac85` and merged it without history
  rewriting as `6fcd0f082102e09fbfd5e748009f08ab307a9f57`, whose parents are the starting
  checkpoint and exact fetched main; no conflicts or manual resolutions were
  required, and coordinator-owned ancestry is byte-equal to `origin/main`;
- owned changes: only this plan's state, runtime-reported session owner, and
  activation checkpoint; no feature code, tests, fixtures, shared authority,
  runtime, provider, or deployment surface was changed by this lane;
- validation: the branch has no open pull request; focused plan-authority
  tests pass `10/10`; the repo-native plan authority audit reports `passed`
  with zero issues; the goal-governance audit passes; the active planning audit
  reports only the expected branch-local ROADMAP/RUNBOOK wiring findings
  reserved to the coordinator; patch hygiene passes with only this plan in the
  owned diff; final local/remote equality remains to be verified after push;
- remaining acceptance: all five Packet 1 criteria remain unimplemented;
- subagent status: `not_spawned`; activation was performed by the independent
  top-level owner without delegation;
- Graphiti status: runtime doctor is healthy; one bounded read-only query of
  `last30days_skill_main` returned no relevant P37/WI-008 activation evidence;
  `not_written` because this activation turn does not authorize graph-memory
  mutation;
- next action: publish this activation checkpoint, verify exact local/remote
  equality, then stop for the coordinator to integrate lane ownership before
  any Packet 1 implementation begins.
