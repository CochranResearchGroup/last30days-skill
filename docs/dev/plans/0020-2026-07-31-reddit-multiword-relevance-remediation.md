# Plan 0020 | Reddit multiword relevance remediation

State: OPEN
Roadmap: P07
Date: 2026-07-31
Plan version: 1
Predecessor: Plan 0019 checkpoint P0019-C11

## Objective

Fix phrase-aware and multiword relevance offline so the Reddit agent-browser
adapter rejects candidates that match only part of a meaningful multiword
query. Prove the behavior deterministically before requesting or authorizing
any new live-query budget.

## Current State

- Plan 0019 exhausted its six-query matrix and rejected production use.
- `agent browser` and `Claude Code` accepted one-token false positives because
  `RedditBrowserScraper._quality_gate` accepts every relevance score above zero.
- The shared relevance module scores query coverage, informative-token
  coverage, precision, and phrase containment, but exposes no strict
  query-term coverage decision for source adapters.
- Source service 0.2.13 remains uninstalled. No browser session, live Reddit
  request, canary, soak, push, tag, or release is authorized by this plan.

## Scope

Owned write surfaces:

- `skills/last30days/scripts/lib/relevance.py`;
- `skills/last30days/scripts/lib/reddit_browser.py`;
- `tests/test_relevance_core_v3.py`;
- `tests/test_reddit_browser.py`;
- `tests/test_plan_authority_audit.py` for the current active-plan assertion;
- runtime manifest/build artifacts when required by repo checks;
- this plan, `ROADMAP.md`, `RUNBOOK.md`, and one redacted offline receipt.

## Non-Goals

- changing global relevance thresholds or ranking semantics for other sources;
- requiring exact phrase adjacency or original token order;
- redesigning Reddit extraction, routing, browser isolation, or fallback order;
- running Reddit/browser traffic, installing 0.2.13, or starting a canary;
- pushing, tagging, publishing, or releasing.

## Contract

- A query term is one non-stopword lexical token before synonym expansion.
- A term is covered when the candidate contains that literal token or one of
  its configured synonyms.
- Multiword Reddit browser queries require 100% query-term coverage across the
  normalized title and body. Terms may be separated or reordered; an exact
  phrase remains higher-scoring but is not mandatory.
- Single-term and stopword-only scoring behavior remains unchanged.
- A zero-overlap candidate remains `off_topic`; a partial multiword match is
  rejected as `partial_query_match` for operator visibility.
- The shared scorer's numeric semantics remain unchanged for existing callers;
  the new strict decision is opt-in at the Reddit browser adapter seam.

## Test-Driven Packets

1. `RED/GREEN A`: expose query-term coverage and prove literal full, partial,
   reordered, case/punctuation, stopword, and synonym-backed coverage.
2. `RED/GREEN B`: exercise `RedditBrowserScraper.search` and prove the two Plan
   0019 false-positive shapes are rejected while full multiword and single-word
   posts remain accepted.
3. `REFACTOR`: keep query tokenization and synonym logic inside the relevance
   module; do not duplicate it in the adapter.
4. `VALIDATE`: run focused tests, combined Reddit/worker tests, compilation,
   runtime package/build checks, the complete Python suite, Go MCP suite,
   `git diff --check`, CodeGraph impact review, and plan-authority audit.

Each RED/GREEN packet has one implementation attempt. One consolidated review
and one bounded remediation pass are allowed.

## Acceptance Criteria

- `agent browser` rejects candidates containing only `agent` or only `browser`;
- `Claude Code` rejects candidates containing only `Claude` or only `Code`;
- full terms pass when adjacent, separated, reordered, differently cased, or
  punctuated;
- a configured synonym can satisfy its original query term without requiring
  every expanded synonym token;
- stopwords do not create impossible coverage requirements;
- single-term Reddit relevance remains compatible;
- diagnostics distinguish partial-query rejection from zero overlap;
- all validation gates pass with zero browser/network traffic;
- source service 0.2.13 remains uninstalled and no new live-query budget is
  requested or implied.

## Hard Stops

Stop without live traffic on:

- a required change to global relevance thresholds for unrelated sources;
- a regression in single-term or synonym behavior;
- a required schema, service, browser, credential, paid-source, or runtime
  mutation;
- a second failed implementation attempt or failed bounded re-review;
- an unsafe or overlapping dirty worktree.

## Work Units And Authority

Critical-path owner: primary agent. No subagent is used because the change is a
small, tightly coupled TDD slice and live work is prohibited.

Authority classification: `inherited_authority` from the user's explicit goal
to fix phrase-aware/multiword relevance offline. Any live query, installation,
push, tag, or release requires separate authority.

## Definition Of Done

Close `CLOSED` only when every acceptance criterion has current deterministic
evidence, the full affected validation surface passes, the receipt and
roadmap/runbook are current, a compact Graphiti checkpoint is verified, and no
live or installed-runtime mutation occurred.

### Checkpoint P0020-C01 | 2026-07-31

Plan version: 1

State transition: `PLANNED -> OPEN`

Progress classification: `outcome_progress`

Evidence:

- Plan 0019 receipt identifies one-token multiword false positives as the
  failed production-acceptance criterion;
- CodeGraph traces Reddit browser acceptance through `_quality_gate` to
  `token_overlap_relevance` and confirms the adapter currently accepts every
  score above zero;
- current worktree was clean at successor start.

Subagent status: `not_spawned`.

Graphiti write status: pending validated implementation closeout.

Authority classification:

- `inherited_authority`

Next action: execute RED/GREEN packet A without network or browser traffic.
