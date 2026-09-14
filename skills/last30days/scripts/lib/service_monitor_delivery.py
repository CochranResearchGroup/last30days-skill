"""Disabled delivery intents; only an explicit provider-free recording sink runs."""

import json

from . import service_monitor_contracts as c
from .service_monitor_views import _digest, _json
from .service_monitors import MonitorKernelError


class RecordingSink:
    """Test-only, in-memory effect target. No credentials, sockets or channels."""

    def __init__(self, *, failures=0):
        self.failures = failures
        self.effects = {}

    def send(self, key, digest):
        if key in self.effects:
            return self.effects[key]
        if self.failures:
            self.failures -= 1
            return {"status": "failed", "effect": "none"}
        receipt = {
            "status": "sent",
            "effect": "recording_sink",
            "digest_id": digest["digest_id"],
        }
        self.effects[key] = receipt
        return receipt


class MonitorDelivery:
    def __init__(self, records):
        self.records = records
        conn = records.repository._connect()
        try:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS service_monitor_delivery_attempts (
                    intent_id TEXT NOT NULL, attempt INTEGER NOT NULL,
                    state TEXT NOT NULL CHECK(state IN ('pending', 'failed', 'sent')),
                    payload_json TEXT, payload_sha256 TEXT,
                    PRIMARY KEY(intent_id, attempt)
                );
                CREATE TRIGGER IF NOT EXISTS monitor_attempts_terminal
                BEFORE UPDATE ON service_monitor_delivery_attempts
                WHEN OLD.state != 'pending' OR NEW.intent_id != OLD.intent_id
                    OR NEW.attempt != OLD.attempt BEGIN
                    SELECT RAISE(ABORT, 'delivery attempt is immutable'); END;
                CREATE TRIGGER IF NOT EXISTS monitor_attempts_no_delete
                BEFORE DELETE ON service_monitor_delivery_attempts BEGIN
                    SELECT RAISE(ABORT, 'delivery attempt is immutable'); END;
            """)
        finally:
            conn.close()

    def preference(self, monitor_id, partition, version=None):
        if version is None:
            conn = self.records.repository._connect()
            try:
                rows = conn.execute(
                    """SELECT payload_json FROM service_monitor_records
                    WHERE kind='delivery_preference' AND owner_id=? AND partition_id=?""",
                    (monitor_id, partition),
                ).fetchall()
            finally:
                conn.close()
            version = max((json.loads(row[0])["version"] for row in rows), default=0)
        if not version:
            return {
                "schema_version": 1,
                "monitor_id": monitor_id,
                "version": 0,
                "mode": "disabled",
                "channel_config_ref": None,
            }
        return self.records.get(
            "delivery_preference", f"{monitor_id}:{version}", partition
        )

    def set_preference(self, spec, expected_version, channel_config_ref):
        current = self.preference(spec.monitor_id, spec.access_partition_id)
        if current["version"] != expected_version:
            raise MonitorKernelError(
                c.MonitorErrorCode.INVALID_REVISION, "delivery preference changed"
            )
        payload = {
            "schema_version": 1,
            "monitor_id": spec.monitor_id,
            "version": expected_version + 1,
            "mode": "disabled",
            "channel_config_ref": channel_config_ref,
        }
        return self.records.put(
            "delivery_preference",
            f"{spec.monitor_id}:{expected_version + 1}",
            spec.access_partition_id,
            spec.monitor_id,
            payload,
        )

    def prepare(
        self, spec, digest, version, *, parent=None, reason=None, request_id=None
    ):
        preference = self.preference(spec.monitor_id, spec.access_partition_id, version)
        if version < 1:
            raise c.MonitorContractError(
                "delivery requires an explicit preference version"
            )
        parent_receipt = None
        if parent:
            parent_receipt = self.latest_attempt(parent["intent_id"])
            if not parent_receipt or parent_receipt["status"] != "sent":
                raise MonitorKernelError(
                    c.MonitorErrorCode.INVALID_LIFECYCLE,
                    "resend requires a successful parent receipt",
                )
        payload = {
            "schema_version": 1,
            "monitor_id": spec.monitor_id,
            "run_id": digest["run_id"],
            "digest_id": digest["digest_id"],
            "access_partition_id": spec.access_partition_id,
            "preference_version": version,
            "channel_config_ref": preference["channel_config_ref"],
            "mode": "disabled",
            "authorization_receipt": None,
            "parent_intent_id": None if parent is None else parent["intent_id"],
            "parent_receipt_id": None
            if parent_receipt is None
            else parent_receipt["receipt_id"],
            "resend_reason": reason,
            "request_id": request_id,
        }
        payload["intent_id"] = "delivery-" + _digest(payload)[:32]
        payload["idempotency_key"] = payload["intent_id"]
        if request_id is not None:
            binding = (
                "resend-"
                + _digest([spec.access_partition_id, spec.monitor_id, request_id])[:32]
            )
            self.records.put(
                "resend_request",
                binding,
                spec.access_partition_id,
                spec.monitor_id,
                payload,
            )
        return self.records.put(
            "delivery_intent",
            payload["intent_id"],
            spec.access_partition_id,
            spec.monitor_id,
            payload,
        )

    def latest_attempt(self, intent_id):
        conn = self.records.repository._connect()
        try:
            row = conn.execute(
                "SELECT * FROM service_monitor_delivery_attempts WHERE intent_id=? ORDER BY attempt DESC LIMIT 1",
                (intent_id,),
            ).fetchone()
        finally:
            conn.close()
        if row is None:
            return None
        if row["state"] == "pending":
            raise MonitorKernelError(
                c.MonitorErrorCode.VIEW_UNAVAILABLE,
                "delivery effect ambiguous; no retry",
            )
        result = json.loads(row["payload_json"])
        if _digest(result) != row["payload_sha256"]:
            raise MonitorKernelError(
                c.MonitorErrorCode.IMMUTABLE_CONFLICT,
                "delivery receipt integrity failure",
            )
        return result

    def dispatch(self, intent_id, partition, *, sink=None):
        if type(sink) is not RecordingSink:
            raise MonitorKernelError(
                c.MonitorErrorCode.INVALID_LIFECYCLE, "delivery disabled"
            )
        intent = self.records.get("delivery_intent", intent_id, partition)
        digest = self.records.get("digest", intent["run_id"], partition)
        conn = self.records.repository._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute(
                "SELECT attempt, state FROM service_monitor_delivery_attempts WHERE intent_id=? ORDER BY attempt DESC LIMIT 1",
                (intent_id,),
            ).fetchone()
            if row and row["state"] == "sent":
                conn.rollback()
                return self.latest_attempt(intent_id)
            if row and row["state"] == "pending":
                raise MonitorKernelError(
                    c.MonitorErrorCode.VIEW_UNAVAILABLE,
                    "delivery effect ambiguous; no retry",
                )
            attempt = 1 if row is None else row["attempt"] + 1
            if attempt > 2:
                raise MonitorKernelError(
                    c.MonitorErrorCode.INVALID_LIFECYCLE,
                    "delivery attempt bound reached",
                )
            conn.execute(
                "INSERT INTO service_monitor_delivery_attempts VALUES (?, ?, 'pending', NULL, NULL)",
                (intent_id, attempt),
            )
            conn.commit()
            # A crash/exception leaves pending, which must never auto-retry.
            outcome = sink.send(intent["idempotency_key"], digest)
            result = {
                "schema_version": 1,
                "receipt_id": "delivery-receipt-" + _digest([intent_id, attempt])[:32],
                "intent_id": intent_id,
                "idempotency_key": intent["idempotency_key"],
                "attempt": attempt,
                **outcome,
            }
            conn.execute(
                "UPDATE service_monitor_delivery_attempts SET state=?, payload_json=?, payload_sha256=? WHERE intent_id=? AND attempt=?",
                (result["status"], _json(result), _digest(result), intent_id, attempt),
            )
            conn.commit()
            return result
        finally:
            conn.close()
