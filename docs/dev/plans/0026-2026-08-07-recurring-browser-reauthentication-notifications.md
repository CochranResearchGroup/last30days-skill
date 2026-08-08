# Plan 0026 | Recurring Browser Reauthentication Notifications

State: CLOSED
Roadmap: P10
Plan version: 12
Date: 2026-08-07

## Objective

Make browser-session authentication expiry an ordinary governed operating
state: Last30Days detects an authentication or checkpoint incident, asks the
operator to reauthenticate through agent-browser, and sends a safe actionable
message through the configured notification chain. The current production
route is Slack Receipts workspace `default`, user reference `@eric`.

## Current State

- Installed service 0.3.20/schema16 is ready with 0.3.19 and 0.3.18 retained;
  the service-owned daily schedule is unchanged and ready for the Aug 9 UTC
  boundary.
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
- Agent-browser remote control is ready, and the retained Facebook browser is
  ready at PID 96078. False CAPTCHA/login notices and the later collection
  timeout are repaired; the final packet emitted no human-action incident and
  completed through navigation and extraction.
- Authentication inspection now skips frozen retained Facebook targets under
  short job deadlines and reuses explicit authenticated DOM or `c_user`
  evidence. Installed proof reached search, extracted 12 candidates, emitted no
  human-action incident, and terminated truthfully at the content quality gate.

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
- order the Facebook command deadlines so agent-browser cancels first, retain
  bounded operation timings in durable tick results, and remove repeated DOM
  subtree scans from extraction.

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
9. A Facebook read uses a shorter cancellation-safe agent-browser job deadline
   than its subprocess deadline, and the following queue command is not delayed
   by abandoned work.
10. Durable provider results retain only bounded, sanitized browser operation
    names, outcomes, error types, and timings needed to diagnose a future
    collection failure.
11. Authentication inspection probes retained Facebook targets under bounded
    deadlines, skips frozen targets without claiming logout, and preserves
    retained tabs rather than closing duplicates.

## Execution Packets And Bounds

| Packet | Outcome | Attempts | Terminal condition |
| --- | --- | ---: | --- |
| S00 plan and baseline | Freeze contracts and runtime routing evidence | 1 | plan/audits pass |
| S01 notification contract | Red/green safe action and link carriage | 1 implementation, 1 rework | focused tests pass or blocker recorded |
| S02 Facebook handoff | Red/green on-demand retained-browser handoff | 1 implementation, 1 rework | focused tests pass or blocker recorded |
| S03 candidate | Version, build, and complete validation | 1 build, 1 review | exact artifact ready or blocker recorded |
| S04 activation | Reconcile agent-browser, install exact candidate, one Slack test | 1 repair, 1 install, 1 message | exact readbacks pass or hard stop |
| S05 collection timeout | Repair timeout ordering, extraction cost, and durable operation evidence | 1 implementation, 1 rework, 1 live proof | one bounded Facebook proof passes or an exact later blocker is recorded |
| S06 responsive target selection | Skip frozen retained Facebook targets without false auth notices or tab closure | 1 implementation, 1 installed proof | one bounded Facebook proof passes or an exact later blocker is recorded |

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
- `skills/last30days/scripts/lib/service_tick_builtin_adapters.py`
- `skills/last30days/scripts/lib/service_tick_runner.py`
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

- all acceptance criteria have current evidence;
- active plan/roadmap/runbook authority and one serial receipt agree;
- exact installed version and rollback are healthy; the validated diff remains
  local and uncommitted because this plan does not authorize a commit or push;
- one compact Graphiti episode records the shipped workflow, or the runbook
  retains the exact bounded write-failure receipt;
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

### Checkpoint P0026-C04 | 2026-08-07

Plan version: 4

State transition:

- `installed_notification_ready_link_gate_blocked -> truthful_checkpoint_repair_in_progress`.

Progress classification:

- `outcome_progress`; agent-browser remote control is now independently ready,
  and the first routine Facebook incident exposed a Last30Days taxonomy defect.

Runtime adjudication:

- installed agent-browser SHA-256
  `8582bf0900b4d974994846c4ff3985746dcbbf5ee2136699f68e56ea5e73726b`
  reports `remoteControl.status=ready` with every prerequisite true;
- the routine Facebook adapter reported the exact safe error
  `checkpoint_required`, but Last30Days canonicalized it to
  `captcha_required`, producing a misleading Slack alert;
- the retained handoff browser was no longer live after the separate
  agent-browser repair cycle, so its stored operator URL is not accepted as a
  current handoff.

