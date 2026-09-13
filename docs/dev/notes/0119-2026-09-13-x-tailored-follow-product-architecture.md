# X Tailored Follow Product Architecture

Date: 2026-09-13
Work item: WI-004
Plan: 0078
Repository checkpoint: `16562fefc9b7f0f2c776a51ed727cd73a898ae66`
Investigation mode: stable local Git repository, service architecture and mixed
code/docs synthesis, hybrid structure-first retrieval

## Decision

Treat an X tailored follow as a specialized, versioned `CollectionSpec`, not as
a second scheduler. Evolve the collection contract with an explicit
`collection_purpose` (`general` or `tailored_follow`), an `attention_class`
(`standard` or `priority`), typed X selectors, and an append-only lifecycle.

The existing coordinator remains authoritative for cadence, lookback, budgets,
cursors, immutable revisions, interval coalescing, profile leases, coverage,
gaps, source health, assessment, and retries. The acquisition boundary gains a
typed collection target and exact collection-cause identity so adapters never
have to infer account, list, topic, or feed semantics from flattened query
text.

The existing service CLI and MCP `collection` tool are the first operator and
agent surfaces. This lane tightens those contracts rather than adding a second
top-level follow API. The richer question-answering surface remains WI-003.

## Current Evidence

- `CollectionSpec` already stores immutable revisions with a surface-specific
  selector, profile/access partition, interval, lookback, item/network/time/
  cost bounds, retention/redaction, assessment, and enabled state.
- `CollectionCoordinator` derives stable interval runs, coalesces timer and
  manual triggers, blocks another active run for the same spec, persists
  cursor/watermark state, and freezes the exact spec revision used by a job.
- the X worker routes only `feed` to `scrape_x_feed`; every other surface is
  flattened to `request.query` and sent to generic `search_x_browser`. There
  is no X list route, and `AcquisitionWorkRequest` has `surface_kind` but no
  typed selector or target identity.
- publication deduplicates documents by canonical URL or source-native ID and
  records append-only `document_version_sightings`, including collection spec
  and run IDs. The publisher currently recovers one collection cause by a
  `job_id` lookup with `LIMIT 1` instead of receiving the frozen cause in the
  work contract.
- lifecycle operations are put, list, pause, resume, and manual run. There is
  no get-by-ID operation or history-preserving delete/archive operation.
- X has only the authenticated Agent Browser access method. Existing profile
  leases are therefore the serialization boundary even when several follows
  become due at once.

Graphiti discovery recovered the accepted collection architecture from Plan
0011: immutable specs and revisions, durable schedules, frozen run identity,
raw publication before assessment, host-enforced budgets, cursor/watermark,
coverage/gap, source-health/backoff, and authenticated profile leases. Current
CodeGraph and source evidence verified these seams and exposed the typed-target
and collection-cause gaps.

## Product Contract

`CollectionSpec` remains the durable execution contract. Its next compatible
revision adds:

- `collection_purpose`: `general` or `tailored_follow`;
- `attention_class`: `standard` or `priority`;
- `lifecycle_state`: `active` or `archived`, distinct from the schedulable
  `enabled` flag;
- a typed, canonical selector for the declared source and surface.

Migration assigns existing rows `general`, `standard`, and `active`. Existing
serialized revisions remain readable through explicit defaulting, while every
new revision serializes all three fields. Unknown values fail closed.

For X v1, the canonical target matrix is:

| Surface | Exact selector | Canonicalization | Adapter route |
|---|---|---|---|
| `feed` | `{"feed":"home"}` | exact literal | existing authenticated home feed |
| `topic` | `{"topic":"<query>"}` | trim and collapse whitespace; retain case and operators | existing dated X search |
| `account` | `{"account":"<handle>"}` | remove one leading `@`, ASCII case-fold, validate 1-15 letters/digits/underscore | authenticated account Posts timeline |
| `list` | `{"list_id":"<numeric-id>"}` | decimal string without signs or leading whitespace | authenticated `x.com/i/lists/<id>` timeline |

