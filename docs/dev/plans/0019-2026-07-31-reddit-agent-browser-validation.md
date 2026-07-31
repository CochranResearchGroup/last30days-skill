# Plan 0019 | Reddit agent-browser production validation

State: OPEN
Roadmap: P07
Date: 2026-07-31
Plan version: 1
Predecessor: Plan 0018 checkpoints C22 and C23

## Objective

Determine whether the source-ready Reddit agent-browser fallback is reliable,
bounded, observable, and valuable enough for recurring service use. Acceptance
requires current browser compatibility, repeatable public-post yield, correct
fallback routing, installed-service proof, durable evidence/index advancement,
and clean failure behavior. Test counts or a healthy browser process alone are
not acceptance evidence.

## Current State

- Commit `12b7298` implements the opt-in Reddit browser adapter in source
  service 0.2.13. Commit `fe50d5d` records its Plan 0018 closeout.
- Thirty-eight focused tests and the complete deterministic suite passed.
- One public `OpenClaw` query completed in about 47 seconds. The initial DOM
  extraction failed closed, one remediation updated the selector, and a read
  against the same page returned seven candidates.
- The result proves one current page shape, not repeatability, performance,
  installed-runtime behavior, durable yield, restart recovery, or production
  value.
- Installed service 0.2.12 remains production authority. Source 0.2.13 is not
  installed or pushed, and the paused collection has not been resumed.
- T0 attempt 1 failed closed on 2026-07-31 before new Reddit traffic. The
  install doctor reports unrelated duplicate leases on profile `default`; the
  remote-view doctor additionally reports the Guacamole stack down; and the
  plan-owned `last30days-reddit` browser still holds the selected social
  profile on `shared_display`, which cannot satisfy T0's required
  `private_virtual_display` access plan.
- T0 passed on 2026-07-31 after Docker recovered without a host restart and
  the plan-owned stale browser had been closed. All required readiness
  surfaces are current and mutually consistent; no Reddit query has run.
- T1 passed on 2026-07-31 with 45 adapter tests, 57 combined adapter/worker
  tests, the complete 2,378-test Python collection, runtime-package/build
  checks, the Go MCP suite, compilation, diff, and authority gates green. No
  Reddit traffic ran.
- T2 passed on 2026-07-31 with 12 real-subprocess fake-CLI cases covering the
  seven-command new-session path, every terminal boundary, malformed output,
  timeout/child termination, redaction, retained-session reuse, and unrelated
  session ownership. No Reddit traffic or browser session ran.
- G1 preflight passed on 2026-07-31: successful results now expose bounded
  command/page-state diagnostics, all deterministic gates remain green, and
  current doctors/access-plan evidence is ready with no plan session or lease.
- G1 Window A ran exactly three spaced, non-retried public searches. A1 yielded
  three relevant posts, A2 returned `checkpoint_required`, and A3 returned
  truthful `extraction_empty`. Post-window status then exposed a hard isolation
  mismatch: the private-display launch request produced `shared_display`.
  Window B did not start, and the named session/browser/tab were closed cleanly.
- Read-only cross-repo diagnosis confirmed the mismatch is deterministic:
  agent-browser fixed RDP route displays intentionally default to
  `shared_display`, the route planner does not compare the requested private
  isolation, and a dry run silently rewrites both binding and launch posture.

## Authority And Gates

The operator's 2026-07-31 instruction, `i approve. execute plan 19`, activates
this plan and authorizes both bounded execution gates below. Push, tag,
publication, and independent release acceptance remain outside that authority.

The approved execution includes these two bounded gates:

1. `G1 | public browser matrix`: authorize up to six public Reddit searches in
   one managed agent-browser profile/session lane.
2. `G2 | installed canary`: after G1 acceptance, authorize installation and
   restart of 0.2.13, one service-owned collection attempt, and the bounded
   soak defined below.

