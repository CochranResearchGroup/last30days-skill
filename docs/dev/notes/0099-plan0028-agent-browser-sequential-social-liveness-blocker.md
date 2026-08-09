# Note 0099 | Agent-Browser Sequential Social Liveness Blocker

Date: 2026-08-08
Owner: agent-browser investigation
Source plan: Plan 0028 version 7/checkpoint P0028-C07

## Request

Investigate why a retained shared browser can remain service-health `ready`
while a newly created Facebook target cannot complete a bounded CDP evaluation
after the X adapter has just used the same session. Do not repair Facebook DOM
selectors or relax last30days quality gates; direct and exact-post-tick tests
already prove those semantics.

## Environment And Safety Boundary

- agent-browser version: 0.28.0;
- executable: `/home/ecochran76/.local/bin/agent-browser`;
- executable SHA-256:
  `266103ec1e05c2cd216bbffbcc49610abf998be5dce1032265f94f180d786e76`;
- retained session: `last30days-facebook`;
- retained browser: `session:last30days-facebook`, PID 96078;
- service metadata profile: `default`; access-plan product profile:
  `last30days-facebook`;
- current service status: browser health ready, one writable ready
  `cdp_screencast` stream, 15 retained tabs;
- do not close tabs, restart or replace the browser, create a duplicate profile,
  automate login/checkpoint/CAPTCHA, expose page/chat content, or change the
  recurring schedule. Read-only status/job/target inspection is authorized.

## Proven Last30days Behavior

Working-tree Facebook execution from the exact post-tick browser state succeeds:

- bounded service acquisition reuses the exact configured session and canonical
  browser ID;
- at most two retained Facebook targets are probed;
- one fresh Facebook target is created and navigated with a single
  `tab new https://www.facebook.com/` command;
- the fresh auth evaluation uses a 15-second inner job deadline and 20-second
  process deadline;
- the run observed three candidates, accepted two dated in-range posts, rejected
  one ad, and completed browser work in about 91 seconds under the 120-second
  provider limit.

Installed sequential execution fails before Facebook content:

- service version 0.3.26, schema 16, runtime-manifest SHA-256
  `189680b97f4c5ca9b838a4ea1e960dcc95c169f275fb2a11fd3684926253d982`;
- tick: `tick-d08819fc38346ad98f8eb070267d1076`;
- Facebook provider attempt:
  `provider-attempt-3b81211ca0a73be9481fa6262d1b59f8`;
- X immediately before Facebook ran for 84 seconds and returned
  `quality_gate_failed` with 16 observed and 16 rejected candidates;
- Facebook then listed tabs successfully, bounded two retained selection
  timeouts, created the combined fresh target successfully, and timed out only
  on the fresh target's 20-second auth eval;
- Facebook usage: one attempt, one governed network request, 55 wall seconds,
  zero observed/accepted items, zero cost/model tokens;
- no incident or notification was emitted; LinkedIn subsequently succeeded.

The immediately preceding 0.3.25 attempt shows the same family with the older
recovery shape:

- tick: `tick-a070c5b89c0d9b94a8f1708635b49357`;
- Facebook attempt: `provider-attempt-4262c1862ff1f05b3adfbf19acd03ecc`;
- eight retained-tab timeouts, fresh target opened, then 8-second auth eval
  timed out; zero observed/accepted candidates.

## Questions For Agent-Browser

1. Does the X operation leave a serialized job, active-target pointer, CDP
   session, or page lifecycle wait that outlives the provider command while
   service health still reports `ready`?
2. Does `tab new <url>` update the daemon's active target deterministically
   before the next stdin `eval`, especially after prior tab-selection timeouts?
3. Can status/readiness distinguish a browser whose CDP endpoint is alive from
   a selected target whose main thread or agent-browser command queue cannot
   answer within 20 seconds?
4. Are timed-out tab/eval jobs cancellation-safe and fully removed from the
   per-session serialized queue before the next provider begins?

## Acceptance Evidence Needed

- provider-free or fixture-backed reproduction of X-like long work followed by
  a fresh Facebook target and stdin eval on the same retained session;
- proof that the eval targets the newly created target and completes within the
  existing 15-second job/20-second process bounds, or a truthful typed readiness
  failure before last30days spends its provider attempt;
- proof that timed-out jobs no longer delay later commands in the same session;
- retained PID/profile/tabs remain intact and no private page content is stored
  in the investigation artifact.

Do not ask last30days to retry 0.3.26. Return a versioned agent-browser repair or
an exact contract change that last30days can consume in one distinct successor
and one manually preflighted proof tick.

## Resolution | 2026-08-08

No agent-browser source change was required for this blocker. Current job
evidence proved that agent-browser's worker deadline excludes queue wait: both
retained tab-switch jobs succeeded after their prior 8-second Last30Days callers
had already exited. The fresh evaluation then independently hit its 15-second
worker limit and returned through the repaired outer bound.

Last30Days service 0.3.28 consumes that contract by keeping retained worker
limits at 3 seconds while allowing 15 seconds of caller time, and by reserving a
30-second worker / 45-second caller bound for a genuinely fresh auth target.
Manual tick `tick-f273eb12d642b31d49a7f12959b93b87` closes the handoff:
Facebook attempt `provider-attempt-5e5205b623e52dfd122dbbf2e4e668af`
is `success` with 19 observed, two accepted, and 17 rejected candidates. All
browser operations succeeded, PID 63205 remains ready on the canonical profile
with 17 tabs, and no duplicate browser or tab closure occurred.
