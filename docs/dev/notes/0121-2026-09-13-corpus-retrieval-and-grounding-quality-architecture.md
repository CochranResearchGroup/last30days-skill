# Corpus, Retrieval, And Grounding Quality Architecture

Date: 2026-09-13
Work item: WI-008
Plan: 0080
Repository checkpoint: `aa7db9085fb54415c70bdad51c7f9aa821fb6e61`
Investigation mode: stable local Git repository, quality-system architecture
and mixed code/docs synthesis, hybrid structure-first retrieval

## Decision

Build one versioned, replayable quality harness with four explicitly separate
axes:

1. acquisition coverage;
2. corpus integrity;
3. retrieval quality;
4. answer grounding.

The harness compares a frozen candidate against a named baseline and emits a
machine-readable `QualityEvaluationReportV1`, a concise Markdown projection,
and an exit classification. It never combines the four axes into an opaque
single score. Every metric carries its numerator, denominator, excluded cases,
threshold identity, and applicable evidence head.

Provider-free fixture evaluation is the blocking presubmit authority. Optional
model judging and production-bound samples are separate, explicitly labeled
observation lanes; neither can silently change thresholds, promote a model,
delete data, refresh a source, or certify production quality.

The initial product is a repo-only maintainer command under
`dev/last30days/scripts/`, because it compares code revisions and sealed
fixtures and must not ship inside the Agent Skill. A later read-only service or
MCP `quality_status` projection is allowed only after durable evaluation runs
exist and an agent-facing consumer need is demonstrated. It is not part of
Packet 1.

## Current Evidence

- the installed service remains active and ready at `0.3.116`, database schema
  17, with immutable index head `index-e51e8df608f7374bd1d89b9b`, 167 documents,
  167 embeddings, and five represented sources;
- `service_eval.run_retrieval_eval` is deterministic and provider-free, but its
  case schema contains only query, expected document IDs, lane, sources,
  top-k, and latency. Its report aggregates precision, recall, graph precision,
  latency, cost, and lane hits without case-level failure evidence, fixture or
  threshold identity, filter semantics, nDCG, revisions, or provenance checks;
- `dev/last30days/scripts/evaluate_search_quality.py` compares the slash-command
  engine across revisions and computes P@5, nDCG@5, source coverage, Jaccard,
  and retention. Its stable key can fall back to URL/title, its default topics
  are time-sensitive, and uncached judgments may call Gemini. It is useful
  historical machinery, not a sealed provider-free service-quality authority;
- acquisition coverage is stored by normalized query, profile, and source, and
  service publication exposes corpus/index counts, but neither is a complete
  denominator-aware quality report;
- immutable temporal evidence refs and content-addressed index versions provide
  the right replay coordinates for integrity and retrieval cases;
- structured App Intelligence can return evidence-linked retrieval judgments,
  but those are bounded proposals. They cannot set thresholds or replace a
  deterministic evaluator;
- WI-002 defines the stable post-search head, filters, revisions, and ranking
  explanations; WI-003 assigns calibrated grounding evaluation to WI-008.

Graphiti discovery recovered the current immutable-revision rule and older
coverage/relevance history. Current CodeGraph and source evidence verified the
active seams and exposed the contract gaps above.

## Quality Run Contract

`QualityEvaluationRequestV1` contains:

- schema version, caller-supplied run ID, evaluation-set ID and digest;
- candidate repository commit and optional baseline commit;
- evaluator and threshold-policy versions;
- requested axes and named case subsets;
- exact provider-free execution mode by default;
- maximum cases, wall time, output bytes, and per-case retrieval limit;
- optional read-only database snapshot path and declared environment class:
  `fixture`, `development`, `staging`, or `production_sample`.

Unknown fields fail closed. A run ID is immutable: replay with a different
canonical request is a conflict. The runner resolves commits before execution,
uses detached temporary worktrees only when comparison requires them, and
records cleanup outcomes. It never force-removes an unrecognized worktree.

The candidate and baseline receipts pin:

- Git commit, dirty-state rejection, Python and evaluator versions;
- service contract and database schema versions;
- evaluation-set and threshold-policy digests;
- search/index head plus component heads where applicable;
- embedding/ranking configuration identities;
- database snapshot digest and environment classification when used;
- optional judge policy, worker, model, prompt, and output digests.

## Evaluation-Set Contract

`QualityEvaluationSetV1` is a reviewed JSON document under
`fixtures/service_quality/`. Each set has a stable ID, version, description,
source licenses/synthetic status, created/reviewed dates, case IDs, axis tags,
and a canonical digest. Fixture content is synthetic or redistribution-safe
and contains no credentials, cookies, private profile data, or copied live
payloads.

Cases name their denominator explicitly. Expected identities use stable
document, revision, evidence, source, author, collection, topic, and statement
refs from the fixture manifest—never URL/title fallback. Cases may declare
positive, negative, ambiguous, stale, conflicting, missing-field, duplicate,
revision, access-partition, and abstention expectations.

