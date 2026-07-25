"""Concrete loopback-only Graphiti projection sink."""

from __future__ import annotations

import hashlib
import json
import re
import urllib.error
import urllib.parse
import urllib.request
import uuid
from collections.abc import Callable, Mapping
from typing import Any


_NODE_NAMESPACE = uuid.UUID("9bf768e9-1718-5da1-9d28-674a7ee518bb")
_MAX_RESPONSE_BYTES = 65_536


class GraphitiHTTPSink:
    """Project accepted records into partition-specific local Graphiti groups."""

    def __init__(
        self,
        base_url: str,
        *,
        group_prefix: str = "last30days",
        timeout_seconds: float = 10.0,
        opener: Callable[..., Any] = urllib.request.urlopen,
    ) -> None:
        parsed = urllib.parse.urlsplit(base_url.rstrip("/"))
        if (
            parsed.scheme != "http"
            or parsed.hostname not in {"127.0.0.1", "localhost", "::1"}
            or parsed.username is not None
            or parsed.password is not None
        ):
            raise ValueError("Graphiti projection URL must be loopback HTTP")
        if not 0 < timeout_seconds <= 60:
            raise ValueError("Graphiti projection timeout is invalid")
        if re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", group_prefix) is None:
            raise ValueError("Graphiti group prefix is invalid")
        self.base_url = base_url.rstrip("/")
        self.group_prefix = group_prefix
        self.timeout_seconds = timeout_seconds
        self._opener = opener

    @staticmethod
    def _read_json(response: Any) -> dict[str, object]:
        raw = response.read(_MAX_RESPONSE_BYTES + 1)
        if len(raw) > _MAX_RESPONSE_BYTES:
            raise RuntimeError("Graphiti response exceeded the transport limit")
        decoded = json.loads(raw.decode("utf-8"))
        if not isinstance(decoded, dict):
            raise RuntimeError("Graphiti returned a non-object response")
        return decoded

    def _request(
        self,
        method: str,
        path: str,
        payload: Mapping[str, object] | None = None,
    ) -> dict[str, object]:
        data = None
        headers = {"Accept": "application/json"}
        if payload is not None:
            data = json.dumps(
                dict(payload),
                allow_nan=False,
                ensure_ascii=False,
                separators=(",", ":"),
                sort_keys=True,
            ).encode("utf-8")
            headers["Content-Type"] = "application/json"
        request = urllib.request.Request(
            f"{self.base_url}{path}",
            data=data,
            headers=headers,
            method=method,
        )
        try:
            with self._opener(request, timeout=self.timeout_seconds) as response:
                return self._read_json(response)
        except (OSError, urllib.error.URLError, json.JSONDecodeError) as exc:
            raise RuntimeError("local Graphiti projection is unavailable") from exc

    def _group_id(self, partition_id: str) -> str:
        suffix = re.sub(r"[^A-Za-z0-9_-]+", "_", partition_id).strip("_")
        if not suffix:
            raise ValueError("projection partition is invalid")
        return f"{self.group_prefix}_{suffix}"[:127]

    def upsert(
        self,
        *,
        aggregate_kind: str,
        aggregate_id: str,
        payload: Mapping[str, object],
        partition_id: str,
    ) -> str:
        health = self._request("GET", "/healthcheck")
        if health.get("status") != "healthy":
            raise RuntimeError("local Graphiti projection is not healthy")
        canonical = json.dumps(
            dict(payload),
            allow_nan=False,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )
        payload_digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        node_uuid = str(
            uuid.uuid5(
                _NODE_NAMESPACE,
                f"{partition_id}\0{aggregate_kind}\0{aggregate_id}",
            )
        )
        group_id = self._group_id(partition_id)
        node_name = f"{aggregate_kind}:{aggregate_id}"
        response = self._request(
            "POST",
            "/entity-node",
            {
                "uuid": node_uuid,
                "group_id": group_id,
                "name": node_name,
                "summary": (
                    "last30days-projection-v1 "
                    f"payload_sha256={payload_digest} payload={canonical}"
                ),
            },
        )
        returned_uuid = response.get("uuid", node_uuid)
        if (
            returned_uuid not in {node_uuid, None}
            or response.get("group_id", group_id) != group_id
            or response.get("name", node_name) != node_name
        ):
            raise RuntimeError("Graphiti projection receipt did not match the node")
        return f"graphiti-http-v1:{node_uuid}:{payload_digest}"
