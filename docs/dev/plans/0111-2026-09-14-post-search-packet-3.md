# Plan 0111 | Bounded Hybrid Post Search Packet 3

State: OPEN
Lane: P33
Work item: WI-002
Branch: feat/post-search-v3
Target: main
Integration: merge
Roadmap: P33
Plan version: 1
Date: 2026-09-14
Execution owner: /root/wi002_packet3_planning
Coordination owner: /root
Requested model route: gpt-6-astra, high reasoning
Effective runtime model: unknown (not reported by runtime)
Effective reasoning effort: unknown (not reported by runtime)

## Objective

Complete WI-002 Packet 3 with provider-free semantic candidates,
deterministic reciprocal-rank fusion, reproducible explanations, bounded
responses and coverage diagnostics, plus measured 10,000-post local evidence.

## Current State

Packets 1-2 are integrated through PRs 36 and 79. Both storage families,
complete filters, current/all revisions, cross-store identity, and stable
snapshot pagination exist. Ranking remains lexical-only; the existing 10,000
candidate and 32 MiB limits are admission controls, not performance evidence.
Checkpoint P0111-C01 activates plan ownership and publication only. Product
implementation and all seven acceptance criteria remain outstanding; the
coordinator must reconcile shared-surface ownership before assigning execution.

## Scope

- rank authorized prefiltered candidates through lexical and local deterministic
  semantic channels without creating embeddings or inheriting provider access;
- fuse independently ordered channels through a versioned deterministic RRF
  contract with reproducible component ranks, scores, and stable tie breaks;
- preserve exact revision/evidence identity, access partitions, retained cursor
  inputs, and explicit semantic coverage/degradation for both storage families;
- fit complete UTF-8 responses beneath the existing transport bound without
  skipping hits across budget-shortened pages;
- baseline first, then freeze and prove explicit latency/RSS budgets on one
  opt-in synthetic 10,000-post fixture split across both families;
- keep Python, HTTP, MCP, Skill, and configuration guidance aligned.

## Non-Goals

No materialized unified index, schema migration, general provider embedding
plumbing, durable cursor redesign, WI-003 answer change, release/version,
installed runtime, provider/browser, schedule, staging, or production effect.

## Acceptance Criteria

1. Semantic-only, lexical-only, dual-channel, tied, zero-vector, and missing or
   mismatched-vector fixtures reproduce deterministic RRF order and coverage.
2. Unauthorized and filtered-out candidates never reach either ranker; current/
   all collisions cannot promote stale matching revisions.
3. Cursor pages pin ranking inputs and remain stable across publication or
   semantic metadata change; existing tamper/access/expiry cases stay green.
4. Complete serialized responses fit the transport limit or fail with one
   stable bounded error; concatenated shortened pages equal logical order.
5. Python application/HTTP and fresh Go MCP clients agree, WI-003 evidence and
   `/v1/query` compatibility remain green, and no effectful call is admitted.
6. A durably recorded baseline precedes the frozen 10,000-post latency/RSS
   budget, and the final opt-in fixture meets it without erasing correctness
   evidence on a performance failure.
7. The exact clean branch checkpoint is published for coordinator review.

## Execution Packet

- one top-level implementation owner, no children; two implementation attempts,
  one independent broad review, and one closed-world remediation pass;
- lane-owned writes: post-search backend or narrow ranking module, focused
  search/ranking/performance fixtures and tests, this plan;
- coordinator-assigned overlaps: search-specific Python contract/schema, app
  wiring only if required, MCP search tool/tests, and search guidance;
- coordinator-exclusive: generated catalogs, runtime manifest, roadmap,
  runbook, active lanes, and work-item state;
- terminal condition: published source acceptance for Packet 3 or one exact
  recorded blocker; do not begin Packet 4.

## Definition Of Done

All seven criteria pass at one published checkpoint suitable for joined review,
or one exact blocker is recorded without widening the packet.

## Current Checkpoint

### Checkpoint P0111-C01 | 2026-09-14

Plan version: 1

State transition: `planned -> activation_published`; plan state is `OPEN`.

