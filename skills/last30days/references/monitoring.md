# Monitoring reference

Load this reference only when the user explicitly asks to inspect service
health, freshness, coverage, topic/feed state, or a durable job.

Monitoring is read-only:

1. Call `service_info` first and require a compatible client/service result.
2. Use `coverage` for attempted intervals, yield, gaps, and source coverage.
3. Use `maintenance_status` for safe App Intelligence and graph-projection
   readiness plus receipt counts.
4. Use `job_status` only with a job ID supplied by the user or returned by a
   service operation in this conversation.
5. Use `topic` or `collection` only in their list/read form.

Report service health separately from research yield. A ready process with no
new evidence is healthy but did not produce a successful research outcome.

Do not mutate schedules, request new work, resume a job, inspect private
ledgers, or expose implementation details from this reference.
