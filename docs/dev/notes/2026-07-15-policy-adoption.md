# Policy Adoption | 2026-07-15

## Source

- Selector bundle: `repo-policy-selector` `v0.1.13`
- Source commit: `b38c90694e15562819d28a4338c5d148dc5171fd`
- Policy library SHA-256: `2bc6622358be86d910b7fc404cac93df0d0b495ae904d44a4a5a0956355fec09`
- Selected profile: `standalone-library`

## Decision

Adopted the complete recommended profile under `docs/dev/policies/`:

- planning discipline
- policy management, upgrades, and adoption feedback
- graph-backed memory and CodeGraph usage
- Git worktree, commit history, branch integration, and push cadence
- versioning and release
- turn closeout, validation, and handoff
- upstream fork maintenance

No recommended modules were deferred, retired, or locally overridden.

## Fit Review

The deterministic adoption preserved the existing `AGENTS.md` package boundary,
slash-command orientation, validation commands, security rules, configuration
contract, and beta-channel guidance. It added a policy loading contract and
references to the durable policy files without replacing repo-specific guidance.

The repo does not use canonical `ROADMAP.md` or `RUNBOOK.md` governance. The
standalone-library profile's bounded planning policy applies when substantive
plans are needed, but the stricter roadmap/runbook contract is intentionally not
installed.

The live remote layout required one local clarification: `origin` is the public
CochranResearchGroup fork, while `upstream` is the non-pushable mvanhorn source.
Work is pushed to the fork without opening pull requests against upstream.

## Feedback

The initial selector and draft writer completed cleanly. On the unmodified repo,
profile selection correctly recognized a library-style package and downstream
fork. After adoption, however, a second selector pass treated language introduced
by the installed policies and this note as new product-engineering signals. It
changed the recommendation to `repo-product-engineering`, proposed six additional
modules, and reported roadmap/runbook gaps. This makes automatic post-adoption
selection non-idempotent. The original clean-repo classification remains the
adoption authority; the recursively inferred modules were not installed.

The planning-contract audit also reports missing `ROADMAP.md`, `RUNBOOK.md`, and
`docs/dev/plans/` even when the selected lightweight profile intentionally omits
roadmap/runbook governance. Future selector tooling should exclude installed
policy text from purpose detection and make the planning audit profile-aware.

Keep the detailed package, harness, credential, and release constraints local to
this repo. The shared module content needs no change; the selector's post-adoption
signal filtering and the audit's profile awareness warrant upstream fixes.
