# Plan 0066 | Full Tick Recovery

State: CLOSED
Lane: P26
Branch: fix/full-tick-recovery
Target: fix/installed-service-command
Integration: fast-forward
Plan version: 1
Date: 2026-09-06

## Objective

Repair and retry until one complete all-enabled-source tick succeeds, using at
most five full attempts and waiting at least 300 seconds after terminalization
before starting the next attempt. This is the operator's explicit goal.

## Current State

Service 0.3.113 is installed and ready. Attempt 4 completed all four enabled
lanes and promoted its snapshot, retaining 187 items. Four of five authorized
attempts were used; each retry gap exceeded 300 seconds. The original config
is byte-identical to its pre-campaign backup. Full acceptance is met.

## Scope

One primary owner, serialized work, no delegated agents. Repair admission,
LinkedIn deadline/result handling, and exact-profile Reddit acquisition only as
current evidence requires. Retain the four enabled sources, target selectors,
item ceilings, pacing, privacy, source quality, and aggregate cost limits.
Build/test/install each repair before its bounded live attempt.

## Definition Of Done

A durable terminal `complete` tick with all four enabled lanes successful,
retained evidence and promoted snapshot, healthy post-run service/schedule, and
no abandoned active work. Source changes tested, committed, published, and
installed. Verify every attempt against the durable ledger and 300-second gap.
No weakening acceptance to terminal failure or `complete_degraded`.

## Non-Goals

No unrelated browser/profile cleanup, auth bypass, extra source scope, increased
cost ceilings, weakened scraping pacing, or more than five full tick attempts.
If all five fail, retain the goal as unmet with exact remaining blocker.

## Execution Control

`docs/dev/notes/0066-full-tick-attempts.json` is the attempt ledger. Reserve an
ordinal before enqueue, retain tick identity/process handle, then record the
terminal receipt and next eligible UTC time. No blind retries of an observed
running tick. Checkpoint after each repair/install/attempt cycle. Inherit this
ledger across continuations. Repair work may use the five-minute cooldown.

### Checkpoint P0066-C01 | 2026-09-06

Plan version: 1

- Current authority: five new full attempts, minimum five-minute gaps.
- State: diagnosed -> repair; zero attempts consumed.
- Prior diagnostic turn: outcome_progress (reproduced zero-budget crash).
- Next: fix budget admission and preserve LinkedIn output before worker timeout.

Authority classification:

- `inherited_authority`

### Checkpoint P0066-C02 | 2026-09-06

Plan version: 1

- State: installed 0.3.111 -> attempt 1 complete_degraded -> browser ownership repaired.
- Progress: blocker_reduction. Tick tick-7881125257dc8a17ec8aed3ae2715a5d retained three YouTube items; browser lanes failed acquisition. No full success yet.
- Trace: X and LinkedIn existing_session_profile_identity_inconsistent. The correct live profile retained PID 50967 and owner generation 79, but registered principal binding was stale.
- Broker recovery/reconcile plans offered no replacement transition. The advertised capability-authenticated lease rejoin succeeded at 21:27:11Z; lease fc553beb74ded8415f61dbf1 is active with zero blocking identity axes, generation 79 unchanged. No browser terminated or profile changed.
- Attempt 2 earliest 21:27:44.292699Z; retain original config and managed environment.
- Tests: focused tick runner/runtime, LinkedIn, acquisition worker and release version suites passed before install. Source commit a1bb7b2.
- Authority classification: `inherited_authority`.

### Checkpoint P0066-C03 | 2026-09-06

Plan version: 1

- State: attempt 2 complete_degraded -> client repair installed 0.3.112.
- Progress: blocker_reduction. The authenticated lease rejoin removed identity mismatch; legacy allowDuplicateProfileLane=true still forced a conflicting launch against live PID 50967.
- A bounded unmodified broker-request probe reused the exact browser and released its own tab successfully. Client repair d857d83 suppresses the cold-launch override when a compatible live browser exists.
- Existing retained-reuse regression test failed before repair and passes afterward. Focused runtime/acquisition tests passed; version test initially detected pending manifest refresh, then all five version tests passed after refresh.
- Installed manifest ada044f8f20786c098a3b3799d9feb2dfe735601e590c249ddc4eb00289e54e1, readiness 21:31:56Z. LinkedIn and Reddit blank-tab acquisition/release probes through the repaired client both succeeded on the original profile/session.
- No full tick success yet. Attempt 3 earliest 21:34:07.690217Z; unchanged source limits and config digest.
- Authority classification: `inherited_authority`.

### Checkpoint P0066-C04 | 2026-09-06

Plan version: 1

- State: attempt 3 complete_degraded -> Reddit request repair installed 0.3.113.
- Progress: outcome_progress. Attempt 3 retained 80 X, 33 LinkedIn and 3 YouTube items. LinkedIn completed within its worker budget; Reddit alone failed acquisition.
- Exact MCP ingress failure: invalid_bounded_recipe, tab_new cannot execute remote-view route intent. The actual Reddit configuration adds routePoolEntryId=guacamole-rdp-b to an existing-browser tab request; the earlier generic blank probe omitted that configuration.
- Repair 9aa8f83 omits cold-launch route hints for compatible retained browsers. Regression failed before repair. Updated stale test that required the invalid request; runtime, Reddit, acquisition and release-version focused suites then passed.
- Installed 0.3.113 readiness at 21:43:41Z, manifest f556daae3796c8be6b94f04e5a8dc3eb0603ae79a0a6e0c3ed5882e46fec979b. Installed actual-config Reddit acquisition/auth probe succeeded: authenticated true; login form, checkpoint and network block false. Exact probe tab released.
- Attempt 4 earliest 21:45:59.547017Z. Original config digest and caps preserved; no complete tick yet.
- Authority classification: `inherited_authority`.

### Checkpoint P0066-C05 | 2026-09-06

Plan version: 1

- State: attempt 4 complete -> P26 CLOSED; progress: outcome_progress.
- Tick tick-eb2d052248583ae432599ce037ae349c completed at 21:54:48Z; all four lanes success. Retained YouTube 3, X 80, LinkedIn 33, Reddit home-feed 71; total 187, reported cost zero.
- Snapshot tick-snapshot-0193a2ffb2e35999f86a98b1439317fb promoted; lexical/semantic indexes succeeded. All stages terminal success or valid empty; no failed stage.
- Service 0.3.113 ready and systemd active. Zero nonterminal ticks and zero unreleased tick resource leases. Daily-default remains enabled/ready with next boundary 2026-09-07T00:00:00Z; its previous scheduled degraded result is historical and was not rewritten by this manual run.
- All four attempts bind unchanged config digest 8e3811d5e9b561cfd3f97b3d9897770ee4c623fe9e74a443bc01d86fca4d3449. Exact config bytes match pre-campaign backup. Retry gaps: 321.043353, 313.552340, 317.392909 seconds.
- Source repair commits a1bb7b2, d857d83, 9aa8f83 validated and installed. Build/install continues to refresh the frozen skill service command inherited from Plan 0065.
- Durable sanitized receipts: docs/dev/notes/0066-full-tick-attempts.json. Raw provider receipts stay private under the installed diagnostics/plan0066 directory.
- Graphiti compact repair write job d557aa24-24ec-4244-93a1-394c2c419e98 failed with TimeoutError; no episode persistence claimed. Repo artifacts are authoritative.
- Authority classification: `inherited_authority`. Goal complete; no fifth attempt.

Closeout audit: Plan 0066 has no new findings. The repository-wide planning audit still reports the two pre-existing Plan 0064 issues (invalid authority classification and missing Definition Of Done). These are outside this recovery slice.
