"""Strict provider-free monitor commands shared by local service transports."""

from dataclasses import replace

from . import service_monitor_contracts as c
from .service_monitor_delivery import MonitorDelivery
from .service_monitor_digests import MonitorRecords, prepare_digest
from .service_monitor_follow_views import FollowViewProvider
from .service_monitor_import import import_legacy
from .service_monitor_views import (
    SavedQueryRepository,
    SavedQueryViewProvider,
    _digest,
    _json,
)
from .service_monitors import MonitorKernel, MonitorKernelError, _utc_now

COMMAND_FIELDS = {
    "create": {
        "monitor_id",
        "name",
        "view_ref",
        "cadence_seconds",
        "max_items",
        "retention_days",
    },
    "revise": {
        "monitor_id",
        "expected_revision",
        "name",
        "cadence_seconds",
        "max_items",
        "retention_days",
    },
    "get": {"monitor_id"},
    "list": {"limit", "after"},
    "activate": {"monitor_id"},
    "pause": {"monitor_id"},
    "archive": {"monitor_id"},
    "resume": {"monitor_id", "snapshot_id"},
    "capture": {"monitor_id", "capture_id"},
    "evaluate": {"monitor_id", "snapshot_id"},
    "digest": {"run_id"},
    "run": {"run_id"},
    "accept": {"run_id"},
    "reject": {"run_id"},
    "baseline": {"monitor_id"},
    "history": {"monitor_id", "limit", "after"},
    "set_delivery": {"monitor_id", "expected_version", "channel_config_ref"},
    "get_delivery": {"monitor_id"},
    "prepare_delivery": {"run_id", "preference_version"},
    "delivery_intent": {"intent_id"},
    "send": {"intent_id"},
    "resend": {"intent_id", "reason", "request_id"},
    "import_legacy": {"export"},
}


