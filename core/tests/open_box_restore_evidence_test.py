from pathlib import Path
import shutil

from core.services import maintenance_utils
from core.services.destructive_ops import ensure_memory_layout
from core.services.sonic_device_service import get_sonic_device_service


def _seed_sonic_sql(repo_root: Path) -> None:
    datasets = repo_root.parent / "uDOS-sonic" / "datasets"
    datasets.mkdir(parents=True, exist_ok=True)
    (datasets / "sonic-devices.sql").write_text(
        (
            "DROP TABLE IF EXISTS devices;\n"
            "CREATE TABLE devices (\n"
            "  id TEXT PRIMARY KEY,\n"
            "  vendor TEXT NOT NULL,\n"
            "  model TEXT NOT NULL,\n"
            "  variant TEXT,\n"
            "  year INTEGER NOT NULL,\n"
            "  cpu TEXT,\n"
            "  gpu TEXT,\n"
            "  ram_gb INTEGER,\n"
            "  storage_gb INTEGER,\n"
            "  bios TEXT NOT NULL,\n"
            "  secure_boot TEXT NOT NULL,\n"
            "  tpm TEXT NOT NULL,\n"
            "  usb_boot TEXT NOT NULL,\n"
            "  uefi_native TEXT NOT NULL,\n"
            "  reflash_potential TEXT NOT NULL,\n"
            "  methods TEXT NOT NULL,\n"
            "  notes TEXT,\n"
            "  sources TEXT,\n"
            "  last_seen TEXT NOT NULL,\n"
            "  windows10_boot TEXT NOT NULL,\n"
            "  media_mode TEXT NOT NULL,\n"
            "  udos_launcher TEXT NOT NULL,\n"
            "  wizard_profile TEXT,\n"
            "  media_launcher TEXT,\n"
            "  settings_template_md TEXT,\n"
            "  installers_template_md TEXT,\n"
            "  containers_template_md TEXT,\n"
            "  drivers_template_md TEXT\n"
            ");\n"
            "INSERT INTO devices (\n"
            "  id, vendor, model, variant, year, cpu, gpu, ram_gb, storage_gb,\n"
            "  bios, secure_boot, tpm, usb_boot, uefi_native, reflash_potential,\n"
            "  methods, notes, sources, last_seen, windows10_boot, media_mode, udos_launcher,\n"
            "  settings_template_md, installers_template_md, containers_template_md, drivers_template_md\n"
            ") VALUES (\n"
            "  'seed-device', 'SeedVendor', 'SeedModel', 'Mk1', 2025, 'cpu', 'gpu', 8, 64,\n"
            "  'uefi', 'unknown', 'unknown', 'native', 'works', 'medium',\n"
            "  '[\"seed\"]', 'seed record', '[\"seed\"]', '2026-03-03', 'install', 'htpc', 'basic',\n"
            "  'core/framework/seed/bank/templates/submissions/SONIC-DEVICE-SETTINGS-template.md',\n"
            "  'core/framework/seed/bank/templates/submissions/SONIC-DEVICE-INSTALLERS-template.md',\n"
            "  'core/framework/seed/bank/templates/submissions/SONIC-DEVICE-CONTAINERS-template.md',\n"
            "  'core/framework/seed/bank/templates/submissions/SONIC-DEVICE-DRIVERS-template.md'\n"
            ");\n"
        ),
        encoding="utf-8",
    )


def test_open_box_restore_preserves_user_memory_and_sonic_overlay(
    tmp_path: Path, monkeypatch
) -> None:
    repo_root = tmp_path / "repo"
    memory_root = repo_root / "memory"
    knowledge_note = memory_root / "bank" / "knowledge" / "user" / "devices" / "note.md"
    knowledge_note.parent.mkdir(parents=True, exist_ok=True)
    knowledge_note.write_text("# Local note\n\nPersistent user content.\n", encoding="utf-8")

    _seed_sonic_sql(repo_root)
    monkeypatch.setattr(maintenance_utils, "get_repo_root", lambda: repo_root)

    sonic = get_sonic_device_service(repo_root)
    sonic.ensure_seed_runtime(force=True)
    bootstrap = sonic.register_current_machine()
    assert bootstrap["status"] == "ok"

    archive_path, _manifest_path = maintenance_utils.create_backup(
        memory_root,
        label="open-box-proof",
    )

    shutil.rmtree(memory_root)
    ensure_memory_layout(memory_root)
    assert not knowledge_note.exists()

    restore_message = maintenance_utils.restore_backup(
        archive_path,
        memory_root,
        force=True,
    )
    assert "Restored" in restore_message
    assert knowledge_note.read_text(encoding="utf-8").startswith("# Local note")

    restored = get_sonic_device_service(repo_root)
    runtime = restored.runtime_contract()
    assert runtime["user_catalog"]["current_machine_registered"] is True

    restored.ensure_seed_runtime(force=True)
    devices = restored.list_devices(limit=20)
    assert any(device["catalog_source"] == "seed" for device in devices)
    assert any(device["catalog_source"] == "user" for device in devices)
