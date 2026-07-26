# Post-Reboot Fresh-Session Handoff

Date: 2026-07-26

## Purpose

Resume the last30days productization work from current installed and runtime
truth after the workstation reboot. Do not reopen Plans 0010 or 0011: both are
closed. Use this handoff to decide and authorize the next bounded validation or
successor implementation plan.

## Read First

1. `AGENTS.md`
2. this handoff
3. `ROADMAP.md`
4. `RUNBOOK.md`, especially Turns 28 and 29
5. `docs/dev/plans/0011-2026-07-25-integrated-temporal-intelligence-service.md`
6. `docs/dev/plans/0002-2026-07-15-linkedin-agent-browser-scraper.md`
7. the relevant policies under `docs/dev/policies/`

Suggested skills:

- `repo-policy-selector` for the next plan or implementation slice
- `agent-browser` for profile, route, and remote-view truth
- `last30days` for installed service and source canaries
- `diagnosing-bugs` if a canary produces a stable adapter failure
- `codegraph-workspace` before structural code investigation
- `graphiti-discovery` before Graphiti projection or retrieval work

## Durable Baseline

- Branch `main` was clean and matched `origin/main` at `3ed6cb0` before this
  handoff was written.
- The integrated foundation milestone is closed. The installed user-scoped
  service is version `0.2.7`, database schema `12`.
- The corpus currently reports 43 documents, 43 embeddings, and 6
  relationships. Source counts are Facebook 4, LinkedIn 4, Reddit 19, X 14,
  and YouTube 2.
- No recurring authenticated timer was enabled at closeout.
- Graphiti closeout authorities:
  - agent-browser episode `f0e2ccb4-ba46-4242-a74e-2903a992ccea` in
    `agent_browser_main`;
  - last30days job `6bcf1bfd-31e2-406b-a469-13ac8b6ecfa5`;
  - last30days episode `3b68fd75-5a06-49b2-99f2-2039e1b00715` in
    `last30days_skill_main`.

## Post-Reboot Runtime Readback

The reboot occurred at `2026-07-26 07:53:40` local time.

### last30days

- `last30days.service` is enabled and active.
- Installed service status is `ready`, version `0.2.7`, schema `12`, over its
  Unix transport.
- All five cataloged sources report acquisition-ready. This is service/catalog
  readiness, not fresh post-reboot acquisition proof.

Readback:

```bash
systemctl --user is-enabled last30days.service
systemctl --user is-active last30days.service
/home/ecochran76/.local/bin/python3 \
  /home/ecochran76/.agents/skills/last30days/scripts/service.py status
```

### Graphiti

- The MCP server reports `ok` and is connected to FalkorDB.
- The in-process queue is idle: no active or queued memory jobs.
- The latest reviewed operator batch remains paired and completed with one
  verified readback.
- Historical queue totals include timed-out and failed jobs; do not confuse
  those cumulative counters with a current queue failure.

### agent-browser

- Installed agent-browser is version `0.27.0`; runtime convergence is current
  and the dashboard, Chromium bundle, and remote-view privilege helper are
  present.
- The canonical persisted profile is `last30days-facebook`, with retained
  target-readiness evidence for Facebook, LinkedIn, and X.
- Identity-specific lookups select that profile correctly:

```bash
agent-browser service profiles lookup \
  --service-name last30days --target-service-id x --json
agent-browser service profiles lookup \
  --service-name last30days --target-service-id facebook --json
agent-browser service profiles lookup \
  --service-name last30days --target-service-id linkedin --json
```

Each lookup matches `authenticatedServiceIds` with reason
`authenticated_target`. Use these fields instead of fuzzy `--search`.

- There is no live last30days browser, session, or tab after reboot.
- The retained route `guacamole:4` is orphaned/unavailable because its display
  socket is missing. Profile lookup therefore recommends `launch` and reports
  `routeAvailable: false`.
- `agent-browser doctor remote-view --json` is blocked for actual operator
  control and many-to-many proof: zero selected live RDP Guacamole
  connections, missing route displays, and no distinct live RDP targets.
  Guacamole, guacd, XRDP, the public route, display allocation, and the
  privilege helper are otherwise reachable.
