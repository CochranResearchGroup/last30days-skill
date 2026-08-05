"""Code-owned agent-browser transport for explicit human observation leases."""

from __future__ import annotations

import json
import urllib.request
from collections.abc import Callable, Mapping, Sequence
from typing import Any
from urllib.parse import urlparse

from .service_tick_incidents import ObservationLease


UrlOpen = Callable[..., Any]
_MAX_RESPONSE_BYTES = 1_048_576


class ObservationTransportError(RuntimeError):
    """Raised when agent-browser cannot prove a fresh external viewer lease."""


def _external_url(value: object) -> str | None:
    if not isinstance(value, Mapping):
        return None
    for field in ("publicOperatorUrl", "externalUrl"):
        candidate = value.get(field)
        if isinstance(candidate, str) and candidate.strip():
            return candidate.strip()
    for field in ("routeDescriptor", "operatorVisible", "route"):
        candidate = _external_url(value.get(field))
        if candidate is not None:
            return candidate
    return None


def _records(payload: Mapping[str, object], name: str) -> list[Mapping[str, object]]:
    data = payload.get("data", payload)
    if not isinstance(data, Mapping):
        return []
    values = data.get(name, [])
    if not isinstance(values, Sequence) or isinstance(values, (str, bytes)):
        return []
    return [value for value in values if isinstance(value, Mapping)]


def _nested_text(payload: object, name: str) -> str | None:
    if isinstance(payload, Mapping):
        value = payload.get(name)
        if isinstance(value, str) and value.strip():
            return value.strip()
        for child in payload.values():
            found = _nested_text(child, name)
            if found is not None:
                return found
    elif isinstance(payload, Sequence) and not isinstance(payload, (str, bytes)):
        for child in payload:
            found = _nested_text(child, name)
            if found is not None:
                return found
    return None


class AgentBrowserObservationTransport:
    """Resolve one retained stream, then request agent-browser `view_takeover`."""

    def __init__(
        self,
        service_base_url: str,
        *,
        urlopen: UrlOpen = urllib.request.urlopen,
        timeout_seconds: int = 10,
    ) -> None:
        parsed = urlparse(service_base_url)
        if (
            parsed.scheme not in {"http", "https"}
            or not parsed.hostname
            or parsed.username is not None
            or parsed.password is not None
            or parsed.query
            or parsed.fragment
        ):
            raise ValueError("agent-browser service_base_url is invalid")
        if (
            isinstance(timeout_seconds, bool)
            or not isinstance(timeout_seconds, int)
            or not 1 <= timeout_seconds <= 60
        ):
            raise ValueError("timeout_seconds must be between 1 and 60")
        self.service_base_url = service_base_url.rstrip("/")
        self.urlopen = urlopen
        self.timeout_seconds = timeout_seconds

    def _request(
        self,
        path: str,
        *,
        payload: Mapping[str, object] | None = None,
    ) -> Mapping[str, object]:
        data = None
        method = "GET"
        headers = {"Accept": "application/json"}
        if payload is not None:
            data = json.dumps(
                payload,
                allow_nan=False,
                ensure_ascii=False,
                separators=(",", ":"),
                sort_keys=True,
            ).encode("utf-8")
            method = "POST"
            headers["Content-Type"] = "application/json"
        request = urllib.request.Request(
            self.service_base_url + path,
            data=data,
            headers=headers,
            method=method,
        )
        try:
            with self.urlopen(request, timeout=self.timeout_seconds) as response:
                encoded = response.read(_MAX_RESPONSE_BYTES + 1)
        except (OSError, TimeoutError, ValueError) as exc:
            raise ObservationTransportError(
                "agent-browser service request failed"
            ) from exc
        if not encoded or len(encoded) > _MAX_RESPONSE_BYTES:
            raise ObservationTransportError(
                "agent-browser response is empty or exceeds the size limit"
            )
        try:
            result = json.loads(encoded)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ObservationTransportError(
                "agent-browser response is not valid JSON"
            ) from exc
        if not isinstance(result, Mapping):
            raise ObservationTransportError("agent-browser response must be an object")
        return result

    def _route(
        self, public_operator_url: str
    ) -> tuple[str, str, str, str]:
        browsers_response = self._request("/api/service/browsers")
        sessions_response = self._request("/api/service/sessions")
        sessions_by_id: dict[str, Mapping[str, object]] = {}
        for session in _records(sessions_response, "sessions"):
            session_id = session.get("id")
            if isinstance(session_id, str) and session_id.strip():
                sessions_by_id[session_id] = session
        matches: list[tuple[str, str, str, str]] = []
        for browser in _records(browsers_response, "browsers"):
            browser_id = browser.get("browserId") or browser.get("id")
            active_session_ids = browser.get("activeSessionIds", [])
            if not isinstance(active_session_ids, Sequence) or isinstance(
                active_session_ids, (str, bytes)
            ):
                continue
            active_sessions: list[str] = []
            for session_id in active_session_ids:
                if not isinstance(session_id, str) or not session_id.strip():
                    continue
                session = sessions_by_id.get(session_id)
                if session is None:
                    continue
                browser_ids = session.get("browserIds", [])
                if (
                    isinstance(browser_ids, Sequence)
                    and not isinstance(browser_ids, (str, bytes))
                    and browser_id in browser_ids
                ):
                    active_sessions.append(session_id)
            if len(active_sessions) != 1:
                continue
            session_name = active_sessions[0]
            streams = browser.get("viewStreams", [])
            if not isinstance(streams, Sequence) or isinstance(
                streams, (str, bytes)
            ):
                continue
            for stream in streams:
                if not isinstance(stream, Mapping):
                    continue
                readiness = stream.get("readiness")
                if (
                    _external_url(stream) != public_operator_url
                    or not isinstance(readiness, Mapping)
                    or readiness.get("state") != "ready"
                ):
                    continue
                stream_id = stream.get("streamId") or stream.get("id")
                provider = stream.get("provider")
                if all(
                    isinstance(value, str) and value.strip()
                    for value in (browser_id, session_name, stream_id, provider)
                ):
                    matches.append(
                        (
                            str(browser_id),
                            str(session_name),
                            str(stream_id),
                            str(provider),
                        )
                    )
        if len(matches) != 1:
            raise ObservationTransportError(
                "agent-browser external route did not resolve to one ready stream"
            )
        return matches[0]

    def acquire(
        self, *, incident_id: str, public_operator_url: str
    ) -> ObservationLease:
        ObservationLease(
            viewer_lease_id="route-resolution-only",
            public_operator_url=public_operator_url,
        )
        browser_id, session_name, stream_id, provider = self._route(
            public_operator_url
        )
        response = self._request(
            "/api/service/request",
            payload={
                "serviceName": "last30days",
                "agentName": "incident-observer",
                "taskName": f"observe-{incident_id}"[:128],
                "browserId": browser_id,
                "sessionName": session_name,
                "action": "view_takeover",
                "params": {
                    "browserId": browser_id,
                    "sessionName": session_name,
                    "streamId": stream_id,
                    "provider": provider,
                    "openMode": "external",
                },
            },
        )
        if response.get("success") is not True:
            raise ObservationTransportError("agent-browser view_takeover failed")
        viewer_lease_id = _nested_text(response.get("data", response), "viewerLeaseId")
        external_url = _external_url(response.get("data", response))
        if viewer_lease_id is None or external_url is None:
            raise ObservationTransportError(
                "agent-browser view_takeover omitted lease or external route proof"
            )
        return ObservationLease(
            viewer_lease_id=viewer_lease_id,
            public_operator_url=external_url,
        )
