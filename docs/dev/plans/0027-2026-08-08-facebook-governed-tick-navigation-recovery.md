# Plan 0027 | Facebook Governed Tick Navigation Recovery

State: CLOSED
Roadmap: P11
Plan version: 4
Date: 2026-08-08
Completed: 2026-08-08
Predecessor: Plan 0026 version 12/checkpoint P0026-C12

## Objective

Make the installed Facebook adapter complete through the normal governed manual
tick path when authentication is explicit but the selected retained target
freezes during query navigation.

## Current State

- service 0.3.20/schema16 is installed ready and correctly avoids false login,
  checkpoint, and CAPTCHA notices;
- explicit manual tick `tick-848f61b8a22d7e603c7e473c16ba5fdf`
  completed `complete_degraded` with seven items, five bounded attempts, 14
  requests, 66 wall seconds, zero cost, zero model tokens, a promoted snapshot,
  zero incidents, and zero notifications;
- Facebook auth inspection skipped two frozen retained targets, selected one
  responsive target, and proved authentication in 500 ms;
- query navigation job `r198316` then failed after 25.787 seconds with the
  page-operation timeout. The queue released normally and later tab, eval, and
  LinkedIn navigation jobs succeeded;
- retained browser PID 96078 and all eight tabs remain live. No browser or tab
  was opened or closed by the manual tick.
- service 0.3.21 implements and deterministically validates a one-shot fresh
  blank-target recovery after authenticated query navigation times out;
- successor manual tick `tick-1acdcedb61adbc45e900e1913feb6d12`
  stopped earlier: all six retained Facebook targets timed out during bounded
  auth selection, so the new navigation branch was not exercised. The tick
  remained zero-cost with no incident or notification, and later LinkedIn jobs
  proved the queue healthy.
- service 0.3.22 then recovered the all-frozen auth boundary on manual tick
  `tick-cbeb2ff5277c5c95e1445cb265ed2974`: it opened one fresh same-browser
  blank target, navigated to Facebook, proved auth, and completed the search
  navigation. The first post-navigation page-state evaluation then timed out
  after 20 seconds, localizing a distinct readback blocker after both recovery
  branches succeeded.
- service 0.3.23 replays the whole search open/read attempt once when that
  initial page-state evaluation times out. Final manual tick
  `tick-771c7a87e4a65636047b83b478a0bd0e` exercised the retained-tab fallback,
  fresh auth, search navigation, page-state readback, extraction, and scrolling
  without a browser failure; it observed 18 candidates and truthfully rejected
  all 18 under the unchanged post-quality gate.

## Scope

- add a bounded navigation/readback recovery path for a target that freezes
  after explicit authentication;
- preserve typed auth/checkpoint handling, the retained exact profile, bounded
  command deadlines, zero-cost posture, and durable browser-operation evidence;
- prove the successor with one explicit manual governed tick rather than
  waiting for a natural schedule boundary.

## Non-Goals

- no automated login, MFA, CAPTCHA, checkpoint, or credential handling;
- no blind retry without a code or runtime-state change;
- no retained-tab cleanup, browser restart, duplicate profile, schedule change,
  provider expansion, paid/model use, or notification test message;
- no formal release, tag, upstream pull request, or unrelated repository
  cleanup.

## Acceptance Criteria

1. A navigation timeout after explicit authentication cannot become an auth or
   checkpoint incident.
2. Recovery is bounded, preserves the retained browser/profile, and either
   reaches verified query-page readback or returns the exact typed navigation
   blocker.
3. The following agent-browser command is not delayed by abandoned navigation
   work.
4. Focused and complete validation, immutable service build/install, patch and
   plan-authority checks pass.
5. One distinct manual governed tick completes with truthful Facebook lane
   evidence, zero cost/model use, no false human incident, and no retained-tab
   closure.

## Execution Bounds

- one completed red navigation-recovery contract, one completed red
  all-frozen-auth recovery contract, and one red post-navigation page-state
  readback recovery contract;
- one focused rework per distinct manual-gate blocker, with no rework or retry
  for a repeated unchanged signature;
