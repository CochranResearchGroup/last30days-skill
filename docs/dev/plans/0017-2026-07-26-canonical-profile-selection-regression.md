# Plan 0017 | Canonical profile-selection regression

State: PLANNED
Roadmap: P03
Date: 2026-07-26
Predecessors: Plans 0006 and 0011

## Objective

Make service-plus-target identity the fail-closed canonical profile-selection
contract and prevent duplicate-name or fuzzy catalog matches from selecting an
unrelated browser profile.

## Current State

- Current identity-specific X, Facebook, and LinkedIn lookups select
  `last30days-facebook` through `authenticatedServiceIds`.
- Earlier free-text/fuzzy lookups could rank unrelated custom profiles.
- The current corrected runtime behavior needs deterministic regression
  coverage across exact selection, ambiguity, and no-match outcomes.

## Scope

- inventory the profile-selection inputs and ownership boundary with CodeGraph;
- add fixtures for exact service-plus-target identity, duplicate display names,
  fuzzy near-matches, missing identity, and conflicting identity metadata;
- assert exact canonical selection only when identity evidence agrees;
- assert typed ambiguity or `not_found` with zero fallback selection otherwise;
- verify X, Facebook, and LinkedIn share the contract without provider-specific
  widening.

## Non-Goals

- deleting, renaming, migrating, or merging live profiles;
- launching a browser, operating a route, or probing authentication;
- changing account credentials or `authenticatedServiceIds`;
- ranking cleanup outside the identity-selection boundary.

## Dependencies And Owned Surfaces

- Depends on the agent-browser expert/profile-routing contract from Plan 0006.
- Expected writes are the narrow last30days profile-selection adapter/helper,
  fixtures, focused tests, and configuration docs only if a user-facing rule
  changes.
- Cross-repository agent-browser changes require a separate authorized plan in
  that repository.

## Execution Packets

1. Use CodeGraph to locate selection ownership and impact.
2. Add failing identity, ambiguity, and no-fallback tests.
3. Implement the narrowest fail-closed correction if current code fails.
4. Run focused and full regression validation and document the contract.

## Bounds And Gates

- maximum implementation attempts per packet: 2;
- maximum review/rework cycles: 1;
- maximum hardening-only checkpoints: 1;
- active-agent concurrency: 1;
- one selection boundary and no live profile mutation;
- stop if the fix requires agent-browser source changes, profile migration, or
  a broader catalog/ranking redesign.

## Acceptance Criteria

- exact service-plus-target identity selects the canonical profile;
- duplicate display names and fuzzy near-matches cannot override identity;
- missing or conflicting identity returns typed ambiguity or `not_found` and
  selects nothing;
- X, Facebook, and LinkedIn fixtures exercise the same fail-closed contract;
- diagnostics explain selection class without credentials or private browser
  data.

## Validation

- CodeGraph impact read before source edits;
- focused profile lookup/selection tests followed by the full relevant suite;
- no-navigation installed lookup readback for each service;
- planning audit and `git diff --check`.

## Definition Of Done

Deterministic tests and installed readbacks prove canonical identity-first
selection and zero fuzzy fallback under ambiguity, without mutating live
profiles or browsers.
