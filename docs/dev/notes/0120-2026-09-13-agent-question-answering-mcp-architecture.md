# Agent Question Answering MCP Architecture

Date: 2026-09-13
Work item: WI-003
Plan: 0079
Repository checkpoint: `4687a07465b16e634644f4a0419ca1632cfe4969`
Investigation mode: stable local Git repository, agent-facing service
architecture and mixed code/docs synthesis, hybrid structure-first retrieval

## Decision

Add a cache-grounded, durable question workflow that composes WI-002's
post-search contract rather than extending legacy `/v1/query` or treating the
current `temporal_query` result as a generated answer.

The product surface is four small MCP tools:

- `search_posts`, owned by WI-002, for paginated cache-only discovery;
- `ask_question` to freeze a question, filters, search heads, selected evidence,
  access scope, answer policy, and bounded stochastic attempt;
- `question_status` to poll a durable question that exceeds one MCP call's wait
  budget;
- `read_evidence` to dereference exact citations into immutable, bounded source
  records.

The corresponding service seams are additive `POST /v1/questions`,
`GET /v1/questions/<question_id>`, and `POST /v1/evidence/read`. Existing
`/v1/query` and `/v1/intelligence` behavior remains compatible.

A deterministic host owns retrieval, access control, evidence selection,
prompt construction, limits, idempotency, validation, persistence, and
receipts. A separate question-answer worker may synthesize only from the
supplied immutable evidence, under a strict output schema and with no browser,
source acquisition, tools, or corpus mutation. Model unavailability never
widening into provider refresh is a normal, inspectable outcome.

## Current Evidence

- the installed service is active at version `0.3.116`, database schema 17,
  with 167 indexed documents and local-hash embeddings across five sources;
- the Go MCP adapter currently registers ten tools, including `query`,
  `temporal_query`, `profile_history`, `coverage`, and `collection`, but no
  post-search, question, question-status, or evidence-read tool;
- `CacheQueryApplication.query` can enqueue refresh unless `cache_only` is
  selected. Its `brief` mode concatenates bounded evidence snippets; it does
  not synthesize or validate an answer and always returns `next_cursor: null`;
- `TemporalKnowledgeQuery.query` returns claims, events, conflicts, evidence,
  and corpus retrieval. Its claim/event SQL is partition/time filtered but is
  not relevance-filtered by `query_text`, so those records cannot be injected
  wholesale into a question answer;
- `EvidenceItem` is citation-ready but snippet-oriented. There is no public
  operation that dereferences its evidence ID to an exact immutable version;
- existing App Intelligence proves the useful execution pattern: immutable
  evidence references, access-partition closure, bounded limits, a structured
  no-browse worker, host-computed output digest, validation receipts, and
  durable task state. Its proposal-shaped task/result contracts are not an
  answer contract and must not be overloaded.

Graphiti discovery recovered the established rule that immutable temporal
evidence and access partitions precede stochastic App Intelligence, and that
the deterministic host supervises bounded model leaves. Current CodeGraph,
source, and live read-only service evidence verified that rule and exposed the
missing answer and citation-read boundaries.

## Dependency Contract With WI-002

WI-003 consumes, but does not redefine, these WI-002 outputs:

- strict `PostSearchRequest` filters, revision mode, sorting, pagination, and
  response budgets;
- one federated `PostSearchBackend` across legacy and tick storage;
- immutable `search_head_id` plus component-head receipts;
- stable post, revision, evidence/provenance, author, collection, topic, and
  observation identifiers;
- filter-before-ranking access enforcement and opaque cursor validation.

Packet 1 of this lane may begin only after WI-002 Packet 1 integrates the
contract and backend seam. Later filter/citation work may proceed in parallel
against coordinated interfaces, but WI-003 acceptance waits for WI-002's
search/MCP closeout. The coordinator owns conflict resolution for shared
contracts, service HTTP/application files, generated catalogs, and Go MCP tool
registration.

## Question Request Contract

`QuestionRequestV1` contains:

- schema version, caller-supplied request ID, authorized profile ID, and a
  non-empty question bounded to 4,096 characters;
- the exact WI-002 filters: sources, authors, namespaced collection refs, topic
  IDs, published range, and observed range;
- optional temporal intent: `as_of`, `during_from`/`during_to`, and
  `known_as_of`, with strict range validation;
- `answer_mode`: `synthesized` or `evidence_only`;
- `model_fallback`: `none` or explicit `evidence_only`;
- evidence limit 1-50, maximum evidence-input bytes, maximum answer characters,
  maximum statement count, and bounded `wait_ms`;
- optional maximum evidence age. An unmet age bound is reported as stale and
  never causes acquisition.

Unknown fields fail closed. `request_id` is immutable: replay with a different
payload is a conflict. The host normalizes only fields governed by the search
contract and computes a request fingerprint before retrieval.