The primary agent must still checkpoint before crossing G1 and G2 and must
stop on the plan's hard-stop conditions; the approval does not increase any
query, attempt, time, concurrency, remediation, or data-scope ceiling.

## Scope

Owned evidence and possible write surfaces:

- `tests/test_reddit_browser.py`;
- focused worker/runtime tests needed to exercise the fallback contract;
- `docs/dev/notes/0019-reddit-browser-validation-receipt.json`;
- Plan 0019, `ROADMAP.md`, and `RUNBOOK.md`;
- source fixes in `reddit_browser.py` or its worker seam only if a bounded test
  exposes a defect and the remediation remains inside this adapter contract.

Public live scope:

- unauthenticated, publicly visible Reddit search and post metadata only;
- no private/quarantined/community-gated content;
- no voting, posting, commenting, messaging, joining, saving, following, or
  account/profile mutation;
- no new credential, proxy, CAPTCHA-solving service, or paid-source use.

## Non-Goals

- proving comprehensive Reddit coverage or parity with the Reddit API;
- testing authenticated or private-community access;
- load testing Reddit or maximizing scrape volume;
- modifying agent-browser itself;
- enabling paid fallback or adding a ScrapeCreators credential;
- release publication.

## Test Stages

### T0 | Bind the candidate and baseline

Before any browser launch:

1. Record source commit, candidate service version, runtime-manifest hash,
   installed service version, schema version, branch state, and rollback target.
2. Record baseline counts for Reddit items, evidence, documents, versions, and
   active-index entries without exposing private corpus content.
3. Require current successful JSON results from:
   - `agent-browser install doctor --json`;
   - `agent-browser doctor remote-view --json` with remote control and route
     pool ready;
   - `agent-browser service status --json` with a ready compatible browser
     build and live route displays;
   - an access plan labeled `last30days` / `reddit-scraper` /
     `reddit-post-search`, target `reddit`, remote-headed RDP view, and private
     virtual-display isolation.
4. Reject retained readiness when its display socket, route allocation,
   browser-build proof, or operator-visible evidence is stale or mismatched.

Acceptance: all identifiers and readiness surfaces agree; otherwise stop
without launching Reddit or changing the service.

### T1 | Deterministic adapter expansion

Add table-driven and fixture tests for:

- all supported DOM shapes: `search-post-unit`, `shreddit-post`, and the
  article/permalink fallback;
- canonical URLs, post IDs, subreddit/author extraction, deleted authors,
  missing bodies, crossposts, promoted units, duplicate posts, and malformed
  permalinks;
- score/comment forms including plain integers, commas, `K`/`M`, `Vote`,
  hidden scores, and absent counts;
- inclusive date boundaries, UTC offsets, invalid timestamps, sort order,
  relevance, item limits, Unicode, punctuation, and encoded query terms;
- verified no-results, an empty-but-post-shaped page, consent/interstitial
  pages, login, checkpoint, 403/429/5xx-style pages, and wrong-host navigation;
- invalid/oversized JSON, subprocess exit, timeout, browser crash, stale tab,
  missing binary, and profile-lease conflict;
- exact quick/default/deep time and scroll ceilings;
- caller labels, target `reddit`, access-plan usage, retained-session reuse,
  bounded command sequence, and absence of raw CDP/process discovery;
- worker routing: keyless success suppresses browser and paid sources; keyless
  empty invokes browser once; browser success suppresses paid fallback; browser
  typed failure preserves diagnostics and invokes paid fallback only when the
  already-configured policy permits it.

Use recorded/synthetic fixtures only. Fixtures must contain no cookies,
credentials, tokens, or raw private data.

Acceptance:

- every matrix row has a deterministic expected item or typed failure;
- no false success for empty or malformed extraction;
- no unbounded retry, navigation, scroll, or subprocess path;
- focused tests, Python compilation, `git diff --check`, the complete pytest
  suite, runtime-package checks, and the plan-authority audit pass.

