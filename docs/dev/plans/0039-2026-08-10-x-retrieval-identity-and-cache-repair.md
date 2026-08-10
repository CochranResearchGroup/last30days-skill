# Plan 0039 | X Retrieval Identity And Cache Repair

State: OPEN
Roadmap: P15
Plan version: 3
Date: 2026-08-10
Predecessor: Plan 0038 version 3/checkpoint P0038-C03

## Objective

Make authenticated X collection produce durable, correctly attributed evidence
that remains retrievable through the public cache-only MCP query surface after
an unrelated source-only tick becomes the ordinary query head.

## Current State

- the handoff's installed MCP/runtime baseline is current: a fresh 4.0.2
  process is compatible with ready service 0.3.43/schema 16, the current and
  rollback databases pass `PRAGMA quick_check`, and `daily-default` is ready;
- the latest scheduled X lane did not fail rendered-page extraction or
  authentication: it observed 10 candidates, accepted three, rejected seven,
  used one request, and reported no auth, challenge, CAPTCHA, rate-limit, or
  fallback signal;
- the X browser quality gate emits run-local display IDs (`X1`, `X2`, ...),
  while durable source identity currently consumes those IDs. Repeated runs
  therefore collide on `(service_id, source_native_id, access_partition_id)`;
  retained source records prove current text was attached to older X URLs;
- the service query contract already accepts `profile_id`, but the MCP query
  and refresh tools omit it and hard-code `default`, making X evidence stored
  in `profile:last30days-facebook` unreachable through the public MCP surface;
- the ordinary query path binds every filtered request to one singleton head.
  A later Facebook-only tick superseded the prior all-source snapshot, so an X
  filter returns a miss even though the previous terminal snapshot contains
  nine authorized X entries;
- these source-backed defects supersede the handoff's proposed retry-first
  extractor diagnosis. No X reauthentication or scraper-selector repair is
  justified by current evidence.

### Handoff Corrections

The retained tick and source-record evidence correct the handoff's proposed
failure classification and retry order; the facts above are the successor
authority for this implementation.

## Scope

- derive stable X source-native identity from the canonical status URL while
  preserving short `X1`-style display IDs for slash-command rendering;
- preserve that stable identity through normalization and acquisition worker
  publication, and retain bounded quality-rejection diagnostics;
- select the newest terminal snapshot that covers an explicitly requested
  source set, while retaining the singleton ordinary head for unfiltered
  queries and reporting metadata from the exact selected snapshot;
- expose bounded `profile_id` selection on MCP query and refresh, generate and
  lock the changed contract, and release the adapter under a new identity;
- release/install the service and MCP adapter, then consume at most one live
  X-only manual tick to prove corrected identity and cache retrieval end to end;
- update canonical Skill/release/operator surfaces required by the changed
  public contract and installed release.

## Non-Goals

- no new X selector strategy, relevance-ranking model, browser profile,
  credential, source, schedule, timer, notification, database schema, or
  external paid provider;
- no rewrite or destructive repair of historical source/version rows;
- no Facebook, LinkedIn, Reddit, or YouTube acquisition attempt;
- no second X attempt if the single acceptance tick reaches a terminal source,
  browser, auth, challenge, budget, or quality result;
- no Git tag, GitHub release, or pull request.

## Acceptance Criteria

1. Focused regressions fail before implementation and prove X source-native
   identity is derived from the status ID, remains stable under result
   reordering, and reaches the acquisition result unchanged.
2. X quality diagnostics preserve deterministic rejection reasons whenever
   observed candidates exceed accepted candidates.
3. Source-filtered cache queries select the newest terminal snapshot whose
   completeness map mentions every requested source, return that exact
   snapshot's metadata, and never read staging snapshots or silently fall back
   past a newer failure/empty result for the requested source.
4. Unfiltered queries retain the singleton ordinary-head behavior and access
   partition filtering remains fail closed.
5. MCP query and refresh accept a validated `profile_id`, default to
   `default`, forward the selected profile to the service request, and receive
   a new release-locked adapter identity without changing database schema 16.
6. Focused Python/Go tests, generated-contract cleanliness, applicable full
   suites, formatting, planning/authority audits, and patch hygiene pass.
7. The service and MCP adapter are committed, pushed, installed once from a
   clean revision, and fresh-process discovery/readback proves exact compatible
   versions and contract digest.
8. One bounded X-only acceptance tick either proves three correctly attributed
   durable items and a profile-authorized cache-only MCP hit, or closes with an
   exact terminal blocker without another acquisition attempt.
9. The repository closes clean with local `main == origin/main`, and runtime,
   schedule, database, retained browser, and rollback readbacks are recorded.

