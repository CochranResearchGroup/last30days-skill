# Plan 0010 | App Intelligence task contracts

State: PLANNED
Roadmap: P06
Date: 2026-07-25
Predecessor: Plan 0007
Integrated campaign authority: Plan 0011

Plan 0010 is a component contract plan. Execute its packets only through the
attachment gates in
`0011-2026-07-25-integrated-temporal-intelligence-service.md`; it does not own
the temporal corpus, recurring collection, profile history, GraphRAG
authority, or complete agent-facing product.

## Execution State

Plan version: 1
Critical-path owner: primary agent
Execution branch: `main`
Optimization posture: contract-first vertical slices with deterministic
host-validation gates

Local goal bounds:

- maximum implementation attempts per packet: 2;
- maximum review/rework cycles per packet: 1;
- maximum consecutive hardening-only checkpoints: 2;
- checkpoint after the common contract kernel, domain contracts, supervisor
  integration, and acceptance evaluation;
- every task contract must set finite item, byte, model-call, cost, and
  wall-time limits before it can be enabled;
- no stochastic output may directly mutate corpus authority, identity,
  collection state, ranking policy, source configuration, the main worktree,
  installed services, or deployments.

## Objective

Create a versioned contract system for App Intelligence tasks so stochastic
workers can assess incoming content, propose profile and identity
relationships, evaluate retrieval, and diagnose or repair adapters while the
host remains deterministic, auditable, replayable, and idempotent.

The model itself is not required or claimed to be deterministic. The contract
must make each recorded output deterministically acceptable, rejectable,
promotable, and replayable under a named host policy.

## Current Evidence

- `service-contracts-v1.json` is already the public schema catalog for query,
  acquisition, evidence, job, entity, relationship, and decision records.
- `service_contracts.py` already rejects unknown contracts and unexpected
  fields, and `DecisionRecord` records the proposal plus deterministic host
  acceptance and validator errors.
- `service_intelligence.py` already provides strict structured-output schemas
  for enrichment, retrieval evaluation, and repair recommendation, along with
  a durable intelligence ledger, model-call budgets, evaluation records,
  approvals, branch isolation, and terminal repair states.
- `service_enrichment.py` already separates accepted IDs from bounded proposal
  rejection codes.
- The existing leaves do not share one versioned task envelope, evidence
  closure contract, validator-code taxonomy, promotion receipt, or consistent
  domain policy. `content_assessment`, `profile_change_assessment`,
  `identity_resolution`, and `adapter_failure_triage` are not yet first-class
  contracts.

## Contract Principles

1. The host constructs inputs, selects evidence, computes digests and stable
   IDs, reserves budgets, invokes workers, validates results, promotes accepted
   proposals, records receipts, and owns all state transitions.
2. Workers return bounded recommendations only. They do not call other
   adapters, fetch unreferenced evidence, choose their own authority, or
   perform control actions.
3. Every result is correlated to the exact task, input digest, contract
   version, policy version, worker configuration, evidence set, and access
   partition used to produce it.
4. Every array and free-text field has an explicit maximum. Unknown fields,
   actions, targets, evidence IDs, or enum values fail closed.
5. Evidence closure is mandatory: a proposal can cite only supplied,
   authorized, immutable evidence spans and document/profile versions.
6. Validation and promotion are separate records. A schema-valid model result
   may still be rejected by evidence, temporal, domain, policy, budget, or
   authorization rules.
7. Duplicate requests, results, and promotions are idempotent. Stable keys are
   derived by the host from canonical inputs, not invented by the worker.
8. Acquisition and cache-first retrieval remain useful when App Intelligence
   is disabled, exhausted, invalid, or unavailable.

## Common Contract Kernel

### `intelligence_task_request`

The host-issued request carries:

- `schema_version`, `contract_name`, `task_type`, `task_id`, `job_id`,
  `run_id`, and host-derived `idempotency_key`;
- immutable `input_artifact_ref`, `input_digest`, evidence references, source
  document/profile version IDs, and the applicable corpus/index version;
- `policy_version`, worker configuration reference, access partition,
  redaction class, and requested time;
- an exact allowed-action set and finite item, byte, call, cost, and wall-time
  limits.

The request never embeds credentials, cookies, browser profile mechanics, or
unbounded private source material.

### `intelligence_task_result`

The worker result carries:

- the matching contract, task, run, input, and policy identifiers;
- exactly one allowed action plus a bounded proposal collection;
- proposal-local confidence, supplied evidence IDs, uncertainty or conflict
  indicators, and bounded rationale or diagnostic codes;
- worker/model reference and an output digest assigned or verified by the
  host.

The result contains no executable command, arbitrary filesystem target,
credential request, deployment instruction, or implicit mutation.

### Evidence and decision records

