# Plan 0023 | Durable all-source intelligence tick MVP

State: OPEN
Roadmap: P07
Date: 2026-08-04
Plan version: 2
Predecessor: Plan 0018 version 28/checkpoint P0018-C76

## Stable Goal

Build and prove one manual, durable, all-source intelligence tick before any
recurring timer is enabled. One tick must collect every enabled target across
all configured services, publish immutable raw evidence, analyze and catalog
the result, enrich images with OCR and semantic sidecars, detect and escalate
operator-actionable failures, and atomically publish one coherent lexical and
semantic query snapshot.

The tick is the product unit. A future timer may only enqueue that exact unit;
it may not introduce a second execution path or weaker safeguards.

## Product Decision

Browser-backed services are ordinary provider adapters, not exceptional or
second-class sources. Agent-browser may acquire pages without a Guacamole
lease. Guacamole exists only for temporary human observation after an incident
has been persisted, notified, and explicitly acknowledged for observation.

The repository contains generic tick machinery, supported adapter types,
schemas, validators, and test fixtures. Service definitions, targets, provider
order, credentials references, notification routing, tenant/recipient fields,
budgets, thresholds, retention, schedules, and operator particulars are
versioned user-scoped configuration. No operator-specific incident recipient,
email address, browser profile, tenant, or credential belongs in repo data.

## Current State

Fresh read-only evidence on 2026-08-04 establishes this starting point:

- `last30days.service` is active/running and reports service 0.2.29, database
  schema 12, ready status, and all five configured sources ready;
- the corpus and active immutable index
  `index-d4b3c45667cc2f635c557b85` are complete at 62 documents and 62
  embeddings;
- all 42 collection specifications are disabled; no recurring collection is
  authorized by this plan;
- the corpus contains 47 media references: 41 images and 6 videos, with 32
  source alt-text values, but it has no OCR, semantic-sidecar, media-asset, or
  incident tables;
- `CollectionCoordinator` already owns per-spec interval enqueueing, leases,
  attempts, and durable run state; `CorpusPublisher` already validates work
  identity, persists immutable envelopes, versions documents, records
  sightings, embeds pending version chunks, and publishes immutable indexes;
- `HybridRetriever` is already a deep retrieval module hiding FTS, vector,
  access filtering, fusion, and immutable index-head mechanics;
- `ServiceSourcePolicy` still embeds the supported source/access-method matrix
  in code and reads effective orders mainly from environment fields. It does
  not yet implement versioned user-defined services, targets, provider
  capabilities, notification chains, or a frozen global tick config;
- media is retained as JSON on documents and versions. Only normalized source
  text becomes searchable chunks and embeddings;
- there is no global tick identity, lane/stage receipt graph, incident state
  machine, screenshot artifact store, notification delivery ledger, OCR
  channel, semantic-sidecar channel, or atomic terminal tick query head.

Plan 0018/C76 terminally accepted service distribution, browser profile
binding, source-local outcome handling, durable publication, and immutable
index integrity. Those are foundations; this plan does not reopen their
historical canaries or forecast-calibration experiment.

## Scope

This plan owns the first production-shaped manual tick and the deterministic
machinery required to prove it:

1. a strict versioned user-scoped tick configuration contract;
2. one deep `enqueue_tick` interface shared by manual and future scheduled
   triggers;
3. immutable tick, attempt, lane, stage, budget, provider, evidence, incident,
   artifact, derivative, notification, and index-promotion receipts;
4. config-driven service and target expansion into one immutable lane set;
5. provider capability/admission, resource-key concurrency, bounded retry, and
   explicit sequential fallback;
6. raw evidence publication before derived work;
7. per-item/per-lane analysis followed by a cross-source catalog join;
8. user-scoped content-addressed image and rendered-page artifacts;
9. OCR and typed semantic sidecars for images and video thumbnails;
10. deterministic anomaly and browser-challenge detection with persisted
    incidents and configurable notification failover;
11. coherent lexical/semantic staging indexes and atomic ordinary-query-head
    promotion at terminal tick completion;
12. crash recovery, idempotent replay, overlap accounting, and one manual
    acceptance tick over every enabled target.

## Non-Goals

- no recurring timer, enabled schedule, unattended recurrence, or timer-owned
  source attempt;
- no broad historical backfill; backfill is a separate bounded job using the
  same immutable evidence and derivative interfaces;
- no arbitrary command or user-supplied code execution from configuration;
- no full video retrieval, audio extraction, transcription, scene analysis,
  or general video understanding;
- no model-owned state transition, provider selection, access decision,
  incident declaration, index promotion, or durable target creation;
- no destructive merge of records from different services;
- no repo-stored runtime corpus, screenshots, credentials, notification
  recipients, tenant IDs, email addresses, or browser-session particulars;
- no release, tag, public publication, paid overage, credential addition, or
  unrelated source/browser cleanup.

## Vocabulary And Identity

- **Tick**: one immutable global interval and frozen config revision.
- **Service**: a configured source identity plus an ordered provider policy,
  health rules, limits, and capabilities.
- **Target**: a configured topic, profile, feed, channel, account, or selector
  expanded against a service.
- **Lane**: one immutable service/target/access-partition unit inside a tick.
- **Stage**: a terminally accounted collection, publication, enrichment,
  catalog, notification, or index operation.
- **Provider attempt**: one adapter execution under a frozen lane/provider
  identity and resource budget.
- **Artifact**: content-addressed user-scoped bytes with provenance, access
  partition, retention, and integrity metadata.
- **Derivative**: OCR, semantic sidecar, screenshot, thumbnail, or other
  versioned output linked to an immutable parent.

Tick identity is derived from schedule identity, exact UTC interval, and the
frozen config revision. Recovery or explicit replay creates a new execution
attempt beneath the same tick identity. It never invents a new coverage window.
A config change requires a new tick or a separately identified backfill.

Source-item identity is stable within service and access partition using the
provider-native ID when available and canonical source identity otherwise.
Unchanged repeat observations create sightings, not duplicate searchable
documents. Changed text, media, metadata, or access state creates an immutable
version. Non-observation is not deletion; only explicit deleted,
access-denied, or verified-not-found evidence creates a preserved tombstone or
unavailable state.

## Deep Tick Module

The external seam is intentionally small:

```text
enqueue_tick(TickRequest) -> TickReceipt
get_tick(TickId) -> TickReceipt
```

Manual operation and the future scheduler both call `enqueue_tick`. Callers do
not coordinate providers, browser profiles, retries, budgets, enrichment,
notifications, or index publication.

```text
manual trigger -----+
                    +--> TickCoordinator.enqueue_tick
future scheduler ---+             |
                                  +-- freeze config/window/lanes/budgets
                                  +-- collect through provider adapters
                                  +-- publish immutable raw evidence
                                  +-- enrich and catalog
                                  +-- persist/escalate incidents
                                  +-- stage lexical/semantic snapshots
                                  +-- atomically promote terminal head
                                  +-- emit terminal TickReceipt
```

Internal seams exist only where behavior genuinely varies:

- installed provider adapters and in-memory test adapters;
- user-config stores and immutable frozen-config records;
- content-addressed artifact storage and in-memory test storage;
- OCR and semantic-sidecar adapters;
- notification transports, including generic Slack-receipts and GWS-email
  adapters plus test adapters;
- embedding providers and immutable index publishers.

The deterministic host owns identities, canonical JSON/hashes, provenance,
state transitions, budgets, access partitions, validation, and publication.
Models return schema-validated proposals with explicit inputs, provider/model
version, confidence, and provenance.

## User-Scoped Configuration Contract

Add one versioned config document beneath `LAST30DAYS_CONFIG_DIR` or the
standard user config directory. The exact filename and schema version are
defined in the first implementation packet and documented in
`CONFIGURATION.md`. The repo may include only sanitized examples.

The schema separates:

- `services`: source identity, installed adapter type, capability declaration,
  health checks, resource keys, limits, ordered provider chain, explicit
  fallback conditions, and credential references;
- `targets`: service reference, selector/surface, access partition, retention,
  enabled state, and bounded collection/enrichment limits;
- `tick`: cadence metadata for boundary calculation, timezone, aggregate
  ceilings, lateness bound, warning/critical thresholds, and anomaly rules;
- `artifacts`: user-scoped root, retention and garbage-collection policy,
  access enforcement, and optional encryption-at-rest adapter;
- `analysis`: enabled deterministic and model-backed stages with model/provider
  references and ceilings;
- `notifications`: ordered transports, readiness rules, routing fields,
  cooldown/reminder policy, acknowledgment behavior, and credential refs;
- `query`: embedding space, fusion/ranking versions, result limits, and
  ordinary query-head policy.

Configuration selects installed, capability-declared adapter types. It cannot
name arbitrary executables, shell fragments, Python modules, URLs to execute,
or unregistered code. Credential references are resolved at runtime and never
copied into frozen config records or receipts.

Every enabled target participates in every tick. Target-specific cadences are
out of scope for this MVP. Client instructions may be deterministically or
model-assisted translated into request-scoped searches, filters, or proposed
sync targets. A durable target begins only after schema validation and explicit
client confirmation, and only in the next tick. It may not silently widen
recurring scope, access, or budget.

