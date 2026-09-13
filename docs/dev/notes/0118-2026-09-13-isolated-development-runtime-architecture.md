# Isolated Development Runtime Architecture

Date: 2026-09-13
Work item: WI-001
Plan: 0077
Repository checkpoint: `b71e652317bea4607ced38719a16b4d039c2609f`
Investigation mode: stable local Git repository, runtime architecture and mixed
code/docs synthesis, hybrid structure-first retrieval

## Decision

Add a repo-only `dev/last30days/scripts/lane_runtime.py` controller for one
provider-free development service per named lane. The controller owns
`doctor`, `up`, `status`, and `down`; invokes the worktree's existing
`skills/last30days/scripts/service.py serve` entrypoint; and never installs,
upgrades, or controls `last30days.service`.

The controller derives a stable runtime ID from the repository identity and
explicit lane ID. It creates one private lane state tree plus a short
user-runtime socket tree:

- configuration, identity, and generated offline Tick configuration;
- SQLite database and any local artifacts;
- service log, PID record, and immutable startup receipt;
- Unix socket under `XDG_RUNTIME_DIR` with a bounded path length;
- current status receipt that binds lane, worktree, branch, commit, effective
  configuration digest, process birth identity, socket, database, and service
  handshake.

The first implementation must add an explicit cache-only service effect mode.
In that mode, refresh admission, recurring collection, Tick scheduling,
assessment, notification, Graphiti projection, provider subprocesses, and
browser/profile access are unavailable even if a caller requests them or the
ambient host has credentials. Isolation is not accepted merely because no
provider request happened during a smoke test.

## Why A Repo-Only Controller

The managed installer owns one production-shaped release root, one
`last30days.service` unit, the shared `~/.config/last30days/.env`, the shared
database, and the production Unix socket. Extending that installer for
arbitrary worktrees would mix release management with disposable lane
lifecycle and could refresh frozen Skill entrypoints.

The current service already exposes the right process seam: `serve` accepts
independent `--db` and `--socket` paths. A development controller can compose
that seam without creating another application implementation. The missing
pieces are effect isolation, config isolation, process identity, collision
detection, and exact-target teardown.

## Current Evidence

- Canonical `main` and `origin/main` agree at
  `b71e652317bea4607ced38719a16b4d039c2609f`; this architecture work uses a
  separate worktree and branch.
- The live installed unit is `last30days.service`, active/running with PID
  `24968`, launcher
  `~/.local/share/last30days/service/last30days-service`, environment file
  `~/.config/last30days/.env`, and socket
  `/run/user/1000/last30days/service.sock`.
- Live service readback reports service `0.3.116`, database schema 17, ready
  status, and runtime manifest SHA-256
  `19707a469eb58c21ca4c5b43a0bfbfb6cac4b0f5a5310480b01b1a3f652429e8`.
- `_serve` already accepts explicit database and socket paths, but resolves
  Tick configuration through `LAST30DAYS_CONFIG_DIR` and starts acquisition
  and enrichment loops unconditionally. Assessment and Graphiti loops are
  ambient-environment gated.
- `load_service_source_policy` defaults to all service sources. Reddit's
  keyless method is intrinsically ready, YouTube depends on subprocess PATH,
  and browser sources can become ready from binary and environment state.
- The production installer renders one fixed unit and injects only the socket;
  database, config, credentials, release selection, readiness receipt, and
  service identity remain production-shaped shared paths.

Graphiti discovery recovered the earlier service-first decision: the managed
release root, runtime allowlist/manifest, atomic current/previous selection,
and version handshake are production authorities. Current CodeGraph and live
readback verified that evidence and exposed the development-isolation gaps.

## Runtime Identity Contract

The controller requires a normalized lane ID and an absolute Git worktree.
Its descriptor is strict, canonical JSON with:

- schema version and runtime kind `development`;
- stable runtime ID, lane/work-item/plan locators, repository remote identity,
  worktree path, branch, and exact commit;
- explicit config, data, database, artifacts, log, run, socket, PID, and
  startup/status receipt paths;
- effect mode `cache_only`, credential policy `deny`, schedule policy `deny`,
  browser policy `deny`, and inherited-environment policy `allowlist`;
- descriptor digest and creation/update timestamps.

`doctor` is read-only. It renders the descriptor and fails on a dirty or
non-Git worktree, detached/default branch, non-absolute or unsafe path,
runtime-ID collision, production path equality or containment, overlong Unix
socket, unsafe symlink, existing live owner, or a descriptor owned by another
lane/worktree. A dirty tree may be supported later only through an explicit
policy decision; the tracer remains commit-bound.

## Environment And Effect Boundary

The child environment is built from a documented allowlist, not copied and
redacted after the fact. It carries only process necessities plus controller
values such as `HOME`, locale, a deterministic minimal `PATH`, isolated XDG
roots, DB/socket paths, and the cache-only effect mode.

