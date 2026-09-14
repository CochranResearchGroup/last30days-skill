"""Scoped public question composition, independent of HTTP or model providers."""

from __future__ import annotations

import json
import sqlite3
import threading
import time
from contextlib import closing
from pathlib import Path
from typing import Callable, Sequence

from . import service_question_contracts as contracts
from .service_question_evidence import QuestionEvidenceResolver
from .service_questions import NoToolAnswerWorker, PostSearchBackend, QuestionRunner, QuestionService, QuestionWorkerError


MAX_RESPONSE_BYTES = 131_072


class QuestionUnavailableError(LookupError):
    """The same public error for absent and unauthorized question identities."""


class QuestionResponseTooLargeError(ValueError):
    """An immutable result cannot be represented within the transport bound."""


class QuestionRuntimeUnavailableError(RuntimeError):
    """A configured question executor is stopped or has failed."""


def _bounded(result):
    if len(contracts.canonical_json(result.to_dict()).encode("utf-8")) > MAX_RESPONSE_BYTES:
        raise QuestionResponseTooLargeError("question response exceeds transport limit")
    return result


class _UnavailableWorker:
    worker_ref = "unconfigured-question-worker-v1"

    def answer(self, payload):
        raise QuestionWorkerError("model_unavailable", "question synthesis is not configured", retryable=False)


class QuestionApplication:
    """Authorize every public read against the host's current profile scope."""

    def __init__(
        self,
        db_path: Path,
        search_backend: PostSearchBackend,
        *,
        access_partitions: Callable[[str], Sequence[str]],
        worker: NoToolAnswerWorker | None = None,
    ) -> None:
        self.db_path = Path(db_path).resolve()
        self._access_partitions = access_partitions
        self.service = QuestionService(self.db_path, search_backend)
        self.resolver = QuestionEvidenceResolver(self.db_path)
        self.runner = QuestionRunner(self.service.queue, worker or _UnavailableWorker())
        self._worker_configured = worker is not None
        self._lock = threading.RLock()
        self._stopping = threading.Event()
        self._wake = threading.Event()
        self._thread: threading.Thread | None = None
        self._failed = False

    def start(self) -> None:
        """Start one host-owned executor; the unavailable default needs no thread."""
        with self._lock:
            if not self._worker_configured:
                return
            if self._thread is not None and self._thread.is_alive():
                if self._stopping.is_set():
                    raise QuestionRuntimeUnavailableError("question worker is stopping")
                return
            self._stopping.clear()
            self._failed = False
            self._thread = threading.Thread(target=self._run, name="last30days-question-worker")
            self._thread.start()

    def stop(self, *, timeout: float = 5.0) -> bool:
        """Stop admission, wake waits, and report whether the exact thread exited.

        Injected workers must enforce their own call timeout. This method never
        pretends that a timed-out join killed Python code or cancelled a lease.
        """
        if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or not 0 <= timeout <= 30:
            raise ValueError("question shutdown timeout must be between 0 and 30 seconds")
        with self._lock:
            self._stopping.set()
            self._wake.set()
            thread = self._thread
        if thread is not None:
            thread.join(timeout)
        return thread is None or not thread.is_alive()

    def _run(self) -> None:
        try:
            while not self._stopping.is_set():
                status = self.runner.run_once(worker_id="question-application")
                if status is None:
                    self._wake.wait(0.05)
                    self._wake.clear()
        except Exception:
            # Do not leak source/model payloads or silently start a retry loop.
            self._failed = True
            self._stopping.set()

    def _partitions(self, profile_id: str) -> tuple[str, ...]:
        partitions = tuple(dict.fromkeys(self._access_partitions(profile_id)))
        if not partitions or not all(isinstance(item, str) and item for item in partitions):
            raise QuestionUnavailableError("question unavailable")
        return partitions

    def ask_question(
        self, request: contracts.QuestionRequestV1, *, wait_cancelled: threading.Event | None = None
    ) -> contracts.QuestionStatusV1:
        with self._lock:
            if self._stopping.is_set() or self._failed or (
                self._worker_configured and (self._thread is None or not self._thread.is_alive())
            ):
                raise QuestionRuntimeUnavailableError("question worker is unavailable")
            status = self.service.submit(request, access_partitions=self._partitions(request.profile_id))
            if status.state == "pending":
                if self._worker_configured:
                    self._wake.set()
                else:
                    self.runner.run_once(worker_id="unconfigured-host", question_id=status.question_id)
        deadline = time.monotonic() + request.limits.wait_ms / 1000
        while True:
            status = self.question_status(status.question_id, profile_id=request.profile_id)
            remaining = deadline - time.monotonic()
            if (status.state not in {"pending", "running"} or remaining <= 0
                    or self._stopping.is_set()
                    or (wait_cancelled is not None and wait_cancelled.is_set())):
                return status
            self._stopping.wait(min(remaining, 0.01))

    def question_status(self, question_id: str, *, profile_id: str) -> contracts.QuestionStatusV1:
        partitions = self._partitions(profile_id)
        with closing(sqlite3.connect(f"{self.db_path.as_uri()}?mode=ro", uri=True, timeout=5)) as conn:
            conn.execute("PRAGMA query_only=ON")
            row = conn.execute(
                """SELECT q.request_json, r.access_partitions_digest
                   FROM service_question_retrievals r
                   JOIN service_question_requests q USING (request_id)
                   WHERE r.question_id = ?""",
                (question_id,),
            ).fetchone()
        if row is None:
            raise QuestionUnavailableError("question unavailable")
        if (json.loads(row[0])["profile_id"] != profile_id
                or row[1] != contracts.digest(sorted(partitions))):
            raise QuestionUnavailableError("question unavailable")
        return _bounded(self.service.status(question_id))

    def read_evidence(self, request: contracts.EvidenceReadRequestV1) -> contracts.EvidenceReadResponseV1:
        return _bounded(self.resolver.read(request, access_partitions=self._partitions(request.profile_id)))
