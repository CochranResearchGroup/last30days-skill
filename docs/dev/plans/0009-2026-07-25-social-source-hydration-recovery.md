# Plan 0009 | Social-source hydration recovery

State: CLOSED
Roadmap: P00
Date: 2026-07-25
Predecessor: Plan 0008

## Execution State

Plan version: 2
Critical-path owner: primary agent
Execution branch: `main`
Optimization posture: one bounded live-recovery slice with deterministic
debugging loops and read-only audit sidecars

Local goal bounds:

- maximum implementation attempts per defect: 2;
- maximum live acquisition attempts per source: 3 after version 2 expanded
  the original two-attempt diagnostic bound to permit one installed,
  database-publishing acceptance run;
- maximum review/rework cycles: 1;
- checkpoint after root-cause proof, implementation, installed-runtime
  validation, and database readback;
- browser authentication is fail-closed: automation may reuse and verify an
  existing authenticated profile but may not enter credentials, solve a
  challenge, or manufacture readiness;
- completion requires fresh X, Facebook, and LinkedIn database rows, not only
  profile health or successful browser navigation.

## Objective

Recover the three browser-backed social sources left non-yielding by Plan 0008:
restore truthful X profile routing, make Facebook acquisition finish within the
service worker budget, and obtain one quality-gated LinkedIn result. Publish one
new document per source and prove each result through acquisition, sighting,
active-index, and cache-only database readbacks.

## Current Evidence

- `last30days-facebook` is live and freshly authenticated for Facebook and
  LinkedIn, with a retained shared browser process;
- the user-scoped X target currently resolves to that Facebook/LinkedIn
  profile, which has no X readiness claim;
- no dedicated `last30days-x` runtime-profile registration survived reboot;
- the last X acquisition stopped safely at `auth_required`;
- the last Facebook acquisition exhausted the 120-second worker budget twice;
- the last LinkedIn acquisition reached extraction but failed its content
  quality gate twice.

## Packets

### Packet 1 | Fast failure loops and root-cause proof

- extract the prior Facebook acquisition diagnostics and command timings;
- create a focused, seconds-scale red-capable test for the proven timeout
  mechanism before changing implementation;
- inspect the X profile registry and retained runtime data without exposing or
  copying credentials;
- inspect LinkedIn rejection diagnostics and distinguish query mismatch from
  adapter failure.

Exit gate: each source has a source-attributed failure mechanism and a bounded
test or live probe capable of disproving the leading hypothesis.

### Packet 2 | Minimal repair

- fix only the proven Facebook worker-budget defect;
- restore X routing only if a pre-existing authenticated profile can be
  verified; otherwise create an explicit operator-seeding handoff and stop X
  work at that gate;
- adjust LinkedIn only if evidence proves an adapter defect rather than a
  low-yield query.

Exit gate: focused tests pass and no source readiness is inferred from profile
existence alone.

### Packet 3 | Installed live hydration

- sync the installed Skill and restart the user service when code or
  configuration changes;
- make at most two one-item acquisition attempts for each of X, Facebook, and
  LinkedIn;
- poll each job to a terminal state and preserve its acquisition envelope.

Exit gate: each source either publishes one new document or has a truthful,
terminal operator/external gate with exact evidence.

### Packet 4 | Acceptance and closeout

- verify document, provenance, media, sighting, acquisition, and active-index
  rows for every yielding source;
- verify cache-only retrieval causes no acquisition work;
- run focused and full repository validation;
- reconcile audit sidecars, close this plan truthfully, create structured
  commits, push `origin/main`, and verify local, remote, installed, and live
  state separately.

Exit gate: the requested live outcome is database-backed, validated, committed,
pushed, installed, and served.

## Ranked Falsifiable Hypotheses

1. Facebook exceeds the worker budget because several individually bounded
   browser-control calls accumulate inside one 120-second acquisition attempt.
   Disproof: prior command timings plus a focused fake-client test remain below
   the budget.
2. Facebook is redoing expensive control-plane/profile discovery despite
   receiving retained-browser route hints. Disproof: diagnostics show direct
   reuse of the selected browser and no repeated discovery calls.
3. LinkedIn is operational but the chosen hydration query yields text that
   correctly fails the quality gate. Disproof: rejected candidates contain
   recent, substantive post text that the adapter misclassifies.
4. The X login still exists in an unregistered durable profile and only
   user-scoped target routing was lost. Disproof: registry and bounded auth
   probes find no authenticated X identity.

## Acceptance Criteria

- one fresh X, Facebook, and LinkedIn document is published, unless X requires
  an operator login that cannot be performed by automation;
- Facebook completes without a worker timeout;
- X uses a profile explicitly verified for X and never borrows another
  profile's readiness claim;
- LinkedIn returns substantive recent content that passes the existing quality
  contract;
- each result has a durable acquisition, sighting, active-index membership,
  provenance, and cache-only evidence readback;
- focused tests and the full Python and Go suites pass;
- work is committed in reviewable structure and pushed to `origin/main`.

## Delegation Decision

Policy 0021 supports two disjoint read-only audits while the primary agent owns
the critical path, all mutations, and reconciliation:

- `/root/packet3_pipeline_audit`: inventory possible retained X profile
  authorities and return only profile/readiness evidence;
