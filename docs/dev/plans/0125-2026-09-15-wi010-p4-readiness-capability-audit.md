# Plan 0125 | WI-010 P4 Readiness Capability Audit

State: OPEN
Lane: P53
Work item: WI-010
Branch: feat/wi010-p4-readiness-preflight-v1
Target: main
Integration: merge
Roadmap: P53
Plan version: 1
Date: 2026-09-15
Execution owner: /root
Coordination owner: /root
Requested model route: host default, no delegation
Effective runtime model: not exposed

## Objective

Determine which of WI-010's eight acquisition adapters has a truthful
readiness-only seam, implement a provider-free sealed P4 preflight contract,
and emit an independently verifiable capability receipt without resolving a
credential, acquiring a real browser, or contacting a provider.

## Current State

Plan 0124's P0-P3 campaign is integrated at `72f1c744`. The architecture
defines P4 as one explicitly granted remote/auth probe for one exact
route/profile. No P4 executor, external grant, credential-profile reference,
or remote readiness receipt exists.

## Definition Of Done

The repository contains an exact eight-adapter capability matrix, a pure
preflight that rejects unsupported adapters and non-exact profile references,
an effect-free audit CLI, a durable independently verifiable receipt, focused
tests proving the external-effect boundary, and truthful authority projections.

## Scope

- classify all eight production adapters from their current request/auth flow;
- distinguish a readiness-only seam from a content-fetching path;
- seal exact adapter/provider/profile/expiry/budget grants without resolving
  the profile or dependency;
- emit and verify a source-bound capability receipt;
- recommend one later P4 pilot only when its exact profile reference is
  supplied under separate authority.

## Non-Goals

No environment or secret-store lookup, credential validation, browser
workspace acquisition, browser action, DNS, socket, HTTP, subprocess, provider
call, P4 execution, P5 canary, retry, installed-runtime mutation, schedule,
release, deployment, issue mutation, or Graphiti write.

## Capability Hypothesis

| Adapter | Existing separable seam | Audit expectation |
|---|---|---|
| `x_agent_browser` | browser workspace plus `inspect_auth` before search | eligible only with an explicit opaque profile reference |
| `facebook_agent_browser` | retained/fresh-target auth inspection before search | eligible only with an explicit opaque profile reference |
| `linkedin_agent_browser` | browser auth inspection before post search | eligible only with an explicit opaque profile reference |
| `linkedin_profile_agent_browser` | same auth inspection before profile acquisition | eligible only with an explicit opaque profile reference |
| `reddit_agent_browser` | browser auth inspection before search/feed extraction | eligible only with an explicit opaque profile reference |
| `youtube_ytdlp` | `yt-dlp` search immediately fetches content | no readiness-only seam |
| `reddit_keyless` | public search immediately fetches content | no readiness-only seam |
| `reddit_scrapecreators` | key presence plus paid content request | no auth/readiness-only seam |

## Frozen Preflight Contract

1. The catalog contains exactly the eight Plan 0124 adapter IDs and binds the
   production source files used to justify each classification.
2. Audit and verification import no production adapter and resolve no
   executable, environment variable, profile, credential, browser, or network.
3. A readiness plan may select exactly one eligible case. It rejects empty,
   default, filesystem, URL, secret-like, or multi-profile references.
4. The grant binds the sealed plan digest, provider, adapter, case ID, opaque
   profile reference, expiration, attempt count one, external concurrency one,
   and explicit action/request/time/cost ceilings.
5. This packet emits `AUDITED_NOT_RUN`; neither preparation nor receipt
   verification can emit a P4 readiness verdict.
6. Every unsupported or not-yet-authorized case retains its exact blocker.

## Validation

- focused unit tests for exact catalog coverage, classification, sealing,
  tamper detection, profile-reference rejection, expiry, and budgets;
- an effect tripwire that fails on environment access, executable resolution,
  subprocess, browser dependency import, DNS, socket connect, or URL open;
- CLI audit and offline verification agree on the durable receipt;
- provider-acceptance and authority regression suites pass;
- `git diff --check` and deterministic authority audit pass.

## Acceptance Criteria

1. All eight adapters receive one evidence-backed classification.
2. The receipt independently verifies from sealed metadata and source digests.
3. Every possible external effect remains zero and P4 is not claimed.
4. The next gate names the missing exact profile/authority input rather than
   silently selecting or resolving one.

## Stop Rules

Stop before reading environment variables, resolving a credential/profile,
checking an installed executable, acquiring or inspecting a real browser,
opening DNS/socket/HTTP, or executing any provider-shaped subprocess. Stop if
the source does not support a readiness-only claim without content retrieval.

## Next Action

Implement the pure capability catalog, plan/grant sealer, effect-free audit
receipt, verifier, CLI, and tests. Execute only that provider-free audit.

### Checkpoint P0125-C01 | 2026-09-15

Plan version: 1

State transition: `unplanned -> OPEN`.

Progress classification: `outcome_progress`; current production flows have
been structurally audited and the implementation packet is frozen.

Authority classification:

- `inherited_authority` from the operator's provider-free planning and
  execution instruction.

Owned changes:

- registered Plan 0125, P53 custody, WI-010 linkage, roadmap state, and the
  provider-free stop boundary.

Validation evidence:

- CodeGraph covered all eight adapter entries and found five browser-auth
  seams plus three content-fetch-only seams;
- current canonical `main` and `origin/main` agreed at `c315eaca` before the
  branch was created.

Subagent status and reconciliation:

- `not_spawned`; direct graph exploration was sufficient.

Graphiti write status:

- `not_written`; no memory write was authorized.

Remaining acceptance criteria:

- implement, execute, verify, and independently audit the provider-free
  capability receipt.

Next action:

- implement the frozen contract and stop before any P4 external effect.
