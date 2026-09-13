<!-- last30days-work-item:WI-005 -->
# Extend tailored follows across supported services

State: TRIAGE
Priority: P2
Lane: Follows
Parent: WI-000
Blocked by: WI-004

## Problem

An X-only follow design would force later services into accidental semantics or
duplicate scheduling and provenance concepts inconsistently.

## Outcome / Proposed Solution

The accepted follow contract supports service-native targets such as Reddit
communities or users and YouTube channels without erasing their distinct
identity, authorization, and collection semantics.

## Acceptance Evidence

- shared fields remain provider-neutral while each target kind retains exact
  service-specific identifiers and validation;
- capability discovery reports supported target kinds and unavailable
  operations truthfully;
- schedules, receipts, provenance, pause/resume, and query filtering behave
  consistently across fixture-backed adapters;
- unsupported or unauthorized services fail closed without widening scope;
- migrations preserve accepted X follow identity and history.

## Non-Goals

No promise that every service supports lists, accounts, or the same cadence;
no live provider onboarding without separate authority.
