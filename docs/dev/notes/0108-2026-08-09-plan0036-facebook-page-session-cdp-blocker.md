---
module: facebook
tags: [agent-browser, cdp, runtime-evaluate, target-session, automation]
problem_type: integration-issue
---

# Plan 0036 Facebook Page-Session CDP Blocker

Service 0.3.39 cleared the 10-second tab inventory blocker. Its sole proof
completed exact retained-session inventory and authentication evaluation,
navigated to the verified Facebook search URL, and opened one fresh successor
directly at that URL. Both search targets then stopped answering page-session
CDP commands, so no candidate extraction occurred.

The durable provider ledger is bound to
`provider-attempt-65db1ad398602e6f8c7a259bc47a3e79` and result digest
`sha256:d08753a4e782c82b91bf9036eaa1f78feafae145daa6c0d352aca7f19e7683da`.
It consumed one request and 104 seconds with zero candidates, items, cost,
model tokens, quality rejections, or auth/challenge/rate-limit signals.

Manual investigation proved browser-level CDP remains responsive:
`Browser.getVersion`, `Target.getTargets`, and `Target.attachToTarget` return.
After successful target attachment, neither `Page.getFrameTree` nor trivial
`Runtime.evaluate` returns. Direct page-WebSocket evaluation and agent-browser
eval/snapshot show the same stall.

Do not lengthen the Last30 timeout or retry the provider. The next repair
belongs at the agent-browser or Chromium page-session boundary and must
preserve the retained browser/profile. Cross-repo investigation evidence is
published at agent-browser commit `78c088bc`.
