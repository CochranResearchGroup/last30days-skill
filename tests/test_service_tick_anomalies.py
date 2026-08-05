"""Deterministic anomaly baselines and terminal decisions."""

from lib.service_tick_anomalies import AnomalyRule, evaluate_anomaly


def test_low_direction_rule_learns_then_uses_a_deterministic_median_baseline():
    rule = AnomalyRule(
        rule_id="yield-collapse",
        metric="yield_count",
        direction="low",
        minimum_comparable_ticks=3,
        warning_ratio=0.8,
        critical_ratio=0.5,
    )

    learning = evaluate_anomaly(rule, current_value=1.0, history=(10.0, 10.0))
    critical = evaluate_anomaly(
        rule,
        current_value=1.0,
        history=(9.0, 10.0, 11.0),
    )
    healthy = evaluate_anomaly(
        rule,
        current_value=9.0,
        history=(9.0, 10.0, 11.0),
    )

    assert learning.state == "learning_baseline"
    assert learning.baseline_value is None
    assert critical.state == "critical"
    assert critical.baseline_value == 10.0
    assert critical.ratio == 0.1
    assert healthy.state == "healthy"


def test_high_direction_rule_rejects_invalid_threshold_order():
    try:
        AnomalyRule(
            rule_id="latency-growth",
            metric="latency_seconds",
            direction="high",
            minimum_comparable_ticks=2,
            warning_ratio=2.0,
            critical_ratio=1.5,
        )
    except ValueError as exc:
        assert "critical_ratio" in str(exc)
    else:
        raise AssertionError("invalid high-direction thresholds were accepted")


def test_high_direction_rule_detects_a_spike_from_a_stable_zero_baseline():
    rule = AnomalyRule(
        rule_id="rejection-spike",
        metric="rejection_rate",
        direction="high",
        minimum_comparable_ticks=2,
        warning_ratio=2.0,
        critical_ratio=4.0,
    )

    healthy = evaluate_anomaly(rule, current_value=0.0, history=(0.0, 0.0))
    critical = evaluate_anomaly(rule, current_value=0.25, history=(0.0, 0.0))

    assert healthy.state == "healthy"
    assert healthy.baseline_value == 0.0
    assert healthy.ratio == 1.0
    assert critical.state == "critical"
    assert critical.baseline_value == 0.0
    assert critical.ratio is None
