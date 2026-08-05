"""Installed, config-selected image analysis adapters for durable ticks."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass

from .service_tick_media import OcrRegion, SemanticSidecar


class AnalysisAdapterError(ValueError):
    pass


class AnalysisOutputMissing(RuntimeError):
    pass


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


def default_analysis_adapter_registry() -> AnalysisAdapterRegistry:
    """Adapters for workers that already return bounded, typed image analysis."""
    return AnalysisAdapterRegistry(
        (
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
        )
    )
