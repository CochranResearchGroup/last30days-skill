# Service Quality Tracer

This repo-only module implements the provider-free quality contracts introduced
by Plan 0092 and the sealed-fixture adapters completed by Plan 0122. The
original deterministic tracer can run four fake adapters without importing the
shipped Agent Skill, connecting to the service, reading a database, calling a
provider or judge, starting a browser, or mutating a runtime.

For product evidence, pass one or more `--fixture ID=PATH` arguments. That mode
uses real read-only adapters for corpus integrity, acquisition coverage,
post-search retrieval, and durable question grounding. Fixtures are opened as
immutable SQLite databases in query-only mode and must match their pinned
SHA-256 digests; WAL or journal companions fail closed. These adapters make no
network, model, browser, or runtime calls and perform no database writes.
Grounding is structural: it verifies durable request, retrieval, task, answer,
citation, partition, and digest closure. It does not claim semantic entailment
or production quality.

The public interface is `QualityRunnerV1.run(request, evaluation_set, policy)`.
Inputs reject unknown fields and pin the evaluation-set and threshold-policy
digests. Reports retain acquisition, corpus, retrieval, and grounding as
separate axes. Every metric records its numerator, denominator, exclusions,
threshold rule, and comparison shape. Canonical JSON is authoritative;
Markdown is a deterministic projection.

Run the sealed passing fixture from the repository root:

```bash
python3 dev/last30days/scripts/evaluate_service_quality.py \
  --evaluation-set fixtures/service_quality/evaluation-set-pass.v1.json \
  --threshold-policy fixtures/service_quality/threshold-policy.v1.json \
  --request fixtures/service_quality/request-pass.v1.json \
  --emit json
```

For a sealed SQLite fixture, add:

```bash
  --fixture sealed-corpus=/absolute/path/to/research.sqlite
```

Use `--emit markdown` for the human projection. Exit codes are stable:

- `0`: all blocking axes passed;
- `2`: a measured blocking quality threshold failed;
- `3`: an input or contract is invalid;
- `4`: execution or evidence is incomplete, including unknown denominators.

Fixtures under `fixtures/service_quality/` are reviewed synthetic inputs.
Changing a set or policy requires changing its canonical digest in every
request that pins it.
