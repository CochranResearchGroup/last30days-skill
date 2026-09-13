<!-- last30days-work-item:WI-001 -->
# Run one lane in an isolated development runtime

State: TRIAGE
Priority: P1
Lane: Runtime
Parent: WI-000
Blocked by: none

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
