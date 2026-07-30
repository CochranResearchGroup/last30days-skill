# Plan 0016 | App Intelligence contract acceptance

State: CLOSED
Roadmap: P06
Date: 2026-07-26
Predecessors: Plans 0010 and 0011
Transition authority: Plan 0018

## Objective

Exercise one accepted and one rejected App Intelligence task envelope through
the installed deterministic supervisor, prove replay behavior and finite
limits, and confirm that stochastic output cannot bypass host-owned evidence,
browser, publication, or repair authority.

This is a software control-plane acceptance packet under Plan 0018. It proves
bounded stochastic assistance behind service-owned authority; it is not a
Skill feature and does not make a querying agent the App Intelligence
supervisor.

## Current State

- Commit `bbff9f8` and
  `docs/dev/notes/0016-app-intelligence-contract-acceptance-proof.json`
  preserve the accepted, rejected, replay, finite-limit, and authority-closure
  proof.
- One public-evidence `content_assessment` completed in one read-only Codex
  App Server call with one proposal and host validation, promotion, and replay
  receipts.
- A request containing forbidden `browser_profile` state returned
  `schema_invalid` before persistence, provider execution, or mutation on both
  the original validation and replay.
- Installed service 0.2.7 replayed the durable accepted request/result to the
  same three receipt IDs with no new rows or provider call.
- The live attempt exposed and retained one terminal pre-stochastic
  response-schema failure. The canonical schema now satisfies the App Server
  strict subset; packaging that fix into the next compatible service release
  belongs to Plan 0018 S07 rather than this plan's no-deployment packet.

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
- Opens only after Plan 0018 freezes the independent service lifecycle and MCP
  client/service compatibility boundary.
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

## Closeout Receipt | 2026-07-30

- Accepted task
  `intelligence-task-fa47bff380504648800536a4e6206961` consumed one of one
  calls, used one evidence item, stayed within 4,096 bytes, one cent, and 60
  seconds, and produced one accepted proposal.
- Host receipts are
  `validation-receipt-61e56dc19c658ba94acb736abcc2ecd2`,
  `promotion-receipt-7612e1f20dd4ddfe0dacc24accec0a06`, and
  `replay-receipt-7612e1f20dd4ddfe0dacc24accec0a06`.
- Accepted replay used both the canonical candidate and installed 0.2.7
  deterministic queue/validator path, created no new rows, and invoked no
  provider.
- Rejected request digest
  `sha256:295a623a80fa389bc108c169bf28bc396381e3bc89e6142d898fee7cdab99e93`
  returned `schema_invalid` twice with zero persistence and zero provider or
  mutation calls.
- Before/after logical hashes and row counts are identical for canonical
  evidence, identity, claim, collection, document, entity, relationship, and
  index authority. No browser-state table exists, and source, deployment,
  timer, and service process state were not changed.
- Installed maintenance discovery still exposes eight version-1 task types
  without prompts, credentials, raw provider events, or browser mechanics.
- Fifty focused contract, supervisor, replay, product-surface, process, and
  artifact tests passed; the corrected independent artifact SHA-256 is
  `3c1b3ad42942206f487041c0ce2b383842582732da88f8c60df05d740125d989`.
- No subagent was spawned because the plan fixed active-agent concurrency at
  one. The primary agent executed and compared the bounded proof.
