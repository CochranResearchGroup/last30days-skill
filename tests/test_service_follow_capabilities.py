import pytest

from lib.service_follow_capabilities import (
    DEFAULT_FOLLOW_CAPABILITIES,
    FollowCapabilityError,
    FollowCapabilityRegistry,
    FollowCapabilityV1,
    compatibility_trace,
)


def test_closed_registry_distinguishes_available_unavailable_and_unsupported():
    assert DEFAULT_FOLLOW_CAPABILITIES.capability("x", "account").state == "available"
    reddit = DEFAULT_FOLLOW_CAPABILITIES.capability("reddit", "community")
    assert (reddit.state, reddit.reason_code) == ("unavailable", "adapter_not_implemented")
    assert DEFAULT_FOLLOW_CAPABILITIES.capability("facebook", "account").state == "unsupported"
    with pytest.raises(FollowCapabilityError, match="duplicate"):
        FollowCapabilityRegistry([
            FollowCapabilityV1("x", "account", "available", validator=str),
            FollowCapabilityV1("x", "account", "available", validator=str),
        ])
    with pytest.raises(FollowCapabilityError, match="requires validator"):
        FollowCapabilityV1("x", "account", "available")


def test_compatibility_trace_is_additive_idempotent_and_deterministic():
    rows = [
        {"collection_purpose": "general", "source": "reddit", "surface_kind": "topic"},
        {"collection_purpose": "tailored_follow", "source": "x", "surface_kind": "list"},
        {"collection_purpose": "tailored_follow", "source": "reddit", "surface_kind": "account"},
    ]
    first = compatibility_trace(rows)
    assert first == compatibility_trace(rows)
    assert first["preserved"] == 1
    assert first["mapped"] == 1
    assert first["quarantined"] == 1
    assert first["digest"].startswith("sha256:")
