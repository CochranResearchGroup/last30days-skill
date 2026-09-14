# Plan 0121 | Monitor And Digest Product Closeout

State: OPEN
Lane: P40
Work item: WI-006
Branch: feat/monitor-digest-product-closeout-v1
Target: main
Integration: merge
Roadmap: P40
Plan version: 1
Date: 2026-09-14
Execution owner: unassigned
Coordination owner: /root
Requested model route: gpt-6-astra, high reasoning
Effective runtime model: unknown until reported

## Objective

Close WI-006 provider-free with immutable query/follow monitors, explicit
lifecycle and baseline decisions, evidence-linked deterministic digests,
disabled-by-default delivery intents, safe legacy import and fresh public
runtime acceptance.

## Current State

Plans 0093 and 0116 are closed; WI-001/WI-002/WI-004 are `DONE`. The durable
monitor kernel and saved-query composition exist. Follow views, deterministic
digests, disabled delivery intents, safe import and complete public/runtime
acceptance remain for WI-006.

## Definition Of Done

All acceptance criteria pass at one reviewed joined checkpoint, exact runtime
and effect receipts are retained, canonical integration is recorded, and
WI-006 is reconciled to `DONE` with schedules and live delivery still disabled.

## Scope

- add backward-compatible discriminated follow-view capture over exact
  collection revisions, partitions, causes, versions, cutoff and coverage;
- expose create/read/list/revise/lifecycle/capture/evaluate/history and explicit
  accept/reject through one strict monitor application contract;
- render immutable run-bound digests with four change classes, denominators,
  omissions, coverage windows, byte bounds and evidence links;
- persist versioned delivery preferences plus immutable intent/attempt/receipt
  ledgers; production prepares/reads only, while an injected recording sink
  proves idempotency, retry and explicit child resend;
- import only explicitly supplied legacy-topic exports into disabled saved
  queries/monitors with source locator and unmapped-field reports;
- join strict CLI/HTTP/MCP parity and prove restart/teardown in an isolated
  packaged cache-only runtime.

## Non-Goals

No background schedule, provider acquisition, generated/model summary, channel
adapter, real notification, installed migration, retention purge, implicit
baseline acceptance or issue/release/deployment mutation.

## Acceptance Criteria

1. Existing saved-query bytes/replay remain compatible; query and follow views
   freeze exact authorized identities and deduplicate without losing causes.
2. Identical frozen inputs yield identical runs/digests across restart.
   Removal requires explicit tombstone/unavailability evidence; absence,
   truncation, provider failure or top-k drift never proves removal.
3. Only explicit race-safe acceptance advances a baseline. Partial/old-cutoff
   runs, rejection and render failure do not.
4. Every digest is bounded, denominator-aware and cites current/prior immutable
   evidence as applicable; cross-partition probes reveal nothing.
5. Default runtime refuses send. Recording-sink success has one effect per key;
   failure keeps its key and explicit resend creates a reason-linked child.
6. Legacy import is disabled, idempotent and credential-free.
7. Fresh CLI/HTTP/MCP covers the complete workflow and denial cases across
   restart, exact-owner teardown and declared-ledger-only mutations.
8. Focused/full Python, Go/vet, generation, package/lifecycle, reproducibility,
   audit and diff validation pass at the reviewed joined head.

## Ownership And Topology

One top-level owner, no children, at most two implementation attempts, one
independent joined review and one closed-world remediation. Lane-owned modules:
`service_monitor_contracts.py`, `service_monitors.py`,
`service_monitor_views.py`, new `service_monitor_follow_views.py`,
`service_monitor_application.py`, `service_monitor_digests.py`,
`service_monitor_delivery.py`, `service_monitor_import.py`, their focused
tests/fixture, `monitor_dogfood.py`, its test/receipt, and this plan.
Coordinator serializes app/client/HTTP/CLI/MCP, generated artifacts, versions,
docs and authority projections.

## Stop Rules