Missing or invalid required config, including the absence of at least one
notification transport that passes a non-message readiness check, fails tick
preflight before any source work.

## Window, Overlap, And Admission Semantics

- Every tick freezes one half-open interval
  `[previous_tick_boundary, current_tick_boundary)` and attributes all lane
  evidence to it.
- Boundaries are derived from the configured cadence and timezone without
  completion-time drift, then persisted in UTC. Delayed ticks keep their
  original intervals.
- Global tick execution concurrency is one. If a boundary arrives while a tick
  is active, create one distinct queued tick. Start it after the current tick
  only within the configured lateness bound; otherwise terminalize it as
  `missed_due_to_overlap` and record a coverage gap. Never merge or silently
  drop intervals.
- Within a tick, provider-declared resource keys control concurrency. Lanes may
  run concurrently only when they do not share a browser profile, API quota,
  credential, provider cap, or other exclusive resource.
- Every enabled lane is admitted or terminally refused with a receipt. Silent
  skipping is invalid.

## Tick And Lane State Machines

Tick states are:

```text
queued -> preflight -> collecting -> analyzing -> cataloging -> indexing
       -> complete | complete_degraded | failed
```

Recovery may re-enter only an incomplete state under the same tick identity.
`missed_due_to_overlap` is a terminal coverage outcome. Shared integrity
failures such as config/hash/ownership/index corruption may terminate the tick
as `failed`. Source-local failures do not abort unrelated lanes.

Every expected stage for every lane must terminate as exactly one of:

- `success`
- `empty`
- `unsupported`
- `failure`
- `blocked_human`
- `budget_exhausted`

A tick cannot close while an expected stage is merely pending. A source-local
failure, blocked-human lane, exhausted lane, failed derivative, or exhausted
notification chain produces `complete_degraded` when global integrity remains
sound. A healthy zero-yield lane is valid `empty`, never a silent skip.

## Provider Selection, Retry, And Budgets

Each service has an ordered provider chain with explicit conditions for
advancing. The tick freezes the chain revision and records every attempted and
selected provider. Fallback is sequential by default and never occurs after an
authentication, policy, budget, access-partition, or deterministic data
integrity failure unless that exact condition is configured as eligible.

The service owns at most one retry for a failure explicitly classified as
transient. Never automatically retry:

- authentication or reauthentication;
- CAPTCHA or Cloudflare challenge;
- policy or quality rejection;
- healthy zero yield;
- budget exhaustion or rate-limit exhaustion;
- deterministic contract, schema, identity, or integrity failure.

The host enforces aggregate tick ceilings plus per-service and per-provider
item, request, wall-time, attempt, model-token, and cost ceilings. Lanes do not
borrow beyond their configured caps. When the aggregate ceiling is reached,
stop admitting new work, preserve all already-published evidence, and
terminalize affected lanes. Configurable warning thresholds emit incidents;
critical exhaustion never raises a ceiling, selects an unconfigured provider,
or incurs paid overage.

## Immutable Evidence And Cross-Source Catalog

Raw normalized acquisition envelopes and referenced source artifacts publish
before analysis, OCR, sidecards, clustering, or index promotion. Derived-stage
failure is replayable from immutable evidence without rescraping.

Different services remain different evidence. Never destructively merge
Reddit, X, Facebook, LinkedIn, YouTube, web, or other provider records. A
versioned derived catalog may cluster probable duplicates, shared stories,
entities, corroborations, contradictions, trends, and events while preserving
every member record and provenance edge.

Per-item and per-lane analysis may run as evidence arrives. Cross-source
cataloging begins only after every collection lane is terminal. Models may
propose entities, relationships, claims, clusters, explanations, or target
translations, but deterministic validators own acceptance and publication.

## Media, OCR, And Semantic Sidecars

Store image bytes and video thumbnails in a user-scoped content-addressed
artifact store. Retention and optional garbage collection are configurable.
Durable hashes, metadata, provenance, derivative IDs, and receipts survive
optional byte garbage collection. Runtime artifacts never live in the repo.

The first multimodal scope is images and video thumbnails:

- OCR preserves ordered regions, bounding boxes, confidence, detected
  language, engine/version, and source-asset coordinates;
- normalized OCR full text is a separate lexical candidate channel;
- a typed semantic sidecar contains literal visual description, entities and
  relationships, objects/actions, inferred context, search terms,
  uncertainty, model/provider version, and input provenance;
- observable facts and model inference remain distinct fields;
- sidecar input may include the image, OCR, source alt text, and bounded parent
  context, preserving each input separately rather than blending them into one
  asserted truth;
- OCR and sidecars are not concatenated into normalized source text;
- parent evidence, source alt text, OCR, and sidecar channels fail and query
  independently.

Every derivative inherits the strongest parent access partition, redaction,
and retention class; no derivative can downgrade them. Image-derived citations
include parent document version, media asset ID/hash, source URL, derivative
ID/version, and OCR region/confidence where applicable.

## Incident, Artifact, And Human Escalation Contract

The repo defines a stable incident vocabulary while provider adapters preserve
redacted native diagnostics. Initial types include:

- `captcha_required`
- `cloudflare_challenge`
- `rate_limit_warning`
- `rate_limit_blocked`
- `reauthentication_required`
- `provider_degraded`
- `notification_exhausted`

Deterministic configurable anomaly rules also cover yield collapse, rejection
spikes, latency growth, and missing media. Hard provider signals fire
immediately. Statistical rules remain `learning_baseline` until the configured
minimum number of comparable terminal ticks exists. Models may explain an
incident but may not declare or resolve it.

Incident handling order is immutable:

1. persist the incident and transition receipt;
2. capture required protected artifacts;
3. attempt the configured notification chain;
4. record every delivery receipt;
5. terminalize the affected lane and tick without waiting indefinitely for a
   person.

Incidents deduplicate on a stable source/profile/stage/class fingerprint.
Notify on first detection, meaningful severity/state change, and configured
bounded reminders—not every tick. A later exact successful execution of the
same source/profile/stage resolves the incident, records recovery, and sends
one resolution notification. A generic health check is not resolution proof.

Browser incidents capture one bounded screenshot on first detection and each
meaningful state change. Store the page exactly as rendered, without content
redaction, in the mandatory parent access partition with provenance and hash.
Encryption at rest is configurable; access-partition enforcement is not.

Notifications never embed or upload screenshots, raw rendered content,
cookies, tokens, credentials, or authentication evidence. They contain safe
incident metadata and a protected artifact reference.

Notification transports are an ordered, user-configured sequential failover
chain. The generic Slack-receipts adapter may be followed by a generic GWS
email adapter, but order and all routing particulars are config data. Stop
after the first successful delivery. Record success/failure for each attempted
transport and never duplicate after success.

If every configured transport fails, persist critical
`notification_exhausted` and close the current tick `complete_degraded`. The
next tick fails preflight before source work until at least one transport
passes a non-message readiness check.

CAPTCHA, Cloudflare, blocked rate limits, and reauthentication terminalize the
affected lane as `blocked_human`; other lanes continue and the tick closes.
The unattended tick never waits indefinitely. A Guacamole observation lease is
acquired only after a human acknowledges the incident and requests
observation. The follow-up contains agent-browser's direct external Guacamole
URL, never a localhost repo/dashboard link. Informational rate-limit warnings
do not allocate Guacamole automatically.

## Query And Index Publication Contract

Persist raw evidence immediately but build immutable lexical, semantic, OCR,
sidecar, and catalog staging snapshots under the tick. Ordinary queries do not
see an in-progress tick. Operator diagnostics may explicitly inspect staging
evidence.

When the tick reaches `complete` or `complete_degraded`, atomically advance the
ordinary query head to its coherent snapshot. A degraded snapshot includes all
successful, internally consistent lanes and derivatives plus tick/lane/stage
completeness, freshness, incidents, and coverage-gap metadata. Stale data may
remain queryable only with its originating tick and freshness labels.

Query processing applies tenant, access-partition, source, and time filters
before candidate retrieval. Lexical, source-alt-text, OCR, semantic-source,
semantic-sidecar, and catalog channels retrieve independently and combine with
versioned deterministic rank fusion. Optional model reranking may refine order
but cannot bypass filters, remove provenance, or become the only replay path.
Results expose matching channels and evidence.

Embedding model/dimensionality versions remain separate vector spaces. Build a
replacement index in staging, replay/backfill from immutable evidence, validate
it, and atomically promote it. Never compare raw similarity scores across
incompatible spaces.

## Crash Recovery And Idempotency

On restart, reconcile the durable graph, verify hashes and terminal receipts,
reacquire only expired execution leases, and resume only incomplete work under
the same tick/lane/stage identities. Completed stages are immutable and
idempotent. Recovery must prove:

- no duplicate provider attempt beyond frozen retry authority;
- no duplicate source version, sighting, artifact, derivative, incident,
  notification, or index promotion;
- no lost already-published raw evidence;
- no query-head movement before a terminal coherent snapshot;
- exact budget accounting across execution attempts.

## Tick Receipt

The terminal receipt contains:

- tick identity, schedule identity, UTC interval, trigger, and attempt IDs;
- frozen non-secret config revision/hash and expanded immutable lane manifest;
- provider attempts, selected providers, resource keys, fallback reasons, and
  budgets consumed;
- every expected stage and terminal state;
- evidence, media, artifact, derivative, and catalog manifest hashes;
- code, schema, adapter, OCR, model, embedding, fusion, and index versions;
- incident transitions, protected artifact refs, acknowledgment state, and
  notification delivery receipts;
- anomaly/baseline results, query staging snapshots, and atomic head-promotion
  result;
- completeness, freshness, coverage gaps, recovery history, and terminal tick
  classification.

## Data And Write Surfaces

Implementation may extend the existing service modules and schema with narrow
owners for:

- tick configuration validation/freezing and installed adapter registry;
- `TickCoordinator` orchestration and tick/lane/stage state;
- tick execution attempts, provider attempts, resource leases, and budget
  ledger;
- incident fingerprints/transitions, artifact refs, acknowledgments, and
  notification receipts;
- content-addressed media assets and rendered-page screenshots;
- OCR regions, semantic sidecars, and derivative provenance;
- derived cross-source cluster/member/conflict records;
- tick-bound staging snapshots and ordinary query-head promotion.

Expected repo write surfaces are
`skills/last30days/scripts/lib/service_*.py`, the service CLI/HTTP/MCP contracts
only as required by the deep interface, migrations, focused tests,
`CONFIGURATION.md`, canonical Skill references when an agent-facing operation
changes, and plan/roadmap/runbook/change-log files required by policy. Runtime
config and artifact mutations remain user-scoped and are separate gated
operations.

## Work Graph

| Packet | Outcome | Depends on | Integration/terminal gate |
|---|---|---|---|
| T01 contracts | Freeze tick/config/receipt/state schemas and the two-method deep interface | Plan 0023 | schema tests and no operator particulars in repo |
| T02 durable state | Add migrations, tick graph, attempts, stages, budgets, leases, and idempotent recovery | T01 | migration/rollback/replay tests |
| T03 config and providers | Replace source-matrix ownership with installed adapter registry plus user-defined services/targets/provider chains | T01, T02 | config/admission/fallback/resource-key tests |
| T04 evidence and media | Bind raw-first publication, stable versions/sightings, artifact store, OCR, and typed sidecars | T01, T02 | provenance/access/replay/citation tests |
| T05 incidents | Add deterministic detection, screenshots, dedup/resolution, notification chain, acknowledgments, and Guac observation gate | T01, T02 | mocked transport/failover/privacy/state tests |
| T06 catalog and query | Add cross-source derived clusters, independent query channels, staging snapshots, deterministic fusion, and atomic head promotion | T02, T04 | complete/degraded snapshot and embedding-space tests |
| T07 coordinator join | Execute every enabled lane through T03-T06 and emit one terminal tick receipt | T03, T04, T05, T06 | crash/overlap/budget/source-local/global-failure matrices |
| T08 manual acceptance | Run controlled failure scenarios and one bounded manual all-target tick | T07, human/live gate | independently reviewed acceptance receipt |
| T09 timer successor | Define thin recurring enqueue only after T08 closes this plan | T08, new plan/gate | explicitly outside Plan 0023 execution |

T01 and T02 are the critical path. After their interfaces stabilize, T03, T04,
and T05 are low-conflict parallelizable tracks, but no delegation is authorized
by this planning checkpoint. T06 joins T04. T07 is the serialized integration
owner. T08 is the only live product acceptance packet.

## Bounds, Gates, And Stop Conditions

Local goal bounds:

- maximum implementation attempts per packet: 2;
- maximum review/rework cycles per packet: 1;
- maximum consecutive hardening-only or no-progress checkpoints: 2;
- checkpoint after every validated packet and before install, live source work,
  user-config mutation, notification send, human observation, independent
  review, or closeout;
- active implementation-agent concurrency: 1 unless a later checkpoint
  explicitly assigns disjoint write surfaces under repo policy;
- active global runtime tick concurrency: 1;
- provider concurrency, requests, attempts, wall time, accepted items, model
  tokens, and cost: only the frozen user-config values for that tick.

Deterministic implementation, tests, fixtures, sanitized documentation, and
local migration rehearsal remain inside the approved product objective once an
implementation checkpoint is opened. Separate human/live gates remain for:

- installing or restarting a candidate service;
- modifying real user-scoped service, target, provider, credential-reference,
  notification, artifact, or tick config;
- calling live providers or sending a real notification;
- acquiring a Guacamole observation lease;
- enabling a timer or recurring spec;
- paid calls, ceiling increases, new tenants/sources/credentials/private-data
  classes, destructive actions, push, tag, publication, or release.

Stop and checkpoint on schema or access-partition ambiguity, non-idempotent
replay, mutable historical evidence/indexes, secret or operator-particular
leakage into repo data, unbounded model or provider loop, silent lane skip,
unconfigured fallback, budget overflow, duplicate notification, notification
content leakage, unrequested Guac allocation, ordinary-query exposure of
in-progress data, or two consecutive no-progress/hardening checkpoints.

## Acceptance Criteria

Plan 0023 is accepted only when current evidence proves all of the following:

1. One manual call to `enqueue_tick` freezes one config revision, one UTC
   interval, all enabled lanes, provider policies, and budgets.
2. Every enabled target is attempted or receives an explicit terminal
   admission receipt; source-local failures do not abort independent lanes.
3. Raw evidence and artifacts publish before derived stages and replay without
   rescraping.
4. Every expected stage terminalizes; the tick closes truthfully as
   `complete`, `complete_degraded`, or `failed` with no pending work.
5. Retry, fallback, concurrency, ceilings, threshold incidents, and budget
   exhaustion follow only the frozen policy and remain exactly auditable.
6. Stable source records retain immutable versions and sightings; cross-source
   clustering never merges away distinct service evidence; non-observation
   never fabricates deletion.
7. Images and video thumbnails preserve content-addressed assets, OCR regions,
   typed sidecars, provenance, inherited access, independent failure, and
   citation-ready IDs.
8. CAPTCHA, Cloudflare, rate-limit, reauthentication, provider degradation,
   and deterministic anomaly cases persist before notification, deduplicate,
   remind boundedly, resolve only on exact recovery, and protect raw artifacts.
9. Configured notification transports fail over sequentially with durable
   delivery receipts; exhaustion degrades the current tick and blocks the next
   preflight until readiness returns.
10. Agent-browser executes as a normal provider without Guac; a direct external
    Guac URL is produced only after incident acknowledgment and explicit human
    observation request.
11. Crash recovery and replay preserve tick identity, budgets, evidence, stage
    terminals, notification uniqueness, and query-head integrity.
12. Ordinary clients see only an atomically promoted terminal tick snapshot;
    degraded publication includes successful data plus exact coverage and
    freshness metadata.
13. Access/time/source filters precede independent lexical and semantic
    retrieval; deterministic fusion exposes matching channels and provenance;
    incompatible embedding spaces never share raw scoring.
14. Every configured provider adapter has prior non-zero normalization proof
    from a stable fixture or bounded canary. A healthy zero-yield lane may pass
    a tick but cannot serve as the adapter's only onboarding proof.
15. The terminal tick receipt independently reconstructs identities, hashes,
    versions, attempts, budgets, incidents, artifacts, derivatives, snapshots,
    and final state.
16. All schedules remain disabled and no recurring timer exists at closeout.

## Manual Acceptance Gate

Before T08 live execution, require:

- complete deterministic suite and migration/recovery matrices;
- mocked CAPTCHA, Cloudflare, rate warning/block, reauthentication, provider
  degradation, notification-failover/exhaustion, acknowledgment, and Guac-gate
  tests;
- a clean reviewed candidate commit and exact install/rollback artifact;
- sanitized readback that every enabled target/provider/resource/budget and
  notification transport is frozen from user config;
- an explicit bounded live packet covering every enabled lane, with exact
  attempt/request/item/wall/model/cost ceilings and one-at-a-time receipt
  verification;
- controlled crash/restart and replay proof under the same tick identity;
- independent terminal receipt review after the manual tick;
- zero enabled schedule and zero unrequested Guac leases afterward.

Timer admission is not a T08 side effect. T08 success closes Plan 0023 and may
seed a separate reviewed successor whose only new behavior is cadence-aligned
enqueueing of the already-proven tick.

## Definition Of Done

Close Plan 0023 when the deep tick interface, user-scoped configuration model,
durable state graph, provider execution, raw-first evidence, incidents and
notification failover, protected screenshots, OCR/sidecards, cross-source
catalog, hybrid terminal snapshots, recovery semantics, and manual all-target
acceptance tick all pass current deterministic and independent review evidence;
the installed runtime and rollback are identified; every schedule remains
disabled; and the next timer decision is represented only as a separate gate.

Checkpoint P0023-C19 is the current authority.

### Checkpoint P0023-C01 | 2026-08-04

Plan version: 1

State transition:

- `planned -> open`

Progress classification:

- `outcome_progress`; the operator-grilled design is converted into a bounded
  repo-native successor plan with the tick—not the timer—as the first MVP.

Owned changes:

