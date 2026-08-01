#!/usr/bin/env python3
"""Audit canonical roadmap, runbook, and active-goal authority."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


ALLOWED_LANE_STATES = frozenset({"PLANNED", "OPEN", "CLOSED", "CANCELLED"})
ALLOWED_AUTHORITY_CLASSIFICATIONS = frozenset(
    {"inherited_authority", "human_gate", "scope_expansion"}
)
PLAN_PATH_PATTERN = re.compile(r"`(docs/dev/plans/[^`]+\.md)`")
LANE_PATTERN = re.compile(r"^## (P\d{2}) \| (.+)$", re.MULTILINE)
TURN_PATTERN = re.compile(r"^## Turn (\d+) \| (\d{4}-\d{2}-\d{2})$", re.MULTILINE)
CHECKPOINT_PATTERN = re.compile(
    r"^### Checkpoint ([A-Za-z0-9-]+) \| (\d{4}-\d{2}-\d{2})$",
    re.MULTILINE,
)
PLAN_VERSION_PATTERN = re.compile(
    r"^Plan version:[ \t]*(\d+)[ \t]*$",
    re.MULTILINE,
)
CHECKPOINT_VERSION_PATTERN = re.compile(
    r"^Plan version:[ \t]*(?:([0-9]+)[ \t]*$|"
    r"\n(?:[ \t]*\n)?[ \t]*-[ \t]*([0-9]+)[ \t]*$)",
    re.MULTILINE,
)
CURRENT_AUTHORITY_PATTERN = re.compile(
    r"Checkpoint ([A-Za-z0-9-]+) is the current authority",
)


def _body_until_next(text: str, start: int, pattern: re.Pattern[str]) -> str:
    match = pattern.search(text, start)
    return text[start : match.start() if match else len(text)]


def _has_label(text: str, label: str) -> bool:
    return re.search(rf"^{re.escape(label)}\s*$", text, re.MULTILINE | re.IGNORECASE) is not None


def _audit_roadmap(root: Path, issues: list[str]) -> tuple[str, ...]:
    path = root / "ROADMAP.md"
    if not path.is_file():
        issues.append("ROADMAP.md is missing")
        return ()
    text = path.read_text(encoding="utf-8")
    if "canonical product direction, priority map" not in text:
        issues.append("ROADMAP.md is missing its canonical-authority declaration")

    active_plans: set[str] = set()
    lanes = list(LANE_PATTERN.finditer(text))
    if not lanes:
        issues.append("ROADMAP.md has no P## lanes")
    for index, match in enumerate(lanes):
        lane_id = match.group(1)
        end = lanes[index + 1].start() if index + 1 < len(lanes) else len(text)
        body = text[match.end() : end]
        state_match = re.search(r"^State:\s+(\S+)\s*$", body, re.MULTILINE)
        if state_match is None:
            issues.append(f"ROADMAP {lane_id} lane is missing State")
            continue
        state = state_match.group(1)
        if state not in ALLOWED_LANE_STATES:
            issues.append(f"ROADMAP {lane_id} has invalid state {state!r}")
        if not _has_label(body, "Objective:") and not re.search(
            r"^Objective:\s+\S", body, re.MULTILINE
        ):
            issues.append(f"ROADMAP {lane_id} lane is missing Objective")
        if state != "OPEN":
            continue
        if not _has_label(body, "Current State:"):
            issues.append(f"ROADMAP {lane_id} OPEN lane is missing Current State")
        plan_paths = PLAN_PATH_PATTERN.findall(body)
        actionable: list[str] = []
        for plan_path in plan_paths:
            candidate = root / plan_path
            if not candidate.is_file():
                continue
            candidate_state = re.search(
                r"^State:\s+(\S+)\s*$",
                candidate.read_text(encoding="utf-8"),
                re.MULTILINE,
            )
            if candidate_state is not None and candidate_state.group(1) == "OPEN":
                actionable.append(plan_path)
        if not actionable:
            issues.append(f"ROADMAP {lane_id} OPEN lane has no actionable plan")
        active_plans.update(actionable)
    return tuple(sorted(active_plans))


def _audit_active_plan(
    root: Path,
    plan_path: str,
    roadmap_text: str,
    runbook_text: str,
    issues: list[str],
) -> None:
    path = root / plan_path
    if not path.is_file():
        issues.append(f"active plan does not exist: {plan_path}")
        return
    text = path.read_text(encoding="utf-8")
    state = re.search(r"^State:\s+(\S+)\s*$", text, re.MULTILINE)
    if state is None or state.group(1) != "OPEN":
        issues.append(f"active plan {plan_path} must have State: OPEN")
    checkpoints = list(CHECKPOINT_PATTERN.finditer(text))
    if not checkpoints:
        issues.append(f"active plan {plan_path} has no durable checkpoint")
        latest = None
        latest_body = ""
    else:
        latest = checkpoints[-1]
        latest_body = _body_until_next(
            text,
            latest.end(),
            re.compile(r"^### |^## ", re.MULTILINE),
        )
        authority_match = re.search(
            r"^Authority classification:\s*(?:\n\s*)+-\s+`([^`]+)`",
            latest_body,
            re.MULTILINE,
        )
        if authority_match is None:
            issues.append(
                f"latest checkpoint {latest.group(1)} is missing "
                "Authority classification"
            )
        elif authority_match.group(1) not in ALLOWED_AUTHORITY_CLASSIFICATIONS:
            issues.append(
                f"latest checkpoint {latest.group(1)} has invalid "
                f"Authority classification {authority_match.group(1)!r}"
            )
        declared_version = PLAN_VERSION_PATTERN.search(text)
        checkpoint_version = CHECKPOINT_VERSION_PATTERN.search(latest_body)
        if checkpoint_version is None:
            issues.append(
                f"latest checkpoint {latest.group(1)} has no parseable plan version"
            )
        elif declared_version is not None:
            latest_version = (
                checkpoint_version.group(1) or checkpoint_version.group(2)
            )
            if declared_version.group(1) != latest_version:
                issues.append(
                    f"active plan {plan_path} declares plan version "
                    f"{declared_version.group(1)}, but latest checkpoint "
                    f"{latest.group(1)} declares {latest_version}"
                )
        authority_declarations = list(CURRENT_AUTHORITY_PATTERN.finditer(text))
        if authority_declarations:
            declared_checkpoint = authority_declarations[-1].group(1)
            if declared_checkpoint != latest.group(1):
                issues.append(
                    f"active plan {plan_path} declares checkpoint "
                    f"{declared_checkpoint} as current, but latest checkpoint is "
                    f"{latest.group(1)}"
                )
    is_campaign = "## Authority Correction" in text and "four explicit joins" in text
    if not is_campaign:
        if not ("## Scope" in text or "## Objective" in text):
            issues.append(f"active plan {plan_path} is missing Scope or Objective")
        for heading in ("## Current State", "## Non-Goals", "## Definition Of Done"):
            if heading not in text:
                issues.append(f"active plan {plan_path} is missing {heading}")
        if plan_path not in roadmap_text:
            issues.append(f"active plan is not wired into ROADMAP.md: {plan_path}")
        serial_match = re.match(r"(\d{4})-", Path(plan_path).name)
        serial_label = f"Plan {serial_match.group(1)}" if serial_match else plan_path
        if plan_path not in runbook_text and serial_label not in runbook_text:
            issues.append(f"active plan is not wired into RUNBOOK.md: {plan_path}")
        return
    for heading in (
        "## Execution State",
        "## Objective",
        "## Authority Correction",
        "## Current State",
        "## Packets",
        "## Integrated Acceptance Criteria",
        "## Stop Rules",
    ):
        if heading not in text:
            issues.append(f"active plan {plan_path} is missing {heading}")
    for bound in (
        "maximum implementation attempts per packet",
        "maximum review/rework cycles per packet",
        "maximum consecutive hardening-only checkpoints",
        "checkpoint after every validated packet",
    ):
        if bound not in text:
            issues.append(f"active plan {plan_path} is missing goal bound: {bound}")
    if "Plan 0010 is a component contract plan for P06" not in text:
        issues.append(f"active plan {plan_path} does not subordinate Plan 0010")
    if "four explicit joins" not in text:
        issues.append(f"active plan {plan_path} does not define the four Plan 0010 joins")
    if plan_path not in roadmap_text:
        issues.append(f"active plan is not wired into ROADMAP.md: {plan_path}")
    if plan_path not in runbook_text:
        issues.append(f"active plan is not wired into RUNBOOK.md: {plan_path}")

    if latest is None:
        return
    body = latest_body
    required_labels = (
        "Plan version:",
        "State transition:",
        "Progress classification:",
        "Owned changes:",
        "Validation evidence:",
        "Subagent status and reconciliation:",
        "Graphiti write status:",
        "Next action:",
    )
    for label in required_labels:
        if not _has_label(body, label) and not re.search(
            rf"^{re.escape(label)}\s+\S", body, re.MULTILINE | re.IGNORECASE
        ):
            issues.append(
                f"latest checkpoint {latest.group(1)} is missing {label.rstrip(':')}"
            )
    if not (
        _has_label(body, "Remaining acceptance criteria:")
        or _has_label(body, "Stop rule:")
    ):
        issues.append(
            f"latest checkpoint {latest.group(1)} is missing remaining criteria or stop rule"
        )


def _audit_runbook(
    text: str,
    issues: list[str],
) -> int:
    turns = list(TURN_PATTERN.finditer(text))
    if not turns:
        issues.append("RUNBOOK.md has no Turn N entries")
        return 0
    numbers = [int(match.group(1)) for match in turns]
    if numbers != sorted(set(numbers)):
        issues.append("RUNBOOK.md turn numbers are not unique and ascending")
    latest = turns[-1]
    body = text[latest.end() :]
    required_labels = (
        "Authority Consulted:",
        "Decisions And Changes:",
        "Validation Evidence:",
        "State Movement:",
        "Subagent Status And Reconciliation:",
        "Graphiti Write Status:",
    )
    for label in required_labels:
        if not _has_label(body, label):
            issues.append(f"latest runbook Turn {latest.group(1)} is missing {label.rstrip(':')}")
    if not (
        _has_label(body, "Next Bounded Action:")
        or _has_label(body, "Stop Reason:")
        or _has_label(body, "Live Outcome And Stop:")
    ):
        issues.append(
            f"latest runbook Turn {latest.group(1)} is missing next action or stop reason"
        )
    return int(latest.group(1))


def audit_repository(root: Path) -> dict[str, Any]:
    root = Path(root).resolve()
    issues: list[str] = []
    active_plans = _audit_roadmap(root, issues)
    roadmap_path = root / "ROADMAP.md"
    runbook_path = root / "RUNBOOK.md"
    roadmap_text = (
        roadmap_path.read_text(encoding="utf-8") if roadmap_path.is_file() else ""
    )
    runbook_text = (
        runbook_path.read_text(encoding="utf-8") if runbook_path.is_file() else ""
    )
    latest_turn = _audit_runbook(runbook_text, issues) if runbook_text else 0
    campaign_plan_count = 0
    for plan_path in active_plans:
        plan_text = (root / plan_path).read_text(encoding="utf-8")
        if "## Authority Correction" in plan_text and "four explicit joins" in plan_text:
            campaign_plan_count += 1
        _audit_active_plan(
            root,
            plan_path,
            roadmap_text,
            runbook_text,
            issues,
        )
    if campaign_plan_count > 1:
        issues.append(
            "expected at most one integrated campaign authority, "
            f"found {campaign_plan_count}"
        )
    return {
        "schema_version": 1,
        "status": "passed" if not issues else "failed",
        "root": str(root),
        "active_plan_count": len(active_plans),
        "campaign_plan_count": campaign_plan_count,
        "active_plans": list(active_plans),
        "latest_runbook_turn": latest_turn,
        "issue_count": len(issues),
        "issues": issues,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Audit roadmap, runbook, and active goal-plan authority"
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[3],
        help="Repository root (defaults to this script's repository)",
    )
    return parser


def main() -> int:
    report = audit_repository(build_parser().parse_args().root)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
