# Plan 0062 | Recurring X And LinkedIn 80-Item Volume

State: OPEN
Roadmap: P08
Plan version: 6
Date: 2026-09-02
Branch: `fix/tick-restart-recovery`
Target: `main`

## Objective

Update the existing `daily-default` timer to request 80 unique canonical X
home-feed posts and 80 unique canonical LinkedIn home-feed posts on every tick,
with enough installed scroll and wall-time budget to make those limits real.

## Current State

- the timer requests 80 X and 80 LinkedIn items with three attempts per source;
- Reddit and Facebook are disabled, while YouTube remains enabled for 3 items;
- the installed X scraper permits 40 explicit feed scrolls;
- a bounded 36-scroll X canary accepted 80/80, and LinkedIn accepted 80/80 in
  289.453 seconds after 29 scrolls;
- `daily-default` is ready for `2026-09-03T00:00:00Z` and no tick or provider
  attempt is active;
- the one operator-authorized manual 80+80 tick is terminal failed before page
  observation: two X attempts stopped at the reviewed stale-session identity
  gate, then schema 16 rejected retry ordinal 2 and prevented LinkedIn from
  starting;
- schema 17 is installed and the September 2 ordinary tick durably recorded
  all three attempts for both social providers, but every acquisition failed
  before observation because protected profile capability was absent;
- service 0.3.96 and MCP 4.0.4 are installed. The existing `last30days`
  principal grant is active, its capability remains in an owner-only 0600 file,
  and the service reads it without exposing the secret;
- manual tick `tick-2fa1622b2c62fbd54a9880e456dbcbb9` is terminal complete
  with 80 distinct canonical X URLs and 80 distinct canonical LinkedIn URLs.
  The recurring schedule remains ready for `2026-09-03T00:00:00Z`.

## Scope

- raise X and LinkedIn provider item limits from 10 to 80;
- retain three attempts for X and LinkedIn and existing source enablement;
- raise X's finite explicit-feed allowance to the two-posts-per-scroll 80-item
  bound;
- raise X and LinkedIn provider wall-time budgets to 360 seconds and update the
  aggregate item and wall-time budgets consistently;
- build, validate, and install one version-distinct service artifact;
- rebind only the paused `daily-default` row from the old exact config digest to
  the new validated digest while preserving its next boundary;
- observe the next ordinary scheduled tick under the resulting configuration.
- migrate schema 16 to 17 so the configured third attempt can be recorded
  without losing provider attempt or result receipts.

## Non-Goals

- manually triggering more than one X-and-LinkedIn-only acceptance tick;
- changing Reddit, Facebook, or YouTube enablement or selectors;
- changing the authenticated browser profile, content acceptance rules,
  deterministic ad/spam filtering, or retry count;
- operating or repairing Agent Browser lifecycle state.

## Acceptance Criteria

1. Saved configuration reads back X `items=80`, LinkedIn `items=80`, both with
   `attempts=3` and `wall_seconds=360`.
2. Aggregate limits admit all enabled work: 7 attempts, 163 items, 350 network
   requests, and 2,280 wall seconds.
3. Installed X explicit-feed policy permits 40 scrolls and a deterministic
   two-new-posts-per-scroll fixture reaches 80 unique items.
4. Service 0.3.96/schema 17 and MCP 4.0.4 are installed, ready, compatible, and
   bound to their exact runtime and contract manifests.
5. `daily-default` remains enabled and ready at the unchanged September 2
   boundary under the new exact config digest, with no tick admitted by the
   configuration/rebind operation.
6. The next ordinary tick has terminal provider receipts for X, LinkedIn, and
   YouTube, after which active attempts and leases return to zero and SQLite
   `quick_check` passes.

## Definition Of Done

The timer, installed service, and schedule read back acceptance criteria 1
through 5 without admitting a manual tick, and the next ordinary scheduled
tick subsequently satisfies acceptance criterion 6 or records one exact
external blocker.

## Execution Packets

### P0062-A | Deterministic capacity and configuration change

