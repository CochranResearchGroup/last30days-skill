# Plan 0123 | Provider Acceptance Architecture And Lane Handoff

State: CLOSED
Lane: P53
Work item: WI-010
Branch: docs/provider-acceptance-architecture
Target: main
Integration: merge
Roadmap: P53
Plan version: 1
Date: 2026-09-14
Execution owner: /root
Coordination owner: /root
Requested model route: gpt-6-astra, high reasoning
Effective runtime model: not exposed

## Objective

Design a provider acceptance system that gives maintainers truthful,
independently verifiable evidence across replay, owned transport, readiness,
and bounded live-canary tiers, then leave one implementation-ready provider-
free packet without invoking a provider.

## Current State

P52 is closed and current product surfaces have joined provider-free evidence.
Provider integrations have substantial local tests, and historical live
canaries exist, but the repository has no common acceptance campaign contract
or receipt that prevents one evidence tier from being mistaken for another.

## Definition Of Done

The repo records the selected interface, evidence tiers, dependency taxonomy,
authority and budget rules, receipt contract, provider matrix, implementation
topology, stop rules, first bounded packet, and a restart-safe machine-readable
handoff. WI-010 and P53 are registered without creating a remote issue or
performing any provider effect.

## Scope

- inspect current acquisition request/result, adapter registry, source policy,
  browser, subprocess, and receipt seams;
- design the acceptance surface twice and reconcile the alternatives;
- separate replay, local transport, readiness, and live-canary evidence;
- define authority, redaction, accounting, retry, cleanup, and receipt rules;
- bound the first provider-free implementation packet.

## Non-Goals

No implementation, credential resolution, provider call, browser action,
remote probe, installed-runtime change, schedule, live data, release,
deployment, GitHub issue mutation, or Graphiti write.

## Selected Architecture

The public Python interface is deliberately small:

```python
prepare(spec: CampaignSpec, *, catalog: AcceptanceCatalog) -> SealedPlan
execute(plan: SealedPlan, *, grant: ExecutionGrant,
        deps: AcceptanceDependencies) -> AcceptanceReceipt
verify(receipt: AcceptanceReceipt, *, plan: SealedPlan) -> AcceptanceVerdict
```

`prepare` seals exact cases, adapters, expectations, fixtures, source identity,
effect class, and ceilings. `execute` is the sole effect-capable entry point;
it validates the grant before credential or transport resolution. `verify`
checks the immutable receipt against the sealed plan and performs no provider
rerun. One maintainer CLI wraps these operations.

The implementation lives outside the shipped Skill under
`dev/last30days/provider_acceptance/`. Internal HTTP, command, and Agent Browser
ports remain separate. Provider-specific assertions live in a closed catalog;
common orchestration owns effects, budgets, redaction, receipts, and teardown.

## Evidence Tiers

| Tier | Name | Permitted dependency | Claim |
|---|---|---|---|
| P0 | Catalog/static | imports and sealed metadata | registrations and contracts are coherent |
| P1 | Sealed replay | checked-in sanitized fixtures | parser, normalization, provenance and error semantics |
| P2 | Owned transport | loopback HTTP, fake executable, browser simulator | request/protocol construction and local fault handling |
| P3 | Isolated join | dedicated provider-free service/database/socket | adapter-to-public-result integration and cleanup |
| P4 | Readiness | explicitly granted remote/auth probe | only the exact probed route/profile is ready at that time |
| P5 | Live canary | one explicitly granted external attempt | exact route execution plus recorded yield and accounting confidence |

P0-P3 may run in normal provider-free development and CI. P4 and P5 are
separate human-gated effects. Drift/soak testing is a later campaign with its
own authority; it is not a presubmit mode.

## Authority And Safety Contract

- an external grant binds the plan digest, effect class, provider, adapter,
  case IDs, credential-profile references, expiration, and request/cost/time/
  concurrency ceilings;
- environment variables and available credentials establish readiness inputs,
  never authority;
- external concurrency is one; broad `--all external` selection is rejected;
- the default attempt count is one and automatic external retries are zero;
- auth, CAPTCHA, rate limit, profile/route/lease mismatch, uncertain accounting,
  timeout, redaction failure, and teardown failure stop the campaign;
- an uncertain effect is preserved and blocks retry rather than being rewritten
  as failure-before-effect;
- exact-owner cleanup runs in `finally`, and cleanup failure is terminal;
- fixtures derived from authenticated sessions remain outside Git. Only
  reviewed sanitized payloads, hashes, and safe locators may enter the repo.

## Receipt Contract

The append-only canonical receipt records schema version; campaign, plan,
source, catalog and fixture digests; provider/adapter/case identities; evidence
tier and effect class; grant digest; planned and observed budgets; accounting
confidence (`exact` or `opaque_request_equivalent`); timestamps; normalized
result counts; safe reason codes; redaction disposition; and exact-owner
teardown/census. It never stores raw secrets, cookies, authorization headers,
environment contents, private page text, or reusable browser-route material.

