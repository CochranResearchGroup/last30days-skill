# Plan 0093 | Saved Monitors Packet 1

State: CLOSED
Lane: P40
Work item: WI-006
Branch: feat/saved-monitors-v1
Target: main
Integration: merge
Roadmap: P40
Plan version: 1
Date: 2026-09-13
Session owner: Codex `01a09cf4-c89e-7660-9caf-66a78f34ded0`

## Objective

Ship a provider-free monitor kernel with immutable specs, runs, accepted
baselines, fake saved-query views, deterministic comparison, lifecycle, and
replay semantics without scraping, scheduling, follow tracing, or delivery.

## Current State

- Packet 1 now supplies strict immutable monitor, saved-query view snapshot,
  comparison, run, baseline, decision, lifecycle, and error contracts;
- an additive provider-free kernel persists its own schema-v1 monitor tables,
  compares frozen evidence, replays deterministically, and advances the
  baseline only after explicit acceptance;
- P35 Packet 1 is not integrated, so every follow-view surface remains outside
  this packet;
- no digest, delivery, live query, refresh, provider/browser, installed
  runtime/database, scheduler, staging, release, production, or tracker effect
  was added;
- this branch contains exact `origin/main` commit
  `169a45b86735e1d4ccb48346d0f044f86105d610` through merge commit
  `f8b7bd6474163170e2cd62dea98d5c6125c0534a`.

## Scope

- implement immutable monitor-spec, run, baseline, view-snapshot, comparison,
  acceptance, lifecycle, and error contracts;
- add a fake saved-query view provider using stable evidence identity/version,
  access partition, coverage, cutoff, and frozen head;
- compare new, revised, unchanged, and explicitly tombstoned evidence while
  treating top-k absence or incomplete coverage as non-removal;
- advance a baseline only after explicit acceptance and make replay
  deterministic and idempotent;
- add migrations and provider-free lifecycle/comparison/replay tests.

## Non-Goals

- no follow-view contract or tracer, digest delivery, channel adapter, live
  query, refresh, scrape, browser/provider, installed runtime/database,
  scheduler, staging, release, production, or GitHub tracker mutation;
- no shared roadmap/runbook/catalog edits from this lane.

## Acceptance Criteria

1. Strict immutable contracts freeze monitor/view revisions, partition,
   evidence head, cutoff, coverage, prior baseline, and comparator version.
2. Identical frozen inputs replay to the same run and candidate baseline.
3. Only explicit acceptance advances the baseline; failure or rejection does
   not.
4. New, revised, unchanged, explicit removal, incomplete comparison, archive,
   pause, and partition mismatch are distinct and fail closed.
5. Focused migration, lifecycle, comparison, acceptance, and replay tests pass
   without network, schedule, delivery, runtime, or follow dependencies.

## Execution Packet

- accountable human owner: repository operator;
- execution owner: one independent top-level Codex session in this worktree;
- coordination owner: coordinator session for shared search/follow schemas,
  catalog, roadmap/runbook, MCP, notification, and release joins;
- expected writes: monitor contracts, durable repository/kernel, fake query
  view provider, migrations, focused fixtures/tests, and this plan;
- inputs: Plan 0083, note 0124, WI-006, merged P33 Packet 1, and current
  origin/main;
- terminal condition: all five criteria pass and a published PR-ready
  checkpoint exists, or one exact blocker is recorded without widening scope;
- authority: provider-free source, tests, branch publication, and PR
  preparation only.

## Start Checklist

- verify exact base, clean worktree, remote custody, and no overlapping PR;
- reread AGENTS.md and relevant planning, Git, validation, architecture, and
  multi-session policies;
- use read-only Graphiti discovery and CodeGraph impact where available;
- transition this plan to OPEN, record the runtime session identity, and push
  that planning checkpoint before implementation;
- coordinate any shared search-contract overlap before editing it.

## Stop Rules

- stop before follow tracing until P35 Packet 1 integrates;
- stop before digest delivery, notification/channel work, live query,
  refresh/scrape, provider/browser, installed runtime/database, schedule,
  staging, release, production, or tracker effects;
- stop and reconcile if another lane owns an overlapping shared contract.

## Current Checkpoint

### Checkpoint P0093-C01 | 2026-09-13

Plan version: 1

State transition: `planned -> open`.

Progress classification: `blocker_reduction`; independent lane custody is
activated and reconciled to current `origin/main`, while feature implementation
has not begun.

Base, merge, and ref evidence:

- the branch was created from exact base
  `87a8cbac467f979237f85b7e9a96946a2f137613` and its published plan-only tip
  was `7c184e439973fb860c5d93b8450d513b59baa328`;
- the 2026-09-13 fetch resolved `origin/main` to
  `606272ab82ba2c97d833e8b06e2c1ea4092bac85` and the pre-activation remote
  branch to `7c184e439973fb860c5d93b8450d513b59baa328`;
- `origin/main` was merged without rebase or history rewriting as merge commit
  `0023129028b75102d87e9c68074f829b6e65b86f`, with first parent
  `7c184e439973fb860c5d93b8450d513b59baa328` and second parent
  `606272ab82ba2c97d833e8b06e2c1ea4092bac85`;
- the worktree was clean before activation, exclusively owns
  `feat/saved-monitors-v1`, and no open pull request used that head branch.

Authority classification:

- `inherited_authority` for this activation checkpoint, the non-rewriting
  `origin/main` merge, branch publication, and later provider-free Packet 1
  source/tests within the frozen plan;
- `not_authorized` for shared roadmap/runbook/catalog/contracts, work-item or
  tracker mutation, follow tracing before P35 integration, installed runtime,
  provider/browser, schedules, delivery, staging, release, or production.

Owned changes:

- this checkpoint changes only Plan 0093 state, runtime session ownership, and
  activation evidence;
- the merge ancestry carries coordinator-owned documentation and validation
  updates from `origin/main`; none was independently edited or reconciled by
  this lane.

Validation evidence:

- AGENTS.md and the applicable planning, Graphiti, Git/worktree, commit/push,
  validation/handoff, documentation, lane, testing, work-item, multi-session,
  model-selection, and collaborative-development policies were reread;
- Plan 0083, note 0124 and its JSON companion, WI-006, and this plan were read
  as the controlling product and packet authorities;
- branch, worktree, clean-status, local/remote ref, merge-parent, ancestry, and
  open-PR checks passed;
- `git diff --check` and all 10 focused tests in
  `tests/test_plan_authority_audit.py` passed; final local/remote equality
  remains to be verified after publication.

Remaining acceptance criteria:

- all five Packet 1 criteria remain unmet because activation intentionally
  changed no feature source, migrations, fixtures, or tests;
- follow-view tracing remains out of scope until P35 integrates.

Subagent status and reconciliation:

- `not_spawned`; activation is a tightly coupled top-level ownership and Git
  checkpoint, and no independent implementation or review lane was opened.

Graphiti status:

- `healthy_read_no_relevant_recall`; the user-scoped runtime and FalkorDB were
  healthy, but one bounded search of `last30days_skill_main` returned no useful
  P40/WI-006 fact or episode;
- `write_not_attempted`; activation authority limits mutations to this plan and
  Git branch publication, so no Graphiti episode was added.

Next action:

- publish this activation checkpoint, verify exact local/remote equality, and
  stop for the coordinator to integrate ownership before Packet 1 feature
  implementation begins.

### Checkpoint P0093-C02 | 2026-09-13

Plan version: 1

State transition: `open -> closed`.

Progress classification: `outcome_progress`; all five Packet 1 acceptance
criteria are satisfied at the provider-free branch boundary.

Authority classification:

- `inherited_authority` for provider-free monitor source, fixtures, tests,
  this plan checkpoint, commit, and branch publication;
- `not_authorized` for coordinator-owned roadmap/runbook/catalog/work items,
  follow tracing before P35 integration, digest/delivery/channel work, live
  query or refresh, provider/browser, installed runtime/database, scheduler,
  staging, release, production, tracker, or PR effects.

Base, merge, and protected-surface evidence:

- the 2026-09-13 fetch resolved exact `origin/main` to
  `169a45b86735e1d4ccb48346d0f044f86105d610`;
- it was merged without rebase or history rewriting as
  `f8b7bd6474163170e2cd62dea98d5c6125c0534a`, whose first parent is
  `0253e82dfad36877371cbdaaa41e846560cfbc8a` and second parent is exact
  `origin/main`;
- `ROADMAP.md`, `RUNBOOK.md`, `docs/dev/active-lanes.yaml`, and every work item
  remained identical to `origin/main` after the merge and throughout this
  lane-owned implementation.

Owned changes:

- added `service_monitor_contracts.py` with closed-world immutable spec, view,
  evidence, coverage, comparison, baseline, run, decision, lifecycle, and
  error contracts;
- added `service_monitors.py` with a fake saved-query view adapter, isolated
  monitor-schema migration, durable repository, deterministic comparator,
  lifecycle transitions, replay, rejection, and acceptance-only head advance;
- added one provider-free JSON fixture and focused monitor tests, plus this
  acceptance checkpoint;
- no edits were required in `service_contracts.py`, `service_store.py`,
  `store.py`, shared schemas, MCP surfaces, or release/runtime manifests.

Acceptance evidence:

- immutable contracts freeze saved-query revision, monitor revision,
  partition, evidence head, cutoff, coverage, prior baseline, and comparator;
- identical frozen inputs return the same run and candidate baseline;
- explicit acceptance alone advances the durable head, while rejection,
  incomplete comparison, and stale-baseline races do not;
- new, revised, unchanged, explicit tombstone removal, top-k absence,
  incomplete coverage, pause, resume, archive, and partition mismatch have
  distinct provider-free assertions;
- Python compilation and `git diff --check` passed;
- all 48 focused monitor, migration, store, contract, and saved-search tests
  passed;
- the broad non-release presubmit passed with 2,787 tests, 7 skips, and 9
  subtests; only release/install packaging suites were excluded.

Validation boundary:

- the retained comprehensive first-failure receipt was 2,785 passed, 7 skipped,
  and 10 failed after the monitor schema was isolated; every failure was in
  runtime artifact/install packaging because the new modules are intentionally
  absent from frozen release manifests;
- release-manifest, installed-runtime, lifecycle-install, MCP publication, and
  release-version changes are outside Packet 1 and were not used to turn that
  packaging boundary green.

Shared overlap for coordinator reconciliation with P36:

- `none` in current tracked implementation: no shared contract, store, schema,
  MCP, or coordinator-owned authority was edited;
- future runtime packaging and service/MCP exposure of these additive modules
  remain coordinator/release integration joins, not Packet 1 work.

Subagent status and reconciliation:

- `not_spawned`; the operator explicitly prohibited subagents for this packet.

Graphiti status:

- `healthy_read_no_relevant_recall`; one bounded read of
  `last30days_skill_main` returned no useful P40/WI-006 episode or fact;
- `write_not_attempted`; the explicit no-installed-runtime/database boundary
  excludes a Graphiti database mutation in this packet.

Remaining criteria:

- none for Plan 0093 Packet 1; follow tracing remains forbidden until P35
  integrates, and digest/delivery plus runtime publication remain later gated
  packets.

Next action:

- publish a clean remote-equal Packet 1 checkpoint and stop for coordinator
  reconciliation; do not open or merge a pull request from this session.