- owner: primary agent;
- write surfaces: X feed bound, focused regression, service release identity,
  owner-private tick config, Plan 0061/0062, P08 roadmap state, and runbook;
- terminal condition: acceptance criteria 1 through 5 have current readback.

### P0062-B | Ordinary scheduled-tick observation

- owner: primary agent;
- write surfaces: Plan 0062, P08 roadmap state, and append-only runbook only;
- dependency: P0062-A accepted and the September 2 boundary reached;
- terminal condition: acceptance criterion 6 has a durable readback or one
  exact external blocker is recorded.

### P0062-C | Operator-requested immediate acceptance tick

- owner: primary agent;
- input: one manual service tick scoped to already-enabled X and LinkedIn;
- bounds: saved 80-item limits, three attempts per source, no YouTube, Reddit,
  or Facebook lane, and no second manually enqueued tick;
- terminal condition: the one tick reaches a durable terminal receipt and its
  X/LinkedIn yields, attempts, exclusions, budgets, schedule continuity, and
  active-work cleanup are reconciled.

### P0062-D | Three-attempt persistence repair

- owner: primary agent;
- write surfaces: provider-attempt schema migration, migration and real-tick
  regressions, service/MCP compatibility identities, Plan 0062, P08, and the
  append-only runbook;
- dependency: Agent Browser terminal replacement parity is source-validated
  and must be installed before another live acceptance tick;
- terminal condition: schema 17 preserves a v16 provider result, admits retry
  ordinal 2, rejects ordinal 3, and the version-distinct service artifact is
  installed ready without changing saved tick configuration.

## Bounds And Stops

- one release build/installation transaction and one exact schedule rebind;
- no manual tick enqueue or provider attempt during P0062-A;
- no more than the already-configured three attempts per X or LinkedIn lane;
- preserve the exact `last30days-facebook` profile and all deterministic
  exclusions;
- stop if the schedule row, prior digest, next boundary, or active-work census
  differs from the pre-mutation readback.

### Checkpoint P0062-C01 | 2026-09-01

Plan version: 1

State: `implementation_active`

Progress classification: `outcome_progress`

Authority classification:

- `inherited_authority`; the operator directed the recurring timer to collect
  80 unique X and 80 unique LinkedIn posts.

Evidence:

- live service 0.3.91 is ready and compatible on schema 16;
- the current saved timer requests 10/10 with 120-second provider ceilings;
- Plan 0059's live canary proved X 80 at 36 scrolls and LinkedIn 80 in 289.453
  seconds, while the installed 32-scroll X pass stopped at 78 without
  stagnation.

Subagent status: `not_spawned`

Graphiti write status: `not_written`; current repository and runtime evidence
are sufficient.

Next action: validate and install the bounded capacity change, save the 80+80
configuration, then perform the exact guarded schedule rebind without
admitting a tick.

### Checkpoint P0062-C02 | 2026-09-01

Plan version: 1

State: `configured_and_installed_awaiting_ordinary_tick`

Progress classification: `outcome_progress`

Authority classification:

- `inherited_authority`; installation and the guarded schedule rebind are
  ordinary implementation steps for the operator's recurring 80+80 request.

Evidence:

- complete canonical `uv run pytest -q` and focused X/runtime/release suites
  pass; plan-authority, active planning, and goal-governance audits pass;
- commit `80eec3d` is published at `origin/fix/tick-restart-recovery`;
- service 0.3.92 is installed, active, ready, and MCP-compatible on schema 16
  with runtime-manifest SHA-256
  `68f57446667df4f9d105b80c63a48e215b625ea6a94fc79eee81d2d0c2ae901b`;
- saved revision `operator-20260901-x-linkedin-80-v1` reads back X 80/3/360,
  LinkedIn 80/3/360, YouTube 3/1/120, and aggregate limits 163/7/2,280;
- with the service stopped and active attempts and leases proven zero, one
  exact guarded update moved only `daily-default` from digest
  `sha256:b2ec0ed2eecc7d0e1fa1b6fa97595bf6fbfeb51d44db9f99d4a5884986856c3e`
  to validated digest
  `sha256:069cf238586388e1e55924083e97161a403dd7fa488a6c2cf45d55fb29500074`;
