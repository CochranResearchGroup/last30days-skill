# Plan 0034 | Facebook Post-Navigation Target Loss Repair

State: CLOSED
Roadmap: P13
Plan version: 3
Date: 2026-08-09
Predecessor: Plan 0033 version 5/checkpoint P0033-C05

## Objective

Build a deterministic regression for the repeated Facebook page-execution and
navigation loss proven by Plan 0033, repair the adapter without weakening its
auth/challenge/rate-limit or browser-ownership gates, and install a bounded
successor. A later live qualification tick is outside this version's authority.

## Current State

- installed 0.3.37/schema16 is service-ready and selects the retained owner;
- three distinct manual ticks reached the retained Facebook browser but ended
  before extraction with two `agent_browser_timeout` results and one
  `facebook_target_unresponsive` result;
- all attempts had zero candidates, quality rejections, page signals,
  auth/challenge/rate-limit evidence, cost, and model use;
- browser PID 63205 is ready after cleanup with four live tabs and one
  Facebook home target.

## Scope

- replay the exact operation sequences from the three Plan 0033 provider
  receipts at the smallest correct adapter seam;
- distinguish target loss during evaluation from target loss during a later
  open, and preserve the typed failing stage;
- repair cumulative timeout/navigation behavior with bounded replacement and
  exact same-site cleanup;
- validate, release, install, and re-read the current runtime without a live
  provider tick.

## Non-Goals

- no fourth Facebook tick, schedule change, browser close, logout/login, MFA,
  CAPTCHA/checkpoint interaction, rate-limit generation, provider fallback,
  cost/model use, or content dump;
- no weakening of exact owner/profile/target or auth/challenge safety gates.

## Acceptance Criteria

1. One deterministic red regression reproduces each terminal operation shape:
   successful retained-owner reuse followed by an unresponsive evaluation, and
   successful replacement evaluation followed by a timed-out later open.
2. The repair returns accepted extraction input or one exact typed terminal
   result within the 120-second parent wall while leaving one Facebook target.
3. Focused and canonical suites, release reproducibility, installed manifests,
   doctors, databases, schedule, browser, tab, challenge, and queue readbacks
   pass.
4. No effect-bearing Facebook tick occurs; a later proof requires a separately
   recorded operator attempt ceiling.

## Definition Of Done

- criteria 1-4 have deterministic test, artifact, installed-runtime, and
  current browser-state evidence;
- the plan, roadmap, runbook, and bounded repair receipt agree on whether the
  successor is installed and whether a later live proof remains gated;
- no live Facebook attempt is consumed by this offline repair plan.

## Execution Bounds

- primary agent owns one offline diagnosis/repair/install packet;
- one regression/red-green cycle and one closed-world validation cycle;
- hard stop on missing deterministic seam, browser/profile mutation need,
  safety-gate weakening, or any proposed live provider effect.

## Owned Write Surfaces

- Facebook adapter tests and the minimum source/runtime packaging surfaces;
- this plan, `ROADMAP.md`, `RUNBOOK.md`, and one later repair receipt.

### Checkpoint P0034-C01 | 2026-08-09

Plan version: 1

State transition:

- `terminal_typed_blocker -> offline_repair_ready`.

Progress classification:

- `outcome_progress`; three live receipts narrow the failure to a repeatable
  post-navigation target execution/open seam.

Subagent status and reconciliation:

- none; the next packet remains serialized with the primary.

Authority classification:

- `inherited_authority` for offline diagnosis, repair, validation, release,
  and installation only; `human_gate` for any later live Facebook tick.

Next action:

- create the red-capable deterministic regression from the three provider
  operation sequences before reading or changing adapter implementation.

### Checkpoint P0034-C02 | 2026-08-09

Plan version: 2

State transition:

- `offline_repair_ready -> deterministic_red_proven`.

Evidence:

- the retained-owner/evaluation-loss regression exhausted its remaining three
  seconds while the legacy blank-target replacement was still starting;
