# Plan 0008 | Content-service hydration readiness

State: CLOSED
Roadmap: P00
Date: 2026-07-25
Predecessor: Plan 0007

## Execution State

Plan version: 1
Critical-path owner: primary agent
Execution branch: `main`
Optimization posture: one thin production vertical slice with read-only audit
sidecars

Local goal bounds:

- maximum implementation attempts per packet: 2;
- maximum review/rework cycles: 1;
- maximum consecutive hardening-only checkpoints: 1;
- checkpoint after contract implementation, installed-runtime validation, and
  live hydration;
- authenticated acquisition remains fail-closed and may not perform login,
  checkpoint, CAPTCHA, credential, or profile mutation;
- completion requires database readback, not only process health or job state.

## Objective

Close the gap between Plan 0007's product contract and the installed content
service by preserving media-bearing source metadata, publishing the semantic
and graph projections that already exist, registering the thin MCP for normal
agent discovery, and hydrating one real post from each configured source.

The requested live source set is Reddit, X, YouTube, Facebook, and LinkedIn.
Each source attempt is limited to one requested result. A source is counted as
hydrated only when its document, provenance, and available photo/video
references survive acquisition, publication, active-index projection, and a
cache-only readback.

## Current Evidence

- the user service is live against
  `~/.local/share/last30days/research.db`, schema version 6;
- 27 active documents exist: Reddit 19, X 7, YouTube 1, Facebook 0, LinkedIn
  0;
- the active index reports zero embeddings and relationships even though
  historical index projections contain embeddings;
- acquired items already carry sanitized JSON metadata, but the document
  projection and evidence contract discard it;
- the Go MCP implements the intended five-tool surface, but Codex has no
  user-scoped `last30days` MCP registration;
- Facebook and LinkedIn share the authenticated `last30days-facebook`
  agent-browser profile, while X uses its own authenticated profile.

## Packets

### Packet 1 | Durable media/provenance projection

- add an additive database migration for sanitized source metadata and
  normalized media assets;
- retain acquired-item metadata during insert and update;
- expose bounded photo/video metadata in citation-ready evidence without
  leaking browser/session/auth mechanics;
- update the canonical schema and focused contract, migration, publication,
  retrieval, and response-budget tests.

Exit gate: a media-bearing acquisition result round-trips through SQLite and a
cache-only query with stable source/provenance fields and bounded media assets.

### Packet 2 | Installed semantic, graph, and MCP readiness

- run the local deterministic embedding/entity loop and publish a fresh active
  index;
- verify semantic and entity-graph scoring from the active index;
- build/install the thin MCP and register it at user scope;
- restart the installed service so current source-profile configuration and
  code are authoritative.

Exit gate: live service info reports a non-zero active embedding projection,
graph-backed retrieval has a current proof case, and a fresh MCP client
discovers exactly the five intended tools and can query the daemon.

### Packet 3 | Bounded five-source hydration

- request exactly one post from each configured source in separate durable
  refresh jobs;
- poll every job to a terminal state;
- preserve photos and videos when the returned post exposes them;
- never synthesize unavailable media or claim readiness from authentication
  alone.

Exit gate: every yielding source has one newly observed document with an
acquisition envelope, sighting, active-index membership, and cache-only
readback. Any non-yielding source has a terminal, safe, source-attributed
failure receipt.

### Packet 4 | Database and product acceptance

- audit active counts for documents, chunks, embeddings, entities,
  relationships, source yield, media assets, sightings, and acquisitions;
- run lexical, semantic, graph/entity, provenance, media, freshness, restart,
  and MCP readbacks;
- run focused and full repository validation;
- reconcile audit sidecars, close this plan truthfully, create structured
  commits, push the public fork, and verify local, remote, installed, and live
  state separately.

Exit gate: the installed service demonstrates the product behavior described
by Plan 0007 without exposing scraper/browser mechanics to querying agents.

## Acceptance Criteria

- one real post is attempted from each of Reddit, X, YouTube, Facebook, and
  LinkedIn with an item limit of one;
- available image/video references are durable and returned as bounded media
  assets;
- all returned evidence is citation-ready and includes source-native identity,
  URL, content hash, acquisition ID, fetched time, and published time when
  supplied;
