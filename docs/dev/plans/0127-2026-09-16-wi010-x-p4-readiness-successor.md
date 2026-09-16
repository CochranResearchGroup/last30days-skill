# Plan 0127 | WI-010 X P4 Readiness Successor

State: OPEN
Lane: P53
Work item: WI-010
Branch: feat/wi010-x-p4-readiness-successor-v1
Target: main
Integration: merge
Roadmap: P53
Plan version: 1
Date: 2026-09-16
Execution owner: /root
Coordination owner: /root
Requested model route: host default, no delegation
Effective runtime model: not exposed

## Objective

Consume one newly authorized X P4 auth-readiness attempt against the same
stable `last30days-facebook` profile after independently confirming that the
host-global display-allocation symptom from Plan 0126 is no longer present.

## Current State

Plan 0126's attempt is terminal and remains immutable. Agent Browser issue
#159 repaired the pathname classifier in source and is closed through repair
PR #166 and closeout PR #167. The installed runtime still reports version
0.28.0, while current physical evidence shows no live display, abstract socket,
lock, or X server in the configured `:90-:129` range. The operator explicitly
said `try again`, authorizing this one successor attempt. No P5 or content
request is authorized.

## Definition Of Done

One fresh packet is prepared from canonical source, consumed exactly once
against the exact stable profile, independently verified, followed by a clean
post-run ownership census, and retained through the repository PR workflow.

## Scope

- retain Plan 0126's packet and receipts unchanged;
- verify the exact stable X profile, route, lease, jobs, challenges, and
  physical display occupancy before execution;
- prepare a new short-lived source-bound one-attempt grant;
- invoke the already-integrated executor exactly once;
- independently verify its safe receipt and retain a fresh post-run census;
- publish the successor evidence through the existing PR workflow.

## Non-Goals

No X search, timeline or content extraction, P5 canary, retry, alternate
profile, manual login, CAPTCHA/checkpoint intervention, allocator cleanup,
service restart, installed-runtime mutation, credential disclosure, or private
page-data capture.

## Frozen Effect Contract

Plan 0126's provider, adapter, profile, budgets, allowed operations,
redaction, teardown, and receipt rules apply unchanged. This successor has one
new grant, one external attempt, and automatic retry zero. A preflight
mismatch or any execution uncertainty is terminal.

## Acceptance Criteria

1. The packet binds `x`, `x_agent_browser`, `x-browser`, and
   `profile:last30days-facebook` from canonical source.
2. Execution calls only workspace acquisition, auth inspection, and exact-owner
   release; no content-search path executes.
3. The safe receipt records one explicit auth observation, bounded accounting,
   and teardown state without credentials or page content.
4. Offline verification succeeds and the fresh post-run census shows no owned
   lease, tab handle, or attributed process remaining.

## Stop Rules

Stop before execution on profile, route, source, grant, lease, challenge,
display, or concurrency mismatch. After invocation, preserve the first result
and do not retry. P5 remains held regardless of the outcome.

## Next Action

Checkpoint this plan remotely, complete the read-only preflight, then prepare,
consume, verify, and publish exactly one successor receipt.

### Checkpoint P0127-C01 | 2026-09-16

Plan version: 1

State transition: `unplanned -> OPEN`.

Progress classification: `outcome_progress`; the operator authorized one new
bounded attempt after diagnosis and upstream repair of the prior host-global
allocator failure.

Authority classification:

- `human_gate` from the operator's explicit `try again` instruction.

Validation evidence:

- canonical `main` was clean and equal to `origin/main` at
  `64409e7fa8d1e1d946479f801dc758fcdecc2ac4` before lane creation;
- Agent Browser issue #159 is closed with repair merge `a23764a1` and closeout
  merge `151ebccd`;
- current physical census found no socket, abstract socket, lock, or X server
  in `:90-:129`; installed Agent Browser reports version `0.28.0`.

Subagent status and reconciliation:

- `not_spawned`; the singleton external attempt remains serialized.

Graphiti write status:

- `not_written`; no memory write was authorized.

Next action:

- publish this authority checkpoint, then run the exact preflight and one
  successor attempt.