- one immutable service successor per validated implementation;
- one additional distinct manual tick after each revised preflight and installed
  readback; no natural-time wait and no same-build retry;
- hard stop on a real login/checkpoint, browser ownership drift, nonzero cost,
  notification misroute, or repeated same-signature navigation failure.

## Owned Write Surfaces

- `skills/last30days/scripts/lib/facebook.py` and focused tests;
- exact service version/runtime manifest and changelog if implementation lands;
- `ROADMAP.md`, `RUNBOOK.md`, and this plan.

### Checkpoint P0027-C01 | 2026-08-08

Plan version: 1

State transition:

- `plan0026_direct_adapter_proof -> governed_manual_tick_navigation_blocker`.

Progress classification:

- `validated_learning`; the explicit manual gate rejected a premature claim
  that direct adapter proof alone established governed-tick reliability.

Validation evidence:

- preflight predicted the exact manual tick, five provider lanes, aggregate
  zero-cost limits, and trigger `manual` before state creation;
- the durable tick and provider result localize Facebook to an authenticated
  retained target followed by one failed `open` operation, while the queue and
  remaining browser-backed lane stayed healthy;
- provider outcome is `agent_browser_error/transient`, not auth, checkpoint, or
  CAPTCHA, and no incident or notification was created.

Subagent status and reconciliation:

- none; the primary owns the tightly coupled adapter/runtime path.

Authority classification:

- `inherited_authority`; the operator explicitly required manual proof now and
  forbade waiting for natural time.

Graphiti write status:

- not written; the repository plan, roadmap, runbook, durable tick, and browser
  job records are the current source-backed authorities for this bounded
  blocker.

Next action:

- commit and push the completed false-auth and timeout repair with this exact
  blocker preserved; derive the red navigation-recovery contract before any
  additional Facebook or all-source manual tick.

### Checkpoint P0027-C02 | 2026-08-08

Plan version: 2

State transition:

- `governed_manual_tick_navigation_blocker -> all_retained_auth_targets_frozen`.

Progress classification:

- `validated_learning`; service 0.3.21 passed deterministic navigation recovery
  but the governed path stopped before that branch because every retained
  Facebook candidate timed out under its three-second selection bound.

Validation evidence:

- preflight predicted manual tick
  `tick-1acdcedb61adbc45e900e1913feb6d12` with the same five-attempt,
  zero-cost limits before state creation;
- the terminal tick consumed five attempts, 14 requests, seven items, 54 wall
  seconds, zero cost, and zero model tokens, with no incident or notification;
- Facebook jobs `r760955`, `r156957`, `r517648`, `r857166`, `r234245`, and
  `r598928` each timed out during bounded retained-tab selection; later
  agent-browser jobs succeeded and retained PID 96078 stayed ready.

Subagent status and reconciliation:

- none; the primary owns the tightly coupled adapter and installed runtime.

Authority classification:

- `inherited_authority`; the operator directed that proof remain manual until
  proven and explicitly rejected waiting for natural time.

Graphiti write status:

- not written; the durable tick, agent-browser jobs, this revised plan, and the
  runbook are the source-backed authorities.

Next action:

- make one fresh same-browser blank target the bounded fallback when every
  retained Facebook target is frozen, validate and install an immutable
  successor, then run one new preflight-predicted manual tick.

### Checkpoint P0027-C03 | 2026-08-08

Plan version: 3

State transition:

- `all_retained_auth_targets_frozen -> post_navigation_page_state_timeout`.

Progress classification:

- `blocker_reduction` and `validated_learning`; service 0.3.22 proved the
  all-frozen auth fallback and the earlier search-navigation recovery in the
  governed path, then exposed one later timeout during initial query-page
  readback.

Validation evidence:

- preflight predicted exact manual tick
  `tick-cbeb2ff5277c5c95e1445cb265ed2974` with five attempts, 250 requests, 15
  items, 600 wall seconds, zero cost, and zero model tokens before state
  creation;
- the terminal tick is `complete_degraded`, promoted snapshot
  `tick-snapshot-8bde63166b410549d08f2f038219e090`, consumed five attempts,
  14 requests, seven items, 97 wall seconds, zero cost, and zero model tokens,
  and created no incident or notification;
