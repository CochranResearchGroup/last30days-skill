# Policy | GitHub Issue Operations

## Policy

- Use this adapter with `0030-forge-issue-reporting.md` and identify a target
  by explicit GitHub hostname plus `OWNER/REPO`. Distinguish this owned public
  fork from its non-owned upstream.
- Before any write, use the pinned selector's read-only preflight helper to
  verify the authenticated actor, canonical `nameWithOwner`, viewer
  permission, archive state, Issues availability, fork parent, templates,
  security route, and relevant labels.
- Treat create, comment, edit, apply-label, create-label, assign, milestone,
  Project, close, reopen, and transfer as separate capabilities and operator
  actions. A successful read preflight grants none of them.
- Read `CONTRIBUTING.md`, `SECURITY.md`, issue forms, chooser configuration,
  and contact links when present. API-created issues must satisfy the same
  required fields as the repository's forms.
- Resolve every normalized label to one exact existing repository label before
  creation. Missing labels fail closed unless label creation was separately
  authorized.
- Issue types, Projects, milestones, sub-issues, dependencies, and assignees
  are optional extensions. Do not populate them from issue-create authority.
- Use GitHub private vulnerability reporting or the declared private security
  route for vulnerability details. With no accepted private route, stop and
  report the gap without publishing details.
- Bind every mutation receipt to the returned repository, issue number, URL,
  actor, and read-back state. On timeout, rate-limit ambiguity, or connection
  loss, search the stable work-item marker before retrying.

## Repository Defaults

- The only allowed remote target is the owned public fork
  `github.com/CochranResearchGroup/last30days-skill`; never create tracker
  content against `mvanhorn/last30days-skill`.
- GitHub Issues are enabled. The accepted publication action allows creation of
  WI-000 through WI-009 with existing mapped labels; exact URLs must be read
  back before repo-local drafts claim remote identity.
- `docs/dev/forge-issue-targets.json` governs issue and Project actions, not
  pull requests. Pull requests follow branch and integration policy.
- Comment, edit, close, reopen, assign, milestone, Project, and label-creation
  actions remain separately gated unless the registry and current operator
  authority explicitly allow them.
