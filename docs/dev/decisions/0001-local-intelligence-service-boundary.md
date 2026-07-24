# ADR 0001 | Local intelligence service boundary

Status: ACCEPTED
Date: 2026-07-24
Governing plan: Plan 0007

## Context

The current Agent Skill, direct CLI, and Go MCP package invoke the research
engine inside the client request. The Go MCP server extracts an embedded Python
engine and launches a new subprocess for every `research` tool call. The
optional SQLite store accumulates findings, but it is not the query authority.

This makes every querying agent participate in acquisition mechanics and
prevents reliable cache reuse, request coalescing, replay, semantic retrieval,
and background refresh.

The install surfaces impose real constraints:

- `skills/last30days/` is the recursively copied Agent Skills package boundary;
- the MCPB currently embeds enough Python to remain self-contained and
  advertises Linux and macOS;
- source credentials currently reach the MCP process through its environment;
- project-local `.claude/last30days.env` can currently override the user
  configuration based on the caller's working directory;
- a long-lived user service cannot safely infer one requesting client's
  working-directory configuration or inherit MCP-only environment values;
- the reference Linux user-manager PATH omits user and Linuxbrew binaries used
  by several source adapters.

## Decision

### Product and authority

The user-scoped Python intelligence service is the durable product authority.
The Agent Skill, direct CLI, and Go MCP server are clients of one versioned
service interface.

The service owns:

- content acquisition and browser leases;
- credentials and registered configuration profiles;
- cache freshness and refresh coalescing;
- SQLite migrations and normalized storage;
- lexical, semantic, and graph indexing;
- deterministic ranking and response budgets;
- the job, event, decision, approval, and evaluation ledger.

Clients own transport adaptation and presentation. They do not implement
ranking, acquire browser leases, or receive raw source diagnostics.

### Runtime and package authority

Canonical Python runtime code and JSON Schemas ship inside
`skills/last30days/`. This preserves the existing Agent Skills package boundary
and ensures the direct CLI and service use identical contracts.

The v4 MCPB remains installable without a source checkout. It must package or
materialize the same service runtime and connect to one user-scoped instance.
Starting the service once is allowed; launching a fresh crawl subprocess from a
query handler is not.

The Go binary remains CGO-free and acts as a thin MCP/transport adapter. The
current embedded-engine execution path remains only until the packaged service
bootstrap and migration path pass integration gates, then is removed with the
legacy `research` tool.

Linux systemd user supervision is the primary operator path. A portable managed
daemon bootstrap is required before a service-backed MCPB continues to
advertise macOS. If that bootstrap is not ready for v4, macOS must be removed
from the advertised release platforms rather than shipping a nonfunctional
bundle.

### Local transport

The primary Linux socket is:

```text
$XDG_RUNTIME_DIR/last30days/service.sock
```

The runtime directory is mode `0700` and the socket is mode `0600`. The service
binds only a local Unix-domain socket. A platform transport resolver may select
a comparably private local socket on systems without `XDG_RUNTIME_DIR`.

WebSocket and non-loopback transports are outside this decision. They require a
separate authorization, network, audit, and token-rotation decision.

### Configuration and credentials

The service owns named user-scoped configuration profiles. Query and
acquisition contracts carry a stable `profile_id`, never credential values.

The `default` profile imports the current user-scoped configuration. Additional
profiles may be registered explicitly for different source or budget policies.
Project-local `.claude/last30days.env` is not read implicitly by the daemon.
Clients that need project-specific behavior select a registered profile.

Credential migration from MCPB environment configuration is an explicit
install/bootstrap operation that writes through the service's secure
configuration interface. Credentials, cookies, browser/session IDs, operator
URLs, and lease data never enter query, evidence, event, or decision envelopes.

The service worker environment uses a sanitized, explicitly configured PATH and
reports readiness from that actual environment. It must not claim a CLI-gated
source is active because a binary exists outside the worker PATH.

### Cache and MCP semantics

`prefer_cache` remains the default query freshness policy and may atomically
enqueue or join a background refresh when cached evidence is stale.

Because that behavior creates durable state and can initiate external
acquisition, the MCP `query` tool is conservatively annotated:

- read-only: false;
- destructive: false;
- open-world: true.

`cache_only` guarantees no refresh job or external work. Clients that require a
statically read-only action can select it explicitly.

MCP exposes exactly five primary tools:

- `service_info`;
- `query`;
- `refresh`;
- `job_status`;
- `topic`.

Long-running service jobs use durable job IDs. Experimental MCP Tasks may adapt
to those jobs when negotiated by the client, but they are not the service
authority.

### Persistence and schema

SQLite in WAL mode remains the MVP authority. Schema version 3 introduces
versioned service envelopes, job/event/acquisition tables, normalized
documents/chunks/embeddings, typed entity and relationship projections, index
versions, decisions, and evaluations.

Migrations:

- reject databases created by newer runtimes;
- acquire a write lock and recheck the current version;
- execute each version atomically;
- record the version only after its schema succeeds;
- preserve existing topics, runs, findings, sightings, and FTS behavior.

The canonical v1 JSON Schema catalog is
`skills/last30days/schemas/service-contracts-v1.json`. Transport adapters must
generate from it or verify against it; they must not maintain an independent
semantic copy.

### Deterministic and stochastic control

The host service alone transitions job state, spends budgets, acquires leases,
publishes index versions, accepts decisions, or requests approval.

Stochastic workers return versioned proposals. Their model reference, input and
output artifact references, evidence IDs, confidence, validator result, and
acceptance decision are persisted. A stochastic failure cannot make cached
deterministic evidence unavailable.

Codex app-server is reserved for persistent maintenance and repair workflows.
Structured leaf extraction may use the Responses API. Neither integration may
self-deploy or directly mutate supervisor control state.

## Consequences

Positive:

- ordinary agents learn a small intelligence interface rather than scraper and
  browser mechanics;
- warm queries avoid network and browser work;
- all clients share cache, provenance, ranking, and readiness truth;
- acquisition and enrichment become replayable and budgeted;
- the current Python engine and SQLite investment remain useful.

Costs:

- service lifecycle and cross-platform bootstrap become release-critical;
- MCPB credential migration needs an operator-safe path;
- the Go and Python contracts require a generated or hash-gated compatibility
  check;
- project-local configuration no longer changes daemon behavior implicitly;
- release validation must cover Python, Go, socket lifecycle, packaging, and
  installed-client behavior.

## Rejected Alternatives

### Keep request-scoped crawls behind MCP

Rejected because it preserves context leakage, duplicate browser work, and no
durable query authority.

### Make the Go MCP server the content service

Rejected because it would duplicate the Python normalization/ranking engine,
move SQLite/vector behavior into a CGO-constrained package, and create two
authorities.

### Require PostgreSQL, pgvector, and a graph database in the MVP

Rejected because the measured local corpus does not yet justify three durable
infrastructure dependencies. Storage adapters remain possible after benchmark
evidence.

### Mark `query` read-only while it schedules refresh

Rejected because MCP annotations are static and must describe real behavior.

### Let the daemon read arbitrary client working-directory configuration

Rejected because a shared process cannot safely infer which client owns that
directory or secret context. Named registered profiles make the authority
explicit.

