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

Activation custody is accepted at P0114-C01. Implementation remains held until
the coordinator integrates the canonical activation projection and resumes this
owner with the bounded implementation assignment.

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
