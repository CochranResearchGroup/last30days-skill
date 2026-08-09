"""Deterministic roadmap, runbook, and active-goal authority audit."""

from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDITOR_PATH = ROOT / "dev" / "last30days" / "scripts" / "audit_plan_authority.py"


def _load_auditor():
    spec = importlib.util.spec_from_file_location("audit_plan_authority", AUDITOR_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write_minimal_authority(root: Path, *, checkpoint_extra: str = "") -> None:
    plan_path = (
        root
        / "docs"
        / "dev"
        / "plans"
        / "0011-2026-07-25-integrated-temporal-intelligence-service.md"
    )
    plan_path.parent.mkdir(parents=True)
    plan_path.write_text(
        f"""# Plan 0011 | Integrated temporal intelligence service

State: OPEN
Roadmap: P01

## Execution State

Plan version: 1
Critical-path owner: primary agent

Local goal bounds:

- maximum implementation attempts per packet: 2;
- maximum review/rework cycles per packet: 1;
- maximum consecutive hardening-only checkpoints: 2;
- checkpoint after every validated packet.

## Objective

Execute the integrated P01-P06 service.

## Authority Correction

Plan 0010 is a component contract plan for P06.
This plan activates Plan 0010 only at four explicit joins.

## Current State

Packet 6 is active.

## Packets

Packets 1 through 7.

## Integrated Acceptance Criteria

Current evidence is required.

### Checkpoint P0011-C01 | 2026-07-25

Plan version: 1

State transition: `ready -> active`

Progress classification: `outcome_progress`

Authority classification:

- `inherited_authority`.

Owned changes:

- created the authority.

Validation evidence:

- deterministic audit fixture.

Subagent status and reconciliation:

- `not_spawned`.

Remaining acceptance criteria:

- integrated closeout.

Graphiti write status:

- deferred in the fixture.

Next action:

- continue.
{checkpoint_extra}

## Stop Rules

Stop at a human gate.
""",
        encoding="utf-8",
    )
    (root / "ROADMAP.md").write_text(
        """# Roadmap

Authority: this file is the canonical product direction, priority map, and lane catalog.

## P01 | Temporal Corpus Foundation

State: OPEN

Objective: preserve immutable temporal evidence.

Current State:

- Packet 6 is active.

Active Plan:

- `docs/dev/plans/0011-2026-07-25-integrated-temporal-intelligence-service.md`
  is the integrated P01-P06 campaign authority.
""",
        encoding="utf-8",
    )
    (root / "RUNBOOK.md").write_text(
        """# Runbook

Plan 0011 authority:
`docs/dev/plans/0011-2026-07-25-integrated-temporal-intelligence-service.md`

## Turn 1 | 2026-07-25

Authority Consulted:

- Plan 0011.

Decisions And Changes:

- established the fixture.

Validation Evidence:

- fixture created.

State Movement:

- `ready -> active`.

Subagent Status And Reconciliation:

- `not_spawned`.

Graphiti Write Status:

- deferred.

Next Bounded Action:

- continue.
""",
        encoding="utf-8",
    )


def test_current_repository_authority_passes() -> None:
    auditor = _load_auditor()

    report = auditor.audit_repository(ROOT)

    assert report["status"] == "passed", report
    assert report["issues"] == []
    assert report["active_plan_count"] == 1
    assert report["active_plans"] == [
        "docs/dev/plans/0036-2026-08-09-facebook-tab-inventory-latency-repair.md"
    ]
    assert report["campaign_plan_count"] == 0


def test_closed_campaign_allows_zero_active_campaigns(tmp_path: Path) -> None:
    auditor = _load_auditor()
    _write_minimal_authority(tmp_path)
    roadmap = tmp_path / "ROADMAP.md"
    roadmap.write_text(
        roadmap.read_text(encoding="utf-8").replace("State: OPEN", "State: PLANNED"),
        encoding="utf-8",
    )
    plan = next((tmp_path / "docs" / "dev" / "plans").glob("0011-*.md"))
    plan.write_text(
        plan.read_text(encoding="utf-8").replace("State: OPEN", "State: CLOSED"),
        encoding="utf-8",
    )

    report = auditor.audit_repository(tmp_path)

    assert report["status"] == "passed", report
    assert report["active_plan_count"] == 0
    assert report["campaign_plan_count"] == 0


def test_open_lane_requires_current_state_and_plan(tmp_path: Path) -> None:
    auditor = _load_auditor()
    _write_minimal_authority(tmp_path)
    roadmap = tmp_path / "ROADMAP.md"
    roadmap.write_text(
        roadmap.read_text(encoding="utf-8").replace("Current State:", "Progress:"),
        encoding="utf-8",
    )

    report = auditor.audit_repository(tmp_path)

    assert report["status"] == "failed"
    assert "ROADMAP P01 OPEN lane is missing Current State" in report["issues"]


def test_latest_checkpoint_requires_graphiti_and_subagent_fields(tmp_path: Path) -> None:
    auditor = _load_auditor()
    _write_minimal_authority(tmp_path)
    plan = next((tmp_path / "docs" / "dev" / "plans").glob("0011-*.md"))
    text = plan.read_text(encoding="utf-8")
    text = text.replace(
        "Subagent status and reconciliation:\n\n- `not_spawned`.\n\n", ""
    ).replace("Graphiti write status:\n\n- deferred in the fixture.\n\n", "")
    plan.write_text(text, encoding="utf-8")

    report = auditor.audit_repository(tmp_path)

    assert report["status"] == "failed"
    assert any("Subagent status" in issue for issue in report["issues"])
    assert any("Graphiti write status" in issue for issue in report["issues"])


def test_latest_checkpoint_requires_authority_classification(tmp_path: Path) -> None:
    auditor = _load_auditor()
    _write_minimal_authority(tmp_path)
    plan = next((tmp_path / "docs" / "dev" / "plans").glob("0011-*.md"))
    text = plan.read_text(encoding="utf-8")
    text = text.replace(
        "Authority classification:\n\n- `inherited_authority`.\n\n",
        "",
    )
    plan.write_text(text, encoding="utf-8")

    report = auditor.audit_repository(tmp_path)

    assert report["status"] == "failed"
    assert any("Authority classification" in issue for issue in report["issues"])


def test_latest_checkpoint_rejects_unknown_authority_classification(
    tmp_path: Path,
) -> None:
    auditor = _load_auditor()
    _write_minimal_authority(tmp_path)
    plan = next((tmp_path / "docs" / "dev" / "plans").glob("0011-*.md"))
    text = plan.read_text(encoding="utf-8")
    text = text.replace("`inherited_authority`", "`ask_again_just_in_case`")
    plan.write_text(text, encoding="utf-8")

    report = auditor.audit_repository(tmp_path)

    assert report["status"] == "failed"
    assert any("invalid Authority classification" in issue for issue in report["issues"])


def test_declared_plan_version_must_match_latest_checkpoint(tmp_path: Path) -> None:
    auditor = _load_auditor()
    _write_minimal_authority(tmp_path)
    plan = next((tmp_path / "docs" / "dev" / "plans").glob("0011-*.md"))
    text = plan.read_text(encoding="utf-8")
    text = text.replace("Plan version: 1\n", "Plan version: 7\n", 1)
    plan.write_text(text, encoding="utf-8")

    report = auditor.audit_repository(tmp_path)

    assert report["status"] == "failed"
    assert any("declares plan version 7" in issue for issue in report["issues"])
    assert any("latest checkpoint P0011-C01 declares 1" in issue for issue in report["issues"])


def test_current_authority_declaration_must_name_latest_checkpoint(
    tmp_path: Path,
) -> None:
    auditor = _load_auditor()
    _write_minimal_authority(tmp_path)
    plan = next((tmp_path / "docs" / "dev" / "plans").glob("0011-*.md"))
    text = plan.read_text(encoding="utf-8")
    text = text.replace(
        "Packet 6 is active.\n",
        "Checkpoint P0011-C00 is the current authority.\n",
        1,
    )
    plan.write_text(text, encoding="utf-8")

    report = auditor.audit_repository(tmp_path)

    assert report["status"] == "failed"
    assert any("declares checkpoint P0011-C00 as current" in issue for issue in report["issues"])
    assert any("latest checkpoint is P0011-C01" in issue for issue in report["issues"])
