"""Bounded subprocess boundary for source acquisition workers."""

from __future__ import annotations

import json
import os
import selectors
import signal
import subprocess
import tempfile
import threading
import time
from collections.abc import Callable, Mapping, Sequence

from . import service_contracts as contracts


MAX_WORK_REQUEST_BYTES = 131_072
DEFAULT_MAX_WORK_RESULT_BYTES = 1_048_576
DEFAULT_MAX_STDERR_BYTES = 65_536

SOURCE_ADAPTERS = {
    "x": ("x_agent_browser", "1"),
    "facebook": ("facebook_agent_browser", "1"),
    "linkedin": ("linkedin_agent_browser", "1"),
    "youtube": ("youtube_ytdlp", "1"),
    "reddit": ("reddit_api", "1"),
}
PROFILE_SOURCE_ADAPTERS = {
    "linkedin": ("linkedin_profile_agent_browser", "1"),
}
SOURCE_COST_RESERVATIONS_CENTS = {
    "reddit": 1,
    "x": 0,
    "facebook": 0,
    "linkedin": 0,
    "youtube": 0,
}


class WorkerExecutionError(RuntimeError):
    """Safe typed failure from the process boundary, never raw worker output."""

    def __init__(
        self,
        code: str,
        retry_class: contracts.RetryClass,
        *,
        retry_after_seconds: int | None = None,
    ) -> None:
        self.code = code
        self.retry_class = retry_class
        self.retry_after_seconds = retry_after_seconds
        super().__init__(f"acquisition worker failed: {code}")


CommandResolver = Callable[
    [contracts.AcquisitionWorkRequest], Sequence[str]
]
EnvironmentResolver = Callable[
    [contracts.AcquisitionWorkRequest], Mapping[str, str]
]


