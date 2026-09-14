# P51 Fresh-Agent Handoff

Date: 2026-09-13
Repository: `/home/ecochran76/workspace.local/last30days-skill`
Canonical remote: `origin` = `CochranResearchGroup/last30days-skill`
Canonical branch: `main`
Canonical checkpoint at handoff creation:
`b95b5548ffae852c4eb7a8523b8c1fb04ca1e10c`

## Mission

Continue Plan 0102/P51 and close the accepted productization prerequisites
before starting any unrelated feature packet. The immediate bounded outcome is
the two question-answering contract repairs tracked by WI-009 / GitHub issue
#55.

Do not duplicate the full program design here. Read these authorities in order:

1. `AGENTS.md` and the policies it routes for planning, Git/worktrees,
   validation, documentation, work items, collaborative development, and
   issue operations;
2. `ROADMAP.md`, P51;
3. `docs/dev/plans/0102-2026-09-13-productization-readiness-prerequisites.md`;
4. `docs/dev/work-items/WI-009-productization-readiness-remediation.md` and
   https://github.com/CochranResearchGroup/last30days-skill/issues/55;
5. `docs/dev/work-items/README.md` for all live issue mappings.

## Startup Checks

Run from the canonical worktree before creating a corrective checkout:

```bash
cd /home/ecochran76/workspace.local/last30days-skill
git fetch origin --prune
git status --short --branch
git rev-parse HEAD origin/main
git worktree list --porcelain
gh issue view 55 --repo CochranResearchGroup/last30days-skill
gh pr list --repo CochranResearchGroup/last30days-skill --state open
```

Require a clean canonical `main` equal to current `origin/main`. The SHA above
is a handoff anchor, not permission to ignore a newer remote tip.

Use CodeGraph for structural discovery. At handoff creation the canonical index
was known healthy during the review, but recheck `codegraph status` and honor
its staleness banner before relying on it. Run focused Graphiti discovery in
`last30days_skill_main`; treat it as advisory because the latest searches
returned only older roadmap history.

## Accepted Findings To Repair

1. `QuestionRunner.run_once` catches `QuestionWorkerError` and
   `QuestionValidationError`, but a `QuestionContractError` raised while
   constructing the final structured answer can escape. An `answered` worker
   result with no statements was reproduced leaving the task `running`, attempt
   count 1, with no error receipt until lease-expiry recovery. Relevant source:
   `skills/last30days/scripts/lib/service_questions.py` around `_worker_answer`
   and `QuestionRunner.run_once`; contract invariant in
   `service_question_contracts.py` requires statements for `answered`.
2. The direct `answer_mode=evidence_only` path copies full selected evidence
   text without enforcing `max_answer_characters`. A 128-character request was
   reproduced returning 1,046 total answer characters. The structured-worker
   and model-unavailable fallback paths already enforce or budget this limit.

Plan 0098 acceptance criterion 3 requires malformed and oversized outputs to
fail closed with safe durable terminal receipts. Add regression tests that fail
before implementation, then make the smallest host-owned correction.

## Current Program And Forge State

- PR 51 merged the P51/WI-009 plan and corrected the category error that treated
  the issue registry as a pull-request gate.
- PR 62 merged exact issue mappings and provider readback.
- WI-000 through WI-009 are open as issues #52 through #61. WI-009 is #55.
- `docs/dev/forge-issue-targets.json` permits only `read`, `create`, and
  `apply_labels`. Do not comment, edit, assign, close, reopen, create labels,
  create Projects, or mutate milestones without new operator authority and a
  matching registry action.
- Pull requests are not governed by the issue registry. They follow
  `docs/dev/policies/0032-collaborative-development-workflow.md`.
- Tracker-documentation reconciliation and initial issue publication are
  complete prerequisites. Q&A repair, P35 integration, development release,
  and development dogfood remain.

## Git, Runtime, And P35 Boundaries

- Create a new short-lived corrective branch and worktree from freshly fetched
  `origin/main`; do not reuse the old WI-003 checkout.
- Write and register Plan 0103 for the Q&A corrective packet before source
  implementation. Link WI-009/#55 and identify the question modules/tests as
  the expected write surface.
- P35 remains on `feat/x-tailored-follows-v1` at remote-equal checkpoint
  `d2c9f8ebfa79e99eb501910c7d606ce3bcbcf07d`. At this handoff it is 80 commits
  behind and eight commits ahead of `origin/main`; do not reconcile it until the
  Q&A correction integrates.
- Production is the sole running service. It reports service `0.3.116`, schema
  17, and manifest
  `19707a469eb58c21ca4c5b43a0bfbfb6cac4b0f5a5310480b01b1a3f652429e8`.
- Source also declares `0.3.116` but has a different 139-file manifest
  `9494e8129b13875057dade22afb00935748cf4336b80281423d330a192aa0050`.
  Do not install, restart, migrate, release, or touch production during the Q&A
  corrective packet.

## Required Validation For The Next Packet

- focused red/green tests for empty-statements contract construction and direct
  evidence-only total character budgeting;
- affected question, worker, service-contract, package, and MCP tests;
- `uv run pytest` and `go test ./...` before integration because the correction
  touches a public product contract;
- runtime-manifest drift, planning-contract, active-lane, and `git diff --check`
  validation;
- published branch equality, PR diff self-check, merge receipt, and canonical
  ancestry before marking the corrective packet integrated.

The earlier broad suite was green, but that does not discharge either
reproduced defect because the exact edge cases were absent.

## Hard Stops

- no unrelated WI-001 through WI-006 or WI-008 feature packet while P51/WI-009
  remains open;
- WI-007 production hotfixes remain the only unrelated exception;
- no model/provider/browser/profile call, acquisition, schedule, installed
  database/runtime mutation, staging, production, tag, release, or deployment;
- no P35 Packet 2 or cross-service follows;
- no issue mutation beyond the registry and current operator authority.

## Exact Next Action

From freshly verified `origin/main`, create and register Plan 0103 plus a new
Q&A corrective branch/worktree linked to WI-009/#55. Add the two failing
regression tests, implement only the accepted repairs, run the required
provider-free validation, and integrate through a normal owned-fork PR. Then
reconcile P35 as the next serialized P51 packet.

## Suggested Skills

- `last30days:repo-policy-selector` for deterministic planning and lane audits;
- `graphiti-discovery` for narrow prior-context discovery;
- `codegraph-workspace` for structural source and impact analysis;
- `diagnosing-bugs` and `tdd` for the two accepted Q&A regressions;
- `handoff` again at the next material checkpoint.
