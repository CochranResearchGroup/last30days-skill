# Plan 0124 | WI-010 Provider-Free P0-P3 Campaign

State: OPEN
Lane: P53
Work item: WI-010
Branch: feat/provider-acceptance-p0-p3-v1
Target: main
Integration: merge
Roadmap: P53
Plan version: 1
Date: 2026-09-14
Execution owner: /root
Coordination owner: /root
Requested model route: host default with three parallel bounded tracers
Effective runtime model: not exposed

## Objective

Implement and accept the common provider-free P0-P3 campaign across all eight
advertised acquisition adapters with independently verifiable, append-only
receipts and no credential or external-provider exercise.

## Current State

Plan 0123 froze the `prepare -> execute -> verify` architecture and WI-010 is
`READY`. No harness implementation exists yet. The eight registered adapters
are X Agent Browser, Facebook Agent Browser, LinkedIn post Agent Browser,
LinkedIn profile Agent Browser, YouTube yt-dlp, Reddit keyless, Reddit Agent
Browser, and Reddit ScrapeCreators.

## Definition Of Done

P0 catalog sealing, P1 fixture replay, P2 owned transport, and P3 isolated
service join pass for every adapter. A verifier that does not invoke transport
accepts durable receipts bound to the plan, catalog, fixtures, budgets,
outcomes, redaction, and exact-owner teardown. Focused and comprehensive
provider-free validation pass with zero credential resolution, non-loopback
network, real browser, provider, installed-runtime, schedule, deployment,
release, or tracker effect.

## Scope

- add the repo-only provider acceptance package and maintainer CLI;
- seal the eight-adapter catalog and provider-free fixtures;
- implement replay, HTTP loopback, fake-command, and browser-simulator ports;
- join every adapter through an isolated temporary service/database/socket;
- emit immutable JSON receipts and verify them independently;
- preserve first failure, accounting confidence, budget, redaction, and
  teardown evidence.

## Non-Goals

No credentials, provider endpoints, real browser profiles, remote readiness,
live canaries, retries after uncertain effects, installed runtime mutation,
production data, schedule, release, deployment, issue mutation, or Graphiti
write. P4 and P5 remain unauthorized.

## Work Graph And Ownership

Critical path: coordinator freezes contracts/catalog/receipt schema -> three
tracers run in parallel -> coordinator joins P3 and validates -> independent
review -> bounded remediation -> acceptance.

| Unit | Owner | Depends on | Write surface | Terminal evidence |
|---|---|---|---|---|
| Shared contract | `/root` | none | `dev/last30days/provider_acceptance/` shared modules, CLI, shared tests | frozen P0/P1 contract tests |
| HTTP tracer | subagent `http_tracer` | shared freeze | HTTP adapter module, HTTP fixtures/tests only | Reddit keyless and ScrapeCreators P2 receipts |
| Command tracer | subagent `command_tracer` | shared freeze | command adapter module, YouTube fixtures/tests only | YouTube P2 receipt |
| Browser tracer | subagent `browser_tracer` | shared freeze | browser adapter module, five browser fixtures/tests only | X, Facebook, LinkedIn post/profile, Reddit-browser P2 receipts |
| P3 join and acceptance | `/root` | all tracers | join module/tests, plan and authority projections | eight P0-P3 receipts plus verifier and suite results |

Maximum nesting depth is one; children may not spawn. Concurrency is the host
cap of four including the coordinator. Each tracer stops after its owned files
and focused tests and returns its run handle, status, files, tests, and known
gaps. `/root` owns all shared schemas and final reconciliation.

## Frozen Acceptance Contract

1. P0 seals exactly eight unique adapter IDs and rejects unknown or duplicate
   cases without resolving any dependency.
2. P1 proves success-with-content, success-with-zero-yield, malformed/parser
   failure, provenance, and bounded failure semantics from sanitized fixtures.
3. P2 observes the real request/protocol construction through loopback HTTP, a
   fake PATH executable, or an in-memory browser protocol simulator; it rejects
   non-owned transports before invocation.
4. P3 runs the campaign through a dedicated temporary service identity, SQLite
   database, and local socket/port, then proves exact-owner cleanup and a clean
   post-run census.
5. Receipts bind plan/catalog/source/fixture digests, tier, adapter/case IDs,
   planned and observed budgets, accounting confidence, normalized counts,
   safe outcomes, redaction, and teardown. `verify` is transport-free and
   detects tampering.