Stop for upstream follow/search semantic changes, missing trustworthy revision,
coverage or removal evidence, unsafe scope checks, unbounded capture, corrupt
immutable receipts, ambiguous delivery effects, teardown failure, shared-file
conflict or any excluded external effect.

## Next Action

Integrate registration, publish exact isolated custody and assign one owner.
The first coherent source checkpoint must include a real frozen follow-to-
digest tracer. Reviewed canonical integration may move WI-006 to `DONE`.

### Checkpoint P0121-C01 | 2026-09-14

Plan version: 1

State transition: `unplanned -> PLANNED`.

Progress classification: `blocker_reduction`; follow composition, digest,
disabled intent and runtime closure form one coherent acceptance packet.

Authority classification: `inherited_authority` for registration and later
provider-free work; every Non-Goal remains a `human_gate` effect.

Subagent status and reconciliation: `joined`; one read-only planner completed.
Implementation owner remains unassigned pending exact custody.

Next action: integrate registration and publish a plan-only activation ref.

### Checkpoint P0121-C02 | 2026-09-14

Plan version: 1

State transition: `PLANNED -> OPEN`.

Progress classification: `implementation_ready`; exact isolated custody is
accepted from canonical registration merge `e0fab676`.

Authority classification:

- `inherited_authority` covers the registered provider-free write set only;
- every external-effect gate remains held.

Subagent status and reconciliation: `assigned`; `/root/wave4_wi003_plan`, one
owner, no children. Implementation waits for activation reconciliation.

Next action: publish this plan-only checkpoint and return exact custody.

### Checkpoint P0121-C03 | 2026-09-14

Plan version: 1

State transition: `implementation_ready -> first_tracer_green`; plan remains OPEN.

Progress classification: `outcome_progress`; a real immutable collection revision
and stored-post search now feed frozen follow capture, monitor evaluation,
deterministic evidence-linked digest, explicit acceptance and restart readback.

Authority classification: `inherited_authority`, restricted to registered
monitor source/tests and this plan. Base and upstream were clean/equal at
`a660a51cc0177cea258ddda94e5df215b1ac2e8e`. No shared transport, authority,
provider, model, browser, installed state, schedule or delivery changes occurred.

Execution owner: `/root/wave4_wi003_plan`; requested route gpt-6-astra/high,
effective model and effort runtime-unknown. One implementation attempt is in
progress, incremental TDD; no children. TDD/deep-module design and CodeGraph
skills guided the command seam. The lane has no CodeGraph index; existing
canonical graph context and direct source reads were used without indexing.

Validation evidence: the first test failed with the missing application module
before implementation; fixture constraint corrections were retained as setup
failures. Focused monitor/application/view suite passes: 32 tests in 4.96 s.
Monitor-local schema v2 widens the view discriminator while copying old
payload bytes/hashes and checking only monitor foreign keys; shared corpus
schema is unchanged. Full compatibility, lifecycle/privacy, delivery/import,
public transport and packaged runtime acceptance remain unproven.

Next action: publish this coherent tracer checkpoint, then complete the
registered lifecycle/privacy, delivery/import and probe behaviors. Coordinator
joins only against published source; this checkpoint is not WI-006 acceptance.

### Checkpoint P0121-C04 | 2026-09-14

Plan version: 1

State transition: `first_tracer_green -> product_source_green`; plan remains OPEN.

Progress classification: `outcome_progress`; scoped monitor names, bounded
lifecycle/list/history, source-archive pause, durable baseline evidence references,
disabled preferences/intents, recording-sink retry/resend, ambiguous-effect
lockout and export-only legacy import now pass their provider-free behaviors.

Authority classification: `inherited_authority`; no shared transports,
source/follow adapters, providers/models/browsers, installed state, schedules,
real delivery or authority projections changed. One implementation attempt
continues; no children or independent review was started. Effective runtime
model/effort remain unknown.

Evidence: incremental RED tests demonstrated missing lifecycle/import/delivery
behavior, globally colliding monitor names and missing prior evidence after an
accepted absent view; each is now GREEN. Existing query snapshots keep v1 wire
bytes. Focused monitor/search/collection tier: 122 passed in 17.20 seconds.
Ruff import fixes and formatting affected only new lane files. Full-suite,
generated/package and public runtime gates remain coordinator-join dependent.