### T2 | CLI contract integration without Reddit traffic

Exercise the real subprocess boundary against a controlled fake
`agent-browser` executable or captured JSON fixture stream. Prove:

- arguments, JSON decoding, timeout propagation, error redaction, and command
  order across access plan, workspace acquisition, navigation, evaluation, and
  release/cleanup;
- one retained session is reused and an unrelated live profile owner is not
  replaced;
- failure at every command boundary produces one typed adapter result and no
  follow-on browser command after a terminal state.

Acceptance: the adapter-to-CLI contract passes end to end without network
traffic and leaves no session/process fixture behind.

### T3 | Public live-browser matrix — G1

Run exactly six searches across two windows separated by at least 30 minutes.
Use one named managed session, at most one active query, at least 60 seconds
between query starts, paid fallback disabled, and no automatic retry.

Window A:

1. high-yield single topic, quick depth;
2. high-yield multiword topic, quick depth;
3. intentionally improbable topic, quick depth, to verify typed empty behavior.

Window B:

4. repeat case 1 at quick depth to test session reuse and repeatability;
5. repeat case 2 at default depth to test one bounded scroll;
6. a current public topic selected before the window, quick depth, to reduce
   overfitting to the two development selectors.

For every query record start/end time, requested and final URL, selected
profile/session/browser/route, page-state classification, command count,
candidate/accepted/rejected counts, rejection reasons, normalized items, and a
capped screenshot or DOM-shape digest. Never record cookies or headers.

Live acceptance:

- all five positive cases finish with a typed result inside their depth wall;
- at least four of five positive cases return one or more items, and both
  repeated high-yield selectors return items in both windows;
- every accepted item has a unique Reddit post ID, canonical public URL,
  parseable in-range timestamp, subreddit, title, and nonnegative engagement;
- a manual sample of up to three items per positive case is at least 90%
  relevant and contains no promoted unit;
- quick-query p95 is at most 60 seconds and the default query is at most 90
  seconds; no command or routine crosses the 120-second service wall;
- the improbable query returns either verified no-results or a truthful typed
  non-success, never fabricated negative coverage;
- all searches reuse the intended managed profile/session lane, with no leaked
  duplicate browser process or tab accumulation after cleanup.

T3 rejects rather than repairs when two distinct page shapes fail, any
positive selector fails twice, or one remediation cannot restore a newly
observed DOM shape. A remediation does not add a seventh live query.

### T4 | Isolated resilience and contention

Before production installation, use controlled fault injection to prove:

- missing CLI, process exit, malformed output, command timeout, navigation
  mismatch, stale handle/tab, browser disconnect, and lease contention;
- one terminal adapter outcome, one fallback decision, and no retry storm;
- secrets and raw page content are absent from operator diagnostics;
- concurrent worker requests serialize or fail with typed lease pressure while
  only one browser query is active;
- service cancellation/deadline propagates to the browser subprocess and does
  not leave a running job or browser command.

Acceptance: every injected failure is deterministic, bounded, observable, and
leak-free. No live Reddit failure is intentionally induced.

### T5 | Installed-service canary — G2

After T0-T4 pass:

1. Build the source runtime, refresh and verify its manifest, preserve the
   installed 0.2.12 rollback target, install 0.2.13, restart once, and require
   exact installed-version/hash/readiness agreement.
2. Run exactly one public/default-profile collection attempt with:
   - one previously accepted high-yield selector;
   - maximum three Reddit items;
   - browser fallback enabled;
   - paid fallback and all stochastic/App Intelligence workers disabled;
   - one attempt and a 120-second wall.
3. Verify the durable receipt identifies keyless outcome, browser selection,
   typed status, latency, and item count without browser mechanics leaking into
   ordinary MCP responses.
4. Verify one to three new canonical items create corresponding evidence,
   document/version, and active-index advancement, then retrieve at least one
   through the normal MCP query contract with a valid citation.