- the active index contains deterministic embeddings and entity projections;
- at least one live query demonstrates non-zero semantic contribution and at
  least one demonstrates non-zero graph/entity contribution when corpus
  evidence supports it;
- cache-only readbacks cause no acquisition work;
- user-scoped MCP discovery and query work against the installed daemon;
- source health, authentication readiness, acquisition yield, and database
  publication are reported independently;
- focused tests and the full Python and Go suites pass;
- the work is committed in reviewable structure and pushed to `origin/main`.

## Delegation Decision

Policy 0021 makes bounded delegation appropriate for three disjoint read-only
audits while the primary agent owns all edits and integration:

- `/root/packet2_retrieval`: MCP publication and runtime registration audit;
- `/root/packet3_pipeline_audit`: media-inclusive acquisition-path audit;
- `/root/packet3_supervisor_store`: active semantic/graph publication audit.

No sidecar owns files or may mutate runtime state. Their findings are advisory
until independently reconciled by the primary agent.

## Checkpoints

### Checkpoint P0008-C00 | 2026-07-25

Plan version: 1

State transition: `planned -> active`

Progress classification: `outcome_progress`

Owned changes:

- created this successor rather than rewriting the closed Plan 0007;
- converted current live discrepancies into four bounded packets and explicit
  database-backed acceptance gates;
- retained authenticated browser work as a fail-closed supervised operation.

Validation evidence:

- current service, database, source counts, active-index counts, and MCP
  registration were read directly from installed/runtime authorities;
- CodeGraph traced acquisition metadata into `AcquiredItem` and confirmed that
  `CorpusPublisher.record_result` currently drops it before retrieval.

Subagent status and reconciliation:

- three read-only audits are running;
- all implementation and final evidence remain owned by the primary agent.

Remaining acceptance criteria:

- all Packet 1 through Packet 4 gates.

Next action:

- implement and test the additive media/provenance projection.

### Checkpoint P0008-C01 | 2026-07-25

Plan version: 1

State transition: `packet_1_active -> packet_1_complete`

Progress classification: `outcome_progress`

Owned changes:

- added database schema version 7 with sanitized source metadata, bounded media
  JSON, and an explicit active-index head;
- preserved photo/video descriptors from the five configured adapter families
  through normalized worker results, document publication, and evidence;
- fixed immutable-index reactivation so republishing an existing semantic
  snapshot moves the active head without mutating the snapshot;
- added evidence-gated deterministic relationship extraction and a bounded
  enrichment `run_once` seam;
- made browser-source readiness depend on the agent subprocess PATH and explicit
  user-scoped source enablement.

Validation evidence:

- each tracer test failed for the missing behavior before implementation and
  passed afterward;
- 11 focused service/source modules passed together, including migrations,
  contracts, publication, retrieval, enrichment, runtime, worker, Facebook,
  LinkedIn, X, and YouTube.

Subagent status and reconciliation:

- the MCP audit confirmed the five-tool server works but is absent from Codex
  user configuration and existing binaries are stale;
- the media audit confirmed all five source adapters previously dropped
  attachments before query evidence;
- the semantic/graph audit identified stale active-head selection and the
  absent relationship-production path; both findings are addressed in the
  current implementation.

Remaining acceptance criteria:

- installed service and MCP publication;
- one bounded live hydration attempt per source;
- live database/query readbacks, full validation, commits, push, and closeout.

Next action:

- add the durable Codex MCP install surface, sync the installed Skill, restart,
  and verify the active semantic/graph projection before live acquisition.

### Checkpoint P0008-C02 | 2026-07-25

Plan version: 1

State transition: `packet_1_complete -> packet_2_complete`

Progress classification: `outcome_progress`

Owned changes:

- added a deterministic user-scoped Codex MCP installer and registered
  `last30days` against the Unix socket;
- made the systemd unit load the user-scoped service environment file;
- synced the Skill, restarted the user service, and published an active hybrid
  index from the live database.

Validation evidence:

- a fresh MCP initialization returned protocol `2025-03-26` and exactly the
  five intended tools;
- live service status reported 28 documents, 28 local-hash embeddings, five
  accepted relationships, and the semantic and graph capabilities;
