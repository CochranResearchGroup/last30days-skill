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

## Best Next Action

Implement and run T0-T2 only after the operator authorizes execution of this
plan. Return at G1 with deterministic evidence and the exact six-case query
labels for approval before generating more Reddit traffic.
