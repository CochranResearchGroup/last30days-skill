# Saved Monitor And Digest Product Architecture

Date: 2026-09-13
Work item: WI-006
Plan: 0083
Repository checkpoint: `8d3c50a2`
Investigation mode: stable local Git repository, service architecture and mixed
code/docs synthesis, hybrid structure-first retrieval

## Decision

Make a saved monitor a durable, versioned cache-view subscription, not a hidden
scraper. `MonitorSpecV1` references an immutable WI-002 saved-query version or
an immutable WI-004 follow-view version, evaluates only committed service
evidence at a frozen retrieval/index head, and advances from one explicitly
accepted baseline to another. A monitor run can prepare a digest; delivery is a
separate durable effect intent that is disabled by default.

Use the service-owned task/schedule and receipt patterns, but do not reuse the
legacy `watchlist.py` storage or couple digests to the incident schema. The
legacy watchlist reruns research and sends webhooks opportunistically; it lacks
immutable evidence heads, access partitions, durable delivery intents, and
accepted-baseline semantics required here.

## Current Evidence

- WI-002 selects immutable search snapshots and stable evidence references;
  WI-004 selects immutable follow identity and collection-cause filtering.
- `LocalServiceRetriever.search_snapshot` already returns evidence with the
  exact index version read in one transaction.
- tick query snapshots preserve promoted/superseded heads and source coverage.
- document versions and collection sightings can distinguish stable content
  identity from revisions and acquisition causes.
- the incident subsystem has durable transition-aware notification receipts
  and idempotency keys, while Slack Receipts and GWS email transports expose
  readiness and receipt references.
- legacy `watchlist.py` stores topics/findings, recomputes deltas by URL, reruns
  acquisition, and sends a configured webhook directly. Delivery failure does
  not fail the run and successful sends are not durable service evidence.

Graphiti recovered a prior idempotent Slack Receipts notification chain, but
that is advisory evidence of a transport pattern, not authority to send a
digest. Current CodeGraph/source evidence verified the retrieval snapshot,
tick head, document history, legacy watchlist, incident delivery, and transport
seams.

## Monitor Contract

`MonitorSpecV1` is immutable by revision and contains:

- monitor ID, name, version, lifecycle state, enabled flag, and access
  partition;
- `view_ref`, a discriminated reference to an exact saved-query version or
  follow-view version;
- cadence, comparison policy, maximum digest items/characters, and retention;
- delivery preference as a disabled-by-default channel reference and mode,
  never embedded credentials;
- created/updated actor and timestamps.

Create persists a disabled monitor. Updates require `current_version + 1`.
Changing the view identity creates a new monitor; pause, resume, and tombstone
archive preserve every run, baseline, digest, and delivery receipt. Resume
requires the referenced view to remain readable in the caller's partition and
the selected delivery channel, if any, to remain only configured—not invoked.

The monitor scheduler is local/cache-only. It may run on cadence or when a new
eligible index/view head appears, with interval coalescing and one active run
per monitor. It cannot request refresh, start a collection, open a browser, or
call a source provider. Stale or partial evidence produces an explicit
coverage verdict rather than widening acquisition.

## Frozen Run And Baseline

Each `MonitorRunV1` freezes the monitor revision, view revision, access
partition, prior accepted baseline ID, selected index/query/follow head,
knowledge cutoff, coverage window, source coverage, and comparator version.
Replay of the same tuple returns the same run/digest identity.

A completed run produces a candidate baseline. The baseline cursor advances
only when the digest is explicitly accepted (or an operator accepts a
no-change run). A failed render, rejected digest, or failed delivery never
advances it. This makes retries compare against the same evidence boundary and
prevents loss caused by an attempted notification.

First run is `baseline_only` by default: it records the initial evidence set
without announcing every historical item as new. An explicit bounded
`include_initial` option may prepare an initial digest but does not send it.

## Change Semantics

Comparison operates on stable evidence/document identity and immutable content
version, not rank or snippet text:

- `new`: identity absent from the accepted baseline and present now;
- `revised`: same identity with a new immutable content version;
- `removed`: an explicit tombstone/unavailable event, or absence from a
  provider-complete enumerable follow view under a declared removal policy;
- `unchanged`: same identity and version in both comparable sets;
- `ranking_changed`: optional non-content observation kept separate from the
  four evidence states.

Absence from top-k search results never proves removal. Partial/stale coverage,
changed query semantics, incomparable access partitions, unavailable heads,
or missing history yields `comparison_incomplete` and cannot emit a removal.
Every count exposes its denominator and coverage verdict.

## Digest Contract