5. Restart the service once more without starting another collection and prove
   the receipt, corpus rows, active index, schedule state, and query result
   survive unchanged.

Acceptance: exact installed candidate, one terminal attempt, positive durable
yield, citation retrieval, persistence across restart, and zero model/paid
calls. On failure, pause the spec if created, capture the receipt, and roll back
to 0.2.12 if service readiness or existing query behavior regresses.

### T6 | Bounded recurring soak — G2

Only after T5 acceptance, run three scheduled intervals over at least 12 hours,
with at least four hours between interval starts. Keep the same three-item,
one-attempt, 120-second, public-only, paid-disabled, model-disabled envelope.

Acceptance:

- exactly three new terminal receipts and no overlap/duplicate attempts;
- at least two intervals yield posts and the soak produces at least three
  unique accepted post IDs overall;
- all three finish within 120 seconds with no challenge, rate limit, browser
  leak, stuck job, duplicate profile lane, or schedule drift;
- corpus/index counts are monotonic, deduplication is stable, and MCP retrieval
  remains available throughout.

Pause the canary after the third interval regardless of outcome. This stage is
not authorization for indefinite recurring collection.

### T7 | Independent acceptance review

A fresh reviewer evaluates the machine-readable receipt against every
criterion without relying on implementation narration. One consolidated
finding set and one remediation pass are allowed. A failed re-review closes
the packet as rejected, blocked, or split; it does not reopen an unbounded
hardening loop.

## Evidence Contract

Persist one redacted JSON receipt with:

- plan/version, source commit, installed and rollback versions/hashes;
- commands or stable command identifiers, timestamps, exit states, and test
  summaries;
- doctor/access-plan summaries and route/display/browser agreement;
- one record per live case with query label rather than sensitive raw input;
- latency, backend/fallback path, candidate/item/rejection counts, typed error,
  and canonical item IDs/URLs;
- before/after durable counts, job/attempt/receipt IDs, index generation, and
  MCP citation proof;
- hard-stop status, rollback status, reviewer outcome, and remaining risk.

Large screenshots, raw DOM, HAR, and temporary browser diagnostics remain
ephemeral unless a failure requires them. Record their hashes and retention
reason; never persist cookies, authorization headers, profile data, or secrets.

## Hard Stops

Stop the current stage immediately on:

- non-ready or mismatched install/remote-view/access-plan evidence;
- login, checkpoint, CAPTCHA, account restriction, or rate limit;
- navigation outside public `reddit.com` post/search scope;
- any account mutation or request for new authentication;
- paid-source invocation, model call, or new credential requirement;
- query, attempt, time, interval, concurrency, or remediation ceiling breach;
- duplicate independent browser process for the selected profile;
- service readiness regression, stuck job, missing receipt, non-monotonic
  durable state, or inability to preserve/execute rollback;
- secret or private-data capture.

A hard stop records a durable checkpoint. It does not authorize a retry,
additional query, ceiling increase, or bypass.

## Work Units And Dependencies

Critical path owner: primary agent. Active-agent concurrency: one for all live
and installed-runtime work.

```text
T0 -> T1 -> T2 -> G1 -> T3 -> T4 -> G2 -> T5 -> T6 -> T7
                         |                 |
                         +-- reject -------+-- rollback/reject
```

Deterministic fixture authoring and receipt-schema preparation are logically
parallelizable but should converge before T2. Live work is strictly serialized.
No subagent is authorized by this planning request; any later delegation must
name its bounded lane and remain outside live-browser and runtime ownership.

## Bounds

- deterministic implementation/remediation passes: one each;
- public live searches: six total, two windows, one active at a time;
- production collection attempts: one canary plus three soak intervals;
- automatic retries: zero;
- reviewer/rework cycles: one;
- live query wall: 120 seconds absolute;
- soak duration: 12 to 24 hours;
- checkpoint cadence: after every stage and before/after each human gate;
- independent release/tag/push work: not authorized.

