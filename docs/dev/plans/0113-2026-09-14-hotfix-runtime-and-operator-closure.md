# Plan 0113 | Hotfix Runtime And Operator Closure

State: CLOSED
Lane: P38
Work item: WI-007
Branch: feat/hotfix-runtime-drill-v1
Target: main
Integration: merge
Roadmap: P38
Plan version: 1
Date: 2026-09-14
Execution owner: /root/wi007_packet3_planning
Coordination owner: /root
Requested model route: gpt-6-astra, high reasoning
Effective runtime model: unknown; not reported by runtime
Effective runtime reasoning: unknown; not reported by runtime

## Objective

Complete WI-007 provider-free by composing the reproducible builder and
installer into a disposable release/rollback drill, adding deterministic
preflight/report operator tooling, and proving the reserved real slot returns
to dormant without provisioning operational staging.

## Current State

Provider-free control and Git drills are integrated through PR 79. WI-001
provides an isolated development-runtime pattern, not operational staging.
Builder/installer tests cover low-level lifecycle recovery, but no reusable
hotfix drill binds their artifact, database, process, and receipt identities to
WI-007's state machine.

Implementation is published at `6b278fce0debf9cd2ebb6b6253feade5c31fd773`.
The fresh complete drill passed against exact canonical source
`5471e928b1f4c7867ea15de1d4e203b3315bb6e4`; durable receipt 0127 binds source,
tooling, artifacts, all five outcomes, and cleanup. Focused/comprehensive tests
pass. Coordinator review/integration, three known shared RUNBOOK links, and the
CONFIGURATION.md projection remain before repo-local work-item closeout.

## Scope

- add a repo-only runtime drill using owned temporary roots, synthetic database,
  fake user manager, private sockets, allowlisted environment, and exact
  process ownership;
- build fixed source twice and bind artifact/manifest/source identity without
  changing fixture versions or repository release metadata;
- exercise successful upgrade, failed-upgrade restoration, deliberate rollback,
  rollback-forward, and a truthful terminal recovery failure when needed;
- compose results into existing hotfix receipts without treating simulated Git,
  staging, or authorization as operational proof;
- add read-only preflight/report plus explicit disposable drill commands and
  operator guidance; run one fresh complete provider-free drill and retain its
  bounded receipt bundle.

## Non-Goals

No real incident/hotfix branch, installed user service, operational staging,
production, provider/browser, credentials, release metadata/tag/publication,
GitHub issue, deployment, or rollback effect.

## Acceptance Criteria

1. Preflight rejects dirty/stale source, manifest drift, foreign/redirected
   roots, ambient credentials/config, real manager paths, and identity mismatch
   before mutation.
2. Fixed-input builds are byte-identical and bind to the actual clean source;
   fixture versions never edit release metadata.
3. Installer readbacks prove exact releases, schema, manifest, contract,
   readiness, sentinel restoration, and retained raw failed attempts.
4. Each scenario permits at most one upgrade and one recovery rollback;
   rollback-forward is separately declared rather than an automatic retry.
5. Teardown verifies process owner/birth identity, fresh OS census finds no
   fixture process, and exact cleanup preserves foreign sentinels.
6. Report validation preserves simulated-versus-operational distinctions and
   the final receipt maps every WI-007 criterion with the real slot dormant.
7. Focused lifecycle/package/control tests, one fresh composed drill, full
   provider-free presubmit, authority audits, and diff checks pass.

## Execution Packet

- one top-level implementation owner, no children; two implementation attempts,
  one independent review, one closed-world remediation pass;
- lane-owned writes: new runtime drill/operator entrypoint, focused tests,
  operator doc, bounded receipt, and this plan; narrow existing hotfix module
  changes only when composition proves necessary;
- builder, installer, runtime controller, version/changelog, public contracts,
  generated catalogs, and manifest are reference-only unless a blocker is
  returned to the coordinator; authority projections are coordinator-only;
- terminal condition: published provider-free acceptance making WI-007 eligible
  for repo-local DONE, or one exact blocker. The production hotfix slot is never
  activated by this packet.

## Definition Of Done

All seven criteria pass at one published checkpoint, the durable receipt is
independently verifiable, and no operational staging or production claim is made.

## Current Checkpoint

### Checkpoint P0113-C01 | 2026-09-14

Plan version: 1

State transition: `planned -> activation_published`.

Progress classification: `blocker_reduction`; exact execution ownership and
recoverable branch custody are established. All seven implementation acceptance
criteria remain unproved by this activation.

Authority classification:

