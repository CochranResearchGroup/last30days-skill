# Provider Acceptance Architecture

Date: 2026-09-14
Work item: WI-010
Plan: 0123
Repository checkpoint: `c6cbbb023d47e63fdaff2534eeec7e73f87c77d2`

## Decision

Adopt a sealed `prepare -> execute -> verify` acceptance campaign outside the
shipped Skill. Keep provider-specific expectations in a closed catalog and
HTTP, subprocess, and Agent Browser mechanics behind separate internal ports.
The harness owns effect authorization, bounded execution, redaction,
append-only receipts, exact-owner teardown, and independent verification.

Recorded fixtures prove deterministic contract behavior; owned substitutes
prove local transport behavior; a remote readiness probe proves only a time-
bound route/profile observation; and a live canary proves only its exact
attempt, yield, and declared accounting confidence. None automatically proves
completeness, semantic quality, recurring safety, or production readiness.

## Current Evidence

- `AcquisitionWorkRequest` and `AcquisitionWorkResult` already form a strong
  provider-neutral production seam with wall, item, network, and cost budgets.
- the built-in adapter registry currently covers X, Facebook, LinkedIn post,
  LinkedIn profile, YouTube yt-dlp, Reddit keyless, Reddit Agent Browser, and
  Reddit ScrapeCreators routes;
- source policy admits provider-specific methods instead of one universal
  transport;
- existing tests cover many adapter, parser, policy, fixture, and failure
  paths, but no common tiered campaign and independently verifiable receipt;
- browser and subprocess boundaries may expose opaque request-equivalent usage,
  so exact upstream request/cost claims require a future injected usage meter.

Historical Graphiti evidence was advisory: prior serialized canaries used
single-use authority and first-failure stopping, while one authorized Reddit
run proved execution and observability but produced zero content. Current code
and retained repo plans were treated as authority.

## Contract

`prepare(spec, catalog)` validates and seals explicit providers, adapters,
cases, fixtures, expectations, source/catalog digests, effect class, and hard
ceilings. It is pure with respect to credentials and transports.

`execute(plan, grant, deps)` first validates an exact grant, then resolves only
the dependencies named by the sealed plan. It runs bounded cases, records the
first failure and any uncertain effect, always tears down exact owners, and
returns one append-only receipt. It is the only effect-capable entry point.

`verify(receipt, plan)` checks schema, digests, selection, ceiling adherence,
redaction, result classification, accounting confidence, and teardown without
re-executing a provider.

## Provider Matrix

| Adapter family | First accepted provider-free evidence | Later gated evidence |
|---|---|---|
| Reddit keyless HTTP | sealed replay plus loopback HTTP | exact readiness/canary grant |
| YouTube yt-dlp | sealed replay plus fake executable/PATH | exact readiness/canary grant |
| X/Facebook/LinkedIn Agent Browser | sealed replay plus browser-protocol simulator | exact profile/route lease and one canary |
| Reddit Agent Browser | same browser simulator contract | exact profile/route lease and one canary |
| Reddit ScrapeCreators | replay plus loopback HTTP/API substitute | exact credential/profile and canary grant |

Engine web-search and reasoning providers may adopt the harness later through
their own catalog capabilities and transport ports. The initial implementation
is deliberately bounded to acquisition adapters and does not claim one generic
semantic oracle.

## Evidence And Dependency Taxonomy

- in-process: schemas, parsers, normalization, catalog, sealing, verification;
- local-substitutable: loopback HTTP servers and fake executables;
- remote-but-owned: isolated service processes and browser-protocol simulators;
- true external: provider endpoints, authenticated browser profiles, paid APIs,
  and any remote readiness probe.

P0-P3 cover static/catalog, sealed replay, owned transport, and isolated
service join. P4 readiness and P5 canary always require separate exact grants.
Drift/soak is intentionally excluded from presubmit and requires a new plan.

## Failure Semantics

Stable outcomes distinguish success with content, success with zero yield,
authentication required, authorization mismatch, dependency unavailable,
rate limited, CAPTCHA/challenge, route drift, parser drift, malformed output,
budget exhausted, timeout, accounting uncertain, redaction failed, teardown
failed, and internal harness error. Transport completion and useful yield are
orthogonal.

External attempts are serialized, default to one, and never automatically
retry. Auth, challenge, rate limit, lease/route mismatch, uncertainty, timeout,
redaction, or teardown failure stops the campaign. The first failure and effect
uncertainty remain immutable evidence.

## Safe Artifact Boundary

Receipts store only safe reason codes, counts, timestamps, identities, digests,
budgets, confidence, and teardown evidence. Raw auth material, cookies,
headers, environment contents, private response/page text, and reusable browser
routes are prohibited. Authenticated raw captures remain outside Git until a
separate sanitization review produces a sealed safe fixture.

## Implementation Handoff

Create `dev/last30days/provider_acceptance/` with contract, catalog, campaign,
effect, receipt, redaction, and port modules, plus
`dev/last30days/scripts/provider_acceptance.py`. Begin with red tests for
sealing and grant validation, then add Reddit loopback HTTP and YouTube fake-
command tracers. Freeze shared contracts before parallel tracer ownership.

Agent Browser simulation, isolated service join, readiness, and live canaries
are later packets in that order. The browser simulator explicitly covers X,
Facebook, LinkedIn post/profile, and Reddit browser adapters; a loopback API
substitute covers Reddit ScrapeCreators before the isolated join. No P4/P5
packet may be activated by citing this architecture plan.

## Invalidation Map

- authority rejection before invocation invalidates the selected case and
  whole-campaign verdict but creates no transport sample;
- transport failure invalidates that case's transport/yield verdict, while
  preserving admission, consumed budget, failure, and prior cases;
- parse/normalization failure invalidates normalized/yield claims while
  preserving transport and accounting observations;
- accounting uncertainty invalidates exact budget compliance and overall
  acceptance, while preserving observations labeled
  `opaque_request_equivalent`;
- timeout or uncertain effect invalidates retry eligibility and terminal
  acceptance, while preserving attempts and uncertainty;
- redaction failure invalidates publication and downstream use of that unsafe
  receipt, while prior safe receipts survive;
- teardown failure invalidates lifecycle safety and overall acceptance, while
  completed observations survive only as teardown-incomplete.

Partial evidence is never promoted to full case, provider, tier, or campaign
acceptance, and a later stop never erases an unaffected finalized sample.

## Graphiti Write Status

`not_written`; no memory write was authorized. Repository artifacts are the
durable authority.

## State Location

This note and its JSON companion are the restart-safe architecture record.
