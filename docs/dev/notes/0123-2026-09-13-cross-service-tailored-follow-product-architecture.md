# Cross-Service Tailored Follow Product Architecture

Date: 2026-09-13
Work item: WI-005
Plan: 0082
Repository checkpoint: `d20b82546d45050e0e02774d9780a2ed059b5e7f`
Investigation mode: stable local Git repository, service architecture and mixed
code/docs synthesis, hybrid structure-first retrieval

## Decision

Extend WI-004's purpose-typed `CollectionSpec`; do not introduce a universal
"social account" model or another scheduler. Replace the current globally
permissive surface vocabulary with a provider-owned, versioned capability
registry and a discriminated `FollowTargetV1` envelope. Shared lifecycle,
scheduling, attention, receipt, provenance, and query-filter semantics remain
provider-neutral, while each provider owns its target kinds, stable identity,
validation, resolution, access method, and acquisition route.

The first implementation increment preserves all accepted X identities and
adds provider-free Reddit community/user and YouTube channel tracers. Facebook
and LinkedIn remain truthfully discoverable as unavailable for tailored target
kinds until their stable identifiers and exact acquisition routes are proven.
That is deliberate: a generic search or feed route is not evidence that a
provider-native follow target is supported.

## Current Evidence

- `CollectionSpec` already admits `feed`, `topic`, `poster`, `channel`,
  `account`, and `profile`, but the selector table is global. It can therefore
  accept source/surface combinations that no adapter implements.
- source policy currently declares Facebook, LinkedIn, Reddit, X, and YouTube,
  with provider-specific access methods. Readiness answers whether an access
  method is present, not whether a target kind and operation are supported.
- acquisition routing is provider-specific. Reddit has a distinct feed route
  and otherwise receives flattened query text; YouTube has a yt-dlp adapter;
  X, Facebook, and LinkedIn use authenticated browser access.
- the adapter registry declares source and coarse `collect` capability, but
  not target kinds, operations, cadence limits, resolution requirements, or
  readiness reasons.
- accepted Plan 0011 machinery already owns immutable spec revisions,
  schedules, interval coalescing, cursors/watermarks, coverage/gaps,
  source-health/backoff, budgets, profile leases, and raw publication.
- WI-004 establishes `collection_purpose=tailored_follow`, exact X feed/topic/
  account/list targets, deterministic target identity, append-only archive,
  and immutable collection cause at acquisition/publication.

Graphiti recovered the accepted collection foundation, including feed, topic,
poster, channel, account, and profile surfaces plus durable scheduling and
authenticated profile leases. Current CodeGraph evidence verified the global
selector table, source/access policy, and coarse adapter registry. The graph
memory is advisory; the current repository is authoritative.

## Contract Boundary

`FollowTargetV1` is a discriminated object embedded in a tailored-follow
`CollectionSpec` revision:

- `source`: exact provider identifier;
- `target_kind`: provider-owned kind from the capability registry;
- `canonical_id`: stable provider-native identity when one exists;
- `selector`: the exact typed provider-owned acquisition selector;
- `display_locator`: optional user-facing handle/URL, never identity;
- `resolution_receipt`: optional immutable evidence of a locator-to-ID
  resolution, including method, observed time, and access partition.

The spec's deterministic `follow_target_id` digests source, target kind,
canonical ID, canonical selector, and access partition. Display labels, names,
mutable handles, and URLs never participate when a provider offers a stable
native ID. A target without the stable identity required by its capability is
`unresolved` and cannot be enabled or scheduled.

Target resolution is a separate operation from collection. Accepting an
already stable ID can be provider-free. Resolving a handle or URL through a
live provider requires explicit provider authority and writes an attributable
receipt; it never silently activates the follow.

## Initial Target Matrix

| Source | Target kind | Stable identity | Selector and route posture |
|---|---|---|---|
| X | `topic`, `account`, `list` | query digest, canonical handle, numeric list ID | Preserve the exact WI-004 contract and migrations. |
| Reddit | `community` | case-insensitive subreddit name | Explicit community route; remove one `r/` prefix and validate provider syntax. |
| Reddit | `user` | case-insensitive Reddit username | Explicit user-post route; remove one `u/` prefix and validate provider syntax. |
| YouTube | `channel` | canonical channel ID | Explicit channel uploads route; handle/custom-URL lookup is separate resolution. |
| Facebook | none in v1 | not yet frozen | Report source access readiness separately and tailored targets unavailable. |
| LinkedIn | none in v1 | not yet frozen | Report source access readiness separately and tailored targets unavailable. |

Existing general feeds and generic topic/search collection retain their
current purpose. `poster`, `account`, `profile`, and `channel` are not treated
as interchangeable aliases. Adding a provider-native kind requires a registry
revision, validator, route, fixture corpus, and migration/compatibility proof.

## Capability Discovery

Expose a cache-safe `FollowCapabilityV1` catalog through the existing service
information/collection boundary and its MCP projection. Each row contains:

- source, target kind, contract version, and lifecycle operations;
- identity fields, whether resolution is required, and accepted locator forms;
- acquisition method, authentication class, access-partition requirement, and
  installed/readiness state;
- allowed cadence and collection bounds;
- implementation state: `available`, `unavailable`, or `unsupported`, plus a
  stable reason code and safe remediation hint.

`unsupported` means the product has no contract for the requested kind.
`unavailable` means the contract exists but its exact adapter, authentication,
or installed dependency is not ready. `unauthorized` is an operation outcome,
not a capability claim. Source readiness alone never upgrades a target kind to
available, and absence of credentials is not reported as lack of product
support.

