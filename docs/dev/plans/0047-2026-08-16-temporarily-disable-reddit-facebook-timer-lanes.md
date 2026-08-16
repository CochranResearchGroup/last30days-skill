# Plan 0047 | Temporarily Disable Reddit And Facebook Timer Lanes

State: CLOSED
Roadmap: P08
Plan version: 1
Date: 2026-08-16

## Objective

Honor the operator's request to stop recurring Reddit and Facebook acquisition
while preserving the accepted service-owned daily cadence, YouTube/X/LinkedIn
lanes, zero-cost posture, durable boundary continuity, and fail-closed schedule
binding.

## Scope And Non-Goals

- change only the owner-private tick revision and the `enabled` flags for the
  existing Reddit and Facebook targets;
- keep `daily-default`, its 86,400-second interval, UTC anchor, last boundary,
  next boundary, and prior tick receipt unchanged;
- do not enqueue a tick, change a provider, browser, credential, selector,
  ceiling, notification route, source code, or installed release;
- re-enablement is a later explicit operator action.

## Acceptance Criteria

1. The private config enables exactly YouTube, X, and LinkedIn and disables
   exactly Reddit and Facebook.
2. A no-state preflight produces exactly three lanes; source-scoped Reddit and
   Facebook preflights fail closed because no enabled target exists.
3. The existing schedule remains enabled/ready for the same next UTC boundary
   with no runtime error and no added tick, attempt, or schedule event.
4. Service 0.3.47/schema 16 and SQLite remain ready/healthy, and a recoverable
   pre-change database backup exists.

### Checkpoint P0047-C01 | 2026-08-16

State transition:

- `five_source_daily_schedule -> reddit_facebook_temporarily_disabled`.

Progress classification:

- `outcome_progress`; the operator-requested source reduction is installed and
  live without changing cadence or admitting work.

Validation evidence:

- owner-private revision is
  `operator-20260816-disable-reddit-facebook-v1`; exact target readback is
  Reddit false, YouTube true, X true, Facebook false, LinkedIn true;
- full-config digest is
  `sha256:aaefca9f2aaa73faf78c703918fbad819096dcaffb711aea32d14e86cf4cb3af`;
  the durable `daily-default` row is bound to that exact digest;
- enabled-source preflight is `ready` with three lanes and narrowed aggregate
  limits of three attempts, 150 requests, nine items, 360 wall seconds, zero
  cost, and zero model tokens;
- Reddit-only and Facebook-only preflights both fail with
  `manual service selector has no enabled target`;
- service is active/ready at 0.3.47/schema 16; schedule remains ready for
  `2026-08-17T00:00:00Z` with no runtime error; timer ticks remain 11, total
  provider attempts remain 139, active attempts remain zero, schedule events
  remain 23, and SQLite quick check is `ok`;
- backup
  `/home/ecochran76/.local/share/last30days/backups/research-pre-source-disable-20260816.db`
  passes SQLite quick check and is owner-private.

Authority classification:

- `inherited_authority`; the operator explicitly requested disabling these two
  recurring sources. No broader source, cadence, cost, browser, or publication
  action was inferred.

Graphiti write status:

- not attempted because no Graphiti write interface is available in this
  runtime; this plan, the runbook, private config, schedule row, and live
  readbacks are authoritative.

Next action or stop reason:

- stop. Let the next ordinary boundary run only YouTube, X, and LinkedIn.
  Re-enable Reddit or Facebook only after an explicit operator request.
