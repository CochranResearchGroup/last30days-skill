<!-- last30days-work-item:WI-009 -->
# Clear the productization readiness gate

State: READY
Priority: P0
Lane: Program
Parent: WI-000
Blocked by: none for planning and provider-free repair; P35 pull-request creation, development-runtime provisioning, release, dogfood effects, and GitHub issue publication retain their separate authority gates
Plan: docs/dev/plans/0102-2026-09-13-productization-readiness-prerequisites.md

## Problem

The first productization packets are integrated and broadly test-clean, but the
program review found two question-answering contract defects, contradictory
issue-tracker guidance, a stale tailored-follows integration candidate, and no
installed development runtime carrying the new product surfaces. Source and
production also identify materially different runtime packages as service
version `0.3.116`.

Starting another feature packet before resolving these findings would compound
unverified behavior and increase reconciliation and release risk.

## Outcome / Proposed Solution

Create one ordered prerequisite gate that repairs the accepted defects,
reconciles and integrates P35, establishes an unambiguous versioned development
runtime, dogfoods the integrated product surfaces, and publishes the governed
work-item backlog when separately authorized.

## Acceptance Evidence

- malformed structured answers become safe durable terminal receipts without
  waiting for lease expiry or consuming an unrelated retry;
- every evidence-only answer respects `max_answer_characters`, with regression
  coverage for small bounds and multiple evidence items;
- `AGENTS.md`, the tracker operating contract, the work-item index, live GitHub
  readback, and the forge registry describe one non-contradictory tracker state;
- P35 is reconciled from current `origin/main`, passes combined validation, and
  enters `main` through a reviewed pull request;
- source and installed artifacts never use one service version for different
  manifests, and an isolated development runtime is proven distinct from
  production by service identity, database, socket or port, config, logs, and
  credentials/effect boundary;
- provider-free development dogfood proves stored-post search, question
  answering, saved monitors, quality reporting, and tailored-follow lifecycle;
- any live-provider dogfood is separately authorized, serialized, bounded, and
  recorded rather than inferred from provider-free evidence;
- WI-000 through WI-009 are published idempotently to the enabled GitHub issue
  tracker only after the target registry and operator authority permit the exact
  mutations, with URLs read back into repo authority.

## Program Gate

No new feature packet for WI-001 through WI-006 or WI-008 may be activated until
this work item is `DONE`. Work that directly closes this gate is allowed. The
reserved WI-007 production-hotfix path remains available and must retain
priority integration when production health requires it.

## Non-Goals

This work item does not itself authorize a provider call, browser/profile use,
installed-runtime mutation, release, deployment, GitHub issue mutation, P35 pull
request, or production change. Each effect retains its existing explicit gate.

## Next Owner Action

Open the first bounded corrective packet from current `origin/main` for the two
question-answering defects and the tracker-documentation contradiction. Keep
P35 reconciliation serialized behind that repair because both touch the service
contract and application integration surface.