Capabilities are declarations from a closed registry, not executable module
names supplied by configuration. Startup fails closed on duplicate
source/kind registrations or a declared route without its validator. Runtime
responses include the registry digest so clients can detect drift.

## Shared Lifecycle And Scheduling

WI-004 lifecycle semantics apply unchanged: create disabled, immutable
revision updates, pause/resume, tombstone archive, interval/manual trigger
coalescing, preserved history, and no physical deletion. Provider capabilities
may narrow operations and cadence but cannot widen global budgets or bypass
authorization.

The shared scheduler orders already-due work and obtains the required access
partition lease. A provider adapter may impose stricter minimum cadence,
serialization, lookback, or batch limits. Those constraints are validated at
spec creation/update and rechecked before work is issued. Capability drift
pauses new issuance with an attributable reason; it does not rewrite history
or silently change the target.

Pause/resume are shared state transitions. Resume fails closed when the target
is unresolved, archived, unavailable, unauthorized, or no longer admitted by
the current registry. Existing leased work is not killed by pause; its result
retains the frozen revision and cause.

## Provenance, Dedupe, And Retrieval

The typed immutable `collection_context` selected by WI-004 carries the exact
source, target kind, target identity, selector digest, follow ID, spec/run IDs,
purpose, attention, and access partition. Provider adapters receive that
object and must reject a mismatched route rather than reconstructing a target
from generic query text.

Content identity remains source-native. One post observed by a general feed,
Reddit community and user follows, or a YouTube channel and generic query is
stored once per immutable content version while append-only sightings retain
every collection cause. Query filters use exact follow/target/spec IDs inside
the authorized partition; display names are never filters of record.

Receipts distinguish successful zero yield, target unavailable, auth required,
rate limited, unsupported, adapter unavailable, and operator authorization
required. A missing or renamed target is not inferred from zero results.

## Migration And Compatibility

WI-004's X revisions migrate byte-for-byte in identity semantics: their source,
surface, canonical selector, access partition, and `follow_target_id` remain
stable. The new registry maps those exact discriminants to X capabilities.
Legacy general collection specs remain readable and are not reclassified as
tailored follows.

Existing globally accepted but provider-invalid surface combinations are not
activated. They remain readable as legacy revisions, report
`unsupported_legacy_target`, and cannot be enabled or revised except to pause
or archive. Migration is additive, idempotent, and records counts/digests for
preserved, mapped, and quarantined rows.

## Access And Effect Boundary

Provider-free implementation uses temporary databases, fake clocks, fake
registries/adapters, and recorded or synthetic payload fixtures. It may create
disabled specs only in disposable stores. It does not resolve real handles,
open a browser, call a provider, change installed configuration, install a
Skill/service, create or enable an installed follow, start a schedule, or
deploy staging/production.

Live resolution, authentication, canaries, recurring enablement, and provider
onboarding each require separate explicit authority. Fresh isolated runtime
acceptance joins WI-001. GitHub Issues remain disabled until the operator
authorizes tracker activation.

## Vertical Delivery Packets

1. Registry and compatibility tracer: implement the closed capability
   registry, discriminated target envelope, registry digest, X identity
   preservation, legacy quarantine, and fake-adapter tests. No jobs start.
   This packet begins only after WI-004 Packet 1 freezes the base contract.
2. Reddit tracer: add community/user validators and explicit acquisition
   routes, frozen context, lifecycle/receipt/query filters, overlap sightings,
   and provider-free fixtures for success, zero yield, malformed identity,
   unavailable, rate limit, replay, and bounded work.
3. YouTube tracer: add channel-ID validation and explicit uploads routing with
   fixtures for success, empty channel, unavailable channel, malformed ID,
   timeout, replay, and overlap with generic search. No live resolution.
4. Discovery and product closure: expose exact capability/readiness and safe
   lifecycle errors through service CLI/MCP, add cadence constraint tests,
   migration/performance evidence, docs/version metadata, and fresh isolated
   client acceptance. Facebook/LinkedIn remain unavailable unless a later
   reviewed packet supplies exact contracts and fixtures.

Each packet is an end-to-end tracer through its public boundary. Shared
collection contracts, publication, search filters, MCP catalog, migrations,
and release metadata are coordinator-owned integration joins with WI-002,
WI-003, and WI-004.

## Provider-Free Acceptance Boundary

- every advertised target kind has one exact validator, route, operation set,
  cadence range, access rule, and stable readiness reason;
- X follow IDs and immutable revision histories are unchanged by migration;
- legacy invalid combinations remain readable but cannot schedule;
- Reddit community/user and YouTube channel work reaches only its declared
  adapter with frozen bounds and access partition;
- unsupported, unavailable, unresolved, and unauthorized requests fail closed
  and remain distinguishable;
- create/update/pause/resume/archive and interval/manual replay preserve shared
  lifecycle and history semantics across fake adapters;
- one content version can expose several general/follow sightings without
  duplicate content or lost cause;
- service CLI and MCP capability/lifecycle/filter responses agree, and no
  browser, provider, installed runtime, or real schedule is touched.

## Open Questions For The Lane Owner

- Freeze Reddit community/user and YouTube channel fixtures before writing
  parsers or routes.
- Measure migration and 10,000-sighting filter baselines before setting Packet
  4 thresholds.
- Decide through a later reviewed architecture increment which stable native
  identities and privacy rules admit Facebook page/group and LinkedIn
  person/company targets; do not infer them from current browser surfaces.

## Graphiti Write Status

`graphiti_write_pending`: the known ingestion path previously timed out during
node deduplication without an episode UUID. This slice used bounded read-only
discovery and does not queue another write behind the degraded path.

## State Location

This note and its machine-readable companion are durable in the stable Git
repository. No bundle or snapshot is needed.
