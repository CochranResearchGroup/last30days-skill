"""Durable replay ledger for intelligence-service contract envelopes."""

from __future__ import annotations

import hashlib
import json
import sqlite3
import time
from pathlib import Path

import store

from . import service_contracts as contracts


class EnvelopeConflictError(RuntimeError):
    """Raised when an immutable envelope ID is reused for different content."""


class EnvelopeIntegrityError(RuntimeError):
    """Raised when persisted envelope bytes do not match their recorded hash."""


class ServiceStore:
    """Deep persistence module for versioned service envelopes.

    Callers provide validated contract objects and stable IDs.  The module owns
    canonical serialization, hashing, idempotency, transactions, and contract
    revalidation on read.
    """

    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)

    def initialize(self) -> None:
        store.init_db(self.db_path)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=5)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA busy_timeout=5000")
        deadline = time.monotonic() + 5
        while True:
            try:
                conn.execute("PRAGMA journal_mode=WAL")
                break
            except sqlite3.OperationalError as exc:
                if (
                    "locked" not in str(exc).lower()
                    or time.monotonic() >= deadline
                ):
                    conn.close()
                    raise
                time.sleep(0.01)
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    @staticmethod
    def _canonical_payload(
        envelope: contracts.ContractEnvelope,
    ) -> tuple[str, str]:
        payload_json = json.dumps(
            envelope.to_dict(),
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        )
        digest = hashlib.sha256(payload_json.encode("utf-8")).hexdigest()
        return payload_json, digest

    def put_envelope(
        self,
        contract_name: str,
        envelope_id: str,
        envelope: contracts.ContractEnvelope,
    ) -> None:
        if envelope.CONTRACT_NAME != contract_name:
            raise contracts.ContractValidationError(
                f"contract name {contract_name!r} does not match "
                f"{envelope.CONTRACT_NAME!r}"
            )
        if not isinstance(envelope_id, str) or not envelope_id.strip():
            raise contracts.ContractValidationError(
                "envelope_id must be a non-empty string"
            )
        payload_json, digest = self._canonical_payload(envelope)
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            existing = conn.execute(
                """SELECT payload_sha256
                   FROM service_envelopes
                   WHERE envelope_type = ? AND envelope_id = ?""",
                (contract_name, envelope_id),
            ).fetchone()
            if existing is not None:
                if existing["payload_sha256"] != digest:
                    raise EnvelopeConflictError(
                        f"immutable envelope conflict: "
                        f"{contract_name}/{envelope_id}"
                    )
                conn.commit()
                return
            conn.execute(
                """INSERT INTO service_envelopes
                   (envelope_type, envelope_id, schema_version,
                    payload_json, payload_sha256)
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    contract_name,
                    envelope_id,
                    envelope.schema_version,
                    payload_json,
                    digest,
                ),
            )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def get_envelope(
        self, contract_name: str, envelope_id: str
    ) -> contracts.ContractEnvelope:
        conn = self._connect()
        try:
            row = conn.execute(
                """SELECT schema_version, payload_json, payload_sha256
                   FROM service_envelopes
                   WHERE envelope_type = ? AND envelope_id = ?""",
                (contract_name, envelope_id),
            ).fetchone()
        finally:
            conn.close()
        if row is None:
            raise KeyError(f"envelope not found: {contract_name}/{envelope_id}")
        actual_digest = hashlib.sha256(
            row["payload_json"].encode("utf-8")
        ).hexdigest()
        if actual_digest != row["payload_sha256"]:
            raise EnvelopeIntegrityError(
                f"envelope hash mismatch: {contract_name}/{envelope_id}"
            )
        try:
            payload = json.loads(row["payload_json"])
        except json.JSONDecodeError as exc:
            raise EnvelopeIntegrityError(
                f"envelope JSON is invalid: {contract_name}/{envelope_id}"
            ) from exc
        if payload.get("schema_version") != row["schema_version"]:
            raise EnvelopeIntegrityError(
                f"envelope schema version mismatch: "
                f"{contract_name}/{envelope_id}"
            )
        return contracts.parse_envelope(contract_name, payload)
