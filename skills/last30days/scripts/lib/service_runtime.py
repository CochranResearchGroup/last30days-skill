"""Composition root and bounded background loop for durable acquisition."""

from __future__ import annotations

import os
import shutil
import sys
import threading
import uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, Protocol, Sequence

from .service_enrichment import EnrichmentService
from .service_job_runner import AcquisitionJobRunner, AcquisitionRunner, JobRunnerPolicy
from .service_publication import CorpusPublisher
from .service_refresh import RefreshPolicy, ServiceRefreshScheduler
from .service_retrieval import HybridRetriever
from .service_store import ServiceStore
from .service_supervisor import RefreshSupervisor
from .service_worker import SOURCE_ADAPTERS, SubprocessAcquisitionRunner


Clock = Callable[[], datetime]


class JobRunner(Protocol):
    def run_once(self, *, worker_id: str): ...

    def cancel_active_work(self) -> None: ...


class EnrichmentBackend(Protocol):
    def embed_chunks(self): ...

    def extract_and_promote_entities(self): ...


class IndexPublisher(Protocol):
    def publish_index(self) -> str: ...


@dataclass(frozen=True)
class AcquisitionRuntime:
    supervisor: RefreshSupervisor
    ledger: ServiceStore
    scheduler: ServiceRefreshScheduler
    publisher: CorpusPublisher
    worker: AcquisitionRunner
    runner: AcquisitionJobRunner
    sources: tuple[str, ...]
    source_readiness: dict[str, bool]


class AcquisitionLoop:
    """Run one durable job at a time without coupling listener lifecycle to work."""

    def __init__(
        self,
        runner: JobRunner,
        *,
        worker_id: str | None = None,
        idle_seconds: float = 0.2,
        error_seconds: float = 1.0,
    ) -> None:
        if idle_seconds <= 0 or error_seconds <= 0:
            raise ValueError("loop delays must be positive")
        self.runner = runner
        self.worker_id = worker_id or f"service-{os.getpid()}-{uuid.uuid4().hex[:12]}"
        self.idle_seconds = idle_seconds
        self.error_seconds = error_seconds
        self.last_error_code: str | None = None
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    @property
    def is_alive(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def start(self) -> None:
        if self.is_alive:
            return
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._run,
            name="last30days-acquisition",
            daemon=True,
        )
        self._thread.start()

    def _run(self) -> None:
        while not self._stop_event.is_set():
            try:
                completed = self.runner.run_once(worker_id=self.worker_id)
                self.last_error_code = None
            except Exception:
                self.last_error_code = "acquisition_loop_failure"
                self._stop_event.wait(self.error_seconds)
                continue
            if completed is None:
                self._stop_event.wait(self.idle_seconds)

    def stop(self, *, timeout: float = 5.0) -> None:
        self._stop_event.set()
        cancel = getattr(self.runner, "cancel_active_work", None)
        if callable(cancel):
            cancel()
        if self._thread is not None:
            self._thread.join(timeout=timeout)


class EnrichmentLoop:
    """Run optional enrichment independently from query and acquisition paths."""

    def __init__(
        self,
        enrichment: EnrichmentBackend,
        publisher: IndexPublisher,
        *,
        interval_seconds: float = 30.0,
    ) -> None:
        if interval_seconds <= 0:
            raise ValueError("enrichment interval must be positive")
        self.enrichment = enrichment
        self.publisher = publisher
        self.interval_seconds = interval_seconds
        self.last_error_code: str | None = None
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    @property
    def is_alive(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def start(self) -> None:
        if self.is_alive:
            return
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._run,
            name="last30days-enrichment",
            daemon=True,
        )
        self._thread.start()

    def _run(self) -> None:
        while not self._stop_event.is_set():
            try:
                embeddings = self.enrichment.embed_chunks()
                entities = self.enrichment.extract_and_promote_entities()
                if embeddings.embeddings_written or entities.accepted_count:
                    self.publisher.publish_index()
                self.last_error_code = (
                    embeddings.error_code
                    if getattr(embeddings, "status", None) == "failed"
                    else None
                )
            except Exception:
                self.last_error_code = "enrichment_loop_failure"
            self._stop_event.wait(self.interval_seconds)

    def stop(self, *, timeout: float = 5.0) -> None:
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=timeout)


def _default_worker() -> SubprocessAcquisitionRunner:
    scripts_root = Path(__file__).resolve().parents[1]

    def environment(_request) -> dict[str, str]:
        existing = os.environ.get("PYTHONPATH")
        value = str(scripts_root)
        if existing:
            value = os.pathsep.join((value, existing))
        return {"PYTHONPATH": value}

    return SubprocessAcquisitionRunner(
        lambda _request: [sys.executable, "-m", "lib.service_acquisition_worker"],
        environment_resolver=environment,
    )


def build_acquisition_runtime(
    db_path: Path,
    retriever: HybridRetriever,
    *,
    worker: AcquisitionRunner | None = None,
    clock: Clock | None = None,
    default_sources: Sequence[str] = tuple(SOURCE_ADAPTERS),
    refresh_policy: RefreshPolicy | None = None,
    job_policy: JobRunnerPolicy | None = None,
) -> AcquisitionRuntime:
    """Build the host-owned policy objects; source code remains subprocess-only."""
    sources = tuple(sorted(set(default_sources)))
    source_readiness = {
        source: (
            True
            if source == "reddit"
            else bool(shutil.which("yt-dlp"))
            if source == "youtube"
            else False
        )
        for source in sources
    }
    supervisor = RefreshSupervisor(db_path, clock=clock)
    supervisor.initialize()
    ledger = ServiceStore(db_path)
    ledger.initialize()
    retriever.initialize()
    scheduler = ServiceRefreshScheduler(
        supervisor,
        ledger,
        refresh_policy
        or RefreshPolicy(
            default_sources=sources,
            freshness_seconds=86_400,
            max_attempts=2,
            budget_cents=100,
        ),
        clock=clock,
    )
    publisher = CorpusPublisher(db_path, retriever, clock=clock)
    acquisition_worker = worker or _default_worker()
    runner = AcquisitionJobRunner(
        supervisor,
        ledger,
        publisher,
        acquisition_worker,
        scheduler,
        job_policy or JobRunnerPolicy(),
        clock=clock,
    )
    return AcquisitionRuntime(
        supervisor=supervisor,
        ledger=ledger,
        scheduler=scheduler,
        publisher=publisher,
        worker=acquisition_worker,
        runner=runner,
        sources=sources,
        source_readiness=source_readiness,
    )
