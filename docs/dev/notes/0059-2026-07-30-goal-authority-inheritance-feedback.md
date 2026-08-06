# Note 0059 | Goal Authority Inheritance Feedback | 2026-07-30

## Policy Source

- Installed selector bundle: `repo-policy-selector` `v0.1.14`
- Source commit: `b3fdcccf8a36a3eef596a1a35b2084c8c51ff254`
- Policy library SHA-256:
  `089536f36ee74a741adf2488571a34a5418131347af4a4df258fa0cfdef1f203`
- Current deterministic profile recommendation: `repo-product-engineering`
- Recommendation mode: `patch-missing`
- Local module override: `goal-execution-governance`

## Observed Friction

Plan 0018 authorized a long-running objective and bounded execution packets.
After one public Reddit remediation returned zero items, its packet-level
`no retry` language was interpreted as revoking the whole goal's standing
authority. A second packet with the same source, public data class, budgets,
mutation class, and acceptance criterion was unnecessarily escalated to the
operator.

The ambiguity came from treating three distinct concepts as equivalent:

- stopping the current attempt;
- exhausting the goal's configured attempt ceiling;
- crossing a human-approval boundary.

Only the first occurred. The successor was attempt two of the repo's configured
two-attempt limit and changed only the topic selector.

## Local Decision

The local goal policy now says:

- a hard stop ends the current attempt and requires a checkpoint;
- standing goal authority continues for a bounded successor that preserves the
  objective and risk envelope;
- `no retry` applies to the packet instance unless the plan explicitly names a
  `human_gate` or revokes standing authority;
- an agent must cite the exact crossed boundary before requesting approval;
- human approval remains mandatory for scope expansion, new systems or private
  data, ceiling increases, consequential external effects, named gates,
  repeated failure at the configured bound, and unapproved immutable actions.

Plan 0018 checkpoint P0018-C15 applies this classification without weakening
its public-only limits, second-attempt ceiling, independent review, or release
gate.

## Upstream Candidate

The shared `goal-execution-governance` module should distinguish:

1. packet termination;
2. bounded successor authority;
3. explicit human gates.

That distinction would prevent approval mazes while retaining drift protection.
The exact local wording should undergo upstream review rather than being copied
blindly because repositories differ in live-write, privacy, financial, and
publication risk.