- backup
  `/home/ecochran76/.local/share/last30days/backups/research-pre-80x80-rebind-20260901.db`
  and the live database both pass `quick_check`;
- `daily-default` remains enabled and ready at the unchanged boundary
  `2026-09-02T00:00:00Z`, retains prior tick
  `tick-56318fada747d408976df141ab17a0ef`, and reports no runtime error;
- the database still contains 111 ticks with the latest created on the prior
  September 1 boundary. The update admitted no manual or timer tick, and active
  tick attempts, provider attempts, and open resource leases remain zero.

Subagent status: `not_spawned`

Graphiti write status: `not_written`; the plan, runbook, published commit, and
live readbacks are durable and authoritative.

Next action: at the September 2 UTC boundary, observe the first ordinary tick
under the 80+80 configuration and reconcile its X, LinkedIn, and YouTube
terminal receipts without manually enqueueing work.

### Checkpoint P0062-C03 | 2026-09-01

Plan version: 2

State: `manual_80x80_acceptance_tick_authorized`

Progress classification: `planned_followup`

Authority classification:

- `inherited_authority`; the operator's `try it` instruction explicitly
  authorizes one immediate live test of the newly configured X and LinkedIn
  limits.

Evidence:

- service 0.3.92 remains ready and compatible at the installed runtime
  manifest;
- the saved config and schedule remain ready at the validated 80+80 digest;
- the service MCP collection projection is empty, so the existing native
  service tick operation remains the governed execution surface.

Subagent status: `not_spawned`

Graphiti write status: `not_written`; current repository and live service
evidence are sufficient.

Next action: enqueue exactly one manual tick scoped to X and LinkedIn, poll
only that tick to terminal state, then reconcile its provider receipts and
schedule invariants.

### Checkpoint P0062-C04 | 2026-09-01

Plan version: 2

State: `manual_tick_failed_before_scraping`

Progress classification: `blocker_reduction`

Authority classification:

- `inherited_authority`; this checkpoint reconciles the single immediate tick
  authorized at C03 and does not enqueue another tick.

Evidence:

- manual tick `tick-8a7c84f0337e04e6b90aa02068dd0383` reached terminal
  `failed` with execution error `integrityerror` after 1.161 seconds;
- X retry ordinals 0 and 1 each returned transient zero-observation
  `agent_browser_error` at `workspace_acquisition`, reason
  `existing_session_profile_identity_unproven`, with failure signature
  `sha256:a489884adfd2a0f6f6d1247c8a3d924910ca0fcb65fe8c9d8f68d11ce58563ef`;
- the installed service environment does not set the reviewed recovery switch
  `LAST30DAYS_AGENT_BROWSER_ALLOW_DUPLICATE_PROFILE_LANE`, so neither X
  attempt took the exact-profile fresh-session path;
- the saved provider limit admits three attempts, but schema 16 constrains
  `service_tick_provider_attempts.retry_ordinal` to `IN (0, 1)`. Inserting
  retry ordinal 2 raised the recorded SQLite integrity error and aborted lane
  iteration before the LinkedIn provider was attempted;
- the tick consumed two attempts, two network requests, two wall seconds, and
  zero items. It published no snapshot or head and left zero active tick
  attempts, active provider attempts, or open resource leases;
- `daily-default` remains ready for `2026-09-02T00:00:00Z` at unchanged digest
  `sha256:069cf238586388e1e55924083e97161a403dd7fa488a6c2cf45d55fb29500074`
  and still references its prior scheduled tick. Live SQLite `quick_check` is
  `ok`.

Subagent status: `not_spawned`

Graphiti write status: `not_written`; the repository plan and direct live
database readbacks are sufficient.

Next action: repair the schema/config contract for three provider attempts and
durably enable the already-reviewed exact-profile fresh-session recovery path;
then obtain authority for a new manual tick or observe the ordinary September
2 tick. No second manual tick is authorized by this plan version.

### Checkpoint P0062-C05 | 2026-09-01

Plan version: 3

State: `schema_repair_source_validated`

