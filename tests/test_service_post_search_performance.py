"""Opt-in local 10,000-post measurement; excluded from ordinary test runs."""

import hashlib
import json
import os
import platform
import resource
import time

import pytest

from lib.service_contracts import PostSearchRequest
from lib.service_post_search import PostSearchBackend
from tests.post_search_fixtures import seed_large_corpus
from tests.test_service_post_search import _request_payload


@pytest.mark.skipif(
    os.environ.get("POST_SEARCH_PERFORMANCE") != "1",
    reason="opt-in synthetic performance fixture",
)
def test_ten_thousand_post_measurement(tmp_path):
    db = tmp_path / "performance.db"
    seed_large_corpus(db)
    before = hashlib.sha256(db.read_bytes()).hexdigest()
    backend = PostSearchBackend(db)
    request = _request_payload(page_size=20)
    started = time.perf_counter()
    first = backend.search(
        PostSearchRequest.from_dict(request), access_partitions=("public",)
    )
    first_seconds = time.perf_counter() - started
    started = time.perf_counter()
    second = backend.search(
        PostSearchRequest.from_dict({**request, "cursor": first.next_cursor}),
        access_partitions=("public",),
    )
    cursor_seconds = time.perf_counter() - started
    receipt = {
        "corpus": "synthetic-5000-legacy-5000-temporal-v1",
        "posts": 10_000,
        "database_sha256": before,
        "python": platform.python_version(),
        "platform": platform.platform(),
        "first_page_seconds": first_seconds,
        "cursor_page_seconds": cursor_seconds,
        "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "first_returned": first.returned,
        "second_returned": second.returned,
        "response_bytes": len(
            json.dumps(
                first.to_dict(), ensure_ascii=False, separators=(",", ":")
            ).encode()
        ),
    }
    print("POST_SEARCH_MEASUREMENT=" + json.dumps(receipt, sort_keys=True))
    assert first.returned == second.returned == 20
    assert not (
        {hit.post_id for hit in first.hits} & {hit.post_id for hit in second.hits}
    )
    assert hashlib.sha256(db.read_bytes()).hexdigest() == before
    # Frozen after the baseline and before Packet 3 product implementation.
    assert first_seconds <= 5.0
    assert cursor_seconds <= 0.1
    assert receipt["peak_rss_kib"] <= 262_144
    assert receipt["response_bytes"] <= 131_072
    assert first.coverage["semantic"]["families"]["legacy"]["available"] == 5_000
    assert first.coverage["semantic"]["families"]["temporal"]["available"] == 5_000
