# Plan 0092 | Service Quality Packet 1

State: PLANNED
Lane: P37
Work item: WI-008
Branch: feat/service-quality-v1
Target: main
Integration: merge
Roadmap: P37
Plan version: 1
Date: 2026-09-13
Session owner: unassigned

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

No execution checkpoint yet. The plan-only launch ref is awaiting publication
and canonical registration.
