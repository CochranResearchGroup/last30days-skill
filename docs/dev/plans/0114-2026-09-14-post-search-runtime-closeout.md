# Plan 0114 | Post Search Runtime Closeout Packet 4

State: OPEN
Lane: P33
Work item: WI-002
Branch: feat/post-search-runtime-closeout-v1
Target: main
Integration: merge
Roadmap: P33
Plan version: 1
Date: 2026-09-14
Execution owner: /root/next_search_qa_plan
Coordination owner: /root
Requested model route: gpt-5.6-terra, medium reasoning
Effective runtime model: unknown (not reported by runtime)
Effective reasoning effort: unknown (not reported by runtime)

## Objective

Close WI-002 provider-free by proving the integrated stored-post search product
through a fresh MCP client against an exact versioned isolated development
runtime, with stable HTTP/MCP behavior, immutable evidence, and exact teardown.

## Current State

Plans 0108 and 0111 are integrated. Search already supports both storage
families, full filters, revisions, deduplication, deterministic hybrid ranking,
bounded pagination, HTTP/MCP parity fixtures, and a frozen 10,000-post
performance sample. Remaining acceptance is versioned isolated-runtime and
fresh-client product proof, not another ranking redesign.

Activation custody is accepted at P0114-C01. The coordinator integrated that
projection at `c4251dc12c905e513c9f37119b3442382741f31e` and resumed this owner
for the bounded implementation and isolated-runtime acceptance. Source and
exact-runtime acceptance pass at C03, bound to `68279438`; independent review,
coordinator integration and repo-local WI-002 closeout remain outstanding.

## Scope

- add a repo-only search dogfood probe reusable against an isolated runtime;
- prove fresh MCP discovery and typed HTTP/MCP equivalence across both stores;
- exercise filters, revisions, dedupe, empty/malformed/partition behavior,
  retained pagination, publication, restart-stale cursors, and read-only state;
- bind runtime artifact, source commit, schema, manifest, and contract digests;
- retain a bounded acceptance receipt and finish search guidance if needed.

## Non-Goals

No ranking tuning, new embedding provider, live acquisition, browser, installed
service, staging, production, release publication, schedule, issue mutation, or
WI-003 question transport.

## Acceptance Criteria

1. Fresh MCP discovery exposes `search_posts` against the exact runtime build.
2. HTTP and MCP return equivalent stable evidence across both storage families.
3. Full filters, current/all revisions, dedupe, empty/malformed requests, and
   access partitions pass at the public boundary.
4. Pagination survives publication and fails `cursor_stale` after restart.
5. Corpus, acquisition, and schedule state are unchanged by every probe.
6. Runtime identity and teardown receipts prove the exact artifact/source and
   an empty owned-process census.
7. Focused, package, full Python, Go test/vet, audits, and diff checks pass.

## Ownership And Topology

One top-level implementation owner, no children, at most two implementation
attempts, one independent review, and one closed-world remediation. Lane writes
are a repo-only search probe, focused acceptance fixtures/tests, branch-local
plan, and narrow search guidance. Catalogs, manifests, version metadata, shared
authority, and integration remain coordinator-owned.

## Stop Rules

Stop on ambiguous runtime/process custody, source or artifact mismatch, shared
transport changes required for WI-003, cursor semantics drift, provider/live
effects, or a need to rerun the frozen performance experiment without a
demonstrated invalidation.

## Definition Of Done

All seven criteria pass at a reviewed integrated checkpoint and WI-002 is
truthfully eligible for `DONE` without claiming installed or live acceptance.

## Current Checkpoint

### Checkpoint P0114-C01 | 2026-09-14

Plan version: 1

State transition: `PLANNED -> OPEN`; custody advances to
`activation_published`, with implementation held.

Progress classification: `hardening`; this checkpoint records ownership and
publication custody, not product or runtime acceptance.

Authority classification:

- `inherited_authority` under Plan 0107 and the coordinator's activation-only
  assignment covers this plan alone, deterministic plan/diff validation, one
  coherent commit, and publication to the exact owned-fork branch;