Authority classification:

- `inherited_authority`; the operator explicitly requested the repair and a
  bounded resume. No credential, CAPTCHA, checkpoint, or login interaction is
  delegated to Last30Days.

Next action:

- map explicit checkpoints to the existing `reauthentication_required`
  incident gate, preserve literal CAPTCHA classification, validate and install
  one immutable service successor, then resume only the affected Facebook
  handoff and stop at the human gate.

### Checkpoint P0026-C05 | 2026-08-07

Plan version: 5

State transition:

- `truthful_checkpoint_repair_in_progress -> authenticated_dom_false_positive_repair_in_progress`.

Progress classification:

- `validated_learning`; service 0.3.14 corrected the alert taxonomy, and the
  bounded Facebook-only resume exposed the actual detector defect without
  interacting with the page.

Evidence:

- tick `tick-ef09ce739aba02f3afaf7dc4ff20c4af` ran only the Facebook lane,
  consumed one zero-cost provider attempt, and stopped `blocked_human`;
- incident `incident-8ebb4a29d6aa72cf234c9ff6cdc09817`
  correctly used `reauthentication_required` and delivered through Slack
  receipt
  `slack-receipts:sha256:fd6bbd7b25fe0085f11127cdf5404cc02b8a257fca9ae43c362a68f4013c7465`;
- the protected screenshot proves the page was an authenticated Facebook feed;
  a visible Meta help conversation mentioned two-factor authentication, and
  the auth script's global body regex misclassified that incidental text as a
  checkpoint.

Authority classification:

- `inherited_authority`; correcting the false positive and rerunning the same
  one-lane zero-cost packet remains within the operator's repair-and-resume
  instruction.

Next action:

- require checkpoint URL/form evidence or checkpoint-specific text only when
  authenticated DOM is absent, validate and install immutable service 0.3.15,
  then rerun the exact Facebook-only packet once and adjudicate its terminal
  state.

### Checkpoint P0026-C06 | 2026-08-07

Plan version: 6

State transition:

- `authenticated_dom_false_positive_repair_in_progress -> extraction_snapshot_fallback_in_progress`.

Progress classification:

- `blocker_reduction`; service 0.3.15 removed the false authentication gate,
  and the next exact recheck advanced to Facebook search extraction before a
  read-only accessibility snapshot timed out.

Evidence:

- tick `tick-a0769353f394593f0a6da72a9c454fe2` produced zero incidents and zero
  notifications, proving the authenticated page no longer triggers a login or
  checkpoint alert;
- the Facebook-only lane consumed one zero-cost attempt and failed with the
  sanitized code `agent_browser_timeout` after 68 seconds;
- the retained profile browser remains `ready` with PID 96078 and an active
  Facebook search target; an independent read-only interactive snapshot timed
  out after 33.53 seconds, while tab inventory remained responsive.

Authority classification:

- `inherited_authority`; a timeout-specific fallback to the already available
  same-target DOM extraction is the smallest repair that can complete the
  operator's requested resume without browser mutation or another source lane.

Next action:

- validate and install immutable service 0.3.16, run one final Facebook-only
  recheck, and close the plan only if the lane terminalizes without a false
  human incident.

### Checkpoint P0026-C07 | 2026-08-07

Plan version: 7

State transition:

- `extraction_snapshot_fallback_in_progress -> direct_dom_extraction_candidate`.

Progress classification:

- `validated_learning`; the post-timeout fallback was too late because the
  snapshot job consumed the worker window before a provider result could be
  returned.

Evidence:

- tick `tick-7e81dea0eb9ea916393cd946630b2080` produced no incident or
  notification but failed at the worker boundary with zero recorded provider
  usage after 114 seconds;
- a direct read-only evaluation of the installed extraction script on the
  already active Facebook search target completed in 8.14 seconds and returned
  six candidate records without exposing their content;
- the accessibility snapshot is therefore enrichment, not a required first
  read, for this authenticated search page.

Authority classification:

- `inherited_authority`; moving the proven same-target DOM read ahead of
  optional snapshot enrichment is a narrower repair than another timeout or
  browser mutation.

Next action:

- validate and install immutable service 0.3.17, run the exact one-lane packet
  once, and close or terminally checkpoint Plan 0026 from that readback.

### Checkpoint P0026-C08 | 2026-08-07

Plan version: 8

State transition:

- `direct_dom_extraction_candidate -> authenticated_alert_repaired_collection_timeout`.