The retrieval phase pins the exact `search_head_id`, component heads, request
fingerprint, selected result order, revision/content digests, coverage, and
authorized partition digest. `question_id` is derived from that frozen
retrieval receipt plus answer policy. A changed search head, filter, evidence
selection, worker policy, or model configuration creates a different question
task rather than silently reusing an older answer.

## Evidence Selection And Temporal Context

Raw immutable posts from `PostSearchBackend` are the primary answer evidence.
The host retrieves within a fixed candidate/page ceiling and persists the
ordered selected references before model work.

Structured temporal claims, events, and conflicts may be attached only when:

- their access partition is authorized;
- every supporting evidence ID resolves through the selected search result set
  or an explicitly recorded secondary search page;
- their valid/system time intersects the request's temporal scope;
- their source version and digest still match.

This prevents the current non-relevance-filtered temporal tables from flooding
an answer. Structured records supplement source posts; they do not replace
them or become citations without their underlying evidence.

Coverage is part of the frozen input. It records requested and represented
sources, unavailable fields, collection/topic gaps, truncation, component
heads, newest/oldest evidence times, and requested freshness. The answer may
be generated from partial or stale evidence only when the response labels that
state; it may not present partial coverage as complete.

## Answer Contract

`QuestionAnswerV1` is immutable and contains:

- question ID, request fingerprint, search head and worker/policy/model
  identities, generated time, and exact input/output digests;
- `answer_state`: `answered`, `no_evidence`, `insufficient_evidence`,
  `conflicting_evidence`, `model_unavailable`, `failed`, or `pending`;
- a bounded answer summary;
- ordered statements with stable statement ID, text, `statement_kind`,
  `support_state`, and one or more exact citation refs;
- uncertainty codes, explicit alternatives where evidence conflicts, and the
  frozen coverage/freshness receipt;
- model invocation state, attempt count, latency, safe error code, and whether
  an explicit evidence-only fallback was used;
- a `cache_only: true` acquisition receipt and `acquisition_performed: false`.

`statement_kind` is one of `source_fact`, `temporal_inference`, or
`analytical_inference`. `support_state` is `supported`, `mixed`, or
`insufficient`. Every substantive statement in an answered result has at
least one citation from the frozen selected set. A mixed statement must cite
at least two distinct evidence refs and expose the alternatives. Inferences
must be labeled; model output cannot promote an inference into a source fact.

Zero selected evidence yields `no_evidence` without invoking a model. Missing
required coverage or citations yields `insufficient_evidence`. Known
contradictory records cannot be collapsed into a single supported statement;
the result is `conflicting_evidence` or contains mixed statements. A prose
answer without schema-valid statements is rejected.

The deterministic validator proves schema, limits, correlation, input/output
digests, citation closure, partition closure, immutable revision/content
digests, statement/citation counts, and required uncertainty labels. It cannot
prove semantic entailment alone; WI-008 owns calibrated grounding evaluation.
Provider-free adversarial fixtures still reject unknown citations, changed
digests, uncited assertions, mislabeled inference, and omitted conflict sides.

## Evidence Read Contract

`read_evidence` accepts 1-20 exact citation refs, the caller's authorized
profile ID, and a response-byte bound. It returns the immutable revision named
by each reference, including source/native identity, canonical URL, author,
title, bounded source text, published/observed/fetched and valid/system times,
content/span digests, collection/topic causes, media metadata when authorized,
and provenance.

Citation refs are namespaced by storage family and immutable identity; they
are not bearer tokens and carry no access authority. Missing, expired, and
unauthorized refs all return the same `unavailable` status so existence cannot
leak across partitions. A ref never drifts to the current revision. Response
truncation occurs only at item boundaries and reports omitted refs.

## Durable Execution And MCP Semantics

Question requests, retrieval receipts, worker attempts, validated answers, and
failure receipts are append-only SQLite records. One exact pending/terminal
task is reused idempotently; an abandoned lease can be recovered through the
existing generation-based worker pattern. Automatic retry is limited to one
transient worker failure. Validation, policy, unavailable-model, or evidence-
drift failures are terminal until a new explicit request creates a new task.

`ask_question` waits only within its declared `wait_ms`, then returns a
terminal answer or `pending` plus `question_id`. `question_status` is read-only
and never starts or retries work. The MCP client timeout must exceed the
service wait budget but remain below the worker hard wall.

MCP annotations remain truthful:

- `search_posts`, `question_status`, and `read_evidence` are read-only and
  closed-world;
- `ask_question` is not read-only because it persists a task and may invoke a
  configured model; it is marked open-world even though corpus acquisition is
  prohibited;
- model and acquisition effects are reported separately in every response.

