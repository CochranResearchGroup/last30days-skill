"""Content-addressed media plus independent OCR and semantic sidecars."""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import tempfile
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

import store


Clock = Callable[[], datetime]


def _canonical_json(value: object) -> str:
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def _sha256(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def _digest(value: object) -> str:
    return _sha256(_canonical_json(value).encode("utf-8"))


def _stable_id(prefix: str, value: object) -> str:
    return f"{prefix}-{hashlib.sha256(_canonical_json(value).encode()).hexdigest()[:32]}"


def _text(value: object, field: str, maximum: int = 4_096) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > maximum:
        raise ValueError(f"{field} must be a bounded non-empty string")
    return value


def _optional_text(value: object, field: str, maximum: int = 16_384) -> str | None:
    if value is None:
        return None
    return _text(value, field, maximum)


def _strings(values: Iterable[object], field: str) -> tuple[str, ...]:
    result = tuple(_text(value, field) for value in values)
    if len(result) > 1_000:
        raise ValueError(f"{field} is too large")
    return result


def _now(clock: Clock) -> str:
    value = clock()
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("clock must return a timezone-aware datetime")
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class MediaAssetReceipt:
    asset_id: str
    parent_version_id: str
    source_url: str
    content_hash: str
    mime_type: str
    media_kind: str
    alt_text: str | None
    byte_size: int
    storage_ref: str
    access_partition_id: str
    retention_class: str


@dataclass(frozen=True)
class DerivativeReceipt:
    derivative_id: str
    asset_id: str
    derivative_kind: str
    derivative_version: str
    input_digest: str
    output_digest: str
    access_partition_id: str
    retention_class: str
    state: str


@dataclass(frozen=True)
class OcrRegion:
    ordinal: int
    text: str
    bounding_box: tuple[int, int, int, int]
    confidence: float

    def __post_init__(self) -> None:
        if isinstance(self.ordinal, bool) or not isinstance(self.ordinal, int) or self.ordinal < 0:
            raise ValueError("OCR ordinal must be non-negative")
        if not isinstance(self.text, str) or len(self.text) > 65_536:
            raise ValueError("OCR text must be bounded")
        if (
            len(self.bounding_box) != 4
            or any(isinstance(value, bool) or not isinstance(value, int) or value < 0 for value in self.bounding_box)
            or self.bounding_box[2] <= self.bounding_box[0]
            or self.bounding_box[3] <= self.bounding_box[1]
        ):
            raise ValueError("OCR bounding box is invalid")
        if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)) or not 0 <= float(self.confidence) <= 1:
            raise ValueError("OCR confidence must be between zero and one")

    def to_dict(self) -> dict[str, object]:
        return {
            "ordinal": self.ordinal,
            "text": self.text,
            "bounding_box": list(self.bounding_box),
            "confidence": float(self.confidence),
        }


@dataclass(frozen=True)
class SemanticSidecar:
    literal_description: str
    observable_entities: tuple[str, ...]
    observable_relationships: tuple[str, ...]
    objects_actions: tuple[str, ...]
    inferred_context: tuple[str, ...]
    search_terms: tuple[str, ...]
    uncertainty: tuple[str, ...]
    model_provider: str
    model_version: str
    input_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        _text(self.literal_description, "literal_description", 16_384)
        for field in (
            "observable_entities",
            "observable_relationships",
            "objects_actions",
            "inferred_context",
            "search_terms",
            "uncertainty",
        ):
            _strings(getattr(self, field), field)
        _text(self.model_provider, "model_provider", 128)
        _text(self.model_version, "model_version", 128)
        if not _strings(self.input_refs, "input_refs"):
            raise ValueError("sidecar input_refs must not be empty")

    def to_dict(self) -> dict[str, object]:
        return {
            "literal_description": self.literal_description,
            "observable_entities": list(self.observable_entities),
            "observable_relationships": list(self.observable_relationships),
            "objects_actions": list(self.objects_actions),
            "inferred_context": list(self.inferred_context),
            "search_terms": list(self.search_terms),
            "uncertainty": list(self.uncertainty),
            "model_provider": self.model_provider,
            "model_version": self.model_version,
            "input_refs": list(self.input_refs),
        }


