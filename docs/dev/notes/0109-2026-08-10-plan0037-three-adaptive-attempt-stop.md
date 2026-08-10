# Plan 0037 Three-Adaptive-Attempt Stop

Date: 2026-08-10
Plan: `docs/dev/plans/0037-2026-08-09-facebook-page-session-cdp-readability.md`
Outcome: attempt ceiling exhausted; Facebook remains not usable

## Adaptation Chain

| Attempt | Installed candidate | Change selected from prior evidence | Result |
|---|---|---|---|
| 1 | 0.3.40 | Replace the frozen target through a blank successor and exact predecessor close so Chromium could not reuse the wedged target. Increase the cumulative budget only enough to contain the already-bounded operations. | Home navigation and auth evaluation returned. Desktop top-search navigation reached its command deadline although the page rendered. |
| 2 | 0.3.41 | Replace top search with the posts-only route because attempt 1 isolated the stall at the search transition. | Posts navigation returned, but the next Runtime evaluation stalled. A separate raw Runtime probe also timed out, rejecting a clock-only explanation. |
| 3 | 0.3.42 | Use mobile posts search and one composite auth/page/extraction Runtime capture so the recovery path needs no later target command. | Mobile redirected to the rendered desktop posts route. The one composite Runtime command timed out after 30 seconds. |

These were not identical retries. Each candidate removed or changed the last
observed failing boundary, was covered by a red regression, passed focused and
canonical validation, was installed with exact artifact/runtime convergence,
and only then consumed one provider attempt.

## Manual CDP Investigation

The deterministic provider receipts were supplemented with direct, read-only
CDP controls:

- browser-WebSocket discovery, target listing, and flattened attachment
  returned normally;
- raw `Runtime.evaluate` through the Facebook page WebSocket and attached
  browser session received no response within bounded 15-18 second probes;
- `Page.captureScreenshot` returned a CDP internal error on the Facebook
  search target;
- the same direct Runtime probe returned on LinkedIn, X, preview, and a new
  tab in the same browser.

This localizes the current blocker to the Facebook search target's page-session
Runtime/renderer path. It is not evidence of logout, CAPTCHA, rate limiting,
browser process failure, JSON parsing failure, or insufficient outer time.

## Final Bound

Attempt 3 ended as `facebook_target_unresponsive` with provider attempt
`provider-attempt-556a632cf7e995cfa8c3fbf079200478`: one request, 105
seconds, and zero observed, accepted, rejected, cost, or model-use counters.
The retained browser, four intended tabs, profile leases, databases, and daily
schedule remain healthy and unchanged. No fourth attempt is authorized.

The next admissible proof follows an installed agent-browser/Chromium repair
that makes a bounded target command return a success or typed protocol failure
on an authenticated disposable Facebook search fixture.
