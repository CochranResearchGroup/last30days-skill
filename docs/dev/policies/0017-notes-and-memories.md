# Policy | Notes And Memories

## Policy

- Routinely look for opportunities to record durable notes under `docs/dev/notes/` when a slice leaves behind findings, migration lessons, semantic mismatches, or operational lessons worth preserving.
- Routinely look for opportunities to record durable memories under `docs/dev/memories/` when a repo accumulates stable context, conventions, or recurring facts that future sessions should not have to rediscover.
- Prefer notes for dated observations tied to a specific slice or event.
- Prefer memories for stable context that should persist across many slices.
- Use the same deterministic serial-plus-date filename prefix for human-readable Markdown notes and memories that this repo uses for plans: `NNNN-YYYY-MM-DD-slug.md`.
- Keep machine-readable receipts and evidence packets serially prefixed under `docs/dev/notes/`; their schema-bound filenames may omit the date when the receipt contract already supplies durable chronology.
- Allocate new serials after the highest existing top-level note serial. Do not reuse a serial for a different human-readable note.
- Keep notes and memories discoverable and auditable through deterministic helpers rather than relying on chat history or ad hoc filenames.
- When this policy is active, check existing `docs/dev/notes/` and `docs/dev/memories/` before starting work and record new entries when the current slice produces reusable context.
- Do not create multiple overlapping notes for one event when one well-scoped dated note already captures the decision, evidence, and reusable lesson.
- When the repo also uses a durable memory system, keep the boundary explicit: use notes and memories for richer human-readable continuity, and use the memory system for compact retrieval-oriented facts and relationships.
- Do not treat graph-memory writes as a substitute for repo-file continuity. Write the durable note, memory, plan, release note, or artifact first, then mirror only the stable retrieval-oriented facts.

## Adoption Notes

This repo adopts the shared `notes-and-memories` module with one local distinction: machine-readable receipts retain their existing serial-first schema-bound names, while prose notes and memories use the full serial-plus-date form.
