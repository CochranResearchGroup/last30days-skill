# Plan 0003 | Agent-Browser X Scraper

State: OPEN
Date: 2026-07-19

## Scope

Add a quality-gated X search routine backed by the authenticated
`last30days-facebook` agent-browser profile. Make the browser lane an explicit
X backend that can be selected without removing the existing Bird, xAI, or
official-X-API fallbacks.

## Current State

Current repo and runtime evidence:

- The production X source still uses Bird with `AUTH_TOKEN` and `CT0`; it does
  not invoke agent-browser.
- Bird authentication works, but a live run needed several failed GraphQL
  attempts before returning six unevenly relevant posts in roughly 76 seconds.
- Agent-browser access planning for `serviceName=last30days` and
  `targetServiceId=x` selects `last30days-facebook` with fresh X readiness.
- A live authenticated browser smoke loaded X search through
  `stealthcdp_chromium`, preserved the signed-in account, and exposed canonical
  status permalinks, ISO timestamps, post text, and engagement controls.
- URL-only access planning does not reliably select the authenticated profile;
  the X target identity is therefore part of the required interface.

Still required:

- a repo-owned X browser module
- pipeline/backend selection and diagnosis wiring
- configuration and Skill runtime-contract documentation
- fixture, adapter, pipeline, security, and opt-in live tests
- installed-skill synchronization and dogfood proof

## Interface And Seam

The external seam is one function:

```python
def search_x_browser(
    topic: str,
    from_date: str,
    to_date: str,
    *,
    depth: str = "default",
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    ...
```

Callers receive normalized candidates plus typed failure and diagnostic
metadata. They do not learn agent-browser command arrays, tab indices, DOM
selectors, profile lease details, or extraction scripts.

The internal browser seam has two adapters:

- a production agent-browser CLI adapter
- an in-memory test adapter that returns reviewed page states and candidates

This keeps browser I/O replaceable while query verification, canonicalization,
date filtering, relevance gating, and diagnostics remain inside one deep
module.

## Browser Acquisition Design

1. Request an agent-browser access plan with caller labels, the X URL, and
   `targetServiceId=x`.
2. Require a selected profile with usable X readiness. During this rollout,
   require the selected profile to match
   `LAST30DAYS_X_BROWSER_PROFILE`, whose default is
   `last30days-facebook`.
3. Reuse the selected profile's retained browser and X tab when available.
4. When no compatible browser exists, open the broker-selected runtime profile
   with the access-plan browser build and headed posture.
5. Consolidate only duplicate `x.com`/`twitter.com` tabs; never close another
   site's tab in the shared profile.
6. Inspect authenticated DOM state without returning cookie values. Stop on
   login, checkpoint, challenge, or restriction pages.

The access plan is authoritative for profile selection. The configured profile
is an acceptance constraint for this rollout, not a substitute for target
identity routing.

## Search-State Design

- Navigate to `https://x.com/search` with a query containing the requested
  topic plus `since:` and `until:` date operators.
- Select the Latest lane with `f=live`.
- Read back the final host, path, decoded `q` parameter, `f` parameter, search
  input value, authenticated navigation, error/challenge state, and article
  count from the same selected tab.
- Require an exact decoded query match and `f=live` before extraction.
- Treat an explicit no-results page as valid empty evidence.
- Treat a home/explore page, Top results, stale query, login page, or generic
  error page as a typed failure and emit zero posts.

## Extraction And Quality Design

Extraction is scoped to X `article` nodes. Each candidate records:

- the primary post's canonical `/handle/status/<numeric-id>` permalink
- author handle derived from that permalink
- visible primary tweet text
- machine-readable `time[datetime]`
- reply, repost, like, bookmark, and view counts when present
- promoted/restriction flags

Quoted-post links and nested media links must not replace the primary status
permalink. Canonicalization strips query strings, analytics paths, media paths,
and tracking fragments.

Every emitted post must have:

- an allowlisted canonical X status permalink
- an author handle
- meaningful text
- an ISO publication date inside the requested range
- non-trivial relevance to the user topic
- no promoted label

When articles exist but all candidates fail, return `quality_gate_failed` with
rejection counts. Never broaden into trends, recommendations, or the home feed.

## Errors

Stable error types:

- `agent_browser_missing`
- `profile_mismatch`
- `route_stale`
- `auth_required`
- `checkpoint_required`
- `rate_limited`
- `navigation_mismatch`
- `search_unavailable`
- `extraction_empty`
- `quality_gate_failed`
- `agent_browser_timeout`
- `agent_browser_error`

Errors and debug artifacts must omit cookie values, raw authenticated HTML,
full page dumps, profile filesystem paths, and operator-route credentials.

## Configuration And Backend Selection

- `LAST30DAYS_X_BROWSER=1` explicitly enables the browser lane.
- `LAST30DAYS_X_BROWSER_PROFILE` defaults to `last30days-facebook` for this
  rollout.
- `LAST30DAYS_X_BACKEND=browser` explicitly selects it.
- When browser mode is enabled and no backend is pinned, prefer browser before
  Bird so the authenticated visible search path is primary.
- Bird, xAI, and xurl remain available as non-browser fallbacks.
- Normal runs must not launch an authenticated browser unless browser mode is
  explicitly enabled or pinned.

## Implementation Slices

Critical path, owned serially by the primary agent:

1. Add one public-interface tracer test for a canonical dated X post, then the
   minimum browser module implementation.
2. Add acquisition/auth/navigation failure tests one at a time and implement
   their gates.
3. Add extraction/quality cases one at a time, including quoted posts,
   promoted posts, malformed URLs, stale dates, and off-topic cards.
4. Wire backend availability, diagnosis, pipeline dispatch, normalization, and
   rendering through observable interface tests.
5. Update configuration, Skill runtime instructions, README, onboarding, and
   package-boundary expectations.
6. Run focused tests, full tests, package build, installed-copy checks, and a
   low-volume three-query live smoke using `last30days-facebook`.

Low-conflict work that can be performed independently after the module
interface stabilizes:

- documentation wording
- sanitized fixture review
- build/install boundary verification

No subagent owns the critical path for this plan.

## Acceptance Criteria

- Access-plan requests include `targetServiceId=x` and select
  `last30days-facebook` in the current live runtime.
- Three unrelated live queries reuse the same profile without profile-lock or
  cross-site-tab damage.
- Each query reaches an exact `f=live` search URL with the requested date
  operators.
- Every emitted item has a canonical numeric X status permalink, handle,
  meaningful text, in-range date, and normalized engagement.
- Quoted posts, promoted content, recommendations, trends, stale posts,
  malformed links, and off-topic cards are rejected.
- Login, challenge, rate-limit, navigation-mismatch, extraction-empty, and
  all-rejected states emit zero posts with typed failures.
- Source logs remain visible in non-TTY hosts.
- Tests and debug artifacts contain no credentials, raw private page HTML, or
  full authenticated page dumps.
- `uv run pytest tests/test_x_browser.py` passes.
- Existing X, Facebook, LinkedIn, pipeline, rendering, and security tests pass.
- `uv run pytest` passes.
- The skill artifact builds and respects the install boundary.
- The installed skill matches the working-tree X browser module and passes an
  X-browser-only dogfood run.

## Definition Of Done

The plan is complete only when implementation, focused and full automated
tests, package validation, installed-copy validation, and the three-query live
smoke all pass, and the final live evidence proves that agent-browser used the
`last30days-facebook` profile selected for X.

## Non-Goals

- posting, liking, reposting, following, messaging, or otherwise mutating X
- bypassing login challenges, CAPTCHAs, restrictions, or rate limits
- exporting or persisting browser cookies
- guaranteeing X will always return matching recent posts
- removing the existing non-browser X backends in this slice