- `inherited_authority` from Plan 0107 and the coordinator's activation-only
  assignment covers reading current policy/evidence, editing only this plan,
  validating the document, committing, and publishing its assigned branch;
- implementation and all build/runtime execution are held until coordinator
  activation reconciliation and a separate resume instruction;
- every installed-service, operational-staging, production, provider/browser,
  credential, schedule, issue, release publication, deployment, and operational
  rollback effect remains outside this assignment.

Ownership and custody:

- execution owner: `/root/wi007_packet3_planning`; coordinator: `/root`;
- worktree: `/home/ecochran76/workspace.local/last30days-skill-wi007-v2`;
- branch: `feat/hotfix-runtime-drill-v1`; target: `main`; integration by
  coordinator-owned reviewed pull request to the owned public fork;
- exact activation base: `7f65c4285146e8d4dabd417617584fe7042a582f`;
- initial lane checkout is clean at that base. Canonical
  `/home/ecochran76/workspace.local/last30days-skill` owns clean `main`, equal
  to local `origin/main` and live owned-fork `refs/heads/main` at the same base;
- publication establishes `origin/feat/hotfix-runtime-drill-v1`; the exact
  checkpoint is the commit containing this activation, returned with verified
  live remote equality and clean status. No historical custody is changed.

Inputs, evidence, and overlaps:

- re-read current planning, Git/commit/integration, documentation, validation,
  goal, active-lane, subagent, work-item, operating-model, model-routing, and
  collaborative-workflow policies before activation;
- current Plan 0107, Plan 0113, and WI-007 preserve the provider-free boundary;
  the prior read-only audit inspected note 0122 and its JSON companion, closed
  Plan 0110, WI-001/Plan 0106/receipt 0126, and current builder/installer tests;
- WI-001 acceptance supplies development isolation, not operational staging.
  This activation makes no current production identity or runtime-health claim;
- this checkpoint writes only this plan. Prospective implementation owns
  repo-only hotfix drill/operator code, focused tests, operator guidance, and
  bounded receipts, with narrow existing hotfix-module changes when required;
- no expected implementation overlap with concurrent search/follows packets.
  Builder, installer, lane runtime, manifest, release metadata, public schemas,
  generated catalogs, and CI remain reference-only pending coordinator
  disposition of any demonstrated blocker; shared authority is coordinator-only;
- requested route remains `gpt-6-astra`, high reasoning for installer recovery,
  containment, and receipt-identity composition. Effective model and reasoning
  are unknown; no runtime override or child is requested;
- Graphiti discovery is skipped because exact current authorities and the
  completed bounded audit suffice. Graphiti write status: `not_written`.

Validation and next action:

- plan-authority audit passed: two active authority plans, zero issues;
  goal-only planning audit passed; this plan's filename, state, lane, and
  current-state checks passed; inspected one-file diff and `git diff --check`
  passed;
- active planning audit failed only on six shared-projection findings: each of
  Plans 0111, 0112, and 0113 is not wired in ROADMAP.md and RUNBOOK.md. These
  findings are reported to the coordinator for activation reconciliation;
  this plan-only assignment does not change those shared files or claim the
  active audit passed;
- no implementation tests, builds, installer commands, service starts/stops,
  providers, or operational checks run during activation;
- publish the one-file activation, verify local/upstream/live-remote equality,
  and return its exact SHA. Then wait for the coordinator to reconcile the
  activation and resume this same lane owner.

Stop condition: do not implement, build, run a fixture/runtime, mutate shared
authority, open a pull request, change issue state, or spawn children during
this activation. Stop on unexpected dirt, branch/base mismatch, or publication
divergence and return the exact evidence to the coordinator.

### Checkpoint P0113-C02 | 2026-09-14

Plan version: 1

State transition: `activation_published -> implementation_baseline_passed`.

Progress classification: `outcome_progress`; a real reproducible builder and
installer compose with the synthetic Unix service and exact-owned cleanup.

Authority classification:

- `inherited_authority`; coordinator resume permits the planned provider-free
  implementation, disposable builds/runtime tests, validation, and branch
  publication. Operational effects remain excluded.

Evidence and fixed bounds:

- TDD first red: missing preflight module; green: stale-source rejection test
  passed. Lifecycle tracer red: missing run interface; implementation then
  exposed absent native Python pidfd wrappers. The Linux syscall fallback
  follows WI-001's established approach. Fresh OS search found no residual
  fixture process after that failed attempt;
- added short socket-root preflight before resource creation. Current baseline:
  `uv run pytest tests/test_hotfix_runtime_drill.py -k baseline`: one passed,
  one deselected in 2.84s; measured wall 3.00s, peak RSS 39,512 KiB;
