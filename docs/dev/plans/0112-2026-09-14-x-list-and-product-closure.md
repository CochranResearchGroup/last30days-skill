# Plan 0112 | X List And Product Closure

State: OPEN
Lane: P35
Work item: WI-004
Branch: feat/x-tailored-follows-v3
Target: main
Integration: merge
Roadmap: P35
Plan version: 1
Date: 2026-09-14
Execution owner: /root/wi004_packet3_planning
Coordination owner: /root
Requested model route: gpt-5.6-terra, medium reasoning
Effective runtime model: unknown until reported

## Objective

Complete WI-004 provider-free by adding typed X-list acquisition and closing
scheduler, lifecycle, MCP, exact-follow search, readiness, and documentation
semantics without a real browser, schedule, or installed runtime.

## Current State

Packets 1-2 are integrated through PRs 68 and 79. Typed feed/topic/account/list
specs, immutable account context, account routing, lifecycle persistence, and
multi-cause publication exist. List work is still rejected/falls through;
scheduler aging and full MCP lifecycle parity remain incomplete.

## Scope

- add strict list-ID work dispatch and canonical `/i/lists/<id>` fixture route;
- cover list success, truthful empty, unavailable/private, auth/rate-limit,
  identity mismatch, bounded scroll, replay, and feed/account/list overlap;
- make oldest due time dominate scheduling and attention priority break only
  equal-due ties, preserving backoff, no-overlap, and profile leases;
- expose get/archive/include-archived parity through the existing MCP collection
  tool and prove CLI/app/MCP lifecycle agreement;
- prove exact partition-safe follow search through existing
  `legacy:spec:<collection_spec_id>` references without a new search field;
- update bounded operator/runtime guidance and complete provider-free presubmit.

## Non-Goals

No new collection migration or top-level API, WI-005 cross-service semantics,
real browser/profile/provider, installed database/runtime, schedule start,
release, staging, deployment, or live canary.

## Acceptance Criteria

1. Frozen list context reaches only the list adapter and cannot validate as
   account/topic/search work.
2. Synthetic outcomes preserve typed zero-yield/failure semantics, bounded
   work, and idempotent replay.
3. One native post seen by feed/account/list stays one content version with
   three exact sightings and partition-safe exact-follow search.
4. Scheduler tests prove oldest-due ordering, equal-due priority, and unchanged
   backoff/no-overlap/profile-lease controls.
5. CLI, app, and MCP agree on list/get/pause/resume/run/archive and archived
   default visibility.
6. Focused Python/Go suites, full Python presubmit, generated artifact join,
   runtime manifest, authority audits, and diff checks pass provider-free.
7. The exact clean branch is published and WI-004 has no remaining
   provider-free acceptance gap after coordinator integration.

## Execution Packet

- one top-level implementation owner, no children; two implementation attempts,
  one independent review, and one closed-world remediation pass;
- lane-owned writes: list acquisition/browser route, collection scheduler,
  focused Python fixtures/tests, MCP collection tool/tests, narrow docs, plan;
- shared contract/publication/search edits require coordinator reconciliation;
  generated catalog/manifest and authority projections are coordinator-only;
- terminal condition: published final provider-free WI-004 source acceptance or
  one exact blocker; do not begin WI-005.

## Definition Of Done

All seven criteria pass at an integration-ready checkpoint and coordinator
evidence can truthfully close WI-004 without any live canary.

## Current Checkpoint

### Checkpoint P0112-C01 | 2026-09-14

Plan version: 1

State transition: `PLANNED -> OPEN`.

Progress classification: `blocker_reduction`; this activation establishes
accountable branch custody and a recoverable provider-free implementation
boundary. No product source, test, generated artifact, shared authority, or
runtime state changed.

Custody:

- execution owner: `/root/wi004_packet3_planning` in
  `/home/ecochran76/workspace.local/last30days-skill-wi004-v3` on
  `feat/x-tailored-follows-v3`;
- registered base and local `HEAD` are
  `7f65c4285146e8d4dabd417617584fe7042a582f`, the Wave-2 registration merge;
- the branch was clean before this plan-only edit and no remote lane ref
  existed at activation preflight; publish this checkpoint with its exact
  post-commit remote equality before implementation resumes.

Authority classification:

- `inherited_authority` covers only this branch-local plan activation,
  provider-free source/tests, branch publication, review, and later coordinator
  integration under Plan 0107, WI-004, and this bounded plan;
- `human_gate` remains for browser/profile/provider access, live data, jobs or
  schedule starts, installed database/runtime, release, staging, production,
  deployment, rollback, and issue mutation;
- coordinator-owned `ROADMAP.md`, `RUNBOOK.md`,
  `docs/dev/active-lanes.yaml`, work-item projections, generated catalog,
  runtime manifest, and shared-contract joins were not edited by this lane.

Overlap and dependency boundary:

- lane-owned intended implementation surfaces are list acquisition/browser
  routing, collection scheduler ordering, focused Python fixtures/tests, MCP
  collection tool/tests, narrow operator guidance, and this plan;
- shared `service_contracts.py`, publication/search seams, generated artifacts,
  and MCP catalog/manifest reconciliation require coordinator ownership before
  any edit; P33 owns search ranking and P38 owns hotfix tooling;
