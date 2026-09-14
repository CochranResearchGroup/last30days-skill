<!-- last30days-work-item:WI-005 -->
# Extend tailored follows across supported services

State: READY
Priority: P2
Lane: Follows
Parent: WI-000
GitHub issue: https://github.com/CochranResearchGroup/last30days-skill/issues/58
Blocked by: none for Packet 1; later provider tracers and product closure remain
Last completed plan: docs/dev/plans/0115-2026-09-14-follow-capability-compatibility.md
Active plan: none
Branch: main
Owner: /root

## Problem

An X-only follow design would force later services into accidental semantics or
duplicate scheduling and provenance concepts inconsistently.

## Outcome / Proposed Solution

The accepted follow contract supports service-native targets such as Reddit
communities or users and YouTube channels without erasing their distinct
identity, authorization, and collection semantics.

## Acceptance Evidence

- shared fields remain provider-neutral while each target kind retains exact
  service-specific identifiers and validation;
- capability discovery reports supported target kinds and unavailable
  operations truthfully;
- schedules, receipts, provenance, pause/resume, and query filtering behave
  consistently across fixture-backed adapters;
- unsupported or unauthorized services fail closed without widening scope;
- migrations preserve accepted X follow identity and history.

## Non-Goals

No promise that every service supports lists, accounts, or the same cadence;
no live provider onboarding without separate authority.

## Selected Architecture

Use WI-004's purpose-typed `CollectionSpec` and one shared scheduler. Add a
closed provider capability registry and discriminated `FollowTargetV1` so each
source owns exact stable identity, validation, resolution, access, cadence, and
route semantics. Preserve X target IDs; add Reddit community/user and YouTube
channel as fixture-backed vertical tracers; report Facebook and LinkedIn
tailored targets unavailable until exact contracts exist.

Authority:

- `docs/dev/notes/0123-2026-09-13-cross-service-tailored-follow-product-architecture.md`
- `docs/dev/plans/0082-2026-09-13-cross-service-tailored-follow-architecture-and-lane-handoff.md`

## Next Owner Action

WI-004 is `DONE`. Plan 0115 registers Packet 1 for the capability registry,
target envelope, exact X compatibility, legacy quarantine, and fake-adapter
tests. It remains `PLANNED` until exact branch/worktree custody is published.
Do not start a job, resolve a live locator, open a browser, or mutate an
installed runtime.

Activation checkpoint `337866e0` is published and awaits coordinator custody
reconciliation before implementation begins.

Packet 1 integrated through reviewed PR 87 as canonical merge `d2f15ed6`.
The closed registry now preserves exact X identity, reports Reddit/YouTube
adapters unavailable, quarantines unsupported legacy follows without starving
healthy scheduler work, and retains identity-bound compatibility evidence.
WI-005 is `READY` for a separately planned fixture-backed tracer packet; it is
not yet `DONE`.
