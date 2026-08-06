# Note 0061 | Fresh-agent handoff | Plan 0018 V22/C54

Date: 2026-08-02  
Repository: `/home/ecochran76/workspace.local/last30days-skill`  
Branch: `main`  
Public remote: `origin` (`CochranResearchGroup/last30days-skill`)  
Pre-handoff base: `b913b68c40c760ac96a0032b48235e0d8c76bfc8`

## Purpose

Continue Plan 0018 after the independently accepted zero-source index-
sequencing repair. The next agent must begin read-only and stop at the explicit
remaining-proof human gate. This note is a routing document; the plan and
machine-readable receipts remain authoritative for detailed history.

## Authority order

Read these in order before proposing or executing anything:

1. `AGENTS.md` and the relevant modules under `docs/dev/policies/`;
2. `docs/dev/plans/0018-2026-07-29-service-first-software-product-transition.md`,
   especially V22/C54;
3. `ROADMAP.md` P07 current state and next bounded action;
4. `RUNBOOK.md` Turns 113-120;
5. `docs/dev/notes/0031-replacement-youtube-index-proof.json`;
6. `docs/dev/notes/0032-zero-source-index-sequencing-repair.json`;
7. current Git, installed-service, SQLite, and collection-spec readbacks.

The older
`docs/dev/notes/0060-2026-08-01-timed-polling-service-replan-handoff.md` is durable
history, not current authority.

## Current verified state

- Plan 0018 is the sole open plan at version 22/C54
  `zero_source_index_sequencing_repair_complete`.
- Service 0.2.26/schema 12 is installed, ready, and systemd active/running.
  Rollback is 0.2.25.
- Runtime manifest SHA-256 is
  `21564f14a2c87f3d2ee27013470bdc3642e9d70997facebc726b75c92982c1fb`.
- Active index is `index-28418bd968076bba6653223f`; it has 59 stable and
  59 current-version embedding rows. The corpus has 59 documents.
- SQLite `quick_check` is `ok`; the last verified foreign-key error count is
  zero. Configuration mode is 0600.
- Acquisition/job/collection-run counts are 102/87/50.
- All 37 collection specifications are disabled.
- The cumulative source-attempt ceiling is fully consumed at 25.
- Work through C54 is pushed to `origin/main`. The handoff commit containing
  this note must also be verified against remote `main` before closeout.

## What completed

- The authorized replacement YouTube proof produced useful content but failed
  closed because three new current versions lacked embeddings. Receipt 0031
  binds the run, source provenance, immutable envelopes, counts, and hard stop.
- The zero-source repair moved pending embedding completion behind the existing
  `CorpusPublisher.publish_index()` interface. The full-runner regression is in
  `tests/test_service_job_runner.py`.
- Service 0.2.26 forward-filled exactly the three missing version embeddings,
  published one complete successor index, and preserved all 68 pre-install
  index snapshots. Receipt 0032 binds the hashes and live readbacks.
- Fresh-context final review passed with no critical finding after independently
  rerunning 23 focused tests, 7 package tests, and the full suite: 2,416 passed,
  7 skipped, and 6 subtests passed.
- Key commits are:
  - `f3a7c9c` — embed pending content before publication;
  - `7f11000` — close the repair and persist receipt 0032;
  - `b913b68` — record the bounded Graphiti timeout truthfully.

## Remaining human gate

No source execution is currently authorized. The remaining evidence-completion
identities are:

1. `p0018-v17-x-browser-manual`;
2. `p0018-v17-linkedin-topic-browser-manual`;
3. `p0018-v17-linkedin-profile-browser-manual`.

Before any of them may run, derive and independently review a bounded successor
that asks the operator to raise the exact cumulative attempt ceiling from 25 to
28. Preserve serial execution, one attempt per identity, no retry, zero cost,
global integrity stops, immutable receipts, and independent final review.
Recurring enablement is a separate later human gate even if all three proofs
pass.

Do not treat the prior generic approvals as authority for this new ceiling
increase. Do not enable specs, submit a proof, refresh credentials, change
access methods, retry YouTube, or start recurrence before the new plan is
reviewed and the operator explicitly approves the named boundary.

## Startup commands

Run read-only checks first:

```bash
cd /home/ecochran76/workspace.local/last30days-skill
git status --short --branch
git fetch origin main
git rev-list --left-right --count origin/main...HEAD
git log -8 --oneline --decorate
uv run python dev/last30days/scripts/audit_plan_authority.py --root .
/home/ecochran76/.local/share/last30days/service/last30days-service status
sqlite3 /home/ecochran76/.local/share/last30days/research.db \
  "PRAGMA quick_check; PRAGMA foreign_key_check; SELECT COUNT(*), SUM(enabled) FROM collection_specs;"
```

Expected starting results: clean `main`; local/remote divergence `0 0` after
this handoff is pushed; authority audit passed with Plan 0018 only; service
0.2.26/schema 12 ready; SQLite `ok` with no foreign-key rows; 37 specs and zero
enabled.

If any expected result differs, stop and reconcile current source, installed,
and remote state before planning the successor.

## Validation and evidence commands

The repair is already validated; do not rerun broad tests merely to orient.
When a successor changes code or authority, use the repo-native checks:

```bash
uv run pytest tests/test_service_job_runner.py tests/test_service_publication.py tests/test_service_retrieval.py -q
uv run pytest tests/test_release_versions.py tests/test_service_runtime_package.py -q
uv run pytest
uv run python dev/last30days/scripts/audit_plan_authority.py --root .
git diff --check
```

The installed runtime must be verified separately from Git. A passing source
suite does not prove installed-service or live-index state.

## Hard stops

Stop immediately on any of these:

- an acquisition starts before the new 25-to-28 ceiling approval;
- any spec becomes enabled before its distinct recurrence gate;
- a retry, second attempt, or out-of-order proof appears;
- current-version completeness drops below 59/59;
- any pre-existing immutable index row changes;
- SQLite, configuration mode, manifest, service readiness, or installed/source
  version diverges;
- the independently reviewed successor arithmetic or authority surfaces disagree.

## Graphiti status

The required compact closeout episode was submitted to
`last30days_skill_main`, but job
`1dfbe360-4e08-4dab-92e4-fa7d6e09b3b5` timed out once during edge extraction.
It is `graphiti_write_pending`. Do not retry it merely during orientation; retry
at the next non-trivial closeout after provider readiness, as required by
`docs/dev/policies/0005-graph-backed-memory-usage.md`.

## Suggested skills

- `last30days` for the installed-service operator workflow and collection
  receipts;
- `codegraph-workspace` for structural source questions before file-search
  loops;
- `tdd` plus `codebase-design` if a new product-code defect is discovered;
- `handoff` when producing the next repo-native continuity checkpoint.

## Best next action

Remain read-only, verify the startup state, then draft one bounded Plan 0018
successor for the three remaining proofs. Obtain fresh independent plan review
and ask the operator for the exact 25-to-28 attempt-ceiling increase. Stop there
until explicit approval arrives.
