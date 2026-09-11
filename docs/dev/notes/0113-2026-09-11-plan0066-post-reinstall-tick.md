# Plan 0066 Post-Reinstall Tick Receipt

Date: 2026-09-11

Plan: [0066](../plans/0066-2026-09-11-post-reinstall-bounded-tick.md)

## Terminal Result

- Tick: `tick-3fe4ae25a3fb7f6dce63e2881fedc504`
- State: `complete_degraded`
- Interval: `2026-09-10T10:25:42Z` to `2026-09-11T10:25:42Z`
- Schedule: `manual-p0066-20260911-102542`
- Snapshot: `tick-snapshot-63666743e2c95ded9a705bc7f7d22612`
- Promoted sources: 93
- Media artifacts: 16

| Source | Attempts | Accepted | Observed | State |
|---|---:|---:|---:|---|
| YouTube | 1 | 3 | 8 | success |
| X | 1 | 0 | 0 | failure |
| LinkedIn | 1 | 52 | 1472 | success |
| Reddit | 1 | 38 | 673 | success |

## X Failure Correlation

- Provider attempt:
  `provider-attempt-5558ccc9438992d42198bce711f3fa52`
- Failure stage: `extraction`
- Safe code: `agent_browser_error`
- Reason: `service_state_lock_timeout`
- Agent Browser job:
  `mcp-service-request-evaluate-a45fc2da-b4ec-4d07-bac8-d43dd9528e04`
- Agent Browser error: `service_state_lock_timeout: file lock; waited_ms=1002`
- Job interval: `2026-09-11T10:28:43.603877902Z` to
  `2026-09-11T10:28:46.120030113Z`
- Effect state: `effect_uncertain`
- Retry disposition: `inspect_before_retry`
- Recommended action: `inspect_job_and_refresh_plan`
- Hard stop: `blind_retry`

The failed job overlaps successful X evaluation job
`mcp-service-request-evaluate-1c52cf98-8a32-4b1a-b078-78cc42b70ee8`, whose
recorded interval is `2026-09-11T10:28:41.118292455Z` through
`2026-09-11T10:28:44.495696073Z`. The X adapter reported 12 successful eval
operations before the failure. Last30days did not retry and successfully
released the exact tab handle.

## Agent Browser Observability Defect

Five successful evaluate jobs have `completedAt` earlier than `startedAt`:

- `mcp-service-request-evaluate-07b47946-dca9-464f-9beb-01312812540d`
  (LinkedIn; inversion 229 ms);
- `mcp-service-request-evaluate-cd3de398-dbe8-44f4-8432-616843ef1006`
  (Reddit; inversion 60 ms);
- `mcp-service-request-evaluate-32b610c8-15e1-4cdd-b755-2f59da980f04`
  (Reddit; inversion 944 ms);
- `mcp-service-request-evaluate-215c17e8-a5f0-493b-87ce-27de104392da`
  (Reddit; inversion 736 ms);
- `mcp-service-request-evaluate-1868430d-0c85-4b2a-97e5-5c96cc41653a`
  (Reddit; inversion 439 ms).

These timestamps should not be used to infer true concurrency until Agent
Browser's job-clock or persistence ordering is repaired. The X overlap remains
corroborated by the recorded intervals, but its causal relationship to the
file-lock timeout is a hypothesis, not proof.

## Postflight State

- Agent Browser install/runtime generation:
  `0.28.0-6d4e6085c1de-e6cab967af18`;
- runtime admission drain: false;
- profile diagnosis: `ready`, current healthy retained browser PID 84416,
  shared-tab reuse available, no dominant blocker;
- Last30days open resource leases: zero;
- recurring `daily-default`: enabled/ready, next boundary
  `2026-09-12T00:00:00Z`;
- Last30days database `quick_check`: `ok`;
- no Agent Browser repair, profile seeding, freshness update, restart, or retry
  was performed.