## Definition Of Done

- criteria 1-9 have exact test, runtime, receipt, identity, provenance,
  contract, commit, and push evidence;
- P15 and this plan close only after the single live acceptance boundary has a
  terminal disposition and all safe closeout work is complete.

## Execution Bounds And Gates

- maximum work-unit attempts: 2; maximum review/rework cycles: 1; maximum
  consecutive hardening-only checkpoints: 2;
- one service install, one MCP install, and one live X-only tick are authorized
  after the candidate is committed and all pre-install gates pass;
- stop without retry on login, checkpoint, CAPTCHA, rate limit, wrong profile,
  unsafe destination, browser ownership ambiguity, deadline exhaustion,
  provider fallback, database integrity failure, or need for a second tick;
- the primary agent owns the serialized code, release, install, and live-effect
  boundaries. One fresh independent review is required before closeout.

## Work Graph

| Packet | Outcome | Depends on | Gate |
|---|---|---|---|
| X01 identity | Stable status-derived source identity and rejection receipts | C01 | red/green browser, normalize, worker tests |
| X02 retrieval | Source-aware terminal snapshot selection with exact metadata | C01 | red/green query and application tests |
| X03 public contract | Profile-aware MCP query/refresh and locked release identity | X02 | Go contract/generation/integration tests |
| X04 release candidate | Version/docs/package convergence and broad validation | X01-X03 | full candidate gate and independent review |
| X05 installed acceptance | One install boundary and one X-only tick | X04 | fresh discovery, DB/runtime/browser/query receipts |
| X06 closeout | Reconcile findings, Graphiti, docs, commit and push | X05 | planning audits and clean origin alignment |

X01 and X02 are logically separable, but the primary keeps ownership because
both meet in acquisition-to-query provenance. X03 follows the query contract.
X05 is the only external acquisition effect.

## Validation Plan

- TDD focused tests for X browser/normalization/worker identity and diagnostics;
- TDD snapshot-publisher and cache-application tests for source-specific
  selection, exact metadata, failure/empty freshness, and partition isolation;
- MCP handler/schema/release-lock generation tests plus full Go tests and vet;
- applicable full Python suite, compilation, generated-file, formatting,
  planning, authority, and diff checks;
- pre/post install hashes and versions, fresh `service_info`, database checks,
  schedule status, browser inventory, exact tick/provider/snapshot/source rows,
  and a cache-only MCP query with the authorized profile.

### Checkpoint P0039-C01 | 2026-08-10

Plan version: 1

State transition:

- `handoff_retry_hypothesis -> confirmed_identity_partition_head_defects`.

Progress classification:

- `outcome_progress`; retained service receipts and durable rows replace the
  speculative extraction/reauth path with three reproducible code seams.

Evidence:

- X provider attempt `provider-attempt-b66c...` observed 10, accepted three,
  and rejected seven without auth, challenge, fallback, or source failure;
- current provider items use three 208660... status URLs, while the superseded
  snapshot attaches their current text to three older 208536... URLs through
  colliding `X1`/`X2`/`X3` records;
- MCP query hard-codes `profile_id=default`; the X entries are private-profile
  partitioned;
- promoted snapshot `tick-snapshot-edacb2efdce06eaf2def9d41607d1c20`
  contains only Facebook, while the immediately superseded scheduled snapshot
  contains X and the other successful lanes.

Subagent status and reconciliation:

- `not_spawned`; startup and diagnosis stayed on the serialized critical path.
  A fresh independent review remains required at X04.

Authority classification:

- `inherited_authority`; the operator requested handoff correction, planning,
  repair, and execution. The sole external acceptance effect is explicitly
  capped at one X-only tick.

Review disposition summary:

- `blocking=3` identity, profile access, and source snapshot selection;
  `nonblocking_backlog=0`, `rejected=2` reauthentication and extractor retry,
  `needs_evidence=1` rejection-reason propagation.

Graphiti write status:

- pending validated outcome; repo/runtime evidence remains authoritative.

Next action:

- establish the focused red tests for X identity, source-aware retrieval, and
  MCP profile forwarding, then implement one bounded vertical slice at a time.

### Checkpoint P0039-C02 | 2026-08-10

Plan version: 2

State transition:

- `confirmed_identity_partition_head_defects -> validated_release_candidate`.

Progress classification:

- `outcome_progress`; every confirmed seam now has a red/green regression and
  the independently versioned service/MCP candidate is internally consistent.

Owned changes:

- X browser items retain short display IDs but carry canonical numeric status
  IDs; normalization publishes the stable ID, and the worker accounts for
  candidates removed after browser quality gating;
