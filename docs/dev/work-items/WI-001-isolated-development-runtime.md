<!-- last30days-work-item:WI-001 -->
# Run one lane in an isolated development runtime

State: READY
Priority: P1
Lane: Runtime
Parent: WI-000
GitHub issue: https://github.com/CochranResearchGroup/last30days-skill/issues/54
Blocked by: none
Architecture: docs/dev/notes/0118-2026-09-13-isolated-development-runtime-architecture.md
Implementation plan seed: docs/dev/plans/0077-2026-09-13-isolated-development-runtime-architecture-and-lane-handoff.md
Last completed plan: docs/dev/plans/0085-2026-09-13-isolated-dev-runtime-packet-1.md
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

Packet 1 merged through PR 35 as `c6bccab86074e83067a624a57efbc9d9b485c87f`.
The coordinator should register a separate Packet 2 plan before implementing
offline `up`/`status`/`down` or service-side cache-only effect gates. Do not
start or mutate a runtime under the closed Packet 1 plan.
