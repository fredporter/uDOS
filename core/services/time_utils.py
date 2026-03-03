"""Canonical time helpers for UTC timestamps."""

from __future__ import annotations

from datetime import UTC, datetime, timezone
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


def utc_now() -> datetime:
    """Return timezone-aware UTC datetime."""
    return datetime.now(UTC)


def utc_now_iso() -> str:
    """Return timezone-aware UTC ISO timestamp."""
    return utc_now().isoformat()


def utc_now_iso_z() -> str:
    """Return UTC ISO timestamp with Z suffix and no microseconds."""
    return utc_now().replace(microsecond=0).isoformat().replace("+00:00", "Z")


def utc_day_string() -> str:
    return utc_now().strftime("%Y-%m-%d")


def utc_compact_timestamp() -> str:
    return utc_now().strftime("%Y%m%d-%H%M%S")


def utc_filename_timestamp() -> str:
    return utc_now().strftime("%Y-%m-%d_%H%M%S")


def utc_from_timestamp(value: float) -> datetime:
    return datetime.fromtimestamp(value, tz=timezone.utc)


def parse_utc_datetime(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def resolve_timezone(timezone_name: str | None = None) -> tuple[Any, str]:
    if timezone_name:
        try:
            return ZoneInfo(timezone_name), timezone_name
        except ZoneInfoNotFoundError:
            pass
    local_now = datetime.now().astimezone()
    local_tz = local_now.tzinfo or UTC
    resolved_name = getattr(local_tz, "key", None) or local_tz.tzname(local_now) or "UTC"
    return local_tz, resolved_name


def render_utc_as_local(
    value: str | datetime | None = None,
    timezone_name: str | None = None,
    *,
    include_utc: bool = True,
) -> dict[str, str]:
    tz, resolved_name = resolve_timezone(timezone_name)
    source = utc_now() if value is None else (parse_utc_datetime(value) if isinstance(value, str) else value)
    localized = source.astimezone(tz)
    payload = {
        "timezone": resolved_name,
        "label": localized.tzname() or resolved_name,
        "offset": localized.strftime("%z"),
        "local_time": localized.isoformat(),
        "local_date": localized.strftime("%Y-%m-%d"),
        "local_clock": localized.strftime("%H:%M:%S"),
        "local_display": localized.strftime("%Y-%m-%d %H:%M"),
    }
    if include_utc:
        payload["utc_time"] = source.astimezone(UTC).isoformat().replace("+00:00", "Z")
    return payload
