# Handoff: Timed-Polling Service Replan

Date: 2026-08-01

Repository: `/home/ecochran76/workspace.local/last30days-skill`

Purpose: start a fresh session to design the next bounded Plan 0018 packet for
user-configured recurring polling. Do not enable schedules or reopen completed
browser repair work merely while orienting or planning.

## Start Here

Read these authorities in order:

1. `AGENTS.md` and the relevant files under `docs/dev/policies/`.
2. `ROADMAP.md`, especially P07.
3. the latest entry in `RUNBOOK.md`.
4. Plan 0018 checkpoint C37 in
   `docs/dev/plans/0018-2026-07-29-service-first-software-product-transition.md`.
5. `docs/dev/notes/0026-configured-browser-service-campaign-receipt.json`.
6. live service, user-policy, collection, and agent-browser readbacks below.

The receipt owns exact run IDs, job IDs, counts, method provenance, commits,
and validation. Do not reproduce that matrix from chat history.

## Current Outcome

The configured browser transport campaign is complete. The service-first
timed-polling plan is ready for a bounded replan, with source quality kept
separate from transport health:

- production candidates: X `agent_browser`, LinkedIn topic/profile
  `agent_browser`, YouTube `yt_dlp`, and Reddit `keyless` first;
- diagnostic/fallback candidates: Facebook `agent_browser` and Reddit
  `agent_browser`;
- Facebook reached 16 candidates but accepted zero at its quality gate;
- Reddit browser reached seven candidates but rejected all as off topic;
- no recurring collection is enabled;
- Reddit user order is restored to `keyless,agent_browser`.

Installed last30days service truth at handoff:

- version `0.2.20`, schema 12, status `ready`;
- runtime manifest
  `47005b1da4a8ef4b80323db1f2eeafce321883a7b61b265b7893531f30e791ee`;
- 56 documents and 56 embeddings;
- active index `index-c237b6d6591afe53629fe99a`;
- all five configured sources report acquisition ready.

Installed agent-browser truth at handoff:

- binary SHA-256
  `cc22abe43a069e55e2dd46598b3eaa4954ffd4b8859388f646d7761c6c05da60`;
- runtime convergence is `converged`;
- doctor currently reports one `service_duplicate_profile_pressure` warning;
- the warning is not readiness-impacting and comes from two live browsers on
  profile `default`: sessions `default` and `litscout-plan0311`;
- the last30days social lane is singular and ready on profile/session
  `last30days-facebook`;
- do not close or mutate the unrelated LitScout/default sessions without
  separate ownership evidence and authority.

## Git And Installed State

Last30days `main` is locally clean and 36 commits ahead of its upstream:

- `82944d9 docs(plan): close browser service campaign`
- `44a8304 fix(service): label reddit access variants`
- `eb24cdf fix(service): configure durable browser handoff`

Agent-browser `main` is 2 commits ahead:

- `11a276fb fix(remote-view): harden slow page handoff`
- `662050d7 fix(service): preserve handle-bound routing`

Its only worktree entry is the user-owned untracked file
`/home/ecochran76/workspace.local/agent-browser/--full-page`. Preserve it.
Neither repository was pushed, tagged, published, or released by this campaign.

## Validation Already Completed

Primary-agent evidence:

- last30days full suite: 2400 passed, 7 skipped, 6 subtests passed;
- final Reddit provenance focus: 21 passed;
- agent-browser: 32 focused tests passed;
- agent-browser production clippy, route-confusion gates, and docs build passed;
- agent-browser all-target clippy remains blocked by pre-existing test-only
  lint findings unrelated to the handoff slice;
- cold LinkedIn route-bound handoff passed exact target, visible X11 window,
  and operator route in 5.5 seconds;
- Plan authority audit passed at latest Runbook Turn 101.

No subagents were used because the live cases shared one user config, browser
profile/session, and route pool.

Graphiti closeout memory completed in group `last30days_skill_main`:

- job `48efd724-f1ea-46df-9788-9057a6c782b2`;
- episode `3c4bf360-4efd-4443-9d2a-72b5c56c8e5c`.

## Fresh Readback Commands

Run these before making current-state claims:

```bash
cd /home/ecochran76/workspace.local/last30days-skill
git status --short
git rev-list --left-right --count @{upstream}...HEAD

/home/ecochran76/.local/share/last30days/service/last30days-service status
/home/ecochran76/.local/share/last30days/service/last30days-service collection list
stat -c '%a %n' /home/ecochran76/.config/last30days/.env

agent-browser install doctor --json
agent-browser service status --json

uv run python dev/last30days/scripts/audit_plan_authority.py --root .
```

Do not print `.env` values wholesale. Read only the named non-secret policy
keys needed for the plan.

## Next Bounded Planning Packet

The recommended next action is planning, not live enablement. Revise Plan 0018
to define one bounded timed-polling packet for the accepted production set.
The packet should specify:

- per-source interval and freshness objective;
- item, wall-clock, network-request, and cost ceilings;
- user-scoped access order and fallback semantics;
- negative-yield and quality-rejection behavior;
- timer/manual attempt policy, overlap prevention, and profile-lease behavior;
- durable provenance, collection receipt, index-advance, and no-yield evidence;
- rollout sequence, canary duration, rollback, and hard stops;
- whether Facebook and Reddit browser remain disabled diagnostics or receive
  separate quality-successor plans;
- an explicit human gate before enabling recurring production collections if
  the new plan changes live scheduling state.

Do not treat `source.ready=true` as proof of useful yield. Preserve service
health, transport acceptance, content quality, and publication/index outcomes
as separate judgments.

## Hard Stops

- Do not enable, resume, or create recurring live schedules during read-only
  orientation or plan review.
- Do not add credentials, export cookies, mutate social accounts, or broaden
  source/data scope.
- Do not push, tag, publish, release, or rewrite history without explicit
  authority.
- Do not retry consumed campaign identities from receipt 0026.
- Do not weaken Facebook or Reddit quality gates to manufacture acceptance.
- Stop on service integrity/runtime convergence failure, ambiguous profile
  ownership, missing provenance, or a plan that lacks bounded rollback.

## Suggested Skills

- `last30days`: interpret the service/Skill boundary and source behavior.
- `agent-browser`: inspect current broker, profile, session, and route truth.
- `define-architecture`: frame timed polling, policy ownership, and service
  boundaries if the session becomes an architecture decision.
- `handoff`: produce another repo-native continuity note if work crosses a
  session or human gate.

## Best Recommendation

Open a Plan 0018 version-17 timed-polling packet for the accepted production
set, validate it against current live readbacks, and stop for review before any
recurring collection is enabled. Keep Facebook and Reddit-browser quality work
outside that critical path.
