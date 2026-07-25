# Policy | Graph-Backed Memory Usage

## Policy

- Treat graph-backed memory as durable retrievable context, not as a scratchpad for every turn.
- Use graph-backed memory for compact, stable cross-turn facts such as:
  - user preferences
  - project decisions
  - durable entity relationships
  - recurring operational context that later turns should retrieve quickly
- Do not store ephemeral material in graph-backed memory, including:
  - temporary debugging notes
  - one-off command output
  - transient errors unless they represent a durable incident worth tracking
  - raw reasoning traces
  - secrets, tokens, passwords, or credential material
- Before re-asking the user for likely durable context, prefer a bounded graph-memory read.
- At the start of non-trivial planning, debugging, architecture, audit, adoption, upgrade, harvest, or handoff work, use the repo's documented memory-discovery workflow when prior context may exist.
- Query the repo-named memory group first when repo policy names one.
- When the right memory group is unclear, or when the task crosses repos, tenants, or domains, query a reviewed atlas or routing layer first and inspect retrieval, privacy, export, and audience policy before descending into source groups.
- Prefer compact, factual, retrieval-friendly writes over conversational filler or repeated paraphrases of the same fact.
- Avoid memory spam:
  - do not write the same preference or project fact every turn
  - prefer one good durable memory over many near-duplicate entries
  - if a durable fact changed, record the new durable state rather than narrating every intermediate thought
- Use partitions, groups, namespaces, or equivalent separation mechanisms deliberately so unrelated projects, tenants, or domains do not bleed into one another.
- Treat destructive memory-maintenance tools as explicit cleanup or repair operations, not casual day-to-day commands.
- Verify the memory system's availability or health before debugging against it or assuming it is available during normal work.
- Treat memory-derived claims as advisory until verified against repo files, artifacts, commits, tests, or cited episodes.
- Keep richer narrative rationale, long-form handoff, and human-readable change history in repo notes or memories; use graph-backed memory for compact retrieval-oriented facts and relationships.

## Adoption Notes

Use this module when a repo regularly works with an installed graph-backed memory system and agents need explicit discipline for when to read, write, partition, or clean up memory.

This module complements:
- `notes-and-memories`, which governs durable repo notes and long-form continuity artifacts
- `runtime-state-governance`, when the memory system is part of a user-scoped or operator-scoped runtime surface

Keep product-specific tool names, partition-key semantics, and runtime assumptions repo-local unless they clearly generalize across multiple graph-memory systems.

Repo-local policy should name the primary memory group when one exists and should identify the memory-discovery skill, tool, or command agents are expected to use.

## Repo-Local Graphiti Contract

- The primary repository memory group is `last30days_skill_main`.
- Use atlas-first discovery when a question crosses repositories. For work
  confined to this repository, query `last30days_skill_main` before broader
  memory groups.
- A Graphiti write is required after every non-trivial validated implementation
  slice, architecture or product decision, plan checkpoint, runtime incident
  resolution, or durable blocker discovery.
- Write at most one compact episode for one bounded slice unless distinct
  security or audience boundaries require separation. Do not write routine
  command transcripts, raw fetched content, browser state, credentials, or
  speculative conclusions.
- Each development-journey episode must identify:
  - repository path;
  - roadmap lane and plan/checkpoint when applicable;
  - decision, shipped outcome, or verified blocker;
  - source authority such as files, commit, test receipt, or live readback;
  - current state and the next bounded action.
- Verify Graphiti provider readiness before broad or repeated writes. When the
  service is unavailable, record `graphiti_write_pending` in `RUNBOOK.md` with
  the intended episode summary and retry it at the next non-trivial closeout.
- Graphiti is a retrieval projection of durable development history. It does
  not replace `ROADMAP.md`, `RUNBOOK.md`, plans, commits, or current runtime
  evidence, and memory-derived claims remain advisory until verified against
  those authorities.
- When a durable fact changes, write the new source-backed state so temporal
  invalidation can supersede the older fact; do not delete history merely
  because the repository evolved.
