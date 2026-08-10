# Plan 0039 | X Retrieval Identity And Cache Repair

State: CLOSED
Roadmap: P15
Plan version: 4
Date: 2026-08-10
Predecessor: Plan 0038 version 3/checkpoint P0038-C03

## Objective

Make authenticated X collection produce durable, correctly attributed evidence
that remains retrievable through the public cache-only MCP query surface after
an unrelated source-only tick becomes the ordinary query head.

## Current State

- implementation commit `6a77d4823e43580f677415ecbd1e914110f3fccb` is
  pushed to `origin/main`; installed service 0.3.44/schema 16 and MCP adapter
  4.0.3 report the canonical contract digest and pass fresh-process discovery;
- stable numeric X status identity, exact raw-candidate rejection accounting,
  source-aware terminal snapshot selection, public-plus-exact-profile access,
  and validated query/refresh `profile_id` forwarding are implemented and
  covered by focused and full regression suites;
- the sole authorized live X tick `tick-e15b1ed57efbb0c618253ecd90429295`
  terminated `complete_degraded`: its one provider attempt failed transiently
  with `safe_error_code=agent_browser_error` before any browser operation or
  page signal, observed zero candidates, and consumed one network request;
- no retry was made. The installed cache-only MCP query selected the exact new
  failed X snapshot `tick-snapshot-6d850a95c831f066294525a3530de61e`,
  returned zero evidence, and reported `coverage_gaps=["x"]`, proving that the
  repaired selector does not silently fall back to stale X evidence;
- current and rollback databases pass `PRAGMA quick_check`; `daily-default`
  remains ready and unchanged, and the retained browser profile lease is
  available with no holder or waiter. The remaining live source blocker is
  recorded without widening this closed implementation plan.

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

### Checkpoint P0039-C04 | 2026-08-10

Plan version: 4

State transition:

- `reviewed_preinstall_candidate -> installed_terminal_live_blocker`.

Progress classification:

- `outcome_progress`; the repaired code, public contract, release identities,
  installed runtime, and fail-closed cache behavior are accepted. The single
  live acquisition boundary ended in a retained transient browser blocker.

Install and runtime evidence:

- implementation commit `6a77d4823e43580f677415ecbd1e914110f3fccb`
  was pushed before installation. The first installer invocation failed closed
  before mutation because `--artifact` was required; the second and final
  service invocation installed the reconciled 0.3.44 artifact with SHA-256
  `1c47b685e4690d64953d10962109b474fa3e3bbf64a0d7aa89614e3a01411138`;
- installed service readback is ready at 0.3.44/schema 16, release
  `releases/0.3.44`, runtime-manifest SHA-256
  `c63fe7e8ae771210f1ab91e9d226d0dcab0187e52094b729be5f9716880465bd`,
  and contract SHA-256
  `fe8727fbe0d4e2f6775f49a6fc958369fe4877ba812bae4ef69121b88f12e2f1`;
- one MCP install produced adapter 4.0.3 with installed binary SHA-256
  `4900af6ba30af06e0a90cf675b0c5d83477b2ef5aaed486bbea9ff878890d08c`;
  fresh JSON-RPC discovery and compatibility readback passed, and a named
  profile resolved access partitions `public` plus
  `profile:last30days-facebook`.

Live acceptance evidence:

- browser access planning selected fresh retained profile
  `last30days-facebook`, recommended `use_selected_profile`, required no manual
  action, and browser-capability preflight returned `wouldLaunch=false` with a
  validated stealth-CDP executable binding;
- the ready X-only service preflight fixed one lane, one `x_agent_browser`
  provider, one attempt, three items, zero paid/model budget, and interval
  `2026-08-01T00:00:00Z..2026-08-10T00:00:00Z`;
- the sole enqueue created tick `tick-e15b1ed57efbb0c618253ecd90429295`.
  Provider attempt `provider-attempt-69155789e4000dbd795a7fb1f586e006`
  ended transient failure with `safe_error_code=agent_browser_error`, zero
  browser operations/page signals, zero observed/accepted/rejected items, one
  network request, six seconds, and no fallback. No second attempt ran;
- promoted snapshot `tick-snapshot-6d850a95c831f066294525a3530de61e`
  records `x=failure`. A fresh installed cache-only named-profile query bound
  to that exact snapshot, returned a miss with zero evidence and
  `coverage_gaps=["x"]`; it did not resurrect the older corrupted X rows.

Validation and operational state:

- candidate validation remains 2,653 Python outcomes with seven skips, full Go
  tests/vet, generated-contract cleanliness, compilation, release/runtime
  locks, formatting, planning/goal/authority audits, and diff hygiene;
- current and 0.3.43 rollback databases both return `ok` from
  `PRAGMA quick_check`; `daily-default` remains ready for its next unchanged
  boundary; the named browser profile lease is available with zero holders and
  waiters. Browser resource-pressure reporting names no cleanup candidate, so
  no unrelated process was changed.

Acceptance disposition:

- criteria 1-7 and 9 pass. Criterion 8 closes through its explicit alternate
  terminal condition: exact browser-provider blocker retained, no retry, and
  fail-closed newest-source snapshot behavior proven. Plan 0039 and P15 close;
  any new live retry or browser-runtime repair requires a successor authority.

Subagent status and reconciliation:

- `review_complete`; the single fresh read-only reviewer made no edits. Its
  accepted findings were repaired in the sole rework cycle and no later review
  discovery was opened.

Authority classification:

- `inherited_authority`; one service install, one MCP install, and one
  live X tick were consumed exactly as bounded. No second tick, schedule
  mutation, historical rewrite, fallback provider, tag, release, or PR ran.

Graphiti write status:

- provider readiness and duplicate search passed. The one idempotent write job
  `67993046-7ee8-4d5f-a544-7e5727b33ccb` timed out once during node extraction
  after 45 seconds and is non-retryable; no second write was queued.

Next action:

- no action remains in this plan. Treat the retained `agent_browser_error` as
  evidence for a separately authorized browser-runtime diagnostic if live X
  acquisition is revisited.
