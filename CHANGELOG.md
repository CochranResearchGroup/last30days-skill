# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

- **X authentication and recovery-notice truthfulness.** Service 0.3.52 keeps
  `auth_required` for an observed X login surface and reports an inconclusive
  rendered page as `auth_state_ambiguous` instead of asserting the user is
  logged out. Resolved Slack notices now lead with resolved status and label
  the historical incident classification and summary as previous state, so a
  successful recovery no longer resembles a fresh authentication alert.

- **Operator-ingress alert classification.** Service 0.3.51 classifies an
  unavailable Guacamole/dashboard route as `provider_degraded` and states that
  authentication was not determined. Genuine login-page and checkpoint
  signals still produce `reauthentication_required`; source configuration,
  schedules, browser state, and notification transports are unchanged.

- **X attached-context recovery and rejection receipts.** Service 0.3.50
  evaluates bounded quoted-post text and meaningful media alt text alongside
  the outer X post caption, allowing short real posts to pass the existing
  length and relevance gates when their attached context supplies the evidence.
  Rejections now include bounded, content-free receipts with the reason,
  native status ID, text/context lengths, quote presence, and media count so
  scraper limitations can be distinguished from legitimate quality drops.

- **LinkedIn activity-URN recovery.** Service 0.3.49 traverses each post
  card's bounded React props graph before falling back to the larger React
  fiber graph. This recovers canonical activity URLs for ordinary LinkedIn
  posts whose fiber state previously exhausted the shared traversal budget;
  sponsored detection, content quality gates, navigation, source budgets, and
  timer configuration are unchanged.

- **LinkedIn literal-now timestamp extraction.** Service 0.3.48 retains
  visible `now` and `just now` lines, including LinkedIn's bullet suffix,
  through the existing plain-text timestamp fallback. This lets the already
  strict date parser normalize fresh posts instead of rejecting them as
  `missing_date`; selectors, navigation, relevance, duplicate handling,
  budgets, source configuration, and derivative processing are unchanged.

- **Facebook prepared-extraction freshness.** Service 0.3.47 preserves the
  combined replacement-target auth/page/extraction capture when it contains
  candidates or rate-limit evidence, but refreshes an empty immediate capture
  after the configured settle wait before deciding whether scrolling is
  necessary. This prevents stale post-navigation emptiness from forcing a
  renderer-stalling scroll while retaining the existing non-empty single-read
  fast path and all parent budgets.

- **Facebook combined-capture deadline.** Service 0.3.46 gives the existing
  single combined Facebook query capture a 45-second inner job deadline inside
  a 50-second outer waiter. The change stays within the existing 105-second
  adapter and 120-second parent budgets and adds no command, target, retry,
  browser/profile effect, or source request.

- **Facebook late browser-operation reconciliation.** Service 0.3.45 keeps a
  ten-second reserve inside the bounded Facebook adapter run when remote-view
  acquisition is required. If the CLI waiter returns a typed browser error or
  timeout, the adapter performs one read-only service-status reconciliation and
  accepts only an already-ready browser owned by the exact selected profile or
  the existing narrow retained-default alias. It does not retry the request,
  relaunch Chrome, create a duplicate profile lane, or weaken authentication,
  challenge, rate-limit, and profile checks.

- **X evidence identity and profile-aware cache retrieval.** Service 0.3.44
  derives durable X source identity from the canonical numeric status ID while
  preserving short display IDs, preventing later runs from attaching new text
  to an older status URL. Source-filtered queries now use the newest promoted
  or superseded terminal snapshot whose completeness receipt covers the exact
  requested sources, while unfiltered queries retain the ordinary singleton
  head. MCP adapter 4.0.3 validates and forwards `profile_id` on query and
  refresh so an authorized named profile can retrieve its own partition.

- **MCP schema-16 release identity and installed convergence.** MCP adapter
  4.0.2 is explicitly bound to the canonical schema-16 catalog digest and
  service/database compatibility ranges. A checked-in compatibility-release
  lock now makes generation and Codex installation fail closed when a catalog
  change reuses an unbound adapter version, preventing a stale binary from
  sharing the same visible release identity as newer contract source.

- **Retained social navigation deadline ordering.** Service 0.3.43 gives
  navigation through the shared Facebook/X browser adapter an explicit
  25-second agent-browser job deadline inside its 30-second Python subprocess
  deadline. The repaired agent-browser worker can now return a typed
  navigation result and preserve five seconds for response delivery and
  adapter cleanup instead of racing equal outer and inner clocks. Target URLs,
  Facebook's one-successor bound, profiles, schedules, cost, and model-use
  contracts are unchanged.

- **Facebook mobile single-capture recovery.** Service 0.3.42 uses the
  authenticated `m.facebook.com/search/posts/` surface when a retained desktop
  target is frozen. Its one replacement navigation performs a single bounded
  Runtime capture containing authentication, page-state, and extraction data,
  then reuses that capture through quality gating without another target
  command. Ordinary responsive retained-target behavior is unchanged; browser
  restart, profile mutation, retry growth, cost, and model use remain absent.

- **Facebook post-specific search surface.** Service 0.3.41 navigates directly
  to `/search/posts/` with the existing recent-post filter after an installed
  0.3.40 proof showed `/search/top/` rendered the requested results but wedged
  its Runtime channel. Query, filter, authentication, one-successor,
  extraction, quality, parent-wall, and cleanup gates remain unchanged.

- **Facebook renderer-isolating recovery.** Service 0.3.40 replaces a frozen
  Facebook target with `about:blank`, closes the exact predecessor, and only
  then navigates the successor to Facebook. This prevents Chromium from
  reusing the same stalled same-site renderer observed when 0.3.39 left the
  predecessor alive. The default Facebook adapter allowance is 105 seconds
  beneath the unchanged 120-second parent worker boundary, preserving room
  for the bounded replacement sequence and cleanup. Recovery remains limited
  to one successor and never restarts the browser or profile.

- **Facebook retained-session inventory latency.** Service 0.3.39 gives the
  read-only authenticated-session tab inventory up to 20 seconds after an
  installed proof timed out at 10,025 milliseconds and three exact-session
  diagnostics completed in 8.4-8.8 seconds. The independent 75-second
  cumulative adapter budget still clamps the command, and no retry, browser
  launch, profile reassignment, or schedule change is introduced.

- **Facebook recovery-budget preservation.** Service 0.3.38 bounds the
  navigation-only page-state probe separately from extraction, opens its sole
  recovery target directly at the verified Facebook URL, and defers exact
  same-site duplicate closure to the existing guaranteed cleanup. This removes
  the redundant blank-target navigation, identity inventory read, second open,
  and local post-open wait that exhausted the 75-second adapter budget in three
  observed attempts. Owner/profile, explicit-auth, challenge, rate-limit,
  query/filter, one-successor, typed-terminal, parent-wall, and one-final-target
  gates remain unchanged. No live Facebook tick is part of this release.

- **Facebook replacement-navigation classification.** Service 0.3.37 applies
  the same `facebook_target_unresponsive` classification when the one exact
  replacement target times out during its initial Facebook navigation as when
  its subsequent authentication read times out. This closes the final generic
  timeout seam without adding a target, provider attempt, or retry.

- **Facebook retained-owner CDP reuse.** Service 0.3.36 reuses the exact
  reciprocal owner of the configured Facebook session when its ready browser
  exposes a live `cdpEndpoint`, even if the optional CDP screencast viewer is
  unavailable. Profile alias, one-browser ownership, health, session
  reciprocity, and an existing Facebook target remain mandatory. This keeps
  acquisition on the already-running browser instead of attempting an
  unnecessary remote-view launch; it does not weaken authentication probing
  or launch a second provider attempt.

- **Facebook rendered-target recovery.** Service 0.3.35 treats a painted
  Facebook page whose target no longer answers CDP Runtime reads as a target
  failure, not a slow render or logout. It opens one blank successor, closes
  the exact predecessor immediately, and retries the navigation/read once.
  A repeated authentication or navigation failure is typed
  `facebook_target_unresponsive` with its failure stage. A 75-second
  cumulative adapter budget leaves the parent worker enough time for the
  existing non-masking 30-second same-site cleanup. The repair does not retry
  a provider attempt, close the retained browser, touch unrelated tabs, or
  change schedule, schema, limits, cost, model, or notification behavior.

- **Facebook hard-timeout tab containment.** Service 0.3.34 runs one
  provider-scoped, non-masking same-site cleanup after the isolated Facebook
  worker is killed and reaped at its hard wall deadline. The durable provider
  result and wall accounting remain `worker_timeout`; cleanup does not retry
  Facebook, navigate content, close the retained browser, or touch unrelated
  tabs. Facebook close operations use a 30-second command bound to accommodate
  observed agent-browser broker latency.

- **Facebook retained-tab lifecycle convergence.** Service 0.3.33 performs one
  best-effort same-site cleanup after every acquired Facebook workspace outcome,
  including typed failures, and retains exactly one reusable Facebook target.
  Cleanup failures never mask the provider result. The retained browser process
  and unrelated service tabs remain untouched; provider limits, retries,
  schedule, schema, cost, model, and notification behavior are unchanged.

- **Facebook Runtime-timeout fresh-target recovery.** Service 0.3.32 treats an
  exact active-tab URL/query/filter identity as diagnostic evidence after a
  post-navigation Runtime timeout, not proof that the same target is safe for
  extraction. The scraper now uses its existing single `about:blank`
  fresh-target replay even when identity matches; a successful second
  page-state read proceeds, while a repeated timeout remains terminal with no
  third target or attempt. Browser/profile lifecycle, provider limits, scroll
  depth, schedule, schema, cost, model, and notification behavior are unchanged.

- **Facebook tick item-bound execution and typed worker failures.** Service
  0.3.31 constrains Facebook collection to the item limit already admitted by
  the governed tick instead of retaining the scraper's broader default result
  target and unnecessary scroll loop. Isolated-worker boundary failures now
  become durable provider failures with their existing safe error code and
  retry class, so a wall timeout is retained as `worker_timeout` rather than
  collapsing the tick to an opaque `workerexecutionerror`. No provider limit,
  retry count, schedule, browser lifecycle, schema, cost, or notification
  behavior is expanded.

- **Facebook navigation readback fallback.** Service 0.3.30 no longer makes a
  responsive Facebook search target's Runtime evaluation a prerequisite for
  collection. Navigation state reads now use bounded, layout-free DOM text and
  capped structural surfaces. If that read still reaches its cancellation-safe
  deadline, the adapter accepts only an exact active-tab URL/title/query/filter
  identity from agent-browser's tab inventory, opens no recovery tab, and
  defers content, rate-limit, and candidate inspection to the existing
  extraction stage. A mismatched identity or non-timeout browser failure
  remains terminal.

- **Source-scoped manual ticks and Facebook rate-limit safety.** Service 0.3.29
  adds a repeatable manual-only `tick preflight/enqueue --service SERVICE_ID`
  selector. It can only disable already-enabled targets, narrows aggregate
  limits to the selected lanes, binds scope into the frozen config/tick
  identity, and leaves scheduler-created ticks all-source. Invalid, duplicate,
  empty, or disabled selections fail before provider work. Facebook now
  recognizes structurally bounded temporary-block and action-frequency-limit
  surfaces during authentication, navigation, or extraction and stops as
  `rate_limit_detected` without recovery navigation or an authentication
  handoff. Durable diagnostics retain only a stable reason signal, not page
  content.

