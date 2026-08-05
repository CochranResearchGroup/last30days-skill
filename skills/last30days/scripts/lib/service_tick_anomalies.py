"""Deterministic statistical baselines for durable tick incident rules."""

from __future__ import annotations

import hashlib
import json
import sqlite3
import statistics
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import store


Clock = Callable[[], datetime]
_METRICS = frozenset(
    {"yield_count", "rejection_rate", "latency_seconds", "missing_media_rate"}
)


def _canonical_json(value: object) -> str:
    return json.dumps(value, allow_nan=False, separators=(",", ":"), sort_keys=True)


def _digest(value: object) -> str:
    return "sha256:" + hashlib.sha256(_canonical_json(value).encode()).hexdigest()


def _stable_id(prefix: str, value: object) -> str:
    return f"{prefix}-{hashlib.sha256(_canonical_json(value).encode()).hexdigest()[:32]}"


def _now(clock: Clock) -> str:
    value = clock()
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("clock must return a timezone-aware datetime")
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class AnomalyRule:
    rule_id: str
    metric: str
    direction: str
    minimum_comparable_ticks: int
    warning_ratio: float
    critical_ratio: float

    def __post_init__(self) -> None:
        if (
            not isinstance(self.rule_id, str)
            or not self.rule_id.strip()
            or len(self.rule_id) > 48
        ):
            raise ValueError("rule_id must be a bounded non-empty string")
        if self.metric not in _METRICS:
            raise ValueError("anomaly metric is unsupported")
        if self.direction not in {"low", "high"}:
            raise ValueError("anomaly direction is unsupported")
        if (
            isinstance(self.minimum_comparable_ticks, bool)
            or not isinstance(self.minimum_comparable_ticks, int)
            or not 2 <= self.minimum_comparable_ticks <= 1_000
        ):
            raise ValueError("minimum_comparable_ticks must be between 2 and 1000")
        for field in ("warning_ratio", "critical_ratio"):
            value = getattr(self, field)
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or value <= 0
            ):
                raise ValueError(f"{field} must be a positive number")
        if self.direction == "low" and self.critical_ratio > self.warning_ratio:
            raise ValueError("critical_ratio must not exceed warning_ratio for low rules")
        if self.direction == "high" and self.critical_ratio < self.warning_ratio:
            raise ValueError("critical_ratio must not be below warning_ratio for high rules")

    @classmethod
    def from_dict(cls, value: Mapping[str, object]) -> AnomalyRule:
        return cls(
            rule_id=value["rule_id"],
            metric=value["metric"],
            direction=value["direction"],
            minimum_comparable_ticks=value["minimum_comparable_ticks"],
            warning_ratio=value["warning_ratio"],
            critical_ratio=value["critical_ratio"],
        )


@dataclass(frozen=True)
class AnomalyResult:
    result_id: str
    rule_id: str
    metric: str
    state: str
    current_value: float
    baseline_value: float | None
    ratio: float | None
    sample_count: int


def evaluate_anomaly(
    rule: AnomalyRule,
    *,
    current_value: float,
    history: Sequence[float],
) -> AnomalyResult:
    current = float(current_value)
    samples = tuple(float(value) for value in history)
    if len(samples) < rule.minimum_comparable_ticks:
        state = "learning_baseline"
        baseline = None
        ratio = None
    else:
        baseline = float(statistics.median(samples))
        if baseline <= 0:
            if rule.direction == "high":
                state = "healthy" if current <= 0 else "critical"
                ratio = 1.0 if current <= 0 else None
            else:
                state = "learning_baseline"
                baseline = None
                ratio = None
        else:
            ratio = current / baseline
            if rule.direction == "low":
                state = (
                    "critical"
                    if ratio <= rule.critical_ratio
                    else "warning" if ratio <= rule.warning_ratio else "healthy"
                )
            else:
                state = (
                    "critical"
                    if ratio >= rule.critical_ratio
                    else "warning" if ratio >= rule.warning_ratio else "healthy"
                )
    identity = {
        "rule_id": rule.rule_id,
        "current": current,
        "history": samples,
    }
    return AnomalyResult(
        result_id=_stable_id("anomaly-evaluation", identity),
        rule_id=rule.rule_id,
        metric=rule.metric,
        state=state,
        current_value=current,
        baseline_value=baseline,
        ratio=ratio,
        sample_count=len(samples),
    )


class AnomalyMonitor:
    def __init__(self, db_path: Path, *, clock: Clock | None = None) -> None:
        self.db_path = Path(db_path)
        self.clock = clock or (lambda: datetime.now(timezone.utc))
        store.init_db(self.db_path)

    def record(
        self,
        *,
        tick_id: str,
        lane_id: str,
        source: str,
        profile_ref: str,
        rule: AnomalyRule,
        current_value: float,
    ) -> AnomalyResult:
        conn = sqlite3.connect(str(self.db_path), timeout=5)
        conn.row_factory = sqlite3.Row
        try:
            history = tuple(
                float(row[0])
                for row in conn.execute(
                    """SELECT current_value FROM service_tick_anomaly_results
                       WHERE source = ? AND profile_ref = ? AND rule_id = ?
                         AND tick_id <> ? ORDER BY created_at, result_id""",
                    (source, profile_ref, rule.rule_id, tick_id),
                ).fetchall()
            )
            evaluated = evaluate_anomaly(
                rule,
                current_value=current_value,
                history=history,
            )
            payload = {
                "tick_id": tick_id,
                "lane_id": lane_id,
                "source": source,
                "profile_ref": profile_ref,
                "rule": rule.__dict__,
                "state": evaluated.state,
                "current_value": evaluated.current_value,
                "baseline_value": evaluated.baseline_value,
                "ratio": evaluated.ratio,
                "sample_count": evaluated.sample_count,
            }
            result_id = _stable_id(
                "tick-anomaly",
                {
                    "tick_id": tick_id,
                    "lane_id": lane_id,
                    "rule_id": rule.rule_id,
                },
            )
            conn.execute(
                """INSERT OR IGNORE INTO service_tick_anomaly_results (
                       result_id, tick_id, lane_id, source, profile_ref, rule_id,
                       metric, direction, state, current_value, baseline_value,
                       ratio, sample_count, result_digest, created_at
                   ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    result_id,
                    tick_id,
                    lane_id,
                    source,
                    profile_ref,
                    rule.rule_id,
                    rule.metric,
                    rule.direction,
                    evaluated.state,
                    evaluated.current_value,
                    evaluated.baseline_value,
                    evaluated.ratio,
                    evaluated.sample_count,
                    _digest(payload),
                    _now(self.clock),
                ),
            )
            row = conn.execute(
                "SELECT result_digest FROM service_tick_anomaly_results WHERE result_id = ?",
                (result_id,),
            ).fetchone()
            if row["result_digest"] != _digest(payload):
                raise ValueError("immutable anomaly result conflict")
            conn.commit()
            return AnomalyResult(
                result_id=result_id,
                rule_id=evaluated.rule_id,
                metric=evaluated.metric,
                state=evaluated.state,
                current_value=evaluated.current_value,
                baseline_value=evaluated.baseline_value,
                ratio=evaluated.ratio,
                sample_count=evaluated.sample_count,
            )
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
