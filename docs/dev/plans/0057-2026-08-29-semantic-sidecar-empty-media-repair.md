# Plan 0057 | Semantic Sidecar Empty Media Repair And Volume Canary

State: OPEN
Roadmap: P08
Plan version: 3
Date: 2026-08-29

## Objective

Stop expected text-free media from degrading otherwise successful X and
LinkedIn home-feed ticks, exclude deterministic LinkedIn avatar/logo chrome
from post-owned media, prove the repair with a 20-item canary for each source,
and only after that canary succeeds run one 40-item canary for each source.

## Current State

- `main` and `origin/main` are synchronized at
  `59acf55125182e63f3463672d55be3d0a75a302a` before this slice;
- tick `tick-b5c8a3b8b06e9103e581cdac8456ec67` collected 20 canonical X posts and
  20 canonical LinkedIn posts, but terminalized `complete_degraded` because
  both optional semantic-sidecar stages were `failure`;
- 17 of 30 media assets produced deterministic source-grounded sidecars;
  all 13 failures had neither source alt text nor OCR text;
- 12 failures were LinkedIn assets, including 11 profile photos across only
  three distinct URLs, and one was an X video thumbnail;
- the source-grounded adapter raises `AnalysisOutputMissing` when both grounded
  text inputs are absent, and the runner records that expected absence as a
  failure; mixed success plus empty already aggregates to success, but no
  explicit empty analysis outcome reaches that path today.

## Scope

- filter deterministic LinkedIn author/profile/company chrome from candidate
  media before generic acquisition materializes it;
- represent the absence of source-grounded text as an explicit empty analysis
  outcome with the preserved reason `source_grounded_text_missing`;
- publish a durable empty semantic-sidecar derivative for that outcome while
  retaining true exceptions and invalid adapter output as failures;
- prove mixed successful and empty sidecars leave the lane and tick successful;
- run focused, presubmit/full, packaging, installed-runtime, and durable receipt
  validation proportionate to the changed surface;
- run exactly one 20+20 X/LinkedIn home-feed canary after installation; if and
  only if both collections yield 20 canonical posts and the expected empty
  sidecars do not degrade the tick, run exactly one 40+40 canary.

## Non-Goals

- do not add a vision model, GraphRAG, probabilistic content-quality filtering,
  or semantic post ranking;
- do not exclude posts because their media is empty, and do not change the
  deterministic obvious-ad/spam rejection policy;
- do not re-enable Reddit or Facebook, alter authenticated browser profiles,
  create replacement browser sessions, or modify Agent Browser;
- do not persist higher recurring ceilings until the one-shot 40+40 result is
  reconciled; use owner-private canary configuration that leaves the recurring
  schedule unchanged;
- do not hide genuine OCR, adapter, persistence, or media failures by
  classifying them as empty.

## Acceptance Criteria

1. LinkedIn post normalization excludes known `profile-displayphoto`,
   `company-logo`, and `group-logo` media while retaining post image and video
   media.
2. A source-grounded sidecar input with neither meaningful alt text nor OCR
   emits a typed empty outcome carrying `source_grounded_text_missing`.
3. The durable derivative ledger records that outcome as `empty`, not
   `failure`, and retains its adapter, reason, and input references.
4. A lane containing both successful and empty semantic sidecars reports the
   semantic-sidecar stage `success`; genuine adapter-output absence remains a
   stage failure and degrades the tick.
5. Focused tests demonstrate red-before-green for each repaired invariant, and
   the documented presubmit/full, packaging, and policy checks pass.
6. The installed runtime is bound to the validated source/artifact identity and
   remains ready on schema 16 with SQLite integrity healthy.
7. One 20+20 canary yields 20 unique canonical X URLs and 20 unique canonical
   LinkedIn URLs with successful collection and no degradation from expected
   text-free media.
8. Only after criterion 7 passes, one 40+40 canary is attempted and its exact
   observed, accepted, rejected, media, derivative, stage, timing, and terminal
   receipts are reconciled without treating ceilings as guaranteed yield.
9. The recurring configuration, Reddit/Facebook disabled state, authenticated
   profile routing, and timer schedule remain unchanged by both canaries.

## Execution Packets

### P1 | Contract repair

- Owner: primary agent.
- Write surface: LinkedIn media normalization, analysis outcome, derivative
  publication, runner handling, and focused tests.
- Terminal condition: all four code-level acceptance criteria pass at focused
  seams and existing genuine-failure coverage remains green.

### P2 | Integration and install

- Owner: primary agent.
- Write surface: package/version and required governing documentation only.
- Terminal condition: comprehensive validation passes and the exact artifact is
  transactionally installed with current readiness evidence.

### P3 | 20 then 40 live canaries

- Owner: primary agent.
- Inputs: installed candidate, existing authenticated X and LinkedIn profiles,
  bounded owner-private one-shot configs.
- Terminal condition: one terminal 20+20 receipt; if accepted, one terminal
  40+40 receipt, followed by recurring-schedule and database reconciliation.

## Definition Of Done

- all acceptance criteria have current authoritative evidence; the plan is
  reconciled to `CLOSED`, the implementation is committed and pushed through
  the repository's normal integration path, and no temporary canary config or
  active lease remains.

### Checkpoint P0057-C01 | 2026-08-29

Plan version: 1

State transition:

- `diagnosed -> contract_repair_active`.

Progress classification:

- `outcome_progress`; the live 20+20 receipt and code flow isolate expected
  text-free media from genuine analyzer failures and establish a stable test
  seam.

Validation evidence:

- current database correlation is exact: 13/13 failed sidecars had no alt text
  and no OCR text, while every asset with either grounded input produced a
  sidecar;
- failure composition is 11 LinkedIn profile photos across three URLs, one
  LinkedIn post image, and one X video thumbnail;
- current code raises `source_grounded_text_missing` inside the deterministic
  adapter, catches it as a generic exception, persists
  `analysisoutputmissing`, and marks any resulting failure as lane-stage
  failure;
- branch and remote start synchronized and the worktree starts clean.

Authority classification:

- `inherited_authority`; implementation, installation, a 20+20 canary, and the
  conditional 40+40 canary were explicitly requested.

Subagent status:

- `not_spawned`; current orchestration policy prohibits delegation.

Next action or stop reason:

- execute one red-green vertical slice for LinkedIn post-owned media, then one
  red-green vertical slice for the explicit empty analysis outcome and durable
  tick aggregation.

### Checkpoint P0057-C02 | 2026-08-29

Plan version: 2

State transition:

- `contract_repair_active -> validated_runtime_candidate`.

Progress classification:

- `outcome_progress`; both repaired invariants are green at their stable seams
  and service 0.3.78 carries the exact runtime candidate.

Validation evidence:

- the LinkedIn regression failed red with avatar and company-logo URLs retained,
  then passed with post image and video media preserved;
- the source-grounded adapter regression failed red because no typed empty
  outcome existed, the durable publisher regression failed red because no
  empty derivative interface existed, and the tick regression failed red as
  `complete_degraded`; all pass after the bounded repair;
- focused affected suites pass with 136 tests plus one opt-in live skip;
- release/runtime package checks pass after service 0.3.78 and its canonical
  runtime manifest were refreshed;
- the comprehensive suite reports 2,708 passed, seven skipped, and six
  subtests, with one plan-authority expectation failure caused by the prior
  test still naming now-closed Plan 0056. Plan 0057 is now wired into P08 and
  Turn 349 while that deterministic expectation is updated in this checkpoint;
- after the authority repair, the comprehensive rerun passes with 2,709 tests,
  seven skips, and six subtests; MCP Go packages, Python compilation, active
  planning, goal-governance, plan-authority, and catalog-only lane audits pass;
- Ruff is unavailable in the repository uv environment, so no Ruff claim is
  made.

Authority classification:

- `inherited_authority`; source repair, validation, release preparation, and
  the next transactional install remain inside the approved goal.

Subagent status:

- `not_spawned`; current orchestration policy prohibits delegation.

Next action or stop reason:

- make the plan-authority projection green, rerun comprehensive validation,
  build and transactionally install exact service 0.3.78, then execute the
  bounded 20+20 canary.

### Checkpoint P0057-C03 | 2026-08-29

Plan version: 3

State transition:

- `validated_runtime_candidate -> live_gate_failed_repair_validated`.

Progress classification:

- `outcome_progress`; the semantic-empty repair is proven live, the 20-item
  volume gate has an exact failure receipt, and one additional deterministic
  LinkedIn chrome family exposed by that receipt is repaired in service
  0.3.79.

Validation evidence:

- combined canary `tick-fec768d7311523394f8ca5b5b714cde6` terminalized
  `complete_degraded`: X observed and attempted 35 cards, accepted 20, rejected
  15, and completed every media, OCR, and semantic-sidecar stage successfully;
  LinkedIn failed before observing a card with the safe transient code
  `agent_browser_error` after 102 seconds and one network request;
- bounded LinkedIn successor `tick-4ba548dbb0869f08cccebf0309f8a523`
  terminalized `complete`: it observed and attempted 246 cards, accepted 11,
  rejected 235, and completed collection, media, OCR, and semantic-sidecar
  stages successfully in 86 seconds and ten network requests;
- the LinkedIn rejection receipt records 102 outside-date-range observations,
  76 duplicates, 48 sponsored/ad observations, and nine cards without a
  canonical permalink. Counts can overlap when one card has multiple reasons;
  no authentication or semantic-sidecar failure explains the 11-item yield;
- the successful successor persisted eight media assets and 16 derivatives,
  including three truthful `source_grounded_semantic_sidecar_v1:empty-v1`
  outcomes and no semantic failure;
- three remaining `group-logo_image-shrink_48x48` identity assets produced six
  empty OCR/sidecar derivatives. A focused regression reproduced that leak
  red, then passed after `group-logo` joined the deterministic identity-chrome
  filter while feed-share and video-cover media remained retained;
- focused LinkedIn, release, runtime-package, and lifecycle-install suites pass;
  the comprehensive Python suite, all MCP Go packages, Python compilation,
  and diff checks pass for service 0.3.79. Ruff remains unavailable and is not
  claimed.

Gate disposition:

- criterion 7 is not met because LinkedIn accepted 11 rather than 20; the
  criterion 8 precondition is therefore false and no 40+40 canary is
  authorized by this plan;
- the two live attempts exhaust this bounded work unit. Further retrieval work
  should target the nine missing-permalink observations with new durable
  instrumentation rather than repeat the same canary unchanged.

Authority classification:

- `inherited_authority`; the deterministic media repair, validation, and exact
  successor installation remain inside the approved goal. Another live volume
  attempt is intentionally stopped at the recorded bound.

Subagent status:

- `not_spawned`; current orchestration policy prohibits delegation.

Next action or stop reason:

- commit and push the service 0.3.79 candidate, transactionally install that
  exact artifact, and reconcile readiness, schedule/configuration invariance,
  leases, and database integrity. Leave the plan open on the unmet 20-item
  LinkedIn gate; do not run 40+40.
