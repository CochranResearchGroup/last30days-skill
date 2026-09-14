# Plan 0101 | Enable GitHub Issues

State: CLOSED
Lane: P50
Work item: WI-000
Branch: chore/enable-github-issues
Target: main
Integration: merge
Roadmap: P50
Plan version: 1
Date: 2026-09-13
Session owner: coordinator Codex thread `01a0860e-b671-7f62-b6ae-6c06a08e6852`

## Objective

Enable the GitHub Issues surface on the owned public fork and preserve an exact,
readable mutation receipt without creating issues, labels, Projects, milestones,
assignments, or other tracker content.

## Current State

- GitHub reports Issues enabled on `CochranResearchGroup/last30days-skill`;
- the authenticated actor was `ecochran76` with `ADMIN` repository permission;
- the issue list is empty after activation;
- `docs/dev/forge-issue-targets.json` remains read-only, so agent-side issue
  creation and all other tracker mutations remain separately gated.

## Scope

- verify the exact owned target and current administrator capability;
- change only the repository `has_issues` setting from `false` to `true`;
- read back the repository setting and issue list;
- update the repo-local tracker status and durable execution authorities;
- publish this receipt through the normal owned-fork pull-request workflow.

## Non-Goals

- no issue creation, migration, edit, label application or creation, assignment,
  comment, closure, milestone, Project, or security-report mutation;
- no product implementation, runtime, service, model, browser, provider,
  credential, install, release, staging, deployment, or production effect;
- no change to the P35 pull-request gate.

## Acceptance Criteria

1. Live GitHub readback reports the exact repository, `has_issues: true`, and
   administrator capability for the authenticated actor.
2. The pinned issue preflight passes for the registry's read action.
3. A post-activation issue listing succeeds and contains no issue created by
   this operation.
4. Repo-local guidance distinguishes an enabled issue surface from authority
   to publish the prepared backlog or perform any other tracker mutation.
5. Planning authority, focused policy tests, and patch hygiene pass on a clean,
   published branch before integration.

## Execution Packet

- accountable human owner: repository operator;
- execution owner: coordinator session;
- expected write surface: this plan, `ROADMAP.md`, `RUNBOOK.md`, and the
  work-item status documentation;
- external effect: one GitHub repository-setting mutation on the exact owned
  fork, explicitly authorized by the operator;
- stop condition: stop after verified Issues enablement and documentation; do
  not publish backlog items or mutate any issue metadata without separate
  operator authority.

Subagents: not used.

## Definition Of Done

The owned fork accepts GitHub Issues, the empty issue surface and exact setting
are read back, and the repository records both the completed activation and the
remaining per-action gates.

## Current Checkpoint

### Checkpoint P0101-C01 | 2026-09-13

Plan version: 1

State transition: `unplanned -> CLOSED`.

Progress classification: `verified_outcome`; the explicitly authorized
repository setting is enabled and its postcondition is independently readable.

Authority classification:

- `explicit_authority` for enabling GitHub Issues on the exact owned fork;
- `not_authorized` for issue, label, Project, milestone, assignment, comment,
  closure, or other tracker-content mutations;
- all installed/runtime/provider/model/release/production gates are unchanged.

Mutation receipt:

- timestamp: `2026-09-13T21:22:13-05:00`;
- actor: `ecochran76`;
- host and repository: `github.com/CochranResearchGroup/last30days-skill`;
- action: repository setting `has_issues: false -> true`;
- pre-write readback: repository unarchived, Issues disabled, actor admin;
- write response: repository unarchived, Issues enabled, actor admin;
- post-write readback: repository unarchived, Issues enabled, actor admin;
- pinned read-only preflight: `ok: true`, exact target and role resolved;
- post-write issue listing: successful and empty.

Validation boundary: the setting readback proves availability only. It does not
prove or authorize backlog publication, labels, Projects, implementation,
integration, deployment, or runtime behavior.

Next action: integrate this receipt through an owned-fork pull request, then
seek a separate operator decision on the exact backlog-publication actions.
