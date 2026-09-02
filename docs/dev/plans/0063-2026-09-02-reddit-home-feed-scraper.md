# Plan 0063 | Reddit Home Feed Scraper

State: OPEN
Lane: P23
Branch: feat/reddit-home-feed
Target: main
Integration: fast-forward
Roadmap: P23
Plan version: 1
Date: 2026-09-02

## Objective

Add a deterministic Agent Browser scraper for the authenticated Reddit home
feed that can collect 80 unique canonical posts without applying topic-quality
filtering, while preserving the existing Reddit search capability.

## Current State

- `RedditBrowserScraper.search` is limited to Reddit `/search`, caps each DOM
  snapshot at 80 candidates, stops scrolling when raw candidate count reaches
  the requested limit, and applies query-term relevance gates;
- the service acquisition worker already distinguishes `surface_kind=feed` for
  X and LinkedIn but sends every Reddit request through the search access-order
  path;
- prior live Reddit proof established bounded execution and truthful zero-yield
  observability, not successful post retrieval;
- Reddit remains disabled in `daily-default`, and this plan does not enable or
  otherwise mutate that schedule.

## Scope

- introduce a `scrape_reddit_feed` interface beside `search_reddit_browser`;
- route only Reddit `surface_kind=feed` requests to that interface;
- use the existing configured `last30days-facebook` protected profile and the
  shared Agent Browser acquisition module;
- navigate the authenticated Reddit home feed, inspect its rendered DOM, and
  accumulate unique post observations across bounded infinite scrolling;
- canonicalize `/comments/<id>/...` post URLs and preserve legitimate posts
  without topical relevance filtering;
- deterministically exclude Reddit-labeled promoted advertisements and posts
  explicitly marked by Reddit as spam or removed by platform filters;
- classify malformed links, missing timestamps, and unsupported DOM shapes as
  scraper limitations in diagnostics rather than as off-topic content;
- retain date-window enforcement as collection scope rather than quality
  scoring;
- add focused public-interface and worker-routing regressions, then validate,
  package, install, and run one bounded live acceptance campaign.

## Non-Goals

- enabling Reddit in any recurring schedule;
- replacing, weakening, or removing Reddit topic search;
- semantic relevance, ranking, GraphRAG, or subjective quality filtering;
- creating or replacing browser profiles, changing credentials, or inspecting
  unrelated tabs;
- provider writes, votes, comments, subscriptions, or other Reddit mutations;
- changing X, LinkedIn, Facebook, or YouTube acquisition behavior.

## Acceptance Criteria

1. A Reddit feed request reaches `scrape_reddit_feed`; a Reddit topic request
   continues through the existing access-order search path.
2. The public feed interface navigates a verified Reddit home-feed URL and
   returns structurally normalized posts with unique canonical Reddit
   permalinks.
3. Feed acceptance has no topic-overlap gate. It rejects only explicit ads or
   platform-marked spam as content-quality decisions; structural and date
   failures remain separately diagnosed.
4. Infinite-scroll collection deduplicates observations across virtualized DOM
   snapshots, stops after reaching 80 accepted unique posts or a deterministic
   stagnation/scroll/deadline bound, and reports yield and rejection counters.
5. Existing Reddit search regressions remain green and retain their search
   relevance semantics.
6. The full relevant source, worker, contract, packaging, and release suites
   pass; the install artifact is reproducible and the installed service is
   ready on its expected schema.
7. One live campaign uses no more than three Reddit acquisition attempts and
   proves 80 unique canonical posts, or terminates with a typed receipt that
   identifies the exact remaining scraper/provider limitation.
8. After live proof, active work, provider attempts, browser resource leases,
   and database integrity reconcile cleanly; `daily-default` still has Reddit
   disabled.

## Execution Packets

### Packet A | Feed Interface Tracer Bullet

- add one failing public-interface test for a real unrelated Reddit home-feed
  post and make it pass without touching search behavior;
- terminal condition: feed navigation and one canonical item work through the
  new interface.

### Packet B | Deterministic Infinite Scroll And Exclusions

- add one behavior test at a time for cross-snapshot dedupe, promoted/platform
  spam exclusion, structural limitation diagnostics, stagnation, and the
  80-item bound;
- terminal condition: focused Reddit tests pass and search remains unchanged.

### Packet C | Service Routing And Release Candidate

- route Reddit feed work at the acquisition seam, update consumer-facing
  configuration documentation only if a knob changes, run focused then broad
  validation, and build/install the next patch release;
- terminal condition: exact installed runtime identity is ready and matches
  the validated source artifact.

### Packet D | Bounded Live Proof

- inspect only the Reddit surface in the existing configured profile, run at
  most three attempts for one 80-item feed campaign, and reconcile durable
  receipts and cleanup;
- terminal condition: 80 unique canonical posts are proven or a typed terminal
  blocker is recorded without enabling the timer.

## Ownership And Bounds

- critical-path owner: primary Codex agent;
- parallel work: none; current orchestration policy prohibits delegation;
- owned code surfaces:
  `skills/last30days/scripts/lib/reddit_browser.py`,
  `skills/last30days/scripts/lib/service_acquisition_worker.py`, and their
  focused tests;
- owned authority surfaces: this plan, P23 in `ROADMAP.md`, the chronological
  `RUNBOOK.md` entry, and the P23 active-lane registration;
- live bounds: one exact profile, one provider, 80 requested items, three total
  acquisition attempts, no schedule enablement, no provider mutation;
- review bound: one primary review and one closed-world remediation pass for
  accepted blocking findings;
- stop conditions: acceptance met, operator authentication is genuinely
  required, the exact profile cannot be safely acquired, or remaining work
  would expand beyond Reddit feed retrieval.

## Definition Of Done

The installed service can retrieve 80 unique canonical posts from the Reddit
home feed within the approved bounds, retains Reddit search, truthfully records
ads/spam and scraper limitations, leaves the recurring Reddit lane disabled,
and publishes source, test, install, live-receipt, cleanup, and plan/runbook
evidence.

### Checkpoint P0063-C01 | 2026-09-02

Plan version: 1

State: `authorized_plan_opened`

Progress classification: `acceptance_progress`

Authority classification:

- `scope_expansion`; the operator approved the proposed feed interface,
  existing configured profile, deterministic exclusions, 80-item live proof,
  and three-attempt bound.

Evidence:

- current source and CodeGraph show Reddit has only a topic-search browser path,
  while X and LinkedIn already route `surface_kind=feed` to dedicated methods;
- exact Graphiti episodes confirm prior Reddit work proved relevance semantics
  and healthy-zero execution, not successful content retrieval;
- branch `feat/reddit-home-feed` is isolated at base `f5a191a` so the still-open
  P08 scheduled-tick gate remains unchanged.

Subagent status: `not_spawned`.

Graphiti write status: `pending`; defer the required compact write until the
first validated implementation checkpoint rather than storing plan-only churn.

Next action: execute Packet A with one red/green public-interface test for an
unrelated legitimate home-feed post and its canonical permalink.
