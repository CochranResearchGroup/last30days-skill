"""Ephemeral provider-free service join for P3 acceptance."""

from __future__ import annotations

import hashlib
import json
import sqlite3
import tempfile
import threading
import urllib.request
from dataclasses import asdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from .contracts import ContractError, SealedCase, TransportObservation, TransportTracer


_MAX_RESPONSE_BYTES = 131_072


def _decode_observation(payload: dict[str, Any]) -> TransportObservation:
    allowed = {
        "outcome",
        "transport_success",
        "item_count",
        "request_count",
        "safe_reason_code",
        "accounting_confidence",
        "raw_safe_sha256",
        "details",
    }
    if set(payload) != allowed:
        raise ContractError("isolated_join_response_schema_mismatch")
    return TransportObservation(**payload)


class IsolatedServiceJoin:
    """Run one tracer behind an owned loopback service and temporary SQLite DB."""

    def __call__(
        self,
        case: SealedCase,
        tracer: TransportTracer,
        *,
        item_limit: int,
    ) -> tuple[TransportObservation, dict[str, Any]]:
        owner = "wi010-" + hashlib.sha256(case.case.case_id.encode()).hexdigest()[:12]
        holder: dict[str, Any] = {}
        with tempfile.TemporaryDirectory(prefix=f"{owner}-") as temp_name:
            temp_root = Path(temp_name)
            database = temp_root / "acceptance.sqlite3"
            with sqlite3.connect(database) as connection:
                connection.execute(
                    "CREATE TABLE samples(case_id TEXT PRIMARY KEY, adapter_id TEXT NOT NULL, payload_sha256 TEXT NOT NULL)"
                )

            class Handler(BaseHTTPRequestHandler):
                def log_message(self, _format, *args):
                    return

                def do_POST(self):
                    if self.path != "/v1/provider-acceptance/execute":
                        self.send_error(404)
                        return
                    length = int(self.headers.get("Content-Length", "0"))
                    request = json.loads(self.rfile.read(length))
                    if request != {"case_id": case.case.case_id, "adapter_id": case.case.adapter_id}:
                        self.send_error(409)
                        return
                    try:
                        observation = tracer(case, item_limit=item_limit)
                        payload = asdict(observation)
                        with sqlite3.connect(database) as connection:
                            connection.execute(
                                "INSERT INTO samples VALUES (?, ?, ?)",
                                (case.case.case_id, case.case.adapter_id, observation.raw_safe_sha256),
                            )
                        body = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
                        holder["completed"] = True
                        self.send_response(200)
                        self.send_header("Content-Type", "application/json")
                        self.send_header("Content-Length", str(len(body)))
                        self.end_headers()
                        self.wfile.write(body)
                    except Exception as exc:  # cleanup remains the primary invariant
                        holder["error"] = type(exc).__name__
                        self.send_error(500)

            server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
            thread = threading.Thread(target=server.serve_forever, name=owner, daemon=False)
            thread.start()
            port = server.server_address[1]
            try:
                request = urllib.request.Request(
                    f"http://127.0.0.1:{port}/v1/provider-acceptance/execute",
                    data=json.dumps({"case_id": case.case.case_id, "adapter_id": case.case.adapter_id}).encode(),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with urllib.request.urlopen(request, timeout=10) as response:
                    body = response.read(_MAX_RESPONSE_BYTES + 1)
                if len(body) > _MAX_RESPONSE_BYTES:
                    raise ContractError("isolated_join_response_too_large")
                observation = _decode_observation(json.loads(body))
                with sqlite3.connect(database) as connection:
                    row = connection.execute(
                        "SELECT adapter_id, payload_sha256 FROM samples WHERE case_id = ?",
                        (case.case.case_id,),
                    ).fetchone()
                if row != (case.case.adapter_id, observation.raw_safe_sha256):
                    raise ContractError("isolated_join_database_mismatch")
                return observation, {
                    "complete": True,
                    "owner_census": 0,
                    "service_identity": owner,
                    "database_committed": True,
                    "socket_kind": "loopback_tcp",
                    "socket_closed": True,
                }
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)
                if thread.is_alive():
                    raise ContractError("isolated_join_teardown_failed")