- accountable human owner: repository operator; execution owner:
  `/root/next_search_qa_plan`; coordination owner: `/root`;
- no implementation, fixture build, benchmark, development runtime, provider,
  browser, installed runtime, schedule, staging, production, release, issue,
  pull-request, other-file, or durable-memory mutation is assigned here.

Custody and base evidence:

- assigned worktree:
  `/home/ecochran76/workspace.local/last30days-skill-wi002-v4`;
- branch: `feat/post-search-runtime-closeout-v1`;
- exact clean activation base:
  `bf12c730eaa592cf627311aeef36d06810a2e83c`;
- fresh `git ls-remote --heads origin main
  feat/post-search-runtime-closeout-v1` returned that exact `main` base and no
  existing remote activation branch;
- `origin` resolves to `CochranResearchGroup/last30days-skill`; upstream push is
  disabled. Publication targets only
  `refs/heads/feat/post-search-runtime-closeout-v1`;
- the canonical worktree remains clean on `main` at the exact base above;
  default-branch custody is unchanged.

Inputs, model, and topology:

- this plan, Plan 0107, WI-002, architecture note 0117, integrated Plans
  0108/0111, and the accepted WI-001 controller define the next packet;
- AGENTS.md and planning, documentation, Git/worktree, commit/publication,
  validation/closeout, work-item, multi-session, model-routing, and
  collaborative-workflow policies were reread for activation;
- requested implementation route remains `gpt-5.6-terra`, medium reasoning;
  effective runtime model and reasoning are unknown, not inferred from this
  owner's name or the requested route;
- one assigned owner under the campaign's one-level topology, no children;
  two implementation attempts, one broad independent review, and one
  closed-world remediation remain the packet bounds. Activation consumes no
  implementation attempt;
- shared transports for WI-003, generated catalogs, manifests, version
  metadata, work-item/lane projections, roadmap/runbook, and integration remain
  coordinator-owned. Future runtime acceptance requires exact controller and
  artifact custody under the implementation assignment.

Validation evidence and publication boundary:

- the pre-edit plan-authority audit passed with zero findings and two active
  plans in the existing canonical projection;
- post-edit `python3 dev/last30days/scripts/audit_plan_authority.py` passed
  with zero findings against the existing canonical projection; the new lane
  activation projection remains coordinator-owned. `git diff --check` passed,
  and direct diff inspection confirmed that only this plan changed;
- post-publication readback must prove a clean worktree and equality of HEAD,
  the configured upstream, and the live owned-fork branch. The exact publication
  SHA is reported from Git, not embedded into its own commit;
- product tests, packages, benchmarks, and runtimes are unrun in this
  activation; none of the seven product criteria is newly claimed satisfied.

Graphiti status: `skip`; current repository authorities and the preceding
read-only planning audit suffice. No durable-memory write is assigned.

Stop and next action:

- stop after reporting the exact published checkpoint and custody validation;
- coordinator reconciles this activation into canonical authority before
  resuming the same owner on the implementation packet;
- on resume, re-anchor the assigned worktree, exact remote checkpoint, current
  policies, and shared-surface assignment. Stop on custody mismatch or newly
  conflicting ownership; do not infer implementation or runtime activation
  from publication alone.

### Checkpoint P0114-C02 | 2026-09-14

Plan version: 1

State transition: `activation_published -> source_probe_ready`; plan remains
`OPEN` pending isolated-runtime evidence, independent review and integration.

Progress classification: `outcome_progress`; one reusable repo-only probe now
crosses typed HTTP and a freshly built MCP process over 19 fixture cases,
malformed requests, sort modes, partition/cursor changes and publication.

Authority classification:

- `inherited_authority` under Plan 0107 and the coordinator's implementation
  continuation covers the repo-only probe/fixtures/docs, this plan, safe
  validation, exact WI-001 isolated-runtime acceptance, receipts, and branch
  publication;