- The general install doctor also reports duplicate-profile pressure. Its
  resource report found two warnings but no readiness-impacting cleanup
  candidates. Do not delete profiles or leases without resolving exact
  ownership.

Interpretation: the authenticated profile data persisted, but Facebook,
LinkedIn, and X authentication has not been proven live since this reboot. The
current blocker is route/display recovery, not evidence that any account is
logged out. Do not request reauthentication until a live route has been
restored and a bounded DOM probe actually shows a login or challenge surface.

## Best Next Test

Run one serialized post-reboot social canary packet before hydrating more data
or enabling timers:

1. Reconcile the agent-browser service and restore one Guacamole/RDP desktop
   for `last30days-facebook`. Require a live X11 display socket and
   `routeAvailable: true`; retained route metadata alone is insufficient.
2. Open that route from the dashboard and prove the user can see and control
   it. If multiple-client support is in scope, require two independent clients
   before claiming many-to-many readiness.
3. Without navigating away or launching another profile, run bounded DOM auth
   probes for X, Facebook, and LinkedIn on the canonical shared browser.
4. Only if all three probes are authenticated, run exactly one serialized
   acquisition canary per source. Verify published item count, immutable
   version/sighting provenance, source account, acquisition ID, and duplicate
   behavior.
5. Stop and preserve evidence on the first stable failure. Use deterministic
   stage/signature classification before authorizing App Intelligence repair.

This packet has the highest information value because it separates reboot
recovery defects from adapter/auth defects and tests the shared-profile
contract the timers will depend on.

## Tests After The Social Canary

In priority order:

1. **YouTube transcript and media path.** Fetch one new transcript from a
   subscribed channel, then download one bounded media item. Confirm the
   installed `yt-dlp` path/version, the `../transcribe-audio` handoff, provenance,
   and cleanup behavior. Do not treat binary presence as a successful source.
2. **Recurring timer durability.** Enable one low-risk public-source spec for
   two intervals with a service restart between them; prove cursor continuity,
   budgets, immutable deduplication, and coverage, then pause it. Keep
   authenticated timers disabled until the social canary is clean.
3. **Cache-only retrieval.** From a fresh MCP client, query an existing topic
   with temporal `as_of` and profile filters. Prove no acquisition job is
   enqueued and citations resolve to immutable evidence.
4. **GraphRAG resilience.** Replay one existing projection idempotently, verify
   Graphiti readback, then test the documented local-evidence fallback with the
   projection provider unavailable. Do not generate broad new graph writes for
   this test.
5. **App Intelligence contracts.** Dry-run one accepted and one rejected task
   envelope, replay them deterministically, and verify finite item, byte, call,
   cost, and time limits. No stochastic browser action should bypass the
   deterministic supervisor.
6. **Profile discovery regression.** Add coverage for canonical selection by
   service plus target identity and for duplicate-name/fuzzy-search ambiguity.
   Earlier fuzzy searches selected unrelated custom profiles; identity-specific
   lookups now select the correct shared profile.

## Stop Conditions

- Stop before login mutation if the route is not operator-visible.
- Stop and ask the operator only after a live DOM probe proves authentication
  or challenge is required.
- Stop after one stable repeated adapter signature; preserve the failure
  envelope instead of retrying broadly.
- Do not enable recurring authenticated hydration during the validation packet.
- Do not perform Graphiti batch writes without provider readiness, an
  allow-listed target group, reviewed input, and read-after-write proof.
- Broad implementation beyond these checks needs a successor plan and explicit
  bounded authorization. Plans 0010 and 0011 remain historical authorities.

## Closeout Expected From The Next Session

Record:

- exact route/profile/browser/display IDs and live readiness;
- per-source post-reboot authentication and acquisition outcomes;
- durable item/version/sighting/projection receipts;
- whether any failure is route recovery, auth, adapter, or publication;
- commands and validation results;
- current commit, push, installed-service, and runtime state separately;
- a compact Graphiti memory if a durable decision or runtime lesson was
  established.

