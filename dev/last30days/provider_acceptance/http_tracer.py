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

from skills.last30days.scripts.lib import (
    reddit_keyless,
    service_acquisition_worker,
    service_contracts,
)

from .contracts import SealedCase, TransportObservation


_SUPPORTED_ADAPTERS = frozenset({"reddit_keyless", "reddit_scrapecreators"})
_LOGICAL_HOSTS = {
    "reddit_keyless": "www.reddit.com",
    "reddit_scrapecreators": "api.scrapecreators.com",
}
_PLACEHOLDER_TOKEN = "provider-free-placeholder"
_FIXED_TIME = datetime(2026, 9, 14, 12, 0, tzinfo=timezone.utc)
_URLLIB_LOCK = threading.Lock()


def _digest_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def _digest_json(value: object) -> str:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False
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

    def __init__(
        self, expected_target: str, response_body: bytes, adapter_id: str
    ) -> None:
        self.expected_target = expected_target
        self.response_body = response_body
        self.adapter_id = adapter_id
        self.request_count = 0
        self.route_matched = False
        self.protocol_matched = False
        super().__init__(("127.0.0.1", 0), _FixtureHandler)


class _FixtureHandler(BaseHTTPRequestHandler):
    server: _OwnedHTTPServer

    def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler contract
        self.server.request_count += 1
        headers = {key.casefold(): value for key, value in self.headers.items()}
        if self.server.adapter_id == "reddit_keyless":
            protocol_matched = headers.get("accept") == "application/json"
        else:
            protocol_matched = (
                headers.get("content-type") == "application/json"
                and headers.get("x-api-key") == _PLACEHOLDER_TOKEN
            )
        route_matched = (
            self.server.request_count == 1 and self.path == self.server.expected_target
        )
        self.server.route_matched = route_matched
        self.server.protocol_matched = protocol_matched
        matched = route_matched and protocol_matched
        body = self.server.response_body if matched else b"{}"
        self.send_response(200 if matched else 404)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, _format: str, *_args: object) -> None:
        return


def _request_target(request_spec: Mapping[str, Any]) -> str | None:
    if request_spec.get("method") != "GET" or request_spec.get("host") != "127.0.0.1":
        return None
    logical_host = request_spec.get("logical_host")
    path = request_spec.get("path")
    query = request_spec.get("query")
    if (
        not isinstance(logical_host, str)
        or not isinstance(path, str)
        or not path.startswith("/")
        or path.startswith("//")
        or not isinstance(query, Mapping)
        or any(
            not isinstance(key, str) or not isinstance(value, str)
            for key, value in query.items()
        )
    ):
        return None
    encoded = urllib.parse.urlencode(query)
    return path + (f"?{encoded}" if encoded else "")


def _owned_base_url(server: _OwnedHTTPServer) -> str:
    host, port = server.server_address
    url = f"http://{host}:{port}"
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


def _redirected_request(
    original: str | urllib.request.Request,
    *,
    adapter_id: str,
    request_spec: Mapping[str, Any],
    owned_base_url: str,
) -> urllib.request.Request:
    if isinstance(original, urllib.request.Request):
        logical_url = original.full_url
        method = original.get_method()
        data = original.data
        headers = dict(original.header_items())
    else:
        logical_url = str(original)
        method = "GET"
        data = None
        headers = {}
    parsed = urllib.parse.urlsplit(logical_url)
    expected_query = sorted(request_spec["query"].items())
    observed_query = sorted(urllib.parse.parse_qsl(parsed.query, keep_blank_values=True))
    header_map = {key.casefold(): value for key, value in headers.items()}
    protocol_matches = method == request_spec["method"] == "GET" and data is None
    if adapter_id == "reddit_keyless":
        protocol_matches = (
            protocol_matches and header_map.get("accept") == "application/json"
        )
    else:
        protocol_matches = (
            protocol_matches
            and header_map.get("content-type") == "application/json"
            and header_map.get("x-api-key") == _PLACEHOLDER_TOKEN
        )
    if (
        parsed.scheme != "https"
        or parsed.hostname != request_spec["logical_host"]
        or parsed.hostname != _LOGICAL_HOSTS[adapter_id]
        or parsed.path != request_spec["path"]
        or observed_query != expected_query
        or not protocol_matches
    ):
        raise RuntimeError("production adapter request drifted from sealed route")
    target = parsed.path + (f"?{parsed.query}" if parsed.query else "")
    return urllib.request.Request(
        owned_base_url + target, data=data, headers=headers, method=method
    )


