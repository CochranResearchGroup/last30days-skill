<!-- last30days-work-item:WI-001 -->
# Run one lane in an isolated development runtime

State: READY
Priority: P1
Lane: Runtime
Parent: WI-000
Blocked by: none
Architecture: docs/dev/notes/0118-2026-09-13-isolated-development-runtime-architecture.md
Implementation plan seed: docs/dev/plans/0077-2026-09-13-isolated-development-runtime-architecture-and-lane-handoff.md

## Problem

Concurrent lane work cannot safely execute services when ports, databases,
credentials, schedules, logs, or process identity may overlap production.

## Outcome / Proposed Solution

A lane owner can provision, identify, inspect, and tear down one development
service instance whose configuration root, database, port or socket, logs, and
service identity cannot collide with production or another lane.

## Acceptance Evidence

- provider-free fixture proves deterministic per-lane configuration;
- startup fails closed on a collision or inherited production credential,
  browser profile, writable data path, or schedule;
- health and identity readback bind the process to lane, commit, and config;
- teardown removes only the named lane runtime and leaves production intact;
- operator documentation defines staging as a separate later deployment gate.

## Non-Goals

No production deployment, credential copying, authenticated provider canary,
or permanent `develop` branch.

## Ready Handoff

Assign one independent top-level lane session. Start from current
`origin/main`, create a dedicated `feat/isolated-dev-runtime` worktree,
register its active custody, and implement Packet 1 from the architecture note:
the strict descriptor, deterministic paths, read-only `doctor`, collision and
environment-deny checks, and provider-free fixtures. Do not start, install,
restart, stop, or signal any service in Packet 1.
