"""Shared Sonic device storage and bootstrap services."""

from __future__ import annotations

import json
import shutil
import sqlite3
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from core.services.external_repo_service import resolve_sonic_repo_root
from core.services.path_service import get_repo_root
from core.services.system_capability_service import get_system_capability_service


SONIC_TEMPLATE_DEFAULTS = {
    "settings_template_md": "core/framework/seed/bank/templates/submissions/SONIC-DEVICE-SETTINGS-template.md",
    "installers_template_md": "core/framework/seed/bank/templates/submissions/SONIC-DEVICE-INSTALLERS-template.md",
    "containers_template_md": "core/framework/seed/bank/templates/submissions/SONIC-DEVICE-CONTAINERS-template.md",
    "drivers_template_md": "core/framework/seed/bank/templates/submissions/SONIC-DEVICE-DRIVERS-template.md",
}

DEVICE_COLUMNS = [
    "id",
    "vendor",
    "model",
    "variant",
    "year",
    "cpu",
    "gpu",
    "ram_gb",
    "storage_gb",
    "bios",
    "secure_boot",
    "tpm",
    "usb_boot",
    "uefi_native",
    "reflash_potential",
    "methods",
    "notes",
    "sources",
    "last_seen",
    "windows10_boot",
    "media_mode",
    "udos_launcher",
    "wizard_profile",
    "media_launcher",
    "settings_template_md",
    "installers_template_md",
    "containers_template_md",
    "drivers_template_md",
]

