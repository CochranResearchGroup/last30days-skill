# Plan 0001 | Agent-Browser Facebook Scraper

State: OPEN
Date: 2026-07-15

## Scope

Implement the agent-browser-centered Facebook search design while preserving
the existing `search_facebook(...)` pipeline seam. Facebook remains explicit
opt-in and read-only.

## Current State

Implemented and verified in the working tree:

- typed agent-browser workspace, auth, page, candidate, diagnostic, and failure contracts
- current service-state acquisition with stale route hints demoted below live state
- retained browser reuse and profile mismatch rejection
- accessible Search Facebook navigation with verified new-tab fallback
- exact final URL and query readback before extraction
- scoped candidate extraction and post-only classification
- canonical permalink cleanup, timestamp parsing, date-window filtering, text cleanup, relevance gating, and rejection diagnostics
- sanitized debug artifacts without cookies, operator URLs, raw HTML, or page text
- logged-out, authenticated-home, checkpoint, no-results, mixed-card, and date fixtures
- configuration, skill, onboarding, and installed artifact coverage

Automated evidence:

- focused Facebook/pipeline/security tests pass
- full Python suite: `2035 passed, 5 skipped, 6 subtests passed`
- skill artifact build and package-boundary test pass

Still required:

- restore live agent-browser RDP route desktops; current doctor reports missing
  X11 sockets for both route users and the scraper correctly returns
  `route_stale`
- authenticate the retained Facebook profile after remote-view recovery
- pass the three-query live smoke in one retained browser
- reinstall the working tree and pass an installed-copy Facebook-only dogfood run

## Non-Goals

- bypass Facebook checkpoints, CAPTCHAs, restrictions, or rate limits
- mutate Facebook data
- persist credentials, cookie values, private feed text, or raw authenticated HTML
- silently fall back to broad home-feed extraction

## Definition Of Done

- three unrelated queries reach distinct query-specific Facebook search pages
- consecutive queries reuse one retained profile without route drift
- every emitted item has a canonical post permalink, author, meaningful text,
  and an in-range publication date
- non-post cards, ads, stories, comments, recommendations, and home-feed fallbacks emit zero items
- focused, full-suite, build, install, and live-smoke gates pass
- implementation is committed and pushed to the CochranResearchGroup fork
