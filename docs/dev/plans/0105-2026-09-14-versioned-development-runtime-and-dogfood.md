# Plan 0105 | Versioned Development Runtime And Dogfood

State: CLOSED
Lane: P51
Work item: WI-009
Parent plan: docs/dev/plans/0102-2026-09-13-productization-readiness-prerequisites.md
Branch: feat/p51-isolated-runtime-v1
Target: main
Integration: merge
Roadmap: P51
Plan version: 4
Date: 2026-09-14
Session owner: primary Codex goal thread

## Objective

Complete P51 Packets 4 and 5 by producing a deterministic service `0.3.117`
development artifact, provisioning exactly one isolated development runtime
whose identity and state cannot collide with production, and executing
provider-free dogfood across stored search, question answering, monitors,
quality reporting, and tailored-follow lifecycle.

## Current State

- PRs 73 and 74 integrated the exact-owner cache-only runtime lifecycle and
  canonical versioned artifact-root handling at canonical
  `1168c62e0192ff33f71a07482a32b05721fb839a`;
- two clean fixed-input builds from that commit are byte-identical at SHA-256
  `cf64df41ed072b3d87085b537e0cbe4960d56e71d34d70891b386e152d15bff2`;
  service `0.3.117`, schema 18, and runtime manifest
  `a0a11ff4be28ac72048f1634221ef59d464802222f0f0ac571a6fe242d1e83c3`
  agree;
- exactly one isolated runtime, `l30d-p51-dogfood-cdbb3d9fd80b`, passed
  `doctor`, `up`, and `status`, completed the five synthetic provider-free
  dogfood surfaces, rejected a refresh-capable live-socket query, and stopped
  through exact-owner `down` while retaining its state and receipts;
- fresh post-dogfood production readback still reports PID 1428, service
  `0.3.116`, schema 17, installed manifest
  `19707a469eb58c21ca4c5b43a0bfbfb6cac4b0f5a5310480b01b1a3f652429e8`,
  and the original unit, database, socket, and config identities;
- comprehensive Python, focused runtime/package/plan, MCP Go test/vet,
  manifest, diff, and authority validation pass. Durable evidence is indexed by
  `docs/dev/notes/0126-2026-09-14-p51-runtime-dogfood-closeout-receipt.json`.

## Scope And Ordered Slices

1. Publish this registration, then run independent read-only audits of artifact
   reproducibility, runtime isolation, and provider-free dogfood coverage.
2. Add the minimum controller lifecycle and service-side cache-only effect gate
   required by the accepted Plan 0077 architecture, with exact-target tests.
3. Integrate source through a reviewed pull request, then build twice from the
   exact merged commit with fixed inputs. Require byte-identical artifact hashes
   and a manifest matching source.
4. From the verified artifact, provision exactly one runtime with private
   identity, database, socket, config, logs, PID/birth identity, receipts, and
   credential-free child environment. Refuse a second live owner.
5. Seed only synthetic/local non-private fixtures and dogfood stored search,
   structured and evidence-only questions, saved monitors, quality reports, and
   tailored-follow create/read/archive history.
6. Re-read production without mutation, reconcile all receipts and projections
   through a reviewed closeout pull request, and close WI-009 only if every
   Plan 0102 and Plan 0105 criterion passes.

## Authority

The operator authorizes repository changes, normal owned-fork pull requests,
deterministic local builds, disposable provider-free fixtures, and mutation of
exactly one isolated development runtime created by this plan.

## Non-Goals

This plan does **not** authorize production or staging mutation; provider
credentials or calls; browsers/profiles, schedules, notifications, live or
private data; release publication, tags, deployment; GitHub issue mutation; or
deletion of historical worktrees/evidence. The controller must never control
or install production `last30days.service`.

## Isolation Contract

- Runtime identity derives from repository identity, worktree, work item, plan,
  lane, and exact artifact/source commit.
- Config, data, database, artifacts, logs, run directory, Unix socket, PID,
  lock, descriptor, and receipts stay beneath one private controller-owned root
  and outside every production root.
- The child environment is an allowlist without provider, browser, notification,
  scheduling, Graphiti, assessment, or inherited credential variables.
- `up` locks the lane, validates `doctor`, records startup intent, launches the
  foreground service with redirected logs, waits for its identity handshake,
  and binds PID plus OS-process birth identity and descriptor digest.
- `status` verifies that same process, command, artifact/source commit, socket
  owner, descriptor, service version, schema, and manifest.
- `down` signals only the exactly verified process and retains database, logs,
  and receipts. Ambiguous or stale ownership fails closed.