- **Facebook live post extraction and retained-session acquisition.** Service
  0.3.28 models both
  author-named organic cards and generic ad cards from the current authenticated
  Facebook search layout. It selects timestamp anchors by date-shaped evidence,
  reconstructs human-visible timestamp and ad labels from rendered glyph
  geometry, accepts current compact and `Yesterday at <clock>` date labels, and
  keeps ads explicitly rejected. When agent-browser reports the exact configured
  retained session as profile `default`, the scraper reuses its browser only if
  the alias points to exactly one healthy ready-CDP browser, exactly one active
  session reciprocally owns that browser, and the alias or owner already owns a
  tab for the requested service; ambiguous and unrelated owners remain
  fail-closed,
  and the normal authentication probe still runs before navigation. Governed
  provider receipts now preserve only bounded per-reason rejection counts
  alongside existing aggregate counts and browser-operation evidence, so a
  future zero-yield result is diagnosable without retaining private page
  content. No schedule, provider, credential, schema, cost, or notification
  migration is required. Authentication inspection tries at most two retained
  Facebook targets before recovery, creates the fresh Facebook target in one
  command. Retained tab switches and auth reads keep their 3-second worker
  limits but receive 15-second process bounds so serialized queue wait cannot
  outlive the caller; only a genuinely fresh auth target receives a bounded
  30-second job/45-second process deadline. This leaves enough of the existing
  120-second provider budget for navigation and extraction even after another
  social source used the shared retained browser.

- **Facebook post-navigation readback recovery.** Service 0.3.23 treats the
  initial query-page state evaluation as part of the bounded search open/read
  attempt. A timeout replays that whole attempt exactly once on a fresh
  `about:blank` target in the same retained browser and profile; a repeated
  timeout or any non-timeout failure remains terminal.

- **All-frozen Facebook auth-target recovery.** Service 0.3.22 opens one fresh
  `about:blank` target in the same retained browser and profile when every
  retained Facebook target times out during bounded authentication inspection.
  The fresh target must still produce explicit authenticated, login, or
  checkpoint evidence; non-timeout failures remain terminal.

- **Bounded Facebook navigation recovery.** Service 0.3.21 retries a timed-out
  authenticated search navigation exactly once on a fresh `about:blank` target
  in the same retained browser and profile. Non-timeout failures do not retry,
  a repeated timeout stops terminally, and no retained tab is closed.

- **Responsive retained Facebook target selection.** Service 0.3.20 probes
  retained Facebook tabs under short command deadlines, skips frozen targets,
  and accepts explicit authenticated DOM or retained `c_user` evidence before
  collection. An unresponsive or ambiguous target now returns a typed browser
  failure instead of becoming a false login/checkpoint notice. Routine cleanup
  preserves the operator's other retained tabs.

- **Deferred Facebook operator-view acquisition.** Service 0.3.19 reuses a
  ready retained Facebook browser for ordinary CDP collection even when the
  requested RDP/Guacamole stream has not been prepared. External operator view
  acquisition remains on demand and runs only after authentication or
  checkpoint inspection proves that a human action is required.

- **Facebook command timeout layering.** Service 0.3.18 gives extraction
  evaluation a 20-second cancellation-safe agent-browser job deadline inside a
  25-second subprocess deadline. The daemon now releases its serialized queue
  before the caller exits. Extraction precomputes action-card ancestor
  ownership instead of repeatedly scanning every ancestor subtree, and durable
  provider results retain only bounded operation names, outcomes, error types,
  and timings for later diagnosis.

- **Direct-first Facebook extraction.** Service 0.3.17 uses the active search
  target's DOM extractor before requesting an accessibility snapshot. Dated DOM
  candidates now complete without the heavier snapshot path; snapshot-assisted
  timestamp recovery remains bounded to otherwise undated action cards.

- **Facebook extraction snapshot fallback.** Service 0.3.16 falls back to the
  same active target's DOM extraction when agent-browser's paired accessibility
  snapshot times out. The fallback is read-only and timeout-specific; malformed,
  failed, or timed-out DOM evaluation still terminates the provider attempt.

- **Authenticated Facebook checkpoint false positives.** Service 0.3.15 no
  longer treats help-chat or ordinary feed text about two-factor authentication
  as proof of a blocking checkpoint. Both authentication and search-page probes
  now require a checkpoint URL/form, or checkpoint-specific body evidence while
  the authenticated Facebook search control is absent.

- **Truthful Facebook checkpoint alerts.** Service 0.3.14 keeps explicit
  Facebook security checkpoints distinct from true CAPTCHA detections. A
  checkpoint now enters the existing `reauthentication_required` human gate,
  so Slack asks for the manual browser check without claiming that a CAPTCHA
  is present; literal CAPTCHA signals remain `captcha_required`.

- **Routine browser reauthentication handoff.** Service 0.3.13 turns recurring
  Facebook login and checkpoint failures into actionable browser-incident
  notifications. It reuses the retained profile and opens an operator view only
  after `agent-browser doctor remote-view` and `operatorVisible.state=ready`
  both pass, then carries only the resulting external HTTPS URL through the
  existing deduplicated notification chain. Detected incidents and hourly
  reminders request the manual browser action; resolution notices omit the
  stale link. Localhost, loopback, non-HTTPS, and unready routes fail closed.

- **Fresh Facebook collection targets.** Service 0.3.11 no longer treats an
  inactive Facebook tab in the shared social browser as proof that its CDP page
  domain is responsive. Every collection opens and evaluates a fresh Facebook
  home target for authentication, then navigates that same known-responsive
  target to Recent search instead of creating a separate query target whose
  first page-state evaluation can stall. Once any extracted candidate has a
  parseable timestamp, the adapter avoids repeating costly paired browser reads
  merely because a different action card is still undated. Sanitized command
  timing and verified search-page signals make the bounded result diagnosable
  without retaining page content. Same-site cleanup runs only after page
  extraction, uses short per-close bounds, and cannot turn valid page evidence
  into a provider failure. Together these changes address stale targets and
  wall-budget failures without launching another browser or weakening auth and
  page-quality gates.

- **Ordinary tick-head retrieval.** Service 0.3.4 routes ordinary queries to
  the atomically promoted terminal tick snapshot when one exists. Access,
  source, and time filters run before independent channel retrieval; responses
  expose the snapshot's terminal coverage/freshness plus each result's access
  partition, matching channels, and provenance. Installations without a
  promoted tick head retain the legacy cache fallback.

- **Retained social-browser acquisition.** Service 0.3.2 reuses a healthy
  same-profile browser for ordinary acquisition when it exposes writable CDP
  control, even if that browser does not satisfy a separately configured RDP
  human-observation route. This prevents duplicate-profile launch conflicts
  while keeping Guacamole acquisition behind the incident observation gate.

- **Config-owned tick lane order.** Service 0.3.1 preserves the frozen enabled
  target-array order through sanitized preflight, durable receipts, execution,
  and replay instead of re-sorting lanes by service ID. This keeps bounded
  manual ticks aligned with their reviewed user-scoped execution packet without
  adding a new flag, schema field, retry, or scheduling behavior.

- **Tick partial-result, observation, and media safety.** Worker results that
  contain publishable items plus a blocking browser issue now retain their raw
  evidence while the provider attempt and lane terminalize `blocked_human`.
  Explicit acknowledged observation resolves one ready agent-browser stream,
  requests `view_takeover`, persists the returned viewer-lease ID, and returns
  only the fresh external HTTPS route from that response. Media fetching now
  rejects non-global destinations and unsafe redirects before the next
  request, counts every redirect, and caps each request by the remaining
  monotonic wall budget.

- **Durable X profile planning.** The X adapter now passes its resolved
  user-scoped profile ID to agent-browser's no-launch access planner as the
  explicit runtime profile before validating the returned selection. Ambient
  target defaults can no longer stand in for the caller's durable
  `last30days-facebook` binding.
- **Canonical X profile and operator handoff.** X acquisition now consumes the
  stable user-scoped target binding in `agent-browser.json` when an explicit
  run/environment override is absent, while the live agent-browser access plan
  remains authoritative. Genuine X authentication or checkpoint gates retain
  agent-browser's direct external Guacamole `publicOperatorUrl`; localhost
  dashboard/embed URLs are never substituted as the human interaction link.
- **Reddit adapter provenance.** Reddit acquisition diagnostics now derive the
  concrete `reddit_keyless`, `reddit_agent_browser`, or
  `reddit_scrapecreators` variant from the recorded access-method chain, while
  preserving `reddit_access_chain` when no single method was selected.
- **Shared-browser operator routing.** Facebook shared-profile reuse now
  resolves the live retained browser and its service-local operator route
  before returning the workspace. Logged-out sessions therefore distinguish
  an actionable authentication gate from a missing handoff URL.

### Added

- **Governed recurring all-source tick.** Service 0.3.5/database schema 16 adds
  one optional service-owned UTC schedule to `tick-config-v1.json`. The daemon
  admits only the latest completed boundary through the existing durable tick
  coordinator, advances schedule state before execution, waits for live
  recovery leases, reuses the existing expired-lease successor attempt, and
  pauses on config drift or enqueue failure. `tick schedule status` and
  `GET /v1/tick-schedule` expose only sanitized cadence and last/next tick
  state. An absent or disabled schedule creates no tick work; no systemd or
  per-source timer is added.

- **Local source-grounded image analysis.** Service 0.3.3 adds a PATH-gated
  `tesseract_cli_v1` OCR adapter and a deterministic
  `source_grounded_semantic_sidecar_v1` adapter. The sidecar uses only source
  alt text plus completed local OCR, records no inferred visual facts, and
  consumes no provider cost or model tokens. Missing or broken Tesseract
  remains a preflight failure when that adapter is selected.

- **Durable all-source tick foundation.** Service 0.3.0 introduces database
  schema 15, the versioned user-scoped `tick-config-v1.json` contract, and a
  two-call durable tick seam. Enqueueing freezes an exact interval, sanitized
  config digest, enabled lanes, provider order, expected stages, and aggregate
  and provider ceilings. Expired execution leases create a bounded recovery
  attempt under the same tick identity, with integrity checks on frozen state.
  Provider results are staged durably before raw publication, with media and
  rendered-page bytes referenced through the user-scoped content-addressed
  store. Recovery reuses that exact result without another source call or
  budget charge, skips terminal lanes, and rebuilds the query snapshot from
  persisted evidence. This candidate does not enable a recurring timer or
  mutate user configuration.

- **Manual tick execution and evidence pipeline.** Installed provider adapters
  now execute config-owned service/target lanes with sequential fallback,
  resource-key exclusion, measured outcome counts, and exact budget admission.
  Successful evidence publishes as immutable records, versions, and sightings;
  content-addressed images preserve OCR and typed semantic-sidecar derivatives,
  including independent failure receipts. A deterministic exact-text catalog
  links cross-source duplicates without merging their source records, and one
  terminal lexical/semantic/OCR/sidecar/catalog snapshot promotes atomically.

- **Tick incidents and reconstructable receipts.** Deterministic browser,
  authentication, rate-limit, provider, and statistical signals persist before
  sequential notification failover. Exact rendered pages remain protected
  artifacts, repeated incidents suppress alert churn, exact recovery resolves
  once, and Guacamole observation remains acknowledgment-gated. Terminal tick
  receipts now carry sanitized manifests whose independently recomputable
  digests cover attempts, events, budgets, providers, staged provider results,
  evidence, artifacts, derivatives, incidents, deliveries, anomalies, catalog
  entries, and the promoted snapshot. Production live acceptance,
  installation, scheduling, and release remain separate gates.

