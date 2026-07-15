# Plan 0001 | Agent-Browser Facebook Scraper

State: COMPLETE
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
- verified Recent Posts filtering with a deterministic filtered-URL fallback
- action-card extraction with semantic-card fallback and post-only classification
- canonical permalink recovery from direct and media URLs, including username and numeric-profile posts
- accessibility timestamp merging with bounded retries for asynchronous Comet rendering
- timestamp parsing, date-window filtering, text cleanup, relevance gating, and rejection diagnostics
- bounded local waits while retaining agent-browser for every browser interaction
- sanitized debug artifacts without cookies, operator URLs, raw HTML, or page text
- logged-out, authenticated-home, checkpoint, no-results, mixed-card, and date fixtures
- configuration, skill, onboarding, and installed artifact coverage

Automated evidence:

- focused Facebook/pipeline/security tests pass
- full Python suite: `2045 passed, 5 skipped, 6 subtests passed`
- skill artifact build and package-boundary test pass
- installed `facebook.py` SHA-256 matches the working tree
- installed-copy Facebook-only dogfood accepted two current posts
- opt-in three-query `FacebookLiveSmokeTests` passes

Live evidence:

- agent-browser doctor reports both RDP route desktops ready on displays `:10` and `:11`
- retained profile/session `last30days-facebook` is authenticated and operator-visible
- three unrelated queries reused browser `session:last30days-facebook`
- `regenerative agriculture farming soil health`: two accepted posts, zero rejections
- `AI agents`: one accepted post with a canonical numeric-profile permalink
- `robotic lawn mower`: two accepted posts, zero rejections

Still required: None.

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