- The service cache-only gate denies refresh, collection, scheduled ticks,
  incidents/observation, assessment, repair, notification, projection,
  provider, and browser effects before durable work is admitted.

## Parallel Execution And Model Routing

Topology: one primary orchestrator with at most three one-level read-only
subagents. Optimization is `balanced`; maximum active subagents is 3 and depth
is 1. Subagents may inspect and report but may not edit, run a service, build
artifacts, call providers/browsers, mutate Git/forge state, or spawn agents.

- Artifact reproducibility audit: economical `gpt-5.6-luna`, low effort.
- Runtime isolation/deny-surface audit: `gpt-5.6-sol`, medium effort because a
  missed effect can cross an authority boundary.
- Provider-free dogfood matrix audit: economical `gpt-5.6-luna`, low effort.

These are provisional requested routes because the repository has no accepted
model benchmark. Reports record actual model/effort only when the runtime
reports it. The primary owns architecture, authority, edits, joins, Git
integration, live-process actions, and final acceptance.

## Expected Write Surface

- `dev/last30days/scripts/lane_runtime.py` and focused controller tests;
- minimum service initialization/application surfaces needed for an explicit
  cache-only gate and focused tests;
- deterministic build metadata only if current tooling cannot prove the
  artifact contract;
- provider-free dogfood fixtures/scripts and repo-only receipts;
- this plan, Plan 0102, WI-009, ROADMAP, RUNBOOK, and active-lane projections.

Any production installer/unit/config path, provider behavior, schema redesign,
public release surface, or product capability outside these requirements needs
a plan revision and fresh authority.

## Acceptance Criteria

1. Two clean builds from one exact merged commit and fixed inputs are
   byte-identical; artifact/source version, schema, and runtime manifest agree
   at service `0.3.117` / schema 18.
2. Exactly one development process passes `doctor`, `up`, and `status`; its
   descriptor, PID birth identity, database, socket, config, log, receipt,
   environment, version, schema, and manifest are distinct from production.
3. Negative tests prove stale PID reuse, foreign descriptors, second-owner
   startup, symlinks, production paths, inherited secrets, and effectful
   operations fail closed before external or durable effect admission.
4. Provider-free dogfood receipts prove stored search, structured and
   evidence-only questions, saved monitors, quality reports, and tailored-follow
   create/read/archive history against that exact runtime.
5. Focused suites, full `uv run pytest`, MCP `go test ./...` and `go vet ./...`,
   manifest validation, planning/lane audits, and `git diff --check` pass.
6. Fresh post-dogfood readback shows production retains its original unit,
   PID/process identity, database/socket/config identity, service `0.3.116`,
   schema 17, and installed manifest hash.
7. Source, artifact, runtime, dogfood, Git/PR, plan, roadmap, runbook, lane, and
   work-item claims reconcile before WI-009 is marked `DONE`.

## Work Bounds And Stop Rules

- Critical path: registration PR, audit join, implementation PR, canonical
  artifact build, one-runtime provisioning, dogfood, and closeout PR.
- At most two implementation attempts per failed criterion, one
  infrastructure-only retry, one full remote-diff review per PR, and one
  bounded remediation pass before checkpointing an exact blocker.
- Stop on dirty/ambiguous custody, stale mainline, non-reproducible artifact,
  manifest mismatch, unknown process identity, second runtime, production
  drift, unexpected credentials/effect capability, private data, or any named
  prohibited effect.
- Preserve failed receipts. Do not kill, overwrite, migrate, or clean an
  unverified process or state root.

## Definition Of Done

All seven criteria pass at exact merged commits; the deterministic artifact and
exactly one isolated development runtime agree at service `0.3.117`; all five
provider-free product lanes have inspectable receipts; production is freshly
proven unchanged; Plan 0102 is closed; and WI-009 is `DONE` in repo authority
without mutating its GitHub issue.

## Current Checkpoint

### Checkpoint P0105-C01 | 2026-09-14

Plan version: 1

State transition: `unplanned -> OPEN`.

Progress classification: `blocker_reduction`; the exact goal and isolated
runtime authority are active, current Git/runtime evidence is re-anchored, and
Packets 4 and 5 now have bounded proof, integration, fanout, and stop contracts.

Authority classification:

- `inherited_authority` for repository changes, deterministic builds,
  provider-free fixtures, normal pull requests, and one isolated runtime;
- `human_gate` for production/staging, providers, browsers, schedules,
  private/live data, release publication, tags, deployment, and GitHub issues;
- `scope_expansion` for new product features or any second runtime.

Evidence:

- canonical main, production, source, and manifests match the exact Current
  State readback above; production PID was 1428 and no timer was present;
