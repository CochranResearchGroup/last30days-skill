"""Real Unix-socket transport tests for the local intelligence service."""

import os
import socket
import stat
import threading

import pytest

from lib import service_contracts as contracts
from lib.service_client import ServiceClient, ServiceClientError
from lib.service_http import ServiceAlreadyRunningError, UnixServiceServer


class StubApplication:
    def health(self):
        return {
            "status": "ready",
            "service_version": "0.1.0",
            "schema_version": 1,
        }

    def service_info(self):
        return contracts.ServiceInfo.from_dict(
            {
                "schema_version": 1,
                "service_version": "0.1.0",
                "database_schema_version": 3,
                "status": "ready",
                "capabilities": ["cache_query"],
                "sources": {},
                "freshness_policies": [
                    "cache_only",
                    "prefer_cache",
                    "refresh_if_stale",
                    "force_refresh",
                ],
                "response_modes": ["evidence", "brief"],
                "limits": {
                    "default_top_k": 8,
                    "max_top_k": 100,
                    "max_chars": 65536,
                },
                "index": {
                    "version": "index-empty",
                    "document_count": 0,
                    "embedding_model": None,
                },
                "transport": "unix",
            }
        )

    def query(self, request):
        return contracts.QueryResponse.from_dict(
            {
                "schema_version": 1,
                "request_id": request.request_id,
                "index_version": "index-empty",
                "cache_status": "miss",
                "generated_at": "2026-07-24T12:00:00Z",
                "evidence": [],
                "brief": None,
                "job_id": None,
                "diagnostics_available": False,
                "truncated": False,
                "next_cursor": None,
            }
        )

    def job(self, job_id):
        if job_id != "job-001":
            raise KeyError(job_id)
        return contracts.JobRecord.from_dict(
            {
                "schema_version": 1,
                "job_id": job_id,
                "job_type": "refresh",
                "dedupe_key": "sha256:dedupe",
                "state": "published",
                "query_request_id": "query-001",
                "attempts": 1,
                "max_attempts": 2,
                "budget_cents": 100,
                "spent_cents": 0,
                "lease_generation": 1,
                "lease_owner": None,
                "lease_expires_at": None,
                "not_before_at": None,
                "created_at": "2026-07-24T12:00:00Z",
                "updated_at": "2026-07-24T12:00:01Z",
                "published_index_version": "index-001",
                "error_code": None,
            }
        )

    def topic(self, payload):
        return {
            "schema_version": 1,
            "action": payload["action"],
            "topics": [],
            "job_id": None,
        }


def test_unix_service_exposes_health_and_capabilities_with_private_socket(tmp_path):
    socket_path = tmp_path / "runtime" / "service.sock"
    server = UnixServiceServer(socket_path, StubApplication())
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        client = ServiceClient(socket_path)

        assert client.health()["status"] == "ready"
        info = client.service_info()
        assert info.status is contracts.ServiceStatus.READY
        response = client.query(
            contracts.QueryRequest.from_dict(
                {
                    "schema_version": 1,
                    "request_id": "query-001",
                    "profile_id": "default",
                    "query": "cached query",
                    "freshness_policy": "cache_only",
                    "response_mode": "evidence",
                    "filters": {},
                    "top_k": 8,
                    "max_chars": 8192,
                    "wait_ms": 0,
                }
            )
        )
        assert response.cache_status is contracts.CacheStatus.MISS
        assert client.job("job-001").state is contracts.JobState.PUBLISHED
        assert client.topic({"action": "list"})["action"] == "list"
        assert stat.S_IMODE(socket_path.stat().st_mode) == 0o600
        assert stat.S_IMODE((socket_path.parent / "service.lock").stat().st_mode) == 0o600
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    assert not socket_path.exists()


def test_job_endpoint_returns_safe_not_found(tmp_path):
    socket_path = tmp_path / "runtime" / "service.sock"
    server = UnixServiceServer(socket_path, StubApplication())
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with pytest.raises(ServiceClientError, match="job_not_found"):
            ServiceClient(socket_path).job("missing")
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_second_server_cannot_unlink_or_replace_the_live_socket(tmp_path):
    socket_path = tmp_path / "runtime" / "service.sock"
    server = UnixServiceServer(socket_path, StubApplication())
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with pytest.raises(ServiceAlreadyRunningError):
            UnixServiceServer(socket_path, StubApplication())

        assert ServiceClient(socket_path).health()["status"] == "ready"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_server_recovers_an_owned_stale_socket(tmp_path):
    socket_path = tmp_path / "runtime" / "service.sock"
    socket_path.parent.mkdir(parents=True)
    stale = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    stale.bind(str(socket_path))
    stale.close()

    server = UnixServiceServer(socket_path, StubApplication())
    try:
        assert socket_path.is_socket()
        assert stat.S_IMODE(socket_path.stat().st_mode) == 0o600
    finally:
        server.server_close()


@pytest.mark.parametrize("path_kind", ["regular", "dangling_symlink"])
def test_server_fails_closed_for_non_socket_paths(tmp_path, path_kind):
    socket_path = tmp_path / "runtime" / "service.sock"
    socket_path.parent.mkdir(parents=True)
    if path_kind == "regular":
        socket_path.write_text("must survive", encoding="utf-8")
    else:
        socket_path.symlink_to(tmp_path / "missing-target")

    with pytest.raises(RuntimeError, match="not an owned Unix socket"):
        UnixServiceServer(socket_path, StubApplication())

    assert os.path.lexists(socket_path)
    if path_kind == "regular":
        assert socket_path.read_text(encoding="utf-8") == "must survive"
    else:
        assert socket_path.is_symlink()


def test_malformed_contract_error_does_not_echo_attacker_input(tmp_path):
    socket_path = tmp_path / "runtime" / "service.sock"
    server = UnixServiceServer(socket_path, StubApplication())
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    attacker_value = "secret-cookie-value-must-not-echo"
    request_body = (
        '{"schema_version":1,"request_id":"bad","profile_id":"default",'
        f'"query":"x","unknown":"{attacker_value}"}}'
    ).encode()
    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        client.connect(str(socket_path))
        client.sendall(
            b"POST /v1/query HTTP/1.1\r\nHost: localhost\r\n"
            + f"Content-Length: {len(request_body)}\r\n".encode()
            + b"Content-Type: application/json\r\nConnection: close\r\n\r\n"
            + request_body
        )
        response = bytearray()
        while chunk := client.recv(4096):
            response.extend(chunk)
    finally:
        client.close()
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    assert b"400 Bad Request" in response
    assert b"invalid_contract" in response
    assert attacker_value.encode() not in response
