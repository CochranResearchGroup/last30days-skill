# Plan 0026 | Recurring Browser Reauthentication Notifications

State: OPEN
Roadmap: P10
Plan version: 3
Date: 2026-08-07

## Objective

Make browser-session authentication expiry an ordinary governed operating
state: Last30Days detects an authentication or checkpoint incident, asks the
operator to reauthenticate through agent-browser, and sends a safe actionable
message through the configured notification chain. The current production
route is Slack Receipts workspace `default`, user reference `@eric`.

## Current State

- Installed service 0.3.13/schema16 is ready with 0.3.12 and 0.3.11 retained;
  the daily schedule is unchanged and ready for the Aug 8 UTC boundary.
- Browser incidents carry a validated external HTTPS operator link into the
  existing idempotent Slack/email chain. Resolutions omit stale links, and an
  unavailable handoff preserves the source incident and sends a no-link manual
  intervention notice.
- Facebook prepares a handoff on demand against the retained browser only
  after `remoteControl.status=ready`; it additionally requires
  `operatorVisible.state=ready` and an external HTTPS URL before carriage.
- The private route remains Slack Receipts `default/@eric` first with hourly
  reminders and email fallback. One labeled no-action validation message was
  delivered with receipt
  `slack-receipts:sha256:4cb4078685bcd3551ac49bc17cb9d24a58432e7a140c0b4ca50681056c392287`.
- Agent-browser workstation and dashboard payload drift reconciled, but doctor
  still reports `needs_browser_launch_prerequisites` solely because of global
  duplicate-profile warnings; `readinessImpactingCandidates=0`. No retained or
  unrelated session was closed, and no live operator link is claimed ready.

## Scope

- carry a validated external operator URL and a bounded manual action through
  incident notification payloads;
- render a direct reauthentication/checkpoint link in Slack and email messages
  only when agent-browser has proved a ready operator-visible route;
- on Facebook authentication/checkpoint detection, prepare that route on demand
  through the retained canonical browser/profile rather than opening a second
  profile lane;
- preserve existing incident idempotency, hourly reminders, sequential
  transport failover, one-time resolution messages, and protected artifacts;
- validate and install one exact service successor, reconcile agent-browser
  readiness, and send one clearly labeled Slack validation message to the
  configured default-tenant `@eric` route.

## Non-Goals

- no automated credential entry, MFA, CAPTCHA, checkpoint, consent, or account
  recovery;
- no direct Slack Web API calls and no Slack channel-ID or stale-DM binding;
- no browser/profile duplication, cookie export, credential storage, or local
  dashboard URL in notifications;
- no schedule cadence, source set, provider order, cost/model, database schema,
  or legacy collection-spec change;
- no automatic retry of the blocked source until the operator completes the
  handoff and a separately bounded verification run is derived.

## Acceptance Criteria

1. `auth_required`, `checkpoint_required`, CAPTCHA, and equivalent browser
   incidents emit an actionable manual-auth message through the existing
   notification chain.
2. A message includes a link only when it is external HTTPS and the
   agent-browser handoff reports `remoteControl.status=ready` plus
   `operatorVisible.state=ready`.
3. Facebook prepares the handoff on demand against the retained canonical
   browser/profile and does not create a duplicate profile lane.
4. Duplicate detections reuse the incident and delivery; unresolved incidents
   remind no more often than `notifications.reminder_seconds`; resolution is
   delivered once.
5. Slack delivery remains child-owned by Slack Receipts and targets configured
   workspace `default`, user reference `@eric`, with stable idempotency.
6. Messages contain no cookies, credentials, page bytes, local URLs, raw
   private page content, browser IDs, session IDs, routes, or displays.
7. Exact candidate tests/build/install pass while the service-owned daily
   schedule, database integrity, disabled legacy specs, zero-cost posture, and
   rollback remain intact.
8. One labeled Slack validation message returns a durable Slack Receipts
   delivery reference before the workflow is called active.

## Execution Packets And Bounds

| Packet | Outcome | Attempts | Terminal condition |
| --- | --- | ---: | --- |
| S00 plan and baseline | Freeze contracts and runtime routing evidence | 1 | plan/audits pass |
| S01 notification contract | Red/green safe action and link carriage | 1 implementation, 1 rework | focused tests pass or blocker recorded |
| S02 Facebook handoff | Red/green on-demand retained-browser handoff | 1 implementation, 1 rework | focused tests pass or blocker recorded |
| S03 candidate | Version, build, and complete validation | 1 build, 1 review | exact artifact ready or blocker recorded |
| S04 activation | Reconcile agent-browser, install exact candidate, one Slack test | 1 repair, 1 install, 1 message | exact readbacks pass or hard stop |

- Critical-path owner: primary agent. No subagent is authorized or needed for
  this tightly coupled cross-runtime slice.
- Live Facebook acquisition attempts: zero in this plan until manual checkpoint
  completion; a notification validation is not a source retry.
- Slack external effects: exactly one clearly labeled validation message during
  activation. Routine future messages are incident-driven and idempotent.
- Hard stop on identity ambiguity, non-ready remote control, missing external
  HTTPS operator URL, duplicate profile pressure after one reconciliation,
  notification rejection, schedule drift, paid/model use, or unsafe worktree.

## Owned Write Surfaces