- Graphiti was healthy but returned no newer governing P51 runtime decision;
  current plans, note 0118, files, Git, and runtime readback are authoritative;
- the controller currently exposes only `doctor`, while service startup enables
  recurring/effectful loops unless an explicit cache-only gate is added.

Subagent status: `not_spawned`; fanout begins after registration integration.

Graphiti write status: `not_written`; no explicit memory-write authority exists.

Next action: validate, publish, review, and merge this registration; then spawn
and join the three bounded read-only audits before implementation.

### Checkpoint P0105-C02 | 2026-09-14

Plan version: 2

State transition: `OPEN -> OPEN`; the implementation slice is validated on
commit `a8c8114832df588e786891cd36fb69457f402250` and published with its governance
checkpoint at remote-equal tip `3ac5728753abb57d5239d0812740323653cbfebb`.

Progress classification: `outcome_progress`; the artifact, isolation, and
dogfood audits were joined, the cache-only boundary and exact-owner lifecycle
were implemented, and comprehensive provider-free validation passes.

Authority classification:

- `inherited_authority` covered source/tests, deterministic manifest refresh,
  read-only subagent audits, and provider-free validation;
- `human_gate` remains for every production/staging, provider/browser, schedule,
  private/live data, release-publication, deployment, or GitHub issue effect;
- `scope_expansion` remains any new product surface or second runtime.

Evidence:

- requested audit routes were artifact `gpt-5.6-luna`/low, isolation
  `gpt-5.6-sol`/medium, and dogfood `gpt-5.6-luna`/low; no worker runtime exposed
  an actual effective model/effort identity;
- the artifact audit found the existing builder already canonicalizes inventory,
  ownership, timestamps, gzip metadata, and manifest validation, so no builder
  change was required;
- the isolation audit identified every acquisition, Tick, assessment, Graphiti,
  maintenance, enrichment, refresh, resume, topic-mutation, and collection-run
  seam. The primary resolved the join by keeping the service process strictly
  cache-only while permitting only explicit provider-free dogfood kernels/CLI
  against the isolated database;
- the corrected dogfood audit confirmed tailored-follow lifecycle through the
  existing collection CLI and question/monitor proof through accepted direct
  kernels, with no need to add a public product API;
- controller `doctor/up/status/down` now verifies a safe extracted artifact,
  signed descriptor, private state, Linux boot/start birth identity, exact
  command, environment digest, Unix peer credentials, version/schema/manifest
  handshake, duplicate-owner denial, and pidfd-only teardown;
- cache-only service startup constructs no acquisition, Tick, assessment,
  Graphiti, maintenance, or recurring-enrichment loop, advertises no effectful
  capabilities, and denies refresh-capable query, topic mutation, job resume,
  and collection-run actions before admission;
- focused 65-test service/app/HTTP/controller validation, runtime-package tests,
  full `uv run pytest -q`, MCP `go test ./...`, MCP `go vet ./...`, Python
  compilation, manifest refresh, and `git diff --check` pass.

Subagent status: `joined`; all three reports were advisory and read-only. The
primary corrected the initial dogfood report's missed P35 collection contract
before using it and retained every architecture and acceptance decision.

Graphiti write status: `not_written`; no explicit memory-write authority exists.

Remaining acceptance criteria: publish/review/merge the implementation, build
two byte-identical artifacts from merged canonical main, provision exactly one
runtime, execute and retain five dogfood receipts, prove production unchanged,
and integrate closeout projections.

Next action: integrate this catalog checkpoint, then self-review and merge the
exact owned-fork implementation pull request.

### Checkpoint P0105-C03 | 2026-09-14

Plan version: 3

State transition: `OPEN -> OPEN`; custody advances from `ACTIVE_WORKTREE` to
`INTEGRATION_READY` at exact remote-equal feature tip
`5c1d62285f3bd834c9c7cdf060ca710d1bcbe928`.

Progress classification: `outcome_progress`; the canonical catalog join was
merged through PR 71, its three expected governance conflicts were resolved by
preserving the accepted canonical versions, and the combined feature branch
passes its focused integration surface.

Authority classification:

- `inherited_authority` covers immutable custody publication, reviewed feature
  PR integration, and provider-free validation;
- every named external/live effect remains `human_gate`, while a second runtime
  or new product API remains `scope_expansion`.

Evidence:

- PR 71 merged the audit/validation catalog at canonical
  `ee97362d2777d7a9c5e24f82d7784e4adda69b0f`;
- the feature branch merged that exact canonical commit and preserved its
  governance versions while retaining implementation commit `a8c81148`;
- post-merge focused controller, service app, HTTP, process, and runtime-package
  validation passes 69 tests at remote-equal tip `5c1d6228`;
