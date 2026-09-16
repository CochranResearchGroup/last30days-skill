# Plan 0126 | WI-010 X P4 Readiness Probe

State: OPEN
Lane: P53
Work item: WI-010
Branch: feat/wi010-x-p4-readiness-v1
Target: main
Integration: merge
Roadmap: P53
Plan version: 1
Date: 2026-09-15
Execution owner: /root
Coordination owner: /root
Requested model route: host default, no delegation
Effective runtime model: not exposed

## Objective

Use the already-authenticated X profile selected by the current Agent Browser
target binding for one bounded P4 auth-readiness probe, retain a safe and
independently verifiable receipt, and stop before any content search or P5
canary.

## Current State

Plan 0125's provider-free audit is integrated at `8ecf221c` and classifies the
X browser adapter as readiness-capable only with an exact profile. The operator
has now authorized proceeding and explicitly selected the profile already
authenticated for X. Its exact non-secret registered ID has not yet been read
or sealed. No P4 effect has occurred.

## Definition Of Done

The repository contains a tested single-case P4 executor that binds the stable
X target profile to a short-lived grant before dependency resolution, performs
only workspace acquisition plus X auth inspection, releases its attributed tab
handle in `finally`, records a safe source-bound receipt, and independently
verifies the retained result.

## Scope

- read the stable non-secret X target binding from the user-scoped Agent
  Browser configuration;
- reject a missing, fallback-only, ambiguous, secret-like, or mismatched profile;
- seal one `x-browser` P4 plan and matching short-lived grant;
- use the production X Agent Browser client only for acquisition, auth
  inspection, and exact-owner release;
- record safe auth booleans, bounded operation names/statuses, budget use,
  accounting confidence, and teardown outcome;
- publish and integrate the executor before the live probe, then retain the
  probe receipt through the normal PR workflow.

## Non-Goals

No query, timeline extraction, content normalization, yield or quality claim,
P5 canary, retry, alternate profile, manual login, CAPTCHA/checkpoint handling,
credential disclosure, cookie/page-text capture, installed-runtime mutation,
schedule, release, deployment, or tracker mutation.

## Frozen Effect Contract

1. Provider `x`, adapter `x_agent_browser`, case `x-browser`, and the current
   stable X target profile are the only selectable identities.
2. The stable profile ID is read once as non-secret routing metadata and bound
   as an opaque `profile:<id>` reference before the client is constructed.
3. The grant expires within 15 minutes and binds attempt count one, external
   concurrency one, at most four browser actions, three opaque external request
   equivalents, 120 seconds, and zero cost.
4. Dependency/profile-capability resolution occurs only after plan and grant
   verification. Capability material is never emitted or persisted.
5. Execution calls only `acquire_workspace`, `inspect_auth`, and
   `release_workspace`; importing or calling any X search/account/list/feed
   entrypoint is forbidden.
6. Login form, checkpoint, restriction, ambiguous auth, profile/route/lease
   mismatch, timeout, accounting uncertainty beyond the declared opaque bound,
   redaction failure, or teardown failure is terminal. Automatic retry is zero.
7. The receipt may claim only the exact X route/profile was ready at the
   observed time. It cannot claim content availability, provider health, or
   future readiness.

## Invalidation Map

| Stop | Invalidated | Preserved |
|---|---|---|
| plan/grant/profile mismatch before acquisition | P4 sample | sealed safe failure; no provider attempt |
| acquisition or auth failure | readiness verdict | attempt, safe reason, budget and accounting evidence |
| timeout or uncertain effect | retry eligibility and acceptance | first attempt and uncertainty evidence |
| redaction failure | receipt publication | quarantined local failure only |
| teardown failure | lifecycle safety and overall acceptance | auth observation labeled teardown-incomplete |

## Validation

- provider-free unit tests with injected fake clients for success, every auth
  stop state, mismatch, budget, no-search enforcement, tamper detection, and
  teardown on every path;
- focused provider-acceptance and authority suites;
- pre-effect exact plan/grant verification and source digest readback;
- one live attempt only after the executor commit is merged to canonical main;
- post-effect offline receipt verification and fresh runtime census.

## Acceptance Criteria

1. The selected runtime profile exactly equals the stable X target profile.
2. No content-search code path executes.
3. One attempt returns an explicit authenticated/login/checkpoint/restricted/
   ambiguous observation without storing private page data.
4. Exact-owner release completes and the post-run census shows no owned lease
   or attributed tab handle left behind.
5. The receipt verifies independently from canonical source and sealed hashes.

## Stop Rules

Stop before execution if the stable X profile is absent or still resolves only
through an unreviewed fallback; if the source or grant changes after sealing;
if another authenticated provider canary is active; or if exact cleanup cannot
be guaranteed. After invocation, preserve the first outcome and never retry.

## Next Action

Implement and provider-free test the P4 executor. Merge it through a pull
request before resolving and probing the current X profile.

### Checkpoint P0126-C01 | 2026-09-15

Plan version: 1

State transition: `unplanned -> OPEN`.

Progress classification: `outcome_progress`; the operator selected the
existing authenticated X profile and authorized one bounded P4 probe.

Authority classification:

- `human_gate` from `ok go` followed by the explicit direction
  to use the profile already authenticated for X.

Owned changes:

- registered the exact X-only P4 execution contract and retained P5, retries,
  alternate profiles, provider content, and runtime mutation as non-goals.

Validation evidence:

- current canonical `main` was clean and equal to `origin/main` at
  `2d628311940bbe018766198b33fb7957157ec9a4` before lane creation;
- current source requires the broker-selected X profile to equal the requested
  profile, separates auth inspection from search, and releases the attributed
  tab handle without closing the shared browser.

Subagent status and reconciliation:

- `not_spawned`; live-provider execution is serialized and no delegation was
  requested.

Graphiti write status:

- `not_written`; no memory write was authorized.

Next action:

- implement and merge the executor without provider access, then perform the
  single authorized P4 attempt from canonical main.
