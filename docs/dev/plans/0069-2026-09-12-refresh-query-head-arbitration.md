# Plan 0069 | Refresh / Query Head Arbitration

State: CLOSED
Roadmap: P08
Plan version: 1
Date: 2026-09-12
Branch: `fix/refresh-query-head-arbitration`
Target: `main`

## Objective

Make a successfully published ad-hoc refresh query-visible when its immutable
retrieval index is newer than the promoted recurring-tick snapshot, while
preserving the newer tick snapshot as ordinary-query authority.

## Current State

- Plan 0068 proved successful X acquisition and publication, but cache-only
  reads still selected an older recurring-tick snapshot and returned no
  evidence.
- `CacheQueryApplication.query` selects any available tick snapshot before it
  inspects the immutable retrieval head.
- Current installed-source branch `fix/full-tick-recovery` provides service
  0.3.114 and is the qualified base for this successor.

## Scope

- add deterministic application-boundary regressions;
- expose retrieval-head activation metadata through the retrieval backend;
- choose the newest eligible query head by durable publication timestamp;
- retain tick provenance only when the tick snapshot is selected;
- advance the independent service candidate and refresh its exact manifest;
- run focused, affected, packaging, and comprehensive provider-free tests.

## Non-Goals

- no provider retry, schedule change, browser mutation, profile repair,
  production installation, or release action;
- no change to tick construction, source ranking, or evidence scoring;
- no Agent Browser timestamp repair in this plan.

## Acceptance Criteria

1. A newer retrieval head wins over an older tick snapshot and returns its
   matching evidence with the retrieval index version.
2. A newer or equal tick snapshot remains authoritative with exact provenance.
3. Missing retrieval-head metadata preserves compatible tick behavior.
4. Runtime manifest, focused, affected, package, and comprehensive tests pass
   without masking a first failure.
5. Read-only live evidence proves the installed head ordering that the source
   repair would select; installation remains a separate gate.

## Execution Packet

- owner: primary agent;
- write surface: service retrieval/application code, focused tests, service
  version and manifest, this plan, runbook, and one closeout note;
- validation tier: focused, affected service, package, comprehensive;
- terminal condition: source-qualified candidate or one exact blocker;
- overall effort ceiling: one implementation attempt and one repair pass;
- authority classification: `inherited_authority`; this is the requested
  repair after Plan 0068 localized the defect.

Subagent status: `not_spawned`; current orchestration policy prohibits
delegation.

### Checkpoint P0069-C01 | 2026-09-12

State transition: `diagnosed -> source_qualified`.

Progress classification: `outcome_progress`; the later published refresh head
is now selected ahead of an older tick head, with the inverse and compatibility
cases preserved.

Evidence:

- the regression first failed with `tick-snapshot-001` selected instead of
  `index-x-refresh`, then passed after timestamp-based arbitration;
- 59 affected application, retrieval, publication, job-runner, packaging, and
  lifecycle-install tests pass;
- the comprehensive provider-free suite passes when the pre-existing plan
  authority audit is excluded;
- the remaining plan audit reports exactly the two retained Plan 0064 findings
  already recorded by Plan 0066: invalid legacy authority classification and a
  missing Definition Of Done;
- live read-only SQLite head evidence shows retrieval index
  `index-e51e8df608f7374bd1d89b9b` activated at
  `2026-09-12T14:40:57.713486+00:00`, later than tick snapshot
  `tick-snapshot-1182fab1bf8d9b99ef2a22bb91739b87` promoted at
  `2026-09-12T00:11:02.360677Z`;
- installed service 0.3.114 still selects the older tick snapshot, proving the
  remaining gate is installation of source-qualified candidate 0.3.115 rather
  than another X acquisition.

Acceptance reconciliation: criteria 1-5 are satisfied for source
qualification. Production installation and a post-install cache-only read are
explicitly unexecuted.

Next action: review and integrate this branch, then install candidate 0.3.115
under the normal runtime gate and repeat only the cache-only `AI agents` X
readback. Do not issue another provider refresh for this acceptance.
