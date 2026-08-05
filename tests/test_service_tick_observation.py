"""Agent-browser viewer leases remain behind the explicit incident gate."""

from __future__ import annotations

import json

from lib.service_tick_observation import AgentBrowserObservationTransport


class Response:
    def __init__(self, payload):
        self.payload = json.dumps(payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self, _limit=-1):
        return self.payload


def test_agent_browser_transport_resolves_route_then_posts_view_takeover():
    requests = []

    def open_request(request, *, timeout):
        requests.append((request, timeout))
        if request.full_url.endswith("/api/service/browsers"):
            return Response(
                {
                    "success": True,
                    "data": {
                        "browsers": [
                            {
                                "id": "browser-x-1",
                                "activeSessionIds": ["last30days-facebook"],
                                "viewStreams": [
                                    {
                                        "id": "stream-rdp-1",
                                        "provider": "rdp_gateway",
                                        "readiness": {"state": "ready"},
                                        "routeDescriptor": {
                                            "publicOperatorUrl": (
                                                "https://guac.example.test/client/stored"
                                            )
                                        },
                                    }
                                ],
                            }
                        ]
                    },
                }
            )
        if request.full_url.endswith("/api/service/sessions"):
            return Response(
                {
                    "success": True,
                    "data": {
                        "sessions": [
                            {
                                "id": "last30days-facebook",
                                "browserIds": ["browser-x-1"],
                            }
                        ]
                    },
                }
            )
        assert request.full_url.endswith("/api/service/request")
        return Response(
            {
                "success": True,
                "data": {
                    "status": "ready",
                    "viewerLeaseId": "viewer-lease-1",
                    "externalUrl": "https://guac.example.test/client/fresh",
                },
            }
        )

    transport = AgentBrowserObservationTransport(
        "http://127.0.0.1:4848",
        urlopen=open_request,
    )

    lease = transport.acquire(
        incident_id="incident-1",
        public_operator_url="https://guac.example.test/client/stored",
    )

    assert lease.viewer_lease_id == "viewer-lease-1"
    assert lease.public_operator_url == "https://guac.example.test/client/fresh"
    assert [request.get_method() for request, _ in requests] == [
        "GET",
        "GET",
        "POST",
    ]
    payload = json.loads(requests[2][0].data)
    assert payload == {
        "serviceName": "last30days",
        "agentName": "incident-observer",
        "taskName": "observe-incident-1",
        "browserId": "browser-x-1",
        "sessionName": "last30days-facebook",
        "action": "view_takeover",
        "params": {
            "browserId": "browser-x-1",
            "sessionName": "last30days-facebook",
            "streamId": "stream-rdp-1",
            "provider": "rdp_gateway",
            "openMode": "external",
        },
    }
