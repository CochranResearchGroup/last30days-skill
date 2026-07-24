"""Installable Linux user-service boundary."""

import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INSTALLER = ROOT / "skills" / "last30days" / "scripts" / "install-service.sh"


def test_installer_renders_private_restartable_user_unit(tmp_path):
    result = subprocess.run(
        ["bash", str(INSTALLER), "--print-unit"],
        check=True,
        capture_output=True,
        text=True,
        env={
            **os.environ,
            "HOME": str(tmp_path),
            "LAST30DAYS_PYTHON": "/usr/bin/python3",
        },
    )

    assert 'ExecStart="/usr/bin/python3"' in result.stdout
    assert "service.py\" serve" in result.stdout
    assert "UMask=0077" in result.stdout
    assert "NoNewPrivileges=true" in result.stdout
    assert "Restart=on-failure" in result.stdout
    assert not (tmp_path / ".config" / "systemd").exists()