- **Production media and browser-incident carriage.** The isolated acquisition
  contract now transports bounded image and video-thumbnail bytes plus exact
  rendered-page screenshots through the production tick bridge. Browser issue
  capture reuses the active agent-browser tab without requesting Guacamole;
  the direct external operator URL is persisted with the incident and becomes
  observable only after acknowledgment. The observation command no longer
  accepts a caller-supplied link, and deployments may inject a code-owned
  provider registry while user config remains limited to selecting registered
  adapter types. This schema-14 candidate supersedes the unreleased schema-13
  build; neither candidate has been installed or released.

- **Bounded manual collection retries.** Operator-triggered collection runs
  retain a one-attempt default and now accept an explicit
  `--max-attempts 2` override for separately reviewed transient-retry budgets.
  Timer retry policy stays service-owned, invalid values fail before run
  creation, and both attempts remain inside one immutable run/job identity.
  Attempt two is restricted to allowlisted browser/worker transients with an
  immutable zero-side-effect receipt; broad rate-limit, content, internal-error,
  missing-count, and unreceipted lease-expiry retries fail closed.

- **Configurable browser job timeout.** Every Reddit, X, Facebook, and LinkedIn
  agent-browser launch now passes a positive per-request control-plane timeout.
  The default follows that source's user-scoped browser timeout, while
  `LAST30DAYS_AGENT_BROWSER_JOB_TIMEOUT_MS` supplies one shared user override.
  This keeps slow durable-profile launches from inheriting agent-browser's
  shorter daemon default without hard-coding policy per service.
- **User-scoped browser display policy.** Reddit, X, Facebook, and LinkedIn now
  resolve display isolation from
  `LAST30DAYS_AGENT_BROWSER_DISPLAY_ISOLATION`, while preserving their existing
  source defaults when it is unset. Serial service deployments can select
  private route displays without patching individual adapters.

- **Safe access-method provenance.** Every managed acquisition result now
  records its exact adapter variant plus the ordered access methods attempted
  and the method that supplied publishable items. This makes configured
  fallbacks independently auditable without exposing browser state or
  credentials.
- **One-attempt manual collections.** Operator-triggered collection intervals
  now use a single durable job attempt, while recurring timer intervals retain
  their two-attempt recovery policy. Bounded acceptance and diagnostic runs can
  therefore enforce their declared attempt ceiling without disabling normal
  scheduler resilience.

- **User-scoped recurring-source policy.** The managed service now reads an
  explicit source catalog and per-source ordered access chains from the user
  configuration, advertises readiness from that effective policy, and rejects
  empty, duplicate, unsupported, or cross-source methods. Explicit Reddit
  policy can include the bounded `agent_browser` fallback without implicitly
  enabling the paid ScrapeCreators route.
- **Opt-in agent-browser Reddit fallback.** Service-owned Reddit acquisition can
  now run a bounded public post-search DOM routine after empty RSS/Shreddit
  yield and before the paid ScrapeCreators fallback. The routine uses the
  broker-selected managed profile, emits canonical normalized posts, performs
  no account actions, and returns typed navigation, challenge, rate-limit,
  extraction, and quality failures.

## [4.0.0] - 2026-07-30

This release makes the independently installed intelligence service and its
MCP adapter the primary product. Artifact versions are intentionally
independent: Skill/plugin `4.0.0`, MCP/MCPB `4.0.1`, and service `0.2.9`.
Existing schema-12 databases require no migration.

### Migration

- Install or upgrade the service 0.2.9 artifact before replacing the MCP
  adapter, then install MCP 4.0.1 and require
  `compatibility_state=compatible`.
- A stale client/service pair fails closed through `service_info`; it does not
  authorize direct Engine acquisition.
- The request-scoped Engine remains packaged as an explicitly approved
  compatibility/debug path, but is deprecated as the ordinary primary path.
- The managed installer preserves the existing database, profiles, schedules,
  ledgers, corpus, and indexes. `service/scripts/install.sh rollback` swaps to
  the one retained previous verified release.

### Added

- **Discoverable App Intelligence contracts.** `maintenance_status` now reports
  the canonical task registry, request/result contract versions, and finite
  validator-enforced limit ranges without exposing prompts, provider events,
  evidence bodies, or repair controls.
- **Deterministic adapter-failure automation contracts.** App Intelligence
  workers can now propose bounded failure triage, repair recommendations, and
  branch decisions through strict host-validated schemas. Authentication,
  checkpoint, rate-limit, access, transient, configuration, and
  insufficient-evidence classes cannot be routed into code repair.
- **Local cached intelligence service.** The user-scoped service now preserves
  bounded image/video descriptors and source provenance, publishes deterministic
  local embeddings plus evidence-backed entity relationships behind an explicit
  active-index head, and exposes the five-tool query surface through a durable
  Codex MCP installer.
- **Authenticated agent-browser X search.** Opt-in `LAST30DAYS_X_BROWSER=1` / `LAST30DAYS_X_BACKEND=browser` search now resolves target identity `x`, reuses the access-plan-selected retained profile (default `last30days-facebook`), verifies the exact dated Latest query, and emits only canonical, dated, relevant status posts without exporting cookies.
- **Hidden-RDP YouTube transcript fallback.** Classified `yt-dlp` transport, bot-check, timeout, and rate-limit failures can now fall back to browser-native caption retrieval inside a serialized, headed `stealthcdp_chromium` session on a checked-out hidden XRDP display exposed through agent-browser's Guacamole operator route. Cookies and caption URLs remain inside Chromium.
- **Bounded YouTube media operations.** The skill now ships `scripts/youtube_media.py` for runtime doctoring, authenticated subscription-feed discovery through the retained hidden-RDP browser, caption-first transcripts with local `transcribe-audio` fallback, and single-video resolution-bounded downloads.

### Fixed

- **Current X sign-in pages are typed as login gates.** The X adapter now
  recognizes the modern root-page “Happening now / Email or username” surface
  as signed out. It no longer treats that page as ambiguous, reloads it, and
  obscures the operator-auth requirement.
- **Acquisition failures carry stable repair evidence.** Failed work results
  now preserve a bounded failure stage, safe browser-operation timings where
  the adapter provides them, and a host-computed signature that is stable
  across job and attempt IDs without exposing raw browser state.
- **Shared social profiles reuse the Guacamole/RDP browser.** X, Facebook, and
  LinkedIn post/profile adapters now pass the complete remote-view posture into
  agent-browser access planning and request the retained social profile's
  `shared_display`. This prevents a false private-display lease conflict from
  blocking a healthy route-bound authenticated browser.
- **X browser workspaces use Guacamole/RDP instead of CDP screencasts.** X now
  delegates acquisition to agent-browser's route-bound remote-view path with
  an `rdp_gateway` default and requires an operator-ready workspace. This keeps
  authentication and recovery attached to a visible, controllable browser.
- **Authenticated X sessions recover from a stalled retained tab.** The X auth
  probe now reloads `x.com/home` once when the DOM is ambiguous, then checks
  again before requesting operator authentication. Explicit login,
  checkpoint, and restriction states remain terminal and are never reloaded.
- **Awaiting-operator refresh jobs can resume after the human gate clears.**
  Operators can use `service.py job <job-id> --resume` to return the same
  bounded job to the queue without losing its attempt count or event history.
  The local HTTP service exposes the same guarded transition and rejects jobs
  in any other state.
- **YouTube discovery stays inside worker budgets.** Search now uses yt-dlp's
  flat metadata projection, retaining video URLs, channel, duration, views, and
  thumbnails without expanding every result into a slow watch-page request.
- **X challenge detection avoids generic-content false positives.** Only known
  checkpoint routes and explicit identity/security copy now trigger an operator
  checkpoint; ordinary posts containing the word “challenge” no longer do.
- **YouTube caption fallback no longer loses a preferred transcript to a lower-priority translation failure.** `LAST30DAYS_YT_SUB_LANGS` entries are now attempted sequentially, stopping at the first available caption, instead of asking `yt-dlp` to download every requested language in one failure-coupled command.

## [3.6.0] - 2026-06-18

### Added

- **First-party X posts are no longer buried.** A post authored by one of the run's resolved handles (`--x-handle`, `--x-related`, the GitHub user) is now treated as first-class evidence: it is exempt from the entity-miss demotion (a post never repeats its own author's name, so the body-text grounding check used to zero out the subject's own highest-signal posts) and gets a small authorship credit. Third-party collision-noise suppression is unchanged.
- **Engagement rescue for on-topic X posts.** A high-engagement X post that is first-party or entity-grounded gets a `final_score` floor scaled by its engagement percentile within the run's X pool, so a viral on-topic post can't sit at ~0. Off-topic name-collision posts are explicitly excluded.
- **First-party interaction signal.** A first-party post directed at another account (a reply / leading @mention) is floated into the visible band regardless of like-count and tagged `interaction:→@handle` in the EVIDENCE block, so the synthesis reads it as a relationship signal rather than low-engagement noise. New **LAW 10** in SKILL.md teaches the model to surface first-party posts and read the interaction tag.

### Changed