- Facebook jobs `r756681`, `r129271`, `r509980`, `r888911`, `r269181`, and
  `r655841` timed out on retained-tab selection; fresh-target jobs `r7190`,
  `r547496`, `r677397`, and `r176339` then opened the target, navigated to
  Facebook, proved auth, and completed search navigation before page-state job
  `r202055` timed out after 20 seconds;
- retained browser PID 96078 remained live and later LinkedIn jobs succeeded.

Subagent status and reconciliation:

- none; the primary owns the tightly coupled adapter and installed runtime.

Authority classification:

- `inherited_authority`; the operator directed that ticks remain manual until
  proven and explicitly forbade waiting for natural time. The next packet is a
  code-changed successor, not a same-build retry.

Graphiti write status:

- not written; the durable tick, agent-browser job records, plan, roadmap, and
  runbook remain the source-backed authorities for this blocker.

Next action:

- replay the whole search open-and-read attempt exactly once on a fresh target
  when the first page-state evaluation times out, validate and install an
  immutable successor, then run one distinct preflight-predicted manual tick.

### Checkpoint P0027-C04 | 2026-08-08

Plan version: 4

State transition:

- `post_navigation_page_state_timeout -> browser_recovery_proven_quality_policy_terminal`.

Progress classification:

- `outcome_progress`; the governed path now completes every browser operation
  through candidate extraction. The remaining Facebook lane failure is the
  existing deterministic content-quality policy, not an auth, checkpoint,
  CAPTCHA, navigation, readback, queue, or browser failure.

Validation evidence:

- deterministic red/green coverage proves one-shot navigation, all-frozen auth,
  and post-navigation page-state recovery plus repeated-timeout and non-timeout
  terminal guards;
- the complete Python suite exits zero with 2,589 passing tests, seven skips,
  and six passing subtests; focused Facebook, release, runtime-package, plan-
  authority, deterministic build, and patch checks pass;
- service artifact 0.3.23 SHA-256 is
  `a121a458dcf44f0fbb975eccaf5763984e88de586bc8a37ee7f0655452e0390e`;
  installed service 0.3.23/schema16 is ready with runtime-manifest SHA-256
  `f1ba57fc8e2405ea96a280d70915860ab7932a8cc21ed521ee5c30b02a6d4173`;
- no-state preflight predicted exact manual tick
  `tick-771c7a87e4a65636047b83b478a0bd0e` with five attempts, 250 requests, 15
  items, 600 wall seconds, zero cost, and zero model tokens;
- the terminal tick promoted snapshot
  `tick-snapshot-cc7a22ba47a2654e1758a435bb7b5600`, consumed five attempts,
  14 requests, seven items, 103 wall seconds, zero cost, and zero model tokens,
  and created no incident or notification;
- Facebook attempt `provider-attempt-1b41ffe16ab6105b377de4fe9c4ec471`
  observed 18 candidates and rejected all 18 as
  `quality_gate_failed/policy`; its bounded browser-operation receipt contains
  only successful operations after the expected frozen retained-tab probes;
- retained browser PID 96078 remained live and ready. No browser was restarted
  or closed, no retained tab was closed, and later LinkedIn collection
  succeeded.

Subagent status and reconciliation:

- none; the primary implemented and independently verified the serialized
  adapter/runtime path.

Authority classification:

- `inherited_authority`; all proof ticks were explicit manual packets under the
  operator's standing instruction, and no natural-time wait or same-build retry
  was used.

Graphiti write status:

- not written; the durable ticks, agent-browser jobs, this terminal plan,
  roadmap, runbook, artifact, and installed-runtime readbacks are the compact
  source-backed authorities.

Next action:

- stop manual proof ticks. Preserve the unchanged quality gate; treat any
  future quality-yield tuning as a separate product packet rather than a
  browser-recovery retry.

## Definition Of Done

- all acceptance criteria have current commit-bound and installed-runtime
  evidence;
- P11, this plan, and the latest runbook agree;
- exact remote commit and installed artifact identities are recorded;
- no unrelated worktree artifacts are included.
