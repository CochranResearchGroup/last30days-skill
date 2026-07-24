# Concepts

Shared vocabulary for `last30days-skill`. Terms here have a precise project-specific meaning — distinct enough from their general technical sense that a new contributor would need them defined to follow conversations, PR descriptions, or the SKILL.md contract.

## The package

### Intelligence Service

The user-scoped, cache-backed product authority. It owns durable acquisition
jobs, source authentication boundaries, normalized content, immutable search
indexes, semantic enrichment, evidence-linked graph projections, and compact
query responses. Agents discover and query it; they do not operate browsers or
scrapers on its behalf.

### Skill

A self-contained agent-instructions package consisting of a `SKILL.md` prose contract plus a sibling `scripts/` directory. The package conforms to the [Agent Skills](https://agentskills.io) open format and installs across every major harness. A Skill is a distribution and synthesis surface; the Intelligence Service is the product authority.

For service-enabled hosts, the Skill is a client and synthesis surface over the
Intelligence Service. Its direct Engine workflow remains the portable
operator/debug fallback.

### Engine

The Python script (`scripts/last30days.py`) the Skill's SKILL.md invokes to do the actual research work. The Engine and SKILL.md have a contract: SKILL.md tells the model which flags to pass (`--plan`, `--competitors-plan`, `--x-handle`, `--subreddits`, `--emit=compact`, etc.), and the Engine produces a specific output shape (badge line, ranked evidence clusters, emoji-tree footer) that the model is contractually required to pass through. The Engine is implementation; the SKILL.md prose is the agent-facing surface.

The Engine is request-scoped compatibility infrastructure. Service-backed
agents use the cache/query contract instead of invoking it per request.

### MCP Adapter

The CGO-free Go process that exposes service discovery, cached query, durable
refresh, and job polling as compact MCP tools/resources. It is deliberately a
thin Unix-socket client: it contains no source acquisition logic. A packaged
MCPB may start the one shared service daemon when absent, but query handlers
never launch a request-scoped research subprocess.

### Intelligence Ledger

The user-scoped, append-only evidence surface for stochastic work. It stores
content-addressed inputs and outputs, model-call receipts, strict decisions,
evaluation results, approval records, and maintenance-run state. Browser
cookies, credentials, sessions, raw private page data, and live route
identifiers are forbidden. The ledger makes an enrichment or repair
recommendation replayable without making the model an authority.

### App Intelligence Worker

A bounded stochastic worker invoked by a deterministic service supervisor for
structured enrichment, retrieval evaluation, or repeated adapter-failure
investigation. Every turn uses a strict output schema and a fixed call budget.
The host owns state, tests, branch limits, validation, approval, and replay.
Workers can propose and judge; they cannot publish an index, deploy code, or
mutate live source configuration.

### Maintenance Plane

The operator-owned control plane for investigating repeated adapter failures.
It is separate from normal query and refresh traffic: ordinary agents never
operate it, and ordinary research requests never trigger an unbounded model
loop. The plane can prepare one allowlisted repair branch and run allowlisted
tests within configured attempt and rework limits. Publication and live-source
configuration remain explicit human-gated actions.

### Harness

The agent runtime that loads Skills and invokes them on the user's behalf. Claude Code is the most common Harness for this Skill but not the only one — Codex, Cursor, GitHub Copilot, Gemini CLI, and the rest of the Agent Skills ecosystem also count. "Multi-harness" describes a Skill that works correctly across every Harness it installs into; features written without multi-harness awareness (e.g., engine flags with no SKILL.md integration, or paths hardcoded to one Harness's install layout) regress on Harnesses other than the one they were tested against.

## Research pipeline

### Primary entity

The brand or proper-noun core of a research topic — the topic with its Intent modifier stripped. It is what the research is *about*, as distinct from how the user phrased the search.

### Intent modifier

A trailing word or phrase in a topic that expresses what the user wants to know rather than what the topic is ("review", "use cases", "pricing"). Stripped when deriving the Primary entity.

### Entity grounding

The check that a candidate item plausibly mentions the Primary entity before final ranking. Grounding keys on the head token (first word) of the Primary entity rather than the full phrase — trailing words are usually search descriptors, so requiring them falsely demotes on-entity items.

An item that fails grounding receives a decisive entity-miss demotion, designed so engagement cannot rescue off-entity content. Because the demotion is decisive, the grounding bar is deliberately conservative: its failure modes degrade toward "no penalty," never toward burying on-entity signal.

### Keyless path

The research flow available with no API keys: source data is gathered by scraping and RSS rather than authenticated APIs, and ranking falls back to local scoring instead of LLM-based reranking. This is the free tier of the Skill; lexical quality safeguards like Entity grounding matter most here, because no LLM is available to judge relevance semantically.

### Comment-enrichment slots

The small, depth-dependent budget of Reddit posts whose comments get fetched in the Keyless path. Slot selection is relevance-aware: posts that pass Entity grounding claim slots first, so the budget is not spent on high-engagement posts that final ranking will demote anyway.