Shared contract: `MonitorApplication(db_path, search_backend, *,
access_partitions, collection_reader=None, clock=None).command(payload)` takes
exactly `{profile_id, command}`. `COMMAND_FIELDS` exports every strict action's
required keys. The collection reader needs only `get_spec` and
`get_spec_revision`; it receives no enqueue/schedule authority. The public
`send` action always raises `MonitorKernelError(INVALID_LIFECYCLE,
"delivery disabled")`; fixture dispatch accepts only an explicit in-memory
`RecordingSink`. Return projections use caller-facing partition-scoped monitor
names while durable identities are namespaced internally. Every command is
bounded to 64 KiB input and 124 KiB output; captures freeze at 32 KiB evidence,
100 pages, 1,000 items and a cooperative 10-second deadline.

Next action: publish this source checkpoint for coordinator CLI/HTTP/MCP joins;
finish probe integrity tests and source regression checks. No WI-006 DONE or
packaged-runtime claim is made from this source checkpoint.

### Checkpoint P0121-C05 | 2026-09-14

Plan version: 1

State transition: `product_source_green -> probe_ready_for_shared_join`.

Progress classification: `outcome_progress`; the repo-only monitor probe now
checks real query/follow workflows, strict HTTP/MCP parity and denial cases,
restart CLI readback, frozen intent replay, exact runtime/manifest/process
identity, teardown and a whole non-monitor database mutation census.

Authority classification:

- `inherited_authority` for lane source/tests/probe, this append-only plan,
  safe local validation and branch publication;
- `human_gate` remains for providers/models/browsers, installed/live data,
  schedules, real delivery, release/deployment and issue mutation.

Execution owner: `/root/wave4_wi003_plan`; one implementation attempt, no
children. Effective runtime model/effort remain unknown. No independent
review has been launched from this lane.

Validation evidence:

- focused monitor/search/collection suite at source checkpoint C04: 122
  passed in 17.20 seconds;
- explicit synthetic stored tombstone rendering cites prior immutable
  evidence, and partial capture/render failure cannot advance the baseline;
  these three digest tests pass in 1.31 seconds;
- probe integrity/fixture suite: 3 passed, 1 skipped in 0.24 seconds. The skip
  explicitly identifies the absent coordinator monitor transport join;
- one broad diagnostic Python run completed: 3,082 passed, 8 skipped,
  14 subtests passed, 13 failed in 194.06 seconds. Eleven failures are the
  unchanged shared runtime-manifest/package/lifecycle gate; one hotfix fixture
  expects service 0.3.117 while the current base reports 0.3.118; one plan
  audit failure was this lane's inline C04 authority label. This C05 uses
  the auditor-required list form and will be validated before publication;
- probe source was authored during that broad diagnostic run, so it is not
  immutable-head final acceptance. No full-suite pass is claimed; the
  coordinator must repeat it on the joined, regenerated source;
- no packaged development runtime was started, no runtime receipt is invented,
  and no installed runtime/database or provider was touched by the probe.

Exact joins: existing constructor and COMMAND_FIELDS at C04 remain frozen.
CLI is `service.py monitor --socket S --profile P --input FILE`, HTTP is
`POST /v1/monitor`, client is `monitor(command, *, profile_id="default")`,
MCP tool is `monitor` with exact `{profile_id, command}`. Source/configuration
reader needs only get_spec/get_spec_revision, never collection issuance.

Remaining acceptance criteria: coordinator shared joins/discovery, manifest
and version reconciliation, fresh public/runtime proof, independent joined
review, full suite/package/reproducibility checks and canonical integration.
The probe is ready, not an executed runtime proof. WI-006 remains unfinished.

Next action: validate and publish this clean checkpoint, then hand the exact
probe/source contract to coordinator integration. Do not manufacture a passing
receipt or edit shared transports to remove the guarded skip from this lane.

