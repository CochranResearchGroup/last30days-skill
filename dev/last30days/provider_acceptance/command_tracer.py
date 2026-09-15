"""Provider-free command transport tracer for the YouTube acquisition adapter."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import stat
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from unittest.mock import patch

from lib import service_acquisition_worker, service_contracts

from .contracts import ContractError, SealedCase, TransportObservation


_MAX_STDOUT_BYTES = 65_536
_FIXED_OBSERVED_AT = datetime(2026, 9, 14, 12, 0, tzinfo=timezone.utc)
_FAKE_YTDLP = r'''#!/usr/bin/python3
import hashlib
import json
import os
import sys

fixture_path = os.environ["WI010_FIXTURE_PATH"]
invocation_path = os.environ["WI010_INVOCATION_PATH"]
maximum = int(os.environ["WI010_MAX_STDOUT_BYTES"])

with open(fixture_path, encoding="utf-8") as fixture_file:
    fixture = json.load(fixture_file)
lines = [
    json.dumps(item, ensure_ascii=True, separators=(",", ":"))
    for item in fixture["transport"]["stdout_items"]
]
payload = ("\n".join(lines) + ("\n" if lines else "")).encode("utf-8")
bounded = len(payload) <= maximum
emitted = payload if bounded else b""
record = {
    "argv": sys.argv[1:],
    "invocation_count": 1,
    "returncode": 0 if bounded else 73,
    "stdout_bytes": len(emitted),
    "stdout_sha256": "sha256:" + hashlib.sha256(emitted).hexdigest(),
}
descriptor = os.open(invocation_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
with os.fdopen(descriptor, "w", encoding="utf-8") as invocation:
    json.dump(record, invocation, ensure_ascii=True, separators=(",", ":"))
if not bounded:
    sys.stderr.write("bounded_output_exceeded\n")
    raise SystemExit(73)
sys.stdout.buffer.write(emitted)
'''


def _digest_bytes(payload: bytes) -> str:
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def _digest_json(payload: object) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")
    return _digest_bytes(encoded)


class CommandTracer:
    """Trace one exact fake ``yt-dlp`` invocation through worker normalization."""

    def __init__(self, repo_root: Path | str = ".") -> None:
        self._repo_root = Path(repo_root).resolve()

    def __call__(
        self, case: SealedCase, *, item_limit: int
    ) -> TransportObservation:
        adapter = case.case
        if (
            adapter.transport != "command"
            or adapter.adapter_id != "youtube_ytdlp"
            or adapter.source != "youtube"
        ):
            raise ContractError("command tracer rejects non-owned transport")
        if not isinstance(item_limit, int) or isinstance(item_limit, bool) or item_limit < 1:
            raise ContractError("item_limit must be a positive integer")

        fixture_path = (self._repo_root / adapter.fixture_path).resolve()
        if self._repo_root not in fixture_path.parents or not fixture_path.is_file():
            raise ContractError("command fixture unavailable")
        fixture_bytes = fixture_path.read_bytes()
        if _digest_bytes(fixture_bytes) != case.fixture_sha256:
            raise ContractError("command fixture digest mismatch")
        try:
            fixture = json.loads(fixture_bytes)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ContractError("command fixture is malformed") from exc
        if not isinstance(fixture, dict) or not isinstance(fixture.get("items"), list):
            raise ContractError("command fixture must contain items")
        transport = fixture.get("transport")
        if not isinstance(transport, dict):
            raise ContractError("command fixture must contain transport")
        query = transport.get("query")
        from_date = transport.get("from_date")
        to_date = transport.get("to_date")
        expected_argv = transport.get("expected_argv")
        if not all(isinstance(value, str) and value for value in (query, from_date, to_date)):
            raise ContractError("command fixture transport fields are malformed")
        if not isinstance(expected_argv, list) or not all(
            isinstance(value, str) for value in expected_argv
        ):
            raise ContractError("command fixture expected argv is malformed")
        if not isinstance(transport.get("stdout_items"), list):
            raise ContractError("command fixture stdout items are malformed")

        owner_path: Path | None = None
        result = None
        invocation_record: dict[str, Any] | None = None
        executable_sha256: str | None = None

        with tempfile.TemporaryDirectory(prefix="wi010-youtube-") as owner_dir:
            owner_path = Path(owner_dir)
            executable = owner_path / "yt-dlp"
            invocation_path = owner_path / "invocation.json"
            executable.write_text(_FAKE_YTDLP, encoding="utf-8")
            executable.chmod(0o700)
            executable_stat = executable.lstat()
            if (
                stat.S_ISLNK(executable_stat.st_mode)
                or executable_stat.st_uid != os.getuid()
                or stat.S_IMODE(executable_stat.st_mode) != 0o700
            ):
                raise ContractError("fake executable ownership is unsafe")
            isolated_path = str(owner_path)
            resolved = shutil.which("yt-dlp", path=isolated_path)
            if resolved is None or Path(resolved).resolve() != executable.resolve():
                raise ContractError("fake executable resolution is not exact")
            executable_sha256 = _digest_bytes(executable.read_bytes())

            request = service_contracts.AcquisitionWorkRequest.from_dict(
                {
                    "schema_version": 1,
                    "work_id": "wi010-youtube-command",
                    "job_id": "wi010-provider-acceptance",
                    "lease_generation": 1,
                    "attempt": 1,
                    "profile_id": "provider-free",
                    "source": "youtube",
                    "query": query,
                    "from_date": from_date,
                    "to_date": to_date,
                    "depth": "standard",
                    "adapter": "youtube_ytdlp",
                    "adapter_version": "1",
                    "wall_timeout_seconds": 10,
                    "item_limit": item_limit,
                    "network_request_limit": 1,
                    "cost_budget_cents": 0,
                }
            )
            isolated_environment = {
                "PATH": isolated_path,
                "LC_ALL": "C",
                "PYTHONIOENCODING": "utf-8",
                "WI010_FIXTURE_PATH": str(fixture_path),
                "WI010_INVOCATION_PATH": str(invocation_path),
                "WI010_MAX_STDOUT_BYTES": str(_MAX_STDOUT_BYTES),
            }
            with patch.dict(os.environ, isolated_environment, clear=True):
                result = service_acquisition_worker.execute_work(
                    request,
                    {},
                    adapters={
                        "youtube_ytdlp": service_acquisition_worker._youtube_adapter
                    },
                    clock=lambda: _FIXED_OBSERVED_AT,
                )
            if invocation_path.is_file():
                raw_record = json.loads(invocation_path.read_text(encoding="utf-8"))
                if isinstance(raw_record, dict):
                    invocation_record = raw_record

        cleanup_complete = owner_path is not None and not owner_path.exists()
        if result is None:
            raise ContractError("command normalization did not produce a result")
        invocation_valid = (
            invocation_record is not None
            and invocation_record.get("invocation_count") == 1
            and invocation_record.get("argv") == expected_argv
            and isinstance(invocation_record.get("returncode"), int)
            and isinstance(invocation_record.get("stdout_bytes"), int)
            and 0 <= invocation_record["stdout_bytes"] <= _MAX_STDOUT_BYTES
            and isinstance(invocation_record.get("stdout_sha256"), str)
            and invocation_record["stdout_sha256"].startswith("sha256:")
        )
        returncode = invocation_record.get("returncode") if invocation_record else None
        success = (
            result.safe_error_code is None
            and invocation_valid
            and returncode == 0
            and cleanup_complete
        )
        reason = None
        if not invocation_valid:
            reason = "command_invocation_mismatch"
        elif not cleanup_complete:
            reason = "command_teardown_failed"
        elif returncode == 73:
            reason = "bounded_output_exceeded"
        elif returncode != 0:
            reason = "command_failed"
        elif result.safe_error_code is not None:
            reason = result.safe_error_code

        invocation_count = (
            invocation_record.get("invocation_count", 0) if invocation_record else 0
        )
        stdout_bytes = invocation_record.get("stdout_bytes", 0) if invocation_record else 0
        stdout_sha256 = (
            invocation_record.get("stdout_sha256", _digest_bytes(b""))
            if invocation_record
            else _digest_bytes(b"")
        )
        details = {
            "normalization_seam": "service_acquisition_worker.execute_work",
            "adapter_seam": "service_acquisition_worker._youtube_adapter",
            "production_adapter_invoked": invocation_count == 1,
            "command_argv_sha256": _digest_json(expected_argv),
            "executable_sha256": executable_sha256,
            "stdout_bytes": stdout_bytes,
            "stdout_sha256": stdout_sha256,
            "normalized_result_sha256": _digest_json(result.to_dict()),
            "invocation_count": invocation_count,
            "exact_owner_cleanup": cleanup_complete,
            "owner_census": 0 if cleanup_complete else 1,
        }
        return TransportObservation(
            outcome="success" if success else (reason or "command_failed"),
            transport_success=bool(returncode == 0 and invocation_valid),
            item_count=result.item_count,
            request_count=result.network_request_count or invocation_count,
            safe_reason_code=reason,
            accounting_confidence=adapter.accounting_confidence,
            raw_safe_sha256=_digest_json(result.to_dict()),
            details=details,
        )
