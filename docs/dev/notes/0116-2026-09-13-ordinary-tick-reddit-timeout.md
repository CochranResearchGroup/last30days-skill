# Note 0116 | Ordinary Tick Receipt And Reddit Timeout Diagnosis

Date: 2026-09-13
Scope: Last30days only

## Ordinary receipt

Timer tick `tick-2a466080dc3c23c429ad788c88757ea4` covers
`2026-09-12T00:00:00Z` through `2026-09-13T00:00:00Z` and terminalized
`complete_degraded` at `2026-09-13T00:16:28.816519Z`.

- YouTube succeeded on ordinal 0: 8 observed, 3 accepted.
- X succeeded on ordinal 0: 193 observed, 80 accepted, 322 budgeted seconds.
- LinkedIn succeeded on ordinal 0: 1,611 observed, 47 accepted, 309 budgeted
  seconds.
- Reddit home feed exhausted its lane on ordinal 0: zero observed, zero
  accepted, transient `worker_timeout`, and 360 budgeted seconds. Exact
  provider attempt:
  `provider-attempt-149c5c51b5db6afd3ad451278a1cb25b`.

The Reddit attempt ran from `2026-09-13T00:10:41.143792Z` through
`2026-09-13T00:16:28.229229Z`. Its worker was terminated before it returned a
structured provider result, so `failure_stage`, `failure_reason_code`, and
`browser_operations` are absent.

Post-run readback shows `daily-default` enabled and ready for
`2026-09-14T00:00:00Z`, with this tick as its last boundary receipt and no
runtime error. Active ticks, execution attempts, provider attempts, and open
resource leases are all zero; SQLite `quick_check` is `ok`.

## Agent Browser correlation

Installed Agent Browser reports version 0.28.0. Its retained 200-job window has
no job in the exact Reddit interval. A trace filtered to service `last30days`,
agent `reddit-scraper`, task `reddit-home-feed`, and the September 13 boundary
returns no contexts, jobs, events, or incidents. The append-only failure journal
contains no matching failure during the Reddit provider interval.

This is an evidence gap, not proof that Agent Browser was healthy or at fault.
The nearest matching retained Last30days failure is a prior September 12
`evaluate` job timeout; it does not identify the September 13 stalled action.

## Diagnosis

`service_worker.py` enforces the provider's 360-second outer subprocess
deadline and maps termination to `worker_timeout`. Inside that subprocess,
`RedditBrowserScraper.feed()` may perform acquisition, authentication,
navigation, repeated evaluation, as many as 40 scroll cycles, and cleanup.
Each browser command is bounded, but Reddit never calls the shared
`begin_run_budget()` / `end_run_budget()` lifecycle. The adapter already caps
such cumulative work at 105 seconds when activated.

Therefore the accepted blocker is a Last30days deadline-layering defect: the
outer worker can kill a long Reddit browser sequence before the adapter returns
typed diagnostics. The exact stalled browser operation remains unknown.

Plan 0071 owns the provider-free repair. No tick, provider refresh, browser
launch, profile mutation, or schedule change is authorized by this note.