### Checkpoint P0121-C06 | 2026-09-14

Plan version: 1

State transition: `probe_ready_for_shared_join -> lane_source_accepted`;
Plan 0121 remains OPEN for joined acceptance, not independently CLOSED.

Progress classification: `outcome_progress`; registered lane source and the
reproducible probe are ready for coordinator joins and independent review.

Authority classification:

- `inherited_authority` for provider-free source/test verification and clean
  owned-fork branch publication;
- `human_gate` for all excluded effects; no deployment, provider/model/browser,
  installed/live state, scheduler or external delivery authority is inferred.

Validation evidence:

- final focused monitor/probe/search/collection tier before the last census
  regression: 127 passed, 1 guarded transport skip in 15.59 seconds;
- added RED/GREEN census regression proving undeclared `service_monitor_*`
  tables are not silently ignored. The probe now allows exactly eleven named
  monitor ledgers; its final isolated suite is 4 passed, 1 guarded skip in
  0.24 seconds;
- Go `test ./...` and `vet ./...` passed against the unchanged lane-base Go
  adapter, not the still-pending new monitor transport;
- Ruff checks/formatting, repo-native plan authority audit and diff hygiene
  pass. C04's owned plan-format defect is resolved by C05/C06 list syntax;
- C05 retains all thirteen broad diagnostic failures. Shared manifest,
  hotfix-version expectation and joined full-suite checks remain coordinator
  responsibilities. No packaged runtime proof or passing receipt is claimed.

Subagent status and reconciliation: one existing campaign worker, no children;
requested gpt-6-astra/high, effective model/effort runtime-unknown. One
incremental implementation attempt; independent joined review and any accepted
closed-world remediation remain coordinator-owned.

Remaining acceptance criteria: public app/client/HTTP/CLI/MCP and discovery
joins, current generated manifest/versions, fresh packaged runtime probe and
exact-owner teardown, reviewed full-suite/reproducibility acceptance and
canonical integration. WI-006 is acceptance-eligible once these prove all
criteria; it is not DONE from this lane-source checkpoint alone.

Next action: commit/push the exact source checkpoint, verify remote equality
and cleanliness, and return concrete shared join requirements plus probe
locator. Preserve the lane worktree/ref; no cleanup or forge issue action.

### Checkpoint P0121-C07 | 2026-09-14

Plan version: 1

State transition: `lane_source_accepted -> joined_runtime_acceptance_ready`.

Progress classification: `blocker_reduction`; exact shared service0.3.119/MCP4.0.7
join `4204da5f017bd2352c4c53b95200250bf009ce0c` merged without conflicts as
`6de679a2fcdb0683d74ca34104e380b3a103254b`. No shared file was independently
edited by this lane. Coordinator clock fix
`c21a729b5be4a9abd87427259d1be02a06a13503` was cherry-picked on explicit
coordinator direction as `4e71f45b`.

Authority classification:

- `inherited_authority` for this exact join, focused/package checks and one
  guarded packaged monitor dogfood in fresh isolated synthetic roots;
- `human_gate` still applies to every provider/model/browser, live/installed
  state, schedule or real delivery effect.

Validation evidence and retained failures:

- initial joined focused tier: 46 passed, 1 failed because the in-process
  fixture omitted the read-only collection authority that packaged service.py
  supplies. The lane-owned fixture now injects build_collection_read_authority;
- the next focused reproducer correctly exposed the shared datetime-versus-
  UTC-string monitor clock mismatch, fixed by the coordinator commit above;
- package/lifecycle tests passed: 18 tests in 29.82 seconds before the clock
  correction. Two pre-correction service builds were byte-identical at SHA256
  `36d8301de965c7f0d38e74718db816a35b3808413e00f49e08a9465eecfc7103`;
- the single packaged dogfood attempt has not yet started; its artifact must
  be rebuilt after the accepted clock fix and bound to a clean source commit.