6. No partial sample is promoted. Authority mismatch, transport/parser drift,
   accounting uncertainty, timeout, redaction failure, and teardown failure
   invalidate only the claims named by Plan 0123's invalidation map while
   preserving unaffected finalized samples.

## Validation

- focused tracer tests run independently per transport family;
- joined provider-acceptance tests cover all eight adapters and all P0-P3
  tiers, including tamper and fail-closed tests;
- `uv run pytest` is the comprehensive provider-free regression;
- planning, active-lane, authority, documentation, and `git diff --check`
  audits pass;
- a fresh independent reviewer evaluates repo conformance and the frozen
  acceptance contract against the exact candidate commit.

## Stop Rules

Stop before secret resolution, a non-loopback connection, a real browser or
provider executable, installed-service mutation, private fixture capture, or
P4/P5 execution. Stop the affected unit on uncertain accounting, ownership,
redaction, or teardown and preserve the partial receipt. Do not expand beyond
the eight registered acquisition adapters.

## Acceptance Criteria

1. Every adapter has independently verifiable P0, P1, P2, and P3 evidence.
2. Every receipt verifies without transport access and fails verification when
   a sealed identity, digest, budget, outcome, or teardown field is altered.
3. Each tracer's owned transport invocation and cleanup are independently
   reproducible with a focused test command.
4. Comprehensive provider-free validation and governance audits pass.
5. The final effect census is zero for credentials, external providers, real
   browsers, installed runtimes, schedules, releases, deployments, and issues.

## Next Action

Freeze the shared contract and catalog, then launch the three bounded transport
tracers in parallel.

### Checkpoint P0124-C01 | 2026-09-14

Plan version: 1

State transition: `OPEN -> OPEN`.

Progress classification: `implementation_complete`; the shared harness, three
transport tracers, eight fixtures, isolated P3 join, CLI, and offline verifier
produced 32 accepted adapter-tier samples. Comprehensive validation and
independent review remain before plan closure.

Authority classification:

- `inherited_authority`

Subagent status and reconciliation: `joined`; HTTP tracer `/root/http_tracer`
reported 5 focused passes, command tracer `/root/command_tracer` reported 5,
and browser tracer `/root/browser_tracer` reported 8. `/root` assembled the
disjoint files and independently ran the combined provider-acceptance suite.

Validation: provider-acceptance suite 22 passed; campaign run and separate CLI
verification each accepted 32/32 samples. The first comprehensive suite run
preserved one authority-audit failure caused by an incorrect P02 roadmap state
introduced during lane registration; 3,146 tests passed and 8 skipped. The
projection defect is corrected before the no-retry comprehensive rerun.

Effect boundary: zero credentials, external provider calls, real browser
actions, and installed-runtime mutations. P4/P5 remain held.

Next action: run the corrected comprehensive gate, commit the exact candidate,
and obtain one fresh independent review.

### Checkpoint P0124-C02 | 2026-09-14

Plan version: 1

State transition: `OPEN -> OPEN`.

Progress classification: `blocking_review_remediated`; fresh review of
`c5271380` rejected the first candidate with eight accepted blockers covering
asserted redaction, unclosed dependencies/effect census, incomplete P1 replay,
replacement rather than production adapters, recomputable receipt forgeries,
per-tier rather than cumulative budgets, exception evidence loss, and
overwriteable receipt output.

Authority classification:

- `inherited_authority`

Finding disposition: all eight were `blocking`. One bounded remediation pass
added schema-enforced evidence redaction, exact-class dependency admission and
ledger reconciliation, five P1 scenarios per adapter, production-adapter
transport injection, source/timestamp/planned-budget bindings, semantic
verification, cumulative pre-invocation budgets, first-failure receipts, and
exclusive pre-execution receipt creation.

Validation: 34 provider-acceptance tests pass. The regenerated canonical
receipt accepts 64/64 samples across eight adapters and P0-P3, records 16 owned
local request or request-equivalents, eight isolated joins, 32 normalized item
observations, no first failure, and zero credentials/external providers/non-
loopback calls/real browsers/installed runtime/schedule/release/deployment/
tracker effects. A duplicate output attempt stopped before dependency
resolution with exit 2 and left the receipt digest unchanged.

Next action: commit the remediated candidate, run the comprehensive suite and
closed-world verification limited to these eight findings, then close only if
both pass.
