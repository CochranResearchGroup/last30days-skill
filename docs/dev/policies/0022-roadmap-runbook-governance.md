# Policy | Roadmap / Runbook Governance

## Policy

- `ROADMAP.md` is the canonical product direction, priority map, dependency
  graph, and lane catalog.
- `RUNBOOK.md` is the append-only dated record of material work, decisions,
  validation, blockers, and handoffs.
- Keep roadmap lanes named `P## | <Lane Title>` and use only `PLANNED`, `OPEN`,
  `CLOSED`, or `CANCELLED` as lane states.
- Do not materially reorder, rename, or reprioritize roadmap lanes without
  explicit user direction or a narrow correction required to unblock approved
  work.
- Every `OPEN` lane must state what exists, what remains, its dependencies, and
  at least one actionable plan under `docs/dev/plans/`.
- `PLANNED` lanes may hold goal seeds without a detailed execution plan. Before
  execution, convert the next bounded outcome into a plan with:
  - a stable objective and explicit non-goals;
  - dependencies and owned write surfaces;
  - acceptance criteria and current evidence;
  - deterministic and stochastic boundaries;
  - execution packets, hard bounds, gates, and stop conditions;
  - checkpoint fields required by
    `0015-goal-execution-governance.md`.
- Wire every new active plan into both `ROADMAP.md` and `RUNBOOK.md`. A plan is
  not active merely because a file exists.
- Append one `Turn N | YYYY-MM-DD` entry to `RUNBOOK.md` after every material
  planning, implementation, runtime, or closeout slice. Never rewrite prior
  turn history to make later work appear cleaner.
- Each runbook entry must include authority consulted, changes or decisions,
  validation evidence, roadmap/plan state movement, Graphiti write status, and
  the next bounded action or stop reason.
- When summaries drift, the current roadmap, latest runbook entry, active plan,
  current commit, and live runtime evidence outrank older narrative notes in
  that order appropriate to the question.
- Preserve completed plans as history. Use a successor plan or roadmap revision
  for materially new scope rather than silently reopening completed work.

## Adoption Notes

This repository uses the roadmap to preserve long-horizon product intent while
deriving goal-compatible execution packets just in time. The runbook and the
`last30days_skill_main` Graphiti group provide complementary human-readable and
semantic development-journey recall.
