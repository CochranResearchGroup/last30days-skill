# Plan 0013 | YouTube transcript and media acceptance

State: PLANNED
Roadmap: P02
Date: 2026-07-26
Predecessors: Plans 0004, 0005, and 0011

## Objective

Prove one current YouTube transcript acquisition and one bounded media download
through the installed service, including provenance, the `transcribe-audio`
handoff, and cleanup behavior.

## Current State

- YouTube is acquisition-ready, but the last integrated canary published zero
  items; service health is not current transcript or media yield.
- Transcript fallback and media-capability source exist from Plans 0004 and
  0005.
- Current installed `yt-dlp` PATH visibility, version, real transcript yield,
  downstream handoff, and cleanup remain unproved after reboot.

## Scope

- select one recent video from a configured subscribed channel;
- verify the exact agent-subprocess `yt-dlp` path and version;
- acquire and publish one transcript with immutable provenance;
- download one bounded media item to the governed temporary surface;
- pass the media artifact to `../transcribe-audio` using its documented
  contract;
- verify terminal receipts and cleanup of temporary media.

## Non-Goals

- playlist or channel backfill;
- DRM bypass, account login, cookies export, or age/region-control bypass;
- retaining unbounded media;
- treating binary presence or a zero-yield successful job as acceptance;
- changing transcript semantics or adding a new media provider.

## Dependencies And Owned Surfaces

- Depends on P01 immutable publication and P02 governed acquisition.
- Expected writes are focused YouTube adapter/service tests, configuration docs
  only if a user-facing knob changes, runtime job ledgers, and bounded
  temporary media.
- The downstream `transcribe-audio` repository is read-only unless separately
  authorized.

## Execution Packets

1. Read-only capability and PATH preflight.
2. One transcript acquisition and immutable publication proof.
3. One bounded download, handoff, and cleanup proof.
4. Focused regression validation and durable closeout.

Packets are serialized because they share one source item and provenance chain.

## Bounds And Gates

- maximum implementation attempts per packet: 2;
- maximum review/rework cycles per packet: 1;
- maximum hardening-only checkpoints: 1;
- active-agent concurrency: 1;
- one video, one transcript job, and one bounded media download;
- stop on authentication, access restriction, unsupported media, missing PATH
  gate, provenance break, downstream contract mismatch, or cleanup failure.

## Acceptance Criteria

- the subprocess resolves the intended `yt-dlp` binary and records its version;
- one non-empty transcript publishes with source URL, video identity,
  acquisition, version, sighting, and evidence receipts;
- one bounded media artifact reaches the documented `transcribe-audio`
  handoff;
- temporary media is removed according to policy while durable receipts remain;
- source health, transcript yield, download success, handoff success, and
  cleanup success are reported independently.

## Validation

- focused YouTube, media-capability, publication, and cleanup tests;
- one installed-runtime transcript canary and one bounded media canary;
- planning audit, `git diff --check`, and current service readback.

## Definition Of Done

One current transcript and one bounded media handoff complete with durable
provenance and verified cleanup, with no broad backfill or credential action.
