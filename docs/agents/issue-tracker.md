# Issue Tracker Operating Contract

## Current Phase

State: `REPO_NATIVE_PREACTIVATION`

GitHub Issues are currently disabled for the owned public fork. The exact
target registry permits read-only preflight, so files under
`docs/dev/work-items/` are reviewable drafts rather than remote issues.

Until explicit activation is accepted:

- use the stable `WI-###` marker as the work-item locator;
- keep actionable state in the work-item draft, roadmap lane, bounded plan,
  and active-lane catalog as applicable;
- do not claim an issue number, URL, Project item, assignment, or remote state;
- do not enable Issues, create labels or Projects, or publish drafts.

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

## Activation Sequence

1. Review and accept the issue breakdown and dependency graph.
2. Receive explicit operator direction for the exact GitHub mutations.
3. Enable Issues on `CochranResearchGroup/last30days-skill`.
4. Re-run read-only preflight and confirm templates and label mappings.
5. Expand the registry only to the accepted actions.
6. Create one Project with the fields above, then read it back.
7. Publish parent and child issues idempotently, searching each stable marker
   before creation and recording every resulting URL.
8. Link dependencies and Project metadata only after their separate gates pass.
9. Replace each draft's provisional locator with a mapping that preserves its
   `WI-###` marker and records the exact GitHub issue URL.

Security reports remain prohibited until an accepted private reporting route
exists. The public issue tracker is never a fallback disclosure channel.