Progress classification:

- `terminal_checkpoint`; the requested false login/CAPTCHA repair is installed
  and the Facebook workflow resumed past authentication, but ordinary
  collection still terminates on a separate agent-browser timeout.

Final repair evidence:

- service 0.3.17/schema16 is installed `ready`; artifact SHA-256
  `d47aa6e23d433ac044fbc25073296e0775cb4d5c8da5823824e36ef2e14d8826`
  and runtime-manifest SHA-256
  `a3218e755a31c97edbe220d65b665d6d6008db3d52f1ffa3b5ea81e2158392d3`;
- full Python and focused Facebook/incident/runtime/release suites pass, along
  with `git diff --check` and plan-authority validation;
- explicit `checkpoint_required` now maps to
  `reauthentication_required`, while literal CAPTCHAs remain
  `captcha_required`;
- authenticated Facebook DOM suppresses incidental help-chat checkpoint text;
  direct DOM extraction is attempted before optional accessibility snapshot
  enrichment.

Resume evidence and remaining blocker:

- post-repair ticks `tick-a0769353f394593f0a6da72a9c454fe2`,
  `tick-7e81dea0eb9ea916393cd946630b2080`, and
  `tick-eabcf915652f86a91dff60f9b29ce562` created zero incidents and zero
  notification deliveries, so no repeat login notice was emitted;
- the terminal packet ran only Facebook, consumed one zero-cost provider
  attempt, and failed with `agent_browser_timeout` after 70 seconds;
- the installed schedule remains `ready` for `2026-08-09T00:00:00Z`, SQLite
  integrity is `ok`, and no retained or unrelated browser was closed.

Authority classification:

- `inherited_authority`; further retries would repeat the same collection
  timeout without new evidence. Authentication is not the blocker and the
  operator should not log in again.

Next action:

- preserve service 0.3.17 and the live retained browser. Investigate the exact
  later agent-browser operation under a separate bounded collection-timeout
  packet before deriving any additional Facebook source retry.

### Checkpoint P0026-C09 | 2026-08-08

Plan version: 9

State transition:

- `collection_timeout_unattributed -> timeout_layering_repair_active`.

Progress classification:

- `evidence_progress`; the retained browser is authenticated and ready, and
  the exact later failure is now localized to command timeout ordering rather
  than login, CAPTCHA, checkpoint, profile, or route state.

Evidence:

- direct extraction evaluation exceeded Last30Days's 30-second subprocess cap;
- a retained-tab switch exceeded a 12-second client probe and its queued
  restore completed only when the daemon's 30-second command deadline fired;
- the agent-browser control plane already drops a timed-out command future and
  cleans its pending CDP registration, but ordinary CLI commands cannot yet
  request that earlier job deadline;
- Facebook extraction repeatedly scans ancestor subtrees with
  `querySelectorAll`, compounding work on the live search DOM;
- provider acquisition diagnostics contain bounded browser-operation timings,
  but the tick adapter currently drops them before durable result storage.

Authority classification:

- `inherited_authority`; this continues the operator-authorized repair and resume lane
  without another login request, browser launch, browser close, or schedule
  change.

Next bounded action:

- add red contracts at the agent-browser CLI and Last30Days adapter seams, then
  implement the smallest timeout-ordering, extraction, and persistence repair.

### Checkpoint P0026-C10 | 2026-08-08

Plan version: 10

State transition:

- `installed_timeout_repair -> retained_workspace_acquisition_rework`.

Progress classification:

- `blocker_reduction`; agent-browser timeout and handoff ownership are repaired,
  but the first installed 0.3.18 Facebook proof exposed an eager remote-view
  acquisition that precedes authentication inspection.

Evidence:

- agent-browser remote control is ready, installed executable SHA-256 is
  `e899753a27005a79fe820f9128420eb0ea80ed8ea59a8719c64d9bc14c278d5f`,
  and a one-second cancelled eval preserves PID 96078, all seven tabs, and
  active index 3;
- service 0.3.18/schema16 installed ready; its bounded Facebook proof completed
  service access-plan/status in 96/1363 ms, then timed out only the
  `remote_view_open` job at 20 seconds before auth inspection;
- service state already exposes ready browser `session:last30days-facebook`,
  PID 96078, its shared session, seven retained tabs, and a CDP stream, but no
  RDP stream. The adapter therefore requests remote view eagerly even though
  the product contract requires it only after auth/checkpoint detection.

Subagent status:

- none; the primary retains the cross-runtime critical path.

