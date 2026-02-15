"""Location and timezone setup subroutes."""

from __future__ import annotations

from typing import Any, Callable, Dict, Optional

from fastapi import APIRouter


def create_setup_location_routes(
    *,
    search_locations: Callable[..., list[Dict[str, Any]]],
    get_default_location_for_timezone: Callable[[str | None], Dict[str, Any] | None],
    collect_timezone_options: Callable[[], list[Dict[str, Any]]],
    get_system_timezone_info: Callable[[], Dict[str, str]],
) -> APIRouter:
    router = APIRouter(tags=["setup"])

    @router.get("/locations/search")
    async def search_locations_endpoint(
        query: str = "",
        timezone: Optional[str] = None,
        limit: int = 10,
    ):
        return {"results": search_locations(query, timezone_hint=timezone, limit=limit)}

    @router.get("/locations/default")
    async def default_location_endpoint(timezone: Optional[str] = None):
        default = get_default_location_for_timezone(timezone)
        return {"result": default}

    @router.get("/data/timezones")
    async def timezone_options_endpoint():
        options = collect_timezone_options()
        system_tz = get_system_timezone_info().get("timezone")
        return {"timezones": options, "default_timezone": system_tz}

    return router
