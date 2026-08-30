"""Installed, config-selected image analysis adapters for durable ticks."""

from __future__ import annotations

import csv
import io
import re
import shutil
import subprocess
from collections.abc import Callable, Iterable
from dataclasses import dataclass, replace

from .service_tick_media import OcrRegion, SemanticSidecar


class AnalysisAdapterError(ValueError):
    pass


class AnalysisOutputMissing(RuntimeError):
    pass


class AnalysisOutputEmpty(RuntimeError):
    def __init__(self, reason_code: str) -> None:
        super().__init__(reason_code)
        self.reason_code = reason_code


@dataclass(frozen=True)
class MediaAnalysisInput:
    source_url: str
    content: bytes
    mime_type: str
    media_kind: str
    alt_text: str | None
    provided_ocr_regions: tuple[OcrRegion, ...]
    provided_ocr_language: str | None
    provided_ocr_engine: str | None
    provided_ocr_engine_version: str | None
    provided_semantic_sidecar: SemanticSidecar | None

    def with_ocr(self, analysis: OcrAnalysis) -> MediaAnalysisInput:
        return replace(
            self,
            provided_ocr_regions=analysis.regions,
            provided_ocr_language=analysis.detected_language,
            provided_ocr_engine=analysis.engine,
            provided_ocr_engine_version=analysis.engine_version,
        )


@dataclass(frozen=True)
class OcrAnalysis:
    engine: str
    engine_version: str
    detected_language: str | None
    regions: tuple[OcrRegion, ...]


AnalysisCallable = Callable[[MediaAnalysisInput], object]


@dataclass(frozen=True)
class AnalysisAdapterSpec:
    adapter_type: str
    capability: str
    analyze: AnalysisCallable

    def __post_init__(self) -> None:
        if (
            not isinstance(self.adapter_type, str)
            or not self.adapter_type.strip()
            or len(self.adapter_type) > 128
        ):
            raise AnalysisAdapterError("analysis adapter_type is invalid")
        if self.capability not in {"ocr", "semantic_sidecar"}:
            raise AnalysisAdapterError("analysis adapter capability is unsupported")
        if not callable(self.analyze):
            raise AnalysisAdapterError("analysis adapter must be callable")


class AnalysisAdapterRegistry:
    def __init__(self, specs: Iterable[AnalysisAdapterSpec]) -> None:
        self._specs: dict[tuple[str, str], AnalysisAdapterSpec] = {}
        for spec in specs:
            key = (spec.adapter_type, spec.capability)
            if key in self._specs:
                raise AnalysisAdapterError(
                    f"duplicate analysis adapter: {spec.adapter_type}/{spec.capability}"
                )
            self._specs[key] = spec

    def require(self, adapter_type: str, *, capability: str) -> AnalysisAdapterSpec:
        spec = self._specs.get((adapter_type, capability))
        if spec is None:
            raise AnalysisAdapterError(
                f"analysis adapter is not installed: {adapter_type}/{capability}"
            )
        return spec


def _provided_ocr(value: MediaAnalysisInput) -> OcrAnalysis:
    if not value.provided_ocr_engine or not value.provided_ocr_engine_version:
        raise AnalysisOutputMissing("ocr_output_missing")
    return OcrAnalysis(
        engine=value.provided_ocr_engine,
        engine_version=value.provided_ocr_engine_version,
        detected_language=value.provided_ocr_language,
        regions=value.provided_ocr_regions,
    )


def _provided_sidecar(value: MediaAnalysisInput) -> SemanticSidecar:
    if value.provided_semantic_sidecar is None:
        raise AnalysisOutputMissing("semantic_sidecar_output_missing")
    return value.provided_semantic_sidecar


def _decode_output(value: object) -> str:
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value if isinstance(value, str) else ""


