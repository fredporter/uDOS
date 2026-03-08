"""Sonic integration loader for the external `uDOS-sonic` repository."""

from __future__ import annotations

import importlib
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Dict, Optional

from core.services.external_repo_service import ensure_sonic_python_paths, resolve_sonic_repo_root


class _CompatSonicAPI:
    def __init__(self, repo_root: Path):
        service_mod = importlib.import_module("installers.usb.service")
        self._service = service_mod.SonicService(repo_root=repo_root)

    def health(self) -> dict[str, Any]:
        health = self._service.get_health()
        return {"status": "ok" if health.get("ok") else "warning", **health}

    def get_schema(self) -> dict[str, Any]:
        schema = self._service.get_schema()
        return schema.get("schema") if schema.get("ok") else schema

    def query_devices(self, query: Any) -> list[dict[str, Any]]:
        result = self._service.list_devices(
            vendor=getattr(query, "vendor", None),
            reflash_potential=getattr(query, "reflash_potential", None),
            usb_boot=getattr(query, "usb_boot", None),
            uefi_native=getattr(query, "uefi_native", None),
            limit=int(getattr(query, "limit", 100)),
            offset=int(getattr(query, "offset", 0)),
        )
        return list(result.get("items") or [])

    def get_device(self, device_id: str) -> dict[str, Any] | None:
        result = self._service.list_devices(limit=10000, offset=0)
        return next((item for item in result.get("items") or [] if item.get("id") == device_id), None)

    def get_stats(self) -> dict[str, Any]:
        items = list((self._service.list_devices(limit=10000, offset=0).get("items") or []))
        by_vendor: dict[str, int] = {}
        by_reflash: dict[str, int] = {}
        by_windows: dict[str, int] = {}
        by_media: dict[str, int] = {}
        usb_boot_capable = 0
        uefi_native_capable = 0
        for item in items:
            vendor = str(item.get("vendor") or "unknown")
            by_vendor[vendor] = by_vendor.get(vendor, 0) + 1
            reflash = str(item.get("reflash_potential") or "unknown")
            by_reflash[reflash] = by_reflash.get(reflash, 0) + 1
            windows = str(item.get("windows10_boot") or "unknown")
            by_windows[windows] = by_windows.get(windows, 0) + 1
            media = str(item.get("media_mode") or "unknown")
            by_media[media] = by_media.get(media, 0) + 1
            if str(item.get("usb_boot") or "").lower() not in {"", "none", "unknown"}:
                usb_boot_capable += 1
            if str(item.get("uefi_native") or "").lower() == "works":
                uefi_native_capable += 1
        return {
            "total_devices": len(items),
            "by_vendor": by_vendor,
            "by_reflash_potential": by_reflash,
            "by_windows10_boot": by_windows,
            "by_media_mode": by_media,
            "usb_boot_capable": usb_boot_capable,
            "uefi_native_capable": uefi_native_capable,
            "last_updated": None,
        }

    def list_flash_packs(self) -> list[dict[str, Any]]:
        packs_root = self._service.repo_root / "config" / "flash-packs"
        if not packs_root.exists():
            return []
        packs: list[dict[str, Any]] = []
        for path in sorted(packs_root.glob("*.json")):
            packs.append({"id": path.stem, "path": str(path)})
        return packs

    def get_flash_pack(self, pack_id: str) -> dict[str, Any] | None:
        path = self._service.repo_root / "config" / "flash-packs" / f"{pack_id}.json"
        if not path.exists():
            return None
        import json

        return json.loads(path.read_text(encoding="utf-8"))


class _CompatSonicSync:
    def __init__(self, repo_root: Path):
        service_mod = importlib.import_module("installers.usb.service")
        self._service = service_mod.SonicService(repo_root=repo_root)

    def get_status(self) -> dict[str, Any]:
        status = self._service.get_db_status()
        paths = status.get("paths") or {}
        summary = status.get("summary") or {}
        return {
            "last_sync": None,
            "db_path": paths.get("legacy_db", ""),
            "db_exists": bool(status.get("artifacts", {}).get("legacy_db_present", False)),
            "record_count": int(summary.get("device_count", 0)),
            "schema_version": None,
            "needs_rebuild": not bool(status.get("artifacts", {}).get("seed_db_present", False)),
            "errors": [] if status.get("ok") else [status.get("error", "unknown sync error")],
            "seed_db_path": paths.get("seed_db"),
            "user_db_path": paths.get("user_db"),
            "seed_record_count": summary.get("device_count"),
            "user_record_count": None,
            "current_machine_registered": None,
        }

    def rebuild_database(self, force: bool = False) -> dict[str, Any]:
        if force:
            self._service._ensure_seed_catalog(force=True)  # noqa: SLF001
        else:
            self._service._ensure_seed_catalog(force=False)  # noqa: SLF001
        return {"status": "ok", "message": "database rebuilt", "force": force, "db": self.get_status()}

    def export_to_csv(self, output_path: Path | None = None) -> dict[str, Any]:
        export = self._service.export_db()
        if output_path is not None:
            import csv

            items = export.get("items") or []
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with output_path.open("w", encoding="utf-8", newline="") as handle:
                if items:
                    writer = csv.DictWriter(handle, fieldnames=sorted(items[0].keys()))
                    writer.writeheader()
                    writer.writerows(items)
                else:
                    handle.write("")
        return {"status": "ok", "output_path": str(output_path) if output_path else None, "count": export.get("count", 0)}

    def bootstrap_current_machine(self, overwrite: bool = True) -> dict[str, Any]:
        result = self._service.bootstrap_current_machine()
        record = result.get("record") or {}
        return {
            "status": "ok" if result.get("ok") else "error",
            "device_id": record.get("id"),
            "overwrite": overwrite,
            "record": record,
        }


class SonicPluginLoader:
    """Dynamic loader for Sonic components from the external repo."""

    def __init__(self, repo_root: Optional[Path] = None):
        self.repo_root = Path(repo_root or Path(__file__).resolve().parents[1])
        self.sonic_repo_root = ensure_sonic_python_paths(self.repo_root)

    def load_schemas(self):
        return SimpleNamespace()

    def load_api(self):
        return SimpleNamespace(get_sonic_service=lambda: _CompatSonicAPI(self.sonic_repo_root))

    def load_sync(self):
        return SimpleNamespace(
            DeviceDatabaseSync=_CompatSonicSync,
            get_sync_service=lambda: _CompatSonicSync(self.sonic_repo_root),
        )

    def load_all(self) -> Dict[str, Any]:
        return {
            "schemas": self.load_schemas(),
            "api": self.load_api(),
            "sync": self.load_sync(),
            "loader": self,
        }

    def get_plugin_info(self) -> Dict[str, Any]:
        return {
            "installed": self.sonic_repo_root.exists(),
            "path": str(self.sonic_repo_root),
        }

    def is_available(self) -> bool:
        try:
            importlib.import_module("installers.usb.service")
            return True
        except ImportError:
            return False


def get_sonic_loader(repo_root: Optional[Path] = None) -> SonicPluginLoader:
    return SonicPluginLoader(repo_root)


def load_sonic_plugin(repo_root: Optional[Path] = None) -> Dict[str, Any]:
    return get_sonic_loader(repo_root).load_all()


__all__ = ["SonicPluginLoader", "get_sonic_loader", "load_sonic_plugin"]
