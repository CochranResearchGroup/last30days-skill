# Plan 0121 | Monitor And Digest Product Closeout

State: OPEN
Lane: P40
Work item: WI-006
Branch: feat/monitor-digest-product-closeout-v1
Target: main
Integration: merge
Roadmap: P40
Plan version: 1
Date: 2026-09-14
Execution owner: unassigned
Coordination owner: /root
Requested model route: gpt-6-astra, high reasoning
Effective runtime model: unknown until reported

## Objective

Close WI-006 provider-free with immutable query/follow monitors, explicit
lifecycle and baseline decisions, evidence-linked deterministic digests,
disabled-by-default delivery intents, safe legacy import and fresh public
runtime acceptance.

## Current State

Plans 0093 and 0116 are closed; WI-001/WI-002/WI-004 are `DONE`. The durable
monitor kernel and saved-query composition exist. Follow views, deterministic
digests, disabled delivery intents, safe import and complete public/runtime
acceptance remain for WI-006.

## Definition Of Done

All acceptance criteria pass at one reviewed joined checkpoint, exact runtime
and effect receipts are retained, canonical integration is recorded, and
WI-006 is reconciled to `DONE` with schedules and live delivery still disabled.

## Scope

- add backward-compatible discriminated follow-view capture over exact
  collection revisions, partitions, causes, versions, cutoff and coverage;
- expose create/read/list/revise/lifecycle/capture/evaluate/history and explicit
  accept/reject through one strict monitor application contract;
- render immutable run-bound digests with four change classes, denominators,
  omissions, coverage windows, byte bounds and evidence links;
- persist versioned delivery preferences plus immutable intent/attempt/receipt
  ledgers; production prepares/reads only, while an injected recording sink
  proves idempotency, retry and explicit child resend;
- import only explicitly supplied legacy-topic exports into disabled saved
  queries/monitors with source locator and unmapped-field reports;
- join strict CLI/HTTP/MCP parity and prove restart/teardown in an isolated
  packaged cache-only runtime.

## Non-Goals

No background schedule, provider acquisition, generated/model summary, channel
adapter, real notification, installed migration, retention purge, implicit
baseline acceptance or issue/release/deployment mutation.

## Acceptance Criteria

1. Existing saved-query bytes/replay remain compatible; query and follow views
   freeze exact authorized identities and deduplicate without losing causes.
2. Identical frozen inputs yield identical runs/digests across restart.
   Removal requires explicit tombstone/unavailability evidence; absence,
   truncation, provider failure or top-k drift never proves removal.
3. Only explicit race-safe acceptance advances a baseline. Partial/old-cutoff
   runs, rejection and render failure do not.
4. Every digest is bounded, denominator-aware and cites current/prior immutable
   evidence as applicable; cross-partition probes reveal nothing.
5. Default runtime refuses send. Recording-sink success has one effect per key;
   failure keeps its key and explicit resend creates a reason-linked child.
6. Legacy import is disabled, idempotent and credential-free.
7. Fresh CLI/HTTP/MCP covers the complete workflow and denial cases across
   restart, exact-owner teardown and declared-ledger-only mutations.
8. Focused/full Python, Go/vet, generation, package/lifecycle, reproducibility,
   audit and diff validation pass at the reviewed joined head.

## Ownership And Topology

One top-level owner, no children, at most two implementation attempts, one
independent joined review and one closed-world remediation. Lane-owned modules:
`service_monitor_contracts.py`, `service_monitors.py`,
`service_monitor_views.py`, new `service_monitor_follow_views.py`,
`service_monitor_application.py`, `service_monitor_digests.py`,
`service_monitor_delivery.py`, `service_monitor_import.py`, their focused
tests/fixture, `monitor_dogfood.py`, its test/receipt, and this plan.
Coordinator serializes app/client/HTTP/CLI/MCP, generated artifacts, versions,
docs and authority projections.

## Stop Rules

Stop for upstream follow/search semantic changes, missing trustworthy revision,
coverage or removal evidence, unsafe scope checks, unbounded capture, corrupt
immutable receipts, ambiguous delivery effects, teardown failure, shared-file
conflict or any excluded external effect.

## Next Action

Integrate registration, publish exact isolated custody and assign one owner.
The first coherent source checkpoint must include a real frozen follow-to-
digest tracer. Reviewed canonical integration may move WI-006 to `DONE`.

### Checkpoint P0121-C01 | 2026-09-14

Plan version: 1

State transition: `unplanned -> PLANNED`.

Progress classification: `blocker_reduction`; follow composition, digest,
disabled intent and runtime closure form one coherent acceptance packet.

Authority classification: `inherited_authority` for registration and later
provider-free work; every Non-Goal remains a `human_gate` effect.

Subagent status and reconciliation: `joined`; one read-only planner completed.
Implementation owner remains unassigned pending exact custody.

Next action: integrate registration and publish a plan-only activation ref.

### Checkpoint P0121-C02 | 2026-09-14

Plan version: 1

State transition: `PLANNED -> OPEN`.

Progress classification: `implementation_ready`; exact isolated custody is
accepted from canonical registration merge `e0fab676`.

Authority classification:

- `inherited_authority` covers the registered provider-free write set only;
- every external-effect gate remains held.

Subagent status and reconciliation: `assigned`; `/root/wave4_wi003_plan`, one
owner, no children. Implementation waits for activation reconciliation.

Next action: publish this plan-only checkpoint and return exact custody.
