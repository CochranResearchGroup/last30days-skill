# Administration reference

Load this reference only for an explicit request to govern a service-owned
topic, collection, refresh, or waiting job.

## Authority order

1. Call `service_info` and require compatibility.
2. Read the current object with `topic`, `collection`, or `job_status`.
3. State the exact intended mutation, target identifier, and bounded effect.
4. Use only the operation and fields exposed by current MCP discovery.
5. Read the resulting object or job and report its durable state.

## Allowed governed actions

- request one `refresh` for a stated topic and poll its returned job;
- create or update a scheduled topic through `topic`;
- create, update, pause, resume, or manually enqueue one recurring
  specification through `collection`;
- after the user completes a required human action, resume only the exact
  `awaiting_operator` job when the exposed product contract provides that
  action.

Never broaden a target, invent an identifier, bypass an attempt limit, or
present a queued/running job as complete. Stop on incompatibility,
authorization failure, ambiguous target, or a state transition not advertised
by the service.