## Definition Of Done

Plan 0019 may close `CLOSED` only when T0-T7 are accepted, the canary is
paused, the receipt is durable and redacted, installed state and rollback
status are explicit, every acceptance criterion has current evidence, and the
independent reviewer accepts production use. Otherwise close as `CANCELLED`,
leave `PLANNED`, or transition to a bounded successor with the exact blocker.

### Checkpoint P0019-C01 | 2026-07-31

Plan version:

- 1

State transition:

- `PLANNED -> OPEN`

Progress classification:

- `outcome_progress`

Owned changes:

- activated Plan 0019 and wired its approved execution state into the roadmap
  and runbook;
- preserved all traffic, runtime, retry, data-scope, and release bounds.

Validation evidence:

- the operator explicitly instructed `i approve. execute plan 19`;
- current plan, roadmap, runbook, agent-browser skill, and execution policies
  were re-read before live/runtime work;
- no browser launch, service mutation, or collection attempt preceded this
  checkpoint.

Subagent status and reconciliation:

- `not_spawned`; active concurrency remains one.

Graphiti write status:

- pending after the first validated execution packet.

Authority classification:

- `inherited_authority`

Next action:

- run T0 and stop without traffic or mutation if readiness evidence is not
  current, ready, and mutually consistent.

### Checkpoint P0019-C02 | 2026-07-31

Plan version:

- 1

State transition:

- `active -> awaiting_gate`

Progress classification:

- `blocker_reduction`

Owned changes:

- created the redacted T0 receipt at
  `docs/dev/notes/0019-reddit-browser-validation-receipt.json`;
- made no browser, service, collection, credential, paid-source, or model
  mutation.

Validation evidence:

- source candidate is 0.2.13 with runtime-manifest SHA-256
  `7e878b728694c1c5b48fc82698d3764403f29b37bf91014f42562ac16fd10e0b`;
- installed service 0.2.12/schema 12 is ready on
  `/run/user/1000/last30days/service.sock` with 19 indexed Reddit documents;
- `agent-browser install doctor --json` returned `success=false` with
  `service_duplicate_profile_pressure` caused by three unrelated exclusive
  sessions on profile `default`;
- `agent-browser doctor remote-view --json` returned remote-control `blocked`
  because the Guacamole containers/route pool are unavailable and the install
  doctor is non-ready;
- the Reddit access plan selected `last30days-facebook` but recommended
  `wait_for_profile_lease`: the plan-owned `last30days-reddit` browser is ready
  on `shared_display`/`:11`, while T0 requires `private_virtual_display`;
- no new Reddit query, install, restart, or collection attempt ran.

Subagent status and reconciliation:

- `not_spawned`; all evidence was collected directly by the primary agent.

Graphiti write status:

- not written; the hard-stop receipt and repo checkpoint are durable authority.

Authority classification:

- `human_gate`

Next action:

- obtain explicit authority for successor T0-R1 to preserve unrelated
  sessions, close only the plan-owned `last30days-reddit` browser, reconcile
  the Guacamole stack, and rerun T0 once without Reddit traffic.

### Checkpoint P0019-C03 | 2026-07-31

Plan version:

- 1

State transition:

- `awaiting_gate -> active -> awaiting_gate`

Progress classification:

- `blocker_reduction`

Owned changes:

- executed the operator-approved T0-R1 packet once;
- closed only named session `last30days-reddit`, removing browser PID 1945818
  and releasing the `last30days-facebook` profile lease;
- attempted to start the already-installed Docker Desktop application once;
- made no Reddit request, collection attempt, service install, credential,
  paid-source call, or model call.

Validation evidence:

- post-close resource inventory reports zero plan-browser processes and the
  Reddit access plan reports zero active leases plus
  `defaultAcquisition=launch_new_browser`;
