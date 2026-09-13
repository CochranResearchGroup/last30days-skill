# Policy | Multi-Session Development Operating Model

## Purpose

Make independent product lanes fast, restart-safe, and reconcilable without
allowing parallel agents, branches, runtimes, or external effects to blur
ownership and evidence.

## Operating Unit

- Use one top-level Codex session as the owner of each substantive development
  lane. A lane session owns one work item, one bounded plan, one short-lived
  branch, one worktree, its acceptance evidence, and its handoff.
- Keep one separate coordinator session for roadmap priority, work-item
  intake, dependency joins, shared-contract decisions, active-lane
  reconciliation, and final integration. The coordinator should not become a
  general feature implementation lane; small conflict resolution and shared
  contract edits are its normal coding boundary.
- Use subagents inside a lane only for concrete, bounded support work such as
  investigation, design alternatives, disjoint implementation, focused tests,
  independent review, or documentation audit. The lane owner reconciles every
  result and remains accountable for the outcome.
- Keep routine delegation one level deep. A lane owner's subagent must not
  spawn another subagent unless the active plan explicitly justifies the
  exceptional topology, names the maximum depth and fan-out, and defines result
  and cancellation flow.
- A single top-level session coordinating subagents is an acceptable temporary
  fallback for governance bootstrap or a short, tightly coupled slice. It is
  not the default for several long-lived feature lanes because session context
  and ownership then become a single failure and congestion point.

## Lane Portfolio And Priority

- Default work-in-process capacity is three feature lanes plus one reserved
  hotfix lane. A normal four-session portfolio is coordinator, runtime/platform,
  search/retrieval, and tailored-follows. The names may change; the ownership
  and capacity rules do not.
- The initial product lanes are:
  - repository search and retrieval productization;
  - a richer agent-facing MCP question and evidence surface;
  - tailored follows for accounts, lists, and topics by supported service;
  - runtime/platform isolation, observability, and deployment controls;
  - a reserved bug-fix and hotfix lane.
- When a production-impacting bug needs the reserved hotfix lane, pause the
  lowest-priority conflicting feature lane if necessary. The hotfix starts
  from current `origin/main`, receives priority review and integration, and
  affected feature branches reconcile to the integrated fix before continuing.
- Do not fill unused capacity merely because an agent slot exists. Dependencies,
  overlapping write surfaces, live-provider serialization, or review load may
  require fewer concurrent lanes.

## Git And Shared Authority

- Keep `main` releasable and use short-lived lane branches. Do not create a
  permanent `develop` branch; environments are deployment identities, not Git
  branches.
- Give every substantive lane its own worktree. Register concurrent lanes in
  `docs/dev/active-lanes.yaml` before parallel execution and publish a
  recoverable remote checkpoint at the earliest safe boundary.
- The coordinator owns cross-lane edits to `ROADMAP.md`, `RUNBOOK.md`,
  `docs/dev/active-lanes.yaml`, shared schemas, and other declared integration
  surfaces. A lane may propose changes to them, but concurrent lane sessions
  must not independently rewrite those shared authorities.
- Define shared schemas and interfaces before parallel implementations depend
  on them. Record dependencies and overlaps rather than relying on sessions to
  discover collisions at merge time.
- GitHub work items are the intended team coordination surface once the
  transition in `0027-work-item-traceability.md` is complete. Chat and session
  summaries remain handoff aids, not the durable portfolio authority.

## Runtime Topology

- The target topology is one production runtime, one staging runtime, and an
  isolated development runtime for each active implementation lane that needs
  service execution. Do not claim that staging or a lane runtime exists until
  provisioning and current readback prove it.
- A lane runtime must use a unique configuration root, database, socket or
  port, logs, and service identity. It must fail closed when isolation cannot
  be proven and must not inherit production credentials, schedules, browser
  profiles, or writable data by convenience.
- Treat authenticated provider/browser canaries as a serialized singleton
  resource unless an explicit plan proves separate profiles and independent
  external-effect boundaries. Multiple development runtimes do not authorize
  parallel live-provider effects.
- Promotion flows from lane evidence to integration, staging acceptance, and
  then production under the applicable release and effect authority. A branch,
  passing unit suite, or healthy dev runtime is not production proof.

## Request And Delivery Discipline

- Use the lifecycle: work item -> bounded plan -> lane owner -> worktree and
  branch -> isolated development runtime when needed -> pull request and
  acceptance evidence -> coordinator integration -> staging/production gate.
- Every work item and plan must name its outcome, non-goals, owner, dependencies,
  expected write surfaces, acceptance evidence, stop condition, and effect
  boundary. Preserve the stable locator through commits, pull requests,
  receipts, and closeout.
- Handoffs must be restart-safe: state the current ref and checkpoint, exact
  worktree/branch locator, authoritative plan and work item, evidence already
  accepted, outstanding gate, and one bounded next action.
- Reserve live mutations, credential use, provider retries, deployments, and
  production changes for explicit authority. Planning readiness or an open
  lane does not grant external-effect authority.
- Close a lane only after its work-item, plan, branch custody, integration,
  validation, and runtime claims agree. Preserve failed and partial evidence;
  do not rewrite history to make a lane appear cleaner.

## Adoption Notes

Read this policy before starting or resuming a substantive development lane,
assigning session ownership, delegating work, creating a runtime, integrating
parallel branches, or entering the hotfix path.
