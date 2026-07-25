"""Thin local HTTP client for the last30days Unix-socket service."""

from __future__ import annotations

import http.client
import json
import socket
import urllib.parse
from pathlib import Path
from typing import Any

from . import service_contracts as contracts


class ServiceClientError(RuntimeError):
    """Safe client-facing service transport or response error."""


class _UnixHTTPConnection(http.client.HTTPConnection):
    def __init__(self, socket_path: Path, timeout: float):
        super().__init__("localhost", timeout=timeout)
        self.socket_path = socket_path

    def connect(self) -> None:
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.settimeout(self.timeout)
        self.sock.connect(str(self.socket_path))


class ServiceClient:
    """Small typed interface used by CLI and MCP transport adapters."""

    def __init__(self, socket_path: Path, *, timeout: float = 5.0):
        self.socket_path = Path(socket_path)
        self.timeout = timeout

    def _request(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        connection = _UnixHTTPConnection(self.socket_path, self.timeout)
        body = None
        headers = {"Accept": "application/json"}
        if payload is not None:
            body = json.dumps(
                payload,
                allow_nan=False,
                ensure_ascii=False,
                separators=(",", ":"),
                sort_keys=True,
            ).encode("utf-8")
            headers["Content-Type"] = "application/json"
            headers["Content-Length"] = str(len(body))
        try:
            connection.request(method, path, body=body, headers=headers)
            response = connection.getresponse()
            raw = response.read(131_073)
            if len(raw) > 131_072:
                raise ServiceClientError("service response exceeded transport limit")
        except (OSError, http.client.HTTPException) as exc:
            raise ServiceClientError(
                f"local service unavailable at {self.socket_path}"
            ) from exc
        finally:
            connection.close()
        try:
            decoded = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ServiceClientError("service returned invalid JSON") from exc
        if not isinstance(decoded, dict):
            raise ServiceClientError("service returned a non-object response")
        if not 200 <= response.status < 300:
            code = decoded.get("code", "service_error")
            message = decoded.get("message", "service request failed")
            raise ServiceClientError(f"{code}: {message}")
        return decoded

    def health(self) -> dict[str, Any]:
        return self._request("GET", "/v1/health")

    def service_info(self) -> contracts.ServiceInfo:
        return contracts.ServiceInfo.from_dict(
            self._request("GET", "/v1/service-info")
        )

    def query(self, request: contracts.QueryRequest) -> contracts.QueryResponse:
        return contracts.QueryResponse.from_dict(
            self._request("POST", "/v1/query", request.to_dict())
        )

    def job(self, job_id: str) -> contracts.JobRecord:
        encoded = urllib.parse.quote(job_id, safe="")
        return contracts.JobRecord.from_dict(
            self._request("GET", f"/v1/jobs/{encoded}")
        )

    def topic(self, payload: dict[str, object]) -> dict[str, Any]:
        return self._request("POST", "/v1/topic", payload)

    def intelligence(self, payload: dict[str, object]) -> dict[str, Any]:
        return self._request("POST", "/v1/intelligence", payload)
