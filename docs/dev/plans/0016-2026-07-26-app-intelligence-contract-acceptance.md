# Plan 0016 | App Intelligence contract acceptance

State: PLANNED
Roadmap: P06
Date: 2026-07-26
Predecessors: Plans 0010 and 0011

## Objective

Exercise one accepted and one rejected App Intelligence task envelope through
the installed deterministic supervisor, prove replay behavior and finite
limits, and confirm that stochastic output cannot bypass host-owned evidence,
browser, publication, or repair authority.

## Current State

- Installed version 0.2.7 discovery exposes eight task types, versioned
  request/result contracts, and validator-enforced item, byte, call, cost, and
  time ranges.
- Plan 0010 contracts and Plan 0011 deterministic joins are closed.
- Discovery is proved; current accepted/rejected execution and replay receipts
  remain the bounded successor acceptance gap.

## Scope

- choose one non-browser task type with existing evidence fixtures;
- submit one schema-valid bounded envelope and preserve normalized supervisor
  and decision receipts;
- submit one intentionally invalid or policy-rejected envelope and verify
  fail-closed behavior before stochastic execution;
- replay both inputs and compare deterministic validation/decision paths;
- verify all finite reservations, consumption, terminal state, and allowed
  actions.

## Non-Goals

- browser action, live acquisition, identity auto-merge, claim promotion,
  adapter code mutation, branch integration, deployment, or service restart;
- prompt or raw provider-event exposure through normal discovery;
- benchmarking models or widening contract limits;
- more than one accepted and one rejected envelope.

## Dependencies And Owned Surfaces

- Depends on P01 evidence authority and the closed Plan 0010/0011 host
  contracts.
- Expected writes are focused contract/supervisor/replay tests, bounded
  intelligence-ledger receipts, and closeout docs.

## Execution Packets

1. Freeze task type, evidence fixture, contract version, and finite limits.
2. Execute the valid envelope and verify host-owned terminal decision.
3. Execute the rejected envelope and prove no stochastic or mutating work.
4. Replay both and verify deterministic validation and receipt closure.

## Bounds And Gates

- maximum implementation attempts per packet: 2;
- maximum review/rework cycles: 1;
- maximum hardening-only checkpoints: 1;
- active-agent concurrency: 1;
- one accepted envelope, one rejected envelope, and one replay of each;
- stop on evidence-ID escape, unbounded reservation, browser/tool action,
  unauthorized mutation, nonterminal task, or replay inconsistency.

## Acceptance Criteria

- the accepted task stays within item, byte, call, cost, and time limits and
  terminates with schema-valid proposal and host decision receipts;
- the rejected task fails before stochastic execution or mutation;
- replay preserves contract version, normalized inputs, validator outcomes,
  host decision path, and terminal classification;
- no model output directly changes canonical evidence, identities, claims,
  collection state, browser state, index publication, source, or deployment;
- discovery continues to omit prompts, credentials, raw provider events, and
  browser mechanics.

## Validation

- focused registry, schema, validator, supervisor, ledger, replay, and product
  discovery tests;
- installed maintenance-status readback and bounded task receipts;
- planning audit and `git diff --check`.

## Definition Of Done

One accepted and one rejected task are durably replayable within finite bounds,
with deterministic host authority and zero unauthorized side effects.
