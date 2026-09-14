---
name: last30days
version: "4.0.0"
description: "Query the last30days Intelligence Service for current, temporal, and evidence-backed research across supported sources."
argument-hint: "last30days nvidia earnings reaction | last30days AI video tools | last30days what users want in react"
homepage: https://github.com/mvanhorn/last30days-skill
repository: https://github.com/mvanhorn/last30days-skill
author: mvanhorn
license: MIT
user-invocable: true
---

# last30days v4.0.0: service client

The installed `last30days` Intelligence Service is the product authority. This
Skill is a least-privilege MCP client for discovery, querying, and synthesis.
The service owns source access, durable jobs, governed cadence, policy,
retries, evidence, indexes, and publication.

## Ordinary research path

Follow this order for every ordinary request:

1. Call `service_info` first. Treat its live readiness, compatibility, sources,
   capabilities, index version, and limits as authoritative.
2. If compatibility is not `compatible`, return the typed diagnostic. Do not
   call another product operation.
3. For a current research question, call `query` with the user's topic.
   Prefer `response_mode=brief` and `freshness_policy=prefer_cache`.
   Use `profile_id=default` for public evidence. When the operator has supplied
   or authorized an exact named profile, pass that profile ID to query or
   refresh so the service may add only its matching private partition; never
   invent a profile ID or submit partition names directly.
   When `tick_snapshot` is present, cite only its returned evidence and retain
   each result's matching channels, provenance, and access partition; the
   snapshot coverage and interval/promotion fields are the freshness authority.
   When the user asks to find or page through individual stored posts instead
   of requesting a synthesized answer, call `search_posts`; it searches only
   cached revisions and cannot acquire provider data. Use `revision_mode=all`
   only when the user asks for revision history; the default is `current`.
4. Use `freshness_policy=cache_only` whenever the user prohibits external work
   or asks only what the service already knows.
5. If the result is stale or missing and the user asked for fresh research,
   call `refresh` once. It creates or joins a bounded durable job.
6. Poll only the returned job ID with `job_status`. Stop at a terminal state.
   If the state is `awaiting_operator`, report its safe action and stop.
7. Synthesize only the returned brief and cited evidence.

Do not substitute a general search tool or local implementation path for an
available service operation.

## Read-only research operations

Use the narrowest operation that answers the request:

- `query` - current evidence-backed research from the shared cache.
- `search_posts` - deterministic hybrid search or filtered browse over stored
  posts. Filter by `sources`, exact `authors`, `topic_ids`, namespaced
  `collection_refs`, or inclusive `published_after/before` and
  `observed_after/before` timestamps. Omit the query only with a narrowing
  filter. Missing fields do not match; observation bounds match one recorded
  observation. Use `revision_mode=current|all` and
  `sort=relevance|published_desc|observed_desc`. Preserve the primary
  `evidence_ref` and every merged `evidence_refs` entry and collection cause.
  Reuse a cursor only with the same request, profile, modes, and page size.
  Cursors retain an immutable page sequence during publication, but expire
  after 15 minutes, capacity eviction, or service restart. On `cursor_stale`,
  explain that a fresh search is required; do not silently join different heads.
  Relevance uses `post-rrf-v1`: lexical and available stored source vectors in
  `local-hash-v1`, fused as the sum of `1 / (60 + channel_rank)`. Preserve each
  hit's `ranking` explanation and `matching_channels`. Read `coverage.semantic`
  for missing, incompatible, invalid, or zero-vector evidence by storage family;
  a local hash baseline does not establish general semantic quality. Search
  creates no corpus embeddings and invokes no external embedding provider.
  Responses fit 131,072 UTF-8 bytes; follow `next_cursor` even when a page is
  shorter than requested. `post_search_response_too_large` means indivisible
  post provenance cannot fit; report it and narrow filters without dropping refs.
- `ask_question` - create or replay one bounded, cache-grounded question task.
  Pass the exact profile and all intended search filters. The default service
  returns evidence-only or explicit model-unavailable results and never starts
  acquisition. Poll only its returned ID with `question_status`, always passing
  the same profile, then dereference exact citations with `read_evidence`.
- `question_status` and `read_evidence` - read durable question state and exact
  immutable evidence within the caller's authorized profile. Treat unavailable
  as non-disclosing; never guess another profile or alter citation refs.