USER_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS user_devices (
  id TEXT PRIMARY KEY,
  vendor TEXT NOT NULL,
  model TEXT NOT NULL,
  variant TEXT,
  year INTEGER,
  cpu TEXT,
  gpu TEXT,
  ram_gb INTEGER,
  storage_gb INTEGER,
  bios TEXT,
  secure_boot TEXT,
  tpm TEXT,
  usb_boot TEXT,
  uefi_native TEXT,
  reflash_potential TEXT,
  methods TEXT,
  notes TEXT,
  sources TEXT,
  last_seen TEXT,
  windows10_boot TEXT,
  media_mode TEXT,
  udos_launcher TEXT,
  wizard_profile TEXT,
  media_launcher TEXT,
  settings_template_md TEXT,
  installers_template_md TEXT,
  containers_template_md TEXT,
  drivers_template_md TEXT,
  local_origin TEXT,
  local_enabled INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
"""


@dataclass(frozen=True)
class SonicRuntimePaths:
    seed_db_path: Path
    user_db_path: Path
    legacy_db_path: Path
    sql_source: Path
    schema_path: Path

    def to_dict(self) -> dict[str, str]:
        return {
            "seed_db_path": str(self.seed_db_path),
            "user_db_path": str(self.user_db_path),
            "legacy_db_path": str(self.legacy_db_path),
            "sql_source": str(self.sql_source),
            "schema_path": str(self.schema_path),
        }


class SonicDeviceStorageService:
    """Canonical seeded + local Sonic device runtime."""

    def __init__(self, repo_root: Path | None = None) -> None:
        self.repo_root = Path(repo_root or get_repo_root())
        self.sonic_root = resolve_sonic_repo_root(self.repo_root)
        self.dataset_root = self.sonic_root / "datasets"
        self.memory_root = self.repo_root / "memory" / "sonic"
        self.submissions_root = self.memory_root / "submissions"
        self.paths = SonicRuntimePaths(
            seed_db_path=self.memory_root / "seed" / "sonic-devices.seed.db",
            user_db_path=self.memory_root / "user" / "sonic-devices.user.db",
            legacy_db_path=self.memory_root / "sonic-devices.db",
            sql_source=self.dataset_root / "sonic-devices.sql",
            schema_path=self.dataset_root / "sonic-devices.schema.json",
        )

    def runtime_contract(self) -> dict[str, Any]:
        self.ensure_user_runtime()
        seed_exists = self.paths.seed_db_path.exists()
        user_exists = self.paths.user_db_path.exists()
        seed_count = self._count_rows(self.paths.seed_db_path, "devices") if seed_exists else 0
        user_count = self._count_rows(self.paths.user_db_path, "user_devices") if user_exists else 0
        current_machine_id = self._current_machine_id()
        return {
            "paths": self.paths.to_dict(),
            "seed_catalog": {
                "exists": seed_exists,
                "record_count": seed_count,
            },
            "user_catalog": {
                "exists": user_exists,
                "record_count": user_count,
                "current_machine_id": current_machine_id,
                "current_machine_registered": self.has_user_device(current_machine_id),
            },
            "submissions": self.submission_runtime_contract(),
        }

    def submission_runtime_contract(self) -> dict[str, Any]:
        pending = self.list_submissions(status="pending")
        approved = self.list_submissions(status="approved")
        rejected = self.list_submissions(status="rejected")
        return {
            "root": str(self.submissions_root),
            "pending_count": len(pending),
            "approved_count": len(approved),
            "rejected_count": len(rejected),
        }

    def ensure_user_runtime(self) -> None:
        self.paths.user_db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(str(self.paths.user_db_path)) as conn:
            conn.execute(USER_TABLE_SQL)
            conn.commit()

    def ensure_seed_runtime(self, *, force: bool = False) -> dict[str, Any]:
        if not self.paths.sql_source.exists():
            return {
                "status": "error",
                "message": f"SQL source not found: {self.paths.sql_source}",
            }

        self.paths.seed_db_path.parent.mkdir(parents=True, exist_ok=True)
        if self.paths.seed_db_path.exists() and not force:
            return {
                "status": "skip",
                "message": "Seed catalog is up to date",
                "db_path": str(self.paths.seed_db_path),
                "record_count": self._count_rows(self.paths.seed_db_path, "devices"),
            }

        if self.paths.seed_db_path.exists():
            self.paths.seed_db_path.unlink()

        with sqlite3.connect(str(self.paths.seed_db_path)) as conn:
            conn.executescript(self.paths.sql_source.read_text(encoding="utf-8"))
            conn.commit()

        self._refresh_legacy_bridge()
        return {
            "status": "ok",
            "message": "Seed catalog rebuilt",
            "db_path": str(self.paths.seed_db_path),
            "record_count": self._count_rows(self.paths.seed_db_path, "devices"),
        }

    def export_seed_to_csv(self, output_path: Path | None = None) -> dict[str, Any]:
        if output_path is None:
            output_path = self.dataset_root / "sonic-devices.csv"
        if not self.paths.seed_db_path.exists():
            return {"status": "error", "message": "Seed catalog does not exist"}

        with sqlite3.connect(str(self.paths.seed_db_path)) as conn:
            cursor = conn.execute("SELECT * FROM devices")
            columns = [item[0] for item in cursor.description]
            rows = cursor.fetchall()

        import csv

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(columns)
            writer.writerows(rows)

        return {
            "status": "ok",
            "message": "Seed catalog exported",
            "output_path": str(output_path),
            "record_count": len(rows),
        }

    def has_user_device(self, device_id: str) -> bool:
        self.ensure_user_runtime()
        with sqlite3.connect(str(self.paths.user_db_path)) as conn:
            row = conn.execute(
                "SELECT id FROM user_devices WHERE id = ? AND local_enabled = 1",
                (device_id,),
            ).fetchone()
        return row is not None

    def list_devices(
        self,
        *,
        vendor: str | None = None,
        reflash_potential: str | None = None,
        usb_boot: str | None = None,
        uefi_native: str | None = None,
        windows10_boot: str | None = None,
        media_mode: str | None = None,
        udos_launcher: str | None = None,
        year_min: int | None = None,
        year_max: int | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        records = self._merged_device_rows()
        records = self._apply_filters(
            records,
            vendor=vendor,
            reflash_potential=reflash_potential,
            usb_boot=usb_boot,
            uefi_native=uefi_native,
            windows10_boot=windows10_boot,
            media_mode=media_mode,
            udos_launcher=udos_launcher,
            year_min=year_min,
            year_max=year_max,
        )
        return records[offset : offset + limit]

    def get_device(self, device_id: str) -> dict[str, Any] | None:
        for record in self._merged_device_rows():
            if str(record.get("id")) == device_id:
                return record
        return None

    def get_stats(self) -> dict[str, Any]:
        records = self._merged_device_rows()
        by_vendor: dict[str, int] = {}
        by_reflash: dict[str, int] = {}
        by_windows10: dict[str, int] = {}
        by_media: dict[str, int] = {}
        usb_boot_capable = 0
        uefi_native_capable = 0
        for record in records:
            vendor = str(record.get("vendor") or "unknown")
            by_vendor[vendor] = by_vendor.get(vendor, 0) + 1
            reflash = str(record.get("reflash_potential") or "unknown")
            by_reflash[reflash] = by_reflash.get(reflash, 0) + 1
            windows10_boot = str(record.get("windows10_boot") or "unknown")
            by_windows10[windows10_boot] = by_windows10.get(windows10_boot, 0) + 1
            media_mode = str(record.get("media_mode") or "unknown")
            by_media[media_mode] = by_media.get(media_mode, 0) + 1
            if str(record.get("usb_boot") or "none") != "none":
                usb_boot_capable += 1
            if str(record.get("uefi_native") or "unknown") != "unknown":
                uefi_native_capable += 1
        return {
            "total_devices": len(records),
            "by_vendor": by_vendor,
            "by_reflash_potential": by_reflash,
            "by_windows10_boot": by_windows10,
            "by_media_mode": by_media,
            "usb_boot_capable": usb_boot_capable,
            "uefi_native_capable": uefi_native_capable,
            "last_updated": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        }

    def register_current_machine(self, *, overwrite: bool = True) -> dict[str, Any]:
        self.ensure_user_runtime()
        capability = get_system_capability_service(self.repo_root).measure()
        now = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        machine_id = self._current_machine_id(capability.hostname)
        existing = self._read_user_device(machine_id)
        existing_refs = existing or {}
        record = {
            "id": machine_id,
            "vendor": capability.system or "Local",
            "model": capability.hostname or "Current Machine",
            "variant": capability.arch,
            "year": datetime.now(UTC).year,
            "cpu": capability.processor or capability.arch,
            "gpu": "unknown",
            "ram_gb": int(round(capability.ram_gb)),
            "storage_gb": int(round(capability.storage_total_gb)),
            "bios": "uefi" if capability.uefi_native else "legacy",
            "secure_boot": "unknown",
            "tpm": "unknown",
            "usb_boot": "native",
            "uefi_native": "works" if capability.uefi_native else "unknown",
            "reflash_potential": "unknown",
            "methods": json.dumps(["local-bootstrap", "capability-probe"]),
            "notes": "Local machine bootstrap record managed by uDOS core.",
            "sources": json.dumps(["local-system-probe"]),
            "last_seen": datetime.now(UTC).date().isoformat(),
            "windows10_boot": "unknown",
            "media_mode": "unknown",
            "udos_launcher": "basic" if not capability.headless else "none",
            "wizard_profile": "local-machine",
            "media_launcher": None,
            "settings_template_md": existing_refs.get("settings_template_md") or SONIC_TEMPLATE_DEFAULTS["settings_template_md"],
            "installers_template_md": existing_refs.get("installers_template_md") or SONIC_TEMPLATE_DEFAULTS["installers_template_md"],
            "containers_template_md": existing_refs.get("containers_template_md") or SONIC_TEMPLATE_DEFAULTS["containers_template_md"],
            "drivers_template_md": existing_refs.get("drivers_template_md") or SONIC_TEMPLATE_DEFAULTS["drivers_template_md"],
            "local_origin": "core-capability-probe",
            "local_enabled": 1,
            "created_at": existing_refs.get("created_at") or now,
            "updated_at": now,
        }
        self._upsert_user_device(record, overwrite=overwrite)
        self._refresh_legacy_bridge()
        return {
            "status": "ok",
            "message": "Current machine registered in Sonic user catalog",
            "device_id": machine_id,
            "record": self.get_device(machine_id),
        }

    def import_user_csv(self, csv_path: Path) -> dict[str, Any]:
        if not csv_path.exists():
            return {"status": "error", "message": f"CSV not found: {csv_path}"}
        self.ensure_user_runtime()
        import csv

        inserted = 0
        updated = 0
        with csv_path.open("r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                device_id = str(row.get("id") or "").strip()
                if not device_id:
                    continue
                payload = {
                    column: row.get(column)
                    for column in DEVICE_COLUMNS
                    if column in row
                }
                payload["id"] = device_id
                payload["local_origin"] = "user-import"
                payload["local_enabled"] = 1
                payload["created_at"] = datetime.now(UTC).isoformat().replace("+00:00", "Z")
                payload["updated_at"] = payload["created_at"]
                exists = self.has_user_device(device_id)
                self._upsert_user_device(payload, overwrite=True)
                if exists:
                    updated += 1
                else:
                    inserted += 1
        self._refresh_legacy_bridge()
        return {
            "status": "ok",
            "message": "User catalog import successful",
            "inserted": inserted,
            "updated": updated,
        }

    def list_submissions(self, *, status: str | None = None) -> list[dict[str, Any]]:
        statuses = [status] if status else ["pending", "approved", "rejected"]
        records: list[dict[str, Any]] = []
        for item_status in statuses:
            for path in sorted(self._submission_dir(item_status).glob("*.json")):
                payload = json.loads(path.read_text(encoding="utf-8"))
                payload["status"] = item_status
                payload["path"] = str(path)
                records.append(payload)
        return sorted(
            records,
            key=lambda item: (
                str(item.get("updated_at") or item.get("submitted_at") or ""),
                str(item.get("submission_id") or ""),
            ),
            reverse=True,
        )

    def submit_device_submission(
        self, payload: dict[str, Any], *, submitter: str | None = None
    ) -> dict[str, Any]:
        normalized = self._normalize_submission_payload(payload)
        submission_id = str(normalized["id"])
        now = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        record = {
            "submission_id": submission_id,
            "status": "pending",
            "submitted_at": now,
            "updated_at": now,
            "submitter": submitter or "local-user",
            "device": normalized,
        }
        path = self._submission_path("pending", submission_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(record, indent=2), encoding="utf-8")
        return {
            "status": "ok",
            "message": "Device submission queued for contributor review",
            "submission": record,
        }

    def approve_submission(
        self, submission_id: str, *, approved_by: str | None = None
    ) -> dict[str, Any]:
        record = self._load_submission("pending", submission_id)
        if record is None:
            return {"status": "error", "message": f"Pending submission not found: {submission_id}"}

        now = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        device_payload = self._submission_device_to_user_record(record["device"], updated_at=now)
        self._upsert_user_device(device_payload, overwrite=True)
        self._refresh_legacy_bridge()

        approved = {
            **record,
            "status": "approved",
            "updated_at": now,
            "approved_at": now,
            "approved_by": approved_by or "contributor",
        }
        self._write_submission("approved", submission_id, approved)
        self._delete_submission("pending", submission_id)
        return {
            "status": "ok",
            "message": "Submission approved and merged into the local user catalog",
            "submission": approved,
            "device": self.get_device(submission_id),
        }

    def reject_submission(
        self,
        submission_id: str,
        *,
        rejected_by: str | None = None,
        reason: str | None = None,
    ) -> dict[str, Any]:
        record = self._load_submission("pending", submission_id)
        if record is None:
            return {"status": "error", "message": f"Pending submission not found: {submission_id}"}

        now = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        rejected = {
            **record,
            "status": "rejected",
            "updated_at": now,
            "rejected_at": now,
            "rejected_by": rejected_by or "contributor",
            "reason": reason or "",
        }
        self._write_submission("rejected", submission_id, rejected)
        self._delete_submission("pending", submission_id)
        return {
            "status": "ok",
            "message": "Submission rejected",
            "submission": rejected,
        }

    def _refresh_legacy_bridge(self) -> None:
        self.paths.legacy_db_path.parent.mkdir(parents=True, exist_ok=True)
        if self.paths.seed_db_path.exists():
            shutil.copy2(self.paths.seed_db_path, self.paths.legacy_db_path)
        else:
            with sqlite3.connect(str(self.paths.legacy_db_path)) as conn:
                conn.execute("DROP TABLE IF EXISTS devices")
                conn.execute(
                    """
                    CREATE TABLE devices (
                      id TEXT PRIMARY KEY,
                      vendor TEXT NOT NULL,
                      model TEXT NOT NULL,
                      variant TEXT,
                      year INTEGER,
                      cpu TEXT,
                      gpu TEXT,
                      ram_gb INTEGER,
                      storage_gb INTEGER,
                      bios TEXT,
                      secure_boot TEXT,
                      tpm TEXT,
                      usb_boot TEXT,
                      uefi_native TEXT,
                      reflash_potential TEXT,
                      methods TEXT,
                      notes TEXT,
                      sources TEXT,
                      last_seen TEXT,
                      windows10_boot TEXT,
                      media_mode TEXT,
                      udos_launcher TEXT,
                      wizard_profile TEXT,
                      media_launcher TEXT,
                      settings_template_md TEXT,
                      installers_template_md TEXT,
                      containers_template_md TEXT,
                      drivers_template_md TEXT
                    )
                    """
                )
                conn.commit()
        user_rows = self._read_rows(self.paths.user_db_path, "user_devices")
        if not user_rows:
            return
        with sqlite3.connect(str(self.paths.legacy_db_path)) as conn:
            existing_columns = {
                row[1]
                for row in conn.execute("PRAGMA table_info(devices)").fetchall()
            }
            for row in user_rows:
                if int(row.get("local_enabled") or 0) != 1:
                    continue
                payload = {
                    column: row.get(column)
                    for column in DEVICE_COLUMNS
                    if column in existing_columns
                }
                columns = list(payload.keys())
                placeholders = ", ".join("?" for _ in columns)
                assignments = ", ".join(f"{column}=excluded.{column}" for column in columns if column != "id")
                conn.execute(
                    f"""
                    INSERT INTO devices ({", ".join(columns)})
                    VALUES ({placeholders})
                    ON CONFLICT(id) DO UPDATE SET {assignments}
                    """,
                    tuple(payload[column] for column in columns),
                )
            conn.commit()

    def _submission_dir(self, status: str) -> Path:
        return self.submissions_root / status

    def _submission_path(self, status: str, submission_id: str) -> Path:
        return self._submission_dir(status) / f"{submission_id}.json"

    def _load_submission(self, status: str, submission_id: str) -> dict[str, Any] | None:
        path = self._submission_path(status, submission_id)
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def _write_submission(self, status: str, submission_id: str, payload: dict[str, Any]) -> None:
        path = self._submission_path(status, submission_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _delete_submission(self, status: str, submission_id: str) -> None:
        path = self._submission_path(status, submission_id)
        if path.exists():
            path.unlink()

    def _count_rows(self, db_path: Path, table: str) -> int:
        with sqlite3.connect(str(db_path)) as conn:
            row = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()
        return int(row[0]) if row else 0

    def _read_rows(self, db_path: Path, table: str) -> list[dict[str, Any]]:
        if not db_path.exists():
            return []
        with sqlite3.connect(str(db_path)) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(f"SELECT * FROM {table}").fetchall()
        return [dict(row) for row in rows]

    def _merged_device_rows(self) -> list[dict[str, Any]]:
        seed_rows = {row["id"]: self._normalize_row(row, source="seed") for row in self._read_rows(self.paths.seed_db_path, "devices")}
        user_rows = {
            row["id"]: self._normalize_row(row, source="user")
            for row in self._read_rows(self.paths.user_db_path, "user_devices")
            if int(row.get("local_enabled") or 0) == 1
        }
        merged = dict(seed_rows)
        merged.update(user_rows)
        return sorted(
            merged.values(),
            key=lambda item: (
                str(item.get("vendor") or ""),
                str(item.get("model") or ""),
                str(item.get("id") or ""),
            ),
        )

    def _normalize_row(self, row: dict[str, Any], *, source: str) -> dict[str, Any]:
        payload = {column: row.get(column) for column in DEVICE_COLUMNS}
        payload["methods"] = self._normalize_list(payload.get("methods"))
        payload["sources"] = self._normalize_list(payload.get("sources"))
        payload["catalog_source"] = source
        return payload

    def _normalize_list(self, value: Any) -> list[str] | None:
        if value is None or value == "":
            return None
        if isinstance(value, list):
            return [str(item) for item in value]
        try:
            parsed = json.loads(value)
        except Exception:
            return [str(value)]
        if isinstance(parsed, list):
            return [str(item) for item in parsed]
        return [str(value)]

    def _read_user_device(self, device_id: str) -> dict[str, Any] | None:
        self.ensure_user_runtime()
        with sqlite3.connect(str(self.paths.user_db_path)) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM user_devices WHERE id = ?",
                (device_id,),
            ).fetchone()
        return dict(row) if row else None

    def _upsert_user_device(self, payload: dict[str, Any], *, overwrite: bool) -> None:
        self.ensure_user_runtime()
        existing = self._read_user_device(str(payload["id"]))
        if existing and not overwrite:
            return
        values = {key: payload.get(key) for key in DEVICE_COLUMNS}
        values["local_origin"] = payload.get("local_origin")
        values["local_enabled"] = int(payload.get("local_enabled", 1))
        values["created_at"] = payload.get("created_at")
        values["updated_at"] = payload.get("updated_at")
        columns = list(values.keys())
        placeholders = ", ".join("?" for _ in columns)
        assignments = ", ".join(f"{column}=excluded.{column}" for column in columns if column not in {"id", "created_at"})
        with sqlite3.connect(str(self.paths.user_db_path)) as conn:
            conn.execute(
                f"""
                INSERT INTO user_devices ({", ".join(columns)})
                VALUES ({placeholders})
                ON CONFLICT(id) DO UPDATE SET {assignments}
                """,
                tuple(values[column] for column in columns),
            )
            conn.commit()

    def _normalize_submission_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        device_id = str(payload.get("id") or "").strip()
        vendor = str(payload.get("vendor") or "").strip()
        model = str(payload.get("model") or "").strip()
        if not device_id or not vendor or not model:
            raise ValueError("Submission requires non-empty id, vendor, and model")
        normalized = {column: payload.get(column) for column in DEVICE_COLUMNS}
        normalized["id"] = device_id
        normalized["vendor"] = vendor
        normalized["model"] = model
        normalized["settings_template_md"] = (
            normalized.get("settings_template_md")
            or SONIC_TEMPLATE_DEFAULTS["settings_template_md"]
        )
        normalized["installers_template_md"] = (
            normalized.get("installers_template_md")
            or SONIC_TEMPLATE_DEFAULTS["installers_template_md"]
        )
        normalized["containers_template_md"] = (
            normalized.get("containers_template_md")
            or SONIC_TEMPLATE_DEFAULTS["containers_template_md"]
        )
        normalized["drivers_template_md"] = (
            normalized.get("drivers_template_md")
            or SONIC_TEMPLATE_DEFAULTS["drivers_template_md"]
        )
        normalized["bios"] = normalized.get("bios") or "unknown"
        normalized["year"] = normalized.get("year") or datetime.now(UTC).year
        normalized["secure_boot"] = normalized.get("secure_boot") or "unknown"
        normalized["tpm"] = normalized.get("tpm") or "unknown"
        normalized["usb_boot"] = normalized.get("usb_boot") or "unknown"
        normalized["uefi_native"] = normalized.get("uefi_native") or "unknown"
        normalized["reflash_potential"] = normalized.get("reflash_potential") or "unknown"
        normalized["methods"] = normalized.get("methods") or []
        normalized["last_seen"] = normalized.get("last_seen") or datetime.now(UTC).date().isoformat()
        normalized["windows10_boot"] = normalized.get("windows10_boot") or "unknown"
        normalized["media_mode"] = normalized.get("media_mode") or "unknown"
        normalized["udos_launcher"] = normalized.get("udos_launcher") or "unknown"
        return normalized

    def _submission_device_to_user_record(
        self, payload: dict[str, Any], *, updated_at: str
    ) -> dict[str, Any]:
        existing = self._read_user_device(str(payload["id"])) or {}
        methods = payload.get("methods")
        sources = payload.get("sources")
        return {
            **{column: payload.get(column) for column in DEVICE_COLUMNS},
            "methods": json.dumps(methods) if isinstance(methods, list) else methods,
            "sources": json.dumps(sources) if isinstance(sources, list) else sources,
            "local_origin": "approved-submission",
            "local_enabled": 1,
            "created_at": existing.get("created_at") or updated_at,
            "updated_at": updated_at,
        }

    def _apply_filters(
        self,
        records: list[dict[str, Any]],
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
    ) -> list[dict[str, Any]]:
        filtered: list[dict[str, Any]] = []
        for record in records:
            if vendor and vendor.lower() not in str(record.get("vendor") or "").lower():
                continue
            if reflash_potential and str(record.get("reflash_potential") or "") != reflash_potential:
                continue
            if usb_boot and str(record.get("usb_boot") or "") != usb_boot:
                continue
            if uefi_native and str(record.get("uefi_native") or "") != uefi_native:
                continue
            if windows10_boot and str(record.get("windows10_boot") or "") != windows10_boot:
                continue
            if media_mode and str(record.get("media_mode") or "") != media_mode:
                continue
            if udos_launcher and str(record.get("udos_launcher") or "") != udos_launcher:
                continue
            year = record.get("year")
            if year_min is not None and isinstance(year, int) and year < year_min:
                continue
            if year_max is not None and isinstance(year, int) and year > year_max:
                continue
            filtered.append(record)
        return filtered

    def _current_machine_id(self, hostname: str | None = None) -> str:
        host = (hostname or get_system_capability_service(self.repo_root).measure().hostname or "local-machine").strip().lower()
        slug = "".join(char if char.isalnum() else "-" for char in host).strip("-")
        return f"local-{slug or 'machine'}"


def get_sonic_device_service(repo_root: Path | None = None) -> SonicDeviceStorageService:
    return SonicDeviceStorageService(repo_root=repo_root)
