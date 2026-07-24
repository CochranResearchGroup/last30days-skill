"""Runtime wiring keeps acquisition durable, isolated, and independently stoppable."""

import sys
import threading
from datetime import datetime, timezone

from lib import service_contracts as contracts
from lib.service_retrieval import HybridRetriever
from lib.service_runtime import AcquisitionLoop, build_acquisition_runtime


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
