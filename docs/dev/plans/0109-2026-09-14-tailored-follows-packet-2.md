# Plan 0109 | Tailored Follows Packet 2

State: PLANNED
Lane: P35
Work item: WI-004
Branch: feat/x-tailored-follows-v2
Target: main
Integration: merge
Roadmap: P35
Plan version: 1
Date: 2026-09-14
Requested model route: gpt-5.6-terra, medium reasoning
Effective runtime model: unknown until reported

## Objective

Complete WI-004 Packet 2 by carrying immutable tailored-follow collection
context through typed X account acquisition and publication, with provider-free
success and failure fixtures and general-feed separation.

## Current State

Packet 1 is integrated at `87858934` with compatible purpose, attention,
lifecycle, typed target, inactive creation, migration, and archive semantics.
No job, browser, schedule, or provider was activated. This packet has not
started.

## Scope

- propagate frozen collection revision, typed target, cause, limits, and access
  partition through work, acquisition, and publication contracts;
- route X account work explicitly without flattening identity into query text;
- publish multi-cause sightings idempotently while keeping general feed and
  account routes distinct;
- test success, malformed identity, unavailable/unknown target, authentication,
  rate limit, timeout/network bound, replay, and overlapping sightings using
  recorded or synthetic fixtures only.

## Non-Goals

- no X list browser route, scheduler-attention closure, live profile/browser,
  installed database/runtime, schedule activation, provider call, canary,
  release, staging, or production;
- no WI-005 cross-service implementation.

## Acceptance Criteria

1. Account work reaches only its typed adapter with the exact frozen collection
   revision, target, bounds, and access partition.
2. Fixture outcomes preserve truthful success, zero-yield, unavailable/unknown,
   auth, rate-limit, timeout, and replay semantics.
3. One post observed through feed and account is stored once per content version
   with both collection causes retained.
4. Legacy/general collection behavior and focused migration/publication suites
   remain green without a real browser or provider.
5. The accepted branch is published for coordinator review without external
   runtime or schedule effects.

## Definition Of Done

All five criteria pass at one published checkpoint suitable for reviewed PR
integration, or one exact blocker is recorded without beginning Packet 3.

## Stop Rules

- stop before list routing, live X, browser/profile, schedule, installed runtime,
  issue, release, staging, or production effects;
- stop and notify the coordinator before conflicting shared search or generated
  contract edits.