- close Plan 0018 at its already-terminal C76 authority;
- create Plan 0023 and wire it as P07's sole actionable plan;
- preserve the accepted service/index/source evidence while defining the
  missing tick, incident, media-enrichment, catalog, and query contracts.

Validation evidence:

- fresh service status, source readiness, collection-spec counts, corpus/index
  counts, media counts, CodeGraph architecture evidence, planning policies,
  and the operator's sequential grilling decisions were reconciled before the
  plan was written.

Remaining acceptance criteria:

- T01-T08 and all 16 acceptance criteria remain; T09 is a separate successor.

Subagent status and reconciliation:

- `not_spawned`; the operator requested design conversion, not delegated or
  parallel implementation.

Graphiti write status:

- not written; this canonical plan, Roadmap wiring, and Runbook turn are the
  source-backed authority for the new work.

Authority classification:

- `human_gate`; this checkpoint authorizes documentation reconciliation only.
  It does not authorize implementation, installation, user-config mutation,
  source execution, real notification, Guac observation, recurrence, push,
  tag, publication, or release.

Next action:

- review Plan 0023 as the design freeze; when implementation is explicitly
  opened, begin T01 contracts without any live or user-config mutation.

### Checkpoint P0023-C02 | 2026-08-04

Plan version: 1

State transition:

- `design_open -> t01_active`

Progress classification:

- `outcome_progress`; the operator explicitly opened execution of Plan 0023,
  satisfying C01's implementation gate without widening any live boundary.

Owned changes:

- T01 contract and deep-interface implementation under
  `skills/last30days/scripts/lib/service_*.py`, schema catalog, focused tests,
  and the canonical plan/runbook surfaces required by policy.

Validation evidence:

- the worktree contains only the known Plan 0023 design-freeze changes;
- CodeGraph confirms the existing `CollectionCoordinator`, `CorpusPublisher`,
  `HybridRetriever`, strict contract helpers, and migration owner are the live
  seams to deepen rather than bypass.

Remaining acceptance criteria:

- T01-T08 and all 16 acceptance criteria remain. This checkpoint opens only
  deterministic implementation and tests for T01, followed by bounded T02
  work when T01 validates.

Subagent status and reconciliation:

- `not_spawned`; the critical-path contract/state work has overlapping write
  surfaces and CodeGraph provides direct structural discovery.

Graphiti write status:

- pending a validated implementation checkpoint; no derived memory is used as
  completion evidence.

Authority classification:

- `inherited_authority`; the explicit instruction to execute Plan 0023 opens
  deterministic repo implementation, tests, sanitized docs, and local
  migration rehearsal. Installation, real user-config mutation, live sources,
  real notifications, Guac observation, recurrence, push, tag, publication,
  release, paid calls, and ceiling increases remain closed.

Next action:

- execute the first TDD tracer through `enqueue_tick` and `get_tick`: freeze
  one config revision, one UTC interval, and one immutable expanded lane set in
  SQLite, then return the same receipt idempotently.

### Checkpoint P0023-C03 | 2026-08-04

Plan version: 1

State transition:

- `t01_active -> t03_active`

Progress classification:

- `outcome_progress`; T01 and the bounded T02 durable-state foundation now
  validate behind the two-method seam without opening any live boundary.

Owned changes:

- publish strict `TickRequest`, `TickLaneReceipt`, and `TickReceipt` v1
  contracts plus the sanitized user-scoped `tick-config-v1.json` schema;
- advance the deployable candidate to service 0.3.0/database schema 13 and
  synchronize Python/Go compatibility catalogs and deterministic packaging;
- persist immutable ticks, attempts, expanded lanes, expected stages, provider
  order, per-provider and aggregate budgets, resource leases, budget events,
  provider attempts, and recovery history;
- recover an expired execution attempt under the same tick identity, reset
  only in-progress stages, preserve idempotent graph rows, and fail closed on
  frozen-config or lane-digest corruption;
- document the exact user-scoped config filename and keep recurrence absent.

Validation evidence:

- the first TDD tracer failed on missing `lib.service_tick` and then passed with
  idempotent `enqueue_tick`/`get_tick` persistence;
- focused contract, tick, migration, temporal, release, runtime-package,
  lifecycle-install, and Skill-package validation passes 48/48;
- Go contract-catalog and client compatibility tests pass for schema 13;
- deterministic runtime packaging includes both versioned schemas and the new
  tick module under candidate service 0.3.0;
- migration rollback, concurrent initialization, legacy-data preservation,
  expired-attempt recovery, and frozen-config integrity checks all pass;
- `git diff --check` passes.

Remaining acceptance criteria:

- T03-T08 and Plan 0023 acceptance criteria 2-16 remain. T01/T02 establish the
  durable graph but do not call an adapter, publish evidence, send a
  notification, promote a query head, install the candidate, or enable a
  schedule.

Subagent status and reconciliation:

- `not_spawned`; the active schema/state surfaces overlap and no checkpoint
  authorized delegation.

Graphiti write status:

- pending a larger integrated milestone; this checkpoint and its deterministic
  tests remain the source-backed authority.

Authority classification:

- `inherited_authority`; proceed to deterministic T03 installed-adapter
  registry, strict config admission, sequential fallback, and resource-key
  tests. Installation, real user-config mutation, live source calls, real
  notifications, Guac observation, recurrence, push, tag, publication,
  release, paid calls, and ceiling increases remain closed.

Next action:

- replace hard-coded source/provider admission for the tick path with a
  capability-declared installed adapter registry and test strict config,
  sequential fallback eligibility, shared resource keys, and zero silent
  lanes using in-memory adapters only.

### Checkpoint P0023-C04 | 2026-08-04

Plan version: 1

State transition:

- `t03_active -> t07_recovery_active`

Progress classification:

- `outcome_progress`; the manual deterministic tick now joins config-driven
  providers, raw/versioned evidence, protected media, typed analysis,
  incidents, anomaly monitoring, cross-source cataloging, and terminal hybrid
  publication, while the remaining crash boundary is explicitly kept open.

Owned changes:

- admit only installed source-specific adapters with a concrete non-zero
  normalization fixture, then execute frozen provider chains with sequential
  fallback, one configured retry ceiling, resource leases, aggregate/provider
  budget admission, and preserved attempted/observed/accepted/rejected counts;
- persist content-addressed image and rendered-page artifacts, OCR regions,
  typed semantic sidecars, inherited access/retention, citation IDs, and
  immutable derivative failures selected through installed analysis adapters;
- classify and deduplicate CAPTCHA, Cloudflare, rate-limit,
  reauthentication, provider-degradation, and deterministic anomaly incidents;
  preserve exact rendered pages, sequential notification failover, stable
  reminder idempotency, exact recovery resolution, and acknowledged external
  agent-browser observation without allocating a Guac lease in the tick;
- publish immutable source records, versions, and sightings; build a
  deterministic exact-normalized-text cross-source catalog without merging
  source evidence; stage independent lexical, semantic, alt-text, OCR,
  sidecar, and catalog channels; apply filter-first RRF v1; and atomically
  promote only a terminal snapshot;
- expose manual `tick enqueue`, `tick get`, and incident
  get/acknowledge/observe commands from the user-scoped runtime assembly while
  creating no schedule or timer;
- make `TickReceipt` independently hashable over sanitized attempt, event,
  budget, provider, lease, evidence, artifact, derivative, incident,
  notification, anomaly, catalog, and snapshot manifests, including exact
  incident-artifact associations instead of a mutable latest pointer.

Validation evidence:

- TDD RED cases were observed for the absent manual runner, provider fallback,
  aggregate exhaustion, singleton overlap, late coverage gap, media and
  incident lifecycle, filter-first RRF, zero-baseline anomaly spike, measured
  worker rejection counts, cross-source catalog join, analysis-output failure,
  stable normalization proof, persistent rate-warning recovery, and terminal
  receipt reconstruction before their focused GREEN results;
- the focused Python tick/contract/migration/runtime/package acceptance set
  passes 94/94;
- the full repository Python suite passes at the C04 documented checkpoint;
- Go contract-catalog and service client tests pass against service 0.3.0 and
  database schema 13;
- generated Go contracts and the packaged runtime manifest are synchronized;
  no installed runtime, user config, source, notification, Guac lease, timer,
  or remote was touched.

Remaining acceptance criteria:

- T03, T05, and T06 are deterministically joined; T04 has a complete typed
  artifact/derivative path, but the production acquisition bridge has not yet
  proven image/video-thumbnail bytes or rendered-page bytes from every live
  browser-backed adapter;
- T07 is not complete: recovery is proven for the frozen coordinator graph and
  expired leases, but an interruption after provider completion and before raw
  publication cannot yet reconstruct the provider result without rescraping;
- because that T07 boundary remains, acceptance criteria 11 and 15 and all of
  T08 remain open. Criterion 16 remains preserved with every schedule disabled
  and no recurring timer implementation.

Subagent status and reconciliation:

- `not_spawned`; the active contract, runner, schema, and receipt surfaces
  overlap, and no checkpoint authorized delegation.

Graphiti write status:

- not written. This checkpoint is the compact source-backed authority; no
  durable memory write was requested.

Authority classification:

