# Note 0104 | Plan 0033 Facebook Target And Owner Recovery Receipt

Date: 2026-08-09
Source plan: Plan 0033 version 3/C03

## Repair

- service 0.3.35 replaces one rendered-but-CDP-unresponsive Facebook target,
  closes the exact predecessor, retries navigation/readback once, preserves a
  typed failure stage, and caps cumulative adapter work at 75 seconds so the
  parent can still run its bounded cleanup;
- service 0.3.36 repairs retained-owner selection: a ready exact reciprocal
  owner with a live local `cdpEndpoint` and an existing Facebook target remains
  reusable even when the optional CDP screencast viewer is unavailable;
- service 0.3.37 consistently types a timeout during the replacement target's
  initial Facebook navigation as `facebook_target_unresponsive`;
- alias equality, exactly one ready browser, reciprocal active ownership,
  target-service presence, and authentication inspection remain fail-closed.

## Live Receipt

- the predecessor interval preflight resolved to already-terminal tick
  `tick-c9a6b9e9e30d22fbe01328ab1e7ee6d8` and was not enqueued;
- the sole effect-bearing preflight/enqueue created tick
  `tick-b5aa065db0a567dd5e29e3851d1b1858`, lane
  `tick-lane-ee71797f06ddfb474e2515458840fbff`, execution attempt
  `tick-attempt-00d9c50d77c3233d8ca086e2547fe4e4`, and provider attempt
  `provider-attempt-1a06176af35b4e729bd95914bcaacc16` exactly once;
- the provider failed transiently as `agent_browser_error` after six wall
  seconds and one network request with attempted/observed/accepted/rejected
  counts `0/0/0/0`, no quality rejections or page signals, and zero items,
  cost, or model tokens;
- two service reads succeeded and `remote-view` failed. This proves the attempt
  never reached Facebook and does not qualify content acquisition. No retry,
  fallback, login, CAPTCHA/checkpoint interaction, or browser close occurred.

## Validation And Installation

- the 0.3.37 focused Facebook, service-worker, release, runtime-package, and
  authority suites pass; the final canonical full run passed 2,625 tests with
  7 skips and 6 subtests;
- two 0.3.37 service builds are byte-identical at SHA-256
  `d1344ed74b8ac3d9ee277fc676dc17e8967f79404701363aee1d7801701a82b3`;
- installed 0.3.37/schema16 is ready with runtime-manifest SHA-256
  `43e95736825389d6840c79d49be9864123ef71238a3f9eddb0fc52035889cc91`;
- installed pure-function readback resolves browser
  `session:last30days-facebook`, session `last30days-facebook`, and Facebook
  target `1D0EE09568AB75971C4850E7D89783F4` without a launch command;
- agent-browser 0.28.0 workstation state is installed and converged at
  executable SHA-256
  `01965e35f09883522ca281fcd66657a6d8d372dcda8797eca7fe260c6f8b4c9b`;
  remote control is ready and both install readiness gates are true.

Facebook remains manual and not routine-qualified. The next live proof must be
a separately guarded successor checkpoint; it must not retry the consumed tick.
