"""Strict provider-free monitor commands shared by local service transports."""

from . import service_monitor_contracts as c
from .service_monitor_views import SavedQueryRepository, SavedQueryViewProvider
from .service_monitor_follow_views import FollowViewProvider
from .service_monitor_digests import MonitorRecords, prepare_digest
from .service_monitors import MonitorKernel, MonitorKernelError, _utc_now


class MonitorApplication:
    def __init__(self, db_path, search_backend, *, access_partitions,
                 collection_reader=None, clock=None):
        self.db_path, self.search_backend = db_path, search_backend
        self.access_partitions, self.clock = access_partitions, clock or _utc_now
        self.repository = SavedQueryRepository(db_path)
        self.repository.initialize()
        self.queries = SavedQueryViewProvider(self.repository, search_backend, max_bytes=32_768)
        self.follows = FollowViewProvider(self.repository, search_backend, collection_reader, max_bytes=32_768)
        self.records = MonitorRecords(self.repository)
        self.kernel = MonitorKernel(self.repository, self, clock=self.clock)

    def read(self, ref, partition, snapshot_id):
        provider = self.follows if isinstance(ref, c.FollowViewRefV1) else self.queries
        return provider.read(ref, partition, snapshot_id)

    def _spec(self, monitor_id, partition):
        spec = self.repository.current_spec(monitor_id)
        if spec.access_partition_id != partition:
            raise KeyError("monitor unavailable")
        return spec

    def command(self, payload):
        c._exact(c._object(payload, "monitor_request"), ("profile_id", "command"), "monitor_request")
        profile = c._bounded_text(payload["profile_id"], "profile_id")
        partitions = self.access_partitions(profile)
        partition = "public" if profile == "default" else "profile:" + profile
        if partition not in partitions:
            raise MonitorKernelError(c.MonitorErrorCode.VIEW_UNAVAILABLE, "monitor unavailable")
        cmd = c._object(payload["command"], "command")
        fields = {
            "create": {"monitor_id", "name", "view_ref", "cadence_seconds", "max_items", "retention_days"},
            "activate": {"monitor_id"}, "capture": {"monitor_id", "capture_id"},
            "evaluate": {"monitor_id", "snapshot_id"}, "digest": {"run_id"},
            "accept": {"run_id"}, "baseline": {"monitor_id"},
        }
        action = cmd.get("action")
        if not isinstance(action, str) or action not in fields:
            raise c.MonitorContractError("invalid monitor action")
        c._exact(cmd, fields[action] | {"action"}, "monitor command")
        try:
            if action == "create":
                ref = c.view_ref_from_dict(cmd["view_ref"])
                if isinstance(ref, c.FollowViewRefV1):
                    self.follows.definition(ref, partition)
                else:
                    self.repository.get(ref, partition)
                spec = c.MonitorSpecV1.from_dict({
                    **{key: value for key, value in cmd.items() if key != "action"},
                    "schema_version": 1, "revision": 1, "access_partition_id": partition,
                    "lifecycle_state": "disabled", "comparison_policy": c.COMPARATOR_VERSION,
                    "created_by": profile, "created_at": self.clock()})
                return self.kernel.create(spec).to_dict()
            if "run_id" in cmd:
                run = self.repository.get_run(cmd["run_id"])
                spec = self._spec(run.monitor_id, partition)
            else:
                spec = self._spec(cmd["monitor_id"], partition)
            if action == "activate":
                return self.kernel.activate(spec.monitor_id, actor=profile).to_dict()
            if action == "capture":
                provider = self.follows if isinstance(spec.view_ref, c.FollowViewRefV1) else self.queries
                return provider.capture(spec.view_ref, partition, cmd["capture_id"]).to_dict()
            if action == "evaluate":
                run = self.kernel.evaluate(spec.monitor_id, cmd["snapshot_id"])
                return {"run": run.to_dict(), "digest": prepare_digest(self.repository, self.records, run, spec)}
            if action == "digest":
                return self.records.get("digest", run.run_id, partition)
            if action == "accept":
                self.records.get("digest", run.run_id, partition)
                return self.kernel.accept(run.run_id, actor=profile).to_dict()
            baseline = self.repository.current_baseline(spec.monitor_id)
            return {"baseline": None if baseline is None else baseline.to_dict()}
        except KeyError:
            raise MonitorKernelError(c.MonitorErrorCode.VIEW_UNAVAILABLE, "monitor unavailable") from None