class ContentAddressedArtifactStore:
    """User-scoped byte store; database receipts survive optional byte GC."""

    def __init__(self, root: Path) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)

    def put(self, content: bytes, *, access_partition_id: str) -> tuple[str, str]:
        if not isinstance(content, bytes):
            raise TypeError("artifact content must be bytes")
        partition = _text(access_partition_id, "access_partition_id", 256)
        content_hash = _sha256(content)
        raw_hash = content_hash.removeprefix("sha256:")
        partition_hash = hashlib.sha256(partition.encode("utf-8")).hexdigest()[:16]
        relative = PurePosixPath("objects", partition_hash, raw_hash[:2], raw_hash)
        target = self.root.joinpath(*relative.parts)
        target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        if target.exists():
            if _sha256(target.read_bytes()) != content_hash:
                raise RuntimeError("artifact content hash conflict")
        else:
            with tempfile.NamedTemporaryFile(
                mode="wb", dir=target.parent, prefix=".artifact-", delete=False
            ) as handle:
                handle.write(content)
                temporary = Path(handle.name)
            os.chmod(temporary, 0o600)
            os.replace(temporary, target)
        return relative.as_posix(), content_hash

    def read(self, storage_ref: str) -> bytes:
        reference = PurePosixPath(storage_ref)
        if reference.is_absolute() or ".." in reference.parts:
            raise ValueError("artifact reference is unsafe")
        return self.root.joinpath(*reference.parts).read_bytes()