Set changes require review and a version/digest change. Candidate code cannot
rewrite its own expected results or threshold policy during a run. A failing
case remains in the report with its exact inputs and bounded observed output.

## Axis 1: Acquisition Coverage

Coverage is measured against declared expected opportunities, not merely
documents that happened to exist. Metrics include:

- scheduled/eligible intervals observed;
- attempted, succeeded, partial, auth-required, rate-limited, timed-out, and
  failed source runs;
- requested, observed, accepted, published, and indexed item yield;
- publication lag and freshness-window compliance;
- missing receipt fields and unknown/unavailable denominators.

The report groups by source, collection/follow cause, target kind, and interval
where those dimensions are present. `unavailable` is not counted as success,
and an unknown expected denominator is reported as `not_measurable`, never
100 percent. Fixture runs use sealed acquisition/coverage receipts. A
production sample is read-only, time-bounded, separately authorized, and may
support only the claims its sampled denominator proves.

## Axis 2: Corpus Integrity

Integrity checks operate over one frozen database/index head and include:

- document, revision, chunk, evidence-span, acquisition, publication, and
  access-partition referential closure;
- content/version/span digest reproducibility;
- identical acquisition reuse and changed-content new-revision behavior;
- current-head uniqueness and revision/system-time monotonicity;
- canonical identity collisions and exact duplicate rate;
- collection/topic/author/source provenance completeness without fabricating
  unavailable fields;
- orphan embeddings, invalid vector metadata, stale component-head references,
  and cross-partition leakage.

Counts always report checked rows and excluded rows. The evaluator is
read-only: it must not repair, delete, compact, reindex, or promote a head.
Repair suggestions are findings, not actions.

## Axis 3: Retrieval Quality

WI-002's `PostSearchBackend` and exact public request/response contract are the
only candidate retrieval seam. Cases exercise lexical, semantic, fused,
filter-only browse, source, author, collection, topic, published/observed time,
revision, access, empty, malformed, and pagination behavior.

Metrics include case-level and macro/micro:

- precision@k, recall@k, nDCG@k, reciprocal rank, and zero-result rate;
- filter precision/recall and unauthorized-result count;
- duplicate result rate, stable-page replay, cursor integrity, and revision
  correctness;
- provenance completeness and ranking-explanation closure;
- p50/p95 latency, response bytes, candidate count, and declared cost.

Relevance grades are frozen in the evaluation set. Provider-free blocking
runs do not infer labels from candidate output. Optional human/model judgments
are annotation proposals saved separately with judge identity and uncertainty;
they enter a blocking set only through reviewed fixture versioning.

## Axis 4: Answer Grounding

Grounding evaluation consumes WI-003's immutable `QuestionAnswerV1`, frozen
question request, selected evidence receipt, and dereferenceable citation set.
It never asks the evaluator to retrieve or browse.

Deterministic metrics include:

- citation validity and access/partition closure;
- substantive-statement citation coverage;
- citation precision against allowed supporting evidence;
- supported/mixed/insufficient label correctness;
- source-fact versus inference label correctness;
- contradiction preservation, abstention/no-evidence accuracy, and fabricated
  citation count;
- evidence digest replay and answer size/latency/cost bounds.

Semantic entailment cases may use reviewed labels or an optional bounded judge.
Judge output is recorded as evidence with disagreement and uncertainty; it
cannot override deterministic citation, access, digest, or schema failures.
Prompt-injection-shaped evidence is part of the provider-free adversarial set.

## Threshold Policy And Comparison

`QualityThresholdPolicyV1` is a reviewed, versioned JSON document. Each rule
names axis, metric, scope, comparator, threshold, minimum denominator, severity,
and missing-data behavior. Thresholds are never embedded as unreported defaults
or chosen by the candidate/model during evaluation.

Run state is one of `passed`, `failed`, `not_measurable`, `invalid`, or
`incomplete`. Axis states remain separate. A global blocking pass requires all
declared blocking rules to pass with their minimum denominators; warning-only
rules cannot hide a blocking failure. Baseline comparison reports absolute
values and deltas. A candidate may fail a fixed floor even when it improves on
baseline, and may fail a regression budget while remaining above the floor.

Production-quality wording requires a current production-bound sample receipt,
an accepted sample design, and explicit applicable scope. Fixture success is
labeled `provider_free_fixture`, never production quality.

## Report And Artifact Contract

`QualityEvaluationReportV1` contains:

- immutable run/request IDs and all pinned identities/digests;
- effect receipt proving provider-free or declaring each optional external
  dependency actually used;
- per-axis states, metric numerators/denominators/exclusions, thresholds,
  baseline/candidate values, and deltas;
- ordered case results with bounded observed identities, failure codes, and
  artifact refs;
- aggregate blocking decision and safe exit code;
- truncation, incomplete-run, cleanup, and evaluator-error receipts.

The canonical JSON is authoritative. Markdown is a deterministic projection.
Artifacts default under an ignored explicit output directory; CI may upload
them but repository commits contain only reviewed fixtures, policies, and
small expected metadata. Reports redact paths or values that could disclose
credentials or private data.

