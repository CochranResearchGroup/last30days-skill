# Policy | Forge Issue Reporting

## Policy

- Use this policy with `0027-work-item-traceability.md`. The tracker owns
  intake, discussion, priority, and dependencies; plans, lanes, review, Git,
  tests, deployment readback, and receipts retain separate authority.
- Resolve every operation through `docs/dev/forge-issue-targets.json` to an
  exact forge, hostname, and canonical repository. Do not infer a write target
  from the working directory, default remote, similarly named fork, or prior
  operation.
- Require current operator authority for the exact action, an allowlisted
  target/action, target-policy compliance, current provider capability, and a
  readable postcondition before any provider mutation.
- Authentication and repository roles prove capability, not operator intent.
  Read authority never implies create, comment, edit, label, assign, close,
  reopen, transfer, or Project authority.
- Keep the target registry non-secret and fail closed on unknown actions,
  targets, label mappings, provider-label drift, or security routing.
- Classify proposed reports as defect, feature, operational incident,
  governance gap, or security report. Include bounded expected-versus-observed
  evidence, impact, environment/version, and uncertainty without credentials,
  customer data, or unnecessary personal data.
- Search for duplicates before creation and retain the stable marker from the
  corresponding repo-local work item. After a timeout or ambiguous response,
  search and read back that marker before retrying.
- Applying an existing label, creating a label, changing taxonomy, assignment,
  milestone mutation, and Project mutation are distinct actions and authority
  gates. Never silently substitute a label or create a missing one.
- Security-sensitive content must use an accepted private disclosure route.
  When the registry says no route is configured, stop; never fall back to a
  public issue.
- Record each mutation in `RUNBOOK.md` or a linked durable receipt with actor,
  host, repository, issue or Project locator, action, idempotency marker,
  timestamp, before/after state, and post-write readback.
- Issue closure is not implementation, validation, integration, deployment, or
  cleanup proof. Close only when the governing acceptance evidence exists.

## Activation Gate

- The registry initially allows read-only preflight. Expanding its
  `allowed_actions`, enabling GitHub Issues, creating labels or a Project, and
  publishing the draft backlog are external mutations that require explicit
  operator direction and their own verified receipts.
