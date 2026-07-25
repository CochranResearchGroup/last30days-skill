"""Private HTTP/JSON transport over a user-scoped Unix-domain socket."""

from __future__ import annotations

import fcntl
import json
import os
import socket
import socketserver
import stat
import struct
import urllib.parse
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from typing import Any, Protocol

from . import service_contracts as contracts
from .service_app import JobResumeConflictError


MAX_REQUEST_BYTES = 131_072
MAX_RESPONSE_BYTES = 131_072


class ServiceAlreadyRunningError(RuntimeError):
    """Raised when a live process already owns the configured socket."""


class ServiceApplication(Protocol):
    def health(self) -> dict[str, Any]: ...

    def service_info(self) -> contracts.ServiceInfo: ...

    def job(self, job_id: str) -> contracts.JobRecord: ...

    def resume_job(self, job_id: str) -> contracts.JobRecord: ...

    def query(self, request: contracts.QueryRequest) -> contracts.QueryResponse: ...

    def topic(self, payload: dict[str, object]) -> dict[str, object]: ...

    def intelligence(self, payload: dict[str, object]) -> dict[str, object]: ...


class _RequestHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = "last30days-service/0.1"
    sys_version = ""

    @property
    def application(self) -> ServiceApplication:
        return self.server.application  # type: ignore[attr-defined,no-any-return]

    def log_message(self, format: str, *args: object) -> None:
        return

    def handle(self) -> None:
        if hasattr(socket, "SO_PEERCRED"):
            credentials = self.request.getsockopt(
                socket.SOL_SOCKET,
                socket.SO_PEERCRED,
                struct.calcsize("3i"),
            )
            _, peer_uid, _ = struct.unpack("3i", credentials)
            if peer_uid != os.geteuid():
                return
        super().handle()

    def _write_json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(
            payload,
            allow_nan=False,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        if len(body) > MAX_RESPONSE_BYTES:
            status = 500
            body = (
                b'{"code":"response_too_large","message":"service response '
                b'exceeded its transport limit","retryable":false,'
                b'"schema_version":1}'
            )
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header(
            "X-Last30days-Contract-SHA256",
            contracts.SCHEMA_CATALOG_SHA256,
        )
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(body)

    def _error(self, status: int, code: str, message: str) -> None:
        self._write_json(
            status,
            {
                "schema_version": contracts.SCHEMA_VERSION,
                "code": code,
                "message": message,
                "retryable": status >= 500,
            },
        )

    def do_GET(self) -> None:
        try:
            if self.path == "/v1/health":
                self._write_json(200, self.application.health())
                return
            if self.path == "/v1/service-info":
                self._write_json(200, self.application.service_info().to_dict())
                return
            if self.path in {"/v1/capabilities", "/v1/sources"}:
                info = self.application.service_info().to_dict()
                field = self.path.removeprefix("/v1/")
                self._write_json(
                    200,
                    {
                        "schema_version": contracts.SCHEMA_VERSION,
                        field: info[field],
                    },
                )
                return
            if self.path == "/v1/topics":
                self._write_json(200, self.application.topic({"action": "list"}))
                return
            if self.path.startswith("/v1/jobs/"):
                job_id = urllib.parse.unquote(self.path.removeprefix("/v1/jobs/"))
                self._write_json(200, self.application.job(job_id).to_dict())
                return
            self._error(404, "not_found", "unknown service endpoint")
        except KeyError:
            self._error(404, "job_not_found", "job was not found")
        except Exception:
            self._error(500, "internal_error", "service request failed")

    def do_POST(self) -> None:
        resume_prefix = "/v1/jobs/"
        resume_suffix = "/resume"
        resume_job_id = None
        if self.path.startswith(resume_prefix) and self.path.endswith(resume_suffix):
            encoded_job_id = self.path[
                len(resume_prefix) : -len(resume_suffix)
            ]
            if encoded_job_id and "/" not in encoded_job_id:
                resume_job_id = urllib.parse.unquote(encoded_job_id)
        if (
            self.path not in {"/v1/query", "/v1/topic", "/v1/intelligence"}
            and resume_job_id is None
        ):
            self._error(404, "not_found", "unknown service endpoint")
            return
        raw_length = self.headers.get("Content-Length")
        try:
            length = int(raw_length or "")
        except ValueError:
            self._error(400, "invalid_content_length", "invalid request length")
            return
        if not 0 < length <= MAX_REQUEST_BYTES:
            self._error(413, "request_too_large", "request body is outside limits")
            return
        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            if not isinstance(payload, dict):
                raise contracts.ContractValidationError(
                    "request body must be an object"
                )
            if resume_job_id is not None:
                if payload:
                    raise contracts.ContractValidationError(
                        "resume request body must be empty"
                    )
                response = self.application.resume_job(resume_job_id).to_dict()
            elif self.path == "/v1/query":
                request = contracts.QueryRequest.from_dict(payload)
                response = self.application.query(request).to_dict()
            elif self.path == "/v1/topic":
                response = self.application.topic(payload)
            else:
                response = self.application.intelligence(payload)
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._error(400, "invalid_json", "request body must be valid JSON")
            return
        except contracts.ContractValidationError as exc:
            del exc
            self._error(400, "invalid_contract", "request contract is invalid")
            return
        except KeyError:
            self._error(404, "job_not_found", "job was not found")
            return
        except JobResumeConflictError:
            self._error(
                409,
                "job_not_awaiting_operator",
                "only an awaiting-operator job with attempts remaining can be resumed",
            )
            return
        except Exception:
            self._error(500, "internal_error", "service request failed")
            return
        self._write_json(200, response)


class UnixServiceServer(socketserver.ThreadingMixIn, socketserver.UnixStreamServer):
    """Threaded same-user HTTP server with safe stale-socket recovery."""

    daemon_threads = True
    block_on_close = True

    def __init__(self, socket_path: Path, application: ServiceApplication):
        self.socket_path = Path(socket_path)
        self.lock_path = self.socket_path.parent / "service.lock"
        self.application = application
        self._socket_identity: tuple[int, int] | None = None
        self._lock_fd: int | None = None
        self._closed = False
        self._prepare_runtime_directory()
        self._acquire_lock()
        try:
            self._prepare_socket_path()
            super().__init__(str(self.socket_path), _RequestHandler)
            os.chmod(self.socket_path, 0o600)
            stat_result = self.socket_path.stat()
            self._socket_identity = (stat_result.st_dev, stat_result.st_ino)
        except Exception:
            self._release_lock()
            raise

    def _prepare_runtime_directory(self) -> None:
        self.socket_path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        directory_stat = self.socket_path.parent.lstat()
        if stat.S_ISLNK(directory_stat.st_mode) or not stat.S_ISDIR(
            directory_stat.st_mode
        ):
            raise RuntimeError("service runtime path must be a real directory")
        if directory_stat.st_uid != os.geteuid():
            raise RuntimeError("service runtime directory has the wrong owner")
        os.chmod(self.socket_path.parent, 0o700)

    def _acquire_lock(self) -> None:
        flags = os.O_CREAT | os.O_RDWR
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        lock_fd = os.open(self.lock_path, flags, 0o600)
        try:
            lock_stat = os.fstat(lock_fd)
            if not stat.S_ISREG(lock_stat.st_mode):
                raise RuntimeError("service lock path must be a regular file")
            if lock_stat.st_uid != os.geteuid():
                raise RuntimeError("service lock file has the wrong owner")
            os.fchmod(lock_fd, 0o600)
            fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            os.close(lock_fd)
            raise ServiceAlreadyRunningError(
                f"service singleton is already held for {self.socket_path}"
            ) from exc
        except Exception:
            os.close(lock_fd)
            raise
        self._lock_fd = lock_fd

    def _release_lock(self) -> None:
        if self._lock_fd is None:
            return
        try:
            fcntl.flock(self._lock_fd, fcntl.LOCK_UN)
        finally:
            os.close(self._lock_fd)
            self._lock_fd = None

    def _prepare_socket_path(self) -> None:
        if not os.path.lexists(self.socket_path):
            return
        socket_stat = self.socket_path.lstat()
        if (
            stat.S_ISLNK(socket_stat.st_mode)
            or not stat.S_ISSOCK(socket_stat.st_mode)
            or socket_stat.st_uid != os.geteuid()
        ):
            raise RuntimeError(
                "service socket path is not an owned Unix socket"
            )
        probe = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        probe.settimeout(0.2)
        try:
            probe.connect(str(self.socket_path))
        except OSError:
            self.socket_path.unlink()
        else:
            raise ServiceAlreadyRunningError(
                f"service already running at {self.socket_path}"
            )
        finally:
            probe.close()

    def server_close(self) -> None:
        if self._closed:
            return
        self._closed = True
        try:
            super().server_close()
        finally:
            try:
                stat_result = self.socket_path.stat()
            except FileNotFoundError:
                pass
            else:
                identity = (stat_result.st_dev, stat_result.st_ino)
                if (
                    identity == self._socket_identity
                    and self.socket_path.is_socket()
                ):
                    self.socket_path.unlink()
            self._release_lock()
