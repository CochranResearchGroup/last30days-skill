# Note 0103 | Plan 0032 Facebook Hard-Timeout Cleanup Receipt

Date: 2026-08-09
Source plans: Plan 0032 version 3/C04; Plan 0033 version 1/C01

## Rejected Live Receipt

- tick `tick-c9a6b9e9e30d22fbe01328ab1e7ee6d8`, execution attempt
  `tick-attempt-4eac4e2846257f9179a8ddd91428ad18`, and provider attempt
  `provider-attempt-d666f13ccab3f3e7e5d35ed30a808f29` ran exactly once;
- provider result digest
  `sha256:2a745df8b8177db430be8f49e7bd5590c7a0f6bde97c3f3fe6b5a41dbf01b95c`
  is transient `worker_timeout`; attempted/observed/accepted/rejected counts
  are `0/0/0/0`, rejection counts are empty, and no quality rejection exists;
- the tick consumed 120 wall seconds, one attempt, zero requests/items/cost/
  model tokens, and completed `complete_degraded` without retry;
- no auth, CAPTCHA, checkpoint, rate-limit, incident, notification, or browser
  process lifecycle event was reported.

## Tab Lifecycle Evidence

- initial exact inventory contained 16 Facebook tabs among 19 total;
- 0.3.33 and one governed cleanup converged the live session to one Facebook,
  one X, one LinkedIn, and one preview tab while preserving PID 63205;
- the hard-killed live worker bypassed Python `finally` and temporarily left a
  second Facebook tab; one exact manual consolidation restored four total;
- service 0.3.34 moves timeout cleanup to a second source-owned process after
  the parent has killed and reaped the acquisition child. Cleanup is Facebook-
  only, same-site-only, bounded, non-masking, and cannot retry the provider.

## Validation And Installation

- 2,620 Python tests passed with 7 skips and 6 subtests; all Go MCP packages,
  compileall, source-isolation, release/package/authority, and patch checks
  passed;
- reproducible artifact SHA-256 is
  `f1c3043abec18df159f46f8af75b7c4e619b5d4e7bef090de60315f6e59873ad`;
- installed 0.3.34/schema16 is ready with runtime-manifest SHA-256
  `e2d31ce5c6d9d5257eea3317deaa96901aae7737cdb04142c3ff1bc57a0d3231`;
- SQLite is `ok`; schedule `daily-default` is unchanged; browser PID 63205 is
  ready with four live tabs and zero waiting profile-lease jobs;
- copied Skills are synchronized. PromptScript remains truthfully unsupported
  for global Skill installation.

Facebook remains manual and not routine-qualified. Plan 0033 owns one later
0.3.34 proof after `2026-08-09T19:20:00Z`, fresh guards, and no retry.
