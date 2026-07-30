# Maintenance reference

Load this reference only for an explicit maintenance, evaluation,
repair-readiness, approval, or release-safety request.

The deterministic service remains authority. Start read-only:

1. Call `service_info`.
2. Call `maintenance_status`.
3. Report supported task contracts, finite ranges, task states, receipt
   counts, projection state, and repair-policy gates.

Ordinary MCP discovery does not authorize starting a model turn, inspecting
private artifacts, changing source configuration, creating a repair branch,
running evaluations, approving a proposal, publishing an index, restarting a
service, or deploying a release.

If a separate operator surface is explicitly supplied, preserve its exact
task, evidence, call, cost, time, branch, test, approval, restart, and
deployment bounds. Model output is a proposal only. The host must validate it,
record a decision, and satisfy every human gate before promotion.

Stop on missing evidence closure, unbounded reservation, nonterminal work,
failed evaluation, ambiguous approval, or any requested action outside the
exposed operator contract.
