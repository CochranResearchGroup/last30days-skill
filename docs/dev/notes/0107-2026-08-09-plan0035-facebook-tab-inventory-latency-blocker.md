---
module: facebook
tags: [agent-browser, cdp, timeout, automation, retained-session]
problem_type: integration-issue
---

# Plan 0035 Facebook Tab Inventory Latency Blocker

The first post-0.3.38 Facebook-only proof did not reach page evaluation.
Provider attempt `provider-attempt-746e9438cb50a275aa04bd6572bcc74c`
completed its access-plan and service-state reads in 716 and 4,252
milliseconds, then hit the adapter's fixed 10-second `tab list` timeout at
10,025 milliseconds.

Raw CDP discovery showed the retained Facebook target was live. The exact
session-scoped command subsequently succeeded four times; three measured
sequential reads took 8.4-8.8 seconds and returned the four intended tabs with
Facebook active. This isolates inadequate jitter margin in the 10-second
read-only inventory allowance.

An unscoped explicit-CDP experiment failed because another `shared-social`
browser held the default runtime-profile lock. Do not conflate that diagnostic
with the provider failure: the production adapter uses the exact retained
session, and that route is responsive.

Repair by widening only session tab inventory to 20 seconds while preserving
the independent 75-second cumulative adapter budget. Do not add provider
retries, launch another browser, or treat CDP liveness as content success.