- source fixture uses two committed payloads (historical 0.3.116 and current
  0.3.117), without editing versions or release metadata. The builder creates
  two byte-identical candidate artifacts. The installer acts only inside
  the owned temporary fixture with an explicit fake manager;
- service/schema behavior is synthetic and labeled as such; these samples
  prove installer selection/restoration, not product migration correctness;
- freeze five scenarios: upgrade, failed-upgrade restoration, rollback,
  separately declared rollback-forward, terminal recovery failure. At most
  one upgrade per scenario; at most one recovery/backward rollback, with one
  explicit forward operation only in rollback-forward. No automatic retries;
- operation timeout 15s, builder timeout 30s, service readiness bound 1s,
  child teardown bound 3s; total drill ceiling 60s, focused suite 60s,
  selected lifecycle fallback 180s, comprehensive provider-free suite 600s.
  A breach retains evidence and ends that run without expanding its bounds;
- no children. Effective runtime model/reasoning remain unknown.

Next action: implement one recovery tracer at a time, then report/control
composition and focused negative tests. Preserve failed attempts and serialize
the fresh drill after a clean published source checkpoint.

### Checkpoint P0113-C03 | 2026-09-14

Plan version: 1

State transition: `implementation_baseline_passed -> implementation_validated`.

Progress classification: `outcome_progress`; five installer scenarios,
read-only preflight/report, synthetic controller replay, operator guidance,
and exact process/socket cleanup are implemented and validated.

Authority classification:

- `inherited_authority` for the resumed provider-free packet and publication;
- coordinator approved one proven installer exception: add optional
  `--skill-host-root PATH`, retaining default user-home behavior and changing
  only frozen-host entrypoint refresh. XDG roots alone could not contain the
  installer's unconditional user-home refresh. The fixture now passes its own
  private empty directory and never overrides HOME or CODEX_HOME;
- CONFIGURATION.md remains coordinator-owned because of Wave 2 overlap.
  Required projection: document `service/scripts/install.sh --skill-host-root
  PATH` as an optional absolute, owner-private, non-symlink directory scoping
  frozen host-entrypoint refresh only, defaulting to the existing user home.

Implementation and evidence:

- repo-only runtime/controller adapter, synthetic Unix service/manager client,
  and operator command are under `dev/last30days/scripts/hotfix_*`; operator
  guidance is `docs/agents/hotfix-operator.md`;
- tests clone source Git with `--no-hardlinks --no-checkout`, retain the exact
  existing commits, and checkout the clone's exact origin/main. This supersedes
  the initial synthetic re-commit test fixture; acceptance never attributes an
  artifact to a synthetic Git commit;
- preflight rejects `.git` pointer files, common-directory redirects, object
  alternates, metadata symlinks, included configuration, dirty/stale source,
  and ambient credential/configuration keys before building;
- reports validate exact artifact/source/build hashes, expected contract,
  manifest, version, synthetic schema, ready state, database content digests,
  sentinels, process/socket birth identity, and replayed drill-only controls;
- focused hotfix selection: 63 passed in 33.07s, wall 33.22s, peak RSS
  42,320 KiB. One serial run, no retries; under the 60s focused budget;
- comprehensive provider-free suite: `timeout 600 uv run pytest`: 2,979 passed,
  7 expected skips, 11 subtests passed in 157.04s; measured wall 156.95s,
  peak RSS 186,720 KiB. One serial run, no retries or budget breach. Existing
  lifecycle/package tests ran in this comprehensive selection;
- source seam before/after evidence: baseline installer at `5471e928` rejects
  an explicit host root with a two-argument TypeError. Current tests prove
  explicit-root containment, default behavior compatibility, and rejection of
  relative, foreign-owner, symlinked, or shared-writable roots;
- Ruff check/format, Python compilation, `bash -n service/scripts/install.sh`,
  and diff checks passed. Plan-authority audit passed with five active plans
  and zero issues; goal-only planning audit passed;
- active planning audit retains exactly three shared findings: Plans 0111,
  0112, and 0113 are not wired in RUNBOOK.md. Coordinator has been notified and
  owns their reconciliation; no all-audits-passed claim is made;
- subagent status: no children; this lane ran the recorded validation itself.
  Effective model and reasoning remain unknown. Graphiti: `not_written`.

Remaining acceptance: publish the tooling checkpoint, run one fresh complete
drill against exact clean source, retain its bounded receipt, and return the
clean published result for coordinator review/integration and shared-doc joins.

### Checkpoint P0113-C04 | 2026-09-14

Plan version: 1

