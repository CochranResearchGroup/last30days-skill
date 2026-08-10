# Plan 0038 | MCP Schema-16 Adapter Convergence

State: CLOSED
Roadmap: P14
Plan version: 3
Date: 2026-08-10
Predecessor: Plan 0037 version 5/checkpoint P0037-C12

## Objective

Restore a compatible installed MCP handshake for service 0.3.43/schema 16 and
prevent future canonical-contract changes from silently reusing an older MCP
adapter release identity.

## Current State

- the installed MCP binary is release 4.0.2 at clean source revision
  `0eabd9950520869de9f6685c0f6c574641f65b20`, SHA-256
  `4336d24aedf067a54745407b9e8a1dfe2280c0ce1ea17f3f81efef9f8de5ebbc`;
- a fresh installed process reports ready service 0.3.43/schema 16, adapter
  4.0.2/schema 16-16, the canonical digest, and
  `compatibility_state=compatible`;
- `maintenance_status` succeeds through that fresh installed process, proving
  the repaired handshake admits a governed operation beyond discovery;
- adapter processes already attached to running Codex conversations keep their
  prior 4.0.1 process image until connector/session restart. They were not
  terminated because other active sessions own them; new processes use 4.0.2;
- service 0.3.43, `daily-default`, current and rollback databases, browsers,
  tabs, and acquisition state were not changed by this repair.

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

### Checkpoint P0038-C03 | 2026-08-10

Plan version: 3

State transition:

- `validated_4_0_2_install_candidate -> installed_compatible_closed`.

Progress classification:

- `outcome_progress`; the installed adapter and governed maintenance surface
  now use the exact schema-16 release identity.

Installed and repository evidence:

- implementation commit `0eabd9950520869de9f6685c0f6c574641f65b20` is pushed
  to `origin/main`;
- the pre-install binary SHA-256 was
  `7dfc61af38faa69fbfcc3b2a2adc1cbd87734ed1b7bbea3a7fe3f6ad0c4f735d`;
- the single authorized install produced SHA-256
  `4336d24aedf067a54745407b9e8a1dfe2280c0ce1ea17f3f81efef9f8de5ebbc`
  with adapter 4.0.2 and clean VCS revision `0eabd995`;
- a fresh installed JSON-RPC process reports `compatible`, the schema-16
  digest, database range 16-16, ready service 0.3.43, and no RPC error;
- a fresh installed `maintenance_status` call succeeds and preserves the
  approval, branch-isolation, evaluation, and failure-signature repair policy;
- the current conversation's pre-existing connector still reports 4.0.1 until
  it is reconnected. This is process-lifetime state, not an installed-binary
  failure, and no other session's adapter process was killed.

Validation evidence:

- the final Python suite passes 2,640 tests with 7 skips and 6 subtests;
- Go generation, full Go tests, Go vet, touched-Go formatting, planning audits,
  plan-authority audit, and patch checks pass;
- service status remains ready at 0.3.43/schema 16; `daily-default` remains
  enabled/ready with its next boundary `2026-08-11T00:00:00Z`; current and
  rollback SQLite `quick_check` both return `ok`;
- Graphiti provider readiness passed. One exact, duplicate-preflighted closeout
  write was queued as job `8ae1dd76-11a6-48cb-be26-133d409a75ca`, then timed
  out after 45 seconds during node extraction with `episode_uuid=null` and
  `retryable=false`; no retry or duplicate was queued.

Subagent status and reconciliation:

- `not_spawned`; the primary owned the serialized release/install boundary.

Authority classification:

- `inherited_authority`; installation and validation stayed inside the
  operator-requested MCP adapter repair.

Review disposition summary:

- `blocking=0`, `nonblocking_backlog=0`, `rejected=0`, `needs_evidence=0`.

Acceptance result:

- criteria 1-7 pass; Plan 0038 and P14 are closed.

Next action:

- reconnect any already-running Codex MCP connector that must consume adapter
  4.0.2 immediately; ordinary new connector processes require no intervention.