Subagent status: existing lane owner, no children; effective model/effort
runtime-unknown. Runtime evidence will be retained truthfully whether the
single allowed attempt passes or fails. Independent joined review and final
canonical integration remain coordinator-owned.

Next action: publish the clean corrected fixture checkpoint, build the exact
artifact, execute the packaged probe once, preserve the receipt and run final
focused/full/package/audit acceptance without widening effect authority.

### Checkpoint P0121-C08 | 2026-09-14

Plan version: 1

State transition: `joined_runtime_acceptance_ready -> acceptance_eligible`;
plan remains OPEN pending independent joined review and canonical integration.

Progress classification: `outcome_progress`; all executable acceptance tiers
pass on clean published source `283da4dc95caebe11480c44d24c705a5e692e572`.
This checkpoint adds only evidence custody and this append-only progress record.

Authority classification:

- `inherited_authority` covered exactly one guarded packaged monitor probe,
  focused/full/package/audit checks, receipt retention and lane publication;
- `human_gate` remains held for providers, models, browsers, live/installed
  state, schedules, real delivery, issues, release and deployment.

Runtime evidence:

- The single packaged probe passed; it was not retried. Exact retained receipt:
  `docs/dev/notes/0121-2026-09-14-monitor-product-closeout-receipt.json`, SHA256
  `58ab6130f4e13dc26485a2c68a4d837f843ec368d9d98ff743d28154aff5fe96`.
- Artifact `last30days-service-0.3.119.tar.gz` SHA256
  `6ba2ec626ace8cd7a67b770d01d13dd628e7c9f81720736181e831e4ebece586`;
  independently rebuilt bytes match exactly. Artifact and original receipt
  remain under `/tmp/wi006-plan0121-ULyDNG`; the retained JSON binds source,
  artifact, manifest, MCP binary, runtime owner identities and both cycles.
- Both cycles reported service0.3.119/MCP4.0.7 compatible; query/follow digest,
  explicit baseline, disabled intent, strict denials and CLI/HTTP/MCP parity
  passed. Restart preserved immutable digest/intent readback. Non-monitor
  ledgers retained digest
  `24340d06b54175848db8893e6146f84170ebedc2d2351340a9f03422f1858414`.
- Final controller state is `absent`, both down receipts are `stopped`, and
  owned-process census is empty. A fresh OS `ps` readback independently found
  none of service PIDs 2948984/2949286 or MCP PIDs 2949080/2949289 present.
  No installed runtime was changed and no external delivery occurred.

Validation on the joined source checkpoint:

- Focused monitor/probe tier: 47 passed in 10.85 seconds, including the fresh
  HTTP/MCP case; no guarded transport skip remains.
- Full safe Python suite: 3102 passed, 8 skipped, 14 subtests passed in 219.10
  seconds (`uv run pytest -q -o addopts='' --tb=short`). Source stayed unchanged
  throughout this acceptance run; earlier diagnostic failures remain above.
- Explicit package/lifecycle tier: 18 passed in 30.83 seconds.
- Go `test ./...`, `vet ./...` and `generate ./...` passed; generated files
  produced no tracked diff.
- Cached local Ruff0.16.7 checked all new lane modules and focused tests with
  no findings. `uv run ruff` initially found no lane-installed executable;
  using the existing local cached binary needed no install or network access.
- Repo-native authority audit passed with zero issues; active planning audit
  returned `ok=true`, no problems and no unused baseline findings. Diff
  whitespace checks passed.

Subagent status and reconciliation: `/root/wave4_wi003_plan`, one owner, no
children. Requested gpt-6-astra/high; effective model/effort runtime-unknown.
One incremental implementation attempt and bounded joined corrections only.
No code joins remain identified. Independent review, canonical integration,
WI-006/P40 authority reconciliation and final plan closure are coordinator-owned.

Next action: publish this evidence-only checkpoint clean and remote-equal;
coordinator reviews and merges exact custody, then marks WI-006 DONE only if
all acceptance criteria remain satisfied. Preserve this branch/worktree and
all runtime evidence; no cleanup or external-effect authority is implied.
