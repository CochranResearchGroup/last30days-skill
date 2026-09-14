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
    assert (reddit.state, reddit.reason_code) == ("available", None)
    assert (
        DEFAULT_FOLLOW_CAPABILITIES.capability("facebook", "account").state
        == "unsupported"
    )
    with pytest.raises(FollowCapabilityError, match="duplicate"):
        FollowCapabilityRegistry(
            [
                FollowCapabilityV1(
                    "x",
                    "account",
                    "available",
                    validator=str,
                    route="x_account",
                    selector_field="account",
                    access_method="agent_browser",
                ),
                FollowCapabilityV1(
                    "x",
                    "account",
                    "available",
                    validator=str,
                    route="x_account",
                    selector_field="account",
                    access_method="agent_browser",
                ),
            ]
        )
    with pytest.raises(FollowCapabilityError, match="requires validator"):
        FollowCapabilityV1("x", "account", "available")


def test_compatibility_trace_is_additive_idempotent_and_deterministic():
    rows = [
        {
            "collection_spec_id": "general-a",
            "collection_purpose": "general",
            "source": "reddit",
            "surface_kind": "topic",
        },
        {
            "collection_spec_id": "x-list-a",
            "collection_purpose": "tailored_follow",
            "source": "x",
            "surface_kind": "list",
        },
        {
            "collection_spec_id": "legacy-a",
            "collection_purpose": "tailored_follow",
            "source": "reddit",
            "surface_kind": "account",
        },
    ]
    first = compatibility_trace(rows)
    assert first == compatibility_trace(rows)
    assert first["preserved"] == 1
    assert first["mapped"] == 1
    assert first["quarantined"] == 1
    assert first["digest"].startswith("sha256:")
    assert first == compatibility_trace(reversed(rows))
    same_counts_different_rows = [
        {**row, "collection_spec_id": f"other-{index}"}
        for index, row in enumerate(rows)
    ]
    assert first["digest"] != compatibility_trace(same_counts_different_rows)["digest"]
    assert set(first["class_digests"]) == {"preserved", "mapped", "quarantined"}


def test_catalog_separates_support_dependency_and_execution_readiness():
    missing = DEFAULT_FOLLOW_CAPABILITIES.catalog({}, which=lambda _: None)
    present = DEFAULT_FOLLOW_CAPABILITIES.catalog({}, which=lambda _: "/fixture/tool")
    assert missing["registry_digest"] == present["registry_digest"]
    yt = next(row for row in missing["targets"] if row["source"] == "youtube")
    ready_yt = next(row for row in present["targets"] if row["source"] == "youtube")
    assert yt["state"] == "available"
    assert yt["dependency_readiness"] == {
        "state": "unavailable",
        "reason_code": "missing_tool",
    }
    assert ready_yt["dependency_readiness"] == {"state": "ready", "reason_code": None}
    assert ready_yt["execution_readiness"] == {
        "state": "unavailable",
        "reason_code": "transport_not_configured",
    }
    assert yt["route"] == "youtube_channel_uploads"
    assert yt["selector_field"] == "channel"
    assert yt["access_partition_required"] is True
    assert "resume" in yt["operations"]
    assert yt["bounds"]["item_limit_max"] == 100


def test_available_capability_requires_a_route_and_valid_bounds():
    with pytest.raises(FollowCapabilityError, match="route"):
        FollowCapabilityV1("reddit", "user", "available", validator=str)
    with pytest.raises(FollowCapabilityError, match="bounds"):
        FollowCapabilityV1(
            "reddit",
            "user",
            "available",
            validator=str,
            route="reddit_user_posts",
            selector_field="user",
            access_method="keyless",
            interval_seconds_min=30,
        )


def test_compatibility_does_not_map_malformed_newly_supported_native_rows():
    rows = [
        {
            "collection_spec_id": "invalid-native",
            "collection_purpose": "tailored_follow",
            "source": "reddit",
            "surface_kind": "community",
            "selector": {"community": "bad//name"},
        }
    ]
    assert compatibility_trace(rows)["quarantined"] == 1
