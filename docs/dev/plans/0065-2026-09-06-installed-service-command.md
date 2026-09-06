# Plan 0065 | Installed Service Command

State: OPEN
Lane: P25
Branch: fix/installed-service-command
Target: feat/recurring-reddit-home-feed
Integration: fast-forward
Date: 2026-09-06

## Objective

Keep the documented installed Skill service command aligned with the managed
service after builds, installs, upgrades, and rollbacks.

## Current State

The frozen Skill script rejected a valid three-attempt config and schema 17;
the installed 0.3.109 launcher accepted both. The original config is restored.
One authorized manual tick is running through the installed launcher.

## Scope and Sequence

One primary owner, serialized implementation and installation. No subagents.
1. Route installed Skill service invocations to the stable managed launcher
   before loading bundled libraries; retain source-checkout execution.
2. Refresh existing frozen Skill entrypoints during managed installation;
   preserve symlinked development checkouts and unrelated files.
3. Exercise stale-client regression, install/upgrade/rollback, release build,
   and installed read-only preflight after the manual tick terminalizes.
4. Record the tick outcome, release evidence, and branch custody.

## Definition Of Done

- A frozen client with stale libraries executes the selected managed runtime.
- Installation refreshes the previously stale command; subsequent release
  selection and rollback do not require a separate Skill reinstall.
- Missing managed runtime fails clearly without accessing the database.
- Source checkout behavior remains available for development tests.
- Focused tests pass; versioned build and installed readback prove the fix.
- Plan/runbook/roadmap and a coherent committed checkpoint describe the result.

## Non-Goals

No browser repair, new source attempts beyond the requested tick, source config
changes, database migration, broad Skill synchronization, or unrelated lane
integration. The active tick must finish before the service upgrade.

## Checkpoints

### Checkpoint P0065-C01 | 2026-09-06

Plan version: 1

- Stale installed-command regression failed before the fix and passed after it.
- Twenty lifecycle/release/Skill packaging checks and eighteen preflight checks
  passed. Build produced service 0.3.110; schema remains 17.
- Manual tick `tick-e38e517c62d8ec6eba1882af7e8586c2` failed with
  `contractvalidationerror` during LinkedIn retry; 80 X and three YouTube items
  were retained, Reddit did not run, and no snapshot was promoted.
- Installation and post-install readback remain for C02. No retry tick.

Authority classification:

- `inherited_authority`