class HttpTracer:
    """Trace a sealed case through the production adapter and worker seam."""

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
        if (
            not isinstance(fixture, dict)
            or not isinstance(fixture.get("items"), list)
            or not isinstance(fixture.get("transport_response"), Mapping)
        ):
            return _failure("parser_drift", "malformed_output")
        request_spec = fixture.get("request")
        if not isinstance(request_spec, Mapping):
            return _failure("route_drift", "malformed_route")
        target = _request_target(request_spec)
        if (
            target is None
            or request_spec.get("logical_host") != _LOGICAL_HOSTS[case.case.adapter_id]
        ):
            return _failure("route_drift", "non_loopback_route")

        response_body = json.dumps(
            fixture["transport_response"],
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        ).encode("utf-8")
        server = _OwnedHTTPServer(target, response_body, case.case.adapter_id)
        thread = threading.Thread(
            target=server.serve_forever,
            name=f"wi010-{case.case.case_id}",
            daemon=True,
        )
        thread.start()
        result = None
        redirect_count = 0
        cleanup_complete = False
        try:
            owned_base_url = _owned_base_url(server)
            request_query = request_spec["query"]
            query = str(
                request_query.get("q")
                or request_query.get("query")
                or "provider acceptance"
            ).replace("+", " ")
            request = service_contracts.AcquisitionWorkRequest.from_dict(
                {
                    "schema_version": 1,
                    "work_id": f"wi010-{case.case.case_id}",
                    "job_id": "wi010-provider-free-p2",
                    "lease_generation": 1,
                    "attempt": 1,
                    "profile_id": "provider-free",
                    "source": case.case.source,
                    "query": query,
                    "from_date": "2026-08-15",
                    "to_date": "2026-09-14",
                    "depth": "quick",
                    "adapter": case.case.adapter_id,
                    "adapter_version": "1",
                    "wall_timeout_seconds": 10,
                    "item_limit": min(item_limit, 3),
                    "network_request_limit": 1,
                    "cost_budget_cents": (
                        1 if case.case.adapter_id == "reddit_scrapecreators" else 0
                    ),
                }
            )
            config = (
                {"SCRAPECREATORS_API_KEY": _PLACEHOLDER_TOKEN}
                if case.case.adapter_id == "reddit_scrapecreators"
                else {}
            )
            with _URLLIB_LOCK:
                native_urlopen = urllib.request.urlopen
                original_enrich_limits = reddit_keyless.ENRICH_LIMITS

                def redirect_urlopen(original, *args, **kwargs):
                    nonlocal redirect_count
                    redirect_count += 1
                    if redirect_count > 1:
                        raise RuntimeError("HTTP tracer request budget exhausted")
                    redirected = _redirected_request(
                        original,
                        adapter_id=case.case.adapter_id,
                        request_spec=request_spec,
                        owned_base_url=owned_base_url,
                    )
                    return native_urlopen(redirected, *args, **kwargs)

                urllib.request.urlopen = redirect_urlopen
                if case.case.adapter_id == "reddit_keyless":
                    reddit_keyless.ENRICH_LIMITS = {
                        **original_enrich_limits,
                        "quick": 0,
                    }
                try:
                    result = service_acquisition_worker.execute_work(
                        request, config, clock=lambda: _FIXED_TIME
                    )
                finally:
                    reddit_keyless.ENRICH_LIMITS = original_enrich_limits
                    urllib.request.urlopen = native_urlopen
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)
            cleanup_complete = not thread.is_alive()

        if result is None:  # pragma: no cover - execute_work returns a result
            return _failure("internal_harness_error", "missing_worker_result")
        request_count = server.request_count
        normalized_count = result.item_count
        transport_success = (
            server.route_matched
            and server.protocol_matched
            and request_count == redirect_count == 1
        )
        success = (
            transport_success
            and result.status is service_contracts.AcquisitionStatus.SUCCEEDED
            and result.safe_error_code is None
            and result.network_request_count == 1
            and normalized_count == case.case.expected_item_count
            and normalized_count <= item_limit
            and cleanup_complete
        )
        reason = None
        if not success:
            reason = (
                result.safe_error_code
                or ("request_budget_exhausted" if redirect_count > 1 else None)
                or ("route_drift" if not server.route_matched else None)
                or ("protocol_drift" if not server.protocol_matched else None)
                or ("teardown_failed" if not cleanup_complete else None)
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
            "exact_owner_cleanup": cleanup_complete,
            "loopback": True,
            "normalization_seam": "service_acquisition_worker.execute_work",
            "owned_server": True,
            "production_adapter_invoked": True,
            "request_method": "GET",
            "request_target_sha256": _digest_bytes(target.encode("utf-8")),
            "server_request_count": request_count,
            "owner_census": 0 if cleanup_complete else 1,
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
