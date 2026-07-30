"""Process-isolation tests for bounded acquisition workers."""

import json
import subprocess
import sys

import pytest

from lib import service_contracts as contracts
from lib import service_worker
from lib.service_worker import SubprocessAcquisitionRunner, WorkerExecutionError


def _request(**overrides):
    values = {
        "schema_version": 1,
        "work_id": "work-001",
        "job_id": "job-001",
        "lease_generation": 3,
        "attempt": 1,
        "profile_id": "default",
        "source": "reddit",
        "query": "cache service",
        "from_date": "2026-06-24",
        "to_date": "2026-07-24",
        "depth": "standard",
        "adapter": "reddit_api",
        "adapter_version": "1",
        "wall_timeout_seconds": 2,
        "item_limit": 20,
        "network_request_limit": 50,
        "cost_budget_cents": 25,
    }
    values.update(overrides)
    return contracts.AcquisitionWorkRequest.from_dict(values)


def _result_payload(request, **overrides):
    values = {
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
        "diagnostics": {"candidate_count": 0},
    }
    values.update(overrides)
    return values


def test_runner_sends_one_contract_and_validates_the_worker_result():
    request = _request()
    payload = json.dumps(_result_payload(request), separators=(",", ":"))
    script = (
        "import json,sys;"
        "request=json.load(sys.stdin);"
        "assert request['lease_generation']==3;"
        f"sys.stdout.write({payload!r})"
    )
    runner = SubprocessAcquisitionRunner(
        lambda _: [sys.executable, "-c", script]
    )

    result = runner.run(request)

    assert result.work_id == request.work_id
    assert result.status is contracts.AcquisitionStatus.SUCCEEDED


def test_runner_times_out_and_returns_only_a_safe_typed_failure():
    request = _request(wall_timeout_seconds=1)
    runner = SubprocessAcquisitionRunner(
        lambda _: [sys.executable, "-c", "import time; time.sleep(10)"]
    )

    with pytest.raises(WorkerExecutionError) as caught:
        runner.run(request)

    assert caught.value.code == "worker_timeout"
    assert caught.value.retry_class is contracts.RetryClass.TRANSIENT
    assert "time.sleep" not in str(caught.value)


def test_timeout_cleanup_never_waits_unbounded_for_child_reaping(monkeypatch):
    waits = []
    threads = []

    class StuckProcess:
        pid = 12345

        def wait(self, timeout=None):
            waits.append(timeout)
            raise subprocess.TimeoutExpired("worker", timeout)

    class ReaperThread:
        def __init__(self, *, target, name, daemon):
            threads.append((target, name, daemon))

        def start(self):
            return None

    killed = []
    monkeypatch.setattr(
        SubprocessAcquisitionRunner,
        "_kill_process_group",
        lambda process: killed.append(process.pid),
    )
    monkeypatch.setattr(service_worker.threading, "Thread", ReaperThread)
    process = StuckProcess()

    SubprocessAcquisitionRunner._kill_and_reap(process)

    assert killed == [process.pid]
    assert waits == [service_worker.WORKER_REAP_TIMEOUT_SECONDS]
    assert threads == [
        (
            process.wait,
            f"last30days-worker-reaper-{process.pid}",
            True,
        )
    ]


def test_runner_rejects_a_stale_worker_lease_generation():
    request = _request()
    payload = json.dumps(
        _result_payload(request, lease_generation=2),
        separators=(",", ":"),
    )
    runner = SubprocessAcquisitionRunner(
        lambda _: [sys.executable, "-c", f"print({payload!r})"]
    )

    with pytest.raises(WorkerExecutionError) as caught:
        runner.run(request)

    assert caught.value.code == "worker_result_mismatch"
    assert caught.value.retry_class is contracts.RetryClass.PERMANENT


def test_runner_rejects_oversized_output_before_contract_use():
    request = _request()
    runner = SubprocessAcquisitionRunner(
        lambda _: [sys.executable, "-c", "print('x' * 2048)"],
        max_output_bytes=1024,
    )

    with pytest.raises(WorkerExecutionError) as caught:
        runner.run(request)

    assert caught.value.code == "worker_output_too_large"


def test_runner_terminates_worker_when_stderr_exceeds_bound():
    request = _request()
    runner = SubprocessAcquisitionRunner(
        lambda _: [
            sys.executable,
            "-c",
            "import sys,time; sys.stderr.write('x' * 4096); "
            "sys.stderr.flush(); time.sleep(10)",
        ],
        max_stderr_bytes=1024,
    )

    with pytest.raises(WorkerExecutionError) as caught:
        runner.run(request)

    assert caught.value.code == "worker_stderr_too_large"