- WI-005 remains outside this packet and may not start from this lane. P35
  completion is its Wave-2 prerequisite.

Discovery and validation evidence:

- Graphiti runtime doctor was healthy; focused `last30days_skill_main`
  discovery returned no WI-004/Plan-0112-specific fact, so current repository
  authorities are controlling;
- this worktree's CodeGraph status is `not initialized`. The activation makes
  no structural source claim and does not initialize derived state; an
  implementation turn must establish or document the required structural
  impact readback before changing code;
- pre-edit custody readback, `git diff --check`, and clean status passed. The
  activation validation after this edit is plan authority/audit validation,
  `git diff --check`, scoped diff review, commit, push, and exact remote
  equality. Product tests are intentionally not run because product files are
  out of scope.

Model and topology:

- requested route is `gpt-5.6-terra` at medium reasoning; effective runtime
  model and effort are `unknown` because the runtime did not report them;
- this packet has one top-level owner and no children. No subagent was spawned.

Next action or stop reason: commit and publish this activation-only checkpoint,
verify the remote ref resolves to the exact local commit, then stop. Resume
only for the provider-free implementation packet after re-reading current lane
overlaps and reconciling every shared surface through the coordinator.

### Checkpoint P0112-C02 | 2026-09-14

Plan version: 1

State: `OPEN`; provider-free source acceptance is complete, but coordinator
integration and generated-runtime reconciliation remain before the plan or
WI-004 may close.

Custody and ancestry:

- fetched `origin` and fast-forwarded this lane to exact canonical PR-82
  merge `5471e928b1f4c7867ea15de1d4e203b3315bb6e4`, preserving the C01
  activation ancestry before implementation;
- implementation remains confined to the registered P35 worktree and branch;
  no children, provider, browser/profile, schedule/job, installed database or
  runtime, WI-005, issue, release, or other live effect was invoked;
- model requested by the plan remains `gpt-5.6-terra` at medium reasoning;
  effective model/effort is still runtime-unknown.

Implemented provider-free source boundary:

- `AcquisitionWorkRequest` now admits only the typed `list` surface and the
  X worker dispatches it exclusively to `scrape_x_list`; it cannot take the
  generic X-search path;
- X list retrieval uses canonical `/i/lists/<list_id>` navigation and the
  established typed authentication, navigation, target, zero-yield, bounded
  scroll, quality, and replay semantics;
- due ordering is oldest `next_due_at` first, with `attention_class=priority`
  only breaking equal-due ties;
- the existing collection MCP tool has `get`, `archive`, and list-only
  `include_archived` parity, while its Go test proves the forwarded payloads;
- frozen feed/account/list context and three-sighting idempotency are covered,
  and existing post search is proven to use the exact
  `legacy:spec:<collection_spec_id>` partition reference without a new search
  contract;
- narrow SKILL, configuration, and MCP operator documentation records the
  supported list selector and lifecycle behavior.

Evidence:

- RED then GREEN focused checks passed for the new list dispatch, list browser
  route/outcomes, due-ordering, collection-context/search, and MCP lifecycle
  tests;
- `uv run pytest tests/test_service_contracts.py tests/test_service_acquisition_worker.py tests/test_service_collection.py tests/test_service_publication.py tests/test_service_post_search.py tests/test_service_product.py tests/test_x_browser.py -q` passed
  (exit 0; one documented skip);
- `go test ./internal/tools -count=1`, `go vet ./internal/tools`,
  `go test ./...`, and `go vet ./...` passed;
- existing CLI/app lifecycle parity was rechecked with
  `uv run pytest tests/test_service_product.py tests/test_service_process.py -q -k 'collection_service_get_list_and_archive_expose_lifecycle_history or collection_cli_exposes_additive_get_archive_and_hidden_history_controls'`
  (2 passed);
- `git diff --check` passed and the scoped diff contains only declared
  lane source/tests/docs plus this plan.

Generated-authority stop boundary:

- `uv run pytest -q` completed with 11 failures, all runtime-package or
  lifecycle-install tests caused by the deliberately untouched stale
  `service/runtime-manifest.json`; the direct no-effect build preflight says
  `service/runtime-manifest.json is stale; run service/scripts/build-runtime.sh --refresh-manifest`;
- generated runtime manifest/catalog and their authoritative join are
  coordinator-owned, so this lane must not refresh or commit them. The
  coordinator must regenerate/review those artifacts and repeat full
  presubmit after merging this source slice. This is an integration residual,
  not a provider or live-operation request.

Discovery and closeout:

- lane CodeGraph is not initialized and was not initialized as derived state;
  the clean canonical worktree at exact `5471e928` supplied the pre-edit
  structural readback. Current edited files are source/test authority until a
  coordinator re-index after integration;
- Graphiti discovery remained advisory and yielded no Plan-0112-specific
  current fact. Repository files and test receipts control;
- remaining gates are coordinator generated-artifact reconciliation, an
  independent scoped review, integration, and resulting clean source/full
  validation. Once those are complete, WI-004 has no known provider-free
  acceptance gap and is eligible for DONE; this lane stops before PR or WI-005.