- canonical `main` was restored to remote equality after one accidental local
  cherry-pick was caught before push; the preserved commit remains recoverable
  in reflog and no remote state was affected.

Subagent status: `joined`; no further delegation is required for integration.

Graphiti write status: `not_written`; no explicit memory-write authority exists.

Remaining acceptance criteria: merge the reviewed feature PR, build the exact
canonical artifact twice, provision/dogfood exactly one runtime, prove
production unchanged, and integrate closeout.

Next action: publish this integration-ready catalog, then open, self-review, and
merge the exact feature PR without another feature-branch rewrite.

### Checkpoint P0105-C04 | 2026-09-14

Plan version: 4

State transition: `OPEN -> CLOSED`; all seven acceptance criteria pass and the
exact isolated runtime has been stopped through its verified owner identity.

Progress classification: `outcome_complete`; Packets 4 and 5 are integrated,
reproducible, dogfooded, reconciled, and closed without crossing any prohibited
production, provider, browser, schedule, release, deployment, private-data, or
GitHub issue boundary.

Evidence:

- reviewed implementation PR 73 merged at
  `633297cb88b161bdd72c57fcd186d51364cb60d4`; focused hotfix PR 74 merged at
  canonical `1168c62e0192ff33f71a07482a32b05721fb839a` after a production-shaped
  archive regression test reproduced `artifact_manifest_invalid`;
- two `SOURCE_DATE_EPOCH=0` builds from exact canonical `1168c62e` are
  byte-identical at artifact SHA-256
  `cf64df41ed072b3d87085b537e0cbe4960d56e71d34d70891b386e152d15bff2`;
- runtime `l30d-p51-dogfood-cdbb3d9fd80b` bound descriptor digest
  `a7551944051cd59d78b575022d5f4e81afc8663a0b7bbdd7ba2020ec7a8e3c76`,
  PID 859669/start ticks 1166337, exact Unix peer PID/UID, service `0.3.117`,
  schema 18, and manifest
  `a0a11ff4be28ac72048f1634221ef59d464802222f0f0ac571a6fe242d1e83c3`;
- the strict child environment contained only locale, private XDG/runtime
  paths, and explicit deny/cache-only policy keys; no credential, provider,
  browser, notification, or schedule input was inherited;
- synthetic provider-free receipts pass stored search, structured and
  evidence-only questions, saved monitors, four-axis quality reporting, and
  tailored-follow create/read/archive history. Search also passed through the
  live runtime socket, and `force_refresh` was denied with
  `effect_disabled_by_runtime`;
- exact-owner `down` stopped only PID 859669 and removed the dev socket while
  retaining the private database, logs, descriptor, artifact, and 0600
  receipts. The fresh process census then contained production PID 1428 alone;
- fresh production readback preserved unit
  `/home/ecochran76/.config/systemd/user/last30days.service`, config
  `/home/ecochran76/.config/last30days/.env`, database
  `/home/ecochran76/.local/share/last30days/research.db`, socket
  `/run/user/1000/last30days/service.sock`, service `0.3.116`, schema 17, and
  installed manifest
  `19707a469eb58c21ca4c5b43a0bfbfb6cac4b0f5a5310480b01b1a3f652429e8`;
- full `uv run pytest -q`, the focused 38-test controller/package/authority
  surface, MCP `go test ./...`, MCP `go vet ./...`, plan-authority audit,
  deterministic manifest refresh, and `git diff --check` pass.

Failure evidence retained:

- the first provisioning attempt failed closed before process launch because
  the controller expected a direct archive root; PR 74 repaired the canonical
  single version-directory layout without weakening safe extraction;
- one redundant validation process caused by unsafe PR-body shell quoting was
  identified and terminated by exact PID before PR creation; no forge or
  runtime state was affected;
- the first dogfood script attempt wrote valid synthetic search/question/
  monitor state before stopping on a quality receipt field-name mismatch. The
  durable state was preserved and read back idempotently; the final receipt
  records all five passes.

Subagent status: `joined`; the artifact, isolation, and dogfood audits remained
read-only advisory evidence. Requested routes were Luna/low, Sol/medium, and
Luna/low; actual effective worker identities were not runtime-reported. The
primary independently validated every acceptance surface and retained all
runtime, integration, and acceptance decisions.

Graphiti write status: `not_written`; no explicit durable-memory write authority
was granted. Repo plans, receipt index, Git, tests, artifact hashes, and runtime
readbacks are authoritative.

Next action: close parent Plan 0102 and WI-009 in repo authority, release the P51
feature freeze, and select later work only through a separately bounded plan.