- `skills/last30days/scripts/lib/facebook.py`
- `skills/last30days/scripts/lib/service_tick_incidents.py`
- `skills/last30days/scripts/lib/service_tick_notifications.py`
- focused tests for those surfaces
- service version/runtime manifest and required user-facing configuration docs
- `ROADMAP.md`, `RUNBOOK.md`, this plan, and serial validation receipts
- exact installed Last30Days release and private routing config only if a
  config change is actually required; current evidence says it is not.

## Gates And Authority

- The operator explicitly requested routine manual reauthentication messages
  via agent-browser and Slack Receipts to default-tenant `@eric`; that is the
  authority for this successor lane and its one labeled validation message.
- The operator must perform the actual login/checkpoint interaction. Last30Days
  may prepare and send the handoff but must never perform the human action.
- Agent-browser doctor and the final open response are authoritative for link
  readiness. A merely live Chrome process or retained URL is insufficient.

## Definition Of Done

- all eight acceptance criteria have current evidence;
- active plan/roadmap/runbook authority and one serial receipt agree;
- exact installed version and rollback are healthy and origin contains the
  validated commit;
- one compact Graphiti episode records the shipped workflow or exact blocker;
- remaining manual Facebook completion stays an explicit operator action, not
  a hidden implementation retry.

### Checkpoint P0026-C01 | 2026-08-07

Plan version: 1

State transition:

- `facebook_checkpoint_human_gate -> recurring_reauthentication_workflow_active`.

Progress classification:

- `outcome_progress`; the operator converted a one-off checkpoint into an
  explicit recurring product requirement and named the delivery tenant/user.

Evidence:

- installed service 0.3.11 is ready; current private notification routing is
  Slack Receipts `default/@eric` first with hourly reminders and email fallback;
- Slack Receipts default tenant is enabled, credential-ready, live, and passes
  explicit-outbound workspace verification;
- CodeGraph confirms existing incident deduplication/reminder/resolution,
  operator-URL storage, and the missing notification-link carriage seam;
- agent-browser requires doctor-ready remote control and an operator-visible
  ready response before a handoff link may be sent.

Subagent status:

- no subagent used; the primary owns the critical path.

Authority classification:

- `scope_expansion`; the operator explicitly added agent-browser handoff and
  default-tenant Slack delivery to the Last30Days product workflow.

Review disposition summary:

- accepted blocker: notification payload/message omits the stored operator URL;
- accepted blocker: Facebook does not prepare a route after a retained shared
  browser discovers an authentication checkpoint without a ready stream;
- accepted runtime blocker: remote-control workstation drift must reconcile
  before a link is called ready.

Graphiti status:

- deferred until implementation or a durable terminal blocker is validated.

Next action:

- add red tests for safe notification link carriage and on-demand Facebook
  handoff preparation, then implement the smallest shared contract change.

### Checkpoint P0026-C02 | 2026-08-07

Plan version: 2

State transition:

- `recurring_reauthentication_workflow_active -> exact_candidate_installed`.

Progress classification:

- `outcome_progress`; the red seams are green, the notification path is
  installed, and default-tenant Slack delivery is independently proven.

Implementation and evidence:

- incident delivery payloads now carry the stored operator URL;
- browser messages render a manual action and link only for external HTTPS,
  while resolution omits the stale link and unsafe routes remain absent;
- Facebook doctor-checks and opens an operator view against the retained
  browser on auth/checkpoint detection, then requires visible-ready readback;
- a handoff-readiness failure preserves the source auth/checkpoint incident so
  ordinary notification still occurs without a link;
- exact service 0.3.13 is installed ready on schema 16 with runtime-manifest
  SHA-256 `88c516db666a2c5ca2323d5f1e0fe4ae1fba679f0d31b76e366b61938241074b`;
- full Python suite exits zero, focused Facebook/incident/runtime tests and
  compileall pass, the daily schedule remains ready for Aug 8, and SQLite is
  `ok`;
- the one authorized Slack validation message returned receipt
  `slack-receipts:sha256:4cb4078685bcd3551ac49bc17cb9d24a58432e7a140c0b4ca50681056c392287`.

Authority classification:

- `inherited_authority`; implementation, immutable 0.3.13 rework, exact
  install, and the single labeled Slack effect remain within the operator's
  recurring-handoff request.

### Checkpoint P0026-C03 | 2026-08-07

Plan version: 3

State transition:

- `exact_candidate_installed -> installed_notification_ready_link_gate_blocked`.

Progress classification:

- `blocker_reduction`; the product and delivery path are live, but the current
  agent-browser runtime cannot truthfully create a manual link.

Runtime adjudication:

- workstation refresh and dashboard convergence removed payload/runtime drift;
- the only remaining install-doctor issue is
  `service_duplicate_profile_pressure`, with zero readiness-impacting cleanup
  candidates;
- the two Last30Days session names resolve to the same retained Facebook
  browser, while other duplicate warnings belong to unrelated profiles;
- policy and this plan therefore forbid closing those sessions or publishing a
  link while `remoteControl.ready=false`.

Authority classification:

- `human_gate`; literal Facebook checkpoint completion remains operator-only,
  and further agent-browser repair would expand beyond this plan's consumed
  reconciliation packet.

Current authority:

- P0026-C03 is the current authority. Keep Plan 0026 `OPEN` with the exact
  agent-browser readiness blocker; routine incidents still notify safely
  without a link.

Next action:

- repair agent-browser's duplicate-profile readiness adjudication without
  closing retained or unrelated sessions, require
  `remoteControl.status=ready`, then allow the next real incident to open and
  send its operator-visible external HTTPS link. Do not retry Facebook now.