- `evidence_ref` binds an authorized evidence ID to an immutable source
  revision, optional span or section, observed time, valid-time claim when
  known, content digest, and access partition.
- `validation_receipt` records ordered validator versions, stable error codes,
  accepted/rejected state, and the exact input/output/policy digests.
- `promotion_receipt` records accepted stable IDs, bounded rejection codes,
  prior and resulting authority versions, and idempotency outcome.
- `decision_record` remains the compact model-proposal and host-decision
  summary, extended or versioned only through the schema migration policy.
- `replay_receipt` proves that a recorded result follows the same
  schema/evidence/domain/policy/promotion path under the recorded versions. It
  does not claim that a new model invocation will reproduce the same text.

## Deterministic Validation Pipeline

The host applies these stages in order and stops at the first failed boundary
unless a contract explicitly permits collecting multiple safe error codes:

1. parse strict JSON Schema with `additionalProperties: false`;
2. verify task correlation, input digest, contract/policy versions,
   idempotency key, cardinality, and byte limits;
3. close every evidence reference against supplied immutable artifacts and the
   request's access partition;
4. apply task-specific candidate, temporal, conflict, confidence, and
   authority rules;
5. enforce allowed actions, budgets, target scope, approval class, and current
   host state;
6. deterministically accept, reject, defer, or route proposals to review using
   stable validator codes;
7. publish accepted records idempotently and record validation, promotion,
   decision, and replay receipts.

Validator codes are versioned machine identifiers such as
`unknown_evidence`, `stale_input_version`, `candidate_out_of_scope`,
`temporal_conflict`, `insufficient_support`, `review_required`,
`action_not_allowed`, and `budget_exhausted`; provider text is never used as a
control-flow code.

## Task Contract Catalog

| Task | Bounded worker output | Deterministic host decision |
|---|---|---|
| `content_assessment` | content type, novelty, relevance, entity/claim/event/profile-change candidates, follow-up priority | validate evidence and novelty, deduplicate, promote proposals or record no material signal |
| `profile_change_assessment` | section-level change candidates with previous/current evidence and temporal uncertainty | distinguish real change from missing/redesigned page, promote reversible temporal claims, or review |
| `entity_claim_event_extraction` | normalized entity, claim, event, role, and relationship proposals | validate spans, candidate types, temporal bounds, duplicates, conflicts, and authority policy |
| `identity_resolution` | `same_entity`, `different_entity`, `ambiguous`, or `insufficient_evidence` for host-generated candidates | promote an evidence-backed assertion, keep records separate, or require review; never silently merge |
| `retrieval_evaluation` | bounded relevance judgments and cited evidence for supplied cases/documents | compute metrics, enforce case/document closure, and accept or reject an evaluation batch |
| `adapter_failure_triage` | one failure class, evidence, confidence, and repair eligibility recommendation | route auth, rate-limit, access, transient, configuration, site-change, code-defect, or insufficient-evidence states |
| `adapter_repair_recommendation` | one allowlisted repair action, bounded target files, risk, rationale, and optional next prompt | enforce branch/write scope and budgets; evaluate in isolation; request approval or stop |
| `branch_decision` | select, reject, request one bounded rework, or stop based on supplied eval artifacts | verify evaluation provenance and limits; the host alone changes repair state or requests approval |

`identity_resolution` may compare only candidates generated by deterministic
canonical URL, declared-link, official-domain, normalized-name/handle, and
existing-alias rules. Handle or name similarity alone can never authorize
`same_entity`.

`adapter_failure_triage` uses a host-computed stable failure signature.
Authentication checkpoints, CAPTCHA, access restrictions, and rate limits are
operator or backoff states, not code-repair targets.

## Packets

### Packet 1 | Common schema and validator kernel

- add the common request, result, evidence, validation, promotion, and replay
  contracts to the canonical schema catalog;
- implement exact dataclass/parser representations and a registry keyed by
  contract name and version;
- add canonical digest and idempotency-key derivation;
- define stable validator-code and terminal-decision enums;
- provide compatibility adapters for current enrichment, evaluation,
  `DecisionRecord`, and proposal promotion paths.

Exit gate: strict round-trip fixtures pass; extra fields, oversized values,
unknown actions, mismatched digests, duplicate requests, and unsupported
versions fail with stable codes.

### Packet 2 | Intake, profile, and identity contracts

- implement `content_assessment`, `profile_change_assessment`,
  `entity_claim_event_extraction`, and `identity_resolution`;
- reuse P01 immutable revision, evidence-span, valid-time, system-time, access,
  conflict, alias, and merge/split semantics;
- add deterministic candidate generation and conservative identity/profile
  promotion policy;
- record deferred, ambiguous, and insufficient-evidence outcomes as useful
  terminal decisions rather than retry failures.