Progress classification: `blocker_reduction`

Authority classification:

- `inherited_authority`; the operator authorized the diagnosed repairs,
  testing, merge, installation, and one bounded post-install acceptance tick.

Evidence:

- the real tick regression was red after provider calls at retry ordinals 0
  and 1 and is green through ordinals 0, 1, and 2 after schema 17;
- the migration regression was red at schema 16 and is green after rebuilding
  only `service_tick_provider_attempts`, preserving a referenced provider
  result, admitting ordinal 2, rejecting ordinal 3, and returning an empty
  `PRAGMA foreign_key_check`;
- service 0.3.93, schema 17, and MCP 4.0.4 identities are aligned across the
  canonical contract catalog, generated Go constants, compatibility release
  lock, runtime manifest, and install/rollback fixtures;
- complete `uv run pytest -q` and `go test ./...` pass; `git diff --check`
  passes. Ruff is not installed in the declared uv environment and was not
  added as an undeclared dependency;
- source checkpoint `646ef5b88f7874978641db5ab9cfc3ac6dbd5cf2` is published
  at `origin/fix/tick-restart-recovery`.

Subagent status: `not_spawned`

Graphiti write status: `not_written`; current source, tests, plan, and direct
runtime diagnosis remain authoritative.

Next action: publish this source checkpoint, qualify and install the exact
Agent Browser candidate first, then build and install service 0.3.93 and run
one bounded X-and-LinkedIn acceptance tick after a zero-active-work preflight.

### Checkpoint P0062-C06 | 2026-09-01

Plan version: 4

State: `profile_capability_client_installed`

Progress classification: `blocker_reduction`

Authority classification:

- `inherited_authority` for source plumbing, tests, and installation; capability
  registration, private configuration mutation, and another provider tick are
  explicitly withheld pending operator authorization.

Evidence:

- service 0.3.93/schema 17 and Agent Browser truthful planning are installed;
  the consumed successor tick proved retry ordinals zero through two for both X
  and LinkedIn, then failed every browser acquisition because Last30days passed
  no `profileCapability`;
- Last30days 0.3.94 source accepts one absolute private capability-file path,
  opens it with no-follow semantics, requires a same-user regular file with no
  group/other permission bits, bounds and validates its content, and emits only
  the safe `profile_capability_unavailable` failure when invalid;
- when configured, the client calls Agent Browser MCP `service_access_plan` and
  `service_request` with the capability added only to ephemeral argument copies.
  The raw value is absent from CLI argv, the retained request route, command
  timings, stable `agent-browser.json`, logs, receipts, and service state;
- the capability-specific red tests failed before implementation and pass after
  it. The complete Agent Browser-runtime, X, Facebook, and LinkedIn test slice
  passes with the historical X presentation constraints preserved;
- the complete Python suite has one reproducible baseline-only teardown timeout
  in `test_real_service_mcp_discovery_query_refresh_and_poll`; the exact same
  test fails on unchanged `origin/main`, while the changed focused suites pass.
- the broad Python run excluding that baseline integration file exits zero; all
  MCP Go packages, Python compilation, generated-manifest validation, plan
  authority, and `git diff --check` pass;
- live first-call `service_info` exposed a retained adapter 4.0.3 process whose
  schema ceiling is 16 against ready service 0.3.93/schema 17. Source adapter
  4.0.4 is already aligned and must be reinstalled before service acceptance.
- commit `51ae5c9` was merged to main by `96400a4`; MCP adapter 4.0.4 was
  installed with binary SHA-256
  `6e8d0886d0d9e8988af5e3cade3a5d7e88cea086d37801e93d135bfb95cf6d14`;
- merged-main service artifact SHA-256
  `57dfd8b5966224c4853a191db9cb293973b40bcb543e29718e7f6fe4a5b14f1b`
  installed as 0.3.94. Diagnose reports ready/schema 17/runtime manifest
  `882612c588752cefc41c94e011359927148437a3ee8765853fb0460a29deaf2e`,
  and installed capability-client source matches merged source;
