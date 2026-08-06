# Fresh-agent handoff | Plan 0023 goal-worthy all-source tick

Date: 2026-08-06  
Repository: `/home/ecochran76/workspace.local/last30days-skill`  
Branch: `main`  
Pre-handoff base: `0f34ad0a015c4660d271faed01bea8b13612d710`

## Purpose

Continue Plan 0023 from its reviewed service 0.3.1 candidate without creating
another chain of install/preflight/canary micro-approvals. The operator rejected
that approval granularity and asked for one goal-worthy authority packet.

This note is a routing document. The current plan, roadmap, runbook, receipts,
commits, user-scoped config, and fresh runtime readbacks remain authoritative.

## Authority order

Read these before acting:

1. `AGENTS.md` and relevant modules under `docs/dev/policies/`;
2. `docs/dev/plans/0023-2026-08-04-durable-all-source-intelligence-tick-mvp.md`,
   especially C36-C40;
3. `ROADMAP.md` P07 and the latest `RUNBOOK.md` turn;
4. `docs/dev/notes/0053-manual-t08-live-packet-independent-review-receipt.json`;
5. `docs/dev/notes/0054-service-0.3.1-target-order-candidate-receipt.json`;
6. `docs/dev/notes/0052-manual-t08-live-packet.json` and terminal review
   `docs/dev/notes/0055-service-0.3.1-target-order-independent-review-receipt.json`;
7. current Git, installed service, SQLite, user-config digest/modes, timer, and
   artifact readbacks.

Do not reconstruct exact identities or historical findings from chat when the
receipts above already bind them.

## Approval status: do not overstate it

The broad goal below is a **draft awaiting explicit operator approval**. It was
proposed after the operator rejected the granular install gate, but the
operator did not subsequently say that the goal was approved. The last approved
mutation was the owner-private Plan 0018 config derivation and sanitized
preflight. Do not install 0.3.1 or start a live tick merely from this handoff.

Ask once for this goal-level authority:

> Deliver the production-ready first MVP all-source tick end to end. Install
> and reconcile the reviewed runtime; execute, diagnose, repair, and revalidate
> bounded manual ticks within the existing cumulative 50-provider-attempt
> ceiling; prove durable raw evidence, OCR and semantic image sidecards,
> cataloging, hybrid retrieval, incident capture, and independently
> reconstructable receipts; escalate genuine CAPTCHA, Cloudflare, rate-limit,
> or reauthentication incidents through configured sequential notifications;
> use Guac only when human observation is actually needed; and push the
> reviewed repository result to `origin`. Keep timers disabled. Stop only for
> human interaction, a new credential/source/data class, paid spending, the
> 50-attempt ceiling, or a materially different objective.

If approved, treat it as standing authority for ordinary installs, restarts,
transactional rollback, sanitized preflights, bounded manual ticks,
deterministic diagnosis/repair, validation, independent review, and final push
inside that objective and cumulative ceiling. Do not ask again merely because
one bounded attempt fails or an implementation detail changes.

The current user config still governs exact services, targets, profiles,
selectors, provider types, per-tick ceilings, artifacts, analysis, and
notification particulars. Repository machinery must remain generic. Timer
admission remains a separate later goal even if the manual tick succeeds.

## Current verified state

- Clean local `main` at pre-handoff base `0f34ad0`, 35 commits ahead of
  `origin/main` and zero behind. Nothing from this campaign has been pushed.
- Installed service is active/ready 0.3.0, schema 15, manifest
  `da005555f45fc86a54013821900049cca7320df4d8966930f8fee9c1d167b514`.
- Database integrity is `ok`; active index
  `index-d4b3c45667cc2f635c557b85` has 62 documents and 62 embeddings.
- There are zero service ticks and zero queued/running tick attempts.
- There are 42 collection specifications and zero enabled. No last30days
  systemd timer exists.
- Owner-private config directory/file modes are 0700/0600. File SHA-256 is
  `66b81392f8ab8092d5af2757a4764ddb0944e6a0aa212de0f375906a6412ba98`.
  Do not read or copy its particulars into repo data.
- Reviewed candidate service 0.3.1 implementation commit is `51b4401`; exact
  artifact SHA-256 is
  `54e53ca8a1bb3172edb14cb66909dc2028d2d80e8b8906bc4064dbf92b981fe5`
  and manifest SHA-256 is
  `6e105eecbd3b1fcd84a48cbf9d4d5a73b6789fe91b3ad715c539568436d64504`.
- Reworked packet 0052 SHA-256 is
  `2895084f69cb339df3a72b0a92119123adcf7621a84b838e78f3b7e07b7131a0`.
  Terminal review 0055 passes with no critical finding.

## What completed

- Plan 0018's five-source user config was derived owner-privately and passed
  installed 0.3.0 sanitized preflight without creating a tick or live side
  effect.