Noncanonical input is rejected with the canonical candidate in a safe
validation response; it is not silently rewritten inside digest computation.
Display labels and URLs are derived metadata, never target identity. A list
name or account display name cannot identify a follow.

`follow_target_id` is a deterministic digest of source, surface kind,
canonical selector, and access partition. At most one non-archived tailored
follow for that identity may exist in a partition. Operators revise the
existing spec rather than creating duplicate scheduled collection. The
general feed has a different purpose and target identity and remains an
independent collection.

## Attention Semantics

“Separate attention” is inspectable rather than an opaque recommendation:

- cadence and lookback control when and how far the follow collects;
- item, wall-time, network, and cost limits bound one run;
- `attention_class=priority` breaks ties among already-due work after the
  oldest due time, without preempting an active profile lease;
- collection spec/run IDs, selector digest, target ID, and purpose identify
  why each observation exists;
- coverage, gaps, source health, retry-after, and last-run receipt expose
  freshness and failure state.

Cadence remains the primary attention control. Priority does not bypass
budgets, rate-limit backoff, authentication gates, profile serialization, or
the no-overlap rule, and it cannot starve an older due run.

## Typed Acquisition Boundary

Extend `AcquisitionWorkRequest` with an optional immutable
`collection_context` containing:

- collection spec ID and frozen spec version;
- collection run ID and purpose;
- surface kind, typed canonical selector, selector digest, and target ID;
- attention class and access partition ID.

Non-collection jobs omit the object. The host validates that its source,
profile, partition, selector, and frozen revision agree before subprocess
execution. X dispatch is then explicit:

- feed -> `scrape_x_feed`;
- topic -> `search_x_browser`;
- account -> a new `scrape_x_account` route;
- list -> a new `scrape_x_list` route.

Account collection navigates the canonical account Posts timeline and accepts
only candidates with structurally verified post ownership by that handle.
List collection navigates the canonical list-ID timeline and accepts posts
from that rendered list surface; membership is not inferred or persisted as a
claim. Both routes reuse the existing authentication, workspace, bounded
scroll, quality, and cleanup primitives. A generic search success must never
be reported as account or list support.

The acquisition envelope and publication path copy the exact frozen
collection cause from the work request. Publication no longer selects an
arbitrary cause by `job_id`. One document/version remains deduplicated by its
native identity, while separate acquisitions create separate sightings, so a
post can truthfully retain several follow/general-feed collection causes.

## Lifecycle And Failure Semantics

- create: a new tailored follow is persisted disabled unless a caller
  separately and explicitly requests enablement through an effect-authorized
  surface;
- get/list: return current spec, immutable revision locator, schedule/run
  health, and target identity within the caller's access partition;
- update: requires exactly `current_version + 1`; identity-changing edits are
  rejected and require a new follow;
- pause: writes a disabled revision and prevents new timer work; existing
  leased work is not killed;
- resume: writes an enabled revision only for an active target and schedules
  from the service-owned next-due rule;
- retry/manual run: uses existing interval identity and trigger coalescing;
  it cannot create concurrent duplicate collection;
- delete: is a tombstone operation that writes `archived` plus `enabled=false`;
  specs, revisions, runs, sightings, coverage, and gaps remain queryable.
  Archived follows cannot resume, update, or run and are hidden from default
  lists unless `include_archived` is explicit. Physical deletion is not a v1
  operation.

`auth_required` and checkpoint states remain awaiting-operator outcomes;
`rate_limited` remains retryable only under existing bounded backoff; a
structurally verified missing, suspended, or unavailable target returns a
permanent `target_unavailable` outcome for that run but does not silently
archive the follow. Empty valid timelines remain successful zero-yield runs
and are distinguishable from target failure.

## Access And Effect Boundary

X follows always use an authenticated access partition tied to the named
profile. Target IDs and collection history never cross that partition. The
MCP collection tool and service application recheck caller-visible partitions
for every read or mutation.

