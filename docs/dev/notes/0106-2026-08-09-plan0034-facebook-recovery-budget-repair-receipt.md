# Note 0106 | Plan 0034 Facebook Recovery-Budget Repair Receipt

Date: 2026-08-09
Source plan: Plan 0034 version 3/C03

## Diagnosis And Red Proof

- Plan 0033's retained-owner/evaluation-loss trace left three seconds before
  legacy blank-target replacement; its replacement-auth/later-open traces left
  four seconds for the query open;
- two deterministic regressions replay those operation budgets. Both failed
  before implementation as `facebook_target_unresponsive` or
  `agent_browser_timeout` and pass with the successor;
- the cause was cumulative-budget starvation, not evidence of logout,
  CAPTCHA, checkpoint, rate limit, empty content, or quality rejection.

## Repair

- service 0.3.38 uses a 12-second/three-second navigation-only page-state
  deadline while leaving extraction's existing bound unchanged;
- one recovery target opens directly at the verified Facebook home or query
  URL. The existing guaranteed cleanup retains the active successor and closes
  only same-site predecessors;
- the redundant identity inventory read, blank-target navigation, second open,
  and local post-open wait are removed from the recovery critical path;
- owner/profile, explicit-auth, challenge, rate-limit, query/filter,
  one-successor, typed-terminal, 75-second adapter, 120-second parent, and
  one-final-target gates remain fail-closed.

## Validation And Installation

- focused Facebook, isolated-worker, parent-cleanup, tick-runtime, release,
  runtime-package, and authority suites pass;
- the full suite passes 2,629 tests with 7 skips and 6 subtests;
- three service artifacts are byte-identical at SHA-256
  `401a4f2d14d1cc977d2f4e14681ba3b61456432b3762814213a0d0e83e4ef5be`;
- installed 0.3.38/schema16 is ready with runtime-manifest SHA-256
  `99b2e4c1db862a99855430929d82d5ae5bc5ae092332cf035299e8b337da59b4`
  and unchanged contract SHA-256
  `fe8727fbe0d4e2f6775f49a6fc958369fe4877ba812bae4ef69121b88f12e2f1`;
- repository, installed Skill, and installed-service Facebook files match at
  SHA-256 `5f4dd38aad442d3c501af6d648c36f3a703f9c3663f7347888d9264420adc53e`.

## Current Runtime Readback

- a manual read-only direct CDP evaluation—not a provider tick—returned the
  Facebook home URL, `readyState=complete`, authenticated DOM, and `c_user`;
- browser `session:last30days-facebook` remains PID 63205, health `ready`,
  `lastError=null`, with four live tabs and one Facebook target
  `82D598B764CDCCC8F71D26B05F5F6EC2`;
- challenges, control-plane queue depth, and profile-lease wait depth are zero;
- current and rollback SQLite quick checks are `ok`; `daily-default` remains
  enabled/ready at 86,400 seconds with next boundary
  `2026-08-10T00:00:00Z`;
- install doctor has only nonblocking duplicate-profile-pressure warnings:
  candidate count and readiness-impacting candidate count are zero. Remote
  control is ready with effective `installReady=true`.

No Facebook provider tick, new target, navigation, close, browser lifecycle,
login/logout, MFA, CAPTCHA/checkpoint interaction, rate-limit generation,
provider fallback, cost, or model use occurred. Facebook remains manual and
not routine-qualified; any live proof needs a new explicit attempt ceiling.
