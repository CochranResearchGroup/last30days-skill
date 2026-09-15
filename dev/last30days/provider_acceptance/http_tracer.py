"""Owned loopback HTTP tracer for the WI-010 Reddit adapter cases."""

from __future__ import annotations

import hashlib
import ipaddress
import json
import threading
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, Mapping

from skills.last30days.scripts.lib import service_contracts
from skills.last30days.scripts.lib.service_acquisition_worker import execute_work

from .contracts import SealedCase, TransportObservation


_SUPPORTED_ADAPTERS = frozenset({"reddit_keyless", "reddit_scrapecreators"})
_FIXED_TIME = datetime(2026, 9, 14, 12, 0, tzinfo=timezone.utc)


def _digest_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def _digest_json(value: object) -> str:
    encoded = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")
    return _digest_bytes(encoded)


def _failure(
    outcome: str,
    reason: str,
    *,
    request_count: int = 0,
    transport_success: bool = False,
    details: Mapping[str, Any] | None = None,
) -> TransportObservation:
    safe_details = dict(details or {})
    return TransportObservation(
        outcome=outcome,
        transport_success=transport_success,
        item_count=0,
        request_count=request_count,
        safe_reason_code=reason,
        accounting_confidence="exact",
        raw_safe_sha256=_digest_json(
            {"outcome": outcome, "reason": reason, "details": safe_details}
        ),
        details=safe_details,
    )


class _OwnedHTTPServer(HTTPServer):
    """HTTP server carrying only immutable fixture bytes and safe counters."""

    allow_reuse_address = False

    def __init__(self, expected_target: str, response_body: bytes) -> None:
        self.expected_target = expected_target
        self.response_body = response_body
        self.request_count = 0
        self.route_matched = False
        super().__init__(("127.0.0.1", 0), _FixtureHandler)


class _FixtureHandler(BaseHTTPRequestHandler):
    server: _OwnedHTTPServer

    def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler contract
        self.server.request_count += 1
        matched = (
            self.server.request_count == 1
            and self.path == self.server.expected_target
            and self.headers.get("Accept") == "application/json"
        )
        self.server.route_matched = matched
        body = self.server.response_body if matched else b'{"items":[]}'
        self.send_response(200 if matched else 404)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, _format: str, *_args: object) -> None:
        return


def _request_target(request_spec: Mapping[str, Any]) -> str | None:
    if request_spec.get("method") != "GET":
        return None
    if request_spec.get("host") != "127.0.0.1":
        return None
    path = request_spec.get("path")
    query = request_spec.get("query")
    if (
        not isinstance(path, str)
        or not path.startswith("/")
        or path.startswith("//")
        or not isinstance(query, Mapping)
        or any(not isinstance(key, str) or not isinstance(value, str) for key, value in query.items())
    ):
        return None
    encoded = urllib.parse.urlencode(sorted(query.items()))
    return path + (f"?{encoded}" if encoded else "")


def _owned_url(server: _OwnedHTTPServer, target: str) -> str:
    host, port = server.server_address
    url = f"http://{host}:{port}{target}"
    parsed = urllib.parse.urlsplit(url)
    try:
        address = ipaddress.ip_address(parsed.hostname or "")
    except ValueError as exc:  # pragma: no cover - server_address is numeric
        raise RuntimeError("owned loopback server returned an invalid address") from exc
    if (
        not address.is_loopback
        or parsed.hostname != host
        or parsed.port != port
        or parsed.scheme != "http"
    ):
        raise RuntimeError("owned loopback route validation failed")
    return url