State transition: `implementation_validated -> integration_ready`.

Progress classification: `outcome_progress`; one fresh complete provider-free
drill now has durable, independently checkable source and runtime receipts.

Authority classification:

- `inherited_authority` for the exact fresh disposable drill, its owned cleanup,
  receipt, plan update, and branch publication;
- installed service, operational staging, production, providers, browsers,
  credentials, schedules, releases, real incident activation, deployment,
  operational rollback, and issue mutations remain excluded.

Fresh receipt and measurement:

- receipt: `docs/dev/notes/0127-2026-09-14-wi007-runtime-drill-receipt.json`,
  98,758 bytes; content digest
  `5ee59e1630211c9510bff8279f0d3824a689c267450d978c2c8e6290daf24ae6`;
- tooling commit `6b278fce0debf9cd2ebb6b6253feade5c31fd773`, clean and
  remote-equal before the fresh run; per-file hashes are retained in the receipt;
- clean standalone source clone retained exact current owned-fork main
  `5471e928b1f4c7867ea15de1d4e203b3315bb6e4`, verified by live remote readback
  before cloning; previous source was exact ancestor
  `94d4852fabd56e09f399ec77816ff25a690e294a`. No source was re-committed or
  assigned a synthetic source identity;
- current artifact 0.3.117, SHA-256
  `81a3fb2af355c1e7b15343441ad09a59db3ddb40eff0a7b56a96a58ac3a95c80`,
  built twice identically; manifest
  `a05bc0c480ecdde3b49cb7c647992b4215d2b1b14b8643b9a3bf6fb791cde7ea`;
- previous artifact 0.3.116, SHA-256
  `64b1b2a2d99260c4411762c656a0d670e7e1278a9406a4b9433391247b0c37a0`;
- measured drill 11.4195s; complete CLI wall 12.23s, peak RSS 28,864 KiB;
  one run, no retries, no budget breach;
- outcomes: upgrade verified, failed upgrade restored, backward rollback
  restored, explicit rollback-forward verified, recovery failure blocked.
  Every raw installer result and original failed-attempt outcome is retained;
- report command passed with `done_eligible: true`, `mode: drill`, and
  `operational_authority: false`. This is receipt eligibility for coordinator
  disposition, not an automatic work-item or deployment authorization.

Cleanup and current-state proof:

- all 14 fixture process PID/start identities were reaped; receipt cleanup
  records zero residual processes. A subsequent fresh OS command-line census
  also found no fixture process;
- fixture `/tmp/wi007-drill-_ungd9y1/wi007-1nzic09x` and its parent are absent;
  disposable Git cleanup is verified in the receipt;
- the exact source clone `/tmp/wi007-source-6ta1iJ` was checked clean at the
  recorded source commit and removed without force. It is reproducible from
  retained Git refs; the durable receipt remains available;
- canonical worktree stayed clean on main at `5471e928`, equal to origin/main.
  No installed database or live production-health readback is claimed;
- no children or unknown delegated test results. Effective model/reasoning
  remain unknown. Graphiti: `not_written`.

Acceptance mapping and remaining coordinator gate:

- criteria 1-6 have focused negative tests and fresh receipt evidence for
  source/root isolation, reproducibility, exact lifecycle observations,
  bounded attempts, exact teardown, and synthetic control/report separation;
- criterion 7 has the focused/comprehensive results at C03 and the fresh run
  above. Plan-authority/goal audits pass; three known RUNBOOK-link findings
  remain coordinator-owned, as does the approved configuration projection;
- synthetic schemas and services prove installer recovery behavior only;
  no operational staging, real incident handling, or live migration acceptance
  is inferred. Review/integration and truthful shared authority reconciliation
  are still required before WI-007 is marked DONE locally;
- next action: publish this receipt checkpoint and return exact SHA, clean
  remote equality, test/measurement evidence, and coordinator follow-ups.
  Stop before PR creation; preserve the dormant production slot.

### Checkpoint P0113-C05 | 2026-09-14

Plan version: 1

State transition: `OPEN -> CLOSED`; WI-007 `IN_PROGRESS -> DONE`.

Reviewed PR 83 merged validated integration head `b4e3123f` into canonical
main as `5aec73245fa699b50ee74b4578cc891ffd239f0c`. Source checkpoint
`d25f9df441aa6e92af9827f56fb3b75ffbbb363c` and retained receipt digest
`5ee59e1630211c9510bff8279f0d3824a689c267450d978c2c8e6290daf24ae6`
passed independent joined review and full provider-free acceptance. The real
slot remains dormant with zero resources; no operational authority is granted.