- `inherited_authority`; continue deterministic T07 recovery work only.
  Installation, real user-config readback or mutation, live providers, real
  notifications, Guac observation, independent review, recurrence, push, tag,
  publication, release, paid calls, and ceiling increases remain closed.

Next action:

- persist or atomically publish the bounded provider result so a crash at any
  provider/raw boundary resumes the same tick without a duplicate source call;
  rebuild snapshot inputs from durable evidence, then prove the controlled
  restart/replay matrix before preparing the clean candidate commit and T08
  human/live gate.

### Checkpoint P0023-C05 | 2026-08-04

Plan version: 1

State transition:

- `t07_recovery_active -> t08_candidate_review_pending`

Progress classification:

- `outcome_progress`; deterministic T07 recovery now crosses the provider/raw
  and between-lanes crash boundaries without another source call, budget
  charge, evidence identity, or partial-snapshot leak.

Owned changes:

- stage every bounded `ProviderResult` in
  `service_tick_provider_results` before raw publication, storing media and
  rendered-page bytes in the user-scoped content-addressed store and retaining
  only verified storage references and hashes in the durable payload;
- preserve `result_staged` provider attempts across expired execution leases,
  reuse their original provider-attempt identity, and finalize raw versions,
  raw media receipts, provider state, and resource release idempotently without
  invoking the adapter or consuming its budget twice;
- skip already-terminal lanes after restart, reconstruct lexical source,
  source-alt-text, OCR, and semantic-sidecar snapshot inputs from durable
  evidence, then perform cataloging and terminal head promotion over the full
  recovered tick rather than only current-process memory;
- add sanitized provider-result receipt manifests and controlled fault points
  proving both the provider/raw boundary and the between-lanes boundary.

Validation evidence:

- TDD recorded RED then GREEN for provider-result staging/replay and durable
  between-lanes snapshot reconstruction;
- the focused Python tick, media, incident, anomaly, query, runtime, contract,
  migration, package, lifecycle, and Skill acceptance set passes 119/119;
- the complete repository Python suite passes at this C05 documented state;
- Go internal contract and service packages pass against service 0.3.0 and
  database schema 13;
- generated runtime-package hashes are synchronized; Python compilation,
  canonical JSON parsing, diff hygiene, and the authority audit pass;
- no installed runtime, user config, live source, notification recipient,
  Guac lease, schedule, timer, remote, or external system was touched.

Remaining acceptance criteria:

- deterministic T07 and the restart portions of criteria 3, 11, and 15 are
  complete; the production acquisition bridge still needs bounded T08 proof
  that live browser-backed adapters carry image/video-thumbnail bytes and
  rendered-page screenshots through the typed artifact path;
- the exact candidate still requires independent review, install/rollback
  proof, sanitized user-config readback, a separately authorized bounded live
  all-target packet, and independent terminal receipt review;
- criterion 16 remains preserved: every schedule is disabled and no recurring
  timer has been implemented.

Subagent status and reconciliation:

- `not_spawned`; no applicable instruction authorized delegation, and the
  active schema, runner, recovery, receipt, and documentation surfaces were
  one overlapping critical path.

Graphiti write status:

- not written. Plan 0023/C05, Roadmap P07, and the corresponding append-only
  runbook turn are the compact source-backed authority; no memory write was
  requested.

Authority classification:

- `human_gate`; deterministic implementation and validation are complete.
  Independent review may inspect the exact local candidate, but installation,
  real user-config readback or mutation, live providers, real notifications,
  Guac observation, recurrence, push, tag, publication, release, paid calls,
  and ceiling increases remain closed.

Next action:

- bind this validated checkpoint into one coherent local candidate commit,
  independently review that exact commit and its build/install/rollback
  artifact, then stop for an explicit bounded T08 human/live authorization.

### Checkpoint P0023-C06 | 2026-08-04

Plan version: 1

State transition:

- `t08_candidate_review_pending -> exact_candidate_review_pending`

Progress classification:

- `outcome_progress` and `blocker_reduction`; the production acquisition seam
  now transports the media, rendered-page, and operator-route evidence that
  T08 must exercise instead of dropping it before the tick runner.

Owned changes:

- add bounded typed image and video-thumbnail bytes to the isolated worker
  result, enforce one aggregate binary-evidence envelope, and decode them into
  the existing content-addressed tick artifact path;
- capture the current rendered agent-browser tab for authentication, captcha,
  checkpoint, Cloudflare, and rate-limit incidents without requesting remote
  view or a Guacamole observation lease;
- carry only a direct external HTTPS agent-browser operator URL into the
  persisted incident, reject localhost/loopback routes, and return that stored
  route only after acknowledgment; the observation CLI no longer accepts a
  caller-supplied URL;
- require an absolute user-scoped artifact root and permit deployments to
  inject a code-owned provider registry, while configuration remains limited
  to selecting already-registered adapter types;
- advance the unreleased service 0.3.0 candidate from database schema 13 to
  schema 14, superseding the earlier local artifact without installing it.

Validation evidence:

- TDD recorded six initial failures at the media, screenshot, route, registry,
  and artifact-root seams, plus separate RED/GREEN aggregate binary-evidence
  and partial-result screenshot-carriage cases;
- the final focused contract, worker, and runner set passes 59/59; the complete
  repository Python suite exits zero; all Go packages pass; Python compilation,
  canonical JSON parsing, diff hygiene, and the plan-authority audit pass, with
  the audit reporting 8/8;
- three independent builds of
  `dist/service/last30days-service-0.3.0.tar.gz` are byte-identical at SHA-256
  `4f8a92db987b15c7de4d16bf966743198f55b4c6e610413aa93f299340e908d6`;
- read-only postflight confirms the installed runtime remains service 0.2.29,
  database schema 12, ready, with 42 collection specifications and zero
  enabled;
- no user config, live source, real notification, Guac lease, install, timer,
  remote, or external recipient was touched.

Remaining acceptance criteria:

- deterministic media/screenshot carriage is fixture-proven, but T08 must
  still prove every enabled production adapter against one separately
  authorized controlled-failure and manual all-target live packet;
- the exact local candidate still requires independent review,
  install/rollback proof, sanitized user-config readback, and independent
  terminal receipt review;
- criterion 16 remains preserved: every schedule is disabled and no recurring
  timer has been implemented.

Subagent status and reconciliation:

- `not_spawned`; the active runtime instruction explicitly prohibited
  delegation. Consequently an independent evaluator was not available in this
  slice and that review gate is not claimed as passed.

Graphiti write status:

- provider readiness passed. The initial compact episode is still `running` as
  job `44b0d8e8-f171-4e43-9ac3-60c6e8ee97cd`; after final review changed the
  artifact digest, an explicit final-state correction was queued behind it as
  job `ea998210-8dca-44eb-9d43-06b1457294e2` so the earlier in-slice digest is
  superseded rather than presented as final.

Authority classification:

- `human_gate`; deterministic implementation and candidate construction are
  complete. Installation, real user-config readback or mutation, live
  providers, real notifications, Guac observation, recurrence, push, tag,
  publication, release, paid calls, and ceiling increases remain closed.

Next action:

- independently review the exact local candidate commit and reproducible
  build/install/rollback artifact, then request explicit bounded T08 human/live
  authorization. Timer design remains a separate successor after T08.

### Checkpoint P0023-C07 | 2026-08-05

Plan version: 1

State transition:

- `exact_candidate_review_pending -> bounded_rework_recheck_pending`.

Independent review result:

- the evaluator verified the exact `7b51c5f` commit and original 0.3.0
  artifact, then returned `FAIL` with two blockers, one high finding, and one
  medium finding;
- typed worker `partial` results were being converted to provider `success`,
  so blocking authentication could falsely terminalize the lane successfully;
- the observation gate returned a cached external URL without asking
  agent-browser for `view_takeover` or retaining a viewer-lease ID;
- media fetching admitted private/non-global destinations and unsafe redirects;
  per-media timeouts also ignored the tick's remaining monotonic wall budget.

Owned rework:

- preserve typed partial provider results, publish their raw evidence first,
  and terminalize the provider attempt/lane as `blocked_human` for exact
  CAPTCHA, Cloudflare, blocked-rate-limit, and reauthentication incidents;
- resolve an acknowledged explicit observation request through the browser's
  `activeSessionIds` and the service session inventory to exactly one ready
  agent-browser stream, post code-owned `view_takeover`, return only the fresh
  external HTTPS route from its successful response, and retain the
  viewer-lease ID in user-scoped database schema 15;
- validate every media destination and redirect as external HTTPS with only
  global resolved addresses, account for each request, and cap its timeout by
  the tick's remaining monotonic wall budget;
- keep the agent-browser service endpoint and all operator particulars in the
  user-scoped tick document. No ordinary acquisition path requests a viewer
  lease.

Validation evidence:

- each review finding recorded a focused RED before its GREEN implementation;
- the combined worker, incident, observation, runner, runtime, migration,
  contract, lifecycle, temporal, and package matrix passes; all Go packages
  pass against generated schema-15 compatibility data;
- the complete repository Python suite exits zero, runtime packaging is
  reproducible, migration 14 to 15 preserves legacy observation rows, and
  `git diff --check` passes;