- a fresh MCP process reports `compatible`, adapter 4.0.4, service 0.3.94, and
  schema range 17..17. This conversation's retained connector stayed on 4.0.3;
  targeted termination closed only that process, but the host returned
  `Transport closed` instead of hot-restarting. This client must reconnect;
- the owner-private environment still has no capability-file setting. No
  capability was registered or read, and no provider tick was invoked.

Subagent status: `not_spawned`.

Graphiti write status: `not_written`; repository source, tests, and this
checkpoint are the current durable authority.

Next action: reconnect the Codex client, then request explicit authority for
capability registration and owner-private environment wiring. A further
provider tick remains separately authorized.

### Checkpoint P0062-C07 | 2026-09-02

Plan version: 5

State: `profile_capability_configured_tick_ready`

Progress classification: `blocker_reduction`

Authority classification:

- `inherited_authority`; the operator explicitly authorized registration and
  private capability wiring followed by one 80+80 tick.

Evidence:

- the checkout fast-forwarded cleanly to merged main commit `cfb1da0`, which
  contains service 0.3.94's authenticated Agent Browser client and the schema
  17 retry repair;
- Agent Browser reported one existing active grant for principal `last30days`
  and profile `last30days-facebook`, with rotation allowed and no blockers;
- the missing local capability was recovered by rotating that same grant, not
  by creating a duplicate principal. The prior capability is revoked, the new
  grant is active and bound to the current owner, and the replacement file is
  an owner-owned 0600 regular file under the owner-private Last30days config;
- the owner-private environment now points
  `LAST30DAYS_AGENT_BROWSER_PROFILE_CAPABILITY_FILE` at that file and retains
  the reviewed exact-profile fresh-lane recovery flag. The raw capability was
  not printed, persisted in repository state, or placed in command arguments;
- Last30days restarted active and reports service 0.3.94/schema 17 ready with
  runtime manifest
  `882612c588752cefc41c94e011359927148437a3ee8765853fb0460a29deaf2e`;
- `daily-default` remains ready for `2026-09-03T00:00:00Z` at unchanged digest
  `sha256:069cf238586388e1e55924083e97161a403dd7fa488a6c2cf45d55fb29500074`;
  active tick attempts, provider attempts, and leases are zero and SQLite
  `quick_check` is `ok`.

Subagent status: `not_spawned`.

Graphiti write status: `pending`; this durable security and runtime transition
will be written after the bounded acceptance result is known.

Next action: preflight and enqueue exactly one X-and-LinkedIn-only 80+80 tick,
poll only its returned ID to terminal state, and reconcile yield, exclusions,
budgets, schedule continuity, and active-work cleanup.

### Checkpoint P0062-C08 | 2026-09-02

Plan version: 5

State: `manual_tick_environment_bypass_identified`

Progress classification: `blocker_reduction`

Authority classification:

- `inherited_authority`; this checkpoint reconciles the one C07-authorized
  tick and does not enqueue another.

Evidence:

- manual tick `tick-94d0476e65170ad5df114b6d47e0790f` completed degraded
  after exactly three attempts for each social provider, with zero observations
  and zero accepted items;
- Agent Browser retained six matching `remote_view_open` jobs, all failed with
  `existing_session_profile_identity_unproven`. X attempts share signature
  `sha256:d7fe9f118c424ddcd83cea8b5319d2801c304787296f2918ecf10b435003e2b6`;
  LinkedIn attempts share
  `sha256:0fe41b74f0da779e4111d8c89977ba9367b507145c748d553eb5c208a08cd087`;
- source trace proves `service.py tick enqueue` assembles and executes its tick
  in the invoking CLI process. The acquisition subprocess copies that parent
  environment and only adds `PYTHONPATH`; it does not read the systemd unit's
  `EnvironmentFile`;
- the invoking shell contained neither
  `LAST30DAYS_AGENT_BROWSER_PROFILE_CAPABILITY_FILE` nor
  `LAST30DAYS_AGENT_BROWSER_ALLOW_DUPLICATE_PROFILE_LANE`. Consequently this
  manual command bypassed the configured protected path and repeated the old
  unauthenticated acquisition route. This result does not test the newly
  configured capability;