The deny check rejects any proposed child key matching known credential,
token, cookie, browser/profile, notification, Graphiti, assessment, provider,
or schedule families. It also rejects an existing Tick configuration unless
it is the controller-generated, digest-bound disabled fixture. Provider
binaries being installed on the host must not make the lane service ready for
acquisition.

The service-side cache-only gate is defense in depth and authoritative for
requests: only health, service information, cache reads, and provider-free
local indexing/enrichment required by those reads may run. Any refresh,
collection, Tick, incident mutation, assessment, repair, notification,
projection, or provider/browser path returns a stable disabled-by-runtime
error without creating work.

## Process And Collision Contract

`up` obtains an exclusive lane lock, reruns `doctor`, writes the immutable
startup receipt, starts one foreground child redirected to the lane log, and
waits for `/v1/service-info`. Acceptance requires the handshake plus exact
PID birth token and descriptor digest; socket existence alone is insufficient.

`status` is read-only and reports `absent`, `starting`, `ready`, `stale`, or
`foreign`. It verifies the recorded PID is still the same OS process, its
command resolves to the expected worktree entrypoint, the Unix socket is owned
by the current user, and service information agrees with the startup receipt.
It never repairs or kills a process.

`down` requires the same runtime ID, descriptor digest, PID birth token,
worktree, and command identity before signaling the process. It waits a bounded
drain, reports failure without escalation if identity changes, and removes
only named ephemeral socket/PID/lock files. Database, logs, and receipts are
retained by default. A separate future `purge` operation would require an
explicit exact target and is outside v1.

## Staging And Production Boundary

Production remains the managed, versioned user service. Staging is a future
separately installed release identity with its own unit, release root, config,
database, socket, logs, credentials policy, and promotion receipt. It is not a
`develop` branch and must not be simulated by pointing a development
controller at production data or credentials.

Lane evidence can support integration, but neither a healthy lane runtime nor
passing tests authorizes staging or production deployment. Authenticated
provider/browser canaries remain serialized and separately authorized.

## Vertical Delivery Packets

1. Identity tracer: strict descriptor model, deterministic path derivation,
   read-only `doctor`, collision and deny-list tests, and a provider-free
   fixture. No process is started.
2. Offline lifecycle: service cache-only effect gate plus `up`, `status`, and
   `down`; exact process/readiness binding; request-level denial tests; and two
   concurrent isolated fixture runtimes that leave the live unit untouched.
3. Developer product surface: bounded log/status diagnostics, stale-state
   recovery that never signals an unverified PID, usage documentation, and a
   WI-002 consumer smoke against seeded local data.
4. Closeout: package-boundary and full presubmit validation, release/version
   changes only if shipped service files changed, fresh-session handoff, and a
   separately proposed staging work item. No production installation occurs.

## Expected Write Surfaces

- repo-only controller and focused tests under `dev/last30days/scripts/` and
  `tests/`;
- the existing service bootstrap/application policy seam for cache-only effect
  enforcement and service-info visibility;
- service contracts/generated artifacts only if the lane proves a public
  response field is necessary;
- `CONFIGURATION.md`, `docs/ONBOARDING.md`, roadmap, runbook, plan, and work-item
  state;
- release metadata and runtime manifest only when shipped service code changes.

The lane owner must use CodeGraph impact before changing the service contract
or bootstrap and coordinate overlapping service files with WI-002.

## Acceptance Boundary

Provider-free acceptance requires:

- deterministic descriptor/path output for the same repository and lane, and
  distinct output for two lanes;
- rejection of every production-path collision, foreign descriptor, unsafe
  symlink, inherited credential/browser/provider/schedule setting, and
  overlong or non-owner socket;
- two simultaneous fixture runtimes with unique configuration, database,
  socket, logs, PID, and identity, both bound to their expected commits;
- non-cache requests fail before durable job creation or external adapter
  invocation;
- status detects dead, PID-reused, wrong-command, wrong-commit, and wrong-
  descriptor cases without repair;
- teardown proves the production PID/socket/database/unit are unchanged and
  retains the lane database/log/receipts;
- no test touches a real provider, browser profile, credential, notification,
  Graphiti endpoint, schedule, installed Skill, or managed service.

## Open Questions For The Lane Owner

- Measure actual startup/shutdown timing before freezing readiness and drain
  budgets.
- Confirm the portable process-birth token implementation on Linux and define
  the explicit unsupported-platform result for v1.
- Decide whether service-info needs a backward-compatible runtime-mode field or
whether the controller's digest-bound composite receipt is sufficient.

## Skill Friction

The shared `codebase-investigator` skill references two optional shared example
files that are absent from the installed skill tree. Its required environment,
tool, runbook, retrieval, output, and plan references were available; the
missing examples did not limit this investigation.

## State Location

This note and its machine-readable companion are durable in the stable Git
repository. No bundle or snapshot is needed.
