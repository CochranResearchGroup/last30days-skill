"""Deterministic offline quality, latency, and cost gates for service retrieval."""

from __future__ import annotations

import math
import time
from dataclasses import dataclass
from typing import Callable, Protocol, Sequence


class EvalRetriever(Protocol):
    embedding_provider: object | None

    def search_snapshot(
        self,
        query: str,
        *,
        sources: Sequence[str] | None = None,
        top_k: int = 8,
        snippet_chars: int = 320,
    ): ...


@dataclass(frozen=True)
class RetrievalEvalCase:
    case_id: str
    query: str
    expected_document_ids: tuple[str, ...]
    lane: str = "lexical"
    sources: tuple[str, ...] = ()
    top_k: int = 5
    max_latency_ms: float = 250.0

    def __post_init__(self) -> None:
        if not self.case_id or not self.query or not self.expected_document_ids:
            raise ValueError("eval cases require ids, queries, and expected documents")
        if self.lane not in {"lexical", "semantic", "graph"}:
            raise ValueError("eval lane must be lexical, semantic, or graph")
        if self.top_k < 1 or self.max_latency_ms <= 0:
            raise ValueError("eval bounds must be positive")


@dataclass(frozen=True)
class RetrievalEvalReport:
    case_count: int
    precision_at_k: float
    recall_at_k: float
    graph_precision_at_k: float
    p95_latency_ms: float
    cost_cents: int
    lane_passes: dict[str, int]
    passed: bool


def run_retrieval_eval(
    retriever: EvalRetriever,
    cases: Sequence[RetrievalEvalCase],
    *,
    max_cost_cents: int = 0,
    minimum_precision: float = 0.8,
    minimum_recall: float = 1.0,
    minimum_graph_precision: float = 0.8,
    clock: Callable[[], float] = time.perf_counter,
) -> RetrievalEvalReport:
    """Evaluate fixed cases without network, model judgment, or mutable thresholds."""

    if not cases:
        raise ValueError("at least one eval case is required")
    if max_cost_cents < 0:
        raise ValueError("max_cost_cents must not be negative")
    for value in (minimum_precision, minimum_recall, minimum_graph_precision):
        if not 0 <= value <= 1:
            raise ValueError("quality thresholds must be between zero and one")
    precisions: list[float] = []
    recalls: list[float] = []
    latencies: list[float] = []
    graph_precisions: list[float] = []
    lane_passes = {"lexical": 0, "semantic": 0, "graph": 0}
    passed = True
    for case in cases:
        started = clock()
        snapshot = retriever.search_snapshot(
            case.query,
            sources=case.sources or None,
            top_k=case.top_k,
            snippet_chars=320,
        )
        elapsed_ms = round(max(0.0, (clock() - started) * 1000), 6)
        latencies.append(elapsed_ms)
        returned = [item.document_id for item in snapshot.evidence]
        expected = set(case.expected_document_ids)
        matched = expected.intersection(returned)
        precision = len(matched) / max(1, len(returned))
        precisions.append(precision)
        recall = len(matched) / len(expected)
        recalls.append(recall)
        if case.lane == "graph":
            graph_precisions.append(precision)
        lane_hit = any(
            item.document_id in expected and item.scores[case.lane] > 0
            for item in snapshot.evidence
        )
        if lane_hit:
            lane_passes[case.lane] += 1
        passed = (
            passed
            and precision >= minimum_precision
            and recall >= minimum_recall
            and lane_hit
        )
        if case.lane == "graph":
            passed = passed and precision >= minimum_graph_precision
        passed = passed and elapsed_ms <= case.max_latency_ms

    provider = getattr(retriever, "embedding_provider", None)
    per_call_cost = getattr(provider, "cost_cents_per_call", 0)
    cost_cents = int(per_call_cost) * len(cases)
    passed = passed and cost_cents <= max_cost_cents
    ordered_latency = sorted(latencies)
    p95_index = max(0, math.ceil(len(ordered_latency) * 0.95) - 1)
    return RetrievalEvalReport(
        case_count=len(cases),
        precision_at_k=sum(precisions) / len(precisions),
        recall_at_k=sum(recalls) / len(recalls),
        graph_precision_at_k=(
            sum(graph_precisions) / len(graph_precisions)
            if graph_precisions
            else 1.0
        ),
        p95_latency_ms=ordered_latency[p95_index],
        cost_cents=cost_cents,
        lane_passes=lane_passes,
        passed=passed,
    )