- direct `/proc` readback of the restarted managed Last30days process confirms
  it has both the capability-file path and reviewed fresh-lane flag. The next
  ordinary timer tick will inherit them;
- all six tick resource leases are released, active tick/provider attempts and
  open leases are zero, live SQLite `quick_check` is `ok`, and `daily-default`
  remains ready for `2026-09-03T00:00:00Z` at its unchanged saved digest and
  prior timer receipt.

Subagent status: `not_spawned`.

Graphiti write status: `graphiti_write_pending`; provider readiness passed and
exact duplicate checks found no episode, but the initial 300-second job and one
compact 600-second retry both failed with `TimeoutError` before creating an
episode. Do not queue a third write from this checkpoint.

Next action: either observe the September 3 ordinary service-owned tick, which
will inherit the configured capability, or obtain authority for one corrected
manual tick whose parent process explicitly receives the same two non-secret
environment values. Do not enqueue another manual tick under C07 authority.

### Checkpoint P0062-C09 | 2026-09-02

Plan version: 6

State: `manual_80x80_accepted`

Progress classification: `acceptance_progress`

Authority classification:

- `inherited_authority`; the operator required proof, authorized forced lease
  acquisition for this sole-user profile, and retained the existing 80+80
  three-attempt bounds.

Evidence:

- failed corrected tick `tick-3d5abd0280cf89e33acae1fde772fc81`
  proved the capability itself was valid, then isolated a Last30days routing
  defect: the reviewed duplicate-profile lane replaced Agent Browser's fresh
  broker session with the stale fixed session name;
- service 0.3.95 preserved the broker session. Its bounded successor
  `tick-01d8786958e774376069a5134d673fc2` moved past identity selection but
  exposed a separate cold-launch failure at CDP port 37747;
- a forced exact-profile launch returned a false identity error after it had
  actually committed PID 84749 and a reachable CDP browser. Capability-bound
  rejoin of exact lease `profile-lease-v1:fc553beb74ded8415f61dbf1` removed all
  identity blockers without broad cleanup or profile replacement;
- direct LinkedIn acquisition then succeeded while X still failed. The final
  Last30days defect was X feed's `constrain_presentation=True`, which discarded
  the reusable authenticated route despite the presentation-neutral social
  acquisition contract. The regression failed before removing that flag and
  passed afterward;
- published commits `c672b84` and `7b3b082` contain the two fixes. Installed
  service 0.3.96 is ready on schema 17 with runtime manifest
  `a147cdf7e8e88d15cf7a324570940b7b27f7834063674beda0136a22a34ade1c`;
- final tick `tick-2fa1622b2c62fbd54a9880e456dbcbb9` completed with both
  lanes successful. X accepted 80 after one transient ambiguous-auth attempt,
  observing 255 and deterministically rejecting 173 duplicate statuses plus
  two over-limit items. LinkedIn accepted 80 on attempt zero, observing 1,775
  and rejecting 1,354 duplicates plus 341 sponsored ads;
- the durable source projection contains exactly 80 X and 80 LinkedIn versions,
  80 distinct canonical URLs per service, and zero missing URLs. The tick used
  three of six attempts, 100 of 100 network requests, and 386 of 720 wall
  seconds, then promoted its head with all collection, media, OCR, lexical,
  semantic, and sidecar stages successful;
- active ticks, nonterminal provider attempts, and open tick leases returned to
  zero; SQLite `quick_check` is `ok`. `daily-default` remains enabled and ready
  for `2026-09-03T00:00:00Z` with its prior automatic tick identity unchanged;
- the exact protected browser lease is active with no identity blockers and was
  renewed through `2026-09-03T01:00:00Z`, covering the next scheduled run.

Subagent status: `not_spawned`.

Graphiti write status: `not_written`; two prior bounded writes timed out, and
the published repository plus durable tick receipt are the current authority.

Next action: observe the September 3 ordinary timer tick under the now-proven
80+80 configuration; do not infer that manual acceptance alone closes the
recurring-scheduler acceptance criterion.
