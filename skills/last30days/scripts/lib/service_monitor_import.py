"""Explicit export-only legacy import; never reads a path or adopts delivery."""

from . import service_monitor_contracts as c
from .service_monitor_views import _digest
from .service_monitors import MonitorKernelError


def import_legacy(app, exported, profile, partition):
    exported = c._object(exported, "legacy_export")
    c._exact(exported, {"source_locator", "topic"}, "legacy_export")
    locator = c._bounded_text(exported["source_locator"], "source_locator", 256)
    topic = c._object(exported["topic"], "topic")
    if not {"id", "query", "interval_seconds"} <= set(topic) or len(topic) > 32:
        raise c.MonitorContractError("legacy topic fields invalid")
    topic_id = c._bounded_text(topic["id"], "topic.id")
    query = c._bounded_text(topic["query"], "topic.query", 4096)
    cadence = c._positive_int(topic["interval_seconds"], "interval_seconds")
    if cadence > 31_536_000:
        raise c.MonitorContractError("legacy cadence exceeds bound")
    unmapped = sorted(
        c._bounded_text(key, "legacy field", 64)
        for key in set(topic) - {"id", "query", "interval_seconds"}
    )
    key = "legacy-monitor-" + _digest([partition, locator, topic_id])[:32]
    binding = _digest([locator, topic_id, query, cadence, unmapped])
    try:
        prior = app.records.get("legacy_import", key, partition)
    except KeyError:
        prior = None
    if prior is not None:
        if prior["binding"] != binding:
            raise MonitorKernelError(
                c.MonitorErrorCode.IMMUTABLE_CONFLICT, "legacy import inputs changed"
            )
        return prior
    definition = c.SavedQueryDefinitionV1.from_dict(
        {
            "schema_version": 1,
            "saved_query_id": key,
            "version": 1,
            "access_partition_id": partition,
            "search": {
                "profile_id": profile,
                "query": query,
                "filters": {},
                "page_size": 20,
                "sort": "relevance",
                "revision_mode": "current",
            },
        }
    )
    app.repository.save(definition)
    monitor = app.command(
        {
            "profile_id": profile,
            "command": {
                "action": "create",
                "monitor_id": key,
                "name": "Imported legacy topic " + topic_id,
                "view_ref": definition.view_ref.to_dict(),
                "cadence_seconds": cadence,
                "max_items": 20,
                "retention_days": 30,
            },
        }
    )
    result = {
        "schema_version": 1,
        "source_locator": locator,
        "topic_id": topic_id,
        "binding": binding,
        "saved_query": definition.to_dict(),
        "monitor": monitor,
        "delivery": app.delivery.preference(key, partition),
        "unmapped_fields": unmapped,
    }
    return app.records.put("legacy_import", key, partition, key, result)