Progress classification: `hardening`; execution custody and the activation
boundary are recorded. This checkpoint claims no product acceptance result.

Authority classification:

- `inherited_authority` under Plan 0107 and the coordinator's activation-only
  assignment permits editing this plan, validation, one coherent commit, and
  publication to `origin/feat/post-search-v3`;
- the accountable human owner is the repository operator; execution owner is
  `/root/wi002_packet3_planning`, a direct child of coordinator `/root`;
- this assignment stops after publication readback. No source implementation,
  shared-authority edit, benchmark, runtime, provider/browser, schedule, issue,
  release, staging, production, or durable-memory write is included.

Base and custody evidence:

- assigned worktree:
  `/home/ecochran76/workspace.local/last30days-skill-wi002-v3`;
- branch: `feat/post-search-v3`; initial clean HEAD:
  `7f65c4285146e8d4dabd417617584fe7042a582f`, the PR 81 Wave 2 registration merge;
- a fresh `git ls-remote --heads origin main feat/post-search-v3` returned
  `refs/heads/main` at that exact base and no existing Packet 3 remote branch;
- `origin` is `CochranResearchGroup/last30days-skill`; `upstream` push is
  disabled. The publication target is exactly `refs/heads/feat/post-search-v3`;
- the canonical worktree remains reserved for coordinator-owned `main`.
  Its fresh readback was clean `main` at the exact base above. No checkout,
  ref custody, or default-branch reassignment is performed here.

Inputs and validation boundary:

- Plan 0107, this Plan 0111, WI-002, architecture note 0117, and the closed
  Plans 0084/0108 provide the execution and acceptance authority;
- planning, documentation, Git/worktree, commit/publication, validation,
  work-item, operating-model, model-selection, and collaborative-workflow
  policies were reread for this activation;
- current repository authorities are sufficient for this bounded activation:
  Graphiti discovery is `skip`; prior read-only planning inspected the current
  backend and public contract with CodeGraph and found the lexical-only gap;
- activation validation consists of the plan-authority audit, `git diff
  --check`, exact one-file diff inspection, and post-push clean worktree plus
  local/remote SHA equality. Product tests and benchmarks are intentionally
  unrun; no product or performance acceptance is implied.
- `python dev/last30days/scripts/audit_plan_authority.py` passed with zero
  issues against the existing canonical projection (two active plans);
  `git diff --check` passed, and direct diff inspection confirmed this plan
  alone changes with the required owner, `OPEN` state, and activation bounds.
  Canonical activation projection remains the coordinator's next join.

Overlap and dependency handoff:

- the lane will own the backend or narrow ranking module and focused tests;
- before product execution, the coordinator assigns search-specific sections
  of `service_contracts.py`, `post-search-contracts-v1.json`, optional app
  wiring, `mcp/internal/tools/service_tools.go` and its tests, and search
  paragraphs in `SKILL.md` and `CONFIGURATION.md`;
- generated catalogs, `service/runtime-manifest.json`, roadmap, runbook,
  active-lane catalog, and work-item projections remain coordinator-exclusive;
- WI-003 transport work may consume the frozen search interface, but its
  answer semantics and overlapping shared files are not lane-owned. WI-008
  consumes the accepted ranking/coverage result after integration;
- two implementation attempts, one broad independent review, and one
  closed-world remediation pass remain the inherited execution bounds.
  Activation consumes no implementation attempt.

Model and worker receipt:

- requested route: `gpt-6-astra`, high reasoning, justified by ranking,
  identity, access, and cursor correctness across two storage families;
- effective runtime model and reasoning effort: unknown, not reported;
- one active lane owner; no children spawned. The coordinator owns
  reconciliation and final acceptance of this publication.

Stop and next action:

- stop after reporting the exact publication SHA, clean status, and remote
  equality to the coordinator; do not start product code or Packet 4;
- on resume, verify the published branch and assigned worktree, reread this
  checkpoint and current policies, and obtain the coordinator's reconciled
  implementation assignment and exact shared-surface ownership;
- stop and report any custody mismatch or newly conflicting write ownership;
  no automatic implementation, benchmark, provider, or runtime continuation.