- the three unrelated `default`-profile sessions remain present and unmodified;
- Docker Desktop processes are present, but `docker info` remains unable to
  connect and the host backend log reports HTTP 503 while waiting for the
  engine for more than 1 hour 52 minutes;
- Guacamole Compose was not attempted without a ready Docker engine;
- remote-view readiness therefore remains `blocked` and T0 was not rerun.

Subagent status and reconciliation:

- `not_spawned`; active concurrency remained one.

Graphiti write status:

- not written; the plan checkpoint, runbook, and updated JSON receipt are the
  durable evidence surfaces.

Authority classification:

- `human_gate`

Next action:

- obtain explicit authority for T0-R2 to perform one host-level Docker Desktop
  engine restart, require `docker info` readiness, reconcile the installed
  Guacamole stack, and rerun T0 exactly once without Reddit traffic.

### Checkpoint P0019-C04 | 2026-07-31

Plan version:

- 1

State transition:

- `awaiting_gate -> active`

Progress classification:

- `outcome_progress`

Owned changes:

- resumed after Docker recovered naturally; no host restart was performed;
- verified Guacamole PostgreSQL continuity and all T0 readiness surfaces;
- made no Reddit request, collection attempt, service install, credential,
  paid-source call, or model call.

Validation evidence:

- Docker server 29.6.2 is ready; PostgreSQL and guacd are healthy and the
  Guacamole web container is running;
- PostgreSQL continuity reports `status=ready`, the recorded system identifier
  matches, and the named-volume mount remains authoritative;
- install doctor 0.27.0 reports `success=true`, zero issues, zero duplicate
  pressure, converged runtimes, ready stealth Chromium, and ready privileges;
- remote-view doctor reports remote control, many-to-many, and route pool
  `ready` with zero issues;
- the exact labeled Reddit access plan selects `last30days-facebook`, has zero
  active leases or duplicate pressure, and preserves remote-headed RDP/private
  display posture;
- installed last30days 0.2.12/schema 12 remains ready and the redacted baseline
  counts remain unchanged at 19 Reddit documents and 14 Reddit acquisitions.

Subagent status and reconciliation:

- `not_spawned`; active concurrency remained one.

Graphiti write status:

- not written; checkpoint C04 and the updated JSON receipt are durable.

Authority classification:

- `inherited_authority`

Next action:

- execute T1 deterministic adapter expansion without Reddit traffic, then T2
  fake-CLI contract validation; keep G1/T3 closed.

### Checkpoint P0019-C05 | 2026-07-31

Plan version:

- 1

State transition:

- `active -> active`; T1 `ready -> passed`.

Progress classification:

- `outcome_progress`

Owned changes:

- expanded the Reddit adapter's fixture matrix across all supported DOM
  shapes, normalization gates, typed page/runtime failures, depth ceilings,
  and caller/access-plan posture;
- enforced private virtual-display isolation, bounded candidate accumulation,
  valid timestamps/titles/subreddits, promoted-unit rejection, and truthful
  verified-no-results diagnostics;
- preserved a safe typed browser outcome at the paid-fallback seam and
  refreshed the service runtime manifest;
- aligned the current-repository authority assertion with open Plans 0018 and
  0019;
- made no Reddit request, browser launch, service install/restart, collection
  attempt, credential, paid-source call, or model call.

Validation evidence:

- 45 Reddit adapter tests and 57 combined adapter/worker tests pass;
- Python compilation, `git diff --check`, runtime-package and lifecycle tests,
  reproducible service-runtime build, and installable Skill build pass;
- the complete Python suite collected 2,378 tests and exited zero; the complete
  Go MCP suite passes;
- the plan-authority audit reports `status=passed`, zero issues, and the two
  roadmap-declared open plans.

Subagent status and reconciliation:

- `not_spawned`; the plan fixes active concurrency at one and all work was
  performed by the primary agent.

Graphiti write status:

- deferred; the plan, runbook, and machine-readable receipt are the current
  source-backed evidence surfaces.

Authority classification:

- `inherited_authority`

Next action:

- execute T2 against a controlled fake `agent-browser` subprocess without
  Reddit traffic; keep G1/T3 closed until the T2 checkpoint.

### Checkpoint P0019-C06 | 2026-07-31

Plan version:

- 1

State transition:

- `active -> active`; T2 `ready -> passed`; G1 `closed -> ready`.

Progress classification:

- `outcome_progress`

Owned changes:

- added a temporary executable fixture that crosses the real synchronous
  subprocess boundary without Reddit or browser traffic;
- proved the bounded access-plan, service-status, remote-view, tab, page-state,
  and extraction command order plus nested JSON decoding;
- proved a terminal typed result with no follow-on command at all seven command
  boundaries, malformed JSON, and a one-second subprocess timeout;
- proved retained-session reuse without opening or closing it and preserved an
  unrelated named-session owner by selecting a profile-scoped lane;
- added Reddit-boundary redaction for residual bearer-token and email material
  exposed by the controlled failure stream.

Validation evidence:

- all 12 fake-CLI cases, 57 Reddit adapter tests, and 69 combined
  adapter/worker tests pass;
- Python compilation, runtime-package/lifecycle tests, reproducible runtime
  build, and installable Skill build pass;
- the complete Python suite collected 2,390 tests and exited zero; the complete
  Go MCP suite passes;
- `git diff --check` and the plan-authority audit pass with zero issues;
- no raw CDP/process-discovery command, Reddit request, real browser session,
  collection attempt, install/restart, credential, paid call, or model call
  occurred.

Subagent status and reconciliation:

- `not_spawned`; active concurrency remained one.

Graphiti write status:

- deferred; checkpoint C06, runbook Turn 79, and the updated receipt are the
  durable evidence surfaces.

Authority classification:

- `inherited_authority`; the operator already approved bounded G1, while the
  plan still requires this checkpoint and current readiness before crossing.

Next action:

- rerun current readiness checks, then execute exactly the G1 six-query public
  matrix across two windows at least 30 minutes apart, with one active query,
  60-second start spacing, paid fallback disabled, and no retries.

### Checkpoint P0019-C07 | 2026-07-31

Plan version:

- 1

State transition:

- `active -> active`; G1 `ready -> active` at preflight.

Progress classification:

- `blocker_reduction`

Owned changes:

- exposed the already-bounded CLI operation timings, command count, and
  page-state classification on successful adapter results so every G1 query
  can satisfy the plan's observability contract;
- refreshed the checked runtime manifest;
- performed current read-only G1 readiness checks and made no Reddit request
  or browser mutation.

Validation evidence:

- 57 Reddit adapter tests, the complete 2,390-test Python collection,
  compilation, runtime-package/lifecycle checks, and runtime build pass;
- install doctor 0.27.0 reports success, zero issues/resource warnings, and
  converged runtimes;
- remote-view and remote-control status plus route pool are ready;
- the exact access plan selects `last30days-facebook`, reports zero active
  leases/duplicate pressure, and requests remote-headed RDP/private-display
  launch;
- service status contains no `last30days-reddit` session or browser.

Subagent status and reconciliation:

- `not_spawned`; active concurrency remains one.

Graphiti write status:

- deferred; checkpoint C07, runbook Turn 80, and the receipt are durable.

Authority classification:

- `inherited_authority`; G1 is within the operator-approved six-query public
  scope and all preconditions are now satisfied.

Next action:

- execute Window A exactly once per case, with query starts at least 60 seconds
  apart: `openclaw` quick, `agent browser` quick, and
  `zzqv-no-such-topic-20260731` quick; then hold Window B until at least 30
  minutes after Window A completes.

### Checkpoint P0019-C08 | 2026-07-31

Plan version:

- 1

State transition:

- `active -> awaiting_gate`; T3 Window A `active -> failed_closed`.

Progress classification:

- `regression`

Owned changes:

