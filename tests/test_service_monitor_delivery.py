"""Disabled production delivery and injectable recording-sink idempotency."""

import pytest
from lib.service_monitor_delivery import RecordingSink
from lib.service_monitors import MonitorKernelError

from tests.test_service_monitor_application import command, composition, create


def test_intents_never_send_by_default_and_recording_retry_resend_is_exact(tmp_path):
    app, _, ref = composition(tmp_path)
    create(app, ref)
    command(app, "activate", monitor_id="monitor-fixture")
    snap = command(app, "capture", monitor_id="monitor-fixture", capture_id="delivery")
    result = command(
        app, "evaluate", monitor_id="monitor-fixture", snapshot_id=snap["snapshot_id"]
    )
    preference = command(
        app,
        "set_delivery",
        monitor_id="monitor-fixture",
        expected_version=0,
        channel_config_ref="fixture-sink-v1",
    )
    assert preference["mode"] == "disabled"
    command(app, "accept", run_id=result["run"]["run_id"])
    intent = command(
        app, "prepare_delivery", run_id=result["run"]["run_id"], preference_version=1
    )
    assert (
        command(
            app,
            "prepare_delivery",
            run_id=result["run"]["run_id"],
            preference_version=1,
        )
        == intent
    )
    with pytest.raises(MonitorKernelError, match="delivery disabled"):
        command(app, "send", intent_id=intent["intent_id"])
    sink = RecordingSink(failures=1)
    failed = app.delivery.dispatch(intent["intent_id"], "profile:x-primary", sink=sink)
    assert failed["status"] == "failed"
    success = app.delivery.dispatch(intent["intent_id"], "profile:x-primary", sink=sink)
    assert success["status"] == "sent"
    assert (
        app.delivery.dispatch(intent["intent_id"], "profile:x-primary", sink=sink)
        == success
    )
    assert len(sink.effects) == 1
    child = command(
        app,
        "resend",
        intent_id=intent["intent_id"],
        reason="Explicit fixture resend",
        request_id="resend-1",
    )
    assert child["parent_intent_id"] == intent["intent_id"]
    assert child["parent_receipt_id"] == success["receipt_id"]
    assert child == command(
        app,
        "resend",
        intent_id=intent["intent_id"],
        reason="Explicit fixture resend",
        request_id="resend-1",
    )
    app.delivery.dispatch(child["intent_id"], "profile:x-primary", sink=sink)
    assert len(sink.effects) == 2


def test_ambiguous_recording_effect_never_automatically_retries(tmp_path):
    app, _, ref = composition(tmp_path)
    create(app, ref)
    command(app, "activate", monitor_id="monitor-fixture")
    snap = command(app, "capture", monitor_id="monitor-fixture", capture_id="ambiguous")
    result = command(
        app, "evaluate", monitor_id="monitor-fixture", snapshot_id=snap["snapshot_id"]
    )
    command(app, "accept", run_id=result["run"]["run_id"])
    command(
        app,
        "set_delivery",
        monitor_id="monitor-fixture",
        expected_version=0,
        channel_config_ref="fixture",
    )
    intent = command(
        app, "prepare_delivery", run_id=result["run"]["run_id"], preference_version=1
    )
    sink = RecordingSink()

    def lost_receipt(key, digest):
        sink.effects[key] = digest
        raise RuntimeError("simulated lost receipt")

    sink.send = lost_receipt
    with pytest.raises(RuntimeError):
        app.delivery.dispatch(intent["intent_id"], "profile:x-primary", sink=sink)
    with pytest.raises(MonitorKernelError, match="ambiguous"):
        app.delivery.dispatch(
            intent["intent_id"], "profile:x-primary", sink=RecordingSink()
        )
