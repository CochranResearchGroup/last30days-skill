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

The repair is implemented and focused validation passes. Agent Browser profile
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

All six criteria pass. Primary validation ran the seven focused test modules:
245 tests passed and two skipped. Python compilation and `git diff --check`
also passed. Ruff was unavailable in the environment and was not installed for
this bounded repair.

The Agent Browser boundary remains tracked in
[incident note 0111](../notes/0111-2026-09-09-plan0063-agent-browser-tick-incident.md).
A future live tick needs separate current authority after Agent Browser repairs
the exact profile and its pending effect state.

