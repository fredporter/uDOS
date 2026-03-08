"""Canonical Sonic API adapters for Wizard route payloads."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

_USB_BOOT_ALIASES = {
    "yes": "native",
    "native": "native",
    "uefi_only": "uefi_only",
    "legacy_only": "legacy_only",
    "mixed": "mixed",
    "none": "none",
    "no": "none",
}


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
) -> Any:
    return SimpleNamespace(
        vendor=vendor,
        reflash_potential=reflash_potential,
        usb_boot=_normalize_usb_boot_value(usb_boot),
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
    elif hasattr(device, "__dict__") and not isinstance(device, dict):
        payload = dict(vars(device))
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
    if isinstance(stats, dict):
        return {
            "total_devices": int(stats.get("total_devices", 0)),
            "by_vendor": dict(stats.get("by_vendor", {})),
            "by_reflash_potential": dict(stats.get("by_reflash_potential", {})),
            "by_windows10_boot": dict(stats.get("by_windows10_boot", {})),
            "by_media_mode": dict(stats.get("by_media_mode", {})),
            "usb_boot_capable": int(stats.get("usb_boot_capable", 0)),
            "uefi_native_capable": int(stats.get("uefi_native_capable", 0)),
            "last_updated": stats.get("last_updated"),
        }
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
    if isinstance(status, dict):
        return {
            "last_sync": status.get("last_sync"),
            "db_path": status.get("db_path", ""),
            "db_exists": bool(status.get("db_exists", False)),
            "record_count": int(status.get("record_count", 0)),
            "schema_version": status.get("schema_version"),
            "needs_rebuild": bool(status.get("needs_rebuild", False)),
            "errors": list(status.get("errors", [])),
            "seed_db_path": status.get("seed_db_path"),
            "user_db_path": status.get("user_db_path"),
            "seed_record_count": status.get("seed_record_count"),
            "user_record_count": status.get("user_record_count"),
            "current_machine_registered": status.get("current_machine_registered"),
        }
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
    if value is None:
        return None
    normalized = _USB_BOOT_ALIASES.get(str(value).strip().lower())
    return normalized if normalized is not None else str(value)