- The X FROM lane (the subject's own timeline) now pulls up to 8 posts per handle (was 3); the about/related lanes stay modest.

## [3.5.0] - 2026-06-18

### Added

- **X surfaces tweets FROM and ABOUT a person, both engagement-weighted.** The handle search now pulls the person's real timeline (`from:handle since:`, topic used for ranking only — never AND'd into the query, which previously matched only tweets where they wrote their own name and returned ~0), and a new mention lane (`@handle since:`) surfaces what others say to/about them, excluding their own tweets and deduping against the FROM lane ([#610](https://github.com/mvanhorn/last30days-skill/pull/610)).
- **`## Top Community Comments` block.** The engine now surfaces vote-ranked community comments across all candidates (not just the top-cluster representatives), per-platform-normalized, into the EVIDENCE-for-synthesis block, so the funniest/sharpest crowd reactions reach the synthesizing model even when no LLM fun-scorer is available. Paired with a new SKILL.md **LAW 9** that requires weaving ≥2 verbatim attributed comments, copying URLs verbatim, and never narrating the tooling in the deliverable ([#608](https://github.com/mvanhorn/last30days-skill/pull/608)).

### Fixed

- **`--diagnose` honesty.** X status now reflects a real 1-tweet probe (downgrades from green when X is effectively dead; fail-open on a transient timeout) and reports the true auth lane (browser / env / keychain) instead of a hardcoded `env AUTH_TOKEN`. Handle/mention searches log query + result count on success, not only on failure ([#609](https://github.com/mvanhorn/last30days-skill/pull/609)).
- **X column de-pollution.** The last-chance keyword retry no longer collapses a multi-word subquery to a bare generic token (e.g. `compound`); it keeps an entity anchor ([#607](https://github.com/mvanhorn/last30days-skill/pull/607)).
- **Mandatory person-aware subquery disambiguation.** Collision-prone person names (Kevin Rose vs Kevin Warsh, Lan Xuezhao vs Lanzhou) must anchor every subquery with the resolved company/role/domain context ([#611](https://github.com/mvanhorn/last30days-skill/pull/611)).

## [3.4.0] - 2026-06-18

### Added

- **Crowd-vote weighting in the fun judge (Best Takes).** The fun judge now factors how many upvotes/likes each top comment earned. Comment vote counts are fed into the LLM prompt (as traction, not funniness), and Best-Takes selection ranks by an effective score — `fun_score` plus a bounded, per-platform-normalized, relevance-confidence-scaled crowd nudge — so genuinely funny, crowd-loved, on-topic comments surface while off-topic virality and high-voted-but-unfunny rants are excluded. `FUN_LEVEL=medium` stays the default and applies the signal as a meaningful factor ([#592](https://github.com/mvanhorn/last30days-skill/pull/592)).
- **Digg added to first-run setup.** The free, keyless `digg-pp-cli` is now auto-installed during the first-run wizard (best-effort via the Printing Press installer, with a recommend-only fallback), so the already-built Digg AI-news source activates automatically for new users instead of silently never appearing ([#590](https://github.com/mvanhorn/last30days-skill/pull/590)).

- **`LAST30DAYS_YOUTUBE_SSH_HOST` transcript routing** — yt-dlp transcript fetch runs on the remote SSH host via a mktemp + cat pipeline ([#422](https://github.com/mvanhorn/last30days-skill/pull/422)).
- Browser-cookie auth for X/Twitter now covers the full Chromium family on macOS - Brave, Microsoft Edge, Vivaldi, Opera, Arc, and Chromium - alongside the existing Chrome, Firefox, and Safari. They all share Chrome's v10 AES-128-CBC decryption, differing only in profile path and Keychain service name, so they run through one shared decryption core. The profile finder probes both the modern `Default/Network/Cookies` layout (Chromium >= 96) and the legacy flat `Default/Cookies`, and Chrome now resolves through that same finder so it picks up the modern layout too. Set `FROM_BROWSER=auto` to try every browser, or `FROM_BROWSER=<name>` (e.g. `brave`, `edge`, `arc`) to target one. Verified end-to-end on real Brave and Edge installs ([#572](https://github.com/mvanhorn/last30days-skill/pull/572)).
- **First-party positioning research + pitch-vs-pulse synthesis (company / product / service topics).** A new mandatory research step captures each entity's current stated positioning from first-party sources (homepage, docs, pricing) rather than from memory. The fetched pitch grounds `What it is` descriptions (entities described as they pitch themselves today), helps reject unrelated brand-name noise, and feeds an evidence-triggered prose beat: when the month's conversation directly supports a specific claim, cuts against one, or is squarely about the pitched ground, the synthesis says so anchored to the top thread — and stays silent when the pulse is orthogonal to the pitch, because a manufactured connection is worse than omission. Claims are tested at matched altitude (specific claims against specific threads; broad taglines are never graded against individual items), and statements stay windowed to the 30 days — no trend verdicts. Scoped to entities with an identifiable first party: people are always excluded (even founders whose companies qualify), as are events, abstract concepts, and ownerless topics like Bitcoin; the beat requires positioning fetched during the run, never from memory.

### Changed

- Updated "Unlock X" promo message to mention Chrome/macOS support and Windows Firefox-only limitation instead of generic "Firefox or Safari" ([#387](https://github.com/mvanhorn/last30days-skill/issues/387))

### Fixed

- **SSH routing failures no longer present as "0 results"** — `search_youtube` surfaces non-zero SSH exit codes as an explicit `error` field ([#422](https://github.com/mvanhorn/last30days-skill/pull/422)).
- `extract_browser_credentials()` silently ignored Brave even though the lower-level `cookie_extract` layer already supported it: `FROM_BROWSER=brave` fell back to Firefox/Safari and `FROM_BROWSER=auto` never tried Brave. The env wiring now passes Brave - and the rest of the Chromium family - through to the extractor ([#572](https://github.com/mvanhorn/last30days-skill/pull/572)).
- Chromium cookie extraction now fetches the macOS Keychain key lazily - only when an encrypted cookie actually needs decrypting. Previously the key was fetched as soon as the cookie DB existed, so `FROM_BROWSER=auto` could trigger a Keychain prompt for every installed Chromium browser. Now only the browser that actually holds the requested cookie prompts ([#572](https://github.com/mvanhorn/last30days-skill/pull/572)).
- YouTube transcript budget prioritises recent videos (by a combination of views and recency) instead of views alone, preventing transcript slots from being consumed by old high-view-count videos that would be discarded by strict_recent freshness pruning ([#531](https://github.com/mvanhorn/last30days-skill/issues/531))
- YouTube items with successfully extracted transcripts are no longer pruned by title-only relevance scoring; the transcript content proves substantive topical coverage even when the video title has low lexical overlap with the query ([#468](https://github.com/mvanhorn/last30days-skill/issues/468))
- First-run setup wizard in SKILL.md now references the existing Python setup wizard (`last30days.py setup`) instead of the missing `nux-wizard.md` file, so first-run setup actually runs on new installs. ([#574](https://github.com/mvanhorn/last30days-skill/issues/574))
- `check-config.sh` no longer exits 1 on the ScrapeCreators-configured path when no prior run exists (empty `LAST_RUN_LINE`) — swapped `&&` guard for an `if` block that always exits cleanly ([#463](https://github.com/mvanhorn/last30days-skill/issues/463))
- `check-config.sh` no longer exits 1 when a `.env` value contains an unbalanced quote — replaced `xargs` (which interprets quotes) with `sed` for whitespace trimming in `load_env_vars` ([#506](https://github.com/mvanhorn/last30days-skill/issues/506))
- X/Twitter `.env` template now includes `CT0` alongside `AUTH_TOKEN` in the example skeleton ([CONFIGURATION.md](CONFIGURATION.md)), and the just-in-time unlock wizard offers AUTH_TOKEN/CT0 cookie entry ([#396](https://github.com/mvanhorn/last30days-skill/issues/396))
- `check-config.sh` no longer counts X as an active source when only `AUTH_TOKEN` is set without `CT0` — both cookies are now required to credit X in the source count ([#396](https://github.com/mvanhorn/last30days-skill/issues/396))
- Firefox cookie extraction now falls back to scanning non-default profiles when the default profile has no matching X cookies, fixing multi-profile setups where login lives on a non-default profile ([#498](https://github.com/mvanhorn/last30days-skill/issues/498))
- `subproc.py` `run_with_timeout()` now guards `os.killpg` / `os.getpgid` with `hasattr`, preventing an uncaught `AttributeError` crash when a subprocess times out on Windows where these functions don't exist ([#527](https://github.com/mvanhorn/last30days-skill/issues/527))
- Entity-grounding rerank demotion now keys on the head token of the primary entity instead of requiring the full multi-word phrase as a contiguous substring. A high-engagement on-entity item (e.g. a 323-pt HN thread titled "Stripe is friendly to 'friendly fraud'") is no longer demoted to score 0 on a `Stripe payments` query just because it lacks the trailing search-hint word. The intended demotion still fires for items that never name the brand at all. The keyless Reddit comment-enrichment slot selection (`_slot_priority`), which mirrors this signal, was updated to the same head-token grounding so the two paths stay consistent.
- `--plan` / `--competitors-plan` file reads now specify `encoding="utf-8"` and catch `UnicodeDecodeError`, preventing crashes on non-ASCII content like accented entity names on Windows (cp1252). `check_perms()` in `check-config.sh` now skips the POSIX 600-permission check on MSYS/MinGW/Cygwin where `stat` runs in noacl mode. `skill_meta.py` `read_skill_version()` now passes `encoding="utf-8"` so SKILL.md emoji doesn't break version detection on Windows. ([#549](https://github.com/mvanhorn/last30days-skill/issues/549))


## [3.3.2] - 2026-06-06

### Fixed

- YouTube transcript extraction now falls back through `en,es,pt` (configurable via `LAST30DAYS_YT_SUB_LANGS`) instead of English-only, so non-English videos with auto-captions in any of those three languages now contribute transcripts to the brief ([#469](https://github.com/mvanhorn/last30days-skill/issues/469))
- Keyless Reddit comment enrichment now spends its limited slots on entity-matching posts first (mirroring rerank's entity-miss demotion signal) instead of raw upvote order, so off-topic high-upvote threads from broad subreddits no longer consume the comment budget only to be demoted afterward ([#484](https://github.com/mvanhorn/last30days-skill/pull/484))

## [3.3.1] - 2026-05-30

### Fixed

- Removed the redundant `commands/last30days.md` wrapper so the plugin exposes only the skill ([#461](https://github.com/mvanhorn/last30days-skill/issues/461)). Previously the plugin shipped both a command wrapper and the skill under the same name, so `/last30` surfaced two `last30days` entries with two different descriptions. The skill already carries its own `argument-hint`, so the `/last30days <topic>` picker UX is unchanged.
- Corrected the README install note that claimed Claude Code dedupes the slash command across install methods; it does not, so having both the marketplace plugin and the `npx skills` copy active shows two entries.

## [3.3.0] - 2026-05-17

A week-long shipping cycle: ~75 PRs merged plus 7 community fixes salvaged through PR triage. Big themes: install story modernized for the multi-harness world (Claude Code, Codex, Cursor, Gemini CLI, Copilot, Windsurf, and 50+ Agent Skills hosts), new emit and source modes, and a substantial reliability sweep across Reddit, X, Windows, YouTube, and the planner.

### Added

**Emit modes and sources**

- `--emit=html` for shareable, print-friendly HTML research briefs ([#332](https://github.com/mvanhorn/last30days-skill/pull/332)).
- **Digg AI 1000 source**, auto-enabled when `digg-pp-cli` is on PATH ([#370](https://github.com/mvanhorn/last30days-skill/pull/370)). Surfaces curated story clusters from the AI 1000 leaderboard and pulls attributable X-post quotes into the brief.

**Configuration knobs**

- `EXCLUDE_SOURCES` env var — the inverse of `INCLUDE_SOURCES`, honored in source count and pipeline filter ([#399](https://github.com/mvanhorn/last30days-skill/pull/399)).
- `LAST30DAYS_YOUTUBE_SSH_HOST` — opt-in SSH routing for `yt-dlp` through a residential-IP host, for users on datacenter VPS hit by YouTube's bot-wall ([#376](https://github.com/mvanhorn/last30days-skill/pull/376)). Host validated against `^[a-zA-Z0-9._-]+$` to reject SSH option-injection. Transcript path unchanged (uses HTTP fallback).
- macOS Keychain as a credential source — reads from the system keychain when env vars and config files aren't set ([#407](https://github.com/mvanhorn/last30days-skill/pull/407)).
- Configuration enablement: env-var defaults and source-resilience patterns across the config layer ([#344](https://github.com/mvanhorn/last30days-skill/pull/344)).

**Pipeline and storage**

- Reddit URL auto-enrichment from web search via the public JSON API ([#366](https://github.com/mvanhorn/last30days-skill/pull/366)).
- Per-run finding sightings recorded in the SQLite store ([#373](https://github.com/mvanhorn/last30days-skill/pull/373)).
- Brave browser support for X/Twitter cookie extraction ([#320](https://github.com/mvanhorn/last30days-skill/pull/320)).

**Tests and CI**

- Full pytest suite restored to CI; 13 rotted tests repaired ([#416](https://github.com/mvanhorn/last30days-skill/pull/416)).
- `greptile.json` added with `triggerOnUpdates` + `statusCheck` ([#418](https://github.com/mvanhorn/last30days-skill/pull/418)).
- Advisory security workflow ([#368](https://github.com/mvanhorn/last30days-skill/pull/368)).
- Parallel grounding backend test coverage ([#355](https://github.com/mvanhorn/last30days-skill/pull/355)).

**Docs**

- New `CONFIGURATION.md` with README pointers ([#339](https://github.com/mvanhorn/last30days-skill/pull/339)).
- `docs/solutions/` learning capture for release-time consistency-test cascades ([#413](https://github.com/mvanhorn/last30days-skill/pull/413)) and the eval-not-in-CI design decision ([#417](https://github.com/mvanhorn/last30days-skill/pull/417)).

### Changed

**Install story modernized**

- `npx skills add` is now the canonical install path for every harness ([#405](https://github.com/mvanhorn/last30days-skill/pull/405)). README and SKILL.md flipped to recommend `npx skills add . -g -y` over per-harness manual instructions. Surfaces Gemini CLI, Copilot, Windsurf, and 50+ other Agent Skills hosts that the install pattern reaches.
- README dropped the Gemini CLI native-extension install path (now covered by `npx skills add`).
- `hooks.json` made polyglot for Gemini CLI + Claude Code compatibility ([#318](https://github.com/mvanhorn/last30days-skill/pull/318)).

**Skill semantics and multi-harness reframe**

- `AGENTS.md` is now canonical; `CLAUDE.md` points at it ([#410](https://github.com/mvanhorn/last30days-skill/pull/410)). Reframes the project as a multi-harness Agent Skills package rather than a Claude-Code-specific tool.
- SKILL.md path resolution rewritten: STEP 0 narrows to a Claude-Code-marketplaces-only stale-clone guard; Step 1 walks a single `SKILL_DIR` substitution pattern ([#400](https://github.com/mvanhorn/last30days-skill/pull/400), [#409](https://github.com/mvanhorn/last30days-skill/pull/409)). Removes ~80 lines of bash and fixes a real spec-vs-engine divergence where the previous resolver could pick a different install than the SKILL.md the model loaded from.
- SKILL.md version regex consolidated into `lib/skill_meta.py` ([#412](https://github.com/mvanhorn/last30days-skill/pull/412)).
- `--plan` / `--competitors-plan` invocation templates switched from inline single-quoted JSON to heredoc-written tmpfiles ([#404](https://github.com/mvanhorn/last30days-skill/pull/404), fixes [#403](https://github.com/mvanhorn/last30days-skill/issues/403)). Apostrophes in resolved context strings ("McDonald's", "people's choice") no longer break shell parsing.
- `POSTS_PER_CLUSTER` raised 3→5 and render-side display limit 2→3 to match the per-source enrichment caps used by Reddit, HN, YouTube, TikTok, and GitHub. The previous caps routinely truncated cluster context.
- Digg AI 1000 renamed to "Digg" in user-facing output ([#372](https://github.com/mvanhorn/last30days-skill/pull/372)) — footer line, source label, inline-quote suffix, why_relevant, container attribution. Internal references retain the upstream product name.
- GitHub repo resolution canonicalized for ambiguous product comparisons ([#302](https://github.com/mvanhorn/last30days-skill/pull/302)).

**Dependencies and tooling**

- Dropped `requests` runtime dependency. All providers route through stdlib `urllib` via the `lib/http` wrapper ([#393](https://github.com/mvanhorn/last30days-skill/pull/393)).
- Migrated to `gemini-3.1-flash-lite` GA model ([#378](https://github.com/mvanhorn/last30days-skill/pull/378)).
- Aligned Codex/Claude plugin manifests + added Codex `AGENTS.md` ([#321](https://github.com/mvanhorn/last30days-skill/pull/321)).
- pytest dev dep bumped 9.0.2 → 9.0.3 ([#414](https://github.com/mvanhorn/last30days-skill/pull/414)).

### Removed

- **BREAKING for Codex native-plugin users:** `.codex-plugin/plugin.json` and the matching SKILL_ROOT resolver branch in SKILL.md Step 1 ([#400](https://github.com/mvanhorn/last30days-skill/pull/400)). Codex users should install via `npx skills add mvanhorn/last30days-skill` or copy the skill to `~/.codex/skills/last30days/`.
- **`skills/last30days/scripts/sync.sh`** — maintainer dev-deploy script ([#405](https://github.com/mvanhorn/last30days-skill/pull/405)). Replaced by `npx skills add . -g -y` (live-symlink into every detected harness's skill dir — better than sync.sh's copy model since edits propagate live). Hermes uses `hermes skills install mvanhorn/last30days-skill --force`; OpenClaw uses `clawhub install last30days-official`.
- Orphaned `SPEC.md` and `TASKS.md` ([#419](https://github.com/mvanhorn/last30days-skill/pull/419)).

### Fixed

**Reddit**

- `lstrip("r/")` mangled subreddits starting with `r` (`r/robotics` → `obotics`, `r/ruby` → `uby`); replaced with `removeprefix("r/")` at 4 sites (Alex Key, salvaged from #288).
- Browser-like User-Agent + `Accept-Language`/`Accept-Encoding`/`Connection` headers + gzip decompression to fix `urllib` 403s on Reddit's public JSON endpoint (Franco Carballar, salvaged from #199).
- HTTP 402 re-raised across all three ScrapeCreators paths (`_global_search`, `_subreddit_search`, `fetch_post_comments`) so the OpenAI/public-JSON fallback chain triggers when credits are exhausted (Jonathan Oppenheim, salvaged from #170).

**Authentication and credentials**

- Restored multi-key rotation for `SCRAPECREATORS_API_KEY` accidentally dropped in v3.0.6 (Eric Oberhofer, salvaged from #287). Comma-separated keys round-robin via `random.choice` per run.

**Windows compatibility**

- `os.killpg` in `_cleanup_children()` guarded with `hasattr(os, "killpg")`, falls back to `os.kill(SIGTERM)` (gujishh, salvaged from #226).
- POSIX-style secret-permission warning skipped on Windows ([#357](https://github.com/mvanhorn/last30days-skill/pull/357)).
- Render uses forward slashes in save-path footer for Windows ([#338](https://github.com/mvanhorn/last30days-skill/pull/338)).

**xAI / X / xurl**

- `parse_x_response` now raises `http.HTTPError` on empty output, missing JSON, or decode failure — surfaces in `errors_by_source` instead of silently returning an empty result list (Kaustav Mishra, salvaged from #155).
- `xurl` treats `PermissionError` from PATH lookup as unavailable ([#322](https://github.com/mvanhorn/last30days-skill/pull/322)).

**YouTube**

- SC YouTube + multi-token HN searches unblocked ([#388](https://github.com/mvanhorn/last30days-skill/pull/388)).
- Transcript-fetch ratio surfaced + degraded-run nudge for stale `yt-dlp` ([#340](https://github.com/mvanhorn/last30days-skill/pull/340)).

**bird_x / HTTP**

- Subprocess retry on non-JSON stdout to handle X anti-bot HTML interstitials ([#383](https://github.com/mvanhorn/last30days-skill/pull/383)).
- HTTP retry budget expanded + exponential backoff on DNS resolution failure ([#382](https://github.com/mvanhorn/last30days-skill/pull/382)).
- Parallel AI search aligned with current API schema ([#341](https://github.com/mvanhorn/last30days-skill/pull/341)).
- Parallel web backend routed through grounding ([#354](https://github.com/mvanhorn/last30days-skill/pull/354)).

**Planner and sources**

- `xquik` registered in `SOURCE_CAPABILITIES` ([#336](https://github.com/mvanhorn/last30days-skill/pull/336), fixes [#319](https://github.com/mvanhorn/last30days-skill/issues/319)).
- Honor explicit optional source requests ([#356](https://github.com/mvanhorn/last30days-skill/pull/356)).
- ScrapeCreators source-gating aligned between code and docs ([#415](https://github.com/mvanhorn/last30days-skill/pull/415)).
- OpenClaw works without ScrapeCreators key ([#392](https://github.com/mvanhorn/last30days-skill/pull/392), by @thinkun).

**Render, version display, hosting paths**

- Hardcoded `v3.0.0` in render replaced with dynamic `_skill_version()` ([#365](https://github.com/mvanhorn/last30days-skill/pull/365)).
- Comparison HTML artifacts saved correctly ([#389](https://github.com/mvanhorn/last30days-skill/pull/389)).
- `OPENROUTER_DEFAULT` model ID corrected ([#323](https://github.com/mvanhorn/last30days-skill/pull/323)).
- OpenClaw poll-timing initialized once ([#358](https://github.com/mvanhorn/last30days-skill/pull/358)).
- Prefer sandboxed Safari cookie path ([#343](https://github.com/mvanhorn/last30days-skill/pull/343)).
- Preserve clean mode for last-run state ([#334](https://github.com/mvanhorn/last30days-skill/pull/334)).
- Replaced hardcoded `/Users/mvanhorn/...` paths in `test-v1-vs-v2.sh` with portable env-var overrides (Dave Morin, salvaged from #297).

**Hooks**

- `check-config.sh` path-quoting fix for paths with spaces ([#337](https://github.com/mvanhorn/last30days-skill/pull/337)).
- Replaced unsafe `eval` with `declare` in `check-config.sh` ([#364](https://github.com/mvanhorn/last30days-skill/pull/364)).

**Sync and version metadata**

- `sync.sh` pointed at this repo's plugin cache, not the private repo's ([#402](https://github.com/mvanhorn/last30days-skill/pull/402)).
- Sync cache target bumped to 3.2.1 to match SKILL.md ([#397](https://github.com/mvanhorn/last30days-skill/pull/397)).
- ScrapeCreators free-tier credit count corrected to 100 in docs ([#369](https://github.com/mvanhorn/last30days-skill/pull/369), fixes [#367](https://github.com/mvanhorn/last30days-skill/issues/367)).
- Gemini extension version synced ([#349](https://github.com/mvanhorn/last30days-skill/pull/349)).
- Various stale path/link fixes ([#345](https://github.com/mvanhorn/last30days-skill/pull/345), [#346](https://github.com/mvanhorn/last30days-skill/pull/346), [#347](https://github.com/mvanhorn/last30days-skill/pull/347), [#348](https://github.com/mvanhorn/last30days-skill/pull/348), [#351](https://github.com/mvanhorn/last30days-skill/pull/351)).

### Contributors

First-time contributors whose fixes shipped in this release (most via PR triage salvage — fix re-applied directly to main with co-author credit when path migration made the original branch un-rebaseable):

- Dave Morin — portable test-harness paths
- Alex Key — `removeprefix("r/")` for subreddit names
- Eric Oberhofer — multi-key rotation restored
- gujishh — Windows process cleanup
- Franco Carballar — Reddit browser-like headers
- Jonathan Oppenheim — Reddit 402 fallback chain
- Kaustav Mishra — xAI error surfacing
- [@thinkun](https://github.com/thinkun) ([#363](https://github.com/mvanhorn/last30days-skill/pull/363)) — OpenClaw ScrapeCreators-key-optional fix

Full PR list at [github.com/mvanhorn/last30days-skill/releases/tag/v3.3.0](https://github.com/mvanhorn/last30days-skill/releases/tag/v3.3.0).

## [3.2.0] - 2026-05-09

### Added

- Add `--emit=html` for shareable, print-friendly HTML research briefs.
- **Digg AI 1000 source** (auto-enabled when `digg-pp-cli` is on PATH). Surfaces curated story clusters from the AI 1000 leaderboard and pulls attributable X-post quotes into the brief as `[@handle](xUrl) via Digg AI 1000: ...` lines. Footer line: `⛏️ Digg AI 1000: N clusters │ K posts │ M authors`. No X auth required for the inline quotes since they flow through Digg's read-only endpoints.

## [3.1.1] - 2026-04-24

### Fixed

- **Codex plugin layout.** Move the canonical runtime payload under `skills/last30days/` and update Codex/Claude plugin metadata and tests for the relocated engine path.
- **Claude Code cache resolution.** Resolve Claude plugin installs to `skills/last30days/scripts/last30days.py` after the plugin-layout restructure.

## [3.1.0] - 2026-04-22

Consolidates the 3.0.10 to 3.0.14 dev cycle (commenter handles, `--competitors`, per-entity Step 0.55, vs-mode N passes, comparison title attribution) and republishes the OpenClaw bundle, which had been frozen on ClawHub at `3.0.0-open` since April 8.

### Added

- **OpenClaw republish.** `clawhub install last30days-official` now resolves to `3.1.0-open`, matching current main. Closes [#307](https://github.com/mvanhorn/last30days-skill/issues/307), [#195](https://github.com/mvanhorn/last30days-skill/issues/195), [#236](https://github.com/mvanhorn/last30days-skill/issues/236). The ClawHub bundle had shipped a broken `env.py get_config()` and stale SKILL.md path references since April; both are fixed at source on main and the republish carries the fixes to installers.

### Fixed

- **Claude Code plugin manifest path-escape.** The `.claude-plugin/plugin.json` `skills` key was removed in commit `93fbed2` but never shipped in a tagged release. Installing via `/plugin install last30days-skill` could hit `/doctor`'s `Path escapes plugin directory: ./ (skills)` error. This release ships the fix. Closes [#306](https://github.com/mvanhorn/last30days-skill/issues/306).
- **Broken README link.** The README's "source of truth" link pointed at root `SKILL.md`, which is no longer maintained after the plugin-layout restructure. Fixed to point at `skills/last30days/SKILL.md`.

### Dev cycle journal (3.0.10 - 3.0.14, not separately tagged)

Individual changelog entries for 3.0.10 through 3.0.14 below document the incremental work consolidated into this release.

## [3.0.14] - 2026-04-22

### Changed

- **Comparison-mode title attribution.** The synthesis title for vs-mode and `--competitors` outputs changes from `What the Community Says (Last 30 Days)` to `What the Community Says (/Last30Days)`. Surfaces the slash-command identity instead of restating the date range. Three SKILL.md occurrences updated; pure documentation change.

## [3.0.13] - 2026-04-22

### Changed

- **vs mode runs N full passes in parallel, one per entity.** Architectural revert of the 3-pass → 1-pass latency optimization from an earlier version. `/last30days "OpenAI vs Anthropic vs xAI"` now runs three full `pipeline.run()` calls in parallel via the same fanout `--competitors` uses, producing three `*-raw.md` save files plus a merged comparison output. Each entity gets its own Step 0.55-grade targeting, own primary X handle weight, own subreddit scoping — apples-to-apples depth instead of the one-pool merged retrieval the single-pass path produced. Parallel execution keeps wall clock ≈ single pass.
- **`--competitors` is now a SKILL.md-level shortcut for vs-mode with auto-discovery.** The hosting reasoning model (Claude Code, Codex, Hermes, Gemini, any agent with WebSearch) performs discovery and Step 0.55 per entity via its own WebSearch tool, then invokes the engine with a vs-topic and `--competitors-plan` JSON. The engine flag remains for headless/cron use with BRAVE/EXA/SERPER/PARALLEL/OPENROUTER keys (engine-internal `auto_resolve` stays as fallback).
- **LAW 7-style stderr for `--competitors` with no backend** now leads with the hosting-model path (WebSearch + Step 0.55 + `--competitors-plan`) instead of `BRAVE_API_KEY`. API-key framing moved to a secondary "headless" section.

### Added

- **`--competitors-plan` JSON flag** for per-entity Step 0.55 targeting. Schema: `{entity_name: {x_handle?, x_related?, subreddits?, github_user?, github_repos?, context?}}`. Accepts inline JSON or a file path (matches `--plan`). When present for an entity, skips engine-internal `auto_resolve` and uses the provided values; missing fields fall back to `auto_resolve` (if backend) or planner defaults. Case-insensitive entity matching. The `subrun_kwargs_for` helper is the single source of truth for per-entity kwargs — no closure-default fallthrough from main scope.
- **Per-entity save files** when `--save-dir` is set on a vs-mode or `--competitors` run. Each entity's sub-run produces its own `{slug}-raw.md` with a single-row Resolved Entities block — matches historical vs-mode behavior (N passes → N save files).
- **`--polymarket-keywords "kw1,kw2"`** to filter Polymarket matches for ambiguous single-token topics (e.g., "Warriors" → `nba,gsw,golden-state` kills Glasgow Warriors rugby and Honor of Kings Rogue Warriors noise).

### Fixed

- **BRAVE/SERPER footer nudge suppressed** when `--plan` or `--competitors-plan` is present. The nudge told Claude Code users to set an API key when they already have WebSearch via the hosting model. Nudge still fires for true headless runs (no `--plan`, no backend) where the advice is correct.
- **Override-leak regression testing.** 3.0.12 already fixed the main-topic `--subreddits` / `--x-handle` / `--github-*` from leaking into peer sub-runs via explicit per-entity kwargs scrubbing. This release adds a 4-test regression suite (`test_competitor_subrun_isolation.py`) locking in the invariant.

## [3.0.12] - 2026-04-22

### Fixed

- **Per-entity Step 0.55 resolution for competitor sub-runs.** In 3.0.11, only the main topic got X handle / subreddit / GitHub resolution; competitor sub-runs ran with planner defaults and produced visibly thinner evidence (Reddit 403 fallbacks, single-word queries). Each competitor sub-run now calls `resolve.auto_resolve()` inside `fanout.run_competitor_fanout` when a web backend is available, mirroring the main topic's pre-flight resolution. Per-entity X handle, subreddit list, GitHub user/repos, and news context are threaded into each sub-run's `pipeline.run()` call. Deep-copied config per sub-run prevents `_auto_resolve_context` cross-leak. Surfaces in a new `## Resolved Entities` output block so the resolution coverage is visible without reading stderr.
- **LAW 7 false-positive on internal fan-out sub-runs.** Each competitor sub-run was emitting the `[Planner] No --plan passed... YOU ARE the planner` stderr warning. LAW 7 targets the hosting-reasoning-model path, not engine-internal fan-out. New `internal_subrun=True` keyword on `planner.plan_query` and `pipeline.run` suppresses the warning for sub-runs only; the default path is unchanged.
- **Marketplace-stale SKILL.md trap.** Added a STEP 0 canonical-path self-check at the top of SKILL.md. Two of three 2026-04-22 test runs loaded SKILL.md from `plugins/marketplaces/last30days-skill/` (Claude-Code-managed git clone pinned to origin/main, lagging the versioned cache), then ran `--help` against the same stale path, did not see `--competitors`, and fell back to a manual comparison plan. The STEP 0 block forces any reader to verify they loaded from `plugins/cache/last30days-skill/last30days/{VERSION}/SKILL.md` and re-read from the versioned cache if not.

### Changed

- **Default `--competitors` count is now 2 (3-way total: original + 2 peers).** Previously 3. `--competitors=N` still customizes (range 1..6). Matches the feature description's canonical example (`Kanye vs Drake vs Kendrick`).

### Added

- **`## Resolved Entities` block** in `render_comparison_multi` output. Shows per-entity X handle, subreddits, GitHub user/repos, and truncated context for every entity in the comparison. Block is omitted entirely when no entity has a resolved payload (mock mode, no backend).

## [3.0.11] - 2026-04-22

### Added

- **`--competitors` flag for auto-discovered comparison fan-out.** Pass `--competitors` on a single-entity topic and the engine discovers 2-6 peer entities via web search, then runs the full pipeline on each in parallel and emits one N-way comparison. `last30days Kanye West --competitors` resolves Drake, Kendrick Lamar, and one more peer. `last30days OpenAI --competitors` resolves Anthropic, xAI, Google Gemini. `--competitors=N` controls count, `--competitors-list="A,B,C"` skips discovery and uses the explicit list. Discovery mirrors the `auto_resolve` pattern (Brave / Exa / Serper / Parallel) with deterministic text extraction - no internal LLM call. Sub-runs inherit the main `--quick`/`--deep`/`--days`, run in a `ThreadPoolExecutor`, and degrade gracefully when at least 2 entities survive. Output reuses the existing 9-axis `## Head-to-Head` scaffold.

## [3.0.10] - 2026-04-21

### Added

- **Commenter handles on evidence lines.** Top-comment rendering now includes the commenter's handle - `u/author` for Reddit, `@handle` for TikTok/YouTube/Instagram/Bluesky/X/Threads. The enrichment adapters already captured `author`; the render layer just was not using it. Evidence lines change from `- Comment (6822 upvotes): Finally, John Apple` to `- u/Cyrisaurus (6822 upvotes): Finally, John Apple`. Person-level citations make synthesis-side inline markdown links per LAW 8 much more natural. Both the compact and full render paths are covered.

### Fixed

- **TikTok author preference.** `_fetch_post_comments` in `scripts/lib/tiktok.py` preferred `user.nickname` over `user.unique_id`, so the engine captured display names ("Moosa Noormahomed") instead of @handles ("moosanoormahomed"). Flipped to prefer `unique_id`. Nickname still wins as a fallback when `unique_id` is missing. Display names can contain emoji, spaces, and non-Latin characters that do not round-trip to a profile URL; the @handle is the stable identifier.
- **Single plugin payload layout.** The canonical runtime moved to `skills/last30days/` for both Claude Code and Codex plugin loading. Root-level `SKILL.md`, `scripts/`, `agents/`, and `assets/` are no longer maintained as duplicate copies.

### Behavior fallback

- When an author is empty, `[deleted]`, or `[removed]`, the render falls back to the legacy `Comment (...)` shape - no `u/` or `@` prefix with an empty handle is ever emitted.

## [3.0.9] - 2026-04-18 - The Self-Debug Release

### Highlights

v3.0.9 adds the engine-side Class 1 keyword-trap refuse-gate ("birthday gift for 40 year old" now gets a clarifying question, not 5 minutes of junk), promotes TikTok and YouTube top comments to the same first-class rendering Reddit's got, lands Hermes AI Agent as a first-class deploy target, and moves the SKILL.md formatting contract from line 1094 to the top of the file.

"The Self-Debug Release" refers to how the fixes in 3.0.6-3.0.9 were written: 5 separate Opus 4.7 instances each debugged their own failed outputs. Three converged on "SKILL.md is too big and the LAWs are too deep." Two converged on "the engine should refuse demographic-shopping queries." I shipped exactly what they said. Validation: 5/5 canonical compliance.

### Added

- **Engine Class 1 keyword-trap refuse-gate** (`scripts/lib/preflight.py`, new). Pattern-matches demographic-shopping queries at main() front-door. Exit code 2 with structured REFUSE message. Escape hatch: `LAST30DAYS_SKIP_PREFLIGHT=1`. 29 tests in `tests/test_preflight.py`.
- **TikTok + YouTube top comments** rendered with same `💬 Top comment` prominence as Reddit's. Shipped in [#260](https://github.com/mvanhorn/last30days-skill/pull/260); enrichment fixed in [#265](https://github.com/mvanhorn/last30days-skill/pull/265).
- **Hermes AI Agent as a deploy target** - thanks @stephenmcconnachie ([#228](https://github.com/mvanhorn/last30days-skill/pull/228)). `scripts/sync.sh` detects `~/.hermes/skills/research` and deploys automatically.
- **Multi-key SCRAPECREATORS_API_KEY rotation** - thanks @zaydiscold ([#268](https://github.com/mvanhorn/last30days-skill/pull/268)). Set `SCRAPECREATORS_API_KEY_1`, `_2`, etc. Engine rotates on rate-limit.
- **Offline quality evaluation fixture** - thanks @j-sperling ([#233](https://github.com/mvanhorn/last30days-skill/pull/233)). `eval_topics.json` lets contributors run quality regressions without burning live API credits.
- **END-OF-CANONICAL-OUTPUT boundary** in `render_compact()`. Engine now emits an explicit pass-through instruction so re-synthesis requires actively ignoring a visible boundary.
- **LAW 1 verbatim-pattern override.** LAW 1 now quotes the exact WebSearch tool-result reminder ("CRITICAL REQUIREMENT: MUST include Sources: section") and declares it OVERRIDDEN inside last30days output.

### Changed

- **SKILL.md restructure.** VOICE CONTRACT LAWs and BADGE MANDATORY block moved from line 1094 to lines 75-150. Grounded in 3 separate Opus 4.7 self-debugs.
- **Engine emits the badge as stdout.** `🌐 last30days v3.0.9 · synced YYYY-MM-DD` is the first line of every compact emit. Pass-through is now the default-correct behavior.
- **Reddit client HTTP consolidation** - thanks @iliaal ([#207](https://github.com/mvanhorn/last30days-skill/pull/207)). Migrated to `http.get(params=...)` helper.
- **ScrapeCreators header consolidation** - thanks @iliaal ([#209](https://github.com/mvanhorn/last30days-skill/pull/209)). `_sc_headers` refactored into `http.scrapecreators_headers`.
- **Simpler Hermes sync.** `scripts/sync.sh` Hermes branch now always uses main SKILL.md (previously had a `.hermes-plugin/SKILL.md` fallback that created a wrong-file-capture hazard).

### Fixed

- **Peter Steinberger trailing Sources leak.** 2026-04-18 validation failure where the model appended a TechCrunch / TED / Fortune / Wikipedia Sources list after the invitation. Now structurally prevented at three layers: engine emits the canonical body, LAW 1 quotes the exact WebSearch reminder, closing boundary names the anti-pattern.
- **Wrong-file SKILL.md capture.** Deleted `.agents/skills/last30days/SKILL.md` (1382 lines, April 13 snapshot) and `.hermes-plugin/SKILL.md` (269 lines). One SKILL.md per plugin now, at the plugin root.
- **GitHub date parsing garbage** - thanks @iliaal ([#208](https://github.com/mvanhorn/last30days-skill/pull/208)). `_parse_date` now rejects invalid input cleanly.
- **Windows Bird X stability** - thanks @Chelebii ([#227](https://github.com/mvanhorn/last30days-skill/pull/227)).
- **Linux `check_perms` false-warn** - thanks @george231224 ([#216](https://github.com/mvanhorn/last30days-skill/pull/216)). Uses GNU stat first.
- **UTF-8 saved output** - thanks @Gujiassh ([#225](https://github.com/mvanhorn/last30days-skill/pull/225)).
- **Version metadata alignment** - thanks @Gujiassh ([#217](https://github.com/mvanhorn/last30days-skill/pull/217)) and @shalomma ([#229](https://github.com/mvanhorn/last30days-skill/pull/229)).
- **`--days` alias backcompat** - thanks @BryanTegomoh ([#230](https://github.com/mvanhorn/last30days-skill/pull/230)).
- **`INCLUDE_SOURCES` env default** - thanks @hnshah ([#223](https://github.com/mvanhorn/last30days-skill/pull/223)).
- **Bird X all-None engagement** - thanks @j-sperling ([#234](https://github.com/mvanhorn/last30days-skill/pull/234)).

### Contributors

@j-sperling, @stephenmcconnachie, @zaydiscold, @iliaal, @Chelebii, @Gujiassh, @hnshah, @george231224, @shalomma, @BryanTegomoh for PRs since v3.0.0. @uppinote20, @zerone0x, @thinkun, @thomasmktong, @fanispoulinakisai-boop, @pejmanjohn, @zl190, @Jah-yee, @dannyshmueli, @Cody-Coyote for issues and PRs that shaped the v3 roadmap.

### Recovery

```
/plugin update last30days
/reload-plugins
```

Verify: `cat ~/.claude/plugins/cache/last30days-skill/last30days/*/.claude-plugin/plugin.json | grep version` returns `"version": "3.0.9"`.

Smoke test: `/last30days birthday gift for 40 year old` should ask a clarifying question before running.

## [3.0.5] - 2026-04-15

### Added

- **`/last30days` slash command for plugin users.** New `commands/last30days.md` registers a Claude Code slash command. Users type `/last30days <topic>` and Claude Code's autocomplete prefix-matches it to the canonical `/last30days:last30days` form (the same way `/ce:plan` resolves to `/compound-engineering:ce-plan`). The command delegates to the existing `last30days` skill body — no skill behavior changes.

### Removed

- **`skills/last30days-nux/`** — byte-identical duplicate of root `SKILL.md` that created confusing `/last30days:last30days-nux` autocomplete entries via Claude Code's plugin namespacing. The root `SKILL.md` remains the canonical skill source.

### Recovery

```
/plugin update last30days
/reload-plugins
```

Then type `/last30days <topic>` to invoke the skill via slash command. Natural-language invocation ("search the last 30 days for X") continues to work unchanged.

## [3.0.4] - 2026-04-15

### Fixed

- **Cleared `/doctor` path-escape error on Claude Code v2.1.109+.** `.claude-plugin/plugin.json` previously declared `"skills": ["./"]`. That value shipped unchanged from v2.1.0 through v3.0.3 and worked on older Claude Code, but current versions reject `./` with `Path escapes plugin directory: ./ (skills)`. The `"skills"` key is now omitted entirely, matching the pattern used by every other plugin in the Claude Code marketplace ecosystem. Claude Code auto-discovers `skills/*/SKILL.md` when the key is absent.

### Recovery

If `/doctor` reports a path-escape error for last30days, run `/plugin update last30days` then `/reload-plugins`. If errors persist, uninstall and reinstall the plugin.

## [3.0.3] - 2026-04-15

### Fixed

- **Restored `skills/` and `.claude-plugin/` to the plugin install tarball.** v3.0.1 added `.gitattributes` rules that excluded both directories from `git archive` output to shrink the claude.ai `.skill` bundle. Claude Code's `/plugin install` fetches the same archive, so users installing v3.0.1 or v3.0.2 received a tarball with no plugin manifest and no skill files. `git archive v3.0.0` contained 8 files under those paths; `v3.0.1` and `v3.0.2` contained 0. This release reverts those `.gitattributes` lines.
- **Reverted `plugin.json` `"skills"` field to `["./"]`.** v3.0.2 changed this to `["skills"]` based on a misdiagnosis — the manifest change had no effect because the manifest wasn't in the tarball at all. The historical `["./"]` value shipped in every release from v2.1.0 through v3.0.0 without issues and is restored here.

### Recovery

Users on v3.0.1 or v3.0.2: run `/plugin update last30days` then `/reload-plugins`. If autoUpdate is enabled, the next session start will pull v3.0.3 automatically. Users on cached v3.0.0 or earlier installs were unaffected.

### Notes

- The claude.ai `.skill` bundle built by `scripts/build-skill.sh` still works — the archive grew from 89 to 97 files, well under the 200-file cap.
- claude.ai-specific exclusions (avoiding duplicate `SKILL.md` files in the bundle) should move into `scripts/build-skill.sh` rather than `.gitattributes` in a future release, since `.gitattributes` cannot distinguish between the two distribution channels.

## [3.0.2] - 2026-04-15

### Fixed

- **`/last30days` slash command now registers on Claude Code v2.1.105+.** `.claude-plugin/plugin.json` declared `"skills": ["./"]`, which newer Claude Code rejects with `Path escapes plugin directory: ./ (skills)`. The skill silently failed to register, so `/last30days <query>` returned "Unknown command" even though `/plugin list` showed the plugin as installed. Fix: `"skills": ["skills"]` so the loader scans the real skill subdirectory.
- **Version drift between manifests.** `.claude-plugin/marketplace.json` was pinned to `3.0.0` while `.claude-plugin/plugin.json` advertised `3.0.1`. The `/plugin` resolver used the marketplace version and could install stale cached metadata alongside the correct build. Both manifests now agree on `3.0.2`.

### Recovery

If `/last30days` stopped working for you, run `/plugin update last30days` then `/reload-plugins`. If `/doctor` still reports errors, uninstall and reinstall the plugin from the marketplace.

## [3.0.1] - 2026-04-14

### Fixed

- **Skill upload packaging** - `scripts/build-skill.sh` produces a claude.ai-upload-ready `.skill` file that fits under the 200-file cap. Previously, zipping the repo hit 406 files and the "Upload skill" UI rejected it outright.
- **SKILL.md description length** - trimmed from 228 to 167 chars (Anthropic caps descriptions at 200).

### Removed

- Unused root `vendor/` directory (215 files from an accidental commit in PR #48 - the real vendored X client lives at `scripts/lib/vendor/bird-search/`).
- Legacy top-level `plans/` directory (superseded by `docs/plans/`; both plans described work that was already shipped in v3).

### Added

- `.gitattributes` with `export-ignore` entries so `git archive` drops tests, docs, fixtures, assets, historical manifests, and internal skill subdirs. Mirrors Anthropic's canonical `package_skill.py` exclusions.
- `scripts/build-skill.sh` - one-command path to produce `dist/last30days.skill` with a single top-level `last30days/` folder, defensive `=200` file check, and dirty-tree refusal.
- `README.md` section documenting the claude.ai skill upload workflow.

## [3.0.0] - 2026-04-11

### Highlights

Intelligent search, fun judge, cross-source cluster merging, single-pass comparisons, and OpenClaw as a first-class citizen. The v3 engine doesn't just search for your topic -- it figures out *where* to search before the search begins. Engine architecture by @j-sperling.

### Added

- **Intelligent pre-research** -- Resolves X handles, subreddits, TikTok hashtags, and YouTube channels via a new Python brain before any API calls fire. Bidirectional: person to company, product to founder.
- **Fun judge / Best Takes** -- Second parallel LLM judge scores humor, cleverness, and virality. Surfaces the best reactions in a dedicated output section.
- **Cross-source cluster merging** -- Entity-based overlap detection merges the same story across Reddit, X, YouTube into one cluster instead of three separate items.
- **Single-pass comparisons** -- "X vs Y" runs one pass with entity-aware subqueries instead of three serial passes. 3 minutes instead of 12+.
- **GitHub as a source** -- Stars, reactions, and comments from repos and issues.
- **OpenClaw first-class citizen** -- Auto-resolve for engine-side pre-research. Device auth for frictionless ScrapeCreators signup.
- **Per-author cap** -- Max 3 items per author prevents single-voice dominance.
- **Entity disambiguation** -- Synthesis trusts resolved handles over keyword matches.
- **Perplexity Sonar Pro as additive source** -- AI-synthesized research with citations via OpenRouter. Opt-in via `INCLUDE_SOURCES=perplexity`. Returns structured narratives that complement social data.
- **Perplexity Deep Research** -- `--deep-research` flag for exhaustive 50+ citation reports (~$0.90/query). Premium opt-in for serious investigation.
- **OpenRouter as reasoning provider** -- One OPENROUTER_API_KEY powers planning, reranking, and Perplexity search. Auto-detected after Gemini/OpenAI/xAI.
- **Parallel AI grounding backend** -- `--web-backend parallel` or auto-detected via PARALLEL_API_KEY.
- **Grounding in planner** -- Grounding source properly registered in SOURCE_CAPABILITIES instead of force-injected.

### Changed

- YouTube transcript candidate pool widened 3x past music videos to reach talk/review content with captions
- Reddit comment enrichment sorted by total engagement (upvotes + comments), not just upvotes
- Polymarket display shows % odds only; dollar volumes removed
- 852 tests passing

### Fixed

- Marketplace validation: duplicate `name: last30days` collision in `skills/last30days/SKILL.md` caused strict validators to reject the plugin. Resolved by renaming the internal v3 architecture spec to `last30days-v3-spec` with `user-invocable: false`. Fixed in #214 (reported by @Cody-Coyote in #204).
- Stale README link to the deleted `skills/last30days-v3/` path from the v3 directory rename. Fixed in #214.
- OpenAI Codex CLI discoverability: added `.agents/skills/last30days/SKILL.md` as a real file (Codex's loader skips symlinked files) plus `.codex-plugin/plugin.json` as the namespace marker. The skill now registers as `last30days:last30days` when Codex runs in a checkout of the repo. Fixed in #219 (inspired by @Jah-yee in #153 and @dannyshmueli on X).

### Contributors

- @j-sperling -- v3 engine architecture, Python pre-research brain
- @hnshah -- Watchlist features
- @Cody-Coyote -- Marketplace validation bug report (#204)
- @Jah-yee -- Codex CLI integration inspiration (#153)

## [2.9.4] - 2026-03-06

### Changed

- Move save into Python script via `--save-dir` flag - raw research data saved during the existing script Bash call, zero extra tool calls after invitation
- Remove entire "Save Research to Documents" section from SKILL.md (~45 lines removed)
- No more `📎` footer, no Bash heredoc, no `(No output)`, no multi-minute cogitation after research

## [2.9.3] - 2026-03-06

### Fixed

- **Critical:** Switch save from `run_in_background` to foreground Bash - background callbacks caused model to re-engage, hallucinate fake user messages, and generate unsolicited multi-paragraph responses
- Save uses foreground `cat >` heredoc (executes sub-second, no callback, no delayed notification)

## [2.9.2] - 2026-03-06

### Fixed

- Save research silently using background Bash heredoc instead of Write tool (eliminates "Wrote N lines..." clutter)
- Suppress follow-up text after background save completes (no more "Research briefing saved..." noise)
- Add `📎` footer line for save path instead of verbose confirmation

## [2.9.1] - 2026-03-05

### Highlights

Auto-save research briefings to the default memory directory as topic-named .md files. Every run now builds a personal research library automatically - no more manual copy-paste.

### Added

- Auto-save complete research briefings (synthesis, stats, follow-up suggestions) to the default memory directory after every run
- Kebab-case filename generation from topic (e.g., "Claude Code skills" -> `claude-code-skills.md`)
- Duplicate topic handling: appends date suffix instead of overwriting (e.g., `claude-code-skills-2026-03-05.md`)
- Agent mode (`--agent`) also saves research files
- Brief confirmation after save with the saved file path

### Credits

- [@devin_explores](https://x.com/devin_explores) -- Inspired this feature by sharing their workflow of saving every last30days run into organized .md files ([PR #51](https://github.com/mvanhorn/last30days-skill/pull/51))

## [2.9.0] - 2026-03-05

### Highlights

ScrapeCreators Reddit as the default backend (one `SCRAPECREATORS_API_KEY` covers Reddit + TikTok + Instagram), smart subreddit discovery with relevance-weighted scoring, and top comments elevated with 10% scoring weight and prominent display.

### Added

- ScrapeCreators Reddit backend (`scripts/lib/reddit.py`) — keyword search, subreddit discovery, comment enrichment, all via `api.scrapecreators.com`
- Smart subreddit discovery with relevance-weighted scoring: frequency × recency × topic-word match, replacing pure frequency count
- `UTILITY_SUBS` blocklist to filter noise subreddits (r/tipofmytongue, r/whatisthisthing, etc.) from discovery results
- Top comment scoring: 10% weight in engagement formula via `log1p(top_comment_score)`
- Top comment rendering: `💬 Top comment` lines with upvote counts in compact and full report output
- Comment excerpt length increased from 300 → 400 chars; `comment_insights` limit raised from 7 → 10

### Changed

- `primaryEnv` switched from `OPENAI_API_KEY` to `SCRAPECREATORS_API_KEY` — one key now powers Reddit, TikTok, and Instagram
- Reddit engagement scoring formula: `0.55/0.40/0.05` (score/comments/ratio) → `0.50/0.35/0.05/0.10` (score/comments/ratio/top-comment)
- SKILL.md synthesis instructions updated to emphasize quoting top comments

### Fixed

- Utility subreddit noise in discovery (e.g., r/tipofmytongue appearing for unrelated topics)
- Reddit search no longer requires `OPENAI_API_KEY` — ScrapeCreators API handles search directly

## [2.8.0] - 2026-03-04

### Highlights

Instagram Reels as the 8th signal source, TikTok migrated from Apify to ScrapeCreators API, and SKILL.md quality improvements. One API key (`SCRAPECREATORS_API_KEY`) now covers both TikTok and Instagram.

### Added

- Instagram Reels as 8th research source via ScrapeCreators API — keyword search, engagement metrics (views, likes, comments), spoken-word transcript extraction (`scripts/lib/instagram.py`)
- `InstagramItem` dataclass, normalization, scoring (45% relevance / 25% recency / 30% engagement), deduplication, cross-source linking, and rendering
- Instagram in SKILL.md: stats template (`📸 Instagram:`), citation priority, item format description, output footer
- URL-to-name extraction examples in SKILL.md for cleaner web source display
- `--search=instagram` flag support

### Changed

- TikTok backend migrated from Apify to ScrapeCreators API (`api.scrapecreators.com`)
- `APIFY_API_TOKEN` replaced by `SCRAPECREATORS_API_KEY` in config
- SKILL.md version bumped to v2.8
- WebSearch citation instruction strengthened to prevent trailing Sources: blocks
- Security section updated: Apify → ScrapeCreators references

### Fixed

- Web stats line showing full URLs instead of plain domain names
- Trailing "Sources:" block appearing after skill invitation (WebSearch tool mandate conflict)
- Instagram/TikTok not running in web-only mode when `--search=instagram` used without Reddit/X
- `$ARGUMENTS` quoting in SKILL.md for correct flag forwarding

## [2.1.0] - 2026-02-15

### Highlights

Three headline features: watchlists for always-on bots, YouTube transcripts as a 4th source, and Codex CLI compatibility. Plus bundled X search with no external CLI needed.

### Added

- Open-class skill with watchlists, briefings, and history modes (SQLite-backed, FTS5 full-text search, WAL mode) (`feat(open)`)
- YouTube as a 4th research source via yt-dlp -- search, view counts, and auto-generated transcript extraction (`feat: Add YouTube`)
- OpenAI Codex CLI compatibility -- install to `~/.agents/skills/last30days`, invoke with `$last30days` (`feat: Add Codex CLI`)
- Bundled X search -- vendored subset of Bird's Twitter GraphQL client (MIT, originally by @steipete), no external CLI needed (`v2.1: Bundle Bird X search`)
- Native web search backends: Parallel AI, Brave Search, OpenRouter/Perplexity Sonar Pro (`feat(engine)`)
- `--diagnose` flag for checking available sources and authentication status
- `--store` flag for SQLite accumulation (open variant)
- Conversational first-run experience (NUX) with dynamic source status (`feat(nux)`)

### Changed

- Smarter query construction -- strips noise words, auto-retries with shorter queries when X returns 0 results
- Two-phase search architecture -- Phase 1 discovers entities (@handles, r/subreddits), Phase 2 drills into them
- Reddit JSON enrichment -- real upvotes, comments, and upvote ratio from reddit.com/.json endpoint
- Engagement-weighted scoring: relevance 45%, recency 25%, engagement 30% (log1p dampening)
- Model auto-selection with 7-day cache and fallback chain (gpt-4.1 -> gpt-4o -> gpt-4o-mini)
- `--days=N` configurable lookback flag (thanks @jonthebeef, [#18](https://github.com/mvanhorn/last30days-skill/pull/18))
- Model fallback for unverified orgs (thanks @levineam, [#16](https://github.com/mvanhorn/last30days-skill/pull/16))
- Marketplace plugin support via `.claude-plugin/plugin.json` (inspired by @galligan, [#1](https://github.com/mvanhorn/last30days-skill/pull/1))

### Fixed

- YouTube timeout increased to 90s, Reddit 429 rate limit fail-fast
- YouTube soft date filter -- keeps evergreen content instead of filtering to 0 results
- Eager import crash in `__init__.py` that broke Codex environments
- Reddit future timeout (same pattern as YouTube timeout bug)
- Process cleanup on timeout/kill -- tracks child PIDs for clean shutdown
- Windows Unicode fix for cp1252 emoji crash (thanks @JosephOIbrahim, [#17](https://github.com/mvanhorn/last30days-skill/pull/17))
- X search returning 0 results on popular topics due to over-specific queries

### New Contributors

- @JosephOIbrahim -- Windows Unicode fix ([#17](https://github.com/mvanhorn/last30days-skill/pull/17))
- @levineam -- Model fallback for unverified orgs ([#16](https://github.com/mvanhorn/last30days-skill/pull/16))
- @jonthebeef -- `--days=N` configurable lookback ([#18](https://github.com/mvanhorn/last30days-skill/pull/18))

### Credits

- @galligan -- Marketplace plugin inspiration
- @hutchins -- Pushed for YouTube feature

## [1.0.0] - 2026-01-15

Initial public release. Reddit + X search via OpenAI Responses API and xAI API.

[3.0.9]: https://github.com/mvanhorn/last30days-skill/compare/v3.0.5...v3.0.9
[2.9.1]: https://github.com/mvanhorn/last30days-skill/compare/v2.9.0...v2.9.1
[2.9.0]: https://github.com/mvanhorn/last30days-skill/compare/v2.8.0...v2.9.0
[2.8.0]: https://github.com/mvanhorn/last30days-skill/compare/v2.6.0...v2.8.0
[2.1.0]: https://github.com/mvanhorn/last30days-skill/compare/v1.0.0...v2.1.0
[1.0.0]: https://github.com/mvanhorn/last30days-skill/releases/tag/v1.0.0
