# Plan 0070 Integration And Install Receipt

Date: 2026-09-12

- Fork integration: pull request 1, merge commit
  `905b9dbc6773e26c0141b4a38355c471c59b84b6`.
- Validation: 66 affected provider-free tests passed on the reconciled source.
- Built artifact: `last30days-service-0.3.115.tar.gz`, SHA-256
  `82d4d4cb2838cf7f8a24665afd7067127c7489032d6034aab6170ad73a54ac8a`.
- Guarded install: accepted service 0.3.115, schema 17, runtime manifest
  `1565301a364eba2d1a5a3f20169687bdc3f7c078a826a1fda0d723fbae614554`.
- Frozen Skill install: synchronized from the exact integrated tree; both
  `last30days` and the bundled repository policy selector were refreshed for
  supported hosts. PromptScript global installation remained unsupported and
  was reported as such by the installer.
- Runtime readback: ready on query index
  `index-e51e8df608f7374bd1d89b9b`; X acquisition ready with 25 indexed
  documents.
- Cache-only acceptance: `AI agents`, source `x`, profile
  `last30days-facebook`, returned eight evidence items and no refresh job.
- Boundary adjudication: the default profile returned no X evidence because
  the current snapshot's 94 X entries use the private
  `profile:last30days-facebook` partition. The authorized-profile result proves
  retrieval while preserving the intended access boundary.

No provider refresh, browser/profile mutation, recurring tick, or upstream
pull request occurred.
