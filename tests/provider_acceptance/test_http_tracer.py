from dataclasses import replace
import hashlib
import json
import socket

import pytest

from dev.last30days.provider_acceptance import (
    AcceptanceDependencies,
    CampaignSpec,
    EvidenceTier,
    ExecutionGrant,
    execute,
    prepare,
    verify,
)
from dev.last30days.provider_acceptance.catalog import default_catalog
from dev.last30days.provider_acceptance.contracts import AdapterCase, SealedCase
from dev.last30days.provider_acceptance import http_tracer as http_tracer_module
from dev.last30days.provider_acceptance.http_tracer import HttpTracer
from skills.last30days.scripts.lib import service_acquisition_worker


HTTP_CASE_IDS = ("reddit-keyless-http", "reddit-scrapecreators-http")


def _http_plan(repo_root, *, tiers=(EvidenceTier.P2,)):
    return prepare(
        CampaignSpec("wi010-http", HTTP_CASE_IDS, tiers=tiers),
        catalog=default_catalog(),
        repo_root=repo_root,
    )


@pytest.mark.parametrize("case_id", HTTP_CASE_IDS)
def test_http_tracer_uses_one_owned_loopback_request_and_real_normalization(
    monkeypatch, case_id
):
    repo_root = __file__.rsplit("/tests/", 1)[0]
    case = next(item for item in _http_plan(repo_root).cases if item.case.case_id == case_id)
    connections = []
    production_calls = []
    original_connect = socket.create_connection
    production_adapter = service_acquisition_worker._DEFAULT_ADAPTERS[
        case.case.adapter_id
    ]
    original_execute = http_tracer_module.service_acquisition_worker.execute_work

    def loopback_only(address, *args, **kwargs):
        connections.append(address)
        assert address[0] == "127.0.0.1"
        return original_connect(address, *args, **kwargs)

    monkeypatch.setattr(socket, "create_connection", loopback_only)

    def production_spy(request, config):
        production_calls.append(request.adapter)
        return production_adapter(request, config)

    def reject_adapter_replacement(request, config, **kwargs):
        assert "adapters" not in kwargs
        return original_execute(request, config, **kwargs)

    monkeypatch.setitem(
        service_acquisition_worker._DEFAULT_ADAPTERS,
        case.case.adapter_id,
        production_spy,
    )
    monkeypatch.setattr(
        http_tracer_module.service_acquisition_worker,
        "execute_work",
        reject_adapter_replacement,
    )

    observation = HttpTracer(repo_root)(case, item_limit=3)

    assert observation.outcome == "success"
    assert observation.transport_success is True
    assert observation.item_count == 1
    assert observation.request_count == 1
    assert observation.safe_reason_code is None
    assert observation.accounting_confidence == "exact"
    assert observation.raw_safe_sha256.startswith("sha256:")
    assert observation.details == {
        "adapter_variant": case.case.adapter_id,
        "exact_owner_cleanup": True,
        "loopback": True,
        "normalization_seam": "service_acquisition_worker.execute_work",
        "owned_server": True,
        "production_adapter_invoked": True,
        "request_method": "GET",
        "request_target_sha256": observation.details["request_target_sha256"],
        "server_request_count": 1,
        "owner_census": 0,
    }
    assert connections and all(address[0] == "127.0.0.1" for address in connections)
    assert production_calls == [case.case.adapter_id]
    assert "Sanitized provider-free" not in str(observation.details)


def test_http_tracer_receipts_verify_for_both_reddit_adapters():
    repo_root = __file__.rsplit("/tests/", 1)[0]
    plan = _http_plan(repo_root)
    receipt = execute(
        plan,
        grant=ExecutionGrant.for_plan(plan),
        deps=AcceptanceDependencies(
            {"http": HttpTracer(repo_root)},
            lambda *_args, **_kwargs: pytest.fail("P3 join must not run in P2 test"),
        ),
        repo_root=repo_root,
    )

    assert verify(receipt, plan=plan).accepted
    assert [(sample.adapter_id, sample.request_count, sample.item_count) for sample in receipt.samples] == [
        ("reddit_keyless", 1, 1),
        ("reddit_scrapecreators", 1, 1),
    ]


def test_http_tracer_rejects_non_loopback_route_before_server_or_request(tmp_path, monkeypatch):
    fixture = {
        "items": [],
        "request": {
            "host": "provider.example",
            "logical_host": "www.reddit.com",
            "method": "GET",
            "path": "/unsafe",
            "query": {},
        },
        "transport_response": {},
    }
    path = tmp_path / "unsafe.json"
    path.write_text(json.dumps(fixture), encoding="utf-8")
    sealed = SealedCase(
        AdapterCase(
            "reddit-unsafe-http",
            "reddit_keyless",
            "reddit",
            "http",
            "unsafe.json",
            expected_item_count=0,
        ),
        "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest(),
    )
    monkeypatch.setattr(
        "dev.last30days.provider_acceptance.http_tracer._OwnedHTTPServer",
        lambda *_args, **_kwargs: pytest.fail("unsafe route must be rejected before bind"),
    )

    observation = HttpTracer(tmp_path)(sealed, item_limit=3)

    assert observation.outcome == "route_drift"
    assert observation.transport_success is False
    assert observation.request_count == 0
    assert observation.safe_reason_code == "non_loopback_route"


def test_http_tracer_rejects_fixture_drift_without_transport(tmp_path):
    path = tmp_path / "fixture.json"
    path.write_text(
        json.dumps(
            {
                "items": [],
                "request": {
                    "host": "127.0.0.1",
                    "method": "GET",
                    "path": "/safe",
                    "query": {},
                },
            }
        ),
        encoding="utf-8",
    )
    sealed = SealedCase(
        replace(
            default_catalog().cases[5],
            fixture_path="fixture.json",
            expected_item_count=0,
        ),
        "sha256:" + "0" * 64,
    )

    observation = HttpTracer(tmp_path)(sealed, item_limit=3)

    assert observation.outcome == "parser_drift"
    assert observation.request_count == 0
    assert observation.safe_reason_code == "fixture_digest_mismatch"