- generated artifacts, runtime manifest, version metadata, shared transport,
  roadmap/runbook, work-item/lane projections and PR integration remain
  coordinator-owned; no provider, browser, installed runtime, schedule, staging,
  production, release publication or issue effect is permitted.

Custody and implementation evidence:

- fetched `origin/main` and fast-forwarded the assigned branch to exact
  `c4251dc12c905e513c9f37119b3442382741f31e`; Git verifies activation
  `81cbfc09b197b8cde325e468e79d19115d4fc4fb` remains in ancestry;
- `dev/last30days/scripts/post_search_dogfood.py` reuses existing synthetic
  fixtures and the WI-001 controller without changing packaged product source;
- it refuses existing lane state, builds the MCP adapter with offline Go
  dependency resolution, supplies a private credential-free MCP environment,
  compares complete HTTP/MCP responses except request ID and generated time,
  and checks the whole logical database digest around read-only probes;
- one explicit synthetic publication has separate before/after digests and
  proves pinned traversal; it is never counted as a read-only search mutation;
- the runtime bound is exactly two start/stop cycles of one unique isolated
  identity, sequentially, to prove restart-stale cursors. Each MCP process is
  terminated and reaped; final OS census includes both owned process sessions;
- source checks first failed because the probe was absent, then passed with
  the implementation. The probe also detects deliberately forged evidence
  parity, refuses existing corpus seeding and detects an owned OS session;
- 69 focused search/MCP/controller/package tests passed. Go tests and vet pass;
  focused Ruff and patch checks pass after import/format cleanup. Comprehensive
  Python validation is running and is not yet claimed passed;
- two fixed-epoch service `0.3.117` builds are byte-identical at
  `a103624e7aa64a86513c7d4c34c5c10152a9a0c0a8785e9f5fd86730a4ec2a44`;
  no manifest/catalog/version changes were needed. Exact-runtime execution
  waits for this clean source checkpoint.

Model/topology remain unchanged: requested `gpt-5.6-terra` / medium, effective
configuration unknown, one owner, no children. One implementation attempt is
in progress; no broad independent review or remediation has been consumed.

Next action: commit this source checkpoint, verify its clean custody, rebuild
the exact artifact, exercise the isolated runtime, retain its raw receipt and
record the final validation/teardown outcome. Any concrete transport or manifest
blocker returns to the coordinator without widening the write set.

### Checkpoint P0114-C03 | 2026-09-14

Plan version: 1

State transition: `source_probe_ready -> acceptance_met_pending_integration`;
plan remains `OPEN` for coordinator review and integration.

Progress classification: `outcome_progress`; the remaining provider-free
search product has exact versioned-runtime, fresh-client and teardown evidence.

Authority classification:

- `inherited_authority`: the bounded coordinator continuation authorized the
  probe and this isolated development runtime; every provider, browser,
  installed-service, live-data,
  schedule, staging, production, release and issue effect remained excluded;
- runtime acceptance used clean source commit
  `682794385e6b666e4f813847486bb7ae85e56b08`, preserving both the activation and
  `c4251dc1` integration ancestry. That exact source was committed before the
  run and published afterward, before this receipt-only closeout commit;
- the coordinator's later request for publication before runtime arrived after
  the completed run. No prior-publication claim or second runtime run is made;
- this C03 update and the retained raw receipt are receipt-only changes. They
  do not change the source/artifact identity exercised by the run;
- local HEAD, configured upstream and live remote were verified equal at
  `682794385e6b666e4f813847486bb7ae85e56b08` before this closeout update.

Exact runtime and artifact receipt:

- durable raw receipt:
  `dev/last30days/receipts/plan0114-search-runtime.json`;
- its SHA-256 is
  `4a5cab7e762b56a08af72787ba44f9ce3be829f51c989d633ec4855f844a3b61`,
  byte-identical to the original
  `/tmp/l30d-p33-state.bbWa33/last30days/lanes/l30d-p33-search-packet4-65eaf9ba6469/receipts/search-packet4.json`;
