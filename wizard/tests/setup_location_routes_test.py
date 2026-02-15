from fastapi import FastAPI
from fastapi.testclient import TestClient

from wizard.routes.setup_location_routes import create_setup_location_routes


def _build_app(calls):
    def search_locations(query, timezone_hint=None, limit=10):
        calls["search"] = {
            "query": query,
            "timezone_hint": timezone_hint,
            "limit": limit,
        }
        return [{"id": "loc-1"}]

    router = create_setup_location_routes(
        search_locations=search_locations,
        get_default_location_for_timezone=lambda timezone: {"id": "loc-default", "timezone": timezone},
        collect_timezone_options=lambda: [{"timezone": "UTC", "label": "UTC"}],
        get_system_timezone_info=lambda: {"timezone": "UTC", "local_time": "2026-01-01 12:00"},
    )
    app = FastAPI()
    app.include_router(router, prefix="/api/setup")
    return app


def test_search_locations_endpoint_passes_arguments():
    calls = {}
    app = _build_app(calls)
    client = TestClient(app)

    res = client.get("/api/setup/locations/search", params={"query": "ny", "timezone": "UTC", "limit": 5})
    assert res.status_code == 200
    assert calls["search"] == {"query": "ny", "timezone_hint": "UTC", "limit": 5}


def test_default_and_timezone_endpoints():
    calls = {}
    app = _build_app(calls)
    client = TestClient(app)

    res_default = client.get("/api/setup/locations/default", params={"timezone": "UTC"})
    assert res_default.status_code == 200
    assert res_default.json()["result"]["id"] == "loc-default"

    res_tz = client.get("/api/setup/data/timezones")
    assert res_tz.status_code == 200
    payload = res_tz.json()
    assert payload["default_timezone"] == "UTC"
    assert payload["timezones"][0]["timezone"] == "UTC"
