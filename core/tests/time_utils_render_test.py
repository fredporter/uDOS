from __future__ import annotations

from core.services.time_utils import render_utc_as_local


def test_render_utc_as_local_respects_timezone_conversion() -> None:
    payload = render_utc_as_local("2026-03-03T12:00:00Z", "Australia/Brisbane")

    assert payload["timezone"] == "Australia/Brisbane"
    assert payload["local_date"] == "2026-03-03"
    assert payload["local_clock"] == "22:00:00"
    assert payload["utc_time"] == "2026-03-03T12:00:00Z"


def test_render_utc_as_local_falls_back_to_system_timezone() -> None:
    payload = render_utc_as_local("2026-03-03T12:00:00Z", "Invalid/Timezone")

    assert payload["timezone"]
    assert payload["local_time"]
    assert payload["utc_time"] == "2026-03-03T12:00:00Z"
