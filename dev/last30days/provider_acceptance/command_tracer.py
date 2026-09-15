"""Provider-free command transport tracer for the YouTube acquisition adapter."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import stat
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from lib import service_acquisition_worker, service_contracts

from .contracts import ContractError, SealedCase, TransportObservation


_MAX_STDOUT_BYTES = 65_536
_FIXED_OBSERVED_AT = datetime(2026, 9, 14, 12, 0, tzinfo=timezone.utc)
_FAKE_YTDLP = r'''#!/usr/bin/python3
import json
import os
import sys

fixture_path = os.environ["WI010_FIXTURE_PATH"]
invocation_path = os.environ["WI010_INVOCATION_PATH"]
maximum = int(os.environ["WI010_MAX_STDOUT_BYTES"])

descriptor = os.open(invocation_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
with os.fdopen(descriptor, "w", encoding="utf-8") as invocation:
    json.dump(sys.argv[1:], invocation, ensure_ascii=True, separators=(",", ":"))

with open(fixture_path, encoding="utf-8") as fixture_file:
    fixture = json.load(fixture_file)
lines = [json.dumps(item, ensure_ascii=True, separators=(",", ":")) for item in fixture["items"]]
payload = ("\n".join(lines) + ("\n" if lines else "")).encode("utf-8")
if len(payload) > maximum:
    sys.stderr.write("bounded_output_exceeded\n")
    raise SystemExit(73)
sys.stdout.buffer.write(payload)
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

        state: dict[str, Any] = {
            "invocations": 0,
            "stdout": b"",
            "returncode": None,
            "argv": None,
            "executable_sha256": None,
        }
        owner_path: Path | None = None
        result = None
        invocation_record: list[str] | None = None

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
            state["executable_sha256"] = _digest_bytes(executable.read_bytes())

            command = [
                "yt-dlp",
                "--ignore-config",
                "--no-cookies-from-browser",
                f"ytsearch8:{query}",
                "--flat-playlist",
                "--dump-json",
                "--no-warnings",
                "--no-download",
            ]

            def fake_command_adapter(
                _request: service_contracts.AcquisitionWorkRequest,
                _config: dict[str, str],
            ) -> dict[str, Any]:
                if state["invocations"] != 0:
                    raise RuntimeError("command invocation budget exhausted")
                state["invocations"] = 1
                completed = subprocess.run(
                    command,
                    cwd=owner_path,
                    env={
                        "PATH": isolated_path,
                        "LC_ALL": "C",
                        "PYTHONIOENCODING": "utf-8",
                        "WI010_FIXTURE_PATH": str(fixture_path),
                        "WI010_INVOCATION_PATH": str(invocation_path),
                        "WI010_MAX_STDOUT_BYTES": str(_MAX_STDOUT_BYTES),
                    },
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=5,
                    check=False,
                )
                state["returncode"] = completed.returncode
                state["stdout"] = completed.stdout
                state["argv"] = command[1:]
                if len(completed.stdout) > _MAX_STDOUT_BYTES:
                    return {
                        "items": [],
                        "error_type": "bounded_output_exceeded",
                        "diagnostics": {"failure_stage": "command_stdout"},
                        "_network_request_count": 1,
                    }
                if completed.returncode != 0:
                    reason = (
                        "bounded_output_exceeded"
                        if completed.returncode == 73
                        else "command_failed"
                    )
                    return {
                        "items": [],
                        "error_type": reason,
                        "diagnostics": {"failure_stage": "command_execution"},
                        "_network_request_count": 1,
                    }
                items: list[dict[str, Any]] = []
                try:
                    for line in completed.stdout.splitlines():
                        parsed = json.loads(line)
                        if not isinstance(parsed, dict):
                            raise ValueError("yt-dlp item is not an object")
                        items.append(parsed)
                except (UnicodeDecodeError, json.JSONDecodeError, ValueError):
                    return {
                        "items": [],
                        "error_type": "parser_drift",
                        "diagnostics": {"failure_stage": "command_parse"},
                        "_network_request_count": 1,
                    }
                return {"items": items, "_network_request_count": 1}

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
            result = service_acquisition_worker.execute_work(
                request,
                {},
                adapters={"youtube_ytdlp": fake_command_adapter},
                clock=lambda: _FIXED_OBSERVED_AT,
            )
            if invocation_path.is_file():
                raw_record = json.loads(invocation_path.read_text(encoding="utf-8"))
                if isinstance(raw_record, list) and all(
                    isinstance(value, str) for value in raw_record
                ):
                    invocation_record = raw_record

        cleanup_complete = owner_path is not None and not owner_path.exists()
        if result is None:
            raise ContractError("command normalization did not produce a result")
        invocation_valid = (
            state["invocations"] == 1
            and invocation_record == state["argv"]
            and invocation_record == expected_argv
            and state["returncode"] is not None
        )
        success = result.safe_error_code is None and invocation_valid and cleanup_complete
        reason = None
        if not invocation_valid:
            reason = "command_invocation_mismatch"
        elif not cleanup_complete:
            reason = "command_teardown_failed"
        elif result.safe_error_code is not None:
            reason = result.safe_error_code

        stdout = state["stdout"]
        assert isinstance(stdout, bytes)
        details = {
            "normalization_seam": "service_acquisition_worker.execute_work",
            "command_argv_sha256": _digest_json(state["argv"]),
            "executable_sha256": state["executable_sha256"],
            "stdout_bytes": len(stdout),
            "stdout_sha256": _digest_bytes(stdout),
            "normalized_result_sha256": _digest_json(result.to_dict()),
            "invocation_count": state["invocations"],
            "exact_owner_cleanup": cleanup_complete,
            "owner_census": 0 if cleanup_complete else 1,
        }
        return TransportObservation(
            outcome="success" if success else (reason or "command_failed"),
            transport_success=bool(state["returncode"] == 0 and invocation_valid),
            item_count=result.item_count,
            request_count=result.network_request_count or state["invocations"],
            safe_reason_code=reason,
            accounting_confidence=adapter.accounting_confidence,
            raw_safe_sha256=_digest_json(result.to_dict()),
            details=details,
        )