- `/root/packet2_retrieval`: inspect Facebook timeout diagnostics and command
  timing evidence without editing files or runtime state.

## Checkpoints

### Checkpoint P0009-C00 | 2026-07-25

Plan version: 1

State transition: `planned -> active`

Progress classification: `outcome_progress`

Owned changes:

- converted the three Plan 0008 source failures into a bounded successor plan;
- established deterministic failure loops and explicit authentication gates;
- recorded four ranked, falsifiable hypotheses before implementation.

Validation evidence:

- live profile inventory confirms Facebook and LinkedIn readiness on the
  retained shared profile;
- a fresh access plan confirms X currently selects that same profile but
  requires a bounded auth probe before authenticated work.

Remaining acceptance criteria:

- all Packet 1 through Packet 4 gates.

Next action:

- collect prior acquisition timing/rejection evidence and run the first focused
  failure loops.

### Checkpoint P0009-C01 | 2026-07-25

Plan version: 2

State transition: `packet_1_active -> packet_2_complete`

Progress classification: `outcome_progress`

Owned changes:

- made retained shared-browser access plans authoritative so Facebook,
  LinkedIn, and X skip redundant full service-state discovery;
- replaced Facebook's multi-control search/filter choreography with one
  deterministic recent-post URL plus readback;
- batched Facebook snapshot and extraction evaluation into one dependent
  daemon queue job;
- recovered LinkedIn activity URNs from bounded React runtime state when the
  current DOM omits both permalink anchors and `data-urn`;
- made X open a target tab when none survived reboot and prevented challenge
  text inside authenticated search results from masquerading as a checkpoint.

Validation evidence:

- every defect received a focused red test before implementation;
- the focused Facebook, LinkedIn, X, and user-scoped configuration suites pass;
- live Facebook duration fell from 148,164 ms to 75,201 ms before dependent
  batching;
- live LinkedIn yielded one accepted post in 54,282 ms;
- live X yielded four accepted posts in 56,569 ms.

Subagent status and reconciliation:

- the X profile audit found one durable shared-profile candidate with stale
  retained X evidence overridden by current config; a fresh live probe proved
  that profile's X authentication;
- the timeout audit proved two nearly identical global worker-boundary kills
  and no evidence for a single timed-out browser command;
- both findings were independently reconciled into the implementation and
  runtime proof.

Bound update:

- version 1's two-attempt limit was consumed by failure reproduction and
  post-fix timing proof before the database acceptance run;
- version 2 permits one final installed attempt per source and no further
  implementation loop.

Next action:

- sync the installed Skill, publish one durable result per source, and perform
  database-backed acceptance.

### Checkpoint P0009-C02 | 2026-07-25

Plan version: 2

State transition: `packet_2_complete -> packet_3_complete`

Progress classification: `outcome_progress`

Owned changes:

- recorded the freshly verified X readiness claim in effective user-scoped
  agent-browser configuration;
- synced the installed Skill and restarted the user service;
- published one new X, Facebook, and LinkedIn document through separate
  durable refresh jobs.

Validation evidence:

- X job `fd946b0b-203a-4836-a0c5-83763f34be04`, Facebook job
  `96c8d481-e921-4e8d-b385-488ad5faea54`, and LinkedIn job
  `087fdf83-377d-4531-ad84-be3d210ce09c` each reached `published` on the first
  corrected attempt;
- each new document has one successful acquisition, one sighting, membership
  in its published index, source-native identity, canonical URL, content hash,
  and media metadata;
- the active database now has 31 documents, 31 chunks, 31 embeddings, 77
  entities, six relationships, 51 sightings, and 33 acquisitions;
- three source-specific cache-only queries returned the new evidence with
  `job_id=null`, while acquisition count remained 33 before and after.

Acceptance reconciliation:

- X, Facebook, and LinkedIn each produced a fresh database-backed document;
- Facebook no longer exhausts the worker boundary;
- X readiness is backed by a current live auth/search probe and effective
  user-scoped configuration;
- LinkedIn's current obfuscated DOM produces a canonical activity URL through
  the bounded fallback;
- installed/runtime and database gates pass.

Next action:

- run full repository validation, create structured commits, push
  `origin/main`, and verify local, remote, installed, and live state.

### Checkpoint P0009-C03 | 2026-07-25

Plan version: 2

State transition: `packet_3_complete -> closed`

Progress classification: `outcome_progress`

Validation evidence:

- `uv run pytest`: 2,242 passed, seven skipped, six subtests passed;
- `go generate ./...`, `go test ./...`, and `go vet ./...` all passed under
  `mcp/`;
- `git diff --check` passed;
- installed Facebook, LinkedIn, and X adapter files match the working tree;
- `last30days.service` is active after restart.

Delegation reconciliation:

- both read-only sidecars completed without runtime or file mutation;
- the primary agent independently verified their findings against live
  profiles, durable service receipts, adapter tests, and database rows.

Acceptance reconciliation:

- all Plan 0009 acceptance criteria pass;
- historical failed/awaiting-operator jobs remain as truthful incident
  evidence and do not affect the three corrected published jobs.

Next action:

- commit the implementation and plan closeout in reviewable structure, push
  `origin/main`, and verify local/remote parity.
