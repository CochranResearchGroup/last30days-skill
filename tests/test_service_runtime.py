"""Runtime wiring keeps acquisition durable, isolated, and independently stoppable."""

import sys
import threading
from datetime import datetime, timezone
from types import SimpleNamespace

from lib import service_contracts as contracts
from lib.service_retrieval import HybridRetriever
from lib.service_runtime import (
    AcquisitionLoop,
    AssessmentLoop,
    EnrichmentLoop,
    build_acquisition_runtime,
)


NOW = datetime(2026, 7, 24, 12, 0, tzinfo=timezone.utc)


class EmptyWorker:
    def __init__(self):
        self.requests = []

    def run(self, request):
        self.requests.append(request)
        return contracts.AcquisitionWorkResult.from_dict(
            {
                "schema_version": 1,
                "work_id": request.work_id,
                "job_id": request.job_id,
                "lease_generation": request.lease_generation,
                "source": request.source,
                "adapter": request.adapter,
                "adapter_version": request.adapter_version,
                "status": "succeeded",
                "safe_error_code": None,
                "retry_class": "none",
                "retry_after_seconds": None,
                "observed_at": "2026-07-24T12:00:00Z",
                "fetched_at": "2026-07-24T12:00:01Z",
                "items": [],
                "item_count": 0,
                "cost_cents": 0,
                "diagnostics": {"accepted_count": 0},
            }
        )


def _query():
    return contracts.QueryRequest.from_dict(
        {
            "schema_version": 1,
            "request_id": "runtime-query",
            "profile_id": "default",
            "query": "runtime wiring",
            "freshness_policy": "force_refresh",
            "response_mode": "evidence",
            "filters": {"sources": ["reddit"]},
            "top_k": 8,
            "max_chars": 8192,
            "wait_ms": 0,
        }
    )


def test_runtime_processes_durable_job_without_importing_worker_entrypoint(tmp_path):
    sys.modules.pop("lib.service_acquisition_worker", None)
    worker = EmptyWorker()
    runtime = build_acquisition_runtime(
        tmp_path / "research.db",
        HybridRetriever(tmp_path / "research.db"),
        worker=worker,
        clock=lambda: NOW,
        default_sources=("reddit",),
    )
    job_id = runtime.scheduler.ensure_refresh(_query())

    completed = runtime.runner.run_once(worker_id="runtime-test")

    assert completed is not None
    assert completed.job_id == job_id
    assert completed.state is contracts.JobState.PUBLISHED
    assert len(worker.requests) == 1
    assert "lib.service_acquisition_worker" not in sys.modules


def test_runtime_readiness_uses_worker_visible_browser_enablement(tmp_path, monkeypatch):
    monkeypatch.setenv("LAST30DAYS_X_BROWSER", "true")
    monkeypatch.setenv("LAST30DAYS_FACEBOOK_BROWSER", "true")
    monkeypatch.setenv("LAST30DAYS_LINKEDIN_BROWSER", "true")
    monkeypatch.setattr("lib.service_runtime.shutil.which", lambda name: f"/bin/{name}")

    runtime = build_acquisition_runtime(
        tmp_path / "readiness.db",
        HybridRetriever(tmp_path / "readiness.db"),
        worker=EmptyWorker(),
        default_sources=("facebook", "linkedin", "reddit", "x", "youtube"),
    )

    assert runtime.source_readiness == {
        "facebook": True,
        "linkedin": True,
        "reddit": True,
        "x": True,
        "youtube": True,
    }


def test_runtime_uses_user_scoped_source_catalog_and_access_orders(tmp_path, monkeypatch):
    monkeypatch.setenv("LAST30DAYS_SERVICE_SOURCES", "reddit,youtube")
    monkeypatch.setenv("LAST30DAYS_REDDIT_ACCESS_ORDER", "keyless,agent_browser")
    monkeypatch.setenv("LAST30DAYS_YOUTUBE_ACCESS_ORDER", "yt_dlp")
    monkeypatch.setattr("lib.service_runtime.shutil.which", lambda name: f"/bin/{name}")

    runtime = build_acquisition_runtime(
        tmp_path / "configured-readiness.db",
        HybridRetriever(tmp_path / "configured-readiness.db"),
        worker=EmptyWorker(),
    )

    assert runtime.sources == ("reddit", "youtube")
    assert runtime.source_readiness == {"reddit": True, "youtube": True}


