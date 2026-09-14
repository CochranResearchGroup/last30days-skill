"""Internal synthetic Unix service and manager client for the WI-007 drill.

This file never talks to systemd, loads service providers, or signals a PID.
The owning drill supervises every child through its original process handle.
"""

from __future__ import annotations

import hashlib
import json
import os
import signal
import socket
import socketserver
import sqlite3
import sys
from http.server import BaseHTTPRequestHandler
from pathlib import Path


def manager() -> None:
    endpoint = os.environ["WI007_MANAGER_SOCKET"]
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as connection:
        connection.settimeout(10)
        connection.connect(endpoint)
        connection.sendall(json.dumps(sys.argv[1:]).encode() + b"\n")
        reply = connection.makefile("rb").readline(16384)
    result = json.loads(reply)
    print(result["message"])
    raise SystemExit(result["returncode"])


def serve(root: Path, schema: int, unhealthy: bool) -> None:
    release = root / "data/last30days/service/current"
    version = (release / "VERSION").read_text().strip()
    database = root / "data/last30days/research.db"
    database.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(database) as connection:
        connection.execute(
            "CREATE TABLE IF NOT EXISTS schema_version(version INTEGER PRIMARY KEY)"
        )
        current = (
            connection.execute("SELECT MAX(version) FROM schema_version").fetchone()[0]
            or 0
        )
        if current > schema:
            raise SystemExit("fixture_schema_incompatible")
        connection.executemany(
            "INSERT INTO schema_version VALUES (?)",
            [(n,) for n in range(current + 1, schema + 1)],
        )
        connection.execute(
            "CREATE TABLE IF NOT EXISTS sentinel(value TEXT PRIMARY KEY)"
        )
        connection.commit()
    contract = hashlib.sha256(
        (release / "schemas/service-contracts-v1.json").read_bytes()
    ).hexdigest()
    payload = json.dumps(
        {
            "service_version": version,
            "database_schema_version": schema,
            "runtime_manifest_sha256": hashlib.sha256(
                (release / "runtime-manifest.json").read_bytes()
            ).hexdigest(),
            "status": "degraded" if unhealthy else "ready",
        }
    ).encode()

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path != "/v1/service-info":
                self.send_error(404)
                return
            self.send_response(200)
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("X-Last30days-Contract-SHA256", contract)
            self.end_headers()
            self.wfile.write(payload)

        def log_message(self, *_args):
            pass

    endpoint = root / "run/service.sock"
    endpoint.unlink(missing_ok=True)
    with socketserver.UnixStreamServer(str(endpoint), Handler) as server:
        os.chmod(endpoint, 0o600)

        def stop(*_args):
            raise SystemExit(0)

        signal.signal(signal.SIGTERM, stop)
        try:
            server.serve_forever(poll_interval=0.05)
        finally:
            endpoint.unlink(missing_ok=True)


if __name__ == "__main__":
    if len(sys.argv) == 5 and sys.argv[1] == "serve":
        serve(Path(sys.argv[2]), int(sys.argv[3]), sys.argv[4] == "unhealthy")
    else:
        manager()
