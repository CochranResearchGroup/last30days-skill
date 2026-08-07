# Plan 0025 | Facebook agent-browser timeout remediation

State: OPEN
Roadmap: P09
Plan version: 1
Date: 2026-08-07

## Objective

Diagnose the exact retained-browser command that causes Facebook collection to
time out before page readback, implement the narrowest source-owned mitigation,
and prove the repaired Facebook lane live without changing the accepted daily
schedule, source set, credentials, cost posture, or browser identity boundary.

## Current State

- P08/Plan 0024 is closed and the installed service-owned daily schedule is
  enabled and ready for the Aug 8 UTC boundary on service 0.3.5/schema 16.
- The latest five Facebook provider attempts are one `agent_browser_error`
  followed by four `agent_browser_timeout` results. The latest attempt took 38
  seconds, observed zero page signals, persisted no rendered page, and accepted
  zero items.
- A red-capable current-state assertion against the latest Facebook provider
  result exits 1 while its safe error code is `agent_browser_timeout`.
- The retained `stored-last30days-social` browser is live and viable, uses the
  canonical `last30days-facebook` profile, and contains a Facebook search tab.
  A read-only tab inventory succeeds but takes about eight seconds.
- Agent-browser service and remote-view doctors report ready/converged runtime
  state. The installed workstation payload reports a binary provenance
  mismatch, but current runtimes converge on the command on `PATH`; this is a
  maintenance finding, not yet proven causal.

## Scope

- capture operation-level timing for the exact acquisition/auth/navigation
  path without exposing credentials or page content;
- add a deterministic regression at the real adapter seam before changing the
  implementation;
- repair only the Facebook/shared agent-browser command behavior that current
  evidence proves faulty;
- build and install one reviewed service candidate if runtime code changes;
- run at most one bounded live Facebook proof after offline validation;
- preserve and verify daily schedule, disabled legacy specs, database
  integrity, browser/profile reuse, zero cost/model use, and next-boundary
  continuity.

## Non-Goals

- no new source, provider, credential, account, profile, browser process, route,
  cadence, notification, retry fanout, schema, or acquisition architecture;
- no Facebook authentication, checkpoint, or manual operator interaction;
- no repair of unrelated agent-browser retained state or installation drift;
- no change to relevance, timestamp, permalink, or publication quality gates
  unless the timeout diagnosis proves one is directly involved;
- no broad source-suite redesign or reopening of P08/Plan 0024.

## Authority And Gates

- The active user goal, `diagnose, plan a mitigation, execute`, is standing
  authority for ordinary diagnosis, code/test/docs changes, candidate install,
  and one bounded live proof inside this existing source and profile boundary.
- Stop before any login, checkpoint, consent, challenge, new credential,
  duplicate browser/profile lane, destructive cleanup, paid request, external
  communication, or change to the daily schedule.
- Preserve fail-closed provider results. A timeout becoming an auth, challenge,
  integrity, or quality-gate failure is not a successful repair.

## Acceptance Criteria

1. One operation-level reproducer identifies the exact timed-out command or
   proves a specific timeout-budget interaction with current evidence.
2. A regression test at the `CliAgentBrowserClient`/`FacebookScraper` seam goes
   red on the reproduced pattern and green after the mitigation.
3. The mitigation reuses the canonical retained profile/browser and does not
   open a duplicate profile lane or weaken auth/page/quality validation.
4. Focused Facebook, worker, provider, config, and source-log tests pass; wider
   validation is proportional to the touched runtime surface.
5. One bounded live Facebook proof returns a rendered Facebook page signal and
   does not return `agent_browser_timeout`; any accepted items still pass the
   existing quality gate.
6. Installed service readback, schedule identity/cadence/next boundary,
   database integrity, disabled legacy specs, zero cost/model use, and absence
   of a last30days systemd timer remain unchanged except for the reviewed
   service version when installation is required.
7. ROADMAP, RUNBOOK, plan state, receipt, commit, origin state, and compact
   Graphiti memory agree on the terminal outcome or exact remaining blocker.

## Execution Graph And Bounds

| Packet | Outcome | Depends on | Write surface | Terminal condition |
| --- | --- | --- | --- | --- |
| S01 diagnose | Exact timed command and falsified alternatives | current runtime and DB | plan/runbook plus optional sanitized diagnostic artifact | one ranked hypothesis is proven |
| S02 test and fix | Red regression then narrow green mitigation | S01 | Facebook adapter/tests and config docs only if a knob changes | focused suite passes |
| S03 candidate | Reviewed build/install with rollback retained | S02 | version/release artifacts and installed user service | installed readback matches candidate |
| S04 live proof | One bounded Facebook attempt and invariant readback | S03 | governed runtime evidence only | acceptance passes or hard stop |
| S05 closeout | Terminal authorities, receipt, memory, commit/push | S04 | plan/roadmap/runbook/notes/Graphiti | exact readbacks agree |

- Critical-path owner: primary agent; active-agent concurrency is one and no
  subagent is authorized or needed.
- Maximum implementation attempts: 2.
- Maximum review/rework cycles: 1.
- Maximum live Facebook source attempts: 1 after offline validation.
- Maximum diagnostic browser interaction: one tab-select/auth-read sequence,
  restoring the prior active tab when safe.
- Any repeated identical timeout after the one mitigation attempt is a hard
  stop for this execution window, not permission for retry fanout.

## Validation Commands

```bash
uv run pytest tests/test_facebook.py
uv run pytest tests/test_service_worker.py tests/test_service_tick_runner.py
uv run pytest tests/test_source_log_visibility.py
python3 -m compileall -q skills/last30days/scripts/lib
python3 skills/last30days/scripts/service.py status
python3 skills/last30days/scripts/service.py tick schedule status
sqlite3 /home/ecochran76/.local/share/last30days/research.db 'PRAGMA integrity_check;'
```

## Definition Of Done

Plan 0025 closes only when every acceptance criterion has current evidence,
the one bounded live proof no longer returns `agent_browser_timeout`, all P08
schedule and safety invariants remain intact, terminal authorities agree, the
validated slice is committed and pushed to `origin/main`, and one compact
Graphiti episode passes exact readback. A truthful hard stop remains `OPEN`
with the blocker recorded; it is not completion.

### Checkpoint P0025-C01 | 2026-08-07

Plan version: 1

State transition:

- `p08_steady_state_facebook_gap -> facebook_timeout_diagnosis_active`.

Progress classification:

- `outcome_progress`; the repeated transient gap now has a red-capable live
  assertion, ranked falsifiable hypotheses, explicit bounds, and a governed
  remediation path.

Evidence:

- clean `main` at `21ba32d`, matching `origin/main`;
- installed service 0.3.5/schema16 ready; daily schedule enabled/ready for Aug
  8 with no runtime error;
- latest Facebook result `agent_browser_timeout`, 38 wall seconds, zero page
  signals, no rendered page; the fast assertion exits 1;
- retained browser/profile viable and read-only tab inventory succeeds in
  about eight seconds;
- Graphiti discovery returned Plan 0023/0024 and earlier Facebook route history
  as advisory context; current repo/runtime/SQLite evidence is authoritative.

Authority classification:

- `inherited_authority`; the user explicitly authorized diagnosis, mitigation
  planning, and execution within the existing Facebook lane.

Next action:

- time the single bounded tab-select/auth-read sequence, identify the exact
  stall, then add a red regression before implementing the mitigation.