- source-filtered queries select the newest ever-promoted terminal snapshot
  whose completeness receipt mentions every requested source, bind lookup to
  its exact snapshot ID, retain failure/empty freshness, and preserve the
  singleton head for unfiltered queries;
- both tick and legacy retrieval paths enforce the service-derived public or
  exact-profile partitions;
- MCP query/refresh validate and forward `profile_id`; adapter 4.0.3 and
  service 0.3.44 preserve database schema 16 and the canonical catalog digest;
- Skill, MCP, configuration, changelog, release tests, and runtime manifest are
  synchronized with the public behavior.

Validation evidence:

- the identity tests failed on missing `source_native_id` and `X1` publication,
  then passed status-level and reordered-result proofs;
- the retrieval tests failed on absent source selection, metadata binding, and
  partition forwarding, then passed source-success, later unrelated head,
  later source-failure, exact metadata, and public-partition cases;
- the MCP test failed on hard-coded `default`, then passed named-profile
  forwarding plus invalid-profile rejection;
- focused changed-area Python suites, Skill/package contracts, release/runtime
  tests, full Go tests/vet, contract generation, and deterministic service
  artifact build pass. The candidate artifact SHA-256 is
  `fa0ba9eb4eaa5a4f3f64d7e90db520a579d095de84eba1e1c347bf3bb113b7ab`.

Subagent status and reconciliation:

- `not_spawned` through implementation; the required fresh independent review
  is the next packet and has no write authority.

Authority classification:

- `inherited_authority`; changes remain within Plan 0039's source, contract,
  release, documentation, and test surfaces. No install or live X call has run.

Review disposition summary:

- `blocking=0`, `nonblocking_backlog=0`, `rejected=0`,
  `needs_evidence=2` full-suite/fresh-review and installed/live acceptance.

Graphiti write status:

- pending installed terminal outcome; no intermediate episode is queued.

Next action:

- run the fresh independent candidate review and full pre-install gate, repair
  at most one blocking review cycle, then commit/push before installation.

### Checkpoint P0039-C03 | 2026-08-10

Plan version: 3

State transition:

- `validated_release_candidate -> reviewed_preinstall_candidate`.

Progress classification:

- `outcome_progress`; the single review/rework cycle closed every blocking and
  evidence finding, and the complete candidate gate now passes.

Fresh review reconciliation:

- accepted and repaired three blocking findings: raw X candidates removed by
  canonical dedupe/result limits now have exact reasons and totals; explicit
  empty MCP profiles fail closed for query and refresh; the current release
  documentation consistently names schema 16;
- accepted and supplied all three requested evidence packets: multi-source
  all-of selection, newer empty and exact snapshot metadata; public/exact/other
  profile isolation on tick snapshots plus an actual legacy SQLite index; and
  named-profile refresh forwarding;
- accepted both nonblocking findings: normalization defensively derives status
  identity from a canonical X/Twitter URL even when an ordinal/mismatched ID is
  supplied, and the MCP README now says named profiles add their exact private
  partition to public evidence;
- retained the review's two rejected defect claims: source-specific selection
  and application partition wiring were already correct and remain unchanged.

Validation evidence:

- the remediation regressions were observed red for missing dedupe totals,
  ordinal normalization fallback, and empty-profile defaulting, then passed;
- focused X/worker/query/application/retrieval Python suites and full Go
  tests/vet pass after reconciliation;
- the complete Python suite exits zero with 2,653 collected outcomes and seven
  skips; contract generation, compilation, runtime/release locks, Go formatting,
  planning/goal/authority audits, and diff hygiene pass;
- reconciled service artifact SHA-256 is
  `1c47b685e4690d64953d10962109b474fa3e3bbf64a0d7aa89614e3a01411138`.

Subagent status and reconciliation:

- `review_complete`; one fresh read-only reviewer supplied the findings above,
  made no edits, and the primary performed the sole authorized rework cycle.

Authority classification:

- `inherited_authority`; no installation, live browser/source call, schedule,
  database, or external state change occurred during review/rework.

Review disposition summary:

- `blocking=3 accepted_repaired`, `nonblocking_backlog=2 accepted_repaired`,
  `rejected=2 confirmed_no_defect`, `needs_evidence=3 supplied`.

Graphiti write status:

- pending installed terminal outcome; no intermediate episode is queued.

Remaining acceptance criteria:

- criteria 1-6 pass; criteria 7-9 remain at commit/push, install, single live
  X acceptance, installed readback, and terminal closeout.

Next action:

- verify remote ancestry and candidate cleanliness, commit/push, then install
  the exact service and MCP artifacts before the sole X-only acceptance tick.
