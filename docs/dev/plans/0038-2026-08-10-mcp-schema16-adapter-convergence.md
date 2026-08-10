# Plan 0038 | MCP Schema-16 Adapter Convergence

State: OPEN
Roadmap: P14
Plan version: 2
Date: 2026-08-10
Predecessor: Plan 0037 version 5/checkpoint P0037-C12

## Objective

Restore a compatible installed MCP handshake for service 0.3.43/schema 16 and
prevent future canonical-contract changes from silently reusing an older MCP
adapter release identity.

## Current State

- live `service_info` is ready but returns `contract_digest_mismatch`;
- installed MCP adapter 4.0.1 advertises database schema range 15-15 while the
  service and canonical catalog are schema 16 with digest
  `fe8727fbe0d4e2f6775f49a6fc958369fe4877ba812bae4ef69121b88f12e2f1`;
- a fresh checkout build reports schema range 16-16 and `compatible`, proving
  the defect is stale adapter release/install identity rather than service
  behavior;
- commit `2e05b51` advanced the generated adapter contract from schema 15 to 16
  without advancing MCP manifest version 4.0.1.
- MCP 4.0.2 is now source-complete with an immutable compatibility-release
  lock, generator/install fail-closed enforcement, release documentation, and
  public-interface integration coverage; installed convergence remains.

## Scope

- add a deterministic MCP compatibility-release lock that binds each adapter
  version to one canonical catalog digest and supported service/database range;
- make contract generation fail closed when the manifest and current catalog
  do not have one exact release-lock entry;
- release the schema-16 adapter as 4.0.2, update focused tests and release docs,
  rebuild/install/register it, and verify the live public MCP interface;
- preserve the service, database, schedule, browsers, and source acquisition
  state unchanged.

## Non-Goals

- no service release, schema migration, source refresh, browser action,
  schedule mutation, provider attempt, external research, or Git tag/release;
- no broad MCP interface redesign or compatibility-range widening beyond the
  exact schema-16 contract already present in source.

## Acceptance Criteria

1. A deterministic red-capable live probe reproduces the installed
   `contract_digest_mismatch` and schema 15-15 advertisement.
2. Release validation binds MCP 4.0.2 to the current catalog digest, service
   interface range 1-1, and database schema range 16-16, while retaining the
   previous 4.0.1/schema-15 identity as history.
3. Contract generation and tests fail closed on a missing, duplicate, or
   mismatched current release-lock entry.
4. Go generation, focused Go/Python integration tests, broader applicable
   suites, formatting, and planning/patch audits pass.
5. The installed binary is stamped 4.0.2, advertises schema 16-16, and returns
   `compatibility_state=compatible` against service 0.3.43.
6. A post-install MCP `maintenance_status` read succeeds, proving operations
   beyond discovery are admitted by the repaired handshake.
7. Repository evidence is committed and pushed with the worktree clean and
   local `main` equal to `origin/main`.

## Definition Of Done

- criteria 1-7 have exact test, version, digest, binary, live-readback, commit,
  and push evidence;
- P14 and this plan close only after installed-process convergence is proven.

## Execution Bounds

- one implementation cycle and one bounded remediation cycle;
- one installed adapter replacement and, only if needed, one exact stale MCP
  process restart; no service restart;
- primary agent owns the serialized release/install boundary; no subagent is
  required for this compact compatibility repair.

## Validation Plan

- red/green installed-binary JSON-RPC `service_info` probe;
- `python3 mcp/scripts/generate-contracts.py` and generated-file cleanliness;
- focused release, contract-generation, Go client/tool, and live MCP tests;
- full `go test ./...` under `mcp/` and the applicable Python release/product
  suite, followed by formatting, planning audits, and `git diff --check`;
- installed binary digest/version plus live `service_info` and
  `maintenance_status` readback.

### Checkpoint P0038-C01 | 2026-08-10

Plan version: 1

State transition:

- `untracked_compatibility_backlog -> reproduced_release_install_drift`.

Progress classification:

- `outcome_progress`; the live/source differential isolates the repair seam.

Evidence:

- installed 4.0.1 returns `contract_digest_mismatch`, schema 15-15, against
  ready service 0.3.43/schema 16;
- a fresh source build returns `compatible`, schema 16-16;
- current and remote Git heads are aligned at `a31da0c` before this slice.

Subagent status and reconciliation:

- `not_spawned`; the primary owns this small serialized repair.

Authority classification:

- `inherited_authority`; the operator explicitly requested the MCP adapter fix.

Review disposition summary:

- `blocking=1` installed compatibility drift, `nonblocking_backlog=0`,
  `rejected=0`, `needs_evidence=0`.

Next action:

- add the failing release-lock contract, then make the minimal version,
  generator, test, documentation, and installed-runtime changes that satisfy it.

### Checkpoint P0038-C02 | 2026-08-10

Plan version: 2

State transition:

- `reproduced_release_install_drift -> validated_4_0_2_install_candidate`.

Progress classification:

- `outcome_progress`; release/install drift now has a fail-closed source gate
  and a uniquely bound successor adapter identity.

Owned changes:

- MCP manifest 4.0.2 and `mcp/compatibility-releases.json` bind current schema
  16 and preserve the prior 4.0.1/schema-15 identity;
- contract generation and Codex installation validate the release lock before
  building;
- release, integration, manifest, planning-authority, changelog, MCP README,
  and onboarding surfaces reflect the new contract.

Validation evidence:

- release-lock test went red for missing implementation, then green for exact,
  missing, duplicate, and mismatched identities;
- live integration builds the manifest-stamped adapter and proves 4.0.2,
  schema 16-16, and `compatible` through the public `service_info` tool;
- focused Python and Go suites, generator cleanliness, full Go tests, Go vet,
  touched-Go formatting, planning audits, and patch checks pass;
- the first full Python run reached 2,639 passes, 7 skips, and 6 subtests with
  one expected planning-authority fixture drift; after that fixture was
  repaired, the full suite passed 2,640 tests, 7 skips, and 6 subtests.

Subagent status and reconciliation:

- `not_spawned`; the primary owns the serialized install boundary.

Authority classification:

- `inherited_authority`; implementation stays inside the requested MCP repair.

Review disposition summary:

- `blocking=1` installed convergence,
  `nonblocking_backlog=0`, `rejected=0`, `needs_evidence=0`.

Remaining acceptance criteria:

- criteria 5-7 remain; criteria 1-4 pass.

Next action:

- run the final candidate gate, commit/push the source slice, install once from
  the clean commit, and verify live discovery plus maintenance admission.
