"""Canonical Sonic API adapters for route payloads and query coercion."""

from __future__ import annotations

from typing import Any

from library.sonic.schemas import (
    DeviceQuery,
    ReflashPotential,
    USBBootSupport,
    normalize_usb_boot,
)


def build_device_query(
    *,
    vendor: str | None,
    reflash_potential: str | None,
    usb_boot: str | None,
    uefi_native: str | None,
    windows10_boot: str | None,
    media_mode: str | None,
    udos_launcher: str | None,
    year_min: int | None,
    year_max: int | None,
    limit: int,
    offset: int,
) -> DeviceQuery:
    reflash_enum = ReflashPotential(reflash_potential) if reflash_potential else None
    usb_enum = normalize_usb_boot(usb_boot)
    return DeviceQuery(
        vendor=vendor,
        reflash_potential=reflash_enum,
        usb_boot=usb_enum,
        uefi_native=uefi_native,
        windows10_boot=windows10_boot,
        media_mode=media_mode,
        udos_launcher=udos_launcher,
        year_min=year_min,
        year_max=year_max,
        limit=limit,
        offset=offset,
    )


def to_device_payload(device: Any) -> dict[str, Any]:
    if hasattr(device, "to_dict"):
        payload = dict(device.to_dict())
    elif isinstance(device, dict):
        payload = dict(device)
    else:
        payload = {"id": str(device)}
    payload["usb_boot"] = _normalize_usb_boot_value(payload.get("usb_boot"))
    return payload


def to_device_list_payload(*, devices: list[Any], limit: int, offset: int) -> dict[str, Any]:
    mapped = [to_device_payload(device) for device in devices]
    return {
        "total": len(mapped),
        "limit": limit,
        "offset": offset,
        "devices": mapped,
    }


def to_stats_payload(stats: Any) -> dict[str, Any]:
    return {
        "total_devices": int(getattr(stats, "total_devices", 0)),
        "by_vendor": dict(getattr(stats, "by_vendor", {})),
        "by_reflash_potential": dict(getattr(stats, "by_reflash_potential", {})),
        "by_windows10_boot": dict(getattr(stats, "by_windows10_boot", {})),
        "by_media_mode": dict(getattr(stats, "by_media_mode", {})),
        "usb_boot_capable": int(getattr(stats, "usb_boot_capable", 0)),
        "uefi_native_capable": int(getattr(stats, "uefi_native_capable", 0)),
        "last_updated": getattr(stats, "last_updated", None),
    }


def to_sync_status_payload(status: Any) -> dict[str, Any]:
    return {
        "last_sync": getattr(status, "last_sync", None),
        "db_path": getattr(status, "db_path", ""),
        "db_exists": bool(getattr(status, "db_exists", False)),
        "record_count": int(getattr(status, "record_count", 0)),
        "schema_version": getattr(status, "schema_version", None),
        "needs_rebuild": bool(getattr(status, "needs_rebuild", False)),
        "errors": list(getattr(status, "errors", [])),
        "seed_db_path": getattr(status, "seed_db_path", None),
        "user_db_path": getattr(status, "user_db_path", None),
        "seed_record_count": getattr(status, "seed_record_count", None),
        "user_record_count": getattr(status, "user_record_count", None),
        "current_machine_registered": getattr(status, "current_machine_registered", None),
    }


def _normalize_usb_boot_value(value: Any) -> str | None:
    normalized = normalize_usb_boot(value)
    if isinstance(normalized, USBBootSupport):
        return normalized.value
    if value is None:
        return None
    return str(value)