Exit gate: adversarial fixtures cannot cite unseen evidence, cross access
partitions, auto-merge weak identities, overwrite history, or mistake a
missing profile section for a confirmed real-world change.

### Packet 3 | Adapter diagnosis and repair contracts

- implement `adapter_failure_triage`, version the existing repair schema as
  `adapter_repair_recommendation`, and add `branch_decision`;
- map acquisition safe error codes and retry classes into stable failure
  signatures and repair eligibility;
- bind allowed target paths, commands, branches, attempts, rework, browser
  leases, calls, cost, and time to host policy;
- preserve the existing no-publish repair supervisor and explicit approval
  boundary.

Exit gate: auth/rate-limit/access/transient cases never enter code repair;
invalid targets and actions fail closed; failed eval reaches a bounded
terminal state.

### Packet 4 | Supervisor, ledger, and service discovery integration

- persist task, evidence, validation, promotion, replay, policy, and worker
  configuration records with additive migrations;
- schedule post-publication assessment independently from acquisition success;
- expose compact capability/readiness and operator diagnostics through MCP
  without exposing prompts, raw model events, browser mechanics, or private
  artifacts;
- preserve raw provider events separately from normalized supervisor events;
- add replay and idempotent recovery across process restarts.

Exit gate: the installed service can discover supported task contracts, replay
a recorded accepted and rejected decision, safely resume duplicate work, and
continue raw acquisition/query behavior with all workers disabled.

### Packet 5 | Evaluation, documentation, and rollout gate

- add golden, malformed, adversarial, temporal-conflict, ambiguity, budget,
  authorization, restart, and replay fixtures for every contract;
- measure validation precision, promotion correctness, ambiguous-identity
  preservation, evidence closure, and repair-routing safety separately from
  model quality;
- document operator-visible policy knobs and service-discovery output;
- run focused and full validation, install a candidate runtime, and perform
  bounded live canaries before timers depend on the contracts.

Exit gate: all acceptance criteria pass against one durable commit and
installed-runtime receipt; P02/P03 timers remain gated until this packet is
closed.

## Parallelism And Reconciliation

Packet 1 is the critical path and has one owner. After its schema names and
validator semantics are frozen, Packets 2 and 3 may proceed in parallel
because their domain files and fixtures are separable. Packet 4 integrates
both and therefore owns reconciliation of migrations, registries, state
transitions, and service discovery. Packet 5 provides one consolidated review
and at most one bounded remediation pass.

No subagent or delegated implementation is part of this planning slice.
Future execution may delegate only disjoint packets with explicit file
ownership and must reconcile all advisory results against the primary
contract catalog.

## Acceptance Criteria

- every App Intelligence task uses a named, strict, versioned request/result
  contract with finite item, byte, call, cost, and wall-time bounds;
- identical recorded input, result, policy, and validator versions replay to
  the same accept/reject/defer/promotion outcome;
- duplicate task delivery and promotion are idempotent across restart;
- every accepted proposal closes to authorized immutable evidence and records
  validation, decision, promotion, and replay receipts;
- unknown fields, actions, evidence, targets, versions, and partitions fail
  closed with stable codes;
- ambiguous identity remains separate and reviewable; no model output directly
  merges canonical people, organizations, or source accounts;
- acquisition publication and cache-first querying succeed when stochastic
  workers are unavailable or disabled;
- adapter auth, checkpoint, rate-limit, access, and transient failures cannot
  trigger autonomous code repair;
- repair actions stay within isolated branches, allowlisted files and tests,
  finite budgets, and explicit integration/deployment approval gates;
- MCP discovery reports contract names, versions, readiness, and safe limits
  without leaking prompts, provider event streams, credentials, browser
  mechanics, or private evidence;
- focused contract, ledger, supervisor, replay, retrieval, migration, and MCP
  tests plus the full repository suites pass;
- `CONFIGURATION.md`, the canonical Skill runtime guidance, service schema
  catalog, roadmap, runbook, and Graphiti checkpoint agree on the shipped
  contract versions and policy knobs.

## Non-Goals

- making model sampling or generated prose seed-reproducible;
- replacing SQLite as the authoritative corpus and ledger;
- allowing model-selected browsing, collection, deployment, or cross-adapter
  orchestration;
- implementing P01 temporal storage, P02 timers, or P03 profile scrapers inside
  this plan beyond the contract seams they consume;
- enabling autonomous identity merges or unattended production repair.

## Stop Rules

Stop this plan when all acceptance criteria are proven, when a P01 temporal
authority decision blocks Packet 2, when an approval or installed-runtime gate
requires operator action, or when remaining work is unbounded quality polish.
Do not broaden the task catalog, add model-driven control actions, or continue
hardening after two consecutive checkpoints without outcome progress; split a
successor plan instead.
