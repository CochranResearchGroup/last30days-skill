"""Deadline-aware, destination-pinned HTTP transport for tick media."""

from __future__ import annotations

import http.client
import ipaddress
import queue
import socket
import ssl
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Protocol
from urllib.parse import urlparse


class MediaTransportError(RuntimeError):
    """Base class for fail-closed media transport failures."""


class UnsafeMediaDestination(MediaTransportError):
    """Raised when URL admission and the connected peer do not agree."""


class MediaDeadlineExceeded(MediaTransportError):
    """Raised when the shared tick wall deadline is exhausted."""


Resolver = Callable[..., Any]
SocketFactory = Callable[[int, int, int], Any]
SslContextFactory = Callable[[], Any]


@dataclass(frozen=True)
class PinnedMediaResponse:
    status: int
    headers: dict[str, str]
    content: bytes


class MediaTransport(Protocol):
    def get(
        self,
        source_url: str,
        *,
        deadline: float,
        maximum_bytes: int,
        before_connect: Callable[[], None],
    ) -> PinnedMediaResponse: ...


class DeadlinePinnedMediaTransport:
    """Resolve, admit, and connect one media request without a second DNS choice."""

    def __init__(
        self,
        *,
        resolver: Resolver = socket.getaddrinfo,
        socket_factory: SocketFactory = socket.socket,
        ssl_context_factory: SslContextFactory = ssl.create_default_context,
        monotonic_clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self.resolver = resolver
        self.socket_factory = socket_factory
        self.ssl_context_factory = ssl_context_factory
        self.monotonic = monotonic_clock

    def _remaining(self, deadline: float) -> float:
        remaining = deadline - self.monotonic()
        if remaining <= 0:
            raise MediaDeadlineExceeded("media wall deadline exhausted")
        return remaining

    def _resolve(
        self,
        hostname: str,
        port: int,
        deadline: float,
    ) -> Any:
        result_queue: queue.Queue[tuple[bool, Any]] = queue.Queue(maxsize=1)

        def resolve() -> None:
            try:
                result = self.resolver(
                    hostname,
                    port,
                    family=socket.AF_UNSPEC,
                    type=socket.SOCK_STREAM,
                    proto=socket.IPPROTO_TCP,
                )
            except Exception as exc:
                result_queue.put((False, exc))
            else:
                result_queue.put((True, result))

        threading.Thread(
            target=resolve,
            name="last30days-media-dns",
            daemon=True,
        ).start()
        try:
            succeeded, value = result_queue.get(timeout=self._remaining(deadline))
        except queue.Empty as exc:
            raise MediaDeadlineExceeded("media DNS deadline exhausted") from exc
        self._remaining(deadline)
        if not succeeded:
            raise MediaTransportError("media DNS resolution failed") from value
        return value

    def _destination(
        self,
        source_url: str,
        deadline: float,
    ) -> tuple[str, int, tuple[Any, ...]]:
        if any(
            ord(character) <= 32 or ord(character) == 127
            for character in source_url
        ):
            raise UnsafeMediaDestination("unsafe media URL")
        parsed = urlparse(source_url)
        try:
            explicit_port = parsed.port
        except ValueError as exc:
            raise UnsafeMediaDestination("unsafe media URL port") from exc
        port = 443 if explicit_port is None else explicit_port
        if (
            parsed.scheme != "https"
            or not parsed.hostname
            or parsed.username is not None
            or parsed.password is not None
            or parsed.fragment
            or not 1 <= port <= 65_535
        ):
            raise UnsafeMediaDestination("unsafe media URL")
        hostname = parsed.hostname.rstrip(".")
        if not hostname:
            raise UnsafeMediaDestination("unsafe media URL hostname")
        try:
            literal = ipaddress.ip_address(hostname)
        except ValueError:
            resolved = self._resolve(hostname, port, deadline)
        else:
            family = socket.AF_INET6 if literal.version == 6 else socket.AF_INET
            sockaddr: tuple[Any, ...] = (
                (literal.compressed, port, 0, 0)
                if literal.version == 6
                else (literal.compressed, port)
            )
            resolved = [(family, socket.SOCK_STREAM, socket.IPPROTO_TCP, "", sockaddr)]
        admitted: list[
            tuple[
                int,
                int,
                int,
                tuple[Any, ...],
                ipaddress.IPv4Address | ipaddress.IPv6Address,
            ]
        ] = []
        for result in resolved:
            if not isinstance(result, tuple) or len(result) < 5:
                continue
            family, socktype, proto, _canonname, sockaddr = result[:5]
            if (
                family not in {socket.AF_INET, socket.AF_INET6}
                or not isinstance(sockaddr, tuple)
                or not sockaddr
            ):
                continue
            try:
                address = ipaddress.ip_address(str(sockaddr[0]))
            except ValueError:
                continue
            admitted.append((family, socktype, proto, sockaddr, address))
        if not admitted or any(not entry[4].is_global for entry in admitted):
            raise UnsafeMediaDestination("unsafe media destination")
        family, socktype, proto, sockaddr, address = admitted[0]
        return hostname, port, (family, socktype, proto, sockaddr, address)

    def get(
        self,
        source_url: str,
        *,
        deadline: float,
        maximum_bytes: int,
        before_connect: Callable[[], None],
    ) -> PinnedMediaResponse:
        if (
            isinstance(maximum_bytes, bool)
            or not isinstance(maximum_bytes, int)
            or maximum_bytes <= 0
        ):
            raise ValueError("maximum_bytes must be a positive integer")
        self._remaining(deadline)
        hostname, port, destination = self._destination(source_url, deadline)
        self._remaining(deadline)
        family, socktype, proto, sockaddr, admitted_address = destination
        before_connect()
        sock = None
        tls_sock = None
        connection = None
        try:
            sock = self.socket_factory(family, socktype, proto)
            sock.settimeout(self._remaining(deadline))
            sock.connect(sockaddr)
            self._remaining(deadline)
            peer = sock.getpeername()
            if not isinstance(peer, tuple) or not peer:
                raise UnsafeMediaDestination("media peer identity is unavailable")
            try:
                peer_address = ipaddress.ip_address(str(peer[0]))
            except ValueError as exc:
                raise UnsafeMediaDestination("media peer identity is invalid") from exc
            if peer_address != admitted_address:
                raise UnsafeMediaDestination(
                    "media peer differs from the admitted destination"
                )
            sock.settimeout(self._remaining(deadline))
            tls_sock = self.ssl_context_factory().wrap_socket(
                sock,
                server_hostname=hostname,
            )
            self._remaining(deadline)

            parsed = urlparse(source_url)
            target = parsed.path or "/"
            if parsed.query:
                target += "?" + parsed.query
            host_header = f"[{hostname}]" if ":" in hostname else hostname
            if port != 443:
                host_header += f":{port}"

            connection = http.client.HTTPConnection(
                host=hostname,
                port=port,
                timeout=self._remaining(deadline),
            )
            connection.sock = tls_sock
            tls_sock.settimeout(self._remaining(deadline))
            connection.putrequest(
                "GET",
                target,
                skip_host=True,
                skip_accept_encoding=True,
            )
            connection.putheader("Host", host_header)
            connection.putheader("User-Agent", "last30days-media-fetch/1")
            connection.putheader("Accept", "*/*")
            connection.endheaders()
            self._remaining(deadline)

            tls_sock.settimeout(self._remaining(deadline))
            response = connection.getresponse()
            self._remaining(deadline)
            headers = {
                str(key).casefold(): str(value)
                for key, value in response.getheaders()
            }
            if 300 <= response.status < 400:
                content = b""
            else:
                tls_sock.settimeout(self._remaining(deadline))
                content = response.read(maximum_bytes + 1)
                self._remaining(deadline)
            return PinnedMediaResponse(
                status=int(response.status),
                headers=headers,
                content=content,
            )
        except MediaTransportError:
            raise
        except (OSError, http.client.HTTPException, ValueError) as exc:
            raise MediaTransportError("media request failed") from exc
        finally:
            if connection is not None:
                connection.close()
            elif tls_sock is not None and tls_sock is not sock:
                tls_sock.close()
            if sock is not None:
                sock.close()
