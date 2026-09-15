"""Owned in-memory browser protocol tracer for WI-010's five browser adapters."""

from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

_SKILL_SCRIPTS = Path(__file__).resolve().parents[3] / "skills/last30days/scripts"
if str(_SKILL_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SKILL_SCRIPTS))

from lib import service_contracts
from lib.service_acquisition_worker import execute_work

from .contracts import ContractError, SealedCase, TransportObservation


@dataclass(frozen=True)
class _BrowserRoute:
    case_id: str
    source: str
    route: str
    surface_kind: str
    fixture_path: str


_BROWSER_ROUTES = {
    "x_agent_browser": _BrowserRoute(
        "x-browser",
        "x",
        "browser://x/topic-search",
        "topic",
        "tests/provider_acceptance/fixtures/x.json",
    ),
    "facebook_agent_browser": _BrowserRoute(
        "facebook-browser",
        "facebook",
        "browser://facebook/topic-search",
        "topic",
        "tests/provider_acceptance/fixtures/facebook.json",
    ),
    "linkedin_agent_browser": _BrowserRoute(
        "linkedin-post-browser",
        "linkedin",
        "browser://linkedin/post-search",
        "topic",
        "tests/provider_acceptance/fixtures/linkedin_post.json",
    ),
    "linkedin_profile_agent_browser": _BrowserRoute(
        "linkedin-profile-browser",
        "linkedin",
        "browser://linkedin/profile",
        "profile",
        "tests/provider_acceptance/fixtures/linkedin_profile.json",
    ),
    "reddit_agent_browser": _BrowserRoute(
        "reddit-browser",
        "reddit",
        "browser://reddit/topic-search",
        "topic",
        "tests/provider_acceptance/fixtures/reddit_browser.json",
    ),
}


def _canonical_digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode()
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


class BrowserProtocolSimulator:
    """A single-request protocol endpoint with explicit lease ownership."""

    def __init__(self, responses: Mapping[str, Mapping[str, Any]]) -> None:
        self._responses = {
            route: dict(response) for route, response in responses.items()
        }
        self._owners: dict[str, str] = {}
        self._request_counts: dict[str, int] = {}

    def acquire(self, *, owner: str, adapter_id: str) -> None:
        if owner in self._owners:
            raise ContractError("browser_owner_already_acquired")
        if adapter_id not in _BROWSER_ROUTES:
            raise ContractError("browser_adapter_mismatch")
        self._owners[owner] = adapter_id
        self._request_counts[owner] = 0

    def request(self, *, owner: str, adapter_id: str, route: str) -> dict[str, Any]:
        if self._owners.get(owner) != adapter_id:
            raise ContractError("browser_owner_mismatch")
        expected = _BROWSER_ROUTES[adapter_id].route
        if route != expected or route not in self._responses:
            raise ContractError("browser_route_mismatch")
        count = self._request_counts[owner] + 1
        self._request_counts[owner] = count
        if count > 1:
            raise ContractError("browser_request_budget_exhausted")
        return json.loads(json.dumps(self._responses[route]))

    def release(self, *, owner: str) -> None:
        if owner not in self._owners:
            raise ContractError("browser_owner_mismatch")
        del self._owners[owner]
        del self._request_counts[owner]

    def owner_census(self, *, owner: str) -> int:
        return int(owner in self._owners)


class BrowserTracer:
    """Replay one sealed browser fixture through the production normalization seam."""

    def __init__(self, repo_root: Path | str = ".") -> None:
        self._repo_root = Path(repo_root).resolve()

    def __call__(self, case: SealedCase, *, item_limit: int) -> TransportObservation:
        definition = _BROWSER_ROUTES.get(case.case.adapter_id)
        if (
            definition is None
            or case.case.case_id != definition.case_id
            or case.case.transport != "browser"
            or case.case.source != definition.source
            or case.case.fixture_path != definition.fixture_path
        ):
            raise ContractError("browser_case_route_mismatch")
        fixture_path = (self._repo_root / case.case.fixture_path).resolve()
        if self._repo_root not in fixture_path.parents or not fixture_path.is_file():
            raise ContractError("browser_fixture_unavailable")
        fixture_bytes = fixture_path.read_bytes()
        fixture_digest = "sha256:" + hashlib.sha256(fixture_bytes).hexdigest()
        if fixture_digest != case.fixture_sha256:
            raise ContractError("browser_fixture_digest_mismatch")
        try:
            fixture = json.loads(fixture_bytes)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ContractError("browser_fixture_malformed") from exc
        if (
            not isinstance(fixture, dict)
            or set(fixture) != {"adapter_id", "route", "items"}
            or fixture.get("adapter_id") != case.case.adapter_id
            or fixture.get("route") != definition.route
            or not isinstance(fixture.get("items"), list)
        ):
            raise ContractError("browser_fixture_schema_mismatch")

        owner_digest = hashlib.sha256(case.case.case_id.encode()).hexdigest()[:12]
        owner = "wi010-browser-" + owner_digest
        simulator = BrowserProtocolSimulator(
            {
                definition.route: {
                    "items": fixture["items"],
                    "diagnostics": {"accepted_count": len(fixture["items"])},
                }
            }
        )
        simulator.acquire(owner=owner, adapter_id=case.case.adapter_id)
        request_count = 0
        try:
            def adapter(_request, _config):
                nonlocal request_count
                raw = simulator.request(
                    owner=owner,
                    adapter_id=case.case.adapter_id,
                    route=definition.route,
                )
                request_count += 1
                raw["_network_request_count"] = 1
                return raw

            request = service_contracts.AcquisitionWorkRequest.from_dict(
                {
                    "schema_version": 1,
                    "work_id": f"work-{case.case.case_id}",
                    "job_id": f"job-{case.case.case_id}",
                    "lease_generation": 1,
                    "attempt": 1,
                    "profile_id": "provider-free-fixture",
                    "source": case.case.source,
                    "query": "provider acceptance fixture",
                    "from_date": "2026-09-01",
                    "to_date": "2026-09-30",
                    "depth": "standard",
                    "adapter": case.case.adapter_id,
                    "adapter_version": "1",
                    "wall_timeout_seconds": 30,
                    "item_limit": item_limit,
                    "network_request_limit": 1,
                    "cost_budget_cents": 0,
                    "surface_kind": definition.surface_kind,
                }
            )
            frozen_time = datetime(2026, 9, 14, 12, 0, tzinfo=timezone.utc)
            result = execute_work(
                request,
                {},
                adapters={case.case.adapter_id: adapter},
                clock=lambda: frozen_time,
            )
            safe_result = result.to_dict()
        finally:
            simulator.release(owner=owner)
        owner_census = simulator.owner_census(owner=owner)
        if owner_census != 0:
            raise ContractError("browser_teardown_failed")
        success = result.safe_error_code is None
        return TransportObservation(
            outcome="success" if success else "parser_drift",
            transport_success=True,
            item_count=result.item_count,
            request_count=request_count,
            safe_reason_code=None if success else result.safe_error_code,
            accounting_confidence="opaque_request_equivalent",
            raw_safe_sha256=_canonical_digest(safe_result),
            details={
                "protocol": "in_memory_browser_v1",
                "route_sha256": _canonical_digest(definition.route),
                "normalized_result_sha256": _canonical_digest(safe_result),
                "owner_sha256": _canonical_digest(owner),
                "owner_census": owner_census,
                "exact_owner_teardown": True,
            },
        )