- no installed runtime, real user config, live source, real notification,
  Guac lease, schedule, timer, remote, or recipient was touched by rework.

Review and loop accounting:

- this is Plan 0023's single allowed consolidated review/rework cycle. The
  same evaluator must recheck the rebuilt exact candidate; no second rework
  cycle is authorized by this checkpoint.

Authority classification:

- `human_gate`; deterministic rework is validated. A local exact candidate
  commit, reproducible artifact, isolated install/rollback proof, and evaluator
  recheck are authorized next. Real installation, user-config readback or
  mutation, live providers, real notifications, Guac observation, recurrence,
  push, tag, publication, release, paid calls, and ceiling increases remain
  closed.

Next action:

- bind the rework into one exact local commit, rebuild and hash the service
  artifact, repeat isolated install/rollback/roll-forward proof, and send that
  exact state to the same evaluator. T08 remains closed until recheck passes.

### Checkpoint P0023-C08 | 2026-08-05

Plan version: 1

State transition:

- `bounded_rework_recheck_pending -> failed_recheck_human_gate`.

Progress classification:

- `regression`; exact comparison with the real agent-browser response contract
  disproved the observation fixture, and deterministic deadline testing found
  that DNS resolution can outlive the media wall budget. The candidate is
  stopped even though one original finding and the isolated lifecycle proof
  are accepted.

Exact candidate evidence:

- implementation commit
  `4f1e642dfcaae8aeff5ff8b475b447a08b67fef5`, evidence commit
  `8f222d94f1ea1566c9567cfb966b46ac2ff506a7`, and service artifact SHA-256
  `8217c994d54cbba2ced9b65261ce3149caff1ed86e4006f75ab0cca1a00ff92b`
  were the evaluator's exact review state;
- `docs/dev/notes/0039-service-0.3.0-candidate-install-rollback-receipt.json`
  proves two byte-identical builds and an isolated 0.2.29 to 0.3.0 upgrade,
  rollback, and roll-forward at schema 15. Read-only postflight leaves the real
  installation unchanged at 0.2.29/schema 12 with 42/42 specs disabled;
- the evaluator confirmed the packaged runtime files are byte-identical to the
  reviewed workspace and ran 70 focused tests successfully. Those results do
  not override the failed contract review.

Independent recheck result:

- terminal `FAIL`; only the typed-partial/raw-first terminal-state finding is
  closed;
- the code correctly resolves the browser's active session and ready stream,
  calls `view_takeover`, and obtains `viewerLeaseId`, but requires an
  `externalUrl` in that action's response. Agent-browser's actual
  `ServiceViewTakeoverData` returns takeover metadata and the lease ID without
  an external route, so the handoff fails closed instead of returning and
  persisting the already-resolved direct route;
- media validation computes remaining wall time before DNS resolution and
  passes that stale value to the opener even when resolution consumes the
  deadline;
- resolved global-address admission and redirect checks reject simple private
  destinations, but the later urllib connection performs a second unpinned
  resolution, leaving DNS rebinding open.

Review and loop accounting:

- C07 consumed Plan 0023 version 1's single authorized consolidated
  review/rework cycle. This failed recheck is terminal for that candidate; no
  second remediation or evaluator loop is authorized under version 1.

Authority classification:

- `human_gate`; T08, installation, user-config readback or mutation, live
  providers, real notifications, Guac observation, recurrence, push, tag,
  publication, release, paid calls, and ceiling increases remain closed. A
  bounded Plan 0023 version 2 successor requires explicit approval because it
  follows failure at the configured review/rework bound.

Next action or stop reason:

- stop candidate 0.3.0. If explicitly approved, open Plan 0023 version 2 with
  one bounded packet owning only actual-contract observation handoff and a
  deadline-aware, destination-pinned media transport, with fresh independent
  review bounds. Do not repair either seam under C07/C08 authority.

### Checkpoint P0023-C09 | 2026-08-05

Plan version: 2

State transition:

- `failed_recheck_human_gate -> v2_observation_media_repair_active`.

Progress classification:

- `blocker_reduction`; the operator explicitly approved Plan 0023 version 2,
  removing the C08 human gate while preserving every live, install, config,
  notification, Guac, recurrence, publication, and cost boundary.

Changed assumptions and bounded outcome:

- agent-browser `view_takeover` is lease authority, not route authority. The
  already-resolved ready stream remains route authority; after takeover the
  bridge must re-read service state and prove the returned viewer lease is
  active and bound to the same browser, session, stream, provider, and route
  before returning or persisting that stream's direct external HTTPS URL;
- media admission and media connection cannot be separate DNS decisions. One
  internal transport must resolve under the tick deadline, reject every
  non-global destination, connect to one admitted address, preserve the
  original hostname for TLS SNI/certificate and `Host`, verify the connected
  peer, recompute remaining time before each blocking phase, and repeat the
  full process for every redirect;
- this packet owns only those two seams and their focused regression tests.
  It does not reopen T08, add a timer, change service/config schemas, install a
  candidate, read or mutate real user config, call a provider, notify a real
  recipient, or acquire a real observation lease.

Owned write surfaces:

- the existing tick runtime modules that implement observation handoff and
  media retrieval, their focused tests/fixtures, and only the contract or
  configuration documentation proven necessary by an observable interface
  change;
- this plan, Roadmap P07, Runbook, and candidate evidence required by policy.

Execution and review bounds:

- one primary implementation packet with at most two implementation attempts;
- vertical TDD: one failing behavior test followed by the minimum passing
  implementation before the next behavior is opened;
- one fresh independent candidate review and at most one consolidated
  review/rework cycle for version 2;
- checkpoint before independent review and on any repeated invariant failure,
  deadline ambiguity, unpinned connection path, route/lease identity mismatch,
  dirty-worktree overlap, or proposed crossing of a closed gate;
- terminal stop after a failed exact recheck, after two implementation
  attempts, or after two consecutive hardening/no-progress checkpoints.

Validation evidence required before candidate review:

- actual-contract takeover fixtures omit external URL data and succeed only
  when a post-takeover service read proves the returned lease against the
  unchanged ready stream and route; missing/mismatched/changed proof fails
  closed and no takeover occurs before acknowledgment plus explicit observe;
- resolver latency can consume the deadline without any connect attempt;
  admitted-address and connected-peer disagreement fails closed; HTTPS keeps
  original-host TLS and `Host` semantics while connecting to the admitted IP;
  redirects repeat resolution/pinning and remain inside the shared request and
  wall budgets;
- focused tests, affected integration/runtime/lifecycle tests, the complete
  Python suite, all Go packages, compile checks, and `git diff --check` pass.

Subagent status and reconciliation:

- no implementation delegation. The primary owns both coupled seams and their
  integration. The existing read-only evaluator may receive only the exact
  committed candidate for the single fresh version-2 review.

Authority classification:

- `inherited_authority`; the operator's explicit `yes` opens this exact local
  repair and validation packet. Installation, real user-config access or
  mutation, live providers, real notifications, Guac observation, recurrence,
  push, tag, publication, release, paid calls, and ceiling increases remain
  `human_gate` actions and are not authorized here.

Next action:

- commit this authority checkpoint, then run the first focused red/green cycle
  for actual-contract observation handoff. Continue with the deadline-pinned
  media cycle only after observation is green.

### Checkpoint P0023-C10 | 2026-08-05

Plan version: 2

State transition:

- `v2_observation_media_repair_active -> v2_contract_verified_implementation_active`.

Progress classification:

- `blocker_reduction`; direct agent-browser source evidence removed one stale
  planning assumption before implementation began.

Authority correction:

- `view_takeover` returns accepted takeover identity, `viewerLeaseId`, viewer
  event metadata, and service-event identity; it does not create a durable
  record in the separate `/api/service/viewer-leases` collection;
- the agent-browser dashboard's external-open path resolves the external URL
  from the retained stream, queues `view_takeover`, requires success, and then
  opens that retained URL. Version 2 will mirror that contract: require the
  response's accepted status, preserved process, non-empty viewer lease, and
  exact browser/session/stream/provider/open-mode identity, then return and
  persist the already-validated retained-stream route;
- the C09 requirement for post-action viewer-lease collection readback is
  retired. No replacement endpoint, durable lease invention, or agent-browser
  repo change is authorized or required.

Validation adjustment:

- the observation regression fixture must use the actual takeover response
  shape with no external URL and must fail closed on any missing lease,
  non-accepted status, unpreserved process, or identity mismatch;
- acknowledgment and explicit-observe ordering remains covered through the
  incident interface, while transport tests prove the retained route is
  resolved before takeover and is the returned URL afterward.

Subagent status and reconciliation:

- `not_spawned`; CodeGraph and agent-browser's own handler/dashboard source
  provided the contract evidence. The independent evaluator remains reserved
  for the exact committed candidate.

Authority classification:

- `inherited_authority`; this correction narrows implementation to the actual
  approved contract and crosses no live, config, install, notification, Guac,
  recurrence, publication, or cost gate.

Next action:

- write the actual-shape observation regression test, prove it fails against
  the C08 implementation, and make only that vertical slice green.

### Checkpoint P0023-C11 | 2026-08-05

Plan version: 2

State transition:

- `v2_contract_verified_implementation_active -> v2_candidate_review_pending`.

Progress classification:

- `blocker_reduction`; both terminal C08 defects now have implementation,
  regression, packaging, and isolated lifecycle evidence at one exact commit.

Candidate implementation:

- exact code commit `6402d16c0ba652ac339c0d75e0994203e930aeae`
  validates the actual agent-browser takeover shape while retaining the
  prevalidated external stream route;
- the same commit introduces a deadline-pinned HTTPS media transport that
  bounds DNS under the one absolute media deadline, admits only globally
  routable resolutions, connects to the admitted socket address, verifies the
  peer, preserves original-host TLS SNI and HTTP `Host`, and applies the same
  checks to every redirect;
- service runtime manifest SHA-256 is
  `58e34738d2e55f0b857bac05aaebb8726f31620365c99038a8234db3c61a8fb3`;
- two clean builds and the repository candidate artifact are byte-identical at
  SHA-256
  `ea91dd5897a2b67911e9b60683ef5896d168ceda045d5e15fdff3d9f2683a8ba`.

Validation and lifecycle evidence:

- focused affected matrix: 55 passed;
- full Python suite: 2,515 passed, 7 skipped, 6 subtests passed;
- all Go packages, compileall, and diff checks passed;
- temporary-XDG lifecycle proof installed synthetic 0.2.29, upgraded to the
  exact candidate, diagnosed ready, rolled back ready, and rolled forward
  ready; schema remained 15 and SQLite integrity was `ok`;
- receipt:
  `docs/dev/notes/0041-service-0.3.0-v2-candidate-install-rollback-receipt.json`.

Closed-gate readback:

- no real installed runtime, user-scoped config, provider, notification,
  Guacamole observation, recurrence, paid call, push, tag, publication, or
  release action was read or changed.

Subagent status and reconciliation:

- the primary completed the two coupled vertical TDD seams and exact candidate
  validation. The existing read-only evaluator is now assigned one fresh
  review of this exact commit, evidence checkpoint, and artifact; only its one
  consolidated rework allowance remains if that review fails.

Authority classification:

- `inherited_authority`; implementation and local validation are inside the
  operator-approved V2 packet. Independent review is required before any
  separately human-gated installation or live T08 request.

Next action:

- commit this evidence checkpoint, then obtain the fresh independent exact-
  candidate review. Stop after its terminal result; do not cross any live,
  install, config, notification, Guac, recurrence, publication, or cost gate.

### Checkpoint P0023-C12 | 2026-08-05

Plan version: 2

State transition:

- `v2_candidate_review_pending -> v2_candidate_accepted_live_gate`.

Progress classification:

- `blocker_reduction`; terminal independent review accepts the repaired local
  candidate and retires both C08 implementation blockers.

Independent review result:

- reviewer `/root/p0023_c06_review` returned terminal `PASS` with no release-
  blocking, high-severity, regression, or consolidated rework finding;
- actual agent-browser request flattening, takeover response identity,
  retained-route use, process/lease proof, and acknowledgement-before-observe
  ordering all passed;
- media deadline, DNS-set admission, address pinning, peer verification,
  original-host SNI/Host, redirect re-admission, malformed-destination stop,
  socket cleanup, and typed degradation checks all passed;
- reviewer validation passed 58 focused Python tests, 4 package tests, all Go
  packages, diff checks, exact package contents, and a clean worktree;
- exact implementation commit:
  `6402d16c0ba652ac339c0d75e0994203e930aeae`;
- exact evidence commit:
  `803b71234b38fb164915c28c204a5a96ef97f836`;
- exact artifact SHA-256:
  `ea91dd5897a2b67911e9b60683ef5896d168ceda045d5e15fdff3d9f2683a8ba`;
- durable review receipt:
  `docs/dev/notes/0042-service-0.3.0-v2-independent-review-receipt.json`.

Ceiling and rework accounting:

- one of one fresh independent reviews used and passed;
- zero of one consolidated rework packets used;
- one of two implementation attempts used;
- no retry, provider, notification, observation, or recurrence budget was
  consumed.

Authority classification:

- `human_gate`; the V2 local repair packet is terminally accepted, but Plan
  0023 remains `OPEN`. Installing the exact reviewed artifact, reading or
  changing real user-scoped service/incident/provider configuration, and
  executing the live manual all-target T08 tick each require a separately
  bounded operator authorization. Guac remains observation-only and on-demand;
  timer or schedule creation remains prohibited until T08 is accepted and a
  separate successor plan is reviewed.

Next action:

- request one separately bounded installation/config/live-T08 authority packet
  for the exact accepted candidate. Do not infer it from this terminal local
  PASS, and do not create or enable recurrence.

### Checkpoint P0023-C13 | 2026-08-05

Plan version: 2

State transition:

- `v2_candidate_accepted_live_gate -> t08_sanitized_preflight_active`.

Progress classification:

- `blocker_reduction`; the requirement-by-requirement completion audit found
  that the live gate still lacks a side-effect-free, sanitized readback of the
  exact frozen config, lane, provider, resource, budget, and notification
  admission data required by the Manual Acceptance Gate.

Bounded local packet:

- add one public `tick preflight` interface using the same interval,
  schedule, config loader, adapter registry, identity derivation, lane
  expansion, and notification adapter machinery as `tick enqueue`;
- return the exact prospective tick/config identity; enabled lane IDs and
  non-sensitive identity digests; provider order, adapter types,
  normalization-proof refs, fallback classes, resource-key digests, and
  limits; aggregate limits; and ordered notification transport IDs, adapter
  types, routing digests, and non-message readiness results;
- never emit target selectors, access-partition values, routing particulars,
  credential refs, artifact paths, observation URLs, recipient values, or
  other operator-specific config content;
- read the config exactly once and perform no database, artifact-store,
  provider-acquisition, notification-send, incident, observation, schedule, or
  timer mutation;
- fail before source work when the config is invalid, an adapter lacks a
  normalization proof, notification configuration is invalid, or no
  configured notification transport passes readiness.

TDD and validation contract:

- first public-interface tracer proves a sanitized ready receipt and fails
  before implementation;
- separate vertical tests prove zero state writes, exact enqueue identity
  parity, secret/operator-particular omission, ordered readiness/fail-closed
  behavior, and CLI argument/output wiring;
- maximum implementation attempts: 2; maximum independent review/rework
  cycles: 1; checkpoint before independent review and before any real config
  readback or installation;
- rebuild and lifecycle proof are required because this changes the exact
  install candidate.

Subagent status and reconciliation:

- `not_spawned`; the primary owns the single deep preflight seam. The existing
  read-only evaluator may review the exact committed successor after primary
  validation; no implementation delegation is authorized.

Authority classification:

- `inherited_authority`; this local deterministic interface directly closes a
  named Manual Acceptance Gate prerequisite and crosses no live, user-config,
  install, provider, notification-send, Guac, recurrence, publication, or cost
  boundary.

Next action:

- commit C13, then run one public-interface RED/GREEN tracer for `tick
  preflight`. Keep the real install/config/live-T08 and every recurrence gate
  closed.

### Checkpoint P0023-C14 | 2026-08-05

Plan version: 2

State transition:

- `t08_sanitized_preflight_active -> t08_preflight_validation_active`.

Progress classification:

- `blocker_reduction`; the public preflight seam is implemented and its first
  RED/GREEN cycles exposed and repaired a previously hidden observation-config
  admission mismatch.

Owned changes:

- add `preflight_tick_runtime` and public `service.py tick preflight` without a
  database option;
- share one pure config-load, config-digest, tick-identity, adapter-admission,
  and lane-expansion path with `enqueue_tick`;
- emit only tick/config identity, lane IDs, config-defined identity digests,
  adapter types, normalization-proof refs, fallback classes, resource-key
  digests, provider/aggregate limits, routing digests, and ordered readiness
  states;
- perform sequential non-message notification readiness, stopping after the
  first ready transport and failing closed when the chain is unavailable;
- admit optional `observation` config through the canonical loader and validate
  its installed adapter plus strict HTTP(S) endpoint before any readiness or
  state work;
- document the preflight workflow and correct the observation handoff text to
  the actual retained-route/takeover-metadata contract.

TDD evidence:

- public tracer failed because `preflight_tick_runtime` did not exist, then
  passed with a sanitized ready manifest and zero database/artifact creation;
- the first observation-bearing config failed because the canonical loader
  rejected `observation` even though runtime assembly and the schema accepted
  it; optional-field admission was separated from required fields and passed;
- CLI parsing failed because `preflight` was not a tick action, then passed
  with interval/config arguments and no database option;
- a sensitive-identifier fixture failed because raw target/provider/transport
  IDs were exposed; those config-defined identities now publish only digests;
- an invalid `file:` observation endpoint incorrectly passed readiness, then
  failed before readiness through shared strict observation validation.

Validation evidence:

- 6/6 focused preflight behaviors pass;
- the combined coordinator/runtime/preflight set passes 33/33;
- the broader tick, runner, incidents, observation, media HTTP, runtime
  package, and lifecycle matrix passed after manifest refresh;
