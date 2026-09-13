<!-- last30days-work-item:WI-001 -->
# Run one lane in an isolated development runtime

State: IN_PROGRESS
Priority: P1
Lane: Runtime
Parent: WI-000
Blocked by: none
Architecture: docs/dev/notes/0118-2026-09-13-isolated-development-runtime-architecture.md
Implementation plan seed: docs/dev/plans/0077-2026-09-13-isolated-development-runtime-architecture-and-lane-handoff.md
Active plan: docs/dev/plans/0085-2026-09-13-isolated-dev-runtime-packet-1.md
Branch: feat/isolated-dev-runtime-v1

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

## Active Handoff

Resume the owning top-level session from published checkpoint
`4a8080daf354fe90db9462dc65ec1b29109058cc` and implement only Packet 1's
strict descriptor, deterministic paths, read-only `doctor`, collision and
environment-deny checks, and provider-free fixtures. Do not start, install,
restart, stop, or signal any service in Packet 1.
