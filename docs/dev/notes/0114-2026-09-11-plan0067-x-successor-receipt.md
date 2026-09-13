# Plan 0067 X Successor Receipt

Date: 2026-09-11

Plan: [0067](../plans/0067-2026-09-11-x-lock-timeout-successor.md)

## Terminal Result

- Last30days refresh job: `45d7167e-9378-450e-98f6-09c7c0641da0`
- Query: `AI agents`
- Sources: `x`
- Partition: `default` / public
- State: `failed`
- Attempts: 2 of 2, service-owned
- Error: `agent_browser_error`
- Published index version: none
- Spend: zero

The client issued one refresh call. The returned durable job moved from
`acquiring` to a service-owned queued retry after attempt one, then reached its
first terminal state after attempt two. No second refresh call was issued.

## Agent Browser Correlation

| Attempt | Evaluate job | Failure | Revision | Effect |
|---:|---|---|---|---|
| 1 | `mcp-service-request-evaluate-3e59f7ea-aaed-4ac7-a7f2-3e6d6aba1d09` | `service_state_stale_revision` | expected 78568, actual 78569 | `no_effect` |
| 2 | `mcp-service-request-evaluate-e472e152-08f4-422b-9a35-7c610a399035` | `service_state_stale_revision` | expected 78678, actual 78679 | `no_effect` |

Both failures are at the Service State `commit` phase and preserve
`inspect_before_retry`, `reload_state_and_replan`, and hard stop `blind_retry`.
The first exact job was evicted before postflight lookup; its immutable failure
journal record remains. The second exact job remained inspectable.

The installed Agent Browser identity is package `0.28.0`, source revision
`0f6b949eea2b5c853415d15310ca6362535d0d27`, support generation
`0.28.0-842bb1beedbf-249db11e4fdb`. This revision prepares a mutation from a
snapshot outside the exclusive commit lock, then compares the current revision
under lock. It internally reloads and replays once after a stale candidate; a
second collision returns `service_state_stale_revision`. Both Last30days
attempts reached that terminal collision.

## Postflight

- current lock diagnostics: no active holder and zero process-local timeouts;
- retained browser: `session:terminal-profile-38f540268ae65cf6ee8ce5de`, PID
  5681, profile `last30days-facebook`, health `ready`;
- no duplicate browser process, profile mutation, runtime maintenance, schedule
  operation, or further Last30days refresh was performed;
- no X evidence was published.

This run reclassifies the immediate failure from a one-second file-lock timeout
to repeated optimistic-commit revision collision. It does not prove that the
underlying shared-state contention is repaired.

