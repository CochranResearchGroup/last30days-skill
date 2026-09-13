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
- Select model, reasoning effort, context scope, and delegation topology together to minimize total allocation consumed per accepted milestone while meeting required correctness, safety, and delivery-time constraints. Count orchestration, workers, failed attempts, evaluation, repair, and integration. Treat token counts and API-price estimates as labeled proxies when measured allocation is unavailable.
- Define the milestone before routing substantial work. It must describe usable behavior at its intended integration boundary and a stable acceptance check. Worker completion, prerequisite repair, passing unrelated tests, and document volume do not establish milestone completion.
- Keep a dated repo-local mapping from task tiers to available model and reasoning configurations. Start routine work on the calibrated economical default; use a cheaper tier for mechanical, readily verified work; route material policy design, architectural tradeoffs, or difficult consequential reasoning directly to a designated specialist tier when justified. Select reasoning effort separately. Model novelty and task length alone do not justify an upgrade.
- Reassess routing at non-trivial task start, material replanning, failed acceptance, conflicting evidence, and the configured no-progress interval. Reassessment is a brief primary-agent decision within the existing checkpoint; it does not itself require another model call. Distinguish reasoning limits from missing inputs, authority, unavailable tools, and environmental failure.
- Escalate only when stronger reasoning is likely to resolve a specific obstacle. Delegate the smallest useful decision or diagnostic task with evidence, attempted approaches, acceptance check, write scope, remaining budget, and stop condition. Return ordinary execution to its configured default when that task concludes. Record requested and runtime-reported effective model and effort; report unknown effective configuration explicitly.
- Model upgrades, reasoning changes, prompt edits, tool substitutions, successor plans, and worker replacement inherit cumulative milestone accounting. Reassessment intervals are not renewable budgets. Exhaustion cannot be bypassed by renaming an approach or opening another worker.
- Delegate when expected gains in expertise, independence, context isolation, or elapsed time justify setup and reconciliation cost. Do deterministic mechanical work with existing tools before purchasing model work for it. A compact specialist brief is preferred when full-history inheritance adds no value. The primary integrates returned evidence without repeating the worker's investigation.
- Route polling, hashing, schema checks, counter reconciliation, deterministic
  test execution, and exact structured transformations to tools before any
  model. When judgment-light work still needs a model, use the calibrated
  economical tier with a narrow input packet, structured output, deterministic
  verifier, attempt/time bound, and no authority to change scope or acceptance.
- Retain causality decisions, safety or authority changes, material experiment
  design, architectural tradeoffs, and the final acceptance claim with the
  primary or a justified specialist tier. Do not pay a stronger model to repeat
  verified mechanical work returned by a cheaper worker.
- Calibrate complete workflows, not isolated responses. Before starting, freeze representative inputs, acceptance checks, baseline and candidate configurations, quality floor, sample size, retry allowance, resource ceiling, evaluator, and promotion/stop rules. Include failed and timed-out attempts, retain difficult regressions, and use held-out examples when tuning on earlier samples.
- Record the sample/date, workload identity, model and effort, context and tools, topology, accepted count and denominator, defects, interventions, elapsed time, cumulative agent effort, and measured allocation or labeled proxy. Keep elapsed wall time separate from summed worker effort. Do not attribute shared-account consumption to one configuration when concurrent use prevents attribution.
- Stop calibration at its predeclared sample or resource ceiling, or at a defined critical-quality failure. Small samples yield provisional routing only. Do not enlarge the experiment, weaken acceptance, or retry away failures to obtain a favorable result.
- Promote the least costly configuration that meets frozen quality and delivery requirements. An expensive configuration must show a task-relevant benefit that justifies its added consumption. Revert a regressed default promptly and retain specialist use only where justified. Recalibrate after material configuration changes or repeated observed failures with a bounded scheduled sample, not before every task.
- Deterministic audits establish wiring and record validity; they do not prove model quality, allocation savings, or runtime stopping. Repos that operate a controller must test aggregate counters and stop behavior at its real transition boundary. Policy-only adoption must identify calibration and runtime enforcement as unverified.

## Repository Calibration State

- No repo-specific model benchmark has yet been accepted. Host defaults remain
  the provisional routine configuration.
- The coordinator may choose a specialist tier for shared-contract or
  consequential integration decisions, but must record the task-specific
  reason in the governing plan or runbook.
