"""Contract tests for the Plan 0107 joined product acceptance driver."""

from __future__ import annotations

import importlib.util
import sqlite3
from pathlib import Path
from types import SimpleNamespace

import pytest

SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "dev/last30days/scripts/provider_free_productization_dogfood.py"
)


def _load():
    spec = importlib.util.spec_from_file_location(
        "provider_free_productization_dogfood", SCRIPT
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_parser_locks_the_campaign_identity(tmp_path):
    module = _load()
    common = [
        "--worktree",
        str(Path(__file__).resolve().parents[1]),
        "--state-root",
        str(tmp_path / "state"),
        "--runtime-root",
        str(tmp_path / "run"),
        "--artifact",
        str(tmp_path / "artifact.tar.gz"),
    ]

    args = module.build_parser().parse_args(common)
    assert args.work_item == "WI-000"
    assert args.plan == "0107"
    assert args.lane == "p52-provider-free-productization"

    with pytest.raises(SystemExit):
        module.build_parser().parse_args([*common, "--work-item", "WI-006"])


def test_run_composes_all_products_under_one_runtime_identity(tmp_path, monkeypatch):
    module = _load()
    artifact = tmp_path / "artifact.tar.gz"
    artifact.write_bytes(b"fixture")
    descriptor = SimpleNamespace(
        runtime_id="l30d-p52-fixture",
        state_root=str(tmp_path / "lane"),
        database_path=str(tmp_path / "lane" / "research.db"),
        socket_path=str(tmp_path / "run" / "service.sock"),
        commit="1" * 40,
        to_dict=lambda: {"runtime_id": "l30d-p52-fixture", "commit": "1" * 40},
    )
    args = module.build_parser().parse_args(
        [
            "--worktree",
            str(tmp_path),
            "--state-root",
            str(tmp_path / "state"),
            "--runtime-root",
            str(tmp_path / "run"),
            "--artifact",
            str(artifact),
        ]
    )
    monkeypatch.setattr(module, "ROOT", tmp_path)
    monkeypatch.setattr(
        module.lane_runtime, "_expected_descriptor", lambda _args: descriptor
    )
    monkeypatch.setattr(
        module.lane_runtime,
        "doctor",
        lambda **_kwargs: {
            "ok": True,
            "reasons": [],
            "descriptor": descriptor.to_dict(),
        },
    )
    monkeypatch.setattr(
        module,
        "verify_artifact",
        lambda _path: {"sha256": "a" * 64, "manifest_sha256": "b" * 64},
    )
    monkeypatch.setattr(module, "build_mcp", lambda _path: tmp_path / "mcp")
    seen = []

    def phase(_args, actual, _binary, name):
        Path(actual.state_root, "receipts").mkdir(parents=True, exist_ok=True)
        seen.append((name, actual.runtime_id))
        return {
            "name": name,
            "runtime_id": actual.runtime_id,
            "startup": {"state": "ready"},
            "status": {"state": "ready"},
            "down": {"state": "stopped"},
            "owned_processes": [],
            "result": {"state": "passed"},
        }

    monkeypatch.setattr(
        module,
        "PHASE_RUNNERS",
        (("search_question_quality", phase), ("follows", phase), ("monitors", phase)),
    )
    monkeypatch.setattr(
        module.lane_runtime,
        "status",
        lambda _args: {"state": "absent", "runtime_id": descriptor.runtime_id},
    )
    written = {}
    monkeypatch.setattr(
        module.lane_runtime,
        "_atomic_json",
        lambda path, value: written.update(path=path, value=value),
    )

    receipt_path, report = module.run(args)

    assert seen == [
        ("search_question_quality", descriptor.runtime_id),
        ("follows", descriptor.runtime_id),
        ("monitors", descriptor.runtime_id),
    ]
    assert report["state"] == "passed"
    assert report["provider_free"] is True
    assert report["runtime_id"] == descriptor.runtime_id
    assert report["final_controller_status"]["state"] == "absent"
    assert written["path"] == receipt_path
    assert written["value"] is report


def test_database_reset_is_confined_to_the_campaign_state_root(tmp_path):
    module = _load()
    state_root = tmp_path / "state"
    data_root = state_root / "data"
    data_root.mkdir(parents=True)
    database = data_root / "research.db"
    database.write_bytes(b"fixture")
    Path(str(database) + "-wal").write_bytes(b"wal")
    descriptor = SimpleNamespace(
        state_root=str(state_root), database_path=str(database)
    )

    module._reset_database(descriptor)

    assert not database.exists()
    assert not Path(str(database) + "-wal").exists()

    foreign = state_root / "foreign.db"
    foreign.write_bytes(b"preserve")
    descriptor.database_path = str(foreign)
    with pytest.raises(ValueError, match="database_outside_campaign_state"):
        module._reset_database(descriptor)
    assert foreign.read_bytes() == b"preserve"


def test_question_probe_precedes_search_publication(monkeypatch):
    module = _load()
    order = []
    anchor = {"status": {"question_id": "question-1"}}
    monkeypatch.setattr(
        module.question_dogfood,
        "check_questions",
        lambda *_args: (order.append("questions") or {"state": "passed"}, anchor),
    )
    monkeypatch.setattr(
        module.post_search_dogfood,
        "check_search",
        lambda *_args: (order.append("search") or {"state": "passed"}, {}),
    )

    result, actual_anchor = module._check_search_question_quality(
        object(), object(), Path("fixture.sqlite")
    )

    assert order == ["questions", "search"]
    assert result == {
        "search": {"state": "passed"},
        "questions": {"state": "passed"},
    }
    assert actual_anchor is anchor


def test_sealing_does_not_change_journal_mode_while_a_reader_is_open(tmp_path):
    module = _load()
    database = tmp_path / "fixture.sqlite"
    with sqlite3.connect(database) as writer:
        writer.execute("PRAGMA journal_mode=WAL")
        writer.execute("CREATE TABLE evidence (id INTEGER PRIMARY KEY)")
        writer.execute("INSERT INTO evidence VALUES (1)")
    with sqlite3.connect(database) as reader:
        reader.execute("BEGIN")
        assert reader.execute("SELECT count(*) FROM evidence").fetchone() == (1,)
        module._seal_database(database)
        assert reader.execute("PRAGMA journal_mode").fetchone() == ("wal",)
