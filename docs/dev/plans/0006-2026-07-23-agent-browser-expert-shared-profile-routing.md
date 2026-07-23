# Plan 0006 | Agent-browser expert shared-profile routing

State: CLOSED
Date: 2026-07-23

## Scope

Make the last30days fork consume agent-browser's access-plan and shared-profile
acquisition contract for authenticated browser sources. Record stable,
non-secret agent-browser target configuration at the last30days user scope
without persisting runtime browser, session, route, display, or tab leases as
configuration.

## Current State

Current live evidence:

- agent-browser selects the durable `last30days-facebook` profile for both X
  and Facebook by target identity;
- the access plan recommends `shared_browser_tabs`, `tab_new`, and the retained
  owner route hints `browserId=session:last30days-facebook` and
  `sessionName=last30days-facebook`;
- X can reuse the retained owner after service discovery converges;
- Facebook rejects a configured session/profile mismatch before consulting the
  broker-selected owner;
- Facebook loads `LAST30DAYS_FACEBOOK_BROWSER_ID` but does not use the hint
  during acquisition;
- static route and display hints can bind a new request to a lease owned by an
  unrelated session.

The authenticated profiles are healthy. The remaining failure is caller-side
acquisition and configuration handling.

## Design

Add one shared agent-browser integration module that:

1. parses the broker-selected profile and profile-reuse decision;
2. resolves a compatible retained browser owner from current service state;
3. treats the access-plan `browserId` and `sessionName` as runtime route hints,
   not durable configuration;
4. records stable target configuration under
   `~/.config/last30days/agent-browser.json`, or the directory selected by
   `LAST30DAYS_CONFIG_DIR`;
5. writes the user file atomically with mode `0600`;
6. excludes cookies, credentials, operator URLs, browser IDs, session names,
   route IDs, display allocations, tabs, and page data.

The durable target record may contain:

- selected profile ID;
- profile origin and class;
- selected browser build and host;
- view-stream and control-input providers;
- display-isolation posture;
- profile process and client-sharing policies;
- default acquisition mode.

X and Facebook must query access-plan by target identity on every acquisition.
The current access plan remains authoritative over the recorded user file.

## Implementation Slices

1. Add failing tests for user-scoped configuration recording and exclusion of
   ephemeral route hints.
2. Add failing adapter tests for broker-selected shared-owner reuse when the
   caller's configured session is unrelated.
3. Implement the shared parser, recorder, and retained-owner resolver.
4. Move X and Facebook acquisition onto the shared contract.
5. Update `SKILL.md` and `CONFIGURATION.md`.
6. Run focused tests, the broader browser-source regression set, package
   validation, installed-skill synchronization, and live X/Facebook smokes.

## Acceptance Criteria

- X and Facebook resolve `last30days-facebook` through target-identity access
  planning.
- A configured session owned by another profile does not block reuse of the
  broker-selected compatible browser.
- Shared acquisition uses the retained owner browser and session instead of
  starting a duplicate profile process.
- Static route or display hints cannot override the access-plan shared owner.
- The user-scoped JSON file records stable, non-secret target configuration.
- The user-scoped JSON file contains no runtime browser, session, route,
  display, tab, operator URL, cookie, or credential data.
- File writes are atomic and mode `0600`.
- Existing environment variables remain supported as explicit acceptance or
  launch constraints.
- Focused X, Facebook, environment, pipeline, and security tests pass.
- Live X and Facebook smokes reuse the authenticated profile without profile
  or display-owner mismatch.

## Non-Goals

- persisting cookies or credential values;
- copying agent-browser's service state into last30days;
- making runtime leases durable;
- bypassing login, checkpoint, CAPTCHA, or rate-limit states;
- modifying agent-browser itself.

## Definition Of Done

The plan closes when implementation, documentation, focused tests, package
validation, installed-copy synchronization, and live X/Facebook smokes pass,
and the recorded user-scoped configuration contains only the approved stable
fields.

## Completion Evidence

Closed on 2026-07-23.

- Implementation commit: `e4ffdb1 feat: share agent-browser profiles through
  access plans`.
- Focused agent-browser, Facebook, X, YouTube, environment, pipeline, security,
  and source-log tests passed.
- The full `uv run pytest -q` suite passed.
- Python compilation and `git diff --check` passed. Ruff was not available in
  the project environment.
- `dev/last30days/scripts/build-skill.sh` built
  `dist/last30days.skill` with 103 files at 452 KiB.
- The installed `~/.agents/skills/last30days` copies of `SKILL.md`,
  `agent_browser_config.py`, `facebook.py`, `x_browser.py`, and
  `youtube_yt.py` are byte-for-byte identical to the repository copies.
- An installed-copy X smoke completed in 78.4 seconds with six X posts and no
  acquisition or profile-owner error.
- A live Facebook smoke reused `session:last30days-facebook`, reported
  authenticated, and navigated to the exact query URL. It produced no emitted
  posts because all five candidates failed content quality gates
  (`missing_permalink`, `off_topic`, or `missing_date`), not because browser
  acquisition or authentication failed.
- `~/.config/last30days/agent-browser.json` records X and Facebook against the
  durable `last30days-facebook` profile with `shared_browser_tabs` and
  `tab_new`; YouTube records its separate `stealthcdp-default` profile.
- The user file is mode `0600`. A recursive key audit found no cookie, token,
  secret, credential, user-data path, operator URL, browser ID, session name,
  route ID, display ID, or tab ID fields.

## Follow-up

The engine's source-quality message can still say `Missing: X/Twitter` after a
successful X result set. That reporting inconsistency is outside this
shared-profile routing plan and should be handled as a separate quality-status
fix.