## Model Boundary And Prompt-Injection Safety

The question worker is a new narrow contract over the existing structured-turn
transport, not a reuse of `IntelligenceProposal`. It receives only a canonical
JSON input artifact containing the question, selected evidence, coverage, and
allowed citation IDs. Source text is delimited and treated as untrusted data.
The worker has no tools, browser, shell, repository mutation, retrieval, or
provider-source access. Its only allowed action is `answer_from_evidence`.

The host supplies an explicit output schema, validates returned JSON, computes
the output digest, and persists the raw validated answer before projection.
No model name is hard-coded by architecture. Service capabilities expose
whether synthesis is configured, and every answer records the actual worker
and model identity when the runtime reports them. Model prompts, outputs, and
errors must not expose credentials or evidence from another partition.

## Vertical Delivery Packets

1. Contract tracer: after WI-002 Packet 1, add strict question/request/answer,
   citation-read, retrieval-receipt, attempt, and status contracts; migrations;
   deterministic IDs; queue/lease/idempotency; and provider-free tests with a
   fake PostSearchBackend and fake worker. No model or server process starts.
2. Evidence tracer: compose the real PostSearchBackend, freeze selected
   evidence and coverage, add immutable evidence dereference, and prove source,
   author, collection, topic, time, revision, access, pagination, and response-
   budget behavior across both storage families.
3. Answer tracer: add the no-tool structured question worker, validator,
   durable async execution, explicit fallback, stale/partial/conflict/no-
   evidence states, and adversarial provider-free fixtures for unsupported and
   prompt-injection-shaped source text.
4. Agent surface and closeout: expose the three new service routes and MCP
   tools alongside `search_posts`; update Skill guidance, capabilities,
   compatibility/version artifacts and docs; run full presubmit; and prove one
   fresh MCP client round trip on an isolated provider-free runtime. A real
   model canary, staging, install, and production remain separate gates.

## Expected Write Surfaces

- question contracts, queue/ledger/worker/validator modules, migrations, and
  focused tests;
- WI-002 search backend and evidence-ref interface only through the agreed
  shared contract;
- service application/HTTP/client and Go MCP tool schema/handlers/tests;
- generated service-contract catalogs/digests, capabilities and compatibility
  manifests when public contracts change;
- `SKILL.md`, configuration documentation only for actual knobs, changelog and
  version metadata when shipped, plan, roadmap, runbook, work-item, and lane
  custody.

The lane owner must rebase on current `origin/main`, run CodeGraph impact, and
coordinate all shared contract, service application/HTTP, generated catalog,
and MCP registration edits with active WI-002/WI-004 owners.

## Provider-Free Acceptance Boundary

- exact request replay reuses one task; changed payload or changed pinned heads
  cannot reuse it;
- all filters and temporal bounds flow through the stable post-search contract,
  and selected evidence is frozen before worker execution;
- every answer statement closes over authorized immutable citations with exact
  digests; cross-partition, changed, missing, uncited, or fabricated refs fail;
- contradictory, stale, partial, empty, truncated, worker-unavailable,
  transient-failure, terminal-validation, and idempotent-recovery fixtures have
  distinct truthful outcomes;
- evidence-only mode never invokes a model, and synthesized mode never invokes
  a source adapter, browser, refresh, follow, schedule, or notification;
- prompt-injection-shaped evidence remains inert data and cannot widen worker
  actions or output schema;
- `search_posts`, `ask_question`, `question_status`, and `read_evidence` have
  compact discoverable MCP schemas and HTTP/MCP parity;
- a fresh client can search, ask, poll if needed, follow every citation, and
  reproduce the answer's evidence receipt on an isolated provider-free runtime;
- no test touches a real model, provider, browser, credential, installed Skill,
  schedule, staging, or production service.

## Open Questions For The Lane Owner

- Measure question prompt construction and fake-worker round-trip latency before
  freezing `wait_ms`, input-byte, and answer-size defaults.
- Freeze a provider-free evaluation corpus with supported, contradictory,
  stale, partial, no-evidence, revision, and prompt-injection cases before
  implementing the answer validator.
- Decide immutable evidence-retention behavior with WI-002 before promising how
  long old citation refs remain dereferenceable.

## Graphiti Write Status

`graphiti_write_pending`: Plans 0076-0078 already await recovery of the
degraded ingestion path after a retryable node-deduplication transport timeout
with no episode UUID. This slice does not queue another write. Its intended
episode is this decision, integrated commit, validation, dependency state, and
Packet 1 gate.

## Skill Friction

The shared `codebase-investigator` skill references two optional shared example
files that remain absent from the installed skill tree. All required core
references were available; the missing examples did not limit this
investigation.

## State Location

This note and its machine-readable companion are durable in the stable Git
repository. No bundle or snapshot is needed.
