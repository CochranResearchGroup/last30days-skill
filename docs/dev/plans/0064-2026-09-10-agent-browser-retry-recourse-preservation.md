# Plan 0064 | Agent Browser Retry-Recourse Preservation

State: CLOSED
Roadmap: P08
Plan version: 1
Date: 2026-09-10
Branch: `fix/tick-restart-recovery`
Target: `main`

## Objective

Preserve Agent Browser retry recourse through the Last30days acquisition and
tick pipeline so a provider lane stops when browser effects require inspection,
while configured independent provider fallback remains available.

## Current State

The repair is installed as service 0.3.114. Agent Browser profile
recovery remains external and incomplete: request and job `r348638` stopped at
`lease_authority_protocol_pending_effect_reconciliation`, and read-only
diagnosis `r513089` proves no replacement browser was launched. No research
tick ran in this plan.

## Scope

- retain bounded request ID, job ID, code, phase, effect state, recommended
  action, retry disposition and hard stops from Agent Browser failures;
- carry those fields through provider diagnostics, isolated worker results and
  persisted tick state;
- stop same-provider retries on `inspect_before_retry` or `blind_retry`;
- document the Agent Browser and Last30days ownership boundary in incident note
  0111.

## Non-goals

- running or authorizing another tick;
- repairing Agent Browser profile, lease, browser, runtime or provider state;
- changing provider attempt counts or fallback order;
- persisting page content, authenticated URLs, capabilities or credentials.

## Acceptance criteria

1. Current nested and legacy Agent Browser failure shapes retain only the
   bounded diagnostic fields.
2. Retry policy refuses a same-provider retry for either terminal instruction.
3. An independent configured fallback provider keeps its existing policy.
4. Serialized and restored provider results retain the guidance.
5. X, LinkedIn and Reddit adapters expose the guidance to the tick boundary.
6. Focused tests and Python compilation pass without a live tick.

## Result

All six criteria pass on the 0.3.113 source line and installed service 0.3.114.
The seven focused test modules, Python compilation, 21 release/install tests,
artifact build, transactional install, ready status and SQLite quick check
passed. Ruff was unavailable and was not installed for this bounded repair.
The installed runtime manifest SHA-256 is
`256656fb9f1584ed9f7c4ddf650c51a30de7749f58b639b2d371e10c3d6af7d6`.

The Agent Browser boundary remains tracked in
[incident note 0111](../notes/0111-2026-09-09-plan0063-agent-browser-tick-incident.md).
A future live tick needs separate current authority after Agent Browser repairs
the exact profile and its pending effect state.
