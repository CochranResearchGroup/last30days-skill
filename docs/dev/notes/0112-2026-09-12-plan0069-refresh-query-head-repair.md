# Plan 0069 Refresh / Query Head Repair Receipt

Date: 2026-09-12
Branch: `fix/refresh-query-head-arbitration`
Base: `1acdba8cd2e8d3112cf6bf154cc96280383750bf`
Candidate service: `0.3.115`

## Diagnosis

The successful X refresh and recurring tick publish into two immutable query
heads. `CacheQueryApplication.query` unconditionally chose a promoted tick head
whenever one existed, even when the general retrieval head was published later.
The later refresh therefore remained invisible until another recurring tick.

## Repair

- `HybridRetriever.current_metadata` exposes the active retrieval index and its
  durable activation timestamp.
- query arbitration compares that timestamp with tick `promoted_at` and chooses
  the later head.
- tick metadata is returned only when the tick head actually wins.
- missing retrieval metadata preserves the prior compatible tick behavior.
- service candidate 0.3.115 and its canonical runtime manifest contain the
  repair.

## Validation

- red regression: expected `index-x-refresh`, observed `tick-snapshot-001`;
- focused and affected tests: 59 passed;
- release, runtime package, and lifecycle install tests: 23 passed;
- comprehensive provider-free suite excluding the known plan-authority test:
  passed with no retry;
- Rust-independent live readback: installed 0.3.114 remains ready, but selects
  the older tick head despite a retrieval head published more than 14 hours
  later.

The comprehensive first run also exposed one version assertion updated for
0.3.115 and the two pre-existing Plan 0064 audit findings retained by Plan
0066. No provider, browser, profile, schedule, tenant, or production runtime
mutation occurred.

## Remaining Gate

Integration and production installation are not implied by source
qualification. After installation, perform one cache-only X read. Evidence
yield and correct head selection remain separate acceptance statements.
