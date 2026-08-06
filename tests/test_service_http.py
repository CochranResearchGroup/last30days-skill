"""Real Unix-socket transport tests for the local intelligence service."""

import json
import os
import socket
import stat
import threading

import pytest

from lib import service_contracts as contracts
from lib.service_app import JobResumeConflictError
from lib.service_client import (
    ServiceClient,
    ServiceClientError,
    _UnixHTTPConnection,
)
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
                "product": "last30days",
                "service_version": "0.1.0",
                "service_api_version": 1,
                "contract_schema_version": 1,
                "contract_sha256": contracts.SCHEMA_CATALOG_SHA256,
                "database_schema_version": 3,
                "runtime_manifest_sha256": "a" * 64,
                "mcp_adapter_version": None,
                "mcp_supported_service_api_min": None,
                "mcp_supported_service_api_max": None,
                "mcp_supported_database_schema_min": None,
                "mcp_supported_database_schema_max": None,
                "compatibility_state": "mcp_client_not_declared",
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

    def tick_schedule_status(self):
        return {
            "schema_version": 1,
            "enabled": False,
            "schedule_id": None,
            "interval_seconds": None,
            "anchor_seconds": None,
            "state": "disabled",
            "next_boundary": None,
            "last_boundary": None,
            "last_tick_id": None,
            "last_tick_state": None,
            "runtime_error": None,
        }

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

    def resume_job(self, job_id):
        if job_id == "job-published":
            raise JobResumeConflictError(
                "only awaiting_operator jobs can be resumed"
            )
        if job_id != "job-001":
            raise KeyError(job_id)
        payload = self.job(job_id).to_dict()
        payload.update(
            {
                "state": "queued",
                "attempts": 1,
                "published_index_version": None,
            }
        )
        return contracts.JobRecord.from_dict(payload)

    def topic(self, payload):
        return {
            "schema_version": 1,
            "action": payload["action"],
            "topics": [],
            "job_id": None,
        }

    def intelligence(self, payload):
        return {
            "schema_version": 1,
            "action": payload["action"],
            "access_partitions": ["public"],
            "coverage": [],
        }


def test_unix_service_exposes_health_and_capabilities_with_private_socket(tmp_path):
    socket_path = tmp_path / "runtime" / "service.sock"
    server = UnixServiceServer(socket_path, StubApplication())
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        client = ServiceClient(socket_path)

        assert client.health()["status"] == "ready"
        assert client.tick_schedule_status()["state"] == "disabled"
        info = client.service_info()
        assert info.status is contracts.ServiceStatus.READY
        assert info.product == "last30days"
        assert info.service_api_version == 1
        assert info.contract_sha256 == contracts.SCHEMA_CATALOG_SHA256
        assert info.mcp_adapter_version is None
        assert info.compatibility_state == "mcp_client_not_declared"
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
        assert client.intelligence(
            {"action": "coverage", "profile_id": "default"}
        )["action"] == "coverage"
        assert stat.S_IMODE(socket_path.stat().st_mode) == 0o600
        assert stat.S_IMODE((socket_path.parent / "service.lock").stat().st_mode) == 0o600
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    assert not socket_path.exists()


def test_service_info_body_and_header_publish_the_same_contract_digest(tmp_path):
    socket_path = tmp_path / "runtime" / "service.sock"
    server = UnixServiceServer(socket_path, StubApplication())
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    connection = _UnixHTTPConnection(socket_path, timeout=2)
    try:
        connection.request(
            "GET",
            "/v1/service-info",
            headers={
                "X-Last30days-Expected-Product": "last30days",
                "X-Last30days-MCP-Version": "4.0.1",
                "X-Last30days-Service-API-Min": "1",
                "X-Last30days-Service-API-Max": "1",
                "X-Last30days-Contract-Schema": "1",
                "X-Last30days-Expected-Contract-SHA256": (
                    contracts.SCHEMA_CATALOG_SHA256
                ),
                "X-Last30days-Database-Schema-Min": "3",
                "X-Last30days-Database-Schema-Max": "3",
            },
        )
        response = connection.getresponse()
        payload = json.loads(response.read())

        assert response.status == 200
        assert (
            response.getheader("X-Last30days-Contract-SHA256")
            == contracts.SCHEMA_CATALOG_SHA256
            == payload["contract_sha256"]
        )
        assert payload["contract_schema_version"] == contracts.SCHEMA_VERSION
        assert payload["mcp_adapter_version"] == "4.0.1"
        assert payload["compatibility_state"] == "compatible"
    finally:
        connection.close()
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


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


def test_operator_can_resume_an_awaiting_job_through_the_public_client(tmp_path):
    socket_path = tmp_path / "runtime" / "service.sock"
    server = UnixServiceServer(socket_path, StubApplication())
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        resumed = ServiceClient(socket_path).resume_job("job-001")

        assert resumed.state is contracts.JobState.QUEUED
        assert resumed.attempts == 1
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_job_resume_conflict_is_safe_and_non_retryable(tmp_path):
    socket_path = tmp_path / "runtime" / "service.sock"
    server = UnixServiceServer(socket_path, StubApplication())
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with pytest.raises(
            ServiceClientError,
            match="job_not_awaiting_operator",
        ):
            ServiceClient(socket_path).resume_job("job-published")
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