def _tesseract_version(path: str, runner: Callable[..., object]) -> str | None:
    try:
        completed = runner(
            [path, "--version"],
            capture_output=True,
            check=False,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if getattr(completed, "returncode", 1) != 0:
        return None
    match = re.search(
        r"(?im)^tesseract\s+([^\s]+)",
        _decode_output(getattr(completed, "stdout", b"")),
    )
    return match.group(1)[:128] if match else None


def _tesseract_analyzer(
    path: str,
    version: str,
    runner: Callable[..., object],
) -> AnalysisCallable:
    def analyze(value: MediaAnalysisInput) -> OcrAnalysis:
        try:
            completed = runner(
                [path, "stdin", "stdout", "-l", "eng", "tsv"],
                input=value.content,
                capture_output=True,
                check=False,
                timeout=60,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            raise AnalysisOutputMissing("tesseract_execution_failed") from exc
        if getattr(completed, "returncode", 1) != 0:
            raise AnalysisOutputMissing("tesseract_execution_failed")
        tsv = _decode_output(getattr(completed, "stdout", b""))
        if len(tsv.encode("utf-8")) > 4 * 1024 * 1024:
            raise AnalysisOutputMissing("tesseract_output_too_large")
        regions: list[OcrRegion] = []
        for row in csv.DictReader(io.StringIO(tsv), delimiter="\t"):
            if len(regions) >= 10_000 or row.get("level") != "5":
                continue
            text = (row.get("text") or "").strip()
            if not text:
                continue
            try:
                left = int(row["left"])
                top = int(row["top"])
                width = int(row["width"])
                height = int(row["height"])
                confidence = float(row["conf"])
            except (KeyError, TypeError, ValueError):
                continue
            if left < 0 or top < 0 or width <= 0 or height <= 0:
                continue
            regions.append(
                OcrRegion(
                    ordinal=len(regions),
                    text=text[:65_536],
                    bounding_box=(left, top, left + width, top + height),
                    confidence=max(0.0, min(1.0, confidence / 100.0)),
                )
            )
        return OcrAnalysis(
            engine="tesseract",
            engine_version=version,
            detected_language="eng",
            regions=tuple(regions),
        )

    return analyze


def _source_grounded_sidecar(value: MediaAnalysisInput) -> SemanticSidecar:
    sections: list[str] = []
    if value.alt_text and value.alt_text.strip():
        sections.append(f"Source alt text: {value.alt_text.strip()}")
    ocr_text = " ".join(
        region.text.strip()
        for region in value.provided_ocr_regions
        if region.text.strip()
    )
    if ocr_text:
        sections.append(f"OCR text: {ocr_text}")
    if not sections:
        raise AnalysisOutputEmpty("source_grounded_text_missing")
    literal_description = "\n".join(sections)[:16_384]
    terms: list[str] = []
    seen: set[str] = set()
    for match in re.finditer(r"[A-Za-z0-9][A-Za-z0-9_-]{1,63}", literal_description):
        term = match.group(0).casefold()
        if term not in seen:
            seen.add(term)
            terms.append(term)
        if len(terms) >= 64:
            break
    return SemanticSidecar(
        literal_description=literal_description,
        observable_entities=(),
        observable_relationships=(),
        objects_actions=(),
        inferred_context=(),
        search_terms=tuple(terms),
        uncertainty=(
            "Description is limited to source alt text and local OCR output.",
        ),
        model_provider="deterministic_local",
        model_version="source-grounded-v1",
        input_refs=("analysis-input",),
    )


def default_analysis_adapter_registry(
    *,
    which: Callable[[str], str | None] = shutil.which,
    runner: Callable[..., object] = subprocess.run,
) -> AnalysisAdapterRegistry:
    """Installed typed adapters, including PATH-gated local analysis."""
    specs = [
            AnalysisAdapterSpec(
                "provider_output_ocr_v1",
                "ocr",
                _provided_ocr,
            ),
            AnalysisAdapterSpec(
                "provider_output_semantic_sidecar_v1",
                "semantic_sidecar",
                _provided_sidecar,
            ),
            AnalysisAdapterSpec(
                "source_grounded_semantic_sidecar_v1",
                "semantic_sidecar",
                _source_grounded_sidecar,
            ),
    ]
    tesseract_path = which("tesseract")
    if tesseract_path:
        version = _tesseract_version(tesseract_path, runner)
        if version:
            specs.append(
                AnalysisAdapterSpec(
                    "tesseract_cli_v1",
                    "ocr",
                    _tesseract_analyzer(tesseract_path, version, runner),
                )
            )
    return AnalysisAdapterRegistry(specs)