- query `TigrimOSR` returned a graph score of `1.0`; normal evidence queries
  returned non-zero semantic scores.

Source-authority correction:

- agent-browser retained only `last30days-facebook` and
  `stealthcdp-default`; no X-authenticated profile survived reboot;
- the X target map had been overwritten to `last30days-facebook`, which is
  authenticated only for Facebook and LinkedIn. X therefore remains an
  operator/auth-profile gate rather than a healthy authenticated source.

Remaining acceptance criteria:

- complete bounded source attempts, database/query readbacks, final validation,
  commits, push, and closeout.

Next action:

- run and read back one-result refresh jobs for every configured source.

### Checkpoint P0008-C03 | 2026-07-25

Plan version: 1

State transition: `packet_2_complete -> packet_3_complete`

Progress classification: `outcome_progress`

Hydration receipts:

- Reddit job `a11a75f4-6817-48d4-a34d-a267512ddf84` published one document;
- YouTube job `426ba8dc-da31-404a-b6a9-7c413303e914` published one video after
  the bounded flat-metadata repair;
- X job `5b3d7274-332f-43cb-b3a4-c9cd9aea03d1` stopped
  `awaiting_operator/auth_required`, accurately reflecting the missing
  post-reboot X profile;
- Facebook job `3fd026a3-843f-494d-a15e-ab9985829799` exhausted two bounded
  attempts with `worker_timeout`;
- LinkedIn job `30ae8f2b-e04c-4516-9f7d-6dd99baf79b9` exhausted two bounded
  attempts with `quality_gate_failed`.

Database readback:

- the Reddit acquisition has one durable document and full provenance;
- the YouTube acquisition has one durable document plus a normalized video
  asset with watch URL, thumbnail preview, duration, and alt text;
- X, Facebook, and LinkedIn have durable safe failure acquisitions and no
  synthesized documents or media;
- a cache-only YouTube read returned the media-bearing evidence with no new
  job, and the active index advanced to
  `index-6916a0495c1c170b8b8caabb`.

Remaining acceptance criteria:

- final full-suite validation, MCP readback from the final commit, structured
  commits, push, installed/live commit-bound proof, and plan closeout.

Next action:

- complete Packet 4 and close the plan truthfully.

### Checkpoint P0008-C04 | 2026-07-25

Plan version: 1

State transition: `packet_3_complete -> closed`

Progress classification: `outcome_progress`

Final acceptance:

- schema versions 1 through 7 are applied and the active database contains 28
  documents, 28 embeddings, five accepted relationships, and one media-bearing
  document;
- cache-only readback returned the hydrated YouTube evidence without enqueuing
  a job, including source-native ID, URL, content hash, acquisition ID, fetched
  time, video URL, thumbnail, duration, and semantic score;
- graph query `TigrimOSR` returned a graph contribution of `1.0`;
- the final installed MCP initialized successfully, discovered exactly
  `job_status`, `query`, `refresh`, `service_info`, and `topic`, and returned
  both live service info and media-bearing cached evidence;
- the full Python suite passed, and `go generate ./...`, `go test ./...`, Go
  vet, and `git diff --check` passed;
- the Skill and systemd service were reinstalled, the live daemon is active,
  and the Codex MCP registration points to the durable user-scoped binary.

Truthful residual state:

- X still requires restoration or reseeding of its distinct authenticated
  post-reboot profile;
- Facebook remains acquisition-unhealthy because its bounded worker attempts
  time out despite verified profile authentication;
- LinkedIn authentication is verified, but this query produced candidates
  that did not pass the content/date quality gate;
- these source failures are durable, source-attributed receipts and did not
  create fabricated documents or media.

Closeout decision:

- the content database and query service meet the MVP storage, semantic,
  graph, provenance, media, cache, and MCP acceptance gates;
- source hydration readiness is partial: Reddit and YouTube yielded new
  documents, while X, Facebook, and LinkedIn require follow-up adapter/profile
  work before five-source yield can be claimed.

Recommended next action:

- repair the Facebook worker timeout and restore the dedicated X profile, then
  rerun one-result hydration for X, Facebook, and LinkedIn without expanding
  the content-service contract.
