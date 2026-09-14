"""Bounded native Reddit post routes, exercised through injected transports.

No transport is selected implicitly. Missing injection is an explicit unavailable
result; this module never falls through to topic search or an authenticated feed.
"""

from __future__ import annotations

import json
import re
import time
from datetime import UTC, datetime
from urllib.parse import urlencode

from .service_follow_capabilities import FollowCapabilityError, validate_native_request


def collect(request, config, *, transport=None, monotonic_clock=time.monotonic):
    items = []
    requests = 0
    route_name = f"reddit_{request.surface_kind}_posts"
    diagnostics = {"follow_route": route_name, "failure_stage": "native_follow_route"}

    def result(error=None):
        return {
            "items": items if error is None else [],
            "error_type": error,
            "_network_request_count": requests,
            "diagnostics": diagnostics,
        }

    try:
        target = validate_native_request(request, config, "reddit")
        if transport is None:
            return result("adapter_unavailable")
        deadline = monotonic_clock() + request.wall_timeout_seconds
        path = (
            f"r/{target.canonical_id}/new.json"
            if target.target_kind == "community"
            else f"user/{target.canonical_id}/submitted.json"
        )
        after = None
        cursors = set()
        seen = set()
        for page in range(min(10, request.network_request_limit)):
            if monotonic_clock() >= deadline:
                return result("wall_time_budget_exhausted")
            params = {"limit": request.item_limit - len(items)}
            if after is not None:
                params["after"] = after
            url = f"https://www.reddit.com/{path}?{urlencode(params)}"
            response = transport(
                url,
                deadline=deadline,
                maximum_bytes=1_048_576,
                network_request_limit=request.network_request_limit - requests,
            )
            if not isinstance(response, dict):
                return result("validator_failed")
            usage = response.get("network_request_count")
            if isinstance(usage, bool) or not isinstance(usage, int) or usage < 1:
                return result("validator_failed")
            requests += usage
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
            if not isinstance(payload, dict) or payload.get("kind") != "Listing":
                return result("validator_failed")
            data = payload.get("data")
            if not isinstance(data, dict) or not isinstance(data.get("children"), list):
                return result("validator_failed")
            if len(data["children"]) > params["limit"]:
                return result("validator_failed")
            for child in data["children"]:
                if (
                    not isinstance(child, dict)
                    or child.get("kind") != "t3"
                    or not isinstance(child.get("data"), dict)
                ):
                    return result("validator_failed")
                post = child["data"]
                native_id = post.get("id")
                if (
                    not isinstance(native_id, str)
                    or re.fullmatch(r"[a-z0-9]{1,32}", native_id) is None
                ):
                    return result("validator_failed")
                field = "subreddit" if target.target_kind == "community" else "author"
                if str(post.get(field, "")).casefold() != target.canonical_id:
                    return result("route_mismatch")
                permalink = post.get("permalink")
                if (
                    not isinstance(permalink, str)
                    or re.fullmatch(
                        r"/r/[A-Za-z0-9_]+/comments/"
                        + re.escape(native_id)
                        + r"/[A-Za-z0-9_-]*/?",
                        permalink,
                    )
                    is None
                ):
                    return result("route_mismatch")
                title = post.get("title")
                if not isinstance(title, str) or not title.strip():
                    return result("validator_failed")
                timestamp = post.get("created_utc")
                if isinstance(timestamp, bool) or not isinstance(
                    timestamp, (int, float)
                ):
                    return result("validator_failed")
                published = (
                    datetime.fromtimestamp(timestamp, UTC)
                    .isoformat()
                    .replace("+00:00", "Z")
                )
                if (
                    request.from_date <= published[:10] <= request.to_date
                    and native_id not in seen
                ):
                    items.append(
                        {
                            "id": native_id,
                            "url": "https://www.reddit.com" + permalink,
                            "title": title,
                            "selftext": str(post.get("selftext") or ""),
                            "subreddit": post.get("subreddit"),
                            "date": published,
                            "metadata": {"author": post.get("author")},
                        }
                    )
                    seen.add(native_id)
            after = data.get("after")
            diagnostics["pages"] = page + 1
            if after is None or len(items) >= request.item_limit:
                return result()
            if (
                not isinstance(after, str)
                or re.fullmatch(r"t3_[a-z0-9]{1,32}", after) is None
            ):
                return result("validator_failed")
            if after in cursors:
                return result("pagination_cycle")
            cursors.add(after)
        return result("pagination_bound_reached")
    except FollowCapabilityError as exc:
        return result(str(exc))
    except TimeoutError:
        return result("wall_time_budget_exhausted")
    except (TypeError, ValueError, OverflowError):
        return result("validator_failed")
