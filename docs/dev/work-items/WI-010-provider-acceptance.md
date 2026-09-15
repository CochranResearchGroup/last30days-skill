<!-- last30days-work-item:WI-010 -->
# Build controlled provider acceptance

State: IN_PROGRESS
Priority: P0
Lane: Provider Acceptance
Parent: none
GitHub issue: not published; issue mutation was not authorized
Blocked by: none for provider-free implementation; readiness and live canaries require separate exact operator authority
Architecture plan: docs/dev/plans/0123-2026-09-14-provider-acceptance-architecture-and-lane-handoff.md
Execution plan: docs/dev/plans/0124-2026-09-14-wi010-provider-free-p0-p3-campaign.md

## Problem

The repository has extensive provider-shaped unit, parser, fixture, policy,
adapter, and provider-free service tests, but no common acceptance system that
states exactly what was proved at each evidence tier. A parser fixture,
loopback transport, credential probe, successful external request, and useful
content result are materially different claims.

Browser and subprocess adapters also expose request-equivalent accounting at
some boundaries rather than exact upstream request and cost usage. A live test
must not silently promote opaque accounting into an exact budget claim.

## Outcome / Proposed Solution

Build a repo-only provider acceptance harness with three public operations:
`prepare`, `execute`, and `verify`. Preparation seals the selected cases,
adapters, fixtures, expectations, effect class, budgets, and source identity.
Execution is the only effect-capable operation and requires a matching grant.
Verification independently checks the append-only receipt without rerunning a
provider.

Keep HTTP, subprocess, and Agent Browser execution behind distinct internal
ports. A closed capability catalog supplies provider-specific expectations;
the shared harness owns authority, budgets, redaction, teardown, receipts, and
evidence-tier vocabulary.

## Acceptance Evidence

- deterministic replay tests prove every advertised acquisition adapter's
  parsing, normalization, provenance, empty-yield, malformed, and bounded-error
  behavior from sealed fixtures;
- loopback HTTP, fake executable, and browser-protocol simulation prove owned
  transport behavior without an external provider;
- the harness distinguishes successful zero yield, auth failure, rate limit,
  route drift, parser drift, accounting uncertainty, and teardown failure;
- receipts bind plan/source/catalog/fixture digests, planned and observed
  budgets, accounting confidence, safe outcomes, and exact-owner teardown;
- preparation and verification cannot resolve credentials or perform network,
  browser, subprocess-provider, installed-runtime, or external effects;
- readiness and live-canary modes fail closed without a nonexpired exact grant,
  run serially, attempt once, stop on the first uncertainty, and never accept
  environment variables alone as authority;
- a successful request is never reported as useful content, completeness,
  semantic quality, or production readiness without separate evidence.

## Initial Delivery Packets

1. Implement contracts, catalog, redaction, effect ledger, sealed replay, and
   receipt verification in `dev/last30days/provider_acceptance/`.
2. Prove the real acquisition seam with two heterogeneous provider-free
   adapters: Reddit keyless over loopback HTTP and YouTube through a fake
   `yt-dlp` executable.
3. Add deterministic auth, rate-limit, timeout, malformed-output, budget,
   uncertain-accounting, and teardown faults.
4. Add an Agent Browser protocol simulator for X, Facebook, LinkedIn post,
   LinkedIn profile, and Reddit Agent Browser adapters.
5. Add a loopback API substitute for Reddit ScrapeCreators, then join every
   advertised acquisition adapter through an isolated provider-free service
   runtime.
6. Only after packets 1-5 are accepted, draft a separately authorized
   readiness packet and one-canary-per-grant live packet.

## Non-Goals

This work item does not authorize credentials, provider calls, real browser
profiles, remote readiness probes, live canaries, recurring schedules,
installed-service mutation, production data, release, deployment, or GitHub
issue mutation. It does not unify provider semantics into a generic oracle or
claim exact upstream accounting where the adapter cannot observe it.

## Next Owner Action

Plan 0124's provider-free P0-P3 packet is accepted at
`bcaceb96144764f2a17ec62aa8fafeaf03255de2`. Integrate that topic branch only
under separate forge authority. Keep WI-010 `IN_PROGRESS` because readiness
and live-canary P4/P5 evidence remain separately unauthorized and incomplete.
