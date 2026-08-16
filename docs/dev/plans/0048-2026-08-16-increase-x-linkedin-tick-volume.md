# Plan 0048 | Increase X And LinkedIn Tick Volume

State: CLOSED
Roadmap: P08
Plan version: 1
Date: 2026-08-16

## Objective

Increase the useful recurring volume available from X and LinkedIn at each
ordinary daily tick while preserving the accepted scheduler, standard-depth
collection, zero-cost posture, existing evidence, and the operator's temporary
Reddit/Facebook pause.

## Scope And Non-Goals

- raise the X provider's accepted-item ceiling from three to ten;
- replace LinkedIn's one-record company-profile lane with the existing
  topic/content adapter and give it an accepted-item ceiling of ten;
- keep the LinkedIn topic at `OpenAI`, preserve all previously collected
  company-profile evidence, and keep YouTube at three items;
- keep `daily-default`, its 86,400-second interval, UTC anchor, last boundary,
  next boundary, attempt/request/wall ceilings, zero cost/model limits,
  notification routes, credentials, browser profile, and standard depth;
- do not enqueue a tick, re-enable Reddit or Facebook, use deep mode, change
  installed code, or promise that a source will always expose ten usable
  records.

## Acceptance Criteria

1. X and LinkedIn source-scoped no-state preflights are ready with one lane and
   an accepted-item ceiling of ten each.
2. The enabled-source preflight is ready with exactly YouTube, X, and LinkedIn
   and an aggregate accepted-item ceiling of 23.
3. LinkedIn uses `linkedin_agent_browser` against the `OpenAI` topic rather
   than the single company-profile adapter.
4. The existing schedule remains enabled/ready for the same next UTC boundary
   with no added tick, attempt, or schedule event; service and SQLite remain
   healthy and a recoverable pre-change database backup exists.

### Checkpoint P0048-C01 | 2026-08-16

State transition:

- `reddit_facebook_temporarily_disabled -> higher_volume_x_linkedin_schedule`.

Progress classification:

- `outcome_progress`; the requested recurring capacity is installed and live
  without consuming a transition tick.

Validation evidence:

- owner-private revision is
  `operator-20260816-increase-x-linkedin-volume-v1`; exact target readback is
  Reddit false, YouTube true, X true, Facebook false, LinkedIn true;
- X uses `x_agent_browser` at ten items; LinkedIn uses
  `linkedin_agent_browser` at ten items against topic `OpenAI`; both remain at
  standard depth, one attempt, 50 requests, 120 wall seconds, zero cost, and
  zero model tokens;
- X-only and LinkedIn-only no-state preflights are each `ready` with one lane
  and ten items. The enabled-source preflight is `ready` with three lanes and
  aggregate limits of five attempts, 250 requests, 23 items, 600 wall seconds,
  zero cost, and zero model tokens;
- full-config digest is
  `sha256:209dcf64968394b1327a93d31309a51fd3ebbb5ddebbfe2f5235e1dbc39e619e`;
  the durable `daily-default` row is bound to that exact digest;
- service is active/ready at 0.3.47/schema 16; schedule remains ready for
  `2026-08-17T00:00:00Z` with no runtime error and unchanged last tick;
  timer ticks remain 11, total provider attempts remain 139, active attempts
  remain zero, schedule events remain 23, and SQLite quick check is `ok`;
- backup
  `/home/ecochran76/.local/share/last30days/backups/research-pre-volume-increase-20260816.db`
  passes SQLite quick check and is owner-private.

Authority classification:

- `inherited_authority`; the operator explicitly requested higher recurring X
  and LinkedIn volume. The provider change is the minimum required to let the
  LinkedIn lane return more than the profile adapter's single record.

Graphiti write status:

- not attempted because no Graphiti write interface is available in this
  runtime; this plan, the runbook, private config, schedule row, and live
  readbacks are authoritative.

Next action or stop reason:

- stop. Let the next ordinary boundary exercise the higher ceilings. Treat ten
  as a ceiling, not a guaranteed yield, and assess observed/accepted counts
  from the resulting durable receipt.
