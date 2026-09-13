# Service Quality Tracer

This repo-only module implements Plan 0092 Packet 1. It loads sealed synthetic
fixtures, runs four fake adapters, and emits a strict
`QualityEvaluationReportV1`. It does not import the shipped Agent Skill,
connect to the service, read a database, call a provider or judge, start a
browser, or mutate a runtime.

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

Use `--emit markdown` for the human projection. Exit codes are stable:

- `0`: all blocking axes passed;
- `2`: a measured blocking quality threshold failed;
- `3`: an input or contract is invalid;
- `4`: execution or evidence is incomplete, including unknown denominators.

Fixtures under `fixtures/service_quality/` are reviewed synthetic inputs.
Changing a set or policy requires changing its canonical digest in every
request that pins it.
