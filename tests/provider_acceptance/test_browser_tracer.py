import hashlib
from pathlib import Path

import pytest

from dev.last30days.provider_acceptance.browser_tracer import (
    BrowserProtocolSimulator,
    BrowserTracer,
    _BROWSER_ROUTES,
)
from lib import service_acquisition_worker
from dev.last30days.provider_acceptance.catalog import default_catalog
from dev.last30days.provider_acceptance.contracts import ContractError, SealedCase


ROOT = Path(__file__).resolve().parents[2]


def _sealed_browser_cases():
    for case in default_catalog().cases:
        if case.transport != "browser":
            continue
        fixture = ROOT / case.fixture_path
        yield SealedCase(
            case,
            "sha256:" + hashlib.sha256(fixture.read_bytes()).hexdigest(),
        )


@pytest.mark.parametrize(
    "case",
    list(_sealed_browser_cases()),
    ids=lambda value: value.case.case_id,
)
def test_browser_tracer_normalizes_all_five_adapters_without_external_effects(case):
    observation = BrowserTracer(ROOT)(case, item_limit=3)

    assert observation.outcome == "success"
    assert observation.transport_success
    assert observation.item_count == 1
    assert observation.request_count == 1
    assert observation.safe_reason_code is None
    assert observation.accounting_confidence == "opaque_request_equivalent"
    assert observation.raw_safe_sha256.startswith("sha256:")
    assert observation.raw_safe_sha256 != case.fixture_sha256
    assert set(observation.details) == {
        "protocol",
        "production_adapter_invoked",
        "route_sha256",
        "normalized_result_sha256",
        "owner_sha256",
        "owner_census",
        "exact_owner_teardown",
    }
    assert observation.details["owner_census"] == 0
    assert observation.details["exact_owner_teardown"] is True
    assert observation.details["production_adapter_invoked"] is True
    assert "browser://" not in str(observation.details)


def test_browser_protocol_rejects_wrong_route_before_consuming_request():
    adapter_id = "x_agent_browser"
    route = _BROWSER_ROUTES[adapter_id].route
    simulator = BrowserProtocolSimulator({route: {"items": []}})
    simulator.acquire(owner="owner-one", adapter_id=adapter_id)

    with pytest.raises(ContractError, match="browser_route_mismatch"):
        simulator.request(
            owner="owner-one", adapter_id=adapter_id, route="browser://x/feed"
        )
    assert simulator.request(
        owner="owner-one", adapter_id=adapter_id, route=route
    ) == {"items": []}
    with pytest.raises(ContractError, match="browser_request_budget_exhausted"):
        simulator.request(owner="owner-one", adapter_id=adapter_id, route=route)
    simulator.release(owner="owner-one")
    assert simulator.owner_census(owner="owner-one") == 0


def test_browser_protocol_rejects_non_owner_and_adapter_mismatch():
    adapter_id = "facebook_agent_browser"
    route = _BROWSER_ROUTES[adapter_id].route
    simulator = BrowserProtocolSimulator({route: {"items": []}})
    simulator.acquire(owner="owner-one", adapter_id=adapter_id)

    with pytest.raises(ContractError, match="browser_owner_mismatch"):
        simulator.request(owner="owner-two", adapter_id=adapter_id, route=route)
    with pytest.raises(ContractError, match="browser_owner_mismatch"):
        simulator.request(
            owner="owner-one", adapter_id="x_agent_browser", route=route
        )
    simulator.release(owner="owner-one")


@pytest.mark.parametrize(
    "case",
    list(_sealed_browser_cases()),
    ids=lambda value: value.case.case_id,
)
def test_browser_tracer_invokes_the_production_adapter_boundary(monkeypatch, case):
    calls = []
    original = service_acquisition_worker._DEFAULT_ADAPTERS[case.case.adapter_id]

    def spy(request, config):
        calls.append((request.adapter, request.source))
        return original(request, config)

    monkeypatch.setitem(
        service_acquisition_worker._DEFAULT_ADAPTERS,
        case.case.adapter_id,
        spy,
    )

    observation = BrowserTracer(ROOT)(case, item_limit=3)

    assert observation.outcome == "success"
    assert calls == [(case.case.adapter_id, case.case.source)]


def test_browser_tracer_rejects_tampered_fixture_before_protocol_invocation(tmp_path):
    case = next(_sealed_browser_cases())
    fixture = tmp_path / case.case.fixture_path
    fixture.parent.mkdir(parents=True)
    fixture.write_text('{"adapter_id":"x_agent_browser","route":"wrong","items":[]}')

    with pytest.raises(ContractError, match="browser_fixture_digest_mismatch"):
        BrowserTracer(tmp_path)(case, item_limit=3)
