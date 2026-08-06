"""Subprocess lifecycle and no-network proof for the local service."""

import json
import os
import stat
import sqlite3
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import store

from lib import service_contracts as contracts
from lib.service_client import ServiceClient, ServiceClientError
from service import build_parser


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "last30days" / "scripts"
SERVICE = SCRIPTS / "service.py"


def _wait_ready(client: ServiceClient, process: subprocess.Popen, timeout=8):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if process.poll() is not None:
            stdout, stderr = process.communicate()
            raise AssertionError(
                f"service exited before readiness: {process.returncode}\n"
                f"stdout={stdout}\nstderr={stderr}"
            )
        try:
            return client.service_info()
        except ServiceClientError:
            time.sleep(0.05)
    raise AssertionError("service did not become ready")


def test_service_subprocess_drains_cleanly_and_warm_path_has_no_network(tmp_path):
    runtime_dir = tmp_path / "runtime"
    data_dir = tmp_path / "data"
    canary_dir = tmp_path / "canary"
    canary_dir.mkdir()
    violation_path = tmp_path / "network-violation"
    (canary_dir / "sitecustomize.py").write_text(
        """
import os
import importlib.abc
import socket
import subprocess

_violation = os.environ["LAST30DAYS_TEST_NETWORK_VIOLATION"]
_connect = socket.socket.connect
def _guarded_connect(self, address):
    if self.family in (socket.AF_INET, socket.AF_INET6):
        open(_violation, "a", encoding="utf-8").write("network-connect\\n")
        raise RuntimeError("network disabled by service test")
    return _connect(self, address)
socket.socket.connect = _guarded_connect

def _blocked_popen(*args, **kwargs):
    open(_violation, "a", encoding="utf-8").write("subprocess\\n")
    raise RuntimeError("subprocess disabled by service test")
subprocess.Popen = _blocked_popen

class _BlockedAcquisitionImports(importlib.abc.MetaPathFinder):
    blocked = {
        "lib.pipeline",
        "lib.facebook",
        "lib.linkedin",
        "lib.twitter",
        "lib.youtube",
        "lib.browser_service_client",
    }
    def find_spec(self, fullname, path=None, target=None):
        if fullname in self.blocked:
            open(_violation, "a", encoding="utf-8").write(
                "acquisition-import:" + fullname + "\\n"
            )
            raise RuntimeError("acquisition modules disabled by service test")
        return None

import sys
sys.meta_path.insert(0, _BlockedAcquisitionImports())
""",
        encoding="utf-8",
    )
    socket_path = runtime_dir / "last30days" / "service.sock"
    db_path = data_dir / "research.db"
    store.init_db(db_path)
    conn = sqlite3.connect(db_path)
    observed_at = datetime.now(timezone.utc).isoformat()
    topic_id = conn.execute(
        "INSERT INTO topics(name) VALUES ('Browser research')"
    ).lastrowid
    run_id = conn.execute(
        """INSERT INTO research_runs(topic_id, run_date, status)
           VALUES (?, ?, 'completed')""",
        (topic_id, observed_at),
    ).lastrowid
    conn.execute(
        """INSERT INTO findings
           (run_id, topic_id, source, source_url, source_title, author,
            content, summary, first_seen, last_seen)
           VALUES (?, ?, 'reddit', 'https://reddit.example/cached-browser',
                   'Cached browser research', 'researcher',
                   'Cached browser research without any live acquisition.',
                   'Cached browser research', ?, ?)""",
        (run_id, topic_id, observed_at, observed_at),
    )
    conn.commit()
    conn.close()
    env = {
        **os.environ,
        "PYTHONPATH": os.pathsep.join([str(canary_dir), str(SCRIPTS)]),
        "LAST30DAYS_TEST_NETWORK_VIOLATION": str(violation_path),
        "LAST30DAYS_CONFIG_DIR": str(tmp_path / "empty-config"),
    }
    process = subprocess.Popen(
        [
            sys.executable,
            str(SERVICE),
            "serve",
            "--socket",
            str(socket_path),
            "--db",
            str(db_path),
        ],
        cwd=ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    client = ServiceClient(socket_path)
    try:
        info = _wait_ready(client, process)
        assert info.status is contracts.ServiceStatus.READY
        before = sqlite3.connect(db_path).execute(
            """SELECT
                 (SELECT COUNT(*) FROM service_jobs),
                 (SELECT COUNT(*) FROM service_job_events),
                 (SELECT COUNT(*) FROM acquisitions)"""
        ).fetchone()
        response = client.query(
            contracts.QueryRequest.from_dict(
                {
                    "schema_version": 1,
                    "request_id": "query-empty",
                    "profile_id": "default",
                    "query": "cached browser research",
                    "freshness_policy": "cache_only",
                    "response_mode": "evidence",
                    "filters": {},
                    "top_k": 8,
                    "max_chars": 8192,
                    "wait_ms": 0,
                }
            )
        )
        prefer_cache_response = client.query(
            contracts.QueryRequest.from_dict(
                {
                    "schema_version": 1,
                    "request_id": "query-prefer-cache",
                    "profile_id": "default",
                    "query": "cached browser research",
                    "freshness_policy": "prefer_cache",
                    "response_mode": "evidence",
                    "filters": {},
                    "top_k": 8,
                    "max_chars": 8192,
                    "wait_ms": 0,
                }
            )
        )
        after = sqlite3.connect(db_path).execute(
            """SELECT
                 (SELECT COUNT(*) FROM service_jobs),
                 (SELECT COUNT(*) FROM service_job_events),
                 (SELECT COUNT(*) FROM acquisitions)"""
        ).fetchone()

        assert response.cache_status is contracts.CacheStatus.FRESH
        assert prefer_cache_response.cache_status is contracts.CacheStatus.FRESH
        assert [item.url for item in response.evidence] == [
            "https://reddit.example/cached-browser"
        ]
        published_versions = {
            row[0]
            for row in sqlite3.connect(db_path).execute(
                """SELECT index_version FROM index_versions
                   WHERE published_at IS NOT NULL"""
            ).fetchall()
        }
        assert response.index_version in published_versions
        assert prefer_cache_response.index_version in published_versions
        assert response.job_id is None
        assert prefer_cache_response.job_id is None
        assert before == after
        assert before[0] >= 1
        assert before[2] >= 1
        assert not violation_path.exists()
    finally:
        process.terminate()
        stdout, stderr = process.communicate(timeout=8)

    assert process.returncode == 0, stderr
    assert stdout == ""
    assert not socket_path.exists()
    assert not violation_path.exists()
    assert stat.S_IMODE(runtime_dir.joinpath("last30days").stat().st_mode) == 0o700
    assert stat.S_IMODE(data_dir.stat().st_mode) == 0o700
    assert stat.S_IMODE(db_path.stat().st_mode) == 0o600


def test_service_constructs_disabled_tick_schedule_without_tick_work(tmp_path):
    runtime_dir = tmp_path / "runtime"
    data_dir = tmp_path / "data"
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    db_path = data_dir / "research.db"
    socket_path = runtime_dir / "last30days" / "service.sock"
    config_path = config_dir / "tick-config-v1.json"
    config_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "config_revision": "disabled-schedule-1",
                "services": [
                    {
                        "service_id": "reddit",
                        "source": "reddit",
                        "providers": [
                            {
                                "provider_id": "reddit-keyless",
                                "adapter_type": "reddit_keyless",
                                "resource_keys": ["network:reddit"],
                                "fallback_on": ["transient"],
                                "limits": {
                                    "attempts": 1,
                                    "network_requests": 10,
                                    "wall_seconds": 30,
                                    "items": 3,
                                    "cost_cents": 0,
                                    "model_tokens": 0,
                                },
                            }
                        ],
                    }
                ],
                "targets": [
                    {
                        "target_id": "reddit-topic",
                        "service_id": "reddit",
                        "surface_kind": "topic",
                        "selector": {"topic": "OpenAI"},
                        "access_partition_id": "public",
                        "retention_class": "durable",
                        "enabled": True,
                    }
                ],
                "tick": {
                    "timezone": "UTC",
                    "lateness_seconds": 86_400,
                    "aggregate_limits": {
                        "attempts": 1,
                        "network_requests": 10,
                        "wall_seconds": 30,
                        "items": 3,
                        "cost_cents": 0,
                        "model_tokens": 0,
                    },
                    "schedule": {
                        "enabled": False,
                        "schedule_id": "daily-default",
                        "interval_seconds": 86_400,
                        "anchor_seconds": 0,
                    },
                },
                "artifacts": {
                    "root": str(tmp_path / "artifacts"),
                    "retention_days": 30,
                    "encryption_adapter": None,
                },
                "analysis": {
                    "ocr_enabled": False,
                    "ocr_adapter_type": None,
                    "semantic_sidecars_enabled": False,
                    "semantic_sidecar_adapter_type": None,
                },
                "notifications": {
                    "transports": [
                        {
                            "transport_id": "ops",
                            "adapter_type": "gws_email",
                            "credential_ref": "credential-ref:test",
                            "routing": {"recipient": "operator@example.test"},
                        }
                    ],
                    "reminder_seconds": 3600,
                },
                "query": {
                    "embedding_space": "local-hash-v1",
                    "fusion_version": "rrf-v1",
                },
            }
        ),
        encoding="utf-8",
    )
    env = {
        **os.environ,
        "PYTHONPATH": str(SCRIPTS),
        "LAST30DAYS_CONFIG_DIR": str(config_dir),
    }
    process = subprocess.Popen(
        [
            sys.executable,
            str(SERVICE),
            "serve",
            "--socket",
            str(socket_path),
            "--db",
            str(db_path),
        ],
        cwd=ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    client = ServiceClient(socket_path)
    try:
        _wait_ready(client, process)
        status = client.tick_schedule_status()
        conn = sqlite3.connect(db_path)
        counts = conn.execute(
            """SELECT
                 (SELECT COUNT(*) FROM service_tick_schedules),
                 (SELECT COUNT(*) FROM service_ticks)"""
        ).fetchone()
        conn.close()
    finally:
        process.terminate()
        _, stderr = process.communicate(timeout=8)

    assert process.returncode == 0, stderr
    assert status["schedule_id"] == "daily-default"
    assert status["enabled"] is False
    assert status["state"] == "disabled"
    assert counts == (0, 0)


def test_service_help_does_not_require_runtime_environment():
    env = {
        key: value
        for key, value in os.environ.items()
        if key not in {"XDG_RUNTIME_DIR", "LAST30DAYS_SERVICE_SOCKET"}
    }
    result = subprocess.run(
        [sys.executable, str(SERVICE), "--help"],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        timeout=8,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "Run or query the local last30days intelligence service" in result.stdout


def test_cli_request_id_is_generated_unless_caller_supplies_idempotency_key():
    parser = build_parser()

    assert parser.parse_args(["query", "first"]).request_id is None
    assert (
        parser.parse_args(
            ["query", "second", "--request-id", "caller-key"]
        ).request_id
        == "caller-key"
    )


def test_job_cli_exposes_explicit_operator_resume():
    args = build_parser().parse_args(["job", "job-001", "--resume"])

    assert args.job_id == "job-001"
    assert args.resume is True


def test_manual_collection_cli_exposes_bounded_attempt_override():
    args = build_parser().parse_args(
        ["collection", "run", "spec-x", "--max-attempts", "2"]
    )

    assert args.collection_spec_id == "spec-x"
    assert args.max_attempts == 2


def test_operator_intelligence_entrypoint_is_explicit_and_bounded():
    args = build_parser().parse_args(
        [
            "intelligence",
            "enrich",
            "--job-id",
            "job-001",
            "--input",
            "chunks.json",
        ]
    )

    assert args.mode == "enrich"
    assert args.job_id == "job-001"
    assert args.max_calls == 1
    assert args.max_input_bytes == 65_536
    assert args.cost_budget_cents == 1

    repair = build_parser().parse_args(
        [
            "repair",
            "evaluate",
            "--policy",
            "policy.json",
            "--run-id",
            "repair-run-" + "a" * 24,
            "--test",
            "uv run pytest tests/test_reddit.py",
        ]
    )
    assert repair.repair_action == "evaluate"
    assert repair.test == ["uv run pytest tests/test_reddit.py"]
