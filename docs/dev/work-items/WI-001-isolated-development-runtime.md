<!-- last30days-work-item:WI-001 -->
# Run one lane in an isolated development runtime

State: DONE
Priority: P1
Lane: Runtime
Parent: WI-000
GitHub issue: https://github.com/CochranResearchGroup/last30days-skill/issues/54
Blocked by: none
Architecture: docs/dev/notes/0118-2026-09-13-isolated-development-runtime-architecture.md
Implementation plan seed: docs/dev/plans/0077-2026-09-13-isolated-development-runtime-architecture-and-lane-handoff.md
Last completed plan: docs/dev/plans/0106-2026-09-14-wi001-runtime-evidence-reconciliation.md
Implementation evidence plan: docs/dev/plans/0105-2026-09-14-versioned-development-runtime-and-dogfood.md
Evidence receipt: docs/dev/notes/0126-2026-09-14-p51-runtime-dogfood-closeout-receipt.json
Branch: main

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

WI-001 is complete in repo-local authority. Packet 1 merged through PR 35 as
`c6bccab86074e83067a624a57efbc9d9b485c87f`. P51 subsequently implemented the
offline `doctor`/`up`/`status`/`down` lifecycle and authoritative cache-only
effect gates through PRs 73 and 74, then exercised exactly one isolated runtime
and retained the acceptance receipt through PR 75 at canonical `b2741a86`.

Acceptance mapping is recorded in Plan 0106. The isolated runtime is stopped;
the fresh final census contained production PID 1428 alone. GitHub issue 54
remains open because issue edit/close authority was not granted.

## Disposition

No further WI-001 packet is required. Staging remains a separate later
deployment gate, and any new runtime or deployment requires its own plan and
action-specific authority.
