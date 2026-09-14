"""Exact native YouTube uploads routing through injected transports."""

from __future__ import annotations

import json
import re
import time
from datetime import date

from .service_follow_capabilities import FollowCapabilityError, validate_native_request


def collect(request, config, *, transport=None, monotonic_clock=time.monotonic):
    """Validate one bounded uploads response; do not infer yt-dlp network usage.

    A transport must return explicit measured usage along with its provider-shaped
    payload. Missing transport/usage fails closed, including when yt-dlp exists.
    """
    items = []
    requests = 0
    diagnostics = {
        "follow_route": "youtube_channel_uploads",
        "failure_stage": "native_follow_route",
    }

    def result(error=None):
        return {
            "items": items if error is None else [],
            "error_type": error,
            "_network_request_count": requests,
            "diagnostics": diagnostics,
        }

    try:
        target = validate_native_request(request, config, "youtube")
        if transport is None:
            return result("adapter_unavailable")
        deadline = monotonic_clock() + request.wall_timeout_seconds
        uploads_id = "UU" + target.canonical_id[2:]
        response = transport(
            f"https://www.youtube.com/playlist?list={uploads_id}",
            deadline=deadline,
            maximum_bytes=1_048_576,
            item_limit=request.item_limit,
            network_request_limit=request.network_request_limit,
        )
        if not isinstance(response, dict):
            return result("validator_failed")
        usage = response.get("network_request_count")
        if isinstance(usage, bool) or not isinstance(usage, int) or usage < 1:
            return result("validator_failed")
        requests = usage
        if requests > request.network_request_limit:
            return result("network_budget_exhausted")
        if monotonic_clock() >= deadline:
            return result("wall_time_budget_exhausted")
        status = response.get("status")
        if status != 200:
            return result(
                {
                    401: "unauthorized_target",
                    403: "unauthorized_target",
                    404: "target_unavailable",
                    410: "target_unavailable",
                    429: "rate_limited",
                }.get(status, "source_error")
            )
        payload = response.get("payload")
        if len(json.dumps(payload, allow_nan=False).encode()) > 1_048_576:
            return result("validator_failed")
        if not isinstance(payload, dict):
            return result("validator_failed")
        if (
            payload.get("id") != uploads_id
            or payload.get("channel_id") != target.canonical_id
        ):
            return result("route_mismatch")
        entries = payload.get("entries")
        if not isinstance(entries, list) or len(entries) > request.item_limit:
            return result("validator_failed")
        seen = set()
        for video in entries:
            if not isinstance(video, dict):
                return result("validator_failed")
            native_id = video.get("id")
            if (
                not isinstance(native_id, str)
                or re.fullmatch(r"[A-Za-z0-9_-]{11}", native_id) is None
            ):
                return result("validator_failed")
            if video.get("channel_id") != target.canonical_id:
                return result("route_mismatch")
            title = video.get("title")
            if not isinstance(title, str) or not title.strip():
                return result("validator_failed")
            upload_date = video.get("upload_date")
            if (
                not isinstance(upload_date, str)
                or re.fullmatch(r"[0-9]{8}", upload_date) is None
            ):
                return result("validator_failed")
            published = date.fromisoformat(upload_date).isoformat()
            if (
                request.from_date <= published <= request.to_date
                and native_id not in seen
            ):
                items.append(
                    {
                        "video_id": native_id,
                        "url": f"https://www.youtube.com/watch?v={native_id}",
                        "title": title,
                        "description": str(video.get("description") or ""),
                        "channel_name": str(video.get("channel") or ""),
                        "date": published + "T00:00:00Z",
                        "media": [],
                    }
                )
                seen.add(native_id)
        diagnostics["pages"] = 1
        return result()
    except FollowCapabilityError as exc:
        return result(str(exc))
    except TimeoutError:
        return result("wall_time_budget_exhausted")
    except (TypeError, ValueError, OverflowError):
        return result("validator_failed")
