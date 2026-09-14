"""Read-only immutable collection revisions composed with stored-post search."""

from dataclasses import dataclass

from . import service_monitor_contracts as c
from .service_monitor_views import SavedQueryViewProvider, _digest
from .service_monitors import MonitorKernelError


@dataclass(frozen=True)
class FollowDefinition:
    view_ref: c.FollowViewRefV1
    access_partition_id: str
    spec: object

    def to_dict(self):
        return {
            "schema_version": 1,
            "view_ref": self.view_ref.to_dict(),
            "collection_spec": self.spec.to_dict(),
            "spec_digest": self.spec.spec_digest,
            "search": {
                "profile_id": self.spec.profile_id,
                "query": None,
                "filters": {
                    "sources": [self.spec.source],
                    "collection_refs": ["legacy:spec:" + self.spec.collection_spec_id],
                },
                "page_size": 100,
                "sort": "observed_desc",
                "revision_mode": "current",
            },
        }


class FollowViewProvider(SavedQueryViewProvider):
    def __init__(self, repository, search_backend, collection_reader, **limits):
        super().__init__(repository, search_backend, **limits)
        self.collection_reader = collection_reader

    def definition(self, ref, partition, *, readable=True):
        if self.collection_reader is None:
            raise MonitorKernelError(
                c.MonitorErrorCode.VIEW_UNAVAILABLE, "follow view unavailable"
            )
        try:
            spec = self.collection_reader.get_spec_revision(
                ref.collection_spec_id, ref.spec_version
            )
            current = self.collection_reader.get_spec(ref.collection_spec_id)
        except KeyError:
            raise MonitorKernelError(
                c.MonitorErrorCode.VIEW_UNAVAILABLE, "follow view unavailable"
            ) from None
        if (
            spec.access_partition_id != partition
            or current.access_partition_id != partition
        ):
            raise MonitorKernelError(
                c.MonitorErrorCode.VIEW_UNAVAILABLE, "follow view unavailable"
            )
        if spec.collection_purpose != "tailored_follow" or spec.is_quarantined_follow:
            raise MonitorKernelError(
                c.MonitorErrorCode.VIEW_UNAVAILABLE, "follow view unavailable"
            )
        if readable and (
            current.lifecycle_state != "active"
            or current.is_quarantined_follow
            or current.follow_target_id != spec.follow_target_id
        ):
            raise MonitorKernelError(
                c.MonitorErrorCode.VIEW_UNAVAILABLE, "follow view unavailable"
            )
        return FollowDefinition(ref, partition, spec)

    def capture(self, ref, access_partition_id, capture_id):
        definition = self.definition(ref, access_partition_id)
        snapshot_id = (
            "follow-view-"
            + _digest([ref.to_dict(), access_partition_id, capture_id])[:32]
        )
        c._bounded_text(capture_id, "capture_id")
        limits = {
            "max_items": self.max_items,
            "max_pages": self.max_pages,
            "max_bytes": self.max_bytes,
            "max_seconds": self.max_seconds,
        }
        binding = _digest({"definition": definition.to_dict(), "limits": limits})
        if not self.repository.begin_capture(snapshot_id, binding):
            return self.read(ref, access_partition_id, snapshot_id)
        try:
            snapshot, receipt = self._capture(definition, snapshot_id, limits)
            # Re-check lifecycle/identity before publishing a frozen view.
            self.definition(ref, access_partition_id)
            self.repository.put_snapshot(snapshot)
            self.repository.finish_capture(snapshot_id, receipt=receipt)
            return snapshot
        except Exception as exc:
            self.repository.finish_capture(
                snapshot_id, error_code="follow_capture_failed"
            )
            if isinstance(exc, MonitorKernelError):
                raise
            raise MonitorKernelError(
                c.MonitorErrorCode.VIEW_UNAVAILABLE, "follow capture failed"
            ) from exc

    def read(self, ref, access_partition_id, snapshot_id):
        receipt = self.repository.capture_receipt(snapshot_id)
        snapshot = c.SavedQueryViewSnapshotV1.from_dict(receipt["snapshot"])
        if (
            snapshot.view_ref != ref
            or snapshot.access_partition_id != access_partition_id
        ):
            raise MonitorKernelError(
                c.MonitorErrorCode.VIEW_UNAVAILABLE, "follow view unavailable"
            )
        return snapshot