- ran exactly Window A's three public quick searches with one active query,
  95.304-second and 81.624-second start gaps, paid fallback disabled, and zero
  retries;
- recorded bounded normalized outcomes and a three-item manual sample;
- inspected the plan-owned live session after the window and found one browser
  plus one tab but a display-isolation contradiction;
- stopped before Window B and closed only `last30days-reddit`, leaving zero
  matching sessions, browsers, or Reddit tabs.

Validation evidence:

- A1 `openclaw`: three of seven candidates accepted in 42.794 seconds; all
  sampled items were relevant, non-promoted `search-post-unit` results;
- A2 `agent browser`: typed `checkpoint_required` in 28.861 seconds after five
  commands, with no extraction or retry;
- A3 improbable topic: typed `extraction_empty` in 38.893 seconds after six
  commands, explicitly not verified negative coverage and not retried;
- all queries used profile `last30days-facebook`, session
  `last30days-reddit`, and one active query;
- post-window status reported the requested `private_virtual_display` browser
  as `shared_display` on route `guacamole:1`; cleanup then reported
  `closed=true` and zero plan resources.

Subagent status and reconciliation:

- `not_spawned`; active concurrency remained one.

Graphiti write status:

- not written; the source-backed plan, runbook, and machine-readable receipt
  are the durable incident evidence.

Authority classification:

- `scope_expansion`; repairing agent-browser is an explicit non-goal, while
  accepting `shared_display` would weaken the approved isolation criterion.

Next action:

- obtain operator direction to authorize a separate bounded agent-browser
  isolation repair or cancel the remaining Plan 0019 matrix;
- do not run Window B, T4, installation, canary, soak, push, tag, or release.

### Checkpoint P0019-C09 | 2026-07-31

Plan version:

- 1

State transition:

- `awaiting_gate -> awaiting_gate`; isolation cause `unknown -> confirmed`.

Progress classification:

- `blocker_reduction`

Owned changes:

- performed read-only source and advisory-memory discovery in the current
  agent-browser `main` worktree at `914728ac`;
- ran one documented `remote-view open --dry-run` with the exact Plan 0019
  labels/posture and launched no browser;
- modified no agent-browser source, runtime, route, profile, credential, or
  service state and preserved its unrelated untracked `--full-page` file.

Validation evidence:

- the dry run records requested isolation `private_virtual_display`, selects
  `guacamole-rdp-a` / `guacamole:1` / `:10`, then emits route binding and launch
  isolation `shared_display` with zero planner blockers;
- `build_route_binding` defaults any fixed RDP route with a display name to
  `shared_display` unless the route target explicitly declares otherwise and
  does not receive the request intent for compatibility checking;
- existing unit coverage explicitly expects fixed route display metadata to
  override a stale private allocation with `shared_display`;
- current agent-browser guidance says fixed XRDP route-display smokes use
  `shared_display`, while true `private_virtual_display` uses the service
  private-display allocator;
- Graphiti was healthy and supplied only advisory route-history leads; current
  source and dry-run output are the authority.

Subagent status and reconciliation:

- `not_spawned`; investigation remained direct and read-only.

Graphiti write status:

- not written; the result is already captured in this source-backed checkpoint
  and receipt.

Authority classification:

- `scope_expansion`; dynamic private-display-to-RDP routing requires
  agent-browser product work, while accepting fixed-route `shared_display`
  changes Plan 0019's safety acceptance.

Next action:

- obtain operator selection among: authorize a separately planned
  agent-browser private-display/RDP implementation; explicitly revise Plan 0019
  to accept the route-scoped shared-display topology; or cancel the remaining
  matrix;
- do not retry G1 or run T4-T7 meanwhile.

## Best Next Action

Resolve the G1 isolation hard stop without weakening the private-display
criterion. A repair requires separate scope because modifying agent-browser is
a Plan 0019 non-goal. Until then, keep Window B and T4-T7 closed.
