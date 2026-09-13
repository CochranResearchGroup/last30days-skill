# Policy | Work Item Traceability

## Policy

- Use the issue tracker or governed repo-local backlog as the intake,
  discussion, prioritization, and dependency surface. Do not make it the sole
  authority for detailed execution, Git custody, review, or completion proof.
- Keep authority roles explicit:
  - `ROADMAP.md`: initiative priority and sequencing;
  - work item: problem or outcome, owner, state, priority, and dependencies;
  - bounded plan: execution scope, non-goals, acceptance criteria, and next action;
  - `docs/dev/active-lanes.yaml`: concurrent branch and custody projection;
  - review system: review state and findings;
  - Git, tests, deployment readback, and receipts: implementation and completion evidence.
- Give every actionable work item a stable locator, one bounded outcome,
  acceptance evidence, an owner or owning lane, current state, and explicit
  blockers or dependencies. Preserve the locator across plans, branches,
  changes, handoffs, and completion receipts.
- Use `TRIAGE`, `READY`, `IN_PROGRESS`, `BLOCKED`, `DONE`, and `CANCELLED` for
  work-item state. Do not infer implementation or integration from a label,
  assignee, comment, or closed issue alone.
- Keep unrefined ideas in `TRIAGE`. Move an item to `READY` only when its
  outcome and acceptance signal are understandable. Move it to `IN_PROGRESS`
  only when an owner has accepted it and any substantive implementation lane
  is discoverable.
- Keep at most three substantive feature items `IN_PROGRESS`. The separately
  reserved hotfix capacity does not increase that feature limit. When the
  limit is reached, finish, unblock, split, cancel, or pause existing work
  before starting another feature lane.
- Split oversized work into outcome-oriented child items or plans and record
  blocking relationships. Avoid parallel children whose expected write
  surfaces substantially overlap unless reconciliation is part of the plan.
- Link delivery changes to their governing work item. Use automatic closing
  only when integration into the intended target satisfies the work item;
  otherwise use a non-closing reference and close from verified evidence.
- Close a work item only when its acceptance evidence and truthful
  implementation, integration, rollout, cleanup, or non-code disposition are
  recorded. Reopen it or create a linked corrective item when rollback,
  regression, or missing evidence invalidates that claim.
- Triage stale, duplicate, blocked, and abandoned items on a documented
  cadence. Link duplicates, retain decision context, and cancel work
  explicitly rather than leaving an indefinitely active shadow backlog.

## Repository Transition

- GitHub Issues and Projects are the intended shared work-item surface for this
  repository, but they are not active authority until the operator enables
  them and a bounded migration establishes target, labels, templates, and
  provider-operation controls.
- Until that migration is accepted, use stable roadmap lane and plan locators
  as the governed repo-local work-item identifiers. Do not claim an issue URL,
  issue state, or Project state that does not exist.
- Adopt forge- and GitHub-specific issue-operation policy in the same bounded
  slice that enables the tracker. Migrate existing active-lane locators before
  making external work-item linkage a required catalog field.

## Adoption Notes

This repository has enough concurrent and deferred product work that chat,
branch names, and plans alone are not a sufficient long-term intake surface.
This policy establishes traceability now while keeping external tracker writes
behind their own explicit authority and readiness gate.
