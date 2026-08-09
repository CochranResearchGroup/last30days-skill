# Note 0101 | Plan 0029 Facebook Successor Worker-Boundary Receipt

Date: 2026-08-09
Source plans: Plan 0029 version 4/C04; Plan 0030 version 1/C01

## Rejected Live Receipt

- tick: `tick-2e63a98ad3b92830bee87e61b07cfdf5`;
- execution attempt: `tick-attempt-029f02fdf5e58957fa41b58346e90eab`;
- provider attempt: `provider-attempt-296bd9c8c3a600c379f566d7a884dab3`;
- interval: `2026-08-08T02:00:00Z` through `2026-08-09T02:00:00Z`;
- provider: one `facebook_agent_browser`, no fallback, one-attempt limit;
- result: tick `failed` as `workerexecutionerror`; provider failure class
  `integrity`; no provider result, artifact, evidence, anomaly, incident,
  notification, or budget consumption was staged;
- outcome counts: zero observed, accepted, rejected, and attempted.

## Browser Trace

- retained browser/session: `session:last30days-facebook`, PID 63205;
- bounded retained-tab switches `r589548` and `r229054` each timed out after
  3,000 ms;
- fresh target `r496978`, navigation `r561481`, evaluations `r276858`,
  `r37368`, `r183847`, and `r673990`, and scrolls `r215243` and `r640284`
  succeeded;
- the trace ends after the second default scroll and before another extraction
  evaluation could begin. This is consistent with exhaustion at the worker
  boundary, but 0.3.30 did not preserve the typed worker code;
- no login form, logout, checkpoint, CAPTCHA, organic rate limit, browser
  closure, or tab closure was observed. The one fresh recovery target advanced
  the retained tab count from 18 to 19.

## Successor Repair Receipt

- service 0.3.31 binds Facebook's maximum result target to the governed
  request's admitted item limit; a three-item tick no longer retains the
  default 16-result/two-scroll target;
- typed isolated-worker failures now become durable provider failures with the
  worker's safe code and retry class. A future `worker_timeout` consumes the
  admitted attempt and wall bound instead of collapsing to generic tick
  integrity;
- focused and complete validation passes; reproducible artifact SHA-256 is
  `298958b365932b0fa811d78f94cb3fa71c1fb305e4ba4820d9a60d8d39a57f34`;
- installed service 0.3.31/schema16 is ready; runtime-manifest SHA-256 is
  `15f389ece20f1a5bf9064adfc64e2c604661d1dc587cd91f9672f72bad3e6edf`;
- SQLite quick check is `ok`; releases 0.3.28-0.3.31 are retained; browser PID
  63205 remains ready.

This is an implementation and installed-runtime receipt, not live usability
acceptance. Facebook ticks remain manual until Plan 0030 criterion 6 is proved.
