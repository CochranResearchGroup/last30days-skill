# Plan 0002 | Agent-Browser LinkedIn Scraper

State: OPEN
Date: 2026-07-15

## Scope

Add LinkedIn content-post research as an explicit opt-in source backed by an
operator-authenticated, retained agent-browser profile. Preserve the existing
planner, normalization, ranking, rendering, persistence, and watchlist
contracts.

## Implementation

- add a typed LinkedIn scraper with retained profile/session verification
- detect login and security-verification checkpoints without bypassing them
- navigate directly to a query-specific content search sorted by latest date
- verify final host, path, query, sort, and authenticated page state
- extract only scoped post/activity cards and canonical LinkedIn permalinks
- reject ads, people/jobs/company recommendations, comments, undated posts,
  off-topic cards, and out-of-window posts
- emit sanitized diagnostics and optional debug artifacts without cookies,
  operator URLs, raw HTML, or private page text
- wire the source into configuration, diagnosis, planning, normalization,
  ranking, rendering, onboarding, and the slash-command source vocabulary

## Current State

Implemented and verified:

- explicit enablement plus explicit source-request gating
- retained profile/session acquisition with LinkedIn-tab reselection
- login and security-checkpoint detection with sanitized operator handoff
- exact latest-content search URL and query/sort readback
- scoped activity/post extraction, canonical URL handling, relative dates,
  engagement parsing, and strict sponsored/non-post/date/relevance gates
- retained source-tab reuse and same-site duplicate cleanup, preventing social
  query tabs from accumulating or leaving the wrong site selected
- conservative LinkedIn interaction pacing (four-second minimum, six actions
  per rolling minute) with immediate stop on limit/restriction warnings
- sanitized diagnostics and debug artifacts
- planner, pipeline, normalization, ranking, rendering, README, configuration,
  runtime-spec, and onboarding integration
- focused tests and full suite: `2064 passed, 6 skipped, 6 subtests passed`
- distributable skill build and package-boundary test pass

Live evidence:

- agent-browser reused `session:last30days-facebook` and selected the retained
  LinkedIn target
- the real LinkedIn SMS verification page returns `checkpoint_required` and
  the current public operator URL without exposing checkpoint or cookie data
- after operator login, the redesigned authenticated navigation cluster is
  recognized and a one-query smoke reused the existing LinkedIn tab
- the smoke found three semantic post cards and no rate-limit/restriction
  warning; all three remained rejected because the current card DOM exposes no
  canonical post permalink
- same-site cleanup reduced the shared retained browser from five Facebook
  tabs plus LinkedIn to one Facebook tab plus one selected LinkedIn tab

Still required:

- complete the operator-owned LinkedIn security verification
- resolve canonical post permalinks from LinkedIn's current opaque search-card
  DOM without clicking per-card controls or fabricating URLs
- pass three-query live smoke and installed-copy LinkedIn-only dogfood

## Non-Goals

- bypass checkpoints, CAPTCHAs, restrictions, or rate limits
- scrape private messages, connections, invitations, or non-search feeds
- mutate LinkedIn data
- export browser cookies or authenticated page HTML
- run LinkedIn automatically unless explicitly requested and enabled

## Definition Of Done

- focused adapter, pipeline, normalization, rendering, and security tests pass
- three unrelated live queries reuse one retained authenticated browser
- every emitted item has a canonical post/activity permalink, author,
  meaningful text, and an in-range date
- non-post cards and sponsored content emit zero items
- full suite, package build, installed-copy dogfood, commit, and public-fork
  push pass