class SubprocessAcquisitionRunner:
    """Execute one schema request in an isolated process with hard host bounds."""

    def __init__(
        self,
        command_resolver: CommandResolver,
        *,
        environment_resolver: EnvironmentResolver | None = None,
        max_output_bytes: int = DEFAULT_MAX_WORK_RESULT_BYTES,
        max_stderr_bytes: int = DEFAULT_MAX_STDERR_BYTES,
    ) -> None:
        if max_output_bytes < 1 or max_stderr_bytes < 1:
            raise ValueError("worker output bounds must be positive")
        self.command_resolver = command_resolver
        self.environment_resolver = environment_resolver
        self.max_output_bytes = max_output_bytes
        self.max_stderr_bytes = max_stderr_bytes
        self._process_lock = threading.Lock()
        self._processes: set[subprocess.Popen[bytes]] = set()

    @staticmethod
    def _kill_process_group(process: subprocess.Popen[bytes]) -> None:
        if os.name == "posix":
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                return
        else:
            process.kill()

    def cancel_all(self) -> None:
        """Terminate every worker owned by this runner during service shutdown."""
        with self._process_lock:
            processes = tuple(self._processes)
        for process in processes:
            self._kill_process_group(process)

    def _read_bounded(
        self,
        process: subprocess.Popen[bytes],
        *,
        timeout_seconds: int,
    ) -> tuple[bytes, bytes]:
        if process.stdout is None or process.stderr is None:
            raise WorkerExecutionError(
                "worker_pipe_unavailable",
                contracts.RetryClass.CONFIGURATION,
            )
        selector = selectors.DefaultSelector()
        selector.register(process.stdout, selectors.EVENT_READ, "stdout")
        selector.register(process.stderr, selectors.EVENT_READ, "stderr")
        buffers = {"stdout": bytearray(), "stderr": bytearray()}
        limits = {
            "stdout": self.max_output_bytes,
            "stderr": self.max_stderr_bytes,
        }
        deadline = time.monotonic() + timeout_seconds
        try:
            while selector.get_map():
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    self._kill_process_group(process)
                    process.wait()
                    raise WorkerExecutionError(
                        "worker_timeout",
                        contracts.RetryClass.TRANSIENT,
                    )
                events = selector.select(min(remaining, 0.1))
                for key, _mask in events:
                    chunk = os.read(key.fileobj.fileno(), 65_536)
                    if not chunk:
                        selector.unregister(key.fileobj)
                        key.fileobj.close()
                        continue
                    name = key.data
                    if len(buffers[name]) + len(chunk) > limits[name]:
                        self._kill_process_group(process)
                        process.wait()
                        raise WorkerExecutionError(
                            (
                                "worker_output_too_large"
                                if name == "stdout"
                                else "worker_stderr_too_large"
                            ),
                            contracts.RetryClass.PERMANENT,
                        )
                    buffers[name].extend(chunk)
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise subprocess.TimeoutExpired(process.args, timeout_seconds)
            process.wait(timeout=remaining)
        except subprocess.TimeoutExpired as exc:
            self._kill_process_group(process)
            process.wait()
            raise WorkerExecutionError(
                "worker_timeout",
                contracts.RetryClass.TRANSIENT,
            ) from exc
        finally:
            selector.close()
        return bytes(buffers["stdout"]), bytes(buffers["stderr"])

    def run(
        self, request: contracts.AcquisitionWorkRequest
    ) -> contracts.AcquisitionWorkResult:
        command = [str(part) for part in self.command_resolver(request)]
        if not command or any(not part for part in command):
            raise WorkerExecutionError(
                "worker_command_invalid",
                contracts.RetryClass.CONFIGURATION,
            )
        request_bytes = json.dumps(
            request.to_dict(),
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        if len(request_bytes) > MAX_WORK_REQUEST_BYTES:
            raise WorkerExecutionError(
                "worker_request_too_large",
                contracts.RetryClass.PERMANENT,
            )
        env = dict(os.environ)
        if self.environment_resolver is not None:
            additions = self.environment_resolver(request)
            if not all(
                isinstance(key, str) and isinstance(value, str)
                for key, value in additions.items()
            ):
                raise WorkerExecutionError(
                    "worker_environment_invalid",
                    contracts.RetryClass.CONFIGURATION,
                )
            env.update(additions)
        input_file = tempfile.TemporaryFile()
        input_file.write(request_bytes)
        input_file.seek(0)
        try:
            process = subprocess.Popen(
                command,
                stdin=input_file,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                start_new_session=os.name == "posix",
            )
        except OSError as exc:
            input_file.close()
            raise WorkerExecutionError(
                "worker_launch_failed",
                contracts.RetryClass.CONFIGURATION,
            ) from exc
        with self._process_lock:
            self._processes.add(process)
        try:
            stdout, _stderr = self._read_bounded(
                process,
                timeout_seconds=request.wall_timeout_seconds,
            )
        finally:
            with self._process_lock:
                self._processes.discard(process)
            input_file.close()
        if process.returncode != 0:
            raise WorkerExecutionError(
                "worker_exit_nonzero",
                contracts.RetryClass.TRANSIENT,
            )
        try:
            payload = json.loads(stdout.decode("utf-8"))
            result = contracts.AcquisitionWorkResult.from_dict(payload)
        except (
            UnicodeDecodeError,
            json.JSONDecodeError,
            contracts.ContractValidationError,
        ) as exc:
            raise WorkerExecutionError(
                "worker_result_invalid",
                contracts.RetryClass.TRANSIENT,
            ) from exc
        expected = (
            request.work_id,
            request.job_id,
            request.lease_generation,
            request.source,
            request.adapter,
            request.adapter_version,
        )
        observed = (
            result.work_id,
            result.job_id,
            result.lease_generation,
            result.source,
            result.adapter,
            result.adapter_version,
        )
        if observed != expected:
            raise WorkerExecutionError(
                "worker_result_mismatch",
                contracts.RetryClass.PERMANENT,
            )
        if result.item_count > request.item_limit:
            raise WorkerExecutionError(
                "worker_item_limit_exceeded",
                contracts.RetryClass.PERMANENT,
            )
        if result.cost_cents > request.cost_budget_cents:
            raise WorkerExecutionError(
                "worker_cost_limit_exceeded",
                contracts.RetryClass.PERMANENT,
            )
        return result
