# Plan 0050 | LinkedIn Literal-Now Date Repair

State: CLOSED
Roadmap: P08
Plan version: 2
Date: 2026-08-16

## Objective

Retain LinkedIn's visible literal `now` and `just now` timestamps through the
browser extraction fallback, install the repair as service 0.3.48, then run
exactly one fresh X/LinkedIn receipt-only canary and report its realized yield.

## Current State

- Plan 0049 proved X and LinkedIn provider success but rejected six LinkedIn
  candidates as `missing_date`;
- a read-only snapshot of the retained authenticated LinkedIn result page
  showed the first three rejected cards carry visible `now •` timestamps,
  while numeric relative timestamps such as `2m • Edited` were retained;
- the Python date parser already accepts `now` and `just now`, but the browser
  extraction fallback admitted only numeric relative timestamps, so literal
  values were discarded before parsing;
- a Node-backed replay of the production extraction script failed with
  `timestamp == ""` before the repair and passes with `timestamp == "now •"`
  after the one-regex change;
- immutable service 0.3.47 is installed ready with 0.3.46 retained. The
  recurring source configuration and `daily-default` schedule are unchanged.

## Scope

- extend only the LinkedIn plain-text timestamp fallback to retain `now` and
  `just now`, preserving its existing optional bullet suffix;
- keep an executable regression at the production JavaScript extraction seam;
- package and transactionally install service 0.3.48 after all release gates;
- use distinct schedule identity
  `plan-0050-x-linkedin-date-repair-canary` for exactly one X attempt and one
  LinkedIn attempt over a completed interval;
- read back source counts, rejection reasons, stage outcomes, durable records,
  and recurring-schedule invariants before closing.

## Non-Goals

- do not weaken date, relevance, duplicate, or derivative quality gates;
- do not change selectors, navigation, query, profile, source enablement,
  cadence, budgets, retry policy, cost, or model-token limits;
- do not repair LinkedIn semantic-sidecar `analysisoutputmissing`, re-enable
  Reddit/Facebook, or run more than one fresh canary tick.

## Acceptance Criteria

1. The production-script replay is deterministically red before the change and
   green after it; the complete LinkedIn test module also passes.
2. Service 0.3.48 passes authority, full Python, Go, package, and readiness
   gates and installs through the transactional runtime with 0.3.47 retained.
3. The live canary is preflight-bound to exactly X and LinkedIn, is enqueued
   once, and reaches one terminal receipt without retry or fallback.
4. The report distinguishes observed, accepted, and rejected yield and states
   whether literal-now retention reduced `missing_date`; no yield is promised.
5. `daily-default` retains its source configuration, next boundary, and timer
   identity, with SQLite and the installed service healthy after the canary.

## Definition Of Done

- exact service 0.3.48 is pushed, installed, and ready; one fresh two-lane
  canary is terminal; source and schedule receipts are recorded here and in
  the runbook; P08 and this plan close without a second attempt.

### Checkpoint P0050-C01 | 2026-08-16

Plan version: 1

State transition:

- `canary_terminal_complete_degraded -> linkedin_literal_now_repair_validated`.

Progress classification:

- `outcome_progress`; the primary LinkedIn realized-volume limiter from Plan
  0049 is reproduced at the production extraction boundary and repaired under
  deterministic test.

Validation evidence:

- retained-browser snapshot shows three fresh cards with `now •`, followed by
  cards with numeric relative dates that the existing fallback retained;
- the exact production-script regression failed twice before the fix with
  expected `now •` versus actual empty timestamp, then passed after the fix;
- the complete LinkedIn module passes 28 tests with one intentional skip;
- CodeGraph is healthy with no pending sync;
- an accidental invocation of the legacy service helper during diagnosis
  temporarily rendered its working-tree unit. No tick/provider effect ran;
  the transactional 0.3.47 artifact was immediately reinstalled and verified
  ready with managed launcher plus unchanged 0.3.47/0.3.46 links.

Authority classification:

- `inherited_authority`; the operator approved the recommended repair and
  explicitly requested another test and report when done.

Subagent status:

- `not_spawned`; current orchestration policy prohibits delegation.

Next action or stop reason:

- cut and validate service 0.3.48, publish and install the exact artifact,
  preflight one fresh two-lane canary, enqueue it once, and stop at its first
  terminal receipt.

### Checkpoint P0050-C02 | 2026-08-16

Plan version: 2

State transition:

- `linkedin_literal_now_repair_validated -> live_repair_accepted`.

Progress classification:

- `outcome_progress`; installed service 0.3.48 accepted a visible literal-now
  LinkedIn result and eliminated `missing_date` from the fresh canary's
  rejection reasons.

Validation evidence:

- exact pushed candidate `c0131e3` produced runtime artifact SHA-256
  `b2d21c2b077246ce5363bbadd2363fb184a7000f195a53c7132df178e2b3de6f`;
  transactional install reports service 0.3.48/schema 16 ready with runtime
  manifest SHA-256
  `af2cd36a8e4188802de5646c8faf4700bcd9cb41fccec3f5aff9fea95a94720a`
  and 0.3.47 retained;
- authority audit, Go suite, install-readiness suite, skill artifact build,
  focused production-script replay, and complete LinkedIn module pass. The
  pre-live full Python run passed 2,650 tests with seven skips and had one
  governance-only failure because Plans 0046 and 0050 were concurrently open;
- after this plan closed, the terminal authority audit passed with exactly one
  remaining active plan and the clean full Python suite passed 2,651 tests,
  seven skips, and six subtests;
- exact tick `tick-4683d92b8e85ebf68503325d6289a48b` was enqueued once and
  terminalized `complete_degraded` after 124 provider wall seconds, two
  attempts, 12 network requests, seven accepted records, zero cost, and zero
  model tokens;
- X succeeded in 51 seconds: seven observed, four accepted, three rejected;
  reasons are one each `duplicate_status`, `insufficient_text`, and
  `off_topic`;
- LinkedIn succeeded in 73 seconds: ten observed, three accepted, seven
  rejected. `missing_date` is zero; one accepted durable result carries
  visible `now •` and normalized date `2026-08-16`. Rejection reason counts
  are three `duplicate`, four `kind_unknown`, and four `missing_permalink`,
  with some candidates carrying more than one reason;
- seven source versions and a promoted 25-entry snapshot are durable. The tick
  is degraded only because three separate LinkedIn semantic sidecars returned
  `analysisoutputmissing`; collection, media, OCR, lexical/semantic indexing,
  and head promotion succeeded;
- no incident or notification was created. Service 0.3.48 is ready, SQLite
  quick check is `ok`, and active attempts are zero. `daily-default` retains
  digest
  `sha256:209dcf64968394b1327a93d31309a51fd3ebbb5ddebbfe2f5235e1dbc39e619e`,
  prior tick, and next boundary `2026-08-17T00:00:00Z`; timer ticks remain 11
  and schedule events remain 23.

Authority classification:

- `inherited_authority`; this is the one repair and one live retry explicitly
  approved by the operator.

Subagent status and reconciliation:

- `not_spawned`; current orchestration policy prohibits delegation.

Graphiti write status:

- not attempted because no Graphiti write interface is available in this
  runtime; installed receipts, SQLite, this plan, and the runbook are the
  durable authorities.

Next action or stop reason:

- stop without retry. Keep Reddit/Facebook disabled and the X/LinkedIn
  ten-item ceilings. Let the next ordinary boundary run; treat permalink/type
  quality and semantic-sidecar output as separate possible future work.