- one complete-suite run reached 100% with one expected authority-audit failure
  because latest Turn 156 lacked the auditor's literal `Decisions And Changes`
  and `Validation Evidence` headings; this Turn 157 supplies those fields, so a
  fresh complete run is required before commit.

Authority classification:

- `inherited_authority`; all work is deterministic repo implementation and
  sanitized documentation under C13. No real install, config, provider,
  notification-send, Guac, recurrence, push, publication, release, or paid
  boundary was crossed.

Next action:

- refresh the exact runtime manifest, run the complete Python and Go suites,
  compile/diff audits, then commit and reproducibly rebuild the changed 0.3.0
  candidate before isolated lifecycle proof and independent review.

### Checkpoint P0023-C15 | 2026-08-05

Plan version: 2

State transition:

- `t08_preflight_validation_active -> t08_preflight_candidate_commit_ready`.

Progress classification:

- `blocker_reduction`; the sanitized preflight prerequisite and the full-suite
  clock-rollback integrity defect are both deterministically closed.

Final local implementation evidence:

- seven preflight tests cover sanitized ready output, no state writes, exact
  enqueue identity parity, CLI shape, sequential fallback, readiness
  exhaustion, stop-after-first-ready, and invalid observation admission;
- a separate RED/GREEN worker regression proves backward wall-clock movement
  cannot produce a self-invalidating `fetched_at < observed_at` receipt;
- the complete repository Python suite passes 2,523 tests with 7 skipped and 6
  subtests passed;
- all Go packages pass;
- full Python compilation, manifest/schema JSON parsing, diff hygiene, the
  plan-authority audit, and the goal-planning audit pass;
- runtime manifest hashes are refreshed for every changed packaged module.

Candidate scope:

- changed runtime files are `service.py`, `service_tick.py`,
  `service_tick_runtime.py`, and `service_acquisition_worker.py`, plus the
  refreshed runtime manifest;
- `CONFIGURATION.md` and focused tests are the only non-policy companion
  surfaces;
- no database migration or service-contract version change is required: the
  preflight is state-free and the observation field already exists in the
  shipped config schema.

Authority classification:

- `inherited_authority`; local implementation and validation are complete.
  Reproducible build, isolated lifecycle proof, evidence checkpoint, and one
  fresh read-only independent review remain inside C13. Real install,
  user-config, providers, notification sends, Guac, recurrence, push,
  publication, release, paid calls, and ceiling changes remain closed.

Next action:

- commit this exact candidate, rebuild twice, prove isolated 0.2.29 upgrade,
  rollback, and roll-forward, then bind hashes/receipts before independent
  review.

### Checkpoint P0023-C16 | 2026-08-05

Plan version: 2

State transition:

- `t08_preflight_candidate_commit_ready -> t08_preflight_independent_review_pending`.

Progress classification:

- `outcome_progress`; the Manual Acceptance Gate now has an exact committed,
  reproducibly packaged, and lifecycle-proven sanitized preflight candidate.

Exact candidate evidence:

- implementation/evidence-base commit:
  `0fa63c06578dc9d1c6b41fc6afd531508c5728f3`;
- two independent clean builds and the repository candidate artifact are
  byte-identical at SHA-256
  `32107a9dd13de7f548f1456cf5a91d7dfe414c3ef63b58129c295bd033b0a9ea`;
- runtime manifest SHA-256 is
  `6dda355222e90df958169022df365973cfb317565954dbded25994984784a5c4`;
- temporary-XDG lifecycle proof installed synthetic 0.2.29, upgraded to exact
  0.3.0, diagnosed ready, rolled back ready, and rolled forward ready while
  preserving schema 15 and SQLite integrity `ok`;
- durable candidate receipt:
  `docs/dev/notes/0043-service-0.3.0-c15-preflight-candidate-receipt.json`.

Review contract:

- one fresh read-only independent review must verify shared preflight/enqueue
  identity, one config read, strict adapter/observation admission, complete
  sanitization, sequential non-message readiness, zero state/provider/send
  effects, clock-rollback receipt integrity, package identity, lifecycle
  evidence, and closed-gate compliance;
- maximum independent review/rework cycles: 1; return one consolidated PASS or
  FAIL result; no implementation delegation or live action is authorized.

Authority classification:

- `inherited_authority`; exact local review is the last C13 action. Real
  install, user-config access/mutation, provider work, notification send, Guac,
  recurrence, push, publication, release, paid calls, and ceiling changes
  remain `human_gate` actions.

Next action:

- commit this evidence checkpoint, then send exact commit/artifact/receipt 0043
  to the existing read-only evaluator. Stop after its terminal result.

### Checkpoint P0023-C17 | 2026-08-05

Plan version: 2

State transition:

- `t08_preflight_independent_review_pending -> t08_preflight_consolidated_rework_active`.

Progress classification:

- `validation_failure`; the independent evaluator returned one terminal FAIL
  containing two reproducible false-ready admission defects.

Terminal review evidence:

- an enabled `ocr_adapter_type` absent from the installed analysis registry
  passed preflight, while the same request failed only after enqueue created a
  database and artifact directory; preflight therefore did not share the
  runner's complete deterministic adapter admission;
- observation endpoints with a nonnumeric port or port 70000 passed preflight
  and invoked notification readiness because the shared URL validator never
  evaluated `parsed.port`;
- exact commit, artifact, manifest, reproducible build, package contents,
  focused/full validation, isolated lifecycle, and all closed authority gates
  otherwise passed review.

Consolidated rework contract:

- validate every enabled OCR and semantic-sidecar adapter against the exact
  installed analysis registry in the state-free path used by preflight and
  runtime assembly;
- reject observation URL control characters, malformed ports, and ports
  outside 1..65535 before notification readiness;
- add regressions proving each rejection performs zero readiness calls and
  creates zero state;
- refresh the manifest, rebuild the exact artifact, regenerate isolated
  lifecycle evidence, and submit only that successor for the single bounded
  re-review authorized by C16;
- no interface expansion, real install, user-config access or mutation,
  provider work, notification send, Guac, recurrence, push, publication,
  release, paid call, or ceiling change is authorized.

Authority classification:

- `inherited_authority`; C16 explicitly allowed one consolidated rework and
  exact re-review. This checkpoint consumes that rework slot and does not
  reopen implementation scope beyond the two terminal findings.

Next action:

- drive both findings RED then GREEN, run the complete candidate validation,
  and bind a fresh exact commit/artifact/lifecycle receipt before the one
  bounded re-review.

### Checkpoint P0023-C18 | 2026-08-05

Plan version: 2

State transition:

- `t08_preflight_consolidated_rework_active -> t08_preflight_rework_validation_active`.

Progress classification:

- `blocker_reduction`; both independently reproduced false-ready paths now
  fail deterministically before readiness or state creation.

TDD and implementation evidence:

- five adversarial cases first failed: enabled uninstalled OCR, enabled
  uninstalled semantic-sidecar, nonnumeric observation port, port 70000, and
  an embedded observation URL control character;
- the runtime now resolves one exact installed analysis registry, validates
  every enabled OCR/semantic-sidecar adapter against it during state-free
  admission, and passes that same registry object to `TickRunner`;
- the shared observation validator rejects C0/DEL control characters and
  evaluates the parsed port, converting malformed/out-of-range authorities
  into `TickConfigError` before notification readiness;
- regressions assert zero readiness calls and absence of database/artifact
  state for every repaired preflight rejection;
- 28 focused preflight/runtime tests, 52 coordinator/runtime/runner tests, and
  the 60-test tick/package/lifecycle matrix pass after manifest refresh.

Authority classification:

- `inherited_authority`; this is the complete C17 implementation packet. Full
  repository validation, exact commit, reproducible build, isolated lifecycle
  evidence, and the one exact re-review remain authorized. All real/live and
  recurrence gates remain closed.

Next action:

- run the complete Python/Go/compile/diff/authority validation, commit the
  exact repair, rebuild twice, and produce a successor lifecycle receipt.

### Checkpoint P0023-C19 | 2026-08-05

Plan version: 2

State transition:

- `t08_preflight_rework_validation_active -> t08_preflight_rework_commit_ready`.

Progress classification:

- `outcome_progress`; the consolidated repair now passes every local
  implementation, package, and authority validation surface.

Complete validation evidence:

- the full repository suite exits zero with 2,535 tests collected: 2,528
  passed and 7 intentionally skipped, with 6 subtests passed;
- all Go packages pass from the `mcp/` module root;
- full Python compilation, runtime-manifest and both shipped schema JSON
  parses, `git diff --check`, the deterministic plan-authority audit, and the
  current goal-plan reconciliation pass;
- the initial root-level `go test ./...` and a guessed schema path were invalid
  validation invocations, not product failures; both were immediately rerun
  from their canonical module/file locations and passed;
- no user-scoped configuration, installed runtime, provider, notification,
  Guac, timer, paid service, or remote state was accessed or changed.

Authority classification:

- `inherited_authority`; the exact local repair is ready to commit. Only
  reproducible build, isolated lifecycle proof, receipt binding, and the one
  bounded re-review remain before returning to the human gate.

Next action:

- commit this exact candidate, rebuild it twice, execute only temporary-XDG
  fake-manager lifecycle proof, and bind a successor receipt before re-review.
