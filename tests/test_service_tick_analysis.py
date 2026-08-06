from types import SimpleNamespace

import pytest

from lib.service_tick_analysis import (
    AnalysisAdapterError,
    MediaAnalysisInput,
    OcrAnalysis,
    default_analysis_adapter_registry,
)
from lib.service_tick_media import OcrRegion


def _input(**overrides):
    values = {
        "source_url": "https://example.test/image.png",
        "content": b"image-bytes",
        "mime_type": "image/png",
        "media_kind": "image",
        "alt_text": "A red chart showing quarterly revenue",
        "provided_ocr_regions": (),
        "provided_ocr_language": None,
        "provided_ocr_engine": None,
        "provided_ocr_engine_version": None,
        "provided_semantic_sidecar": None,
    }
    values.update(overrides)
    return MediaAnalysisInput(**values)


def test_local_tesseract_adapter_is_path_gated_and_parses_bounded_tsv():
    calls = []

    def runner(command, **kwargs):
        calls.append((command, kwargs))
        if command[-1] == "--version":
            return SimpleNamespace(returncode=0, stdout=b"tesseract 5.3.4\n", stderr=b"")
        return SimpleNamespace(
            returncode=0,
            stdout=(
                b"level\tpage_num\tblock_num\tpar_num\tline_num\tword_num\t"
                b"left\ttop\twidth\theight\tconf\ttext\n"
                b"5\t1\t1\t1\t1\t1\t10\t20\t30\t12\t87.5\tRevenue\n"
            ),
            stderr=b"",
        )

    registry = default_analysis_adapter_registry(
        which=lambda name: "/usr/bin/tesseract" if name == "tesseract" else None,
        runner=runner,
    )
    result = registry.require("tesseract_cli_v1", capability="ocr").analyze(
        _input()
    )

    assert result == OcrAnalysis(
        engine="tesseract",
        engine_version="5.3.4",
        detected_language="eng",
        regions=(OcrRegion(0, "Revenue", (10, 20, 40, 32), 0.875),),
    )
    assert calls[1][0] == [
        "/usr/bin/tesseract",
        "stdin",
        "stdout",
        "-l",
        "eng",
        "tsv",
    ]
    assert calls[1][1]["input"] == b"image-bytes"

    missing = default_analysis_adapter_registry(
        which=lambda _name: None,
        runner=runner,
    )
    with pytest.raises(AnalysisAdapterError, match="not installed"):
        missing.require("tesseract_cli_v1", capability="ocr")


def test_source_grounded_sidecar_uses_only_alt_and_completed_ocr():
    ocr = OcrAnalysis(
        engine="tesseract",
        engine_version="5.3.4",
        detected_language="eng",
        regions=(OcrRegion(0, "Revenue 2026", (0, 0, 20, 10), 0.9),),
    )
    analysis_input = _input().with_ocr(ocr)

    sidecar = default_analysis_adapter_registry(
        which=lambda _name: None
    ).require(
        "source_grounded_semantic_sidecar_v1", capability="semantic_sidecar"
    ).analyze(analysis_input)

    assert sidecar.literal_description == (
        "Source alt text: A red chart showing quarterly revenue\n"
        "OCR text: Revenue 2026"
    )
    assert sidecar.observable_entities == ()
    assert sidecar.observable_relationships == ()
    assert sidecar.objects_actions == ()
    assert sidecar.inferred_context == ()
    assert "revenue" in sidecar.search_terms
    assert sidecar.model_provider == "deterministic_local"
    assert sidecar.model_version == "source-grounded-v1"
    assert sidecar.uncertainty == (
        "Description is limited to source alt text and local OCR output.",
    )
    assert analysis_input.provided_ocr_engine == "tesseract"
    assert analysis_input.provided_ocr_regions == ocr.regions
