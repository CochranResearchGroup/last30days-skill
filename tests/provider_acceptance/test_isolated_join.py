import hashlib
import json

from dev.last30days.provider_acceptance.contracts import (
    AdapterCase,
    SealedCase,
    TransportObservation,
)
from dev.last30days.provider_acceptance.isolated_join import IsolatedServiceJoin


def test_isolated_join_commits_one_sample_and_tears_down_exact_owner(tmp_path):
    fixture = tmp_path / "fixture.json"
    fixture.write_text(json.dumps({"items": [{"id": "one"}]}))
    case = SealedCase(
        AdapterCase("case", "adapter", "reddit", "http", "fixture.json"),
        "sha256:" + hashlib.sha256(fixture.read_bytes()).hexdigest(),
    )

    def tracer(_case, *, item_limit):
        assert item_limit == 3
        return TransportObservation(
            "success", True, 1, 1, None, "exact", case.fixture_sha256, {"owned": True}
        )

    observation, teardown = IsolatedServiceJoin()(case, tracer, item_limit=3)
    assert observation.item_count == 1
    assert teardown["database_committed"]
    assert teardown["socket_closed"]
    assert teardown["owner_census"] == 0