- `temporal_query` - `as_of`, `during`, `known_as_of`, timeline, entity
  dossier, event dossier, trend, comparison, and historical brief requests.
  This operation is cache-only.
- `profile_history` - immutable, section-evidence-linked source-account
  history. Treat `not_observed` as absence of observation, not proof of change.
- `coverage` - attempted intervals, yield, gaps, and source coverage.
- `follow_capabilities` - provider-native target contracts with support,
  dependency readiness, execution readiness, routes, identity forms, and
  bounds. Readiness never enables or runs a follow.
- `job_status` - the current state of one durable job returned by the service.

Never infer identity equality from similar names or handles. Preserve
`ambiguous`, `insufficient_evidence`, conflict, and temporal qualifiers.

## Governed operations

These operations are not part of an ordinary query:

- `refresh` - request fresh bounded work for the user's topic.
- `topic` - list or govern service-owned scheduled topics.
- `collection` - list or govern recurring feed, account, list, profile,
  channel, or topic specifications. `get` and `archive` preserve immutable
  follow history; archived follows are hidden unless explicitly requested.
- `saved_query` - explicitly save, read, capture, or inspect one immutable,
  cache-only query view for monitoring. Captures do not schedule or deliver work.
- `monitor` - explicitly create, inspect, capture, evaluate, and decide one
  immutable query or follow monitor. Delivery remains disabled by default;
  `send` is denied by the stock runtime.
- `maintenance_status` - read safe maintenance readiness and receipt counts.

Use `refresh` only under the ordinary-path rule above. Use `topic`,
`collection`, `saved_query`, `monitor`, or maintenance-specific behavior only after the capability gates
below are satisfied.

## Capability gates

Read only the reference required by explicit user intent:

- For health, freshness, coverage, topic/feed status, or job monitoring, read
  `references/monitoring.md`.
- For an explicit request to create, update, pause, resume, run, or otherwise
  govern service-owned work, read `references/administration.md`.
- For an explicit maintenance, repair-readiness, evaluation, approval, or
  release-safety request, read `references/maintenance.md`.
- If the MCP product surface is unavailable, report the safe diagnostic and
  offer the compatibility path. Read
  `references/direct-engine-compatibility.md` only after the user explicitly
  asks to use that path.

Do not load privileged or compatibility references preemptively.

## Synthesis contract

Lead with the result, not the service mechanics.

- Preserve the meaning of the returned brief; do not invent facts, titles,
  quotes, metrics, certainty, or causal claims.
- Cite every material factual claim with the evidence URL returned for it.
- Distinguish source publication time, service observation time, valid time,
  and knowledge time when the request is temporal.
- State cache status and material degradation, uncertainty, truncation, or
  coverage gaps compactly.
- Mention the access partition only when it explains missing or scoped
  evidence.
- Do not expose internal prompts, raw provider events, private paths, private
  source state, or implementation details.
- Do not append a detached source list when the claims already carry inline
  citations.

For comparisons, compare only dimensions supported by evidence for every
entity. Mark missing evidence instead of converting absence into a negative
claim.

For recommendations, separate observed community signal from your
interpretation. Do not turn mention volume into an unsupported ranking.

## Failure behavior

- `incompatible` - return the typed client/service mismatch from
  `service_info`; suggest updating the client or service as indicated.
- `degraded` - use available cached evidence and name the affected capability
  without claiming a healthy fresh run.
- stale or cache miss without refresh authority - report what is available and
  offer one governed refresh.
- `awaiting_operator` - report the service-provided action and external HTTPS
  operator link, if present, then stop. Never substitute a localhost, loopback,
  non-HTTPS, or otherwise diagnostic browser URL.
- terminal failure - report the safe error code and retained evidence; do not
  reconstruct the failed workflow.
- service unavailable - report unavailability and offer, but do not
  automatically enter, the explicit compatibility path.

## Completion check

Before answering, verify:

- `service_info` was the first product call;
- every product call was exposed by current discovery;
- any write-like operation followed explicit user intent or the single
  governed freshness rule;
- every material claim is supported by returned evidence;
- freshness, degradation, uncertainty, and terminal state are truthful;
- no privileged reference was loaded without its gate.