def test_acquisition_loop_starts_and_stops_cleanly():
    class IdleRunner:
        def __init__(self):
            self.calls = 0

        def run_once(self, *, worker_id):
            assert worker_id
            self.calls += 1
            return None

    runner = IdleRunner()
    loop = AcquisitionLoop(runner, idle_seconds=0.01)

    loop.start()
    loop.stop(timeout=1)

    assert runner.calls >= 1
    assert loop.is_alive is False
    assert loop.last_error_code is None


def test_acquisition_loop_cancels_active_work_before_join():
    class BlockingRunner:
        def __init__(self):
            self.started = threading.Event()
            self.released = threading.Event()
            self.cancelled = False

        def run_once(self, *, worker_id):
            assert worker_id
            self.started.set()
            self.released.wait(2)
            return None

        def cancel_active_work(self):
            self.cancelled = True
            self.released.set()

    runner = BlockingRunner()
    loop = AcquisitionLoop(runner, idle_seconds=0.01)
    loop.start()
    assert runner.started.wait(1)

    loop.stop(timeout=1)

    assert runner.cancelled is True
    assert loop.is_alive is False


def test_assessment_loop_is_independent_and_stoppable():
    class Assessment:
        def __init__(self):
            self.called = threading.Event()

        def run_once(self, *, worker_id):
            assert worker_id
            self.called.set()
            return None

    assessment = Assessment()
    loop = AssessmentLoop(assessment, idle_seconds=0.01, error_seconds=0.01)

    loop.start()
    assert assessment.called.wait(1)
    loop.stop(timeout=1)

    assert loop.is_alive is False
    assert loop.last_error_code is None


def test_enrichment_loop_publishes_changed_projection_asynchronously():
    class Enrichment:
        def __init__(self):
            self.called = threading.Event()
            self.relationships_called = threading.Event()

        def embed_chunks(self):
            self.called.set()
            return SimpleNamespace(embeddings_written=2)

        def extract_and_promote_entities(self):
            return SimpleNamespace(accepted_count=1)

        def extract_and_promote_relationships(self):
            self.relationships_called.set()
            return SimpleNamespace(accepted_count=1)

    class Retriever:
        def __init__(self):
            self.published = 0

        def publish_index(self):
            self.published += 1

    enrichment = Enrichment()
    retriever = Retriever()
    loop = EnrichmentLoop(enrichment, retriever, interval_seconds=0.01)

    loop.start()
    assert enrichment.called.wait(1)
    assert enrichment.relationships_called.wait(1)
    loop.stop(timeout=1)

    assert retriever.published >= 1
    assert loop.last_error_code is None


def test_enrichment_loop_failure_isolated_from_runtime():
    class BrokenEnrichment:
        def __init__(self):
            self.called = threading.Event()

        def embed_chunks(self):
            self.called.set()
            raise RuntimeError("provider details")

        def extract_and_promote_entities(self):
            raise AssertionError("cycle must stop after embedding failure")

    class Retriever:
        def publish_index(self):
            raise AssertionError("failed enrichment must not publish")

    enrichment = BrokenEnrichment()
    loop = EnrichmentLoop(enrichment, Retriever(), interval_seconds=0.01)

    loop.start()
    assert enrichment.called.wait(1)
    loop.stop(timeout=1)

    assert loop.last_error_code == "enrichment_loop_failure"
    assert loop.is_alive is False


def test_enrichment_loop_reports_returned_provider_failure():
    class FailedEnrichment:
        def __init__(self):
            self.called = threading.Event()

        def embed_chunks(self):
            self.called.set()
            return SimpleNamespace(
                status="failed",
                error_code="embedding_provider_error",
                embeddings_written=0,
            )

        def extract_and_promote_entities(self):
            return SimpleNamespace(accepted_count=0)

        def extract_and_promote_relationships(self):
            return SimpleNamespace(accepted_count=0)

    class Retriever:
        def publish_index(self):
            raise AssertionError("failed enrichment must not publish")

    enrichment = FailedEnrichment()
    loop = EnrichmentLoop(enrichment, Retriever(), interval_seconds=60)

    loop.start()
    assert enrichment.called.wait(1)
    loop.stop(timeout=1)

    assert loop.last_error_code == "embedding_provider_error"