Authority classification:

- `inherited_authority`; this rework enforces the existing on-demand handoff
  scope and uses no additional browser, message, provider, or schedule effect.

Review disposition summary:

- blocking code defect: a ready retained browser without the requested operator
  stream must remain eligible for ordinary CDP collection; absence of the
  external stream is not an auth incident and must not force route acquisition.

Next action:

- add a red retained-CDP/no-RDP acquisition regression, return the retained
  workspace with `operator_visible_state=not_required`, rebuild/install the
  successor, and consume one final bounded Facebook proof.

### Checkpoint P0026-C11 | 2026-08-08

Plan version: 11

State transition:

- `retained_workspace_acquisition_rework -> responsive_target_selection_candidate`.

Progress classification:

- `blocker_reduction`; service 0.3.19 reuses the retained browser, and its
  bounded proof exposed multiple retained Facebook targets with different CDP
  responsiveness rather than an authentication failure.

Evidence:

- the known responsive retained Facebook target returns
  `authenticated_dom=true`, `has_c_user=true`, `login_form=false`, and
  `checkpoint=false` under a three-second job deadline;
- other retained Facebook targets time out during page-domain evaluation even
  though their visible tabs remain logged in;
- focused red/green adapter tests prove that authentication inspection tries
  the active target first, skips a frozen target, reuses a responsive retained
  target, never converts all-frozen targets into `auth_required`, and opens a
  fresh Facebook tab only when no retained Facebook target exists;
- post-search target preservation disables duplicate-tab consolidation so no
  retained operator tab is closed by this repair.

Subagent status:

- none; the primary retains the bounded critical path.

Authority classification:

- `inherited_authority`; this is the smallest evidence-backed continuation of
  the operator-authorized repair and resume, with no login, checkpoint, message,
  schedule, browser-launch, or browser-close effect.

Next action:

- build and install immutable service 0.3.20, run the complete validation set,
  then consume one bounded Facebook proof against the retained authenticated
  browser and close only if the workflow terminalizes cleanly.

### Checkpoint P0026-C12 | 2026-08-08

Plan version: 12

State transition:

- `responsive_target_selection_candidate -> CLOSED`.

Progress classification:

- `outcome_complete`; routine authentication inspection is truthful and the
  installed Facebook lane resumed through navigation and extraction.

Final evidence:

- immutable service 0.3.20/schema16 is installed `ready`; artifact SHA-256 is
  `e7de7efa624dc6f7bdbb46431eb768412774f94b3e0b41cc14e785b3808b5837`
  and runtime-manifest SHA-256 is
  `2ff48ec18f10652bbb4250428b19654f45034b30e85a3366babf623fafe3dd69`;
- full Python validation passed 2,583 tests with 7 skipped and 6 subtests;
  compileall, release/runtime-package tests, plan-authority audit, deterministic
  rebuild, and patch checks passed;
- work `p0026-facebook-live-20260808-01` acquired the retained browser,
  inspected `authenticated=true`, navigated the verified Recent-posts URL,
  extracted 12 candidates, and completed in 33.051 seconds with one zero-cost
  network action, no login/checkpoint/CAPTCHA alert, and no browser timeout;
- the content cohort accepted zero items and returned
  `quality_gate_failed/content`, with truthful rejection counters rather than a
  human-action incident;
- retained browser PID 96078 stayed live; tab count remained eight and active
  index remained 5 before and after proof. No retained tab was closed;
- schedule `daily-default` remains enabled/ready for the Aug 9 UTC boundary,
  SQLite integrity is `ok`, 42 legacy specs remain disabled, all collection,
  tick, and provider attempts are terminal, and no Last30Days systemd timer
  exists.
- compact Graphiti closeout job
  `b99e4bfa-08c2-4ffc-b88e-db51714e2704` timed out after its explicit
  120-second bound before creating an episode UUID; it was not retried.

Subagent status:

- none; the primary completed and independently verified the full critical
  path.

Authority classification:

- `inherited_authority`; the operator explicitly requested repair and resume.

Review disposition summary:

- accepted and repaired: eager operator-view acquisition, timeout layering,
  frozen-target auth selection, and duplicate-tab cleanup;
- correctly terminal content result: current candidates did not pass the date,
  permalink, author, and topic gates; this is not an authentication failure.

Next action:

- stop. Let the normal daily schedule use service 0.3.20; send a manual-auth
  notification only when a future bounded responsive probe proves a real login
  form or checkpoint.
