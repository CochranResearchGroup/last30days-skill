# Policy | Model Selection And Calibration

## Policy

- Select model, reasoning effort, context scope, and delegation topology as one
  decision. Optimize for accepted outcomes while meeting correctness, safety,
  and delivery constraints; do not optimize an isolated worker call.
- Define the milestone and its stable acceptance check before routing
  substantive work. A worker response, prerequisite repair, or unrelated test
  pass is not milestone completion.
- Use the host's calibrated economical default for routine lane work and local
  deterministic tools for mechanical work. Reserve a stronger reasoning tier
  for consequential architecture, policy, security, integration, or ambiguous
  failure analysis where it is likely to change the outcome.
- Select reasoning effort independently from model family. Novelty, task
  length, or an unused concurrency slot alone does not justify escalation.
- Reassess routing at non-trivial task start, material replanning, failed
  acceptance, conflicting evidence, or repeated lack of progress. Distinguish
  a reasoning limit from missing input, missing authority, unavailable tools,
  or an environmental fault.
- Delegate only when expertise, independence, context isolation, or elapsed
  time justifies setup and reconciliation cost. Send the smallest useful brief
  with evidence, acceptance check, write scope, and stop condition. The lane
  owner remains responsible for integration.
- Keep routine delegation one level deep under
  `0028-multi-session-development-operating-model.md`. A deeper topology needs
  explicit plan bounds and evidence flow.
- Calibration must compare complete workflows against frozen representative
  inputs, acceptance checks, retry limits, and resource ceilings. Record
  failures and timeouts; do not retry them away.
- Record model and effort only when the runtime reports them. Label unknown
  effective configuration as unknown; never infer it from an agent name.
- Treat token or price estimates as labeled proxies unless measured allocation
  is available. Keep wall time separate from cumulative worker effort.
- Promote the least costly configuration that meets the frozen quality and
  delivery floor. Revert a regressed default and retain specialist routing only
  where evidence supports it.
- Policy adoption does not prove model quality or savings. Any future default
  change requires a bounded, dated calibration artifact with its sample,
  results, decision, and limitations.

## Repository Calibration State

- No repo-specific model benchmark has yet been accepted. Host defaults remain
  the provisional routine configuration.
- The coordinator may choose a specialist tier for shared-contract or
  consequential integration decisions, but must record the task-specific
  reason in the governing plan or runbook.
