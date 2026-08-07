"""Fixed notification adapter machinery with user-scoped routing data."""

from __future__ import annotations

import base64
import hashlib
import json
import subprocess
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from email.message import EmailMessage
from urllib.parse import urlparse


@dataclass(frozen=True)
class CommandReceipt:
    returncode: int
    stdout: str
    stderr: str


CommandRunner = Callable[..., CommandReceipt]


def _run_command(
    argv: Sequence[str], *, input_text: str | None = None, timeout_seconds: int = 30
) -> CommandReceipt:
    result = subprocess.run(
        list(argv),
        input=input_text,
        text=True,
        capture_output=True,
        timeout=timeout_seconds,
        check=False,
    )
    return CommandReceipt(result.returncode, result.stdout, result.stderr)


def _canonical_json(value: object) -> str:
    return json.dumps(value, allow_nan=False, separators=(",", ":"), sort_keys=True)


def _receipt_ref(prefix: str, value: object) -> str:
    digest = hashlib.sha256(_canonical_json(value).encode()).hexdigest()
    return f"{prefix}:sha256:{digest}"


def _safe_message(payload: Mapping[str, object]) -> str:
    lines = [
        f"last30days incident {payload['incident_id']}",
        f"kind: {payload['notification_kind']}",
        f"type: {payload['incident_type']}",
        f"severity: {payload['severity']}",
        f"source/stage: {payload['source']} / {payload['stage']}",
        f"summary: {payload['safe_summary']}",
        f"protected artifact: {payload.get('protected_artifact_ref') or 'none'}",
    ]
    browser_incidents = {
        "captcha_required",
        "cloudflare_challenge",
        "rate_limit_blocked",
        "reauthentication_required",
    }
    if payload["incident_type"] in browser_incidents:
        if payload["notification_kind"] == "resolved":
            lines.append("manual action: none; browser incident resolved")
        else:
            operator_url = str(payload.get("operator_url") or "")
            parsed = urlparse(operator_url)
            is_external_https = (
                parsed.scheme == "https"
                and bool(parsed.hostname)
                and parsed.hostname.casefold() not in {"localhost", "127.0.0.1", "::1"}
            )
            if is_external_https:
                lines.extend(
                    (
                        "manual action: Open the operator link and complete the manual browser check.",
                        f"operator link: {operator_url}",
                    )
                )
            else:
                lines.append(
                    "manual action: Browser intervention is required, but the operator link is unavailable."
                )
    return "\n".join(lines)


class SlackReceiptsTransport:
    def __init__(
        self,
        transport_id: str,
        *,
        workspace: str,
        channel_ref: str,
        command_runner: CommandRunner = _run_command,
    ) -> None:
        self.transport_id = transport_id
        self.workspace = workspace
        self.channel_ref = channel_ref
        self.command_runner = command_runner

    def readiness(self) -> bool:
        result = self.command_runner(
            (
                "slack-receipts",
                "workspaces",
                "verify",
                "--workspace",
                self.workspace,
                "--require-explicit-outbound",
            ),
            timeout_seconds=30,
        )
        return result.returncode == 0

    def send(self, payload: Mapping[str, object]) -> str:
        request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "messages.send",
                "arguments": {
                    "workspace": self.workspace,
                    "channel_ref": self.channel_ref,
                    "text": _safe_message(payload),
                    "options": {
                        "idempotency_key": (
                            f"{payload['incident_id']}:"
                            f"{payload['notification_kind']}:"
                            f"{payload['notification_sequence']}"
                        )
                    },
                },
            },
        }
        input_text = "\n".join(
            (
                _canonical_json(
                    {
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "initialize",
                        "params": {
                            "protocolVersion": "2025-03-26",
                            "capabilities": {},
                            "clientInfo": {"name": "last30days", "version": "1"},
                        },
                    }
                ),
                _canonical_json(
                    {"jsonrpc": "2.0", "method": "notifications/initialized"}
                ),
                _canonical_json(request),
            )
        ) + "\n"
        result = self.command_runner(
            ("slack-receipts", "mcp", "serve"),
            input_text=input_text,
            timeout_seconds=30,
        )
        if result.returncode != 0:
            raise RuntimeError("slack_receipts_delivery_failed")
        response = None
        for line in result.stdout.splitlines():
            try:
                candidate = json.loads(line)
            except json.JSONDecodeError:
                continue
            if candidate.get("id") == 2:
                response = candidate
                break
        if not isinstance(response, dict) or "error" in response:
            raise RuntimeError("slack_receipts_delivery_invalid")
        if response.get("result", {}).get("isError") is True:
            raise RuntimeError("slack_receipts_delivery_rejected")
        return _receipt_ref("slack-receipts", response["result"])


class GwsEmailTransport:
    def __init__(
        self,
        transport_id: str,
        *,
        recipient: str,
        subject_prefix: str = "last30days incident",
        command_runner: CommandRunner = _run_command,
    ) -> None:
        self.transport_id = transport_id
        self.recipient = recipient
        self.subject_prefix = subject_prefix
        self.command_runner = command_runner

    def readiness(self) -> bool:
        result = self.command_runner(
            (
                "gws",
                "gmail",
                "users",
                "getProfile",
                "--params",
                _canonical_json({"userId": "me"}),
                "--format",
                "json",
            ),
            timeout_seconds=30,
        )
        return result.returncode == 0

    def send(self, payload: Mapping[str, object]) -> str:
        message = EmailMessage()
        message["To"] = self.recipient
        message["Subject"] = f"{self.subject_prefix}: {payload['incident_type']}"
        message.set_content(_safe_message(payload))
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode().rstrip("=")
        result = self.command_runner(
            (
                "gws",
                "gmail",
                "users",
                "messages",
                "send",
                "--params",
                _canonical_json({"userId": "me"}),
                "--json",
                _canonical_json({"raw": raw}),
                "--format",
                "json",
            ),
            timeout_seconds=30,
        )
        if result.returncode != 0:
            raise RuntimeError("gws_email_delivery_failed")
        try:
            response = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            raise RuntimeError("gws_email_delivery_invalid") from exc
        return _receipt_ref("gws-email", response)


def build_notification_transports(
    notifications: Mapping[str, object],
    *,
    command_runner: CommandRunner = _run_command,
) -> tuple[object, ...]:
    raw_transports = notifications.get("transports")
    if not isinstance(raw_transports, list) or not raw_transports:
        raise ValueError("notification transports must be a non-empty list")
    transports = []
    for raw in raw_transports:
        if not isinstance(raw, Mapping):
            raise ValueError("notification transport must be an object")
        transport_id = str(raw.get("transport_id") or "")
        adapter_type = raw.get("adapter_type")
        routing = raw.get("routing")
        if not transport_id or not isinstance(routing, Mapping):
            raise ValueError("notification transport identity/routing is invalid")
        if adapter_type == "slack_receipts":
            transports.append(
                SlackReceiptsTransport(
                    transport_id,
                    workspace=str(routing["workspace"]),
                    channel_ref=str(routing["channel_ref"]),
                    command_runner=command_runner,
                )
            )
        elif adapter_type == "gws_email":
            transports.append(
                GwsEmailTransport(
                    transport_id,
                    recipient=str(routing["recipient"]),
                    subject_prefix=str(
                        routing.get("subject_prefix", "last30days incident")
                    ),
                    command_runner=command_runner,
                )
            )
        else:
            raise ValueError(f"notification adapter is not installed: {adapter_type}")
    return tuple(transports)