- runtime identity: `l30d-p33-search-packet4-65eaf9ba6469`;
  socket: `/tmp/l30d-p33-runtime.LZHEqF/65eaf9ba6469/s`;
- service `0.3.117`, database schema 18, source manifest
  `21566b5da1acc4220c572356b4a83bc76f83265cc87413191fc916c39fe74abe`,
  and public contract digest
  `ff7923059768032111fe47af144a060bb95180c90214b6a19e73ec4844a2edb6`
  agree across controller, HTTP and fresh MCP readbacks;
- two fixed-input builds from the exact clean source are byte-identical at
  `a103624e7aa64a86513c7d4c34c5c10152a9a0c0a8785e9f5fd86730a4ec2a44`;
  artifacts remain under `/tmp/l30d-p33-build.2Z1QZL/first` and `second`;
- fresh MCP binary SHA-256:
  `2c1e7d9544d2afbab6361458fee24e891dfedfd4af5c5738ded93b61181efb05`;
- controller service cycles: PID 2052166/start ticks 2971226 and PID
  2052593/start ticks 2971519; fresh MCP processes: PID 2052329/start ticks
  2971351 and PID 2052607/start ticks 2971545;
- both controller `down` receipts are `stopped`; final controller status is
  `absent`, the socket is absent and the fresh owned-session OS census is empty.
  A separate post-run `ps` readback found none of the four exact PIDs;
- synthetic database, logs, adapter and original receipts are retained in the
  unique temporary runtime roots. The committed raw receipt survives cleanup
  or expiry of those temporary paths and names the exact reproducible source.

Acceptance mapping:

1. Both fresh MCP clients complete discovery/handshake against the artifact;
   `search_posts` is read-only/closed-world and exposes the expected filters.
2. Typed HTTP and MCP compare the entire validated response except their
   generated request IDs and timestamps, preserving identity, revision,
   provenance, ranking components, coverage, cursor and response bounds.
3. Nineteen cases cover both families, source/author/topic/collection/time
   filters, conjunctions, current/all revisions, cross-store deduplication,
   private and unrelated profiles, private provenance exclusion and empty
   results; malformed cases and both explicit date sorts also pass.
4. A retained four-revision traversal survives an explicit synthetic
   publication; a fresh search sees the new revision. Both HTTP and MCP reject
   the old cursor with `cursor_stale` after the sequential runtime restart.
5. Complete logical-database digests remain unchanged around read-only probes;
   the explicit fixture publication alone changes its separately recorded
   before/after digest. No acquisition or schedule work is admitted by search.
6. Exact artifact/source, owner PID/birth, manifest, contract and teardown
   evidence are retained above; no installed or production-runtime claim is
   inferred from this development proof.
7. Comprehensive Python passes: **2,999 passed, 8 skipped, 14 subtests passed**
   in **197.92 seconds** using `uv run pytest --override-ini addopts='' -q`.
   Focused search/probe/MCP/controller/package selection passes **69 tests** in
   **14.66 seconds**. `go test ./...`, `go vet ./...`, focused Ruff, plan-authority
   audit and `git diff --check` pass. Source packaging is reproducible without
   any shared manifest edit. The opt-in 10,000-post benchmark remains skipped;
   Packet 3's frozen ranking/performance evidence is unchanged.

Review, bounds and handoff:

- one implementation attempt and one successful isolated acceptance run used;
  the two process cycles implement the planned restart scenario, not retries;
- no children or independent reviewer were launched. The coordinator retains
  the one broad independent review, any closed-world remediation, PR and join;
- no coordinator-owned manifest/catalog/version/shared transport or product
  documentation edits are required. Only the repo-only probe/test/docs, this
  plan and the raw receipt changed;
- next action: publish this receipt-only checkpoint and verify clean
  local/upstream/live-remote equality. Coordinator reviews/integrates the exact
  branch, then reconciles WI-002 to `DONE` only from accepted merged evidence.
  WI-003 public question transport remains its separate packet.
