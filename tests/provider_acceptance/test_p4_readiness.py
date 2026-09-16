from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from dev.last30days.provider_acceptance.contracts import ContractError
from dev.last30days.provider_acceptance.p4_readiness import (
    ACCOUNTING_CONFIDENCE,
    MAX_BROWSER_ACTIONS,
    MAX_REQUEST_EQUIVALENTS,
    P4ReadinessReceipt,
    _digest,
    execute_x_readiness,
    packet_from_dict,
    prepare_x_packet,
    receipt_from_dict,
    verify_packet,
    verify_receipt,
)
from dev.last30days.scripts.provider_p4_readiness import main as cli_main


ROOT = Path(__file__).resolve().parents[2]
NOW = datetime(2026, 9, 15, 20, 0, tzinfo=timezone.utc)


def _target_config(path: Path, profile_id: str = "last30days-x-primary") -> Path:
    path.write_text(
        json.dumps(
            {
                "schema_version": "last30days.agent-browser-targets.v1",
                "targets": {
                    "x": {
                        "profile_id": profile_id,
                        "browser_build": "stealthcdp_chromium",
                        "browser_host": "remote_headed",
                        "control_input_provider": "manual_attached_desktop",
                        "display_isolation": "shared_display",
                        "view_stream_provider": "rdp_gateway",
                    }
                },
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    return path


class FakeClient:
    def __init__(
        self,
        *,
        auth: tuple[bool, bool, bool, bool] = (True, False, False, False),
        action_operations: tuple[str, ...] = (),
        workspace_profile: str = "last30days-x-primary",
        release_fails: bool = False,
        acquire_fails: BaseException | None = None,
    ) -> None:
        self.auth = auth
        self.action_operations = action_operations
        self.workspace_profile = workspace_profile
        self.release_fails = release_fails
        self.acquire_fails = acquire_fails
        self._service_tab_handle = {"targetId": "owned"}
        self.calls: list[str] = []
        self.budget = None
        self.prepare_consolidate_values: list[bool] = []

    def begin_run_budget(self, seconds: int) -> None:
        self.budget = seconds

    def end_run_budget(self) -> None:
        self.calls.append("end_budget")

    def acquire_workspace(self, request):
        self.calls.append("acquire_workspace")
        if self.acquire_fails:
            raise self.acquire_fails
        return SimpleNamespace(profile_id=self.workspace_profile)

    def inspect_auth(self, workspace):
        self.calls.append("inspect_auth")
        for operation in self.action_operations:
            self.act(workspace, SimpleNamespace(operation=operation))
        return SimpleNamespace(
            authenticated=self.auth[0],
            login_form=self.auth[1],
            checkpoint=self.auth[2],
            restricted=self.auth[3],
        )

    def act(self, _workspace, action):
        self.calls.append(f"act:{action.operation}")

    def prepare_site_tab(self, _workspace, _hostname, *, consolidate=False, **_kwargs):
        self.prepare_consolidate_values.append(consolidate)
        return True

    def release_workspace(self) -> None:
        self.calls.append("release_workspace")
        if self.release_fails:
            raise RuntimeError("private teardown detail")
        self._service_tab_handle = None


def _factory(client: FakeClient):
    def create(fields):
        request = SimpleNamespace(profile_id=fields["profile_id"])
        return client, request

    return create


def _packet(tmp_path: Path):
    config = _target_config(tmp_path / "agent-browser.json")
    return (
        prepare_x_packet(
            target_config_path=config,
            repo_root=ROOT,
            now=NOW,
        ),
        config,
    )


def test_prepare_binds_exact_stable_x_profile_without_external_resolution(tmp_path):
    packet, config = _packet(tmp_path)
    assert packet.profile_id == "last30days-x-primary"
    assert packet.plan.profile_ref == "profile:last30days-x-primary"
    assert packet.plan.max_attempts == packet.plan.external_concurrency == 1
    assert packet.plan.max_browser_actions == MAX_BROWSER_ACTIONS
    assert packet.plan.max_request_equivalents == MAX_REQUEST_EQUIVALENTS
    assert packet.plan.accounting_confidence == ACCOUNTING_CONFIDENCE
    target = verify_packet(
        packet,
        target_config_path=config,
        repo_root=ROOT,
        now=NOW + timedelta(minutes=1),
    )
    assert target["profile_id"] == packet.profile_id
    assert packet_from_dict(packet.to_dict()) == packet


@pytest.mark.parametrize(
    ("auth", "state", "reason"),
    [
        ((True, False, False, False), "READY", "authenticated"),
        ((False, True, False, False), "NOT_READY", "auth_required"),
        ((False, False, True, False), "NOT_READY", "checkpoint_required"),
        ((False, False, False, True), "NOT_READY", "restricted"),
        ((False, False, False, False), "NOT_READY", "auth_state_ambiguous"),
    ],
)
def test_one_attempt_preserves_each_safe_auth_outcome(tmp_path, auth, state, reason):
    packet, config = _packet(tmp_path)
    client = FakeClient(auth=auth)
    receipt = execute_x_readiness(
        packet,
        target_config_path=config,
        repo_root=ROOT,
        now=NOW + timedelta(minutes=1),
        client_factory=_factory(client),
    )
    assert receipt.state == state
    assert receipt.safe_reason_code == reason
    assert receipt.attempt_count == receipt.external_concurrency == 1
    assert receipt.teardown_completed
    assert not receipt.owned_handle_remaining
    assert client.calls.count("acquire_workspace") == 1
    assert client.calls.count("inspect_auth") == 1
    assert client.calls.count("release_workspace") == 1
    assert not any("search" in call for call in client.calls)
    assert verify_receipt(receipt, packet, repo_root=ROOT) == (True, ())
    assert receipt_from_dict(receipt.to_dict()) == receipt


def test_plan_and_grant_verify_before_client_factory_or_dependency_resolution(tmp_path):
    packet, config = _packet(tmp_path)
    forged = replace(packet, profile_id="forged")
    called = False

    def forbidden_factory(_fields):
        nonlocal called
        called = True
        raise AssertionError("dependency resolved before authority")

    with pytest.raises(ContractError, match="packet_digest_mismatch"):
        execute_x_readiness(
            forged,
            target_config_path=config,
            repo_root=ROOT,
            now=NOW + timedelta(minutes=1),
            client_factory=forbidden_factory,
        )
    assert not called


def test_target_binding_change_stops_before_client_factory(tmp_path):
    packet, config = _packet(tmp_path)
    _target_config(config, profile_id="last30days-x-other")
    with pytest.raises(ContractError, match="target_binding_mismatch"):
        execute_x_readiness(
            packet,
            target_config_path=config,
            repo_root=ROOT,
            now=NOW + timedelta(minutes=1),
            client_factory=lambda _fields: pytest.fail("must not resolve client"),
        )


def test_expired_grant_stops_before_client_factory(tmp_path):
    packet, config = _packet(tmp_path)
    with pytest.raises(ContractError, match="grant_expired"):
        execute_x_readiness(
            packet,
            target_config_path=config,
            repo_root=ROOT,
            now=NOW + timedelta(minutes=10),
            client_factory=lambda _fields: pytest.fail("must not resolve client"),
        )


def test_profile_mismatch_is_terminal_and_tears_down(tmp_path):
    packet, config = _packet(tmp_path)
    client = FakeClient(workspace_profile="wrong-profile")
    receipt = execute_x_readiness(
        packet,
        target_config_path=config,
        repo_root=ROOT,
        now=NOW + timedelta(minutes=1),
        client_factory=_factory(client),
    )
    assert receipt.state == "FAILED"
    assert receipt.safe_reason_code == "profile_mismatch"
    assert receipt.teardown_completed
    assert "inspect_auth" not in client.calls


def test_browser_action_budget_stops_without_retry_and_tears_down(tmp_path):
    packet, config = _packet(tmp_path)
    client = FakeClient(action_operations=("wait",) * (MAX_BROWSER_ACTIONS + 1))
    receipt = execute_x_readiness(
        packet,
        target_config_path=config,
        repo_root=ROOT,
        now=NOW + timedelta(minutes=1),
        client_factory=_factory(client),
    )
    assert receipt.state == "FAILED"
    assert receipt.safe_reason_code == "browser_action_budget_exhausted"
    assert receipt.browser_actions == MAX_BROWSER_ACTIONS
    assert client.calls.count("acquire_workspace") == 1
    assert client.calls.count("release_workspace") == 1


def test_auth_probe_cannot_consolidate_or_close_preexisting_x_tabs(tmp_path):
    packet, config = _packet(tmp_path)
    client = FakeClient()

    def inspecting_with_normal_consolidation(workspace):
        client.prepare_site_tab(workspace, "x.com", consolidate=True)
        return SimpleNamespace(
            authenticated=True,
            login_form=False,
            checkpoint=False,
            restricted=False,
        )

    client.inspect_auth = inspecting_with_normal_consolidation
    receipt = execute_x_readiness(
        packet,
        target_config_path=config,
        repo_root=ROOT,
        now=NOW + timedelta(minutes=1),
        client_factory=_factory(client),
    )
    assert receipt.state == "READY"
    assert client.prepare_consolidate_values == [False]


def test_request_equivalent_budget_stops_before_excess_action(tmp_path):
    packet, config = _packet(tmp_path)
    client = FakeClient(action_operations=("navigate",) * MAX_REQUEST_EQUIVALENTS)
    receipt = execute_x_readiness(
        packet,
        target_config_path=config,
        repo_root=ROOT,
        now=NOW + timedelta(minutes=1),
        client_factory=_factory(client),
    )
    assert receipt.state == "FAILED"
    assert receipt.safe_reason_code == "request_equivalent_budget_exhausted"
    assert receipt.request_equivalents == MAX_REQUEST_EQUIVALENTS
    assert client.calls.count("release_workspace") == 1


def test_acquisition_failure_retains_safe_code_and_never_retries(tmp_path):
    packet, config = _packet(tmp_path)
    failure = RuntimeError("private provider detail")
    failure.error_type = "agent_browser_timeout"
    client = FakeClient(acquire_fails=failure)
    receipt = execute_x_readiness(
        packet,
        target_config_path=config,
        repo_root=ROOT,
        now=NOW + timedelta(minutes=1),
        client_factory=_factory(client),
    )
    assert receipt.state == "FAILED"
    assert receipt.safe_reason_code == "agent_browser_timeout"
    assert "private provider detail" not in json.dumps(receipt.to_dict())
    assert client.calls.count("acquire_workspace") == 1
    assert client.calls.count("release_workspace") == 1


def test_dependency_failure_before_attempt_still_emits_safe_receipt(tmp_path):
    packet, config = _packet(tmp_path)

    def missing_dependency(_fields):
        raise ModuleNotFoundError("private module path")

    receipt = execute_x_readiness(
        packet,
        target_config_path=config,
        repo_root=ROOT,
        now=NOW + timedelta(minutes=1),
        client_factory=missing_dependency,
    )
    assert receipt.state == "FAILED"
    assert receipt.safe_reason_code == "agent_browser_missing"
    assert receipt.attempt_count == 0
    assert receipt.request_equivalents == 0
    assert receipt.teardown_completed
    assert "private module path" not in json.dumps(receipt.to_dict())
    assert verify_receipt(receipt, packet, repo_root=ROOT) == (True, ())


def test_teardown_failure_invalidates_ready_observation(tmp_path):
    packet, config = _packet(tmp_path)
    client = FakeClient(release_fails=True)
    receipt = execute_x_readiness(
        packet,
        target_config_path=config,
        repo_root=ROOT,
        now=NOW + timedelta(minutes=1),
        client_factory=_factory(client),
    )
    assert receipt.state == "FAILED"
    assert receipt.safe_reason_code == "teardown_incomplete"
    accepted, reasons = verify_receipt(receipt, packet, repo_root=ROOT)
    assert not accepted
    assert "teardown_incomplete" in reasons


def test_receipt_tampering_is_rejected_even_when_rehashed(tmp_path):
    packet, config = _packet(tmp_path)
    receipt = execute_x_readiness(
        packet,
        target_config_path=config,
        repo_root=ROOT,
        now=NOW + timedelta(minutes=1),
        client_factory=_factory(FakeClient()),
    )
    forged = receipt.to_dict()
    forged["profile_ref"] = "profile:other"
    forged["receipt_sha256"] = ""
    forged["receipt_sha256"] = _digest(forged)
    accepted, reasons = verify_receipt(
        P4ReadinessReceipt(**forged), packet, repo_root=ROOT
    )
    assert not accepted
    assert "receipt_binding_mismatch" in reasons


def test_receipt_decoder_and_semantics_reject_ambiguous_types_and_reason(tmp_path):
    packet, config = _packet(tmp_path)
    receipt = execute_x_readiness(
        packet,
        target_config_path=config,
        repo_root=ROOT,
        now=NOW + timedelta(minutes=1),
        client_factory=_factory(FakeClient(auth=(False, True, False, False))),
    )
    ambiguous = receipt.to_dict()
    ambiguous["attempt_count"] = True
    with pytest.raises(ContractError, match="type_mismatch"):
        receipt_from_dict(ambiguous)

    forged = receipt.to_dict()
    forged["safe_reason_code"] = "restricted"
    forged["receipt_sha256"] = ""
    forged["receipt_sha256"] = _digest(forged)
    accepted, reasons = verify_receipt(
        receipt_from_dict(forged), packet, repo_root=ROOT
    )
    assert not accepted
    assert "not_ready_reason_mismatch" in reasons


def test_missing_or_unsafe_profile_fails_closed(tmp_path):
    config = _target_config(tmp_path / "agent-browser.json", profile_id="default")
    with pytest.raises(ContractError):
        prepare_x_packet(target_config_path=config, repo_root=ROOT, now=NOW)

    config.write_text(
        json.dumps(
            {
                "schema_version": "last30days.agent-browser-targets.v1",
                "targets": {"facebook": {"profile_id": "last30days-facebook"}},
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(ContractError, match="binding_missing"):
        prepare_x_packet(target_config_path=config, repo_root=ROOT, now=NOW)


def test_cli_prepare_is_exclusive_and_provider_free(tmp_path, capsys):
    config = _target_config(tmp_path / "agent-browser.json")
    packet_path = tmp_path / "packet.json"
    assert (
        cli_main(
            [
                "prepare",
                "--target-config",
                str(config),
                "--output",
                str(packet_path),
            ]
        )
        == 0
    )
    assert json.loads(capsys.readouterr().out)["prepared"] is True
    initial = packet_path.read_bytes()
    with pytest.raises(SystemExit, match="output already exists"):
        cli_main(
            [
                "prepare",
                "--target-config",
                str(config),
                "--output",
                str(packet_path),
            ]
        )
    assert packet_path.read_bytes() == initial