`DigestV1` is an immutable projection of one monitor run. It records the prior
and current baseline/head locators, coverage window, counts by change class,
omissions/truncation, comparator and renderer versions, and bounded entries.
Every entry carries exact WI-002 evidence references plus document/version and
follow/collection cause where applicable.

Packet 1 uses a deterministic renderer: heading, counts, coverage warning, and
evidence-linked entries. No language-model claim is required. Later optional
synthesis may join WI-003, but its statements must pass the same citation and
coverage rules and failure falls back to the deterministic digest.

Digest preparation and acceptance are local state transitions. Reading a
digest is side-effect free. An accepted digest remains immutable even if a
later evidence version changes the story.

## Delivery Boundary

`DigestDeliveryIntentV1` is separate from the digest and includes monitor,
digest, channel-config version, explicit authorization receipt, mode, and an
idempotency key derived from those fields. A channel adapter returns a durable
attempt/success/failure receipt. Retrying a failed attempt reuses the exact key;
a successful key returns its prior receipt and cannot redeliver.

An operator-requested resend creates a new intent with a reason and parent
delivery receipt. It does not mutate or masquerade as the original delivery.
Channel readiness is capability evidence only. Configuration, validation,
preparation, acceptance, and send are distinct operations and authority gates.

Reuse the closed transport-registry/readiness/receipt pattern from incident
notifications, not incident transitions or incident message schemas. Initial
fixture adapters are sink/recording transports. Slack Receipts, email, webhook,
or any other live channel requires its own work item, allowlisted destination,
current authority, and post-send readback.

## Access, Privacy, And Retention

The monitor, both compared views, digest, evidence references, and channel
configuration must share an authorized access partition. A caller cannot use a
monitor to test existence across partitions. Responses redact unavailable
evidence rather than leaking counts or identifiers.

Archiving a source view pauses dependent monitors but preserves history.
Retention may expire rendered bodies while retaining hashes, counts, evidence
locators, coverage, acceptance, and delivery receipts required for audit.

## Migration And Legacy Watchlists

Do not silently adopt legacy watchlists. Provide a provider-free importer that
maps a legacy topic to a disabled draft saved query plus disabled monitor,
records the original topic ID/query/schedule, and reports anything that cannot
map. Legacy webhook configuration is never copied into an enabled delivery
intent. Import is idempotent and leaves legacy data readable until a separate
deprecation/removal plan is accepted.

## Vertical Delivery Packets

1. Monitor kernel: after WI-002 Packet 1, add immutable specs/runs/baselines,
   fake saved-view providers, deterministic comparison, baseline acceptance,
   lifecycle, migration, and replay tests. Delivery remains disabled.
2. Query monitor tracer: bind exact WI-002 query versions and evidence refs;
   test new/revised/unchanged, top-k absence, partial coverage, cutoff,
   truncation, and access partitions through CLI/MCP.
3. Follow monitor tracer: after WI-004 Packet 1, bind exact follow targets and
   collection sightings; test multi-cause overlap, explicit unavailable/
   tombstone removal, pause/archive propagation, and cross-source fixtures.
4. Digest and delivery closure: deterministic digest rendering, acceptance,
   delivery intents, sink transport, retry/resend idempotency, legacy import,
   capability discovery, docs, performance evidence, and fresh isolated-client
   acceptance. Live channel adapters remain separately gated.

Shared search/follow contracts, MCP catalog, migrations, notification registry,
and release metadata are coordinator-owned integration joins. Packet 1 can
start after WI-002 Packet 1; Packet 3 and final acceptance also require WI-004
Packet 1/closeout. Optional synthesized summaries join WI-003 later.

## Provider-Free Acceptance Boundary

- identical frozen inputs replay to one monitor run and digest;
- only explicit acceptance advances the baseline cursor;
- new/revised/removed/unchanged states use stable identity/version evidence and
  incomplete coverage never creates a false removal;
- deterministic digests bind every entry to exact authorized evidence and
  report windows, denominators, gaps, and truncation;
- successful delivery keys cannot redeliver, failed attempts reuse the same
  key, and explicit resend creates a child intent;
- archived/unreadable views pause safely and partition mismatches disclose
  nothing;
- legacy import creates disabled drafts and never copies a live webhook;
- fixtures make no network, provider, browser, installed runtime, schedule, or
  external-channel mutation.

## Graphiti Write Status

`graphiti_write_pending`: prior ingestion timed out during node deduplication
without an episode UUID. This slice used bounded reads and queues no duplicate
write.

## State Location

This note and its machine-readable companion are durable in Git.
