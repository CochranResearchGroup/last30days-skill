"""Deadline and destination guarantees for tick-owned media HTTP."""

from __future__ import annotations

import io
import threading
import time

import pytest

from lib.service_tick_http import (
    DeadlinePinnedMediaTransport,
    MediaDeadlineExceeded,
    MediaTransportError,
    UnsafeMediaDestination,
)


class PeerSocket:
    def __init__(self, peer_ip: str):
        self.peer_ip = peer_ip
        self.connected_to = None
        self.closed = False

    def settimeout(self, _timeout):
        return None

    def connect(self, address):
        self.connected_to = address

    def getpeername(self):
        return (self.peer_ip, 443)

    def close(self):
        self.closed = True


class HttpSocket(PeerSocket):
    def __init__(self, peer_ip: str):
        super().__init__(peer_ip)
        self.sent = bytearray()
        self.timeout_values = []

    def settimeout(self, timeout):
        self.timeout_values.append(timeout)

    def sendall(self, value):
        self.sent.extend(value)

    def makefile(self, _mode):
        return io.BytesIO(
            b"HTTP/1.1 200 OK\r\n"
            b"Content-Type: image/jpeg\r\n"
            b"Content-Length: 5\r\n"
            b"\r\nimage"
        )


def test_media_transport_rejects_a_peer_that_differs_from_the_admitted_address():
    sock = PeerSocket("203.0.113.9")
    tls_calls = []
    transport = DeadlinePinnedMediaTransport(
        resolver=lambda *_args, **_kwargs: [
            (2, 1, 6, "", ("93.184.216.34", 443))
        ],
        socket_factory=lambda *_args: sock,
        ssl_context_factory=lambda: tls_calls.append(True),
        monotonic_clock=lambda: 100.0,
    )

    with pytest.raises(UnsafeMediaDestination):
        transport.get(
            "https://cdn.example.test/image.jpg",
            deadline=101.0,
            maximum_bytes=1_024,
            before_connect=lambda: None,
        )

    assert sock.connected_to == ("93.184.216.34", 443)
    assert sock.closed is True
    assert tls_calls == []


def test_media_transport_pins_ip_while_preserving_tls_name_and_host_header():
    sock = HttpSocket("93.184.216.34")
    tls_names = []
    connect_calls = []

    class Context:
        def wrap_socket(self, raw_socket, *, server_hostname):
            tls_names.append(server_hostname)
            return raw_socket

    transport = DeadlinePinnedMediaTransport(
        resolver=lambda *_args, **_kwargs: [
            (2, 1, 6, "", ("93.184.216.34", 443))
        ],
        socket_factory=lambda *_args: sock,
        ssl_context_factory=Context,
        monotonic_clock=lambda: 100.0,
    )

    response = transport.get(
        "https://cdn.example.test/image.jpg?size=large",
        deadline=101.0,
        maximum_bytes=1_024,
        before_connect=lambda: connect_calls.append(True),
    )

    request = bytes(sock.sent)
    assert response.status == 200
    assert response.headers["content-type"] == "image/jpeg"
    assert response.content == b"image"
    assert sock.connected_to == ("93.184.216.34", 443)
    assert tls_names == ["cdn.example.test"]
    assert b"GET /image.jpg?size=large HTTP/1.1\r\n" in request
    assert b"Host: cdn.example.test\r\n" in request
    assert connect_calls == [True]


def test_media_transport_bounds_dns_wait_by_the_shared_deadline():
    release_resolver = threading.Event()
    socket_calls = []

    def blocked_resolver(*_args, **_kwargs):
        release_resolver.wait(1.0)
        return [(2, 1, 6, "", ("93.184.216.34", 443))]

    transport = DeadlinePinnedMediaTransport(
        resolver=blocked_resolver,
        socket_factory=lambda *_args: socket_calls.append(True),
    )
    started = time.monotonic()
    try:
        with pytest.raises(MediaDeadlineExceeded):
            transport.get(
                "https://cdn.example.test/image.jpg",
                deadline=started + 0.02,
                maximum_bytes=1_024,
                before_connect=lambda: None,
            )
    finally:
        elapsed = time.monotonic() - started
        release_resolver.set()

    assert elapsed < 0.5
    assert socket_calls == []


def test_media_transport_wraps_connection_failure_and_closes_the_socket():
    class FailingSocket(PeerSocket):
        def connect(self, address):
            self.connected_to = address
            raise OSError("connection refused")

    sock = FailingSocket("93.184.216.34")
    transport = DeadlinePinnedMediaTransport(
        resolver=lambda *_args, **_kwargs: [
            (2, 1, 6, "", ("93.184.216.34", 443))
        ],
        socket_factory=lambda *_args: sock,
        monotonic_clock=lambda: 100.0,
    )

    with pytest.raises(MediaTransportError, match="media request failed"):
        transport.get(
            "https://cdn.example.test/image.jpg",
            deadline=101.0,
            maximum_bytes=1_024,
            before_connect=lambda: None,
        )

    assert sock.connected_to == ("93.184.216.34", 443)
    assert sock.closed is True


@pytest.mark.parametrize(
    "url",
    [
        "https://93.184.216.34:0/image.jpg",
        "https://93.184.216.34/image.jpg\r\nX-Injected: value",
    ],
)
def test_media_transport_rejects_malformed_urls_before_network(url):
    socket_calls = []
    transport = DeadlinePinnedMediaTransport(
        socket_factory=lambda *_args: socket_calls.append(True),
        monotonic_clock=lambda: 100.0,
    )

    with pytest.raises(UnsafeMediaDestination):
        transport.get(
            url,
            deadline=101.0,
            maximum_bytes=1_024,
            before_connect=lambda: None,
        )

    assert socket_calls == []


def test_media_transport_rejects_mixed_global_and_private_dns_answers():
    socket_calls = []
    transport = DeadlinePinnedMediaTransport(
        resolver=lambda *_args, **_kwargs: [
            (2, 1, 6, "", ("93.184.216.34", 443)),
            (2, 1, 6, "", ("127.0.0.1", 443)),
        ],
        socket_factory=lambda *_args: socket_calls.append(True),
        monotonic_clock=lambda: 100.0,
    )

    with pytest.raises(UnsafeMediaDestination):
        transport.get(
            "https://cdn.example.test/image.jpg",
            deadline=101.0,
            maximum_bytes=1_024,
            before_connect=lambda: None,
        )

    assert socket_calls == []
