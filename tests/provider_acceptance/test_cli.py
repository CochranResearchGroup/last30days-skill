import pytest

from dev.last30days.scripts import provider_acceptance as cli


def test_run_refuses_existing_receipt_before_dependency_resolution(tmp_path, monkeypatch):
    output = tmp_path / "receipt.json"
    output.write_text("sentinel")
    monkeypatch.setattr(cli, "_dependencies", lambda: (_ for _ in ()).throw(AssertionError("dependencies resolved")))
    with pytest.raises(SystemExit) as stopped:
        cli.main(["run", "--output", str(output)])
    assert stopped.value.code == 2
    assert output.read_text() == "sentinel"