Transport success, content yield, completeness, and semantic quality are
separate fields. A zero-yield successful request is preserved as such.

## First Implementation Packet

Packet 1 creates the contracts, catalog, replay runner, effect ledger,
redaction, receipts, independent verifier, and CLI. It then proves two real
acquisition seams with sealed data: Reddit keyless through loopback HTTP and
YouTube through a fake `yt-dlp` executable. Tests begin red for sealing,
authority-before-dependency-resolution, budget exhaustion, safe redaction,
uncertain accounting, first-failure preservation, and exact-owner cleanup.

This packet does not include Agent Browser, service join, credentials, remote
readiness, or live canaries. Those remain subsequent vertical packets.

## Ownership And Parallel Topology

After Packet 1's shared contracts are frozen, one coordinator may assign two
parallel, non-overlapping tracers: loopback HTTP/Reddit and fake command/
YouTube. The coordinator owns shared contracts, CLI, receipts, authority
projections, integration, and joined validation. A later Agent Browser tracer
starts only after the shared port/effect contracts are accepted. No nested
subagents are needed for the first packet.

## Stop Rules

Stop before resolving a secret or contacting a non-loopback endpoint; before
opening a real browser/profile; if exact ownership cannot be proven; if a test
requires private raw fixtures; if accounting confidence would be overstated;
if a retry could duplicate an uncertain effect; or if implementation requires
changing production/installed runtime, schedule, release, deployment, or issue
state.

## Invalidation Map

Each stop makes the overall campaign incomplete but preserves unaffected,
already-finalized samples:

| Stop predicate | Invalidated evidence | Preserved evidence |
|---|---|---|
| plan/grant/authority mismatch before invocation | selected case and whole-campaign verdict | prior finalized cases; no transport sample exists for the rejected case |
| request/transport failure | that case's transport-success and yield verdicts | its admitted-plan, budget consumed, safe failure, and all prior cases |
| parser/normalization drift | that case's normalized result, yield interpretation, and provider-contract verdict | observed transport, raw-safe digest, budgets, and prior cases |
| accounting uncertainty | exact budget-compliance verdict and overall acceptance | declared transport/yield observation labeled `opaque_request_equivalent` |
| timeout or uncertain effect | retry eligibility and terminal case/campaign acceptance | attempts, consumed bounds, first failure, and uncertainty evidence |
| redaction failure | publication and every downstream claim derived only from that unsafe receipt | prior safe receipts; failed artifact remains quarantined outside publishable evidence |
| teardown/census failure | lifecycle-safety and overall campaign verdict | completed transport/yield observations labeled teardown-incomplete |

No later failure erases a prior sample. No preserved partial sample may be
promoted into a complete provider, tier, or campaign acceptance verdict.

## Acceptance Criteria

1. Architecture note and JSON handoff agree on interface, tiers, matrix,
   gates, topology, and next packet.
2. WI-010 and P53 truthfully distinguish design closure from implementation
   readiness.
3. Current plan-authority and documentation validation pass.
4. Independent review findings are adjudicated and every accepted blocker is
   closed without authority leakage or an unsupported evidence claim.
5. No provider, browser, credential, installed-runtime, tracker, or external
   network effect occurs.

### Checkpoint P0123-C01 | 2026-09-14

Plan version: 1

State transition: `unplanned -> CLOSED`.

Progress classification: `architecture_complete`; three independent designs
were reconciled into one minimal public API with transport-specific internal
ports, tiered evidence, exact authority, and a provider-free first packet.

Authority classification: `inherited_authority` covered repository inspection,
design, documentation, validation, review, and normal pull-request integration.
All external effects and GitHub issue mutations remained held.

Subagent status and reconciliation: `joined`; minimal-interface, common-caller,
and extensibility designs completed read-only and were synthesized by `/root`.
Independent review produced four blocking candidates: missing invalidation map,
premature review closure wording, inconsistent WI parent projection, and
incomplete explicit adapter delivery. All four were accepted and remediated;
closed-world verification is recorded in the next checkpoint.

Next action: integrate this design, then activate a separate Packet 1 plan from
current canonical main. Do not infer P4/P5 authority from architecture closure.

### Checkpoint P0123-C02 | 2026-09-14

Plan version: 1

State transition: `CLOSED -> CLOSED`.

Progress classification: `review_reconciled`; the bounded independent review
completed and all four accepted blockers were corrected without expanding the
effect boundary. Closed-world verification passed the parent and eight-adapter
corrections, then found two projection residuals: authority-mismatch campaign
invalidation was missing from the note/JSON, and the verification disposition
was still marked pending. The primary agent corrected both mechanically and
verified exact plan/note/JSON/runbook agreement plus the authority tests.

Authority classification: unchanged; documentation/review only, with every
provider, browser, credential, remote and tracker effect still held.

Next action: integrate the reconciled architecture through the normal reviewed
pull-request workflow.