class MediaDerivativePublisher:
    def __init__(
        self,
        db_path: Path,
        artifacts: ContentAddressedArtifactStore,
        *,
        clock: Clock | None = None,
    ) -> None:
        self.db_path = Path(db_path)
        self.artifacts = artifacts
        self.clock = clock or (lambda: datetime.now(timezone.utc))
        store.init_db(self.db_path)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=5)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    @staticmethod
    def _asset_from_row(row: Mapping[str, object]) -> MediaAssetReceipt:
        return MediaAssetReceipt(
            asset_id=str(row["asset_id"]),
            parent_version_id=str(row["parent_version_id"]),
            source_url=str(row["source_url"]),
            content_hash=str(row["content_hash"]),
            mime_type=str(row["mime_type"]),
            media_kind=str(row["media_kind"]),
            alt_text=row["alt_text"] if isinstance(row["alt_text"], str) else None,
            byte_size=int(row["byte_size"]),
            storage_ref=str(row["storage_ref"]),
            access_partition_id=str(row["access_partition_id"]),
            retention_class=str(row["retention_class"]),
        )

    def store_asset_in_transaction(
        self,
        conn: sqlite3.Connection,
        *,
        parent_version_id: str,
        source_url: str,
        content: bytes,
        mime_type: str,
        media_kind: str,
        alt_text: str | None,
        access_partition_id: str,
        retention_class: str,
    ) -> MediaAssetReceipt:
        parent = _text(parent_version_id, "parent_version_id", 128)
        url = _text(source_url, "source_url", 4_096)
        mime = _text(mime_type, "mime_type", 256)
        if media_kind not in {"image", "video_thumbnail", "rendered_page"}:
            raise ValueError("media_kind is unsupported")
        alt = _optional_text(alt_text, "alt_text")
        partition = _text(access_partition_id, "access_partition_id", 256)
        retention = _text(retention_class, "retention_class", 64)
        storage_ref, content_hash = self.artifacts.put(
            content, access_partition_id=partition
        )
        identity = {
            "parent_version_id": parent,
            "source_url": url,
            "content_hash": content_hash,
            "media_kind": media_kind,
            "access_partition_id": partition,
        }
        asset_id = _stable_id("media-asset", identity)
        conn.execute(
            """INSERT OR IGNORE INTO service_media_assets (
                   asset_id, parent_version_id, source_url, content_hash,
                   mime_type, media_kind, alt_text, byte_size, storage_ref,
                   access_partition_id, retention_class, created_at
               ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                asset_id,
                parent,
                url,
                content_hash,
                mime,
                media_kind,
                alt,
                len(content),
                storage_ref,
                partition,
                retention,
                _now(self.clock),
            ),
        )
        row = conn.execute(
            "SELECT * FROM service_media_assets WHERE asset_id = ?", (asset_id,)
        ).fetchone()
        expected = (mime, alt, len(content), storage_ref, retention)
        observed = tuple(
            row[key]
            for key in (
                "mime_type",
                "alt_text",
                "byte_size",
                "storage_ref",
                "retention_class",
            )
        )
        if observed != expected:
            raise ValueError("immutable media asset conflict")
        return self._asset_from_row(row)

    def store_asset(
        self,
        *,
        parent_version_id: str,
        source_url: str,
        content: bytes,
        mime_type: str,
        media_kind: str,
        alt_text: str | None,
        access_partition_id: str,
        retention_class: str,
    ) -> MediaAssetReceipt:
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            receipt = self.store_asset_in_transaction(
                conn,
                parent_version_id=parent_version_id,
                source_url=source_url,
                content=content,
                mime_type=mime_type,
                media_kind=media_kind,
                alt_text=alt_text,
                access_partition_id=access_partition_id,
                retention_class=retention_class,
            )
            conn.commit()
            return receipt
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _asset(self, conn: sqlite3.Connection, asset_id: str) -> sqlite3.Row:
        row = conn.execute(
            "SELECT * FROM service_media_assets WHERE asset_id = ?", (asset_id,)
        ).fetchone()
        if row is None:
            raise KeyError(f"unknown media asset: {asset_id}")
        return row

    def _publish_derivative(
        self,
        conn: sqlite3.Connection,
        *,
        asset: sqlite3.Row,
        kind: str,
        version: str,
        input_digest: str,
        output: object,
        state: str,
    ) -> DerivativeReceipt:
        identity = {
            "asset_id": asset["asset_id"],
            "kind": kind,
            "version": version,
            "input_digest": input_digest,
        }
        derivative_id = _stable_id("media-derivative", identity)
        output_json = _canonical_json(output)
        output_digest = _sha256(output_json.encode("utf-8"))
        conn.execute(
            """INSERT OR IGNORE INTO service_media_derivatives (
                   derivative_id, asset_id, derivative_kind, derivative_version,
                   input_digest, output_digest, output_json, access_partition_id,
                   retention_class, state, created_at
               ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                derivative_id,
                asset["asset_id"],
                kind,
                version,
                input_digest,
                output_digest,
                output_json,
                asset["access_partition_id"],
                asset["retention_class"],
                state,
                _now(self.clock),
            ),
        )
        row = conn.execute(
            "SELECT * FROM service_media_derivatives WHERE derivative_id = ?",
            (derivative_id,),
        ).fetchone()
        if row["output_digest"] != output_digest:
            raise ValueError("immutable media derivative conflict")
        return DerivativeReceipt(
            derivative_id=derivative_id,
            asset_id=str(asset["asset_id"]),
            derivative_kind=kind,
            derivative_version=version,
            input_digest=input_digest,
            output_digest=output_digest,
            access_partition_id=str(asset["access_partition_id"]),
            retention_class=str(asset["retention_class"]),
            state=state,
        )

    def publish_ocr(
        self,
        asset_id: str,
        *,
        engine: str,
        engine_version: str,
        detected_language: str | None,
        regions: tuple[OcrRegion, ...],
    ) -> DerivativeReceipt:
        engine_name = _text(engine, "engine", 128)
        version = _text(engine_version, "engine_version", 128)
        language = _optional_text(detected_language, "detected_language", 64)
        if len({region.ordinal for region in regions}) != len(regions):
            raise ValueError("OCR region ordinals must be unique")
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            asset = self._asset(conn, asset_id)
            output = {
                "engine": engine_name,
                "engine_version": version,
                "detected_language": language,
                "regions": [region.to_dict() for region in regions],
                "normalized_full_text": "\n".join(
                    region.text for region in sorted(regions, key=lambda item: item.ordinal)
                ),
            }
            receipt = self._publish_derivative(
                conn,
                asset=asset,
                kind="ocr",
                version=f"{engine_name}:{version}",
                input_digest=str(asset["content_hash"]),
                output=output,
                state="success" if regions else "empty",
            )
            for region in regions:
                conn.execute(
                    """INSERT OR IGNORE INTO service_ocr_regions (
                           derivative_id, ordinal, text, bounding_box_json,
                           confidence, detected_language
                       ) VALUES (?, ?, ?, ?, ?, ?)""",
                    (
                        receipt.derivative_id,
                        region.ordinal,
                        region.text,
                        _canonical_json(list(region.bounding_box)),
                        float(region.confidence),
                        language,
                    ),
                )
            conn.commit()
            return receipt
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def publish_sidecar(
        self, asset_id: str, sidecar: SemanticSidecar
    ) -> DerivativeReceipt:
        if not isinstance(sidecar, SemanticSidecar):
            raise TypeError("sidecar must be SemanticSidecar")
        output = sidecar.to_dict()
        input_digest = _digest(list(sidecar.input_refs))
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            asset = self._asset(conn, asset_id)
            receipt = self._publish_derivative(
                conn,
                asset=asset,
                kind="semantic_sidecar",
                version=f"{sidecar.model_provider}:{sidecar.model_version}",
                input_digest=input_digest,
                output=output,
                state="success",
            )
            conn.execute(
                """INSERT OR IGNORE INTO service_semantic_sidecars (
                       derivative_id, literal_description,
                       observable_entities_json, observable_relationships_json,
                       objects_actions_json, inferred_context_json,
                       search_terms_json, uncertainty_json, model_provider,
                       model_version, input_refs_json
                   ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    receipt.derivative_id,
                    sidecar.literal_description,
                    _canonical_json(list(sidecar.observable_entities)),
                    _canonical_json(list(sidecar.observable_relationships)),
                    _canonical_json(list(sidecar.objects_actions)),
                    _canonical_json(list(sidecar.inferred_context)),
                    _canonical_json(list(sidecar.search_terms)),
                    _canonical_json(list(sidecar.uncertainty)),
                    sidecar.model_provider,
                    sidecar.model_version,
                    _canonical_json(list(sidecar.input_refs)),
                ),
            )
            conn.commit()
            return receipt
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def publish_failure(
        self,
        asset_id: str,
        *,
        derivative_kind: str,
        adapter_type: str,
        safe_error_code: str,
        input_refs: tuple[str, ...],
    ) -> DerivativeReceipt:
        if derivative_kind not in {"ocr", "semantic_sidecar"}:
            raise ValueError("derivative failure kind is unsupported")
        adapter = _text(adapter_type, "adapter_type", 128)
        error_code = _text(safe_error_code, "safe_error_code", 128)
        references = _strings(input_refs, "input_refs")
        if not references:
            raise ValueError("derivative failure input refs must not be empty")
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            asset = self._asset(conn, asset_id)
            receipt = self._publish_derivative(
                conn,
                asset=asset,
                kind=derivative_kind,
                version=f"{adapter}:failure-v1",
                input_digest=_digest(list(references)),
                output={
                    "adapter_type": adapter,
                    "safe_error_code": error_code,
                    "input_refs": list(references),
                },
                state="failure",
            )
            conn.commit()
            return receipt
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def publish_empty(
        self,
        asset_id: str,
        *,
        derivative_kind: str,
        adapter_type: str,
        reason_code: str,
        input_refs: tuple[str, ...],
    ) -> DerivativeReceipt:
        if derivative_kind not in {"ocr", "semantic_sidecar"}:
            raise ValueError("derivative empty kind is unsupported")
        adapter = _text(adapter_type, "adapter_type", 128)
        reason = _text(reason_code, "reason_code", 128)
        references = _strings(input_refs, "input_refs")
        if not references:
            raise ValueError("derivative empty input refs must not be empty")
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            asset = self._asset(conn, asset_id)
            receipt = self._publish_derivative(
                conn,
                asset=asset,
                kind=derivative_kind,
                version=f"{adapter}:empty-v1",
                input_digest=_digest(list(references)),
                output={
                    "adapter_type": adapter,
                    "reason_code": reason,
                    "input_refs": list(references),
                },
                state="empty",
            )
            conn.commit()
            return receipt
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def ocr_citation(
        self, derivative_id: str, *, region_ordinal: int
    ) -> dict[str, object]:
        conn = self._connect()
        try:
            row = conn.execute(
                """SELECT a.parent_version_id, a.asset_id, a.content_hash,
                          a.source_url, d.derivative_id, d.derivative_version,
                          r.ordinal, r.confidence
                   FROM service_media_derivatives AS d
                   JOIN service_media_assets AS a ON a.asset_id = d.asset_id
                   JOIN service_ocr_regions AS r
                     ON r.derivative_id = d.derivative_id
                   WHERE d.derivative_id = ? AND d.derivative_kind = 'ocr'
                     AND r.ordinal = ?""",
                (derivative_id, region_ordinal),
            ).fetchone()
            if row is None:
                raise KeyError("OCR citation target does not exist")
            return {
                "parent_version_id": row["parent_version_id"],
                "media_asset_id": row["asset_id"],
                "content_hash": row["content_hash"],
                "source_url": row["source_url"],
                "derivative_id": row["derivative_id"],
                "derivative_version": row["derivative_version"],
                "ocr_region_ordinal": row["ordinal"],
                "ocr_region_confidence": row["confidence"],
            }
        finally:
            conn.close()
