# Issue Tracker Operating Contract

## Current Phase

State: `GITHUB_ISSUES_ACTIVE`

GitHub Issues are enabled for the owned public fork. The operator authorized
publication of the prepared WI-000 through WI-009 backlog. The exact target
registry permits `read`, `create`, and `apply_labels`; all other issue actions
and GitHub Projects remain separately gated.

During publication and steady-state operation:

- use the stable `WI-###` marker as the work-item locator;
- search the exact marker before creation and read back every created issue;
- record the issue URL in the matching repo-local work item without replacing
  roadmap, plan, lane, Git, validation, or runtime authority;
- apply only an existing mapped label; do not create or substitute labels;
- do not comment, edit, close, reopen, assign, create milestones, or create a
  Project without separate operator authority and registry support.

## Workflow

Work-item states are `TRIAGE`, `READY`, `IN_PROGRESS`, `BLOCKED`, `DONE`, and
`CANCELLED`. No more than three feature items may be `IN_PROGRESS`; one
additional reserved slot is available only for a production hotfix.

The intended GitHub Project fields are:

| Field | Values |
|---|---|
| Status | Triage, Ready, In progress, Blocked, Done, Cancelled |
| Priority | P0, P1, P2, P3 |
| Lane | Program, Search, MCP, Follows, Runtime, Hotfix, Quality |
| Environment | N/A, Development, Staging, Production |

Existing repository labels are reused through the exact mappings in
`docs/dev/forge-issue-targets.json`. Priority, lane, state, and environment
belong in Project fields rather than a new label taxonomy.

## Publication Sequence

1. Re-run preflight and confirm target, actor, templates, and label mappings.
2. Publish parent and child issues idempotently, searching each stable marker
   before creation and recording every resulting URL.
3. Replace each draft's provisional locator with a mapping that preserves its
   `WI-###` marker and records the exact GitHub issue URL.
4. Link dependencies through issue-body references available at creation time;
   later comments or edits remain separately gated.

GitHub Projects remain planned but inactive. Project creation, fields, and item
linkage require a separate operator decision and registry action.

Security reports remain prohibited until an accepted private reporting route
exists. The public issue tracker is never a fallback disclosure channel.