class MonitorApplication:
    def __init__(
        self,
        db_path,
        search_backend,
        *,
        access_partitions,
        collection_reader=None,
        clock=None,
    ):
        self.db_path, self.search_backend = db_path, search_backend
        self.access_partitions, self.clock = access_partitions, clock or _utc_now
        self.repository = SavedQueryRepository(db_path)
        self.repository.initialize()
        self.queries = SavedQueryViewProvider(
            self.repository, search_backend, max_bytes=32_768
        )
        self.follows = FollowViewProvider(
            self.repository, search_backend, collection_reader, max_bytes=32_768
        )
        self.records = MonitorRecords(self.repository)
        self.delivery = MonitorDelivery(self.records)
        self.kernel = MonitorKernel(self.repository, self, clock=self.clock)

    def read(self, ref, partition, snapshot_id):
        provider = self.follows if isinstance(ref, c.FollowViewRefV1) else self.queries
        return provider.read(ref, partition, snapshot_id)

    def _spec(self, monitor_id, partition):
        scoped = "scoped-monitor-" + _digest([partition, monitor_id])[:32]
        try:
            return self._stored_spec(scoped, partition)
        except KeyError:
            return self._stored_spec(monitor_id, partition)  # legacy v1 identity

    def _stored_spec(self, monitor_id, partition):
        spec = self.repository.current_spec(monitor_id)
        if spec.access_partition_id != partition:
            raise KeyError("monitor unavailable")
        return spec

    def _readable(self, spec, profile):
        if isinstance(spec.view_ref, c.FollowViewRefV1):
            try:
                self.follows.definition(spec.view_ref, spec.access_partition_id)
            except MonitorKernelError:
                if spec.lifecycle_state is c.MonitorLifecycle.ACTIVE:
                    self.kernel.pause(spec.monitor_id, actor=profile)
                raise
        else:
            self.repository.get(spec.view_ref, spec.access_partition_id)

    def _page(self, kind, partition, limit, after, monitor_id=None):
        conn = self.repository._connect()
        try:
            if kind == "list":
                rows = conn.execute(
                    """SELECT DISTINCT monitor_id FROM service_monitor_specs
                    WHERE access_partition_id=? AND monitor_id>? ORDER BY monitor_id LIMIT ?""",
                    (partition, after or "", limit + 1),
                ).fetchall()
                ids = [row[0] for row in rows]
                items = [
                    self._stored_spec(key, partition).to_dict() for key in ids[:limit]
                ]
            else:
                rows = conn.execute(
                    """SELECT run_id FROM service_monitor_runs
                    WHERE monitor_id=? AND run_id>? ORDER BY run_id LIMIT ?""",
                    (monitor_id, after or "", limit + 1),
                ).fetchall()
                ids = [row[0] for row in rows]
                items = [self.repository.get_run(key).to_dict() for key in ids[:limit]]
        finally:
            conn.close()
        return {
            "monitors" if kind == "list" else "runs": items,
            "next_after": ids[limit - 1] if len(ids) > limit else None,
        }

    def command(self, payload):
        try:
            if len(_json(payload).encode()) > 65_536:
                raise c.MonitorContractError("monitor request exceeds byte bound")
        except (TypeError, ValueError) as exc:
            raise c.MonitorContractError("monitor request is not bounded JSON") from exc
        result = self._command(payload)
        partition = (
            "public"
            if payload["profile_id"] == "default"
            else "profile:" + payload["profile_id"]
        )
        result = self._export(result, partition)
        if len(_json(result).encode()) > 126_976:
            raise MonitorKernelError(
                c.MonitorErrorCode.VIEW_UNAVAILABLE,
                "monitor response exceeds byte bound; use a smaller page",
            )
        return result

    def _export(self, value, partition):
        if isinstance(value, list):
            return [self._export(item, partition) for item in value]
        if not isinstance(value, dict):
            return value
        result = {key: self._export(item, partition) for key, item in value.items()}
        if "monitor_id" in result:
            try:
                result["monitor_id"] = self.records.get(
                    "monitor_alias", result["monitor_id"], partition
                )["alias"]
            except KeyError:
                pass
        return result

    def _command(self, payload):
        c._exact(
            c._object(payload, "monitor_request"),
            ("profile_id", "command"),
            "monitor_request",
        )
        profile = c._bounded_text(payload["profile_id"], "profile_id")
        partitions = self.access_partitions(profile)
        partition = "public" if profile == "default" else "profile:" + profile
        if partition not in partitions:
            raise MonitorKernelError(
                c.MonitorErrorCode.VIEW_UNAVAILABLE, "monitor unavailable"
            )
        cmd = c._object(payload["command"], "command")
        action = cmd.get("action")
        if not isinstance(action, str) or action not in COMMAND_FIELDS:
            raise c.MonitorContractError("invalid monitor action")
        c._exact(cmd, COMMAND_FIELDS[action] | {"action"}, "monitor command")
        for key in (
            "monitor_id",
            "run_id",
            "snapshot_id",
            "capture_id",
            "name",
            "after",
            "intent_id",
            "reason",
            "request_id",
            "channel_config_ref",
        ):
            if key in cmd and not (key == "after" and cmd[key] is None):
                c._bounded_text(cmd[key], key, 256 if key == "name" else 128)
        for key, maximum in (
            ("limit", 20),
            ("max_items", 100),
            ("retention_days", 3650),
            ("cadence_seconds", 31_536_000),
            ("expected_revision", 1_000_000),
            ("preference_version", 1_000_000),
        ):
            if key in cmd and (c._positive_int(cmd[key], key) > maximum):
                raise c.MonitorContractError(f"{key} exceeds bound")
        if (
            "expected_version" in cmd
            and c._non_negative_int(cmd["expected_version"], "expected_version")
            > 1_000_000
        ):
            raise c.MonitorContractError("expected_version exceeds bound")
        try:
            if action == "import_legacy":
                return import_legacy(self, cmd["export"], profile, partition)
            if action == "list":
                return self._page(action, partition, cmd["limit"], cmd["after"])
            if action == "create":
                try:
                    prior = self._spec(cmd["monitor_id"], partition)
                except KeyError:
                    prior = None
                if prior is not None:
                    comparable = prior.to_dict()
                    if all(
                        comparable[key] == value
                        for key, value in cmd.items()
                        if key not in {"action", "monitor_id"}
                    ):
                        return comparable
                    raise MonitorKernelError(
                        c.MonitorErrorCode.IMMUTABLE_CONFLICT,
                        "monitor identity already exists",
                    )
                ref = c.view_ref_from_dict(cmd["view_ref"])
                if isinstance(ref, c.FollowViewRefV1):
                    self.follows.definition(ref, partition)
                else:
                    self.repository.get(ref, partition)
                spec = c.MonitorSpecV1.from_dict(
                    {
                        **{key: value for key, value in cmd.items() if key != "action"},
                        "monitor_id": "scoped-monitor-"
                        + _digest([partition, cmd["monitor_id"]])[:32],
                        "schema_version": 1,
                        "revision": 1,
                        "access_partition_id": partition,
                        "lifecycle_state": "disabled",
                        "comparison_policy": c.COMPARATOR_VERSION,
                        "created_by": profile,
                        "created_at": self.clock(),
                    }
                )
                self.records.put(
                    "monitor_alias",
                    spec.monitor_id,
                    partition,
                    spec.monitor_id,
                    {"alias": cmd["monitor_id"]},
                )
                return self.kernel.create(spec).to_dict()
            if "intent_id" in cmd:
                intent = self.records.get(
                    "delivery_intent", cmd["intent_id"], partition
                )
                spec = self._stored_spec(intent["monitor_id"], partition)
                run = self.repository.get_run(intent["run_id"])
            elif "run_id" in cmd:
                run = self.repository.get_run(cmd["run_id"])
                spec = self._stored_spec(run.monitor_id, partition)
            else:
                spec = self._spec(cmd["monitor_id"], partition)
            if action == "get":
                return spec.to_dict()
            if action == "get_delivery":
                return self.delivery.preference(spec.monitor_id, partition)
            if action == "set_delivery":
                return self.delivery.set_preference(
                    spec, cmd["expected_version"], cmd["channel_config_ref"]
                )
            if action == "delivery_intent":
                return {
                    "intent": intent,
                    "latest_receipt": self.delivery.latest_attempt(intent["intent_id"]),
                }
            if action == "send":
                raise MonitorKernelError(
                    c.MonitorErrorCode.INVALID_LIFECYCLE, "delivery disabled"
                )
            if action in {"prepare_delivery", "resend"}:
                conn = self.repository._connect()
                try:
                    accepted = conn.execute(
                        "SELECT decision FROM service_monitor_decisions WHERE run_id=?",
                        (run.run_id,),
                    ).fetchone()
                finally:
                    conn.close()
                if not accepted or accepted[0] != "accepted":
                    raise MonitorKernelError(
                        c.MonitorErrorCode.INVALID_LIFECYCLE,
                        "delivery intent requires an accepted digest",
                    )
                digest = self.records.get("digest", run.run_id, partition)
                return self.delivery.prepare(
                    spec,
                    digest,
                    cmd["preference_version"]
                    if action == "prepare_delivery"
                    else intent["preference_version"],
                    parent=None if action == "prepare_delivery" else intent,
                    reason=cmd.get("reason"),
                    request_id=cmd.get("request_id"),
                )
            if action == "history":
                return self._page(
                    action, partition, cmd["limit"], cmd["after"], spec.monitor_id
                )
            if action == "revise":
                if cmd["expected_revision"] != spec.revision:
                    raise MonitorKernelError(
                        c.MonitorErrorCode.INVALID_REVISION, "monitor revision changed"
                    )
                updated = replace(
                    spec,
                    revision=spec.revision + 1,
                    name=cmd["name"],
                    cadence_seconds=cmd["cadence_seconds"],
                    max_items=cmd["max_items"],
                    retention_days=cmd["retention_days"],
                    created_by=profile,
                    created_at=self.clock(),
                )
                self.repository.put_spec(updated)
                return updated.to_dict()
            if action in {"activate", "resume", "capture", "evaluate"}:
                self._readable(spec, profile)
            if action in {"activate", "pause", "archive"}:
                return getattr(self.kernel, action)(
                    spec.monitor_id, actor=profile
                ).to_dict()
            if action == "resume":
                return self.kernel.resume(
                    spec.monitor_id, cmd["snapshot_id"], actor=profile
                ).to_dict()
            if action == "capture":
                if spec.lifecycle_state is not c.MonitorLifecycle.ACTIVE:
                    raise MonitorKernelError(
                        c.MonitorErrorCode.INVALID_LIFECYCLE,
                        "only an active monitor can capture",
                    )
                provider = (
                    self.follows
                    if isinstance(spec.view_ref, c.FollowViewRefV1)
                    else self.queries
                )
                return provider.capture(
                    spec.view_ref, partition, cmd["capture_id"]
                ).to_dict()
            if action == "evaluate":
                run = self.kernel.evaluate(spec.monitor_id, cmd["snapshot_id"])
                return {
                    "run": run.to_dict(),
                    "digest": prepare_digest(self.repository, self.records, run, spec),
                }
            if action == "digest":
                return self.records.get("digest", run.run_id, partition)
            if action == "run":
                return run.to_dict()
            if action in {"accept", "reject"}:
                self.records.get("digest", run.run_id, partition)
                return getattr(self.kernel, action)(run.run_id, actor=profile).to_dict()
            baseline = self.repository.current_baseline(spec.monitor_id)
            return {"baseline": None if baseline is None else baseline.to_dict()}
        except KeyError:
            raise MonitorKernelError(
                c.MonitorErrorCode.VIEW_UNAVAILABLE, "monitor unavailable"
            ) from None
