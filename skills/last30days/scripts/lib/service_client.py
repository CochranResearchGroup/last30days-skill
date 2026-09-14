"""Thin local HTTP client for the last30days Unix-socket service."""

from __future__ import annotations

import http.client
import json
import socket
import urllib.parse
from pathlib import Path
from typing import Any

from . import service_contracts as contracts
from . import service_question_contracts as question_contracts


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
        *,
        timeout: float | None = None,
    ) -> dict[str, Any]:
        connection = _UnixHTTPConnection(
            self.socket_path, self.timeout if timeout is None else timeout
        )
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

    def tick_schedule_status(self) -> dict[str, Any]:
        return self._request("GET", "/v1/tick-schedule")

    def follow_capabilities(self) -> dict[str, Any]:
        return self._request("GET", "/v1/follow-capabilities")

    def query(self, request: contracts.QueryRequest) -> contracts.QueryResponse:
        return contracts.QueryResponse.from_dict(
            self._request("POST", "/v1/query", request.to_dict())
        )

    def search_posts(
        self, request: contracts.PostSearchRequest
    ) -> contracts.PostSearchResponse:
        return contracts.PostSearchResponse.from_dict(
            self._request("POST", "/v1/posts/search", request.to_dict())
        )

    def ask_question(
        self, request: question_contracts.QuestionRequestV1
    ) -> question_contracts.QuestionStatusV1:
        timeout = max(self.timeout, request.limits.wait_ms / 1000 + 5.0)
        return question_contracts.QuestionStatusV1.from_dict(
            self._request(
                "POST", "/v1/questions", request.to_dict(), timeout=timeout
            )
        )

    def question_status(
        self, question_id: str, *, profile_id: str
    ) -> question_contracts.QuestionStatusV1:
        encoded_id = urllib.parse.quote(question_id, safe="")
        encoded_profile = urllib.parse.quote(profile_id, safe="")
        return question_contracts.QuestionStatusV1.from_dict(
            self._request(
                "GET", f"/v1/questions/{encoded_id}?profile_id={encoded_profile}"
            )
        )

    def read_evidence(
        self, request: question_contracts.EvidenceReadRequestV1
    ) -> question_contracts.EvidenceReadResponseV1:
        return question_contracts.EvidenceReadResponseV1.from_dict(
            self._request("POST", "/v1/evidence/read", request.to_dict())
        )

    def saved_query(
        self, command: dict[str, object], *, profile_id: str = "default"
    ) -> dict[str, Any]:
        return self._request(
            "POST",
            "/v1/saved-query",
            {"profile_id": profile_id, "command": command},
        )

    def monitor(
        self, command: dict[str, object], *, profile_id: str = "default"
    ) -> dict[str, Any]:
        return self._request(
            "POST",
            "/v1/monitor",
            {"profile_id": profile_id, "command": command},
        )

    def job(self, job_id: str) -> contracts.JobRecord:
        encoded = urllib.parse.quote(job_id, safe="")
        return contracts.JobRecord.from_dict(
            self._request("GET", f"/v1/jobs/{encoded}")
        )

    def resume_job(self, job_id: str) -> contracts.JobRecord:
        encoded = urllib.parse.quote(job_id, safe="")
        return contracts.JobRecord.from_dict(
            self._request("POST", f"/v1/jobs/{encoded}/resume", {})
        )

    def topic(self, payload: dict[str, object]) -> dict[str, Any]:
        return self._request("POST", "/v1/topic", payload)

    def intelligence(self, payload: dict[str, object]) -> dict[str, Any]:
        return self._request("POST", "/v1/intelligence", payload)