Exit codes distinguish pass, quality failure, invalid configuration/fixture,
and incomplete infrastructure execution. A crash or skipped axis cannot become
a passing report.

## Continuous Execution Topology

- focused development: changed-axis cases only, with the trustworthy affected
  mapping recorded;
- blocking presubmit: full provider-free fixture set for affected public
  contracts, with unknown impact widening to all axes;
- periodic comprehensive: full provider-free sets, larger performance corpus,
  baseline trend retention, and evaluator self-tests;
- opt-in observation: read-only staging or production sample and optional
  judge, separately gated and never required for ordinary local development.

No evaluation run refreshes sources, starts a browser, follows an account,
changes a schedule, writes an installed database, deploys, or promotes a model.
An opt-in observation reads an immutable snapshot or read-only export, not the
live writable database.

## Dependency And Ownership Contract

- Packet 1 is independent and may begin now using fake axis adapters and sealed
  fixtures.
- Retrieval adapter integration waits for WI-002 Packet 1's accepted
  `PostSearchBackend`, request/response, evidence refs, and search heads.
- Retrieval acceptance waits for WI-002 closeout.
- Grounding adapter integration waits for WI-003 Packet 3's accepted answer,
  statement, citation, and status contracts; final grounding acceptance waits
  for WI-003 closeout.
- WI-008 owns evaluation-set, threshold, metric, report, and runner contracts.
  It does not own search ranking, question answering, collection behavior, or
  provider adapters.
- The coordinator resolves shared contract/catalog, CI workflow, and generated
  compatibility overlaps.

## Vertical Delivery Packets

1. Quality tracer: strict evaluation-set, threshold-policy, request/report,
   metric/result, effect, and artifact contracts; deterministic IDs/digests;
   fake four-axis adapters; JSON/Markdown renderer; CLI exit semantics; and
   provider-free self-tests. No service process or external judge starts.
2. Integrity and coverage tracer: sealed SQLite/receipt fixtures, read-only
   corpus and coverage adapters, denominator handling, provenance/digest/
   revision/access invariants, and case-level failure artifacts.
3. Retrieval tracer: after WI-002 Packet 1, exercise the real
   `PostSearchBackend`, filter/pagination/revision/provenance/ranking metrics,
   a deterministic 10,000-post performance set, and baseline comparison.
4. Grounding and continuous closeout: after WI-003 Packet 3, add deterministic
   answer/citation/conflict/abstention metrics, prompt-injection fixtures,
   affected-axis mapping, blocking presubmit and periodic commands, docs, and
   one fresh isolated provider-free run. Optional judge and production sample
   remain separate later gates.

## Expected Write Surfaces

- new repo-only modules and command under `dev/last30days/quality/` and
  `dev/last30days/scripts/`;
- reviewed fixtures under `fixtures/service_quality/`;
- focused tests under `tests/` and CI only when the command is stable;
- WI-002/WI-003 interfaces only through their accepted shared contracts;
- configuration docs only if a real user-facing knob is introduced;
- plan, roadmap, runbook, work item, and active-lane custody.

The lane owner must start from current `origin/main`, run CodeGraph impact
before shared-contract changes, and coordinate CI or service catalog edits with
the coordinator.

## Provider-Free Acceptance Boundary

- the same commits, fixture set, threshold policy, and inputs produce the same
  semantic report and case ordering;
- numerator, denominator, exclusions, threshold identity, and pinned heads are
  present for every metric;
- empty, unknown-denominator, stale, partial, corrupt, duplicate, cross-
  partition, malformed-cursor, unsupported-claim, conflicting, no-evidence,
  and evaluator-crash fixtures yield distinct truthful states;
- candidate code cannot modify its fixture expectations, threshold policy, or
  baseline during execution;
- JSON/Markdown projections agree and exit codes cannot label skipped or
  incomplete blocking axes as passed;
- no test touches a network, model, provider, browser, credential, installed
  Skill, writable production database, schedule, staging, or deployment;
- a fresh isolated run produces replayable artifacts and leaves no untracked
  worktree or process.

## Open Questions For The Lane Owner

- Measure the Packet 1 fake-axis and Packet 3 10,000-post runs before freezing
  focused and presubmit wall-clock budgets.
- Select the smallest reviewed redistribution-safe fixture corpus that spans
  all five current sources without encoding time-sensitive live expectations.
- Define the production-sample design and privacy review only when explicit
  authority for that later observation lane exists.

## Graphiti Write Status

`graphiti_write_pending`: Plans 0076-0079 already await recovery of the known
degraded ingestion path. This architecture does not queue another write. Its
intended episode is the integrated decision, validation, dependency joins, and
Packet 1 gate.

## Skill Friction

The shared `codebase-investigator` skill still references optional shared
example files absent from its installed tree. All required core references and
CodeGraph evidence were available; this did not limit the investigation.

## State Location

This note and its machine-readable companion are durable in the stable Git
repository. No bundle or snapshot is needed.