- The first T08 packet failed independent review because runtime execution was
  lexicographic rather than the accepted configured order and because two
  evidence bindings were incomplete. Receipt 0053 is the accepted finding set.
- Service 0.3.1 now preserves frozen target-array order through preflight,
  receipt reconstruction, execution, and replay. The repair kept the existing
  tick interface and added no schema field, retry, source, credential, or timer.
- Primary validation passed 2,537 tests, 7 skipped, and 6 subtests. Final
  independent review reran 88 focused tick tests and 7 package/release tests,
  reproduced the exact 129-entry artifact, and passed packet/privacy/gate
  review.
- Plan 0018 order is Reddit, YouTube, X, Facebook, LinkedIn. Per current config,
  one tick remains serial with aggregate limits 5 attempts, 250 governed
  requests, 15 items, 600 wall seconds, zero cost, and zero model tokens.

## Remaining outcome

After goal approval, carry the first MVP to a truthful terminal outcome:

1. reconcile fresh state and transactionally install exact service 0.3.1;
2. prove postinstall readiness/integrity/rollback and rerun one sanitized
   preflight for the frozen tick identity;
3. execute and monitor bounded manual all-source ticks under the goal's
   cumulative ceiling, repairing deterministic defects under standing
   authority rather than requesting successor micro-approvals;
4. require durable incidents for CAPTCHA, Cloudflare, rate-limit, or reauth
   conditions, protected screenshot plus rendered-page evidence, and configured
   sequential notification;
5. acquire/provide a Guac lease only when a human actually needs to observe;
   the handoff must be a direct external agent-browser URL, never a local link;
6. independently reconstruct and review the terminal tick, including raw
   evidence, OCR/sidecards, catalog, lexical/semantic snapshot, coverage,
   budgets, incidents, artifacts, and final state;
7. push the reviewed repo result to `origin`; leave every schedule/timer off.

`complete_degraded` is acceptable only when source-local failures, coverage,
freshness, and incidents are exact and global integrity holds. Green tests or
a healthy install alone do not complete the goal.

## Read-only startup commands

```bash
cd /home/ecochran76/workspace.local/last30days-skill
git status --short --branch
git rev-list --left-right --count origin/main...HEAD
git log -8 --oneline --decorate
python3 dev/last30days/scripts/audit_plan_authority.py

~/.local/share/last30days/service/last30days-service status
~/.local/share/last30days/service/last30days-service collection list
sqlite3 -readonly ~/.local/share/last30days/research.db \
  "PRAGMA integrity_check; SELECT COUNT(*) FROM service_ticks; SELECT COUNT(*) FROM service_tick_attempts WHERE state IN ('queued','running');"
stat -c '%a %n' ~/.config/last30days ~/.config/last30days/tick-config-v1.json
sha256sum ~/.config/last30days/tick-config-v1.json \
  dist/service/last30days-service-0.3.1.tar.gz \
  service/runtime-manifest.json \
  docs/dev/notes/0052-manual-t08-live-packet.json
systemctl --user list-timers --all --no-pager --plain
```

Do not print the owner-private config or `.env` content. If source, installed,
database, config-digest, artifact, plan, or remote state differs, reconcile the
drift read-only before asking for or consuming goal authority.

## Hard stops after goal approval

Stop and escalate only when:

- actual human interaction is required;
- a new credential, source, tenant, audience, access partition, private-data
  class, or paid provider/model would be introduced;
- cumulative provider attempts would exceed 50, or current user-config ceilings
  would be exceeded without an explicitly reviewed config revision;
- the objective would expand to timer enablement, autonomous video
  transcription/analysis, publication/release, or another materially different
  product outcome;
- database/index integrity, immutable evidence, access isolation, protected
  artifacts, incident notification, or reconstructable receipts cannot be
  preserved;
- repeated failure/no-progress reaches the plan's bounded rework threshold.

Do not stop merely for an ordinary install, preflight, deterministic defect,
source-local failure, bounded successor, rollback, review, or final push that
stays within the approved goal.

## Suggested skills

- `last30days:repo-policy-selector` at the start of the implementation turn;
- `codegraph-workspace` for structural code questions before native search;
- `tdd` and `codebase-design` for any deterministic implementation repair;
- `agent-browser` only when browser runtime diagnosis or an actual observation
  gate is reached; no Guac lease during ordinary acquisition;
- `slack-receipts-orchestrator` only for read-only notification readiness or
  governed incident machinery, never ad hoc recipient handling;
- `handoff` if the goal crosses another context boundary.

## Best next action

Verify the read-only startup state, then ask the operator once for the exact
goal-level authority above. If approved, execute through independently reviewed
manual-tick completion and push without reopening granular approval loops.
Keep timer admission for the next goal.