- the replacement-auth/later-open regression reproduced the installed trace's
  four-second remainder and failed the later query open;
- both regressions failed before implementation with the expected
  `facebook_target_unresponsive`/`agent_browser_timeout` shapes.

Decision:

- bound navigation page-state evaluation separately from extraction;
- open a recovery successor directly at its intended Facebook URL and defer
  predecessor consolidation to the existing guaranteed same-site cleanup;
- remove the redundant post-`open` local wait because `agent-browser open`
  already owns page-load waiting.

Safety preservation:

- exact owner/profile, explicit auth, challenge, rate-limit, query/filter, and
  typed terminal gates remain mandatory;
- cleanup still retains one active Facebook target and closes only same-site
  duplicates; no browser close or live provider effect is authorized.

Authority classification:

- `inherited_authority` for the bounded offline repair and installation;
  `human_gate` remains unchanged for any later Facebook provider tick.

Next action:

- implement the minimum adapter changes and turn both regressions green.

### Checkpoint P0034-C03 | 2026-08-09

Plan version: 3

State transition:

- `deterministic_red_proven -> repaired_installed_closed`.

Progress classification:

- `outcome_progress`; both installed failure shapes now have red-capable
  regressions and a bounded green successor.

Repair and validation evidence:

- service 0.3.38 gives navigation-only page-state reads a 12-second outer and
  three-second inner bound, opens the sole successor directly at its verified
  Facebook URL, removes the redundant local post-open wait, and leaves exact
  same-site predecessor closure to guaranteed cleanup;
- the two regressions failed before implementation with the observed
  three/four-second remaining-budget shapes and pass after repair;
- focused Facebook/worker/cleanup/tick/release/runtime/authority suites pass;
  the canonical suite passes 2,629 tests with 7 skips and 6 subtests;
- three independently produced artifacts are byte-identical at SHA-256
  `401a4f2d14d1cc977d2f4e14681ba3b61456432b3762814213a0d0e83e4ef5be`;
- installed 0.3.38/schema16 is ready at runtime-manifest SHA-256
  `99b2e4c1db862a99855430929d82d5ae5bc5ae092332cf035299e8b337da59b4`
  and contract SHA-256
  `fe8727fbe0d4e2f6775f49a6fc958369fe4877ba812bae4ef69121b88f12e2f1`;
- worktree, installed Skill, and installed service Facebook sources match at
  SHA-256 `5f4dd38aad442d3c501af6d648c36f3a703f9c3663f7347888d9264420adc53e`;
- a direct read-only CDP evaluation on the retained Facebook home target
  returned `readyState=complete`, authenticated DOM and `c_user` evidence;
  no provider tick, navigation, target open/close, or browser lifecycle action
  occurred;
- PID 63205 remains ready with four live tabs, exactly one Facebook target,
  zero challenges, and zero queue/lease wait depth. Both current/rollback
  SQLite quick checks are `ok`; `daily-default` remains enabled/ready at
  86,400 seconds with next boundary `2026-08-10T00:00:00Z`.

Doctor interpretation:

- raw install doctor remains false solely for two duplicate-profile-pressure
  warnings with zero candidates and zero readiness-impacting candidates;
- remote-view doctor preserves that raw warning while reporting effective
  `installReady=true` and `remoteControl.status=ready` with no issues.

Subagent status and reconciliation:

- none; diagnosis, implementation, installation, and verification remained
  serialized with the primary agent.

Authority classification:

- `inherited_authority` is consumed for the offline repair/install packet;
  `human_gate` remains mandatory for any later Facebook provider tick.

Graphiti write status:

- provider readiness passed and one compact source-backed closeout episode was
  queued as job `341c2a09-0cd5-40d8-acee-eb5a4da6650a` in
  `last30days_skill_main`.

Next action:

- keep Facebook manual. A later live proof needs a newly recorded operator
  attempt ceiling; do not infer qualification from offline or direct-CDP
  evidence and do not retry any Plan 0033 tick.