Provider-free implementation uses temporary databases, fake clocks, synthetic
worker results, and recorded/synthetic DOM fixtures only. Creating or enabling
a follow in an installed database, starting a recurring schedule, using a real
profile, opening X, retrying an authenticated job, installing a Skill or
service, or deploying staging/production remains separately authorized. Live
X canaries are serialized through one profile and are not part of provider-
free acceptance.

## Vertical Delivery Packets

1. Contract tracer: add compatible collection-purpose, attention, lifecycle,
   canonical X account/list selectors, target identity, inactive-by-default
   creation rules, migration, get/list/archive semantics, and provider-free
   persistence tests. No job or browser starts.
2. Typed account tracer: propagate immutable collection context through the
   work/acquisition/publication path, route account work explicitly, publish
   multi-cause sightings, and test account success, malformed identity,
   unavailable target, auth-required, rate-limit, replay, and general-feed
   separation with fixtures.
3. Typed list tracer: add the list-ID browser route and synthetic DOM fixtures,
   including list-page mismatch, empty list, unavailable/private target,
   bounded scrolling, replay, and account/list overlap. No live profile.
4. Product and scheduler closure: expose the tightened lifecycle through the
   existing CLI and MCP collection tool, add attention ordering with aging,
   collection-filter integration for WI-002, capability/readiness reporting,
   docs, full presubmit, and a separately proposed live canary.

Each packet must be end-to-end through its public boundary and must leave the
installed service untouched. The lane owner coordinates shared contract and
publication files with WI-002 and leaves richer answer synthesis to WI-003.

## Expected Write Surfaces

- collection models/coordinator, service contracts, job runner, acquisition
  worker, publication, migration, service application/CLI, and focused tests;
- X browser code and fixtures only in Packets 2-3;
- Go MCP tool schemas/tests and generated service contracts when the public
  collection contract changes;
- `CONFIGURATION.md`, Skill/runtime docs, changelog/version metadata, roadmap,
  runbook, plan, work-item, and active-lane custody as required by the shipped
  surface.

Before editing shared contracts, publication, or search-filter code, the lane
owner must rebase on current `origin/main`, run CodeGraph impact, and reconcile
ownership with active WI-002/WI-003 lanes through the coordinator.

## Provider-Free Acceptance Boundary

- legacy specs migrate without identity drift and new specs round-trip every
  explicit field and immutable revision;
- malformed/noncanonical account and list selectors, public X partitions,
  duplicate active targets, archived mutations, and identity-changing updates
  fail closed;
- feed, topic, account, and list work reach only their declared adapters with
  exact frozen context, limits, and profile partition;
- account/list fixtures cover success, zero yield, target unavailable,
  authentication, rate limit, bounded timeout/network work, and idempotent
  replay;
- one native post observed by general feed, account, and list is stored once
  per content version and exposes all three collection sightings;
- interval and manual triggers coalesce, no same-spec concurrent job appears,
  profile leases serialize X work, and priority cannot bypass an older due
  run or backoff;
- pause/resume/update/delete preserve immutable history, and archived content
  remains filterable by exact follow ID inside the authorized partition;
- CLI and MCP responses agree on lifecycle, target, cause, readiness, and safe
  errors; no provider/browser/install/runtime mutation occurs.

## Open Questions For The Lane Owner

- Freeze the exact account/list synthetic DOM corpus before implementing the
  parser, so selector changes cannot make the tests self-fulfilling.
- Measure the current migration and 10,000-sighting collection-filter baseline
  before choosing performance thresholds for Packet 4.
- Confirm whether account Posts timelines expose a stable unavailable-versus-
  empty distinction in fixtures; if not, preserve `target_state=unknown`
  rather than inventing certainty.

## Graphiti Write Status

`graphiti_write_pending`: the prior exact architecture-write retry failed in
node deduplication with a retryable transport timeout and no episode UUID.
This slice does not queue another write behind that degraded ingestion path.
The intended compact episode is this decision, its integrated commit, tests,
current state, and Packet 1 handoff.

## State Location

This note and its machine-readable companion are durable in the stable Git
repository. No bundle or snapshot is needed.