class HttpTracer:
    """Trace one sealed Reddit HTTP case through the real worker seam."""

    def __init__(self, repo_root: Path | str = ".") -> None:
        self._repo_root = Path(repo_root).resolve()

    def __call__(
        self, case: SealedCase, *, item_limit: int
    ) -> TransportObservation:
        if case.case.transport != "http" or case.case.adapter_id not in _SUPPORTED_ADAPTERS:
            return _failure("route_drift", "unsupported_http_adapter")
        if not isinstance(item_limit, int) or isinstance(item_limit, bool) or item_limit < 1:
            return _failure("budget_exhausted", "invalid_item_limit")

        fixture_path = (self._repo_root / case.case.fixture_path).resolve()
        if self._repo_root not in fixture_path.parents:
            return _failure("route_drift", "fixture_outside_repository")
        try:
            fixture_bytes = fixture_path.read_bytes()
        except OSError:
            return _failure("parser_drift", "fixture_unavailable")
        if _digest_bytes(fixture_bytes) != case.fixture_sha256:
            return _failure("parser_drift", "fixture_digest_mismatch")
        try:
            fixture = json.loads(fixture_bytes)
        except (UnicodeDecodeError, json.JSONDecodeError):
            return _failure("parser_drift", "malformed_output")
        if not isinstance(fixture, dict) or not isinstance(fixture.get("items"), list):
            return _failure("parser_drift", "malformed_output")
        request_spec = fixture.get("request")
        if not isinstance(request_spec, Mapping):
            return _failure("route_drift", "malformed_route")
        target = _request_target(request_spec)
        if target is None:
            return _failure("route_drift", "non_loopback_route")

        response_body = json.dumps(
            {"items": fixture["items"]},
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        ).encode("utf-8")
        server = _OwnedHTTPServer(target, response_body)
        thread = threading.Thread(
            target=server.serve_forever,
            name=f"wi010-{case.case.case_id}",
            daemon=True,
        )
        thread.start()
        try:
            url = _owned_url(server, target)

            def adapter(_request, _config):
                request = urllib.request.Request(
                    url,
                    headers={"Accept": "application/json"},
                    method="GET",
                )
                with urllib.request.urlopen(request, timeout=5) as response:
                    payload = json.loads(response.read())
                if not isinstance(payload, dict):
                    raise ValueError("loopback response must be an object")
                return payload

            request = service_contracts.AcquisitionWorkRequest.from_dict(
                {
                    "schema_version": 1,
                    "work_id": f"wi010-{case.case.case_id}",
                    "job_id": "wi010-provider-free-p2",
                    "lease_generation": 1,
                    "attempt": 1,
                    "profile_id": "provider-free",
                    "source": case.case.source,
                    "query": str(request_spec.get("query", {}).get("q", "provider acceptance")),
                    "from_date": "2026-08-15",
                    "to_date": "2026-09-14",
                    "depth": "quick",
                    "adapter": case.case.adapter_id,
                    "adapter_version": "1",
                    "wall_timeout_seconds": 10,
                    "item_limit": item_limit,
                    "network_request_limit": 1,
                    "cost_budget_cents": 0,
                }
            )
            result = execute_work(
                request,
                {},
                adapters={case.case.adapter_id: adapter},
                clock=lambda: _FIXED_TIME,
            )
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)

        request_count = server.request_count
        normalized_count = result.item_count
        transport_success = server.route_matched and request_count == 1
        success = (
            transport_success
            and result.status is service_contracts.AcquisitionStatus.SUCCEEDED
            and result.safe_error_code is None
            and result.network_request_count == 1
            and normalized_count == case.case.expected_item_count
            and normalized_count <= item_limit
        )
        reason = None
        if not success:
            reason = (
                result.safe_error_code
                or ("request_budget_exhausted" if request_count > 1 else None)
                or ("route_drift" if not server.route_matched else None)
                or "normalized_count_mismatch"
            )
        safe_result = {
            "adapter": result.adapter,
            "adapter_variant": result.diagnostics.get("adapter_variant"),
            "item_count": normalized_count,
            "network_request_count": result.network_request_count,
            "safe_error_code": result.safe_error_code,
            "status": result.status.value,
        }
        details = {
            "adapter_variant": result.diagnostics.get("adapter_variant"),
            "loopback": True,
            "normalization_seam": "service_acquisition_worker.execute_work",
            "owned_server": True,
            "request_method": "GET",
            "request_target_sha256": _digest_bytes(target.encode("utf-8")),
            "server_request_count": request_count,
        }
        return TransportObservation(
            outcome="success" if success else "parser_drift",
            transport_success=transport_success,
            item_count=normalized_count,
            request_count=request_count,
            safe_reason_code=reason,
            accounting_confidence=case.case.accounting_confidence,
            raw_safe_sha256=_digest_json(safe_result),
            details=details,
        )
